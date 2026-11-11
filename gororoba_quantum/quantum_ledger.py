"""Lossless evidence navigation for the research registry and retained artifact census.

The registry owns scientific statements. The ledger projects those statements,
their qualifications and the retained files into queryable relations. JSON
Pointers select observations without guessing an estimator from field names.
File ownership, digest agreement and numerical replay remain separate facts.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from parallel import ordered_map


def local_file(root: Path, reference: str) -> Path:
    """Resolve a repository-relative evidence file, refusing escapes and symlinks outside ROOT."""
    name = reference.partition("#")[0]
    path = Path(name)
    resolved = (root / path).resolve()
    if path.is_absolute() or ".." in path.parts or not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"evidence path leaves the repository: {reference}")
    if not resolved.is_file():
        raise ValueError(f"evidence file is missing: {reference}")
    return resolved


def pointer_value(document: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON Pointer, preserving null, zero and array order."""
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError("a JSON Pointer is empty or starts with /")
    value = document
    for encoded in pointer[1:].split("/"):
        if re.search(r"~(?![01])", encoded):
            raise ValueError(f"invalid JSON Pointer escape: {pointer}")
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and token in value:
            value = value[token]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", token) and int(token) < len(value):
            value = value[int(token)]
        else:
            raise ValueError(f"JSON Pointer selects no value: {pointer}")
    return value


def _describe_source(item: tuple[Path, str]) -> dict[str, Any]:
    root, reference = item
    path = local_file(root, reference)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    result: dict[str, Any] = {"path": reference, "file_sha256": digest, "bytes": path.stat().st_size}
    if path.suffix != ".json":
        result.update(schema=None, metadata_status="non-json")
        return result
    document = json.loads(path.read_text(encoding="utf-8"))
    result.update(schema=document.get("schema") if isinstance(document, dict) else None, metadata_status="decoded")
    # Metadata remains source-native: a version label names an environment,
    # whereas an estimator's statistical assumptions live in its own record.
    result["provenance"] = (
        {
            key: value
            for key, value in document.items()
            if key in {"versions", "source_sha256", "sources", "analysis_boundary", "provenance"}
            or key.endswith("_version")
        }
        if isinstance(document, dict)
        else {}
    )
    return result


