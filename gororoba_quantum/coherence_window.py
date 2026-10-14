"""Branch-signed work coherence after the first N=21 orbit round, in three window contexts.

The first orbit round (patch_characterization.orbit, qpe_diagnostics.n21_orbit_diagnostic)
leaves the control's first bit b0 correlated with the work superposition: on
the pinned patch, work_a and work_b carry |10> + (-1)^b0 e^{i phi} |01> with
the spectator in |0>. The selected coherence rho_{10,01} therefore changes
sign with b0, and its average over both branches is zero on an ideal device;
weighting every shot by (-1)^b0 recovers it.

Each circuit runs the round-1 prefix, then one of three contexts before the
work readout:

- immediate: every qubit is measured at the end, with no window;
- matched_idle: the patch idles for window_dt (the control's measure plus
  reset duration) and every qubit, the control included, is measured at the
  end, so b0 is read after the window;
- measure_reset: the control is measured into b0 and reset mid-circuit, and
  the work and spectator are read after that window.

Every circuit writes four clbits: b0 (c0), the work_a and work_b readouts in
the setting's bases (c1, c2), and the spectator in Z (c3), the sector
indicator. For the Pauli settings P, Q in {X, Y} the signed correlation is
S_PQ = E[(-1)^(c0 + c1 + c2)], and with the work pair in |work_a work_b>
order

    C = (S_XX + S_YY + i (S_XY - S_YX)) / 4

is the branch-signed rho_{10,01}; the ideal value has |C| = 1/2 in every
context. A coherent phase acquired during the window rotates C, dephasing
and amplitude damping shrink |C|, and first-bit assignment error epsilon
scales C by (1 - 2 epsilon). matched_idle reads b0 after the window, so
control relaxation during the window adds to that context's epsilon; it
scales C without rotating it, like every first-bit error. The ZZ setting
returns the work populations.
"""

from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member
from patch_characterization import CONTROL, PATCH_ROLES, SPECTATOR, WORK_A, WORK_B, _patch

CONTEXTS = ("immediate", "matched_idle", "measure_reset")
SETTINGS = ("xx", "xy", "yx", "yy", "zz")
PAULI_SETTINGS = SETTINGS[:4]
CLBITS = 4
B0, READ_A, READ_B, SECTOR = range(CLBITS)


def _basis(circuit: QuantumCircuit, qubit: int, axis: str) -> None:
    if axis == "y":
        circuit.sdg(qubit)
    if axis in ("x", "y"):
        circuit.h(qubit)


def coherence_circuit(context: str, setting: str, window_dt: int) -> QuantumCircuit:
    """The round-1 prefix, one window context and one work readout setting."""
    if context not in CONTEXTS or setting not in SETTINGS:
        raise ValueError(f"unknown context {context!r} or setting {setting!r}")
    if context == "matched_idle" and (type(window_dt) is not int or window_dt <= 0):
        raise ValueError("matched_idle requires a positive integer window_dt from calibration")
    circuit = _patch(f"coherence_{context}_{setting}", CLBITS)
    circuit.x(WORK_A)
    circuit.h(CONTROL)
    circuit.cswap(CONTROL, WORK_A, SPECTATOR)
    circuit.cswap(CONTROL, SPECTATOR, WORK_B)
    circuit.h(CONTROL)
    circuit.barrier()
    if context == "measure_reset":
        circuit.measure(CONTROL, B0)
        circuit.reset(CONTROL)
        circuit.barrier()
    elif context == "matched_idle":
        circuit.delay(window_dt, [CONTROL, WORK_A, SPECTATOR, WORK_B], unit="dt")
        circuit.barrier()
    _basis(circuit, WORK_A, setting[0])
    _basis(circuit, WORK_B, setting[1])
    if context != "measure_reset":
        circuit.measure(CONTROL, B0)
    circuit.measure(WORK_A, READ_A)
    circuit.measure(WORK_B, READ_B)
    circuit.measure(SPECTATOR, SECTOR)
    return circuit


def coherence_circuits(window_dt: int) -> tuple[list[QuantumCircuit], list[QuantumCircuit]]:
    """Ten static circuits (immediate, matched_idle) and five dynamic ones (measure_reset)."""
    static = [coherence_circuit(c, s, window_dt) for c in CONTEXTS[:2] for s in SETTINGS]
    dynamic = [coherence_circuit("measure_reset", s, window_dt) for s in SETTINGS]
    return static, dynamic


