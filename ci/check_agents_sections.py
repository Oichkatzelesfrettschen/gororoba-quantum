"""Check that the algebra circuit design rules bind every directory that carries them.

The root AGENTS.md owns the section between the algebra-circuit-rules markers.
gororoba_quantum/AGENTS.md and scripts/AGENTS.md repeat it byte for byte, and
each of those directories loads its AGENTS.md through a CLAUDE.md containing
`@AGENTS.md`, so an agent started in either subtree reads the same rules.

Usage: "$PYTHON" ci/check_agents_sections.py   (from the repository root)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- algebra-circuit-rules:begin -->"
END = "<!-- algebra-circuit-rules:end -->"
NESTED = ("gororoba_quantum", "scripts")


def section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise SystemExit(f"{path.relative_to(ROOT)}: needs exactly one algebra-circuit-rules section")
    start, end = text.index(BEGIN), text.index(END) + len(END)
    if start > end:
        raise SystemExit(f"{path.relative_to(ROOT)}: section markers out of order")
    body = text[start:end]
    if not body.isascii():
        raise SystemExit(f"{path.relative_to(ROOT)}: section carries non-ASCII text")
    return body


def main() -> int:
    reference = section(ROOT / "AGENTS.md")
    for directory in NESTED:
        if section(ROOT / directory / "AGENTS.md") != reference:
            raise SystemExit(f"{directory}/AGENTS.md: algebra circuit rules differ from the root AGENTS.md")
        loader = (ROOT / directory / "CLAUDE.md").read_text(encoding="utf-8")
        if "@AGENTS.md" not in loader.split():
            raise SystemExit(f"{directory}/CLAUDE.md: must load @AGENTS.md")
    print(f"algebra circuit rules: root and {', '.join(NESTED)} identical ({len(reference)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
