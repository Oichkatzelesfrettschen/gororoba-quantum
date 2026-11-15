"""Exploratory: per-qubit readout error rates of the eleven readout batches against elapsed time, their binomial
homogeneity chi-square (10 degrees of freedom), and the read-value dependence between register qubits pooled over the
batches. Run from the repository root."""

import json
import math

import line_fold
from scan_forward import HERE

import parallel


def main() -> None:
    batches = list(range(0, 21, 2))
    jobs = parallel.ordered_map(line_fold.bracket_job, batches, min_items=2)
    start = jobs[0]["midpoint"]
    rates = {
        f"batch-{b:02d}": {"minutes": round((job["midpoint"] - start) / 60, 1)} | job["rates"]
        for b, job in zip(batches, jobs, strict=True)
    }
    homogeneity = {}
    for q in line_fold.REGISTER:
        for kind in ("e01", "e10"):
            v = [r[f"q{q}_{kind}"] for r in rates.values()]
            m = sum(v) / len(v)
            homogeneity[f"q{q}_{kind}"] = {
                "mean": m,
                "min": min(v),
                "max": max(v),
                "chi2_10": sum((x - m) ** 2 / (m * (1 - m) / 32768) for x in v),
            }
    dependence = {}
    for k in (0, 1):
        for a, b in line_fold.DEPENDENCE_PAIRS:
            n = [sum(job["counts"][f"{k}:{a}:{b}"][0][i] for job in jobs) for i in (0, 1)]
            hit = [sum(job["counts"][f"{k}:{a}:{b}"][1][i] for job in jobs) for i in (0, 1)]
            p0, p1 = hit[0] / n[0], hit[1] / n[1]
            se = math.sqrt(p0 * (1 - p0) / n[0] + p1 * (1 - p1) / n[1])
            dependence[f"readout-{k}: P(q{a}=1 | q{b})"] = {
                "given_0": p0,
                "given_1": p1,
                "difference": p1 - p0,
                "z": (p1 - p0) / se,
            }
    out = {"rates": rates, "homogeneity": homogeneity, "read_value_dependence": dependence}
    (HERE / "bracket_drift.json").write_text(json.dumps(out, indent=1) + "\n")
    for key, row in homogeneity.items():
        print(key, {k: round(v, 4) for k, v in row.items()})


if __name__ == "__main__":
    main()
