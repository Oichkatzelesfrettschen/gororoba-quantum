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


def test_campaign_passes_deadline_and_retains_preflight_refusal(tmp_path, monkeypatch) -> None:
    import hypercomplex_campaign
    import qi_platform

    write_files(tmp_path, qi_cases(16))
    approved = campaign_plan(tmp_path)["plan_sha256"]
    monkeypatch.setattr(hypercomplex_campaign.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(qi_platform, "Client", lambda: object())
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda client: 0)

    def expired(batch, backend, approval, *, expected_cases_sha256, execution_deadline):
        if execution_deadline != 160.0:
            raise RuntimeError("the submission must receive the campaign's absolute deadline")
        raise TimeoutError("execution deadline expired")

    monkeypatch.setattr(qi_platform, "submit", expired)
    with pytest.raises(TimeoutError, match="deadline"):
        execute(tmp_path, "approved fixture", approved, 60)
    batch = sorted(tmp_path.glob("*/cases.json"))[0].parent
    intent = json.loads((batch / "execution-intent.json").read_text())
    refusal = json.loads((batch / "preflight-refusal.json").read_text())
    if refusal != {**intent, "schema": "qi-campaign-refusal-v1", "phase": "preflight-refused"}:
        raise RuntimeError("deadline preflight refusal must retain the exact intent binding")


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


def test_execution_registers_explicit_nested_batch_container(tmp_path, monkeypatch) -> None:
    import qi_platform

    runs = tmp_path / "runs"
    campaign = runs / "order-acquisition"
    write_files(campaign, qi_cases(16))
    plan = campaign_plan(campaign)
    monkeypatch.setattr(qi_platform, "Client", lambda: object())
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda client: 0)

    def stop_before_cloud(*args, **kwargs):
        qi_platform._write_json(args[0] / "submission-state.json", {"phase": "creating"}, exclusive=True)
        raise RuntimeError("stop before cloud")

    monkeypatch.setattr(qi_platform, "submit", stop_before_cloud)
    with pytest.raises(RuntimeError, match="stop before cloud"):
        execute(campaign, "approved fixture", plan["plan_sha256"], 60)
    if len(qi_platform.run_directories(runs)) != 1:
        raise RuntimeError("the campaign container must expose the attempted batch and distinguish future plans")
    marker = json.loads((campaign / "campaign.json").read_text())
    if len(marker["batches"]) != 8:
        raise RuntimeError("the immutable container must bind every approved batch")
    if campaign_plan(campaign)["plan_sha256"] != plan["plan_sha256"]:
        raise RuntimeError("container metadata must preserve the frozen plan identity")


def test_preflight_refusal_distinguishes_plans_from_acquisitions(tmp_path, monkeypatch) -> None:
    import qi_platform

    runs = tmp_path / "runs"
    campaign = runs / "order-acquisition"
    write_files(campaign, qi_cases(16))
    plan = campaign_plan(campaign)
    monkeypatch.setattr(qi_platform, "Client", lambda: object())
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda client: 0)

    def refuse_before_creation(*args, **kwargs):
        raise SystemExit("fixture admission refused")

    monkeypatch.setattr(qi_platform, "submit", refuse_before_creation)
    with pytest.raises(SystemExit, match="admission refused"):
        execute(campaign, "approved fixture", plan["plan_sha256"], 60)
    if qi_platform.run_directories(runs):
        raise RuntimeError("a local preflight refusal must remain distinct from an acquisition")
    refusals = list(campaign.glob("*/preflight-refusal.json"))
    if len(refusals) != 1:
        raise RuntimeError("the attempted batch needs exactly one durable refusal record")


def test_refusal_classification_observes_competing_creation_under_lock(tmp_path, monkeypatch) -> None:
    from contextlib import contextmanager

    import qi_platform

    runs = tmp_path / "runs"
    campaign = runs / "order-acquisition"
    write_files(campaign, qi_cases(16))
    first = sorted(campaign.glob("*/cases.json"))[0].parent
    plan = campaign_plan(campaign)
    monkeypatch.setattr(qi_platform, "Client", lambda: object())
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda client: 0)

    @contextmanager
    def competing_creation(lock_path):
        if lock_path != qi_platform.SUBMIT_LOCK:
            raise RuntimeError("refusal classification must reacquire the account submission lock")
        qi_platform._write_json(first / "submission-state.json", {"phase": "creating"}, exclusive=True)
        yield

    def refused(*args, **kwargs):
        raise SystemExit("fixture preflight refused")

    monkeypatch.setattr(qi_platform, "token_lock", competing_creation)
    monkeypatch.setattr(qi_platform, "submit", refused)
    with pytest.raises(SystemExit, match="preflight refused"):
        execute(campaign, "approved fixture", plan["plan_sha256"], 60)
    if (first / "preflight-refusal.json").exists() or qi_platform.run_directories(runs) != [first]:
        raise RuntimeError("a competing durable creation must remain an attempted acquisition")
