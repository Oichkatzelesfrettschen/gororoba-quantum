"""Which loss channel reproduces the walk readout0 floors: fit on readout0, predict the depth members.

Every ripple walk member executes the same 252-CZ scaffold on its lane's four
qubits; readout0 is identity-equivalent, and the depth members bind angles
that implement the walk of a sedenion associator sign pattern
(ripple_experiments._walk_ideal over predict.associator_phase(32, i, j)).
docs/evidence/walk-control-scaffolding/README.md records that the hardware
readout0 floor (P(0000) 0.064 to 0.336) sits far below the calibrated replay
(0.540 to 0.666) and that the loss is structured, not depolarizing. This
script asks which single extra channel, added to live_run's calibrated noise
model, reproduces it.

Data: the walk members of the Fez ripple run 2026-10-13T025444.603480Z and
the Kingston run 2026-10-15T031229.371738Z, four lanes of 14 members each.
Each member is extracted from its fused PUB (packing.split), moved onto its
four qubits, scheduled as late as possible against the Target durations of
the calibration it executed under (docs/evidence/calibration/history/,
matched by the member's execution calibration), and simulated with
snapshot_laws' restricted noise. Its hardware law (1024 shots) is the count
vector the collection retains.

Candidates, each added to the scheduled calibrated model with one parameter
per qubit (per CZ edge for the conditional phase):

- end_flip: a 0 -> 1 flip of each qubit before readout, which a hidden
  readout fault and leakage read as 1 both produce;
- sx_overrotation: RX(eps_q) after every SX on qubit q;
- cz_local_phase: RZ(zeta_q) on each qubit after every CZ it joins;
- cz_conditional_phase: CP(phi_e) after every CZ on edge e;
- extra_damping: amplitude damping gamma_q after every CZ on its qubits;
- extra_depolarizing: depolarizing p_q after every CZ on its qubits.

Inserted operations carry no duration and no calibrated noise of their own,
and the model with every parameter at zero reproduces the scheduled baseline
exactly. Each candidate is fitted to the lane's readout0 counts by maximum
likelihood (a seeded global search for the coherent candidates, L-BFGS-B
from FIT_STARTS for the others), then frozen and scored
on the lane's 13 other members (readout1 and the depth members).

Preregistered reading: a candidate passes the readout0 gate when its
deviance G^2 against the saturated law has p >= 0.01, and it reproduces the
floor only when its frozen parameters also predict the held-out members with
G^2 p >= 0.01 and a higher held-out likelihood than the scheduled baseline.

Algebra: every member's noiseless law must equal its cd_core ideal
(_walk_ideal for depth members, the point mass for the readout controls),
and the dim-32 products the two walk pairs' associator patterns use are
recomputed (80 distinct products) with the pinned python-hypercomplex (exact Fraction coefficients)
and python-hypercomplex-engine under their declared identity map onto
cd_core; the run fails on any difference.

Laws, fits and scores run through parallel.ordered_map. The entry reads
GOROROBA_AER_DEVICE (CPU by default). ``--check FILE --run DIR`` binds FILE
to the Kaggle run's collect.json digest, recomputes the cd_core side of the
algebra record without importing any package, re-derives Kingston lane 0's
baseline and fitted laws of all 14 members to 1e-8 with the held-out
log-likelihood, deviance and reproduces_floor decision, and requires each
recorded optimum to be a local minimum: no single parameter moved by
PROBE_STEP of its bound width, in either direction the bounds allow,
raises the readout0 log-likelihood by more than 1e-3.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import re
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.circuit.library import CPhaseGate, RXGate, RZGate, UnitaryGate  # noqa: E402
from qiskit.transpiler import PassManager  # noqa: E402
from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDelay  # noqa: E402
from qiskit_aer.noise import amplitude_damping_error, depolarizing_error  # noqa: E402
from scipy import optimize, stats  # noqa: E402

import calibration_snapshot  # noqa: E402
import packing  # noqa: E402
import parallel  # noqa: E402
import predict  # noqa: E402
import snapshot_laws  # noqa: E402
from cd_core import cd_sign  # noqa: E402
from ripple_dynamics import PAIRS  # noqa: E402
from ripple_experiments import _walk_ideal  # noqa: E402

OUTPUT = "results/kaggle_out/walk_scaffold_channels.json"
EVIDENCE = ROOT / "docs/evidence/walk_scaffold_channels"
EXTRACT_JSON = EVIDENCE / "members.json"
EXTRACT_QPY = EVIDENCE / "members.qpy"
HISTORY = ROOT / "docs/evidence/calibration/history"
RUNS = ("results/live/2026-10-13T025444.603480Z", "results/live/2026-10-15T031229.371738Z")
FIT_MEMBER = "readout0"
DIM = 32
# name -> (parameters per qubit or per edge, lower bound, upper bound)
CHANNELS: dict[str, tuple[str, float, float]] = {
    "end_flip": ("qubit", 0.0, 0.5),
    "sx_overrotation": ("qubit", -0.15, 0.15),
    "cz_local_phase": ("qubit", -0.15, 0.15),
    "cz_conditional_phase": ("edge", -0.15, 0.15),
    "extra_damping": ("qubit", 0.0, 0.2),
    "extra_depolarizing": ("qubit", 0.0, 0.2),
}
# A coherent per-gate angle error delta costs about delta^2 / 4 of gate
# infidelity, so the calibrated CZ and SX errors near 2e-3 and 3e-4 put
# |delta| near 0.09 and 0.035 rad; the coherent bounds of 0.15 rad leave room
# above both. The coherent likelihood winds with the angle accumulated over
# about 100 gates per qubit, so those candidates take a seeded global search
# (differential evolution from a Sobol population, polished by L-BFGS-B);
# the incoherent candidates start L-BFGS-B at fixed fractions of the bound.
FIT_STARTS = {"positive": ((0.05, 0.05, 0.05, 0.05), (0.3, 0.3, 0.3, 0.3))}
PROBE_STEP = 1e-3
GLOBAL_SEARCH = {"seed": 20261016, "popsize": 10, "maxiter": 60, "init": "sobol", "tol": 1e-6}
GATE_P = 0.01


def snapshot_files() -> dict[str, Path]:
    """Execution calibration string -> retained snapshot file."""
    out = {}
    for path in sorted(HISTORY.glob("*/*.json")):
        out[json.loads(path.read_text(encoding="utf-8"))["calibration"]] = path
    return out


def member_role(name: str) -> tuple[str, tuple[int, int] | None, int | None]:
    match = re.fullmatch(r"ripple_walk_lane\d+_pair(\d+)_(\d+)_depth(\d+)_\w+", name)
    if match:
        return "depth", (int(match[1]), int(match[2])), int(match[3])
    match = re.fullmatch(r"ripple_walk_lane\d+_(readout[01])", name)
    if match:
        return match[1], None, None
    raise ValueError(f"unrecognized walk member {name}")


def ideal_law(name: str) -> np.ndarray:
    role, pair, depth = member_role(name)
    if role == "depth":
        assert pair is not None and depth is not None
        return _walk_ideal(pair, depth)
    law = np.zeros(16)
    law[0 if role == "readout0" else 15] = 1.0
    return law


def local_circuit(component: QuantumCircuit) -> tuple[QuantumCircuit, list[int]]:
    """The component on its own qubits (ascending physical order), barriers and measures kept.

    The walk template's layer barriers hold every qubit until its layer ends,
    so ALAP scheduling keeps them to reproduce the executed idles.
    """
    qubits = snapshot_laws.active_qubits(component)
    index = {q: k for k, q in enumerate(qubits)}
    out = QuantumCircuit(len(qubits), component.num_clbits)
    for instruction in component.data:
        out.append(
            instruction.operation,
            [index[component.find_bit(q).index] for q in instruction.qubits],
            [component.find_bit(b).index for b in instruction.clbits],
        )
    return out, qubits


def extract_lanes() -> list[dict[str, Any]]:
    """Every walk member of both runs, grouped by lane, with its circuit, counts and snapshot."""
    files = snapshot_files()
    lanes: dict[tuple[str, str], dict[str, Any]] = {}
    for run in RUNS:
        record = json.loads((ROOT / run / "record.json").read_text(encoding="utf-8"))
        measurements: dict[str, Any] = {}
        for group in json.loads((ROOT / run / "collect.json").read_text(encoding="utf-8")):
            measurements.update(group.get("family_measurements", {}))
        with (ROOT / run / "isa.qpy").open("rb") as stream:
            circuits = qpy.load(stream)
        backend = record["groups"][0]["backend"]
        for circuit, pub in zip(circuits, record["execution_pubs"], strict=True):
            for component in pub["components"]:
                name = component["member"]
                if not name.startswith("ripple_walk"):
                    continue
                lane = re.match(r"ripple_walk_(lane\d+)_", name)
                assert lane is not None
                measured = measurements[name]
                execution = measured["execution"]
                if execution["calibration_changed_during_shots"]:
                    raise SystemExit(f"{run} {name}: calibration changed during the shots")
                shots = int(execution["shots"])
                law = np.asarray(measured["replica_probabilities"][0])
                counts = np.rint(law * shots)
                if np.max(np.abs(counts - law * shots)) > 1e-6:
                    raise SystemExit(f"{run} {name}: probabilities are not whole counts of {shots}")
                part = packing.split(circuit, component["register_prefix"] + "r0_", component["physical_qubits"], name)
                small, qubits = local_circuit(part)
                entry = lanes.setdefault(
                    (run, lane[1]), {"run": run, "backend": backend, "lane": lane[1], "qubits": qubits, "members": {}}
                )
                if entry["qubits"] != qubits:
                    raise SystemExit(f"{run} {name}: lane qubits {qubits} differ from {entry['qubits']}")
                entry["members"][name] = {
                    "circuit": small,
                    "counts": counts.astype(int).tolist(),
                    "shots": shots,
                    "replay": measured["replayed_replica_probabilities"][0],
                    "snapshot": str(files[execution["calibration"]].relative_to(ROOT)),
                }
    return [lanes[key] for key in sorted(lanes)]


def write_extract(json_path: Path, qpy_path: Path) -> None:
    """The walk members as a compact extract: lane metadata in JSON, local circuits in QPY order.

    The retained runs carry about 77 MB of record, collection and QPY; the
    extract holds only what the fits read, with the sha256 of every source
    file, so a kernel bundle stays small and the replay gate re-derives the
    extract byte for byte from the retained runs.
    """
    lanes = extract_lanes()
    circuits: list[QuantumCircuit] = []
    meta = []
    for lane in lanes:
        members = {}
        for name, entry in lane["members"].items():
            members[name] = {key: value for key, value in entry.items() if key != "circuit"} | {
                "qpy_index": len(circuits)
            }
            circuits.append(entry["circuit"])
        meta.append({key: value for key, value in lane.items() if key != "members"} | {"members": members})
    sources = {
        f"{run}/{name}": hashlib.sha256((ROOT / run / name).read_bytes()).hexdigest()
        for run in RUNS
        for name in ("record.json", "collect.json", "isa.qpy")
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps({"schema": "walk-scaffold-members-v1", "sources": sources, "lanes": meta}, indent=1, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    with qpy_path.open("wb") as stream:
        qpy.dump(circuits, stream)


def load_lanes() -> list[dict[str, Any]]:
    """The lanes from the retained extract (EXTRACT_JSON and EXTRACT_QPY)."""
    data = json.loads(EXTRACT_JSON.read_text(encoding="utf-8"))
    with EXTRACT_QPY.open("rb") as stream:
        circuits = qpy.load(stream)
    lanes = []
    for lane in data["lanes"]:
        members = {
            name: {key: value for key, value in entry.items() if key != "qpy_index"}
            | {"circuit": circuits[entry["qpy_index"]]}
            for name, entry in lane["members"].items()
        }
        lanes.append(lane | {"members": members})
    return lanes


def schedule(circuit: QuantumCircuit, snapshot: dict[str, Any]) -> QuantumCircuit:
    """ALAP schedule with delays from the restricted snapshot's Target durations."""
    target = calibration_snapshot.build_target(snapshot)
    return PassManager([ALAPScheduleAnalysis(target=target), PadDelay(target=target)]).run(circuit)


