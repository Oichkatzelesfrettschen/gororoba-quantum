"""Bounded receipt and manifest contracts for the memory acceptance and selected-array model."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = "docs/evidence/a5-exceptional-fibers/memory-bounded"
LAUNCH_MANIFEST = f"{DIRECTORY}/w8-n16-launch-inputs.json"
DEPENDENCIES = {
    "runner": "docs/evidence/a5-exceptional-fibers/replay/engine/rank_cell.py",
    "compact": "gororoba_quantum/modular_echelon_compact.py",
    "parallel": "gororoba_quantum/parallel.py",
}
SPEC = importlib.util.spec_from_file_location(
    "a5_memory_acceptance_receipt_test", ROOT / DIRECTORY / "acceptance_summary.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the acceptance summary")
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)


def check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record) + "\n")


def bind_launch_manifest(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    resource_path = root / summary.RECORD_DIRECTORY / f"{summary.RECORD_STEM}.resources.json"
    manifest = {
        "schema": "a5-fiber-rank-v14-launch-inputs-v1",
        "launch_head": "0" * 40,
        "source_case_sha256": "0" * 64,
        "input_sha256": {
            name: summary.sha256(root / name)
            for name in [summary.ENGINE, *DEPENDENCIES.values(), "inputs/header.sing", "inputs/receipt.json"]
        },
        "resource_record": {
            "path": str(resource_path.relative_to(root)),
            "sha256": summary.sha256(resource_path),
        },
    }
    write_json(root / LAUNCH_MANIFEST, manifest)
    monkeypatch.setattr(summary, "LAUNCH_INPUTS_SHA256", summary.sha256(root / LAUNCH_MANIFEST), raising=False)


@pytest.fixture
def receipt_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    engine = tmp_path / summary.ENGINE
    engine.parent.mkdir(parents=True)
    engine.write_text("bounded engine fixture\n")
    for label, filename in DEPENDENCIES.items():
        dependency = tmp_path / filename
        dependency.parent.mkdir(parents=True, exist_ok=True)
        dependency.write_text(f"bounded {label} fixture\n")
    header = "inputs/header.sing"
    receipt = "inputs/receipt.json"
    (tmp_path / header).parent.mkdir()
    (tmp_path / header).write_text("bounded header fixture\n")
    (tmp_path / receipt).write_text("{}\n")
    engine_digest = summary.sha256(engine)
    header_digest = summary.sha256(tmp_path / header)
    record = {
        "engine_sha256_16": engine_digest[:16],
        "header_sha256_16": header_digest[:16],
        "d": 5,
        "N": 16,
        "prime": 32009,
        "mode": "quotient",
        "stream_products": True,
        "product_operator": "uint16-cached",
        "echelon": "compact",
        "closure_tables": "sparse",
        "closure_rounds": 1,
        "dim_quotient": 4,
        "products": 2,
        "r_N": 2,
        "per_block": {"0": {"r_N": 2, "rank_W": 2, "cols": 4}},
        "checks": {"count": 1, "rank_growth": {}},
        "preflight_stages": {"products": 128, "closure": 64},
        "seconds": {"singular": 1.0, "products": 2.0, "closure": 3.0, "total": 6.0},
        "representatives": {"built_rows": {"5": 2}, "receipt_sha256": summary.sha256(tmp_path / receipt)},
    }
    directory = tmp_path / summary.RECORD_DIRECTORY
    output = directory / f"{summary.RECORD_STEM}.json"
    write_json(output, record)
    stderr = directory / f"{summary.RECORD_STEM}.err"
    stderr.write_text("products built in 2.0 s: 2 retained rows\nechelon insert seconds in the closure: 1.0\n")
    resources = {
        "command": [
            "python",
            summary.ENGINE,
            header,
            "5",
            "16",
            "--operator-cache-gb",
            "6",
            "--chunk",
            "64",
            "--max-gb",
            "12",
            "--dense-tables-gb",
            "0",
            "--k2-receipt",
            receipt,
        ],
        "runner_exit": 0,
        "engine_exit": 0,
        "termination": "exited",
        "validation_error": None,
        "engine_sha256": engine_digest,
        "header_sha256": header_digest,
        "stdout_part_sha256": summary.sha256(output),
        "stderr_sha256": summary.sha256(stderr),
        "max_sampled_process_group_rss_bytes": 1024,
        "max_sampled_processes": 1,
        "rss_poll_seconds": 0.1,
        "rss_unavailable_samples": 0,
        "elapsed_seconds": 6.0,
        "timeout_seconds": 60,
        "engine_args_sha256_16": "a" * 16,
    }
    write_json(directory / f"{summary.RECORD_STEM}.resources.json", resources)
    comparator = tmp_path / summary.COMPARATOR_DIRECTORY
    write_json(comparator / f"{summary.COMPARATOR_STEM}.out", record)
    (comparator / f"{summary.COMPARATOR_STEM}.err").write_text("Maximum resident set size (kbytes): 2\n")
    bind_launch_manifest(tmp_path, monkeypatch)
    return tmp_path


def test_acceptance_summary_admits_a_complete_bounded_receipt(receipt_fixture: Path) -> None:
    record = summary.build_summary(receipt_fixture, True)
    check(record["result"]["r_N"] == 2)
    check(record["resources"]["rss_poll_seconds"] == 0.1)
    check(record["launch_inputs"]["path"] == LAUNCH_MANIFEST)
    check(record["launch_inputs"]["sha256"] == summary.sha256(receipt_fixture / LAUNCH_MANIFEST))
    check(len(record["launch_inputs"]["input_sha256"]) == 6)


@pytest.mark.parametrize("mutation", ["engine", "header", "receipt", "stdout", "stderr", *DEPENDENCIES])
def test_acceptance_summary_rejects_changed_bound_bytes(receipt_fixture: Path, mutation: str) -> None:
    paths = {
        "engine": summary.ENGINE,
        "header": "inputs/header.sing",
        "receipt": "inputs/receipt.json",
        "stdout": f"{summary.RECORD_DIRECTORY}/{summary.RECORD_STEM}.json",
        "stderr": f"{summary.RECORD_DIRECTORY}/{summary.RECORD_STEM}.err",
        **DEPENDENCIES,
    }
    path = receipt_fixture / paths[mutation]
    path.write_bytes(path.read_bytes() + b" \n")
    with pytest.raises(SystemExit):
        summary.build_summary(receipt_fixture, True)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "empty",
        "withheld_manifest",
        "withheld_inputs",
        "missing_dependency",
        "withheld_digest",
        "wrong_resource_binding",
        "tampered",
    ],
)
def test_acceptance_summary_rejects_missing_withheld_or_tampered_launch_manifest(
    receipt_fixture: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    path = receipt_fixture / LAUNCH_MANIFEST
    if mutation == "missing":
        path.unlink()
    elif mutation == "empty":
        path.write_text("")
    else:
        manifest = json.loads(path.read_text())
        if mutation == "withheld_manifest":
            manifest = None
        elif mutation == "withheld_inputs":
            manifest["input_sha256"] = None
        elif mutation == "missing_dependency":
            del manifest["input_sha256"][DEPENDENCIES["compact"]]
        elif mutation == "withheld_digest":
            manifest["input_sha256"][DEPENDENCIES["parallel"]] = None
        elif mutation == "wrong_resource_binding":
            manifest["resource_record"]["sha256"] = "0" * 64
        else:
            manifest["launch_head"] = "1" * 40
        path.write_text(json.dumps(manifest) + "\n")
        if mutation != "tampered":
            monkeypatch.setattr(summary, "LAUNCH_INPUTS_SHA256", summary.sha256(path), raising=False)
    with pytest.raises(SystemExit):
        summary.build_summary(receipt_fixture, True)


@pytest.mark.parametrize("dependency", DEPENDENCIES.values())
def test_skipping_the_engine_digest_keeps_imported_dependency_checks(receipt_fixture: Path, dependency: str) -> None:
    path = receipt_fixture / dependency
    path.write_bytes(path.read_bytes() + b" \n")
    with pytest.raises(SystemExit):
        summary.build_summary(receipt_fixture, False)


@pytest.mark.parametrize(
    "mutation", ["missing_output", "empty_resources", "empty_blocks", "withheld_rank", "withheld_checks", "empty_rss"]
)
def test_acceptance_summary_refuses_missing_empty_or_withheld_results(
    receipt_fixture: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    directory = receipt_fixture / summary.RECORD_DIRECTORY
    output = directory / f"{summary.RECORD_STEM}.json"
    resource_path = directory / f"{summary.RECORD_STEM}.resources.json"
    if mutation == "missing_output":
        output.rename(output.with_suffix(".withheld"))
    elif mutation == "empty_resources":
        resource_path.write_text("")
    else:
        resources = json.loads(resource_path.read_text())
        if mutation == "empty_rss":
            resources["max_sampled_process_group_rss_bytes"] = 0
        else:
            comparator = receipt_fixture / summary.COMPARATOR_DIRECTORY / f"{summary.COMPARATOR_STEM}.out"
            for path in (output, comparator):
                record = json.loads(path.read_text())
                if mutation == "empty_blocks":
                    record["per_block"] = {}
                elif mutation == "withheld_rank":
                    record["r_N"] = None
                else:
                    record["checks"]["count"] = None
                write_json(path, record)
            resources["stdout_part_sha256"] = summary.sha256(output)
        write_json(resource_path, resources)
        bind_launch_manifest(receipt_fixture, monkeypatch)
    with pytest.raises((SystemExit, OSError, ValueError)):
        summary.build_summary(receipt_fixture, True)


@pytest.mark.parametrize("mutation", ["valid", "stale_summary", "changed_header", *DEPENDENCIES, "missing_manifest"])
def test_acceptance_check_mode_admits_good_and_rejects_bad_without_writing(
    receipt_fixture: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    producer = receipt_fixture / DIRECTORY / "acceptance_summary.py"
    producer.parent.mkdir(parents=True, exist_ok=True)
    destination = producer.parent / summary.SUMMARY
    destination.write_text(summary.render(summary.build_summary(receipt_fixture, True)))
    if mutation == "stale_summary":
        destination.write_text("{}\n")
    elif mutation == "changed_header":
        (receipt_fixture / "inputs/header.sing").write_text("changed header\n")
    elif mutation in DEPENDENCIES:
        (receipt_fixture / DEPENDENCIES[mutation]).write_text("changed dependency\n")
    elif mutation == "missing_manifest":
        (receipt_fixture / LAUNCH_MANIFEST).unlink()
    before = destination.read_bytes(), destination.stat().st_mtime_ns
    monkeypatch.setattr(summary, "repository_root", lambda: receipt_fixture)
    monkeypatch.setattr(summary, "__file__", str(producer))
    monkeypatch.setattr(sys, "argv", [str(producer), "--check"])
    if mutation not in ("valid", "stale_summary"):
        with pytest.raises(SystemExit):
            summary.main()
    else:
        check(summary.main() == (1 if mutation == "stale_summary" else 0))
    check((destination.read_bytes(), destination.stat().st_mtime_ns) == before)


@pytest.mark.parametrize(
    ("name", "record"),
    [
        ("core-a5-w8-memory-acceptance-summary", "w8-n16-acceptance.json"),
        ("core-a5-w8-n19-memory-model", "w8-n19-memory-model.json"),
    ],
)
def test_memory_evidence_is_declared_by_read_only_on_demand_gates(name: str, record: str) -> None:
    gates = json.loads((ROOT / "ci/gates.json").read_text())["gates"]
    matches = [gate for gate in gates if gate["name"] == name]
    check(len(matches) == 1)
    gate = matches[0]
    check("--check" in gate["cmd"] and "--out" not in gate["cmd"])
    check(f"{DIRECTORY}/{record}" in gate["replays"])
