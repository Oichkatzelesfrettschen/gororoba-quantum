"""Exact branching density matrices of dynamic circuits under Aer noise models, replayed in numpy or torch.

A circuit with mid-circuit measurement, reset and ``if_else`` feed-forward
is a quantum instrument. ``export`` turns it into the operations Aer's
density-matrix method applies per shot. The top-level instructions pass
through the noise model's custom passes when the circuit holds a delay (the
relaxation pass, as AerBackend._assemble_noise_model runs it) and then
``qiskit_aer.utils.insert_noise``. insert_noise walks top-level instructions
only, while AerSimulator inlines every control-flow block into the circuit
(AerCompiler) before its noise passes and per-instruction local errors act,
so each ``if_else`` body is exported as its own sub-circuit on the outer
qubits through the same passes and insert_noise; every channel either path
attaches is local to its instruction's qubits, so the two placements give
the same channels. Each operation becomes a superoperator on the active
qubits, renumbered 0..n-1 in ascending physical order with jax_bridge's
little-endian local convention: a gate from its unitary, a ``reset`` from
the exact channel {|0><0|, |0><1|} (its reset local error follows it), and
a local error from ``error_superop``, which sums the error's circuits'
probability-weighted products of exact Kraus superoperators with no
eigenvalue truncation. It equals qiskit's SuperOp of the QuantumError on
every error the ghost sweep converts (ghost_error_scale_branching.py
``--check-converter``) at about 1/65 of its cost; qiskit composes each
circuit through SuperOp instruction conversions, which dominated export.

Measurement roles. A measure is deferred when no later operation touches
its qubit and no later condition reads its clbit; collapsing then or at the
end gives the same law, so it is read from the final diagonal. Every other
measure splits: each branch rho becomes four children (m, b), true outcome m
and recorded bit b, with state Pi_m rho Pi_m (unnormalized) and memory
c := b. The child carries P_r(b | m) as a symbol, evaluated only at the end
for each readout scale r, because ``if_else`` reads the recorded,
readout-noisy bit (Aer's semantics). A condition reads each branch's memory;
the true body acts on the branches where the clbit or register equals the
value and the false body on the rest. A clbit keeps its last write, and an
unwritten clbit stays 0. Classical-expression conditions, measurements
inside a body and loops raise UnsupportedCircuit.

The joint law over the classical register at readout scale r is
sum_branches w_r(branch) R_r(diag(branch)), where w_r is the product of the
branch's P_r(b | m) and R_r maps the register diagonal through the deferred
qubits' readout matrices at scale r (``flip`` per entry, as
ghost_error_scale.flip caps it) and places the branch's memory bits. Indices
follow ghost_run.distribution: clbit 0 least significant over all
``num_clbits`` bits. With k splitting measures there are 4^k children; a
child whose trace stays below PRUNE_FLOOR in every row of its batch leaves
the batch (one host read per splitting measure). Children of one parent
differ in (m, b) and children of different parents differ in an ancestor's
(m, b), so no two children share a readout symbol and the merging rule
(identical memory, state and symbol) admits none.

``build_plan`` turns a ``template`` export (jax_bridge.template's scheme:
top-level angle gates open, each body's gates part of the ``dynamic_key``)
into superoperator steps for a batch of G replicas of one key, each angle
slot filled from its replica, and F CZ factors. A CZ local error is replaced by
``cz_superop``, jax_bridge.CzChannel's map (1 - p) S_relax + p S_depolarized
at that factor's error, so the CZ factor touches only those steps. A step's
superoperator S[(i, j), (k, l)] = sum_a K_a[i, k] conj(K_a[j, l]) has shape
(G or 1, F or 1, d^2, d^2). With ``fuse`` (the default), an operation folds
into the latest step on a superset of its qubits when no later step touches
them, and a step on a subset of a new operation's qubits that nothing
touched since folds into it; operations on disjoint qubits commute, so the
composed channel is the same map, and every superoperator stays d^2 x d^2
whatever its Kraus rank. Conditional steps and splitting measures do not
fuse. The same plan feeds every backend, so fusion changes the work of the
numpy and torch paths alike.

``evolve`` runs one plan on a backend. The state is one batch
(G, F, B, 2^n, 2^n) with B the live branches; a step is one contraction of
the reshaped qubit legs, x = rho permuted to (G, F, d^2, B 4^(n-k)) and
S @ x, so a step launches two layout copies and one batched matmul whatever
the batch size, and a conditional step adds one masked select. The backends
are numpy complex128 (the reference, the CI path) and torch on cuda or cpu
in complex64 or complex128. The torch path stays on its device from the
upload of the plan's superoperators to the law tensor; the classical
readout map runs in float64 on the device. Host reads happen once per
splitting measure (the pruning test) and once at the end (the readout map
upload waits for the queue).

Contraction form. ``form="local"`` is the superoperator contraction above.
``form="dense"`` (torch only) takes each step's Kraus operators from the
eigendecomposition of its Choi matrix, embeds them as 2^n x 2^n matrices on
the device and applies sum_a E_a rho E_a^dagger with two batched matmuls.
At n = 6 a two-qubit step costs 16 x 16 x 4^4 = 2^16 complex products per
row in the local form and 2 x 16 x 64^3 = 2^23 in the dense form at Kraus
rank 16. On an RTX 4070 Ti (torch 2.14.1, CUDA, another process sharing
the GPU), the fused part-a plans (27 and 16 structures, 801 and 688 steps)
evolved in 0.41 and 0.062 s local against 0.70 and 0.16 s dense in
complex64, and 0.22 and 0.063 s local against 0.87 and 0.54 s dense in
complex128. The complex64 gaps stay under 2x and the complex128 gaps reach
4x and 8.6x, so the complex128 timings and the flop count carry the choice
of the local form as the default; both forms and the unfused plan give the
fused local law within 1e-14 in complex128.
"""

