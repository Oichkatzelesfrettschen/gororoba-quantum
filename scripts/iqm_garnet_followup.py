"""IQM Garnet follow-up case: Grover depth, single-qubit load, qubit-versus-role, and sedenion sign-row Walsh
spectroscopy, built on the line-native CCZ compile of scripts/iqm_grover_line.py.

The retained grover-line-ccz run (docs/design/iqm-garnet-grover-line-ccz.md) leaves four questions this case
answers in two jobs on one calibration set (the written case: docs/design/iqm-garnet-grover-depth-sedenion-walsh.md).

Job "grover" (three qubits, the retained path FORWARD_PATH and its reversal):
  m101-k1 one iteration four ways, four copies each in blocks L P F G and G F P L mirrored about the job's
                     center: line-native (L, 14 CZ, 22 prx); padded (P, the line arm with identity prx pairs
                     placed to match F's per-qubit prx counts within one, 38 prx at the line's CZ list); fused
                     (F, the 18-CZ generic compile at grover.TRANSPILER_SEED with its logical wires permuted by
                     GENERIC_PERMUTATION so that it measures the line's mapping, each run of prx between CZs
                     fused, 38 prx); generic (G, that compile as emitted, 68 prx). L - P and F - G each change
                     only the prx count at a fixed CZ list; P - F changes only the CZ list, at equal prx and one
                     measurement mapping.
  m101-k2, m101-k3, k0, m011-k1, m011-k2, m011-k3   the depth series, grouped at the job's center (not mirrored):
                     three depths test the geometric retention law lambda_k = A r^k that two depths fit exactly;
                     k0 is the reference of the unmarked-uniformity test.
  r-m101-k1 (four copies), r-m011-k1 (two)   the reversed path: QB20 and QB17 exchange logical roles while QB16
                     keeps the middle.
  ro-xyz             the eight readout preparations on FORWARD_PATH (the reversed arms measure the same qubits).

Job "sedenion" (four qubits on a square):
  s5-row, s5-trunc, s5-id, s10-row, s10-trunc, s10-id   H on every wire, a phase oracle, H on every wire. The row
                     is the left sign row diag(cd_sign(16, m, x)) of the sedenion basis element e_m
                     (gororoba_quantum/sedenion_sign_oracle.py): 8 CNOTs on the square for m = 5 and m = 10, whose
                     two bits sit on opposite corners; ideal output 9/16 on one string, 1/16 on seven, 0 on eight.
                     trunc is the mutation, the degree-two truncation of the row's sign polynomial: the same CNOT
                     network with four of the row's eight parity phases removed and the other four changed, so the
                     CZ list is identical while the prx count falls (12 to 8); its ideal output puts 1/4 on four
                     strings. id runs the same network with every phase zero, the null arm, ideal output 0000.
                     Row, truncation and null run two copies each in mirrored order.
  ro4-wxyz           the sixteen readout preparations on the square.

The Grover arms run on the retained case's path (no re-selection on this calibration) and its reversal; the
square is SQUARE, which the rule (highest predicted mean peak probability of the two rows, labeled from its
lowest-index qubit toward that qubit's lower-index square neighbor) chose on calibration set ea681de1 and which
later rebuilds keep. Every prediction is the exact density matrix of iqm_grover_line.predicted's model
(depolarizing PRX and CZ, idle T1 and T2 over the ASAP schedule, herald-conditioned readout), generalized here
to four qubits. Native compiles drop the final Z frames, so they agree with their logical circuits in every
computational-basis probability, not as unitaries.

Usage: "$PYTHON" scripts/iqm_garnet_followup.py (build DIR --calibration SRC | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import cmath
import itertools
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_grover_line as grover  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import ACTIVE_SHOT_SECONDS, CALIBRATION_FILES, OPTIONS, relaxed, target_of  # noqa: E402

import sedenion_sign_oracle as sed  # noqa: E402
from grover_line_analysis import ideal_probability  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "grover-depth-sedenion-walsh"
QCS = ["garnet:mock", "garnet"]
PRICE = grover.PRICE
SHOTS = {"grover": 4000, "sedenion": 1000}
RETAINED_CASE = ROOT / "results" / "iqm" / "cases" / grover.CASE
FORWARD_PATH = ["QB20", "QB16", "QB17"]
REVERSED_PATH = FORWARD_PATH[::-1]
ROWS = (5, 10)
COPIES = 4
# Logical-wire permutation of the generic compile: of the six, at the retained seed, this one ends with the
# line-native arm's measurement mapping (logical bit q on path position q), so line and generic arms differ in
# their CZ list alone (18 CZ, 68 prx emitted, 38 fused); none of the six fuses below 37 prx.
GENERIC_PERMUTATION = (2, 0, 1)
# The square the selection rule chose on calibration set ea681de1 (score 0.5115; the next three within 0.004).
# A rebuild on a later calibration keeps it, so the square is never re-selected on the predicting calibration.
SQUARE = ["QB11", "QB12", "QB17", "QB16"]
KINDS = ("padded", "fused", "generic")
DEPTHS = (("101", 2), ("101", 3), ("011", 1), ("011", 2), ("011", 3))
H = grover.H
X = grover.X

Arm = dict[str, Any]


def count(circuit: dict[str, Any], name: str) -> int:
    return sum(op["name"] == name for op in circuit["instructions"])


def fused(circuit: dict[str, Any], path: list[str], name: str) -> dict[str, Any]:
    """The circuit with every run of prx between two CZ on one qubit fused into one prx, the residual Z rotation
    carried as a frame through the CZ (which commutes with it) into the next prx and dropped before the measure;
    the CZ sequence and its loci are unchanged."""
    pending = [np.eye(2, dtype=complex) for _ in path]
    out: list[dict[str, Any]] = []
    measure: dict[str, Any] | None = None

    def flush(p: int) -> None:
        theta, phi, gamma = grover.euler(pending[p])
        if theta > 1e-9:
            out.append(
                {"name": "prx", "locus": [path[p]], "args": {"angle": grover.angle(theta), "phase": grover.angle(phi)}}
            )
        pending[p] = grover.rz(gamma)

    for op in circuit["instructions"]:
        if op["name"] == "prx":
            p = path.index(op["locus"][0])
            pending[p] = grover.prx_matrix(op["args"]["angle"], op["args"]["phase"]) @ pending[p]
        elif op["name"] == "cz":
            for q in op["locus"]:
                flush(path.index(q))
            out.append(op)
        elif op["name"] == "measure":
            measure = op
        else:
            raise ValueError(f"{name}: unexpected {op['name']}")
    if measure is None:
        raise ValueError(f"{name}: no measurement")
    for p in range(len(path)):
        flush(p)
    out.append(measure)
    return {"name": name, "instructions": out}


def generic_mapped(marked: str, path: list[str], name: str) -> dict[str, Any]:
    """One iteration through qiskit's optimization level 3 at the retained seed, with logical wire q placed on
    circuit wire GENERIC_PERMUTATION[q]: the generic compile whose measurement reads logical bit q on path[q]."""
    perm = GENERIC_PERMUTATION
    logical = QuantumCircuit(3, 3)
    for op in grover.grover_ops(marked, 1):
        if op[0] == "h":
            logical.h(perm[op[1]])
        elif op[0] == "x":
            logical.x(perm[op[1]])
        else:
            logical.ccz(0, 1, 2)
    for q in range(3):
        logical.measure(perm[q], q)
    compiled = transpile(
        logical,
        basis_gates=["r", "cz"],
        coupling_map=CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1]]),
        initial_layout=[0, 1, 2],
        optimization_level=3,
        seed_transpiler=grover.TRANSPILER_SEED,
    )
    out: list[dict[str, Any]] = []
    readout: dict[int, str] = {}
    for item in compiled.data:
        op = item.operation
        locus = [path[compiled.find_bit(q).index] for q in item.qubits]
        if op.name == "r":
            theta, phi = (float(p) for p in op.params)
            args = {"angle": grover.angle(theta), "phase": grover.angle(phi)}
            out.append({"name": "prx", "locus": locus, "args": args})
        elif op.name == "cz":
            out.append({"name": "cz", "locus": locus, "args": {}})
        elif op.name == "measure":
            readout[compiled.find_bit(item.clbits[0]).index] = locus[0]
        elif op.name != "barrier":
            raise ValueError(f"{name}: {op.name} is not a Garnet native operation")
    out.append({"name": "measure", "locus": [readout[q] for q in range(3)], "args": {"key": "m"}})
    return {"name": name, "instructions": out}


def prx_per_qubit(circuit: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for op in circuit["instructions"]:
        if op["name"] == "prx":
            out[op["locus"][0]] = out.get(op["locus"][0], 0) + 1
    return out


def pad_pairs(base: dict[str, Any], target: dict[str, Any], path: list[str]) -> dict[str, int]:
    """Identity pairs per qubit that bring base's prx count to target's: each qubit takes half its deficit,
    rounded down, and the pairs left go to the qubits with an odd deficit in path order, so per-qubit counts
    match to within one prx and the totals match exactly."""
    have, want = prx_per_qubit(base), prx_per_qubit(target)
    deficit = {q: want.get(q, 0) - have.get(q, 0) for q in path}
    total = sum(deficit.values())
    if total < 0 or total % 2:
        raise ValueError(f"prx deficit {deficit} cannot be met by pairs")
    pairs = {q: max(d, 0) // 2 for q, d in deficit.items()}
    for q in path:
        if sum(pairs.values()) == total // 2:
            break
        if deficit[q] > 0 and deficit[q] % 2:
            pairs[q] += 1
    if sum(pairs.values()) != total // 2:
        raise ValueError(f"prx deficit {deficit} gives pairs {pairs}")
    return pairs


def padded(circuit: dict[str, Any], pairs: dict[str, int], name: str) -> dict[str, Any]:
    """The circuit with identity pairs prx(pi/2, 0) prx(pi/2, pi) on each named qubit, one pair before each of
    that qubit's first CZ until its count is met: the same CZ sequence, loci, measurement and unitary, since
    prx(theta, phi + pi) = prx(-theta, phi)."""
    out: list[dict[str, Any]] = []
    left = dict(pairs)
    half = grover.angle(math.pi / 2)
    for op in circuit["instructions"]:
        if op["name"] == "cz":
            for qubit in op["locus"]:
                if left.get(qubit, 0):
                    out.append({"name": "prx", "locus": [qubit], "args": {"angle": half, "phase": 0.0}})
                    out.append(
                        {"name": "prx", "locus": [qubit], "args": {"angle": half, "phase": grover.angle(math.pi)}}
                    )
                    left[qubit] -= 1
        out.append(op)
    if any(left.values()):
        raise ValueError(f"{name}: pairs left over {left}")
    return {"name": name, "instructions": out}


def compile_native(ops: list[tuple[Any, ...]], path: list[str], name: str) -> dict[str, Any]:
    """Native prx and cz of logical gates on path positions ("h", p), ("x", p), ("phase", p, angle) and
    ("cnot", c, t), a CNOT as H CZ H on its target, Z rotations carried as frames; measures every position in
    path order."""
    pending = [np.eye(2, dtype=complex) for _ in path]
    out: list[dict[str, Any]] = []

    def flush(p: int) -> None:
        theta, phi, gamma = grover.euler(pending[p])
        if theta > 1e-9:
            out.append(
                {"name": "prx", "locus": [path[p]], "args": {"angle": grover.angle(theta), "phase": grover.angle(phi)}}
            )
        pending[p] = grover.rz(gamma)

    for op in ops:
        if op[0] in ("h", "x"):
            pending[op[1]] = (H if op[0] == "h" else X) @ pending[op[1]]
        elif op[0] == "phase":
            pending[op[1]] = np.diag([1, cmath.exp(1j * op[2])]) @ pending[op[1]]
        elif op[0] == "cnot":
            control, target = op[1], op[2]
            pending[target] = H @ pending[target]
            flush(control)
            flush(target)
            out.append({"name": "cz", "locus": [path[control], path[target]], "args": {}})
            pending[target] = H @ pending[target]
        else:
            raise ValueError(f"{name}: unknown logical gate {op[0]}")
    for p in range(len(path)):
        flush(p)
    out.append({"name": "measure", "locus": list(path), "args": {"key": "m"}})
    return {"name": name, "instructions": out}


def embed(gate: np.ndarray, q: int, n: int) -> np.ndarray:
    full = np.zeros((2**n, 2**n), dtype=complex)
    for i in range(2**n):
        for j in range(2**n):
            if (i ^ j) & ~(1 << q) == 0:
                full[i, j] = gate[(i >> q) & 1, (j >> q) & 1]
    return full


def ideal(circuit: dict[str, Any], path: list[str]) -> np.ndarray:
    """Noiseless probability of each outcome index sum(bit_q << q), bit q read from the q-th measured qubit."""
    n = len(path)
    state = np.zeros(2**n, dtype=complex)
    state[0] = 1
    measured: list[int] = []
    for op in circuit["instructions"]:
        where = [path.index(q) for q in op["locus"]]
        if op["name"] == "prx":
            state = embed(grover.prx_matrix(op["args"]["angle"], op["args"]["phase"]), where[0], n) @ state
        elif op["name"] == "cz":
            a, b = where
            state = np.array([-v if (i >> a) & (i >> b) & 1 else v for i, v in enumerate(state)])
        elif op["name"] == "measure":
            measured = where
    out = np.zeros(2**n)
    for i in range(2**n):
        out[sum(((i >> p) & 1) << q for q, p in enumerate(measured))] += abs(state[i]) ** 2
    return out


def key(index: int, n: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(n))


def predicted(item: tuple[str, str]) -> dict[str, float]:
    """iqm_grover_line.predicted's exact model for a circuit on any number of measured qubits."""
    circuit_text, calibration_dir = item
    circuit = json.loads(circuit_text)
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, _ = target_of(calibration)
    qiskit_circuit, bits = iqm_sim.to_qiskit(circuit, calibration)
    measured = [calibration.qubits.index(qubit) for _, qubit in bits]
    unmeasured = qiskit_circuit.remove_final_measurements(inplace=False)
    scheduled = transpile(unmeasured, target=target, optimization_level=0, scheduling_method="asap")
    body = relaxed(calibration, scheduled)
    if any(item.operation.name in ("measure", "reset") for item in body.data):
        raise ValueError(f"{circuit['name']}: a measure or reset precedes the joint final measure")
    body.save_probabilities(measured)
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model())
    read = np.asarray(simulator.run(body).result().data(0)["probabilities"], dtype=float)
    n = len(bits)
    for q, (_, qubit) in enumerate(bits):
        e01, e10 = calibration.readout(qubit, heralded=True)
        confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
        read = np.einsum("rt,atb->arb", confusion, read.reshape(2 ** (n - 1 - q), 2, 2**q)).reshape(2**n)
    return {key(i, n): round(float(read[i]), 9) for i in range(2**n)}


