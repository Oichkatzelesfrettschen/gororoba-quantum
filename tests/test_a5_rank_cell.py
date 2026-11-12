# ruff: noqa: S101
"""Atomic fiber-rank cell publication and validation."""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from argparse import Namespace
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

RUNNER = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine/rank_cell.py"
SPEC = importlib.util.spec_from_file_location("a5_rank_cell_test", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {RUNNER}")
rank_cell = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rank_cell
SPEC.loader.exec_module(rank_cell)


def _engine(path: Path, exit_code: int = 0) -> None:
    path.write_text(
        """import hashlib,json,sys
from pathlib import Path
engine,header,d,N=Path(sys.argv[0]),Path(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
p=int(header.read_text().split('ring r=',1)[1].split(',',1)[0])
print(json.dumps({'check':'fiber-rank-linear-algebra','engine_sha256_16':hashlib.sha256(engine.read_bytes()).hexdigest()[:16],
'header_sha256_16':hashlib.sha256(header.read_bytes()).hexdigest()[:16],'prime':p,'d':d,'N':N,'r_N':7}))
raise SystemExit(EXIT)
""".replace("EXIT", str(exit_code))
    )


def _args(tmp_path: Path, engine: Path, output: Path) -> Namespace:
    header = tmp_path / "header.sing"
    header.write_text("ring r=32009,(x),dp; ideal J=x; ideal G=x;\n")
    return Namespace(
        engine=str(engine),
        header=str(header),
        degree=2,
        order=7,
        output=str(output),
        python=sys.executable,
        poll_seconds=0.01,
        timeout=None,
        grace_seconds=0.5,
        engine_args=[],
    )


def test_success_publishes_and_validates_existing_record(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    assert rank_cell.run_cell(args) == 0
    assert output.exists() and not output.with_suffix(".json.part").exists()
    assert output.with_suffix(".resources.json").exists()
    assert rank_cell.run_cell(args) == 0


def test_failure_keeps_partial_record_and_propagates_status(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine, 9)
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 9
    assert not output.exists() and output.with_suffix(".json.part").exists()


def test_nonempty_stale_record_is_not_skipped(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    output.write_text("{}\n")
    with pytest.raises(ValueError, match="identity mismatch"):
        rank_cell.run_cell(args)


def test_process_group_rss_uses_ps_without_proc(monkeypatch: pytest.MonkeyPatch) -> None:
    class Snapshot:
        stdout = " 41 100\n 42 200\n 42 300\nmalformed\n"

    original_is_dir = rank_cell.Path.is_dir
    monkeypatch.setattr(rank_cell.Path, "is_dir", lambda path: False if str(path) == "/proc" else original_is_dir(path))
    monkeypatch.setattr(rank_cell.shutil, "which", lambda command: "/bin/ps" if command == "ps" else None)
    monkeypatch.setattr(rank_cell.subprocess, "run", lambda *args, **kwargs: Snapshot())

    assert rank_cell.process_group_rss(42) == (500 * 1024, 2)


def test_nonzero_status_with_empty_record_fails_validation(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    engine.write_text("print('{}')\n")
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 2
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert record["runner_exit"] == 2 and "identity mismatch" in record["validation_error"]
    assert not output.exists() and output.with_suffix(".json.part").exists()


def test_signal_killed_engine_reports_128_plus_signal(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    engine.write_text("import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n")
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 128 + signal.SIGKILL
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert record["engine_exit"] == -signal.SIGKILL and record["runner_exit"] == 137


def test_engine_arguments_need_a_double_dash() -> None:
    base = ["engine.py", "header.sing", "2", "7", "cell.json"]
    with pytest.raises(SystemExit):
        rank_cell.parse_arguments([*base, "--chunk", "3"])
    args = rank_cell.parse_arguments([*base, "--python", "py", "--timeout", "5", "--", "--chunk", "3"])
    assert (args.python, args.timeout, args.engine_args) == ("py", 5.0, ["--chunk", "3"])


def test_runner_options_after_positionals_stay_with_the_runner() -> None:
    args = rank_cell.parse_arguments(["e", "h", "2", "7", "o", "--poll-seconds", "1", "--", "--poll-seconds", "9"])
    assert (args.poll_seconds, args.engine_args) == (1.0, ["--poll-seconds", "9"])


def test_skip_validation_binds_the_engine_arguments(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    args.engine_args = ["--chunk", "3", "--echelon", "compact"]
    assert rank_cell.run_cell(args) == 0
    args.engine_args = ["--echelon", "compact", "--chunk", "3"]
    assert rank_cell.run_cell(args) == 0
    for other in (["--chunk", "4", "--echelon", "compact"], ["--chunk", "3"], []):
        args.engine_args = other
        with pytest.raises(ValueError, match="engine arguments differ"):
            rank_cell.run_cell(args)


def test_skip_requires_a_resource_record_of_a_successful_run_with_the_same_bytes(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    assert rank_cell.run_cell(args) == 0
    resources = output.with_suffix(".resources.json")
    evidence = json.loads(resources.read_text())
    resources.write_text(json.dumps({**evidence, "runner_exit": 9}))
    with pytest.raises(ValueError, match="successful run"):
        rank_cell.run_cell(args)
    resources.write_text(json.dumps(evidence))
    assert rank_cell.run_cell(args) == 0
    record = json.loads(output.read_text())
    output.write_text(json.dumps({**record, "r_N": record["r_N"] + 1}))
    with pytest.raises(ValueError, match="successful run"):
        rank_cell.run_cell(args)
    resources.unlink()
    with pytest.raises(ValueError, match="engine-argument binding"):
        rank_cell.run_cell(args)


def test_argument_digest_ignores_flag_order_and_checkout_location(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    one = ["--k2-receipt", "/one/place/receipt.json", "--chunk", "4"]
    two = ["--chunk", "4", "--k2-receipt", "/another/place/receipt.json"]
    assert rank_cell.engine_arguments_digest(one, root) == rank_cell.engine_arguments_digest(two, root)
    assert rank_cell.engine_arguments_digest(one, root) != rank_cell.engine_arguments_digest(["--chunk", "5"], root)
    assert root is not None
    inside = [str(root / "a.json")]
    assert rank_cell.engine_arguments_digest(inside, root) == rank_cell.engine_arguments_digest(["a.json"], root)


def test_resource_record_holds_no_local_absolute_path(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 0
    text = output.with_suffix(".resources.json").read_text()
    assert str(tmp_path) not in text and str(Path(sys.executable).parent) not in text
    command = json.loads(text)["command"]
    assert command[:2] == [Path(sys.executable).name, "engine.py"]


def test_portable_path_is_relative_to_the_checkout_or_a_basename(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    assert root is not None
    assert rank_cell.portable_path(str(root / "docs" / "x.sing"), root) == "docs/x.sing"
    assert rank_cell.portable_path(str(tmp_path / "x.sing"), root) == "x.sing"
    assert rank_cell.portable_path("--chunk", root) == "--chunk"


def test_publication_flushes_before_the_rename(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    events: list[tuple[str, str]] = []
    real_replace, real_file, real_directory = os.replace, rank_cell.fsync_path, rank_cell.fsync_directory

    def replace(source: Path, target: Path) -> None:
        events.append(("replace", Path(target).name))
        real_replace(source, target)

    def flush_file(path: Path) -> None:
        events.append(("fsync file", path.name))
        real_file(path)

    def flush_directory(path: Path) -> None:
        events.append(("fsync directory", path.name))
        real_directory(path)

    monkeypatch.setattr(rank_cell.os, "replace", replace)
    monkeypatch.setattr(rank_cell, "fsync_path", flush_file)
    monkeypatch.setattr(rank_cell, "fsync_directory", flush_directory)
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 0
    assert events[-3:] == [
        ("fsync file", "cell.json.part"),
        ("replace", "cell.json"),
        ("fsync directory", tmp_path.name),
    ]


def _stand_in_engine(path: Path, pids: Path, ignore_term: bool) -> None:
    """An engine that spawns a child, records both pids, then idles; optionally it ignores SIGTERM."""
    path.write_text(
        """import os, signal, subprocess, time
if IGNORE:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
child = subprocess.Popen(["sleep", "60"], stdin=subprocess.DEVNULL)
with open(PIDS + ".tmp", "w") as handle:
    handle.write(f"{os.getpid()} {child.pid}")
os.replace(PIDS + ".tmp", PIDS)
for _ in range(1200):
    time.sleep(0.05)
""".replace("IGNORE", str(ignore_term)).replace("PIDS", repr(str(pids)))
    )


Launch = Callable[..., tuple[subprocess.Popen[bytes], Path, list[int]]]


def _alive(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except FileNotFoundError, ProcessLookupError:
        return False


@pytest.fixture
def launch(tmp_path: Path) -> Iterator[Callable[..., tuple[subprocess.Popen[bytes], Path, list[int]]]]:
    """Start the runner on a stand-in engine; teardown kills whatever a failing test leaves running."""
    started: list[tuple[subprocess.Popen[bytes], list[int]]] = []

    def start(ignore_term: bool, *options: str) -> tuple[subprocess.Popen[bytes], Path, list[int]]:
        engine, output, pids = tmp_path / "engine.py", tmp_path / "cell.json", tmp_path / "pids"
        _stand_in_engine(engine, pids, ignore_term)
        header = tmp_path / "header.sing"
        header.write_text("ring r=32009,(x),dp; ideal J=x; ideal G=x;\n")
        runner = subprocess.Popen(
            [sys.executable, str(RUNNER), str(engine), str(header), "2", "7", str(output), *options],
            stdin=subprocess.DEVNULL,
        )
        running: list[int] = []
        started.append((runner, running))
        deadline = time.monotonic() + 20
        while not pids.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert pids.exists(), "the stand-in engine did not start"
        running.extend(int(token) for token in pids.read_text().split())
        return runner, output, running

    yield start
    for runner, running in started:
        runner.kill()
        runner.wait()
        for pid in running:
            with contextlib.suppress(ProcessLookupError):
                os.kill(pid, signal.SIGKILL)


@pytest.mark.parametrize("ignore_term", [False, True])
def test_sigterm_to_the_runner_leaves_no_engine_process(launch: Launch, ignore_term: bool) -> None:
    runner, output, pids = launch(ignore_term, "--grace-seconds", "0.5")
    runner.send_signal(signal.SIGTERM)
    assert runner.wait(timeout=20) == 128 + signal.SIGTERM
    assert not any(_alive(pid) for pid in pids)
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert (record["termination"], record["runner_exit"]) == ("SIGTERM", 143)
    assert not output.exists() and output.with_suffix(".json.part").exists()


def test_sigint_to_the_runner_terminates_the_engine_group(launch: Launch) -> None:
    runner, output, pids = launch(False, "--grace-seconds", "0.5")
    runner.send_signal(signal.SIGINT)
    assert runner.wait(timeout=20) == 128 + signal.SIGINT
    assert not any(_alive(pid) for pid in pids)
    assert json.loads(output.with_suffix(".resources.json").read_text())["termination"] == "SIGINT"


@pytest.mark.parametrize("ignore_term", [False, True])
def test_timeout_exits_124_and_terminates_the_group(launch: Launch, ignore_term: bool) -> None:
    runner, output, pids = launch(ignore_term, "--timeout", "0.5", "--grace-seconds", "0.5")
    assert runner.wait(timeout=20) == 124
    assert not any(_alive(pid) for pid in pids)
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert (record["termination"], record["timeout_seconds"], record["runner_exit"]) == ("timeout", 0.5, 124)
