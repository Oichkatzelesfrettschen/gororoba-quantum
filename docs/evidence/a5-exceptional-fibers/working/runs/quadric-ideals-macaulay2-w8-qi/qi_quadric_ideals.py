"""Write the Q(i) quadric relation ideals of the weight-slice fiber cones as text files for a second engine.

weight_slice_fiber_relations.py (ledger row A5-421) computes, at the N+ and N- basepoints, the degree-2 relations of
the fiber cones of the nullity-8 sources over Q(i) and hands each relation ideal in characteristic 0 to its Hilbert
stage through hilbert_script. This script wraps hilbert_script, rebuilds the record (with the producer's own pass
rules), and writes every characteristic-0 relation ideal it receives as qi-gG-DIGEST.txt in the output directory: a
first line "generators G relations R", then one polynomial per line in Singular syntax over Q(i) with i^2 = -1.
DIGEST is the first 12 hex digits of the sha256 of the polynomial lines, so a rerun that writes the same names wrote
the same ideals.

Usage: PYTHON qi_quadric_ideals.py [OUTDIR] (default: this directory), from any working directory.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "docs/evidence/a5-kernel-attachments"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT))

import weight_slice_fiber_relations as wsf  # noqa: E402

OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE
ORIGINAL = wsf.hilbert_script


def recording(relations: list[str], generators: int, characteristic: int, root: int) -> Any:
    """hilbert_script, which also writes the relation ideal when the field is Q(i)."""
    script = ORIGINAL(relations, generators, characteristic, root)
    if characteristic == 0:
        polynomials = []
        for line in relations:
            terms = [
                f"({coefficient})*{'*'.join(f'y({k})' for k in key)}" for key, coefficient in wsf.parse_relation(line)
            ]
            polynomials.append("+".join(terms))
        body = "\n".join(polynomials)
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
        text = f"generators {generators} relations {len(polynomials)}\n{body}\n"
        (OUT / f"qi-g{generators}-{digest}.txt").write_text(text, encoding="utf-8")
    return script


# The producer dispatches through a spawning process pool, so the wrapper is installed at import in every process.
wsf.hilbert_script = recording

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    record = wsf.build_record(2)
    wsf._self_test(record)
    print("written", len(sorted(OUT.glob("qi-g*.txt"))), "pass", record["pass"])
