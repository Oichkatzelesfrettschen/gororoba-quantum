"""ET family adapter: complete physical controls, fixed allocation, and bound readout roles."""

import copy
import gc
import math
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.exceptions import QiskitError
from qiskit.quantum_info import Operator, Statevector
from qiskit.transpiler import Target

import parallel
from et_campaign import configuration, et_group
from experiments import Group
from packing import Replica


@contextmanager
def bulk_packing() -> Iterator[None]:
    """Collect cyclic Qiskit graphs after a bounded bulk build, preserving the caller's GC policy.

    Repeated whole-heap collections while adding thousands of independent
    packed circuits rescan retained circuit graphs quadratically. Reference
    counting remains active throughout the build; cyclic collection resumes
    at the boundary, including exceptional exits.
    """
    enabled = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if enabled:
            gc.enable()
            gc.collect()


def measurement_map(circuit: QuantumCircuit) -> list[int]:
    writers: dict[int, int] = {}
    for instruction in circuit.data:
        if instruction.operation.name == "measure":
            classical = circuit.find_bit(instruction.clbits[0]).index
            if classical in writers:
                raise ValueError("ET acquisitions require one terminal writer per classical bit")
            writers[classical] = circuit.find_bit(instruction.qubits[0]).index
    if set(writers) != set(range(6)) or len(set(writers.values())) != 6:
        raise ValueError("ET acquisition must retain all six distinct measured roles")
    return [writers[index] for index in range(6)]


def native_signature(circuit: QuantumCircuit) -> tuple:
    """Native probability programs ignore register spelling but retain wire/bit roles and angles."""
    return (
        circuit.num_qubits,
        circuit.num_clbits,
        tuple(
            (
                instruction.operation.name,
                tuple(map(str, instruction.operation.params)),
                tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits),
                tuple(circuit.find_bit(bit).index for bit in instruction.clbits),
            )
            for instruction in circuit.data
        ),
    )


def terminal_probabilities(circuit: QuantumCircuit) -> np.ndarray:
    """Evaluate the static six-wire acquisition without enumerating measurement branches."""
    writers = measurement_map(circuit)
    positions = {physical: bit for bit, physical in enumerate(sorted(writers))}
    compact = QuantumCircuit(6)
    compact.global_phase = circuit.global_phase
    measuring = False
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name in ("barrier", "delay"):
            continue
        if operation.name == "measure":
            measuring = True
            continue
        if measuring or instruction.clbits or operation.name == "reset" or hasattr(operation, "blocks"):
            raise ValueError("ET static law requires only terminal measurements")
        physical = [circuit.find_bit(qubit).index for qubit in instruction.qubits]
        if any(qubit not in positions for qubit in physical):
            raise ValueError("ET static law exceeds its six measured wires")
        compact.append(operation, [positions[qubit] for qubit in physical])
    probabilities = Statevector.from_instruction(compact).probabilities()
    rows = [
        sum(((outcome >> bit) & 1) << positions[physical] for bit, physical in enumerate(writers))
        for outcome in range(64)
    ]
    return probabilities[rows]


def validate_ideals(choice: Any) -> None:
    """Check every member law while evaluating independent identical programs only once."""
    programs: dict[tuple, QuantumCircuit] = {}
    for entry in choice.entries:
        for replica in entry.replicas:
            programs.setdefault(native_signature(replica), replica)
    signatures = list(programs)
    with bulk_packing():
        laws = parallel.ordered_map(terminal_probabilities, list(programs.values()), min_items=2)
    references = dict(zip(signatures, laws, strict=True))
    for entry in choice.entries:
        for replica in entry.replicas:
            if not np.allclose(references[native_signature(replica)], entry.ideal, rtol=0, atol=1e-10):
                raise ValueError(f"{entry.name}: compiled labeled ideal differs from its exact oracle")


