"""Replica sub-circuits of the retained IBM ISA circuits, and a small density-matrix simulator with switchable noise."""

import ast
import json
from functools import cache

import numpy as np
from c2_data import ROOT, RUNS
from qiskit import qpy

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1.0, -1.0]).astype(complex)
SX = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])


def rz(t):
    return np.diag([np.exp(-1j * t / 2), np.exp(1j * t / 2)])


def rx(t):
    return np.cos(t / 2) * I2 - 1j * np.sin(t / 2) * X


CZ = np.diag([1, 1, 1, -1]).astype(complex)
ZZ = np.kron(Z, Z)


@cache
def load_circs(run_key):
    with open(ROOT / "results/live" / RUNS[run_key] / "isa.qpy", "rb") as f:
        return qpy.load(f)


@cache
def record(run_key):
    return json.loads((ROOT / "results/live" / RUNS[run_key] / "record.json").read_bytes())


def members(run_key):
    return [m["name"] for m in record(run_key)["groups"][0]["members"]]


def replica_ops(run_key, member, k):
    """[(name, (phys qubits), params)] for replica k of a member in circuit order, and {clbit_index: phys qubit}."""
    rec = record(run_key)
    g = rec["groups"][0]
    mem = next(m for m in g["members"] if m["name"] == member)
    qubits = (
        mem["replica_qubits"][k]
        if not isinstance(mem["replica_qubits"], str)
        else ast.literal_eval(mem["replica_qubits"])[k]
    )
    qset = set(qubits)
    pubs = rec["execution_pubs"]
    idx = next(i for i, p in enumerate(pubs) if p["components"][0]["member"] == member)
    circ = load_circs(run_key)[idx]
    ops, meas = [], {}
    reg = next(r for r in circ.cregs if r.name == f"g0_r{k}_c")
    for inst in circ.data:
        qs = tuple(circ.find_bit(q).index for q in inst.qubits)
        if not set(qs) <= qset:
            continue
        name = inst.operation.name
        if name == "measure":
            cl = reg.index(inst.clbits[0]) if inst.clbits[0] in reg else None
            if cl is None:
                continue
            meas[cl] = qs[0]
        elif name in ("sx", "rz", "cz", "x"):
            ops.append((name, qs, tuple(float(p) for p in inst.operation.params)))
        elif name == "barrier":
            continue
        else:
            raise ValueError(name)
    return ops, meas, sorted(qubits)


def device_params(run_key):
    g = record(run_key)["groups"][0]
    fp = g["calibration_fingerprint"]
    pq = g["placed_qubit_calibration"]
    return fp, pq


