"""Executable contracts and property tests for maximal-scale experiments."""

from __future__ import annotations

import copy
import warnings
from typing import Any

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKingston

import packing
from experiments import all_experiment_groups, experiment_groups, standalone_campaign_groups
from live_run import LiveRunError, PlacementJudge, _ops, plan, select_candidates, target_duration_dt
from maximal_experiments import (
    build_spectator_wavefront_circuits,
    concurrent_shor_mod15_group,
    core_x_duration_dt,
    maximal_groups,
    spectator_wavefront_ramsey_group,
)
from runtime_contracts import _fake_snapshot, _fixture_args, _ProbeBackend, _ProbeService


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _math_close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def _verify_spectator_wavefront_circuits() -> None:
    spectator_count = 5
    delay_dt = 2500
    qc_active, qc_control, qc_null = build_spectator_wavefront_circuits(spectator_count, delay_dt)

    total_qubits = 1 + spectator_count
    _require(qc_active.num_qubits == total_qubits, "active qubit count mismatch")
    _require(qc_active.num_clbits == total_qubits, "active clbit count mismatch")
    _require(qc_control.num_qubits == total_qubits, "control qubit count mismatch")
    _require(qc_control.num_clbits == total_qubits, "control clbit count mismatch")
    _require(qc_null.num_qubits == total_qubits, "null qubit count mismatch")
    _require(qc_null.num_clbits == total_qubits, "null clbit count mismatch")

    # Active and control circuits are purely static with connected line topology
    for qc, name in ((qc_active, "active"), (qc_control, "control")):
        ops = qc.count_ops()
        _require("barrier" in ops, f"{name} must have barriers")
        _require("delay" in ops, f"{name} must have delays")
        _require("measure" in ops, f"{name} must have terminal measures")
        _require("cz" in ops, f"{name} must have native cz gauge pairs")
        _require("if_else" not in ops, f"{name} must not contain dynamic control flow")
        _require("reset" not in ops, f"{name} must not contain reset")

        base_ops = set(_ops(qc))
        used, edges = packing.pattern(base_ops)
        _require(used == list(range(total_qubits)), f"{name} used qubits must be 0..{total_qubits - 1}")
        _require(len(edges) == total_qubits - 1, f"{name} must have {total_qubits - 1} edges for line topology")
        expected_edges = {(i, i + 1) for i in range(total_qubits - 1)}
        _require(edges == expected_edges, f"{name} edges must form connected line graph")

    # Readout null is a bare ground-state measurement free of gauge operations
    null_ops = qc_null.count_ops()
    _require(dict(null_ops) == {"measure": total_qubits}, "null circuit must contain only terminal measurements")

    # Verify core_x_duration_dt helper
    backend = FakeKingston()
    _require(core_x_duration_dt(None) == 8, "default x_duration_dt must be 8")
    _require(core_x_duration_dt(backend.target, 0) == 8, "FakeKingston qubit 0 x_duration_dt must be 8")

    # Verify scheduled duration matching when derived dynamically from target
    group_cal = spectator_wavefront_ramsey_group(spectator_count=2, delay_dt=4000, target=backend.target, core_qubit=0)
    qc_act = group_cal.members[0].circuit
    qc_ctrl = group_cal.members[1].circuit
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        t_act = transpile(qc_act, backend, scheduling_method="asap")
        t_ctrl = transpile(qc_ctrl, backend, scheduling_method="asap")
        _require(
            t_act.duration == t_ctrl.duration,
            f"active duration ({t_act.duration}) must match control duration ({t_ctrl.duration})",
        )

    # Test non-default target single-qubit duration (e.g. 16 dt at 4 ns dt)
    target_mod = copy.deepcopy(backend.target)
    for q in range(target_mod.num_qubits):
        if (q,) in target_mod["x"]:
            target_mod["x"][(q,)].duration = 6.4e-8
    derived_mod_dt = core_x_duration_dt(target_mod, 0)
    _require(derived_mod_dt == 16, f"expected 16 dt on modified target, got {derived_mod_dt}")
    group_mod = spectator_wavefront_ramsey_group(spectator_count=2, delay_dt=4000, target=target_mod, core_qubit=0)
    qc_act_mod = group_mod.members[0].circuit
    qc_ctrl_mod = group_mod.members[1].circuit
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        t_act_mod = transpile(qc_act_mod, target=target_mod, scheduling_method="asap")
        t_ctrl_mod = transpile(qc_ctrl_mod, target=target_mod, scheduling_method="asap")
        _require(
            t_act_mod.duration == t_ctrl_mod.duration,
            f"modified target active duration ({t_act_mod.duration}) must match control ({t_ctrl_mod.duration})",
        )


