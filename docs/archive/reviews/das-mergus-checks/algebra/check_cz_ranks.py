"""Numerical cross-check of G.P6 (nu = 28 - 2 rank C_z), G9/G.40 (rank B = rank C_z - 2) on random points
of V_reg, S+-, Z, the incidence chart, Q=0 and G=0. C_z built from cd_core signs, float64 SVD."""
import json
import numpy as np
from common import sign
rng = np.random.default_rng(9845)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 1
S16 = np.array([[sign(16, p, q) for q in range(16)] for p in range(16)])
S32 = np.array([[sign(32, p, q) for q in range(32)] for p in range(32)])
def Lc(z16):
    M = np.zeros((16, 16), complex)
    for p in range(16):
        for q in range(16):
            M[p ^ q, q] += z16[p] * S16[p, q]
    return M
def Rc(z16):
    M = np.zeros((16, 16), complex)
    for q in range(16):
        for p in range(16):
            M[p ^ q, p] += z16[q] * S16[p, q]
    return M
def Cz(z):
    z16 = np.concatenate([[0], z])
    return ((Lc(z16) - Rc(z16)) / 2)[1:, 1:]
def L32(y):
    M = np.zeros((32, 32))
    for p in range(32):
        if y[p]:
            for q in range(32):
                M[p ^ q, q] += y[p] * S32[p, q]
    return M
def rank(M, tol=1e-8):
    s = np.linalg.svd(M, compute_uv=False)
    return int((s > tol * s[0]).sum())
def nu(z):
    y = np.zeros(32); y[1:16] = z.real; y[17:32] = z.imag
    return 32 - rank(L32(y))
def isotropic(n):
    w = rng.normal(size=n) + 1j * rng.normal(size=n)
    a = rng.normal(size=n); b = rng.normal(size=n)
    b -= a * (a @ b) / (a @ a); b *= np.linalg.norm(a) / np.linalg.norm(b)
    return (a + 1j * b) * (rng.normal() + 1j * rng.normal())
def ocross(a, b):
    r = np.zeros(7, complex)
    for i in range(7):
        for j in range(7):
            k = (i + 1) ^ (j + 1)
            if k: r[k - 1] += sign(8, i + 1, j + 1) * a[i] * b[j]
    return r
pts = {}
for _ in range(5):
    w = rng.normal(size=7) + 1j * rng.normal(size=7); lam = rng.normal() + 1j * rng.normal()
    mu = np.sqrt(-(1 + lam**2) * (w @ w))
    pts.setdefault("V_reg", []).append(np.concatenate([w, [mu], lam * w]))
    w = isotropic(7); pts.setdefault("S_pm", []).append(np.concatenate([w, [0], 1j * w]))
    a, b = isotropic(7), isotropic(7)
    pts.setdefault("Z", []).append(np.concatenate([(a + b) / 2, [0], (a - b) / 2j]))
    u = rng.normal(size=7) + 1j * rng.normal(size=7); U = u @ u; rho = np.sqrt(-U)
    Cu = np.array([ocross(u, e) for e in np.eye(7)]).T
    P = 0.5 * (np.eye(7) - np.outer(u, u) / U + Cu / rho)
    n = P @ (rng.normal(size=7) + 1j * rng.normal(size=7)); lam = rng.normal() + 1j * rng.normal()
    mu = np.sqrt(-(1 + lam**2) * U)
    pts.setdefault("incidence", []).append(np.concatenate([u, [mu], lam * u + n]))
    z = rng.normal(size=15) + 1j * rng.normal(size=15); z[7] = np.sqrt(-(z @ z - z[7]**2))
    pts.setdefault("Q0", []).append(z)
    u = rng.normal(size=7) + 1j * rng.normal(size=7); v = rng.normal(size=7) + 1j * rng.normal(size=7)
    U, V0, W = u @ u, v @ v, u @ v
    mu = np.sqrt(2 * np.sqrt(U * V0 - W**2) - U - V0)
    pts.setdefault("G0", []).append(np.concatenate([u, [mu], v]))
out = {}
for k, L in pts.items():
    rows = []
    for z in L:
        C = Cz(z); t = z.conj(); a = z @ t; h = C @ t
        B = a * C + np.outer(z, h) - np.outer(h, z)
        rows.append((nu(z), rank(C), rank(B), bool(np.allclose(C @ z, 0))))
    out[k] = rows
print(json.dumps(out))
