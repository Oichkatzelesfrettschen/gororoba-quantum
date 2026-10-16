"""Local-channel programs from Aer noise models, replayed as exact density matrices in numpy or JAX.

``export`` turns an ISA circuit whose measurements are all terminal, under an
Aer NoiseModel, into the operations Aer applies: the noise model's custom
passes first (thermal relaxation after each delay, as
AerBackend._assemble_noise_model runs them on circuits that contain a
delay), then ``qiskit_aer.utils.insert_noise``, which appends each
instruction's local quantum error after it. Every operation becomes a stack
of Kraus matrices (a gate is the rank-1 stack of its unitary) on the
circuit's active qubits, renumbered 0..n-1 in ascending physical order.
Readout stays classical: each measured qubit carries Aer's matrix
R[i][j] = P(record j | prepared i), so p_recorded = R^T p over that bit.

Local operators follow Qiskit's little-endian order: qargs[0] is the least
significant bit of the local index, and active qubit q is bit q of the
register index. ``probabilities`` returns the distribution over the
circuit's classical bits indexed as live_run._distribution reads counts,
clbit 0 least significant, so it compares directly with a retained
hardware distribution.

``evolve_numpy`` is the complex128 reference; ``make_jax_evolver`` builds
the same contraction sequence in JAX (complex64 storage, matmuls at
Precision.HIGHEST) for one program structure, and ``stack_programs``
batches programs that share that structure (the same qargs in the same
order, as a sweep over error scales produces) by padding every Kraus stack
with zero operators to a common rank, which leaves each channel unchanged.
Circuits with reset, mid-circuit measurement or classical control raise
UnsupportedCircuit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Delay
from qiskit.quantum_info import Kraus, Operator

SKIPPED = {"barrier"}


class UnsupportedCircuit(ValueError):
    """The circuit carries an operation the local-channel program does not represent."""


@dataclass
class Program:
    """Ordered local channels on n active qubits, terminal measurement map and readout matrices."""

    n: int
    physical: list[int]
    ops: list[tuple[tuple[int, ...], np.ndarray]] = field(default_factory=list)
    measured: list[tuple[int, int]] = field(default_factory=list)
    num_clbits: int = 0
    readout: dict[int, np.ndarray] = field(default_factory=dict)

    def structure(self) -> list[tuple[int, ...]]:
        return [qargs for qargs, _ in self.ops]


def _active(circuit: QuantumCircuit) -> list[int]:
    return sorted(
        {
            circuit.find_bit(q).index
            for instruction in circuit.data
            if instruction.operation.name not in SKIPPED
            for q in instruction.qubits
        }
    )


def export(circuit: QuantumCircuit, noise_model: Any, kraus_cache: dict[int, np.ndarray] | None = None) -> Program:
    """The local-channel program Aer's density-matrix method applies to circuit under noise_model."""
    from qiskit_aer.noise.errors.base_quantum_error import QuantumChannelInstruction
    from qiskit_aer.utils import insert_noise

    cache = {} if kraus_cache is None else kraus_cache
    physical = _active(circuit)
    index = {q: k for k, q in enumerate(physical)}
    measured_qubits: set[int] = set()
    for instruction in circuit.data:
        name = instruction.operation.name
        touched = [circuit.find_bit(q).index for q in instruction.qubits]
        if name in ("reset", "if_else", "while_loop", "for_loop", "switch_case") or getattr(
            instruction.operation, "condition", None
        ):
            raise UnsupportedCircuit(f"{circuit.name}: {name} is not a local channel")
        if name == "measure":
            measured_qubits.update(touched)
        elif name not in SKIPPED and measured_qubits.intersection(touched):
            raise UnsupportedCircuit(f"{circuit.name}: {name} acts after a measurement")
    staged = circuit
    passes = noise_model._pass_manager()
    if passes is not None and any(isinstance(i.operation, Delay) for i in circuit.data):
        staged = passes.run(circuit)
    noisy = insert_noise(staged, noise_model, transpile=False)
    program = Program(n=len(physical), physical=physical, num_clbits=circuit.num_clbits)
    for instruction in noisy.data:
        operation = instruction.operation
        name = operation.name
        if name in SKIPPED:
            continue
        qubits = tuple(index[noisy.find_bit(q).index] for q in instruction.qubits)
        if name == "measure":
            program.measured.append((qubits[0], noisy.find_bit(instruction.clbits[0]).index))
            continue
        if isinstance(operation, QuantumChannelInstruction):
            error = operation._quantum_error
            key = id(error)
            if key not in cache:
                cache[key] = np.asarray(Kraus(error.to_quantumchannel()).data, dtype=np.complex128)
            program.ops.append((qubits, cache[key]))
        elif isinstance(operation, Delay):
            continue
        else:
            program.ops.append((qubits, Operator(operation).data[None].astype(np.complex128)))
    for qubit, _ in program.measured:
        error = noise_model._local_readout_errors.get((program.physical[qubit],))
        program.readout[qubit] = np.asarray(error.probabilities if error is not None else np.eye(2), dtype=float)
    return program


