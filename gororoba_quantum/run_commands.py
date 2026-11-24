"""Run independent shell commands through the process pool and report each exit status.

Usage: "$PYTHON" run_commands.py COMMAND...

Each argument is one `sh -c` command line. The commands are the independent
units of a replay script (one Singular run each); parallel.ordered_map spreads
them over the pool, so GOROROBA_WORKERS caps how many run at once and 1 runs
them one after another. A unit's standard output and error come back with its
status and print in argument order after every unit has ended, so a failing
unit never leaves a sibling running unobserved. The exit status is 1 when any
unit exits nonzero. List the longest units first: the pool takes items in order.
"""

from __future__ import annotations

import subprocess
import sys

import parallel


def run_command(command: str) -> tuple[str, int, str]:
    """The command, its exit status and its combined standard output and error."""
    done = subprocess.run(["sh", "-c", command], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
    return command, done.returncode, done.stdout + done.stderr


def main(commands: list[str]) -> int:
    if not commands:
        raise SystemExit("run_commands: no command given")
    failed = 0
    for command, status, output in parallel.ordered_map(run_command, commands, min_items=1):
        print(f"run_commands: exit {status}: {command}")
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
        failed += status != 0
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
