"""Tuna-17 case for the null block's selector offset (row A5-186): coin-fixed twins, 6-CZ blocks, QX control.

The coin series' null block b0 = e1 + e17 (coset 0 of the basis 16, 1, 2; 21 routed CZ) read a raw selector
contrast of +0.0164 +- 0.0039 where every arm-symmetric product readout and every unital or relaxation channel
gives 0. Three hypotheses reproduce it (section C2 of mechanisms.md in docs/evidence/pathion-kernel-
map/conjectures/, c2_one_cz_mech.txt): a coherent over-rotation of the X90 and X gates, a selector dropout
conditioned on the coin (an arm-asymmetric readout), and a selector flip conditioned on q12 (a readout
correlation). This module builds the case that separates them from qi_pathion_coset_coin_cases.py by import,
which keeps its bytes.

Replay. b0 is the coin series' own compile (region, transpiler seed and role map read from the retained batch-02
cases.json, whose b0.cq and cases.json digests COIN_PINS pins); replay_text() regenerates its circuit bytes and
--replay refuses any difference from the retained file.

Routing. The coin template of each low-CZ block (cosets 4, 8, 12) compiles on b0's region from each of the 120
initial layouts of the five logical bits at SEEDS_PER_BLOCK transpiler seeds from the retained ANU QRNG draw
DRAW (block slice index * SEEDS_PER_BLOCK to (index + 1) * SEEDS_PER_BLOCK - 1, in the order of LOW_CZ), at the
coin series' optimization level and basis. The pin "roles" keeps the whole role map of b0 (d0 q12, d1 q4, d2
q11, selector q8, coin q2) and routes to 12 CZ, where the over-rotation itself predicts a selector contrast of
0.0279 to 0.0549; the pin "selector_coin" keeps the selector on q8 and the coin on q2, routes to 6 CZ (d0 q4, d1
q12, d2 q11) and gives the over-rotation a selector contrast of 0. A coin block compiles to 3 CZ at all-to-all
connectivity and 4 CZ unpinned. Each block keeps the fewest-CZ candidate that meets the pin, ties to the lowest
draw index and then the least layout; SELECTION records the winners and --select repeats the search and refuses
a table that differs.

Series. The series pin is "selector_coin". Each template (b0, k4, k8, k12) runs as a base batch [readout-0,
template, readout-1] and as a twin batch holding both coin-fixed twins (the routed template with the coin's
Hadamard removed and the coin prepared in |0> or |1>, every other instruction byte-identical) and one readout
circuit, twice each, in a forward round and its mirror (batch_order), so each contrast is computed inside a
batch and pooled over the replicates. Three batches of the eight X-only preparations of q2, q8 and q12 are a
secondary readout calibration. The QX twin holds every circuit, five to a batch. preregistered(), OUTCOMES and
decide_estimates state the rules and apply them: replicate-batch and 6-CZ-block heterogeneity first, then the
control, the twin control and the class of the pooled 6-CZ contrasts against zero and against b0;
operating_characteristics simulates the decision under each mechanism. evaluate() reads the collected shot lists
through qi_records (pca.read_series). A readout drift between brackets is recorded and stops nothing.

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_cases.py
       (--select | --replay | --write DIR | --check DIR | --qx-conformance RUN_DIR | --sanity RUN_DIR...
        | --analyze RUN_DIR... --out FILE | --self-test)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_cases as blk  # noqa: E402
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_zero_divisor_cases as zd  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_analysis as pca  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_one_cz_null_tuna_17"
QX_SERIES = "pathion_one_cz_null_qx"
RY_SERIES = "pathion_one_cz_null_ry"
CASE_DIR = "results/quantum_inspire/cases/pathion_one_cz_null_tuna_17"
# The retained coin series holds b0 in its third batch; the bytes of its circuit and manifest are pinned.
COIN_BATCH = ROOT / "results/quantum_inspire/cases" / cc.TUNA_SERIES / "batch-02"
COIN_PINS = {
    "b0.cq": "9994e3b74314e0176bdbe77644be3faba9450a65ac79dae5136c7bc011cad56f",
    "cases.json": "b7d52dd9f635fd3e8ee507ab0b1d4aa706e3698adedcd659b6750ab164c113ab",
}
NQUBITS = cc.NQUBITS
KEYS = cc.KEYS
BASIS = cc.BASIS
HALF = cc.HALF
NOUT = cc.NOUT
Z_RESOLVE = pca.Z_RESOLVE
# The ANU QRNG draw whose values seed every routing candidate of the low-CZ blocks; the case manifest owns it whole.
DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json"
SEEDS_PER_BLOCK = 64
# (template name, coset of the operand e1 + e17 on the basis (16, 1, 2)); b0 is coset 0 and replays the coin series.
OPERAND = (1, 17, 1)
BASIS_VECTORS = (16, 1, 2)
LOW_CZ = (("k4", 4), ("k8", 8), ("k12", 12))
TEMPLATES = ("b0", *(name for name, _ in LOW_CZ))
BLOCKS = {"b0": pcb.Block("b0", OPERAND, BASIS_VECTORS, 0)} | {
    name: pcb.Block(name, OPERAND, BASIS_VECTORS, coset) for name, coset in LOW_CZ
}


# The routing search's winner per (pin mode, low-CZ block): (draw index of the transpiler seed, initial layout of the
# five logical bits onto region indices). `--select` repeats the search over all 120 initial layouts and each block's
# seed slice and refuses a table that differs from its result; every build and check compiles only these.
# Pin modes: "roles" holds b0's whole role map (d0 q12, d1 q4, d2 q11, selector q8, coin q2), "selector_coin" holds
# only the selector on q8 and the coin on q2 and leaves the three data qubits free.
PIN_MODES = ("roles", "selector_coin")
SELECTION: dict[tuple[str, str], tuple[int, tuple[int, ...]]] = {
    ("roles", "k4"): (0, (2, 0, 4, 3, 1)),
    ("roles", "k8"): (69, (2, 0, 4, 3, 1)),
    ("roles", "k12"): (132, (2, 0, 4, 3, 1)),
    ("selector_coin", "k4"): (0, (1, 2, 3, 4, 0)),
    ("selector_coin", "k8"): (64, (1, 2, 3, 4, 0)),
    ("selector_coin", "k12"): (128, (1, 2, 3, 4, 0)),
}


def pinned_digest(name: str) -> str:
    return hashlib.sha256((COIN_BATCH / name).read_bytes()).hexdigest()


def verify_pins() -> None:
    """Refuse the build unless each pinned file of the coin series' b0 batch carries its recorded digest."""
    for name, digest in COIN_PINS.items():
        if pinned_digest(name) != digest:
            raise ValueError(f"{COIN_BATCH / name} differs from the retained record its digest pins")


@cache
def coin_manifest() -> dict[str, Any]:
    return json.loads((COIN_BATCH / "cases.json").read_text(encoding="utf-8"))


@cache
def reference() -> dict[str, Any]:
    """The retained b0 of the coin series: its region, transpiler seed, role map and the digest of its circuit."""
    verify_pins()
    manifest = coin_manifest()
    t = manifest["templates"]["b0"]
    return {
        "region": tuple(int(q) for q in manifest["region"]),
        "seed": int(t["transpiler_seed"]),
        "roles": {k: int(v) for k, v in t["roles"].items()},
        "cz": int(t["cz"]),
        "draw": manifest["qrng_draw"],
        "draw_index": int(t["draw_index"]),
        "sha256": COIN_PINS["b0.cq"],
    }


def want_layout() -> list[int]:
    """The final index layout a routed template needs for b0's role map: logical bit -> region index."""
    ref = reference()
    return [ref["region"].index(ref["roles"][k]) for k in KEYS]


def topology() -> tuple[tuple[int, int], ...]:
    tuna, _ = zd.catalogue_check()
    return tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))


def template_circuit(name: str) -> Any:
    return pcb.block_template(BLOCKS[name], measure=False, coin=True)


