"""Frozen campaign plans bind every batch before the provider runner is reached."""

import hashlib
import json
import shutil

import pytest
from hypercomplex_campaign import ROOT, analyze_batch, campaign_plan, execute, measured_wave
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

    batch = tmp_path / "swapped-layout"
    shutil.copytree(ROOT / "results/hypercomplex/cases/quantum_inspire/wave/wave-batch-19", batch)
    manifest_path = batch / "cases.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["shots"] = 16
    manifest_path.write_text(json.dumps(manifest))
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
    if record["physical_readout_one_probabilities"] != [[0.0, 0.0, 0.0], [1.0, 0.0, 1.0]]:
        raise RuntimeError("the analysis must preserve asymmetric readout references")
    if record["scientific_continuation_admitted"]:
        raise RuntimeError("readout quality alone cannot admit scientific continuation")
    for label in ("native", "requested"):
        if abs(sum(record["observed_minus_predicted"][label])) > 1e-12:
            raise RuntimeError("paired prediction residuals must retain their zero total")


def test_pacing_wait_cannot_replace_approved_manifest(tmp_path, monkeypatch) -> None:
    from contextlib import nullcontext

    import hypercomplex_campaign
    import qi_platform

    write_files(tmp_path, qi_cases(16))
    approved = campaign_plan(tmp_path)["plan_sha256"]
    first = sorted(tmp_path.glob("*/cases.json"))[0]
    pauses = iter((1, 0))
    monkeypatch.setattr(qi_platform, "Client", lambda: object())
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda client: next(pauses))
    monkeypatch.setattr(qi_platform, "token_lock", lambda *args: nullcontext())
    monkeypatch.setattr(hypercomplex_campaign.time, "sleep", lambda seconds: first.write_text(first.read_text() + " "))
    with pytest.raises(SystemExit, match="approved manifest"):
        execute(tmp_path, "approved fixture", approved, 60)


def test_measured_wave_requires_retained_shot_order(tmp_path, monkeypatch) -> None:
    import hypercomplex_campaign

    for index in range(17):
        batch = tmp_path / f"time-{index:02d}"
        batch.mkdir()
        setting = {"coupling": 1, "representative": 0, "time": index / 8}
        (batch / "cases.json").write_text(json.dumps({"circuits": [{}, {}, {"setting": setting}]}))
        (batch / "hypercomplex-analysis.json").write_text(json.dumps({"time": index / 8, "raw_sha256": "a" * 64}))

    def analyze(batch):
        return json.loads((batch / "hypercomplex-analysis.json").read_text())

    monkeypatch.setattr(hypercomplex_campaign, "analyze_batch", analyze)
    if len(measured_wave(tmp_path)["frames"]) != 17:
        raise RuntimeError("the complete retained wave must remain available")

    def reordered(batch):
        return {**analyze(batch), "raw_sha256": "b" * 64}

    monkeypatch.setattr(hypercomplex_campaign, "analyze_batch", reordered)
    with pytest.raises(ValueError, match="retained per-batch"):
        measured_wave(tmp_path)
