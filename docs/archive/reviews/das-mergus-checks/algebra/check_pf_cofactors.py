"""Numerical cross-check of (G.P2): signed order-14 principal Pfaffians of C_z equal Q G z_j, and (G.P3)."""
import json
import numpy as np
from check_cz_ranks import Cz, rng  # reuses cd_core-based C_z
def pfaff(A):
    A = A.astype(complex).copy(); n = A.shape[0]; res = 1.0 + 0j
    for k in range(0, n - 1, 2):
        kp = k + 1 + np.argmax(np.abs(A[k, k + 1:]))
        if kp != k + 1:
            A[[k + 1, kp]] = A[[kp, k + 1]]; A[:, [k + 1, kp]] = A[:, [kp, k + 1]]; res = -res
        if A[k, k + 1] == 0: return 0j
        res *= A[k, k + 1]
        if k + 2 < n:
            tau = A[k, k + 2:] / A[k, k + 1]
            A[k + 2:, k + 2:] += np.outer(tau, A[k + 2:, k + 1]) - np.outer(A[k + 2:, k + 1], tau)
    return res
worst = 0.0; worst_mut = 1e9; worstA = 0.0
for _ in range(10):
    z = rng.normal(size=15) + 1j * rng.normal(size=15)
    u, mu, v = z[:7], z[7], z[8:]
    Q = u @ u + mu**2 + v @ v; G = Q**2 - 4 * ((u @ u) * (v @ v) - (u @ v) ** 2)
    C = Cz(z)
    for j in range(15):
        idx = [i for i in range(15) if i != j]
        P = (-1) ** j * pfaff(C[np.ix_(idx, idx)])
        worst = max(worst, abs(P - Q * G * z[j]) / abs(Q * G * z[j]))
        Gm = Q**2 - 3 * ((u @ u) * (v @ v) - (u @ v) ** 2)
        worst_mut = min(worst_mut, abs(P - Q * Gm * z[j]) / abs(Q * Gm * z[j]))
    t = rng.normal(size=15) + 1j * rng.normal(size=15)
    A = np.zeros((16, 16), complex); A[0, 1:] = -t; A[1:, 0] = t; A[1:, 1:] = C
    worstA = max(worstA, abs(pfaff(A) + (z @ t) * Q * G) / abs((z @ t) * Q * G))
print(json.dumps({"max_rel_err_cofactors": worst, "min_rel_err_mutated_G": worst_mut, "max_rel_err_bordered": worstA}))