def readout_circuit(bits: str, path: list[str], prefix: str) -> dict[str, Any]:
    out: list[dict[str, Any]] = [
        {"name": "prx", "locus": [path[q]], "args": {"angle": grover.angle(math.pi), "phase": 0.0}}
        for q in range(len(path))
        if bits[q] == "1"
    ]
    out.append({"name": "measure", "locus": list(path), "args": {"key": "m"}})
    return {"name": f"{prefix}-{bits}", "instructions": out}


def oracle_angles(m: int, kind: str) -> dict[int, int]:
    """Parity angles in eighths of pi: the row, its degree-two truncation, or none (the identity)."""
    bits = sed.row_bits(m)
    if kind == "row":
        return sed.phase_eighths(bits)
    if kind == "trunc":
        return sed.phase_eighths(sed.truncated_bits(bits))
    if kind == "id":
        return {}
    raise ValueError(kind)


def sedenion_circuit(m: int, kind: str, square: list[str], name: str) -> tuple[dict[str, Any], np.ndarray]:
    """The native circuit H, oracle, H on the square, and its ideal distribution from the 16 x 16 algebra
    (H P D H on |0000>, P the network's final relabeling and D the oracle's diagonal)."""
    row = sed.phase_eighths(sed.row_bits(m))
    net, final = sed.network("square", frozenset(row), False)
    angles = oracle_angles(m, kind)
    oracle, _ = sed.oracle_ops(net, angles)
    ops: list[tuple[Any, ...]] = [("h", p) for p in range(4)] + oracle + [("h", p) for p in range(4)]
    h4: np.ndarray = np.ones((1, 1))
    for _ in range(4):
        h4 = np.kron(H, h4)
    state = h4 @ sed.relabeling(final) @ np.diag(sed.diagonal_of(angles)) @ h4[:, 0]
    return compile_native(ops, square, name), np.abs(state) ** 2


