"""Contract for check_markdown_links block parsing: code blocks, code spans and fences hide links and anchors as
CommonMark renders them, and repeated headings take the anchors GitHub's renderer assigns.
"""

from __future__ import annotations

import check_markdown_links as cml
import pytest


def targets(text: str) -> list[str]:
    return [target for _, target in cml.link_targets(text)]


@pytest.mark.parametrize(
    ("headings", "anchors"),
    [
        (["A", "A", "A-1"], ["a", "a-1", "a-1-1"]),
        (["A-1", "A", "A"], ["a-1", "a", "a-2"]),
        (
            ["A-1", "A-1", "A", "A", "A", "B", "B-1", "B", "B-1"],
            ["a-1", "a-1-1", "a", "a-2", "a-3", "b", "b-1", "b-2", "b-1-1"],
        ),
    ],
)
def test_repeated_headings_take_github_anchors(headings: list[str], anchors: list[str]) -> None:
    # Expected ids are those GitHub's contents API renders (application/vnd.github.html) for these documents.
    found = cml.anchors_of("".join(f"# {heading}\n\n" for heading in headings))
    if found != set(anchors):
        raise AssertionError(f"{headings} -> {sorted(found)}, expected {anchors}")


def test_code_span_attribute_is_no_anchor() -> None:
    found = cml.anchors_of('Write `<a id="ghost"></a>` for an anchor.\n\n<a id="real"></a>\n\n# `Code` heading\n')
    if "ghost" in found or not {"real", "code-heading"} <= found:
        raise AssertionError(f"anchors {sorted(found)}")


@pytest.mark.parametrize(
    "text",
    [
        "```\n[hidden](a.md)\n``` still code\n[hidden](b.md)\n```\n[shown](c.md)\n",
        "~~~\n[hidden](a.md)\n```\n[hidden](b.md)\n~~~~~\n[shown](c.md)\n",
        "````\n[hidden](a.md)\n```\n[hidden](b.md)\n````  \n[shown](c.md)\n",
        "```py\n[hidden](a.md)\n   ```\n[shown](c.md)\n",
    ],
    ids=["trailing-text", "tilde-longer-close", "backtick-longer-open", "indented-close"],
)
def test_fence_closes_only_on_a_bare_matching_run(text: str) -> None:
    if targets(text) != ["c.md"]:
        raise AssertionError(f"targets {targets(text)}")


@pytest.mark.parametrize(
    ("text", "shown"),
    [
        ("Intro.\n\n    [hidden](a.md)\n\n[shown](c.md)\n", ["c.md"]),
        ("# Heading\n    [hidden](a.md)\n", []),
        ("A paragraph\n    [shown](c.md) continues it.\n", ["c.md"]),
        ("- item\n\n    [shown](c.md) belongs to the item.\n", ["c.md"]),
        ("- item\n\n      [hidden](a.md)\n", []),
        ("- a\n  - b\n\n        [hidden](a.md)\n\n      [shown](c.md)\n", ["c.md"]),
        ("1. step\n\n       [hidden](a.md)\n\n[shown](c.md)\n", ["c.md"]),
        ("- item\n\n\t[shown](c.md)\n", ["c.md"]),
        ("\t[hidden](a.md)\n", []),
    ],
    ids=[
        "standalone",
        "after-heading",
        "paragraph-continuation",
        "list-paragraph",
        "list-code",
        "nested-list",
        "ordered-list",
        "tab-list-paragraph",
        "tab-code",
    ],
)
def test_indented_code_follows_paragraph_and_list_context(text: str, shown: list[str]) -> None:
    if targets(text) != shown:
        raise AssertionError(f"targets {targets(text)}, expected {shown}")


def test_list_fence_ends_with_its_item() -> None:
    text = "- item\n\n  ```\n  [hidden](a.md)\n  ```\n  [shown](b.md)\n\n- next\n  ```\n[shown](c.md)\n"
    if targets(text) != ["b.md", "c.md"]:
        raise AssertionError(f"targets {targets(text)}")
