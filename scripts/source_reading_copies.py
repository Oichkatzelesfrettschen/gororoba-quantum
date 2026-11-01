"""The reading-copy index: every external-only PDF of docs/SOURCES.json with its note, public source and reading copy.

docs/SOURCES.json lists under `external_pdfs` each PDF whose rights exclude redistribution from this repository; its
bytes live in the ignored `docs/local_source_cache/` and in one of the owner's workspace documents repositories,
gororoba-documents-public for an openly licensed file and gororoba-documents-private otherwise, which
scripts/fetch_source_cache.py restores from. Each documents repository names its files in `manifest.tsv` (columns
`sha256`, `bytes`, `path` first), and `docs/sources/reading-copy-locations.tsv` carries the repository and path of
every registered digest so this repository's checks run without either checkout. The index links each entry's note,
its registered `source_url`, and that reading copy.

Usage:
  "$PYTHON" scripts/source_reading_copies.py [--check]

A plain run writes the git-ignored docs/sources/reading-copies.md; `--check` renders in memory, which validates the
registry against the locations file, and compares no file.
  "$PYTHON" scripts/source_reading_copies.py --locate DOCUMENTS_CHECKOUT...

`--locate` rewrites the locations file from the manifests of the named checkouts, whose directory names are the
repository names, then regenerates the index; every registered digest must resolve in exactly one of them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "docs/SOURCES.json"
OUT = ROOT / "docs/sources/reading-copies.md"
LOCATIONS = ROOT / "docs/sources/reading-copy-locations.tsv"
OWNER = "https://github.com/Oichkatzelesfrettschen/"
REPOSITORIES = ("gororoba-documents-public", "gororoba-documents-private")
LOCATIONS_HEADER = "sha256\trepository\tpath\n"

HEADER = """# Reading copies of external sources

Rendered on demand by [`scripts/source_reading_copies.py`](../../scripts/source_reading_copies.py) from
[`SOURCES.json`](../SOURCES.json) and [`reading-copy-locations.tsv`](reading-copy-locations.tsv), and never committed;
edit the registry and run `--locate` against the documents checkouts. Each row names an external-only PDF: its note, its
public source, and its reading copy in one of the owner's documents repositories. A copy in
gororoba-documents-public opens for every reader under the license its manifest row names; a copy in
gororoba-documents-private opens for accounts with access to that repository, and every other reader follows the
public source. [`fetch_source_cache.py`](../../scripts/fetch_source_cache.py) restores the same bytes into the
ignored `docs/local_source_cache/` from either.

| Source | Note | Public source | Reading copy |
|---|---|---|---|
"""


def cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def heading(note: Path) -> str:
    """The note's first Markdown heading, the label of an entry that carries no title."""
    for line in note.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def registry() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = json.loads(SOURCES.read_text(encoding="utf-8"))["external_pdfs"]
    return entries


def read_locations() -> dict[str, tuple[str, str]]:
    lines = LOCATIONS.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0] != LOCATIONS_HEADER:
        raise ValueError(f"{LOCATIONS.relative_to(ROOT)} must start with the header {LOCATIONS_HEADER!r}")
    locations: dict[str, tuple[str, str]] = {}
    for line in lines[1:]:
        digest, repository, path = line.rstrip("\n").split("\t")
        if repository not in REPOSITORIES or digest in locations:
            raise ValueError(f"{LOCATIONS.relative_to(ROOT)}: bad or repeated row for {digest}")
        locations[digest] = (repository, path)
    return locations


def row(entry: dict[str, Any], location: tuple[str, str]) -> tuple[str, str]:
    note = Path(entry["note"])
    repository, path = location
    label = cell(entry.get("title") or heading(ROOT / note) or note.stem)
    link = f"[{note.name}](../{note.relative_to('docs').as_posix()})"
    copy = f"[{Path(path).name}]({OWNER}{repository}/blob/main/{path})"
    return label.lower(), f"| {label} | {link} | [source]({entry['source_url']}) | {copy} |"


def render() -> str:
    entries = registry()
    locations = read_locations()
    digests = {entry["sha256"] for entry in entries}
    missing = sorted(digests - set(locations))
    extra = sorted(set(locations) - digests)
    if missing or extra:
        raise ValueError(f"{LOCATIONS.relative_to(ROOT)} lacks {missing} and carries unregistered {extra}")
    rows = sorted(row(entry, locations[entry["sha256"]]) for entry in entries)
    return HEADER + "".join(line + "\n" for _, line in rows)


def manifest_paths(checkout: Path) -> dict[str, str]:
    """Maps each sha256 of the checkout's manifest.tsv to its checkout-relative path."""
    lines = (checkout / "manifest.tsv").read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("sha256\tbytes\tpath"):
        raise ValueError(f"{checkout / 'manifest.tsv'}: header must start with sha256, bytes, path")
    return {fields[0]: fields[2] for fields in (line.split("\t") for line in lines[1:])}


def locate(checkouts: list[Path]) -> str:
    """The locations file for every registered digest, resolved through the named documents checkouts."""
    found: dict[str, list[tuple[str, str]]] = {}
    for checkout in checkouts:
        if checkout.name not in REPOSITORIES:
            raise ValueError(f"{checkout} is not named as one of {REPOSITORIES}")
        for digest, path in manifest_paths(checkout).items():
            found.setdefault(digest, []).append((checkout.name, path))
    rows = []
    for digest in sorted({entry["sha256"] for entry in registry()}):
        hits = found.get(digest, [])
        if len(hits) != 1:
            raise ValueError(f"registered digest {digest} resolves in {len(hits)} documents checkouts")
        rows.append(f"{digest}\t{hits[0][0]}\t{hits[0][1]}\n")
    return LOCATIONS_HEADER + "".join(rows)


def main(argv: list[str]) -> int:
    if argv[:1] == ["--locate"] and len(argv) > 1:
        LOCATIONS.write_text(locate([Path(arg).resolve() for arg in argv[1:]]), encoding="utf-8")
        argv = []
    text = render()
    if argv == ["--check"]:
        return 0
    if argv:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
