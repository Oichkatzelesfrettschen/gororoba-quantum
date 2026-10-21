"""Contract for ci/check_agents_sections.py: every loader variant other than the exact bytes fails,
including Markdown that hides the import, and every CLAUDE.md of the tree holds the exact bytes.
"""

from __future__ import annotations

import check_agents_sections
import pytest

REJECTED = {
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


@pytest.mark.parametrize("data", REJECTED.values(), ids=REJECTED.keys())
def test_variant_is_rejected(data: bytes) -> None:
    if check_agents_sections.is_loader(data):
        raise AssertionError(f"accepted {data!r}")


def test_canonical_loader_is_accepted() -> None:
    if not check_agents_sections.is_loader(check_agents_sections.LOADER):
        raise AssertionError("rejected the canonical loader")


def test_repository_loaders() -> None:
    if check_agents_sections.main([]) != 0:
        raise AssertionError("a CLAUDE.md of the tree is not the exact loader")
