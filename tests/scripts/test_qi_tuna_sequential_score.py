"""Exercise the prospective job-level destination response scoring contract."""

from __future__ import annotations

from fractions import Fraction

import pytest


def test_exact_one_slot_mixture_and_direction() -> None:
    """Catch a reversed treatment sign or an incorrect mixture weight."""
    from qi_tuna_sequential_score import score_sequence

    result = score_sequence([{"slot": 1, "arm": "rotated", "kind": "complete", "early_ones": 4096, "terminal_ones": 0}])
    if result["processes"]["early_positive"]["value"] != Fraction(39, 20):
        raise AssertionError("a rotated one fraction must increase the positive process to 39/20")
    if result["processes"]["early_negative"]["value"] != Fraction(1, 20):
        raise AssertionError("the opposing process must retain its half-stake component")
    if result["processes"]["terminal_positive"]["value"] != Fraction(1, 20):
        raise AssertionError("the terminal response must have an independent score")


def test_neutral_failure_stops_and_rejects_following_slot() -> None:
    """Catch silent replacement or post-failure continuation of a scored slot."""
    from qi_tuna_sequential_score import score_sequence

    neutral = {"slot": 1, "arm": "baseline", "kind": "unavailable"}
    result = score_sequence([neutral])
    if result["stop_reason"] != "unavailable" or any(p["value"] != 1 for p in result["processes"].values()):
        raise AssertionError("an unavailable slot must contribute neutral factors and stop")
    with pytest.raises(ValueError, match="after stop"):
        score_sequence([neutral, {"slot": 2, "arm": "rotated", "kind": "unavailable"}])


def test_crossing_is_recorded_before_shared_stop() -> None:
    """Catch loss of first crossing or dispatch after both responses cross."""
    from qi_tuna_sequential_score import score_sequence

    rows = [
        {"slot": slot, "arm": "rotated", "kind": "complete", "early_ones": 4096, "terminal_ones": 4096}
        for slot in range(1, 10)
    ]
    result = score_sequence(rows)
    if result["stop_reason"] != "both_observables_crossed":
        raise AssertionError("nine maximal positive scores cross 400 for both responses")
    if result["processes"]["early_positive"]["first_crossing"] != 9:
        raise AssertionError("the first exact threshold crossing must be retained")
    with pytest.raises(ValueError, match="after stop"):
        score_sequence([*rows, {"slot": 10, "arm": "rotated", "kind": "unavailable"}])


@pytest.mark.parametrize(
    ("difference", "slots", "expected_stop"),
    [(Fraction(1, 4), 24, "slot_limit"), (Fraction(1, 2), 16, "both_observables_crossed")],
)
def test_symmetric_constant_response_has_exact_evidence_trajectory(
    difference: Fraction, slots: int, expected_stop: str
) -> None:
    from qi_tuna_sequential_score import score_sequence

    rows = []
    for slot in range(1, slots + 1):
        rotated = slot % 2 == 0
        fraction = Fraction(1, 2) + (difference / 2 if rotated else -difference / 2)
        exact_count = 4096 * fraction
        if exact_count.denominator != 1:
            raise AssertionError("illustrative response is not an attainable shot count")
        count = exact_count.numerator
        rows.append(
            {
                "slot": slot,
                "arm": "rotated" if rotated else "baseline",
                "kind": "complete",
                "early_ones": count,
                "terminal_ones": count,
            }
        )
    for prefix_length in range(1, slots + 1):
        result = score_sequence(rows[:prefix_length])
        expected = (
            Fraction(9, 10) * (1 + difference) ** prefix_length
            + Fraction(1, 10) * (1 + difference / 2) ** prefix_length
        )
        for response in ("early", "terminal"):
            process = result["processes"][f"{response}_positive"]
            expected_crossing = 16 if difference == Fraction(1, 2) and prefix_length == 16 else None
            if process["value"] != expected or process["first_crossing"] != expected_crossing:
                raise AssertionError("symmetric constant response differs from its exact evidence trajectory")
        if result["stop_reason"] != (expected_stop if prefix_length == slots else None):
            raise AssertionError("symmetric constant response stopped at the wrong position")


