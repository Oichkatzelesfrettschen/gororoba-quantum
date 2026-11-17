"""Exploratory refit of the retained Tuna-17 null rotation scan histograms under gate noise and a q12 phase.

The 30 data circuits of `pathion_null_rotation_scan_tuna_17` (10 data batches of 3 circuits, each batch between two
readout brackets) are read through the retained shots. Each circuit's 32 logical outcome counts are compared with a
density-matrix forward model of the retained b0 circuit (five region qubits, the arm's pulse rewrite, the gate-noise
terms below) pushed through the joint readout matrix that the mean of the two adjacent brackets defines. The
statistic is the Pearson chi-square of the 30 x 32 counts, with 30 x 31 degrees of freedom less the free parameters.

Models (every model is a fit of those counts; nothing else is read):

- exact_circuit: no free parameter; the exact pulses and CZ gates.
- exact_circuit_batch_retention: one retention per data batch contracts the exact law toward uniform.
- five_noise_terms: pulse amplitude and phase damping, CZ depolarizing, CZ amplitude damping and CZ phase damping.
- five_noise_terms_selector_flip: the five terms and a selector flip of probability `flip` when bit d0 reads 0.
- five_noise_terms_q12_z_after_pulse: the five terms and a z rotation of q12 after each of its pulses.
- cz_noise_flip_q12_z_after_pulse / cz_noise_flip_q12_z_after_cz: CZ damping and dephasing, the selector flip and
  a q12 z rotation after each pulse of q12, or after each CZ that touches q12.

Evidence class: exploratory post-hoc fit of retained shots; no provider job, no random draw, no preregistered
decision. A parameter that sits on a bound is reported as such (`at_bound`), and degrees of freedom count every
declared parameter. Every model carries its starts, bounds, step scales and difference step, and one rule for the
expected probability in the Pearson denominator (a floor of CLIP). `--check` replays the headline fits and requires
agreement within TOLERANCE, the reproducibility that the optimizer's own stopping tolerance supports across BLAS
builds, and that the stored search found no lower chi-square. `--profile` replays that search: a phase profile with
refinement for the two q12-phase models, four starts for each five-noise-term model and ten one-dimensional
retention profiles. The search draws no random number.

Usage: `--write DIR` writes DIR/RECORD with the search; `--check DIR` replays the headline fits against DIR/RECORD;
`--profile DIR` replays the search; `--self-test` runs the simulator and optimizer against exact laws and planted
parameters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402
import qi_pathion_null_rotation_scan_noise as ns  # noqa: E402

from parallel import ordered_map  # noqa: E402

SCHEMA = "qi-pathion-null-rotation-scan-phase-refit-v2"
RECORD = "pathion_null_rotation_scan_tuna_17_phase_refit.json"
RUNS = "results/quantum_inspire/runs"
RUN_PREFIX = "2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-"
QUBITS = 5
TOLERANCE = 1e-5
CLIP = 1e-9
FLIP_BIT = "d0"
FLIP_STATE = 0
Z_QUBIT = 12
BOUND_FRACTION = 1e-4

Observation = dict[str, Any]


# Loading ------------------------------------------------------------------------------------------------------------


def verify_raw_files(directory: Path, listed: list[str]) -> None:
    """The raw directory of a run holds exactly the files its retained manifest lists, one `FILE.json` per circuit."""
    expected = sorted(f"{name}.json" for name in listed)
    raw = directory / "raw"
    actual = sorted(p.name for p in raw.iterdir()) if raw.is_dir() else []
    if actual != expected:
        raise ValueError(f"{directory.name}/raw holds {actual}, the manifest lists {expected}")


def run_directories() -> list[Path]:
    """The run directories the series plan names, each with the raw files its retained manifest lists."""
    runs: list[Path] = []
    for row in rs.batch_rows(rs.TUNA_SERIES):
        directory = ROOT / RUNS / f"{RUN_PREFIX}{row['batch'][-2:]}"
        manifest = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        listed = [circuit["file"] for circuit in manifest["circuits"]]
        planned = [circuit["file"] for circuit in row["circuits"]]
        if sorted(listed) != sorted(planned):
            raise ValueError(f"{directory.name} lists {sorted(listed)}, the series plan holds {sorted(planned)}")
        verify_raw_files(directory, listed)
        runs.append(directory)
    return runs


def observations() -> tuple[list[Observation], list[Path]]:
    """The 30 scan circuits with counts over the logical outcome index and the readout matrix of their brackets."""
    cc, pca, pcs = rs.cc, rs.pca, rs.pcs
    runs = run_directories()
    data = pca.read_series(runs, pcs.CASES_ROOT, rs.series_of, "data", rs.BATCH_FIELDS, pcs.load_run)
    shots, manifest = data["shots"], data["shared"]
    roles = {k: int(v) for k, v in manifest["templates"]["b0"]["roles"].items()}
    register = [int(q) for q in manifest["register"]]
    plan = {row["batch"]: row for row in rs.batch_rows(rs.TUNA_SERIES)}
    names = sorted(plan)
    brackets: dict[str, dict[int, tuple[float, float]]] = {}
    for b in names:
        if plan[b]["kind"] != "readout":
            continue
        assignment = cc.batch_assignment(shots, b, register)
        if assignment is None:
            raise ValueError(f"readout batch {b} of the retained series lacks its bracket pair")
        brackets[b] = assignment
    found: list[Observation] = []
    for position, batch in enumerate(names):
        row = plan[batch]
        if row["kind"] == "readout":
            continue
        before, after = brackets[names[position - 1]], brackets[names[position + 1]]
        mean = {q: ((before[q][0] + after[q][0]) / 2, (before[q][1] + after[q][1]) / 2) for q in register}
        for circuit in row["circuits"]:
            found.append(
                {
                    "batch": batch,
                    "kind": row["kind"],
                    "arm": rs.arm_of(circuit["file"]),
                    "counts": cc.coin_counts(shots[f"{batch}/{circuit['file']}"], roles),
                    "matrix": cc.readout_matrix(mean, roles),
                }
            )
    return found, runs


def data_digest(found: list[Observation]) -> str:
    payload = [
        {
            "batch": o["batch"],
            "arm": o["arm"],
            "counts": [int(c) for c in o["counts"]],
            "matrix": [[float(x) for x in row] for row in o["matrix"]],
        }
        for o in found
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# Density-matrix forward model ---------------------------------------------------------------------------------------


def kraus(amplitude: float, phase: float) -> list[np.ndarray]:
    """Amplitude damping followed by phase damping, as the Kraus operators that are not zero."""
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    return [p @ a for p in (p0, p1) for a in (a0, a1) if np.any(p @ a)]


def channel(rho: np.ndarray, ops: list[np.ndarray], axis: int) -> np.ndarray:
    """rho -> sum_k K rho K^dagger on one qubit axis of the (2,) * 10 density tensor."""
    out: np.ndarray | None = None
    for k in ops:
        t = np.moveaxis(np.tensordot(k, rho, axes=(1, axis)), 0, axis)
        t = np.moveaxis(np.tensordot(k.conj(), t, axes=(1, QUBITS + axis)), 0, QUBITS + axis)
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


def law(arm: str, values: dict[str, float]) -> np.ndarray:
    """Law of an arm over the 32 logical outcomes. Parameters (absent means 0): pa and pp, amplitude and phase
    damping after each pulse; cd, CZ two-qubit depolarizing; ca and cp, CZ amplitude and phase damping on both
    qubits; delta, CZ conditional phase; x<q>, x-angle offset of q's pulses; z<q>, z rotation after q's pulses;
    c<q>, z rotation of q after each CZ that touches it."""
    ref = rs.retained()
    region = ref["region"]
    axis_of = {q: i for i, q in enumerate(region)}
    index = np.indices((2,) * QUBITS)
    pulse, scope, steps = rs.ARMS[arm]
    injected = () if scope is None else rs.SCOPES[scope]
    pa, pp, cd = values.get("pa", 0.0), values.get("pp", 0.0), values.get("cd", 0.0)
    ca, cp, delta = values.get("ca", 0.0), values.get("cp", 0.0), values.get("delta", 0.0)
    offsets, after_pulse, after_cz = per_qubit(values, "x"), per_qubit(values, "z"), per_qubit(values, "c")
    pulse_ops = kraus(pa, pp) if (pa or pp) else None
    cz_ops = kraus(ca, cp) if (ca or cp) else None
    rho = np.zeros((2,) * (2 * QUBITS), dtype=complex)
    rho.flat[0] = 1.0
    for gate, angle, qubits in ref["ops"]:
        if gate == "CZ":
            a, b = axis_of[qubits[0]], axis_of[qubits[1]]
            d = np.where(index[a] * index[b] == 1, -np.exp(1j * delta), 1.0)
            rho = rho * d.reshape((2,) * QUBITS + (1,) * QUBITS) * d.conj().reshape((1,) * QUBITS + (2,) * QUBITS)
            for q in qubits:
                if after_cz.get(q):
                    rho = channel(rho, [rs.rotation("z", after_cz[q])], axis_of[q])
            if cd:
                # two-qubit depolarizing: mix with the state whose two qubits are maximally mixed
                r = np.moveaxis(rho, (a, b, QUBITS + a, QUBITS + b), (0, 1, 2, 3))
                reduced = np.einsum("ijij...->...", r)
                mixed = np.einsum("ik,jl,...->ijkl...", np.eye(2), np.eye(2), reduced) / 4
                rho = np.moveaxis((1 - cd) * r + cd * mixed, (0, 1, 2, 3), (a, b, QUBITS + a, QUBITS + b))
            if cz_ops:
                rho = channel(channel(rho, cz_ops, a), cz_ops, b)
            continue
        q = qubits[0]
        a = axis_of[q]
        if gate == "Rz":
            rho = channel(rho, [rs.rotation("z", float(angle or 0.0))], a)
            continue
        injection = steps * rs.STEP if pulse == "Rx" and q in injected else 0.0
        u = rs.rotation("x", math.pi / 2 + injection + offsets.get(q, 0.0))
        if after_pulse.get(q):
            u = rs.rotation("z", after_pulse[q]) @ u
        rho = channel(rho, [u], a)
        if pulse_ops:
            rho = channel(rho, pulse_ops, a)
    prob = np.real(np.einsum("abcdeabcde->abcde", rho))
    return prob.transpose([axis_of[ref["roles"][k]] for k in reversed(rs.KEYS)]).reshape(rs.NOUT)


# Fits ---------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FitSpec:
    """One least-squares fit: free parameters with start, bounds and step scale, as the exploratory run set them."""

    name: str
    free: tuple[str, ...]
    start: tuple[float, ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]
    x_scale: tuple[float, ...]
    fixed: tuple[tuple[str, float], ...] = ()


DIFF_STEP = 1e-3

NOISE_BOUNDS = {"pa": (0.0, 0.3), "pp": (0.0, 0.3), "cd": (0.0, 0.5), "ca": (0.0, 0.3), "cp": (0.0, 0.3)}
NOISE_START = {"pa": 0.003, "pp": 0.003, "cd": 0.02, "ca": 0.005, "cp": 0.005}
EXTRA_BOUNDS = {"flip": (0.0, 0.2), f"z{Z_QUBIT}": (-0.3, 0.3)}
EXTRA_START = {"flip": 0.02, f"z{Z_QUBIT}": 0.0}


def noise_spec(name: str, extra: tuple[str, ...]) -> FitSpec:
    """The noise-family fit: start values and step scales of the first exploratory sweep (scale = upper bound / 10)."""
    free = (*NOISE_BOUNDS, *extra)
    bounds = {**NOISE_BOUNDS, **EXTRA_BOUNDS}
    start = {**NOISE_START, **EXTRA_START}
    return FitSpec(
        name,
        free,
        tuple(start[k] for k in free),
        tuple(bounds[k][0] for k in free),
        tuple(bounds[k][1] for k in free),
        tuple(max(abs(bounds[k][1]), 1e-3) / 10 for k in free),
    )


def phase_spec(name: str, phase: str) -> FitSpec:
    """The CZ-damping fit with the selector flip and one q12 phase, as the exploratory phase sweep set it."""
    return FitSpec(
        name,
        ("ca", "cp", "flip", phase),
        (0.02, 0.03, 0.017, 0.0),
        (0.0, 0.0, 0.0, -0.4),
        (0.3, 0.3, 0.2, 0.4),
        (0.01, 0.01, 0.01, 0.03),
    )


SPECS = (
    noise_spec("five_noise_terms", ()),
    noise_spec("five_noise_terms_selector_flip", ("flip",)),
    noise_spec("five_noise_terms_q12_z_after_pulse", (f"z{Z_QUBIT}",)),
    phase_spec("cz_noise_flip_q12_z_after_pulse", f"z{Z_QUBIT}"),
    phase_spec("cz_noise_flip_q12_z_after_cz", f"c{Z_QUBIT}"),
)
EXACT = "exact_circuit"
RETENTION = "exact_circuit_batch_retention"
MODEL_NAMES = (EXACT, RETENTION, *(spec.name for spec in SPECS))


def flip_matrix(flip: float) -> np.ndarray:
    return rs.oc.selector_flip(rs.KEYS.index(FLIP_BIT), FLIP_STATE, flip)


def predict(found: list[Observation], values: dict[str, float]) -> list[np.ndarray]:
    laws: dict[str, np.ndarray] = {}
    matrix = flip_matrix(values["flip"]) if values.get("flip") else None
    out = []
    for o in found:
        if o["arm"] not in laws:
            laws[o["arm"]] = law(o["arm"], values)
        p = laws[o["arm"]] if matrix is None else matrix @ laws[o["arm"]]
        out.append(o["matrix"] @ p)
    return out


def pearson(found: list[Observation], predicted: list[np.ndarray]) -> np.ndarray:
    return np.concatenate(
        [
            (o["counts"] - o["counts"].sum() * p) / np.sqrt(o["counts"].sum() * np.clip(p, CLIP, None))
            for o, p in zip(found, predicted, strict=True)
        ]
    )


def contrast_chi2(found: list[Observation], predicted: list[np.ndarray]) -> tuple[float, dict[str, float]]:
    """Chi-square of the 30 selector contrasts against the model's, in total and by scan kind."""
    by_kind: dict[str, float] = {}
    for o, p in zip(found, predicted, strict=True):
        stat = rs.count_statistics(o["counts"])
        model = float(rs.selector_contrast(p[None, :])[0])
        by_kind[o["kind"]] = by_kind.get(o["kind"], 0.0) + ((stat["contrast"] - model) / stat["se"]) ** 2
    return float(sum(by_kind.values())), by_kind


