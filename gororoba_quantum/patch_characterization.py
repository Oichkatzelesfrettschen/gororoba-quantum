"""Ramsey, readout-window and exchange characterization of a pinned six-qubit patch.

The patch binds logical qubits to physical ones in the order control, work A,
spectator, work B, neighbor of A, neighbor of B; the N=21 orbit runs placed
control, work bit 1, work bit 4 and work bit 16 on the first four. Static
Ramsey circuits put both work qubits in |+>, idle them for a delay with or
without a midpoint X echo, and read them in the X or Y basis, so the pair of
quadratures gives each qubit's accumulated phase and coherence. Readout-window
circuits run the same Ramsey while the control, prepared in |0> or |1>, is
measured and reset, the operations the orbit window performs. Exchange
circuits excite one work qubit, idle, and read the whole patch, so population
leaving the work qubit for the spectator or a neighbor shows directly. The
barrier pair repeats the orbit feed-forward comparison with a barrier before
the first measurement, which completes both multipliers' first round before
the window in both members.
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
# Idle lengths in dt bracketing the orbit window, 3.6 to 7.6 us at 4 ns per dt.
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
CONTROL_STATES = (0, 1)


def _validate_delay(delay_dt: int) -> None:
    if type(delay_dt) is not int or delay_dt <= 0 or delay_dt % 2:
        raise ValueError("patch delays are positive even integers in dt so an echo splits them evenly")


def _patch(name: str, clbits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(QuantumRegister(len(PATCH_ROLES), "patch"), ClassicalRegister(clbits, "c"))
    circuit.name = name
    return circuit


def _read_work(circuit: QuantumCircuit, quadrature: str, first_clbit: int) -> None:
    for offset, qubit in enumerate((WORK_A, WORK_B)):
        if quadrature == "y":
            circuit.sdg(qubit)
        circuit.h(qubit)
        circuit.measure(qubit, first_clbit + offset)


def ramsey(delay_dt: int, variant: str, quadrature: str) -> QuantumCircuit:
    """Both work qubits idle in |+> for delay_dt, echoed at the midpoint when variant is echo."""
    _validate_delay(delay_dt)
    if variant not in RAMSEY_VARIANTS or quadrature not in QUADRATURES:
        raise ValueError(f"unknown Ramsey variant {variant!r} or quadrature {quadrature!r}")
    circuit = _patch(f"ramsey_{variant}_{quadrature}_d{delay_dt}", 2)
    circuit.h([WORK_A, WORK_B])
    circuit.barrier()
    if variant == "plain":
        circuit.delay(delay_dt, [WORK_A, WORK_B], unit="dt")
    else:
        for _half in range(2):
            circuit.delay(delay_dt // 2, [WORK_A, WORK_B], unit="dt")
            circuit.x([WORK_A, WORK_B])
    circuit.barrier()
    _read_work(circuit, quadrature, 0)
    return circuit


def readout_window(delay_dt: int, control_state: int, quadrature: str) -> QuantumCircuit:
    """Ramsey on both work qubits while the control is measured and reset inside the idle.

    The control's bit is clbit 0; the work qubits read into clbits 1 and 2.
    The idle lasts at least delay_dt and at least the measurement and reset.
    """
    _validate_delay(delay_dt)
    if control_state not in CONTROL_STATES or quadrature not in QUADRATURES:
        raise ValueError(f"unknown control state {control_state!r} or quadrature {quadrature!r}")
    circuit = _patch(f"readout_window_c{control_state}_{quadrature}_d{delay_dt}", 3)
    if control_state:
        circuit.x(CONTROL)
    circuit.h([WORK_A, WORK_B])
    circuit.barrier()
    circuit.delay(delay_dt, [WORK_A, WORK_B], unit="dt")
    circuit.measure(CONTROL, 0)
    circuit.reset(CONTROL)
    circuit.barrier()
    _read_work(circuit, quadrature, 1)
    return circuit


def exchange(delay_dt: int, target: int) -> QuantumCircuit:
    """Excite one work qubit, idle the patch, and read every patch qubit except the control."""
    _validate_delay(delay_dt)
    if target not in (WORK_A, WORK_B):
        raise ValueError("exchange excites work qubit A or B")
    circuit = _patch(f"exchange_{PATCH_ROLES[target]}_d{delay_dt}", 5)
    circuit.x(target)
    circuit.barrier()
    circuit.delay(delay_dt, list(range(1, len(PATCH_ROLES))), unit="dt")
    circuit.barrier()
    for clbit, qubit in enumerate(range(1, len(PATCH_ROLES))):
        circuit.measure(qubit, clbit)
    return circuit


def barrier_orbit(feed_forward: bool) -> QuantumCircuit:
    """The N=21 orbit comparison with a barrier before the first measurement, on the first four patch qubits."""
    from qpe_diagnostics import n21_orbit_diagnostic

    orbit = n21_orbit_diagnostic(feed_forward, "window_barrier")
    circuit = _patch(f"barrier_orbit_{'feedback' if feed_forward else 'no_feedback'}", orbit.num_clbits)
    circuit.compose(orbit, qubits=[CONTROL, WORK_A, SPECTATOR, WORK_B], clbits=range(orbit.num_clbits), inplace=True)
    return circuit


def _exact_law(circuit: QuantumCircuit) -> np.ndarray:
    from qpe_diagnostics import ideal_branch_probabilities

    return np.asarray(ideal_branch_probabilities(circuit), dtype=float)


def _expected_law(name: str) -> list[Fraction]:
    """Independent labeled law of each member, from the preparation alone."""
    if name.startswith("ramsey_"):
        quadrature = name.split("_")[2]
        return [Fraction(1)] + [Fraction(0)] * 3 if quadrature == "x" else [Fraction(1, 4)] * 4
    if name.startswith("readout_window_"):
        control_state, quadrature = int(name.split("_")[2][1]), name.split("_")[3]
        work = [Fraction(1)] + [Fraction(0)] * 3 if quadrature == "x" else [Fraction(1, 4)] * 4
        law = [Fraction(0)] * 8
        for outcome, probability in enumerate(work):
            law[control_state + 2 * outcome] = probability
        return law
    if name.startswith("exchange_"):
        target = WORK_A if "work_a" in name else WORK_B
        law = [Fraction(0)] * 32
        law[1 << (target - 1)] = Fraction(1)
        return law
    from qpe_diagnostics import n21_labeled_law

    return list(n21_labeled_law("no_feedback" not in name))


def patch_groups(delays_dt: list[int]) -> list[Group]:
    """The static characterization group and the dynamic window group for the given delays."""
    for delay in delays_dt:
        _validate_delay(delay)
    static = [ramsey(d, v, q) for d in delays_dt for v in RAMSEY_VARIANTS for q in QUADRATURES]
    static += [exchange(d, target) for d in delays_dt for target in (WORK_A, WORK_B)]
    dynamic = [readout_window(d, c, q) for d in delays_dt for c in CONTROL_STATES for q in QUADRATURES]
    dynamic += [barrier_orbit(True), barrier_orbit(False)]

    def group(name: str, circuits: list[QuantumCircuit]) -> Group:
        members = tuple(Member(c.name, c, np.asarray([float(p) for p in _expected_law(c.name)])) for c in circuits)
        return Group(name, members, lambda distributions: {})

    return [group("patch_static", static), group("patch_dynamic", dynamic)]


def patch_contracts(delays_dt: list[int], alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Each work qubit keeps X-basis Ramsey visibility at the shortest plain delay."""
    shortest = min(delays_dt)
    name = f"ramsey_plain_x_d{shortest}"
    contracts = []
    for bit, role in ((0, "work_a"), (1, "work_b")):
        values = tuple(1.0 if not (outcome >> bit) & 1 else -1.0 for outcome in range(4))
        contracts.append(
            ObservableContract(
                f"{role}_ramsey_visibility",
                (ObservableTerm(name, values),),
                minimum_effect=0.0,
                alpha=alpha / 2,
                power=power,
            )
        )
    return tuple(contracts)


