"""Per-round linear encodings of the N=21 order-finding work register, joined by CNOT transitions.

factor_order_finding(work_columns=B) holds the five-bit work register in the
encoding x = B^-1 v for one B in GL(5,2) across every round. A split encoding
uses B_k in round k. Between rounds k and k+1 the register moves from
x_k = B_k^-1 v to x_(k+1) = B_(k+1)^-1 v through the uncontrolled linear map
T_k = B_(k+1)^-1 B_k, a CNOT network on the work qubits; the operations
between rounds act on the control alone, so the phase register's law is
unchanged. The surrogate cost of a split schedule is
sum_k s(B_k^-1 f_k B_k) + sum_k d(T_k), with s the phase-controlled CX
surrogate of linear_conjugation_search.py (an uncontrolled CX weighs
CONTROLLED_CX_COST[0] = 1) and d the CNOT count of T_k.

Distance. d(M) is the fewest CNOT gates whose product is M, from a
breadth-first search of all 9,999,360 matrices of GL(5,2) over the 20
ordered CNOT generators. A matrix packs into a 25-bit integer, row r in bits
5r to 5r+4 and bit j of row r the entry M[r][j]; CNOT(c -> t) is the row
operation row_t ^= row_c. The table is a 2^25 uint8 array, singular packings
holding 255, and the record keeps its histogram and sha256. Qubit
permutations are free: B_(k+1) and B_(k+1) Q share a coset and an s value,
and choosing Q realizes d_perm(T) = min_P d(P T) = min_P d(T P) with no SWAP
and no relabeling, because a permutation conjugates a CNOT into a CNOT. The
permutation-free table comes from the same search seeded with the 120
permutation matrices. Coset distance is the graph distance on the 83,328
cosets B S_5, whose 20 neighbors replace one column c_a by c_a ^ c_b.

Optimization. Round costs depend on the coset only (s(B^-1 f_16 B) =
s(B^-1 f_4 B) since 16 = 4^-1 mod 21 and the synthesis minimizes over reversed
inverse networks), so a dynamic program over rounds runs on the coset graph:
v_1 = s_(m_1), v_k = s_(m_k) + relax(v_(k-1)) with relax(v)(C) = min_A v(A) +
d(A, C), a multi-source unit-edge distance transform. The first encoding is
a basis-state preparation and the last is never measured, so neither costs a
transition.

Routed admission. Every circuit compiles with the challenger's preset pass
manager (optimization level 3, transpiler seeds 0 to 7) on FakeFez and
FakeKingston, and on the IQM Garnet coupling map retained in
docs/evidence/open_quantum/catalogue.json with the Heron r2 basis (cz, rz,
sx, x) and no error or duration data, so the Garnet comparison isolates the
square-grid coupling and admits on routed CZ and depth. A split wins on a
target only when its median routed CZ is strictly below the best single-B
median on that target over the same seeds, on every arm. Seeds 8 to 15
recompile the best split and the best single-B as a selection-bias check.
The module submits no quantum work.

Usage:
    "$PYTHON" scripts/gl52_split_conjugators.py --out PATH
    "$PYTHON" scripts/gl52_split_conjugators.py --check PATH
    "$PYTHON" scripts/gl52_split_conjugators.py --self-test PATH

--check recomputes the distance tables, the dynamic program, the candidate
lists, the compiler contract and every exact equivalence check, re-derives
every median and verdict from the retained runs (joined by transpiler seed),
requires the holdout section to hold the decisive circuits, both arms and
seeds 8 to 15, and recompiles the unencoded baseline, the best single-B, the
best split and the incumbent of every problem on every target over seeds 0 to
7: routed CZ, qubit counts exact, depth and duration within REPLAY_TOLERANCE.
The decisive verdicts are re-derived from those fresh runs. --self-test runs the
search on GL(3,2) against a brute-force search, checks the permutation-free
identities and the coset-graph distance on seeded samples, and requires
--check to reject corrupted copies of the record.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import re
import statistics
import sys
from functools import cache, lru_cache
from itertools import permutations
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import linear_conjugation_search as lcs  # noqa: E402
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister  # noqa: E402
from qiskit.circuit import IfElseOp, Parameter  # noqa: E402
from qiskit.circuit.library import CZGate, Measure, Reset, RZGate, SXGate, XGate  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402
from qiskit.transpiler import Target, generate_preset_pass_manager  # noqa: E402

import parallel  # noqa: E402
from compile_evidence import MODULUS, OPTIMIZATION_LEVEL, _versions, _write_atomic  # noqa: E402
from linear_conjugation_challenger import (  # noqa: E402
    COMPARED_METRICS,
    PROBLEMS,
    REPLAY_TOLERANCE,
    SAMPLED_SEED,
    SAMPLED_SHOTS,
    SAMPLED_TV_BOUND,
    _baseline_candidate,
    equivalence_checks,
    total_variation,
)
from linear_conjugation_challenger import source as single_source  # noqa: E402
from live_run import _feed_forward_stages, _gate_time_view  # noqa: E402
from modular_arithmetic import (  # noqa: E402
    _append_controlled_target_flips,
    conjugated_permutation,
    linear_encoding,
    modular_permutation,
)
from order_finding import ENCODED_STRATEGY, order_finding_plan  # noqa: E402
from target_flip import target_flip_network  # noqa: E402

SCHEMA = "gl52-split-conjugators-v1"
WIDTH = 5
SIZE = 1 << WIDTH
PACKED_BITS = WIDTH * WIDTH
UNREACHED = 255
GL52_ORDER = 9_999_360
GENERATORS = tuple((control, target) for control in range(WIDTH) for target in range(WIDTH) if control != target)
SEARCH_RECORD = "docs/evidence/linear_conjugation/search.json"
SEARCH_RECORD_SHA256 = "910f86c8f0631fa59e560d49ff479fb4aacce65765bf7b2f2b2b84e0a9058df3"
CATALOGUE = "docs/evidence/open_quantum/catalogue.json"
GARNET = "iqm:garnet"
CATALOGUE_PROVENANCE = ("garnet_catalogue_sha256", "garnet_retrieved_utc")
INCUMBENT_RECORD = "results/hw_estimate/n21_linear_conjugation_challenger.json"
DEFAULT_OUTPUT = ROOT / "docs/evidence/gl52_split_conjugators/split.json"
SEEDS = tuple(range(8))
HOLDOUT_SEEDS = tuple(range(8, 16))
TARGETS = ("fake_fez", "fake_kingston", "iqm_garnet_coupling")
# Single-B controls: the eight cosets the challenger compiled per problem.
CHALLENGER_COSETS = 8
# Two-round: ordered pairs (X, Y), X != Y, drawn from every coset whose s4 is
# at most TWO_ROUND_POOL_S4, ranked by s4(X) + s4(Y) + d(X, Y).
TWO_ROUND_POOL_S4 = 192
TWO_ROUND_SPLITS = 16
# Ten-round: for each challenger coset X on rounds 1 to 9, the
# TEN_ROUND_PER_X cosets Y != X of least s2(Y) + d(X, Y) on round 10.
TEN_ROUND_PER_X = 2
SAMPLE_SEED = 20261017
SAMPLE_PAIRS = 64
RUN_FIELDS = (
    "seed_transpiler",
    "logical_qubits",
    "active_physical_qubits",
    "routed_cz",
    "depth",
    "duration_dt",
    "if_else",
    "classical_stages",
    "classical_sha256_16",
    "final_layout",
)
# A replay on another host holds routed CZ, layout and classical stages
# exactly; depth and duration follow BLAS rounding (REPLAY_TOLERANCE).
EXACT_FIELDS = (
    "seed_transpiler",
    "logical_qubits",
    "active_physical_qubits",
    "routed_cz",
    "if_else",
    "classical_stages",
    "classical_sha256_16",
    "final_layout",
)


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"gl52_split_conjugators: {message}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- distances


def pack_columns(columns: tuple[int, ...] | list[int], width: int = WIDTH) -> int:
    """The packed matrix whose column j is columns[j] (bit r of a column is row r)."""
    packed = 0
    for row in range(width):
        bits = sum(((column >> row) & 1) << j for j, column in enumerate(columns))
        packed |= bits << (width * row)
    return packed


def permutation_matrices(width: int = WIDTH) -> list[int]:
    return [pack_columns([1 << image for image in order], width) for order in permutations(range(width))]


def cnot_bfs(sources: list[int], width: int = WIDTH) -> np.ndarray:
    """Fewest CNOT row operations from any source to every packed matrix; UNREACHED marks singular packings."""
    mask = (1 << width) - 1
    generators = [(c, t) for c in range(width) for t in range(width) if c != t]
    distance = np.full(1 << (width * width), UNREACHED, dtype=np.uint8)
    frontier = np.asarray(sources, dtype=np.int64)
    distance[frontier] = 0
    level = 0
    while frontier.size:
        for control, target in generators:
            image = frontier ^ (((frontier >> (width * control)) & mask) << (width * target))
            image = image[distance[image] == UNREACHED]
            distance[image] = level + 1
        level += 1
        frontier = np.flatnonzero(distance == level)
    return distance


@lru_cache(maxsize=1)
def identity_table() -> np.ndarray:
    return cnot_bfs([pack_columns([1 << j for j in range(WIDTH)])])


@lru_cache(maxsize=1)
def permutation_free_table() -> np.ndarray:
    return cnot_bfs(permutation_matrices())


def distance_tables() -> tuple[np.ndarray, np.ndarray]:
    """(d, d_perm) over every packed 5x5 matrix."""
    return identity_table(), permutation_free_table()


def table_summary(table: np.ndarray) -> dict[str, Any]:
    reached = table[table != UNREACHED]
    counts = np.bincount(reached)
    return {
        "reached": int(reached.size),
        "maximum": int(counts.size - 1),
        "histogram": {str(level): int(count) for level, count in enumerate(counts)},
        "table_sha256": hashlib.sha256(table.tobytes()).hexdigest(),
    }


def cnot_word(packed: int) -> list[tuple[int, int]]:
    """A shortest CNOT circuit (control, target) for the packed matrix, in application order."""
    table = identity_table()
    _require(table[packed] != UNREACHED, f"packed matrix {packed:#x} is singular")
    peeled = []
    while table[packed]:
        for control, target in GENERATORS:
            image = packed ^ (((packed >> (WIDTH * control)) & (SIZE - 1)) << (WIDTH * target))
            if table[image] == table[packed] - 1:
                peeled.append((control, target))
                packed = image
                break
    return peeled[::-1]


def transition_columns(previous: tuple[int, ...], following: tuple[int, ...]) -> tuple[int, ...]:
    """Columns of T = B_next^-1 B_prev, the map x_prev -> x_next."""
    inverse = [0] * SIZE
    for value, image in enumerate(linear_encoding(following)):
        inverse[image] = value
    return tuple(inverse[column] for column in previous)


def best_representative(previous: tuple[int, ...], coset: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    """The column order of coset with the shortest transition from previous (first order on ties), and its d."""
    table = identity_table()
    best: tuple[int, tuple[int, ...]] | None = None
    for order in permutations(range(WIDTH)):
        columns = tuple(coset[position] for position in order)
        cost = int(table[pack_columns(transition_columns(previous, columns))])
        if best is None or cost < best[0]:
            best = (cost, columns)
    if best is None:
        raise SystemExit("gl52_split_conjugators: no column order")
    return best[1], best[0]


# ------------------------------------------------------------ coset graph


@lru_cache(maxsize=1)
def surrogate_arrays() -> tuple[np.ndarray, np.ndarray]:
    path = ROOT / SEARCH_RECORD
    _require(_sha256(path) == SEARCH_RECORD_SHA256, f"{SEARCH_RECORD} differs from its bound sha256")
    record = json.loads(path.read_text(encoding="utf-8"))
    return np.asarray(record["s4"], dtype=np.int64), np.asarray(record["s2"], dtype=np.int64)


@lru_cache(maxsize=1)
def coset_array() -> np.ndarray:
    return np.asarray(lcs.coset_columns(), dtype=np.int64)


@lru_cache(maxsize=1)
def coset_graph() -> np.ndarray:
    """(cosets, 20) neighbor indices: column a replaced by column a ^ column b."""
    columns = coset_array()
    keys = np.bitwise_or.reduce(np.left_shift(1, columns), axis=1)
    order = np.argsort(keys)
    sorted_keys = keys[order]
    neighbors = []
    for a in range(WIDTH):
        for b in range(WIDTH):
            if a == b:
                continue
            replaced = columns[:, a] ^ columns[:, b]
            moved = keys ^ np.left_shift(1, columns[:, a]) ^ np.left_shift(1, replaced)
            position = np.searchsorted(sorted_keys, moved)
            _require(bool(np.all(sorted_keys[position] == moved)), "a neighbor column set is not a coset")
            neighbors.append(order[position])
    return np.stack(neighbors, axis=1)


def relax(values: np.ndarray) -> np.ndarray:
    """min over A of values[A] + coset distance(A, C), for every C."""
    graph = coset_graph()
    current = values.copy()
    while True:
        updated = np.minimum(current, current[graph].min(axis=1) + 1)
        if np.array_equal(updated, current):
            return current
        current = updated


def coset_distances_from(index: int) -> np.ndarray:
    start = np.full(len(coset_array()), 1 << 20, dtype=np.int64)
    start[index] = 0
    return relax(start)


@lru_cache(maxsize=1)
def coset_inverses() -> np.ndarray:
    """(cosets, 32): row Y holds B_Y^-1 v for every register value v."""
    columns = coset_array()
    values = np.arange(SIZE)
    tables = np.zeros((len(columns), SIZE), dtype=np.int64)
    for j in range(WIDTH):
        tables ^= np.where((values >> j) & 1, columns[:, j : j + 1], 0)
    inverse = np.zeros_like(tables)
    np.put_along_axis(inverse, tables, np.broadcast_to(values, tables.shape), axis=1)
    return inverse


def pair_distances(x: int, ys: np.ndarray) -> np.ndarray:
    """d_perm(B_Y^-1 B_X) for one coset X against many Y, by table lookup."""
    d_perm = permutation_free_table()
    images = coset_inverses()[ys][:, list(coset_array()[x])]
    packed = np.zeros(len(ys), dtype=np.int64)
    for row in range(WIDTH):
        for j in range(WIDTH):
            packed |= ((images[:, j] >> row) & 1) << (WIDTH * row + j)
    return d_perm[packed].astype(np.int64)


def distances_from(x: int) -> np.ndarray:
    """d_perm from coset x to every coset, as uint8; one pool item per coset."""
    return pair_distances(x, np.arange(len(coset_array()))).astype(np.uint8)


def distance_rows(xs: list[int]) -> list[np.ndarray]:
    """distances_from for each x, over the process pool; each worker builds the shared tables once."""
    return [row.astype(np.int64) for row in parallel.ordered_map(distances_from, [int(x) for x in xs], min_items=2)]


def round_costs(problem: str) -> list[np.ndarray]:
    s4, s2 = surrogate_arrays()
    by_multiplier = {4: s4, 16: s4, 2: s2}
    return [by_multiplier[multiplier] for multiplier in schedule(problem)]


@cache
def schedule(problem: str) -> tuple[int, ...]:
    base, phase_bits, _, _ = PROBLEMS[problem]
    plan = order_finding_plan(MODULUS, base, phase_bits, multiplier_strategy=ENCODED_STRATEGY)
    return tuple(resource.multiplier for resource in plan.rounds[plan.leading_identity_rounds :])


def split_program(problem: str) -> dict[str, Any]:
    """Exact optimum over every per-round coset sequence, its path, and the single-B optimum."""
    costs = round_costs(problem)
    values = costs[0].copy()
    history = [(values, values)]
    for cost in costs[1:]:
        relaxed = relax(values)
        history.append((values, relaxed))
        values = cost + relaxed
    single = np.sum(np.stack(costs), axis=0)
    final = int(np.argmin(values))
    path = [final]
    transitions = []
    graph = coset_graph()
    current = final
    for previous_values, relaxed in reversed(history[1:]):
        steps = 0
        while relaxed[current] != previous_values[current]:
            current = int(min(n for n in graph[current] if relaxed[n] == relaxed[current] - 1))
            steps += 1
        transitions.append(steps)
        path.append(current)
    path.reverse()
    transitions.reverse()
    total = sum(int(cost[coset]) for cost, coset in zip(costs, path, strict=True)) + sum(transitions)
    _require(total == int(values[final]), f"{problem}: backtracked path costs {total}, optimum {int(values[final])}")
    return {
        "round_multipliers": list(schedule(problem)),
        "single_b_optimum": int(single.min()),
        "single_b_optimal_cosets": [int(index) for index in np.flatnonzero(single == single.min())],
        "split_optimum": int(values[final]),
        "split_path": path,
        "split_transition_distances": transitions,
        "gain": int(single.min()) - int(values[final]),
    }


def ten_round_enumeration() -> dict[str, Any]:
    """min over X with 9 s4(X) + min s2 below the single-B optimum, and every Y, of 9 s4(X) + d(X, Y) + s2(Y)."""
    s4, s2 = surrogate_arrays()
    nine = sum(multiplier != 2 for multiplier in schedule("ten_round"))
    single = int((nine * s4 + s2).min())
    xs = np.flatnonzero(nine * s4 + int(s2.min()) < single)
    best = None
    for x, distances in zip(xs, distance_rows([int(x) for x in xs]), strict=True):
        totals = nine * int(s4[x]) + s2 + distances
        y = int(np.argmin(totals))
        if best is None or int(totals[y]) < best[0]:
            best = (int(totals[y]), int(x), y)
    if best is None:
        raise SystemExit("gl52_split_conjugators: no rounds-one-to-nine coset beats the single-B optimum")
    return {"rounds_one_to_nine_cosets": [int(x) for x in xs], "optimum": best[0], "x": best[1], "y": best[2]}


def ten_round_per_x(xs: list[int]) -> list[dict[str, Any]]:
    s4, s2 = surrogate_arrays()
    rows = []
    for x, distances in zip(xs, distance_rows(xs), strict=True):
        totals = s2 + distances
        totals[x] = 1 << 30
        # A stable sort orders ties by coset index.
        ranked = [int(y) for y in np.argsort(totals, kind="stable")[:TEN_ROUND_PER_X]]
        rows.append(
            {
                "x": x,
                "s4": int(s4[x]),
                "s2": int(s2[x]),
                "round_ten": [
                    {
                        "y": y,
                        "s2": int(s2[y]),
                        "distance": int(distances[y]),
                        "gain": int(s2[x]) - int(s2[y]) - int(distances[y]),
                    }
                    for y in ranked
                ],
            }
        )
    return rows


# --------------------------------------------------------------- candidates


def search_summary() -> dict[str, Any]:
    surrogate_arrays()
    summary: dict[str, Any] = json.loads((ROOT / SEARCH_RECORD).read_text(encoding="utf-8"))["summary"]
    return summary


def incumbent_cosets() -> dict[str, int]:
    """The challenger's best admitted coset per problem, the single-B circuit a hardware case carries."""
    record = json.loads((ROOT / INCUMBENT_RECORD).read_text(encoding="utf-8"))
    return {problem: int(entry["best_admitted"]) for problem, entry in record["problems"].items()}