from __future__ import annotations

import importlib
import itertools
import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ClassicalRegister, Clbit, Delay, IfElseOp, Parameter
from qiskit.quantum_info import Operator

import jax_bridge

SKIPPED = jax_bridge.SKIPPED
REFUSED = ("while_loop", "for_loop", "switch_case", "box", "store", "initialize")
RESET_KRAUS = np.array([[[1, 0], [0, 0]], [[0, 1], [0, 0]]], dtype=np.complex128)
# A child whose trace stays below this in every row of its batch carries no
# probability the register law resolves at complex128.
PRUNE_FLOOR = 1e-15
FORMS = ("local", "dense")


class UnsupportedCircuit(ValueError):
    """The circuit carries an operation the branching program does not represent."""


@dataclass(frozen=True)
class Condition:
    """A test on branch memory: the register of clbits (least significant first) equals value (holds) or differs."""

    clbits: tuple[int, ...]
    value: int
    holds: bool

    def test(self, memory: Mapping[int, int]) -> bool:
        register = sum(memory.get(c, 0) << k for k, c in enumerate(self.clbits))
        return (register == self.value) == self.holds


@dataclass
class Item:
    """One exported operation: a channel's superoperator on local qubits, or a measurement of one qubit to a clbit."""

    kind: str
    qargs: tuple[int, ...]
    superop: np.ndarray | None = None
    clbit: int = -1
    when: Condition | None = None


@dataclass
class DynamicProgram:
    """Ordered channels and measurements on n active qubits, with readout matrices and the CZ and angle slots."""

    n: int
    physical: list[int]
    num_clbits: int
    items: list[Item] = field(default_factory=list)
    readout: dict[int, np.ndarray] = field(default_factory=dict)
    # (position in items, physical qargs) of every CZ local error, bodies included.
    cz: list[tuple[int, tuple[int, ...]]] = field(default_factory=list)
    # (position in items, source instruction index) of every open angle gate of a template.
    angles: list[tuple[int, int]] = field(default_factory=list)

    def roles(self) -> tuple[list[int], list[tuple[int, int]]]:
        """Positions of the splitting measures, and (qubit, clbit) of the deferred measures that write a clbit last."""
        splits: list[int] = []
        last: dict[int, int] = {}
        deferred: dict[int, tuple[int, int]] = {}
        for position, item in enumerate(self.items):
            if item.kind != "measure":
                continue
            qubit, clbit = item.qargs[0], item.clbit
            later = self.items[position + 1 :]
            touched = any(qubit in other.qargs for other in later)
            read = any(other.when is not None and clbit in other.when.clbits for other in later)
            if touched or read:
                splits.append(position)
            else:
                deferred[position] = (qubit, clbit)
            last[clbit] = position
        return splits, [deferred[p] for p in sorted(deferred) if last[deferred[p][1]] == p]


def _condition(circuit: QuantumCircuit, condition: Any) -> tuple[tuple[int, ...], int]:
    if not isinstance(condition, tuple) or len(condition) != 2:
        raise UnsupportedCircuit(f"{circuit.name}: a classical expression condition is not a register test")
    target, value = condition
    if isinstance(target, Clbit):
        return (circuit.find_bit(target).index,), int(value)
    if isinstance(target, ClassicalRegister):
        return tuple(circuit.find_bit(bit).index for bit in target), int(value)
    raise UnsupportedCircuit(f"{circuit.name}: condition on {type(target).__name__}")


def _body(outer: QuantumCircuit, instruction: Any, block: QuantumCircuit) -> QuantumCircuit:
    """block on the outer circuit's qubits and clbits, positionally mapped through the if_else instruction."""
    sub = outer.copy_empty_like()
    qubits = dict(zip(block.qubits, instruction.qubits, strict=True))
    clbits = dict(zip(block.clbits, instruction.clbits, strict=True))
    for inner in block.data:
        sub.append(inner.operation, [qubits[q] for q in inner.qubits], [clbits[c] for c in inner.clbits], copy=False)
    return sub


def _rows(circuit: QuantumCircuit, open_angles: bool) -> tuple[Any, ...]:
    rows: list[tuple[Any, ...]] = []
    for instruction in circuit.data:
        operation = instruction.operation
        qargs = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        cargs = tuple(circuit.find_bit(c).index for c in instruction.clbits)
        if isinstance(operation, IfElseOp):
            bits, value = _condition(circuit, operation.condition)
            bodies = tuple(
                None if block is None else _rows(_body(circuit, instruction, block), False)
                for block in operation.blocks
            )
            rows.append((operation.name, qargs, cargs, (bits, value), bodies))
            continue
        if open_angles and jax_bridge.angle_gate(operation):
            params: tuple[Any, ...] = ("angles", len(operation.params))
        else:
            params = (tuple(float(p) for p in operation.params), getattr(operation, "unit", None))
        rows.append((operation.name, qargs, cargs, params))
    return tuple(rows)


def dynamic_key(circuit: QuantumCircuit) -> tuple[Any, ...]:
    """jax_bridge.structure_key extended to control flow: each body's rows, with its gate parameters, and its condition.

    Top-level angle gates contribute their parameter count; body gates keep
    their parameters, so a template opens top-level angles only.
    """
    return (circuit.num_qubits, circuit.num_clbits, _rows(circuit, True))


