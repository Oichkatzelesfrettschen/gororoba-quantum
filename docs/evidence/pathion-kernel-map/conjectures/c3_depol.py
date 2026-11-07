"""C3: gate-level Pauli depolarization on the routed circuits (the contraction is then bin dependent through the compiled
gate structure), with optional T1, followed by bracket readout. Scan p2 (per CZ), p1 = p2 / 10 per X90/X."""

import numpy as np
from c3_corr import NAMES, OBS, SIGN
from c3_data import KEYS, T, matrix_for, ratio_of
from c3_mech2 import embed, kraus_apply, relax_kraus
from c3_zz import LOC, REGION, T1Q, TCZ, gate, parse

PAULI = [np.eye(2), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1.0, -1.0])]
P1 = [embed_k for embed_k in PAULI]
P2 = [np.kron(a, b) for a in PAULI for b in PAULI]


def depol_apply(rho, p, qs):
    if p <= 0:
        return rho
    ps = P1 if len(qs) == 1 else P2
    d = len(ps)
    out = (1 - p) * rho
    for k in ps[1:]:
        e = embed(k, qs)
        out = out + (p / (d - 1)) * (e @ rho @ e.conj().T)
    return out


def simulate(n, p2, p1_ratio=0.1, T1=None, p_idle=0.0):
    ops = parse(T[n]["cq"])
    rho = np.zeros((32, 32), complex)
    rho[0, 0] = 1
    clock = {q: 0.0 for q in REGION}
    for name, angle, qs in ops:
        start = max(clock[q] for q in qs)
        d = TCZ if name == "CZ" else (0.0 if name == "Rz" else T1Q)
        if T1:
            for q in qs:
                idle = start - clock[q]
                if idle > 0:
                    rho = kraus_apply(rho, relax_kraus(idle, T1), q)
        U = embed(np.diag([1, 1, 1, -1]).astype(complex), qs) if name == "CZ" else embed(gate(name, angle), qs)
        rho = U @ rho @ U.conj().T
        if name == "CZ":
            rho = depol_apply(rho, p2, qs)
        elif name in ("X90", "X"):
            rho = depol_apply(rho, p2 * p1_ratio, qs)
        if T1 and d > 0:
            for q in qs:
                rho = kraus_apply(rho, relax_kraus(d, T1), q)
        for q in qs:
            clock[q] = start + d
    prob = np.real(np.diag(rho)).clip(min=0)
    out = np.zeros(32)
    roles = T[n]["roles"]
    for state in range(32):
        bits = [(state >> (4 - i)) & 1 for i in range(5)]
        j = 0
        for k, key in enumerate(KEYS):
            j |= bits[LOC[roles[key]]] << k
        out[j] += prob[state]
    return out


def chi2(p2, **kw):
    tot = 0.0
    parts = []
    V = []
    for n in NAMES:
        law = simulate(n, p2, **kw)
        Mp = matrix_for(n)
        r, v, _ = ratio_of((Mp @ law) * 1e6, SIGN[n])
        # a residual global contraction rho on top, matched to the observed visibility
        best = None
        for rho in np.linspace(0.3, 1.0, 71):
            rr, vv, _ = ratio_of((Mp @ (rho * law + (1 - rho) / 32)) * 1e6, SIGN[n])
            if best is None or abs(vv - OBS[n]["V"]) < abs(best[1] - OBS[n]["V"]):
                best = (rho, vv, rr)
        c = float((((OBS[n]["r"] - best[2]) / OBS[n]["se"]) ** 2).sum())
        tot += c
        parts.append(c)
        V.append(v)
    return tot, parts, V


if __name__ == "__main__":
    for p2 in (0.0, 0.01, 0.02, 0.03, 0.05, 0.08):
        tot, parts, V = chi2(p2)
        print(
            f"p2 {p2:.2f} (p1 {p2 / 10:.3f}): chi2 {tot:7.1f} (ba {parts[0]:.0f}, bb {parts[1]:.0f}, b0 {parts[2]:.0f}); model V before residual contraction {np.round(V, 3)} (observed {[round(OBS[n]['V'], 3) for n in NAMES]})",
            flush=True,
        )
    for T1 in (12e-6, 25e-6):
        for p2 in (0.02, 0.04):
            tot, parts, V = chi2(p2, T1=T1)
            print(
                f"T1 {T1 * 1e6:.0f} us + p2 {p2:.2f}: chi2 {tot:7.1f} (ba {parts[0]:.0f}, bb {parts[1]:.0f}, b0 {parts[2]:.0f})",
                flush=True,
            )
