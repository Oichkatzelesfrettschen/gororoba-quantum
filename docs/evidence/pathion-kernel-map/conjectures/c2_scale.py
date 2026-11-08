"""C2 (a) and (d): Tuna and IBM null-block offsets on one scale; residuals of every operand against its ideal nullity."""

import importlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from c2_data import ROOT, RUNS, load_ibm

pcs = importlib.import_module("qi_pathion_coset_block_series")
cc = importlib.import_module("qi_pathion_coset_coin_cases")
pca = importlib.import_module("pathion_coset_analysis")
pcb = importlib.import_module("pathion_coset_block")

HERE = Path(__file__).resolve().parent

# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 9
rng = np.random.default_rng(15053)


def nhat_arms(plus, minus, sign):
    """N_hat from two 16-outcome count piles with the repo's c(y) and signed visibility."""
    c = pcb.output_contrast(plus / plus.sum(), minus / minus.sum())
    dec = np.abs(sign) > 0
    V = float(np.mean(c[dec] * sign[dec]))
    return c.sum() / 2 / V, c.sum() / 2, V, float(plus[:8].sum() / plus.sum() - minus[:8].sum() / minus.sum())


def boot(plus, minus, sign, B=2000):
    out = []
    for _ in range(B):
        p = rng.multinomial(int(plus.sum()), plus / plus.sum()).astype(float)
        m = rng.multinomial(int(minus.sum()), minus / minus.sum()).astype(float)
        out.append(nhat_arms(p, m, sign)[:2])
    out = np.array(out)
    return out.std(0)


print("=== IBM measured (collect.json measured_statistics; replica mean, replica spread se) ===")
ibm = {}
for key, run in (("fez", RUNS["fez"]), ("marrakesh", RUNS["marrakesh"])):
    coll = json.loads((ROOT / f"results/live/{run}/collect.json").read_bytes())[1]
    ms = coll["measured_statistics"]
    cnt, rec = load_ibm(key)
    g = rec["groups"][0]
    ideal = {m["name"]: np.array(m["ideal"], float) for m in g["members"]}
    for blk in ("k0", "k4", "k8", "k12"):
        per: Any = []
        for k in range(cnt[f"cmap_e1pe17_{blk}_plus"].shape[0]):
            ci = pcb.output_contrast(ideal[f"cmap_e1pe17_{blk}_plus"], ideal[f"cmap_e1pe17_{blk}_minus"])
            per.append(
                nhat_arms(
                    cnt[f"cmap_e1pe17_{blk}_plus"][k],
                    cnt[f"cmap_e1pe17_{blk}_minus"][k],
                    np.sign(np.where(abs(ci) > 1e-9, ci, 0)),
                )
            )
        per = np.array(per)
        mean, se_rep = per[:, 0].mean(), per[:, 0].std(ddof=1) / np.sqrt(len(per))
        hs = per[:, 1].mean()
        hs_se = per[:, 1].std(ddof=1) / np.sqrt(len(per))
        ibm[(key, blk)] = dict(
            N=mean,
            se=se_rep,
            hs=hs,
            hs_se=hs_se,
            V=per[:, 2].mean(),
            sel=per[:, 3].mean(),
            sel_se=per[:, 3].std(ddof=1) / np.sqrt(len(per)),
            reps=len(per),
            repo=ms["summary"][f"cmap_e1pe17_{blk}_nullity_estimate"],
            per=per[:, 0],
        )
        print(
            f"{key:9s} {blk:3s} N_hat {mean:+.4f} +- {se_rep:.4f} (repo summary {ibm[(key, blk)]['repo']:+.4f}); half-sum {hs:+.4f} +- {hs_se:.4f}; V {per[:, 2].mean():.3f}; selector contrast {per[:, 3].mean():+.4f} +- {ibm[(key, blk)]['sel_se']:.4f}; replicas {len(per)}; replicas > 0: {(per[:, 0] > 0).sum()}"
        )
    tot = sum(ibm[(key, b)]["N"] for b in ("k0", "k4", "k8", "k12"))
    tse = np.sqrt(sum(ibm[(key, b)]["se"] ** 2 for b in ("k0", "k4", "k8", "k12")))
    print(f"{key:9s} operand sum N_hat {tot:+.4f} +- {tse:.4f}")
    cor = coll["measured_summary_readout_corrected"]
    print(
        f"{key:9s} readout-corrected blocks (repo): "
        + ", ".join(f"{b} {cor[f'cmap_e1pe17_{b}_nullity_estimate']:+.4f}" for b in ("k0", "k4", "k8", "k12"))
    )

