"""Retained numerical contracts reject altered samples, probabilities and verdicts."""

import copy

import pytest
from local_simulation_replay import check_photonic, check_qi, load


def test_photonic_replay_rejects_changed_probability() -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json")["rows"][0])
    row["probabilities"]["SLOS"][0] += 0.01
    with pytest.raises(ValueError, match="probability criterion"):
        check_photonic(row)


def test_qi_replay_rejects_changed_sample_denominator() -> None:
    row = copy.deepcopy(load("fullprecision-compiler-crosscheck/qi.json")["rows"][0])
    row["simulations"]["source"]["counts"]["00"] -= 1
    with pytest.raises(ValueError, match="denominator"):
        check_qi((row, True, True))


def test_qi_replay_rejects_changed_verdict() -> None:
    row = copy.deepcopy(load("validated-terminal-unitary-compiler-crosscheck/qi.json")["rows"][8])
    row["passed"] = True
    with pytest.raises(ValueError, match="verdict"):
        check_qi((row, False, True))