def edges(circuit: QuantumCircuit) -> list[tuple[int, int]]:
    pairs = [[circuit.find_bit(q).index for q in i.qubits] for i in circuit.data if i.operation.name == "cz"]
    return sorted({(min(pair), max(pair)) for pair in pairs})


def _unitary(gate: Any) -> UnitaryGate:
    return UnitaryGate(gate.to_matrix(), label="channel")


def with_channel(
    circuit: QuantumCircuit, channel: str | None, params: np.ndarray, edge_list: list[tuple[int, int]]
) -> QuantumCircuit:
    """Insert the candidate's operations after the gates they modify; durations are untouched."""
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        out.append(instruction)
        name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        if channel == "sx_overrotation" and name == "sx":
            out.append(_unitary(RXGate(float(params[qubits[0]]))), qubits)
        elif name == "cz" and channel == "cz_local_phase":
            for q in qubits:
                out.append(_unitary(RZGate(float(params[q]))), [q])
        elif name == "cz" and channel == "cz_conditional_phase":
            out.append(_unitary(CPhaseGate(float(params[edge_list.index(tuple(sorted(qubits)))]))), qubits)
        elif name == "cz" and channel == "extra_damping":
            for q in qubits:
                out.append(amplitude_damping_error(float(params[q])).to_instruction(), [q])
        elif name == "cz" and channel == "extra_depolarizing":
            for q in qubits:
                out.append(depolarizing_error(float(params[q]), 1).to_instruction(), [q])
    return out


