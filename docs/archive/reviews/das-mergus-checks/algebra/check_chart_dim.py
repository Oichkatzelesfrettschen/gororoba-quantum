"""Lower bound for the nullity-8 chart dimension at rows 4, 11, 18: complex rank of the holomorphic
Jacobian of (u, m, mu) -> z, n = Pi_rho(u) m, lambda from mu^2 + (1+lambda^2) U = 0 near lambda=-i."""
import json
from fractions import Fraction
import numpy as np
from common import REPO, sign
rows = json.load(open(REPO + "/docs/evidence/rank_locus_local_dimension/result.json"))["rows"]
def ocross(a, b):
    r = np.zeros(7, complex)
    for i in range(7):
        for j in range(7):
            k = (i + 1) ^ (j + 1)
            if k: r[k - 1] += sign(8, i + 1, j + 1) * a[i] * b[j]
    return r
out = {}
for idx in (4, 11, 18):
    x = np.array([float(Fraction(s)) for s in rows[idx]["x"]])
    z0 = x[1:16] + 1j * x[17:32]
    u0, mu0, v0 = z0[:7], z0[7], z0[8:]
    U0 = u0 @ u0; lam0 = (u0 @ v0) / U0; n0 = v0 - lam0 * u0
    rho0 = (ocross(u0, n0) @ n0.conj()) / (n0 @ n0.conj())
    def zmap(p):
        u, m, mu = p[:7], p[7:14], p[14]
        U = u @ u
        rho = np.sqrt(-U); rho = rho if abs(rho - rho0) < abs(rho + rho0) else -rho
        Cu = np.array([ocross(u, e) for e in np.eye(7)]).T
        P = 0.5 * (np.eye(7) - np.outer(u, u) / U + Cu / rho)
        n = P @ m
        lam = np.sqrt(-mu**2 / U - 1); lam = lam if abs(lam - lam0) < abs(lam + lam0) else -lam
        return np.concatenate([u, [mu], lam * u + n])
    p0 = np.concatenate([u0, n0, [mu0]])
    zz = zmap(p0)
    h = 1e-6
    J = np.array([(zmap(p0 + h * e) - zmap(p0 - h * e)) / (2 * h) for e in np.eye(15)]).T
    s = np.linalg.svd(J, compute_uv=False)
    out[idx] = {"reproduces_witness": float(np.abs(zz - z0).max()), "lambda0": str(lam0), "sv": [float(f"{v:.3g}") for v in s],
                "complex_rank": int((s > 1e-6 * s[0]).sum())}
print(json.dumps(out, indent=1))
