#!/usr/bin/env python3
"""
Try to factor the smallest composite cofactors from Cunningham-table partial
factorizations, and assemble a comprehensive complete-factorization file.

Steps:
1. Parse Cunningham table -> get partial factorizations (entries with C cofactor).
2. For each such entry, compute the cofactor C = M(n) / product(known_factors).
3. Run ECM on the smallest cofactors (sorted by digit count).
4. If ECM finds a factor, divide out and re-ECM. Repeat until cofactor is prime
   or ECM budget exhausted.
5. Write a comprehensive factorizations file combining:
   - The original 191 entries from A136030_first_191_full_factorizations.txt
   - The newly-covered entries from Cunningham (fully-factored and partial).
6. Print stats.

All paths under /home/z/my-project/.
"""

import re
import sys
import json
import time
from pathlib import Path
from sympy import isprime
from sympy.ntheory import ecm

BASE = Path('/home/z/my-project')
CUN_FILE = BASE / 'download/cunningham_table_2_minus.txt'
EXISTING_FULL_FILE = BASE / 'download/A136030_first_191_full_factorizations.txt'
COMPLETE_OUT = BASE / 'download/A136030_complete_factorizations.txt'
ECM_LOG = BASE / 'download/cofactor_ecm_log.txt'

# Per-cofactor ECM budget (seconds). C300+ cofactors will not yield to ECM in
# this time, but we make an honest attempt.
ECM_BUDGET_PER_COFACTOR = 60
# How many cofactors to attack (smallest first).
MAX_COFRACTORS = 4


def parse_cunningham_full(path: Path) -> dict[int, dict]:
    """Re-implementation that also cleans line-continuation backslashes."""
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = []
    for raw in text.splitlines():
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

    records: list[str] = []
    for s in lines:
        stripped = s.strip()
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        first = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        if first.isdigit() and rest:
            records.append(f'{first} {rest}')
        else:
            if records:
                records[-1] = records[-1] + ' ' + stripped

    out: dict[int, dict] = {}
    rec_re = re.compile(r'^\s*(\d+)\s+(.*)$')
    for rec in records:
        m = rec_re.match(rec)
        if not m:
            continue
        n = int(m.group(1))
        body = m.group(2).strip()
        alg_re = re.compile(r'^\(([^)]*)\)\s*')
        am = alg_re.match(body)
        if am:
            body = body[am.end():].strip()
        # Clean line-continuation backslashes that snuck in from the source file
        body = body.replace('\\ ', '')
        body = body.replace('\\', '')
        # Collapse multiple spaces
        body = re.sub(r'\s+', ' ', body).strip()
        # Re-handle the resulting '..' that may appear after cleaning
        body = body.replace('.. ', '.').replace(' .', '.').replace('. ', '.')
        body = re.sub(r'\.+', '.', body)
        # Now tokenize
        token_re = re.compile(r'(\d+)|([PC])(\d+)')
        found_tokens = []
        for m2 in token_re.finditer(body):
            if m2.group(1):
                found_tokens.append(('I', int(m2.group(1))))
            else:
                found_tokens.append((m2.group(2), int(m2.group(3))))
        explicit_factors = [v for k, v in found_tokens if k == 'I']
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


def parse_existing_full(path: Path) -> dict[int, list[int]]:
    """Parse A136030_first_191_full_factorizations.txt.
    Returns {p: [prime factors in order shown]}.
    """
    out: dict[int, list[int]] = {}
    line_re = re.compile(r'\[(\d+)\]\s+M\((\d+)\)\s*=\s*(.+)')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = line_re.match(line.strip())
            if not m:
                continue
            p = int(m.group(2))
            rhs = m.group(3).strip()
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = factors
    return out


