"""Matched QPE controls and independently calculated labeled outcome laws.

The folded family shares logical control 0 and work qubits 1 through 4.
The coherent arm adds control 5 for the first, least-significant phase bit;
control 0 still carries the terminal, most-significant phase bit. A physical
comparison must bind those shared logical qubits to the same device qubits.
The delay arm records only its measured terminal bit, rather than presenting
the supplied eigenstate label as an observed first bit.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit import CircuitInstruction, Clbit, ControlFlowOp, Qubit
from qiskit.circuit.library import XGate
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from order_finding import ENCODED_STRATEGY, controlled_rotate, eigenstate_prep, factor_order_finding, folded_qpe

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


# The linear work-register encoding of the two-round circuit with the fewest
# median routed CZ among the admitted cosets (coset 15265 of GL(5,2)/S_5,
# results/hw_estimate/n21_linear_conjugation_challenger.json, which _verify
# binds). The phase register keeps n21_labeled_law exactly.
N21_ENCODED_COLUMNS = (2, 4, 5, 10, 17)
N21_CHALLENGER_RECORD = (
    Path(__file__).resolve().parents[1] / "results/hw_estimate/n21_linear_conjugation_challenger.json"
)


def n21_encoded_diagnostic(feed_forward: bool = True) -> QuantumCircuit:
    """n21_diagnostic with the work register encoded by N21_ENCODED_COLUMNS (factor_order_finding work_columns)."""
    circuit = factor_order_finding(
        21, 4, 2, multiplier_strategy=ENCODED_STRATEGY, feed_forward=feed_forward, work_columns=N21_ENCODED_COLUMNS
    )
    circuit.name = "n21_a4_two_bit_encoded_" + ("feed_forward" if feed_forward else "no_feed_forward")
    return circuit


def _check_encoded_binding() -> None:
    """N21_ENCODED_COLUMNS is the challenger record's best admitted two-round coset."""
    record = json.loads(N21_CHALLENGER_RECORD.read_text(encoding="utf-8"))
    entry = record["problems"]["two_round"]
    best = next(c for c in entry["challengers"] if c["coset_index"] == entry["best_admitted"])
    if tuple(best["columns"]) != N21_ENCODED_COLUMNS:
        raise RuntimeError(f"N21_ENCODED_COLUMNS {N21_ENCODED_COLUMNS} is not the admitted {best['columns']}")


# Bits 0, 2 and 4 of the binary work register hold the orbit 1, 4, 16 of
# multiplication by 4 modulo 21 one-hot; bits 1 and 3 stay zero on the orbit.
N21_ORBIT_BITS = (0, 2, 4)


# Window variants between the first measurement and the second round. Each
# keeps the ideal labeled law and changes one exposure of the work superposition
# |1> +/- |16> while the control is measured and reset. Barriers over every
# qubit open the window before the control's first measurement and close it
# after its reset, so work-only gates of either multiplier round stay outside
# it and every arm holds the work superposition on the same wires.
N21_ORBIT_VARIANTS = ("nominal", "window_delay", "extra_readout", "window_echo")
# window_delay_long idles the control twice window_delay_dt after its reset:
# with window_delay it separates a coherence loss that grows with the added
# idle from a one-time loss at the first added idle.
N21_ORBIT_SWEEP_VARIANTS = ("window_delay_long",)
# window_barrier idles the work bits for the same requested echo halves as
# window_echo, without the pulses; elapsed exposure and pulse differences come
# from the returned schedule. nominal_unbarriered omits both barriers, so the
# compiler may move work-only gates across the control's measurement and reset.
# window_delay_unbarriered is window_delay without both barriers.
N21_UNBARRIERED = ("nominal_unbarriered", "window_delay_unbarriered")
# window_dose idles every qubit for dose_dt after the control's reset, inside
# the barrier bracket; window_dose_echo spends the same dose as
# delay(q) X delay(2q) X delay(q) on the work bits that carry the superposition
# and a plain delay on the rest (n21_dose_name names the members).
N21_DOSE_VARIANTS = ("window_dose", "window_dose_echo")
# The quadrature variants are window_dose and window_dose_echo without
# feed-forward and with P(-pi/2) on the control where the feedback member
# conditions it, so the second round reads the sine of the work
# superposition's relative phase where the plain member reads its cosine.
N21_DOSE_QUADRATURE_VARIANTS = ("window_dose_y", "window_dose_echo_y")
N21_DOSE_NAMED = (*N21_DOSE_VARIANTS, *N21_DOSE_QUADRATURE_VARIANTS)
N21_ORBIT_BUILDABLE = (
    *N21_ORBIT_VARIANTS,
    *N21_ORBIT_SWEEP_VARIANTS,
    "window_barrier",
    *N21_UNBARRIERED,
    *N21_DOSE_NAMED,
)
_DELAY_MULTIPLES = {"window_delay": 1, "window_delay_long": 2, "window_delay_unbarriered": 1}

