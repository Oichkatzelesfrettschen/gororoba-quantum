"""Semiclassical order finding with a recycled control qubit.

``folded_qpe`` preserves the known-eigenstate dynamic-control benchmark for
multiplication by two modulo 15. ``factor_order_finding`` implements the
faithful Shor surface: the work register starts in |1>, the circuit consumes no
known order, and each measured phase bit controls the remaining inverse-QFT
feedback. Exact host code validates measured denominators and factors.
"""

from __future__ import annotations

import math

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator

from factoring import MultiplierResource, OrderFindingPlan, decode_counts, make_order_finding_plan
from modular_arithmetic import append_controlled_modular_multiply, multiplier_profile


def controlled_rotate(qc: QuantumCircuit, ctrl: int, work: list[int], steps: int) -> None:
    """Append the original specialized four-bit controlled rotation."""
    pairs = {1: [(2, 3), (1, 2), (0, 1)], 2: [(0, 2), (1, 3)]}[steps]
    for first, second in pairs:
        qc.cswap(ctrl, work[first], work[second])


def eigenstate_prep(qc: QuantumCircuit, work: list[int], phase_label: int) -> None:
    """Prepare the known |u_s> conformance state for multiplication by two modulo 15."""
    qc.x(work[0])
    for work_index, remaining in ((0, 4), (1, 3), (2, 2)):
        qc.cry(2 * math.acos(math.sqrt(1 / remaining)), work[work_index], work[work_index + 1])
        qc.cx(work[work_index + 1], work[work_index])
    for work_index in range(1, 4):
        qc.p(-2 * math.pi * phase_label * work_index / 4, work[work_index])


def folded_qpe(phase_label: int, identity: bool = False) -> QuantumCircuit:
    """Read a supplied two-bit eigenphase for the dynamic-control conformance test."""
    if phase_label not in range(4):
        raise ValueError(f"phase_label must lie in [0, 4), got {phase_label}")
    control_register = QuantumRegister(1, "ctrl")
    work_register = QuantumRegister(4, "w")
    phase_register = ClassicalRegister(2, "c")
    circuit = QuantumCircuit(
        control_register,
        work_register,
        phase_register,
        name=f"folded_qpe_s{phase_label}" + ("_id" if identity else ""),
    )
    work_qubits = [1, 2, 3, 4]
    eigenstate_prep(circuit, work_qubits, phase_label)
    circuit.h(0)
    if not identity:
        controlled_rotate(circuit, 0, work_qubits, 2)
    circuit.h(0)
    circuit.measure(0, phase_register[0])
    circuit.reset(0)
    circuit.h(0)
    if not identity:
        controlled_rotate(circuit, 0, work_qubits, 1)
    with circuit.if_test((phase_register[0], 1)):
        circuit.p(-math.pi / 2, 0)
    circuit.h(0)
    circuit.measure(0, phase_register[1])
    return circuit


def order_finding_plan(
    modulus: int,
    base: int,
    phase_bits: int | None = None,
    *,
    identity: bool = False,
    multiplier_strategy: str = "auto",
) -> OrderFindingPlan:
    """Extract every modular-power coefficient without constructing a circuit."""
    if modulus < 3:
        raise ValueError(f"modulus must be at least 3, got {modulus}")
    normalized_base = base % modulus
    if normalized_base in (0, 1) or math.gcd(normalized_base, modulus) != 1:
        raise ValueError(f"base {base} must be a nonidentity unit modulo {modulus}")
    precision = 2 * modulus.bit_length() if phase_bits is None else phase_bits
    if precision < 1:
        raise ValueError(f"phase_bits must be positive, got {precision}")
    resources: list[MultiplierResource] = []
    scheduled_multipliers = tuple(
        pow(normalized_base, 1 << (precision - round_index - 1), modulus) for round_index in range(precision)
    )
    leading_identity_rounds = next(
        (index for index, multiplier in enumerate(scheduled_multipliers) if multiplier != 1),
        precision,
    )
    for round_index in range(precision):
        exponent = 1 << (precision - round_index - 1)
        multiplier = 1 if identity else scheduled_multipliers[round_index]
        profile = multiplier_profile(modulus, multiplier, multiplier_strategy)
        resources.append(
            MultiplierResource(
                round_index=round_index,
                exponent=exponent,
                multiplier=multiplier,
                strategy=profile.strategy,
                scratch_qubits=profile.scratch_qubits,
                forward_anf_terms=profile.forward_term_count,
                inverse_anf_terms=profile.inverse_term_count,
                maximum_anf_degree=profile.maximum_anf_degree,
                degree_histogram=profile.degree_histogram,
                controlled_swaps=profile.controlled_swap_count,
                basis_edge_gates=profile.basis_edge_gate_count,
                maximum_control_count=profile.maximum_control_count,
            )
        )
    return make_order_finding_plan(
        modulus,
        normalized_base,
        precision,
        resources,
        leading_identity_rounds=leading_identity_rounds,
    )


