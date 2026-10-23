"""Read-only, content-addressed planning discovery across registered Git worktrees."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from check_markdown_links import is_excluded

HEADINGS = re.compile(
    r"^#{1,4} .*\b(plan|roadmap|next steps|open (items|work|questions)|implementation queue|program|ordered tasks)\b",
    re.I | re.M,
)


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *arguments], text=True).strip()


def candidate(path: str, content: str) -> bool:
    if path.startswith(("docs/local/plans/", "plans/")):
        return path.endswith((".md", ".json"))
    if not path.endswith(".md") or not path.startswith(("docs/", "gororoba_quantum/")):
        return False
    if is_excluded(path) or path.startswith(("docs/evidence/", "docs/state/", "docs/notes/papers/", "docs/sources/")):
        return False
    if path.startswith("docs/design/") or (path.startswith("docs/runbooks/") and "case" in Path(path).stem):
        return True
    return bool(re.search(r"\b(plan|roadmap)\b", Path(path).stem.replace("_", "-"), re.I) or HEADINGS.search(content))


def worktrees(root: Path) -> list[dict[str, str]]:
    result = []
    for block in git(root, "worktree", "list", "--porcelain", "-z").split("\0\0"):
        fields = dict(field.split(" ", 1) for field in block.split("\0") if " " in field)
        if "worktree" in fields:
            result.append(fields)
    return result


def scan(root: Path, all_worktrees: bool = False) -> dict[str, Any]:
    locations = worktrees(root) if all_worktrees else [{"worktree": str(root)}]
    snapshots = []
    variants: dict[str, dict[str, Any]] = {}
    for location in locations:
        checkout = Path(location["worktree"])
        if not checkout.is_dir():
            raise ValueError("registered worktree unavailable; inventory would be incomplete")
        before = git(checkout, "rev-parse", "HEAD")
        branch = git(checkout, "rev-parse", "--abbrev-ref", "HEAD")
        identity = hashlib.sha256(str(checkout.resolve()).encode()).hexdigest()[:16]
        dirty = git(checkout, "status", "--porcelain", "--untracked-files=all")
        index_digest = hashlib.sha256(git(checkout, "ls-files", "--stage", "-z").encode()).hexdigest()
        names = set(git(checkout, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0"))
        local = checkout / "docs/local/plans"
        if local.exists():
            names.update(
                str(path.relative_to(checkout))
                for path in local.rglob("*")
                if path.is_file() and path.suffix in {".md", ".json"}
            )
        observed: dict[str, str] = {}
        for name in sorted(names):
            if not name.endswith((".md", ".json")):
                continue
            path = checkout / name
            if not path.is_file() or path.is_symlink():
                continue
            if not name.startswith(("docs/", "plans/", "gororoba_quantum/")):
                continue
            if is_excluded(name) or name.startswith(
                ("docs/evidence/", "docs/state/", "docs/notes/papers/", "docs/sources/")
            ):
                continue
            content = path.read_text(encoding="utf-8")
            if not candidate(name, content):
                continue
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            observed[name] = sha
            key = f"{name}@{sha}"
            if key not in variants:
                variants[key] = {"path": name, "sha256": sha, "bytes": path.stat().st_size, "worktrees": []}
            variants[key]["worktrees"].append(identity)
        for name, sha in observed.items():
            if hashlib.sha256((checkout / name).read_bytes()).hexdigest() != sha:
                raise ValueError(f"planning source changed during scan: {name}; retry snapshot")
        if before != git(checkout, "rev-parse", "HEAD") or dirty != git(
            checkout, "status", "--porcelain", "--untracked-files=all"
        ):
            raise ValueError(f"worktree changed during scan: {branch}; retry snapshot")
        if index_digest != hashlib.sha256(git(checkout, "ls-files", "--stage", "-z").encode()).hexdigest():
            raise ValueError(f"worktree index changed during scan: {branch}; retry snapshot")
        snapshots.append(
            {
                "id": identity,
                "revision": before,
                "branch": branch,
                "dirty": bool(dirty),
                "index_sha256": index_digest,
                "candidates": len(observed),
            }
        )
    if all_worktrees and worktrees(root) != locations:
        raise ValueError("worktree registry changed during scan; retry snapshot")
    return {"schema": "plan-inventory-v1", "worktrees": snapshots, "sources": list(variants.values())}


def check_retained_inventory(root: Path, plans: dict[str, Any], *, initial: bool = False) -> None:
    """Check the frozen migration denominator independently of live worktree availability."""
    from plan_records import HEX, loads, local_path, require

    manifest = root / "docs/evidence/plan-reconciliation" / ("initial-inventory.json" if initial else "inventory.json")
    if not manifest.exists():
        require(not (root / "plans/quantum_dispatch.json").exists(), "required migration manifest missing")
        return
    inventory = loads(manifest.read_text())
    require(inventory["schema"] == "plan-inventory-v1", "invalid inventory schema")
    frozen = loads((manifest.parent / ("initial-scan.json" if initial else "scan.json")).read_text())

    def source_set(rows: list[dict[str, Any]]) -> set[tuple[str, str, tuple[str, ...]]]:
        return {(row["path"], row["sha256"], tuple(sorted(row["worktrees"]))) for row in rows}

    require(source_set(inventory["sources"]) == source_set(frozen["sources"]), "migration source denominator differs")
    require(inventory["worktrees"] == frozen["worktrees"], "migration worktree denominator differs")
    identities = {row["id"] for row in inventory["worktrees"]}
    require(len(identities) == len(inventory["worktrees"]), "duplicate worktree snapshot ID")
    seen: set[tuple[str, str]] = set()
    for source in inventory["sources"]:
        key = (source["path"], source["sha256"])
        require(key not in seen, "duplicate inventory source")
        seen.add(key)
        require(bool(HEX.fullmatch(source["sha256"])), "invalid original source digest")
        require(bool(source["worktrees"]) and set(source["worktrees"]) <= identities, "source worktree missing")
        require(source["disposition"] in {"plan", "supporting", "template", "reference"}, "unclassified source")
        require(set(source["plans"]) <= set(plans), "inventory target plan missing")
        if source["disposition"] in {"plan", "supporting"}:
            require(bool(source["plans"]), "planning source lacks target")
        else:
            require(bool(source.get("note")), "exclusion needs reason")
        retained = local_path(root, source["retained"])
        require(
            hashlib.sha256(retained.read_bytes()).hexdigest() == source["retained_sha256"], "retained source changed"
        )
    original = loads((root / "plans/quantum_dispatch.json").read_text())
    expected = {task["task_id"] for task in original["tasks"]}
    mappings = inventory["legacy_tasks"]
    require(
        len(mappings) == len(expected) and {row["id"] for row in mappings} == expected, "legacy task coverage differs"
    )
    for row in mappings:
        require(row["successor"] in plans and bool(row["finding"]), "legacy obligation lacks disposition")

    predecessor_files = (manifest.parent / "initial-inventory.json", manifest.parent / "initial-scan.json")
    if not initial and any(path.exists() for path in predecessor_files):
        require(all(path.is_file() for path in predecessor_files), "initial inventory pair incomplete")
        require(inventory.get("predecessor_inventory") == "initial-inventory.json", "required predecessor missing")
    if "predecessor_inventory" in inventory:
        require(
            not initial and inventory["predecessor_inventory"] == "initial-inventory.json",
            "invalid inventory predecessor",
        )
        require((manifest.parent / "initial-inventory.json").is_file(), "initial inventory missing")
        check_retained_inventory(root, plans, initial=True)
