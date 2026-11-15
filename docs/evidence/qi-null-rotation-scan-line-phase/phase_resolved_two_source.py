"""Exploratory: two error parameters driven by one line phase, fitted to the phase-bin contrasts.

Candidates and falsifier stand in the opening print and were written before the fit."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, rs
from scipy.interpolate import RegularGridInterpolator

print(
    "(single-parameter preamble kept for the shared setup) a single error parameter u oscillates with "
    "the line, u = u0 + s A cos(theta), theta = 0 at the maximum of q4's P(1), s the sign of dP(q4 = "
    "1)/du of the model at u0 for that arm. Data: the selector contrast of each arm type in 8 phase "
    "bins pooled over its jobs (10 arm types, 80 points) plus the 10 mean q4-bit line amplitudes. "
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

print(
    "two-source phase-resolved fit, written before fitting: one line drives two error parameters with "
    "a common phase, a = a0 + s Aa cos(theta) and b = b0 + s Ab cos(theta) (Ab of either sign), s per "
    "arm chosen so that the model's q4 P(1) is largest at theta = 0. Pairs: (z on q4 pulses, z on q12 "
    "pulses), (cz phase 4-8, z on q12), (z on q4, cz phase 8-12), (cz phase 4-8, cz phase 8-12), (z "
    "on q4, z on q8), (z on q8, z on q12). Four shared parameters; falsifier: chi-square of the 80 "
    "contrast points above 122.3 (0.001 point, 76 degrees of freedom)."
)

G = np.linspace(-0.5, 0.5, 41)
ga, gb = [x.ravel() for x in np.meshgrid(G, G, indexing="ij")]
PAIRS = [
    (("pulse", "zb", 4), ("pulse", "zb", 12)),
    (("cz", (4, 8), None), ("pulse", "zb", 12)),
    (("pulse", "zb", 4), ("cz", (8, 12), None)),
    (("cz", (4, 8), None), ("cz", (8, 12), None)),
    (("pulse", "zb", 4), ("pulse", "zb", 8)),
    (("pulse", "zb", 8), ("pulse", "zb", 12)),
]
A0 = np.linspace(-0.3, 0.3, 25)
AA = np.linspace(0.0, 0.2, 9)
AB = np.linspace(-0.2, 0.2, 17)
a0, aa, b0, ab = [x.ravel() for x in np.meshgrid(A0, AA, A0, AB, indexing="ij")]
cos = np.cos(ang)
out: list[dict[str, Any]] = []
for ca, cb in PAIRS:
    chi = np.zeros(len(a0))
    chia = np.zeros(len(a0))
    preds = {}
    for a in arms_seen:
        seen = r0 * (laws(a, [(ca, ga), (cb, gb)]) @ M.T) + (1 - r0) * U
        fc = RegularGridInterpolator((G, G), rs.selector_contrast(seen).reshape(41, 41))
        fp = RegularGridInterpolator((G, G), q4p(seen).reshape(41, 41))
        best_c = None
        res = []
        for sgn in (1.0, -1.0):
            ua = a0[:, None] + sgn * aa[:, None] * cos[None]
            ub = b0[:, None] + sgn * ab[:, None] * cos[None]
            pts = np.stack([ua.ravel(), ub.ravel()], 1)
            c = fc(pts).reshape(-1, 8)
            p = fp(pts).reshape(-1, 8)
            h = 2 * (p * np.exp(-1j * ang)[None]).mean(1)
            res.append((c, h))
        pick = res[0][1].real >= res[1][1].real
        c = np.where(pick[:, None], res[0][0], res[1][0])
        amp = np.where(pick, np.abs(res[0][1]), np.abs(res[1][1]))
        chi += (((c - data[a][0][None]) / data[a][1]) ** 2).sum(1)
        chia += ((amp - data[a][2]) / 0.002) ** 2
        preds[a] = (c, amp)
    k = int((chi + chia).argmin())
    k2 = int(chi.argmin())
    out.append(
        {
            "A": str(ca),
            "B": str(cb),
            "total": round(float(chi[k] + chia[k]), 1),
            "chi_contrast_80": round(float(chi[k]), 1),
            "chi_q4amp_10": round(float(chia[k]), 1),
            "params_a0_Aa_b0_Ab": [round(float(x[k]), 3) for x in (a0, aa, b0, ab)],
            "contrast_only_best": round(float(chi[k2]), 1),
            "contrast_only_params": [round(float(x[k2]), 3) for x in (a0, aa, b0, ab)],
            "pred": {a: [np.round(preds[a][0][k], 4).tolist(), round(float(preds[a][1][k]), 4)] for a in arms_seen},
        }
    )
    print({k_: v for k_, v in out[-1].items() if k_ != "pred"}, flush=True)
out.sort(key=lambda r: r["total"])
b = out[0]
print("BEST", b["A"], b["B"])
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
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/phase_resolved_two_source.json").write_text(
    json.dumps(out, indent=1)
)
