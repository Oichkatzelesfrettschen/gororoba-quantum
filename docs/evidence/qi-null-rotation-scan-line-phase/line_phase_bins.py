"""Exploratory: selector contrast and bit means of each data job in 8 bins of the shot-order line's phase.

Written before computing. The line's frequency and phase per job come from the q4 bit (largest |sum x exp(-2 pi i f n)|
on a grid of 0.02008 to 0.02016 cycles per shot); phase 0 is the maximum of q4's P(1). Statistic: first and second
harmonic of the selector contrast over the phase, per job and pooled over the eleven b0-rx jobs. Null: no dependence,
harmonic amplitudes within their binomial errors; calibration: the same fold at a frequency outside the line
(0.0237 cycles per shot) gives the null distribution in the same data."""

import json
from typing import Any

import line_fold
import numpy as np
from scan_forward import HERE

import parallel


def main() -> None:
    rows = parallel.ordered_map(line_fold.bins_job, line_fold.data_jobs(), min_items=2)
    pooled: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        pooled.setdefault(row["arm"], []).append(row)
    print("POOLED (coherent mean over jobs of one arm)")
    summary: dict[str, Any] = {}
    for arm, v in pooled.items():
        h1 = np.mean([r["h1"][0] * np.exp(1j * r["h1"][1]) for r in v])
        h2 = np.mean([r["h2"][0] * np.exp(1j * r["h2"][1]) for r in v])
        g1 = np.mean([r["null_h1"] * np.exp(1j * r["null_h1_phase"]) for r in v])
        g2 = np.mean([r["null_h2"] * np.exp(1j * r["null_h2_phase"]) for r in v])
        se = float(np.sqrt(np.mean([r["se"] ** 2 for r in v]) / len(v)))
        proj = (np.array([r["h1"][0] * np.exp(1j * r["h1"][1]) for r in v]) * np.conj(h1 / abs(h1))).real
        summary[arm] = {
            "jobs": len(v),
            "mean_contrast": float(np.mean([r["bins"] for r in v])),
            "h1": line_fold.polar(h1),
            "h2": line_fold.polar(h2),
            "shot_noise_se": se,
            "cluster_se_h1": float(proj.std(ddof=1) / np.sqrt(len(v))) if len(v) > 2 else None,
            "off_line_h1": float(abs(g1)),
            "off_line_h2": float(abs(g2)),
        }
        print(arm.ljust(15), {k: x for k, x in summary[arm].items()})
    (HERE / "line_phase_bins_pooled.json").write_text(json.dumps(summary, indent=1) + "\n")
    (HERE / "line_phase_bins.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