def operator_error(native: QuantumCircuit, logical: QuantumCircuit, layout: list[int]) -> float:
    """Compare arbitrary inputs on six active wires, retaining actual output permutations and phase."""
    indices = {physical: logical_bit for logical_bit, physical in enumerate(layout)}
    unitary = native.remove_final_measurements(inplace=False)
    compact = QuantumCircuit(6)
    compact.global_phase = unitary.global_phase
    for instruction in unitary.data:
        if instruction.operation.name == "barrier":
            continue
        if instruction.clbits or any(native.find_bit(qubit).index not in indices for qubit in instruction.qubits):
            raise ValueError("ET full operator must stay on its six declared wires")
        compact.append(instruction.operation, [indices[native.find_bit(qubit).index] for qubit in instruction.qubits])
    writers = measurement_map(native)
    rows = [
        sum(((outcome >> bit) & 1) << indices[physical] for bit, physical in enumerate(writers))
        for outcome in range(64)
    ]
    return float(
        np.max(abs(Operator(compact).data[rows] - Operator(logical.remove_final_measurements(inplace=False)).data))
    )


def _operator_job(arguments: tuple[QuantumCircuit, QuantumCircuit, list[int]]) -> float:
    return operator_error(*arguments)


def bind_controls(choice: Any, definition: dict[str, Any], runtime: Any) -> None:
    """Cut the actual native decoder suffix and prepare controls on its physical input wires."""
    metadata = definition["members"]
    sources: dict[tuple, QuantumCircuit] = {}
    for member, circuit in zip(choice.group.members, choice.isas, strict=True):
        item = metadata[member.name]
        if item["kind"] == "signal":
            sources.setdefault((tuple(item["spec"]), item["block"], item["basis"]), circuit)
    bound_cache = {}
    maps = {}
    for index, member in enumerate(choice.group.members):
        item = metadata[member.name]
        source = sources[(tuple(item["spec"]), item["block"], item["basis"])]
        writers = measurement_map(source)
        if item["kind"] in ("readout", "decoder"):
            cache_key = (
                id(source),
                item["kind"],
                tuple((key, item.get(key)) for key in ("value", "sector", "column", "bit", "phase")),
            )
            if cache_key not in bound_cache:
                control = QuantumCircuit(source.num_qubits, 6)
                if item["kind"] == "readout":
                    for bit, physical in enumerate(writers):
                        if item["value"] & (1 << bit):
                            control.x(physical)
                    control.measure(writers, range(6))
                else:
                    barriers = [
                        position
                        for position, instruction in enumerate(source.data)
                        if instruction.operation.name == "barrier"
                    ]
                    if len(barriers) != 1:
                        raise ValueError("ET native circuit must preserve its single decoder boundary")
                    cut = barriers[0]
                    inputs = [source.find_bit(qubit).index for qubit in source.data[cut].qubits]
                    if len(inputs) != 6:
                        raise ValueError("ET decoder barrier must identify all six logical input wires")
                    value = item["sector"] * 16 + item["column"]
                    for bit, physical in enumerate(inputs):
                        if value & (1 << bit):
                            control.x(physical)
                    if item["bit"] >= 0:
                        physical = inputs[item["bit"]]
                        # H = Rz(pi/2) SX Rz(pi/2), up to a retained global phase.
                        control.rz(math.pi / 2, physical)
                        control.sx(physical)
                        control.rz(math.pi / 2, physical)
                        control.global_phase += math.pi / 4
                        if item["phase"]:
                            control.rz(math.pi, physical)
                            control.global_phase += math.pi / 2
                    for instruction in source.data[cut:]:
                        control.append(
                            instruction.operation,
                            [source.find_bit(qubit).index for qubit in instruction.qubits],
                            [source.find_bit(bit).index for bit in instruction.clbits],
                        )
                control.metadata = dict(source.metadata or {})
                violations = runtime.target_violations(control, choice.snap.backend.target)
                if violations:
                    raise ValueError(f"ET native control violates Target: {violations}")
                bound_cache[cache_key] = control
            choice.isas[index] = bound_cache[cache_key].copy(name=member.name)
        circuit = choice.isas[index]
        actual = measurement_map(circuit)
        if actual != writers:
            raise ValueError(f"{member.name}: phase/null/control member changed final role sites")
        maps[member.name] = {
            "initial_physical": list(choice.layout),
            "classical_to_final_physical": actual,
            "column_clbits": [0, 1, 2, 3],
            "high_clbit": 4,
            "selector_clbit": 5,
        }
    definition["measurement_maps"] = maps