print("\n=== Tuna coin series (coin-resolved arms, b0 = IBM block k0 of e1+e17: basis 16,1,2) ===")
case = json.loads((ROOT / "results/quantum_inspire/cases/pathion_coset_coin_tuna_17/batch-02/cases.json").read_bytes())
roles = case["templates"]["b0"]["roles"]
shots = json.loads(
    (
        ROOT / "results/quantum_inspire/runs/2026-11-07T001031Z-pathion_coset_coin_tuna_17-batch-02/raw/b0.cq.json"
    ).read_bytes()
)
cn = cc.coin_counts(shots, roles)
plus, minus = cn[16:], cn[:16]
ideal_c = np.array(case["templates"]["b0"]["ideal_c"])
sign = np.sign(ideal_c)
n, hs, V, sel = nhat_arms(plus, minus, sign)
sd = boot(plus, minus, sign)
print(
    f"Tuna b0 raw: N_hat {n:+.4f} +- {sd[0]:.4f}; half-sum {hs:+.4f} +- {sd[1]:.4f}; V {V:.3f}; selector contrast {sel:+.4f}; arms shots {int(plus.sum())}/{int(minus.sum())}"
)
# readout corrected with the series' own brackets
an = json.loads((ROOT / "results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json").read_bytes())
print(
    "Tuna analysis b0 visibility",
    an["templates"]["b0"]["visibility"],
    "selector",
    an["templates"]["b0"]["selector_contrast"],
    "+-",
    an["templates"]["b0"]["selector_se"],
    "readout-corrected visibility",
    an["templates"]["b0"]["visibility_readout_corrected"],
)
print("raw selector contrast = sum c /8:", hs * 2 / 8)
# stopped series b0
STOP = pcs.ROOT if hasattr(pcs, "ROOT") else None
sp = cc.stopped_path
cases_s = json.loads(sp("batch-02/cases.json").read_text())
roles_s = cases_s["templates"]["b0"]["roles"]
pl = pca.outcome_counts(json.loads(sp("batch-02/raw/b0-plus-r0.cq.json").read_text()), roles_s)
mi = pca.outcome_counts(json.loads(sp("batch-02/raw/b0-minus-r0.cq.json").read_text()), roles_s)
ic_s = np.array(cases_s["templates"]["b0"]["ideal_c"])
sg_s = np.sign(ic_s)
ns, hss, Vs, sels = nhat_arms(pl, mi, sg_s)
sds = boot(pl, mi, sg_s)
print(
    f"Tuna stopped (coin-free, plus then minus circuits) b0 raw: N_hat {ns:+.4f} +- {sds[0]:.4f}; half-sum {hss:+.4f} +- {sds[1]:.4f}; V {Vs:.3f}; selector contrast {sels:+.4f}; shots {int(pl.sum())}/{int(mi.sum())}"
)
np.savez(
    HERE / "c2_scale.npz",
    tuna_N=n,
    tuna_se=sd[0],
    tuna_hs=hs,
    tuna_hs_se=sd[1],
    stop_N=ns,
    stop_se=sds[0],
    stop_hs=hss,
    stop_hs_se=sds[1],
    **{f"ibm_{k[0]}_{k[1]}_N": v["N"] for k, v in ibm.items()},
    **{f"ibm_{k[0]}_{k[1]}_se": v["se"] for k, v in ibm.items()},
    **{f"ibm_{k[0]}_{k[1]}_hs": v["hs"] for k, v in ibm.items()},
    **{f"ibm_{k[0]}_{k[1]}_hs_se": v["hs_se"] for k, v in ibm.items()},
)
k0f, k0m = ibm[("fez", "k0")], ibm[("marrakesh", "k0")]
for lab, a, b, sa, sb in (
    ("Tuna coin vs IBM Fez k0", n, k0f["N"], sd[0], k0f["se"]),
    ("Tuna coin vs IBM Marrakesh k0", n, k0m["N"], sd[0], k0m["se"]),
    ("Tuna stopped vs IBM Fez k0", ns, k0f["N"], sds[0], k0f["se"]),
    ("Tuna coin vs Tuna stopped", n, ns, sd[0], sds[0]),
):
    print(f"{lab}: difference {a - b:+.4f} +- {np.hypot(sa, sb):.4f} (z {(a - b) / np.hypot(sa, sb):+.1f})")
print(
    "half-sum scale:",
    f"Tuna coin {hs:+.4f}+-{sd[1]:.4f}; stopped {hss:+.4f}+-{sds[1]:.4f}; Fez k0 {k0f['hs']:+.4f}+-{k0f['hs_se']:.4f}; Marrakesh k0 {k0m['hs']:+.4f}+-{k0m['hs_se']:.4f}",
)
