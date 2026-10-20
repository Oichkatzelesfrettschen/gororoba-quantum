"""Preregistered decay and detuning fit of the n21-orbit-rca ground Ramsey sweep.

The sweep (live_run.py --ground-control-split --ramsey-windows) reads logical
qubit 2 in X and Y at once after its preparation (immediate) and after idles
of whole multiples of the control's measure plus reset durations with the
control held in |0> (idle_ground at each multiple). Each member's exposure t
is the compiled gap between the spectator's preparation pulse and its basis
change in the returned schedule, so pulse edges never enter the time axis.

Model. Over the shots whose initialization herald reads the control 0,
each member's quadrature expectation is

    <X>(t) = b + A exp(-(t / T)^beta) cos(2 pi delta t + phi0)
    <Y>(t) = b + A exp(-(t / T)^beta) sin(2 pi delta t + phi0)

with t in microseconds and delta in MHz. A rz(+theta) on qubit 2 advances
phi by +theta, since Y reads through sdg and h, so delta > 0 is a phase
advance at the rate of rz(+2 pi delta t). b is a common readout offset. The
fit is the binomial maximum likelihood over every member's X and Y counts
jointly, so a low visibility enters through its counts and never through
hypot or atan2 of noisy expectations; visibility and phase per member are
derived descriptions.

Decisions, each at FAMILY_ALPHA / 3 (Bonferroni over the spectator herald
admission, the detuning test and the decay-shape test):
- herald admission: n21_orbit_rca.herald_report over the sweep members,
  conditioned on the control's herald bit; a refused or unevaluable herald
  leaves both tests not_admissible.
- detuning: the two-sided Wald interval of delta in the free-beta fit;
  "detuned" when it excludes 0, else "unresolved" with the interval as
  the bound. delta is identified modulo 1 / (largest exposure gap), so the
  report carries the alias bound 1 / (2 gap) the grid sets.
- decay shape: the two-sided Wald interval of beta in the free-beta fit;
  "exponential" when it holds 1 and excludes 2, "gaussian" when it holds 2
  and excludes 1, "unresolved" when it holds both, "neither" when it holds
  neither. T2* is reported from the free fit and from both fixed-beta fits.

--design prints the Fisher-information precision of a grid at stated truths
and shots (no sampling); --self-check runs the planted truths; --check
regenerates RUN_DIR/ramsey.json from the archived circuits and raw files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import n21_orbit_rca as rca  # noqa: E402

import parallel  # noqa: E402

FAMILY_ALPHA = 0.05
TESTS = ("spectator_herald_admission", "detuning", "decay_shape")
TEST_ALPHA = FAMILY_ALPHA / len(TESTS)
SCHEMA = "n21-spectator-ramsey-v1"
RETAINED = "ramsey.json"
PARAMETERS = ("amplitude", "t2_star_us", "beta", "detuning_mhz", "phi0", "offset")
QUADRATURES = ("x", "y")
# Parameter bounds of the likelihood search: beta spans sub-exponential to
# super-Gaussian decay, T2* spans 0.5 to 500 us, the offset is a readout
# asymmetry of a few percent.
BOUNDS = ((0.0, 1.2), (0.5, 500.0), (0.5, 4.0), (None, None), (None, None), (-0.2, 0.2))
DETUNING_STARTS = 25
# Exposures above this many dt read the member as an idle; immediate's
# preparation and basis-change pulses abut.
SPECTATOR_PULSES = 2


def mean_expectation(params: np.ndarray, times: np.ndarray, quadratures: np.ndarray) -> np.ndarray:
    """<Q> of every (time, quadrature) point; quadratures holds 0 for X and 1 for Y."""
    amplitude, t2, beta, detuning, phi0, offset = params
    envelope = amplitude * np.exp(-np.power(times / t2, beta))
    angle = 2.0 * math.pi * detuning * times + phi0
    return offset + envelope * np.where(quadratures == 0, np.cos(angle), np.sin(angle))


def _clipped(mean: np.ndarray) -> np.ndarray:
    return np.clip(mean, -1.0 + 1e-12, 1.0 - 1e-12)


def negative_log_likelihood(
    params: np.ndarray, times: np.ndarray, quadratures: np.ndarray, zeros: np.ndarray, shots: np.ndarray
) -> float:
    probability = (1.0 + _clipped(mean_expectation(params, times, quadratures))) / 2.0
    return float(-(zeros * np.log(probability) + (shots - zeros) * np.log1p(-probability)).sum())


def fisher_covariance(
    params: np.ndarray, times: np.ndarray, quadratures: np.ndarray, shots: np.ndarray, free: tuple[int, ...]
) -> np.ndarray:
    """Inverse expected Fisher information of the free parameters.

    A binomial read of p = (1 + mu) / 2 carries information n / (1 - mu^2)
    about mu; the Jacobian of mu is taken by central differences.
    """
    mean = _clipped(mean_expectation(params, times, quadratures))
    jacobian = np.empty((times.size, len(free)))
    for column, index in enumerate(free):
        step = 1e-6 * max(1.0, abs(float(params[index])))
        upper, lower = params.copy(), params.copy()
        upper[index] += step
        lower[index] -= step
        jacobian[:, column] = (
            mean_expectation(upper, times, quadratures) - mean_expectation(lower, times, quadratures)
        ) / (2 * step)
    weights = shots / (1.0 - mean**2)
    information = jacobian.T @ (weights[:, None] * jacobian)
    return np.asarray(np.linalg.pinv(information))


class StartFit:
    """One bounded likelihood search from a detuning start; module level so the pool pickles it."""

    def __init__(self, data: tuple[np.ndarray, ...], fixed_beta: float | None, start: np.ndarray) -> None:
        self.data = data
        self.fixed_beta = fixed_beta
        self.start = start

    def __call__(self, detuning: float) -> tuple[float, list[float]]:
        times, quadratures, zeros, shots = self.data
        initial = self.start.copy()
        initial[3] = detuning
        bounds = list(BOUNDS)
        if self.fixed_beta is not None:
            initial[2] = self.fixed_beta
            bounds[2] = (self.fixed_beta, self.fixed_beta)
        result = minimize(
            negative_log_likelihood,
            initial,
            args=(times, quadratures, zeros, shots),
            method="L-BFGS-B",
            bounds=bounds,
        )
        return float(result.fun), [float(value) for value in result.x]


def alias_bound_mhz(times: np.ndarray) -> float:
    """Largest |delta| the grid identifies: 1 / (2 gap) over the largest gap between distinct exposures."""
    distinct = np.unique(times)
    return float(1.0 / (2.0 * np.diff(distinct).max()))


def fit_model(
    times: np.ndarray, quadratures: np.ndarray, zeros: np.ndarray, shots: np.ndarray, fixed_beta: float | None
) -> dict[str, Any]:
    """Binomial maximum likelihood with Wald intervals; fixed_beta None fits beta free.

    Starts span delta over the alias band; the start phase is the immediate
    member's atan2 and the start amplitude its hypot.
    """
    data = (times, quadratures, zeros, shots)
    expectation = 2.0 * zeros / shots - 1.0
    first = times == times.min()
    x0 = float(expectation[first & (quadratures == 0)].mean())
    y0 = float(expectation[first & (quadratures == 1)].mean())
    later = times[times > times.min()]
    start = np.array(
        [
            min(1.0, math.hypot(x0, y0)),
            float(np.median(later)) if later.size else 1.0,
            1.0,
            0.0,
            math.atan2(y0, x0),
            0.0,
        ]
    )
    alias = alias_bound_mhz(times)
    starts = [float(value) for value in np.linspace(-alias, alias, DETUNING_STARTS)]
    found = parallel.ordered_map(StartFit(data, fixed_beta, start), starts, min_items=DETUNING_STARTS + 1)
    value, best = min(found, key=lambda item: (round(item[0], 9), abs(item[1][3])))
    params = np.array(best)
    # On a uniform exposure lattice of spacing gap, delta and delta + k / gap
    # predict the same counts; the estimate is folded into the alias band.
    params[3] = math.remainder(params[3], 2 * alias)
    params[4] = math.remainder(params[4], 2 * math.pi)
    free = tuple(index for index in range(len(PARAMETERS)) if not (fixed_beta is not None and index == 2))
    covariance = fisher_covariance(params, times, quadratures, shots, free)
    errors = dict.fromkeys(PARAMETERS, 0.0)
    for column, index in enumerate(free):
        errors[PARAMETERS[index]] = float(math.sqrt(max(covariance[column, column], 0.0)))
    return {
        "beta": "free" if fixed_beta is None else fixed_beta,
        "negative_log_likelihood": value,
        "estimates": dict(zip(PARAMETERS, (float(v) for v in params), strict=True)),
        "standard_errors": errors,
        "alias_bound_mhz": alias,
    }


def interval(estimate: float, error: float, alpha: float) -> list[float]:
    quantile = float(norm.ppf(1 - alpha / 2))
    return [estimate - quantile * error, estimate + quantile * error]


def decisions(free: dict[str, Any], alpha: float = TEST_ALPHA) -> dict[str, Any]:
    """The preregistered detuning and decay-shape verdicts of the free-beta fit at alpha each."""
    estimates, errors = free["estimates"], free["standard_errors"]
    detuning = interval(estimates["detuning_mhz"], errors["detuning_mhz"], alpha)
    beta = interval(estimates["beta"], errors["beta"], alpha)
    holds = {value: beta[0] <= value <= beta[1] for value in (1.0, 2.0)}
    shape = (
        "unresolved"
        if all(holds.values())
        else "exponential"
        if holds[1.0]
        else "gaussian"
        if holds[2.0]
        else "neither"
    )
    return {
        "detuning": {
            "status": "detuned" if detuning[0] > 0 or detuning[1] < 0 else "unresolved",
            "estimate_khz": 1e3 * estimates["detuning_mhz"],
            "interval_khz": [1e3 * value for value in detuning],
            "alias_bound_khz": 1e3 * free["alias_bound_mhz"],
            "alpha": alpha,
        },
        "decay_shape": {
            "status": shape,
            "beta": estimates["beta"],
            "interval": beta,
            "t2_star_us": estimates["t2_star_us"],
            "t2_star_interval_us": interval(estimates["t2_star_us"], errors["t2_star_us"], alpha),
            "alpha": alpha,
        },
    }


def fit_counts(points: list[tuple[float, str, int, int]], alpha: float = TEST_ALPHA) -> dict[str, Any]:
    """Every fit and verdict of (exposure_us, quadrature, zeros, shots) points."""
    times = np.array([point[0] for point in points], dtype=float)
    quadratures = np.array([QUADRATURES.index(point[1]) for point in points])
    zeros = np.array([point[2] for point in points], dtype=float)
    shots = np.array([point[3] for point in points], dtype=float)
    fits = {
        "free": fit_model(times, quadratures, zeros, shots, None),
        "exponential": fit_model(times, quadratures, zeros, shots, 1.0),
        "gaussian": fit_model(times, quadratures, zeros, shots, 2.0),
    }
    by_time: dict[float, dict[str, float]] = {}
    for time, quadrature, zero, shot in points:
        by_time.setdefault(time, {})[quadrature] = 2.0 * zero / shot - 1.0
    derived = [
        {
            "exposure_us": time,
            "visibility": math.hypot(values["x"], values["y"]),
            "phase": math.atan2(values["y"], values["x"]),
        }
        for time, values in sorted(by_time.items())
    ]
    return {"fits": fits, "decisions": decisions(fits["free"], alpha), "derived": derived}


def expected_points(
    truth: dict[str, float], exposures_us: list[float], shots: int
) -> list[tuple[float, str, int, int]]:
    """Noise-free counts round(n p) of a truth at every exposure and quadrature."""
    params = np.array([truth[name] for name in PARAMETERS])
    points = []
    for time in exposures_us:
        for index, quadrature in enumerate(QUADRATURES):
            mean = float(mean_expectation(params, np.array([time]), np.array([index]))[0])
            points.append((time, quadrature, round(shots * (1.0 + mean) / 2.0), shots))
    return points


def design_precision(truth: dict[str, float], exposures_us: list[float], shots: int) -> dict[str, Any]:
    """Expected Wald half-widths at TEST_ALPHA of the free and fixed-beta fits at the truth's Fisher information."""
    params = np.array([truth[name] for name in PARAMETERS])
    times = np.repeat(np.array(exposures_us, dtype=float), len(QUADRATURES))
    quadratures = np.tile(np.arange(len(QUADRATURES)), len(exposures_us))
    counts = np.full(times.size, float(shots))
    quantile = float(norm.ppf(1 - TEST_ALPHA / 2))
    report: dict[str, Any] = {"truth": truth, "exposures_us": exposures_us, "shots_per_circuit": shots}
    for label, free in (("free", (0, 1, 2, 3, 4, 5)), ("fixed_beta", (0, 1, 3, 4, 5))):
        covariance = fisher_covariance(params, times, quadratures, counts, free)
        report[label] = {
            PARAMETERS[index]: quantile * math.sqrt(max(covariance[column, column], 0.0))
            for column, index in enumerate(free)
        }
    report["detuning_half_width_khz"] = 1e3 * report["free"]["detuning_mhz"]
    report["alias_bound_khz"] = 1e3 * alias_bound_mhz(times)
    return report


