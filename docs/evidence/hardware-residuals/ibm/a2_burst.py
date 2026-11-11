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
to 0.5 (both fixed from the marginals alone; a Poisson approximation); (4) adjacency of the highest-scoring 1
percent of shots (score z_n = (M_n - mu_b) / sigma_b, ties kept) in shot index, and (5) the same for pairs
separated by 1..16 shots, each against a deterministic circular-shift null: column i is rotated by
i * round(g N) shots (g in the golden-ratio powers 0.381966, 0.236068, 0.145898, 0.090170), which keeps every
column's marginal and its own time structure (per-qubit temporal dependence) and removes only the cross-column
alignment; the
null mean is the larger of the mean count over the four rotated copies and the exact permutation mean and the
p-value is the Poisson upper tail at that mean (an approximation: four shifted copies estimate a mean and no
distribution). The exact permutation expectation |B|(|B|-1)/N is reported beside it as a diagnostic: per-qubit
temporal dependence raises adjacency above the permutation mean without any burst, and only the shift null
separates the two.
The p-value of test (1) is the circular-shift law of the same statistic over the full group of shifts: column i
rotates by i s mod N shots for every s = 1 ... N-1 (the rotations T_s compose as T_s T_s' = T_(s+s'), so the
observation ranks among N equally likely points when shots are exchangeable inside independent columns, and the
rank p-value is exact there), the z statistic of the preregistered form is recomputed on every rotated copy with
block-local marginals of the rotated columns, and p = min(1, 2 min(P(z_s >= z), P(z_s <= z))) over the N-1 shifts
and the observation. Under drift of a column the rotation moves its time structure, so the shift law then serves as
a reference that keeps each column's own structure and no Poisson-binomial assumption. Its resolution
1 / N sets a floor of 2 / N on every p-value (`dispersion.shift.full_group`). As a sensitivity, the same test over
the shifts whose column offsets stay at least 16 shots apart (the per-qubit dependence of analysis 4 falls by
0.55 to 0.7 per lag, so a 16-shot separation leaves under 0.4 percent of the lag-1 excess) sits beside it
(`dispersion.shift.admissible_gap_16`; a PUB with fewer shots than 16 times its columns has none). The normal-law
p-value stays in the record as `lp_normal_approximation`.
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
SHIFT_GAP = 16
SHIFT_CHUNK = 128
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


