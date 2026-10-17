"""Aer density-matrix oracle for the exact branch-resolved law of the encoded N=21 feedback pair.

gororoba_quantum/dynamic_density.py claims Aer's semantics for dynamic ISA
circuits. This script checks the claim against Aer itself, sampling only which
branches appear: AerSimulator with method="density_matrix" applies every
channel as a superoperator (AerController enables the superop noise method for
it), and ``save_density_matrix(conditional=True)`` before each mid-circuit
measure and at the end returns the exact state of every recorded-memory value
a shot reached.

- **Keys.** A conditional save keys on ``ClassicalRegister::memory_hex``
  (ExperimentResult::save_data_average, DataSubType::c_average), and
  ClassicalRegister::apply_roerror writes the readout-flipped value into both
  the memory and the register that ``check_conditional`` reads, so the key is
  the recorded value. A recorded value r averages the shots of both true
  outcomes k in their sampled proportions; the oracle therefore runs each
  pattern f of mid-circuit readout flips once, with that qubit's readout made
  deterministic (identity for f = 0, the swap [[0, 1], [1, 0]] for f = 1).
  In run f the key r = k xor f names one true outcome, every shot behind a
  key carries the same state, and branch (k, r) lives in run f = k xor r.
- **Law.** A branch weighs the product over mid-circuit measures of
  P(k | prefix), read from the normalized pre-measure save, and the noise
  model's own readout entry R[k][r]. Terminal measures (no later instruction
  touches their qubit or clbit) leave the oracle circuit; the joint diagonal
  of the normalized end state over the terminal qubits, mapped through the
  tensor product of their readout matrices, gives each branch's recorded
  terminal law. Aer renormalizes the state at each measure
  (State::measure_reset_update divides by the outcome probability) and at
  sampling, as the normalized saves do.
- **Threshold.** qiskit-aer 0.17.2 QuantumError::set_circuits
  (src/noise/quantum_error.hpp, threshold_ = 1e-10) keeps only the noise
  circuits whose probability exceeds 1e-10 and does not renormalize. Each
  noise circuit is trace preserving, so the discarded part removes the same
  fraction of every branch's trace, and the renormalization at each measure
  and at sampling restores it: Aer's law under live_run's channel (``raw``)
  is the law of the ``cleaned`` model, which removes those components in
  Python, where QuantumError renormalizes the rest. dynamic_density keeps the
  components, so under ``raw`` the two engines differ by at most D / (1 - D)
  per outcome, D the summed discarded mass of every noisy instruction (the
  discarded part is completely positive, so the unnormalized branch weights
  fall by at most D in total, and each renormalization rescales by at most
  1 / (1 - D)). Under ``cleaned`` both engines apply one channel.

``--out FILE`` writes the record: both circuits under both models, laws,
arm scores and contrast from each engine, per-branch weights and state gaps
at every save, the first instruction whose error Aer truncates with the
states on either side of it, and the fixture. ``--check FILE`` recomputes
it, requires the same structure and every float within TOLERANCE.
``--self-test`` runs dynamic_density's three-qubit fixture: the default
Semantics within TOLERANCE of the oracle, each of the seven alternatives
beyond it, and a removed branch refused.
"""

from __future__ import annotations

import argparse
import copy
import io
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import n21_exact_model_validation as validation  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.quantum_info import DensityMatrix, partial_trace  # noqa: E402

import calibration_snapshot  # noqa: E402
import dynamic_density  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "n21-exact-crosscheck-v1"
SNAPSHOT = Path("docs/evidence/calibration/history/ibm_kingston/20261016T1213360700.json")
ISA = Path("results/live/2026-10-17T003834.987727Z/isa.qpy")
RECORD = ISA.parent / "record.json"
AER_THRESHOLD = 1e-10
# TOLERANCE separates the float error of two engines evolving one channel
# (order 1e-15 on these states) from the smallest effect the record must
# resolve: one noise component Aer truncates (order 1e-10) and an alternative
# Semantics on the fixture (order 1e-2).
TOLERANCE = 1e-12
SHOTS = 32
SEED = 20261017
SWAP = [[0.0, 1.0], [1.0, 0.0]]
SEMANTICS_FIELDS = ("body_noise", "reset_error_after", "recorded_condition")


