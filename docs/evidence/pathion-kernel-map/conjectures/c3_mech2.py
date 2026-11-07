"""C3 further mechanisms on the routed circuits: X90/X over-rotation, CZ conditional-phase error, T1 relaxation with T2 = T1
(amplitude damping plus dephasing), each followed by contraction toward uniform, bracket readout and the 24-bin comparison."""

import numpy as np
from c3_corr import NAMES, OBS, SIGN
from c3_data import KEYS, T, matrix_for, ratio_of
from c3_zz import LOC, REGION, T1Q, TCZ, gate, parse

I2 = np.eye(2)


def embed(u, qs):
    k = len(qs)
    n = 5
    t = u.reshape([2] * (2 * k))
    out = np.eye(2**n, dtype=complex).reshape([2] * (2 * n))
    loc = [LOC[q] for q in qs]
    out = np.tensordot(t, out, axes=(list(range(k, 2 * k)), loc))
    out = np.moveaxis(out, list(range(k)), loc)
    return out.reshape(2**n, 2**n)


def kraus_apply(rho, ks, q):
    return sum(embed(k, (q,)) @ rho @ embed(k, (q,)).conj().T for k in ks)


def relax_kraus(t, T1):
    g = 1 - np.exp(-t / T1)
    # T2 = 2 T1: no pure dephasing
    ad = [np.array([[1, 0], [0, np.sqrt(1 - g)]]), np.array([[0, np.sqrt(g)], [0, 0]])]
    return ad


def simulate(n, eps=0.0, dcz=0.0, T1=None, t2_ratio=None):
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
        if name == "CZ":
            u = np.diag([1, 1, 1, -1]).astype(complex)
            if dcz:
                u = u @ np.diag(np.exp(-1j * dcz / 2 * np.array([1, -1, -1, 1])))
            U = embed(u, qs)
        else:
            g = gate(name, angle)
            if eps and name in ("X90", "X"):
                g = g @ np.array([[np.cos(eps / 2), -1j * np.sin(eps / 2)], [-1j * np.sin(eps / 2), np.cos(eps / 2)]])
            U = embed(g, qs)
        rho = U @ rho @ U.conj().T
        if T1 and d > 0:
            for q in qs:
                rho = kraus_apply(rho, relax_kraus(d, T1), q)
        for q in qs:
            clock[q] = start + d
    end = max(clock.values())
    if T1:
        for q in REGION:
            if end - clock[q] > 0:
                rho = kraus_apply(rho, relax_kraus(end - clock[q], T1), q)
    prob = np.real(np.diag(rho)).clip(min=0)
    out = np.zeros(32)
    roles = T[n]["roles"]
    for state in range(32):
        bits = [
            (state >> (4 - i)) & 1 for i in range(5)
        ]  # tensor order: qubit region index i is the (4-i)th bit of the flat index
        j = 0
        for k, key in enumerate(KEYS):
            j |= bits[LOC[roles[key]]] << k
        out[j] += prob[state]
    return out


def chi2(**kw):
    tot = 0.0
    parts = []
    for n in NAMES:
        law = simulate(n, **kw)
        Mp = matrix_for(n)
        best = None
        for rho in np.linspace(0.2, 1.0, 81):
            r, V, _ = ratio_of((Mp @ (rho * law + (1 - rho) / 32)) * 1e6, SIGN[n])
            if best is None or abs(V - OBS[n]["V"]) < abs(best[1] - OBS[n]["V"]):
                best = (rho, V, r)
        c = float((((OBS[n]["r"] - best[2]) / OBS[n]["se"]) ** 2).sum())
        tot += c
        parts.append(c)
    return tot, parts


if __name__ == "__main__":
    t0, _ = chi2()
    print(f"sanity: noiseless simulation reproduces baseline chi2 {t0:.1f}")
    for lab, key, vals in (
        ("X90/X over-rotation (rad)", "eps", (0.03, 0.06, 0.12, -0.03, -0.06, -0.12)),
        ("CZ conditional-phase error (rad)", "dcz", (0.03, 0.06, 0.12, -0.03, -0.06, -0.12)),
        ("T1 relaxation, T2 = 2 T1 (us)", "T1", (1e-6 * v for v in (3, 6, 12, 25, 50, 100))),
    ):
        for v in vals:
            tot, parts = chi2(**{key: v})
            print(
                f"{lab:36s} {v:+.2e}: chi2 {tot:7.1f} (ba {parts[0]:.0f}, bb {parts[1]:.0f}, b0 {parts[2]:.0f})",
                flush=True,
            )
