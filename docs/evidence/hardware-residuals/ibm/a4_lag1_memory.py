"""Lag-1 temporal dependence of errors: P(error of qubit i at shot n+1 | error of qubit j at shot n) against the
marginal.

Generalizes the qubit-147 successor effect of docs/evidence/primorial_cover/q147-remeasure/README.md
(prep0 reads 1 at shot s+1 in 0.0825 of the shots after a remeasure first read of 1 at shot s, against 0.020
after a 0). Data: the 153 sensors of the 24 readout-actor pilot PUBs, pooled per ordered qubit pair across the
PUBs (list positions of one PUB lie one job slot, 8 circuits, apart); and the 12 wide single-PUB state-prep
runs on ibm_kingston, one PUB per job, where the next list position is the next physical shot.

Falsifier, fixed before the run. For the error indicator matrix E, the count C_ji = sum_n e_j[n] e_i[n+1]
has, under shots that are exchangeable (a uniformly random reordering of whole shot rows), the exact mean
(K_j K_i - J_ji) / N, where J_ji is the same-shot joint count. Each ordered pair (153 x 153 = 23,409 for the
pilot; Q^2 per state-prep PUB) gets one two-sided test.
- Diagonal (j = i, the per-qubit adjacency of ones): the law of the adjacent (1, 1) count given (N, K) is exact,
  P(R = r) = C(K-1, r-1) C(N-K+1, r) / C(N, K) for R runs of ones and C = K - R; the pilot's pooled count follows
  the convolution of its 24 PUB laws (`exact_laws.adjacency_pmf`).
- Off-diagonal (j != i): the exact joint law of C_ji over arrangements of rows is not computed; a Poisson law at the
  exact mean stands in as an approximation. The exact variance of C_ji (`exact_laws.lag1_cross_moments`) is
  reported beside the p-values: a variance above the mean makes the Poisson upper tail anti-conservative, a
  variance below it makes the tail conservative.
Slow drift also raises lag-1 counts, so every survivor is re-evaluated at lags 2 and 3 with the Poisson law at
the exact mean: a dependence confined to one shot decays at once, drift does not. A drift-robust variant of the diagonal
test permutes shots only inside consecutive blocks of 512 shots (the block length of a2_burst.py), excluding
the pairs that straddle a block boundary from the count and from the law; its exact law is the convolution of
the blocks' adjacency laws. A block spans 16 to 134 ms at the state-prep slots, so nonstationarity faster than a
block stays inside the block null: a surviving excess is a temporal dependence at lags of a few shots beyond
512-shot nonstationarity and does not identify its mechanism. The block-local results sit beside the ledger.
"No dependence" means no pair below the Bonferroni line over all these tests and a flat distribution of the
diagonal z scores.

Positive control from the repository record: the q147 successor (remeasure first read at shot s against the
prep0 read at shot s+1, three static PUBs in one job, one list step = one physical step) must reproduce
0.0825 against 0.020 with the same detector (the detector's count and mean, applied to two PUBs).
"""

from __future__ import annotations

import math
from typing import Any, cast

import common
import exact_laws
import numpy as np
from scipy.stats import poisson

ALPHA = 0.05
LAGS = (1, 2, 3)
BLOCK = 512


def lag_counts(e: np.ndarray, lag: int) -> np.ndarray:
    ef = e.astype(np.float32)
    return (ef[:-lag].T @ ef[lag:]).astype(np.int64)


def log10_two_sided(obs: np.ndarray, mean: np.ndarray) -> np.ndarray:
    mean = np.maximum(mean, 1e-12)
    upper = poisson.logsf(obs - 1, mean) / math.log(10)
    lower = poisson.logcdf(obs, mean) / math.log(10)
    return np.minimum(0.0, math.log10(2) + np.minimum(upper, lower))


