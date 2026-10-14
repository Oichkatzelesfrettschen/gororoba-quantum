"""Opt-in hardware campaign: spectator wavefront Ramsey.

The group is a standalone campaign (experiments.standalone_campaign_groups),
selected with --groups and planned alone:

1. ``spectator_wavefront_ramsey``: Measures spatial spectator dephasing and crosstalk
   along a connected line graph of physical qubits during active core driving.
   Spectators are protected by explicit barriers and matched delay intervals,
   preventing compiler cancellation of the H...H Ramsey sequence. A matched control
   circuit runs with the driving core held idle for the identical scheduled duration,
   accounting for physical single-qubit gate durations (x_duration_dt), providing
   a differential contrast delta_C = C_control - C_active that isolates hardware
   crosstalk from intrinsic T1/T2 relaxation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from experiments import Group, Member, tvd

DEFAULT_DELAY_DT = 4000
DEFAULT_SPECTATORS = 5
DEFAULT_X_DURATION_DT = 8


def core_x_duration_dt(target: Any, core_qubit: int = 0) -> int:
    """Derive physical single-qubit X duration in dt from a Target and physical core qubit."""
    if target is None:
        return DEFAULT_X_DURATION_DT
    dt = getattr(target, "dt", None)
    if dt is None or dt <= 0:
        return DEFAULT_X_DURATION_DT
    duration = None
    if "x" in target and (core_qubit,) in target["x"]:
        duration = target["x"][(core_qubit,)].duration
    elif "sx" in target and (core_qubit,) in target["sx"]:
        sx_dur = target["sx"][(core_qubit,)].duration
        if sx_dur is not None:
            duration = 2.0 * sx_dur
    if duration is None or duration <= 0:
        raise ValueError(f"the Target gives no X duration for qubit {core_qubit}")
    return max(1, int(round(duration / dt)))


def exposure_dt(isa: QuantumCircuit, qubit: int, target: Any) -> int:
    """Summed duration in dt of one qubit's instructions between the last two barriers.

    The exposure window of every arm sits between those barriers; the
    critical-path duration cannot see a core track shorter than the
    spectator delays, because the closing barrier pads it.
    """
    barriers = [index for index, inst in enumerate(isa.data) if inst.operation.name == "barrier"]
    if len(barriers) < 2:
        raise ValueError("the exposure window needs two closing barriers")
    total = 0.0
    for inst in isa.data[barriers[-2] + 1 : barriers[-1]]:
        if qubit not in (isa.find_bit(bit).index for bit in inst.qubits):
            continue
        if inst.operation.name == "delay":
            total += float(inst.operation.duration)
            continue
        duration = target[inst.operation.name][(qubit,)].duration
        if duration is None:
            raise ValueError(f"the Target gives no {inst.operation.name} duration for qubit {qubit}")
        total += duration / target.dt
    return int(round(total))


def build_spectator_wavefront_circuits(
    spectator_count: int = DEFAULT_SPECTATORS,
    delay_dt: int = DEFAULT_DELAY_DT,
    x_duration_dt: int = DEFAULT_X_DURATION_DT,
) -> tuple[QuantumCircuit, QuantumCircuit, QuantumCircuit]:
    """Construct active core, matched idle control, and readout null circuits.

    All circuits enforce a connected linear topology via native CZ identity pairs
    (CZ-barrier-CZ) between adjacent qubits along the line 0-1-2-...-(N-1). This
    guarantees VF2 finds physical nearest-neighbor line embeddings without isolated-node
    combinatorial search.

    The active circuit drives core qubit 0 while spectators 1..N-1 idle in |+>.
    The core driving window explicitly subtracts 2 * x_duration_dt from the core delay,
    ensuring the active core's scheduled track duration exactly equals the spectators'
    delay_dt and the control's delay_dt duration down to the dt cycle.
    The matched control circuit holds core qubit 0 idle for the identical delay_dt duration.
    The null circuit measures every qubit immediately in the ground state, so it
    is a readout baseline without a delay window; only the active and control
    Ramsey arms are static and share one scheduled timing envelope.
    """
    if spectator_count < 1:
        raise ValueError(f"spectator_count must be at least 1, got {spectator_count}")
    if delay_dt <= 2 * x_duration_dt:
        raise ValueError(f"delay_dt ({delay_dt}) must exceed 2 * x_duration_dt ({2 * x_duration_dt})")

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

    # Ramsey exposure: core driving while spectators idle in superposition.
    # Subtract 2 * x_duration_dt from core delays so the scheduled duration
    # of the core track exactly matches the spectator delay_dt duration.
    core_net_delay = delay_dt - 2 * x_duration_dt
    half_dt = core_net_delay // 2
    rem_dt = core_net_delay - half_dt
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

    # 3. Readout null circuit (bare ground state readout baseline)
    qc_null = QuantumCircuit(
        QuantumRegister(total_qubits, "q"),
        ClassicalRegister(total_clbits, "c"),
        name="spectator_wavefront_null",
    )
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
    target: Any | None = None,
    core_qubit: int = 0,
    x_duration_dt: int | None = None,
    replica_floor: float | None = None,
) -> Group:
    """Group evaluating spectator Ramsey contrast under active drive vs idle control.

    Offline construction takes x_duration_dt, or derives it from target for
    core_qubit, or uses the 8 dt default. live_run.select_candidates rebuilds
    the arms for each routed core from that core's calibrated X duration and
    checks every exposure track against delay_dt (exposure_dt), so these
    arguments shape only the offline template.
    """
    if x_duration_dt is None:
        if target is not None:
            effective_x_dt = core_x_duration_dt(target, core_qubit)
        else:
            effective_x_dt = DEFAULT_X_DURATION_DT
    else:
        effective_x_dt = x_duration_dt

    qc_active, qc_control, qc_null = build_spectator_wavefront_circuits(spectator_count, delay_dt, effective_x_dt)
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
            metrics[f"spectator_p0_active_s{dist_step}"] = active_spectator_p0s[idx]
            metrics[f"spectator_p0_control_s{dist_step}"] = control_spectator_p0s[idx]
            metrics[f"null_p0_s{dist_step}"] = null_spectator_p0s[idx]

        return metrics

    return Group(
        "spectator_wavefront_ramsey",
        members,
        summarize,
        replica_floor=replica_floor,
        # Each spectator's p0 is one bit per shot, a Bernoulli rate with a pooled-shot
        # Wilson interval. The spectator means average correlated bits within a shot,
        # so they carry only the replica t interval.
        rate_keys=frozenset(
            {"core_p0_active"}
            | {
                f"{prefix}_s{step}"
                for prefix in ("spectator_p0_active", "spectator_p0_control", "null_p0")
                for step in range(1, 1 + spectator_count)
            }
        ),
    )
