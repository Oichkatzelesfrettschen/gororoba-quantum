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


def laws(arm, cand, thetas):
    kind, a, b = cand
    pulse, scope, steps = rs.ARMS[arm]
    inj = () if scope is None else rs.SCOPES[scope]
    n = len(thetas)
    shape = (2,) * 5
    psi = np.zeros((n, *shape), complex)
    psi.reshape(n, -1)[:, 0] = 1
    idx = np.indices(shape)
    for gate, angle, qs in ref["ops"]:
        if gate == "CZ":
            both = idx[ax[qs[0]]] * idx[ax[qs[1]]]
            ph = thetas if (kind == "cz" and (a is None or tuple(sorted(qs)) == a)) else np.zeros(n)
            psi = psi * np.where(both[None] == 1, -np.exp(1j * ph)[:, None, None, None, None, None], 1.0)
            continue
        q = qs[0]
        if gate == "Rz":
            u = np.broadcast_to(rs.rotation("z", float(angle or 0.0)), (n, 2, 2))
        else:
            ex = rs.rotation("x", math.pi / 2 + (steps * rs.STEP if pulse == "Rx" and q in inj else 0.0))
            if kind == "pulse" and (b is None or q == b):
                e = rot(a[0], thetas)
                u = ex @ e if a[1] == "b" else e @ ex
            else:
                u = np.broadcast_to(ex, (n, 2, 2))
        m = np.moveaxis(psi, ax[q] + 1, -1)
        lo, hi = m[..., 0], m[..., 1]
        uu = u[:, :, :, None, None, None, None]
        psi = np.moveaxis(
            np.stack([uu[:, 0, 0] * lo + uu[:, 0, 1] * hi, uu[:, 1, 0] * lo + uu[:, 1, 1] * hi], -1), -1, ax[q] + 1
        )
    p = np.abs(psi) ** 2
    return p.transpose([0, *(ax[ref["roles"][k]] + 1 for k in reversed(rs.KEYS))]).reshape(n, rs.NOUT)


cands: list[tuple[Any, Any, Any]] = [("none", None, None)]
for axis in "xyz":
    for order in "ba":
        if axis == "x" and order == "a":
            continue
        for q in (None, *region):
            cands.append(("pulse", axis + order, q))
cands += [("cz", None, None)] + [("cz", p, None) for p in pairs]
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
    table = {arm: laws(arm, cand, TH) for arm in rs.ARM_NAMES if arm != rs.RETAINED}
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
    for mix in (0.0, 1.0):
        pred = model(cand, mix)
        chi = [(((p - c) / e) ** 2).sum(1) for p, (_, _, _, c, e, _) in zip(pred, B, strict=True)]
        fwd, mir, tot = sum(chi[:4]), sum(chi[4:]), sum(chi)
        j = int(fwd.argmin())
        k = int(tot.argmin())
        rows.append(
            {
                "cand": str(cand),
                "mix": mix,
                "theta_fwd": round(float(TH[j]), 4),
                "chi_fwd": round(float(fwd[j]), 1),
                "chi_mirror_at_fwd": round(float(mir[j]), 1),
                "theta_all": round(float(TH[k]), 4),
                "chi_all": round(float(tot[k]), 1),
                "per_batch": [round(float(x[k]), 1) for x in chi],
            }
        )
        if cand[0] == "none":
            break
rows.sort(key=lambda r: r["chi_all"])
for r in rows[:25]:
    print(r)
print("exact:", [r for r in rows if "none" in r["cand"]])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/widened_worlds.json").write_text(json.dumps(rows, indent=1))
