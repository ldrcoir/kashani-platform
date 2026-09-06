#!/usr/bin/env python3
"""
Parse the Cunningham 2- table and extract the smallest prime factor for
every odd exponent n. Then propagate these into A136030_factors_1_to_8000.txt
(only updating entries that are currently -1).

The Cunningham table format (per line, after the header):
   n   (algebraic-factors) p1.p2.p3....Pxxx  or  ...Cxxx
where:
  - '(a,b,c)' lists exponents whose Mersenne factors divide M(n) - skip these
  - 'Pxxx' denotes a prime of xxx digits (cofactor is prime => fully factored)
  - 'Cxxx' denotes a composite of xxx digits (cofactor still composite)
  - 'p1.p2....' are explicit prime factors

We extract the smallest explicit prime factor (the first integer token after
the algebraic-factor list).

Strategy:
1. Parse table to get {n: smallest_explicit_prime_factor} for odd n in [1,1499]
2. Read A136030_factors_1_to_8000.txt; for every -1 row whose n is in the
   Cunningham map, replace with the smallest factor.
3. Write updated table.
4. Write a richer report: full factorization strings from Cunningham for the
   newly-covered primes, marked as 'full' (P cofactor) or 'partial' (C cofactor).
5. Print stats.

All paths under /home/z/my-project/.
"""

import re
import sys
import json
import time
from pathlib import Path
from sympy import isprime

BASE = Path('/home/z/my-project')
CUN_FILE = BASE / 'download/cunningham_table_2_minus.txt'
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
REPORT_FILE = BASE / 'download/cunningham_propagation_report.txt'
SUMMARY_FILE = BASE / 'download/cunningham_propagation_summary.json'


def parse_cunningham(path: Path) -> dict[int, dict]:
    """
    Returns: { n: {
        'smallest_factor': int or None,
        'factors': [int, ...],     # explicit prime factors (in order shown)
        'cofactor_kind': 'P'|'C'|None,    # P=prime cofactor, C=composite cofactor
        'cofactor_digits': int or None,
        'full_string': str,         # the raw factorization string
    }}
    """
    # Read the whole file, glue continuation lines.
    # A record starts with a line like:
    #    1277   ...factors...
    # continuation lines start with whitespace and contain more factor data
    text = path.read_text(encoding='utf-8', errors='ignore')

    # Strip the header / footer / decorative lines
    lines = []
    for raw in text.splitlines():
        # Skip decorative separator lines and headers
        s = raw.rstrip()
        if not s:
            continue
        if set(s.strip()) <= {'='}:
            continue
        if s.strip().startswith('Cunningham') or s.strip().startswith('Table 2'):
            continue
        if s.strip().startswith('n ') or s.strip().startswith('n n'):
            continue
        lines.append(s)

    # Now merge: every line in this file starts with whitespace.
    # A "record start" line looks like:  "   <n>  <factor-data>"
    # A continuation line looks like:    "       <more-factor-data>"
    # Heuristic: try to parse the first non-space token as an integer.
    # If it parses AND there is at least one more token after it, it's a record start.
    records: list[str] = []
    for s in lines:
        stripped = s.strip()
        if not stripped:
            continue
        # Try first token
        parts = stripped.split(None, 1)
        first = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        if first.isdigit() and rest:
            # New record
            records.append(f'{first} {rest}')
        else:
            # Continuation
            if records:
                records[-1] = records[-1] + ' ' + stripped

    # Parse each record
    out: dict[int, dict] = {}
    rec_re = re.compile(r'^\s*(\d+)\s+(.*)$')
    for rec in records:
        m = rec_re.match(rec)
        if not m:
            continue
        n = int(m.group(1))
        body = m.group(2).strip()
        # Strip algebraic factor prefix like '(3,7,21,61,183,427)'
        alg_re = re.compile(r'^\(([^)]*)\)\s*')
        am = alg_re.match(body)
        if am:
            body = body[am.end():].strip()
        # Find tokens: integers, P\d+, C\d+
        # Split on '.' but careful with digits in P/C markers
        # Replace Pxxx and Cxxx with markers
        tokens = []
        # First, find all matches of either \d+ (explicit factor) or [PC]\d+ (cofactor)
        token_re = re.compile(r'(\d+)|([PC])(\d+)')
        # But the '.' separators may merge digits - we need to be careful.
        # Replace P\d+ and C\d+ with placeholders before splitting on '.'
        # Actually, we can find tokens directly with a global regex
        # Use finditer over the whole body
        found_tokens = []
        for m2 in token_re.finditer(body):
            if m2.group(1):
                found_tokens.append(('I', int(m2.group(1))))
            else:
                kind = m2.group(2)
                digits = int(m2.group(3))
                found_tokens.append((kind, digits))
        # Extract explicit integer factors
        explicit_factors = [v for k, v in found_tokens if k == 'I']
        # Find cofactor marker (last P or C)
        cofactor_kind = None
        cofactor_digits = None
        for k, v in found_tokens:
            if k in ('P', 'C'):
                cofactor_kind = k
                cofactor_digits = v
        smallest = min(explicit_factors) if explicit_factors else None
        out[n] = {
            'smallest_factor': smallest,
            'factors': explicit_factors,
            'cofactor_kind': cofactor_kind,
            'cofactor_digits': cofactor_digits,
            'full_string': body,
        }
    return out


def read_factors_table(path: Path) -> list[tuple[int, int]]:
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            try:
                n = int(parts[0]); v = int(parts[1])
            except ValueError:
                continue
            rows.append((n, v))
    return rows