class LaneModel:
    """Exact laws of one member under the scheduled calibrated model plus one candidate channel."""

    def __init__(self, circuit: QuantumCircuit, snapshot: dict[str, Any], qubits: list[int], device: str) -> None:
        self.reduced = snapshot_laws.restrict(snapshot, qubits)
        self.flips = [(q["e10"], q["e01"]) for q in self.reduced["qubits"]]
        self.measured = {
            circuit.find_bit(i.qubits[0]).index: circuit.find_bit(i.clbits[0]).index
            for i in circuit.data
            if i.operation.name == "measure"
        }
        body = circuit.remove_final_measurements(inplace=False)
        self.unscheduled = body
        self.scheduled = schedule(body, self.reduced)
        self.edges = edges(body)
        self.simulator = calibration_snapshot.noise_simulator(self.reduced, device)

    def law(self, channel: str | None, params: np.ndarray, scheduled: bool = True) -> np.ndarray:
        base = self.scheduled if scheduled else self.unscheduled
        circuit = with_channel(base, channel, params, self.edges)
        order = sorted(self.measured, key=self.measured.__getitem__)
        circuit.save_probabilities(order, label="p")
        probabilities = np.asarray(self.simulator.run(circuit).result().data(0)["p"], dtype=float)
        matrix = np.ones((1, 1))
        for q in order:
            e10, e01 = self.flips[q]
            assign = np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])
            if channel == "end_flip":
                a = float(params[q])
                assign = assign @ np.array([[1.0 - a, 0.0], [a, 1.0]])
            matrix = np.kron(assign, matrix)
        law = matrix @ probabilities
        return np.clip(law, 1e-15, None) / law.sum()