def draw_values() -> list[int]:
    values = read_record(DRAW)["values"]
    if len(values) < SEEDS_PER_BLOCK * len(LOW_CZ):
        raise ValueError(f"{DRAW} holds {len(values)} values, fewer than {SEEDS_PER_BLOCK * len(LOW_CZ)}")
    return [int(v) for v in values]


def block_seeds(index: int) -> list[tuple[int, int]]:
    """(draw index, transpiler seed value) of the SEEDS_PER_BLOCK candidates of low-CZ block `index`; the block's
    slice is draw indices index * SEEDS_PER_BLOCK to (index + 1) * SEEDS_PER_BLOCK - 1."""
    values = draw_values()
    return [(n, values[n]) for n in range(index * SEEDS_PER_BLOCK, (index + 1) * SEEDS_PER_BLOCK)]


def compile_pinned(name: str, layout: tuple[int, ...], seed: int) -> Any:
    """The coin template of `name` routed on b0's region from the initial layout `layout` (logical bit -> region
    index), at the retained optimization level and basis of the coin series."""
    from qiskit import transpile

    ref = reference()
    return transpile(
        template_circuit(name),
        coupling_map=cc.local_coupling(topology(), ref["region"]),
        basis_gates=BASIS,
        optimization_level=2,
        seed_transpiler=seed,
        initial_layout=list(layout),
    )


class LayoutScore:
    """(routed CZ, final index layout) of one candidate (block, initial layout, seed, draw index); a module-level
    callable for the pool."""

    def __call__(self, item: tuple[str, tuple[int, ...], int, int]) -> tuple[int, tuple[int, ...]]:
        name, layout, seed, _draw_index = item
        compiled = compile_pinned(name, layout, seed)
        return int(compiled.count_ops().get("cz", 0)), tuple(compiled.layout.final_index_layout())


def pinned(mode: str, final: tuple[int, ...]) -> bool:
    """Whether a final layout satisfies the pin mode against b0's role map."""
    want = want_layout()
    if mode == "roles":
        return list(final) == want
    if mode == "selector_coin":
        return final[KEYS.index("selector")] == want[KEYS.index("selector")] and (
            final[KEYS.index("coin")] == want[KEYS.index("coin")]
        )
    raise ValueError(f"unknown pin mode {mode}")


@cache
def search_table() -> dict[str, list[tuple[int, int, tuple[int, ...], int, tuple[int, ...]]]]:
    """Per low-CZ block, every candidate over all 120 initial layouts and the block's seed slice:
    (CZ, draw index, initial layout, seed, final layout)."""
    layouts = list(itertools.permutations(range(len(KEYS))))
    out: dict[str, list[tuple[int, int, tuple[int, ...], int, tuple[int, ...]]]] = {}
    for index, (name, _) in enumerate(LOW_CZ):
        items = [(name, layout, seed, n) for layout in layouts for n, seed in block_seeds(index)]
        scores = parallel.ordered_map(LayoutScore(), items)
        out[name] = [
            (cz, n, layout, seed, final) for (_, layout, seed, n), (cz, final) in zip(items, scores, strict=True)
        ]
    return out


def best_pinned(mode: str, name: str) -> tuple[int, int, tuple[int, ...], int]:
    """The fewest-CZ candidate that meets the pin mode; ties go to the lowest draw index, then the least layout."""
    rows = [r[:4] for r in search_table()[name] if pinned(mode, r[4])]
    if not rows:
        raise ValueError(f"no candidate of {name} meets the pin mode {mode}")
    return min(rows, key=lambda r: (r[0], r[1], r[2]))


def free_best(name: str) -> int:
    """Fewest routed CZ of `name` over every candidate, with no pin."""
    return min(r[0] for r in search_table()[name])


def compile_b0() -> Any:
    """The retained b0 compile replayed: the coin series' own compile of template b0 on its region at its seed."""
    ref = reference()
    index = next(i for i, t in enumerate(cc.TEMPLATES) if t[0] == "b0")
    return cc.compile_template(topology(), index, ref["region"], ref["seed"])


def entry_of(
    name: str, compiled: Any, seed: int, draw_index: int | None, layout: tuple[int, ...] | None
) -> dict[str, Any]:
    ref = reference()
    rounded = blk.round_to_grid(compiled)
    final = rounded.layout.final_index_layout()
    ideal = blk.ideal_of_record(rounded)
    plus, minus = cc.arm_laws(ideal)
    return {
        "block": name,
        "coset": BLOCKS[name].coset,
        "draw_index": draw_index,
        "transpiler_seed": seed,
        "initial_layout": None if layout is None else list(layout),
        "cz": int(rounded.count_ops().get("cz", 0)),
        "roles": {k: int(ref["region"][final[v]]) for v, k in enumerate(KEYS)},
        "circuit": rounded,
        "ideal": ideal,
        "ideal_c": pcb.output_contrast(plus, minus),
        "ideal_selector_contrast": float(pcb.selector_contrast(plus, minus)),
    }


def routed(mode: str, name: str) -> dict[str, Any]:
    """The routed, grid-rounded entry of low-CZ block `name` under the pin mode, compiled from SELECTION."""
    n, layout = SELECTION[(mode, name)]
    seed = draw_values()[n]
    return entry_of(name, compile_pinned(name, layout, seed), seed, n, layout)


def select() -> dict[str, dict[str, Any]]:
    """Repeat the routing search and refuse a SELECTION that is not its winner; returns, per pin mode and block, the
    winner, the number of candidates that meet the pin by CZ count and the unpinned minimum."""
    report: dict[str, dict[str, Any]] = {}
    for mode in PIN_MODES:
        for name, _ in LOW_CZ:
            cz, n, layout, seed = best_pinned(mode, name)
            if SELECTION[(mode, name)] != (n, layout):
                raise ValueError(
                    f"{mode} {name}: SELECTION {SELECTION[(mode, name)]} differs from the winner {(n, layout)}"
                )
            counts: dict[int, int] = {}
            for row in search_table()[name]:
                if pinned(mode, row[4]):
                    counts[row[0]] = counts.get(row[0], 0) + 1
            report[f"{mode}/{name}"] = {
                "cz": cz,
                "draw_index": n,
                "initial_layout": list(layout),
                "transpiler_seed": seed,
                "candidates_by_cz": dict(sorted(counts.items())),
                "unpinned_minimum_cz": free_best(name),
            }
    return report


def template_text(name: str, entry: dict[str, Any]) -> str:
    """The Tuna-17 circuit file of a routed entry on b0's region, in the coin series' layout; b0's note line is the
    retained one, a low-CZ block's also names its initial layout."""
    ref = reference()
    region = ref["region"]
    layout = "" if entry["initial_layout"] is None else f" layout {entry['initial_layout']}"
    note = f"// region {list(region)} template {name} seed {entry['transpiler_seed']}{layout} coin"
    return cc.circuit_text(entry["circuit"], dict(enumerate(region)), NQUBITS, note)


def replay_text() -> str:
    """The regenerated bytes of the retained b0.cq: b0's compile at its own region and transpiler seed."""
    ref = reference()
    return template_text("b0", entry_of("b0", compile_b0(), ref["seed"], ref["draw_index"], None))


def replay_check() -> str:
    """Refuse a replay whose bytes differ from the retained b0.cq."""
    text = replay_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    if text != (COIN_BATCH / "b0.cq").read_text(encoding="utf-8") or digest != COIN_PINS["b0.cq"]:
        raise ValueError("the replayed b0 circuit differs from the retained b0.cq")
    return digest


# Series ---------------------------------------------------------------------------------------------------------

