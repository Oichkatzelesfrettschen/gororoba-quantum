"""Single-job ordering, immutable case bindings, and operational stop boundaries."""

import json
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_tuna_destination_one_run as runner
from qi_tuna_destination_one_cases import ARMS, PREPARATIONS, build
from qi_tuna_destination_sequential_cases import PROPOSAL as PRIOR_PROPOSAL
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


def completed_case(case: Path, batch: dict[str, Any], campaign: dict[str, Any], created_second: int = 30) -> None:
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
        "collected_utc": "2026-10-27T00:00:37+00:00",
        "jobs": [{"file": source["file"], "job": job, "results": [result]}],
        "transactions": [],
    }
    frozen = json.loads((case / "backend.json").read_text())
    instances = [{"backend_type_id": 7, "status": "idle", "last_heartbeat": "2026-10-27T00:00:28+00:00"}]
    for name, observed in (
        ("admission.json", "2026-10-27T00:00:29+00:00"),
        ("locked-admission.json", "2026-10-27T00:00:29.500000+00:00"),
    ):
        admission = runner.structural_check(
            frozen,
            frozen,
            instances,
            {"number_of_jobs_in_queue": 0},
            [],
            0,
            runner.timestamp(observed),
            campaign["heartbeat_max_age_seconds"],
        )
        admission["limits"]["batch_circuits"] = 1
        if name == "admission.json":
            admission.update(
                schema="qi-tuna-destination-one-admission-v1",
                request_started_utc="2026-10-27T00:00:29+00:00",
                observed_utc=observed,
            )
        else:
            admission.update(
                schema="qi-tuna-destination-one-locked-admission-v1",
                observed_utc=observed,
                cases_sha256=batch["cases_sha256"],
                runner_sha256=campaign["producer_inputs"]["scripts/qi_tuna_destination_one_run.py"],
                submission_helper_sha256=campaign["producer_inputs"]["scripts/qi_platform_submission_deadline.py"],
            )
        (case / name).write_text(encoded(admission))
    (case.parent / "execution-window.json").write_text(
        encoded(
            {
                "schema": "qi-tuna-destination-one-window-v1",
                "started_utc": "2026-10-27T00:00:00+00:00",
                "request_deadline_utc": "2026-10-27T02:00:00+00:00",
                "request_initiation_timeout_seconds": 7200,
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
        preparation = batch["name"]
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
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch, campaign)
    result = runner.validate_completion(
        case,
        batch,
        {"finished_at": "2026-10-27T00:00:00+00:00", "collected_utc": "2026-10-27T00:00:01+00:00"},
        campaign,
    )
    if result["job"] != 71:
        raise AssertionError("valid complete job rejected based on scientific outcome")
    if result["inputs"].get("locked-admission.json") != sha((case / "locked-admission.json").read_bytes()):
        raise AssertionError("completion receipt omitted its semantically validated locked admission")


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "malformed",
        "schema",
        "false_admission",
        "failures",
        "manifest_hash",
        "runner_hash",
        "helper_hash",
        "structure",
        "enabled",
        "queue",
        "ledger",
        "heartbeat",
        "before_initial",
        "after_creation",
    ],
)
def test_completion_requires_semantically_valid_locked_admission_even_after_rehash(tmp_path: Path, fault: str) -> None:
    files = generated()
    write_tree(tmp_path, files)
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch, campaign)
    receipt = runner.validate_completion(case, batch, None, campaign)
    path = case / "locked-admission.json"
    locked = json.loads(path.read_text())
    if fault == "missing":
        path.unlink()
    elif fault == "malformed":
        path.write_text("{")
    else:
        if fault == "schema":
            locked["schema"] = "wrong-schema"
        elif fault == "false_admission":
            locked["admitted"] = False
        elif fault == "failures":
            locked["failures"] = ["unavailable"]
        elif fault == "manifest_hash":
            locked["cases_sha256"] = "0" * 64
        elif fault == "runner_hash":
            locked["runner_sha256"] = "0" * 64
        elif fault == "helper_hash":
            locked["submission_helper_sha256"] = "0" * 64
        elif fault == "structure":
            locked["backend"]["default_compiler_config"] = {}
        elif fault == "enabled":
            locked["enabled"] = False
        elif fault == "queue":
            locked["queued_batches"] = 1
        elif fault == "ledger":
            locked["all_transaction_changes_zero"] = False
        elif fault == "heartbeat":
            locked["instances"][0]["age_seconds"] = 0.5
        elif fault == "before_initial":
            locked["observed_utc"] = "2026-10-27T00:00:28.500000+00:00"
        else:
            locked["observed_utc"] = "2026-10-27T00:00:30.500000+00:00"
        path.write_text(encoded(locked))
    if path.exists():
        receipt["inputs"]["locked-admission.json"] = sha(path.read_bytes())
    (case / "completion-admission.json").write_text(encoded(receipt))
    with pytest.raises((ValueError, FileNotFoundError)):
        runner.validate_completion(case, batch, None, campaign)


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
        "collection_before_finish",
    ],
)
def test_operational_fault_stops(tmp_path: Path, fault: str) -> None:
    files = generated()
    write_tree(tmp_path, files)
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch, campaign)
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
    elif fault == "collection_before_finish":
        collection["collected_utc"] = "2026-10-27T00:00:35+00:00"
    elif fault == "charge_string":
        collection["transactions"] = [{"id": 1, "job": 71, "change": "0"}]
    else:
        admission = json.loads((case / "admission.json").read_text())
        admission["request_started_utc"] = "2026-10-26T23:59:00+00:00"
        (case / "admission.json").write_text(encoded(admission))
    (case / "results.json").write_text(encoded(collection))
    with pytest.raises(ValueError):
        runner.validate_completion(
            case,
            batch,
            {"finished_at": "2026-10-27T00:00:00+00:00", "collected_utc": "2026-10-27T00:00:01+00:00"},
            campaign,
        )


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
        lambda *_args, **_kwargs: {
            "admitted": True,
            "observed_utc": qi_platform.now(),
            "request_started_utc": qi_platform.now(),
        },
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

    def validate(case: Path, _batch: dict, preceding: dict | None, _campaign: dict) -> dict:
        index = names.index(case.name)
        if index and (preceding is None or preceding["job"] != index):
            raise AssertionError("completion chain lost predecessor")
        events.append(f"validate:{case.name}")
        return {"job": index + 1, "batch_job": index + 1, "finished_at": qi_platform.now()}

    monkeypatch.setattr(runner.deadline_submission, "submit", submit)
    monkeypatch.setattr(runner.deadline_submission, "collect", collect)
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
        if len([event for event in events if event.startswith("submit:")]) != 3:
            raise AssertionError("executor did not process all three jobs")
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


