"""C2 one-CZ null case: operating characteristics of the over-rotation worlds that also rotate Rz.

The case admits an X-axis over-rotation on the pulse gates X90 and X only, on the hypothesis that Rz is a frame change.
c2_one_cz_twins.txt section 4 lists two worlds outside that set whose 6-CZ response is nonzero: an X-axis rotation
before every single-qubit gate, Rz included (eps -0.0786: k4 s +0.0076, t +0.0103) and after every single-qubit gate
(eps -0.1150: k4 s -0.0040, t 0). This script runs the case's own decision rule (decide_estimates through
operating_characteristics) on both worlds at the design standard errors, stationary and with the case's batch drift, so
the share that reads "b0-like" (a wrong refutation of A5-186) is measured, not assumed. b0's twin contrast is set equal
to its base contrast, as for every over-rotation world of the case. Seed: value 1 of draw-2026-11-07T193501Z, read at
run time."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_one_cz_null_cases as case  # noqa: E402

WORLDS = {
    "over_rotation_x_all_before": {"s_b0": 0.0164, "t_b0": 0.0164, "s_k": 0.0076, "t_k": 0.0103},
    "over_rotation_x_all_after": {"s_b0": 0.0164, "t_b0": 0.0164, "s_k": -0.0040, "t_k": 0.0},
}


def main() -> None:
    case.PREDICTED = dict(WORLDS)
    case.WORLDS_SIZED = tuple(WORLDS)
    case.OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T193501Z.json"
    case.OC_SEED_INDEX = 1
    print(f"decision-label shares, {case.OC_DRAWS} simulated series per world, seed {case.OC_DRAW} value 1")
    for title, drift in (("stationary", 0.0), (f"batch drift sd {case.OC_DRIFT_SD}", case.OC_DRIFT_SD)):
        print(f"  {title}")
        for world, shares in case.operating_characteristics(drift_sd=drift).items():
            print(f"    {world}: " + ", ".join(f"{k} {v:.4f}" for k, v in shares.items()))


if __name__ == "__main__":
    main()
