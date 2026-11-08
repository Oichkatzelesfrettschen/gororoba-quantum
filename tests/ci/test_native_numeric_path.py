"""Every lane, gate, workflow and record writer computes on its CPU's native numeric path.

numpy and OpenBLAS select their kernels from the CPU; a forced OpenBLAS core or a numpy dispatch mask gives no
single path across CPUs (with numpy 2.5.4 the forced Haswell core segfaults in dgemm on AMD EPYC 9V74 runners) and
hides the path a record was written on (docs/design/native-numeric-replay.md, ci/AGENTS.md). This module fails when
a workflow, the pins-venv action or a script under ci/, scripts/, kaggle_kernel/ or gororoba_quantum/ assigns
OPENBLAS_CORETYPE or NPY_DISABLE_CPU_FEATURES. scripts/numerics_fingerprint.py measures those configurations on
purpose, in child processes it starts, and stays allowed.
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPS = ("OPENBLAS_CORETYPE", "NPY_DISABLE_CPU_FEATURES")
SCANNED = (".github", "ci", "scripts", "kaggle_kernel", "gororoba_quantum")
ALLOWED = {"scripts/numerics_fingerprint.py"}
# A shell or YAML assignment: `NAME=value`, `export NAME=value` or the YAML mapping `NAME: value`.
TEXT_ASSIGNMENT = re.compile(r"(?:^|[\s;'\"])(?:export\s+)?(" + "|".join(CAPS) + r")\s*(?:=|:\s*\S)", re.MULTILINE)


def python_assignments(source: str) -> list[int]:
    """Lines of a Python module that put a cap into an environment: a dict literal keyed by it, a subscript store,
    or setdefault, putenv or update with it as the key."""
    lines = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Dict):
            keys = [key for key in node.keys if isinstance(key, ast.Constant)]
            lines += [key.lineno for key in keys if key.value in CAPS]
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store):
            if isinstance(node.slice, ast.Constant) and node.slice.value in CAPS:
                lines.append(node.lineno)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"setdefault", "putenv"} and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value in CAPS:
                    lines.append(node.lineno)
            elif node.func.attr == "update":
                lines += [k.lineno for k in node.keywords if k.arg in CAPS]
    return lines


def cap_assignments(root: Path = ROOT) -> list[str]:
    tracked = subprocess.run(
        ["git", "ls-files", "--", *SCANNED], cwd=root, capture_output=True, text=True, check=True
    ).stdout.split()
    found = []
    for name in tracked:
        if name in ALLOWED:
            continue
        path = root / name
        if name.endswith(".py"):
            found += [f"{name}:{line}" for line in python_assignments(path.read_text(encoding="utf-8"))]
        elif name.endswith((".sh", ".yml", ".yaml")):
            text = path.read_text(encoding="utf-8")
            found += [f"{name}:{text.count(chr(10), 0, m.start()) + 1}" for m in TEXT_ASSIGNMENT.finditer(text)]
    return found


def test_no_lane_forces_a_kernel_or_masks_dispatch() -> None:
    found = cap_assignments()
    if found:
        raise AssertionError("these sites set a numeric cap; compute on the native path instead:\n" + "\n".join(found))


def test_the_scan_catches_each_assignment_form(tmp_path: Path) -> None:
    python_forms = [
        'env = {"OPENBLAS_CORETYPE": "Haswell"}',
        'os.environ["NPY_DISABLE_CPU_FEATURES"] = "X86_V4"',
        'environment.setdefault("OPENBLAS_CORETYPE", "Haswell")',
        "os.environ.update(NPY_DISABLE_CPU_FEATURES='X86_V4')",
    ]
    for line in python_forms:
        if not python_assignments(line + "\n"):
            raise AssertionError(f"missed {line!r}")
    for line in (
        "export OPENBLAS_CORETYPE=Haswell",
        "  NPY_DISABLE_CPU_FEATURES: X86_V4",
        "env OPENBLAS_CORETYPE=Haswell cmd",
    ):
        if not TEXT_ASSIGNMENT.search(line):
            raise AssertionError(f"missed {line!r}")
    for line in ('caps = {name: os.environ.get(name) for name in ("OPENBLAS_CORETYPE",)}', "x = 'OPENBLAS_CORETYPE'"):
        if python_assignments(line + "\n"):
            raise AssertionError(f"flagged a read: {line!r}")
    if TEXT_ASSIGNMENT.search("# no lane sets OPENBLAS_CORETYPE or NPY_DISABLE_CPU_FEATURES"):
        raise AssertionError("flagged a comment that names the caps")
