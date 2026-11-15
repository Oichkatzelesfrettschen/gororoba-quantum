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
    "follow-up predictions: mean selector contrast at the retention where the exact center reads "
    "visibility 0.42 through the mean bracket matrix of the retained series, under three worlds: "
    "exact pulses; a phase of -0.18 rad before each q12 pulse; a conditional phase of -0.25 rad on "
    "coupler 8-12. Arms: q4 pulses at k steps of 5 degrees; Rz(phi) before each q12 pulse."
)
S = "2026-11-15T001929Z"
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
one = np.zeros(1)
exact_center = laws(rs.CENTER, [(("none", None, None), one)])[0] @ M.T
R = np.linspace(0.05, 1, 381)
r0 = R[np.abs(np.array([rs.visibility(r * exact_center + (1 - r) * U) for r in R]) - 0.42).argmin()]
WORLDS: dict[str, list[tuple[Any, Any]]] = {
    "exact": [],
    "z12 -0.18": [(("pulse", "zb", 12), np.array([-0.18]))],
    "cz(8,12) -0.25": [(("cz", (8, 12), None), np.array([-0.25]))],
}
out = {}


def contrast(arm, items):
    seen = r0 * (laws(arm, items or [(("none", None, None), one)])[0] @ M.T) + (1 - r0) * U
    return round(float(rs.selector_contrast(seen)), 4), round(float(rs.d2_split(seen)[0]), 4)


for k in (-2, -1, 0, 1, 2, 3):
    rs.ARMS[f"q4k{k}"] = ("Rx", "q4", k)
for name, items in WORLDS.items():
    out[name] = {
        "q4": {str(5 * k): contrast(f"q4k{k}", items) for k in (-2, -1, 0, 1, 2, 3)},
        "q12_rz": {
            str(d): contrast(
                rs.CENTER,
                [*items, (("pulse", "zb", 12), np.array([np.radians(d)]))]
                if not (name.startswith("z12"))
                else [(("pulse", "zb", 12), np.array([-0.18 + np.radians(d)]))],
            )
            for d in (-20, -10, 0, 10, 20)
        },
    }
    print(name)
    print("  q4 degrees -> (contrast, d2_split):", out[name]["q4"])
    print("  Rz on q12 degrees -> (contrast, d2_split):", out[name]["q12_rz"])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/followup_predictions.json").write_text(
    json.dumps({"retention": float(r0), "worlds": out}, indent=1) + "\n"
)
