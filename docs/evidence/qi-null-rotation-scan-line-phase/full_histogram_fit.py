"""Exploratory: Pearson chi-square of all 96 outcome counts per batch under a contraction.

Candidates and statistic stand in the opening print and were written before the fit."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, pairs, region, rs

print(
    "full-histogram fit, written before fitting: per batch, Pearson chi-square of the 3 x 32 outcome "
    "counts against the model law (one error parameter, one contraction retention and one contraction "
    "share per batch; 93 - 3 = 90 degrees of freedom per batch, 720 over eight batches). Candidates: "
    "exact; x, y, z on each single qubit's pulses and on all; conditional phase on all CZs and on "
    "each coupler. A crude noise model inflates every chi-square, so the ranking and the gain over "
    "exact carry the reading, and the per-bit marginals of the best model are printed against the "
    "data."
)
S = "2026-11-15T001929Z"
cands = (
    [("none", None, None)]
    + [("pulse", a + "b", q) for a in "xyz" for q in (None, *region)]
    + [("cz", None, None)]
    + [("cz", p, None) for p in pairs]
)
TH = np.linspace(-0.35, 0.35, 141)
A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
B = []
for batch, row in A["batch_rows"].items():
    if row["kind"] == "bridge":
        continue
    d = ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-{batch}"
    man = json.loads((d / "cases.json").read_text())
    roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
    register = [int(q) for q in man["register"]]
    g = row["guard"]
    mean = {q: tuple((g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for i in (0, 1)) for q in register}
    counts = {}
    for f in (d / "raw").iterdir():
        counts[rs.arm_of(f.name.removesuffix(".json"))] = np.asarray(
            cc.coin_counts(json.loads(f.read_text()), roles), float
        )
    B.append((batch, tuple(row["arms"]), cc.readout_matrix(mean, roles), np.stack([counts[a] for a in row["arms"]])))
R = np.linspace(0.05, 1.0, 96)
MIX = (0.0, 0.25, 0.5, 0.75, 1.0)
rows: list[dict[str, Any]] = []
for cand in cands:
    table = {arm: laws(arm, [(cand, TH)]) for arm in rs.ARM_NAMES if arm != rs.RETAINED}
    per = []
    par: list[Any] = []
    for _batch, arms, M, obs in B:
        N = obs.sum(1)[None, None, :, None]
        law = np.stack([table[a] for a in arms], 1)  # (theta, arm, out)
        best: tuple[Any, ...] = (np.inf, None)
        for mix in MIX:
            for r in R:
                p = rs.contract(law, r, mix) @ M.T
                chi = (((obs[None] - N[0] * p) ** 2) / (N[0] * p)).sum((1, 2))
                j = int(chi.argmin())
                if chi[j] < best[0]:
                    best = (float(chi[j]), (float(TH[j]), float(r), mix))
        per.append(best[0])
        par.append(best[1])
    rows.append(
        {
            "cand": str(cand),
            "chi": round(sum(per), 0),
            "per": [round(x) for x in per],
            "theta": [round(p[0], 3) for p in par],
            "r": [round(p[1], 2) for p in par],
            "mix": [p[2] for p in par],
        }
    )
    print(rows[-1], flush=True)
rows.sort(key=lambda r: r["chi"])
print("RANK")
[print(r["cand"], r["chi"], r["per"], r["theta"]) for r in rows[:10]]
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/full_histogram_fit.json").write_text(json.dumps(rows, indent=1))
