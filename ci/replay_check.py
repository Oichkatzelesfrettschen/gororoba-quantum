"""Replay a retained JSON analysis within a declared float tolerance.

Usage: ``"$PYTHON" ci/replay_check.py RETAINED [--rel R] [--abs A] -- COMMAND...``

COMMAND writes a fresh analysis to the path that replaces ``{out}`` among its
arguments, a file in a temporary directory named like RETAINED. The replay
passes when the fresh bytes equal RETAINED's, or when both parse as JSON
whose structure, keys, strings, booleans, integers and nulls agree exactly
and every pair of floats differs by at most ``abs + rel * max(|a|, |b|)``.

Fitted values follow the floating-point kernels of the host: BLAS, numpy's
CPU-dispatched loops and libm round differently on different CPUs, so a
byte replay of a fit holds only on the CPU that wrote it. Each gate states
the tolerance its analysis resolves, below its reported uncertainties, and
every discrete outcome (a status, a chosen cell, a wrap count) still
compares exactly.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PLACEHOLDER = "{out}"
SHOWN = 10


def differences(retained: Any, fresh: Any, rel: float, absolute: float, path: str = "") -> list[str]:
    """Every place where fresh departs from retained beyond the tolerance, as readable lines."""
    if isinstance(retained, bool) or isinstance(fresh, bool):
        return [] if retained is fresh else [f"{path or '.'}: {retained!r} -> {fresh!r}"]
    numbers = (int, float)
    if isinstance(retained, numbers) and isinstance(fresh, numbers):
        if isinstance(retained, int) and isinstance(fresh, int):
            return [] if retained == fresh else [f"{path or '.'}: {retained} -> {fresh}"]
        bound = absolute + rel * max(abs(retained), abs(fresh))
        return [] if abs(retained - fresh) <= bound else [f"{path or '.'}: {retained!r} -> {fresh!r}"]
    if isinstance(retained, dict) and isinstance(fresh, dict):
        if set(retained) != set(fresh):
            return [f"{path or '.'}: keys {sorted(set(retained) ^ set(fresh))} on one side only"]
        found: list[str] = []
        for key in sorted(retained):
            found += differences(retained[key], fresh[key], rel, absolute, f"{path}.{key}")
        return found
    if isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            return [f"{path or '.'}: length {len(retained)} -> {len(fresh)}"]
        found = []
        for index, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            found += differences(left, right, rel, absolute, f"{path}[{index}]")
        return found
    return [] if retained == fresh else [f"{path or '.'}: {retained!r} -> {fresh!r}"]


def compare(retained: Path, fresh: Path, rel: float, absolute: float) -> list[str]:
    if retained.read_bytes() == fresh.read_bytes():
        return []
    try:
        old, new = json.loads(retained.read_text()), json.loads(fresh.read_text())
    except json.JSONDecodeError as error:
        return [f"{retained} differs from the fresh output and does not parse as JSON: {error}"]
    return differences(old, new, rel, absolute)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--" not in arguments:
        raise SystemExit("replay_check: separate the command with --")
    split = arguments.index("--")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("retained", type=Path)
    parser.add_argument("--rel", type=float, default=0.0)
    parser.add_argument("--abs", dest="absolute", type=float, default=0.0)
    options = parser.parse_args(arguments[:split])
    command = arguments[split + 1 :]
    if PLACEHOLDER not in command:
        raise SystemExit(f"replay_check: the command names no {PLACEHOLDER} argument")
    with tempfile.TemporaryDirectory() as directory:
        fresh = Path(directory) / options.retained.name
        completed = subprocess.run([str(fresh) if part == PLACEHOLDER else part for part in command], check=False)
        if completed.returncode:
            return completed.returncode
        found = compare(options.retained, fresh, options.rel, options.absolute)
    if found:
        print(f"{options.retained}: {len(found)} fields differ beyond rel {options.rel:g}, abs {options.absolute:g}")
        for line in found[:SHOWN]:
            print(f"  {line}")
        return 1
    print(f"{options.retained}: replayed within rel {options.rel:g}, abs {options.absolute:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
