"""Contract for ci/run_gates.py: unique gate names, every CPU, keep-going past a launch failure,
one child worker by default, --device.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import run_gates


def main() -> None:
    # run_gates selects and reports gates by name, so two gates of one name make a shard result ambiguous.
    names = [gate["name"] for gate in json.loads((Path(__file__).parent / "gates.json").read_text())["gates"]]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise RuntimeError(f"ci/gates.json names more than one gate {', '.join(duplicates)}")
    expected = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    if run_gates._cpus() != expected:
        raise RuntimeError(f"gate pool uses {run_gates._cpus()} workers, not every available CPU ({expected})")
    with TemporaryDirectory(prefix="ci-launch-contract-") as temporary:
        root = Path(temporary)
        (root / "ci").mkdir()
        for override, workers in ((None, "1"), ("3", "3")):
            gates = {
                "gates": [
                    {"name": "missing-directory", "cwd": "absent", "cmd": "exit 0"},
                    {
                        "name": "retained-success",
                        "cwd": ".",
                        "cmd": f'test "$GOROROBA_WORKERS" = {workers}; printf "success survived\\n"',
                    },
                ]
            }
            (root / "ci/gates.json").write_text(json.dumps(gates))
            output = io.StringIO()
            with (
                patch.object(run_gates, "ROOT", root),
                patch.dict(os.environ),
                contextlib.redirect_stdout(output),
            ):
                os.environ.pop("GOROROBA_WORKERS", None)
                if override is not None:
                    os.environ["GOROROBA_WORKERS"] = override
                status = run_gates.main([])
            text = output.getvalue()
            if status != 1 or "FAIL missing-directory" not in text or "PASS retained-success" not in text:
                raise RuntimeError(f"a launch failure stopped the shard or lost a passing gate:\n{text}")
            if "could not start" not in text or "1 passed, 1 failed of 2" not in text:
                raise RuntimeError(f"the launch diagnostic or the keep-going denominator is missing:\n{text}")
        for flag, expected_device in (([], "CPU"), (["--device", "GPU"], "GPU")):
            gates = {
                "gates": [
                    {"name": "device", "cwd": ".", "cmd": f'test "${{GOROROBA_AER_DEVICE:-CPU}}" = {expected_device}'}
                ]
            }
            (root / "ci/gates.json").write_text(json.dumps(gates))
            output = io.StringIO()
            with (
                patch.object(run_gates, "ROOT", root),
                patch.dict(os.environ),
                contextlib.redirect_stdout(output),
            ):
                os.environ.pop("GOROROBA_AER_DEVICE", None)
                status = run_gates.main(flag)
            text = output.getvalue()
            if status != 0 or f"gates in shard 0/1 on {expected_device}" not in text:
                raise RuntimeError(f"{flag} did not give every gate GOROROBA_AER_DEVICE={expected_device}:\n{text}")
    print(
        "run_gates: unique gate names, every CPU, a launch failure keeps going with its diagnostic, "
        "child workers default to one, --device GPU reaches every gate"
    )


if __name__ == "__main__":
    main()
