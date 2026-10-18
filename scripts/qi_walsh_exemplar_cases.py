"""Tuna-17 cases for the two dimension-32 cubic Walsh classes, with q13 readout-context circuits.

The associator phase omega_{i,j}(x) of the pairs (1,16) and (9,18)
(predict.associator_phase, dimension 32) falls in the two cubic spectral
classes of scripts/associator_walsh_classes.py, EXPECTED_CUBIC_CLASSES: |W|
multiset {0: 24, 8: 7, 24: 1} with collision probability K = 11/32 ("high")
and {0: 22, 8: 8, 16: 2} with K = 5/32 ("low"). Under |+>^n input a linear
change of variables is free: a phase h with omega(x) = (-1)^h(Ax + b + ...)
up to affine terms samples P_omega(y) = P_h(z) at y = M z + u for an
injective affine map, so each class runs as a four-qubit phase circuit whose
outcome distribution pushes forward to the census spectrum.

path_search() enumerates every circuit of CNOT and CZ gates on a four-qubit
path, with diagonal phases k pi/4 on the parities the CNOT network visits
and a free final linear map, breadth first by two-qubit gate count. The
cheapest circuit reaching each class (5 CZ high, 6 CZ low, CNOT as H CZ H)
is the emitted one; the search proves no circuit of that gate set reaches the
class with fewer. A phase polynomial sum_p c_p (pi/4) [p.x] is a Boolean
phase pi h(x) exactly when, in the monomial expansion of [p.x], the sums
over p containing a set T of c_p vanish mod 4 for |T| = 1, are even for
|T| = 2 (their halves add the quadratic part of h) and are the cubic part of
h mod 2 for |T| = 3; c_p mod 4 is all that matters, since 4 [p.x] only adds
a linear term.

Each Walsh circuit runs both classes at once on the disjoint paths
BLOCKS["X"] = q1-q4-q8-q12 and BLOCKS["Y"] = q10-q13-q11-q14, which avoid the
excluded and avoided qubits of box_kite_cases and meet at the parked couplers
8-11 and 12-14. walsh-c1 puts high on X and low on Y and walsh-c2 swaps them,
so class and block separate inside one calibration. Both Y placements hold
q13, whose |1> misassignment depends on its neighbors' state
(results/quantum_inspire/box_kite_tuna_17_ladder_analysis.json); the
context readouts prepare q13 alone, beside X X on q10 and q11 (driven, left
in |0>), and beside one excited neighbor at a time, so the analysis corrects
q13 conditioned on the measured q10 and q11 bits of each shot.

SERIES_PLAN fixes four batches of three circuits under the hardware limits of
qi_platform.py, with readout-0 and readout-1 in the first and the last. Every
emitted text is checked against the exact state vector of its own gate list,
every block against the census spectrum through its recorded map, and the
relabeled QX twins against the same distributions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from associator_walsh_classes import EXPECTED_CUBIC_CLASSES  # noqa: E402
from box_kite_cases import (  # noqa: E402
    CATALOGUE,
    QX_SHOTS,
    TUNA_AVOIDED,
    TUNA_EXCLUDED,
    TUNA_QUBITS,
    Z_LIMIT,
    qx_backend,
    tuna_backend,
)
from qi_platform import HARDWARE_BATCH_CIRCUITS, declared_qubits  # noqa: E402
from qi_zero_divisor_cases import TUNA17, header, readout_circuits  # noqa: E402

import parallel  # noqa: E402
import qi_stack  # noqa: E402
from predict import associator_phase  # noqa: E402

SCHEMA = "qi-walsh-exemplar-cases-v1"
SERIES_SCHEMA = "qi-walsh-exemplar-series-v1"
FAMILY = "walsh_exemplar_tuna_17"
TWIN_FAMILY = "walsh_exemplar_twins_qx"
DIM = 32
NBITS = 5
EXEMPLARS = {"high": (1, 16), "low": (9, 18)}
WIDTH = 4
PATH_EDGES = ((0, 1), (1, 2), (2, 3))
MAX_DEPTH = 7
BLOCKS = {"X": (1, 4, 8, 12), "Y": (10, 13, 11, 14)}
CIRCUITS = {"walsh-c1": {"X": "high", "Y": "low"}, "walsh-c2": {"X": "low", "Y": "high"}}
SHOTS = 131072
CONTEXT_QUBIT = 13
CONTEXT_NEIGHBORS = (10, 11)
# Each context readout: the X pulses per qubit, in order, with a per-qubit
# barrier run between the two pulses of a driven neighbor.
CONTEXTS = {
    "readout-q13": {13: 1},
    "readout-q13-xx": {13: 1, 10: 2, 11: 2},
    "readout-q13-q10": {13: 1, 10: 1},
    "readout-q13-q11": {13: 1, 11: 1},
}
SERIES_PLAN = (
    ("readout-0", "readout-1", "readout-q13"),
    ("walsh-c1", "walsh-c2", "readout-q13-xx"),
    ("walsh-c1", "walsh-c2", "readout-q13-q10"),
    ("readout-0", "readout-1", "readout-q13-q11"),
)
PHASE_GATES = {0: [], 1: ["T"], 2: ["S"], 3: ["Tdag"]}
# The retention per CZ that T0 measured (docs/notes/quantum_inspire/tuna-17.md),
# which the informational prediction raises to each class's CZ count.
R_PER_CZ = 0.965
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20261018
Z_DECISION = 3.0
DELTA_MIN = 0.02
SHAPE_LOG10_P = -3.0
SCATTER_ALLOWANCE = 0.03
BRACKET_DRIFT_MAX = 0.02

TOLERANCE = 1e-12
PAIRS = tuple(itertools.combinations(range(WIDTH), 2))
TRIPLES = tuple(itertools.combinations(range(WIDTH), 3))
CASES = ROOT / "results/quantum_inspire/cases"
CONFORMANCE = ROOT / "results/quantum_inspire/walsh_exemplar_qx_conformance.json"
CONFORMANCE_SCHEMA = "qi-walsh-exemplar-qx-conformance-v1"
CONFORMANCE_SHOTS = 8192
CONFORMANCE_SEED = 20261018
QX_WORKER = ROOT / "scripts/box_kite_qx_sweep.py"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


# ---------------------------------------------------------------- spectra


def walsh(bits: list[int]) -> list[int]:
    """Integer Walsh transform W(y) = sum_x (-1)^(h(x) + x.y) of a 0/1 truth table."""
    w = [1 - 2 * b for b in bits]
    step = 1
    while step < len(w):
        for start in range(0, len(w), 2 * step):
            for k in range(start, start + step):
                w[k], w[k + step] = w[k] + w[k + step], w[k] - w[k + step]
        step *= 2
    return w


def signature(w: list[int]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(Counter(abs(v) for v in w).items()))


def exemplar(name: str) -> dict[str, Any]:
    """omega's truth table, census spectrum and class of one exemplar pair, checked against the census table."""
    i, j = EXEMPLARS[name]
    bits = [(1 - s) // 2 for s in associator_phase(DIM, i, j)]
    w = walsh(bits)
    key = signature(w)
    require(key in EXPECTED_CUBIC_CLASSES, f"({i},{j}): |W| multiset {key} is no census cubic class")
    k = sum(Fraction(v * v, DIM * DIM) ** 2 for v in w)
    census: dict[Any, tuple[int, str]] = EXPECTED_CUBIC_CLASSES
    require(str(k) == census[key][1], f"({i},{j}): K = {k} against the census")
    wanted = "11/32" if name == "high" else "5/32"
    require(str(k) == wanted, f"({i},{j}) sits in the K = {k} class, not {wanted}")
    return {"pair": [i, j], "bits": bits, "p": [Fraction(v * v, DIM * DIM) for v in w], "k": k, "signature": key}


# ---------------------------------------------------------------- path search


def class_table() -> dict[tuple[int, int], tuple[tuple[int, int], ...]]:
    """|W| multiset of every four-variable h = cubic part + quadratic part, keyed by their monomial masks."""
    table = {}
    for cubic in range(1 << len(TRIPLES)):
        for quadratic in range(1 << len(PAIRS)):
            bits = []
            for x in range(1 << WIDTH):
                value = sum(bool(cubic >> n & 1 and contains(x, tri)) for n, tri in enumerate(TRIPLES))
                value += sum(bool(quadratic >> n & 1 and contains(x, pair)) for n, pair in enumerate(PAIRS))
                bits.append(value & 1)
            table[(cubic, quadratic)] = signature(walsh(bits))
    return table


def target_signature(name: str) -> tuple[tuple[int, int], ...]:
    """The four-variable spectrum of a class: x0 x1 x2 for high, x0 x1 x2 + x1 x3 for low."""
    cubic = 1 << TRIPLES.index((0, 1, 2))
    quadratic = 0 if name == "high" else 1 << PAIRS.index((1, 3))
    return class_table()[(cubic, quadratic)]


def contains(p: int, members: tuple[int, ...]) -> bool:
    return all(p >> t & 1 for t in members)


def solve(
    support: frozenset[int], extra: int, wanted: tuple[tuple[int, int], ...], table: dict
) -> dict[int, int] | None:
    """Phase coefficients c_p mod 4 on the visited parities whose phase polynomial is a Boolean h of the class.

    c_p = eps_p + 2 delta_p. eps fixes the cubic part and must leave every
    single- and pair-monomial sum even; delta then solves the single-monomial
    conditions and adds to the quadratic part, so the reachable quadratic
    parts of one eps form a coset that the span enumeration lists.
    """
    parities = sorted(support)
    rows = []
    for p in parities:
        single = sum(1 << i for i in range(WIDTH) if p >> i & 1)
        pair = sum(1 << n for n, ab in enumerate(PAIRS) if contains(p, ab))
        rows.append((single, pair))
    for eps in range(1 << len(parities)):
        chosen = [p for n, p in enumerate(parities) if eps >> n & 1]
        singles = [sum(p >> i & 1 for p in chosen) for i in range(WIDTH)]
        pairs = [sum(contains(p, ab) for p in chosen) for ab in PAIRS]
        if any(s % 2 for s in singles) or any(s % 2 for s in pairs):
            continue
        cubic = sum(1 << n for n, tri in enumerate(TRIPLES) if sum(contains(p, tri) for p in chosen) % 2)
        base = sum(1 << n for n, s in enumerate(pairs) if s // 2 % 2) ^ extra
        need = sum(1 << i for i, s in enumerate(singles) if s // 2 % 2)
        span = {(0, 0): 0}
        for n, (single, pair) in enumerate(rows):
            for (s0, q0), delta in list(span.items()):
                span.setdefault((s0 ^ single, q0 ^ pair), delta | 1 << n)
        for (s0, q0), delta in sorted(span.items(), key=lambda item: item[1]):
            if s0 == need and table[(cubic, base ^ q0)] == wanted:
                return {p: (eps >> n & 1) + 2 * (delta >> n & 1) for n, p in enumerate(parities)}
    return None


def path_search(with_cz: bool, max_depth: int = MAX_DEPTH) -> dict[str, dict[str, Any]]:
    """Fewest-two-qubit-gate circuit of each class on the path, breadth first in a fixed move order.

    A state is the parity each position holds, the set of parities visited
    and the quadratic form CZ moves have added; the first state of a layer
    that reaches a class names that class's circuit.
    """
    table = class_table()
    wanted = {name: target_signature(name) for name in EXEMPLARS}
    start = (tuple(1 << i for i in range(WIDTH)), frozenset(1 << i for i in range(WIDTH)), 0)
    layer: dict[Any, tuple[tuple[str, int, int], ...]] = {start: ()}
    seen = set(layer)
    found: dict[str, dict[str, Any]] = {}
    for depth in range(max_depth + 1):
        cache: dict[tuple[frozenset[int], int], dict[str, dict[int, int] | None]] = {}
        for state, moves in layer.items():
            rows, support, extra = state
            key = (support, extra)
            if key not in cache:
                cache[key] = {name: solve(support, extra, wanted[name], table) for name in wanted if name not in found}
            for name, coefficients in cache[key].items():
                if name not in found and coefficients is not None:
                    found[name] = {"cz_count": depth, "moves": list(moves), "coefficients": coefficients}
        if len(found) == len(EXEMPLARS):
            return found
        following: dict[Any, tuple[tuple[str, int, int], ...]] = {}
        for (rows, support, extra), moves in layer.items():
            for a, b in PATH_EDGES:
                for control, target in ((a, b), (b, a)):
                    new = list(rows)
                    new[target] ^= new[control]
                    state = (tuple(new), support | {new[target]}, extra)
                    if state not in seen:
                        seen.add(state)
                        following[state] = (*moves, ("cx", control, target))
                if with_cz:
                    p, q = rows[a], rows[b]
                    form = sum(
                        1 << n
                        for n, (i, j) in enumerate(PAIRS)
                        if (p >> i & 1 and q >> j & 1) ^ (p >> j & 1 and q >> i & 1)
                    )
                    state = (rows, support, extra ^ form)
                    if state not in seen:
                        seen.add(state)
                        following[state] = (*moves, ("cz", a, b))
        layer = following
    raise ValueError(f"no circuit of at most {max_depth} two-qubit gates reaches {sorted(set(EXEMPLARS) - set(found))}")


def block_ops(solution: dict[str, Any]) -> list[tuple[str, tuple[int, ...]]]:
    """The gate list on path positions: H on all, each phase at its parity's first visit, CNOT as H CZ H, H on all.

    Two H on one position with no gate between them cancel, so a position a
    CNOT targets first starts in |0>.
    """
    rows = [1 << i for i in range(WIDTH)]
    pending = {p: c for p, c in solution["coefficients"].items() if c % 4}
    ops: list[tuple[str, tuple[int, ...]]] = [("H", (q,)) for q in range(WIDTH)]

    def phases() -> None:
        for q, p in enumerate(rows):
            if p in pending:
                ops.extend((gate, (q,)) for gate in PHASE_GATES[pending.pop(p) % 4])

    phases()
    for kind, a, b in solution["moves"]:
        if kind == "cx":
            ops += [("H", (b,)), ("CZ", (a, b)), ("H", (b,))]
            rows[b] ^= rows[a]
        else:
            ops.append(("CZ", (a, b)))
        phases()
    require(not pending, f"parities {sorted(pending)} never visited")
    ops += [("H", (q,)) for q in range(WIDTH)]
    out: list[tuple[str, tuple[int, ...]]] = []
    for op in ops:
        name, qubits = op
        last = next((n for n in range(len(out) - 1, -1, -1) if set(out[n][1]) & set(qubits)), None)
        if name == "H" and last is not None and out[last] == op:
            del out[last]
        else:
            out.append(op)
    return out


# ---------------------------------------------------------------- state vectors and maps

ONE_QUBIT = {
    "H": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Z": np.diag([1, -1]).astype(complex),
    "S": np.diag([1, 1j]),
    "Sdag": np.diag([1, -1j]),
    "T": np.diag([1, np.exp(1j * np.pi / 4)]),
    "Tdag": np.diag([1, np.exp(-1j * np.pi / 4)]),
}


def gate_lines(text: str) -> list[tuple[str, tuple[int, ...]]]:
    """Gates of an emitted text in order; barriers, comments, declarations and the final measure carry none."""
    out = []
    for line in text.splitlines()[5:]:
        if not line or line.startswith(("//", "barrier", "b = measure")):
            continue
        name, _, args = line.partition(" ")
        qubits = tuple(int(a.strip()[2:-1]) for a in args.split(","))
        require(name in ONE_QUBIT or (name == "CZ" and len(qubits) == 2), f"{line!r} is outside the case gate set")
        out.append((name, qubits))
    return out


def probabilities(ops: list[tuple[str, tuple[int, ...]]], qubits: tuple[int, ...]) -> np.ndarray:
    """Outcome probabilities over `qubits` (bit k of the index is qubits[k]) after the gate list from |0...0>."""
    index = {q: n for n, q in enumerate(qubits)}
    state = np.zeros((2,) * len(qubits), dtype=complex)
    state[(0,) * len(qubits)] = 1
    for name, on in ops:
        if not set(on) & set(qubits):
            continue
        require(set(on) <= set(qubits), f"{name} on q{list(on)} leaves the simulated qubits {list(qubits)}")
        axes = [len(qubits) - 1 - index[q] for q in on]
        if name == "CZ":
            sign = np.ones((2,) * len(qubits))
            sel = [slice(None)] * len(qubits)
            for axis in axes:
                sel[axis] = 1  # type: ignore[call-overload]
            sign[tuple(sel)] = -1
            state = state * sign
        else:
            state = np.moveaxis(np.tensordot(ONE_QUBIT[name], state, axes=([1], [axes[0]])), 0, axes[0])
    return np.abs(state.reshape(-1)) ** 2


def census_map(phys: np.ndarray, census: list[Fraction]) -> dict[str, Any]:
    """The first injective affine y = M z + u, by u then the columns of M in ascending order, with P(y) = P(z)."""
    target = np.array([float(p) for p in census])
    width = int(np.log2(len(phys)))

    def extend(u: int, columns: list[int]) -> list[int] | None:
        k = len(columns)
        for z in range(1 << k):
            y = u
            for n, col in enumerate(columns):
                if z >> n & 1:
                    y ^= col
            if abs(target[y] - phys[z]) > TOLERANCE:
                return None
        if k == width:
            return columns
        for col in range(1, DIM):
            images = {u ^ sum_cols(columns + [col], z) for z in range(1 << (k + 1))}
            if len(images) == 1 << (k + 1):
                result = extend(u, columns + [col])
                if result is not None:
                    return result
        return None

    for u in range(DIM):
        columns = extend(u, [])
        if columns is not None:
            images = [u ^ sum_cols(columns, z) for z in range(1 << width)]
            require(abs(sum(target[y] for y in images) - 1) < TOLERANCE, "the census mass leaves the mapped image")
            return {"offset": u, "columns": columns, "images": images}
    raise ValueError("no injective affine map carries the block distribution onto the census spectrum")


def sum_cols(columns: list[int], z: int) -> int:
    value = 0
    for n, col in enumerate(columns):
        if z >> n & 1:
            value ^= col
    return value


# ---------------------------------------------------------------- texts


def check_layout() -> None:
    couplers = {tuple(sorted(edge)) for edge in TUNA17}
    used = [q for block in BLOCKS.values() for q in block]
    require(len(set(used)) == len(used), "the blocks overlap")
    require(not set(used) & set(TUNA_EXCLUDED + TUNA_AVOIDED), "a block touches an excluded or avoided qubit")
    for name, block in BLOCKS.items():
        for a, b in PATH_EDGES:
            require(tuple(sorted((block[a], block[b]))) in couplers, f"block {name}: q{block[a]}-q{block[b]} uncoupled")
    require(CONTEXT_QUBIT in BLOCKS["Y"], "the context qubit sits outside block Y")
    for q in CONTEXT_NEIGHBORS:
        require(tuple(sorted((q, CONTEXT_QUBIT))) in couplers, f"q{q} is no neighbor of q{CONTEXT_QUBIT}")
    neighbors = {a ^ b ^ CONTEXT_QUBIT for a, b in couplers if CONTEXT_QUBIT in (a, b)}
    usable = neighbors - set(TUNA_EXCLUDED + TUNA_AVOIDED)
    require(usable == set(CONTEXT_NEIGHBORS), f"q{CONTEXT_QUBIT}'s usable neighbors are {sorted(usable)}")


def walsh_text(assignment: dict[str, str], ops: dict[str, list[tuple[str, tuple[int, ...]]]]) -> str:
    lines = header(TUNA_QUBITS)
    for block, name in assignment.items():
        qubits = BLOCKS[block]
        i, j = EXEMPLARS[name]
        lines.append(f"// block {block}: {name} class, pair ({i},{j}), position k on q{list(qubits)}[k]")
        for gate, on in ops[name]:
            lines.append(f"{gate} " + ", ".join(f"q[{qubits[k]}]" for k in on))
    return "\n".join(lines + ["", "barrier q", "b = measure q", ""])


def context_text(pulses: dict[int, int]) -> str:
    first = sorted(pulses)
    second = sorted(q for q, n in pulses.items() if n == 2)
    body = [f"// X on q{[q for q in first if q not in second]}; X X on q{second}"]
    body += [f"X q[{q}]" for q in first]
    if second:
        body += [f"barrier q[{q}]" for q in second] + [f"X q[{q}]" for q in second]
    return "\n".join(header(TUNA_QUBITS) + body + ["", "barrier q", "b = measure q", ""])


def check_tuna(file: str, text: str, witness: bool) -> None:
    require(declared_qubits(text) == TUNA_QUBITS, f"{file}: Tuna circuits declare qubit[{TUNA_QUBITS}]")
    couplers = {tuple(sorted(edge)) for edge in TUNA17}
    for name, on in gate_lines(text):
        if name == "CZ":
            require(tuple(sorted(on)) in couplers, f"{file}: CZ on q{list(on)}, which no Tuna-17 coupler joins")
        if witness:
            require(not set(on) & set(TUNA_EXCLUDED + TUNA_AVOIDED), f"{file}: {name} touches an excluded qubit")


def twin_text(text: str) -> tuple[str, dict[int, int]]:
    """The gate list on QX qubits 0..n-1, the block qubits in ascending order, an idle position included."""
    used = sorted(q for block in BLOCKS.values() for q in block)
    mapping = {q: n for n, q in enumerate(used)}
    lines = header(10)
    for line in text.splitlines()[5:]:
        if line.startswith("//"):
            lines.append(line)
            continue
        if not line or line.startswith(("barrier", "b = measure")):
            continue
        name, _, args = line.partition(" ")
        lines.append(f"{name} " + ", ".join(f"q[{mapping[int(a.strip()[2:-1])]}]" for a in args.split(",")))
    return "\n".join(lines + ["", "barrier q", "b = measure q", ""]), mapping


# ---------------------------------------------------------------- series


def design() -> dict[str, Any]:
    """Exemplars, the searched circuits with their minimality certificate, and each block's census map."""
    check_layout()
    exemplars = {name: exemplar(name) for name in EXEMPLARS}
    plain, with_cz = parallel.ordered_map(path_search, [False, True], min_items=2)
    classes = {}
    ops = {}
    for name, info in exemplars.items():
        solution = plain[name]
        require(with_cz[name]["cz_count"] == solution["cz_count"], f"{name}: CZ moves reach the class with fewer gates")
        ops[name] = block_ops(solution)
        phys = probabilities(ops[name], tuple(range(WIDTH)))
        mapping = census_map(phys, info["p"])
        k = float(np.sum(phys**2))
        require(abs(k - float(info["k"])) < TOLERANCE, f"{name}: the block's K {k} differs from the census {info['k']}")
        classes[name] = {
            "pair": info["pair"],
            "census_signature": [list(item) for item in info["signature"]],
            "k": str(info["k"]),
            "cz_count": solution["cz_count"],
            "moves": [list(move) for move in solution["moves"]],
            "phase_coefficients": {str(p): c for p, c in sorted(solution["coefficients"].items()) if c % 4},
            "ideal_p": [str(Fraction(round(p * 256), 256)) for p in phys],
            "support": [z for z in range(1 << WIDTH) if phys[z] > TOLERANCE],
            "census_map": mapping,
        }
    return {"classes": classes, "ops": ops}


def preregistered(classes: dict[str, Any]) -> dict[str, Any]:
    """Decision rules and thresholds scripts/qi_walsh_exemplar_analysis.py reads from the manifest."""
    uniform = 1 / (1 << WIDTH)
    prediction = {}
    for name, info in classes.items():
        visibility = R_PER_CZ ** (2 * info["cz_count"])
        prediction[name] = round(visibility * (float(Fraction(info["k"])) - uniform) + uniform, 4)
    return {
        "readout": "per-qubit e01 from readout-0 and e10 from readout-1, the mean of the batch-00 and batch-03 "
        f"brackets; a bracket difference above {BRACKET_DRIFT_MAX} on a block qubit is reported",
        "q13": {
            "variants": ["bracket", "isolated", "context"],
            "primary": "context",
            "context": "q13's e10 by the true state of (q10, q11): (0,0) readout-q13, (1,0) readout-q13-q10, "
            "(0,1) readout-q13-q11, (1,1) readout-1; q13's e01 from readout-0; the block response is the "
            "16 x 16 product of the other qubits' channels with that conditional channel",
            "attribution": "delta_drive = e10(readout-q13-xx) - e10(readout-q13) and delta_q10, delta_q11 = "
            "e10(readout-q13-qN) - e10(readout-q13); a delta is established at |delta| >= delta_min and "
            "|z| >= z_decision; drive alone, state alone, both or neither",
        },
        "class_order": "K_high > K_low on each block at z >= z_decision in every job; a reversal refutes the "
        "emitted circuits",
        "interaction": "I = ln V(high, X) - ln V(high, Y) - ln V(low, X) + ln V(low, Y), V = (K - 1/16) / "
        "(K_ideal - 1/16), each job's block pooled over its replicates; |I| >= z_decision SE establishes a "
        "class-by-block interaction, which a per-block multiplicative fidelity excludes",
        "shape": "per job and block, lambda fitted by maximum likelihood to raw counts N R (lambda P + "
        "(1 - lambda) / 16); a G statistic with 14 degrees of freedom at log10 p <= shape_log10_p rejects the "
        "depolarizing shape, the signature of a coherent error",
        "replicates": "TVD between the batch-01 and batch-02 copies of each block; above scatter_allowance plus "
        "z_decision SE is reported as batch scatter",
        "forbidden": "corrected weight outside the ideal support, per job and block",
        "prediction": {
            "k": prediction,
            "basis": f"global depolarizing with retention {R_PER_CZ} per CZ; informational, no decision rests on "
            "it; rho above 1 in the ladder already excludes global depolarizing as the whole channel",
        },
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED},
        "z_decision": Z_DECISION,
        "delta_min": DELTA_MIN,
        "shape_log10_p": SHAPE_LOG10_P,
        "scatter_allowance": SCATTER_ALLOWANCE,
        "bracket_drift_max": BRACKET_DRIFT_MAX,
    }


def series() -> dict[str, dict[str, str]]:
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    tuna = tuna_backend(catalogue)
    qx = qx_backend(catalogue)
    built = design()
    texts: dict[str, str] = dict(readout_circuits(TUNA_QUBITS))
    texts |= {f"{name}.cq": context_text(pulses) for name, pulses in CONTEXTS.items()}
    texts |= {f"{name}.cq": walsh_text(assignment, built["ops"]) for name, assignment in CIRCUITS.items()}
    checks = []
    for name, assignment in CIRCUITS.items():
        gates = gate_lines(texts[f"{name}.cq"])
        for block, cls in assignment.items():
            checks.append((f"{name}.cq", block, cls, probabilities(gates, BLOCKS[block])))

    def row(name: str) -> dict[str, Any]:
        file = f"{name}.cq"
        if name in CIRCUITS:
            return {"file": file, "kind": "witness", "blocks": {b: c for b, c in CIRCUITS[name].items()}}
        if name in CONTEXTS:
            return {"file": file, "kind": "readout", "prepared": name.removeprefix("readout-"),
                    "pulses": {str(q): n for q, n in sorted(CONTEXTS[name].items())}}  # fmt: skip
        return {"file": file, "kind": "readout", "prepared": int(name[-1])}

    shared = {
        "schema": SCHEMA,
        "family": FAMILY,
        "backend": tuna["identifier"],
        "backend_type_id": tuna["id"],
        "nqubits": tuna["nqubits"],
        "shots": SHOTS,
        "dialect": "tuna",
        "bit_order": "qubit 0 at the rightmost character (Tuna)",
        "blocks": {name: list(qubits) for name, qubits in BLOCKS.items()},
        "block_bits": "z bit k is the outcome of the block's position k, position k on blocks[block][k]",
        "classes": built["classes"],
        "context": {"qubit": CONTEXT_QUBIT, "neighbors": list(CONTEXT_NEIGHBORS)},
        "readout_calibration": "bracketed",
        "preregistered": preregistered(built["classes"]),
    }
    files = write(shared, [[row(name) for name in batch] for batch in SERIES_PLAN], texts, tuna)
    twin_texts = {}
    twin_rows = []
    for name in CIRCUITS:
        text, mapping = twin_text(texts[f"{name}.cq"])
        twin_texts[f"twin-{name}.cq"] = text
        twin_rows.append({**row(name), "file": f"twin-{name}.cq", "qubit_map": {str(q): n for q, n in mapping.items()}})
        gates = gate_lines(text)
        for block, cls in CIRCUITS[name].items():
            positions = tuple(mapping[q] for q in BLOCKS[block])
            checks.append((f"twin-{name}.cq", block, cls, probabilities(gates, positions)))
    twin_shared = {
        **{k: v for k, v in shared.items() if k not in ("readout_calibration", "preregistered")},
        "family": TWIN_FAMILY,
        "backend": qx["identifier"],
        "backend_type_id": qx["id"],
        "nqubits": qx["nqubits"],
        "shots": QX_SHOTS,
        "dialect": "qx",
        "bit_order": "qubit 0 at the rightmost character (QX)",
        "twin_of": tuna["identifier"],
    }
    twins = write(twin_shared, [twin_rows], twin_texts, qx)
    for file, block, cls, phys in checks:
        ideal = np.array([float(Fraction(p)) for p in built["classes"][cls]["ideal_p"]])
        require(np.max(np.abs(phys - ideal)) < TOLERANCE, f"{file}: block {block} differs from the {cls} class")
    return {FAMILY: files, TWIN_FAMILY: twins}


def write(
    shared: dict[str, Any], chunks: list[list[dict[str, Any]]], texts: dict[str, str], backend: dict[str, Any]
) -> dict[str, str]:
    """batch-NN/ directories of the given chunks and the series index, each batch within the hardware limits."""
    files: dict[str, str] = {}
    batches = []
    for index, chunk in enumerate(chunks):
        name = f"batch-{index:02d}"
        require(len(chunk) <= min(HARDWARE_BATCH_CIRCUITS, backend["max_jobs_per_batch_job"]), f"{name} is too large")
        rows = []
        for item in chunk:
            text = texts[item["file"]]
            require(declared_qubits(text) == shared["nqubits"], f"{name}/{item['file']}: declared width")
            if shared["dialect"] == "tuna":
                check_tuna(f"{name}/{item['file']}", text, item["kind"] == "witness")
            rows.append({**item, "sha256": hashlib.sha256(text.encode()).hexdigest()})
            files[f"{name}/{item['file']}"] = text
        files[f"{name}/cases.json"] = json.dumps({**shared, "batch": name, "circuits": rows}, indent=1) + "\n"
        batches.append({"batch": name, "files": [item["file"] for item in chunk]})
    if shared["dialect"] == "tuna":
        pair = ["readout-0.cq", "readout-1.cq"]
        require(batches[0]["files"][:2] == pair and batches[-1]["files"][:2] == pair, "brackets open and close")
    series_index = {
        "schema": SERIES_SCHEMA,
        "family": shared["family"],
        "backend": shared["backend"],
        "batches": batches,
    }
    files["cases.json"] = json.dumps(series_index, indent=1) + "\n"
    return files


# ---------------------------------------------------------------- qxelarator conformance


def conformance_jobs(directories: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    """Every Walsh text of the series and its twins, with the qubits of each block and a fixed seed."""
    jobs: list[dict[str, Any]] = []
    for directory, files in directories.items():
        for path, text in sorted(files.items()):
            name = path.rsplit("/", 1)[-1]
            if not name.endswith(".cq") or name.removeprefix("twin-").removesuffix(".cq") not in CIRCUITS:
                continue
            circuit = name.removeprefix("twin-").removesuffix(".cq")
            mapping = dict(enumerate(range(TUNA_QUBITS)))
            if name.startswith("twin-"):
                mapping = {q: n for n, q in enumerate(sorted(q for b in BLOCKS.values() for q in b))}
            blocks = {b: [mapping[q] for q in BLOCKS[b]] for b in BLOCKS}
            jobs.append(
                {
                    "file": f"{directory}/{path}",
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "seed": CONFORMANCE_SEED + len(jobs),
                    "classes": CIRCUITS[circuit],
                    "blocks": blocks,
                    "text": text,
                }
            )
    return jobs


def reduce_counts(histogram: dict[str, int], blocks: dict[str, list[int]]) -> dict[str, Any]:
    """Each block's z histogram (bit k from blocks[b][k], qubit 0 at the rightmost character) and the stray shots."""
    out: dict[str, Any] = {b: {} for b in blocks}
    used = {q for qubits in blocks.values() for q in qubits}
    stray = 0
    for key, count in sorted(histogram.items()):
        bits = {q: int(key[len(key) - 1 - q]) for q in range(len(key))}
        stray += count * any(bits[q] for q in bits if q not in used)
        for b, qubits in blocks.items():
            z = str(sum(bits[q] << k for k, q in enumerate(qubits)))
            out[b][z] = out[b].get(z, 0) + count
    return {"blocks": {b: dict(sorted(h.items(), key=lambda kv: int(kv[0]))) for b, h in out.items()}, "stray": stray}


def judge(counts: dict[str, Any], classes: dict[str, str], ideal: dict[str, Any]) -> dict[str, Any]:
    """Forbidden shots and the largest |z| of any outcome against the class's exact probability."""
    verdicts = {}
    for block, name in classes.items():
        p = [float(Fraction(v)) for v in ideal[name]["ideal_p"]]
        h = counts["blocks"][block]
        n = sum(h.values())
        forbidden = sum(c for z, c in h.items() if p[int(z)] == 0)
        zs = [abs(h.get(str(z), 0) - n * q) / (n * q * (1 - q)) ** 0.5 for z, q in enumerate(p) if 0 < q < 1]
        verdicts[block] = {"forbidden": forbidden, "max_abs_z": round(max(zs), 6)}
        require(forbidden == 0, f"block {block}: {forbidden} shots outside the {name} support")
        require(max(zs) < Z_LIMIT, f"block {block}: an outcome sits at |z| {max(zs):.2f} from the {name} spectrum")
    require(counts["stray"] == 0, f"{counts['stray']} shots excite a qubit outside the blocks")
    return verdicts


def conformance(directories: dict[str, dict[str, str]], live: bool) -> dict[str, Any]:
    jobs = conformance_jobs(directories)
    histograms = []
    if live:
        payload = json.dumps([[job["text"], CONFORMANCE_SHOTS, job["seed"]] for job in jobs])
        histograms = json.loads(qi_stack.run(["-B", "-W", "error", str(QX_WORKER), "--qx-worker"], payload))
        require(len(histograms) == len(jobs), "the qxelarator worker returned a histogram per job")
    ideal = json.loads(directories[FAMILY]["batch-01/cases.json"])["classes"]
    rows = []
    for n, job in enumerate(jobs):
        row = {k: v for k, v in job.items() if k != "text"}
        if live:
            row["counts"] = reduce_counts(histograms[n], job["blocks"])
        rows.append(row)
    return {"schema": CONFORMANCE_SCHEMA, "qxelarator": qi_stack.pins()["qxelarator"], "shots": CONFORMANCE_SHOTS,
            "ideal": ideal, "circuits": rows}  # fmt: skip


def check_header(retained: dict[str, Any], fresh: dict[str, Any]) -> None:
    """The record's schema, pinned qxelarator version, shots and ideal spectra equal the regenerated header."""
    for key in ("schema", "qxelarator", "shots", "ideal"):
        require(retained.get(key) == fresh[key], f"record header {key} differs from {fresh[key]!r}")


def check_conformance(directories: dict[str, dict[str, str]], path: Path) -> str:
    """The retained record against the regenerated jobs; a live qxelarator rerun must equal its counts."""
    retained = json.loads(path.read_text(encoding="utf-8"))
    live = qi_stack.live("qxelarator", "judged the retained counts")
    fresh = conformance(directories, live)
    keys = ("file", "sha256", "seed", "classes", "blocks")
    check_header(retained, fresh)
    require(
        [{k: r[k] for k in keys} for r in retained["circuits"]] == [{k: r[k] for k in keys} for r in fresh["circuits"]],
        "the record's circuits differ from the regenerated series",
    )
    for row, again in zip(retained["circuits"], fresh["circuits"], strict=True):
        if live:
            require(row["counts"] == again["counts"], f"{row['file']}: qxelarator counts differ at seed {row['seed']}")
        require(judge(row["counts"], row["classes"], retained["ideal"]) == row["verdicts"], f"{row['file']}: verdicts")
    return "live" if live else "replayed"


def expect_rejection(label: str, action: Any) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(f"self-test: {label} was accepted")


def self_test() -> None:
    """Every admission rule rejects its corrupted input; the searched circuits pass their own checks."""
    global BLOCKS, EXEMPLARS
    saved_blocks, saved_exemplars = BLOCKS, EXEMPLARS
    try:
        EXEMPLARS = {"high": (1, 2), "low": (9, 18)}
        expect_rejection("a quadratic pair as an exemplar", lambda: exemplar("high"))
        EXEMPLARS = {"high": (9, 18), "low": (1, 16)}
        expect_rejection("exemplars in swapped classes", lambda: exemplar("high"))
        EXEMPLARS = saved_exemplars
        BLOCKS = {"X": (1, 4, 12, 8), "Y": saved_blocks["Y"]}
        expect_rejection("a block path over an uncoupled pair", check_layout)
        BLOCKS = {"X": saved_blocks["X"], "Y": (8, 11, 14, 16)}
        expect_rejection("overlapping blocks", check_layout)
        BLOCKS = {"X": saved_blocks["Y"], "Y": saved_blocks["X"]}
        expect_rejection("the context qubit outside block Y", check_layout)
        BLOCKS = {"X": (5, 8, 4, 1), "Y": saved_blocks["Y"]}
        expect_rejection("a block on an excluded qubit", check_layout)
    finally:
        BLOCKS, EXEMPLARS = saved_blocks, saved_exemplars
    check_layout()
    expect_rejection("a two-qubit gate budget below the class minimum", lambda: path_search(True, 4))
    solutions = path_search(False)
    for name, solution in solutions.items():
        ops = block_ops(solution)
        info = exemplar(name)
        census_map(probabilities(ops, tuple(range(WIDTH))), info["p"])
        first_t = next(k for k, (g, _) in enumerate(ops) if g == "T")
        first_cz = next(k for k, (g, _) in enumerate(ops) if g == "CZ")
        mutated = {
            "its first T inverted": [("Tdag", on) if k == first_t else (g, on) for k, (g, on) in enumerate(ops)],
            "its first CZ dropped": [op for k, op in enumerate(ops) if k != first_cz],
        }
        for label, gates in mutated.items():
            phys = probabilities(gates, tuple(range(WIDTH)))
            expect_rejection(f"{name} with {label}", partial(census_map, phys, info["p"]))
    text = walsh_text(CIRCUITS["walsh-c1"], {name: block_ops(s) for name, s in solutions.items()})
    uncoupled = text.replace("CZ q[1], q[4]", "CZ q[1], q[8]")
    excluded = text.replace("H q[1]\n", "H q[9]\n", 1)
    expect_rejection("a CZ on an uncoupled pair", partial(check_tuna, "x.cq", uncoupled, True))
    expect_rejection("a witness on an excluded qubit", partial(check_tuna, "x.cq", excluded, True))
    expect_rejection("a gate outside the case set", lambda: gate_lines(text.replace("T q[1]", "Rz(0.1) q[1]", 1)))
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    tuna = tuna_backend(catalogue)
    shared = {"family": FAMILY, "backend": tuna["identifier"], "nqubits": TUNA_QUBITS, "dialect": "tuna"}
    texts = dict(readout_circuits(TUNA_QUBITS)) | {"w.cq": text}
    row = {"file": "w.cq", "kind": "witness"}
    zero, one = {"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"}
    expect_rejection("a four-circuit batch", lambda: write(shared, [[zero, one, row, row]], texts, tuna))
    unclosed = [[zero, one, row], [row]]
    expect_rejection("a series without its closing bracket", partial(write, shared, unclosed, texts, tuna))
    write(shared, [[zero, one, row], [row, row], [zero, one, row]], texts, tuna)
    retained = json.loads(CONFORMANCE.read_text(encoding="utf-8"))
    fresh = conformance(series(), False)
    check_header(retained, fresh)
    for key, value in (("schema", "qi-walsh-exemplar-qx-conformance-v0"), ("qxelarator", "0.9.0")):
        expect_rejection(
            f"a conformance record with {key} {value}", partial(check_header, retained | {key: value}, fresh)
        )
    print("walsh exemplar cases self-test: every corrupted input rejected")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="DIR")
    mode.add_argument("--check", type=Path, metavar="DIR")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--write-conformance", type=Path, metavar="RECORD")
    mode.add_argument("--check-conformance", type=Path, metavar="RECORD")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.write_conformance or args.check_conformance:
        try:
            directories = series()
            if args.check_conformance:
                how = check_conformance(directories, args.check_conformance)
                print(f"walsh exemplar qx conformance: {how}, every block inside its class's support and z limit")
                return 0
            record = conformance(directories, True)
            for row in record["circuits"]:
                row["verdicts"] = judge(row["counts"], row["classes"], record["ideal"])
        except ValueError as error:
            raise SystemExit(str(error)) from error
        args.write_conformance.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(f"walsh exemplar qx conformance: {len(record['circuits'])} circuits written")
        return 0
    try:
        directories = series()
    except ValueError as error:
        raise SystemExit(str(error)) from error
    count = 0
    for directory, files in directories.items():
        root = (args.write or args.check) / directory
        if args.check:
            retained = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            if retained != set(files):
                raise SystemExit(f"{root}: files {sorted(retained ^ set(files))[:8]} differ from the regeneration")
        for name, text in files.items():
            path = root / name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
            count += 1
    print(f"walsh exemplar cases: {count} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