# Run reading. Member names come from qpe_diagnostics.n21_ramsey_name; the
# control is the one wire every member resets after the spectator's readout.


def member_key(name: str) -> tuple[int, str] | None:
    """(idle multiple, quadrature) of a sweep member; immediate reads multiple 0."""
    from qpe_diagnostics import n21_ramsey_multiple

    if name.startswith(f"{rca.SPECTATOR_PREFIX}immediate_"):
        quadrature = name.rsplit("_", 1)[1]
        return (0, quadrature) if quadrature in QUADRATURES else None
    return n21_ramsey_multiple(name)


def is_sweep(names: list[str]) -> bool:
    """Whether a record's members are the ground Ramsey sweep: an idle_ground member with an idle multiple."""
    from qpe_diagnostics import n21_ramsey_multiple

    return any(n21_ramsey_multiple(name) is not None for name in names)


def member_schedule(plays: list[tuple[int, int, str, int]], control: int, control_delay_dt: int) -> dict[str, Any]:
    """ground_member_schedule with the count of spectator pulses before its readout.

    A sweep member plays exactly the preparation and the basis change on
    the spectator, so any further pulse, such as a dynamical-decoupling X
    inside the idle, turns the Ramsey into an echo and is counted here.
    """
    schedule = rca.ground_member_schedule(plays, control, control_delay_dt)
    readout = max(play[0] for play in plays if play[2] == "measure" and play[3] == schedule["spectator"])
    schedule["spectator_pulses"] = sum(
        1 for play in plays if play[3] == schedule["spectator"] and play[2] != "measure" and play[0] < readout
    )
    return schedule


