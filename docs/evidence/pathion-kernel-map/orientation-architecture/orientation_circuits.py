"""Circuit side of the orientation-architecture analysis: stage ledger, merged-diagonal synthesis, layout search.

The retained group (gororoba_quantum/pathion_kernel_map_orientation.py) builds each member as H on the five data
qubits, a five-qubit oracle diagonal, a phase on the orientation qubit, H on the selector, a six-qubit SELECT diagonal,
an X layer, a CX fan from the selector, an optional X, H on the selector and the measurement. This module

- counts the CZ of each stage, logical and routed (ledger);
- builds the same operator with the oracle, the orientation phase and the SELECT sign merged into one six-qubit
  diagonal (merged_template) and proves operator equality with the retained member on both arms;
- compiles every assignment of the six logical qubits onto a six-qubit heavy-hex tile (layout search).

Compile calls take a Target through live_run.build_admission_target, so a recompute needs the network (the Target) and
is run by orientation_architecture.py --recompute-circuits; the retained circuits.json carries its results.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Operator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import pathion_kernel_map as pkm  # noqa: E402
import pathion_kernel_map_orientation as pko  # noqa: E402
from select_lcu import joint_select_signs  # noqa: E402

BASIS = ["cz", "rz", "sx", "x"]
ROLES = pko.ROLES
OPERANDS = pko.OPERANDS
STAGES = (
    "h_layer",
    "oracle_diagonal",
    "orientation_and_selector_phase",
    "select_diagonal",
    "select_x_layer",
    "select_cx_fan",
    "exchange_x",
    "final_h",
)


def member_name(role: str, operand: tuple[int, int, int], plus: bool = True) -> str:
    return f"kmo_{role}_{pkm.operand_tag(operand)}_{'plus' if plus else 'minus'}"


def merged_template(role: str, operand: tuple[int, int, int], *, measure: bool = True) -> QuantumCircuit:
    """role_template with the oracle diagonal folded into the SELECT diagonal (one six-qubit DiagonalGate).

    The oracle acts on the data qubits only, so it commutes with the selector's H and with the phase on the orientation
    qubit and joins the SELECT diagonal that follows: signs(x, a) = oracle(x) * select(x, a)."""
    i, j, t = operand
    orientation_bit, exchange_bit = pko.role_options(role, operand)
    data = pkm.DATA
    oracle = pko.orientation_signs(operand, False, orientation_bit)
    select = joint_select_signs(pkm.DIM, i, j)
    merged = [select[z] * oracle[z % pkm.DIM] for z in range(2 * pkm.DIM)]
    qc = QuantumCircuit(data + 1, data + 1 if measure else 0)
    qc.h(range(data))
    qc.p(pkm.ORIENTATION, orientation_bit)
    qc.h(data)
    if t < 0:
        qc.z(data)
    qc.append(DiagonalGate(merged), range(data + 1))
    for b in range(data):
        if i >> b & 1:
            qc.x(b)
    for b in range(data):
        if (i ^ j) >> b & 1:
            qc.cx(data, b)
    if exchange_bit is not None:
        qc.x(exchange_bit)
    qc.h(data)
    if role == "swap":
        perm = list(range(data + 1))
        a, b = pko.SWAP_WIRES
        perm[a], perm[b] = b, a
        swapped = QuantumCircuit(data + 1, data + 1 if measure else 0)
        swapped.compose(qc, qubits=perm, inplace=True)
        qc = swapped
        if measure:
            for q in range(data + 1):
                qc.measure(perm[q], q)
        return qc
    if measure:
        qc.measure(range(data + 1), range(data + 1))
    return qc


def unitary_part(qc: QuantumCircuit) -> QuantumCircuit:
    return qc.remove_final_measurements(inplace=False)


def operator_equal(a: QuantumCircuit, b: QuantumCircuit, plus: bool) -> bool:
    """Equality of two members' unitaries on one arm up to a global phase."""
    phase = np.pi if plus else 0.0
    ua = Operator(unitary_part(a.assign_parameters({pkm.ORIENTATION: phase}))).data
    ub = Operator(unitary_part(b.assign_parameters({pkm.ORIENTATION: phase}))).data
    k = int(np.argmax(np.abs(ub)))
    scale = ua.flat[k] / ub.flat[k]
    return bool(abs(abs(scale) - 1.0) < 1e-9 and np.allclose(ua, scale * ub, atol=1e-9))