def single_b_cosets(problem: str) -> list[int]:
    ranking = PROBLEMS[problem][3]
    cosets = [int(winner["index"]) for winner in search_summary()[ranking][:CHALLENGER_COSETS]]
    if problem == "two_round":
        s4 = surrogate_arrays()[0]
        cosets += [int(index) for index in np.flatnonzero(s4 <= TWO_ROUND_POOL_S4) if int(index) not in cosets]
    return cosets


def make_split(problem: str, x: int, y: int, switch: int) -> dict[str, Any]:
    """Coset x on rounds before switch and y from switch on, y in its shortest-transition column order."""
    columns = lcs.coset_columns()
    first = tuple(columns[x])
    second, distance = best_representative(first, tuple(columns[y]))
    word = cnot_word(pack_columns(transition_columns(first, second)))
    _require(len(word) == distance, f"split {x}->{y}: word of {len(word)} CNOTs for distance {distance}")
    costs = round_costs(problem)
    surrogate = sum(int(cost[x if k < switch else y]) for k, cost in enumerate(costs)) + distance
    return {
        "name": f"split_{x}_{y}",
        "segments": [
            {"rounds": [0, switch], "coset": x, "columns": list(first)},
            {"rounds": [switch, len(costs)], "coset": y, "columns": list(second)},
        ],
        "transitions": [{"after_round": switch - 1, "distance": distance, "cnots": [list(gate) for gate in word]}],
        "surrogate": surrogate,
    }


