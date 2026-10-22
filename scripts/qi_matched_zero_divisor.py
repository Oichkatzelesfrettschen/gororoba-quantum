"""Generate a local Tuna-17 matched-response proposal without provider calls.

One symbolic circuit per region fixes routing before binding the dark, bright
and same-support quadrature fixture. The only varying instruction is a nonzero
Rz angle. The source, retained catalogue and emitted circuit digests belong to
the written case; a later submission requires separate user approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import warnings
from collections.abc import Sequence
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_zero_divisor_cases import (  # noqa: E402
    A_PAIR,
    BASIS,
    CATALOGUE,
    CQASM,
    DATA,
    REGIONS,
    ROTATION,
    SELECTOR,
    TUNA17,
    catalogue_backends,
    header,
    readout_circuits,
    select_exact,
)

import parallel  # noqa: E402
import qi_stack  # noqa: E402
from cd_core import cd_multiply_exact  # noqa: E402

CATALOGUE_SHA256 = "1b978cf3518149cd72886865bffb971ab0c359ae5a7a993cb5f51b230159cd78"
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response"
ANGLES = {"dark": math.pi / 2, "bright": -math.pi / 2, "fixture": math.pi}
IDEALS = {"dark": 0.0, "bright": 1.0, "fixture": 0.5}
SHOTS = 16384
TOOLCHAIN_RECORD = ROOT / "docs/evidence/quantum_inspire/matched-zero-divisor-toolchain-admission-closure.json"
COMPILER_SOURCES = (
    "scripts/qi_matched_zero_divisor.py",
    "scripts/qi_toolchain_check.py",
    "scripts/qi_zero_divisor_cases.py",
    "scripts/qi_platform.py",
    "gororoba_quantum/qi_stack.py",
    "gororoba_quantum/parallel.py",
)


def matched_response_contrast(
    probabilities: Sequence[float], covariance: Sequence[Sequence[float]]
) -> dict[str, float]:
    """Within-batch difference of half-spacings, cancelling batch and region offsets.

    Order: (dark R1, bright R2), (bright R1, fixture R2),
    (fixture R1, dark R2). The contrast is F2-B1+F1-D2, or twice H
    when offsets are common. Covariance includes same-shot dependence and
    shared calibration uncertainty, with independent acquired batches.
    """
    values = np.asarray(probabilities, dtype=float)
    matrix = np.asarray(covariance, dtype=float)
    if values.shape != (6,) or matrix.shape != (6, 6) or not np.isfinite(values).all() or not np.isfinite(matrix).all():
        raise ValueError("matched response needs six finite probabilities and a finite 6 by 6 covariance")
    if not np.allclose(matrix, matrix.T, rtol=0, atol=1e-12):
        raise ValueError("matched covariance must be symmetric")
    if float(np.linalg.eigvalsh(matrix).min()) < -1e-12:
        raise ValueError("matched covariance must be positive semidefinite")
    weights = np.asarray([0, 0, -1, 1, 1, -1], dtype=float)
    residual = float(weights @ values)
    variance = float(weights @ matrix @ weights)
    if variance <= 0:
        raise ValueError("matched contrast requires positive sampling variance")
    standard_error = math.sqrt(variance)
    return {"residual": residual, "standard_error": standard_error, "z": residual / standard_error}


def _route_region(region: tuple[int, ...]) -> tuple[Any, dict[str, int], Any]:
    from qiskit import QuantumCircuit, transpile
    from qiskit.circuit import Parameter
    from qiskit.transpiler import CouplingMap

    phase = Parameter("relative_phase_after_S")
    circuit = QuantumCircuit(5)
    circuit.h(0)
    circuit.s(0)
    circuit.rz(phase, 0)
    for bit in (1, 3):
        circuit.cx(0, bit)
    circuit.x(2)
    circuit.h(SELECTOR)
    circuit.compose(select_exact(*A_PAIR), range(5), inplace=True)
    circuit.h(SELECTOR)
    local = {qubit: index for index, qubit in enumerate(region)}
    edges = [[local[first], local[second]] for first, second in TUNA17 if first in local and second in local]
    routed = transpile(
        circuit,
        coupling_map=CouplingMap(edges + [edge[::-1] for edge in edges]),
        basis_gates=[*BASIS, "rz"],
        optimization_level=0,
        seed_transpiler=11,
        layout_method="trivial",
        routing_method="sabre",
    )
    final = routed.layout.final_index_layout()
    roles = {f"d{bit}": region[final[bit]] for bit in DATA}
    roles["selector"] = region[final[SELECTOR]]
    return routed, roles, phase


def _emit(circuit: Any, region: tuple[int, ...]) -> tuple[list[str], list[tuple[str, tuple[int, ...]]]]:
    lines = []
    shape = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = tuple(region[circuit.find_bit(qubit).index] for qubit in instruction.qubits)
        if name == "barrier":
            continue
        if name == "rz":
            angle = float(instruction.operation.params[0])
            if abs(angle / (math.pi / 36) - round(angle / (math.pi / 36))) > 1e-10 or angle == 0:
                raise ValueError("matched phase must be a nonzero native grid angle")
            lines.append(f"Rz({angle:.15f}) q[{qubits[0]}]")
        elif name == "cz":
            lines.append(f"CZ q[{qubits[0]}], q[{qubits[1]}]")
        elif name in CQASM:
            lines.append(f"{CQASM[name]} q[{qubits[0]}]")
        else:
            raise ValueError(f"matched circuit contains unsupported instruction {name}")
        shape.append((name, qubits))
    return lines, shape


def _exact_ideals() -> dict[str, float]:
    operand = [int(index in A_PAIR) for index in range(16)]
    result = {}
    for case, sign in (("dark", -1), ("bright", 1), ("fixture", 0)):
        real = [int(index == 4) + sign * int(index == 15) for index in range(16)]
        imaginary = [-int(index == 15) if case == "fixture" else 0 for index in range(16)]
        product_real = cd_multiply_exact(16, operand, real)
        product_imaginary = cd_multiply_exact(16, operand, imaginary)
        result[case] = float(sum(value**2 for value in (*product_real, *product_imaginary)) / 8)
    return result


def build() -> dict[str, str]:
    from qiskit.quantum_info import Statevector

    catalogue = CATALOGUE.read_bytes()
    if hashlib.sha256(catalogue).hexdigest() != CATALOGUE_SHA256:
        raise ValueError("the matched proposal requires review of its changed retained catalogue")
    catalogue_backends(json.loads(catalogue))
    if _exact_ideals() != IDEALS:
        raise ValueError("the exact split-real certificate differs from the matched ideals")
    routed_regions = parallel.ordered_map(_route_region, list(REGIONS), min_items=1)
    rows = []
    region_lines: dict[tuple[int, str], list[str]] = {}
    for region_index, (region, (routed, roles, phase)) in enumerate(zip(REGIONS, routed_regions, strict=True)):
        first_shape = None
        probabilities = {}
        for case, angle in ANGLES.items():
            circuit = routed.assign_parameters({phase: angle})
            lines, shape = _emit(circuit, region)
            if first_shape is not None and shape != first_shape:
                raise ValueError("matched cases differ in routed gate locations or timing shape")
            first_shape = shape
            selector = region.index(roles["selector"])
            probability = float(Statevector(circuit).probabilities([selector])[0])
            if abs(probability - IDEALS[case]) > 1e-10:
                raise ValueError(f"{case}: matched routed ideal probability is {probability}")
            probabilities[case] = IDEALS[case]
            region_lines[region_index, case] = lines
        rows.append(
            {
                "qubits": list(region),
                "roles": roles,
                "case_shapes_equal": True,
                "ideal_probabilities": probabilities,
                "cz": sum(name == "cz" for name, _ in first_shape or []),
                "t": sum(name in {"t", "tdg"} for name, _ in first_shape or []),
            }
        )
    files = {}
    for batch, assignment in enumerate(ROTATION):
        prefix = f"batch-{batch:02d}"
        witness = header(17) + ["init q", "barrier q"]
        for region_index, case in enumerate(assignment):
            witness += region_lines[region_index, case]
        witness += ["barrier q", "b = measure q", ""]
        texts = {"witness.cq": "\n".join(witness), **readout_circuits(17)}
        for name, text in texts.items():
            files[f"{prefix}/{name}"] = text
        manifest = {
            "schema": "qi-matched-zero-divisor-cases-v1",
            "backend": "tuna_17",
            "backend_type_id": 7,
            "shots": SHOTS,
            "batch": prefix,
            "circuits": [
                {"file": name, "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in texts.items()
            ],
            "replicas": [{"case": case, **rows[index]} for index, case in enumerate(assignment)],
            "catalogue_sha256": CATALOGUE_SHA256,
            "provider_execution_authorized": False,
        }
        files[f"{prefix}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
    proposal = {
        "schema": "qi-matched-zero-divisor-proposal-v1",
        "backend": "tuna_17",
        "jobs": 9,
        "shots_per_job": SHOTS,
        "total_shots": 9 * SHOTS,
        "expected_device_seconds": 9 * (2_600_000 + 530 * SHOTS) / 1_000_000,
        "minimum_pause_per_interbatch_seconds": 120,
        "minimum_total_interbatch_pause_seconds": 240,
        "expected_metered_credits": 0,
        "budget_basis": "retained 2.6 seconds fixed overhead plus 0.53 ms per shot; refresh before approval",
        "provider_execution_authorized": False,
        "catalogue_sha256": CATALOGUE_SHA256,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "regions": rows,
        "batches": [f"batch-{batch:02d}" for batch in range(3)],
        "primary_contrast": {
            "order": ["D_R1_b0", "B_R2_b0", "B_R1_b1", "F_R2_b1", "F_R1_b2", "D_R2_b2"],
            "weights": [0, 0, -1, 1, 1, -1],
            "rejection": "abs(z)>=3",
            "null": "batch offsets plus one fixed region offset and a common affine response",
        },
        "fixture": "(e4 - i e15)/sqrt2; same-support complex-linear quadrature control",
        "timing_boundary": (
            "identical emitted gate sequence and locations per region; "
            "provider physical scheduling remains a separate admission check"
        ),
    }
    files["proposal.json"] = json.dumps(proposal, indent=1) + "\n"
    files["cases.json"] = (
        json.dumps({"schema": "qi-matched-zero-divisor-series-v1", "batches": proposal["batches"]}, indent=1) + "\n"
    )
    return files


def _wire_operations(text: str) -> list[list[tuple[str, tuple[int, ...], float | None]]]:
    """Preserve partners and control ordering while allowing disjoint-wire scheduling."""
    wires: list[list[tuple[str, tuple[int, ...], float | None]]] = [[] for _ in range(17)]
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line in {"version 3.0", "qubit[17] q", "bit[17] b"}:
            continue
        measurement = re.fullmatch(r"b(?:\[(\d+)\])? = measure q(?:\[(\d+)\])?", line)
        if measurement:
            if measurement[1] is None and measurement[2] is None:
                for qubit in range(17):
                    wires[qubit].append(("measure", (qubit,), None))
            elif measurement[1] is not None and measurement[2] is not None:
                wires[int(measurement[2])].append(("measure", (int(measurement[1]),), None))
            else:
                raise ValueError("unsupported measurement operands")
            continue
        operation = re.fullmatch(r"(\w+)(?:\(([^)]+)\))? (q(?:\[\d+\])?(?:, q\[\d+\])?)", line)
        if operation is None:
            raise ValueError(f"unsupported compiler instruction: {line}")
        name, angle, operands = operation.groups()
        targets = tuple(int(value) for value in re.findall(r"\[(\d+)\]", operands))
        if operands == "q":
            if name not in {"init", "barrier"} or angle is not None:
                raise ValueError("unsupported register-wide operation")
            for qubit in range(17):
                wires[qubit].append((name, (), None))
            continue
        if any(qubit >= 17 for qubit in targets):
            raise ValueError("compiler operand outside the 17-qubit register")
        signature: tuple[str, tuple[int, ...], float | None]
        if name == "CZ":
            if len(targets) != 2 or len(set(targets)) != 2 or angle is not None:
                raise ValueError("invalid controlled-Z operands")
            signature = (name, tuple(sorted(targets)), None)
        else:
            if len(targets) != 1 or (angle is not None) != (name == "Rz"):
                raise ValueError("invalid single-wire operands")
            signature = (name, (), float(angle) if angle is not None else None)
        for qubit in targets:
            wires[qubit].append(signature)
    return wires


def _compiler_angle_error(source: str, compiled: str) -> float:
    errors = []
    for original_row, compiled_row in zip(_wire_operations(source), _wire_operations(compiled), strict=True):
        if len(original_row) != len(compiled_row):
            raise ValueError("compiler changed per-wire operation count")
        for original, emitted in zip(original_row, compiled_row, strict=True):
            if original[:2] != emitted[:2]:
                raise ValueError("compiler changed operands or per-wire control/gate ordering")
            if original[2] is not None and emitted[2] is not None:
                error = abs(original[2] - emitted[2])
                if not math.isfinite(error) or error > 5e-8:
                    raise ValueError("compiler angle error exceeds serialization bound")
                errors.append(error)
    return max(errors, default=0.0)


def _check_toolchain(item: tuple[str, str]) -> dict[str, Any]:
    from qi_toolchain_check import compile_circuit

    warnings.filterwarnings("ignore", r"builtin type \w+ has no __module__ attribute", DeprecationWarning)
    import cqasm.v3x as v3

    name, text = item
    analysis = json.loads(v3.Analyzer().analyze_string_to_json(text), strict=False)
    if analysis.get("errors"):
        raise ValueError(f"matched proposal cQASM analysis failed for {name}: {analysis['errors']}")
    catalogue = json.loads(CATALOGUE.read_text())
    backend, _ = catalogue_backends(catalogue)
    compiled = compile_circuit(text, backend["default_compiler_config"])
    angle_error = _compiler_angle_error(text, compiled)
    return {
        "file": name,
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "compiled_sha256": hashlib.sha256(compiled.encode()).hexdigest(),
        "maximum_angle_serialization_error": angle_error,
        "operand_control_order_preserved": True,
    }


def toolchain_record(directory: Path) -> dict[str, Any]:
    items = [(path.relative_to(directory).as_posix(), path.read_text()) for path in sorted(directory.rglob("*.cq"))]
    if len(items) != 9:
        raise ValueError("matched toolchain check requires exactly nine circuit files")
    return {
        "schema": "qi-matched-zero-divisor-toolchain-v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "producer_sources_sha256": compiler_sources(),
        "catalogue_sha256": CATALOGUE_SHA256,
        "toolchain": {name: version(name) for name in qi_stack.DISTRIBUTIONS},
        "circuits": parallel.ordered_map(_check_toolchain, items, min_items=1),
    }


def compiler_sources() -> dict[str, str]:
    """Bind the executed compiler, catalogue admission, stack adapter and pool drivers."""
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in COMPILER_SOURCES}


def validate_toolchain_record(directory: Path, record: dict[str, Any]) -> None:
    if record.get("schema") != "qi-matched-zero-divisor-toolchain-v1":
        raise ValueError("matched toolchain receipt schema differs")
    if record.get("source_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise ValueError("matched toolchain receipt producer source differs")
    if record.get("producer_sources_sha256") != compiler_sources():
        raise ValueError("matched toolchain receipt producer dependency sources differ")
    if record.get("catalogue_sha256") != hashlib.sha256(CATALOGUE.read_bytes()).hexdigest():
        raise ValueError("matched toolchain receipt catalogue differs")
    if record.get("toolchain") != qi_stack.pins():
        raise ValueError("matched toolchain receipt versions differ from the locked stack")
    expected = {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*.cq")
    }
    rows = record.get("circuits")
    if len(expected) != 9 or not isinstance(rows, list) or len(rows) != 9:
        raise ValueError("matched toolchain receipt requires nine circuit rows")
    observed = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "file",
            "source_sha256",
            "compiled_sha256",
            "maximum_angle_serialization_error",
            "operand_control_order_preserved",
        }:
            raise ValueError("matched toolchain receipt row shape differs")
        name = row["file"]
        if not isinstance(name, str) or name in observed:
            raise ValueError("matched toolchain receipt repeats a circuit")
        observed[name] = row["source_sha256"]
        error = row["maximum_angle_serialization_error"]
        if (
            row["operand_control_order_preserved"] is not True
            or not isinstance(row["compiled_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", row["compiled_sha256"])
            or isinstance(error, bool)
            or not isinstance(error, int | float)
            or not math.isfinite(error)
            or not 0 <= error <= 5e-8
        ):
            raise ValueError("matched toolchain receipt contains a failed compiler comparison")
    if observed != expected:
        raise ValueError("matched toolchain receipt circuit bytes differ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--check-toolchain", type=Path)
    mode.add_argument("--write-toolchain", type=Path)
    mode.add_argument("--emit-toolchain", type=Path)
    parser.add_argument("--toolchain-record", type=Path, default=TOOLCHAIN_RECORD)
    arguments = parser.parse_args()
    if arguments.emit_toolchain or arguments.write_toolchain:
        directory = arguments.emit_toolchain or arguments.write_toolchain
        rendered = json.dumps(toolchain_record(directory), indent=1) + "\n"
        if arguments.emit_toolchain:
            print(rendered, end="")
        else:
            destination = arguments.toolchain_record
            if destination.exists() and destination.read_text() != rendered:
                raise ValueError("retain a separately named matched toolchain successor")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered)
        return 0
    if arguments.check_toolchain:
        record = json.loads(arguments.toolchain_record.read_text())
        validate_toolchain_record(arguments.check_toolchain, record)
        if qi_stack.live("matched compiler", "checked the retained operand/control-order receipt"):
            rebuilt = json.loads(
                qi_stack.run(
                    [
                        "-B",
                        "-W",
                        "error",
                        str(Path(__file__).resolve()),
                        "--emit-toolchain",
                        str(arguments.check_toolchain.resolve()),
                    ]
                )
            )
            if rebuilt != record:
                raise ValueError("live matched compiler differs from its retained receipt")
            print("all nine live compiler rows match the retained operand/control-order receipt")
        return 0
    files = build()
    destination = arguments.write if arguments.write is not None else arguments.check
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()}
    if actual - set(files):
        raise ValueError("matched proposal directory contains unexpected files")
    for name, text in files.items():
        path = destination / name
        if arguments.check or path.exists():
            if not path.is_file() or path.read_text() != text:
                raise ValueError(f"matched proposal differs at {name}; retain a separately named successor")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print("validated nine unsubmitted matched jobs and their exact ideal endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
