"""Ramsey, measurement-window, exchange and orbit-context characterization of a pinned patch.

The patch binds logical qubits to physical ones in the order control, work A,
spectator, work B, neighbor of A, neighbor of B; the N=21 orbit runs placed
control, work bit 1, work bit 4 and work bit 16 on the first four. The 46
circuits follow docs/notes/patch_window_staged_plan.md:

- Paired Ramsey puts both work qubits in |+>, idles them plain or echoed, and
  reads both in the X or Y basis, so a quadrature pair gives each qubit's phase
  and visibility. Zero-idle pairs anchor phase and contrast.
- Single-work-qubit references idle one work qubit with the other in |0>;
  simultaneous X on both work qubits leaves their mutual ZZ unrefocused, since
  (X_A X_B)(Z_A Z_B)(X_A X_B) = Z_A Z_B, so the pair and the single references
  separate a paired-preparation context from a single-qubit effect.
- Measurement-window Ramsey idles the work pair while the control, prepared in
  |0> or |1>, is measured and reset. The explicit-measurement-omitted reference
  replaces that measurement with a delay of the calibrated measure duration and
  keeps the reset, so the pair isolates the explicit measurement.
- Exchange circuits excite one work qubit and read the patch at zero and long
  idle; the unexcited long idle and the all-one immediate readout bound the
  population and readout background. Weak transfer leaves dispersive phase
  possible, so these circuits test population exchange only.
- Orbit pairs run the original scheduling freedom, a barrier with matched
  requested idle halves, and a barrier with an echo across the same halves,
  each with and without feed-forward, in the same acquisition; the returned
  schedules qualify their elapsed exposure and pulse-related differences.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member

PATCH_ROLES = ("control", "work_a", "spectator", "work_b", "neighbor_a", "neighbor_b")
CONTROL, WORK_A, SPECTATOR, WORK_B, NEIGHBOR_A, NEIGHBOR_B = range(len(PATCH_ROLES))
QUADRATURES = ("x", "y")
RAMSEY_VARIANTS = ("plain", "echo")
CONTROL_STATES = (0, 1)
ORBIT_CONTEXTS = ("nominal", "window_barrier", "window_echo")
# Idle lengths in dt bracketing the orbit window, 3.6 to 7.6 us at 4 ns per dt;
# the analysis uses each PUB's returned schedule, not these requests.
PATCH_DELAYS_DT = (900, 1400, 1900)
# Couplers the patch exercises: control-spectator, each work qubit with the
# spectator, and each work qubit with its outer neighbor.
PATCH_EDGES = (
    (CONTROL, SPECTATOR),
    (WORK_A, SPECTATOR),
    (WORK_B, SPECTATOR),
    (WORK_A, NEIGHBOR_A),
    (WORK_B, NEIGHBOR_B),
)
WORK_CLBIT = {WORK_A: 0, WORK_B: 1}
SIGNED = (0.0, 1.0, 0.0, -1.0)


def _validate_delay(delay_dt: int, *, allow_zero: bool = False) -> None:
    if type(delay_dt) is not int or delay_dt < (0 if allow_zero else 1) or delay_dt % 2:
        raise ValueError("patch delays are nonnegative even integers in dt so an echo splits them evenly")


def _patch(name: str, clbits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(QuantumRegister(len(PATCH_ROLES), "patch"), ClassicalRegister(clbits, "c"))
    circuit.name = name
    return circuit


def _read(circuit: QuantumCircuit, qubits: tuple[int, ...], quadrature: str, first_clbit: int) -> None:
    for offset, qubit in enumerate(qubits):
        if quadrature == "y":
            circuit.sdg(qubit)
        circuit.h(qubit)
        circuit.measure(qubit, first_clbit + offset)


def ramsey(
    delay_dt: int, variant: str, quadrature: str, prepared: tuple[int, ...] = (WORK_A, WORK_B)
) -> QuantumCircuit:
    """Work qubits in prepared idle in |+> for delay_dt, echoed at the midpoint when variant is echo.

    Work A and B read into clbits 0 and 1; an unprepared work qubit stays in
    |0> and reads in the computational basis.
    """
    _validate_delay(delay_dt, allow_zero=variant == "plain")
    if variant not in RAMSEY_VARIANTS or quadrature not in QUADRATURES:
        raise ValueError(f"unknown Ramsey variant {variant!r} or quadrature {quadrature!r}")
    if not prepared or not set(prepared) <= {WORK_A, WORK_B}:
        raise ValueError("Ramsey prepares work qubit A, B, or both")
    single = "" if len(prepared) == 2 else f"_only_{PATCH_ROLES[prepared[0]]}"
    circuit = _patch(f"ramsey_{variant}_{quadrature}_d{delay_dt}{single}", 2)
    circuit.h(list(prepared))
    circuit.barrier()
    if variant == "plain" and delay_dt:
        circuit.delay(delay_dt, [WORK_A, WORK_B], unit="dt")
    elif variant == "echo":
        for _half in range(2):
            circuit.delay(delay_dt // 2, [WORK_A, WORK_B], unit="dt")
            circuit.x(list(prepared))
    circuit.barrier()
    # Every basis change precedes every measurement, so no gate follows a
    # measurement and the circuit stays static (local_compute.is_dynamic).
    for qubit in prepared:
        if quadrature == "y":
            circuit.sdg(qubit)
        circuit.h(qubit)
    for qubit in (WORK_A, WORK_B):
        circuit.measure(qubit, WORK_CLBIT[qubit])
    return circuit


def measurement_window(
    delay_dt: int, control_state: int, quadrature: str, *, omit_measurement_dt: int | None = None
) -> QuantumCircuit:
    """Paired Ramsey while the control is measured and reset inside the idle.

    The control's bit is clbit 0; work A and B read into clbits 1 and 2. With
    omit_measurement_dt the control idles that many dt in place of the
    explicit measurement and still resets, and clbit 0 stays unwritten.
    """
    _validate_delay(delay_dt)
    if control_state not in CONTROL_STATES or quadrature not in QUADRATURES:
        raise ValueError(f"unknown control state {control_state!r} or quadrature {quadrature!r}")
    if omit_measurement_dt is not None and (type(omit_measurement_dt) is not int or omit_measurement_dt <= 0):
        raise ValueError("the omitted measurement idles a positive calibrated duration")
    kind = "measure_reset" if omit_measurement_dt is None else "reset_only"
    circuit = _patch(f"window_{kind}_c{control_state}_{quadrature}_d{delay_dt}", 3)
    if control_state:
        circuit.x(CONTROL)
    circuit.h([WORK_A, WORK_B])
    circuit.barrier()
    circuit.delay(delay_dt, [WORK_A, WORK_B], unit="dt")
    if omit_measurement_dt is None:
        circuit.measure(CONTROL, 0)
    else:
        circuit.delay(omit_measurement_dt, CONTROL, unit="dt")
    circuit.reset(CONTROL)
    circuit.barrier()
    _read(circuit, (WORK_A, WORK_B), quadrature, 1)
    return circuit


def exchange(delay_dt: int, excited: tuple[int, ...]) -> QuantumCircuit:
    """Excite the listed patch qubits, idle, and read every patch qubit except the control."""
    _validate_delay(delay_dt, allow_zero=True)
    label = "none" if not excited else "all" if len(excited) == 5 else PATCH_ROLES[excited[0]]
    circuit = _patch(f"exchange_{label}_d{delay_dt}", 5)
    if excited:
        circuit.x(list(excited))
    circuit.barrier()
    if delay_dt:
        circuit.delay(delay_dt, list(range(1, len(PATCH_ROLES))), unit="dt")
        circuit.barrier()
    for clbit, qubit in enumerate(range(1, len(PATCH_ROLES))):
        circuit.measure(qubit, clbit)
    return circuit


def orbit(feed_forward: bool, context: str, echo_half_dt: int) -> QuantumCircuit:
    """The N=21 orbit comparison in one scheduling context, on the first four patch qubits."""
    from qpe_diagnostics import n21_orbit_diagnostic

    if context not in ORBIT_CONTEXTS:
        raise ValueError(f"unknown orbit context {context!r}")
    # The nominal context leaves the window unbracketed; window_barrier and
    # window_echo add the barriers as their scheduling intervention.
    variant = "nominal_unbarriered" if context == "nominal" else context
    source = n21_orbit_diagnostic(feed_forward, variant, echo_half_dt=echo_half_dt)
    circuit = _patch(f"orbit_{context}_{'feedback' if feed_forward else 'no_feedback'}", source.num_clbits)
    circuit.compose(source, qubits=[CONTROL, WORK_A, SPECTATOR, WORK_B], clbits=range(source.num_clbits), inplace=True)
    return circuit


def _expected_law(name: str) -> list[Fraction]:
    """Independent labeled law of each member, from its preparation alone."""
    quarter, half, one, zero = Fraction(1, 4), Fraction(1, 2), Fraction(1), Fraction(0)
    if name.startswith("ramsey_"):
        quadrature = name.split("_")[2]
        if "_only_" in name:
            clbit = WORK_CLBIT[WORK_A if name.endswith("work_a") else WORK_B]
            if quadrature == "x":
                return [one, zero, zero, zero]
            law = [zero] * 4
            law[0], law[1 << clbit] = half, half
            return law
        return [one, zero, zero, zero] if quadrature == "x" else [quarter] * 4
    if name.startswith("window_"):
        parts = name.split("_")
        control_state, quadrature = int(parts[3][1]), parts[4]
        recorded = control_state if parts[1] == "measure" else 0
        work = [one, zero, zero, zero] if quadrature == "x" else [quarter] * 4
        law = [zero] * 8
        for outcome, probability in enumerate(work):
            law[recorded + 2 * outcome] = probability
        return law
    if name.startswith("exchange_"):
        label = name.split("_d")[0].removeprefix("exchange_")
        law = [zero] * 32
        law[{"none": 0, "all": 31, "work_a": 1 << (WORK_A - 1), "work_b": 1 << (WORK_B - 1)}[label]] = one
        return law
    from qpe_diagnostics import n21_labeled_law

    return list(n21_labeled_law("no_feedback" not in name))


def patch_circuits(
    delays_dt: list[int], measure_dt: int, echo_half_dt: int
) -> tuple[list[QuantumCircuit], list[QuantumCircuit]]:
    """The 24 static and 22 dynamic circuits of the staged design."""
    for delay in delays_dt:
        _validate_delay(delay)
    middle, longest = sorted(delays_dt)[len(delays_dt) // 2], max(delays_dt)
    static = [ramsey(d, v, q) for v in RAMSEY_VARIANTS for d in delays_dt for q in QUADRATURES]
    static += [ramsey(0, "plain", q) for q in QUADRATURES]
    static += [ramsey(longest, "plain", q, (qubit,)) for qubit in (WORK_A, WORK_B) for q in QUADRATURES]
    static += [exchange(d, (qubit,)) for qubit in (WORK_A, WORK_B) for d in (0, longest)]
    static += [exchange(longest, ()), exchange(0, tuple(range(1, len(PATCH_ROLES))))]
    dynamic = [measurement_window(d, c, q) for d in delays_dt for c in CONTROL_STATES for q in QUADRATURES]
    dynamic += [
        measurement_window(middle, c, q, omit_measurement_dt=measure_dt) for c in CONTROL_STATES for q in QUADRATURES
    ]
    dynamic += [orbit(f, context, echo_half_dt) for context in ORBIT_CONTEXTS for f in (True, False)]
    return static, dynamic


def patch_groups(delays_dt: list[int], measure_dt: int, echo_half_dt: int) -> list[Group]:
    """The static characterization group and the dynamic window group."""
    static, dynamic = patch_circuits(delays_dt, measure_dt, echo_half_dt)

    def group(name: str, circuits: list[QuantumCircuit]) -> Group:
        members = tuple(Member(c.name, c, np.asarray([float(p) for p in _expected_law(c.name)])) for c in circuits)
        return Group(name, members, lambda distributions: {})

    return [group("patch_static", static), group("patch_dynamic", dynamic)]


def _quadrature(clbits: int, clbit: int) -> tuple[float, ...]:
    """Score +1 when the clbit reads 0 and -1 when it reads 1: the measured basis expectation."""
    return tuple(1.0 if not (outcome >> clbit) & 1 else -1.0 for outcome in range(1 << clbits))


def _excited(clbits: int, clbit: int) -> tuple[float, ...]:
    return tuple(float((outcome >> clbit) & 1) for outcome in range(1 << clbits))


def _difference(name: str, first: str, second: str, values: tuple[tuple[float, ...], ...], width: float) -> tuple:
    return (name, (ObservableTerm(first, values[0]), ObservableTerm(second, values[1], sign=-1)), width)


def patch_contracts(delays_dt: list[int], alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Two-sided precision on the comparisons that separate the window hypotheses.

    Each endpoint is a difference of members, so a predicted interval narrower
    than its half-width resolves the comparison whatever sign the hardware
    gives it; the calibration noise model has no coherent window phase to
    predict an effect from. Alpha is shared across the endpoints.
    """
    middle, longest = sorted(delays_dt)[len(delays_dt) // 2], max(delays_dt)
    pair_a, pair_b, window_a, window_b = _quadrature(2, 0), _quadrature(2, 1), _quadrature(3, 1), _quadrature(3, 2)
    endpoints = [
        _difference(
            "work_a_echo_minus_plain_y",
            f"ramsey_echo_y_d{longest}",
            f"ramsey_plain_y_d{longest}",
            (pair_a, pair_a),
            0.25,
        ),
        _difference(
            "work_b_echo_minus_plain_y",
            f"ramsey_echo_y_d{longest}",
            f"ramsey_plain_y_d{longest}",
            (pair_b, pair_b),
            0.25,
        ),
        _difference(
            "work_a_window_minus_plain_y",
            f"window_measure_reset_c1_y_d{middle}",
            f"ramsey_plain_y_d{middle}",
            (window_a, pair_a),
            0.25,
        ),
        _difference(
            "work_b_window_minus_plain_y",
            f"window_measure_reset_c1_y_d{middle}",
            f"ramsey_plain_y_d{middle}",
            (window_b, pair_b),
            0.25,
        ),
        _difference(
            "work_a_control_one_minus_zero_y",
            f"window_measure_reset_c1_y_d{middle}",
            f"window_measure_reset_c0_y_d{middle}",
            (window_a, window_a),
            0.25,
        ),
        _difference(
            "work_a_measured_minus_reset_only_y",
            f"window_measure_reset_c1_y_d{middle}",
            f"window_reset_only_c1_y_d{middle}",
            (window_a, window_a),
            0.25,
        ),
        _difference(
            "work_a_paired_minus_single_y",
            f"ramsey_plain_y_d{longest}",
            f"ramsey_plain_y_d{longest}_only_work_a",
            (pair_a, pair_a),
            0.25,
        ),
        _difference(
            "spectator_excess_from_work_a",
            f"exchange_work_a_d{longest}",
            f"exchange_none_d{longest}",
            (_excited(5, SPECTATOR - 1),) * 2,
            0.12,
        ),
    ]
    for name, first, second in (
        ("orbit_barrier_minus_nominal", "window_barrier", "nominal"),
        ("orbit_echo_minus_barrier", "window_echo", "window_barrier"),
    ):
        terms = (
            ObservableTerm(f"orbit_{first}_feedback", SIGNED),
            ObservableTerm(f"orbit_{first}_no_feedback", SIGNED, sign=-1),
            ObservableTerm(f"orbit_{second}_feedback", SIGNED, sign=-1),
            ObservableTerm(f"orbit_{second}_no_feedback", SIGNED),
        )
        endpoints.append((name, terms, 0.25))
    return tuple(
        ObservableContract(name, terms, alpha=alpha / len(endpoints), power=power, precision_half_width=width)
        for name, terms, width in endpoints
    )


def _exact_law(circuit: QuantumCircuit) -> np.ndarray:
    from qpe_diagnostics import ideal_branch_probabilities

    return np.asarray(ideal_branch_probabilities(circuit), dtype=float)


def _verify() -> None:
    delays = list(PATCH_DELAYS_DT)
    static, dynamic = patch_circuits(delays, 416, 502)
    names = [circuit.name for circuit in static + dynamic]
    if (len(static), len(dynamic), len(set(names))) != (24, 22, 46):
        raise RuntimeError(
            f"patch design changed: {len(static)} static, {len(dynamic)} dynamic, {len(set(names))} names"
        )
    for group in patch_groups(delays, 416, 502):
        for member in group.members:
            observed = _exact_law(member.circuit)
            if not np.allclose(observed, member.ideal, atol=1e-12):
                raise RuntimeError(f"{member.name}: exact circuit law {observed} differs from {member.ideal}")
    from local_compute import is_dynamic

    if any(is_dynamic(circuit) for circuit in static):
        raise RuntimeError("a static patch circuit measures before later quantum work")
    if not all({"reset", "if_else"} & set(circuit.count_ops()) for circuit in dynamic):
        raise RuntimeError("a dynamic patch circuit lost its reset or feed-forward")
    for contract in patch_contracts(delays, 0.05, 0.8):
        missing = {term.member for term in contract.terms} - set(names)
        if missing:
            raise RuntimeError(f"{contract.name} names absent members {missing}")
    without_basis_change = ramsey(900, "plain", "y")
    without_basis_change.data = [i for i in without_basis_change.data if i.operation.name != "sdg"]
    if np.allclose(_exact_law(without_basis_change), [0.25] * 4, atol=1e-12):
        raise RuntimeError("the Y-quadrature law cannot distinguish a missing basis change")
    for invalid in (-2, 901):
        try:
            ramsey(invalid, "plain", "x")
        except ValueError:
            continue
        raise RuntimeError(f"Ramsey accepted delay {invalid}")
    print("patch characterization: 24 static and 22 dynamic members match exact laws; contracts name real members")


if __name__ == "__main__":
    _verify()
