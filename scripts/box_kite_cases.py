"""Box-kite zero-product cases for Quantum Inspire, generated from the retained box-kite census.

Family (a) of docs/notes/box_kites/experiment-program.md on the QX emulator:
every Design B row of docs/evidence/box_kite_census/census.json (840
within-kite rows, 168 cross-kite controls with the negative fixture
(1,10)+ x (2,13)-, 168 ordered (l, l^8) pairs) in two encodings, each read
through the selector's success outcome P(selector = 0) (root AGENTS.md,
"Zero-product witnesses").

- Full Design B (5 qubits, data 0-3 and selector 4) wraps
  designs.lcu_witness: (L_{e_L} + L_{e_U})/2 on y = (e_L' + y_sign e_U')/sqrt2,
  and x_sign = -1 adds a Z on the selector after its first H. Its ideal is
  P = ||x y||^2 / 2, the census column p_selector_zero.
- Reduced two-label LCU (2 qubits, selector a and data d). The four product
  terms of a two-label row land on L^L' (d = 0) and L^U' (d = 1), so SELECT is
  the diagonal g(L,L'), g(L,U') on a = 0 and g(U,L'), g(U,U') on a = 1 over the
  input d, then CNOT(a -> d). The phases come from the census row,
  g(L,L') = (c0 + d0)/2, g(U,U') = s t (c0 - d0)/2, g(L,U') = t (c1 + d1)/2 and
  g(U,L') = s (c1 - d1)/2 for x_sign s and y_sign t, since c0 = g(L,L') +
  s t g(U,U'), c1 = t g(L,U') + s g(U,L') and d0, d1 the differences. x_sign
  enters once, as the selector Z. A diagonal with phase product +1 (every
  edge) is local Z gates and SELECT is one CNOT; product -1 (every strut) adds
  CZ, and CNOT CZ = Sdag(a) (S(d) CNOT Sdag(d)) keeps one two-qubit gate.
- Reduced cross-kite control (3 qubits, a, d and w). Four distinct labels make
  the branches orthogonal, so CNOT(a -> w) marks them and P = 1/2 for every
  sign; the census carries no phases for four-label rows, so the diagonal is
  the identity and the circuit depends on (x_sign, y_sign) alone.

The generator reads every sign from census.json and recomputes none from
cd_core. validate_census requires each two-label row's four phases to lie in
{+1, -1}, to agree over the four sign rows of an ordered pair, to give the
kite's edge or strut sign products, and to reproduce P, 1 - P and both
post-selected coherences. Before emission every full Design B replica must
reproduce its census amplitudes c0, c1, d0, d1 / (2 sqrt2) (the
designs.lcu_witness state, built on cd_core, against the census), every
reduced SELECT must equal its two-label restriction as a unitary, and every
emitted cQASM file is parsed back and simulated by state vector: each packed
replica's selector marginal must equal its census P. A mismatch raises.

QX serves 10 qubits, so pack() places two full replicas (slots 0-4, 5-9),
five reduced replicas or three cross-kite replicas per circuit. A batch holds
at most qi_platform.HARDWARE_BATCH_CIRCUITS circuits, the cap every retained
case directory meets, and batches never mix sub-families. Full Design B
compiles at optimization level 0 to H, X, Z, S, Sdag, Rz and CNOT; each Rz
angle snaps to a multiple of pi/64 and prints from that integer, so the
emitted bytes do not depend on the host's floating-point library. Bit strings
put qubit 0 at the rightmost character (QX).

--write DIR writes DIR/box_kite_a_qx/ (batch-NNN/ cases and the series
cases.json); --check DIR regenerates in memory and compares file sets and
bytes; --self-test requires census, circuit, packing and manifest mutations
to be rejected.

Usage: "$PYTHON" scripts/box_kite_cases.py (--write DIR | --check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS, declared_qubits  # noqa: E402
from qi_zero_divisor_cases import header  # noqa: E402

import parallel  # noqa: E402

CENSUS = ROOT / "docs/evidence/box_kite_census/census.json"
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
CENSUS_SCHEMA = "box-kite-census-v1"
CASES_SCHEMA = "box-kite-cases-v1"
SERIES_SCHEMA = "box-kite-series-v1"

QX_IDENTIFIER = "QXsinglenodesimulator"
QX_BACKEND_TYPE_ID = 1
QX_QUBITS = 10
QX_SHOTS = 2048
# Rz angles of the compiled full Design B are multiples of pi/ANGLE_GRID.
ANGLE_GRID = 64
ANGLE_TOLERANCE = 1e-9
PROBABILITY_TOLERANCE = 1e-9
# Bonferroni bound of family (a) on its P = 1/2 rows at family error 0.01.
Z_LIMIT = 4.5
FULL_BASIS = ["cx", "rz", "h", "x", "z", "s", "sdg"]
DIALECTS: dict[str, dict[str, str]] = {
    "qx": {"h": "H", "x": "X", "z": "Z", "s": "S", "sdg": "Sdag", "cx": "CNOT", "cz": "CZ", "rz": "Rz"},
}
TWO_QUBIT = {"cx", "cz"}
SQRT8 = 2.0 * math.sqrt(2.0)

# Local qubit roles of each encoding.
FULL_DATA, FULL_SELECTOR = (0, 1, 2, 3), 4
REDUCED_SELECTOR, REDUCED_DATA, CROSS_MARK = 0, 1, 2
WIDTH = {"full": 5, "reduced": 2, "reduced_cross": 3}
SELECTOR = {"full": FULL_SELECTOR, "reduced": REDUCED_SELECTOR, "reduced_cross": REDUCED_SELECTOR}
ROLES: dict[str, dict[str, list[int]]] = {
    "full": {"selector": [FULL_SELECTOR], "data": list(FULL_DATA)},
    "reduced": {"selector": [REDUCED_SELECTOR], "data": [REDUCED_DATA]},
    "reduced_cross": {"selector": [REDUCED_SELECTOR], "data": [REDUCED_DATA], "mark": [CROSS_MARK]},
}
# Sub-families of family (a) in run order: (name, census sources, encoding).
SUB_FAMILIES = (
    ("full_within_kite", ("within_kite",), "full"),
    ("reduced_within_kite", ("within_kite",), "reduced"),
    ("full_cross_kite", ("cross_kite_controls", "negative_fixture"), "full"),
    ("reduced_cross_kite", ("cross_kite_controls", "negative_fixture"), "reduced_cross"),
    ("full_nonkite", ("nonkite_pairs",), "full"),
    ("reduced_nonkite", ("nonkite_pairs",), "reduced"),
)

Row = dict[str, Any]


# ---------------------------------------------------------------- census


def load_census(path: Path = CENSUS) -> dict[str, Any]:
    census = json.loads(path.read_text(encoding="utf-8"))
    if census.get("schema") != CENSUS_SCHEMA:
        raise ValueError(f"{path}: census schema {census.get('schema')!r}, expected {CENSUS_SCHEMA}")
    return census


def census_rows(census: dict[str, Any]) -> dict[str, list[Row]]:
    """The Design B rows by census source, each a column dict with its source and index."""
    table = census["design_b"]
    columns = table["columns"]
    out: dict[str, list[Row]] = {}
    for source in ("within_kite", "cross_kite_controls", "nonkite_pairs", "negative_fixture"):
        values = [table[source]] if source == "negative_fixture" else table[source]
        rows = []
        for index, value in enumerate(values):
            if len(value) != len(columns):
                raise ValueError(f"census {source}[{index}] has {len(value)} fields for {len(columns)} columns")
            rows.append({**dict(zip(columns, value, strict=True)), "source": source, "index": index})
        out[source] = rows
    return out


def two_label(row: Row) -> bool:
    return row["c0"] is not None


def pair_phases(row: Row) -> tuple[int, int, int, int]:
    """(g(L,L'), g(L,U'), g(U,L'), g(U,U')) solved from the row's coefficients c0, c1, d0, d1 and signs."""
    if not two_label(row):
        raise ValueError(f"census {row['source']}[{row['index']}] is a four-label row and carries no phases")
    s, t = row["x_sign"], row["y_sign"]
    c0, c1, d0, d1 = row["c0"], row["c1"], row["d0"], row["d1"]
    doubled = (c0 + d0, t * (c1 + d1), s * (c1 - d1), s * t * (c0 - d0))
    if any(value not in (2, -2) for value in doubled):
        raise ValueError(f"census {row['source']}[{row['index']}]: coefficients give phases {doubled} / 2")
    return (doubled[0] // 2, doubled[1] // 2, doubled[2] // 2, doubled[3] // 2)


def coherence(a: int, b: int) -> str | None:
    norm = a * a + b * b
    if norm == 0:
        return None
    value = Fraction(a * b, norm)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def validate_census(census: dict[str, Any]) -> dict[str, list[Row]]:
    """Internal consistency of every Design B row the generator reads; raises on the first failure.

    Two-label rows: labels L^L' = U^U' and L^U' = U^L', phases in {+1, -1}
    shared by the four sign rows of an ordered pair, P = (c0^2 + c1^2)/8,
    1 - P = (d0^2 + d1^2)/8, the post-selected coherences, and for
    within-kite rows the kite's relation: the pair's phase products equal the
    edge's sign_products (zero P exactly on its zero_signs, else 1) or the
    strut's strut_sign_products (P = 1/2). Four-label rows: distinct XOR
    labels and P = 1/2.
    """
    rows = census_rows(census)
    counts = census["experiment_counts"]
    for source, count in (
        ("within_kite", "within_kite_rows"),
        ("cross_kite_controls", "cross_kite_control_rows"),
        ("nonkite_pairs", "nonkite_rows"),
    ):
        if len(rows[source]) != counts[count]:
            raise ValueError(
                f"census {source} holds {len(rows[source])} rows against experiment_counts {counts[count]}"
            )
    relations: dict[tuple[tuple[int, int], tuple[int, int]], dict[str, Any]] = {}
    for kite in census["kites"]:
        for edge in kite["edges"]:
            p, q = (tuple(plane) for plane in edge["pair"])
            entry = {
                "kite": kite["strut_constant"],
                "relation": f"edge_{edge['type']}",
                "products": tuple(edge["sign_products"]),
                "zero_signs": {tuple(z) for z in edge["zero_signs"]},
            }
            relations[(p, q)] = relations[(q, p)] = entry
        for strut, products in zip(kite["struts"], kite["strut_sign_products"], strict=True):
            p, q = (tuple(plane) for plane in strut)
            entry = {"kite": kite["strut_constant"], "relation": "strut", "products": tuple(products)}
            relations[(p, q)] = relations[(q, p)] = entry
    phases_of: dict[tuple[Any, ...], tuple[int, int, int, int]] = {}
    keys: set[tuple[Any, ...]] = set()
    for source, source_rows in rows.items():
        for row in source_rows:
            name = f"census {source}[{row['index']}]"
            low, high, q_low, q_high = row["p_low"], row["p_high"], row["q_low"], row["q_high"]
            key = (source, low, high, row["x_sign"], q_low, q_high, row["y_sign"])
            if key in keys:
                raise ValueError(f"{name} repeats the signed pair {key[1:]}")
            keys.add(key)
            if row["x_sign"] not in (1, -1) or row["y_sign"] not in (1, -1):
                raise ValueError(f"{name}: signs must be +1 or -1")
            prob = Fraction(row["p_selector_zero"])
            if not two_label(row):
                if any(row[c] is not None for c in ("label_0", "label_1", "c1", "d0", "d1")):
                    raise ValueError(f"{name}: a four-label row carries reduced coefficients")
                if (low ^ high) == (q_low ^ q_high):
                    raise ValueError(f"{name}: equal XOR labels on a row without reduced coefficients")
                if prob != Fraction(1, 2):
                    raise ValueError(f"{name}: a four-label row has P = {prob}, not 1/2")
                continue
            if (low ^ high) != (q_low ^ q_high):
                raise ValueError(f"{name}: two-label coefficients on planes of different XOR labels")
            if (row["label_0"], row["label_1"]) != (low ^ q_low, low ^ q_high):
                raise ValueError(f"{name}: labels differ from L^L' and L^U'")
            c0, c1, d0, d1 = row["c0"], row["c1"], row["d0"], row["d1"]
            if Fraction(c0 * c0 + c1 * c1, 8) != prob or Fraction(d0 * d0 + d1 * d1, 8) != 1 - prob:
                raise ValueError(f"{name}: P = {prob} differs from (c0^2 + c1^2)/8 or 1 - (d0^2 + d1^2)/8")
            if (row["coherence_selector_0"], row["coherence_selector_1"]) != (coherence(c0, c1), coherence(d0, d1)):
                raise ValueError(f"{name}: post-selected coherences differ from the coefficients")
            phases = pair_phases(row)
            pair = (source, low, high, q_low, q_high)
            if phases_of.setdefault(pair, phases) != phases:
                raise ValueError(f"{name}: phases {phases} differ from {phases_of[pair]} on another sign row")
            if source != "within_kite":
                continue
            relation = relations.get(((low, high), (q_low, q_high)))
            if relation is None or (relation["kite"], relation["relation"]) != (row["kite"], row["relation"]):
                raise ValueError(f"{name}: kite {row['kite']} {row['relation']} is not a census kite relation")
            g_ll, g_lu, g_ul, g_uu = phases
            if (g_ll * g_uu, g_lu * g_ul) != relation["products"]:
                raise ValueError(f"{name}: phase products differ from the kite's sign products")
            if relation["relation"] == "strut":
                expected = Fraction(1, 2)
            else:
                expected = Fraction(0 if (row["x_sign"], row["y_sign"]) in relation["zero_signs"] else 1)
            if prob != expected:
                raise ValueError(f"{name}: P = {prob} against {expected} from the kite's zero sign choices")
    return rows


# ---------------------------------------------------------------- circuits


def full_design_b(row: Row) -> Any:
    """designs.lcu_witness on the row's planes, measurement removed, with the selector Z for x_sign = -1."""
    from qiskit import QuantumCircuit

    from designs import lcu_witness

    witness = lcu_witness(
        (row["p_low"], row["p_high"]), (row["q_low"], row["q_high"]), 0.0 if row["y_sign"] > 0 else math.pi
    ).remove_final_measurements(inplace=False)
    qc = QuantumCircuit(5, global_phase=witness.global_phase)
    selector_z = row["x_sign"] < 0
    for instruction in witness.data:
        qubits = [witness.find_bit(q).index for q in instruction.qubits]
        qc.append(instruction.operation, qubits)
        if selector_z and instruction.operation.name == "h" and qubits == [FULL_SELECTOR]:
            qc.z(FULL_SELECTOR)
            selector_z = False
    if selector_z:
        raise ValueError("designs.lcu_witness applied no H to the selector")
    return qc


def two_label_select(phases: tuple[int, int, int, int]) -> Any:
    """SELECT on (selector 0, data 1): diag(g(a, d)) over the input d, then CNOT(a -> d).

    (-1)^f(a, d) with f = f0 + alpha a + beta d + gamma a d: alpha is a Z on
    a, beta a Z on d, and gamma = 1 turns CNOT into CNOT CZ = Sdag(a) CY with
    CY = S(d) CNOT Sdag(d). The constant f0 is the circuit's global phase.
    """
    from qiskit import QuantumCircuit

    bits = [0 if g > 0 else 1 for g in phases]  # (a, d) = 00, 01, 10, 11
    f0 = bits[0]
    alpha, beta = bits[0] ^ bits[2], bits[0] ^ bits[1]
    gamma = bits[0] ^ bits[1] ^ bits[2] ^ bits[3]
    a, d = REDUCED_SELECTOR, REDUCED_DATA
    qc = QuantumCircuit(2, global_phase=math.pi * f0, name="select2")
    if alpha:
        qc.z(a)
    if beta:
        qc.z(d)
    if gamma:
        qc.sdg(d)
        qc.cx(a, d)
        qc.s(d)
        qc.sdg(a)
    else:
        qc.cx(a, d)
    return qc


def two_label_restriction(phases: tuple[int, int, int, int]) -> Any:
    """|a, d> -> g(a, d)|a, d ^ a>, the LCU restricted to span{e_L', e_U'}; Qiskit index a + 2 d."""
    import numpy as np

    matrix = np.zeros((4, 4), dtype=complex)
    for a in (0, 1):
        for d in (0, 1):
            matrix[a + 2 * (d ^ a), a + 2 * d] = phases[2 * a + d]
    return matrix


def cross_restriction() -> Any:
    """|a, d, w> -> |a, d ^ a, w ^ a>; Qiskit index a + 2 d + 4 w."""
    import numpy as np

    matrix = np.zeros((8, 8), dtype=complex)
    for a in (0, 1):
        for d in (0, 1):
            for w in (0, 1):
                matrix[a + 2 * (d ^ a) + 4 * (w ^ a), a + 2 * d + 4 * w] = 1
    return matrix


def cross_select() -> Any:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3, name="select_cross")
    qc.compose(two_label_select((1, 1, 1, 1)), [REDUCED_SELECTOR, REDUCED_DATA], inplace=True)
    qc.cx(REDUCED_SELECTOR, CROSS_MARK)
    return qc


