"""Contract for fetch_source_cache: a reading copy enters the ignored cache only when its bytes match the registry,
from the network loader or a documents checkout, and a mismatch leaves the cache untouched.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import fetch_source_cache as fetch
import pytest

PAYLOAD = b"%PDF-1.7\nregistered bytes\n"


def make_root(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    entry = {
        "source_url": "https://example.org/paper-v1.pdf",
        "note": "docs/notes/papers/paper.md",
        "sha256": hashlib.sha256(PAYLOAD).hexdigest(),
        "bytes": len(PAYLOAD),
        "local_cache_path": "docs/local_source_cache/paper-v1.pdf",
    }
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "SOURCES.json").write_text(json.dumps({"external_pdfs": [entry]}))
    return tmp_path, entry


def test_matching_payload_is_restored_and_checked(tmp_path: Path) -> None:
    root, entry = make_root(tmp_path)
    if fetch.restore(root, entry, lambda _: (200, PAYLOAD)) is not None:
        raise AssertionError("a matching payload is refused")
    if (root / entry["local_cache_path"]).read_bytes() != PAYLOAD or fetch.cached_error(root, entry) is not None:
        raise AssertionError("the restored copy differs")
    if fetch.main(["--root", str(root), "--check"]) != 0:
        raise AssertionError("check rejects a matching copy")


@pytest.mark.parametrize(
    "answer, reason",
    [
        ((404, b""), "HTTP 404"),
        ((200, b"<html>moved</html>"), "payload is not a PDF"),
        ((200, PAYLOAD + b"x"), "size"),
        ((200, PAYLOAD[:-1] + b"?"), "sha256"),
    ],
)
def test_mismatch_writes_nothing(tmp_path: Path, answer: tuple[int, bytes], reason: str) -> None:
    root, entry = make_root(tmp_path)
    refusal = fetch.restore(root, entry, lambda _: answer)
    if refusal is None or reason not in refusal or (root / entry["local_cache_path"]).exists():
        raise AssertionError(f"refusal {refusal!r}")
    if fetch.main(["--root", str(root), "--check"]) != 1:
        raise AssertionError("check accepts a missing copy")


def test_documents_checkout_supplies_the_payload(tmp_path: Path) -> None:
    root, entry = make_root(tmp_path / "repo")
    documents = tmp_path / "documents"
    loader = fetch.documents_loader(documents)
    if loader(entry) != (404, b""):
        raise AssertionError("an absent documents file answers")
    (documents / "pdf").mkdir(parents=True)
    (documents / "pdf" / "paper-v1.pdf").write_bytes(PAYLOAD)
    if fetch.main(["--root", str(root), "--missing", "--from-documents", str(documents)]) != 0:
        raise AssertionError("restore from the documents checkout")
    if fetch.cached_error(root, entry) is not None:
        raise AssertionError("the documents copy differs")


def test_selection_refuses_unknown_names(tmp_path: Path) -> None:
    root, _ = make_root(tmp_path)
    with pytest.raises(SystemExit):
        fetch.main(["--root", str(root), "--check", "--note", "docs/notes/papers/absent.md"])
    if fetch.main(["--root", str(root), "--check", "--file", "paper-v1.pdf"]) != 1:
        raise AssertionError("a selected missing copy passes")


@pytest.mark.parametrize(
    ("selectors", "refused"),
    [
        (["--note", "paper-v1.pdf"], "--note paper-v1.pdf"),
        (["--file", "docs/notes/papers/paper.md"], "--file docs/notes/papers/paper.md"),
        (["--note", "docs/notes/papers/paper.md", "--file", "absent.pdf"], "for: --file absent.pdf"),
    ],
    ids=["file-name-as-note", "note-as-file-name", "valid-and-invalid"],
)
def test_selection_matches_each_flag_to_its_own_field(tmp_path: Path, selectors: list[str], refused: str) -> None:
    root, _ = make_root(tmp_path)
    with pytest.raises(SystemExit, match=f"{re.escape(refused)}$"):
        fetch.main(["--root", str(root), "--check", *selectors])
    entries = fetch.registry_entries(root)
    if fetch.select(entries, ["docs/notes/papers/paper.md"], []) != entries:
        raise AssertionError("--note selects its entry by note path")
    if fetch.select(entries, [], ["paper-v1.pdf"]) != entries:
        raise AssertionError("--file selects its entry by cache file name")
