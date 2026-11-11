"""Run-length structure of ground-prepared reads: temporal dependence of the 1 outcomes.

Data: the 153 sensors of the 24 readout-actor PUBs (pooled per qubit; list positions 8 circuits apart) and the
ground-prepared first read of every qubit of the 14 state-prep-control PUBs (prep0, x_history, remeasure arms;
list positions are consecutive shots in the single-PUB runs). Raw outcomes are two-level (`meas_type`
classified): the analysis measures run lengths of 1 outcomes and cannot name a hidden state such as |2>; a
slow drift of the marginal lengthens runs too, so an excess is a temporal dependence of unidentified origin.

Falsifier. The statistic was fixed before the first run; the Poisson reference law was replaced by the exact
conditional law after the review of 2026-11-10. A column of N reads with K ones, in uniformly random order, has
the exact law of the count M_L of runs of at least L ones: the N-K zeros cut it into g = N-K+1 gaps filled by the
K ones as a uniform weak composition, the binomial moments are
S_t = C(g, t) C(K - L t + g - 1, g - 1) / C(K + g - 1, g - 1) and
P(M_L >= m) = sum_t (-1)^(t-m) C(t-1, m-1) S_t, evaluated in Python integers (`exact_laws`). Its mean is
E_L = (N-L+1) F_L - (N-L) F_{L+1}, F_L = K(K-1)...(K-L+1) / (N(N-1)...(N-L+1)), because a run of length l >= L
holds l-L+1 windows of L ones and l-L windows of L+1. The observed count is compared with that law (one-sided,
excess); the pooled count of independently arranged columns follows the convolution of their laws (the pilot's
PUBs per qubit, and every column of a group). The group law is exact for independently arranged columns; the
columns of one PUB share shots, so a group p-value measures the excess over that reference and states no
calibrated significance. A pooled p-value below 1e-300 is written as -300. Family 1: per column
(qubit pooled over the pilot's PUBs, or one state-prep PUB), L in {2, 3, 5}. Family 2: per (dataset group, L in
{2, 3, 4, 5}) the pooled count against the pooled law. Family 3, the memory-free continuation test: per group, the
number of runs of at least 3 against sum_runs>=2 (R2 R2 / R1) (a run that reached 2 continues at the rate a run
that reached 1 did) with binomial variance, one z test per group (a normal approximation). "No temporal
dependence" means family 1 and 2 stay above the Bonferroni line, and family 3 stays consistent with 0. The law
is stationary: a slow drift of the marginal lengthens runs and is not separated from dependence at short lags.
Controls (deterministic): a hash-order scramble of a prep0 PUB reads uniform p-values; six runs of 20 ones
inserted into a scrambled column are flagged.
"""

from __future__ import annotations

import math
from typing import Any

import common
import exact_laws
import numpy as np
from scipy.stats import norm

ALPHA = 0.05
LS = (1, 2, 3, 4, 5, 6, 8)
L_COL = (2, 3, 5)
L_GROUP = (2, 3, 4, 5)


def expected_runs_at_least(n: int, k: int, big_l: int) -> float:
    def falling(m: int) -> float:
        # F_m = prod_{i<m} (K - i) / (N - i)
        out = 1.0
        for i in range(m):
            out *= max(k - i, 0) / (n - i)
        return out

    return (n - big_l + 1) * falling(big_l) - (n - big_l) * falling(big_l + 1)


def run_counts(col: np.ndarray) -> dict[int, int]:
    """Number of runs of ones with length >= L for L in LS."""
    x = np.concatenate([[0], col.astype(np.int8), [0]])
    d = np.diff(x)
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]
    lengths = ends - starts
    return {big_l: int((lengths >= big_l).sum()) for big_l in LS}


def column_record(col: np.ndarray) -> dict[str, Any]:
    n = col.size
    k = int(col.sum())
    return {
        "n": n,
        "k": k,
        "runs": run_counts(col),
        "exp": {big_l: expected_runs_at_least(n, k, big_l) for big_l in LS},
    }


def analyze(ds: dict[str, Any]) -> dict[str, Any]:
    e, qubits = common.load_errors(ds)
    cols = [column_record(e[:, i]) for i in range(e.shape[1])]
    return {
        "id": ds["id"],
        "kind": ds["kind"],
        "arm": ds["arm"],
        "run": ds["run"],
        "qubits": qubits,
        "n": e.shape[0],
        "slot_us": ds["slot_s"] * 1e6,
        "cols": cols,
    }


def pool_cols(recs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": sum(r["n"] for r in recs),
        "k": sum(r["k"] for r in recs),
        "runs": {length: sum(r["runs"][length] for r in recs) for length in LS},
        "exp": {length: sum(r["exp"][length] for r in recs) for length in LS},
    }


