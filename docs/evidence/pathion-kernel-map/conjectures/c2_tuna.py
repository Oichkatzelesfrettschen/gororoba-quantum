"""C2: Tuna b0 estimator offset under the retained readout brackets alone (product-form, asymmetric) and after correction."""

import importlib
import json
from typing import Any

import numpy as np
from c2_data import ROOT

cc = importlib.import_module("qi_pathion_coset_coin_cases")
pcb = importlib.import_module("pathion_coset_block")

an = json.loads((ROOT / "results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json").read_bytes())
case = json.loads((ROOT / "results/quantum_inspire/cases/pathion_coset_coin_tuna_17/batch-02/cases.json").read_bytes())
t = case["templates"]["b0"]
roles = t["roles"]
brk = {int(q): tuple(v) for q, v in an["drift_covariate"]["brackets"]["batch-02"].items()}
print(
    "b0 roles", roles, "bracket (e01, e10) per qubit:", {q: tuple(round(x, 4) for x in brk[q]) for q in roles.values()}
)
shots = json.loads(
    (
        ROOT / "results/quantum_inspire/runs/2026-11-07T001031Z-pathion_coset_coin_tuna_17-batch-02/raw/b0.cq.json"
    ).read_bytes()
)
cn = cc.coin_counts(shots, roles)
M = cc.readout_matrix(brk, roles)
sign = np.sign(np.array(t["ideal_c"]))


def nhat(plus, minus):
    c = pcb.output_contrast(plus / plus.sum(), minus / minus.sum())
    V = float(np.mean(c * sign))
    return c.sum() / 2 / V, c.sum() / 2, V


raw = nhat(cn[16:], cn[:16])
x = np.linalg.solve(M, cn)
cor = nhat(x[16:], x[:16])
# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 10
rng = np.random.default_rng(22436)
B: Any = []
for _ in range(2000):
    s = rng.multinomial(int(cn.sum()), cn / cn.sum()).astype(float)
    y = np.linalg.solve(M, s)
    B.append(nhat(y[16:], y[:16])[:2])
B = np.array(B)
print(
    f"Tuna b0 raw N_hat {raw[0]:+.4f} (half-sum {raw[1]:+.4f}, V {raw[2]:.3f}); readout-corrected (batch-02 bracket, joint product matrix) N_hat {cor[0]:+.4f} +- {B[:, 0].std():.4f} (half-sum {cor[1]:+.4f} +- {B[:, 1].std():.4f}, V {cor[2]:.3f})"
)
# readout-only prediction: apply M to the ideal coin laws contracted toward uniform to the observed raw visibility
ideal = np.array(case["circuits"][1]["ideal"])
for V_target in (1.0, 0.44):
    # contraction factor r so that raw V matches after readout: solve by scan
    best: Any = None
    for r in np.linspace(0.3, 1.0, 71):
        law = M @ (r * ideal + (1 - r) / 32)
        a = 2 * law[16:]
        b = 2 * law[:16]
        n = nhat(a, b)
        if best is None or abs(n[2] - V_target) < abs(best[1][2] - V_target):
            best = (r, n)
    print(
        f"readout-only prediction (contraction r={best[0]:.2f}, then bracket misassignment): N_hat {best[1][0]:+.4f}, half-sum {best[1][1]:+.4f}, V {best[1][2]:.3f}"
    )
# per-arm coin read fraction vs ideal 0.5
print("coin read fraction", cn[16:].sum() / cn.sum(), "(ideal 0.5); coin qubit bracket", brk[roles["coin"]])
