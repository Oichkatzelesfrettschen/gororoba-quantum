"""Check that the replicated AGENTS.md sections bind every directory that carries them.

The owner named in SECTIONS holds each section, delimited by
`<!-- NAME:begin -->` and `<!-- NAME:end -->`, and every copy directory listed
for it repeats it byte for byte: gororoba_quantum/AGENTS.md owns the algebra
circuit design rules, which scripts/AGENTS.md repeats, and the Heron execution
facts, which have no copy. The root and each nested directory carry a CLAUDE.md whose
entire content is the loader line `@AGENTS.md` followed by one LF, so an agent
started in any of them reads the same rules. The loader format is fixed bytes: a CLAUDE.md
that adds prose, comments, fences or a different line ending fails, which
leaves no Markdown construct able to hide the import.

Usage: "$PYTHON" ci/check_agents_sections.py [--self-test]   (from the repository root)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# section name -> (owner directory, directories that repeat the owner's bytes)
SECTIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "algebra-circuit-rules": ("gororoba_quantum", ("scripts",)),
    "heron-execution-facts": ("gororoba_quantum", ()),
}
LOADER = b"@AGENTS.md\n"
NESTED = ("gororoba_quantum", "scripts", "ci")


def read(path: Path) -> bytes:
    """Raw bytes, so a CRLF or other line-ending change counts as a difference."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing") from None


def section(path: Path, name: str) -> bytes:
    data = read(path)
    begin, end_marker = f"<!-- {name}:begin -->".encode(), f"<!-- {name}:end -->".encode()
    if data.count(begin) != 1 or data.count(end_marker) != 1:
        raise SystemExit(f"{path.relative_to(ROOT)}: needs exactly one {name} section")
    start, end = data.index(begin), data.index(end_marker) + len(end_marker)
    if start > end:
        raise SystemExit(f"{path.relative_to(ROOT)}: section markers out of order")
    body = data[start:end]
    if not body.isascii():
        raise SystemExit(f"{path.relative_to(ROOT)}: section carries non-ASCII text")
    return body


def is_loader(data: bytes) -> bool:
    return data == LOADER


def self_test() -> None:
    """Every loader variant other than the exact bytes fails, including Markdown that hides the import."""
    rejected = {
        "inline comment opened after text": b"text <!--\n@AGENTS.md\n-->\n",
        "second comment on one line": b"<!-- first --> text <!--\n@AGENTS.md\n-->\n",
        "comment block": b"<!--\n@AGENTS.md\n-->\n",
        "backtick fence": b"```\n@AGENTS.md\n```\n",
        "tilde fence": b"~~~\n@AGENTS.md\n~~~\n",
        "nested backtick fence": b"````\n```\n@AGENTS.md\n````\n",
        "comment holding a fence": b"<!-- ```\n-->\n@AGENTS.md\n```\n",
        "CRLF": b"@AGENTS.md\r\n",
        "missing newline": b"@AGENTS.md",
        "leading prose": b"# loader\n@AGENTS.md\n",
        "trailing prose": b"@AGENTS.md\nmore\n",
        "indented": b"  @AGENTS.md\n",
        "empty": b"",
    }
    for name, data in rejected.items():
        if is_loader(data):
            raise SystemExit(f"self-test: accepted {name}")
    if not is_loader(LOADER):
        raise SystemExit("self-test: rejected the canonical loader")
    print(f"loader self-test: {len(rejected)} variants rejected, canonical bytes accepted")


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        self_test()
        return 0
    if argv:
        raise SystemExit("usage: check_agents_sections.py [--self-test]")
    sizes = []
    for name, (owner, copies) in SECTIONS.items():
        reference = section(ROOT / owner / "AGENTS.md", name)
        for directory in copies:
            if section(ROOT / directory / "AGENTS.md", name) != reference:
                raise SystemExit(f"{directory}/AGENTS.md: {name} differs from {owner}/AGENTS.md")
        holders = ", ".join((owner, *copies))
        sizes.append(f"{name} in {holders} ({len(reference)} bytes)")
    for directory in ("", *NESTED):
        loader = ROOT / directory / "CLAUDE.md"
        if not is_loader(read(loader)):
            raise SystemExit(f"{loader.relative_to(ROOT)}: must contain exactly the line @AGENTS.md and one LF")
    print("identical sections: " + "; ".join(sizes))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
