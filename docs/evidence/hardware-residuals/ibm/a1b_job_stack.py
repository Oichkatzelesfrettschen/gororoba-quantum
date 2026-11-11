"""Job-level stacked periodogram: a line shared by the columns of one job, in physical frequency.

Follow-up to a1_line_scan.py, whose per-column narrow-line hits cluster at one physical frequency near 60 Hz
across jobs with different slot periods. All PUBs of a job share the shot count N and the column-wise slot
period, so one list-position bin k is one physical frequency f = k / (N slot) for every column of the job.

Falsifier. The statistic was fixed before the first run; the Gamma and F reference laws stay as descriptive
p-values, and the bin-enumeration, cross-unit and job-level calibrations below were added after the review of
2026-11-10. For each job, S_k = sum over its tested binary columns (at least 30 minority
shots) of the normalized ordinate c_k is Gamma(C, 1) under independent shots, and the ratio of S_k to the mean
of its 64 neighbors (guard 1 bin) is F(2C, 128C). "No structure" means every job's stacked narrow-line p-value
stays above 0.05 / (74 jobs x 2 families = 148 tests) after the union bound over bins, and the targeted
60 Hz bins (within 0.15 Hz of 60 Hz) of every job stay above 0.05 / 74. The centre of the 60 Hz window comes
from the mains frequency; its 0.15 Hz half-width and the decision to test it came after the column scan
(a1_line_scan.json), and the jobs that suggested the window sit inside its counts, so the family is labeled
exploratory and counted in the multiplicity.

Calibration of the stacked p-values. Columns of one PUB share circuit structure and a noise source, so C counts
correlated channels. Positive correlation between columns raises the variance of the stacked sum S_k above that of
Gamma(C, 1) and fattens its upper tail, so the Gamma and F p-values of the stack are anti-conservative; nothing
bounds how much, and the stacked p-values (down to 10^-128) are descriptive. Three calibrations that need no
independence between columns sit beside them in `calibrated`:
- Bin-enumeration null of a window. For the 60 Hz window (centre from the US mains frequency; half-width and
  test chosen after the column scan) and the 29.70 Hz window (centre found in these records by
  a1_line_scan.py), the statistic is the maximum of
  the neighbor-normalized ordinate over the window's bins. The null is the same statistic on every other
  non-overlapping tile of the same width over the bins that have a full neighbor window, taken from the same
  spectrum; p = (tiles with a statistic at least the window's) / (tiles). The tiles are exchangeable with the
  window only if the neighbor normalization removes the spectral color; spectral color that it leaves uneven
  inflates the null tiles near the drift band and no proof covers the rest, so the calibration is an inference
  that the windows lie in a flat region of the spectrum. Applied to the stack it shifts all
  columns of the job together, so column correlation and drift carry into the null; applied to one column or one
  PUB stack it keeps that unit's own coloring. The enumeration is exact, draws no random number, and has the
  resolution 1 / (tiles).
- Combination across units. Over the 74 jobs the number with a window rank p at or below 0.01 (and 0.05) is
  tested against the Poisson-binomial law of independent units at the attainable thresholds; the same count over
  the PUBs of each job (one unit per PUB) and over its columns is listed. Jobs that share one design (slot,
  shots, PUB count) share a list-position period, so the independent unit is the design: the passing jobs are
  grouped by design.
- Job-level Bonferroni minimum. The smallest column-level p-value of a job from a1_line_scan.py multiplied by
  the job's number of columns is valid under any dependence between the columns, and is the evidence the
  per-column hits already carry.
"""

from __future__ import annotations

import math
from typing import Any

import common
import exact_laws
import numpy as np
from scipy.stats import f as fdist
from scipy.stats import gamma

KMIN = 30
LOW = 8
HALF = 32
GUARD = 1
ALPHA = 0.05
MAINS = 60.0
WINDOW = 0.15
# windows: (name, centre in Hz, basis); the 29.70 Hz centre comes from a1_line_scan.py
TARGETS = (
    ("mains_60hz", MAINS, "centre from the mains frequency; half-width and test chosen after the column scan"),
    ("line_29_7hz", 29.70, "centre and half-width found in the column scan; test chosen after it"),
)
RANK_LEVELS = (0.01, 0.05)
A1_LINE_LOG10 = -6.843708558971848  # Bonferroni line of a1_line_scan.py over its 348,882 tests


