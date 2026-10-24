"""Export the pinned Tuna pilot's finite native IR with round-trip binary64 angles.

The public IR visitor carries the export. The accepted statement classes are
explicit because IRVisitor's default methods silently return None.
"""

from __future__ import annotations

import importlib
import math
from importlib.metadata import version
from typing import Any


def float_literal(value: float) -> str:
    """Seventeen significant decimal digits round-trip every finite binary64."""
    if not math.isfinite(value):
        raise ValueError("cQASM angle must be finite")
    return format(value, ".17g")


def export_circuit(circuit: Any) -> str:
    if version("opensquirrel") != "0.9.1":
        raise ValueError("full-precision exporter requires opensquirrel 0.9.1")
    from opensquirrel.ir import Barrier, IRVisitor, Measure
    from opensquirrel.ir.default_gates.single_qubit_gates import Rx, Ry, Rz, X
    from opensquirrel.ir.default_gates.two_qubit_gates import CZ
    from opensquirrel.ir.semantics import BsrAngleParam, BsrNoParams

    accepted = {Rx, Ry, Rz, X, CZ, Barrier, Measure}
    for statement in circuit.ir.statements:
        if type(statement) not in accepted:
            raise ValueError(f"unsupported IR statement: {type(statement).__name__}")

    class Writer(IRVisitor):
        def __init__(self) -> None:
            self.lines: list[str] = []

        def visit_single_qubit_gate(self, gate: Any) -> None:
            if type(gate) in {Rx, Ry, Rz} and type(gate.bsr) is BsrAngleParam:
                parameters = f"({float_literal(float(gate.bsr.theta.value))})"
            elif type(gate) is X and type(gate.bsr) is BsrNoParams:
                parameters = ""
            else:
                raise ValueError("unsupported single-qubit semantic")
            self.lines.append(f"{gate.name}{parameters} {circuit.qubit_register_name}[{gate.qubit.index}]")

        def visit_two_qubit_gate(self, gate: Any) -> None:
            self.lines.append(
                f"CZ {circuit.qubit_register_name}[{gate.qubit0.index}], "
                f"{circuit.qubit_register_name}[{gate.qubit1.index}]"
            )

        def visit_barrier(self, barrier: Any) -> None:
            self.lines.append(f"barrier {circuit.qubit_register_name}[{barrier.qubit.index}]")

        def visit_measure(self, measure: Any) -> None:
            if tuple(measure.axis.value) != (0, 0, 1):
                raise ValueError("unsupported measurement axis")
            self.lines.append(
                f"{circuit.bit_register_name}[{measure.bit.index}] = "
                f"measure {circuit.qubit_register_name}[{measure.qubit.index}]"
            )

    writer = Writer()
    circuit.ir.accept(writer)
    if len(writer.lines) != len(circuit.ir.statements):
        raise ValueError("every IR statement must emit exactly one cQASM instruction")
    declarations = [
        "version 3.0",
        f"qubit[{circuit.qubit_register_size}] {circuit.qubit_register_name}",
        f"bit[{circuit.bit_register_size}] {circuit.bit_register_name}",
    ]
    return "\n".join(declarations + writer.lines) + "\n"


def compile_circuit(text: str, config: dict[str, Any]) -> str:
    from opensquirrel import Circuit

    circuit = Circuit.from_string(text)
    for stage in ("decomposition", "mapping", "optimization", "routing"):
        for step in config.get(stage, []):
            module, _, name = step["path"].rpartition(".")
            instance = getattr(importlib.import_module(module), name)(**step.get("arguments", {}))
            method = {"decompose": "decompose", "map": "map", "merge": "merge", "route": "route"}[step["method"]]
            getattr(circuit, method)(instance)
    return export_circuit(circuit)
