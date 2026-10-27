"""Qualification binds the frozen case and rejects incomplete or misdecoded evidence."""

import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from qi_tuna_qualification import FILES, MANIFEST_SHA256, ROOT, SHOTS, replay, screen, shot_counts, validate_metadata


@pytest.fixture
def run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    source = ROOT / "results/quantum_inspire/proposals/tuna-projector-geometry/tuna-qualification"
    for filename in (*FILES, "cases.json"):
        shutil.copyfile(source / filename, tmp_path / filename)
    (tmp_path / "raw").mkdir()
    manifest = json.loads((tmp_path / "cases.json").read_text())
    submitted = []
    collected = []
    for index, entry in enumerate(manifest["circuits"]):
        filename = entry["file"]
        shots = [("1" if filename == "readout-one.cq" else "0") * 20] * SHOTS
        (tmp_path / "raw" / f"{filename}.json").write_text(json.dumps(shots))
        submitted.append({"file": filename, "job": index + 1, "sha256": entry["sha256"]})
        collected.append(
            {
                "file": filename,
                "job": {
                    "id": index + 1,
                    "batch_job_id": 99,
                    "status": "completed",
                    "number_of_shots": SHOTS,
                    "raw_data_enabled": True,
                },
                "results": [
                    {
                        "job_id": index + 1,
                        "shots_requested": SHOTS,
                        "shots_done": SHOTS,
                        "execution_time_in_seconds": 5,
                        "results": dict(Counter(shots)),
                    }
                ],
            }
        )
    (tmp_path / "submission.json").write_text(
        json.dumps(
            {
                "state": "enqueued",
                "backend_type_id": 7,
                "backend": "tuna_17",
                "shots": SHOTS,
                "cases_sha256": MANIFEST_SHA256,
                "jobs": submitted,
                "batch_job": 99,
            }
        )
    )
    (tmp_path / "results.json").write_text(json.dumps({"jobs": collected, "transactions": []}))
    return tmp_path


def test_complete_case(run: Path) -> None:
    report = replay(run)
    if not report["passed"] or len(report["assignment_contrasts"]) != 20 or report["execution_seconds_decimal"] != "15":
        raise AssertionError("complete qualification should pass, including modest estimate overrun")
    if sum(row["required"] for row in report["assignment_contrasts"]) != 12:
        raise AssertionError("nine active terminal and three early bits must gate admission")


@pytest.mark.parametrize("defect", ["missing", "partial", "identity", "histogram", "time", "charge", "duplicate"])
def test_collection_defects(run: Path, defect: str) -> None:
    path = run / "results.json"
    data = json.loads(path.read_text())
    if defect == "missing":
        data["jobs"].pop()
    elif defect == "partial":
        data["jobs"][0]["results"][0]["shots_done"] -= 1
    elif defect == "identity":
        data["jobs"][0]["job"]["batch_job_id"] += 1
    elif defect == "histogram":
        data["jobs"][0]["results"][0]["results"] = {"0" * 20: 4095}
    elif defect == "time":
        data["jobs"][0]["results"][0]["execution_time_in_seconds"] = "NaN"
    elif defect == "charge":
        data["transactions"] = [{"id": 1, "job": 1, "change": -1}, {"id": 2, "job": 1, "change": 1}]
    else:
        data["jobs"][1] = data["jobs"][0]
    path.write_text(json.dumps(data))
    if defect == "charge":
        if replay(run)["passed"]:
            raise AssertionError("offsetting transactions cannot establish zero recorded charges")
    else:
        with pytest.raises(ValueError):
            replay(run)


@pytest.mark.parametrize("shots", [["0" * 19] * SHOTS, ["x" * 20] * SHOTS, ["0" * 20] * (SHOTS - 1)])
def test_malformed_shots(shots: list[str]) -> None:
    with pytest.raises(ValueError):
        shot_counts((FILES[0], shots))


def test_bit_map(run: Path) -> None:
    metadata = json.loads((run / "cases.json").read_text())["circuits"][0]["analysis_metadata"]
    metadata["replicas"][0]["herald"] = 17
    with pytest.raises(ValueError, match="bit map"):
        validate_metadata(metadata)


def test_exact_thresholds() -> None:
    counts: dict[str, dict[str, Any]] = {
        FILES[0]: {"ones": [0] * 20, "disagreements": [0] * 3},
        FILES[1]: {"ones": [2048] * 20, "disagreements": [409] * 3},
        FILES[2]: {"ones": [0] * 20, "disagreements": [0] * 3},
    }
    if not screen(counts)["passed"]:
        raise AssertionError("contrast exactly one half and 409/4096 disagreement must pass")
    counts[FILES[1]]["ones"][18] = 2047
    if screen(counts)["passed"]:
        raise AssertionError("contrast below one half must fail")
    counts[FILES[1]]["ones"][18] = 2048
    counts[FILES[2]]["disagreements"][0] = 410
    if screen(counts)["passed"]:
        raise AssertionError("410/4096 disagreement must fail")


def test_order_bound_by_raw_digest(run: Path) -> None:
    path = run / "raw" / f"{FILES[2]}.json"
    shots = ["0" * 20, "1" * 20] * (SHOTS // 2)
    path.write_text(json.dumps(shots))
    result_path = run / "results.json"
    data = json.loads(result_path.read_text())
    data["jobs"][2]["results"][0]["results"] = dict(Counter(shots))
    result_path.write_text(json.dumps(data))
    before = replay(run)
    path.write_text(json.dumps(list(reversed(shots))))
    after = replay(run)
    if before["inputs"] == after["inputs"]:
        raise AssertionError("equal histograms with reordered shots must change replay binding")
