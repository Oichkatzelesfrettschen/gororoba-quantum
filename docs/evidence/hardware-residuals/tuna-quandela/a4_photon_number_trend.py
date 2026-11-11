"""Analysis 4: within-job trend of the detected-photon number across iterations, Belenos and Ascella QPU jobs.

Falsifier, fixed before computing. "No structure" is: in every QPU job whose iterations repeat an identical
circuit and input, the setting-stratified weighted slope of the mean detected photon number per sample against
the iteration index has a 95 percent interval containing zero. A positive result is a slope whose interval
excludes zero after Benjamini-Hochberg correction over every job tested, with the same sign in at least three
quarters of the job's repeated-circuit groups (monotone, not one outlier group). The retained sim:* jobs run the
same statistic as the type-I control: their p-values must be uniform and about 5 percent below 0.05.

What the counts identify. Quandela returns counts per iteration, so the iteration index is the only clock: no
iteration timestamp exists. Perceval's nb_shots_used equals the sample budget in most jobs (docs/notes/quandela/
calibration.md, strategy.md), so optical trials per iteration are unknown there and a loss rate per shot is
identifiable only where nb_shots_used exceeds samples (the yield analysis below). physical_perf is a model value
(docs/notes/quandela/literature.md section 31) and is not trended. Samples already passed the service's
default DetectorBalancing mitigation. The mean detected photon number reads loss for multiphoton inputs and the
multi-click share (g2 and dark coincidences, not loss) for single-photon inputs; the output labels each job.
Where an iteration's position is aliased with its setting (no repeated circuit inside the job) the trend is
not identifiable and the job is listed as such.

Nulls: iterations of one repeated circuit are exchangeable draws of one multinomial; the weighted slope with the
group-pooled variance is asymptotically normal (applied only when at least 30 off-mode samples exist in the
groups used). No random draw anywhere.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Any

import common as c
import numpy as np
from scipy import stats

import parallel
import qd_records as qd


def photon_stats(counts: dict[str, int]) -> tuple[int, float, float, dict[int, int]]:
    s = sum(counts.values())
    hist: dict[int, int] = defaultdict(int)
    for state, n in counts.items():
        hist[sum(int(x) for x in state.split(","))] += n
    s1 = sum(k * v for k, v in hist.items())
    s2 = sum(k * k * v for k, v in hist.items())
    return s, float(s1), float(s2), dict(hist)


def group_key(it: dict[str, Any]) -> str:
    rf = it.get("result_fields") or {}
    if "computed_circuit" in rf:
        return hashlib.sha256((rf["computed_circuit"] + rf.get("computed_input", "")).encode()).hexdigest()[:12]
    params = {k: v for k, v in it.get("iteration", {}).items() if not k.startswith("max_")}
    return "p" + hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:11]


def analyze_job(directory: Any, run: Any) -> dict[str, Any]:
    its = [i for i in (run.collected.get("iterations") or []) if "counts" in i and i["counts"]]
    out: dict[str, Any] = {
        "run": c.rel(directory),
        "platform": run.submission["platform"],
        "family": run.manifest.get("family"),
        "iterations": len(its),
    }
    if not its:
        return out | {"status": "no iterations with counts"}
    rows: list[dict[str, Any]] = []
    for index, it in enumerate(its):
        s, s1, s2, hist = photon_stats(it["counts"])
        rows.append(
            {
                "k": index,
                "key": group_key(it),
                "S": s,
                "s1": s1,
                "s2": s2,
                "hist": hist,
                "nb": (it.get("result_fields") or {}).get("nb_shots_used"),
            }
        )
    total_hist: dict[int, int] = defaultdict(int)
    for r in rows:
        for n, v in r["hist"].items():
            total_hist[n] += v
    mode_n = max(total_hist, key=lambda n: total_hist[n])
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[r["key"]].append(r)
    out["groups"] = len(groups)
    out["repeated_groups"] = sum(1 for g in groups.values() if len(g) > 1)
    out["modal_photon_number"] = mode_n
    out["photon_number_histogram"] = {str(n): v for n, v in sorted(total_hist.items())}
    out["input_kind"] = (
        "single-photon input"
        if mode_n == 1 and all(n <= 3 for n in total_hist)
        else "multiphoton input or broad detected-number distribution"
    )
    if out["repeated_groups"] == 0:
        return out | {
            "status": (
                "not identifiable: no circuit repeats inside the job, so iteration position is aliased with setting"
            )
        }
    num = den = 0.0
    events = 0
    group_info = []
    budget_varies = False
    for g in groups.values():
        if len(g) < 2:
            continue
        if len({r["S"] for r in g}) > 1:
            budget_varies = True
        s_tot = sum(r["S"] for r in g)
        m = sum(r["s1"] for r in g) / s_tot
        var = (sum(r["s2"] for r in g) - s_tot * m * m) / max(s_tot - 1, 1)
        if var <= 0:
            continue
        w = np.array([r["S"] / var for r in g])
        k = np.array([r["k"] for r in g], float)
        y = np.array([r["s1"] / r["S"] for r in g])
        kbar = float((w * k).sum() / w.sum())
        sxx = float((w * (k - kbar) ** 2).sum())
        if sxx <= 0:
            continue
        sxy = float((w * (k - kbar) * (y - (w * y).sum() / w.sum())).sum())
        num += sxy
        den += sxx
        events += sum(v for r in g for n_, v in r["hist"].items() if n_ != mode_n)
        group_info.append(
            {
                "members": len(g),
                "samples": s_tot,
                "mean_n": c.sig(m, 6),
                "slope": sxy / sxx,
                "span": int(k.max() - k.min()),
            }
        )
    if den <= 0:
        return out | {"status": "no group with variance and spread of positions"}
    beta, se = num / den, 1 / math.sqrt(den)
    mean_n = sum(r["s1"] for r in rows) / sum(r["S"] for r in rows)
    out |= {
        "off_mode_samples_in_groups": int(events),
        "slope_per_iteration": beta,
        "se": se,
        "mean_detected_photons": mean_n,
        "relative_slope_per_iteration": beta / mean_n,
        "ci95": [beta - c.Z95 * se, beta + c.Z95 * se],
        "z": beta / se,
        "same_sign_groups": [sum(1 for g in group_info if np.sign(g["slope"]) == np.sign(beta)), len(group_info)],
        "group_info": group_info[:12],
    }
    if budget_varies:
        out["status"] = (
            "confounded: the sample budget varies inside a repeated-circuit group (dwell ladder), so the iteration "
            "index aliases the budget"
        )
    elif events < 30:
        out["status"] = "underpowered: fewer than 30 off-mode samples in the groups used"
    else:
        out["status"] = "tested"
    return out


def yield_job(directory: Any, run: Any) -> dict[str, Any] | None:
    """Detected-sample yield per optical trial where nb_shots_used exceeds the samples; stratified by circuit."""
    its = [i for i in (run.collected.get("iterations") or []) if "counts" in i and i.get("result_fields")]
    rows: list[dict[str, Any]] = []
    for index, it in enumerate(its):
        s = sum(it["counts"].values())
        nb = it["result_fields"].get("nb_shots_used")
        if nb is None or nb <= s * 1.5:
            return None
        rows.append({"k": index, "key": group_key(it), "x": s, "n": nb})
    if not rows:
        return None
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[r["key"]].append(r)
    out: dict[str, Any] = {
        "run": c.rel(directory),
        "platform": run.submission["platform"],
        "iterations": len(rows),
        "groups": len(groups),
    }
    used = sum(1 for g in groups.values() if len(g) > 1)
    if used == 0:
        return out | {
            "status": "not identifiable: no circuit repeats inside the job (position aliased with setting)",
            "yield_range": [c.sig(min(r["x"] / r["n"] for r in rows), 5), c.sig(max(r["x"] / r["n"] for r in rows), 5)],
        }
    # score test of a common slope in the logit of the yield, per-group normalization by p(1-p)
    score = 0.0
    info = 0.0
    for g in groups.values():
        if len(g) < 2:
            continue
        x = np.array([r["x"] for r in g], float)
        n = np.array([r["n"] for r in g], float)
        k = np.array([r["k"] for r in g], float)
        p = x.sum() / n.sum()
        if p in (0.0, 1.0):
            continue
        kbar = float((n * p * (1 - p) * k).sum() / (n * p * (1 - p)).sum())
        score += float((k - kbar) @ (x - n * p))
        info += float(n @ ((k - kbar) ** 2) * p * (1 - p))
    z = score / math.sqrt(info) if info > 0 else float("nan")
    return out | {
        "status": "tested",
        "groups_used": used,
        "logit_slope_per_iteration": score / info,
        "se": 1 / math.sqrt(info),
        "z": z,
        "ci95": [score / info - c.Z95 / math.sqrt(info), score / info + c.Z95 / math.sqrt(info)],
    }


def job_task(directory: Any) -> dict[str, Any]:
    """One run directory: its trend analysis and, for a QPU job, its yield analysis; a failure becomes a problem row."""
    result: dict[str, Any] = {"analysis": None, "yield": None, "problems": []}
    try:
        run = qd.read_run(directory)
    except Exception as error:  # reported as a problem row, never dropped
        result["problems"].append({"run": c.rel(directory), "problem": str(error)[:160]})
        if "qpu_" in directory.name:
            result["problems"].append({"run": c.rel(directory), "yield_problem": str(error)[:160]})
        return result
    try:
        result["analysis"] = analyze_job(directory, run)
    except Exception as error:  # reported as a problem row, never dropped
        result["problems"].append({"run": c.rel(directory), "problem": str(error)[:160]})
    if "qpu_" in directory.name:
        try:
            result["yield"] = yield_job(directory, run)
        except Exception as error:  # reported as a problem row, never dropped
            result["problems"].append({"run": c.rel(directory), "yield_problem": str(error)[:160]})
    return result


def main() -> None:
    directories = [p for p in qd.run_directories() if "qpu_" in p.name or "sim_" in p.name]
    qpu: list[dict[str, Any]] = []
    sim: list[dict[str, Any]] = []
    yields: list[dict[str, Any]] = []
    problems: list[dict[str, str]] = []
    results = parallel.ordered_map(job_task, directories, min_items=2)
    for d, task in zip(directories, results, strict=True):
        problems += task["problems"]
        if task["analysis"] is not None:
            (qpu if "qpu_" in d.name else sim).append(task["analysis"])
        if task["yield"]:
            yields.append(task["yield"])
    ledger = []
    for r in qpu:
        if r.get("status") == "tested":
            ledger.append(
                c.ledger_row(
                    "A4." + r["run"].split("/")[-1][:60],
                    4,
                    f"setting-stratified slope of mean detected photons against iteration index, {r['platform']} "
                    f"{r.get('family')}",
                    c.normal_two_sided_log10(r["z"]),
                    {
                        "slope_per_iteration": c.sig(r["slope_per_iteration"]),
                        "relative_slope_per_iteration": c.sig(r["relative_slope_per_iteration"]),
                        "same_sign_groups": r["same_sign_groups"],
                    },
                    [c.sig(v) for v in r["ci95"]],
                    r["input_kind"],
                )
            )
    # yield per shot where identifiable
    for y in yields:
        if y.get("status") == "tested" and math.isfinite(y["z"]):
            ledger.append(
                c.ledger_row(
                    "A4y." + y["run"].split("/")[-1][:58],
                    4,
                    "stratified logit slope of detected-sample yield per optical trial against iteration index, "
                    f"{y['platform']}",
                    c.normal_two_sided_log10(y["z"]),
                    {
                        "logit_slope_per_iteration": c.sig(y["logit_slope_per_iteration"]),
                        "iterations": y["iterations"],
                    },
                    [c.sig(v) for v in y["ci95"]],
                    "yield per Perceval shot = samples / nb_shots_used",
                )
            )
    # control: sim jobs, same statistic
    sim_tested = [r for r in sim if r.get("status") == "tested"]
    sim_p = [math.exp(c.normal_two_sided_log10(r["z"]) * math.log(10)) for r in sim_tested]
    control: dict[str, Any] = {"sim_jobs_with_iterations": len(sim), "sim_jobs_tested": len(sim_tested)}
    if len(sim_p) >= 5:
        ks = stats.kstest(sim_p, "uniform")
        control |= {
            "fraction_p_below_0.05": c.sig(float(np.mean(np.array(sim_p) < 0.05))),
            "binomial_p_of_count_below_0.05_vs_5pct": c.sig(
                float(stats.binomtest(int(np.sum(np.array(sim_p) < 0.05)), len(sim_p), 0.05).pvalue)
            ),
            "ks_uniform_p": c.sig(float(ks.pvalue)),
            "min_p": c.sig(min(sim_p)),
        }
    out = {
        "analysis": 4,
        "falsifier": __doc__,
        "qpu_jobs": len(qpu),
        "qpu_jobs_tested": sum(1 for r in qpu if r.get("status") == "tested"),
        "qpu_jobs_underpowered": sum(1 for r in qpu if str(r.get("status", "")).startswith("underpowered")),
        "qpu_jobs_not_identifiable": sum(1 for r in qpu if str(r.get("status", "")).startswith("not identifiable")),
        "read_run_problems": problems,
        "sim_control": control,
        "ledger": c.summarize_ledger(ledger),
        "yield_jobs": yields,
        "qpu_jobs_detail": qpu,
        "sim_jobs_detail": sim,
    }
    path = c.write_json("a4_photon_number_trend.json", out)
    print(
        f"wrote {c.rel(path)}: qpu {len(qpu)} jobs, tested {out['qpu_jobs_tested']}, underpowered "
        f"{out['qpu_jobs_underpowered']}, not identifiable {out['qpu_jobs_not_identifiable']}; sim control {control}"
    )


if __name__ == "__main__":
    main()