def _prepared(width: int, row: Row) -> Any:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(width)
    qc.h(REDUCED_DATA)
    if row["y_sign"] < 0:
        qc.z(REDUCED_DATA)
    qc.h(REDUCED_SELECTOR)
    if row["x_sign"] < 0:
        qc.z(REDUCED_SELECTOR)
    return qc


def reduced_lcu(row: Row) -> Any:
    """Selector 0 and data 1: H (Z for y_sign = -1) on d, H (Z for x_sign = -1) on a, SELECT, H on a."""
    qc = _prepared(2, row)
    qc.compose(two_label_select(pair_phases(row)), [0, 1], inplace=True)
    qc.h(REDUCED_SELECTOR)
    return qc


def reduced_cross_control(row: Row) -> Any:
    """reduced_lcu's preparation and identity-diagonal SELECT plus CNOT(a -> w) on mark qubit 2."""
    if two_label(row):
        raise ValueError(f"census {row['source']}[{row['index']}] is a two-label row")
    qc = _prepared(3, row)
    qc.compose(cross_select(), [0, 1, 2], inplace=True)
    qc.h(REDUCED_SELECTOR)
    return qc


def logical(encoding: str, row: Row) -> Any:
    if encoding == "full":
        return full_design_b(row)
    if encoding == "reduced":
        return reduced_lcu(row)
    if encoding == "reduced_cross":
        return reduced_cross_control(row)
    raise ValueError(f"unknown encoding {encoding!r}")