# Spectator Ramsey members prepare logical qubit 2, the work bit for 4, in
# |+> on the orbit's wires, open and close the same barrier bracket around
# the control's measurement (or a calibrated idle of the measurement's
# length) and reset, and read qubit 2 in X or Y. Clbit 0 holds the control's
# bit and clbit 1 qubit 2's, in the phase register, so an outcome index is
# control + 2 * qubit-2 bit + 4 * herald and the phase-register lifts apply.
N21_SPECTATOR_QUBIT = 2
N21_SPECTATOR_KINDS = ("measured", "reset_only")
# The overlap split reads qubit 2 at once after its preparation (immediate),
# across an idle of the control's measure plus reset durations with no reset
# (idle), and across the reset_only reference, so the loss splits into a
# preparation and readout floor, idle dephasing and the control's
# reset readout.
N21_SPECTATOR_SPLIT_KINDS = ("immediate", "idle", "reset_only")
# idle_ground is idle with the control left in |0>: a ZZ coupling to the
# control then rotates qubit 2 by a fixed angle, which leaves the X and Y
# visibility unchanged, so idle against idle_ground separates
# control-state-dependent dephasing from qubit 2's own idle dephasing.
N21_SPECTATOR_GROUND_KINDS = ("immediate", "idle", "idle_ground")
N21_SPECTATOR_BUILDABLE = ("measured", "immediate", "idle", "idle_ground", "reset_only")
N21_SPECTATOR_QUADRATURES = ("x", "y")
# The ground Ramsey sweep reads idle_ground at whole multiples of the
# control's measure plus reset idle; a member's name carries its multiple
# before the quadrature, n21_spectator_idle_ground_w<multiple>_<quadrature>,
# so the single-idle split's kind parse (rsplit on the quadrature) never
# reads a sweep member as idle_ground.
N21_RAMSEY_PREFIX = "n21_spectator_idle_ground_w"


def n21_ramsey_name(multiple: int, quadrature: str) -> str:
    """Member name of the ground Ramsey sweep's idle_ground arm at an idle of multiple windows."""
    if type(multiple) is not int or multiple < 1 or quadrature not in N21_SPECTATOR_QUADRATURES:
        raise ValueError(f"a ground Ramsey member needs a positive integer multiple and a quadrature, not {multiple!r}")
    return f"{N21_RAMSEY_PREFIX}{multiple}_{quadrature}"


def n21_ramsey_multiple(name: str) -> tuple[int, str] | None:
    """(multiple, quadrature) of a ground Ramsey sweep member name, or None for any other member."""
    if not name.startswith(N21_RAMSEY_PREFIX):
        return None
    head, _, quadrature = name.removeprefix(N21_RAMSEY_PREFIX).partition("_")
    if not head.isdigit() or int(head) < 1 or quadrature not in N21_SPECTATOR_QUADRATURES:
        return None
    return int(head), quadrature


# The initialization herald measures every qubit into its own register before
# the program and a barrier over all qubits follows it, so the labeled law
# over the phase register is unchanged. Packing prefixes register names
# (packing.relabel), so a register plays a role by its name or by its name's
# last underscore-separated field.
HERALD_REGISTER = "herald"
# The labeled law occupies the two phase bits, clbits 0 and 1; the herald
# register follows them, so an outcome index is phase + 4 * herald.
N21_PHASE_OUTCOMES = 4


def register_role(name: str) -> str:
    """The unprefixed role of a classical register name: its last underscore-separated field."""
    return name.rsplit("_", 1)[-1]


def herald_clbits(circuit: QuantumCircuit) -> frozenset[int]:
    """Indices of every clbit in a herald register of circuit."""
    return frozenset(
        circuit.find_bit(bit).index
        for register in circuit.cregs
        if register_role(register.name) == HERALD_REGISTER
        for bit in register
    )


def has_herald(circuit: QuantumCircuit) -> bool:
    return bool(herald_clbits(circuit))


def herald_measurement(circuit: QuantumCircuit, instruction: CircuitInstruction) -> bool:
    """Whether instruction is a measurement into a herald register of circuit."""
    return (
        instruction.operation.name == "measure"
        and bool(instruction.clbits)
        and circuit.find_bit(instruction.clbits[0]).index in herald_clbits(circuit)
    )


def lift_phase_values(values: object, clbits: int) -> np.ndarray:
    """A per-outcome vector over the phase register extended to every outcome of clbits bits.

    Outcome k of the full register reads the phase label k mod 4, so a score,
    weight or contrast vector keeps its value whatever the herald recorded.
    """
    phase = np.asarray(values, dtype=float)
    if phase.shape != (N21_PHASE_OUTCOMES,) or clbits < 2:
        raise ValueError(f"a phase vector has {N21_PHASE_OUTCOMES} entries and lifts onto two or more clbits")
    return np.asarray(phase[np.arange(1 << clbits) % N21_PHASE_OUTCOMES])


def lift_phase_law(law: object, clbits: int) -> np.ndarray:
    """A phase-register law extended with every herald bit 0, the ideal heralded law."""
    phase = np.asarray(law, dtype=float)
    if phase.shape != (N21_PHASE_OUTCOMES,) or clbits < 2:
        raise ValueError(f"a phase law has {N21_PHASE_OUTCOMES} entries and lifts onto two or more clbits")
    lifted = np.zeros(1 << clbits)
    lifted[:N21_PHASE_OUTCOMES] = phase
    return lifted


def phase_marginal(distribution: object) -> np.ndarray:
    """The law over the phase bits, clbits 0 and 1, of a distribution over phase and herald bits."""
    values = np.asarray(distribution, dtype=float)
    if values.ndim != 1 or values.size % N21_PHASE_OUTCOMES:
        raise ValueError(f"a distribution over phase and herald bits has a multiple of {N21_PHASE_OUTCOMES} entries")
    return np.asarray(values.reshape(-1, N21_PHASE_OUTCOMES).sum(axis=0))


