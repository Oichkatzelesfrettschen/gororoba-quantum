"""Box-kite cases for Quantum Inspire, generated from the retained box-kite census.

docs/notes/box_kites/experiment-program.md fixes the design. Every sign comes
from docs/evidence/box_kite_census/census.json; the generator recomputes none
from cd_core. Five products come out of one census read:

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
- The Tuna-17 pre-T0 batch (box_kite_tuna_pre/: X, a per-qubit barrier run
  and X on all 17 qubits, then readout-0 and readout-1), which separates an
  under-rotated X from |1> misassignment on Q0 and Q6 and re-reads the
  layout's readout before T0, and its 10-qubit QX twin.
- The Tuna-17 series T0 (depth ladder), T1 (edge-sign classification and
  twist), coherence and walk, each batch one witness circuit plus readout-0
  and readout-1, and the relabeled QX twin of every witness circuit.
  Each stage's preregistered block carries its numeric thresholds, which
  scripts/box_kite_analysis.py reads from the retained manifests.
- Families (d1)-(d3) and (e), exhaustive in memory (series_de(): 149 QX
  circuits, the associator-sign witnesses on fixed triples, fixed pairs with
  uniform k and fixed i with uniform (j, k), and the full-encoding coherence
  settings) for the same sweep, and their smoke representatives, the first
  circuit of each sub-family, written to box_kite_de_qx/.
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
import itertools
import json
import math
import re
import sys
import tempfile
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS, declared_qubits  # noqa: E402
from qi_zero_divisor_cases import (  # noqa: E402
    EXCLUDED_QUBITS,
    READOUT_EXCLUDED,
    TUNA17,
    catalogue_backends,
    header,
    readout_circuits,
    visibility_excluded,
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
# the larger shot count. The follow series reads conditional coherences on
# about half the shots of each branch and phase differences at the 0.01 level,
# and a Tuna-17 shot costs about 0.5 ms against a 120 s pause per batch, so it
# takes the same count (docs/notes/quantum_inspire/tuna-17-run-design.md).
T0_SHOTS = 16384
FOLLOW_SHOTS = 16384
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
DE_SUB_FAMILIES = ("d1_fixed_triple", "d2_fixed_pair", "d3_fixed_i", "e_full_coherence")
D3_WIDTH = 9
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
# LCU_PAIRS is a maximum induced matching of the admitted coupling graph: no
# coupler joins two pairs, so three replicas run side by side without a CZ
# next to another replica's qubit.
LCU_PAIRS = ((1, 4), (10, 13), (12, 14))
# The walk set the pre-T0 batch read its readout stop rule on; its retained
# cases fix it.
WALK_LAYOUTS: dict[str, tuple[int, tuple[int, ...]]] = {"star_11": (11, (8, 13, 14)), "path_8_11_13": (11, (8, 13))}
T0_DEPTHS = (1, 5, 9)
# Follow-series walks: a 3-data star and a 2-data path with no qubit or
# coupler in common, so one circuit carries both. Among the stars that admit
# such a path on the admitted qubits, star_14 with data (11, 12, 16) loses the
# least contrast to the retained static ZZ under both a 60 ns and a 0.8 us CZ
# window (docs/notes/quantum_inspire/tuna-17-run-design.md).
FOLLOW_WALK_LAYOUTS: dict[str, tuple[int, tuple[int, ...]]] = {"star_14": (14, (11, 12, 16)), "path_4": (4, (1, 2))}
FOLLOW_WALKS = (((2, 11, 3), "star_14"), ((2, 3, 10), "path_4"))
FOLLOW_DEPTHS = (5, 9)
# Census rows by (kite, (p_low, p_high), x_sign, (q_low, q_high), y_sign).
EDGE_K3 = (3, (1, 10), (4, 15))  # opposite-sign edge of kite 3, the acquired (1,10) witness pair
TWIST_K6 = (6, (4, 10), (1, 15))  # its twist, a same-sign edge of kite 6 (census kites[2].twists[0])
STRUT_K3 = (3, (1, 10), (2, 9))
WALK_KITE = "1"
TUNA_STAGES = ("t0", "follow")
# Per-batch sanity limits of every Tuna-17 stage. An idle qubit of a witness
# circuit reads within IDLE_MARGIN of its own readout-0 P1; a replica's
# outcome moved onto an idle position (a reversed bit order) leaves it.
READOUT_0_P1_MAX = 0.10
READOUT_1_P1_MIN = 0.80
BRIGHT_P_MIN = 0.7
# The floor reads state preparation where the contrast is highest; deeper T0 replicas enter only
# through C(n) and r, whose pessimistic range puts a depth-9 bright replica near 0.6.
BRIGHT_FLOOR_CZ_DEPTHS = (1,)
IDLE_MARGIN = 0.15
# Two-sided 99% normal quantile; the T0 depth-1 bound is C(1) + Z99 SE.
Z99 = 2.5758293035489004
T0_C1_FLOOR = 0.5
T0_R_RANGE = (0.87, 0.97)
T0_C1_PREDICTION = (0.72, 0.82)
BOOTSTRAP_DRAWS = 4000
BOOTSTRAP_SEED = 20261017
T1_SAME_ABOVE, T1_OPPOSITE_BELOW, T1_STRUT_BELOW = 0.4, -0.4, 0.2
NULL_OFFSET, SIGMA = 0.1, 3.0
# Readout brackets: a used qubit whose e01 or e10 moves more than this between
# two brackets stops the series. T0's three batches moved at most 0.0071.
BRACKET_DRIFT_MAX = 0.02
# Cross-prediction band around r ** n_CZ for the walk magnitudes and the
# depth-1 conditional coherences.
CROSS_PREDICTION_BAND = 0.10
# T0's fitted contrast decay per CZ (claim qi-tuna17-boxkite-t0-depth-ladder).
T0_R = 0.9654
RY_DETERMINISTIC_MIN = 0.9
# Pre-T0 double-X batch (claim proposed-tuna17-q0-q6-double-x-discriminator).
PRE_SHOTS = 4096
PRE_CLAIM = "proposed-tuna17-q0-q6-double-x-discriminator"
RESEARCH_STATE = ROOT / "docs/state/research_state.json"
PRE_PREDICTIONS = {"under_rotation": {"0": 0.98, "6": 0.52}, "misassignment": {"0": 0.038, "6": 0.013}}
PRE_FAULT_P1_GIVEN_1_BELOW = {"0": 0.7, "6": 0.3}
PRE_UNDER_ROTATION_ABOVE = {"0": 0.5, "6": 0.25}
PRE_MISASSIGNMENT_BELOW = {"0": 0.1, "6": 0.1}
PRE_READMISSION = (5, 6, 7, 9)
CASE_DIRECTORIES = (
    "box_kite_a_qx",
    "box_kite_tuna_pre",
    "box_kite_tuna_t0",
    "box_kite_tuna_follow",
    "box_kite_tuna_twins_qx",
    "box_kite_ry_ladder",
    "box_kite_ry_smoke",
    "box_kite_de_qx",
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


def associator_walk(
    i: int, j: int, k: int, omega: int, bits: list[int], omit_last: bool = False, readout: str = "X"
) -> Any:
    """Control 0 and data 1..len(bits), data qubit 1 + b carrying algebra bit bits[b].

    X prepares the bits of k; H, then Z for omega = -1, on the control;
    CNOT(c -> data) for every set bit of j, then of i, then of i^j unless
    omit_last; H on the control. Bits of k outside `bits` are never walked.
    Readout Y puts Sdag before the last H, so Z on the control after it reads
    S X Sdag = Y: 2 P(c = 0) - 1 = <Y_c>, the imaginary part of the overlap.
    """
    if readout not in ("X", "Y"):
        raise ValueError(f"walk readout {readout!r} is not X or Y")
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
    if readout == "Y":
        qc.sdg(0)
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


def snap_angle(theta: float, grid: int = ANGLE_GRID) -> int:
    k = round(theta * grid / math.pi)
    if abs(theta - k * math.pi / grid) > ANGLE_TOLERANCE:
        raise ValueError(f"Rz angle {theta!r} is off the pi/{grid} grid")
    return k


def emit(circuit: Any, place: dict[int, int], dialect: str = "qx", angle_grid: int | None = ANGLE_GRID) -> list[str]:
    """cQASM 3.0 lines of a basis-level replica; place maps its local qubits to register indices.

    The circuit's global phase is unobservable and is not written. Rz angles
    print from their pi/angle_grid multiple, which rejects an angle off that
    grid; angle_grid None prints the angle itself at the same 15 decimals.
    The tuna dialect writes a barrier as one per-qubit barrier line per
    qubit, a run the platform's scheduler aligns; the qx dialect omits
    barriers. No dialect maps rz into tuna or reset into any backend, so a
    Tuna text carries no angle to quantize and no text reaches qxelarator's
    reset.
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
            theta = float(instruction.operation.params[0])
            if angle_grid is not None:
                theta = snap_angle(theta, angle_grid) * math.pi / angle_grid
            lines.append(f"{names[name]}({theta:.15f}) q[{qubits[0]}]")
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

    p_zero: P(q = 0); p_zero_given_zero and p_zero_given_one: P(d = 0 | a = 0) and P(d = 0 | a = 1);
    parity_zero_given_zero: P(the data bits have even parity | selector = 0); cz_count: CZ lines on the pair.
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
    if "p_data_zero_given_selector_one" in replica:
        checks.append(
            ("p_zero_given_one", (roles["selector"], roles["data"][0]), replica["p_data_zero_given_selector_one"])
        )
    if "p_parity_even_given_selector_zero" in replica:
        checks.append(
            (
                "parity_zero_given_zero",
                (roles["selector"], *roles["data"]),
                replica["p_parity_even_given_selector_zero"],
            )
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
        elif kind in ("p_zero_given_zero", "p_zero_given_one"):
            joint = state.probabilities([index[qubits[0]], index[qubits[1]]])
            branch = int(kind == "p_zero_given_one")
            value = float(joint[branch] / (joint[branch] + joint[2 + branch]))
        elif kind == "parity_zero_given_zero":
            joint = state.probabilities([index[q] for q in qubits])
            kept = [n for n in range(len(joint)) if n % 2 == 0]
            value = float(sum(joint[n] for n in kept if bin(n >> 1).count("1") % 2 == 0) / sum(joint[n] for n in kept))
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
    bracketed: list[bool] = []
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
                check_tuna_text(f"{name}/{row['file']}", text, witness=row["kind"] == "witness")
            if row["kind"] == "diagnostic" and "ideal_p1" in row:
                check_double_x(f"{name}/{row['file']}", text)
            listed.add(f"{name}/{row['file']}")
        if manifest["dialect"] == "tuna":
            # A diagnostic circuit (the pre-T0 double X) addresses every qubit by design;
            # a witness keeps to the admitted layout.
            kinds = [row["kind"] for row in circuits]
            pair = ["readout-0.cq", "readout-1.cq"]
            if manifest.get("readout_calibration") == "bracketed":
                if not (
                    kinds == ["witness"] * HARDWARE_BATCH_CIRCUITS
                    or (kinds == ["readout", "readout", "witness"] and batch["files"][:2] == pair)
                    or (kinds == ["witness", "readout", "readout"] and batch["files"][1:] == pair)
                ):
                    raise ValueError(f"{name}: a bracketed Tuna batch is three witnesses or a readout pair and one")
                bracketed.append("readout" in kinds)
            elif (
                kinds[0] not in ("witness", "diagnostic")
                or kinds[1:] != ["readout", "readout"]
                or batch["files"][1:] != pair
            ):
                raise ValueError(f"{name}: a Tuna batch is one witness circuit, then readout-0 and readout-1")
        listed.add(f"{name}/cases.json")
    if listed | {"cases.json"} != set(files):
        raise ValueError("series files differ from the batches its cases.json lists")
    if bracketed:
        gaps = "".join("R" if b else "." for b in bracketed).split("R")
        if not (bracketed[0] and bracketed[-1]) or max(map(len, gaps)) > BRACKET_SPAN:
            raise ValueError(
                f"a bracketed series needs readout pairs in its first and last batch and at most {BRACKET_SPAN} "
                "witness-only batches between two pairs"
            )


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
    slot: int,
    row: Row,
    pair: tuple[int, int],
    kind: str,
    depth: int = 1,
    setting: str | None = None,
    label: str | None = None,
) -> tuple[dict[str, Any], Any]:
    """Manifest record and Tuna-level circuit of one reduced LCU replica on an LCU pair (selector first).

    With a setting, the data qubit is read in X or Y, and the record carries
    the conditional data prediction of every selector branch the row populates.
    """
    check_select("reduced", row)
    check_amplitudes("reduced", row, reduced_lcu(row))
    logical_circuit = reduced_lcu(row) if setting is None else coherence_setting(row, setting)
    if depth % 2 != 1:
        raise ValueError(f"CZ depth {depth} is not 1 plus identity pairs")
    circuit = lower_for_tuna(logical_circuit, (depth - 1) // 2)
    record: dict[str, Any] = {
        "slot": slot,
        "kind": kind,
        **({"label": label} if label is not None else {}),
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
        record["setting"] = setting
        populated = 0
        for branch, name in (("0", "zero"), ("1", "one")):
            coh = row[f"coherence_selector_{branch}"]
            if coh is None:
                continue
            populated += 1
            expectation = 2 * Fraction(coh) if setting == "X" else Fraction(0)
            record[f"coherence_selector_{branch}"] = coh
            record[f"expectation_given_selector_{name}"] = str(expectation)
            record[f"p_data_zero_given_selector_{name}"] = str((1 + expectation) / 2)
        if not populated:
            raise ValueError(f"census {record['census']}: no selector branch carries a coherence")
    return record, circuit


def walk_replica(
    slot: int,
    census: dict[str, Any],
    triple: tuple[int, int, int],
    layout: str,
    omit_last: bool,
    readout: str = "X",
    layouts: dict[str, tuple[int, tuple[int, ...]]] = FOLLOW_WALK_LAYOUTS,
) -> tuple[dict[str, Any], Any]:
    exemplar = walk_exemplar(census, triple)
    control, data = layouts[layout]
    if len(data) != len(exemplar["bits"]):
        raise ValueError(f"walk {triple} needs {len(exemplar['bits'])} data qubits; {layout} holds {len(data)}")
    i, j, k, omega = exemplar["i"], exemplar["j"], exemplar["k"], exemplar["omega"]
    circuit = lower_for_tuna(associator_walk(i, j, k, omega, exemplar["bits"], omit_last, readout))
    balanced = omit_last or readout == "Y"
    record = {
        "slot": slot,
        "kind": "walk",
        "census": f"associator.deterministic_exemplars[{WALK_KITE}].{exemplar['class']}",
        "kite": int(WALK_KITE),
        "triple": [i, j, k],
        "omega": omega,
        "omit_last_block": omit_last,
        "readout": readout,
        "layout": layout,
        "roles": {"control": control, "data": list(data)},
        "data_bits": {str(bit): q for bit, q in zip(exemplar["bits"], data, strict=True)},
        "cz": exemplar["cnots"] - (bin(i ^ j).count("1") if omit_last else 0),
        "p_control_zero": "1/2" if balanced else str(Fraction(1 + omega, 2)),
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
                f"{' omit-last-block' if record['omit_last_block'] else ''}"
                f"{' readout Y' if record['readout'] == 'Y' else ''} control q[{roles['control']}] "
                f"P(c=0) {record['p_control_zero']}"
            )
        else:
            place = {0: roles["selector"], 1: roles["data"][0]}
            setting = f" setting {record['setting']}" if "setting" in record else ""
            label = f" {record['label']}" if "label" in record else ""
            what = (
                f"{record['kind']}{label} census {record['census']} kite {record['kite']} "
                f"({record['p'][0]},{record['p'][1]}){'+' if record['p'][2] > 0 else '-'} x "
                f"({record['q'][0]},{record['q'][1]}){'+' if record['q'][2] > 0 else '-'} {record['relation']} "
                f"depth {record['cz_depth']}{setting} P {record['p_selector_zero']} selector q[{roles['selector']}]"
            )
        lines.append(f"// slot {record['slot']} {what}")
        lines += emit(circuit, place, dialect="tuna")
    return "\n".join(lines + ["", "barrier q", "b = measure q", ""])


# The follow series in submission order. Each witness name is a circuit file;
# readout-0 and readout-1 bracket the witnesses at the start, the middle and
# the end, so no witness sits more than one batch from a readout pair.
FOLLOW_PLAN = (
    ("readout-0", "readout-1", "walk-x"),
    ("lcu-bright-x-1", "lcu-bright-x-2", "depth-9-x"),
    ("lcu-bright-y-1", "lcu-bright-y-2", "depth-9-y"),
    ("readout-0", "readout-1", "walk-omit"),
    ("lcu-dark-x-1", "lcu-dark-x-2", "depth-5-x"),
    ("lcu-dark-y-1", "lcu-dark-y-2", "depth-5-y"),
    ("walk-y", "readout-0", "readout-1"),
)
# Witness-only batches allowed between two readout brackets.
BRACKET_SPAN = 2


def follow_witnesses(census: dict[str, Any], rows: dict[str, list[Row]]) -> dict[str, list[tuple[Any, Any]]]:
    """The fifteen follow witnesses by name: crossover LCU pairs, the coherence depth ladder and the walks.

    lcu-{bright,dark}-{x,y}-{1,2} are 2 x 2 crossovers: the edge and its twist
    at the opposite y_sign trade the pairs LCU_PAIRS[0] and [1] between
    circuits 1 and 2 of a setting, so the twist difference averaged over both
    pairs cancels the pair and the circuit offsets. LCU_PAIRS[2] holds the
    edge at both signs in the bright block and the strut at both signs in the
    dark block. depth-{5,9}-{x,y} put the bright edge at that CZ depth on all
    three pairs. walk-x, walk-omit and walk-y carry both FOLLOW_WALKS read in
    X, with the last block omitted, and read in Y.
    """
    check_twist(census)
    edge = {y: find_row(rows, EDGE_K3, 1, y) for y in (1, -1)}
    twist = {y: find_row(rows, TWIST_K6, 1, y) for y in (1, -1)}
    strut = {y: find_row(rows, STRUT_K3, 1, y) for y in (1, -1)}
    if edge[1]["p_selector_zero"] != "1" or twist[-1]["p_selector_zero"] != "1":
        raise ValueError("the follow crossover lost its bright pair (edge +, twist -)")
    if edge[-1]["p_selector_zero"] != "0" or twist[1]["p_selector_zero"] != "0":
        raise ValueError("the follow crossover lost its dark pair (edge -, twist +)")
    named = {**{f"edge{'+' if y > 0 else '-'}": r for y, r in edge.items()}}
    named |= {f"twist{'+' if y > 0 else '-'}": r for y, r in twist.items()}
    named |= {f"strut{'+' if y > 0 else '-'}": r for y, r in strut.items()}

    def circuit(labels: tuple[str, str, str], setting: str, depth: int = 1) -> list[tuple[Any, Any]]:
        return [
            lcu_replica(slot, named[label], LCU_PAIRS[slot], "lcu", depth, setting, label)
            for slot, label in enumerate(labels)
        ]

    witnesses: dict[str, list[tuple[Any, Any]]] = {}
    for setting in ("X", "Y"):
        s = setting.lower()
        witnesses[f"lcu-bright-{s}-1"] = circuit(("edge+", "twist-", "edge-"), setting)
        witnesses[f"lcu-bright-{s}-2"] = circuit(("twist-", "edge+", "edge+"), setting)
        witnesses[f"lcu-dark-{s}-1"] = circuit(("edge-", "twist+", "strut+"), setting)
        witnesses[f"lcu-dark-{s}-2"] = circuit(("twist+", "edge-", "strut-"), setting)
        for depth in FOLLOW_DEPTHS:
            witnesses[f"depth-{depth}-{s}"] = circuit(("edge+", "edge+", "edge+"), setting, depth)
    for name, omit_last, readout in (("walk-x", False, "X"), ("walk-omit", True, "X"), ("walk-y", False, "Y")):
        witnesses[name] = [
            walk_replica(slot, census, triple, layout, omit_last, readout)
            for slot, (triple, layout) in enumerate(FOLLOW_WALKS)
        ]
    planned = [name for batch in FOLLOW_PLAN for name in batch if not name.startswith("readout-")]
    if sorted(planned) != sorted(witnesses) or len(planned) != len(set(planned)):
        raise ValueError("FOLLOW_PLAN does not list every follow witness exactly once")
    return witnesses


def tuna_witnesses(census: dict[str, Any], rows: dict[str, list[Row]]) -> list[list[tuple[Any, Any]]]:
    """The T0 witness circuits, one per batch: a 3 x 3 Latin square of CZ depth over the LCU pairs."""
    check_twist(census)
    edge = {y: find_row(rows, EDGE_K3, 1, y) for y in (1, -1)}
    if edge[1]["p_selector_zero"] != "1" or edge[-1]["p_selector_zero"] != "0":
        raise ValueError("the T0 edge rows lost their (P = 1, P = 0) pair")
    # Depth index (pair + batch) mod 3, and y_sign -1 on the diagonal pair == batch, so every
    # depth, pair and batch holds one dark and two bright replicas.
    return [
        [
            lcu_replica(p, edge[-1 if p == batch else 1], LCU_PAIRS[p], "lcu", T0_DEPTHS[(p + batch) % 3])
            for p in range(3)
        ]
        for batch in range(3)
    ]


def sanity_thresholds() -> dict[str, Any]:
    return {
        "readout_0_p1_at_most": READOUT_0_P1_MAX,
        "readout_1_p1_at_least": READOUT_1_P1_MIN,
        "bright_p_selector_zero_at_least": BRIGHT_P_MIN,
        "bright_floor_cz_depths": list(BRIGHT_FLOOR_CZ_DEPTHS),
        "idle_p1_above_readout_0_at_most": IDLE_MARGIN,
    }


def tuna_preregistered() -> dict[str, dict[str, Any]]:
    stop = (
        f"each batch: every job completed with the manifest's shots; readout-0 P1 at most {READOUT_0_P1_MAX:.2f} "
        f"and readout-1 P1 at least {READOUT_1_P1_MIN:.2f} on every used qubit (a failure stops the series and "
        "re-plans the layout); every bright or reference replica at CZ depth 1 at raw P(selector = 0) at least "
        f"{BRIGHT_P_MIN:g} (deeper replicas enter only through C(n) and r); "
        f"every qubit the witness leaves idle at P1 at most {IDLE_MARGIN:g} above its readout-0 P1 (bit-order "
        "conformance); circuit digests equal cases.json; the account's queue empty; a 120 s pause before the next "
        "batch"
    )
    sanity = sanity_thresholds()
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
            "fit": "r = exp(slope) of the weighted least-squares line of ln C(n) on n over n = 1, 5, 9, weights "
            "C(n)^2 / Var C(n); its two-sided 99% interval from the 0.5 and 99.5 percentiles of a parametric "
            f"bootstrap ({BOOTSTRAP_DRAWS} draws, seed {BOOTSTRAP_SEED}) of the binomial counts and each batch's "
            "readout pair",
            "predictions": f"C(1) in [{T0_C1_PREDICTION[0]}, {T0_C1_PREDICTION[1]}]; C(9) / C(1) = r^8 with r in "
            "[0.87, 0.96], central 0.955",
            "falsifier": f"the pooled depth-1 contrast with its 99% upper bound C(1) + {Z99:.4f} SE below "
            f"{T0_C1_FLOOR} refutes the shallow admission and ends the Tuna-17 program; a 99% interval of r disjoint "
            f"from [{T0_R_RANGE[0]}, {T0_R_RANGE[1]}] refutes the planning range and resizes T1, coherence and walk "
            "before they run",
            "stop_rule": stop,
            "thresholds": {
                **sanity,
                "depths": list(T0_DEPTHS),
                "depth_1_contrast_upper_bound_floor": T0_C1_FLOOR,
                "upper_bound_z": Z99,
                "r_planning_range": list(T0_R_RANGE),
                "c1_prediction": list(T0_C1_PREDICTION),
                "bootstrap_draws": BOOTSTRAP_DRAWS,
                "bootstrap_seed": BOOTSTRAP_SEED,
                "interval_percentiles": [0.5, 99.5],
            },
        },
        "follow": {
            "observable": "per LCU replica the selector success P(a = 0) and, for every populated selector branch b, "
            "the data expectation E_b = <S_d | a = b> = 2 P(d = 0 | a = b) - 1 in the replica's setting S (X: H on "
            "d; Y: Sdag, H on d); per walk the control expectation 2 P(c = 0) - 1, which reads <X_c> (readout X) or "
            "<Y_c> (readout Y: Sdag, H on c)",
            "design": "seven batches in FOLLOW_PLAN order. lcu-{bright,dark}-{x,y}-{1,2}: 2 x 2 crossovers in which "
            "the edge (1,10)(4,15) of kite 3 at y_sign y and its census twist (4,10)(1,15) of kite 6 at -y trade "
            "the pairs (1, 4) and (10, 13) between circuits 1 and 2; (12, 14) holds the edge at both signs in the "
            "bright block and the strut (1,10)(2,9) at both signs in the dark block. depth-{5,9}-{x,y}: the bright "
            "edge at that CZ depth on all three pairs. walk-x, walk-omit, walk-y: the kite 1 exemplars (2,11,3) on "
            "star 14 {11, 12, 16} (6 CZ) and (2,3,10) on path 4 {1, 2} (4 CZ), read in X, with the last block "
            "omitted, and read in Y",
            "readout": "readout-0 and readout-1 in batches 0, 3 and 6; each qubit's e01 and e10 at a witness job are "
            "interpolated linearly in job finish time between the two nearest brackets, with the binomial variance "
            "of both brackets; the bracket difference enters as a reported systematic. Pc = (p - e10) / (1 - e01 - "
            "e10) on the selector; E_b inverts the tensor product of the selector's and the data qubit's "
            "assignment matrices on the joint (a, d) counts",
            "classification": f"D = Pc(y_sign -1) - Pc(y_sign +1) per row and pair, pooled over the settings: D "
            f"above +{T1_SAME_ABOVE} same-sign (twist), below {T1_OPPOSITE_BELOW} opposite-sign (edge), |D| below "
            f"{T1_STRUT_BELOW} strut, otherwise unresolved; a misclassified or unresolved row refutes the "
            "separation of its pair",
            "twist": "per block (bright: edge +, twist -; dark: edge -, twist +) and setting, Delta = "
            "[(Pc(edge, pair 0, circuit 1) - Pc(twist, pair 0, circuit 2)) + (Pc(edge, pair 1, circuit 2) - "
            "Pc(twist, pair 1, circuit 1))] / 2, in which the pair and circuit offsets cancel; the census predicts "
            f"Delta = 0, and |Delta| above {SIGMA:g} standard errors refutes twist equality for that block and "
            "setting. The edge and the twist differ only in their local Z, S and Sdag gates, so a refutation "
            "measures a gate-dependent error between them",
            "strut": f"D of the strut on (12, 14) per setting; |D| above {NULL_OFFSET} + {SIGMA:g} sigma exposes a "
            "pair-dependent bias",
            "coherence": "census predictions: E_0 = -1 on the bright edge and twist in X, E_1 = +1 on the dark edge "
            "and twist in X, 0 in Y and 0 on both strut branches. Falsifier: an X expectation of sign opposite to "
            f"the census at |z| > {SIGMA:g}, or a strut |E_b| above {NULL_OFFSET} + {SIGMA:g} sigma. "
            f"Cross-prediction: the depth-1 magnitude |E_b| in X equals T0's C(1) = 0.954 within "
            f"{CROSS_PREDICTION_BAND}, the value a depolarizing error of the two-qubit block gives",
            "depth_ladder": "per pair, the bright edge at CZ depths 1 (the lcu-bright circuits), 5 and 9 gives the "
            "conditional magnitude m(n) = sqrt(E_X^2 + E_Y^2), the phase phi(n) = atan2(E_Y, -E_X) about the "
            "census value -1, and the population Pc(n) of the same replicas; the joint coherence J(n) = Pc(n) m(n) "
            "and the population contrast 2 Pc(n) - 1 both equal lambda^n under a global depolarizing channel of "
            "rate lambda per CZ, so r_coh and r_pop are exp(slope) of ln J(n) and ln(2 Pc(n) - 1) on n and their "
            "ratio is 1 there, while dephasing lowers it and amplitude damping raises r_pop; the phase slope is "
            "phi per CZ, the data qubit's detuning phase over one CZ window plus the CZ's residual local phase. "
            "Each is an unweighted least-squares slope with a 99% parametric-bootstrap interval "
            f"({BOOTSTRAP_DRAWS} draws, seed {BOOTSTRAP_SEED}), reported as estimates",
            "walks": f"<X_c> = omega = -1 on both walks, 0 on both omit-last controls and 0 in Y. Falsifier: sign "
            f"opposite to omega at |z| > {SIGMA:g}, or a control's |<X_c>| above {NULL_OFFSET} + {SIGMA:g} sigma. "
            "Cross-prediction: sqrt(<X_c>^2 + <Y_c>^2) equals r^n_CZ for T0's r = "
            f"{T0_R}, 0.810 on the star and 0.869 on the path, within {CROSS_PREDICTION_BAND}; the phase "
            "atan2(<Y_c>, -<X_c>) is reported",
            "replication": "the depth-5 and depth-9 bright edge populations per pair against T0's values on the "
            "same pair and depth, reported as drift over the hours between the series",
            "stop_rule": f"each batch: every job completed with the manifest's shots; circuit digests equal "
            f"cases.json; the account's queue empty; a 120 s pause before the next batch. At each readout "
            f"bracket: readout-0 P1 at most {READOUT_0_P1_MAX:.2f} and readout-1 P1 at least "
            f"{READOUT_1_P1_MIN:.2f} on every used qubit, and no used qubit's e01 or e10 moved more than "
            f"{BRACKET_DRIFT_MAX} since the previous bracket; a failure stops the series. Every depth-1 "
            f"deterministic LCU replica within {1 - BRIGHT_P_MIN:g} of its ideal raw P(selector = 0), and a "
            f"walk read in X at raw P(c = 1) at least {BRIGHT_P_MIN:g}; every idle qubit at P1 at most "
            f"{IDLE_MARGIN:g} above its interpolated readout-0 P1",
            "thresholds": {
                **sanity,
                "deterministic_floor_margin": round(1 - BRIGHT_P_MIN, 12),
                "same_sign_above": T1_SAME_ABOVE,
                "opposite_sign_below": T1_OPPOSITE_BELOW,
                "strut_abs_below": T1_STRUT_BELOW,
                "null_offset": NULL_OFFSET,
                "sigma": SIGMA,
                "bracket_drift_max": BRACKET_DRIFT_MAX,
                "bracket_span": BRACKET_SPAN,
                "cross_prediction_band": CROSS_PREDICTION_BAND,
                "t0_r": T0_R,
                "t0_c1": 0.954,
                "depths": [1, *FOLLOW_DEPTHS],
                "bootstrap_draws": BOOTSTRAP_DRAWS,
                "bootstrap_seed": BOOTSTRAP_SEED,
                "interval_percentiles": [0.5, 99.5],
            },
        },
    }