SERIES_PIN = "selector_coin"
SCHEMA = "qi-pathion-one-cz-null-cases-v2"
ANALYSIS_SCHEMA = "qi-pathion-one-cz-null-analysis-v2"
# Every circuit of a base or twin batch runs at BATCH_SHOTS (b0's base batches at CONTROL_SHOTS, which lifts the
# control's power), each template appears in REPLICATES batches of each kind,
# and the X-only joint preparations run at JOINT_SHOTS.
BATCH_SHOTS = 32768
CONTROL_SHOTS = 65536
REPLICATES = 2
JOINT_SHOTS = 16384
QX_SHOTS = 2048
# Shots of the coin series' Tuna-17 jobs whose timings size this series.
COIN_SHOTS = 65536
QX_QUBITS = 10
QX_BATCH_CIRCUITS = 5
# Physical qubits of the X-only readout calibration: the coin and the selector of every template, and the qubit that
# carries d0 in b0 and d1 in the 6-CZ blocks.
JOINT_QUBITS = {"coin": 2, "selector": 8, "q12": 12}
JOINT_PREPS = tuple(itertools.product((0, 1), repeat=3))
# The preparations of (q2, q8, q12) by batch: the two coin values of a prepared selector 1 meet at equal q12 in one
# batch.
JOINT_BATCHES = (
    ((0, 1, 1), (1, 1, 1), (0, 0, 0)),
    ((0, 1, 0), (1, 1, 0), (0, 0, 1)),
    ((1, 0, 0), (1, 0, 1)),
)
# Sized models of the mechanism simulation: each gives b0 a raw selector contrast of +0.0164.
MODEL_SIZE = 0.036
SMALL = 0.012
# A calibration statistic informs only at a standard error that lets three of them stay inside SMALL.
JOINT_SE_LIMIT = SMALL / Z_RESOLVE
# Heterogeneity bounds: replicate batches of one template and kind (1 degree of freedom, alpha 0.001 over the eight
# comparisons) and the three 6-CZ blocks (2 degrees of freedom, alpha 0.01 for each of two observables).
BATCH_CHI2 = 10.828
BLOCK_CHI2 = 9.210
LOW_NAMES = tuple(name for name, _ in LOW_CZ)
# Raw selector contrast of the base circuit (s) and of the coin-twin pair (t) of b0 and of a 6-CZ block under each
# hypothesis, from c2_one_cz_mech.txt and c2_one_cz_twins.txt (each model sized to give b0's base circuit +0.0164). The
# X-axis over-rotation (sized to 0.0513 rad after every X90 and X gate) and the q12 correlation leave a 6-CZ block at
# 0, and the worst admitted over-rotation about another axis (Y, before or after the pulse gate, 0.07 rad) leaves it at
# 0.0038 and 0.0039; the coin-conditioned dropout reads the b0 value on it;
# the superposition-only offset is a hypothesis with no simulation, an offset that the classical-coin twin cannot show.
PREDICTED: dict[str, dict[str, float]] = {
    "over_rotation": {"s_b0": 0.0164, "t_b0": 0.0166, "s_k": 0.0, "t_k": 0.0},
    "over_rotation_y_axis": {"s_b0": 0.0164, "t_b0": 0.0164, "s_k": 0.0038, "t_k": 0.0039},
    "coin_dropout": {"s_b0": 0.0164, "t_b0": 0.0170, "s_k": 0.0164, "t_k": 0.0170},
    "q12_correlation": {"s_b0": 0.0164, "t_b0": 0.0170, "s_k": 0.0, "t_k": 0.0},
    "superposition_only": {"s_b0": 0.0164, "t_b0": 0.0, "s_k": 0.0164, "t_k": 0.0},
}
WORLDS_SIZED = ("absent", *PREDICTED)
CONTROL_KIND = pcs.CONTROL_KIND
# Operating characteristics: Gaussian batch estimates at the design standard errors, drawn from a QRNG seed.
OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T185234Z.json"
OC_SEED_INDEX = 0
OC_DRAWS = 20000
OC_DRIFT_SD = 0.003


def joint_file(prep: tuple[int, ...]) -> str:
    return "joint-" + "".join(str(b) for b in prep) + ".cq"


def joint_text(nqubits: int, prep: tuple[int, ...]) -> str:
    """Every register qubit in |0> except the joint qubits prepared in |1> by X, all qubits measured."""
    qubits = list(JOINT_QUBITS.values())
    note = "// joint preparation " + " ".join(f"q{q}={b}" for q, b in zip(qubits, prep, strict=True))
    lines = zd.header(nqubits) + [note] + [f"X q[{q}]" for q, b in zip(qubits, prep, strict=True) if b]
    return "\n".join(lines + ["", "barrier q", "b = measure q", ""])


@cache
def series_plan() -> dict[str, Any]:
    """b0 replayed and the 6-CZ blocks (selector q8 and coin q2 held, data qubits free) on b0's region."""
    region = reference()["region"]
    templates = {"b0": entry_of("b0", compile_b0(), reference()["seed"], reference()["draw_index"], None)}
    for name, _ in LOW_CZ:
        templates[name] = routed(SERIES_PIN, name)
    return {"region": region, "templates": templates}


def selector_dropout(source: int, state: int, x: float) -> np.ndarray:
    """32x32 stochastic matrix: a true selector 1 reads 0 with probability x when bit `source` equals `state`."""
    matrix = np.eye(NOUT)
    for s in range(NOUT):
        if (s >> SELECTOR) & 1 and (s >> source) & 1 == state:
            matrix[s, s] -= x
            matrix[s ^ (1 << SELECTOR), s] += x
    return matrix


def selector_flip(source: int, state: int, x: float) -> np.ndarray:
    """32x32 stochastic matrix: the selector flips with probability x when bit `source` equals `state`."""
    matrix = np.zeros((NOUT, NOUT))
    for s in range(NOUT):
        p = x if (s >> source) & 1 == state else 0.0
        matrix[s, s] += 1.0 - p
        matrix[s ^ (1 << SELECTOR), s] += p
    return matrix


def joint_law(
    prep: tuple[int, ...], assignment: dict[int, tuple[float, float]], dropout: float, flip: float
) -> np.ndarray:
    """Law over the reads (coin, selector, q12) of a preparation: independent assignment on each qubit, a selector 1
    read as 0 with probability `dropout` when the coin was prepared 1, and the selector flipped with probability `flip`
    when q12 was prepared 0."""
    law = np.ones(1)
    for position, (name, q) in reversed(list(enumerate(JOINT_QUBITS.items()))):
        e01, e10 = assignment[q]
        p1 = 1.0 - e10 if prep[position] else e01
        if name == "selector":
            if prep[0] == 1 and prep[1] == 1:
                p1 *= 1.0 - dropout
            if prep[2] == 0:
                p1 = p1 * (1.0 - flip) + (1.0 - p1) * flip
        law = np.kron(law, np.array([1.0 - p1, p1]))
    return law


def coin_timing() -> dict[str, Any]:
    """Execution seconds per shot of the coin series' 65536-shot Tuna-17 jobs, from the retained results.json files."""
    rates = []
    for batch in range(4):
        run = ROOT / "results/quantum_inspire/runs" / f"2026-11-07T001031Z-{cc.TUNA_SERIES}-batch-{batch:02d}"
        for row in json.loads((run / "results.json").read_text(encoding="utf-8"))["jobs"]:
            result = row["results"][0]
            if result["shots_done"] == COIN_SHOTS:
                rates.append(result["execution_time_in_seconds"] / COIN_SHOTS)
    if not rates:
        raise ValueError("the retained coin series holds no 65536-shot job")
    return {"jobs": len(rates), "seconds_per_shot_min": min(rates), "seconds_per_shot_max": max(rates)}


COIN = KEYS.index("coin")
SELECTOR = KEYS.index("selector")


def fixed_qubit(circuit: Any, logical_bit: int, value: int) -> tuple[Any, list[Any]]:
    """The routed circuit with logical bit `logical_bit` prepared in |value> in place of its first single-qubit run.

    The bit starts on physical qubit initial_index_layout()[logical_bit]; its single-qubit gates before its first
    two-qubit gate are removed (and replaced by one X for value 1) while every other instruction and the CZ count stay
    byte-identical. Returns the circuit and the removed operations."""
    from qiskit.circuit.library import XGate

    start = circuit.layout.initial_index_layout()[logical_bit]
    out = circuit.copy_empty_like()
    out._layout = circuit.layout
    removed: list[Any] = []
    seen_two_qubit = False
    for inst in circuit.data:
        qubits = [circuit.find_bit(q).index for q in inst.qubits]
        if not seen_two_qubit and len(qubits) == 1 and qubits[0] == start:
            if not removed and value == 1:
                out.append(XGate(), [out.qubits[start]])
            removed.append(inst.operation)
            continue
        if len(qubits) == 2 and start in qubits:
            seen_two_qubit = True
        out.append(inst.operation, [out.qubits[i] for i in qubits])
    return out, removed


