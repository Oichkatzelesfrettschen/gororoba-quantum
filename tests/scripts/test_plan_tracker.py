"""Planning mutations preserve scope, dependency and execution-authority boundaries."""

from __future__ import annotations

import copy
import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import plan_inventory
import plan_records as records
import plan_tracker as tracker
import pytest


@pytest.fixture
def root(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "context.md").write_text("# Question\n\nA bounded source.\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "context.md"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "test: retain context",
        ],
        check=True,
    )
    return tmp_path


def plan(name: str = "bounded-investigation") -> dict[str, Any]:
    return {
        "schema": records.SCHEMA,
        "id": name,
        "kind": "investigation",
        "summary": "Test a bounded conjecture.",
        "sources": ["context.md"],
        "state": "planned",
        "scope": "Finite counterexample search.",
        "owner": "investigator",
        "next_action": "Enumerate the specified domain.",
        "reconciliation": {"status": "verified", "note": "The context file supplies the question."},
        "steps": [
            {
                "id": "find-counterexample",
                "action": "Enumerate the finite domain.",
                "acceptance": "Retain the checked domain and any counterexample.",
                "state": "todo",
            }
        ],
    }


def receipt(root: Path, item: dict[str, Any], step: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "scope_sha256": records.obligation(item, step),
        "result": "A counterexample refutes the hypothesis.",
        "observed_at": "2026-10-23T12:00:00Z",
        "revision": plan_inventory.git(root, "rev-parse", "HEAD"),
        "evidence": [{"ref": "context.md", "sha256": hashlib.sha256((root / "context.md").read_bytes()).hexdigest()}],
    }


def invoke(root: Path, *arguments: str) -> int:
    return tracker.run(tracker.parser().parse_args(["--root", str(root), *arguments]))


def test_capture_render_query_and_pause(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    invoke(root, "capture", "bounded-investigation", "--summary", "Test the conjecture.", "--source", "context.md")
    draft = records.load(root)["bounded-investigation"]
    if draft["state"] != "inbox":
        raise RuntimeError("capture must not commit work")
    patch = root / "patch.json"
    proposed = plan()
    patch.write_text(records.encoded({key: value for key, value in proposed.items() if key not in {"id", "schema"}}))
    invoke(root, "update", proposed["id"], "--input", str(patch))
    invoke(
        root,
        "pause",
        proposed["id"],
        "--last-result",
        "Found a candidate.",
        "--next-action",
        "Check its sign.",
        "--resume-when",
        "The sign convention is resolved.",
    )
    invoke(root, "render", "--write")
    invoke(root, "check")
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts}
    invoke(root, "list", "--blocked", "--json")
    invoke(root, "show", proposed["id"])
    invoke(root, "search", "sign")
    after = {path: path.read_bytes() for path in before}
    if before != after:
        raise RuntimeError("read commands mutated planning files")
    if "Check its sign" not in capsys.readouterr().out:
        raise RuntimeError("resume action is absent")
    invoke(root, "resume", proposed["id"])
    if records.load(root)[proposed["id"]]["state"] != "active":
        raise RuntimeError("resume must reactivate committed work")


