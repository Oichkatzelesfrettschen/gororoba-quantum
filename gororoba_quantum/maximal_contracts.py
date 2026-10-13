"""Executable contracts and property tests for maximal-scale experiments."""

from __future__ import annotations

import numpy as np
from qiskit_aer import AerSimulator

from maximal_experiments import (
    build_spectator_wavefront_circuits,
    concurrent_shor_mod15_group,
    maximal_groups,
    spectator_wavefront_ramsey_group,
)


def _verify_spectator_wavefront_circuits() -> None:
    spectator_count = 6
    delay_dt = 2500
    qc_active, qc_control, qc_null = build_spectator_wavefront_circuits(spectator_count, delay_dt)

    assert qc_active.num_qubits == 2 + spectator_count
    assert qc_active.num_clbits == 2 + spectator_count
    assert qc_control.num_qubits == 2 + spectator_count
    assert qc_control.num_clbits == 2 + spectator_count
    assert qc_null.num_qubits == 2 + spectator_count
    assert qc_null.num_clbits == 2 + spectator_count

    active_ops = qc_active.count_ops()
    assert "barrier" in active_ops
    assert "delay" in active_ops
    assert "if_else" in active_ops
    assert "reset" in active_ops
    assert "measure" in active_ops

    control_ops = qc_control.count_ops()
    assert "barrier" in control_ops
    assert "delay" in control_ops
    assert "measure" in control_ops
    assert "if_else" not in control_ops  # core is silent/idle in control


def _verify_spectator_wavefront_summary_and_simulation() -> None:
    group = spectator_wavefront_ramsey_group(spectator_count=4, delay_dt=1000)
    assert group.name == "spectator_wavefront_ramsey"
    assert len(group.members) == 3

    # Check that rate keys are a subset of summary keys
    ideals = {member.name: member.ideal for member in group.members}
    summary = group.summarize(ideals)
    for rate_key in group.rate_keys:
        assert rate_key in summary, f"rate key {rate_key} missing from summary"

    # In ideal noiseless distributions:
    # Spectator contrast is exactly 1.0 for both active and control
    assert math_close(summary["spectator_contrast_active"], 1.0)
    assert math_close(summary["spectator_contrast_control"], 1.0)
    assert math_close(summary["delta_contrast"], 0.0)
    assert math_close(summary["core_trigger_rate"], 0.5)

    # Run Aer simulation on the active and control circuits
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
    # Spectator contrast should be close to 1.0 under noiseless simulation
    assert sim_summary["spectator_contrast_active"] > 0.95
    assert sim_summary["spectator_contrast_control"] > 0.95
    assert abs(sim_summary["delta_contrast"]) < 0.05


def _verify_concurrent_shor_group() -> None:
    group = concurrent_shor_mod15_group(replica_floor=0.75)
    assert group.name == "concurrent_shor_mod15"
    assert len(group.members) == 2
    assert group.replica_floor == 0.75

    # Check rate keys
    ideals = {member.name: member.ideal for member in group.members}
    summary = group.summarize(ideals)
    for rate_key in group.rate_keys:
        assert rate_key in summary, f"rate key {rate_key} missing from summary"

    # In ideal distributions:
    # Primary has factorable probability = 0.50
    # Null has factorable probability = 0.0, null_p00 = 1.0
    assert math_close(summary["factorable_probability"], 0.50)
    assert math_close(summary["identity_null_factorable_probability"], 0.0)
    assert math_close(summary["factorable_margin_over_null"], 0.50)
    assert math_close(summary["identity_null_p00"], 1.0)
    assert math_close(summary["tvd_to_ideal"], 0.0)

    # Aer simulation
    sim = AerSimulator()
    sim_dists: dict[str, np.ndarray] = {}
    for member in group.members:
        res = sim.run(member.circuit, shots=10000, seed_simulator=20261011).result()
        counts = res.get_counts()
        total = sum(counts.values())
        dist = np.zeros(4, dtype=float)
        for bitstring, count in counts.items():
            dist[int(bitstring, 2)] = count / total
        sim_dists[member.name] = dist

    sim_summary = group.summarize(sim_dists)
    assert abs(sim_summary["factorable_probability"] - 0.50) < 0.03
    assert sim_summary["identity_null_factorable_probability"] == 0.0
    assert sim_summary["identity_null_p00"] == 1.0

    # Admission check
    assert group.admission is not None
    admit_result = group.admission([sim_summary], 10000)
    assert admit_result["admitted"] is True


def _verify_maximal_groups() -> None:
    groups = maximal_groups()
    assert len(groups) == 2
    names = {g.name for g in groups}
    assert "spectator_wavefront_ramsey" in names
    assert "concurrent_shor_mod15" in names


def math_close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


if __name__ == "__main__":
    _verify_spectator_wavefront_circuits()
    _verify_spectator_wavefront_summary_and_simulation()
    _verify_concurrent_shor_group()
    _verify_maximal_groups()
    print("maximal contracts: spectator wavefront, idle control, concurrent Shor, and admission pass")