def exact_task(task: tuple[list[tuple[int, int]], int, int]) -> float:
    """log10 P(total run count >= observed) over independent columns (n, k) at run length L."""
    units, big_l, obs = task
    return exact_laws.runs_ge_l_log10_upper(units, big_l, obs)


def controls() -> dict[str, Any]:
    from a1_line_scan import hash_order

    cat = common.catalog()
    ds = next(
        d
        for d in common.ground_datasets(cat)
        if d["kind"] == "state_prep" and d["arm"] == "prep0" and d["run"].endswith("2026-10-18T220218.089776Z")
    )
    e, _ = common.load_errors(ds)
    n = e.shape[0]
    perm = hash_order(n)
    scr = e[perm]
    tasks: list[tuple[list[tuple[int, int]], int, int]] = []
    kinds: list[str] = []
    for i in range(e.shape[1]):
        for data, kind in ((scr, "scrambled"), (e, "raw")):
            rec = column_record(data[:, i])
            if rec["k"] >= 5:
                tasks.append(([(rec["n"], rec["k"])], 2, rec["runs"][2]))
                kinds.append(kind)
    col = scr[:, int(np.argmax(e.sum(axis=0)))].copy()
    for j in range(6):
        col[1000 + 5000 * j : 1020 + 5000 * j] = 1
    inj = column_record(col)
    base = column_record(scr[:, int(np.argmax(e.sum(axis=0)))])
    tasks.append(([(inj["n"], inj["k"])], 5, inj["runs"][5]))
    lps = common.ordered_map(exact_task, tasks, min_items=1)
    scrambled = np.array([lp for lp, kind in zip(lps[:-1], kinds, strict=True) if kind == "scrambled"])
    raw = np.array([lp for lp, kind in zip(lps[:-1], kinds, strict=True) if kind == "raw"])
    return {
        "dataset": ds["id"],
        "scrambled_fraction_L2_p_below_0.05": float(np.mean(scrambled < math.log10(0.05))),
        "raw_fraction_L2_p_below_0.05": float(np.mean(raw < math.log10(0.05))),
        "n_columns_scored": int(scrambled.size),
        "injected_six_runs_of_20": {
            "observed_runs_ge_5": inj["runs"][5],
            "expected": inj["exp"][5],
            "log10_p": lps[-1],
            "unmodified_observed_runs_ge_5": base["runs"][5],
        },
    }