def admissibility(
    schedules: dict[str, dict[str, Any]], names: list[str], control: int, window_dt: int
) -> dict[str, Any]:
    """Whether every sweep member exposes the spectator as built.

    immediate: exposure 0, no control delay, control prepared (as the split
    builds it); idle_ground at multiple m: exposure and control delay m *
    window_dt and an unprepared control; every member: one spectator other
    than the control and SPECTATOR_PULSES pulses before its readout.
    """
    missing = [name for name in names if name not in schedules]
    spectators = {schedule["spectator"] for schedule in schedules.values()}
    differing: dict[str, Any] = {}
    unresolved: dict[str, list[str]] = {}
    if len(spectators) > 1 or control in spectators:
        unresolved["spectator"] = [f"the members read spectators {sorted(spectators)} beside control {control}"]
    for name, schedule in schedules.items():
        key = member_key(name)
        if key is None:
            unresolved[name] = ["not a sweep member"]
            continue
        window = key[0] * window_dt
        expected = {
            "exposure_dt": window,
            "control_prepared": key[0] == 0,
            "control_delay_dt": window,
            "spectator_pulses": SPECTATOR_PULSES,
        }
        found = {field: schedule[field] for field in expected}
        if found != expected:
            differing[name] = {"expected": expected, "found": found}
    return {
        "admissible": not (missing or differing or unresolved),
        "differing": differing,
        "unresolved": unresolved,
        "missing": missing,
        "control": control,
        "window_dt": window_dt,
        "schedules": schedules,
    }


