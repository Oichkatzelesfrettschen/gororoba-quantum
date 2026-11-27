"""Analysis of the three IBM Heron devices and the A5-242 orientation-bit circuits, with redesigns that place regions.

Everything here is offline: the retained JSON beside this file (collect.py: device calibrations and compiled patterns of
the three 2026-11-27 dry runs; orientation_recompute.py: compiled layouts of ibm_kingston) and the retained records of
results/live. Nothing is submitted.

  "$PYTHON" orientation_architecture.py --check             recompute every table and compare with results.json
  "$PYTHON" orientation_architecture.py --write             write results.json
  "$PYTHON" orientation_architecture.py --recompute-circuits   network: orientation_recompute.py (live Target)

--check fails when the placement model departs from the records (exclusions, candidate counts, placed counts, scores,
esp, coherence, duration, charge), when a merged circuit departs from its retained operator, or when results.json
departs from the recomputed tables.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "pathion-kernel-map" / "orientation-bit"))

import orientation_circuits as C  # noqa: E402
import orientation_model as M  # noqa: E402

import pathion_kernel_map as pkm  # noqa: E402

DT = 4e-9
JOB_OVERHEAD = 2.0  # seconds, scripts/pathion_kernel_map_check.py
POWER_JSON = ROOT / "docs" / "evidence" / "pathion-kernel-map" / "orientation-bit" / "power.json"
UNITS = ("ctrl", "move", "xtwin", "swap")
OPERAND_TAGS = ("e1pe26", "e1pe18")
DIGITS = 5


def rnd(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, DIGITS)
    if isinstance(value, dict):
        return {str(k): rnd(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [rnd(v) for v in value]
    if isinstance(value, (np.floating,)):
        return round(float(value), DIGITS)
    if isinstance(value, (np.integer,)):
        return int(value)
    return value


def quantiles(values: list[float]) -> dict[str, float]:
    a = np.array(values, dtype=float)
    return {
        "n": int(a.size),
        "min": float(a.min()),
        "q25": float(np.quantile(a, 0.25)),
        "median": float(np.median(a)),
        "q75": float(np.quantile(a, 0.75)),
        "max": float(a.max()),
    }


def reason_class(reason: str) -> str:
    for key, label in (
        ("operator", "operator"),
        ("readout", "readout"),
        ("T1", "T1/T2"),
        ("sx", "sx"),
        ("missing", "missing"),
        ("faulty", "faulty"),
    ):
        if reason.startswith(key) or key in reason.split(" ")[0]:
            return label
    return reason.split(" ")[0]


# ------------------------------------------------------------------------------------------------ 1 devices
def device_tables() -> dict[str, Any]:
    out: dict[str, Any] = {}
    pats = M.patterns()
    for backend in M.BACKENDS:
        for tag in ("dry", "now"):
            dev = M.Dev(M.device(backend, tag))
            operator = M.OPERATOR[backend] if tag == "dry" else M.OPERATOR[backend]
            ex_q, ex_e = dev.exclusions(operator)
            healthy = [q for q in range(dev.n) if q not in ex_q]
            cz_ok = [
                v["error"]
                for e, v in dev.cz.items()
                if e[0] < e[1] and e not in ex_e and e[::-1] not in ex_e and e[0] in healthy and e[1] in healthy
            ]
            row: dict[str, Any] = {
                "calibration": dev.raw["calibration"],
                "excluded_qubits": len(ex_q),
                "excluded_edges_directed": len(ex_e),
                "qubit_reasons": {c: sum(1 for r in ex_q.values() if r == c) for c in sorted(set(ex_q.values()))},
                "t1_us": quantiles([dev.q[q]["t1"] * 1e6 for q in healthy]),
                "t2_us": quantiles([dev.q[q]["t2"] * 1e6 for q in healthy]),
                "readout_error": quantiles([dev.q[q]["readout_error"] for q in healthy]),
                "sx_error": quantiles([dev.q[q]["sx"]["error"] for q in healthy]),
                "cz_error": quantiles(cz_ok),
            }
            if tag == "dry":
                rec = pats[backend]["excluded_qubits"]
                row["record_exclusions"] = {str(k): v for k, v in sorted(rec.items(), key=lambda kv: int(kv[0]))}
                row["record_edges"] = sorted(
                    {tuple(sorted(map(int, k.split("-")))) for k in pats[backend]["excluded_edges"]}
                )
            out[f"{backend}:{tag}"] = row
    return out


# ------------------------------------------------------------------------------------------------ 2 validation
def member_key(unit: str, plus: bool = True) -> str:
    role, tag = unit.split("_", 1)
    return f"kmo_{role}_{tag}_{'plus' if plus else 'minus'}"


def validation_and_decomposition() -> tuple[dict[str, Any], dict[str, Any]]:
    val: dict[str, Any] = {}
    dec: dict[str, Any] = {}
    pats = M.patterns()
    for backend in M.BACKENDS:
        p = pats[backend]
        dev = M.Dev(M.device(backend, "dry"))
        ex_q, ex_e = dev.exclusions(M.OPERATOR[backend])
        rec_q = {int(k) for k in p["excluded_qubits"]}
        rec_e = {tuple(map(int, k.split("-"))) for k in p["excluded_edges"]}
        qs, es = M.pattern_graph(p["members"])
        ops0 = p["members"]["kmo_ctrl_e1pe26_plus"]["ops"]
        cands = M.candidates(ops0, qs, es, dev, ex_q, ex_e, M.FLOOR)
        placed = M.place(cands, dev)
        rec_scores = [r["score"] for r in p["replicas_record"]]
        # decomposition of every recorded region: map replica 0 labels onto each recorded replica
        regions = []
        err_esp = err_coh = err_dur = 0.0
        base_to_r0 = {int(b): ph for b, ph in p["replicas_record"][0]["mapping"].items()}
        for k, rep in enumerate(p["replicas_record"]):
            base_to_k = {int(b): ph for b, ph in rep["mapping"].items()}
            mapping = {base_to_r0[b]: base_to_k[b] for b in base_to_r0}
            t = M.score_terms(ops0, mapping, dev)
            rec_m = p["member_replicas_record"]["kmo_ctrl_e1pe26_plus"][k]
            err_esp = max(err_esp, abs(sum(t[x] for x in ("cz", "sx", "x", "rz", "measure")) - math.log(rec_m["esp"])))
            err_coh = max(err_coh, abs(t["coherence"] - math.log(rec_m["coherence"])))
            err_dur = max(err_dur, abs(t["seconds"] - rec_m["duration_s"]))
            terms = {x: t[x] for x in ("cz", "sx", "x", "rz", "measure", "coherence")}
            dominant = min(terms, key=lambda x: terms[x])
            regions.append(
                {
                    "qubits": rep["qubits"],
                    "ln_score": t["ln_score"],
                    "score": math.exp(t["ln_score"]),
                    "terms": terms,
                    "dominant": dominant,
                    "microseconds": t["seconds"] * 1e6,
                }
            )
        # charge: record's PUB durations against the model's (max over replicas)
        charge_err = 0.0
        for name, m in p["members"].items():
            durs = []
            for rep in p["replicas_record"]:
                base_to_k = {int(b): ph for b, ph in rep["mapping"].items()}
                mapping = {base_to_r0[b]: base_to_k[b] for b in base_to_r0}
                durs.append(M.duration(M.moved_ops(m["ops"], mapping), dev))
            charge_err = max(charge_err, abs(max(durs) - p["pub_dt_record"][name] * DT))
        rec_charge = JOB_OVERHEAD + p["shots"] * sum(p["rep_delay"] + dt * DT for dt in p["pub_dt_record"].values())
        floor_all = M.candidates(ops0, qs, es, dev, ex_q, ex_e, 0.0)
        blocked = len(cands) - len(placed)
        val[backend] = {
            "exclusions_match": bool(set(ex_q) == rec_q and set(ex_e) == rec_e),
            "candidates_at_floor": len(cands),
            "record_floor_candidates": p["floor_candidates"],
            "placed": len(placed),
            "record_placed": len(rec_scores),
            "scores": [s for s, _ in placed],
            "record_scores": rec_scores,
            "max_score_error": max(abs(a - b) for (a, _), b in zip(placed, rec_scores, strict=True))
            if len(placed) == len(rec_scores)
            else None,
            "max_ln_esp_error": err_esp,
            "max_ln_coherence_error": err_coh,
            "max_duration_error_s": err_dur,
            "max_pub_duration_error_s": charge_err,
            "charge_seconds": rec_charge,
            "candidates_blocked_by_overlap_or_guard": blocked,
            "candidates_below_floor": len(floor_all) - len(cands),
            "best_below_floor": next((s for s, _ in floor_all if s < M.FLOOR * floor_all[0][0] - 1e-15), None),
        }
        dec[backend] = {
            "regions": regions,
            "dominant_counts": {
                x: sum(1 for r in regions if r["dominant"] == x)
                for x in ("cz", "sx", "x", "rz", "measure", "coherence")
            },
        }
    return val, dec


# ------------------------------------------------------------------------------------------------ 3 circuits
def ledger() -> dict[str, Any]:
    circ = json.loads((HERE / "circuits.json").read_text())
    out: dict[str, Any] = {
        "logical": {},
        "routed_dry_run_layout": circ["routed_ledger_retained_ctrl_dry_run_layout"],
        "reproduction": circ["reproduction"],
    }
    for operand in C.OPERANDS:
        tag = pkm.operand_tag(operand)
        out["logical"][tag] = {role: C.logical_ledger(role, operand) for role in UNITS}
        out["logical"][tag]["merged_totals"] = {role: C.merged_logical(role, operand) for role in UNITS}
        out["logical"][tag]["sparse_totals"] = {role: C.logical_cz(C.sparse_template(role, operand)) for role in UNITS}
    pats = M.patterns()
    out["routed_by_backend_record"] = {
        b: {
            m.removeprefix("kmo_").removesuffix("_plus"): pats[b]["members"][m]["cz_record"]
            for m in pats[b]["members"]
            if m.endswith("_plus") and "isolated" not in m
        }
        for b in M.BACKENDS
    }
    units = circ["units"]
    summary: dict[str, Any] = {}
    for key, s in circ["search"].items():
        table = s["table"]
        col = {u: sorted(row[k] for row in table) for k, u in enumerate(units)}
        summary[key] = {
            "sum_min": s["sum_min"],
            "sum_median": s["sum_median"],
            "sum_max": s["sum_max"],
            "per_unit_min_median_max": {u: [col[u][0], col[u][len(col[u]) // 2], col[u][-1]] for u in units},
            "best": {
                "perm": s["top"][0]["perm"],
                "cz": dict(zip(units, s["top"][0]["cz"], strict=True)),
                "confirm_sums": [sum(c) for c in s["top"][0]["confirm"]],
            },
        }
    out["layout_search"] = summary
    out["tiles"] = circ["tiles"]
    # where the retained dry-run compile of kingston and the offline snapshot compile (158 to 160 for e1+e18) sit
    table = circ["search"]["retained:spider_2_2_1"]["table"]
    k = units.index("ctrl_e1pe18")
    col_sorted = sorted(row[k] for row in table)
    out["ctrl_e1pe18_percentile_of_snapshot_range"] = {
        "fraction_at_or_below_125": sum(1 for v in col_sorted if v <= 125) / len(col_sorted),
        "fraction_at_or_below_158": sum(1 for v in col_sorted if v <= 158) / len(col_sorted),
        "fraction_at_or_below_160": sum(1 for v in col_sorted if v <= 160) / len(col_sorted),
    }
    return out


def operator_invariants() -> dict[str, Any]:
    eq = {}
    for role in UNITS:
        for operand in C.OPERANDS:
            a = C.pko.role_template(role, operand)
            b = C.merged_template(role, operand)
            eq[f"{role}_{pkm.operand_tag(operand)}"] = [C.operator_equal(a, b, True), C.operator_equal(a, b, False)]
    sp = {}
    for role in UNITS:
        for operand in C.OPERANDS:
            a = C.pko.role_template(role, operand)
            b = C.sparse_template(role, operand)
            sp[f"{role}_{pkm.operand_tag(operand)}"] = [C.operator_equal(a, b, True), C.operator_equal(a, b, False)]
    return {
        "operator_equal_plus_minus": eq,
        "sparse_operator_equal_plus_minus": sp,
        "all_equal": all(all(v) for v in [*eq.values(), *sp.values()]),
    }


# ------------------------------------------------------------------------------------------------ 4 designs
def design_pattern(design: dict[str, Any]) -> dict[str, Any]:
    return {u: {"ops": v["ops"]} for u, v in design["units"].items()}


def pub_charge(
    ops_by_unit: dict[str, list[list[Any]]], mappings: list[dict[int, int]], dev: M.Dev, shots: int, rep: float
) -> tuple[float, float]:
    """Charge 2 + shots * sum(rep + PUB duration) of 16 member PUBs and the isolated reference, and the sum."""
    total = 0.0
    for ops in ops_by_unit.values():
        longest = max(M.duration(M.moved_ops(ops, m), dev) for m in mappings)
        total += 2 * (rep + longest)  # plus and minus arms
    primary = max(M.duration(M.moved_ops(ops_by_unit["ctrl_e1pe26"], m), dev) for m in mappings)
    total += rep + primary  # isolated reference
    return JOB_OVERHEAD + shots * total, total


def power_cells(n: int, jobs: int) -> dict[str, Any]:
    import orientation_bit_analysis as oba

    power = json.loads(POWER_JSON.read_text())
    alpha = power["alpha_per_test"]
    out: dict[str, Any] = {}
    for tag in OPERAND_TAGS:
        stats = power["operands"][tag]["statistics"]
        for stat in ("ctrl_g16", "diff_cm"):
            effect, sd = stats[stat]["effect"], stats[stat]["sd_per_replica"]
            if n < 3:
                out[f"{stat}:{tag}"] = None
                continue
            if jobs == 1:
                cells = {"rho_any": oba.power_at(effect, sd, n, alpha)}
            else:
                cells = {
                    f"rho{int(rho)}": oba.power_at(effect, oba._design_sd(sd, rho), n, alpha) for rho in (0.0, 1.0)
                }
            out[f"{stat}:{tag}"] = {
                "effect": effect,
                "sd_per_replica": sd,
                "power_full": cells,
                "power_half": {k: None for k in cells},
            }
            for k in cells:
                if jobs == 1:
                    out[f"{stat}:{tag}"]["power_half"][k] = oba.power_at(effect / 2, sd, n, alpha)
                else:
                    out[f"{stat}:{tag}"]["power_half"][k] = oba.power_at(
                        effect / 2, oba._design_sd(sd, float(k[-1])), n, alpha
                    )
    return out


def regions_for(
    pattern: dict[str, Any], backend: str, tag: str, floor: float, guard: int, operator: list[int]
) -> tuple[list[tuple[float, dict[int, int]]], list[tuple[float, dict[int, int]]], M.Dev]:
    dev = M.Dev(M.device(backend, tag))
    ex_q, ex_e = dev.exclusions(operator)
    qs, es = M.pattern_graph(pattern)
    ops = pattern["ctrl_e1pe26"]["ops"]
    cands = M.candidates(ops, qs, es, dev, ex_q, ex_e, floor)
    return M.place(cands, dev, guard), cands, dev


def design_tables() -> dict[str, Any]:
    pats = M.patterns()
    designs = json.loads((HERE / "designs.json").read_text())
    out: dict[str, Any] = {}
    # D0: the dry-run compile of each backend (its own pattern)
    for name in ("dry_run_compile", *designs):
        rows: dict[str, Any] = {}
        for backend in M.BACKENDS:
            if name == "dry_run_compile":
                pattern = {
                    m.removeprefix("kmo_").removesuffix("_plus"): v
                    for m, v in pats[backend]["members"].items()
                    if m.endswith("_plus") and "isolated" not in m
                }
                czs = {u: pats[backend]["members"][member_key(u)]["cz_record"] for u in pattern}
            else:
                pattern = design_pattern(designs[name])
                czs = {u: designs[name]["units"][u]["cz"] for u in designs[name]["units"]}
            row: dict[str, Any] = {
                "cz": czs,
                "swap_ratio": {t: czs[f"swap_{t}"] / czs[f"ctrl_{t}"] for t in OPERAND_TAGS},
                "moved_ratio": {t: czs[f"move_{t}"] / czs[f"ctrl_{t}"] for t in OPERAND_TAGS},
            }
            variants: dict[str, Any] = {}
            for floor, guard in ((0.7, 1), (0.5, 1), (0.3, 1), (0.7, 0), (0.0, 1)):
                placed, cands, dev = regions_for(pattern, backend, "dry", floor, guard, M.OPERATOR[backend])
                charge, _ = (
                    pub_charge(
                        {u: pattern[u]["ops"] for u in pattern},
                        [m for _, m in placed],
                        dev,
                        pats[backend]["shots"],
                        pats[backend]["rep_delay"],
                    )
                    if placed
                    else (None, None)
                )
                variants[f"floor{floor}_guard{guard}"] = {
                    "candidates": len(cands),
                    "placed": len(placed),
                    "scores": [s for s, _ in placed],
                    "charge_seconds": charge,
                    "exact_max_packing": M.max_packing(cands, dev, guard) if len(cands) <= 700 else None,
                }
            row["variants"] = variants
            n = variants["floor0.7_guard1"]["placed"]
            row["power_one_job"] = power_cells(n, 1)
            row["power_two_jobs"] = power_cells(n, 2)
            # operator exclusions lifted (live health exclusions kept)
            placed_free, cands_free, dev_free = regions_for(pattern, backend, "dry", 0.7, 1, [])
            row["without_operator_exclusions"] = {
                "candidates": len(cands_free),
                "placed": len(placed_free),
                "scores": [s for s, _ in placed_free],
            }
            rows[backend] = row
        out[name] = rows
    return out


def power_by_regions() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for n in range(3, 16):
        out[str(n)] = {"one_job": power_cells(n, 1), "two_jobs": power_cells(n, 2)}
    return out


def current_calibration_prediction() -> dict[str, Any]:
    """Region counts the model predicts at the calibration read after the dry runs (fez, marrakesh recalibrated)."""
    pats = M.patterns()
    out: dict[str, Any] = {}
    for backend in M.BACKENDS:
        dev = M.Dev(M.device(backend, "now"))
        ex_q, ex_e = dev.exclusions(M.OPERATOR[backend])
        qs, es = M.pattern_graph(pats[backend]["members"])
        ops = pats[backend]["members"]["kmo_ctrl_e1pe26_plus"]["ops"]
        cands = M.candidates(ops, qs, es, dev, ex_q, ex_e, M.FLOOR)
        placed = M.place(cands, dev)
        out[backend] = {
            "calibration": dev.raw["calibration"],
            "dry_run_pattern_candidates": len(cands),
            "placed": len(placed),
            "scores": [s for s, _ in placed],
        }
    return out


# ------------------------------------------------------------------------------------------------ 5 coset blocks
def coset_tables() -> dict[str, Any]:
    out: dict[str, Any] = {"funnel": {}}
    for operand in C.OPERANDS:
        r = C.coset_funnel(operand)
        out["funnel"][pkm.operand_tag(operand)] = {
            "counts": r["funnel"],
            "weight_matched": [s for s in r["survivors"] if s["weight_matched"]],
            "survivors_with_unequal_weights": len([s for s in r["survivors"] if not s["weight_matched"]]),
        }
    coset = json.loads((HERE / "coset.json").read_text())
    out["block"] = coset["block"]
    out["logical_cz"] = coset["logical_cz"]
    out["pricing"] = {}
    for shape, s in coset["shapes"].items():
        pattern = {u: {"ops": v["ops"]} for u, v in s["units"].items()}
        row: dict[str, Any] = {
            "cz": {u: v["cz"] for u, v in s["units"].items()},
            "cz_min_median_max_sum": [s["cz_min_sum"], s["cz_median_sum"], s["cz_max_sum"]],
        }
        for backend in M.BACKENDS:
            dev = M.Dev(M.device(backend, "dry"))
            ex_q, ex_e = dev.exclusions(M.OPERATOR[backend])
            qs, es = M.pattern_graph(pattern)
            ops = pattern["ctrl"]["ops"]
            for floor in (0.7, 0.0):
                cands = M.candidates(ops, qs, es, dev, ex_q, ex_e, floor)
                placed = M.place(cands, dev)
                row[f"{backend}:floor{floor}"] = {
                    "candidates": len(cands),
                    "placed": len(placed),
                    "best_score": placed[0][0] if placed else None,
                    "worst_score": placed[-1][0] if placed else None,
                    "exact_max_packing": M.max_packing(cands, dev, 1) if len(cands) <= 700 else None,
                }
        out["pricing"][shape] = row
    return out


# ------------------------------------------------------------------------------------------------ assemble
def invariants(designs: dict[str, Any]) -> dict[str, Any]:
    pats = M.patterns()
    out: dict[str, Any] = {}
    arms = all(
        m["cz_record"] == pats[b]["members"][m_name.replace("_plus", "_minus")]["cz_record"]
        for b in M.BACKENDS
        for m_name, m in pats[b]["members"].items()
        if m_name.endswith("_plus") and m_name.replace("_plus", "_minus") in pats[b]["members"]
    )
    out["dry_run_arms_equal_cz"] = bool(arms)
    dj = json.loads((HERE / "designs.json").read_text())
    for name, d in dj.items():

        def skeleton(ops: list[list[Any]]) -> list[Any]:
            return [(n, tuple(q)) for n, q in ops if n != "rz"]

        for tag in OPERAND_TAGS:
            ctrl, xt = d["units"][f"ctrl_{tag}"]["ops"], d["units"][f"xtwin_{tag}"]["ops"]
            same = skeleton(ctrl) == skeleton(xt)
            rz_c = sorted(tuple(q) for n, q in ctrl if n == "rz")
            rz_x = sorted(tuple(q) for n, q in xt if n == "rz")
            out[f"{name}:xtwin_equals_ctrl_plus_frame:{tag}"] = {
                "non_rz_sequence_equal": same,
                "rz_count_difference_qubits": sorted({q[0] for q in set(rz_c) ^ set(rz_x)}) if rz_c != rz_x else [],
            }
        out[f"{name}:one_layout"] = len(d["layout"]) == 6 and len(set(d["layout"])) == 6
    return out


def build() -> dict[str, Any]:
    val, dec = validation_and_decomposition()
    designs = design_tables()
    return rnd(
        {
            "schema": "orientation-architecture-v1",
            "devices": device_tables(),
            "validation": val,
            "decomposition": dec,
            "ledger": ledger(),
            "operator_invariants": operator_invariants(),
            "designs": designs,
            "current_calibration_prediction": current_calibration_prediction(),
            "coset_blocks": coset_tables(),
            "invariants": invariants(designs),
            "power_by_regions": power_by_regions(),
        }
    )


def verdicts(res: dict[str, Any]) -> list[str]:
    bad: list[str] = []
    for backend, v in res["validation"].items():
        if not v["exclusions_match"]:
            bad.append(f"{backend}: exclusions differ from the record")
        if v["candidates_at_floor"] != v["record_floor_candidates"]:
            bad.append(f"{backend}: {v['candidates_at_floor']} candidates against {v['record_floor_candidates']}")
        if v["placed"] != v["record_placed"]:
            bad.append(f"{backend}: placed {v['placed']} against {v['record_placed']}")
        if v["max_score_error"] is None or v["max_score_error"] > 1e-4:
            bad.append(f"{backend}: score error {v['max_score_error']}")
        if v["max_ln_esp_error"] > 1e-6 or v["max_ln_coherence_error"] > 1e-6 or v["max_duration_error_s"] > 1e-9:
            bad.append(f"{backend}: esp, coherence or duration terms differ from the record")
        if v["max_pub_duration_error_s"] > DT:
            bad.append(f"{backend}: PUB duration differs from the record by more than one dt")
    if not res["operator_invariants"]["all_equal"]:
        bad.append("a merged circuit departs from its retained operator")
    for k, v in res["ledger"]["reproduction"].items():
        if v[0] != v[1]:
            bad.append(f"routed reproduction {k}: {v[0]} against {v[1]}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--recompute-circuits", action="store_true")
    args = ap.parse_args()
    if args.recompute_circuits:
        return subprocess.call([sys.executable, str(HERE / "orientation_recompute.py"), str(HERE / "circuits.json")])
    res = build()
    bad = verdicts(res)
    if args.write:
        if bad:
            print("\n".join(bad), file=sys.stderr)
            return 1
        (HERE / "results.json").write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
        print(
            "results.json written; placed regions: "
            + ", ".join(f"{b} {v['placed']}" for b, v in res["validation"].items())
        )
        return 0
    stored = json.loads((HERE / "results.json").read_text())
    if stored != json.loads(json.dumps(res, sort_keys=True)):
        bad.append("results.json departs from the recomputed tables")
    for line in bad:
        print(f"orientation_architecture check: {line}", file=sys.stderr)
    if not bad:
        print("orientation_architecture check: model reproduces the records and results.json is current")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
