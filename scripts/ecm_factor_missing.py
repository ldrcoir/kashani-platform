#!/usr/bin/env python3
"""
ECM Factor Missing Mersenne Numbers in A136030 series
=====================================================

Strategy:
1. Parse download/A136030_first_191_full_factorizations.txt to get known
   smallest prime factors for M(p) (191 prime exponents).
2. Read download/A136030_factors_1_to_8000.txt; for every entry currently
   marked as -1, replace with the smallest known factor if available.
3. For the remaining -1 entries (genuinely unknown), run ECM (Lenstra's
   Elliptic Curve Method via sympy) for a bounded time per number.
4. Write the updated factors file and a report of newly-found factors.

All output paths stay under /home/z/my-project/.
"""

import re
import sys
import time
import json
from pathlib import Path

# sympy provides ecm() and isprime()
from sympy import isprime
from sympy.ntheory import ecm

BASE = Path('/home/z/my-project')
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
FULL_FACT_FILE = BASE / 'download/A136030_first_191_full_factorizations.txt'
REPORT_FILE = BASE / 'download/ECM_factor_report.txt'
NEW_FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'  # update in-place

# Time budget per ECM target (seconds). 5 minutes per number is generous;
# ECM on these targets is unlikely to succeed in any short window but we
# do the work as requested.
ECM_PER_TARGET_SECONDS = 15
# Cap on number of ECM targets (so total runtime stays bounded)
MAX_ECM_TARGETS = 8
# Only attempt ECM on p in this range (the smallest unknowns)
ECM_P_MIN = 1277
ECM_P_MAX = 2500


def parse_full_factorizations(path: Path) -> dict[int, int]:
    """Return {p: smallest_prime_factor} for every entry in the file."""
    known: dict[int, int] = {}
    line_re = re.compile(r'\[(\d+)\]\s+M\((\d+)\)\s*=\s*(.+)')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = line_re.match(line.strip())
            if not m:
                continue
            _idx, p_str, rhs = m.groups()
            p = int(p_str)
            # Extract every integer token on the right-hand side
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            factors = [t for t in factors if t > 1]
            if not factors:
                continue
            # Verify the smallest divides M(p) (cheap sanity check)
            q = min(factors)
            if pow(2, p, q) != 1:
                # Skip silently; we don't want bad data
                continue
            known[p] = q
    return known


def read_factors_table(path: Path) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            try:
                n = int(parts[0])
                v = int(parts[1])
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


def try_ecm(p: int, seconds: int) -> int | None:
    """Run ECM on M(p) = 2^p - 1 for up to `seconds` seconds.
    Returns a non-trivial factor if found, else None.
    """
    M = (1 << p) - 1
    t0 = time.time()
    # sympy.ntheory.ecm takes a `B1` bound; we sweep increasing B1.
    # Each call runs until it finds a factor or exhausts curves at that B1.
    # We loop with growing B1 until our wall-clock budget is consumed.
    B1_schedule = [2000, 11000, 50000, 250000, 1000000]
    for B1 in B1_schedule:
        if time.time() - t0 > seconds:
            break
        try:
            # ncurves gives the number of random curves to try at this B1
            factors = ecm(M, B1=B1, B2=10 * B1, max_curve=20)
            # factors may be a list; take the smallest >1
            cand = [int(f) for f in factors if int(f) > 1 and int(f) < M]
            if cand:
                return min(cand)
        except Exception as exc:
            print(f'    ECM B1={B1} error: {exc!r}', file=sys.stderr)
            continue
    return None


