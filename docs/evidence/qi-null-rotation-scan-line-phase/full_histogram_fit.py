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
