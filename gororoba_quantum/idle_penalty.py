"""Idle penalty of a target qubit beside a coupled spectator: relaxation, free and echoed dephasing, readout crosstalk.

Every member acts on two qubits, the target T (qubit 0, clbit 0) and a spectator
S coupled to it (qubit 1, clbit 1), with one CZ in one member, so placement packs
disjoint pairs on admitted couplers, each with a guard ring of idle neighbors, and
one shot measures every pair. Every member opens with a reset of both qubits and
a barrier, so each preparation follows the resets' readout and starts from the
same state whatever the previous shot left. The reset makes every member dynamic
(local_compute.is_dynamic), so all of them share one job and one calibration
window: a group never mixes static and dynamic circuits
(live_run.capability_violations).
Each idle is a whole number of dt on the Target clock (4 ns on Heron r2):

- cz_kick (first member): X on S, then H, CZ and H on T, measure. The CZ phase
  kickback flips T to |1>, so P(0) of T against excited reads the CZ phase
  error. It is the group's only two-qubit gate and its primary: live_run
  compiles the first member alone to choose the layout, and placement maps
  every qubit and CZ edge the members touch (live_run.place_replicas), so each
  replica's S sits on a coupler of its T and every other member inherits the pair.
- ground: measure both. P(1) per qubit is preparation plus |0> assignment error.
- excited: X on both, measure. P(0) per qubit is the |1> assignment error.
- relax_t: X on both, an idle of t, measure. The drop of P(1) from excited over
  the RELAX_DT ladder is energy relaxation on both qubits; its rate against the
  reported 1 / T1 is the relaxation idle multiplier of each qubit.
- ramsey_q_t: H on T, an idle of t, then H (q = x) or Sdg and H (q = y), measure.
  <X> = 1 - 2 P(1 | x) and <Y> = 1 - 2 P(1 | y) give T's free-evolution
  visibility and phase; S rests in |0>.
- echo_q_t: as ramsey with an X on T at t / 2. The echo refocuses a static
  detuning and every noise slower than t, so echo against ramsey at one t
  measures how much dephasing an echo removes; the ratio bounds the low-frequency
  share under exponential decay and identifies no noise spectrum. IBM reports T2 from a
  Hahn echo (docs/notes/ibm_quantum/qpu-information.md), and a noise model
  built from it charges a free idle that echo T2.
- zz_q: ramsey at ZZ_DT with S held in |1>. Its phase against ramsey_q at ZZ_DT
  is the static ZZ rate of the coupler.
- meas_during_q and meas_after_q (dynamic): ramsey at MEAS_DT with S read
  MEAS_COUNT times, each read followed by MEAS_GAP_DT, inside T's idle or after
  the joint readout of T and S. Both read T together with S, as the assignment
  references do, and they carry the same operations in a different order.
  Every replica runs its train at once, so the stimulus during T's idle is S's
  readout plus every other replica's on the shared feedlines, the condition of a
  wide dynamic circuit; a visibility or phase of during below after is
  readout-induced dephasing or an AC Stark shift of T from that drive.

- meas_short_q: the during arm over SHORT_MEAS_DT with SHORT_MEAS_COUNT reads,
  against ramsey_q at the same idle. Its phase fixes the shift modulo 100 kHz,
  which unwraps the MEAS_DT phase, identified only modulo 25 kHz.
- idle_s_ramsey, idle_s_echo and idle_s_meas_during/after/short: the same Ramsey,
  echo and readout arms with the roles swapped, S on the equator and T in |0>
  (reading T's train), so every placed qubit carries a dephasing and a
  readout-crosstalk measurement and a repeat whose placement swaps T and S
  still compares each qubit with itself.

A readout train must fit inside its partner's idle: routed_pair_violations rejects a
placement whose Target measure duration on the reading qubit, MEAS_COUNT times with its gaps,
reaches MEAS_DT, so the barrier window that brackets the train lasts the
probe's delay and its exposure in the during arm equals the after arm's. The returned schedule,
not these requests, times every exposure. The group carries no admission: it is
a characterization, analyzed per physical qubit against the calibration the
run's record fingerprints (scripts/idle_penalty_report.py).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from experiments import Group, Member

WIDTH = 2
TARGET, SPECTATOR = 0, 1
# 10, 40 and 100 us at 4 ns per dt.
RELAX_DT = (2500, 10000, 25000)
RAMSEY_DT = (2500, 10000, 25000)
ECHO_DT = (2500, 10000, 25000)
ZZ_DT = 10000
MEAS_DT = 10000
MEAS_COUNT = 12
MEAS_GAP_DT = 64
# A second, shorter readout window: its phase identifies a shift modulo 1 / 10 us = 100 kHz, which
# unwraps the MEAS_DT phase, identified only modulo 25 kHz.
SHORT_MEAS_DT = 2500
SHORT_MEAS_COUNT = 3
QUADRATURES = ("x", "y")


def _circuit(name: str) -> QuantumCircuit:
    circuit = QuantumCircuit(WIDTH, WIDTH, name=name)
    # Both qubits start from an active reset, so each arm's preparation is independent of the shot
    # before it at a short repetition delay and the same for both roles; the barrier keeps every
    # idle clear of the resets' readout.
    circuit.reset(range(WIDTH))
    circuit.barrier(range(WIDTH))
    return circuit


def _law(bits: dict[int, int | None]) -> np.ndarray:
    """Ideal law with each qubit's bit fixed (0 or 1) or uniform (None)."""
    law = np.zeros(1 << WIDTH)
    for outcome in range(1 << WIDTH):
        weight = 1.0
        for qubit, value in bits.items():
            bit = outcome >> qubit & 1
            weight *= 0.5 if value is None else float(bit == value)
        law[outcome] = weight
    return law


