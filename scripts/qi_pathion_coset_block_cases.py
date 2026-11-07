"""Coset-block map of the 32-dimensional Cayley-Dickson kernel map on Tuna-17, and its QX twin.

gororoba_quantum/pathion_kernel_map.py defines the pair-resolved kernel map of the operand e_i + t e_j of A_5 on six
qubits; the full map routes to 116 to 144 CZ on the admitted Tuna-17 qubits and does not resolve at the retained
0.955 to 0.9654 contrast per CZ. gororoba_quantum/pathion_coset_block.py restricts it exactly to a coset block, 8
inputs, 4 XOR pairs and 16 SELECT signs on three data qubits and the selector. This case runs three blocks on one
admitted 4-qubit region of Tuna-17:

| template | operand | V = span | coset | aligned pairs N_b |
|---|---|---|---|---|
| ba | e1 + e18 | 19, 2, 12 | 1 | 2 |
| bb | e1 + e26 | 27, 2, 9 | 0 | 2 |
| b0 | e1 + e17 | 16, 1, 2 | 0 | 0 |
| xor_ba | ba with every SELECT sign table replaced by its cocycle-free XOR permutation | | | selector contrast -1 |

Each template compiles once with the orientation phase as a parameter (``ORIENTATION``), so the minus and plus arms
bind one routed circuit, share every CZ and differ by a phase pi on data qubit 0 before routing. Every rotation is
rounded to the nearest multiple of pi/36, the grid Tuna applies itself, and the ideal law of record is the
Statevector of the exact rounded routed circuit, read through the circuit's final layout.

Region and routing. The admitted qubits are the complement of zd.excluded_qubits() (the readout faults and the Ramsey
visibility floor of qi_zero_divisor_cases) and of q15, which reads P(0|1) 0.270 (tuna17-bipartite-designs.md). A
connected 4-qubit region is admitted when every coupler inside it has a retained residual coupling |J| of at most
J_LIMIT_HZ (the coupler-ZZ analysis, which rejects (1,4) at -19.3 kHz and (11,14) at -31.4 kHz). Every template
routes onto every admitted region at the candidate transpiler seeds of its own slice of one retained ANU QRNG draw
(DRAW, CANDIDATES per template, slice t holds draw indices t * CANDIDATES to (t + 1) * CANDIDATES - 1), and the whole
series runs on the one region with the fewest routed CZ summed over ba, bb and b0 (ties: the lexicographically least
region). Each template keeps the fewest-CZ candidate on that region (ties: the lowest index).

Series. One batch holds an arm pair and one readout circuit, so the minus and plus arm of a contrast share a
calibration, and each template runs two replicates, the first as (plus, minus), the second as (minus, plus). Batch
index 4 * replicate + template carries readout-0 when replicate + template is even and readout-1 otherwise, so every
contrast sees both readout references and neither reference follows one replicate.

Preregistered decisions (Z_RESOLVE standard errors; raw counts, pooled over a template's replicates):
- resolution: ba and bb each read the ideal sign of at least 6 of their 8 bins at Z_RESOLVE;
- pattern: ba and bb differ in two bins of c(y), and the two blocks read opposite signs there at Z_RESOLVE, so the
  selector contrast (0.5 for both) is not the observable;
- null: the b0 selector contrast lies within Z_RESOLVE standard errors of zero;
- cocycle-free: the xor_ba selector contrast is negative at Z_RESOLVE and the ba selector contrast positive;
- depth: the contraction per CZ implied by each template's visibility lies inside or outside the retained band
  RHO_BAND, reported with the template's routed CZ.

Usage: "$PYTHON" scripts/qi_pathion_coset_block_cases.py
       (--write DIR | --check DIR | --select-region | --qx-conformance RUN_DIR | --analyze RUN_DIR... --out FILE
        | --self-test)
--write DIR writes DIR/pathion_coset_block_tuna_17/ and DIR/pathion_coset_block_qx/ (batch-NN/ cases under a series
cases.json); --check regenerates both and compares bytes and file sets; --qx-conformance reads a local qxelarator run
of the Tuna series (scripts/qx_local_series.py) and compares each circuit with its ideal law. Bit strings put qubit 0
at the rightmost character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_cancellation_cases as kcc  # noqa: E402
import qi_zero_divisor_cases as zd  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
import qi_records  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_coset_block_tuna_17"
QX_SERIES = "pathion_coset_block_qx"
NQUBITS = 17
SHOTS = 16384
QX_QUBITS = 10
QX_SHOTS = 2048
GRID = kcc.GRID
BASIS = kcc.BASIS
Z_RESOLVE = 3.0
# The ANU QRNG draw whose 64 values seed every routing candidate; it belongs to this case's manifest.
DRAW = "docs/evidence/anu_qrng/draw-2026-11-06T184327Z.json"
CANDIDATES = 16
EXTRA_EXCLUDED = (15,)
J_LIMIT_HZ = 1.0e4
REGION_SIZE = 4
RHO_BAND = (0.955, 0.9654)
# Retained per-qubit readout of the region qubits: the six readout circuits of the kernel-cancellation series.
READOUT_RUNS = tuple(
    ROOT / "results/quantum_inspire/runs" / f"2026-10-23T{stamp}-kernel_cancellation_tuna_17-batch-{batch:02d}"
    for batch, stamp in enumerate(("075543Z", "080006Z", "080624Z", "081101Z", "081536Z", "082011Z"))
)

BLOCKS = {
    "ba": pcb.Block("ba", (1, 18, 1), (19, 2, 12), 1),
    "bb": pcb.Block("bb", (1, 26, 1), (27, 2, 9), 0),
    "b0": pcb.Block("b0", (1, 17, 1), (16, 1, 2), 0),
}
# (template name, block key, cocycle-free); the order fixes the draw slice and the batch order.
TEMPLATES = (("ba", "ba", False), ("bb", "bb", False), ("b0", "b0", False), ("xor_ba", "ba", True))
PRIMARY = ("ba", "bb", "b0")
SELECTOR = 3


def template_circuit(name: str) -> Any:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    return pcb.block_template(BLOCKS[key], cocycle_free=free, measure=False)


def logical_laws(name: str) -> dict[bool, Any]:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    return {
        plus: pcb.block_law(pcb.block_circuit(BLOCKS[key], plus, cocycle_free=free, measure=False))
        for plus in (False, True)
    }


def draw_values() -> list[int]:
    values = read_record(DRAW)["values"]
    if len(values) != CANDIDATES * len(TEMPLATES):
        raise ValueError(f"{DRAW} holds {len(values)} values, not {CANDIDATES * len(TEMPLATES)}")
    return [int(v) for v in values]


def candidate_seeds(index: int) -> list[tuple[int, int]]:
    """(draw index, transpiler seed value) of the candidates of template `index`."""
    values = draw_values()
    return [(n, values[n]) for n in range(index * CANDIDATES, (index + 1) * CANDIDATES)]


def coupler_limit_regions(topology: tuple[tuple[int, int], ...]) -> list[tuple[int, ...]]:
    """Connected REGION_SIZE-qubit regions off the excluded qubits whose inner couplers all satisfy J_LIMIT_HZ."""
    analysis = json.loads(zd.COUPLER_ZZ_ANALYSIS.read_text(encoding="utf-8"))
    coupling = {tuple(sorted(row["edge"])): abs(row["j_hz"]) for row in analysis["edges"]}
    out = []
    for region in zd.connected_regions(topology, REGION_SIZE):
        inside = {tuple(sorted(e)) for e in topology if e[0] in region and e[1] in region}
        if set(region) & set(EXTRA_EXCLUDED) or any(coupling[e] > J_LIMIT_HZ for e in inside):
            continue
        out.append(region)
    return out


class RouteCount:
    """Routed CZ count of one (template index, region, seed value); a module-level callable for the pool."""

    def __init__(self, topology: tuple[tuple[int, int], ...]) -> None:
        self.topology = topology

    def __call__(self, item: tuple[int, tuple[int, ...], int]) -> int:
        index, region, seed = item
        return int(compile_template(self.topology, index, region, seed).count_ops().get("cz", 0))


def compile_template(topology: tuple[tuple[int, int], ...], index: int, region: tuple[int, ...], seed: int) -> Any:
    from qiskit import transpile
    from qiskit.transpiler import CouplingMap

    local = {q: n for n, q in enumerate(region)}
    edges = [[local[a], local[b]] for a, b in topology if a in local and b in local]
    coupling = CouplingMap(edges + [[b, a] for a, b in edges])
    return transpile(
        template_circuit(TEMPLATES[index][0]),
        coupling_map=coupling,
        basis_gates=BASIS,
        optimization_level=2,
        seed_transpiler=seed,
    )


@cache
def routing_table(
    topology: tuple[tuple[int, int], ...],
) -> dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]]:
    """(template index, region) -> [(draw index, seed value, routed CZ)] over every admitted region."""
    regions = coupler_limit_regions(topology)
    items = [(t, region, seed) for t in range(len(TEMPLATES)) for region in regions for _, seed in candidate_seeds(t)]
    counts = parallel.ordered_map(RouteCount(topology), items)
    table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]] = {}
    position = 0
    for t in range(len(TEMPLATES)):
        for region in regions:
            row = []
            for n, seed in candidate_seeds(t):
                row.append((n, seed, counts[position]))
                position += 1
            table[(t, region)] = row
    return table


def choose_region(table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]]) -> tuple[int, ...]:
    regions = sorted({region for _, region in table})
    primary = [i for i, t in enumerate(TEMPLATES) if t[0] in PRIMARY]
    return min(regions, key=lambda r: (sum(min(c for *_, c in table[(t, r)]) for t in primary), r))


def round_to_grid(circuit: Any) -> Any:
    from qiskit.circuit.library import RZGate

    out = circuit.copy()
    for k, instruction in enumerate(out.data):
        if instruction.operation.name == "rz":
            angle = float(instruction.operation.params[0])
            out.data[k] = instruction.replace(operation=RZGate(round(angle / GRID) * GRID))
    return out


def bind_arm(compiled: Any, plus: bool) -> Any:
    """The compile bound at one orientation, every rotation on the pi/36 grid; parameters bind by name."""
    value = math.pi if plus else 0.0
    bound = compiled.assign_parameters({p: value for p in compiled.parameters if p.name == pcb.ORIENTATION.name})
    return round_to_grid(bound)


def skeleton(circuit: Any) -> list[tuple[str, tuple[int, ...]]]:
    """Every non-rotation operation in order with its qubits: the part the two arms must share."""
    return [
        (i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits))
        for i in circuit.data
        if i.operation.name != "rz"
    ]


def rz_sites(circuit: Any) -> list[tuple[int, ...]]:
    return [tuple(circuit.find_bit(q).index for q in i.qubits) for i in circuit.data if i.operation.name == "rz"]


def ideal_of_record(bound: Any) -> np.ndarray:
    """Outcome law of the rounded routed circuit over the logical bits (data 0-2, selector 3), index y + 8 s."""
    from qiskit.quantum_info import Statevector

    final = bound.layout.final_index_layout()
    physical = Statevector(bound).probabilities()
    logical = np.zeros_like(physical)
    for index, value in enumerate(physical):
        v = sum(1 << bit for bit in range(bound.num_qubits) if index >> final[bit] & 1)
        logical[v] += value
    return logical


def retained_readout(region: tuple[int, ...]) -> dict[int, tuple[float, float]]:
    """(e01, e10) of each region qubit from the retained readout circuits: mean P(1 | prepared 0) and
    1 - mean P(1 | prepared 1) over the readout-0 and readout-1 runs of the kernel-cancellation series."""
    zero: dict[int, list[float]] = {q: [] for q in region}
    one: dict[int, list[float]] = {q: [] for q in region}
    for run in READOUT_RUNS:
        for name, bucket in (("readout-0.cq", zero), ("readout-1.cq", one)):
            path = run / "raw" / f"{name}.json"
            if not path.exists():
                continue
            shots = json.loads(path.read_text(encoding="utf-8"))
            for q in region:
                bucket[q].append(sum(bit(s, q) for s in shots) / len(shots))
    return {q: (float(np.mean(zero[q])), 1.0 - float(np.mean(one[q]))) for q in region if zero[q] and one[q]}


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def confusion(readout: list[tuple[float, float]]) -> np.ndarray:
    """Joint assignment matrix over the logical bits: row = measured, column = true, bit v of the index."""
    matrix = np.ones((1, 1))
    for e01, e10 in reversed(readout):
        matrix = np.kron(matrix, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    return matrix


def conditional_contrast(plus: np.ndarray, minus: np.ndarray) -> tuple[float, np.ndarray]:
    return pcb.selector_contrast(plus, minus), pcb.output_contrast(plus, minus)


def forecast(ideal: dict[bool, np.ndarray], cz: int, rho: float, readout: list[tuple[float, float]]) -> dict[str, Any]:
    """Raw contrasts of a device that contracts the 16-outcome law toward uniform by rho^cz and then misassigns each
    bit with the retained single-qubit assignment (hypothesis-level model), and the shot error of pooled replicates."""
    retention = rho**cz
    matrix = confusion(readout)
    law = {p: matrix @ (retention * ideal[p] + (1 - retention) / ideal[p].size) for p in (False, True)}
    selector, per_bin = conditional_contrast(law[True], law[False])
    ideal_bins = pcb.output_contrast(ideal[True], ideal[False])
    sign = np.sign(ideal_bins)
    decided = np.abs(ideal_bins) > 0.5
    half = law[True].size // 2
    sigma = []
    for y in range(half):
        var = 0.0
        for p in (False, True):
            weight = law[p][y] + law[p][y + half]
            p0 = law[p][y] / weight
            var += p0 * (1 - p0) / (SHOTS * 2 * weight)
        sigma.append(math.sqrt(var))
    return {
        "retention": retention,
        "selector_contrast": selector,
        "c": [round(float(x), 6) for x in per_bin],
        "visibility": float(np.mean(per_bin[decided] * sign[decided])),
        "se_per_bin_two_replicates": [round(s, 6) for s in sigma],
        "z_per_bin": [round(float(abs(c) / s), 2) for c, s in zip(per_bin, sigma, strict=True)],
        "selector_se": math.sqrt(2 * 0.25 / (SHOTS * 2)),
    }


def build_plan() -> dict[str, Any]:
    tuna, _ = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    table = routing_table(topology)
    region = choose_region(table)
    templates: dict[str, dict[str, Any]] = {}
    for t, (name, key, free) in enumerate(TEMPLATES):
        n, seed, cz = min(table[(t, region)], key=lambda row: (row[2], row[0]))
        compiled = compile_template(topology, t, region, seed)
        arms = {plus: bind_arm(compiled, plus) for plus in (False, True)}
        if skeleton(arms[False]) != skeleton(arms[True]) or rz_sites(arms[False]) != rz_sites(arms[True]):
            raise ValueError(f"{name}: the two arms do not share one routed gate sequence")
        final = compiled.layout.final_index_layout()
        templates[name] = {
            "block": key,
            "cocycle_free": free,
            "draw_index": n,
            "transpiler_seed": seed,
            "cz": cz,
            "roles": {f"d{v}": int(final[v]) for v in range(3)} | {"selector": int(final[SELECTOR])},
            "arms": arms,
            "ideal": {plus: ideal_of_record(arms[plus]) for plus in (False, True)},
            "unrounded": logical_laws(name),
        }
    return {"region": region, "table": table, "templates": templates}


def rounding_gap(template: dict[str, Any]) -> float:
    return float(max(np.abs(template["ideal"][p] - template["unrounded"][p]).max() for p in (False, True)))


def label_table() -> dict[str, Any]:
    """Tuna bin y of each block against the IBM full-map outcome index k_out (add 32 for the selector value 1)."""
    return {
        key: {
            "operand": list(block.operand),
            "basis": list(block.basis),
            "coset": block.coset,
            "ibm_data_index_of_bin": pcb.output_labels(block),
        }
        for key, block in BLOCKS.items()
    }


def ideal_summary(template: dict[str, Any]) -> dict[str, Any]:
    plus, minus = template["ideal"][True], template["ideal"][False]
    selector, per_bin = conditional_contrast(plus, minus)
    return {
        "selector_contrast": round(float(selector), 6),
        "c": [round(float(x), 6) for x in per_bin],
    }


def predictions(plan: dict[str, Any]) -> dict[str, Any]:
    readout = retained_readout(plan["region"])
    out: dict[str, Any] = {
        "model": "contraction of the 16-outcome law toward uniform by rho^cz, then the retained single-qubit "
        "assignment; hypothesis-level",
        "rho_band": list(RHO_BAND),
        "readout_runs": [p.relative_to(ROOT).as_posix() for p in READOUT_RUNS],
        "readout_e01_e10": {str(q): [round(a, 4), round(b, 4)] for q, (a, b) in readout.items()},
        "templates": {},
    }
    for name, t in plan["templates"].items():
        roles = t["roles"]
        per_bit = [readout[plan["region"][roles[k]]] for k in ("d0", "d1", "d2", "selector")]
        out["templates"][name] = {f"rho_{rho}": forecast(t["ideal"], t["cz"], rho, per_bit) for rho in RHO_BAND}
    return out


def circuit_text(compiled: Any, place: dict[int, int], nqubits: int, note: str) -> str:
    lines = zd.header(nqubits) + [note]
    return "\n".join(lines + kcc.emit(compiled, place) + ["", "barrier q", "b = measure q", ""])


def batch_plan() -> list[dict[str, Any]]:
    """The eight batches: (batch, template, replicate, arm order, readout state)."""
    plan = []
    for replicate in (0, 1):
        for t, (name, *_rest) in enumerate(TEMPLATES):
            order = (True, False) if replicate == 0 else (False, True)
            plan.append(
                {
                    "batch": f"batch-{4 * replicate + t:02d}",
                    "template": name,
                    "replicate": replicate,
                    "order": order,
                    "readout": (replicate + t) % 2,
                }
            )
    return plan


def arm_file(name: str, plus: bool, replicate: int) -> str:
    return f"{name}-{'plus' if plus else 'minus'}-r{replicate}.cq"


def series(
    plan: dict[str, Any], backend: dict[str, Any], nqubits: int, shots: int, place: dict[int, int]
) -> dict[str, str]:
    region = plan["region"]
    files: dict[str, str] = {}
    texts = {"readout-0.cq": kcc.readout(nqubits, False), "readout-1.cq": kcc.readout(nqubits, True)}
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "shots": shots,
        "region": list(region),
        "placement": {str(k): v for k, v in place.items()},
        "qrng_draw": DRAW,
        "candidates_per_template": CANDIDATES,
        "templates": {
            name: {
                "block": t["block"],
                "operand": list(BLOCKS[t["block"]].operand),
                "basis": list(BLOCKS[t["block"]].basis),
                "coset": BLOCKS[t["block"]].coset,
                "cocycle_free": t["cocycle_free"],
                "draw_index": t["draw_index"],
                "draw_indices_searched": [
                    TEMPLATES.index(next(x for x in TEMPLATES if x[0] == name)) * CANDIDATES,
                    (TEMPLATES.index(next(x for x in TEMPLATES if x[0] == name)) + 1) * CANDIDATES - 1,
                ],
                "transpiler_seed": t["transpiler_seed"],
                "cz": t["cz"],
                "roles": {k: place[v] for k, v in t["roles"].items()},
                "ideal_selector_contrast": ideal_summary(t)["selector_contrast"],
                "ideal_c": ideal_summary(t)["c"],
                "rounding_gap": round(rounding_gap(t), 6),
            }
            for name, t in plan["templates"].items()
        },
        "labels": label_table(),
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_plan():
        name = row["template"]
        t = plan["templates"][name]
        rows: list[dict[str, Any]] = []
        for plus in row["order"]:
            fname = arm_file(name, plus, row["replicate"])
            texts[fname] = circuit_text(
                t["arms"][plus],
                place,
                nqubits,
                f"// region {list(region)} template {name} seed {t['transpiler_seed']} {'plus' if plus else 'minus'}",
            )
            rows.append(
                {
                    "file": fname,
                    "kind": "arm",
                    "template": name,
                    "arm": "plus" if plus else "minus",
                    "replicate": row["replicate"],
                    "ideal": [round(float(x), 12) for x in t["ideal"][plus]],
                }
            )
        rows.append({"file": f"readout-{row['readout']}.cq", "kind": "readout"})
        for r in rows:
            r["sha256"] = hashlib.sha256(texts[r["file"]].encode()).hexdigest()
            files[f"{row['batch']}/{r['file']}"] = texts[r["file"]]
        manifest = {"schema": "qi-pathion-coset-block-cases-v1", **common, "batch": row["batch"], "circuits": rows}
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "files": [r["file"] for r in rows]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-pathion-coset-block-series-v1", "backend": backend["identifier"], "batches": batches},
            indent=1,
        )
        + "\n"
    )
    return files


def preregistered() -> dict[str, str]:
    return {
        "resolution": f"ba and bb each read the ideal sign of at least 6 of 8 bins at {Z_RESOLVE} se",
        "pattern": f"ba and bb read opposite signs in their two differing bins at {Z_RESOLVE} se",
        "null": f"b0 selector contrast within {Z_RESOLVE} se of zero",
        "cocycle_free": f"xor_ba selector contrast below -{Z_RESOLVE} se and ba selector contrast above {Z_RESOLVE} se",
        "depth": "contraction per CZ implied by each template visibility against RHO_BAND, reported with its CZ",
    }


def build() -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    tuna, qx = zd.catalogue_check()
    plan = build_plan()
    region = plan["region"]
    return {
        TUNA_SERIES: series(plan, tuna, NQUBITS, SHOTS, dict(enumerate(region))),
        QX_SERIES: series(plan, qx, QX_QUBITS, QX_SHOTS, {n: n for n in range(REGION_SIZE)}),
    }, plan


def write(directory: Path) -> None:
    built, plan = build()
    for name, files in built.items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    proposal = directory / TUNA_SERIES / "prediction.json"
    proposal.write_text(json.dumps(predictions(plan), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path) -> None:
    built, plan = build()
    built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(plan), indent=1, sort_keys=True) + "\n"
    for name, files in built.items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and not p.name.startswith(".")
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


def select_region() -> None:
    tuna, _ = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    table = routing_table(topology)
    primary = [i for i, t in enumerate(TEMPLATES) if t[0] in PRIMARY]
    ranking = sorted(
        {r for _, r in table},
        key=lambda r: (sum(min(c for *_, c in table[(t, r)]) for t in primary), r),
    )
    for r in ranking:
        per = {TEMPLATES[t][0]: min(c for *_, c in table[(t, r)]) for t in range(len(TEMPLATES))}
        print(r, per, sum(per[n] for n in PRIMARY))


# Analysis -------------------------------------------------------------------------------------------------


def outcome_counts(shots: list[str], roles: dict[str, int]) -> np.ndarray:
    """Counts over the logical outcome index y + 8 s read from the physical qubits of `roles`."""
    counts = np.zeros(16)
    keys = ("d0", "d1", "d2", "selector")
    for shot in shots:
        counts[sum(bit(shot, roles[k]) << v for v, k in enumerate(keys))] += 1
    return counts


def bin_contrast(plus: np.ndarray, minus: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """c(y) and its standard error from counts (conditional P(s = 0 | y) of each arm, binomial error)."""
    values = np.zeros(8)
    errors = np.zeros(8)
    for y in range(8):
        var = 0.0
        for counts, sign in ((plus, 1.0), (minus, -1.0)):
            n = counts[y] + counts[y + 8]
            p = counts[y] / n if n else 0.5
            values[y] += sign * p
            var += p * (1 - p) / max(n, 1.0)
        errors[y] = math.sqrt(var)
    return values, errors


def selector_stat(plus: np.ndarray, minus: np.ndarray) -> tuple[float, float]:
    n_plus, n_minus = plus.sum(), minus.sum()
    p, m = float(plus[:8].sum() / n_plus), float(minus[:8].sum() / n_minus)
    return p - m, math.sqrt(p * (1 - p) / n_plus + m * (1 - m) / n_minus)


def corrected(counts: np.ndarray, readout: list[tuple[float, float]]) -> np.ndarray:
    return np.linalg.solve(confusion(readout), counts)


def register_assignment(shots: dict[str, list[str]]) -> dict[int, tuple[float, float]] | None:
    """(e01, e10) of every register qubit from the readout-0 and readout-1 circuits of the shot lists, None when
    the series lacks either reference."""
    zero = [v for k, v in shots.items() if k.endswith("/readout-0.cq")]
    one = [v for k, v in shots.items() if k.endswith("/readout-1.cq")]
    if not zero or not one:
        return None
    width = len(zero[0][0])
    return {
        q: (
            float(np.mean([sum(bit(s, q) for s in run) / len(run) for run in zero])),
            1.0 - float(np.mean([sum(bit(s, q) for s in run) / len(run) for run in one])),
        )
        for q in range(width)
    }


def signed_z(c: float, se: float, sign: float) -> float:
    """Contrast c along the ideal sign in standard errors. A bin whose sampled selector outcomes are deterministic in
    both arms has se 0 and decides by an exact sign match: +inf when c carries the ideal sign, -inf when it carries
    the opposite sign, 0 when c or the ideal sign is zero."""
    along = c * sign
    if se > 0:
        return along / se
    return math.inf if along > 0 else -math.inf if along < 0 else 0.0


def ratio_or_none(value: float, se: float) -> float | None:
    """value / se for a report, None when se is 0 (a deterministic statistic has no finite z)."""
    return value / se if se > 0 else None


def pattern_bins(ideal_a: np.ndarray, ideal_b: np.ndarray) -> list[int]:
    """The preregistered pattern bins: those where the two templates' ideal contrasts carry opposite signs."""
    return [y for y in range(len(ideal_a)) if np.sign(ideal_a[y]) * np.sign(ideal_b[y]) < 0]


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """Preregistered decisions from shot lists keyed by "batch/file"; manifest is any batch's cases.json."""
    templates = manifest["templates"]
    rows: dict[str, dict[str, Any]] = {}
    ideal_c = {n: np.array(t["ideal_c"]) for n, t in templates.items()}
    along_ideal: dict[str, list[float]] = {}
    assignment = register_assignment(shots)
    for name, t in templates.items():
        roles = t["roles"]
        plus = np.zeros(16)
        minus = np.zeros(16)
        replicate_rows = []
        for key in sorted(shots):
            batch, fname = key.split("/")
            if not fname.startswith(f"{name}-"):
                continue
            counts = outcome_counts(shots[key], roles)
            if "-plus-" in fname:
                plus += counts
            else:
                minus += counts
            replicate_rows.append(key)
        c, se = bin_contrast(plus, minus)
        selector, selector_se = selector_stat(plus, minus)
        sign = np.sign(ideal_c[name])
        decided = np.abs(ideal_c[name]) > 0.5
        z_raw = [signed_z(float(c[y]), float(se[y]), float(sign[y])) for y in range(8)]
        along_ideal[name] = z_raw
        visibility = float(np.mean(c[decided] * sign[decided]))
        cz = t["cz"]
        corrected_visibility = float("nan")
        if assignment is not None:
            keys = ("d0", "d1", "d2", "selector")
            matrix = confusion([assignment[roles[k]] for k in keys])
            fixed = [np.linalg.solve(matrix, counts) for counts in (plus, minus)]
            c_fixed = pcb.output_contrast(fixed[0] / fixed[0].sum(), fixed[1] / fixed[1].sum())
            corrected_visibility = float(np.mean(c_fixed[decided] * sign[decided]))
        implied = corrected_visibility ** (1.0 / cz) if corrected_visibility > 0 else float("nan")
        position = "below" if implied < RHO_BAND[0] else "above" if implied > RHO_BAND[1] else "inside"
        rows[name] = {
            "files": replicate_rows,
            "c": [float(x) for x in c],
            "se": [float(x) for x in se],
            "z_signed": [None if math.isinf(z) else float(z) for z in z_raw],
            "deterministic_bins": [bool(se[y] == 0) for y in range(8)],
            "bins_with_ideal_sign": int(sum(z >= Z_RESOLVE for z in z_raw)),
            "selector_contrast": selector,
            "selector_se": selector_se,
            "visibility": visibility,
            "cz": cz,
            "visibility_readout_corrected": corrected_visibility,
            "contraction_per_cz_implied": implied,
            "against_rho_band": position if implied == implied else "not read",
        }
    ba, bb, b0, xor = rows["ba"], rows["bb"], rows["b0"], rows["xor_ba"]
    differing = pattern_bins(ideal_c["ba"], ideal_c["bb"])
    pattern_z = [max(min(along_ideal["ba"][y], along_ideal["bb"][y]), 0.0) for y in differing]
    decisions = {
        "resolution": {
            "ba": ba["bins_with_ideal_sign"] >= 6,
            "bb": bb["bins_with_ideal_sign"] >= 6,
        },
        "pattern": {
            "bins": differing,
            "z": [None if math.isinf(z) else z for z in pattern_z],
            "resolved": bool(differing) and all(z >= Z_RESOLVE for z in pattern_z),
        },
        "null": {
            "z": ratio_or_none(b0["selector_contrast"], b0["selector_se"]),
            "holds": abs(b0["selector_contrast"]) <= Z_RESOLVE * b0["selector_se"],
        },
        "cocycle_free": {
            "xor_z": ratio_or_none(xor["selector_contrast"], xor["selector_se"]),
            "ba_z": ratio_or_none(ba["selector_contrast"], ba["selector_se"]),
            "resolved": xor["selector_contrast"] <= -Z_RESOLVE * xor["selector_se"]
            and ba["selector_contrast"] >= Z_RESOLVE * ba["selector_se"],
        },
    }
    order: dict[str, str] | None = None
    if executed is not None:
        order = {}
        for key in sorted(executed, key=lambda k: executed[k]):
            batch, fname = key.split("/")
            if not fname.startswith("readout"):
                order[batch] = order.get(batch, "") + ("+" if "-plus-" in fname else "-")
    return {
        "templates": rows,
        "decisions": decisions,
        "all_decisions_met": bool(
            all(decisions["resolution"].values())
            and decisions["pattern"]["resolved"]
            and decisions["null"]["holds"]
            and decisions["cocycle_free"]["resolved"]
        ),
        "executed_order": order,
    }


