"""Contract for source_reading_copies: every registered digest resolves in exactly one documents checkout, and the
index links each entry to the repository and path its manifest row names.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import source_reading_copies as index

DIGEST = "a" * 64


def make_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    (root / "docs/sources").mkdir(parents=True)
    (root / "docs/notes/papers").mkdir(parents=True)
    (root / "docs/notes/papers/paper.md").write_text("# A paper\n", encoding="utf-8")
    entry = {"sha256": DIGEST, "note": "docs/notes/papers/paper.md", "source_url": "https://example.org/p.pdf"}
    (root / "docs/SOURCES.json").write_text(json.dumps({"external_pdfs": [entry]}), encoding="utf-8")
    monkeypatch.setattr(index, "ROOT", root)
    monkeypatch.setattr(index, "SOURCES", root / "docs/SOURCES.json")
    monkeypatch.setattr(index, "OUT", root / "docs/sources/reading-copies.md")
    monkeypatch.setattr(index, "LOCATIONS", root / "docs/sources/reading-copy-locations.tsv")
    return root


def checkout(tmp_path: Path, name: str, rows: str) -> Path:
    path = tmp_path / name
    path.mkdir()
    (path / "manifest.tsv").write_text("sha256\tbytes\tpath\tsource_url\n" + rows, encoding="utf-8")
    return path


def test_locate_links_the_manifest_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_root(tmp_path, monkeypatch)
    public = checkout(tmp_path, "gororoba-documents-public", f"{DIGEST}\t9\tmathematics/journal/x/p.pdf\t\n")
    private = checkout(tmp_path, "gororoba-documents-private", "")
    if index.main(["--locate", str(public), str(private)]) != 0 or index.main(["--check"]) != 0:
        raise AssertionError("a resolved digest fails to index")
    text = (root / "docs/sources/reading-copies.md").read_text(encoding="utf-8")
    if "gororoba-documents-public/blob/main/mathematics/journal/x/p.pdf" not in text:
        raise AssertionError("the index does not link the manifest path")


@pytest.mark.parametrize("copies", [0, 2], ids=["unresolved", "in-both"])
def test_locate_refuses_a_digest_outside_exactly_one_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, copies: int
) -> None:
    make_root(tmp_path, monkeypatch)
    row = f"{DIGEST}\t9\tp.pdf\t\n"
    public = checkout(tmp_path, "gororoba-documents-public", row if copies else "")
    private = checkout(tmp_path, "gororoba-documents-private", row if copies == 2 else "")
    with pytest.raises(ValueError, match=f"resolves in {copies} documents checkouts"):
        index.main(["--locate", str(public), str(private)])


def test_render_refuses_a_registry_entry_without_location(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = make_root(tmp_path, monkeypatch)
    (root / "docs/sources/reading-copy-locations.tsv").write_text(index.LOCATIONS_HEADER, encoding="utf-8")
    with pytest.raises(ValueError, match="lacks"):
        index.main(["--check"])
