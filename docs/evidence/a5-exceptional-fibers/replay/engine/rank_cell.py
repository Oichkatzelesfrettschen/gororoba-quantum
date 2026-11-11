"""Run one fiber-rank cell with atomic publication, identity validation and process-tree resource evidence.

An existing JSON is skipped only after its engine, header, field, degree and truncation identities validate. A new
record is written to `.part`, validated after a zero engine exit and atomically renamed. Failures retain `.part`,
stderr and the resource record, and this runner exits with the engine or validation status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


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


def process_group_rss(pgid: int) -> tuple[int, int]:
    """Resident bytes and process count in Linux process group `pgid`; vanished or unreadable members are skipped."""
    pages = os.sysconf("SC_PAGE_SIZE")
    resident = count = 0
    for entry in Path("/proc").iterdir():
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


def run_cell(args: argparse.Namespace) -> int:
    engine, header, output = Path(args.engine).resolve(), Path(args.header).resolve(), Path(args.output).resolve()
    identity = expected_identity(engine, header, args.degree, args.order)
    if output.exists():
        validate_record(output, identity)
        print(f"validated existing {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(output.suffix + ".part")
    stderr = output.with_suffix(".err")
    resources = output.with_suffix(".resources.json")
    command = [args.python, str(engine), str(header), str(args.degree), str(args.order), *args.engine_args]
    started = time.time()
    with part.open("w") as out, stderr.open("w") as err:
        process = subprocess.Popen(command, stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True)
        peak_rss = peak_processes = 0
        while process.poll() is None:
            rss, processes = process_group_rss(process.pid)
            peak_rss = max(peak_rss, rss)
            peak_processes = max(peak_processes, processes)
            time.sleep(args.poll_seconds)
        rss, processes = process_group_rss(process.pid)
        peak_rss = max(peak_rss, rss)
        peak_processes = max(peak_processes, processes)
    elapsed = time.time() - started
    evidence = {
        "command": command,
        "elapsed_seconds": round(elapsed, 3),
        "engine_exit": process.returncode,
        "max_process_group_rss_bytes": peak_rss,
        "max_processes": peak_processes,
        "engine_sha256": sha256(engine),
        "header_sha256": sha256(header),
        "stdout_part_sha256": sha256(part),
        "stderr_sha256": sha256(stderr),
    }
    resources.write_text(json.dumps(evidence, indent=1) + "\n")
    if process.returncode:
        return int(process.returncode)
    try:
        validate_record(part, identity)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    os.replace(part, output)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("engine")
    parser.add_argument("header")
    parser.add_argument("degree", type=int)
    parser.add_argument("order", type=int)
    parser.add_argument("output")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--poll-seconds", type=float, default=0.2)
    parser.add_argument("engine_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")
    if args.engine_args[:1] == ["--"]:
        args.engine_args = args.engine_args[1:]
    raise SystemExit(run_cell(args))


if __name__ == "__main__":
    main()