def tuna_series(census_path: Path = CENSUS) -> dict[str, dict[str, str]]:
    """The pre-T0, T0 and follow Tuna-17 case directories and the QX twin directory."""
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    tuna = tuna_backend(catalogue)
    qx = qx_backend(catalogue)
    census = load_census(census_path)
    rows = validate_census(census)
    prereg = tuna_preregistered()
    readout = readout_circuits(TUNA_QUBITS)
    layout = {
        "excluded": list(TUNA_EXCLUDED),
        "avoided": list(TUNA_AVOIDED),
        "lcu_pairs": [list(p) for p in LCU_PAIRS],
        "walks": {name: {"control": c, "data": list(d)} for name, (c, d) in WALK_LAYOUTS.items()},
    }
    directories: dict[str, dict[str, str]] = {"box_kite_tuna_pre": pre_series(tuna, census_path, census, layout)}
    witness_jobs: list[tuple[str, str, list[tuple[str, tuple[int, ...], str]]]] = []
    twins: dict[str, list[tuple[dict[str, Any], str]]] = {"t0": [], "follow": []}

    def witness(stage: str, file: str, members: list[tuple[Any, Any]], batch: int) -> dict[str, Any]:
        text = tuna_text(members)
        row = {"file": file, "kind": "witness", "stage": stage, "replicas": [r for r, _ in members]}
        texts[file] = text
        witness_jobs.append((f"box_kite_tuna_{stage}/{file}", text, checks_of(row)))
        twins[stage].append(twin(row, text, f"box_kite_tuna_{stage}/batch-{batch:02d}/{file}"))
        return row

    def readout_row(stage: str, prepared: int) -> dict[str, Any]:
        return {"file": f"readout-{prepared}.cq", "kind": "readout", "stage": stage, "prepared": prepared}

    # T0: one witness, then the batch's own readout pair.
    texts: dict[str, str] = dict(readout)
    chunks = [
        [witness("t0", f"t0-{index + 1}.cq", members, index), readout_row("t0", 0), readout_row("t0", 1)]
        for index, members in enumerate(tuna_witnesses(census, rows))
    ]
    shared = {
        "schema": CASES_SCHEMA,
        "family": "tuna_t0",
        "backend": tuna["identifier"],
        "backend_type_id": tuna["id"],
        "nqubits": tuna["nqubits"],
        "shots": T0_SHOTS,
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
        "preregistered": prereg["t0"],
    }
    files = write_batches(shared, chunks, texts, "stage")
    validate_series(files, tuna)
    directories["box_kite_tuna_t0"] = files

    # Follow: FOLLOW_PLAN batches with readout brackets.
    texts = dict(readout)
    follow = follow_witnesses(census, rows)
    chunks = [
        [
            readout_row("follow", int(name[-1])) if name.startswith("readout-") else
            witness("follow", f"{name}.cq", follow[name], index)
            for name in batch
        ]
        for index, batch in enumerate(FOLLOW_PLAN)
    ]  # fmt: skip
    shared = {
        **shared,
        "family": "tuna_follow",
        "shots": FOLLOW_SHOTS,
        "layout": {
            **layout,
            "walks": {name: {"control": c, "data": list(d)} for name, (c, d) in FOLLOW_WALK_LAYOUTS.items()},
        },
        "readout_calibration": "bracketed",
        "encodings": {
            "reduced": "selector a = the pair's first qubit, data d = its second; reduced two-label LCU with "
            "CNOT as H CZ H on d; setting X adds H on d and setting Y adds Sdag, H on d before the measurement; "
            "CZ depth n repeats CZ(a, d) (n - 1) times after the SELECT CZ, each after a per-qubit barrier run",
            "walk": "control c and the data bits on the layout's data qubits in ascending bit order; CNOT as H CZ H "
            "on the data qubit; omega as Z on c after its first H; readout Y adds Sdag on c before its last H",
            "readout": "readout-0 measures all 17 qubits in |0>, readout-1 after X on all 17",
        },
        "preregistered": prereg["follow"],
    }
    files = write_batches(shared, chunks, texts, "stage")
    validate_series(files, tuna)
    directories["box_kite_tuna_follow"] = files

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
    # Batch-04 keeps the double-X twin, whose retained run binds that batch name.
    pre_row, pre_text = pre_twin()
    follow_twins = [row for row, _ in twins["follow"]]
    twin_chunks = [
        [row for row, _ in twins["t0"]],
        *(follow_twins[start : start + HARDWARE_BATCH_CIRCUITS] for start in range(0, 9, HARDWARE_BATCH_CIRCUITS)),
        [pre_row],
        *(follow_twins[start : start + HARDWARE_BATCH_CIRCUITS] for start in range(9, 15, HARDWARE_BATCH_CIRCUITS)),
    ]
    twin_texts = {row["file"]: text for row, text in twins["t0"] + twins["follow"]} | {pre_row["file"]: pre_text}
    twin_files = write_batches(twin_shared, twin_chunks, twin_texts, "stage")
    validate_series(twin_files, qx)
    directories["box_kite_tuna_twins_qx"] = twin_files
    pre_text_17 = directories["box_kite_tuna_pre"][f"batch-00/{PRE_FILE}"]
    parallel.ordered_map(
        verify_text,
        witness_jobs
        + [(row["file"], twin_texts[row["file"]], checks_of(row)) for row, _ in twins["t0"] + twins["follow"]]
        + [(PRE_FILE, pre_text_17, double_x_checks(range(TUNA_QUBITS)))],
    )
    return directories


