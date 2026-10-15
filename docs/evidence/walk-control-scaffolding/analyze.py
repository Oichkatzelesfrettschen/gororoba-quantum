"""Total-variation distances and a uniformity test for the ripple walk members of one run.

Usage: analyze.py --run results/live/<run>. Reads the run's collect.json and
prints, for every walk member, the distances of the hardware and replayed
replica-0 laws from uniform and from each other, then a chi-square test of
the lane-0 readout0 hardware law against uniform at the member's shots.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats


def total_variation(first: np.ndarray, second: np.ndarray) -> float:
    return float(0.5 * np.abs(first - second).sum())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="run directory holding collect.json")
    parser.add_argument("--shots", type=int, default=1024, help="shots of the walk readout members")
    arguments = parser.parse_args()
    measurements = json.loads((arguments.run / "collect.json").read_text())[0]["family_measurements"]
    uniform = np.full(16, 1.0 / 16.0)
    print(f"{'member':55s} {'TV(hw,U)':>9s} {'TV(rp,U)':>9s} {'TV(hw,rp)':>9s}")
    for name in sorted(member for member in measurements if "walk" in member):
        hardware = np.asarray(measurements[name]["replica_probabilities"][0])
        replay = np.asarray(measurements[name]["replayed_replica_probabilities"][0])
        print(
            f"{name:55s} {total_variation(hardware, uniform):9.4f} "
            f"{total_variation(replay, uniform):9.4f} {total_variation(hardware, replay):9.4f}"
        )
    for name in sorted(member for member in measurements if "walk_lane0" in member and "readout0" in member):
        hardware = np.asarray(measurements[name]["replica_probabilities"][0])
        statistic, p_value = stats.chisquare(hardware * arguments.shots, uniform * arguments.shots)
        print(f"{name}: chi2 = {statistic:.1f}, p = {p_value:.2e}")


if __name__ == "__main__":
    main()
