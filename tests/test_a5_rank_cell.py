# ruff: noqa: S101
"""Atomic fiber-rank cell publication and validation."""

from __future__ import annotations

import contextlib
import errno
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

HAS_PROC = Path("/proc/self/stat").exists()
RUNNER = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine/rank_cell.py"
SPEC = importlib.util.spec_from_file_location("a5_rank_cell_test", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {RUNNER}")
rank_cell = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rank_cell
SPEC.loader.exec_module(rank_cell)


def _check_equal(left: object, right: object) -> None:
    assert left == right


def _check_unequal(left: object, right: object) -> None:
    assert left != right


def _engine(path: Path, exit_code: int = 0, child_pids: Path | None = None) -> None:
    """A stand-in engine that prints a valid record; with `child_pids` it first leaves a `sleep` child in its process
    group, records the child's pid there and exits without waiting."""
    path.write_text(
        """import hashlib,json,subprocess,sys
from pathlib import Path
if CHILD:
    child=subprocess.Popen(['sleep','60'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    Path(CHILD).write_text(str(child.pid))
engine,header,d,N=Path(sys.argv[0]),Path(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
p=int(header.read_text().split('ring r=',1)[1].split(',',1)[0])
print(json.dumps({'check':'fiber-rank-linear-algebra','engine_sha256_16':hashlib.sha256(engine.read_bytes()).hexdigest()[:16],
'header_sha256_16':hashlib.sha256(header.read_bytes()).hexdigest()[:16],'prime':p,'d':d,'N':N,'r_N':7}))
raise SystemExit(EXIT)
""".replace("EXIT", str(exit_code)).replace("CHILD", repr(None if child_pids is None else str(child_pids)))
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
        returncode = 0

    original_is_dir = rank_cell.Path.is_dir
    monkeypatch.setattr(rank_cell.Path, "is_dir", lambda path: False if str(path) == "/proc" else original_is_dir(path))
    monkeypatch.setattr(rank_cell.shutil, "which", lambda command: "/bin/ps" if command == "ps" else None)
    monkeypatch.setattr(rank_cell.subprocess, "run", lambda *args, **kwargs: Snapshot())

    assert rank_cell.process_group_rss(42) == (500 * 1024, 2)


def test_process_group_liveness_uses_posix_signals_even_when_rss_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, int]] = []
    monkeypatch.setattr(rank_cell.os, "killpg", lambda pgid, number: calls.append((pgid, number)))
    assert rank_cell.process_group_alive(42)
    assert calls == [(42, 0)]

    def missing_group(pgid: int, number: int) -> None:
        raise ProcessLookupError

    monkeypatch.setattr(rank_cell.os, "killpg", missing_group)
    assert not rank_cell.process_group_alive(42)

    def denied_group(pgid: int, number: int) -> None:
        raise PermissionError

    monkeypatch.setattr(rank_cell.os, "killpg", denied_group)
    assert rank_cell.process_group_alive(42)