def squares(calibration: iqm_sim.Calibration) -> list[list[str]]:
    """Every four-cycle of the coupler graph, labeled from its lowest-index qubit toward that qubit's
    lower-index neighbor on the cycle."""
    order = calibration.qubits.index
    adjacent: dict[str, set[str]] = {q: set() for q in calibration.qubits}
    for pair in calibration.cz:
        a, b = tuple(pair)
        adjacent[a].add(b)
        adjacent[b].add(a)
    found: set[frozenset[str]] = set()
    out: list[list[str]] = []
    for a in calibration.qubits:
        for b, d in itertools.combinations(sorted(adjacent[a], key=order), 2):
            for c in sorted((adjacent[b] & adjacent[d]) - {a}, key=order):
                cycle = frozenset((a, b, c, d))
                if cycle in found:
                    continue
                found.add(cycle)
                start = min(cycle, key=order)
                ring = [a, b, c, d]
                i = ring.index(start)
                ring = ring[i:] + ring[:i]
                if order(ring[3]) < order(ring[1]):
                    ring = [ring[0], ring[3], ring[2], ring[1]]
                out.append(ring)
    return out


def square_score(item: tuple[list[str], str]) -> tuple[list[str], float | None, str | None]:
    square, calibration_dir = item
    try:
        peaks = []
        for m in ROWS:
            circuit, p = sedenion_circuit(m, "row", square, f"s{m}-row")
            peaks.append(predicted((dump(circuit), calibration_dir))[key(int(np.argmax(p)), 4)])
        return square, round(sum(peaks) / len(peaks), 9), None
    except (KeyError, ValueError) as error:
        return square, None, f"{type(error).__name__}: {error}"