PRE_FILE = "double-x.cq"


def double_x_lines(qubits: list[int]) -> list[str]:
    """X on each qubit, a per-qubit barrier run, X again: a merge pass that cancels adjacent X pairs meets a barrier."""
    return [f"X q[{q}]" for q in qubits] + [f"barrier q[{q}]" for q in qubits] + [f"X q[{q}]" for q in qubits]


def double_x_text(nqubits: int) -> str:
    comment = "// double X on every qubit, a per-qubit barrier run between the two layers; ideal P1 0 on every qubit"
    return "\n".join(
        header(nqubits) + [comment, *double_x_lines(list(range(nqubits))), "", "barrier q", "b = measure q", ""]
    )


def check_double_x(file: str, text: str) -> None:
    """Every declared qubit carries X, its own barrier, X, in that order, and nothing else before the measurement."""
    sequence: dict[int, list[str]] = {q: [] for q in range(declared_qubits(text))}
    for line in text.splitlines()[5:]:
        if not line or line.startswith("//") or line in ("barrier q", "b = measure q"):
            continue
        match = GATE_LINE.fullmatch(line)
        if match is None or match["b"] is not None or match["gate"] not in ("X", "barrier"):
            raise ValueError(f"{file}: {line!r} is outside the double-X circuit")
        sequence[int(match["a"])].append(match["gate"])
    bad = [q for q, ops in sequence.items() if ops != ["X", "barrier", "X"]]
    if bad:
        raise ValueError(f"{file}: q{bad} lack the X, barrier, X sequence")


