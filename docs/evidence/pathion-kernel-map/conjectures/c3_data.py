"""Tuna-17 coin-series data: per-template counts, roles, brackets, ideal laws, observed raw and corrected bin ratios."""

import importlib
import json

import numpy as np
from c2_data import ROOT

cc = importlib.import_module("qi_pathion_coset_coin_cases")
pcb = importlib.import_module("pathion_coset_block")

CASES = ROOT / "results/quantum_inspire/cases/pathion_coset_coin_tuna_17"
RUNS = ROOT / "results/quantum_inspire/runs"
BATCH = {"ba": "batch-00", "bb": "batch-01", "b0": "batch-02", "xor_ba": "batch-03"}
AN = json.loads((ROOT / "results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json").read_bytes())
BRACKETS = {b: {int(q): tuple(v) for q, v in d.items()} for b, d in AN["drift_covariate"]["brackets"].items()}
T = {}
for name, batch in BATCH.items():
    case = json.loads((CASES / batch / "cases.json").read_bytes())
    t = case["templates"][name]
    shots = json.loads(
        (RUNS / f"2026-11-07T001031Z-pathion_coset_coin_tuna_17-{batch}/raw/{name}.cq.json").read_bytes()
    )
    ideal = np.array(next(c for c in case["circuits"] if c.get("template") == name)["ideal"])
    T[name] = dict(
        roles=t["roles"],
        counts=cc.coin_counts(shots, t["roles"]),
        ideal=ideal,
        ideal_c=np.array(t["ideal_c"]),
        cz=t["cz"],
        batch=batch,
        cq=(CASES / batch / f"{name}.cq"),
        basis=t["basis"],
        operand=t["operand"],
    )
KEYS = cc.KEYS


def ratio_of(counts, sign, matrix=None):
    """c(y)*sign / V and V of a 32-outcome coin law (counts or probabilities)."""
    x = counts if matrix is None else np.linalg.solve(matrix, counts)
    plus, minus = x[16:], x[:16]
    c = pcb.output_contrast(plus / plus.sum(), minus / minus.sum())
    V = float(np.mean(c * sign))
    return c * sign / V, V, c


def matrix_for(name, batch=None):
    t = T[name]
    return cc.readout_matrix(BRACKETS[batch or t["batch"]], t["roles"])


# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 11
def se_ratio(counts, sign, matrix=None, B=600, seed=17331):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(B):
        s = rng.multinomial(int(counts.sum()), counts / counts.sum()).astype(float)
        out.append(ratio_of(s, sign, matrix)[0])
    return np.std(out, axis=0)