def _layout(circuit: QuantumCircuit) -> dict[str, Any]:
    """Mid-circuit and terminal measures as (instruction index, qubit, clbit), in circuit order."""
    touches: list[tuple[set[int], set[int]]] = []
    for instruction in circuit.data:
        qubits = {circuit.find_bit(q).index for q in instruction.qubits}
        clbits = {circuit.find_bit(c).index for c in instruction.clbits}
        condition = getattr(instruction.operation, "condition", None)
        if condition is not None:
            clbits.update(dynamic_density._condition_bits(circuit, condition)[0])
        touches.append((qubits, clbits))
    mid: list[tuple[int, int, int]] = []
    terminal: list[tuple[int, int, int]] = []
    for position, instruction in enumerate(circuit.data):
        if instruction.operation.name != "measure":
            continue
        qubit = circuit.find_bit(instruction.qubits[0]).index
        clbit = circuit.find_bit(instruction.clbits[0]).index
        later = touches[position + 1 :]
        if any(qubit in q or clbit in c for q, c in later):
            mid.append((position, qubit, clbit))
        else:
            terminal.append((position, qubit, clbit))
    if len({q for _p, q, _c in mid}) != len(mid):
        raise dynamic_density.UnsupportedCircuit(
            f"{circuit.name}: two mid-circuit measures share a qubit, whose Aer readout one flip pattern sets"
        )
    written = [c for _p, _q, c in mid + terminal]
    if len(set(written)) != len(written):
        raise dynamic_density.UnsupportedCircuit(f"{circuit.name}: two measures write one clbit")
    if terminal:
        tail = circuit.data[terminal[0][0] :]
        if any(i.operation.name not in ("measure", "barrier") for i in tail):
            raise dynamic_density.UnsupportedCircuit(f"{circuit.name}: an operation follows the first terminal measure")
    if dynamic_density._active(circuit) != list(range(circuit.num_qubits)):
        raise dynamic_density.UnsupportedCircuit(f"{circuit.name}: idle qubits; restrict the circuit first")
    return {"mid": mid, "terminal": terminal}


def _oracle_circuit(circuit: QuantumCircuit, layout: dict[str, Any]) -> QuantumCircuit:
    """circuit with a conditional density-matrix save before each mid-circuit measure and at the end."""
    from qiskit_aer.library import SaveDensityMatrix

    before = {position: j for j, (position, _q, _c) in enumerate(layout["mid"])}
    dropped = {position for position, _q, _c in layout["terminal"]}
    out = circuit.copy_empty_like()
    for position, instruction in enumerate(circuit.data):
        if position in before:
            out.append(
                SaveDensityMatrix(circuit.num_qubits, label=f"pre{before[position]}", conditional=True), out.qubits
            )
        if position not in dropped:
            out.append(instruction)
    out.append(SaveDensityMatrix(circuit.num_qubits, label="end", conditional=True), out.qubits)
    return out


def dropped_mass(error: Any) -> float:
    """Probability Aer's QuantumError discards: the components at or below AER_THRESHOLD."""
    return math.fsum(float(p) for p in error.probabilities if p <= AER_THRESHOLD)


def cleaned(noise: Any) -> Any:
    """noise with every component at or below AER_THRESHOLD removed and the rest renormalized."""
    from qiskit_aer.noise import QuantumError

    out = copy.deepcopy(noise)
    for by_qubits in out._local_quantum_errors.values():
        for qubits, error in list(by_qubits.items()):
            if dropped_mass(error) > 0:
                kept = [(c, p) for c, p in zip(error.circuits, error.probabilities, strict=True) if p > AER_THRESHOLD]
                by_qubits[qubits] = QuantumError(kept)
    for name, error in list(out._default_quantum_errors.items()):
        if dropped_mass(error) > 0:
            kept = [(c, p) for c, p in zip(error.circuits, error.probabilities, strict=True) if p > AER_THRESHOLD]
            out._default_quantum_errors[name] = QuantumError(kept)
    return out


def _flipped(noise: Any, qubits: list[int], flips: tuple[int, ...]) -> Any:
    """noise with each mid-circuit qubit's readout deterministic: identity for flip 0, the swap for flip 1."""
    from qiskit_aer.noise import ReadoutError

    if getattr(noise, "_default_readout_error", None) is not None:
        raise dynamic_density.UnsupportedCircuit("an all-qubit readout error cannot be replaced per qubit")
    out = copy.deepcopy(noise)
    for qubit, flip in zip(qubits, flips, strict=True):
        out._local_readout_errors.pop((qubit,), None)
        if flip:
            out.add_readout_error(ReadoutError(SWAP), [qubit], warnings=False)
    return out


