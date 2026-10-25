"""Primorial cover-defect circuits under retained calibration noise: Grover quotient, phase gradients, QAOA.

gororoba_quantum/primorial_cover.py derives three small circuit families from
the certified missing gaps 20, 86 and 88 of the primorial wheels P_6 and P_14.
This script compiles each family onto a path of the snapshot's coupling map
and computes every arm's exact noisy outcome law with
snapshot_laws.outcome_law (live_run's gate, idle and assignment noise):

1. **Gap-20 quotient (two qubits).** H = 2 I - |a=0, b=1><a=0, b=1| on the
   parities a (qubit 0) and b (qubit 1). One Grover iteration marks one
   label m (phase oracle X^{1-m} CZ X^{1-m}, then the diffuser) and ideally
   reads m with probability 1; the arm marked with the complement of m reads m
   with probability 0; the no-oracle arm (Hadamards then the diffuser) reads
   every label with 1/4. Four basis preparations give the readout reference.
   The problem's own label is m = 10 (q1 = 1, q0 = 0), and the lifted score
   is the mean of the quotient energy under the law.
2. **Phase gradients (three qubits).** For each slice cost (gap86, gap88 and
   gap88 repaired by the class 29 mod 47) and each of the twelve cube edges
   (j, x) with x_j = 0, the arm prepares (|x> + |x ^ 2^j>)/sqrt2, applies
   U = exp(-i gamma H) with gamma = pi/9 through the eight-CNOT network
   (CX_{0,1} CX_{1,2})^4 and its seven RZ(2 gamma c_S), and reads qubit j in
   the X or the Y basis. Ideally <X_j> = cos(gamma d) and <Y_j> = -sin(gamma d)
   with d = E(x ^ 2^j) - E(x). A least-squares potential on the cube's
   edges recovers every nonconstant c_S; the residual lies in the five-dimensional
   cycle space. The gap86 repair shifts H by -I, so its circuits equal the
   unrepaired ones and are compiled only to prove it.
3. **QAOA contrast (three qubits).** One layer exp(-i beta sum X)
   exp(-i gamma H)|+++> at primorial_cover.QAOA_ANGLES for gap88 before and
   after repair, whose ideal laws differ in total variation by 0.132128193.

Every compile runs at optimization level 0 with the initial layout given, so
the cost block of every arm is the same instruction sequence; the compiled CZ
count must equal the logical CX and CZ count, which excludes inserted SWAPs.
The noiseless law of each compiled arm must equal its ideal law to 1e-9.
Layouts: the path minimizing summed CZ error plus mean assignment error, and
the path at the median of that cost, so the prediction spans a good and a
typical patch. Shot prices use the delta method for the phase of (<X>, <Y>)
and resolve each contrast at z = Z_SCORE.

``--out FILE`` writes the record; ``--check FILE --run DIR`` requires FILE to
be byte-identical to the collected output of Kaggle run DIR, recomputes the
laws on GOROROBA_AER_DEVICE and requires layouts and CZ counts to match exactly
and each law to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import primorial_cover as pc  # noqa: E402
import snapshot_laws  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
OUTPUT = "results/kaggle_out/primorial_cover_noise.json"
GRADIENT_GAMMA = math.pi / 9
Z_SCORE = 3.0
# A coefficient is identified when its estimate lies within half the 1/8 grid.
IDENTIFY_RADIUS = 1.0 / 16.0
# Two-sided z for all seven coefficients of one cost at family-wise level 0.01 (Bonferroni).
SIMULTANEOUS_Z = statistics.NormalDist().inv_cdf(1.0 - 0.01 / (2 * 7))
# Coherent sensitivity scenarios: a conditional phase (rad) after every CZ, and a fractional
# amplitude error eta on every sx, RX(pi/2 (1 + eta)), spanning the retained atlas scales.
COHERENT_SCENARIOS = (
    ("cz_phase", 0.02),
    ("cz_phase", 0.05),
    ("cz_phase", 0.1),
    ("sx_amplitude", 0.002),
    ("sx_amplitude", 0.004),
    ("sx_amplitude", 0.01),
)
# "null" is the zero table: the same eight-CNOT block with every RZ at angle zero, ideally the identity.
GRADIENT_COSTS = ("null", "gap86", "gap86_repaired", "gap88", "gap88_repaired")


def cost_table(name: str) -> list[int]:
    if name == "null":
        return [0] * 8
    case, _, repaired = name.partition("_")
    return pc.slice_table(case, repaired=bool(repaired))


def coefficients(table: list[int]) -> dict[str, float]:
    return {key: float(value) for key, value in pc.walsh(table).items() if key}


# ---------------------------------------------------------------- layouts


def _readout(snapshot: dict[str, Any], q: int) -> float:
    row = snapshot["qubits"][q]
    return 0.5 * (row["e01"] + row["e10"])


def path_costs(snapshot: dict[str, Any], length: int) -> list[tuple[float, list[int]]]:
    """Every simple path of ``length`` qubits on working CZ edges, with its error cost, sorted."""
    error = {tuple(sorted(row["qargs"])): row["error"] for row in snapshot["instructions"]["cz"] if row["error"] < 1.0}
    neighbors: dict[int, set[int]] = {}
    for a, b in error:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    paths: list[list[int]] = [[q] for q in sorted(neighbors)]
    for _ in range(length - 1):
        paths = [[*p, n] for p in paths for n in sorted(neighbors[p[-1]]) if n not in p]
    unique = {tuple(p) if p[0] < p[-1] else tuple(reversed(p)) for p in paths}
    costs = [
        (
            sum(error[tuple(sorted(e))] for e in zip(p, p[1:], strict=False))
            + sum(_readout(snapshot, q) for q in p) / len(p),
            list(p),
        )
        for p in unique
    ]
    return sorted(costs)


def layouts(snapshot: dict[str, Any], length: int) -> dict[str, list[int]]:
    ranked = path_costs(snapshot, length)
    return {"best": ranked[0][1], "median": ranked[len(ranked) // 2][1]}


# --------------------------------------------------------------- circuits


def cost_block(circuit: QuantumCircuit, table: list[int], gamma: float) -> None:
    """exp(-i gamma H) up to a global phase, through the eight-CNOT network on the path 0-1-2."""
    c = coefficients(table)
    angle = {mask: 2.0 * gamma * c["".join(str(j) for j in range(3) if mask >> j & 1)] for mask in range(1, 8)}
    wires = [1, 2, 4]
    done: set[int] = set()
    for j in range(3):
        circuit.rz(angle[wires[j]], j)
        done.add(wires[j])
    for _ in range(4):
        for control, target in ((0, 1), (1, 2)):
            circuit.cx(control, target)
            wires[target] ^= wires[control]
            if wires[target] not in done:
                circuit.rz(angle[wires[target]], target)
                done.add(wires[target])


def gradient_arm(table: list[int], j: int, x: int, basis: str) -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)
    for i in range(3):
        if i != j and x >> i & 1:
            circuit.x(i)
    circuit.h(j)
    circuit.barrier()
    cost_block(circuit, table, GRADIENT_GAMMA)
    circuit.barrier()
    if basis == "Y":
        circuit.sdg(j)
    circuit.h(j)
    circuit.measure(range(3), range(3))
    return circuit


def gradient_ideal(table: list[int], j: int, x: int, basis: str) -> float:
    d = table[x ^ (1 << j)] - table[x]
    return math.cos(GRADIENT_GAMMA * d) if basis == "X" else -math.sin(GRADIENT_GAMMA * d)


def edges() -> list[tuple[int, int]]:
    return [(j, x) for j in range(3) for x in range(8) if not x >> j & 1]


def qaoa_arm(table: list[int], gamma: float, beta: float) -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)
    circuit.h(range(3))
    circuit.barrier()
    cost_block(circuit, table, gamma)
    circuit.barrier()
    circuit.rx(2.0 * beta, range(3))
    circuit.measure(range(3), range(3))
    return circuit


def grover_arm(mark: int | None) -> QuantumCircuit:
    """One Grover iteration on two qubits marking label ``mark`` (None: no oracle)."""
    circuit = QuantumCircuit(2, 2)
    circuit.h(range(2))
    if mark is not None:
        flips = [q for q in range(2) if not mark >> q & 1]
        circuit.barrier()
        if flips:
            circuit.x(flips)
        circuit.cz(0, 1)
        if flips:
            circuit.x(flips)
    circuit.barrier()
    circuit.h(range(2))
    circuit.x(range(2))
    circuit.cz(0, 1)
    circuit.x(range(2))
    circuit.h(range(2))
    circuit.measure(range(2), range(2))
    return circuit


def basis_arm(width: int, label: int) -> QuantumCircuit:
    circuit = QuantumCircuit(width, width)
    for q in range(width):
        if label >> q & 1:
            circuit.x(q)
    circuit.measure(range(width), range(width))
    return circuit


def ideal_law(circuit: QuantumCircuit) -> np.ndarray:
    from qiskit.quantum_info import Statevector

    body = circuit.remove_final_measurements(inplace=False)
    law: np.ndarray = Statevector(body).probabilities()
    return law


def arms() -> list[tuple[dict[str, Any], QuantumCircuit]]:
    out: list[tuple[dict[str, Any], QuantumCircuit]] = []
    for mark in range(4):
        out.append(({"family": "quotient", "arm": "marked", "label": mark}, grover_arm(mark)))
        out.append(({"family": "quotient", "arm": "wrong_mark", "label": mark}, grover_arm(3 - mark)))
        out.append(({"family": "quotient", "arm": "readout", "label": mark}, basis_arm(2, mark)))
    out.append(({"family": "quotient", "arm": "no_oracle", "label": None}, grover_arm(None)))
    for name in GRADIENT_COSTS:
        table = cost_table(name)
        for j, x in edges():
            for basis in ("X", "Y"):
                meta = {"family": "gradient", "cost": name, "j": j, "x": x, "basis": basis}
                out.append((meta, gradient_arm(table, j, x, basis)))
    for case in ("gap88",):
        gamma, beta = pc.QAOA_ANGLES[case]
        for repaired in (False, True):
            meta = {"family": "qaoa", "cost": case + ("_repaired" if repaired else "")}
            out.append((meta, qaoa_arm(pc.slice_table(case, repaired=repaired), gamma, beta)))
    for label in range(8):
        out.append(({"family": "readout3", "label": label}, basis_arm(3, label)))
    return out


def logical_entanglers(circuit: QuantumCircuit) -> int:
    return sum(1 for instruction in circuit.data if instruction.operation.name in ("cx", "cz"))


def compile_arm(view: Any, circuit: QuantumCircuit, layout: list[int]) -> QuantumCircuit:
    compiled = transpile(circuit, view, initial_layout=layout, optimization_level=0)
    cz = sum(1 for instruction in compiled.data if instruction.operation.name == "cz")
    if cz != logical_entanglers(circuit):
        raise SystemExit(f"compile on {layout} has {cz} CZ against {logical_entanglers(circuit)} logical entanglers")
    return compiled


class ArmLaw:
    """Picklable worker: one (metadata, logical, compiled) arm -> its checked noisy law."""

    def __init__(self, snapshot: dict[str, Any], device: str) -> None:
        self.snapshot = snapshot
        self.device = device

    def __call__(self, item: tuple[dict[str, Any], QuantumCircuit, QuantumCircuit]) -> dict[str, Any]:
        meta, logical, compiled = item
        expected = ideal_law(logical)
        noiseless = snapshot_laws.outcome_law(self.snapshot, compiled, self.device, noisy=False)
        if not np.allclose(noiseless, expected, atol=1e-9):
            raise SystemExit(f"{meta}: compiled noiseless law {noiseless} against {expected}")
        law = snapshot_laws.outcome_law(self.snapshot, compiled, self.device)
        return {
            **meta,
            "ideal": [round(float(v), 12) for v in expected],
            "law": [float(v) for v in law],
            "cz": sum(1 for instruction in compiled.data if instruction.operation.name == "cz"),
            "depth": compiled.depth(),
        }


class CoherentLaw:
    """Picklable worker: a compiled arm's noiseless law under one coherent error family.

    ``cz_phase`` follows every CZ by CPhase(value) on its pair; ``sx_amplitude`` replaces every sx by
    RX(pi/2 (1 + value)). The first is diagonal; the second acts inside every Hadamard of the network.
    """

    def __init__(self, snapshot: dict[str, Any], device: str, family: str, value: float) -> None:
        self.snapshot = snapshot
        self.device = device
        self.family = family
        self.value = value

    def replace(self, operation: Any, qubits: list[int]) -> Any:
        from qiskit.circuit.library import RXGate, UnitaryGate

        if operation.name == "barrier":
            return None
        if self.family == "cz_phase" and operation.name == "cz":
            return UnitaryGate(np.diag([1.0, 1.0, 1.0, -np.exp(1j * self.value)]), label="cz_cphase")
        if self.family == "sx_amplitude" and operation.name == "sx":
            return RXGate(math.pi / 2 * (1.0 + self.value))
        return operation

    def __call__(self, item: tuple[dict[str, Any], QuantumCircuit]) -> dict[str, Any]:
        meta, compiled = item
        law = snapshot_laws.outcome_law(self.snapshot, compiled, self.device, replace=self.replace, noisy=False)
        return {**meta, "law": [float(v) for v in law]}


def coherent_sensitivity(
    snapshot: dict[str, Any], device: str, compiled: list[tuple[dict[str, Any], QuantumCircuit]]
) -> list[dict[str, Any]]:
    """Coefficient shifts each COHERENT_SCENARIOS error produces on the gap88 gradient arms, noise-free."""
    arms_88 = [(m, c) for m, c in compiled if m["family"] == "gradient" and m["cost"] in ("gap88", "null")]
    table = cost_table("gap88")
    exact = coefficients(table)
    out = []
    for family, value in COHERENT_SCENARIOS:
        rows = parallel.ordered_map(CoherentLaw(snapshot, device, family, value), arms_88, min_items=1)
        readings = gradient_readings(rows, "gap88")
        fit = phase_fit(table, *readings)
        subtracted = null_subtracted(table, *readings, gradient_readings(rows, "null"))
        out.append(
            {
                "family": family,
                "value": value,
                "coefficient_shift": {k: v - exact[k] for k, v in fit["recovered_coefficients"].items()},
                "max_coefficient_bias": fit["max_coefficient_bias"],
                "cycle_residual_rms": fit["cycle_residual_rms"],
                "min_visibility": min(fit["visibility"]),
                "null_subtracted_coefficient_shift": {
                    k: v - exact[k] for k, v in subtracted["recovered_coefficients"].items()
                },
                "null_subtracted_max_bias": subtracted["max_coefficient_bias"],
            }
        )
    return out


# --------------------------------------------------------------- analysis


def _marginal(law: list[float], bit: int) -> float:
    """<Z> of classical bit ``bit`` under law."""
    return float(sum(p * (1 - 2 * (k >> bit & 1)) for k, p in enumerate(law)))


def incidence() -> np.ndarray:
    """Oriented edge-vertex incidence B: (B E)_e = E(x ^ 2^j) - E(x)."""
    rows = []
    for j, x in edges():
        row = np.zeros(8)
        row[x ^ (1 << j)] += 1.0
        row[x] -= 1.0
        rows.append(row)
    return np.asarray(rows)


def walsh_matrix() -> tuple[list[str], np.ndarray]:
    keys = [k for k in pc.walsh([0] * 8) if k]
    matrix = np.asarray([[(-1) ** sum(x >> int(j) & 1 for j in key) / 8.0 for x in range(8)] for key in keys])
    return keys, matrix


def assignment(rows: list[dict[str, Any]]) -> list[tuple[float, float]]:
    """Per-qubit (p(1|0), p(0|1)) from the three-qubit basis-preparation arms, averaged over the other qubits."""
    reads = [r for r in rows if r["family"] == "readout3"]
    out = []
    for q in range(3):
        flip: dict[int, list[float]] = {0: [], 1: []}
        for r in reads:
            prepared = r["label"] >> q & 1
            flip[prepared].append(sum(p for k, p in enumerate(r["law"]) if (k >> q & 1) != prepared))
        out.append((float(np.mean(flip[0])), float(np.mean(flip[1]))))
    return out


def corrected(z_obs: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """<Z> before an assignment channel with p(1|0) = a, p(0|1) = b: <Z>_obs = (1 - a - b) <Z> + b - a."""
    out: np.ndarray = (z_obs - (b - a)) / (1.0 - a - b)
    return out


def phase_fit(table: list[int], x_read: np.ndarray, y_read: np.ndarray) -> dict[str, Any]:
    """Least-squares cube potential from edge readings, recovered c_S, cycle residual and shot price."""
    exact = coefficients(table)
    visibility = np.hypot(x_read, y_read)
    d_hat = -np.arctan2(y_read, x_read) / GRADIENT_GAMMA
    b = incidence()
    potential, *_ = np.linalg.lstsq(b, d_hat, rcond=None)
    residual = d_hat - b @ potential
    keys, w = walsh_matrix()
    projector = w @ np.linalg.pinv(b)
    recovered = dict(zip(keys, (projector @ d_hat).tolist(), strict=True))
    bias = max(abs(recovered[k] - exact[k]) for k in keys)
    # Delta-method per-shot variance of each edge's d estimate, X and Y arms each taking N shots.
    phase_var = (y_read**2 * (1.0 - x_read**2) + x_read**2 * (1.0 - y_read**2)) / visibility**4
    coeff_var = (projector**2) @ (phase_var / GRADIENT_GAMMA**2)
    margin = IDENTIFY_RADIUS - bias
    return {
        "visibility": visibility.tolist(),
        "d_estimate": d_hat.tolist(),
        "cycle_residual_rms": float(math.sqrt(float(np.mean(residual**2)))),
        "recovered_coefficients": recovered,
        "max_coefficient_bias": bias,
        "per_shot_coefficient_variance": dict(zip(keys, coeff_var.tolist(), strict=True)),
        "shots_identify_all": math.ceil(SIMULTANEOUS_Z**2 * float(coeff_var.max()) / margin**2) if margin > 0 else None,
    }


def gradient_readings(rows: list[dict[str, Any]], name: str) -> tuple[np.ndarray, np.ndarray]:
    got = {
        (r["j"], r["x"], r["basis"]): _marginal(r["law"], r["j"])
        for r in rows
        if r["family"] == "gradient" and r["cost"] == name
    }
    return (
        np.asarray([got[(j, x, "X")] for j, x in edges()]),
        np.asarray([got[(j, x, "Y")] for j, x in edges()]),
    )


def null_subtracted(
    table: list[int], x_read: np.ndarray, y_read: np.ndarray, null: tuple[np.ndarray, np.ndarray]
) -> dict[str, Any]:
    """Phase fit after rotating each edge reading by minus the null arm's phase on the same edge."""
    rotation = np.exp(-1j * np.arctan2(null[1], null[0]))
    turned = (x_read + 1j * y_read) * rotation
    return phase_fit(table, turned.real, turned.imag)


