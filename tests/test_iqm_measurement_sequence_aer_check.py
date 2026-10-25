"""The pinching case's Bloch model agrees with an Aer density-matrix simulation of its own circuits."""

import iqm_measurement_sequence_aer_check as check


def test_bloch_model_matches_aer() -> None:
    if "agree" not in check.self_test():
        raise AssertionError("the Aer check summary changed")