def coin_fixed(circuit: Any, value: int) -> tuple[Any, list[str]]:
    """The routed circuit with the coin prepared in |value> in place of the |+> its first single-qubit run builds.

    That run is the Hadamard of the template, and it must equal the Hadamard up to a global phase: the twin then differs
    from the template by that one gate and the X that replaces it. Returns the circuit and the removed gate names."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import HGate
    from qiskit.quantum_info import Operator

    out, removed = fixed_qubit(circuit, COIN, value)
    run = QuantumCircuit(1)
    for operation in removed:
        run.append(operation, [0])
    if not Operator(run).equiv(Operator(HGate())):
        raise ValueError("the coin's first single-qubit run is not the Hadamard of the template")
    return out, [operation.name for operation in removed]


@cache
def twin_entry(name: str, value: int) -> dict[str, Any]:
    """The coin-fixed twin of template `name` with the coin prepared in |value>."""
    base = series_plan()["templates"][name]
    circuit, removed = coin_fixed(base["circuit"], value)
    return {
        **{k: base[k] for k in ("block", "coset", "draw_index", "transpiler_seed", "initial_layout", "cz", "roles")},
        "template": name,
        "coin": value,
        "removed": removed,
        "circuit": circuit,
        "ideal": blk.ideal_of_record(circuit),
    }


def twin_file(name: str, value: int) -> str:
    return f"{name}-coin{value}.cq"


def twin_note(name: str, value: int) -> str:
    base = series_plan()["templates"][name]
    note = template_note(name, base, series_plan()["region"])
    return note.removesuffix(" coin") + f" coin prepared {value}"


def batch_order() -> list[tuple[str, str, int]]:
    """(template, kind, replicate) of the sixteen template batches: a forward round and its mirror, so each template's
    base and twin batches sit at mirrored positions and a linear drift cancels between the two replicates."""
    first = [(t, k) for t, k in (("b0", "base"), ("b0", "twin"), ("k4", "twin"), ("k4", "base"))]
    first += [("k8", "base"), ("k8", "twin"), ("k12", "twin"), ("k12", "base")]
    return [(t, k, 0) for t, k in first] + [(t, k, 1) for t, k in reversed(first)]


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: the sixteen template batches of batch_order (a base batch is [readout-0,
    template, readout-1]; a twin batch holds both coin twins and one readout, readout-0 in the forward round and
    readout-1 in the mirror), then the three X-only calibration batches. QX: every base circuit and twin, five to a
    batch."""
    rows: list[dict[str, Any]] = []
    if series_name == QX_SERIES:
        files: list[dict[str, Any]] = []
        for name in TEMPLATES:
            files.append({"file": f"{name}.cq", "kind": "data", "template": name, "coin": None})
            files += [{"file": twin_file(name, v), "kind": "data", "template": name, "coin": v} for v in (0, 1)]
        for start in range(0, len(files), QX_BATCH_CIRCUITS):
            rows.append(
                {
                    "batch": f"batch-{len(rows):02d}",
                    "kind": "control",
                    "template": None,
                    "replicate": None,
                    "circuits": files[start : start + QX_BATCH_CIRCUITS],
                }
            )
        return rows
    for name, kind, replicate in batch_order():
        base = {"file": f"{name}.cq", "kind": "data", "template": name, "coin": None}
        twins = [{"file": twin_file(name, v), "kind": "data", "template": name, "coin": v} for v in (0, 1)]
        if kind == "base":
            circuits = [{"file": "readout-0.cq", "kind": "readout"}, base, {"file": "readout-1.cq", "kind": "readout"}]
        elif replicate == 0:
            circuits = [{"file": "readout-0.cq", "kind": "readout"}, *twins]
        else:
            circuits = [*reversed(twins), {"file": "readout-1.cq", "kind": "readout"}]
        rows.append(
            {
                "batch": f"batch-{len(rows):02d}",
                "kind": kind,
                "template": name,
                "replicate": replicate,
                "circuits": circuits,
            }
        )
    for preps in JOINT_BATCHES:
        circuits = [
            {"file": joint_file(prep), "kind": "joint", "prep": dict(zip(JOINT_QUBITS, prep, strict=True))}
            for prep in preps
        ]
        rows.append(
            {
                "batch": f"batch-{len(rows):02d}",
                "kind": "joint",
                "template": None,
                "replicate": None,
                "circuits": circuits,
            }
        )
    return rows


def row_shots(row: dict[str, Any]) -> int:
    """Shots of every circuit of a batch row."""
    if row["kind"] == "joint":
        return JOINT_SHOTS
    return CONTROL_SHOTS if row["kind"] == "base" and row["template"] == "b0" else BATCH_SHOTS


# Fields of a batch's cases.json that differ between batches of one series.
BATCH_FIELDS = ("batch", "circuits", "shots", "kind", "template", "replicate")


def preregistered() -> dict[str, str]:
    z = Z_RESOLVE
    return {
        "estimates": "per template and batch kind, the raw selector contrast of each batch (base: the arm contrast "
        "P(s=0 | coin read 1) - P(s=0 | coin read 0); twin: P(s=0) of the coin-1 twin minus that of the coin-0 twin), "
        "pooled over the replicate batches by inverse variance",
        "heterogeneity": f"replicate batches of one template and kind agree within chi-square {BATCH_CHI2} "
        f"(1 degree of freedom, alpha 0.001); the three 6-CZ blocks agree within chi-square {BLOCK_CHI2} "
        "(2 degrees of freedom, alpha 0.01) for the base contrasts and for the twin contrasts; otherwise the "
        "decision is unresolved",
        "control": f"b0 base contrast s0 above {z} se, else the offset is absent and nothing about its mechanism "
        "is decided",
        "twin_control": f"b0 twin contrast t0 above {z} se; if not, and s0 - t0 exceeds {z} combined se, the offset "
        "exists only with the coin in superposition",
        "six_cz": f"c and d the inverse-variance means of the three 6-CZ base and twin contrasts, m their combination "
        f"and r the combination of s0 and t0: contexts disagree when |c - d| exceeds {z} combined se; zero when |m| "
        f"is within {z} se and r - m exceeds {z} combined se; b0-like when m exceeds {z} se and |r - m| is within "
        f"{z} combined se; otherwise unresolved",
        "calibration": "the eight X-only preparations of q2, q8 and q12 are a secondary readout calibration in a "
        "terminal-assignment context: D, the selector misassignment with the coin prepared 1 minus 0 at a prepared "
        f"selector 1, and G, with q12 prepared 0 minus 1, are reported with large (>= {MODEL_SIZE} - {z} se) and small "
        f"(|.| + {z} se < {SMALL}) classes and change no outcome",
        "qx": "every circuit within twice the sampling floor of its ideal law",
    }


