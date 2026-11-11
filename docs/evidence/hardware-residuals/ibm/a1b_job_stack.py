"""Job-level stacked periodogram: a line shared by the columns of one job, in physical frequency.

Follow-up to a1_line_scan.py, whose per-column narrow-line hits cluster at one physical frequency near 60 Hz
across jobs with different slot periods. All PUBs of a job share the shot count N and the column-wise slot
period, so one list-position bin k is one physical frequency f = k / (N slot) for every column of the job.

Falsifier, fixed before the run. For each job, S_k = sum over its tested binary columns (at least 30 minority
shots) of the normalized ordinate c_k is Gamma(C, 1) under independent shots, and the ratio of S_k to the mean
of its 64 neighbors (guard 1 bin) is F(2C, 128C). "No structure" means every job's stacked narrow-line p-value
stays above 0.05 / (74 jobs x 2 families = 148 tests) after the union bound over bins, and the targeted
60 Hz bins (within 0.15 Hz of 60 Hz) of every job stay above 0.05 / 74. The 60 Hz targeted family is
post-hoc (suggested by a1_line_scan.json), so it is labeled exploratory and counted in the multiplicity.
Columns of one PUB share circuit structure, so C counts correlated channels; the p-values are
conservative only if column correlations are positive. The per-column counts of exceedances carry the
unstacked evidence.
"""

from __future__ import annotations

import math
from typing import Any

import common
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


def stack_job(task: dict[str, Any]) -> dict[str, Any]:
    job = task["job"]
    n = task["n"]
    m = (n - 1) // 2
    total = np.zeros(m)
    count = 0
    per_pub: dict[str, Any] = {}
    slot = job["slot_s"]
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
        per_pub[loaded["name"]] = {"columns": c.shape[1], "stack": s.astype(np.float32)}
    return {"job": job["job"], "run": job["run"], "n": n, "slot_s": slot, "C": count, "S": total, "per_pub": per_pub}


def local_ratio(stack: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = HALF + GUARD
    m = stack.size
    csum = np.concatenate([[0.0], np.cumsum(stack)])
    idx = np.arange(h, m - h)
    nb = (csum[idx - GUARD] - csum[idx - h] + csum[idx + h + 1] - csum[idx + GUARD + 1]) / (2 * HALF)
    return idx, stack[idx] / np.maximum(nb, 1e-300)


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
