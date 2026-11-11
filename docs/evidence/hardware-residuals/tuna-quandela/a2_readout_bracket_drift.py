"""Analysis 2: Tuna-17 readout-bracket drift against elapsed time and time of day.

Falsifier, fixed before computing. "No structure" is: within a cluster of readout jobs (jobs of any series
whose consecutive start times are at most 6 h apart, so no documented platform recalibration separates them
unless it falls inside the cluster) each qubit's flip probability is constant, i.e. (a) the binomial
homogeneity chi-square over a cluster's jobs of one (qubit, prepared state) holds at its nominal level, (b)
the pooled within-cluster relative slope per hour of the flip probability has a 95 percent interval containing
zero, separately for prepared |0> (e0, P(1|0)) and prepared |1> (e1, P(0|1)), and (c) a 24 h harmonic of the
within-cluster residuals is absent. Binomial counting noise is the only null; no random draw is used.

Groups are keyed by (qubit, prepared state, full prepared X-set), so a qubit's readout is compared only between jobs \
with the same neighbor excitation.

Data. Every retained Tuna-17 circuit that holds only X gates and a full-register measurement (a pure readout
bracket), read through qi_records.read_run. Time is the job midpoint, finished_at minus half the execution time.
Brackets of one payload series are the readout jobs of its cluster; the series' payload jobs lie between them.

Limits stated before computing. Most clusters span under 1.1 h; one (pathion one-CZ null) spans 14 h. Time of
day is therefore collinear with elapsed time inside the only long cluster and confounded with calibration
epoch (documented at docs/notes/quantum_inspire/tuna-17.md, "Readout calibration drift") across clusters.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import common as c
import numpy as np
import readout_data
from scipy import stats

GAP_HOURS = 6.0
MIN_FLIPS = 20


def clusters(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    out: list[list[dict[str, Any]]] = []
    for row in rows:
        if out and row["t"] - out[-1][-1]["t"] <= GAP_HOURS * 3600:
            out[-1].append(row)
        else:
            out.append([row])
    return out


def group_points(cluster: list[dict[str, Any]]) -> dict[tuple[int, int, tuple[int, ...]], list[tuple[float, int, int]]]:
    """Groups keyed by (qubit, prepared state, full prepared X-set): neighbor excitation is part of the context."""
    points: dict[tuple[int, int, tuple[int, ...]], list[tuple[float, int, int]]] = defaultdict(list)
    for row in cluster:
        prepared = set(row["prepared_one"])
        for q in range(row["width"]):
            points[(q, int(q in prepared), tuple(row["prepared_one"]))].append(
                (row["t"], row["flips"][q], row["shots"])
            )
    return points


def weighted_fit(points: list[tuple[float, int, int]]) -> dict[str, Any] | None:
    k = np.array([p[1] for p in points], float)
    n = np.array([p[2] for p in points], float)
    t = np.array([p[0] for p in points], float) / 3600.0
    if k.sum() < MIN_FLIPS or len(points) < 2:
        return None
    fbar = (k.sum() + 0.5) / (n.sum() + 1.0)
    f = k / n
    w = n / (fbar * (1 - fbar))
    q_stat = float(((f - fbar) ** 2 * w).sum())
    tbar = float((w * t).sum() / w.sum())
    stt = float((w * (t - tbar) ** 2).sum())
    out = {"fbar": fbar, "Q": q_stat, "dof": len(points) - 1, "span_h": float(t.max() - t.min()), "points": len(points)}
    if stt > 0:
        stf = float((w * (t - tbar) * (f - fbar)).sum())
        slope = stf / stt
        out |= {
            "slope_per_h": slope,
            "z": slope * math.sqrt(stt),
            "se_slope": 1 / math.sqrt(stt),
            "stt": stt,
            "tbar_h": tbar,
        }
    return out


def main() -> None:
    rows, problems = readout_data.collect()
    cl = clusters(rows)
    per_class: dict[int, dict[str, Any]] = {0: defaultdict(float), 1: defaultdict(float)}
    rel_list: dict[int, list[float]] = {0: [], 1: []}
    z_list: dict[int, list[float]] = {0: [], 1: []}
    cluster_table: list[dict[str, Any]] = []
    group_table = []
    harmonic_rows: dict[int, list[tuple[float, float, float]]] = {0: [], 1: []}
    for index, cluster in enumerate(cl):
        points = group_points(cluster)
        q_sum = {0: 0.0, 1: 0.0}
        d_sum = {0: 0, 1: 0}
        slope_zs: list[float] = []
        span = (cluster[-1]["t"] - cluster[0]["t"]) / 3600
        for (q, s, context), pts in sorted(points.items()):
            fit = weighted_fit(pts)
            if fit is None or fit["dof"] < 1:
                continue
            q_sum[s] += fit["Q"]
            d_sum[s] += fit["dof"]
            per_class[s]["Q"] += fit["Q"]
            per_class[s]["dof"] += fit["dof"]
            if "slope_per_h" in fit:
                rel_list[s].append(fit["slope_per_h"] / fit["fbar"])
                z_list[s].append(fit["z"])
                slope_zs.append(fit["z"])
            group_table.append(
                {
                    "cluster": index,
                    "qubit": q,
                    "prepared": s,
                    "prepared_x_set": list(context),
                    "points": fit["points"],
                    "span_h": c.sig(fit["span_h"], 4),
                    "mean_flip": c.sig(fit["fbar"], 4),
                    "Q": c.sig(fit["Q"], 4),
                    "dof": fit["dof"],
                    "log10_p_homogeneity": c.sig(c.chi2_log10_sf(fit["Q"], fit["dof"]), 4),
                    "slope_rel_per_h": c.sig(fit["slope_per_h"] / fit["fbar"], 4) if "slope_per_h" in fit else None,
                    "z_slope": c.sig(fit["z"], 4) if "z" in fit else None,
                }
            )
            # harmonic residuals: weighted residual per point, one row per (job, qubit, class)
            t_h = np.array([p[0] for p in pts]) / 3600
            k = np.array([p[1] for p in pts], float)
            n = np.array([p[2] for p in pts], float)
            if span >= 3.0 and len(pts) >= 3:
                resid = (k / n - fit["fbar"]) / math.sqrt(fit["fbar"] * (1 - fit["fbar"]) / n[0])
                for tt, rr in zip(t_h, resid, strict=True):
                    harmonic_rows[s].append((float(tt), float(rr), index))
        dof_total = d_sum[0] + d_sum[1]
        cluster_table.append(
            {
                "cluster": index,
                "start_utc": datetime.fromtimestamp(cluster[0]["t"], UTC).strftime("%Y-%m-%dT%H:%MZ"),
                "span_h": c.sig(span, 4),
                "readout_jobs": len(cluster),
                "series": sorted({r["series"] for r in cluster}),
                "groups_tested": dof_total,
                "Q_over_dof_e0": c.sig(q_sum[0] / d_sum[0], 4) if d_sum[0] else None,
                "Q_over_dof_e1": c.sig(q_sum[1] / d_sum[1], 4) if d_sum[1] else None,
                "log10_p_cluster": c.sig(c.chi2_log10_sf(q_sum[0] + q_sum[1], dof_total), 4) if dof_total else None,
                "mean_signed_z_slope": c.sig(float(np.mean(slope_zs)), 4) if slope_zs else None,
            }
        )

    ledger = []
    cls_summary = {}
    for s, name in ((0, "e0 (prepared |0>, P(1|0))"), (1, "e1 (prepared |1>, P(0|1))")):
        q_total, dof_total = per_class[s]["Q"], int(per_class[s]["dof"])
        log10_p = c.chi2_log10_sf(q_total, dof_total) if dof_total else 0.0
        phi = q_total / dof_total if dof_total else float("nan")
        ledger.append(
            c.ledger_row(
                f"A2.{1 + s}",
                2,
                f"within-cluster binomial homogeneity of {name} over all readout clusters (summed chi-square)",
                log10_p,
                {"Q": c.sig(q_total), "dof": dof_total, "Q_over_dof": c.sig(phi)},
                None,
                "a value far above 1 is drift or a recalibration inside a cluster, or counting-noise overdispersion",
            )
        )
        z_all = np.array(z_list[s])
        if len(z_all) >= 5:
            chi_slope = float((z_all**2).sum())
            ledger.append(
                c.ledger_row(
                    f"A2.{3 + s}",
                    2,
                    f"any within-cluster linear drift in {name}: sum of squared per-group slope z over all (cluster, "
                    "qubit) groups",
                    c.chi2_log10_sf(chi_slope, len(z_all)),
                    {"sum_z2": c.sig(chi_slope), "groups": len(z_all), "z2_over_groups": c.sig(chi_slope / len(z_all))},
                    None,
                    "binomial null; qubits of one job share shots, so the groups are not strictly independent",
                )
            )
            neg = int((z_all < 0).sum())
            sign_p = float(stats.binomtest(neg, len(z_all), 0.5).pvalue)
            rels = np.array(rel_list[s])
            ledger.append(
                c.ledger_row(
                    f"A2.{5 + s}",
                    2,
                    f"common direction of the linear drift in {name}: groups with a negative slope against 0.5 (sign "
                    "test)",
                    math.log10(max(sign_p, 1e-300)),
                    {
                        "negative_slopes": neg,
                        "groups": len(z_all),
                        "median_relative_slope_per_hour": c.sig(float(np.median(rels))),
                        "iqr_relative_slope_per_hour": [
                            c.sig(float(np.percentile(rels, 25))),
                            c.sig(float(np.percentile(rels, 75))),
                        ],
                    },
                    c.wilson(neg, len(z_all)),
                    "a common sign would mean one monotone platform drift; mixed signs mean qubit-specific fluctuation",
                )
            )
        cls_summary[name] = {"Q": q_total, "dof": dof_total, "Q_over_dof": phi}

    # exploratory 24 h harmonic of within-cluster residuals, clusters spanning at least 3 h (kept out of the ledger)
    exploratory = []
    for s, name in ((0, "e0"), (1, "e1")):
        data = harmonic_rows[s]
        if len(data) < 20:
            continue
        t = np.array([d[0] for d in data])
        r = np.array([d[1] for d in data])
        cl_id = np.array([d[2] for d in data])
        # remove each cluster's linear elapsed-time trend, then fit a 24 h harmonic to what is left
        res = r.copy()
        for g in np.unique(cl_id):
            m = cl_id == g
            a = np.vstack([np.ones(m.sum()), t[m] - t[m].mean()]).T
            beta = np.linalg.lstsq(a, r[m], rcond=None)[0]
            res[m] = r[m] - a @ beta
        omega = 2 * math.pi / 24.0
        # the harmonic is fitted on the same detrended residuals; regressors detrended likewise
        regs = np.vstack([np.cos(omega * t), np.sin(omega * t)]).T
        regs_d = regs.copy()
        for g in np.unique(cl_id):
            m = cl_id == g
            a = np.vstack([np.ones(m.sum()), t[m] - t[m].mean()]).T
            regs_d[m] = regs[m] - a @ np.linalg.lstsq(a, regs[m], rcond=None)[0]
        gram = regs_d.T @ regs_d
        if np.linalg.matrix_rank(gram) < 2:
            continue
        coef = np.linalg.solve(gram, regs_d.T @ res)
        cov = np.linalg.inv(gram)
        chi = float(coef @ np.linalg.solve(cov, coef))
        exploratory.append(
            {
                "test": (
                    f"24 h harmonic of {name} residuals after removing each cluster's linear trend (clusters spanning "
                    "at least 3 h)"
                ),
                "amplitude_z_units": c.sig(float(math.hypot(*coef))),
                "chi2_2dof_binomial_null": c.sig(chi),
                "log10_p_binomial_null": c.sig(c.chi2_log10_sf(chi, 2), 5),
                "rows": len(data),
                "verdict": (
                    "not run as a test of time of day: only one cluster spans more than 6 h, the harmonic is "
                    "collinear with its elapsed time, and the residual dispersion is far above binomial"
                ),
            }
        )

    # bracket pairs: first and last readout of the same prepared state in each cluster, difference against elapsed time
    pair_rows = []
    for index, cluster in enumerate(cl):
        by_state: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in cluster:
            by_state[tuple(row["prepared_one"])].append(row)
        for state, jobs in by_state.items():
            if len(jobs) < 2:
                continue
            first, last = jobs[0], jobs[-1]
            zs = []
            diffs = []
            for q in range(first["width"]):
                k1, n1, k2, n2 = first["flips"][q], first["shots"], last["flips"][q], last["shots"]
                if k1 + k2 < 10:
                    continue
                pbar = (k1 + k2) / (n1 + n2)
                zs.append((k2 / n2 - k1 / n1) / math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n2)))
                diffs.append(k2 / n2 - k1 / n1)
            if zs:
                pair_rows.append(
                    {
                        "cluster": index,
                        "prepared_one_count": len(state),
                        "elapsed_h": c.sig((last["t"] - first["t"]) / 3600, 4),
                        "qubits": len(zs),
                        "chi2_over_dof": c.sig(float(np.sum(np.square(zs)) / len(zs)), 4),
                        "mean_signed_z": c.sig(float(np.mean(zs)), 4),
                        "max_abs_z": c.sig(float(np.max(np.abs(zs))), 4),
                        "median_abs_difference": c.sig(float(np.median(np.abs(diffs))), 4),
                        "max_abs_difference": c.sig(float(np.max(np.abs(diffs))), 4),
                    }
                )
    if len(pair_rows) >= 5:
        dt = [p["elapsed_h"] for p in pair_rows]
        x2 = [p["chi2_over_dof"] for p in pair_rows]
        rho = stats.spearmanr(dt, x2)
        ledger.append(
            c.ledger_row(
                "A2.7",
                2,
                "first-to-last bracket chi-square per qubit against elapsed hours (Spearman across bracket pairs)",
                math.log10(max(float(rho.pvalue), 1e-300)),
                {"rho": c.sig(float(rho.statistic)), "pairs": len(pair_rows)},
                None,
                "a positive rho says the bracket difference grows with elapsed time; clusters are confounded with "
                "series",
            )
        )

    out = {
        "analysis": 2,
        "falsifier": __doc__,
        "data": {
            "readout_jobs": len(rows),
            "clusters": len(cl),
            "read_run_problems": problems,
            "series": sorted({r["series"] for r in rows}),
            "span_utc": [
                datetime.fromtimestamp(rows[0]["t"], UTC).strftime("%Y-%m-%dT%H:%MZ"),
                datetime.fromtimestamp(rows[-1]["t"], UTC).strftime("%Y-%m-%dT%H:%MZ"),
            ],
            "runs": sorted({r["run"] for r in rows}),
            "clusters_spanning_6h_or_more": sum(1 for t in cluster_table if t["span_h"] >= 6),
        },
        "class_summary": cls_summary,
        "clusters": cluster_table,
        "bracket_pairs": pair_rows,
        "groups_with_largest_homogeneity_Q": sorted(group_table, key=lambda g: g["log10_p_homogeneity"])[:25],
        "exploratory_time_of_day": exploratory,
        "ledger": c.summarize_ledger(ledger),
    }
    path = c.write_json("a2_readout_bracket_drift.json", out)
    print(f"wrote {c.rel(path)}: {len(rows)} readout jobs, {len(cl)} clusters, {len(ledger)} tests")


if __name__ == "__main__":
    main()
