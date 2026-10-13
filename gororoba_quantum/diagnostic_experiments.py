"""Matched QPE diagnostics with measured-bit observables and explicit inference.

The folded family compares a common terminal bit across two execution kinds.
The N=21 family measures the labeled distribution's response to feed-forward;
two phase bits do not supply an order-recovery experiment.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member, tvd
from qpe_diagnostics import (
    N21_ORBIT_VARIANTS,
    folded_diagnostic,
    folded_ideal,
    folded_terminal_weights,
    n21_diagnostic,
    n21_labeled_law,
    n21_orbit_diagnostic,
)

FAMILY_NAMES = (
    "folded-qpe",
    "folded-correction",
    "n21-feedback",
    "n21-orbit-feedback",
    "n21-orbit-rca",
    "ripple",
    "rank-sector",
)
N21_FAMILIES = ("n21-feedback", "n21-orbit-feedback")


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


def n21_group(orbit: bool = False) -> Group:
    """Pair the feed-forward arm with its omitted-correction control.

    orbit selects the multipliers compiled on the orbit of |1>; both variants
    share the exact labeled law, weights, and contrast.
    """
    prefix = "n21_orbit" if orbit else "n21"
    build = n21_orbit_diagnostic if orbit else n21_diagnostic
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


def family_contracts(family: str, precision: float, alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Simultaneous raw terminal-bit intervals or a directional labeled contrast."""
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
        prefix = "n21_orbit" if family == "n21-orbit-feedback" else "n21"
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
    if family.get("name") == "n21-orbit-rca":
        return [n21_orbit_rca_group(int(family["window_delay_dt"]), int(family["echo_half_dt"]))]
    if family.get("name") in N21_FAMILIES:
        return [n21_group(orbit=family["name"] == "n21-orbit-feedback")]
    return []
