"""Exploratory: the retained d2 splits of the 24 scan arms against three worlds at fixed parameters.

Worlds: exact pulses; a phase of -0.18 rad before each q12 pulse; a conditional phase of -0.25 rad on coupler
8-12 (the shared-parameter values of widened_worlds.py, fitted to the selector contrasts alone). Each batch takes
the contraction (share 0) at which the world's center arm reads the batch's center visibility through its
bracket matrix. Statistic: chi-square of the 24 d2 splits, which no fit here used, with their binomial errors."""

import json

import numpy as np
from scan_forward import ROOT, cc, laws, rs

A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
S = "2026-11-15T001929Z"
man = json.loads(
    (ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-batch-01/cases.json").read_text()
)
roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
register = [int(q) for q in man["register"]]
WORLDS = {
    "exact": (("none", None, None), 0.0),
    "q12_phase": (("pulse", "zb", 12), -0.18),
    "coupler_8_12_phase": (("cz", (8, 12), None), -0.25),
}
R = np.linspace(0.05, 1.0, 381)
out: dict[str, dict[str, object]] = {}
for name, (cand, value) in WORLDS.items():
    table = {arm: laws(arm, [(cand, np.array([value]))])[0] for arm in rs.ARM_NAMES if arm != rs.RETAINED}
    chi = 0.0
    rows = {}
    for batch, row in A["batch_rows"].items():
        if row["kind"] == "bridge":
            continue
        g = row["guard"]
        mean = {q: tuple((g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for i in (0, 1)) for q in register}
        M = cc.readout_matrix(mean, roles)
        U = np.full(rs.NOUT, 1 / rs.NOUT) @ M.T
        center = table[rs.CENTER] @ M.T
        cv = row["statistics"][row["arms"].index(rs.CENTER)]["visibility"]
        r = R[np.abs(np.array([rs.visibility(x * center + (1 - x) * U) for x in R]) - cv).argmin()]
        for arm, st in zip(row["arms"], row["statistics"], strict=True):
            model = float(rs.d2_split(r * (table[arm] @ M.T) + (1 - r) * U)[0])
            chi += ((st["d2_split"] - model) / st["d2_split_se"]) ** 2
            rows[f"{batch}/{arm}"] = [round(st["d2_split"], 4), round(model, 4)]
    out[name] = {"chi2_24": round(chi, 1), "measured_model": rows}
    print(name, out[name]["chi2_24"])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/d2_split_worlds.json").write_text(
    json.dumps(out, indent=1) + "\n"
)
