"""Admit and execute an approved three-job nominal-one destination comparison in verified serial order.

Every job occupies its own batch. Completion, full raw collection, zero recorded
charges and the account-wide pause precede creation of the next job. An ambiguous
or failed operation stops the campaign; an existing run root is never resumed by
this executor. Recovery uses read-only reconciliation and the successor collector.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import time
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import acquisition_decisions
import qi_platform
import qi_platform_submission_deadline as deadline_submission
from qi_projector_live_admission import structural_check
from qi_tuna_destination_one_analysis import (
    analyze,
    validate_execution_seconds,
    validate_locked_admission,
    validate_positive_integer,
    validate_terms,
    validate_zero_transactions,
)
from qi_tuna_destination_one_cases import PROPOSAL, ROOT, check
from qi_tuna_readout_mapping_cases import encoded, sha

TERMS_URLS = {
    "https://www.quantum-inspire.com/faq/",
    "https://www.quantum-inspire.com/kbase/managing-your-account/",
    "https://www.quantum-inspire.com/terms-and-conditions/",
}


def bound_file(path: Path, expected: str) -> bytes:
    content = path.read_bytes()
    if sha(content) != expected:
        raise ValueError(f"approved digest differs: {path.name}")
    return content


def validate_bindings(
    proposal: Path,
    campaign_sha256: str,
    written_case: Path,
    written_case_sha256: str,
    decision: Path,
    decision_sha256: str,
    terms: Path,
    terms_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    campaign = json.loads(bound_file(proposal / "campaign.json", campaign_sha256))
    if check(proposal) != campaign:
        raise ValueError("compiled proposal differs from the approved campaign")
    bound_file(written_case, written_case_sha256)
    decision_record = json.loads(bound_file(decision, decision_sha256))
    acquisition_decisions.validate_decision(decision_record)
    expected = {
        "status": "admitted-for-owner-approval",
        "campaign_sha256": campaign_sha256,
        "written_case_sha256": written_case_sha256,
        "analysis_contract_sha256": sha(encoded(campaign["analysis_contract"])),
        "expected_credits": 0,
        "execution_authorized": False,
        "provider": "quantum_inspire",
        "backend": "tuna_17",
        "shot_ceiling": campaign["shots_total"],
        "seconds_ceiling": campaign["provider_execution_ceiling_seconds"],
        "credits_ceiling": 0,
        "reserve_seconds": 0,
        "retry_authorized": False,
        "expected_execution_seconds_decimal": campaign["expected_execution_seconds_decimal"],
    }
    if any(
        type(decision_record.get(key)) is not type(value) or decision_record[key] != value
        for key, value in expected.items()
    ):
        raise ValueError("decision does not bind the exact unexecuted reviewed case")
    terms_record = json.loads(bound_file(terms, terms_sha256))
    validate_terms(terms_record)
    if qi_platform.HARDWARE_PAUSE_SECONDS != 30 or campaign["minimum_interjob_pause_seconds"] != 30:
        raise ValueError("this frozen case requires the 30-second account hardware pause")
    return (
        campaign,
        terms_record,
        {
            "campaign_sha256": campaign_sha256,
            "written_case_sha256": written_case_sha256,
            "decision_sha256": decision_sha256,
            "terms_sha256": terms_sha256,
            "analysis_contract_sha256": sha(encoded(campaign["analysis_contract"])),
        },
    )


class PolicyTextParser(HTMLParser):
    """Discard executable and style content; bind the complete normalized visible text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def policy_text(content: bytes) -> str:
    parser = PolicyTextParser()
    parser.feed(content.decode("utf-8"))
    parser.close()
    text = " ".join(" ".join(parser.parts).split())
    if not text:
        raise ValueError("public policy page has empty text")
    return text


def verify_public_terms(receipt: dict[str, Any], *, execution_deadline: float) -> list[dict[str, str]]:
    validate_terms(receipt)
    observed = []
    for page in receipt["pages"]:
        deadline_submission.check_deadline(execution_deadline)
        request = urllib.request.Request(page["url"], headers={"User-Agent": "gororoba-quantum-readonly-admission"})
        with urllib.request.urlopen(request, timeout=20) as response:
            content = response.read()
        if sha(policy_text(content)) != page["text_sha256"]:
            raise ValueError("public policy page differs from the reviewed terms receipt")
        observed.append({"url": page["url"], "html_sha256": sha(content), "text_sha256": sha(policy_text(content))})
    return observed


