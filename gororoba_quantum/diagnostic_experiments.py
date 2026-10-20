"""Matched QPE diagnostics with measured-bit observables and explicit inference.

The folded family compares a common terminal bit across two execution kinds.
The N=21 family measures the labeled distribution's response to feed-forward;
two phase bits do not supply an order-recovery experiment. The
state-prep-control family reads each named qubit's excited fraction after
initialization, after an active reset, and after an X, at one repetition
delay, or alone the excited fraction after shots that end with an X on
the measured state; run
directly with --self-test it checks the family's exact laws.
"""

from __future__ import annotations

import argparse
import math
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member, tvd
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
    """
    if ramsey_windows and not ground_control_split:
        raise ValueError("ramsey_windows is a ground_control_split configuration")
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
        [("immediate", 1)] + [("idle_ground", multiple) for multiple in ramsey]
        if ramsey
        else [(kind, 1) for kind in n21_spectator_kinds(overlap_split, ground_control_split)]
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


def family_contracts(
    family: str, precision: float, alpha: float, power: float, configuration: dict[str, Any] | None = None
) -> tuple[ObservableContract, ...]:
    """Simultaneous raw terminal-bit intervals or a directional labeled contrast.

    state-prep-control reads its qubits from the family configuration.
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
            )
        ]
    if family.get("name") in N21_FAMILIES:
        return [
            n21_group(orbit=family["name"] == "n21-orbit-feedback", encoded=family["name"] == "n21-feedback-encoded")
        ]
    if family.get("name") == STATE_PREP_FAMILY:
        return state_prep_groups([int(qubit) for qubit in family["qubits"]], family.get("arms"))
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="check the state-prep-control exact laws")
    if parser.parse_args().self_test:
        _state_prep_self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