class _Exporter:
    """Converts noisy (sub)circuits into Items under one noise model, sharing the superoperator caches."""

    def __init__(
        self,
        noise_model: Any,
        cache: dict[int, np.ndarray] | None,
        program: DynamicProgram,
        audit: list[tuple[Any, np.ndarray]] | None = None,
    ) -> None:
        self.noise_model = noise_model
        self.audit = audit
        self.shared = {} if cache is None else cache
        self.local: dict[int, np.ndarray] = {}
        self.owned = {
            id(error) for by_qubits in noise_model._local_quantum_errors.values() for error in by_qubits.values()
        }
        self.cz_errors = noise_model._local_quantum_errors.get("cz", {})
        self.passes = noise_model._pass_manager()
        self.program = program
        self.index = {q: k for k, q in enumerate(program.physical)}

    def noisy(self, circuit: QuantumCircuit) -> QuantumCircuit:
        from qiskit_aer.utils import insert_noise

        staged = circuit
        if self.passes is not None and any(isinstance(i.operation, Delay) for i in circuit.data):
            staged = self.passes.run(circuit)
        return insert_noise(staged, self.noise_model, transpile=False)

    def convert(self, circuit: QuantumCircuit, angles: Mapping[str, tuple[int, int]], when: Condition | None) -> None:
        from qiskit_aer.noise.errors.base_quantum_error import QuantumChannelInstruction

        noisy = self.noisy(circuit)
        program = self.program
        for instruction in noisy.data:
            operation = instruction.operation
            name = operation.name
            if name in SKIPPED:
                continue
            qargs = tuple(noisy.find_bit(q).index for q in instruction.qubits)
            qubits = tuple(self.index[q] for q in qargs)
            if isinstance(operation, IfElseOp):
                if when is not None:
                    raise UnsupportedCircuit(f"{circuit.name}: nested control flow")
                bits, value = _condition(noisy, operation.condition)
                for block, holds in zip(operation.blocks, (True, False), strict=False):
                    if block is not None:
                        self.convert(_body(noisy, instruction, block), {}, Condition(bits, value, holds))
                continue
            if name in REFUSED or operation.name.startswith("save_"):
                raise UnsupportedCircuit(f"{circuit.name}: {name} is not a channel or measurement")
            if name == "measure":
                if when is not None:
                    raise UnsupportedCircuit(f"{circuit.name}: measurement inside a conditional body")
                program.items.append(Item("measure", qubits, clbit=noisy.find_bit(instruction.clbits[0]).index))
                continue
            if isinstance(operation, Delay):
                continue
            if name == "reset":
                s = RESET_SUPEROP
            elif isinstance(operation, QuantumChannelInstruction):
                error = operation._quantum_error
                key = id(error)
                cache = self.shared if key in self.owned else self.local
                if key not in cache:
                    cache[key] = error_superop(error)
                    if self.audit is not None:
                        self.audit.append((error, cache[key]))
                if error is self.cz_errors.get(qargs):
                    program.cz.append((len(program.items), qargs))
                s = cache[key]
            elif angles and operation.is_parameterized():
                names = {p.name for value in operation.params for p in value.parameters}
                sources = {angles[p][0] for p in names}
                if len(sources) != 1:
                    raise ValueError(f"{circuit.name}: {name} carries parameters of several instructions")
                dimension = 4 ** len(qubits)
                program.angles.append((len(program.items), sources.pop()))
                s = np.zeros((dimension, dimension), dtype=np.complex128)
            else:
                try:
                    s = superop(Operator(operation).data[None].astype(np.complex128))
                except Exception as error:
                    raise UnsupportedCircuit(f"{circuit.name}: {name} has no unitary ({error})") from None
            program.items.append(Item("channel", qubits, s, when=when))


def _export(
    circuit: QuantumCircuit,
    noise_model: Any,
    cache: dict[int, np.ndarray] | None,
    angles: Mapping[str, tuple[int, int]],
    audit: list[tuple[Any, np.ndarray]] | None = None,
) -> DynamicProgram:
    physical = jax_bridge._active(circuit)
    program = DynamicProgram(n=len(physical), physical=physical, num_clbits=circuit.num_clbits)
    _Exporter(noise_model, cache, program, audit).convert(circuit, angles, None)
    for item in program.items:
        if item.kind == "measure" and item.qargs[0] not in program.readout:
            error = noise_model._local_readout_errors.get((program.physical[item.qargs[0]],))
            program.readout[item.qargs[0]] = np.asarray(
                error.probabilities if error is not None else np.eye(2), dtype=float
            )
    return program


def export(circuit: QuantumCircuit, noise_model: Any, cache: dict[int, np.ndarray] | None = None) -> DynamicProgram:
    """The branching program Aer's density-matrix method applies to circuit under noise_model.

    cache maps id(QuantumError) of the noise model's local errors to their
    superoperators and may be shared across exports under the same, live
    noise model (jax_bridge.export's rule).
    """
    return _export(circuit, noise_model, cache, {})