def stage_of(qc: QuantumCircuit) -> list[str]:
    """Stage label of every non-measure instruction of a retained member, from the build order of
    pko.kernel_map_template (the labels follow the gate sequence, not the qubit wires)."""
    labels: list[str] = []
    seen_diagonals = 0
    for inst in qc.data:
        name = inst.operation.name
        if name == "measure":
            continue
        if name == "diagonal":
            seen_diagonals += 1
            labels.append("oracle_diagonal" if seen_diagonals == 1 else "select_diagonal")
        elif seen_diagonals == 0:
            labels.append("h_layer")
        elif seen_diagonals == 1:
            labels.append("orientation_and_selector_phase")
        else:
            labels.append("?")
    # after the select diagonal: x layer, cx fan, optional exchange x, final h
    out: list[str] = []
    after = False
    cx_seen = False
    for label, inst in zip(labels, [i for i in qc.data if i.operation.name != "measure"], strict=True):
        name = inst.operation.name
        if label == "select_diagonal":
            after = True
            out.append(label)
        elif after:
            if name == "x" and not cx_seen:
                out.append("select_x_layer")
            elif name == "cx":
                cx_seen = True
                out.append("select_cx_fan")
            elif name == "x":
                out.append("exchange_x")
            else:
                out.append("final_h")
        else:
            out.append(label)
    return out


def prefix(qc: QuantumCircuit, labels: list[str], upto: str) -> QuantumCircuit:
    """The first instructions of qc through the last instruction of stage upto (no measurement)."""
    last = max(k for k, label in enumerate(labels) if STAGES.index(label) <= STAGES.index(upto))
    out = QuantumCircuit(qc.num_qubits)
    body = [i for i in qc.data if i.operation.name != "measure"]
    for inst in body[: last + 1]:
        out.append(inst.operation, [qc.find_bit(q).index for q in inst.qubits])
    return out


def cz(qc: QuantumCircuit) -> int:
    return int(qc.count_ops().get("cz", 0))


def logical_cz(qc: QuantumCircuit) -> int:
    """CZ of the circuit with all-to-all connectivity at optimization level 1 (a5-complex-kernel-map statement 5)."""
    return cz(transpile(qc, basis_gates=BASIS, optimization_level=1))


def logical_ledger(role: str, operand: tuple[int, int, int]) -> dict[str, Any]:
    qc = pko.role_template(role, operand)
    labels = stage_of(qc)
    marginal: dict[str, int] = {}
    previous = 0
    for stage in STAGES:
        if stage not in labels:
            marginal[stage] = 0
            continue
        total = logical_cz(prefix(qc, labels, stage))
        marginal[stage] = total - previous
        previous = total
    return {"total": logical_cz(qc), "marginal": marginal}


def merged_logical(role: str, operand: tuple[int, int, int]) -> int:
    return logical_cz(merged_template(role, operand))


class Compile:
    """Picklable compile job: one template, one layout, one seed, one Target."""

    def __init__(self, target: Any, templates: dict[str, QuantumCircuit], seed: int) -> None:
        self.target = target
        self.templates = templates
        self.seed = seed

    def __call__(self, item: tuple[str, tuple[int, ...]]) -> int:
        name, layout = item
        isa = transpile(
            self.templates[name],
            target=self.target,
            optimization_level=3,
            seed_transpiler=self.seed,
            initial_layout=list(layout),
        )
        return cz(isa)


def all_templates(kind: str) -> dict[str, QuantumCircuit]:
    """Templates of the eight units (role x operand): kind retained, merged or sparse."""
    out: dict[str, QuantumCircuit] = {}
    for role in ROLES:
        for operand in OPERANDS:
            name = f"{role}_{pkm.operand_tag(operand)}"
            out[name] = {"retained": pko.role_template, "merged": merged_template, "sparse": sparse_template}[kind](
                role, operand
            )
    return out


def assignments() -> list[tuple[int, ...]]:
    return list(itertools.permutations(range(6)))


# ----------------------------------------------------------------------------------------------- coset blocks
import pathion_coset_block as pcb  # noqa: E402