def n21_dose_name(variant: str, dose_dt: int, feedback: bool) -> str:
    """Member name of a window-dose arm: variant, dose in dt and the feed-forward arm."""
    if variant not in N21_DOSE_NAMED or type(dose_dt) is not int or dose_dt < 0:
        raise ValueError(f"a window-dose member needs a variant in {N21_DOSE_NAMED} and a dose >= 0, not {variant!r}")
    if feedback and variant in N21_DOSE_QUADRATURE_VARIANTS:
        raise ValueError(f"{variant} has no feed-forward arm")
    return f"n21_orbit_{variant}_d{dose_dt}_{'feedback' if feedback else 'no_feedback'}"


def n21_dose_key(name: str) -> tuple[str, int, bool] | None:
    """(variant, dose_dt, feedback) of a window-dose member name, or None for any other member."""
    stem = name.removeprefix("n21_orbit_")
    if stem == name:
        return None
    for suffix in ("_no_feedback", "_feedback"):
        if stem.endswith(suffix):
            head = stem.removesuffix(suffix)
            break
    else:
        return None
    variant, _, dose = head.rpartition("_d")
    if variant not in N21_DOSE_NAMED or not dose.isdigit() or str(int(dose)) != dose:
        return None
    if suffix == "_feedback" and variant in N21_DOSE_QUADRATURE_VARIANTS:
        return None
    return variant, int(dose), suffix == "_feedback"


# A work Ramsey member puts the work bit for 1 (logical qubit 1) or for 16
# (logical qubit 3) on the equator with every other qubit in |0>, the
# condition of that bit while the orbit's single work excitation sits on it,
# idles every qubit dose_dt between barriers and reads the bit in X or Y into
# clbit 1 of the phase register; clbit 0 stays unwritten and reads 0.
N21_WORK_RAMSEY_PREFIX = "n21_work_ramsey_"
N21_WORK_RAMSEY_QUBITS = {"one": 1, "sixteen": 3}


def n21_work_ramsey_name(role: str, quadrature: str, dose_dt: int) -> str:
    """Member name of a work Ramsey arm: the work bit's role, the quadrature and the idle in dt."""
    if role not in N21_WORK_RAMSEY_QUBITS or quadrature not in N21_SPECTATOR_QUADRATURES:
        raise ValueError(f"a work Ramsey member needs a role in {tuple(N21_WORK_RAMSEY_QUBITS)}, not {role!r}")
    if type(dose_dt) is not int or dose_dt < 0 or dose_dt == 1:
        raise ValueError(f"a work Ramsey idle is an integer of 0 or at least 2 dt, not {dose_dt!r}")
    return f"{N21_WORK_RAMSEY_PREFIX}{role}_{quadrature}_d{dose_dt}"


def n21_work_ramsey_key(name: str) -> tuple[str, str, int] | None:
    """(role, quadrature, dose_dt) of a work Ramsey member name, or None for any other member."""
    if not name.startswith(N21_WORK_RAMSEY_PREFIX):
        return None
    role, _, rest = name.removeprefix(N21_WORK_RAMSEY_PREFIX).partition("_")
    quadrature, _, dose = rest.partition("_d")
    if role not in N21_WORK_RAMSEY_QUBITS or quadrature not in N21_SPECTATOR_QUADRATURES:
        return None
    if not dose.isdigit() or str(int(dose)) != dose or int(dose) == 1:
        return None
    return role, quadrature, int(dose)


def n21_work_ramsey(role: str, quadrature: str, dose_dt: int, *, init_herald: bool = False) -> QuantumCircuit:
    """Ramsey of one orbit work bit over a free idle of dose_dt, on the orbit's four logical qubits.

    H puts the bit on the equator, a barrier over every qubit opens the
    idle and a delay of dose_dt on every qubit fills it at the top level of
    the circuit, and a second barrier closes it; the bit then reads X (h)
    or Y (sdg, h) into clbit 1. A frame offset f of the bit turns
    <X> + i<Y> by 2 pi f t, the same sense in which the orbit's quadrature
    pair turns with the offset of the work bit for 16 minus that of the bit
    for 1 (tests/gororoba_quantum/test_detuning_sign.py). init_herald
    prepends the orbit's herald readouts and barrier, which also makes the
    member dynamic so it shares the orbit members' job.
    """
    name = n21_work_ramsey_name(role, quadrature, dose_dt)
    qubit = N21_WORK_RAMSEY_QUBITS[role]
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(len(N21_ORBIT_BITS), "w")
    phase = ClassicalRegister(2, "phase")
    circuit = QuantumCircuit(control, work, phase)
    if init_herald:
        herald = ClassicalRegister(circuit.num_qubits, HERALD_REGISTER)
        circuit.add_register(herald)
        for index in range(circuit.num_qubits):
            circuit.measure(index, herald[index])
        circuit.barrier()
    circuit.h(qubit)
    circuit.barrier()
    if dose_dt:
        circuit.delay(dose_dt, list(range(circuit.num_qubits)), unit="dt")
    circuit.barrier()
    if quadrature == "y":
        circuit.sdg(qubit)
    circuit.h(qubit)
    circuit.measure(qubit, phase[1])
    circuit.name = name + ("_heralded" if init_herald else "")
    return circuit


def n21_work_ramsey_law(quadrature: str) -> np.ndarray:
    """Ideal law of a work Ramsey member over the phase register: clbit 1 reads 0 in X, 0 or 1 equally in Y."""
    if quadrature not in N21_SPECTATOR_QUADRATURES:
        raise ValueError(f"unknown quadrature {quadrature!r}")
    return np.array([1.0, 0.0, 0.0, 0.0]) if quadrature == "x" else np.array([0.5, 0.0, 0.5, 0.0])


