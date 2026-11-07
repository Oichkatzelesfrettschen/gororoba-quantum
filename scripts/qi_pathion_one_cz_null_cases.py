"""Tuna-17 case for the null block's selector offset (row A5-186): joint readout, 6-CZ blocks, QX twin.

The coin series' null block b0 = e1 + e17 (coset 0 of the basis 16, 1, 2; 21 routed CZ) read a raw selector
contrast of +0.0164 +- 0.0039 where every arm-symmetric product readout and every unital or relaxation channel
gives 0. Three hypotheses reproduce it (section C2 of mechanisms.md in docs/evidence/pathion-kernel-
map/conjectures/, c2_one_cz_mech.txt): a coherent X90 over-rotation of about +0.03 rad, a selector dropout
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

Series. The series pin is "selector_coin". The Tuna-17 series holds seven batches: three of joint readout
characterization (the eight X-gate preparations of q2, q8 and q12 with every other register qubit in |0>,
JOINT_SHOTS each) and four of [readout-0, template, readout-1] for b0, k4, k8 and k12 at SHOTS. The QX twin
holds the four templates in one batch. preregistered() and DECISIONS state the rules; evaluate() reads the
collected shot lists through qi_records (pca.read_series) and applies them: the control (b0 above 3 se), the
class of the 6-CZ mean against 0 and against b0, the coin and q12 classes of the joint misassignment, and the
decision of their combination. A readout drift between brackets is recorded and stops nothing.

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
SCHEMA = "qi-pathion-one-cz-null-cases-v1"
ANALYSIS_SCHEMA = "qi-pathion-one-cz-null-analysis-v1"
SHOTS = 65536
JOINT_SHOTS = 32768
QX_SHOTS = 2048
QX_QUBITS = 10
# Physical qubits of the joint readout characterization: the coin and the selector of every template, and the qubit that
# carries d0 in b0 and d1 in the 6-CZ blocks.
JOINT_QUBITS = {"coin": 2, "selector": 8, "q12": 12}
JOINT_PREPS = tuple(itertools.product((0, 1), repeat=3))
JOINT_BATCH_SIZES = (3, 3, 2)
# Sized models of the mechanism simulation (c2_one_cz_mech.txt): each gives b0 a raw selector contrast of +0.0164.
MODEL_SIZE = 0.036
SMALL = 0.012
# A joint statistic informs only at a standard error that lets three of them stay inside SMALL; a template selector
# contrast only at 1.15 times its design value 1 / sqrt(SHOTS).
JOINT_SE_LIMIT = SMALL / Z_RESOLVE
SELECTOR_SE_LIMIT = 0.0045
# Raw selector contrast of b0 and of a 6-CZ block under each hypothesis, from the simulation log. The over-rotation
# and the q12 correlation leave a 6-CZ block at 0; the coin-conditioned dropout reads the b0 value on it.
PREDICTED = {
    "over_rotation": {"b0": 0.0167, "six_cz": 0.0},
    "coin_dropout": {"b0": 0.0164, "six_cz": 0.0164},
    "q12_correlation": {"b0": 0.0164, "six_cz": 0.0},
}
CONTROL_KIND = pcs.CONTROL_KIND


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


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series: joint characterizations first (Tuna), then each template alone with its readout pair."""
    if series_name == QX_SERIES:
        return [{"batch": "batch-00", "templates": list(TEMPLATES), "joint": [], "readout": False}]
    rows: list[dict[str, Any]] = []
    start = 0
    for size in JOINT_BATCH_SIZES:
        rows.append(
            {
                "batch": f"batch-{len(rows):02d}",
                "templates": [],
                "joint": list(JOINT_PREPS[start : start + size]),
                "readout": False,
            }
        )
        start += size
    for name in TEMPLATES:
        rows.append({"batch": f"batch-{len(rows):02d}", "templates": [name], "joint": [], "readout": True})
    return rows