def run_schedules(run: Path) -> tuple[dict[str, dict[str, Any]], int, dict[str, list[str]]]:
    names = [member["name"] for member in rca._group(run)["members"]]
    circuits = rca._circuits(run)
    resets = {
        circuit.find_bit(instruction.qubits[0]).index
        for circuit in circuits
        for instruction in circuit.data
        if instruction.operation.name == "reset"
    }
    if len(resets) != 1:
        raise RuntimeError(f"the sweep members reset qubits {sorted(resets)}, not one control")
    (control,) = resets
    schedules: dict[str, dict[str, Any]] = {}
    unresolved: dict[str, list[str]] = {}
    for name, circuit, payload in zip(names, circuits, rca.raw_pubs(run), strict=True):
        delays = [
            instruction.operation
            for instruction in circuit.data
            if instruction.operation.name == "delay" and circuit.find_bit(instruction.qubits[0]).index == control
        ]
        if any(delay.unit != "dt" for delay in delays):
            unresolved[name] = ["a control delay is not in dt"]
            continue
        try:
            _program, prefix = rca.herald_program(circuit)
            plays = rca._without_prefix(rca._plays(payload), prefix)
            schedules[name] = member_schedule(plays, control, sum(int(delay.duration) for delay in delays))
        except ValueError as error:
            unresolved[name] = [str(error)]
    return schedules, control, unresolved


def conditioned_zeros(phases: list[str], heralds: list[str], positions: tuple[int, ...]) -> tuple[int, int]:
    """(qubit-2 zeros, shots) over the shots whose herald string reads 0 at every position; clbit 1 is qubit 2."""
    if len(heralds) != len(phases):
        raise RuntimeError(f"{len(heralds)} herald and {len(phases)} phase shots")
    kept = [value for value, herald in zip(phases, heralds, strict=True) if all(herald[k] == "0" for k in positions)]
    return sum(value[0] == "0" for value in kept), len(kept)


# Selections over the initialization herald. Qubit 143 couples on the Fez
# coupling map (docs/evidence/heron_platform/targets.json, cz qargs) to 136,
# 142 and 144, every other pinned qubit, so an excited neighbor of any role
# shifts its frequency by that ZZ. The primary selection keeps the shots
# whose herald reads all four pinned qubits 0; control-only is secondary.
SELECTIONS = ("all_zero", "control_zero")


