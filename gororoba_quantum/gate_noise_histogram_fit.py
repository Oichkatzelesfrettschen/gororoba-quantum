"""Density-matrix forward model of a circuit under gate noise, and the bounded least-squares fits of its parameters to
outcome histograms.

An Experiment holds everything the model reads from the experiment: the instruction list of the circuit, its qubit
region and roles, the arms (pulse gate, injection scope, grid steps), the scope table, the injection step and the
selector-flip rule. A caller builds one from its own acquisition record, so a compatible acquisition reuses the model
and the fits without a change here. Observations are dicts with the keys arm, batch, kind, counts (outcome counts over
the logical index) and matrix (the readout matrix that maps the model law to the read law).

Parameters of a law (absent means 0): pa and pp, amplitude and phase damping after each pulse; cd, CZ two-qubit
depolarizing; ca and cp, CZ amplitude and phase damping on both qubits; delta, CZ conditional phase; x<q>, x-angle
offset of q's pulses; z<q>, z rotation after q's pulses; c<q>, z rotation of q after each CZ that touches it; flip,
the selector-flip probability applied to the law.

The independent arm laws and the independent starts of every search map over parallel.py, in input order; a call from
inside a worker runs serially there.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import least_squares, minimize_scalar

from elementary_error_laws import rotation
from parallel import ordered_map

Observation = dict[str, Any]
Operation = tuple[str, str | None, tuple[int, ...]]

# An expected probability below the floor enters the Pearson denominator as the floor.
CLIP = 1e-9
# Relative step of the finite-difference Jacobian of every least-squares fit.
DIFF_STEP = 1e-3
RETENTION_START = 0.45
RETENTION_BOUNDS = (0.05, 1.0)
PHASE_POINTS = 17
RETENTION_POINTS = 96
NEAR_LOWER = 0.01
NEAR_ZERO = 1e-4


@dataclass(frozen=True)
class Experiment:
    """The circuit and the arm definitions that the forward model reads.

    ops: instructions (gate, angle text, qubits) of the circuit; gate is CZ, Rz or the pulse gate that an arm rewrites.
    region: physical qubits in tensor-axis order. roles: role name to physical qubit. keys: role names in order of the
    bits of the logical outcome index (bit v of the index is keys[v]). arms: arm name to (pulse gate, injection scope
    or None, grid steps); a pulse of an arm whose pulse gate is Rx on a qubit of the scope turns by steps * step beyond
    the quarter turn. flip_bit and flip_state: the selector flips when that role bit reads flip_state.
    """

    ops: tuple[Operation, ...]
    region: tuple[int, ...]
    roles: dict[str, int]
    keys: tuple[str, ...]
    arms: dict[str, tuple[str, str | None, int]]
    scopes: dict[str, tuple[int, ...]]
    step: float
    selector: str
    flip_bit: str
    flip_state: int

    @property
    def nout(self) -> int:
        return 2 ** len(self.keys)


# Forward model --------------------------------------------------------------------------------------------------------


def kraus(amplitude: float, phase: float) -> list[np.ndarray]:
    """Amplitude damping followed by phase damping, as the Kraus operators that are not zero."""
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    return [p @ a for p in (p0, p1) for a in (a0, a1) if np.any(p @ a)]


def channel(rho: np.ndarray, ops: list[np.ndarray], axis: int, qubits: int) -> np.ndarray:
    """rho -> sum_k K rho K^dagger on one qubit axis of the (2,) * 2 * qubits density tensor."""
    out: np.ndarray | None = None
    for k in ops:
        t = np.moveaxis(np.tensordot(k, rho, axes=(1, axis)), 0, axis)
        t = np.moveaxis(np.tensordot(k.conj(), t, axes=(1, qubits + axis)), 0, qubits + axis)
        out = t if out is None else out + t
    if out is None:
        raise ValueError("a channel needs at least one Kraus operator")
    return out


COORDINATE = re.compile(r"^([xzc])(\d+)$")


def per_qubit(values: dict[str, float], prefix: str) -> dict[int, float]:
    """The angles of parameters named like x4 (x offset), z12 (z after pulse) or c12 (z after CZ)."""
    found: dict[int, float] = {}
    for name, value in values.items():
        match = COORDINATE.fullmatch(name)
        if match is not None and match.group(1) == prefix:
            found[int(match.group(2))] = value
    return found


def law(experiment: Experiment, arm: str, values: dict[str, float]) -> np.ndarray:
    """Law of an arm over the logical outcomes, for the parameters in the module docstring."""
    n = len(experiment.region)
    axis_of = {q: i for i, q in enumerate(experiment.region)}
    index = np.indices((2,) * n)
    pulse, scope, steps = experiment.arms[arm]
    injected = () if scope is None else experiment.scopes[scope]
    pa, pp, cd = values.get("pa", 0.0), values.get("pp", 0.0), values.get("cd", 0.0)
    ca, cp, delta = values.get("ca", 0.0), values.get("cp", 0.0), values.get("delta", 0.0)
    offsets, after_pulse, after_cz = per_qubit(values, "x"), per_qubit(values, "z"), per_qubit(values, "c")
    pulse_ops = kraus(pa, pp) if (pa or pp) else None
    cz_ops = kraus(ca, cp) if (ca or cp) else None
    rho = np.zeros((2,) * (2 * n), dtype=complex)
    rho.flat[0] = 1.0
    for gate, angle, qubits in experiment.ops:
        if gate == "CZ":
            a, b = axis_of[qubits[0]], axis_of[qubits[1]]
            d = np.where(index[a] * index[b] == 1, -np.exp(1j * delta), 1.0)
            rho = rho * d.reshape((2,) * n + (1,) * n) * d.conj().reshape((1,) * n + (2,) * n)
            for q in qubits:
                if after_cz.get(q):
                    rho = channel(rho, [rotation("z", after_cz[q])], axis_of[q], n)
            if cd:
                # two-qubit depolarizing: mix with the state whose two qubits are maximally mixed
                r = np.moveaxis(rho, (a, b, n + a, n + b), (0, 1, 2, 3))
                reduced = np.einsum("ijij...->...", r)
                mixed = np.einsum("ik,jl,...->ijkl...", np.eye(2), np.eye(2), reduced) / 4
                rho = np.moveaxis((1 - cd) * r + cd * mixed, (0, 1, 2, 3), (a, b, n + a, n + b))
            if cz_ops:
                rho = channel(channel(rho, cz_ops, a, n), cz_ops, b, n)
            continue
        q = qubits[0]
        a = axis_of[q]
        if gate == "Rz":
            rho = channel(rho, [rotation("z", float(angle or 0.0))], a, n)
            continue
        injection = steps * experiment.step if pulse == "Rx" and q in injected else 0.0
        u = rotation("x", math.pi / 2 + injection + offsets.get(q, 0.0))
        if after_pulse.get(q):
            u = rotation("z", after_pulse[q]) @ u
        rho = channel(rho, [u], a, n)
        if pulse_ops:
            rho = channel(rho, pulse_ops, a, n)
    prob = np.real(np.diagonal(rho.reshape(2**n, 2**n))).reshape((2,) * n)
    order = [axis_of[experiment.roles[k]] for k in reversed(experiment.keys)]
    return np.asarray(prob.transpose(order).reshape(experiment.nout))


def flip_matrix(experiment: Experiment, flip: float) -> np.ndarray:
    """Stochastic matrix over the logical outcomes: the selector flips with probability flip when the flip bit reads
    flip_state."""
    source, selector = experiment.keys.index(experiment.flip_bit), experiment.keys.index(experiment.selector)
    matrix = np.zeros((experiment.nout, experiment.nout))
    for s in range(experiment.nout):
        p = flip if (s >> source) & 1 == experiment.flip_state else 0.0
        matrix[s, s] += 1.0 - p
        matrix[s ^ (1 << selector), s] += p
    return matrix


def arm_law_item(item: tuple[Experiment, str, dict[str, float]]) -> np.ndarray:
    """The law of one arm; the unit of work that arm_laws maps over the pool."""
    experiment, arm, values = item
    return law(experiment, arm, values)


def arm_laws(experiment: Experiment, arms: list[str], values: dict[str, float]) -> dict[str, np.ndarray]:
    """The law of each listed arm at one parameter point. The arms are independent density-matrix simulations, so
    they map over parallel.py; a call from inside a pool worker (a fit's residual) runs them serially there."""
    laws = ordered_map(arm_law_item, [(experiment, arm, values) for arm in arms], min_items=2)
    return dict(zip(arms, laws, strict=True))


def arms_of(found: list[Observation]) -> list[str]:
    """The distinct arms of the observations, sorted."""
    return sorted({o["arm"] for o in found})


def predict(experiment: Experiment, found: list[Observation], values: dict[str, float]) -> list[np.ndarray]:
    """The law each observation reads at a parameter point: its arm's law, the selector flip, its readout matrix."""
    laws = arm_laws(experiment, arms_of(found), values)
    matrix = flip_matrix(experiment, values["flip"]) if values.get("flip") else None
    return [o["matrix"] @ (laws[o["arm"]] if matrix is None else matrix @ laws[o["arm"]]) for o in found]


def pearson(found: list[Observation], predicted: list[np.ndarray]) -> np.ndarray:
    """The Pearson residuals of every observation's counts against its predicted law, concatenated."""
    return np.concatenate(
        [
            (o["counts"] - o["counts"].sum() * p) / np.sqrt(o["counts"].sum() * np.clip(p, CLIP, None))
            for o, p in zip(found, predicted, strict=True)
        ]
    )


# Fits -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FitSpec:
    """One least-squares fit: free parameters with start, bounds and step scale; fixed parameters join the values."""

    name: str
    free: tuple[str, ...]
    start: tuple[float, ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]
    x_scale: tuple[float, ...]
    fixed: tuple[tuple[str, float], ...] = ()


def optimize(
    experiment: Experiment, spec: FitSpec, found: list[Observation], start: tuple[float, ...]
) -> tuple[Any, dict[str, float]]:
    """One bounded least-squares fit of the free parameters from start; the fixed ones join the values."""
    fixed = dict(spec.fixed)

    def full(x: np.ndarray) -> dict[str, float]:
        return {**fixed, **{k: float(v) for k, v in zip(spec.free, x, strict=True)}}

    def residual(x: np.ndarray) -> np.ndarray:
        return pearson(found, predict(experiment, found, full(x)))

    result = least_squares(
        residual,
        list(start),
        bounds=(list(spec.lower), list(spec.upper)),
        x_scale=list(spec.x_scale),
        diff_step=DIFF_STEP,
    )
    return result, full(result.x)


def fit_item(item: tuple[Experiment, FitSpec, list[Observation]]) -> tuple[str, dict[str, Any]]:
    """The fit of one specification from its stored start."""
    experiment, spec, found = item
    result, values = optimize(experiment, spec, found, spec.start)
    return spec.name, {
        "values": values,
        "histogram_chi2": float(2 * result.cost),
        "optimizer_status": int(result.status),
    }


def contract(exact: np.ndarray, retention: float) -> np.ndarray:
    """The exact law contracted toward uniform by one retention."""
    return retention * exact + (1 - retention) / len(exact)


def retained_laws(found: list[Observation], exact: dict[str, np.ndarray], values: dict[str, float]) -> list[np.ndarray]:
    """The law each observation reads when its batch's retention (values retention_<batch>) contracts the exact law."""
    return [o["matrix"] @ contract(exact[o["arm"]], values[f"retention_{o['batch']}"]) for o in found]


def fit_retention(experiment: Experiment, found: list[Observation]) -> dict[str, Any]:
    """The exact law contracted toward uniform by one retention per data batch (a free-retention contraction)."""
    batches = sorted({o["batch"] for o in found})
    exact = arm_laws(experiment, arms_of(found), {})

    def residual(x: np.ndarray) -> np.ndarray:
        values = {f"retention_{b}": float(v) for b, v in zip(batches, x, strict=True)}
        return pearson(found, retained_laws(found, exact, values))

    count = len(batches)
    result = least_squares(
        residual, [RETENTION_START] * count, bounds=([RETENTION_BOUNDS[0]] * count, [RETENTION_BOUNDS[1]] * count)
    )
    values = {f"retention_{b}": float(v) for b, v in zip(batches, result.x, strict=True)}
    return {"values": values, "histogram_chi2": float(2 * result.cost), "optimizer_status": int(result.status)}


# Deterministic multistart and profile search -------------------------------------------------------------------------

SearchItem = tuple[Experiment, FitSpec, list[Observation], tuple[float, ...]]
# A model's search: its record, the candidate points (label, chi-square, parameter values) and the chi-squares of
# its full-model fits.
SearchResult = tuple[dict[str, Any], list[tuple[str, float, dict[str, float]]], list[float]]


def clipped(spec: FitSpec, point: list[float] | tuple[float, ...]) -> tuple[float, ...]:
    return tuple(min(max(v, lo), hi) for v, lo, hi in zip(point, spec.lower, spec.upper, strict=True))


def search_item(item: SearchItem) -> tuple[float, list[float]]:
    """Chi-square and parameters of one fit from one start."""
    experiment, spec, found, start = item
    result, _ = optimize(experiment, spec, found, clipped(spec, start))
    return float(2 * result.cost), [float(v) for v in result.x]


def phase_search(experiment: Experiment, spec: FitSpec, found: list[Observation]) -> SearchResult:
    """The last free parameter, a phase, is fixed on a grid across its bounds and the others are fitted from a start
    near their lower bounds, the stored start and the bound midpoints; each local minimum of the profile is then
    refined with the phase free."""
    phase, lower, upper = spec.free[-1], spec.lower[-1], spec.upper[-1]
    grid = [float(v) for v in np.linspace(lower, upper, PHASE_POINTS)]
    items: list[SearchItem] = []
    for value in grid:
        reduced = FitSpec(
            spec.name,
            spec.free[:-1],
            spec.start[:-1],
            spec.lower[:-1],
            spec.upper[:-1],
            spec.x_scale[:-1],
            ((phase, value),),
        )
        near = tuple(lo + NEAR_LOWER * (hi - lo) for lo, hi in zip(reduced.lower, reduced.upper, strict=True))
        middle = tuple((lo + hi) / 2 for lo, hi in zip(reduced.lower, reduced.upper, strict=True))
        items += [(experiment, reduced, found, start) for start in (near, reduced.start, middle)]
    results = ordered_map(search_item, items, min_items=2)
    profile: list[float] = []
    nuisance: list[list[float]] = []
    for index in range(PHASE_POINTS):
        best = min(results[3 * index : 3 * index + 3], key=lambda r: r[0])
        profile.append(best[0])
        nuisance.append(best[1])
    basins = [
        i
        for i in range(PHASE_POINTS)
        if (i == 0 or profile[i] <= profile[i - 1]) and (i == PHASE_POINTS - 1 or profile[i] <= profile[i + 1])
    ]
    refined = ordered_map(
        search_item, [(experiment, spec, found, (*nuisance[i], grid[i])) for i in basins], min_items=2
    )
    record = {
        "method": f"{phase} fixed on {PHASE_POINTS} grid points across its bounds, the other parameters fitted from "
        "three starts (near the lower bounds, the stored start, the bound midpoints), then every local minimum of "
        "the profile refined with the phase free",
        "starts": len(items) + len(basins),
        "phase_grid": grid,
        "profile_histogram_chi2": profile,
        "refined_phases": [grid[i] for i in basins],
    }
    candidates = [
        (f"profile at {phase}={grid[i]:.4f}", profile[i], dict(zip(spec.free, (*nuisance[i], grid[i]), strict=True)))
        for i in range(PHASE_POINTS)
    ] + [
        (f"refinement from {phase}={grid[i]:.4f}", r[0], dict(zip(spec.free, r[1], strict=True)))
        for i, r in zip(basins, refined, strict=True)
    ]
    return record, candidates, [r[0] for r in refined]


def noise_search(
    experiment: Experiment, spec: FitSpec, found: list[Observation], values: dict[str, float]
) -> SearchResult:
    """The fit from the stored start, a start near zero, the bound midpoints and the fitted point."""
    zero = tuple(NEAR_ZERO for _ in spec.free)
    middle = tuple((lo + hi) / 2 for lo, hi in zip(spec.lower, spec.upper, strict=True))
    fitted = tuple(values[k] for k in spec.free)
    starts = (spec.start, zero, middle, fitted)
    labels = ("stored start", "start of 1e-4", "bound midpoints", "fitted point")
    results = ordered_map(search_item, [(experiment, spec, found, start) for start in starts], min_items=2)
    record = {
        "method": "the fit from the stored start, a start of 1e-4 in every parameter, the bound midpoints and the "
        "fitted point",
        "starts": len(starts),
        "start_labels": list(labels),
        "start_histogram_chi2": [r[0] for r in results],
    }
    candidates = [
        (f"search from the {label}", r[0], dict(zip(spec.free, r[1], strict=True)))
        for label, r in zip(labels, results, strict=True)
    ]
    return record, candidates, [r[0] for r in results]


def retention_profile_item(item: tuple[str, list[Observation], dict[str, np.ndarray]]) -> tuple[str, float, float]:
    """One batch's chi-square over its retention: a grid across the bounds, then a bounded scalar refinement."""
    batch, found, exact = item

    def chi2(retention: float) -> float:
        predicted = [o["matrix"] @ contract(exact[o["arm"]], retention) for o in found]
        return float(np.sum(pearson(found, predicted) ** 2))

    grid = np.linspace(RETENTION_BOUNDS[0], RETENTION_BOUNDS[1], RETENTION_POINTS)
    values = [chi2(float(r)) for r in grid]
    best = int(np.argmin(values))
    window = (float(grid[max(best - 1, 0)]), float(grid[min(best + 1, RETENTION_POINTS - 1)]))
    result = minimize_scalar(chi2, bounds=window, method="bounded", options={"xatol": 1e-10})
    return batch, min(float(result.fun), values[best]), float(result.x)


def retention_search(experiment: Experiment, found: list[Observation]) -> SearchResult:
    """The objective is a sum over batches, so each batch's retention is profiled on its own."""
    batches = sorted({o["batch"] for o in found})
    exact = arm_laws(experiment, arms_of(found), {})
    items = [(b, [o for o in found if o["batch"] == b], exact) for b in batches]
    results = ordered_map(retention_profile_item, items, min_items=2)
    record = {
        "method": f"one-dimensional bounded profile of each batch's retention: {RETENTION_POINTS} grid points across "
        "the bounds, then a bounded scalar refinement around the lowest",
        "starts": len(batches),
        "batch_histogram_chi2": {b: chi2 for b, chi2, _ in results},
    }
    total = float(sum(chi2 for _, chi2, _ in results))
    point = {f"retention_{b}": r for b, _, r in results}
    return record, [("batch profiles", total, point)], [total]
