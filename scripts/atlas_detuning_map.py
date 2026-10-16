"""Fit coherent frame and CZ-phase errors to the Fez ripple atlas fringes, on the circuits and times that ran.

The atlas ran each of the 84 box-kite edges as an 8-point phase sweep
(phase k pi/4) on one of 7 lanes, each lane a fixed set of 5 physical
qubits shared by its 12 edges (results/ripple/measured-ripple.json). Fitting
a + b cos(phi - phi0) to each edge's 8 measured points gives a fringe phase;
the hardware fringe phases sit about +0.13 rad from the ideal with a 0.22
rad spread, while the calibrated execution replay, whose noise model has no
coherent term, sits within 0.06 rad of it.

Every quantity here comes from the run itself:

- the circuit of each phase point is the executed replica, rebuilt from
  isa.qpy as live_run.collect does (packing.extract on the member's fused-PUB
  component, packing.split on its replica);
- the time of each pulse is the hardware's executed schedule, the
  ``scheduler_timing`` table IBM returned with the PUB
  (raw/<job>/pub_NN.json): each qubit's play rows, in start order, pair one
  to one with the replica's non-virtual instructions on that qubit.

A frame detuning delta_q on qubit q enters as RZ(2 pi delta_q (t_i - t_{i-1}))
before each executed pulse i on q, where t is the pulse start in seconds; a
CZ phase error epsilon_c enters as CPhase(epsilon_c) after every CZ on
coupler c. For every edge the script simulates the 8 replicas, compacted to
their active qubits, and differentiates the fringe phase by a 1 kHz detuning
per lane qubit and a 0.01 rad CPhase per lane coupler. Four models per lane
(lane mean, detunings, CZ phases, both) are compared by leave-one-edge-out
RMS error against the shot-noise floor, the binomial variance of the 8
points propagated through the fringe fit.

Self-check: with no error term each edge's simulated fringe phase must equal
the fringe phase of the recorded ideal probabilities within 1e-9 rad, so the
extraction and timing pairing preserve the circuit.

``--lanes all`` or ``--lanes 0,4``. ``--check FILE`` reruns the named lanes on
the CPU and requires every response to 1e-9 and every fitted parameter to
1e-6, since the computation is deterministic statevector algebra.
"""

from __future__ import annotations

import argparse
import io
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
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

import packing  # noqa: E402

