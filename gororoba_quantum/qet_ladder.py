"""QET passivity ladder: whether a measured record lowers a local energy below its vacuum value.

The encoded model is Hotta's two-qubit Hamiltonian H = H_A + H_B + V with
H_A = -h Z_A + h^2/r, H_B = -h Z_B + h^2/r, V = 2k X_A X_B + 2k^2/r,
r = sqrt(h^2 + k^2), ground energy zero (scripts/qet_two_qubit_reference.py).
A is qubit 0 and B qubit 1; the ground state cos(t)|00> - sin(t)|11>,
tan(2t) = k/h, is prepared by RY(2t) on A, CX and Z on A. Bob's local
energy is L = <H_B + V> = CONST - h <Z_B> + 2k <X_A X_B>, zero on the ground
state.

Every circuit is dynamic. Alice measures A mid-circuit (X_A through H, or
Z_A in the floor arm) into clbit 0, and B branches on that bit with an
if_else whose bodies are Bob's rotation RY(-b phi*), phi* =
atan2(hk, h^2 + 2k^2), or an idle of BRANCH_IDLE_DT, so every arm carries
the same broadcast and measure-to-branch wait. The idle equals two sx on
ibm_kingston; routed_violations rejects a candidate whose Target gives the
if_else bodies of the members unequal durations, which refuses ibm_fez
(12 dt) and ibm_marrakesh (18 dt) for this constant. A is then read again in the
same frame into clbit 1, which gives the physical X_A the estimator uses:
substituting Alice's reported bit for X_A turns a readout error into an
apparent excess (scripts/qet_passivity_controls.py). B is read into clbit 2
in the arm's basis. A distribution index is r + 2a + 4b.

Arms, on the ground state and on the product state |00> (same angle and
Hamiltonian): reference (idle branch, B in X, Y, Z), feedback (b = mu),
and the floor arm (Alice reads Z_A, idle branch, B in Z); on the ground
state also reversed (b = -mu) and fixed plus and minus (one rotation in
both branches), each with B in X and Z; and a readout calibration with A and
B in |11> through the same mid-circuit measure, idle branch and readouts,
whose |00> partner is the product-state floor arm. Nineteen circuits.

Endpoints (summarize):
- channel floor margin -<H_A> - L_fb, sound against every record-independent
  channel on B, positive (E_B) on the ground state and negative on |00>;
- information excess, the Kabsch minimum of L over record-independent
  unitaries on B from the reference arm's Bloch vector s and correlation
  c_j = <X_A sigma_j^B>, minus L_fb;
- the record-binned fixed arms (+, -, -, + ideal) and the feed-forward
  flip q_eff = (L_fb - L_match) / (L_mismatch - L_match), which cancels
  preparation and readout error to first order because both sides bin on
  the same recorded bit;
- the readout-corrected margin, which inverts each terminal bit's measured
  assignment (from the |00> and |11> calibrations) before forming the
  moments; Alice's mid-circuit bit enters only the floor arm, whose idle
  branch makes it a terminal observable there.
Readout error shrinks <Z_A>, <Z_B> and <X_A X_B> toward zero, which lowers
the raw ground-state margin, so the raw margin is the conservative primary.
The values are expectation values of an encoded spin Hamiltonian, not field
stress-energy.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from experiments import Group, Member
from parallel import ordered_map

H_FIELD = 1.0
COUPLING = 1.0
RADIUS = math.hypot(H_FIELD, COUPLING)
CONST = (H_FIELD**2 + 2 * COUPLING**2) / RADIUS
PHI_STAR = math.atan2(H_FIELD * COUPLING, H_FIELD**2 + 2 * COUPLING**2)
THETA = math.atan2(COUPLING, H_FIELD) / 2
E_A = H_FIELD**2 / RADIUS
E_B = math.hypot(H_FIELD, 2 * COUPLING) - (H_FIELD**2 + 2 * COUPLING**2) / RADIUS
# Two sx durations on ibm_kingston (8 dt each), the length an RY compiles to.
BRANCH_IDLE_DT = 16
GROUP_NAME = "qet_ladder"

# (name, preparation, Alice basis, Bob rule, Bob basis); preparations ground, product (|00>) and ones (|11>)
ARMS: tuple[tuple[str, str, str, str, str], ...] = (
    *((f"ref_{basis}", "ground", "x", "idle", basis) for basis in "xyz"),
    *((f"fb_{basis}", "ground", "x", "feedback", basis) for basis in "xz"),
    *((f"rev_{basis}", "ground", "x", "reversed", basis) for basis in "xz"),
    *((f"plus_{basis}", "ground", "x", "plus", basis) for basis in "xz"),
    *((f"minus_{basis}", "ground", "x", "minus", basis) for basis in "xz"),
    ("za", "ground", "z", "idle", "z"),
    *((f"prod_ref_{basis}", "product", "x", "idle", basis) for basis in "xyz"),
    *((f"prod_fb_{basis}", "product", "x", "feedback", basis) for basis in "xz"),
    ("prod_za", "product", "z", "idle", "z"),
    ("cal_11", "ones", "z", "idle", "z"),
)


def bob_angle(rule: str, record: int) -> float | None:
    """Bob's RY angle -b phi* for Alice's bit (mu = 1 - 2 record), or None for the idle branch."""
    mu = 1 - 2 * record
    sign = {"feedback": mu, "reversed": -mu, "plus": 1, "minus": -1}.get(rule)
    return None if sign is None else -sign * PHI_STAR


def _branch(circuit: QuantumCircuit, angle: float | None) -> None:
    if angle is None:
        circuit.delay(BRANCH_IDLE_DT, 1, unit="dt")
    else:
        circuit.ry(angle, 1)


def _bob_basis(circuit: QuantumCircuit, basis: str) -> None:
    if basis == "y":
        circuit.sdg(1)
    if basis in "xy":
        circuit.h(1)


def arm_circuit(name: str, prep: str, alice: str, rule: str, basis: str, deferred: bool = False) -> QuantumCircuit:
    """The arm's dynamic circuit; deferred replaces the branch by controlled rotations for exact checks."""
    qubits = QuantumRegister(2, "q")
    record, final, bob = ClassicalRegister(1, "alice"), ClassicalRegister(1, "a_final"), ClassicalRegister(1, "bob")
    circuit = QuantumCircuit(qubits, record, final, bob, name=f"{GROUP_NAME}_{name}")
    if prep == "ground":
        circuit.ry(2 * THETA, 0)
        circuit.cx(0, 1)
        circuit.z(0)
    elif prep == "ones":
        circuit.x([0, 1])
    if alice == "x":
        circuit.h(0)
    zero, one = bob_angle(rule, 0), bob_angle(rule, 1)
    if deferred:
        if zero is not None and one is not None:
            circuit.ry(zero, 1)
            circuit.cry(one - zero, 0, 1)
        circuit.measure(0, record[0])
    else:
        circuit.measure(0, record[0])
        with circuit.if_test((record[0], 1)) as otherwise:
            _branch(circuit, one)
        with otherwise:
            _branch(circuit, zero)
    circuit.measure(0, final[0])
    _bob_basis(circuit, basis)
    circuit.measure(1, bob[0])
    return circuit


