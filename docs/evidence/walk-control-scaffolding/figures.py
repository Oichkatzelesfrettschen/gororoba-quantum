"""Figures for the walk scaffold audit.

Usage: figures.py --run results/live/<run> --out DIR. Figure 1 plots hardware
and replayed P(0000) against walk depth, figure 2 the lane-0 readout0 laws,
and figure 3 an Aer depolarizing sweep of the executed 252-CZ readout
circuit. The sweep's generating script was not retained, so its points are
tabulated in SWEEP below as they were reported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAIRS = ((0, (25, 31)), (0, (9, 22)), (1, (25, 31)), (1, (9, 22)))
SWEEP = ((0.002, 0.6290), (0.005, 0.3372), (0.010, 0.1551), (0.015, 0.0960), (0.020, 0.0760))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    measurements = json.loads((arguments.run / "collect.json").read_text())[0]["family_measurements"]

    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
    for axis, (lane, pair) in zip(axes.flat, PAIRS, strict=True):
        names = [f"ripple_walk_lane{lane}_pair{pair[0]}_{pair[1]}_depth{depth}_packed" for depth in range(5)]
        axis.plot(range(5), [measurements[n]["replica_probabilities"][0][0] for n in names], "o-", label="hardware")
        replayed = [measurements[n]["replayed_replica_probabilities"][0][0] for n in names]
        axis.plot(range(5), replayed, "s--", label="calibrated replay")
        axis.set_title(f"lane {lane}, pair {pair[0]}-{pair[1]}")
        axis.set_xlabel("walk depth")
        axis.set_ylabel("P(0000)")
        axis.legend()
    figure.suptitle("Walk depth sweep: identical physical gates at every depth")
    figure.tight_layout()
    figure.savefig(arguments.out / "fig1_depth_sweep.png", dpi=120)

    figure, axis = plt.subplots(figsize=(12, 5))
    outcomes = np.arange(16)
    hardware = np.asarray(measurements["ripple_walk_lane0_readout0"]["replica_probabilities"][0])
    replay = np.asarray(measurements["ripple_walk_lane0_readout0"]["replayed_replica_probabilities"][0])
    axis.bar(outcomes - 0.25, hardware, 0.25, label="hardware")
    axis.bar(outcomes, replay, 0.25, label="calibrated replay")
    axis.bar(outcomes + 0.25, np.full(16, 1.0 / 16.0), 0.25, label="uniform")
    axis.set_xlabel("outcome")
    axis.set_ylabel("probability")
    axis.set_xticks(outcomes)
    axis.legend()
    axis.set_title("lane 0 readout0: prepare |0000>, 252 CZ, measure")
    figure.tight_layout()
    figure.savefig(arguments.out / "fig2_readout_dist.png", dpi=120)

    figure, axis = plt.subplots(figsize=(8, 5))
    axis.semilogx([p for p, _ in SWEEP], [value for _, value in SWEEP], "o-", label="Aer depolarizing sweep")
    axis.axhline(hardware[0], linestyle="--", label=f"hardware {hardware[0]:.3f}")
    axis.axhline(replay[0], linestyle=":", label=f"calibrated replay {replay[0]:.3f}")
    axis.set_xlabel("per-CZ depolarizing error")
    axis.set_ylabel("P(0000)")
    axis.legend()
    axis.set_title("Depolarizing sweep of the 252-CZ readout circuit")
    figure.tight_layout()
    figure.savefig(arguments.out / "fig3_noise_fit.png", dpi=120)


if __name__ == "__main__":
    main()
