"""Exploratory: two-parameter composites of the two leading worlds, forward fit and mirror score.

Candidates and falsifier stand in the opening print and were written before the fit."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, rs

print(
    "round 3, written before fitting: pairs A x B with A in {cz phase on coupler 8-12, z on q12 "
    "pulses} and B in the list below; two shared parameters on 24 arms (22 degrees of freedom, 0.001 "
    "point 48.27), and fit on the forward round scored on the mirror round (12 arms, 32.91)"
)
AS = [("cz", (8, 12), None), ("pulse", "zb", 12)]
BS = [
    ("pulse", "zb", 4),
    ("pulse", "yb", 4),
    ("pulse", "xb", 4),
    ("pulse", "xb", 8),
    ("pulse", "zb", 8),
    ("pulse", "yb", 8),
    ("cz", None, None),
    ("cz", (4, 8), None),
    ("pulse", "zb", 2),
    ("pulse", "zb", 11),
    ("czz", 8, (8, 12)),
    ("pulse", "xb", None),
    ("pulse", "xb", 12),
    ("pulse", "yb", 12),
    ("cz", (8, 11), None),
    ("cz", (2, 4), None),
]
G = np.linspace(-0.35, 0.35, 57)
ta, tb = [x.ravel() for x in np.meshgrid(G, G, indexing="ij")]
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
            np.array([s["visibility"] for s in row["statistics"]]),
        )
    )
R = np.linspace(0.02, 1.0, 99)
rows: list[dict[str, Any]] = []
for ca in AS:
    for cb in BS:
        if ca == cb:
            continue
        table = {arm: laws(arm, [(ca, ta), (cb, tb)]) for arm in rs.ARM_NAMES if arm != rs.RETAINED}
        chi = []
        visd = []
        for _batch, arms, M, c, e, cv, vm in B:
            U = np.full(rs.NOUT, 1 / rs.NOUT) @ M.T
            cen = table[rs.CENTER] @ M.T
            vis = rs.visibility(R[:, None, None] * cen[None] + (1 - R[:, None, None]) * U)
            r = R[np.abs(vis - cv).argmin(0)][:, None]
            seen = [r * (table[a] @ M.T) + (1 - r) * U for a in arms]
            pred = np.stack([rs.selector_contrast(x) for x in seen], 1)
            chi.append((((pred - c) / e) ** 2).sum(1))
            visd.append(np.stack([rs.visibility(x) for x in seen], 1) - vm)
        fwd, mir, tot = sum(chi[:4]), sum(chi[4:]), sum(chi)
        j = int(fwd.argmin())
        k = int(tot.argmin())
        rows.append(
            {
                "A": str(ca),
                "B": str(cb),
                "fwd": [round(float(ta[j]), 3), round(float(tb[j]), 3)],
                "chi_fwd": round(float(fwd[j]), 1),
                "chi_mirror_at_fwd": round(float(mir[j]), 1),
                "all": [round(float(ta[k]), 3), round(float(tb[k]), 3)],
                "chi_all": round(float(tot[k]), 1),
                "per_batch": [round(float(x[k]), 1) for x in chi],
                "max_abs_visibility_miss": round(float(max(np.abs(v[k]).max() for v in visd)), 3),
            }
        )
        print(rows[-1], flush=True)
rows.sort(key=lambda r: r["chi_all"])
print("RANK")
[
    print(
        r["A"],
        r["B"],
        r["chi_all"],
        r["all"],
        "mirror@fwd",
        r["chi_mirror_at_fwd"],
        "vis miss",
        r["max_abs_visibility_miss"],
    )
    for r in rows[:12]
]
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/widened_worlds_round3.json").write_text(
    json.dumps(rows, indent=1)
)
