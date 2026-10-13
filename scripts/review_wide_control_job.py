"""Replay the recovered Kingston wide-control acquisition offline.

Exact Gaussian-integer amplitudes bound the ideal calculation to each connected
component. Hardware vectors retain shot order; intervals have marginal scope.
The decoded QPY and indexed raw evidence remain immutable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.quantum_info import Statevector

JOB = "db6qe7klf4us73c5pdc0"
NAMES = ("exp1_ramsey_156q", "exp2_shor_carpet_150q")
SHOTS = 512
Gaussian = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def encode(data: Any) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


@dataclass
class Step:
    operation: Any
    qubits: tuple[int, ...]
    clbits: tuple[int, ...]
    condition: tuple[int, int] | None = None
    blocks: tuple[tuple[Step, ...], ...] = ()


def steps(circuit: QuantumCircuit, qubits: tuple[int, ...], clbits: tuple[int, ...]) -> tuple[Step, ...]:
    result = []
    for instruction in circuit.data:
        operation = instruction.operation
        mapped_qubits = tuple(qubits[circuit.find_bit(bit).index] for bit in instruction.qubits)
        mapped_clbits = tuple(clbits[circuit.find_bit(bit).index] for bit in instruction.clbits)
        require(
            operation.name in {"rz", "sx", "cz", "measure", "reset", "if_else", "barrier"},
            f"Unsupported ideal operation: {operation.name}",
        )
        condition = None
        blocks: tuple[tuple[Step, ...], ...] = ()
        if operation.name == "if_else":
            require(operation.condition[0] in circuit.clbits, "Only a single-Clbit condition is admitted")
            condition = (clbits[circuit.find_bit(operation.condition[0]).index], int(operation.condition[1]))
            require(condition[1] in (0, 1), "Condition must compare one bit to zero or one")
            blocks = tuple(steps(block, mapped_qubits, mapped_clbits) for block in operation.blocks)
        if operation.name == "rz":
            quarter_turns = float(operation.params[0]) / (math.pi / 2)
            require(abs(quarter_turns - round(quarter_turns)) < 1e-12, "RZ angle leaves the exact Clifford domain")
        result.append(Step(operation, mapped_qubits, mapped_clbits, condition, blocks))
    return tuple(result)


def flatten(actions: tuple[Step, ...]) -> list[Step]:
    return [item for step in actions for item in [step, *(item for block in step.blocks for item in flatten(block))]]


def components(circuit: QuantumCircuit, actions: tuple[Step, ...]) -> list[tuple[int, ...]]:
    parents = list(range(circuit.num_qubits))

    def root(qubit: int) -> int:
        while parents[qubit] != qubit:
            qubit = parents[qubit]
        return qubit

    owners: dict[int, set[int]] = {}
    for step in flatten(actions):
        if step.operation.name == "measure":
            require(len(step.qubits) == len(step.clbits) == 1, "Measurement must map one qubit to one bit")
            owners.setdefault(step.clbits[0], set()).add(step.qubits[0])
    for step in flatten(actions):
        if step.operation.name == "barrier":
            continue
        linked = set(step.qubits)
        if step.condition:
            require(step.condition[0] in owners, "Condition has no measurement producer")
            linked.update(owners[step.condition[0]])
        for bit in step.clbits:
            linked.update(owners.get(bit, set()))
        linked_qubits = sorted(linked)
        for qubit in linked_qubits[1:]:
            parents[root(qubit)] = root(linked_qubits[0])
    groups: dict[int, list[int]] = {}
    touched = {qubit for step in flatten(actions) if step.operation.name != "barrier" for qubit in step.qubits}
    for qubit in sorted(touched):
        groups.setdefault(root(qubit), []).append(qubit)
    return sorted((tuple(group) for group in groups.values()), key=lambda group: group[0])


def multiply(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def add(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def projected(state: list[Gaussian], qubit: int, value: int, reset: bool = False) -> list[Gaussian]:
    result = [(0, 0)] * len(state)
    for basis, amplitude in enumerate(state):
        if (basis >> qubit) & 1 == value:
            result[basis ^ ((1 << qubit) if reset and value else 0)] = amplitude
    return result


def exact_law(actions: tuple[Step, ...], component: tuple[int, ...], bits: tuple[int, ...]) -> list[Fraction]:
    require(1 <= len(component) <= 3, "Ideal component exceeds the three-qubit bound")
    local = {qubit: index for index, qubit in enumerate(component)}
    initial = [(0, 0)] * (1 << len(component))
    initial[0] = (1, 0)
    branches: list[Any] = [(initial, 1, {})]

    def execute(sequence: tuple[Step, ...], inputs: list[Any]) -> list[Any]:
        branches = inputs
        for step in sequence:
            name = step.operation.name
            updated = []
            for state, denominator, classical in branches:
                if name == "barrier":
                    updated.append((state, denominator, classical))
                elif name in {"measure", "reset"}:
                    qubit = local[step.qubits[0]]
                    for value in (0, 1):
                        result = projected(state, qubit, value, name == "reset")
                        if any(amplitude != (0, 0) for amplitude in result):
                            memory = dict(classical)
                            if name == "measure":
                                memory[step.clbits[0]] = value
                            updated.append((result, denominator, memory))
                elif name == "if_else":
                    if step.condition is None:
                        raise ValueError("Missing if_else condition")
                    bit, expected = step.condition
                    require(bit in classical, "Conditional bit is read before its measurement")
                    selected = 0 if classical[bit] == expected else 1
                    branch = step.blocks[selected] if selected < len(step.blocks) else ()
                    updated.extend(execute(branch, [(state, denominator, classical)]))
                else:
                    result = list(state)
                    if name == "rz":
                        phase = ((1, 0), (0, 1), (-1, 0), (0, -1))[
                            round(float(step.operation.params[0]) / (math.pi / 2)) % 4
                        ]
                        for basis in range(len(state)):
                            if (basis >> local[step.qubits[0]]) & 1:
                                result[basis] = multiply(state[basis], phase)
                    elif name == "sx":
                        mask = 1 << local[step.qubits[0]]
                        for basis in range(len(state)):
                            result[basis] = add(multiply(state[basis], (1, 1)), multiply(state[basis ^ mask], (1, -1)))
                        denominator *= 2
                    elif name == "cz":
                        for basis in range(len(state)):
                            if all((basis >> local[qubit]) & 1 for qubit in step.qubits):
                                result[basis] = multiply(state[basis], (-1, 0))
                    updated.append((result, denominator, classical))
            branches = updated
            require(len(branches) <= 256, "Ideal branch count exceeds the finite replay bound")
        return branches

    probabilities = [Fraction(0)] * (1 << len(bits))
    for state, denominator, classical in execute(actions, branches):
        require(set(classical) == set(bits), "Final classical bits differ from the component's measurement bits")
        output = sum(classical[bit] << index for index, bit in enumerate(bits))
        probabilities[output] += Fraction(
            sum(real * real + imag * imag for real, imag in state), denominator * denominator
        )
    require(sum(probabilities) == 1, "Exact component probabilities must sum to one")
    return probabilities


def reference_law(actions: tuple[Step, ...], component: tuple[int, ...], bits: tuple[int, ...]) -> list[float]:
    """Cross-check exact arithmetic using Qiskit gates and exhaustive numeric branches."""
    local = {qubit: index for index, qubit in enumerate(component)}
    initial = Statevector.from_int(0, 1 << len(component)).data

    def execute(sequence: tuple[Step, ...], branches: list[Any]) -> list[Any]:
        for step in sequence:
            name = step.operation.name
            updated = []
            for state, classical in branches:
                if name == "barrier":
                    updated.append((state, classical))
                elif name in {"measure", "reset"}:
                    qubit = local[step.qubits[0]]
                    for value in (0, 1):
                        result = np.zeros_like(state)
                        for basis, amplitude in enumerate(state):
                            if (basis >> qubit) & 1 == value:
                                result[basis ^ ((1 << qubit) if name == "reset" and value else 0)] = amplitude
                        if float(np.vdot(result, result).real) > 1e-24:
                            memory = dict(classical)
                            if name == "measure":
                                memory[step.clbits[0]] = value
                            updated.append((result, memory))
                elif name == "if_else":
                    if step.condition is None:
                        raise ValueError("Missing numeric reference condition")
                    bit, expected = step.condition
                    selected = 0 if classical[bit] == expected else 1
                    branch = step.blocks[selected] if selected < len(step.blocks) else ()
                    updated.extend(execute(branch, [(state, classical)]))
                else:
                    evolved = Statevector(state).evolve(step.operation, [local[qubit] for qubit in step.qubits]).data
                    updated.append((evolved, classical))
            branches = updated
        return branches

    probabilities = [0.0] * (1 << len(bits))
    for state, classical in execute(actions, [(initial, {})]):
        output = sum(classical[bit] << index for index, bit in enumerate(bits))
        probabilities[output] += float(np.vdot(state, state).real)
    return probabilities


def statistic(successes: int, trials: int) -> dict[str, Any]:
    require(0 <= successes <= trials and trials > 0, "Binomial statistic leaves its finite domain")
    probability = successes / trials
    z = 1.959963984540054
    denominator = 1 + z * z / trials
    center = (probability + z * z / (2 * trials)) / denominator
    radius = z * math.sqrt(probability * (1 - probability) / trials + z * z / (4 * trials * trials)) / denominator
    return {
        "count": successes,
        "trials": trials,
        "probability": probability,
        "wilson_95_marginal": [max(0.0, center - radius), min(1.0, center + radius)],
    }


def time_summary(vector: list[int]) -> dict[str, Any]:
    half = len(vector) // 2
    earlier, later = vector[:-1], vector[1:]
    mean_earlier, mean_later = sum(earlier) / len(earlier), sum(later) / len(later)
    covariance = (
        sum(left * right for left, right in zip(earlier, later, strict=True)) / len(earlier) - mean_earlier * mean_later
    )
    variance = mean_earlier * (1 - mean_earlier) * mean_later * (1 - mean_later)
    return {
        "first_half": statistic(sum(vector[:half]), half),
        "second_half": statistic(sum(vector[half:]), len(vector) - half),
        "lag1_covariance": covariance,
        "lag1_correlation": covariance / math.sqrt(variance) if variance > 0 else None,
    }


def audit_inputs(run: Path) -> tuple[list[QuantumCircuit], list[list[int]], dict[str, str], dict[str, Any]]:
    retention = read(run / "retention.json")
    submitted = read(run / "submitted-input.json")
    require(
        retention["job_id"] == JOB and retention["backend"] == "ibm_kingston", "Retention job/backend identity differs"
    )
    require(retention["status"] == "DONE" and retention["usage_status"] == "complete", "Job/charge remains unsettled")
    require(
        retention["pub_count"] == 2 and retention["shots_per_pub"] == submitted["shots_per_item"] == SHOTS,
        "Retained PUB or shot denominator differs",
    )
    require(retention["register_bit_widths"] == [[156], [58]], "Retention register widths differ")
    archive = run / submitted["circuit_archive"]
    require(archive == run / "submitted-circuits.qpy", "QPY archive path differs")
    require(digest(archive) == submitted["circuit_archive_sha256"], "QPY digest differs")
    with archive.open("rb") as stream:
        circuits = list(qpy.load(stream))
    require(tuple(circuit.name for circuit in circuits) == NAMES, "QPY PUB order/name differs")
    require(len(submitted["items"]) == len(circuits), "Submitted item denominator differs")
    for circuit, item in zip(circuits, submitted["items"], strict=True):
        require(
            circuit.name == item["name"]
            and circuit.num_qubits == item["num_qubits"]
            and circuit.num_clbits == item["num_clbits"]
            and dict(circuit.count_ops()) == item["operation_counts"],
            "QPY circuit differs from decoded submitted metadata",
        )
        require(
            circuit.num_parameters == 0 and item["circuit_arguments"] == [],
            "Parameterized input is outside this replay",
        )
    directory = run / "raw" / JOB
    index = read(directory / "index.json")
    require(index["job_id"] == JOB, "Raw index job identity differs")
    require(
        set(index["files"]) == {"pub_00.json", "pub_01.json", "result_metadata.json"}, "Indexed PUB denominator differs"
    )
    require(
        retention["raw_index"] == {"directory": f"raw/{JOB}", "files": index["files"]}, "Retention/index join differs"
    )
    require(len(index["metrics"]) == len(index["metrics_sha256"]) > 0, "Metric digest denominator differs")
    require(len(set(index["metrics"])) == len(index["metrics"]), "Metric paths repeat")
    require(index["metrics_latest"] in index["metrics"], "Latest metric escapes the indexed set")
    indexed = dict(index["files"])
    for filename, expected in zip(index["metrics"], index["metrics_sha256"], strict=True):
        require(filename not in indexed, "Metric path aliases a raw PUB")
        indexed[filename] = expected
    require({path.name for path in directory.iterdir()} == {*indexed, "index.json"}, "Raw file denominator differs")
    for filename, expected in indexed.items():
        require(Path(filename).name == filename, "Indexed path escapes the raw directory")
        require(digest(directory / filename) == expected, f"Indexed digest differs: {filename}")
    metrics = read(directory / index["metrics_latest"])
    require(
        metrics["usage"]["status"] == "complete"
        and metrics["usage"]["qpu_charge_time_seconds"] == retention["final_qpu_charge_seconds"] == 2,
        "Final charge differs",
    )
    metadata = read(directory / "result_metadata.json")
    require(
        metadata["shots"] == SHOTS and metadata["options"]["default_shots"] == SHOTS, "Result shot denominator differs"
    )
    values = []
    for pub_index, circuit in enumerate(circuits):
        pub = read(directory / f"pub_{pub_index:02}.json")
        require(pub["pub_index"] == pub_index and pub["pub_name"] == circuit.name, "Raw PUB order/name differs")
        expected = {register.name: register.size for register in circuit.cregs}
        require(expected == {"c": (156, 58)[pub_index]}, "QPY register shape differs")
        require(set(pub["registers"]) == set(expected), "Raw register names differ")
        register = pub["registers"]["c"]
        strings = register["bitstrings"]
        require(
            register["num_bits"] == circuit.num_clbits and register["num_shots"] == len(strings) == SHOTS,
            "Raw width/count differs",
        )
        require(
            isinstance(strings, list)
            and all(
                isinstance(value, str) and len(value) == circuit.num_clbits and set(value) <= {"0", "1"}
                for value in strings
            ),
            "Raw shot bitstring is malformed",
        )
        values.append([int(value, 2) for value in strings])
    sources = [run / "retention.json", run / "submitted-input.json", archive, *sorted(directory.iterdir())]
    hashes = {str(path.relative_to(run)): digest(path) for path in sources}
    return circuits, values, hashes, metrics


def report(run: Path) -> dict[str, Any]:
    circuits, values_by_pub, hashes, metrics = audit_inputs(run)
    pub_rows = []
    for circuit, values in zip(circuits, values_by_pub, strict=True):
        actions = steps(circuit, tuple(range(circuit.num_qubits)), tuple(range(circuit.num_clbits)))
        expanded = flatten(actions)
        active = sorted(
            {qubit for step in expanded if step.operation.name not in {"measure", "barrier"} for qubit in step.qubits}
        )
        measured = sorted({step.qubits[0] for step in expanded if step.operation.name == "measure"})
        spectators = sorted(set(measured) - set(active))
        idle = sorted(set(range(circuit.num_qubits)) - set(active) - set(measured))
        component_rows: list[dict[str, Any]] = []
        vectors: dict[int, list[int]] = {}
        all_bits: list[int] = []
        for component in components(circuit, actions):
            subset = tuple(step for step in actions if any(qubit in component for qubit in step.qubits))
            require(
                all(set(step.qubits) <= set(component) for step in subset), "Component omits an operation dependency"
            )
            bits = tuple(sorted({step.clbits[0] for step in flatten(subset) if step.operation.name == "measure"}))
            all_bits.extend(bits)
            if set(component).isdisjoint(active):
                require(
                    len(component) == len(bits) == len(subset) == 1 and subset[0].operation.name == "measure",
                    "Measurement-only spectator has unexpected operations",
                )
                continue
            probabilities = exact_law(subset, component, bits)
            expected_law = (
                [Fraction(1, 4)] * 4
                if circuit.name == NAMES[0]
                else [Fraction(1, 2), Fraction(1, 4), Fraction(0), Fraction(1, 4)]
            )
            require(probabilities == expected_law, "Recovered component leaves the admitted exact output law")
            reference = reference_law(subset, component, bits)
            discrepancy = max(
                abs(float(exact) - numeric) for exact, numeric in zip(probabilities, reference, strict=True)
            )
            require(discrepancy < 1e-12, "Exact law disagrees with Qiskit Statevector exhaustive branching")
            outcomes = [sum(((value >> bit) & 1) << index for index, bit in enumerate(bits)) for value in values]
            counts = Counter(outcomes)
            error_vector = [int(probabilities[outcome] == 0) for outcome in outcomes]
            key = bits[0] // 2 if circuit.name == NAMES[1] else 0
            vectors[key] = error_vector
            output_width = len(bits)
            labels = [format(outcome, f"0{output_width}b") for outcome in range(1 << output_width)]
            measurements = [
                (step.qubits[0], step.clbits[0]) for step in flatten(subset) if step.operation.name == "measure"
            ]
            component_rows.append(
                {
                    "replica": key,
                    "physical_qubits": list(component),
                    "classical_bits_lsb_first": list(bits),
                    "measurement_sequence": [list(site) for site in measurements],
                    "ideal_probabilities_exact": {
                        label: str(probability) for label, probability in zip(labels, probabilities, strict=True)
                    },
                    "ideal_reference_max_abs_error": discrepancy,
                    "classical_bit_one": [
                        {
                            "classical_bit": bit,
                            **statistic(sum((value >> bit) & 1 for value in values), SHOTS),
                            "shot_order": time_summary([(value >> bit) & 1 for value in values]),
                        }
                        for bit in bits
                    ],
                    "ideal_bit_one_covariance_exact": str(
                        probabilities[3] - (probabilities[1] + probabilities[3]) * (probabilities[2] + probabilities[3])
                    ),
                    "measured_bit_one_covariance": (
                        counts[3] / SHOTS - (counts[1] + counts[3]) / SHOTS * (counts[2] + counts[3]) / SHOTS
                    ),
                    "joint_bit_ones": statistic(
                        sum(all((value >> bit) & 1 for bit in bits) for value in values), SHOTS
                    ),
                    "measured_outcomes": {
                        label: statistic(counts[outcome], SHOTS) for outcome, label in enumerate(labels)
                    },
                    "total_variation_from_ideal": sum(
                        abs(counts[outcome] / SHOTS - float(probabilities[outcome]))
                        for outcome in range(1 << output_width)
                    )
                    / 2,
                    "ideal_support_violations": statistic(sum(error_vector), SHOTS),
                    "support_violation_shot_order": time_summary(error_vector),
                }
            )
        require(
            len(set(all_bits)) == circuit.num_clbits and sorted(all_bits) == list(range(circuit.num_clbits)),
            "Connected components do not partition all output bits",
        )
        spectator_bits = [
            step.clbits[0] for step in expanded if step.operation.name == "measure" and step.qubits[0] in spectators
        ]
        spectator_ones = [sum((value >> bit) & 1 for bit in spectator_bits) for value in values]
        joint_rows = []
        for left, left_vector in sorted(vectors.items()):
            for right, right_vector in sorted(vectors.items()):
                if left >= right:
                    continue
                joint = sum(first * second for first, second in zip(left_vector, right_vector, strict=True))
                covariance = joint / SHOTS - (sum(left_vector) / SHOTS) * (sum(right_vector) / SHOTS)
                variance = (
                    (sum(left_vector) / SHOTS)
                    * (1 - sum(left_vector) / SHOTS)
                    * (sum(right_vector) / SHOTS)
                    * (1 - sum(right_vector) / SHOTS)
                )
                joint_rows.append(
                    {
                        "replicas": [left, right],
                        "joint_support_violations": statistic(joint, SHOTS),
                        "covariance": covariance,
                        "correlation": covariance / math.sqrt(variance) if variance > 0 else None,
                    }
                )
        active_bits = sorted(set(all_bits) - set(spectator_bits))
        active_ones = [sum((value >> bit) & 1 for bit in active_bits) for value in values]
        violation_totals = [sum(vector[index] for vector in vectors.values()) for index in range(SHOTS)]
        pub_rows.append(
            {
                "name": circuit.name,
                "num_qubits": circuit.num_qubits,
                "num_clbits": circuit.num_clbits,
                "resource_partition": {
                    "gate_active_qubits": active,
                    "gate_active_count": len(active),
                    "measured_qubits": measured,
                    "measured_count": len(measured),
                    "measurement_only_spectator_qubits": spectators,
                    "spectator_count": len(spectators),
                    "idle_unmeasured_qubits": idle,
                    "idle_count": len(idle),
                },
                "classical_register_ones_per_shot": {
                    str(count): frequency
                    for count, frequency in sorted(Counter(value.bit_count() for value in values).items())
                },
                "active_output_ones_per_shot": {
                    str(count): frequency for count, frequency in sorted(Counter(active_ones).items())
                },
                "spectators": {
                    "ideal_joint_law": "all measurement-only spectator bits are zero",
                    "all_zero": statistic(sum(count == 0 for count in spectator_ones), SHOTS),
                    "any_one_shot_order": time_summary([int(count > 0) for count in spectator_ones]),
                    "mean_ones_per_shot": sum(spectator_ones) / SHOTS,
                    "ones_per_shot": {
                        str(count): frequency for count, frequency in sorted(Counter(spectator_ones).items())
                    },
                    "per_bit_one": [
                        {"classical_bit": bit, **statistic(sum((value >> bit) & 1 for value in values), SHOTS)}
                        for bit in spectator_bits
                    ],
                },
                "components": sorted(component_rows, key=lambda row: row["replica"]),
                "same_shot_component_support_violations": {
                    "count_histogram": {
                        str(count): frequency for count, frequency in sorted(Counter(violation_totals).items())
                    },
                    "at_least_one": statistic(sum(count > 0 for count in violation_totals), SHOTS),
                    "mean_count": sum(violation_totals) / SHOTS,
                    "pairwise": joint_rows,
                },
            }
        )
    require(
        len(pub_rows[0]["components"]) == 1 and len(pub_rows[1]["components"]) == 29,
        "Active component denominator differs",
    )
    require(
        pub_rows[0]["resource_partition"]["gate_active_count"] == 2
        and pub_rows[1]["resource_partition"]["gate_active_count"] == 87,
        "Active-qubit denominator differs",
    )
    return {
        "schema": "retrospective-wide-control-analysis-v1",
        "job_id": JOB,
        "backend": "ibm_kingston",
        "shots_per_pub": SHOTS,
        "final_qpu_charge_seconds": metrics["usage"]["qpu_charge_time_seconds"],
        "evidence_boundary": "Completed hardware acquisition recovered retrospectively. Original approval, local "
        "pre-submission archive, calibration, and preregistration are unavailable.",
        "statistical_scope": "Wilson 95% intervals are marginal binomial descriptions under independent identical shot "
        "sampling. They are neither simultaneous nor preregistered. Shot drift and shared-resource "
        "dependence remain unmodeled; pairwise statistics describe same-PUB shot vectors. PUB shot "
        "indices are not paired across PUBs.",
        "ideal_scope": "Exact Gaussian-integer amplitudes for the actual decoded QPY circuit, with exhaustive "
        "mid-measurement/reset/Clbit-condition branches. Components contain at most three qubits; "
        "Qiskit Statevector gate evolution independently cross-checks every active component. "
        "Product ideal laws assume ideal isolated components, not measured hardware independence. "
        "Exact RZ phases interpret numeric pi/2 multiples within the checked 1e-12 quarter-turn tolerance.",
        "bit_order": "Raw strings are MSB first; c[0] is the rightmost bit. Component labels use the reversed "
        "listed classical_bits_lsb_first order.",
        "versions": {name: version(name) for name in ("qiskit", "numpy")},
        "replay_source_sha256": digest(Path(__file__)),
        "immutable_source_sha256": hashes,
        "pubs": pub_rows,
    }


def markdown(analysis: dict[str, Any]) -> bytes:
    ramsey, carpet = analysis["pubs"]
    ramsey_component = ramsey["components"][0]
    carpet_violations = carpet["same_shot_component_support_violations"]
    lines = [
        "# Recovered Kingston wide-control job",
        "",
        f"Job `{JOB}` completed on `ibm_kingston` with two PUBs of {SHOTS} shots and a settled 2 s QPU charge.",
        "",
        analysis["evidence_boundary"],
        "Analysis remains retrospective and descriptive.",
        "",
        "## Actual submitted resources and ideal laws",
        "",
        "The replay reads `submitted-circuits.qpy`, validates its recorded digest and decoded item "
        "order, and derives connected components from gate and classical dependencies.",
        "",
        "| PUB | Gate-active qubits | Measured qubits | Measurement-only spectators | Idle "
        "unmeasured qubits | Active components |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for pub in analysis["pubs"]:
        resources = pub["resource_partition"]
        lines.append(
            f"| `{pub['name']}` | {resources['gate_active_count']} | {resources['measured_count']} | "
            f"{resources['spectator_count']} | {resources['idle_count']} | {len(pub['components'])} |"
        )
    lines.extend(
        [
            "",
            "The 156-bit Ramsey register contains 154 zero-state measurement-only spectators and the "
            "outputs from physical qubits 79 and 93. Qubit 93 is measured before reset and again into "
            "c[93]; the final register overwrites the earlier value. A conditional RZ immediately after "
            "reset changes only the reset state's global phase, so that conditional cannot alter the "
            "final output law.",
            "",
            f"Ramsey's ideal active output law is `{ramsey_component['ideal_probabilities_exact']}` in "
            f"c[93]c[79] order. The measured ideal-support violation count is "
            f"{ramsey_component['ideal_support_violations']['count']}/{SHOTS}. All spectator bits are "
            f"zero in {ramsey['spectators']['all_zero']['count']}/{SHOTS} hardware shots. "
            "Ramsey admits all four active outputs, so its zero support-violation count carries "
            "no agreement evidence; total variation measures the active distribution residual.",
            "",
            "The carpet's name includes 150q, while the decoded submitted gates occupy 87 physical "
            "qubits in 29 disconnected three-qubit components. Each component writes two classical "
            "bits. The remaining 69 qubits carry neither gates nor measurements in the decoded QPY; the "
            "backend scheduler's initialization/finalization pulses remain a separate execution "
            "surface. Two replica outputs measure one recycled control qubit before and after "
            "reset/feed-forward; active work qubits remain unmeasured.",
            "",
            "The exact replay keeps Gaussian-integer amplitudes and integer powers of two, branches on "
            "measurement/reset without sampling, executes each classical condition, and sums exact "
            "rational output probabilities. Qiskit Statevector gate evolution cross-checks every "
            "component within 1e-12. The largest state has eight amplitudes; the replay never builds a "
            "156-qubit state.",
            "",
            "## Measured carpet outputs",
            "",
            "Labels list the later bit on the left and the earlier bit on the right. An ideal-support "
            "violation is an observed output whose exact ideal probability is zero; total variation "
            "additionally measures deviations among supported outcomes.",
            "",
            "| Replica | Physical qubits | Classical bits (LSB first) | Exact ideal law | Counts 00, "
            "01, 10, 11 | Support violations | TV |",
            "| ---: | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for component in carpet["components"]:
        counts = ", ".join(str(item["count"]) for item in component["measured_outcomes"].values())
        law = ", ".join(
            f"{label}:{probability}" for label, probability in component["ideal_probabilities_exact"].items()
        )
        lines.append(
            f"| {component['replica']} | {component['physical_qubits']} | "
            f"{component['classical_bits_lsb_first']} | {law} | {counts} | "
            f"{component['ideal_support_violations']['count']}/{SHOTS} | "
            f"{component['total_variation_from_ideal']:.6f} |"
        )
    lines.extend(
        [
            "",
            f"At least one carpet component violates its ideal support in "
            f"{carpet_violations['at_least_one']['count']}/{SHOTS} shared shots; the mean is "
            f"{carpet_violations['mean_count']:.6f} violating components per shot. `analysis.json` "
            f"retains the joint violation histogram, all 406 replica pairs' joint "
            f"counts/covariance/correlation, first/second-half statistics, and lag-one descriptions. "
            f"Those quantities preserve the raw same-PUB shot order. PUB indices identify separate "
            f"executions, so the analysis pairs replicas within the carpet PUB and treats the two PUBs "
            f"separately.",
            "",
            analysis["statistical_scope"],
            "",
            "Hardware errors combine initialization, gates, reset, feedback, and readout. The recovered "
            "archive cannot attribute the observed residuals to one mechanism, establish a "
            "calibration-matched noise prediction, or admit a matched benefit claim. Classical-register "
            "occupancy differs from coherent quantum-resource occupancy; spectator ones describe "
            "zero-state/readout residuals.",
            "",
            "## Offline replay and byte retention",
            "",
            "Run from the repository root with the pinned requirements:",
            "",
            "```sh",
            'PYTHON="${PYTHON:-$(command -v python3)}"',
            'PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/review_wide_control_job.py --check',
            'PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/review_wide_control_job.py --check',
            "(cd results/live/kingston-wide-control-result && sha256sum -c SHA256SUMS)",
            "```",
            "",
            "Generation uses the same command without `--check`. Generation writes only "
            "`analysis.json`, `README.md`, and `SHA256SUMS`. Check mode compares all three derived "
            "files byte for byte and writes stdout. The replay validates every raw-index digest, "
            "metrics digest, PUB order/name, register width, shot count, bit alphabet, measurement-bit "
            "partition, and QPY digest. `SHA256SUMS` records immutable input files and generated "
            "outputs; `analysis.json` binds the replay source digest.",
            "",
            "The self-test checks exact conditional feedback, reset, classical-bit overwrite, and "
            "entanglement laws. Nine copied-fixture mutations exercise raw/QPY/metric digest identity, "
            "PUB order, width, shot count, bit alphabet, shot ordering, and file completeness.",
            "",
            "`retention.json` binds the original retrieval script by digest. That temporary script "
            "contains a local absolute path and remains outside the published bundle. The immutable "
            "decoded inputs and raw files provide the replay inputs. A later retrieval would create a "
            "separately identified acquisition snapshot rather than rewrite these bytes.",
            "",
        ]
    )
    return ("\n".join(lines)).encode()


def generated(run: Path) -> dict[str, bytes]:
    analysis = report(run)
    outputs = {"analysis.json": encode(analysis), "README.md": markdown(analysis)}
    hashes = dict(analysis["immutable_source_sha256"])
    hashes.update({filename: digest_bytes(data) for filename, data in outputs.items()})
    outputs["SHA256SUMS"] = "".join(
        f"{expected}  {filename}\n" for filename, expected in sorted(hashes.items())
    ).encode()
    return outputs


def self_test(run: Path) -> None:
    """Falsify branch semantics and each load-bearing retained-input contract."""

    def hadamard(circuit: QuantumCircuit, qubit: int) -> None:
        circuit.rz(math.pi / 2, qubit)
        circuit.sx(qubit)
        circuit.rz(math.pi / 2, qubit)

    cases = []
    feedback = QuantumCircuit(1, 2)
    hadamard(feedback, 0)
    feedback.measure(0, 0)
    feedback.reset(0)
    with feedback.if_test((feedback.clbits[0], True)):
        feedback.sx(0)
        feedback.sx(0)
    feedback.measure(0, 1)
    cases.append((feedback, [Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1, 2)]))
    reset = QuantumCircuit(1, 2)
    hadamard(reset, 0)
    reset.measure(0, 0)
    reset.reset(0)
    reset.measure(0, 1)
    cases.append((reset, [Fraction(1, 2), Fraction(1, 2), Fraction(0), Fraction(0)]))
    overwrite = QuantumCircuit(1, 1)
    hadamard(overwrite, 0)
    overwrite.measure(0, 0)
    overwrite.reset(0)
    overwrite.measure(0, 0)
    cases.append((overwrite, [Fraction(1), Fraction(0)]))
    entangled = QuantumCircuit(2, 2)
    hadamard(entangled, 0)
    hadamard(entangled, 1)
    entangled.cz(0, 1)
    hadamard(entangled, 1)
    entangled.measure([0, 1], [0, 1])
    cases.append((entangled, [Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1, 2)]))
    for circuit, expected in cases:
        qubits, bits = tuple(range(circuit.num_qubits)), tuple(range(circuit.num_clbits))
        actions = steps(circuit, qubits, bits)
        require(
            exact_law(actions, qubits, bits) == expected, "Exact branch/reset/overwrite/entanglement litmus differs"
        )
        numeric = reference_law(actions, qubits, bits)
        require(
            max(abs(float(exact) - value) for exact, value in zip(expected, numeric, strict=True)) < 1e-12,
            "Numeric litmus differs",
        )
    rejected = QuantumCircuit(1, 1)
    rejected.rz(0.3, 0)
    try:
        steps(rejected, (0,), (0,))
    except ValueError as error:
        require("exact Clifford domain" in str(error), "Unexpected angle rejection reason")
    else:
        raise ValueError("Unsupported RZ angle was accepted")
    mutations = {
        "raw_digest": "Indexed digest differs",
        "qpy_digest": "QPY digest differs",
        "pub_order": "Raw PUB order/name differs",
        "register_width": "Raw width/count differs",
        "shot_count": "Raw width/count differs",
        "bit_alphabet": "Raw shot bitstring is malformed",
        "shot_order": "Indexed digest differs",
        "metric_digest": "Indexed digest differs",
        "missing_pub": "Raw file denominator differs",
    }
    for mutation, reason in mutations.items():
        with tempfile.TemporaryDirectory(prefix="wide-control-replay-falsifier-") as temporary:
            copied = Path(temporary) / "retained"
            shutil.copytree(run, copied, ignore=shutil.ignore_patterns("analysis.json", "README.md", "SHA256SUMS"))
            raw = copied / "raw" / JOB
            pub_path = raw / "pub_00.json"
            if mutation in {"pub_order", "register_width", "shot_count", "bit_alphabet"}:
                pub = read(pub_path)
                if mutation == "pub_order":
                    pub["pub_index"] = 1
                elif mutation == "register_width":
                    pub["registers"]["c"]["num_bits"] = 155
                elif mutation == "shot_count":
                    pub["registers"]["c"]["bitstrings"].pop()
                else:
                    pub["registers"]["c"]["bitstrings"][0] = "x" * 156
                pub_path.write_bytes(encode(pub))
                index = read(raw / "index.json")
                index["files"][pub_path.name] = digest(pub_path)
                (raw / "index.json").write_bytes(encode(index))
                retention = read(copied / "retention.json")
                retention["raw_index"]["files"] = index["files"]
                (copied / "retention.json").write_bytes(encode(retention))
            elif mutation == "raw_digest":
                pub_path.write_bytes(pub_path.read_bytes() + b" ")
            elif mutation == "qpy_digest":
                archive = copied / "submitted-circuits.qpy"
                archive.write_bytes(archive.read_bytes() + b" ")
            elif mutation == "metric_digest":
                metric = raw / "job_metrics.json"
                metric.write_bytes(metric.read_bytes() + b" ")
            elif mutation == "shot_order":
                pub = read(pub_path)
                strings = pub["registers"]["c"]["bitstrings"]
                strings.reverse()
                pub_path.write_bytes(encode(pub))
            else:
                pub_path.unlink()
            try:
                audit_inputs(copied)
            except ValueError as error:
                require(reason in str(error), f"Mutation {mutation} failed for an unexpected reason: {error}")
            else:
                raise ValueError(f"Mutation {mutation} was accepted")
    print("Wide-control falsifiers passed: 4 exact branch litmuses, unsupported-angle rejection, 9 input mutations.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results/live/kingston-wide-control-result",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    run = arguments.run_dir.resolve()
    if arguments.self_test:
        self_test(run)
        return
    outputs = generated(run)
    source_hashes = json.loads(outputs["analysis.json"])["immutable_source_sha256"]
    source_identities = {((run / filename).stat().st_dev, (run / filename).stat().st_ino) for filename in source_hashes}
    output_identities = set()
    for filename in outputs:
        destination = run / filename
        require(destination.resolve().parent == run, "Derived output escapes the retention directory")
        if destination.exists():
            identity = (destination.stat().st_dev, destination.stat().st_ino)
            require(identity not in source_identities, "Derived output aliases immutable evidence")
            require(identity not in output_identities, "Derived outputs alias each other")
            output_identities.add(identity)
    for filename, data in outputs.items():
        destination = run / filename
        if arguments.check:
            require(destination.read_bytes() == data, f"Derived replay differs: {filename}")
        else:
            destination.write_bytes(data)
    require(
        all(digest(run / filename) == expected for filename, expected in source_hashes.items()),
        "Immutable source digest changed during replay",
    )
    print("Wide-control replay verified: 2 PUBs, 512 shots each, 1 two-qubit and 29 three-qubit active components.")


if __name__ == "__main__":
    main()