def family_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    if args.max_replicas not in (None, 1) or args.replica_tiers != [1]:
        raise runtime.LiveRunError("et-row requires one replica and --replica-tiers 1")
    definition = configuration()
    group = et_group(definition)
    candidates = []
    for snapshot in snapshots:
        try:
            print(f"et-row: searching six-wire placements on {snapshot.name}", flush=True)
            primary = Group("et_row_placement", (group.members[0],), lambda _: {})
            routed = runtime.select_candidates(primary, [snapshot], args.seeds, trace)
            for choice in routed[: args.optimizer_candidates]:
                config = copy.deepcopy(definition)
                # Restrict native routing to the chosen six-wire region. Extra
                # routing ancillas would change the declared acquisition width.
                target = snapshot.admission_target or snapshot.backend.target
                restricted = Target(
                    num_qubits=target.num_qubits,
                    dt=target.dt,
                    qubit_properties=target.qubit_properties,
                    granularity=target.granularity,
                    pulse_alignment=target.pulse_alignment,
                    acquire_alignment=target.acquire_alignment,
                    min_length=target.min_length,
                )
                for operation in target.operation_names:
                    properties = {
                        qargs: props
                        for qargs, props in target[operation].items()
                        if qargs is not None and set(qargs) <= set(choice.layout)
                    }
                    if properties:
                        restricted.add_instruction(target.operation_from_name(operation), properties, name=operation)
                local_snapshot = copy.copy(snapshot)
                local_snapshot.admission_target = restricted
                templates = {}
                isas = []
                checked = set()
                operator_jobs = []
                for member in group.members:
                    if config["members"][member.name]["kind"] in ("signal", "dephased"):
                        if id(member.circuit) not in templates:
                            templates[id(member.circuit)] = runtime._compile(
                                member.circuit, local_snapshot, choice.seed, choice.layout
                            )
                        native = runtime._bind(templates[id(member.circuit)], member)
                        binding_key = (
                            id(member.circuit),
                            tuple((str(key), value) for key, value in (member.binding or {}).items()),
                        )
                        if binding_key not in checked:
                            logical = member.circuit.assign_parameters(member.binding or {})
                            operator_jobs.append((native, logical, choice.layout))
                            checked.add(binding_key)
                        isas.append(native)
                    else:
                        # bind_controls replaces every control with an actual
                        # native readout or decoder twin before ISA admission.
                        isas.append(isas[0])
                operator_errors = parallel.ordered_map(_operator_job, operator_jobs, min_items=2)
                if max(operator_errors) > 1e-10:
                    raise ValueError(f"native arbitrary-input error {max(operator_errors)}")
                choice.group = group
                choice.isas = isas
                bind_controls(choice, config, runtime)
                print(f"et-row: {snapshot.name} layout {choice.layout}, {len(choice.isas)} native members", flush=True)
                scores = [runtime.layout_score(circuit, snapshot.backend.target) for circuit in choice.isas]
                if any(score <= 0 or not math.isfinite(score) for score in scores):
                    raise ValueError("ET candidate has an invalid native quality proxy")
                choice.member_scores = scores
                choice.joint_score = min(scores)
                used = sorted({qubit for circuit in choice.isas for qubit in runtime._physical(circuit)})
                with bulk_packing():
                    runtime._set_entries(
                        choice,
                        [Replica(0, {qubit: qubit for qubit in used}, min(scores))],
                        runtime.ReplicaPolicy(args.replica_floor, 1, False, True),
                    )
                config["dt_seconds"] = snapshot.backend.target.dt
                config["native_operator_check"] = {"bindings": len(checked), "max_error": max(operator_errors)}
                config["placement_contract"] = (
                    "one physical placement; per-member final role maps and native suffix twins"
                )
                candidates.append(([choice], config))
        except (QiskitError, ValueError, runtime.LiveRunError) as error:
            trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
    return candidates


