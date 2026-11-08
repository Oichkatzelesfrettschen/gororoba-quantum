"""C2 (b), (c): estimator algebra and mechanism simulations on the actual Fez replica circuits of the null operand e1+e17."""

import importlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from c2_circuits import Sim, device_params, record, replica_ops
from c2_data import load_ibm

from parallel import ordered_map

pcb = importlib.import_module("pathion_coset_block")

HERE = Path(__file__).resolve().parent

RUN = "fez"
BLOCKS = ("k0", "k4", "k8", "k12")
REP = 17
rec = record(RUN)
G = rec["groups"][0]
FP, PQ = device_params(RUN)
MEM = {m["name"]: m for m in G["members"]}
IDEAL = {n: np.array(m["ideal"], float) for n, m in MEM.items()}
CNT, _ = load_ibm(RUN)
COUP: dict[Any, Any] = {}
OPS: dict[Any, Any] = {}


def edges(qubits):
    return [(a, b) for a in qubits for b in qubits if a < b and f"target:cz({a}, {b}):duration" in FP]


def get_ops(member, k):
    key = (member, k)
    if key not in OPS:
        OPS[key] = replica_ops(RUN, member, k)
    return OPS[key]


def nhat(plus, minus, ideal_plus, ideal_minus):
    c = pcb.output_contrast(plus, minus)
    ci = pcb.output_contrast(ideal_plus, ideal_minus)
    dec = np.abs(ci) > 1e-9
    V = np.mean(c[dec] * np.sign(ci[dec]))
    return c.sum() / 2 / V, c.sum() / 2, V


def simulate(task):
    cfg, blk, k = task
    laws = {}
    for arm in ("plus", "minus"):
        name = f"cmap_e1pe17_{blk}_{arm}"
        ops, meas, qubits = get_ops(name, k)
        s = Sim(ops, qubits, meas, FP, PQ, couplers=edges(qubits), **cfg)
        rho, _ = s.run()
        laws[arm] = s.probs(rho)
    ip, im = IDEAL[f"cmap_e1pe17_{blk}_plus"], IDEAL[f"cmap_e1pe17_{blk}_minus"]
    n, hs, V = nhat(laws["plus"], laws["minus"], ip, im)
    tvd = 0.5 * (0.5 * abs(laws["plus"] - ip).sum() + 0.5 * abs(laws["minus"] - im).sum())
    sel = laws["plus"][:8].sum() - laws["minus"][:8].sum()
    return dict(N=n, hs=hs, V=V, tvd=tvd, sel=sel)


def run_cfg(name, cfg, blocks=BLOCKS, reps=range(REP)):
    tasks = [(cfg, b, k) for b in blocks for k in reps]
    res = ordered_map(simulate, tasks, min_items=1)
    out = {}
    for b in blocks:
        r = [x for x, t in zip(res, tasks, strict=True) if t[1] == b]
        out[b] = {key: float(np.mean([x[key] for x in r])) for key in ("N", "hs", "V", "tvd", "sel")}
    return out


def observed_tvd():
    out = {}
    for b in BLOCKS:
        v = []
        for arm in ("plus", "minus"):
            c = CNT[f"cmap_e1pe17_{b}_{arm}"]
            v.append(np.mean([0.5 * abs(r / r.sum() - IDEAL[f"cmap_e1pe17_{b}_{arm}"]).sum() for r in c]))
        out[b] = float(np.mean(v))
    return out


