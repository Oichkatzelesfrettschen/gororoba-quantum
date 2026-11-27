"""Cohen-Macaulay and reducedness of the quadric ring of E8-bar -> VB over Q(i) (the ninth cell of A5-548).

`weight_slice_quadric_rings.py` decides the eight cells at the N+ and N- basepoints. E8-bar -> VB has no weight-slice
relations; its degree-2 relations over Q(i) come from `a5-char0-transfer/quadric_lift.py` (ledger row A5-315): the
quadrics q with q(G) in J + m I^2, as the reduced row echelon form of the constant syzygies. This program reruns
that computation, binds the relations to the retained K2 by their reduction at (32029, 9115), which must equal the
reduced echelon form of the retained relation file, and passes the 21 quadrics on 10 generators to the decision
procedure of `weight_slice_quadric_rings.decide`: a system of parameters from the fixed list of sparse forms, the
length of the Artinian quotient against the degree, the chart certificate and the radical probe.

Prediction, from the two primes and 32057 (A5-010, A5-020, A5-560): dimension 4, degree 7, length 7, so
Cohen-Macaulay, and K radical. The program exits 1 on any other row.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_vb_quadric_ring_qi.py --out OUT.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "a5-char0-transfer"))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import quadric_lift as ql  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402
import weight_slice_quadric_rings as wq  # noqa: E402

SCHEMA = "gororoba.a5.e8-vb-quadric-ring-qi/1"
SLUG = "e8-vb"
TIMEOUT_SECONDS = 4 * 3600
RING = "E8bar->VB"
VARIABLES = 10
EXPECTED: dict[str, Any] = {
    "ring": RING,
    "variables": VARIABLES,
    "generators": 21,
    "krull_dim": 4,
    "degree": 7,
    "length": 7,
    "cohen_macaulay": True,
    "reduced": True,
    "reduced_basis": "rad K = K",
    "hypothesis_holds": True,
}


def relations() -> tuple[list[str], dict[str, Any]]:
    """The Q(i) quadrics as Singular polynomials, and their binding to the retained K2 at each prime of the slug."""
    outcome = ql.rees._run_singular(ql.singular_script(SLUG), "quadrics_qi", TIMEOUT_SECONDS)
    if outcome.status != "completed":
        raise SystemExit(f"{SLUG}: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    count = int(res["targets"])
    targets = [ql._monomial(res[f"target_{i}"]) for i in range(1, count + 1)]
    columns = {monomial: index for index, monomial in enumerate(targets)}
    rows = [[ql._g(x) for x in res[f"rel_{j}"].split(";")] for j in range(1, int(res["relations"]) + 1)]
    echelon, _ = ql._rref_qi(rows)
    bound = []
    for prime, root, directory in ql.SOURCES[SLUG]:
        modular = ql._rref_fp(ql._modular_rows(ql.FIBERS / directory / "relations-upto-d2.rel", columns, prime), prime)
        reduced, bad = ql._reduce(echelon, prime, root)
        bound.append({"prime": prime, "root": root, "echelon_equal": bad == 0 and reduced == modular})
    polynomials = [
        "+".join(
            f"(({a})+({b})*i)*" + "*".join(f"y({k})" for k in targets[j])
            for j, (a, b) in enumerate(row)
            if (a, b) != (0, 0)
        )
        for row in echelon
    ]
    digest = hashlib.sha256("\n".join(polynomials).encode()).hexdigest()
    return polynomials, {"relations": len(polynomials), "relations_sha256": digest, "reductions": bound}


def problems(record: dict[str, Any]) -> list[str]:
    """The departures of a record from the prediction; an empty list for the retained record."""
    found = []
    cell = record.get("cell", {})
    if {k: cell.get(k) for k in EXPECTED} != EXPECTED:
        found.append("the cell differs from a reduced Cohen-Macaulay ring of dimension 4 and degree 7")
    binding = record.get("binding", {})
    reductions = binding.get("reductions", [])
    if binding.get("relations") != 21 or not reductions or not all(r.get("echelon_equal") is True for r in reductions):
        found.append("the Q(i) relations are not 21 quadrics that reduce onto the retained K2")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="write the JSON record")
    args = parser.parse_args()
    polynomials, binding = relations()
    cell = wq.decide(RING, VARIABLES, polynomials, None)
    cell.pop("measurements", None)
    banner, version = ws.singular_version()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "tools": {"singular": banner, "singular_version": version},
        "binding": binding,
        "cell": cell,
    }
    record["problems"] = problems(record)
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(cell["ring"], cell["krull_dim"], cell["degree"], cell["length"], cell["cohen_macaulay"], cell["reduced"])
    for line in record["problems"]:
        print("PROBLEM", line, file=sys.stderr)
    return 0 if record["problems"] == [] else 1


if __name__ == "__main__":
    sys.exit(main())
