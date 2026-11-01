"""Selection among compiled meshes: per-input block contrasts, their hierarchical shrinkage and replay power.

A block is the set of iterations that ran one compilation seed per input; two blocks A and B give each input one
correctness contrast. The functions here take explicit inputs (iteration rows, the input labels, the rejection
reasons, the prior grid, the simulation sizes), so a later acquisition with the same row format reuses them by
selecting its own runs and blocks.

- block_counts sums a block's correct, accepted, sample and shot counts per input.
- contrast_shrinkage is the normal-normal hierarchical estimate of each input's A minus B difference (Efron 2011,
  "Tweedie's formula and selection bias", Eqs. 3.7, 3.8 and the regret term of 7.26) with directional
  Benjamini-Hochberg sign decisions (Weinstein and Yekutieli, arXiv 1404.7403, Definition 2).
- replay_power is the posterior-predictive power of a winner-and-loser replay of the two blocks.
- exact_permutation_r is Pearson r with its exact one-sided permutation p-value.
"""

from __future__ import annotations

import itertools
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


def normal_cdf(x: Any) -> Any:
    from scipy.special import ndtr

    return ndtr(x)


def block_counts(
    rows: Sequence[Mapping[str, Any]], labels: Sequence[str], rejections: Sequence[str]
) -> dict[str, dict[str, dict[str, float]]]:
    """Per input and block: correct, accepted, samples, shots and each rejection reason, summed over the block's runs.

    Each row carries label, block_of_seed, compilation_seed, correct, accepted, samples, nb_shots_used and a
    rejected mapping. A block pools runs of one seed per input (a run and its exact replay); a block that mixes
    seeds for one input raises."""
    out: dict[str, dict[str, dict[str, float]]] = {label: {} for label in labels}
    for row in rows:
        cell = out[row["label"]].setdefault(
            row["block_of_seed"],
            {"correct": 0, "accepted": 0, "samples": 0, "shots": 0, "seed": row["compilation_seed"]},
        )
        if cell["seed"] != row["compilation_seed"]:
            raise ValueError(f"{row['label']} block {row['block_of_seed']} mixes compilation seeds")
        for key in ("correct", "accepted", "samples"):
            cell[key] += row[key]
        cell["shots"] += row["nb_shots_used"]
        for reason in rejections:
            cell[f"rejected_{reason}"] = cell.get(f"rejected_{reason}", 0) + row["rejected"][reason]
    return out


def exact_permutation_r(x: np.ndarray, y: np.ndarray, negative: bool) -> tuple[float, float]:
    """Pearson r of paired values and its exact one-sided permutation p-value over all pairings: P(r_perm <= r) for a
    predicted negative association, P(r_perm >= r) for a positive one."""

    def pearson(a: np.ndarray, b: np.ndarray) -> float:
        a, b = a - a.mean(), b - b.mean()
        return float(a @ b / np.sqrt((a @ a) * (b @ b)))

    observed = pearson(x, y)
    values = [pearson(x, np.asarray(perm)) for perm in itertools.permutations(y)]
    if negative:
        return observed, float(np.mean([v <= observed + 1e-12 for v in values]))
    return observed, float(np.mean([v >= observed - 1e-12 for v in values]))


