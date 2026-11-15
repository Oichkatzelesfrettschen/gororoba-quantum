"""Exploratory: one global parameter per elementary error, fitted to all 24 scan arms at matched center visibility.

Written before fitting. Candidates: a constant rotation about x, y or z before or after every pulse of one region
qubit or of all; a constant conditional-phase error on every CZ or on the CZs of one coupler; none (exact). Statistic:
chi-square of the 24 raw selector contrasts of the eight scan batches with one parameter shared by all batches and a
contraction (share 0 or 1) matched to each batch's center visibility. Split: fit on the forward round (batches 01 to
07), score on the mirror round (13 to 19) with the parameter fixed. Falsifier of a candidate: mirror chi-square above
the 0.001 point of chi-square with 12 degrees of freedom (32.9)."""

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

cc = rs.cc
ref = rs.retained()
region = ref["region"]
ax = {q: i for i, q in enumerate(region)}
pairs = sorted({tuple(sorted(q)) for g, a, q in ref["ops"] if g == "CZ"})


def rot(axis, t):
    return np.cos(t / 2)[:, None, None] * np.eye(2) - 1j * np.sin(t / 2)[:, None, None] * rs.PAULI[axis]


def laws(arm, items):
    thetas0 = items[0][1]
    pulse, scope, steps = rs.ARMS[arm]
    inj = () if scope is None else rs.SCOPES[scope]
    n = len(thetas0)
    shape = (2,) * 5
    psi = np.zeros((n, *shape), complex)
    psi.reshape(n, -1)[:, 0] = 1
    idx = np.indices(shape)
    for gate, angle, qs in ref["ops"]:
        if gate == "CZ":
            both = idx[ax[qs[0]]] * idx[ax[qs[1]]]
            ph = np.zeros(n)
            for (kind, a, _b), thetas in items:
                if kind == "cz" and (a is None or tuple(sorted(qs)) == a):
                    ph = ph + thetas
            psi = psi * np.where(both[None] == 1, -np.exp(1j * ph)[:, None, None, None, None, None], 1.0)
            for (kind, a, b), thetas in items:
                if kind == "czz" and a in qs and (b is None or tuple(sorted(qs)) == b):
                    psi = psi * np.exp(1j * thetas[:, None, None, None, None, None] * (idx[ax[a]][None] - 0.5))
            continue
        q = qs[0]
        if gate == "Rz":
            u = np.broadcast_to(rs.rotation("z", float(angle or 0.0)), (n, 2, 2))
        else:
            ex = rs.rotation("x", math.pi / 2 + (steps * rs.STEP if pulse == "Rx" and q in inj else 0.0))
            u = np.broadcast_to(ex, (n, 2, 2))
            for (kind, a, b), thetas in items:
                if kind == "pulse" and (b is None or q == b):
                    e = rot(a[0], thetas)
                    u = u @ e if a[1] == "b" else e @ u
        m = np.moveaxis(psi, ax[q] + 1, -1)
        lo, hi = m[..., 0], m[..., 1]
        uu = u[:, :, :, None, None, None, None]
        psi = np.moveaxis(
            np.stack([uu[:, 0, 0] * lo + uu[:, 0, 1] * hi, uu[:, 1, 0] * lo + uu[:, 1, 1] * hi], -1), -1, ax[q] + 1
        )
    p = np.abs(psi) ** 2
    return p.transpose([0, *(ax[ref["roles"][k]] + 1 for k in reversed(rs.KEYS))]).reshape(n, rs.NOUT)


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
