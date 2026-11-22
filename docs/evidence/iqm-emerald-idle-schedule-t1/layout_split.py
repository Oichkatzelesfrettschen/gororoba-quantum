"""Per-layout gap split of the Emerald idle-schedule successor's analysis record.

For each qubit pulsed beside both train qubits (QB20 and QB26) and each train length, the per-pulse gap
g = d (k / k_T1 - 1) of each layout's arm, its shot-noise standard error, and the z-score of the layout difference;
then the mean and standard deviation of those z-scores. A gap set by the particular train qubit would separate the
layouts; a gap common to the control stack would not.

Both layouts divide by the same fitted delay rate k_T1 of the qubit, so the difference
g_a - g_b = d (k_a - k_b) / k_T1 is propagated jointly: its variance is
(d / k_T1)^2 (se_a^2 + se_b^2 + ((k_a - k_b) se_T1 / k_T1)^2), which counts the shared T1 error once.

Usage: python3 docs/evidence/iqm-emerald-idle-schedule-t1/layout_split.py \
    results/iqm/idle_schedule_t1_emerald_analysis.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "gororoba_quantum"))

from parallel import ordered_map  # noqa: E402

PRX_SECONDS = 24e-9
LAYOUTS = ("QB20", "QB26")

Item = tuple[str, int, float, float, float, float, float, float]


def compare(item: Item) -> tuple[str, int, float, float, float, float, float]:
    """Gaps of both layouts in ns with their marginal standard errors, and the z-score of their joint difference."""
    qubit, pulses, ka, se_a, kb, se_b, k1, se_k1 = item

    def gap(k: float, se_k: float) -> tuple[float, float]:
        return PRX_SECONDS * (k / k1 - 1) * 1e9, PRX_SECONDS * math.hypot(se_k / k1, k * se_k1 / k1**2) * 1e9

    (ga, sa), (gb, sb) = gap(ka, se_a), gap(kb, se_b)
    se_diff = PRX_SECONDS / k1 * math.sqrt(se_a**2 + se_b**2 + ((ka - kb) * se_k1 / k1) ** 2) * 1e9
    return qubit, pulses, ga, sa, gb, sb, (ga - gb) / se_diff


def items(record: dict[str, Any]) -> list[Item]:
    t1 = record["t1_delay"]
    rates: dict[str, dict[tuple[str, int], tuple[float, float]]] = {}
    for layout, rows in record["h1_schedule"]["arms"].items():
        for qubit, arms in rows.items():
            if not t1[qubit].get("rate_per_second"):
                continue
            for arm in arms:
                if "apparent_rate_per_second" in arm:
                    key = (layout, arm["pulses"])
                    rates.setdefault(qubit, {})[key] = (arm["apparent_rate_per_second"], arm["apparent_rate_se"])
    out = []
    for qubit in sorted(rates, key=lambda q: int(q[2:])):
        k1, se_k1 = t1[qubit]["rate_per_second"], t1[qubit]["rate_se"]
        for pulses in (500, 1000):
            a, b = (rates[qubit].get((layout, pulses)) for layout in LAYOUTS)
            if a and b:
                out.append((qubit, pulses, a[0], a[1], b[0], b[1], k1, se_k1))
    return out


def main() -> int:
    rows = ordered_map(compare, items(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
    for qubit, pulses, a, sa, b, sb, z in rows:
        print(f"{qubit} {pulses} QB20 {a:.1f}+-{sa:.1f} QB26 {b:.1f}+-{sb:.1f} z {z:.2f}")
    zs = [row[-1] for row in rows]
    mean = sum(zs) / len(zs)
    sd = math.sqrt(sum((z - mean) ** 2 for z in zs) / len(zs))
    print(f"comparisons {len(zs)} z mean {mean:.2f} sd {sd:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
