"""Order of contact along the two measured incidence lines: how the extra kernel directions open as the operand leaves
the boundary orbit.

On W8 -> N- (a(b) = e1 + e10 + b (e18 - e25), N- at b = 1) and E8-bar -> VB (a(b) = e1 + e18 + b (e8 + e27), VB at
b = 0), the singular values of cd_core.left_mult_matrix(32, a) that vanish at the boundary are fitted against the
distance eps to it: the slope of log(sigma) against log(eps) is the order of contact of each group. The orders are
statements about the matrices. Hypothesis: a hardware contrast scanned toward the boundary shows the same orders;
testing it needs an observable-specific noisy forward model and a calibrated scan.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "gororoba_quantum"))
import cd_core  # noqa: E402

LINES = {
    "W8 -> N-": (lambda b: {1: 1.0, 10: 1.0, 18: b, 25: -b}, 1.0, 8, 16),
    "E8-bar -> VB": (lambda b: {1: 1.0, 18: 1.0, 8: b, 27: b}, 0.0, 8, 12),
}
EPS = (1e-1, 1e-2, 1e-3)


def operand(terms: dict[int, float]) -> np.ndarray:
    a = np.zeros(32)
    for k, x in terms.items():
        a[k] += x
    return a


def main() -> None:
    for name, (line, boundary, n_open, n_boundary) in LINES.items():
        rows = []
        for eps in EPS:
            b = boundary - eps if boundary else eps
            s = np.sort(np.linalg.svd(cd_core.left_mult_matrix(32, operand(line(b)).tolist()), compute_uv=False))
            rows.append(s[n_open:n_boundary])
        values = np.array(rows)
        groups = sorted({round(float(x), 6) for x in values[0]})
        print(f"{name}: {n_boundary - n_open} singular values vanish at the boundary")
        for g in groups:
            idx = np.flatnonzero(np.isclose(values[0], g, rtol=1e-4))
            slope = np.polyfit(np.log(EPS), np.log(values[:, idx[0]]), 1)[0]
            coef = values[-1, idx[0]] / EPS[-1] ** round(slope)
            print(f"  {len(idx)} values: sigma ~ {coef:.4f} eps^{slope:.3f}")


if __name__ == "__main__":
    main()
