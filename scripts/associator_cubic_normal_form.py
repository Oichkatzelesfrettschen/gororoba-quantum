"""Exact cubic normal form of the dim-32 associator phases and its compiled cost.

The associator phase omega_ij(x) of W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j}
(predict.associator_phase) is a Boolean function of x in F_2^5. For the 360
unordered pairs whose larger index has bit length 5 its algebraic degree is 3
(DESIGN_NOTES.md). This script certifies, by exhaustive ANF over cd_core,
that each such phase is f = l1 l2 l3 + q with l1, l2, l3 linearly
independent linear forms and deg q <= 2, so W_ij equals
D_q U_A^dagger (CCZ x I) U_A with U_A a CNOT network and D_q a Z/CZ
diagonal. The degree-3 part takes 15 distinct values, 24 pairs each.

Three circuits implement each W_ij and are checked entry by entry,
global phase included, against diag((-1)^f), since a controlled block turns
a global sign into a relative one:

- factorized: designs.design_c_associator_spectrum's three multiplication
  blocks with the barriers between them kept, so compilation optimizes each
  block separately as the hardware circuit does, the circuit whose run tests
  composition of the factors;
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
--cross-check compares the retained file with an independent package
(docs/evidence/ccz-reduction/independent_package/, its own recursive
Cayley-Dickson product and Boolean code, standard library only), whose
retained certificates must name the same cubic part and the same three
linear forms for every pair; the package is compared as data and its
scripts are not run.
"""

from __future__ import annotations

import argparse
import hashlib
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
from designs import design_c_associator_spectrum  # noqa: E402
from predict import associator_phase  # noqa: E402
from select_lcu import phase_oracle_from_truth_table  # noqa: E402

OUT = ROOT / "docs/evidence/ccz-reduction/normal_form.json"
INDEPENDENT = ROOT / "docs/evidence/ccz-reduction/independent_package"
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


def factorized_blocks(i: int, j: int) -> QuantumCircuit:
    """Design C between its H layers: the three blocks and the two barriers that separate them."""
    full = design_c_associator_spectrum(DIM, i, j).remove_final_measurements(inplace=False)
    barriers = [k for k, inst in enumerate(full.data) if inst.operation.name == "barrier"]
    core = QuantumCircuit(N, global_phase=full.global_phase)
    for inst in full.data[barriers[0] + 1 : barriers[-1]]:
        core.append(inst.operation, [full.find_bit(q).index for q in inst.qubits])
    require(core.count_ops().get("barrier", 0) == 2, f"pair ({i}, {j}) lost its block barriers")
    return core


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
    records: list[dict[str, Any]] = []
    part_counts: Counter[frozenset[int]] = Counter()
    for i, j in pairs:
        truth_table = [1 if sign == -1 else 0 for sign in associator_phase(DIM, i, j)]
        degree = max(mask.bit_count() for mask in anf_coefficients(truth_table))
        require(degree == 3, f"pair ({i}, {j}) has degree {degree}")
        part = cubic_part(truth_table)
        require(part in forms_by_part, f"pair ({i}, {j}) cubic part is not a product of three independent forms")
        part_counts[part] += 1
        forms = forms_by_part[part]
        want = np.diag([(-1.0) ** bit for bit in truth_table])
        circuits = {
            "factorized": factorized_blocks(i, j),
            "reed_muller": phase_oracle_from_truth_table(truth_table),
            "normal_form": normal_form_circuit(truth_table, forms),
        }
        for name, circuit in circuits.items():
            deviation = float(np.max(np.abs(Operator(circuit).data - want)))
            require(deviation < 1e-9, f"pair ({i}, {j}) {name} deviates from diag((-1)^f) by {deviation:.2e}")
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
        "normal_form_below_reed_muller": {
            size: sum(
                r["cz"]["normal_form"] < r["cz"]["reed_muller"]
                for r in records
                if len(r["cubic_monomials"]) == int(size)
            )
            for size in by_size
        },
        "records": records,
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=1, sort_keys=True) + "\n"


def cross_check() -> int:
    """The retained independent package names the same cubic part and linear forms for every pair."""
    package = INDEPENDENT / "cubic_core_certificates.json"
    manifest = json.loads((INDEPENDENT / "MANIFEST.json").read_text(encoding="utf-8"))
    retention = json.loads((INDEPENDENT / "retention.json").read_text(encoding="utf-8"))
    # Every manifest entry is either retained (under its recorded .txt name for
    # the scripts, never imported or run) with its shipped sha256, or listed
    # as not shipped and absent under its manifest name.
    for name, entry in manifest.items():
        if name in retention["not_shipped"]:
            require(not (INDEPENDENT / name).exists(), f"{name} is listed as not shipped but is present")
            continue
        retained = INDEPENDENT / retention["renamed"].get(name, name)
        digest = hashlib.sha256(retained.read_bytes()).hexdigest()
        require(entry["sha256"] == digest, f"{name} differs from the package manifest")
    theirs = {(r["i"], r["j"]): r for r in json.loads(package.read_text(encoding="utf-8"))["certificates"]}
    ours = {tuple(r["pair"]): r for r in json.loads(OUT.read_text(encoding="utf-8"))["records"]}
    require(set(theirs) == set(ours) and len(ours) == 360, "the package covers other pairs")
    for pair, record in ours.items():
        cubic = sorted(m for m in theirs[pair]["f_anf_masks"] if m.bit_count() == 3)
        require(cubic == record["cubic_monomials"], f"pair {pair}: cubic part differs from the package")
        require(list(theirs[pair]["ccz_linear_form_masks"]) == record["forms"], f"pair {pair}: forms differ")
    print("independent package: 360 pairs agree on cubic part and linear forms")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--cross-check", action="store_true")
    args = parser.parse_args()
    if args.cross_check:
        return cross_check()
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