def make_split_job(job: tuple[str, int, int, int]) -> dict[str, Any]:
    return make_split(*job)


def split_candidates(problem: str) -> list[dict[str, Any]]:
    if problem == "two_round":
        s4 = surrogate_arrays()[0]
        pool = [int(index) for index in np.flatnonzero(s4 <= TWO_ROUND_POOL_S4)]
        pairs = []
        for x, distances in zip(pool, distance_rows(pool), strict=True):
            pairs += [(int(s4[x]) + int(s4[y]) + int(distances[y]), x, y) for y in pool if y != x]
        jobs = [(problem, x, y, 1) for _, x, y in sorted(pairs)[:TWO_ROUND_SPLITS]]
    else:
        switch = len(schedule(problem)) - 1
        jobs = [
            (problem, row["x"], entry["y"], switch)
            for row in ten_round_per_x(single_b_cosets(problem))
            for entry in row["round_ten"]
        ]
    return parallel.ordered_map(make_split_job, jobs, min_items=2)


def single_candidate(index: int) -> dict[str, Any]:
    return {"name": f"coset_{index}", "coset": index, "columns": list(lcs.coset_columns()[index])}


def round_columns(problem: str, candidate: dict[str, Any] | None) -> tuple[tuple[int, ...], ...] | None:
    if candidate is None:
        return None
    rounds = len(schedule(problem))
    if "segments" not in candidate:
        return (tuple(candidate["columns"]),) * rounds
    per_round: list[tuple[int, ...]] = []
    for segment in candidate["segments"]:
        start, stop = segment["rounds"]
        per_round += [tuple(segment["columns"])] * (stop - start)
    _require(len(per_round) == rounds, f"{candidate['name']} covers {len(per_round)} of {rounds} rounds")
    return tuple(per_round)


# ----------------------------------------------------------------- circuits


def append_transition(
    circuit: QuantumCircuit, work: list[int], previous: tuple[int, ...], following: tuple[int, ...]
) -> None:
    for control, target in cnot_word(pack_columns(transition_columns(previous, following))):
        circuit.cx(work[control], work[target])


