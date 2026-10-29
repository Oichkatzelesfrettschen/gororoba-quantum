"""Render the observed reporter margin and activity contrasts."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

root = Path("docs/evidence/ibm-fez-actor-pilot")
result = json.loads((root / "analysis.json").read_bytes())
rows = result["conditions"]
contrasts = sorted(result["actor_contrasts"], key=lambda row: (row["delay_us"], row["input"]))
figure, axes = plt.subplots(2, 1, figsize=(13, 9), layout="constrained")
positions = np.arange(12)
width = 0.38
for arm, offset, color in (("idle", -width / 2, "#246b94"), ("active", width / 2, "#d17837")):
    values = [
        100
        * next(
            row["gain"] for row in rows if row["delay_us"] == delay and row["input"] == pattern and row["arm"] == arm
        )
        for delay in (30, 50, 250)
        for pattern in range(4)
    ]
    axes[0].bar(positions + offset, values, width, label=arm, color=color)
axes[0].axhline(0, color="black", linewidth=0.8)
axes[0].set_ylabel("Parity advantage G (percentage points)")
axes[0].set_title("Reporter pair: negative advantage in all observed conditions")
axes[0].legend()
for field, offset, label, color in (
    ("delta_p0", -width / 2, "Reporter 0", "#246b94"),
    ("delta_p1", width / 2, "Reporter 1", "#d17837"),
):
    axes[1].bar(positions + offset, [100 * row[field] for row in contrasts], width, label=label, color=color)
axes[1].axhline(0, color="black", linewidth=0.8)
axes[1].set_ylabel("Active minus idle error rate (percentage points)")
axes[1].set_title("Activity-associated contrasts: descriptive, without confidence intervals")
axes[1].legend()
labels = [f"{delay} µs\ninput {pattern:02b}" for delay in (30, 50, 250) for pattern in range(4)]
for axis in axes:
    axis.set_xticks(positions, labels)
figure.savefig(root / "reporter-pair-and-activity.png", dpi=170)
plt.close(figure)
