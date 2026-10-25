"""Matched QPE diagnostics with measured-bit observables and explicit inference.

The folded family compares a common terminal bit across two execution kinds.
The N=21 family measures the labeled distribution's response to feed-forward;
two phase bits do not supply an order-recovery experiment. The
state-prep-control family reads each named qubit's excited fraction after
initialization, after an active reset, and after an X, at one repetition
delay, or alone the excited fraction after shots that end with an X on
the measured state. The measurement-sequence family compares a named qubit's
final Z outcome after N rotations that each precede a mid-circuit measurement
with the same rotations separated by an idle of the measurement's duration;
run directly with --self-test it checks both families' exact laws.
"""

from __future__ import annotations

import argparse
import math
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member, Summary, tvd
from qpe_diagnostics import (
    N21_ORBIT_SWEEP_VARIANTS,
    N21_ORBIT_VARIANTS,
    N21_SPECTATOR_GROUND_KINDS,
    N21_SPECTATOR_KINDS,
    N21_SPECTATOR_QUADRATURES,
    N21_SPECTATOR_SPLIT_KINDS,
    folded_diagnostic,
    folded_ideal,
    folded_terminal_weights,
    lift_phase_law,
    lift_phase_values,
    n21_diagnostic,
    n21_encoded_diagnostic,
    n21_labeled_law,
    n21_orbit_diagnostic,
    n21_ramsey_name,
    n21_segment_read_clbits,
    n21_segmented_law,
    n21_segmented_name,
    n21_segmented_ramsey,
    n21_spectator_law,
    n21_spectator_ramsey,
    phase_marginal,
)

FAMILY_NAMES = (
    "et-row",
    "folded-qpe",
    "folded-correction",
    "n21-feedback",
    "n21-feedback-encoded",
    "n21-orbit-feedback",
    "n21-orbit-rca",
    "patch-window",
    "coherence-window",
    "ripple",
    "rank-sector",
    "state-prep-control",
    "measurement-sequence",
)
# Families that run on one pinned patch (--patch-qubits, patch_characterization.PATCH_ROLES).
PATCH_FAMILIES = ("patch-window", "coherence-window")
N21_FAMILIES = ("n21-feedback", "n21-feedback-encoded", "n21-orbit-feedback")
# Member and observable prefix of each N21 family's matched pair.
N21_PREFIXES = {"n21-feedback": "n21", "n21-feedback-encoded": "n21_encoded", "n21-orbit-feedback": "n21_orbit"}


def correction_group() -> Group:
    """Reconstruct the finite odd-label correction family and its raw summaries."""
    from correction_planning import correction_group as build_correction_group

    return build_correction_group()