def test_completed_falsification_and_historical_revalidation(root: Path) -> None:
    item = plan()
    step = item["steps"][0]
    step.update(state="done", receipts=[receipt(root, item, step)])
    item.update(
        state="closed", disposition="completed", resolution="Finite claim refuted.", receipts=[receipt(root, item)]
    )
    records.validate(root, {item["id"]: item})
    (root / "context.md").write_text("# Expanded context\n")
    records.validate(root, {item["id"]: item})
    if not records.receipt_freshness(root, item):
        raise RuntimeError("changed receipt inputs must request revalidation")
    stale = copy.deepcopy(item)
    newer = receipt(root, item, step) | {"observed_at": "2026-10-24T12:00:00Z"}
    step["receipts"].append(newer)
    if records.receipt_freshness(root, item) != [f"{item['id']}: revalidation required for context.md"]:
        raise RuntimeError("a step revalidation leaves the plan receipt stale")
    step["receipts"].insert(0, step["receipts"].pop())
    if records.receipt_freshness(root, item) != [f"{item['id']}: revalidation required for context.md"]:
        raise RuntimeError("the newest receipt is chosen by observed_at, not list position")
    tracker.publish(root, {}, item)
    revalidation = root / "revalidation.json"
    revalidation.write_text(records.encoded(receipt(root, item) | {"observed_at": "2026-10-24T12:00:00Z"}))
    invoke(root, "update", item["id"], "--receipt", str(revalidation))
    revalidated = records.load(root)[item["id"]]
    if records.receipt_freshness(root, revalidated) or len(revalidated["receipts"]) != 2:
        raise RuntimeError("update --receipt appends a plan revalidation and keeps the superseded receipt")
    if records.receipt_freshness(root, stale) != sorted(
        f"{name}: revalidation required for context.md" for name in (item["id"], step["id"])
    ):
        raise RuntimeError("the superseded receipts alone still request revalidation")
    step["acceptance"] = "Prove the universal claim."
    with pytest.raises(ValueError, match="scope differs"):
        records.validate(root, {item["id"]: item})


@pytest.mark.parametrize(
    "defect",
    [
        "unknown",
        "missing-source",
        "duplicate-step",
        "missing-receipt",
        "cancelled-dependency",
        "cycle",
        "escape",
        "ignored",
    ],
)
def test_invalid_records(root: Path, defect: str) -> None:
    item = plan()
    step = item["steps"][0]
    if defect == "unknown":
        item["approved"] = True
    elif defect == "missing-source":
        item["sources"] = ["missing.md"]
    elif defect == "duplicate-step":
        item["steps"].append(copy.deepcopy(step))
    elif defect == "missing-receipt":
        step["state"] = "done"
    elif defect == "cancelled-dependency":
        step.update(state="cancelled", reason="Wrong question.")
        item["steps"].append(
            {
                "id": "analyze",
                "action": "Analyze.",
                "acceptance": "Result retained.",
                "state": "doing",
                "depends_on": [step["id"]],
            }
        )
    elif defect == "cycle":
        step["depends_on"] = [step["id"]]
    elif defect == "escape":
        item["sources"] = ["../context.md"]
    elif defect == "ignored":
        item["sources"] = ["docs/local/plans/context.md"]
    with pytest.raises(ValueError):
        records.validate(root, {item["id"]: item})


def test_related_cycles_and_cross_plan_dependencies(root: Path) -> None:
    first, second = plan("first-plan"), plan("second-plan")
    first["related"], second["related"] = [second["id"]], [first["id"]]
    records.validate(root, {first["id"]: first, second["id"]: second})
    second["depends_on"] = [first["id"]]
    second["steps"][0]["state"] = "doing"
    with pytest.raises(ValueError, match="prerequisite unfinished"):
        records.validate(root, {first["id"]: first, second["id"]: second})


def test_duplicate_json_keys() -> None:
    with pytest.raises(ValueError, match="duplicate JSON key"):
        records.loads('{"state": "planned", "state": "closed"}')


def test_invalid_mutation_leaves_record_bytes(root: Path) -> None:
    item = plan()
    tracker.publish(root, {}, item)
    path = root / records.DIRECTORY / f"{item['id']}.json"
    before = path.read_bytes()
    with pytest.raises(ValueError, match="receipt"):
        invoke(root, "step", item["id"], "find-counterexample", "--state", "done")
    if path.read_bytes() != before:
        raise RuntimeError("invalid update changed the record")