def run_reads(run: Path, control: int) -> tuple[dict[str, dict[str, tuple[int, int]]] | None, dict[str, Any]]:
    """Per selection and member, herald-conditioned (zeros, shots) of qubit 2; None without the herald."""
    from qpe_diagnostics import HERALD_REGISTER, register_role

    names = [member["name"] for member in rca._group(run)["members"]]
    reads: dict[str, dict[str, tuple[int, int]]] = {selection: {} for selection in SELECTIONS}
    totals: dict[str, int] = {}
    for name, circuit, payload in zip(names, rca._circuits(run), rca.raw_pubs(run), strict=True):
        registers = [register for register in circuit.cregs if register_role(register.name) == HERALD_REGISTER]
        if not registers:
            return None, {"present": False}
        (register,) = registers
        writer = {
            circuit.find_bit(i.clbits[0]).index: circuit.find_bit(i.qubits[0]).index
            for i in circuit.data
            if i.operation.name == "measure"
        }
        bits = [k for k, clbit in enumerate(register) if writer[circuit.find_bit(clbit).index] == control]
        if len(bits) != 1:
            raise RuntimeError(f"{name} reads the control {control} on herald bits {bits}, not one")
        heralds = payload["registers"][register.name]["bitstrings"]
        phases = payload["registers"][rca.REGISTER]["bitstrings"]
        everything = tuple(register.size - 1 - k for k in range(register.size))
        reads["all_zero"][name] = conditioned_zeros(phases, heralds, everything)
        reads["control_zero"][name] = conditioned_zeros(phases, heralds, (register.size - 1 - bits[0],))
        totals[name] = len(phases)
    return reads, {
        "present": True,
        "control": control,
        "primary": "all_zero: keep shots whose initialization herald reads every pinned qubit 0",
        "secondary": "control_zero: keep shots whose initialization herald reads the control 0",
        "kept_shots": {
            selection: {name: [reads[selection][name][1], totals[name]] for name in totals} for selection in SELECTIONS
        },
    }


def selection_admission(reads: dict[str, tuple[int, int]], totals: dict[str, int], alpha: float) -> dict[str, Any]:
    """Whether the rejected fraction of the primary selection differs between members beyond herald_bound.

    On the all-zero shots every herald bit reads 0, so a per-bit excitation
    test is empty there; the admission instead tests the member spread of
    the rejected fraction (the probability that any pinned qubit heralds 1)
    with n21_orbit_rca.herald_admission at unit readout contrast, so the
    kept shots of every member come from one initial ensemble.
    """
    counts = {
        0: {"qubit": -1, "members": {name: (totals[name] - kept, totals[name]) for name, (_z, kept) in reads.items()}}
    }
    shots = min(totals.values())
    admitted = rca.herald_admission(counts, {-1: 1.0}, rca.herald_bound(shots, alpha), alpha)
    return admitted | {"present": True, "evaluable": True, "shots": shots, "rule": "rejected-fraction spread"}


def evaluate(
    reads: dict[str, tuple[int, int]] | None, exposures_dt: dict[str, int], dt_us: float, alpha: float = TEST_ALPHA
) -> dict[str, Any]:
    """Fits and verdicts of herald-conditioned reads; an empty selection or absent herald reads not_evaluable."""
    if reads is None:
        reason = "the record carries no initialization herald"
        return {"tests": {name: {"status": "not_evaluable", "reason": reason} for name in TESTS[1:]}}
    empty = sorted(name for name, (_zeros, shots) in reads.items() if shots == 0)
    if empty:
        reason = f"members {empty} keep no shot the herald selects"
        return {"tests": {name: {"status": "not_evaluable", "reason": reason} for name in TESTS[1:]}}
    points = [
        (exposures_dt[name] * dt_us, name.rsplit("_", 1)[1], zeros, shots)
        for name, (zeros, shots) in sorted(reads.items(), key=lambda item: (exposures_dt[item[0]], item[0]))
    ]
    fitted = fit_counts(points, alpha)
    return {"points": [list(point) for point in points], **fitted, "tests": fitted["decisions"]}


def analyzer_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def report(run: Path) -> dict[str, Any]:
    """The sweep's report: admissibility, the spectator herald, the herald-conditioned fits and verdicts."""
    record = json.loads((run / "record.json").read_text())
    family = record["family_configuration"]
    names = [member["name"] for member in rca._group(run)["members"]]
    if not is_sweep(names):
        raise RuntimeError(f"{run} is not a ground Ramsey sweep record")
    schedules, control, unresolved = run_schedules(run)
    admitted = admissibility(schedules, names, control, int(family["window_delay_dt"]) + int(family["reset_dt"]))
    if unresolved:
        admitted["unresolved"] |= unresolved
        admitted["admissible"] = False
    calibrations = rca.execution_calibration(run)
    reads, conditioning = run_reads(run, control)
    output: dict[str, Any] = {
        "schema_version": SCHEMA,
        "analyzer_sha256": analyzer_sha256(),
        "alpha": {"family_alpha": FAMILY_ALPHA, "tests": list(TESTS), "per_test_alpha": TEST_ALPHA},
        "admissibility": admitted,
        "herald_conditioning": conditioning,
        # Descriptive: each herald bit's member spread over the control-zero shots.
        "control_zero_bit_herald": rca.herald_report(
            run, calibrations, lambda name: member_key(name) is not None, TEST_ALPHA, rca.HERALD_ROLES.index("control")
        ),
    }
    if not admitted["admissible"]:
        output["tests"] = {name: {"status": "not_admissible", "reason": "schedule"} for name in TESTS[1:]}
        return output
    if reads is None:
        output |= evaluate(None, {}, 0.0)
        return output
    totals = {name: pair[1] for name, pair in conditioning["kept_shots"]["all_zero"].items()}
    herald = selection_admission(reads["all_zero"], totals, TEST_ALPHA)
    output["spectator_herald"] = herald
    if not herald["admissible"]:
        output["tests"] = rca.herald_refusal(herald, TESTS[1:])
        return output
    exposures = {name: int(schedule["exposure_dt"]) for name, schedule in schedules.items()}
    dt_us = float(family["dt_seconds"]) * 1e6
    output |= evaluate(reads["all_zero"], exposures, dt_us)
    secondary = evaluate(reads["control_zero"], exposures, dt_us)
    output["secondary_control_zero"] = {"status": "descriptive", **secondary}
    return output


