"""Contracts of the idle-penalty campaign: ideal laws, job kinds, matched readout arms and the readout-train fit."""

from __future__ import annotations

from collections import Counter

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston, FakeMarrakesh

import idle_penalty as ip
from local_compute import is_dynamic


def _on(circuit: QuantumCircuit, pair: tuple[int, int]) -> QuantumCircuit:
    """circuit with T and S on the physical qubits of pair, on a 156-qubit register."""
    wide = QuantumCircuit(156, circuit.num_clbits, name=circuit.name)
    return wide.compose(circuit, qubits=list(pair), clbits=list(range(circuit.num_clbits)))


def test_every_member_matches_its_ideal_law_and_job_kind() -> None:
    for name, circuit, ideal in ip.idle_penalty_circuits():
        probabilities = Statevector(ip._unitary_part(circuit)).probabilities()
        if not np.allclose(probabilities, ideal, atol=1e-12):
            raise AssertionError(f"{name}: statevector law differs from its ideal")
        if not is_dynamic(circuit):
            raise AssertionError(f"{name}: classifies static, so it would leave the group's job")


def test_ideal_summary_reads_unit_visibility_and_zero_phase() -> None:
    group = ip.idle_penalty_group()
    summary = group.summarize({member.name: member.ideal for member in group.members})
    keys = [f"ramsey_{d}dt" for d in ip.RAMSEY_DT] + [f"echo_{d}dt" for d in ip.ECHO_DT] + ["meas_during", "meas_after"]
    roles = [f"{role}_{key}" for role in ("target", "spectator") for key in keys] + ["target_zz"]
    for key in roles:
        if abs(summary[f"{key}_visibility"] - 1.0) > 1e-12 or abs(summary[f"{key}_phase"]) > 1e-12:
            raise AssertionError(f"{key}: ideal visibility differs from one or phase from zero")
    for role in ("target", "spectator"):
        if summary[f"{role}_p1_ground"] != 0.0 or summary[f"{role}_p0_excited"] != 0.0:
            raise AssertionError(f"{role}: ideal assignment references differ from zero")


def _placed_ops(circuit: QuantumCircuit) -> Counter[tuple[str, tuple[int, ...], float]]:
    """Each operation with its qubits and duration, barriers aside: a train moved to the probe changes it."""
    return Counter(
        (
            inst.operation.name,
            tuple(circuit.find_bit(q).index for q in inst.qubits),
            float(getattr(inst.operation, "duration", 0) or 0),
        )
        for inst in circuit.data
        if inst.operation.name != "barrier"
    )


def test_readout_arms_carry_the_same_physical_operations() -> None:
    members = {name: circuit for name, circuit, _ in ip.idle_penalty_circuits()}
    for head, quadrature in [(head, q) for head in ("idle_", "idle_s_") for q in ip.QUADRATURES]:
        during, after = members[f"{head}meas_during_{quadrature}"], members[f"{head}meas_after_{quadrature}"]
        ops = [_placed_ops(c) for c in (during, after)]
        if ops[0] != ops[1]:
            raise AssertionError(f"{head}{quadrature}: the during and after arms differ in operations")


@pytest.mark.parametrize("backend", [FakeKingston(), FakeFez(), FakeMarrakesh()], ids=lambda b: b.name)
def test_readout_train_fits_inside_the_target_idle(backend: object) -> None:
    target = backend.target  # type: ignore[attr-defined]
    pair = next(iter(target["cz"]))
    members = [_on(circuit, pair) for _, circuit, _ in ip.idle_penalty_circuits()]
    reasons = ip.routed_pair_violations(members, target)
    if reasons:
        raise AssertionError(reasons)


def test_a_pair_off_any_coupler_is_rejected() -> None:
    target = FakeKingston().target
    coupled = {q for edge in target["cz"] for q in edge if 0 in edge}
    far = next(q for q in range(target.num_qubits) if q not in coupled and q != 0)
    members = [_on(circuit, (0, far)) for _, circuit, _ in ip.idle_penalty_circuits()]
    if not any("not one Target CZ coupler" in reason for reason in ip.routed_pair_violations(members, target)):
        raise AssertionError("a pair off every coupler was admitted")


def test_a_slow_measure_rejects_the_placement() -> None:
    target = FakeKingston().target
    slow = ip.MEAS_DT // ip.MEAS_COUNT
    pair = next(iter(target["cz"]))
    target["measure"][(pair[1],)].duration = slow * target.dt
    members = [_on(circuit, pair) for _, circuit, _ in ip.idle_penalty_circuits()]
    reasons = ip.routed_pair_violations(members, target)
    if len(reasons) != 3 * len(ip.QUADRATURES):
        raise AssertionError(f"a {slow} dt measure left the readout arms admitted: {reasons}")


def test_pin_layout_admits_idle_penalty_and_still_refuses_unpinned_campaigns() -> None:
    import live_run

    if "idle_penalty" not in live_run.PIN_CAPABLE_CAMPAIGNS or "idle_penalty" in live_run.PINNED_CAMPAIGNS:
        raise AssertionError("idle_penalty must accept a pin without requiring one")
    with pytest.raises(SystemExit):
        live_run.main(["--groups", "qubit_baseline", "--pin-layout", "ibm_kingston:150,149/21,36"])
