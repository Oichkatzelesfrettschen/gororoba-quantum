"""Matched QPE diagnostics with measured-bit observables and explicit inference.

The folded family compares a common terminal bit across two execution kinds.
The N=21 family measures the labeled distribution's response to feed-forward;
two phase bits do not supply an order-recovery experiment. The
state-prep-control family reads each named qubit's excited fraction after
initialization, after an active reset, and after an X, at one repetition
delay; run directly with --self-test it checks the family's exact laws.
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
    N21_ORBIT_VARIANTS,
    folded_diagnostic,
    folded_ideal,
    folded_terminal_weights,
    n21_diagnostic,
    n21_encoded_diagnostic,
    n21_labeled_law,
    n21_orbit_diagnostic,
)

FAMILY_NAMES = (
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
    build = n21_orbit_diagnostic if orbit else n21_encoded_diagnostic if encoded else n21_diagnostic
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
STATE_PREP_FAMILY = "state-prep-control"
STATE_PREP_ARMS = ("prep0", "reset", "x")
STATE_PREP_ARM_STEPS = {"prep0": "init, measure", "reset": "init, reset, measure", "x": "x, measure"}
# The retained n21-feedback-encoded dry run whose R = 2 replica qubits the
# family measures when --layout is absent; repository-relative.
STATE_PREP_SOURCE_RECORD = "results/live/2026-10-17T130242.718497Z/record.json"
# Two-sided half-widths every endpoint must reach at the family-wise alpha
# split over 3 endpoints per qubit. With 14 qubits and alpha 0.05 the
# Hoeffding radius of one PUB is 0.0213 at 8192 shots and 0.0301 at 4096; a
# two-PUB difference takes 0.0445 and 0.0630, so 8192 shots is the smallest
# admitted power-of-two tier.
STATE_PREP_PRECISION = {"excited": 0.025, "reset_benefit": 0.05, "one_column": 0.025}
_EXCITED = (0.0, 1.0)


def state_prep_member(arm: str, qubit: int) -> str:
    return f"spc_{arm}_q{qubit}"


def state_prep_circuit(arm: str, qubit: int) -> QuantumCircuit:
    """One arm on one qubit: init then measure, init-reset-measure, or x then measure."""
    if arm not in STATE_PREP_ARMS:
        raise ValueError(f"unknown state-prep arm {arm!r}")
    circuit = QuantumCircuit(1, 1, name=state_prep_member(arm, qubit))
    if arm == "reset":
        circuit.reset(0)
    elif arm == "x":
        circuit.x(0)
    circuit.measure(0, 0)
    return circuit


def state_prep_arms(arms: Any = None) -> tuple[str, ...]:
    """The selected arms in STATE_PREP_ARMS order; None selects all three, and every selection holds prep0."""
    if arms is None:
        return STATE_PREP_ARMS
    selected = tuple(arms)
    if not selected or len(set(selected)) != len(selected) or set(selected) - set(STATE_PREP_ARMS):
        raise ValueError(f"state-prep arms must be distinct members of {STATE_PREP_ARMS}, got {list(selected)}")
    if "prep0" not in selected:
        raise ValueError("the family measures the initial excited fraction, which only the prep0 arm reads")
    return tuple(arm for arm in STATE_PREP_ARMS if arm in selected)


def state_prep_groups(qubits: list[int], arms: Any = None) -> list[Group]:
    """Per qubit, a static group (prep0, then x) and a dynamic group (reset), each holding its selected arms.

    Fusion joins row r of every group of one kind into one PUB, so PUB A
    measures every qubit's prep0 arm in the same shots, PUB C every x arm,
    and the dynamic PUB B every reset arm.
    """
    if not qubits or len(set(qubits)) != len(qubits) or any(type(q) is not int or q < 0 for q in qubits):
        raise ValueError(f"state-prep-control needs distinct nonnegative qubits, got {qubits}")
    selected = state_prep_arms(arms)
    static_arms = tuple(arm for arm in selected if arm != "reset")
    groups = []
    for qubit in qubits:
        ideal = {"prep0": (1.0, 0.0), "reset": (1.0, 0.0), "x": (0.0, 1.0)}
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

        if static_arms:
            groups.append(Group(f"state_prep_q{qubit}", tuple(members[arm] for arm in static_arms), summarize_static))
        if "reset" in selected:
            groups.append(Group(f"state_prep_reset_q{qubit}", (members["reset"],), summarize_reset))
    return groups


def state_prep_contracts(
    qubits: list[int], alpha: float, power: float, arms: Any = None
) -> tuple[ObservableContract, ...]:
    """Two-sided precision endpoints per qubit for the selected arms, at the family-wise alpha split over all.

    spc_excited_qQ reads P(1) after initialization (residual excitation plus
    readout misassignment); spc_reset_benefit_qQ reads that minus P(1) after
    an active reset, positive where initialization leaves more excitation
    than the reset's own misassignment; spc_one_column_qQ reads P(1) after
    an X, the |1> column of the assignment matrix. Each endpoint needs every
    arm it reads among the selected arms.
    """
    selected = state_prep_arms(arms)
    endpoints = [
        name
        for name, needs in (("excited", {"prep0"}), ("reset_benefit", {"prep0", "reset"}), ("one_column", {"x"}))
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
            )
            if contract.name.removeprefix("spc_").rsplit("_q", 1)[0] in endpoints
        )
    return tuple(contracts)


def state_prep_excitation(excited: float, prob_meas1_prep0: float, prob_meas0_prep1: float) -> float:
    """The initial excitation epsilon an excited fraction implies under a readout channel.

    P(1 | init) = (1 - eps) e10 + eps (1 - e01) with e10 = prob_meas1_prep0 and
    e01 = prob_meas0_prep1, so eps = (P - e10) / (1 - e01 - e10): the value
    dynamic_density's prep_excitation and live_run's --prep-excitation take.
    """
    contrast = 1.0 - prob_meas0_prep1 - prob_meas1_prep0
    if not contrast > 0:
        raise ValueError("the readout channel carries no information about the prepared state")
    return (excited - prob_meas1_prep0) / contrast


def n21_orbit_rca_group(window_delay_dt: int, echo_half_dt: int) -> Group:
    """Pair feed-forward with its omitted-correction control in each window variant.

    The nominal pair repeats n21-orbit-feedback; window_delay and extra_readout
    lengthen the measurement window by one readout duration through idling or
    through a second readout; window_echo refocuses static work-qubit
    detuning. Every member keeps the exact labeled law.
    """
    members = tuple(
        Member(
            f"n21_orbit_{variant}_{'feedback' if feedback else 'no_feedback'}",
            n21_orbit_diagnostic(feedback, variant, window_delay_dt=window_delay_dt, echo_half_dt=echo_half_dt),
            np.asarray(n21_labeled_law(feedback), dtype=float),
            weights=np.asarray((0.5, 1.0, 0.5, 0.0)),
        )
        for variant in N21_ORBIT_VARIANTS
        for feedback in (True, False)
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result = {}
        for variant in N21_ORBIT_VARIANTS:
            primary = distributions[f"n21_orbit_{variant}_feedback"]
            control = distributions[f"n21_orbit_{variant}_no_feedback"]
            result[f"{variant}_feedback_signed_contrast"] = float(primary[1] - primary[3])
            result[f"{variant}_no_feedback_signed_contrast"] = float(control[1] - control[3])
            result[f"{variant}_contrast_difference"] = float(primary[1] - primary[3] - control[1] + control[3])
        return result

    return Group("n21_orbit_rca", members, summarize)


def family_contracts(
    family: str, precision: float, alpha: float, power: float, configuration: dict[str, Any] | None = None
) -> tuple[ObservableContract, ...]:
    """Simultaneous raw terminal-bit intervals or a directional labeled contrast.

    state-prep-control reads its qubits from the family configuration.
    """
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
        # Four directional endpoints share the requested family-wise alpha.
        return tuple(
            ObservableContract(
                f"n21_orbit_{variant}_feedback_contrast",
                (
                    ObservableTerm(f"n21_orbit_{variant}_feedback", _SIGNED),
                    ObservableTerm(f"n21_orbit_{variant}_no_feedback", _SIGNED, sign=-1),
                ),
                minimum_effect=0.0,
                alpha=alpha / len(N21_ORBIT_VARIANTS),
                power=power,
            )
            for variant in N21_ORBIT_VARIANTS
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
        return [n21_orbit_rca_group(int(family["window_delay_dt"]), int(family["echo_half_dt"]))]
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
    for group in groups:
        kinds = {is_dynamic(member.circuit) for member in group.members}
        if kinds != {group.name.startswith("state_prep_reset_")}:
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
        for arm, expected in (("prep0", excited), ("reset", after_reset), ("x", one)):
            if abs(laws[arm][1] - expected) > 1e-15:
                raise AssertionError(f"{arm} at eps {epsilon}: P(1) {laws[arm][1]} != closed form {expected}")
        recovered = state_prep_excitation(float(laws["prep0"][1]), e10, e01)
        if abs(recovered - epsilon) > 1e-14:
            raise AssertionError(f"eps {epsilon}: the excited fraction implies {recovered}")
    for arms, group_count, endpoint_names in (
        (("prep0",), 1, {"excited"}),
        (("x", "prep0"), 1, {"excited", "one_column"}),
        (("prep0", "reset"), 2, {"excited", "reset_benefit"}),
    ):
        subset = state_prep_groups(qubits, arms)
        members = {member.name.split("_q")[0].removeprefix("spc_") for group in subset for member in group.members}
        if len(subset) != group_count * len(qubits) or members != set(arms):
            raise AssertionError(f"arms {arms}: groups {len(subset)} hold {members}")
        chosen = state_prep_contracts(qubits, 0.05, 0.8, arms)
        names = {contract.name.removeprefix("spc_").rsplit("_q", 1)[0] for contract in chosen}
        if names != endpoint_names or not math.isclose(math.fsum(c.alpha for c in chosen), 0.05):
            raise AssertionError(f"arms {arms}: endpoints {names} or the alpha split moved")
    for refused in ((), ("reset",), ("x",), ("reset", "x"), ("prep0", "prep0"), ("prep1",)):
        try:
            state_prep_arms(refused)
        except ValueError:
            continue
        raise AssertionError(f"arms {refused} were admitted")
    print(
        f"state-prep-control: {len(qubits)} qubits, {len(contracts)} endpoints at alpha {share:.3g} each, "
        "8192 shots the smallest admitted tier; prep0, reset and x laws match their closed forms under "
        "readout, reset and X errors and an initial excitation, which the excited fraction recovers; arm "
        "subsets keep the endpoints their arms support"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="check the state-prep-control exact laws")
    if parser.parse_args().self_test:
        _state_prep_self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
