"""The Ascella predecessor case is one eight-iteration job of retained seed-0 settings."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import ascella_predecessor_case as case
import pytest
import qd_platform as qd

ROOT = Path(__file__).resolve().parents[2]
CASE = case.CASE
SOURCE = ROOT / "results/quandela/cases/ascella_signed_coherence/job-00"
JOB00_RUN = ROOT / "results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00"
JOB02_RUN = ROOT / "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02"


def test_contrast_coefficients_expose_even_and_odd_drift_directions() -> None:
    positions = (-3, -1, 1, 3)
    common = tuple(Fraction(value, 2) for value in (1, -1, -1, 1))
    reversal = tuple(Fraction(value, 2) for value in (-1, 1, -1, 1))
    registered = manifest()["preregistered"]
    if (
        tuple(map(Fraction, registered["common_coefficients"])) != common
        or tuple(map(Fraction, registered["reversal_coefficients"])) != reversal
    ):
        raise AssertionError("the coefficient analysis must match the frozen acquisition case")
    for weights, expected in ((common, (0, 0, 8, 0, 80)), (reversal, (0, 2, 0, 26, 0))):
        moments = tuple(
            sum(weight * position**degree for weight, position in zip(weights, positions, strict=True))
            for degree in range(5)
        )
        if moments != expected:
            raise AssertionError("the contrast must expose its exact polynomial drift sensitivity")
    if sum(weight for weight, assigned in zip(common, (True, False, False, True), strict=True) if assigned) != 1:
        raise AssertionError("the common contrast must have unit additive-condition gain")


def test_fixed_allocation_has_explicit_sufficient_power_regions() -> None:
    """The union event bounds decision power as well as interval precision."""
    decision_factor = 12 * math.log(2) + math.log(8 / 0.05)
    power_factor = 12 * math.log(2) + math.log(8 / 0.20)
    radius_sum = 2 * (math.sqrt(decision_factor) + math.sqrt(power_factor)) / math.sqrt(2 * 32768)
    if not math.isclose(radius_sum, 0.0556616975517971, abs_tol=1e-15):
        raise AssertionError("decision and power deviations both enter the sufficient region")
    for population, expected in ((0.15, 40610), (0.16, 28201), (0.0462, 35076), (0.0654, 84803)):
        required = 2 * (math.sqrt(decision_factor) + math.sqrt(power_factor)) ** 2 / (population - 0.1) ** 2
        if math.floor(required) + 1 != expected:
            raise AssertionError("the sensitivity table must size decision power rather than radius alone")
    if not math.isclose(2 * case.subset_radius(8, 32768), 0.028590910871208422, abs_tol=1e-15):
        raise AssertionError("the power calculation must use the frozen case's simultaneous radius")


def test_eight_target_successor_still_accepts_a_cubic_drift_counterexample() -> None:
    positions = (-7, -5, -3, -1, 1, 3, 5, 7)
    weights = tuple(Fraction(value, 4) for value in (1, -1, -1, 1, -1, 1, 1, -1))
    moments = tuple(
        sum(weight * position**degree for weight, position in zip(weights, positions, strict=True))
        for degree in range(4)
    )
    if moments != (0, 0, 0, -96):
        raise AssertionError("the successor removes quadratic index drift while retaining cubic sensitivity")
    counts = (263, 10509, 15115, 16337, 16431, 17653, 22259, 32505)
    if counts != tuple(16384 + 47 * position**3 for position in positions):
        raise AssertionError("the falsifier must contain pure cubic drift")
    contrast = sum(weight * Fraction(count, 32768) for weight, count in zip(weights, counts, strict=True))
    if abs(contrast) != Fraction(141, 1024) or float(abs(contrast)) - 2 * case.subset_radius(16, 32768) <= 0.1:
        raise AssertionError("the signed successor can clear the margin without a predecessor effect")


SCHEDULE = (
    ("A", "theta2-x-arm1", "predecessor", 0),
    ("A", "theta2-x-arm0", "target", 1),
    ("A", "theta0-x-arm0", "predecessor", 0),
    ("A", "theta2-x-arm0", "target", 1),
    ("B", "theta0-x-arm0", "predecessor", 0),
    ("B", "theta2-x-arm0", "target", 1),
    ("B", "theta2-x-arm1", "predecessor", 0),
    ("B", "theta2-x-arm0", "target", 1),
)


def manifest() -> dict[str, Any]:
    return json.loads((CASE / "cases.json").read_text(encoding="utf-8"))


@pytest.mark.audit
def test_check_reproduces_the_retained_bytes() -> None:
    rebuilt = case.check()
    if rebuilt["family"] != "ascella_predecessor" or rebuilt["platforms"] != ["qpu:ascella"]:
        raise AssertionError(rebuilt["platforms"])
    if rebuilt["command"] != "sample_count" or rebuilt["mitigations"] != [] or rebuilt["iterations"] != 8:
        raise AssertionError(rebuilt["iterations"])


@pytest.mark.audit
def test_schedule_uses_job00_columns_on_odd_target_slots() -> None:
    settings = manifest()["settings"]
    source = {row["name"]: row for row in json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))["settings"]}
    actual = [(row["order"], row["source_name"], row["role"], row["slot"]) for row in settings]
    if actual != list(SCHEDULE) or [row["observation_index"] for row in settings] != list(range(8)):
        raise AssertionError(actual)
    if (CASE / "circuit.json").read_bytes() != (SOURCE / "circuit.json").read_bytes():
        raise AssertionError("circuit.json is not the job-00 template bytes")
    for row in settings:
        origin = source[row["source_name"]]
        if row["source_observation_index"] != origin["observation_index"]:
            raise AssertionError(row["name"])
        for key in ("circuit_params", "column", "operator", "compilation_seed"):
            if row[key] != origin[key]:
                raise AssertionError(f"{row['name']} {key}")
        if "mutation" in row["source_name"] or row["role"] not in {"predecessor", "target"}:
            raise AssertionError(row["name"])


@pytest.mark.audit
def test_requested_separation_radius_and_credit_hold() -> None:
    record = manifest()
    source = {row["name"]: row for row in json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))["settings"]}
    laws = {
        name: case.probabilities(source[name]["column"]) for name in ("theta2-x-arm0", "theta2-x-arm1", "theta0-x-arm0")
    }
    pairs = (
        ("theta2-x-arm0", "theta2-x-arm1"),
        ("theta2-x-arm0", "theta0-x-arm0"),
        ("theta2-x-arm1", "theta0-x-arm0"),
    )
    for left, right in pairs:
        distance = case.total_variation(laws[left], laws[right])
        if distance < 0.5:
            raise AssertionError(f"{left} {right} {distance}")
    epsilon = case.subset_radius(8, 32768)
    registered = record["preregistered"]
    if registered["two_law_radius"] != 2.0 * epsilon or not registered["two_law_radius"] < 0.1:
        raise AssertionError(registered["two_law_radius"])
    if record["max_samples"] != 262144 or record["max_shots"] != 262144:
        raise AssertionError((record["max_samples"], record["max_shots"]))
    if record["max_credits"] != case.charge(32768) or registered["expected_credits"] != case.charge(32768):
        raise AssertionError(record["max_credits"])
    if registered["contrast_pairs"] != [[1, 3], [7, 5]] or registered["target_only"] != "absent":
        raise AssertionError(registered["contrast_pairs"])
    if registered["auto_retry"] is not False:
        raise AssertionError(registered["auto_retry"])


@pytest.mark.audit
def test_frozen_circuits_match_the_retained_blobs() -> None:
    identity = manifest()["preregistered"]["compilation_identity"]
    source_cases = json.loads((JOB00_RUN / "cases.json").read_text(encoding="utf-8"))
    source_results = json.loads((JOB00_RUN / "results.json").read_text(encoding="utf-8"))
    index = next(i for i, row in enumerate(source_cases["settings"]) if row["name"] == "theta2-x-arm0")
    target = case.sha256_text(source_results["iterations"][index]["result_fields"]["computed_circuit"])
    if identity["target"]["computed_circuit_sha256"] != target:
        raise AssertionError(target)
    anchors = json.loads((JOB02_RUN / "cases.json").read_text(encoding="utf-8"))
    anchor_results = json.loads((JOB02_RUN / "results.json").read_text(encoding="utf-8"))
    hashed = [
        case.sha256_text(row["result_fields"]["computed_circuit"])
        for setting, row in zip(anchors["settings"], anchor_results["iterations"], strict=True)
        if setting["compilation_seed"] == source_cases["settings"][index]["compilation_seed"]
    ]
    if hashed != [target] * 8:
        raise AssertionError(hashed[:1])


@pytest.mark.parametrize("processor_status", ["available", "running"])
def test_running_platform_admission_preserves_queue_and_status_gates(
    monkeypatch: pytest.MonkeyPatch, processor_status: str
) -> None:
    record = manifest()
    if record["preregistered"]["admitted_platform_statuses"] != ["available", "running"]:
        raise AssertionError("the written case must explicitly admit queueing")
    row = {"status": "running", "max_duration": 300, "price_per_shot": 1e-6, "type": "qpu"}
    processor = {"status": processor_status, "perfs": {}}
    counters = {"num_concurrent_jobs": 0, "num_jobs_in_queue": 0}
    monkeypatch.setattr(qd, "explorer_row", lambda platform: row)
    monkeypatch.setattr(qd, "get", lambda route: processor)
    monkeypatch.setattr(qd, "availability", lambda: counters)
    monkeypatch.setattr(qd, "hom_warning", lambda *args: None)
    monkeypatch.setattr(
        qd,
        "payload",
        lambda *args: {"estimated_shots": 262144, "body": {}, "versions": {}, "payload_version_basis": "test"},
    )

    def planned() -> dict[str, Any]:
        return qd.plan(CASE, "qpu:ascella", 1.032768, 40, 1, ("running",))

    admitted = planned()
    if admitted["admitted_statuses"] != ["available", "running"]:
        raise AssertionError(admitted)
    with pytest.raises(qd.PlatformError, match="is running"):
        qd.plan(CASE, "qpu:ascella", 1.032768, 40, 1)
    for field in counters:
        counters[field] = 1
        with pytest.raises(qd.PlatformError, match="running or queued"):
            planned()
        counters[field] = 0
    for status in ("calibration", "maintenance"):
        processor["status"] = status
        with pytest.raises(qd.PlatformError, match="processor is"):
            planned()
    processor["status"] = processor_status
    row["status"] = "maintenance"
    with pytest.raises(qd.PlatformError, match="is maintenance"):
        planned()


@pytest.fixture
def reviewed_submission(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """A real checkpoint and submit path use recorded transport and fresh-plan doubles."""
    import copy

    monkeypatch.setattr(qd, "ROOT", tmp_path)
    source_names = (
        "scripts/qd_platform.py",
        "scripts/ascella_predecessor_case.py",
        "scripts/ascella_predecessor_analysis.py",
        "scripts/ascella_experiment_analysis.py",
        "scripts/experiment_analysis.py",
        "gororoba_quantum/parallel.py",
    )
    for name in source_names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("frozen source")
    sources = {name: qd.sha256_bytes((tmp_path / name).read_bytes()) for name in source_names}
    directory = tmp_path / "run"
    directory.mkdir()
    circuit = b"{}\n"
    (directory / "circuit.json").write_bytes(circuit)
    request = {
        "family": "ascella_predecessor",
        "analysis_sources": sources,
        "circuit": {"file": "circuit.json", "sha256": qd.sha256_bytes(circuit)},
    }
    (directory / "cases.json").write_text(json.dumps(request))

    def load(path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
        raw = (path / "cases.json").read_bytes()
        return json.loads(raw), {}, qd.sha256_bytes(raw)

    monkeypatch.setattr(qd, "load_case", load)
    body = {"process_id": "00000000-0000-4000-8000-000000000001", "payload": {"command": "sample_count"}}
    checked = {
        "platform": "qpu:ascella",
        "cases_sha256": load(directory)[2],
        "body": body,
        "body_sha256": qd.sha256_bytes(json.dumps(body, sort_keys=True).encode()),
        "versions": {"perceval-quandela": "1.3.1"},
        "payload_version_basis": "declared",
        "estimated_shots": 262144,
        "admitted_statuses": ["available", "running"],
    }
    monkeypatch.setattr(qd, "plan", lambda *args: copy.deepcopy(checked))
    monkeypatch.setenv(qd.TOKEN_ENV, str(tmp_path / "token"))
    monkeypatch.setattr(qd, "get", lambda route: [])
    sent: list[dict[str, Any]] = []

    def post(method: str, route: str, body: dict[str, Any]) -> dict[str, str]:
        sent.append(copy.deepcopy(body))
        return {"job_id": "recorded-job"}

    monkeypatch.setattr(qd, "request", post)
    return {"directory": directory, "checked": checked, "sent": sent, "root": tmp_path}


def prepare_review(fixture: dict[str, Any]) -> tuple[Path, str]:
    path = fixture["root"] / "review.json"
    qd.prepare_acquisition_review(fixture["directory"], "qpu:ascella", 1.032768, 40, 1, ("running",), path)
    return path, qd.sha256_bytes(path.read_bytes())


def submit_bound(fixture: dict[str, Any], path: Path, expected: str) -> dict[str, Any]:
    return qd.submit(
        fixture["directory"],
        "qpu:ascella",
        "case-specific approval",
        1.032768,
        40,
        1,
        ("running",),
        reviewed_packet=path,
        reviewed_sha256=expected,
    )


def test_reviewed_submit_pins_only_transport_uuid_and_posts_exact_reviewed_body(
    reviewed_submission: dict[str, Any],
) -> None:
    path, expected = prepare_review(reviewed_submission)
    approved = json.loads(path.read_text())["binding"]["body"]
    reviewed_submission["checked"]["body"]["process_id"] = "00000000-0000-4000-8000-000000000002"
    result = submit_bound(reviewed_submission, path, expected)
    if reviewed_submission["sent"] != [approved] or result["reviewed_packet_sha256"] != expected:
        raise AssertionError("the actual POST must equal the complete reviewed body")


@pytest.mark.parametrize("mutation", ["source", "body", "versions", "packet", "policy", "circuit", "case"])
def test_reviewed_submit_refuses_binding_mutations_before_post(
    reviewed_submission: dict[str, Any], mutation: str
) -> None:
    path, expected = prepare_review(reviewed_submission)
    root = reviewed_submission["root"]
    checked = reviewed_submission["checked"]
    if mutation == "source":
        (root / "scripts/ascella_predecessor_analysis.py").write_text("changed source")
    elif mutation == "body":
        checked["body"]["payload"]["command"] = "changed"
    elif mutation == "versions":
        checked["versions"]["perceval-quandela"] = "changed"
    elif mutation == "packet":
        path.write_text(path.read_text() + " ")
    elif mutation == "circuit":
        (reviewed_submission["directory"] / "circuit.json").write_text("changed circuit")
    elif mutation == "case":
        checked["cases_sha256"] = "0" * 64
    if mutation == "policy":
        with pytest.raises(qd.PlatformError):
            qd.submit(
                reviewed_submission["directory"],
                "qpu:ascella",
                "approval",
                1.0,
                40,
                1,
                ("running",),
                reviewed_packet=path,
                reviewed_sha256=expected,
            )
    else:
        with pytest.raises(qd.PlatformError):
            submit_bound(reviewed_submission, path, expected)
    if reviewed_submission["sent"]:
        raise AssertionError("a failed binding must never call POST")


def test_plain_ascella_submit_requires_review_anchor(reviewed_submission: dict[str, Any]) -> None:
    with pytest.raises(qd.PlatformError, match="review"):
        qd.submit(reviewed_submission["directory"], "qpu:ascella", "approval", 1.032768, 40, 1, ("running",))
    if reviewed_submission["sent"]:
        raise AssertionError("the generic CLI route must enforce the reviewed binding")


def test_consumed_review_refuses_a_copied_case_directory(reviewed_submission: dict[str, Any]) -> None:
    import shutil

    path, expected = prepare_review(reviewed_submission)
    original = reviewed_submission["directory"]
    copy = reviewed_submission["root"] / "copied-run"
    shutil.copytree(original, copy)
    submit_bound(reviewed_submission, path, expected)
    reviewed_submission["directory"] = copy
    with pytest.raises(qd.PlatformError, match="consumed"):
        submit_bound(reviewed_submission, path, expected)
    if len(reviewed_submission["sent"]) != 1:
        raise AssertionError("copying a run directory must not renew an attempt")


def test_uncertain_post_consumes_case_wide_attempt(
    reviewed_submission: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import shutil

    path, expected = prepare_review(reviewed_submission)
    copy = reviewed_submission["root"] / "copy-before-post"
    shutil.copytree(reviewed_submission["directory"], copy)

    def lost(*args: Any, **kwargs: Any) -> None:
        raise qd.UnansweredError("answer lost")

    monkeypatch.setattr(qd, "request", lost)
    with pytest.raises(qd.UnansweredError):
        submit_bound(reviewed_submission, path, expected)
    reviewed_submission["directory"] = copy
    with pytest.raises(qd.PlatformError, match="consumed"):
        submit_bound(reviewed_submission, path, expected)


def test_submit_cli_enforces_and_accepts_review_binding(
    reviewed_submission: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    arguments = [
        "qd_platform.py",
        "submit",
        str(reviewed_submission["directory"]),
        "--platform",
        "qpu:ascella",
        "--max-credits",
        "1.032768",
        "--expected-seconds",
        "40",
        "--per-job-credits",
        "1",
        "--admit-status",
        "running",
        "--approval",
        "case-specific approval",
    ]
    monkeypatch.setattr(sys, "argv", arguments)
    with pytest.raises(SystemExit, match="review"):
        qd.main()
    path, checksum = prepare_review(reviewed_submission)
    monkeypatch.setattr(sys, "argv", arguments + ["--reviewed-packet", str(path), "--reviewed-sha256", checksum])
    if qd.main() != 0 or len(reviewed_submission["sent"]) != 1:
        raise AssertionError("the documented CLI must enforce and execute the bound submit path")


def test_case_wide_guard_serializes_competing_directories(reviewed_submission: dict[str, Any]) -> None:
    import shutil
    from concurrent.futures import ThreadPoolExecutor

    path, checksum = prepare_review(reviewed_submission)
    first = reviewed_submission["directory"]
    second = reviewed_submission["root"] / "concurrent-copy"
    shutil.copytree(first, second)

    def attempt(directory: Path) -> str:
        try:
            qd.submit(
                directory,
                "qpu:ascella",
                "approval",
                1.032768,
                40,
                1,
                ("running",),
                reviewed_packet=path,
                reviewed_sha256=checksum,
            )
        except qd.PlatformError:
            return "refused"
        return "submitted"

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(attempt, (first, second)))
    if sorted(outcomes) != ["refused", "submitted"] or len(reviewed_submission["sent"]) != 1:
        raise AssertionError("competing copies must consume exactly one case-wide attempt")


def test_review_refuses_an_omitted_analyzer_dependency(reviewed_submission: dict[str, Any]) -> None:
    path = reviewed_submission["directory"] / "cases.json"
    request = json.loads(path.read_text())
    request["analysis_sources"].pop("gororoba_quantum/parallel.py")
    path.write_text(json.dumps(request))
    with pytest.raises(qd.PlatformError, match="source"):
        prepare_review(reviewed_submission)


def test_case_swap_during_plan_cannot_bypass_required_review(
    reviewed_submission: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import copy

    path = reviewed_submission["directory"] / "cases.json"
    request = json.loads(path.read_text())
    request["family"] = "other"
    diagnostic_sources = request.pop("analysis_sources")
    path.write_text(json.dumps(request))

    def replace_case(*args: Any) -> dict[str, Any]:
        request["family"] = "ascella_predecessor"
        request["analysis_sources"] = diagnostic_sources
        path.write_text(json.dumps(request))
        checked = copy.deepcopy(reviewed_submission["checked"])
        checked["cases_sha256"] = qd.sha256_bytes(path.read_bytes())
        return checked

    monkeypatch.setattr(qd, "plan", replace_case)
    with pytest.raises(qd.PlatformError, match="case changed"):
        qd.submit(reviewed_submission["directory"], "qpu:ascella", "approval", 1.032768, 40, 1, ("running",))
    if reviewed_submission["sent"]:
        raise AssertionError("the fresh case must remain identical to the admission gate snapshot")


def test_source_change_during_usage_read_refuses_before_consumption(
    reviewed_submission: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    path, expected = prepare_review(reviewed_submission)

    def mutate(route: str) -> list[Any]:
        (reviewed_submission["root"] / "scripts/ascella_predecessor_analysis.py").write_text("changed")
        return []

    monkeypatch.setattr(qd, "get", mutate)
    with pytest.raises(qd.PlatformError, match="source changed"):
        submit_bound(reviewed_submission, path, expected)
    if reviewed_submission["sent"] or (reviewed_submission["root"] / "reviewed-acquisition-attempts").exists():
        raise AssertionError("post-read verification must reject source drift before consuming the attempt")


def test_request_wire_bytes_use_the_reviewed_canonical_json(monkeypatch: pytest.MonkeyPatch) -> None:
    import contextlib
    import io
    from types import SimpleNamespace

    body = {"z": "last", "a": {"y": 2, "b": 1}}
    sent: list[bytes] = []

    def opened(call: Any, timeout: int) -> Any:
        sent.append(call.data)
        return contextlib.nullcontext(io.BytesIO(b'{"ok": true}'))

    monkeypatch.setattr(qd, "OPENER", SimpleNamespace(open=opened))
    qd.request("POST", "/api/jobs", auth=False, body=body)
    if sent != [json.dumps(body, sort_keys=True).encode("utf-8")]:
        raise AssertionError("the actual HTTP bytes must equal the reviewed canonical encoding")


def test_renaming_diagnostic_family_preserves_required_review(reviewed_submission: dict[str, Any]) -> None:
    path = reviewed_submission["directory"] / "cases.json"
    request = json.loads(path.read_text())
    request["family"] = "renamed-diagnostic"
    path.write_text(json.dumps(request))
    with pytest.raises(qd.PlatformError, match="review"):
        qd.submit(reviewed_submission["directory"], "qpu:ascella", "approval", 1.032768, 40, 1, ("running",))
    if reviewed_submission["sent"]:
        raise AssertionError("diagnostic analyzer identity must retain the reviewed-acquisition gate")