def n21_dose_violations(doses: Any, granularity: int, min_length: int) -> list[str]:
    """Reasons a window dose list breaks a Target's delay timing; empty when every delay is playable.

    A delay plays only as a multiple of the Target's granularity and of at
    least min_length dt. The echo splits a nonzero dose into the delays
    dose/4, dose/2 and dose/4, equal outer halves so that a static detuning
    accumulates opposite phases in the two X-separated intervals, so
    dose/4 meets the same two rules.
    """
    reasons = []
    for dose in doses:
        if dose == 0:
            continue
        if dose % granularity or dose < min_length:
            reasons.append(
                f"dose {dose} dt is not a multiple of granularity {granularity} dt that is at least {min_length} dt"
            )
        elif dose % (4 * granularity) or dose // 4 < min_length:
            reasons.append(
                f"the echo needs dose {dose} dt to be a multiple of {4 * granularity} dt of at least "
                f"{4 * min_length} dt"
            )
    return reasons


def n21_orbit_diagnostic(
    feed_forward: bool = True,
    variant: str = "nominal",
    *,
    window_delay_dt: int | None = None,
    echo_half_dt: int | None = None,
    init_herald: bool = False,
    dose_dt: int | None = None,
) -> QuantumCircuit:
    """Build the N=21 two-bit diagnostic with multipliers compiled on the orbit of |1>.

    On the orbit, multiplication by 4 cycles the one-hot bits 0 -> 2 -> 4 -> 0,
    two controlled swaps, and multiplication by 16 is its inverse. The
    multipliers act correctly only on the orbit, so constructing them supplies
    the order 3; the circuit measures feed-forward in two-round semiclassical
    QPE with the labeled law of n21_labeled_law and performs no order finding
    (Smolin, Smith and Vargo, Nature 499, 163 (2013), doi:10.1038/nature12290).

    Every variant except N21_UNBARRIERED brackets the control's
    measurement and reset with barriers over all qubits. window_delay idles
    the control for window_delay_dt after its reset, inside the bracket, so
    the work superposition waits that much longer before the second round;
    window_delay_long idles twice window_delay_dt.
    extra_readout measures the control a second time into the first bit, which
    adds one readout of the same duration and leaves the last write as the
    feed-forward bit. window_echo applies X to the work bits for 1 and 16 after
    echo_half_dt and again after a second echo_half_dt, both concurrent with
    the measurement and reset; a static frequency offset on those qubits
    accumulates opposite phases in the two halves and cancels.

    window_dose and window_dose_echo take dose_dt, an integer of 0 or at
    least 2 dt, and add idle after the control's reset, inside the bracket.
    window_dose idles every qubit for dose_dt. window_dose_echo idles the
    control and the work bit for 4 for dose_dt, and plays delay(dose_dt/4) X
    delay(dose_dt/2) X delay(dose_dt/4) on the work bits for 1 and 16, which
    hold the superposition (the bit for 4 stays in |0>); the two X pulses
    cancel in the ideal law, and a nonzero dose_dt is a multiple of 4 of at
    least 8. Every dose delay
    sits at the top level of the circuit, where the relaxation pass of an
    Aer noise model charges it (it acts on top-level delays, not on
    if_else bodies). A dose of 0 emits no delay, so both variants then
    equal the nominal bracketed program. window_dose_y and
    window_dose_echo_y are those programs without feed-forward and with
    P(-pi/2) on the control where the feedback member conditions it, so the
    second round reads the sine of the work superposition's relative phase.

    init_herald measures every qubit into the register HERALD_REGISTER, qubit
    k into its bit k, and places a barrier over all qubits before the
    program. Each herald bit reads 1 with the qubit's initial excitation plus
    its readout P(1|0); the ideal herald is all zero, so the ideal law over
    phase and herald bits is the labeled law lifted by lift_phase_law.
    """
    if variant not in N21_ORBIT_BUILDABLE:
        raise ValueError(f"unknown N=21 orbit variant {variant!r}")
    if variant in _DELAY_MULTIPLES and (type(window_delay_dt) is not int or window_delay_dt <= 0):
        raise ValueError(f"{variant} requires a positive integer window_delay_dt from calibration")
    if variant in ("window_echo", "window_barrier") and (type(echo_half_dt) is not int or echo_half_dt <= 0):
        raise ValueError(f"{variant} requires a positive integer echo_half_dt from calibration")
    dosed = variant.removesuffix("_y") if variant in N21_DOSE_QUADRATURE_VARIANTS else variant
    if variant in N21_DOSE_NAMED:
        if type(dose_dt) is not int or dose_dt < 0 or dose_dt == 1:
            raise ValueError(f"{variant} requires an integer dose_dt of 0 or at least 2, not {dose_dt!r}")
        if dosed == "window_dose_echo" and dose_dt and (dose_dt % 4 or dose_dt < 8):
            raise ValueError(f"{variant} requires dose_dt of 0 or a multiple of 4 of at least 8, not {dose_dt}")
        if feed_forward and variant in N21_DOSE_QUADRATURE_VARIANTS:
            raise ValueError(f"{variant} reads the second quadrature without feed-forward")
    elif dose_dt is not None:
        raise ValueError(f"dose_dt applies to {N21_DOSE_NAMED}, not {variant}")
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(len(N21_ORBIT_BITS), "w")
    phase = ClassicalRegister(2, "phase")
    circuit = QuantumCircuit(control, work, phase)
    if init_herald:
        herald = ClassicalRegister(circuit.num_qubits, HERALD_REGISTER)
        circuit.add_register(herald)
        for qubit in range(circuit.num_qubits):
            circuit.measure(qubit, herald[qubit])
        circuit.barrier()
    one, four, sixteen = 1, 2, 3
    circuit.x(one)
    circuit.h(0)
    circuit.cswap(0, one, four)
    circuit.cswap(0, four, sixteen)
    circuit.h(0)
    bracketed = variant not in N21_UNBARRIERED
    if bracketed:
        circuit.barrier()
    if variant == "window_echo":
        if echo_half_dt is None:
            raise AssertionError
        for _half in range(2):
            circuit.delay(echo_half_dt, [one, sixteen], unit="dt")
            circuit.x([one, sixteen])
    if variant == "window_barrier":
        if echo_half_dt is None:
            raise AssertionError
        circuit.delay(2 * echo_half_dt, [one, sixteen], unit="dt")
    circuit.measure(0, phase[0])
    if variant == "extra_readout":
        circuit.measure(0, phase[0])
    circuit.reset(0)
    if variant in _DELAY_MULTIPLES:
        if window_delay_dt is None:
            raise AssertionError
        circuit.delay(_DELAY_MULTIPLES[variant] * window_delay_dt, 0, unit="dt")
    if dose_dt:
        # Without a full-width barrier the work-wire delays share no dependency with the control's reset and an
        # ASAP schedule starts them beside its readout; the barrier starts every dose after the reset ends.
        circuit.barrier()
        if dosed == "window_dose":
            circuit.delay(dose_dt, list(range(circuit.num_qubits)), unit="dt")
        else:
            circuit.delay(dose_dt, [0, four], unit="dt")
            quarter = dose_dt // 4
            circuit.delay(quarter, [one, sixteen], unit="dt")
            circuit.x([one, sixteen])
            circuit.delay(2 * quarter, [one, sixteen], unit="dt")
            circuit.x([one, sixteen])
            circuit.delay(quarter, [one, sixteen], unit="dt")
    if bracketed:
        circuit.barrier()
    circuit.h(0)
    circuit.cswap(0, four, sixteen)
    circuit.cswap(0, one, four)
    if feed_forward:
        with circuit.if_test((phase[0], 1)):
            circuit.p(-math.pi / 2, 0)
    elif variant in N21_DOSE_QUADRATURE_VARIANTS:
        circuit.p(-math.pi / 2, 0)
    circuit.h(0)
    circuit.measure(0, phase[1])
    suffix = "" if variant == "nominal" else f"_{variant}_d{dose_dt}" if variant in N21_DOSE_NAMED else f"_{variant}"
    suffix += "_heralded" if init_herald else ""
    circuit.name = "n21_orbit_a4_two_bit_" + ("feed_forward" if feed_forward else "no_feed_forward") + suffix
    return circuit