def build_split(problem: str, per_round: tuple[tuple[int, ...], ...], feed_forward: bool) -> QuantumCircuit:
    """factor_order_finding with round k's network conjugated by per_round[k], CNOT transitions between encodings."""
    base, phase_bits, _, _ = PROBLEMS[problem]
    plan = order_finding_plan(MODULUS, base, phase_bits, multiplier_strategy=ENCODED_STRATEGY)
    rounds = plan.rounds[plan.leading_identity_rounds :]
    _require(len(per_round) == len(rounds) and plan.scratch_qubits == 1, "the split needs one encoding per round")
    phase_register = ClassicalRegister(plan.phase_bits, "phase")
    circuit = QuantumCircuit(
        QuantumRegister(1, "ctrl"),
        QuantumRegister(plan.work_qubits, "w"),
        QuantumRegister(plan.scratch_qubits, "scratch"),
        phase_register,
    )
    circuit.name = f"shor_order_N{MODULUS}_a{base % MODULUS}"
    work = list(range(1, 1 + plan.work_qubits))
    scratch = list(range(1 + plan.work_qubits, plan.quantum_qubits))
    initial = linear_encoding(per_round[0]).index(1)
    for bit, qubit in enumerate(work):
        if initial >> bit & 1:
            circuit.x(qubit)
    for position, resource in enumerate(rounds):
        columns = per_round[position]
        circuit.h(0)
        permutation = conjugated_permutation(modular_permutation(MODULUS, resource.multiplier), columns)
        _append_controlled_target_flips(circuit, 0, work, scratch, target_flip_network(permutation))
        if position + 1 < len(rounds) and per_round[position + 1] != columns:
            append_transition(circuit, work, columns, per_round[position + 1])
        if feed_forward:
            for prior_round in range(plan.leading_identity_rounds, resource.round_index):
                angle = -math.pi / (1 << (resource.round_index - prior_round))
                with circuit.if_test((phase_register[prior_round], 1)):
                    circuit.p(angle, 0)
        circuit.h(0)
        circuit.measure(0, phase_register[resource.round_index])
        if resource.round_index + 1 < plan.phase_bits:
            circuit.reset(0)
    return circuit


def source(problem: str, candidate: dict[str, Any] | None, feed_forward: bool) -> QuantumCircuit:
    """The unencoded circuit, the challenger's single-B circuit, or the split circuit."""
    if candidate is None or "segments" not in candidate:
        return single_source(problem, None if candidate is None else tuple(candidate["columns"]), feed_forward)
    per_round = round_columns(problem, candidate)
    if per_round is None:
        raise SystemExit("gl52_split_conjugators: a split names no rounds")
    return build_split(problem, per_round, feed_forward)


def builder_matches_reference(job: tuple[str, int, bool]) -> bool:
    """With one encoding in every round the split builder emits factor_order_finding(work_columns=B)."""
    problem, index, feed_forward = job
    columns = tuple(lcs.coset_columns()[index])
    reference = single_source(problem, columns, feed_forward)
    built = build_split(problem, (columns,) * len(schedule(problem)), feed_forward)
    return bool(reference == built and reference.name == built.name and reference.count_ops() == built.count_ops())


# ------------------------------------------------------------------ routing


def garnet_coupling() -> tuple[int, list[list[int]], str]:
    catalogue = json.loads((ROOT / CATALOGUE).read_text(encoding="utf-8"))
    entries = [entry for entry in catalogue["backend_classes"] if entry["short_code"] == GARNET]
    _require(len(entries) == 1, f"{CATALOGUE} lists {len(entries)} {GARNET} entries")
    data = entries[0]["constraint_data"]
    _require(not data["topology"]["directed_edges"], f"{GARNET} lists directed edges")
    return int(data["n_qubits"]), [list(edge) for edge in data["topology"]["coupling_map"]], catalogue["retrieved_utc"]


@cache
def compile_target(name: str) -> Any:
    """(pass-manager keyword, Target or backend, whether the target carries durations)."""
    if name == "fake_fez":
        from qiskit_ibm_runtime.fake_provider import FakeFez

        return FakeFez()
    if name == "fake_kingston":
        from qiskit_ibm_runtime.fake_provider import FakeKingston

        return FakeKingston()
    _require(name == "iqm_garnet_coupling", f"unknown target {name}")
    qubits, edges, _ = garnet_coupling()
    target = Target(num_qubits=qubits)
    target.add_instruction(CZGate(), {(a, b): None for edge in edges for a, b in (edge, edge[::-1])})
    every = {(qubit,): None for qubit in range(qubits)}
    target.add_instruction(RZGate(Parameter("theta")), every)
    for gate in (SXGate(), XGate(), Measure(), Reset()):
        target.add_instruction(gate, dict(every))
    target.add_instruction(IfElseOp, name="if_else")
    return target


def _active_physical_qubits(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits})


def classical_digest(circuit: QuantumCircuit) -> str:
    """First 16 hex of the sha256 of every measure, reset and if_else site in order.

    Each site carries its physical qubits and clbits; an if_else adds its
    condition and the gates of each block with their parameters.
    """
    sites: list[Any] = []
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name not in ("measure", "reset", "if_else"):
            continue
        site: list[Any] = [
            operation.name,
            [circuit.find_bit(qubit).index for qubit in instruction.qubits],
            [circuit.find_bit(clbit).index for clbit in instruction.clbits],
        ]
        if isinstance(operation, IfElseOp):
            clbit, value = operation.condition
            site.append([circuit.find_bit(clbit).index, int(value)])
            site.append(
                [
                    [
                        [inner.operation.name, [repr(float(param)) for param in inner.operation.params]]
                        for inner in block.data
                    ]
                    for block in operation.blocks
                ]
            )
        sites.append(site)
    return hashlib.sha256(json.dumps(sites, separators=(",", ":")).encode()).hexdigest()[:16]


def compile_job(job: tuple[str, str, dict[str, Any] | None, bool, int]) -> list[Any]:
    """One arm of one circuit at one transpiler seed, as a RUN_FIELDS row."""
    target_name, problem, candidate, feed_forward, seed = job
    circuit = source(problem, candidate, feed_forward)
    backend = compile_target(target_name)
    _require(_baseline_candidate().mcx_hls_method is None, "the challenger pass manager gained an HLS config")
    if isinstance(backend, Target):
        manager = generate_preset_pass_manager(
            optimization_level=OPTIMIZATION_LEVEL, target=backend, seed_transpiler=seed
        )
        duration = None
    else:
        manager = generate_preset_pass_manager(
            optimization_level=OPTIMIZATION_LEVEL, backend=backend, seed_transpiler=seed
        )
    compiled = manager.run(circuit)
    if not isinstance(backend, Target):
        duration = int(_gate_time_view(compiled).estimate_duration(backend.target, unit="dt"))
    _require(compiled.layout is not None, f"{target_name} {problem} seed {seed}: the transpiler set no layout")
    return [
        seed,
        circuit.num_qubits,
        _active_physical_qubits(compiled),
        int(compiled.count_ops().get("cz", 0)),
        compiled.depth(),
        duration,
        int(compiled.count_ops().get("if_else", 0)),
        _feed_forward_stages(compiled),
        classical_digest(compiled),
        list(compiled.layout.final_index_layout(filter_ancillas=True)),
    ]


def arms(problem: str) -> tuple[bool, ...]:
    return tuple(PROBLEMS[problem][2])


def arm_name(feed_forward: bool) -> str:
    return "feed_forward" if feed_forward else "no_feed_forward"


def metrics(target_name: str) -> tuple[str, ...]:
    return COMPARED_METRICS if target_name != "iqm_garnet_coupling" else ("routed_cz", "depth")


def run_value(run: list[Any], metric: str) -> Any:
    return run[RUN_FIELDS.index("duration_dt" if metric == "scheduled_duration_dt" else metric)]


def medians(runs: list[list[Any]], target_name: str) -> dict[str, float]:
    return {metric: statistics.median(run_value(run, metric) for run in runs) for metric in metrics(target_name)}


def summed_median_cz(entry: dict[str, Any]) -> float:
    return float(sum(arm["medians"]["routed_cz"] for arm in entry["arms"].values()))


