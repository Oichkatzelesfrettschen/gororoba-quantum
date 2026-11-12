"""Run one fiber-rank cell with atomic publication, identity validation and process-group resource evidence.

An existing JSON is skipped only after its engine, header, field, degree and truncation identities validate and its
resource record names a successful run that wrote the same bytes with the same engine arguments (a digest of the
canonical arguments, absolute paths reduced to repository-relative paths or basenames). A new record is written to
`.part`, validated after a zero engine exit, flushed to disk and atomically renamed. Engine arguments follow a mandatory
`--`. The engine runs in its own process group; SIGTERM or SIGINT delivered to this runner and `--timeout` both
terminate that group (SIGTERM, then SIGKILL after `--grace-seconds`) and still write the resource record with the
termination cause. Failures retain `.part`, stderr and the resource record. `--timeout` replaces an outer `timeout`; an
outer `timeout -k` must exceed `--grace-seconds`, or its SIGKILL reaches the runner before the runner reaches the engine
group. The exit status is 0 on success, 2 when validation fails, 124 on timeout, 128 + n when signal n ended the runner
or the engine, and the engine's own status otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

TIMEOUT_STATUS = 124


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def header_prime(path: Path) -> int:
    text = path.read_text()
    marker = "ring r="
    if marker not in text:
        raise ValueError("header has no ring r line")
    return int(text.split(marker, 1)[1].split(",", 1)[0])


def canonical_engine_arguments(engine_args: list[str]) -> list[list[str]]:
    """Engine arguments grouped as one `--flag` with its values, groups sorted, so flag order does not matter."""
    groups: list[list[str]] = []
    for token in engine_args:
        if token.startswith("--") or not groups:
            groups.append([token])
        else:
            groups[-1].append(token)
    return sorted(groups)


def engine_arguments_digest(engine_args: list[str], root: Path | None) -> str:
    """Digest of the canonical engine arguments, absolute paths made portable so a moved checkout matches."""
    portable = [portable_path(token, root) for token in engine_args]
    text = json.dumps(canonical_engine_arguments(portable), separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def expected_identity(engine: Path, header: Path, degree: int, order: int) -> dict[str, Any]:
    return {
        "check": "fiber-rank-linear-algebra",
        "engine_sha256_16": sha256(engine)[:16],
        "header_sha256_16": sha256(header)[:16],
        "prime": header_prime(header),
        "d": degree,
        "N": order,
    }


def validate_record(path: Path, identity: dict[str, Any]) -> dict[str, Any]:
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: invalid JSON: {error}") from error
    mismatch = {key: (record.get(key), value) for key, value in identity.items() if record.get(key) != value}
    if mismatch:
        raise ValueError(f"{path}: identity mismatch: {mismatch}")
    if type(record.get("r_N")) is not int or record["r_N"] < 0:
        raise ValueError(f"{path}: r_N is not a nonnegative integer")
    return record


def validate_arguments_binding(resources: Path, record: Path, digest: str) -> None:
    """The resource record beside a published record must come from a successful run that wrote these bytes with
    these engine arguments."""
    try:
        evidence = json.loads(resources.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{resources}: cannot read the engine-argument binding: {error}") from error
    if evidence.get("runner_exit") != 0 or evidence.get("stdout_part_sha256") != sha256(record):
        raise ValueError(f"{resources}: does not describe a successful run that wrote {record.name}")
    if evidence.get("engine_args_sha256_16") != digest:
        raise ValueError(
            f"{resources}: engine arguments differ from the recorded run: "
            f"{evidence.get('engine_args_sha256_16')} != {digest}"
        )


def repository_root() -> Path | None:
    """The nearest ancestor of this file that holds gororoba_quantum/parallel.py, or None outside a checkout."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            return parent
    return None


def portable_path(value: str, root: Path | None) -> str:
    """A path as stored in evidence: relative to the repository root when inside it, else its basename."""
    path = Path(value)
    if not path.is_absolute():
        return value
    if root is not None:
        try:
            return str(path.resolve().relative_to(root))
        except ValueError:
            pass
    return path.name


def process_group_rss(pgid: int) -> tuple[int, int]:
    """Resident bytes and process count in process group `pgid`; vanished or unreadable members are skipped."""
    proc = Path("/proc")
    if not proc.is_dir():
        ps = shutil.which("ps")
        if ps is None:
            return 0, 0
        snapshot = subprocess.run(  # noqa: S603 -- resolved system utility, fixed arguments
            [ps, "-axo", "pgid=,rss="],
            check=False,
            capture_output=True,
            text=True,
        )
        resident_kib = count = 0
        for line in snapshot.stdout.splitlines():
            try:
                member_pgid, rss_kib = (int(value) for value in line.split())
            except (ValueError, TypeError):
                continue
            if member_pgid == pgid:
                resident_kib += rss_kib
                count += 1
        return resident_kib * 1024, count

    pages = os.sysconf("SC_PAGE_SIZE")
    resident = count = 0
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
            fields = stat[stat.rfind(")") + 2 :].split()
            if int(fields[2]) != pgid:
                continue
            rss_pages = int((entry / "statm").read_text().split()[1])
        except (FileNotFoundError, PermissionError, ValueError, IndexError):
            continue
        resident += rss_pages * pages
        count += 1
    return resident, count


