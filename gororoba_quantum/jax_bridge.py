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

Every export records the positions of its CZ local errors (``Program.cz``)
so that a sweep over CZ error scales replaces only those stacks.
``CzChannel`` rebuilds the channel NoiseModel.from_backend attaches to one
coupler at any reported CZ error: the depolarizing part
depolarizing_error(p, 2) composed with the thermal relaxation of both qubits
over the gate duration, depolarizing first (QuantumError.compose order), with
p from Aer's _device_depolarizing_error. The channel is affine in p, so each
coupler keeps the Choi matrices at p = 0 and p = 1 and a stack at any error
is the eigendecomposition of their combination.

``structure_key`` names what an export depends on besides gate angles, and
``template``/``instantiate`` export once per key: insert_noise selects each
local error by instruction name and qubits, and the noise model's custom
passes act on delays only, so replicas that differ only in gate angles
receive the same channels at the same positions and differ only in those
gates' unitaries.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from numbers import Real
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Delay, Gate, Parameter, ParameterExpression
from qiskit.quantum_info import Choi, Kraus, Operator

SKIPPED = {"barrier"}
UNSUPPORTED = ("reset", "if_else", "while_loop", "for_loop", "switch_case")
# Choi eigenvalues at or below this floor leave the stack; the Choi trace of a
# two-qubit channel is 4, so the dropped weight stays below 16 * 1e-13.
KRAUS_FLOOR = 1e-13


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
    # (position in ops, physical qargs) of every CZ local error.
    cz: list[tuple[int, tuple[int, ...]]] = field(default_factory=list)
    # (position in ops, source instruction index) of every open angle gate of a template.
    angles: list[tuple[int, int]] = field(default_factory=list)

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


def _require_local(circuit: QuantumCircuit) -> None:
    """Raise UnsupportedCircuit unless every measurement is terminal and no reset or control flow occurs."""
    measured_qubits: set[int] = set()
    for instruction in circuit.data:
        name = instruction.operation.name
        touched = [circuit.find_bit(q).index for q in instruction.qubits]
        if name in UNSUPPORTED or getattr(instruction.operation, "condition", None):
            raise UnsupportedCircuit(f"{circuit.name}: {name} is not a local channel")
        if name == "measure":
            measured_qubits.update(touched)
        elif name not in SKIPPED and measured_qubits.intersection(touched):
            raise UnsupportedCircuit(f"{circuit.name}: {name} acts after a measurement")


def angle_gate(operation: Any) -> bool:
    """A gate whose parameters are all bound real numbers; its unitary is the only output they reach."""
    return (
        isinstance(operation, Gate)
        and bool(operation.params)
        and all(isinstance(p, Real) and not isinstance(p, ParameterExpression) for p in operation.params)
    )


def structure_key(circuit: QuantumCircuit) -> tuple[Any, ...]:
    """Everything export reads from circuit except the angles of angle gates.

    Per instruction: name, physical qubits, clbits, and the parameters of
    every operation that is not an angle gate (a delay's duration and unit
    set its relaxation channel); an angle gate contributes its parameter
    count. Two circuits with equal keys under one noise model export
    programs with equal qargs, equal channels and equal measurement maps,
    differing only in the unitaries at angle-gate positions.
    """
    _require_local(circuit)
    rows: list[tuple[Any, ...]] = []
    for instruction in circuit.data:
        operation = instruction.operation
        qargs = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        cargs = tuple(circuit.find_bit(c).index for c in instruction.clbits)
        if angle_gate(operation):
            params: tuple[Any, ...] = ("angles", len(operation.params))
        else:
            params = (tuple(float(p) for p in operation.params), getattr(operation, "unit", None))
        rows.append((operation.name, qargs, cargs, params))
    return (circuit.num_qubits, circuit.num_clbits, tuple(rows))


def export(circuit: QuantumCircuit, noise_model: Any, kraus_cache: dict[int, np.ndarray] | None = None) -> Program:
    """The local-channel program Aer's density-matrix method applies to circuit under noise_model.

    kraus_cache maps id(QuantumError) of the noise model's local errors to
    their Kraus stacks and may be shared across exports under the same, live
    noise model. Relaxation errors the delay pass creates live only as long
    as one noisy circuit, so their ids recur after collection and they are
    converted per export.
    """
    return _export(circuit, noise_model, kraus_cache, {})


