"""Frozen response inference accepts arbitrary dependence while refusing scope and ordering defects."""

import datetime as dt
import hashlib
import json
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

import pytest
from qi_tuna_destination_one_analysis import BATCHES, ROOT, SHOTS, analyze, cells, classify, contract, digest
from qi_tuna_readout_mapping_cases import build


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture
def acquisition(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    run, proposal = tmp_path / "run", tmp_path / "proposal"
    source_files = build()
    batches = []
    for index, name in enumerate(BATCHES):
        state, arm = "-".join(name.split("-")[:2]), "-".join(name.split("-")[2:])
        original = json.loads(source_files[f"{state}/cases.json"])
        entry = next(entry for entry in original["circuits"] if entry["name"] == arm)
        original["circuits"] = [entry]
        for base in (run, proposal):
            save(base / name / "cases.json", original)
            (base / name / "backend.json").write_text(source_files[f"{state}/backend.json"])
            (base / name / entry["file"]).write_text(source_files[f"{state}/{entry['file']}"])
        manifest_hash = digest(run / name / "cases.json")
        batches.append({"name": name, "cases_sha256": manifest_hash})
        job_id = index + 10
        start = dt.datetime(2026, 10, 27, 19, index, tzinfo=dt.UTC)
        shots = [("1") * 20] * SHOTS
        save(run / name / "raw" / f"{entry['file']}.json", shots)
        save(
            run / name / "submission.json",
            {
                "schema": "qi-submission-v2",
                "approval": "Synthetic fixture approval; local tests only.",
                "backend_type_id": 7,
                "backend": "tuna_17",
                "shots": SHOTS,
                "cases_sha256": manifest_hash,
                "state": "enqueued",
                "batch_job": job_id + 100,
                "jobs": [{"file": entry["file"], "sha256": entry["sha256"], "job": job_id}],
            },
        )
        save(
            run / name / "results.json",
            {
                "schema": "qi-collection-v1",
                "collected_utc": (start + dt.timedelta(seconds=6)).isoformat(),
                "jobs": [
                    {
                        "file": entry["file"],
                        "job": {
                            "id": job_id,
                            "batch_job_id": job_id + 100,
                            "status": "completed",
                            "number_of_shots": SHOTS,
                            "raw_data_enabled": True,
                            "created_on": start.isoformat(),
                            "queued_at": start.isoformat(),
                            "finished_at": (start + dt.timedelta(seconds=5)).isoformat(),
                        },
                        "results": [
                            {
                                "job_id": job_id,
                                "shots_requested": SHOTS,
                                "shots_done": SHOTS,
                                "execution_time_in_seconds": 5,
                                "results": dict(Counter(shots)),
                            }
                        ],
                    }
                ],
                "transactions": [],
            },
        )
    plan: dict[str, Any] = {
        "schema": "qi-tuna-destination-one-campaign-v1",
        "circuits_total": 3,
        "shots_per_circuit": SHOTS,
        "minimum_interjob_pause_seconds": 30,
        "expected_credits": 0,
        "campaign_request_initiation_timeout_seconds": 7200,
        "batches": batches,
        "analysis_contract": {
            "file": "scripts/qi_tuna_destination_one_analysis.py",
            "sha256": digest(ROOT / "scripts/qi_tuna_destination_one_analysis.py"),
            "mathematical_note": {
                "file": "docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md",
                "sha256": digest(
                    ROOT / "docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md"
                ),
            },
        },
    }
    plan.update(
        {
            "shots_total": 12288,
            "provider_execution_ceiling_seconds": 900,
            "expected_execution_seconds_decimal": "14.688660",
            "admission_max_age_seconds": 60,
            "heartbeat_max_age_seconds": 120,
            "producer_inputs": {
                "scripts/qi_tuna_destination_one_run.py": digest(ROOT / "scripts/qi_tuna_destination_one_run.py"),
                "scripts/qi_platform_submission_deadline.py": digest(
                    ROOT / "scripts/qi_platform_submission_deadline.py"
                ),
            },
        }
    )
    save(proposal / "campaign.json", plan)
    save(run / "sequence-plan.json", plan)
    save(
        run / "campaign.json",
        {
            "schema": "qi-campaign-v1",
            "plan_sha256": digest(run / "sequence-plan.json"),
            "batches": {row["name"]: row["cases_sha256"] for row in batches},
        },
    )
    save(
        run / "execution-window.json",
        {
            "schema": "qi-tuna-destination-one-window-v1",
            "started_utc": "2026-10-27T18:59:00+00:00",
            "request_deadline_utc": "2026-10-27T20:59:00+00:00",
            "request_initiation_timeout_seconds": 7200,
        },
    )
    written = run / "written-case-at-approval.md"
    written.write_text("Synthetic bound case for offline contract tests.\n")
    terms = json.loads((ROOT / "docs/evidence/tuna-projector-geometry/readout-destination-terms-text.json").read_text())
    save(run / "terms-at-approval.json", terms)
    contract_hash = hashlib.sha256(
        (json.dumps(plan["analysis_contract"], indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()
    decision = json.loads(
        (ROOT / "docs/evidence/tuna-projector-geometry/readout-ordered-response-decision.json").read_text()
    )
    decision.update(
        {
            "campaign_sha256": digest(run / "sequence-plan.json"),
            "written_case_sha256": digest(written),
            "analysis_contract_sha256": contract_hash,
            "shot_ceiling": 12288,
            "seconds_ceiling": 900,
            "expected_execution_seconds_decimal": "14.688660",
        }
    )
    save(run / "decision-at-approval.json", decision)
    bindings = {
        "campaign_sha256": digest(run / "sequence-plan.json"),
        "written_case_sha256": digest(written),
        "decision_sha256": digest(run / "decision-at-approval.json"),
        "terms_sha256": digest(run / "terms-at-approval.json"),
        "analysis_contract_sha256": contract_hash,
    }
    save(
        run / "approval.json",
        {
            "schema": "qi-tuna-destination-one-approval-v1",
            "approval": "Synthetic fixture approval; local tests only.",
            **bindings,
        },
    )
    for index, name in enumerate(BATCHES):
        directory = run / name
        collection = json.loads((directory / "results.json").read_text())
        job = collection["jobs"][0]["job"]
        created = dt.datetime.fromisoformat(job["created_on"])
        admission = json.loads(
            (ROOT / "docs/evidence/tuna-projector-geometry/readout-ordered-response-admission.json").read_text()
        )
        admission.update(
            {
                "schema": "qi-tuna-destination-one-admission-v1",
                "bindings": bindings,
                "producer_sha256": plan["producer_inputs"]["scripts/qi_tuna_destination_one_run.py"],
                "request_started_utc": (created - dt.timedelta(seconds=5)).isoformat(),
                "observed_utc": (created - dt.timedelta(seconds=1)).isoformat(),
            }
        )
        admission["instances"] = [
            {"status": "idle", "last_heartbeat": (created - dt.timedelta(seconds=2)).isoformat(), "age_seconds": 1.0}
        ]
        save(directory / "admission.json", admission)
        locked = {
            key: value
            for key, value in admission.items()
            if key
            not in {
                "schema",
                "bindings",
                "producer_sha256",
                "request_started_utc",
                "observed_utc",
                "public_policy_pages",
            }
        }
        locked.update(
            {
                "schema": "qi-tuna-destination-one-locked-admission-v1",
                "observed_utc": (created - dt.timedelta(microseconds=500000)).isoformat(),
                "cases_sha256": batches[index]["cases_sha256"],
                "runner_sha256": plan["producer_inputs"]["scripts/qi_tuna_destination_one_run.py"],
                "submission_helper_sha256": plan["producer_inputs"]["scripts/qi_platform_submission_deadline.py"],
                "instances": [
                    {
                        "status": "idle",
                        "last_heartbeat": (created - dt.timedelta(seconds=2)).isoformat(),
                        "age_seconds": 1.5,
                    }
                ],
            }
        )
        save(directory / "locked-admission.json", locked)
        save(
            directory / "execution-intent.json",
            {
                "schema": "qi-campaign-intent-v1",
                "plan_sha256": bindings["campaign_sha256"],
                "cases_sha256": batches[index]["cases_sha256"],
            },
        )
        filename = collection["jobs"][0]["file"]
        save(
            directory / "completion-admission.json",
            {
                "schema": "qi-tuna-destination-one-completion-v1",
                "batch": name,
                "job": job["id"],
                "batch_job": job["batch_job_id"],
                "created_on": job["created_on"],
                "queued_at": job["queued_at"],
                "finished_at": job["finished_at"],
                "collected_utc": collection["collected_utc"],
                "execution_seconds_decimal": "5",
                "inputs": {
                    key: digest(directory / key)
                    for key in (
                        "cases.json",
                        filename,
                        "submission.json",
                        "results.json",
                        f"raw/{filename}.json",
                        "locked-admission.json",
                    )
                },
            },
        )
    return run, proposal


def test_complete_fixed_case(acquisition: tuple[Path, Path]) -> None:
    result = analyze(*acquisition)
    if result["outcome"] != "objective established within scope" or len(result["comparisons"]) != 12:
        raise AssertionError(result)
    if result["attribution_status"] != "unresolved" or result["physical_continuation_admitted"]:
        raise AssertionError("response equivalence must not establish causal attribution")


def test_simultaneous_bounds_are_rounded_conservatively() -> None:
    rule = contract()
    with localcontext() as context:
        context.prec = 50
        logarithm = (Decimal(48) / Decimal(".01")).ln()
        response = (3 * logarithm / (4 * SHOTS)).sqrt()
        baseline = (logarithm / SHOTS).sqrt()
        if Decimal(rule["response_radius_decimal"]) < response or Decimal(rule["baseline_radius_decimal"]) < baseline:
            raise AssertionError("rounded radii must cover the analytic bounds")
        if Decimal(rule["uniform_response_equivalence_separation_decimal"]) <= 0:
            raise AssertionError("fixed budget must have nonempty uniform equivalence separation")
        failure = 24 * (-4 * SHOTS * Decimal(rule["response_radius_decimal"]) ** 2 / 3).exp()
        failure += 24 * (-SHOTS * Decimal(rule["baseline_radius_decimal"]) ** 2).exp()
        if failure > Decimal(".01"):
            raise AssertionError("union-bound false-report probability exceeds frozen alpha")


def tables() -> list[dict[str, Any]]:
    return [{"batch": name, "joint_counts": [[4096, 0, 0, 0] for _ in range(3)]} for name in BATCHES]


def test_departure_and_drift_veto() -> None:
    rows = tables()
    rows[1]["joint_counts"][0] = [3072, 1024, 0, 0]
    if classify(rows)["outcome"] != "specified alternative supported":
        raise AssertionError("large selected response departure must be detected")
    rows[2]["joint_counts"][0] = [3072, 1024, 0, 0]
    if classify(rows)["outcome"] != "inconclusive within budget":
        raise AssertionError("uncertified baseline must veto response classification")


def test_overlap_is_inconclusive() -> None:
    rows = tables()
    rows[1]["joint_counts"][0] = [3686, 410, 0, 0]
    if classify(rows)["outcome"] != "inconclusive within budget":
        raise AssertionError("interval overlapping practical margin must remain inconclusive")


@pytest.mark.parametrize("defect", ["partial", "reordered", "failed", "charged", "raw-width", "source", "decoder"])
def test_invalidity_preserves_raw(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    directory = run / BATCHES[1]
    result_path = directory / "results.json"
    result = json.loads(result_path.read_text())
    manifest_path = directory / "cases.json"
    manifest = json.loads(manifest_path.read_text())
    filename = manifest["circuits"][0]["file"]
    if defect == "partial":
        result["jobs"][0]["results"][0]["shots_done"] -= 1
    elif defect == "reordered":
        result["jobs"][0]["job"]["created_on"] = "2026-10-27T19:00:00+00:00"
    elif defect == "failed":
        result["jobs"][0]["job"]["status"] = "failed"
    elif defect == "charged":
        result["transactions"] = [{"id": 1, "job": 11, "change": -1}]
    elif defect == "raw-width":
        save(directory / "raw" / f"{filename}.json", ["0" * 19] * SHOTS)
        result["jobs"][0]["results"][0]["results"] = {"0" * 19: SHOTS}
    elif defect == "source":
        path = directory / filename
        path.write_text(path.read_text().replace("measure q[4]", "measure q[5]"))
    else:
        manifest["circuits"][0]["analysis_metadata"]["canonical_early_string_offsets"] = [0, 1, 2]
        save(manifest_path, manifest)
    save(result_path, result)
    hashes = {path: digest(path) for path in run.rglob("raw/*.json")}
    if analyze(run, proposal)["outcome"] != "protocol inadmissible":
        raise AssertionError(f"{defect} must refuse inference")
    if any(digest(path) != before for path, before in hashes.items()):
        raise AssertionError("invalidity analysis changed raw evidence")


def test_missing_artifact_returns_route_failure(acquisition: tuple[Path, Path]) -> None:
    run, proposal = acquisition
    (run / BATCHES[-1] / "results.json").unlink()
    if analyze(run, proposal)["outcome"] != "implementation route unavailable":
        raise AssertionError("missing acquisition must have a frozen terminal outcome")


def test_decoder_matches_declared_destinations() -> None:
    bits = ["0"] * 20
    bits[19] = bits[4] = "1"
    raw = "".join(reversed(bits))
    result = cells(("rotated", [raw] * SHOTS, [19, 17, 18]))
    if result["joint_counts"] != [[0, 0, 0, 4096], [4096, 0, 0, 0], [4096, 0, 0, 0]]:
        raise AssertionError("rotated destination inverse decoding differs")


@pytest.mark.parametrize("defect", ["short-pause", "duplicate-batch", "malformed-jobs", "missing-timestamp"])
def test_additional_protocol_boundaries(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    directory = run / BATCHES[1]
    result_path = directory / "results.json"
    result = json.loads(result_path.read_text())
    if defect == "short-pause":
        result["jobs"][0]["job"]["created_on"] = "2026-10-27T19:00:34+00:00"
    elif defect == "duplicate-batch":
        result["jobs"][0]["job"]["batch_job_id"] = 110
        submission_path = directory / "submission.json"
        submission = json.loads(submission_path.read_text())
        submission["batch_job"] = 110
        save(submission_path, submission)
    elif defect == "malformed-jobs":
        result["jobs"] = {"invalid": "shape"}
    else:
        del result["jobs"][0]["job"]["created_on"]
    save(result_path, result)
    if analyze(run, proposal)["outcome"] != "protocol inadmissible":
        raise AssertionError(f"{defect} must refuse the fixed protocol")


@pytest.mark.parametrize(
    "relative",
    [
        "approval.json",
        "written-case-at-approval.md",
        "decision-at-approval.json",
        "terms-at-approval.json",
        "execution-window.json",
        f"{BATCHES[0]}/admission.json",
        f"{BATCHES[0]}/locked-admission.json",
        f"{BATCHES[0]}/execution-intent.json",
        f"{BATCHES[0]}/completion-admission.json",
    ],
)
def test_missing_operational_receipt_refuses(acquisition: tuple[Path, Path], relative: str) -> None:
    run, proposal = acquisition
    (run / relative).unlink()
    report = analyze(run, proposal)
    if report["outcome"] != "implementation route unavailable" or "comparisons" in report:
        raise AssertionError("missing operational evidence must prevent substantive statistical classification")


@pytest.mark.parametrize(
    "relative",
    [
        "approval.json",
        "decision-at-approval.json",
        "terms-at-approval.json",
        "execution-window.json",
        f"{BATCHES[0]}/submission.json",
        f"{BATCHES[0]}/results.json",
        f"{BATCHES[0]}/admission.json",
        f"{BATCHES[0]}/locked-admission.json",
        f"{BATCHES[0]}/execution-intent.json",
        f"{BATCHES[0]}/completion-admission.json",
    ],
)
def test_malformed_operational_schema_refuses(acquisition: tuple[Path, Path], relative: str) -> None:
    run, proposal = acquisition
    path = run / relative
    receipt = json.loads(path.read_text())
    receipt["schema"] = "unrecognized-schema"
    save(path, receipt)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "comparisons" in report:
        raise AssertionError("malformed operational evidence must prevent substantive statistical classification")


@pytest.mark.parametrize("defect", ["stale", "refused", "wrong-binding", "wrong-producer", "stale-heartbeat"])
def test_admission_must_be_bound_fresh_and_successful(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    path = run / BATCHES[0] / "admission.json"
    receipt = json.loads(path.read_text())
    if defect == "stale":
        receipt["request_started_utc"] = "2026-10-27T18:58:00+00:00"
    elif defect == "refused":
        receipt["admitted"] = False
    elif defect == "wrong-binding":
        receipt["bindings"]["campaign_sha256"] = "0" * 64
    elif defect == "wrong-producer":
        receipt["producer_sha256"] = "0" * 64
    else:
        receipt["instances"][0]["last_heartbeat"] = "2026-10-27T18:50:00+00:00"
    save(path, receipt)
    if analyze(run, proposal)["outcome"] != "protocol inadmissible":
        raise AssertionError("unsupported live admission must refuse the campaign")


@pytest.mark.parametrize("value", ["5", True, None, float("nan"), float("inf"), -1, 301])
def test_shared_execution_number_rejects_malformed(value: Any) -> None:
    from qi_tuna_destination_one_analysis import validate_execution_seconds

    with pytest.raises(ValueError):
        validate_execution_seconds(value)


@pytest.mark.parametrize("value", ["0", False, 0.0, None, -1])
def test_shared_zero_change_requires_exact_integer(value: Any) -> None:
    from qi_tuna_destination_one_analysis import validate_zero_transactions

    with pytest.raises(ValueError):
        validate_zero_transactions([{"id": 1, "job": 10, "change": value}], 10)


def test_shared_numeric_valid_boundaries() -> None:
    from qi_tuna_destination_one_analysis import validate_execution_seconds, validate_zero_transactions

    if validate_execution_seconds(0) != Decimal(0) or validate_execution_seconds(300.0) != Decimal(300):
        raise AssertionError("finite integer and floating execution endpoints must pass")
    validate_zero_transactions([{"id": 1, "job": 10, "change": 0}], 10)


@pytest.mark.parametrize("field", ["shots_requested", "shots_done", "job_id"])
def test_float_result_integer_fields_refuse(acquisition: tuple[Path, Path], field: str) -> None:
    run, proposal = acquisition
    path = run / BATCHES[0] / "results.json"
    receipt = json.loads(path.read_text())
    receipt["jobs"][0]["results"][0][field] = float(receipt["jobs"][0]["results"][0][field])
    save(path, receipt)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "positive JSON integer" not in report["reason"]:
        raise AssertionError("integer API fields must reject numerically equal floating values")


def test_completion_hash_chain_is_checked(acquisition: tuple[Path, Path]) -> None:
    run, proposal = acquisition
    path = run / BATCHES[0] / "completion-admission.json"
    receipt = json.loads(path.read_text())
    receipt["inputs"]["results.json"] = "0" * 64
    save(path, receipt)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "completion admission differs" not in report["reason"]:
        raise AssertionError("completion receipt must bind the acquired result bytes")


def refresh_completion(directory: Path) -> None:
    """Keep synthetic receipt hashes coherent while testing chronology predicates."""
    path = directory / "completion-admission.json"
    receipt = json.loads(path.read_text())
    collection = json.loads((directory / "results.json").read_text())
    receipt["collected_utc"] = collection["collected_utc"]
    receipt["inputs"] = {relative: digest(directory / relative) for relative in receipt["inputs"]}
    save(path, receipt)


def test_nominal_one_scope_is_separate(acquisition: tuple[Path, Path]) -> None:
    run, proposal = acquisition
    report = analyze(run, proposal)
    rule = report["contract"]
    if (rule["jobs"], rule["selected_response_cells"], rule["simultaneously_bounded_contrasts"]) != (3, 12, 24):
        raise AssertionError("three nominal-one jobs require their own multiplicity family")
    if {row["prepared_label"] for row in report["comparisons"]} != {1}:
        raise AssertionError("nominal-zero evidence entered the new primary endpoint")
    if rule["response_radius_decimal"] != "0.039396318627" or rule["baseline_radius_decimal"] != "0.045490950328":
        raise AssertionError("frozen three-job uncertainty radii changed")
    if list(run.glob("prepared-zero-*")):
        raise AssertionError("fixture must establish the nominal-one endpoint without nominal-zero artifacts")
    with pytest.raises(ValueError, match="three nominal-one"):
        classify(tables() + tables())


@pytest.mark.parametrize("defect", ["precedes-finish", "after-successor"])
def test_collection_chronology_is_semantic(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    directory = run / BATCHES[0]
    path = directory / "results.json"
    collection = json.loads(path.read_text())
    collection["collected_utc"] = (
        "2026-10-27T19:00:04+00:00" if defect == "precedes-finish" else "2026-10-27T19:01:01+00:00"
    )
    save(path, collection)
    refresh_completion(directory)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "collection" not in report["reason"]:
        raise AssertionError("coherent receipt hashes cannot admit contradictory raw collection chronology")


@pytest.mark.parametrize(
    "defect", ["wrong-horizon", "wrong-width", "admission-before-window", "admission-after-window"]
)
def test_execution_window_is_checked(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    path = run / "execution-window.json"
    window = json.loads(path.read_text())
    if defect == "wrong-horizon":
        window["request_initiation_timeout_seconds"] = 3600
    elif defect == "wrong-width":
        window["request_deadline_utc"] = "2026-10-27T20:58:59+00:00"
    elif defect == "admission-before-window":
        window["started_utc"] = "2026-10-27T19:00:00+00:00"
        window["request_deadline_utc"] = "2026-10-27T21:00:00+00:00"
    else:
        window["started_utc"] = "2026-10-27T16:58:00+00:00"
        window["request_deadline_utc"] = "2026-10-27T18:58:00+00:00"
    save(path, window)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "initiation window" not in report["reason"]:
        raise AssertionError("unqualified window cannot admit the completed response case")


@pytest.mark.parametrize("defect", ["schema", "empty-text", "duplicate-url", "malformed-html-hash", "naive-time"])
def test_terms_schema_and_page_provenance(defect: str) -> None:
    from qi_tuna_destination_one_analysis import validate_terms

    path = ROOT / "docs/evidence/tuna-projector-geometry/readout-destination-terms-text.json"
    terms = json.loads(path.read_text())
    if defect == "schema":
        terms["schema"] = "unknown"
    elif defect == "empty-text":
        terms["pages"][0]["text"] = ""
        terms["pages"][0]["text_sha256"] = hashlib.sha256(b"").hexdigest()
    elif defect == "duplicate-url":
        terms["pages"][0]["url"] = terms["pages"][1]["url"]
    elif defect == "malformed-html-hash":
        terms["pages"][0]["html_sha256"] = "wrong"
    else:
        terms["pages"][0]["observed_utc"] = "2026-10-27T19:00:00"
    with pytest.raises(ValueError):
        validate_terms(terms)


@pytest.mark.parametrize(
    "defect",
    [
        "false-admission",
        "nonempty-failures",
        "manifest-hash",
        "runner-hash",
        "helper-hash",
        "enabled",
        "status",
        "topology",
        "gateset",
        "compiler-hash",
        "queue",
        "queue-scope",
        "pause",
        "transaction-rows",
        "zero-ledger",
        "heartbeat",
        "heartbeat-policy",
        "heartbeat-age",
        "instance-status",
        "missing-instances",
        "limits",
        "before-initial-observation",
        "after-provider-creation",
        "malformed-root",
    ],
)
def test_locked_admission_semantics_survive_refreshed_hashes(acquisition: tuple[Path, Path], defect: str) -> None:
    run, proposal = acquisition
    directory = run / BATCHES[0]
    path = directory / "locked-admission.json"
    locked = json.loads(path.read_text())
    if defect == "false-admission":
        locked["admitted"] = False
    elif defect == "nonempty-failures":
        locked["failures"] = ["synthetic admission refusal"]
    elif defect == "manifest-hash":
        locked["cases_sha256"] = "0" * 64
    elif defect == "runner-hash":
        locked["runner_sha256"] = "0" * 64
    elif defect == "helper-hash":
        locked["submission_helper_sha256"] = "0" * 64
    elif defect == "enabled":
        locked["enabled"] = False
    elif defect == "status":
        locked["status"] = "offline"
    elif defect == "topology":
        locked["topology"] = []
    elif defect == "gateset":
        locked["gateset"] = []
    elif defect == "compiler-hash":
        locked["compiler_config_sha256"] = "0" * 64
    elif defect == "queue":
        locked["queued_batches"] = 1
    elif defect == "queue-scope":
        locked["queue_user_only"] = False
    elif defect == "pause":
        locked["hardware_pause_left_seconds"] = 30
    elif defect == "transaction-rows":
        locked["account_transaction_rows"] = -1
    elif defect == "zero-ledger":
        locked["all_transaction_changes_zero"] = False
    elif defect == "heartbeat":
        locked["instances"][0]["last_heartbeat"] = "2026-10-27T18:50:00+00:00"
    elif defect == "heartbeat-policy":
        locked["heartbeat_max_age_seconds"] = 121
    elif defect == "heartbeat-age":
        locked["instances"][0]["age_seconds"] = 2.5
    elif defect == "instance-status":
        locked["instances"][0]["status"] = "offline"
    elif defect == "missing-instances":
        locked["instances"] = []
    elif defect == "limits":
        locked["limits"]["batch_circuits"] = 3
    elif defect == "before-initial-observation":
        locked["observed_utc"] = "2026-10-27T18:59:58+00:00"
    elif defect == "after-provider-creation":
        locked["observed_utc"] = "2026-10-27T19:00:01+00:00"
    else:
        locked = []
    save(path, locked)
    refresh_completion(directory)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "comparisons" in report:
        raise AssertionError("semantic locked-admission faults must prevent scientific classification")
    if "completion admission differs" in report["reason"]:
        raise AssertionError("regression must exercise locked semantics after refreshing completion hashes")


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "identifier",
        "nqubits",
        "is_hardware",
        "supports_raw_data",
        "protocol_version",
        "job_execution_time_limit",
        "max_jobs_per_batch_job",
        "max_number_of_shots",
        "batchjobs_per_queue_limit",
        "default_compiler_config",
    ],
)
def test_locked_admission_checks_every_structural_field(acquisition: tuple[Path, Path], field: str) -> None:
    run, proposal = acquisition
    directory = run / BATCHES[0]
    path = directory / "locked-admission.json"
    locked = json.loads(path.read_text())
    locked["backend"][field] = None
    save(path, locked)
    refresh_completion(directory)
    report = analyze(run, proposal)
    if report["outcome"] != "protocol inadmissible" or "comparisons" in report:
        raise AssertionError(f"under-lock structural drift in {field} must refuse classification")
    if "completion admission differs" in report["reason"]:
        raise AssertionError("regression must validate structure instead of relying on stale completion hashes")


def test_locked_admission_is_hash_bound_and_retained_in_provenance(acquisition: tuple[Path, Path]) -> None:
    run, proposal = acquisition
    report = analyze(run, proposal)
    for name in BATCHES:
        relative = f"{name}/locked-admission.json"
        expected = digest(run / relative)
        job = next(row for row in report["jobs"] if row["batch"] == name)
        if report["inputs"].get(relative) != expected or job["inputs"].get(relative) != expected:
            raise AssertionError("final analysis must bind every decisive under-lock admission receipt")
    path = run / BATCHES[0] / "locked-admission.json"
    locked = json.loads(path.read_text())
    locked["boundary"] = "A harmless content change still changes the decisive evidence bytes."
    save(path, locked)
    refused = analyze(run, proposal)
    if refused["outcome"] != "protocol inadmissible" or "completion admission differs" not in refused["reason"]:
        raise AssertionError("completion receipt must bind the exact locked-admission bytes")
