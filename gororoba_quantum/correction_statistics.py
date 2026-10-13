"""Exact-binomial decisions for the two known-label correction witnesses.

The decision uses integer shot counts and four directional Clopper-Pearson
bounds. Planning uses a hypothetical gain over retained reference rates;
the planning certificate establishes neither a hardware-model prediction nor
permission to execute a quantum job. SciPy evaluates quantiles and tails in
floating point; exact-binomial describes the statistical construction.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import scipy
from scipy.stats import beta, binom

MEMBERS = (
    "correction_measured_s1",
    "correction_known_s1",
    "correction_known_s3",
    "correction_measured_s3",
)
REFERENCE_SUCCESSES = {1: 6433, 3: 6241}
REFERENCE_SHOTS = 8192
MAX_PLANNING_SHOTS = 1_000_000
MAX_EXACT_FLOAT_INTEGER = 2**53 - 1
NUMERICAL_METHOD = (
    "SciPy beta quantiles and binomial tails in float64; math.fsum aggregation; "
    "floating-point rounding is not interval-certified"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _real(value: Any, name: str) -> float:
    _require(type(value) in (int, float), f"{name} must be a finite real number, excluding bool")
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} exceeds finite floating-point range") from error
    _require(math.isfinite(result), f"{name} must be finite")
    return result


def _shots(value: Any, name: str, maximum: int = MAX_EXACT_FLOAT_INTEGER) -> int:
    _require(type(value) is int and 0 < value <= maximum, f"{name} must be an integer in [1, {maximum}]")
    return int(value)


def _parameters(alpha: float, minimum_gain: float) -> tuple[float, float, float]:
    family_alpha = _real(alpha, "alpha")
    margin = _real(minimum_gain, "minimum_gain")
    _require(0 < family_alpha < 1, "alpha must lie in (0, 1)")
    _require(0 <= margin < 1, "minimum_gain must lie in [0, 1)")
    tail = family_alpha / 4
    _require(tail > 0, "alpha/4 underflows")
    return family_alpha, margin, tail


def _lower(successes: int, shots: int, tail: float) -> float:
    value = 0.0 if successes == 0 else float(beta.ppf(tail, successes, shots - successes + 1))
    _require(math.isfinite(value) and 0 <= value <= successes / shots, "invalid lower CP bound")
    return value


def _upper(successes: int, shots: int, tail: float) -> float:
    value = 1.0 if successes == shots else float(beta.isf(tail, successes + 1, shots - successes))
    _require(math.isfinite(value) and successes / shots <= value <= 1, "invalid upper CP bound")
    return value


def _terminal_successes(histogram: Sequence[int], label: int) -> int:
    return sum(count for outcome, count in enumerate(histogram) if outcome >> 1 == label >> 1)


def analyze_counts(
    counts: Mapping[str, Sequence[int]],
    expected_shots: int,
    alpha: float = 0.05,
    minimum_gain: float = 0.01,
) -> dict[str, Any]:
    """Analyze all four raw histograms in y = first_bit + 2*terminal_bit order.

    Each member supplies exactly one list or tuple of four integer counts.
    The procedure uses raw Bernoulli trials, without readout correction,
    replica pooling, supplied-label substitution, or conditional postselection.
    Missing or malformed observations raise ValueError instead of a decision.
    """
    shots = _shots(expected_shots, "expected_shots")
    family_alpha, margin, tail = _parameters(alpha, minimum_gain)
    _require(isinstance(counts, Mapping), "counts must be a mapping")
    _require(all(type(name) is str for name in counts), "member names must be strings")
    _require(set(counts) == set(MEMBERS), "counts must contain exactly the four correction members")
    for name in MEMBERS:
        histogram = counts[name]
        _require(
            isinstance(histogram, (list, tuple)) and len(histogram) == 4, f"{name}: expected one four-count vector"
        )
        _require(all(type(count) is int and count >= 0 for count in histogram), f"{name}: invalid integer count")
        _require(sum(histogram) == shots, f"{name}: count total differs from expected_shots")
    comparisons = []
    for label in (1, 3):
        measured_member = f"correction_measured_s{label}"
        known_member = f"correction_known_s{label}"
        measured_successes = _terminal_successes(counts[measured_member], label)
        known_successes = _terminal_successes(counts[known_member], label)
        measured_upper = _upper(measured_successes, shots, tail)
        known_lower = _lower(known_successes, shots, tail)
        lower_gain = known_lower - measured_upper
        comparisons.append(
            {
                "label": label,
                "measured_member": measured_member,
                "known_member": known_member,
                "shots_per_arm": shots,
                "measured_successes": measured_successes,
                "known_successes": known_successes,
                "gain_estimate": (known_successes - measured_successes) / shots,
                "measured_upper_bound": measured_upper,
                "known_lower_bound": known_lower,
                "gain_lower_bound": lower_gain,
                "passes_minimum_gain": lower_gain > margin,
            }
        )
    descriptive = {}
    for name in MEMBERS:
        label = int(name[-1])
        strata = []
        for first_bit in (0, 1):
            stratum_shots = sum(counts[name][outcome] for outcome in range(4) if outcome & 1 == first_bit)
            successes = sum(
                counts[name][outcome] for outcome in range(4) if outcome & 1 == first_bit and outcome >> 1 == label >> 1
            )
            strata.append(
                {
                    "recorded_first_bit": first_bit,
                    "shots": stratum_shots,
                    "terminal_successes": successes,
                    "terminal_success_probability": successes / stratum_shots if stratum_shots else None,
                }
            )
        descriptive[name] = strata
    admitted = all(row["passes_minimum_gain"] for row in comparisons)
    return {
        "schema": 1,
        "method": "four_one_sided_clopper_pearson_bounds",
        "alpha": family_alpha,
        "per_bound_tail": tail,
        "minimum_gain": margin,
        "decision_rule": "known_lower - measured_upper > minimum_gain for both labels",
        "admit_known_correction": admitted,
        "decision": "admit_known_label_correction" if admitted else "retain_measured_correction",
        "comparisons": comparisons,
        "descriptive_recorded_first_bit_strata": descriptive,
        "scope": "known-label odd witnesses s1 and s3; circuit and schedule conformance require separate checks",
        "assumptions": [
            "independent stationary Bernoulli repetitions within each PUB",
            "four directional bounds have family failure probability at most alpha by a union bound",
            "dependence between PUBs is unrestricted for the observation bounds",
            "descriptive first-bit strata supply neither additional inferential claims nor causal attribution",
            "failure to admit establishes neither equivalence nor absence of improvement",
        ],
        "numerical_method": NUMERICAL_METHOD,
    }


def _thresholds(shots: int, tail: float, margin: float) -> tuple[np.ndarray, float]:
    counts = np.arange(shots + 1)
    lower = np.zeros(shots + 1)
    lower[1:] = beta.ppf(tail, counts[1:], shots - counts[1:] + 1)
    upper = np.ones(shots + 1)
    upper[:-1] = beta.isf(tail, counts[:-1] + 1, shots - counts[:-1])
    _require(bool(np.isfinite(lower).all() and np.isfinite(upper).all()), "planning CP limits must be finite")
    _require(bool(((0 <= lower) & (lower <= upper) & (upper <= 1)).all()), "planning CP limits outside [0, 1]")
    _require(bool((np.diff(lower) >= 0).all() and (np.diff(upper) >= 0).all()), "planning CP limits lost monotonicity")
    required = np.searchsorted(lower, upper + margin, side="right")
    # Match the collector's subtraction comparison at a floating-point boundary.
    for measured_count, first_admitted in enumerate(required):
        threshold = int(first_admitted)
        while threshold <= shots and lower[threshold] - upper[measured_count] <= margin:
            threshold += 1
        while threshold > 0 and lower[threshold - 1] - upper[measured_count] > margin:
            threshold -= 1
        required[measured_count] = threshold
    gaps = []
    for measured_count, threshold_value in enumerate(required):
        threshold = int(threshold_value)
        for known_count in (threshold - 1, threshold):
            if 0 <= known_count <= shots:
                gaps.append(abs(float(lower[known_count] - upper[measured_count] - margin)))
    return required, min(gaps)


def _power(shots: int, measured_probability: float, known_probability: float, required: np.ndarray) -> dict[str, Any]:
    counts = np.arange(shots + 1)
    mass = binom.pmf(counts, shots, measured_probability)
    tail_probabilities = binom.sf(required - 1, shots, known_probability)
    _require(bool(np.isfinite(mass).all() and np.isfinite(tail_probabilities).all()), "nonfinite binomial evaluation")
    _require(
        bool(((0 <= mass) & (mass <= 1) & (0 <= tail_probabilities) & (tail_probabilities <= 1)).all()),
        "binomial probability outside [0, 1]",
    )
    total_mass = math.fsum(map(float, mass))
    _require(abs(total_mass - 1) <= 1e-12, "binomial PMF mass residual exceeds 1e-12")
    power = math.fsum(float(weight) * float(tail) for weight, tail in zip(mass, tail_probabilities, strict=True))
    _require(-1e-12 <= power <= 1 + 1e-12, "calculated power outside numerical probability tolerance")
    return {
        "power": min(1.0, max(0.0, power)),
        "unclipped_power": power,
        "pmf_mass_residual": total_mass - 1,
        "summed_terms": shots + 1,
        "deliberately_truncated_terms": 0,
    }


def planning_certificate(
    shots: int,
    alpha: float = 0.05,
    minimum_gain: float = 0.01,
    assumed_gain: float = 0.04,
    required_joint_power: float = 0.8,
) -> dict[str, Any]:
    """Price statistical sensitivity under an explicit hypothetical alternative.

    Enumerating all count values takes O(shots) memory and work apart from the
    library's quantile evaluation. The bounded domain caps that allocation.
    Reference rates are scenario constants, without a stationarity or transfer
    claim from the retained run to a future device calibration.
    """
    shot_count = _shots(shots, "shots", MAX_PLANNING_SHOTS)
    family_alpha, margin, tail = _parameters(alpha, minimum_gain)
    gain = _real(assumed_gain, "assumed_gain")
    target_power = _real(required_joint_power, "required_joint_power")
    _require(0 < target_power < 1, "required_joint_power must lie in (0, 1)")
    probabilities = {label: successes / REFERENCE_SHOTS for label, successes in REFERENCE_SUCCESSES.items()}
    _require(all(0 <= probability + gain <= 1 for probability in probabilities.values()), "assumed gain leaves [0, 1]")
    required, threshold_gap = _thresholds(shot_count, tail, margin)
    comparisons = []
    for label, probability in probabilities.items():
        comparisons.append(
            {
                "label": label,
                "reference_successes": REFERENCE_SUCCESSES[label],
                "reference_shots": REFERENCE_SHOTS,
                "hypothetical_measured_probability": probability,
                "hypothetical_known_probability": probability + gain,
                **_power(shot_count, probability, probability + gain, required),
            }
        )
    joint_lower = max(0.0, 1 - math.fsum(1 - row["power"] for row in comparisons))
    feasible = gain > margin and joint_lower >= target_power
    reasons = []
    if gain <= margin:
        reasons.append("hypothetical gain does not exceed the required minimum gain")
    if joint_lower < target_power:
        reasons.append("hypothetical joint power lower bound is below the requested power")
    return {
        "schema": 1,
        "method": "full_finite_binomial_power_for_four_CP_bounds",
        "evidence_class": "HYPOTHETICAL planning scenario; not a modeled or measured advantage",
        "shots_per_pub": shot_count,
        "pub_count": 4,
        "alpha": family_alpha,
        "per_bound_tail": tail,
        "minimum_gain": margin,
        "assumed_gain": gain,
        "required_joint_power": target_power,
        "joint_power_union_lower_bound": joint_lower,
        "hypothetical_power_qualified": feasible,
        "rejection_reasons": reasons,
        "comparisons": comparisons,
        "minimum_decision_grid_distance_to_margin": threshold_gap,
        "power_formula": "sum_j BinPMF(j;n,p_measured) * BinSF(r(j)-1;n,p_known), j=0,...,n",
        "threshold_formula": "r(j)=min{k: L(k,n)-U(j,n)>minimum_gain}; r=n+1 when the set is empty",
        "assumptions": [
            "reference F rates 6433/8192 and 6241/8192 are fixed scenario values from already inspected evidence",
            "the assumed gain is hypothetical and supplies neither a fresh model prediction nor independent validation",
            "binomial product power adds independence between measured and known arms within each label",
            "the joint-power union bound requires no independence between labels",
            "prospective decision data must come from a fresh acquisition after freezing the design",
            "hypothetical power qualification alone supplies neither complete run admission nor execution approval",
        ],
        "numerical_method": NUMERICAL_METHOD,
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__},
    }