def summary(
    found: list[Observation], predicted: list[np.ndarray], n_free: int, histogram: float, values: dict[str, float]
) -> dict[str, Any]:
    total, by_kind = contrast_chi2(found, predicted)
    return {
        "n_free": n_free,
        "dof": len(found) * (rs.NOUT - 1) - n_free,
        "histogram_chi2": histogram,
        "min_expected_probability": min(float(p.min()) for p in predicted),
        "contrast_chi2": total,
        "contrast_chi2_by_kind": dict(sorted(by_kind.items())),
        "values": {k: float(v) for k, v in values.items()},
    }


def optimize(spec: FitSpec, found: list[Observation], start: tuple[float, ...]) -> tuple[Any, dict[str, float]]:
    """One bounded least-squares fit of the free parameters from `start`; the fixed ones join the values."""
    fixed = dict(spec.fixed)

    def full(x: np.ndarray) -> dict[str, float]:
        return {**fixed, **{k: float(v) for k, v in zip(spec.free, x, strict=True)}}

    def residual(x: np.ndarray) -> np.ndarray:
        return pearson(found, predict(found, full(x)))

    result = least_squares(
        residual,
        list(start),
        bounds=(list(spec.lower), list(spec.upper)),
        x_scale=list(spec.x_scale),
        diff_step=DIFF_STEP,
    )
    return result, full(result.x)


