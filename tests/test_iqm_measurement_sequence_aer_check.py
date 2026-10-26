"""The pinching case's Bloch model agrees with an Aer density-matrix simulation of its own circuits."""

import iqm_measurement_sequence_aer_check as check
import pytest


def test_bloch_model_matches_aer() -> None:
    if "agree" not in check.self_test():
        raise AssertionError("the Aer check summary changed")


def test_pooled_comparison_equals_the_serial_one(monkeypatch: pytest.MonkeyPatch) -> None:
    calibration = check.iqm_sim.Calibration.from_directory(check.case.CALIBRATION_DIR)
    qubit = "QB1"
    keys = [("measure", 1), ("unitary", 16)]
    monkeypatch.setattr(check.case, "group_keys", lambda: keys)
    circuits = {
        name: check.case.circuit(name, [qubit], arm, n, sign)
        for arm, n in keys
        for name, sign in zip(check.case.group_names(arm, n), check.case.SIGNS, strict=True)
    }
    inputs = {
        "t1_s": calibration.values[f"characterization.model.{qubit}.t1_time"],
        "t2_s": calibration.values[f"characterization.model.{qubit}.t2_time"],
        "prx_p": calibration.prx_p(qubit),
    }
    pooled = check.compare(circuits, {qubit: inputs}, calibration)
    monkeypatch.setattr(check, "ordered_map", lambda function, items: [function(item) for item in items])
    serial = check.compare(circuits, {qubit: inputs}, calibration)
    if pooled != serial or len(pooled) != len(keys):
        raise AssertionError("the pooled comparison differs from the serial one")
