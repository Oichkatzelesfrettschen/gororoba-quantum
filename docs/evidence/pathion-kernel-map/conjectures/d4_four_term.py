"""D4: the four-term blocks B12 (coset 2) and C8 (coset 5) on IBM against the Ascella readings of ledger row A5-188.

Normalization, fixed before the numbers. Ascella reports a' = (a - dark) / (anchor - dark) with the unit anchor and the
dark kernel arm. IBM has no unit anchor, so each placement's level L_x of arm x takes the dark kernel arm D as zero and
the basis-input arms E0 and E1 (ideal 1/4 in every block) as the scale:
    n_x = 0.25 * (L_x - L_D) / (mean(L_E0, L_E1) - L_D).
The top arm T is not forced to its ideal by this scale (a T and D scale would return the ideal by construction).
Arms are matched to the Ascella blocks of the same ideal level: B12 coset 2 matches Ascella blocks 2 and 7 on T, F, C, N
(0.75, 0.25, 0, 0.5625); C8 coset 5 matches all four Ascella C8 blocks on T and F (0.6545, 0.0691) and blocks 4 and 6
on N (0.4523); no Ascella C8 block carries the IBM C level 0, so that arm is not run.

Falsifier: the platforms disagree on a block class if any matched arm's IBM level n_x and Ascella class mean a' differ
by more than 0.07, the tolerance of the Ascella case (A5-188), or if either platform's class mean leaves its ideal by
more than 0.07. The IBM readings are the per-placement levels in collect.json (measured_statistics.summary_per_replica).
"""

import json
import math
from typing import Any

import numpy as np
from d_data import ASCELLA, run_dir
from scipy import stats

TOLERANCE = 0.07
CLASSES: dict[str, dict[str, Any]] = {
    "ftb_B12_c2": {"operand": "B12", "blocks": (2, 7), "arms": ("T", "F", "C", "N")},
    "ftb_C8_c5": {"operand": "C8", "blocks": (4, 5, 6, 7), "arms": ("T", "F", "N")},
}
ARM_BLOCKS = {("C8", "N"): (4, 6)}

readings = json.loads((ASCELLA / "analysis.json").read_bytes())["readings"]


def ascella(operand: str, arm: str, blocks: tuple[int, ...], ideal: float) -> list[float]:
    chosen = ARM_BLOCKS.get((operand, arm), blocks)
    return [
        r["a_prime"]
        for r in readings
        if r["operand"] == operand
        and r["role"] == "pathion"
        and r["arm"] == arm
        and r["block"] in chosen
        and abs(r["ideal"] - ideal) < 1e-6
    ]


print(
    f"falsifier: a matched arm differs between platforms by more than {TOLERANCE}, or a class mean leaves its ideal by more"
)
overall = True
for backend in ("ibm_fez", "ibm_kingston"):
    collected = json.loads((run_dir(backend) / "collect.json").read_bytes())[1]
    per = collected["measured_statistics"]["summary_per_replica"]
    print(f"== {backend}: {len(per)} placements")
    for prefix, spec in CLASSES.items():
        dark = np.array([p[f"{prefix}_level_D"] for p in per])
        scale = np.array([0.5 * (p[f"{prefix}_level_E0"] + p[f"{prefix}_level_E1"]) for p in per]) - dark
        visibility = np.array([p[f"{prefix}_visibility"] for p in per])
        print(
            f"  {prefix}: dark level {dark.mean():.4f}, basis level {np.mean(scale + dark):.4f}, T-D visibility {visibility.mean():.4f}"
        )
        for arm in spec["arms"]:
            ideal = per[0][f"{prefix}_level_ideal_{arm}"]
            level = np.array([p[f"{prefix}_level_{arm}"] for p in per])
            n = 0.25 * (level - dark) / scale
            se = n.std(ddof=1) / math.sqrt(n.size)
            half = stats.t.ppf(0.975, n.size - 1) * se
            asc = ascella(spec["operand"], arm, spec["blocks"], ideal)
            if not asc:
                print(f"    {arm:2s} ideal {ideal:.4f}: not run, no Ascella block carries this ideal level")
                continue
            asc_mean = float(np.mean(asc))
            gap = n.mean() - asc_mean
            ok = abs(gap) <= TOLERANCE and abs(n.mean() - ideal) <= TOLERANCE and abs(asc_mean - ideal) <= TOLERANCE
            overall &= ok
            print(
                f"    {arm:2s} ideal {ideal:.4f}  IBM n {n.mean():.4f} +- {se:.4f} (95 percent [{n.mean() - half:.4f}, {n.mean() + half:.4f}])"
                f"  Ascella a' {asc_mean:.4f} over {len(asc)} blocks (min {min(asc):.4f}, max {max(asc):.4f})  "
                f"IBM - Ascella {gap:+.4f}  IBM - ideal {n.mean() - ideal:+.4f}  Ascella - ideal {asc_mean - ideal:+.4f}  within {ok}"
            )
print(f"every matched arm within {TOLERANCE} of the other platform and of its ideal, on both IBM backends: {overall}")
print(
    "scope: IBM readings are one coset block per class on 16 or 17 placements; Ascella readings are 2 to 4 blocks per "
    "class, each one pooled reading, so the Ascella mean carries the block-to-block spread of the mesh and no placement error"
)
