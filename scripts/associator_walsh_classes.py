"""Census of associator Walsh spectra by doubling level, one class per distinct spectrum.

For the Cayley-Dickson algebra of dimension 2^n (cd_core.cd_sign) and a pair
of basis indices 0 < i < j, the associator phase omega_{i,j}(x) of
W = L_{e_i e_j}^dagger L_{e_i} L_{e_j} is a +-1 function on F_2^n
(predict.associator_phase) of algebraic degree max(1, bitlen(j) - 2)
(verify.py checks the degree for every pair through dimension 128). Its
Walsh transform W(y) = sum_x omega(x) (-1)^(x . y) is what the Design C
circuit samples: H^n, the diagonal phase, H^n, measure, with
P(y) = W(y)^2 / 4^n. This census groups every pair of one degree by the
multiset of |W(y)| and the collision probability K = sum_y P(y)^2, the
quantity two independent output samples estimate by their equality rate.
Pairs of one degree fall into several spectral classes from degree 3 on, so
the degree formula bounds the circuit cost and does not fix the output
distribution; the class is the finer invariant.

The census is finite evidence for the classification and no theorem: the
closed form of the classes, their multiplicities, and the comparison with
the published twist formulas (literature/notes/1602.02843.md) remain open.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

EXPECTED_CLASS_COUNTS = {8: 1, 16: 1, 32: 2, 64: 6}
EXPECTED_CUBIC_CLASSES = {
    ((0, 22), (8, 8), (16, 2)): (126, "5/32"),
    ((0, 24), (8, 7), (24, 1)): (234, "11/32"),
}


def walsh(values: np.ndarray) -> np.ndarray:
    """Unnormalized Walsh-Hadamard transform of a +-1 vector of power-of-two length."""
    amp = values.astype(np.int64).copy()
    h = 1
    while h < len(amp):
        for start in range(0, len(amp), 2 * h):
            lo = amp[start : start + h].copy()
            hi = amp[start + h : start + 2 * h].copy()
            amp[start : start + h] = lo + hi
            amp[start + h : start + 2 * h] = lo - hi
        h *= 2
    return amp


def spectral_class(phase: list[int]) -> tuple[tuple[tuple[int, int], ...], Fraction]:
    dim = len(phase)
    coefficients = walsh(np.array(phase))
    if int((coefficients.astype(np.int64) ** 2).sum()) != dim * dim:
        raise RuntimeError("Parseval fails")
    magnitudes = tuple(sorted(Counter(int(abs(w)) for w in coefficients).items()))
    collision = sum((Fraction(int(w) * int(w), dim * dim) ** 2 for w in coefficients), Fraction(0))
    return magnitudes, collision


def census(max_dim: int) -> dict[str, object]:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
    from predict import associator_phase

    levels: dict[str, dict[str, object]] = {}
    out: dict[str, object] = {"max_dim": max_dim, "levels": levels}
    dim = 8
    while dim <= max_dim:
        n = dim.bit_length() - 1
        degree = max(1, n - 2)
        classes: Counter[tuple[tuple[tuple[int, int], ...], Fraction]] = Counter()
        exemplars: dict[tuple[tuple[tuple[int, int], ...], Fraction], tuple[int, int]] = {}
        pairs = 0
        for i, j in itertools.combinations(range(1, dim), 2):
            if max(1, j.bit_length() - 2) != degree:
                continue  # the pair first appears at a lower level and is counted there
            key = spectral_class(associator_phase(dim, i, j))
            classes[key] += 1
            exemplars.setdefault(key, (i, j))
            pairs += 1
        level = {
            "degree": degree,
            "pairs_first_appearing": pairs,
            "class_count": len(classes),
            "classes": [
                {
                    "pairs": count,
                    "walsh_magnitudes": [list(item) for item in magnitudes],
                    "collision_probability": str(collision),
                    "exemplar": list(exemplars[(magnitudes, collision)]),
                }
                for (magnitudes, collision), count in sorted(classes.items(), key=lambda kv: (-kv[1], kv[0][1]))
            ],
        }
        levels[str(dim)] = level
        dim *= 2
    return out


def _check(result: dict[str, object]) -> None:
    levels = result["levels"]
    assert isinstance(levels, dict)
    for dim, want in EXPECTED_CLASS_COUNTS.items():
        if str(dim) in levels and levels[str(dim)]["class_count"] != want:
            raise RuntimeError(f"dim {dim}: {levels[str(dim)]['class_count']} classes, expected {want}")
    if "32" in levels:
        seen = {
            tuple(tuple(item) for item in c["walsh_magnitudes"]): (c["pairs"], c["collision_probability"])
            for c in levels["32"]["classes"]
        }
        if seen != EXPECTED_CUBIC_CLASSES:
            raise RuntimeError(f"dim 32 cubic classes read {seen}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-dim", type=int, default=128)
    parser.add_argument("--out", type=Path, help="JSON path; default prints a summary only")
    args = parser.parse_args()
    result = census(args.max_dim)
    _check(result)
    levels = result["levels"]
    assert isinstance(levels, dict)
    for dim, level in levels.items():
        pairs = level["pairs_first_appearing"]
        print(f"dim {dim}: degree {level['degree']}, {pairs} pairs, {level['class_count']} classes")
        for c in level["classes"]:
            magnitudes = c["walsh_magnitudes"]
            collision = c["collision_probability"]
            print(f"   {c['pairs']:5d} pairs  K = {collision:>8}  |W| {magnitudes}  e.g. {c['exemplar']}")
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
