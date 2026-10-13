"""Check CI resource defaults and keep-going behavior after a launch failure."""

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
    run_gates._cpus()
    import parallel

    for available, expected in ((12, 6), (7, 3), (1, 1)):
        with patch.object(parallel, "available_cpus", return_value=available):
            if run_gates._cpus() != expected:
                raise RuntimeError("CI pool differs from the shared half-CPU default")
    with TemporaryDirectory(prefix="ci-launch-contract-") as temporary:
        root = Path(temporary)
        (root / "ci").mkdir()
        gates = {
            "gates": [
                {"name": "missing-directory", "cwd": "absent", "cmd": "exit 0"},
                {
                    "name": "retained-success",
                    "cwd": ".",
                    "cmd": 'test "$GOROROBA_WORKERS" = EXPECTED_WORKERS; printf "success survived\\n"',
                },
            ]
        }
        for override, expected_workers in ((None, "1"), ("3", "3")):
            current = json.loads(json.dumps(gates))
            current["gates"][1]["cmd"] = current["gates"][1]["cmd"].replace("EXPECTED_WORKERS", expected_workers)
            (root / "ci/gates.json").write_text(json.dumps(current))
            output = io.StringIO()
            with (
                patch.object(run_gates, "ROOT", root),
                patch.object(run_gates, "_cpus", return_value=2),
                patch.dict(os.environ),
                contextlib.redirect_stdout(output),
            ):
                if override is None:
                    os.environ.pop("GOROROBA_WORKERS", None)
                else:
                    os.environ["GOROROBA_WORKERS"] = override
                status = run_gates.main([])
            if (
                status != 1
                or "FAIL missing-directory" not in output.getvalue()
                or "PASS retained-success" not in output.getvalue()
            ):
                raise RuntimeError("Launch failure discarded the successful gate or its diagnostics")
            if "1 passed, 1 failed of 2" not in output.getvalue():
                raise RuntimeError("Keep-going summary denominator differs")
    print("CI launch failure is retained; later gates run; half-CPU and child-worker overrides hold")


if __name__ == "__main__":
    main()
