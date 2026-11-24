"""The readout twins of the IBM kernel map are the primaries times e16: one orbit point, one sign network.

For a two-term operand a = e_i + t e_j with m = i XOR j, K = L_i^T (t L_j) is a signed permutation x -> x XOR m and
s(x) is the sign it carries from x to x XOR m (pathion_kernel_map). The script checks, exactly, for the two twin
pairs that hardware measured: the twin is a * e16 in the 32-dimensional Cayley-Dickson algebra; its split
coordinates z_k = a_k + i a_(16 + k) are i times those of the primary; and s_twin(x) = -s_primary(x XOR 16) for all
32 basis states, so the twin circuit is the primary circuit with basis bit 4 flipped and K negated.

Run from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/hardware-orbits/twin_sign_relation.py
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import cd_core  # noqa: E402

DIM = 32
PAIRS = (((1, 18, 1), (17, 2, -1)), ((1, 26, 1), (17, 10, -1)))


def unit(index: int) -> list[Fraction]:
    return [Fraction(int(k == index)) for k in range(DIM)]


def operand(i: int, j: int, t: int) -> list[Fraction]:
    return [Fraction(int(k == i) + t * int(k == j)) for k in range(DIM)]


def signs(i: int, j: int, t: int) -> list[int]:
    """s(x): the entry of K = L_i^T (t L_j) that carries x to x XOR m."""
    left_i = cd_core.left_mult_matrix_exact(DIM, unit(i))
    left_j = cd_core.left_mult_matrix_exact(DIM, unit(j))
    m = i ^ j
    out = []
    for x in range(DIM):
        entry = sum(left_i[r][x ^ m] * t * left_j[r][x] for r in range(DIM))
        out.append(int(entry))
    return out


def split(vector: list[Fraction]) -> list[tuple[Fraction, Fraction]]:
    """z_k = a_k + i a_(16 + k) as (real, imaginary), k = 1..15."""
    return [(vector[k], vector[16 + k]) for k in range(1, 16)]


def main() -> int:
    rows = []
    for primary, twin in PAIRS:
        a, b = operand(*primary), operand(*twin)
        product = [Fraction(v) for v in cd_core.cd_multiply_exact(DIM, a, unit(16))]
        s_primary, s_twin = signs(*primary), signs(*twin)
        m = primary[0] ^ primary[1]
        aligned_primary = [s_primary[x] == s_primary[x ^ m] for x in range(DIM)]
        aligned_twin = [s_twin[x] == s_twin[x ^ m] for x in range(DIM)]
        row = {
            "primary": list(primary),
            "twin": list(twin),
            "xor_mask": m,
            "twin_is_primary_times_e16": product == b,
            "split_coordinates_times_i": [(-im, re) for re, im in split(a)] == split(b),
            "sign_relation_negated_bit4_flip": all(s_twin[x] == -s_primary[x ^ 16] for x in range(DIM)),
            "aligned_pairs": [sum(aligned_primary) // 2, sum(aligned_twin) // 2],
            "aligned_sets_equal": aligned_primary == aligned_twin,
            "signs_equal_without_the_flip": sum(int(p == q) for p, q in zip(s_primary, s_twin, strict=True)),
        }
        rows.append(row)
    control = signs(1, 18, 1)
    record = {
        "schema": "a5-hardware-twin-sign-relation-v1",
        "pairs": rows,
        "control_primary_against_itself_fails_the_relation": not all(
            control[x] == -control[x ^ 16] for x in range(DIM)
        ),
    }
    keys = ("twin_is_primary_times_e16", "split_coordinates_times_i", "sign_relation_negated_bit4_flip")
    record["pass"] = all(row[key] for row in rows for key in keys) and all(row["aligned_sets_equal"] for row in rows)
    record["pass"] = bool(record["pass"] and record["control_primary_against_itself_fails_the_relation"])
    (HERE / "twin-sign-relation.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0 if record["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