def grover_arms() -> list[Arm]:
    path, rev = FORWARD_PATH, REVERSED_PATH

    def line(marked: str, k: int, p: list[str], name: str) -> Arm:
        circuit = grover.line_arm(marked, k, p, name)[1]
        return {"name": name, "circuit": circuit, "path": p, "marked": marked, "k": k}

    def one_iteration(kind: str, copy: int) -> Arm:
        name = "m101-k1" + ("" if kind == "line" else f"-{kind}") + f"-c{copy}"
        if kind == "line":
            return line("101", 1, path, name)
        generic = generic_mapped("101", path, name)
        if kind == "padded":
            base = grover.line_arm("101", 1, path, name)[1]
            pairs = pad_pairs(base, fused(generic, path, name), path)
            return {"name": name, "circuit": padded(base, pairs, name), "path": path, "marked": "101", "k": 1}
        circuit = generic if kind == "generic" else fused(generic, path, name)
        return {"name": name, "circuit": circuit, "path": path, "marked": "101", "k": 1}

    # Copy blocks sit at positions mirrored about the job's center, each block the reverse of its mirror, so
    # every arm's summed position is equal and a drift linear in position cancels from each pairwise contrast.
    blocks = [
        [one_iteration(kind, copy) for kind in (order if copy in (0, 2) else order[::-1])]
        for copy, order in zip(range(COPIES), [("line", "padded", "fused", "generic")] * COPIES, strict=True)
    ]
    # The depth arms sit in one block at the job's center (k0 in the middle); they are not mirrored, so a drift
    # linear in position enters each depth statistic through offsets of at most three positions.
    depth_arms = [line(m, k, path, f"m{m}-k{k}") for m, k in DEPTHS]
    depth = [*depth_arms[:3], line("000", 0, path, "k0"), *depth_arms[3:]]
    reversed_first = [line("101", 1, rev, "r-m101-k1-c0"), line("011", 1, rev, "r-m011-k1-c0")]
    reversed_mid = [line("101", 1, rev, "r-m101-k1-c1"), line("101", 1, rev, "r-m101-k1-c2")]
    reversed_last = [line("011", 1, rev, "r-m011-k1-c1"), line("101", 1, rev, "r-m101-k1-c3")]
    readout = [
        {"name": c["name"], "circuit": c, "path": path, "marked": None, "k": None}
        for c in (readout_circuit("".join(b), path, "ro") for b in itertools.product("01", repeat=3))
    ]
    out = (
        blocks[0]
        + readout[:4]
        + reversed_first
        + blocks[1]
        + reversed_mid[:1]
        + depth
        + reversed_mid[1:]
        + blocks[2]
        + reversed_last
        + readout[4:]
        + blocks[3]
    )
    total = len(out)
    sums = {kind: sum(n for n, a in enumerate(out) if a["name"].startswith(f"m101-k1-{kind}-c")) for kind in KINDS}
    sums["line"] = sum(n for n, a in enumerate(out) if a["name"].startswith("m101-k1-c"))
    if len(set(sums.values())) != 1 or any(
        out[n]["name"].rsplit("-c", 1)[0] != out[total - 1 - n]["name"].rsplit("-c", 1)[0]
        for n in range(total)
        if out[n]["name"].startswith("m101-k1")
    ):
        raise AssertionError(f"one-iteration copies are not mirrored: summed positions {sums}")
    return out