def contrast_shrinkage(
    counts: Mapping[str, Mapping[str, Mapping[str, float]]],
    labels: Sequence[str],
    tau_grid: np.ndarray,
    fdr_q: float,
) -> dict[str, Any]:
    """Normal-normal hierarchical shrinkage of each input's block A minus block B correctness difference.

    The A and B seeds of an input are exchangeable draws of the transpiler, so the prior on the true difference is
    centered at zero: mu_i ~ N(0, tau^2), d_i | mu_i ~ N(mu_i, s_i^2) with s_i the binomial standard error. Tweedie's
    formula for this prior gives E[mu_i | d_i, tau] = C_i d_i with C_i = tau^2 / (tau^2 + s_i^2) (Efron 2011, Eqs. 3.7
    and 3.8). tau carries a uniform prior on tau_grid, so its estimation error enters every posterior moment, the
    hierarchical counterpart of Efron's Eq. 7.26 regret term. The expected winner-minus-loser gap of input i is
    E[sign(d_i) mu_i | data] = |d_i| E[C_i | data]. The record's z and difference are A minus B. The returned
    "_draw" entry carries d, s and the tau weights for replay_power and leaves the record before it is written."""
    n = len(labels)
    d = np.empty(n)
    s = np.empty(n)
    for i, label in enumerate(labels):
        a, b = counts[label]["A"], counts[label]["B"]
        pa, pb = a["correct"] / a["accepted"], b["correct"] / b["accepted"]
        d[i] = pa - pb
        s[i] = np.sqrt(pa * (1 - pa) / a["accepted"] + pb * (1 - pb) / b["accepted"])
    z = d / s
    chi_square = float(np.sum(z**2))
    variance = tau_grid[:, None] ** 2 + s[None, :] ** 2
    log_post = np.sum(-0.5 * np.log(variance) - d[None, :] ** 2 / (2 * variance), axis=1)
    weights = np.exp(log_post - log_post.max())
    weights /= weights.sum()
    factor = tau_grid[:, None] ** 2 / variance
    mean_factor = weights @ factor
    gap = np.abs(d) * mean_factor
    gap_second = weights @ (factor * s**2 + factor**2 * d**2)
    sign_right = weights @ normal_cdf(np.sqrt(factor) * np.abs(d) / s)
    cdf = np.cumsum(weights)
    p_values = 2 * (1 - normal_cdf(np.abs(z)))
    order = np.argsort(p_values)
    passed = [p_values[k] <= fdr_q * (rank + 1) / n for rank, k in enumerate(order)]
    determined = max((rank + 1 for rank, ok in enumerate(passed) if ok), default=0)
    return {
        "prior": f"mu_i ~ N(0, tau^2), tau uniform on [{tau_grid[0]:g}, {tau_grid[-1]:g}]",
        "inputs": {
            label: {
                "block_a": dict(counts[label]["A"]),
                "block_b": dict(counts[label]["B"]),
                "difference": float(d[i]),
                "standard_error": float(s[i]),
                "z": float(z[i]),
                "two_sided_p": float(p_values[i]),
                "winner_block": "A" if d[i] > 0 else "B",
                "shrinkage_factor": float(mean_factor[i]),
                "expected_gap": float(gap[i]),
                "gap_posterior_sd": float(np.sqrt(gap_second[i] - gap[i] ** 2)),
                "probability_winner_is_better": float(sign_right[i]),
                "sign_determined_directional_bh": bool(i in {int(k) for k in order[:determined]}),
            }
            for i, label in enumerate(labels)
        },
        f"chi_square_on_{n}": chi_square,
        # The James-Stein factor is 0 (full shrinkage) when every difference is zero.
        "james_stein_factor": float(max(0.0, 1 - (n - 2) / chi_square)) if chi_square > 0 else 0.0,
        "tau_mle": float(tau_grid[np.argmax(log_post)]),
        "tau_posterior_mean": float(weights @ tau_grid),
        "tau_90_interval": [float(tau_grid[np.searchsorted(cdf, 0.05)]), float(tau_grid[np.searchsorted(cdf, 0.95)])],
        "mean_expected_gap": float(gap.mean()),
        "directional_bh_q": fdr_q,
        "signs_determined": determined,
        "_draw": {"d": d, "s": s, "weights": weights},
    }


