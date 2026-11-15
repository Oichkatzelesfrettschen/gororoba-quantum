"""Exploratory: one error parameter that follows the shot-order line, fitted to the phase-bin contrasts.

Written before fitting: a single error parameter u oscillates with the line, u = u0 + s A cos(theta), theta = 0 at
the maximum of q4's P(1), s the sign of dP(q4 = 1)/du of the model at u0 for that arm; where the model's q4 bit
has no response to u the alignment is unidentified and each such arm takes the s that scores lower (recorded as
`free_alignment_arms`). Data: the selector contrast of each `Rx` arm type in 8 phase bins pooled over its jobs (9
arm types, 72 points; the `X90` arm `b0` has no model row here) plus the 9 mean q4-bit line amplitudes. Parameters shared by all arms: u0, A. Noise: contraction share 0 at the retention where the exact
center reads visibility 0.42 through the mean bracket matrix. Candidates: z, x or y before each qubit's pulses or
all; conditional phase on each coupler or all; a z phase on one qubit after each of its CZs on one coupler.
Falsifier of a candidate: chi-square of the 72 contrast points above 112.3 (upper tail 0.001, 70 degrees of
freedom; `contrast_limit` in each row is computed from the selected data);
the alignment rule and this bound were set after the first fit, which scored the same 72 points against the
80-point bound 124.8 and took the alignment from the sign of a zero slope. A free alignment per arm is not removed
from the degrees of freedom, so the score of a candidate with free arms is a lower bound;
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
        print(r["cand"], r["total"], r["chi_contrast"], r["chi_q4amp"], r["u0"], r["A"])
    (HERE / "phase_resolved_fit.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