def sedenion_arms(square: list[str]) -> list[Arm]:
    def arm(m: int, kind: str, name: str) -> Arm:
        circuit, p = sedenion_circuit(m, kind, square, name)
        return {"name": name, "circuit": circuit, "path": square, "m": m, "kind": kind, "ideal": p}

    # Each row's null runs its own network with every phase zero, so row, truncation and null share one CZ list.
    first = [arm(m, "id", f"s{m}-id-c0") for m in ROWS]
    for m in ROWS:
        first += [arm(m, "row", f"s{m}-row-c0"), arm(m, "trunc", f"s{m}-trunc-c0")]
    last = []
    for m in reversed(ROWS):
        last += [arm(m, "trunc", f"s{m}-trunc-c1"), arm(m, "row", f"s{m}-row-c1")]
    last += [arm(m, "id", f"s{m}-id-c1") for m in reversed(ROWS)]
    readout = [
        {"name": c["name"], "circuit": c, "path": square, "m": None, "kind": None, "ideal": None}
        for c in (readout_circuit("".join(b), square, "ro4") for b in itertools.product("01", repeat=4))
    ]
    return first + readout + last


# Heralded kept fraction of the retained run (13,700 kept of 16,000 requested in the line arm, 85.6 %).
KEPT = 0.856


def se_difference(p1: float, n1: float, p2: float, n2: float) -> float:
    return math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)


