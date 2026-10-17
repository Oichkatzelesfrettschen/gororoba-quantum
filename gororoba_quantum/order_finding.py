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
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator

from factoring import MultiplierResource, OrderFindingPlan, decode_counts, make_order_finding_plan
from modular_arithmetic import (
    NONZERO_RESIDUES,
    _append_controlled_target_flips,
    append_controlled_modular_multiply,
    conjugated_permutation,
    linear_encoding,
    modular_permutation,
    multiplier_profile,
)
from target_flip import target_flip_network

ENCODED_STRATEGY = "target_flip_1_clean"


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


def folded_qpe(phase_label: int, identity: bool = False, *, feed_forward: bool = True) -> QuantumCircuit:
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
    if feed_forward:
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
        profile = multiplier_profile(
            modulus,
            multiplier,
            multiplier_strategy,
            input_domain=NONZERO_RESIDUES,
        )
        resources.append(
            MultiplierResource(
                round_index=round_index,
                exponent=exponent,
                multiplier=multiplier,
                input_domain=profile.input_domain,
                strategy=profile.strategy,
                scratch_qubits=profile.scratch_qubits,
                forward_anf_terms=profile.forward_term_count,
                inverse_anf_terms=profile.inverse_term_count,
                maximum_anf_degree=profile.maximum_anf_degree,
                degree_histogram=profile.degree_histogram,
                controlled_swaps=profile.controlled_swap_count,
                controlled_x_gates=profile.controlled_x_count,
                basis_edge_gates=profile.basis_edge_gate_count,
                maximum_control_count=profile.maximum_control_count,
                controlled_target_flips=profile.controlled_target_flip_count,
                control_arity_histogram=profile.control_arity_histogram,
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
    feed_forward: bool = True,
    work_columns: tuple[int, ...] | None = None,
) -> QuantumCircuit:
    """Build one coherent order-finding attempt or a schedule-matched identity null.

    work_columns names an invertible GF(2) matrix B by its columns and holds
    the work register in the encoding x = B^-1 v: the register starts in
    B^-1 |1> and every round applies the one-clean target-flip network of
    B^-1 f B. The operations between rounds act on the control alone and the
    work register is never measured, so the phase register's law is the
    unencoded circuit's.
    """
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
    if work_columns is None:
        circuit.x(work_qubits[0])
    else:
        if identity or multiplier_strategy != ENCODED_STRATEGY or plan.scratch_qubits != 1:
            raise ValueError(f"an encoded work register needs the {ENCODED_STRATEGY} multiplier and no identity null")
        initial = linear_encoding(work_columns).index(1)
        for bit, qubit in enumerate(work_qubits):
            if initial >> bit & 1:
                circuit.x(qubit)
    for resource in plan.rounds[plan.leading_identity_rounds :]:
        circuit.h(control_qubit)
        if work_columns is None:
            append_controlled_modular_multiply(
                circuit,
                control_qubit,
                work_qubits,
                scratch_qubits if resource.scratch_qubits else [],
                modulus,
                resource.multiplier,
                multiplier_strategy,
                input_domain=NONZERO_RESIDUES,
            )
        else:
            permutation = conjugated_permutation(modular_permutation(modulus, resource.multiplier), work_columns)
            _append_controlled_target_flips(
                circuit, control_qubit, work_qubits, scratch_qubits, target_flip_network(permutation)
            )
        if feed_forward:
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
        plan.input_domain,
        plan.quantum_qubits,
        plan.active_rounds,
        plan.unique_multipliers,
        plan.controlled_swaps,
        plan.controlled_x_gates,
        plan.conditional_phases,
        plan.leading_identity_rounds,
    )
    if coefficients != (NONZERO_RESIDUES, 5, 2, (2, 4), 5, 0, 1, 6):
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
    signed_plan = order_finding_plan(15, 7, 8)
    signed_coefficients = (
        signed_plan.quantum_qubits,
        signed_plan.scratch_qubits,
        signed_plan.unique_multipliers,
        signed_plan.controlled_swaps,
        signed_plan.controlled_x_gates,
        signed_plan.basis_edge_gates,
        signed_plan.maximum_control_count,
    )
    if signed_coefficients != (5, 0, (4, 7), 5, 4, 0, 1):
        raise RuntimeError(f"unexpected signed N=15 resource plan {signed_plan}")
    signed_strategies = {resource.strategy for resource in signed_plan.rounds if resource.strategy != "identity"}
    if signed_strategies != {"mersenne_rotation", "mersenne_signed_rotation"}:
        raise RuntimeError(f"unexpected signed N=15 synthesis strategies {sorted(signed_strategies)}")
    signed_counts = simulator.run(factor_order_finding(15, 7, 8), shots=2048, seed_simulator=7).result().get_counts()
    if set(signed_counts) != expected_support:
        raise RuntimeError(f"signed N=15 phase support {sorted(signed_counts)}, expected {sorted(expected_support)}")
    signed_decoded = decode_counts(signed_counts, 8, 15, 7)
    signed_factors = {factor for recovery, _ in signed_decoded for factor in recovery.factors}
    if signed_factors != {3, 5}:
        raise RuntimeError(f"signed N=15 recovered factors {sorted(signed_factors)}, expected [3, 5]")
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
    generic_plan = order_finding_plan(21, 2, 10, multiplier_strategy="cycle_transpositions_1_clean")
    if generic_plan.quantum_qubits != 7 or generic_plan.unique_multipliers != (2, 4, 16):
        raise RuntimeError(f"unexpected N=21 resource plan {generic_plan}")
    generic_strategies = {resource.strategy for resource in generic_plan.rounds if resource.strategy != "identity"}
    if generic_strategies != {"cycle_transpositions_1_clean"}:
        raise RuntimeError(f"unexpected N=21 synthesis strategies {sorted(generic_strategies)}")
    generic_circuit = factor_order_finding(21, 2, 10, multiplier_strategy="cycle_transpositions_1_clean")
    generic_operations = generic_circuit.count_ops()
    expected_synthesis_counts = {"rccx": 2_694, "ccx": 449}
    observed_synthesis_counts = {
        operation: generic_operations.get(operation, 0) for operation in expected_synthesis_counts
    }
    opaque_mcx_operations = {
        name: count for name, count in generic_operations.items() if name == "mcx" or name.startswith("mcx_o")
    }
    if observed_synthesis_counts != expected_synthesis_counts or opaque_mcx_operations:
        raise RuntimeError(
            f"N=21 one-clean source synthesis is {dict(generic_operations)}, "
            f"expected {expected_synthesis_counts} and zero opaque MCX gates; "
            f"opaque operations are {opaque_mcx_operations}"
        )

    target_plan = order_finding_plan(21, 2, 10)
    target_counts = (
        target_plan.quantum_qubits,
        target_plan.controlled_target_flips,
        target_plan.basis_edge_gates,
        target_plan.control_arity_histogram,
    )
    if target_counts != (7, 170, 0, ((2, 20), (3, 87), (4, 20), (5, 43))):
        raise RuntimeError(f"unexpected N=21 target-flip coefficients {target_counts}")
    target_operations = factor_order_finding(21, 2, 10).count_ops()
    if target_operations.get("rccx", 0) != 512 or target_operations.get("ccx", 0) != 170:
        raise RuntimeError(f"unexpected N=21 target-flip synthesis {dict(target_operations)}")
    target_phase_bits = 5
    target_simulation_circuit = transpile(
        factor_order_finding(21, 2, target_phase_bits), simulator, optimization_level=0
    )
    target_counts_sampled = simulator.run(target_simulation_circuit, shots=2048, seed_simulator=7).result().get_counts()
    target_decoded = decode_counts(target_counts_sampled, target_phase_bits, 21, 2)
    target_factors = {factor for recovery, _ in target_decoded for factor in recovery.factors}
    if target_factors != {3, 7}:
        raise RuntimeError(f"N=21 target flips recovered factors {sorted(target_factors)}, expected [3, 7]")
    target_null_counts = (
        simulator.run(factor_order_finding(21, 2, target_phase_bits, identity=True), shots=512, seed_simulator=7)
        .result()
        .get_counts()
    )
    if target_null_counts != {"00000": 512}:
        raise RuntimeError(f"N=21 five-bit identity null returned {target_null_counts}")


