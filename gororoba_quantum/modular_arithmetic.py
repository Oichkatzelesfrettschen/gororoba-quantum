"""Reversible constant modular multiplication with explicit synthesis profiles.

The fast path recognizes multiplication by powers of two modulo a Mersenne
number as a cyclic permutation of qubit wires. Generic synthesis exposes an
ANF compute/swap/uncompute network and a scratch-free Gray-path cycle network;
the default follows the lower-CZ ANF result on the bounded FakeFez race.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from boolean_anf import anf_coefficients, anf_degree_from_coefficients, evaluate_anf

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

MAX_ANF_WIDTH = 8


@dataclass(frozen=True)
class MultiplierProfile:
    """Static coefficients for one controlled modular-multiplier synthesis."""

    modulus: int
    multiplier: int
    width: int
    strategy: str
    scratch_qubits: int
    forward_term_count: int
    inverse_term_count: int
    maximum_anf_degree: int
    degree_histogram: tuple[tuple[int, int], ...]
    controlled_swap_count: int
    basis_edge_gate_count: int
    maximum_control_count: int

    @property
    def controlled_anf_gate_count(self) -> int:
        return self.forward_term_count + self.inverse_term_count


def register_width(modulus: int) -> int:
    """Return the number of qubits required to represent residues below modulus."""
    if modulus < 3:
        raise ValueError(f"modulus must be at least 3, got {modulus}")
    return modulus.bit_length()


def modular_permutation(modulus: int, multiplier: int) -> tuple[int, ...]:
    """Extend x -> multiplier*x mod modulus by identity on invalid basis states."""
    width = register_width(modulus)
    normalized = multiplier % modulus
    if math.gcd(normalized, modulus) != 1:
        raise ValueError(f"multiplier {multiplier} is not invertible modulo {modulus}")
    permutation = tuple(normalized * value % modulus if value < modulus else value for value in range(1 << width))
    if len(set(permutation)) != len(permutation):
        raise ValueError(f"modular map for {normalized} modulo {modulus} is not a permutation")
    return permutation


def _output_coefficients(permutation: tuple[int, ...], width: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        anf_coefficients([(output_value >> output_bit) & 1 for output_value in permutation])
        for output_bit in range(width)
    )


def _power_of_two_shift(modulus: int, multiplier: int) -> int | None:
    width = register_width(modulus)
    if modulus != (1 << width) - 1:
        return None
    normalized = multiplier % modulus
    for shift in range(width):
        if (1 << shift) % modulus == normalized:
            return shift
    return None


def rotation_swap_pairs(width: int, shift: int) -> tuple[tuple[int, int], ...]:
    """Return a minimal transposition sequence for a cyclic left bit rotation."""
    normalized = shift % width
    if normalized == 0:
        return ()
    visited: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for start in range(width):
        if start in visited:
            continue
        cycle: list[int] = []
        position = start
        while position not in visited:
            visited.add(position)
            cycle.append(position)
            position = (position + normalized) % width
        for other in cycle[1:]:
            pairs.append((cycle[0], other))
    return tuple(pairs)


def permutation_cycles(permutation: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Return the nontrivial cycles of a packed-basis permutation."""
    visited: set[int] = set()
    cycles: list[tuple[int, ...]] = []
    for start in range(len(permutation)):
        if start in visited:
            continue
        cycle: list[int] = []
        current = start
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = permutation[current]
        if current != start:
            raise ValueError(f"permutation path from {start} enters an earlier cycle at {current}")
        if len(cycle) > 1:
            cycles.append(tuple(cycle))
    return tuple(cycles)