def signed_parity() -> tuple[float, ...]:
    """(-1)^(b0 + read_a + read_b) per outcome: the branch-signed Pauli correlation score."""
    return tuple(-1.0 if ((o >> B0) ^ (o >> READ_A) ^ (o >> READ_B)) & 1 else 1.0 for o in range(1 << CLBITS))


def unsigned_parity() -> tuple[float, ...]:
    """(-1)^(read_a + read_b): the branch-unsigned correlation, zero on an ideal device."""
    return tuple(-1.0 if ((o >> READ_A) ^ (o >> READ_B)) & 1 else 1.0 for o in range(1 << CLBITS))


def coherence(distributions: dict[str, np.ndarray], context: str, score: tuple[float, ...] | None = None) -> complex:
    """C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 from one context's four Pauli-setting distributions."""
    values = np.asarray(signed_parity() if score is None else score)
    s = {setting: float(values @ distributions[f"coherence_{context}_{setting}"]) for setting in PAULI_SETTINGS}
    return complex(s["xx"] + s["yy"], s["xy"] - s["yx"]) / 4


def _expected_law(circuit: QuantumCircuit) -> np.ndarray:
    from qpe_diagnostics import ideal_branch_probabilities

    return np.asarray(ideal_branch_probabilities(circuit), dtype=float)


def coherence_groups(window_dt: int) -> list[Group]:
    """The static group (immediate, matched_idle) and the dynamic group (measure_reset)."""
    static, dynamic = coherence_circuits(window_dt)

    def group(name: str, circuits: list[QuantumCircuit]) -> Group:
        members = tuple(Member(c.name, c, _expected_law(c)) for c in circuits)
        return Group(name, members, lambda distributions: {})

    return [group("coherence_static", static), group("coherence_dynamic", dynamic)]


def _context_terms(context: str, part: str, sign: int) -> tuple[ObservableTerm, ...]:
    signed = signed_parity()
    pairs = (("xx", 1), ("yy", 1)) if part == "re" else (("xy", 1), ("yx", -1))
    return tuple(ObservableTerm(f"coherence_{context}_{s}", signed, sign=sign * k) for s, k in pairs)


