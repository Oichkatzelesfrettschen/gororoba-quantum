"""Fiber-rank engine v12: the echelon backend selects flint or the CUDA device and leaves every rank field unchanged."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import modular_echelon

EVIDENCE = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers"
sys.path.insert(0, str(EVIDENCE / "engine-v12"))

import compare_rank_fields  # noqa: E402

ENGINE_DIR = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "replay" / "engine"

SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")
needs_gpu = pytest.mark.skipif(not modular_echelon.gpu_available(), reason="no CUDA device with torch and CuPy")
# G = (t1^2, t2^2, t1*t2) satisfies y1*y2 - y3^2 = 0 as polynomials, so that quadric holds in J + m * P_2.
PURE = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^3-t2*t3^2,t2^3-t1^2*t3;\nideal G=t1^2,t2^2,t1*t2;\n"
MIXED = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^4-t2^4,t3^3-t1^2*t2^2;\nideal G=t1+t2,t1-t2,t3^2;\n"


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _run(engine: str, header: Path, d: int, n: int, *extra: str) -> dict:
    res = subprocess.run(
        [sys.executable, str(ENGINE_DIR / engine), str(header), str(d), str(n), "--quotient", *extra],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SINGULAR": str(SINGULAR)},
    )
    if res.returncode:
        raise RuntimeError(res.stderr)
    return json.loads(res.stdout)


def _rank_fields(rec: dict, across_engines: bool = False) -> str:
    return compare_rank_fields.rank_fields(rec, across_engines)


@needs_singular
@pytest.mark.parametrize(("text", "d", "n"), [(PURE, 3, 9), (MIXED, 3, 7)])
def test_flint_echelon_record_equals_engine_v11(tmp_path: Path, text: str, d: int, n: int) -> None:
    header = tmp_path / "h.sing"
    header.write_text(text)
    old = _run("fiber_rank_v11.py", header, d, n, "--chunk", "7")
    new = _run("fiber_rank_v12.py", header, d, n, "--chunk", "7")
    _check(new["echelon"] == "flint" and _rank_fields(old, True) == _rank_fields(new, True))


@needs_singular
@needs_gpu
@pytest.mark.parametrize(("text", "d", "n"), [(PURE, 3, 9), (MIXED, 3, 7)])
def test_gpu_echelon_record_equals_flint_echelon(tmp_path: Path, text: str, d: int, n: int) -> None:
    header = tmp_path / "h.sing"
    header.write_text(text)
    flint_rec = _run("fiber_rank_v12.py", header, d, n, "--chunk", "7", "--echelon", "flint")
    gpu_rec = _run("fiber_rank_v12.py", header, d, n, "--chunk", "7", "--echelon", "gpu")
    _check(gpu_rec["echelon"] == "gpu" and _rank_fields(flint_rec) == _rank_fields(gpu_rec))
