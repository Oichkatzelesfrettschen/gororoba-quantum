"""Readout attribution of the idle phase rate: the idle_readout campaign on idle_penalty's two-qubit members.

The campaign keeps the idle_penalty members that carry the all-read shift and its references and adds patterned
members: replica k of a patterned member runs the reading body when pair k's class reads in the member's pattern
and the quiet body (a body template) otherwise, so one fused PUB holds readers and quiet pairs at once. A quiet
body is the reading body with the partner's train replaced by an idle of the same nominal span inside the same
barrier window; the probe's idle is unchanged, so the pattern changes which partners read and nothing else. The
group runs on the 30 pinned ordered pairs the class strings index (live_run.plan refuses it unpinned). The design
is docs/design/heron-idle-readout-attribution.md and the analysis scripts/idle_readout_attribution.py.
"""

from __future__ import annotations

import itertools
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from experiments import Group, Member
from idle_penalty import (
    MEAS_COUNT,
    MEAS_DT,
    MEAS_GAP_DT,
    QUADRATURES,
    RAMSEY_DT,
    SHORT_MEAS_COUNT,
    SHORT_MEAS_DT,
    SPECTATOR,
    TARGET,
    WIDTH,
    _circuit,
    _quadrature_law,
    _quadrature_pair,
    _read,
    _readout_train,
    bit_one_probability,
    idle_penalty_circuits,
    probe_prefix,
    routed_pair_violations,
)

# Target measure duration, in dt, that sets a quiet body's partner idle. Every qubit of ibm_kingston
# reports 2180 ns at dt 4 ns (docs/evidence/heron_platform/targets.json); a quiet idle shorter or
# longer by a few reads leaves the barrier window, which the probe's idle fixes, unchanged.
MEASURE_DT = 545
# Class of each pinned ordered pair (one letter per pair, in pin order) under the two partitions of
# the readout attribution. Each is a proper 2-coloring of the graph joining pairs with a qubit
# within three CZ hops on ibm_kingston, so every reader within three hops of a probe sits in the
# opposite class (scripts/idle_readout_attribution.geometry refuses a string that is not).
PARTITIONS = {
    "p1": "ABABAAABBABABBBBBABBAABAABBBAA",
    "p2": "ABBBAAABBBBBBBBBAABBAAAAABABAA",
}
# Pattern a reads the partners of class A pairs and holds class B quiet; pattern b swaps them.
PATTERNS = {"a": "A", "b": "B"}
READOUT_RAMSEY_DT = RAMSEY_DT[:2]


def _window_arm(name: str, probe: int, quadrature: str, idle_dt: int, count: int, reading: bool) -> QuantumCircuit:
    """Ramsey of probe over idle_dt with its partner reading count times (reading) or idling the train's span.

    Both variants bracket the window with the same barriers and give the partner the same
    operations except the reads, so the probe's idle and the window it sits in are identical.
    """
    both = [TARGET, SPECTATOR]
    arm = _circuit(name)
    arm.h(probe)
    arm.barrier(both)
    arm.delay(idle_dt, probe, unit="dt")
    if reading:
        _readout_train(arm, 1 - probe, count)
    else:
        arm.delay(count * (MEASURE_DT + MEAS_GAP_DT), 1 - probe, unit="dt")
    arm.barrier(both)
    _read(arm, quadrature, probe)
    arm.measure(both, both)
    return arm


def half_member(probe: int, partition: str, pattern: str, quadrature: str, short: bool = False) -> str:
    """Name of the patterned member of probe, partition, pattern and quadrature (the short window when short)."""
    window = "meas_short_half" if short else "meas_half"
    return f"{probe_prefix(probe)}{window}_{partition}{pattern}_{quadrature}"


def _quiet_name(probe: int, quadrature: str, short: bool) -> str:
    return f"{probe_prefix(probe)}{'meas_short_quiet' if short else 'meas_quiet'}_{quadrature}"


def readout_templates() -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    """Quiet bodies: the reading arms with the partner's train replaced by an idle of the train's span."""
    templates: list[tuple[str, QuantumCircuit, np.ndarray]] = []
    for probe in (TARGET, SPECTATOR):
        for short in (False, True):
            for quadrature in QUADRATURES:
                idle, count = (SHORT_MEAS_DT, SHORT_MEAS_COUNT) if short else (MEAS_DT, MEAS_COUNT)
                name = _quiet_name(probe, quadrature, short)
                quiet = _window_arm(name, probe, quadrature, idle, count, reading=False)
                templates.append((name, quiet, _quadrature_law(quadrature, probe, 0)))
    return tuple(templates)


def readout_bodies(probe: int, partition: str, pattern: str, quadrature: str, short: bool) -> tuple[str, ...]:
    """Body of each replica in pin order: the reading arm for the pattern's class, the quiet arm otherwise."""
    head = probe_prefix(probe)
    reader = f"{head}meas_short_{quadrature}" if short else f"{head}meas_during_{quadrature}"
    quiet = _quiet_name(probe, quadrature, short)
    return tuple(reader if cls == PATTERNS[pattern] else quiet for cls in PARTITIONS[partition])


