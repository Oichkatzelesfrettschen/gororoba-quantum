"""State-vector laws of the null rotation scan arms under elementary errors, shared by the forward-model scripts here.

`laws(arm, items)` returns the logical outcome laws of one arm, one row per parameter value. `items` lists
(candidate, values) pairs that act together: ("pulse", axis + order, qubit or None) rotates by the value about the
axis before ("b") or after ("a") every pulse of the qubit or of all; ("cz", coupler or None, None) adds the value
to the conditional phase of the CZ gates of one coupler or of all; ("czz", qubit, coupler or None) applies
Rz(value) to the qubit after each of its CZ gates on the coupler or on all; ("none", None, None) changes nothing.
The routine equals `forward_laws` of scripts/qi_pathion_null_rotation_scan_cases.py where both apply."""

# ruff: noqa: E402  (the scan module is imported after the path insertion that locates it)
import math
import sys
from pathlib import Path

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