def series(
    plan: dict[str, Any], backend: dict[str, Any], series_name: str, nqubits: int, place: dict[int, int]
) -> dict[str, str]:
    region = plan["region"]
    register = [place[n] for n in range(len(region))]
    files: dict[str, str] = {}
    ref = reference()
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "region": list(region),
        "placement": {str(k): v for k, v in place.items()},
        "register": register,
        "qrng_draw": DRAW,
        "joint_qubits": dict(JOINT_QUBITS),
        "templates": {
            name: {
                "block": name,
                "operand": list(OPERAND),
                "basis": list(BASIS_VECTORS),
                "coset": BLOCKS[name].coset,
                "pin": "replay of the retained coin series b0" if name == "b0" else SERIES_PIN,
                "draw_index": t["draw_index"],
                "transpiler_seed": t["transpiler_seed"],
                "initial_layout": t["initial_layout"],
                "cz": t["cz"],
                "roles": {k: place[list(region).index(q)] for k, q in t["roles"].items()},
                "ideal_selector_contrast": round(t["ideal_selector_contrast"], 9) + 0.0,
                "ideal_c": [round(float(x), 6) for x in t["ideal_c"]],
            }
            for name, t in plan["templates"].items()
        },
        "retained_b0": {"cases_sha256": COIN_PINS["cases.json"], "circuit_sha256": ref["sha256"]},
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_rows(series_name):
        hardware = series_name != QX_SERIES
        shots = row_shots(row) if hardware else QX_SHOTS
        texts: dict[str, str] = {}
        circuits: list[dict[str, Any]] = []
        for spec in row["circuits"]:
            record = dict(spec)
            if spec["kind"] == "readout":
                texts[spec["file"]] = cc.readout_text(nqubits, spec["file"] == "readout-1.cq", register)
            elif spec["kind"] == "joint":
                prep = tuple(spec["prep"].values())
                texts[spec["file"]] = joint_text(nqubits, prep)
            else:
                name = spec["template"]
                if spec["coin"] is None:
                    t = plan["templates"][name]
                    texts[spec["file"]] = cc.circuit_text(t["circuit"], place, nqubits, template_note(name, t, region))
                else:
                    t = twin_entry(name, spec["coin"])
                    texts[spec["file"]] = cc.circuit_text(t["circuit"], place, nqubits, twin_note(name, spec["coin"]))
                record["ideal"] = [round(float(x), 12) for x in t["ideal"]]
            record["sha256"] = hashlib.sha256(texts[spec["file"]].encode()).hexdigest()
            circuits.append(record)
            files[f"{row['batch']}/{spec['file']}"] = texts[spec["file"]]
        manifest = {
            "schema": SCHEMA,
            **common,
            "shots": shots,
            "batch": row["batch"],
            "kind": row["kind"],
            "template": row["template"],
            "replicate": row["replicate"],
            "circuits": circuits,
        }
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "kind": row["kind"], "files": [c["file"] for c in circuits]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-pathion-one-cz-null-series-v2", "backend": backend["identifier"], "batches": batches},
            indent=1,
        )
        + "\n"
    )
    return files


def template_note(name: str, entry: dict[str, Any], region: tuple[int, ...]) -> str:
    layout = "" if entry["initial_layout"] is None else f" layout {entry['initial_layout']}"
    return f"// region {list(region)} template {name} seed {entry['transpiler_seed']}{layout} coin"


def build() -> dict[str, dict[str, str]]:
    tuna, qx = zd.catalogue_check()
    plan = series_plan()
    region = plan["region"]
    return {
        TUNA_SERIES: series(plan, tuna, TUNA_SERIES, NQUBITS, dict(enumerate(region))),
        QX_SERIES: series(plan, qx, QX_SERIES, QX_QUBITS, {n: n for n in range(len(region))}),
    }


def design() -> dict[str, Any]:
    """Standard errors and seconds of the series: batch and pooled contrasts at BATCH_SHOTS, the calibration statistics
    at JOINT_SHOTS under the retained readout rates of the selector, and the Tuna-17 seconds."""
    e01, e10 = cc.retained_readout(reference()["region"])[JOINT_QUBITS["selector"]]
    joint_se = {s: math.sqrt(p * (1 - p) / JOINT_SHOTS) for s, p in ((0, e01), (1, e10))}
    timing = coin_timing()
    rows = batch_rows(TUNA_SERIES)
    jobs = sum(len(r["circuits"]) for r in rows)
    shots_total = sum(row_shots(r) * len(r["circuits"]) for r in rows)
    se_base_batch = 1.0 / math.sqrt(BATCH_SHOTS)
    se_twin_batch = math.sqrt(0.5 / BATCH_SHOTS)
    se_control_batch = 1.0 / math.sqrt(CONTROL_SHOTS)
    return {
        "base_batch_se": round(se_base_batch, 6),
        "b0_base_batch_se": round(se_control_batch, 6),
        "twin_batch_se": round(se_twin_batch, 6),
        "pooled_se": {
            "base": round(se_base_batch / math.sqrt(REPLICATES), 6),
            "b0_base": round(se_control_batch / math.sqrt(REPLICATES), 6),
            "twin": round(se_twin_batch / math.sqrt(REPLICATES), 6),
        },
        "calibration_se": {f"selector_prepared_{s}": round(v, 6) for s, v in joint_se.items()},
        "calibration_se_limit": JOINT_SE_LIMIT,
        "retained_selector_readout_e01_e10": [round(e01, 4), round(e10, 4)],
        "jobs": jobs,
        "batches": len(rows),
        "shots_total": shots_total,
        "execution_seconds_range": [
            round(jobs * 2.6 + shots_total * 0.53e-3, 1),
            round(jobs * 2.6 + shots_total * timing["seconds_per_shot_max"], 1),
        ],
        "pause_seconds_per_batch": 30,
        "coin_series_timing": timing,
    }


# Decisions ------------------------------------------------------------------------------------------------------

OUTCOMES: dict[str, tuple[str, str]] = {
    "offset_absent": (
        "offset absent: b0's base contrast no longer reads positive at the control level; nothing about the mechanism "
        "is decided",
        "unchanged",
    ),
    "superposition_only": (
        "the offset exists only with the coin in superposition: b0's classical-coin twin reads below the base "
        "contrast, where the over-rotation, the coin-conditioned dropout and the q12 correlation all predict the "
        "same value",
        "refuted as modeled: the over-rotation predicts the offset in the classical-coin twin as well",
    ),
    "zero": (
        "6-CZ blocks read zero in both contexts: the coin-conditioned selector dropout is excluded; a coherent "
        "over-rotation and a q12 correlation remain, and these observables do not separate them",
        "survives: its falsifier, a resolved nonzero 6-CZ response inconsistent with the model's bounded prediction "
        "of zero, is unmet; the q12 correlation stays open",
    ),
    "b0_like": (
        "6-CZ blocks read the b0 value in both contexts: consistent with a coin-conditioned selector dropout, and the "
        "over-rotation and the q12 correlation are excluded",
        "refuted as stated: the resolved 6-CZ response is inconsistent with the model's bounded prediction of zero",
    ),
    "unresolved_batch": (
        "unresolved: replicate batches disagree beyond the heterogeneity bound",
        "unchanged; the numbers are reported",
    ),
    "unresolved_block": (
        "unresolved: the three 6-CZ blocks disagree beyond the heterogeneity bound",
        "unchanged; the numbers are reported",
    ),
    "unresolved_context": (
        "unresolved: the 6-CZ base and twin contrasts disagree beyond three standard errors",
        "unchanged; the numbers are reported",
    ),
    "unresolved": ("unresolved: the contrasts match no preregistered row", "unchanged; the numbers are reported"),
}
DECIDING = ("zero", "b0_like", "superposition_only")


def heterogeneity(values: list[tuple[float, float]]) -> float:
    """Chi-square of (value, se) pairs about their inverse-variance mean."""
    mean, _ = pooled(values)
    return sum(((v - mean) / se) ** 2 for v, se in values)


