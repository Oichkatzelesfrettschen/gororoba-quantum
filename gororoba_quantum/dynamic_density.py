"""Exact branch-resolved density matrices of dynamic ISA circuits under an Aer noise model.

``probabilities(circuit, noise_model)`` returns the recorded distribution over
the circuit's classical bits, clbit 0 least significant (live_run._distribution
order), as Aer's density-matrix and statevector methods sample it, without
sampling. The state is a classical-quantum mixture: one unnormalized density
matrix per classical-register value, whose traces sum to one.

- **Gates** apply their unitary, then the local quantum error
  ``qiskit_aer.utils.insert_noise`` attaches after them; the Kraus stacks and
  the tensor layout are jax_bridge's.
- **measure** projects the qubit onto its true outcome k and records r with
  the readout matrix R[k][r] of the noise model (``ReadoutError.probabilities``),
  so a conditional reads the recorded bit while the state carries the true one.
- **reset** applies the Kraus pair |0><0|, |0><1|, then the reset's local error.
- **if_else** on one clbit or one register applies the true body (or false
  body) to each branch whose recorded value selects it. Body gates carry the
  same local errors as top-level gates: insert_noise leaves bodies untouched
  while Aer attaches the noise model inside them at run time.

The self-test pins those orderings against Aer sampling of a three-qubit
fixture with exaggerated errors and shows that each alternative ordering
(body noise omitted, the reset error before the reset, the conditional on the
true outcome) lies outside the sampled confidence radius.

Circuits with a delay under a noise model that carries custom passes (the
relaxation pass acts on delays only), a quantum error on measure, nested
control flow, loops, switch, expression conditions, or measure or reset
inside a body raise UnsupportedCircuit. A distribution needs one evolution
per circuit; its cost grows with 4^n for n active qubits and with the number
of distinct recorded values.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ClassicalRegister, Clbit, Delay, Gate
from qiskit.quantum_info import Kraus, Operator

from jax_bridge import _Numpy, _subscripts

SKIPPED = {"barrier"}
UNSUPPORTED = ("while_loop", "for_loop", "switch_case", "box")
RESET_KRAUS = np.array([[[1, 0], [0, 0]], [[0, 1], [0, 0]]], dtype=np.complex128)


class UnsupportedCircuit(ValueError):
    """The circuit carries an operation the branch-resolved evolution does not represent."""


@dataclass(frozen=True)
class Semantics:
    """Ordering choices the self-test compares with Aer; the defaults are Aer's.

    body_noise attaches local errors to if_else body gates; reset_error_after
    applies the reset's local error after the reset; recorded_condition
    selects branches by the recorded (readout-flipped) bit rather than the
    true outcome.
    """

    body_noise: bool = True
    reset_error_after: bool = True
    recorded_condition: bool = True


AER = Semantics()


def _active(circuit: QuantumCircuit) -> list[int]:
    qubits: set[int] = set()
    for instruction in circuit.data:
        if instruction.operation.name in SKIPPED:
            continue
        qubits.update(circuit.find_bit(q).index for q in instruction.qubits)
    return sorted(qubits)


def _condition_bits(circuit: QuantumCircuit, condition: Any) -> tuple[list[int], int]:
    """The clbit indices a condition reads, least significant first, and its value."""
    target, value = condition
    if isinstance(target, Clbit):
        return [circuit.find_bit(target).index], int(value)
    if isinstance(target, ClassicalRegister):
        return [circuit.find_bit(bit).index for bit in target], int(value)
    raise UnsupportedCircuit(f"{circuit.name}: condition {condition!r} is not a clbit or register comparison")


class _Evolution:
    """Branch dictionary over recorded register values, each an unnormalized (2,)*2n tensor."""

    def __init__(self, circuit: QuantumCircuit, noise_model: Any, semantics: Semantics) -> None:
        if getattr(noise_model, "_nonlocal_quantum_errors", None):
            raise UnsupportedCircuit("nonlocal quantum errors are outside the branch-resolved model")
        self.noise = noise_model
        self.semantics = semantics
        self.physical = _active(circuit)
        self.index = {q: k for k, q in enumerate(self.physical)}
        self.n = len(self.physical)
        self.num_clbits = circuit.num_clbits
        self.kraus_cache: dict[int, np.ndarray] = {}
        self.subscripts: dict[tuple[int, ...], str] = {}
        # Branch keys are full recorded registers; a classical value carries the
        # true outcome alongside only for the true-outcome comparison semantics.
        rho = np.zeros((2,) * (2 * self.n), dtype=np.complex128)
        rho[(0,) * (2 * self.n)] = 1
        self.branches: dict[tuple[int, int], np.ndarray] = {(0, 0): rho}

    def _apply(self, rho: np.ndarray, qargs: tuple[int, ...], kraus: np.ndarray) -> np.ndarray:
        script = self.subscripts.get(qargs)
        if script is None:
            script = self.subscripts[qargs] = _subscripts(qargs, self.n)
        ops = kraus.reshape((kraus.shape[0],) + (2,) * (2 * len(qargs)))
        return _Numpy.einsum(script, ops, np.conj(ops), rho)

    def _kraus(self, error: Any) -> np.ndarray:
        key = id(error)
        if key not in self.kraus_cache:
            self.kraus_cache[key] = np.asarray(Kraus(error.to_quantumchannel()).data, dtype=np.complex128)
        return self.kraus_cache[key]

    def _local_error(self, name: str, physical: tuple[int, ...]) -> Any:
        local = self.noise._local_quantum_errors.get(name, {}).get(physical)
        return local if local is not None else self.noise._default_quantum_errors.get(name)

    def _readout(self, physical: int) -> np.ndarray:
        error = self.noise._local_readout_errors.get((physical,))
        if error is None:
            error = getattr(self.noise, "_default_readout_error", None)
        return np.eye(2) if error is None else np.asarray(error.probabilities, dtype=float)

    def channel(self, qargs: tuple[int, ...], kraus: np.ndarray, select: Any = None) -> None:
        for key, rho in self.branches.items():
            if select is None or select(key):
                self.branches[key] = self._apply(rho, qargs, kraus)

    def gate(self, operation: Any, physical: tuple[int, ...], noisy: bool, select: Any = None) -> None:
        qargs = tuple(self.index[q] for q in physical)
        self.channel(qargs, Operator(operation).data[None].astype(np.complex128), select)
        if noisy:
            error = self._local_error(operation.name, physical)
            if error is not None:
                self.channel(qargs, self._kraus(error), select)

    def measure(self, physical: int, clbit: int) -> None:
        if self._local_error("measure", (physical,)) is not None:
            raise UnsupportedCircuit(f"measure on qubit {physical} carries a quantum error of unpinned order")
        readout = self._readout(physical)
        axis = self.n - 1 - self.index[physical]
        merged: dict[tuple[int, int], np.ndarray] = {}
        for (recorded, true), rho in self.branches.items():
            for outcome in (0, 1):
                projected = np.zeros_like(rho)
                selector: list[Any] = [slice(None)] * (2 * self.n)
                selector[axis] = outcome
                selector[self.n + axis] = outcome
                projected[tuple(selector)] = rho[tuple(selector)]
                if not np.any(projected):
                    continue
                true_key = (true & ~(1 << clbit)) | (outcome << clbit)
                for written in (0, 1):
                    weight = readout[outcome][written]
                    if weight == 0:
                        continue
                    key = ((recorded & ~(1 << clbit)) | (written << clbit), true_key)
                    merged[key] = merged[key] + weight * projected if key in merged else weight * projected
        self.branches = merged

    def reset(self, physical: int) -> None:
        qargs = (self.index[physical],)
        error = self._local_error("reset", (physical,))
        if error is not None and not self.semantics.reset_error_after:
            self.channel(qargs, self._kraus(error))
        self.channel(qargs, RESET_KRAUS)
        if error is not None and self.semantics.reset_error_after:
            self.channel(qargs, self._kraus(error))

    def if_else(self, circuit: QuantumCircuit, instruction: Any) -> None:
        operation = instruction.operation
        bits, value = _condition_bits(circuit, operation.condition)
        outer_qubits = [circuit.find_bit(q).index for q in instruction.qubits]

        def reads(key: tuple[int, int]) -> int:
            register = key[0] if self.semantics.recorded_condition else key[1]
            return sum(((register >> bit) & 1) << position for position, bit in enumerate(bits))

        for taken, body in zip((True, False), operation.blocks, strict=False):
            if body is None:
                continue

            def select(key: tuple[int, int], taken: bool = taken) -> bool:
                return (reads(key) == value) is taken

            for inner in body.data:
                name = inner.operation.name
                if name in SKIPPED:
                    continue
                if not isinstance(inner.operation, Gate):
                    raise UnsupportedCircuit(f"{circuit.name}: {name} inside an if_else body")
                physical = tuple(outer_qubits[body.find_bit(q).index] for q in inner.qubits)
                self.gate(inner.operation, physical, self.semantics.body_noise, select)

    def distribution(self) -> np.ndarray:
        out = np.zeros(2**self.num_clbits)
        size = 2**self.n
        for (recorded, _true), rho in self.branches.items():
            out[recorded] += float(np.real(np.trace(rho.reshape(size, size))))
        return out


def probabilities(circuit: QuantumCircuit, noise_model: Any, semantics: Semantics = AER) -> np.ndarray:
    """Recorded distribution over circuit's clbits under noise_model, clbit 0 least significant."""
    from qiskit_aer.noise.errors.base_quantum_error import QuantumChannelInstruction
    from qiskit_aer.utils import insert_noise

    if any(isinstance(i.operation, Delay) for i in circuit.data) and noise_model._pass_manager() is not None:
        raise UnsupportedCircuit(f"{circuit.name}: delays under custom noise passes are outside the model")
    evolution = _Evolution(circuit, noise_model, semantics)
    noisy = insert_noise(circuit, noise_model, transpile=False)
    previous: Any = None
    for instruction in noisy.data:
        after_reset = (
            previous is not None
            and previous.operation.name == "reset"
            and list(previous.qubits) == list(instruction.qubits)
        )
        previous = instruction
        operation = instruction.operation
        name = operation.name
        if name in SKIPPED:
            continue
        if name in UNSUPPORTED:
            raise UnsupportedCircuit(f"{circuit.name}: {name} is outside the branch-resolved model")
        physical = tuple(noisy.find_bit(q).index for q in instruction.qubits)
        if name == "measure":
            evolution.measure(physical[0], noisy.find_bit(instruction.clbits[0]).index)
        elif name == "reset":
            evolution.reset(physical[0])
        elif name == "if_else":
            evolution.if_else(noisy, instruction)
        elif isinstance(operation, QuantumChannelInstruction):
            error = operation._quantum_error
            if after_reset:
                continue  # evolution.reset applies the reset error in the order the semantics names
            qargs = tuple(evolution.index[q] for q in physical)
            evolution.channel(qargs, evolution._kraus(error))
        elif isinstance(operation, Gate):
            evolution.gate(operation, physical, noisy=False)
        else:
            raise UnsupportedCircuit(f"{circuit.name}: {name} is outside the branch-resolved model")
    out = evolution.distribution()
    total = math.fsum(out)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"{circuit.name}: branch traces sum to {total}")
    return out / total


