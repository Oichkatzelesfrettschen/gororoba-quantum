"""Shot-level simulation of the Tuna-17 injected-rotation scan under physical noise, read by its own decision.

The written case `results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md` fits a noise model of
two contractions (toward uniform, and of the three data bits alone). Its operating characteristics are drawn from
that same model. This program asks what the preregistered decision reads when the visibility loss comes from gate
noise instead: a density matrix over the five region qubits carries the retained b0 instruction list with a Kraus
channel after each pulse or CZ, and a planted mechanism (a coherent rotation on the pulses, an amplitude scale on
every pulse angle, a conditional-phase error of the CZ gates, or a stochastic map on the selector read) sized to the
observed center contrast where the mechanism reaches it.

Noise kinds, each a one-parameter family whose strength is set so that the center arm reads the visibility 0.44 of
the retained b0 runs (`pathion_one_cz_null_tuna_17_analysis.v3.json`, `template_rows.b0`): two-qubit depolarizing
after each CZ; phase damping after each pulse; phase damping on both qubits after each CZ; amplitude damping on both
qubits after each CZ; and amplitude with phase damping after pulses and CZ together. hypothesis: Tuna-17's loss on b0
lies inside the span of these families; the provider publishes no channel tomography of the region.

A simulated series follows the case's 21 batches under one of two readout regimes. `retained_walk`: the (e01, e10)
of the five qubits walk through the retained bracket rates of the one-CZ series in their recorded order from a
random start, one step per bracket (q11's e10 moves between 0.03 and 0.43 there). `stable`: every bracket holds the
mean retained rates. Each bracket reads its rates with binomial noise at the case's readout shots, and a data batch
is read through the assignment at a uniform point between its two brackets. Data circuits draw multinomial counts at
the case's shots.
The counts pass through the statistics, guard, bridge and fit of
`qi_pathion_null_rotation_scan_cases` (`count_statistics`, `decide`, `outcome`), the functions `evaluate` applies to
hardware shots; `--self-test` requires the two paths to agree on a series expanded to shot strings.

--run OUT [--series N] [--kinds ...] [--truths ...] writes OUT after every scenario: per noise kind and truth the
planted parameter, the label of the expected contrasts (no sampling noise, exact readout knowledge), and over N
series the share of each label, of guard-admitted batches, the wrong-class share and the median chi-square of each
class leader. Seeds: `DRAW_RECORD` value `DRAW_INDEX` spawns one generator per scenario and series
(`numpy.random.SeedSequence`), so the record replays on any worker count. --cross-check adds, where the packages
import, the same noisy laws from Qiskit Aer's density-matrix method on `GOROROBA_AER_DEVICE` and the exact laws of the
QX twin's circuits from qxelarator at `QX_CHECK_SHOTS` shots. --replay RECORD recomputes a record's planted
parameters and expected-contrast labels and, with --series N, the first N series of every scenario.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402

from parallel import ordered_map  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

SCHEMA = "qi-pathion-null-rotation-scan-noise-v1"
RETAINED_ANALYSIS = "results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json"
QX_CASES = ROOT / "results/quantum_inspire/cases" / rs.QX_SERIES
DRAW_RECORD = rs.OC_DRAW
DRAW_INDEX = 1
TARGET_VISIBILITY = 0.44
QX_CHECK_SHOTS = 131072
QX_CHECK_Z = 5.0
AER_TOLERANCE = 1e-9
NQ = 5
DIM = 1 << NQ
IDENTITY = np.eye(2, dtype=complex)
PAULIS = (IDENTITY, rs.PAULI["x"], rs.PAULI["y"], rs.PAULI["z"])

# Noise kind -> (amplitude damping per pulse, phase damping per pulse, depolarizing per CZ, amplitude damping per CZ
# qubit, phase damping per CZ qubit) as multiples of the one strength the visibility fixes.
KINDS: dict[str, tuple[float, float, float, float, float]] = {
    "cz_depolarizing": (0.0, 0.0, 1.0, 0.0, 0.0),
    "pulse_dephasing": (0.0, 1.0, 0.0, 0.0, 0.0),
    "cz_dephasing": (0.0, 0.0, 0.0, 0.0, 1.0),
    "cz_damping": (0.0, 0.0, 0.0, 1.0, 0.0),
    "damping_and_dephasing": (1 / 3, 1 / 3, 0.0, 1.0, 1.0),
}

# Truth -> (mechanism, world or None, class the decision should read or None for no offset).
PULSE_TRUTHS = ("pulse_x_before_all", "pulse_x_before_q8", "pulse_y_before_all", "pulse_z_before_all")
READOUT_TRUTHS = tuple(rs.READOUT_WORLDS)
CZ_PHASE_TRUTHS = (-0.08, 0.08)
TRUTH_CLASS = {"x": "pulse_x", "y": "pulse_other", "z": "pulse_other"}


# Density matrix ---------------------------------------------------------------------------------------------------


def embed(matrices: dict[int, np.ndarray]) -> np.ndarray:
    out = np.ones((1, 1), dtype=complex)
    for axis in range(NQ):
        out = np.kron(out, matrices.get(axis, IDENTITY))
    return out


def damping_kraus(amplitude: float, phase: float) -> list[np.ndarray]:
    """Kraus operators of amplitude damping `amplitude` followed by phase damping `phase` on one qubit."""
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    return [p @ a for p in (p0, p1) for a in (a0, a1) if np.any(p @ a)]


def noise_of(kind: str, strength: float) -> tuple[float, float, float, float, float]:
    a, b, c, d, e = (strength * m for m in KINDS[kind])
    return a, b, c, d, e


def circuit_steps(
    arm: str, world: str | None, theta: float, cz_phase: float, scale: float = 0.0
) -> list[tuple[str, tuple[int, ...], np.ndarray]]:
    """The arm as (gate, region axes, unitary) steps with the planted pulse rotation and CZ phase folded in; `scale`
    multiplies every pulse angle, the injected part included, by 1 + scale."""
    ref = rs.retained()
    axis_of = {q: i for i, q in enumerate(ref["region"])}
    pulse, scope, steps = rs.ARMS[arm]
    injected = () if scope is None else rs.SCOPES[scope]
    error_axis, order, error_scope = ("x", "before", None) if world is None else rs.PULSE_WORLDS[world]
    faulty = () if error_scope is None else rs.SCOPES[error_scope]
    error = rs.rotation(error_axis, theta)
    out: list[tuple[str, tuple[int, ...], np.ndarray]] = []
    for gate, angle, qubits in ref["ops"]:
        axes = tuple(axis_of[q] for q in qubits)
        if gate == "CZ":
            out.append(("cz", axes, np.diag([1, 1, 1, -np.exp(1j * cz_phase)]).astype(complex)))
        elif gate == "Rz":
            out.append(("rz", axes, rs.rotation("z", float(angle or 0.0))))
        else:
            angle_x = math.pi / 2 + (steps * rs.STEP if pulse == "Rx" and qubits[0] in injected else 0)
            exact = rs.rotation("x", (1 + scale) * angle_x)
            if qubits[0] in faulty:
                exact = exact @ error if order == "before" else error @ exact
            out.append(("pulse", axes, exact))
    return out


def logical(probabilities: np.ndarray) -> np.ndarray:
    """Probabilities over the region axes (axis 0 most significant) as a law over the logical outcome index."""
    ref = rs.retained()
    axis_of = {q: i for i, q in enumerate(ref["region"])}
    axes = [axis_of[ref["roles"][key]] for key in reversed(rs.KEYS)]
    return np.asarray(probabilities.reshape((2,) * NQ).transpose(axes).reshape(rs.NOUT), dtype=float)


def noisy_law(
    arm: str,
    noise: tuple[float, float, float, float, float],
    world: str | None,
    theta: float,
    cz_phase: float = 0.0,
    scale: float = 0.0,
) -> np.ndarray:
    """Law of an arm over the logical outcome index under the gate noise and the planted coherent error."""
    pulse_amplitude, pulse_phase, cz_depolarizing, cz_amplitude, cz_phase_damping = noise
    rho = np.zeros((DIM, DIM), dtype=complex)
    rho[0, 0] = 1.0
    index = np.arange(DIM)
    pulse_kraus = damping_kraus(pulse_amplitude, pulse_phase)
    cz_kraus = damping_kraus(cz_amplitude, cz_phase_damping)
    for gate, axes, unitary in circuit_steps(arm, world, theta, cz_phase, scale):
        if gate == "cz":
            a, b = axes
            both = ((index >> (NQ - 1 - a)) & 1) * ((index >> (NQ - 1 - b)) & 1)
            diagonal = np.where(both == 1, unitary[3, 3], 1.0)
            rho = diagonal[:, None] * rho * diagonal.conj()[None, :]
            if cz_depolarizing:
                mixed = np.zeros_like(rho)
                for s in PAULIS:
                    for t in PAULIS:
                        op = embed({a: s, b: t})
                        mixed += op @ rho @ op.conj().T
                rho = (1 - cz_depolarizing) * rho + cz_depolarizing * mixed / 16
            if cz_amplitude or cz_phase_damping:
                for axis in axes:
                    rho = sum(
                        (embed({axis: k}) @ rho @ embed({axis: k}).conj().T for k in cz_kraus), np.zeros_like(rho)
                    )
            continue
        full = embed({axes[0]: unitary})
        rho = full @ rho @ full.conj().T
        if gate == "pulse" and (pulse_amplitude or pulse_phase):
            axis = axes[0]
            rho = sum((embed({axis: k}) @ rho @ embed({axis: k}).conj().T for k in pulse_kraus), np.zeros_like(rho))
    return logical(np.real(np.diag(rho)))


# Retained readout -------------------------------------------------------------------------------------------------


@cache
def retained_brackets() -> tuple[dict[int, tuple[float, float]], ...]:
    """(e01, e10) of the region qubits at each bracket of the one-CZ series, in recorded order; a batch that holds
    one of the two readout circuits keeps the other rate of the bracket before it."""
    record = json.loads((ROOT / RETAINED_ANALYSIS).read_text(encoding="utf-8"))
    region = rs.retained()["region"]
    last: dict[str, dict[int, float]] = {}
    out: list[dict[int, tuple[float, float]]] = []
    batches: dict[str, dict[str, dict[int, float]]] = {}
    for row in record["drift_covariate"]["references"]["references"]:
        batches.setdefault(row["batch"], {})[row["kind"]] = {int(q): float(v) for q, v in row["rates"].items()}
    for batch in sorted(batches):
        last |= batches[batch]
        if len(last) == 2:
            out.append({q: (last["e01"][q], last["e10"][q]) for q in region})
    if len(out) < 4:
        raise ValueError(f"{RETAINED_ANALYSIS} holds {len(out)} complete brackets")
    return tuple(out)


@cache
def mean_matrix() -> np.ndarray:
    """Assignment matrix at the mean retained bracket rates: the readout the sizing and expected labels use."""
    return np.asarray(cc.readout_matrix(mean_bracket(), rs.retained()["roles"]))


# Scenarios --------------------------------------------------------------------------------------------------------


def center_visibility(kind: str, strength: float) -> float:
    return float(rs.visibility(rs.read(noisy_law(rs.CENTER, noise_of(kind, strength), None, 0.0), mean_matrix())))


@cache
def strength_of(kind: str) -> float:
    """The strength at which the kind's center arm reads TARGET_VISIBILITY through the mean retained readout."""
    return float(brentq(lambda s: center_visibility(kind, s) - TARGET_VISIBILITY, 1e-6, 0.5, xtol=1e-10))


