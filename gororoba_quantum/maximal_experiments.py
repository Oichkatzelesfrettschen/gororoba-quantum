"""Maximal-scale hardware benchmark experiments: spectator wavefront and concurrent Shor carpet.

This module provides two calibration-aware, hardware-scale experiments designed
for whole-chip execution under the repository's strict submission gating:

1. ``spectator_wavefront_ramsey``: Measures spatial spectator dephasing and crosstalk
   along a connected line graph of physical qubits during active core driving.
   Spectators are protected by explicit barriers and matched delay intervals,
   preventing compiler cancellation of the H...H Ramsey sequence. A matched control
   circuit runs with the driving core held idle for the identical duration, providing
   a differential contrast delta_C = C_control - C_active that isolates hardware
   crosstalk from intrinsic T1/T2 relaxation.

2. ``concurrent_shor_mod15``: Reuses the repository's verified semiclassical order-finding
   circuit from order_finding.py for N=15, a=2 with 2 phase bits. Placing replicas
   using live backend calibration metrics filters degraded ("bum") qubits and embeds
   the order-finding engines across disjoint hardware patches with identical compiled
   gate sequences.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

import variance
from experiments import Group, Member, tvd
from factoring import distribution_success
from order_finding import factor_order_finding

DEFAULT_DELAY_DT = 4000
DEFAULT_SPECTATORS = 5


def build_spectator_wavefront_circuits(
    spectator_count: int = DEFAULT_SPECTATORS,
    delay_dt: int = DEFAULT_DELAY_DT,
) -> tuple[QuantumCircuit, QuantumCircuit, QuantumCircuit]:
    """Construct active core, matched idle control, and readout null circuits.

    All circuits enforce a connected linear topology via native CZ identity pairs
    (CZ-barrier-CZ) between adjacent qubits along the line 0-1-2-...-(N-1). This
    guarantees VF2 finds physical nearest-neighbor line embeddings without isolated-node
    combinatorial search.

    The active circuit drives core qubit 0 while spectators 1..N-1 idle in |+>.
    The matched control circuit holds core qubit 0 idle for the identical duration.
    The null circuit measures the ground state readout baseline.
    All three circuits are purely static and share identical timing envelopes.
    """
    if spectator_count < 1:
        raise ValueError(f"spectator_count must be at least 1, got {spectator_count}")

    total_qubits = 1 + spectator_count
    total_clbits = total_qubits

    # 1. Active core circuit
    qc_active = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_active",
    )
    # Native connected topology gauge along line 0-1-...-(N-1)
    for i in range(total_qubits - 1):
        qc_active.cz(i, i + 1)
        qc_active.barrier()
        qc_active.cz(i, i + 1)
        qc_active.barrier()

    # Ramsey preparation
    for s in range(1, total_qubits):
        qc_active.h(s)
    qc_active.barrier()

    # Ramsey exposure: core driving while spectators idle in superposition
    half_dt = delay_dt // 2
    rem_dt = delay_dt - half_dt
    qc_active.delay(half_dt, 0, unit="dt")
    qc_active.x(0)
    qc_active.delay(rem_dt, 0, unit="dt")
    qc_active.x(0)
    for s in range(1, total_qubits):
        qc_active.delay(delay_dt, s, unit="dt")
    qc_active.barrier()

    # Ramsey readout
    for s in range(1, total_qubits):
        qc_active.h(s)
    for q in range(total_qubits):
        qc_active.measure(q, q)

    # 2. Matched idle control circuit
    qc_control = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_control",
    )
    for i in range(total_qubits - 1):
        qc_control.cz(i, i + 1)
        qc_control.barrier()
        qc_control.cz(i, i + 1)
        qc_control.barrier()

    for s in range(1, total_qubits):
        qc_control.h(s)
    qc_control.barrier()

    # Matched exposure: core is idle for identical delay_dt duration
    for q in range(total_qubits):
        qc_control.delay(delay_dt, q, unit="dt")
    qc_control.barrier()

    for s in range(1, total_qubits):
        qc_control.h(s)
    for q in range(total_qubits):
        qc_control.measure(q, q)

    # 3. Readout null circuit (ground state baseline)
    qc_null = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_null",
    )
    for i in range(total_qubits - 1):
        qc_null.cz(i, i + 1)
        qc_null.barrier()
        qc_null.cz(i, i + 1)
        qc_null.barrier()

    for q in range(total_qubits):
        qc_null.delay(delay_dt, q, unit="dt")
    qc_null.barrier()

    for q in range(total_qubits):
        qc_null.measure(q, q)

    return qc_active, qc_control, qc_null


def _ground_ideal_distribution(total_clbits: int) -> np.ndarray:
    """Ideal distribution: all qubits measure 0 with probability 1.0."""
    size = 1 << total_clbits
    ideal = np.zeros(size, dtype=float)
    ideal[0] = 1.0
    return ideal


def spectator_wavefront_ramsey_group(
    spectator_count: int = DEFAULT_SPECTATORS,
    delay_dt: int = DEFAULT_DELAY_DT,
) -> Group:
    """Group evaluating spectator Ramsey contrast under active drive vs idle control."""
    qc_active, qc_control, qc_null = build_spectator_wavefront_circuits(spectator_count, delay_dt)
    total_clbits = qc_active.num_clbits

    ideal_active = _ground_ideal_distribution(total_clbits)
    ideal_control = _ground_ideal_distribution(total_clbits)
    ideal_null = _ground_ideal_distribution(total_clbits)

    members = (
        Member("spectator_wavefront_active", qc_active, ideal_active),
        Member("spectator_wavefront_control", qc_control, ideal_control),
        Member("spectator_wavefront_null", qc_null, ideal_null),
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        active_dist = distributions["spectator_wavefront_active"]
        control_dist = distributions["spectator_wavefront_control"]
        null_dist = distributions["spectator_wavefront_null"]

        def marginal_p0(dist: np.ndarray, bit_index: int) -> float:
            p0 = 0.0
            for outcome, prob in enumerate(dist):
                if not ((outcome >> bit_index) & 1):
                    p0 += prob
            return float(p0)

        active_spectator_p0s = [marginal_p0(active_dist, s) for s in range(1, 1 + spectator_count)]
        control_spectator_p0s = [marginal_p0(control_dist, s) for s in range(1, 1 + spectator_count)]
        null_spectator_p0s = [marginal_p0(null_dist, s) for s in range(1, 1 + spectator_count)]

        mean_p0_active = float(np.mean(active_spectator_p0s))
        mean_p0_control = float(np.mean(control_spectator_p0s))
        mean_p0_null = float(np.mean(null_spectator_p0s))
        core_p0_active = marginal_p0(active_dist, 0)

        contrast_active = 2.0 * mean_p0_active - 1.0
        contrast_control = 2.0 * mean_p0_control - 1.0
        delta_contrast = contrast_control - contrast_active

        metrics: dict[str, float] = {
            "spectator_p0_active": mean_p0_active,
            "spectator_p0_control": mean_p0_control,
            "null_p0": mean_p0_null,
            "core_p0_active": core_p0_active,
            "contrast_active": float(contrast_active),
            "contrast_control": float(contrast_control),
            "delta_contrast": float(delta_contrast),
            "tvd_to_ideal_active": tvd(active_dist, ideal_active),
            "tvd_to_ideal_control": tvd(control_dist, ideal_control),
        }
        for idx in range(spectator_count):
            dist_step = idx + 1
            c_act = 2.0 * active_spectator_p0s[idx] - 1.0
            c_ctrl = 2.0 * control_spectator_p0s[idx] - 1.0
            metrics[f"delta_contrast_dist_{dist_step}"] = float(c_ctrl - c_act)

        return metrics

    return Group(
        "spectator_wavefront_ramsey",
        members,
        summarize,
        rate_keys=frozenset(
            {
                "spectator_p0_active",
                "spectator_p0_control",
                "null_p0",
                "core_p0_active",
            }
        ),
    )


def concurrent_shor_mod15_group(replica_floor: float = 0.75) -> Group:
    """Group evaluating concurrent semiclassical order finding for N=15, a=2.

    Reuses verified order-finding logic with 2 phase bits. Odd-phase outcomes (01, 11)
    recover non-trivial factors 3 and 5 of 15. The replica floor filters degraded
    qubits while placing disjoint instances across the physical device.
    """
    modulus, base, phase_bits = 15, 2, 2
    qc_primary = factor_order_finding(modulus, base, phase_bits)
    qc_null = factor_order_finding(modulus, base, phase_bits, identity=True)

    ideal_primary = np.full(4, 0.25, dtype=float)
    ideal_null = np.zeros(4, dtype=float)
    ideal_null[0] = 1.0

    factorable_weights = np.array([0.0, 1.0, 0.0, 1.0], dtype=float)

    uniform_baseline = distribution_success([0.25] * 4, phase_bits, modulus, base)
    uniform_factorable_rate = uniform_baseline["factorable_probability"]
    uniform_order_rate = uniform_baseline["order_recovery_probability"]

    members = (
        Member("shor_mod15_a2", qc_primary, ideal_primary, weights=factorable_weights),
        Member("shor_mod15_a2_null", qc_null, ideal_null, weights=factorable_weights),
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        primary = distributions["shor_mod15_a2"]
        null = distributions["shor_mod15_a2_null"]

        primary_success = distribution_success(primary, phase_bits, modulus, base)
        null_success = distribution_success(null, phase_bits, modulus, base)

        p_factorable = primary_success["factorable_probability"]
        p_order = primary_success["order_recovery_probability"]
        p_null_factorable = null_success["factorable_probability"]
        p_null_order = null_success["order_recovery_probability"]

        return {
            "factorable_probability": p_factorable,
            "order_recovery_probability": p_order,
            "identity_null_factorable_probability": p_null_factorable,
            "identity_null_order_recovery_probability": p_null_order,
            "factorable_margin_over_null": float(p_factorable - p_null_factorable),
            "order_recovery_margin_over_null": float(p_order - p_null_order),
            "uniform_null_factorable_probability": uniform_factorable_rate,
            "uniform_null_order_recovery_probability": uniform_order_rate,
            "identity_null_p00": float(null[0]),
            "tvd_to_ideal": tvd(primary, ideal_primary),
        }

    def admit(per_replica: list[dict[str, float]], shots: int) -> dict[str, Any]:
        primary_rates = [r["factorable_probability"] for r in per_replica]
        null_rates = [r["identity_null_factorable_probability"] for r in per_replica]
        primary_interval = variance.interval(primary_rates, shots, bernoulli=True)
        null_interval = variance.interval(null_rates, shots, bernoulli=True)

        admitted = bool(
            "lo" in primary_interval
            and "hi" in null_interval
            and null_interval["hi"] < primary_interval["lo"]
            and primary_interval["lo"] >= 0.20
        )
        return {
            "primary": primary_interval,
            "null": null_interval,
            "uniform_null": uniform_factorable_rate,
            "admitted": admitted,
        }

    return Group(
        "concurrent_shor_mod15",
        members,
        summarize,
        admission=admit,
        replica_floor=replica_floor,
        rate_keys=frozenset(
            {
                "factorable_probability",
                "order_recovery_probability",
                "identity_null_factorable_probability",
                "identity_null_order_recovery_probability",
                "identity_null_p00",
            }
        ),
    )


def maximal_groups() -> list[Group]:
    """Return all maximal-scale benchmark groups."""
    return [spectator_wavefront_ramsey_group(), concurrent_shor_mod15_group()]
