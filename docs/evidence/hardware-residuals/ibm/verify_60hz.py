"""Independent check of the 60 Hz line: plain FFT of every bit column of the flagged jobs, power stacked per job.

Uses the catalog and reader of common.py for file listing and decoding only; the spectrum, the stacking and the peak
search are recomputed here. Reports, per job, the three strongest stacked bins above bin 40 and their frequency.
"""

import json

import common
import numpy as np

cat = common.catalog()
stack = json.load(open(common.Path(__file__).parent / "a1b_job_stack.json"))
flag = {j["job"]: j for j in stack["mains_jobs"]}
jobs = cat["jobs"] if isinstance(cat["jobs"], list) else list(cat["jobs"].values())
for job in jobs:
    name = job.get("job") or job.get("job_id")
    if name not in flag:
        continue
    total: np.ndarray | None = None
    cols = 0
    for pub in job["pubs"]:
        data = common.load_pub(common.ROOT / pub["file"] if hasattr(common, "ROOT") else pub["file"])
        bits = np.concatenate(list(data["regs"].values()), axis=1)
        x = bits.astype(float)
        keep = (x.sum(0) >= 30) & ((1 - x).sum(0) >= 30)
        x = x[:, keep]
        if not x.shape[1]:
            continue
        x = x - x.mean(0)
        power = np.abs(np.fft.rfft(x, axis=0)) ** 2 / (x.var(0) * x.shape[0])
        total = power.sum(1) if total is None else total + power.sum(1)
        cols += x.shape[1]
        n = x.shape[0]
    if total is None:
        raise ValueError(f"job {name} has no column with at least 30 errors and 30 non-errors")
    slot = job["slot_s"]
    top = [int(k) for k in np.argsort(total[40:])[::-1][:3] + 40]
    print(
        name[:6],
        "slot_ms",
        round(slot * 1e3, 3),
        "N",
        n,
        "columns",
        cols,
        "expected mean per bin",
        cols,
        "top bins",
        [(k, round(k / (n * slot), 2), round(float(total[k]) / cols, 2)) for k in top],
        flush=True,
    )