@pytest.mark.parametrize("fault", ["lower_budget", "terms_schema", "terms_text", "valid"])
def test_exact_case_and_terms_bindings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str) -> None:
    files = generated()
    proposal = tmp_path / "proposal"
    write_tree(proposal, files)
    campaign = json.loads(files["campaign.json"])
    monkeypatch.setattr(runner, "check", lambda _proposal: campaign)
    written = tmp_path / "case.md"
    written.write_text("Exact three-job nominal-one diagnostic case")
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
        shot_ceiling=4096 if fault == "lower_budget" else 12288,
        seconds_ceiling=900,
        credits_ceiling=0,
        reserve_seconds=0,
        retry_authorized=False,
        expected_execution_seconds_decimal="14.688660",
    )
    runner.acquisition_decisions.validate_decision(decision)
    decision_path = tmp_path / "decision.json"
    decision_path.write_text(encoded(decision))
    terms_path = tmp_path / "terms.json"
    terms_path.write_text(
        encoded(
            {
                "schema": "qi-readout-destination-terms-text-v1" if fault != "terms_schema" else "wrong-schema",
                "pages": [
                    {
                        "url": url,
                        "text": "public terms",
                        "text_sha256": sha("public terms"),
                        "html_sha256": sha("public terms"),
                        "observed_utc": "2026-10-27T00:00:00+00:00",
                    }
                    for url in sorted(runner.TERMS_URLS)
                ],
            }
        )
    )
    if fault == "terms_text":
        terms = json.loads(terms_path.read_text())
        terms["pages"][0]["text"] = "changed policy"
        terms_path.write_text(encoded(terms))
    arguments = (
        proposal,
        sha(files["campaign.json"]),
        written,
        sha(written.read_bytes()),
        decision_path,
        sha(decision_path.read_bytes()),
        terms_path,
        sha(terms_path.read_bytes()),
    )
    if fault == "valid":
        actual_campaign, _terms, bindings = runner.validate_bindings(*arguments)
        if actual_campaign != campaign or bindings["campaign_sha256"] != sha(files["campaign.json"]):
            raise AssertionError("exact-case validation changed the frozen campaign")
    else:
        with pytest.raises(ValueError):
            runner.validate_bindings(*arguments)


def test_successor_creation_waits_for_predecessor_raw_collection(tmp_path: Path) -> None:
    files = generated()
    write_tree(tmp_path, files)
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    case = tmp_path / batch["name"]
    completed_case(case, batch, campaign)
    preceding = {"finished_at": "2026-10-27T00:00:00+00:00", "collected_utc": "2026-10-27T00:00:35+00:00"}
    with pytest.raises(ValueError, match="predecessor raw collection"):
        runner.validate_completion(case, batch, preceding, campaign)