def factor_order_finding(
    modulus: int,
    base: int,
    phase_bits: int | None = None,
    *,
    identity: bool = False,
    multiplier_strategy: str = "auto",
) -> QuantumCircuit:
    """Build one coherent order-finding attempt or a schedule-matched identity null."""
    plan = order_finding_plan(
        modulus,
        base,
        phase_bits,
        identity=identity,
        multiplier_strategy=multiplier_strategy,
    )
    control_register = QuantumRegister(1, "ctrl")
    work_register = QuantumRegister(plan.work_qubits, "w")
    scratch_register = QuantumRegister(plan.scratch_qubits, "scratch") if plan.scratch_qubits else None
    phase_register = ClassicalRegister(plan.phase_bits, "phase")
    if scratch_register is None:
        circuit = QuantumCircuit(control_register, work_register, phase_register)
    else:
        circuit = QuantumCircuit(control_register, work_register, scratch_register, phase_register)
    circuit.name = f"shor_order_N{modulus}_a{base % modulus}" + ("_null" if identity else "")
    control_qubit = 0
    work_qubits = list(range(1, 1 + plan.work_qubits))
    scratch_qubits = list(range(1 + plan.work_qubits, plan.quantum_qubits))
    circuit.x(work_qubits[0])
    for resource in plan.rounds[plan.leading_identity_rounds :]:
        circuit.h(control_qubit)
        append_controlled_modular_multiply(
            circuit,
            control_qubit,
            work_qubits,
            scratch_qubits if resource.scratch_qubits else [],
            modulus,
            resource.multiplier,
            multiplier_strategy,
        )
        for prior_round in range(plan.leading_identity_rounds, resource.round_index):
            feedback_angle = -math.pi / (1 << (resource.round_index - prior_round))
            with circuit.if_test((phase_register[prior_round], 1)):
                circuit.p(feedback_angle, control_qubit)
        circuit.h(control_qubit)
        circuit.measure(control_qubit, phase_register[resource.round_index])
        if resource.round_index + 1 < plan.phase_bits:
            circuit.reset(control_qubit)
    return circuit


def _verify_folded_conformance(simulator: AerSimulator) -> None:
    rotation = QuantumCircuit(5)
    controlled_rotate(rotation, 0, [1, 2, 3, 4], 1)
    matrix = Operator(rotation).data
    for input_value in range(16):
        packed_input = 1 + 2 * input_value
        observed = int(np.argmax(np.abs(matrix[:, packed_input])))
        expected_value = 2 * input_value % 15 if input_value < 15 else input_value
        expected = 1 + 2 * expected_value
        if observed != expected:
            raise RuntimeError(
                f"controlled rotation sends {input_value} to {(observed - 1) // 2}, expected {expected_value}"
            )
    for phase_label in range(4):
        preparation = QuantumCircuit(4)
        eigenstate_prep(preparation, [0, 1, 2, 3], phase_label)
        controlled_unitary = QuantumCircuit(5)
        controlled_rotate(controlled_unitary, 0, [1, 2, 3, 4], 1)
        state = Statevector(preparation)
        rotated = state.evolve(Operator(controlled_unitary).data[1::2, 1::2])
        overlap = complex(np.vdot(state.data, rotated.data))
        expected_overlap = np.exp(2j * math.pi * phase_label / 4)
        if abs(overlap - expected_overlap) > 1e-12:
            raise RuntimeError(f"|u_{phase_label}> eigenvalue {overlap}")
        for identity in (False, True):
            counts = simulator.run(folded_qpe(phase_label, identity), shots=512, seed_simulator=1).result().get_counts()
            expected_measurement = 0 if identity else phase_label
            if counts.get(format(expected_measurement, "02b"), 0) != 512:
                raise RuntimeError(
                    f"phase_label={phase_label} identity={identity}: counts {counts}, "
                    f"expected all {expected_measurement}"
                )


def _verify_factor_path(simulator: AerSimulator) -> None:
    plan = order_finding_plan(15, 2, 8)
    coefficients = (
        plan.quantum_qubits,
        plan.active_rounds,
        plan.unique_multipliers,
        plan.controlled_swaps,
        plan.conditional_phases,
        plan.leading_identity_rounds,
    )
    if coefficients != (5, 2, (2, 4), 5, 1, 6):
        raise RuntimeError(f"unexpected N=15 resource plan {plan}")
    circuit = factor_order_finding(15, 2, 8)
    counts = simulator.run(circuit, shots=4096, seed_simulator=7).result().get_counts()
    expected_support = {format(measurement, "08b") for measurement in (0, 64, 128, 192)}
    if set(counts) != expected_support:
        raise RuntimeError(f"N=15 phase support {sorted(counts)}, expected {sorted(expected_support)}")
    decoded = decode_counts(counts, 8, 15, 2)
    recovered_factors = {factor for recovery, _ in decoded for factor in recovery.factors}
    if recovered_factors != {3, 5}:
        raise RuntimeError(f"N=15 recovered factors {sorted(recovered_factors)}, expected [3, 5]")
    null_counts = (
        simulator.run(factor_order_finding(15, 2, 8, identity=True), shots=512, seed_simulator=7).result().get_counts()
    )
    if null_counts != {"00000000": 512}:
        raise RuntimeError(f"N=15 identity null returned {null_counts}")
    null_plan = order_finding_plan(15, 2, 8, identity=True)
    null_schedule = (
        null_plan.leading_identity_rounds,
        null_plan.executed_rounds,
        null_plan.measurements,
        null_plan.resets,
        null_plan.conditional_phases,
    )
    if null_schedule != (6, 2, 2, 1, 1):
        raise RuntimeError(f"N=15 identity null schedule is {null_schedule}")
    generic_plan = order_finding_plan(21, 2, 10)
    if generic_plan.quantum_qubits != 11 or generic_plan.unique_multipliers != (2, 4, 16):
        raise RuntimeError(f"unexpected N=21 resource plan {generic_plan}")


def _verify() -> None:
    simulator = AerSimulator()
    _verify_folded_conformance(simulator)
    _verify_factor_path(simulator)
    print(
        "order finding: folded eigenstate controls exact; N=15 |1> samples "
        "{0,64,128,192}, validates order 4, and extracts factors 3 and 5"
    )


if __name__ == "__main__":
    _verify()
