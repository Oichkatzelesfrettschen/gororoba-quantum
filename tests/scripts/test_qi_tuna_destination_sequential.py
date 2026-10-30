"""Single-job ordering, immutable case bindings, and operational stop boundaries."""

import json
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_tuna_destination_sequential_run as runner
from qi_tuna_destination_sequential_cases import ARMS, PREPARATIONS, build
from qi_tuna_readout_mapping_cases import PROPOSAL as PRIOR_PROPOSAL
from qi_tuna_readout_mapping_cases import encoded, sha


def generated() -> dict[str, str]:
    return build(
        {
            path.relative_to(PRIOR_PROPOSAL).as_posix(): path.read_text()
            for path in PRIOR_PROPOSAL.rglob("*")
            if path.is_file()
        }
    )


def write_tree(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def completed_case(case: Path, batch: dict[str, Any], created_second: int = 30) -> None:
    manifest = json.loads((case / "cases.json").read_text())
    source = manifest["circuits"][0]
    submission = {
        "schema": qi_platform.SUBMISSION_SCHEMA,
        "state": "enqueued",
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": 4096,
        "batch_job": 70,
        "cases_sha256": batch["cases_sha256"],
        "jobs": [{"file": source["file"], "job": 71, "sha256": source["sha256"]}],
    }
    job = {
        "id": 71,
        "batch_job_id": 70,
        "status": "completed",
        "number_of_shots": 4096,
        "raw_data_enabled": True,
        "created_on": f"2026-10-27T00:00:{created_second:02d}+00:00",
        "queued_at": "2026-10-27T00:00:31+00:00",
        "finished_at": "2026-10-27T00:00:36+00:00",
    }
    result = {
        "job_id": 71,
        "shots_done": 4096,
        "shots_requested": 4096,
        "execution_time_in_seconds": 5,
        "results": {"0" * 20: 4096},
    }
    collection = {
        "schema": "qi-collection-v1",
        "jobs": [{"file": source["file"], "job": job, "results": [result]}],
        "transactions": [],
    }
    (case / "admission.json").write_text(
        encoded(
            {
                "schema": "qi-tuna-sequential-admission-v1",
                "admitted": True,
                "request_started_utc": "2026-10-27T00:00:29+00:00",
                "observed_utc": "2026-10-27T00:00:29+00:00",
            }
        )
    )
    (case / "submission.json").write_text(encoded(submission))
    (case / "results.json").write_text(encoded(collection))
    (case / "raw").mkdir(exist_ok=True)
    (case / "raw" / f"{source['file']}.json").write_text(encoded(["0" * 20] * 4096))


def test_single_job_manifest_and_physical_source_preservation() -> None:
    files = generated()
    campaign = json.loads(files["campaign.json"])
    if [batch["name"] for batch in campaign["batches"]] != [f"{prep}-{arm}" for prep in PREPARATIONS for arm in ARMS]:
        raise AssertionError("sequential prepared-label bracket changed")
    for batch in campaign["batches"]:
        manifest = json.loads(files[f"{batch['name']}/cases.json"])
        if len(manifest["circuits"]) != 1 or manifest["shots"] != 4096:
            raise AssertionError("single-job shot ceiling changed")
        preparation = "prepared-zero" if batch["prepared_label"] == 0 else "prepared-one"
        if (
            files[f"{batch['name']}/{batch['source_file']}"]
            != (PRIOR_PROPOSAL / preparation / batch["source_file"]).read_text()
        ):
            raise AssertionError("successor changed a frozen source")
        if sha(files[f"{batch['name']}/cases.json"]) != batch["cases_sha256"]:
            raise AssertionError("campaign fails to bind manifest")


def test_completion_accepts_operational_success_even_all_zero(tmp_path: Path) -> None:
    files = generated()
    write_tree(tmp_path, files)
    batch = json.loads(files["campaign.json"])["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch)
    result = runner.validate_completion(case, batch, {"finished_at": "2026-10-27T00:00:00+00:00"})
    if result["job"] != 71:
        raise AssertionError("valid complete job rejected based on scientific outcome")


@pytest.mark.parametrize(
    "fault",
    [
        "failed",
        "partial",
        "charge",
        "order",
        "manifest",
        "raw",
        "submission_schema",
        "collection_schema",
        "duration_string",
        "duration_bool",
        "charge_string",
        "stale_admission",
        "float_shots",
        "float_job_id",
        "float_histogram",
    ],
)
def test_operational_fault_stops(tmp_path: Path, fault: str) -> None:
    files = generated()
    write_tree(tmp_path, files)
    batch = json.loads(files["campaign.json"])["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch)
    collection = json.loads((case / "results.json").read_text())
    if fault == "failed":
        collection["jobs"][0]["job"]["status"] = "failed"
    elif fault == "partial":
        collection["jobs"][0]["results"][0]["shots_done"] = 4095
    elif fault == "charge":
        collection["transactions"] = [{"id": 1, "job": 71, "change": -1}]
    elif fault == "order":
        collection["jobs"][0]["job"]["created_on"] = "2026-10-27T00:00:29+00:00"
    elif fault == "manifest":
        (case / "cases.json").write_text("{}")
    elif fault == "raw":
        (case / "raw" / f"{batch['source_file']}.json").write_text(encoded(["0" * 19] * 4096))
    elif fault == "submission_schema":
        submission = json.loads((case / "submission.json").read_text())
        del submission["schema"]
        (case / "submission.json").write_text(encoded(submission))
    elif fault == "collection_schema":
        del collection["schema"]
    elif fault in {"duration_string", "duration_bool"}:
        collection["jobs"][0]["results"][0]["execution_time_in_seconds"] = "5" if fault == "duration_string" else True
    elif fault == "float_shots":
        collection["jobs"][0]["results"][0]["shots_done"] = 4096.0
    elif fault == "float_job_id":
        collection["jobs"][0]["results"][0]["job_id"] = 71.0
    elif fault == "float_histogram":
        collection["jobs"][0]["results"][0]["results"] = {"0" * 20: 4096.0}
    elif fault == "charge_string":
        collection["transactions"] = [{"id": 1, "job": 71, "change": "0"}]
    else:
        admission = json.loads((case / "admission.json").read_text())
        admission["request_started_utc"] = "2026-10-26T23:59:00+00:00"
        (case / "admission.json").write_text(encoded(admission))
    (case / "results.json").write_text(encoded(collection))
    with pytest.raises(ValueError):
        runner.validate_completion(case, batch, {"finished_at": "2026-10-27T00:00:00+00:00"})


def test_native_campaign_marker_and_exclusive_creation(tmp_path: Path) -> None:
    files = generated()
    proposal = tmp_path / "proposal"
    write_tree(proposal, files)
    campaign = json.loads(files["campaign.json"])
    run = tmp_path / "runs" / "campaign"
    bindings = {"campaign_sha256": sha(files["campaign.json"])}
    runner.prepare_run(proposal, run, campaign, bindings, "explicit test authorization")
    if qi_platform.run_directories(run):
        raise AssertionError("preparation alone created acquisition intents")
    if (run / "sequence-plan.json").read_bytes() != (proposal / "campaign.json").read_bytes():
        raise AssertionError("run plan differs from frozen proposal")
    with pytest.raises(FileExistsError):
        runner.prepare_run(proposal, run, campaign, bindings, "duplicate")


def test_policy_text_ignores_scripts_but_detects_policy_changes() -> None:
    one = runner.policy_text(b"<p>Free <b>research</b> use.</p><script>nonce1</script>")
    two = runner.policy_text(b"<p>Free <b>research</b> use.</p><script>nonce2</script>")
    changed = runner.policy_text(b"<p>Paid <b>research</b> use.</p>")
    if one != two or one == changed:
        raise AssertionError("policy normalization confuses executable wrappers with visible policy")


@pytest.mark.parametrize("failure", ["none", "ambiguous", "collection"])
def test_executor_collects_before_successor_and_stops_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    files = generated()
    proposal = tmp_path / "proposal"
    write_tree(proposal, files)
    campaign = json.loads(files["campaign.json"])
    run = tmp_path / "results/quantum_inspire/runs/campaign"
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "check", lambda _proposal: campaign)
    events: list[str] = []
    monkeypatch.setattr(runner, "wait_for_pause", lambda _deadline: events.append("pause"))
    monkeypatch.setattr(
        runner,
        "observe",
        lambda *_args: {"admitted": True, "observed_utc": qi_platform.now(), "request_started_utc": qi_platform.now()},
    )
    names = [row["name"] for row in campaign["batches"]]

    def submit(case: Path, _backend: int, _approval: str, **kwargs: Any) -> None:
        index = names.index(case.name)
        if kwargs["expected_cases_sha256"] != campaign["batches"][index]["cases_sha256"]:
            raise AssertionError("submission lost exact manifest binding")
        if index and events[-2] != f"validate:{names[index - 1]}":
            raise AssertionError("next job submitted before predecessor validation and pause")
        events.append(f"submit:{case.name}")
        (case / "submission-state.json").write_text('{"phase":"enqueue_outcome_unknown"}')
        if failure == "ambiguous":
            raise TimeoutError("ambiguous enqueue")

    def collect(case: Path, **_kwargs: Any) -> None:
        events.append(f"collect:{case.name}")
        if failure == "collection":
            raise ValueError("partial raw collection")

    def validate(case: Path, _batch: dict, preceding: dict | None) -> dict:
        index = names.index(case.name)
        if index and (preceding is None or preceding["job"] != index):
            raise AssertionError("completion chain lost predecessor")
        events.append(f"validate:{case.name}")
        return {"job": index + 1, "batch_job": index + 1, "finished_at": qi_platform.now()}

    monkeypatch.setattr(qi_platform, "submit", submit)
    monkeypatch.setattr(qi_platform, "collect", collect)
    monkeypatch.setattr(runner, "validate_completion", validate)
    monkeypatch.setattr(runner, "analyze", lambda *_args: {"outcome": "inconclusive within budget"})
    attachments = {
        "written-case-at-approval.md": b"frozen written case",
        "decision-at-approval.json": b"frozen decision",
        "terms-at-approval.json": b"frozen terms",
    }
    arguments: tuple[Any, ...] = (
        proposal,
        run,
        campaign,
        {},
        {
            "campaign_sha256": sha(files["campaign.json"]),
            "written_case_sha256": sha(attachments["written-case-at-approval.md"]),
            "decision_sha256": sha(attachments["decision-at-approval.json"]),
            "terms_sha256": sha(attachments["terms-at-approval.json"]),
        },
        "test authorization",
        attachments,
    )
    if failure == "none":
        runner.execute(*arguments)
        if len([event for event in events if event.startswith("submit:")]) != 6:
            raise AssertionError("executor did not process all six jobs")
    else:
        with pytest.raises((TimeoutError, ValueError)):
            runner.execute(*arguments)
        if len([event for event in events if event.startswith("submit:")]) != 1:
            raise AssertionError("executor continued after operational failure")
        state = json.loads((run / "execution-state.json").read_text())
        if state["phase"] != "stopped":
            raise AssertionError("failure lacked a durable stop record")
    with pytest.raises(FileExistsError):
        runner.execute(*arguments)


def test_guard_rejects_expired_admission_after_account_lock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from contextlib import contextmanager

    clock = [100.0]
    monkeypatch.setattr(qi_platform.time, "monotonic", lambda: clock[0])

    @contextmanager
    def delayed_lock(_path: Path):
        clock[0] = 161.0
        yield

    def forbidden_client():
        raise AssertionError("expired admission reached the provider client")

    monkeypatch.setattr(qi_platform, "token_lock", delayed_lock)
    monkeypatch.setattr(qi_platform, "Client", forbidden_client)
    with pytest.raises(TimeoutError, match="deadline expired"):
        qi_platform.submit(tmp_path, 7, "test authorization", execution_deadline=160.0)


def test_lower_budget_decision_cannot_authorize_campaign(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = generated()
    proposal = tmp_path / "proposal"
    write_tree(proposal, files)
    campaign = json.loads(files["campaign.json"])
    monkeypatch.setattr(runner, "check", lambda _proposal: campaign)
    written = tmp_path / "case.md"
    written.write_text("Exact six-job diagnostic case")
    decision: dict[str, Any] = {
        field: "specified"
        for field in (
            "case_id",
            "simulation_justification",
            "objective",
            "discriminating_observable",
            "trial_definition",
            "observation_chain",
            "dependence_model",
            "layout_timing_identity",
            "processing_policy",
            "end_without_retry",
        )
    }
    decision.update(
        schema="acquisition-decision-v1",
        status="admitted-for-owner-approval",
        provider="quantum_inspire",
        backend="tuna_17",
        alternatives=["response equivalent", "response differs"],
        stopping_outcomes={name: "specified" for name in runner.acquisition_decisions.OUTCOMES},
        power_model={"status": "qualified", "evidence": "frozen conditional mathematical bounds"},
        campaign_sha256=sha(files["campaign.json"]),
        written_case_sha256=sha(written.read_bytes()),
        analysis_contract_sha256=sha(encoded(campaign["analysis_contract"])),
        expected_credits=0,
        execution_authorized=False,
        shot_ceiling=4096,
        seconds_ceiling=1800,
        credits_ceiling=0,
        reserve_seconds=0,
        retry_authorized=False,
        expected_execution_seconds_decimal="29.533215",
    )
    runner.acquisition_decisions.validate_decision(decision)
    decision_path = tmp_path / "decision.json"
    decision_path.write_text(encoded(decision))
    terms_path = tmp_path / "terms.json"
    terms_path.write_text(
        encoded(
            {
                "pages": [
                    {
                        "url": url,
                        "text": "public terms",
                        "text_sha256": sha("public terms"),
                        "html_sha256": sha("public terms"),
                    }
                    for url in sorted(runner.TERMS_URLS)
                ]
            }
        )
    )
    with pytest.raises(ValueError, match="decision does not bind"):
        runner.validate_bindings(
            proposal,
            sha(files["campaign.json"]),
            written,
            sha(written.read_bytes()),
            decision_path,
            sha(decision_path.read_bytes()),
            terms_path,
            sha(terms_path.read_bytes()),
        )


def test_execute_requires_retained_approval_attachments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = generated()
    proposal = tmp_path / "proposal"
    write_tree(proposal, files)
    campaign = json.loads(files["campaign.json"])
    run = tmp_path / "results/quantum_inspire/runs/campaign"
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="approval attachments"):
        runner.execute(proposal, run, campaign, {}, {"campaign_sha256": sha(files["campaign.json"])}, "approval")
    if run.exists():
        raise AssertionError("missing attachments created an execution directory")