def test_queue_allowance_and_scope_remain_separate_from_old_case() -> None:
    files = generated()
    campaign = json.loads(files["campaign.json"])
    if (
        campaign["schema"] != "qi-tuna-destination-one-campaign-v1"
        or campaign["shots_total"] != 12288
        or campaign["provider_execution_ceiling_seconds"] != 900
        or campaign["campaign_request_initiation_timeout_seconds"] != 7200
        or any(batch["prepared_label"] != 1 for batch in campaign["batches"])
    ):
        raise AssertionError("nominal-one scope or queue allowance changed")
    basis = campaign["queue_horizon_basis"]
    estimate = 3 * basis["observed_queue_maximum_seconds"] + 900 + 2 * 30
    if (
        estimate != basis["three_waits_plus_execution_ceiling_and_pauses_seconds"]
        or estimate + basis["additional_admission_collection_allowance_seconds"] != 7200
    ):
        raise AssertionError("queue allowance lost its measured-wait arithmetic")
    for batch in campaign["batches"]:
        relative = f"{batch['name']}/cases.json"
        if files[relative] != (PRIOR_PROPOSAL / relative).read_text():
            raise AssertionError("nominal-one manifest bytes changed from approved control sources")


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


def test_public_policy_request_initiation_obeys_campaign_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextlib import contextmanager

    clock = [0.0]
    calls: list[str] = []
    monkeypatch.setattr(runner.time, "monotonic", lambda: clock[0])
    terms = {
        "schema": "qi-readout-destination-terms-text-v1",
        "pages": [
            {
                "url": url,
                "text": "policy",
                "text_sha256": sha("policy"),
                "html_sha256": sha("<p>policy</p>"),
                "observed_utc": "2026-10-27T00:00:00+00:00",
            }
            for url in sorted(runner.TERMS_URLS)
        ],
    }

    class Response:
        def read(self) -> bytes:
            return b"<p>policy</p>"

    @contextmanager
    def request(url: Any, **_kwargs: Any):
        calls.append(url.full_url)
        clock[0] = 100.0
        yield Response()

    monkeypatch.setattr(runner.urllib.request, "urlopen", request)
    with pytest.raises(TimeoutError):
        runner.verify_public_terms(terms, execution_deadline=100.0)
    if len(calls) != 1:
        raise AssertionError("policy admission initiated another URL request after deadline")


@pytest.mark.parametrize("fault", ["enabled", "compiler", "heartbeat", "ledger", "valid"])
def test_locked_dispatch_rechecks_full_structural_and_account_contract(tmp_path: Path, fault: str) -> None:
    import copy

    files = generated()
    write_tree(tmp_path, files)
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    case = tmp_path / batch["name"]
    live = copy.deepcopy(json.loads((case / "backend.json").read_text()))
    live["enabled"] = fault != "enabled"
    if fault == "compiler":
        live["default_compiler_config"] = {}
    instances = [
        {
            "backend_type_id": 7,
            "status": "idle",
            "last_heartbeat": "2026-01-01T00:00:00+00:00" if fault == "heartbeat" else qi_platform.now(),
        }
    ]

    class Client:
        def pages(self, path: str) -> list[dict[str, Any]]:
            if path == "/backends":
                return instances
            return [{"change": -1}] if fault == "ledger" else []

    client: Any = Client()
    callback = runner.locked_admission_check(case, campaign)
    if fault == "valid":
        callback(client, live, {"number_of_jobs_in_queue": 0}, 0)
    else:
        with pytest.raises(ValueError, match="locked dispatch admission refused"):
            callback(client, live, {"number_of_jobs_in_queue": 0}, 0)
    receipt = json.loads((case / "locked-admission.json").read_text())
    if receipt["admitted"] is not (fault == "valid"):
        raise AssertionError("locked admission did not retain its actual acceptance or refusal")
    if (
        receipt["cases_sha256"] != batch["cases_sha256"]
        or receipt["runner_sha256"] != campaign["producer_inputs"]["scripts/qi_tuna_destination_one_run.py"]
        or receipt["submission_helper_sha256"]
        != campaign["producer_inputs"]["scripts/qi_platform_submission_deadline.py"]
    ):
        raise AssertionError("locked admission lost its exact manifest or producer provenance")


def test_initial_admission_preserves_fractional_window_start(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = generated()
    write_tree(tmp_path, files)
    campaign = json.loads(files["campaign.json"])
    batch = campaign["batches"][0]
    frozen = json.loads((tmp_path / batch["name"] / "backend.json").read_text())
    observed = runner.timestamp("2026-10-27T00:00:00.123456+00:00")
    monkeypatch.setattr(qi_platform, "utc_now", lambda: observed)
    monkeypatch.setattr(qi_platform, "hardware_pause_left", lambda _client: 0)
    monkeypatch.setattr(runner, "verify_public_terms", lambda *_args, **_kwargs: [])

    class Client:
        def __init__(self, _deadline: float) -> None:
            pass

        def get(self, path: str, **_kwargs: Any) -> dict[str, Any]:
            return frozen if path == "/backend_types/7" else {"number_of_jobs_in_queue": 0}

        def pages(self, path: str) -> list[dict[str, Any]]:
            if path == "/backends":
                return [{"backend_type_id": 7, "status": "idle", "last_heartbeat": observed.isoformat()}]
            return []

    monkeypatch.setattr(runner.deadline_submission, "Client", Client)
    admission = runner.observe(tmp_path, campaign, {}, {})
    if admission["request_started_utc"] != observed.isoformat() or admission["observed_utc"] != observed.isoformat():
        raise AssertionError("admission truncated its request origin before the fractional execution-window start")