def local_ratio_matrix(c: np.ndarray) -> np.ndarray:
    """Neighbor-normalized ordinates for bins h+1 ... m-h (rows), per column; c holds bins 1 ... m."""
    h = HALF + GUARD
    m = c.shape[0]
    csum = np.concatenate([np.zeros((1,) + c.shape[1:]), np.cumsum(c, axis=0)], axis=0)
    idx = np.arange(h, m - h)
    nb = (csum[idx - GUARD] - csum[idx - h] + csum[idx + h + 1] - csum[idx + GUARD + 1]) / (2 * HALF)
    return c[idx] / np.maximum(nb, 1e-300)


def window_bins(centre: float, slot: float, n: int, m: int) -> tuple[int, int]:
    lo = max(int(math.floor((centre - WINDOW) * slot * n)), 1)
    hi = min(int(math.ceil((centre + WINDOW) * slot * n)), m)
    return lo, hi


def window_rank(ratio: np.ndarray, m: int, lo: int, hi: int) -> tuple[np.ndarray, np.ndarray, int] | None:
    """Window statistic and its bin-enumeration rank p per column (or for one series), and the tile count.

    ratio holds the neighbor-normalized ordinates of bins h+1 ... m-h. Tiles have the window's width, start at
    the window's phase and cover the bins with a full neighbor window; the window is one tile.
    """
    h = HALF + GUARD
    width = hi - lo + 1
    if lo < h + 1 or hi > m - h or width < 1:
        return None
    first = lo - width * ((lo - (h + 1)) // width)
    starts = np.arange(first, m - h - width + 2, width)
    rows = starts - (h + 1)
    block = ratio[rows[0] : rows[-1] + width]
    stats = np.maximum.reduceat(block, rows - rows[0], axis=0)
    obs = stats[(lo - first) // width]
    rank = (stats >= obs).sum(axis=0) / starts.size
    return obs, rank, int(starts.size)


def asymptotic_window_log10_p(stat: np.ndarray, width: int) -> np.ndarray:
    """Union bound over the window's bins of the locally flat law (1 + r / 64)^-64 of a1_line_scan.py."""
    return np.minimum(0.0, math.log10(width) - 2 * HALF * np.log10(1 + stat / (2 * HALF)))


def stack_job(task: dict[str, Any]) -> dict[str, Any]:
    job = task["job"]
    n = task["n"]
    m = (n - 1) // 2
    total = np.zeros(m)
    count = 0
    per_pub: dict[str, Any] = {}
    slot = job["slot_s"]
    columns: dict[str, Any] = {}
    for name, centre, _ in TARGETS:
        lo, hi = window_bins(centre, slot, n, m)
        columns[name] = {"lo": lo, "hi": hi, "n": 0, "rank_le": [0] * len(RANK_LEVELS), "hits": []}
    for pub in job["pubs"]:
        loaded = common.load_pub(pub["file"])
        cols = []
        for _, matrix in sorted(loaded["regs"].items()):
            for b in range(matrix.shape[1]):
                col = matrix[:, b]
                k = int(col.sum())
                if min(k, n - k) >= KMIN:
                    cols.append(col.astype(np.float64))
        if not cols:
            continue
        data = np.stack(cols, axis=1)
        p = data.mean(axis=0)
        spec = np.fft.rfft(data - p, axis=0)[1 : m + 1]
        c = (spec.real**2 + spec.imag**2) / (n * p * (1 - p))
        s = c.sum(axis=1)
        total += s
        count += c.shape[1]
        ratio = local_ratio_matrix(c)
        for name, _, _ in TARGETS:
            slot_info = columns[name]
            ranked = window_rank(ratio, m, slot_info["lo"], slot_info["hi"])
            if ranked is None:
                continue
            stat, rank, tiles = ranked
            slot_info["tiles"] = tiles
            slot_info["n"] += int(rank.size)
            for j, level in enumerate(RANK_LEVELS):
                slot_info["rank_le"][j] += int((rank <= math.floor(level * tiles) / tiles).sum())
            lp_win = asymptotic_window_log10_p(stat, slot_info["hi"] - slot_info["lo"] + 1)
            for col in np.flatnonzero(lp_win <= A1_LINE_LOG10):
                slot_info["hits"].append(
                    {
                        "pub": loaded["name"],
                        "column": int(col),
                        "log10_p_asymptotic": float(lp_win[col]),
                        "rank_p": float(rank[col]),
                    }
                )
        per_pub_ratio = local_ratio_matrix(s)
        per_pub_rank = {
            name: window_rank(per_pub_ratio, m, columns[name]["lo"], columns[name]["hi"]) for name, _, _ in TARGETS
        }
        per_pub[loaded["name"]] = {
            "columns": c.shape[1],
            "stack": s.astype(np.float32),
            "rank": {k: (None if v is None else float(v[1])) for k, v in per_pub_rank.items()},
        }
    return {
        "job": job["job"],
        "run": job["run"],
        "n": n,
        "slot_s": slot,
        "C": count,
        "S": total,
        "per_pub": per_pub,
        "columns": columns,
    }


def local_ratio(stack: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = HALF + GUARD
    m = stack.size
    csum = np.concatenate([[0.0], np.cumsum(stack)])
    idx = np.arange(h, m - h)
    nb = (csum[idx - GUARD] - csum[idx - h] + csum[idx + h + 1] - csum[idx + GUARD + 1]) / (2 * HALF)
    return idx, stack[idx] / np.maximum(nb, 1e-300)


def design_of(row: dict[str, Any], n_pubs: int) -> str:
    return f"slot {row['slot_ms']:.3f} ms, {row['n']} shots, {n_pubs} PUBs"


def calibrated_tails(cat: dict[str, Any], results: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Bin-enumeration ranks of the two windows, their combination, and job-level Bonferroni minima."""
    import gzip
    import json

    n_pubs = {j["job"]: len(j["pubs"]) for j in cat["jobs"]}
    by_job = {r["job"]: r for r in results if r["C"] > 0}
    row_of = {r["job"]: r for r in rows}
    out: dict[str, Any] = {"targets": {}}
    for name, centre, basis in TARGETS:
        jobs = []
        for job, r in by_job.items():
            info = r["columns"][name]
            m = r["S"].size
            ranked = window_rank(local_ratio_matrix(r["S"]), m, info["lo"], info["hi"])
            if ranked is None:
                continue
            stat, rank, tiles = ranked
            pub_ranks = [v["rank"][name] for v in r["per_pub"].values() if v["rank"][name] is not None]
            jobs.append(
                {
                    "job": job,
                    "run": r["run"],
                    "design": design_of(row_of[job], n_pubs[job]),
                    "tiles": tiles,
                    "window_bins": [info["lo"], info["hi"]],
                    "stack_statistic": float(stat),
                    "stack_rank_p": float(rank),
                    "n_pubs": len(pub_ranks),
                    "pub_rank_p": pub_ranks,
                    "n_columns": info["n"],
                    "column_rank_counts": dict(zip(map(str, RANK_LEVELS), info["rank_le"], strict=True)),
                    "column_hits_at_a1_line": info["hits"],
                }
            )
        entry: dict[str, Any] = {"centre_hz": centre, "half_width_hz": WINDOW, "basis": basis, "n_jobs": len(jobs)}
        for level in RANK_LEVELS:
            q = [math.floor(level * j["tiles"]) / j["tiles"] for j in jobs]
            passing = [j for j, qj in zip(jobs, q, strict=True) if j["stack_rank_p"] <= qj]
            entry[f"jobs_rank_p_at_most_{level}"] = {
                "observed": len(passing),
                "expected": float(sum(q)),
                "log10_p_poisson_binomial": exact_laws.poisson_binomial_log10_upper(q, len(passing)),
                "designs": sorted({j["design"] for j in passing}),
                "jobs": [j["job"] for j in passing],
            }
            by_design: dict[str, list[tuple[float, bool]]] = {}
            for j, qj in zip(jobs, q, strict=True):
                by_design.setdefault(j["design"], []).append((qj, j["stack_rank_p"] <= qj))
            design_q = [1.0 - math.prod(1.0 - qj for qj, _ in members) for members in by_design.values()]
            design_hit = sum(1 for members in by_design.values() if any(hit for _, hit in members))
            entry[f"designs_rank_p_at_most_{level}"] = {
                "n_designs": len(by_design),
                "observed": design_hit,
                "expected": float(sum(design_q)),
                "log10_p_poisson_binomial": exact_laws.poisson_binomial_log10_upper(design_q, design_hit),
                "note": "a design counts once; its chance of one passing job assumes independent jobs inside it",
            }
            pub_q = [(math.floor(level * j["tiles"]) / j["tiles"], r_) for j in jobs for r_ in j["pub_rank_p"]]
            k_pub = sum(1 for qj, r_ in pub_q if r_ <= qj)
            entry[f"pubs_rank_p_at_most_{level}"] = {
                "n_pubs": len(pub_q),
                "observed": k_pub,
                "expected": float(sum(qj for qj, _ in pub_q)),
                "log10_p_poisson_binomial": exact_laws.poisson_binomial_log10_upper([qj for qj, _ in pub_q], k_pub),
            }
            cols = [
                (j["n_columns"], j["column_rank_counts"][str(level)], math.floor(level * j["tiles"]) / j["tiles"])
                for j in jobs
            ]
            entry[f"columns_rank_p_at_most_{level}"] = {
                "n_columns": sum(c[0] for c in cols),
                "observed": sum(c[1] for c in cols),
                "expected": float(sum(c[0] * c[2] for c in cols)),
            }
        entry["jobs"] = jobs
        out["targets"][name] = entry
    # job-level Bonferroni minimum of the per-column p-values of a1_line_scan.py (any dependence between columns)
    file_job = {p["file"]: j["job"] for j in cat["jobs"] for p in j["pubs"]}
    with gzip.open(common.OUT / "a1_pvalues.json.gz", "rt") as handle:
        a1_rows = json.load(handle)["tests"]
    best: dict[str, dict[str, list[float]]] = {}
    for test_id, family, lp in a1_rows:
        job = file_job[test_id.split("|", 1)[0]]
        fam_best = best.setdefault(job, {}).setdefault(family, [0.0, 0.0])
        fam_best[0] = min(fam_best[0], float(lp))
        fam_best[1] += 1
    bonferroni_min = {}
    for job, fams in best.items():
        bonferroni_min[job] = {
            fam: {
                "n_tests": int(v[1]),
                "min_log10_p": v[0],
                "bonferroni_min_log10_p": min(0.0, v[0] + math.log10(v[1])),
            }
            for fam, v in fams.items()
        }
    out["job_bonferroni_min_a1_columns"] = bonferroni_min
    return out


def main() -> None:
    cat = common.catalog()
    tasks = [{"job": j, "n": j["pubs"][0]["shots"]} for j in cat["jobs"]]
    results = common.ordered_map(stack_job, tasks, min_items=1)
    rows = []
    tests: list[tuple[str, str, float]] = []
    for r in results:
        if r["C"] == 0:
            continue
        n, slot, c_cols, s_arr = r["n"], r["slot_s"], r["C"], r["S"]
        m = s_arr.size
        # white stacked line, bins above the drift band
        white = s_arr[LOW:]
        kw = int(white.argmax()) + LOW + 1
        lp_white = float(min(0.0, (gamma.logsf(white.max(), c_cols) + math.log(white.size)) / math.log(10)))
        idx, ratio = local_ratio(s_arr)
        kl = int(idx[ratio.argmax()]) + 1
        lp_local = float(
            min(0.0, (fdist.logsf(ratio.max(), 2 * c_cols, 128 * c_cols) + math.log(idx.size)) / math.log(10))
        )
        lo = max(int(math.floor((MAINS - WINDOW) * slot * n)), 1)
        hi = min(int(math.ceil((MAINS + WINDOW) * slot * n)), m)
        sel = np.where((idx + 1 >= lo) & (idx + 1 <= hi))[0]
        if sel.size:
            kt = int(idx[sel[ratio[sel].argmax()]]) + 1
            lp_mains = float(
                min(0.0, (fdist.logsf(ratio[sel].max(), 2 * c_cols, 128 * c_cols) + math.log(sel.size)) / math.log(10))
            )
            r_mains = float(ratio[sel].max())
        else:
            kt, lp_mains, r_mains = None, 0.0, None
        # sub-bin refinement of the narrow peak by a parabola through log S at k-1, k, k+1
        y0, y1, y2 = (math.log(s_arr[kl - 2]), math.log(s_arr[kl - 1]), math.log(s_arr[kl]))
        denom = y0 - 2 * y1 + y2
        shift = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        row = {
            "run": r["run"],
            "job": r["job"],
            "n": n,
            "slot_ms": slot * 1e3,
            "columns": c_cols,
            "white_peak_bin": kw,
            "white_peak_hz": kw / (n * slot),
            "lp_white": lp_white,
            "narrow_peak_bin": kl,
            "narrow_peak_hz": (kl + shift) / (n * slot),
            "narrow_peak_hz_resolution": 1 / (n * slot),
            "narrow_peak_ratio": float(ratio.max()),
            "lp_narrow": lp_local,
            "mains_bin": kt,
            "mains_ratio": r_mains,
            "lp_mains_60hz": lp_mains,
        }
        rows.append(row)
        tests += [
            (f"{r['run']}|{r['job']}|white", "stack_white", lp_white),
            (f"{r['run']}|{r['job']}|narrow", "stack_narrow", lp_local),
            (f"{r['run']}|{r['job']}|mains", "stack_60hz", lp_mains),
        ]
    corr = common.global_corrections(tests, ALPHA)
    bh = set(corr.pop("_bh_member_ids", []))
    thr = corr["bonferroni_log10_threshold"]
    for row in rows:
        for fam, key in (("white", "lp_white"), ("narrow", "lp_narrow"), ("mains", "lp_mains_60hz")):
            row[f"{fam}_bonferroni"] = bool(row[key] <= thr)
            row[f"{fam}_bh"] = f"{row['run']}|{row['job']}|{fam}" in bh
    # per-PUB breakdown at the stacked 60 Hz bin and at the narrow-peak bin of each flagged job
    pub_rows = []
    by_job = {r["job"]: r for r in results}
    for row in rows:
        targets = []
        if row["mains_bonferroni"]:
            targets.append(("60hz_window_peak", row["mains_bin"]))
        if row["narrow_bonferroni"]:
            targets.append(("narrow_peak", row["narrow_peak_bin"]))
        if not targets:
            continue
        r = by_job[row["job"]]
        record = common.record_of(row["run"]) or {}
        members = {e["name"]: [c["member"] for c in e["components"]][:3] for e in record.get("execution_pubs", [])}
        for label, kt in targets:
            for name, entry in r["per_pub"].items():
                st = entry["stack"].astype(np.float64)
                idx2, ratio2 = local_ratio(st)
                j2 = np.where(idx2 + 1 == kt)[0]
                if not j2.size:
                    continue
                ratio_at = float(ratio2[j2[0]])
                cc = entry["columns"]
                lp = float(min(0.0, fdist.logsf(ratio_at, 2 * cc, 128 * cc) / math.log(10)))
                pub_rows.append(
                    {
                        "run": row["run"],
                        "job": row["job"],
                        "bin_label": label,
                        "bin": kt,
                        "hz": kt / (row["n"] * row["slot_ms"] * 1e-3),
                        "pub": name,
                        "columns": cc,
                        "ratio_at_bin": ratio_at,
                        "log10_p_bin": lp,
                        "members": members.get(name),
                    }
                )
    pub_rows.sort(key=lambda x: x["log10_p_bin"])
    calibrated = calibrated_tails(cat, results, rows)
    out = {
        "analysis": "a1b_job_stack",
        "n_jobs_stacked": len(rows),
        "n_tests": len(tests),
        "corrections": corr,
        "jobs": rows,
        "mains_jobs": [r for r in rows if r["mains_bonferroni"]],
        "n_jobs_mains_bonferroni": sum(r["mains_bonferroni"] for r in rows),
        "n_jobs_narrow_bonferroni": sum(r["narrow_bonferroni"] for r in rows),
        "n_jobs_white_bonferroni": sum(r["white_bonferroni"] for r in rows),
        "pub_rows_at_flagged_bins": pub_rows,
        "n_pub_rows_at_flagged_bins": len(pub_rows),
        "calibrated": calibrated,
        "stack_p_values_note": (
            "Gamma and F stack p-values assume independent columns; positive column correlation makes them "
            "anti-conservative. `calibrated` holds the bin-enumeration, cross-unit and job-level Bonferroni results."
        ),
    }
    common.write_json(common.OUT / "a1b_job_stack.json", out)
    common.write_json_gz(common.OUT / "a1b_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 4)] for t in tests]})
    print(
        out["n_jobs_stacked"],
        out["corrections"],
        out["n_jobs_mains_bonferroni"],
        out["n_jobs_narrow_bonferroni"],
        out["n_jobs_white_bonferroni"],
    )
    for name, entry in calibrated["targets"].items():
        print(
            name,
            {k: v for k, v in entry.items() if k != "jobs"},
        )
    for r in out["mains_jobs"]:
        print(
            r["run"][-27:],
            r["n"],
            round(r["slot_ms"], 3),
            r["narrow_peak_hz"],
            r["narrow_peak_hz_resolution"],
            r["lp_narrow"],
            r["lp_mains_60hz"],
            r["columns"],
        )


if __name__ == "__main__":
    main()
