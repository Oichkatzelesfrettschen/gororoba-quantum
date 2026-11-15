"""Exploratory: which probabilities carry the line-phase dependence of the selector contrast in the b0 and b0-rx jobs.

The line's frequency and phase come from q4's bit on the odd-indexed shots; every statistic is folded on the
even-indexed shots in 8 phase bins and reduced to its first harmonic, coherently averaged over the jobs. Statistics:
P(selector reads 0 | coin 1), P(selector reads 0 | coin 0), their difference (the selector contrast), the marginals
P(selector reads 0) and P(coin reads 1), and the contrast within the shots where q4 reads 0 and where q4 reads 1."""

import json

import line_fold
import numpy as np
from scan_forward import HERE

import parallel


def main() -> None:
    rows = parallel.ordered_map(line_fold.conditionals_job, line_fold.data_jobs(("b0", "b0-rx")), min_items=2)
    out = {}
    for key in line_fold.CONDITIONALS:
        per = np.array([complex(*r[key]) for r in rows])
        h = per.mean()
        proj = (per * np.conj(h / abs(h))).real
        out[key] = {
            "h1": float(abs(h)),
            "phase": float(np.angle(h)),
            "cluster_se": float(proj.std(ddof=1) / np.sqrt(len(proj))),
        }
        print(key, {k: round(v, 5) for k, v in out[key].items()})
    (HERE / "line_phase_conditionals.json").write_text(
        json.dumps({"jobs": len(rows), "first_harmonic": out}, indent=1) + "\n"
    )


if __name__ == "__main__":
    main()
