"""Same-shot error correlation against coupler (heavy-hex graph) distance.

Data: the 153 sensor qubits of the 24 ibm_fez readout-actor PUBs (73,728 shots; replicate PUBs of one device
session), and as a second dataset the ground-prepared first reads of the 12 wide ibm_kingston state-prep
PUBs. Distance is the hop count on the undirected graph of the backend's cz qargs (176 undirected couplers on
ibm_fez after removing the 352 directed entries' duplicates).

Falsifier, fixed before the run. Under independent qubit errors the Pearson correlation r_ij of two error
columns has mean 0 and standard deviation N^-1/2. Per PUB and distance bin d (1, 2, 3, 4, 5, 6, 7, 8-10, 11+)
the mean r over the pairs in the bin is one replicate of the bin; the PUBs of a dataset are the replicates, so
the pair sharing of qubits inside a PUB drops out of the error bar (a two-sided one-sample t test over PUBs
with the t interval as effect size). A distance trend is the across-PUB t test of the per-PUB least-squares
slope of the bin means on the bin index (bins with d >= 1). Together that is 9 bin tests + 1 trend test + 1
near-minus-far contrast (d = 1 against d >= 6) per dataset, plus the same 11 on a variant that drops every pair
whose joint count is individually significant (own Bonferroni line over the PUB's pairs), 22 tests per dataset.
"No spatial structure" means every one stays above 0.05 / 22 and the trend and contrast are consistent with 0. A
pair scan adds one exact
two-sided Poisson test per qubit pair on the pooled joint-error count against the pooled independence mean
sum_PUB K_i K_j / N (pilot: 11,628 pairs; each state-prep PUB: its own pairs), Bonferroni over all pair tests.
"""

from __future__ import annotations

import math
from typing import Any

import common
import numpy as np
from scipy.stats import poisson
from scipy.stats import t as tdist

ALPHA = 0.05
BINS = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 10), (11, 99)]


def bin_index(d: np.ndarray) -> np.ndarray:
    out = -np.ones(d.shape, dtype=np.int64)
    for k, (lo, hi) in enumerate(BINS):
        out[(d >= lo) & (d <= hi)] = k
    return out


def analyze(ds: dict[str, Any]) -> dict[str, Any]:
    e, qubits = common.load_errors(ds)
    n, q = e.shape
    ef = e.astype(np.float64)
    k = ef.sum(axis=0)
    joint = ef.T @ ef
    p = k / n
    ok = (p > 0) & (p < 1)
    cov = joint / n - np.outer(p, p)
    sd = np.sqrt(p * (1 - p))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = cov / np.outer(sd, sd)
    graph = common.coupling_graph(ds["backend"])
    dist = common.graph_distances(graph)
    qi = np.array(qubits)
    d = dist[np.ix_(qi, qi)]
    bins = bin_index(d)
    upper = np.triu(np.ones((q, q), dtype=bool), 1) & np.outer(ok, ok) & (d > 0)
    rbin = []
    # robust variant: drop the pairs whose joint count is individually significant (own Bonferroni line over the
    # PUB's pairs)
    expected = np.outer(k, k) / n
    upper_tail = poisson.logsf(joint - 1, np.maximum(expected, 1e-12)) / math.log(10)
    lower_tail = poisson.logcdf(joint, np.maximum(expected, 1e-12)) / math.log(10)
    pair_lp = np.minimum(0.0, math.log10(2) + np.minimum(upper_tail, lower_tail))
    n_pairs = int(upper.sum())
    outlier = pair_lp <= math.log10(ALPHA) - math.log10(max(n_pairs, 1))
    rbin_trim = []
    for kk in range(len(BINS)):
        sel = upper & (bins == kk)
        rbin.append((float(r[sel].mean()), int(sel.sum())) if sel.any() else (None, 0))
        sel_t = sel & ~outlier
        rbin_trim.append((float(r[sel_t].mean()), int(sel_t.sum())) if sel_t.any() else (None, 0))
    return {
        "id": ds["id"],
        "kind": ds["kind"],
        "arm": ds["arm"],
        "run": ds["run"],
        "backend": ds["backend"],
        "n": n,
        "q": q,
        "qubits": qubits,
        "k": k.astype(int).tolist(),
        "joint": joint.astype(np.int32),
        "rbin": rbin,
        "rbin_trim": rbin_trim,
        "n_outlier_pairs_removed": int((outlier & upper).sum()),
        "mean_r_all_pairs": float(r[upper].mean()),
    }