def _verify_spectator_wavefront_summary_and_simulation() -> None:
    group = spectator_wavefront_ramsey_group(spectator_count=4, delay_dt=1000)
    _require(group.name == "spectator_wavefront_ramsey", "group name mismatch")
    _require(len(group.members) == 3, "group must have 3 members")

    # Rate keys must be actual probabilities, not unbounded contrasts or differences
    _require(
        "delta_contrast" not in group.rate_keys,
        "delta_contrast is a contrast difference, not a Bernoulli rate key",
    )
    _require(
        "contrast_active" not in group.rate_keys,
        "contrast_active is a transformed contrast, not a Bernoulli rate key",
    )

    # Check that all rate keys exist in summary
    ideals = {member.name: member.ideal for member in group.members}
    summary = group.summarize(ideals)
    for rate_key in group.rate_keys:
        _require(rate_key in summary, f"rate key {rate_key} missing from summary")
        _require(0.0 <= summary[rate_key] <= 1.0, f"rate key {rate_key} must be in [0, 1]")

    # Ideal noiseless values:
    _require(_math_close(summary["spectator_p0_active"], 1.0), "ideal spectator_p0_active must be 1.0")
    _require(_math_close(summary["spectator_p0_control"], 1.0), "ideal spectator_p0_control must be 1.0")
    _require(_math_close(summary["contrast_active"], 1.0), "ideal contrast_active must be 1.0")
    _require(_math_close(summary["contrast_control"], 1.0), "ideal contrast_control must be 1.0")
    _require(_math_close(summary["delta_contrast"], 0.0), "ideal delta_contrast must be 0.0")

    # Aer simulation
    sim = AerSimulator()
    sim_dists: dict[str, np.ndarray] = {}
    for member in group.members:
        res = sim.run(member.circuit, shots=4096, seed_simulator=20261011).result()
        counts = res.get_counts()
        total = sum(counts.values())
        dist = np.zeros(len(member.ideal), dtype=float)
        for bitstring, count in counts.items():
            dist[int(bitstring, 2)] = count / total
        sim_dists[member.name] = dist

    sim_summary = group.summarize(sim_dists)
    _require(sim_summary["spectator_p0_active"] > 0.95, "noiseless active spectator p0 must exceed 0.95")
    _require(sim_summary["spectator_p0_control"] > 0.95, "noiseless control spectator p0 must exceed 0.95")
    _require(abs(sim_summary["delta_contrast"]) < 0.05, "noiseless delta contrast must be near zero")


def _verify_concurrent_shor_group() -> None:
    phase_bits = 4
    outcomes = 1 << phase_bits
    group = concurrent_shor_mod15_group(replica_floor=0.75, phase_bits=phase_bits)
    _require(group.name == "concurrent_shor_mod15", "group name mismatch")
    _require(len(group.members) == 2, "group must have 2 members")
    _require(group.replica_floor == 0.75, "replica floor mismatch")

    # Rate keys must not contain differences or margins
    _require(
        "factorable_margin_over_null" not in group.rate_keys,
        "factorable_margin_over_null is a difference, not a Bernoulli rate key",
    )

    # Check rate keys
    ideals = {member.name: member.ideal for member in group.members}
    summary = group.summarize(ideals)
    for rate_key in group.rate_keys:
        _require(rate_key in summary, f"rate key {rate_key} missing from summary")
        _require(0.0 <= summary[rate_key] <= 1.0, f"rate key {rate_key} must be in [0, 1]")

    # In ideal distributions:
    # Primary has factorable probability = 0.50
    # Null has factorable probability = 0.0, null_p0 = 1.0
    # Uniform null has factorable probability = 0.375
    _require(_math_close(summary["factorable_probability"], 0.50), "ideal factorable probability must be 0.50")
    _require(
        _math_close(summary["identity_null_factorable_probability"], 0.0),
        "ideal null factorable probability must be 0.0",
    )
    _require(_math_close(summary["factorable_margin_over_null"], 0.50), "ideal margin over null must be 0.50")
    _require(
        _math_close(summary["uniform_null_factorable_probability"], 0.375),
        "uniform null factorable probability must be 0.375 for 4 phase bits",
    )
    _require(_math_close(summary["identity_null_p0"], 1.0), "ideal identity_null_p0 must be 1.0")
    _require(_math_close(summary["tvd_to_ideal"], 0.0), "ideal tvd must be 0.0")

    # Aer simulation
    sim = AerSimulator()
    sim_dists: dict[str, np.ndarray] = {}
    for member in group.members:
        res = sim.run(member.circuit, shots=10000, seed_simulator=20261011).result()
        counts = res.get_counts()
        total = sum(counts.values())
        dist = np.zeros(outcomes, dtype=float)
        for bitstring, count in counts.items():
            dist[int(bitstring, 2)] = count / total
        sim_dists[member.name] = dist

    sim_summary = group.summarize(sim_dists)
    _require(
        abs(sim_summary["factorable_probability"] - 0.50) < 0.03,
        "simulated factorable probability must be near 0.50",
    )
    _require(
        sim_summary["identity_null_factorable_probability"] == 0.0,
        "simulated identity null factorable probability must be 0.0",
    )
    _require(sim_summary["identity_null_p0"] == 1.0, "simulated identity null p0 must be 1.0")

    # Admission check on valid simulation
    admission = group.admission
    _require(admission is not None, "admission check must be defined")
    if admission is None:
        raise RuntimeError("unreachable")
    admit_result = admission([sim_summary], 10000)
    _require(admit_result["admitted"] is True, "noiseless simulation must pass admission")

    # Admission check on uniform random noise: MUST FAIL admission!
    uniform_summary = group.summarize(
        {
            "shor_mod15_a2": np.full(outcomes, 1.0 / outcomes),
            "shor_mod15_a2_null": np.zeros(outcomes),
        }
    )
    noise_admit = admission([uniform_summary], 10000)
    _require(
        noise_admit["admitted"] is False,
        "uniform random noise must fail statistical admission",
    )