def parameter_count(channel: str, model: LaneModel) -> int:
    return len(model.edges) if CHANNELS[channel][0] == "edge" else 4


def log_likelihood(counts: list[int], law: np.ndarray) -> float:
    return float(np.dot(counts, np.log(law)))


def deviance(counts: list[int], law: np.ndarray) -> float:
    """G^2 = 2 sum n log(n / (N p)) against the saturated law."""
    n = np.asarray(counts, dtype=float)
    mask = n > 0
    return float(2.0 * np.sum(n[mask] * np.log(n[mask] / (n.sum() * law[mask]))))


_MODELS: dict[tuple[str, str], LaneModel] = {}


def lane_model(lane: dict[str, Any], member: str, device: str) -> LaneModel:
    key = (lane["run"], member)
    if key not in _MODELS:
        entry = lane["members"][member]
        snapshot = json.loads((ROOT / entry["snapshot"]).read_text(encoding="utf-8"))
        _MODELS[key] = LaneModel(entry["circuit"], snapshot, lane["qubits"], device)
    return _MODELS[key]


def fit_member(lane: dict[str, Any]) -> str:
    return next(name for name in lane["members"] if name.endswith(FIT_MEMBER))


class FitTask:
    """Picklable worker: (lane, channel, start) -> the readout0 maximum-likelihood fit.

    An empty start runs the seeded global search; any other start runs
    L-BFGS-B from that start as a fraction of the bound.
    """

    def __init__(self, lanes: list[dict[str, Any]], device: str) -> None:
        self.lanes = lanes
        self.device = device

    def __call__(self, item: tuple[int, str, tuple[float, ...]]) -> dict[str, Any]:
        lane_index, channel, start = item
        lane = self.lanes[lane_index]
        member = fit_member(lane)
        model = lane_model(lane, member, self.device)
        counts = lane["members"][member]["counts"]
        size = parameter_count(channel, model)
        _, low, high = CHANNELS[channel]
        x0 = np.clip(np.asarray(start[:size]) * max(abs(low), abs(high)), low, high) if start else None

        def objective(x: np.ndarray) -> float:
            return -log_likelihood(counts, model.law(channel, x))

        bounds = [(low, high)] * size
        if not start:
            result = optimize.differential_evolution(
                objective,
                bounds,
                seed=GLOBAL_SEARCH["seed"],
                popsize=GLOBAL_SEARCH["popsize"],
                maxiter=GLOBAL_SEARCH["maxiter"],
                init=GLOBAL_SEARCH["init"],
                tol=GLOBAL_SEARCH["tol"],
                polish=True,
                updating="immediate",
                workers=1,
            )
        else:
            result = optimize.minimize(
                objective, x0, method="L-BFGS-B", bounds=bounds, options={"eps": 1e-5, "maxiter": 200}
            )
        return {
            "lane": lane_index,
            "channel": channel,
            "start": list(start[:size]),
            "x": result.x.tolist(),
            "neg_log_likelihood": float(result.fun),
            "evaluations": int(result.nfev),
        }