def test_slot_and_count_validation_rejects_ambiguous_values() -> None:
    """Catch duplicate slots, malformed counts, and non-neutral failure payloads."""
    from qi_tuna_sequential_score import score_sequence

    for row in (
        {"slot": True, "arm": "baseline", "kind": "complete", "early_ones": 0, "terminal_ones": 0},
        {"slot": 1, "arm": "baseline", "kind": "complete", "early_ones": True, "terminal_ones": 0},
        {"slot": 1, "arm": "baseline", "kind": "complete", "early_ones": 4097, "terminal_ones": 0},
        {"slot": 1, "arm": "baseline", "kind": "unavailable", "early_ones": 0},
        {"slot": 2, "arm": "baseline", "kind": "unavailable"},
        {"slot": 1, "arm": [], "kind": "unavailable"},
        {"slot": 1, "arm": "baseline", "kind": []},
    ):
        with pytest.raises(ValueError):
            score_sequence([row])


def test_running_max_survives_zero_factor_and_later_recovery() -> None:
    """Catch a lost crossing or discarded smaller-stake product after a zero factor."""
    from qi_tuna_sequential_score import score_sequence

    rows = [
        {"slot": slot, "arm": "rotated", "kind": "complete", "early_ones": 4096, "terminal_ones": 2048}
        for slot in range(1, 10)
    ]
    rows.extend(
        [
            {"slot": 10, "arm": "rotated", "kind": "complete", "early_ones": 0, "terminal_ones": 2048},
            {"slot": 11, "arm": "rotated", "kind": "complete", "early_ones": 4096, "terminal_ones": 2048},
        ]
    )
    process = score_sequence(rows)["processes"]["early_positive"]
    if process["first_crossing"] != 9 or process["maximum"] != Fraction(2378979, 5120):
        raise AssertionError("the running maximum must retain the first crossing after a zero factor")
    if process["value"] != Fraction(59049, 20480):
        raise AssertionError("the half-stake product must survive a full-stake zero and recover")


def test_decode_uses_assigned_destination_and_terminal_bit() -> None:
    """Catch swapped early destinations or reversed bit-string indexing."""
    from qi_tuna_sequential_score import decode_counts

    # Leftmost is bit 19; bit 18 is the next character; bit 6 is offset 13.
    baseline = "1" + "0" * 12 + "1" + "0" * 6
    rotated = "01" + "0" * 18
    if decode_counts("baseline", [baseline] * 4096) != {"early_ones": 4096, "terminal_ones": 4096}:
        raise AssertionError("baseline must decode bit 19 early and bit 6 terminal")
    if decode_counts("rotated", [rotated] * 4096) != {"early_ones": 4096, "terminal_ones": 0}:
        raise AssertionError("rotated must decode bit 18 early and bit 6 terminal")
    if decode_counts("baseline", [rotated] * 4096)["early_ones"] != 0:
        raise AssertionError("baseline must not read the rotated early destination")
    terminal_only = "0" * 13 + "1" + "0" * 6
    baseline_only = "1" + "0" * 19
    for arm in ("baseline", "rotated"):
        if decode_counts(arm, [terminal_only] * 4096) != {"early_ones": 0, "terminal_ones": 4096}:
            raise AssertionError("terminal decoding must be independent of both early destinations")
        if decode_counts(arm, [baseline_only] * 4096)["terminal_ones"] != 0:
            raise AssertionError("an early destination alone must not produce terminal ones")
    for invalid in ([baseline] * 4095, ["2" + baseline[1:]] * 4096, [baseline[:-1]] * 4096):
        with pytest.raises(ValueError):
            decode_counts("baseline", invalid)


