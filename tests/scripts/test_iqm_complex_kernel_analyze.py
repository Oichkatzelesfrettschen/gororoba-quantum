"""The run reader of the A_5 complex kernel case on a synthetic run built from the case's own predicted laws."""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from typing import Any

import iqm_complex_kernel_analyze as reader
import pytest

import iqm_records

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "results/iqm/cases/a5-complex-kernel-garnet"
KEPT = 2000


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def rows_of(law: list[float], width: int) -> list[list[int]]:
    """Shot rows (bit c of the outcome at position c) holding each outcome in proportion to its law."""
    out: list[list[int]] = []
    for index, p in enumerate(law):
        out += [[(index >> c) & 1 for c in range(width)]] * round(p * KEPT)
    return out


GARNET_ID = json.loads((ROOT / "docs/evidence/iqm/qc/garnet/details.json").read_text(encoding="utf-8"))["id"]


def make_run(
    tmp_path: Path,
    *,
    qc: str = "garnet",
    mutate: Any = None,
    calibration: str | None = None,
    job: dict[str, Any] | None = None,
    shape: Any = None,
) -> Path:
    run = tmp_path / "run"
    (run / "raw").mkdir(parents=True)
    shutil.copytree(CASE_DIR / "circuits", run / "circuits")
    for name in ("cases.json", "prediction.json"):
        shutil.copyfile(CASE_DIR / name, run / name)
    pred = json.loads((run / "prediction.json").read_text(encoding="utf-8"))
    case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    measurements = []
    for position, entry in enumerate(case["jobs"][0]["circuits"]):
        operand, kind, orientation, _ = Path(entry["file"]).stem.split("-")
        width = pred["operands"][operand]["block"]["data_qubits"] + 1
        law = pred["operands"][operand]["kinds"][kind]["law"][orientation]
        if shape is not None:
            uniform = 1.0 / len(law)
            law = [uniform + shape(position) * (p - uniform) for p in law]
        measurements.append({"m": rows_of(law, width)})
    if mutate is not None:
        mutate(measurements)
    raw = {
        "job.json": {
            "id": "job-1",
            "status": "completed",
            "qc": {"id": GARNET_ID},
            "compilation": {"calibration_set_id": calibration or pred["calibration_set"]},
            "metrics": {"billed_seconds": 9, "runtime_seconds": 8.5},
            **(job or {}),
        },
        "measurements.json": measurements,
        "measurement_counts.json": [],
    }
    digests = {}
    for name, value in raw.items():
        data = json.dumps(value).encode()
        (run / "raw" / name).write_bytes(data)
        digests[name] = iqm_records.sha256(data)
    (run / "results.json").write_text(
        json.dumps(
            {
                "schema": iqm_records.RESULTS_SCHEMA,
                "job_id": "job-1",
                "status": "completed",
                "raw_sha256": digests,
                "shots_per_circuit": [len(next(iter(m.values()))) for m in measurements],
            }
        ),
        encoding="utf-8",
    )
    (run / "submission.json").write_text(
        json.dumps(
            {
                "schema": iqm_records.SUBMISSION_SCHEMA,
                "approval": "test",
                "cases_sha256": iqm_records.sha256((run / "cases.json").read_bytes()),
                "job": "kernel",
                "job_id": "job-1",
                "qc": qc,
                "submitted_at": "2026-11-28T00:00:00Z",
                "price_per_second": 0.5,
            }
        ),
        encoding="utf-8",
    )
    return run


def test_run_at_the_predicted_laws_reads_complex_strata(tmp_path: Path) -> None:
    result = reader.analyze_run(make_run(tmp_path))
    analysis = result["analysis"]
    require(analysis["verdict"] == "complex strata within tolerance" and analysis["null_resolved"])
    for name, n_c in (("s016", 16.0), ("s412", 12.0), ("s124", 4.0)):
        require(abs(analysis["subtracted"][name]["n_c"] - n_c) < 0.5)
    require(result["billed_seconds"] == 9.0 and 0.0 < result["kept_fraction"] <= 1.0)
    require(all(abs(z) < 5 for z in result["half_to_half_z"].values()))
    require(abs(result["inner_outer_z"]) < 5)


