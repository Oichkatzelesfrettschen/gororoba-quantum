"""C2 (d): residual of N_hat from the ideal nullity for every coset block, measured against the readout-only and the
calibrated incoherent predictions, on the 17 Fez replicas (replica-matched)."""

import importlib
import json
import sys
from pathlib import Path

import numpy as np
from c2_circuits import Sim, device_params, record, replica_ops
from c2_data import load_ibm
from scipy import stats

from parallel import ordered_map

pcb = importlib.import_module("pathion_coset_block")

HERE = Path(__file__).resolve().parent

RUN = sys.argv[1] if len(sys.argv) > 1 else "fez"
rec = record(RUN)
G = rec["groups"][0]
FP, PQ = device_params(RUN)
MEM = {m["name"]: m for m in G["members"]}
CNT, _ = load_ibm(RUN)
blocks = sorted({n.rsplit("_", 1)[0] for n in MEM if n.endswith("_plus")})
NREP = CNT[blocks[0] + "_plus"].shape[0]


def nh(plus, minus, ip, im):
    c = pcb.output_contrast(plus, minus)
    ci = pcb.output_contrast(ip, im)
    dec = np.abs(ci) > 1e-9
    V = np.mean(c[dec] * np.sign(ci[dec]))
    return c.sum() / 2 / V, V


def sim(task):
    blk, k, cfg = task
    out = {}
    for arm in ("plus", "minus"):
        ops, meas, qubits = replica_ops(RUN, f"{blk}_{arm}", k)
        edges = [(a, b) for a in qubits for b in qubits if a < b and f"target:cz({a}, {b}):duration" in FP]
        s = Sim(ops, qubits, meas, FP, PQ, couplers=edges, **cfg)
        rho, _ = s.run()
        out[arm] = s.probs(rho)
    ip = np.array(MEM[f"{blk}_plus"]["ideal"], float)
    im = np.array(MEM[f"{blk}_minus"]["ideal"], float)
    return nh(out["plus"], out["minus"], ip, im)[0]


def main():
    cfgs = {"readout": dict(readout=True), "incoherent": dict(readout=True, depol=True, thermal=True)}
    tasks = [(b, k, cfgs[c]) for b in blocks for k in range(NREP) for c in ("readout", "incoherent")]
    res = ordered_map(sim, tasks, min_items=1)
    it = iter(res)
    table = {}
    for b in blocks:
        ro, inc, meas_ = [], [], []
        for k in range(NREP):
            ro.append(next(it))
            inc.append(next(it))
            ip = np.array(MEM[f"{b}_plus"]["ideal"], float)
            im = np.array(MEM[f"{b}_minus"]["ideal"], float)
            meas_.append(nh(CNT[f"{b}_plus"][k], CNT[f"{b}_minus"][k], ip, im)[0])
        ni = float(
            np.sum(
                pcb.output_contrast(
                    np.array(MEM[f"{b}_plus"]["ideal"], float), np.array(MEM[f"{b}_minus"]["ideal"], float)
                )
            )
            / 2
        )
        table[b] = dict(
            ideal=ni,
            cz=MEM[f"{b}_plus"]["cz"],
            meas=np.mean(meas_),
            meas_se=np.std(meas_, ddof=1) / np.sqrt(NREP),
            readout=np.mean(ro),
            incoh=np.mean(inc),
        )
    print(f"run {RUN}: {len(blocks)} blocks, {NREP} replicas")
    print(f"{'block':24s} ideal cz   measured-ideal (se)    readout-only  incoherent   measured-incoherent")
    for b, t in table.items():
        print(
            f"{b:24s} {t['ideal']:+.0f}   {t['cz']:2d}   {t['meas'] - t['ideal']:+.4f} ({t['meas_se']:.4f})   {t['readout'] - t['ideal']:+.4f}   {t['incoh'] - t['ideal']:+.4f}    {t['meas'] - t['incoh']:+.4f}"
        )
    nz = [b for b, t in table.items() if abs(t["ideal"]) < 0.5]
    zz = [b for b, t in table.items() if abs(t["ideal"]) >= 0.5]
    for lab, group in (("ideal-zero blocks", nz), ("nonzero-nullity blocks", zz)):
        if not group:
            continue
        r = np.array([table[b]["meas"] - table[b]["ideal"] for b in group])
        p = np.array([table[b]["incoh"] - table[b]["ideal"] for b in group])
        pr = np.array([table[b]["readout"] - table[b]["ideal"] for b in group])
        se = np.array([table[b]["meas_se"] for b in group])
        d = r - p
        print(
            f"{lab} (n {len(group)}): mean measured residual {r.mean():+.4f}; mean incoherent prediction {p.mean():+.4f}; mean (measured - prediction) {d.mean():+.4f} +- {np.sqrt((se**2).sum()) / len(se):.4f}; corr(measured, prediction) {np.corrcoef(r, p)[0, 1]:+.2f}; readout-only mean {pr.mean():+.4f}"
        )
    cz = np.array([table[b]["cz"] for b in table])
    res_ = np.array([table[b]["meas"] - table[b]["ideal"] for b in table])
    pr_ = np.array([table[b]["incoh"] - table[b]["ideal"] for b in table])
    print(
        f"over all blocks: spearman(residual, cz) {stats.spearmanr(cz, res_).statistic:+.2f}; spearman(measured - prediction, cz) {stats.spearmanr(cz, res_ - pr_).statistic:+.2f}"
    )
    json.dump(table, open(HERE / f"c2_resid_{RUN}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