def hoeffding_radius(shots: int, outcomes: int, tail: float) -> float:
    """Simultaneous two-sided radius for outcomes empirical frequencies of shots samples at total tail."""
    return math.sqrt(math.log(2 * outcomes / tail) / (2 * shots))


def _fixture() -> tuple[QuantumCircuit, Any]:
    """Three qubits, one mid-circuit measure, reset, a noisy conditional body, four recorded bits."""
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error, pauli_error

    circuit = QuantumCircuit(3, 4, name="dynamic_density_fixture")
    circuit.sx(0)
    circuit.rz(0.7, 0)
    circuit.sx(0)
    circuit.sx(1)
    circuit.cz(0, 1)
    circuit.measure(0, 0)
    circuit.reset(0)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.x(1)
        circuit.sx(2)
    circuit.cz(1, 2)
    circuit.sx(1)
    circuit.measure(1, 1)
    circuit.measure(0, 2)
    circuit.measure(2, 3)
    noise = NoiseModel(basis_gates=["sx", "x", "rz", "cz", "reset", "measure"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.08, 1), ["sx"])
    noise.add_all_qubit_quantum_error(pauli_error([("X", 0.3), ("I", 0.7)]), ["x"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.1, 2), ["cz"])
    noise.add_all_qubit_quantum_error(pauli_error([("X", 0.2), ("I", 0.8)]), ["reset"])
    noise.add_readout_error(ReadoutError([[0.85, 0.15], [0.25, 0.75]]), [0])
    noise.add_readout_error(ReadoutError([[0.95, 0.05], [0.1, 0.9]]), [1])
    noise.add_readout_error(ReadoutError([[0.9, 0.1], [0.05, 0.95]]), [2])
    return circuit, noise


