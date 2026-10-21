"""Check every relative link and heading anchor in the tracked Markdown files.

A link target resolves against the linking file's directory (repo-root-relative
for a leading slash). The target has to be a tracked file or a directory that
holds tracked files, with `literature -> docs` normalized. A `#fragment` on a
Markdown target has to match a heading slug computed by GitHub's rules
(lowercase, drop characters other than letters, digits, underscore, hyphen and
space, spaces to hyphens, repeated slugs numbered -1, -2) or an explicit
`id=` / `name=` attribute of the target. Absolute URLs (any scheme) and
fragments on non-Markdown targets are out of scope.

Excluded trees (their bytes are captured vendor pages or retained records and
keep the links of their source):
  results/                                  retained audit records
  docs/notes/iqm/{docs,changelog}/          captured IQM documentation
  docs/notes/kaggle/{cli,site}/             captured Kaggle documentation
  docs/notes/open_quantum/{docs,site}/      captured Open Quantum pages
  docs/notes/packages/manual/               captured package manuals
  docs/notes/quandela/{guide,legal,perceval}/  captured Quandela pages
  docs/notes/quantum_inspire/{cqasm-spec,releases,sdk,site}/  captured QI pages
  docs/notes/ibm_quantum/{processor-types,qpu-information,transpile,transpile-with-pass-managers,
    transpiler-stages,execute-dynamic-circuits,fractional-gates,stretch,qiskit-runtime-circuit-timing,
    repetition-rate-execution,calibration-jobs,estimate-job-run-time}.md   transcribed IBM documentation
  docs/local_source_cache/, docs/source_archives/  retained source copies

Usage:
  "$PYTHON" scripts/check_markdown_links.py [--root DIR]
  "$PYTHON" scripts/check_markdown_links.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

EXCLUDED_PREFIXES = (
    "results/",
    "docs/notes/iqm/docs/",
    "docs/notes/iqm/changelog/",
    "docs/notes/kaggle/cli/",
    "docs/notes/kaggle/site/",
    "docs/notes/open_quantum/docs/",
    "docs/notes/open_quantum/site/",
    "docs/notes/packages/manual/",
    "docs/notes/quandela/guide/",
    "docs/notes/quandela/legal/",
    "docs/notes/quandela/perceval/",
    "docs/notes/quantum_inspire/cqasm-spec/",
    "docs/notes/quantum_inspire/releases/",
    "docs/notes/quantum_inspire/sdk/",
    "docs/notes/quantum_inspire/site/",
    "docs/local_source_cache/",
    "docs/source_archives/",
)
IBM_TRANSCRIPTIONS = (
    "calibration-jobs",
    "estimate-job-run-time",
    "execute-dynamic-circuits",
    "fractional-gates",
    "processor-types",
    "qiskit-runtime-circuit-timing",
    "qpu-information",
    "repetition-rate-execution",
    "stretch",
    "transpile",
    "transpile-with-pass-managers",
    "transpiler-stages",
)
EXCLUDED_PATTERNS = (re.compile(r"^docs/notes/ibm_quantum/(?:" + "|".join(IBM_TRANSCRIPTIONS) + r")\.md$"),)

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
INLINE_LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*(<[^>]*>|[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)")
REF_DEF = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]*>|\S+)")
HTML_ATTR = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""")
ID_ATTR = re.compile(r"""\b(?:id|name)\s*=\s*["']([^"']+)["']""")
ATX = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def is_excluded(path: str) -> bool:
    return path.startswith(EXCLUDED_PREFIXES) or any(p.match(path) for p in EXCLUDED_PATTERNS)


def strip_comments(text: str) -> str:
    """Blank HTML comments, keeping their newlines, since GitHub renders neither links nor headings inside them."""
    return HTML_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def strip_code(lines: list[str], inline: bool = True) -> list[str]:
    """Blank fenced blocks (and inline code spans when asked), keeping line numbers."""
    out: list[str] = []
    fence = ""
    for line in lines:
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = ""
            out.append("")
        elif match:
            fence = match.group(1)
            out.append("")
        else:
            out.append(INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line) if inline else line)
    return out


