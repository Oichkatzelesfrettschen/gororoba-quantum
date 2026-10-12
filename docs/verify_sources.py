"""Verify retained source identities, provenance coverage, and historical aliases."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_external_sources(root: Path, registry: dict[str, Any], published_digests: set[str]) -> int:
    """Keep external-only sources verifiable without publishing local reading copies."""
    cache_root = root / "docs" / "local_source_cache"
    require(not cache_root.is_symlink(), "local source cache must not be a symlink")
    require(not cache_root.exists() or cache_root.is_dir(), "local source cache must be a directory")
    require("/docs/local_source_cache/" in (root / ".gitignore").read_text().splitlines(), "local cache ignore rule")
    if (root / ".git").exists():
        tracked_cache = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "ls-files", "-z", "--", "docs/local_source_cache"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        require(not tracked_cache, "local source cache contains Git-tracked files")
    cache_paths: set[str] = set()
    external_digests: set[str] = set()
    for entry in registry["external_pdfs"]:
        require("path" not in entry, "external-only PDF must not carry a published path")
        require(entry["status"] == "external_only", "external-only PDF status")
        require(entry["redistribution"] == "excluded_without_permission", "external-only redistribution status")
        require(bool(entry["rights_locator"]) and bool(entry["rights_reason"]), "external-only rights provenance")
        require(entry["source_url"].startswith(("https://", "http://")), "external-only source URL")
        digest = entry["sha256"]
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "external-only SHA-256")
        require(digest not in external_digests, "duplicate external-only PDF digest")
        require(digest not in published_digests, "external-only PDF appears in the published inventory")
        external_digests.add(digest)
        for size_field in ("bytes", "pages"):
            require(type(entry[size_field]) is int and entry[size_field] > 0, f"external-only {size_field}")
        note = root / entry["note"]
        require(note.is_file(), "external-only owning note")
        note_text = note.read_text()
        require(digest in note_text and entry["source_url"] in note_text, "external-only note identity")
        excluded_source = root / entry["excluded_published_path"]
        require(excluded_source.parent == root / "docs" / "pdf", "external-only excluded path")
        require(
            not excluded_source.exists() and not excluded_source.is_symlink(), "external-only published file exists"
        )
        relative_cache = entry["local_cache_path"]
        source = root / relative_cache
        require(source.parent == cache_root and source.suffix == ".pdf", "external-only cache path")
        require(relative_cache not in cache_paths, "duplicate external-only cache path")
        cache_paths.add(relative_cache)
        require(not source.is_symlink(), "external-only cache file must not be a symlink")
        if source.exists():
            require(source.is_file(), "external-only cache entry must be a file")
            payload = source.read_bytes()
            require(payload.startswith(b"%PDF-"), "external-only cached PDF header")
            require(len(payload) == entry["bytes"], "external-only cached PDF size")
            require(hashlib.sha256(payload).hexdigest() == digest, "external-only cached PDF digest")
    for manifest in ("PDF_SHA256SUMS", "parallel_experiment_pdfs.sha256"):
        for line in (root / "docs" / manifest).read_text().splitlines():
            digest, relative = line.split(maxsplit=1)
            source = (root / relative.lstrip("*")).resolve()
            require(digest not in external_digests, f"external-only digest in {manifest}")
            require(not source.is_relative_to(cache_root.resolve()), f"local cache path in {manifest}")
    return len(external_digests)


def verify() -> None:
    root = Path(__file__).resolve().parents[1]
    library = root / "docs"
    registry: dict[str, Any] = json.loads((library / "SOURCES.json").read_text())
    require(registry["schema"] == "primary-source-library-v1", "unsupported source registry")
    checksum_lines: list[str] = []
    registered_paths: set[str] = set()
    published_digests: set[str] = set()
    for entry in registry["pdfs"]:
        relative = entry["path"]
        require(relative not in registered_paths, f"duplicate PDF: {relative}")
        registered_paths.add(relative)
        source = root / relative
        require(source.parent == library / "pdf" and not source.is_symlink(), f"PDF path: {relative}")
        payload = source.read_bytes()
        require(payload.startswith(b"%PDF-"), f"PDF header: {relative}")
        require(len(payload) == entry["bytes"], f"PDF size: {relative}")
        digest = hashlib.sha256(payload).hexdigest()
        published_digests.add(digest)
        require(digest == entry["sha256"], f"PDF digest: {relative}")
        require(entry["pages"] > 0, f"recorded page count: {relative}")
        require(entry["source_url"].startswith(("https://", "http://")), f"retrieval URL: {relative}")
        require((root / entry["note"]).is_file(), f"owning note: {relative}")
        checksum_lines.append(f"{digest}  {relative}\n")
    actual_paths = {
        path.relative_to(root).as_posix() for path in (library / "pdf").glob("*.pdf") if not path.is_symlink()
    }
    require(actual_paths == registered_paths, "PDF inventory differs from registry")
    require((library / "PDF_SHA256SUMS").read_text() == "".join(checksum_lines), "PDF checksum inventory")
    external_count = verify_external_sources(root, registry, published_digests)
    alias_paths: set[str] = set()
    for entry in registry["aliases"] + [registry["historical_path_alias"]]:
        alias = root / entry["path"]
        require(alias.is_symlink() and alias.readlink().as_posix() == entry["target"], f"alias: {alias.name}")
        require(alias.resolve().is_relative_to(root) and alias.exists(), f"alias target: {alias.name}")
        if alias.parent == library / "pdf":
            alias_paths.add(alias.relative_to(root).as_posix())
    actual_aliases = {path.relative_to(root).as_posix() for path in (library / "pdf").iterdir() if path.is_symlink()}
    require(actual_aliases == alias_paths, "PDF alias inventory differs from registry")
    for entry in registry["immutable_documentation"]:
        payload = (root / entry["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == entry["sha256"], f"historical digest: {entry['path']}")
        record = json.loads((root / entry["record"]).read_text())
        recorded_hashes = record.get("source_sha256", {}) | record.get("documentation_sha256", {})
        require(recorded_hashes[entry["path"]] == entry["sha256"], "historical manifest identity")
    link_count = 0
    for note in library.rglob("*.md"):
        if library / "local_source_cache" in note.parents:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", note.read_text()):
            if ":" in target or target.startswith("#"):
                continue
            relative_target = target.split("#", 1)[0]
            require((note.parent / relative_target).exists(), f"broken link: {note.relative_to(root)} -> {target}")
            link_count += 1
    print(
        f"Verified {len(registered_paths)} published PDFs, {external_count} external-only PDFs, "
        f"{len(alias_paths)} PDF aliases, "
        f"historical identities, and {link_count} local links"
    )


if __name__ == "__main__":
    verify()
