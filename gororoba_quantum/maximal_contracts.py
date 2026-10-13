"""Executable contracts and property tests for maximal-scale experiments."""

from __future__ import annotations

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKingston

import packing
from live_run import _ops
from maximal_experiments import (
    build_spectator_wavefront_circuits,
    concurrent_shor_mod15_group,
    maximal_groups,
    spectator_wavefront_ramsey_group,
)


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

    # All circuits are purely static: no mid-circuit measurement, no dynamic control flow
    for qc, name in ((qc_active, "active"), (qc_control, "control"), (qc_null, "null")):
        ops = qc.count_ops()
        _require("barrier" in ops, f"{name} must have barriers")
        _require("delay" in ops, f"{name} must have delays")
        _require("measure" in ops, f"{name} must have terminal measures")
        _require("cz" in ops, f"{name} must have native cz gauge pairs")
        _require("if_else" not in ops, f"{name} must not contain dynamic control flow")
        _require("reset" not in ops, f"{name} must not contain reset")

    # Verify connected line pattern: packing.pattern must find zero isolated nodes
    for qc, name in ((qc_active, "active"), (qc_control, "control"), (qc_null, "null")):
        base_ops = set(_ops(qc))
        used, edges = packing.pattern(base_ops)
        _require(used == list(range(total_qubits)), f"{name} used qubits must be 0..{total_qubits - 1}")
        _require(len(edges) == total_qubits - 1, f"{name} must have {total_qubits - 1} edges for line topology")
        expected_edges = {(i, i + 1) for i in range(total_qubits - 1)}
        _require(edges == expected_edges, f"{name} edges must form connected line graph")

    # Verify scheduled duration matching between active and control arms
    backend = FakeKingston()
    x_dur_s = backend.target["x"][(0,)].duration
    x_dur_dt = int(round(x_dur_s / backend.target.dt))
    qc_act, qc_ctrl, _ = build_spectator_wavefront_circuits(
        spectator_count=2,
        delay_dt=4000,
        x_duration_dt=x_dur_dt,
    )
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        t_act = transpile(qc_act, backend, scheduling_method="asap")
        t_ctrl = transpile(qc_ctrl, backend, scheduling_method="asap")
        _require(
            t_act.duration == t_ctrl.duration,
            f"active duration ({t_act.duration}) must match control duration ({t_ctrl.duration})",
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


if __name__ == "__main__":
    _verify_spectator_wavefront_circuits()
    _verify_spectator_wavefront_summary_and_simulation()
    _verify_concurrent_shor_group()
    _verify_maximal_groups()
    print("maximal contracts: spectator wavefront, idle control, concurrent Shor, and admission pass")
