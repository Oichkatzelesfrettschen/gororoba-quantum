"""Calibration-age dependence of the ground-read excess in the state-prep-control runs.

Data: every retained IBM run whose records carry both an observed ground-prepared read per qubit and the
per-qubit calibration of a named snapshot: the 13 state-prep-control runs (14 PUBs; arms prep0, x_history,
remeasure first read, 66-149 qubits, 32,768 or 16,384 shots). Observed readout error is the excited fraction
f_q of the ground-prepared read: it carries the initialization excitation together with the readout error
(init_qubits imperfection plus assignment error), so the excess f_q - e10_q is named the ground-read excess,
and no part of it is attributed to readout alone. e10 is `prob_meas1_prep0` of the snapshot (a multiple of
1/4096; its binomial variance enters the error budget). Two calibration references exist per run: the plan
snapshot of record.json `backends.<name>.calibration` with the per-qubit values of
`placed_qubit_calibration`, and, for 12 runs, the execution-time snapshot of `state-prep-readout.json`
(the calibration in force when the PUB started). Age = job `running` timestamp (plan snapshot) or PUB start
(execution snapshot) minus the snapshot stamp.

Not usable: the two runs whose plan snapshot is 18 h old (the 2026-11-07 pathion maps) hold no
ground-prepared column; the 'idle_ground' PUBs hold 30 replica registers of 2 bits against 60 physical qubits
and no recorded bit-to-qubit map (a candidate map correlates with e10 at Spearman rho -0.23 and +0.08, so
neither is validated); baseline_ground has 6 qubits in one run.

Falsifier, fixed before the run. Test 1 (age slope): y_qr = f_qr - e10_qr(plan) regressed on plan-snapshot age
in hours with qubit fixed effects and (arm x rep_delay) fixed effects; cluster-robust standard error over
plan-snapshot stamps (the independent ages: runs that share a stamp share an age and a reference), t with
(clusters - 1) degrees of freedom. "No age dependence" means the slope's 95 percent interval contains 0 and
the p-value stays above 0.05 / 3. Test 2 (staleness versus freshness): for runs whose execution snapshot
differs from the plan snapshot, Delta = sum_q (f - e10_plan)^2 - (f - e10_exec)^2, with variance
sum 4 (e10_exec - e10_plan)^2 f (1 - f) / N from the read noise; a fresher snapshot predicts better when Delta
> 0 (one-sided z per run, Stouffer over the runs with a distinct reference). Test 3: Spearman correlation of
f with e10 under each reference, pooled over qubits of those runs. 3 tests; the power limit is the number of
distinct stamps and the 0.3-3.7 h age span, so a null is a bound on slopes inside that span only.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from typing import Any

import common
import numpy as np
from scipy.stats import norm, spearmanr
from scipy.stats import t as tdist

ALPHA = 0.05


def find(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find(v, key)
            if r is not None:
                return r
    return None


def parse(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def gather(cat: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for ds in common.ground_datasets(cat):
        if ds["kind"] != "state_prep":
            continue
        run = ds["run"]
        record = common.record_of(run)
        if record is None:
            raise ValueError(f"{run} has no record.json")
        placed: dict[str, Any] = {}
        for group in record["groups"]:
            placed.update(group.get("placed_qubit_calibration") or {})
        job = next(j for j in cat["jobs"] if j["job"] == ds["job"])
        stamp_plan = cat["runs"][run]["backends"][ds["backend"]]
        age_plan = (parse(job["running"]) - parse(stamp_plan)).total_seconds() / 3600
        e, qubits = common.load_errors(ds)
        n = e.shape[0]
        f = e.mean(axis=0)
        e10_plan = np.array([placed[str(q)]["prob_meas1_prep0"] for q in qubits])
        side_path = common.ROOT / run / "state-prep-readout.json"
        exec_e10, exec_stamp, age_exec = None, None, None
        if side_path.exists():
            side = json.loads(side_path.read_text())
            win = next(w for w in side["windows"] if w["edge"] == "start" and w["pub"] == ds["pub_name"])
            exec_e10 = np.array([win["qubits"][str(q)]["prob_meas1_prep0"] for q in qubits])
            exec_stamp = win["calibration"]
            age_exec = (parse(win["at"]) - parse(exec_stamp)).total_seconds() / 3600
        rows.append(
            {
                "id": ds["id"],
                "run": run,
                "arm": ds["arm"],
                "backend": ds["backend"],
                "rep_delay_us": ds["rep_delay_s"] * 1e6,
                "n": n,
                "qubits": qubits,
                "f": f,
                "e10_plan": e10_plan,
                "plan_stamp": stamp_plan,
                "age_plan_h": age_plan,
                "e10_exec": exec_e10,
                "exec_stamp": exec_stamp,
                "age_exec_h": age_exec,
            }
        )
    return rows


def slope_test(rows: list[dict[str, Any]]) -> dict[str, Any]:
    qset = sorted({q for r in rows for q in r["qubits"]})
    qidx = {q: i for i, q in enumerate(qset)}
    strata = sorted({(r["arm"], round(r["rep_delay_us"])) for r in rows})
    y_list: list[float] = []
    age_list: list[float] = []
    qi_list: list[int] = []
    st_list: list[int] = []
    cl: list[str] = []
    for r in rows:
        for q, f, e10 in zip(r["qubits"], r["f"], r["e10_plan"], strict=True):
            y_list.append(f - e10)
            age_list.append(r["age_plan_h"])
            qi_list.append(qidx[q])
            st_list.append(strata.index((r["arm"], round(r["rep_delay_us"]))))
            cl.append(r["plan_stamp"] + "|" + r["backend"])
    y, age, qi, st = np.array(y_list), np.array(age_list), np.array(qi_list), np.array(st_list)
    clusters = sorted(set(cl))
    cl_idx = np.array([clusters.index(c) for c in cl])
    # design: age, stratum dummies (drop first), qubit dummies handled by within-qubit demeaning of every column
    cols = [age] + [(st == s).astype(float) for s in range(1, len(strata))]
    x = np.stack(cols, axis=1)
    yd = y.copy()
    xd = x.copy()
    for i in range(len(qset)):
        sel = qi == i
        if sel.sum():
            yd[sel] -= y[sel].mean()
            xd[sel] -= x[sel].mean(axis=0)
    xtx = xd.T @ xd
    beta = np.linalg.lstsq(xtx, xd.T @ yd, rcond=None)[0]
    resid = yd - xd @ beta
    meat = np.zeros_like(xtx)
    for g in range(len(clusters)):
        sel = cl_idx == g
        s = xd[sel].T @ resid[sel]
        meat += np.outer(s, s)
    inv = np.linalg.pinv(xtx)
    n_obs, k = xd.shape
    g_count = len(clusters)
    cov = inv @ meat @ inv * g_count / (g_count - 1)
    se = math.sqrt(cov[0, 0])
    dof = g_count - 1
    tstat = beta[0] / se if se > 0 else float("nan")
    lo, hi = beta[0] - tdist.ppf(0.975, dof) * se, beta[0] + tdist.ppf(0.975, dof) * se
    ages_by_cluster = {
        c: float(np.mean([r["age_plan_h"] for r in rows if r["plan_stamp"] + "|" + r["backend"] == c]))
        for c in clusters
    }
    return {
        "n_rows_qubit_run": int(n_obs),
        "n_runs": len(rows),
        "n_clusters_plan_stamps": g_count,
        "age_h_by_cluster": ages_by_cluster,
        "age_range_h": [float(age.min()), float(age.max())],
        "slope_excess_per_hour": float(beta[0]),
        "se": se,
        "ci95": [float(lo), float(hi)],
        "t": float(tstat),
        "dof": dof,
        "log10_p": float(math.log10(max(2 * tdist.sf(abs(tstat), dof), 1e-300))),
        "strata_arm_rep_delay_us": [list(s) for s in strata],
        "mean_excess_overall": float(y.mean()),
    }


def leave_one_cluster_out(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stamps = sorted({r["plan_stamp"] + "|" + r["backend"] for r in rows})
    out = []
    for st in stamps:
        sub = [r for r in rows if r["plan_stamp"] + "|" + r["backend"] != st]
        if len({r["plan_stamp"] for r in sub}) < 3:
            continue
        res = slope_test(sub)
        out.append(
            {
                "left_out": st,
                "n_clusters": res["n_clusters_plan_stamps"],
                "age_range_h": res["age_range_h"],
                "slope_excess_per_hour": res["slope_excess_per_hour"],
                "ci95": res["ci95"],
                "log10_p": res["log10_p"],
            }
        )
    return out


def skill_tests(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    per_run = []
    fs, ep, ee = [], [], []
    for r in rows:
        if r["e10_exec"] is None or np.allclose(r["e10_exec"], r["e10_plan"]):
            continue
        f, a, b, n = r["f"], r["e10_plan"], r["e10_exec"], r["n"]
        delta = float(((f - a) ** 2 - (f - b) ** 2).sum())
        var = float((4 * (b - a) ** 2 * f * (1 - f) / n).sum())
        z = delta / math.sqrt(var) if var > 0 else float("nan")
        per_run.append(
            {
                "id": r["id"],
                "plan_age_h": r["age_plan_h"],
                "exec_age_h": r["age_exec_h"],
                "delta_sse_plan_minus_exec": delta,
                "z": z,
                "mean_abs_err_plan": float(np.abs(f - a).mean()),
                "mean_abs_err_exec": float(np.abs(f - b).mean()),
                "stamps": [r["plan_stamp"], r["exec_stamp"]],
            }
        )
        fs.append(f)
        ep.append(a)
        ee.append(b)
    # runs sharing the same (plan, exec) stamp pair share the reference: combine one z per distinct pair
    pairs: dict[tuple[str, str], list[float]] = {}
    for pr in per_run:
        pairs.setdefault(tuple(pr["stamps"]), []).append(pr["z"])
    distinct_z = [float(np.mean(v)) for v in pairs.values()]
    stouffer_runs = float(np.nansum([p["z"] for p in per_run]) / math.sqrt(max(len(per_run), 1)))
    stouffer_pairs = float(np.sum(distinct_z) / math.sqrt(max(len(distinct_z), 1))) if distinct_z else float("nan")
    lp_skill = float(math.log10(max(norm.sf(stouffer_pairs), 1e-300))) if distinct_z else 0.0
    skill = {
        "n_runs_with_distinct_exec_snapshot": len(per_run),
        "n_distinct_stamp_pairs": len(pairs),
        "per_run": per_run,
        "stouffer_z_over_runs": stouffer_runs,
        "stouffer_z_over_distinct_pairs": stouffer_pairs,
        "log10_p_one_sided_distinct_pairs": lp_skill,
    }
    if fs:
        f_all, a_all, b_all = np.concatenate(fs), np.concatenate(ep), np.concatenate(ee)
        rho_p = spearmanr(f_all, a_all)
        rho_e = spearmanr(f_all, b_all)
        rank = {
            "n_qubit_reads": int(f_all.size),
            "spearman_f_vs_e10_plan": float(rho_p.statistic),
            "spearman_f_vs_e10_exec": float(rho_e.statistic),
            "note": "qubit reads pool runs that share references; no p-value is assigned to the difference",
        }
    else:
        rank = {}
    return skill, rank


def main() -> None:
    cat = common.catalog()
    rows = gather(cat)
    slope = slope_test(rows)
    skill, rank = skill_tests(rows)
    loco = leave_one_cluster_out(rows)
    sidecar_diff = [
        {
            "id": r["id"],
            "max_abs_e10_plan_minus_exec": float(np.abs(r["e10_exec"] - r["e10_plan"]).max()),
            "plan_stamp": r["plan_stamp"],
            "exec_stamp": r["exec_stamp"],
        }
        for r in rows
        if r["e10_exec"] is not None
    ]
    tests = [("age_slope", "age", slope["log10_p"])]
    if skill["n_distinct_stamp_pairs"]:
        tests.append(("skill_stouffer", "skill", skill["log10_p_one_sided_distinct_pairs"]))
    corr = common.global_corrections(tests, ALPHA)
    corr.pop("_bh_member_ids", None)
    per_run_summary = [
        {
            "id": r["id"],
            "arm": r["arm"],
            "rep_delay_us": r["rep_delay_us"],
            "n_qubits": len(r["qubits"]),
            "shots": r["n"],
            "plan_stamp": r["plan_stamp"],
            "age_plan_h": r["age_plan_h"],
            "mean_f": float(r["f"].mean()),
            "mean_e10_plan": float(r["e10_plan"].mean()),
            "mean_excess_plan": float((r["f"] - r["e10_plan"]).mean()),
            "mean_excess_plan_se": float(
                math.sqrt(((r["f"] * (1 - r["f"]) / r["n"]) + r["e10_plan"] * (1 - r["e10_plan"]) / 4096).sum())
                / len(r["qubits"])
            ),
            "exec_stamp": r["exec_stamp"],
            "age_exec_h": r["age_exec_h"],
            "mean_e10_exec": None if r["e10_exec"] is None else float(r["e10_exec"].mean()),
        }
        for r in rows
    ]
    out = {
        "analysis": "a6_calibration_age",
        "n_tests": len(tests),
        "corrections": corr,
        "runs": per_run_summary,
        "age_slope": slope,
        "leave_one_stamp_out": loco,
        "plan_versus_execution_e10_in_sidecar_runs": sidecar_diff,
        "snapshot_skill": skill,
        "rank_agreement": rank,
        "not_run": {
            "pathion maps with 18 h old snapshots (2026-11-07T153325.*)": (
                "no ground-prepared column with a recorded preparation"
            ),
            "idle_ground and baseline_ground PUBs": (
                "no validated bit-to-qubit map (idle_ground) or a single 6-qubit run (baseline_ground)"
            ),
            "actor pilot": (
                "retains calibration medians only (record.json backends.ibm_fez.medians), snapshot age 0.23-0.24 h in "
                "all three jobs"
            ),
        },
    }
    common.write_json(common.OUT / "a6_calibration_age.json", out)
    common.write_json_gz(common.OUT / "a6_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 3)] for t in tests]})
    print(json.dumps({k: v for k, v in slope.items()}, indent=1))
    print({k: v for k, v in skill.items() if k != "per_run"}, rank)
    print(loco)
    print(sidecar_diff)
    for p in skill["per_run"]:
        print(p)
    for r in per_run_summary:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