def readout_map(world: str, x: float) -> np.ndarray:
    family, key, state = rs.READOUT_WORLDS[world]
    make = oc.selector_flip if family == "flip" else oc.selector_dropout
    return np.asarray(make(rs.KEYS.index(key), state, float(x)))


def roots(function: Any, grid: np.ndarray) -> list[float]:
    values = [function(float(t)) for t in grid]
    return [
        float(brentq(function, float(grid[i]), float(grid[i + 1]), xtol=1e-9))
        for i in range(len(grid) - 1)
        if values[i] * values[i + 1] < 0
    ]


def truth_laws(kind: str, truth: dict[str, Any]) -> np.ndarray:
    """Laws of every arm (ARM_NAMES order) of a truth under a noise kind, before the readout assignment."""
    noise = noise_of(kind, strength_of(kind))
    world = truth["world"] if truth["mechanism"] == "pulse" else None
    theta = truth["parameter"] if truth["mechanism"] == "pulse" else 0.0
    phase = truth["parameter"] if truth["mechanism"] == "cz_phase" else 0.0
    scale = truth["parameter"] if truth["mechanism"] == "amplitude_scale" else 0.0
    laws = np.stack([noisy_law(arm, noise, world, theta, phase, scale) for arm in rs.ARM_NAMES])
    if truth["mechanism"] == "readout":
        laws = laws @ readout_map(truth["world"], truth["parameter"]).T
    return laws