def ecm_one_factor(n: int, seconds: int) -> int | None:
    """Run ECM on n for up to `seconds` seconds. Return a factor if found."""
    t0 = time.time()
    B1_schedule = [2000, 11000, 50000, 250000, 1000000, 3000000]
    for B1 in B1_schedule:
        if time.time() - t0 > seconds:
            break
        try:
            factors = ecm(n, B1=B1, B2=10 * B1, max_curve=30)
            cand = [int(f) for f in factors if int(f) > 1 and int(f) < n]
            if cand:
                return min(cand)
        except Exception as exc:
            print(f'    ECM B1={B1} error: {exc!r}', file=sys.stderr)
            continue
    return None


def fully_factor_with_ecm(n: int, seconds: int, log: list[str]) -> list[int]:
    """Try to fully factor n using ECM recursively. Returns list of prime factors.
    n must be > 1. Stops when cofactor is prime or budget exhausted."""
    if n == 1:
        return []
    if isprime(n):
        return [n]
    budget_end = time.time() + seconds
    factors: list[int] = []
    remaining = n
    while remaining > 1 and not isprime(remaining):
        left = max(5, int(budget_end - time.time()))
        if left <= 0:
            break
        f = ecm_one_factor(remaining, left)
        if f is None:
            break
        log.append(f'    ECM found factor: {f}')
        # f may not be prime; recurse
        sub = fully_factor_with_ecm(f, max(5, left // 2), log)
        factors.extend(sub)
        for s in sub:
            remaining //= s
    if remaining > 1:
        if isprime(remaining):
            factors.append(remaining)
        else:
            log.append(f'    cofactor still composite: {remaining}')
    return sorted(factors)


def main() -> None:
    print('Parsing Cunningham table ...', file=sys.stderr)
    table = parse_cunningham_full(CUN_FILE)
    print(f'  {len(table)} exponents parsed.', file=sys.stderr)

    print('Parsing existing 191 full factorizations ...', file=sys.stderr)
    existing = parse_existing_full(EXISTING_FULL_FILE)
    print(f'  {len(existing)} entries.', file=sys.stderr)

    # Collect partial entries (C cofactor). These are the candidates for ECM.
    partials = []
    for n, rec in table.items():
        if not isprime(n):
            continue
        if rec['cofactor_kind'] != 'C':
            continue
        # Need the cofactor size
        digits = rec['cofactor_digits'] or 9999
        partials.append((digits, n, rec))
    partials.sort()
    print(f'  {len(partials)} partial (C-cofactor) prime entries in Cunningham.',
          file=sys.stderr)
    print(f'  Smallest cofactor sizes: {[d for d, _, _ in partials[:8]]}',
          file=sys.stderr)

    # Attempt ECM on the smallest cofactors
    log_lines: list[str] = []
    log_lines.append(f'Cofactor ECM log - {time.strftime("%Y-%m-%d %H:%M:%S")}')
    log_lines.append('=' * 60)
    newly_fully_factored: dict[int, list[int]] = {}

    targets = partials[:MAX_COFRACTORS]
    for digits, n, rec in targets:
        print(f'\n  M({n}) - cofactor C{digits} ...', file=sys.stderr)
        log_lines.append(f'\nM({n}) - cofactor C{digits}')
        log_lines.append(f'  known factors: {rec["factors"]}')
        # Compute M(n)
        M = (1 << n) - 1
        # Divide by known factors
        cofactor = M
        for f in rec['factors']:
            if cofactor % f == 0:
                cofactor //= f
            else:
                log_lines.append(f'  WARN: factor {f} does not divide M({n})')
        log_lines.append(f'  cofactor digits: {len(str(cofactor))}')
        # Run ECM
        t_start = time.time()
        sub_factors = fully_factor_with_ecm(cofactor, ECM_BUDGET_PER_COFACTOR, log_lines)
        elapsed = time.time() - t_start
        if sub_factors:
            log_lines.append(f'  ECM found {len(sub_factors)} factor(s) in {elapsed:.1f}s')
            log_lines.append(f'  factors: {sub_factors}')
            # Check if cofactor is fully factored
            product = 1
            for f in sub_factors:
                product *= f
            if product == cofactor:
                log_lines.append(f'  *** FULLY FACTORED ***')
                # Combine with known factors and store
                all_factors = sorted(rec['factors'] + sub_factors)
                newly_fully_factored[n] = all_factors
            else:
                log_lines.append(f'  partial: product/cofactor = {product}/{cofactor}')
        else:
            log_lines.append(f'  no factor found in {elapsed:.1f}s')

    ECM_LOG.write_text('\n'.join(log_lines) + '\n', encoding='utf-8')
    print(f'\nECM log written to {ECM_LOG}', file=sys.stderr)
    print(f'Newly fully factored via ECM: {len(newly_fully_factored)}', file=sys.stderr)

    # Assemble comprehensive factorization file.
    # Combine:
    #   - existing 191 (from first_191_full)
    #   - fully-factored Cunningham entries (P cofactor) - reconstruct string
    #   - newly_fully_factored via ECM (overrides 'partial' status)
    #   - partial Cunningham entries (still composite cofactor) - mark as partial
    all_primes: set[int] = set(existing.keys())
    for n, rec in table.items():
        if isprime(n) and (rec['cofactor_kind'] in ('P', 'C') or rec['smallest_factor']):
            all_primes.add(n)
    for n in newly_fully_factored:
        all_primes.add(n)

    lines = []
    lines.append('Complete factorizations of Mersenne numbers M(p) = 2^p - 1')
    lines.append('Aggregated from: A136030_first_191_full_factorizations.txt')
    lines.append('                  Cunningham 2- table (n < 1500)')
    lines.append('                  local ECM attempts on partial cofactors')
    lines.append('=' * 70)
    lines.append('')
    lines.append('Legend:')
    lines.append('  [FULL]   cofactor is prime (P) - complete factorization')
    lines.append('  [PART]   cofactor is composite (C) - partial factorization')
    lines.append('  [MERSE]  M(p) is itself a Mersenne prime')
    lines.append('')

    n_full = 0
    n_part = 0
    n_merse = 0
    for p in sorted(all_primes):
        # Determine status & factors
        if p in newly_fully_factored:
            factors = newly_fully_factored[p]
            status = 'FULL'
        elif p in existing:
            factors = existing[p]
            # Existing entries are all complete (from factordb / Cunningham)
            # Check if it's a Mersenne prime (single factor equal to M(p))
            Mp = (1 << p) - 1
            if len(factors) == 1 and factors[0] == Mp:
                status = 'MERSE'
            else:
                status = 'FULL'
        elif p in table:
            rec = table[p]
            if rec['cofactor_kind'] == 'P':
                # Fully factored - factors list + P cofactor (we don't have its digits,
                # but we know it's prime)
                factors = rec['factors']
                status = 'FULL'
            elif rec['cofactor_kind'] == 'C':
                factors = rec['factors']
                status = 'PART'
            elif rec['smallest_factor'] is None:
                # No explicit factors - probably a Mersenne prime
                Mp = (1 << p) - 1
                if isprime(Mp):
                    factors = [Mp]
                    status = 'MERSE'
                else:
                    factors = []
                    status = 'PART'
            else:
                factors = rec['factors']
                status = 'FULL' if not rec['cofactor_kind'] else 'PART'
        else:
            continue
        if status == 'FULL':
            n_full += 1
        elif status == 'PART':
            n_part += 1
        elif status == 'MERSE':
            n_merse += 1
        factor_str = ' * '.join(str(f) for f in factors) if factors else '(unknown)'
        lines.append(f'[{status:5}] M({p}) = {factor_str}')

    lines.append('')
    lines.append('=' * 70)
    lines.append(f'Total entries: {len(all_primes)}')
    lines.append(f'  [FULL]  complete factorization: {n_full}')
    lines.append(f'  [PART]  partial factorization:  {n_part}')
    lines.append(f'  [MERSE] Mersenne prime:         {n_merse}')
    COMPLETE_OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Complete factorizations file: {COMPLETE_OUT}', file=sys.stderr)
    print(f'  FULL: {n_full}, PART: {n_part}, MERSE: {n_merse}', file=sys.stderr)


if __name__ == '__main__':
    main()