class ScoreTask:
    """Picklable worker: (lane, channel or baseline, parameters, member) -> that member's law."""

    def __init__(self, lanes: list[dict[str, Any]], device: str) -> None:
        self.lanes = lanes
        self.device = device

    def __call__(self, item: tuple[int, str, tuple[float, ...], str]) -> list[float]:
        lane_index, channel, params, member = item
        model = lane_model(self.lanes[lane_index], member, self.device)
        if channel == "unscheduled":
            return model.law(None, np.zeros(4), scheduled=False).tolist()
        if channel == "scheduled":
            return model.law(None, np.zeros(4)).tolist()
        return model.law(channel, np.asarray(params)).tolist()


class ConformanceTask:
    """Picklable worker: (lane, member) -> noiseless law error against the cd_core ideal, and zero-parameter checks."""

    def __init__(self, lanes: list[dict[str, Any]], device: str) -> None:
        self.lanes = lanes
        self.device = device

    def __call__(self, item: tuple[int, str]) -> dict[str, Any]:
        lane_index, member = item
        lane = self.lanes[lane_index]
        model = lane_model(lane, member, self.device)
        from qiskit.quantum_info import Statevector

        body = model.unscheduled
        order = sorted(model.measured, key=model.measured.__getitem__)
        noiseless = Statevector(body).probabilities(order)
        ideal = ideal_law(member)
        baseline = model.law(None, np.zeros(4))
        zero_error = max(
            float(np.max(np.abs(model.law(channel, np.zeros(parameter_count(channel, model))) - baseline)))
            for channel in CHANNELS
        )
        replay = np.asarray(lane["members"][member]["replay"])
        unscheduled = model.law(None, np.zeros(4), scheduled=False)
        return {
            "lane": lane_index,
            "member": member,
            "ideal_max_error": float(np.max(np.abs(noiseless - ideal))),
            "zero_parameter_max_error": zero_error,
            "replay_deviance": deviance(
                np.rint(replay * lane["members"][member]["shots"]).astype(int).tolist(), unscheduled
            ),
        }