def _export(
    circuit: QuantumCircuit,
    noise_model: Any,
    kraus_cache: dict[int, np.ndarray] | None,
    angles: Mapping[str, tuple[int, int]],
) -> Program:
    """export; an operation carrying a Parameter named in angles keeps an empty stack and records its source."""
    from qiskit_aer.noise.errors.base_quantum_error import QuantumChannelInstruction
    from qiskit_aer.utils import insert_noise

    _require_local(circuit)
    shared = {} if kraus_cache is None else kraus_cache
    local: dict[int, np.ndarray] = {}
    owned = {id(error) for by_qubits in noise_model._local_quantum_errors.values() for error in by_qubits.values()}
    physical = _active(circuit)
    index = {q: k for k, q in enumerate(physical)}
    staged = circuit
    passes = noise_model._pass_manager()
    if passes is not None and any(isinstance(i.operation, Delay) for i in circuit.data):
        staged = passes.run(circuit)
    noisy = insert_noise(staged, noise_model, transpile=False)
    cz_errors = noise_model._local_quantum_errors.get("cz", {})
    program = Program(n=len(physical), physical=physical, num_clbits=circuit.num_clbits)
    for instruction in noisy.data:
        operation = instruction.operation
        name = operation.name
        if name in SKIPPED:
            continue
        qargs = tuple(noisy.find_bit(q).index for q in instruction.qubits)
        qubits = tuple(index[q] for q in qargs)
        if name == "measure":
            program.measured.append((qubits[0], noisy.find_bit(instruction.clbits[0]).index))
            continue
        if isinstance(operation, QuantumChannelInstruction):
            error = operation._quantum_error
            key = id(error)
            cache = shared if key in owned else local
            if key not in cache:
                cache[key] = np.asarray(Kraus(error.to_quantumchannel()).data, dtype=np.complex128)
            if error is cz_errors.get(qargs):
                program.cz.append((len(program.ops), qargs))
            program.ops.append((qubits, cache[key]))
        elif isinstance(operation, Delay):
            continue
        elif angles and operation.is_parameterized():
            names = {p.name for value in operation.params for p in value.parameters}
            sources = {angles[p][0] for p in names}
            if len(sources) != 1:
                raise ValueError(f"{circuit.name}: {name} carries parameters of several instructions")
            dimension = 2 ** len(qubits)
            program.angles.append((len(program.ops), sources.pop()))
            program.ops.append((qubits, np.zeros((0, dimension, dimension), dtype=np.complex128)))
        else:
            program.ops.append((qubits, Operator(operation).data[None].astype(np.complex128)))
    for qubit, _ in program.measured:
        error = noise_model._local_readout_errors.get((program.physical[qubit],))
        program.readout[qubit] = np.asarray(error.probabilities if error is not None else np.eye(2), dtype=float)
    return program


def template(circuit: QuantumCircuit, noise_model: Any, kraus_cache: dict[int, np.ndarray] | None = None) -> Program:
    """The export of circuit with every angle gate left open; instantiate fills it for any circuit of equal key.

    Each angle gate's parameters become Parameters named after its
    instruction index, so the noise passes and insert_noise carry the index
    to the position the gate takes in the program whatever order the
    relaxation pass's DAG round trip gives the instructions.
    """
    _require_local(circuit)
    body = circuit.copy_empty_like()
    angles: dict[str, tuple[int, int]] = {}
    for position, instruction in enumerate(circuit.data):
        operation = instruction.operation
        if angle_gate(operation):
            operation = operation.copy()
            symbols = [Parameter(f"angle_{position}_{j}") for j in range(len(operation.params))]
            angles.update({p.name: (position, j) for j, p in enumerate(symbols)})
            operation.params = symbols
        body.append(operation, instruction.qubits, instruction.clbits, copy=False)
    return _export(body, noise_model, kraus_cache, angles)


def instantiate(skeleton: Program, circuit: QuantumCircuit) -> Program:
    """skeleton (a template of circuit's structure key) with circuit's angle-gate unitaries in place."""
    ops = list(skeleton.ops)
    for position, source in skeleton.angles:
        operation = circuit.data[source].operation
        ops[position] = (ops[position][0], Operator(operation).data[None].astype(np.complex128))
    return replace(skeleton, ops=ops, angles=[])


def rescale_cz(program: Program, stacks: Mapping[tuple[int, ...], np.ndarray]) -> Program:
    """program with each CZ local error replaced by stacks[physical qargs]."""
    ops = list(program.ops)
    for position, qargs in program.cz:
        ops[position] = (ops[position][0], stacks[qargs])
    return replace(program, ops=ops)