def basis_circuit(encoding: str, row: Row) -> Any:
    """The replica in the emitter's gate set; full Design B compiles at optimization level 0."""
    circuit = logical(encoding, row)
    if encoding != "full":
        return circuit
    from qiskit import transpile

    return transpile(circuit, basis_gates=FULL_BASIS, optimization_level=0)


# ---------------------------------------------------------------- checks


def census_p(row: Row) -> float:
    return float(Fraction(row["p_selector_zero"]))


def check_amplitudes(encoding: str, row: Row, circuit: Any) -> None:
    """The logical replica's state against the census row; raises on a deviation.

    Full Design B on a two-label row puts c0, c1 / (2 sqrt2) at |selector 0,
    data label_0 or label_1> and d0, d1 / (2 sqrt2) at selector 1, zero
    elsewhere; the reduced LCU does the same on |a, d> with d = 0 for label_0.
    Every replica's selector marginal equals the census P.
    """
    import numpy as np
    from qiskit.quantum_info import Statevector

    name = f"{encoding} census {row['source']}[{row['index']}]"
    state = Statevector(circuit)
    p0 = float(state.probabilities([SELECTOR[encoding]])[0])
    if abs(p0 - census_p(row)) > PROBABILITY_TOLERANCE:
        raise ValueError(f"{name}: P(selector = 0) = {p0:.12f} against the census {row['p_selector_zero']}")
    if encoding == "reduced_cross" or not two_label(row):
        return
    want = np.zeros(len(state.data), dtype=complex)
    coefficients = {(0, 0): row["c0"], (0, 1): row["c1"], (1, 0): row["d0"], (1, 1): row["d1"]}
    for (sel, label), value in coefficients.items():
        if encoding == "full":
            index = (row["label_0"], row["label_1"])[label] + 16 * sel
        else:
            index = sel + 2 * label
        want[index] = value / SQRT8
    deviation = float(np.max(np.abs(state.data - want)))
    if deviation > PROBABILITY_TOLERANCE:
        raise ValueError(f"{name}: amplitudes deviate from c0, c1, d0, d1 / (2 sqrt2) by {deviation:.2e}")


