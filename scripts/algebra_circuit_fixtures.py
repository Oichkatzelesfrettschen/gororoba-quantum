"""Regression fixtures for the algebra circuit design rules, run on the repository's own circuit builders.

Each fixture binds one rule of the gororoba_quantum/AGENTS.md algebra circuit design rules to
the code that a hardware case would compile:

1. Zero-product witnesses. cd_core gives (e1 + e10)(e2 - e13) = e3 + e7 + e8
   - e12 and (e1 + e10)(e4 - e15) = 0. designs.lcu_witness, Design B's circuit,
   gives P(s = 0) = ||x y||^2 / 2: 1/2 for the proposed pair, 0 for the dark
   pair and 1 for the bright pair (e4 + e15).
2. Hadamard-test basis. With W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j) built
   from designs.left_mult_gate and designs.left_mult_adjoint_gate and
   controlled on one qubit, <Z_c> after the final H and <X_c> before it equal
   omega(i, j, k) on |k>, while <X_c> after the final H is 0.
3. Workspace cleanup. An extra register that one branch marks with an XOR
   suppresses the interference (visibility 0); undoing the XOR restores
   omega(i, j, k).
4. Package convention. SageMath 10.10's OctonionAlgebra(QQ) in its natural
   basis order 1, i, j, k, l, li, lj, lk is the opposite algebra of
   cd_core at D = 8, x *_Sage y = y *_cd x on every basis pair; flipping the
   signs of e3, e5 and e6 is an isomorphism; 1344 signed relabelings realize
   each relation. The table is the retained export
   docs/evidence/algebra_packages/sagemath_octonion_table.json.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402

SAGE_TABLE = ROOT / "docs/evidence/algebra_packages/sagemath_octonion_table.json"
TOL = 1e-10


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def product(dim: int, x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for p, a in x.items():
        for q, b in y.items():
            out[p ^ q] = out.get(p ^ q, 0) + cd_sign(dim, p, q) * a * b
    return {k: v for k, v in out.items() if v}


def omega(dim: int, i: int, j: int, k: int) -> int:
    return cd_sign(dim, i, j) * cd_sign(dim, i ^ j, k) * cd_sign(dim, j, k) * cd_sign(dim, i, j ^ k)


def zero_products() -> None:
    from qiskit.quantum_info import Statevector

    from designs import lcu_witness

    require(product(16, {1: 1, 10: 1}, {2: 1, 13: -1}) == {3: 1, 7: 1, 8: 1, 12: -1}, "proposed pair is nonzero")
    require(product(16, {1: 1, 10: 1}, {4: 1, 15: -1}) == {}, "corpus pair is a zero product")
    for partner, phase, expected in (((2, 13), math.pi, 0.5), ((4, 15), math.pi, 0.0), ((4, 15), 0.0, 1.0)):
        circuit = lcu_witness((1, 10), partner, phase).remove_final_measurements(inplace=False)
        p0 = float(Statevector(circuit).probabilities([4])[0])
        require(abs(p0 - expected) < TOL, f"Design B P(s=0) for partner {partner}, phase {phase}: {p0}")


def hadamard_test(i: int, j: int, k: int, *, leak: bool, cleanup: bool) -> dict[str, float]:
    """<Z_c> after the final H, <X_c> before it, and <X_c> after it, for controlled W_ij on |k>."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp, Statevector

    from designs import left_mult_adjoint_gate, left_mult_gate

    data, work, control = range(4), range(4, 8), 8
    w = QuantumCircuit(4)
    w.append(left_mult_gate(16, j), range(4))
    w.append(left_mult_gate(16, i), range(4))
    w.append(left_mult_adjoint_gate(16, i ^ j), range(4))
    if cd_sign(16, i, j) < 0:
        w.global_phase += math.pi
    circuit = QuantumCircuit(9)
    for bit in range(4):
        if (k >> bit) & 1:
            circuit.x(bit)
    circuit.h(control)
    circuit.append(w.to_gate().control(1), [control, *data])
    if leak:
        for bit in range(4):
            if ((i ^ j) >> bit) & 1:
                circuit.cx(control, work[bit])
        if cleanup:
            for bit in range(4):
                if ((i ^ j) >> bit) & 1:
                    circuit.cx(control, work[bit])
    before = Statevector(circuit)
    circuit.h(control)
    after = Statevector(circuit)

    def expect(state: Statevector, label: str) -> float:
        op = SparsePauliOp.from_sparse_list([(label, [control], 1.0)], num_qubits=9)
        return float(np.real(state.expectation_value(op)))

    return {"z_after": expect(after, "Z"), "x_before": expect(before, "X"), "x_after": expect(after, "X")}


