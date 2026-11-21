"""The packed Pauli Garnet case builds, round-trips through check and analyzes bounded synthetic runs."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from fractions import Fraction
from pathlib import Path

import iqm_packed_pauli_case as case
import iqm_sim
import pytest

CALIBRATION = iqm_sim.EVIDENCE / case.QC / "calibration"


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    directory = tmp_path_factory.mktemp("packed-pauli") / "case"
    case.write(directory, CALIBRATION)
    yield directory


def test_build_round_trips_and_binds_the_prediction(built: Path) -> None:
    case.check(built)
    cases = case.json.loads((built / "cases.json").read_text(encoding="utf-8"))
    job = cases["jobs"][0]
    _check(
        len(job["circuits"]) == 36 and job["shots"] == 2000, f"{len(job['circuits'])} circuits, {job['shots']} shots"
    )
    _check(job["options"]["heralding_mode"] == "none" and job["options"]["active_reset_cycles"] == 1, "options")
    _check(job["max_credits"]["garnet:mock"] == 0.0 and 0 < job["max_credits"]["garnet"] <= 24, job["max_credits"])
    _check(cases["prediction_sha256"] == case.sha256((built / "prediction.json").read_bytes()), "unbound prediction")
    last = case.json.loads((built / job["circuits"][2]["file"]).read_text(encoding="utf-8"))["instructions"]
    _check(last[-1]["name"] == "measure" and len(last[-1]["locus"]) == 20, "no joint twenty-qubit measure")
    barriers = [op for op in last if op["name"] == "barrier"]
    _check(len(barriers) == 1 and len(barriers[0]["locus"]) == 20, f"barriers {barriers}")


def test_check_rejects_an_edited_circuit(built: Path, tmp_path: Path) -> None:
    copy = tmp_path / "copy"
    shutil.copytree(built, copy)
    victim = copy / "circuits" / "circuit-002.json"
    victim.write_text(victim.read_text(encoding="utf-8").replace('"prx"', '"prx "', 1), encoding="utf-8")
    with pytest.raises(case.CaseError, match="differs from the build"):
        case.check(copy)


def test_null_device_gives_no_rejection(built: Path, tmp_path: Path) -> None:
    primary = case.analyze(case.synthetic_run(built, tmp_path / "run", "null"))["primary"]
    _check(Fraction(primary["p_value"]) == 1 and not primary["reject_at_0.05"], f"{primary}")
    _check(primary["pairs"] == 16 and set(primary["numerator_2g_dense_minus_sparse"]) == {0}, f"{primary}")


def test_balanced_pair_differences_give_no_rejection(built: Path, tmp_path: Path) -> None:
    primary = case.analyze(case.synthetic_run(built, tmp_path / "run", "alternating"))["primary"]
    _check(any(primary["numerator_2g_dense_minus_sparse"]), "the fixture planted no difference")
    _check(not primary["reject_at_0.05"], f"{primary}")


def test_planted_dense_minus_sparse_response_is_rejected(built: Path, tmp_path: Path) -> None:
    primary = case.analyze(case.synthetic_run(built, tmp_path / "run", "planted"))["primary"]
    _check(Fraction(primary["p_value"]) <= Fraction(1, 128), f"p = {primary['p_value']}")
    _check(primary["mean_difference"] < 0, f"mean difference {primary['mean_difference']}")


def test_mock_run_is_refused(built: Path, tmp_path: Path) -> None:
    run = case.synthetic_run(built, tmp_path / "run", "null", qc="garnet:mock")
    with pytest.raises(case.CaseError, match="not a"):
        case.analyze(run)


def test_swap_off_locus_cz_routing_and_off_map_layout_are_refused() -> None:
    calibration = iqm_sim.Calibration.from_directory(CALIBRATION)
    proposal, _ = case.load_proposal()
    case.refusal_checks(calibration, proposal["physical_map_to_be_applied_by_native_compiler"])


def test_altered_proposal_circuit_is_refused(tmp_path: Path) -> None:
    copy = tmp_path / "proposal"
    shutil.copytree(case.PROPOSAL, copy)
    (copy / "circuit-007.qasm").write_text("OPENQASM 2.0;\n", encoding="utf-8")
    with pytest.raises(case.CaseError, match="differs from the sha256"):
        case.load_proposal(copy)