def check_select(encoding: str, row: Row, select: Any = None) -> None:
    """The reduced SELECT, built from the row unless given, against its restriction, global phase included."""
    import numpy as np
    from qiskit.quantum_info import Operator

    if encoding == "reduced":
        want = two_label_restriction(pair_phases(row))
        select = two_label_select(pair_phases(row)) if select is None else select
    elif encoding == "reduced_cross":
        want = cross_restriction()
        select = cross_select() if select is None else select
    else:
        return
    deviation = float(np.max(np.abs(Operator(select).data - want)))
    if deviation > PROBABILITY_TOLERANCE:
        name = f"{encoding} census {row['source']}[{row['index']}]"
        raise ValueError(f"{name}: SELECT deviates from its restriction by {deviation:.2e}")


def check_row(item: tuple[str, Row]) -> None:
    """Pool worker: SELECT unitary and logical state of one replica against its census row."""
    encoding, row = item
    check_select(encoding, row)
    check_amplitudes(encoding, row, logical(encoding, row))


# ---------------------------------------------------------------- emission


def snap_angle(theta: float) -> int:
    k = round(theta * ANGLE_GRID / math.pi)
    if abs(theta - k * math.pi / ANGLE_GRID) > ANGLE_TOLERANCE:
        raise ValueError(f"Rz angle {theta!r} is off the pi/{ANGLE_GRID} grid")
    return k


def emit(circuit: Any, place: dict[int, int], dialect: str = "qx") -> list[str]:
    """cQASM 3.0 lines of a basis-level replica; place maps its local qubits to register indices.

    The circuit's global phase is unobservable and is not written. Rz angles
    print from their pi/ANGLE_GRID multiple.
    """
    if dialect not in DIALECTS:
        raise ValueError(f"dialect {dialect!r} has no gate map")
    names = DIALECTS[dialect]
    lines = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [place[circuit.find_bit(q).index] for q in instruction.qubits]
        if name == "barrier":
            continue
        if name not in names:
            raise ValueError(f"{name} is outside the {dialect} gate map")
        if name in TWO_QUBIT:
            lines.append(f"{names[name]} q[{qubits[0]}], q[{qubits[1]}]")
        elif name == "rz":
            k = snap_angle(float(instruction.operation.params[0]))
            lines.append(f"{names[name]}({k * math.pi / ANGLE_GRID:.15f}) q[{qubits[0]}]")
        else:
            lines.append(f"{names[name]} q[{qubits[0]}]")
    return lines