def _pivoted_cycles(permutation: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    pivoted: list[tuple[int, ...]] = []
    for cycle in permutation_cycles(permutation):
        pivot_index = min(
            range(len(cycle)),
            key=lambda index: sum((cycle[index] ^ value).bit_count() for value in cycle),
        )
        pivoted.append(cycle[pivot_index:] + cycle[:pivot_index])
    return tuple(pivoted)


def basis_edge_gate_count(permutation: tuple[int, ...]) -> int:
    """Count fully controlled basis-edge swaps in pivoted Gray-path cycles."""
    return sum(2 * (cycle[0] ^ value).bit_count() - 1 for cycle in _pivoted_cycles(permutation) for value in cycle[1:])


def multiplier_profile(modulus: int, multiplier: int, strategy: str = "auto") -> MultiplierProfile:
    """Extract synthesis strategy and coefficient counts without building a circuit."""
    if strategy not in ("auto", "cycle_transpositions", "anf_compute_swap_uncompute"):
        raise ValueError(f"unknown modular multiplier strategy {strategy!r}")
    width = register_width(modulus)
    normalized = multiplier % modulus
    modular_permutation(modulus, normalized)
    if normalized == 1:
        return MultiplierProfile(modulus, normalized, width, "identity", 0, 0, 0, 0, (), 0, 0, 0)

    shift = _power_of_two_shift(modulus, normalized)
    if shift is not None:
        return MultiplierProfile(
            modulus,
            normalized,
            width,
            "mersenne_rotation",
            0,
            0,
            0,
            0,
            (),
            len(rotation_swap_pairs(width, shift)),
            0,
            1,
        )

    if width > MAX_ANF_WIDTH:
        raise ValueError(
            f"generic ANF synthesis is bounded to {MAX_ANF_WIDTH} input qubits; modulus {modulus} needs {width}"
        )
    forward = _output_coefficients(modular_permutation(modulus, normalized), width)
    inverse = _output_coefficients(modular_permutation(modulus, pow(normalized, -1, modulus)), width)
    all_coefficients = tuple(mask for output in forward + inverse for mask in output)
    histogram = Counter(mask.bit_count() for mask in all_coefficients)
    selected_strategy = "anf_compute_swap_uncompute" if strategy == "auto" else strategy
    scratch_qubits = width if selected_strategy == "anf_compute_swap_uncompute" else 0
    permutation = modular_permutation(modulus, normalized)
    return MultiplierProfile(
        modulus,
        normalized,
        width,
        selected_strategy,
        scratch_qubits,
        sum(len(output) for output in forward),
        sum(len(output) for output in inverse),
        max((anf_degree_from_coefficients(output) for output in forward + inverse), default=0),
        tuple(sorted(histogram.items())),
        width if selected_strategy == "anf_compute_swap_uncompute" else 0,
        basis_edge_gate_count(permutation) if selected_strategy == "cycle_transpositions" else 0,
        width if selected_strategy == "cycle_transpositions" else max(histogram, default=0) + 1,
    )


def _append_controlled_basis_edge(
    circuit: QuantumCircuit,
    phase_control: int,
    data_qubits: list[int],
    first: int,
    second: int,
) -> None:
    from qiskit.circuit.library import MCXGate

    difference = first ^ second
    if difference.bit_count() != 1:
        raise ValueError(f"basis edge endpoints {first} and {second} differ in {difference.bit_count()} bits")
    target_bit = difference.bit_length() - 1
    controls = [phase_control]
    control_state = 1
    for bit_index, data_qubit in enumerate(data_qubits):
        if bit_index == target_bit:
            continue
        control_position = len(controls)
        controls.append(data_qubit)
        if first & (1 << bit_index):
            control_state |= 1 << control_position
    gate = MCXGate(len(controls), ctrl_state=control_state)
    circuit.append(gate, controls + [data_qubits[target_bit]])


def _append_controlled_basis_transposition(
    circuit: QuantumCircuit,
    phase_control: int,
    data_qubits: list[int],
    first: int,
    second: int,
) -> None:
    path = [first]
    current = first
    difference = first ^ second
    for bit_index in range(len(data_qubits)):
        if difference & (1 << bit_index):
            current ^= 1 << bit_index
            path.append(current)
    for path_index in range(len(path) - 1):
        _append_controlled_basis_edge(circuit, phase_control, data_qubits, path[path_index], path[path_index + 1])
    for path_index in reversed(range(len(path) - 2)):
        _append_controlled_basis_edge(circuit, phase_control, data_qubits, path[path_index], path[path_index + 1])


def _append_controlled_anf(
    circuit: QuantumCircuit,
    phase_control: int,
    source_qubits: list[int],
    target_qubits: list[int],
    output_coefficients: tuple[tuple[int, ...], ...],
) -> None:
    for target_qubit, coefficients in zip(target_qubits, output_coefficients, strict=True):
        for monomial_mask in coefficients:
            controls = [phase_control] + [
                qubit for bit_index, qubit in enumerate(source_qubits) if monomial_mask & (1 << bit_index)
            ]
            if len(controls) == 1:
                circuit.cx(controls[0], target_qubit)
            elif len(controls) == 2:
                circuit.ccx(controls[0], controls[1], target_qubit)
            else:
                circuit.mcx(controls, target_qubit)


def append_controlled_modular_multiply(
    circuit: QuantumCircuit,
    phase_control: int,
    data_qubits: list[int],
    scratch_qubits: list[int],
    modulus: int,
    multiplier: int,
    strategy: str = "auto",
) -> MultiplierProfile:
    """Append controlled in-place multiplication and restore every scratch qubit."""
    profile = multiplier_profile(modulus, multiplier, strategy)
    if len(data_qubits) != profile.width:
        raise ValueError(f"data register has {len(data_qubits)} qubits, expected {profile.width}")
    if len(scratch_qubits) != profile.scratch_qubits:
        raise ValueError(f"{profile.strategy} needs {profile.scratch_qubits} scratch qubits, got {len(scratch_qubits)}")
    if profile.strategy == "identity":
        return profile
    if profile.strategy == "mersenne_rotation":
        shift = _power_of_two_shift(modulus, profile.multiplier)
        if shift is None:
            raise RuntimeError("Mersenne rotation profile lost its power-of-two shift")
        for first, second in rotation_swap_pairs(profile.width, shift):
            circuit.cswap(phase_control, data_qubits[first], data_qubits[second])
        return profile
    if profile.strategy == "cycle_transpositions":
        permutation = modular_permutation(modulus, profile.multiplier)
        for cycle in _pivoted_cycles(permutation):
            for value in cycle[1:]:
                _append_controlled_basis_transposition(circuit, phase_control, data_qubits, cycle[0], value)
        return profile

    forward = _output_coefficients(modular_permutation(modulus, profile.multiplier), profile.width)
    inverse_multiplier = pow(profile.multiplier, -1, modulus)
    inverse = _output_coefficients(modular_permutation(modulus, inverse_multiplier), profile.width)
    _append_controlled_anf(circuit, phase_control, data_qubits, scratch_qubits, forward)
    for data_qubit, scratch_qubit in zip(data_qubits, scratch_qubits, strict=True):
        circuit.cswap(phase_control, data_qubit, scratch_qubit)
    _append_controlled_anf(circuit, phase_control, data_qubits, scratch_qubits, inverse)
    return profile


def _packed_output(coefficients: tuple[tuple[int, ...], ...], input_value: int) -> int:
    output = 0
    for output_bit, bit_coefficients in enumerate(coefficients):
        output |= evaluate_anf(bit_coefficients, input_value) << output_bit
    return output


def _verify_multiplier(modulus: int, multiplier: int, strategy: str = "auto") -> None:
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector

    profile = multiplier_profile(modulus, multiplier, strategy)
    qubit_count = 1 + profile.width + profile.scratch_qubits
    control = qubit_count - 1
    data = list(range(profile.width))
    scratch = list(range(profile.width, control))
    circuit = QuantumCircuit(qubit_count)
    append_controlled_modular_multiply(circuit, control, data, scratch, modulus, multiplier, strategy)
    permutation = modular_permutation(modulus, multiplier)
    matrix = Operator(circuit).data if profile.scratch_qubits == 0 else None
    for control_value in (0, 1):
        for input_value in range(1 << profile.width):
            packed_input = input_value | (control_value << control)
            if matrix is None:
                state = Statevector.from_int(packed_input, 1 << qubit_count).evolve(circuit).data
            else:
                state = matrix[:, packed_input]
            observed = int(np.argmax(np.abs(state)))
            expected_data = permutation[input_value] if control_value else input_value
            expected = expected_data | (control_value << control)
            if observed != expected or abs(state[observed] - 1.0) > 1e-12:
                raise RuntimeError(
                    f"controlled {multiplier} mod {modulus} maps {packed_input} to {observed}, expected {expected}"
                )


def _verify() -> None:
    cases = (
        (15, 2, "auto"),
        (15, 4, "auto"),
        (5, 2, "cycle_transpositions"),
        (9, 2, "cycle_transpositions"),
        (21, 2, "cycle_transpositions"),
        (21, 4, "cycle_transpositions"),
        (21, 16, "cycle_transpositions"),
        (35, 2, "cycle_transpositions"),
        (35, 4, "cycle_transpositions"),
        (35, 11, "cycle_transpositions"),
        (35, 16, "cycle_transpositions"),
        (5, 2, "anf_compute_swap_uncompute"),
        (9, 2, "anf_compute_swap_uncompute"),
        (21, 2, "anf_compute_swap_uncompute"),
    )
    if multiplier_profile(21, 2).strategy != "anf_compute_swap_uncompute":
        raise RuntimeError("automatic generic synthesis must select the lower-CZ ANF candidate")
    for modulus, multiplier, strategy in cases:
        profile = multiplier_profile(modulus, multiplier, strategy)
        permutation = modular_permutation(modulus, multiplier)
        coefficients = _output_coefficients(permutation, profile.width)
        reconstructed = tuple(_packed_output(coefficients, value) for value in range(1 << profile.width))
        if reconstructed != permutation:
            raise RuntimeError(f"ANF reconstruction fails for {multiplier} modulo {modulus}")
        _verify_multiplier(modulus, multiplier, strategy)
        print(
            f"modular multiply {multiplier} mod {modulus}: strategy={profile.strategy} "
            f"qubits={1 + profile.width + profile.scratch_qubits} "
            f"anf_terms={profile.controlled_anf_gate_count} cswap={profile.controlled_swap_count} "
            f"basis_edges={profile.basis_edge_gate_count}"
        )


if __name__ == "__main__":
    _verify()
