"""Box-kite cases for Quantum Inspire, generated from the retained box-kite census.

docs/notes/box_kites/experiment-program.md fixes the design. Every sign comes
from docs/evidence/box_kite_census/census.json; the generator recomputes none
from cd_core. Four products come out of one census read:

- Family (a), exhaustive, in memory only: every Design B row (840 within-kite
  rows, 168 cross-kite controls with the negative fixture (1,10)+ x (2,13)-,
  168 ordered (l, l^8) pairs) in the full and the reduced encoding, 848 QX
  circuits. scripts/box_kite_qx_sweep.py runs them on the qxelarator
  state-vector emulator, the ideal emulator the remote QX backend runs.
- The QX smoke set, written to box_kite_a_qx/: one replica per gate pattern
  of family (a), the first census row in census order that matches each
  SMOKE_PATTERNS predicate. A remote QX run establishes that the emitted
  cQASM passes the platform's parser, bit order, gate set and angle grid; the
  state-vector checks below already establish the unitary.
- The Tuna-17 series T0 (depth ladder), T1 (edge-sign classification and
  twist), coherence and walk, each batch one witness circuit plus readout-0
  and readout-1, and the relabeled QX twin of every witness circuit.
- The Ry emulator ladder residue (R1 width 9, R2 a comment line, R9 the
  failed teleport.cq without its bit register and comments; the retained
  construct probe settled the rest) and the Ry smoke subset, written in the
  ry dialect: no bit register, measure statement or comment, Sdag as
  Rz(-pi/2), qubit 0 at the leftmost character of the emulator's results.

Encodings, each read through the selector's success outcome P(selector = 0)
(root AGENTS.md, "Zero-product witnesses"):

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
- Fixed-triple associator walk (control c and the walked data bits): the
  Hadamard test of W_ij on the basis input |k> moves the data register
  k -> k^j -> k^j^i -> k under control, one CNOT per set bit of j, i and i^j,
  and omega(i, j, k) from census associator.deterministic_exemplars enters as
  a Z on the control after its first H, so P(c = 0) = (1 + omega)/2. Dropping
  the last block leaves the register branch-marked and P(c = 0) = 1/2.

validate_census requires each two-label row's four phases to lie in {+1, -1},
to agree over the four sign rows of an ordered pair, to give the kite's edge
or strut sign products, and to reproduce P, 1 - P and both post-selected
coherences. Before emission every full Design B replica must reproduce its
census amplitudes c0, c1, d0, d1 / (2 sqrt2) (the designs.lcu_witness state,
built on cd_core, against the census), every reduced SELECT must equal its
two-label restriction as a unitary, and every emitted cQASM file is parsed
back and simulated by state vector on the qubits it uses: each replica's
selector (or control) marginal, each coherence setting's conditional data
marginal and each padded replica's CZ count must equal the prediction. A
mismatch raises.

QX serves 10 qubits, so pack() places two full replicas (slots 0-4, 5-9),
five reduced replicas or three cross-kite replicas per circuit. Full Design B
compiles at optimization level 0 to H, X, Z, S, Sdag, Rz and CNOT; each Rz
angle snaps to a multiple of pi/64 and prints from that integer, so the
emitted bytes do not depend on the host's floating-point library.

Tuna-17 circuits declare qubit[17], use H, S, Sdag, Z, X and CZ (CNOT is
H CZ H on the target), carry no rotation and no binary-controlled gate, and
touch only the admitted layout: the LCU pairs of LCU_PAIRS (selector first),
the walk star WALK_LAYOUTS["star_11"] and path WALK_LAYOUTS["path_8_11_13"],
none of TUNA_EXCLUDED or TUNA_AVOIDED, every CZ on a TUNA17 coupler. Depth
padding repeats CZ on the replica's own pair in identity pairs with a
per-qubit barrier run before each repeat, so a compiler pass that cancels
adjacent CZ pairs meets a barrier. A batch holds at most
qi_platform.HARDWARE_BATCH_CIRCUITS circuits: one witness circuit, then
qi_zero_divisor_cases.readout_circuits(17). twin() moves the identical gate
list of each witness circuit onto QX qubits 0-9 (map recorded). Bit strings
put qubit 0 at the rightmost character (QX and Tuna).

--write DIR writes every case directory of CASE_DIRECTORIES under DIR (each
batch-NN/ cases and a series cases.json); --check DIR regenerates in memory
and compares file sets and bytes; --summary prints circuits, batches, shots
and replicas per directory; --self-test requires census, circuit, layout,
packing and manifest mutations to be rejected.

Usage: "$PYTHON" scripts/box_kite_cases.py (--write DIR | --check DIR | --summary | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS, declared_qubits  # noqa: E402
from qi_zero_divisor_cases import (  # noqa: E402
    EXCLUDED_QUBITS,
    TUNA17,
    catalogue_backends,
    header,
    readout_circuits,
)

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
TUNA_IDENTIFIER = "tuna_17"
RY_IDENTIFIER = "Rydberg"
RY_BACKEND_TYPE_ID = 5
RY_QUBITS = 9
RY_SHOTS = 1024
# The failing Ry program; ry_ladder reads it by digest.
RY_TELEPORT = ROOT / "results/quantum_inspire/runs/2026-10-16T211635Z-Rydberg/teleport.cq"
RY_TELEPORT_SHA256 = "e4df1064cc91a908cb0ad12c253464ca9d441f2a3e36b9bef0be6f3346134f08"
TUNA_QUBITS = 17
# T0 reads a contrast near 0.1 at depth 9 against binomial noise, so it takes
# the larger shot count; the later stages read deterministic or 1/2 rates.
T0_SHOTS = 16384
FOLLOW_SHOTS = 4096
# Rz angles of the compiled full Design B are multiples of pi/ANGLE_GRID.
ANGLE_GRID = 64
ANGLE_TOLERANCE = 1e-9
PROBABILITY_TOLERANCE = 1e-9
# Bonferroni bound of family (a) on its P = 1/2 rows at family error 0.01.
Z_LIMIT = 4.5
FULL_BASIS = ["cx", "rz", "h", "x", "z", "s", "sdg"]
DIALECTS: dict[str, dict[str, str]] = {
    "qx": {"h": "H", "x": "X", "z": "Z", "s": "S", "sdg": "Sdag", "cx": "CNOT", "cz": "CZ", "rz": "Rz"},
    "tuna": {"h": "H", "x": "X", "z": "Z", "s": "S", "sdg": "Sdag", "cz": "CZ"},
    "ry": {"h": "H", "x": "X", "z": "Z", "s": "S", "cx": "CNOT", "rz": "Rz"},
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


def is_edge(row: Row) -> bool:
    return str(row["relation"]).startswith("edge_")


def signs(row: Row, x: int, y: int) -> bool:
    return bool(row["x_sign"] == x and row["y_sign"] == y)


# Smoke patterns of family (a): (name, encoding, census source, selection
# rule, predicate). The sign variants select edge rows because a strut gives
# P = 1/2 at both signs (P(x_sign) + P(-x_sign) = 1), so a dropped selector Z
# or a wrong data phase would read correctly there. Reduced non-kite rows
# share the strut's Sdag-CNOT-S SELECT and P = 1/2 and add no pattern.
SMOKE_PATTERNS: tuple[tuple[str, str, str, str, Callable[[Row], bool]], ...] = (
    ("edge_dark", "full", "within_kite", "first edge row with signs (+, +) and P = 0",
     lambda r: is_edge(r) and signs(r, 1, 1) and r["p_selector_zero"] == "0"),
    ("edge_bright", "full", "within_kite", "first edge row with signs (+, +) and P = 1",
     lambda r: is_edge(r) and signs(r, 1, 1) and r["p_selector_zero"] == "1"),
    ("strut", "full", "within_kite", "first strut row with signs (+, +)",
     lambda r: r["relation"] == "strut" and signs(r, 1, 1)),
    ("edge_x_minus", "full", "within_kite", "first edge row with signs (-, +)",
     lambda r: is_edge(r) and signs(r, -1, 1)),
    ("edge_y_minus", "full", "within_kite", "first edge row with signs (+, -)",
     lambda r: is_edge(r) and signs(r, 1, -1)),
    ("cross_kite", "full", "cross_kite_controls", "first cross-kite control row", lambda r: True),
    ("nonkite", "full", "nonkite_pairs", "first (l, l^8) row", lambda r: True),
    ("fixture", "full", "negative_fixture", "the negative fixture (1,10)+ x (2,13)-", lambda r: True),
    ("edge_dark", "reduced", "within_kite", "first edge row with signs (+, +) and P = 0 (local-Z SELECT)",
     lambda r: is_edge(r) and signs(r, 1, 1) and r["p_selector_zero"] == "0"),
    ("edge_bright", "reduced", "within_kite", "first edge row with signs (+, +) and P = 1 (local-Z SELECT)",
     lambda r: is_edge(r) and signs(r, 1, 1) and r["p_selector_zero"] == "1"),
    ("strut", "reduced", "within_kite", "first strut row with signs (+, +) (Sdag-CNOT-S SELECT)",
     lambda r: r["relation"] == "strut" and signs(r, 1, 1)),
    ("edge_x_minus", "reduced", "within_kite", "first edge row with signs (-, +)",
     lambda r: is_edge(r) and signs(r, -1, 1)),
    ("edge_y_minus", "reduced", "within_kite", "first edge row with signs (+, -)",
     lambda r: is_edge(r) and signs(r, 1, -1)),
    ("cross_kite", "reduced_cross", "cross_kite_controls", "first cross-kite control row", lambda r: True),
    ("fixture", "reduced_cross", "negative_fixture", "the negative fixture (1,10)+ x (2,13)-", lambda r: True),
)  # fmt: skip

# Admitted Tuna-17 layout (program section 4(g)). TUNA_EXCLUDED must equal
# qi_zero_divisor_cases.EXCLUDED_QUBITS, the readout and visibility exclusions
# derived from the retained records; q15 reads P(0|1) 0.270 and stays out.
TUNA_EXCLUDED = (0, 5, 6, 7, 9)
TUNA_AVOIDED = (15,)
LCU_PAIRS = ((1, 4), (10, 13), (12, 14))
WALK_LAYOUTS: dict[str, tuple[int, tuple[int, ...]]] = {"star_11": (11, (8, 13, 14)), "path_8_11_13": (11, (8, 13))}
# The walk circuits place the reference replica on the LCU pair that shares
# the fewest couplers with the walk qubits: (1, 4) meets q8 through 4-8 only.
WALK_REFERENCE_PAIR = 0
T0_DEPTHS = (1, 5, 9)
# Census rows by (kite, (p_low, p_high), x_sign, (q_low, q_high), y_sign).
EDGE_K3 = (3, (1, 10), (4, 15))  # opposite-sign edge of kite 3, the acquired (1,10) witness pair
TWIST_K6 = (6, (4, 10), (1, 15))  # its twist, a same-sign edge of kite 6 (census kites[2].twists[0])
STRUT_K3 = (3, (1, 10), (2, 9))
WALK_KITE = "1"
WALKS = (
    ("walk_ij_strut", (2, 11, 3), "star_11", False),
    ("walk_jk_strut", (2, 3, 10), "path_8_11_13", False),
    ("walk_ij_strut_omit_last", (2, 11, 3), "star_11", True),
)
TUNA_STAGES = ("t0", "t1", "coherence", "walk")
CASE_DIRECTORIES = (
    "box_kite_a_qx",
    "box_kite_tuna_t0",
    "box_kite_tuna_t1",
    "box_kite_tuna_coherence",
    "box_kite_tuna_walk",
    "box_kite_tuna_twins_qx",
    "box_kite_ry_ladder",
    "box_kite_ry_smoke",
)


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


def find_row(rows: dict[str, list[Row]], spec: tuple[int, tuple[int, int], tuple[int, int]], x: int, y: int) -> Row:
    """The one within-kite census row of kite spec[0] on planes spec[1] x spec[2] at signs (x, y)."""
    kite, p, q = spec
    found = [
        row
        for row in rows["within_kite"]
        if (row["kite"], (row["p_low"], row["p_high"]), (row["q_low"], row["q_high"])) == (kite, p, q)
        and signs(row, x, y)
    ]
    if len(found) != 1:
        raise ValueError(f"census holds {len(found)} within-kite rows for kite {kite} {p} x {q} at ({x}, {y})")
    return found[0]


def check_twist(census: dict[str, Any]) -> None:
    """TWIST_K6 is the census twist of EDGE_K3, of the other sign type."""
    kite = next(k for k in census["kites"] if k["strut_constant"] == EDGE_K3[0])
    twist = next((t for t in kite["twists"] if [tuple(p) for p in t["pair"]] == [EDGE_K3[1], EDGE_K3[2]]), None)
    if (
        twist is None
        or [tuple(p) for p in twist["twisted"]] != [TWIST_K6[1], TWIST_K6[2]]
        or twist["twisted_kite"] != TWIST_K6[0]
        or {twist["relation"], twist["twisted_relation"]} != {"edge_opposite", "edge_same"}
    ):
        raise ValueError(f"census kites[].twists does not map {EDGE_K3} to {TWIST_K6} across sign types")


def walk_exemplar(census: dict[str, Any], triple: tuple[int, int, int]) -> dict[str, Any]:
    """[i, j, k, omega, CNOTs, data bits] of census associator.deterministic_exemplars[WALK_KITE]."""
    entries = census["associator"]["deterministic_exemplars"][WALK_KITE]
    found = [(name, e) for name, e in sorted(entries.items()) if tuple(e[:3]) == triple]
    if len(found) != 1:
        raise ValueError(f"census kite {WALK_KITE} exemplars hold {len(found)} entries for {triple}")
    name, (i, j, k, omega, cnots, bits) = found[0]
    walked = [b for b in range(4) if (i | j) >> b & 1]
    if cnots != bin(j).count("1") + bin(i).count("1") + bin(i ^ j).count("1") or bits != len(walked):
        raise ValueError(f"census exemplar {triple}: {cnots} CNOT and {bits} bits differ from the walk of i, j, i^j")
    if omega not in (1, -1):
        raise ValueError(f"census exemplar {triple}: omega {omega}")
    return {"class": name, "i": i, "j": j, "k": k, "omega": omega, "cnots": cnots, "bits": walked}


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


def lower_for_tuna(circuit: Any, pad_pairs: int = 0) -> Any:
    """CNOT as H CZ H on its target; pad_pairs identity CZ pairs follow the first CZ on its own qubits.

    Each padding CZ comes after a barrier on both of its qubits, so adjacent
    CZ gates never meet without a barrier between them.
    """
    from qiskit import QuantumCircuit

    out = QuantumCircuit(circuit.num_qubits, global_phase=circuit.global_phase)
    padded = pad_pairs == 0
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        if name == "cx":
            out.h(qubits[1])
            out.cz(qubits[0], qubits[1])
        elif name in DIALECTS["tuna"]:
            out.append(instruction.operation, qubits)
        else:
            raise ValueError(f"{name} is outside the tuna gate set")
        if name in TWO_QUBIT and not padded:
            for _ in range(2 * pad_pairs):
                out.barrier(*qubits)
                out.cz(qubits[0], qubits[1])
            padded = True
        if name == "cx":
            out.h(qubits[1])
    if not padded:
        raise ValueError("depth padding found no CZ to follow")
    return out


def coherence_setting(row: Row, setting: str) -> Any:
    """reduced_lcu, then the data qubit rotated to read X (H) or Y (Sdag, H) in the computational basis."""
    qc = reduced_lcu(row)
    if setting == "Y":
        qc.sdg(REDUCED_DATA)
    elif setting != "X":
        raise ValueError(f"coherence setting {setting!r} is not X or Y")
    qc.h(REDUCED_DATA)
    return qc


def associator_walk(i: int, j: int, k: int, omega: int, bits: list[int], omit_last: bool = False) -> Any:
    """Control 0 and data 1..len(bits), data qubit 1 + b carrying algebra bit bits[b].

    X prepares the bits of k; H, then Z for omega = -1, on the control;
    CNOT(c -> data) for every set bit of j, then of i, then of i^j unless
    omit_last; H on the control. Bits of k outside `bits` are never walked.
    """
    from qiskit import QuantumCircuit

    if any((mask & ~sum(1 << b for b in bits)) for mask in (i, j)):
        raise ValueError(f"walk ({i}, {j}, {k}) moves bits outside {bits}")
    qc = QuantumCircuit(1 + len(bits))
    for slot, bit in enumerate(bits):
        if k >> bit & 1:
            qc.x(1 + slot)
    qc.h(0)
    if omega < 0:
        qc.z(0)
    for mask in (j, i) if omit_last else (j, i, i ^ j):
        for slot, bit in enumerate(bits):
            if mask >> bit & 1:
                qc.cx(0, 1 + slot)
    qc.h(0)
    return qc


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
    print from their pi/ANGLE_GRID multiple. The tuna dialect writes a
    barrier as one per-qubit barrier line per qubit, a run the platform's
    scheduler aligns; the qx dialect omits barriers.
    """
    if dialect not in DIALECTS:
        raise ValueError(f"dialect {dialect!r} has no gate map")
    names = DIALECTS[dialect]
    lines = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [place[circuit.find_bit(q).index] for q in instruction.qubits]
        if name == "barrier":
            if dialect == "tuna":
                lines += [f"barrier q[{q}]" for q in qubits]
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
QUBIT_REF = re.compile(r"q\[(\d+)\]")


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
            or line in ("b = measure q", "barrier q")
        ):
            continue
        match = GATE_LINE.fullmatch(line)
        if match is not None and match["gate"] == "barrier" and match["b"] is None and match["angle"] is None:
            qc.barrier(int(match["a"]))
            continue
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