def self_test(shots: int = 400_000, seed: int = 20261017) -> None:
    from qiskit_aer import AerSimulator

    circuit, noise = _fixture()
    exact = probabilities(circuit, noise)
    simulator = AerSimulator(method="density_matrix", noise_model=noise, seed_simulator=seed)
    counts = simulator.run(circuit, shots=shots).result().get_counts()
    sampled = np.zeros(2**circuit.num_clbits)
    for bits, count in counts.items():
        sampled[int(bits.replace(" ", ""), 2)] += count / shots
    radius = hoeffding_radius(shots, sampled.size, 1e-6)
    gap = float(np.max(np.abs(exact - sampled)))
    if gap > radius:
        raise AssertionError(f"exact and sampled distributions differ by {gap} > {radius}")
    for name, semantics in (
        ("body noise omitted", Semantics(body_noise=False)),
        ("reset error before reset", Semantics(reset_error_after=False)),
        ("condition on the true outcome", Semantics(recorded_condition=False)),
    ):
        other = probabilities(circuit, noise, semantics)
        distance = float(np.max(np.abs(other - sampled)))
        if distance <= 3 * radius:
            raise AssertionError(f"{name}: sampling cannot reject it ({distance} <= {3 * radius})")
    try:
        loop = QuantumCircuit(1, 1)
        with loop.for_loop(range(2)):
            loop.x(0)
        probabilities(loop, noise)
    except UnsupportedCircuit:
        pass
    else:
        raise AssertionError("a loop must raise UnsupportedCircuit")
    print(
        f"dynamic density: fixture matches {shots} Aer density-matrix shots within {gap:.5f} "
        f"(radius {radius:.5f}); three alternative orderings rejected"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="pin the branch semantics against Aer sampling")
    parser.add_argument("--shots", type=int, default=400_000)
    args = parser.parse_args()
    if args.self_test:
        self_test(args.shots)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