def fit_item(item: tuple[FitSpec, list[Observation]]) -> tuple[str, dict[str, Any]]:
    spec, found = item
    result, values = optimize(spec, found, spec.start)
    return spec.name, {
        "values": values,
        "histogram_chi2": float(2 * result.cost),
        "optimizer_status": int(result.status),
    }


def exact_item(found: list[Observation]) -> tuple[str, dict[str, Any]]:
    histogram = float(np.sum(pearson(found, predict(found, {})) ** 2))
    return EXACT, {"values": {}, "histogram_chi2": histogram, "optimizer_status": None}


RETENTION_START = 0.45
RETENTION_BOUNDS = (0.05, 1.0)


def contract(exact: np.ndarray, retention: float) -> np.ndarray:
    """The exact law contracted toward uniform by one retention."""
    return retention * exact + (1 - retention) / rs.NOUT


def retention_item(found: list[Observation]) -> tuple[str, dict[str, Any]]:
    """The exact law contracted toward uniform by one retention per data batch (a free-retention contraction)."""
    batches = sorted({o["batch"] for o in found})
    exact = {arm: law(arm, {}) for arm in sorted({o["arm"] for o in found})}

    def predicted(x: np.ndarray) -> list[np.ndarray]:
        retention = dict(zip(batches, x, strict=True))
        return [o["matrix"] @ contract(exact[o["arm"]], retention[o["batch"]]) for o in found]

    def residual(x: np.ndarray) -> np.ndarray:
        return pearson(found, predicted(x))

    count = len(batches)
    result = least_squares(
        residual, [RETENTION_START] * count, bounds=([RETENTION_BOUNDS[0]] * count, [RETENTION_BOUNDS[1]] * count)
    )
    values = {f"retention_{b}": float(v) for b, v in zip(batches, result.x, strict=True)}
    record = {"values": values, "histogram_chi2": float(2 * result.cost), "optimizer_status": int(result.status)}
    return RETENTION, record