def restricted(circuit: Any) -> tuple[Any, dict[int, int]]:
    """The circuit on the qubits its gates touch, renumbered in ascending order, and that map."""
    from qiskit import QuantumCircuit

    used = sorted({circuit.find_bit(q).index for inst in circuit.data for q in inst.qubits})
    index = {q: n for n, q in enumerate(used)}
    out = QuantumCircuit(len(used))
    for instruction in circuit.data:
        out.append(instruction.operation, [index[circuit.find_bit(q).index] for q in instruction.qubits])
    return out, index


def replica_checks(replica: dict[str, Any]) -> list[tuple[str, tuple[int, ...], str]]:
    """(kind, register qubits, prediction) for one manifest replica.

    p_zero: P(q = 0); p_zero_given_zero: P(d = 0 | a = 0); cz_count: CZ lines on the pair.
    """
    roles = replica["roles"]
    checks: list[tuple[str, tuple[int, ...], str]] = []
    if "p_control_zero" in replica:
        checks.append(("p_zero", (roles["control"],), replica["p_control_zero"]))
    else:
        checks.append(("p_zero", (roles["selector"],), replica["p_selector_zero"]))
    if "p_data_zero_given_selector_zero" in replica:
        checks.append(
            ("p_zero_given_zero", (roles["selector"], roles["data"][0]), replica["p_data_zero_given_selector_zero"])
        )
    if "cz_depth" in replica:
        checks.append(("cz_count", (roles["selector"], roles["data"][0]), str(replica["cz_depth"])))
    return checks