def _ry(angle: float) -> np.ndarray:
    return np.array([[math.cos(angle / 2), -math.sin(angle / 2)], [math.sin(angle / 2), math.cos(angle / 2)]])


def ideal_distribution(prep: str, alice: str, rule: str, basis: str) -> np.ndarray:
    """Exact law over r + 2a + 4b; the state vector is ordered A then B."""
    psi = np.zeros(4, dtype=complex)
    if prep == "product":
        psi[0] = 1.0
    elif prep == "ones":
        psi[3] = 1.0
    else:
        psi[0], psi[3] = math.cos(THETA), -math.sin(THETA)
    hadamard = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
    eye = np.eye(2)
    if alice == "x":
        psi = np.kron(hadamard, eye) @ psi
    change = {"x": hadamard, "y": hadamard @ np.diag([1, -1j]), "z": eye}[basis]
    law = np.zeros(8)
    for record in (0, 1):
        branch = psi.reshape(2, 2)[record]
        angle = bob_angle(rule, record)
        if angle is not None:
            branch = _ry(angle) @ branch
        amplitudes = change @ branch
        for b in (0, 1):
            law[record + 2 * record + 4 * b] = abs(amplitudes[b]) ** 2
    return law


def _arm(item: tuple[tuple[str, str, str, str, str], bool]) -> tuple[str, QuantumCircuit, np.ndarray]:
    (name, prep, alice, rule, basis), deferred = item
    return (
        f"{GROUP_NAME}_{name}",
        arm_circuit(name, prep, alice, rule, basis, deferred=deferred),
        ideal_distribution(prep, alice, rule, basis),
    )


def circuits(deferred: bool = False) -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    return tuple(ordered_map(_arm, [(arm, deferred) for arm in ARMS]))