def truths_of(kind: str) -> list[dict[str, Any]]:
    """Every truth of a noise kind, each pulse and readout world sized to the design center contrast."""
    noise = noise_of(kind, strength_of(kind))
    matrix = mean_matrix()

    def contrast(law: np.ndarray) -> float:
        return float(rs.selector_contrast(rs.read(law, matrix)))

    out: list[dict[str, Any]] = [
        {"name": "no_offset", "mechanism": "none", "world": None, "parameter": 0.0, "class": None}
    ]
    for world in PULSE_TRUTHS:
        axis = rs.PULSE_WORLDS[world][0]
        found = roots(
            lambda t, w=world: contrast(noisy_law(rs.CENTER, noise, w, t)) - rs.DESIGN_CONTRAST,
            np.linspace(-0.30, 0.30, 61),
        )
        for theta in found:
            out.append(
                {
                    "name": f"{world}@{theta:+.4f}",
                    "mechanism": "pulse",
                    "world": world,
                    "parameter": theta,
                    "class": TRUTH_CLASS[axis],
                }
            )
    exact = noisy_law(rs.CENTER, noise, None, 0.0)
    for world in READOUT_TRUTHS:
        found = roots(
            lambda x, w=world: contrast(readout_map(w, x) @ exact) - rs.DESIGN_CONTRAST, np.linspace(0.0, 0.20, 21)
        )
        for x in found:
            out.append(
                {"name": f"{world}@{x:.4f}", "mechanism": "readout", "world": world, "parameter": x, "class": "readout"}
            )
    scales = roots(
        lambda e: contrast(noisy_law(rs.CENTER, noise, None, 0.0, 0.0, e)) - rs.DESIGN_CONTRAST,
        np.linspace(-0.2, 0.2, 41),
    )
    for value in scales:
        out.append(
            {
                "name": f"amplitude_scale@{value:+.4f}",
                "mechanism": "amplitude_scale",
                "world": None,
                "parameter": value,
                "class": "pulse_x",
            }
        )
    for phase in CZ_PHASE_TRUTHS:
        out.append(
            {
                "name": f"cz_phase@{phase:+.2f}",
                "mechanism": "cz_phase",
                "world": None,
                "parameter": phase,
                "class": "pulse_other",
            }
        )
    return out