def verify_text(item: tuple[str, str, list[tuple[str, tuple[int, ...], str]]]) -> None:
    """Pool worker: an emitted text by state vector on the qubits it uses, against every check."""
    from qiskit.quantum_info import Statevector

    file, text, checks = item
    circuit = parse_cqasm(text)
    compact, index = restricted(circuit)
    state = Statevector(compact)
    measured: set[int] = set()
    for kind, qubits, want in checks:
        if kind == "cz_count":
            pair = set(qubits)
            count = sum(
                inst.operation.name == "cz" and {circuit.find_bit(q).index for q in inst.qubits} == pair
                for inst in circuit.data
            )
            if count != int(want):
                raise ValueError(f"{file}: {count} CZ on q{sorted(pair)} against the declared depth {want}")
            continue
        if qubits[0] in measured and kind == "p_zero":
            raise ValueError(f"{file}: q[{qubits[0]}] serves two replicas")
        if any(q not in index for q in qubits):
            raise ValueError(f"{file}: check {kind} reads q{list(qubits)}, which no gate touches")
        if kind == "p_zero":
            measured.add(qubits[0])
            value = float(state.probabilities([index[qubits[0]]])[0])
        elif kind == "p_zero_given_zero":
            joint = state.probabilities([index[qubits[0]], index[qubits[1]]])
            value = float(joint[0] / (joint[0] + joint[2]))
        else:
            raise ValueError(f"unknown check {kind!r}")
        if abs(value - float(Fraction(want))) > PROBABILITY_TOLERANCE:
            raise ValueError(f"{file}: {kind} on q{list(qubits)} = {value:.12f} against the prediction {want}")


def verify_circuit(item: tuple[str, str, list[tuple[int, str]]]) -> None:
    """Pool worker: each selector marginal of an emitted family (a) text equals its census P."""
    file, text, selectors = item
    verify_text((file, text, [("p_zero", (selector,), p) for selector, p in selectors]))


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
    needed = set(DIALECTS["qx"].values()) | {"measure", "barrier"}
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


def tuna_backend(catalogue: Any) -> dict[str, Any]:
    """The Tuna-17 record admitted by qi_zero_divisor_cases.catalogue_backends, with this layout's gates and shots."""
    backend, _ = catalogue_backends(catalogue)
    if not set(DIALECTS["tuna"].values()) | {"barrier", "measure"} <= set(backend["gateset"]):
        raise SystemExit(f"{TUNA_IDENTIFIER}: catalogue lacks a gate of the tuna dialect")
    if backend["max_number_of_shots"] < T0_SHOTS:
        raise SystemExit(f"{TUNA_IDENTIFIER}: {T0_SHOTS} shots exceed the retained backend capacity")
    if tuple(EXCLUDED_QUBITS) != TUNA_EXCLUDED:
        raise SystemExit(
            f"the retained exclusions {EXCLUDED_QUBITS} differ from the admitted layout's {TUNA_EXCLUDED}; "
            "re-rank the layout before generating"
        )
    return dict(backend)


def check_tuna_text(file: str, text: str, witness: bool = True) -> None:
    """Tuna dialect and admitted layout of one emitted circuit; raises on the first violation."""
    if declared_qubits(text) != TUNA_QUBITS:
        raise ValueError(f"{file}: Tuna circuits declare qubit[{TUNA_QUBITS}]")
    couplers = {tuple(sorted(edge)) for edge in TUNA17}
    single = {name for qk, name in DIALECTS["tuna"].items() if qk not in TWO_QUBIT} | {"barrier"}
    for line in text.splitlines()[5:]:
        if not line or line.startswith("//") or line in ("barrier q", "b = measure q"):
            continue
        match = GATE_LINE.fullmatch(line)
        if match is None or match["angle"] is not None:
            raise ValueError(f"{file}: {line!r} is outside the tuna dialect")
        qubits = [int(match["a"])] + ([int(match["b"])] if match["b"] is not None else [])
        if match["gate"] == "CZ" and len(qubits) == 2:
            if (min(qubits), max(qubits)) not in couplers:
                raise ValueError(f"{file}: CZ on q{qubits}, which no Tuna-17 coupler joins")
        elif match["gate"] not in single or len(qubits) != 1:
            raise ValueError(f"{file}: {line!r} is outside the tuna dialect")
        if witness and set(qubits) & set(TUNA_EXCLUDED + TUNA_AVOIDED):
            raise ValueError(f"{file}: {line!r} touches an excluded or avoided qubit")


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


def finish(
    shared: dict[str, Any], circuits: list[dict[str, Any]], texts: dict[str, str], group: str = "sub_family"
) -> dict[str, str]:
    """batch-NN/ directories of at most HARDWARE_BATCH_CIRCUITS circuits, and the series cases.json.

    Circuits fill batches in manifest order and a batch holds one value of
    the `group` field. Each batch manifest carries every shared field and
    only its own circuits with their replicas, so one batch's run directory
    names the full design.
    """
    chunks: list[list[dict[str, Any]]] = []
    for value in dict.fromkeys(row[group] for row in circuits):
        rows = [row for row in circuits if row[group] == value]
        chunks += [
            rows[start : start + HARDWARE_BATCH_CIRCUITS] for start in range(0, len(rows), HARDWARE_BATCH_CIRCUITS)
        ]
    return write_batches(shared, chunks, texts, group)


