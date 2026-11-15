"""Exploratory: selector contrast of every data job in 8 consecutive shot bins, and heterogeneity of the centers."""

# ruff: noqa: E402  (repository modules are imported after the path insertion that locates them)
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

S = "2026-11-15T001929Z"
BINS = 8
A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
out = {}
for batch, row in A["batch_rows"].items():
    d = ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-{batch}"
    man = json.loads((d / "cases.json").read_text())
    roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
    res = json.loads((d / "results.json").read_text())
    for arm, st in zip(row["arms"], row["statistics"], strict=True):
        files = (
            [p for p in (d / "raw").iterdir() if rs.arm_of(p.name.removesuffix(".json")) == arm]
            if arm not in ("b0", "b0-rx") or row["kind"] != "bridge"
            else []
        )
        if len(files) != 1:
            continue
        raw = json.loads(files[0].read_text())
        shots = (
            raw
            if isinstance(raw, list)
            else raw.get("shots") or raw.get("raw_data") or next(v for v in raw.values() if isinstance(v, list))
        )
        n = len(shots) // BINS
        vals = [rs.circuit_statistics(shots[i * n : (i + 1) * n], roles) for i in range(BINS)]
        c = np.array([v["contrast"] for v in vals])
        e = np.array([v["se"] for v in vals])
        chi = float((((c - st["contrast"]) / e) ** 2).sum())
        slope = float(np.polyfit(np.arange(BINS), c, 1, w=1 / e)[0])
        out[f"{batch}/{arm}"] = {
            "bins": c.round(4).tolist(),
            "chi2_7": round(chi, 1),
            "slope_per_bin": round(slope, 5),
            "se_bin": round(float(e.mean()), 4),
        }
        print(f"{batch} {arm:16s} chi2(7)={chi:5.1f} slope={slope:+.5f}  {c.round(3).tolist()}")
cs = [
    (s["contrast"], s["se"])
    for r in A["batch_rows"].values()
    for a, s in zip(r["arms"], r["statistics"], strict=True)
    if a == "b0-rx"
]
c = np.array([x[0] for x in cs])
e = np.array([x[1] for x in cs])
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
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/time_bins.json").write_text(json.dumps(out, indent=1))