def _readout(noise: Any, qubit: int) -> np.ndarray:
    error = noise._local_readout_errors.get((qubit,))
    if error is None:
        error = getattr(noise, "_default_readout_error", None)
    return np.eye(2) if error is None else np.asarray(error.probabilities, dtype=float)


def _inputs(source: tuple[Any, ...], model: str) -> tuple[QuantumCircuit, Any]:
    """The circuit and noise model of a source: ("fixture",) or ("snapshot", restricted snapshot, qpy bytes)."""
    if source[0] == "fixture":
        circuit, noise = dynamic_density._fixture()
    else:
        circuit = qpy.load(io.BytesIO(source[2]))[0]
        noise = calibration_snapshot.noise_model(source[1])[1]
    return circuit, cleaned(noise) if model == "cleaned" else noise


class _Capture(dynamic_density._Evolution):
    """dynamic_density's evolution, recording its branch states before each measure and at the end."""

    snapshots: list[dict[tuple[int, int], np.ndarray]] = []

    def _record(self) -> None:
        size = 2**self.n
        _Capture.snapshots.append({key: rho.reshape(size, size).copy() for key, rho in self.branches.items()})

    def measure(self, physical: int, clbit: int) -> None:
        self._record()
        super().measure(physical, clbit)

    def distribution(self) -> np.ndarray:
        self._record()
        return super().distribution()


def _dynamic_density(
    circuit: QuantumCircuit, noise: Any, semantics: dynamic_density.Semantics
) -> tuple[np.ndarray, list[dict[tuple[int, int], np.ndarray]]]:
    """dynamic_density.probabilities with the branch states before each measure and at the end."""
    original = dynamic_density._Evolution
    _Capture.snapshots = []
    dynamic_density._Evolution = _Capture  # type: ignore[misc]
    try:
        law = dynamic_density.probabilities(circuit, noise, semantics)
    finally:
        dynamic_density._Evolution = original  # type: ignore[misc]
    return law, _Capture.snapshots


def _aer_saves(circuit: QuantumCircuit, noise: Any, shots: int) -> dict[str, dict[int, np.ndarray]]:
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(
        method="density_matrix",
        noise_model=noise,
        seed_simulator=SEED,
        shot_branching_enable=True,
        max_parallel_threads=1,
    )
    data = simulator.run(circuit, shots=shots).result().data(0)
    return {
        label: {int(key, 16): np.asarray(state) for key, state in value.items()}
        if isinstance(value, dict)
        else {0: np.asarray(value)}
        for label, value in data.items()
        if label != "counts"
    }


def _work(item: tuple[Any, ...]) -> Any:
    """One unit of the cross-check: an Aer run, a dynamic_density run, or a localization prefix."""
    kind, source, model = item[0], item[1], item[2]
    circuit, noise = _inputs(source, model)
    if kind == "aer":
        layout = _layout(circuit)
        flips = item[3]
        variant = _flipped(noise, [q for _p, q, _c in layout["mid"]], flips)
        return _aer_saves(_oracle_circuit(circuit, layout), variant, SHOTS)
    if kind == "dd":
        semantics = dynamic_density.Semantics(**dict(zip(SEMANTICS_FIELDS, item[3], strict=True)))
        law, snapshots = _dynamic_density(circuit, noise, semantics)
        return law, snapshots
    if kind == "prefix":
        # States on either side of instruction `position`, from both engines.
        from qiskit_aer.library import SaveDensityMatrix

        position = item[3]
        prefix = circuit.copy_empty_like()
        for instruction in circuit.data[:position]:
            prefix.append(instruction)
        prefix.append(SaveDensityMatrix(circuit.num_qubits, label="before"), prefix.qubits)
        prefix.append(circuit.data[position])
        prefix.append(SaveDensityMatrix(circuit.num_qubits, label="after"), prefix.qubits)
        aer = _aer_saves(prefix, noise, 1)
        out = {}
        for label, length in (("before", position), ("after", position + 1)):
            head = circuit.copy_empty_like()
            for instruction in circuit.data[:length]:
                head.append(instruction)
            active = dynamic_density._active(head)
            if not active:
                out[label] = 0.0
                continue
            _law, snapshots = _dynamic_density(head, noise, dynamic_density.AER)
            # dynamic_density evolves the active qubits only; the idle ones stay |0> in Aer.
            idle = [q for q in range(circuit.num_qubits) if q not in active]
            reduced = np.asarray(partial_trace(DensityMatrix(aer[label][0]), idle).data)
            out[label] = _state_gap(reduced, snapshots[-1][(0, 0)])
        return out
    raise ValueError(f"unknown work kind {kind}")


