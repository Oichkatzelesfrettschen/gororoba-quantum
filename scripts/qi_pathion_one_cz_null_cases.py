"""Routing, replay and decision gate of the Tuna-17 low-CZ null-block case: the decider for ledger row A5-186.

The coin series' null block b0 = e1 + e17 (coset 0 of the basis 16, 1, 2; 21 routed CZ) read a raw selector
contrast of +0.0164 +- 0.0039 where every arm-symmetric product readout and every unital or relaxation channel
gives 0, and one coherent X90 over-rotation of about +0.03 rad reproduces it (section C2 of mechanisms.md in
docs/evidence/pathion-kernel-map/conjectures/). The decider is a null block of the same operand with few CZ
(coset 4, 8 or 12), on the same five physical qubits: an over-rotation then predicts selector 0 and an arm-
asymmetric or correlated selector readout, shared with b0, predicts about the b0 value. This module builds that
block from qi_pathion_coset_coin_cases.py by import, which keeps its bytes, and states what it routes to.

Replay. b0 is the coin series' own compile (its region, its transpiler seed and role map read from the retained
batch-02 cases.json, whose b0.cq digest COIN_PINS pins); replay_text() regenerates its circuit bytes and
--replay refuses any difference from the retained file.

Routing. The coin template of each low-CZ block compiles on b0's region from each of the 120 initial layouts of
the five logical bits at SEEDS_PER_BLOCK transpiler seeds taken from the retained ANU QRNG draw DRAW (block
slice index * SEEDS_PER_BLOCK to (index + 1) * SEEDS_PER_BLOCK - 1, in the order of LOW_CZ), at the coin series'
optimization level and basis. Two pins are read. "roles" keeps the whole role map of b0 at measurement (d0 q12,
d1 q4, d2 q11, selector q8, coin q2), the brief's "same five physical qubits with the same role map";
"selector_coin" keeps only the selector on q8 and the coin on q2. Each block keeps the fewest-CZ candidate that
meets the pin, ties to the lowest draw index and then the least layout; SELECTION records the winners and
--select repeats the search and refuses a table that differs. A coin block compiles to 3 CZ at all-to-all
connectivity (the coin-free IBM k4 block holds 1); the region's star at q8 plus the edge (2, 4) routes it to 4
CZ unpinned, 6 CZ under "selector_coin" and 12 CZ under "roles".

Decision gate. docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.py runs every mechanism of
c2_tuna_mech.py on these routed circuits. The low-CZ block decides only if an X90 over-rotation of 0.03 rad
gives a selector contrast of at most 0.004 in magnitude on every block while a selector readout sized to give b0
+0.0164 gives at least 0.012. Simulated on the routed circuits, every candidate of the search that meets the
"roles" pin (two distinct circuits per block, 12 and 15 CZ) gives an over-rotation selector contrast of 0.0279
to 0.0549 in magnitude (b0: +0.0167 and -0.0092), so the block does not decide and the series is not built. The
"selector_coin" pin gives 0 and separates only a coin-conditioned (arm-asymmetric) readout offset, since a
readout correlation of the selector with q12 predicts 0 there too. The series design, the QX and Ry controls and
the analysis are not built.

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_cases.py (--select | --replay | --self-test)
Bit strings put qubit 0 at the rightmost character.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_cases as blk  # noqa: E402
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


def self_test() -> str:
    """The replay is byte-equal, every selected block ends on its pin with the ideal law of the block, and the draw
    holds the values the routing search reads."""
    digest = replay_check()
    want = want_layout()
    parts = []
    for mode in PIN_MODES:
        for name, _ in LOW_CZ:
            entry = routed(mode, name)
            n, layout = SELECTION[(mode, name)]
            if entry["transpiler_seed"] != draw_values()[n] or entry["initial_layout"] != list(layout):
                raise RuntimeError(f"{mode} {name}: the entry departs from SELECTION")
            final = [reference()["region"].index(entry["roles"][k]) for k in KEYS]
            if not pinned(mode, tuple(final)) or (mode == "roles" and final != want):
                raise RuntimeError(f"{mode} {name}: the routed circuit does not meet its pin")
            if pcb.contrast_restriction_error(BLOCKS[name]) > 1e-12:
                raise RuntimeError(f"{name}: the block contrast departs from the six-qubit law")
            parts.append(f"{mode}/{name} {entry['cz']} CZ")
    return f"b0 replay {digest[:12]} byte-equal; " + ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--select", action="store_true")
    mode.add_argument("--replay", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.select:
        print(json.dumps(select(), indent=1, sort_keys=True))
    elif args.replay:
        print(f"b0 replay equals the retained b0.cq: sha256 {replay_check()}")
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    sys.exit(main())