def n21_spectator_ramsey(
    kind: str,
    quadrature: str,
    *,
    measure_dt: int | None = None,
    reset_dt: int | None = None,
    init_herald: bool = False,
    idle_multiple: int | None = None,
) -> QuantumCircuit:
    """Ramsey of logical qubit 2 across the orbit's control window, on the orbit's four logical qubits.

    Qubit 2 and the control start in |+> and the other qubits in |0>, so
    the control reads 0 or 1 with equal probability, as it does in the
    orbit; barriers over every qubit bracket the control's measurement into
    clbit 0 and its reset, so qubit 2 idles across the window as the orbit's
    work bits do. A ZZ coupling between the control and qubit 2 then turns
    qubit 2's phase with the recorded control bit (spectator_branch_phase).
    reset_only idles the control measure_dt in place of the measurement and
    leaves clbit 0 unwritten; the reset still projects the control, since a
    Heron r2 reset is a readout followed by a conditional flip. idle idles
    the control measure_dt + reset_dt inside the same bracket with no reset,
    idle_ground is idle with no H on the control, so the control idles in
    |0>; immediate reads qubit 2 right after the barrier that follows its
    preparation, with no window; all three reset the control only after a
    barrier that follows qubit 2's readout. Qubit 2
    reads X (h) or Y (sdg, h) into clbit 1: the ideal law is
    n21_spectator_law. init_herald prepends the orbit's herald readouts
    and barrier. idle_multiple, given for idle_ground only, makes the
    member a ground Ramsey sweep arm: its control delay is idle_multiple *
    (measure_dt + reset_dt) and its name is n21_ramsey_name.
    """
    if kind not in N21_SPECTATOR_BUILDABLE or quadrature not in N21_SPECTATOR_QUADRATURES:
        raise ValueError(f"unknown spectator kind {kind!r} or quadrature {quadrature!r}")
    if kind in ("reset_only", "idle", "idle_ground") and (type(measure_dt) is not int or measure_dt <= 0):
        raise ValueError(f"{kind} requires a positive integer measure_dt from calibration")
    if kind in ("idle", "idle_ground") and (type(reset_dt) is not int or reset_dt <= 0):
        raise ValueError(f"{kind} requires a positive integer reset_dt from calibration")
    if idle_multiple is not None and (type(idle_multiple) is not int or idle_multiple < 1 or kind != "idle_ground"):
        raise ValueError(f"idle_multiple {idle_multiple!r} applies to idle_ground as a positive integer only")
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(len(N21_ORBIT_BITS), "w")
    phase = ClassicalRegister(2, "phase")
    circuit = QuantumCircuit(control, work, phase)
    if init_herald:
        herald = ClassicalRegister(circuit.num_qubits, HERALD_REGISTER)
        circuit.add_register(herald)
        for qubit in range(circuit.num_qubits):
            circuit.measure(qubit, herald[qubit])
        circuit.barrier()
    circuit.h([N21_SPECTATOR_QUBIT] if kind == "idle_ground" else [0, N21_SPECTATOR_QUBIT])
    circuit.barrier()
    if kind == "measured":
        circuit.measure(0, phase[0])
        circuit.reset(0)
        circuit.barrier()
    elif kind != "immediate":
        if measure_dt is None:
            raise AssertionError
        if kind in ("idle", "idle_ground"):
            if reset_dt is None:
                raise AssertionError
            circuit.delay((idle_multiple or 1) * (measure_dt + reset_dt), 0, unit="dt")
        else:
            circuit.delay(measure_dt, 0, unit="dt")
            circuit.reset(0)
        circuit.barrier()
    if quadrature == "y":
        circuit.sdg(N21_SPECTATOR_QUBIT)
    circuit.h(N21_SPECTATOR_QUBIT)
    circuit.measure(N21_SPECTATOR_QUBIT, phase[1])
    if kind in ("immediate", "idle", "idle_ground"):
        # A reset of the control after qubit 2's readout makes the circuit
        # dynamic (local_compute.is_dynamic), so it shares the orbit arms'
        # job; the barrier places it after that readout.
        circuit.barrier()
        circuit.reset(0)
    name = f"n21_spectator_{kind}_{quadrature}" if idle_multiple is None else n21_ramsey_name(idle_multiple, quadrature)
    circuit.name = name + ("_heralded" if init_herald else "")
    return circuit