def folded_group(rungs: tuple[str, ...], measurement_delay_dt: int | dict[int, int] | None = None) -> Group:
    """One execution kind of the ladder, bound to a fresh measurement duration."""
    members = tuple(
        Member(
            f"qpe_{rung}_s{label}",
            folded_diagnostic(
                label,
                rung,
                measurement_delay_dt=(
                    measurement_delay_dt[label] if isinstance(measurement_delay_dt, dict) else measurement_delay_dt
                ),
            ),
            np.asarray(folded_ideal(label, rung), dtype=float),
            weights=np.asarray(folded_terminal_weights(label, rung)),
        )
        for rung in rungs
        for label in range(4)
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result: dict[str, float] = {}
        for member in members:
            result[member.name + "_terminal_correct"] = float(distributions[member.name] @ member.weights)
            result[member.name + "_tvd_to_own_ideal"] = tvd(distributions[member.name], member.ideal)
            if member.circuit.num_clbits == 2:
                label = int(member.name[-1])
                result[member.name + "_first_correct"] = float(
                    sum(distributions[member.name][outcome] for outcome in range(4) if outcome % 2 == label % 2)
                )
        return result

    kind = "static" if rungs == ("coherent",) else "dynamic"
    return Group(
        "folded_qpe_ladder_" + kind,
        members,
        summarize,
        rate_keys=frozenset(member.name + "_terminal_correct" for member in members),
    )


def n21_group(orbit: bool = False, encoded: bool = False) -> Group:
    """Pair the feed-forward arm with its omitted-correction control.

    orbit selects the multipliers compiled on the orbit of |1>; encoded
    selects the complete multipliers in the linear work-register encoding
    (qpe_diagnostics.N21_ENCODED_COLUMNS). Every variant shares the exact
    labeled law, weights, and contrast.
    """
    if orbit and encoded:
        raise ValueError("the orbit and encoded N21 variants are separate families")
    prefix = "n21_orbit" if orbit else "n21_encoded" if encoded else "n21"

    def build(feedback: bool) -> QuantumCircuit:
        if orbit:
            return n21_orbit_diagnostic(feedback, "nominal_unbarriered")
        return n21_encoded_diagnostic(feedback) if encoded else n21_diagnostic(feedback)

    members = tuple(
        Member(
            f"{prefix}_feedback" if feedback else f"{prefix}_no_feedback",
            build(feedback),
            np.asarray(n21_labeled_law(feedback), dtype=float),
            weights=np.asarray((0.5, 1.0, 0.5, 0.0)),
        )
        for feedback in (True, False)
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        primary, control = (distributions[member.name] for member in members)
        return {
            "feedback_signed_contrast": float(primary[1] - primary[3]),
            "no_feedback_signed_contrast": float(control[1] - control[3]),
            "contrast_difference": float(primary[1] - primary[3] - control[1] + control[3]),
            "labeled_tvd": tvd(primary, control),
            "feedback_tvd_to_ideal": tvd(primary, members[0].ideal),
            "no_feedback_tvd_to_ideal": tvd(control, members[1].ideal),
        }

    return Group(f"{prefix}_feedback", members, summarize)


_SIGNED = (0.0, 1.0, 0.0, -1.0)

# state-prep-control: the arms in PUB order, A (init, measure), B (init,
# reset, measure) and C (x, measure). Every named qubit runs each selected arm
# in the same shots, so A and C share the static job and B, which a reset
# makes dynamic, runs in its own job with twirling and DD off.
#
# H (init, measure, x) reads the initial state and then flips the projected
# one, so a shot ends in |1> unless its own initialization left |1> or the X
# fails, and with init_qubits on every shot of H starts from the implicit
# reset of that near-|1> history (scripts/state_prep_excess.py bounds the
# all-|1> excitation from it). Circuits of one job interleave shot by shot
# in an order the service leaves unspecified, so H is the only arm of its
# job; the X after the measurement makes H dynamic
# (local_compute.is_dynamic), so that job runs with twirling and DD off.
STATE_PREP_FAMILY = "state-prep-control"
STATE_PREP_ARMS = ("prep0", "reset", "x", "x_history")
# The selection an omitted --state-prep-arms makes.
STATE_PREP_DEFAULT_ARMS = ("prep0", "reset", "x")
STATE_PREP_HISTORY_ARM = "x_history"
STATE_PREP_ARM_STEPS = {
    "prep0": "init, measure",
    "reset": "init, reset, measure",
    "x": "x, measure",
    "x_history": "init, measure, x",
}
# Arms whose circuits local_compute.is_dynamic classifies dynamic: each runs
# in its own per-qubit group, since one group holds one job kind.
STATE_PREP_DYNAMIC_ARMS = ("reset", "x_history")
# The retained n21-feedback-encoded dry run whose R = 2 replica qubits the
# family measures when --layout is absent; repository-relative.
STATE_PREP_SOURCE_RECORD = "results/live/2026-10-17T130242.718497Z/record.json"
# Two-sided half-widths every endpoint must reach at the family-wise alpha
# split over 3 endpoints per qubit. With 14 qubits and alpha 0.05 the
# Hoeffding radius of one PUB is 0.0213 at 8192 shots and 0.0301 at 4096; a
# two-PUB difference takes 0.0445 and 0.0630, so 8192 shots is the smallest
# admitted power-of-two tier.
STATE_PREP_PRECISION = {"excited": 0.025, "reset_benefit": 0.05, "one_column": 0.025, "history_excited": 0.025}
_EXCITED = (0.0, 1.0)


def state_prep_member(arm: str, qubit: int) -> str:
    return f"spc_{arm}_q{qubit}"


def state_prep_circuit(arm: str, qubit: int) -> QuantumCircuit:
    """One arm on one qubit: init then measure, init-reset-measure, x then measure, or measure then x."""
    if arm not in STATE_PREP_ARMS:
        raise ValueError(f"unknown state-prep arm {arm!r}")
    circuit = QuantumCircuit(1, 1, name=state_prep_member(arm, qubit))
    if arm == "reset":
        circuit.reset(0)
    elif arm == "x":
        circuit.x(0)
    circuit.measure(0, 0)
    if arm == STATE_PREP_HISTORY_ARM:
        circuit.x(0)
    return circuit


def state_prep_arms(arms: Any = None) -> tuple[str, ...]:
    """The selected arms in STATE_PREP_ARMS order; None selects prep0, reset and x.

    Every selection holds prep0, or is x_history alone: x_history sets the
    history of every shot of its job, so another arm in that job would start
    from a |1> history as well.
    """
    if arms is None:
        return STATE_PREP_DEFAULT_ARMS
    selected = tuple(arms)
    if not selected or len(set(selected)) != len(selected) or set(selected) - set(STATE_PREP_ARMS):
        raise ValueError(f"state-prep arms must be distinct members of {STATE_PREP_ARMS}, got {list(selected)}")
    if STATE_PREP_HISTORY_ARM in selected and len(selected) > 1:
        raise ValueError(
            "x_history sets the end state every shot of its job leaves, so it runs as the only arm of its job"
        )
    if "prep0" not in selected and selected != (STATE_PREP_HISTORY_ARM,):
        raise ValueError(
            "the family measures the initial excited fraction, which only the prep0 and x_history arms read"
        )
    return tuple(arm for arm in STATE_PREP_ARMS if arm in selected)


def state_prep_groups(qubits: list[int], arms: Any = None) -> list[Group]:
    """Per qubit, a static group (prep0, then x) and one dynamic group per dynamic arm (reset, x_history).

    Fusion joins row r of every group of one kind into one PUB, so PUB A
    measures every qubit's prep0 arm in the same shots, PUB C every x arm,
    the dynamic PUB B every reset arm, and the dynamic PUB H, alone in its
    job, every x_history arm.
    """
    if not qubits or len(set(qubits)) != len(qubits) or any(type(q) is not int or q < 0 for q in qubits):
        raise ValueError(f"state-prep-control needs distinct nonnegative qubits, got {qubits}")
    selected = state_prep_arms(arms)
    static_arms = tuple(arm for arm in selected if arm not in STATE_PREP_DYNAMIC_ARMS)
    groups = []
    for qubit in qubits:
        ideal = {"prep0": (1.0, 0.0), "reset": (1.0, 0.0), "x": (0.0, 1.0), "x_history": (1.0, 0.0)}
        members = {
            arm: Member(
                state_prep_member(arm, qubit),
                state_prep_circuit(arm, qubit),
                np.asarray(ideal[arm], dtype=float),
                weights=np.asarray(ideal[arm], dtype=float),
            )
            for arm in selected
        }

        def summarize_static(distributions: dict[str, np.ndarray], qubit: int = qubit) -> dict[str, float]:
            names = {"prep0": f"q{qubit}_excited_fraction", "x": f"q{qubit}_one_fraction"}
            return {
                names[arm]: float(distributions[state_prep_member(arm, qubit)][1])
                for arm in names
                if state_prep_member(arm, qubit) in distributions
            }

        def summarize_reset(distributions: dict[str, np.ndarray], qubit: int = qubit) -> dict[str, float]:
            return {f"q{qubit}_reset_excited_fraction": float(distributions[state_prep_member("reset", qubit)][1])}

        def summarize_history(distributions: dict[str, np.ndarray], qubit: int = qubit) -> dict[str, float]:
            member = state_prep_member(STATE_PREP_HISTORY_ARM, qubit)
            return {f"q{qubit}_x_history_excited_fraction": float(distributions[member][1])}

        if static_arms:
            groups.append(Group(f"state_prep_q{qubit}", tuple(members[arm] for arm in static_arms), summarize_static))
        if "reset" in selected:
            groups.append(Group(f"state_prep_reset_q{qubit}", (members["reset"],), summarize_reset))
        if STATE_PREP_HISTORY_ARM in selected:
            groups.append(
                Group(f"state_prep_x_history_q{qubit}", (members[STATE_PREP_HISTORY_ARM],), summarize_history)
            )
    return groups


def state_prep_contracts(
    qubits: list[int], alpha: float, power: float, arms: Any = None
) -> tuple[ObservableContract, ...]:
    """Two-sided precision endpoints per qubit for the selected arms, at the family-wise alpha split over all.

    spc_excited_qQ reads P(1) after initialization (residual excitation plus
    readout misassignment); spc_reset_benefit_qQ reads that minus P(1) after
    an active reset, positive where initialization leaves more excitation
    than the reset's own misassignment; spc_one_column_qQ reads P(1) after
    an X, the |1> column of the assignment matrix; spc_history_excited_qQ
    reads P(1) after initialization from a |1> history. Each endpoint needs
    every arm it reads among the selected arms.
    """
    selected = state_prep_arms(arms)
    endpoints = [
        name
        for name, needs in (
            ("excited", {"prep0"}),
            ("reset_benefit", {"prep0", "reset"}),
            ("one_column", {"x"}),
            ("history_excited", {STATE_PREP_HISTORY_ARM}),
        )
        if needs <= set(selected)
    ]
    share = alpha / (len(endpoints) * len(qubits))
    contracts: list[ObservableContract] = []
    for qubit in qubits:
        contracts.extend(
            contract
            for contract in (
                ObservableContract(
                    f"spc_excited_q{qubit}",
                    (ObservableTerm(state_prep_member("prep0", qubit), _EXCITED),),
                    alpha=share,
                    power=power,
                    precision_half_width=STATE_PREP_PRECISION["excited"],
                ),
                ObservableContract(
                    f"spc_reset_benefit_q{qubit}",
                    (
                        ObservableTerm(state_prep_member("prep0", qubit), _EXCITED),
                        ObservableTerm(state_prep_member("reset", qubit), _EXCITED, sign=-1),
                    ),
                    alpha=share,
                    power=power,
                    precision_half_width=STATE_PREP_PRECISION["reset_benefit"],
                ),
                ObservableContract(
                    f"spc_one_column_q{qubit}",
                    (ObservableTerm(state_prep_member("x", qubit), _EXCITED),),
                    alpha=share,
                    power=power,
                    precision_half_width=STATE_PREP_PRECISION["one_column"],
                ),
                ObservableContract(
                    f"spc_history_excited_q{qubit}",
                    (ObservableTerm(state_prep_member(STATE_PREP_HISTORY_ARM, qubit), _EXCITED),),
                    alpha=share,
                    power=power,
                    precision_half_width=STATE_PREP_PRECISION["history_excited"],
                ),
            )
            if contract.name.removeprefix("spc_").rsplit("_q", 1)[0] in endpoints
        )
    return tuple(contracts)


def state_prep_excitation(excited: float, prob_meas1_prep0: float, prob_meas0_prep1: float) -> float:
    """The initial excitation epsilon an excited fraction implies under a readout channel.

    P(1 | init) = (1 - eps) e10 + eps (1 - e01) with e10 = prob_meas1_prep0 and
    e01 = prob_meas0_prep1, so eps = (P - e10) / (1 - e01 - e10): the value
    dynamic_density's prep_excitation and live_run's --prep-excitation take.
    eps rises in P, falls in e10 wherever P < 1 - e01, and rises in e01
    wherever P > e10.
    """
    contrast = 1.0 - prob_meas0_prep1 - prob_meas1_prep0
    if not contrast > 0:
        raise ValueError("the readout channel carries no information about the prepared state")
    return (excited - prob_meas1_prep0) / contrast


# measurement-sequence: does a mid-circuit measurement act as ideal pinching,
# a nonselective projective measurement in Z, on a named qubit? A measure arm
# applies N rotations RX(sign * THETA / N), each followed by a measurement
# whose outcome the program never reads; a delay arm replaces each such
# measurement with an idle of the backend's measure duration on that qubit, so
# it keeps the elapsed time and drops the projection. Both read the qubit in
# Z at the end. The state after each measurement is diagonal in Z, so the
# measure arm's final P0 follows the Markov law of MSQ_THETA / N rotations
# and a shift of the qubit frequency after readout has no effect on it; the
# delay arm's coherent rotations compose to RX(sign * THETA).
#
# Register layout, clbit 0 first: "final" (1 bit) holds the last read and
# every distribution and summary reads it; the measure arm's "mcm" register
# (N bits) holds the mid-circuit outcomes, which the raw shots keep and no
# endpoint conditions on. A measure member's ideal and weights span all
# N + 1 clbits, as every family with a register no endpoint reads does
# (n21_segmented_law); weights select final == 0.
MSQ_FAMILY = "measurement-sequence"
MSQ_THETA = 8.0 * math.pi / 9.0
MSQ_STEPS = (1, 2, 4, 8, 16)
MSQ_ARMS = ("measure", "delay")
# The four signed members of one (arm, N), in execution order +, -, -, +: the
# sign of the rotation and the repeat letter that names the member.
MSQ_SIGNED = (("p", "a", 1), ("m", "a", -1), ("m", "b", -1), ("p", "b", 1))
# Steps with a gate after a measurement run as dynamic circuits
# (local_compute.is_dynamic); the one-step measure arm and the delay arm do
# not, so a qubit's measure members split over the static and dynamic groups.
MSQ_DYNAMIC_STEPS = tuple(n for n in MSQ_STEPS if n >= 2)
MSQ_ARM_STEPS = {
    "measure": "rx(sign * THETA / N), measure into mcm, repeated N times; measure into final",
    "delay": "rx(sign * THETA / N), delay of one measure duration, repeated N times; measure into final",
}
# Two-sided half-widths every endpoint must reach at the family-wise alpha
# split over 11 endpoints per qubit (5 measure P0, 5 delay P0 and the N = 16
# contrast). The optimizer takes each endpoint's PUBs as streams of span
# 0.25 (a pooled member weighs 1/4) and gives each stream the tail
# alpha_endpoint / streams, so a pooled P0 over 4 PUBs has radius
# sqrt(ln(8 / alpha_endpoint) / (2 shots)) and the contrast over 8 PUBs
# 2 * sqrt(ln(16 / alpha_endpoint) / (2 shots)). With alpha 0.05 and 14 qubits
# (alpha_endpoint 3.25e-4) a P0 reaches 0.0248 at 8192 shots and 0.0351 at
# 4096, and the contrast 0.0514 and 0.0727, so 8192 shots is the smallest
# admitted power-of-two tier from 1 to 14 qubits.
MSQ_PRECISION = {"p0": 0.03, "contrast": 0.055}
MSQ_ENDPOINTS_PER_QUBIT = 2 * len(MSQ_STEPS) + 1


def msq_member(arm: str, steps: int, signed: tuple[str, str, int], qubit: int) -> str:
    """msq_{arm}_n{N}_{sign}{repeat}_q{qubit}: sign p is RX(+THETA / N), m is RX(-THETA / N); repeat a or b."""
    return f"msq_{arm}_n{steps}_{signed[0]}{signed[1]}_q{qubit}"


def msq_circuit(arm: str, steps: int, sign: int, qubit: int, name: str, delay_dt: int) -> QuantumCircuit:
    """One signed member: steps rotations, each followed by a measure (mcm) or by a delay, then the final read."""
    if arm not in MSQ_ARMS or steps not in MSQ_STEPS or sign not in (1, -1):
        raise ValueError(f"unknown measurement-sequence member {arm!r} n{steps} sign {sign!r}")
    if type(delay_dt) is not int or delay_dt <= 0:
        raise ValueError(f"the delay of {name} must be a positive integer number of dt, got {delay_dt!r}")
    wire = QuantumRegister(1, "q")
    final = ClassicalRegister(1, "final")
    if arm == "measure":
        mcm = ClassicalRegister(steps, "mcm")
        circuit = QuantumCircuit(wire, final, mcm, name=name)
    else:
        circuit = QuantumCircuit(wire, final, name=name)
    for step in range(steps):
        circuit.rx(sign * MSQ_THETA / steps, 0)
        if arm == "measure":
            circuit.measure(0, circuit.clbits[1 + step])
        else:
            circuit.delay(delay_dt, 0, unit="dt")
    circuit.measure(0, final[0])
    return circuit


def msq_pinched_p0(steps: int) -> float:
    """Ideal final P0 of the measure arm: (1 + cos(THETA / N) ** N) / 2."""
    return (1.0 + math.cos(MSQ_THETA / steps) ** steps) / 2.0


def msq_delay_p0() -> float:
    """Ideal final P0 of the delay arm at every N: cos(THETA / 2) ** 2."""
    return math.cos(MSQ_THETA / 2.0) ** 2


def msq_measure_law(steps: int) -> np.ndarray:
    """Ideal law of a measure member over its N + 1 clbits: index = final + 2 * (mcm bits, step k at bit k).

    The qubit holds the last outcome after each measurement, so a rotation by
    phi = THETA / N repeats it with probability cos(phi / 2) ** 2 and flips it
    with probability sin(phi / 2) ** 2, starting from outcome 0; the final read
    repeats the last mcm bit. The law is the same for both rotation signs.
    """
    stay = math.cos(MSQ_THETA / steps / 2.0) ** 2
    flip = math.sin(MSQ_THETA / steps / 2.0) ** 2
    law = np.ones(1)
    last = np.zeros(1, dtype=np.int64)
    for _ in range(steps):
        law = np.concatenate([law * np.where(last == bit, stay, flip) for bit in (0, 1)])
        last = np.concatenate([np.full(last.size, bit, dtype=np.int64) for bit in (0, 1)])
    full = np.zeros(2 ** (steps + 1))
    full[(np.arange(law.size) << 1) | last] = law
    return full


def msq_weights(steps: int, arm: str) -> np.ndarray:
    """1 on every outcome whose final bit (clbit 0) reads 0, over the member's outcome space."""
    width = 2 if arm == "delay" else 2 ** (steps + 1)
    return np.asarray([1.0 - (index & 1) for index in range(width)])


def msq_delays(qubits: list[int], measurement_delay_dt: Any) -> dict[int, int]:
    """The per-qubit measure duration in dt, one positive integer for each named qubit."""
    if not qubits or len(set(qubits)) != len(qubits) or any(type(q) is not int or q < 0 for q in qubits):
        raise ValueError(f"measurement-sequence needs distinct nonnegative qubits, got {qubits}")
    if not isinstance(measurement_delay_dt, dict):
        raise ValueError("measurement-sequence needs a measure duration in dt for each qubit")
    delays = {int(qubit): duration for qubit, duration in measurement_delay_dt.items()}
    if set(delays) != set(qubits) or any(type(d) is not int or d <= 0 for d in delays.values()):
        raise ValueError(f"measurement-sequence needs one positive dt duration per qubit, got {measurement_delay_dt}")
    return delays


def msq_members(qubit: int, delay_dt: int) -> tuple[tuple[Member, ...], tuple[Member, ...]]:
    """(static members, dynamic members) of one qubit, in execution order.

    Static: the one-step measure arm, then the delay arm at each N. Dynamic:
    the measure arm at N >= 2. Within an (arm, N) the order is +, -, -, +.
    """

    def build(arm: str, steps: int) -> list[Member]:
        ideal = msq_measure_law(steps) if arm == "measure" else np.asarray([msq_delay_p0(), 1.0 - msq_delay_p0()])
        weights = msq_weights(steps, arm)
        return [
            Member(
                msq_member(arm, steps, signed, qubit),
                msq_circuit(arm, steps, signed[2], qubit, msq_member(arm, steps, signed, qubit), delay_dt),
                ideal,
                weights=weights,
            )
            for signed in MSQ_SIGNED
        ]

    static = [*build("measure", 1), *(m for steps in MSQ_STEPS for m in build("delay", steps))]
    dynamic = [m for steps in MSQ_DYNAMIC_STEPS for m in build("measure", steps)]
    return tuple(static), tuple(dynamic)


def _msq_final_p0(distribution: np.ndarray) -> float:
    return float(distribution[0::2].sum())


def _msq_summary(distributions: dict[str, np.ndarray], qubit: int) -> dict[str, float]:
    """Pooled final P0 per (arm, N) whose four signed members are present, and the measure arm's deficit."""
    result: dict[str, float] = {}
    for arm in MSQ_ARMS:
        for steps in MSQ_STEPS:
            names = [msq_member(arm, steps, signed, qubit) for signed in MSQ_SIGNED]
            if not all(name in distributions for name in names):
                continue
            pooled = math.fsum(_msq_final_p0(distributions[name]) for name in names) / len(names)
            result[f"q{qubit}_msq_p0_{arm}_n{steps}"] = pooled
            if arm == "measure":
                result[f"q{qubit}_msq_deficit_n{steps}"] = msq_pinched_p0(steps) - pooled
    return result


def _msq_summarizer(qubit: int) -> Summary:
    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        return _msq_summary(distributions, qubit)

    return summarize


def measurement_sequence_groups(qubits: list[int], measurement_delay_dt: Any) -> list[Group]:
    """Per qubit, a static group and a dynamic group; row r of each kind fuses across the qubits into one PUB.

    measurement_delay_dt maps each qubit to its measure duration in dt, which
    the delay arm idles per step. Each group's summary reports, per N, the
    final P0 pooled over the four signed members and, for the measure arm,
    the deficit ideal - measured.
    """
    delays = msq_delays(qubits, measurement_delay_dt)
    groups = []
    for qubit in qubits:
        static, dynamic = msq_members(qubit, delays[qubit])
        groups.append(Group(f"msq_static_q{qubit}", static, _msq_summarizer(qubit)))
        groups.append(Group(f"msq_dynamic_q{qubit}", dynamic, _msq_summarizer(qubit)))
    return groups


def measurement_sequence_contracts(qubits: list[int], alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Eleven two-sided precision endpoints per qubit at the family-wise alpha split over all.

    msq_p0_measure_nN_qQ and msq_p0_delay_nN_qQ read the final P0 pooled over
    the four signed members of the arm at N; msq_zeno_contrast_n16_qQ reads the
    measure arm minus the delay arm at N = 16, the mutation-test endpoint. A
    pooled member carries score values at weight 1/4, so the endpoint's
    estimate is the pooled mean.
    """
    if not qubits or len(set(qubits)) != len(qubits) or any(type(q) is not int or q < 0 for q in qubits):
        raise ValueError(f"measurement-sequence needs distinct nonnegative qubits, got {qubits}")
    share = alpha / (MSQ_ENDPOINTS_PER_QUBIT * len(qubits))

    def terms(arm: str, steps: int, qubit: int, sign: int = 1) -> tuple[ObservableTerm, ...]:
        values = tuple(float(value) / len(MSQ_SIGNED) for value in msq_weights(steps, arm))
        return tuple(ObservableTerm(msq_member(arm, steps, signed, qubit), values, sign=sign) for signed in MSQ_SIGNED)

    contracts: list[ObservableContract] = []
    for qubit in qubits:
        for arm in MSQ_ARMS:
            contracts.extend(
                ObservableContract(
                    f"msq_p0_{arm}_n{steps}_q{qubit}",
                    terms(arm, steps, qubit),
                    alpha=share,
                    power=power,
                    precision_half_width=MSQ_PRECISION["p0"],
                )
                for steps in MSQ_STEPS
            )
        top = MSQ_STEPS[-1]
        contracts.append(
            ObservableContract(
                f"msq_zeno_contrast_n{top}_q{qubit}",
                (*terms("measure", top, qubit), *terms("delay", top, qubit, sign=-1)),
                alpha=share,
                power=power,
                precision_half_width=MSQ_PRECISION["contrast"],
            )
        )
    return tuple(contracts)


# Clbits of a heralded n21-orbit-rca member: two phase bits and one herald
# bit per qubit (control and the three work bits).
N21_ORBIT_HERALDED_CLBITS = 6
_N21_WEIGHTS = (0.5, 1.0, 0.5, 0.0)
# A spectator member scores the qubit-2 bit, clbit 1 of the phase register.
_SPECTATOR_ONE = (0.0, 0.0, 1.0, 1.0)


# The overlap split compares bracketed window_delay with bracketed nominal
# and with window_delay without its window barriers (qpe_diagnostics
# variant window_delay_unbarriered). overlap_arm "nominal", the value
# record_groups reads from a configuration that records no overlap_arm,
# pairs nominal with nominal_unbarriered in a ten-member group.
N21_OVERLAP_PAIRS = {
    "window_delay": ("nominal", "window_delay", "window_delay_unbracketed"),
    "nominal": ("nominal", "unbracketed"),
}
N21_OVERLAP_ARM = "window_delay"
_N21_PAIR_BUILDS = {"unbracketed": "nominal_unbarriered", "window_delay_unbracketed": "window_delay_unbarriered"}


def n21_orbit_variants(
    window_sweep: bool = False,
    overlap_split: bool = False,
    overlap_arm: str = N21_OVERLAP_ARM,
    ground_control_split: bool = False,
) -> tuple[str, ...]:
    """The orbit pairs of n21-orbit-rca; window_sweep adds window_delay_long, overlap_split names its pairs.

    ground_control_split holds no orbit pair.
    """
    if ground_control_split:
        return ()
    if overlap_split:
        return N21_OVERLAP_PAIRS[overlap_arm]
    return (*N21_ORBIT_VARIANTS, *(N21_ORBIT_SWEEP_VARIANTS if window_sweep else ()))


def n21_spectator_kinds(overlap_split: bool = False, ground_control_split: bool = False) -> tuple[str, ...]:
    """Spectator kinds of a configuration: the window sweep's, the overlap split's or the ground-control split's."""
    if ground_control_split:
        return N21_SPECTATOR_GROUND_KINDS
    return N21_SPECTATOR_SPLIT_KINDS if overlap_split else N21_SPECTATOR_KINDS


def n21_ramsey_windows(windows: Any) -> tuple[int, ...]:
    """The ground Ramsey sweep's idle multiples, sorted; a non-positive, repeated or empty list raises.

    The sweep needs at least two idle exposures beside immediate's zero to
    fit a decay and a phase slope.
    """
    values = tuple(windows)
    if (
        len(values) < 2
        or any(type(value) is not int or value < 1 for value in values)
        or len(set(values)) != len(values)
    ):
        raise ValueError(f"ramsey_windows needs at least two distinct positive integer multiples, not {values}")
    return tuple(sorted(values))


def n21_segmented_config(config: Any) -> dict[str, Any]:
    """The segmented ground sweep's configuration, validated and in canonical order; anything else raises.

    delays_dt: distinct idles, 0 or at least 2 dt (min_length); segments:
    an even count in [2, N21_SEGMENTED_MAX], so X and Y alternate in pairs;
    backaction_delays_dt: delays among delays_dt that also run with
    backaction_pre_idle_dt (at least 2 dt) between herald and preparation.
    """
    from qpe_diagnostics import N21_SEGMENTED_MAX

    if not isinstance(config, dict) or set(config) != {
        "delays_dt",
        "segments",
        "backaction_delays_dt",
        "backaction_pre_idle_dt",
    }:
        raise ValueError(f"a segmented sweep configuration names delays, segments and its backaction arms: {config}")
    delays = list(config["delays_dt"])
    segments = config["segments"]
    controls = list(config["backaction_delays_dt"])
    pre = config["backaction_pre_idle_dt"]
    if len(delays) < 2 or any(type(d) is not int or d < 0 or d == 1 for d in delays) or len(set(delays)) != len(delays):
        raise ValueError(f"delays_dt needs at least two distinct delays of 0 or >= 2 dt, not {delays}")
    if type(segments) is not int or segments % 2 or not 2 <= segments <= N21_SEGMENTED_MAX:
        raise ValueError(f"segments must be even in [2, {N21_SEGMENTED_MAX}], not {segments!r}")
    if len(set(controls)) != len(controls) or not set(controls) <= set(delays):
        raise ValueError(f"backaction_delays_dt {controls} must be distinct members of delays_dt")
    if controls and (type(pre) is not int or pre < 2):
        raise ValueError(f"backaction_pre_idle_dt must be an integer >= 2 dt with backaction arms, not {pre!r}")
    if not controls and pre != 0:
        raise ValueError("backaction_pre_idle_dt is 0 without backaction arms")
    return {
        "delays_dt": sorted(delays),
        "segments": segments,
        "backaction_delays_dt": sorted(controls),
        "backaction_pre_idle_dt": pre,
    }


def n21_segmented_arms(config: dict[str, Any]) -> tuple[tuple[str, int, int], ...]:
    """(kind, delay_dt, pre_idle_dt) of every segmented arm: xy then z per delay, then the backaction xy arms."""
    checked = n21_segmented_config(config)
    return (
        *((kind, delay, 0) for delay in checked["delays_dt"] for kind in ("xy", "z")),
        *(("xy", delay, checked["backaction_pre_idle_dt"]) for delay in checked["backaction_delays_dt"]),
    )


def n21_spectator_members(
    overlap_split: bool = False, ground_control_split: bool = False, ramsey_windows: tuple[int, ...] = ()
) -> tuple[str, ...]:
    """Member names of the spectator Ramsey arms, kind-major.

    ramsey_windows replaces the ground-control split's idle and idle_ground
    with idle_ground at each idle multiple (n21_ramsey_name) after immediate.
    """
    if ramsey_windows:
        return (
            *(f"n21_spectator_immediate_{quadrature}" for quadrature in N21_SPECTATOR_QUADRATURES),
            *(
                n21_ramsey_name(multiple, quadrature)
                for multiple in n21_ramsey_windows(ramsey_windows)
                for quadrature in N21_SPECTATOR_QUADRATURES
            ),
        )
    return tuple(
        f"n21_spectator_{kind}_{quadrature}"
        for kind in n21_spectator_kinds(overlap_split, ground_control_split)
        for quadrature in N21_SPECTATOR_QUADRATURES
    )


def n21_orbit_rca_group(
    window_delay_dt: int,
    echo_half_dt: int,
    init_herald: bool = False,
    window_sweep: bool = False,
    overlap_split: bool = False,
    reset_dt: int | None = None,
    overlap_arm: str = N21_OVERLAP_ARM,
    ground_control_split: bool = False,
    ramsey_windows: tuple[int, ...] = (),
    segmented: dict[str, Any] | None = None,
) -> Group:
    """Pair feed-forward with its omitted-correction control in each window variant.

    Barriers bracket the control's measurement and reset in every variant, so
    the nominal pair is n21-orbit-feedback with its window bracketed;
    window_delay and extra_readout
    lengthen the measurement window by one readout duration through idling or
    through a second readout; window_echo refocuses static work-qubit
    detuning. Every member keeps the exact labeled law.

    init_herald measures every qubit before the program
    (qpe_diagnostics.n21_orbit_diagnostic). A heralded member's distribution
    spans the phase and herald bits, so its ideal law, weights and contract
    values are the phase vectors lifted onto all six clbits, and the summary
    reads the phase marginal and each herald bit's excited fraction.

    window_sweep adds the window_delay_long pair, which idles the control
    twice window_delay_dt, and the four spectator Ramsey members
    (qpe_diagnostics.n21_spectator_ramsey) on the same logical qubits, whose
    reset_only reference idles window_delay_dt, the control's calibrated
    measure duration (qpu_planning.window_durations), in place of the
    measurement. Every member is dynamic, so the group runs as one job.

    overlap_split replaces the group with twelve members: the bracketed
    nominal and window_delay pairs, the window_delay_unbracketed pair (the
    window_delay program without the window barriers, so the compiler may
    play work-qubit gates during the control's measure and reset), and the
    immediate, idle and reset_only spectators in X and Y; idle idles
    window_delay_dt + reset_dt, the control's calibrated measure and reset
    durations. overlap_arm "nominal" builds the ten-member configuration
    instead: the nominal pair, nominal without its window barriers
    (nominal_unbarriered) and the six spectators. It excludes window_sweep.

    ground_control_split holds six members and no orbit pair: the
    immediate, idle and idle_ground spectators in X and Y. idle_ground is
    idle with the control in |0>, so a ZZ phase to the control becomes a
    fixed rotation of qubit 2 that its X and Y visibility does not see. It
    excludes window_sweep and overlap_split.

    ramsey_windows, with ground_control_split, is the ground Ramsey sweep:
    immediate and idle_ground at each idle multiple m of window_delay_dt +
    reset_dt, in X and Y, with no idle arm, so qubit 2's decay and phase
    slope are read with the control in |0> (n21_spectator_members).

    segmented, with ground_control_split, replaces every spectator arm with
    the segmented ground sweep (qpe_diagnostics.n21_segmented_ramsey):
    an xy and a z arm at each delay of n21_segmented_config and the
    backaction xy arms. Its idles are absolute dt, independent of the
    control's window durations.
    """
    if ramsey_windows and not ground_control_split:
        raise ValueError("ramsey_windows is a ground_control_split configuration")
    if segmented is not None:
        if not ground_control_split or ramsey_windows:
            raise ValueError("segmented is a ground_control_split configuration without ramsey_windows")
        if not init_herald:
            raise ValueError("segmented arms carry their own heralds; the configuration requires init_herald")
        return n21_segmented_group(segmented)
    ramsey = n21_ramsey_windows(ramsey_windows) if ramsey_windows else ()
    if overlap_split and window_sweep:
        raise ValueError("overlap_split and window_sweep are separate n21-orbit-rca configurations")
    if ground_control_split and (window_sweep or overlap_split):
        raise ValueError("ground_control_split excludes window_sweep and overlap_split")
    if (overlap_split or ground_control_split) and (type(reset_dt) is not int or reset_dt <= 0):
        split_name = "ground_control_split" if ground_control_split else "overlap_split"
        raise ValueError(f"{split_name} requires a positive integer reset_dt from calibration")
    if overlap_arm not in N21_OVERLAP_PAIRS:
        raise ValueError(f"unknown overlap arm {overlap_arm!r}")
    variants = n21_orbit_variants(window_sweep, overlap_split, overlap_arm, ground_control_split)
    spectating = window_sweep or overlap_split or ground_control_split
    clbits = N21_ORBIT_HERALDED_CLBITS if init_herald else 2

    def lifted(values: Any) -> np.ndarray:
        return lift_phase_values(values, clbits) if init_herald else np.asarray(values, dtype=float)

    members = tuple(
        Member(
            f"n21_orbit_{variant}_{'feedback' if feedback else 'no_feedback'}",
            n21_orbit_diagnostic(
                feedback,
                _N21_PAIR_BUILDS.get(variant, variant),
                window_delay_dt=window_delay_dt,
                echo_half_dt=echo_half_dt,
                init_herald=init_herald,
            ),
            (
                lift_phase_law(n21_labeled_law(feedback), clbits)
                if init_herald
                else np.asarray(n21_labeled_law(feedback), dtype=float)
            ),
            weights=lifted(_N21_WEIGHTS),
        )
        for variant in variants
        for feedback in (True, False)
    )
    spectator_arms = (
        [("immediate", None)] + [("idle_ground", multiple) for multiple in ramsey]
        if ramsey
        else [(kind, None) for kind in n21_spectator_kinds(overlap_split, ground_control_split)]
    )
    arms = [
        (kind, multiple, quadrature) for kind, multiple in spectator_arms for quadrature in N21_SPECTATOR_QUADRATURES
    ]
    if spectating:
        members += tuple(
            Member(
                name,
                n21_spectator_ramsey(
                    kind,
                    quadrature,
                    measure_dt=window_delay_dt,
                    reset_dt=reset_dt,
                    init_herald=init_herald,
                    idle_multiple=multiple,
                ),
                (
                    lift_phase_law(n21_spectator_law(kind, quadrature), clbits)
                    if init_herald
                    else np.asarray(n21_spectator_law(kind, quadrature), dtype=float)
                ),
                weights=lifted(_SPECTATOR_ONE),
            )
            for (kind, multiple, quadrature), name in zip(
                arms, n21_spectator_members(overlap_split, ground_control_split, ramsey), strict=True
            )
        )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result = {}
        for variant in variants:
            primary = phase_marginal(distributions[f"n21_orbit_{variant}_feedback"])
            control = phase_marginal(distributions[f"n21_orbit_{variant}_no_feedback"])
            result[f"{variant}_feedback_signed_contrast"] = float(primary[1] - primary[3])
            result[f"{variant}_no_feedback_signed_contrast"] = float(control[1] - control[3])
            result[f"{variant}_contrast_difference"] = float(primary[1] - primary[3] - control[1] + control[3])
        if spectating:
            names = n21_spectator_members(overlap_split, ground_control_split, ramsey)
            for pair in range(0, len(names), len(N21_SPECTATOR_QUADRATURES)):
                expectations = []
                stem = names[pair].removeprefix("n21_spectator_").rsplit("_", 1)[0]
                for name in names[pair : pair + len(N21_SPECTATOR_QUADRATURES)]:
                    law = phase_marginal(distributions[name])
                    expectations.append(float(law[0] + law[1] - law[2] - law[3]))
                    result[f"spectator_{name.removeprefix('n21_spectator_')}_expectation"] = expectations[-1]
                result[f"spectator_{stem}_visibility"] = math.hypot(expectations[0], expectations[1])
        if init_herald:
            outcomes = np.arange(1 << clbits)
            for member in members:
                distribution = np.asarray(distributions[member.name], dtype=float)
                for qubit in range(clbits - 2):
                    excited = ((outcomes >> (2 + qubit)) & 1).astype(float)
                    result[f"{member.name.removeprefix('n21_orbit_')}_herald_q{qubit}"] = float(distribution @ excited)
        return result

    return Group("n21_orbit_rca", members, summarize)


def n21_segmented_group(config: dict[str, Any]) -> Group:
    """The segmented ground sweep as one n21_orbit_rca group: one member per n21_segmented_arms entry.

    A member's weights read segment 1's readout bit, so its contract is a
    precision interval on the first read whatever later segments record.
    """
    checked = n21_segmented_config(config)
    segments = checked["segments"]
    read = n21_segment_read_clbits(segments)[0]
    outcomes = np.arange(1 << (3 + 2 * segments))
    first = ((outcomes >> read) & 1).astype(float)
    members = tuple(
        Member(
            n21_segmented_name(kind, delay, pre),
            n21_segmented_ramsey(kind, delay, segments, pre),
            n21_segmented_law(kind, segments),
            weights=first,
        )
        for kind, delay, pre in n21_segmented_arms(checked)
    )
    reads = n21_segment_read_clbits(segments)

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result = {}
        for member in members:
            distribution = np.asarray(distributions[member.name], dtype=float)
            for index, clbit in enumerate(reads):
                one = ((outcomes >> clbit) & 1).astype(float)
                result[f"{member.name.removeprefix('n21_spectator_segmented_')}_s{index + 1}_one"] = float(
                    distribution @ one
                )
        return result

    return Group("n21_orbit_rca", members, summarize)


def family_contracts(
    family: str, precision: float, alpha: float, power: float, configuration: dict[str, Any] | None = None
) -> tuple[ObservableContract, ...]:
    """Simultaneous raw terminal-bit intervals or a directional labeled contrast.

    state-prep-control and measurement-sequence read their qubits from the
    family configuration.
    """
    if family == "et-row":
        from et_campaign import contracts

        return contracts(precision, alpha, power)
    if family == STATE_PREP_FAMILY:
        if configuration is None or not configuration.get("qubits"):
            raise ValueError("state-prep-control contracts need the configuration's named qubits")
        return state_prep_contracts(
            [int(qubit) for qubit in configuration["qubits"]], alpha, power, configuration.get("arms")
        )
    if family == MSQ_FAMILY:
        if configuration is None or not configuration.get("qubits"):
            raise ValueError("measurement-sequence contracts need the configuration's named qubits")
        return measurement_sequence_contracts([int(qubit) for qubit in configuration["qubits"]], alpha, power)
    if family == "folded-correction":
        # The correction collector evaluates four exact-binomial directional
        # bounds on integer counts; bounded-score optimizer inference differs.
        return ()
    if family == "ripple":
        from ripple_contracts import ripple_contracts

        return ripple_contracts(precision, alpha, power)
    if family == "rank-sector":
        from rank_sector_experiments import sector_contracts

        return sector_contracts(precision, alpha, power)
    if family == "patch-window":
        from patch_characterization import PATCH_DELAYS_DT, patch_contracts

        return patch_contracts(list(PATCH_DELAYS_DT), alpha, power)
    if family == "coherence-window":
        from coherence_window import coherence_contracts

        return coherence_contracts(precision, alpha, power)
    if family == "n21-orbit-rca":
        # One directional endpoint per orbit pair and, with window_sweep or
        # overlap_split, one precision-only endpoint per spectator member
        # share the requested family-wise alpha. A heralded member scores its phase label whatever
        # the herald read.
        if (configuration or {}).get("segmented_sweep") is not None:
            # One precision endpoint per segmented arm on its segment-1 read;
            # the preregistered analysis (scripts/n21_q143_segmented_sweep.py)
            # reads every segment.
            group = n21_segmented_group((configuration or {})["segmented_sweep"])
            share = alpha / len(group.members)
            return tuple(
                ObservableContract(
                    f"{member.name}_one",
                    (ObservableTerm(member.name, tuple(float(x) for x in np.asarray(member.weights))),),
                    precision_half_width=precision,
                    alpha=share,
                    power=power,
                )
                for member in group.members
            )
        heralded = bool((configuration or {}).get("init_herald"))
        split = bool((configuration or {}).get("overlap_split"))
        ground = bool((configuration or {}).get("ground_control_split"))
        variants = n21_orbit_variants(
            bool((configuration or {}).get("window_sweep")),
            split,
            str((configuration or {}).get("overlap_arm", "nominal")),
            ground,
        )
        spectators = (
            n21_spectator_members(split, ground, tuple((configuration or {}).get("ramsey_windows", ())))
            if (configuration or {}).get("window_sweep") or split or ground
            else ()
        )

        def scored(values: tuple[float, ...]) -> tuple[float, ...]:
            return (
                tuple(float(value) for value in lift_phase_values(values, N21_ORBIT_HERALDED_CLBITS))
                if heralded
                else values
            )

        signed = scored(_SIGNED)
        share = alpha / (len(variants) + len(spectators))
        directional = tuple(
            ObservableContract(
                f"n21_orbit_{variant}_feedback_contrast",
                (
                    ObservableTerm(f"n21_orbit_{variant}_feedback", signed),
                    ObservableTerm(f"n21_orbit_{variant}_no_feedback", signed, sign=-1),
                ),
                minimum_effect=0.0,
                alpha=share,
                power=power,
            )
            for variant in variants
        )
        # The spectator laws hold no feedback effect; their endpoints ask
        # only for a qubit-2 bit interval of half-width precision.
        return directional + tuple(
            ObservableContract(
                f"{name}_one",
                (ObservableTerm(name, scored(_SPECTATOR_ONE)),),
                precision_half_width=precision,
                alpha=share,
                power=power,
            )
            for name in spectators
        )
    if family in N21_FAMILIES:
        values = _SIGNED
        prefix = N21_PREFIXES[family]
        return (
            ObservableContract(
                f"{prefix}_feedback_contrast",
                (
                    ObservableTerm(f"{prefix}_feedback", values),
                    ObservableTerm(f"{prefix}_no_feedback", values, sign=-1),
                ),
                minimum_effect=0.0,
                alpha=alpha,
                power=power,
            ),
        )
    if family != "folded-qpe":
        raise ValueError(f"unknown diagnostic family {family!r}")
    comparisons = [(rung, label) for rung in ("delay", "no_feed_forward", "coherent") for label in range(4)]
    return tuple(
        ObservableContract(
            f"qpe_{rung}_minus_archived_s{label}",
            (
                ObservableTerm(f"qpe_{rung}_s{label}", folded_terminal_weights(label, rung)),
                ObservableTerm(f"qpe_archived_s{label}", folded_terminal_weights(label, "archived"), sign=-1),
            ),
            precision_half_width=precision,
            alpha=alpha / len(comparisons),
            power=power,
        )
        for rung, label in comparisons
    )


def record_groups(record: dict[str, Any]) -> list[Group]:
    """Reconstruct summaries from the calibration-bound circuit configuration."""
    family = record.get("family_configuration", {})
    if family.get("name") == "et-row":
        from et_campaign import et_group

        return [et_group(family)]
    if family.get("name") == "folded-correction":
        return [correction_group()]
    if family.get("name") == "ripple":
        from ripple_experiments import ripple_groups

        return ripple_groups()
    if family.get("name") == "rank-sector":
        from rank_sector_experiments import sector_groups

        return sector_groups()
    if family.get("name") == "folded-qpe":
        return [
            folded_group(("coherent",)),
            folded_group(
                ("archived", "delay", "no_feed_forward"),
                {int(label): duration for label, duration in family["measurement_delay_dt"].items()},
            ),
        ]
    if family.get("name") == "patch-window":
        from patch_characterization import patch_groups

        return patch_groups(
            [int(delay) for delay in family["delays_dt"]], int(family["measure_dt"]), int(family["echo_half_dt"])
        )
    if family.get("name") == "coherence-window":
        from coherence_window import coherence_groups

        return coherence_groups(int(family["window_dt"]))
    if family.get("name") == "n21-orbit-rca":
        return [
            n21_orbit_rca_group(
                int(family["window_delay_dt"]),
                int(family["echo_half_dt"]),
                bool(family.get("init_herald", False)),
                bool(family.get("window_sweep", False)),
                bool(family.get("overlap_split", False)),
                int(family["reset_dt"]) if "reset_dt" in family else None,
                str(family.get("overlap_arm", "nominal")),
                bool(family.get("ground_control_split", False)),
                tuple(int(multiple) for multiple in family.get("ramsey_windows", ())),
                family.get("segmented_sweep"),
            )
        ]
    if family.get("name") in N21_FAMILIES:
        return [
            n21_group(orbit=family["name"] == "n21-orbit-feedback", encoded=family["name"] == "n21-feedback-encoded")
        ]
    if family.get("name") == STATE_PREP_FAMILY:
        return state_prep_groups([int(qubit) for qubit in family["qubits"]], family.get("arms"))
    if family.get("name") == MSQ_FAMILY:
        return measurement_sequence_groups([int(qubit) for qubit in family["qubits"]], family["measurement_delay_dt"])
    return []


def _state_prep_self_test() -> None:
    """Ideal laws, job kinds, the admitted shot tier, and the exact laws under readout, reset and excitation."""
    from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error

    import dynamic_density
    from local_compute import is_dynamic
    from qpe_diagnostics import ideal_branch_probabilities

    qubits = [57, 65, 66, 67, 68, 69, 70, 104, 105, 106, 107, 117, 125, 126]
    groups = state_prep_groups(qubits)
    if len(groups) != 2 * len(qubits):
        raise AssertionError("each qubit needs one static and one dynamic group")
    for group in [*groups, *state_prep_groups(qubits, (STATE_PREP_HISTORY_ARM,))]:
        kinds = {is_dynamic(member.circuit) for member in group.members}
        dynamic = group.name.startswith(("state_prep_reset_", "state_prep_x_history_"))
        if kinds != {dynamic}:
            raise AssertionError(f"{group.name}: job kind {kinds} differs from its arm")
        for member in group.members:
            law = np.asarray([float(value) for value in ideal_branch_probabilities(member.circuit)])
            if not np.array_equal(law, member.ideal):
                raise AssertionError(f"{member.name}: ideal law {law} differs from {member.ideal}")
    contracts = state_prep_contracts(qubits, 0.05, 0.8)
    if len(contracts) != 3 * len(qubits) or not math.isclose(math.fsum(c.alpha for c in contracts), 0.05):
        raise AssertionError("the endpoints do not split the family-wise alpha over three per qubit")
    share = contracts[0].alpha
    for shots, admitted in ((4096, False), (8192, True)):
        single = math.sqrt(math.log(2 / share) / (2 * shots))
        difference = 2 * math.sqrt(math.log(2 / (share / 2)) / (2 * shots))
        fits = single <= STATE_PREP_PRECISION["excited"] and difference <= STATE_PREP_PRECISION["reset_benefit"]
        if fits is not admitted:
            raise AssertionError(f"{shots} shots: radii {single:.4f}, {difference:.4f} change the admitted tier")
    # One qubit with asymmetric readout, a reset error and an X error.
    e10, e01, reset_flip, x_flip = 0.012, 0.035, 0.004, 0.0007
    noise = NoiseModel(basis_gates=["x", "reset", "measure"])
    noise.add_all_qubit_quantum_error(pauli_error([("X", reset_flip), ("I", 1 - reset_flip)]), ["reset"])
    noise.add_all_qubit_quantum_error(pauli_error([("X", x_flip), ("I", 1 - x_flip)]), ["x"])
    noise.add_readout_error(ReadoutError([[1 - e10, e10], [e01, 1 - e01]]), [0])
    for epsilon in (0.0, 0.01, 0.03):
        laws = {
            arm: dynamic_density.probabilities(state_prep_circuit(arm, 0), noise, prep_excitation=epsilon)
            for arm in STATE_PREP_ARMS
        }
        excited = (1 - epsilon) * e10 + epsilon * (1 - e01)
        after_reset = (1 - reset_flip) * e10 + reset_flip * (1 - e01)
        flipped = (1 - epsilon) * (1 - x_flip) + epsilon * x_flip
        one = flipped * (1 - e01) + (1 - flipped) * e10
        # The model carries no shot history, so x_history reads prep0's law.
        for arm, expected in (("prep0", excited), ("reset", after_reset), ("x", one), ("x_history", excited)):
            if abs(laws[arm][1] - expected) > 1e-15:
                raise AssertionError(f"{arm} at eps {epsilon}: P(1) {laws[arm][1]} != closed form {expected}")
        recovered = state_prep_excitation(float(laws["prep0"][1]), e10, e01)
        if abs(recovered - epsilon) > 1e-14:
            raise AssertionError(f"eps {epsilon}: the excited fraction implies {recovered}")
    for arms, group_count, endpoint_names in (
        (("prep0",), 1, {"excited"}),
        (("x", "prep0"), 1, {"excited", "one_column"}),
        (("prep0", "reset"), 2, {"excited", "reset_benefit"}),
        (("x_history",), 1, {"history_excited"}),
    ):
        subset = state_prep_groups(qubits, arms)
        members = {member.name.split("_q")[0].removeprefix("spc_") for group in subset for member in group.members}
        if len(subset) != group_count * len(qubits) or members != set(arms):
            raise AssertionError(f"arms {arms}: groups {len(subset)} hold {members}")
        chosen = state_prep_contracts(qubits, 0.05, 0.8, arms)
        names = {contract.name.removeprefix("spc_").rsplit("_q", 1)[0] for contract in chosen}
        if names != endpoint_names or not math.isclose(math.fsum(c.alpha for c in chosen), 0.05):
            raise AssertionError(f"arms {arms}: endpoints {names} or the alpha split moved")
    for refused in (
        (),
        ("reset",),
        ("x",),
        ("reset", "x"),
        ("prep0", "prep0"),
        ("prep1",),
        ("x_history", "prep0"),
        ("x_history", "x"),
        ("x_history", "reset"),
        ("x_history", "x_history"),
    ):
        try:
            state_prep_arms(refused)
        except ValueError:
            continue
        raise AssertionError(f"arms {refused} were admitted")
    print(
        f"state-prep-control: {len(qubits)} qubits, {len(contracts)} endpoints at alpha {share:.3g} each, "
        "8192 shots the smallest admitted tier; prep0, reset, x and x_history laws match their closed forms "
        "under readout, reset and X errors and an initial excitation, which the excited fraction recovers; arm "
        "subsets keep the endpoints their arms support, and x_history runs only alone"
    )


def _msq_density_p0(steps: int, sign: int) -> float:
    """Final P0 of the measure arm by density-matrix evolution: rotate, then keep the diagonal, N times."""
    phi = sign * MSQ_THETA / steps
    rotation = np.array([[math.cos(phi / 2), -1j * math.sin(phi / 2)], [-1j * math.sin(phi / 2), math.cos(phi / 2)]])
    rho = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    for _ in range(steps):
        rho = rotation @ rho @ rotation.conj().T
        rho = np.diag(np.diag(rho))
    return float(rho[0, 0].real)


def _msq_unitary_p0(steps: int, sign: int) -> float:
    """Final P0 of the delay arm by unitary evolution of the N rotations."""
    phi = sign * MSQ_THETA / steps
    rotation = np.array([[math.cos(phi / 2), -1j * math.sin(phi / 2)], [-1j * math.sin(phi / 2), math.cos(phi / 2)]])
    state = np.array([1.0, 0.0], dtype=complex)
    for _ in range(steps):
        state = rotation @ state
    return float(abs(state[0]) ** 2)


def _measurement_sequence_self_test() -> None:
    """Ideal laws, job kinds, member order, circuit structure and the admitted shot tier of measurement-sequence."""
    from local_compute import is_dynamic
    from qpe_diagnostics import ideal_branch_probabilities

    for steps in MSQ_STEPS:
        closed = (1.0 + math.cos(MSQ_THETA / steps) ** steps) / 2.0
        law = msq_measure_law(steps)
        if abs(math.fsum(law) - 1.0) > 1e-12 or abs(_msq_final_p0(law) - closed) > 1e-12:
            raise AssertionError(f"n{steps}: the joint law marginalizes to {_msq_final_p0(law)}, not {closed}")
        for sign in (1, -1):
            if abs(_msq_density_p0(steps, sign) - closed) > 1e-12:
                raise AssertionError(f"n{steps} sign {sign}: density-matrix P0 differs from {closed}")
            if abs(_msq_unitary_p0(steps, sign) - msq_delay_p0()) > 1e-12:
                raise AssertionError(f"n{steps} sign {sign}: unitary P0 differs from cos(THETA / 2) ** 2")
        if steps <= 8:
            circuit = msq_circuit("measure", steps, 1, 0, "check", 1)
            branch = np.asarray(ideal_branch_probabilities(circuit))
            if not np.allclose(branch, law, rtol=0, atol=1e-12):
                raise AssertionError(f"n{steps}: the joint law differs from the branch enumeration")
        delay_law = np.asarray(ideal_branch_probabilities(msq_circuit("delay", steps, -1, 0, "check", 1)))
        if not np.allclose(delay_law, [msq_delay_p0(), 1.0 - msq_delay_p0()], rtol=0, atol=1e-12):
            raise AssertionError(f"n{steps}: the delay arm branch law differs from cos(THETA / 2) ** 2")
    table = [round(msq_pinched_p0(steps), 4) for steps in MSQ_STEPS]
    if table != [0.0302, 0.5151, 0.6722, 0.8040, 0.8914] or round(msq_delay_p0(), 4) != 0.0302:
        raise AssertionError(f"the ideal table moved: {table}, delay {msq_delay_p0():.4f}")
    if round(msq_pinched_p0(16) - msq_delay_p0(), 4) != 0.8612:
        raise AssertionError("the N = 16 contrast is not 0.8612")

    qubits = [57, 65, 66, 104]
    delays = {qubit: 1000 + qubit for qubit in qubits}
    groups = measurement_sequence_groups(qubits, delays)
    if len(groups) != 2 * len(qubits):
        raise AssertionError("each qubit needs one static and one dynamic group")
    for group in groups:
        dynamic = group.name.startswith("msq_dynamic_")
        if {is_dynamic(member.circuit) for member in group.members} != {dynamic}:
            raise AssertionError(f"{group.name}: job kind differs from its group")
        for member in group.members:
            if (
                member.weights is None
                or len(member.ideal) != 2**member.circuit.num_clbits
                or len(member.weights) != len(member.ideal)
            ):
                raise AssertionError(f"{member.name}: ideal and weights do not span the clbits")
            branch = member.circuit.count_ops()
            if "delay" in member.name:
                steps = int(member.name.split("_n")[1].split("_")[0])
                if branch.get("measure") != 1 or branch.get("delay") != steps or branch.get("rx") != steps:
                    raise AssertionError(f"{member.name}: delay arm operations {dict(branch)}")
    static_members, dynamic_members = msq_members(57, delays[57])
    expected = [signed[0] + signed[1] for signed in MSQ_SIGNED]
    if (
        expected != ["pa", "ma", "mb", "pb"]
        or len(static_members) != 4 + 4 * len(MSQ_STEPS)
        or len(dynamic_members) != 16
    ):
        raise AssertionError("the member order or counts moved")
    contracts = measurement_sequence_contracts(qubits, 0.05, 0.8)
    if len(contracts) != MSQ_ENDPOINTS_PER_QUBIT * len(qubits) or not math.isclose(
        math.fsum(c.alpha for c in contracts), 0.05
    ):
        raise AssertionError("the endpoints do not split the family-wise alpha over eleven per qubit")
    for count in (1, 4, 14):
        share = 0.05 / (MSQ_ENDPOINTS_PER_QUBIT * count)
        for shots, admitted in ((4096, False), (8192, True)):
            single = math.sqrt(math.log(8 / share) / (2 * shots))
            contrast = 2 * math.sqrt(math.log(16 / share) / (2 * shots))
            fits = single <= MSQ_PRECISION["p0"] and contrast <= MSQ_PRECISION["contrast"]
            if fits is not admitted:
                raise AssertionError(f"{count} qubits, {shots} shots: radii {single:.4f}, {contrast:.4f}")
    print(
        f"measurement-sequence: ideal P0 {table} for N = {list(MSQ_STEPS)} match exact density-matrix evolution to "
        "1e-12, the delay arm matches unitary evolution at cos(THETA / 2) ** 2, the N = 16 contrast is 0.8612; "
        f"{len(contracts)} endpoints on {len(qubits)} qubits, 8192 shots the smallest admitted tier from 1 to 14 qubits"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--self-test", action="store_true", help="check the state-prep-control and measurement-sequence exact laws"
    )
    if parser.parse_args().self_test:
        _state_prep_self_test()
        _measurement_sequence_self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