def _without_feed_forward(circuit: QuantumCircuit) -> QuantumCircuit:
    """circuit with every conditional phase removed: the control measures with no inverse-QFT correction."""
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name not in ("if_else", "if_test"):
            out.append(instruction)
    return out


def _distribution(counts: dict[str, int], phase_bits: int) -> list[float]:
    total = sum(counts.values())
    return [counts.get(format(label, f"0{phase_bits}b"), 0) / total for label in range(1 << phase_bits)]


def _verify_feed_forward_sensitivity(simulator: AerSimulator) -> None:
    """Which order-finding circuits test the semiclassical inverse QFT at all.

    For a power-of-two order the control is entangled with orthogonal work
    states at every round, so the ideal outcome distribution is the same
    with and without the conditional phases (Martin-Lopez et al. 2012, page
    2); every unit modulo 15 has order 2 or 4, so the N = 15 factor yield
    cannot detect a broken feed-forward. N = 21, a = 4 (order 3) at two phase
    bits reads (3/8, 1/4, 1/8, 1/4) with the feed-forward and
    (3/8, 1/8, 1/8, 3/8) without, 1/8 apart in total variation; folded QPE on
    an eigenstate reads one outcome with the feed-forward and a split
    without.
    """
    from qpe_diagnostics import n21_labeled_law

    shots = 20000
    insensitive = factor_order_finding(15, 2, 8)
    with_ff = simulator.run(insensitive, shots=shots, seed_simulator=11).result().get_counts()
    without_ff = simulator.run(_without_feed_forward(insensitive), shots=shots, seed_simulator=12).result().get_counts()
    if set(with_ff) != set(without_ff) or max(abs(with_ff[k] - without_ff[k]) / shots for k in with_ff) > 0.02:
        raise RuntimeError(f"N=15 a=2 outcome distribution depends on the feed-forward: {with_ff} vs {without_ff}")
    sensitive = transpile(factor_order_finding(21, 4, 2), simulator, optimization_level=0)
    stripped = transpile(_without_feed_forward(factor_order_finding(21, 4, 2)), simulator, optimization_level=0)
    with_ff = simulator.run(sensitive, shots=shots, seed_simulator=11).result().get_counts()
    without_ff = simulator.run(stripped, shots=shots, seed_simulator=12).result().get_counts()
    expected_with = n21_labeled_law(feed_forward=True)
    expected_without = n21_labeled_law(feed_forward=False)
    if max(abs(a - float(b)) for a, b in zip(_distribution(with_ff, 2), expected_with, strict=True)) > 0.02:
        raise RuntimeError(f"N=21 a=4 two-bit distribution with feed-forward is {with_ff}")
    if max(abs(a - float(b)) for a, b in zip(_distribution(without_ff, 2), expected_without, strict=True)) > 0.02:
        raise RuntimeError(f"N=21 a=4 two-bit distribution without feed-forward is {without_ff}")
    folded = folded_qpe(3)
    folded_with = simulator.run(folded, shots=2000, seed_simulator=11).result().get_counts()
    folded_without = simulator.run(_without_feed_forward(folded), shots=2000, seed_simulator=12).result().get_counts()
    if folded_with != {"11": 2000} or len(folded_without) < 2:
        raise RuntimeError(f"folded QPE s=3 reads {folded_with} with and {folded_without} without the feed-forward")


def _verify() -> None:
    simulator = AerSimulator()
    _verify_folded_conformance(simulator)
    _verify_factor_path(simulator)
    _verify_feed_forward_sensitivity(simulator)
    print(
        "order finding: folded eigenstate controls exact; N=15 bases 2 and 7 sample "
        "{0,64,128,192}, validate order 4, and extract factors 3 and 5; "
        "N=21 target flips recover factors 3 and 7 at five-bit precision; "
        "N=15 outcomes are feed-forward-insensitive, N=21 a=4 at two bits and folded QPE are not"
    )


if __name__ == "__main__":
    _verify()