def judge(target_name: str, problem: str, block: dict[str, Any]) -> dict[str, Any]:
    """Every median, admission and verdict of one target and problem, derived from the retained runs."""
    for entry in [block["baseline"], *block["single_b"], *block["split"]]:
        for arm in entry["arms"].values():
            arm["medians"] = medians(arm["runs"], target_name)
    baseline = block["baseline"]
    labels = {arm_name(ff) for ff in arms(problem)}
    for entry in [baseline, *block["single_b"], *block["split"]]:
        _require(set(entry["arms"]) == labels, f"{target_name} {problem} {entry['name']}: arms {sorted(entry['arms'])}")
        for label, arm in entry["arms"].items():
            seeds = [run[0] for run in arm["runs"]]
            _require(
                seeds == list(SEEDS), f"{target_name} {problem} {entry['name']} {label}: seeds {seeds}, not {SEEDS}"
            )
    baseline_runs = {label: {run[0]: run for run in arm["runs"]} for label, arm in baseline["arms"].items()}

    def admitted(entry: dict[str, Any]) -> dict[str, Any]:
        regressions = [
            [arm_label, run[0], metric]
            for arm_label, arm in entry["arms"].items()
            for run in arm["runs"]
            for metric in metrics(target_name)
            if run_value(run, metric) > run_value(baseline_runs[arm_label][run[0]], metric)
        ]
        lower = all(
            arm["medians"]["routed_cz"] < baseline["arms"][label]["medians"]["routed_cz"]
            for label, arm in entry["arms"].items()
        )
        return {"per_seed_regressions": regressions, "admitted": bool(lower and not regressions)}

    for entry in [*block["single_b"], *block["split"]]:
        entry["admission"] = admitted(entry)
    best_single = min(block["single_b"], key=lambda entry: (summed_median_cz(entry), entry["name"]))
    best_split = min(block["split"], key=lambda entry: (summed_median_cz(entry), entry["name"]))
    for entry in block["split"]:
        entry["beats_best_single_b"] = all(
            arm["medians"]["routed_cz"] < best_single["arms"][label]["medians"]["routed_cz"]
            for label, arm in entry["arms"].items()
        )
    block["best_single_b"] = best_single["name"]
    block["best_split"] = best_split["name"]
    block["best_split_minus_best_single_b_median_cz"] = summed_median_cz(best_split) - summed_median_cz(best_single)
    block["splits_beating_best_single_b"] = [entry["name"] for entry in block["split"] if entry["beats_best_single_b"]]
    return block


def phase_counts(job: tuple[str, dict[str, Any] | None, bool]) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(method="statevector")
    circuit = transpile(source(*job), simulator, optimization_level=0)
    counts = simulator.run(circuit, shots=SAMPLED_SHOTS, seed_simulator=SAMPLED_SEED).result().get_counts()
    return dict(sorted(counts.items()))


def transition_maps(job: tuple[tuple[int, ...], tuple[int, ...]]) -> bool:
    """The emitted CNOT network sends |x> to |B_next^-1 B_prev x> on all 32 values."""
    previous, following = job
    circuit = QuantumCircuit(WIDTH)
    append_transition(circuit, list(range(WIDTH)), previous, following)
    matrix = Operator(circuit).data
    expected = linear_encoding(transition_columns(previous, following))
    return all(abs(matrix[expected[value], value] - 1) < 1e-12 for value in range(SIZE))


def segment_check(job: tuple[str, tuple[int, ...]]) -> dict[str, Any]:
    """The challenger's exact conjugation and controlled-network checks with the surrogate of that column order."""
    problem, columns = job
    entry = equivalence_checks((problem, columns))
    return {
        "pass": bool(entry["pass"]),
        "cx_surrogate": {key: value["cx_surrogate"] for key, value in entry.items() if key.isdigit()},
    }


def exact_checks(problem: str, splits: list[dict[str, Any]]) -> dict[str, Any]:
    s4, s2 = surrogate_arrays()
    retained = {4: s4, 16: s4, 2: s2}
    segments = sorted({tuple(segment["columns"]) for split in splits for segment in split["segments"]})
    results = dict(
        zip(segments, parallel.ordered_map(segment_check, [(problem, c) for c in segments], min_items=2), strict=True)
    )
    pairs = [(tuple(s["segments"][0]["columns"]), tuple(s["segments"][1]["columns"])) for s in splits]
    transitions = parallel.ordered_map(transition_maps, pairs, min_items=2)
    builder = parallel.ordered_map(
        builder_matches_reference,
        [(problem, index, feed_forward) for index in single_b_cosets(problem)[:2] for feed_forward in arms(problem)],
        min_items=2,
    )
    rows = {}
    for split, transition in zip(splits, transitions, strict=True):
        surrogate_matches = all(
            int(results[tuple(segment["columns"])]["cx_surrogate"][str(multiplier)])
            == int(retained[multiplier][segment["coset"]])
            for segment in split["segments"]
            for multiplier in set(schedule(problem)[segment["rounds"][0] : segment["rounds"][1]])
        )
        rows[split["name"]] = {
            "segments_exact": all(results[tuple(segment["columns"])]["pass"] for segment in split["segments"]),
            "segment_surrogate_matches_search_record": surrogate_matches,
            "transition_exact": transition,
        }
    return {"single_encoding_builder_matches_factor_order_finding": all(builder), "splits": rows}


@cache
def _recomputed_exact_checks(problem: str) -> dict[str, Any]:
    return exact_checks(problem, split_candidates(problem))


def recomputed_exact_checks(problem: str) -> dict[str, Any]:
    """exact_checks over the recomputed split candidates, which check_derived requires the record to list."""
    return copy.deepcopy(_recomputed_exact_checks(problem))


def sampled_checks(problem: str, splits: list[dict[str, Any]]) -> dict[str, float]:
    jobs = [(problem, candidate, feed_forward) for candidate in [None, *splits] for feed_forward in arms(problem)]
    counts = parallel.ordered_map(phase_counts, jobs, min_items=2)
    width = len(arms(problem))
    return {
        split["name"]: max(total_variation(counts[arm], counts[width * (position + 1) + arm]) for arm in range(width))
        for position, split in enumerate(splits)
    }


def routed_block(
    target_name: str, problem: str, singles: list[dict[str, Any]], splits: list[dict[str, Any]], seeds: tuple[int, ...]
) -> dict[str, Any]:
    circuits: list[tuple[str, dict[str, Any] | None]] = [("unencoded", None)]
    circuits += [(entry["name"], entry) for entry in singles + splits]
    jobs = [
        (target_name, problem, candidate, ff, seed)
        for _, candidate in circuits
        for ff in arms(problem)
        for seed in seeds
    ]
    runs = iter(parallel.ordered_map(compile_job, jobs, min_items=2))
    entries = []
    for name, _ in circuits:
        entries.append(
            {"name": name, "arms": {arm_name(ff): {"runs": [next(runs) for _ in seeds]} for ff in arms(problem)}}
        )
    block = {"baseline": entries[0], "single_b": entries[1 : 1 + len(singles)], "split": entries[1 + len(singles) :]}
    return judge(target_name, problem, block)


def surrogate_section() -> dict[str, Any]:
    return {
        "two_round": split_program("two_round"),
        "ten_round": split_program("ten_round"),
        "ten_round_enumeration": ten_round_enumeration(),
        "ten_round_per_x": ten_round_per_x(single_b_cosets("ten_round")),
    }


def static_record() -> dict[str, Any]:
    """Every field that follows from the retained inputs without compiling."""
    return copy.deepcopy(_static_record())


@lru_cache(maxsize=1)
def _static_record() -> dict[str, Any]:
    identity, free = distance_tables()
    qubits, edges, retrieved = garnet_coupling()
    candidates = {
        problem: {
            "single_b": [single_candidate(index) for index in single_b_cosets(problem)],
            "split": split_candidates(problem),
        }
        for problem in PROBLEMS
    }
    return {
        "schema": SCHEMA,
        "capture": "gl52-split-conjugators",
        "qpu_executed": False,
        "inputs": {
            "search_record": SEARCH_RECORD,
            "search_record_sha256": SEARCH_RECORD_SHA256,
            "garnet_catalogue": CATALOGUE,
            "garnet_catalogue_sha256": _sha256(ROOT / CATALOGUE),
            "garnet_retrieved_utc": retrieved,
            "garnet_qubits": qubits,
            "garnet_coupling": edges,
            "incumbent_record": INCUMBENT_RECORD,
            "incumbent": incumbent_cosets(),
        },
        "distance": {
            "packing": "row r in bits 5r..5r+4, bit j of row r is M[r][j]; CNOT(c->t) is row_t ^= row_c",
            "unreached_fill": UNREACHED,
            "table_entries": 1 << PACKED_BITS,
            "identity_source": table_summary(identity),
            "permutation_free": table_summary(free),
        },
        "surrogate": surrogate_section(),
        "candidates": candidates,
    }


