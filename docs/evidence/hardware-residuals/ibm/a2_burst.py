"""Burst multiplicity and temporal clustering of errors in the wide ground-prepared registers.

Data: the 153 sensor qubits of each of the 24 readout-actor pilot PUBs (error = outcome xor prepared bit) and
the ground-prepared first read of the 66-149 qubits of each of the 13 wide state-prep-control PUBs. The six
narrow PUBs of the three-PUB state-prep run are below the 24-column floor. The 156-bit and 58-bit PUBs of
`results/live/kingston-wide-control-result` hold 512 shots and no record of their prepared state: not run.

Falsifier, fixed before the run. Per PUB, let M_n be the number of errors in shot n over Q columns. Blocks of
512 shots carry their own marginals p_i (block-local plug-in), so slow drift sets the null and not the
alternative. Under independent errors, M_n is Poisson-binomial with those marginals. Five tests per PUB:
(1) dispersion z of sum_n (M_n - mu_b)^2 against sum_n sigma_b^2, with variance sum_n (kappa4_b + 2 sigma_b^4)
(positive correlation raises it); (2) and (3) the count of shots with M >= t against Poisson with the
Poisson-binomial tail mass, at the two thresholds t_a and t_b where the expected count first falls to 5 and
to 0.5 (both fixed from the marginals alone); (4) adjacency of the highest-scoring 1 percent of shots (score
z_n = (M_n - mu_b) / sigma_b, ties kept) in shot index, and (5) the same for pairs separated by 1..16 shots,
each against a deterministic circular-shift null: column i is rotated by i * round(g N) shots (g in the
golden-ratio powers 0.381966, 0.236068, 0.145898, 0.090170), which keeps every column's marginal and its own
time structure (per-qubit memory) and removes only the cross-column alignment; the null mean is the larger of the
mean count over the four rotated copies and the exact permutation mean and the p-value is the Poisson upper tail at
that mean. The exact permutation expectation |B|(|B|-1)/N is reported beside it as a diagnostic: per-qubit memory
raises adjacency above the permutation mean without any burst, and only the shift null separates the two.
"No structure" means every one of the 5 x (number of PUBs) p-values stays above 0.05 / that count (Bonferroni) and
above the Benjamini-Hochberg line. Plug-in marginals absorb part of any burst, so the tests lean conservative.
"""

from __future__ import annotations

import math
from typing import Any

import common
import numpy as np
from scipy.stats import norm

BLOCK = 512
ALPHA = 0.05
WINDOW = 16
GOLDEN = (0.381966, 0.236068, 0.145898, 0.090170)


def pair_counts(burst: np.ndarray) -> tuple[int, int]:
    bi = burst.astype(np.int64)
    adj = int((bi[:-1] * bi[1:]).sum())
    win = int(sum((bi[:-d] * bi[d:]).sum() for d in range(1, WINDOW + 1)))
    return adj, win


def burst_mask(e: np.ndarray, blocks: list[np.ndarray], target: int) -> tuple[np.ndarray, float]:
    n = e.shape[0]
    m = e.sum(axis=1).astype(np.float64)
    mu = np.empty(n)
    sig2 = np.empty(n)
    for idx in blocks:
        p = e[idx].mean(axis=0)
        mu[idx] = p.sum()
        sig2[idx] = (p * (1 - p)).sum()
    score = (m - mu) / np.sqrt(np.maximum(sig2, 1e-12))
    cut = np.sort(score)[::-1][target - 1]
    return score >= cut, float(cut)


def pb_pmf(p: np.ndarray) -> np.ndarray:
    """Poisson-binomial pmf by sequential convolution."""
    pmf = np.zeros(p.size + 1)
    pmf[0] = 1.0
    for i, pi in enumerate(p):
        pmf[1 : i + 2] = pmf[1 : i + 2] * (1 - pi) + pmf[: i + 1] * pi
        pmf[0] *= 1 - pi
    return pmf