class Sim:
    """4-qubit density-matrix simulator of a replica; qubits are the sorted physical qubits mapped to 0..3."""

    def __init__(
        self,
        ops,
        qubits,
        meas,
        fp,
        pq,
        *,
        depol=False,
        thermal=False,
        readout=False,
        eps_sx=0.0,
        delta_cz=0.0,
        zeta=0.0,
        couplers=None,
        scale_t1=1.0,
        scale_err=1.0,
        scale_ro=1.0,
        meas_relax=0.0,
    ):
        self.loc = {q: i for i, q in enumerate(qubits)}
        self.n = len(qubits)
        self.ops, self.meas, self.fp, self.pq = ops, meas, fp, pq
        self.flags = dict(depol=depol, thermal=thermal, readout=readout)
        self.eps_sx, self.delta_cz, self.zeta = eps_sx, delta_cz, zeta
        self.scale_t1 = scale_t1
        self.scale_err, self.scale_ro, self.meas_relax = scale_err, scale_ro, meas_relax
        self.couplers = couplers

    def dur(self, name, qs):
        key = f"target:{name}({qs[0]},):duration" if len(qs) == 1 else f"target:{name}({qs[0]}, {qs[1]}):duration"
        return self.fp.get(key, {"rz": 0.0}.get(name, 0.0))

    def err(self, name, qs):
        key = f"target:{name}({qs[0]},):error" if len(qs) == 1 else f"target:{name}({qs[0]}, {qs[1]}):error"
        return self.fp.get(key, 0.0)

    def apply_u(self, rho, u, qs):
        loc = [self.loc[q] for q in qs]
        full = self.embed(u, loc)
        return full @ rho @ full.conj().T

    def embed(self, u, loc):
        n = self.n
        k = len(loc)
        t = u.reshape([2] * (2 * k))
        out = np.eye(2**n, dtype=complex).reshape([2] * (2 * n))
        # apply by contracting u over the output indices of the identity
        out = np.tensordot(t, out, axes=(list(range(k, 2 * k)), loc))
        out = np.moveaxis(out, list(range(k)), loc)
        return out.reshape(2**n, 2**n)

    def kraus(self, rho, ks, qs):
        loc = [self.loc[q] for q in qs]
        tot = np.zeros_like(rho)
        for kk in ks:
            f = self.embed(kk, loc)
            tot += f @ rho @ f.conj().T
        return tot

    def thermal_kraus(self, q, t):
        p = self.pq[str(q)]
        T1, T2 = p["T1"] * 1e-6 * self.scale_t1, p["T2"] * 1e-6
        T2 = min(T2, 2 * T1)
        g1 = 1 - np.exp(-t / T1)
        # pure dephasing probability
        invTphi = max(1 / T2 - 1 / (2 * T1), 0.0)
        pd = 0.5 * (1 - np.exp(-t * invTphi))
        ad = [np.array([[1, 0], [0, np.sqrt(1 - g1)]]), np.array([[0, np.sqrt(g1)], [0, 0]])]
        dp = [np.sqrt(1 - pd) * I2, np.sqrt(pd) * Z]
        return [a @ b for a in ad for b in dp]

    def run(self):
        n = self.n
        rho = np.zeros((2**n, 2**n), complex)
        rho[0, 0] = 1
        clock = {q: 0.0 for q in self.loc}
        for name, qs, params in self.ops:
            qs = tuple(qs)
            # idle relaxation up to the start time of this gate
            start = max(clock[q] for q in qs)
            if self.flags["thermal"]:
                for q in qs:
                    idle = start - clock[q]
                    if idle > 0:
                        rho = self.kraus(rho, self.thermal_kraus(q, idle), (q,))
            for q in qs:
                clock[q] = start
            d = self.dur(name, qs)
            if name == "rz":
                rho = self.apply_u(rho, rz(params[0]), qs)
                continue
            if name == "sx":
                u = SX @ rx(self.eps_sx) if self.eps_sx else SX
                rho = self.apply_u(rho, u, qs)
            elif name == "x":
                u = X @ rx(self.eps_sx) if self.eps_sx else X
                rho = self.apply_u(rho, u, qs)
            elif name == "cz":
                u = CZ
                if self.delta_cz:
                    u = u @ np.diag(np.exp(-1j * self.delta_cz / 2 * np.array([1, -1, -1, 1])))
                rho = self.apply_u(rho, u, qs)
            if self.zeta and self.couplers and d > 0:
                for a, b in self.couplers:
                    if a in qs or b in qs:
                        rho = self.apply_u(
                            rho, np.diag(np.exp(-1j * self.zeta * d / 2 * np.array([1, -1, -1, 1]))), (a, b)
                        )
            if self.flags["depol"]:
                e = self.err(name, qs) * self.scale_err
                if len(qs) == 1 and e > 0:
                    p = 1.5 * e
                    ks = [np.sqrt(1 - p) * I2] + [np.sqrt(p / 3) * P for P in (X, Y, Z)]
                    rho = self.kraus(rho, ks, qs)
                elif len(qs) == 2 and e > 0:
                    p = 1.25 * e
                    ps = [np.kron(a, b) for a in (I2, X, Y, Z) for b in (I2, X, Y, Z)][1:]
                    ks = [np.sqrt(1 - p) * np.eye(4)] + [np.sqrt(p / 15) * P for P in ps]
                    rho = self.kraus(rho, ks, qs)
            if self.flags["thermal"] and d > 0:
                for q in qs:
                    rho = self.kraus(rho, self.thermal_kraus(q, d), (q,))
            for q in qs:
                clock[q] = start + d
        tmax = max(clock.values())
        if self.flags["thermal"]:
            for q in clock:
                idle = tmax - clock[q] + self.meas_relax * self.fp.get(f"target:measure({q},):duration", 0.0)
                if idle > 0:
                    rho = self.kraus(rho, self.thermal_kraus(q, idle), (q,))
        return rho, tmax

    def probs(self, rho):
        diag = np.real(np.diag(rho)).clip(min=0)
        n = self.n
        # measured clbit i <- qubit meas[i]; outcome index sum bit_i << i
        out = np.zeros(2 ** len(self.meas))
        for state in range(2**n):
            # qubit with local index j holds bit at position (n-1-j) of 'state' (big-endian tensor index)
            j = 0
            for cl, q in self.meas.items():
                b = (state >> (n - 1 - self.loc[q])) & 1
                j |= b << cl
            out[j] += diag[state]
        if self.flags["readout"]:
            for cl, q in self.meas.items():
                p = self.pq[str(q)]
                r01, r10 = p["prob_meas1_prep0"] * self.scale_ro, p["prob_meas0_prep1"] * self.scale_ro
                a = np.array([[1 - r01, r10], [r01, 1 - r10]])
                out = out.reshape([2] * len(self.meas))
                ax = len(self.meas) - 1 - cl
                out = np.moveaxis(np.tensordot(a, out, axes=(1, ax)), 0, ax).reshape(-1)
        return out
