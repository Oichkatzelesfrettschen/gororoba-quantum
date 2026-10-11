"""Reversible constant modular multiplication with explicit synthesis profiles.

The fast path recognizes multiplication by signed powers of two modulo a
Mersenne number as a cyclic permutation of qubit wires followed, for a
negative power, by bit inversion. Generic synthesis exposes an ANF
compute/swap/uncompute network, a scratch-free Gray-path cycle network, and an
explicit one-clean-ancilla Gray-path network. The default uses the one-clean
network selected by the bounded FakeFez compiler race.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from boolean_anf import anf_coefficients, anf_degree_from_coefficients, evaluate_anf

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

MAX_ANF_WIDTH = 8
InputDomain = Literal["full_register", "nonzero_residues"]
FULL_REGISTER: InputDomain = "full_register"
NONZERO_RESIDUES: InputDomain = "nonzero_residues"


@dataclass(frozen=True)
class MersennePowerOfTwo:
    """Signed power-of-two representation for one Mersenne multiplier."""

    shift: int
    negative: bool


@dataclass(frozen=True)
class MultiplierProfile:
    """Static coefficients for one controlled modular-multiplier synthesis."""

    modulus: int
    multiplier: int
    width: int
    input_domain: InputDomain
    strategy: str
    scratch_qubits: int
    forward_term_count: int
    inverse_term_count: int
    maximum_anf_degree: int
    degree_histogram: tuple[tuple[int, int], ...]
    controlled_swap_count: int
    controlled_x_count: int
    basis_edge_gate_count: int
    maximum_control_count: int

    @property
    def controlled_anf_gate_count(self) -> int:
        return self.forward_term_count + self.inverse_term_count


@dataclass(frozen=True)
class XorDisplacementProfile:
    """XOR-displacement fibers of one full-register permutation.

    ``signed_xor_lcu_normalization_floor`` is the effective-normalization floor
    for a nonzero exact scaled LCU over signed XOR translations. The same value
    is the coefficient one-norm floor at unit output scale. The profile does not
    assert that the Cayley-Dickson group span contains the permutation.
    """

    width: int
    fiber_sizes: tuple[tuple[int, int], ...]

    @property
    def distinct_displacement_count(self) -> int:
        return len(self.fiber_sizes)

    @property
    def signed_xor_lcu_normalization_floor(self) -> int:
        return self.distinct_displacement_count


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


def xor_displacement_profile(permutation: tuple[int, ...]) -> XorDisplacementProfile:
    """Partition a power-of-two permutation by ``input XOR output``.

    For ``M`` inputs and ``T`` occupied fibers, complete-register validation
    and the sorted fiber census use ``O(M + T log T)`` time and ``O(M)``
    auxiliary space.
    """
    state_count = len(permutation)
    if state_count == 0 or state_count & (state_count - 1):
        raise ValueError(f"permutation size must be a positive power of two, got {state_count}")
    if any(output_value < 0 or output_value >= state_count for output_value in permutation):
        raise ValueError("displacement profile requires every output to lie in the complete register")
    if len(set(permutation)) != state_count:
        raise ValueError("displacement profile requires a bijection of the complete register")
    fiber_counts = Counter(input_value ^ output_value for input_value, output_value in enumerate(permutation))
    return XorDisplacementProfile(
        width=state_count.bit_length() - 1,
        fiber_sizes=tuple(sorted(fiber_counts.items())),
    )


def modular_displacement_profile(modulus: int, multiplier: int) -> XorDisplacementProfile:
    """Return the XOR-displacement profile for an identity-padded multiplier."""
    return xor_displacement_profile(modular_permutation(modulus, multiplier))


def _output_coefficients(permutation: tuple[int, ...], width: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        anf_coefficients([(output_value >> output_bit) & 1 for output_value in permutation])
        for output_bit in range(width)
    )


def _mersenne_power_of_two(modulus: int, multiplier: int) -> MersennePowerOfTwo | None:
    width = register_width(modulus)
    if modulus != (1 << width) - 1:
        return None
    normalized = multiplier % modulus
    for shift in range(width):
        if (1 << shift) % modulus == normalized:
            return MersennePowerOfTwo(shift, False)
    for shift in range(width):
        if -(1 << shift) % modulus == normalized:
            return MersennePowerOfTwo(shift, True)
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


def multiplier_profile(
    modulus: int,
    multiplier: int,
    strategy: str = "auto",
    *,
    input_domain: InputDomain = FULL_REGISTER,
) -> MultiplierProfile:
    """Extract synthesis strategy and coefficient counts without building a circuit."""
    if strategy not in (
        "auto",
        "cycle_transpositions",
        "cycle_transpositions_1_clean",
        "anf_compute_swap_uncompute",
    ):
        raise ValueError(f"unknown modular multiplier strategy {strategy!r}")
    if input_domain not in (FULL_REGISTER, NONZERO_RESIDUES):
        raise ValueError(f"unknown modular multiplier input domain {input_domain!r}")
    width = register_width(modulus)
    normalized = multiplier % modulus
    if math.gcd(normalized, modulus) != 1:
        raise ValueError(f"multiplier {multiplier} is not invertible modulo {modulus}")
    if normalized == 1:
        return MultiplierProfile(
            modulus=modulus,
            multiplier=normalized,
            width=width,
            input_domain=input_domain,
            strategy="identity",
            scratch_qubits=0,
            forward_term_count=0,
            inverse_term_count=0,
            maximum_anf_degree=0,
            degree_histogram=(),
            controlled_swap_count=0,
            controlled_x_count=0,
            basis_edge_gate_count=0,
            maximum_control_count=0,
        )

    mersenne_power = _mersenne_power_of_two(modulus, normalized)
    if mersenne_power is not None:
        endpoint_correction_edges = 2 * width - 1 if mersenne_power.negative and input_domain == FULL_REGISTER else 0
        return MultiplierProfile(
            modulus=modulus,
            multiplier=normalized,
            width=width,
            input_domain=input_domain,
            strategy="mersenne_signed_rotation" if mersenne_power.negative else "mersenne_rotation",
            scratch_qubits=0,
            forward_term_count=0,
            inverse_term_count=0,
            maximum_anf_degree=0,
            degree_histogram=(),
            controlled_swap_count=len(rotation_swap_pairs(width, mersenne_power.shift)),
            controlled_x_count=width if mersenne_power.negative else 0,
            basis_edge_gate_count=endpoint_correction_edges,
            maximum_control_count=width if endpoint_correction_edges else 1,
        )

    if width > MAX_ANF_WIDTH:
        raise ValueError(
            f"generic ANF synthesis is bounded to {MAX_ANF_WIDTH} input qubits; modulus {modulus} needs {width}"
        )
    permutation = modular_permutation(modulus, normalized)
    forward = _output_coefficients(permutation, width)
    inverse = _output_coefficients(modular_permutation(modulus, pow(normalized, -1, modulus)), width)
    all_coefficients = tuple(mask for output in forward + inverse for mask in output)
    histogram = Counter(mask.bit_count() for mask in all_coefficients)
    selected_strategy = "cycle_transpositions_1_clean" if strategy == "auto" else strategy
    if selected_strategy == "anf_compute_swap_uncompute":
        scratch_qubits = width
    elif selected_strategy == "cycle_transpositions_1_clean":
        scratch_qubits = 1
    else:
        scratch_qubits = 0
    cycle_strategy = selected_strategy in ("cycle_transpositions", "cycle_transpositions_1_clean")
    return MultiplierProfile(
        modulus=modulus,
        multiplier=normalized,
        width=width,
        input_domain=input_domain,
        strategy=selected_strategy,
        scratch_qubits=scratch_qubits,
        forward_term_count=sum(len(output) for output in forward),
        inverse_term_count=sum(len(output) for output in inverse),
        maximum_anf_degree=max((anf_degree_from_coefficients(output) for output in forward + inverse), default=0),
        degree_histogram=tuple(sorted(histogram.items())),
        controlled_swap_count=width if selected_strategy == "anf_compute_swap_uncompute" else 0,
        controlled_x_count=0,
        basis_edge_gate_count=basis_edge_gate_count(permutation) if cycle_strategy else 0,
        maximum_control_count=width if cycle_strategy else max(histogram, default=0) + 1,
    )


def _append_controlled_basis_edge(
    circuit: QuantumCircuit,
    phase_control: int,
    data_qubits: list[int],
    workspace_qubits: list[int],
    first: int,
    second: int,
) -> None:
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
    target_qubit = data_qubits[target_bit]
    if workspace_qubits:
        from qiskit.synthesis import synth_mcx_1_clean_kg24

        if len(workspace_qubits) != 1:
            raise ValueError(f"one-clean basis-edge synthesis needs one workspace qubit, got {len(workspace_qubits)}")
        open_controls = [
            data_qubit
            for bit_index, data_qubit in enumerate(data_qubits)
            if bit_index != target_bit and not first & (1 << bit_index)
        ]
        for open_control in open_controls:
            circuit.x(open_control)
        circuit.compose(
            synth_mcx_1_clean_kg24(len(controls)),
            qubits=controls + [target_qubit] + workspace_qubits,
            inplace=True,
        )
        for open_control in reversed(open_controls):
            circuit.x(open_control)
        return

    from qiskit.circuit.library import MCXGate

    gate = MCXGate(len(controls), ctrl_state=control_state)
    circuit.append(gate, controls + [target_qubit])


def _append_controlled_basis_transposition(
    circuit: QuantumCircuit,
    phase_control: int,
    data_qubits: list[int],
    workspace_qubits: list[int],
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
        _append_controlled_basis_edge(
            circuit,
            phase_control,
            data_qubits,
            workspace_qubits,
            path[path_index],
            path[path_index + 1],
        )
    for path_index in reversed(range(len(path) - 2)):
        _append_controlled_basis_edge(
            circuit,
            phase_control,
            data_qubits,
            workspace_qubits,
            path[path_index],
            path[path_index + 1],
        )


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
    *,
    input_domain: InputDomain = FULL_REGISTER,
) -> MultiplierProfile:
    """Append controlled multiplication on the declared domain and restore scratch."""
    profile = multiplier_profile(modulus, multiplier, strategy, input_domain=input_domain)
    if len(data_qubits) != profile.width:
        raise ValueError(f"data register has {len(data_qubits)} qubits, expected {profile.width}")
    if len(scratch_qubits) != profile.scratch_qubits:
        raise ValueError(f"{profile.strategy} needs {profile.scratch_qubits} scratch qubits, got {len(scratch_qubits)}")
    if profile.strategy == "identity":
        return profile
    if profile.strategy in ("mersenne_rotation", "mersenne_signed_rotation"):
        mersenne_power = _mersenne_power_of_two(modulus, profile.multiplier)
        if mersenne_power is None:
            raise RuntimeError("Mersenne rotation profile lost its signed power-of-two representation")
        for first, second in rotation_swap_pairs(profile.width, mersenne_power.shift):
            circuit.cswap(phase_control, data_qubits[first], data_qubits[second])
        if mersenne_power.negative:
            for data_qubit in data_qubits:
                circuit.cx(phase_control, data_qubit)
            if input_domain == FULL_REGISTER:
                _append_controlled_basis_transposition(
                    circuit,
                    phase_control,
                    data_qubits,
                    [],
                    0,
                    modulus,
                )
        return profile
    if profile.strategy in ("cycle_transpositions", "cycle_transpositions_1_clean"):
        permutation = modular_permutation(modulus, profile.multiplier)
        for cycle in _pivoted_cycles(permutation):
            for value in cycle[1:]:
                _append_controlled_basis_transposition(
                    circuit,
                    phase_control,
                    data_qubits,
                    scratch_qubits,
                    cycle[0],
                    value,
                )
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


def _verify_multiplier(
    modulus: int,
    multiplier: int,
    strategy: str = "auto",
    *,
    input_domain: InputDomain = FULL_REGISTER,
) -> None:
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector

    profile = multiplier_profile(modulus, multiplier, strategy, input_domain=input_domain)
    qubit_count = 1 + profile.width + profile.scratch_qubits
    control = qubit_count - 1
    data = list(range(profile.width))
    scratch = list(range(profile.width, control))
    circuit = QuantumCircuit(qubit_count)
    append_controlled_modular_multiply(
        circuit,
        control,
        data,
        scratch,
        modulus,
        multiplier,
        strategy,
        input_domain=input_domain,
    )
    permutation = modular_permutation(modulus, multiplier)
    matrix = Operator(circuit).data if qubit_count <= 8 else None
    for control_value in (0, 1):
        if control_value == 0 or input_domain == FULL_REGISTER:
            input_values = range(1 << profile.width)
        else:
            input_values = range(1, modulus)
        for input_value in input_values:
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


def _verify_xor_displacement_profiles() -> None:
    named_counts = {
        (15, 2): 8,
        (15, 7): 7,
        (21, 2): 16,
        (35, 2): 30,
    }
    for (modulus, multiplier), expected_count in named_counts.items():
        observed_count = modular_displacement_profile(modulus, multiplier).distinct_displacement_count
        if observed_count != expected_count:
            raise RuntimeError(
                f"{multiplier} mod {modulus} has {observed_count} XOR displacements, expected {expected_count}"
            )

    identity_profile = modular_displacement_profile(15, 1)
    if identity_profile.fiber_sizes != ((0, 16),):
        raise RuntimeError(f"identity displacement fiber changed: {identity_profile.fiber_sizes}")

    checked_odd_moduli = 0
    checked_mersenne_rotations = 0
    checked_mersenne_reflections = 0
    for width in range(2, 9):
        first_odd_modulus = (1 << (width - 1)) | 1
        for modulus in range(first_odd_modulus, 1 << width, 2):
            displacement_count = modular_displacement_profile(modulus, 2).distinct_displacement_count
            proven_floor = (modulus + 1) // 2
            if displacement_count < proven_floor:
                raise RuntimeError(
                    f"2 mod {modulus} has {displacement_count} XOR displacements below floor {proven_floor}"
                )
            checked_odd_moduli += 1

        mersenne_modulus = (1 << width) - 1
        for shift in range(width):
            multiplier = pow(2, shift, mersenne_modulus)
            displacement_count = modular_displacement_profile(mersenne_modulus, multiplier).distinct_displacement_count
            expected_count = 1 << (width - math.gcd(width, shift))
            if displacement_count != expected_count:
                raise RuntimeError(
                    f"rotate {shift} at width {width} has {displacement_count} XOR displacements, "
                    f"expected {expected_count}"
                )
            checked_mersenne_rotations += 1

        reflection_count = modular_displacement_profile(
            mersenne_modulus, mersenne_modulus - 1
        ).distinct_displacement_count
        if reflection_count != 2:
            raise RuntimeError(f"negation mod {mersenne_modulus} has {reflection_count} XOR displacements, expected 2")
        checked_mersenne_reflections += 1

    checked_low_dispersion_members = 0
    for exponent in range(2, 13):
        power = 1 << exponent
        quotient = power + 1
        modulus = 3 * quotient
        multiplier = 2 * quotient + 1
        permutation = modular_permutation(modulus, multiplier)
        branch_displacements: dict[str, set[int]] = {
            "fixed": set(),
            "+q": set(),
            "-q": set(),
            "+2q": set(),
            "-2q": set(),
        }
        for input_value, output_value in enumerate(permutation):
            if input_value >= modulus or input_value % 3 == 0:
                branch_name = "fixed"
            elif input_value % 3 == 1:
                branch_name = "+2q" if input_value < quotient else "-q"
            else:
                branch_name = "+q" if input_value < 2 * quotient else "-2q"
            branch_displacements[branch_name].add(input_value ^ output_value)

        lower_q_masks = {power + (1 << mask_width) - 1 for mask_width in range(1, exponent)}
        upper_q_masks = {3 * power + (1 << mask_width) - 1 for mask_width in range(1, exponent - 1)}
        expected_plus_q = lower_q_masks | upper_q_masks | {4 * power - 1}
        ordinary_2q_masks = {2 * power + (1 << (mask_width + 1)) - 2 for mask_width in range(1, exponent)}
        if exponent % 2 == 0:
            expected_branch_displacements = {
                "fixed": {0},
                "+q": expected_plus_q,
                "-q": expected_plus_q,
                "+2q": ordinary_2q_masks,
                "-2q": ordinary_2q_masks,
            }
            expected_order = 2
        else:
            expected_branch_displacements = {
                "fixed": {0},
                "+q": expected_plus_q,
                "-q": lower_q_masks
                | {3 * power - 1}
                | {3 * power + (1 << mask_width) - 1 for mask_width in range(1, exponent)},
                "+2q": {2 * power + (1 << (mask_width + 1)) - 2 for mask_width in range(1, exponent - 1)}
                | {4 * power - 2},
                "-2q": {2 * power + (1 << (mask_width + 1)) - 2 for mask_width in range(1, exponent - 1)}
                | {3 * power - 2},
            }
            expected_order = 3
        if branch_displacements != expected_branch_displacements:
            raise RuntimeError(
                f"low-dispersion branch fibers changed for exponent {exponent}: "
                f"observed {branch_displacements}, expected {expected_branch_displacements}"
            )

        expected_count = 3 * exponent - 2 if exponent % 2 == 0 else 3 * exponent + 1
        displacement_profile = xor_displacement_profile(permutation)
        observed_count = displacement_profile.distinct_displacement_count
        if observed_count != expected_count:
            raise RuntimeError(
                f"low-dispersion family member {multiplier} mod {modulus} has {observed_count} XOR displacements, "
                f"expected {expected_count}"
            )
        if pow(multiplier, expected_order, modulus) != 1 or any(
            pow(multiplier, candidate_order, modulus) == 1 for candidate_order in range(1, expected_order)
        ):
            raise RuntimeError(
                f"low-dispersion family member {multiplier} mod {modulus} does not have order {expected_order}"
            )
        if exponent % 2 == 0 and (
            math.gcd(multiplier - 1, modulus) != quotient or math.gcd(multiplier + 1, modulus) != 3
        ):
            raise RuntimeError(
                f"even-exponent family member {multiplier} mod {modulus} does not yield factors {quotient} and 3"
            )
        checked_low_dispersion_members += 1

    mutated_permutation = list(modular_permutation(15, 2))
    mutated_permutation[0] = mutated_permutation[1]
    invalid_permutations = ((), (0, 1, 2), (0, 1, 2, 4), tuple(mutated_permutation))
    for invalid_permutation in invalid_permutations:
        try:
            xor_displacement_profile(invalid_permutation)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"displacement profiler accepted invalid permutation {invalid_permutation}")

    print(
        "XOR displacement effective-normalization floor: "
        f"{checked_odd_moduli} odd base-2 moduli satisfy T >= (N+1)/2; "
        f"{checked_mersenne_rotations} rotations satisfy T=2^(n-gcd(n,k)); "
        f"{checked_mersenne_reflections} reflections have T=2; "
        f"{checked_low_dispersion_members} low-dispersion family members match every branch formula and order"
    )


def _verify() -> None:
    _verify_xor_displacement_profiles()
    for width in range(3, 9):
        modulus = (1 << width) - 1
        for shift in range(width):
            multiplier = -(1 << shift) % modulus
            mersenne_power = _mersenne_power_of_two(modulus, multiplier)
            if mersenne_power != MersennePowerOfTwo(shift, True):
                raise RuntimeError(
                    f"signed Mersenne classifier returned {mersenne_power} for {multiplier} modulo {modulus}"
                )
            for input_value in range(1, modulus):
                rotated = ((input_value << shift) | (input_value >> ((width - shift) % width))) & modulus
                transformed = modulus ^ rotated
                expected = multiplier * input_value % modulus
                if transformed != expected:
                    raise RuntimeError(
                        f"signed Mersenne transform maps {input_value} to {transformed}, expected {expected}"
                    )
            endpoint_outputs = []
            for input_value in (0, modulus):
                rotated = ((input_value << shift) | (input_value >> ((width - shift) % width))) & modulus
                endpoint_outputs.append(modulus ^ rotated)
            if endpoint_outputs != [modulus, 0]:
                raise RuntimeError(
                    f"raw signed Mersenne transform has endpoint outputs {endpoint_outputs}, expected [{modulus}, 0]"
                )
    for multiplier in (1, 2):
        mersenne_power = _mersenne_power_of_two(3, multiplier)
        if mersenne_power is None or mersenne_power.negative:
            raise RuntimeError(f"positive Mersenne recognition lost priority for {multiplier} modulo 3")
    large_mersenne_modulus = (1 << 31) - 1
    large_signed_profile = multiplier_profile(
        large_mersenne_modulus,
        -(1 << 15),
        input_domain=NONZERO_RESIDUES,
    )
    if (
        large_signed_profile.strategy != "mersenne_signed_rotation"
        or large_signed_profile.width != 31
        or large_signed_profile.scratch_qubits != 0
        or large_signed_profile.controlled_x_count != 31
        or large_signed_profile.controlled_swap_count != 30
    ):
        raise RuntimeError(f"unexpected large signed Mersenne profile {large_signed_profile}")
    try:
        multiplier_profile(large_mersenne_modulus, 5)
    except ValueError as error:
        if "generic ANF synthesis is bounded" not in str(error):
            raise
    else:
        raise RuntimeError("wide generic multiplier passed the bounded synthesis guard")

    cases = (
        (15, 2, "auto"),
        (15, 4, "auto"),
        (5, 2, "cycle_transpositions"),
        (9, 2, "cycle_transpositions"),
        (21, 2, "cycle_transpositions"),
        (21, 4, "cycle_transpositions"),
        (21, 16, "cycle_transpositions"),
        (21, 2, "cycle_transpositions_1_clean"),
        (21, 4, "cycle_transpositions_1_clean"),
        (21, 16, "cycle_transpositions_1_clean"),
        (35, 2, "cycle_transpositions"),
        (35, 4, "cycle_transpositions"),
        (35, 11, "cycle_transpositions"),
        (35, 16, "cycle_transpositions"),
        (5, 2, "anf_compute_swap_uncompute"),
        (9, 2, "anf_compute_swap_uncompute"),
        (21, 2, "anf_compute_swap_uncompute"),
        (21, 4, "anf_compute_swap_uncompute"),
        (21, 16, "anf_compute_swap_uncompute"),
    )
    if multiplier_profile(21, 2).strategy != "cycle_transpositions_1_clean":
        raise RuntimeError("automatic generic synthesis must select the lower-CZ one-clean cycle candidate")
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
            f"cx={profile.controlled_x_count} basis_edges={profile.basis_edge_gate_count}"
        )

    signed_swap_counts = {14: 0, 13: 3, 11: 2, 7: 3}
    for input_domain in (FULL_REGISTER, NONZERO_RESIDUES):
        for multiplier, expected_swaps in signed_swap_counts.items():
            profile = multiplier_profile(15, multiplier, input_domain=input_domain)
            expected_edges = 7 if input_domain == FULL_REGISTER else 0
            expected_maximum_controls = 4 if input_domain == FULL_REGISTER else 1
            if (
                profile.strategy != "mersenne_signed_rotation"
                or profile.scratch_qubits != 0
                or profile.controlled_anf_gate_count != 0
                or profile.controlled_swap_count != expected_swaps
                or profile.controlled_x_count != 4
                or profile.basis_edge_gate_count != expected_edges
                or profile.maximum_control_count != expected_maximum_controls
            ):
                raise RuntimeError(f"unexpected signed Mersenne profile {profile}")
            _verify_multiplier(15, multiplier, input_domain=input_domain)
            print(
                f"modular multiply {multiplier} mod 15: strategy={profile.strategy} "
                f"domain={profile.input_domain} qubits=5 cswap={profile.controlled_swap_count} "
                f"cx={profile.controlled_x_count} basis_edges={profile.basis_edge_gate_count}"
            )


if __name__ == "__main__":
    _verify()