def replicate_tests(
    results: list[dict[str, Any]], label: str, key: str = "rbin"
) -> tuple[dict[str, Any], list[tuple[str, str, float]]]:
    tests: list[tuple[str, str, float]] = []
    rows = []
    mat = np.full((len(results), len(BINS)), np.nan)
    pairs = np.zeros((len(results), len(BINS)))
    for i, r in enumerate(results):
        for k, (v, c) in enumerate(r[key]):
            if v is not None:
                mat[i, k] = v
                pairs[i, k] = c
    for k, (lo, hi) in enumerate(BINS):
        col = mat[:, k]
        col = col[~np.isnan(col)]
        if col.size < 3:
            rows.append({"bin": f"{lo}-{hi}", "n_pubs": int(col.size), "note": "fewer than 3 replicates"})
            continue
        mean = float(col.mean())
        se = float(col.std(ddof=1) / math.sqrt(col.size))
        tcrit = float(tdist.ppf(0.975, col.size - 1))
        t_stat = mean / se if se > 0 else float("inf")
        lp = float(math.log10(max(2 * tdist.sf(abs(t_stat), col.size - 1), 1e-300)))
        null_se = float(
            np.nanmean(
                [
                    1 / math.sqrt(results[i]["n"] * max(pairs[i, k], 1))
                    for i in range(len(results))
                    if not np.isnan(mat[i, k])
                ]
            )
            / math.sqrt(col.size)
        )
        rows.append(
            {
                "bin": f"{lo}-{hi}",
                "n_pubs": int(col.size),
                "mean_pairs_per_pub": float(pairs[:, k][pairs[:, k] > 0].mean()),
                "mean_r": mean,
                "ci95": [mean - tcrit * se, mean + tcrit * se],
                "t": t_stat,
                "log10_p": lp,
                "independence_null_se": null_se,
            }
        )
        tests.append((f"{label}|bin{lo}-{hi}", f"{label}_bin", lp))
    # trend: per-PUB slope across bins (positions 0..8) over available bins
    slopes = []
    for i in range(len(results)):
        xs = np.array([k for k in range(len(BINS)) if not np.isnan(mat[i, k])], dtype=float)
        ys = np.array([mat[i, int(k)] for k in xs])
        if xs.size >= 4:
            slopes.append(float(np.polyfit(xs, ys, 1)[0]))
    trend: dict[str, Any] = {"n_pubs": len(slopes)}
    if len(slopes) >= 3:
        sl = np.array(slopes)
        se = float(sl.std(ddof=1) / math.sqrt(sl.size))
        t_stat = float(sl.mean() / se) if se > 0 else float("inf")
        lp = float(math.log10(max(2 * tdist.sf(abs(t_stat), sl.size - 1), 1e-300)))
        tcrit = float(tdist.ppf(0.975, sl.size - 1))
        trend.update(
            {
                "mean_slope_r_per_bin": float(sl.mean()),
                "ci95": [float(sl.mean() - tcrit * se), float(sl.mean() + tcrit * se)],
                "t": t_stat,
                "log10_p": lp,
            }
        )
        tests.append((f"{label}|trend", f"{label}_trend", lp))
    # near minus far: d = 1 against pooled d >= 6 (pair-count weighted per PUB)
    contrast = []
    for i in range(len(results)):
        near = mat[i, 0]
        far_w = pairs[i, 5:]
        far_v = mat[i, 5:]
        good = ~np.isnan(far_v) & (far_w > 0)
        if not np.isnan(near) and good.any():
            contrast.append(float(near - np.average(far_v[good], weights=far_w[good])))
    cont: dict[str, Any] = {"n_pubs": len(contrast)}
    if len(contrast) >= 3:
        c_arr = np.array(contrast)
        se = float(c_arr.std(ddof=1) / math.sqrt(c_arr.size))
        t_stat = float(c_arr.mean() / se) if se > 0 else float("inf")
        lp = float(math.log10(max(2 * tdist.sf(abs(t_stat), c_arr.size - 1), 1e-300)))
        tcrit = float(tdist.ppf(0.975, c_arr.size - 1))
        cont.update(
            {
                "mean_r_near_minus_far": float(c_arr.mean()),
                "ci95": [float(c_arr.mean() - tcrit * se), float(c_arr.mean() + tcrit * se)],
                "t": t_stat,
                "log10_p": lp,
            }
        )
        tests.append((f"{label}|near_minus_far", f"{label}_contrast", lp))
    return {"bins": rows, "trend": trend, "near_minus_far": cont}, tests