def config(name: str, found: list[Observation]) -> dict[str, Any]:
    """The free parameters of a model with their stored starts, step scales, difference step and bounds."""
    if name == EXACT:
        return {"free": [], "start": {}, "x_scale": {}, "diff_step": None, "bounds": {}}
    if name == RETENTION:
        free = [f"retention_{b}" for b in sorted({o["batch"] for o in found})]
        return {
            "free": free,
            "start": dict.fromkeys(free, RETENTION_START),
            "x_scale": dict.fromkeys(free, 1.0),
            "diff_step": None,
            "bounds": {k: list(RETENTION_BOUNDS) for k in free},
        }
    spec = next(s for s in SPECS if s.name == name)
    return {
        "free": list(spec.free),
        "start": dict(zip(spec.free, spec.start, strict=True)),
        "x_scale": dict(zip(spec.free, spec.x_scale, strict=True)),
        "diff_step": DIFF_STEP,
        "bounds": {k: [lo, hi] for k, lo, hi in zip(spec.free, spec.lower, spec.upper, strict=True)},
    }


def evaluate(found: list[Observation], name: str, values: dict[str, float]) -> dict[str, Any]:
    """The statistics of a model at one parameter point: chi-squares, degrees of freedom, smallest expected
    probability and the parameters that sit on a bound."""
    if name == RETENTION:
        exact = {arm: law(arm, {}) for arm in sorted({o["arm"] for o in found})}
        predicted = [o["matrix"] @ contract(exact[o["arm"]], values[f"retention_{o['batch']}"]) for o in found]
    else:
        predicted = predict(found, values)
    histogram = float(np.sum(pearson(found, predicted) ** 2))
    bounds = config(name, found)["bounds"]
    record = summary(found, predicted, len(bounds), histogram, values)
    record["at_bound"] = [
        k
        for k, (lo, hi) in bounds.items()
        if values[k] <= lo + BOUND_FRACTION * (hi - lo) or values[k] >= hi - BOUND_FRACTION * (hi - lo)
    ]
    return record