def law_shots(law: np.ndarray, roles: dict[str, int], shots: int) -> list[str]:
    """Bit strings of the expected counts of a 16-outcome law over (d0, d1, d2, selector), by largest remainder, so
    the series carries no sampling noise and no random seed."""
    expected = law / law.sum() * shots
    counts = np.floor(expected).astype(int)
    for v in np.argsort(counts - expected)[: shots - counts.sum()]:
        counts[v] += 1
    strings: list[str] = []
    for v, count in enumerate(counts):
        value = 0
        for k, key in enumerate(("d0", "d1", "d2", "selector")):
            value |= (v >> k & 1) << roles[key]
        strings += [format(value, f"0{NQUBITS}b")] * int(count)
    return strings


def cross_platform(
    tuna: dict[str, Any], ibm_c: list[float], ibm_visibility: float, block_key: str, template: str
) -> dict[str, Any]:
    """Tuna c(y) / V_tuna against IBM c(k) / V_ibm on the block's 8 output bins (k = the label table's data index).

    ibm_c is the full 32-bin c(k) of the IBM operand pair; the model-branch values of its record are noise-model
    output, measured values come from its collected record."""
    block = BLOCKS[block_key]
    labels = pcb.output_labels(block)
    row = tuna["templates"][template]
    ratio_tuna = [c / row["visibility"] for c in row["c"]]
    ratio_ibm = [ibm_c[k] / ibm_visibility for k in labels]
    se = [s / abs(row["visibility"]) for s in row["se"]]
    return {
        "labels": labels,
        "tuna_ratio": ratio_tuna,
        "ibm_ratio": ratio_ibm,
        "difference_over_tuna_se": [(a - b) / s for a, b, s in zip(ratio_tuna, ratio_ibm, se, strict=True)],
    }


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """Read each collected batch through qi_records (receipt, circuit and job identities, raw shots against the
    recorded histogram), require every job completed, and evaluate the pooled series; the queue timestamp of each
    job is the `queued_at` of its recorded job metadata."""
    shared: dict[str, Any] | None = None
    shots: dict[str, list[str]] = {}
    executed: dict[str, str] = {}
    batches: list[str] = []
    for run_dir in sorted(run_dirs):
        record = qi_records.load_run(run_dir)
        acquisition = qi_records.validate_run(record, str(run_dir))
        cases = record["cases"]
        fields = {k: v for k, v in cases.items() if k not in ("batch", "circuits")}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise ValueError(f"{run_dir}/cases.json describes a different series")
        if not acquisition.completed:
            raise ValueError(f"{run_dir}: a job did not complete: {dict(acquisition.statuses)}")
        if cases["batch"] in batches:
            raise ValueError(f"{run_dir}: batch {cases['batch']} appears twice")
        batches.append(cases["batch"])
        queued = {row["file"]: row["job"]["queued_at"] for row in record["results"]["jobs"]}
        for job in acquisition.jobs:
            if job.raw is None or len(job.raw) != cases["shots"]:
                raise ValueError(f"{run_dir}/{job.file}: not {cases['shots']} raw shots")
            key = f"{cases['batch']}/{job.file}"
            shots[key] = list(job.raw)
            executed[key] = queued[job.file]
    if shared is None:
        raise ValueError("an analysis needs its run directories")
    expected = sorted(row["batch"] for row in batch_plan())
    if sorted(batches) != expected:
        raise ValueError(f"the runs hold other batches than {expected}")
    return {"schema": "qi-pathion-coset-block-analysis-v1", **evaluate(shots, shared, executed)}