def decide_estimates(rows: dict[str, dict[str, list[tuple[float, float]]]]) -> dict[str, Any]:
    """The preregistered decision of per-batch estimates: rows[template]["base" | "twin"] lists (value, se) of each
    batch."""
    base = {t: pooled(rows[t]["base"]) for t in TEMPLATES}
    twin = {t: pooled(rows[t]["twin"]) for t in TEMPLATES}
    z = Z_RESOLVE
    batch_q = {f"{t}/{kind}": heterogeneity(rows[t][kind]) for t in TEMPLATES for kind in ("base", "twin")}
    block_q = {
        "base": heterogeneity([base[t] for t in LOW_NAMES]),
        "twin": heterogeneity([twin[t] for t in LOW_NAMES]),
    }
    s0, t0 = base["b0"], twin["b0"]
    c, d = pooled([base[t] for t in LOW_NAMES]), pooled([twin[t] for t in LOW_NAMES])
    m, r = pooled([c, d]), pooled([s0, t0])
    diff, diff_se = r[0] - m[0], math.hypot(r[1], m[1])
    numbers = {
        "s_b0": s0,
        "t_b0": t0,
        "c_six_cz_base": c,
        "d_six_cz_twin": d,
        "m_six_cz": m,
        "r_b0": r,
        "r_minus_m": (diff, diff_se),
        "batch_chi2": batch_q,
        "block_chi2": block_q,
    }
    if any(q > BATCH_CHI2 for q in batch_q.values()):
        label = "unresolved_batch"
    elif any(q > BLOCK_CHI2 for q in block_q.values()):
        label = "unresolved_block"
    elif s0[0] < z * s0[1]:
        label = "offset_absent"
    elif t0[0] < z * t0[1]:
        gap = (s0[0] - t0[0]) / math.hypot(s0[1], t0[1])
        label = "superposition_only" if gap >= z else "unresolved"
    elif abs(c[0] - d[0]) > z * math.hypot(c[1], d[1]):
        label = "unresolved_context"
    elif abs(m[0]) <= z * m[1] and diff >= z * diff_se:
        label = "zero"
    elif m[0] >= z * m[1] and abs(diff) <= z * diff_se:
        label = "b0_like"
    else:
        label = "unresolved"
    outcome, effect = OUTCOMES[label]
    return {"label": label, "outcome": outcome, "a5_186": effect, "decided": label in DECIDING, "numbers": numbers}


def operating_characteristics(draws: int = OC_DRAWS, drift_sd: float = 0.0) -> dict[str, dict[str, float]]:
    """Frequency of each decision label per world, from `draws` simulated series of Gaussian batch estimates at the
    design standard errors (extra independent batch drift of standard deviation `drift_sd`), seeded from QRNG value
    OC_SEED_INDEX of OC_DRAW. The decision is decide_estimates, so every gate and comparison of the table counts."""
    seed = int(read_record(OC_DRAW)["values"][OC_SEED_INDEX])
    rng = np.random.default_rng(seed)
    se_base = {t: 1.0 / math.sqrt(CONTROL_SHOTS if t == "b0" else BATCH_SHOTS) for t in TEMPLATES}
    se_twin = math.sqrt(0.5 / BATCH_SHOTS)
    out: dict[str, dict[str, float]] = {}
    for world in WORLDS_SIZED:
        mean = {"s_b0": 0.0, "t_b0": 0.0, "s_k": 0.0, "t_k": 0.0} if world == "absent" else PREDICTED[world]
        counts: dict[str, int] = {}
        noise = rng.normal(size=(draws, len(TEMPLATES), 2, REPLICATES))
        drift = rng.normal(scale=drift_sd, size=(draws, len(TEMPLATES), 2, REPLICATES))
        for i in range(draws):
            rows: dict[str, dict[str, list[tuple[float, float]]]] = {}
            for j, name in enumerate(TEMPLATES):
                key = "b0" if name == "b0" else "k"
                rows[name] = {
                    "base": [
                        (mean[f"s_{key}"] + se_base[name] * noise[i, j, 0, r] + drift[i, j, 0, r], se_base[name])
                        for r in range(REPLICATES)
                    ],
                    "twin": [
                        (mean[f"t_{key}"] + se_twin * noise[i, j, 1, r] + drift[i, j, 1, r], se_twin)
                        for r in range(REPLICATES)
                    ],
                }
            label = decide_estimates(rows)["label"]
            counts[label] = counts.get(label, 0) + 1
        out[world] = {label: round(n / draws, 4) for label, n in sorted(counts.items())}
    return out


# Predictions ----------------------------------------------------------------------------------------------------


def predictions(operating: bool = True) -> dict[str, Any]:
    """The prediction record; `operating` adds the operating characteristics, OC_DRAWS simulated series per world."""
    record: dict[str, Any] = {
        "model": "raw selector contrast of the base circuit (s) and the coin-twin pair (t) of b0 and of a 6-CZ block "
        "under each hypothesis, from docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt and "
        "c2_one_cz_twins.txt",
        "predicted_contrast": PREDICTED,
        "design": design(),
        "preregistered": preregistered(),
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in OUTCOMES.items()},
    }
    if operating:
        record["operating_characteristics"] = {
            "qrng_draw": OC_DRAW,
            "seed_index": OC_SEED_INDEX,
            "draws_per_world": OC_DRAWS,
            "stationary": operating_characteristics(),
            f"batch_drift_sd_{OC_DRIFT_SD}": operating_characteristics(drift_sd=OC_DRIFT_SD),
        }
    return record


def write(directory: Path) -> None:
    for name, files in build().items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    (directory / TUNA_SERIES / "prediction.json").write_text(
        json.dumps(predictions(), indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path, operating: bool = True) -> None:
    """The case directories hold exactly the built files; CASE.md, the hand-written case, is the one extra file.

    `operating` False leaves the operating characteristics of prediction.json unreplayed (they cost two simulations of
    OC_DRAWS series per world) and compares the rest of the record."""
    built = build()
    prediction = directory / TUNA_SERIES / "prediction.json"
    if operating:
        built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(), indent=1, sort_keys=True) + "\n"
    else:
        stored = json.loads(prediction.read_text(encoding="utf-8"))
        if stored.pop("operating_characteristics", None) is None or stored != predictions(operating=False):
            raise ValueError(f"{prediction} differs from the prediction record")
        built[TUNA_SERIES]["prediction.json"] = prediction.read_text(encoding="utf-8")
    for name, files in built.items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and not p.name.startswith(".") and p.name != "CASE.md"
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    if not (directory / TUNA_SERIES / "CASE.md").is_file():
        raise ValueError(f"{directory / TUNA_SERIES}/CASE.md is missing")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


# Analysis -------------------------------------------------------------------------------------------------------


def series_of(run_dir: Path) -> str:
    """The series a run directory `<stamp>-<series>-batch-NN` belongs to."""
    stem = run_dir.name.rpartition("-batch-")[0]
    for name in (TUNA_SERIES, QX_SERIES):
        if stem.endswith(f"-{name}"):
            return name
    raise SystemExit(f"{run_dir.name} is not a run directory of {TUNA_SERIES} or {QX_SERIES}")


def pooled(values: list[tuple[float, float]]) -> tuple[float, float]:
    """Inverse-variance mean and its standard error of (value, se) pairs."""
    weights = [1.0 / se**2 for _, se in values]
    mean = sum(w * v for w, (v, _) in zip(weights, values, strict=True)) / sum(weights)
    return mean, math.sqrt(1.0 / sum(weights))


def joint_statistics(shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, Any]:
    """Secondary calibration: misassignment of the selector (q8) conditioned on the prepared coin (q2) and q12.

    e(s | v = a) is the fraction of shots with q8 prepared s, qubit v prepared a (the other joint qubit pooled) that
    read q8 differently. D is e(1 | coin = 1) - e(1 | coin = 0) taken from the two matched pairs that share a batch and
    q12 (pooled by inverse variance, with their agreement reported); G(s) is e(s | q12 = 0) - e(s | q12 = 1)."""
    qubits = manifest["joint_qubits"]
    cells: dict[tuple[int, ...], tuple[int, int]] = {}
    where: dict[tuple[int, ...], str] = {}
    for key, listed in shots.items():
        batch, name = key.split("/")
        if not name.startswith("joint-"):
            continue
        prep = tuple(int(c) for c in name.removeprefix("joint-").removesuffix(".cq"))
        wrong = sum(1 for s in listed if pca.bit(s, qubits["selector"]) != prep[1])
        cells[prep] = (wrong, len(listed))
        where[prep] = batch
    if set(cells) != set(JOINT_PREPS):
        raise ValueError(f"the joint characterization holds preparations {sorted(cells)}, not all eight")

    def rate(position: int, value: int, selector: int) -> tuple[float, float]:
        picked = [cell for prep, cell in cells.items() if prep[1] == selector and prep[position] == value]
        wrong, total = sum(c[0] for c in picked), sum(c[1] for c in picked)
        p = wrong / total
        return p, p * (1 - p) / total

    def difference(position: int, selector: int, high: int) -> dict[str, float]:
        a, va = rate(position, high, selector)
        b, vb = rate(position, 1 - high, selector)
        return {"value": a - b, "se": math.sqrt(va + vb), "rate_a": a, "rate_b": b}

    pairs = []
    for third in (0, 1):
        hi, lo = (1, 1, third), (0, 1, third)
        if where[hi] != where[lo]:
            raise ValueError("the matched calibration pair is split across batches")
        (wh, nh), (wl, nl) = cells[hi], cells[lo]
        ph, pl = wh / nh, wl / nl
        pairs.append((ph - pl, math.sqrt(ph * (1 - ph) / nh + pl * (1 - pl) / nl)))
    d_value, d_se = pooled(pairs)
    coin = {f"selector_prepared_{s}": difference(0, s, 1) for s in (0, 1)}
    coin["selector_prepared_1"] = {**coin["selector_prepared_1"], "value": d_value, "se": d_se}
    q12 = {f"selector_prepared_{s}": difference(2, s, 0) for s in (0, 1)}
    return {
        "coin_dropout": {"D": coin["selector_prepared_1"], "by_selector": coin, "matched_pairs": pairs},
        "q12_correlation": {"G_by_selector": q12},
        "shots_per_preparation": {"".join(map(str, p)): c[1] for p, c in sorted(cells.items())},
    }