def simulate(runtime: Any, choice: Any, simulator: Any, shots: int) -> dict:
    """Reuse identical modeled native circuits across blocks; measured shots remain distinct."""
    signatures, aliases, unique = {}, {}, []
    for entry in choice.entries:
        signature = native_signature(entry.packed)
        if signature not in signatures:
            signatures[signature] = entry.name
            unique.append(entry)
        aliases[entry.name] = signatures[signature]
    print(f"et-row: model {len(unique)} distinct native programs for {len(choice.entries)} entries", flush=True)
    modeled = runtime.simulate_entries(simulator, unique, shots, runtime.SEED_SIMULATOR)
    return {name: modeled[source] for name, source in aliases.items()}


def calibrated_design(config: dict[str, Any], predictions: dict) -> dict[str, Any]:
    """Apply the collector's calibrated rule at the actual allocation to plug-in model counts."""
    from et_statistics import analyze

    observations = {}
    for name, item in config["members"].items():
        law = np.asarray(predictions[name][0], dtype=float)
        expected = law * item["shots"]
        counts = np.floor(expected).astype(int)
        remainder = item["shots"] - int(counts.sum())
        if remainder < 0 or remainder > 64:
            raise ValueError("ET model law is not normalized")
        counts[np.argsort(-(expected - counts), kind="stable")[:remainder]] += 1
        observations[name] = {"counts": counts.tolist(), "shots": item["shots"]}
    result = analyze(config, observations, {name: {"validated": True} for name in observations})
    return {key: result[key] for key in ("admitted", "withheld", "endpoints", "assumption")} | {
        "method": (
            "plug-in model histograms at declared allocation; additional feasibility screen, not a power guarantee"
        )
    }


def fixed_allocations(plans: tuple, ownership: dict, runtime: Any) -> tuple[tuple, dict]:
    from pub_shot_allocation import _tier_plan

    allocated, audits = [], {}
    for plan in plans:
        choices, config, _shots = ownership[plan.name]
        allocation = {}
        for pub in runtime.execution_pubs(choices):
            if len(pub.components) != 1:
                raise ValueError("ET allocation prohibits implicit fusion of scientific members")
            allocation[pub.name] = config["members"][pub.components[0].entry.name]["shots"]
        allocated.append(_tier_plan(plan, allocation, plan.name))
        audits[plan.name] = {
            "pub_shots": allocation,
            "method": "complete preregistered ET acquisition",
            "total_executions": sum(allocation.values()),
        }
    return tuple(allocated), audits


def collected(
    record: dict[str, Any], evidence: list[dict[str, Any]] | None, executed: dict[str, Any], runtime: Any
) -> dict[str, Any]:
    from et_statistics import analyze

    config = record["family_configuration"]
    required = list(config["members"])
    if set(executed) != set(required):
        return {"admitted": False, "withheld": "ET collection needs every declared signal and physical control"}
    reason = runtime._comparisons_withheld(required, executed)
    if reason:
        return {"admitted": False, "withheld": reason}
    observations = {}
    for item in evidence or []:
        name = item["name"]
        if name in observations or name not in config["members"]:
            raise ValueError("duplicate or unknown ET raw histogram")
        histogram = [0] * 64
        for bits, count in item["counts"].items():
            index = int(bits.replace(" ", ""), 2)
            if index >= 64:
                raise ValueError("ET raw outcome exceeds six bits")
            histogram[index] += count
        expected = config["members"][name]["shots"]
        if sum(histogram) != expected or executed[name].get("shots") != expected:
            raise ValueError("ET measured denominator differs from its declared allocation")
        observations[name] = {"counts": histogram, "shots": expected}
    maps = config.get("measurement_maps", {})
    contexts = {
        name: {"validated": name in maps and item.get("measurement_map") == maps[name]}
        for name, item in ((item["name"], item) for item in evidence or [])
    }
    return analyze(config, observations, contexts)
