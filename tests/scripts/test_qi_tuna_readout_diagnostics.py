"""Exact readout diagnostics preserve bit order and distinguish relabeling from response failure."""

from typing import Any

import numpy as np
import pytest
from qi_tuna_readout_diagnostics import EARLY, FILES, FINAL, arm_diagnostics, audit, joint_counts, summarize


def shot(bits: tuple[int, ...]) -> str:
    return "".join(str(int(bit in bits)) for bit in reversed(range(20)))


def test_joint_orientation_and_conditioning() -> None:
    first = np.array([0, 0, 0, 1, 1, 1, 1], dtype=np.int64)
    second = np.array([0, 1, 1, 0, 0, 0, 1], dtype=np.int64)
    if joint_counts(first, second) != [[1, 2], [3, 1]]:
        raise AssertionError("early and terminal axes exchanged")
    row = arm_diagnostics((FILES[0], [shot(()), shot((4,)), shot((17,)), shot((17, 4))], 2))
    pair = row["early_final"][0]
    if pair["joint_counts"] != [[1, 1], [1, 1]] or pair["final_one_given_early_zero"] != [1, 2]:
        raise AssertionError("conditional counts or little-endian bit decoding differs")
    if pair["block_disagreement_counts"] != [1, 1]:
        raise AssertionError("contiguous blocks must preserve order")


def test_covariance_and_lag_match_scalar_counts() -> None:
    shots = [shot(()), shot((4, 17)), shot((4,)), shot((17,))] * 2
    row = arm_diagnostics((FILES[0], shots, 4))
    bits = [[int(value) for value in value[::-1]] for value in shots]
    for left in range(20):
        for right in range(20):
            expected = len(bits) * sum(value[left] * value[right] for value in bits)
            expected -= sum(value[left] for value in bits) * sum(value[right] for value in bits)
            if row["within_shot_covariance_numerators"][left][right] != expected:
                raise AssertionError("matrix covariance differs from scalar formula")
    lag = row["lag_statistics"][0]
    if lag["pairs"] != 7 or lag["both_one_counts"][4] != 2 or lag["covariance_numerators"][4] != -2:
        raise AssertionError("lag-one statistics include the wrong endpoint")


def test_zero_condition_is_explicit() -> None:
    row = arm_diagnostics((FILES[0], [shot(())] * 4, 2))
    if row["early_final"][0]["final_one_given_early_one"] != [0, 0]:
        raise AssertionError("undefined conditioning must preserve the zero denominator")


@pytest.mark.parametrize("shots,block", [([], 2), (["0" * 19] * 2, 2), (["x" * 20] * 2, 2), (["0" * 20] * 3, 2)])
def test_invalid_record(shots: list[str], block: int) -> None:
    with pytest.raises(ValueError):
        arm_diagnostics((FILES[0], shots, block))


def test_signed_permutation_can_identify_a_pure_label_flip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    arms = [
        arm_diagnostics((FILES[0], [shot((17,))] * 4, 2)),
        arm_diagnostics((FILES[1], [shot(tuple(FINAL) + (18, 19))] * 4, 2)),
        arm_diagnostics((FILES[2], [shot((17,))] * 4, 2)),
    ]
    report = summarize(arms)
    if report["signed_permutation_count"] != 48 or not report["any_signed_permutation_passes_assignment"]:
        raise AssertionError("all six permutations and eight fixed sign choices must be examined")
    if not report["any_signed_permutation_passes_disagreement"] or report["best_maximum_disagreement_count"] != 0:
        raise AssertionError("a pure early-bit inversion should have an exact diagnostic repair")


def test_retained_failure_is_not_a_signed_permutation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    result = audit()
    comparison = result["comparison"]
    if result["frozen_qualification_passed"]:
        raise AssertionError("diagnostics must retain the failed qualification")
    if (
        comparison["any_signed_permutation_passes_assignment"]
        or comparison["any_signed_permutation_passes_disagreement"]
    ):
        raise AssertionError("a signed permutation cannot repair the retained response")
    expected = [1552, -2529, -508]
    if [comparison["contrast_numerators_by_classical_bit"][bit] for bit in EARLY] != expected:
        raise AssertionError("independent early contrasts differ from raw counts")
    pair: dict[str, Any] = result["arms"][0]["early_final"][1]
    if pair["joint_counts"] != [[46, 11], [3937, 102]]:
        raise AssertionError("prepared-zero q11 joint response changed")