def classify_large(value: float, se: float) -> bool:
    return value >= MODEL_SIZE - Z_RESOLVE * se and value >= Z_RESOLVE * se


def classify_small(values: list[tuple[float, float]]) -> bool:
    return all(abs(v) + Z_RESOLVE * se < SMALL for v, se in values)


def joint_classes(joint: dict[str, Any]) -> dict[str, Any]:
    d = joint["coin_dropout"]
    coin_stats = [(v["value"], v["se"]) for v in d["by_selector"].values()]
    q12_stats = [(v["value"], v["se"]) for v in joint["q12_correlation"]["G_by_selector"].values()]
    informative = all(se <= JOINT_SE_LIMIT for _, se in coin_stats + q12_stats)
    large_d = classify_large(d["D"]["value"], d["D"]["se"])
    coin_class = "large" if large_d else "small" if classify_small(coin_stats) else "mid"
    q12_class = (
        "large"
        if any(classify_large(v, se) for v, se in q12_stats)
        else "small"
        if classify_small(q12_stats)
        else "mid"
    )
    return {"coin_dropout": coin_class, "q12_correlation": q12_class, "informative": informative}


def parse_file(name: str) -> tuple[str, str | None, int | None]:
    """(kind, template, coin) of a circuit file name: base, twin, joint or readout."""
    if name.startswith("readout"):
        return "readout", None, None
    if name.startswith("joint-"):
        return "joint", None, None
    stem = name.removesuffix(".cq")
    if "-coin" in stem:
        template, _, coin = stem.partition("-coin")
        return "twin", template, int(coin)
    return "base", stem, None


def batch_estimates(
    shots: dict[str, list[str]], manifest: dict[str, Any]
) -> tuple[dict[str, dict[str, list[tuple[float, float]]]], dict[str, dict[str, dict[str, Any]]]]:
    """Per template and kind, the (value, se) of every batch, and the per-batch template rows (readout-corrected
    statistics) of the base circuits."""
    templates = manifest["templates"]
    register = [int(q) for q in manifest["register"]]
    brackets = {
        batch: asg
        for batch in sorted({k.split("/")[0] for k in shots})
        if (asg := cc.batch_assignment(shots, batch, register)) is not None
    }
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {t: {"base": [], "twin": []} for t in templates}
    detail: dict[str, dict[str, dict[str, Any]]] = {t: {} for t in templates}
    twins: dict[tuple[str, str], dict[int, list[str]]] = {}
    for key in sorted(shots):
        batch, name = key.split("/")
        kind, template, coin = parse_file(name)
        if kind == "base" and template is not None:
            t = templates[template]
            counts = cc.coin_counts(shots[key], t["roles"])
            plus, minus = cc.piles(counts)
            rows[template]["base"].append(pca.selector_stat(plus, minus))
            asg = brackets.get(batch)
            matrix = None if asg is None else cc.readout_matrix(asg, t["roles"])
            detail[template][batch] = cc.template_row(template, t, counts, matrix, np.array(t["ideal_c"]))
        elif kind == "twin" and template is not None and coin is not None:
            twins.setdefault((batch, template), {})[coin] = shots[key]
    for (batch, template), pair in sorted(twins.items()):
        if set(pair) != {0, 1}:
            raise ValueError(f"{batch} holds one coin twin of {template}")
        qubit = templates[template]["roles"]["selector"]
        rates, variances = [], []
        for coin in (1, 0):
            n = len(pair[coin])
            p = sum(1 for s in pair[coin] if pca.bit(s, qubit) == 0) / n
            rates.append(p)
            variances.append(p * (1 - p) / n)
        rows[template]["twin"].append((rates[0] - rates[1], math.sqrt(sum(variances))))
    return rows, detail


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """Preregistered decision from shot lists keyed "batch/file"; `manifest` is any batch's cases.json."""
    rows, detail = batch_estimates(shots, manifest)
    for template in TEMPLATES:
        for kind in ("base", "twin"):
            if len(rows[template][kind]) != REPLICATES:
                raise ValueError(f"{template} holds {len(rows[template][kind])} {kind} batches, not {REPLICATES}")
    decision = decide_estimates(rows)
    joint = joint_statistics(shots, manifest)
    classes = joint_classes(joint)
    register = [int(q) for q in manifest["register"]]
    drift = pcs.reference_drift(
        [(k.split("/")[0], k.split("/")[1], v) for k, v in shots.items() if k.split("/")[1] in pcs.READOUT_KIND],
        register,
    )
    order: dict[str, str] | None = None
    if executed is not None:
        order = {}
        for key in sorted(executed, key=lambda k: executed[k]):
            batch, fname = key.split("/")
            order[batch] = order.get(batch, "") + fname.removesuffix(".cq") + " "
    return {
        "batch_contrasts": {t: {k: [list(x) for x in v] for k, v in rows[t].items()} for t in TEMPLATES},
        "template_rows": detail,
        "decision": decision,
        "calibration": {"statistics": joint, "classes": classes, "role": "secondary, terminal-assignment context"},
        "drift_covariate": {"references": drift},
        "executed_order": order,
    }


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series. A Tuna-17 series that holds fewer batches than the case reports its
    batch list only; a QX series reports the control verdict a Tuna-17 submission needs."""
    data = pca.read_series(run_dirs, case_root, series_of, "data", BATCH_FIELDS, pcs.load_run)
    shared, shots, executed = data["shared"], data["shots"], data["executed"]
    emulator = shared["backend_type_id"] == 1
    expected = sorted(r["batch"] for r in batch_rows(QX_SERIES if emulator else TUNA_SERIES))
    held = sorted({k.split("/")[0] for k in shots})
    head: dict[str, Any] = {
        "schema": ANALYSIS_SCHEMA,
        "claim_kind": CONTROL_KIND if emulator else "hardware acquisition",
        "backend": shared["backend"],
        "batch_cases_sha256": data["digests"],
    }
    if emulator:
        head["qx_control"] = pca.control_report(data["arms"], cc.coin_counts)
    if held != expected:
        return {**head, "complete": False, "batches": held}
    if emulator:
        return {**head, "complete": True}
    return {**head, "complete": True, **evaluate(shots, shared, executed)}


def sanity(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Bind each collected batch to the series case and report the readout drift between brackets."""
    loaded = []
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        case_batch = None if case_root is None else case_root / series_of(run_dir) / cases["batch"]
        loaded.append(pcs.load_run(run_dir, case_batch))
    batches = [r["cases"]["batch"] for r in loaded]
    if len(set(batches)) != len(batches):
        raise SystemExit(f"a batch appears twice in {batches}")
    paired = [r for r in loaded if any(row["kind"] == "readout" for row in r["cases"]["circuits"])]
    return {"batches": batches, "drift": pcs.runs_drift(paired) if paired else None}


