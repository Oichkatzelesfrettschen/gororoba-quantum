"""Matched QPE controls and independently calculated labeled outcome laws.

The folded family shares logical control 0 and work qubits 1 through 4.
The coherent arm adds control 5 for the first, least-significant phase bit;
control 0 still carries the terminal, most-significant phase bit. A physical
comparison must bind those shared logical qubits to the same device qubits.
The delay arm records only its measured terminal bit, rather than presenting
the supplied eigenstate label as an observed first bit.
"""

from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit import Clbit, ControlFlowOp, Qubit
from qiskit.circuit.library import XGate
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from order_finding import controlled_rotate, eigenstate_prep, factor_order_finding, folded_qpe

FOLDED_RUNGS = ("archived", "delay", "no_feed_forward", "coherent")
FOLDED_CONTROL = 0
FOLDED_WORK = (1, 2, 3, 4)
FOLDED_EXTRA_CONTROL = 5

GaussianInteger = tuple[int, int]
IdealBranch = tuple[float, Statevector, int]
_ROOTS: tuple[GaussianInteger, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


def _validate_folded(phase_label: int, rung: str) -> None:
    if type(phase_label) is not int or phase_label not in range(4):
        raise ValueError("phase_label must be an integer in [0, 4)")
    if rung not in FOLDED_RUNGS:
        raise ValueError(f"unknown folded-QPE rung {rung!r}")


def folded_terminal_clbit(rung: str) -> int:
    """Return the index of the actually measured common terminal observable."""
    _validate_folded(0, rung)
    return 0 if rung == "delay" else 1


def folded_diagnostic(phase_label: int, rung: str, *, measurement_delay_dt: int | None = None) -> QuantumCircuit:
    """Build one control, with a positive calibration-bound delay in dt when requested.

    The delay replaces the first measurement only. Reset remains, and the
    prepared label supplies the unconditional correction. The delay duration
    therefore states a measurement-time assumption, not an equality between
    complete backend schedules or a measurement-only causal intervention.
    """
    _validate_folded(phase_label, rung)
    if rung == "archived":
        circuit = folded_qpe(phase_label)
    elif rung == "no_feed_forward":
        circuit = folded_qpe(phase_label, feed_forward=False)
    else:
        control = QuantumRegister(1, "ctrl")
        work = QuantumRegister(4, "w")
        phase = ClassicalRegister(1 if rung == "delay" else 2, "c")
        circuit = QuantumCircuit(control, work)
        if rung == "coherent":
            circuit.add_register(QuantumRegister(1, "extra_ctrl"))
        circuit.add_register(phase)
        eigenstate_prep(circuit, list(FOLDED_WORK), phase_label)
        first_control = FOLDED_EXTRA_CONTROL if rung == "coherent" else FOLDED_CONTROL
        circuit.h(first_control)
        controlled_rotate(circuit, first_control, list(FOLDED_WORK), 2)
        circuit.h(first_control)
        if rung == "delay":
            if type(measurement_delay_dt) is not int or measurement_delay_dt <= 0:
                raise ValueError("delay control requires a positive integer measurement_delay_dt from calibration")
            circuit.delay(measurement_delay_dt, FOLDED_CONTROL, unit="dt")
            circuit.reset(FOLDED_CONTROL)
        circuit.h(FOLDED_CONTROL)
        controlled_rotate(circuit, FOLDED_CONTROL, list(FOLDED_WORK), 1)
        if rung == "coherent":
            circuit.cp(-math.pi / 2, FOLDED_EXTRA_CONTROL, FOLDED_CONTROL)
        elif phase_label & 1:
            circuit.p(-math.pi / 2, FOLDED_CONTROL)
        circuit.h(FOLDED_CONTROL)
        if rung == "coherent":
            circuit.measure(FOLDED_EXTRA_CONTROL, phase[0])
        circuit.measure(FOLDED_CONTROL, phase[folded_terminal_clbit(rung)])
    circuit.name = f"folded_diagnostic_{rung}_s{phase_label}"
    return circuit


def _multiply(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def _add(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return left[0] + right[0], left[1] + right[1]


def _norm_squared(value: GaussianInteger) -> int:
    return value[0] ** 2 + value[1] ** 2


def folded_ideal(phase_label: int, rung: str) -> tuple[Fraction, ...]:
    """Calculate exact measured laws using the eigenvalue i**phase_label.

    All two-bit laws use y = first_bit + 2 * terminal_bit. The one-bit delay
    law contains only terminal_bit. Deferred measurement gives the coherent
    arm the archived arm's law without asserting equal hardware noise.
    """
    _validate_folded(phase_label, rung)
    eigenvalue = _ROOTS[phase_label]
    squared_eigenvalue = _ROOTS[(2 * phase_label) % 4]
    probabilities = [Fraction(0) for _ in range(2 if rung == "delay" else 4)]
    for first_bit in range(2):
        first_amplitude = _add((1, 0), _multiply(((-1) ** first_bit, 0), squared_eigenvalue))
        correction = _ROOTS[-first_bit % 4] if rung != "no_feed_forward" else (1, 0)
        for terminal_bit in range(2):
            second_amplitude = _add((1, 0), _multiply(((-1) ** terminal_bit, 0), _multiply(correction, eigenvalue)))
            probability = Fraction(_norm_squared(_multiply(first_amplitude, second_amplitude)), 16)
            label = terminal_bit if rung == "delay" else first_bit + 2 * terminal_bit
            probabilities[label] += probability
    return tuple(probabilities)


def folded_terminal_weights(phase_label: int, rung: str) -> tuple[float, ...]:
    """Score the common measured terminal bit against the supplied phase label."""
    _validate_folded(phase_label, rung)
    terminal_bit = folded_terminal_clbit(rung)
    return tuple(float((label >> terminal_bit) == (phase_label >> 1)) for label in range(1 << (terminal_bit + 1)))


def n21_diagnostic(feed_forward: bool = True) -> QuantumCircuit:
    """Build |1> order finding at two phase bits; every recorded bit is measured."""
    circuit = factor_order_finding(21, 4, 2, feed_forward=feed_forward)
    circuit.name = "n21_a4_two_bit_" + ("feed_forward" if feed_forward else "no_feed_forward")
    return circuit


# Bits 0, 2 and 4 of the binary work register hold the orbit 1, 4, 16 of
# multiplication by 4 modulo 21 one-hot; bits 1 and 3 stay zero on the orbit.
N21_ORBIT_BITS = (0, 2, 4)


# Window variants between the first measurement and the second round. Each
# keeps the ideal labeled law and changes one exposure of the work superposition
# |1> +/- |16> while the control is measured and reset.
N21_ORBIT_VARIANTS = ("nominal", "window_delay", "extra_readout", "window_echo")
# window_barrier completes the first round before the first measurement and idles
# the work bits for the same requested echo halves as window_echo, without the
# pulses; elapsed exposure and pulse differences come from the returned schedule.
N21_ORBIT_BUILDABLE = (*N21_ORBIT_VARIANTS, "window_barrier")


def n21_orbit_diagnostic(
    feed_forward: bool = True,
    variant: str = "nominal",
    *,
    window_delay_dt: int | None = None,
    echo_half_dt: int | None = None,
) -> QuantumCircuit:
    """Build the N=21 two-bit diagnostic with multipliers compiled on the orbit of |1>.

    On the orbit, multiplication by 4 cycles the one-hot bits 0 -> 2 -> 4 -> 0,
    two controlled swaps, and multiplication by 16 is its inverse. The
    multipliers act correctly only on the orbit, so constructing them supplies
    the order 3; the circuit measures feed-forward in two-round semiclassical
    QPE with the labeled law of n21_labeled_law and performs no order finding
    (Smolin, Smith and Vargo, Nature 499, 163 (2013), doi:10.1038/nature12290).

    window_delay idles the control for window_delay_dt after its reset, so the
    work superposition waits that much longer before the second round.
    extra_readout measures the control a second time into the first bit, which
    adds one readout of the same duration and leaves the last write as the
    feed-forward bit. window_echo applies X to the work bits for 1 and 16 after
    echo_half_dt and again after a second echo_half_dt, both concurrent with
    the measurement and reset; a static frequency offset on those qubits
    accumulates opposite phases in the two halves and cancels.
    """
    if variant not in N21_ORBIT_BUILDABLE:
        raise ValueError(f"unknown N=21 orbit variant {variant!r}")
    if variant == "window_delay" and (type(window_delay_dt) is not int or window_delay_dt <= 0):
        raise ValueError("window_delay requires a positive integer window_delay_dt from calibration")
    if variant in ("window_echo", "window_barrier") and (type(echo_half_dt) is not int or echo_half_dt <= 0):
        raise ValueError("window_echo requires a positive integer echo_half_dt from calibration")
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(len(N21_ORBIT_BITS), "w")
    phase = ClassicalRegister(2, "phase")
    circuit = QuantumCircuit(control, work, phase)
    one, four, sixteen = 1, 2, 3
    circuit.x(one)
    circuit.h(0)
    circuit.cswap(0, one, four)
    circuit.cswap(0, four, sixteen)
    circuit.h(0)
    if variant == "window_echo":
        assert echo_half_dt is not None
        circuit.barrier()
        for _half in range(2):
            circuit.delay(echo_half_dt, [one, sixteen], unit="dt")
            circuit.x([one, sixteen])
    if variant == "window_barrier":
        assert echo_half_dt is not None
        circuit.barrier()
        circuit.delay(2 * echo_half_dt, [one, sixteen], unit="dt")
    circuit.measure(0, phase[0])
    if variant == "extra_readout":
        circuit.measure(0, phase[0])
    circuit.reset(0)
    if variant == "window_delay":
        assert window_delay_dt is not None
        circuit.delay(window_delay_dt, 0, unit="dt")
    if variant in ("window_echo", "window_barrier"):
        circuit.barrier()
    circuit.h(0)
    circuit.cswap(0, four, sixteen)
    circuit.cswap(0, one, four)
    if feed_forward:
        with circuit.if_test((phase[0], 1)):
            circuit.p(-math.pi / 2, 0)
    circuit.h(0)
    circuit.measure(0, phase[1])
    suffix = "" if variant == "nominal" else f"_{variant}"
    circuit.name = "n21_orbit_a4_two_bit_" + ("feed_forward" if feed_forward else "no_feed_forward") + suffix
    return circuit


def _orbit_branch(
    vector: tuple[GaussianInteger, ...], power: int, sign_phase: GaussianInteger
) -> tuple[GaussianInteger, ...]:
    """Apply I + sign_phase U**power on the exact orbit |1>, |4>, |16>."""
    return tuple(_add(value, _multiply(sign_phase, vector[(index - power) % 3])) for index, value in enumerate(vector))


def n21_labeled_law(feed_forward: bool = True) -> tuple[Fraction, ...]:
    """Calculate the labeled law with integer branch amplitudes, independent of Qiskit.

    The two Hadamard sandwiches give the branch amplitude
    (I + (-1)**b1 * (-i)**b0 U)(I + (-1)**b0 U**2)|1> / 4.
    Removing feedback replaces (-i)**b0 by 1. Classical bit 0 stores b0,
    classical bit 1 stores b1, so the array index is b0 + 2*b1.
    """
    probabilities = [Fraction(0) for _ in range(4)]
    for first_bit in range(2):
        first_branch = _orbit_branch(((1, 0), (0, 0), (0, 0)), 2, ((-1) ** first_bit, 0))
        correction = _ROOTS[-first_bit % 4] if feed_forward else (1, 0)
        for terminal_bit in range(2):
            second_branch = _orbit_branch(first_branch, 1, _multiply(((-1) ** terminal_bit, 0), correction))
            probabilities[first_bit + 2 * terminal_bit] = Fraction(
                sum(_norm_squared(value) for value in second_branch), 16
            )
    return tuple(probabilities)


def _project(state: Statevector, qubit: int, outcome: int) -> tuple[float, Statevector] | None:
    projected = state.data.copy()
    projected[((np.arange(len(projected)) >> qubit) & 1) != outcome] = 0
    probability = float(np.vdot(projected, projected).real)
    if probability < 1e-14:
        return None
    return probability, Statevector(projected / math.sqrt(probability))


def _branch_instructions(
    circuit: QuantumCircuit, branches: list[IdealBranch], qubits: list[int], clbits: list[int]
) -> list[IdealBranch]:
    """Enumerate the finite measurement/reset branches for local conformance checks."""
    for instruction in circuit.data:
        operation = instruction.operation
        physical_qubits = [qubits[circuit.find_bit(qubit).index] for qubit in instruction.qubits]
        physical_clbits = [clbits[circuit.find_bit(clbit).index] for clbit in instruction.clbits]
        if operation.name in ("barrier", "delay"):
            continue
        following: list[IdealBranch] = []
        for weight, state, classical in branches:
            if operation.name in ("measure", "reset"):
                for outcome in range(2):
                    projection = _project(state, physical_qubits[0], outcome)
                    if projection is None:
                        continue
                    probability, projected = projection
                    result = classical
                    if operation.name == "measure":
                        result = (classical & ~(1 << physical_clbits[0])) | (outcome << physical_clbits[0])
                    elif outcome:
                        projected = projected.evolve(XGate(), physical_qubits)
                    following.append((weight * probability, projected, result))
            elif isinstance(operation, ControlFlowOp):
                if operation.name != "if_else":
                    raise ValueError(f"unsupported exact-branch control flow {operation.name}")
                condition_bit, condition_value = operation.condition
                if not isinstance(condition_bit, Clbit):
                    raise ValueError("exact branch check requires a single-bit condition")
                condition_index = clbits[circuit.find_bit(condition_bit).index]
                block_index = 0 if ((classical >> condition_index) & 1) == condition_value else 1
                if block_index < len(operation.blocks):
                    following.extend(
                        _branch_instructions(
                            operation.blocks[block_index],
                            [(weight, state, classical)],
                            physical_qubits,
                            physical_clbits,
                        )
                    )
                else:
                    following.append((weight, state, classical))
            else:
                following.append((weight, state.evolve(operation, physical_qubits), classical))
        branches = following
    return branches


def ideal_branch_probabilities(circuit: QuantumCircuit) -> tuple[float, ...]:
    """Evaluate every ideal branch without shots, for the bounded diagnostic circuits."""
    state = Statevector.from_int(0, 1 << circuit.num_qubits)
    branches = _branch_instructions(
        circuit, [(1.0, state, 0)], list(range(circuit.num_qubits)), list(range(circuit.num_clbits))
    )
    probabilities = [0.0 for _ in range(1 << circuit.num_clbits)]
    for weight, _state, classical in branches:
        probabilities[classical] += weight
    return tuple(probabilities)


def ideal_compiled_probabilities(circuit: QuantumCircuit, *, max_active_qubits: int = 12) -> tuple[float, ...]:
    """Check a bounded ISA circuit after removing idle physical wires through public DAG APIs.

    Barriers impose scheduling constraints and act as the identity in the
    ideal branch calculation. Classical registers retain their recorded-bit
    ordering while inactive device qubits are removed before state allocation.
    """
    if type(max_active_qubits) is not int or max_active_qubits < 1:
        raise ValueError("max_active_qubits must be a positive integer")
    dag = circuit_to_dag(circuit)
    for node in dag.op_nodes():
        if node.op.name == "barrier":
            dag.remove_op_node(node)
    idle_qubits = [wire for wire in dag.idle_wires() if isinstance(wire, Qubit)]
    dag.remove_qubits(*idle_qubits)
    compact = dag_to_circuit(dag)
    if compact.num_qubits > max_active_qubits:
        raise ValueError(
            f"{circuit.name}: ideal ISA gate needs {compact.num_qubits} active qubits, "
            f"above the explicit limit {max_active_qubits}"
        )
    return ideal_branch_probabilities(compact)


def _verify() -> None:
    circuits: list[QuantumCircuit] = []
    expected_laws: list[tuple[Fraction, ...]] = []
    for phase_label in range(4):
        for rung in FOLDED_RUNGS:
            circuit = folded_diagnostic(phase_label, rung, measurement_delay_dt=1234)
            expected = folded_ideal(phase_label, rung)
            writers = {
                circuit.find_bit(inst.clbits[0]).index for inst in circuit.data if inst.operation.name == "measure"
            }
            if writers != set(range(circuit.num_clbits)):
                raise RuntimeError(f"{circuit.name}: each classical bit must have a measurement writer")
            if rung == "delay":
                delays = [inst.operation.duration for inst in circuit.data if inst.operation.name == "delay"]
                if delays != [1234]:
                    raise RuntimeError(f"{circuit.name}: delay duration changed")
            if rung == "coherent" and any(inst.operation.name in ("reset", "if_else") for inst in circuit.data):
                raise RuntimeError("coherent control contains a dynamic operation")
            circuits.append(circuit)
            expected_laws.append(expected)
    for feed_forward in (True, False):
        expected = n21_labeled_law(feed_forward)
        numerators = (3, 2, 1, 2) if feed_forward else (3, 1, 1, 3)
        if expected != tuple(Fraction(numerator, 8) for numerator in numerators):
            raise RuntimeError(f"N=21 exact branch law changed: {expected}")
        circuits.append(n21_diagnostic(feed_forward))
        expected_laws.append(expected)
        for variant in N21_ORBIT_BUILDABLE:
            circuits.append(n21_orbit_diagnostic(feed_forward, variant, window_delay_dt=416, echo_half_dt=512))
            expected_laws.append(expected)
    for circuit, expected in zip(circuits, expected_laws, strict=True):
        observed = ideal_branch_probabilities(circuit)
        if not np.allclose(observed, [float(value) for value in expected], atol=1e-11, rtol=0):
            raise RuntimeError(f"{circuit.name}: exact circuit branches {observed} disagree with {expected}")
        padded = circuit.copy()
        padded.add_register(QuantumRegister(20, "idle"))
        padded.barrier(*padded.qubits)
        if not np.allclose(ideal_compiled_probabilities(padded), observed, atol=1e-11, rtol=0):
            raise RuntimeError(f"{circuit.name}: removing idle physical wires changed the labeled law")
    for original in (n21_diagnostic(), n21_orbit_diagnostic()):
        permuted = QuantumCircuit(original.num_qubits, 2)
        permuted.compose(original, clbits=[1, 0], inplace=True)
        if np.allclose(ideal_branch_probabilities(permuted), [float(value) for value in n21_labeled_law()]):
            raise RuntimeError(f"{original.name}: labeled gate accepted swapped classical bits")
    transposition = n21_orbit_diagnostic()
    sixteen = transposition.qubits[3]
    transposition.data = [
        instruction
        for instruction in transposition.data
        if instruction.operation.name != "cswap" or sixteen not in instruction.qubits
    ]
    if np.allclose(ideal_branch_probabilities(transposition), [float(value) for value in n21_labeled_law()]):
        raise RuntimeError("N=21 orbit gate accepted an order-2 multiplier")
    simulator = AerSimulator()
    compiled = transpile(circuits, simulator, optimization_level=0)
    sampled = simulator.run(compiled, shots=8192, seed_simulator=20261011).result()
    for index, (circuit, expected) in enumerate(zip(circuits, expected_laws, strict=True)):
        counts = sampled.get_counts(index)
        for label, probability in enumerate(expected):
            observed_rate = counts.get(format(label, f"0{circuit.num_clbits}b"), 0) / 8192
            if abs(observed_rate - float(probability)) > 0.025:
                raise RuntimeError(f"{circuit.name}: sampled labeled law {counts} disagrees with {expected}")
    for invalid_delay in (None, 0, -1):
        try:
            folded_diagnostic(1, "delay", measurement_delay_dt=invalid_delay)
        except ValueError:
            continue
        raise RuntimeError(f"delay arm accepted invalid duration {invalid_delay}")
    print("QPE diagnostics: 16 folded laws and twelve N=21 laws match exact circuit branches and sampled labels")


if __name__ == "__main__":
    _verify()
