"""The A_5 Kaggle kernels: the committed kernels equal their generators' output, and a kernel reports failure for a
nonzero exit, a deadline, a zero-exit run without a result, or a missing output."""

import importlib.util
import os
import subprocess
import sys
import time
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


def test_char0_runner_orders_its_limits(tmp_path: Path) -> None:
    runner = _load(CHAR0 / "runner.py", "char0_kaggle_runner_limits")
    _check(runner.driver_args(["d.py", "--slug", "w8-nm", "--timeout", "41000"], 123)[-1] == "123")
    _check(runner.driver_args(["d.py"], 123) == ["d.py"])
    # The driver's limit, the outer timeout and the Kaggle run-time limit fire in that order.
    _check(0 < runner.DRIVER_MARGIN and 0 < runner.STOP_MARGIN and runner.SESSION_SECONDS == 41400)
    log = tmp_path / "singular.log"
    _check(runner.last_line(log) == "")
    log.write_text("STAGE product 3 of 300 17\n\n")
    _check(runner.last_line(log) == "STAGE product 3 of 300 17")


def test_char0_shim_keeps_output_of_a_killed_singular(tmp_path: Path) -> None:
    runner = _load(CHAR0 / "runner.py", "char0_kaggle_runner_shim")
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "Singular").write_text("#!/bin/bash\necho STAGE one\necho warning text >&2\nkill -KILL $$\n")
    (fake / "Singular").chmod(0o755)
    (tmp_path / "systemd-run").write_text(runner.shim(tmp_path))
    (tmp_path / "systemd-run").chmod(0o755)
    env = dict(os.environ, PATH=f"{fake}:{os.environ['PATH']}")
    command = [str(tmp_path / "systemd-run"), "--user", "--scope", "Singular", "-q"]
    done = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    _check(done.returncode == -9)
    # The tee processes outlive the killed command by the time they need to drain their pipes.
    for name, text in (("singular.log", "STAGE one"), ("singular.stderr.log", "warning text")):
        deadline = time.time() + 10
        while time.time() < deadline and text not in (tmp_path / name).read_text():
            time.sleep(0.05)
        _check(text in (tmp_path / name).read_text())


def test_char0_setup_commands_keep_their_output(tmp_path: Path) -> None:
    runner = _load(CHAR0 / "runner.py", "char0_kaggle_runner_setup")
    log = tmp_path / "setup.log"
    runner.run_logged(["sh", "-c", "echo fetched; echo refused >&2"], log)
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_logged(["sh", "-c", "echo broke >&2; exit 3"], log)
    text = log.read_text()
    _check(all(part in text for part in ("fetched", "refused", "broke", "+ sh -c")))
