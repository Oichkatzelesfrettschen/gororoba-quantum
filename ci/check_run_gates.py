"""Contract for ci/run_gates.py: unique gate names, every CPU, keep-going past a launch failure,
one child worker by default, --device, --max-seconds, and the requires field with --requires.
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
    expected = run_gates.parallel.available_cpus()
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
    with TemporaryDirectory(prefix="ci-select-contract-") as temporary:
        root = Path(temporary)
        (root / "ci").mkdir()
        listed = [
            {"name": "fast", "cwd": ".", "cmd": "true", "seconds": 1.0},
            {"name": "slow", "cwd": ".", "cmd": "true", "seconds": 9.0},
            {"name": "unmeasured", "cwd": ".", "cmd": "true"},
            {"name": "full-only", "cwd": ".", "cmd": "true", "seconds": 1.0, "tier": "full"},
        ]
        (root / "ci/gates.json").write_text(json.dumps({"gates": listed}))
        for tier, limit, wanted in (("pr", 5.0, ["fast"]), ("pr", None, ["fast", "slow", "unmeasured"])):
            names = [gate["name"] for gate in run_gates.select(root, tier, limit)]
            if names != wanted:
                raise RuntimeError(f"select({tier}, {limit}) chose {names}, not {wanted}")
        # A qi gate runs in every lane, on its replay path where the stack is absent; --requires qi keeps
        # only the qi gates and makes each take its live path.
        qi = [
            {"name": "qi-pr", "cwd": ".", "cmd": 'test "${GOROROBA_QI_REQUIRED:-0}" = 1', "requires": ["qi"]},
            {"name": "qi-full", "cwd": ".", "cmd": "true", "requires": ["qi"], "tier": "full"},
        ]
        (root / "ci/gates.json").write_text(json.dumps({"gates": listed + qi}))
        for tier, requires, wanted in (
            ("pr", None, ["fast", "slow", "unmeasured", "qi-pr"]),
            ("pr", "qi", ["qi-pr"]),
            ("full", "qi", ["qi-pr", "qi-full"]),
        ):
            names = [gate["name"] for gate in run_gates.select(root, tier, None, requires)]
            if names != wanted:
                raise RuntimeError(f"select({tier}, requires={requires}) chose {names}, not {wanted}")
        for flag, expected_status in (([], 1), (["--requires", "qi"], 0)):
            output = io.StringIO()
            with (
                patch.object(run_gates, "ROOT", root),
                patch.dict(os.environ),
                contextlib.redirect_stdout(output),
            ):
                os.environ.pop("GOROROBA_QI_REQUIRED", None)
                status = run_gates.main(["--tier", "pr", *flag])
            if status != expected_status:
                raise RuntimeError(f"{flag or 'no flag'} gave GOROROBA_QI_REQUIRED wrongly:\n{output.getvalue()}")
        for malformed in ([], ["qi", "qi"], ["kaggle"], "qi", [1]):
            gate = {"name": "malformed", "cwd": ".", "cmd": "true", "requires": malformed}
            (root / "ci/gates.json").write_text(json.dumps({"gates": [gate]}))
            try:
                run_gates.select(root, "pr")
            except SystemExit:
                continue
            raise RuntimeError(f"requires {malformed!r} was accepted")
    run_gates.select(Path(__file__).resolve().parent.parent, "full")
    print(
        "run_gates: unique gate names, every CPU, a launch failure keeps going with its diagnostic, "
        "child workers default to one, --device GPU reaches every gate, --max-seconds selects by measured seconds, "
        "qi gates run in every lane and --requires qi keeps them alone with GOROROBA_QI_REQUIRED=1"
    )


if __name__ == "__main__":
    main()
