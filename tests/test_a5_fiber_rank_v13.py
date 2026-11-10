"""Fiber-rank engine v13 builds the export with slimgb; the reduced basis of a global ordering is unique, so its
export files and rank fields equal engine v12's, which builds them with std."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EVIDENCE = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers"
sys.path.insert(0, str(EVIDENCE / "engine-v12"))

import compare_rank_fields  # noqa: E402

ENGINE_DIR = EVIDENCE / "replay" / "engine"
SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")
PURE = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^3-t2*t3^2,t2^3-t1^2*t3;\nideal G=t1^2,t2^2,t1*t2;\n"
MIXED = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^4-t2^4,t3^3-t1^2*t2^2;\nideal G=t1+t2,t1-t2,t3^2;\n"


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _run(engine: str, header: Path, d: int, n: int, export: Path) -> dict:
    res = subprocess.run(
        [
            sys.executable,
            str(ENGINE_DIR / engine),
            str(header),
            str(d),
            str(n),
            "--quotient",
            "--export-dir",
            str(export),
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SINGULAR": str(SINGULAR)},
    )
    if res.returncode:
        raise RuntimeError(res.stderr)
    return json.loads(res.stdout)


@needs_singular
@pytest.mark.parametrize(("text", "d", "n"), [(PURE, 3, 9), (MIXED, 3, 7)])
def test_slimgb_export_equals_std_export(tmp_path: Path, text: str, d: int, n: int) -> None:
    header = tmp_path / "h.sing"
    header.write_text(text)
    old = _run("fiber_rank_v12.py", header, d, n, tmp_path / "v12")
    new = _run("fiber_rank_v13.py", header, d, n, tmp_path / "v13")
    tables = sorted(p.name for p in (tmp_path / "v12").glob("*.txt"))
    _check("s.txt" in tables and "qB.txt" in tables)
    for name in tables:
        _check((tmp_path / "v12" / name).read_bytes() == (tmp_path / "v13" / name).read_bytes())
    _check(compare_rank_fields.rank_fields(old, True) == compare_rank_fields.rank_fields(new, True))