def fit_all(found: list[Observation]) -> dict[str, dict[str, Any]]:
    """Every model's fit from its stored start; the independent fits map over the process pool, in declaration order."""
    results = dict(ordered_map(fit_item, [(spec, found) for spec in SPECS], min_items=2))
    exact_name, exact = exact_item(found)
    retention_name, retention = retention_item(found)
    ordered = {exact_name: exact, retention_name: retention, **results}
    if tuple(ordered) != MODEL_NAMES:
        raise ValueError(f"fitted models {tuple(ordered)} differ from the declared {MODEL_NAMES}")
    return ordered


# Deterministic multistart and profile search ------------------------------------------------------------------------

PHASE_POINTS = 17
RETENTION_POINTS = 96
NEAR_LOWER = 0.01
NEAR_ZERO = 1e-4
SearchItem = tuple[FitSpec, list[Observation], tuple[float, ...]]
# A model's search: its record, the candidate points (label, chi-square, parameter values) and the chi-squares of
# its full-model fits.
SearchResult = tuple[dict[str, Any], list[tuple[str, float, dict[str, float]]], list[float]]


def clipped(spec: FitSpec, point: list[float] | tuple[float, ...]) -> tuple[float, ...]:
    return tuple(min(max(v, lo), hi) for v, lo, hi in zip(point, spec.lower, spec.upper, strict=True))


def search_item(item: SearchItem) -> tuple[float, list[float]]:
    """Chi-square and parameters of one fit from one start."""
    spec, found, start = item
    result, _ = optimize(spec, found, clipped(spec, start))
    return float(2 * result.cost), [float(v) for v in result.x]


def phase_search(spec: FitSpec, found: list[Observation]) -> SearchResult:
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
        items += [(reduced, found, start) for start in (near, reduced.start, middle)]
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
    refined = ordered_map(search_item, [(spec, found, (*nuisance[i], grid[i])) for i in basins], min_items=2)
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


def noise_search(spec: FitSpec, found: list[Observation], values: dict[str, float]) -> SearchResult:
    """The fit from the stored start, a start near zero, the bound midpoints and the fitted point."""
    zero = tuple(NEAR_ZERO for _ in spec.free)
    middle = tuple((lo + hi) / 2 for lo, hi in zip(spec.lower, spec.upper, strict=True))
    fitted = tuple(values[k] for k in spec.free)
    starts = (spec.start, zero, middle, fitted)
    labels = ("stored start", "start of 1e-4", "bound midpoints", "fitted point")
    results = ordered_map(search_item, [(spec, found, start) for start in starts], min_items=2)
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


def retention_search(found: list[Observation]) -> SearchResult:
    """The objective is a sum over batches, so each batch's retention is profiled on its own."""
    batches = sorted({o["batch"] for o in found})
    exact = {arm: law(arm, {}) for arm in sorted({o["arm"] for o in found})}
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


def search_all(found: list[Observation], stored: dict[str, dict[str, Any]]) -> dict[str, SearchResult]:
    """The search of every model; `stored` holds the fits from the stored starts."""
    searches: dict[str, SearchResult] = {
        EXACT: ({"method": "no free parameter", "starts": 0}, [], []),
        RETENTION: retention_search(found),
    }
    for spec in SPECS:
        if spec.name.startswith("cz_noise"):
            searches[spec.name] = phase_search(spec, found)
        else:
            searches[spec.name] = noise_search(spec, found, stored[spec.name]["values"])
    return {name: searches[name] for name in MODEL_NAMES}