def n21_spectator_law(kind: str, quadrature: str) -> tuple[Fraction, ...]:
    """Ideal law of a spectator Ramsey member over control + 2 * qubit-2 bit.

    The measured control bit reads 0 or 1 equally; every other kind leaves
    clbit 0 unwritten, so it reads 0. Qubit 2 reads 0 in X and 0 or 1
    equally in Y.
    """
    if kind not in N21_SPECTATOR_BUILDABLE or quadrature not in N21_SPECTATOR_QUADRATURES:
        raise ValueError(f"unknown spectator kind {kind!r} or quadrature {quadrature!r}")
    qubit_two = (Fraction(1), Fraction(0)) if quadrature == "x" else (Fraction(1, 2), Fraction(1, 2))
    control = (Fraction(1, 2), Fraction(1, 2)) if kind == "measured" else (Fraction(1), Fraction(0))
    return tuple(control[label & 1] * qubit_two[label >> 1] for label in range(4))


# The segmented ground sweep reads qubit 2 several times per shot with the
# control left in |0>. Each segment is herald, preparation, idle, basis
# change and readout; a reset of qubit 2 opens every segment after the
# first, so its herald measures the post-reset state immediately before the
# preparation, as the first segment's herald does. Segment s writes its
# herald into register s<s>_herald (every qubit in segment 1, qubit 2 after
# that) and its readout into s<s>_read, so each segment stays separable in
# the raw bitstrings. kind "xy" alternates X and Y readouts after a |+>
# preparation, segment 1 reading X, so both quadratures of a delay share
# every shot; kind "z" prepares |1> with an X and reads Z. pre_idle_dt idles
# qubit 2 between its herald and its preparation (the herald-backaction
# control).
N21_SEGMENTED_PREFIX = "n21_spectator_segmented_"
N21_SEGMENTED_KINDS = ("xy", "z")
# Segment 1 holds 5 clbits and each further segment 2, so the dense
# per-member law over 3 + 2 K clbits stays at most 2^15 entries.
N21_SEGMENTED_MAX = 6


def n21_segmented_name(kind: str, delay_dt: int, pre_idle_dt: int = 0) -> str:
    """Member name of a segmented sweep arm: kind, idle in dt and, for a backaction control, its pre-idle."""
    if kind not in N21_SEGMENTED_KINDS or type(delay_dt) is not int or delay_dt < 0:
        raise ValueError(f"a segmented arm needs a kind in {N21_SEGMENTED_KINDS} and a delay >= 0, not {kind!r}")
    if type(pre_idle_dt) is not int or pre_idle_dt < 0:
        raise ValueError(f"pre_idle_dt must be a non-negative integer, not {pre_idle_dt!r}")
    return f"{N21_SEGMENTED_PREFIX}{kind}_d{delay_dt}" + (f"_pre{pre_idle_dt}" if pre_idle_dt else "")


def n21_segmented_key(name: str) -> tuple[str, int, int] | None:
    """(kind, delay_dt, pre_idle_dt) of a segmented sweep member name, or None for any other member."""
    if not name.startswith(N21_SEGMENTED_PREFIX):
        return None
    fields = name.removeprefix(N21_SEGMENTED_PREFIX).split("_")
    if len(fields) not in (2, 3) or fields[0] not in N21_SEGMENTED_KINDS or not fields[1].startswith("d"):
        return None
    delay = fields[1][1:]
    pre = fields[2][3:] if len(fields) == 3 and fields[2].startswith("pre") else ("0" if len(fields) == 2 else "")
    if not delay.isdigit() or not pre.isdigit() or (len(fields) == 3 and int(pre) < 1):
        return None
    return fields[0], int(delay), int(pre)