def main():
    # ---- (b) estimator algebra on the ideal laws: marginals, readout maps
    print("== (b) estimator algebra on the ideal null laws ==")
    for b in BLOCKS:
        ip, im = IDEAL[f"cmap_e1pe17_{b}_plus"], IDEAL[f"cmap_e1pe17_{b}_minus"]
        mp, mm = ip[:8] + ip[8:], im[:8] + im[8:]
        print(
            f"{b}: y-marginal plus {np.round(mp[:4], 4)}.. minus {np.round(mm[:4], 4)}; max |P+(y)-P-(y)| {abs(mp - mm).max():.2e}; ideal selector contrast {ip[:8].sum() - im[:8].sum():+.1e}; sum c {pcb.output_contrast(ip, im).sum():+.1e}"
        )
    # QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 8
    rng = np.random.default_rng(54666)
    worst_product = 0.0
    worst_corr = 0.0
    worst_sel_corr = 0.0
    ip, im = IDEAL["cmap_e1pe17_k0_plus"], IDEAL["cmap_e1pe17_k0_minus"]
    for _ in range(2000):
        # product-form asymmetric readout, per-qubit (e01, e10) up to 10 percent
        M = np.array([[1.0]])
        for _q in range(4):
            e01, e10 = rng.uniform(0, 0.1, 2)
            M = np.kron(np.array([[1 - e01, e10], [e01, 1 - e10]]), M)  # qubit q is bit q: little-endian kron order
        p, m = M @ ip, M @ im
        worst_product = max(worst_product, abs(pcb.output_contrast(p, m).sum()), abs(p[:8].sum() - m[:8].sum()))
        # correlated readout: a random column-stochastic matrix close to identity
        R = np.eye(16) * 0.9 + rng.dirichlet(np.ones(16), size=16).T * 0.1
        p2, m2 = R @ ip, R @ im
        worst_corr = max(worst_corr, abs(pcb.output_contrast(p2, m2).sum()))
        worst_sel_corr = max(worst_sel_corr, abs(p2[:8].sum() - m2[:8].sum()))
    print(
        f"arm-symmetric PRODUCT-form readout (per-qubit asymmetric flips up to 0.1): max |sum c| and |selector contrast| over 2000 draws = {worst_product:.2e}"
    )
    print(
        f"arm-symmetric CORRELATED readout (random stochastic mixing 10 percent): max |sum c| = {worst_corr:.3f}, max |selector contrast| = {worst_sel_corr:.3f}"
    )
    # ---- shot-noise bias of the ratio estimator at the observed shots, on the ideal law and on a contracted law
    for lab, contr in (("ideal law", 1.0), ("law contracted to V=0.9", 0.9), ("law contracted to V=0.75", 0.75)):
        vals = []
        for _ in range(4000):
            law_p = contr * ip + (1 - contr) / 16
            law_m = contr * im + (1 - contr) / 16
            p = rng.multinomial(8192, law_p).astype(float)
            m = rng.multinomial(8192, law_m).astype(float)
            vals.append(nhat(p / p.sum(), m / m.sum(), ip, im)[0])
        print(
            f"finite-sample bias of N_hat at 8192 shots per arm, {lab}: mean {np.mean(vals):+.5f} +- {np.std(vals) / np.sqrt(len(vals)):.5f} (sd of one replica {np.std(vals):.4f})"
        )
    # ---- (c) mechanisms
    obs = observed_tvd()
    print("observed mean TVD to ideal per block:", {b: round(v, 3) for b, v in obs.items()})
    configs = {
        "readout only (calibrated)": dict(readout=True),
        "gate depolarizing only (calibrated)": dict(depol=True),
        "T1/T2 relaxation, gates only (calibrated)": dict(thermal=True),
        "T1/T2 incl. measurement time": dict(thermal=True, meas_relax=1.0),
        "all calibrated incoherent (readout+depol+T1)": dict(readout=True, depol=True, thermal=True),
        "all calibrated incoherent + measurement-time T1": dict(readout=True, depol=True, thermal=True, meas_relax=1.0),
        "sx over-rotation +0.03 rad": dict(eps_sx=0.03),
        "sx over-rotation -0.03 rad": dict(eps_sx=-0.03),
        "CZ phase error +0.05 rad": dict(delta_cz=0.05),
        "CZ phase error -0.05 rad": dict(delta_cz=-0.05),
        "ZZ crosstalk zeta +1 MHz*2pi (phase rate 6.3e6 rad/s)": dict(zeta=6.3e6),
        "ZZ crosstalk zeta -1 MHz*2pi": dict(zeta=-6.3e6),
        "ZZ crosstalk zeta +5 MHz*2pi": dict(zeta=3.1e7),
    }
    print(
        "\n== (c) mechanism predictions on the Fez replica circuits (17 replicas per block; mean of per-replica N_hat) =="
    )
    print(f"{'mechanism':58s} " + "  ".join(f"{b:>22s}" for b in BLOCKS))
    rows = {}
    for name, cfg in configs.items():
        r = run_cfg(name, cfg)
        rows[name] = r
        print(f"{name:58s} " + "  ".join(f"N {r[b]['N']:+.4f} TVD {r[b]['tvd']:.3f}" for b in BLOCKS), flush=True)
    json.dump({"observed_tvd": obs, "rows": rows}, open(HERE / "c2_mech.json", "w"), indent=1)


if __name__ == "__main__":
    main()
