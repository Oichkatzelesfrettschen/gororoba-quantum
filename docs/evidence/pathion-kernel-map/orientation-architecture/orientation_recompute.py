"""Network half of the circuit analysis: routed ledger and layout search on the live Target of ibm_kingston.

ibm_kingston carries the dry-run layout and seed; its Target at the recompute calibration is checked against the
dry-run compile counts (the "reproduction" block) before any search row is read. The
search compiles every assignment of the six logical qubits to one tile of each heavy-hex tile shape.

  "$PYTHON" orientation_recompute.py OUT.json
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

import rustworkx as rx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import orientation_circuits as C  # noqa: E402
import orientation_model as M  # noqa: E402
from qiskit import transpile  # noqa: E402

import live_run  # noqa: E402
import parallel  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402

BACKEND = "ibm_kingston"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json"
# Values 30, 31 and 32 of the draw (indices in DRAW): the search seed and two confirmation seeds.
SEARCH_SEED, CONFIRM_SEEDS = 6023, (47051, 26813)
SHAPES = {
    "path6": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    "spider_2_2_1": None,  # from the ibm_fez dry-run pattern
    "spider_3_1_1": None,  # from the ibm_marrakesh dry-run pattern
}
TOP = 8


def shape_edges() -> dict[str, tuple[list[int], list[tuple[int, int]]]]:
    pats = M.patterns()
    out: dict[str, tuple[list[int], list[tuple[int, int]]]] = {}
    for shape, backend in (("spider_2_2_1", "ibm_fez"), ("spider_3_1_1", "ibm_marrakesh")):
        qs, es = M.pattern_graph(pats[backend]["members"])
        out[shape] = (qs, sorted(es))
    out["path6"] = (list(range(6)), SHAPES["path6"] or [])
    return out


def best_tile(
    dev: M.Dev, ex_q: dict[int, str], ex_e: dict[tuple[int, int], str], qs: list[int], es: list[tuple[int, int]]
) -> list[int]:
    """The embedding of a shape with the smallest summed CZ and readout error on healthy hardware."""
    graph = dev.graph()
    graph.remove_nodes_from(sorted(ex_q))
    small = rx.PyGraph()
    small.add_nodes_from(qs)
    idx = {q: i for i, q in enumerate(qs)}
    small.add_edges_from_no_data([(idx[a], idx[b]) for a, b in es])
    best: tuple[float, list[int]] | None = None
    for found in rx.vf2_mapping(graph, small, subgraph=True, induced=False, id_order=True):
        tile = [0] * len(qs)
        for big, s in found.items():
            tile[s] = big
        if any((tile[idx[a]], tile[idx[b]]) in ex_e for a, b in es):
            continue
        cost = sum(dev.cz[(tile[idx[a]], tile[idx[b]])]["error"] for a, b in es) + sum(
            dev.q[q]["readout_error"] for q in tile
        )
        if best is None or cost < best[0]:
            best = (cost, tile)
    if best is None:
        raise RuntimeError("no healthy tile")
    return best[1]


def main(out: Path) -> None:
    from qiskit_ibm_runtime import QiskitRuntimeService

    pats = M.patterns()[BACKEND]
    snap = live_run.take_snapshot(QiskitRuntimeService(), BACKEND, M.OPERATOR[BACKEND])
    target = snap.admission_target if snap.admission_target is not None else live_run.build_admission_target(snap)
    dev = M.Dev(M.device(BACKEND, "dry"))
    ex_q, ex_e = dev.exclusions(M.OPERATOR[BACKEND])
    result: dict[str, Any] = {
        "backend": BACKEND,
        "calibration_dry_run": pats["calibration"],
        "calibration_recompute": snap.calibration,
        "draw": DRAW,
        "seeds": {"search": SEARCH_SEED, "confirm": list(CONFIRM_SEEDS)},
    }
    kinds = {k: C.all_templates(k) for k in ("retained", "merged", "sparse")}
    units = list(kinds["retained"])
    result["units"] = units
    # routed stage ledger of the retained control on the dry-run layout and seed
    layout = pats["layout_logical"]
    seed = pats["seed_transpiler"]
    ledger: dict[str, Any] = {}
    for operand in C.OPERANDS:
        tag = pkm.operand_tag(operand)
        qc = C.pko.role_template("ctrl", operand)
        labels = C.stage_of(qc)
        marg: dict[str, int] = {}
        prev = 0
        for stage in C.STAGES:
            if stage not in labels:
                marg[stage] = 0
                continue
            part = C.prefix(qc, labels, stage)
            isa = transpile(part, target=target, optimization_level=3, seed_transpiler=seed, initial_layout=layout)
            total = C.cz(isa)
            marg[stage] = total - prev
            prev = total
        full = C.Compile(target, kinds["retained"], seed)((f"ctrl_{tag}", tuple(layout)))
        ledger[tag] = {
            "routed_marginal": marg,
            "routed_total_prefix_sum": prev,
            "routed_total_full": full,
            "layout": layout,
            "seed": seed,
        }
    result["routed_ledger_retained_ctrl_dry_run_layout"] = ledger
    # reproduction of the dry-run compiles under the recompute Target (calibration may differ from the dry run)
    repro = C.Compile(target, kinds["retained"], seed)
    result["reproduction"] = {
        u: [
            repro((u, tuple(layout))),
            pats["members"][f"kmo_{u.split('_', 1)[0]}_{u.split('_', 1)[1]}_plus"]["cz_record"],
        ]
        for u in units
    }
    # layout search
    result["tiles"] = {}
    result["search"] = {}
    for shape, (qs, es) in shape_edges().items():
        tile = best_tile(dev, ex_q, ex_e, qs, es)
        result["tiles"][shape] = tile
        for kind, templates in kinds.items():
            job = C.Compile(target, templates, SEARCH_SEED)
            items = [(u, tuple(tile[p] for p in perm)) for perm in C.assignments() for u in units]
            counts = parallel.ordered_map(job, items, min_items=8)
            table = [counts[k * len(units) : (k + 1) * len(units)] for k in range(len(C.assignments()))]
            ranked = sorted(range(len(table)), key=lambda k: (sum(table[k]), max(table[k]), k))
            top = []
            for k in ranked[:TOP]:
                lay = tuple(tile[p] for p in C.assignments()[k])
                confirm = []
                for s in CONFIRM_SEEDS:
                    cj = C.Compile(target, templates, s)
                    confirm.append([cj((u, lay)) for u in units])
                top.append({"perm": list(C.assignments()[k]), "layout": list(lay), "cz": table[k], "confirm": confirm})
            sums = sorted(sum(r) for r in table)
            result["search"][f"{kind}:{shape}"] = {
                "table": table,
                "top": top,
                "sum_min": sums[0],
                "sum_median": statistics.median(sums),
                "sum_max": sums[-1],
            }
    out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"{out.name}: {len(result['search'])} searches")
    designs_out = {}
    best = {kind: result["search"][f"{kind}:spider_2_2_1"]["top"][0] for kind in kinds}
    sabre_merged_primary = live_run._compile_primary(kinds["merged"]["ctrl_e1pe26"], snap, seed)
    sabre_merged_layout = tuple(sabre_merged_primary.layout.initial_index_layout(filter_ancillas=True))
    specs = {
        "retained_optimal_layout": ("retained", tuple(best["retained"]["layout"])),
        "merged_optimal_layout": ("merged", tuple(best["merged"]["layout"])),
        "merged_sabre_layout": ("merged", sabre_merged_layout),
        "sparse_optimal_layout": ("sparse", tuple(best["sparse"]["layout"])),
    }
    for name, (kind, lay) in specs.items():
        units_out = {}
        for u in units:
            isa = transpile(
                kinds[kind][u],
                target=target,
                optimization_level=3,
                seed_transpiler=SEARCH_SEED if name != "merged_sabre_layout" else seed,
                initial_layout=list(lay),
            )
            bound = isa.assign_parameters({pkm.ORIENTATION: 3.141592653589793})
            ops = [
                [inst.operation.name, [bound.find_bit(q).index for q in inst.qubits]]
                for inst in bound.data
                if inst.operation.name != "barrier"
            ]
            units_out[u] = {"cz": C.cz(isa), "ops": ops}
        designs_out[name] = {
            "kind": kind,
            "layout": list(lay),
            "seed": SEARCH_SEED if name != "merged_sabre_layout" else seed,
            "units": units_out,
        }
    (out.parent / "designs.json").write_text(json.dumps(designs_out, sort_keys=True, separators=(",", ":")) + "\n")
    # coset block pricing (one weight-matched block of the nullity-4 operand)
    import itertools

    import pathion_coset_block as pcb

    block = pcb.Block("b", (1, 26, 1), (27, 3, 5), 9)
    templates = {"ctrl": C.block_template_bit(block, 4), "move": C.block_template_bit(block, 1)}
    coset_out: dict[str, Any] = {
        "block": {"operand": [1, 26, 1], "basis": [27, 3, 5], "coset": 9},
        "logical_cz": {k: C.logical_cz(v) for k, v in templates.items()},
        "shapes": {},
    }
    four = {"path4": (list(range(4)), [(0, 1), (1, 2), (2, 3)]), "star4": (list(range(4)), [(0, 1), (0, 2), (0, 3)])}
    for shape, (qs, es) in four.items():
        tile = best_tile(dev, ex_q, ex_e, qs, es)
        job = C.Compile(target, templates, SEARCH_SEED)
        perms = list(itertools.permutations(range(4)))
        items = [(u, tuple(tile[p] for p in perm)) for perm in perms for u in templates]
        counts = parallel.ordered_map(job, items, min_items=8)
        rows = [counts[k * 2 : k * 2 + 2] for k in range(len(perms))]
        k = min(range(len(rows)), key=lambda r: (sum(rows[r]), max(rows[r]), r))
        lay = tuple(tile[p] for p in perms[k])
        units_out = {}
        for u, tpl in templates.items():
            isa = transpile(
                tpl, target=target, optimization_level=3, seed_transpiler=SEARCH_SEED, initial_layout=list(lay)
            )
            bound = isa.assign_parameters({pkm.ORIENTATION: 3.141592653589793})
            units_out[u] = {
                "cz": C.cz(isa),
                "ops": [
                    [i.operation.name, [bound.find_bit(q).index for q in i.qubits]]
                    for i in bound.data
                    if i.operation.name != "barrier"
                ],
            }
        coset_out["shapes"][shape] = {
            "tile": tile,
            "perm": list(perms[k]),
            "layout": list(lay),
            "cz_min_sum": sum(rows[k]),
            "cz_median_sum": statistics.median(sum(r) for r in rows),
            "cz_max_sum": max(sum(r) for r in rows),
            "units": units_out,
        }
    (out.parent / "coset.json").write_text(json.dumps(coset_out, sort_keys=True, separators=(",", ":")) + "\n")
    print("designs.json and coset.json written")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
