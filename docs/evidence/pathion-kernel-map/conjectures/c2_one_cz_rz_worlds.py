"""C2 one-CZ null case: the over-rotation worlds that also rotate Rz, decided with the superseded b0-like band of 3.

The case admits an X-axis over-rotation on the pulse gates X90 and X only; cqasm.md lists Rz as native on Tuna-17, so the
hypothesis that Rz is a frame change, which would exempt it, is unverified. c2_one_cz_twins.txt section 4 lists two worlds
outside the admitted set whose 6-CZ response is nonzero: an X-axis rotation before every single-qubit gate, Rz included
(eps -0.0786: k4 s +0.0076, t +0.0103) and after every single-qubit gate (eps -0.1150: k4 s -0.0040, t 0). Both worlds are
now rows of scripts/qi_pathion_one_cz_null_cases.py PREDICTED, and the stored operating characteristics of
results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/prediction.json decide them with the case's band of
B0_LIKE_Z = 2 combined standard errors. This script only documents the result of the earlier band, B0_LIKE_Z = 3, at the
case's current shots: the world before every gate reads b0-like (a wrong refutation of A5-186) in a third of the series
(48 percent at the earlier shots of 65,536 for b0's base circuits).
b0's twin contrast is set equal to its base contrast, as for every over-rotation world of the case. Seed: value 1 of
draw-2026-11-07T193501Z, read at run time."""

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
    case.B0_LIKE_Z = 3.0
    print(
        f"decision-label shares at B0_LIKE_Z {case.B0_LIKE_Z}, {case.OC_DRAWS} simulated series per world, seed {case.OC_DRAW} value 1"
    )
    for title, drift in (("stationary", 0.0), (f"batch drift sd {case.OC_DRIFT_SD}", case.OC_DRIFT_SD)):
        print(f"  {title}")
        for world, shares in case.operating_characteristics(drift_sd=drift).items():
            print(f"    {world}: " + ", ".join(f"{k} {v:.4f}" for k, v in shares.items()))


if __name__ == "__main__":
    main()
