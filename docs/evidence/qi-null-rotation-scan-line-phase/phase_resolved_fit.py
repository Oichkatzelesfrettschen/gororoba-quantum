"""Exploratory: one error parameter that follows the shot-order line, fitted to the phase-bin contrasts.

Candidates and falsifier stand in the opening print and were written before the fit."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, pairs, region, rs

print(
    "phase-resolved fit, written before fitting: a single error parameter u oscillates with the line, "
    "u = u0 + s A cos(theta), theta = 0 at the maximum of q4's P(1), s the sign of dP(q4 = 1)/du of "
    "the model at u0 for that arm. Data: the selector contrast of each arm type in 8 phase bins "
    "pooled over its jobs (10 arm types, 80 points) plus the 10 mean q4-bit line amplitudes. "
    "Parameters shared by all arms: u0, A. Noise: contraction share 0 at the retention where the "
    "exact center reads visibility 0.42 through the mean bracket matrix. Candidates: z, x or y before "
    "each qubit's pulses or all; conditional phase on each coupler or all; a z phase on one qubit "
    "after each of its CZs on one coupler. Falsifier of a candidate: chi-square of the 80 contrast "
    "points above 124.8 (0.001 point, 78 degrees of freedom); calibration: exact pulses with A = 0."
)
S = "2026-11-15T001929Z"
rows_in = json.loads((ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_bins.json").read_text())
arms_seen = sorted({r["arm"] for r in rows_in if r["arm"] != rs.RETAINED})
data = {}
for a in arms_seen:
    v = [r for r in rows_in if r["arm"] == a]
    data[a] = (
        np.mean([r["bins"] for r in v], 0),
        2 * np.sqrt(np.mean([r["se"] ** 2 for r in v]) / len(v)),
        float(np.mean([r["q4_amp"] for r in v])),
    )
A_ = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
man = json.loads(
    (ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-batch-01/cases.json").read_text()
)
roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
register = [int(q) for q in man["register"]]
gs = [r["guard"] for r in A_["batch_rows"].values()]
mean = {
    q: tuple(float(np.mean([(g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for g in gs])) for i in (0, 1))
    for q in register
}
M = cc.readout_matrix(mean, roles)
U = np.full(rs.NOUT, 1 / rs.NOUT) @ M.T
TH = np.linspace(-0.6, 0.6, 481)
exact_center = laws(rs.CENTER, [(("none", None, None), np.zeros(1))])[0] @ M.T
R = np.linspace(0.05, 1, 381)
r0 = R[np.abs(np.array([rs.visibility(r * exact_center + (1 - r) * U) for r in R]) - 0.42).argmin()]
print("retention", round(float(r0), 3))
d1 = rs.KEYS.index("d1")


def q4p(seen):
    return seen.reshape(*seen.shape[:-1], *([2] * 5)).sum(tuple(-1 - i for i in range(5) if i != d1))[..., 1]


ang = 2 * np.pi * (np.arange(8) + 0.5) / 8
cands = (
    [("none", None, None)]
    + [("pulse", a + "b", q) for a in "zxy" for q in (*region, None)]
    + [("cz", None, None)]
    + [("cz", p, None) for p in pairs]
    + [("czz", q, p) for p in pairs for q in p]
)
U0 = np.linspace(-0.3, 0.3, 61)
AM = np.linspace(0.0, 0.3, 31)
out: list[dict[str, Any]] = []
for cand in cands:
    con = {}
    p4 = {}
    for a in arms_seen:
        seen = r0 * (laws(a, [(cand, TH)]) @ M.T) + (1 - r0) * U
        con[a] = rs.selector_contrast(seen)
        p4[a] = q4p(seen)
    best: tuple[Any, ...] = (np.inf, None)
    for u0 in U0:
        for am in AM if cand[0] != "none" else AM[:1]:
            chi = 0.0
            chia = 0.0
            pred = {}
            for a in arms_seen:
                slope = np.interp(u0 + 1e-3, TH, p4[a]) - np.interp(u0 - 1e-3, TH, p4[a])
                s = 1.0 if slope >= 0 else -1.0
                u = u0 + s * am * np.cos(ang)
                c = np.interp(u, TH, con[a])
                pm = np.interp(u, TH, p4[a])
                amp = abs(2 * np.mean(pm * np.exp(-1j * ang)))
                chi += float((((c - data[a][0]) / data[a][1]) ** 2).sum())
                chia += ((amp - data[a][2]) / 0.002) ** 2
                pred[a] = (c, amp)
            if chi + chia < best[0]:
                best = (chi + chia, chi, chia, float(u0), float(am), pred)
    out.append(
        {
            "cand": str(cand),
            "total": round(best[0], 1),
            "chi_contrast_80": round(best[1], 1),
            "chi_q4amp_10": round(best[2], 1),
            "u0": best[3],
            "A": best[4],
            "pred": {a: [np.round(best[5][a][0], 4).tolist(), round(float(best[5][a][1]), 4)] for a in arms_seen},
        }
    )
    print(
        out[-1]["cand"],
        out[-1]["total"],
        out[-1]["chi_contrast_80"],
        out[-1]["chi_q4amp_10"],
        out[-1]["u0"],
        out[-1]["A"],
        flush=True,
    )
out.sort(key=lambda r: r["total"])
print("RANK")
[print(r["cand"], r["total"], r["chi_contrast_80"], r["chi_q4amp_10"], r["u0"], r["A"]) for r in out[:10]]
b = out[0]
print("BEST", b["cand"])
for a in arms_seen:
    print(
        a.ljust(15),
        "data",
        np.round(data[a][0], 3).tolist(),
        "amp",
        round(data[a][2], 4),
        "| model",
        np.round(b["pred"][a][0], 3).tolist(),
        "amp",
        b["pred"][a][1],
    )
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/phase_resolved_fit.json").write_text(json.dumps(out, indent=1))
