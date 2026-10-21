"""Check that every directory carrying an AGENTS.md loads it through a fixed CLAUDE.md.

The root and each nested directory carry a CLAUDE.md whose entire content is
the loader line `@AGENTS.md` followed by one LF, so an agent started in any of
them reads the same rules. The loader format is fixed bytes: a CLAUDE.md
that adds prose, comments, fences or a different line ending fails, which
leaves no Markdown construct able to hide the import. The algebra and Heron
rule texts live once in docs/notes/algebra_circuit_rules.md and
docs/notes/ibm_heron_platform.md, so no replicated section remains to compare.

Usage: "$PYTHON" ci/check_agents_sections.py [--self-test]   (from the repository root)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = b"@AGENTS.md\n"


def nested_directories() -> tuple[str, ...]:
    """Every directory below the root whose AGENTS.md git tracks, so a new guide needs its loader."""
    listed = subprocess.run(
        ["git", "ls-files", "--", "*/AGENTS.md"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.split()
    return tuple(sorted(str(Path(name).parent) for name in listed))


def read(path: Path) -> bytes:
    """Raw bytes, so a CRLF or other line-ending change counts as a difference."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing") from None


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
    nested = nested_directories()
    for directory in ("", *nested):
        loader = ROOT / directory / "CLAUDE.md"
        if not is_loader(read(loader)):
            raise SystemExit(f"{loader.relative_to(ROOT)}: must contain exactly the line @AGENTS.md and one LF")
    print(f"loaders: {len(('', *nested))} CLAUDE.md files hold exactly @AGENTS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