RUN = ROOT / "results/live/2026-10-13T025444.603480Z"
MEASURED = ROOT / "results/ripple/measured-ripple.json"
TARGETS = ROOT / "docs/evidence/heron_platform/targets.json"
BACKEND = "ibm_fez"
PHASES = 8
KHZ = 1e3
CZ_STEP = 0.01
VIRTUAL = {"rz", "barrier", "delay"}
MEMBER = re.compile(r"ripple_atlas_lane(\d+)_kite(\d+)_edge(\d+)_(\d+)_phase(\d)_atlas$")
Timed = tuple[QuantumCircuit, list[float], int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def fringe(points: list[float]) -> tuple[float, float]:
    """Amplitude and phase of a + b cos(phi - phi0) through 8 equally spaced points."""
    phi = np.arange(PHASES) * math.pi / 4
    design = np.column_stack([np.ones(PHASES), np.cos(phi), np.sin(phi)])
    _, c, s = np.linalg.lstsq(design, np.array(points), rcond=None)[0]
    return math.hypot(c, s), math.atan2(s, c)


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


class Executed:
    """The run's archived circuits, its executed schedules, and its member map."""

    def __init__(self) -> None:
        record = json.loads((RUN / "record.json").read_text(encoding="utf-8"))
        self.isas = {c.name: c for c in qpy.load(io.BytesIO((RUN / "isa.qpy").read_bytes()))}
        self.components: dict[str, tuple[str, dict[str, Any]]] = {}
        for job in record["submission"]["planned_jobs"]:
            for pub in job["pubs"]:
                for component in pub["components"]:
                    self.components[component["member"]] = (pub["name"], component)
        self.members = {m["name"]: m for g in record["groups"] for m in g["members"]}
        self.timing: dict[str, list[list[str]]] = {}
        for path in sorted(RUN.glob("raw/*/pub_*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            table = data["metadata"]["compilation"]["scheduler_timing"]["timing"]
            self.timing[data["pub_name"]] = [row.split(",") for row in table.splitlines()]
        self.dt = float(json.loads(TARGETS.read_text(encoding="utf-8"))["backends"][BACKEND]["dt"])

    def replica(self, name: str) -> tuple[QuantumCircuit, list[list[str]]]:
        pub_name, component = self.components[name]
        member = self.members[name]
        qubits = sorted({q for replica in member["replica_qubits"] for q in replica})
        packed = packing.extract(self.isas[pub_name], component["register_prefix"], qubits, name)
        prefix = component["register_prefix"] + member["replica_prefixes"][0]
        return packing.split(packed, prefix, member["replica_qubits"][0], name), self.timing[pub_name]

    def physical(self, name: str) -> list[int]:
        return list(self.members[name]["replica_qubits"][0])


def timed_compact(circuit: QuantumCircuit, rows: list[list[str]], dt: float) -> Timed:
    """The replica on its active qubits, each instruction's executed start (nan if virtual), and the measured qubit."""
    active = sorted({circuit.find_bit(q).index for inst in circuit.data for q in inst.qubits})
    index = {q: k for k, q in enumerate(active)}
    plays: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        if row[5] != "play" or row[1].startswith(("INIT", "FINI")) or not row[2].startswith("Qubit "):
            continue
        qubit = int(row[2].split()[1])
        if qubit in index:
            plays[qubit].append((int(row[3]), row[1].split("_")[0]))
    for qubit in plays:
        plays[qubit].sort()
    cursor: dict[int, int] = defaultdict(int)
    compact = QuantumCircuit(len(active))
    starts: list[float] = []
    measured = -1
    for inst in circuit.data:
        name = inst.operation.name
        qubits = [circuit.find_bit(q).index for q in inst.qubits]
        if name in VIRTUAL:
            if name == "rz":
                compact.append(inst.operation, [index[q] for q in qubits])
                starts.append(math.nan)
            continue
        times = []
        for q in qubits:
            start, label = plays[q][cursor[q]]
            require(label == name, f"qubit {q}: executed {label} where the circuit has {name}")
            cursor[q] += 1
            times.append(start)
        require(len(set(times)) == 1, f"{name} on {qubits} starts at different times {times}")
        if name == "measure":
            measured = index[qubits[0]]
            continue
        compact.append(inst.operation, [index[q] for q in qubits])
        starts.append(times[0] * dt)
    require(all(cursor[q] == len(plays[q]) for q in plays), "executed pulses remain unpaired")
    require(measured >= 0, "replica has no measurement")
    return compact, starts, measured


def probability(timed: Timed, detuning_hz: list[float], cz_phase: dict[tuple[int, int], float]) -> float:
    """P(measured qubit reads 0) with frame rotations from executed times and CPhase after each CZ."""
    compact, starts, measured = timed
    out = QuantumCircuit(compact.num_qubits)
    last: dict[int, float] = {}
    for inst, start in zip(compact.data, starts, strict=True):
        qubits = [compact.find_bit(q).index for q in inst.qubits]
        if not math.isnan(start):
            for q in qubits:
                if q in last and detuning_hz[q]:
                    out.rz(2 * math.pi * detuning_hz[q] * (start - last[q]), q)
                last[q] = start
        out.append(inst.operation, qubits)
        if inst.operation.name == "cz":
            epsilon = cz_phase.get((min(qubits), max(qubits)), 0.0)
            if epsilon:
                out.cp(epsilon, qubits[0], qubits[1])
    return float(Statevector(out).probabilities([measured])[0])


def measured_edges() -> dict[int, list[dict[str, Any]]]:
    data = json.loads(MEASURED.read_text(encoding="utf-8"))
    points: dict[tuple[int, int, int, int], dict[int, Any]] = defaultdict(dict)
    for name, member in data["members"].items():
        match = MEMBER.match(name)
        if match is None:
            continue
        lane, kite, source, target, phase = (int(group) for group in match.groups())
        counts = member["counts"]
        points[lane, kite, source, target][phase] = (
            name,
            counts[0] / sum(counts),
            sum(counts),
            member["execution_replay"]["probabilities"][0],
            member["ideal_probabilities"][0],
        )
    lanes: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for key in sorted(points):
        series = [points[key][phase] for phase in range(PHASES)]
        amplitude, hardware = fringe([p[1] for p in series])
        _, replay = fringe([p[3] for p in series])
        _, ideal = fringe([p[4] for p in series])
        variance = float(np.mean([p[1] * (1 - p[1]) / p[2] for p in series])) * 2 / PHASES
        lanes[key[0]].append(
            {
                "kite": key[1],
                "source": key[2],
                "target": key[3],
                "members": [p[0] for p in series],
                "ideal_phase": ideal,
                "offset": wrap(hardware - replay),
                "shot_noise_rad": math.sqrt(variance) / amplitude,
            }
        )
    return lanes


def lane_fit(lane: int, edges: list[dict[str, Any]], executed: Executed) -> dict[str, Any]:
    prepared = [[timed_compact(*executed.replica(name), executed.dt) for name in edge["members"]] for edge in edges]
    physical = sorted({q for edge in edges for name in edge["members"] for q in executed.physical(name)})
    require(len(physical) == 5, f"lane {lane} spans {len(physical)} qubits")
    width = prepared[0][0][0].num_qubits
    couplers: set[tuple[int, int]] = set()
    for points in prepared:
        for compact, _, _ in points:
            for inst in compact.data:
                if inst.operation.name == "cz":
                    pair = [compact.find_bit(q).index for q in inst.qubits]
                    couplers.add((min(pair), max(pair)))
    ordered = sorted(couplers)

    def phase(points: list[Timed], detuning: list[float], cz: dict[tuple[int, int], float]) -> float:
        return fringe([probability(timed, detuning, cz) for timed in points])[1]

    zero = [0.0] * width
    detuning_response = np.zeros((len(edges), width))
    coupler_response = np.zeros((len(edges), len(ordered)))
    ideal_mismatch = 0.0
    for e, points in enumerate(prepared):
        base = phase(points, zero, {})
        ideal_mismatch = max(ideal_mismatch, abs(wrap(base - edges[e]["ideal_phase"])))
        for q in range(width):
            shift = list(zero)
            shift[q] = KHZ
            detuning_response[e, q] = wrap(phase(points, shift, {}) - base)
        for k, coupler in enumerate(ordered):
            coupler_response[e, k] = wrap(phase(points, zero, {coupler: CZ_STEP}) - base) / CZ_STEP
    require(ideal_mismatch < 1e-9, f"lane {lane}: executed replicas miss the ideal fringe by {ideal_mismatch:.2e} rad")
    measured = np.array([edge["offset"] for edge in edges])
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

    models = {
        "lane_mean": evaluate(np.ones((len(edges), 1))),
        "detuning": evaluate(detuning_response),
        "cz_phase": evaluate(coupler_response),
        "detuning_and_cz_phase": evaluate(np.hstack([detuning_response, coupler_response])),
    }
    return {
        "lane": lane,
        "physical_qubits": physical,
        "couplers_compact": [list(c) for c in ordered],
        "executed_cz": [int(points[0][0].count_ops().get("cz", 0)) for points in prepared],
        "ideal_mismatch_rad": ideal_mismatch,
        "detuning_response_rad_per_khz": [[round(float(v), 9) for v in row] for row in detuning_response],
        "cz_phase_response_rad_per_rad": [[round(float(v), 9) for v in row] for row in coupler_response],
        "measured_offset_rad": [round(float(v), 6) for v in measured],
        "shot_noise_rms_rad": round(rms(noise), 6),
        "models": models,
        "edges": [{k: edge[k] for k in ("kite", "source", "target")} for edge in edges],
    }


def run(lanes: list[int]) -> dict[str, Any]:
    edges = measured_edges()
    executed = Executed()
    fits = [lane_fit(lane, edges[lane], executed) for lane in lanes]
    for fit in fits:
        summary = {name: model["leave_one_out_rms_rad"] for name, model in fit["models"].items()}
        line = {"lane": fit["lane"], "shot_noise_rms_rad": fit["shot_noise_rms_rad"], "loo": summary}
        print(json.dumps(line), flush=True)
    return {
        "schema": "atlas-detuning-map-v2",
        "backend": BACKEND,
        "run": RUN.relative_to(ROOT).as_posix(),
        "phases": PHASES,
        "lanes": fits,
    }


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
                require(np.allclose(fit[key], other[key], rtol=0, atol=1e-9), f"lane {fit['lane']}: {key} differs")
            for name, model in fit["models"].items():
                require(
                    np.allclose(model["parameters"], other["models"][name]["parameters"], rtol=0, atol=1e-6),
                    f"lane {fit['lane']}: {name} parameters differ",
                )
        print(f"{args.check}: lanes {lanes} reproduced")
        return 0
    require(args.out is not None, "--out is required")
    lanes = list(range(7)) if args.lanes == "all" else [int(v) for v in args.lanes.split(",")]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(run(lanes), indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
