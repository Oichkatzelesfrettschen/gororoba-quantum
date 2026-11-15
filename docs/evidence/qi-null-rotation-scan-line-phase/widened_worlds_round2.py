"""Exploratory: phases tied to CZ gates, scored with one parameter per batch.

Candidates and statistic stand in the opening print and were written before the fit."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, pairs, region, rs

cands: list[tuple[Any, Any, Any]] = [("none", None, None)]
for axis in "xyz":
    for order in "ba":
        if axis == "x" and order == "a":
            continue
        for q in (None, *region):
            cands.append(("pulse", axis + order, q))
cands = [c for c in cands if c[0] == "none" or c == ("pulse", "zb", 12) or c == ("pulse", "zb", None)]
cands += (
    [("cz", None, None), ("cz", (8, 12), None)]
    + [("czz", q, None) for q in region]
    + [("czz", q, p) for p in pairs for q in p]
)
print(
    "round 2, written before fitting: a z rotation on one qubit after each CZ it takes part in (all "
    "its couplers, or one coupler); statistic adds per-batch parameters (16 degrees of freedom, 0.001 "
    "point 39.25)"
)
TH = np.linspace(-0.35, 0.35, 281)
A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
man = json.loads(
    (
        ROOT / "results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-01/cases.json"
    ).read_text()
)
roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
register = [int(q) for q in man["register"]]
B = []
for batch, row in A["batch_rows"].items():
    if row["kind"] == "bridge":
        continue
    g = row["guard"]
    mean = {q: tuple((g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for i in (0, 1)) for q in register}
    B.append(
        (
            batch,
            tuple(row["arms"]),
            cc.readout_matrix(mean, roles),
            np.array([s["contrast"] for s in row["statistics"]]),
            np.array([s["se"] for s in row["statistics"]]),
            row["statistics"][row["arms"].index(rs.CENTER)]["visibility"],
        )
    )
R = np.linspace(0.02, 1.0, 197)


def model(cand, mix):
    table = {arm: laws(arm, [(cand, TH)]) for arm in rs.ARM_NAMES if arm != rs.RETAINED}
    out: list[dict[str, Any]] = []
    for _batch, arms, M, _c, _e, cv in B:
        cen = np.stack([rs.read(rs.contract(table[rs.CENTER][:, None], r, mix)[:, 0], M) for r in R])  # (r, theta, out)
        vis = rs.visibility(cen)  # (r, theta)
        pick = np.abs(vis - cv).argmin(0)
        pred = np.stack(
            [
                [
                    rs.selector_contrast(rs.read(rs.contract(table[a][t][None, None], R[pick[t]], mix)[0, 0], M))
                    for a in arms
                ]
                for t in range(len(TH))
            ]
        )
        out.append(pred)  # (theta, arm)
    return out


rows: list[dict[str, Any]] = []
for cand in cands:
    for mix in (0.0,):
        pred = model(cand, mix)
        chi = [(((p - c) / e) ** 2).sum(1) for p, (_, _, _, c, e, _) in zip(pred, B, strict=True)]
        fwd, mir, tot = sum(chi[:4]), sum(chi[4:]), sum(chi)
        j = int(fwd.argmin())
        k = int(tot.argmin())
        per = [float(x.min()) for x in chi]
        par = [round(float(TH[int(x.argmin())]), 3) for x in chi]
        rows.append(
            {
                "cand": str(cand),
                "mix": mix,
                "theta_fwd": round(float(TH[j]), 4),
                "chi_fwd": round(float(fwd[j]), 1),
                "chi_mirror_at_fwd": round(float(mir[j]), 1),
                "theta_all": round(float(TH[k]), 4),
                "chi_all": round(float(tot[k]), 1),
                "chi_per_batch_param": round(sum(per), 1),
                "params": par,
                "per": [round(x, 1) for x in per],
            }
        )
        if cand[0] == "none":
            break
rows.sort(key=lambda r: r["chi_per_batch_param"])
for r in rows[:25]:
    print(r)
print("exact:", [r for r in rows if "none" in r["cand"]])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/widened_worlds_round2.json").write_text(
    json.dumps(rows, indent=1)
)
