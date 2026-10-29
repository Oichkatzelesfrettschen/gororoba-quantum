"""Encoding reconciliation preserves both frozen analysis files and rejects semantic or byte drift."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import qi_tuna_destination_analysis_receipt as reconciliation
from qi_tuna_destination_one_analysis import BATCHES, ROOT, analyze, digest, json_bytes
from tests.scripts.test_qi_tuna_destination_one_analysis import acquisition as acquisition


def save(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def rebind_plan(run: Path, proposal: Path, campaign: dict[str, Any]) -> None:
    save(run / "sequence-plan.json", campaign)
    save(proposal / "campaign.json", campaign)
    campaign_hash = digest(run / "sequence-plan.json")
    marker = json.loads((run / "campaign.json").read_bytes())
    marker["plan_sha256"] = campaign_hash
    save(run / "campaign.json", marker)
    decision = json.loads((run / "decision-at-approval.json").read_bytes())
    decision["campaign_sha256"] = campaign_hash
    save(run / "decision-at-approval.json", decision)
    approval = json.loads((run / "approval.json").read_bytes())
    approval["campaign_sha256"] = campaign_hash
    approval["decision_sha256"] = digest(run / "decision-at-approval.json")
    save(run / "approval.json", approval)
    for name in BATCHES:
        directory = run / name
        admission = json.loads((directory / "admission.json").read_bytes())
        admission["bindings"]["campaign_sha256"] = campaign_hash
        admission["bindings"]["decision_sha256"] = approval["decision_sha256"]
        save(directory / "admission.json", admission)
        intent = json.loads((directory / "execution-intent.json").read_bytes())
        intent["plan_sha256"] = campaign_hash
        save(directory / "execution-intent.json", intent)


def complete_state(run: Path, outcome: str) -> None:
    save(
        run / "execution-state.json",
        {
            "schema": "qi-tuna-destination-one-state-v1",
            "phase": "complete",
            "completed": [json.loads((run / name / "completion-admission.json").read_bytes()) for name in BATCHES],
            "active_batch": BATCHES[-1],
            "analysis_outcome": outcome,
            "observed_utc": "2026-10-27T19:02:07+00:00",
        },
    )


@pytest.fixture
def encoding_case(acquisition: tuple[Path, Path]) -> tuple[Path, Path]:
    run, proposal = acquisition
    campaign = json.loads((run / "sequence-plan.json").read_bytes())
    campaign["producer_inputs"]["scripts/qi_platform.py"] = digest(ROOT / "scripts/qi_platform.py")
    rebind_plan(run, proposal, campaign)
    report = analyze(run, proposal)
    if report["outcome"] != "objective established within scope":
        raise AssertionError(report)
    complete_state(run, report["outcome"])
    (run / "analysis.json").write_bytes((json.dumps(report, indent=1) + "\n").encode())
    (run / "analysis-canonical.json").write_bytes(json_bytes(report))
    return run, proposal


def observations(run: Path) -> dict[str, str]:
    return {path.relative_to(run).as_posix(): digest(path) for path in run.rglob("*") if path.is_file()}


def test_both_exact_encodings_replay_and_preserve_inputs(encoding_case: tuple[Path, Path]) -> None:
    run, proposal = encoding_case
    before = observations(run)
    first = reconciliation.receipt(run, proposal)
    second = reconciliation.receipt(run, proposal)
    if first != second or first["outcome"] != "objective established within scope":
        raise AssertionError("receipt must deterministically retain the frozen primary decision")
    if not first["parsed_objects_and_numbers_identical"] or not first["decision_identical"]:
        raise AssertionError("both exact byte contracts must describe the same fresh report")
    if first["inputs"]["analysis.json"] == first["inputs"]["analysis-canonical.json"]:
        raise AssertionError("valid runtime and canonical encodings must retain their distinct bytes")
    if first["frozen_sources"]["scripts/qi_platform.py"] != digest(ROOT / "scripts/qi_platform.py"):
        raise AssertionError("receipt must bind the frozen runtime writer")
    if observations(run) != before:
        raise AssertionError("read-only reconciliation changed retained input bytes or file membership")


@pytest.mark.parametrize("name", ["analysis.json", "analysis-canonical.json"])
def test_semantic_analysis_mutation_refuses(encoding_case: tuple[Path, Path], name: str) -> None:
    run, proposal = encoding_case
    report = json.loads((run / name).read_bytes())
    report["comparisons"][0]["difference_decimal"] = "0.25"
    content = (json.dumps(report, indent=1) + "\n").encode() if name == "analysis.json" else json_bytes(report)
    (run / name).write_bytes(content)
    before = observations(run)
    with pytest.raises(ValueError, match="byte contract"):
        reconciliation.receipt(run, proposal)
    if observations(run) != before:
        raise AssertionError("refusal changed retained evidence")


@pytest.mark.parametrize(
    ("name", "encoding"),
    [
        ("analysis.json", "sorted-indent-one"),
        ("analysis.json", "canonical"),
        ("analysis.json", "missing-newline"),
        ("analysis-canonical.json", "runtime"),
        ("analysis-canonical.json", "compact"),
        ("analysis-canonical.json", "extra-newline"),
    ],
)
def test_equivalent_json_with_wrong_byte_format_refuses(
    encoding_case: tuple[Path, Path], name: str, encoding: str
) -> None:
    run, proposal = encoding_case
    path = run / name
    value = json.loads(path.read_bytes())
    if encoding == "sorted-indent-one":
        content = (json.dumps(value, indent=1, sort_keys=True) + "\n").encode()
    elif encoding == "canonical":
        content = json_bytes(value)
    elif encoding == "missing-newline":
        content = path.read_bytes().rstrip(b"\n")
    elif encoding == "runtime":
        content = (json.dumps(value, indent=1) + "\n").encode()
    elif encoding == "compact":
        content = json.dumps(value, separators=(",", ":")).encode()
    else:
        content = path.read_bytes() + b"\n"
    path.write_bytes(content)
    with pytest.raises(ValueError, match="byte contract"):
        reconciliation.receipt(run, proposal)


@pytest.mark.parametrize("defect", ["schema", "phase", "count", "entry", "active", "outcome", "chronology"])
def test_complete_executor_state_is_required(encoding_case: tuple[Path, Path], defect: str) -> None:
    run, proposal = encoding_case
    path = run / "execution-state.json"
    state = json.loads(path.read_bytes())
    if defect == "schema":
        state["schema"] = "unknown"
    elif defect == "phase":
        state["phase"] = "stopped"
    elif defect == "count":
        state["completed"].pop()
    elif defect == "entry":
        state["completed"][0]["job"] += 1
    elif defect == "active":
        state["active_batch"] = BATCHES[0]
    elif defect == "outcome":
        state["analysis_outcome"] = "specified alternative supported"
    else:
        state["observed_utc"] = "2026-10-27T19:02:05+00:00"
    save(path, state)
    with pytest.raises(ValueError, match="executor"):
        reconciliation.receipt(run, proposal)


def test_writer_hash_mutation_refuses_even_after_approval_rebinding(encoding_case: tuple[Path, Path]) -> None:
    run, proposal = encoding_case
    campaign = json.loads((run / "sequence-plan.json").read_bytes())
    campaign["producer_inputs"]["scripts/qi_platform.py"] = "0" * 64
    rebind_plan(run, proposal, campaign)
    with pytest.raises(ValueError, match="source or writer bytes differ"):
        reconciliation.receipt(run, proposal)


def test_changed_writer_bytes_refuse_in_isolated_copy(
    encoding_case: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run, proposal = encoding_case
    campaign = json.loads((run / "sequence-plan.json").read_bytes())
    sources = reconciliation.validate_sources(campaign)
    isolated_root = tmp_path / "isolated-sources"
    for relative in sources:
        target = isolated_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    writer = isolated_root / "scripts/qi_platform.py"
    writer.write_bytes(writer.read_bytes() + b"\n")
    monkeypatch.setattr(reconciliation, "ROOT", isolated_root)
    with pytest.raises(ValueError, match="source or writer bytes differ"):
        reconciliation.receipt(run, proposal)


def test_rehashed_acquisition_semantic_mutation_refuses(encoding_case: tuple[Path, Path]) -> None:
    run, proposal = encoding_case
    directory = run / BATCHES[1]
    raw_path = next((directory / "raw").glob("*.json"))
    shots = ["0" * 20] * 4096
    save(raw_path, shots)
    result_path = directory / "results.json"
    collection = json.loads(result_path.read_bytes())
    collection["jobs"][0]["results"][0]["results"] = {"0" * 20: 4096}
    save(result_path, collection)
    completion_path = directory / "completion-admission.json"
    completion = json.loads(completion_path.read_bytes())
    completion["inputs"] = {name: digest(directory / name) for name in completion["inputs"]}
    save(completion_path, completion)
    report = analyze(run, proposal)
    if report["outcome"] != "specified alternative supported":
        raise AssertionError("coherent changed acquisition must exercise fresh semantic comparison")
    complete_state(run, report["outcome"])
    with pytest.raises(ValueError, match="byte contract"):
        reconciliation.receipt(run, proposal)


def test_invalid_fresh_analysis_is_never_reconciled(encoding_case: tuple[Path, Path]) -> None:
    run, proposal = encoding_case
    path = run / BATCHES[0] / "locked-admission.json"
    locked = json.loads(path.read_bytes())
    locked["admitted"] = False
    save(path, locked)
    report = analyze(run, proposal)
    (run / "analysis.json").write_bytes((json.dumps(report, indent=1) + "\n").encode())
    (run / "analysis-canonical.json").write_bytes(json_bytes(report))
    with pytest.raises(ValueError, match="fresh frozen analyzer refuses"):
        reconciliation.receipt(run, proposal)


def test_receipt_cli_is_exclusive_and_check_is_byte_exact(
    encoding_case: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run, proposal = encoding_case
    output = tmp_path / "encoding-receipt.json"
    arguments = ["receipt", str(run), "--proposal", str(proposal)]
    before = observations(run)
    monkeypatch.setattr(sys, "argv", [*arguments, "--out", str(output)])
    reconciliation.main()
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        reconciliation.main()
    if output.read_bytes() != original:
        raise AssertionError("exclusive receipt creation overwrote existing bytes")
    monkeypatch.setattr(sys, "argv", [*arguments, "--check", str(output)])
    reconciliation.main()
    output.write_bytes(original + b"\n")
    with pytest.raises(SystemExit, match="differs from exact replay"):
        reconciliation.main()
    if observations(run) != before:
        raise AssertionError("receipt output or verification changed retained acquisition artifacts")
