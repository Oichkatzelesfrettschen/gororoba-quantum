"""Lag-1 memory of errors: P(error of qubit i at shot n+1 | error of qubit j at shot n) against the marginal.

Generalizes the qubit-147 successor effect of docs/evidence/primorial_cover/q147-remeasure/README.md
(prep0 reads 1 at shot s+1 in 0.0825 of the shots after a remeasure first read of 1 at shot s, against 0.020
after a 0). Data: the 153 sensors of the 24 readout-actor pilot PUBs, pooled per ordered qubit pair across the
PUBs (list positions of one PUB lie one job slot, 8 circuits, apart); and the 12 wide single-PUB state-prep
runs on ibm_kingston, one PUB per job, where the next list position is the next physical shot.

Falsifier, fixed before the run. For the error indicator matrix E, the count C_ji = sum_n e_j[n] e_i[n+1]
has, under shots that are exchangeable (a uniformly random reordering of whole shot rows), the exact mean
(K_j K_i - J_ji) / N, where J_ji is the same-shot joint count. The count is close to Poisson for sparse errors,
so each ordered pair (153 x 153 = 23,409 for the pilot; Q^2 per state-prep PUB, diagonal included as the
per-qubit memory) gets one exact two-sided Poisson test. Slow drift also raises lag-1 counts, so every
survivor is re-evaluated at lags 2 and 3 with the same null: pure memory of one shot decays at once, drift
does not. "No memory" means no pair below the Bonferroni line over all these tests and a flat distribution
of the diagonal z scores.

Positive control from the repository record: the q147 successor (remeasure first read at shot s against the
prep0 read at shot s+1, three static PUBs in one job, one list step = one physical step) must reproduce
0.0825 against 0.020 with the same detector (the detector's count and mean, applied to two PUBs).
"""

from __future__ import annotations

import math
from typing import Any, cast

import common
import numpy as np
from scipy.stats import poisson

ALPHA = 0.05
LAGS = (1, 2, 3)


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


def evaluate(results: list[dict[str, Any]], label: str) -> tuple[dict[str, Any], list[tuple[str, str, float]]]:
    qubits = results[0]["qubits"]
    q = len(qubits)
    dist = common.graph_distances(common.coupling_graph(results[0]["backend"]))
    obs1, exp1 = pooled(results, 1)
    lp = log10_two_sided(obs1, exp1)
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
    z_diag = (d_obs - d_exp) / np.sqrt(np.maximum(d_exp, 1e-9))
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
    # chain prediction for the cross counts: same-shot correlation of j with i, then i's own lag-1 memory
    joint_tot = sum(r["joint"] for r in results).astype(np.float64)
    prev_all = sum(r["marginal_prev"][1] for r in results).astype(np.float64)
    n_pairs = sum(r["n"] - 1 for r in results)
    a_mem = obs1[diag, diag] / np.maximum(prev, 1)
    b_mem = (prev - obs1[diag, diag]) / np.maximum(n_pairs - prev, 1)  # P(next = 1 | prev = 0) from the marginal count
    b_mem = np.maximum((k_tot - obs1[diag, diag] - 0) / np.maximum(n_tot - prev, 1), 0)
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
                "chain_prediction_same_shot_times_memory": float(chain[j, i]),
                "observed_over_chain": float(obs1[j, i] / max(chain[j, i], 1e-12)),
                "log10_p": float(lp[j, i]),
                "lag2_obs_exp": [int(obs2[j, i]), float(exp2[j, i])],
                "lag3_obs_exp": [int(obs3[j, i]), float(exp3[j, i])],
            }
        )
    near = (dist[np.ix_(qubits, qubits)] == 1) & off
    summary = {
        "n_pubs": len(results),
        "n_shots_total": int(n_tot),
        "n_qubits": q,
        "n_tests": q * q,
        "bonferroni_log10_threshold_own_family": thr,
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
    # one-shot-earlier arm: prep0 at s against the remeasure read at s+1 (a successor cannot act backward)
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
    summ, t = evaluate(pilot, "pilot_fez")
    out["datasets"]["pilot_fez"] = summ
    tests += t
    out["datasets"]["state_prep_kingston"] = {}
    for r in [r for r in results if r["kind"] == "state_prep"]:
        summ, t = evaluate([r], f"sp:{r['id'][-34:]}")
        summ["arm"] = r["arm"]
        summ["slot_us"] = r["slot_us"]
        out["datasets"]["state_prep_kingston"][r["id"]] = summ
        tests += t
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


if __name__ == "__main__":
    main()