def capture() -> dict[str, Any]:
    record = static_record()
    record["checks"] = {}
    for problem, entry in record["candidates"].items():
        record["checks"][problem] = exact_checks(problem, entry["split"])
        record["checks"][problem]["sampled_phase_total_variation"] = sampled_checks(problem, entry["split"])
    record["compiler"] = compiler_section()
    record["routed"] = {
        target_name: {
            problem: routed_block(target_name, problem, entry["single_b"], entry["split"], SEEDS)
            for problem, entry in record["candidates"].items()
        }
        for target_name in TARGETS
    }
    record["holdout"] = holdout(record)
    return record


def compiler_section() -> dict[str, Any]:
    """The compile contract: pass-manager level and description, seeds, targets, run-field schema, versions."""
    return {
        "optimization_level": OPTIMIZATION_LEVEL,
        "pass_manager": "generate_preset_pass_manager, no HLS config, as candidate_pass_manager(target_flip_one_clean)",
        "seeds": list(SEEDS),
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "targets": {
            "fake_fez": "qiskit_ibm_runtime.fake_provider.FakeFez (Heron r2)",
            "fake_kingston": "qiskit_ibm_runtime.fake_provider.FakeKingston (Heron r2)",
            "iqm_garnet_coupling": (
                f"{GARNET} coupling from {CATALOGUE}; cz both directions, rz, sx, x, measure, reset, "
                "if_else; no errors or durations"
            ),
        },
        "run_fields": list(RUN_FIELDS),
        "versions": _versions(),
    }


def by_name(record: dict[str, Any], problem: str, name: str) -> dict[str, Any] | None:
    for entry in [*record["candidates"][problem]["single_b"], *record["candidates"][problem]["split"]]:
        if entry["name"] == name:
            return entry
    return None


def decisive_names(record: dict[str, Any], problem: str, block: dict[str, Any]) -> list[str]:
    """The best single-B and best split on seeds 0 to 7, and the challenger's admitted coset."""
    incumbent = f"coset_{record['inputs']['incumbent'][problem]}"
    return list(dict.fromkeys((block["best_single_b"], block["best_split"], incumbent)))


def holdout(record: dict[str, Any]) -> dict[str, Any]:
    """Seeds 8 to 15 for the decisive circuits chosen on seeds 0 to 7."""
    result: dict[str, Any] = {}
    for target_name, problems in record["routed"].items():
        result[target_name] = {}
        for problem, block in problems.items():
            names = decisive_names(record, problem, block)
            jobs = [
                (target_name, problem, by_name(record, problem, name), ff, seed)
                for name in names
                for ff in arms(problem)
                for seed in HOLDOUT_SEEDS
            ]
            runs = iter(parallel.ordered_map(compile_job, jobs, min_items=2))
            entries = {}
            for name in names:
                arm_runs = {arm_name(ff): [next(runs) for _ in HOLDOUT_SEEDS] for ff in arms(problem)}
                entries[name] = {
                    label: {"runs": rows, "median_routed_cz": statistics.median(r[3] for r in rows)}
                    for label, rows in arm_runs.items()
                }
            result[target_name][problem] = entries
    return result


# -------------------------------------------------------------------- check


def replay_matches(recompiled: list[Any], retained: list[Any]) -> float | None:
    if any(recompiled[RUN_FIELDS.index(field)] != retained[RUN_FIELDS.index(field)] for field in EXACT_FIELDS):
        return None
    deviations = [0.0]
    for field in ("depth", "duration_dt"):
        index = RUN_FIELDS.index(field)
        if retained[index] is None or recompiled[index] is None:
            if retained[index] != recompiled[index]:
                return None
            continue
        deviations.append(abs(recompiled[index] - retained[index]) / retained[index])
    return max(deviations)


def check_derived(record: dict[str, Any], recompute_exact: bool = True) -> None:
    """Static fields recomputed, and every median and verdict re-derived from the retained runs.

    recompute_exact reruns every exact equivalence check; without it the retained checks must all pass.
    """
    _require(record.get("schema") == SCHEMA and record.get("qpu_executed") is False, "not a split-conjugator record")
    expected = static_record()
    for key, value in expected.items():
        retained = record.get(key)
        if key == "inputs" and isinstance(retained, dict):
            # A catalogue refresh rewrites its timestamp, status and queue fields; the
            # routed numbers depend only on Garnet's qubit count and coupling.
            retained = {name: field for name, field in retained.items() if name not in CATALOGUE_PROVENANCE}
            value = {name: field for name, field in value.items() if name not in CATALOGUE_PROVENANCE}
        _require(retained == value, f"retained {key} differs from the recomputed {key}")
    _require(record.get("compiler") == compiler_section(), "retained compiler differs from the recomputed compiler")
    _require(expected["distance"]["identity_source"]["reached"] == GL52_ORDER, "the search misses GL(5,2) matrices")
    _require(set(record["checks"]) == set(PROBLEMS), f"checks cover {sorted(record['checks'])}")
    for section in ("routed", "holdout"):
        _require(set(record[section]) == set(TARGETS), f"{section} covers {sorted(record[section])}, not {TARGETS}")
        for target_name, problems in record[section].items():
            _require(set(problems) == set(PROBLEMS), f"{section} {target_name} covers {sorted(problems)}")
    for problem, checks in record["checks"].items():
        if recompute_exact:
            _require(
                {key: value for key, value in checks.items() if key != "sampled_phase_total_variation"}
                == recomputed_exact_checks(problem),
                f"{problem}: retained exact checks differ from the recomputed checks",
            )
        _require(checks["single_encoding_builder_matches_factor_order_finding"] is True, f"{problem}: builder check")
        for name, row in checks["splits"].items():
            _require(all(value is True for value in row.values()), f"{problem} {name}: exact check {row}")
        for name, variation in checks["sampled_phase_total_variation"].items():
            _require(variation <= SAMPLED_TV_BOUND, f"{problem} {name}: sampled total variation {variation}")
    for target_name, problems in record["routed"].items():
        for problem, block in problems.items():
            rebuilt = judge(target_name, problem, copy.deepcopy(block))
            _require(rebuilt == block, f"{target_name} {problem}: retained medians or verdicts differ from the runs")
            names = [entry["name"] for entry in block["single_b"]] + [entry["name"] for entry in block["split"]]
            listed = [
                entry["name"]
                for entry in record["candidates"][problem]["single_b"] + record["candidates"][problem]["split"]
            ]
            _require(names == listed, f"{target_name} {problem}: routed entries differ from the candidates")
    for target_name, problems in record["holdout"].items():
        for problem, entries in problems.items():
            expected_names = decisive_names(record, problem, record["routed"][target_name][problem])
            where = f"holdout {target_name} {problem}"
            _require(sorted(entries) == sorted(expected_names), f"{where}: entries {sorted(entries)}")
            labels = {arm_name(ff) for ff in arms(problem)}
            for name, entry in entries.items():
                _require(set(entry) == labels, f"{where} {name}: arms {sorted(entry)}")
                for label, arm in entry.items():
                    seeds = [run[0] for run in arm["runs"]]
                    _require(seeds == list(HOLDOUT_SEEDS), f"{where} {name} {label}: seeds {seeds}")
                    _require(
                        all(len(run) == len(RUN_FIELDS) for run in arm["runs"]), f"{where} {name} {label}: run schema"
                    )
                    _require(
                        arm["median_routed_cz"] == statistics.median(run[3] for run in arm["runs"]),
                        f"{where} {name} {label}: median differs from its runs",
                    )


Location = tuple[str, str, str]  # (target, problem, entry name)


def routed_entry(block: dict[str, Any], name: str) -> dict[str, Any]:
    if name == block["baseline"]["name"]:
        return block["baseline"]
    return next(e for e in block["single_b"] + block["split"] if e["name"] == name)