def _block_stats(counts: np.ndarray, sizes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Block-local (mu, sigma^2, kappa4) of the error count from per-block column counts (..., q, blocks)."""
    p = counts / sizes
    mu = p.sum(axis=-2)
    pq = p * (1 - p)
    return mu, pq.sum(axis=-2), (pq * (1 - 6 * pq)).sum(axis=-2)


def _dispersion_z(sum_m2: np.ndarray, sizes: np.ndarray, counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(ratio, z) of the dispersion statistic from sum_n M_n^2 and the block counts of the (rotated) columns.

    Inside a block sum_n (M_n - mu_b)^2 = sum_n M_n^2 - n_b mu_b^2, because the block mean of M_n is mu_b.
    """
    mu, sig2, kap4 = _block_stats(counts, sizes)
    stat = sum_m2 - (sizes * mu**2).sum(axis=-1)
    ref = (sizes * sig2).sum(axis=-1)
    var = (sizes * (kap4 + 2 * sig2**2)).sum(axis=-1)
    return stat / ref, (stat - ref) / np.sqrt(var)


def _rotated_block_counts(
    cumulative: np.ndarray, shifts: np.ndarray, starts: np.ndarray, sizes: np.ndarray
) -> np.ndarray:
    """Per-block counts (shifts, q, blocks) of the columns rotated by i s mod n, from circular prefix sums."""
    q, n_plus = cumulative.shape
    n = n_plus - 1
    offsets = (np.arange(q)[None, :] * shifts[:, None]) % n  # (shifts, q)
    lo = (starts[None, None, :] - offsets[:, :, None]) % n
    hi = lo + sizes.astype(np.int64)[None, None, :]
    cols = np.arange(q)[None, :, None]
    wrapped = hi > n
    head = cumulative[cols, np.minimum(hi, n)] - cumulative[cols, lo]
    tail = cumulative[cols, np.where(wrapped, hi - n, 0)]
    return (head + np.where(wrapped, tail, 0.0)).astype(np.float64)


def shift_distribution(e: np.ndarray, blocks: list[np.ndarray]) -> dict[str, Any]:
    """Exact circular-shift law of the dispersion z (see the module docstring)."""
    n, q = e.shape
    starts = np.array([b[0] for b in blocks])
    sizes = np.array([b.size for b in blocks], dtype=np.float64)
    ef = e.astype(np.float64)
    cumulative = np.vstack([np.zeros((1, q)), np.cumsum(ef, axis=0)]).T.copy()  # (q, n + 1)
    # sum_n M_n^2 at every shift s: sum_i K_i + 2 sum_(i<j) corr_ij((i - j) s mod n), exact in integers
    spectrum = np.fft.rfft(ef, axis=0)
    shifts_all = np.arange(n)
    pair_sum = np.zeros(n)
    for i in range(q - 1):
        corr = np.fft.irfft(np.conj(spectrum[:, i])[None, :] * spectrum[:, i + 1 :].T, n=n, axis=1)
        corr = np.rint(corr)
        lag = ((i - np.arange(i + 1, q))[:, None] * shifts_all[None, :]) % n
        pair_sum += np.take_along_axis(corr, lag, axis=1).sum(axis=0)
    sum_m2 = ef.sum() + 2 * pair_sum
    ratio = np.empty(n)
    z = np.empty(n)
    admissible = np.zeros(n, dtype=bool)
    for lo in range(0, n, SHIFT_CHUNK):
        shifts = shifts_all[lo : lo + SHIFT_CHUNK]
        counts = _rotated_block_counts(cumulative, shifts, starts, sizes)
        ratio[lo : lo + SHIFT_CHUNK], z[lo : lo + SHIFT_CHUNK] = _dispersion_z(
            sum_m2[lo : lo + SHIFT_CHUNK], sizes, counts
        )
        offsets = np.sort((np.arange(q)[None, :] * shifts[:, None]) % n, axis=1)
        gaps = np.diff(np.concatenate([offsets, offsets[:, :1] + n], axis=1), axis=1)
        admissible[lo : lo + SHIFT_CHUNK] = gaps.min(axis=1) >= SHIFT_GAP
    admissible[0] = False
    # direct check of one nonzero shift by gathering the rotated columns
    check_shift = n // 3
    rolled = np.stack([np.roll(e[:, i], (i * check_shift) % n) for i in range(q)], axis=1)
    m_direct = rolled.sum(axis=1).astype(np.float64)
    counts_direct = np.stack([rolled[idx].sum(axis=0) for idx in blocks], axis=1).astype(np.float64)
    ratio_direct, z_direct = _dispersion_z(np.array(float((m_direct**2).sum())), sizes, counts_direct)
    return {
        "z0": float(z[0]),
        "ratio0": float(ratio[0]),
        "z_all": z[1:],
        "admissible": admissible[1:],
        "selfcheck": {
            "direct_shift": check_shift,
            "max_abs_diff_ratio": float(abs(ratio[check_shift] - ratio_direct)),
            "max_abs_diff_z": float(abs(z[check_shift] - z_direct)),
        },
    }


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
    law = shift_distribution(e, blocks)
    if abs(law["z0"] - z_disp) > 1e-9 or abs(law["ratio0"] - ratio) > 1e-12:
        raise ValueError("shift 0 of the fast path differs from the direct dispersion statistic")
    z_all = law.pop("z_all")
    admissible = law.pop("admissible")
    law.pop("z0")
    law.pop("ratio0")

    def shift_summary(z_shift: np.ndarray) -> dict[str, Any]:
        if not z_shift.size:
            return {"n_shifts": 0}
        total = z_shift.size + 1
        upper = (int((z_shift >= z_disp).sum()) + 1) / total
        lower = (int((z_shift <= z_disp).sum()) + 1) / total
        return {
            "n_shifts": int(z_shift.size),
            "lp": math.log10(min(1.0, 2 * min(upper, lower))),
            "p_floor_log10": math.log10(2 / total),
            "z_shift_mean": float(z_shift.mean()),
            "z_shift_sd": float(z_shift.std()),
            "z_observed_in_shift_sd": float((z_disp - z_shift.mean()) / z_shift.std()),
            "upper_tail_count": int((z_shift >= z_disp).sum()),
            "lower_tail_count": int((z_shift <= z_disp).sum()),
        }

    law["full_group"] = shift_summary(z_all)
    law["admissible_gap_16"] = shift_summary(z_all[admissible]) | {"min_offset_gap": SHIFT_GAP}
    lp_dispersion = law["full_group"]["lp"]

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
        "dispersion": {
            "ratio": ratio,
            "z": z_disp,
            "ratio_se": math.sqrt(var_stat) / ref,
            "lp": lp_dispersion,
            "law": "circular-shift distribution over all N-1 shifts (exact for exchangeable independent columns)",
            "lp_normal_approximation": lp_disp,
            "shift": law,
        },
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