def _verify_maximal_groups() -> None:
    groups = maximal_groups()
    _require(len(groups) == 2, "maximal_groups must return 2 groups")
    names = {g.name for g in groups}
    _require("spectator_wavefront_ramsey" in names, "missing spectator_wavefront_ramsey group")
    _require("concurrent_shor_mod15" in names, "missing concurrent_shor_mod15 group")


def _verify_isolation_contract() -> None:
    all_names = {g.name for g in all_experiment_groups()}
    default_names = {g.name for g in experiment_groups()}
    standalone_names = {g.name for g in standalone_campaign_groups()}

    _require(
        "spectator_wavefront_ramsey" in all_names,
        "all_experiment_groups must contain spectator_wavefront_ramsey",
    )
    _require(
        "spectator_wavefront_ramsey" not in default_names,
        "default experiment_groups must NOT contain spectator_wavefront_ramsey",
    )
    _require(
        "spectator_wavefront_ramsey" in standalone_names,
        "standalone_campaign_groups must contain spectator_wavefront_ramsey",
    )
    _require(
        "concurrent_shor_mod15" in default_names,
        "default experiment_groups must contain concurrent_shor_mod15",
    )

    # Verify select_candidates on spectator_wavefront_ramsey produces duration-matched ISAs
    backend = FakeKingston()
    snap = _fake_snapshot(backend)
    group = spectator_wavefront_ramsey_group(spectator_count=3, delay_dt=3000)
    log: dict[str, Any] = {}
    candidates = select_candidates(group, [snap], seeds=1, log=log)
    _require(
        len(candidates) > 0,
        "select_candidates must produce at least one candidate for spectator_wavefront_ramsey",
    )
    best = candidates[0]
    dur_act = target_duration_dt(best.isas[0], backend.target)
    dur_ctrl = target_duration_dt(best.isas[1], backend.target)
    _require(
        dur_act == dur_ctrl,
        f"candidate ISAs must have identical duration: active={dur_act} ctrl={dur_ctrl}",
    )
    # The calibration-aware rebuild keeps the group's requested 3000-dt Ramsey delay.
    ctrl_delay = next(
        int(instruction.operation.duration)
        for instruction in best.isas[1].data
        if instruction.operation.name == "delay"
    )
    _require(
        ctrl_delay == 3000,
        f"candidate ISA delay must preserve requested 3000 dt, got {ctrl_delay}",
    )

    # Replica placement rejects a core whose X duration differs from the routed core's.
    target_x_mod = copy.deepcopy(backend.target)
    for q in range(target_x_mod.num_qubits):
        if (q,) in target_x_mod["x"]:
            target_x_mod["x"][(q,)].duration = 6.4e-8  # 16 dt
    judge_mismatch = PlacementJudge(
        tuple(best.isas),
        target_x_mod,
        frozenset(),
        frozenset(),
        matched_x_duration=(best.layout[0], 8),
    )
    # Mapping best.layout[0] to physical qubit 0 (which has 16 dt in target_x_mod != expected 8 dt) must be rejected
    mismatch_mapping = {best.layout[0]: 0}
    _require(
        judge_mismatch(mismatch_mapping) is None,
        "PlacementJudge must reject replica mapping when core X duration differs from layout[0]",
    )
    # Mapping with matching expected duration (16 dt) passes core duration check
    judge_matched = PlacementJudge(
        tuple(best.isas),
        target_x_mod,
        frozenset(),
        frozenset(),
        matched_x_duration=(best.layout[0], 16),
    )
    _require(
        judge_matched.matched_x_duration == (best.layout[0], 16),
        "PlacementJudge matched_x_duration must be retained",
    )

    # Verify plan rejects co-running spectator_wavefront_ramsey with other groups
    probe_backend = _ProbeBackend("viable", backend)
    service = _ProbeService([probe_backend])
    try:
        plan(
            service,
            _fixture_args(groups=["spectator_wavefront_ramsey", "concurrent_shor_mod15"]),
        )
        raise RuntimeError("plan must reject co-running spectator_wavefront_ramsey with other groups")
    except LiveRunError as err:
        _require(
            "isolated campaign" in str(err),
            f"unexpected error message: {err}",
        )


if __name__ == "__main__":
    _verify_spectator_wavefront_circuits()
    _verify_spectator_wavefront_summary_and_simulation()
    _verify_concurrent_shor_group()
    _verify_maximal_groups()
    _verify_isolation_contract()
    print("maximal contracts: spectator wavefront, idle control, concurrent Shor, and admission pass")