def observe(
    proposal: Path,
    campaign: dict[str, Any],
    terms: dict[str, Any],
    bindings: dict[str, str],
    *,
    execution_deadline: float | None = None,
) -> dict[str, Any]:
    observation_deadline = time.monotonic() + campaign["admission_max_age_seconds"]
    if execution_deadline is not None:
        observation_deadline = min(observation_deadline, execution_deadline)
    started = qi_platform.utc_now().isoformat()
    pages = verify_public_terms(terms, execution_deadline=observation_deadline)
    client = deadline_submission.Client(observation_deadline)
    live = client.get("/backend_types/7")
    instances = [row for row in client.pages("/backends") if row["backend_type_id"] == 7]
    transactions = client.pages("/transactions/")
    pause_left = qi_platform.hardware_pause_left(client)
    queue = client.get("/backend_types/7/queue", user_only=True)
    frozen = json.loads((proposal / campaign["batches"][0]["name"] / "backend.json").read_text())
    observed_at = qi_platform.utc_now()
    result = structural_check(
        frozen, live, instances, queue, transactions, pause_left, observed_at, campaign["heartbeat_max_age_seconds"]
    )
    result["limits"]["batch_circuits"] = 1
    return {
        "schema": "qi-tuna-destination-one-admission-v1",
        "request_started_utc": started,
        "observed_utc": observed_at.isoformat(),
        "bindings": bindings,
        "public_policy_pages": pages,
        "producer_sha256": sha(Path(__file__).read_bytes()),
        "boundary": "Read-only observations; provider state can change after observation.",
        **result,
    }


def timestamp(value: Any) -> datetime.datetime:
    if not isinstance(value, str):
        raise ValueError("job timestamp must be a timezone-aware string")
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("job timestamp lacks timezone")
    return parsed


