"""Exploratory: per-qubit readout error rates of the eleven readout batches against elapsed time, their binomial
homogeneity chi-square (10 degrees of freedom), and the read-value dependence between register qubits pooled over the
batches. Run from the repository root."""

import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
S = "results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-"
Q = (2, 4, 8, 11, 12)


def midpoint(batch: int) -> float:
    jobs = json.loads((ROOT / f"{S}{batch:02d}/results.json").read_text())["jobs"]
    stamps = []
    for job in jobs:
        result = job["results"][0] if isinstance(job.get("results"), list) else job["results"]
        text = job.get("finished_at") or result.get("created_on")
        stamps.append(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    return sum(stamps) / len(stamps)


shots = {
    b: {k: json.loads((ROOT / f"{S}{b:02d}/raw/readout-{k}.cq.json").read_text()) for k in (0, 1)}
    for b in range(0, 21, 2)
}
start = midpoint(0)
rates = {}
for b, pair in shots.items():
    row = {"minutes": round((midpoint(b) - start) / 60, 1)}
    for q in Q:
        row[f"q{q}_e01"] = sum(s[16 - q] == "1" for s in pair[0]) / len(pair[0])
        row[f"q{q}_e10"] = 1 - sum(s[16 - q] == "1" for s in pair[1]) / len(pair[1])
    rates[f"batch-{b:02d}"] = row
homogeneity = {}
for q in Q:
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
    pooled = [s for pair in shots.values() for s in pair[k]]
    for a, b in ((8, 12), (12, 8), (4, 8), (8, 4), (4, 12), (8, 11), (12, 11), (8, 2)):
        n = [0, 0]
        hit = [0, 0]
        for s in pooled:
            c = s[16 - b] == "1"
            n[c] += 1
            hit[c] += s[16 - a] == "1"
        p0, p1 = hit[0] / n[0], hit[1] / n[1]
        se = math.sqrt(p0 * (1 - p0) / n[0] + p1 * (1 - p1) / n[1])
        dependence[f"readout-{k}: P(q{a}=1 | q{b})"] = {
            "given_0": p0,
            "given_1": p1,
            "difference": p1 - p0,
            "z": (p1 - p0) / se,
        }
out = {"rates": rates, "homogeneity": homogeneity, "read_value_dependence": dependence}
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/bracket_drift.json").write_text(
    json.dumps(out, indent=1) + "\n"
)
for key, row in homogeneity.items():
    print(key, {k: round(v, 4) for k, v in row.items()})
