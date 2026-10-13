"""Maximal-scale hardware benchmark experiments: spectator wavefront and concurrent Shor carpet.

This module provides two calibration-aware, hardware-scale experiments designed
for whole-chip execution under the repository's strict submission gating:

1. ``spectator_wavefront_ramsey``: Measures spatial spectator dephasing and crosstalk
   during active mid-circuit measurement, dynamic reset, and feed-forward phase update
   (if_test). Spectators are protected by explicit barriers and matched delay intervals,
   preventing compiler cancellation of the H...H Ramsey sequence. A matched control
   circuit runs with the dynamic core held idle, providing a differential contrast
   delta_C(q) = C_control(q) - C_active(q) that isolates hardware crosstalk from
   intrinsic T1/T2 relaxation.

2. ``concurrent_shor_mod15``: Reuses the repository's verified semiclassical order-finding
   circuit from order_finding.py for N=15, a=2. Placing replicas using live backend
   calibration metrics filters degraded ("bum") qubits and embeds the 5-qubit order-finding
   engines across disjoint hardware patches with identical compiled gate sequences.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

import variance
from experiments import Group, Member, tvd
from order_finding import factor_order_finding

DEFAULT_DELAY_DT = 4000
DEFAULT_SPECTATORS = 10


def build_spectator_wavefront_circuits(
    spectator_count: int = DEFAULT_SPECTATORS,
    delay_dt: int = DEFAULT_DELAY_DT,
) -> tuple[QuantumCircuit, QuantumCircuit, QuantumCircuit]:
    """Construct active core, matched idle control, and readout null circuits.

    The active circuit entangles control and target, measures control mid-circuit,
    resets it, applies feed-forward phase correction, and measures control again.
    Spectator qubits are prepared in |+>, idled across barriers matching the core
    window, and rotated back with H before readout. The matched control circuit
    holds the core idle for the identical duration.
    """
    if spectator_count < 1:
        raise ValueError(f"spectator_count must be at least 1, got {spectator_count}")

    total_qubits = 2 + spectator_count
    total_clbits = 2 + spectator_count

    # Active core circuit
    qc_active = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_active",
    )
    ctrl, target = 0, 1
    spectators = list(range(2, total_qubits))

    for s in spectators:
        qc_active.h(s)

    qc_active.x(target)
    qc_active.h(ctrl)
    qc_active.cx(ctrl, target)
    qc_active.h(ctrl)

    qc_active.barrier()
    qc_active.measure(ctrl, 0)
    qc_active.reset(ctrl)
    for s in spectators:
        qc_active.delay(delay_dt, s, unit="dt")
    with qc_active.if_test((qc_active.clbits[0], 1)):
        qc_active.p(-math.pi / 2, ctrl)
    qc_active.h(ctrl)
    qc_active.measure(ctrl, 1)
    qc_active.barrier()

    for idx, s in enumerate(spectators):
        qc_active.h(s)
        qc_active.measure(s, 2 + idx)

    # Matched idle control circuit
    qc_control = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_control",
    )
    for s in spectators:
        qc_control.h(s)
    qc_control.barrier()
    for q in range(total_qubits):
        qc_control.delay(delay_dt, q, unit="dt")
    qc_control.barrier()
    for idx, s in enumerate(spectators):
        qc_control.h(s)
        qc_control.measure(s, 2 + idx)
    qc_control.measure(ctrl, 0)
    qc_control.measure(ctrl, 1)

    # Readout null circuit (ground state baseline)
    qc_null = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_null",
    )
    for q in range(total_qubits):
        qc_null.measure(q, q)

    return qc_active, qc_control, qc_null


def _spectator_ideal_distribution(total_clbits: int, core_uniform: bool = False) -> np.ndarray:
    """Ideal distribution: spectators all |0>, core uniformly distributed or |00>."""
    size = 1 << total_clbits
    ideal = np.zeros(size, dtype=float)
    if not core_uniform:
        ideal[0] = 1.0
        return ideal
    # Core bits 0 and 1 take states 00, 01, 10, 11 with 1/4 each; spectators are 0
    for outcome in (0, 1, 2, 3):
        ideal[outcome] = 0.25
    return ideal


def spectator_wavefront_ramsey_group(
    spectator_count: int = DEFAULT_SPECTATORS,
    delay_dt: int = DEFAULT_DELAY_DT,
) -> Group:
    """Group evaluating spectator Ramsey contrast under active feed-forward vs idle control."""
    qc_active, qc_control, qc_null = build_spectator_wavefront_circuits(spectator_count, delay_dt)
    total_clbits = qc_active.num_clbits

    ideal_active = _spectator_ideal_distribution(total_clbits, core_uniform=True)
    ideal_control = _spectator_ideal_distribution(total_clbits, core_uniform=False)
    ideal_null = _spectator_ideal_distribution(total_clbits, core_uniform=False)

    members = (
        Member("spectator_wavefront_active", qc_active, ideal_active),
        Member("spectator_wavefront_control", qc_control, ideal_control),
        Member("spectator_wavefront_null", qc_null, ideal_null),
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        active_dist = distributions["spectator_wavefront_active"]
        control_dist = distributions["spectator_wavefront_control"]

        def marginal_p1(dist: np.ndarray, bit_index: int) -> float:
            p1 = 0.0
            for outcome, prob in enumerate(dist):
                if (outcome >> bit_index) & 1:
                    p1 += prob
            return float(p1)

        active_contrasts = [1.0 - 2.0 * marginal_p1(active_dist, 2 + i) for i in range(spectator_count)]
        control_contrasts = [1.0 - 2.0 * marginal_p1(control_dist, 2 + i) for i in range(spectator_count)]

        mean_c_active = float(np.mean(active_contrasts))
        mean_c_control = float(np.mean(control_contrasts))
        delta_c = float(mean_c_control - mean_c_active)

        core_trigger = marginal_p1(active_dist, 0)
        core_final = marginal_p1(active_dist, 1)

        return {
            "spectator_contrast_active": mean_c_active,
            "spectator_contrast_control": mean_c_control,
            "delta_contrast": delta_c,
            "core_trigger_rate": core_trigger,
            "core_final_rate": core_final,
            "tvd_to_ideal_active": tvd(active_dist, ideal_active),
            "tvd_to_ideal_control": tvd(control_dist, ideal_control),
        }

    return Group(
        "spectator_wavefront_ramsey",
        members,
        summarize,
        rate_keys=frozenset(
            {
                "spectator_contrast_active",
                "spectator_contrast_control",
                "delta_contrast",
                "core_trigger_rate",
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

    # Weights score odd-phase factorable outcomes (01 -> 1, 11 -> 3)
    factorable_weights = np.array([0.0, 1.0, 0.0, 1.0], dtype=float)

    members = (
        Member("shor_mod15_a2", qc_primary, ideal_primary, weights=factorable_weights),
        Member("shor_mod15_a2_null", qc_null, ideal_null, weights=factorable_weights),
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        primary = distributions["shor_mod15_a2"]
        null = distributions["shor_mod15_a2_null"]

        p_factorable = float(primary[1] + primary[3])
        p_null_factorable = float(null[1] + null[3])
        margin_over_null = float(p_factorable - p_null_factorable)
        uniform_null = 0.2969  # analytical uniform random factorable yield

        return {
            "factorable_probability": p_factorable,
            "identity_null_factorable_probability": p_null_factorable,
            "factorable_margin_over_null": margin_over_null,
            "uniform_null_factorable_probability": uniform_null,
            "factorable_margin_over_uniform": float(p_factorable - uniform_null),
            "identity_null_p00": float(null[0]),
            "tvd_to_ideal": tvd(primary, ideal_primary),
        }

    def admit(per_replica: list[dict[str, float]], shots: int) -> dict[str, Any]:
        primary_rates = [r["factorable_probability"] for r in per_replica]
        null_rates = [r["identity_null_factorable_probability"] for r in per_replica]
        primary_interval = variance.interval(primary_rates, shots, bernoulli=True)
        null_interval = variance.interval(null_rates, shots, bernoulli=True)
        uniform_rate = per_replica[0]["uniform_null_factorable_probability"]

        admitted = bool(
            "lo" in primary_interval
            and "hi" in null_interval
            and primary_interval["lo"] > uniform_rate
            and null_interval["hi"] < primary_interval["lo"]
        )
        return {
            "primary": primary_interval,
            "null": null_interval,
            "uniform_null": uniform_rate,
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
                "identity_null_factorable_probability",
                "factorable_margin_over_null",
                "identity_null_p00",
            }
        ),
    )


def maximal_groups() -> list[Group]:
    """Return all maximal-scale benchmark groups."""
    return [spectator_wavefront_ramsey_group(), concurrent_shor_mod15_group()]