GATE_LINE = re.compile(r"(?P<gate>[A-Za-z]+)(?:\((?P<angle>[-0-9.e+]+)\))? q\[(?P<a>\d+)\](?:, q\[(?P<b>\d+)\])?")


def parse_cqasm(text: str, dialect: str = "qx") -> Any:
    """The emitter's own cQASM vocabulary back into a Qiskit circuit, measurement excluded."""
    from qiskit import QuantumCircuit

    names = {cq: qk for qk, cq in DIALECTS[dialect].items()}
    width = declared_qubits(text)
    qc = QuantumCircuit(width)
    for line in text.splitlines():
        line = line.strip()
        if (
            not line
            or line.startswith("//")
            or line.startswith(("version ", "qubit[", "bit["))
            or line == "b = measure q"
        ):
            continue
        match = GATE_LINE.fullmatch(line)
        if match is None or match["gate"] not in names:
            raise ValueError(f"unparsed cQASM line {line!r}")
        gate = names[match["gate"]]
        qubits = [int(match["a"])] + ([int(match["b"])] if match["b"] is not None else [])
        if (gate in TWO_QUBIT) != (len(qubits) == 2) or (gate == "rz") != (match["angle"] is not None):
            raise ValueError(f"malformed cQASM line {line!r}")
        if gate == "rz":
            qc.rz(float(match["angle"]), qubits[0])
        else:
            getattr(qc, gate)(*qubits)
    return qc


def emit_circuit(item: tuple[str, list[tuple[str, Row, dict[int, int]]]]) -> str:
    """Pool worker: one packed QX circuit's cQASM text."""
    file, members = item
    lines = header(QX_QUBITS)
    for slot, (encoding, row, place) in enumerate(members):
        roles = replica_roles(encoding, place)
        lines.append(
            f"// slot {slot} {encoding} census {row['source']}[{row['index']}] kite {row['kite']} "
            f"({row['p_low']},{row['p_high']}){'+' if row['x_sign'] > 0 else '-'} x "
            f"({row['q_low']},{row['q_high']}){'+' if row['y_sign'] > 0 else '-'} {row['relation']} "
            f"P {row['p_selector_zero']} selector q[{roles['selector']}]"
        )
        lines += emit(basis_circuit(encoding, row), place)
    return "\n".join(lines + ["", "b = measure q", ""])


def verify_circuit(item: tuple[str, str, list[tuple[int, str]]]) -> None:
    """Pool worker: the emitted text by state vector; each selector marginal equals its census P."""
    from qiskit.quantum_info import Statevector

    file, text, selectors = item
    state = Statevector(parse_cqasm(text))
    used: set[int] = set()
    for selector, p in selectors:
        if selector in used:
            raise ValueError(f"{file}: selector q[{selector}] serves two replicas")
        used.add(selector)
        p0 = float(state.probabilities([selector])[0])
        if abs(p0 - float(Fraction(p))) > PROBABILITY_TOLERANCE:
            raise ValueError(f"{file}: selector q[{selector}] P(0) = {p0:.12f} against the census {p}")


def replica_roles(encoding: str, place: dict[int, int]) -> dict[str, Any]:
    """Register qubits of a placed replica: the selector index and the data (and mark) lists."""
    roles: dict[str, Any] = {role: [place[q] for q in local] for role, local in ROLES[encoding].items()}
    roles["selector"] = roles["selector"][0]
    return roles


def pack(replicas: list[Any], width: int, nqubits: int = QX_QUBITS, per_circuit: int | None = None) -> list[Any]:
    """Consecutive groups of replicas with their slot placements: slot s maps local q to s * width + q."""
    count = nqubits // width if per_circuit is None else per_circuit
    if count < 1 or count * width > nqubits:
        raise ValueError(f"{count} replicas of {width} qubits exceed the {nqubits}-qubit register")
    groups = []
    for start in range(0, len(replicas), count):
        chunk = replicas[start : start + count]
        groups.append([(replica, {q: slot * width + q for q in range(width)}) for slot, replica in enumerate(chunk)])
    return groups


# ---------------------------------------------------------------- catalogue and series


def qx_backend(catalogue: Any) -> dict[str, Any]:
    """Admit the retained QX emulator record: identity, width, all-to-all topology, gates and capacity."""
    if not isinstance(catalogue, dict) or not isinstance(catalogue.get("backend_types"), list):
        raise SystemExit("catalogue must contain a backend_types list")
    matches = [b for b in catalogue["backend_types"] if isinstance(b, dict) and b.get("identifier") == QX_IDENTIFIER]
    if len(matches) != 1:
        raise SystemExit(f"catalogue needs exactly one {QX_IDENTIFIER} backend type")
    backend = matches[0]
    if (
        type(backend.get("id")) is not int
        or backend["id"] != QX_BACKEND_TYPE_ID
        or type(backend.get("nqubits")) is not int
        or backend["nqubits"] != QX_QUBITS
        or backend.get("is_hardware") is not False
    ):
        raise SystemExit(f"{QX_IDENTIFIER}: backend identity, width or hardware class changed; review the cases")
    topology = backend.get("topology")
    if not isinstance(topology, list) or not all(
        isinstance(edge, list) and len(edge) == 2 and all(type(q) is int and 0 <= q < QX_QUBITS for q in edge)
        for edge in topology
    ):
        raise SystemExit(f"{QX_IDENTIFIER}: malformed catalogue topology")
    complete = {(a, b) for a in range(QX_QUBITS) for b in range(QX_QUBITS) if a != b}
    if {tuple(edge) for edge in topology} != complete or len(topology) != len(complete):
        raise SystemExit(f"{QX_IDENTIFIER}: topology is no longer all-to-all; the packing needs review")
    gates = backend.get("gateset")
    needed = set(DIALECTS["qx"].values()) | {"measure"}
    if not isinstance(gates, list) or not needed <= {g for g in gates if isinstance(g, str)}:
        raise SystemExit(f"{QX_IDENTIFIER}: catalogue lacks a required gate")
    if (
        type(backend.get("max_number_of_shots")) is not int
        or backend["max_number_of_shots"] < QX_SHOTS
        or type(backend.get("max_jobs_per_batch_job")) is not int
        or backend["max_jobs_per_batch_job"] < HARDWARE_BATCH_CIRCUITS
    ):
        raise SystemExit(f"{QX_IDENTIFIER}: cases exceed the retained backend capacity")
    return backend


