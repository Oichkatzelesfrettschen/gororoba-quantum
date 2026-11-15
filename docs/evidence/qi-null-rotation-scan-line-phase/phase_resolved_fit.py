"""Exploratory: one error parameter that follows the shot-order line, fitted to the phase-bin contrasts.

Written before fitting: a single error parameter u oscillates with the line, u = u0 + s A cos(theta), theta = 0 at
the maximum of q4's P(1), s the sign of dP(q4 = 1)/du of the model at u0 for that arm. Data: the selector contrast
of each arm type in 8 phase bins pooled over its jobs (10 arm types, 80 points) plus the 10 mean q4-bit line
amplitudes. Parameters shared by all arms: u0, A. Noise: contraction share 0 at the retention where the exact
center reads visibility 0.42 through the mean bracket matrix. Candidates: z, x or y before each qubit's pulses or
all; conditional phase on each coupler or all; a z phase on one qubit after each of its CZs on one coupler.
Falsifier of a candidate: chi-square of the 80 contrast points above 124.8 (0.001 point, 78 degrees of freedom);
calibration: exact pulses with A = 0."""

import json
from typing import Any

import scan_fits
from scan_forward import HERE, pairs, region

import parallel


def main() -> None:
    cands: list[tuple[Any, Any, Any]] = (
        [scan_fits.NONE]
        + [("pulse", a + "b", q) for a in "zxy" for q in (*region, None)]
        + [("cz", None, None)]
        + [("cz", p, None) for p in pairs]
        + [("czz", q, p) for p in pairs for q in p]
    )
    out = parallel.ordered_map(scan_fits.phase_single, cands, min_items=2)
    out.sort(key=lambda r: r["total"])
    print("RANK")
    for r in out[:10]:
        print(r["cand"], r["total"], r["chi_contrast_80"], r["chi_q4amp_10"], r["u0"], r["A"])
    (HERE / "phase_resolved_fit.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