@dataclass
class CzChannel:
    """The CZ channel NoiseModel.from_backend builds for one coupler, at any reported CZ error.

    relax_choi is the Choi matrix of the thermal relaxation R over the gate
    duration (the identity channel when the duration is zero) and
    depolarized_choi that of depolarizing_error(1, 2) followed by R, the map
    rho -> Tr(rho) R(I) / 4. In Qiskit's Choi convention, sum_ij |i><j| (x)
    E(|i><j|) with the input factor more significant, that map's Choi
    matrix is I (x) R(I) / 4, and R(I) is the sum of relax_choi's diagonal
    blocks. relax_fidelity is R's average gate fidelity, which sets Aer's
    depolarizing parameter.
    """

    relax_choi: np.ndarray
    depolarized_choi: np.ndarray
    relax_fidelity: float

    @classmethod
    def build(cls, relaxation: list[tuple[float | None, float | None]], duration: float | None) -> CzChannel:
        """From (T1, T2) of qargs[0] and qargs[1] in seconds and the gate duration in seconds.

        Mirrors _device_thermal_relaxation_error at temperature 0: T2 is
        truncated to 2 T1, a missing T1 or T2 is infinite, and the second
        qubit's channel is the more significant tensor factor (expand).
        """
        from qiskit.quantum_info import average_gate_fidelity
        from qiskit_aer.noise import thermal_relaxation_error

        relax = None
        if duration:
            for t1, t2 in relaxation:
                if t1 is not None:
                    t2 = 2 * t1 if t2 is None else min(t2, 2 * t1)
                single = thermal_relaxation_error(
                    math.inf if t1 is None else t1, math.inf if t2 is None else t2, duration, 0
                )
                relax = single if relax is None else relax.expand(single)
        if relax is None:
            choi, fidelity = Choi(Operator(np.eye(4))).data, 1.0
        else:
            choi, fidelity = Choi(relax.to_quantumchannel()).data, float(average_gate_fidelity(relax))
        image = sum(choi[4 * i : 4 * i + 4, 4 * i : 4 * i + 4] for i in range(4))
        return cls(relax_choi=choi, depolarized_choi=np.kron(np.eye(4), image) / 4, relax_fidelity=fidelity)

    def depolarizing(self, error: float | None) -> float:
        """_device_depolarizing_error's parameter for a two-qubit gate of reported error."""
        dim = 4
        infidelity = 1 - self.relax_fidelity
        if not error or error <= infidelity:
            return 0.0
        error = min(error, dim / (dim + 1))
        return min(dim * (error - infidelity) / (dim * self.relax_fidelity - 1), 16 / 15)

    def kraus(self, error: float | None) -> np.ndarray:
        """The channel's minimal Kraus stack, (rank, 4, 4), at the reported CZ error."""
        p = self.depolarizing(error)
        choi = (1 - p) * self.relax_choi + p * self.depolarized_choi
        values, vectors = np.linalg.eigh((choi + choi.conj().T) / 2)
        keep = values > KRAUS_FLOOR
        return np.stack(
            [math.sqrt(w) * v.reshape((4, 4), order="F") for w, v in zip(values[keep], vectors.T[keep], strict=True)]
        ).astype(np.complex128)


def cz_channel(snapshot: Mapping[str, Any], qargs: tuple[int, ...]) -> tuple[CzChannel, float | None]:
    """The CzChannel and reported error of one CZ qargs of a calibration_snapshot document."""
    entries = [e for e in snapshot["instructions"]["cz"] if tuple(e["qargs"]) == qargs]
    if len(entries) != 1:
        raise KeyError(f"the snapshot holds {len(entries)} cz entries on {qargs}")
    relaxation = [(snapshot["qubits"][q]["t1"], snapshot["qubits"][q]["t2"]) for q in qargs]
    return CzChannel.build(relaxation, entries[0]["duration"]), entries[0]["error"]


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
    """numpy einsum along the greedy contraction path, searched once per subscripts and operand shapes.

    np.einsum with an explicit path runs the contractions the greedy search
    would choose, in the same order, so the result carries the same bits.
    """

    conj = staticmethod(np.conj)
    paths: dict[tuple[str, tuple[tuple[int, ...], ...]], list[Any]] = {}

    @staticmethod
    def einsum(subscripts: str, *operands: Any) -> Any:
        key = (subscripts, tuple(np.shape(operand) for operand in operands))
        path = _Numpy.paths.get(key)
        if path is None:
            path = _Numpy.paths[key] = np.einsum_path(subscripts, *operands, optimize="greedy")[0]
        return np.einsum(subscripts, *operands, optimize=path)


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


def stack_ranks(programs: list[Program]) -> list[int]:
    """Per operation, the largest Kraus rank over programs: the common rank stack_programs pads to."""
    structure = programs[0].structure()
    for program in programs[1:]:
        if program.structure() != structure:
            raise ValueError("programs differ in operation order or qargs and cannot share one evolver")
    return [max(program.ops[position][1].shape[0] for program in programs) for position in range(len(structure))]


def stack_programs(
    programs: list[Program], ranks: list[int] | None = None, dtype: Any = np.complex128
) -> list[tuple[tuple[int, ...], np.ndarray]]:
    """Per operation, the Kraus stacks of every program zero-padded to ranks: shape (batch, rank, d, d).

    ranks defaults to stack_ranks(programs). A slice of a larger group passes
    the group's ranks, so every slice has the shapes of the whole group and
    its rows equal the whole group's stack at the same programs.
    """
    own = stack_ranks(programs)
    if ranks is None:
        ranks = own
    elif len(ranks) != len(own) or any(r < o for r, o in zip(ranks, own, strict=True)):
        raise ValueError(f"ranks {ranks} do not cover the programs' Kraus ranks {own}")
    stacked = []
    for position, qargs in enumerate(programs[0].structure()):
        d = programs[0].ops[position][1].shape[1]
        padded = np.zeros((len(programs), ranks[position], d, d), dtype=dtype)
        for b, program in enumerate(programs):
            s = program.ops[position][1]
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