def replay_jobs(
    record: dict[str, Any],
) -> list[tuple[Location, tuple[str, str, dict[str, Any] | None, bool, int], list[Any]]]:
    """Every compilation behind a decisive verdict: the unencoded baseline and each decisive circuit."""
    jobs = []
    for target_name, problems in record["routed"].items():
        for problem, block in problems.items():
            names = [block["baseline"]["name"], *decisive_names(record, problem, block)]
            for name in names:
                candidate = None if name == block["baseline"]["name"] else by_name(record, problem, name)
                entry = routed_entry(block, name)
                for ff in arms(problem):
                    for run in entry["arms"][arm_name(ff)]["runs"]:
                        jobs.append(((target_name, problem, name), (target_name, problem, candidate, ff, run[0]), run))
    return jobs


def verify_verdicts(record: dict[str, Any], fresh: dict[Location, dict[str, list[list[Any]]]]) -> None:
    """Re-derive the baseline medians and every decisive verdict with the fresh runs in place of the retained ones."""
    for target_name, problems in record["routed"].items():
        for problem, block in problems.items():
            rebuilt = copy.deepcopy(block)
            for (target, prob, name), arm_runs in fresh.items():
                if (target, prob) == (target_name, problem):
                    for label, rows in arm_runs.items():
                        routed_entry(rebuilt, name)["arms"][label]["runs"] = rows
            judge(target_name, problem, rebuilt)
            where = f"{target_name} {problem}"
            for label, arm in block["baseline"]["arms"].items():
                _require(
                    rebuilt["baseline"]["arms"][label]["medians"]["routed_cz"] == arm["medians"]["routed_cz"],
                    f"{where}: baseline {label} median routed CZ differs from the fresh runs",
                )
            for key in ("best_single_b", "best_split"):
                _require(rebuilt[key] == block[key], f"{where}: {key} differs from the fresh runs")
            for name in decisive_names(record, problem, block):
                kept, new = routed_entry(block, name), routed_entry(rebuilt, name)
                for key in ("admission", "beats_best_single_b"):
                    _require(kept.get(key) == new.get(key), f"{where} {name}: {key} differs from the fresh runs")


def check(record: dict[str, Any], replay_limit: int | None = None) -> str:
    check_derived(record)
    for problem in PROBLEMS:
        best = sorted({block[problem]["best_split"] for block in record["routed"].values()})
        splits = [entry for entry in record["candidates"][problem]["split"] if entry["name"] in best]
        sampled = sampled_checks(problem, splits)
        retained = record["checks"][problem]["sampled_phase_total_variation"]
        _require(all(retained[name] == value for name, value in sampled.items()), f"{problem}: sampled check differs")
    jobs = replay_jobs(record)
    if replay_limit is not None:
        jobs = jobs[:replay_limit]
    recompiled = parallel.ordered_map(compile_job, [job for _, job, _ in jobs], min_items=2)
    deviation = 0.0
    fresh: dict[Location, dict[str, list[list[Any]]]] = {}
    for (location, job, kept), run in zip(jobs, recompiled, strict=True):
        fresh.setdefault(location, {}).setdefault(arm_name(job[3]), []).append(run)
        matched = replay_matches(run, kept)
        if matched is None or matched > REPLAY_TOLERANCE:
            raise SystemExit(
                f"gl52_split_conjugators: {job[0]} {job[1]} seed {job[4]}: recompiled {run} against {kept}"
            )
        deviation = max(deviation, matched)
    if replay_limit is None:
        verify_verdicts(record, fresh)
    ten = record["surrogate"]["ten_round"]
    two = record["surrogate"]["two_round"]
    return (
        f"{len(jobs)} compilations replayed (largest depth or duration deviation {deviation:.5f}); surrogate "
        f"two_round {two['single_b_optimum']} -> {two['split_optimum']}, ten_round {ten['single_b_optimum']} -> "
        f"{ten['split_optimum']}"
    )


# ---------------------------------------------------------------- self-test


def brute_force_gl32() -> dict[int, int]:
    """Distances in GL(3,2) by breadth-first search over tuple matrices."""
    identity: tuple[tuple[int, ...], ...] = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    seen = {identity: 0}
    frontier = [identity]
    while frontier:
        following: list[tuple[tuple[int, ...], ...]] = []
        for matrix in frontier:
            for control in range(3):
                for target in range(3):
                    if control == target:
                        continue
                    rows = list(matrix)
                    rows[target] = tuple(a ^ b for a, b in zip(rows[target], rows[control], strict=True))
                    image = tuple(rows)
                    if image not in seen:
                        seen[image] = seen[matrix] + 1
                        following.append(image)
        frontier = following
    return {sum(bit << (3 * r + j) for r, row in enumerate(m) for j, bit in enumerate(row)): d for m, d in seen.items()}


def sample_pair_holds(pair: tuple[int, int]) -> bool:
    """min_P d(P T) = min_P d(T P) = d_perm(T) for T between two cosets, and both distance routes agree."""
    x, y = pair
    identity, free = distance_tables()
    cosets = lcs.coset_columns()
    perms = permutation_matrices()
    packed = pack_columns(transition_columns(tuple(cosets[x]), tuple(cosets[y])))
    left = min(int(identity[_multiply(p, packed)]) for p in perms)
    right = min(int(identity[_multiply(packed, p)]) for p in perms)
    return (
        left == right == int(free[packed])
        and best_representative(tuple(cosets[x]), tuple(cosets[y]))[1] == left
        and int(pair_distances(x, np.asarray([y]))[0]) == left
    )


def graph_distance_holds(job: tuple[int, tuple[int, ...]]) -> bool:
    """The coset-graph distance from x equals the table distance to every listed coset."""
    x, ys = job
    targets = np.asarray(ys)
    return bool(np.array_equal(coset_distances_from(x)[targets], pair_distances(x, targets)))