def preregistered(rows: list[tuple[str, Row]]) -> dict[str, Any]:
    halves = sum(Fraction(row["p_selector_zero"]) == Fraction(1, 2) for _, row in rows)
    return {
        "observable": "zero-product success P(selector = 0), counted from the selector bit of each replica",
        "predictions": "census:design_b p_selector_zero per replica: 0 on the two zero sign choices of an edge, "
        "1 on its other two, 1/2 on every strut, cross-kite, fixture and non-kite row",
        "falsifier": "any shot with selector 0 on a P = 0 replica or selector 1 on a P = 1 replica refutes that "
        f"circuit's implementation; a P = 1/2 replica outside |z| < {Z_LIMIT} at {QX_SHOTS} shots refutes it",
        "half_rows": halves,
        "z_limit": Z_LIMIT,
        "bonferroni": f"two-sided family error 0.01 over the {halves} P = 1/2 replicas of both encodings",
        "lcu_identity": "P(x_sign) + P(-x_sign) = 1 holds by construction and checks the selector Z, not the algebra",
        "stop_rule": "one shot violating a deterministic replica, or a P = 1/2 replica outside the bound, stops the "
        "series until the circuit is explained; each batch checks completed jobs, the shots per job and circuit "
        "digests against cases.json",
    }


def finish(shared: dict[str, Any], circuits: list[dict[str, Any]], texts: dict[str, str]) -> dict[str, str]:
    """batch-NNN/ directories of at most HARDWARE_BATCH_CIRCUITS circuits, and the series cases.json.

    Circuits fill batches in manifest order and a batch holds one sub-family.
    Each batch manifest carries every shared field and only its own circuits
    with their replicas, so one batch's run directory names the full design.
    """
    chunks: list[list[dict[str, Any]]] = []
    for sub_family in dict.fromkeys(row["sub_family"] for row in circuits):
        rows = [row for row in circuits if row["sub_family"] == sub_family]
        chunks += [
            rows[start : start + HARDWARE_BATCH_CIRCUITS] for start in range(0, len(rows), HARDWARE_BATCH_CIRCUITS)
        ]
    digits = max(2, len(str(len(chunks) - 1)))
    files: dict[str, str] = {}
    batches = []
    for index, chunk in enumerate(chunks):
        name = f"batch-{index:0{digits}d}"
        rows = []
        for row in chunk:
            rows.append({**row, "sha256": hashlib.sha256(texts[row["file"]].encode()).hexdigest()})
            files[f"{name}/{row['file']}"] = texts[row["file"]]
        manifest = {**shared, "batch": name, "sub_family": chunk[0]["sub_family"], "circuits": rows}
        files[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": name, "sub_family": chunk[0]["sub_family"], "files": [row["file"] for row in chunk]})
    series = {
        "schema": SERIES_SCHEMA,
        "family": shared["family"],
        "backend": shared["backend"],
        "census_sha256": shared["census"]["sha256"],
        "batches": batches,
    }
    files["cases.json"] = json.dumps(series, indent=1) + "\n"
    return files


def validate_series(files: dict[str, str], backend: dict[str, Any]) -> None:
    """Offline admission of a generated series: batch sizes, digests, widths, shots and the series index."""
    series = json.loads(files["cases.json"])
    listed = set()
    for batch in series["batches"]:
        name = batch["batch"]
        manifest = json.loads(files[f"{name}/cases.json"])
        circuits = manifest["circuits"]
        if len(circuits) > HARDWARE_BATCH_CIRCUITS or len(circuits) > backend["max_jobs_per_batch_job"]:
            raise ValueError(f"{name}: {len(circuits)} circuits exceed the {HARDWARE_BATCH_CIRCUITS}-circuit batch")
        if [row["file"] for row in circuits] != batch["files"]:
            raise ValueError(f"{name}: circuits differ from the series index")
        if manifest["shots"] > backend["max_number_of_shots"] or manifest["nqubits"] > backend["nqubits"]:
            raise ValueError(f"{name}: shots or width exceed the backend")
        for row in circuits:
            text = files[f"{name}/{row['file']}"]
            if hashlib.sha256(text.encode()).hexdigest() != row["sha256"]:
                raise ValueError(f"{name}/{row['file']} differs from its cases.json sha256")
            if declared_qubits(text) != manifest["nqubits"]:
                raise ValueError(f"{name}/{row['file']}: declared width differs from the manifest")
            qubits = [q for replica in row["replicas"] for q in replica_qubits(replica["roles"])]
            if len(set(qubits)) != len(qubits) or max(qubits) >= manifest["nqubits"]:
                raise ValueError(f"{name}/{row['file']}: replicas overlap or leave the register")
            listed.add(f"{name}/{row['file']}")
        listed.add(f"{name}/cases.json")
    if listed | {"cases.json"} != set(files):
        raise ValueError("series files differ from the batches its cases.json lists")


def replica_qubits(roles: dict[str, Any]) -> list[int]:
    return [q for value in roles.values() for q in (value if isinstance(value, list) else [value])]


def series(family: str, backend_name: str, census_path: Path = CENSUS, limit: int | None = None) -> dict[str, str]:
    """The case files of one family on one backend; limit keeps the first rows of each sub-family."""
    if (family, backend_name) != ("a", "qx"):
        raise ValueError(f"series ({family!r}, {backend_name!r}) is not generated by this pass")
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census_bytes = census_path.read_bytes()
    census = load_census(census_path)
    rows = validate_census(census)

    members: dict[str, list[tuple[str, Row]]] = {}
    for sub_family, sources, encoding in SUB_FAMILIES:
        chosen = [(encoding, row) for source in sources for row in rows[source]]
        members[sub_family] = chosen if limit is None else chosen[:limit]
    every = [item for chosen in members.values() for item in chosen]
    parallel.ordered_map(check_row, every)

    circuits: list[dict[str, Any]] = []
    jobs: list[tuple[str, list[tuple[str, Row, dict[int, int]]]]] = []
    summary: dict[str, Any] = {}
    for sub_family, sources, encoding in SUB_FAMILIES:
        width = WIDTH[encoding]
        groups = pack(members[sub_family], width)
        for number, group in enumerate(groups, start=1):
            file = f"{sub_family}-{number:03d}.cq"
            jobs.append((file, [(enc, row, place) for (enc, row), place in group]))
            circuits.append(
                {
                    "file": file,
                    "kind": "witness",
                    "sub_family": sub_family,
                    "encoding": encoding,
                    "replicas": [
                        {
                            "slot": slot,
                            "census": f"{row['source']}[{row['index']}]",
                            "kite": row["kite"],
                            "p": [row["p_low"], row["p_high"], row["x_sign"]],
                            "q": [row["q_low"], row["q_high"], row["y_sign"]],
                            "relation": row["relation"],
                            "roles": replica_roles(enc, place),
                            "p_selector_zero": row["p_selector_zero"],
                        }
                        for slot, ((enc, row), place) in enumerate(group)
                    ],
                }
            )
        summary[sub_family] = {
            "census": [f"design_b.{source}" for source in sources],
            "encoding": encoding,
            "replica_qubits": width,
            "replicas_per_circuit": QX_QUBITS // width,
            "replicas": len(members[sub_family]),
            "circuits": len(groups),
        }
    texts = dict(zip((file for file, _ in jobs), parallel.ordered_map(emit_circuit, jobs), strict=True))
    parallel.ordered_map(
        verify_circuit,
        [
            (row["file"], texts[row["file"]], [(r["roles"]["selector"], r["p_selector_zero"]) for r in row["replicas"]])
            for row in circuits
        ],
    )
    shared = {
        "schema": CASES_SCHEMA,
        "family": family,
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": QX_SHOTS,
        "dialect": backend_name,
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "census": {
            "path": census_path.relative_to(ROOT).as_posix(),
            "schema": census["schema"],
            "sha256": hashlib.sha256(census_bytes).hexdigest(),
        },
        "encodings": {
            "full": "designs.lcu_witness: data 0-3, selector 4; x_sign = -1 adds Z on the selector after its first H; "
            f"compiled at optimization level 0 to {', '.join(FULL_BASIS)} with Rz on the pi/{ANGLE_GRID} grid",
            "reduced": "selector a = slot qubit 0, data d = slot qubit 1; SELECT = diag(g(L,L'), g(L,U'), g(U,L'), "
            "g(U,U')) over (a, d) from the census coefficients, then CNOT(a -> d); x_sign = -1 adds Z on a after "
            "its first H",
            "reduced_cross": "selector a, data d, mark w = slot qubits 0, 1, 2; identity diagonal (the census carries "
            "no phases for four-label rows, and P = 1/2 for every sign), CNOT(a -> d), CNOT(a -> w)",
        },
        "sub_families": summary,
        "preregistered": preregistered(every),
    }
    files = finish(shared, circuits, texts)
    validate_series(files, backend)
    return files


# ---------------------------------------------------------------- self-test


def expect_rejection(label: str, action: Any, *errors: type[BaseException]) -> None:
    caught = errors or (ValueError,)
    try:
        action()
    except caught:
        return
    raise AssertionError(f"{label} was accepted")


def without_selector_z(circuit: Any, selector: int) -> Any:
    """The circuit with the Z that follows the selector's first H removed."""
    from qiskit import QuantumCircuit

    out = QuantumCircuit(circuit.num_qubits, global_phase=circuit.global_phase)
    seen_h = dropped = False
    for instruction in circuit.data:
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        name = instruction.operation.name
        if qubits == [selector] and name == "h":
            seen_h = True
        elif qubits == [selector] and name == "z" and seen_h and not dropped:
            dropped = True
            continue
        out.append(instruction.operation, qubits)
    if not dropped:
        raise AssertionError("the mutation found no selector Z after the first H")
    return out


def self_test() -> None:
    from qiskit import QuantumCircuit

    census = load_census()
    rows = validate_census(census)
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    rejected = 0

    def reject(label: str, action: Any, *errors: type[BaseException]) -> None:
        nonlocal rejected
        expect_rejection(label, action, *errors)
        rejected += 1

    within = rows["within_kite"]
    # A flipped census sign: c1 of one row negated leaves P unchanged, so the
    # cross-row phase agreement and coherences reject it in the census, and
    # the lcu_witness amplitudes (cd_core through designs) reject it in the circuit.
    flip_index = next(i for i, row in enumerate(within) if row["c1"] != 0)
    mutated = copy.deepcopy(census)
    mutated["design_b"]["within_kite"][flip_index][census["design_b"]["columns"].index("c1")] *= -1
    reject("a flipped census sign", lambda: validate_census(mutated))
    flipped = {**within[flip_index], "c1": -within[flip_index]["c1"]}
    reject("a flipped census sign in full Design B", lambda: check_amplitudes("full", flipped, full_design_b(flipped)))
    # A flipped y_sign changes the solved phases, whose products then leave the kite's sign products.
    mutated = copy.deepcopy(census)
    mutated["design_b"]["within_kite"][0][census["design_b"]["columns"].index("y_sign")] *= -1
    reject("a flipped y_sign", lambda: validate_census(mutated))

    # A wrong p_selector_zero, in the census and against an emitted circuit.
    edge_index = next(i for i, row in enumerate(within) if row["p_selector_zero"] == "1")
    mutated = copy.deepcopy(census)
    mutated["design_b"]["within_kite"][edge_index][census["design_b"]["columns"].index("p_selector_zero")] = "0"
    reject("a wrong p_selector_zero", lambda: validate_census(mutated))
    wrong = {**within[edge_index], "p_selector_zero": "0"}
    for encoding in ("full", "reduced"):
        text = emit_circuit(("mutation.cq", [(encoding, wrong, {q: q for q in range(WIDTH[encoding])})]))
        selector = SELECTOR[encoding]
        reject(
            f"a wrong p_selector_zero on emitted {encoding}",
            lambda t=text, s=selector: verify_circuit(("mutation.cq", t, [(s, "0")])),
        )
        verify_circuit(("mutation.cq", text, [(selector, "1")]))

    # A dropped selector Z on an x_sign = -1 edge row moves P from 0 to 1 or back.
    dark = next(row for row in within if row["x_sign"] < 0 and row["p_selector_zero"] in ("0", "1"))
    for encoding, selector in (("full", FULL_SELECTOR), ("reduced", REDUCED_SELECTOR)):
        circuit = logical(encoding, dark)
        check_amplitudes(encoding, dark, circuit)
        reject(
            f"a dropped selector Z in {encoding}",
            lambda e=encoding, c=circuit, s=selector: check_amplitudes(e, dark, without_selector_z(c, s)),
        )
    # SELECT built from another phase set, or without its CNOT, fails the unitary check.
    g_ll, g_lu, g_ul, g_uu = pair_phases(within[0])
    check_select("reduced", within[0])
    reject(
        "a SELECT with one phase flipped",
        lambda: check_select("reduced", within[0], two_label_select((g_ll, -g_lu, g_ul, g_uu))),
    )
    unmarked = QuantumCircuit(3)
    unmarked.compose(two_label_select((1, 1, 1, 1)), [REDUCED_SELECTOR, REDUCED_DATA], inplace=True)
    reject(
        "a cross-kite SELECT without its mark CNOT",
        lambda: check_select("reduced_cross", rows["cross_kite_controls"][0], unmarked),
    )

    # Packing and batching.
    reject("three full replicas in one QX circuit", lambda: pack([0, 1, 2], 5, QX_QUBITS, per_circuit=3))
    files = series("a", "qx", limit=7)
    validate_series(files, backend)
    first = json.loads(files["cases.json"])["batches"][0]["batch"]
    manifest = json.loads(files[f"{first}/cases.json"])
    over = dict(files)
    extra = {**manifest["circuits"][0], "file": "extra.cq"}
    over[f"{first}/extra.cq"] = files[f"{first}/{manifest['circuits'][0]['file']}"]
    over[f"{first}/cases.json"] = json.dumps({**manifest, "circuits": manifest["circuits"] + [extra]}, indent=1) + "\n"
    index = json.loads(files["cases.json"])
    index["batches"][0]["files"].append("extra.cq")
    over["cases.json"] = json.dumps(index, indent=1) + "\n"
    if len(manifest["circuits"]) + 1 <= HARDWARE_BATCH_CIRCUITS:
        raise AssertionError("the over-full mutation leaves the batch within its cap")
    reject("an over-full batch", lambda: validate_series(over, backend))
    tampered = dict(files)
    target = f"{first}/{manifest['circuits'][0]['file']}"
    tampered[target] = tampered[target].replace("H q[", "X q[", 1)
    reject("a circuit digest mismatch", lambda: validate_series(tampered, backend))
    stray = {**files, f"{first}/stray.cq": "version 3.0\n"}
    reject("a file outside the series index", lambda: validate_series(stray, backend))
    reject("an unknown dialect", lambda: emit(logical("reduced", within[0]), {0: 0, 1: 1}, dialect="tuna"))
    reject("an off-grid Rz angle", lambda: snap_angle(math.pi / 3))

    # Catalogue admission.
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    for field, value in (("nqubits", 9), ("id", 2), ("is_hardware", True), ("topology", backend["topology"][1:])):
        altered = copy.deepcopy(catalogue)
        next(b for b in altered["backend_types"] if b["identifier"] == QX_IDENTIFIER)[field] = value
        reject(f"a changed QX {field}", lambda a=altered: qx_backend(a), SystemExit)
    altered = copy.deepcopy(catalogue)
    entry = next(b for b in altered["backend_types"] if b["identifier"] == QX_IDENTIFIER)
    entry["gateset"] = [g for g in entry["gateset"] if g != "Rz"]
    reject("a QX gate set without Rz", lambda: qx_backend(altered), SystemExit)
    print(
        f"box-kite cases: census, SELECT, state-vector, packing, batch and catalogue contracts pass; "
        f"{rejected} mutations rejected"
    )


# ---------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="DIR")
    mode.add_argument("--check", type=Path, metavar="DIR")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        directories = {"box_kite_a_qx": series("a", "qx")}
    except ValueError as error:
        raise SystemExit(str(error)) from error
    count = 0
    for directory, files in directories.items():
        if args.check:
            root = args.check / directory
            retained = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            if retained != set(files):
                raise SystemExit(f"{root}: files {sorted(retained ^ set(files))[:8]} differ from the regeneration")
        for name, text in files.items():
            path = (args.write or args.check) / directory / name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
            count += 1
    print(f"box-kite cases: {count} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
