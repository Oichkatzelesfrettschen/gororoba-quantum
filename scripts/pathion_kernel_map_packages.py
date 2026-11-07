"""Kernel-map operand facts recomputed through three Cayley-Dickson packages' declared maps onto cd_core.

For A_5 (dimension 32) each package's basis product is compared with cd_core on all 1024 basis pairs under the
identity map (hypercomplex.cayley_dickson_algebra(5, Fraction), hyprat.Hy.from_array at the default signs,
hypercomplex_engine.multiply("standard", ...)). A package that agrees then supplies the left-multiplication matrix of
every kernel-map operand, whose exact nullity (python-flint fmpz_mat rank) and aligned-pair count must equal
pathion_kernel_map.nullity. The packages live on the build host's $PYTHON, so this runs there and writes
docs/evidence/pathion-kernel-map/packages.json; --check recomputes and compares.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import cd_sign  # noqa: E402

DIM, LEVEL = 32, 5
OUT = ROOT / "docs/evidence/pathion-kernel-map/packages.json"
OPERANDS = ((1, 17, 1), (1, 26, 1), (2, 27, 1), (1, 10, 1), (1, 18, 1), (1, 24, 1), (17, 10, -1), (17, 2, -1))


def basis_product(package: str):  # noqa: ANN201
    if package == "hypercomplex":
        import hypercomplex

        algebra = hypercomplex.cayley_dickson_algebra(LEVEL, Fraction)

        def hc(p: int, q: int) -> list[Fraction]:
            a = algebra(*[Fraction(int(k == p)) for k in range(DIM)])
            b = algebra(*[Fraction(int(k == q)) for k in range(DIM)])
            return [Fraction(c) for c in (a * b).coefficients()]

        return hc
    if package == "hyprat":
        import hyprat

        def hy(p: int, q: int) -> list[Fraction]:
            a = hyprat.Hy.from_array([Fraction(int(k == p)) for k in range(DIM)])
            b = hyprat.Hy.from_array([Fraction(int(k == q)) for k in range(DIM)])
            return [Fraction(c) for c in (a * b).to_array()]

        return hy
    import hypercomplex_engine

    def he(p: int, q: int) -> list[Fraction]:
        sign, index = hypercomplex_engine.multiply("standard", (1, p), (1, q))
        out = [Fraction(0)] * DIM
        out[int(index)] = Fraction(int(sign))
        return out

    return he


def basis_table(package: str) -> list[list[tuple[int, int]]]:
    """(sign, index) of e_p e_q for all basis pairs, from the package's own product; a product that is not a single
    signed basis element raises."""
    product = basis_product(package)
    table = []
    for p in range(DIM):
        row = []
        for q in range(DIM):
            out = product(p, q)
            support = [k for k, c in enumerate(out) if c != 0]
            if len(support) != 1 or abs(out[support[0]]) != 1:
                raise ValueError(f"{package}: e_{p} e_{q} is not a signed basis element")
            row.append((int(out[support[0]]), support[0]))
        table.append(row)
    return table


def left_matrix(table: list[list[tuple[int, int]]], m: int) -> list[list[int]]:
    """L_(e_m): column q is e_m e_q."""
    matrix = [[0] * DIM for _ in range(DIM)]
    for q in range(DIM):
        sign, index = table[m][q]
        matrix[index][q] = sign
    return matrix


def operand_facts(table: list[list[tuple[int, int]]], operand: tuple[int, int, int]) -> dict[str, int]:
    i, j, t = operand
    li, lj = left_matrix(table, i), left_matrix(table, j)
    matrix = [[li[r][c] + t * lj[r][c] for c in range(DIM)] for r in range(DIM)]
    k = (flint.fmpz_mat(li).transpose() * flint.fmpz_mat(lj)) * t  # L_i^T (t L_j)
    m = i ^ j
    aligned = sum(1 for x in range(DIM) if x < x ^ m and k[x ^ m, x] == k[x, x ^ m])
    return {"nullity": DIM - int(flint.fmpz_mat(matrix).rank()), "aligned_pairs": aligned}


def package_entry(package: str) -> dict[str, object]:
    table = basis_table(package)
    agree = sum(table[p][q] == (cd_sign(DIM, p, q), p ^ q) for p in range(DIM) for q in range(DIM))
    entry: dict[str, object] = {"map": "identity", "basis_pairs_agreeing": agree, "basis_pairs": DIM * DIM}
    if agree == DIM * DIM:
        entry["operands"] = {f"{i},{j},{t}": operand_facts(table, (i, j, t)) for i, j, t in OPERANDS}
    return entry


def compute() -> dict[str, object]:
    import parallel
    from pathion_kernel_map import nullity

    names = ("hypercomplex", "hyprat", "hypercomplex-engine")
    entries = dict(zip(names, parallel.ordered_map(package_entry, list(names), min_items=2), strict=True))
    for entry in entries.values():
        facts = entry.get("operands")
        if isinstance(facts, dict):
            entry["matches_cd_core_nullity"] = all(
                facts[f"{i},{j},{t}"]["nullity"] == nullity((i, j, t)) == facts[f"{i},{j},{t}"]["aligned_pairs"]
                for i, j, t in OPERANDS
            )
    return {"schema": "pathion-kernel-map-packages-v1", "dimension": DIM, "packages": entries}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="recompute and compare with the retained record")
    args = ap.parse_args()
    record = compute()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text() != text:
            raise SystemExit(f"{OUT} differs from the recomputed package facts")
        print("pathion kernel-map package facts reproduce")
        return 0
    OUT.write_text(text)
    packages = record["packages"]
    if not isinstance(packages, dict):
        raise TypeError("packages must be a mapping")
    for package, entry in packages.items():
        print(package, entry["basis_pairs_agreeing"], "/", entry["basis_pairs"], entry.get("matches_cd_core_nullity"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
