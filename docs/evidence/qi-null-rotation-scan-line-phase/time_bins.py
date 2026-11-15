"""Exploratory: selector contrast of every data job in 8 consecutive shot bins, and heterogeneity of the centers."""

import json

import line_fold
import numpy as np
import scan_fits
from scan_forward import HERE

import parallel


def main() -> None:
    rows = scan_fits.analysis()["batch_rows"]
    scan = {b for b, r in rows.items() if r["kind"] != "bridge"}
    jobs = [j for j in line_fold.data_jobs() if j[0][-8:] in scan]
    out = {}
    for job, bins in zip(jobs, parallel.ordered_map(line_fold.time_bins_job, jobs, min_items=2), strict=True):
        batch, arm = job[0][-8:], line_fold.arm_of(job[1])
        stat = rows[batch]["statistics"][rows[batch]["arms"].index(arm)]
        c, e = np.array(bins["contrast"]), np.array(bins["se"])
        chi = float((((c - stat["contrast"]) / e) ** 2).sum())
        slope = float(np.polyfit(np.arange(line_fold.BINS), c, 1, w=1 / e)[0])
        out[f"{batch}/{arm}"] = {
            "bins": c.round(4).tolist(),
            "chi2_7": round(chi, 1),
            "slope_per_bin": round(slope, 5),
            "se_bin": round(float(e.mean()), 4),
        }
        print(f"{batch} {arm:16s} chi2(7)={chi:5.1f} slope={slope:+.5f}  {c.round(3).tolist()}")
    out = {key: out[key] for b, r in rows.items() if b in scan for key in (f"{b}/{a}" for a in r["arms"])}
    centers = [
        (s["contrast"], s["se"])
        for r in rows.values()
        for a, s in zip(r["arms"], r["statistics"], strict=True)
        if a == "b0-rx"
    ]
    c = np.array([x[0] for x in centers])
    e = np.array([x[1] for x in centers])
    m = (c / e**2).sum() / (1 / e**2).sum()
    print(
        "centers",
        c.round(4).tolist(),
        "mean",
        round(float(m), 4),
        "chi2",
        round(float((((c - m) / e) ** 2).sum()), 1),
        "dof",
        len(c) - 1,
    )
    (HERE / "time_bins.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
