"""The degree-3 relations of the fiber cone of E8-bar -> VB along the boost, at one value of w modulo 32029.

boost_family.py (ledger row A5-600) writes the degree-2 relation script of E8-bar -> VB with the basepoint boosted by
c = (w^2 + 1) / (2 w), s = (w^2 - 1) / (2 w). This producer builds the same script with relation_script of
boost_e8_vb_quadrics.py asked for degree 3 (the 220 cubic monomials in the 10 degree-1 generators) and ends it after
the syzygies, printing only the counts, as degree_three_row of that module does for one boost (A5-428). The relations
in degree 3 form {q : q(G) in J + m I^3}; 220 minus their number is h_3 of the fiber cone at that w.

Usage: PYTHON boost_degree3.py --emit VALUE > script.sing (VALUE a rational number, as in boost_family.py), or
PYTHON boost_degree3.py --run DIRECTORY VALUE... to write d3-TAG.sing for each value into DIRECTORY and run Singular
on them through parallel.py (GOROROBA_WORKERS caps the pool), each log beside its script.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[3]
sys.path.insert(0, str(EVIDENCE / "a5-kernel-attachments"))
sys.path.insert(0, str(EVIDENCE.parents[1] / "gororoba_quantum"))
sys.path.insert(0, str(HERE.parent / "e8-vb-boost-family-p32029"))

import boost_e8_vb_quadrics as bq  # noqa: E402
import boost_family as bf  # noqa: E402

import parallel  # noqa: E402

DEGREE = 3
STAGE_END = '"RESULT targets",c;"RESULT relations",size(S);"RESULT done 1";\nquit;\n'


def emit(value: str) -> str:
    """The Singular script of the degree-3 relation count at one value of w."""
    original = bq.relation_script
    bq.relation_script = lambda boost, degree: original(boost, DEGREE)
    try:
        script = bf.emit(value)
    finally:
        bq.relation_script = original
    if f"kbase(std(ideal(0)),{DEGREE})" not in script:
        raise RuntimeError("the relation stage is not of degree 3")
    return script[: script.index('"RESULT targets"')] + STAGE_END


def run_value(item: tuple[str, str]) -> str:
    """Write the script of one value into the directory and run Singular on it; the log sits beside it."""
    directory, value = item
    script = Path(directory) / f"d3-{bf.tag(value)}.sing"
    script.write_text(emit(value), encoding="utf-8")
    with script.with_suffix(".log").open("w", encoding="utf-8") as log:
        subprocess.run(
            ["Singular", "-q", "--no-warn", "--no-rc", str(script)],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return bf.tag(value)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--run":
        # The values are independent Singular runs; the driver reads the logs afterward.
        print(" ".join(parallel.ordered_map(run_value, [(sys.argv[2], v) for v in sys.argv[3:]], min_items=1)))
    elif len(sys.argv) == 3 and sys.argv[1] == "--emit":
        sys.stdout.write(emit(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