def qx_conformance(run_dir: Path, bound: float = 0.025) -> dict[str, Any]:
    """Each circuit of a local qxelarator run of the Tuna series against its ideal law of record."""
    report: dict[str, Any] = {}
    for batch_dir in sorted(run_dir.glob("batch-*")):
        cases = json.loads((batch_dir / "cases.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]:
            if row["kind"] != "arm":
                continue
            template = cases["templates"][row["template"]]
            shots = json.loads((batch_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            counts = outcome_counts(shots, template["roles"])
            tvd = 0.5 * float(np.abs(counts / counts.sum() - np.array(row["ideal"])).sum())
            report[f"{batch_dir.name}/{row['file']}"] = {
                "shots": int(counts.sum()),
                "tvd": round(tvd, 6),
                "ok": tvd <= bound,
            }
    if not report:
        raise ValueError(f"{run_dir} holds no arm circuits")
    if not all(v["ok"] for v in report.values()):
        raise SystemExit(f"a circuit departs from its ideal by more than {bound}: {report}")
    return report


# Self-test --------------------------------------------------------------------------------------------------


def self_test() -> str:
    built, plan = build()
    files = built[TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    arms = [rel for rel in files if rel.endswith(".cq") and "/readout" not in rel]
    if len(arms) != 16 or any(len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) != 3 for n in range(8)):
        raise RuntimeError("the series does not hold sixteen arms in eight batches of three circuits")
    angles = [
        float(line[3:].split(")")[0]) for rel in arms for line in files[rel].splitlines() if line.startswith("Rz(")
    ]
    if not all(kcc.on_grid(a) for a in angles):
        raise RuntimeError("an emitted angle lies off the pi/36 grid")
    for key, block in BLOCKS.items():
        for plus in (False, True):
            if pcb.restriction_error(block, plus) > 1e-12:
                raise RuntimeError(f"{key}: the block law departs from the six-qubit law")
        if pcb.contrast_restriction_error(block) > 1e-12 or pcb.orientation_error(block) > 1e-12:
            raise RuntimeError(f"{key}: the contrast or the orientation phase departs")
    for t in plan["templates"].values():
        if rounding_gap(t) > 0.05:
            raise RuntimeError("grid rounding moved a law by more than 0.05")

    def device(retention: float, swap: tuple[str, str] | None = None, offset_b0: float = 0.0) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for rel in files:
            if rel.endswith("readout-0.cq") or rel.endswith("readout-1.cq"):
                out[rel] = [("0" if rel.endswith("readout-0.cq") else "1") * NQUBITS] * SHOTS
                continue
            if not rel.endswith(".cq"):
                continue
            batch, fname = rel.split("/")
            row = next(r for r in json.loads(files[f"{batch}/cases.json"])["circuits"] if r["file"] == fname)
            template = row["template"]
            plus = row["arm"] == "plus"
            source = swap[1] if swap and template == swap[0] else template
            law = plan["templates"][source]["ideal"][plus]
            law = retention * law + (1 - retention) / 16
            if template == "b0" and offset_b0 and plus:
                law = np.concatenate([law[:8] * (1 + offset_b0), law[8:] * (1 - offset_b0)])
            roles = manifest["templates"][template]["roles"]
            out[rel] = law_shots(law, roles, SHOTS)
        return out

    honest = evaluate(device(0.5), manifest)
    if not honest["all_decisions_met"]:
        raise RuntimeError(f"an honest device at retention 0.5 fails a decision: {honest['decisions']}")
    exact = evaluate(device(1.0), manifest)
    if not exact["all_decisions_met"] or not any(any(r["deterministic_bins"]) for r in exact["templates"].values()):
        raise RuntimeError(f"a noiseless device leaves a decision unmet or no deterministic bin: {exact['decisions']}")
    implied = honest["templates"]["ba"]["contraction_per_cz_implied"]
    if abs(implied - 0.5 ** (1 / plan["templates"]["ba"]["cz"])) > 2e-3:
        raise RuntimeError(f"a device of retention 0.5 implies {implied} per CZ")
    if not np.allclose(confusion([(0.1, 0.2)] * 4).sum(axis=0), 1.0):
        raise RuntimeError("an assignment matrix column does not sum to 1")
    free = evaluate(device(0.5, swap=("ba", "xor_ba")), manifest)
    if free["all_decisions_met"] or free["decisions"]["cocycle_free"]["resolved"]:
        raise RuntimeError("a cocycle-free circuit in the ba slot left the decisions standing")
    biased = evaluate(device(0.5, offset_b0=0.3), manifest)
    if biased["decisions"]["null"]["holds"]:
        raise RuntimeError("a b0 selector offset left the null standing")
    dead = evaluate(device(0.02), manifest)
    if dead["all_decisions_met"]:
        raise RuntimeError("a device at retention 0.02 resolves the map")
    return (
        f"qi pathion coset block: region {plan['region']}, routed CZ "
        + ", ".join(f"{n} {t['cz']}" for n, t in plan["templates"].items())
        + f"; {len(angles)} Rz on the pi/36 grid; honest device resolves every decision, a cocycle-free circuit in "
        "the ba slot, a b0 selector offset and a retention of 0.02 each fail one"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--select-region", action="store_true")
    mode.add_argument("--qx-conformance", type=Path)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.select_region:
        select_region()
    elif args.qx_conformance:
        print(json.dumps(qx_conformance(args.qx_conformance), indent=1))
    else:
        if args.out is None:
            parser.error("--analyze needs --out")
        args.out.write_text(json.dumps(analyze(args.analyze), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
