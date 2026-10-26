"""The pinching case's Bloch model agrees with an Aer density-matrix simulation of its own circuits.

Tests that read the retained calibration set carry `audit`; the unmarked tests write a one-qubit calibration here."""

import json
from pathlib import Path

import iqm_measurement_sequence_aer_check as check
import pytest


@pytest.mark.audit
def test_bloch_model_matches_aer() -> None:
    if "agree" not in check.self_test():
        raise AssertionError("the Aer check summary changed")


@pytest.mark.audit
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
    pooled = check.compare(circuits, {qubit: inputs}, calibration, min_items=2)
    monkeypatch.setattr(check, "ordered_map", lambda function, items, min_items: [function(item) for item in items])
    serial = check.compare(circuits, {qubit: inputs}, calibration)
    if pooled != serial or len(pooled) != len(keys):
        raise AssertionError("the pooled comparison differs from the serial one")


def synthetic_calibration(folder: Path) -> check.iqm_sim.Calibration:
    """A one-qubit calibration folder: relaxation times, a prx fidelity and readout errors."""
    qubit = "QB1"
    values = {
        f"characterization.model.{qubit}.t1_time": 4.5e-5,
        f"characterization.model.{qubit}.t2_time": 1.0e-5,
        check.iqm_sim.PRX_FIELD.format(q=qubit): 1 - 5e-4,
        check.iqm_sim.READOUT_FIELD.format(q=qubit, kind="error_0_to_1"): 0.01,
        check.iqm_sim.READOUT_FIELD.format(q=qubit, kind="error_1_to_0"): 0.02,
    }
    (folder / "metrics.json").write_text(
        json.dumps({"observations": [{"dut_field": k, "value": v} for k, v in values.items()]}), encoding="utf-8"
    )
    (folder / "dynamic-quantum-architecture.json").write_text(
        json.dumps({"qubits": [qubit], "calibration_set_id": "synthetic", "gates": {"cz": {"implementations": {}}}}),
        encoding="utf-8",
    )
    return check.iqm_sim.Calibration.from_directory(folder)


def test_comparison_rows_equal_a_direct_serial_simulation_on_a_synthetic_calibration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calibration = synthetic_calibration(tmp_path)
    qubit = "QB1"
    keys = [("measure", 1), ("unitary", 16)]
    monkeypatch.setattr(check.case, "group_keys", lambda: keys)
    circuits = {
        name: check.case.circuit(name, [qubit], arm, n, sign)
        for arm, n in keys
        for name, sign in zip(check.case.group_names(arm, n), check.case.SIGNS, strict=True)
    }
    inputs = {"t1_s": 4.5e-5, "t2_s": 1.0e-5, "prx_p": calibration.prx_p(qubit)}
    rows = check.compare(circuits, {qubit: inputs}, calibration)
    simulator = check.simulator_of(calibration)
    for row in rows:
        names = check.case.group_names(row["arm"], row["n"])
        direct = sum(check.p0_of(circuits[name], qubit, calibration, simulator) for name in names) / len(names)
        if row["simulated"] != direct or abs(row["gap"]) > check.TOLERANCE:
            raise AssertionError(f"{row}: direct {direct}")
    if [(r["arm"], r["n"]) for r in rows] != keys:
        raise AssertionError("the rows lost the serial order")
