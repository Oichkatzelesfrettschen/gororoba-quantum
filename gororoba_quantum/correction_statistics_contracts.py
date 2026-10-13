"""Credential-free count, decision, and finite-power checks for correction statistics.

Run normally and with Python optimization enabled. Explicit failures preserve
the validation contract when the interpreter removes assert statements.
"""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Callable
from functools import partial
from typing import Any, cast
from unittest.mock import patch

import numpy as np
from scipy.stats import beta

import correction_statistics as statistics


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _invalid(operation: Callable[[], Any]) -> None:
    try:
        operation()
    except ValueError:
        return
    raise RuntimeError("invalid input was accepted")


def _fixture() -> dict[str, list[int]]:
    return {
        "correction_measured_s1": [0, 700, 0, 300],
        "correction_known_s1": [0, 950, 0, 50],
        "correction_known_s3": [0, 50, 0, 950],
        "correction_measured_s3": [0, 300, 0, 700],
    }


def _check_decisions() -> None:
    counts = _fixture()
    original = copy.deepcopy(counts)
    result = statistics.analyze_counts(counts, 1000)
    _require(counts == original, "analysis modified input counts")
    _require(result["admit_known_correction"], "strong labeled improvement was rejected")
    _require(result["per_bound_tail"] == 0.0125, "four-bound alpha allocation changed")
    _require(all(row["gain_estimate"] == 0.25 for row in result["comparisons"]), "terminal counts changed")
    _require(
        all(
            strata[0]["shots"] == 0 and strata[0]["terminal_success_probability"] is None
            for strata in result["descriptive_recorded_first_bit_strata"].values()
        ),
        "empty strata must retain missing probability",
    )
    json.dumps(result, allow_nan=False)
    permuted = {name: [histogram[index] for index in (0, 2, 1, 3)] for name, histogram in counts.items()}
    _require(
        not statistics.analyze_counts(permuted, 1000)["admit_known_correction"],
        "first/terminal bit swap escaped the labeled decision",
    )
    first_bit_flipped = {name: [histogram[index] for index in (1, 0, 3, 2)] for name, histogram in counts.items()}
    _require(
        statistics.analyze_counts(first_bit_flipped, 1000)["comparisons"] == result["comparisons"],
        "descriptive first-bit selection changed the unconditional decision",
    )
    one_label_fails = copy.deepcopy(counts)
    one_label_fails["correction_known_s3"] = one_label_fails["correction_measured_s3"][:]
    failed = statistics.analyze_counts(one_label_fails, 1000)
    _require(
        failed["comparisons"][0]["passes_minimum_gain"] and not failed["admit_known_correction"],
        "the family admitted an improvement in only one label",
    )
    threshold = result["comparisons"][0]["gain_lower_bound"]
    _require(
        not statistics.analyze_counts(counts, 1000, minimum_gain=threshold)["admit_known_correction"],
        "strict threshold accepted equality",
    )
    _require(
        statistics.analyze_counts(counts, 1000, minimum_gain=math.nextafter(threshold, -math.inf))[
            "admit_known_correction"
        ],
        "strict threshold rejected an immediately smaller margin",
    )


def _check_boundaries() -> None:
    tail = 0.0125
    for shots in (1, 2, 20, 1000):
        _require(statistics._lower(0, shots, tail) == 0, "zero-success lower endpoint changed")
        _require(statistics._upper(shots, shots, tail) == 1, "all-success upper endpoint changed")
        _require(
            math.isclose(statistics._lower(shots, shots, tail), tail ** (1 / shots), abs_tol=2e-15),
            "all-success lower endpoint differs from the exact beta identity",
        )
        _require(
            math.isclose(statistics._upper(0, shots, tail), -math.expm1(math.log(tail) / shots), abs_tol=2e-15),
            "zero-success upper endpoint differs from the exact beta identity",
        )
    shots = 20
    for probability in (0.0, 0.01, 0.125, 0.5, 0.875, 0.99, 1.0):
        probabilities = [
            math.comb(shots, count) * probability**count * (1 - probability) ** (shots - count)
            for count in range(shots + 1)
        ]
        lower_failure = math.fsum(
            mass for count, mass in enumerate(probabilities) if statistics._lower(count, shots, tail) > probability
        )
        upper_failure = math.fsum(
            mass for count, mass in enumerate(probabilities) if statistics._upper(count, shots, tail) < probability
        )
        _require(max(lower_failure, upper_failure) <= tail + 1e-14, "finite binomial coverage exceeded its tail")
    extreme = {
        "correction_measured_s1": [0, 0, 0, 1000],
        "correction_known_s1": [0, 1000, 0, 0],
        "correction_known_s3": [0, 0, 0, 1000],
        "correction_measured_s3": [0, 1000, 0, 0],
    }
    _require(statistics.analyze_counts(extreme, 1000)["admit_known_correction"], "boundary counts were rejected")