def main() -> None:
    cat = common.catalog()
    datasets = [d for d in common.ground_datasets(cat)]
    results = common.ordered_map(analyze, datasets, min_items=1)
    tests: list[tuple[str, str, float]] = []

    # family 1: per column (pilot: pool each qubit over PUBs)
    col_rows = []
    pilot = [r for r in results if r["kind"] == "pilot"]
    for qi, qubit in enumerate(pilot[0]["qubits"]):
        recs = [r["cols"][qi] for r in pilot]
        col_rows.append(("pilot", f"pilot|q{qubit}", pool_cols(recs), recs))
    for r in results:
        if r["kind"] == "state_prep":
            for qi, qubit in enumerate(r["qubits"]):
                recs = [r["cols"][qi]]
                col_rows.append((f"state_prep:{r['arm']}", f"{r['id'][-34:]}|q{qubit}", pool_cols(recs), recs))
    col_tasks = [
        ([(c["n"], c["k"]) for c in recs], big_l, pooled["runs"][big_l])
        for _, _, pooled, recs in col_rows
        for big_l in L_COL
    ]
    col_lps = iter(common.ordered_map(exact_task, col_tasks, min_items=1))
    col_out = []
    for group, label, pooled, _recs in col_rows:
        for big_l in L_COL:
            obs, mean = pooled["runs"][big_l], pooled["exp"][big_l]
            lp = next(col_lps)
            tests.append((f"{label}|L{big_l}", "column", lp))
            col_out.append({"group": group, "id": label, "L": big_l, "observed": obs, "expected": mean, "log10_p": lp})

    # family 2 and 3: per group
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        key = "pilot" if r["kind"] == "pilot" else f"state_prep:{r['arm']}"
        groups.setdefault(key, []).extend(r["cols"])
    group_out = {}
    # one law per live column of every (group, L); the reduction over columns runs in this process
    plan = []
    column_tasks: list[tuple[int, int, int, str]] = []
    for key, recs in sorted(groups.items()):
        for big_l in L_GROUP:
            units = [(c["n"], c["k"]) for c in recs if c["k"] >= big_l]
            mode = exact_laws.pooled_mode(units, big_l)
            plan.append((key, big_l, mode, len(units)))
            column_tasks += [(n, k, big_l, mode) for n, k in units]
    column_laws = common.ordered_map(exact_laws.column_law, column_tasks, min_items=1)
    group_laws: dict[tuple[str, int], tuple[str, list[Any]]] = {}
    offset = 0
    for key, big_l, mode, count in plan:
        group_laws[(key, big_l)] = (mode, column_laws[offset : offset + count])
        offset += count
    for key, recs in sorted(groups.items()):
        pooled = pool_cols(recs)
        entry: dict[str, Any] = {"n_columns": len(recs), "reads": pooled["n"], "ones": pooled["k"], "by_L": {}}
        for big_l in L_GROUP:
            obs, mean = pooled["runs"][big_l], pooled["exp"][big_l]
            lo, hi = common.garwood(obs)
            law, laws = group_laws[(key, big_l)]
            if obs <= 0 or not laws:
                lp = 0.0  # P(count >= 0) = 1; an empty law list holds no column long enough for a run
            elif law == "exact":
                lp = exact_laws.pooled_exact_log10_upper(laws, obs)
            else:
                lp = exact_laws.pooled_chernoff_log10_upper(laws, obs)
            law = "exact" if law == "exact" else "chernoff_upper_bound"
            tests.append((f"{key}|pooled_L{big_l}", "group", lp))
            entry["by_L"][big_l] = {
                "observed": obs,
                "expected": mean,
                "ratio": obs / mean if mean > 0 else None,
                "ratio_ci95": [lo / mean, hi / mean] if mean > 0 else None,
                "log10_p": lp,
                "law": law,
            }
        r1 = np.array([c["runs"][1] for c in recs], dtype=float)
        r2 = np.array([c["runs"][2] for c in recs], dtype=float)
        r3 = np.array([c["runs"][3] for c in recs], dtype=float)
        a1 = np.where(r1 > 0, r2 / np.maximum(r1, 1), 0.0)
        mean3 = float((r2 * a1).sum())
        var3 = float((r2 * a1 * (1 - a1)).sum())
        z = (r3.sum() - mean3) / math.sqrt(var3) if var3 > 0 else float("nan")
        lp3 = float(math.log10(max(norm.sf(z), 1e-300))) if var3 > 0 else 0.0
        tests.append((f"{key}|continuation", "continuation", lp3))
        entry["continuation"] = {
            "runs_ge3": int(r3.sum()),
            "expected_if_memory_free_continuation": mean3,
            "ratio": float(r3.sum() / mean3) if mean3 else None,
            "z": z,
            "log10_p": lp3,
        }
        excess = np.array([c["runs"][5] - c["exp"][5] for c in recs])
        pos = np.sort(excess[excess > 0])[::-1]
        entry["runs_ge5_excess_concentration"] = {
            "columns_with_a_run_ge5": int(sum(1 for c in recs if c["runs"][5] > 0)),
            "top10_columns_share_of_positive_excess": float(pos[:10].sum() / pos.sum()) if pos.size else None,
            "top10pct_columns_share_of_positive_excess": float(pos[: max(1, len(recs) // 10)].sum() / pos.sum())
            if pos.size
            else None,
        }
        group_out[key] = entry

    corr = common.global_corrections(tests, ALPHA)
    members = set(corr.pop("_bh_member_ids", []))
    thr = corr["bonferroni_log10_threshold"]
    col_surv = [c for c in col_out if c["log10_p"] <= thr]
    col_bh = [c for c in col_out if f"{c['id']}|L{c['L']}" in members]
    n_by_group: dict[str, dict[str, int]] = {}
    for c in col_out:
        g = n_by_group.setdefault(c["group"], {"columns_x_L": 0, "p_below_0.05": 0, "bonferroni": 0, "bh": 0})
        g["columns_x_L"] += 1
        g["p_below_0.05"] += c["log10_p"] < math.log10(0.05)
        g["bonferroni"] += c["log10_p"] <= thr
        g["bh"] += f"{c['id']}|L{c['L']}" in members
    out = {
        "analysis": "a5_run_length",
        "n_columns_tested": len(col_rows),
        "n_tests": len(tests),
        "corrections": corr,
        "group_results": group_out,
        "column_summary_by_group": n_by_group,
        "column_bonferroni_survivors_top40": sorted(col_surv, key=lambda c: c["log10_p"])[:40],
        "n_column_bonferroni_survivors": len(col_surv),
        "n_column_bh_survivors": len(col_bh),
        "controls": controls(),
    }
    common.write_json(common.OUT / "a5_run_length.json", out)
    common.write_json_gz(common.OUT / "a5_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 3)] for t in tests]})
    print(out["n_columns_tested"], out["n_tests"], corr)
    for k, v in group_out.items():
        print(
            k,
            v["n_columns"],
            {
                length: (None if b["ratio"] is None else round(b["ratio"], 3), round(b["log10_p"], 1))
                for length, b in v["by_L"].items()
            },
            v["continuation"],
        )
    print(n_by_group)
    print(out["controls"])


if __name__ == "__main__":
    main()