def _retained_readout_names() -> frozenset[str]:
    names = {"idle_cz_kick", "idle_ground", "idle_excited"}
    for probe in (TARGET, SPECTATOR):
        head = probe_prefix(probe)
        for quadrature in QUADRATURES:
            names.update(f"{head}ramsey_{quadrature}_{delay}dt" for delay in READOUT_RAMSEY_DT)
            names.update(f"{head}meas_{arm}_{quadrature}" for arm in ("during", "after", "short"))
    return frozenset(names)


def routed_readout_violations(circuits: list[QuantumCircuit], target: Any) -> list[str]:
    """routed_pair_violations plus a quiet body whose partner idle outlasts the probe's idle."""
    reasons = routed_pair_violations(circuits, target)
    for circuit in circuits:
        if "quiet" not in circuit.name:
            continue
        idles: dict[int, int] = {}
        for instruction in circuit.data:
            if instruction.operation.name == "delay":
                qubit = circuit.find_bit(instruction.qubits[0]).index
                idles[qubit] = max(idles.get(qubit, 0), int(instruction.operation.duration))
        delays = sorted(idles.values())
        if len(delays) != WIDTH or delays[0] >= delays[1]:
            reasons.append(f"{circuit.name}: the partner idle does not fit inside the probe idle, delays {delays} dt")
    return reasons


def idle_readout_group() -> Group:
    """The readout-attribution group: 23 retained members, 32 patterned members and 8 quiet body templates."""
    retained = _retained_readout_names()
    unpatterned = [(name, circuit, ideal) for name, circuit, ideal in idle_penalty_circuits() if name in retained]
    if len(unpatterned) != len(retained):
        raise ValueError("a retained readout member is missing from the idle-penalty circuits")
    templates = readout_templates()
    bodies = {name: (circuit, ideal) for name, circuit, ideal in [*unpatterned, *templates]}
    members = [Member(name, circuit, ideal) for name, circuit, ideal in unpatterned]
    for probe in (TARGET, SPECTATOR):
        for partition in PARTITIONS:
            for pattern in PATTERNS:
                for short in (False, True):
                    for quadrature in QUADRATURES:
                        names = readout_bodies(probe, partition, pattern, quadrature, short)
                        circuit, ideal = bodies[names[0]]
                        members.append(
                            Member(
                                half_member(probe, partition, pattern, quadrature, short),
                                circuit,
                                ideal,
                                replica_bodies=names,
                            )
                        )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for bit, role in ((TARGET, "target"), (SPECTATOR, "spectator")):
            excited = bit_one_probability(distributions["idle_excited"], bit)
            summary[f"{role}_p1_ground"] = bit_one_probability(distributions["idle_ground"], bit)
            summary[f"{role}_p0_excited"] = 1.0 - excited
            summary[f"{role}_p1_cz_kick"] = bit_one_probability(distributions["idle_cz_kick"], bit)
            head = probe_prefix(bit)
            stems = {f"ramsey_{delay}dt": f"{head}ramsey_{{q}}_{delay}dt" for delay in READOUT_RAMSEY_DT}
            stems |= {f"meas_{arm}": f"{head}meas_{arm}_{{q}}" for arm in ("during", "after", "short")}
            for partition, pattern in itertools.product(PARTITIONS, PATTERNS):
                stems[f"meas_half_{partition}{pattern}"] = half_member(bit, partition, pattern, "{q}")
                stems[f"meas_short_half_{partition}{pattern}"] = half_member(bit, partition, pattern, "{q}", True)
            for key, stem in stems.items():
                x, y = _quadrature_pair(distributions, stem, bit)
                summary[f"{role}_{key}_x"] = x
                summary[f"{role}_{key}_y"] = y
                summary[f"{role}_{key}_phase"] = float(np.arctan2(y, x))
                summary[f"{role}_{key}_visibility"] = float(np.hypot(x, y))
        return summary

    return Group(
        "idle_readout",
        tuple(members),
        summarize,
        routed_violations=routed_readout_violations,
        body_templates=templates,
    )


if __name__ == "__main__":
    from qiskit.quantum_info import Statevector

    from idle_penalty import _unitary_part
    from local_compute import is_dynamic

    readout = idle_readout_group()
    for name, circuit, ideal in readout.body_templates:
        if not np.allclose(Statevector(_unitary_part(circuit)).probabilities(), ideal, atol=1e-12):
            raise SystemExit(f"{name}: statevector law differs from its ideal")
        if not is_dynamic(circuit):
            raise SystemExit(f"{name}: classifies static, so it would leave the group's job")
    patterned = [member for member in readout.members if member.replica_bodies is not None]
    print(
        f"idle readout: {len(readout.members)} members, {len(patterned)} patterned over "
        f"{len(patterned[0].replica_bodies or ())} replicas, {len(readout.body_templates)} quiet bodies"
    )