def template(
    circuit: QuantumCircuit,
    noise_model: Any,
    cache: dict[int, np.ndarray] | None = None,
    audit: list[tuple[Any, np.ndarray]] | None = None,
) -> DynamicProgram:
    """The export of circuit with every top-level angle gate left open, named by its instruction index.

    audit, when given, receives (QuantumError, superoperator) for every
    local error the export converts, the relaxation pass's included.
    """
    body = circuit.copy_empty_like()
    angles: dict[str, tuple[int, int]] = {}
    for position, instruction in enumerate(circuit.data):
        operation = instruction.operation
        if jax_bridge.angle_gate(operation):
            operation = operation.copy()
            symbols = [Parameter(f"angle_{position}_{j}") for j in range(len(operation.params))]
            angles.update({p.name: (position, j) for j, p in enumerate(symbols)})
            operation.params = symbols
        body.append(operation, instruction.qubits, instruction.clbits, copy=False)
    return _export(body, noise_model, cache, angles, audit)


def superop(kraus: np.ndarray) -> np.ndarray:
    """S[(i, j), (k, l)] = sum_a K_a[i, k] conj(K_a[j, l]) of a (..., rank, d, d) stack: shape (..., d^2, d^2)."""
    d = kraus.shape[-1]
    s = np.einsum("...aik,...ajl->...ijkl", kraus, kraus.conj())
    return s.reshape(kraus.shape[:-3] + (d * d, d * d))


RESET_SUPEROP = superop(RESET_KRAUS)


def _lift(kraus: np.ndarray, qargs: tuple[int, ...], n: int) -> np.ndarray:
    """A (rank, 2^k, 2^k) Kraus stack on local qubits qargs as one on n qubits, little-endian, identity elsewhere."""
    rank = kraus.shape[0]
    if qargs == tuple(range(n)):
        return kraus
    rest = [q for q in range(n) if q not in qargs]
    # kron(I_rest, K): axes most significant first are rest, then qargs, each block in descending order.
    full = np.einsum("ab,rij->raibj", np.eye(2 ** len(rest)), kraus).reshape(rank, 2**n, 2**n)
    order = list(reversed(rest)) + list(reversed(qargs))
    axes = [order.index(q) for q in reversed(range(n))]
    tensor = full.reshape((rank,) + (2,) * (2 * n))
    tensor = tensor.transpose([0] + [1 + a for a in axes] + [1 + n + a for a in axes])
    return tensor.reshape(rank, 2**n, 2**n)


def _instruction_kraus(operation: Any) -> np.ndarray:
    """The Kraus stack of one instruction of a QuantumError circuit: a unitary gate, ``kraus`` or ``reset``."""
    name = operation.name
    if name == "reset":
        return RESET_KRAUS
    if name == "kraus":
        return np.stack([np.asarray(k, dtype=np.complex128) for k in operation.params])
    if operation.is_parameterized() or not hasattr(operation, "to_matrix"):
        raise UnsupportedCircuit(f"local error instruction {name} is not a unitary gate, kraus or reset")
    return np.asarray(operation.to_matrix(), dtype=np.complex128)[None]


def _kraus_superop(kraus: np.ndarray) -> np.ndarray:
    """superop() of a Kraus stack as sum_a kron(K_a, conj(K_a)), which is S[(i, j), (k, l)] for small d."""
    s = np.kron(kraus[0], kraus[0].conj())
    for k in kraus[1:]:
        s += np.kron(k, k.conj())
    return s


# Superoperators of the parameterless gates and resets inside local errors, by (name, params, qargs, n).
_FIXED: dict[tuple[Any, ...], np.ndarray] = {}


def _instruction_superop(
    operation: Any, qargs: tuple[int, ...], n: int, kraus: dict[tuple[Any, ...], np.ndarray]
) -> np.ndarray | None:
    """The superoperator of one error-circuit instruction on n qubits; None for the identity gate.

    kraus caches ``kraus`` instructions by qargs and matrix bytes within
    one error, whose composed terms repeat the same relaxation matrices.
    """
    name = operation.name
    if name == "id":
        return None
    if name == "kraus":
        stack = _instruction_kraus(operation)
        content = (qargs, stack.shape, stack.tobytes())
        if content not in kraus:
            kraus[content] = _kraus_superop(_lift(stack, qargs, n))
        return kraus[content]
    params = tuple(operation.params)
    if not all(isinstance(p, str) for p in params):
        return _kraus_superop(_lift(_instruction_kraus(operation), qargs, n))
    key = (name, params, qargs, n)
    if key not in _FIXED:
        _FIXED[key] = _kraus_superop(_lift(_instruction_kraus(operation), qargs, n))
    return _FIXED[key]


def error_superop(error: Any) -> np.ndarray:
    """A QuantumError's superoperator, sum_t p_t S(circuit_t), each S the ordered product of its instructions' maps.

    Every instruction contributes the superoperator of its exact Kraus
    stack, so no eigenvalue truncation enters; the result equals
    from_superop(SuperOp(error.to_quantumchannel()).data), the qiskit path
    the self-test compares on every local error of the snapshots it covers.
    """
    n = error.num_qubits
    d2 = 4**n
    total = np.zeros((d2, d2), dtype=np.complex128)
    kraus: dict[tuple[Any, ...], np.ndarray] = {}
    for circuit, probability in zip(error.circuits, error.probabilities, strict=True):
        index = {q: k for k, q in enumerate(circuit.qubits)}
        s: np.ndarray | None = None
        for instruction in circuit.data:
            qargs = tuple(index[q] for q in instruction.qubits)
            step = _instruction_superop(instruction.operation, qargs, n, kraus)
            if step is not None:
                s = step if s is None else step @ s
        if s is None:
            total[np.diag_indices(d2)] += probability
        else:
            total += probability * s
    return total