def _moments(law: np.ndarray, record: int | None = None) -> tuple[float, float, float, float]:
    """(P(r), <sigma_B>, <X_A sigma_B>, <first-bit value>) of a law, conditioned on record when given."""
    total = sigma = corr = first = 0.0
    for index, p in enumerate(np.asarray(law, dtype=float)):
        r, a, b = index & 1, (index >> 1) & 1, (index >> 2) & 1
        if record is not None and r != record:
            continue
        total += p
        sigma += p * (1 - 2 * b)
        corr += p * (1 - 2 * a) * (1 - 2 * b)
        first += p * (1 - 2 * r)
    if total <= 0:
        return 0.0, 0.0, 0.0, 0.0
    return total, sigma / total, corr / total, first / total


def local_energy(z_law: np.ndarray, x_law: np.ndarray, record: int | None = None) -> float:
    """L = CONST - h <Z_B> + 2k <X_A X_B> from an arm's Z_B and X_B circuits."""
    return CONST - H_FIELD * _moments(z_law, record)[1] + 2 * COUPLING * _moments(x_law, record)[2]


def kabsch_floor(s: np.ndarray, c: np.ndarray) -> float:
    """Minimum over SO(3) of CONST - h z.(R s) + 2k x.(R c).

    tr(R M) with M = -h s z^T + 2k c x^T has rank at most two, so its
    minimum over rotations is -(sigma_1 + sigma_2) from M's singular values.
    """
    m = -H_FIELD * np.outer(s, [0.0, 0.0, 1.0]) + 2 * COUPLING * np.outer(c, [1.0, 0.0, 0.0])
    sigma = np.linalg.svd(m, compute_uv=False)
    return CONST - float(sigma[0] + sigma[1])


def _state_endpoints(dist: Mapping[str, np.ndarray], prefix: str) -> dict[str, float]:
    def law(arm: str) -> np.ndarray:
        return np.asarray(dist[f"{GROUP_NAME}_{prefix}{arm}"], dtype=float)

    s = np.array([_moments(law(f"ref_{basis}"))[1] for basis in "xyz"])
    c = np.array([_moments(law(f"ref_{basis}"))[2] for basis in "xyz"])
    feedback = local_energy(law("fb_z"), law("fb_x"))
    z_a = _moments(law("za"))[3]
    floor = H_FIELD * z_a - H_FIELD**2 / RADIUS
    unitary_floor = kabsch_floor(s, c)
    return {
        f"{prefix}reference_local": local_energy(law("ref_z"), law("ref_x")),
        f"{prefix}feedback_local": feedback,
        f"{prefix}z_a": z_a,
        f"{prefix}channel_floor": floor,
        f"{prefix}channel_floor_margin": floor - feedback,
        f"{prefix}unitary_floor": unitary_floor,
        f"{prefix}information_excess": unitary_floor - feedback,
        f"{prefix}reference_y_correlation": float(c[1]),
    }


def _assignment(dist: Mapping[str, np.ndarray]) -> list[tuple[float, float]]:
    """(P(1 | prepared 0), P(0 | prepared 1)) for bits r, a and b from the |00> floor arm and the |11> calibration."""
    zeros = np.asarray(dist[f"{GROUP_NAME}_prod_za"], dtype=float)
    ones = np.asarray(dist[f"{GROUP_NAME}_cal_11"], dtype=float)
    out = []
    for bit in range(3):
        mask = [index for index in range(8) if (index >> bit) & 1]
        out.append((float(zeros[mask].sum() / zeros.sum()), float(1 - ones[mask].sum() / ones.sum())))
    return out


def _corrected(law: np.ndarray, channels: list[tuple[float, float]]) -> tuple[float, float, float]:
    """True <r>, <b> and <a b> (values 1 - 2 bit) after inverting independent per-bit assignment channels.

    A bit read through P(1 | 0) = e0, P(0 | 1) = e1 has measured mean
    delta + lambda <true> with lambda = 1 - e0 - e1, delta = e1 - e0, and two
    independently read bits have measured product mean
    delta_a delta_b + delta_a lambda_b <b> + lambda_a delta_b <a> + lambda_a lambda_b <a b>.
    """
    law = np.asarray(law, dtype=float) / float(np.sum(law))
    value = {bit: np.array([1 - 2 * ((index >> bit) & 1) for index in range(8)]) for bit in range(3)}
    lam = [1 - e0 - e1 for e0, e1 in channels]
    delta = [e1 - e0 for e0, e1 in channels]
    true = {bit: (float(law @ value[bit]) - delta[bit]) / lam[bit] for bit in range(3)}
    product = float(law @ (value[1] * value[2]))
    true_ab = (product - delta[1] * delta[2] - delta[1] * lam[2] * true[2] - lam[1] * delta[2] * true[1]) / (
        lam[1] * lam[2]
    )
    return true[0], true[2], true_ab


