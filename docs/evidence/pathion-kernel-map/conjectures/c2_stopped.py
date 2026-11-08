"""C2 replication test: the coin-free stopped series (separate plus and minus circuits, arms differ by one virtual Rz) under a
coherent X90/X over-rotation and under the incoherent mechanisms, with the series' own readout assignment."""

import importlib
import json
import re

import numpy as np
from c2_data import ROOT

cc = importlib.import_module("qi_pathion_coset_coin_cases")
pcb = importlib.import_module("pathion_coset_block")

D = ROOT / "results/quantum_inspire/runs/2026-11-06T221626Z-pathion_coset_block_tuna_17-batch-02"
case = json.loads((D / "cases.json").read_bytes())
roles = case["templates"]["b0"]["roles"]
KEYS4 = ("d0", "d1", "d2", "selector")
REGION = tuple(sorted(set(roles.values())))
LOC = {q: i for i, q in enumerate(REGION)}
N = len(REGION)
ZZT = {
    tuple(e["edge"]): e["zz_shift_hz"]
    for e in json.loads((ROOT / "results/quantum_inspire/coupler_zz_tuna_17_analysis.json").read_bytes())["edges"]
}
T1Q, TCZ = 20e-9, 60e-9
S2 = 1 / np.sqrt(2)


def parse(path):
    ops = []
    for line in path.read_text().splitlines():
        m = re.match(r"(Rz|X90|X)(?:\(([-\d.e]+)\))? q\[(\d+)\]", line.strip())
        if m:
            ops.append((m.group(1), float(m.group(2)) if m.group(2) else None, (int(m.group(3)),)))
        m = re.match(r"CZ q\[(\d+)\], q\[(\d+)\]", line.strip())
        if m:
            ops.append(("CZ", None, (int(m.group(1)), int(m.group(2)))))
    return ops


def gate(name, a, eps):
    if name == "Rz":
        return np.diag([np.exp(-1j * a / 2), np.exp(1j * a / 2)])
    th = (np.pi / 2 if name == "X90" else np.pi) + eps
    return np.array([[np.cos(th / 2), -1j * np.sin(th / 2)], [-1j * np.sin(th / 2), np.cos(th / 2)]])


def embed(u, qs):
    k = len(qs)
    loc = [LOC[q] for q in qs]
    t = u.reshape([2] * (2 * k))
    out = np.eye(2**N, dtype=complex).reshape([2] * (2 * N))
    out = np.tensordot(t, out, axes=(list(range(k, 2 * k)), loc))
    return np.moveaxis(out, list(range(k)), loc).reshape(2**N, 2**N)


def relax(rho, q, t, T1):
    g = 1 - np.exp(-t / T1)
    ks = [np.array([[1, 0], [0, np.sqrt(1 - g)]]), np.array([[0, np.sqrt(g)], [0, 0]])]
    return sum(embed(k, (q,)) @ rho @ embed(k, (q,)).conj().T for k in ks)


def law(arm, eps=0.0, dcz=0.0, T1=None, p2=0.0):
    ops = parse(D / f"b0-{arm}-r0.cq")
    rho = np.zeros((2**N, 2**N), complex)
    rho[0, 0] = 1
    clock = {q: 0.0 for q in REGION}
    P1 = [np.eye(2), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1.0, -1.0])]
    P2 = [np.kron(a, b) for a in P1 for b in P1]
    for name, a, qs in ops:
        start = max(clock[q] for q in qs)
        d = TCZ if name == "CZ" else (0.0 if name == "Rz" else T1Q)
        if T1:
            for q in qs:
                if start - clock[q] > 0:
                    rho = relax(rho, q, start - clock[q], T1)
        if name == "CZ":
            u = np.diag([1, 1, 1, -1]).astype(complex)
            if dcz:
                u = u @ np.diag(np.exp(-1j * dcz / 2 * np.array([1, -1, -1, 1])))
        else:
            u = gate(name, a, eps if name in ("X90", "X") else 0.0)
        U = embed(u, qs)
        rho = U @ rho @ U.conj().T
        if p2 and name in ("CZ", "X90", "X"):
            p = p2 if name == "CZ" else p2 / 10
            ps = P2 if name == "CZ" else P1
            out = (1 - p) * rho
            for k in ps[1:]:
                e = embed(k, qs)
                out = out + p / (len(ps) - 1) * (e @ rho @ e.conj().T)
            rho = out
        if T1 and d > 0:
            for q in qs:
                rho = relax(rho, q, d, T1)
        for q in qs:
            clock[q] = start + d
    prob = np.real(np.diag(rho)).clip(min=0)
    out = np.zeros(16)
    for s in range(2**N):
        bits = [(s >> (N - 1 - i)) & 1 for i in range(N)]
        j = sum(bits[LOC[roles[k]]] << v for v, k in enumerate(KEYS4))
        out[j] += prob[s]
    return out


def readout():
    asg = cc.retained_readout(REGION)
    M = np.array([[1.0]])
    # bit v is the v-th kron factor from the right
    for v in range(4):
        q = roles[KEYS4[v]]
        e01, e10 = asg[q]
        M = np.kron(np.array([[1 - e01, e10], [e01, 1 - e10]]), M)
    return M


def stats(plus, minus, sign):
    a, b = plus / plus.sum(), minus / minus.sum()
    c = pcb.output_contrast(a, b)
    V = float(np.mean(c * sign))
    return V, float(a[:8].sum() - b[:8].sum()), c.sum() / 2 / V


if __name__ == "__main__":
    sign = np.sign(np.array(case["templates"]["b0"]["ideal_c"]))
    M = readout()
    ideal = {a: law(a) for a in ("plus", "minus")}
    print(
        "ideal selector contrast of the routed stopped-series arms:", ideal["plus"][:8].sum() - ideal["minus"][:8].sum()
    )
    print("observed (stopped series, raw): selector contrast +0.0167 +- 0.0055, N_hat +0.152 +- 0.042, V 0.483")
    rows: tuple[tuple[str, dict[str, float]], ...] = (
        ("readout only", {}),
        ("X90/X over-rotation +0.029 rad", dict(eps=0.029)),
        ("X90/X over-rotation -0.029 rad", dict(eps=-0.029)),
        ("CZ phase +0.06 rad", dict(dcz=0.06)),
        ("CZ phase -0.06 rad", dict(dcz=-0.06)),
        ("T1 25 us", dict(T1=25e-6)),
        ("T1 12 us", dict(T1=12e-6)),
        ("gate depolarizing p2 0.03", dict(p2=0.03)),
    )
    for lab, kw in rows:
        pl, mi = M @ law("plus", **kw), M @ law("minus", **kw)
        V, sel, Nh = stats(pl, mi, sign)
        print(f"{lab:36s} V {V:.3f} selector contrast {sel:+.4f} N_hat {Nh:+.4f}")
