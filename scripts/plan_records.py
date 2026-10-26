"""Work obligations and receipts; scientific and execution authorities remain external."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
import parallel  # noqa: E402

SCHEMA = "work-plan-v1"
DIRECTORY = Path("docs/state/plans")
STATES = ("inbox", "planned", "active", "paused", "closed")
KINDS = ("investigation", "implementation", "experiment", "coordination")
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
PLAN_KEYS = {
    "schema",
    "id",
    "kind",
    "summary",
    "sources",
    "state",
    "reconciliation",
    "scope",
    "owner",
    "next_action",
    "steps",
    "depends_on",
    "related",
    "claims",
    "acquisitions",
    "pause",
    "disposition",
    "resolution",
    "superseded_by",
    "receipts",
}
STEP_KEYS = {"id", "action", "acceptance", "state", "depends_on", "receipts", "reason"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def loads(text: str) -> Any:
    return json.loads(text, object_pairs_hook=unique_object)


def encoded(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def text(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: nonempty text required")
    require(not any(ord(character) < 32 for character in value), f"{label}: single-line text required")


def strings(value: Any, label: str) -> None:
    require(isinstance(value, list), f"{label}: list required")
    for member in value:
        text(member, label)
    require(len(value) == len(set(value)), f"{label}: duplicate entries")


def local_path(root: Path, reference: str) -> Path:
    path = PurePosixPath(reference.split("#", 1)[0])
    require(bool(path.parts) and not path.is_absolute() and ".." not in path.parts, "repository-relative path required")
    require(not str(path).startswith("docs/local/"), "ignored local planning sources need a retained successor")
    target = root / path
    require(target.resolve().is_relative_to(root.resolve()), "reference escapes repository")
    return target


def reference(root: Path, value: str) -> None:
    text(value, "reference")
    if value.startswith("https://"):
        parsed = urlsplit(value)
        require(
            bool(parsed.hostname) and parsed.username is None and parsed.password is None, "invalid HTTPS reference"
        )
    else:
        require(local_path(root, value).is_file(), f"missing reference: {value}")


def observed(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def timestamp(value: Any) -> None:
    text(value, "observed_at")
    require(observed(value).utcoffset() is not None, "timestamp needs timezone")


def obligation(plan: dict[str, Any], step: dict[str, Any] | None = None) -> str:
    parent = {key: plan.get(key, []) for key in ("id", "scope", "depends_on")}
    if step is not None:
        return digest(
            {"plan": parent, "step": {key: step.get(key, []) for key in ("id", "action", "acceptance", "depends_on")}}
        )
    return digest({"plan": parent, "steps": [obligation(plan, item) for item in plan.get("steps", [])]})


def check_receipts(root: Path, receipts: Any, scope: str) -> None:
    require(isinstance(receipts, list), "receipts: list required")
    for receipt in receipts:
        require(isinstance(receipt, dict), "receipt: object required")
        require(
            set(receipt) == {"scope_sha256", "result", "observed_at", "evidence", "revision"}, "receipt fields differ"
        )
        require(receipt["scope_sha256"] == scope, "completion receipt scope differs; reassess obligation")
        text(receipt["result"], "receipt result")
        timestamp(receipt["observed_at"])
        require(bool(re.fullmatch(r"[0-9a-f]{40}", receipt["revision"])), "receipt revision needs full Git object ID")
        require(isinstance(receipt["evidence"], list) and bool(receipt["evidence"]), "receipt needs evidence")
        for evidence in receipt["evidence"]:
            require(isinstance(evidence, dict) and set(evidence) == {"ref", "sha256"}, "evidence needs ref and sha256")
            reference(root, evidence["ref"])
            require(bool(HEX.fullmatch(evidence["sha256"])), "evidence digest needs SHA-256")


def evidence_digest(root: Path, reference: str) -> str:
    """The SHA-256 of the checkout bytes a local evidence reference names."""
    return hashlib.sha256(local_path(root, reference).read_bytes()).hexdigest()


def newest_receipt(item: dict[str, Any]) -> dict[str, Any] | None:
    """The receipt with the latest observed_at, the later listed on a tie; None for an item without one."""
    receipts = item.get("receipts", [])
    if not receipts:
        return None
    return max(enumerate(receipts), key=lambda pair: (observed(pair[1]["observed_at"]), pair[0]))[1]


def receipt_freshness(root: Path, plan: dict[str, Any]) -> list[str]:
    """Name each local input whose bytes differ from the digest in the newest receipt of the plan or a step.

    The newest receipt has the latest observed_at, the later listed on a tie. Older receipts stay as history, so
    a revalidation appends a receipt binding the current bytes and leaves the one it supersedes in place.
    """
    stale = []
    for item in [plan, *plan.get("steps", [])]:
        newest = newest_receipt(item)
        if newest is None:
            continue
        for evidence in newest["evidence"]:
            if evidence["ref"].startswith("https://"):
                continue
            if evidence_digest(root, evidence["ref"]) != evidence["sha256"]:
                stale.append(f"{item['id']}: revalidation required for {evidence['ref']}")
    return sorted(set(stale))


def _validate_one(item: tuple[str, dict[str, Any]]) -> None:
    root_string, plan = item
    root = Path(root_string)
    require(isinstance(plan, dict), "plan: object required")
    require(set(plan) <= PLAN_KEYS, f"unknown plan fields: {sorted(set(plan) - PLAN_KEYS)}")
    require(plan.get("schema") == SCHEMA, "unsupported work-plan schema")
    require(isinstance(plan.get("id"), str) and bool(IDENTIFIER.fullmatch(plan["id"])), "invalid plan ID")
    text(plan.get("summary"), "summary")
    for optional in ("scope", "owner", "next_action", "disposition", "resolution"):
        if optional in plan:
            text(plan[optional], optional)
    require(len(plan["summary"]) <= 300, "summary exceeds 300 characters")
    require(plan.get("kind") in KINDS, "invalid plan kind")
    require(plan.get("state") in STATES, "invalid plan lifecycle")
    strings(plan.get("sources"), "sources")
    require(bool(plan["sources"]), "plan needs source context")
    for source in plan["sources"]:
        reference(root, source)
    reconciliation: Any = plan.get("reconciliation")
    require(isinstance(reconciliation, dict), "reconciliation required")
    require(set(reconciliation) == {"status", "note"}, "reconciliation needs status and note")
    require(reconciliation["status"] in {"verified", "historical", "unresolved"}, "invalid reconciliation status")
    text(reconciliation["note"], "reconciliation note")
    for key in ("depends_on", "related", "claims", "acquisitions"):
        strings(plan.get(key, []), key)
    if plan["state"] in {"planned", "active", "paused"}:
        for key in ("scope", "owner", "next_action"):
            text(plan.get(key), key)
        require(bool(plan.get("steps")), "committed plan needs steps")
    if plan["state"] == "paused":
        pause: Any = plan.get("pause")
        require(
            isinstance(pause, dict) and set(pause) == {"last_result", "next_action", "resume_when"},
            "pause capsule required",
        )
        for value in pause.values():
            text(value, "pause field")
    if plan["state"] == "closed":
        require(plan.get("disposition") in {"completed", "cancelled", "superseded"}, "closed disposition required")
        text(plan.get("resolution"), "resolution")
        if plan["disposition"] == "superseded":
            strings(plan.get("superseded_by"), "superseded_by")
            require(bool(plan["superseded_by"]), "superseded plan needs successor")
    steps = plan.get("steps", [])
    require(isinstance(steps, list), "steps: list required")
    require(all(isinstance(step, dict) for step in steps), "step: object required")
    for step in steps:
        require(set(step) <= STEP_KEYS, "unknown step fields")
        require(isinstance(step.get("id"), str) and bool(IDENTIFIER.fullmatch(step["id"])), "invalid step ID")
        for key in ("action", "acceptance"):
            text(step.get(key), key)
        require(step.get("state") in {"todo", "doing", "done", "cancelled"}, "invalid step state")
        strings(step.get("depends_on", []), "step dependencies")
        if step["state"] == "cancelled":
            text(step.get("reason"), "cancellation reason")
        if step["state"] == "done":
            require(bool(step.get("receipts")), "completed step needs receipt")
        check_receipts(root, step.get("receipts", []), obligation(plan, step))
    require(len({step["id"] for step in steps}) == len(steps), "duplicate step ID")
    if plan["state"] == "closed":
        require(all(step["state"] in {"done", "cancelled"} for step in steps), "closed plan has unfinished steps")
    require(sum(step["state"] == "doing" for step in steps) <= 1, "one active step per plan")
    if plan.get("disposition") == "completed" and plan["state"] == "closed":
        require(bool(steps) and all(step["state"] == "done" for step in steps), "completed plan needs all steps done")
        require(bool(plan.get("receipts")), "completed plan needs closure receipt")
    check_receipts(root, plan.get("receipts", []), obligation(plan))


def node_key(plan_id: str, value: str) -> str:
    return value if "/" in value else f"{plan_id}/{value}"


def graph(plans: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    edges: dict[str, list[str]] = {}
    for name, plan in plans.items():
        edges[name] = list(plan.get("depends_on", []))
        for step in plan.get("steps", []):
            edges[f"{name}/{step['id']}"] = [*edges[name], *(node_key(name, ref) for ref in step.get("depends_on", []))]
        edges[name] += [f"{name}/{step['id']}" for step in plan.get("steps", [])]
    return edges


def is_done(plans: dict[str, dict[str, Any]], node: str) -> bool:
    name, separator, step_id = node.partition("/")
    plan = plans[name]
    if separator:
        return next(step for step in plan["steps"] if step["id"] == step_id)["state"] == "done"
    return plan["state"] == "closed" and plan.get("disposition") == "completed"


def validate(root: Path, plans: dict[str, dict[str, Any]]) -> None:
    parallel.ordered_map(_validate_one, [(str(root), plan) for plan in plans.values()])
    edges = graph(plans)
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(node: str) -> None:
        require(node in edges, f"missing dependency: {node}")
        require(node not in visiting, f"blocking dependency cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in edges[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        visit(node)
    registry_path = root / "docs/state/research_state.json"
    registry = loads(registry_path.read_text()) if registry_path.exists() else {"claims": [], "acquisitions": []}
    for name, plan in plans.items():
        require(name == plan["id"], "plan filename and ID differ")
        for key in ("related", "superseded_by"):
            require(all(ref in plans and ref != name for ref in plan.get(key, [])), f"{name}: missing or self {key}")
        for key in ("claims", "acquisitions"):
            known = {entry["id"] for entry in registry[key]}
            require(set(plan.get(key, [])) <= known, f"{name}: unknown {key} reference")
        for step in plan.get("steps", []):
            if step["state"] in {"doing", "done"}:
                dependencies = edges[f"{name}/{step['id']}"]
                require(
                    all(is_done(plans, ref) for ref in dependencies), f"{name}/{step['id']}: prerequisite unfinished"
                )


def load(root: Path) -> dict[str, dict[str, Any]]:
    return {path.stem: loads(path.read_text(encoding="utf-8")) for path in sorted((root / DIRECTORY).glob("*.json"))}


def blockers(plans: dict[str, dict[str, Any]], plan: dict[str, Any]) -> list[str]:
    blocked = [ref for ref in plan.get("depends_on", []) if not is_done(plans, ref)]
    unfinished = [step for step in plan.get("steps", []) if step["state"] in {"todo", "doing"}]
    missing = [
        [
            node_key(plan["id"], ref)
            for ref in step.get("depends_on", [])
            if not is_done(plans, node_key(plan["id"], ref))
        ]
        for step in unfinished
    ]
    if missing and all(missing):
        blocked += sorted({ref for dependencies in missing for ref in dependencies})
    if plan["state"] == "paused":
        blocked.append(plan["pause"]["resume_when"])
    if plan["reconciliation"]["status"] == "unresolved":
        blocked.append("reconciliation evidence unresolved")
    return blocked