def block_law_bit(block: Any, bit: int, plus: bool) -> np.ndarray:
    """Closed-form block law with the pairs split by algebra bit `bit` (pathion_coset_block's law has bit h only)."""
    i, j, t = block.operand
    labels = pcb.input_labels(block)
    orientation = pko.orientation_signs(block.operand, plus, bit)
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels]) * (-1.0 if t < 0 else 1.0)
    psi = np.array([orientation[k] for k in labels]) * f0 / np.sqrt(float(1 << block.d))
    low = psi / np.sqrt(2.0)
    high = (psi * f0 * f1 / np.sqrt(2.0))[np.arange(1 << block.d) ^ 1]
    return np.concatenate([(low + high) / np.sqrt(2.0), (low - high) / np.sqrt(2.0)])


def block_template_bit(block: Any, bit: int, *, measure: bool = True) -> QuantumCircuit:
    """pathion_coset_block.block_template with the orientation phase on the data qubits that carry algebra bit `bit`."""
    i, j, t = block.operand
    d = block.d
    labels = pcb.input_labels(block)
    orientation = pko.orientation_signs(block.operand, False, bit)
    signs = joint_select_signs(block.dim, i, j)
    f0 = np.array([signs[k] for k in labels])
    f1 = np.array([signs[k + block.dim] for k in labels]) * (-1.0 if t < 0 else 1.0)
    qc = QuantumCircuit(d + 1, d + 1 if measure else 0)
    qc.h(range(d))
    qc.append(DiagonalGate(list(np.array([orientation[k] for k in labels]) * f0)), range(d))
    for c, vector in enumerate(block.basis):
        if vector >> bit & 1:
            qc.p(pkm.ORIENTATION, c)
    qc.h(d)
    qc.append(DiagonalGate([1.0] * (1 << d) + list(f0 * f1)), range(d + 1))
    qc.cx(d, 0)
    qc.h(d)
    if measure:
        qc.measure(range(d + 1), range(d + 1))
    return qc


def walsh(values: np.ndarray) -> np.ndarray:
    n = len(values)
    return np.array([sum(values[y] * (-1) ** bin(s & y).count("1") for y in range(n)) / n for s in range(n)])


def character_mask(block: Any, bit: int) -> int:
    """Output character of algebra bit `bit`: the parity over the block qubits whose basis vector carries it."""
    return sum(1 << c for c, v in enumerate(block.basis) if v >> bit & 1)


def contrast(plus: np.ndarray, minus: np.ndarray) -> np.ndarray:
    half = len(plus) // 2

    def cond(law: np.ndarray) -> np.ndarray:
        total = law[:half] + law[half:]
        return np.divide(law[:half], total, out=np.zeros(half), where=total > 1e-12)

    return cond(plus) - cond(minus)


def coset_funnel(operand: tuple[int, int, int], moved_bit: int = pko.MOVED_BIT, tol: float = 1e-9) -> dict[str, Any]:
    """Exact statevector funnel of the orientation-bit statistics over every 3-dimensional block that contains m.

    Per block (coset of a subspace V with basis m, a, b): the retained unit splits pairs by the highest bit h of m,
    the moved unit by `moved_bit`. A block keeps a statistic when the Walsh coefficient of its per-output contrast
    at the character of that bit is nonzero (A ctrl, B moved without the retained character), the two characters differ
    (C), the zero character is nonzero in both (D), and the (zero, signature) magnitudes agree between the units (E)."""
    i, j, _ = operand
    m = i ^ j
    h = pkm.upper_bit(operand)
    seen: set[frozenset[int]] = set()
    funnel = {
        "blocks": 0,
        "A_ctrl_signature": 0,
        "B_moved_signature_no_leak": 0,
        "C_characters_distinct": 0,
        "D_zero_character": 0,
        "E_weights_match": 0,
    }
    survivors: list[dict[str, Any]] = []
    for a in range(1, pkm.DIM):
        for b in range(a + 1, pkm.DIM):
            space = frozenset(pcb.span((m, a, b)))
            if len(space) != 8 or space in seen:
                continue
            seen.add(space)
            basis = (m, a, b)
            for k0 in pcb.cosets(basis):
                block = pcb.Block("b", operand, basis, k0)
                cc = contrast(block_law_bit(block, h, True), block_law_bit(block, h, False))
                cm = contrast(block_law_bit(block, moved_bit, True), block_law_bit(block, moved_bit, False))
                wc, wm = walsh(cc), walsh(cm)
                sh, sb = character_mask(block, h), character_mask(block, moved_bit)
                funnel["blocks"] += 1
                ka = abs(wc[sh]) > tol
                kb = ka and abs(wm[sb]) > tol and abs(wm[sh]) < tol
                kc = kb and sh != sb
                kd = kc and abs(wc[0]) > tol and abs(wm[0]) > tol
                ke = kd and abs(abs(wc[0]) - abs(wm[0])) < tol and abs(abs(wc[sh]) - abs(wm[sb])) < tol
                funnel["A_ctrl_signature"] += int(ka)
                funnel["B_moved_signature_no_leak"] += int(kb)
                funnel["C_characters_distinct"] += int(kc)
                funnel["D_zero_character"] += int(kd)
                funnel["E_weights_match"] += int(ke)
                if kd:
                    survivors.append(
                        {
                            "basis": list(basis),
                            "coset": k0,
                            "weight_matched": bool(ke),
                            "sixteen_in_V": 16 in space,
                            "coefficients_ctrl_0_sig": [float(wc[0]), float(wc[sh])],
                            "coefficients_move_0_sig": [float(wm[0]), float(wm[sb])],
                        }
                    )
    return {"funnel": funnel, "survivors": survivors}


