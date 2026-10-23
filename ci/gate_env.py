"""Run COMMAND... under the environment ci/run_gates.py gives every gate (run_gates.environment_for).

ci/runner_image.sh writes records through it, so a record and the gate that
replays it see the same native thread counts, OpenBLAS kernel, numpy CPU
features and glibc tunables.
"""

from __future__ import annotations

import os
import sys

import run_gates


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("gate_env: name a command")
    os.execvpe(argv[0], argv, run_gates.environment_for(None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
