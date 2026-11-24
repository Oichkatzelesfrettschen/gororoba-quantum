"""Run the Macaulay2 invariant scripts of this directory through parallel.py, one log per ideal.

The modular W8 ideal (w8_a2/w8_k2.rel through ../quadric-ideals-macaulay2-p32009/quadric_invariants.m2) and every
qi-g*.txt ideal (through qi_invariants.m2) are independent runs; parallel.ordered_map dispatches them under the
repository's worker budget (GOROROBA_WORKERS) and returns the names in input order, which the driver uses to assemble
results.txt. Usage: PYTHON qi_m2_runner.py (from the repository root, M2 on PATH).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent
sys.path.insert(0, str(HERE.parents[5] / "gororoba_quantum"))

import parallel  # noqa: E402

W8_SCRIPT = RUNS / "quadric-ideals-macaulay2-p32009" / "quadric_invariants.m2"
W8_IDEAL = RUNS / "w8_a2" / "w8_k2.rel"


def items() -> list[tuple[str, list[str]]]:
    """(name, M2 arguments) for every run, the modular W8 ideal first, then the Q(i) files in name order."""
    runs = [("W8-nm-p32009", [str(W8_SCRIPT), "W8-nm-p32009", str(W8_IDEAL), "24"])]
    for path in sorted(HERE.glob("qi-g*.txt")):
        runs.append((path.stem, [str(HERE / "qi_invariants.m2"), path.stem, str(path)]))
    return runs


def run_one(item: tuple[str, list[str]]) -> str:
    """Run Macaulay2 on one ideal and write NAME.log beside this file; return the name."""
    name, arguments = item
    with (HERE / f"{name}.log").open("w", encoding="utf-8") as log:
        subprocess.run(
            ["M2", "--script", *arguments], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, check=False
        )
    return name


if __name__ == "__main__":
    print(" ".join(parallel.ordered_map(run_one, items(), min_items=1)))
