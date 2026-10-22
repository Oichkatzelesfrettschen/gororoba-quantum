"""Photonic readout keeps the eligible denominator and acquisition identity explicit."""

import pytest
from photonic_repeat_readout import observation


def test_readout_excludes_vacuum_and_multiple_clicks_without_losing_their_counts() -> None:
    row = observation(
        {
            "name": "control-repeat-0",
            "repeat_index": 0,
            "setting": {"name": "control"},
            "operator": {"real": [[1, 0], [0, 1]], "imaginary": [[0, 0], [0, 0]]},
            "circuit_params": {"x0": 0.5},
        },
        {
            "iteration": {"circuit_params": {"x0": 0.5}},
            "counts": {"1,0": 8, "0,1": 2, "0,0": 3, "1,1": 1},
            "samples": 14,
            "result_fields": {"computed_circuit": "retained mesh", "physical_perf": 0.03},
        },
        2,
    )
    if row["eligible_samples"] != 10 or row["excluded_samples"] != 4:
        raise RuntimeError("the one-click denominator must exclude vacuum and multi-click observations explicitly")
    if row["mode_counts"] != [8, 2] or row["mode_probabilities"] != [0.8, 0.2]:
        raise RuntimeError("the eligible detector counts must determine the conditional probabilities")
    if row["expected_mode_probabilities"] != [1.0, 0.0]:
        raise RuntimeError("the submitted operator must determine the ideal reference")


def test_readout_refuses_a_service_parameter_echo_that_changes_the_case() -> None:
    with pytest.raises(ValueError, match="echo"):
        observation({"circuit_params": {"x0": 0.5}}, {"iteration": {"circuit_params": {"x0": 0.7}}}, 2)