# Planted truths. The retained ground split reads immediate 0.989 and
# idle_ground 0.622 after 836 dt (3.344 us), an exponential T2* of 7.2 us or
# a Gaussian T of 4.9 us; the plants sit there at the design shot count.
WINDOW_DT = 836
DT_US = 0.004
DESIGN_MULTIPLES = (1, 2, 3, 4, 5, 6)
DESIGN_SHOTS = 12288
EXPONENTIAL = {"amplitude": 0.989, "t2_star_us": 7.2, "beta": 1.0, "detuning_mhz": 0.0, "phi0": 0.0, "offset": 0.0}
GAUSSIAN = EXPONENTIAL | {"t2_star_us": 4.9, "beta": 2.0}
DETUNED = EXPONENTIAL | {"detuning_mhz": 0.04}


def design_exposures_us(multiples: tuple[int, ...] = DESIGN_MULTIPLES) -> list[float]:
    return [0.0, *(multiple * WINDOW_DT * DT_US for multiple in multiples)]


def _plant(truth: dict[str, float]) -> dict[str, Any]:
    return fit_counts(expected_points(truth, design_exposures_us(), DESIGN_SHOTS))


def _check_plants() -> dict[str, str]:
    verdicts = {}
    for label, truth, shape, detuning in (
        ("exponential", EXPONENTIAL, "exponential", "unresolved"),
        ("gaussian", GAUSSIAN, "gaussian", "unresolved"),
        ("detuned", DETUNED, "exponential", "detuned"),
    ):
        fitted = _plant(truth)
        found = (fitted["decisions"]["decay_shape"]["status"], fitted["decisions"]["detuning"]["status"])
        estimates = fitted["fits"]["free"]["estimates"]
        if found != (shape, detuning):
            raise RuntimeError(f"the {label} plant reads {found}, not {(shape, detuning)}")
        for name in ("t2_star_us", "beta", "detuning_mhz"):
            if abs(estimates[name] - truth[name]) > 0.02 * max(1.0, abs(truth[name])):
                raise RuntimeError(f"the {label} plant recovers {name} {estimates[name]}, not {truth[name]}")
        verdicts[label] = "/".join(found)
    return verdicts


def _check_rz_sign() -> float:
    """The analyzer reads a planted rz(+theta) on qubit 2 of the built idle_ground circuits as delta > 0.

    Each built member (no herald) gets rz(2 pi delta t) on qubit 2 at its
    control delay, and ideal branch probabilities give its counts.
    """
    from qiskit import QuantumCircuit

    from qpe_diagnostics import ideal_compiled_probabilities, n21_spectator_ramsey, phase_marginal

    detuning = 0.03
    points = []
    for multiple in (0, *DESIGN_MULTIPLES):
        for quadrature in QUADRATURES:
            kind = "immediate" if multiple == 0 else "idle_ground"
            built = n21_spectator_ramsey(kind, quadrature, measure_dt=415, reset_dt=421, idle_multiple=multiple or None)
            probed = QuantumCircuit(*built.qregs, *built.cregs)
            for instruction in built.data:
                probed.append(instruction)
                if instruction.operation.name == "delay":
                    probed.rz(2 * math.pi * detuning * multiple * WINDOW_DT * DT_US, 2)
            law = phase_marginal(ideal_compiled_probabilities(probed))
            zeros = round(DESIGN_SHOTS * float(law[0] + law[1]) * 0.95 + DESIGN_SHOTS * 0.025)
            points.append((multiple * WINDOW_DT * DT_US, quadrature, zeros, DESIGN_SHOTS))
    found = fit_counts(points)["fits"]["exponential"]["estimates"]["detuning_mhz"]
    if abs(found - detuning) > 1e-3:
        raise RuntimeError(f"a planted rz(+2 pi {detuning} t) reads delta {found} MHz")
    return found


