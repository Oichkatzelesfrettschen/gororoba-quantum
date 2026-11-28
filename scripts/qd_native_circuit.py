"""A Perceval Circuit built from numbers the repository's own decoder read out of a served circuit string.

perceval.serialization.deserialize evaluates a symbolic parameter expression with sympy (Perceval 1.3.1,
_parameter_serialization.py: sp.S(serial_param.expression)), so a string served by the provider never reaches
it. qd_belenos_mesh.decode reads the protobuf wire format with the standard library and returns couplers and
phase shifters; circuit_from_elements places those elements on a Circuit and refuses every parameter that is not
a plain number, so a served expression is rejected before any evaluation.
"""

from __future__ import annotations

import base64
import math
from typing import Any

import qd_belenos_mesh as mesh_lib

PARAMETER_SYMBOL, PARAMETER_EXPRESSION, PARAMETER_EXPR_PARAMETERS = 2, 3, 5


class NativeCircuitError(ValueError):
    pass


def number(value: Any, what: str) -> float:
    """A finite float; a string (a symbol or an expression), a bool or a non-finite value is refused."""
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise NativeCircuitError(f"{what} is {value!r}, not a finite number")
    return float(value)


def refuse_parameter(data: bytes, where: str) -> None:
    """Refuse a Parameter message that carries a symbol or an expression (fields 2, 3 and 5 of the schema)."""
    fields = {n for n, _ in mesh_lib.wire(data)}
    if fields & {PARAMETER_SYMBOL, PARAMETER_EXPRESSION, PARAMETER_EXPR_PARAMETERS}:
        raise NativeCircuitError(f"{where} carries a symbolic parameter or expression, which no tool evaluates")


def refuse_symbolic(messages: list[bytes]) -> None:
    for message in messages:
        fields = mesh_lib.wire(message)
        for number_, body in fields:
            if number_ == 10:
                refuse_symbolic([v for n, v in mesh_lib.wire(body) if n == 4])
            elif number_ == 11:
                refuse_parameter(bytes(dict(mesh_lib.wire(body))[1]), "a phase shifter")
            elif number_ == 12:
                for n, v in mesh_lib.wire(body):
                    if n in (2, 3, 4, 5, 6):
                        refuse_parameter(bytes(v), "a beam splitter")


def refuse_expressions(text: str) -> None:
    """Walk the protobuf of a served circuit string and refuse any symbol or expression, without evaluating."""
    body = mesh_lib.unzip(text)
    for tag, field in ((":PCVL:ACircuit:", 4), (":PCVL:Experiment:", 9)):
        if body.startswith(tag):
            refuse_symbolic([v for n, v in mesh_lib.wire(base64.b64decode(body[len(tag) :])) if n == field])
            return
    raise NativeCircuitError(f"{body[:24]!r} is not a serialized circuit or experiment")


def circuit_from_elements(elements: list[mesh_lib.Element], modes: int | None = None) -> Any:
    """The Circuit of decoded elements ("bs": five Rx angles, "ps": one phase), in component order."""
    import perceval as pcvl

    if not elements:
        raise NativeCircuitError("the circuit holds no element")
    span = max(m + (2 if kind == "bs" else 1) for kind, m, _ in elements)
    size = span if modes is None else modes
    if size < span:
        raise NativeCircuitError(f"the elements reach mode {span - 1}, beyond the {size}-mode circuit")
    circuit = pcvl.Circuit(size)
    for kind, mode, parameter in elements:
        if kind == "ps":
            circuit.add(mode, pcvl.PS(number(parameter, f"phase shifter on mode {mode}")))
        elif kind == "bs":
            theta, tl, bl, tr, br = (number(a, f"coupler angle on mode {mode}") for a in parameter)
            circuit.add(mode, pcvl.BS(theta=theta, phi_tl=tl, phi_bl=bl, phi_tr=tr, phi_br=br))
        else:
            raise NativeCircuitError(f"element kind {kind!r} is outside the Belenos mesh")
    return circuit


def circuit_from_text(text: str, modes: int | None = None) -> Any:
    """The Circuit of a served ':PCVL:ACircuit:' string, read by the repository's decoder."""
    refuse_expressions(text)
    return circuit_from_elements(mesh_lib.decode(text), modes)