def pair_scan(
    results: list[dict[str, Any]], label: str, backend: str
) -> tuple[dict[str, Any], list[tuple[str, str, float]]]:
    """Pooled joint-error count per pair against the pooled independence mean (same qubit set in every PUB)."""
    qubits = results[0]["qubits"]
    q = len(qubits)
    dist = common.graph_distances(common.coupling_graph(backend))
    obs = np.zeros((q, q))
    exp = np.zeros((q, q))
    for r in results:
        if r["qubits"] != qubits:
            raise ValueError("pair scan pools PUBs with one qubit set")
        k = np.array(r["k"], dtype=np.float64)
        obs += r["joint"]
        exp += np.outer(k, k) / r["n"]
    iu = np.triu_indices(q, 1)
    o, m = obs[iu].astype(int), exp[iu]
    upper = poisson.logsf(o - 1, m) / math.log(10)
    lower = poisson.logcdf(o, m) / math.log(10)
    lp = np.minimum(0.0, math.log10(2) + np.minimum(upper, lower))
    tests = [
        (f"{label}|pair{qubits[a]}-{qubits[b]}", f"{label}_pair", float(v))
        for a, b, v in zip(iu[0], iu[1], lp, strict=True)
    ]
    order = np.argsort(lp)[:10]
    top = [
        {
            "qubits": [qubits[iu[0][i]], qubits[iu[1][i]]],
            "graph_distance": int(dist[qubits[iu[0][i]], qubits[iu[1][i]]]),
            "observed": int(o[i]),
            "expected": float(m[i]),
            "log10_p": float(lp[i]),
        }
        for i in order
    ]
    z = (o - m) / np.sqrt(np.maximum(m, 1e-9))
    summary = {
        "n_pairs": int(len(o)),
        "pooled_observed": int(o.sum()),
        "pooled_expected": float(m.sum()),
        "ratio": float(o.sum() / m.sum()),
        "z_mean": float(z.mean()),
        "z_sd": float(z.std()),
        "top10": top,
    }
    return summary, tests


def main() -> None:
    cat = common.catalog()
    datasets = [d for d in common.ground_datasets(cat) if d["kind"] == "pilot" or len(d["columns"]) >= 24]
    results = common.ordered_map(analyze, datasets, min_items=1)
    tests: list[tuple[str, str, float]] = []
    out: dict[str, Any] = {"analysis": "a3_coupler_distance", "datasets": {}}
    for kind, label, backend in (
        ("pilot", "pilot_fez", "ibm_fez"),
        ("state_prep", "state_prep_kingston", "ibm_kingston"),
    ):
        rs = [r for r in results if r["kind"] == kind]
        rep, rep_tests = replicate_tests(rs, label)
        tests += rep_tests
        rep_trim, rep_trim_tests = replicate_tests(rs, label + "_trimmed", key="rbin_trim")
        tests += rep_trim_tests
        entry: dict[str, Any] = {
            "backend": backend,
            "n_pubs": len(rs),
            "n_shots_total": int(sum(r["n"] for r in rs)),
            "n_columns": sorted({r["q"] for r in rs}),
            "mean_r_all_pairs_per_pub": [round(r["mean_r_all_pairs"], 6) for r in rs],
            "replicate_tests": rep,
            "replicate_tests_pair_outliers_removed": rep_trim,
            "n_outlier_pairs_removed_per_pub": [r["n_outlier_pairs_removed"] for r in rs],
        }
        if kind == "pilot":
            summ, pair_tests = pair_scan(rs, label, backend)
            entry["pair_scan"] = summ
            tests += pair_tests
        else:
            per_pub = {}
            for r in rs:
                summ, pt = pair_scan([r], f"{label}:{r['id'][-34:]}", backend)
                per_pub[r["id"]] = {k_: v for k_, v in summ.items() if k_ != "top10"} | {"top3": summ["top10"][:3]}
                tests += pt
            entry["pair_scan_per_pub"] = per_pub
        out["datasets"][kind] = entry
    corr = common.global_corrections(tests, ALPHA)
    members = set(corr.pop("_bh_member_ids", []))
    out["n_tests"] = len(tests)
    out["corrections"] = corr
    out["survivors_bonferroni"] = [
        {"id": tid, "log10_p": lp}
        for tid, _, lp in sorted(tests, key=lambda t: t[2])
        if lp <= corr["bonferroni_log10_threshold"]
    ][:60]
    out["n_survivors_bonferroni"] = corr["n_bonferroni"]
    out["n_survivors_bh"] = corr["n_bh"]
    out["bh_survivors_non_pair"] = sorted(t for t in members if "|pair" not in t)
    common.write_json(common.OUT / "a3_coupler_distance.json", out)
    common.write_json_gz(common.OUT / "a3_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 4)] for t in tests]})
    print(out["n_tests"], corr)
    for kind, e in out["datasets"].items():
        print(kind, e["n_pubs"], e["replicate_tests"]["trend"], e["replicate_tests"]["near_minus_far"])
        for b in e["replicate_tests"]["bins"]:
            print(
                "  ",
                {
                    k: (round(v, 5) if isinstance(v, float) else v)
                    for k, v in b.items()
                    if k in ("bin", "n_pubs", "mean_r", "t", "log10_p", "independence_null_se")
                },
            )
    print(
        out["datasets"]["pilot"]["pair_scan"]["ratio"],
        out["datasets"]["pilot"]["pair_scan"]["z_sd"],
        out["datasets"]["pilot"]["pair_scan"]["top10"][:3],
    )
    print(out["survivors_bonferroni"][:10], out["bh_survivors_non_pair"])


if __name__ == "__main__":
    main()