def retention(p: float, k: int) -> float:
    return (p - 1 / 8) / (ideal_probability(k) - 1 / 8)


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    retained = json.loads((RETAINED_CASE / "prediction.json").read_text(encoding="utf-8"))
    if retained["path"] != FORWARD_PATH:
        raise ValueError(f"the retained case ran on {retained['path']}, not {FORWARD_PATH}")
    scored = ordered_map(square_score, [(s, str(calibration_dir)) for s in squares(calibration)], min_items=1)
    usable = [(score, s) for s, score, _ in scored if score is not None]
    if SQUARE not in [s for _, s in usable]:
        raise ValueError(f"the case's square {SQUARE} has no complete calibration")
    square = SQUARE
    jobs = {"grover": grover_arms(), "sedenion": sedenion_arms(square)}
    files: dict[str, str] = {}
    for arms in jobs.values():
        for arm in arms:
            files[f"circuits/{arm['name']}.json"] = dump(arm["circuit"])
    names = [arm["name"] for arms in jobs.values() for arm in arms]
    distributions = ordered_map(
        predicted, [(files[f"circuits/{name}.json"], str(calibration_dir)) for name in names], min_items=1
    )
    predictions = dict(zip(names, distributions, strict=True))
    arm_records: dict[str, Any] = {}
    for job, arms in jobs.items():
        for arm in arms:
            c = arm["circuit"]
            record: dict[str, Any] = {
                "job": job,
                "locus": c["instructions"][-1]["locus"],
                "cz": count(c, "cz"),
                "prx": count(c, "prx"),
                "predicted": predictions[arm["name"]],
            }
            if job == "grover" and arm["marked"] is not None:
                record |= {
                    "marked": arm["marked"],
                    "iterations": arm["k"],
                    "ideal_marked": ideal_probability(arm["k"]),
                    "predicted_marked": predictions[arm["name"]][arm["marked"]],
                }
            if job == "sedenion" and arm["kind"] is not None:
                row_ideal = sedenion_circuit(arm["m"], "row", square, "x")[1]
                peak = key(int(np.argmax(row_ideal)), 4)
                record |= {
                    "m": arm["m"],
                    "kind": arm["kind"],
                    "row_peak": peak,
                    "ideal": {key(i, 4): round(float(v), 9) for i, v in enumerate(arm["ideal"]) if v > 1e-12},
                    "predicted_row_peak": predictions[arm["name"]][peak],
                }
            arm_records[arm["name"]] = record
    job_records = []
    for job, arms in jobs.items():
        expected = round(len(arms) * SHOTS[job] * ACTIVE_SHOT_SECONDS, 3)
        job_records.append(
            {
                "job": job,
                "circuits": [
                    {
                        "file": f"circuits/{a['name']}.json",
                        "sha256": sha256(files[f"circuits/{a['name']}.json"].encode()),
                    }
                    for a in arms
                ],
                "shots": SHOTS[job],
                "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
                "expected_seconds": expected,
                "max_credits": {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS},
            }
        )
    prediction = {
        "calibration_set": calibration.set_id,
        "forward_path": FORWARD_PATH,
        "reversed_path": REVERSED_PATH,
        "square": square,
        "squares_scored": [{"square": s, "score": round(v, 4)} for v, s in sorted(usable, key=lambda i: -i[0])],
        "squares_skipped": [{"square": s, "reason": r} for s, v, r in scored if v is None],
        "arms": arm_records,
        "decisions": decisions(arm_records),
        "model": (
            "exact density matrix: iqm_sim depolarizing PRX and CZ, ASAP idle T1/T2, herald-conditioned readout "
            "assignment; no coherent error, leakage or crosstalk"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            # The approval quotes this file's digest, so the prediction the analysis decides against is bound.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "question": (
                "On one Garnet calibration: does the line-native Grover retention stay geometric at a third depth, "
                "does fusing the generic compile's single-qubit gates recover its loss, does the per-qubit error "
                "profile follow the qubit or the logical role, and does a sedenion left sign row imprint its exact "
                "Walsh peak, against its degree-two truncation on the same CZ sequence?"
            ),
            "qcs": QCS,
            "jobs": job_records,
        }
    )
    return files, prediction


def pooled(arms: dict[str, Any], stem: str, outcome: str) -> tuple[float, float]:
    """Mean predicted probability of one outcome over the copies of an arm, and the kept shots they pool."""
    copies = [a for name, a in arms.items() if name == stem or name.startswith(stem + "-c")]
    shots = SHOTS[copies[0]["job"]] * KEPT * len(copies)
    return sum(a["predicted"][outcome] for a in copies) / len(copies), shots


def decision(arms: dict[str, Any], first: str, second: str, outcome: str, rule: str) -> dict[str, Any]:
    p1, n1 = pooled(arms, first, outcome)
    p2, n2 = pooled(arms, second, outcome)
    se = se_difference(p1, n1, p2, n2)
    return {
        "rule": rule,
        "predicted": round(p1 - p2, 4),
        "se_at_planned_shots": round(se, 4),
        "predicted_z": round((p1 - p2) / se, 2),
    }


def end_bits(arms: dict[str, Any], stem: str) -> tuple[float, float, float]:
    """For an arm marked 101 (both end bits ideally 1), averaged over its copies: D = P(QB17 wrong) - P(QB20 wrong),
    the per-shot variance of I(QB17 wrong) - I(QB20 wrong) from the joint outcome distribution (which carries
    the covariance of two bits read in one shot), and the kept shots pooled."""
    copies = [a for name, a in arms.items() if name == stem or name.startswith(stem + "-c")]
    d = 0.0
    second = 0.0
    for arm in copies:
        q17, q20 = arm["locus"].index("QB17"), arm["locus"].index("QB20")
        for outcome, p in arm["predicted"].items():
            x = (outcome[q17] != "1") - (outcome[q20] != "1")
            d += x * p / len(copies)
            second += x * x * p / len(copies)
    return d, second - d * d, SHOTS["grover"] * KEPT * len(copies)