def n21_segment_bases(kind: str, segments: int) -> tuple[str, ...]:
    """The readout basis of each segment: x and y alternating from x, or z throughout."""
    return tuple(("x", "y")[s % 2] for s in range(segments)) if kind == "xy" else ("z",) * segments


def n21_segmented_ramsey(kind: str, delay_dt: int, segments: int, pre_idle_dt: int = 0) -> QuantumCircuit:
    """Segmented ground Ramsey arm of logical qubit 2 on the orbit's four logical qubits.

    The control never leaves |0>; qubit 2's resets make the circuit
    dynamic, and no if_else enters it, so the per-job broadcast budget of
    the dynamic-circuit guide stays unused. A delay of 0 dt plays no delay
    instruction; any other delay is at least the Target's min_length.
    Barriers over every qubit bracket each idle, so the scheduler places
    the idle between the preparation and the basis change.
    """
    if kind not in N21_SEGMENTED_KINDS:
        raise ValueError(f"unknown segmented kind {kind!r}")
    if type(segments) is not int or not 2 <= segments <= N21_SEGMENTED_MAX or (kind == "xy" and segments % 2):
        raise ValueError(f"segments must be an integer in [2, {N21_SEGMENTED_MAX}], even for xy, not {segments!r}")
    if type(delay_dt) is not int or delay_dt < 0 or delay_dt == 1:
        raise ValueError(f"delay_dt must be 0 or an integer >= 2 (min_length), not {delay_dt!r}")
    if type(pre_idle_dt) is not int or pre_idle_dt < 0 or pre_idle_dt == 1:
        raise ValueError(f"pre_idle_dt must be 0 or an integer >= 2 (min_length), not {pre_idle_dt!r}")
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(len(N21_ORBIT_BITS), "w")
    circuit = QuantumCircuit(control, work)
    spectator = N21_SPECTATOR_QUBIT
    for index, basis in enumerate(n21_segment_bases(kind, segments)):
        herald = ClassicalRegister(circuit.num_qubits if index == 0 else 1, f"s{index + 1}_{HERALD_REGISTER}")
        read = ClassicalRegister(1, f"s{index + 1}_read")
        circuit.add_register(herald)
        circuit.add_register(read)
        if index:
            circuit.reset(spectator)
            circuit.barrier()
            circuit.measure(spectator, herald[0])
        else:
            for qubit in range(circuit.num_qubits):
                circuit.measure(qubit, herald[qubit])
        circuit.barrier()
        if pre_idle_dt:
            circuit.delay(pre_idle_dt, spectator, unit="dt")
            circuit.barrier()
        if basis == "z":
            circuit.x(spectator)
        else:
            circuit.h(spectator)
        circuit.barrier()
        if delay_dt:
            circuit.delay(delay_dt, spectator, unit="dt")
            circuit.barrier()
        if basis == "y":
            circuit.sdg(spectator)
        if basis != "z":
            circuit.h(spectator)
        circuit.measure(spectator, read[0])
        circuit.barrier()
    circuit.name = n21_segmented_name(kind, delay_dt, pre_idle_dt)
    return circuit


def n21_segmented_law(kind: str, segments: int) -> np.ndarray:
    """Ideal law over every clbit: heralds read 0, X reads 0, Y reads 0 or 1 equally, Z after X reads 1."""
    bases = n21_segment_bases(kind, segments)
    width = 3 + 2 * segments
    law = np.zeros(1 << width)
    reads = n21_segment_read_clbits(segments)
    for outcome in range(1 << segments):
        probability = 1.0
        index = 0
        for s, basis in enumerate(bases):
            bit = (outcome >> s) & 1
            probability *= {"x": 1.0 - bit, "y": 0.5, "z": float(bit)}[basis]
            index |= bit << reads[s]
        law[index] += probability
    return law


def n21_segment_read_clbits(segments: int) -> tuple[int, ...]:
    """Clbit index of each segment's readout: 4 after the 4-bit first herald, then (herald, read) pairs."""
    return (4, *(4 + 2 * s for s in range(1, segments)))


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
                condition_target, condition_value = operation.condition
                if isinstance(condition_target, Clbit):
                    condition_bits = [condition_target]
                elif isinstance(condition_target, ClassicalRegister):
                    condition_bits = list(condition_target)
                else:
                    raise ValueError("exact branch check requires a bit or register condition")
                # A register condition compares the register's integer value, bit 0 least significant.
                observed = sum(
                    ((classical >> clbits[circuit.find_bit(bit).index]) & 1) << position
                    for position, bit in enumerate(condition_bits)
                )
                block_index = 0 if observed == condition_value else 1
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


def window_bracket_violations(isa: QuantumCircuit, inside: frozenset[str] = frozenset({"delay"})) -> list[str]:
    """Operations on other wires that the control's measurement-and-reset window holds.

    The window opens at the first measurement outside every herald register
    (herald_clbits) and closes at the first reset of its wire that follows
    it, so a heralded circuit reads the window of its unheralded twin. The
    herald measurements precede a barrier over every qubit and so lie before
    the window. An operation on another wire lies outside
    the window when it precedes the measurement or follows the reset in the
    circuit's dependency order; a barrier over every qubit places all of a
    multiplier round on one side. Operations named in inside (delays, and
    the echo pulses of window_echo) belong to the window by design.
    """
    dag = circuit_to_dag(isa)
    nodes = list(dag.topological_op_nodes())
    heralded = herald_clbits(isa)
    opening = next(
        (node for node in nodes if node.op.name == "measure" and isa.find_bit(node.cargs[0]).index not in heralded),
        None,
    )
    if opening is None:
        raise ValueError(f"{isa.name}: no measurement opens a window")
    control = opening.qargs[0]
    after = dag.descendants(opening)
    closing = next(
        (node for node in nodes if node in after and node.op.name == "reset" and node.qargs == (control,)), None
    )
    if closing is None:
        raise ValueError(f"{isa.name}: no reset of the measured wire closes its window")
    before, later = dag.ancestors(opening), dag.descendants(closing)
    return [
        f"{node.op.name} on {[isa.find_bit(qubit).index for qubit in node.qargs]}"
        for node in nodes
        if control not in node.qargs
        and node.op.name not in inside | {"barrier"}
        and node not in before
        and node not in later
    ]


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