def build(
    root: Path,
    claims: list[dict[str, Any]],
    acquisitions: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    gates: dict[str, str],
    tracked_paths: list[str],
) -> dict[str, Any]:
    """Join validated claims to tracked files without treating directory ownership as scientific support."""
    pinned: dict[str, list[dict[str, str]]] = {}
    documented: dict[str, list[str]] = {}
    cited_acquisitions: set[str] = set()
    claim_rows = []
    for claim in sorted(claims, key=lambda row: row["id"]):
        cited_acquisitions.update(claim["acquisitions"])
        for evidence in claim["evidence"]:
            path = evidence["path"].partition("#")[0]
            pinned.setdefault(path, []).append({"claim": claim["id"], **evidence})
        for path in claim["documents"]:
            documented.setdefault(path, []).append(claim["id"])
        claim_rows.append(
            {
                **copy.deepcopy(claim),
                "integrity": "registry-validated",
                "numerical_replay": "not-run-by-ledger",
                "replay_commands": [
                    {"gate": gate, "command": gates[gate]}
                    for gate, role in sorted(claim["gates"].items())
                    if role == "replay"
                ],
            }
        )
    tracked = set(tracked_paths)
    census = {path for path in tracked if path.startswith(("results/", "docs/evidence/", "proofs/"))}
    paths = sorted(census | set(pinned) | set(documented))
    runs_by_path = {run["path"]: run for run in runs}
    artifacts = []
    for path in paths:
        owners = []
        ancestor = Path(path).parent
        while ancestor != Path("."):
            if ancestor.as_posix() in runs_by_path:
                owners.append(ancestor.as_posix())
            ancestor = ancestor.parent
        artifacts.append(
            {
                "path": path,
                "tracked": path in tracked,
                "present": (root / path).is_file(),
                "raw_directory_member": "raw" in Path(path).parts,
                "runs": sorted(owners),
                "claim_bindings": pinned.get(path, []),
                "document_claims": sorted(documented.get(path, [])),
            }
        )
    sources = ordered_map(_describe_source, [(root, path) for path in sorted(pinned)])
    for source in sources:
        for binding in pinned[source["path"]]:
            if "#" not in binding["path"] and binding["sha256"] != source["file_sha256"]:
                raise ValueError(f"evidence changed after registry validation: {binding['path']}")
    classes = Counter(claim["evidence_class"] for claim in claims)
    gaps = {
        "unclaimed_acquisitions": sorted(a["id"] for a in acquisitions if a["id"] not in cited_acquisitions),
        "claims_without_replay_gate": sorted(c["id"] for c in claims if "replay" not in c["gates"].values()),
        "claims_without_pinned_evidence": sorted(c["id"] for c in claims if not c["evidence"]),
        "missing_tracked_artifacts": [row["path"] for row in artifacts if row["tracked"] and not row["present"]],
        "untracked_claim_artifacts": [
            row["path"] for row in artifacts if not row["tracked"] and (row["claim_bindings"] or row["document_claims"])
        ],
        "artifacts_without_claim_or_run_link": [
            row["path"]
            for row in artifacts
            if not row["runs"] and not row["claim_bindings"] and not row["document_claims"]
        ],
        "execution_records_outside_indexed_runs": [
            row["path"]
            for row in artifacts
            if not row["runs"]
            and row["path"].startswith("results/")
            and Path(row["path"]).name in {"submission.json", "record.json"}
        ],
    }
    return {
        "schema": "quantum-evidence-ledger-v1",
        "scope": {
            "claims": "every research_state.json claim, including withdrawn claims and proposed experiments",
            "runs": "the four provider adapters and retained Kaggle submission receipts",
            "artifacts": "git-tracked results/, docs/evidence/ and proofs/ files, plus claim evidence and documents",
            "boundary": "Unlinked artifacts require classification; a file is not an experiment or a trial.",
        },
        "summary": {
            "claims": len(claim_rows),
            "acquisitions": len(acquisitions),
            "runs": len(runs),
            "artifacts": len(artifacts),
            "evidence_classes": dict(sorted(classes.items())),
            "raw_directory_files": sum(row["raw_directory_member"] for row in artifacts),
            "pinned_source_files": len(sources),
            "source_schemas": dict(sorted(Counter(str(row["schema"]) for row in sources).items())),
            "gap_counts": {key: len(value) for key, value in gaps.items()},
        },
        "claims": claim_rows,
        "acquisitions": acquisitions,
        "runs": runs,
        "sources": sources,
        "artifacts": artifacts,
        "gaps": gaps,
    }


def markdown(ledger: dict[str, Any]) -> str:
    """Render scientific qualifications beside each claim, with links to its deciding evidence."""

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    summary = ledger["summary"]
    lines = [
        "# Quantum evidence ledger",
        "",
        f"{summary['claims']} claims; {summary['acquisitions']} acquisitions; {summary['artifacts']} artifacts.",
        "",
        "Registry validation checks retained bindings. Numerical replays are not run by the ledger.",
        "The JSON view holds every artifact, source metadata, acquisition and unresolved coverage link.",
        "",
        "| Claim | Class and recorded status | Statement | Boundary and assumptions | Evidence | Replay gates |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for claim in ledger["claims"]:
        fields = [
            claim["id"],
            f"{claim['evidence_class']}; {claim['status']}",
            claim["statement"],
            claim["boundary"] + " " + "; ".join(claim["assumptions"]),
            "; ".join(entry["path"] for entry in claim["evidence"]),
            "; ".join(entry["gate"] for entry in claim["replay_commands"]),
        ]
        lines.append("| " + " | ".join(cell(field) for field in fields) + " |")
    lines.extend(["", "## Coverage gaps", ""])
    lines.extend(f"- {name}: {count}" for name, count in summary["gap_counts"].items())
    return "\n".join(lines) + "\n"


def inspect(root: Path, reference: str, pointer: str) -> dict[str, Any]:
    """Read an exact JSON field; record-selector interpretation belongs to the registry caller."""
    if "#" in reference:
        raise ValueError("inspect takes a file path and a separate JSON Pointer")
    path = local_file(root, reference)
    content = path.read_bytes()
    document = json.loads(content)
    return {
        "source_file": reference,
        "file_sha256": hashlib.sha256(content).hexdigest(),
        "pointer": pointer,
        "value": pointer_value(document, pointer),
        "interpretation": "retained source value; estimator, denominator and inference follow the cited analysis",
        "numerical_replay": "not-run-by-ledger",
    }
