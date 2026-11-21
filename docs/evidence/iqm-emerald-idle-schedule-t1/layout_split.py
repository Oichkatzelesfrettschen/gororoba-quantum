"""Per-layout gap split of the Emerald idle-schedule successor's analysis record.

For each qubit pulsed beside both train qubits (QB20 and QB26) and each train length, the per-pulse gap
g = d (k / k_T1 - 1) of each layout's arm, its shot-noise standard error, and the z-score of the layout difference;
then the mean and standard deviation of those z-scores. A gap set by the particular train qubit would separate the
layouts; a gap common to the control stack would not.

Usage: python3 docs/evidence/iqm-emerald-idle-schedule-t1/layout_split.py \
    results/iqm/idle_schedule_t1_emerald_analysis.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PRX_SECONDS = 24e-9
LAYOUTS = ("QB20", "QB26")


def split(record: dict) -> list[tuple[str, int, float, float, float, float, float]]:
    t1 = record["t1_delay"]
    gaps: dict[str, dict[tuple[str, int], tuple[float, float]]] = {}
    for layout, rows in record["h1_schedule"]["arms"].items():
        for qubit, arms in rows.items():
            k1, se_k1 = t1[qubit].get("rate_per_second"), t1[qubit].get("rate_se")
            if not k1:
                continue
            for arm in arms:
                if "apparent_rate_per_second" not in arm:
                    continue
                k, se_k = arm["apparent_rate_per_second"], arm["apparent_rate_se"]
                gap = PRX_SECONDS * (k / k1 - 1)
                se = PRX_SECONDS * math.hypot(se_k / k1, k * se_k1 / k1**2)
                gaps.setdefault(qubit, {})[(layout, arm["pulses"])] = (gap * 1e9, se * 1e9)
    out = []
    for qubit in sorted(gaps, key=lambda q: int(q[2:])):
        for pulses in (500, 1000):
            a, b = (gaps[qubit].get((layout, pulses)) for layout in LAYOUTS)
            if a and b:
                out.append((qubit, pulses, a[0], a[1], b[0], b[1], (a[0] - b[0]) / math.hypot(a[1], b[1])))
    return out


def main() -> int:
    rows = split(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    for qubit, pulses, a, sa, b, sb, z in rows:
        print(f"{qubit} {pulses} QB20 {a:.1f}+-{sa:.1f} QB26 {b:.1f}+-{sb:.1f} z {z:.1f}")
    zs = [row[-1] for row in rows]
    mean = sum(zs) / len(zs)
    sd = math.sqrt(sum((z - mean) ** 2 for z in zs) / len(zs))
    print(f"comparisons {len(zs)} z mean {mean:.2f} sd {sd:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
