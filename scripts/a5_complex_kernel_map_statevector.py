"""Noiseless statevector of the pathion kernel map at complex two-term operands of A_5.

The kernel map of gororoba_quantum/pathion_kernel_map.py reads the nullity N of L_(e_i + t e_j) for t = +1 and -1.
This record builds the same circuit for t in {1, -1, i, -i}: H on the five data qubits, a diagonal orientation oracle
that is +1 on the lower member k of every XOR pair {k, k XOR m} (m = i XOR j) and -t s_k (arm minus) or +t s_k (arm
plus) on the upper member, with s_k = (L_i^T L_j)[k XOR m, k] the pair sign, then H on the selector, the selector
phase t (Z for -1, S for i, S-dagger for -i), select_lcu.select_circuit(32, i, j) and H on the selector. It checks,
by exact statevector:

- at t = +1 and -1 the circuit reproduces the laws of pathion_kernel_map.kernel_map_circuit on every operand and twin
  of that module, so the generalization changes nothing the hardware record measured;
- at t = i and -i the half-sum of the output contrasts c(y) and 16 times the selector contrast both equal the exact
  nullity of L_(e_i + t e_j) over C (rank of the 64 x 64 real form), which is 16 minus the real nullity of
  e_i + e_j (ledger A5-629), on all 465 pairs of imaginary units of A_5;
- the complex circuit is the pinned real circuit with an S (or S-dagger) gate on data qubit h, the highest set bit of
  m, after the oracle and one on the selector after its first H; transpiled to the basis cz, rz, sx, x the two
  circuits have the same cz count, since S is the rotation rz(pi/2) up to a global phase;
- the oracle with plain phases +-i, without the pair sign s_k, does not read the nullity.

Independent pairs run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpz_mat
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402
from select_lcu import select_circuit  # noqa: E402

DIM = pkm.DIM
DATA = pkm.data_qubits(DIM)
HALF = DIM // 2
PHASES: dict[str, complex] = {"1": 1, "-1": -1, "i": 1j, "-i": -1j}
# Named points: e_1 + e_3 and e_1 + i e_3 (anticommuting tables), e_1 + e_26 and e_1 +- i e_26 (the slice operand).
POINTS: tuple[tuple[int, int, str], ...] = ((1, 3, "1"), (1, 3, "i"), (1, 26, "1"), (1, 26, "i"), (1, 26, "-i"))
PLAIN_POINTS: tuple[tuple[int, int, str], ...] = ((1, 3, "i"), (1, 26, "i"))
BASIS_GATES = ["cz", "rz", "sx", "x"]
# Real over complex nullity of the 465 two-term operands e_i + e_j and e_i + i e_j of A_5.
HISTOGRAM: dict[str, int] = {"0/16": 171, "12/4": 126, "4/12": 84, "8/8": 84}
EXACT = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def pair_signs(i: int, j: int) -> dict[int, int]:
    """Upper member u -> s_k for every XOR pair {k, u = k XOR m}, s_k = (L_i^T L_j)[u, k]."""
    k_matrix = pkm._k_matrix((i, j, 1), DIM)
    m = i ^ j
    return {k ^ m: int(round(k_matrix[k ^ m, k])) for k in range(DIM) if k < k ^ m}


def oracle(i: int, j: int, t: complex, plus: bool, *, plain: bool = False) -> list[complex]:
    signs = pair_signs(i, j)
    arm = 1 if plus else -1
    diagonal: list[complex] = [1.0] * DIM
    for upper, s_k in signs.items():
        diagonal[upper] = arm * t * (1 if plain else s_k)
    return diagonal


def selector_phase(qc: QuantumCircuit, t: complex) -> None:
    if t == -1:
        qc.z(DATA)
    elif t == 1j:
        qc.s(DATA)
    elif t == -1j:
        qc.sdg(DATA)
    else:
        require(t == 1, f"selector phase {t} is not a fourth root of unity")


def kernel_map(
    i: int,
    j: int,
    t: complex,
    plus: bool,
    *,
    plain: bool = False,
    oracle_flip: int | None = None,
    selector: complex | None = None,
) -> Any:
    """The kernel map without measurements; oracle_flip negates one oracle entry and selector replaces the selector
    phase (self-test only)."""
    diagonal = oracle(i, j, t, plus, plain=plain)
    if oracle_flip is not None:
        diagonal[oracle_flip] = -diagonal[oracle_flip]
    qc = QuantumCircuit(DATA + 1)
    qc.h(range(DATA))
    qc.append(DiagonalGate(diagonal), range(DATA))
    qc.h(DATA)
    selector_phase(qc, t if selector is None else selector)
    qc.compose(select_circuit(DIM, i, j), range(DATA + 1), inplace=True)
    qc.h(DATA)
    return qc


def law(qc: QuantumCircuit) -> np.ndarray:
    return np.asarray(Statevector(qc).probabilities())


def reading(i: int, j: int, t: complex, *, plain: bool = False) -> dict[str, Any]:
    minus = law(kernel_map(i, j, t, False, plain=plain))
    plus = law(kernel_map(i, j, t, True, plain=plain))
    c = pkm.output_contrast(plus, minus)
    half_sum = float(c.sum() / 2.0)
    selector = float(HALF * (pkm.selector_zero(plus) - pkm.selector_zero(minus)))
    return {
        "half_sum": int(round(half_sum)),
        "half_sum_exact": abs(half_sum - round(half_sum)) < EXACT,
        "selector": int(round(selector)),
        "selector_exact": abs(selector - round(selector)) < EXACT,
        "unit_contrasts": bool(np.allclose(np.abs(c), 1.0, atol=EXACT)),
        "p0_minus_32nds": int(round(DIM * pkm.selector_zero(minus))),
        "p0_plus_32nds": int(round(DIM * pkm.selector_zero(plus))),
        "p0_exact": all(
            abs(DIM * pkm.selector_zero(law) - round(DIM * pkm.selector_zero(law))) < EXACT for law in (minus, plus)
        ),
    }


def exact_nullity(i: int, j: int, t: complex) -> int:
    """Nullity over C of L_i + t L_j: integer rank for real t, half the nullity of the real form [[A, -sB], [sB, A]]
    for t = s i."""
    a = pkm._left(i).astype(int)
    b = pkm._left(j).astype(int)
    if t.imag == 0:
        matrix = a + int(t.real) * b
        return DIM - int(fmpz_mat(matrix.tolist()).rank())
    s = int(t.imag)
    real_form = np.block([[a, -s * b], [s * b, a]])
    rank = int(fmpz_mat(real_form.tolist()).rank())
    require(rank % 2 == 0, "the real form has odd rank")
    return (2 * DIM - rank) // 2


def tie_failures() -> dict[str, int]:
    """Laws of this builder against pathion_kernel_map.kernel_map_circuit at t = +-1, both arms."""
    operands = [*pkm.OPERANDS, *(twin for twin, _ in pkm.TWINS)]
    failures = 0
    for i, j, t in operands:
        for plus in (False, True):
            pinned = pkm.ideal_law(pkm.kernel_map_circuit((i, j, t), plus))
            failures += int(not np.allclose(law(kernel_map(i, j, t, plus)), pinned, atol=1e-12))
    return {"operands": len(operands), "laws": 2 * len(operands), "failures": failures}


def s_form(i: int, j: int, t: complex, plus: bool, *, qubit: int | None = None) -> Any:
    """The pinned template of e_i + e_j with S (t = i) or S-dagger (t = -i) inserted on data qubit h after the oracle
    and on the selector after its first H; qubit moves the data-side gate (self-test only)."""
    template = pkm.kernel_map_template((i, j, 1), measure=False)
    target = pkm.upper_bit((i, j, 1)) if qubit is None else qubit
    out = QuantumCircuit(*template.qregs)
    selector_done = False
    for instruction in template.data:
        out.append(instruction.operation, instruction.qubits, instruction.clbits)
        indices = [template.find_bit(q).index for q in instruction.qubits]
        if instruction.operation.name == "diagonal" and len(indices) == DATA:
            (out.s if t == 1j else out.sdg)(target)
        if instruction.operation.name == "h" and indices == [DATA] and not selector_done:
            selector_done = True
            (out.s if t == 1j else out.sdg)(DATA)
    return out.assign_parameters({pkm.ORIENTATION: np.pi if plus else 0.0})


def s_form_row(i: int, j: int, t: complex) -> dict[str, Any]:
    equivalent = all(
        Statevector(s_form(i, j, t, plus)).equiv(Statevector(kernel_map(i, j, t, plus))) for plus in (False, True)
    )
    real = transpile(pkm.kernel_map_circuit((i, j, 1), False), basis_gates=BASIS_GATES, optimization_level=1)
    complex_ = s_form(i, j, t, False)
    complex_.measure_all()
    compiled = transpile(complex_, basis_gates=BASIS_GATES, optimization_level=1)
    return {
        "equivalent": equivalent,
        "cz_real": int(real.count_ops().get("cz", 0)),
        "cz_complex": int(compiled.count_ops().get("cz", 0)),
    }


def pair_item(pair: tuple[int, int]) -> dict[str, Any]:
    i, j = pair
    real = exact_nullity(i, j, 1)
    row: dict[str, Any] = {"pair": [i, j], "real_nullity": real, "real_circuit": reading(i, j, 1)}
    row["s_form_equivalent"] = all(
        Statevector(s_form(i, j, t, plus)).equiv(Statevector(kernel_map(i, j, t, plus)))
        for t in (1j, -1j)
        for plus in (False, True)
    )
    for label in ("i", "-i"):
        row[f"nullity_{label}"] = exact_nullity(i, j, PHASES[label])
        row[f"circuit_{label}"] = reading(i, j, PHASES[label])
    return row


def all_pairs() -> dict[str, Any]:
    rows = parallel.ordered_map(pair_item, list(combinations(range(1, DIM), 2)), min_items=1)
    failures = []
    histogram: Counter[str] = Counter()
    for row in rows:
        histogram[f"{row['real_nullity']}/{row['nullity_i']}"] += 1
        checks = [
            row["real_circuit"]["half_sum"] == row["real_nullity"],
            row["nullity_i"] == row["nullity_-i"] == HALF - row["real_nullity"],
        ]
        for label in ("real_circuit", "circuit_i", "circuit_-i"):
            reading_row = row[label]
            expected = row["real_nullity"] if label == "real_circuit" else row["nullity_i"]
            checks += [
                reading_row["half_sum"] == reading_row["selector"] == expected,
                reading_row["half_sum_exact"] and reading_row["selector_exact"] and reading_row["unit_contrasts"],
            ]
        checks.append(row["s_form_equivalent"])
        if not all(checks):
            failures.append(row["pair"])
    return {
        "pairs": len(rows),
        "failures": failures,
        "real_over_complex_nullity": dict(sorted(histogram.items())),
    }


def section_item(task: tuple[str, tuple[int, int, str]]) -> dict[str, Any]:
    """One named point, pinned-module operand, plain-phase control or S-form comparison."""
    kind, (i, j, label) = task
    t = PHASES[label]
    if kind == "point":
        return {"nullity": exact_nullity(i, j, t), **reading(i, j, t)}
    if kind == "operand":
        return {
            "real_nullity": exact_nullity(i, j, t),
            "nullity_i": exact_nullity(i, j, 1j),
            "circuit_i": reading(i, j, 1j)["half_sum"],
        }
    if kind == "plain":
        return reading(i, j, t, plain=True)
    return s_form_row(i, j, t)


def compute() -> dict[str, Any]:
    tasks: list[tuple[str, tuple[int, int, str]]] = [("point", spec) for spec in POINTS]
    tasks += [("operand", (i, j, str(t))) for i, j, t in pkm.OPERANDS]
    tasks += [("plain", spec) for spec in PLAIN_POINTS]
    tasks += [("s_form", spec) for spec in POINTS if spec[2] != "1"]
    rows = parallel.ordered_map(section_item, tasks, min_items=1)
    by_kind: dict[str, dict[str, Any]] = {kind: {} for kind in ("point", "operand", "plain", "s_form")}
    for (kind, (i, j, label)), row in zip(tasks, rows, strict=True):
        key = pkm.operand_tag((i, j, int(label))) if kind == "operand" else f"e{i}+({label})e{j}"
        by_kind[kind][key] = row
    return {
        "all_pairs": all_pairs(),
        "operands_at_i": by_kind["operand"],
        "plain_phase_control": by_kind["plain"],
        "points": by_kind["point"],
        "s_form": by_kind["s_form"],
        "tie_to_pinned_module": tie_failures(),
    }


def validate(result: dict[str, Any]) -> None:
    tie = result["tie_to_pinned_module"]
    require(tie == {"operands": 8, "laws": 16, "failures": 0}, f"tie to the pinned module: {tie}")
    expected = {"e1+(1)e3": 0, "e1+(i)e3": 16, "e1+(1)e26": 4, "e1+(i)e26": 12, "e1+(-i)e26": 12}
    for name, nullity in expected.items():
        row = result["points"][name]
        require(row["nullity"] == row["half_sum"] == row["selector"] == nullity, f"{name}: {row}")
        require(row["half_sum_exact"] and row["selector_exact"] and row["unit_contrasts"], f"{name}: inexact")
    readings = [row["circuit_i"] for row in result["operands_at_i"].values()]
    require(readings == [16, 12, 12, 8, 4, 4], f"operands at t = i: {readings}")
    for row in result["operands_at_i"].values():
        require(row["nullity_i"] == row["circuit_i"] == HALF - row["real_nullity"], f"operand row {row}")
    p0 = {name: (row["p0_minus_32nds"], row["p0_plus_32nds"]) for name, row in result["points"].items()}
    require(p0["e1+(i)e3"] == (0, 32) and p0["e1+(i)e26"] == (4, 28), f"selector marginals {p0}")
    require(all(row["p0_exact"] for row in result["points"].values()), "selector marginals off the 1/32 grid")
    cz = {name: (row["cz_real"], row["cz_complex"]) for name, row in result["s_form"].items()}
    require(cz == {"e1+(i)e3": (91, 91), "e1+(i)e26": (96, 96), "e1+(-i)e26": (96, 96)}, f"cz counts {cz}")
    plain = result["plain_phase_control"]
    require(plain["e1+(i)e3"]["half_sum"] == -14 and plain["e1+(i)e26"]["half_sum"] == -2, f"plain control: {plain}")
    pairs = result["all_pairs"]
    require(pairs["pairs"] == 465 and pairs["failures"] == [], f"all pairs: {pairs['failures'][:5]}")
    require(pairs["real_over_complex_nullity"] == HISTOGRAM, f"histogram {pairs['real_over_complex_nullity']}")
    for name, row in result["s_form"].items():
        require(row["equivalent"] and row["cz_real"] == row["cz_complex"] > 0, f"S form {name}: {row}")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    true_n = exact_nullity(1, 26, 1j)
    control(reading(1, 26, 1j)["half_sum"] == true_n, reading(1, 26, 1j, plain=True)["half_sum"] == true_n, "s_k")

    def selector_reading(selector: complex) -> float:
        minus = law(kernel_map(1, 26, 1j, False, selector=selector))
        plus = law(kernel_map(1, 26, 1j, True, selector=selector))
        return float(pkm.output_contrast(plus, minus).sum() / 2.0)

    control(abs(selector_reading(1j) - true_n) < EXACT, abs(selector_reading(-1) - true_n) < EXACT, "selector phase")
    pinned = pkm.ideal_law(pkm.kernel_map_circuit((1, 18, 1), True))
    control(
        bool(np.allclose(law(kernel_map(1, 18, 1, True)), pinned, atol=1e-12)),
        bool(np.allclose(law(kernel_map(1, 18, 1, True, oracle_flip=pair_upper(1, 18))), pinned, atol=1e-12)),
        "tie to the pinned module",
    )
    direct = Statevector(kernel_map(1, 26, 1j, True))
    h = pkm.upper_bit((1, 26, 1))
    control(
        Statevector(s_form(1, 26, 1j, True)).equiv(direct),
        Statevector(s_form(1, 26, 1j, True, qubit=(h + 1) % DATA)).equiv(direct),
        "S on qubit h",
    )
    a = pkm._left(1).astype(int)
    b = pkm._left(26).astype(int)
    swapped = DIM - int(fmpz_mat(np.block([[a, b], [b, a]]).tolist()).rank()) // 2
    control(true_n == 12, swapped == 12, "real form")


def pair_upper(i: int, j: int) -> int:
    return min(pair_signs(i, j))


def dumps(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 5 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = dumps(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