def fsync_path(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_file(part: Path, final: Path) -> None:
    """Flush `part` to disk, rename it over `final` and flush the directory entry."""
    fsync_path(part)
    os.replace(part, final)
    fsync_directory(final.parent)


def write_json_atomic(path: Path, value: object) -> None:
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(json.dumps(value, indent=1) + "\n")
    publish_file(part, path)


def stop_group(process: subprocess.Popen[bytes], grace: float) -> None:
    """SIGTERM the engine's process group, wait up to `grace` seconds for it to empty, then SIGKILL what remains."""
    pgid = process.pid
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        if process.poll() is not None and process_group_rss(pgid)[1] == 0:
            return
        time.sleep(0.02)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def exit_status(returncode: int) -> int:
    """Shell convention: a child killed by signal n reports 128 + n."""
    return 128 - returncode if returncode < 0 else returncode


def run_cell(args: argparse.Namespace) -> int:
    engine, header, output = Path(args.engine).resolve(), Path(args.header).resolve(), Path(args.output).resolve()
    engine_args = list(args.engine_args)
    identity = expected_identity(engine, header, args.degree, args.order)
    root = repository_root()
    arguments_digest = engine_arguments_digest(engine_args, root)
    resources = output.with_suffix(".resources.json")
    if output.exists():
        validate_record(output, identity)
        validate_arguments_binding(resources, output, arguments_digest)
        print(f"validated existing {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(output.suffix + ".part")
    stderr = output.with_suffix(".err")
    command = [args.python, str(engine), str(header), str(args.degree), str(args.order), *engine_args]

    received: list[int] = []

    def on_signal(number: int, _frame: object) -> None:
        received.append(number)

    previous = {}
    for number in (signal.SIGTERM, signal.SIGINT):
        try:
            previous[number] = signal.signal(number, on_signal)
        except ValueError:  # not the main thread: no handler can be installed
            break
    started = time.time()
    cause = "exited"
    try:
        with part.open("w") as out, stderr.open("w") as err:
            process = subprocess.Popen(
                command, stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True
            )
            peak_rss = peak_processes = 0
            while process.poll() is None:
                rss, processes = process_group_rss(process.pid)
                peak_rss = max(peak_rss, rss)
                peak_processes = max(peak_processes, processes)
                if received:
                    cause = signal.Signals(received[0]).name
                elif args.timeout is not None and time.time() - started >= args.timeout:
                    cause = "timeout"
                if cause != "exited":
                    stop_group(process, args.grace_seconds)
                    break
                time.sleep(args.poll_seconds)
            rss, processes = process_group_rss(process.pid)
            peak_rss = max(peak_rss, rss)
            peak_processes = max(peak_processes, processes)
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)
    elapsed = time.time() - started

    validation_error = None
    if cause == "timeout":
        status = TIMEOUT_STATUS
    elif cause != "exited":
        status = 128 + signal.Signals[cause].value
    elif process.returncode:
        status = exit_status(process.returncode)
    else:
        status = 0
        try:
            validate_record(part, identity)
        except ValueError as error:
            validation_error = str(error)
            status = 2
    write_json_atomic(
        resources,
        {
            "command": [portable_path(token, root) if i else Path(token).name for i, token in enumerate(command)],
            "engine_args_sha256_16": arguments_digest,
            "elapsed_seconds": round(elapsed, 3),
            "engine_exit": process.returncode,
            "termination": cause,
            "timeout_seconds": args.timeout,
            "runner_exit": status,
            "validation_error": validation_error,
            "max_process_group_rss_bytes": peak_rss,
            "max_processes": peak_processes,
            "engine_sha256": sha256(engine),
            "header_sha256": sha256(header),
            "stdout_part_sha256": sha256(part),
            "stderr_sha256": sha256(stderr),
        },
    )
    if validation_error is not None:
        print(validation_error, file=sys.stderr)
    if status == 0:
        publish_file(part, output)
    return status


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    """Runner options, then `--`, then the engine's own arguments."""
    split = argv.index("--") if "--" in argv else len(argv)
    parser = argparse.ArgumentParser(
        usage="rank_cell.py [options] ENGINE HEADER DEGREE ORDER OUTPUT [-- ENGINE_ARGUMENTS ...]"
    )
    parser.add_argument("engine")
    parser.add_argument("header")
    parser.add_argument("degree", type=int)
    parser.add_argument("order", type=int)
    parser.add_argument("output")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--poll-seconds", type=float, default=0.2)
    parser.add_argument(
        "--timeout", type=float, default=None, help="terminate the engine group after SECONDS; exit 124"
    )
    parser.add_argument("--grace-seconds", type=float, default=5.0, help="SIGTERM to SIGKILL delay")
    args = parser.parse_args(argv[:split])
    args.engine_args = argv[split + 1 :]
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be positive")
    if args.timeout is not None and args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.grace_seconds < 0:
        parser.error("--grace-seconds must not be negative")
    return args


def main() -> None:
    raise SystemExit(run_cell(parse_arguments(sys.argv[1:])))


if __name__ == "__main__":
    main()
