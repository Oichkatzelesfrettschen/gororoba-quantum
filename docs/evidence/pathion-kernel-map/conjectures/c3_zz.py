"""C3 (ii): coherent ZZ on the coupler table's couplers, simulated on the routed cq circuits (state vector over the five
region qubits), then contraction toward uniform, bracket product readout, and the same 24-bin comparison."""

import json
import re

import numpy as np
from c3_corr import NAMES, OBS, SIGN
from c3_data import KEYS, ROOT, T, matrix_for
from scipy.optimize import minimize_scalar

REGION = (2, 4, 8, 11, 12)
LOC = {q: i for i, q in enumerate(REGION)}
ZZ = {
    tuple(e["edge"]): e["zz_shift_hz"]
    for e in json.loads((ROOT / "results/quantum_inspire/coupler_zz_tuna_17_analysis.json").read_bytes())["edges"]
}
EDGES = [(a, b) for (a, b) in ZZ if a in LOC and b in LOC]
T1Q, TCZ = 20e-9, 60e-9


def parse(path):
    ops = []
    for line in path.read_text().splitlines():
        line = line.strip()
        m = re.match(r"(Rz|X90|X|Y90|Y)(?:\(([-\d.e]+)\))? q\[(\d+)\]", line)
        if m:
            ops.append((m.group(1), float(m.group(2)) if m.group(2) else None, (int(m.group(3)),)))
            continue
        m = re.match(r"CZ q\[(\d+)\], q\[(\d+)\]", line)
        if m:
            ops.append(("CZ", None, (int(m.group(1)), int(m.group(2)))))
    return ops


def gate(name, angle):
    s2 = 1 / np.sqrt(2)
    if name == "Rz":
        return np.diag([np.exp(-1j * angle / 2), np.exp(1j * angle / 2)])
    if name == "X90":
        return s2 * np.array([[1, -1j], [-1j, 1]])
    if name == "X":
        return np.array([[0, -1j], [-1j, 0]])
    if name == "Y90":
        return s2 * np.array([[1, -1], [1, 1]])
    raise ValueError(name)


def apply1(psi, u, q):
    psi = np.moveaxis(psi, q, 0)
    psi = np.tensordot(u, psi, axes=(1, 0))
    return np.moveaxis(psi, 0, q)


def apply_zz(psi, a, b, theta):
    """exp(-i theta/2 Z_a Z_b)"""
    idx = np.indices((2,) * 5)
    za, zb = 1 - 2 * idx[a], 1 - 2 * idx[b]
    return psi * np.exp(-1j * theta / 2 * za * zb)


def run(ops, kappa):
    psi = np.zeros((2,) * 5, complex)
    psi[(0,) * 5] = 1
    clock = {q: 0.0 for q in REGION}
    for name, angle, qs in ops:
        start = max(clock[q] for q in qs)
        d = TCZ if name == "CZ" else (0.0 if name == "Rz" else T1Q)
        if name == "CZ":
            la, lb = LOC[qs[0]], LOC[qs[1]]
            idx = np.indices((2,) * 5)
            psi = psi * (1 - 2 * (idx[la] * idx[lb]))
        else:
            psi = apply1(psi, gate(name, angle), LOC[qs[0]])
        for q in qs:
            clock[q] = start + d
    return psi


def run_zz(ops, kappa):
    """Schedule ASAP; apply ZZ of every region edge continuously: before each gate, evolve all edges for the time the
    schedule advanced since the previous gate's start (global time slices)."""
    psi = np.zeros((2,) * 5, complex)
    psi[(0,) * 5] = 1
    clock = {q: 0.0 for q in REGION}
    now = 0.0
    timeline = []
    for name, angle, qs in ops:
        start = max(clock[q] for q in qs)
        d = TCZ if name == "CZ" else (0.0 if name == "Rz" else T1Q)
        timeline.append((start, d, name, angle, qs))
        for q in qs:
            clock[q] = start + d
    timeline.sort(key=lambda x: x[0])
    for start, _duration, name, angle, qs in timeline:
        if kappa and start > now:
            for a, b in EDGES:
                psi = apply_zz(psi, LOC[a], LOC[b], kappa * 2 * np.pi * ZZ[(a, b)] * (start - now))
            now = start
        if name == "CZ":
            idx = np.indices((2,) * 5)
            psi = psi * (1 - 2 * (idx[LOC[qs[0]]] * idx[LOC[qs[1]]]))
        else:
            psi = apply1(psi, gate(name, angle), LOC[qs[0]])
    end = max(clock.values())
    if kappa and end > now:
        for a, b in EDGES:
            psi = apply_zz(psi, LOC[a], LOC[b], kappa * 2 * np.pi * ZZ[(a, b)] * (end - now))
    return psi, end


def law_of(n, kappa):
    ops = parse(T[n]["cq"])
    psi, tend = run_zz(ops, kappa)
    prob = np.abs(psi) ** 2
    out = np.zeros(32)
    roles = T[n]["roles"]
    for state in np.ndindex(*(2,) * 5):
        j = 0
        for k, key in enumerate(KEYS):
            j |= state[LOC[roles[key]]] << k
        out[j] += prob[state]
    return out, tend


def chi2(kappa):
    tot = 0.0
    for n in NAMES:
        law, _ = law_of(n, kappa)
        Mp = matrix_for(n)
        best = None
        for rho in np.linspace(0.25, 1.0, 76):
            mixed = Mp @ (rho * law + (1 - rho) / 32)
            from c3_data import ratio_of

            r, V, _ = ratio_of(mixed * 1e6, SIGN[n])
            if best is None or abs(V - OBS[n]["V"]) < abs(best[1] - OBS[n]["V"]):
                best = (rho, V, r)
        tot += float((((OBS[n]["r"] - best[2]) / OBS[n]["se"]) ** 2).sum())
    return tot


if __name__ == "__main__":
    for n in NAMES:
        law, tend = law_of(n, 0.0)
        print(
            f"{n}: ideal TVD to the case's ideal {0.5 * np.abs(law - T[n]['ideal']).sum():.2e}; scheduled duration {tend * 1e6:.2f} us; edges {EDGES}"
        )
    print("coupler table edges used (Hz):", {e: round(ZZ[e]) for e in EDGES})
    for kappa in (0, 1, 3, 10, 30, -1, -3, -10, -30):
        print(f"kappa {kappa:+4d} (table ZZ x kappa, gate times 20/60 ns): chi2 {chi2(kappa):8.1f}")
    best = minimize_scalar(chi2, bounds=(-60, 60), method="bounded", options={"xatol": 0.05})
    print(f"best kappa {best.x:+.2f}: chi2 {best.fun:.1f}")