def from_superop(data: np.ndarray) -> np.ndarray:
    """A qiskit SuperOp matrix (column-stacking vec, index i + d j for rho[i, j]) in this module's row-major order."""
    d = int(round(np.sqrt(data.shape[0])))
    return np.ascontiguousarray(data.reshape(d, d, d, d).transpose(1, 0, 3, 2).reshape(d * d, d * d))


def from_choi(choi: np.ndarray) -> np.ndarray:
    """A qiskit Choi matrix (sum_ij |i><j| (x) E(|i><j|), input factor more significant) as a superoperator."""
    d = int(round(np.sqrt(choi.shape[0])))
    return np.ascontiguousarray(choi.reshape(d, d, d, d).transpose(1, 3, 0, 2).reshape(d * d, d * d))


def cz_superop(channel: jax_bridge.CzChannel, error: float | None) -> np.ndarray:
    """The CzChannel's superoperator at the reported CZ error, (1 - p) S_relax + p S_depolarized with no truncation."""
    p = channel.depolarizing(error)
    return (1 - p) * from_choi(channel.relax_choi) + p * from_choi(channel.depolarized_choi)


def superop_kraus(s: np.ndarray, floor: float = jax_bridge.KRAUS_FLOOR) -> np.ndarray:
    """A Kraus stack (rank, d, d) of one superoperator from the eigendecomposition of its Choi matrix.

    C[(i, k), (j, l)] = S[(i, j), (k, l)] = sum_a vec(K_a) vec(K_a)^dagger
    with vec row-major over (i, k); eigenvalues at or below floor leave.
    """
    d = int(round(np.sqrt(s.shape[-1])))
    choi = s.reshape(d, d, d, d).transpose(0, 2, 1, 3).reshape(d * d, d * d)
    values, vectors = np.linalg.eigh((choi + choi.conj().T) / 2)
    keep = values > floor
    return np.stack([np.sqrt(w) * v.reshape(d, d) for w, v in zip(values[keep], vectors.T[keep], strict=True)])


