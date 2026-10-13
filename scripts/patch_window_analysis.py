"""Phase, visibility, exchange and barrier-contrast analysis of a collected patch-window run.

Ramsey and readout-window members read each work qubit in the X or Y basis,
so P(0) - P(1) of the pair gives <X> and <Y>; the phase is atan2(<Y>, <X>)
and the visibility is their norm. A least-squares line of unwrapped phase
against idle time gives each condition's detuning. Exchange members report
every patch qubit's excited population after one work qubit is excited.
The barrier pair reports the orbit feed-forward signed contrasts. Every raw
PUB is checked against its collection sha256 before use.

Usage: "$PYTHON" scripts/patch_window_analysis.py RUN_DIR [--out FILE]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


def _counts(run: Path) -> dict[str, Counter[str]]:
    record = json.loads((run / "record.json").read_text())
    counts: dict[str, Counter[str]] = {}
    for job in record["submission"]["jobs"]:
        directory = run / "raw" / job["job_id"]
        indexed = json.loads((directory / "index.json").read_text())["files"]
        for index, member in enumerate(job["members"]):
            path = directory / f"pub_{index:02d}.json"
            if hashlib.sha256(path.read_bytes()).hexdigest() != indexed.get(path.name):
                raise RuntimeError(f"{path} differs from the sha256 retained by collection")
            (register,) = json.loads(path.read_text())["registers"].values()
            counts[member] = Counter(register["bitstrings"])
    return counts


def _expectation(counts: Counter[str], clbit: int) -> tuple[float, float]:
    """<Z> of one clbit after the basis change, and its binomial standard error."""
    shots = sum(counts.values())
    ones = sum(number for bits, number in counts.items() if bits[-1 - clbit] == "1")
    mean = 1 - 2 * ones / shots
    return mean, math.sqrt(max(1 - mean**2, 1e-12) / shots)


def _phase_series(counts: dict[str, Counter[str]], prefix: str, delays: list[int], offset: int) -> dict[str, Any]:
    series: dict[str, Any] = {}
    for label, clbit in (("work_a", offset), ("work_b", offset + 1)):
        points = []
        for delay in delays:
            x, x_error = _expectation(counts[f"{prefix}_x_d{delay}"], clbit)
            y, y_error = _expectation(counts[f"{prefix}_y_d{delay}"], clbit)
            points.append(
                {
                    "delay_dt": delay,
                    "x": x,
                    "y": y,
                    "phase_rad": math.atan2(y, x),
                    "visibility": math.hypot(x, y),
                    "phase_error_rad": math.hypot(x * y_error, y * x_error) / max(x * x + y * y, 1e-12),
                }
            )
        series[label] = {"points": points}
    return series


def _slope(points: list[dict[str, Any]], dt_seconds: float) -> dict[str, float]:
    times = np.array([point["delay_dt"] * dt_seconds * 1e6 for point in points])
    phases = np.unwrap([point["phase_rad"] for point in points])
    weights = 1 / np.array([max(point["phase_error_rad"], 1e-6) for point in points]) ** 2
    design = np.vstack([times, np.ones_like(times)]).T
    covariance = np.linalg.inv(design.T @ (weights[:, None] * design))
    slope, intercept = covariance @ design.T @ (weights * phases)
    return {
        "rad_per_us": float(slope),
        "rad_per_us_error": float(math.sqrt(covariance[0, 0])),
        "detuning_khz": float(slope / (2 * math.pi) * 1e3),
        "intercept_rad": float(intercept),
    }


def analyze(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    family = record["family_configuration"]
    delays = [int(delay) for delay in family["delays_dt"]]
    dt = float(family["dt_seconds"])
    counts = _counts(run)
    report: dict[str, Any] = {"patch_qubits": family["patch_qubits"], "delays_dt": delays, "dt_seconds": dt}
    conditions = {f"ramsey_{variant}": ("ramsey_" + variant, 0) for variant in ("plain", "echo")}
    conditions |= {f"readout_window_c{state}": (f"readout_window_c{state}", 1) for state in (0, 1)}
    for condition, (prefix, offset) in conditions.items():
        series = _phase_series(counts, prefix, delays, offset)
        for entry in series.values():
            entry["fit"] = _slope(entry["points"], dt)
        report[condition] = series
    report["readout_window_control_bit"] = {
        f"c{state}": {str(delay): _expectation(counts[f"readout_window_c{state}_x_d{delay}"], 0)[0] for delay in delays}
        for state in (0, 1)
    }
    exchange = {}
    readout_order = ("work_a", "spectator", "work_b", "neighbor_a", "neighbor_b")
    for target in ("work_a", "work_b"):
        exchange[target] = {
            str(delay): {
                role: (1 - _expectation(counts[f"exchange_{target}_d{delay}"], clbit)[0]) / 2
                for clbit, role in enumerate(readout_order)
            }
            for delay in delays
        }
    report["exchange_excited_population"] = exchange
    contrasts: dict[str, float] = {}
    barrier: dict[str, Any] = {}
    for arm in ("feedback", "no_feedback"):
        shots = counts[f"barrier_orbit_{arm}"]
        total = sum(shots.values())
        law = [shots.get(format(label, "02b"), 0) / total for label in range(4)]
        contrasts[arm] = law[1] - law[3]
        barrier[arm] = {"law": law, "signed_contrast": contrasts[arm]}
    barrier["contrast_difference"] = contrasts["feedback"] - contrasts["no_feedback"]
    report["barrier_orbit"] = barrier
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args(argv)
    report = analyze(arguments.run)
    for condition in ("ramsey_plain", "ramsey_echo", "readout_window_c0", "readout_window_c1"):
        for qubit, entry in report[condition].items():
            fit = entry["fit"]
            phases = ", ".join(f"{point['phase_rad']:+.3f}/{point['visibility']:.3f}" for point in entry["points"])
            print(
                f"{condition:18s} {qubit}: {fit['detuning_khz']:+7.2f} kHz "
                f"(+/- {fit['rad_per_us_error'] / (2 * math.pi) * 1e3:.2f})  phase/visibility {phases}"
            )
    for target, by_delay in report["exchange_excited_population"].items():
        print(f"exchange from {target}: {json.dumps(by_delay)}")
    print(f"barrier orbit: {json.dumps(report['barrier_orbit'])}")
    if arguments.out:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