def test_render_determinism_staleness_and_limit(root: Path) -> None:
    plans = {}
    for number in range(14):
        item = plan(f"investigation-{number}")
        item["state"] = "active"
        plans[item["id"]] = item
        tracker.publish(root, plans, item)
    forward = tracker.rendered(root, plans)
    backward = tracker.rendered(root, dict(reversed(list(plans.items()))))
    if forward != backward or "Showing 12 of 14" not in forward[tracker.INDEX]:
        raise RuntimeError("views must be deterministic and bounded")
    invoke(root, "render", "--write")
    (root / tracker.INDEX).write_text("handwritten status\n")
    with pytest.raises(ValueError, match="stale generated"):
        invoke(root, "check")


def test_semantic_merge_reports_clean_text_scope_receipt_overlap() -> None:
    item = plan()
    base = {item["id"]: item}
    left, right = copy.deepcopy(base), copy.deepcopy(base)
    left[item["id"]]["steps"][0]["acceptance"] = "Expanded domain."
    right[item["id"]]["steps"][0]["state"] = "done"
    findings = tracker.merge_findings(base, left, right)
    if len(findings) != 1 or findings[0]["overlap"]:
        raise RuntimeError("disjoint textual fields still require semantic reconciliation")
    right = {**base, "independent-plan": plan("independent-plan")}
    if tracker.merge_findings(base, left, right):
        raise RuntimeError("independent plan edits should compose")


def test_scan_includes_ignored_local_and_embedded_queue(root: Path) -> None:
    local = root / "docs/local/plans/question.md"
    local.parent.mkdir(parents=True)
    local.write_text("# Local investigation\n")
    (root / ".gitignore").write_text("docs/local/\n")
    embedded = root / "docs/design/circuit.md"
    embedded.parent.mkdir(parents=True)
    embedded.write_text("# Circuit design\n")
    result = plan_inventory.scan(root, True)
    names = {source["path"] for source in result["sources"]}
    if names != {"docs/local/plans/question.md", "docs/design/circuit.md"}:
        raise RuntimeError(f"inventory omitted planning material: {names}")
    if str(root) in records.encoded(result):
        raise RuntimeError("public inventory leaked a machine-local path")


def test_provider_approval_is_not_a_plan_field(root: Path) -> None:
    item = plan()
    item.update(
        kind="experiment",
        state="paused",
        pause={
            "last_result": "Case drafted.",
            "next_action": "Obtain case-specific approval.",
            "resume_when": "Human approves the frozen case.",
        },
    )
    records.validate(root, {item["id"]: item})
    item["execution_authorized"] = True
    with pytest.raises(ValueError, match="unknown plan fields"):
        records.validate(root, {item["id"]: item})


def test_receipt_binds_parent_and_closure_members(root: Path) -> None:
    item = plan()
    step = item["steps"][0]
    step.update(state="done", receipts=[receipt(root, item, step)])
    item.update(state="closed", disposition="completed", resolution="Bounded result retained.")
    item["receipts"] = [receipt(root, item)]
    modified = copy.deepcopy(item)
    modified["scope"] = "Expanded scientific domain."
    with pytest.raises(ValueError, match="scope differs"):
        records.validate(root, {modified["id"]: modified})
    another = copy.deepcopy(step)
    another["id"] = "second-obligation"
    another["receipts"] = [receipt(root, item, another)]
    item["steps"].append(another)
    with pytest.raises(ValueError, match="scope differs"):
        records.validate(root, {item["id"]: item})


def test_runnable_frontier_and_closed_unfinished_steps(root: Path) -> None:
    item = plan()
    item["steps"][0]["depends_on"] = ["later-prerequisite"]
    item["steps"].append(
        {
            "id": "later-prerequisite",
            "action": "Check convention.",
            "acceptance": "Source identity retained.",
            "state": "todo",
        }
    )
    records.validate(root, {item["id"]: item})
    if records.blockers({item["id"]: item}, item):
        raise RuntimeError("a runnable prerequisite must remain discoverable")
    item.update(state="closed", disposition="cancelled", resolution="Scope abandoned.")
    with pytest.raises(ValueError, match="unfinished steps"):
        records.validate(root, {item["id"]: item})