def double_x_checks(qubits: Any) -> list[tuple[str, tuple[int, ...], str]]:
    return [("p_zero", (q,), "1") for q in qubits]


def pre_qubits() -> list[int]:
    """The fault qubits Q0 and Q6 with every qubit of the LCU pairs and the walk layouts, ascending."""
    used = {0, 6} | {q for pair in LCU_PAIRS for q in pair}
    used |= {q for control, data in WALK_LAYOUTS.values() for q in (control, *data)}
    return sorted(used)


def pre_twin() -> tuple[dict[str, Any], str]:
    """The double-X circuit on QX qubits 0-9 for the Tuna qubits pre_qubits() in ascending order."""
    used = pre_qubits()
    if len(used) != QX_QUBITS:
        raise ValueError(f"the double-X twin needs {QX_QUBITS} Tuna qubits; pre_qubits() holds {len(used)}")
    text = double_x_text(QX_QUBITS)
    row: dict[str, Any] = {
        "file": f"twin-{PRE_FILE}",
        "kind": "diagnostic",
        "stage": "pre",
        "tuna_case": f"box_kite_tuna_pre/batch-00/{PRE_FILE}",
        "qubit_map": {str(q): n for n, q in enumerate(used)},
        "dropped": [q for q in range(TUNA_QUBITS) if q not in used],
        "ideal_p1": "0",
        "falsifier": "any shot with a 1 on any qubit refutes the emitted cQASM",
    }
    verify_text((row["file"], text, double_x_checks(range(QX_QUBITS))))
    return row, text


