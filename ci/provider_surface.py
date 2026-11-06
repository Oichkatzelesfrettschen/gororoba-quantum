"""The names the repository's code imports from each pinned provider library.

requirements.txt and ci/requirements-ci.txt pin the libraries in PINNED. surface() parses every Python file under
gororoba_quantum/, scripts/ and ci/ that mentions one of them and collects `from MODULE import NAME`, `import MODULE`
and attribute chains on an imported module (`pcvl.BS.Rx`, `qiskit.qpy.dump`), at module level and inside functions.
tests/providers/test_surface.py resolves each name under the installed versions.
"""

from __future__ import annotations

import ast
import functools
from collections import defaultdict
from pathlib import Path

import parallel

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ("gororoba_quantum", "scripts", "ci")
PINNED = ("qiskit", "qiskit_aer", "qiskit_ibm_runtime", "samplomatic", "perceval", "exqalibur", "mcp")
# Files that run under another provider's venv and import a name the repository pins cannot resolve. A file run
# under another venv whose imports the pins do resolve stays in the scan.
FOREIGN = {
    "scripts/oq_mcp_server.py": "runs under OQ_PYTHON; the vendor openquantum_mcp package requires mcp<2",
}

Use = tuple[str, str, str, str]  # package, module, dotted name ("" for the module itself), file


def file_uses(name: str) -> list[Use]:
    """The pinned-provider names one repository file uses."""
    source = (ROOT / name).read_bytes()
    if not any(package.encode() in source for package in PINNED):
        return []
    tree = ast.parse(source, filename=name)
    uses: list[Use] = []
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.partition(".")[0]
                if top in PINNED:
                    uses.append((top, alias.name, "", name))
                    aliases[alias.asname or top] = alias.name if alias.asname else top
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top = node.module.partition(".")[0]
            if top in PINNED:
                uses += [(top, node.module, alias.name, name) for alias in node.names]
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
            uses.append((module.partition(".")[0], module, ".".join(reversed(chain)), name))
    return uses


@functools.cache
def surface() -> dict[str, dict[tuple[str, str], set[str]]]:
    """Package -> (module, dotted name or "") -> the files that use it."""
    names = [
        path.relative_to(ROOT).as_posix()
        for directory in DIRECTORIES
        for path in sorted((ROOT / directory).rglob("*.py"))
        if path.relative_to(ROOT).as_posix() not in FOREIGN
    ]
    found: dict[str, dict[tuple[str, str], set[str]]] = {package: defaultdict(set) for package in PINNED}
    for per_file in parallel.ordered_map(file_uses, names):
        for package, module, dotted, name in per_file:
            found[package][(module, dotted)].add(name)
    return found
