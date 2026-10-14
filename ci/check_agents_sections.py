"""Check that the algebra circuit design rules bind every directory that carries them.

The root AGENTS.md owns the section between the algebra-circuit-rules markers.
gororoba_quantum/AGENTS.md and scripts/AGENTS.md repeat it byte for byte, and
the root and each of those directories load their AGENTS.md through a
CLAUDE.md with a line that is exactly `@AGENTS.md`, outside HTML comments and
fenced code (backtick or tilde, closed by a matching fence), so an agent
started in any of them reads the same rules.

Usage: "$PYTHON" ci/check_agents_sections.py   (from the repository root)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = b"<!-- algebra-circuit-rules:begin -->"
END = b"<!-- algebra-circuit-rules:end -->"
NESTED = ("gororoba_quantum", "scripts")


def read(path: Path) -> bytes:
    """Raw bytes, so a CRLF or other line-ending change counts as a difference."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing") from None


def section(path: Path) -> bytes:
    data = read(path)
    if data.count(BEGIN) != 1 or data.count(END) != 1:
        raise SystemExit(f"{path.relative_to(ROOT)}: needs exactly one algebra-circuit-rules section")
    start, end = data.index(BEGIN), data.index(END) + len(END)
    if start > end:
        raise SystemExit(f"{path.relative_to(ROOT)}: section markers out of order")
    body = data[start:end]
    if not body.isascii():
        raise SystemExit(f"{path.relative_to(ROOT)}: section carries non-ASCII text")
    return body


def loads_agents(path: Path) -> bool:
    """True when some line outside HTML comments and fenced code is exactly @AGENTS.md.

    A fence opens with three or more backticks or tildes and closes only on a
    line of the same character at least as long (CommonMark); fence markers
    inside a comment open nothing.
    """
    fence: tuple[str, int] | None = None
    in_comment = False
    for raw in read(path).decode("utf-8").splitlines():
        line = raw.strip()
        if in_comment:
            in_comment = "-->" not in line
            continue
        if fence is not None:
            closing = re.fullmatch(r"(`{3,}|~{3,})", line)
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= fence[1]:
                fence = None
            continue
        opening = re.match(r"`{3,}|~{3,}", line)
        if opening:
            fence = (opening[0][0], len(opening[0]))
            continue
        if line.startswith("<!--"):
            in_comment = "-->" not in line[4:]
            continue
        if line == "@AGENTS.md":
            return True
    return False


def main() -> int:
    reference = section(ROOT / "AGENTS.md")
    for directory in NESTED:
        if section(ROOT / directory / "AGENTS.md") != reference:
            raise SystemExit(f"{directory}/AGENTS.md: algebra circuit rules differ from the root AGENTS.md")
    for directory in ("", *NESTED):
        loader = ROOT / directory / "CLAUDE.md"
        if not loads_agents(loader):
            raise SystemExit(f"{loader.relative_to(ROOT)}: needs a line that is exactly @AGENTS.md")
    print(f"algebra circuit rules: root and {', '.join(NESTED)} identical ({len(reference)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