# Self-test ------------------------------------------------------------------------------------------------------


def coin_mask(ideal: np.ndarray) -> np.ndarray:
    """Uniform law over the outcomes that carry the coin value of a coin-fixed ideal law."""
    coin = np.array([(i >> COIN) & 1 for i in range(NOUT)])
    value = 1 if ideal[coin == 1].sum() > 0.5 else 0
    mask = (coin == value).astype(float)
    return mask / mask.sum()


def synthetic_series(
    files: dict[str, str],
    manifest: dict[str, Any],
    *,
    retention: float = 0.5,
    offsets: dict[str, float] | None = None,
    twin_offsets: dict[str, float] | None = None,
    dropout: float = 0.0,
    flip: float = 0.0,
    assignment: dict[int, tuple[float, float]] | None = None,
) -> dict[str, list[str]]:
    """Shot lists of a device at expected counts (largest remainder, no random draw). Every base circuit contracts by
    `retention` toward the uniform law, a twin toward the uniform law over its own coin value; `offsets` and
    `twin_offsets` set a raw selector contrast on a base circuit and on a coin-1 twin by an arm-asymmetric weight;
    `dropout` and `flip` act on the selector of every circuit and calibration preparation as the sized readout
    models."""
    register = [int(q) for q in manifest["register"]]
    asg = assignment or {q: (0.02 + 0.01 * n, 0.04 + 0.01 * n) for n, q in enumerate(register)}
    out: dict[str, list[str]] = {}
    for rel in files:
        if not rel.endswith(".cq"):
            continue
        batch, fname = rel.split("/")
        cases = json.loads(files[f"{batch}/cases.json"])
        total = cases["shots"]
        kind, template, coin = parse_file(fname)
        if kind == "readout":
            excited = fname == "readout-1.cq"
            law = np.ones(1)
            for q in reversed(register):
                e01, e10 = asg[q]
                p1 = 1.0 - e10 if excited else e01
                law = np.kron(law, np.array([1.0 - p1, p1]))
            roles = {f"q{n}": q for n, q in enumerate(register)}
            out[rel] = cc.place_counts(cc.largest_remainder(law, total), tuple(roles), roles, NQUBITS)
            continue
        if kind == "joint":
            prep = tuple(int(c) for c in fname.removeprefix("joint-").removesuffix(".cq"))
            counts = cc.largest_remainder(joint_law(prep, asg, dropout, flip), total)
            out[rel] = cc.place_counts(counts, tuple(JOINT_QUBITS), dict(JOINT_QUBITS), NQUBITS)
            continue
        if template is None:
            raise ValueError(f"{fname} names no template")
        row = next(r for r in cases["circuits"] if r["file"] == fname)
        ideal = np.array(row["ideal"])
        if kind == "base":
            law = retention * ideal + (1 - retention) / ideal.size
            weight = 2.0 * (offsets or {}).get(template, 0.0)
            if weight:
                plus = np.arange(NOUT) >= HALF
                zero = (np.arange(NOUT) % HALF) < HALF // 2
                law = law * np.where(plus & zero, 1 + weight, np.where(plus, 1 - weight, 1.0))
        else:
            law = retention * ideal + (1 - retention) * coin_mask(ideal)
            weight = 2.0 * (twin_offsets or {}).get(template, 0.0)
            if weight and coin == 1:
                zero = (np.arange(NOUT) % HALF) < HALF // 2
                law = law * np.where(zero, 1 + weight, 1 - weight)
        roles = cases["templates"][template]["roles"]
        if dropout:
            law = selector_dropout(COIN, 1, dropout) @ law
        if flip:
            q12 = KEYS.index(next(k for k, q in roles.items() if q == JOINT_QUBITS["q12"]))
            law = selector_flip(q12, 0, flip) @ law
        matrix = cc.confusion([asg[roles[k]] for k in KEYS])
        out[rel] = cc.place_counts(cc.largest_remainder(matrix @ law, total), KEYS, roles, NQUBITS)
    return out


WORLDS: dict[str, dict[str, Any]] = {
    "absent": {},
    "over_rotation": {"offsets": {"b0": 0.0164}, "twin_offsets": {"b0": 0.0166}},
    "coin_dropout": {"dropout": 0.0362},
    "q12_correlation": {"flip": 0.036},
    "superposition_only": {"offsets": {t: 0.02 for t in TEMPLATES}},
}
WORLD_LABELS = {
    "absent": "offset_absent",
    "over_rotation": "zero",
    "coin_dropout": "b0_like",
    "q12_correlation": "zero",
    "superposition_only": "superposition_only",
}


def self_test() -> str:
    """The replay is byte-equal, every selected block ends on its pin with the ideal law of the block, every twin
    removes exactly the coin Hadamard, the series holds its jobs within the platform limits, and a device of each world
    reads its preregistered row."""
    digest = replay_check()
    parts = []
    for mode in PIN_MODES:
        for name, _ in LOW_CZ:
            entry = routed(mode, name)
            n, layout = SELECTION[(mode, name)]
            if entry["transpiler_seed"] != draw_values()[n] or entry["initial_layout"] != list(layout):
                raise RuntimeError(f"{mode} {name}: the entry departs from SELECTION")
            final = [reference()["region"].index(entry["roles"][k]) for k in KEYS]
            if not pinned(mode, tuple(final)) or (mode == "roles" and final != want_layout()):
                raise RuntimeError(f"{mode} {name}: the routed circuit does not meet its pin")
            if pcb.contrast_restriction_error(BLOCKS[name]) > 1e-12:
                raise RuntimeError(f"{name}: the block contrast departs from the six-qubit law")
            parts.append(f"{mode}/{name} {entry['cz']} CZ")
    built = build()
    files = built[TUNA_SERIES]
    rows = batch_rows(TUNA_SERIES)
    sizes = [len(json.loads(files[f"{r['batch']}/cases.json"])["circuits"]) for r in rows]
    if any(s > 3 for s in sizes):
        raise RuntimeError(f"batch sizes {sizes} exceed the hardware limit of three circuits")
    for name in TEMPLATES:
        for value in (0, 1):
            twin = twin_entry(name, value)
            if twin["removed"] != ["rz", "sx", "rz"] or twin["cz"] != series_plan()["templates"][name]["cz"]:
                raise RuntimeError(f"{name} coin {value}: the twin changes more than the coin Hadamard")
    manifest = json.loads(files["batch-00/cases.json"])
    for world, kwargs in WORLDS.items():
        result = evaluate(synthetic_series(files, manifest, **kwargs), manifest)
        if result["decision"]["label"] != WORLD_LABELS[world]:
            raise RuntimeError(f"world {world} reads {result['decision']['label']!r}: {result['decision']['numbers']}")
    return (
        f"b0 replay {digest[:12]} byte-equal; "
        + ", ".join(parts)
        + f"; series of {len(rows)} batches {sizes}; every twin removes only the coin Hadamard; each of {len(WORLDS)} "
        "simulated worlds reads its preregistered row"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--select", action="store_true")
    mode.add_argument("--replay", action="store_true")
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--operating-characteristics", action="store_true")
    mode.add_argument("--qx-conformance", type=Path)
    mode.add_argument("--sanity", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.select:
        print(json.dumps(select(), indent=1, sort_keys=True))
    elif args.replay:
        print(f"b0 replay equals the retained b0.cq: sha256 {replay_check()}")
    elif args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.operating_characteristics:
        print(json.dumps(predictions()["operating_characteristics"], indent=1, sort_keys=True))
    elif args.qx_conformance:
        print(json.dumps(cc.qx_conformance(args.qx_conformance), indent=1))
    elif args.sanity:
        print(json.dumps(sanity(args.sanity), indent=1, sort_keys=True))
    elif args.analyze:
        if args.out is None:
            parser.error("--analyze needs --out")
        args.out.write_text(
            json.dumps(analyze(args.analyze), indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.out}")
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    sys.exit(main())
