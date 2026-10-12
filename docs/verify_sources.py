"""Verify retained source identities, provenance coverage, and historical aliases."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify() -> None:
    root = Path(__file__).resolve().parents[1]
    library = root / "docs"
    registry: dict[str, Any] = json.loads((library / "SOURCES.json").read_text())
    require(registry["schema"] == "primary-source-library-v1", "unsupported source registry")
    checksum_lines: list[str] = []
    registered_paths: set[str] = set()
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
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", note.read_text()):
            if ":" in target or target.startswith("#"):
                continue
            relative_target = target.split("#", 1)[0]
            require((note.parent / relative_target).exists(), f"broken link: {note.relative_to(root)} -> {target}")
            link_count += 1
    print(
        f"Verified {len(registered_paths)} PDFs, {len(alias_paths)} PDF aliases, "
        f"historical identities, and {link_count} local links"
    )


if __name__ == "__main__":
    verify()
