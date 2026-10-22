"""Retain sanitized task evidence and explicit dispositions without modifying source artifacts.

Source labels are logical names, never host paths. Captures preserve original
digests separately from sanitized bytes; a capture is not a bit-identical raw
receipt or an assertion that a running producer has finished.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "quantum-task-artifact-retention-v1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

LIMIT = 64 * 1024 * 1024
GENERATED = frozenset(
    {
        "validation",
        "uv-cache",
        "mypy-cache",
        "ruff-cache",
        "bibtex-build",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "pytest-temp",
    }
)
PRIVATE_KEYS = frozenset(
    {
        "token",
        "token_id",
        "token_label",
        "token_value",
        "creator_id",
        "user_id",
        "entity_id",
        "email",
        "account_id",
        "instance_id",
        "crn",
        "client_secret",
        "access_token",
        "refresh_token",
        "oidc_sub",
        "full_name",
        "password",
        "api_key",
        "apikey",
        "x-api-key",
    }
)
READING = re.compile(r"^(?:\d{4}\.\d{4,5}(?:v\d+)?|quant-ph-\d+(?:v\d+)?|rfc\d+)\.(?:html|txt)$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_text(text: str) -> str:
    text = re.sub(r"/home/[^/\s\"']+", "${USER_HOME}", text)
    text = text.replace("/tmp/", "${TEMP}/")
    text = re.sub(r"(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED-JWT]", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED-EMAIL]", text)
    text = re.sub(r"crn:v\d:[^\s\"<>]+", "[REDACTED-CRN]", text)
    text = re.sub(r"(?i)([?&](?:code|state|access_token|refresh_token)=)[^&\s\"<>]+", r"\1[REDACTED]", text)
    private_fields = "|".join(re.escape(key) for key in sorted(PRIVATE_KEYS, key=len, reverse=True))
    text = re.sub(
        rf"(?i)(?<![\w-])(?:{private_fields})"
        r"[\"']?\s*[:=]\s*(?:\"[^\"\r\n]*\"|'[^'\r\n]*'|[^,;\r\n]+)",
        "[REDACTED-CREDENTIAL-FIELD]",
        text,
    )
    return text


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {clean_text(key): _clean(item) for key, item in value.items() if key.lower() not in PRIVATE_KEYS}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    return clean_text(value) if isinstance(value, str) else value


def sanitize(data: bytes) -> bytes:
    text = data.decode("utf-8")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return clean_text(text).encode()
    return (json.dumps(_clean(parsed), indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def external_copy(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        name.startswith("external-")
        or path.suffix == ".pdf"
        or "local_source_cache" in path.parts
        or bool(READING.match(path.name))
    )


def _payload(arguments: tuple[str, bytes]) -> tuple[dict[str, Any], bytes | None]:
    name, data = arguments
    original_data = data
    row: dict[str, Any] = {"source": name, "source_bytes": len(data), "source_sha256": digest(data)}
    row["git_blob_oid"] = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if external_copy(name):
        return {
            **row,
            "classification": "external-reading-copy",
            "reason": "Reading-copy identity retained; redistribution and source-ledger admission remain separate.",
        }, None
    if PurePosixPath(name).suffix == ".lock":
        return {
            **row,
            "classification": "transient-noise",
            "reason": "Synchronization state is not a scientific observation.",
        }, None
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        content, extension = data, ".png"
        row["classification"] = "retained-figure"
    else:
        if "changed-files" in PurePosixPath(name).name:
            data = data.replace(b"\0", b"\n")
        try:
            content = sanitize(data)
        except UnicodeDecodeError as error:
            raise ValueError(f"unclassified binary requires an owner: {name}") from error
        if b"\0" in content:
            raise ValueError(f"unclassified binary requires an owner: {name}")
        extension = ".txt"
        row["classification"] = "retained-sanitized"
    row.update(
        retained=f"captures/{digest(content)}{extension}",
        retained_sha256=digest(content),
        retained_bytes=len(content),
        content_changed=content != original_data,
    )
    return row, content


def _generated_summary(path: Path, name: str) -> dict[str, Any]:
    files = sorted(item for item in path.rglob("*") if item.is_file() and not item.is_symlink())
    entries = [(item.relative_to(path).as_posix(), item.stat().st_size) for item in files]
    return {
        "source": name,
        "classification": "derived-regenerable",
        "file_count": len(entries),
        "source_bytes": sum(size for _, size in entries),
        "path_size_inventory_sha256": digest(json.dumps(entries).encode()),
        "reason": (
            "Package/build/lint environment; retain pins and invocation evidence, not installed binaries or caches. "
            "The inventory digest covers relative paths and sizes, not file content."
        ),
    }


def capture(sources: dict[str, Path], output: Path, tracked_root: Path | None = None) -> None:
    if output.exists():
        raise ValueError("choose a new capture destination rather than overwrite evidence")
    rows: list[dict[str, Any]] = []
    inputs: list[tuple[str, bytes]] = []
    tracked: dict[str, str] = {}
    commit = ""
    if tracked_root is not None:
        if tracked_root.resolve() != ROOT:
            raise ValueError("tracked evidence must belong to this repository")
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        listing = subprocess.check_output(["git", "ls-tree", "-rz", "HEAD"], cwd=ROOT).decode()
        for entry in listing.split("\0"):
            if entry:
                metadata, name = entry.split("\t", 1)
                mode, kind, oid = metadata.split()
                if kind == "blob" and mode != "120000":
                    tracked.setdefault(oid, name)

    def visit(path: Path, name: str) -> None:
        if path.is_symlink():
            rows.append({"source": name, "classification": "symbolic-link-not-followed"})
        elif path.is_dir():
            if path.name in GENERATED:
                rows.append(_generated_summary(path, name))
            else:
                for child in sorted(path.iterdir()):
                    visit(child, f"{name}/{child.name}")
        elif path.is_file():
            size = path.stat().st_size
            if size > LIMIT:
                raise ValueError(f"source exceeds the capture bound: {name}")
            data = path.read_bytes()
            if len(data) > LIMIT:
                raise ValueError(f"source grew beyond the capture bound: {name}")
            if path.suffix == ".tar":
                count = 0
                expanded = 0
                with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
                    for member in archive:
                        part = PurePosixPath(member.name)
                        if part.is_absolute() or ".." in part.parts or member.issym() or member.islnk():
                            raise ValueError(f"unsafe archive member: {name}")
                        if member.isdir():
                            continue
                        if not member.isfile() or member.size > LIMIT:
                            raise ValueError(f"unsupported archive member: {name}")
                        expanded += member.size
                        if expanded > 4 * LIMIT:
                            raise ValueError(f"archive expansion exceeds its bound: {name}")
                        stream = archive.extractfile(member)
                        if stream is None:
                            raise ValueError(f"unreadable archive member: {name}")
                        with stream:
                            blob = stream.read(LIMIT + 1)
                        if len(blob) != member.size:
                            raise ValueError(f"archive member size differs: {name}")
                        inputs.append((f"{name}!{member.name}", blob))
                        count += 1
                rows.append(
                    {
                        "source": name,
                        "classification": "expanded-archive",
                        "source_bytes": len(data),
                        "source_sha256": digest(data),
                        "member_count": count,
                    }
                )
            else:
                inputs.append((name, data))
        else:
            raise ValueError(f"source is missing or special: {name}")

    for label, path in sorted(sources.items()):
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", label):
            raise ValueError("source labels must be portable logical names")
        visit(path, label)
    payloads = ordered_map(_payload, inputs, min_items=1)
    output.mkdir(parents=True)
    (output / "captures").mkdir()
    for row, content in payloads:
        if content is not None and row["git_blob_oid"] in tracked:
            row = {
                "source": row["source"],
                "source_bytes": row["source_bytes"],
                "source_sha256": row["source_sha256"],
                "classification": "already-retained",
                "git_blob_oid": row["git_blob_oid"],
                "repository_path": tracked[row["git_blob_oid"]],
                "repository_commit": commit,
            }
            content = None
        rows.append(row)
        if content is not None:
            path = output / row["retained"]
            if not path.exists():
                path.write_bytes(content)
    record = {
        "schema": SCHEMA,
        "boundary": (
            "Sanitized source snapshots and dispositions; original digests identify inputs, "
            "not preserved raw bytes or completed execution."
        ),
        "artifacts": sorted(rows, key=lambda row: row["source"]),
    }
    data = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode()
    (output / "inventory.json").write_bytes(data)
    (output / "inventory.sha256").write_text(digest(data) + "\n")
    check(output)


def _verify_row(arguments: tuple[Path, dict[str, Any]]) -> str | None:
    output, row = arguments
    if row["classification"] == "already-retained":
        repository_path = PurePosixPath(row["repository_path"])
        if repository_path.is_absolute() or ".." in repository_path.parts:
            raise ValueError("repository evidence path escapes checkout")
        blob = (ROOT / repository_path).read_bytes()
        if digest(blob) != row["source_sha256"] or len(blob) != row["source_bytes"]:
            raise ValueError("repository evidence digest differs")
    if "retained" not in row:
        return None
    relative = PurePosixPath(row["retained"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "captures":
        raise ValueError("retained path escapes captures")
    path = output / relative
    if path.is_symlink():
        raise ValueError("retained file is a symbolic link")
    blob = path.read_bytes()
    if len(blob) != row["retained_bytes"] or digest(blob) != row["retained_sha256"]:
        raise ValueError("retained artifact digest differs")
    if row["content_changed"] != (row["source_sha256"] != row["retained_sha256"]):
        raise ValueError("content transformation declaration differs")
    if row["classification"] == "retained-sanitized" and sanitize(blob) != blob:
        raise ValueError("retained text contains an unsanitized identifier or path")
    return relative.as_posix()


def disposition_corrections(record: dict[str, Any]) -> dict[str, str]:
    """Correct historical deduplication metadata without rewriting bound inventories."""
    corrections = {}
    for row in record["artifacts"]:
        if row["classification"] != "already-retained":
            continue
        name = row["source"]
        if external_copy(name):
            corrections[name] = "external-reading-copy"
        elif PurePosixPath(name).suffix == ".lock":
            corrections[name] = "transient-noise"
    return corrections


def check(output: Path) -> None:
    data = (output / "inventory.json").read_bytes()
    if (output / "inventory.sha256").read_text().strip() != digest(data):
        raise ValueError("inventory digest differs")
    record = json.loads(data)
    if record.get("schema") != SCHEMA:
        raise ValueError("inventory schema differs")
    correction_path = output / "disposition-corrections.json"
    corrections = json.loads(correction_path.read_text()) if correction_path.exists() else {}
    if corrections != disposition_corrections(record):
        raise ValueError("historical disposition corrections differ")
    names = set()
    for row in record["artifacts"]:
        if row["source"] in names:
            raise ValueError("duplicate source identity")
        names.add(row["source"])
    verified = ordered_map(_verify_row, [(output, row) for row in record["artifacts"]], min_items=1)
    expected = {path for path in verified if path is not None}
    actual = {path.relative_to(output).as_posix() for path in (output / "captures").rglob("*") if path.is_file()}
    if actual != expected:
        raise ValueError("retained artifact file set differs")
    print(f"artifact retention: {len(names)} source identities, {len(expected)} unique retained captures")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source", action="append", default=[], metavar="LABEL=PATH")
    parser.add_argument("--tracked-root", type=Path, help="link byte-identical inputs to retained Git blobs")
    parser.add_argument("--write-disposition-corrections", action="store_true")
    args = parser.parse_args()
    if args.write_disposition_corrections:
        if args.source or args.check or args.tracked_root:
            parser.error("correction generation reads one historical inventory alone")
        record = json.loads((args.directory / "inventory.json").read_text())
        correction_path = args.directory / "disposition-corrections.json"
        with correction_path.open("x") as stream:
            stream.write(json.dumps(disposition_corrections(record), indent=1, sort_keys=True) + "\n")
        check(args.directory)
    elif args.check:
        if args.source:
            parser.error("--check reads retained evidence alone")
        check(args.directory)
    else:
        if any("=" not in item for item in args.source):
            parser.error("each source requires LABEL=PATH")
        sources = dict(item.split("=", 1) for item in args.source)
        if not sources or len(sources) != len(args.source):
            parser.error("capture requires unique --source LABEL=PATH values")
        capture({label: Path(path) for label, path in sources.items()}, args.directory, args.tracked_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
