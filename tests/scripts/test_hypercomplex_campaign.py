"""Frozen campaign plans bind every batch before the provider runner is reached."""

import hashlib
import json

import pytest
from hypercomplex_campaign import analyze_batch, campaign_plan, execute, measured_wave
from hypercomplex_cases import qi_cases, write_files


def test_plan_hashes_and_execution_approval(tmp_path) -> None:
    write_files(tmp_path, qi_cases(16384))
    plan = campaign_plan(tmp_path)
    if plan["batch_count"] != 8 or plan["circuits"] != 24 or plan["shots_total"] != 393216:
        raise RuntimeError("the isolated pilot must retain all eight calibrated settings")
    with pytest.raises(ValueError, match="approval"):
        execute(tmp_path, "", "", 0)
    batch = next(tmp_path.glob("*/cases.json"))
    record = json.loads(batch.read_text())
    record["circuits"].append(record["circuits"][0])
    batch.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="three"):
        campaign_plan(tmp_path)


def test_hardware_analysis_checks_manifest_identity_before_reading_shots(tmp_path) -> None:
    import qi_platform

    write_files(tmp_path, qi_cases(16))
    batch = next(tmp_path.glob("*/cases.json")).parent
    (batch / "submission.json").write_text(
        json.dumps({"schema": qi_platform.SUBMISSION_SCHEMA, "cases_sha256": "0" * 64})
    )
    with pytest.raises(qi_platform.PlatformError, match="digest"):
        analyze_batch(batch)
    with pytest.raises(ValueError, match="seventeen"):
        measured_wave(tmp_path)


def test_output_readout_gate_follows_swapped_layout(tmp_path) -> None:
    import qi_platform

    write_files(tmp_path, qi_cases(16, "wave"))
    batch = next(
        path.parent
        for path in tmp_path.glob("*/cases.json")
        if json.loads(path.read_text())["circuits"][2]["measurement_mapping"] == [1, 0, 2]
    )
    manifest_path = batch / "cases.json"
    manifest = json.loads(manifest_path.read_text())
    receipt = {
        "schema": qi_platform.SUBMISSION_SCHEMA,
        "state": "enqueued",
        "cases_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        **{key: manifest[key] for key in ("backend", "backend_type_id", "shots")},
        "jobs": [
            {"file": row["file"], "sha256": row["sha256"], "job": index + 1}
            for index, row in enumerate(manifest["circuits"])
        ],
    }
    (batch / "submission.json").write_text(json.dumps(receipt))
    raw = batch / "raw"
    raw.mkdir()
    for row in manifest["circuits"]:
        (raw / f"{row['file']}.json").write_text(json.dumps(["000"] * 16))
    high = raw / "readout-1.cq.json"
    high.write_text(json.dumps(["110"] * 16))
    with pytest.raises(ValueError, match="contrast"):
        analyze_batch(batch)
    high.write_text(json.dumps(["101"] * 16))
    record = analyze_batch(batch)
    if record["readout_contrasts"] != [0.0, 1.0, 1.0]:
        raise RuntimeError("logical output readout gating must follow the declared mapping")
