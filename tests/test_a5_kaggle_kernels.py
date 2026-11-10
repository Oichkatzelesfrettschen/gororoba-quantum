"""The A_5 Kaggle kernels: the committed kernels equal their generators' output, and a kernel reports failure for a
nonzero exit, a deadline, a zero-exit run without a result, or a missing output."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
VB = ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "vb-export-levers" / "kaggle"
CHAR0 = ROOT / "docs" / "evidence" / "a5-char0-transfer" / "kaggle"


def _load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


@pytest.mark.parametrize("directory", [VB, CHAR0], ids=["vb", "char0"])
def test_committed_kernels_equal_generator_output(tmp_path: Path, directory: Path) -> None:
    generator = _load(directory / "make_kernels.py", f"make_kernels_{directory.parent.name}")
    generator.main(tmp_path)
    for produced in sorted(tmp_path.rglob("*")):
        if produced.is_file():
            committed = directory / produced.relative_to(tmp_path)
            _check(committed.read_bytes() == produced.read_bytes())


def test_vb_runner_failures() -> None:
    runner = _load(VB / "runner.py", "vb_kaggle_runner")
    ok = {"rc": 0, "results": ["RESULT ms 1"], "sha256": {"s.txt": "a", "kbase.txt": "b"}}
    jobs = {
        "ok": ok,
        "nonzero": {**ok, "rc": 3},
        "deadline": {**ok, "rc": 124},
        "zero_exit_no_result": {**ok, "results": []},
        "missing_output": {**ok, "sha256": {"kbase.txt": "b"}},
    }
    _check(runner.failures(jobs) == ["nonzero", "deadline", "zero_exit_no_result", "missing_output"])


def test_char0_runner_failed() -> None:
    runner = _load(CHAR0 / "runner.py", "char0_kaggle_runner")
    _check(not runner.failed(0, {"verdict": "survives"}))
    _check(runner.failed(1, {"verdict": "survives"}))
    _check(runner.failed(0, None))
    _check(runner.failed(0, {"slug": "xm-nm"}))