def pre_claim(path: Path = RESEARCH_STATE) -> dict[str, Any]:
    """The registry entry of PRE_CLAIM; its statement must carry every prediction of PRE_PREDICTIONS.

    The self-test runs this check; the manifest names the claim by id and
    registry path only, so a later edit of the claim leaves the case bytes,
    and the digests a run binds, unchanged.
    """
    matches = [c for c in json.loads(path.read_text(encoding="utf-8"))["claims"] if c.get("id") == PRE_CLAIM]
    if len(matches) != 1:
        raise ValueError(f"{path.relative_to(ROOT)} holds {len(matches)} claims {PRE_CLAIM}")
    claim = matches[0]
    for hypothesis in PRE_PREDICTIONS.values():
        quoted = " and ".join(f"{hypothesis[q]:g}" for q in ("0", "6"))
        if quoted not in claim["statement"]:
            raise ValueError(f"claim {PRE_CLAIM} no longer states the predictions {quoted}")
    return {"id": PRE_CLAIM, "registry": path.relative_to(ROOT).as_posix(), "statement": claim["statement"]}


def pre_series(
    tuna: dict[str, Any], census_path: Path, census: dict[str, Any], layout: dict[str, Any]
) -> dict[str, str]:
    """box_kite_tuna_pre/: one Tuna-17 batch of the double-X diagnostic, readout-0 and readout-1."""
    lcu = sorted({q for pair in LCU_PAIRS for q in pair})
    walk = sorted({q for control, data in WALK_LAYOUTS.values() for q in (control, *data)})
    visibility = set(visibility_excluded())
    basis = {
        str(q): [name for name, members in (("readout", READOUT_EXCLUDED), ("visibility", visibility)) if q in members]
        for q in PRE_READMISSION
    }
    if any(not reasons for reasons in basis.values()):
        raise ValueError(f"a re-admission candidate of {PRE_READMISSION} carries no retained exclusion")
    fault = ", ".join(f"Q{q} P(1|1) < {v}" for q, v in PRE_FAULT_P1_GIVEN_1_BELOW.items())
    under = " and ".join(f"Q{q} P(1|XX) > {v}" for q, v in PRE_UNDER_ROTATION_ABOVE.items())
    mis = " and ".join(f"Q{q} P(1|XX) < {v}" for q, v in PRE_MISASSIGNMENT_BELOW.items())
    shared = {
        "schema": CASES_SCHEMA,
        "family": "tuna_pre",
        "backend": tuna["identifier"],
        "backend_type_id": tuna["id"],
        "nqubits": tuna["nqubits"],
        "shots": PRE_SHOTS,
        "dialect": "tuna",
        "bit_order": "qubit 0 at the rightmost character (Tuna)",
        "census": census_record(census_path, census),
        "layout": layout,
        "encodings": {
            "double_x": "X on all 17 qubits, a per-qubit barrier run, X on all 17 again, no wait, then the "
            "measurement; ideal P1 0 on every qubit",
            "readout": "readout-0 measures all 17 qubits in |0>, readout-1 after X on all 17",
        },
        "preregistered": {
            "observable": "per-qubit raw P(1|0) from readout-0, P(1|1) from readout-1 and P(1|XX) from double-x, "
            "each with its binomial standard error",
            "claim": {"id": PRE_CLAIM, "registry": RESEARCH_STATE.relative_to(ROOT).as_posix()},
            "predictions": "raw P(1|XX): Q0 0.98 and Q6 0.52 under X under-rotation by the angle the zero-wait "
            "P(1|1) implies, Q0 0.038 and Q6 0.013 (the idle floor) under |1> misassignment",
            "precondition": f"the batch's own readout pair still shows the fault ({fault}); otherwise the batch "
            "reports fault-recovered and the discriminator is not read",
            "decision": f"{under} favor under-rotation; {mis} favor |1> misassignment; otherwise unresolved",
            "t0_stop_rule": f"any qubit of the LCU pairs {lcu} or of the walk set {walk} with readout-1 P1 below "
            f"{READOUT_1_P1_MIN:.2f} or readout-0 P1 above {READOUT_0_P1_MAX:.2f} re-plans the layout before T0",
            "readmission": f"each of q{', q'.join(map(str, PRE_READMISSION))} is readout-admissible when readout-0 P1 "
            f"<= {READOUT_0_P1_MAX:.2f} and readout-1 P1 >= {READOUT_1_P1_MIN:.2f}; a qubit also excluded by the "
            "Ramsey visibility floor stays excluded until a fresh Ramsey run clears it",
            "limit": "the readout pair and the double X run at one calibration; leakage, whose X train plateaus "
            "instead of oscillating, needs X trains of three and more",
            "stop_rule": "each batch: every job completed with the manifest's shots; circuit digests equal "
            "cases.json; the batch measures excluded qubits by design, so its readout limits act through the T0 "
            "stop rule and the re-admission rule",
            "thresholds": {
                "fault_p1_given_1_below": PRE_FAULT_P1_GIVEN_1_BELOW,
                "under_rotation_p1_xx_above": PRE_UNDER_ROTATION_ABOVE,
                "misassignment_p1_xx_below": PRE_MISASSIGNMENT_BELOW,
                "predictions_p1_xx": PRE_PREDICTIONS,
                "readout_0_p1_at_most": READOUT_0_P1_MAX,
                "readout_1_p1_at_least": READOUT_1_P1_MIN,
                "t0_lcu_qubits": lcu,
                "t0_walk_qubits": walk,
                "readmission": basis,
            },
        },
    }
    texts = {PRE_FILE: double_x_text(TUNA_QUBITS), **readout_circuits(TUNA_QUBITS)}
    chunk: list[dict[str, Any]] = [
        {"file": PRE_FILE, "kind": "diagnostic", "stage": "pre", "ideal_p1": "0"},
        {"file": "readout-0.cq", "kind": "readout", "stage": "pre", "prepared": 0},
        {"file": "readout-1.cq", "kind": "readout", "stage": "pre", "prepared": 1},
    ]
    files = write_batches(shared, [chunk], texts, "stage")
    validate_series(files, tuna)
    return files


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
    return {"box_kite_a_qx": smoke_series(), **tuna_series(), **ry_series(), "box_kite_de_qx": de_smoke_series()}