def measurement_basis_and_workspace() -> int:
    checked = 0
    for i, j, k in ((1, 2, 4), (1, 2, 3), (3, 5, 9), (1, 10, 4)):
        w = omega(16, i, j, k)
        clean = hadamard_test(i, j, k, leak=False, cleanup=False)
        require(abs(clean["z_after"] - w) < TOL and abs(clean["x_before"] - w) < TOL, f"({i},{j},{k}): Hadamard test")
        require(abs(clean["x_after"]) < TOL, f"({i},{j},{k}): X after the final H reads zero")
        leaked = hadamard_test(i, j, k, leak=True, cleanup=False)
        require(abs(leaked["z_after"]) < TOL, f"({i},{j},{k}): branch-marked workspace kills the visibility")
        restored = hadamard_test(i, j, k, leak=True, cleanup=True)
        require(abs(restored["z_after"] - w) < TOL, f"({i},{j},{k}): cleanup restores omega")
        checked += 1
    require(omega(16, 1, 2, 4) == -1, "the audit's example triple does not associate")
    return checked


def sage_convention() -> dict[str, int]:
    record = json.loads(SAGE_TABLE.read_text(encoding="utf-8"))
    require(record["basis"] == ["1", "i", "j", "k", "l", "li", "lj", "lk"], "Sage basis order")
    table: dict[tuple[int, int], tuple[int, int]] = {}
    for a in range(8):
        for b in range(8):
            row = record["table"][a][b]
            nonzero = [n for n, c in enumerate(row) if c]
            require(len(nonzero) == 1 and abs(row[nonzero[0]]) == 1, "Sage basis product is a signed basis element")
            table[(a, b)] = (row[nonzero[0]], nonzero[0])
    for a in range(8):
        for b in range(8):
            require(table[(a, b)] == (cd_sign(8, b, a), a ^ b), f"Sage e{a} e{b} is cd_core e{b} e{a}")
    flip = (1, 1, 1, -1, 1, -1, -1, 1)
    for a in range(8):
        for b in range(8):
            sign, index = table[(a, b)]
            require(
                sign * flip[a] * flip[b] == cd_sign(8, a, b) * flip[a ^ b] and index == a ^ b, "sign-flip isomorphism"
            )
    counts = {"isomorphisms": 0, "anti_isomorphisms": 0}
    for perm in itertools.permutations(range(1, 8)):
        p = (0, *perm)
        for signs in itertools.product((1, -1), repeat=7):
            s = (1, *signs)
            for kind in counts:
                ok = True
                for a in range(1, 8):
                    for b in range(1, 8):
                        x, y = (a, b) if kind == "isomorphisms" else (b, a)
                        sign, index = table[(p[a], p[b])]
                        if index != p[a ^ b] or sign * s[a] * s[b] != cd_sign(8, x, y) * s[a ^ b]:
                            ok = False
                            break
                    if not ok:
                        break
                counts[kind] += ok
    require(counts == {"isomorphisms": 1344, "anti_isomorphisms": 1344}, f"signed relabeling counts {counts}")
    return counts


def main() -> int:
    zero_products()
    checked = measurement_basis_and_workspace()
    counts = sage_convention()
    print(
        f"algebra circuit fixtures: Design B 1/2, 0, 1; {checked} Hadamard tests with basis and workspace controls; "
        f"Sage octonions are the opposite of cd_core ({counts['anti_isomorphisms']} anti, {counts['isomorphisms']} iso)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