def _check_control_excited() -> dict[str, str]:
    """A control-excited ensemble moves the unconditioned fit and leaves the conditioned one at the truth.

    Every member gains 30 percent added shots that herald the control 1
    and read qubit 2 after a 0.3 MHz ZZ turn with no decay; conditioning on
    the control herald 0 recovers the exponential plant.
    """
    exposures = design_exposures_us()
    clean = expected_points(EXPONENTIAL, exposures, DESIGN_SHOTS)
    excited = {
        (time, quadrature): zeros
        for time, quadrature, zeros, _shots in expected_points(
            EXPONENTIAL | {"t2_star_us": 500.0, "detuning_mhz": 0.3}, exposures, 3686
        )
    }
    reads_conditioned: dict[str, tuple[int, int]] = {}
    reads_mixed: dict[str, tuple[int, int]] = {}
    exposure_dt: dict[str, int] = {}
    for time, quadrature, zeros, shots in clean:
        multiple = round(time / (WINDOW_DT * DT_US))
        name = f"m{multiple}_{quadrature}"
        exposure_dt[name] = multiple * WINDOW_DT
        phases = ["00"] * zeros + ["10"] * (shots - zeros)
        added = excited[(time, quadrature)]
        phases += ["00"] * added + ["10"] * (3686 - added)
        heralds = ["0000"] * shots + ["0001"] * 3686
        reads_conditioned[name] = conditioned_zeros(phases, heralds, (3,))
        reads_mixed[name] = (sum(value[0] == "0" for value in phases), len(phases))
    conditioned = evaluate(reads_conditioned, exposure_dt, DT_US)["tests"]
    mixed = evaluate(reads_mixed, exposure_dt, DT_US)["tests"]
    if (conditioned["decay_shape"]["status"], conditioned["detuning"]["status"]) != ("exponential", "unresolved"):
        raise RuntimeError(f"the conditioned control-excited ensemble reads {conditioned}")
    if mixed["detuning"]["status"] == "unresolved" and mixed["decay_shape"]["status"] == "exponential":
        raise RuntimeError("the unconditioned control-excited ensemble reads as the clean plant")
    return {
        "conditioned": f"{conditioned['decay_shape']['status']}/{conditioned['detuning']['status']}",
        "unconditioned": f"{mixed['decay_shape']['status']}/{mixed['detuning']['status']}",
    }


def _check_neighbor_excited() -> dict[str, Any]:
    """An excited-neighbor subpopulation biases the control-only fit and leaves the all-zero fit at the truth.

    Every member gains 15 percent added shots that herald work bit 1 (herald
    bit 1, a 143 neighbor) excited and the control 0, and read qubit 2 under
    the ZZ shift such a neighbor imposes, a 0.1 MHz detuning; the control-only
    selection keeps them, the all-zero selection drops them.
    """
    exposures = design_exposures_us()
    added = round(0.15 * DESIGN_SHOTS)
    shifted = {
        (time, quadrature): zeros
        for time, quadrature, zeros, _shots in expected_points(EXPONENTIAL | {"detuning_mhz": 0.1}, exposures, added)
    }
    selections: dict[str, dict[str, tuple[int, int]]] = {"all_zero": {}, "control_zero": {}}
    exposure_dt: dict[str, int] = {}
    for time, quadrature, zeros, shots in expected_points(EXPONENTIAL, exposures, DESIGN_SHOTS):
        multiple = round(time / (WINDOW_DT * DT_US))
        name = f"m{multiple}_{quadrature}"
        exposure_dt[name] = multiple * WINDOW_DT
        excited = shifted[(time, quadrature)]
        phases = ["00"] * zeros + ["10"] * (shots - zeros) + ["00"] * excited + ["10"] * (added - excited)
        heralds = ["0000"] * shots + ["0010"] * added
        selections["all_zero"][name] = conditioned_zeros(phases, heralds, (0, 1, 2, 3))
        selections["control_zero"][name] = conditioned_zeros(phases, heralds, (3,))
    found = {label: evaluate(reads, exposure_dt, DT_US) for label, reads in selections.items()}
    primary = found["all_zero"]["fits"]["free"]["estimates"]
    secondary = found["control_zero"]["fits"]["free"]["estimates"]
    if abs(primary["beta"] - 1.0) > 0.02 or abs(primary["t2_star_us"] - 7.2) > 0.15:
        raise RuntimeError(f"the all-zero selection misses the truth: {primary}")
    shift = abs(secondary["t2_star_us"] - 7.2) / found["control_zero"]["fits"]["free"]["standard_errors"]["t2_star_us"]
    beta_shift = abs(secondary["beta"] - 1.0) / found["control_zero"]["fits"]["free"]["standard_errors"]["beta"]
    if max(shift, beta_shift) < 3.0:
        raise RuntimeError(f"the control-only selection keeps the excited neighbor without bias: {secondary}")
    return {
        "all_zero": f"beta {primary['beta']:.3f} T2* {primary['t2_star_us']:.3f}",
        "control_zero": f"beta {secondary['beta']:.3f} T2* {secondary['t2_star_us']:.3f}",
    }


def _check_empty_selection() -> str:
    phases = ["00"] * 10
    heralds = ["0001"] * 10
    reads = {"m0_x": conditioned_zeros(phases, heralds, (3,)), "m1_x": (5, 10)}
    tests = evaluate(reads, {"m0_x": 0, "m1_x": WINDOW_DT}, DT_US)["tests"]
    if any(test["status"] != "not_evaluable" for test in tests.values()):
        raise RuntimeError(f"an empty herald selection reads {tests}")
    return "not_evaluable"


