#!/usr/bin/env python3
"""
Propagate smallest factors from A136030_complete_factorizations.txt into
A136030_factors_1_to_8000.txt, updating any -1 entries.

Also writes a final-status report.
"""

import re
import sys
import json
import time
from pathlib import Path

BASE = Path('/home/z/my-project')
COMPLETE_FILE = BASE / 'download/A136030_complete_factorizations.txt'
FACTORS_FILE = BASE / 'download/A136030_factors_1_to_8000.txt'
STATUS_FILE = BASE / 'download/A136030_status_report.txt'


def parse_complete(path: Path) -> dict[int, tuple[str, list[int]]]:
    """Returns {p: (status, [factors])}."""
    out: dict[int, tuple[str, list[int]]] = {}
    line_re = re.compile(r'^\[(FULL|PART|MERSE)\s*\]\s+M\((\d+)\)\s*=\s*(.+)$')
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            m = line_re.match(line)
            if not m:
                continue
            status = m.group(1).strip()
            p = int(m.group(2))
            rhs = m.group(3).strip()
            factors = [int(t) for t in re.findall(r'\d+', rhs)]
            out[p] = (status, factors)
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
    print('Parsing complete factorizations ...', file=sys.stderr)
    comp = parse_complete(COMPLETE_FILE)
    print(f'  {len(comp)} entries.', file=sys.stderr)

    print('Reading factors table ...', file=sys.stderr)
    rows = read_factors_table(FACTORS_FILE)
    missing_before = sum(1 for _, v in rows if v == -1)
    print(f'  {len(rows)} rows; {missing_before} marked -1.', file=sys.stderr)

    propagated = []
    for i, (n, v) in enumerate(rows):
        if v == -1 and n in comp:
            status, factors = comp[n]
            if not factors:
                continue
            q = min(factors)
            # Sanity: q must divide M(n)
            if pow(2, n, q) == 1:
                rows[i] = (n, q)
                propagated.append((n, q, status))

    write_factors_table(FACTORS_FILE, rows)
    missing_after = sum(1 for _, v in rows if v == -1)
    print(f'  Propagated {len(propagated)} factors.', file=sys.stderr)
    print(f'  Missing before: {missing_before}', file=sys.stderr)
    print(f'  Missing after:  {missing_after}', file=sys.stderr)

    # Status report
    n_full_in_comp = sum(1 for s, _ in comp.values() if s == 'FULL')
    n_part_in_comp = sum(1 for s, _ in comp.values() if s == 'PART')
    n_merse_in_comp = sum(1 for s, _ in comp.values() if s == 'MERSE')
    total_in_comp = len(comp)

    # Range breakdown of remaining missing
    missing_rows = [n for n, v in rows if v == -1]
    ranges = [(1, 500), (501, 1000), (1001, 1500), (1501, 2000),
              (2001, 3000), (3001, 5000), (5001, 8000)]
    range_counts = []
    for lo, hi in ranges:
        c = sum(1 for n in missing_rows if lo <= n <= hi)
        range_counts.append((f'{lo}-{hi}', c))

    lines = []
    lines.append('A136030 Status Report')
    lines.append('=' * 60)
    lines.append(f'Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append('')
    lines.append('Complete-factorization database:')
    lines.append(f'  Source: A136030_complete_factorizations.txt')
    lines.append(f'  Total entries: {total_in_comp}')
    lines.append(f'    [FULL]  complete: {n_full_in_comp}')
    lines.append(f'    [PART]  partial:  {n_part_in_comp}')
    lines.append(f'    [MERSE] Mersenne: {n_merse_in_comp}')
    lines.append('')
    lines.append('A136030_factors_1_to_8000.txt:')
    lines.append(f'  Total rows: {len(rows)}')
    lines.append(f'  Missing before this pass: {missing_before}')
    lines.append(f'  Propagated in this pass:  {len(propagated)}')
    lines.append(f'  Missing after this pass:  {missing_after}')
    lines.append('')
    lines.append('Range breakdown of remaining missing entries:')
    for r, c in range_counts:
        lines.append(f'  n in {r:>11}: {c}')
    lines.append('')
    lines.append('First 30 remaining missing entries:')
    for n in missing_rows[:30]:
        lines.append(f'  M({n})')
    lines.append('')
    if propagated:
        lines.append('Newly propagated factors in this pass:')
        for n, q, status in propagated:
            lines.append(f'  M({n}) -> {q}  [{status}]')
    STATUS_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Status report: {STATUS_FILE}', file=sys.stderr)


if __name__ == '__main__':
    main()