def _normalized(state: np.ndarray) -> np.ndarray:
    return state / np.real(np.trace(state))


def _state_gap(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.max(np.abs(_normalized(left) - _normalized(right))))


def _qubit_law(state: np.ndarray, qubits: list[int]) -> np.ndarray:
    """Joint true-outcome law of qubits (position i is bit i) in the normalized state."""
    diagonal = np.real(np.diag(_normalized(state)))
    index = np.arange(diagonal.size)
    codes = np.zeros(diagonal.size, dtype=np.int64)
    for position, qubit in enumerate(qubits):
        codes |= ((index >> qubit) & 1) << position
    return np.bincount(codes, weights=diagonal, minlength=2 ** len(qubits))


def reconstruct(
    runs: dict[tuple[int, ...], dict[str, dict[int, np.ndarray]]],
    layout: dict[str, Any],
    noise: Any,
    num_clbits: int,
) -> dict[str, Any]:
    """The recorded law from the flip runs' saves: branch weight times its recorded terminal law."""
    mid, terminal = layout["mid"], layout["terminal"]
    terminal_qubits = [q for _p, q, _c in terminal]
    mixing = np.ones((1, 1))
    for qubit in terminal_qubits:
        mixing = np.kron(_readout(noise, qubit), mixing)
    law = np.zeros(2**num_clbits)
    branches = []
    for outcomes in itertools.product((0, 1), repeat=len(mid)):
        for recorded in itertools.product((0, 1), repeat=len(mid)):
            flips = tuple(k ^ r for k, r in zip(outcomes, recorded, strict=True))
            run = runs[flips]
            weight = 1.0
            key = 0
            states: dict[str, np.ndarray] = {}
            visited = True
            for j, (_p, qubit, clbit) in enumerate(mid):
                state = run[f"pre{j}"].get(key)
                if state is None:
                    visited = False
                    break
                states[f"pre{j}"] = state
                weight *= _qubit_law(state, [qubit])[outcomes[j]] * _readout(noise, qubit)[outcomes[j]][recorded[j]]
                key |= recorded[j] << clbit
            end = run["end"].get(key) if visited else None
            if end is not None:
                states["end"] = end
            branches.append(
                {
                    "outcomes": list(outcomes),
                    "recorded": list(recorded),
                    "weight": weight if end is not None else None,
                    "visited": end is not None,
                    "states": states,
                }
            )
            if end is None:
                continue
            terminal_law = _qubit_law(end, terminal_qubits) @ mixing
            for code, probability in enumerate(terminal_law):
                index = key
                for position, (_p, _q, clbit) in enumerate(terminal):
                    index |= ((code >> position) & 1) << clbit
                law[index] += weight * probability
    return {"law": law, "branches": branches}


def _unvisited_weight(branches: list[dict[str, Any]], mid: list[tuple[int, int, int]], noise: Any) -> float:
    """Exact weight of the branches no shot reached, from the deepest save each one did reach."""
    total = 0.0
    for branch in branches:
        if branch["visited"]:
            continue
        weight = 1.0
        for j, (_p, qubit, _c) in enumerate(mid):
            state = branch["states"].get(f"pre{j}")
            k, r = branch["outcomes"][j], branch["recorded"][j]
            readout = _readout(noise, qubit)[k][r]
            weight *= readout if state is None else _qubit_law(state, [qubit])[k] * readout
        total += weight
    return total


