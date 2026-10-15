"""Exact cubic normal form of the dim-32 associator phases and its compiled cost.

The associator phase omega_ij(x) of W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j}
(predict.associator_phase) is a Boolean function of x in F_2^5. For the 360
unordered pairs whose larger index has bit length 5 its algebraic degree is 3
(DESIGN_NOTES.md). This script certifies, by exhaustive ANF over cd_core,
that each such phase is f = l1 l2 l3 + q with l1, l2, l3 linearly
independent linear forms and deg q <= 2, so W_ij equals
D_q U_A^dagger (CCZ x I) U_A with U_A a CNOT network and D_q a Z/CZ
diagonal. The degree-3 part takes 15 distinct values, 24 pairs each.

Three circuits implement each W_ij and are checked operator-equal to
diag((-1)^f):

- factorized: designs.design_c_associator_spectrum's three multiplication
  blocks, the circuit whose hardware run tests composition of the factors;
- reed_muller: select_lcu.phase_oracle_from_truth_table on f, one Z, CZ or
  CCZ per ANF monomial;
- normal_form: LinearFunction(A), one CCZ, LinearFunction(A)^-1, then the
  Reed-Muller oracle of q.

Each is transpiled to the ibm_kingston coupling map of
docs/evidence/heron_platform/targets.json with basis cz, rz, sx, x at
optimization level 3 and a fixed seed, and the CZ count is retained. The two
diagonal circuits are built from the precomputed phase, so they encode the
predicted answer and serve as references for the factorized circuit, never
as substitutes for it.

--write regenerates docs/evidence/ccz-reduction/normal_form.json; --check
recomputes every value and requires equality with the retained file.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit.library import LinearFunction  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402
from qiskit.transpiler import CouplingMap  # noqa: E402

from boolean_anf import anf_coefficients  # noqa: E402
from designs import _unitary_part, design_c_associator_spectrum  # noqa: E402
from predict import associator_phase  # noqa: E402
from select_lcu import phase_oracle_from_truth_table  # noqa: E402

OUT = ROOT / "docs/evidence/ccz-reduction/normal_form.json"
SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
BACKEND = "ibm_kingston"
BASIS = ["cz", "rz", "sx", "x"]
OPTIMIZATION_LEVEL = 3
SEED = 11
N = 5
DIM = 32
IMPLEMENTATIONS = ("factorized", "reed_muller", "normal_form")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parity(mask: int, x: int) -> int:
    return (mask & x).bit_count() & 1


def gf2_rank(vectors: list[int]) -> int:
    basis: list[int] = []
    for vector in vectors:
        for pivot in sorted(basis, reverse=True):
            vector = min(vector, vector ^ pivot)
        if vector:
            basis.append(vector)
    return len(basis)


def cubic_part(truth_table: list[int]) -> frozenset[int]:
    return frozenset(mask for mask in anf_coefficients(truth_table) if mask.bit_count() == 3)


def product_table(forms: tuple[int, int, int]) -> list[int]:
    u, v, w = forms
    return [parity(u, x) & parity(v, x) & parity(w, x) for x in range(DIM)]


def rank_one_forms() -> dict[frozenset[int], tuple[int, int, int]]:
    """First independent triple (lexicographic) for every reachable cubic part."""
    forms: dict[frozenset[int], tuple[int, int, int]] = {}
    for triple in itertools.combinations(range(1, DIM), 3):
        if gf2_rank(list(triple)) == 3:
            forms.setdefault(cubic_part(product_table(triple)), triple)
    return forms


def completed_rows(forms: tuple[int, int, int]) -> list[int]:
    rows = list(forms)
    for bit in range(N):
        if len(rows) == N:
            break
        if gf2_rank([*rows, 1 << bit]) > len(rows):
            rows.append(1 << bit)
    require(gf2_rank(rows) == N, f"rows {rows} do not complete to an invertible map")
    return rows


def normal_form_circuit(truth_table: list[int], forms: tuple[int, int, int]) -> QuantumCircuit:
    rows = completed_rows(forms)
    matrix = np.array([[row >> bit & 1 for bit in range(N)] for row in rows], dtype=bool)
    remainder = [f ^ p for f, p in zip(truth_table, product_table(forms), strict=True)]
    require(max((m.bit_count() for m in anf_coefficients(remainder)), default=0) <= 2, "remainder exceeds degree 2")
    linear = LinearFunction(matrix)
    circuit = QuantumCircuit(N)
    circuit.append(linear, range(N))
    circuit.ccz(0, 1, 2)
    circuit.append(linear.inverse(), range(N))
    circuit.compose(phase_oracle_from_truth_table(remainder), range(N), inplace=True)
    return circuit


def coupling_map() -> CouplingMap:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return CouplingMap([tuple(edge) for edge in snapshot["backends"][BACKEND]["instructions"]["cz"]["qargs"]])


def compiled_cz(circuit: QuantumCircuit, cmap: CouplingMap) -> int:
    compiled = transpile(
        circuit,
        coupling_map=cmap,
        basis_gates=BASIS,
        optimization_level=OPTIMIZATION_LEVEL,
        seed_transpiler=SEED,
    )
    return int(compiled.count_ops().get("cz", 0))


def compute() -> dict[str, Any]:
    forms_by_part = rank_one_forms()
    cmap = coupling_map()
    pairs = [(i, j) for i in range(1, DIM) for j in range(i + 1, DIM) if j.bit_length() == N]
    require(len(pairs) == 360, f"expected 360 dim-32 pairs, found {len(pairs)}")
    records = []
    part_counts: Counter[frozenset[int]] = Counter()
    for i, j in pairs:
        truth_table = [1 if sign == -1 else 0 for sign in associator_phase(DIM, i, j)]
        degree = max(mask.bit_count() for mask in anf_coefficients(truth_table))
        require(degree == 3, f"pair ({i}, {j}) has degree {degree}")
        part = cubic_part(truth_table)
        require(part in forms_by_part, f"pair ({i}, {j}) cubic part is not a product of three independent forms")
        part_counts[part] += 1
        forms = forms_by_part[part]
        want = Operator(np.diag([(-1.0) ** bit for bit in truth_table]))
        circuits = {
            "factorized": _unitary_part(design_c_associator_spectrum(DIM, i, j)),
            "reed_muller": phase_oracle_from_truth_table(truth_table),
            "normal_form": normal_form_circuit(truth_table, forms),
        }
        for name, circuit in circuits.items():
            require(Operator(circuit).equiv(want), f"pair ({i}, {j}) {name} differs from diag((-1)^f)")
        records.append(
            {
                "pair": [i, j],
                "cubic_monomials": sorted(part),
                "forms": list(forms),
                "cz": {name: compiled_cz(circuits[name], cmap) for name in IMPLEMENTATIONS},
            }
        )
    require(len(part_counts) == 15 and set(part_counts.values()) == {24}, f"cubic parts {sorted(part_counts.values())}")
    by_size: dict[str, dict[str, Any]] = {}
    for size in sorted({len(r["cubic_monomials"]) for r in records}):
        group = [r for r in records if len(r["cubic_monomials"]) == size]
        by_size[str(size)] = {
            "pairs": len(group),
            "cz": {
                name: {
                    "min": min(r["cz"][name] for r in group),
                    "mean": round(sum(r["cz"][name] for r in group) / len(group), 3),
                    "max": max(r["cz"][name] for r in group),
                }
                for name in IMPLEMENTATIONS
            },
        }
    return {
        "schema": "associator-cubic-normal-form-v1",
        "dimension": DIM,
        "pairs": len(records),
        "distinct_cubic_parts": len(part_counts),
        "pairs_per_cubic_part": 24,
        "compile": {
            "backend_snapshot": BACKEND,
            "basis": BASIS,
            "optimization_level": OPTIMIZATION_LEVEL,
            "seed_transpiler": SEED,
            "qiskit": qiskit.__version__,
        },
        "by_cubic_monomial_count": by_size,
        "normal_form_below_reed_muller": sum(r["cz"]["normal_form"] < r["cz"]["reed_muller"] for r in records),
        "records": records,
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render(compute())
    if args.write:
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
        return 0
    require(OUT.read_text(encoding="utf-8") == text, f"{OUT.relative_to(ROOT)} differs from a fresh computation")
    print("associator cubic normal form: 360 pairs, 15 rank-one cubic parts x 24, compiled CZ counts reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