def role_decision(arms: dict[str, Any]) -> dict[str, Any]:
    """QB20 and QB17 exchange logical roles between the two paths while QB16 keeps the middle. On mark 101 both
    end bits are ideally 1, so D = w(QB17) - w(QB20) compares the two qubits alone; mark 011 mixes qubit quality
    with the asymmetry of e01 and e10 and is reported, not decided."""
    out: dict[str, Any] = {}
    for label, stem in (("forward", "m101-k1"), ("reversed", "r-m101-k1")):
        d, variance, shots = end_bits(arms, stem)
        se = math.sqrt(variance / shots)
        out[label] = {"D": round(d, 4), "se_paired": round(se, 4), "z": round(d / se, 2)}
    return {
        "rule": (
            "D = w(QB17) - w(QB20) from raw frequencies of the m101-k1 arms on each path (four copies each), with the "
            "paired per-shot variance of I(QB17 wrong) - I(QB20 wrong); when the forward D resolves (|z| > 3), a "
            "reversed D of the same sign resolved keeps the difference with the qubits, a reversed D of the "
            "opposite sign resolved moves it with the roles, and anything else leaves the question open; the "
            "m011 arms are reported beside"
        ),
        "model": out,
        "retained_corrected_wrong_bit_m101_k1": {"QB20": 0.1542, "QB16": 0.18, "QB17": 0.1775},
        "retained_corrected_wrong_bit_m011_k1": {"QB20": 0.1961, "QB16": 0.1833, "QB17": 0.1702},
    }


def decisions(arms: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "z_resolve": grover.Z_RESOLVE,
        "prx_load_generic": decision(
            arms,
            "m101-k1-fused",
            "m101-k1-generic",
            "101",
            "P(101) of fused minus generic, four copies each: 30 prx at the fixed 18-CZ generic sequence",
        ),
        "prx_load_line": decision(
            arms,
            "m101-k1",
            "m101-k1-padded",
            "101",
            "P(101) of line minus padded line, four copies each: 16 identity-pair prx at the fixed 14-CZ line sequence",
        ),
        "cz_sequence": decision(
            arms,
            "m101-k1-padded",
            "m101-k1-fused",
            "101",
            (
                "P(101) of padded line minus fused generic: 14 against 18 CZ on one logical-to-physical measurement "
                "mapping, at equal total prx and per-qubit prx counts within one"
            ),
        ),
        "k0_reference": (
            "the corrected uniformity Wald statistic of k0 (7 degrees of freedom) is the reference of the unmarked "
            "uniformity test of every Grover arm, as in the retained analysis"
        ),
    }
    for marked in grover.MARKS:
        stems = {k: f"m{marked}-k{k}" for k in (1, 2, 3)}
        pooled_p = {k: pooled(arms, stems[k], marked) for k in stems}
        lam = {k: retention(p, k) for k, (p, _) in pooled_p.items()}
        se = {k: math.sqrt(p * (1 - p) / n) / (ideal_probability(k) - 1 / 8) for k, (p, n) in pooled_p.items()}
        # Delta method for lambda_3 - lambda_2^2 / lambda_1 over three independent arms.
        gradient = {3: 1.0, 2: -2 * lam[2] / lam[1], 1: lam[2] ** 2 / lam[1] ** 2}
        se_f = math.sqrt(sum((gradient[k] * se[k]) ** 2 for k in se))
        out[f"depth_law_{marked}"] = {
            "rule": (
                "f = lambda_3 - lambda_2^2 / lambda_1 from raw marked frequencies, decided against the model's f "
                "(raw frequencies carry readout, so the model's f is not zero); resolves at z 3; the readout-"
                "corrected f, zero under lambda_k = A r^k, is reported beside; the depth arms are centrally "
                "grouped, not mirrored"
            ),
            "predicted_lambda": {str(k): round(v, 4) for k, v in lam.items()},
            "predicted": round(lam[3] - lam[2] ** 2 / lam[1], 4),
            "se_at_planned_shots": round(se_f, 4),
            "resolvable_deviation": round(grover.Z_RESOLVE * se_f, 3),
        }
    out["role_or_qubit"] = role_decision(arms)
    for m in ROWS:
        peak = arms[f"s{m}-row-c0"]["row_peak"]
        out[f"sedenion_{m}"] = decision(
            arms,
            f"s{m}-row",
            f"s{m}-trunc",
            peak,
            (
                f"P(row peak) of row minus truncation for e_{m}, two copies each on one CZ list; the most frequent "
                "string of the row arms must be the row peak"
            ),
        )
        null_p, null_n = pooled(arms, f"s{m}-id", peak)
        row_p, row_n = pooled(arms, f"s{m}-row", peak)
        out[f"sedenion_{m}"]["null_floor"] = round(null_p, 4)
        out[f"sedenion_{m}"]["row_minus_null_z"] = round(
            (row_p - null_p) / se_difference(row_p, row_n, null_p, null_n), 2
        )
        out[f"sedenion_{m}"]["rule"] += "; and the row peak exceeds the null arm's P(row peak) by 3 SE"
    return out