# Series -----------------------------------------------------------------------------------------------------------


@cache
def plan() -> tuple[dict[str, Any], ...]:
    return tuple(rs.batch_rows(rs.TUNA_SERIES))


REGIMES = ("stable", "retained_walk")


@cache
def mean_bracket() -> dict[int, tuple[float, float]]:
    pool = retained_brackets()
    return {q: (float(np.mean([b[q][0] for b in pool])), float(np.mean([b[q][1] for b in pool]))) for q in pool[0]}


def simulate_series(laws: np.ndarray, rng: np.random.Generator, regime: str = "stable") -> dict[str, Any]:
    """Counts of one series: per readout batch the read (e01, e10) of each region qubit, per data batch the counts
    of each circuit over the logical outcome index."""
    ref = rs.retained()
    region, roles = ref["region"], ref["roles"]
    pool = retained_brackets() if regime == "retained_walk" else (mean_bracket(),)
    rows = plan()
    start = int(rng.integers(len(pool)))
    true: dict[str, dict[int, tuple[float, float]]] = {}
    read: dict[str, dict[int, tuple[float, float]]] = {}
    step = 0
    for row in rows:
        if row["kind"] != "readout":
            continue
        rates = pool[(start + step) % len(pool)]
        step += 1
        true[row["batch"]] = rates
        read[row["batch"]] = {
            q: (
                float(rng.binomial(rs.READOUT_SHOTS, rates[q][0]) / rs.READOUT_SHOTS),
                float(rng.binomial(rs.READOUT_SHOTS, rates[q][1]) / rs.READOUT_SHOTS),
            )
            for q in region
        }
    names = [row["batch"] for row in rows]
    data: dict[str, list[np.ndarray]] = {}
    for n, row in enumerate(rows):
        if row["kind"] == "readout":
            continue
        before, after = true[names[n - 1]], true[names[n + 1]]
        weight = float(rng.random())
        during = {
            q: ((1 - weight) * before[q][0] + weight * after[q][0], (1 - weight) * before[q][1] + weight * after[q][1])
            for q in region
        }
        matrix = np.asarray(cc.readout_matrix(during, roles))
        data[row["batch"]] = [
            rng.multinomial(rs.SCAN_SHOTS, np.clip(matrix @ laws[rs.ARM_NAMES.index(rs.arm_of(c["file"]))], 0, None))
            for c in row["circuits"]
        ]
    return {"brackets": read, "data": data}


