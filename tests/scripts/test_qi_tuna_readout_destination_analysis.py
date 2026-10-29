"""Frozen response inference accepts arbitrary dependence while refusing scope and ordering defects."""

import datetime as dt
import hashlib
import json
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

import pytest
from qi_tuna_readout_destination_analysis import BATCHES, ROOT, SHOTS, analyze, cells, classify, contract, digest
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
        shots = [("0" if index < 3 else "1") * 20] * SHOTS
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
        "batches": batches,
        "analysis_contract": {
            "file": "scripts/qi_tuna_readout_destination_analysis.py",
            "sha256": digest(ROOT / "scripts/qi_tuna_readout_destination_analysis.py"),
            "mathematical_note": {
                "file": "docs/evidence/tuna-projector-geometry/destination-response-uncertainty.md",
                "sha256": digest(ROOT / "docs/evidence/tuna-projector-geometry/destination-response-uncertainty.md"),
            },
        },
    }
    plan.update(
        {
            "shots_total": 24576,
            "provider_execution_ceiling_seconds": 1800,
            "expected_execution_seconds_decimal": "29.533215",
            "admission_max_age_seconds": 60,
            "heartbeat_max_age_seconds": 120,
            "producer_inputs": {
                "scripts/qi_tuna_destination_sequential_run.py": digest(
                    ROOT / "scripts/qi_tuna_destination_sequential_run.py"
                )
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
            "schema": "qi-tuna-sequential-approval-v1",
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
                "bindings": bindings,
                "producer_sha256": plan["producer_inputs"]["scripts/qi_tuna_destination_sequential_run.py"],
                "request_started_utc": (created - dt.timedelta(seconds=5)).isoformat(),
                "observed_utc": (created - dt.timedelta(seconds=1)).isoformat(),
            }
        )
        admission["instances"] = [
            {"status": "idle", "last_heartbeat": (created - dt.timedelta(seconds=2)).isoformat(), "age_seconds": 1.0}
        ]
        save(directory / "admission.json", admission)
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
                "schema": "qi-tuna-sequential-completion-v1",
                "batch": name,
                "job": job["id"],
                "batch_job": job["batch_job_id"],
                "created_on": job["created_on"],
                "queued_at": job["queued_at"],
                "finished_at": job["finished_at"],
                "execution_seconds_decimal": "5",
                "inputs": {
                    key: digest(directory / key)
                    for key in ("cases.json", filename, "submission.json", "results.json", f"raw/{filename}.json")
                },
            },
        )
    return run, proposal


def test_complete_fixed_case(acquisition: tuple[Path, Path]) -> None:
    result = analyze(*acquisition)
    if result["outcome"] != "objective established within scope" or len(result["comparisons"]) != 24:
        raise AssertionError(result)
    if result["attribution_status"] != "unresolved" or result["physical_continuation_admitted"]:
        raise AssertionError("response equivalence must not establish causal attribution")


def test_simultaneous_bounds_are_rounded_conservatively() -> None:
    rule = contract()
    with localcontext() as context:
        context.prec = 50
        logarithm = (Decimal(96) / Decimal(".01")).ln()
        response = (3 * logarithm / (4 * SHOTS)).sqrt()
        baseline = (logarithm / SHOTS).sqrt()
        if Decimal(rule["response_radius_decimal"]) < response or Decimal(rule["baseline_radius_decimal"]) < baseline:
            raise AssertionError("rounded radii must cover the analytic bounds")
        if Decimal(rule["uniform_response_equivalence_separation_decimal"]) <= 0:
            raise AssertionError("fixed budget must have nonempty uniform equivalence separation")
        failure = 48 * (-4 * SHOTS * Decimal(rule["response_radius_decimal"]) ** 2 / 3).exp()
        failure += 48 * (-SHOTS * Decimal(rule["baseline_radius_decimal"]) ** 2).exp()
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
        f"{BATCHES[0]}/admission.json",
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
        f"{BATCHES[0]}/submission.json",
        f"{BATCHES[0]}/results.json",
        f"{BATCHES[0]}/admission.json",
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
    from qi_tuna_readout_destination_analysis import validate_execution_seconds

    with pytest.raises(ValueError):
        validate_execution_seconds(value)


@pytest.mark.parametrize("value", ["0", False, 0.0, None, -1])
def test_shared_zero_change_requires_exact_integer(value: Any) -> None:
    from qi_tuna_readout_destination_analysis import validate_zero_transactions

    with pytest.raises(ValueError):
        validate_zero_transactions([{"id": 1, "job": 10, "change": value}], 10)


def test_shared_numeric_valid_boundaries() -> None:
    from qi_tuna_readout_destination_analysis import validate_execution_seconds, validate_zero_transactions

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
