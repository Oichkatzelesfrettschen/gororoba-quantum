"""Count-likelihood analysis of a collected patch-window run.

Every analyzed PUB binds to the submission: its job and position in
record.json, the collection's raw ledger, its own pub_index, and the
submitted circuit archive digest. Ramsey and measurement-window members are
fitted from counts: for idle time t, taken from the returned schedule, the
work qubit's X- and Y-basis readouts are binomial with
P(0) = (1 + V cos phi) / 2 and P(0) = (1 + V sin phi) / 2, where
phi(t) = phi0 + 2 pi delta t and V(t) = V0 exp(-gamma t). The detuning delta
is searched on a grid across its periodic basins and reported with a
profile-likelihood interval; a point whose visibility interval reaches zero
leaves its phase undefined. Populations carry Wilson intervals, which stay
finite at zero or full counts. Orbit contrasts use the multinomial variance.

Usage: "$PYTHON" scripts/patch_window_analysis.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/patch_window_analysis.py --self-check
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
from scipy.optimize import minimize

Z95 = 1.959963984540054
DELTA_GRID_MHZ = np.linspace(-0.5, 0.5, 201)
CONDITIONS = {
    "ramsey_plain": ("ramsey_plain_{q}_d{d}", 0),
    "ramsey_echo": ("ramsey_echo_{q}_d{d}", 0),
    "window_c0": ("window_measure_reset_c0_{q}_d{d}", 1),
    "window_c1": ("window_measure_reset_c1_{q}_d{d}", 1),
}


def wilson(successes: int, trials: int) -> tuple[float, float, float]:
    """Proportion with its Wilson 95 percent interval."""
    if trials <= 0:
        raise ValueError("an interval needs at least one trial")
    p = successes / trials
    centre = (p + Z95**2 / (2 * trials)) / (1 + Z95**2 / trials)
    half = Z95 * math.sqrt(p * (1 - p) / trials + Z95**2 / (4 * trials**2)) / (1 + Z95**2 / trials)
    return p, max(0.0, centre - half), min(1.0, centre + half)


def _bound_counts(run: Path) -> dict[str, Counter[str]]:
    record = json.loads((run / "record.json").read_text())
    submission = record["submission"]
    if hashlib.sha256((run / "isa.qpy").read_bytes()).hexdigest() != submission["qpy_archive_sha256"]:
        raise RuntimeError("isa.qpy differs from the submitted circuit archive")
    ledger = json.loads((run / "collect.json").read_text())[0]["jobs"]
    planned = {job["job_id"]: job for job in submission["jobs"]}
    if set(planned) != set(ledger):
        raise RuntimeError("collected jobs differ from the submitted jobs")
    counts: dict[str, Counter[str]] = {}
    for job_id, job in planned.items():
        directory = run / "raw" / job_id
        index = json.loads((directory / "index.json").read_text())
        raw_ledger = ledger[job_id].get("raw")
        if index.get("job_id", job_id) != job_id or (raw_ledger is not None and raw_ledger["files"] != index["files"]):
            raise RuntimeError(f"raw/{job_id} differs from the collection ledger")
        for position, member in enumerate(job["members"]):
            path = directory / f"pub_{position:02d}.json"
            if hashlib.sha256(path.read_bytes()).hexdigest() != index["files"].get(path.name):
                raise RuntimeError(f"{path} differs from its indexed sha256")
            payload = json.loads(path.read_text())
            if payload.get("pub_index", position) != position:
                raise RuntimeError(f"{path} carries PUB index {payload.get('pub_index')}")
            (register,) = payload["registers"].values()
            counts[member] = Counter(register["bitstrings"])
            _TIMING[member] = payload["metadata"]["compilation"].get("scheduler_timing", {}).get("timing", "")
    return counts


_TIMING: dict[str, str] = {}


def executed_idle_us(member: str, qubit: int, dt_seconds: float) -> float | None:
    """Free-precession time of one physical qubit: idle gaps between its first and last pulses, echo pulses excluded."""
    rows = [line.split(",") for line in _TIMING.get(member, "").splitlines()]
    pulses = sorted(
        (int(row[3]), int(row[4]))
        for row in rows
        if len(row) >= 6 and row[5] == "play" and row[2] == f"Qubit {qubit}" and not row[1].startswith(("INIT", "FINI"))
    )
    if len(pulses) < 2:
        return None
    idle = sum(max(0, b[0] - (a[0] + a[1])) for a, b in zip(pulses, pulses[1:], strict=False))
    return idle * dt_seconds * 1e6


def _ones(counts: Counter[str], clbit: int) -> tuple[int, int]:
    shots = sum(value for key, value in counts.items() if key != "__timing__")
    ones = sum(value for key, value in counts.items() if key != "__timing__" and key[-1 - clbit] == "1")
    return ones, shots


def fit_ramsey(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Binomial likelihood fit of phase and visibility against executed idle; delta over its periodic basins."""
    times = np.array([point["t_us"] for point in points])
    zeros = np.array([[point["x_zero"], point["y_zero"]] for point in points], dtype=float)
    shots = np.array([[point["x_shots"], point["y_shots"]] for point in points], dtype=float)

    def nll(params: np.ndarray, delta: float) -> float:
        phi0, log_v0, gamma = params
        visibility = math.exp(min(log_v0, 0.0)) * np.exp(-max(gamma, 0.0) * times)
        phase = phi0 + 2 * math.pi * delta * times
        probabilities = np.clip(
            np.stack([(1 + visibility * np.cos(phase)) / 2, (1 + visibility * np.sin(phase)) / 2], axis=1),
            1e-9,
            1 - 1e-9,
        )
        return float(-(zeros * np.log(probabilities) + (shots - zeros) * np.log(1 - probabilities)).sum())

    def profile(delta: float, start: np.ndarray) -> Any:
        return min(
            (minimize(nll, start + shift, args=(delta,), method="Nelder-Mead") for shift in (0.0, 1.5, -1.5)),
            key=lambda result: result.fun,
        )

    # A coarse grid finds the periodic basin; a free fit refines delta, and
    # bisection on the profile likelihood finds each interval edge.
    origin = np.array([0.0, -0.2, 0.02])
    coarse = min((profile(float(delta), origin).fun, float(delta)) for delta in DELTA_GRID_MHZ[::4])
    free = minimize(
        lambda v: nll(v[:3], float(v[3])), np.array([*profile(coarse[1], origin).x, coarse[1]]), method="Nelder-Mead"
    )
    best_delta, best_value, best_params = float(free.x[3]), float(free.fun), free.x[:3]

    def edge(direction: float) -> float | None:
        inner, outer = best_delta, best_delta + direction * 0.05
        if 2 * (profile(outer, best_params).fun - best_value) <= Z95**2:
            return None
        for _step in range(30):
            middle = (inner + outer) / 2
            if 2 * (profile(middle, best_params).fun - best_value) <= Z95**2:
                inner = middle
            else:
                outer = middle
        return (inner + outer) / 2

    low, high = edge(-1.0), edge(1.0)
    minimum = (best_value, best_delta, best_params)
    interval = [low if low is not None else best_delta - 0.05, high if high is not None else best_delta + 0.05]
    edge_hit = low is None or high is None
    phi0, log_v0, gamma = minimum[2]
    return {
        "delta_mhz": minimum[1],
        "delta_95_mhz": interval,
        "delta_resolved": not edge_hit,
        "phi0_rad": float(math.remainder(phi0, 2 * math.pi)),
        "visibility0": float(math.exp(min(log_v0, 0.0))),
        "decay_per_us": float(max(gamma, 0.0)),
        "negative_log_likelihood": minimum[0],
    }


