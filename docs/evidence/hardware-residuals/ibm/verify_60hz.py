"""Independent check of the 60 Hz line: plain FFT of every bit column of the flagged jobs, power stacked per job.

Uses the catalog and reader of common.py for file listing and decoding only; the spectrum, the stacking and the peak
search are recomputed here. Reports, per job, the three strongest stacked bins above bin 40 and their frequency.
The jobs are independent, so their spectra run through `common.ordered_map`.
"""

import json
from pathlib import Path
from typing import Any

import common
import numpy as np


def job_spectrum(job: dict[str, Any]) -> dict[str, Any]:
    """Stacked normalized power of every column with at least 30 minority shots in each outcome, for one job."""
    total: np.ndarray | None = None
    cols = 0
    n = 0
    for pub in job["pubs"]:
        data = common.load_pub(common.ROOT / pub["file"])
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
        raise ValueError(f"job {job['job']} has no column with at least 30 errors and 30 non-errors")
    slot = job["slot_s"]
    top = [int(k) for k in np.argsort(total[40:])[::-1][:3] + 40]
    return {
        "name": job["job"],
        "slot_ms": round(slot * 1e3, 3),
        "n": n,
        "cols": cols,
        "top_bins": [(k, round(k / (n * slot), 2), round(float(total[k]) / cols, 2)) for k in top],
    }


def main() -> None:
    cat = common.catalog()
    stack = json.loads((Path(__file__).parent / "a1b_job_stack.json").read_text())
    flagged = {j["job"] for j in stack["mains_jobs"]}
    jobs = [job for job in cat["jobs"] if job["job"] in flagged]
    for row in common.ordered_map(job_spectrum, jobs, min_items=1):
        print(
            row["name"][:6],
            "slot_ms",
            row["slot_ms"],
            "N",
            row["n"],
            "columns",
            row["cols"],
            "expected mean per bin",
            row["cols"],
            "top bins",
            row["top_bins"],
            flush=True,
        )


if __name__ == "__main__":
    main()
