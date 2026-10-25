"""Missing differences of the primorial wheels for k <= 20 by restricted-cover search, checked against Ziller Table 1.

An even difference 2L between consecutive integers coprime to P_k exists
exactly when the odd primes of P_k admit an endpoint-restricted cover of
U_L = {1, ..., L - 1} (primorial_cover). For every k <= 20 and every L with
2L <= h(k), the largest difference Table 1 lists, this module decides that
cover by search:

1. Each search walks every allowed assignment of the first BRANCH_PRIMES
   odd primes in lexicographic order and runs primorial_cover's pruned
   depth-first search over the rest; the pool spreads the pending cells. The
   first covering branch supplies the witness; a cell whose every branch
   fails is excluded, and the record keeps its branch count.
2. A witness found at level k extends to every later level by giving each new
   prime its smallest allowed residue (r outside {0, L mod p}, which exists
   for every odd p), so L is searched again only at levels where it is
   excluded. Every cell (k, L) is then checked directly: its extended witness
   leaves no point of U_L uncovered.
3. The missing set of each k, N_min(k) (the smallest missing difference minus
   2, or h(k) when none is missing) and the membership of h(k) in D(k) are
   compared with the transcription ZILLER_TABLE_1.

h(k) itself enters only as the range bound: membership in D(k) is not
monotone in the difference, so excluding h(k) + 2 would not prove h(k)
maximal, and the record reproduces h(k) in D(k) only.

``--out FILE`` writes the record; ``--check FILE`` recomputes it and requires
byte equality with FILE.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import parallel
import primorial_cover as pc

SCHEMA = "gororoba-primorial-ziller-table-v1"

# Ziller, arXiv:2007.01808v1, Table 1, p. 12 (PDF sha256 99ef4a08...bdba0 in docs/SOURCES.json):
# k -> (p_k, h(k - 1), N_min(k), non-existent differences, h(k)); h(0) is printed as "-".
ZILLER_TABLE_1: dict[int, tuple[int, int | None, int, tuple[int, ...], int]] = {
    1: (2, None, 2, (), 2),
    2: (3, 2, 4, (), 4),
    3: (5, 4, 6, (), 6),
    4: (7, 6, 10, (), 10),
    5: (11, 10, 14, (), 14),
    6: (13, 14, 18, (20,), 22),
    7: (17, 22, 26, (), 26),
    8: (19, 26, 30, (32,), 34),
    9: (23, 34, 40, (), 40),
    10: (29, 40, 46, (), 46),
    11: (31, 46, 58, (), 58),
    12: (37, 58, 66, (), 66),
    13: (41, 66, 74, (), 74),
    14: (43, 74, 84, (86, 88), 90),
    15: (47, 90, 96, (98,), 100),
    16: (53, 100, 106, (), 106),
    17: (59, 106, 118, (), 118),
    18: (61, 118, 132, (), 132),
    19: (67, 132, 144, (146,), 152),
    20: (71, 152, 164, (166, 170, 172), 174),
}
SOURCE = {
    "arxiv": "2007.01808v1",
    "pdf_sha256": "99ef4a080645f90c494f7dcf7da22346bd4d4834f4a2e93391e69565f84bdba0",
    "table": "Table 1, p. 12",
}
# Odd primes whose allowed residues are enumerated before the depth-first search: at most
# 2 * 4 * 6 * 10 branches per cell.
BRANCH_PRIMES = 4


def _find(remaining: int, rows: list[tuple[int, list[tuple[int, int]]]]) -> dict[int, int] | None:
    """One class per row covering every bit of remaining, as {row prime: residue}, in _coverable's order."""
    if remaining == 0:
        return {}
    if not rows:
        return None
    if remaining.bit_count() > sum(max((remaining & m).bit_count() for _, m in classes) for _, classes in rows):
        return None
    p, classes = rows[0]
    for r, m in sorted(classes, key=lambda rm: -(remaining & rm[1]).bit_count()):
        found = _find(remaining & ~m, rows[1:])
        if found is not None:
            return {p: r, **found}
    return None


def complete(half: int, primes: list[int], chosen: dict[int, int]) -> tuple[int, ...]:
    """Residues for every prime: the chosen class, else the smallest allowed residue."""
    return tuple(chosen.get(p, pc.allowed(p, half)[0]) for p in primes)