def write(directory: Path, source: Path) -> None:
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    for name in CALIBRATION_FILES:
        shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({"square": prediction["square"], "decisions": prediction["decisions"]}, indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration")


def self_test() -> str:
    """Every circuit of both jobs against its exact ideal on placeholder qubits."""
    path = ["QA", "QB", "QC"]
    generic = grover.generic("101", path, "g")
    merged = fused(generic, path, "f")
    if count(merged, "cz") != count(generic, "cz") or count(merged, "prx") >= count(generic, "prx"):
        raise AssertionError(f"fusion gives {count(merged, 'cz')} CZ and {count(merged, 'prx')} prx")
    if [op["locus"] for op in merged["instructions"] if op["name"] == "cz"] != [
        op["locus"] for op in generic["instructions"] if op["name"] == "cz"
    ]:
        raise AssertionError("fusion moved a CZ")
    if float(np.max(np.abs(ideal(merged, path) - ideal(generic, path)))) > 1e-9:
        raise AssertionError("the fused compile's distribution differs from the generic one")
    for marked, k in DEPTHS:
        p = ideal(grover.line_arm(marked, k, path, "t")[1], path)[int(marked[::-1], 2)]
        if abs(p - ideal_probability(k)) > 1e-9:
            raise AssertionError(f"line m{marked}-k{k}: P(marked) {p}")
    line_circuit = grover.line_arm("101", 1, path, "l")[1]
    mapped = generic_mapped("101", path, "m")
    if mapped["instructions"][-1]["locus"] != line_circuit["instructions"][-1]["locus"]:
        raise AssertionError("the mapped generic compile measures another logical-to-physical mapping")
    mapped_fused = fused(mapped, path, "mf")
    if float(np.max(np.abs(ideal(mapped_fused, path) - ideal(line_circuit, path)))) > 1e-9:
        raise AssertionError("the mapped generic compile's distribution differs from the line-native one")
    pad = padded(line_circuit, pad_pairs(line_circuit, mapped_fused, path), "p")
    pad_prx, fused_prx = prx_per_qubit(pad), prx_per_qubit(mapped_fused)
    if count(pad, "prx") != count(mapped_fused, "prx") or any(abs(pad_prx[q] - fused_prx.get(q, 0)) > 1 for q in path):
        raise AssertionError(f"padded line prx per qubit {pad_prx}, fused generic {fused_prx}")
    if count(pad, "cz") != count(line_circuit, "cz"):
        raise AssertionError("the identity pairs change the padded line's CZ list")
    if float(np.max(np.abs(ideal(pad, path) - ideal(line_circuit, path)))) > 1e-9:
        raise AssertionError("the identity pairs change the padded line's distribution")
    reversed_line = grover.line_arm("101", 1, path[::-1], "r")[1]
    forward_line = grover.line_arm("101", 1, path, "f")[1]
    if reversed_line["instructions"][-1]["locus"] == forward_line["instructions"][-1]["locus"]:
        raise AssertionError("the reversed path leaves every logical role on the same qubit")
    square = ["QA", "QB", "QC", "QD"]
    for m in ROWS:
        peaks = {}
        for kind in ("row", "trunc", "id"):
            circuit, want = sedenion_circuit(m, kind, square, "s")
            got = ideal(circuit, square)
            if float(np.max(np.abs(got - want))) > 1e-9:
                raise AssertionError(
                    f"e_{m} {kind}: native distribution differs from the algebra by {np.abs(got - want).max()}"
                )
            if count(circuit, "cz") != 8:
                raise AssertionError(f"e_{m} {kind}: {count(circuit, 'cz')} CZ")
            peaks[kind] = got
        top = int(np.argmax(peaks["row"]))
        if (
            abs(peaks["row"][top] - 9 / 16) > 1e-9
            or abs(peaks["trunc"][top] - 0.25) > 1e-9
            or peaks["id"][0] < 1 - 1e-9
        ):
            raise AssertionError(f"e_{m}: peak {peaks['row'][top]}, truncation {peaks['trunc'][top]}")
        loci = [
            [op["locus"] for op in sedenion_circuit(m, kind, square, "s")[0]["instructions"] if op["name"] == "cz"]
            for kind in ("row", "trunc", "id")
        ]
        if not loci[0] == loci[1] == loci[2]:
            raise AssertionError(f"e_{m}: the row, truncation and identity differ in their CZ sequence")
    return (
        f"iqm_garnet_followup self-test passed: fused generic {count(merged, 'cz')} CZ {count(merged, 'prx')} prx "
        f"(emitted {count(generic, 'prx')}), sedenion rows {ROWS} at 8 CZ"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    b.add_argument("--calibration", type=Path, required=True)
    sub.add_parser("check").add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration)
    elif args.command == "check":
        check(args.directory)
    else:
        parser.error("choose build, check or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