def decide_series(series: dict[str, Any]) -> dict[str, Any]:
    """The decision of `qi_pathion_null_rotation_scan_cases.evaluate` from a series' counts."""
    ref = rs.retained()
    region, roles = ref["region"], ref["roles"]
    rows = plan()
    names = [row["batch"] for row in rows]
    brackets = series["brackets"]
    batches: list[dict[str, Any]] = []
    matrices: dict[str, np.ndarray] = {}
    differences: list[tuple[float, float]] = []
    for n, row in enumerate(rows):
        if row["kind"] == "readout":
            continue
        before, after = brackets[names[n - 1]], brackets[names[n + 1]]
        admitted = all(abs(after[q][i] - before[q][i]) <= rs.GUARD_LIMIT for q in region for i in (0, 1))
        mean = {q: ((before[q][0] + after[q][0]) / 2, (before[q][1] + after[q][1]) / 2) for q in region}
        matrices[row["batch"]] = np.asarray(cc.readout_matrix(mean, roles))
        stats = [rs.count_statistics(counts) for counts in series["data"][row["batch"]]]
        arms = [rs.arm_of(c["file"]) for c in row["circuits"]]
        if row["kind"] == "bridge":
            rx = oc.pooled([(s["contrast"], s["se"]) for a, s in zip(arms, stats, strict=True) if a == rs.CENTER])
            x90 = oc.pooled([(s["contrast"], s["se"]) for a, s in zip(arms, stats, strict=True) if a == rs.RETAINED])
            if admitted:
                differences.append((rx[0] - x90[0], math.hypot(rx[1], x90[1])))
            continue
        batches.append(
            {
                "name": row["batch"],
                "kind": row["kind"],
                "arms": arms,
                "contrasts": [s["contrast"] for s in stats],
                "errors": [s["se"] for s in stats],
                "center_visibility": stats[arms.index(rs.CENTER)]["visibility"],
                "admitted": admitted,
            }
        )
    bridges = sum(1 for row in rows if row["kind"] == "bridge")
    bridge = oc.pooled(differences) if len(differences) == bridges else None
    return rs.outcome(rs.decide(batches, bridge, lambda b: matrices[b["name"]], transfer=True))


def expected_label(laws: np.ndarray) -> dict[str, Any]:
    """The decision on the expected contrasts of a truth: no sampling noise, the mean retained readout known."""
    matrix = mean_matrix()
    seen = rs.read(laws, matrix)
    contrast = dict(zip(rs.ARM_NAMES, rs.selector_contrast(seen), strict=True))
    visibility = float(rs.visibility(seen[rs.ARM_NAMES.index(rs.CENTER)]))
    batches = rs.planted_batches(None, 0.0, row={k: float(v) for k, v in contrast.items()})
    for batch in batches:
        batch["center_visibility"] = visibility
    decision = rs.decide(batches, None, lambda _b: matrix)
    numbers = decision["numbers"]
    return {
        "label": decision["label"],
        "center_contrast": round(float(contrast[rs.CENTER]), 5),
        "center_visibility": round(visibility, 4),
        "chi2_of_class_leader": {name: numbers["chi2"][world] for name, world in numbers.get("best_world", {}).items()},
        "best_world": numbers.get("best_world"),
        "contraction_share": {
            name: numbers["contraction_share"][world] for name, world in numbers.get("best_world", {}).items()
        },
    }


def series_summary(item: tuple[np.ndarray, np.random.SeedSequence, str]) -> dict[str, Any]:
    """Pool worker: one simulated series of a truth, reduced to its label and class-leader numbers."""
    laws, seed, regime = item
    decision = decide_series(simulate_series(laws, np.random.default_rng(seed), regime))
    numbers = decision["numbers"]
    leaders = numbers.get("best_world", {})
    return {
        "label": decision["label"],
        "rx_label": numbers.get("rx_label"),
        "a5_186": decision["a5_186"],
        "admitted": len(numbers["admitted_batches"]),
        "chi2": {name: numbers["chi2"][world] for name, world in leaders.items()},
        "best_world": leaders,
    }


def wrong(label: str, rx_label: str | None, truth_class: str | None) -> bool:
    """A deciding class label (or the Rx class under a failed bridge) that names a class other than the truth's;
    `x_excluded` is wrong for an x truth alone."""
    seen = rx_label if label == "unresolved_bridge" else label
    if seen not in rs.DECIDING:
        return False
    if seen == "x_excluded":
        return truth_class == "pulse_x"
    return seen != truth_class