def embed(s: np.ndarray, sub: tuple[int, ...], full: tuple[int, ...]) -> np.ndarray:
    """A superoperator on local qubits sub, (..., 4^|sub|, 4^|sub|), as one on full, identity on full minus sub."""
    if sub == full:
        return s
    ks, kf = len(sub), len(full)
    letters = iter("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # Per full qubit: output row, output column, input row, input column.
    legs = {q: [next(letters) for _ in range(4)] for q in full}
    order_full = list(reversed(full))
    order_sub = list(reversed(sub))
    source = "".join(legs[q][g] for g in range(4) for q in order_sub)
    target = "".join(legs[q][g] for g in range(4) for q in order_full)
    operands: list[Any] = [s.reshape(s.shape[:-2] + (2,) * (4 * ks))]
    terms = ["..." + source]
    eye = np.eye(2)
    for q in full:
        if q not in sub:
            operands += [eye, eye]
            terms += [legs[q][0] + legs[q][2], legs[q][1] + legs[q][3]]
    out = np.einsum(",".join(terms) + "->..." + target, *operands)
    return out.reshape(s.shape[:-2] + (4**kf, 4**kf))


@dataclass
class Step:
    """One superoperator contraction on local qubits; when gates it on branch memory."""

    qargs: tuple[int, ...]
    superop: np.ndarray
    when: Condition | None = None


@dataclass
class Split:
    """A measurement of qubit into clbit that splits every branch into (m, b) children."""

    qubit: int
    clbit: int


@dataclass
class Plan:
    """The steps of G replicas of one dynamic key at F CZ factors, with the terminal readout description."""

    n: int
    rows: tuple[int, int]
    factors: int
    steps: list[Step | Split]
    deferred: list[tuple[int, int]]
    readout: dict[int, np.ndarray]
    num_clbits: int
    exported_ops: int

    @property
    def ops(self) -> int:
        return sum(isinstance(step, Step) for step in self.steps)

    @property
    def splits(self) -> int:
        return sum(isinstance(step, Split) for step in self.steps)


class _Fuser:
    """Appends steps, folding unconditional operations into earlier steps where the composed map is unchanged."""

    def __init__(self, fuse: bool) -> None:
        self.fuse = fuse
        self.steps: list[Step | Split | None] = []
        self.last: dict[int, int] = {}
        self.floor = 0

    def _target(self, j: int | None) -> Step | None:
        if j is None or j < self.floor:
            return None
        step = self.steps[j]
        return step if isinstance(step, Step) and step.when is None else None

    def add(self, qargs: tuple[int, ...], s: np.ndarray, when: Condition | None) -> None:
        if self.fuse and when is None:
            owners = {self.last.get(q) for q in qargs}
            j = next(iter(owners)) if len(owners) == 1 else None
            step = self._target(j)
            if step is not None and set(qargs) <= set(step.qargs):
                step.superop = embed(s, qargs, step.qargs) @ step.superop
                return
            merged: set[int] = set()
            for q in qargs:
                j = self.last.get(q)
                step = self._target(j)
                if (
                    j is not None
                    and j not in merged
                    and step is not None
                    and set(step.qargs) <= set(qargs)
                    and all(self.last.get(p) == j for p in step.qargs)
                ):
                    s = s @ embed(step.superop, step.qargs, qargs)
                    self.steps[j] = None
                    merged.add(j)
        self.steps.append(Step(qargs, s, when))
        for q in qargs:
            self.last[q] = len(self.steps) - 1

    def split(self, qubit: int, clbit: int) -> None:
        self.steps.append(Split(qubit, clbit))
        self.floor = len(self.steps)

    def result(self) -> list[Step | Split]:
        return [step for step in self.steps if step is not None]


def build_plan(
    skeleton: DynamicProgram,
    replicas: Sequence[QuantumCircuit],
    cz_superops: Mapping[tuple[int, ...], np.ndarray] | None,
    factors: int,
    fuse: bool = True,
) -> Plan:
    """The plan of replicas (all of skeleton's dynamic key) at the factors CZ factors cz_superops carries.

    cz_superops maps each CZ physical qargs to its superoperators at the
    factors, shape (factors, 16, 16). Angle slots take each replica's
    unitary, (G, 1, d^2, d^2); every other channel is shared,
    (1, 1, d^2, d^2). cz_superops None keeps the exported CZ local errors
    at one factor. A plan without CZ steps evolves one factor row and its
    law repeats over the factors.
    """
    if cz_superops is None:
        cz_superops, factors = {}, 1
        skeleton = DynamicProgram(
            n=skeleton.n,
            physical=skeleton.physical,
            num_clbits=skeleton.num_clbits,
            items=skeleton.items,
            readout=skeleton.readout,
            cz=[],
            angles=skeleton.angles,
        )
    split_positions, deferred = skeleton.roles()
    splits = set(split_positions)
    angle_source = dict(skeleton.angles)
    cz_slot = dict(skeleton.cz)
    if any(stack.shape[0] != factors for stack in cz_superops.values()):
        raise ValueError(f"CZ superoperators do not all carry {factors} factors")
    shared: dict[int, np.ndarray] = {}
    fuser = _Fuser(fuse)
    for position, item in enumerate(skeleton.items):
        if item.kind == "measure":
            if position in splits:
                fuser.split(item.qargs[0], item.clbit)
            continue
        assert item.superop is not None
        if position in angle_source:
            unitaries = np.stack(
                [Operator(r.data[angle_source[position]].operation).data.astype(np.complex128) for r in replicas]
            )
            s = superop(unitaries[:, None])[:, None]
        elif position in cz_slot:
            s = cz_superops[cz_slot[position]][None]
        else:
            key = id(item.superop)
            if key not in shared:
                shared[key] = item.superop[None, None]
            s = shared[key]
        fuser.add(item.qargs, s, item.when)
    steps = fuser.result()
    return Plan(
        n=skeleton.n,
        rows=(len(replicas), factors if skeleton.cz else 1),
        factors=factors,
        steps=steps,
        deferred=deferred,
        readout=skeleton.readout,
        num_clbits=skeleton.num_clbits,
        exported_ops=sum(item.kind == "channel" for item in skeleton.items),
    )


def scaled_readout(matrix: np.ndarray, factor: float, flip: Callable[[float, float], float]) -> np.ndarray:
    """R[i][j] = P(record j | prepared i) with both flips through flip(value, factor)."""
    e10, e01 = flip(float(matrix[0][1]), factor), flip(float(matrix[1][0]), factor)
    return np.array([[1 - e10, e10], [e01, 1 - e01]])


@dataclass(frozen=True)
class Branch:
    """A branch's memory (clbit -> recorded bit) and its readout symbols (qubit, m, b), in measurement order."""

    memory: tuple[tuple[int, int], ...] = ()
    symbols: tuple[tuple[int, int, int], ...] = ()

    def child(self, qubit: int, clbit: int, m: int, b: int) -> Branch:
        memory = dict(self.memory)
        memory[clbit] = b
        return Branch(tuple(sorted(memory.items())), self.symbols + ((qubit, m, b),))


def readout_map(
    plan: Plan, branches: Sequence[Branch], factors: Sequence[float], flip: Callable[[float, float], float]
) -> np.ndarray:
    """A[branch, r, x, o]: weight of register outcome o from diagonal entry x of branch at readout factor r.

    w_r(branch) = prod P_r(b | m) over the branch's symbols, times the
    deferred qubits' readout probabilities of their recorded bits; the
    branch's memory supplies every clbit no deferred measure writes last.
    """
    d = 2**plan.n
    outcomes = 2**plan.num_clbits
    deferred = plan.deferred
    written = {c for _, c in deferred}
    x = np.arange(d)
    y = np.arange(2 ** len(deferred))
    columns = np.zeros(len(y), dtype=np.int64)
    for k, (_, clbit) in enumerate(deferred):
        columns |= ((y >> k) & 1) << clbit
    out = np.zeros((len(branches), len(factors), d, outcomes))
    for j, factor in enumerate(factors):
        matrices = {q: scaled_readout(m, factor, flip) for q, m in plan.readout.items()}
        table = np.ones((d, len(y)))
        for k, (qubit, _) in enumerate(deferred):
            table *= matrices[qubit][((x >> qubit) & 1)[:, None], ((y >> k) & 1)[None, :]]
        for b, branch in enumerate(branches):
            weight = float(np.prod([matrices[q][m][bit] for q, m, bit in branch.symbols]))
            base = sum(bit << c for c, bit in branch.memory if c not in written)
            out[b, j][:, base | columns] = weight * table
    return out


@lru_cache(maxsize=512)
def _permutations(qargs: tuple[int, ...], n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Axis orders taking (G, F, B, rows, cols) to (G, F, qubit rows, qubit cols, B, other rows, other cols), and back.

    Row axis of qubit q sits at 3 + n - 1 - q, its column axis n later; the
    qubit legs run most significant local bit (qargs[-1]) first.
    """
    rows = [3 + n - 1 - q for q in reversed(qargs)]
    cols = [3 + 2 * n - 1 - q for q in reversed(qargs)]
    rest_rows = [a for a in range(3, 3 + n) if a not in rows]
    rest_cols = [a for a in range(3 + n, 3 + 2 * n) if a not in cols]
    forward = (0, 1, *rows, *cols, 2, *rest_rows, *rest_cols)
    inverse = tuple(int(a) for a in np.argsort(forward))
    return forward, inverse


class NumpyBackend:
    """complex128 numpy arrays on the host."""

    name = "numpy"
    device = "cpu"
    dtype = "complex128"

    def upload(self, array: np.ndarray, real: bool = False) -> Any:
        return np.asarray(array, dtype=np.float64 if real else np.complex128)

    def initial(self, g: int, f: int, d: int) -> Any:
        rho = np.zeros((g, f, 1, d, d), dtype=np.complex128)
        rho[..., 0, 0] = 1
        return rho

    def permute(self, x: Any, axes: tuple[int, ...]) -> Any:
        return np.transpose(x, axes)

    def where(self, mask: Any, left: Any, right: Any) -> Any:
        return np.where(mask, left, right)

    def diagonal(self, x: Any) -> Any:
        return np.real(np.diagonal(x, axis1=-2, axis2=-1)).astype(np.float64)

    def row_max(self, traces: Any) -> np.ndarray:
        return np.max(traces, axis=(0, 1))

    def select(self, x: Any, keep: list[int]) -> Any:
        return x[:, :, keep]

    def einsum(self, subscripts: str, *operands: Any) -> Any:
        return np.einsum(subscripts, *operands)

    def host(self, x: Any) -> np.ndarray:
        return np.asarray(x)

    def expand(self, law: Any, factors: int) -> Any:
        return np.repeat(law, factors, axis=1)

    def synchronize(self) -> None:
        return None


def load_torch() -> Any:
    """The torch module, or None when it is not importable.

    torch.cuda imports pynvml, which raises a FutureWarning about its own
    deprecation; that warning alone is silenced so a ``-W error`` run keeps
    every other warning fatal.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The pynvml package is deprecated", category=FutureWarning)
        try:
            return importlib.import_module("torch")
        except ImportError:
            return None


class TorchBackend:
    """torch tensors on one device in complex64 or complex128; the readout map and probabilities in float64."""

    name = "torch"

    def __init__(self, device: str = "cpu", dtype: str = "complex128") -> None:
        torch = load_torch()
        if torch is None:
            raise SystemExit("the torch engine needs an importable torch")
        if dtype not in ("complex64", "complex128"):
            raise SystemExit(f"dtype {dtype!r} is not complex64 or complex128")
        if device == "cuda" and not torch.cuda.is_available():
            raise SystemExit("torch reports no CUDA device")
        self.torch = torch
        self.device = device
        self.dtype = dtype
        self.complex = getattr(torch, dtype)
        self.real = torch.float32 if dtype == "complex64" else torch.float64

    def upload(self, array: np.ndarray, real: bool = False) -> Any:
        dtype = self.torch.float64 if real else self.complex
        return self.torch.as_tensor(np.ascontiguousarray(array), device=self.device).to(dtype)

    def initial(self, g: int, f: int, d: int) -> Any:
        rho = self.torch.zeros((g, f, 1, d, d), dtype=self.complex, device=self.device)
        rho[..., 0, 0] = 1
        return rho

    def permute(self, x: Any, axes: tuple[int, ...]) -> Any:
        return x.permute(axes)

    def where(self, mask: Any, left: Any, right: Any) -> Any:
        return self.torch.where(mask, left, right)

    def diagonal(self, x: Any) -> Any:
        return self.torch.diagonal(x, dim1=-2, dim2=-1).real.to(self.torch.float64)

    def row_max(self, traces: Any) -> np.ndarray:
        return traces.amax(dim=(0, 1)).cpu().numpy()

    def select(self, x: Any, keep: list[int]) -> Any:
        return x.index_select(2, self.torch.as_tensor(keep, device=self.device))

    def einsum(self, subscripts: str, *operands: Any) -> Any:
        return self.torch.einsum(subscripts, *operands)

    def host(self, x: Any) -> np.ndarray:
        return x.cpu().numpy()

    def expand(self, law: Any, factors: int) -> Any:
        return law.expand(-1, factors, -1, -1)

    def synchronize(self) -> None:
        if self.device == "cuda":
            self.torch.cuda.synchronize()


Backend = NumpyBackend | TorchBackend


@dataclass
class Staged:
    """A plan's operators on one backend: per step its superoperator (local) or padded Kraus stack (dense)."""

    plan: Plan
    form: str
    operators: list[Any]
    projectors: Any


def _padded_kraus(s: np.ndarray) -> np.ndarray:
    """Kraus stacks of every row of a (Gk, Fk, d^2, d^2) superoperator, zero-padded to a common rank."""
    lead = s.shape[:2]
    stacks = [superop_kraus(s[g, f]) for g in range(lead[0]) for f in range(lead[1])]
    rank = max(k.shape[0] for k in stacks)
    d = stacks[0].shape[-1]
    out = np.zeros(lead + (rank, d, d), dtype=np.complex128)
    for index, k in enumerate(stacks):
        out[index // lead[1], index % lead[1], : k.shape[0]] = k
    return out


def stage(plan: Plan, backend: Backend, form: str = "local") -> Staged:
    """Uploads every operator the plan's steps contract and the split projectors."""
    if form not in FORMS:
        raise ValueError(f"form {form!r} is not one of {FORMS}")
    if form == "dense" and backend.name != "torch":
        raise ValueError("the dense form runs on the torch backend")
    operators: list[Any] = []
    for step in plan.steps:
        if isinstance(step, Split):
            operators.append(None)
        elif form == "local":
            operators.append(backend.upload(step.superop))
        else:
            operators.append(backend.upload(_padded_kraus(step.superop)))
    d = 2**plan.n
    projectors: dict[int, Any] = {}
    for step in plan.steps:
        if isinstance(step, Split) and step.qubit not in projectors:
            bits = (np.arange(d) >> step.qubit) & 1
            mask = np.zeros((4, d, d))
            for m, b in itertools.product((0, 1), (0, 1)):
                mask[2 * m + b] = np.outer(bits == m, bits == m)
            projectors[step.qubit] = backend.upload(mask)
    return Staged(plan=plan, form=form, operators=operators, projectors=projectors)


def _apply_local(rho: Any, qargs: tuple[int, ...], s: Any, n: int, backend: Backend) -> Any:
    g, f, b = rho.shape[:3]
    k = len(qargs)
    forward, inverse = _permutations(qargs, n)
    x = backend.permute(rho.reshape((g, f, b) + (2,) * (2 * n)), forward)
    x = x.reshape((g, f, 4**k, b * 4 ** (n - k)))
    y = (s @ x).reshape((g, f) + (2,) * (2 * k) + (b,) + (2,) * (2 * (n - k)))
    return backend.permute(y, inverse).reshape(rho.shape)


def _apply_dense(rho: Any, qargs: tuple[int, ...], kraus: Any, n: int, backend: TorchBackend) -> Any:
    torch = backend.torch
    rest = 2 ** (n - len(qargs))
    gk, fk, rank = kraus.shape[:3]
    # E_a = K_a (x) I on (qubit legs, other legs), then permuted to the register order.
    eye = torch.eye(rest, dtype=kraus.dtype, device=kraus.device)
    lifted = (kraus[:, :, :, :, None, :, None] * eye[None, None, None, None, :, None, :]).reshape(
        (gk, fk, rank) + (2,) * (2 * n)
    )
    # Axis order of lifted after its rank axis: qubit rows, other rows, qubit cols, other cols.
    rows = [n - 1 - q for q in reversed(qargs)]
    rest_rows = [a for a in range(n) if a not in rows]
    order = rows + rest_rows
    position = [order.index(a) for a in range(n)]
    axes = (0, 1, 2, *[3 + p for p in position], *[3 + n + p for p in position])
    embedded = lifted.permute(axes).reshape(gk, fk, rank, 2**n, 2**n)
    left = embedded[:, :, None] @ rho[:, :, :, None]
    return (left @ embedded.conj().transpose(-2, -1)[:, :, None]).sum(dim=3)


def evolve(
    staged: Staged,
    backend: Backend,
    factors: Sequence[float],
    flip: Callable[[float, float], float],
    prune: float = PRUNE_FLOOR,
) -> tuple[Any, dict[str, int]]:
    """The register law of every row, (G, F, len(factors), 2^num_clbits) float64 on the backend, and branch counts."""
    plan = staged.plan
    n = plan.n
    d = 2**n
    g, f = plan.rows
    rho = backend.initial(g, f, d)
    branches = [Branch()]
    masks = _segment_masks(plan, 0, branches, backend)
    for index, (step, operator) in enumerate(zip(plan.steps, staged.operators, strict=True)):
        if isinstance(step, Split):
            children = rho[:, :, :, None] * staged.projectors[step.qubit]
            rho = children.reshape((g, f, 4 * len(branches), d, d))
            branches = [
                parent.child(step.qubit, step.clbit, m, b)
                for parent in branches
                for m, b in itertools.product((0, 1), (0, 1))
            ]
            top = backend.row_max(backend.diagonal(rho).sum(-1))
            keep = [j for j in range(len(branches)) if top[j] >= prune]
            if len(keep) < len(branches):
                rho = backend.select(rho, keep)
                branches = [branches[j] for j in keep]
            masks = _segment_masks(plan, index + 1, branches, backend)
            continue
        if staged.form == "local":
            out = _apply_local(rho, step.qargs, operator, n, backend)
        else:
            assert isinstance(backend, TorchBackend)
            out = _apply_dense(rho, step.qargs, operator, n, backend)
        rho = out if step.when is None else backend.where(masks[index], out, rho)
    weights = backend.upload(readout_map(plan, branches, factors, flip), real=True)
    law = backend.einsum("gfbx,brxo->gfro", backend.diagonal(rho), weights)
    if f != plan.factors:
        law = backend.expand(law, plan.factors)
    return law, {"splits": plan.splits, "children": 4**plan.splits, "live": len(branches), "ops": plan.ops}


def _segment_masks(plan: Plan, start: int, branches: Sequence[Branch], backend: Backend) -> dict[int, Any]:
    """Branch masks, (1, 1, B, 1, 1), of the conditional steps from start up to the next split."""
    masks: dict[int, Any] = {}
    for index in range(start, len(plan.steps)):
        step = plan.steps[index]
        if isinstance(step, Split):
            break
        if step.when is not None:
            row = np.array([step.when.test(dict(branch.memory)) for branch in branches])
            mask = backend.upload(row[None, None, :, None, None].astype(float), real=True) > 0.5
            masks[index] = mask
    return masks