def ramsey_points(
    counts: dict[str, Counter[str]],
    pattern: str,
    offset: int,
    qubit_clbit: int,
    delays: list[int],
    qubit: int,
    dt: float,
) -> list[dict[str, Any]]:
    points = []
    for delay in delays:
        x_name, y_name = pattern.format(q="x", d=delay), pattern.format(q="y", d=delay)
        if x_name not in counts or y_name not in counts:
            continue
        x_ones, x_shots = _ones(counts[x_name], offset + qubit_clbit)
        y_ones, y_shots = _ones(counts[y_name], offset + qubit_clbit)
        executed = executed_idle_us(x_name, qubit, dt)
        x = 1 - 2 * x_ones / x_shots
        y = 1 - 2 * y_ones / y_shots
        radius = math.hypot(x, y)
        se = math.sqrt((1 - x * x) / x_shots + (1 - y * y) / y_shots)
        points.append(
            {
                "member": x_name,
                "requested_dt": delay,
                "t_us": executed if executed is not None else delay * dt * 1e6,
                "timing": "executed schedule" if executed is not None else "requested delay",
                "x_zero": x_shots - x_ones,
                "x_shots": x_shots,
                "y_zero": y_shots - y_ones,
                "y_shots": y_shots,
                "visibility": radius,
                "phase_rad": math.atan2(y, x) if radius > Z95 * se else None,
            }
        )
    return points