def _branch_comparison(
    branches: list[dict[str, Any]],
    snapshots: list[dict[tuple[int, int], np.ndarray]],
    layout: dict[str, Any],
) -> dict[str, Any]:
    """Per save point, the largest normalized-state gap, and at the end the branch-weight gap, oracle against dd."""
    mid, terminal = layout["mid"], layout["terminal"]
    # dynamic_density records before every measure and at the end; the saves
    # sit before each mid-circuit measure and before the first terminal one.
    order = sorted(
        [(p, "mid", j) for j, (p, _q, _c) in enumerate(mid)] + [(p, "terminal", 0) for p, _q, _c in terminal]
    )
    positions: dict[str, int] = {}
    for snapshot_index, (_p, kind, j) in enumerate(order):
        label = f"pre{j}" if kind == "mid" else "end"
        positions.setdefault(label, snapshot_index)
    positions.setdefault("end", len(order))
    gaps: dict[str, dict[str, float]] = {}
    for label, snapshot_index in sorted(positions.items()):
        snapshot = snapshots[snapshot_index]
        depth = len(mid) if label == "end" else int(label[3:])
        state_gap = 0.0
        weight_gap = 0.0
        compared = 0
        for branch in branches:
            state = branch["states"].get(label)
            if state is None:
                continue
            recorded = sum(r << c for r, (_p, _q, c) in zip(branch["recorded"][:depth], mid, strict=False))
            true = sum(k << c for k, (_p, _q, c) in zip(branch["outcomes"][:depth], mid, strict=False))
            reference = snapshot[(recorded, true)]
            state_gap = max(state_gap, _state_gap(state, reference))
            if label == "end":
                total = math.fsum(float(np.real(np.trace(rho))) for rho in snapshot.values())
                weight_gap = max(weight_gap, abs(branch["weight"] - float(np.real(np.trace(reference))) / total))
            compared += 1
        gaps[label] = {"branches": compared, "state_gap": state_gap}
        if label == "end":
            gaps[label]["weight_gap"] = weight_gap
    return gaps


def _scores(laws: dict[str, np.ndarray], members: dict[str, str], contracts: tuple[Any, ...]) -> dict[str, Any]:
    by_member = {members[name]: law for name, law in laws.items()}
    arms = {}
    for contract in contracts:
        for term in contract.terms:
            arms[term.member] = float(np.asarray(term.values, dtype=float) @ by_member[term.member])
    contrasts = {
        contract.name: math.fsum(term.sign * arms[term.member] for term in contract.terms) for contract in contracts
    }
    return {"arms": arms, "contrasts": contrasts}


def _first_dropped(circuit: QuantumCircuit, noise: Any) -> tuple[dict[str, Any] | None, float]:
    """The first instruction whose local error Aer truncates, and the dropped mass summed over the circuit."""
    first = None
    total = 0.0
    for position, instruction in enumerate(circuit.data):
        operation = instruction.operation
        outer = [circuit.find_bit(q).index for q in instruction.qubits]
        if operation.name == "if_else":
            pairs = [
                (inner.operation.name, tuple(outer[body.find_bit(q).index] for q in inner.qubits))
                for body in operation.blocks
                if body is not None
                for inner in body.data
            ]
        else:
            pairs = [(operation.name, tuple(outer))]
        for name, qubits in pairs:
            error = noise._local_quantum_errors.get(name, {}).get(qubits, noise._default_quantum_errors.get(name))
            mass = 0.0 if error is None else dropped_mass(error)
            total += mass
            if mass > 0 and first is None:
                first = {"index": position, "gate": name, "qubits": list(qubits), "dropped_mass": mass}
    return first, total


def _flip_patterns(layout: dict[str, Any]) -> list[tuple[int, ...]]:
    return list(itertools.product((0, 1), repeat=len(layout["mid"])))


def _evaluate(
    sources: dict[str, tuple[Any, ...]],
    models: tuple[str, ...],
    semantics: list[tuple[bool, ...]],
    localize: bool,
) -> dict[str, Any]:
    """Every Aer flip run and dynamic_density run of every source under every model, through one pool."""
    items: list[tuple[Any, ...]] = []
    plan: list[tuple[str, str, str, Any]] = []
    layouts = {}
    for name, source in sources.items():
        circuit, raw = _inputs(source, "raw")
        layouts[name] = _layout(circuit)
        for model in models:
            for flips in _flip_patterns(layouts[name]):
                items.append(("aer", source, model, flips))
                plan.append((name, model, "aer", flips))
            for choice in semantics if model == "raw" else semantics[:1]:
                items.append(("dd", source, model, choice))
                plan.append((name, model, "dd", choice))
        if localize:
            first, _total = _first_dropped(circuit, raw)
            if first is not None and first["index"] < layouts[name]["mid"][0][0]:
                items.append(("prefix", source, "raw", first["index"]))
                plan.append((name, "raw", "prefix", first["index"]))
    results = parallel.ordered_map(_work, items, min_items=2)
    out: dict[str, Any] = {name: {model: {"aer": {}, "dd": {}} for model in models} for name in sources}
    for (name, model, kind, key), result in zip(plan, results, strict=True):
        if kind == "prefix":
            out[name]["raw"]["prefix"] = result
        else:
            out[name][model][kind][key] = result
    return {"layouts": layouts, "runs": out}