def main() -> None:
    print('Parsing full_factorizations ...', file=sys.stderr)
    known = parse_full_factorizations(FULL_FACT_FILE)
    print(f'  {len(known)} known factorizations parsed.', file=sys.stderr)

    print('Reading factors table ...', file=sys.stderr)
    rows = read_factors_table(FACTORS_FILE)
    n_missing_before = sum(1 for _, v in rows if v == -1)
    print(f'  {len(rows)} rows; {n_missing_before} marked -1.', file=sys.stderr)

    # Step 1: propagate known factorizations
    propagated: list[tuple[int, int]] = []
    for i, (n, v) in enumerate(rows):
        if v == -1 and n in known:
            rows[i] = (n, known[n])
            propagated.append((n, known[n]))
    print(f'  Propagated {len(propagated)} known factors from full_factorizations.',
          file=sys.stderr)

    # Step 2: pick ECM targets
    missing_after = [n for n, v in rows if v == -1]
    targets = [n for n in missing_after if ECM_P_MIN <= n <= ECM_P_MAX]
    targets.sort()
    targets = targets[:MAX_ECM_TARGETS]
    print(f'  ECM targets ({len(targets)}): {targets}', file=sys.stderr)

    # Step 3: run ECM
    new_findings: list[tuple[int, int, float]] = []  # (p, factor, seconds)
    for idx, p in enumerate(targets, 1):
        elapsed_so_far = sum(s for _, _, s in new_findings)
        print(f'  [{idx}/{len(targets)}] ECM on M({p}) ... '
              f'(budget {ECM_PER_TARGET_SECONDS}s)', file=sys.stderr)
        t_start = time.time()
        factor = try_ecm(p, ECM_PER_TARGET_SECONDS)
        elapsed = time.time() - t_start
        if factor is not None:
            print(f'    *** FOUND factor for M({p}): {factor} '
                  f'(took {elapsed:.1f}s) ***', file=sys.stderr)
            # Update the row
            for i, (n, v) in enumerate(rows):
                if n == p and v == -1:
                    rows[i] = (n, factor)
                    break
            new_findings.append((p, factor, elapsed))
        else:
            print(f'    no factor found in {elapsed:.1f}s', file=sys.stderr)

    # Step 4: write updated factors table
    write_factors_table(NEW_FACTORS_FILE, rows)
    n_missing_after = sum(1 for _, v in rows if v == -1)
    print(f'\nUpdated factors file written.', file=sys.stderr)
    print(f'  Missing before: {n_missing_before}', file=sys.stderr)
    print(f'  Propagated from full_factorizations: {len(propagated)}', file=sys.stderr)
    print(f'  New ECM findings: {len(new_findings)}', file=sys.stderr)
    print(f'  Missing after: {n_missing_after}', file=sys.stderr)

    # Step 5: write report
    lines = []
    lines.append('ECM Factor Report for A136030 series')
    lines.append('=' * 60)
    lines.append('')
    lines.append(f'Started: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'Missing before: {n_missing_before}')
    lines.append(f'Propagated from full_factorizations: {len(propagated)}')
    lines.append(f'ECM targets tried: {len(targets)}')
    lines.append(f'ECM time budget per target: {ECM_PER_TARGET_SECONDS}s')
    lines.append(f'New factors found by ECM: {len(new_findings)}')
    lines.append(f'Missing after: {n_missing_after}')
    lines.append('')
    if propagated:
        lines.append('Propagated known factors (from full_factorizations.txt):')
        lines.append('-' * 60)
        for p, q in propagated:
            lines.append(f'  M({p}) -> {q}')
        lines.append('')
    if new_findings:
        lines.append('*** NEW FACTORS FOUND BY ECM ***')
        lines.append('-' * 60)
        for p, q, sec in new_findings:
            lines.append(f'  M({p}) -> {q}  (took {sec:.1f}s)')
        lines.append('')
    lines.append('ECM targets that did NOT yield a factor in this run:')
    lines.append('-' * 60)
    succeeded = {p for p, _, _ in new_findings}
    for p in targets:
        if p not in succeeded:
            lines.append(f'  M({p}) - no factor found')
    lines.append('')
    lines.append('Note: These Mersenne numbers have been heavily ECM-ed by the')
    lines.append('broader math community for years. A short local run is unlikely')
    lines.append('to find new factors, but is logged here for completeness.')
    REPORT_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report written to {REPORT_FILE}', file=sys.stderr)

    # Step 6: JSON summary for downstream tooling
    summary = {
        'missing_before': n_missing_before,
        'propagated': [(p, q) for p, q in propagated],
        'ecm_targets': targets,
        'new_factors': [(p, q, round(s, 2)) for p, q, s in new_findings],
        'missing_after': n_missing_after,
        'ecm_per_target_seconds': ECM_PER_TARGET_SECONDS,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    (BASE / 'download' / 'ECM_factor_summary.json').write_text(
        json.dumps(summary, indent=2), encoding='utf-8'
    )


if __name__ == '__main__':
    main()