def heading_text(raw: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", raw)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "").replace("*", "")
    return re.sub(r"(?<!\w)_|_(?!\w)", "", text).strip()


def slugify(text: str) -> str:
    kept = []
    for char in text.lower():
        if char in "-_ " or unicodedata.category(char)[0] in "LN" or unicodedata.category(char) == "Mn":
            kept.append(char)
    return "".join(kept).replace(" ", "-")


def anchors_of(text: str) -> set[str]:
    """Return heading slugs and explicit id/name attributes of one Markdown document."""
    lines = strip_code(text.split("\n"), inline=False)
    lines = strip_comments("\n".join(lines)).split("\n")
    seen: Counter[str] = Counter()
    found: set[str] = set()

    def add(heading: str) -> None:
        slug = slugify(heading_text(heading))
        count = seen[slug]
        seen[slug] += 1
        found.add(slug if count == 0 else f"{slug}-{count}")

    for index, line in enumerate(lines):
        atx = ATX.match(line)
        if atx:
            add(atx.group(2))
        elif index and SETEXT.match(line) and lines[index - 1].strip() and not ATX.match(lines[index - 1]):
            previous = lines[index - 1]
            if not previous.lstrip().startswith(("-", "*", "+", ">", "|")):
                add(previous.strip())
    for line in lines:
        found.update(ID_ATTR.findall(line))
    return found


def link_targets(text: str) -> list[tuple[int, str]]:
    """Inline links match over the whole text, so a label that wraps lines is read; a blank line ends a label."""
    found: list[tuple[int, str]] = []
    joined = strip_comments("\n".join(strip_code(text.split("\n"))))
    lines = joined.split("\n")
    for match in INLINE_LINK.finditer(joined):
        if "\n\n" not in match.group(0):
            found.append((joined.count("\n", 0, match.start()) + 1, match.group(1)))
    for number, line in enumerate(lines, start=1):
        ref = REF_DEF.match(line)
        if ref:
            found.append((number, ref.group(1)))
        for attr in HTML_ATTR.findall(line):
            found.append((number, attr))
    return found


def normalize(path: str) -> str:
    return "docs/" + path[len("literature/") :] if path.startswith("literature/") else path


def check(root: Path, tracked: set[str], files: list[str]) -> list[str]:
    """Return one `path:line: message` per broken link or anchor."""
    tracked_n = {normalize(p) for p in tracked}
    directories = {str(parent) for p in tracked_n for parent in PurePosixPath(p).parents}
    anchor_cache: dict[str, set[str]] = {}

    def anchors(path: str) -> set[str]:
        if path not in anchor_cache:
            real = root / path
            if not real.is_file() and path.startswith("docs/"):
                real = root / "literature" / path[len("docs/") :]
            anchor_cache[path] = anchors_of(real.read_text(encoding="utf-8", errors="replace"))
        return anchor_cache[path]

    problems: list[str] = []
    for source in files:
        text = (root / source).read_text(encoding="utf-8", errors="replace")
        for number, raw in link_targets(text):
            target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
            if not target or SCHEME.match(target) or target.startswith("//"):
                continue
            path_part, _, fragment = target.partition("#")
            path_part = unquote(path_part.split("?", 1)[0])
            fragment = unquote(fragment)
            if not path_part:
                resolved = normalize(source)
            else:
                base = PurePosixPath("") if path_part.startswith("/") else PurePosixPath(source).parent
                joined = PurePosixPath(*[p for p in (base / path_part.lstrip("/")).parts if p != "."])
                parts: list[str] = []
                for part in joined.parts:
                    if part == "..":
                        if not parts:
                            parts = [".."]
                            break
                        parts.pop()
                    else:
                        parts.append(part)
                if parts[:1] == [".."]:
                    problems.append(f"{source}:{number}: link leaves the repository: {target}")
                    continue
                resolved = normalize("/".join(parts))
            if resolved and resolved not in tracked_n and resolved.rstrip("/") not in directories:
                problems.append(f"{source}:{number}: broken link target: {target}")
                continue
            if fragment and resolved in tracked_n and resolved.endswith(".md"):
                if fragment not in anchors(resolved):
                    problems.append(f"{source}:{number}: broken anchor: {target}")
    return problems


def tracked_files(root: Path) -> set[str]:
    output = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], check=True, capture_output=True, text=True
    ).stdout
    return {p for p in output.split("\0") if p}


def run(root: Path) -> int:
    tracked = tracked_files(root)
    files = sorted(p for p in tracked if p.endswith(".md") and not is_excluded(p) and (root / p).is_file())
    problems = check(root, tracked, files)
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} broken link(s) in {len(files)} Markdown files", file=sys.stderr)
        return 1
    print(f"checked {len(files)} Markdown files: every relative link and anchor resolves")
    return 0


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="md-links-") as name:
        root = Path(name)
        (root / "docs/notes").mkdir(parents=True)
        (root / "docs/notes/target.md").write_text(
            "# Title\n\n## Repeated\n\n## Repeated\n\n## A `code` Heading: 1.5 (x_y)\n\nSetext\n------\n"
            '<a id="named"></a>\n\n```\n# not a heading\n```\n<!--\n# Ghost\n-->\n',
            encoding="utf-8",
        )
        good = (
            "[a](notes/target.md) [b](notes/target.md#title) [c](notes/target.md#repeated-1)\n"
            "[d](notes/target.md#a-code-heading-15-x_y) [e](notes/target.md#setext) [f](notes/target.md#named)\n"
            "[g](https://example.invalid/x#y) [h](#local) [i](../literature/notes/target.md)\n"
            "[j](notes/) `[inline](missing.md)`\n\n```\n[fenced](missing.md)\n```\n\n## Local\n"
            "[ref]: notes/target.md#title\n"
            "Text.[^1]\n\n[^1]: Supporting details\n<!-- [old](missing.md) -->\n"
        )
        (root / "docs/good.md").write_text(good, encoding="utf-8")
        (root / "literature").symlink_to("docs")
        bad = (
            "[x](notes/missing.md)\n[y](notes/target.md#no-such-heading)\n[z](#nothing-here)\n[w](../../outside.md)\n"
            "A [label that\nwraps](notes/wrapped-missing.md) across lines.\n"
            "[case](notes/target.md#Title) [ghost](notes/target.md#ghost)\n"
        )
        (root / "docs/bad.md").write_text(bad, encoding="utf-8")
        tracked = {"docs/notes/target.md", "docs/good.md", "docs/bad.md"}
        if problems := check(root, tracked, ["docs/good.md"]):
            print("self-test: false positives:\n" + "\n".join(problems))
            return 1
        found = check(root, tracked, ["docs/bad.md"])
        wanted = (
            "notes/missing.md",
            "no-such-heading",
            "nothing-here",
            "outside.md",
            "wrapped-missing.md",
            "#Title",
            "#ghost",
        )
        if len(found) != len(wanted) or any(not any(w in line for line in found) for w in wanted):
            print("self-test: planted defects not all reported:\n" + "\n".join(found))
            return 1
    print("self-test passed: 7 planted defects reported, 0 false positives")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    return self_test() if arguments.self_test else run(arguments.root)


if __name__ == "__main__":
    sys.exit(main())