def _check_herald_structure(heralded: QuantumCircuit, twin: QuantumCircuit, windowed: bool = True) -> None:
    """A heralded orbit circuit is its twin after one herald measurement per qubit and a full barrier.

    Its phase marginal is the twin's labeled law. With windowed (every
    circuit whose first program measurement is the control's, which a reset
    follows), its window bracket reads the twin's, and the same circuit with the herald written into a register
    of another name opens the window at the control's herald measurement,
    which a bracketed arm then fails.
    """
    width = heralded.num_qubits
    prefix = heralded.data[: width + 1]
    if [heralded.find_bit(i.qubits[0]).index for i in prefix[:width] if herald_measurement(heralded, i)] != list(
        range(width)
    ):
        raise RuntimeError(f"{heralded.name}: the herald does not measure every qubit first, qubit k into bit k")
    if prefix[width].operation.name != "barrier" or len(prefix[width].qubits) != width:
        raise RuntimeError(f"{heralded.name}: no barrier over every qubit follows the herald")
    if [(i.operation.name, i.qubits, i.clbits) for i in heralded.data[width + 1 :]] != [
        (i.operation.name, i.qubits, i.clbits) for i in twin.data
    ]:
        raise RuntimeError(f"{heralded.name}: the program after the herald differs from its unheralded twin")
    marginal = phase_marginal(ideal_branch_probabilities(heralded))
    if not np.allclose(marginal, ideal_branch_probabilities(twin), atol=1e-11, rtol=0):
        raise RuntimeError(f"{heralded.name}: the phase marginal differs from the unheralded labeled law")
    if not windowed:
        return
    if window_bracket_violations(heralded) != window_bracket_violations(twin):
        raise RuntimeError(f"{heralded.name}: the herald changes the window bracket")
    renamed = QuantumCircuit(*heralded.qregs, *(ClassicalRegister(r.size, r.name + "x") for r in heralded.cregs))
    renamed.compose(heralded, inplace=True)
    if "unbarriered" not in heralded.name and not window_bracket_violations(renamed):
        raise RuntimeError(f"{heralded.name}: a window opened at the herald holds no violation, so the check is void")


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
        circuits.append(n21_encoded_diagnostic(feed_forward))
        expected_laws.append(expected)
        for variant in N21_ORBIT_BUILDABLE:
            circuits.append(n21_orbit_diagnostic(feed_forward, variant, window_delay_dt=416, echo_half_dt=512))
            expected_laws.append(expected)
            heralded = n21_orbit_diagnostic(
                feed_forward, variant, window_delay_dt=416, echo_half_dt=512, init_herald=True
            )
            _check_herald_structure(heralded, circuits[-1])
            circuits.append(heralded)
            expected_laws.append(expected + (Fraction(0),) * ((1 << heralded.num_clbits) - len(expected)))
    for kind in N21_SPECTATOR_BUILDABLE:
        for quadrature in N21_SPECTATOR_QUADRATURES:
            law = n21_spectator_law(kind, quadrature)
            plain = n21_spectator_ramsey(kind, quadrature, measure_dt=416, reset_dt=520)
            heralded = n21_spectator_ramsey(kind, quadrature, measure_dt=416, reset_dt=520, init_herald=True)
            _check_herald_structure(heralded, plain, windowed=kind == "measured")
            circuits.extend((plain, heralded))
            expected_laws.extend((law, law + (Fraction(0),) * ((1 << heralded.num_clbits) - len(law))))
    for circuit, expected in zip(circuits, expected_laws, strict=True):
        observed = ideal_branch_probabilities(circuit)
        if not np.allclose(observed, [float(value) for value in expected], atol=1e-11, rtol=0):
            raise RuntimeError(f"{circuit.name}: exact circuit branches {observed} disagree with {expected}")
        padded = circuit.copy()
        padded.add_register(QuantumRegister(20, "idle"))
        padded.barrier(*padded.qubits)
        if not np.allclose(ideal_compiled_probabilities(padded), observed, atol=1e-11, rtol=0):
            raise RuntimeError(f"{circuit.name}: removing idle physical wires changed the labeled law")
    _check_encoded_binding()
    for original in (n21_diagnostic(), n21_encoded_diagnostic(), n21_orbit_diagnostic()):
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
        counts = {key.replace(" ", ""): value for key, value in sampled.get_counts(index).items()}
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
    print(
        "QPE diagnostics: 16 folded laws, the N=21 laws of every orbit variant with their heralded twins, and the "
        "ten spectator Ramsey laws with theirs match exact circuit branches and sampled labels; heralded circuits "
        "measure every qubit before a full barrier, read the window bracket of their unheralded twins and "
        "marginalize to the unheralded law"
    )


if __name__ == "__main__":
    _verify()