def validate_completion(
    case: Path, batch: dict[str, Any], preceding: dict[str, Any] | None, campaign: dict[str, Any]
) -> dict[str, Any]:
    """Validate a sole completed job without selecting on its scientific outcomes."""
    manifest = json.loads(bound_file(case / "cases.json", batch["cases_sha256"]))
    source = manifest["circuits"][0]
    bound_file(case / source["file"], source["sha256"])
    submission = json.loads((case / "submission.json").read_text())
    if submission.get("schema") != qi_platform.SUBMISSION_SCHEMA:
        raise ValueError("submission schema differs from the frozen v2 receipt contract")
    qi_platform._check_submission_manifest(case, submission, require_enqueued=True)
    collection = json.loads((case / "results.json").read_text())
    if collection.get("schema") != "qi-collection-v1":
        raise ValueError("collection schema differs from the frozen receipt contract")
    if len(submission["jobs"]) != 1 or len(collection["jobs"]) != 1:
        raise ValueError("sequential cases require exactly one submitted and collected job")
    submitted = submission["jobs"][0]
    row = collection["jobs"][0]
    job = row["job"]
    for container, keys in (
        (job, ("id", "batch_job_id", "number_of_shots")),
        (submission, ("batch_job", "backend_type_id", "shots")),
        (submitted, ("job",)),
    ):
        for key in keys:
            validate_positive_integer(container[key], key)
    if (
        row["file"] != source["file"]
        or submitted["file"] != source["file"]
        or job["id"] != submitted["job"]
        or job["batch_job_id"] != submission["batch_job"]
        or job["status"] != "completed"
        or job["number_of_shots"] != 4096
        or job["raw_data_enabled"] is not True
        or len(row["results"]) != 1
    ):
        raise ValueError("single-job identity, completion or raw-data contract failed")
    result = row["results"][0]
    for key in ("job_id", "shots_done", "shots_requested"):
        validate_positive_integer(result[key], key)
    shots_path = case / "raw" / f"{source['file']}.json"
    shots = json.loads(shots_path.read_text())
    if (
        result["job_id"] != job["id"]
        or result["shots_done"] != 4096
        or result["shots_requested"] != 4096
        or not isinstance(shots, list)
        or len(shots) != 4096
        or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots)
        or any(type(count) is not int or count <= 0 for count in result["results"].values())
        or dict(Counter(shots)) != result["results"]
    ):
        raise ValueError("complete ordered raw shots and histogram are required")
    seconds = validate_execution_seconds(result["execution_time_in_seconds"])
    validate_zero_transactions(collection["transactions"], job["id"])
    created, queued, finished = (timestamp(job[key]) for key in ("created_on", "queued_at", "finished_at"))
    admission = json.loads((case / "admission.json").read_text())
    if admission.get("schema") != "qi-tuna-destination-one-admission-v1" or admission.get("admitted") is not True:
        raise ValueError("completion requires an admitted structural observation")
    admission_start = timestamp(admission["request_started_utc"])
    admission_end = timestamp(admission["observed_utc"])
    if not admission_start <= admission_end <= created or (created - admission_start).total_seconds() > 60:
        raise ValueError("job creation falls outside the fresh admission interval")
    validate_locked_admission(case, campaign, created)
    if not created <= queued <= finished:
        raise ValueError("job timestamps contradict creation-to-completion order")
    collected = timestamp(collection["collected_utc"])
    if finished > collected:
        raise ValueError("collection timestamp precedes job completion")
    if preceding is not None and created < timestamp(preceding["finished_at"]) + datetime.timedelta(seconds=30):
        raise ValueError("job creation precedes predecessor completion plus the frozen pause")
    if preceding is not None and created < timestamp(preceding["collected_utc"]):
        raise ValueError("job creation precedes predecessor raw collection")
    return {
        "schema": "qi-tuna-destination-one-completion-v1",
        "batch": batch["name"],
        "job": job["id"],
        "batch_job": submission["batch_job"],
        "created_on": job["created_on"],
        "queued_at": job["queued_at"],
        "finished_at": job["finished_at"],
        "collected_utc": collection["collected_utc"],
        "execution_seconds_decimal": str(seconds),
        "inputs": {
            name: sha((case / name).read_bytes())
            for name in (
                "cases.json",
                source["file"],
                "submission.json",
                "results.json",
                f"raw/{source['file']}.json",
                "locked-admission.json",
            )
        },
    }


def prepare_run(proposal: Path, run: Path, campaign: dict[str, Any], bindings: dict[str, str], approval: str) -> None:
    run.mkdir(parents=True, exist_ok=False)
    qi_platform._publish_text(run / "sequence-plan.json", (proposal / "campaign.json").read_text(), exclusive=True)
    for batch in campaign["batches"]:
        destination = run / batch["name"]
        destination.mkdir()
        for name in ("cases.json", "backend.json", batch["source_file"]):
            qi_platform._publish_text(destination / name, (proposal / batch["name"] / name).read_text(), exclusive=True)
    qi_platform._write_json(
        run / "campaign.json",
        {
            "schema": "qi-campaign-v1",
            "plan_sha256": bindings["campaign_sha256"],
            "batches": {batch["name"]: batch["cases_sha256"] for batch in campaign["batches"]},
        },
        exclusive=True,
    )
    qi_platform._write_json(
        run / "approval.json",
        {"schema": "qi-tuna-destination-one-approval-v1", "approval": approval, **bindings},
        exclusive=True,
    )


def wait_for_pause(deadline: float) -> None:
    while True:
        if time.monotonic() >= deadline:
            raise TimeoutError("campaign deadline expired while waiting for hardware pause")
        remaining = qi_platform.hardware_pause_left(deadline_submission.Client(deadline))
        if remaining <= 0:
            return
        time.sleep(min(30, remaining, max(0, deadline - time.monotonic())))