def regime_rows(
    laws: np.ndarray, truth: dict[str, Any], count: int, seed: np.random.SeedSequence, regime: str
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if count:
        rows = ordered_map(series_summary, [(laws, child, regime) for child in seed.spawn(count)], min_items=1)
        labels: dict[str, int] = {}
        for row in rows:
            labels[row["label"]] = labels.get(row["label"], 0) + 1
        medians = {
            name: round(float(np.median([r["chi2"][name] for r in rows if name in r["chi2"]])), 2)
            for name in rs.CLASSES
            if any(name in r["chi2"] for r in rows)
        }
        out |= {
            "labels": dict(sorted(labels.items())),
            "wrong_class": sum(wrong(r["label"], r["rx_label"], truth["class"]) for r in rows),
            "mean_admitted_scan_batches": round(float(np.mean([r["admitted"] for r in rows])), 3),
            "median_chi2_of_class_leader": medians,
            "per_series": [[r["label"], r["rx_label"], r["admitted"]] for r in rows],
        }
    return out


def scenario(kind: str, truth: dict[str, Any], count: int, seed: np.random.SeedSequence) -> dict[str, Any]:
    laws = truth_laws(kind, truth)
    children = seed.spawn(len(REGIMES))
    return {
        **truth,
        "kind": kind,
        "expected": expected_label(laws),
        "series": count,
        "regimes": {
            regime: regime_rows(laws, truth, count, child, regime)
            for regime, child in zip(REGIMES, children, strict=True)
        },
    }


def scenario_seeds(kinds: list[str]) -> dict[tuple[str, str], np.random.SeedSequence]:
    """One seed sequence per (kind, truth name), keyed by position in KINDS and in the kind's truth list."""
    root = int(read_record(DRAW_RECORD)["values"][DRAW_INDEX])
    out = {}
    for kind in kinds:
        for position, truth in enumerate(truths_of(kind)):
            out[kind, truth["name"]] = np.random.SeedSequence([root, list(KINDS).index(kind), position])
    return out


def run(out: Path, count: int, kinds: list[str], only: list[str] | None, cross: bool) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "case": f"results/quantum_inspire/cases/{rs.TUNA_SERIES}/CASE.md",
        "claim_kind": "numerical simulation",
        "seed": {"qrng_draw": DRAW_RECORD, "index": DRAW_INDEX},
        "target_visibility": TARGET_VISIBILITY,
        "retained_brackets": len(retained_brackets()),
        "shots": {"scan": rs.SCAN_SHOTS, "readout": rs.READOUT_SHOTS},
        "series_per_scenario": count,
        "strength": {kind: round(strength_of(kind), 6) for kind in kinds},
        "scenarios": [],
    }
    if cross:
        record["cross_check"] = cross_check(kinds)
    seeds = scenario_seeds(kinds)
    for kind in kinds:
        for truth in truths_of(kind):
            if only and not any(truth["name"].startswith(prefix) for prefix in only):
                continue
            row = scenario(kind, truth, count, seeds[kind, truth["name"]])
            record["scenarios"].append(row)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(
                f"{kind} {truth['name']}: expected {row['expected']['label']}; "
                + "; ".join(
                    f"{g} {r.get('labels', {})} wrong {r.get('wrong_class', 0)}" for g, r in row["regimes"].items()
                ),
                flush=True,
            )
    record["summary"] = summarize(record["scenarios"])
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return record