def _verify() -> None:
    delays = [900, 1400, 1900]
    groups = patch_groups(delays)
    names = [member.name for group in groups for member in group.members]
    if len(names) != len(set(names)) or len(names) != 3 * 4 + 3 * 2 + 3 * 4 + 2:
        raise RuntimeError(f"patch members changed: {len(names)} members")
    for group in groups:
        for member in group.members:
            observed = _exact_law(member.circuit)
            if not np.allclose(observed, member.ideal, atol=1e-12):
                raise RuntimeError(f"{member.name}: exact circuit law {observed} differs from {member.ideal}")
    dynamic = {member.name for member in groups[1].members}
    static_ops = {op for member in groups[0].members for op in member.circuit.count_ops()}
    if static_ops & {"reset", "if_else"} or not all(
        "reset" in member.circuit.count_ops() or "barrier_orbit" in member.name for member in groups[1].members
    ):
        raise RuntimeError("static and dynamic patch circuits crossed job kinds")
    if {"barrier_orbit_feedback", "barrier_orbit_no_feedback"} - dynamic:
        raise RuntimeError("the barrier orbit pair is missing")
    for invalid in (0, -2, 901):
        try:
            ramsey(invalid, "plain", "x")
        except ValueError:
            continue
        raise RuntimeError(f"Ramsey accepted delay {invalid}")
    without_basis_change = ramsey(900, "plain", "y")
    without_basis_change.data = [i for i in without_basis_change.data if i.operation.name != "sdg"]
    if np.allclose(
        _exact_law(without_basis_change), [float(value) for value in _expected_law("ramsey_plain_y_d900")], atol=1e-12
    ):
        raise RuntimeError("the Y-quadrature law cannot distinguish a missing basis change")
    print(f"patch characterization: {len(names)} members match exact laws; job kinds and delays checked")


if __name__ == "__main__":
    _verify()