def locked_admission_check(case: Path, campaign: dict[str, Any]) -> deadline_submission.AdmissionCheck:
    """Recheck the complete frozen Tuna contract under the account submit lock."""
    manifest = json.loads((case / "cases.json").read_text())
    snapshot = manifest["backend_snapshot"]
    frozen = json.loads(bound_file(case / snapshot["file"], snapshot["sha256"]))

    def check(
        client: deadline_submission.Client,
        live: dict[str, Any],
        queue: dict[str, Any],
        pause_left: int,
    ) -> None:
        instances = [row for row in client.pages("/backends") if row["backend_type_id"] == 7]
        transactions = client.pages("/transactions/")
        observed_at = qi_platform.utc_now()
        observed = structural_check(
            frozen,
            live,
            instances,
            queue,
            transactions,
            pause_left,
            observed_at,
            campaign["heartbeat_max_age_seconds"],
        )
        observed["limits"]["batch_circuits"] = 1
        qi_platform._write_json(
            case / "locked-admission.json",
            {
                "schema": "qi-tuna-destination-one-locked-admission-v1",
                "observed_utc": observed_at.isoformat(),
                "cases_sha256": sha((case / "cases.json").read_bytes()),
                "runner_sha256": sha(Path(__file__).read_bytes()),
                "submission_helper_sha256": sha(Path(deadline_submission.__file__).read_bytes()),
                "boundary": "Observations under the account submit lock; provider state can change afterward.",
                **observed,
            },
            exclusive=True,
        )
        if observed["admitted"] is not True:
            raise ValueError("locked dispatch admission refused: " + "; ".join(observed["failures"]))

    return check