def coherence_contracts(alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Two-sided precision on 4 Re C and 4 Im C differences between adjacent contexts.

    A window phase delta rotates C, so 4 Im C moves by about 4 |C| delta
    between contexts, while shrinkage moves 4 Re C. A difference half-width of
    0.33 (Hoeffding over four arbitrary-within-shot terms at 2048 shots each)
    resolves a 0.17 rad rotation at the ideal |C| = 1/2 and 0.19 rad at
    |C| = 0.43. The immediate context's 4 Re C anchors the visibility at 0.24.
    Alpha is shared.
    """
    endpoints: list[tuple[str, tuple[ObservableTerm, ...], float]] = [
        ("re_immediate", _context_terms("immediate", "re", 1), 0.24),
    ]
    for later, earlier in (("matched_idle", "immediate"), ("measure_reset", "matched_idle")):
        for part in ("re", "im"):
            terms = _context_terms(later, part, 1) + _context_terms(earlier, part, -1)
            endpoints.append((f"{part}_{later}_minus_{earlier}", terms, 0.33))
    return tuple(
        ObservableContract(name, terms, alpha=alpha / len(endpoints), power=power, precision_half_width=width)
        for name, terms, width in endpoints
    )


def _verify() -> None:
    from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace

    window = 1000
    static, dynamic = coherence_circuits(window)
    names = [c.name for c in static + dynamic]
    if (len(static), len(dynamic), len(set(names))) != (10, 5, 15):
        raise RuntimeError("the case has ten static and five dynamic circuits with distinct names")
    if any(
        op.operation.name in ("reset",) or op.operation.name == "measure" and i < len(c.data) - 4
        for c in static
        for i, op in enumerate(c.data)
    ):
        raise RuntimeError("static circuits measure only at the end and never reset")
    laws = {c.name: _expected_law(c) for c in static + dynamic}
    for law in laws.values():
        if not math.isclose(float(law.sum()), 1.0, abs_tol=1e-12):
            raise RuntimeError("an ideal law does not sum to one")
    # Independent reference: the post-round-1 state, projected on each control outcome.
    prefix = QuantumCircuit(len(PATCH_ROLES))
    prefix.x(WORK_A)
    prefix.h(CONTROL)
    prefix.cswap(CONTROL, WORK_A, SPECTATOR)
    prefix.cswap(CONTROL, SPECTATOR, WORK_B)
    prefix.h(CONTROL)
    state = DensityMatrix(Statevector(prefix))
    reference = 0j
    for b0 in (0, 1):
        projector = np.zeros((2, 2))
        projector[b0, b0] = 1.0
        full = np.kron(np.eye(1 << (len(PATCH_ROLES) - 1)), projector)
        branch = DensityMatrix(full @ state.data @ full)
        work = partial_trace(branch, [q for q in range(len(PATCH_ROLES)) if q not in (WORK_A, WORK_B)]).data
        # Qiskit orders the reduced pair little-endian: index = work_a + 2 work_b.
        # |work_a work_b> = |10> is index 1 and |01> is index 2.
        reference += (-1) ** b0 * work[1, 2]
    for context in CONTEXTS:
        value = coherence(laws, context)
        if not (math.isclose(abs(value), 0.5, abs_tol=1e-9) and abs(value - reference) < 1e-9):
            raise RuntimeError(f"{context}: branch-signed C {value} differs from rho_10,01 {reference}")
        if abs(coherence(laws, context, unsigned_parity())) > 1e-9:
            raise RuntimeError(f"{context}: the branch-unsigned coherence is not zero")
        population = laws[f"coherence_{context}_zz"]
        sector = sum(p for o, p in enumerate(population) if not (o >> SECTOR) & 1)
        one_hot = sum(p for o, p in enumerate(population) if ((o >> READ_A) ^ (o >> READ_B)) & 1)
        if not (math.isclose(sector, 1.0, abs_tol=1e-12) and math.isclose(one_hot, 1.0, abs_tol=1e-12)):
            raise RuntimeError(f"{context}: the ideal work pair leaves the one-hot sector")
    # A Z rotation by delta on work_b inside the window rotates C by a fixed
    # angle of magnitude delta, and a symmetric first-bit flip with
    # probability epsilon scales C by (1 - 2 epsilon) without rotating it.
    from qiskit.circuit import CircuitInstruction
    from qiskit.circuit.library import RZGate

    delta = 0.3
    probed = {}
    for setting in PAULI_SETTINGS:
        circuit = coherence_circuit("immediate", setting, window)
        first_barrier = next(i for i, op in enumerate(circuit.data) if op.operation.name == "barrier")
        circuit.data.insert(first_barrier + 1, CircuitInstruction(RZGate(delta), (circuit.qubits[WORK_B],)))
        probed[f"coherence_immediate_{setting}"] = _expected_law(circuit)
    base, turned = coherence(laws, "immediate"), coherence(probed, "immediate")
    if not (
        math.isclose(abs(turned), 0.5, abs_tol=1e-9) and math.isclose(abs(np.angle(turned / base)), delta, abs_tol=1e-9)
    ):
        raise RuntimeError("a window Z rotation does not rotate C by its angle")
    epsilon = 0.07
    flipped = {}
    for name, law in laws.items():
        mixed = (1 - epsilon) * law
        for outcome, probability in enumerate(law):
            mixed[outcome ^ (1 << B0)] += epsilon * probability
        flipped[name] = mixed
    if abs(coherence(flipped, "immediate") - (1 - 2 * epsilon) * base) > 1e-12:
        raise RuntimeError("a first-bit flip does not scale C by (1 - 2 epsilon)")
    contracts = coherence_contracts(0.05, 0.8)
    if len(contracts) != 5 or any(c.precision_half_width is None for c in contracts):
        raise RuntimeError("five two-sided precision endpoints")
    members = {member.name for group in coherence_groups(window) for member in group.members}
    if not all(term.member in members for contract in contracts for term in contract.terms):
        raise RuntimeError("a contract names a member outside the groups")


if __name__ == "__main__":
    _verify()
    print("coherence window: 15 circuits; branch-signed C = rho_10,01 with |C| = 1/2 and zero unsigned average")