@pytest.mark.parametrize("mode", ["missing", "failure", "empty", "malformed"])
def test_a_missing_or_failed_ps_sample_is_unknown(monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    class Snapshot:
        stdout = "bad row" if mode == "malformed" else ""
        returncode = 1 if mode == "failure" else 0

    original_is_dir = rank_cell.Path.is_dir
    monkeypatch.setattr(rank_cell.Path, "is_dir", lambda path: False if str(path) == "/proc" else original_is_dir(path))
    monkeypatch.setattr(rank_cell.shutil, "which", lambda _command: None if mode == "missing" else "/bin/ps")
    monkeypatch.setattr(rank_cell.subprocess, "run", lambda *args, **kwargs: Snapshot())
    assert rank_cell.process_group_rss(42) == (None, None)


def test_resource_record_labels_the_polling_statistic(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    assert rank_cell.run_cell(args) == 0
    resources = json.loads(output.with_suffix(".resources.json").read_text())
    assert resources["rss_poll_seconds"] == args.poll_seconds
    assert resources["max_sampled_process_group_rss_bytes"] >= 0
    assert "max_process_group_rss_bytes" not in resources


@pytest.mark.parametrize("alive", [False, True])
def test_finished_engine_cleanup_uses_liveness_when_rss_is_unknown(
    monkeypatch: pytest.MonkeyPatch, alive: bool
) -> None:
    class Finished:
        pid = 42

        def poll(self) -> int:
            return 0

    stopped: list[int] = []
    monkeypatch.setattr(rank_cell, "process_group_rss", lambda _pgid: (None, None))
    monkeypatch.setattr(rank_cell, "process_group_alive", lambda _pgid: alive)
    monkeypatch.setattr(rank_cell, "stop_group", lambda process, _grace: stopped.append(process.pid))
    result = rank_cell.supervise(Finished(), Namespace(grace_seconds=0.01), [], time.time())
    assert stopped == ([42] if alive else [])
    assert result == ("exited", 0, 0, 1)


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


def test_option_order_matters_only_among_repeated_options() -> None:
    root = rank_cell.repository_root()
    digest = rank_cell.engine_arguments_digest
    _check_equal(
        digest(["--chunk", "4", "--echelon", "compact"], root), digest(["--echelon", "compact", "--chunk", "4"], root)
    )
    # argparse keeps the last of a repeated option, so these two invocations run different engines.
    _check_unequal(digest(["--chunk", "3", "--chunk", "4"], root), digest(["--chunk", "4", "--chunk", "3"], root))
    _check_unequal(digest(["--chunk", "4"], root), digest(["--chunk", "5"], root))
    _check_unequal(digest(["--chunk=3", "--chunk=4"], root), digest(["--chunk=4", "--chunk=3"], root))


def test_receipts_of_one_basename_bind_by_their_contents(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    one, other = tmp_path / "one", tmp_path / "other"
    one.mkdir()
    other.mkdir()
    (one / "receipt.json").write_text('{"rank": 1}\n')
    (other / "receipt.json").write_text('{"rank": 2}\n')
    digest = rank_cell.engine_arguments_digest
    first = digest(["--k2-receipt", str(one / "receipt.json")], root)
    _check_unequal(first, digest(["--k2-receipt", str(other / "receipt.json")], root))
    _check_unequal(first, digest([f"--k2-receipt={other / 'receipt.json'}"], root))
    (other / "receipt.json").write_text('{"rank": 1}\n')
    _check_equal(first, digest(["--k2-receipt", str(other / "receipt.json")], root))


def test_one_file_reached_through_two_absolute_paths_binds_equally(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    (tmp_path / "real").mkdir()
    target = tmp_path / "real" / "receipt.json"
    target.write_text('{"rank": 1}\n')
    (tmp_path / "alias.json").symlink_to(target)
    detour = tmp_path / "real" / ".." / "real" / "receipt.json"
    digest = rank_cell.engine_arguments_digest
    base = digest(["--k2-receipt", str(target)], root)
    _check_equal(base, digest(["--k2-receipt", str(tmp_path / "alias.json")], root))
    _check_equal(base, digest(["--k2-receipt", str(detour)], root))


def test_unreadable_paths_bind_by_the_hash_of_their_text(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    one = rank_cell.argument_identity(str(tmp_path / "missing.json"), root)
    other = rank_cell.argument_identity(str(tmp_path / "elsewhere.json"), root)
    assert one.startswith("text-sha256:") and one != other and str(tmp_path) not in one
    assert rank_cell.argument_identity("64", root) == "64"
    assert rank_cell.argument_identity("--chunk", root) == "--chunk"


def test_paths_inside_the_checkout_stay_repository_relative() -> None:
    root = rank_cell.repository_root()
    assert root is not None
    inside = str(root / "docs" / "a.json")
    assert rank_cell.argument_identity(inside, root) == "docs/a.json"
    assert rank_cell.argument_identity(f"--k2-receipt={inside}", root) == "--k2-receipt=docs/a.json"
    assert rank_cell.engine_arguments_digest([inside], root) == rank_cell.engine_arguments_digest(["docs/a.json"], root)


def test_skip_is_refused_when_an_external_receipt_changes(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    receipt = tmp_path / "elsewhere" / "receipt.json"
    receipt.parent.mkdir()
    receipt.write_text('{"rank": 1}\n')
    args = _args(tmp_path, engine, output)
    args.engine_args = ["--k2-receipt", str(receipt)]
    assert rank_cell.run_cell(args) == 0
    assert rank_cell.run_cell(args) == 0
    receipt.write_text('{"rank": 2}\n')
    with pytest.raises(ValueError, match="engine arguments differ"):
        rank_cell.run_cell(args)


def test_missing_interpreter_writes_a_resource_record_and_exits_127(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    args.python = str(tmp_path / "no-such-python")
    assert rank_cell.run_cell(args) == 127
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert (record["termination"], record["engine_exit"], record["runner_exit"]) == ("launch_error", None, 127)
    assert record["launch_error"].startswith("FileNotFoundError: errno 2")
    assert str(tmp_path) not in output.with_suffix(".resources.json").read_text()
    assert "cannot launch the engine" in output.with_suffix(".err").read_text()
    assert output.with_suffix(".json.part").exists() and not output.exists()


def test_unexecutable_interpreter_exits_126(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    plain = tmp_path / "plain-file"
    plain.write_text("not a program\n")
    plain.chmod(0o644)
    args.python = str(plain)
    assert rank_cell.run_cell(args) == 126
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert (record["termination"], record["runner_exit"]) == ("launch_error", 126)
    assert record["launch_error"].startswith("PermissionError: errno 13")
    assert not output.exists()


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
    """True while `pid` runs; a zombie counts as gone. procfs where it exists, `ps` elsewhere (macOS has no /proc)."""
    if HAS_PROC:
        try:
            return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
        except FileNotFoundError, ProcessLookupError:
            return False
    state = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False)  # noqa: S607
    return bool(state.stdout.strip()) and not state.stdout.strip().startswith("Z")


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


@pytest.mark.skipif(not HAS_PROC, reason="the ESRCH skip belongs to the /proc scan; the ps path has no such read")
def test_process_group_rss_skips_a_member_that_exits_during_the_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    """procfs raises ESRCH on a read of a process that exited after the directory listing named it."""
    own = f"/proc/{os.getpid()}/stat"
    original_read_text = rank_cell.Path.read_text
    refused: list[str] = []

    def read_text(path: Path, *args: object, **kwargs: object) -> str:
        if str(path) == own:
            refused.append(own)
            raise ProcessLookupError(errno.ESRCH, "No such process")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(rank_cell.Path, "read_text", read_text)
    resident, count = rank_cell.process_group_rss(os.getpgid(0))

    assert refused == [own]
    assert resident >= 0
    assert count >= 0


def test_option_value_paths_in_the_resource_record_are_portable(tmp_path: Path) -> None:
    root = rank_cell.repository_root()
    assert root is not None
    inside = str(root / "docs" / "r.json")
    assert rank_cell.portable_path(f"--k2-receipt={inside}", root) == "--k2-receipt=docs/r.json"
    assert rank_cell.portable_path(f"--k2-receipt={tmp_path / 'r.json'}", root) == "--k2-receipt=r.json"
    assert rank_cell.portable_path("--chunk=64", root) == "--chunk=64"
    assert rank_cell.portable_path("--max-gb", root) == "--max-gb"
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    args.engine_args = [f"--k2-receipt={tmp_path / 'elsewhere' / 'receipt.json'}", "--chunk=64"]
    assert rank_cell.run_cell(args) == 0
    text = output.with_suffix(".resources.json").read_text()
    assert str(tmp_path) not in text
    assert json.loads(text)["command"][-2:] == ["--k2-receipt=receipt.json", "--chunk=64"]


def test_a_file_named_without_a_slash_binds_by_its_contents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--k2-receipt receipt.json` run from the receipt's directory names a file as surely as an absolute path."""
    monkeypatch.chdir(tmp_path)
    receipt = tmp_path / "receipt.json"
    receipt.write_text('{"rank": 1}\n')
    root = rank_cell.repository_root()
    digest = rank_cell.engine_arguments_digest
    separate, joined = ["--k2-receipt", "receipt.json"], ["--k2-receipt=receipt.json"]
    first_separate, first_joined = digest(separate, root), digest(joined, root)
    _check_equal(first_separate, digest(["--k2-receipt", str(receipt)], root))
    receipt.write_text('{"rank": 2}\n')
    _check_unequal(first_separate, digest(separate, root))
    _check_unequal(first_joined, digest(joined, root))
    assert rank_cell.argument_identity("receipt.json", root).startswith("file-sha256:")
    assert rank_cell.argument_identity("--receipt=receipt.json", root).startswith("--receipt=file-sha256:")
    assert rank_cell.argument_identity("64", root) == "64"
    assert rank_cell.argument_identity("--chunk", root) == "--chunk"
    assert rank_cell.argument_identity("absent.json", root) == "absent.json"


def test_skip_is_refused_when_a_receipt_named_without_a_slash_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    receipt = tmp_path / "receipt.json"
    receipt.write_text('{"rank": 1}\n')
    monkeypatch.chdir(tmp_path)
    args = _args(tmp_path, engine, output)
    args.engine_args = ["--k2-receipt", "receipt.json"]
    assert rank_cell.run_cell(args) == 0
    assert rank_cell.run_cell(args) == 0
    receipt.write_text('{"rank": 2}\n')
    with pytest.raises(ValueError, match="engine arguments differ"):
        rank_cell.run_cell(args)


@pytest.mark.parametrize("exit_code", [0, 3])
def test_a_group_member_that_outlives_the_engine_is_terminated(tmp_path: Path, exit_code: int) -> None:
    """The stand-in engine leaves a `sleep 60` in its process group and exits; the runner returns only after it is
    gone, whether the engine succeeded or failed."""
    engine, output, child_file = tmp_path / "engine.py", tmp_path / "cell.json", tmp_path / "child"
    _engine(engine, exit_code, child_file)
    args = _args(tmp_path, engine, output)
    try:
        assert rank_cell.run_cell(args) == exit_code
        child = int(child_file.read_text())
        assert not _alive(child)
    finally:
        if child_file.exists():
            with contextlib.suppress(ProcessLookupError):
                os.kill(int(child_file.read_text()), signal.SIGKILL)
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert (record["termination"], record["engine_exit"], record["runner_exit"]) == ("exited", exit_code, exit_code)


def test_one_existing_file_binds_equally_through_every_spelling_inside_the_checkout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = rank_cell.repository_root()
    assert root is not None
    monkeypatch.chdir(root / "gororoba_quantum")
    identities = {
        rank_cell.argument_identity(token, root)
        for token in ("parallel.py", "./parallel.py", str(root / "gororoba_quantum" / "parallel.py"))
    }
    assert len(identities) == 1 and identities.pop().startswith("file-sha256:")
    assert rank_cell.argument_identity("--k2-receipt=parallel.py", root).startswith("--k2-receipt=file-sha256:")


def test_a_second_invocation_for_a_locked_output_touches_no_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    lock = tmp_path / "cell.json.lock"
    holder = rank_cell.acquire_output_lock(lock)
    assert holder is not None
    try:
        assert rank_cell.acquire_output_lock(lock) is None
        assert rank_cell.run_cell(args) == rank_cell.LOCKED_STATUS == 75
        assert "another invocation holds cell.json.lock" in capsys.readouterr().err
        assert sorted(path.name for path in tmp_path.iterdir()) == ["cell.json.lock", "engine.py", "header.sing"]
    finally:
        rank_cell.release_output_lock(holder, lock)
    assert not lock.exists()
    assert rank_cell.run_cell(args) == 0
    assert not lock.exists() and output.exists()


def test_the_lock_is_released_when_validation_of_an_existing_record_raises(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    output.write_text("{}\n")
    with pytest.raises(ValueError, match="identity mismatch"):
        rank_cell.run_cell(_args(tmp_path, engine, output))
    assert not (tmp_path / "cell.json.lock").exists()


@pytest.mark.parametrize("text", ["[]", "null", "3", '"record"'])
def test_a_json_value_that_is_not_an_object_is_a_validation_error(tmp_path: Path, text: str) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    identity = rank_cell.expected_identity(engine.resolve(), Path(args.header).resolve(), args.degree, args.order)
    output.write_text(text + "\n")
    with pytest.raises(ValueError, match="not a JSON object"):
        rank_cell.validate_record(output, identity)
    with pytest.raises(ValueError, match="not a JSON object"):
        rank_cell.run_cell(args)
    resources = tmp_path / "cell.resources.json"
    output.write_text('{"r_N": 1}\n')
    resources.write_text(text + "\n")
    with pytest.raises(ValueError, match="not a JSON object"):
        rank_cell.validate_arguments_binding(resources, output, "0" * 16)


@pytest.mark.parametrize("text", ["[]", "null"])
def test_an_engine_that_prints_a_non_object_fails_validation_and_keeps_its_records(tmp_path: Path, text: str) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    engine.write_text(f"print({text!r})\n")
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 2
    record = json.loads(output.with_suffix(".resources.json").read_text())
    assert record["runner_exit"] == 2 and "not a JSON object" in record["validation_error"]
    assert not output.exists() and output.with_suffix(".json.part").exists()