def execute(
    proposal: Path,
    run: Path,
    campaign: dict[str, Any],
    terms: dict[str, Any],
    bindings: dict[str, str],
    approval: str,
    attachments: dict[str, bytes] | None = None,
) -> None:
    if not approval.strip():
        raise ValueError("exact-case owner approval is required")
    if run.parent.resolve() != (ROOT / "results/quantum_inspire/runs").resolve():
        raise ValueError("campaign run must be an immediate child of the repository Quantum Inspire runs directory")
    if run.exists():
        raise FileExistsError("existing campaign is read-only recovery only; automatic resume is forbidden")
    required_attachments = {
        "written-case-at-approval.md": "written_case_sha256",
        "decision-at-approval.json": "decision_sha256",
        "terms-at-approval.json": "terms_sha256",
    }
    if attachments is None or attachments.keys() != required_attachments.keys():
        raise ValueError("execution requires all three frozen approval attachments")
    for name, attachment_binding in required_attachments.items():
        if sha(attachments[name]) != bindings[attachment_binding]:
            raise ValueError("approval attachment differs from its bound digest")
    window_started = qi_platform.utc_now()
    horizon = campaign["campaign_request_initiation_timeout_seconds"]
    deadline = time.monotonic() + horizon
    prepare_run(proposal, run, campaign, bindings, approval)
    qi_platform._write_json(
        run / "execution-window.json",
        {
            "schema": "qi-tuna-destination-one-window-v1",
            "started_utc": window_started.isoformat(),
            "request_deadline_utc": (window_started + datetime.timedelta(seconds=horizon)).isoformat(),
            "request_initiation_timeout_seconds": horizon,
            "boundary": "The monotonic guard governs request initiation; an in-flight request can finish later.",
        },
        exclusive=True,
    )
    for name, content in attachments.items():
        qi_platform._publish_text(run / name, content.decode("utf-8"), exclusive=True)
    completed: list[dict[str, Any]] = []
    state: dict[str, Any] = {"schema": "qi-tuna-destination-one-state-v1", "phase": "prepared", "completed": completed}
    qi_platform._write_json(run / "execution-state.json", state, exclusive=True)
    try:
        for batch in campaign["batches"]:
            wait_for_pause(deadline)
            case = run / batch["name"]
            if check(proposal) != campaign:
                raise ValueError("campaign changed during execution")
            bound_file(case / "cases.json", batch["cases_sha256"])
            admission = observe(proposal, campaign, terms, bindings, execution_deadline=deadline)
            qi_platform._write_json(case / "admission.json", admission, exclusive=True)
            if not admission["admitted"]:
                raise ValueError("fresh structural, pricing or account admission refused")
            age = (qi_platform.utc_now() - timestamp(admission["request_started_utc"])).total_seconds()
            if not math.isfinite(age) or not 0 <= age <= campaign["admission_max_age_seconds"]:
                raise ValueError("live admission expired before submission")
            submission_deadline = min(deadline, time.monotonic() + campaign["admission_max_age_seconds"] - age)
            binding = {"plan_sha256": bindings["campaign_sha256"], "cases_sha256": batch["cases_sha256"]}
            qi_platform._write_json(
                case / "execution-intent.json", {"schema": "qi-campaign-intent-v1", **binding}, exclusive=True
            )
            state.update(phase="submitting", active_batch=batch["name"])
            qi_platform._write_json(run / "execution-state.json", state)
            try:
                deadline_submission.submit(
                    case,
                    7,
                    approval,
                    expected_cases_sha256=batch["cases_sha256"],
                    execution_deadline=submission_deadline,
                    admission_check=locked_admission_check(case, campaign),
                )
            except BaseException:
                if not (case / "submission-state.json").exists() and not (case / "submission.json").exists():
                    qi_platform._write_json(
                        case / "preflight-refusal.json",
                        {"schema": "qi-campaign-refusal-v1", "phase": "preflight-refused", **binding},
                        exclusive=True,
                    )
                raise
            state["phase"] = "collecting"
            qi_platform._write_json(run / "execution-state.json", state)
            deadline_submission.collect(
                case,
                poll=15,
                timeout=campaign["campaign_request_initiation_timeout_seconds"],
                execution_deadline=deadline,
            )
            receipt = validate_completion(case, batch, completed[-1] if completed else None, campaign)
            if any(receipt["job"] == prior["job"] or receipt["batch_job"] == prior["batch_job"] for prior in completed):
                raise ValueError("provider reused an earlier campaign job or batch identity")
            qi_platform._write_json(case / "completion-admission.json", receipt, exclusive=True)
            completed.append(receipt)
            state["phase"] = "collected"
            qi_platform._write_json(run / "execution-state.json", state)
        report = analyze(run, proposal)
        qi_platform._write_json(run / "analysis.json", report, exclusive=True)
        if report["outcome"] in {"implementation route unavailable", "protocol inadmissible"}:
            raise ValueError("frozen final analyzer refuses the completed campaign evidence")
        state["analysis_outcome"] = report["outcome"]
    except BaseException as error:
        state.update(phase="stopped", error_type=type(error).__name__, observed_utc=qi_platform.utc_now().isoformat())
        qi_platform._write_json(run / "execution-state.json", state)
        raise
    state.update(phase="complete", observed_utc=qi_platform.utc_now().isoformat())
    qi_platform._write_json(run / "execution-state.json", state)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", type=Path, default=PROPOSAL)
    for name in ("campaign", "written-case", "decision", "terms"):
        if name != "campaign":
            parser.add_argument(f"--{name}", type=Path, required=True)
        parser.add_argument(f"--{name}-sha256", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-bindings", action="store_true")
    mode.add_argument("--observe", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--approval", default="")
    args = parser.parse_args()
    if args.observe and args.out is None:
        parser.error("--observe requires --out")
    if args.observe and args.out.exists():
        raise FileExistsError("observation output already exists")
    if args.execute and (args.run_root is None or not args.approval.strip()):
        parser.error("--execute requires --run-root and nonempty --approval")
    campaign, terms, bindings = validate_bindings(
        args.proposal,
        args.campaign_sha256,
        args.written_case,
        args.written_case_sha256,
        args.decision,
        args.decision_sha256,
        args.terms,
        args.terms_sha256,
    )
    if args.check_bindings:
        print("exact case, analyzer, compiler, decision and policy bindings match; provider operations unrun")
    elif args.observe:
        report = observe(args.proposal, campaign, terms, bindings)
        qi_platform._write_json(args.out, report, exclusive=True)
        if not report["admitted"]:
            raise SystemExit("read-only live admission refused; provider writes unrun")
    else:
        execute(
            args.proposal,
            args.run_root,
            campaign,
            terms,
            bindings,
            args.approval,
            attachments={
                "written-case-at-approval.md": bound_file(args.written_case, args.written_case_sha256),
                "decision-at-approval.json": bound_file(args.decision, args.decision_sha256),
                "terms-at-approval.json": bound_file(args.terms, args.terms_sha256),
            },
        )


if __name__ == "__main__":
    main()