def test_run_that_swaps_the_real_and_complex_circuits_reads_real_strata(tmp_path: Path) -> None:
    def swap(measurements: list[dict[str, Any]]) -> None:
        names = [Path(e["file"]).stem for e in json.loads((CASE_DIR / "cases.json").read_text())["jobs"][0]["circuits"]]
        index = {n: i for i, n in enumerate(names)}
        for name in names:
            operand, kind, orientation, copy = name.split("-")
            if kind == "real":
                other = index[f"{operand}-cplx-{orientation}-{copy}"]
                measurements[index[name]], measurements[other] = measurements[other], measurements[index[name]]

    require(
        reader.analyze_run(make_run(tmp_path, mutate=swap))["analysis"]["verdict"] == "real strata within tolerance"
    )


def test_mock_run_is_refused(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, qc="garnet:mock"))


def test_run_compiled_against_another_calibration_set_is_refused(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, calibration="00000000-0000-0000-0000-000000000000"))


def test_run_with_a_changed_prediction_is_refused(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "prediction.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(run)


def test_garnet_and_its_mock_have_different_quantum_computer_ids() -> None:
    servers = json.loads((ROOT / "docs/evidence/iqm/server/quantum-computers.json").read_text(encoding="utf-8"))
    rows = servers if isinstance(servers, list) else servers.get("quantum_computers", servers)
    ids = {row["alias"]: row["id"] for row in rows if isinstance(row, dict) and "alias" in row}
    require(ids["garnet"] == GARNET_ID and ids["garnet:mock"] != GARNET_ID)


def test_run_whose_job_record_names_another_quantum_computer_is_refused(tmp_path: Path) -> None:
    run = make_run(tmp_path, job={"qc": {"id": "00000000-0000-0000-0000-000000000000"}})
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(run)


def test_run_with_a_non_binary_shot_value_is_refused(tmp_path: Path) -> None:
    def corrupt(measurements: list[dict[str, Any]]) -> None:
        measurements[0]["m"][0][0] = 2

    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, mutate=corrupt))


def test_run_with_a_circuit_missing_its_measurement_key_is_refused(tmp_path: Path) -> None:
    def rename(measurements: list[dict[str, Any]]) -> None:
        measurements[0] = {"other": measurements[0]["m"]}

    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, mutate=rename))


def test_run_without_a_compilation_record_is_refused(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, job={"compilation": None}))


def test_run_of_zero_variance_shots_reports_no_reading_without_crashing(tmp_path: Path) -> None:
    def zeros(measurements: list[dict[str, Any]]) -> None:
        for circuit in measurements:
            circuit["m"] = [[0] * len(row) for row in circuit["m"]]

    result = reader.analyze_run(make_run(tmp_path, mutate=zeros))
    require("complex strata" not in result["analysis"]["verdict"])
    require(all(z is None or isinstance(z, float) for z in result["half_to_half_z"].values()))


@pytest.mark.parametrize("width", [4.0, 12.0])
def test_a_dip_symmetric_about_the_center_is_caught_by_the_sentinel_and_missed_by_the_halves(
    tmp_path: Path, width: float
) -> None:
    """The mirrored order makes every kind's two quads equidistant from the center, so a drift symmetric about the
    center leaves the half-to-half z at zero; the sentinel at the center against the outer null circuit sees it."""

    def dip(position: int) -> float:
        return 1.0 - 0.3 * math.exp(-(((position - 39.5) / width) ** 2))

    result = reader.analyze_run(make_run(tmp_path, shape=dip))
    require(abs(result["half_to_half_z"]["s808-sent"]) < 1.0)
    require(abs(result["inner_outer_z"]) >= 5.0)
    require("complex strata" not in result["analysis"]["verdict"])