def _check_invalid_inputs() -> None:
    counts = _fixture()
    for shots in (True, False, 0, -1, 1000.0, "1000", statistics.MAX_EXACT_FLOAT_INTEGER + 1):
        _invalid(partial(statistics.analyze_counts, counts, cast(Any, shots)))
    for alpha in (True, 0, -0.1, 1, float("nan"), float("inf"), "0.05", 5e-324):
        _invalid(partial(statistics.analyze_counts, counts, 1000, alpha=cast(Any, alpha)))
    for margin in (True, -0.1, 1, float("nan"), float("inf"), "0.01"):
        _invalid(partial(statistics.analyze_counts, counts, 1000, minimum_gain=cast(Any, margin)))
    invalid_mappings: tuple[Any, ...] = (None, [], {1: [0, 700, 0, 300]})
    for invalid in invalid_mappings:
        _invalid(partial(statistics.analyze_counts, invalid, 1000))
    missing = copy.deepcopy(counts)
    del missing[statistics.MEMBERS[0]]
    _invalid(partial(statistics.analyze_counts, missing, 1000))
    extra = counts | {"unexpected": [0, 1000, 0, 0]}
    _invalid(partial(statistics.analyze_counts, extra, 1000))
    for vector in (
        [True, 699, 0, 300],
        [0, 700.0, 0, 300],
        [0, -1, 0, 1001],
        [0, 700, 0, 299],
        [0, 1000],
        [[0, 700, 0, 300]],
        np.array([0, 700, 0, 300]),
        None,
        [0, float("nan"), 0, 300],
    ):
        malformed: dict[str, Any] = counts | {statistics.MEMBERS[0]: vector}
        _invalid(partial(statistics.analyze_counts, malformed, 1000))
    _invalid(partial(statistics.analyze_counts, counts, 999))
    for shots in (True, 0, -1, 8192.0, statistics.MAX_PLANNING_SHOTS + 1):
        _invalid(partial(statistics.planning_certificate, cast(Any, shots)))
    for gain in (True, float("nan"), float("inf"), 0.3, -0.9):
        _invalid(partial(statistics.planning_certificate, 20, assumed_gain=gain))
    for power in (True, 0, 1, float("nan"), float("inf")):
        _invalid(partial(statistics.planning_certificate, 20, required_joint_power=power))
    with patch("correction_statistics.beta.ppf", return_value=float("nan")):
        _invalid(partial(statistics.analyze_counts, counts, 1000))
    with patch("correction_statistics.binom.pmf", return_value=np.zeros(21)):
        _invalid(partial(statistics.planning_certificate, 20))


def _check_power() -> None:
    shots, tail, margin = 20, 0.0125, 0.01
    required, _ = statistics._thresholds(shots, tail, margin)
    for measured_probability, known_probability in ((0.2, 0.9), (0.0, 1.0), (1.0, 0.0), (0.5, 0.5)):
        full_terms = []
        for measured_count in range(shots + 1):
            measured_upper = (
                1 if measured_count == shots else beta.isf(tail, measured_count + 1, shots - measured_count)
            )
            for known_count in range(shots + 1):
                known_lower = 0 if known_count == 0 else beta.ppf(tail, known_count, shots - known_count + 1)
                if known_lower - measured_upper > margin:
                    full_terms.append(
                        math.comb(shots, measured_count)
                        * measured_probability**measured_count
                        * (1 - measured_probability) ** (shots - measured_count)
                        * math.comb(shots, known_count)
                        * known_probability**known_count
                        * (1 - known_probability) ** (shots - known_count)
                    )
        optimized = statistics._power(shots, measured_probability, known_probability, required)["power"]
        _require(math.isclose(optimized, math.fsum(full_terms), abs_tol=2e-14), "finite power differs from brute force")
    expected = {
        (4096, 0.03): (0.1755392901466377, 0.153472754116934),
        (4096, 0.04): (0.5927598193379399, 0.5372500050001695),
        (8192, 0.03): (0.5057477521949441, 0.4550846090533802),
        (8192, 0.04): (0.9520579067241106, 0.9285428776880107),
    }
    for (shot_count, gain), values in expected.items():
        certificate = statistics.planning_certificate(shot_count, assumed_gain=gain)
        json.dumps(certificate, allow_nan=False)
        for row, expected_power in zip(certificate["comparisons"], values, strict=True):
            _require(math.isclose(row["power"], expected_power, abs_tol=2e-12), "reference planning power changed")
            _require(
                row["summed_terms"] == shot_count + 1 and row["deliberately_truncated_terms"] == 0,
                "planning discarded count support",
            )
        _require(
            certificate["hypothetical_power_qualified"] == (shot_count == 8192 and gain == 0.04),
            "planning admission differs from the joint power requirement",
        )
    for gain in (-0.01, 0.0, 0.01):
        rejected = statistics.planning_certificate(20, assumed_gain=gain)
        _require(
            not rejected["hypothetical_power_qualified"] and bool(rejected["rejection_reasons"]),
            "insufficient hypothetical gain must retain rejection reasons",
        )
    impossible = statistics.planning_certificate(1)
    _require(impossible["joint_power_union_lower_bound"] == 0, "impossible small-sample decision gained power")


def main() -> None:
    _check_decisions()
    _check_boundaries()
    _check_invalid_inputs()
    _check_power()
    print("Correction statistics: labeled counts, CP boundaries, invalid inputs, and full finite power verified")


if __name__ == "__main__":
    main()