class CellSearch:
    """Picklable worker: (k, L) -> (residues of the first cover in branch order, or None; branches searched)."""

    def __call__(self, cell: tuple[int, int]) -> tuple[tuple[int, ...] | None, int]:
        k, half = cell
        primes = pc.odd_primes(k)
        head, tail = primes[:BRANCH_PRIMES], primes[BRANCH_PRIMES:]
        rows = sorted(
            ((p, [(r, pc.class_mask(p, r, half)) for r in pc.allowed(p, half)]) for p in tail),
            key=lambda row: len(row[1]),
        )
        everything = (1 << (half - 1)) - 1
        searched = 0
        for prefix in itertools.product(*(pc.allowed(p, half) for p in head)):
            searched += 1
            covered = 0
            for p, r in zip(head, prefix, strict=True):
                covered |= pc.class_mask(p, r, half)
            found = _find(everything & ~covered, rows)
            if found is not None:
                return complete(half, primes, {**dict(zip(head, prefix, strict=True)), **found}), searched
        return None, searched


def search(cells: list[tuple[int, int]]) -> dict[tuple[int, int], tuple[tuple[int, ...] | None, int]]:
    """(k, L) -> (first cover in branch order or None, branches searched), one pooled item per cell."""
    return dict(zip(cells, parallel.ordered_map(CellSearch(), cells, min_items=1), strict=True))


def extend(half: int, k_from: int, residues: tuple[int, ...], k: int) -> tuple[int, ...]:
    """A level-k_from witness carried to level k with the smallest allowed residue for every new prime."""
    primes = pc.odd_primes(k)
    return residues + tuple(pc.allowed(p, half)[0] for p in primes[len(pc.odd_primes(k_from)) :])


def reproduce(top: int = max(ZILLER_TABLE_1)) -> dict[str, Any]:
    """The record for the Table 1 rows k = 1..top."""
    levels = [k for k in sorted(ZILLER_TABLE_1) if k <= top]
    first = {
        half: next(k for k in levels if 2 * half <= ZILLER_TABLE_1[k][4])
        for half in range(1, ZILLER_TABLE_1[levels[-1]][4] // 2 + 1)
    }
    pending = sorted((k, half) for half, k in first.items())
    witnesses: dict[int, tuple[int, tuple[int, ...]]] = {}
    exclusions: dict[tuple[int, int], int] = {}
    while pending:
        # Search cost grows with k and L; the largest cells enter the pool first.
        found = search(sorted(pending, reverse=True))
        pending = []
        for (k, half), (cover, count) in found.items():
            if cover is not None:
                witnesses[half] = (k, cover)
            else:
                exclusions[(k, half)] = count
                if k < levels[-1]:
                    pending.append((k + 1, half))
    rows = []
    cells = 0
    for k in levels:
        p_k, h_prev, n_min, missing, h = ZILLER_TABLE_1[k]
        if pc.primes_up_to(p_k)[-1] != p_k or len(pc.primes_up_to(p_k)) != k:
            raise RuntimeError(f"Table 1 row {k} prints p_k = {p_k}, not the {k}th prime")
        if k > 1 and h_prev != ZILLER_TABLE_1[k - 1][4]:
            raise RuntimeError(
                f"Table 1 row {k} prints h(k - 1) = {h_prev}, row {k - 1} prints h = {ZILLER_TABLE_1[k - 1][4]}"
            )
        computed = []
        for half in range(1, h // 2 + 1):
            cells += 1
            if (k, half) in exclusions:
                computed.append(2 * half)
                continue
            k_from, residues = witnesses[half]
            if k_from > k:
                raise RuntimeError(f"L = {half} has no verdict at k = {k}")
            if pc.uncovered(half, pc.odd_primes(k), extend(half, k_from, residues, k)):
                raise RuntimeError(f"the carried witness for gap {2 * half} fails at k = {k}")
        computed_n_min = computed[0] - 2 if computed else h
        rows.append(
            {
                "k": k,
                "p_k": p_k,
                "h": h,
                "missing": computed,
                "n_min": computed_n_min,
                "h_in_D": h not in computed,
                "table_agrees": computed == list(missing) and computed_n_min == n_min and h not in computed,
                "exclusion_branches": {str(2 * half): exclusions[(kk, half)] for kk, half in exclusions if kk == k},
            }
        )
    return {
        "schema": SCHEMA,
        "source": SOURCE,
        "branch_primes": BRANCH_PRIMES,
        "cells_checked": cells,
        "rows": rows,
        "table_agrees": all(row["table_agrees"] for row in rows),
        "witnesses": {str(2 * half): {"k": k, "residues": list(r)} for half, (k, r) in sorted(witnesses.items())},
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    record = reproduce()
    text = render(record)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}; table_agrees = {record['table_agrees']}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print(f"{args.check} departs from the recomputed table")
        return 1
    print(f"{args.check}: Table 1 reproduces through k = {max(ZILLER_TABLE_1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