def self_test(record: dict[str, Any]) -> str:
    small = cnot_bfs([pack_columns([1, 2, 4], 3)], 3)
    reference = brute_force_gl32()
    _require(len(reference) == 168, "GL(3,2) has 168 elements")
    _require(int((small != UNREACHED).sum()) == 168, "the packed search misses GL(3,2) elements")
    _require(all(int(small[packed]) == d for packed, d in reference.items()), "packed and brute-force GL(3,2) differ")
    identity, free = distance_tables()
    _require(
        table_summary(identity)["histogram"]["1"] == 20 and table_summary(free)["histogram"]["0"] == 120, "level counts"
    )
    rng = random.Random(SAMPLE_SEED)
    count = len(lcs.coset_columns())
    pairs = [(rng.randrange(count), rng.randrange(count)) for _ in range(SAMPLE_PAIRS)]
    failed = [
        pair
        for pair, ok in zip(pairs, parallel.ordered_map(sample_pair_holds, pairs, min_items=2), strict=True)
        if not ok
    ]
    _require(not failed, f"permutation-free identities fail on coset pairs {failed[:4]}")
    ys = [y for _, y in pairs]
    graph_jobs = [(x, tuple(ys)) for x, _ in pairs[:4]]
    _require(all(parallel.ordered_map(graph_distance_holds, graph_jobs, min_items=2)), "coset-graph distance differs")
    corruptions = {
        "garnet coupling": lambda r: r["inputs"]["garnet_coupling"].pop(),
        "identity histogram": lambda r: r["distance"]["identity_source"]["histogram"].__setitem__("12", 25),
        "table sha256": lambda r: r["distance"]["permutation_free"].__setitem__("table_sha256", "0" * 64),
        "split optimum": lambda r: r["surrogate"]["ten_round"].__setitem__("split_optimum", 1856),
        "transition word": lambda r: r["candidates"]["ten_round"]["split"][0]["transitions"][0]["cnots"].pop(),
        "best split": lambda r: r["routed"]["fake_fez"]["two_round"].__setitem__("best_split", "split_0_0"),
        "median": lambda r: r["routed"]["fake_fez"]["ten_round"]["split"][0]["arms"]["feed_forward"][
            "medians"
        ].__setitem__("routed_cz", 1),
        "verdict": lambda r: r["routed"]["fake_kingston"]["ten_round"]["split"][0].__setitem__(
            "beats_best_single_b", not r["routed"]["fake_kingston"]["ten_round"]["split"][0]["beats_best_single_b"]
        ),
        "sampled variation": lambda r: r["checks"]["two_round"]["sampled_phase_total_variation"].__setitem__(
            next(iter(r["checks"]["two_round"]["sampled_phase_total_variation"])), 0.5
        ),
    }
    corruptions["holdout median"] = lambda r: next(
        iter(next(iter(r["holdout"]["iqm_garnet_coupling"]["two_round"].values())).values())
    ).__setitem__("median_routed_cz", 0)
    corruptions["exact check"] = lambda r: r["checks"]["ten_round"]["splits"][
        next(iter(r["checks"]["ten_round"]["splits"]))
    ].__setitem__("transition_exact", False)
    corruptions["missing target"] = lambda r: (r["routed"].pop("fake_kingston"), r["holdout"].pop("fake_kingston"))
    two = "two_round"
    fez = "fake_fez"

    def first_holdout_entry(r: dict[str, Any]) -> dict[str, Any]:
        return next(iter(r["holdout"][fez][two].values()))

    corruptions["holdout omitted seed"] = lambda r: next(iter(first_holdout_entry(r).values()))["runs"].pop()
    corruptions["holdout omitted arm"] = lambda r: first_holdout_entry(r).pop("no_feed_forward")
    corruptions["holdout omitted entry"] = lambda r: r["holdout"][fez][two].pop(next(iter(r["holdout"][fez][two])))
    corruptions["holdout extra entry"] = lambda r: r["holdout"][fez][two].__setitem__(
        "coset_extra", copy.deepcopy(first_holdout_entry(r))
    )
    corruptions["compiler seeds"] = lambda r: r["compiler"]["seeds"].pop()
    corruptions["compiler level"] = lambda r: r["compiler"].__setitem__("optimization_level", 2)
    corruptions["compiler targets"] = lambda r: r["compiler"]["targets"].pop("fake_fez")
    corruptions["compiler versions"] = lambda r: r["compiler"]["versions"].__setitem__("qiskit", "0.0.0")
    corruptions["compiler removed"] = lambda r: r.pop("compiler")
    corruptions["reordered seeds"] = lambda r: r["routed"][fez][two]["split"][0]["arms"]["feed_forward"][
        "runs"
    ].reverse()
    corruptions["baseline reordered seeds"] = lambda r: r["routed"][fez][two]["baseline"]["arms"]["feed_forward"][
        "runs"
    ].reverse()
    check_derived(record, recompute_exact=False)
    refreshed = copy.deepcopy(record)
    refreshed["inputs"]["garnet_retrieved_utc"] = "2099-01-01T00:00:00+00:00"
    refreshed["inputs"]["garnet_catalogue_sha256"] = "f" * 64
    check_derived(refreshed, recompute_exact=False)
    for label, corrupt in corruptions.items():
        damaged = copy.deepcopy(record)
        corrupt(damaged)
        try:
            check_derived(damaged, recompute_exact=False)
        except SystemExit:
            continue
        raise SystemExit(f"gl52_split_conjugators: --check accepted a corrupted {label}")
    block = record["routed"]["fake_fez"]["two_round"]
    best = next(e for e in block["single_b"] if e["name"] == block["best_single_b"])
    kept = best["arms"]["feed_forward"]["runs"][0]
    job = next(job for _, job, row in replay_jobs(record) if row is kept)
    run = compile_job(job)
    _require(replay_matches(run, kept) is not None, "the replay rejects the retained run")
    stale = copy.deepcopy(record)
    stale_block = stale["routed"][fez][two]
    for stale_arm in stale_block["baseline"]["arms"].values():
        for stale_run in stale_arm["runs"]:
            stale_run[3] += 7
    judge(fez, two, stale_block)
    check_derived(stale, recompute_exact=False)
    baseline_location = (fez, two, "unencoded")
    baseline_jobs = [(job, row) for loc, job, row in replay_jobs(stale) if loc == baseline_location]
    _require(len(baseline_jobs) == len(SEEDS) * len(arms(two)), "the replay omits the unencoded baseline")
    stale_job, stale_row = baseline_jobs[0]
    _require(replay_matches(compile_job(stale_job), stale_row) is None, "the replay accepted a stale baseline run")
    fresh_baseline: dict[Location, dict[str, list[list[Any]]]] = {baseline_location: {}}
    for loc, job, row in replay_jobs(record):
        if loc == baseline_location:
            fresh_baseline[loc].setdefault(arm_name(job[3]), []).append(row)
    try:
        verify_verdicts(stale, fresh_baseline)
    except SystemExit:
        pass
    else:
        raise SystemExit("gl52_split_conjugators: the verdict replay accepted a stale baseline")
    layout = RUN_FIELDS.index("final_layout")
    replay_corruptions = {
        "routed CZ": lambda row: row.__setitem__(3, row[3] + 1),
        "swapped layout entry": lambda row: row.__setitem__(layout, [row[layout][1], row[layout][0], *row[layout][2:]]),
        "classical stages": lambda row: row.__setitem__(
            RUN_FIELDS.index("classical_stages"), row[RUN_FIELDS.index("classical_stages")] + 1
        ),
        "classical sequence": lambda row: row.__setitem__(RUN_FIELDS.index("classical_sha256_16"), "0" * 16),
    }
    for label, corrupt_row in replay_corruptions.items():
        damaged_row = copy.deepcopy(kept)
        corrupt_row(damaged_row)
        _require(replay_matches(run, damaged_row) is None, f"the replay accepted a corrupted {label}")
    total = len(corruptions) + len(replay_corruptions) + 2
    return f"GL(3,2) search, {SAMPLE_PAIRS} sampled coset pairs and {total} corruptions rejected"


def _multiply(left: int, right: int) -> int:
    """Packed product left @ right over GF(2)."""
    mask = SIZE - 1
    product = 0
    for row in range(WIDTH):
        bits = (left >> (WIDTH * row)) & mask
        accumulated = 0
        for j in range(WIDTH):
            if bits >> j & 1:
                accumulated ^= (right >> (WIDTH * j)) & mask
        product |= accumulated << (WIDTH * row)
    return product


SCALAR = r'(?:-?[0-9][0-9.e+-]*|null|true|false|"[^"\n]*")'
FLAT_LIST = rf"\[(?:\s*{SCALAR}\s*,)*\s*{SCALAR}\s*\]"
ROW = rf"\[(?:\s*(?:{SCALAR}|{FLAT_LIST})\s*,)*\s*(?:{SCALAR}|{FLAT_LIST})\s*\]"


def _one_line(match: re.Match[str]) -> str:
    text = re.sub(r"\[\s+", "[", match.group(0))
    text = re.sub(r"\s+\]", "]", text)
    return re.sub(r",\s+", ", ", text)


def dump(record: dict[str, Any]) -> str:
    """Indented JSON with every flat list, and every list of scalars and flat lists, on one line."""
    text = json.dumps(record, indent=1, sort_keys=True)
    text = re.sub(FLAT_LIST, _one_line, text)
    return re.sub(ROW, _one_line, text) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", type=Path)
    args = parser.parse_args()
    if args.check:
        print(f"gl52_split_conjugators: {check(json.loads(args.check.read_text(encoding='utf-8')))}")
        return 0
    if args.self_test:
        print(f"gl52_split_conjugators: {self_test(json.loads(args.self_test.read_text(encoding='utf-8')))}")
        return 0
    record = capture()
    _write_atomic(args.out, dump(record))
    for target_name, problems in record["routed"].items():
        for problem, block in problems.items():
            print(
                f"{target_name} {problem}: best single-B {block['best_single_b']}, best split {block['best_split']}, "
                f"delta {block['best_split_minus_best_single_b_median_cz']}, "
                f"beating {block['splits_beating_best_single_b']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