def analyze(ds: dict[str, Any]) -> dict[str, Any]:
    e, qubits = common.load_errors(ds)
    n, q = e.shape
    if q < 24:
        return {"id": ds["id"], "skipped": "fewer than 24 columns"}
    m = e.sum(axis=1).astype(np.float64)
    nblk = max(1, n // BLOCK)
    blocks = np.array_split(np.arange(n), nblk)
    mu = np.empty(n)
    sig2 = np.empty(n)
    kap4 = np.empty(n)
    pmfs = []
    for idx in blocks:
        p = e[idx].mean(axis=0)
        mu[idx] = p.sum()
        sig2[idx] = (p * (1 - p)).sum()
        kap4[idx] = (p * (1 - p) * (1 - 6 * p * (1 - p))).sum()
        pmfs.append(pb_pmf(p))
    stat = float(((m - mu) ** 2).sum())
    ref = float(sig2.sum())
    var_stat = float((kap4 + 2 * sig2**2).sum())
    z_disp = (stat - ref) / math.sqrt(var_stat)
    lp_disp = float(math.log10(max(2 * norm.sf(abs(z_disp)), 1e-300)))
    ratio = stat / ref

    # expected count of shots with M >= t from the block-local Poisson-binomial tails
    tails = np.zeros(q + 2)
    for idx, pmf in zip(blocks, pmfs, strict=True):
        tail = np.concatenate([np.cumsum(pmf[::-1])[::-1], [0.0]])
        tails[: tail.size] += len(idx) * tail
    expected_at = lambda t: float(tails[t])  # noqa: E731
    t_a = next((t for t in range(q + 1) if expected_at(t) <= 5.0), q)
    t_b = next((t for t in range(q + 1) if expected_at(t) <= 0.5), q)
    out_tail = {}
    for label, t in (("t_a", t_a), ("t_b", t_b)):
        obs = int((m >= t).sum())
        mean = expected_at(t)
        lo, hi = common.garwood(obs)
        out_tail[label] = {
            "threshold": t,
            "observed": obs,
            "expected": mean,
            "ratio": obs / mean if mean > 0 else None,
            "ratio_ci95": [lo / mean, hi / mean] if mean > 0 else None,
            "lp": common.log10_poisson_upper(obs, mean),
        }

    # temporal clustering of the highest-scoring shots
    target = max(10, int(math.ceil(0.01 * n)))
    burst, cut = burst_mask(e, blocks, target)
    b = int(burst.sum())
    adj, win = pair_counts(burst)
    exp_adj_perm = b * (b - 1) / n
    exp_win_perm = sum((n - d) for d in range(1, WINDOW + 1)) * b * (b - 1) / (n * (n - 1))
    shifted = []
    for g in GOLDEN:
        step = int(round(g * n))
        rolled = np.stack([np.roll(e[:, i], (i * step) % n) for i in range(q)], axis=1)
        mask, _ = burst_mask(rolled, blocks, target)
        shifted.append((int(mask.sum()),) + pair_counts(mask))
    # the exact permutation mean floors the shift mean, which is a 4-copy estimate and can read 0
    exp_adj = max(float(np.mean([s_[1] for s_ in shifted])), exp_adj_perm)
    exp_win = max(float(np.mean([s_[2] for s_ in shifted])), exp_win_perm)
    lo_a, hi_a = common.garwood(adj)
    lo_w, hi_w = common.garwood(win)
    # observed multiplicity histogram against the expected one, for the report
    hist_obs = np.bincount(m.astype(int), minlength=q + 1)[:12]
    hist_exp = np.zeros(q + 1)
    for idx, pmf in zip(blocks, pmfs, strict=True):
        hist_exp += len(idx) * pmf
    return {
        "id": ds["id"],
        "kind": ds["kind"],
        "arm": ds["arm"],
        "run": ds["run"],
        "backend": ds["backend"],
        "n_shots": n,
        "n_columns": q,
        "slot_us": ds["slot_s"] * 1e6,
        "mean_errors_per_shot": float(m.mean()),
        "dispersion": {"ratio": ratio, "z": z_disp, "ratio_se": math.sqrt(var_stat) / ref, "lp": lp_disp},
        "tail": out_tail,
        "burst_set": {"size": b, "score_cut": float(cut)},
        "adjacent_pairs": {
            "observed": adj,
            "expected_shift_null": exp_adj,
            "expected_permutation": exp_adj_perm,
            "ratio_to_shift_null": adj / exp_adj if exp_adj else None,
            "ratio_to_permutation": adj / exp_adj_perm if exp_adj_perm else None,
            "ratio_ci95_shift": [lo_a / exp_adj, hi_a / exp_adj] if exp_adj else None,
            "lp": common.log10_poisson_upper(adj, exp_adj),
            "lp_permutation": common.log10_poisson_upper(adj, exp_adj_perm),
        },
        "window_pairs": {
            "window": WINDOW,
            "observed": win,
            "expected_shift_null": exp_win,
            "expected_permutation": exp_win_perm,
            "ratio_to_shift_null": win / exp_win if exp_win else None,
            "ratio_to_permutation": win / exp_win_perm if exp_win_perm else None,
            "ratio_ci95_shift": [lo_w / exp_win, hi_w / exp_win] if exp_win else None,
            "lp": common.log10_poisson_upper(win, exp_win),
            "lp_permutation": common.log10_poisson_upper(win, exp_win_perm),
        },
        "shifted_copies_burst_size_adj_win": shifted,
        "multiplicity_observed_0_to_11": hist_obs.tolist(),
        "multiplicity_expected_0_to_11": [float(x) for x in hist_exp[:12]],
        "max_multiplicity": int(m.max()),
    }


def main() -> None:
    cat = common.catalog()
    datasets = [d for d in common.ground_datasets(cat) if d["kind"] == "pilot" or len(d["columns"]) >= 24]
    results = common.ordered_map(analyze, datasets, min_items=1)
    tests: list[tuple[str, str, float]] = []
    for r in results:
        tests += [
            (f"{r['id']}|dispersion", "dispersion", r["dispersion"]["lp"]),
            (f"{r['id']}|tail_a", "tail", r["tail"]["t_a"]["lp"]),
            (f"{r['id']}|tail_b", "tail", r["tail"]["t_b"]["lp"]),
            (f"{r['id']}|adjacent", "cluster", r["adjacent_pairs"]["lp"]),
            (f"{r['id']}|window", "cluster", r["window_pairs"]["lp"]),
        ]
    corr = common.global_corrections(tests, ALPHA)
    members = set(corr.pop("_bh_member_ids", []))
    for r in results:
        r["bh_members"] = [
            t for t in ("dispersion", "tail_a", "tail_b", "adjacent", "window") if f"{r['id']}|{t}" in members
        ]
    thr = corr["bonferroni_log10_threshold"]
    flagged = sorted(
        [(lp, tid) for tid, _, lp in tests if lp <= thr],
    )
    by_kind: dict[str, Any] = {}
    for kind in ("pilot", "state_prep"):
        rs = [r for r in results if r["kind"] == kind]
        by_kind[kind] = {
            "n_pubs": len(rs),
            "median_dispersion_ratio": float(np.median([r["dispersion"]["ratio"] for r in rs])),
            "dispersion_ratio_range": [
                min(r["dispersion"]["ratio"] for r in rs),
                max(r["dispersion"]["ratio"] for r in rs),
            ],
            "n_dispersion_p_below_0.05": sum(r["dispersion"]["lp"] < math.log10(0.05) for r in rs),
            "n_tail_b_p_below_0.05": sum(r["tail"]["t_b"]["lp"] < math.log10(0.05) for r in rs),
            "n_adjacent_p_below_0.05": sum(r["adjacent_pairs"]["lp"] < math.log10(0.05) for r in rs),
            "n_window_p_below_0.05": sum(r["window_pairs"]["lp"] < math.log10(0.05) for r in rs),
            "pooled_tail_a_ratio": sum(r["tail"]["t_a"]["observed"] for r in rs)
            / sum(r["tail"]["t_a"]["expected"] for r in rs),
            "pooled_adjacent_ratio_to_shift_null": sum(r["adjacent_pairs"]["observed"] for r in rs)
            / sum(r["adjacent_pairs"]["expected_shift_null"] for r in rs),
            "pooled_adjacent_ratio_to_permutation": sum(r["adjacent_pairs"]["observed"] for r in rs)
            / sum(r["adjacent_pairs"]["expected_permutation"] for r in rs),
            "pooled_window_ratio_to_shift_null": sum(r["window_pairs"]["observed"] for r in rs)
            / sum(r["window_pairs"]["expected_shift_null"] for r in rs),
            "pooled_window_ratio_to_permutation": sum(r["window_pairs"]["observed"] for r in rs)
            / sum(r["window_pairs"]["expected_permutation"] for r in rs),
        }
    out = {
        "analysis": "a2_burst",
        "n_pubs_analyzed": len(results),
        "n_tests": len(tests),
        "corrections": corr,
        "bonferroni_flagged": [{"id": tid, "log10_p": lp} for lp, tid in flagged],
        "by_kind": by_kind,
        "pubs": results,
        "not_run": {"kingston-wide-control-result": "512 shots; no record of the prepared state, so no ideal outcome"},
    }
    common.write_json(common.OUT / "a2_burst.json", out)
    common.write_json_gz(common.OUT / "a2_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 4)] for t in tests]})
    print(out["n_pubs_analyzed"], out["n_tests"], corr)
    print(by_kind)
    print(flagged[:15])


if __name__ == "__main__":
    main()
