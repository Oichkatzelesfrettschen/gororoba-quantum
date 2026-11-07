"""The Quantum Inspire and Kaggle GPU interpreters run Python 3.13, which rejects the PEP 758 handler
``except A, B:`` that ``ruff format`` writes at the py314 target: every module they import keeps
``except (A, B):``, and pyproject.toml keeps those modules at the py313 target so a format pass leaves the
parentheses in place.
"""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH = (ROOT / "gororoba_quantum", ROOT / "scripts", ROOT / "ci")
# The modules a 3.13 interpreter loads directly: the shared package (run as scripts from gororoba_quantum/), the
# Kaggle kernel entries and the Quantum Inspire scripts, plus whatever repository module each imports.
ROOTS = (
    *sorted((ROOT / "gororoba_quantum").glob("*.py")),
    *sorted((ROOT / "kaggle_kernel").glob("*.py")),
    *sorted((ROOT / "scripts").glob("qi_*.py")),
)
TARGETS = ("gororoba_quantum/*.py", "kaggle_kernel/*.py", "scripts/qi_*.py", "scripts/qd_platform.py")


def local_module(name: str, importer: Path) -> Path | None:
    for directory in (importer.parent, *SEARCH):
        for candidate in (directory / f"{name}.py", directory / name / "__init__.py"):
            if candidate.is_file():
                return candidate
    return None


IMPORT = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", re.MULTILINE)
# A handler whose first type is followed by a comma; the AST check below confirms each candidate.
CANDIDATE = re.compile(r"^\s*except\s+[\w.]+\s*,", re.MULTILINE)


def closure() -> dict[Path, str]:
    """The source of every repository module a root imports, found by a line scan of its import statements."""
    seen: dict[Path, str] = {}
    pending = list(ROOTS)
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen[path] = path.read_text(encoding="utf-8")
        for name in set(IMPORT.findall(seen[path])):
            found = local_module(name, path)
            if found is not None:
                pending.append(found)
    return seen


def unparenthesized_handlers(source: str) -> list[int]:
    """Line numbers of ``except A, B:`` handlers: a tuple type whose source text does not open with a parenthesis."""
    lines: list[int] = []
    if not CANDIDATE.search(source):
        return lines
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Tuple):
            text = ast.get_source_segment(source, node.type) or ""
            if not text.startswith("("):
                lines.append(node.lineno)
    return lines


def test_the_detector_flags_a_pep_758_handler_and_passes_the_parenthesized_one() -> None:
    bare = "try:\n    pass\nexcept OSError, ValueError:\n    pass\n"
    if unparenthesized_handlers(bare) != [3]:
        raise AssertionError(unparenthesized_handlers(bare))
    for source in (bare.replace("OSError, ValueError", "(OSError, ValueError)"), bare.replace("OSError, ", "")):
        if unparenthesized_handlers(source):
            raise AssertionError(source)


def test_modules_a_python_313_interpreter_imports_parenthesize_multi_type_handlers() -> None:
    found = {
        path.relative_to(ROOT).as_posix(): lines
        for path, source in closure().items()
        if (lines := unparenthesized_handlers(source))
    }
    if found:
        raise AssertionError(f"except A, B: needs Python 3.14; write except (A, B): in {found}")


def test_pyproject_keeps_those_modules_at_the_py313_format_target() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    targets = config["tool"]["ruff"]["per-file-target-version"]
    missing = [pattern for pattern in TARGETS if targets.get(pattern) != "py313"]
    if missing:
        raise AssertionError(f"pyproject.toml [tool.ruff.per-file-target-version] lacks py313 for {missing}")
