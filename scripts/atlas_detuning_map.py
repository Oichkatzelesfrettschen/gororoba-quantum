"""Fit per-qubit idle detunings to the ripple atlas fringe phases on ibm_fez.

The atlas ran each of the 84 box-kite edges as an 8-point phase sweep
(designs.design_d_phase_sweep, phase k pi/4) on one of 7 lanes, every lane a
fixed set of 5 physical qubits shared by its 12 edges
(results/ripple/measured-ripple.json). Fitting a + b cos(phi - phi0) to each
edge's 8 points gives a fringe phase; the hardware fringe phases sit
+0.13 rad from the ideal on average (spread 0.22 rad), while the calibrated
execution replay, whose noise model has no coherent term, sits within 0.06
rad of it. A frame detuning delta_q on qubit q is coherent: it adds
RZ(2 pi delta_q tau) over every interval tau the qubit spends in the scheduled
circuit, and moves the fringe phase.

For every edge this script compiles the circuit onto its lane's 5-qubit
sub-target of ibm_fez (coupling, gate durations and dt from
docs/evidence/heron_platform/targets.json; the snapshot postdates the run by
two days, and gate durations are fixed by the calibrated pulse shapes),
schedules it as late as possible, inserts those rotations and simulates the
5-qubit statevector. The response of each edge's fringe phase to a 1 kHz
detuning on each lane qubit forms a 12 x 5 matrix per lane; least squares on
the measured offsets (hardware minus replay fringe phase) gives the lane's
detunings. Each fit reports its residual, its leave-one-edge-out prediction
error and the error of predicting every edge by the lane mean, so a map that
only fits noise loses to the mean.

``--lanes all`` runs the 7 lanes; ``--lanes 0`` one. ``--check FILE`` reruns
the lanes FILE names and requires every response to agree to 1e-9 and every
fitted parameter to 1e-6, since the computation is deterministic statevector
algebra.

Four models compete per lane by leave-one-edge-out error: the lane mean, the
5 detunings, a CPhase(epsilon_c) error after every CZ on each lane coupler
c, and both together. Each lane also reports the shot-noise floor of its
measured offsets, the binomial variance of the 8 points propagated through
the fringe fit, so no model is credited below it.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit import Delay, Parameter  # noqa: E402
from qiskit.circuit.library import CZGate, Measure, RZGate, SXGate, XGate  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402
from qiskit.transpiler import InstructionProperties, Target  # noqa: E402

from designs import design_d_phase_sweep  # noqa: E402
from ripple_dynamics import box_kites  # noqa: E402

MEASURED = ROOT / "results/ripple/measured-ripple.json"
TARGETS = ROOT / "docs/evidence/heron_platform/targets.json"
BACKEND = "ibm_fez"
PHASES = 8
SEED = 11
KHZ = 1e3
MEMBER = re.compile(r"ripple_atlas_lane(\d+)_kite(\d+)_edge(\d+)_(\d+)_phase(\d)_atlas$")


def fringe(points: list[float]) -> tuple[float, float]:
    """Amplitude and phase of a + b cos(phi - phi0) through 8 equally spaced points."""
    phi = np.arange(PHASES) * math.pi / 4
    design = np.column_stack([np.ones(PHASES), np.cos(phi), np.sin(phi)])
    _, c, s = np.linalg.lstsq(design, np.array(points), rcond=None)[0]
    return math.hypot(c, s), math.atan2(s, c)


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def measured_edges() -> dict[int, list[dict[str, Any]]]:
    data = json.loads(MEASURED.read_text(encoding="utf-8"))
    points: dict[tuple[int, int, int, int], dict[int, Any]] = defaultdict(dict)
    layouts: dict[tuple[int, int, int, int], list[int]] = {}
    for name, member in data["members"].items():
        match = MEMBER.match(name)
        if match is None:
            continue
        lane, kite, source, target, phase = (int(group) for group in match.groups())
        counts = member["counts"]
        points[lane, kite, source, target][phase] = (
            counts[0] / sum(counts),
            sum(counts),
            member["execution_replay"]["probabilities"][0],
            member["ideal_probabilities"][0],
        )
        layouts[lane, kite, source, target] = list(member["physical_qubits"])
    lanes: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for key in sorted(points):
        series = [points[key][phase] for phase in range(PHASES)]
        amplitude, hardware = fringe([p[0] for p in series])
        _, replay = fringe([p[2] for p in series])
        _, ideal = fringe([p[3] for p in series])
        # Binomial variance of each point through the 3-parameter fit: the cosine
        # and sine coefficients each carry 2/PHASES of the mean point variance.
        variance = float(np.mean([p[0] * (1 - p[0]) / p[1] for p in series])) * 2 / PHASES
        lanes[key[0]].append(
            {
                "kite": key[1],
                "source": key[2],
                "target": key[3],
                "physical_qubits": layouts[key],
                "hardware_offset": wrap(hardware - ideal),
                "replay_offset": wrap(replay - ideal),
                "shot_noise_rad": math.sqrt(variance) / amplitude,
            }
        )
    return lanes


def lane_target(physical: list[int]) -> Target:
    """The 5-qubit sub-target of BACKEND on these physical qubits, in this order."""
    backend = json.loads(TARGETS.read_text(encoding="utf-8"))["backends"][BACKEND]
    index = {q: k for k, q in enumerate(physical)}
    target = Target(num_qubits=len(physical), dt=backend["dt"])

    def rows(name: str, width: int) -> dict[tuple[int, ...], InstructionProperties]:
        out = {}
        for qargs, duration in zip(
            backend["instructions"][name]["qargs"], backend["instructions"][name]["duration"], strict=True
        ):
            if len(qargs) == width and all(q in index for q in qargs):
                out[tuple(index[q] for q in qargs)] = InstructionProperties(duration=duration)
        return out

    target.add_instruction(CZGate(), rows("cz", 2))
    target.add_instruction(SXGate(), rows("sx", 1))
    target.add_instruction(XGate(), rows("x", 1))
    target.add_instruction(Measure(), rows("measure", 1))
    target.add_instruction(
        RZGate(Parameter("theta")), {(k,): InstructionProperties(duration=0.0) for k in range(len(physical))}
    )
    target.add_instruction(Delay(Parameter("t")), {(k,): None for k in range(len(physical))})
    return target


def vertex_pairs() -> dict[tuple[int, int], tuple[int, int]]:
    graphs, _, _ = box_kites()
    return {(g["id"], v["id"]): (v["low"], v["high"]) for g in graphs for v in g["vertices"]}


def scheduled(edge: dict[str, Any], phase: float, target: Target, pairs: dict[Any, Any]) -> tuple[QuantumCircuit, int]:
    kite_constant = edge["kite"]
    circuit = design_d_phase_sweep(pairs[kite_constant, edge["source"]], pairs[kite_constant, edge["target"]], phase)
    compiled = transpile(
        circuit,
        target=target,
        initial_layout=list(range(5)),
        optimization_level=1,
        seed_transpiler=SEED,
        scheduling_method="alap",
    )
    selector = compiled.layout.final_index_layout()[4] if compiled.layout else 4
    return compiled, selector


def detuned_probability(
    compiled: QuantumCircuit,
    selector: int,
    target: Target,
    detuning_hz: list[float],
    cz_phase: dict[tuple[int, int], float] | None = None,
) -> float:
    """P(selector reads 0) with RZ(2 pi delta_q tau) after every timed interval on qubit q
    and CPhase(epsilon_c) after every CZ on coupler c."""
    dt = target.dt
    out = QuantumCircuit(compiled.num_qubits)
    for instruction in compiled.data:
        name = instruction.operation.name
        if name in ("measure", "barrier"):
            continue
        qubits = [compiled.find_bit(q).index for q in instruction.qubits]
        out.append(instruction.operation, qubits)
        if name == "delay":
            seconds = instruction.operation.duration * dt
        elif name == "rz":
            continue
        else:
            seconds = target[name][tuple(qubits)].duration or 0.0
        for q in qubits:
            if detuning_hz[q]:
                out.rz(2 * math.pi * detuning_hz[q] * seconds, q)
        if name == "cz" and cz_phase:
            epsilon = cz_phase.get(tuple(sorted(qubits)), 0.0)
            if epsilon:
                out.cp(epsilon, qubits[0], qubits[1])
    return float(Statevector(out).probabilities([selector])[0])


CZ_STEP = 0.01


def lane_fit(lane: int, edges: list[dict[str, Any]], pairs: dict[Any, Any]) -> dict[str, Any]:
    physical = edges[0]["physical_qubits"]
    target = lane_target(physical)
    couplers = sorted({tuple(sorted(qargs)) for qargs in target["cz"]})
    detuning_response = np.zeros((len(edges), 5))
    coupler_response = np.zeros((len(edges), len(couplers)))
    compiled_cz = []
    for e, edge in enumerate(edges):
        circuits = [scheduled(edge, k * math.pi / 4, target, pairs) for k in range(PHASES)]
        compiled_cz.append(int(circuits[0][0].count_ops().get("cz", 0)))
        base = fringe([detuned_probability(c, s, target, [0.0] * 5) for c, s in circuits])[1]
        for q in range(5):
            shift = [0.0] * 5
            shift[q] = KHZ
            moved = fringe([detuned_probability(c, s, target, shift) for c, s in circuits])[1]
            detuning_response[e, q] = wrap(moved - base)
        for k, coupler in enumerate(couplers):
            moved = fringe([detuned_probability(c, s, target, [0.0] * 5, {coupler: CZ_STEP}) for c, s in circuits])[1]
            coupler_response[e, k] = wrap(moved - base) / CZ_STEP
    measured = np.array([edge["hardware_offset"] - edge["replay_offset"] for edge in edges])
    noise = np.array([edge["shot_noise_rad"] for edge in edges])

    def rms(values: Any) -> float:
        return float(math.sqrt(np.mean(np.square(values))))

    def evaluate(design: np.ndarray) -> dict[str, Any]:
        parameters, *_ = np.linalg.lstsq(design, measured, rcond=None)
        loo = []
        for held in range(len(edges)):
            keep = [k for k in range(len(edges)) if k != held]
            fit, *_ = np.linalg.lstsq(design[keep], measured[keep], rcond=None)
            loo.append(measured[held] - design[held] @ fit)
        return {
            "parameters": [round(float(v), 6) for v in parameters],
            "fit_rms_rad": round(rms(measured - design @ parameters), 6),
            "leave_one_out_rms_rad": round(rms(loo), 6),
        }

    ones = np.ones((len(edges), 1))
    models = {
        "lane_mean": evaluate(ones),
        "detuning": evaluate(detuning_response),
        "cz_phase": evaluate(coupler_response),
        "detuning_and_cz_phase": evaluate(np.hstack([detuning_response, coupler_response])),
    }
    return {
        "lane": lane,
        "physical_qubits": physical,
        "couplers": [[physical[a], physical[b]] for a, b in couplers],
        "detuning_response_rad_per_khz": [[round(float(v), 9) for v in row] for row in detuning_response],
        "cz_phase_response_rad_per_rad": [[round(float(v), 9) for v in row] for row in coupler_response],
        "measured_offset_rad": [round(float(v), 6) for v in measured],
        "shot_noise_rms_rad": round(rms(noise), 6),
        "compiled_cz": compiled_cz,
        "models": models,
        "edges": [{k: edge[k] for k in ("kite", "source", "target")} for edge in edges],
    }


def run(lanes: list[int]) -> dict[str, Any]:
    edges = measured_edges()
    pairs = vertex_pairs()
    fits = [lane_fit(lane, edges[lane], pairs) for lane in lanes]
    for fit in fits:
        summary = {name: model["leave_one_out_rms_rad"] for name, model in fit["models"].items()}
        line = {"lane": fit["lane"], "shot_noise_rms_rad": fit["shot_noise_rms_rad"], "loo": summary}
        print(json.dumps(line), flush=True)
    return {"schema": "atlas-detuning-map-v1", "backend": BACKEND, "phases": PHASES, "lanes": fits}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lanes", default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        named = [fit["lane"] for fit in retained["lanes"]]
        lanes = named if args.lanes == "all" else [int(v) for v in args.lanes.split(",")]
        fresh = {fit["lane"]: fit for fit in run(lanes)["lanes"]}
        for fit in retained["lanes"]:
            if fit["lane"] not in fresh:
                continue
            other = fresh[fit["lane"]]
            for key in ("measured_offset_rad", "detuning_response_rad_per_khz", "cz_phase_response_rad_per_rad"):
                if not np.allclose(fit[key], other[key], atol=1e-9):
                    raise SystemExit(f"lane {fit['lane']}: {key} differs from a fresh computation")
            for name, model in fit["models"].items():
                if not np.allclose(model["parameters"], other["models"][name]["parameters"], atol=1e-6):
                    raise SystemExit(f"lane {fit['lane']}: {name} parameters differ")
        print(f"{args.check}: lanes {lanes} reproduced")
        return 0
    if args.out is None:
        parser.error("--out is required")
    lanes = list(range(7)) if args.lanes == "all" else [int(v) for v in args.lanes.split(",")]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(run(lanes), indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
