"""Replay a retained JSON analysis within a declared float tolerance.

Usage: ``"$PYTHON" ci/replay_check.py RETAINED [--rel R] [--abs A] [--field GLOB=R,A]... [--skip GLOB]...
[--select PATH] [--baseline BASELINE] -- COMMAND...``

COMMAND writes a fresh analysis to the path that replaces ``{out}`` among its
arguments, a file in a temporary directory named like RETAINED. The replay
passes when the fresh bytes equal RETAINED's, or when both parse as JSON
whose structure, keys, strings, booleans, integers and nulls agree exactly
and every pair of floats differs by at most ``abs + rel * max(|a|, |b|)``.
A ``--field`` rule replaces that bound for the floats whose dotted path
(``.fits.static.nll``, ``.rows[2].alias_llr``) matches its fnmatch GLOB; the
first matching rule applies. A ``--skip`` GLOB drops the matching paths
from both sides, for fields that name the analyzer rather than its result
(a closure digest that moves with every edit to an imported module).
``--baseline`` names a record of the same analysis written in the runner
image (ci/runner_image.sh) for a RETAINED record that a foreign arithmetic
stack wrote: the fresh output must equal BASELINE outside the skipped
paths, every float bit for bit, and RETAINED compares to BASELINE, two fixed
files, under the tolerance rules.
``--select`` compares one subtree of RETAINED (``.rows[4]``) against the
whole fresh output, so a costly table replays one row per gate.

Fitted values follow the floating-point kernels of the host: BLAS, numpy's
CPU-dispatched loops and libm round differently on different CPUs, so a
byte replay of a fit holds only on the CPU that wrote it. Each gate states
the tolerance its analysis resolves, below its reported uncertainties, and
every discrete outcome (a status, a chosen cell, a wrap count) still
compares exactly. A log-likelihood of 1e5 nats and a readout error of 1e-3
share no relative bound, so likelihood fields take an absolute rule in nats.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PLACEHOLDER = "{out}"
SHOWN = 10

Rule = tuple[str, float, float]


def differences(
    retained: Any,
    fresh: Any,
    rel: float,
    absolute: float,
    path: str = "",
    rules: tuple[Rule, ...] = (),
    skip: tuple[str, ...] = (),
) -> list[str]:
    """Every place where fresh departs from retained beyond the tolerance, as readable lines."""
    if any(fnmatch.fnmatchcase(path, glob) for glob in skip):
        return []
    if isinstance(retained, bool) or isinstance(fresh, bool):
        return [] if retained is fresh else [f"{path or '.'}: {retained!r} -> {fresh!r}"]
    numbers = (int, float)
    if isinstance(retained, numbers) and isinstance(fresh, numbers):
        if isinstance(retained, int) and isinstance(fresh, int):
            return [] if retained == fresh else [f"{path or '.'}: {retained} -> {fresh}"]
        rel, absolute = next(((r, a) for glob, r, a in rules if fnmatch.fnmatchcase(path, glob)), (rel, absolute))
        bound = absolute + rel * max(abs(retained), abs(fresh))
        return [] if abs(retained - fresh) <= bound else [f"{path or '.'}: {retained!r} -> {fresh!r}"]
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
            found += differences(retained[key], fresh[key], rel, absolute, f"{path}.{key}", rules, skip)
        return found
    if isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            return [f"{path or '.'}: length {len(retained)} -> {len(fresh)}"]
        found = []
        for index, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            found += differences(left, right, rel, absolute, f"{path}[{index}]", rules, skip)
        return found
    return [] if retained == fresh else [f"{path or '.'}: {retained!r} -> {fresh!r}"]


def subtree(value: Any, path: str) -> Any:
    """The node of value at a dotted path such as ``.rows[4].alias`` (keys after dots, list indices in brackets)."""
    for key, index in re.findall(r"\.([^.\[]+)|\[(\d+)\]", path):
        value = value[key] if key else value[int(index)]
    return value


def compare(
    retained: Path,
    fresh: Path,
    rel: float,
    absolute: float,
    rules: tuple[Rule, ...] = (),
    skip: tuple[str, ...] = (),
    select: str = "",
) -> list[str]:
    if not select and retained.read_bytes() == fresh.read_bytes():
        return []
    try:
        old, new = subtree(json.loads(retained.read_text()), select), json.loads(fresh.read_text())
    except json.JSONDecodeError as error:
        return [f"{retained} differs from the fresh output and does not parse as JSON: {error}"]
    return differences(old, new, rel, absolute, "", rules, skip)


def rule(text: str) -> Rule:
    glob, separator, bounds = text.rpartition("=")
    rel, comma, absolute = bounds.partition(",")
    if not separator or not glob or not comma:
        raise argparse.ArgumentTypeError(f"{text!r} is not GLOB=REL,ABS")
    return glob, float(rel), float(absolute)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--" not in arguments:
        raise SystemExit("replay_check: separate the command with --")
    split = arguments.index("--")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("retained", type=Path)
    parser.add_argument("--rel", type=float, default=0.0)
    parser.add_argument("--abs", dest="absolute", type=float, default=0.0)
    parser.add_argument("--field", dest="rules", type=rule, action="append", default=[])
    parser.add_argument("--skip", action="append", default=[])
    parser.add_argument("--select", default="")
    parser.add_argument("--baseline", type=Path)
    options = parser.parse_args(arguments[:split])
    command = arguments[split + 1 :]
    if PLACEHOLDER not in command:
        raise SystemExit(f"replay_check: the command names no {PLACEHOLDER} argument")
    with tempfile.TemporaryDirectory() as directory:
        fresh = Path(directory) / options.retained.name
        completed = subprocess.run([str(fresh) if part == PLACEHOLDER else part for part in command], check=False)
        if completed.returncode:
            return completed.returncode
        if options.baseline is not None:
            drift = compare(options.baseline, fresh, 0.0, 0.0, (), tuple(options.skip))
            if drift:
                print(f"{options.baseline}: the fresh output differs from the baseline in {len(drift)} fields")
                for line in drift[:SHOWN]:
                    print(f"  {line}")
                return 1
        found = compare(
            options.retained,
            fresh if options.baseline is None else options.baseline,
            options.rel,
            options.absolute,
            tuple(options.rules),
            tuple(options.skip),
            options.select,
        )
    if found:
        print(f"{options.retained}: {len(found)} fields differ beyond rel {options.rel:g}, abs {options.absolute:g}")
        for line in found[:SHOWN]:
            print(f"  {line}")
        return 1
    print(f"{options.retained}: replayed within rel {options.rel:g}, abs {options.absolute:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