def summarize(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    wrong_expected = [f"{s['kind']}/{s['name']}" for s in scenarios if wrong(s["expected"]["label"], None, s["class"])]
    wrong_series = {
        f"{s['kind']}/{s['name']}/{regime}": [rows["wrong_class"], s["series"]]
        for s in scenarios
        for regime, rows in s["regimes"].items()
        if rows.get("wrong_class")
    }
    return {"expected_label_names_a_wrong_class": wrong_expected, "series_naming_a_wrong_class": wrong_series}


# Cross-checks -----------------------------------------------------------------------------------------------------


def aer_law(arm: str, noise: tuple[float, float, float, float, float], world: str | None, theta: float) -> np.ndarray:
    """The law of `noisy_law` from Qiskit Aer's density-matrix method on GOROROBA_AER_DEVICE."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Kraus
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import depolarizing_error

    pulse_amplitude, pulse_phase, cz_depolarizing, cz_amplitude, cz_phase_damping = noise
    circuit = QuantumCircuit(NQ)
    pulse_noise = Kraus(damping_kraus(pulse_amplitude, pulse_phase)).to_instruction()
    cz_noise = Kraus(damping_kraus(cz_amplitude, cz_phase_damping)).to_instruction()
    for gate, axes, unitary in circuit_steps(arm, world, theta, 0.0):
        # Region axis a is Qiskit qubit NQ - 1 - a, so axis 0 is the most significant bit of a probability index.
        qubits = [NQ - 1 - a for a in axes]
        if gate == "cz":
            circuit.cz(*qubits)
            if cz_depolarizing:
                circuit.append(depolarizing_error(cz_depolarizing, 2).to_instruction(), qubits)
            if cz_amplitude or cz_phase_damping:
                for q in qubits:
                    circuit.append(cz_noise, [q])
            continue
        circuit.append(UnitaryGate(unitary), qubits)
        if gate == "pulse" and (pulse_amplitude or pulse_phase):
            circuit.append(pulse_noise, qubits)
    circuit.save_probabilities()
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    result = AerSimulator(method="density_matrix", device=device).run(circuit, shots=1).result()
    if not result.success:
        raise RuntimeError(f"Aer: {result.status}")
    return logical(np.asarray(result.data(0)["probabilities"]))


def aer_check(kinds: list[str]) -> dict[str, Any]:
    worst = 0.0
    count = 0
    for kind in kinds:
        noise = noise_of(kind, strength_of(kind))
        for arm in rs.ARM_NAMES:
            for world, theta in ((None, 0.0), ("pulse_x_before_all", 0.05), ("pulse_y_before_all", -0.07)):
                worst = max(
                    worst, float(np.abs(aer_law(arm, noise, world, theta) - noisy_law(arm, noise, world, theta)).max())
                )
                count += 1
    if worst > AER_TOLERANCE:
        raise RuntimeError(f"Aer and the numpy density matrix differ by {worst}")
    import qiskit_aer

    return {
        "device": os.environ.get("GOROROBA_AER_DEVICE", "CPU"),
        "qiskit_aer": qiskit_aer.__version__,
        "laws_compared": count,
        "largest_difference": worst,
    }


def qx_check() -> dict[str, Any]:
    """Every circuit of the QX twin on qxelarator: its counts over the logical index against its `ideal` law."""
    import qxelarator

    seed = int(read_record(DRAW_RECORD)["values"][DRAW_INDEX])
    rows = []
    for position, directory in enumerate(sorted(p for p in QX_CASES.glob("batch-*") if p.is_dir())):
        manifest = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        roles = {k: int(v) for k, v in manifest["templates"]["b0"]["roles"].items()}
        for offset, circuit in enumerate(manifest["circuits"]):
            text = (directory / circuit["file"]).read_text(encoding="utf-8")
            result = qxelarator.execute_string(
                text, iterations=QX_CHECK_SHOTS, seed=(seed + 16 * position + offset) % 2**31
            )
            if isinstance(result, qxelarator.SimulationError) or result.shots_done != QX_CHECK_SHOTS:
                raise RuntimeError(f"qxelarator: {result}")
            counts = np.zeros(rs.NOUT)
            for key, value in result.results.items():
                # qxelarator puts qubit 0 at the rightmost character of a key.
                outcome = sum(int(str(key)[len(str(key)) - 1 - roles[name]]) << v for v, name in enumerate(rs.KEYS))
                counts[outcome] += int(value)
            ideal = np.array(circuit["ideal"], dtype=float)
            sigma = np.sqrt(np.maximum(ideal * (1 - ideal), 1e-12) / QX_CHECK_SHOTS)
            z = float(np.abs((counts / QX_CHECK_SHOTS - ideal) / sigma).max())
            if z > QX_CHECK_Z:
                raise RuntimeError(f"qxelarator reads {directory.name}/{circuit['file']} at {z:.1f} standard errors")
            rows.append({"circuit": f"{directory.name}/{circuit['file']}", "largest_z": round(z, 2)})
    return {"qxelarator": getattr(qxelarator, "__version__", "0.10.0"), "shots": QX_CHECK_SHOTS, "circuits": rows}


def cross_check(kinds: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, check in (("aer", lambda: aer_check(kinds)), ("qx", qx_check)):
        try:
            out[name] = check()
        except ImportError as error:
            out[name] = {"skip": f"{error.name} is not importable"}
    return out


# Replay and self-test ---------------------------------------------------------------------------------------------


def replay(path: Path, count: int) -> str:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["schema"] != SCHEMA:
        raise ValueError(f"{path}: schema {record['schema']}")
    kinds = list(record["strength"])
    seeds = scenario_seeds(kinds)
    truths = {(kind, t["name"]): t for kind in kinds for t in truths_of(kind)}
    for kind in kinds:
        if abs(strength_of(kind) - record["strength"][kind]) > 2e-6:
            raise ValueError(f"{path}: strength of {kind} is {strength_of(kind)}")
    checked = 0
    for row in record["scenarios"]:
        truth = truths.get((row["kind"], row["name"]))
        if truth is None or abs(truth["parameter"] - row["parameter"]) > 1e-9:
            raise ValueError(f"{path}: {row['kind']}/{row['name']} is not a truth of this checkout")
        fresh = scenario(row["kind"], truth, min(count, row["series"]), seeds[row["kind"], row["name"]])
        if fresh["expected"]["label"] != row["expected"]["label"]:
            raise ValueError(f"{path}: {row['kind']}/{row['name']} expects {fresh['expected']['label']}")
        for regime, rows in fresh["regimes"].items():
            if count and rows["per_series"] != row["regimes"][regime]["per_series"][: len(rows["per_series"])]:
                raise ValueError(f"{path}: {row['kind']}/{row['name']}/{regime} series differ from the record")
        checked += 1
    if summarize(record["scenarios"]) != record.get("summary"):
        raise ValueError(f"{path}: summary differs from the scenarios")
    return f"{path}: {checked} scenarios replay ({count} series each)"


def strings_of(series: dict[str, Any]) -> dict[str, list[str]]:
    """Shot strings of a series' counts for `evaluate`: the region qubits carry the bits, every other qubit reads 0."""
    ref = rs.retained()
    region, roles = ref["region"], ref["roles"]
    out: dict[str, list[str]] = {}
    for row in plan():
        if row["kind"] == "readout":
            rates = series["brackets"][row["batch"]]
            for state, name in ((0, "readout-0.cq"), (1, "readout-1.cq")):
                shots = []
                for n in range(rs.READOUT_SHOTS):
                    bits = ["0"] * cc.NQUBITS
                    for q in region:
                        wrong_reads = round(rates[q][state] * rs.READOUT_SHOTS)
                        flipped = n < wrong_reads
                        bits[cc.NQUBITS - 1 - q] = str(state ^ int(flipped))
                    shots.append("".join(bits))
                out[f"{row['batch']}/{name}"] = shots
            continue
        for circuit, counts in zip(row["circuits"], series["data"][row["batch"]], strict=True):
            shots = []
            for outcome, number in enumerate(counts):
                bits = ["0"] * cc.NQUBITS
                for position, key in enumerate(rs.KEYS):
                    if (outcome >> position) & 1:
                        bits[cc.NQUBITS - 1 - roles[key]] = "1"
                shots += ["".join(bits)] * int(number)
            out[f"{row['batch']}/{circuit['file']}"] = shots
    return out


def self_test() -> str:
    exact = noisy_law(rs.CENTER, (0.0, 0.0, 0.0, 0.0, 0.0), None, 0.0)
    if np.abs(exact - rs.forward_law(rs.CENTER)).max() > 1e-12:
        raise AssertionError("the noiseless density matrix differs from the state-vector law")
    planted = noisy_law("b0-rx-q8-m10", (0.0, 0.0, 0.0, 0.0, 0.0), "pulse_y_before_all", -0.07)
    if np.abs(planted - rs.forward_law("b0-rx-q8-m10", "pulse_y_before_all", -0.07)).max() > 1e-12:
        raise AssertionError("the noiseless density matrix differs from the state-vector law of a planted world")
    for kind in KINDS:
        law = noisy_law(rs.CENTER, noise_of(kind, strength_of(kind)), None, 0.0)
        if abs(law.sum() - 1) > 1e-10 or law.min() < -1e-12:
            raise AssertionError(f"{kind}: the law is not a probability vector")
        if abs(center_visibility(kind, strength_of(kind)) - TARGET_VISIBILITY) > 1e-6:
            raise AssertionError(f"{kind}: the visibility misses its target")
    kind = "cz_depolarizing"
    truth = next(t for t in truths_of(kind) if t["world"] == "pulse_x_before_all" and t["parameter"] > 0)
    series = simulate_series(truth_laws(kind, truth), np.random.default_rng(np.random.SeedSequence([0, 1])))
    manifest = json.loads(
        (ROOT / "results/quantum_inspire/cases" / rs.TUNA_SERIES / "batch-01" / "cases.json").read_text(
            encoding="utf-8"
        )
    )
    series["brackets"] = {
        batch: {q: tuple(round(v * rs.READOUT_SHOTS) / rs.READOUT_SHOTS for v in pair) for q, pair in rates.items()}
        for batch, rates in series["brackets"].items()
    }
    fast = decide_series(series)
    slow = rs.evaluate(strings_of(series), manifest)["decision"]
    if fast["label"] != slow["label"] or fast["numbers"]["chi2"] != slow["numbers"]["chi2"]:
        raise AssertionError(f"the counts path reads {fast['label']} and evaluate reads {slow['label']}")
    if fast["label"] != "pulse_x":
        raise AssertionError(f"a planted over-rotation under CZ depolarizing reads {fast['label']}")
    walked = decide_series(simulate_series(truth_laws(kind, truth), np.random.default_rng([0, 2]), "retained_walk"))
    if len(walked["numbers"]["admitted_batches"]) >= 8:
        raise AssertionError("the retained readout walk admits every scan batch")
    if not wrong("pulse_x", None, "pulse_other") or wrong("unresolved_both", None, "pulse_x"):
        raise AssertionError("the wrong-class rule misreads a label")
    if wrong("x_excluded", None, "readout") or not wrong("unresolved_bridge", "readout", "pulse_x"):
        raise AssertionError("the wrong-class rule misreads x_excluded or a failed bridge")
    return "qi_pathion_null_rotation_scan_noise self-test: OK"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--series", type=int, default=0)
    parser.add_argument("--kinds", nargs="+", choices=list(KINDS), default=list(KINDS))
    parser.add_argument("--truths", nargs="+", help="keep the truths whose name starts with one of these")
    parser.add_argument("--cross-check", action="store_true")
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    if args.run:
        record = run(args.run, args.series, args.kinds, args.truths, args.cross_check)
        print(json.dumps(record["summary"], indent=1))
    if args.replay:
        print(replay(args.replay, args.series))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