# ------------------------------------------------------------------------------------- sparse phase polynomial
def phase_polynomial(signs: list[float]) -> dict[int, float]:
    """Rotation angle phi_S of every nonzero parity S of diag(signs): exp(i sum_S phi_S parity_S(x)), up to a phase."""
    n = len(signs)
    theta = np.array([0.0 if s > 0 else np.pi for s in signs])
    h = theta.copy()
    step = 1
    while step < n:
        for i in range(0, n, 2 * step):
            a = h[i : i + step].copy()
            b = h[i + step : i + 2 * step].copy()
            h[i : i + step] = a + b
            h[i + step : i + 2 * step] = a - b
        step *= 2
    h /= n
    return {s: float(-2.0 * h[s]) for s in range(1, n) if abs(h[s]) > 1e-12}


def sparse_diagonal(signs: list[float], qubits: int) -> QuantumCircuit:
    """The diagonal as a CX network that visits only the parities of its phase polynomial (the DiagonalGate visits
    all 2^n - 1). Parities group by their highest qubit q; one group runs with q as the CX target, parities ordered
    greedily by Hamming distance, and returns the target to x_q."""
    poly = phase_polynomial(signs)
    qc = QuantumCircuit(qubits)
    for q in range(qubits):
        group = [s for s in poly if s.bit_length() - 1 == q]
        if not group:
            continue
        current = 1 << q
        remaining = sorted(group)
        while remaining:
            nxt = min(remaining, key=lambda s: (bin(s ^ current).count("1"), s))
            remaining.remove(nxt)
            for c in range(qubits):
                if c != q and (nxt ^ current) >> c & 1:
                    qc.cx(c, q)
            current = nxt
            qc.p(poly[nxt], q)
        for c in range(qubits):
            if c != q and (current ^ (1 << q)) >> c & 1:
                qc.cx(c, q)
    return qc


def sparse_template(role: str, operand: tuple[int, int, int], *, measure: bool = True) -> QuantumCircuit:
    """merged_template with the six-qubit DiagonalGate replaced by sparse_diagonal."""
    i, j, t = operand
    orientation_bit, exchange_bit = pko.role_options(role, operand)
    data = pkm.DATA
    oracle = pko.orientation_signs(operand, False, orientation_bit)
    select = joint_select_signs(pkm.DIM, i, j)
    merged = [select[z] * oracle[z % pkm.DIM] for z in range(2 * pkm.DIM)]
    qc = QuantumCircuit(data + 1, data + 1 if measure else 0)
    qc.h(range(data))
    qc.p(pkm.ORIENTATION, orientation_bit)
    qc.h(data)
    if t < 0:
        qc.z(data)
    qc.compose(sparse_diagonal(merged, data + 1), range(data + 1), inplace=True)
    for b in range(data):
        if i >> b & 1:
            qc.x(b)
    for b in range(data):
        if (i ^ j) >> b & 1:
            qc.cx(data, b)
    if exchange_bit is not None:
        qc.x(exchange_bit)
    qc.h(data)
    if role == "swap":
        perm = list(range(data + 1))
        a, b = pko.SWAP_WIRES
        perm[a], perm[b] = b, a
        swapped = QuantumCircuit(data + 1, data + 1 if measure else 0)
        swapped.compose(qc, qubits=perm, inplace=True)
        qc = swapped
        if measure:
            for q in range(data + 1):
                qc.measure(perm[q], q)
        return qc
    if measure:
        qc.measure(range(data + 1), range(data + 1))
    return qc