def replay_power(
    counts: Mapping[str, Any],
    shrink: Mapping[str, Any],
    seed: np.random.SeedSequence,
    *,
    labels: Sequence[str],
    tau_grid: np.ndarray,
    trials: int,
    samples_per_iteration: int,
    job_counts: Sequence[int],
    dropouts: Sequence[int],
    z_critical: float,
) -> dict[str, Any]:
    """Posterior-predictive power of the winner-and-loser replay.

    Each trial draws tau from its posterior, each input's true A-minus-B difference from its conditional posterior
    N(C d, C s^2), and sets the winner and loser correctness at the input's observed two-block mean plus and minus
    half the signed gap. Each mesh runs samples_per_iteration samples per job pair at its observed acceptance per
    sample, so accepted counts and correct counts are binomial. The primary statistic is the summed contrast over the
    kept inputs divided by its binomial standard error, one-sided against z_critical. A dropout removes inputs whose
    seed returns a different mesh after a recalibration. Trials draw every input first and evaluate as numpy arrays,
    so the record depends only on the seed."""
    from scipy.stats import binom

    n = len(labels)
    rng = np.random.default_rng(seed)
    draw = shrink["_draw"]
    d, s, weights = draw["d"], draw["s"], draw["weights"]
    sign = np.sign(d)
    mean_level = np.empty(n)
    accept = np.empty((2, n))
    for i, label in enumerate(labels):
        a, b = counts[label]["A"], counts[label]["B"]
        mean_level[i] = 0.5 * (a["correct"] / a["accepted"] + b["correct"] / b["accepted"])
        winner, loser = (a, b) if d[i] > 0 else (b, a)
        accept[0, i] = winner["accepted"] / winner["samples"]
        accept[1, i] = loser["accepted"] / loser["samples"]
    tau = tau_grid[rng.choice(len(tau_grid), size=trials, p=weights)]
    factor = tau[:, None] ** 2 / (tau[:, None] ** 2 + s[None, :] ** 2)
    true_difference = factor * d + np.sqrt(factor) * s * rng.standard_normal((trials, n))
    gap = sign * true_difference
    tau_mle = tau_grid[int(np.argmax(weights))]
    factor_mle = tau_mle**2 / (tau_mle**2 + s**2)
    gap_mle = sign * (factor_mle * d + np.sqrt(factor_mle) * s * rng.standard_normal((trials, n)))
    order = rng.random((trials, n)).argsort(axis=1)
    uniforms = [rng.random((trials, n)) for _ in range(4 * len(job_counts))]
    out: dict[str, Any] = {
        "seed_spawn_key": list(seed.spawn_key),
        "trials": trials,
        "samples_per_iteration": samples_per_iteration,
        "designs": [],
    }
    for j, jobs in enumerate(job_counts):
        samples = samples_per_iteration * jobs // 2
        u = uniforms[4 * j : 4 * j + 4]
        scenarios = (
            ("persistent mesh error", gap),
            ("persistent mesh error, tau fixed at its maximum", gap_mle),
            ("no persistent mesh error", 0.0 * gap),
        )
        for scenario, effect in scenarios:
            p_win = np.clip(mean_level + effect / 2, 0.0, 1.0)
            p_lose = np.clip(mean_level - effect / 2, 0.0, 1.0)
            n_win = np.maximum(binom.ppf(u[0], samples, accept[0]), 1)
            n_lose = np.maximum(binom.ppf(u[1], samples, accept[1]), 1)
            c_win = binom.ppf(u[2], n_win, p_win)
            c_lose = binom.ppf(u[3], n_lose, p_lose)
            f_win, f_lose = c_win / n_win, c_lose / n_lose
            contrast = f_win - f_lose
            variance = f_win * (1 - f_win) / n_win + f_lose * (1 - f_lose) / n_lose
            for dropped in dropouts:
                keep = order >= dropped
                total = np.where(keep, contrast, 0.0).sum(axis=1)
                spread = np.sqrt(np.where(keep, variance, 0.0).sum(axis=1))
                statistic = np.divide(total, spread, out=np.zeros_like(total), where=spread > 0)
                kept = n - dropped
                out["designs"].append(
                    {
                        "jobs": jobs,
                        "scenario": scenario,
                        "pairs_dropped": dropped,
                        "power": float(np.mean(statistic > z_critical)),
                        "mean_true_gap_kept": float(np.mean(np.where(keep, effect, 0.0).sum(axis=1) / kept)),
                    }
                )
    return out
