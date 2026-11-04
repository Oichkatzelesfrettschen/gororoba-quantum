"""Rank of the Jacobian of Phi (9 x 5) at explicit parameters, exact over F_p by dual numbers (python-flint)."""

from __future__ import annotations

import json
import sys

import laurent as Lm
from arc_targets import TARGETS, Target
from flint import nmod_mat

POINT_NAMES = ("w", "rho", "sigma", "e", "zeta")
POINT = (2, 5, 7, 3, 11)  # w = m - 1
PREC = 20


def jacobian_rank(target: Target, point: tuple[int, ...] = POINT) -> int:
    """Rank of the 9 x 5 matrix of first-order coefficients of Phi in the five parameters."""
    p = target.prime
    cols = []
    for i in range(len(point)):
        vals = [Lm.L.const(v, PREC, p) for v in point]
        vals[i] = vals[i] + Lm.L.mono(1, 1, PREC, p)
        xs = [x.to_series(3) for x in Lm.phi_laurent(target, *vals)]
        cols.append([xs[k].coeff(1) for k in range(9)])
    mat = nmod_mat(9, len(point), [cols[c][r] for r in range(9) for c in range(len(point))], p)
    return int(mat.rank())


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    res = {"point": dict(zip(POINT_NAMES, POINT, strict=True)), "rank": jacobian_rank(target)}
    (target.directory / "phi_rank.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