def algebra_record() -> dict[str, Any]:
    """The dim-32 products behind each walk pair's associator pattern, in cd_core and in the pinned packages."""
    products = sorted({pair for i, j in PAIRS for x in range(16) for pair in ((i, j), (i ^ j, x), (j, x), (i, j ^ x))})
    record: dict[str, Any] = {
        "dim": DIM,
        "products": [list(p) for p in products],
        "cd_core_signs": [cd_sign(DIM, a, b) for a, b in products],
        "patterns": {f"{i},{j}": predict.associator_phase(DIM, i, j)[:16] for i, j in PAIRS},
    }
    try:
        import hypercomplex
        import hypercomplex_engine
    except ImportError as error:
        record["packages"] = {"unavailable": str(error)}
        return record
    algebra = hypercomplex.cayley_dickson_algebra(DIM.bit_length() - 1, Fraction)

    def hypercomplex_sign(a: int, b: int) -> int:
        coefficients = (algebra.e(a) * algebra.e(b)).coefficients()
        nonzero = [(k, c) for k, c in enumerate(coefficients) if c != 0]
        if len(nonzero) != 1 or nonzero[0][0] != a ^ b or abs(nonzero[0][1]) != 1:
            raise SystemExit(f"hypercomplex e{a} e{b} is not the signed unit e{a ^ b}: {nonzero}")
        return int(nonzero[0][1])

    def engine_sign(a: int, b: int) -> int:
        sign, index = hypercomplex_engine.multiply("standard", (1, a), (1, b))
        if int(index) != a ^ b:
            raise SystemExit(f"hypercomplex-engine e{a} e{b} lands on e{index}, not e{a ^ b}")
        return int(sign)

    record["packages"] = {
        "hypercomplex": {
            "version": importlib.metadata.version("hypercomplex"),
            "coefficients": "fractions.Fraction",
            "signs": [hypercomplex_sign(a, b) for a, b in products],
        },
        "hypercomplex-engine": {
            "version": importlib.metadata.version("hypercomplex-engine"),
            "signs": [engine_sign(a, b) for a, b in products],
        },
    }
    for name, entry in record["packages"].items():
        if entry["signs"] != record["cd_core_signs"]:
            raise SystemExit(f"{name} differs from cd_core on the walk's dim-{DIM} products")
    return record


def channel_starts(channel: str) -> tuple[tuple[float, ...], ...]:
    return FIT_STARTS["positive"] if CHANNELS[channel][1] >= 0.0 else ((),)