def _compare_source(
    source: tuple[Any, ...], layout: dict[str, Any], runs: dict[str, Any], model: str
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    """Oracle against dynamic_density (Aer semantics) for one source under one model."""
    circuit, noise = _inputs(source, model)
    oracle = reconstruct(runs["aer"], layout, noise, circuit.num_clbits)
    law, snapshots = runs["dd"][tuple(getattr(dynamic_density.AER, f) for f in SEMANTICS_FIELDS)]
    visited = sum(1 for branch in oracle["branches"] if branch["visited"])
    unvisited = _unvisited_weight(oracle["branches"], layout["mid"], noise)
    if visited != len(oracle["branches"]):
        raise AssertionError(
            f"{circuit.name}: {len(oracle['branches']) - visited} branches unvisited, weight {unvisited}"
        )
    deficits = {
        label: max(1.0 - float(np.real(np.trace(state))) for state in saves.values())
        for label, saves in runs["aer"][_flip_patterns(layout)[0]].items()
    }
    first, total = _first_dropped(circuit, noise)
    row = {
        "aer": [float(v) for v in oracle["law"]],
        "dynamic_density": [float(v) for v in law],
        "max_gap": float(np.max(np.abs(oracle["law"] - law))),
        "oracle_total": math.fsum(oracle["law"]),
        "branches": len(oracle["branches"]),
        "visited": visited,
        "unvisited_weight": unvisited,
        "branch_weights": [
            {"outcomes": b["outcomes"], "recorded": b["recorded"], "weight": b["weight"]} for b in oracle["branches"]
        ],
        "saves": _branch_comparison(oracle["branches"], snapshots, layout),
        "aer_trace_deficit": deficits,
        "dropped_mass": total,
        "first_dropped": first,
    }
    return row, oracle["law"], law


def crosscheck() -> dict[str, Any]:
    """The record: both circuits under the raw and cleaned models, scores, localization, and the fixture."""
    snapshot = json.loads((ROOT / SNAPSHOT).read_text())
    members, contracts = validation.endpoint(ROOT / RECORD)
    sources: dict[str, tuple[Any, ...]] = {}
    for circuit in validation._circuits(ROOT / ISA):
        reduced, restricted, _qubits = validation._restricted(snapshot, circuit)
        sources[circuit.name] = ("snapshot", restricted, validation._serialized(reduced))
    evaluated = _evaluate(sources, ("raw", "cleaned"), [(True, True, True)], localize=True)
    models: dict[str, Any] = {}
    for model in ("raw", "cleaned"):
        circuits = {}
        oracle_laws = {}
        dd_laws = {}
        for name, source in sources.items():
            runs = evaluated["runs"][name][model]
            row, oracle_law, dd_law = _compare_source(source, evaluated["layouts"][name], runs, model)
            row["member"] = members[name]
            if model == "raw" and "prefix" in runs:
                row["first_dropped"]["state_gap_before"] = runs["prefix"]["before"]
                row["first_dropped"]["state_gap_after"] = runs["prefix"]["after"]
            circuits[name] = row
            oracle_laws[name] = oracle_law
            dd_laws[name] = dd_law
        aer_scores = _scores(oracle_laws, members, contracts)
        dd_scores = _scores(dd_laws, members, contracts)
        models[model] = {
            "circuits": circuits,
            "arms": {
                member: {"aer": aer_scores["arms"][member], "dynamic_density": dd_scores["arms"][member]}
                for member in sorted(aer_scores["arms"])
            },
            "contrasts": {
                name: {"aer": aer_scores["contrasts"][name], "dynamic_density": dd_scores["contrasts"][name]}
                for name in sorted(aer_scores["contrasts"])
            },
        }
        for block in (models[model]["arms"], models[model]["contrasts"]):
            for value in block.values():
                value["gap"] = value["dynamic_density"] - value["aer"]
    attribution = {
        name: {
            engine: float(
                np.max(
                    np.abs(
                        np.asarray(models["raw"]["circuits"][name][engine])
                        - np.asarray(models["cleaned"]["circuits"][name][engine])
                    )
                )
            )
            for engine in ("aer", "dynamic_density")
        }
        for name in sources
    }
    _require_verdict(models, attribution)
    import qiskit
    import qiskit_aer

    return {
        "schema": SCHEMA,
        "inputs": {
            "snapshot": {"path": str(SNAPSHOT), "sha256": validation._sha256(ROOT / SNAPSHOT)},
            "isa": {"path": str(ISA), "sha256": validation._sha256(ROOT / ISA)},
            "record": {"path": str(RECORD), "sha256": validation._sha256(ROOT / RECORD)},
        },
        "oracle": {
            "simulator": "AerSimulator",
            "method": "density_matrix",
            "shot_branching_enable": True,
            "shots": SHOTS,
            "seed": SEED,
            "aer_threshold": AER_THRESHOLD,
        },
        "tolerance": TOLERANCE,
        "models": models,
        "raw_minus_cleaned": attribution,
        "fixture": fixture(),
        "versions": {
            "python": ".".join(str(v) for v in sys.version_info[:3]),
            "qiskit": qiskit.__version__,
            "qiskit-aer": qiskit_aer.__version__,
            "numpy": np.__version__,
        },
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_verdict(models: dict[str, Any], attribution: dict[str, dict[str, float]]) -> None:
    """Cleaned: laws, states, weights within TOLERANCE. Raw: Aer's law is the cleaned one; gaps under D / (1 - D)."""
    for name, row in attribution.items():
        _require(row["aer"] <= TOLERANCE, f"{name}: Aer's raw law leaves its cleaned law by {row['aer']}")
    for name, row in models["cleaned"]["circuits"].items():
        _require(row["dropped_mass"] == 0.0, f"{name}: the cleaned model still carries truncated components")
        _require(row["max_gap"] <= TOLERANCE, f"{name}: cleaned law gap {row['max_gap']} exceeds {TOLERANCE}")
        for label, save in row["saves"].items():
            _require(
                save["state_gap"] <= TOLERANCE and save.get("weight_gap", 0.0) <= TOLERANCE,
                f"{name}: cleaned branch gap at {label}: {save}",
            )
    for name, row in models["raw"]["circuits"].items():
        bound = row["dropped_mass"] / (1.0 - row["dropped_mass"])
        _require(row["max_gap"] <= bound, f"{name}: raw law gap {row['max_gap']} exceeds the truncation bound {bound}")
        first = row["first_dropped"]
        if first is not None and "state_gap_before" in first:
            _require(
                first["state_gap_before"] <= TOLERANCE < first["state_gap_after"],
                f"{name}: the states do not first separate at instruction {first['index']}: {first}",
            )


ALTERNATIVES = [choice for choice in itertools.product((True, False), repeat=3) if choice != (True, True, True)]


def fixture() -> dict[str, Any]:
    """dynamic_density's fixture: the default Semantics within TOLERANCE, each alternative beyond it."""
    source: tuple[Any, ...] = ("fixture",)
    choices = [(True, True, True), *ALTERNATIVES]
    evaluated = _evaluate({"fixture": source}, ("raw",), choices, localize=False)
    runs = evaluated["runs"]["fixture"]["raw"]
    row, oracle_law, _law = _compare_source(source, evaluated["layouts"]["fixture"], runs, "raw")
    _require(row["dropped_mass"] == 0.0, "the fixture carries components Aer truncates")
    _require(row["max_gap"] <= TOLERANCE, f"fixture: default semantics gap {row['max_gap']} exceeds {TOLERANCE}")
    for label, save in row["saves"].items():
        _require(
            save["state_gap"] <= TOLERANCE and save.get("weight_gap", 0.0) <= TOLERANCE,
            f"fixture: gap at {label}: {save}",
        )
    alternatives = []
    for choice in ALTERNATIVES:
        law = runs["dd"][choice][0]
        gap = float(np.max(np.abs(law - oracle_law)))
        named = dict(zip(SEMANTICS_FIELDS, choice, strict=True))
        _require(gap > TOLERANCE, f"fixture: Semantics({named}) agrees with the oracle within {TOLERANCE}")
        alternatives.append({"semantics": named, "max_gap": gap})
    row.pop("first_dropped")
    return {"default": row, "alternatives": alternatives}


def _compare(retained: Any, fresh: Any, where: str, failures: list[str]) -> None:
    """Exact equality for structure, strings, ints and bools; floats within TOLERANCE."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        if sorted(retained) != sorted(fresh):
            failures.append(f"{where}: keys {sorted(retained)} != {sorted(fresh)}")
            return
        for key in retained:
            _compare(retained[key], fresh[key], f"{where}.{key}", failures)
    elif isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            failures.append(f"{where}: length {len(retained)} != {len(fresh)}")
            return
        for position, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            _compare(left, right, f"{where}[{position}]", failures)
    elif isinstance(retained, float) or isinstance(fresh, float):
        if isinstance(retained, bool) or isinstance(fresh, bool) or retained is None or fresh is None:
            failures.append(f"{where}: {retained!r} != {fresh!r}")
        elif abs(float(retained) - float(fresh)) > TOLERANCE:
            failures.append(f"{where}: {retained!r} differs from {fresh!r} by more than {TOLERANCE}")
    elif retained != fresh:
        failures.append(f"{where}: {retained!r} != {fresh!r}")


def _json(record: dict[str, Any]) -> Any:
    return json.loads(json.dumps(record))


def check(path: Path) -> dict[str, Any]:
    retained = json.loads(path.read_text())
    fresh = _json(crosscheck())
    failures: list[str] = []
    _compare(retained["versions"]["qiskit-aer"], fresh["versions"]["qiskit-aer"], "versions.qiskit-aer", failures)
    _compare(
        {k: v for k, v in retained.items() if k != "versions"},
        {k: v for k, v in fresh.items() if k != "versions"},
        "record",
        failures,
    )
    if failures:
        raise SystemExit(f"{path}: recomputation differs:\n" + "\n".join(failures[:40]))
    return fresh


def self_test() -> None:
    result = fixture()
    circuit, noise = _inputs(("fixture",), "raw")
    layout = _layout(circuit)
    runs = {flips: _work(("aer", ("fixture",), "raw", flips)) for flips in _flip_patterns(layout)}
    # Removing the end save of one branch must leave that branch unvisited with its exact weight.
    pruned = {flips: {label: dict(saves) for label, saves in run.items()} for flips, run in runs.items()}
    del pruned[(1,)]["end"][1]
    rebuilt = reconstruct(pruned, layout, noise, circuit.num_clbits)
    missing = [b for b in rebuilt["branches"] if not b["visited"]]
    _require(len(missing) == 1, f"a removed save leaves {len(missing)} unvisited branches")
    weight = _unvisited_weight(rebuilt["branches"], layout["mid"], noise)
    full = reconstruct(runs, layout, noise, circuit.num_clbits)
    expected = next(b["weight"] for b in full["branches"] if b["outcomes"] == [0] and b["recorded"] == [1])
    _require(abs(weight - expected) <= TOLERANCE, f"unvisited weight {weight} != branch weight {expected}")
    twice = QuantumCircuit(1, 2)
    twice.measure(0, 0)
    twice.x(0)
    twice.measure(0, 1)
    twice.x(0)
    try:
        _layout(twice)
    except dynamic_density.UnsupportedCircuit:
        pass
    else:
        raise AssertionError("two mid-circuit measures on one qubit must raise UnsupportedCircuit")
    gaps = ", ".join(f"{alt['max_gap']:.4f}" for alt in result["alternatives"])
    print(
        f"n21 exact crosscheck: fixture default gap {result['default']['max_gap']:.1e} <= {TOLERANCE}; "
        f"seven alternative Semantics at gaps {gaps}; a removed branch refused"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.check is not None:
        record = check(args.check)
    else:
        record = crosscheck()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    for model in ("raw", "cleaned"):
        rows = record["models"][model]
        gaps = {name: row["max_gap"] for name, row in rows["circuits"].items()}
        print(json.dumps({"model": model, "max_gap": gaps, "arms": rows["arms"], "contrasts": rows["contrasts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