def write_batches(
    shared: dict[str, Any], chunks: list[list[dict[str, Any]]], texts: dict[str, str], group: str
) -> dict[str, str]:
    """The batch-NN/ files of the given circuit chunks and the series index; texts are keyed by file name."""
    digits = max(2, len(str(len(chunks) - 1)))
    files: dict[str, str] = {}
    batches = []
    for index, chunk in enumerate(chunks):
        name = f"batch-{index:0{digits}d}"
        rows = []
        for row in chunk:
            text = texts[row["file"]]
            rows.append({**row, "sha256": hashlib.sha256(text.encode()).hexdigest()})
            files[f"{name}/{row['file']}"] = text
        manifest = {**shared, "batch": name, group: chunk[0][group], "circuits": rows}
        files[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": name, group: chunk[0][group], "files": [row["file"] for row in chunk]})
    series_index = {
        "schema": SERIES_SCHEMA,
        "family": shared["family"],
        "backend": shared["backend"],
        "census_sha256": shared["census"]["sha256"],
        "batches": batches,
    }
    files["cases.json"] = json.dumps(series_index, indent=1) + "\n"
    return files


def validate_series(files: dict[str, str], backend: dict[str, Any]) -> None:
    """Offline admission of a generated series: batch sizes, digests, widths, shots and the series index."""
    series_index = json.loads(files["cases.json"])
    listed = set()
    for batch in series_index["batches"]:
        name = batch["batch"]
        manifest = json.loads(files[f"{name}/cases.json"])
        circuits = manifest["circuits"]
        if len(circuits) > HARDWARE_BATCH_CIRCUITS or len(circuits) > backend["max_jobs_per_batch_job"]:
            raise ValueError(f"{name}: {len(circuits)} circuits exceed the {HARDWARE_BATCH_CIRCUITS}-circuit batch")
        if [row["file"] for row in circuits] != batch["files"]:
            raise ValueError(f"{name}: circuits differ from the series index")
        if manifest["shots"] > backend["max_number_of_shots"] or manifest["nqubits"] > backend["nqubits"]:
            raise ValueError(f"{name}: shots or width exceed the backend")
        if manifest["backend"] != backend["identifier"] or manifest["backend_type_id"] != backend["id"]:
            raise ValueError(f"{name}: manifest backend differs from the admitted record")
        for row in circuits:
            text = files[f"{name}/{row['file']}"]
            if hashlib.sha256(text.encode()).hexdigest() != row["sha256"]:
                raise ValueError(f"{name}/{row['file']} differs from its cases.json sha256")
            if declared_qubits(text) != row.get("nqubits", manifest["nqubits"]):
                raise ValueError(f"{name}/{row['file']}: declared width differs from the manifest")
            if (
                manifest["dialect"] == "ry"
                and row["kind"] == "witness"
                and re.search(r"(?m)^(bit\[|b = measure|//)", text)
            ):
                raise ValueError(f"{name}/{row['file']}: a Ry circuit carries a bit register, measure or comment")
            qubits = [q for replica in row.get("replicas", []) for q in replica_qubits(replica["roles"])]
            if len(set(qubits)) != len(qubits) or any(q >= manifest["nqubits"] for q in qubits):
                raise ValueError(f"{name}/{row['file']}: replicas overlap or leave the register")
            if row["kind"] == "readout" and row.get("replicas"):
                raise ValueError(f"{name}/{row['file']}: a readout circuit carries replicas")
            if manifest["dialect"] == "tuna":
                check_tuna_text(f"{name}/{row['file']}", text, witness=row["kind"] != "readout")
            listed.add(f"{name}/{row['file']}")
        if manifest["dialect"] == "tuna":
            kinds = [row["kind"] for row in circuits]
            if kinds != ["witness", "readout", "readout"] or batch["files"][1:] != ["readout-0.cq", "readout-1.cq"]:
                raise ValueError(f"{name}: a Tuna batch is one witness circuit, then readout-0 and readout-1")
        listed.add(f"{name}/cases.json")
    if listed | {"cases.json"} != set(files):
        raise ValueError("series files differ from the batches its cases.json lists")


def replica_qubits(roles: dict[str, Any]) -> list[int]:
    return [q for value in roles.values() for q in (value if isinstance(value, list) else [value])]


def census_record(census_path: Path, census: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": census_path.relative_to(ROOT).as_posix(),
        "schema": census["schema"],
        "sha256": hashlib.sha256(census_path.read_bytes()).hexdigest(),
    }


def qx_encodings() -> dict[str, str]:
    return {
        "full": "designs.lcu_witness: data 0-3, selector 4; x_sign = -1 adds Z on the selector after its first H; "
        f"compiled at optimization level 0 to {', '.join(FULL_BASIS)} with Rz on the pi/{ANGLE_GRID} grid",
        "reduced": "selector a = slot qubit 0, data d = slot qubit 1; SELECT = diag(g(L,L'), g(L,U'), g(U,L'), "
        "g(U,U')) over (a, d) from the census coefficients, then CNOT(a -> d); x_sign = -1 adds Z on a after "
        "its first H",
        "reduced_cross": "selector a, data d, mark w = slot qubits 0, 1, 2; identity diagonal (the census carries "
        "no phases for four-label rows, and P = 1/2 for every sign), CNOT(a -> d), CNOT(a -> w)",
    }


def replica_record(slot: int, encoding: str, row: Row, place: dict[int, int]) -> dict[str, Any]:
    return {
        "slot": slot,
        "census": f"{row['source']}[{row['index']}]",
        "kite": row["kite"],
        "p": [row["p_low"], row["p_high"], row["x_sign"]],
        "q": [row["q_low"], row["q_high"], row["y_sign"]],
        "relation": row["relation"],
        "roles": replica_roles(encoding, place),
        "p_selector_zero": row["p_selector_zero"],
    }


def qx_circuits(
    members: dict[str, list[tuple[str, Row]]], extra: Callable[[str, int], dict[str, Any]] | None = None
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Packed QX circuit rows and texts of each named member list, each list packed at its encoding's width.

    extra(name, position) adds fields to the replica at `position` of member list `name`.
    """
    circuits: list[dict[str, Any]] = []
    jobs: list[tuple[str, list[tuple[str, Row, dict[int, int]]]]] = []
    for sub_family, chosen in members.items():
        if not chosen:
            continue
        encoding = chosen[0][0]
        if any(enc != encoding for enc, _ in chosen):
            raise ValueError(f"{sub_family}: one packed list holds one encoding")
        position = 0
        for number, group in enumerate(pack(chosen, WIDTH[encoding]), start=1):
            file = f"{sub_family}-{number:03d}.cq"
            jobs.append((file, [(enc, row, place) for (enc, row), place in group]))
            replicas = []
            for slot, ((enc, row), place) in enumerate(group):
                replicas.append(
                    {**replica_record(slot, enc, row, place), **(extra(sub_family, position) if extra else {})}
                )
                position += 1
            circuits.append(
                {"file": file, "kind": "witness", "sub_family": sub_family, "encoding": encoding, "replicas": replicas}
            )
    texts = dict(zip((file for file, _ in jobs), parallel.ordered_map(emit_circuit, jobs), strict=True))
    parallel.ordered_map(verify_text, [(row["file"], texts[row["file"]], checks_of(row)) for row in circuits])
    return circuits, texts


def checks_of(row: dict[str, Any]) -> list[tuple[str, tuple[int, ...], str]]:
    return [check for replica in row.get("replicas", []) for check in replica_checks(replica)]


def series(family: str, backend_name: str, census_path: Path = CENSUS, limit: int | None = None) -> dict[str, str]:
    """The exhaustive family (a) case files on QX; limit keeps the first rows of each sub-family."""
    if (family, backend_name) != ("a", "qx"):
        raise ValueError(f"series ({family!r}, {backend_name!r}) is not generated by this pass")
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census = load_census(census_path)
    rows = validate_census(census)

    members: dict[str, list[tuple[str, Row]]] = {}
    for sub_family, sources, encoding in SUB_FAMILIES:
        chosen = [(encoding, row) for source in sources for row in rows[source]]
        members[sub_family] = chosen if limit is None else chosen[:limit]
    every = [item for chosen in members.values() for item in chosen]
    parallel.ordered_map(check_row, every)
    circuits, texts = qx_circuits(members)
    summary = {
        sub_family: {
            "census": [f"design_b.{source}" for source in sources],
            "encoding": encoding,
            "replica_qubits": WIDTH[encoding],
            "replicas_per_circuit": QX_QUBITS // WIDTH[encoding],
            "replicas": len(members[sub_family]),
            "circuits": sum(row["sub_family"] == sub_family for row in circuits),
        }
        for sub_family, sources, encoding in SUB_FAMILIES
    }
    shared = {
        "schema": CASES_SCHEMA,
        "family": family,
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": QX_SHOTS,
        "dialect": backend_name,
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "census": census_record(census_path, census),
        "encodings": qx_encodings(),
        "sub_families": summary,
        "preregistered": preregistered(every),
    }
    files = finish(shared, circuits, texts)
    validate_series(files, backend)
    return files


def smoke_members(rows: dict[str, list[Row]]) -> tuple[dict[str, list[tuple[str, Row]]], dict[tuple[str, int], Any]]:
    """Packed member lists per encoding and the (encoding, position) -> pattern record of each selected row."""
    members: dict[str, list[tuple[str, Row]]] = {"smoke_full": [], "smoke_reduced": [], "smoke_reduced_cross": []}
    patterns: dict[tuple[str, int], Any] = {}
    for name, encoding, source, rule, predicate in SMOKE_PATTERNS:
        row = next((r for r in rows[source] if predicate(r)), None)
        if row is None:
            raise ValueError(f"no census {source} row matches smoke pattern {encoding} {name}: {rule}")
        key = f"smoke_{encoding}"
        patterns[(key, len(members[key]))] = {"pattern": f"{encoding}_{name}", "selection": f"census {source}: {rule}"}
        members[key].append((encoding, row))
    return members, patterns


def smoke_series(census_path: Path = CENSUS) -> dict[str, str]:
    """box_kite_a_qx/: the QX smoke set of family (a), one replica per SMOKE_PATTERNS entry."""
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census = load_census(census_path)
    rows = validate_census(census)
    members, patterns = smoke_members(rows)
    every = [item for chosen in members.values() for item in chosen]
    parallel.ordered_map(check_row, every)
    circuits, texts = qx_circuits(members, lambda name, position: dict(patterns[(name, position)]))
    for row in circuits:
        row["group"] = "smoke"
    shared = {
        "schema": CASES_SCHEMA,
        "family": "a_smoke",
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": QX_SHOTS,
        "dialect": "qx",
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "census": census_record(census_path, census),
        "encodings": qx_encodings(),
        "role": "smoke run of the remote QX compile path (parser, bit order, gate set, angle grid); the exhaustive "
        "family (a) runs on Kaggle CPU through scripts/box_kite_qx_sweep.py",
        "preregistered": {
            **preregistered(every),
            "bonferroni": f"the exhaustive family's bound, z_limit {Z_LIMIT}, applies to every P = 1/2 replica",
        },
    }
    files = finish(shared, circuits, texts, group="group")
    validate_series(files, backend)
    return files


# ---------------------------------------------------------------- Tuna-17 series


def lcu_replica(
    slot: int, row: Row, pair: tuple[int, int], kind: str, depth: int = 1, setting: str | None = None
) -> tuple[dict[str, Any], Any]:
    """Manifest record and Tuna-level circuit of one reduced LCU replica on an LCU pair (selector first)."""
    check_select("reduced", row)
    check_amplitudes("reduced", row, reduced_lcu(row))
    logical_circuit = reduced_lcu(row) if setting is None else coherence_setting(row, setting)
    if depth % 2 != 1:
        raise ValueError(f"CZ depth {depth} is not 1 plus identity pairs")
    circuit = lower_for_tuna(logical_circuit, (depth - 1) // 2)
    record: dict[str, Any] = {
        "slot": slot,
        "kind": kind,
        "census": f"{row['source']}[{row['index']}]",
        "kite": row["kite"],
        "p": [row["p_low"], row["p_high"], row["x_sign"]],
        "q": [row["q_low"], row["q_high"], row["y_sign"]],
        "relation": row["relation"],
        "roles": {"selector": pair[0], "data": [pair[1]]},
        "cz_depth": depth,
        "p_selector_zero": row["p_selector_zero"],
    }
    if setting is not None:
        coh = row["coherence_selector_0"]
        if coh is None:
            raise ValueError(f"census {record['census']}: the selector-0 branch is empty and carries no coherence")
        expectation = 2 * Fraction(coh) if setting == "X" else Fraction(0)
        record["setting"] = setting
        record["coherence_selector_0"] = coh
        record["expectation_given_selector_zero"] = str(expectation)
        record["p_data_zero_given_selector_zero"] = str((1 + expectation) / 2)
    return record, circuit


def walk_replica(
    slot: int, census: dict[str, Any], triple: tuple[int, int, int], layout: str, omit_last: bool
) -> tuple[dict[str, Any], Any]:
    exemplar = walk_exemplar(census, triple)
    control, data = WALK_LAYOUTS[layout]
    if len(data) != len(exemplar["bits"]):
        raise ValueError(f"walk {triple} needs {len(exemplar['bits'])} data qubits; {layout} holds {len(data)}")
    i, j, k, omega = exemplar["i"], exemplar["j"], exemplar["k"], exemplar["omega"]
    circuit = lower_for_tuna(associator_walk(i, j, k, omega, exemplar["bits"], omit_last))
    record = {
        "slot": slot,
        "kind": "walk",
        "census": f"associator.deterministic_exemplars[{WALK_KITE}].{exemplar['class']}",
        "kite": int(WALK_KITE),
        "triple": [i, j, k],
        "omega": omega,
        "omit_last_block": omit_last,
        "layout": layout,
        "roles": {"control": control, "data": list(data)},
        "data_bits": {str(bit): q for bit, q in zip(exemplar["bits"], data, strict=True)},
        "cz": exemplar["cnots"] - (bin(i ^ j).count("1") if omit_last else 0),
        "p_control_zero": "1/2" if omit_last else str(Fraction(1 + omega, 2)),
    }
    return record, circuit


def tuna_text(members: list[tuple[dict[str, Any], Any]]) -> str:
    lines = header(TUNA_QUBITS)
    for record, circuit in members:
        roles = record["roles"]
        if record["kind"] == "walk":
            place = {0: roles["control"], **{1 + n: q for n, q in enumerate(roles["data"])}}
            what = (
                f"walk {tuple(record['triple'])} omega {record['omega']}"
                f"{' omit-last-block' if record['omit_last_block'] else ''} control q[{roles['control']}] "
                f"P(c=0) {record['p_control_zero']}"
            )
        else:
            place = {0: roles["selector"], 1: roles["data"][0]}
            setting = f" setting {record['setting']}" if "setting" in record else ""
            what = (
                f"{record['kind']} census {record['census']} kite {record['kite']} "
                f"({record['p'][0]},{record['p'][1]}){'+' if record['p'][2] > 0 else '-'} x "
                f"({record['q'][0]},{record['q'][1]}){'+' if record['q'][2] > 0 else '-'} {record['relation']} "
                f"depth {record['cz_depth']}{setting} P {record['p_selector_zero']} selector q[{roles['selector']}]"
            )
        lines.append(f"// slot {record['slot']} {what}")
        lines += emit(circuit, place, dialect="tuna")
    return "\n".join(lines + ["", "barrier q", "b = measure q", ""])


def tuna_witnesses(census: dict[str, Any], rows: dict[str, list[Row]]) -> dict[str, list[list[tuple[Any, Any]]]]:
    """Per stage, the replica list of each witness circuit, one circuit per batch."""
    check_twist(census)
    edge = {y: find_row(rows, EDGE_K3, 1, y) for y in (1, -1)}
    twist = {y: find_row(rows, TWIST_K6, 1, y) for y in (1, -1)}
    strut = {y: find_row(rows, STRUT_K3, 1, y) for y in (1, -1)}
    reference = edge[1]
    if reference["p_selector_zero"] != "1" or edge[-1]["p_selector_zero"] != "0":
        raise ValueError("the T0 edge rows lost their (P = 1, P = 0) pair")
    stages: dict[str, list[list[tuple[Any, Any]]]] = {stage: [] for stage in TUNA_STAGES}
    # T0: depth index (pair + batch) mod 3, and y_sign -1 on the diagonal pair == batch, so every
    # depth, pair and batch holds one dark and two bright replicas.
    for batch in range(3):
        stages["t0"].append(
            [
                lcu_replica(p, edge[-1 if p == batch else 1], LCU_PAIRS[p], "lcu", T0_DEPTHS[(p + batch) % 3])
                for p in range(3)
            ]
        )
    # T1: each row keeps its pair in both batches, so D compares one pair across the two
    # batches, and each twist pair (edge at y, twist at -y) shares a batch.
    for y in (1, -1):
        stages["t1"].append(
            [
                lcu_replica(0, edge[y], LCU_PAIRS[0], "lcu"),
                lcu_replica(1, twist[-y], LCU_PAIRS[1], "lcu"),
                lcu_replica(2, strut[y], LCU_PAIRS[2], "lcu"),
            ]
        )
    # Coherence: the bright twist edge and the strut keep their pairs across the X and Y
    # settings; the reference sits on the third pair.
    for setting in ("X", "Y"):
        stages["coherence"].append(
            [
                lcu_replica(0, twist[-1], LCU_PAIRS[0], "coherence", setting=setting),
                lcu_replica(1, strut[1], LCU_PAIRS[1], "coherence", setting=setting),
                lcu_replica(2, reference, LCU_PAIRS[2], "reference"),
            ]
        )
    for _, triple, layout, omit_last in WALKS:
        stages["walk"].append(
            [
                walk_replica(0, census, triple, layout, omit_last),
                lcu_replica(1, reference, LCU_PAIRS[WALK_REFERENCE_PAIR], "reference"),
            ]
        )
    return stages


def tuna_preregistered() -> dict[str, dict[str, Any]]:
    stop = (
        "each batch: every job completed with the manifest's shots; readout-0 P1 at most 0.10 and readout-1 P1 at "
        "least 0.80 on every used qubit (a failure stops the series and re-plans the layout); every bright or "
        "reference replica at P(selector = 0) at least 0.7; circuit digests equal cases.json; the account's queue "
        "empty; a 120 s pause before the next batch"
    )
    corrected = (
        "P(selector = 0) corrected for the selector's readout assignment from the readout-0 and readout-1 circuits "
        "of the same batch"
    )
    return {
        "t0": {
            "observable": "zero-product success P(selector = 0) of the reduced LCU of edge (1,10)(4,15) of kite 3 at "
            f"CZ depths {list(T0_DEPTHS)} (1 plus identity CZ pairs on the replica's own pair)",
            "design": "3 x 3 Latin square: batch b places depth index (pair + b) mod 3 on each pair of LCU_PAIRS, "
            "and y_sign -1 (P = 0) on pair b, y_sign +1 (P = 1) on the other two; every depth, pair and batch "
            "holds one dark and two bright replicas",
            "contrast": f"C(n) = mean Pc(bright, n) - Pc(dark, n) with Pc the {corrected}. The difference cancels "
            "a common additive shift of P (amplitude damping toward |0>, the measured common-shift offset), which "
            "2 Pc(bright) - 1 alone would carry into C as a bias",
            "confound": "the dark replica of each depth sits on one pair in one batch and its brights on the other "
            "two, so C(n) carries that pair's and batch's offset against the mean of the others; the square "
            "balances pair and batch main effects across depths, and a pair x depth interaction stays inside r",
            "fit": "r = exp(slope) of the weighted least-squares line of ln C(n) on n over n = 1, 5, 9; its 99% "
            "interval from a parametric bootstrap of the binomial counts and each batch's readout pair",
            "predictions": "C(1) in [0.72, 0.82]; C(9) / C(1) = r^8 with r in [0.87, 0.96], central 0.955",
            "falsifier": "the pooled depth-1 contrast with its 99% upper bound below 0.5 refutes the shallow "
            "admission and ends the Tuna-17 program; a 99% interval of r disjoint from [0.87, 0.97] refutes the "
            "planning range and resizes T1, coherence and walk before they run",
            "stop_rule": stop,
        },
        "t1": {
            "observable": "zero-product success; classification statistic D = Pc(+, -) - Pc(+, +) per row from its "
            "two replicas on one pair, batch-01 minus batch-00",
            "rows": "opposite-sign edge (1,10)(4,15) of kite 3 on (1, 4), its census twist the same-sign edge "
            "(4,10)(1,15) of kite 6 on (10, 13), strut (1,10)(2,9) of kite 3 on (12, 14); batch-00 holds the edge "
            "at y_sign +1, the twist at -1 and the strut at +1, batch-01 the opposite signs",
            "predictions": "D = -1 opposite edge, +1 twist (same-sign edge), 0 strut; P(edge, y) = P(twist, -y) "
            "under the twist map (L, U, x; L', U', y) -> (L', U, x; L, U', -y)",
            "classification": "D above +0.4 same-sign, below -0.4 opposite-sign, |D| below 0.2 strut, otherwise "
            "unresolved; predicted |D| on edges at least 0.72 (pessimistic)",
            "falsifier": "a row misclassified or unresolved refutes the separation estimate for its pair; a strut "
            "with |D| > 0.1 + 3 sigma exposes a pair-dependent bias the analysis carries; a twist pair whose Pc "
            "differ by more than 3 combined standard errors plus the pair-location allowance (the difference of "
            "the two pairs' depth-1 bright Pc in T0) refutes twist equality for that layout",
            "stop_rule": stop,
        },
        "coherence": {
            "observable": "coherence reconstruction of the selector-0 branch: <X_d | a = 0> on setting X (H on d), "
            "<Y_d | a = 0> on setting Y (Sdag, H on d), each 2 P(d = 0 | a = 0) - 1 with the selector and data "
            "readout corrected from the batch's readout pair",
            "rows": "bright same-sign edge (4,10)+ x (1,15)- of kite 6 on (1, 4), strut (1,10)+ x (2,9)+ of kite 3 "
            "on (10, 13), the reference (1,10)+ x (4,15)+ (P = 1) on (12, 14)",
            "predictions": "edge <X_d> = 2 census coherence_selector_0 = -1 and <Y_d> = 0; strut <X_d> = <Y_d> = 0",
            "falsifier": "sign(<X_d>) opposite to the census coherence at |z| > 3 on the edge, or |<X_d>| above "
            "0.1 + 3 sigma on the strut",
            "stop_rule": stop,
        },
        "walk": {
            "observable": "associator-sign interference witness <Z_c> = 2 Pc(c = 0) - 1 of the fixed-triple walk",
            "rows": "kite 1 exemplars (2,11,3) ij-same-vertex-third-strut omega -1 (6 CNOT, star 11 {8, 13, 14}) "
            "and (2,3,10) jk-same-vertex-third-strut omega -1 (4 CNOT, path 8-11-13), and the omit-last-block "
            "control of (2,11,3); each with the reference on (1, 4)",
            "predictions": "<Z_c> = omega = -1 on both walks, 0 on the control",
            "falsifier": "sign(<Z_c>) opposite to omega at |z| > 3, or the control's |<Z_c>| above 0.1 + 3 sigma",
            "limit": "the walk carries omega as a compiled Z on the control; the hardware establishes coherent return "
            "of the walked register and reads a compiled sign, and an associator-sign witness cannot separate the "
            "octonions from the split octonions",
            "stop_rule": stop,
        },
    }


def tuna_series(census_path: Path = CENSUS) -> dict[str, dict[str, str]]:
    """The four Tuna-17 case directories and the QX twin directory."""
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    tuna = tuna_backend(catalogue)
    qx = qx_backend(catalogue)
    census = load_census(census_path)
    rows = validate_census(census)
    stages = tuna_witnesses(census, rows)
    prereg = tuna_preregistered()
    readout = readout_circuits(TUNA_QUBITS)
    shots = {"t0": T0_SHOTS, "t1": FOLLOW_SHOTS, "coherence": FOLLOW_SHOTS, "walk": FOLLOW_SHOTS}
    layout = {
        "excluded": list(TUNA_EXCLUDED),
        "avoided": list(TUNA_AVOIDED),
        "lcu_pairs": [list(p) for p in LCU_PAIRS],
        "walks": {name: {"control": c, "data": list(d)} for name, (c, d) in WALK_LAYOUTS.items()},
    }
    directories: dict[str, dict[str, str]] = {}
    witness_jobs: list[tuple[str, str, list[tuple[str, tuple[int, ...], str]]]] = []
    twin_rows: list[dict[str, Any]] = []
    twin_texts: dict[str, str] = {}
    for stage in TUNA_STAGES:
        chunks: list[list[dict[str, Any]]] = []
        texts: dict[str, str] = {}
        for index, members in enumerate(stages[stage]):
            file = f"{stage}-{index + 1}.cq"
            text = tuna_text(members)
            witness = {"file": file, "kind": "witness", "stage": stage, "replicas": [r for r, _ in members]}
            texts[file] = text
            witness_jobs.append((f"box_kite_tuna_{stage}/{file}", text, checks_of(witness)))
            chunks.append(
                [
                    witness,
                    {"file": "readout-0.cq", "kind": "readout", "stage": stage, "prepared": 0},
                    {"file": "readout-1.cq", "kind": "readout", "stage": stage, "prepared": 1},
                ]
            )
            twin_row, twin_text = twin(witness, text, f"box_kite_tuna_{stage}/batch-{index:02d}/{file}")
            twin_rows.append(twin_row)
            twin_texts[twin_row["file"]] = twin_text
        texts.update(readout)
        shared = {
            "schema": CASES_SCHEMA,
            "family": f"tuna_{stage}",
            "backend": tuna["identifier"],
            "backend_type_id": tuna["id"],
            "nqubits": tuna["nqubits"],
            "shots": shots[stage],
            "dialect": "tuna",
            "bit_order": "qubit 0 at the rightmost character (Tuna)",
            "census": census_record(census_path, census),
            "layout": layout,
            "encodings": {
                "reduced": "selector a = the pair's first qubit, data d = its second; reduced two-label LCU with "
                "CNOT as H CZ H on d; CZ depth n repeats CZ(a, d) (n - 1) times after the SELECT CZ, each after "
                "a per-qubit barrier run",
                "walk": "control c on q11, data bits on the layout's data qubits in ascending bit order; CNOT as "
                "H CZ H on the data qubit; omega as Z on c after its first H",
                "readout": "readout-0 measures all 17 qubits in |0>, readout-1 after X on all 17",
            },
            "preregistered": prereg[stage],
        }
        files = write_batches(shared, chunks, texts, "stage")
        validate_series(files, tuna)
        directories[f"box_kite_tuna_{stage}"] = files
    twin_shared = {
        "schema": CASES_SCHEMA,
        "family": "tuna_twins",
        "backend": qx["identifier"],
        "backend_type_id": qx["id"],
        "nqubits": qx["nqubits"],
        "shots": QX_SHOTS,
        "dialect": "qx",
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "census": census_record(census_path, census),
        "twin_of": tuna["identifier"],
        "role": "the gate list of each Tuna-17 witness circuit relabeled onto QX qubits 0-9 (qubit_map: Tuna "
        "qubit -> QX qubit), run on the remote ideal emulator before its Tuna batch; the identical Tuna bytes run on "
        "local qxelarator",
        "preregistered": {
            "falsifier": "any shot violating a deterministic replica refutes the emitted cQASM; a P = 1/2 replica "
            f"outside |z| < {Z_LIMIT} at {QX_SHOTS} shots refutes it",
        },
    }
    twin_files = finish(twin_shared, twin_rows, twin_texts, group="stage")
    validate_series(twin_files, qx)
    directories["box_kite_tuna_twins_qx"] = twin_files
    parallel.ordered_map(
        verify_text, witness_jobs + [(row["file"], twin_texts[row["file"]], checks_of(row)) for row in twin_rows]
    )
    return directories


def twin(witness: dict[str, Any], text: str, source: str) -> tuple[dict[str, Any], str]:
    """The witness circuit's gate list on QX qubits 0..n-1, Tuna qubits in ascending order, and its manifest row."""
    lines = text.splitlines()
    if lines[:5] != header(TUNA_QUBITS):
        raise ValueError(f"{source}: twin() takes a Tuna witness circuit")
    used = sorted({int(q) for line in lines[5:] if not line.startswith("//") for q in QUBIT_REF.findall(line)})
    if len(used) > QX_QUBITS:
        raise ValueError(f"{source}: {len(used)} active qubits exceed the QX register")
    mapping = {q: n for n, q in enumerate(used)}
    body = [QUBIT_REF.sub(lambda m: f"q[{mapping[int(m[1])]}]", line) for line in lines[5:]]
    if not text.endswith("\n"):
        raise ValueError(f"{source}: circuit text lacks its final newline")
    twin_text = "\n".join(header(QX_QUBITS) + body) + "\n"

    def moved(value: Any) -> Any:
        return [mapping[q] for q in value] if isinstance(value, list) else mapping[value]

    replicas = []
    for replica in witness["replicas"]:
        relabeled = {**replica, "roles": {role: moved(value) for role, value in replica["roles"].items()}}
        if "data_bits" in replica:
            relabeled["data_bits"] = {bit: mapping[q] for bit, q in replica["data_bits"].items()}
        replicas.append(relabeled)
    row = {
        "file": f"twin-{witness['file']}",
        "kind": "witness",
        "stage": witness["stage"],
        "tuna_case": source,
        "qubit_map": {str(q): n for q, n in mapping.items()},
        "replicas": replicas,
    }
    return row, twin_text


def case_directories() -> dict[str, dict[str, str]]:
    return {"box_kite_a_qx": smoke_series(), **tuna_series(), **ry_series()}


# ---------------------------------------------------------------- Ry emulator


def ry_backend(catalogue: Any) -> dict[str, Any]:
    """Admit the retained Ry emulator record: identity, width, all-to-all topology, the ry dialect and 1024 shots."""
    matches = [
        b for b in catalogue.get("backend_types", []) if isinstance(b, dict) and b.get("identifier") == RY_IDENTIFIER
    ]
    if len(matches) != 1:
        raise SystemExit(f"catalogue needs exactly one {RY_IDENTIFIER} backend type")
    backend = matches[0]
    if (backend.get("id"), backend.get("nqubits")) != (RY_BACKEND_TYPE_ID, RY_QUBITS):
        raise SystemExit(f"{RY_IDENTIFIER}: backend identity or width changed; review the cases")
    complete = {(a, b) for a in range(RY_QUBITS) for b in range(RY_QUBITS) if a != b}
    topology = backend.get("topology")
    if not isinstance(topology, list) or {tuple(e) for e in topology if isinstance(e, list)} != complete:
        raise SystemExit(f"{RY_IDENTIFIER}: topology is no longer all-to-all; the packing needs review")
    if not set(DIALECTS["ry"].values()) <= set(backend.get("gateset", [])):
        raise SystemExit(f"{RY_IDENTIFIER}: catalogue lacks a gate of the ry dialect")
    if (
        backend.get("max_number_of_shots", 0) < RY_SHOTS
        or backend.get("max_jobs_per_batch_job", 0) < HARDWARE_BATCH_CIRCUITS
    ):
        raise SystemExit(f"{RY_IDENTIFIER}: cases exceed the retained backend capacity")
    return dict(backend)


def lower_for_ry(circuit: Any) -> Any:
    """Sdag as Rz(-pi/2); every other gate must lie in the ry dialect."""
    from qiskit import QuantumCircuit

    out = QuantumCircuit(circuit.num_qubits, global_phase=circuit.global_phase)
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        if name == "sdg":
            out.rz(-math.pi / 2, qubits[0])
        elif name in DIALECTS["ry"]:
            out.append(instruction.operation, qubits)
        elif name != "barrier":
            raise ValueError(f"{name} is outside the ry gate set")
    return out


def ry_text(width: int, body: list[str]) -> str:
    """A Ry program: no bit register, no measure statement and no comment, which the retained probe found it needs."""
    return "\n".join(["version 3.0", "", f"qubit[{width}] q", "", *body, ""])


def leftmost_distribution(text: str) -> dict[str, str]:
    """Outcome probabilities of a text by state vector, keyed with qubit 0 at the leftmost character (Ry)."""
    from qiskit.quantum_info import Statevector

    out = {}
    for key, prob in sorted(Statevector(parse_cqasm(text)).probabilities_dict().items()):
        if prob < PROBABILITY_TOLERANCE:
            continue
        exact = Fraction(prob).limit_denominator(1 << 12)
        if abs(float(exact) - prob) > PROBABILITY_TOLERANCE:
            raise ValueError(f"outcome probability {prob} is not a dyadic fraction")
        out[key[::-1]] = str(exact)
    return dict(sorted(out.items()))


def ry_ladder() -> tuple[list[dict[str, Any]], dict[str, str]]:
    """The diagnostic factors the retained construct probe leaves open: width 9, a comment line, teleport.cq bare."""
    source = RY_TELEPORT.read_bytes()
    if hashlib.sha256(source).hexdigest() != RY_TELEPORT_SHA256:
        raise ValueError(f"{RY_TELEPORT.relative_to(ROOT)} differs from its recorded digest")
    bare = [line for line in source.decode().splitlines()[3:] if line and not line.startswith(("//", "bit["))]
    factors = (
        ("r1-width-9.cq", "R1", "qubit[9] around the program that ran (X on q[0])", ry_text(9, ["X q[0]"])),
        (
            "r2-comment.cq",
            "R2",
            "one // comment line in the program that ran",
            ry_text(2, ["// one comment line", "X q[0]"]),
        ),
        ("r9-teleport-bare.cq", "R9", "teleport.cq without its bit register and comments", ry_text(9, bare)),
    )
    rows, texts = [], {}
    for file, label, factor, text in factors:
        texts[file] = text
        rows.append(
            {
                "file": file,
                "kind": "diagnostic",
                "group": "ladder",
                "nqubits": declared_qubits(text),
                "ladder": label,
                "factor": factor,
                "expected_leftmost": leftmost_distribution(text),
            }
        )
    return rows, texts


def ry_smoke(rows: dict[str, list[Row]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """The reduced smoke replicas and the T1 edge and twist, four per 9-atom circuit, and the (1,10) full witnesses."""
    members, patterns = smoke_members(rows)
    reduced = [(item, patterns[("smoke_reduced", n)]["pattern"]) for n, item in enumerate(members["smoke_reduced"])]
    reduced += [
        (("reduced", find_row(rows, spec, 1, y)), f"t1_{name}_y{'+' if y > 0 else '-'}")
        for name, spec in (("edge", EDGE_K3), ("twist", TWIST_K6))
        for y in (1, -1)
    ]
    full = [
        (("full", find_row(rows, EDGE_K3, 1, -1)), "full_witness_dark"),
        (("full", find_row(rows, EDGE_K3, 1, 1)), "full_witness_bright"),
        (("full", rows["negative_fixture"][0]), "full_negative_fixture"),
    ]
    parallel.ordered_map(check_row, [item for item, _ in reduced + full])
    groups = [(f"ry-reduced-{n + 1}.cq", group) for n, group in enumerate(pack(reduced, 2, RY_QUBITS, per_circuit=4))]
    groups += [(f"ry-{name.replace('_', '-')}.cq", [((item, name), {q: q for q in range(5)})]) for item, name in full]
    circuits: list[dict[str, Any]] = []
    texts: dict[str, str] = {}
    for file, group in groups:
        body: list[str] = []
        replicas: list[dict[str, Any]] = []
        for slot, (((encoding, row), name), place) in enumerate(group):
            body += emit(lower_for_ry(basis_circuit(encoding, row)), place, dialect="ry")
            replicas.append({**replica_record(slot, encoding, row, place), "pattern": name})
        texts[file] = ry_text(RY_QUBITS, body)
        circuits.append({"file": file, "kind": "witness", "group": "smoke", "replicas": replicas})
    parallel.ordered_map(verify_text, [(row["file"], texts[row["file"]], checks_of(row)) for row in circuits])
    return circuits, texts


def ry_series(census_path: Path = CENSUS) -> dict[str, dict[str, str]]:
    """box_kite_ry_ladder/ (one batch) and box_kite_ry_smoke/ (two batches) for the Ry emulator."""
    backend = ry_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census = load_census(census_path)
    rows = validate_census(census)
    common = {
        "schema": CASES_SCHEMA,
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "shots": RY_SHOTS,
        "dialect": "ry",
        "bit_order": "qubit 0 at the leftmost character (Ry)",
        "census": census_record(census_path, census),
    }
    ladder_rows, ladder_texts = ry_ladder()
    for row in ladder_rows:
        if leftmost_distribution(ladder_texts[row["file"]]) != row["expected_leftmost"]:
            raise ValueError(f"{row['file']}: expected distribution differs from its state vector")
    ladder = {
        **common,
        "family": "ry_ladder",
        "nqubits": max(row["nqubits"] for row in ladder_rows),
        "role": "the diagnostic factors the construct probe (results/quantum_inspire/ry_probe_analysis.json) leaves "
        "open; that probe completed X, H, CNOT and Rz and failed every program with a bit register (error "
        "interpreting cQASM script) or a measure statement (not in the primitive gate set), so R3, R7 and R8 "
        "are settled",
        "preregistered": {
            "observable": "completion or failure of each job, and its counts read with qubit 0 leftmost",
            "falsifier": "a completed job whose counts leave an expected outcome's |z| < 4.5 or show an outcome of "
            "probability 0 is reported as an emulator rate; a failed job names its factor",
            "stop_rule": "R1 failing stops the smoke subset, whose circuits declare qubit[9]",
        },
    }
    ladder_files = finish(ladder, ladder_rows, ladder_texts, group="group")
    validate_series(ladder_files, backend)
    smoke_rows, smoke_texts = ry_smoke(rows)
    smoke = {
        **common,
        "family": "ry_smoke",
        "nqubits": RY_QUBITS,
        "encodings": {
            **qx_encodings(),
            "ry": "Sdag written as Rz(-pi/2); no bit register, measure or comment; the emulator measures every "
            "atom at the end",
        },
        "role": "smoke subset after R1 passes: the reduced smoke replicas of family (a), the T1 edge and its twist "
        "at y_sign +-1, and the (1,10) full Design B dark, bright and fixture witnesses",
        "preregistered": {
            "observable": "zero-product success P(selector = 0) per replica, selector bits read with qubit 0 leftmost",
            "falsifier": "a deterministic replica below 0.9 of its ideal outcome is reported with the emulator's "
            "raw rates as an emulator rate, never as an algebraic result",
            "stop_rule": "a deterministic replica below 0.9 of its ideal outcome stops the series",
        },
    }
    smoke_files = finish(smoke, smoke_rows, smoke_texts, group="group")
    validate_series(smoke_files, backend)
    return {"box_kite_ry_ladder": ladder_files, "box_kite_ry_smoke": smoke_files}


def summary(directories: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    """Circuits, witness circuits, batches, shots per circuit and replicas of each case directory."""
    out = []
    for name, files in directories.items():
        batches = json.loads(files["cases.json"])["batches"]
        manifests = [json.loads(files[f"{b['batch']}/cases.json"]) for b in batches]
        circuits = [row for m in manifests for row in m["circuits"]]
        out.append(
            {
                "directory": name,
                "backend": manifests[0]["backend"],
                "batches": len(batches),
                "circuits": len(circuits),
                "witness_circuits": sum(row["kind"] == "witness" for row in circuits),
                "replicas": sum(len(row.get("replicas", [])) for row in circuits),
                "shots_per_circuit": manifests[0]["shots"],
                "shots": sum(m["shots"] * len(m["circuits"]) for m in manifests),
            }
        )
    return out


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
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    backend = qx_backend(catalogue)
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

    # Smoke selection: every sign-variant pattern lands on a deterministic edge row.
    members, patterns = smoke_members(rows)
    for (key, position), record in patterns.items():
        row = members[key][position][1]
        if ("x_minus" in record["pattern"] or "y_minus" in record["pattern"]) and row["p_selector_zero"] == "1/2":
            raise AssertionError(f"smoke pattern {record['pattern']} selected a P = 1/2 row")

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
    reject("an unknown dialect", lambda: emit(logical("reduced", within[0]), {0: 0, 1: 1}, dialect="ry"))
    reject("an off-grid Rz angle", lambda: snap_angle(math.pi / 3))

    # Tuna dialect and layout.
    reject("a CNOT in the tuna dialect", lambda: emit(logical("reduced", within[0]), {0: 1, 1: 4}, dialect="tuna"))
    rz = QuantumCircuit(2)
    rz.rz(math.pi / 2, 0)
    reject("an Rz in the tuna dialect", lambda: lower_for_tuna(rz))
    reject("padding without a CZ", lambda: lower_for_tuna(QuantumCircuit(2), 1))
    tuna_dirs = tuna_series()
    t0 = tuna_dirs["box_kite_tuna_t0"]
    t0_manifest = json.loads(t0["batch-00/cases.json"])
    t0_text = t0["batch-00/t0-1.cq"]
    tuna = tuna_backend(catalogue)
    deep = next(r for r in t0_manifest["circuits"][0]["replicas"] if r["cz_depth"] > 1)
    pair = f"CZ q[{deep['roles']['selector']}], q[{deep['roles']['data'][0]}]"
    short = t0_text.replace(pair + "\n", "", 1)
    reject("a padded replica missing one CZ", lambda: verify_text(("t0", short, checks_of(t0_manifest["circuits"][0]))))
    verify_text(("t0", t0_text, checks_of(t0_manifest["circuits"][0])))
    reject("a CZ off the coupling graph", lambda: check_tuna_text("t0", t0_text.replace(pair, "CZ q[1], q[10]", 1)))
    reject("an excluded qubit in a witness", lambda: check_tuna_text("t0", t0_text.replace("H q[4]", "H q[9]", 1)))
    reject("a rotation in a Tuna circuit", lambda: check_tuna_text("t0", t0_text.replace("H q[4]", "Rz(0.1) q[4]", 1)))
    wide = t0_text.replace("qubit[17] q", "qubit[10] q", 1)
    reject("a Tuna circuit narrower than qubit[17]", lambda: check_tuna_text("t0", wide))
    swapped = dict(t0)
    swapped["batch-00/cases.json"] = (
        json.dumps(
            {
                **t0_manifest,
                "circuits": [t0_manifest["circuits"][1], t0_manifest["circuits"][0], *t0_manifest["circuits"][2:]],
            },
            indent=1,
        )
        + "\n"
    )
    index = json.loads(t0["cases.json"])
    index["batches"][0]["files"] = [row["file"] for row in json.loads(swapped["batch-00/cases.json"])["circuits"]]
    swapped["cases.json"] = json.dumps(index, indent=1) + "\n"
    reject("a Tuna batch whose witness does not lead", lambda: validate_series(swapped, tuna))
    walk = tuna_dirs["box_kite_tuna_walk"]
    walk_row = json.loads(walk["batch-00/cases.json"])["circuits"][0]
    walk_text = walk["batch-00/walk-1.cq"]
    verify_text(("walk", walk_text, checks_of(walk_row)))
    control_z = f"Z q[{walk_row['replicas'][0]['roles']['control']}]"
    reject(
        "a walk without its omega Z",
        lambda: verify_text(("walk", walk_text.replace(control_z + "\n", "", 1), checks_of(walk_row))),
    )
    coherence_dir = tuna_dirs["box_kite_tuna_coherence"]
    coh_row = json.loads(coherence_dir["batch-00/cases.json"])["circuits"][0]
    coh_text = coherence_dir["batch-00/coherence-1.cq"]
    verify_text(("coherence", coh_text, checks_of(coh_row)))
    edge_data = coh_row["replicas"][0]["roles"]["data"][0]
    lines = coh_text.splitlines()
    last_h = max(n for n, line in enumerate(lines) if line == f"H q[{edge_data}]")
    lines.insert(last_h, f"Z q[{edge_data}]")
    reject(
        "a coherence setting with its sign flipped",
        lambda: verify_text(("coherence", "\n".join(lines), checks_of(coh_row))),
    )
    mutated = copy.deepcopy(census)
    mutated["kites"][2]["twists"][0]["twisted_kite"] = 5
    reject("a census twist that no longer maps the T1 edge", lambda: check_twist(mutated))
    mutated = copy.deepcopy(census)
    mutated["associator"]["deterministic_exemplars"][WALK_KITE]["ij-same-vertex-third-strut"][4] = 5
    reject("an exemplar whose CNOT count leaves the walk", lambda: walk_exemplar(mutated, (2, 11, 3)))
    twins = tuna_dirs["box_kite_tuna_twins_qx"]
    twin_row = json.loads(twins["batch-00/cases.json"])["circuits"][0]
    twin_text = twins[f"batch-00/{twin_row['file']}"]
    verify_text(("twin", twin_text, checks_of(twin_row)))
    moved = {**twin_row, "replicas": [{**r, "roles": {**r["roles"], "selector": 9}} for r in twin_row["replicas"][:1]]}
    reject("a twin replica read on the wrong qubit", lambda: verify_text(("twin", twin_text, checks_of(moved))))

    # Ry dialect, ladder and smoke series.
    strut_row = next(row for row in within if row["relation"] == "strut")
    reject("an Sdag in the ry dialect", lambda: emit(logical("reduced", strut_row), {0: 0, 1: 1}, dialect="ry"))
    emit(lower_for_ry(logical("reduced", strut_row)), {0: 0, 1: 1}, dialect="ry")
    cz = QuantumCircuit(2)
    cz.cz(0, 1)
    reject("a CZ in the ry dialect", lambda: lower_for_ry(cz))
    ry = ry_series()
    ry_record = ry_backend(catalogue)
    smoke_ry = ry["box_kite_ry_smoke"]
    first_ry = json.loads(smoke_ry["cases.json"])["batches"][0]
    target = f"{first_ry['batch']}/{first_ry['files'][0]}"
    manifest_ry = json.loads(smoke_ry[f"{first_ry['batch']}/cases.json"])
    bits = smoke_ry[target].replace("qubit[9] q\n", "qubit[9] q\nbit[9] b\n", 1)
    rows_ry = [
        {**row, "sha256": hashlib.sha256(bits.encode()).hexdigest()} if row["file"] == first_ry["files"][0] else row
        for row in manifest_ry["circuits"]
    ]
    with_bits = {
        **smoke_ry,
        target: bits,
        f"{first_ry['batch']}/cases.json": json.dumps({**manifest_ry, "circuits": rows_ry}, indent=1) + "\n",
    }
    reject("a Ry witness with a bit register", lambda: validate_series(with_bits, ry_record))
    validate_series(ry["box_kite_ry_ladder"], ry_record)
    saved = globals()["RY_TELEPORT_SHA256"]
    globals()["RY_TELEPORT_SHA256"] = "0" * 64
    try:
        reject("a changed teleport.cq digest", ry_ladder)
    finally:
        globals()["RY_TELEPORT_SHA256"] = saved
    altered = copy.deepcopy(catalogue)
    entry = next(b for b in altered["backend_types"] if b["identifier"] == RY_IDENTIFIER)
    entry["gateset"] = [g for g in entry["gateset"] if g != "CNOT"]
    reject("a Ry gate set without CNOT", lambda: ry_backend(altered), SystemExit)

    # Catalogue admission.
    for field, value in (("nqubits", 9), ("id", 2), ("is_hardware", True), ("topology", backend["topology"][1:])):
        altered = copy.deepcopy(catalogue)
        next(b for b in altered["backend_types"] if b["identifier"] == QX_IDENTIFIER)[field] = value
        reject(f"a changed QX {field}", lambda a=altered: qx_backend(a), SystemExit)
    altered = copy.deepcopy(catalogue)
    entry = next(b for b in altered["backend_types"] if b["identifier"] == QX_IDENTIFIER)
    entry["gateset"] = [g for g in entry["gateset"] if g != "Rz"]
    reject("a QX gate set without Rz", lambda: qx_backend(altered), SystemExit)
    altered = copy.deepcopy(catalogue)
    entry = next(b for b in altered["backend_types"] if b["identifier"] == TUNA_IDENTIFIER)
    entry["gateset"] = [g for g in entry["gateset"] if g != "Sdag"]
    reject("a Tuna-17 gate set without Sdag", lambda: tuna_backend(altered), SystemExit)
    print(
        f"box-kite cases: census, SELECT, state-vector, packing, batch, Tuna layout, twin, Ry and catalogue contracts "
        f"pass; {rejected} mutations rejected"
    )


# ---------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="DIR")
    mode.add_argument("--check", type=Path, metavar="DIR")
    mode.add_argument("--summary", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        directories = case_directories()
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if list(directories) != list(CASE_DIRECTORIES):
        raise SystemExit(f"generated directories {list(directories)} differ from CASE_DIRECTORIES")
    if args.summary:
        print(json.dumps(summary(directories), indent=1))
        return 0
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
