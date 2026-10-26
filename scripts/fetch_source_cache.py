"""Restore the ignored reading copies of external-only sources from their registered URLs.

docs/SOURCES.json lists every external-only PDF under ``external_pdfs`` with
its ``source_url``, ``sha256``, ``bytes`` and ``local_cache_path`` under the
ignored docs/local_source_cache/. ``git worktree remove`` deletes ignored
files, so a reading copy lives in the checkout that reads it and is restored
from the registry. This script downloads each selected entry, admits the
payload only when it starts with ``%PDF-`` and matches the registered size
and digest, and writes it to its cache path through a temporary file in the
same directory. A mismatch writes nothing and is reported, because the
registry rows are immutable and a changed upstream file is a finding for a
new record. ``--from-documents DIR`` reads the payloads from ``DIR/pdf/`` of a
checkout of the private gororoba-quantum-documents repository, under the same
admission rule, instead of the network. ``--check`` reads only the local
cache and the registry.

    $PYTHON scripts/fetch_source_cache.py --note docs/notes/papers/1210.4583.md
    $PYTHON scripts/fetch_source_cache.py --missing
    $PYTHON scripts/fetch_source_cache.py --missing --from-documents ../gororoba-quantum-documents
    $PYTHON scripts/fetch_source_cache.py --check --note docs/notes/papers/1210.4583.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from capture_oq_docs import fetch_status

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path("docs/local_source_cache")


def registry_entries(root: Path) -> list[dict[str, Any]]:
    registry = json.loads((root / "docs" / "SOURCES.json").read_text())
    return list(registry["external_pdfs"])


def select(entries: list[dict[str, Any]], notes: list[str], names: list[str]) -> list[dict[str, Any]]:
    """Returns the entries owned by a named note or cache file, refusing a selector its own flag cannot match.

    ``--note`` matches only the ``note`` field and ``--file`` only the cache file name, so a selector passed
    under the other flag is refused rather than selecting nothing.
    """
    if not notes and not names:
        return entries
    unknown = [f"--note {n}" for n in sorted(set(notes) - {e["note"] for e in entries})]
    unknown += [f"--file {n}" for n in sorted(set(names) - {Path(e["local_cache_path"]).name for e in entries})]
    if unknown:
        raise SystemExit(f"no external_pdfs entry for: {', '.join(unknown)}")
    return [e for e in entries if e["note"] in notes or Path(e["local_cache_path"]).name in names]


def cache_target(root: Path, entry: dict[str, Any]) -> Path:
    relative = Path(entry["local_cache_path"])
    if relative.parent != CACHE or relative.suffix != ".pdf":
        raise SystemExit(f"{entry['note']}: cache path {relative} lies outside {CACHE}")
    return root / relative


def admission_error(entry: dict[str, Any], payload: bytes) -> str | None:
    if not payload.startswith(b"%PDF-"):
        return "payload is not a PDF"
    if len(payload) != entry["bytes"]:
        return f"size {len(payload)} differs from registered {entry['bytes']}"
    digest = hashlib.sha256(payload).hexdigest()
    if digest != entry["sha256"]:
        return f"sha256 {digest} differs from registered {entry['sha256']}"
    return None


def cached_error(root: Path, entry: dict[str, Any]) -> str | None:
    target = cache_target(root, entry)
    if target.is_symlink() or not target.is_file():
        return "missing"
    return admission_error(entry, target.read_bytes())


Loader = Callable[[dict[str, Any]], tuple[int, bytes]]


def network_loader(entry: dict[str, Any]) -> tuple[int, bytes]:
    return fetch_status(entry["source_url"])


def documents_loader(documents: Path) -> Loader:
    """A loader reading ``documents/pdf/<cache name>``, answering 404 for an absent or linked file."""

    def load(entry: dict[str, Any]) -> tuple[int, bytes]:
        source = documents / "pdf" / Path(entry["local_cache_path"]).name
        if source.is_symlink() or not source.is_file():
            return 404, b""
        return 200, source.read_bytes()

    return load


def restore(root: Path, entry: dict[str, Any], load: Loader) -> str | None:
    """Loads one entry and writes it only when it matches the registry; returns the refusal reason."""
    status, payload = load(entry)
    if status != 200:
        return f"HTTP {status}"
    error = admission_error(entry, payload)
    if error is not None:
        return error
    target = cache_target(root, entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=".fetch-", suffix=".pdf")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="checkout whose cache is restored")
    parser.add_argument("--note", action="append", default=[], help="owning note path, as SOURCES.json records it")
    parser.add_argument("--file", action="append", default=[], help="cache file name, for example 1210.4583v2.pdf")
    parser.add_argument("--missing", action="store_true", help="restore only entries whose copy is absent or wrong")
    parser.add_argument("--check", action="store_true", help="verify the local copies without network access")
    parser.add_argument(
        "--from-documents", type=Path, help="read payloads from a gororoba-quantum-documents checkout's pdf/"
    )
    args = parser.parse_args(argv)
    load = network_loader if args.from_documents is None else documents_loader(args.from_documents.resolve())
    root = args.root.resolve()
    entries = select(registry_entries(root), args.note, args.file)
    failures = 0
    for entry in entries:
        name = Path(entry["local_cache_path"]).name
        local = cached_error(root, entry)
        if args.check:
            if local is not None:
                failures += 1
                print(f"{name}: {local}")
            continue
        if args.missing and local is None:
            continue
        refusal = restore(root, entry, load)
        if refusal is not None:
            failures += 1
            print(f"{name}: refused, {refusal}")
        else:
            print(f"{name}: restored")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