def _check_schedules() -> dict[str, bool]:
    """Admissibility accepts the built schedule and refuses a decoupling pulse, a short idle and a prepared control."""
    control, spectator = 142, 143

    def plays(multiple: int, extra: bool = False, prepared: bool = False) -> list[tuple[int, int, str, int]]:
        start = 1290
        end = start + 6 + multiple * WINDOW_DT
        rows = [(start, 6, "sx", spectator), (end, 6, "sx", spectator), (end + 7, 180, "measure", spectator)]
        if extra:
            rows.append((start + 400, 8, "x", spectator))
        if prepared or multiple == 0:
            rows.append((start, 6, "sx", control))
        return rows

    names = [f"n21_spectator_immediate_{q}" for q in QUADRATURES] + [
        f"n21_spectator_idle_ground_w{m}_{q}" for m in DESIGN_MULTIPLES for q in QUADRATURES
    ]

    def schedules(**fault: Any) -> dict[str, dict[str, Any]]:
        result = {}
        for name in names:
            key = member_key(name)
            if key is None:
                raise RuntimeError(f"{name} is not a sweep member")
            multiple = key[0]
            target = name == names[-1]
            delay = multiple * WINDOW_DT - (100 if target and fault.get("short") else 0)
            rows = plays(multiple, target and fault.get("extra", False), target and fault.get("prepared", False))
            if target and fault.get("short"):
                rows = [(row[0] - 100, *row[1:]) if row[0] > 1296 else row for row in rows]
            result[name] = member_schedule(rows, control, delay)
        return result

    verdicts = {
        label: admissibility(schedules(**fault), names, control, WINDOW_DT)["admissible"]
        for label, fault in (
            ("built", {}),
            ("decoupling", {"extra": True}),
            ("short", {"short": True}),
            ("prepared", {"prepared": True}),
        )
    }
    if verdicts != {"built": True, "decoupling": False, "short": False, "prepared": False}:
        raise RuntimeError(f"sweep admissibility reads {verdicts}")
    return verdicts


def _check_names() -> None:
    from diagnostic_experiments import n21_orbit_rca_group

    group = n21_orbit_rca_group(
        415, 502, True, reset_dt=421, ground_control_split=True, ramsey_windows=DESIGN_MULTIPLES
    )
    names = [member.name for member in group.members]
    keys = [member_key(name) for name in names]
    if None in keys or not is_sweep(names):
        raise RuntimeError(f"the planned sweep members {names} do not read as the sweep")
    if set(names) & set(rca.ALL_SPECTATOR_MEMBERS) != {f"{rca.SPECTATOR_PREFIX}immediate_{q}" for q in QUADRATURES}:
        raise RuntimeError("an idle_ground sweep member reads as a single-idle split member in n21_orbit_rca")
    single = [
        member.name for member in n21_orbit_rca_group(415, 502, True, reset_dt=421, ground_control_split=True).members
    ]
    if is_sweep(single):
        raise RuntimeError("the single-idle ground split reads as the sweep")


def self_check() -> dict[str, Any]:
    _check_names()
    result = {
        "plants": _check_plants(),
        "rz_sign_detuning_mhz": _check_rz_sign(),
        "control_excited": _check_control_excited(),
        "neighbor_excited": _check_neighbor_excited(),
        "empty_selection": _check_empty_selection(),
        "schedules": _check_schedules(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--check", action="store_true", help=f"regenerate RUN_DIR/{RETAINED} and require equal bytes")
    parser.add_argument(
        "--design",
        action="store_true",
        help="print the Fisher-information precision of the design grid at the exponential and Gaussian plants",
    )
    parser.add_argument("--shots", type=int, default=DESIGN_SHOTS)
    parser.add_argument("--expected-analyzer-sha256", metavar="HEX")
    arguments = parser.parse_args(argv)
    if (
        arguments.expected_analyzer_sha256 is not None
        and arguments.expected_analyzer_sha256.lower() != analyzer_sha256()
    ):
        parser.error(f"this analyzer's sha256 {analyzer_sha256()} differs from {arguments.expected_analyzer_sha256}")
    if arguments.self_check:
        self_check()
        return 0
    if arguments.design:
        exposures = design_exposures_us()
        print(
            serialize(
                {
                    label: design_precision(truth, exposures, arguments.shots)
                    for label, truth in (("exponential", EXPONENTIAL), ("gaussian", GAUSSIAN))
                }
            ),
            end="",
        )
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    produced = serialize(report(arguments.run))
    if arguments.check:
        retained = arguments.run / RETAINED
        if retained.read_text() != produced:
            raise SystemExit(f"{retained} differs from the report its archived raw files regenerate")
        print(f"{retained}: regenerated byte for byte")
        return 0
    if arguments.out:
        arguments.out.write_text(produced)
    else:
        print(produced, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
