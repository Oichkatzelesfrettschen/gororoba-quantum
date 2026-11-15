"""Exploratory: leak control of the phase fold. The line's frequency and phase come from q4's bit on the odd-indexed
shots; the selector contrast is folded on the even-indexed shots. Null by the same procedure: maximize q4's Fourier
amplitude in an off-line band (0.02350 to 0.02358 cycles per shot), then fold. b0 and b0-rx jobs only."""

import json
from typing import Any

import line_fold
import numpy as np
from scan_forward import HERE

import parallel


def job_level(values: list[complex]) -> dict[str, float]:
    """Job-level calibration of a coherent mean of per-job harmonics: the standard error of the projections on the
    mean's direction over jobs, and the exact sign-flip null (every pattern of +-1 per job), whose spread and tail
    take the fitted phases, the frequency drift and the between-job scatter as random."""
    h = np.array(values)
    mean = h.mean()
    unit = mean / abs(mean)
    projections = (h * np.conj(unit)).real
    signs = np.array(np.meshgrid(*[[1.0, -1.0]] * len(h), indexing="ij")).reshape(len(h), -1)
    null = np.abs((signs * h[:, None]).mean(0))
    return {
        "cluster_se": float(projections.std(ddof=1) / np.sqrt(len(h))),
        "sign_flip_p": float((null >= abs(mean) - 1e-15).mean()),
        "sign_flip_null_component_sd": float(np.sqrt((np.abs(h) ** 2).sum() / 2) / len(h)),
    }


def main() -> None:
    rows = parallel.ordered_map(line_fold.split_job, line_fold.data_jobs(("b0", "b0-rx")), min_items=2)
    summary: dict[str, Any] = {}
    for name, key in (("line", "h1"), ("off_line", "off_line_h1")):
        values = [r[key][0] * np.exp(1j * r[key][1]) for r in rows]
        h = np.mean(values)
        summary[name] = {
            "jobs": len(rows),
            "coherent_h1": float(abs(h)),
            "shot_noise_se": float(np.sqrt(np.mean([r["se"] ** 2 for r in rows]) / len(rows))),
            "phase": float(np.angle(h)),
            **job_level(values),
        }
        print(name, summary[name])
    (HERE / "line_phase_split.json").write_text(json.dumps({"jobs": rows, "summary": summary}, indent=1) + "\n")


if __name__ == "__main__":
    main()