def analyze(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    family = record["family_configuration"]
    delays = [int(delay) for delay in family["delays_dt"]]
    dt = float(family["dt_seconds"])
    patch = [int(qubit) for qubit in family["patch_qubits"]]
    counts = _bound_counts(run)
    report: dict[str, Any] = {"patch_qubits": patch, "delays_dt": delays, "dt_seconds": dt, "conditions": {}}
    for condition, (pattern, offset) in CONDITIONS.items():
        for role, clbit, qubit in (("work_a", 0, patch[1]), ("work_b", 1, patch[3])):
            points = ramsey_points(
                counts, pattern, offset, clbit, [0, *delays] if condition == "ramsey_plain" else delays, qubit, dt
            )
            if len(points) >= 2:
                report["conditions"][f"{condition}/{role}"] = {"points": points, "fit": fit_ramsey(points)}
    populations = {}
    for name, histogram in counts.items():
        if name.startswith("exchange_"):
            populations[name] = {
                role: wilson(*_ones(histogram, clbit))
                for clbit, role in enumerate(("work_a", "spectator", "work_b", "neighbor_a", "neighbor_b"))
            }
    report["exchange_populations"] = populations
    orbit = {}
    for context in ("nominal", "window_barrier", "window_echo"):
        arms = {}
        for arm in ("feedback", "no_feedback"):
            member = f"orbit_{context}_{arm}"
            if member not in counts:
                continue
            histogram = counts[member]
            total = sum(value for key, value in histogram.items() if key != "__timing__")
            law = [histogram.get(format(label, "02b"), 0) / total for label in range(4)]
            contrast = law[1] - law[3]
            arms[arm] = (contrast, (law[1] + law[3] - contrast**2) / total)
        if len(arms) == 2:
            difference = arms["feedback"][0] - arms["no_feedback"][0]
            orbit[context] = {
                "contrast_difference": difference,
                "se": math.sqrt(arms["feedback"][1] + arms["no_feedback"][1]),
            }
    report["orbit"] = orbit
    return report


def self_check() -> None:
    """Planted detuning recovery with interval coverage, and an unresolved phase at zero visibility."""
    rng = np.random.default_rng(20261013)
    truth, covered, trials = 0.06, 0, 20
    for _trial in range(trials):
        points = []
        for t in (0.0, 3.6, 5.6, 7.6):
            phase, visibility = 0.3 + 2 * math.pi * truth * t, 0.9 * math.exp(-0.03 * t)
            x0 = int(rng.binomial(1024, (1 + visibility * math.cos(phase)) / 2))
            y0 = int(rng.binomial(1024, (1 + visibility * math.sin(phase)) / 2))
            points.append({"t_us": t, "x_zero": x0, "x_shots": 1024, "y_zero": y0, "y_shots": 1024})
        fit = fit_ramsey(points)
        covered += fit["delta_95_mhz"][0] <= truth <= fit["delta_95_mhz"][1]
    if covered < 0.8 * trials:
        raise RuntimeError(f"planted detuning covered in {covered} of {trials} fits")
    flat = Counter({"0": 512, "1": 512})
    x_ones, x_shots = _ones(flat, 0)
    x, y = 1 - 2 * x_ones / x_shots, 0.0
    if math.hypot(x, y) > Z95 * math.sqrt(2 / 1024):
        raise RuntimeError("a zero-visibility point resolved a phase")
    p, low, high = wilson(0, 1024)
    if not (p == 0 and low == 0 and high > 0):
        raise RuntimeError("a zero-count Wilson interval collapsed")
    print(f"patch window analysis: planted detuning covered in {covered} of {trials} fits; boundary intervals finite")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.self_check:
        self_check()
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    report = analyze(arguments.run)
    for key, entry in report["conditions"].items():
        fit = entry["fit"]
        interval = [round(value * 1e3, 1) for value in fit["delta_95_mhz"]]
        print(f"{key:24s} delta {fit['delta_mhz'] * 1e3:+7.1f} kHz 95% {interval} V0 {fit['visibility0']:.3f}")
    for context, entry in report["orbit"].items():
        half = Z95 * entry["se"]
        print(f"orbit {context:15s} contrast difference {entry['contrast_difference']:+.3f} +/- {half:.3f}")
    if arguments.out:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