# ---------------------------------------------------------------- families (d1)-(d3) and (e)


def pauli_expectation(row: Row, pauli: str) -> Fraction:
    """<P> on the selector-0 branch (c0 |label_0> + c1 |label_1>) / norm; pauli names data qubit b at position b.

    X and Y flip exactly the bits of D = label_0 ^ label_1, so with any X or Y
    the diagonal terms vanish and <P> = 2 c0 c1 Re(phi) / norm^2 with phi the
    phase of P|label_0>: (-1)^{label_0 bit} for each Z, i (-1)^{bit} for each Y.
    """
    c0, c1, l0, l1 = row["c0"], row["c1"], row["label_0"], row["label_1"]
    norm = c0 * c0 + c1 * c1
    flips = sum(1 << b for b, op in enumerate(pauli) if op in "XY")
    if flips == 0:
        return Fraction(c0 * c0 * (-1) ** bin(l0).count("1") + c1 * c1 * (-1) ** bin(l1).count("1"), norm)
    if flips != l0 ^ l1:
        raise ValueError(f"setting {pauli} does not flip exactly the bits where the labels differ")
    ys = [b for b, op in enumerate(pauli) if op == "Y"]
    if len(ys) % 2:
        return Fraction(0)
    phase = (-1) ** (len(ys) // 2)
    for b, op in enumerate(pauli):
        if op in "ZY":
            phase *= (-1) ** (l0 >> b & 1)
    return Fraction(2 * c0 * c1 * phase, norm)


def de_specs(census: dict[str, Any], rows: dict[str, list[Row]]) -> dict[str, list[dict[str, Any]]]:
    """The replicas of (d1)-(d3) and (e) in run order with their census predictions; no circuit is built.

    d1: per kite the five constant-sign exemplars of associator.deterministic_exemplars,
    P(c = 0) = (1 + omega)/2, and the omit-last-block control of its
    ij-same-vertex-third-strut exemplar (1/2). d2: the 105 pairs of
    associator.fixed_pair_uniform_k and d3 the 16 values of fixed_i_uniform_jk,
    P(c = 0) = (1 + <W>)/2. e: per kite the first bright edge row and the
    first strut row at (+, +), every X/Y assignment on the w bits where the
    labels differ (Z elsewhere) and the all-Z setting.
    """
    associator = census["associator"]
    out: dict[str, list[dict[str, Any]]] = {name: [] for name in DE_SUB_FAMILIES}
    for kite in sorted(associator["deterministic_exemplars"], key=int):
        exemplars = associator["deterministic_exemplars"][kite]
        for name in sorted(exemplars):
            i, j, k, omega = exemplars[name][:4]
            out["d1_fixed_triple"].append(
                {"census": f"associator.deterministic_exemplars[{kite}].{name}", "triple": [i, j, k],
                 "omega": omega, "omit_last_block": False, "p_selector_zero": str(Fraction(1 + omega, 2))}
            )  # fmt: skip
        i, j, k, omega = exemplars["ij-same-vertex-third-strut"][:4]
        out["d1_fixed_triple"].append(
            {"census": f"associator.deterministic_exemplars[{kite}].ij-same-vertex-third-strut", "triple": [i, j, k],
             "omega": omega, "omit_last_block": True, "p_selector_zero": "1/2"}
        )  # fmt: skip
    pairs = sorted(
        (tuple(pair), value) for value, listed in associator["fixed_pair_uniform_k"].items() for pair in listed
    )
    for (i, j), value in pairs:
        out["d2_fixed_pair"].append(
            {"census": f"associator.fixed_pair_uniform_k[{value}]", "pair": [i, j], "witness": value,
             "p_selector_zero": str((1 + Fraction(value)) / 2)}
        )  # fmt: skip
    for i in range(16):
        value = associator["fixed_i_uniform_jk"][str(i)]
        out["d3_fixed_i"].append(
            {"census": f"associator.fixed_i_uniform_jk[{i}]", "i": i, "witness": value,
             "p_selector_zero": str((1 + Fraction(value)) / 2)}
        )  # fmt: skip
    for kite in range(1, 8):
        chosen = [
            next(r for r in rows["within_kite"] if r["kite"] == kite and is_edge(r) and r["p_selector_zero"] == "1"),
            next(r for r in rows["within_kite"] if r["kite"] == kite and r["relation"] == "strut" and signs(r, 1, 1)),
        ]
        for row in chosen:
            differ = [b for b in range(4) if (row["label_0"] ^ row["label_1"]) >> b & 1]
            if 1 << len(differ) != row["full_coherence_settings"]:
                raise ValueError(f"census within_kite[{row['index']}]: {len(differ)} differing bits against "
                                 f"{row['full_coherence_settings']} settings")  # fmt: skip
            settings = []
            for choice in itertools.product("XY", repeat=len(differ)):
                ops = ["Z"] * 4
                for b, op in zip(differ, choice, strict=True):
                    ops[b] = op
                settings.append("".join(ops))
            for pauli in [*settings, "ZZZZ"]:
                out["e_full_coherence"].append(
                    {"census": f"within_kite[{row['index']}]", "kite": kite, "relation": row["relation"],
                     "p": [row["p_low"], row["p_high"], row["x_sign"]],
                     "q": [row["q_low"], row["q_high"], row["y_sign"]],
                     "pauli": pauli, "p_selector_zero": row["p_selector_zero"],
                     "expectation_given_selector_zero": str(pauli_expectation(row, pauli)),
                     "p_parity_even_given_selector_zero": str((1 + pauli_expectation(row, pauli)) / 2)}
                )  # fmt: skip
    counts = census["experiment_counts"]
    want = {
        "d1_fixed_triple": 6 * len(associator["deterministic_exemplars"]),
        "d2_fixed_pair": counts["fixed_pair_witnesses"],
        "d3_fixed_i": counts["fixed_i_witnesses"],
        "e_full_coherence": sum(2 * (n + 1) for n in counts["full_coherence_settings_by_kite"].values()),
    }
    if {name: len(specs) for name, specs in out.items()} != want:
        raise ValueError(f"family (d)/(e) replica counts {[len(v) for v in out.values()]} differ from {want}")
    return out


def left_mult_signs(m: int) -> list[int]:
    """The sign diagonal D_m of designs.left_mult_gate(16, m): L_{e_m}|q> = D_m[q] |m ^ q>."""
    from qiskit.quantum_info import Operator

    from designs import left_mult_gate

    matrix = Operator(left_mult_gate(16, m)).data
    return [round(float(matrix[q ^ m, q].real)) for q in range(16)]


def controlled_block(qc: Any, control: int, data: list[int], m: int, adjoint: bool) -> None:
    """Controlled L_{e_m} (D_m, then X on the bits of m) or its adjoint (X, then D_m) on `data`."""
    from qiskit.circuit.library import DiagonalGate

    diagonal = DiagonalGate([1.0] * 16 + [float(sign) for sign in left_mult_signs(m)])
    moves = [data[b] for b in range(4) if m >> b & 1]
    if adjoint:
        for q in moves:
            qc.cx(control, q)
    qc.append(diagonal, [*data, control])
    if not adjoint:
        for q in moves:
            qc.cx(control, q)


def controlled_w(qc: Any, control: int, data: list[int], i: int, j: int, omit_last: bool = False) -> None:
    """Controlled W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j) with e_i e_j = s e_{i^j}, s from designs' L_{e_i}.

    The sign s is set before control: s = -1 is a Z on the control, the
    relative phase the Hadamard test reads.
    """
    if left_mult_signs(i)[j] < 0:
        qc.z(control)
    controlled_block(qc, control, data, j, adjoint=False)
    controlled_block(qc, control, data, i, adjoint=False)
    if not omit_last:
        controlled_block(qc, control, data, i ^ j, adjoint=True)


def w_diagonal(i: int, j: int) -> list[float]:
    """<k| W_ij |k> for every k, from the designs-built W_ij."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    qc = QuantumCircuit(5)
    controlled_w(qc, 4, [0, 1, 2, 3], i, j)
    matrix = Operator(qc).data
    return [float(matrix[16 + k, 16 + k].real) for k in range(16)]


def de_logical(sub_family: str, spec: dict[str, Any]) -> Any:
    """The logical circuit of one (d)/(e) replica: control or selector on its last qubit."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import DiagonalGate

    if sub_family == "d3_fixed_i":
        qc = QuantumCircuit(D3_WIDTH)
        for q in range(8):
            qc.h(q)
        qc.h(8)
        entries = [1.0] * 256
        for j in range(16):
            entries[16 * j : 16 * j + 16] = w_diagonal(spec["i"], j)
        qc.append(DiagonalGate([1.0] * 256 + entries), range(9))
        qc.h(8)
        return qc
    if sub_family == "e_full_coherence":
        row = {
            "p_low": spec["p"][0], "p_high": spec["p"][1], "x_sign": spec["p"][2],
            "q_low": spec["q"][0], "q_high": spec["q"][1], "y_sign": spec["q"][2],
        }  # fmt: skip
        qc = full_design_b(row)
        for b, op in enumerate(spec["pauli"]):
            if op == "Y":
                qc.sdg(b)
            if op in "XY":
                qc.h(b)
        return qc
    qc = QuantumCircuit(5)
    if sub_family == "d1_fixed_triple":
        i, j, k = spec["triple"]
        for b in range(4):
            if k >> b & 1:
                qc.x(b)
        omit = spec["omit_last_block"]
    else:
        i, j = spec["pair"]
        for b in range(4):
            qc.h(b)
        omit = False
    qc.h(4)
    controlled_w(qc, 4, [0, 1, 2, 3], i, j, omit)
    qc.h(4)
    return qc


def de_width(sub_family: str) -> int:
    return D3_WIDTH if sub_family == "d3_fixed_i" else 5


def de_roles(sub_family: str, place: dict[int, int]) -> dict[str, Any]:
    width = de_width(sub_family)
    roles: dict[str, Any] = {"selector": place[width - 1], "data": [place[q] for q in range(4)]}
    if sub_family == "d3_fixed_i":
        roles["j"] = [place[q] for q in range(4, 8)]
    return roles


def emit_de_circuit(item: tuple[str, str, list[tuple[dict[str, Any], dict[int, int]]]]) -> str:
    """Pool worker: one packed (d)/(e) QX circuit, compiled at optimization level 0 to FULL_BASIS."""
    from qiskit import transpile

    file, sub_family, members = item
    lines = header(QX_QUBITS)
    for slot, (spec, place) in enumerate(members):
        what = {key: spec[key] for key in ("triple", "pair", "i", "pauli") if key in spec}
        lines.append(f"// slot {slot} {sub_family} census {spec['census']} {json.dumps(what, sort_keys=True)} "
                     f"P {spec['p_selector_zero']} selector q[{de_roles(sub_family, place)['selector']}]")  # fmt: skip
        circuit = transpile(de_logical(sub_family, spec), basis_gates=FULL_BASIS, optimization_level=0)
        lines += emit(circuit, place)
    return "\n".join(lines + ["", "b = measure q", ""])


def de_circuits(
    census: dict[str, Any], rows: dict[str, list[Row]], limit: int | None = None
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    specs = de_specs(census, rows)
    circuits: list[dict[str, Any]] = []
    jobs = []
    for sub_family in DE_SUB_FAMILIES:
        chosen = specs[sub_family] if limit is None else specs[sub_family][:limit]
        width = de_width(sub_family)
        for number, group in enumerate(pack(chosen, width), start=1):
            file = f"{sub_family}-{number:03d}.cq"
            jobs.append((file, sub_family, group))
            replicas = [
                {"slot": slot, **spec, "roles": de_roles(sub_family, place)} for slot, (spec, place) in enumerate(group)
            ]
            circuits.append({"file": file, "kind": "witness", "sub_family": sub_family, "replicas": replicas})
    texts = dict(zip((file for file, _, _ in jobs), parallel.ordered_map(emit_de_circuit, jobs), strict=True))
    parallel.ordered_map(verify_text, [(row["file"], texts[row["file"]], checks_of(row)) for row in circuits])
    return circuits, texts


def de_shared(backend: dict[str, Any], census_path: Path, census: dict[str, Any], family: str) -> dict[str, Any]:
    return {
        "schema": CASES_SCHEMA,
        "family": family,
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": QX_SHOTS,
        "dialect": "qx",
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "census": census_record(census_path, census),
        "encodings": {
            "d1_fixed_triple": "data 0-3, control 4: X on the bits of k, H on c, controlled W_ij (designs' L_{e_j}, "
            "L_{e_i}, L_{e_{i^j}}^dagger as controlled diagonals and CNOTs, e_i e_j's sign as Z on c), H on c",
            "d2_fixed_pair": "as d1 with H on every data qubit in place of the basis input",
            "d3_fixed_i": "k on 0-3, j on 4-7, control 8: H on 0-8, the diagonal of W_ij over (j, k) from designs' "
            "operators on c = 1, H on c",
            "e_full_coherence": "full Design B (selector 4), then per data qubit H for X, Sdag and H for Y, nothing "
            "for Z; pauli names data qubit b at position b",
            "compile": f"optimization level 0 to {', '.join(FULL_BASIS)} with Rz on the pi/{ANGLE_GRID} grid",
        },
        "preregistered": {
            "observable": "d1-d3: associator-sign interference witness <Z_c> = 2 P(c = 0) - 1; e: coherence "
            "reconstruction <P> = 2 P(data parity even | selector = 0) - 1 per setting",
            "predictions": "d1 omega of census associator.deterministic_exemplars and 0 for the omit-last control; "
            "d2 associator.fixed_pair_uniform_k; d3 associator.fixed_i_uniform_jk; e <P> from the census "
            "coefficients c0, c1 and labels of each row",
            "falsifier": f"a deterministic replica off its outcome in one shot, or any other replica outside "
            f"|z| < {Z_LIMIT} at {QX_SHOTS} shots, refutes that circuit's implementation",
            "limit": "an associator-sign witness cannot separate the octonions from the split octonions",
        },
    }


def series_de(census_path: Path = CENSUS, limit: int | None = None) -> dict[str, str]:
    """The exhaustive (d1)-(d3) and (e) case files on QX, in memory; limit keeps the first replicas of each."""
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census = load_census(census_path)
    rows = validate_census(census)
    circuits, texts = de_circuits(census, rows, limit)
    files = finish(de_shared(backend, census_path, census, "de"), circuits, texts)
    validate_series(files, backend)
    return files


def de_smoke_series(census_path: Path = CENSUS) -> dict[str, str]:
    """box_kite_de_qx/: the first circuit of each (d)/(e) sub-family, the remote QX smoke representatives."""
    backend = qx_backend(json.loads(CATALOGUE.read_text(encoding="utf-8")))
    census = load_census(census_path)
    rows = validate_census(census)
    width = {name: QX_QUBITS // de_width(name) for name in DE_SUB_FAMILIES}
    circuits, texts = de_circuits(census, rows, limit=max(width.values()))
    first: dict[str, dict[str, Any]] = {}
    for row in circuits:
        first.setdefault(row["sub_family"], {**row, "group": "smoke"})
    smoke = list(first.values())
    files = finish(
        {**de_shared(backend, census_path, census, "de_smoke"), "role": "smoke run of the remote QX compile path; "
         "the exhaustive (d1)-(d3) and (e) sets run on Kaggle CPU through scripts/box_kite_qx_sweep.py"},
        smoke, texts, group="group",
    )  # fmt: skip
    validate_series(files, backend)
    return files


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
            "falsifier": f"a completed job whose counts leave an expected outcome's |z| < {Z_LIMIT} or show an "
            "outcome of probability 0 is reported as an emulator rate; a failed job names its factor",
            "stop_rule": "R1 failing stops the smoke subset, whose circuits declare qubit[9]",
            "thresholds": {"z_limit": Z_LIMIT, "gating_factor": "R1"},
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
            "falsifier": f"a deterministic replica below {RY_DETERMINISTIC_MIN} of its ideal outcome is reported "
            "with the emulator's raw rates as an emulator rate, never as an algebraic result",
            "stop_rule": f"a deterministic replica below {RY_DETERMINISTIC_MIN} of its ideal outcome stops the series",
            "thresholds": {"deterministic_ideal_fraction_at_least": RY_DETERMINISTIC_MIN, "z_limit": Z_LIMIT},
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
    from qiskit import QuantumCircuit

    off_grid = QuantumCircuit(1)
    off_grid.rz(math.pi / 3, 0)
    reject("an off-grid Rz angle in the default emit", lambda: emit(off_grid, {0: 0}))
    if emit(off_grid, {0: 2}, angle_grid=None) != [f"Rz({math.pi / 3:.15f}) q[2]"]:
        raise AssertionError("emit with angle_grid None does not print the angle itself")
    on_grid = QuantumCircuit(1)
    on_grid.rz(3 * math.pi / ANGLE_GRID, 0)
    if emit(on_grid, {0: 0}, angle_grid=None) != emit(on_grid, {0: 0}):
        raise AssertionError("an on-grid angle prints differently with and without snapping")
    with_reset = QuantumCircuit(1)
    with_reset.reset(0)
    for dialect in DIALECTS:
        reject(f"a reset in the {dialect} dialect", lambda d=dialect: emit(with_reset, {0: 0}, dialect=d))

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
    pre = tuna_dirs["box_kite_tuna_pre"]
    validate_series(pre, tuna)
    pre_text = pre[f"batch-00/{PRE_FILE}"]
    merged = pre_text.replace("\n".join(f"barrier q[{q}]" for q in range(TUNA_QUBITS)) + "\n", "", 1)
    reject("a double X without its barrier run", lambda: check_double_x(PRE_FILE, merged))
    reject("a double X read as a witness on the admitted layout", lambda: check_tuna_text(PRE_FILE, pre_text))
    reject("a double X with one X dropped", lambda: check_double_x(PRE_FILE, pre_text.replace("X q[6]\n", "", 1)))
    if pre_claim()["id"] != PRE_CLAIM:
        raise AssertionError("the registry claim lost its id")
    registry = json.loads(RESEARCH_STATE.read_text(encoding="utf-8"))
    for claim in registry["claims"]:
        if claim.get("id") == PRE_CLAIM:
            claim["statement"] = claim["statement"].replace("0.98 and 0.52", "0.90 and 0.52")
    with tempfile.TemporaryDirectory() as scratch:
        altered_registry = Path(scratch) / "research_state.json"
        altered_registry.write_text(json.dumps(registry), encoding="utf-8")
        reject("a registry claim whose predictions moved", lambda: pre_claim(altered_registry))
    follow = tuna_dirs["box_kite_tuna_follow"]
    validate_series(follow, tuna)
    follow_rows = {
        row["file"]: (name, row)
        for name in sorted({key.split("/")[0] for key in follow if "/" in key})
        for row in json.loads(follow[f"{name}/cases.json"])["circuits"]
    }

    def follow_case(file: str) -> tuple[str, dict[str, Any]]:
        batch, row = follow_rows[file]
        return follow[f"{batch}/{file}"], row

    walk_text, walk_row = follow_case("walk-x.cq")
    control_z = f"Z q[{walk_row['replicas'][0]['roles']['control']}]"
    reject(
        "a walk without its omega Z",
        lambda: verify_text(("walk", walk_text.replace(control_z + "\n", "", 1), checks_of(walk_row))),
    )
    from qiskit.quantum_info import Statevector

    for theta in (0.3, -1.1):
        walk = associator_walk(2, 11, 3, -1, [0, 1, 3], readout="Y")
        phased = QuantumCircuit(walk.num_qubits)
        for instruction in walk.data[:-2]:
            phased.append(instruction)
        phased.rz(theta, 0)
        for instruction in walk.data[-2:]:
            phased.append(instruction)
        p_zero = float(Statevector(phased).probabilities([0])[0])
        if abs(p_zero - (1 - math.sin(theta)) / 2) > PROBABILITY_TOLERANCE:
            raise AssertionError(f"readout Y on a control phase {theta} reads P(c = 0) {p_zero}, not (1 + omega sin)/2")
    for file, slot in (("lcu-bright-x-1.cq", 0), ("lcu-dark-x-1.cq", 0)):
        text, row = follow_case(file)
        data = row["replicas"][slot]["roles"]["data"][0]
        lines = text.splitlines()
        last_h = max(n for n, line in enumerate(lines) if line == f"H q[{data}]")
        lines.insert(last_h, f"Z q[{data}]")
        reject(
            f"a coherence sign flipped in {file}",
            lambda lines=lines, row=row: verify_text(("coherence", "\n".join(lines), checks_of(row))),
        )
    index = json.loads(follow["cases.json"])
    last = index["batches"][-1]["batch"]
    manifest = json.loads(follow[f"{last}/cases.json"])
    unbracketed = dict(follow)
    witnesses_only = [manifest["circuits"][0]] * HARDWARE_BATCH_CIRCUITS
    unbracketed[f"{last}/cases.json"] = json.dumps({**manifest, "circuits": witnesses_only}, indent=1) + "\n"
    index["batches"][-1]["files"] = [row["file"] for row in witnesses_only]
    unbracketed["cases.json"] = json.dumps(index, indent=1) + "\n"
    for key in [k for k in unbracketed if k.startswith(f"{last}/readout-")]:
        del unbracketed[key]
    reject("a bracketed series without its closing readout pair", lambda: validate_series(unbracketed, tuna))
    swapped_pair = dict(follow)
    first = json.loads(follow["cases.json"])["batches"][0]["batch"]
    head = json.loads(follow[f"{first}/cases.json"])
    order = [head["circuits"][1], head["circuits"][0], head["circuits"][2]]
    swapped_pair[f"{first}/cases.json"] = json.dumps({**head, "circuits": order}, indent=1) + "\n"
    index = json.loads(follow["cases.json"])
    index["batches"][0]["files"] = [row["file"] for row in order]
    swapped_pair["cases.json"] = json.dumps(index, indent=1) + "\n"
    reject("a bracketed batch with readout-1 before readout-0", lambda: validate_series(swapped_pair, tuna))
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

    # Families (d1)-(d3) and (e): every smoke representative against its census value, and two mutations.
    de = de_smoke_series()
    for batch in json.loads(de["cases.json"])["batches"]:
        for row in json.loads(de[f"{batch['batch']}/cases.json"])["circuits"]:
            text = de[f"{batch['batch']}/{row['file']}"]
            verify_text((row["file"], text, checks_of(row)))
            if row["sub_family"] == "d1_fixed_triple":
                flipped_row = copy.deepcopy(row)
                replica = next(r for r in flipped_row["replicas"] if r["p_selector_zero"] in ("0", "1"))
                replica["p_selector_zero"] = "1" if replica["p_selector_zero"] == "0" else "0"
                reject(
                    "a d1 witness with omega negated",
                    lambda t=text, r=flipped_row: verify_text(("d1", t, checks_of(r))),
                )
            if row["sub_family"] == "e_full_coherence":
                swapped_row = copy.deepcopy(row)
                replica = next(
                    r for r in swapped_row["replicas"] if r["p_parity_even_given_selector_zero"] in ("0", "1")
                )
                replica["p_parity_even_given_selector_zero"] = (
                    "1" if replica["p_parity_even_given_selector_zero"] == "0" else "0"
                )
                reject(
                    "an (e) setting with its sign flipped",
                    lambda t=text, r=swapped_row: verify_text(("e", t, checks_of(r))),
                )
    bright = next(r for r in within if is_edge(r) and r["p_selector_zero"] == "1")
    reject("a coherence setting that misses a differing bit", lambda: pauli_expectation(bright, "ZZZX"))

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
        "box-kite cases: census, SELECT, state-vector, packing, batch, Tuna layout, twin, Ry, (d)/(e) and "
        f"catalogue contracts pass; {rejected} mutations rejected"
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
