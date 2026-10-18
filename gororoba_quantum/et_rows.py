"""Coherent full-row multiplication, explicit decoding and independent signed-path references."""

import math
from functools import lru_cache

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector

from cd_core import cd_sign
from et_reference import ETSpec
from select_lcu import select_circuit

COMPILATION_CONTRACT = "arbitrary-input-unitary-v1"


def decode_circuit(spec: ETSpec, basis: str) -> QuantumCircuit:
    if basis not in ("Z", "X"):
        raise ValueError("ET measurement basis must be Z or X")
    circuit = QuantumCircuit(spec.bits + 1, name="et_decoder_" + basis)
    for bit in range(spec.bits - 1):
        if spec.strut & (1 << bit):
            circuit.cx(spec.bits - 1, bit)
        if spec.row & (1 << bit):
            circuit.x(bit)
    if basis == "X":
        circuit.h(range(spec.bits - 1))
    return circuit


def row_template(spec: ETSpec, basis: str) -> tuple[QuantumCircuit, ParameterVector]:
    """One routed template shares sign/mask bindings and the complete decoder suffix."""
    phases = ParameterVector("et_phase", spec.bits)
    circuit = QuantumCircuit(QuantumRegister(spec.bits, "data"), QuantumRegister(1, "selector"))
    circuit.h(range(spec.bits))
    for bit in range(spec.bits):
        circuit.rz(phases[bit], bit)
    circuit.global_phase = sum(phases) / 2
    for bit in range(spec.bits - 1):
        if spec.strut & (1 << bit):
            circuit.cx(spec.bits - 1, bit)
    circuit.h(spec.bits)
    circuit.compose(select_circuit(spec.dimension, spec.row, spec.high), inplace=True)
    circuit.h(spec.bits)
    circuit.barrier()
    circuit.compose(decode_circuit(spec, basis), inplace=True)
    circuit.metadata = {
        "compilation_contract": COMPILATION_CONTRACT,
        "et_spec": [spec.dimension, spec.strut, spec.row],
        "et_basis": basis,
        "outcome_order": "column_lsb,dyad_high,selector",
    }
    return circuit, phases


def row_circuit(
    spec: ETSpec, sign: int = 1, basis: str = "Z", mask: int = 0, *, measured: bool = True
) -> QuantumCircuit:
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError("dyad sign must be +1 or -1")
    if type(mask) is not int or not 0 <= mask < spec.generator:
        raise ValueError("phase mask must fit the column register")
    circuit, phases = row_template(spec, basis)
    angles = [math.pi if mask & (1 << bit) else 0.0 for bit in range(spec.bits - 1)]
    angles.append(math.pi if sign == -1 else 0.0)
    circuit.assign_parameters(dict(zip(phases, angles, strict=True)), inplace=True)
    circuit.name = f"et_d{spec.dimension}_s{spec.strut}_r{spec.row}_{basis}_t{sign}_m{mask}"
    if measured:
        circuit.add_register(ClassicalRegister(spec.bits + 1, "et_out"))
        circuit.measure(range(spec.bits + 1), range(spec.bits + 1))
    return circuit


@lru_cache(maxsize=2048)
def direct_state(spec: ETSpec, sign: int = 1, basis: str = "Z", mask: int = 0) -> np.ndarray:
    """Sum signed multiplication paths, then relabel and Walsh-transform without circuit simulation."""
    if sign not in (-1, 1) or basis not in ("X", "Z") or not 0 <= mask < spec.generator:
        raise ValueError("invalid signed ET reference parameters")
    state = np.zeros((4, spec.generator), dtype=complex)
    for column in range(spec.generator):
        marker = (-1) ** ((column & mask).bit_count() % 2)
        for high in (0, 1):
            source = column ^ (spec.xor_label if high else 0)
            for branch in (0, 1):
                left = spec.high if branch else spec.row
                output = source ^ left
                decoded_high = int(output >= spec.generator)
                amplitude = marker * (sign if high else 1) * cd_sign(spec.dimension, left, source)
                for selector in (0, 1):
                    state[2 * selector + decoded_high, spec.decode(output)] += (
                        amplitude * (-1) ** (branch * selector) / (2 * math.sqrt(spec.dimension))
                    )
    if basis == "X":
        # Butterfly arithmetic evaluates the normalized Walsh transform in O(G log G).
        step = 1
        while step < spec.generator:
            for start in range(0, spec.generator, 2 * step):
                low = state[:, start : start + step].copy()
                high_values = state[:, start + step : start + 2 * step].copy()
                state[:, start : start + step] = low + high_values
                state[:, start + step : start + 2 * step] = low - high_values
            step *= 2
        state /= math.sqrt(spec.generator)
    return state.ravel()