def test_exact_threshold_between_adjacent_counts() -> None:
    """Catch rounding two adjacent attainable values onto the wrong side of 400."""
    from qi_tuna_sequential_score import score_sequence

    prefix = [
        {"slot": slot, "arm": "rotated", "kind": "complete", "early_ones": 4096, "terminal_ones": 4096}
        for slot in range(1, 9)
    ]
    lower = score_sequence(
        [*prefix, {"slot": 9, "arm": "rotated", "kind": "complete", "early_ones": 3524, "terminal_ones": 3524}]
    )
    upper = score_sequence(
        [*prefix, {"slot": 9, "arm": "rotated", "kind": "complete", "early_ones": 3525, "terminal_ones": 3525}]
    )
    if (
        lower["processes"]["early_positive"]["value"] != Fraction(1048409361, 2621440)
        or lower["stop_reason"] is not None
    ):
        raise AssertionError("the lower adjacent count is below the exact threshold")
    if (
        upper["processes"]["early_positive"]["value"] != Fraction(4194823653, 10485760)
        or upper["stop_reason"] != "both_observables_crossed"
    ):
        raise AssertionError("the upper adjacent count is above the exact threshold")


def test_slot_limit_stops_a_non_crossing_campaign() -> None:
    """Catch an implicit conclusion from a non-crossing or a twenty-fifth slot."""
    from qi_tuna_sequential_score import score_sequence

    rows = [
        {"slot": slot, "arm": "baseline", "kind": "complete", "early_ones": 2048, "terminal_ones": 2048}
        for slot in range(1, 25)
    ]
    result = score_sequence(rows)
    if result["stop_reason"] != "slot_limit" or any(
        process["first_crossing"] is not None or process["value"] != 1 for process in result["processes"].values()
    ):
        raise AssertionError("24 neutral complete responses must end inconclusively at the slot limit")
    with pytest.raises(ValueError):
        score_sequence([*rows, {"slot": 25, "arm": "baseline", "kind": "unavailable"}])


def test_baseline_scores_each_direction_and_response() -> None:
    """Catch an unflipped baseline assignment or a neutralized terminal process."""
    from qi_tuna_sequential_score import score_sequence

    result = score_sequence(
        [{"slot": 1, "arm": "baseline", "kind": "complete", "early_ones": 0, "terminal_ones": 4096}]
    )
    expected = {
        "early_positive": Fraction(39, 20),
        "early_negative": Fraction(1, 20),
        "terminal_positive": Fraction(1, 20),
        "terminal_negative": Fraction(39, 20),
    }
    if {name: process["value"] for name, process in result["processes"].items()} != expected:
        raise AssertionError("the baseline arm must flip both independent directional scores")


@pytest.mark.parametrize("kind", ["confirmed_failure", "partial", "unavailable"])
def test_each_neutral_class_stops_without_changing_processes(kind: str) -> None:
    """Catch omission or non-neutral scoring of a specified failure classification."""
    from qi_tuna_sequential_score import score_sequence

    result = score_sequence([{"slot": 1, "arm": "rotated", "kind": kind}])
    if result["stop_reason"] != kind or any(process["value"] != 1 for process in result["processes"].values()):
        raise AssertionError("every defined neutral classification must score one and stop")


@pytest.mark.parametrize("first_response", ["early", "terminal"])
def test_single_observable_crossing_does_not_stop(first_response: str) -> None:
    """Catch a shared-stop rule that ignores either observable."""
    from qi_tuna_sequential_score import score_sequence

    rows = [
        {
            "slot": slot,
            "arm": "rotated",
            "kind": "complete",
            "early_ones": 4096 if first_response == "early" else 2048,
            "terminal_ones": 4096 if first_response == "terminal" else 2048,
        }
        for slot in range(1, 10)
    ]
    result = score_sequence(rows)
    if result["stop_reason"] is not None or result["processes"][f"{first_response}_positive"]["first_crossing"] != 9:
        raise AssertionError("a crossing of only one observable must leave the other eligible")