def gradient_analysis(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    """Raw, assignment-corrected and null-subtracted phase fits.

    The corrected bias is the incoherent model's floor; the null-subtracted fit removes every diagonal error the
    zero-angle block shares with the cost block.
    """
    table = cost_table(name)
    x_read, y_read = gradient_readings(rows, name)
    flips = assignment(rows)
    a = np.asarray([flips[j][0] for j, _ in edges()])
    b = np.asarray([flips[j][1] for j, _ in edges()])
    null_x, null_y = gradient_readings(rows, "null")
    return {
        "exact_coefficients": coefficients(table),
        "d_true": (incidence() @ np.asarray(table, dtype=float)).tolist(),
        "raw": phase_fit(table, x_read, y_read),
        "assignment_corrected": phase_fit(table, corrected(x_read, a, b), corrected(y_read, a, b)),
        "null_subtracted": null_subtracted(
            table,
            corrected(x_read, a, b),
            corrected(y_read, a, b),
            (corrected(null_x, a, b), corrected(null_y, a, b)),
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    quotient = [r for r in rows if r["family"] == "quotient"]
    pick = {(r["arm"], r["label"]): r["law"] for r in quotient}
    quotient_cost = [2.0, 2.0, 1.0, 2.0]
    summary: dict[str, Any] = {
        "quotient": {
            "marked_target_probability": [pick[("marked", m)][m] for m in range(4)],
            "wrong_mark_target_probability": [pick[("wrong_mark", m)][m] for m in range(4)],
            "no_oracle_law": pick[("no_oracle", None)],
            "readout_correct": [pick[("readout", m)][m] for m in range(4)],
            "problem_label_mean_cost": float(np.dot(pick[("marked", 2)], quotient_cost)),
            "uniform_mean_cost": float(np.mean(quotient_cost)),
        }
    }
    gradients: dict[str, Any] = {name: gradient_analysis(rows, name) for name in GRADIENT_COSTS}
    plain, fixed = gradients["gap88"], gradients["gap88_repaired"]
    plain, fixed = plain["assignment_corrected"], fixed["assignment_corrected"]
    shift = fixed["recovered_coefficients"]["1"] - plain["recovered_coefficients"]["1"]
    variance = plain["per_shot_coefficient_variance"]["1"] + fixed["per_shot_coefficient_variance"]["1"]
    gradients["gap88_repair_contrast"] = {
        "exact_z1_shift": -0.5,
        "recovered_z1_shift": shift,
        "shots_per_setting_z": math.ceil(Z_SCORE**2 * variance / shift**2),
    }
    gradients["gap86_repair_identical"] = bool(
        all(
            a["law"] == b["law"]
            for a, b in zip(
                [r for r in rows if r["family"] == "gradient" and r["cost"] == "gap86"],
                [r for r in rows if r["family"] == "gradient" and r["cost"] == "gap86_repaired"],
                strict=True,
            )
        )
    )
    summary["gradient"] = gradients
    qaoa = {r["cost"]: r for r in rows if r["family"] == "qaoa"}
    law_a, law_b = np.asarray(qaoa["gap88"]["law"]), np.asarray(qaoa["gap88_repaired"]["law"])
    ideal_a, ideal_b = np.asarray(qaoa["gap88"]["ideal"]), np.asarray(qaoa["gap88_repaired"]["ideal"])
    gap = np.abs(law_a - law_b)
    k = int(np.argmax(gap))
    pooled = law_a[k] * (1 - law_a[k]) + law_b[k] * (1 - law_b[k])
    summary["qaoa"] = {
        "ideal_total_variation": float(0.5 * np.abs(ideal_a - ideal_b).sum()),
        "noisy_total_variation": float(0.5 * gap.sum()),
        "ground_probability": [float(law_a[0]), float(law_b[0])],
        "largest_outcome_difference": {"outcome": k, "difference": float(law_a[k] - law_b[k])},
        "shots_per_arm_largest_outcome": math.ceil(Z_SCORE**2 * pooled / gap[k] ** 2),
    }
    summary["readout3_correct"] = [r["law"][r["label"]] for r in rows if r["family"] == "readout3"]
    return summary


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
        "workers": parallel.workers(),
    }


def evaluate(snapshot: dict[str, Any], device: str) -> dict[str, Any]:
    view = calibration_snapshot.snapshot_backend(snapshot)
    paths = {2: layouts(snapshot, 2), 3: layouts(snapshot, 3)}
    logical = arms()
    out: dict[str, Any] = {"layouts": {str(n): paths[n] for n in paths}, "patches": {}}
    block = QuantumCircuit(3)
    cost_block(block, cost_table("gap88"), GRADIENT_GAMMA)
    duration = transpile(block, view, initial_layout=paths[3]["best"], optimization_level=0).estimate_duration(
        view.target, unit="s"
    )
    # A static detuning delta on qubit j turns its edge phase by 2 pi delta T over the block, a shift of
    # 2 pi delta T / gamma in every d_j(x) and so of half that in c_j; the null arm carries the same shift.
    out["cost_block_seconds"] = float(duration)
    out["single_body_shift_per_khz"] = math.pi * 1e3 * float(duration) / GRADIENT_GAMMA
    for patch in ("best", "median"):
        items = [(meta, c, compile_arm(view, c, paths[c.num_qubits][patch])) for meta, c in logical]
        rows = parallel.ordered_map(ArmLaw(snapshot, device), items, min_items=1)
        out["patches"][patch] = {"rows": rows, "summary": summarize(rows)}
        if patch == "best":
            compiled = [(meta, c) for meta, _, c in items]
            out["coherent_sensitivity"] = coherent_sensitivity(snapshot, device, compiled)
    return out


def run(device: str) -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    started = time.time()
    result = evaluate(snapshot, device)
    return {
        "schema": "gororoba-primorial-cover-noise-v1",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "gradient_gamma_over_pi": "1/9",
        "z_score": Z_SCORE,
        "environment": environment(device),
        "seconds": round(time.time() - started, 1),
        **result,
    }


def bound_to_run(path: Path, run_dir: Path) -> list[str]:
    """FILE must be the byte-identical output that run_dir's collect.json ledger records."""
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    recorded = ledger["files"].get(f"output/repo/{OUTPUT}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if recorded is None:
        return [f"{run_dir}/collect.json records no {OUTPUT}"]
    return [] if digest == recorded else [f"{path} sha256 {digest} differs from the collected {recorded}"]


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row.get(k) for k in ("family", "arm", "label", "cost", "j", "x", "basis"))


def check(path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, run_dir)
    replay = run(calibration_snapshot.aer_device())
    if replay["layouts"] != retained["layouts"]:
        failures.append(f"layouts {replay['layouts']} against {retained['layouts']}")
    for patch, fresh in replay["patches"].items():
        kept = {_key(r): r for r in retained["patches"][patch]["rows"]}
        for row in fresh["rows"]:
            old = kept.get(_key(row))
            if old is None:
                failures.append(f"{patch} {_key(row)} is absent from {path}")
            elif row["cz"] != old["cz"] or not np.allclose(row["law"], old["law"], rtol=1e-8, atol=1e-10):
                failures.append(f"{patch} {_key(row)}: cz {row['cz']} law {row['law']} against {old['law']}")
    for fresh, old in zip(replay["coherent_sensitivity"], retained["coherent_sensitivity"], strict=True):
        if not math.isclose(fresh["max_coefficient_bias"], old["max_coefficient_bias"], rel_tol=1e-8, abs_tol=1e-10):
            failures.append(f"coherent {fresh['family']} {fresh['value']} departs from {path}")
    for failure in failures:
        print(failure)
    print(f"primorial cover noise replay: {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    args = parser.parse_args()
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    result = run(calibration_snapshot.aer_device())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