def _subscripts(qargs: tuple[int, ...], n: int) -> str:
    """einsum subscripts for sum_a K_a rho K_a^dagger on qargs.

    rho is a (2,)*2n tensor whose row axes come first with qubit n-1 leading
    and whose column axes follow in the same order; the Kraus stack is
    (rank,) + (2,)*2k with output then input local bits, most significant
    (qargs[k-1]) first, so qargs[0] is the least significant local bit.
    """
    letters = iter("bcdefghijklmnopqrstuvwxyzBCDEFGHIJKLMNOPQRSTUVWXYZ")
    rows = [next(letters) for _ in range(n)]
    cols = [next(letters) for _ in range(n)]
    k = len(qargs)
    axes = [n - 1 - q for q in reversed(qargs)]
    out_rows = [next(letters) for _ in range(k)]
    out_cols = [next(letters) for _ in range(k)]
    result_rows, result_cols = list(rows), list(cols)
    for position, axis in enumerate(axes):
        result_rows[axis] = out_rows[position]
        result_cols[axis] = out_cols[position]
    kraus = "a" + "".join(out_rows) + "".join(rows[axis] for axis in axes)
    adjoint = "a" + "".join(out_cols) + "".join(cols[axis] for axis in axes)
    return f"{kraus},{adjoint},{''.join(rows + cols)}->{''.join(result_rows + result_cols)}"


def _apply(rho: Any, qargs: tuple[int, ...], kraus: Any, n: int, xp: Any) -> Any:
    """sum_a K_a rho K_a^dagger on qargs as one contraction over the Kraus index."""
    ops = kraus.reshape((kraus.shape[0],) + (2,) * (2 * len(qargs)))
    return xp.einsum(_subscripts(qargs, n), ops, xp.conj(ops), rho)


class _Numpy:
    conj = staticmethod(np.conj)

    @staticmethod
    def einsum(subscripts: str, *operands: Any) -> Any:
        return np.einsum(subscripts, *operands, optimize="greedy")


def evolve_numpy(program: Program) -> np.ndarray:
    """The final density matrix, (2^n, 2^n) complex128, starting from |0...0>."""
    n = program.n
    rho = np.zeros((2,) * (2 * n), dtype=np.complex128)
    rho[(0,) * (2 * n)] = 1
    for qargs, kraus in program.ops:
        rho = _apply(rho, qargs, kraus, n, _Numpy)
    return rho.reshape(2**n, 2**n)


def probabilities(
    program: Program, diagonal: np.ndarray, readout_scale: float = 1.0, flip_cap: float = 0.5
) -> np.ndarray:
    """Recorded distribution over the classical bits from the register diagonal, with readout applied.

    readout_scale multiplies each flip probability as ghost_error_scale.flip
    does: min(scale * p, max(p, flip_cap)).
    """
    n = program.n
    p = np.clip(np.real(np.asarray(diagonal, dtype=np.complex128)), 0.0, None).reshape((2,) * n)
    # Axis of qubit q is n-1-q; marginalize unmeasured qubits, apply R^T per measured bit.
    measured = dict(program.measured)
    for qubit in range(n):
        if qubit in measured:
            matrix = program.readout[qubit]
            e10, e01 = matrix[0][1], matrix[1][0]
            e10s = min(readout_scale * e10, max(e10, flip_cap))
            e01s = min(readout_scale * e01, max(e01, flip_cap))
            scaled = np.array([[1 - e10s, e10s], [e01s, 1 - e01s]])
            p = np.moveaxis(np.tensordot(scaled.T, p, axes=([1], [n - 1 - qubit])), 0, n - 1 - qubit)
    out = np.zeros(2**program.num_clbits)
    flat = p.reshape(-1)
    for basis, weight in enumerate(flat):
        if weight == 0:
            continue
        clbits = 0
        for qubit, clbit in program.measured:
            clbits |= ((basis >> qubit) & 1) << clbit
        out[clbits] += weight
    return out / out.sum()


def stack_programs(programs: list[Program]) -> list[tuple[tuple[int, ...], np.ndarray]]:
    """Per operation, the Kraus stacks of every program padded to a common rank: shape (batch, rank, d, d)."""
    structure = programs[0].structure()
    for program in programs[1:]:
        if program.structure() != structure:
            raise ValueError("programs differ in operation order or qargs and cannot share one evolver")
    stacked = []
    for position, qargs in enumerate(structure):
        stacks = [program.ops[position][1] for program in programs]
        rank = max(s.shape[0] for s in stacks)
        d = stacks[0].shape[1]
        padded = np.zeros((len(stacks), rank, d, d), dtype=np.complex128)
        for b, s in enumerate(stacks):
            padded[b, : s.shape[0]] = s
        stacked.append((qargs, padded))
    return stacked


def make_jax_evolver(structure: list[tuple[int, ...]], n: int) -> Any:
    """A jitted, batched map from Kraus stacks (one array per operation, leading batch axis) to register diagonals."""
    import jax
    import jax.numpy as jnp

    highest = jax.lax.Precision.HIGHEST

    class _Xp:
        conj = staticmethod(jnp.conj)

        @staticmethod
        def einsum(subscripts: str, *operands: Any) -> Any:
            return jnp.einsum(subscripts, *operands, precision=highest, optimize="greedy")

    xp = _Xp()

    def single(kraus_list: list[Any]) -> Any:
        rho = jnp.zeros((2,) * (2 * n), dtype=jnp.complex64).at[(0,) * (2 * n)].set(1)
        for qargs, kraus in zip(structure, kraus_list, strict=True):
            rho = _apply(rho, qargs, kraus, n, xp)
        return jnp.real(jnp.diagonal(rho.reshape(2**n, 2**n)))

    return jax.jit(jax.vmap(single))