def evaluate(device: str, lane_indices: list[int] | None = None, channels: list[str] | None = None) -> dict[str, Any]:
    lanes = load_lanes()
    chosen = lane_indices if lane_indices is not None else list(range(len(lanes)))
    names = channels if channels is not None else list(CHANNELS)
    conformance = parallel.ordered_map(
        ConformanceTask(lanes, device), [(k, m) for k in chosen for m in lanes[k]["members"]], min_items=1
    )
    for row in conformance:
        if row["ideal_max_error"] > 1e-9 or row["zero_parameter_max_error"] > 1e-12:
            raise SystemExit(f"conformance failed: {row}")
    fits = parallel.ordered_map(
        FitTask(lanes, device), [(k, c, s) for k in chosen for c in names for s in channel_starts(c)], min_items=1
    )
    best: dict[tuple[int, str], dict[str, Any]] = {}
    for fit in fits:
        key = (fit["lane"], fit["channel"])
        if key not in best or fit["neg_log_likelihood"] < best[key]["neg_log_likelihood"]:
            best[key] = fit
    models = ["unscheduled", "scheduled", *names]
    items = [
        (k, c, tuple(best[(k, c)]["x"]) if (k, c) in best else (), m)
        for k in chosen
        for c in models
        for m in lanes[k]["members"]
    ]
    laws = parallel.ordered_map(ScoreTask(lanes, device), items, min_items=1)
    law_of = {(k, c, m): np.asarray(law) for (k, c, _, m), law in zip(items, laws, strict=True)}
    out_lanes = []
    for k in chosen:
        lane = lanes[k]
        fit_name = fit_member(lane)
        held = [m for m in lane["members"] if m != fit_name]
        rows: dict[str, dict[str, Any]] = {}
        for c in models:
            size = parameter_count(c, lane_model(lane, fit_name, device)) if c in CHANNELS else 0
            fit_counts = lane["members"][fit_name]["counts"]
            g2_fit = deviance(fit_counts, law_of[(k, c, fit_name)])
            g2_held = sum(deviance(lane["members"][m]["counts"], law_of[(k, c, m)]) for m in held)
            rows[c] = {
                "parameters": best[(k, c)]["x"] if c in CHANNELS else [],
                "fit_deviance": g2_fit,
                "fit_dof": 15 - size,
                "fit_p": float(stats.chi2.sf(g2_fit, 15 - size)),
                "fit_p0000": float(law_of[(k, c, fit_name)][0]),
                "held_out_log_likelihood": sum(
                    log_likelihood(lane["members"][m]["counts"], law_of[(k, c, m)]) for m in held
                ),
                "held_out_deviance": g2_held,
                "held_out_dof": 15 * len(held),
                "held_out_p": float(stats.chi2.sf(g2_held, 15 * len(held))),
                "held_out_tvd": {
                    m: float(
                        0.5
                        * np.abs(
                            law_of[(k, c, m)] - np.asarray(lane["members"][m]["counts"]) / lane["members"][m]["shots"]
                        ).sum()
                    )
                    for m in held
                },
                "laws": {m: law_of[(k, c, m)].tolist() for m in lane["members"]},
            }
        baseline = rows["scheduled"]["held_out_log_likelihood"]
        for c in names:
            rows[c]["passes_fit_gate"] = rows[c]["fit_p"] >= GATE_P
            rows[c]["reproduces_floor"] = bool(
                rows[c]["passes_fit_gate"]
                and rows[c]["held_out_p"] >= GATE_P
                and rows[c]["held_out_log_likelihood"] > baseline
            )
        out_lanes.append(
            {
                "run": lane["run"],
                "backend": lane["backend"],
                "lane": lane["lane"],
                "qubits": lane["qubits"],
                "edges": [[lane["qubits"][a], lane["qubits"][b]] for a, b in lane_model(lane, fit_name, device).edges],
                "fit_member": fit_name,
                "held_out_members": held,
                "hardware_counts": {m: lane["members"][m]["counts"] for m in lane["members"]},
                "snapshots": {m: lane["members"][m]["snapshot"] for m in lane["members"]},
                "models": rows,
                "fits": [f for f in fits if f["lane"] == k],
            }
        )
    return {"conformance": conformance, "lanes": out_lanes}


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
        "workers": parallel.workers(),
    }


