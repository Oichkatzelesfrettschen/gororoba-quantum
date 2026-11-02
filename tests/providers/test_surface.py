"""Every provider-library name the repository's code imports resolves under the pinned versions.

The scan reads gororoba_quantum/, scripts/ and ci/ when the test runs, so a new import joins the surface without an
edit here. It collects `from MODULE import NAME`, `import MODULE` and attribute chains on an imported module
(`pcvl.BS.Rx`, `qiskit.qpy.dump`), at module level and inside functions. requirements.txt and
ci/requirements-ci.txt pin the libraries in PINNED; a version bump that renames or removes any name the code
reaches fails here before a script meets it on a host.
"""

from __future__ import annotations

import ast
import functools
import importlib
from collections import defaultdict
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
PINNED = ("qiskit", "qiskit_aer", "qiskit_ibm_runtime", "samplomatic", "perceval", "exqalibur", "mcp")
# Files that run under another provider's venv and import a name the repository pins cannot resolve. A file run
# under another venv whose imports the pins do resolve stays in the scan.
FOREIGN = {
    "scripts/oq_mcp_server.py": "runs under OQ_PYTHON; the vendor openquantum_mcp package requires mcp<2",
}


@functools.cache
def surface() -> dict[str, dict[tuple[str, str], set[str]]]:
    """Package -> (module, dotted name or "") -> the files that use it."""
    found: dict[str, dict[tuple[str, str], set[str]]] = {package: defaultdict(set) for package in PINNED}
    for directory in ("gororoba_quantum", "scripts", "ci"):
        for path in sorted((ROOT / directory).rglob("*.py")):
            name = path.relative_to(ROOT).as_posix()
            source = path.read_bytes()
            if name in FOREIGN or not any(package.encode() in source for package in PINNED):
                continue
            tree = ast.parse(source, filename=name)
            aliases: dict[str, str] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.partition(".")[0]
                        if top in found:
                            found[top][(alias.name, "")].add(name)
                            aliases[alias.asname or top] = alias.name if alias.asname else top
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    top = node.module.partition(".")[0]
                    if top in found:
                        for alias in node.names:
                            found[top][(node.module, alias.name)].add(name)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Attribute) or isinstance(node.ctx, ast.Store):
                    continue
                chain = []
                value: ast.expr = node
                while isinstance(value, ast.Attribute):
                    chain.append(value.attr)
                    value = value.value
                if isinstance(value, ast.Name) and value.id in aliases:
                    module = aliases[value.id]
                    found[module.partition(".")[0]][(module, ".".join(reversed(chain)))].add(name)
    return found


def resolve(module: str, dotted: str) -> object:
    target: object = importlib.import_module(module)
    for part in filter(None, dotted.split(".")):
        try:
            target = getattr(target, part)
        except AttributeError:
            if not isinstance(target, ModuleType):
                raise
            target = importlib.import_module(f"{target.__name__}.{part}")
    return target


# One xdist worker holds every case, so the scan (a few seconds of parsing) runs once.
pytestmark = pytest.mark.xdist_group("provider-surface")


def test_foreign_interpreter_files_exist() -> None:
    missing = [name for name in FOREIGN if not (ROOT / name).is_file()]
    if missing:
        raise AssertionError(f"FOREIGN names files that no longer exist: {missing}")


@pytest.mark.parametrize("package", PINNED)
def test_imported_names_resolve(package: str) -> None:
    uses = surface()[package]
    failures = []
    for (module, dotted), files in sorted(uses.items()):
        try:
            resolve(module, dotted)
        except (ImportError, AttributeError) as error:
            failures.append(f"{module}:{dotted or '*'} ({sorted(files)[0]}): {type(error).__name__}: {error}")
    if failures:
        raise AssertionError(f"{len(failures)} of {len(uses)} {package} names fail:\n" + "\n".join(failures))