def _corrected_margin(dist: Mapping[str, np.ndarray], prefix: str, channels: list[tuple[float, float]]) -> float:
    def law(arm: str) -> np.ndarray:
        return np.asarray(dist[f"{GROUP_NAME}_{prefix}{arm}"], dtype=float)

    feedback = (
        CONST - H_FIELD * _corrected(law("fb_z"), channels)[1] + 2 * COUPLING * _corrected(law("fb_x"), channels)[2]
    )
    floor = H_FIELD * _corrected(law("za"), channels)[0] - H_FIELD**2 / RADIUS
    return floor - feedback


def summarize(dist: Mapping[str, np.ndarray]) -> dict[str, float]:
    def law(arm: str) -> np.ndarray:
        return np.asarray(dist[f"{GROUP_NAME}_{arm}"], dtype=float)

    out = _state_endpoints(dist, "")
    out.update(_state_endpoints(dist, "prod_"))
    out["product_mutation_margin_drop"] = out["channel_floor_margin"] - out["prod_channel_floor_margin"]
    reversed_ = local_energy(law("rev_z"), law("rev_x"))
    out["reversed_local"] = reversed_
    out["contrast"] = (reversed_ - out["feedback_local"]) / 2
    weights = [
        float(np.mean([_moments(law(f"{rule}_{basis}"), record)[0] for rule in ("plus", "minus") for basis in "xz"]))
        for record in (0, 1)
    ]
    binned = {}
    for record in (0, 1):
        for rule in ("plus", "minus"):
            binned[(record, rule)] = local_energy(law(f"{rule}_z"), law(f"{rule}_x"), record)
            reference = local_energy(law("ref_z"), law("ref_x"), record)
            key = ("+" if record == 0 else "-") + ("+" if rule == "plus" else "-")
            out[f"binned_drop_{key}"] = reference - binned[(record, rule)]
    match = weights[0] * binned[(0, "plus")] + weights[1] * binned[(1, "minus")]
    mismatch = weights[0] * binned[(0, "minus")] + weights[1] * binned[(1, "plus")]
    out["match_local"], out["mismatch_local"] = match, mismatch
    out["q_eff"] = (out["feedback_local"] - match) / (mismatch - match) if mismatch != match else float("nan")
    out["record_p1"] = weights[1]
    channels = _assignment(dist)
    for bit, (e0, e1) in zip(("r", "a", "b"), channels, strict=True):
        out[f"assignment_{bit}_p1_given_0"], out[f"assignment_{bit}_p0_given_1"] = e0, e1
    out["readout_corrected_channel_floor_margin"] = _corrected_margin(dist, "", channels)
    out["prod_readout_corrected_channel_floor_margin"] = _corrected_margin(dist, "prod_", channels)
    return out


def _duration_dt(operation: Any, physical: int, target: Any) -> float:
    if operation.name == "delay":
        if operation.unit != "dt":
            raise ValueError(f"branch delay in {operation.unit}, expected dt")
        return float(operation.duration)
    if operation.name in ("rz", "barrier"):
        return 0.0
    return float(target[operation.name][(physical,)].duration) / float(target.dt)


def branch_duration_violations(isas: list[QuantumCircuit], target: Any) -> list[str]:
    """Reasons a candidate's if_else bodies differ in duration on target, across every member and branch."""
    durations: dict[float, list[str]] = {}
    for isa in isas:
        for instruction in isa.data:
            if instruction.operation.name != "if_else":
                continue
            for index, block in enumerate(instruction.operation.blocks):
                total = 0.0
                for inner in block.data:
                    for qubit in inner.qubits:
                        physical = isa.find_bit(instruction.qubits[block.find_bit(qubit).index]).index
                        total += _duration_dt(inner.operation, physical, target)
                durations.setdefault(round(total, 6), []).append(f"{isa.name}[{index}]")
    if len(durations) > 1:
        summary = ", ".join(f"{value} dt in {len(names)} bodies" for value, names in sorted(durations.items()))
        return [f"if_else bodies differ in duration ({summary}); BRANCH_IDLE_DT = {BRANCH_IDLE_DT}"]
    return []


def qet_ladder_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in circuits())
    return Group(GROUP_NAME, members, summarize, routed_violations=branch_duration_violations)