def write_factors_table(path: Path, rows: list[tuple[int, int]]) -> None:
    lines = [
        '# Series A136030: Smallest prime factor of Mersenne number M(n) = 2^n - 1',
        '# n from 1 to 8000',
        '# Value: 1 if n=1; 0 if M(n) is a Mersenne prime; else smallest prime factor; -1 if not found',
        '# Format: n<TAB>value',
    ]
    for n, v in rows:
        lines.append(f'{n}\t{v}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    print('Parsing Cunningham 2- table ...', file=sys.stderr)
    table = parse_cunningham(CUN_FILE)
    print(f'  Parsed {len(table)} exponents.', file=sys.stderr)

    # Stats on what the table gives us
    fully_factored = sum(1 for r in table.values() if r['cofactor_kind'] == 'P')
    partial = sum(1 for r in table.values() if r['cofactor_kind'] == 'C')
    no_cofactor = sum(1 for r in table.values() if r['cofactor_kind'] is None)
    print(f'  Fully factored (P cofactor): {fully_factored}', file=sys.stderr)
    print(f'  Partial (C cofactor):       {partial}', file=sys.stderr)
    print(f'  No cofactor marker:         {no_cofactor}', file=sys.stderr)

    print('\nReading factors table ...', file=sys.stderr)
    rows = read_factors_table(FACTORS_FILE)
    missing_before = sum(1 for _, v in rows if v == -1)
    print(f'  {len(rows)} rows; {missing_before} marked -1.', file=sys.stderr)

    # Propagate
    propagated = []
    for i, (n, v) in enumerate(rows):
        if v == -1 and n in table and table[n]['smallest_factor'] is not None:
            q = table[n]['smallest_factor']
            # Sanity: q must divide M(n) = 2^n - 1
            if pow(2, n, q) == 1:
                rows[i] = (n, q)
                propagated.append((n, q, table[n]['cofactor_kind']))
            else:
                print(f'  WARN: q={q} does not divide M({n}); skipping',
                      file=sys.stderr)
    print(f'  Propagated {len(propagated)} factors from Cunningham table.',
          file=sys.stderr)

    # Write updated table
    write_factors_table(FACTORS_FILE, rows)
    missing_after = sum(1 for _, v in rows if v == -1)
    print(f'  Missing before: {missing_before}', file=sys.stderr)
    print(f'  Missing after:  {missing_after}', file=sys.stderr)

    # Write report
    propagated_full = [(n, q) for n, q, k in propagated if k == 'P']
    propagated_partial = [(n, q) for n, q, k in propagated if k == 'C']
    propagated_no = [(n, q) for n, q, k in propagated if k is None]

    lines = []
    lines.append('Cunningham 2- Table Propagation Report')
    lines.append('=' * 60)
    lines.append('')
    lines.append(f'Started: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'Source: {CUN_FILE.name}')
    lines.append(f'Cunningham exponents parsed: {len(table)}')
    lines.append(f'  - Fully factored (P cofactor): {fully_factored}')
    lines.append(f'  - Partial (C cofactor):       {partial}')
    lines.append(f'  - No cofactor marker:         {no_cofactor}')
    lines.append('')
    lines.append(f'A136030_factors_1_to_8000.txt')
    lines.append(f'  Missing before: {missing_before}')
    lines.append(f'  Propagated total: {len(propagated)}')
    lines.append(f'    - From fully-factored entries: {len(propagated_full)}')
    lines.append(f'    - From partial entries:        {len(propagated_partial)}')
    lines.append(f'    - From no-cofactor entries:    {len(propagated_no)}')
    lines.append(f'  Missing after: {missing_after}')
    lines.append('')

    if propagated_full:
        lines.append('--- Fully factored (Cunningham P cofactor) ---')
        for n, q in propagated_full:
            rec = table[n]
            lines.append(f'  M({n}) -> smallest factor = {q}')
            lines.append(f'      full: {rec["full_string"]}')
        lines.append('')

    if propagated_partial:
        lines.append('--- Partial (Cunningham C cofactor still composite) ---')
        for n, q in propagated_partial:
            rec = table[n]
            lines.append(f'  M({n}) -> smallest known factor = {q}')
            lines.append(f'      partial: {rec["full_string"]}')
        lines.append('')

    if propagated_no:
        lines.append('--- No cofactor marker (no P/C in table) ---')
        for n, q in propagated_no:
            rec = table[n]
            lines.append(f'  M({n}) -> smallest factor = {q}')
            lines.append(f'      full: {rec["full_string"]}')
        lines.append('')

    REPORT_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report written to {REPORT_FILE}', file=sys.stderr)

    # Summary JSON
    summary = {
        'cunningham_exponents': len(table),
        'fully_factored_in_cunningham': fully_factored,
        'partial_in_cunningham': partial,
        'missing_before': missing_before,
        'missing_after': missing_after,
        'propagated_total': len(propagated),
        'propagated_from_full': len(propagated_full),
        'propagated_from_partial': len(propagated_partial),
        'propagated_from_no_cofactor': len(propagated_no),
        'propagated_full': [
            {'n': n, 'smallest_factor': q, 'full_string': table[n]['full_string']}
            for n, q in propagated_full
        ],
        'propagated_partial': [
            {'n': n, 'smallest_factor': q, 'full_string': table[n]['full_string']}
            for n, q in propagated_partial
        ],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'Summary written to {SUMMARY_FILE}', file=sys.stderr)


if __name__ == '__main__':
    main()