def preregistered() -> dict[str, str]:
    z = Z_RESOLVE
    return {
        "control": f"b0 raw selector contrast above {z} standard errors, else the offset is absent and nothing about "
        "its mechanism is decided",
        "six_cz": f"inverse-variance mean s of the raw selector contrasts of k4, k8 and k12 with b0's contrast s0: "
        f"zero when |s| within {z} se of 0 and (s - s0) beyond {z} combined se, b0-like when (s - s0) within {z} "
        f"combined se and |s| beyond {z} se, else unresolved",
        "coin_dropout": f"D = misassignment of a prepared selector 1 with the coin prepared 1 minus with the coin "
        f"prepared 0: large when D >= {MODEL_SIZE} - {z} se and D >= {z} se; small when |D| + {z} se < {SMALL} for a "
        "prepared selector 0 and for a prepared selector 1",
        "q12_correlation": "G = misassignment of the selector with q12 prepared 0 minus with q12 prepared 1, the "
        "larger of the values at a prepared selector 0 and 1: large when "
        f"G >= {MODEL_SIZE} - {z} se and G >= {z} se; small when |G| + {z} se < {SMALL} at both prepared selector "
        "values",
        "decision": "the combination of the control, six_cz, coin_dropout and q12_correlation classes read from "
        "DECISIONS; every other combination is unresolved",
        "qx": "every template within twice the sampling floor of its ideal law",
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
        shots = QX_SHOTS if not hardware else JOINT_SHOTS if row["joint"] else SHOTS
        texts: dict[str, str] = {}
        circuits: list[dict[str, Any]] = []
        if row["readout"]:
            texts["readout-0.cq"] = cc.readout_text(nqubits, False, register)
            circuits.append({"file": "readout-0.cq", "kind": "readout"})
        for prep in row["joint"]:
            texts[joint_file(prep)] = joint_text(nqubits, prep)
            circuits.append(
                {
                    "file": joint_file(prep),
                    "kind": "joint",
                    "prep": dict(zip(JOINT_QUBITS, prep, strict=True)),
                }
            )
        for name in row["templates"]:
            t = plan["templates"][name]
            texts[f"{name}.cq"] = cc.circuit_text(t["circuit"], place, nqubits, template_note(name, t, region))
            circuits.append(
                {
                    "file": f"{name}.cq",
                    "kind": "data",
                    "template": name,
                    "ideal": [round(float(x), 12) for x in t["ideal"]],
                }
            )
        if row["readout"]:
            texts["readout-1.cq"] = cc.readout_text(nqubits, True, register)
            circuits.append({"file": "readout-1.cq", "kind": "readout"})
        for r in circuits:
            r["sha256"] = hashlib.sha256(texts[r["file"]].encode()).hexdigest()
            files[f"{row['batch']}/{r['file']}"] = texts[r["file"]]
        manifest = {"schema": SCHEMA, **common, "shots": shots, "batch": row["batch"], "circuits": circuits}
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "files": [r["file"] for r in circuits]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-pathion-one-cz-null-series-v1", "backend": backend["identifier"], "batches": batches},
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


def coin_timing() -> dict[str, Any]:
    """Execution seconds per shot of the coin series' 65536-shot Tuna-17 jobs, from the retained results.json files."""
    rates = []
    for batch in range(4):
        run = ROOT / "results/quantum_inspire/runs" / f"2026-11-07T001031Z-{cc.TUNA_SERIES}-batch-{batch:02d}"
        for row in json.loads((run / "results.json").read_text(encoding="utf-8"))["jobs"]:
            result = row["results"][0]
            if result["shots_done"] == SHOTS:
                rates.append(result["execution_time_in_seconds"] / SHOTS)
    if not rates:
        raise ValueError("the retained coin series holds no 65536-shot job")
    return {"jobs": len(rates), "seconds_per_shot_min": min(rates), "seconds_per_shot_max": max(rates)}


def design() -> dict[str, Any]:
    """Expected standard errors and seconds of the series: the selector contrast of a template at SHOTS, the joint
    statistics at JOINT_SHOTS under the retained readout rates of the selector, and the Tuna-17 seconds."""
    e01, e10 = cc.retained_readout(reference()["region"])[JOINT_QUBITS["selector"]]
    joint_se = {s: math.sqrt(p * (1 - p) / JOINT_SHOTS) for s, p in ((0, e01), (1, e10))}
    timing = coin_timing()
    jobs_joint, jobs_data = len(JOINT_PREPS), 3 * len(TEMPLATES)
    shots_total = jobs_joint * JOINT_SHOTS + 2 * len(TEMPLATES) * SHOTS + len(TEMPLATES) * SHOTS
    return {
        "selector_se": 1.0 / math.sqrt(SHOTS),
        "selector_se_limit": SELECTOR_SE_LIMIT,
        "joint_se": {f"selector_prepared_{s}": round(v, 6) for s, v in joint_se.items()},
        "joint_se_limit": JOINT_SE_LIMIT,
        "model_size_in_se": {f"selector_prepared_{s}": round(MODEL_SIZE / v, 1) for s, v in joint_se.items()},
        "retained_selector_readout_e01_e10": [round(e01, 4), round(e10, 4)],
        "jobs": jobs_joint + jobs_data,
        "batches": len(batch_rows(TUNA_SERIES)),
        "shots_total": shots_total,
        "execution_seconds_range": [
            round(shots_total * timing["seconds_per_shot_min"], 1),
            round(shots_total * timing["seconds_per_shot_max"], 1),
        ],
        "pause_seconds_per_batch": 30,
        "coin_series_timing": timing,
    }


# Decisions: (six_cz class, coin_dropout class, q12_correlation class) -> (outcome, effect on ledger row A5-186).
DECISIONS: dict[tuple[str, str, str], tuple[str, str]] = {
    ("zero", "small", "small"): (
        "over-rotation supported: the 6-CZ blocks read zero and both readout offsets are excluded",
        "survives; the readout alternative is excluded and the falsifier (6-CZ blocks at zero) is unmet",
    ),
    ("b0-like", "large", "small"): (
        "coin-conditioned selector dropout supported: the 6-CZ blocks read the b0 value and the joint readout shows "
        "the dropout",
        "refuted as an over-rotation: the offset is an arm-asymmetric readout effect",
    ),
    ("b0-like", "large", "mid"): (
        "coin-conditioned selector dropout supported: the 6-CZ blocks read the b0 value and the joint readout shows "
        "the dropout; the q12 correlation is neither shown nor excluded",
        "refuted as an over-rotation: the offset is an arm-asymmetric readout effect",
    ),
    ("zero", "small", "large"): (
        "q12 correlation supported: the 6-CZ blocks read zero and the joint readout shows the q12 correlation",
        "weakened: a measured readout correlation of the needed size explains the offset without a coherent error",
    ),
    ("zero", "mid", "large"): (
        "q12 correlation supported: the 6-CZ blocks read zero and the joint readout shows the q12 correlation",
        "weakened: a measured readout correlation of the needed size explains the offset without a coherent error",
    ),
    ("b0-like", "small", "small"): (
        "neither a coherent over-rotation nor a measured readout offset: the 6-CZ blocks read the b0 value and the "
        "joint readout excludes both readout models",
        "refuted as stated: the over-rotation predicts zero on the 6-CZ blocks; the mechanism stays open",
    ),
}
UNRESOLVED = ("unresolved: the combination matches no preregistered row", "unchanged; the numbers are reported")


def predictions() -> dict[str, Any]:
    return {
        "model": "raw selector contrast of b0 and of a 6-CZ block under each hypothesis, and the size of the joint "
        "readout effect each hypothesis needs, from docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt",
        "predicted_selector_contrast": PREDICTED,
        "joint_effect": {"coin_dropout": MODEL_SIZE, "q12_correlation": MODEL_SIZE, "readout_excluded_below": SMALL},
        "design": design(),
        "preregistered": preregistered(),
        "decisions": [{"if": list(k), "outcome": v[0], "a5_186": v[1]} for k, v in DECISIONS.items()],
    }


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


def check(directory: Path) -> None:
    """The case directories hold exactly the built files; CASE.md, the hand-written case, is the one extra file."""
    built = build()
    built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(), indent=1, sort_keys=True) + "\n"
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
    """Misassignment of the selector (q8) conditioned on the prepared coin (q2) and on the prepared q12.

    e(s | v = a) is the fraction of shots with q8 prepared s, qubit v prepared a (the other joint qubit pooled) that
    read q8 differently. D is e(1 | coin = 1) - e(1 | coin = 0), the dropout of a prepared 1 conditioned on the coin;
    G(s) is e(s | q12 = 0) - e(s | q12 = 1)."""
    qubits = manifest["joint_qubits"]
    cells: dict[tuple[int, ...], tuple[int, int]] = {}
    for key, listed in shots.items():
        name = key.split("/")[1]
        if not name.startswith("joint-"):
            continue
        prep = tuple(int(c) for c in name.removeprefix("joint-").removesuffix(".cq"))
        selector = prep[1]
        wrong = sum(1 for s in listed if pca.bit(s, qubits["selector"]) != selector)
        cells[prep] = (wrong, len(listed))
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

    coin = {f"selector_prepared_{s}": difference(0, s, 1) for s in (0, 1)}
    q12 = {f"selector_prepared_{s}": difference(2, s, 0) for s in (0, 1)}
    return {
        "coin_dropout": {"D": coin["selector_prepared_1"], "by_selector": coin},
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
    coin_class = (
        "large" if classify_large(d["D"]["value"], d["D"]["se"]) else "small" if classify_small(coin_stats) else "mid"
    )
    q12_class = (
        "large"
        if any(classify_large(v, se) for v, se in q12_stats)
        else "small"
        if classify_small(q12_stats)
        else "mid"
    )
    return {"coin_dropout": coin_class, "q12_correlation": q12_class, "informative": informative}


def six_cz_class(blocks: dict[str, tuple[float, float]], b0: tuple[float, float]) -> dict[str, Any]:
    s, se = pooled([blocks[name] for name, _ in LOW_CZ])
    z_zero = s / se
    gap, gap_se = s - b0[0], math.hypot(se, b0[1])
    z_b0 = gap / gap_se
    zero = abs(z_zero) <= Z_RESOLVE and abs(z_b0) >= Z_RESOLVE
    like = abs(z_b0) <= Z_RESOLVE and abs(z_zero) >= Z_RESOLVE
    return {
        "mean": s,
        "se": se,
        "z_against_zero": z_zero,
        "z_against_b0": z_b0,
        "class": "zero" if zero else "b0-like" if like else "unresolved",
    }


def decide(control: bool, informative: bool, six: str, coin: str, q12: str) -> dict[str, Any]:
    """The preregistered decision of the four classes."""
    if not control:
        return {
            "outcome": "offset absent: b0 no longer reads a positive selector contrast at the control level; nothing "
            "about the mechanism is decided",
            "a5_186": "unchanged",
            "decided": False,
        }
    if not informative:
        return {"outcome": "uninformative: a standard error exceeds its limit", "a5_186": "unchanged", "decided": False}
    outcome, effect = DECISIONS.get((six, coin, q12), UNRESOLVED)
    return {"outcome": outcome, "a5_186": effect, "decided": (six, coin, q12) in DECISIONS}


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """Preregistered decisions from shot lists keyed "batch/file"; `manifest` is any batch's cases.json."""
    templates = manifest["templates"]
    register = [int(q) for q in manifest["register"]]
    brackets = {
        batch: asg
        for batch in sorted({k.split("/")[0] for k in shots})
        if (asg := cc.batch_assignment(shots, batch, register)) is not None
    }
    rows: dict[str, dict[str, Any]] = {}
    for name, t in templates.items():
        key = cc.template_file(shots, name)
        asg = brackets.get(key.split("/")[0])
        matrix = None if asg is None else cc.readout_matrix(asg, t["roles"])
        rows[name] = cc.template_row(name, t, cc.coin_counts(shots[key], t["roles"]), matrix, np.array(t["ideal_c"]))
    selector = {name: (rows[name]["selector_contrast"], rows[name]["selector_se"]) for name in templates}
    b0 = selector["b0"]
    control = b0[0] >= Z_RESOLVE * b0[1]
    six = six_cz_class({name: selector[name] for name, _ in LOW_CZ}, b0)
    joint = joint_statistics(shots, manifest)
    classes = joint_classes(joint)
    informative = classes["informative"] and all(se <= SELECTOR_SE_LIMIT for _, se in selector.values())
    decision = decide(control, informative, six["class"], classes["coin_dropout"], classes["q12_correlation"])
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
        "templates": rows,
        "control": {"b0_selector_contrast": b0[0], "se": b0[1], "z": b0[0] / b0[1], "positive_at_3_se": control},
        "six_cz": six,
        "joint": joint,
        "classes": {"six_cz": six["class"], **classes},
        "decision": {**decision, "informative": informative},
        "drift_covariate": {"references": drift},
        "executed_order": order,
    }


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series. A Tuna-17 series that holds fewer batches than the case reports its
    batch list only; a QX series reports the control verdict a Tuna-17 submission needs."""
    data = pca.read_series(run_dirs, case_root, series_of, "data", ("batch", "circuits", "shots"), pcs.load_run)
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

SELECTOR = KEYS.index("selector")
COIN = KEYS.index("coin")


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


def synthetic_series(
    files: dict[str, str],
    plan: dict[str, Any],
    manifest: dict[str, Any],
    *,
    retention: float = 0.5,
    offsets: dict[str, float] | None = None,
    dropout: float = 0.0,
    flip: float = 0.0,
    assignment: dict[int, tuple[float, float]] | None = None,
) -> dict[str, list[str]]:
    """Shot lists of a device at expected counts (largest remainder, no random draw): every template contracts by
    `retention`; `offsets` sets a raw selector contrast on a template by an arm-asymmetric weight; `dropout` and `flip`
    act on the selector of every template and of every joint preparation as the sized readout models."""
    register = [int(q) for q in manifest["register"]]
    asg = assignment or {q: (0.02 + 0.01 * n, 0.04 + 0.01 * n) for n, q in enumerate(register)}
    out: dict[str, list[str]] = {}
    for rel in files:
        if not rel.endswith(".cq"):
            continue
        batch, fname = rel.split("/")
        cases = json.loads(files[f"{batch}/cases.json"])
        total = cases["shots"]
        if fname.startswith("readout"):
            excited = fname == "readout-1.cq"
            law = np.ones(1)
            for q in reversed(register):
                e01, e10 = asg[q]
                p1 = 1.0 - e10 if excited else e01
                law = np.kron(law, np.array([1.0 - p1, p1]))
            roles = {f"q{n}": q for n, q in enumerate(register)}
            out[rel] = cc.place_counts(cc.largest_remainder(law, total), tuple(roles), roles, NQUBITS)
        elif fname.startswith("joint"):
            prep = tuple(int(c) for c in fname.removeprefix("joint-").removesuffix(".cq"))
            counts = cc.largest_remainder(joint_law(prep, asg, dropout, flip), total)
            out[rel] = cc.place_counts(counts, tuple(JOINT_QUBITS), dict(JOINT_QUBITS), NQUBITS)
        else:
            template = fname.removesuffix(".cq")
            ideal = plan["templates"][template]["ideal"]
            law = retention * ideal + (1 - retention) / ideal.size
            weight = 2.0 * (offsets or {}).get(template, 0.0)
            if weight:
                plus = np.arange(NOUT) >= HALF
                zero = (np.arange(NOUT) % HALF) < HALF // 2
                law = law * np.where(plus & zero, 1 + weight, np.where(plus, 1 - weight, 1.0))
            roles = cases["templates"][template]["roles"]
            if dropout:
                law = selector_dropout(COIN, 1, dropout) @ law
            if flip:
                law = (
                    selector_flip(KEYS.index(next(k for k, q in roles.items() if q == JOINT_QUBITS["q12"])), 0, flip)
                    @ law
                )
            matrix = cc.confusion([asg[roles[k]] for k in KEYS])
            out[rel] = cc.place_counts(cc.largest_remainder(matrix @ law, total), KEYS, roles, NQUBITS)
    return out


WORLDS: dict[str, dict[str, Any]] = {
    "absent": {},
    "over_rotation": {"offsets": {"b0": 0.0164}},
    "coin_dropout": {"dropout": 0.0362},
    "q12_correlation": {"flip": 0.036},
    "offset_without_readout": {"offsets": {"b0": 0.0164, "k4": 0.0164, "k8": 0.0164, "k12": 0.0164}},
}
WORLD_OUTCOMES = {
    "absent": "offset absent",
    "over_rotation": "over-rotation supported",
    "coin_dropout": "coin-conditioned selector dropout supported",
    "q12_correlation": "q12 correlation supported",
    "offset_without_readout": "neither a coherent over-rotation nor a measured readout offset",
}


def self_test() -> str:
    """The replay is byte-equal, every selected block ends on its pin with the ideal law of the block, the series
    holds its jobs within the platform limits, and a device of each world reads its preregistered outcome."""
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
    sizes = [
        len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) for n in range(len(batch_rows(TUNA_SERIES)))
    ]
    if any(s > 3 for s in sizes) or sum(1 for s in sizes if s) != len(sizes):
        raise RuntimeError(f"batch sizes {sizes} exceed the hardware limit of three circuits")
    plan = series_plan()
    manifest = json.loads(files["batch-00/cases.json"])
    for world, kwargs in WORLDS.items():
        result = evaluate(synthetic_series(files, plan, manifest, **kwargs), manifest)
        if not result["decision"]["outcome"].startswith(WORLD_OUTCOMES[world]):
            raise RuntimeError(f"world {world} reads {result['decision']['outcome']!r}, classes {result['classes']}")
    return (
        f"b0 replay {digest[:12]} byte-equal; "
        + ", ".join(parts)
        + f"; series of {len(sizes)} batches {sizes}; each of {len(WORLDS)} simulated worlds reads its preregistered "
        "outcome"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--select", action="store_true")
    mode.add_argument("--replay", action="store_true")
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
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