def test_inbox_optional_fields_are_typed(root: Path) -> None:
    item = plan()
    item.update(state="inbox", next_action=None)
    with pytest.raises(ValueError, match="next_action"):
        records.validate(root, {item["id"]: item})


def test_ignored_json_inventory(root: Path) -> None:
    path = root / "docs/local/plans/case.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}\n")
    (root / ".gitignore").write_text("docs/local/\n")
    inventory = plan_inventory.scan(root)
    if "docs/local/plans/case.json" not in {row["path"] for row in inventory["sources"]}:
        raise RuntimeError("ignored JSON plan was lost")


def test_same_checkout_cli_updates_serialize(root: Path) -> None:
    item = plan()
    tracker.publish(root, {}, item)
    updates = [("--summary", "Revised question."), ("--owner", "second-investigator")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda update: invoke(root, "update", item["id"], *update), updates))
    result = records.load(root)[item["id"]]
    if result["summary"] != "Revised question." or result["owner"] != "second-investigator":
        raise RuntimeError("concurrent CLI update was lost")


def test_closed_display_uses_resolution(root: Path) -> None:
    item = plan()
    item.update(state="closed", disposition="cancelled", resolution="A counterexample ended the question.", steps=[])
    display = tracker.entry(root, {item["id"]: item}, item)
    if "Next:" in display or "Resolution: A counterexample" not in display:
        raise RuntimeError("a closed plan must display its resolution")


def test_inventory_denominator_and_manifest_are_required(root: Path) -> None:
    item = plan()
    directory = root / "docs/evidence/plan-reconciliation"
    directory.mkdir(parents=True)
    legacy = root / "plans/quantum_dispatch.json"
    legacy.parent.mkdir()
    legacy.write_text('{"tasks": []}')
    sha = hashlib.sha256((root / "context.md").read_bytes()).hexdigest()
    source = {"path": "context.md", "sha256": sha, "worktrees": ["one"]}
    frozen: dict[str, Any] = {
        "schema": "plan-inventory-v1",
        "worktrees": [{"id": "one", "candidates": 1}],
        "sources": [source],
    }
    (directory / "scan.json").write_text(records.encoded(frozen))
    mapped = copy.deepcopy(frozen)
    mapped["sources"][0].update(disposition="plan", plans=[item["id"]], retained="context.md", retained_sha256=sha)
    mapped["legacy_tasks"] = []
    manifest = directory / "inventory.json"
    manifest.write_text(records.encoded(mapped))
    plan_inventory.check_retained_inventory(root, {item["id"]: item})
    (directory / "initial-inventory.json").write_text(records.encoded(mapped))
    with pytest.raises(ValueError, match="pair incomplete"):
        plan_inventory.check_retained_inventory(root, {item["id"]: item})
    (directory / "initial-scan.json").write_text(records.encoded(frozen))
    with pytest.raises(ValueError, match="predecessor missing"):
        plan_inventory.check_retained_inventory(root, {item["id"]: item})
    mapped["predecessor_inventory"] = "initial-inventory.json"
    manifest.write_text(records.encoded(mapped))
    plan_inventory.check_retained_inventory(root, {item["id"]: item})
    mapped["sources"] = []
    manifest.write_text(records.encoded(mapped))
    with pytest.raises(ValueError, match="source denominator differs"):
        plan_inventory.check_retained_inventory(root, {item["id"]: item})
    manifest.unlink()
    with pytest.raises(ValueError, match="manifest missing"):
        plan_inventory.check_retained_inventory(root, {item["id"]: item})


def test_detached_worktree_snapshot_ids_are_distinct(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "checkout", "--detach", "-q"], check=True)
    second = root / "second-checkout"
    subprocess.run(["git", "-C", str(root), "worktree", "add", "--detach", "-q", str(second), "HEAD"], check=True)
    inventory = plan_inventory.scan(root, True)
    if len({row["id"] for row in inventory["worktrees"]}) != 2:
        raise RuntimeError("detached worktrees at identical HEAD need distinct identities")
