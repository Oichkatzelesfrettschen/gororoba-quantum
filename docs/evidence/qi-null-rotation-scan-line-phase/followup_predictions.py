"""Model contrasts of the draft follow-up arms under exact pulses, a q12 phase and a coupler 8-12 phase."""

import json
from typing import Any

import numpy as np
from scan_forward import ROOT, cc, laws, rs

print(
    "follow-up predictions: mean selector contrast at the retention where the exact center reads "
    "visibility 0.42 through the mean bracket matrix of the retained series, under three worlds: "
    "exact pulses; a phase of -0.18 rad before each q12 pulse; a conditional phase of -0.25 rad on "
    "coupler 8-12. Arms: q4 pulses at k steps of 5 degrees; Rz(phi) before each q12 pulse."
)
S = "2026-11-15T001929Z"
A_ = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
man = json.loads(
    (ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-batch-01/cases.json").read_text()
)
roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
register = [int(q) for q in man["register"]]
gs = [r["guard"] for r in A_["batch_rows"].values()]
mean = {
    q: tuple(float(np.mean([(g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for g in gs])) for i in (0, 1))
    for q in register
}
M = cc.readout_matrix(mean, roles)
U = np.full(rs.NOUT, 1 / rs.NOUT) @ M.T
one = np.zeros(1)
exact_center = laws(rs.CENTER, [(("none", None, None), one)])[0] @ M.T
R = np.linspace(0.05, 1, 381)
r0 = R[np.abs(np.array([rs.visibility(r * exact_center + (1 - r) * U) for r in R]) - 0.42).argmin()]
WORLDS: dict[str, list[tuple[Any, Any]]] = {
    "exact": [],
    "z12 -0.18": [(("pulse", "zb", 12), np.array([-0.18]))],
    "cz(8,12) -0.25": [(("cz", (8, 12), None), np.array([-0.25]))],
}
out = {}


def contrast(arm, items):
    seen = r0 * (laws(arm, items or [(("none", None, None), one)])[0] @ M.T) + (1 - r0) * U
    return round(float(rs.selector_contrast(seen)), 4), round(float(rs.d2_split(seen)[0]), 4)


for k in (-2, -1, 0, 1, 2, 3, 4):
    rs.ARMS[f"q4k{k}"] = ("Rx", "q4", k)
Q8_AFTER_CZ = ("czz", 8, (8, 12))
for name, items in WORLDS.items():
    out[name] = {
        "q4": {str(5 * k): contrast(f"q4k{k}", items) for k in (-2, -1, 0, 1, 2, 3, 4)},
        "q12_rz": {
            str(d): contrast(
                rs.CENTER,
                [*items, (("pulse", "zb", 12), np.array([np.radians(d)]))]
                if not (name.startswith("z12"))
                else [(("pulse", "zb", 12), np.array([-0.18 + np.radians(d)]))],
            )
            for d in (-20, -10, 0, 10, 20)
        },
        "q8_rz_after_cz_8_12": {
            str(d): contrast(rs.CENTER, [*items, (Q8_AFTER_CZ, np.array([np.radians(d)]))]) for d in (-20, -10, 10, 20)
        },
    }
    print(name)
    print("  q4 degrees -> (contrast, d2_split):", out[name]["q4"])
    print("  Rz on q12 degrees -> (contrast, d2_split):", out[name]["q12_rz"])
    print("  Rz on q8 after each 8-12 CZ -> (contrast, d2_split):", out[name]["q8_rz_after_cz_8_12"])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/followup_predictions.json").write_text(
    json.dumps({"retention": float(r0), "worlds": out}, indent=1) + "\n"
)