def headline_models(
    found: list[Observation], stored: dict[str, dict[str, Any]], searches: dict[str, SearchResult]
) -> dict[str, dict[str, Any]]:
    """Each model at the lowest chi-square of its stored-start fit and its search, with the start that produced it."""
    models: dict[str, dict[str, Any]] = {}
    for name in MODEL_NAMES:
        record, candidates, fits = searches[name]
        start = stored[name]
        label, _, values = min(
            [("stored start", start["histogram_chi2"], start["values"]), *candidates], key=lambda c: c[1]
        )
        headline = evaluate(found, name, values)
        converged = [start["histogram_chi2"], *fits] if name != EXACT else [start["histogram_chi2"]]
        block = {
            **record,
            "best_histogram_chi2": headline["histogram_chi2"],
            "best_minus_headline": 0.0,
            "spread_histogram_chi2": max(converged) - min(converged),
        }
        models[name] = {
            **config(name, found),
            **headline,
            "headline_start": label,
            "stored_start_histogram_chi2": start["histogram_chi2"],
            "stored_start_optimizer_status": start["optimizer_status"],
            "search": block,
        }
    return models


def replayed_models(
    found: list[Observation], stored: dict[str, dict[str, Any]], retained: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Each retained headline point evaluated again, beside the replayed fit from the stored start."""
    return {
        name: {
            **config(name, found),
            **evaluate(found, name, retained[name]["values"]),
            "headline_start": retained[name]["headline_start"],
            "stored_start_histogram_chi2": stored[name]["histogram_chi2"],
            "stored_start_optimizer_status": stored[name]["optimizer_status"],
        }
        for name in MODEL_NAMES
    }


def verify_search(models: dict[str, dict[str, Any]]) -> None:
    """No start reaches a chi-square below the headline by more than the tolerance, and the headline stands at or
    below the fit from the stored start."""
    problems = []
    for name, model in models.items():
        headline = model["histogram_chi2"]
        slack = TOLERANCE * max(1.0, abs(headline))
        if model["search"]["best_histogram_chi2"] < headline - slack:
            problems.append(f"{name}: {model['search']['best_histogram_chi2']!r} below the headline {headline!r}")
        if headline > model["stored_start_histogram_chi2"] + slack:
            problems.append(f"{name}: headline {headline!r} above its stored-start fit")
    if problems:
        raise ValueError(f"the search found a lower minimum or the headline is not the lowest: {problems}")


# A model and the smaller model it contains: the smaller one's parameters absent from the larger stand at zero.
NESTING = (
    (RETENTION, EXACT),
    ("five_noise_terms", EXACT),
    ("five_noise_terms_selector_flip", "five_noise_terms"),
    ("five_noise_terms_q12_z_after_pulse", "five_noise_terms"),
    ("five_noise_terms_q12_z_after_pulse", "cz_noise_flip_q12_z_after_pulse"),
)
NESTING_ZERO = 1e-6


def verify_nesting(models: dict[str, dict[str, Any]]) -> None:
    """A larger model fits at least as well as the smaller model it contains, within the tolerance."""
    problems = []
    for larger, smaller in NESTING:
        big, small = models[larger], models[smaller]
        for key in small["free"]:
            if key in big["free"]:
                lower, upper = big["bounds"][key]
                if not lower <= small["values"][key] <= upper:
                    problems.append(f"{smaller} holds {key}={small['values'][key]!r} outside the bounds of {larger}")
            elif abs(small["values"][key]) > NESTING_ZERO:
                problems.append(f"{smaller} holds {key}={small['values'][key]!r}, so {larger} does not contain it")
        slack = TOLERANCE * max(1.0, abs(small["histogram_chi2"]))
        if big["histogram_chi2"] > small["histogram_chi2"] + slack:
            problems.append(
                f"{larger} reads {big['histogram_chi2']!r}, above the {smaller} model it contains "
                f"({small['histogram_chi2']!r})"
            )
    if problems:
        raise ValueError(f"the models break the nesting order: {problems}")


# Record -------------------------------------------------------------------------------------------------------------


def build(search: bool = True, retained: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """The record. With `search`, every headline is the lowest point of the stored-start fit and the search; without
    it, the headline points of `retained` are evaluated again beside the replayed stored-start fits."""
    found, runs = observations()
    kinds = sorted({o["kind"] for o in found})
    if len(found) != 30 or kinds != ["all10", "all20", "bridge", "q4-10", "q8-10"]:
        raise ValueError(f"expected 30 scan circuits of five kinds, read {len(found)} of {kinds}")
    stored = fit_all(found)
    if search:
        models = headline_models(found, stored, search_all(found, stored))
        verify_nesting(models)
    elif retained is None:
        raise ValueError("a replay without the search needs the retained models")
    else:
        models = replayed_models(found, stored, retained)
    return {
        "schema": SCHEMA,
        "evidence_class": "exploratory post-hoc fit of retained shots; no provider job, no random draw",
        "series": rs.TUNA_SERIES,
        "runs": [run.name for run in runs],
        "data_sha256": data_digest(found),
        "observations": len(found),
        "outcomes_per_observation": rs.NOUT,
        "statistic": "Pearson chi-square of the 32 logical outcome counts of each circuit against the model law read "
        "through the mean of the two adjacent readout brackets; contrast_chi2 is the 30-circuit selector-contrast "
        "chi-square",
        "expected_probability_floor": CLIP,
        "floor_rule": "an expected probability below the floor enters the Pearson denominator as the floor, in every "
        "model; min_expected_probability is the smallest expected probability of a model at its headline point",
        "tolerance": TOLERANCE,
        "models": models,
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n"


def write(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / RECORD
    target.write_text(render(build()), encoding="utf-8")
    return target


def differences(retained: Any, fresh: Any, path: str = "") -> list[str]:
    """Every place where `fresh` leaves `retained`: other types, keys, text or integers, or floats beyond TOLERANCE."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        unpaired = sorted(set(retained) ^ set(fresh))
        if unpaired:
            return [f"{path or '.'}: keys {unpaired} on one side only"]
        found: list[str] = []
        for key in sorted(retained):
            found += differences(retained[key], fresh[key], f"{path}.{key}")
        return found
    if isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            return [f"{path or '.'}: length {len(retained)} -> {len(fresh)}"]
        found = []
        for index, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            found += differences(left, right, f"{path}[{index}]")
        return found
    if isinstance(retained, float) and isinstance(fresh, float):
        close = abs(retained - fresh) <= TOLERANCE * max(1.0, abs(retained))
        return [] if close else [f"{path}: {retained!r} -> {fresh!r}"]
    same = type(retained) is type(fresh) and retained == fresh
    return [] if same else [f"{path or '.'}: {retained!r} -> {fresh!r}"]


def without_search(record: dict[str, Any]) -> dict[str, Any]:
    """The record with the search section of every model removed."""
    stripped = json.loads(json.dumps(record))
    for model in stripped["models"].values():
        model.pop("search", None)
    return stripped


def check(directory: Path, fresh: dict[str, Any] | None = None) -> None:
    """The headline points of the retained record evaluate again to the stored statistics, the fit from each stored
    start replays, no stored search found a lower minimum and the nesting order of the models holds.

    A difference raises ValueError listing the first of them. The search itself replays under `profile`."""
    retained = json.loads((directory / RECORD).read_text(encoding="utf-8"))
    if any("search" not in model for model in retained["models"].values()):
        raise ValueError(f"{directory / RECORD} stores no search section for a model")
    replay = build(search=False, retained=retained["models"]) if fresh is None else fresh
    found = differences(without_search(retained), replay)
    if found:
        raise ValueError(f"{directory / RECORD} differs from the replay in {len(found)} places: {found[:10]}")
    verify_search(retained["models"])
    verify_nesting(retained["models"])


def profile(directory: Path, fresh: dict[str, Any] | None = None) -> None:
    """Replay the whole search: the record equals it, no start beats a headline and the nesting order holds."""
    retained = json.loads((directory / RECORD).read_text(encoding="utf-8"))
    replay = build() if fresh is None else fresh
    problems = differences(retained, replay)
    if problems:
        raise ValueError(
            f"{directory / RECORD} differs from its search replay in {len(problems)} places: {problems[:10]}"
        )
    verify_search(replay["models"])
    verify_nesting(replay["models"])


# Self-test ----------------------------------------------------------------------------------------------------------

PLANTED = {"ca": 0.015, "cp": 0.035, f"z{Z_QUBIT}": -0.1}
PLANTED_ARMS = (rs.CENTER, "b0-rx-q4-p10", "b0-rx-q8-m10", "b0-rx-all-p20")
PLANTED_SHOTS = 1_000_000
PLANTED_RETENTION = 0.6


def planted_observations(values: dict[str, float]) -> list[Observation]:
    """Expected counts of the planted model through a perfect readout, one circuit per arm."""
    identity = np.eye(rs.NOUT)
    return [
        {
            "batch": f"planted-{n}",
            "kind": "planted",
            "arm": arm,
            "counts": PLANTED_SHOTS * law(arm, values),
            "matrix": identity,
        }
        for n, arm in enumerate(PLANTED_ARMS)
    ]


def self_test() -> str:
    """The simulator against the exact and noisy laws of the repository, then a planted parameter recovered."""
    for arm in (rs.RETAINED, rs.CENTER, "b0-rx-all-p20"):
        gap = float(np.abs(law(arm, {}) - rs.forward_law(arm)).max())
        if gap > 1e-10:
            raise AssertionError(f"the simulator differs from forward_law on {arm} by {gap}")
    noise = (0.002, 0.003, 0.01, 0.004, 0.005)
    values = dict(zip(("pa", "pp", "cd", "ca", "cp"), noise, strict=True)) | {"delta": 0.05}
    reference = ns.noisy_law("b0-rx-q8-p10", noise, None, 0.0, cz_phase=0.05)
    gap = float(np.abs(law("b0-rx-q8-p10", values) - reference).max())
    if gap > 1e-9:
        raise AssertionError(f"the simulator differs from noisy_law by {gap}")
    matrix = flip_matrix(0.1)
    if float(np.abs(matrix.sum(axis=0) - 1.0).max()) > 1e-15:
        raise AssertionError("the selector flip is not a stochastic matrix")
    found = planted_observations(PLANTED)
    spec = FitSpec(
        "planted",
        ("ca", "cp", f"z{Z_QUBIT}"),
        (0.02, 0.03, 0.0),
        (0.0, 0.0, -0.4),
        (0.3, 0.3, 0.4),
        (0.01, 0.01, 0.03),
    )
    _, fit = fit_item((spec, found))
    for key, truth in PLANTED.items():
        if abs(fit["values"][key] - truth) > 1e-4:
            raise AssertionError(f"planted {key}={truth} recovered as {fit['values'][key]}")
    if fit["histogram_chi2"] > 1.0:
        raise AssertionError(f"planted fit leaves chi-square {fit['histogram_chi2']}")
    blind = FitSpec("blind", ("ca", "cp"), (0.02, 0.03), (0.0, 0.0), (0.3, 0.3), (0.01, 0.01))
    _, miss = fit_item((blind, found))
    if miss["histogram_chi2"] < 100.0 * max(fit["histogram_chi2"], 1.0):
        raise AssertionError(f"a model without the planted q12 phase fits it: {miss['histogram_chi2']}")
    exact = {arm: law(arm, {}) for arm in PLANTED_ARMS}
    retained = [
        {
            "batch": "planted",
            "kind": "planted",
            "arm": arm,
            "counts": PLANTED_SHOTS * contract(exact[arm], PLANTED_RETENTION),
            "matrix": np.eye(rs.NOUT),
        }
        for arm in PLANTED_ARMS
    ]
    _, retention_chi2, retention = retention_profile_item(("planted", retained, exact))
    if abs(retention - PLANTED_RETENTION) > 1e-6 or retention_chi2 > 1e-3:
        raise AssertionError(f"planted retention {PLANTED_RETENTION} profiled as {retention} at {retention_chi2}")
    fake = {"histogram_chi2": 100.0, "stored_start_histogram_chi2": 100.0, "search": {"best_histogram_chi2": 100.0}}
    verify_search({"m": fake})
    for bad in (
        {"search": {"best_histogram_chi2": 99.0}},
        {"stored_start_histogram_chi2": 99.0},
    ):
        try:
            verify_search({"m": {**fake, **bad}})
        except ValueError:
            continue
        raise AssertionError(f"verify_search passes {bad}")
    largest_first = (
        "five_noise_terms_q12_z_after_pulse",
        "five_noise_terms_selector_flip",
        RETENTION,
        "cz_noise_flip_q12_z_after_pulse",
        "five_noise_terms",
        EXACT,
    )
    ordered = {
        name: {"free": [], "values": {}, "bounds": {}, "histogram_chi2": 10.0 * rank}
        for rank, name in enumerate(largest_first)
    }
    verify_nesting(ordered)
    ordered[RETENTION]["histogram_chi2"] = 1e9
    try:
        verify_nesting(ordered)
    except ValueError:
        pass
    else:
        raise AssertionError("verify_nesting passes a larger model that fits worse than the model it contains")
    return (
        f"qi_pathion_null_rotation_scan_phase_refit self-test: OK (noisy_law gap {gap:.1e}; planted q12 phase "
        f"{fit['values'][f'z{Z_QUBIT}']:+.5f} recovered, chi-square {fit['histogram_chi2']:.2e}, "
        f"{miss['histogram_chi2']:.0f} without it; planted retention {retention:.6f} profiled)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="DIR")
    mode.add_argument("--check", type=Path, metavar="DIR")
    mode.add_argument("--profile", type=Path, metavar="DIR")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.write is not None:
        print(f"wrote {write(args.write)}")
    elif args.check is not None or args.profile is not None:
        try:
            if args.check is not None:
                check(args.check)
            else:
                profile(args.profile)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"{(args.check or args.profile) / RECORD} matches the replay")
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    sys.exit(main())