def run(device: str, lane_indices: list[int] | None = None, channels: list[str] | None = None) -> dict[str, Any]:
    started = time.time()
    algebra = algebra_record()
    result = evaluate(device, lane_indices, channels)
    return {
        "schema": "gororoba-walk-scaffold-channels-v1",
        "runs": list(RUNS),
        "channels": {name: {"per": per, "bounds": [low, high]} for name, (per, low, high) in CHANNELS.items()},
        "fit_starts": {key: [list(s) for s in value] for key, value in FIT_STARTS.items()},
        "global_search": GLOBAL_SEARCH,
        "gate_p": GATE_P,
        "algebra": algebra,
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


def extract_matches() -> list[str]:
    """Re-derive the extract from the retained runs and require identical bytes."""
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        fresh_json, fresh_qpy = Path(scratch) / "members.json", Path(scratch) / "members.qpy"
        write_extract(fresh_json, fresh_qpy)
        return [
            f"{kept.relative_to(ROOT)} differs from its re-derivation"
            for kept, fresh in ((EXTRACT_JSON, fresh_json), (EXTRACT_QPY, fresh_qpy))
            if kept.read_bytes() != fresh.read_bytes()
        ]


def check(path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, run_dir) + extract_matches()
    algebra = retained["algebra"]
    products = [tuple(p) for p in algebra["products"]]
    signs = [cd_sign(DIM, a, b) for a, b in products]
    if signs != algebra["cd_core_signs"]:
        failures.append("cd_core signs differ from the retained algebra record")
    for name, entry in algebra.get("packages", {}).items():
        if name == "unavailable" or entry["signs"] != signs:
            failures.append(f"package record {name} is unavailable or differs from cd_core")
    lanes = load_lanes()
    index = next(
        k
        for k, lane in enumerate(lanes)
        if lane["run"].endswith("2026-10-15T031229.371738Z") and lane["lane"] == "lane0"
    )
    lane = lanes[index]
    kept = next(entry for entry in retained["lanes"] if entry["run"] == lane["run"] and entry["lane"] == lane["lane"])
    member = kept["fit_member"]
    counts = lane["members"][member]["counts"]
    held = kept["held_out_members"]
    models = list(kept["models"].items())
    items = [
        (index, name, tuple(row.get("parameters", ())), other) for name, row in models for other in lane["members"]
    ]
    probes = []
    for name, row in models:
        if name in CHANNELS:
            _, low, high = CHANNELS[name]
            step = PROBE_STEP * (high - low)
            for k, value in enumerate(row["parameters"]):
                for moved in (value - step, value + step):
                    if low <= moved <= high:
                        params = list(row["parameters"])
                        params[k] = moved
                        probes.append((name, k, moved))
                        items.append((index, name, tuple(params), member))
    results = parallel.ordered_map(ScoreTask(lanes, calibration_snapshot.aer_device()), items, min_items=1)
    replayed = iter(results)
    baseline_ll = None
    for name, row in models:
        laws = {other: np.asarray(next(replayed)) for other in lane["members"]}
        for other, law in laws.items():
            if not np.allclose(law, row["laws"][other], rtol=1e-8, atol=1e-10):
                failures.append(f"{name}: law of {other} differs from the retained law")
        held_ll = sum(log_likelihood(lane["members"][m]["counts"], laws[m]) for m in held)
        held_g2 = sum(deviance(lane["members"][m]["counts"], laws[m]) for m in held)
        if not math.isclose(held_ll, row["held_out_log_likelihood"], rel_tol=1e-8):
            failures.append(f"{name}: held-out log-likelihood {held_ll} against {row['held_out_log_likelihood']}")
        if not math.isclose(held_g2, row["held_out_deviance"], rel_tol=1e-8):
            failures.append(f"{name}: held-out deviance {held_g2} against {row['held_out_deviance']}")
        if name == "scheduled":
            baseline_ll = held_ll
    for (name, k, moved), law in zip(probes, replayed, strict=True):
        retained_ll = log_likelihood(counts, np.asarray(kept["models"][name]["laws"][member]))
        if log_likelihood(counts, np.asarray(law)) > retained_ll + 1e-3:
            failures.append(f"{name}: moving parameter {k} to {moved} improves the retained optimum")
    for name in CHANNELS:
        row = kept["models"][name]
        fit_g2 = deviance(counts, np.asarray(row["laws"][member]))
        decision = bool(
            stats.chi2.sf(fit_g2, row["fit_dof"]) >= GATE_P
            and stats.chi2.sf(row["held_out_deviance"], row["held_out_dof"]) >= GATE_P
            and baseline_ll is not None
            and row["held_out_log_likelihood"] > baseline_ll
        )
        if decision != row["reproduces_floor"]:
            failures.append(f"{name}: reproduces_floor {row['reproduces_floor']} against the replayed {decision}")
    for failure in failures:
        print(failure)
    print(
        f"walk scaffold channels replay: Kingston lane0, {len(kept['models'])} models over "
        f"{len(lane['members'])} members, {len(failures)} departures"
    )
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    parser.add_argument("--extract", action="store_true", help="write the members extract from the retained runs")
    parser.add_argument("--lanes", help="comma-separated lane indices (default all four)")
    parser.add_argument("--channels", help="comma-separated names from CHANNELS (default all)")
    args = parser.parse_args()
    if args.extract:
        write_extract(EXTRACT_JSON, EXTRACT_QPY)
        print(f"wrote {EXTRACT_JSON.relative_to(ROOT)} and {EXTRACT_QPY.relative_to(ROOT)}")
        return 0
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    lanes = [int(k) for k in args.lanes.split(",")] if args.lanes else None
    channels = args.channels.split(",") if args.channels else None
    if channels and set(channels) - set(CHANNELS):
        parser.error(f"unknown channels {sorted(set(channels) - set(CHANNELS))}")
    result = run(calibration_snapshot.aer_device(), lanes, channels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(result['lanes'])} lanes in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
