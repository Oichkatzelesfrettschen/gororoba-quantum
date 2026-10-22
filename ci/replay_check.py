"""Replay a retained JSON analysis exactly, outside declared analyzer-identity paths.

Usage: ``"$PYTHON" ci/replay_check.py RETAINED [--skip GLOB]... -- COMMAND...``

COMMAND writes a fresh analysis to the path that replaces ``{out}`` among its
arguments, a file in a temporary directory named like RETAINED. The replay
passes when the fresh bytes equal RETAINED's, or when both parse as JSON that
agrees in every value, every float bit for bit, once the paths matching a
``--skip`` GLOB (``.analyzer_sha256``) drop from both sides. A skipped path
names the analyzer rather than its result: a closure digest moves with every
edit to an imported module while the fitted values stay fixed.

Bit-for-bit floats hold because the record was written in the runner image
(ci/runner_image.sh, bound by ci/runner_image_records.json) under the
numpy dispatch cap and OpenBLAS core type that ci/run_gates.py sets.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PLACEHOLDER = "{out}"
SHOWN = 10


def differences(retained: Any, fresh: Any, path: str = "", skip: tuple[str, ...] = ()) -> list[str]:
    """Every place where fresh departs from retained outside the skipped paths, as readable lines."""
    if any(fnmatch.fnmatchcase(path, glob) for glob in skip):
        return []
    if isinstance(retained, dict) and isinstance(fresh, dict):
        unpaired = [
            key
            for key in set(retained) ^ set(fresh)
            if not any(fnmatch.fnmatchcase(f"{path}.{key}", glob) for glob in skip)
        ]
        if unpaired:
            return [f"{path or '.'}: keys {sorted(unpaired)} on one side only"]
        found: list[str] = []
        for key in sorted(set(retained) & set(fresh)):
            found += differences(retained[key], fresh[key], f"{path}.{key}", skip)
        return found
    if isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            return [f"{path or '.'}: length {len(retained)} -> {len(fresh)}"]
        found = []
        for index, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            found += differences(left, right, f"{path}[{index}]", skip)
        return found
    # A float compares by its IEEE-754 encoding: 0.0 and -0.0 differ, and a NaN equals itself.
    if isinstance(retained, float) and type(fresh) is float:
        same = retained.hex() == fresh.hex()
    else:
        same = type(retained) is type(fresh) and retained == fresh
    return [] if same else [f"{path or '.'}: {retained!r} -> {fresh!r}"]


def compare(retained: Path, fresh: Path, skip: tuple[str, ...] = ()) -> list[str]:
    if retained.read_bytes() == fresh.read_bytes():
        return []
    try:
        old, new = json.loads(retained.read_text()), json.loads(fresh.read_text())
    except json.JSONDecodeError as error:
        return [f"{retained} differs from the fresh output and does not parse as JSON: {error}"]
    return differences(old, new, "", skip)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--" not in arguments:
        raise SystemExit("replay_check: separate the command with --")
    split = arguments.index("--")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("retained", type=Path)
    parser.add_argument("--skip", action="append", default=[])
    options = parser.parse_args(arguments[:split])
    command = arguments[split + 1 :]
    if PLACEHOLDER not in command:
        raise SystemExit(f"replay_check: the command names no {PLACEHOLDER} argument")
    with tempfile.TemporaryDirectory() as directory:
        fresh = Path(directory) / options.retained.name
        completed = subprocess.run([str(fresh) if part == PLACEHOLDER else part for part in command], check=False)
        if completed.returncode:
            return completed.returncode
        found = compare(options.retained, fresh, tuple(options.skip))
    if found:
        print(f"{options.retained}: {len(found)} fields differ from the fresh output")
        for line in found[:SHOWN]:
            print(f"  {line}")
        return 1
    print(f"{options.retained}: replayed exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