def analyze(ds: dict[str, Any]) -> dict[str, Any]:
    e, qubits = common.load_errors(ds)
    n, q = e.shape
    ef = e.astype(np.float32)
    joint = (ef.T @ ef).astype(np.int64)
    k = e.sum(axis=0).astype(np.int64)
    blocks = np.array_split(np.arange(n), max(1, n // BLOCK))
    starts = np.array([b[0] for b in blocks])
    ends = np.array([b[-1] for b in blocks])
    block_k = np.add.reduceat(e.astype(np.int64), starts, axis=0)
    boundary = (e[ends[:-1]].astype(np.int64) * e[starts[1:]].astype(np.int64)).sum(axis=0)
    adjacency = (e[:-1].astype(np.int64) * e[1:].astype(np.int64)).sum(axis=0)
    out = {
        "id": ds["id"],
        "kind": ds["kind"],
        "arm": ds["arm"],
        "run": ds["run"],
        "backend": ds["backend"],
        "n": n,
        "q": q,
        "qubits": qubits,
        "slot_us": ds["slot_s"] * 1e6,
        "k": k,
        "joint": joint,
        "lag": {lag: lag_counts(e, lag) for lag in LAGS},
        "marginal_prev": {lag: e[:-lag].sum(axis=0).astype(np.int64) for lag in LAGS},
        "block_sizes": [int(b.size) for b in blocks],
        "block_k": block_k,
        "block_adjacency": adjacency - boundary,
    }
    return out


def expected_counts(r: dict[str, Any], lag: int) -> np.ndarray:
    """Exact mean of C_ji at the lag under a uniformly random order of whole shot rows.

    The mean is (N - lag)(K_j K_i - J_ji) / (N (N - 1)).
    """
    n = r["n"]
    k = r["k"].astype(np.float64)
    return (n - lag) * (np.outer(k, k) - r["joint"]) / (n * (n - 1))


def pooled(results: list[dict[str, Any]], lag: int) -> tuple[np.ndarray, np.ndarray]:
    obs = cast(np.ndarray, sum(r["lag"][lag] for r in results))
    exp = cast(np.ndarray, sum(expected_counts(r, lag) for r in results))
    return obs, exp


def diag_tasks(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One exact-law task per qubit: the pooled global adjacency law and the block-local one."""
    tasks = []
    for i in range(len(results[0]["qubits"])):
        tasks.append(
            {
                "units": [(r["n"], int(r["k"][i])) for r in results],
                "observed": int(sum(r["lag"][1][i, i] for r in results)),
                "block_units": [
                    (size, int(k_b))
                    for r in results
                    for size, k_b in zip(r["block_sizes"], r["block_k"][:, i], strict=True)
                ],
                "block_observed": int(sum(r["block_adjacency"][i] for r in results)),
            }
        )
    return tasks


def diag_law(task: dict[str, Any]) -> dict[str, float]:
    """Exact two-sided log10 p of one qubit's lag-1 adjacency, globally and inside 512-shot blocks."""
    out: dict[str, float] = {}
    for tag, units, obs in (
        ("global", task["units"], task["observed"]),
        ("block", task["block_units"], task["block_observed"]),
    ):
        pmf = exact_laws.convolve([exact_laws.adjacency_pmf(n, k) for n, k in units if k >= 2])
        support = np.arange(pmf.size)
        mean = float((pmf * support).sum())
        var = float((pmf * support**2).sum()) - mean * mean
        out[f"lp_{tag}"] = exact_laws.log10_two_sided(pmf, obs)
        out[f"mean_{tag}"] = mean
        out[f"sd_{tag}"] = math.sqrt(max(var, 0.0))
        out[f"observed_{tag}"] = float(obs)
    return out


def cross_variance(results: list[dict[str, Any]]) -> np.ndarray:
    """Exact variance of the pooled lag-1 count of every ordered pair (independent PUBs add)."""
    var = np.zeros((len(results[0]["qubits"]),) * 2)
    for r in results:
        k = r["k"].astype(np.float64)
        var += exact_laws.lag1_cross_moments(r["n"], k[:, None], k[None, :], r["joint"].astype(np.float64))[1]
    return var


def evaluate(
    results: list[dict[str, Any]], label: str, diag_laws: list[dict[str, float]]
) -> tuple[dict[str, Any], list[tuple[str, str, float]]]:
    qubits = results[0]["qubits"]
    q = len(qubits)
    dist = common.graph_distances(common.coupling_graph(results[0]["backend"]))
    obs1, exp1 = pooled(results, 1)
    lp = log10_two_sided(obs1, exp1)  # Poisson approximation: the law of the off-diagonal ordered pairs
    lp_poisson_diag = np.diag(lp).copy()
    lp[np.arange(q), np.arange(q)] = [d["lp_global"] for d in diag_laws]  # exact adjacency law on the diagonal
    tests = [
        (f"{label}|{qubits[j]}->{qubits[i]}", f"{label}_{'diag' if i == j else 'cross'}", float(lp[j, i]))
        for j in range(q)
        for i in range(q)
    ]
    thr = math.log10(ALPHA) - math.log10(q * q)
    # drift control at lags 2 and 3, pooled the same way
    obs2, exp2 = pooled(results, 2)
    obs3, exp3 = pooled(results, 3)
    diag = np.arange(q)
    k_tot = sum(r["k"] for r in results).astype(np.float64)
    n_tot = sum(r["n"] for r in results)
    marginal = k_tot / n_tot
    prev = sum(r["marginal_prev"][1] for r in results).astype(np.float64)
    cond = obs1[diag, diag] / np.maximum(prev, 1)
    ratio = cond / np.maximum(marginal, 1e-12)
    d_obs, d_exp = obs1[diag, diag], exp1[diag, diag]
    z_diag = (d_obs - d_exp) / np.maximum(np.array([d["sd_global"] for d in diag_laws]), 1e-9)
    sig_diag = lp[diag, diag] <= thr
    pos = sig_diag & (d_obs > d_exp)
    neg = sig_diag & (d_obs < d_exp)

    # lag decay among the significant positive diagonal qubits
    def excess(obs: np.ndarray, exp: np.ndarray, sel: np.ndarray) -> float:
        return float((obs[diag, diag][sel].sum() - exp[diag, diag][sel].sum()) / max(exp[diag, diag][sel].sum(), 1e-12))

    decay = {}
    for name, sel in (("positive", pos), ("negative", neg)):
        if sel.any():
            decay[name] = {
                "n_qubits": int(sel.sum()),
                "lag1_excess_over_mean": excess(obs1, exp1, sel),
                "lag2_excess_over_mean": excess(obs2, exp2, sel),
                "lag3_excess_over_mean": excess(obs3, exp3, sel),
            }
    off = ~np.eye(q, dtype=bool)
    sig_off = (lp <= thr) & off
    # chain prediction for the cross counts: same-shot correlation of j with i, then i's own lag-1 dependence
    joint_tot = sum(r["joint"] for r in results).astype(np.float64)
    prev_all = sum(r["marginal_prev"][1] for r in results).astype(np.float64)
    a_mem = obs1[diag, diag] / np.maximum(prev, 1)
    b_mem = np.maximum((k_tot - obs1[diag, diag]) / np.maximum(n_tot - prev, 1), 0)  # P(next = 1 | prev = 0)
    q_ji = joint_tot / np.maximum(k_tot[:, None], 1)  # P(i = 1 | j = 1) at the same shot, row j column i
    chain = prev_all[:, None] * (q_ji * a_mem[None, :] + (1 - q_ji) * b_mem[None, :])
    survivors = []
    for j, i in np.argwhere(sig_off)[np.argsort(lp[sig_off])][:25]:
        survivors.append(
            {
                "from": qubits[j],
                "to": qubits[i],
                "graph_distance": int(dist[qubits[j], qubits[i]]),
                "observed": int(obs1[j, i]),
                "expected": float(exp1[j, i]),
                "ratio": float(obs1[j, i] / exp1[j, i]),
                "chain_prediction_same_shot_times_dependence": float(chain[j, i]),
                "observed_over_chain": float(obs1[j, i] / max(chain[j, i], 1e-12)),
                "log10_p": float(lp[j, i]),
                "lag2_obs_exp": [int(obs2[j, i]), float(exp2[j, i])],
                "lag3_obs_exp": [int(obs3[j, i]), float(exp3[j, i])],
            }
        )
    near = (dist[np.ix_(qubits, qubits)] == 1) & off
    var_cross = cross_variance(results)
    informative = off & (exp1 >= 0.5)
    ratio_var = var_cross[informative] / exp1[informative]
    blk_obs = np.array([d["observed_block"] for d in diag_laws])
    blk_mean = np.array([d["mean_block"] for d in diag_laws])
    blk_sd = np.array([d["sd_block"] for d in diag_laws])
    sig_blk = np.array([d["lp_block"] for d in diag_laws]) <= thr
    summary = {
        "n_pubs": len(results),
        "n_shots_total": int(n_tot),
        "n_qubits": q,
        "n_tests": q * q,
        "bonferroni_log10_threshold_own_family": thr,
        "diag_law": "exact adjacency law, convolved over the pooled PUBs",
        "cross_law": "Poisson at the exact mean (approximation; see cross_variance_over_mean)",
        "diag_n_bonferroni_poisson_approximation": int((lp_poisson_diag <= thr).sum()),
        "diag_n_bonferroni": int(sig_diag.sum()),
        "diag_n_positive": int(pos.sum()),
        "diag_n_negative": int(neg.sum()),
        "diag_median_ratio_cond_to_marginal": float(np.median(ratio[marginal > 0])),
        "diag_ratio_interquartile": [
            float(np.percentile(ratio[marginal > 0], 25)),
            float(np.percentile(ratio[marginal > 0], 75)),
        ],
        "diag_z_mean": float(z_diag.mean()),
        "diag_z_sd": float(z_diag.std()),
        "diag_decay_at_lags": decay,
        "diag_top5": [
            {
                "qubit": qubits[i],
                "marginal": float(marginal[i]),
                "p_next_given_error": float(cond[i]),
                "ratio": float(ratio[i]),
                "ratio_ci95": [
                    float(g / max(prev[i], 1) / max(marginal[i], 1e-12)) for g in common.garwood(int(d_obs[i]))
                ],
                "observed": int(d_obs[i]),
                "expected": float(d_exp[i]),
                "log10_p": float(lp[i, i]),
            }
            for i in np.argsort(lp[diag, diag])[:5]
        ],
        "cross_variance_over_mean": {
            "pairs_with_expected_at_least_0.5": int(informative.sum()),
            "median": float(np.median(ratio_var)) if ratio_var.size else None,
            "fraction_above_1": float((ratio_var > 1).mean()) if ratio_var.size else None,
            "pooled_variance_over_pooled_mean": float(var_cross[off].sum() / exp1[off].sum()),
        },
        "cross_n_pairs_variance_above_mean": int(((var_cross > exp1 * (1 + 1e-9)) & off).sum()),
        "diag_block_local": {
            "block_shots": BLOCK,
            "n_bonferroni": int(sig_blk.sum()),
            "n_positive": int((sig_blk & (blk_obs > blk_mean)).sum()),
            "n_negative": int((sig_blk & (blk_obs < blk_mean)).sum()),
            "n_bonferroni_in_both_global_and_block": int((sig_blk & sig_diag).sum()),
            "z_mean": float(((blk_obs - blk_mean) / np.maximum(blk_sd, 1e-9)).mean()),
            "z_sd": float(((blk_obs - blk_mean) / np.maximum(blk_sd, 1e-9)).std()),
            "pooled_observed_over_expected": float(blk_obs.sum() / max(blk_mean.sum(), 1e-12)),
        },
        "cross_n_bonferroni": int(sig_off.sum()),
        "cross_n_positive": int((sig_off & (obs1 > exp1)).sum()),
        "cross_z_mean": float(((obs1 - exp1) / np.sqrt(np.maximum(exp1, 1e-9)))[off].mean()),
        "cross_z_sd": float(((obs1 - exp1) / np.sqrt(np.maximum(exp1, 1e-9)))[off].std()),
        "cross_pooled_ratio_coupled_pairs": float(obs1[near].sum() / exp1[near].sum()) if near.any() else None,
        "cross_pooled_ratio_uncoupled_pairs": float(obs1[off & ~near].sum() / exp1[off & ~near].sum()),
        "cross_coupled_observed_over_chain": float(obs1[near].sum() / chain[near].sum()) if near.any() else None,
        "cross_coupled_chain_over_expected": float(chain[near].sum() / exp1[near].sum()) if near.any() else None,
        "cross_survivors_top25": survivors,
    }
    return summary, tests


def q147_control() -> dict[str, Any]:
    run = "results/live/2026-10-27T204605.871056Z"
    cat = common.catalog()
    job = next(j for j in cat["jobs"] if j["run"] == run)
    pubs = {p["name"]: p for p in job["pubs"]}
    a = common.load_pub(pubs["ibm_kingston_static_pub_03"]["file"])  # remeasure: bit 0 is the first read
    b = common.load_pub(pubs["ibm_kingston_static_pub_01"]["file"])  # prep0
    # q147 is g0 in every PUB of this run
    first_read = a["regs"]["g0_r0_c"][:, 0].astype(np.int64)
    prep = b["regs"]["g0_r0_c"][:, 0].astype(np.int64)
    n = first_read.size
    ka, kb = int(first_read.sum()), int(prep.sum())
    jab = int((first_read * prep).sum())
    count = int((first_read[:-1] * prep[1:]).sum())
    exp = (ka * kb - jab) / n
    given1 = count / int(first_read[:-1].sum())
    given0 = int(((1 - first_read[:-1]) * prep[1:]).sum()) / int((1 - first_read[:-1]).sum())
    z = (count - exp) / math.sqrt(exp)
    # earlier-step arm: prep0 at s against the remeasure read at s+1 (a successor cannot act backward)
    back = int((prep[:-1] * first_read[1:]).sum())
    exp_back = (kb * ka - jab) / n
    return {
        "run": run,
        "qubit": 147,
        "shots": n,
        "p_prep0_next_given_remeasure_first_read_1": given1,
        "p_prep0_next_given_remeasure_first_read_0": given0,
        "readme_values": {"given_1": 0.0825, "given_0": 0.020},
        "count": count,
        "expected_under_exchangeable_shots": exp,
        "ratio_count_to_expected": count / exp,
        "z_poisson": z,
        "log10_p_two_sided": float(log10_two_sided(np.array([count]), np.array([exp]))[0]),
        "earlier_arm_count": back,
        "earlier_arm_expected": exp_back,
        "earlier_arm_log10_p": float(log10_two_sided(np.array([back]), np.array([exp_back]))[0]),
        "recovered": bool(abs(given1 - 0.0825) < 0.01 and abs(given0 - 0.020) < 0.005),
    }


def main() -> None:
    cat = common.catalog()
    datasets = [d for d in common.ground_datasets(cat) if d["kind"] == "pilot" or len(d["columns"]) >= 24]
    results = common.ordered_map(analyze, datasets, min_items=1)
    out: dict[str, Any] = {"analysis": "a4_lag1_memory", "datasets": {}}
    tests: list[tuple[str, str, float]] = []
    pilot = [r for r in results if r["kind"] == "pilot"]
    groups: list[tuple[str, list[dict[str, Any]]]] = [("pilot_fez", pilot)]
    groups += [(f"sp:{r['id'][-34:]}", [r]) for r in results if r["kind"] == "state_prep"]
    tasks = [task for _, rs in groups for task in diag_tasks(rs)]
    laws = common.ordered_map(diag_law, tasks, min_items=1)
    offset = 0
    out["datasets"]["state_prep_kingston"] = {}
    for label, rs in groups:
        q = len(rs[0]["qubits"])
        summ, t = evaluate(rs, label, laws[offset : offset + q])
        offset += q
        tests += t
        if label == "pilot_fez":
            out["datasets"]["pilot_fez"] = summ
        else:
            summ["arm"] = rs[0]["arm"]
            summ["slot_us"] = rs[0]["slot_us"]
            out["datasets"]["state_prep_kingston"][rs[0]["id"]] = summ
    out["positive_control_q147"] = q147_control()
    corr = common.global_corrections(tests, ALPHA)
    corr.pop("_bh_member_ids", None)
    out["n_tests"] = len(tests)
    out["corrections"] = corr
    common.write_json(common.OUT / "a4_lag1_memory.json", out)
    common.write_json_gz(common.OUT / "a4_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 3)] for t in tests]})
    print(out["n_tests"], corr)
    print(out["positive_control_q147"])
    for k, v in out["datasets"].items():
        if k == "pilot_fez":
            print(k, {a: b for a, b in v.items() if not isinstance(b, (list, dict))}, v["diag_decay_at_lags"])
            print("  ", v["cross_variance_over_mean"], v["diag_block_local"])
        else:
            for kk, vv in v.items():
                print(
                    kk[-34:],
                    {
                        a: (round(b, 4) if isinstance(b, float) else b)
                        for a, b in vv.items()
                        if not isinstance(b, (list, dict))
                    },
                    vv["diag_decay_at_lags"],
                )
                print("  ", vv["cross_variance_over_mean"], vv["diag_block_local"])


if __name__ == "__main__":
    main()