def _read(circuit: QuantumCircuit, quadrature: str, probe: int) -> None:
    if quadrature == "y":
        circuit.sdg(probe)
    circuit.h(probe)


def _quadrature_law(quadrature: str, probe: int, partner: int) -> np.ndarray:
    return _law({probe: 0 if quadrature == "x" else None, 1 - probe: partner})


def _readout_train(circuit: QuantumCircuit, qubit: int, count: int = MEAS_COUNT) -> None:
    for _ in range(count):
        circuit.measure(qubit, qubit)
        circuit.delay(MEAS_GAP_DT, qubit, unit="dt")


def probe_prefix(probe: int) -> str:
    """Member-name prefix of the arms whose probe is T (idle_) or S (idle_s_)."""
    return "idle_" if probe == TARGET else "idle_s_"


def _probe_arms(probe: int) -> list[tuple[str, QuantumCircuit, np.ndarray]]:
    """Ramsey, echo and readout-crosstalk arms with probe on the equator and its partner in |0>."""
    both = [TARGET, SPECTATOR]
    partner = 1 - probe
    head = probe_prefix(probe)
    members: list[tuple[str, QuantumCircuit, np.ndarray]] = []
    for delay in RAMSEY_DT:
        for quadrature in QUADRATURES:
            ramsey = _circuit(f"{head}ramsey_{quadrature}_{delay}dt")
            ramsey.h(probe)
            ramsey.delay(delay, both, unit="dt")
            _read(ramsey, quadrature, probe)
            ramsey.measure(both, both)
            members.append((ramsey.name, ramsey, _quadrature_law(quadrature, probe, 0)))
    for delay in ECHO_DT:
        for quadrature in QUADRATURES:
            echo = _circuit(f"{head}echo_{quadrature}_{delay}dt")
            echo.h(probe)
            echo.delay(delay // 2, both, unit="dt")
            echo.x(probe)
            echo.delay(delay - delay // 2, both, unit="dt")
            _read(echo, quadrature, probe)
            echo.measure(both, both)
            members.append((echo.name, echo, _quadrature_law(quadrature, probe, 0)))
    for quadrature in QUADRATURES:
        during = _circuit(f"{head}meas_during_{quadrature}")
        during.h(probe)
        during.barrier(both)
        during.delay(MEAS_DT, probe, unit="dt")
        _readout_train(during, partner)
        during.barrier(both)
        _read(during, quadrature, probe)
        during.measure(both, both)
        members.append((during.name, during, _quadrature_law(quadrature, probe, 0)))
        after = _circuit(f"{head}meas_after_{quadrature}")
        after.h(probe)
        after.barrier(both)
        after.delay(MEAS_DT, probe, unit="dt")
        after.barrier(both)
        _read(after, quadrature, probe)
        after.measure(both, both)
        after.barrier(both)
        _readout_train(after, partner)
        members.append((after.name, after, _quadrature_law(quadrature, probe, 0)))
    for quadrature in QUADRATURES:
        short = _circuit(f"{head}meas_short_{quadrature}")
        short.h(probe)
        short.barrier(both)
        short.delay(SHORT_MEAS_DT, probe, unit="dt")
        _readout_train(short, partner, SHORT_MEAS_COUNT)
        short.barrier(both)
        _read(short, quadrature, probe)
        short.measure(both, both)
        members.append((short.name, short, _quadrature_law(quadrature, probe, 0)))
    return members


def idle_penalty_circuits() -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    both = [TARGET, SPECTATOR]
    members: list[tuple[str, QuantumCircuit, np.ndarray]] = []
    kick = _circuit("idle_cz_kick")
    kick.x(SPECTATOR)
    kick.h(TARGET)
    kick.cz(TARGET, SPECTATOR)
    kick.h(TARGET)
    kick.measure(both, both)
    members.append((kick.name, kick, _law({TARGET: 1, SPECTATOR: 1})))
    ground = _circuit("idle_ground")
    ground.measure(both, both)
    members.append((ground.name, ground, _law({TARGET: 0, SPECTATOR: 0})))
    excited = _circuit("idle_excited")
    excited.x(both)
    excited.measure(both, both)
    members.append((excited.name, excited, _law({TARGET: 1, SPECTATOR: 1})))
    for delay in RELAX_DT:
        relax = _circuit(f"idle_relax_{delay}dt")
        relax.x(both)
        relax.delay(delay, both, unit="dt")
        relax.measure(both, both)
        members.append((relax.name, relax, _law({TARGET: 1, SPECTATOR: 1})))
    for quadrature in QUADRATURES:
        zz = _circuit(f"idle_zz_{quadrature}_{ZZ_DT}dt")
        zz.x(SPECTATOR)
        zz.h(TARGET)
        zz.delay(ZZ_DT, both, unit="dt")
        _read(zz, quadrature, TARGET)
        zz.measure(both, both)
        members.append((zz.name, zz, _quadrature_law(quadrature, TARGET, 1)))
    members += _probe_arms(TARGET)
    members += _probe_arms(SPECTATOR)
    return tuple(members)


def routed_pair_violations(circuits: list[QuantumCircuit], target: Any) -> list[str]:
    """Why a routed placement breaks the pair: T and S off one coupler, or a readout train outlasting its idle.

    Each routed member must act on the same two physical qubits, joined by a
    Target CZ. A qubit read more than once carries a readout train; its reads
    before the final one, each a Target measure duration plus MEAS_GAP_DT, must
    end before the longest delay on the other qubit, the probe's idle that the
    barriers bracket.
    """
    reasons: list[str] = []
    pairs: set[tuple[int, ...]] = set()
    for circuit in circuits:
        active: set[int] = set()
        reads: dict[int, int] = {}
        idles: dict[int, int] = {}
        for instruction in circuit.data:
            qubits = [circuit.find_bit(q).index for q in instruction.qubits]
            name = instruction.operation.name
            if name != "barrier":
                active.update(qubits)
            if name == "measure":
                reads[qubits[0]] = reads.get(qubits[0], 0) + 1
            if name == "delay":
                idles[qubits[0]] = max(idles.get(qubits[0], 0), int(instruction.operation.duration))
        pairs.add(tuple(sorted(active)))
        for qubit, count in reads.items():
            if count <= 1:
                continue
            props = target["measure"].get((qubit,))
            if props is None or props.duration is None:
                reasons.append(f"{circuit.name}: qubit {qubit} has no Target measure duration")
                continue
            span = (count - 1) * (round(props.duration / target.dt) + MEAS_GAP_DT)
            idle = max((d for q, d in idles.items() if q != qubit), default=0)
            if span >= idle:
                reasons.append(f"{circuit.name}: qubit {qubit} readout train of {span} dt reaches the {idle} dt idle")
    if len(pairs) != 1:
        reasons.append(f"members act on different qubit sets {sorted(pairs)}")
    for pair in pairs:
        if len(pair) != WIDTH or not ({pair, pair[::-1]} & set(target["cz"])):
            reasons.append(f"qubits {pair} are not one Target CZ coupler")
    return reasons


def bit_one_probability(distribution: np.ndarray, bit: int) -> float:
    return float(sum(p for outcome, p in enumerate(distribution) if outcome >> bit & 1))


def _quadrature_pair(distributions: dict[str, np.ndarray], stem: str, probe: int) -> tuple[float, float]:
    x = 1.0 - 2.0 * bit_one_probability(distributions[stem.format(q="x")], probe)
    y = 1.0 - 2.0 * bit_one_probability(distributions[stem.format(q="y")], probe)
    return x, y


def idle_penalty_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in idle_penalty_circuits())

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        summary: dict[str, float] = {}
        for bit, role in ((TARGET, "target"), (SPECTATOR, "spectator")):
            excited = bit_one_probability(distributions["idle_excited"], bit)
            summary[f"{role}_p1_ground"] = bit_one_probability(distributions["idle_ground"], bit)
            summary[f"{role}_p0_excited"] = 1.0 - excited
            summary[f"{role}_p1_cz_kick"] = bit_one_probability(distributions["idle_cz_kick"], bit)
            for delay in RELAX_DT:
                summary[f"{role}_p1_relax_{delay}dt"] = bit_one_probability(distributions[f"idle_relax_{delay}dt"], bit)
            head = probe_prefix(bit)
            stems = {f"ramsey_{delay}dt": f"{head}ramsey_{{q}}_{delay}dt" for delay in RAMSEY_DT}
            stems |= {f"echo_{delay}dt": f"{head}echo_{{q}}_{delay}dt" for delay in ECHO_DT}
            stems |= {"meas_during": f"{head}meas_during_{{q}}", "meas_after": f"{head}meas_after_{{q}}"}
            stems["meas_short"] = f"{head}meas_short_{{q}}"
            if bit == TARGET:
                stems["zz"] = f"idle_zz_{{q}}_{ZZ_DT}dt"
            for key, stem in stems.items():
                x, y = _quadrature_pair(distributions, stem, bit)
                summary[f"{role}_{key}_x"] = x
                summary[f"{role}_{key}_y"] = y
                summary[f"{role}_{key}_phase"] = float(np.arctan2(y, x))
                summary[f"{role}_{key}_visibility"] = float(np.hypot(x, y))
        return summary

    return Group("idle_penalty", members, summarize, routed_violations=routed_pair_violations)


def _unitary_part(circuit: QuantumCircuit) -> QuantumCircuit:
    """The circuit without measurements, resets, barriers and delays.

    Every mid-circuit read and reset acts on S in |0>, where it leaves the state
    unchanged, so the remaining gates carry the ideal law.
    """
    out = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if instruction.operation.name in ("measure", "reset", "barrier", "delay"):
            continue
        out.append(instruction.operation, [circuit.find_bit(q).index for q in instruction.qubits])
    return out


if __name__ == "__main__":
    from qiskit.quantum_info import Statevector

    from local_compute import is_dynamic

    for name, circuit, ideal in idle_penalty_circuits():
        probabilities = Statevector(_unitary_part(circuit)).probabilities()
        if not np.allclose(probabilities, ideal, atol=1e-12):
            raise SystemExit(f"{name}: statevector law differs from its ideal")
        if not is_dynamic(circuit):
            raise SystemExit(f"{name}: classifies static, so it would leave the group's job")
    group = idle_penalty_group()
    summary = group.summarize({member.name: member.ideal for member in group.members})
    keys = [f"{role}_{key}" for role in ("target", "spectator") for key in ("ramsey_2500dt", "echo_25000dt")]
    keys += ["target_zz", "target_meas_during", "spectator_meas_after"]
    for key in keys:
        if abs(summary[f"{key}_visibility"] - 1.0) > 1e-12 or abs(summary[f"{key}_phase"]) > 1e-12:
            raise SystemExit(f"{key}: ideal visibility differs from one or phase from zero")
    circuits = {member.name: member.circuit for member in group.members}
    for head in ("idle_", "idle_s_"):
        for quadrature in QUADRATURES:
            # Barriers schedule nothing; every physical operation must match.
            during, after = (
                {k: v for k, v in circuits[f"{head}meas_{arm}_{quadrature}"].count_ops().items() if k != "barrier"}
                for arm in ("during", "after")
            )
            if during != after:
                raise SystemExit(f"{head}{quadrature}: the readout-during and readout-after arms differ")
    print(f"idle penalty: {len(group.members)} circuits on {WIDTH} qubits match their ideal laws and job kinds")
