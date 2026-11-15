"""Exploratory: measured selector contrast minus the exact-pulse forward law at matched center visibility."""

# ruff: noqa: E402  (repository modules are imported after the path insertion that locates them)
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

cc = rs.cc
A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
S = "2026-11-15T001929Z"
man = json.loads(
    (ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-batch-01/cases.json").read_text()
)
roles = {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}
register = [int(q) for q in man["register"]]
world = "pulse_x_before_all"
grid = rs.parameter_grid(world)
zero = int(np.argmin(np.abs(grid)))
out = {}
for batch, row in A["batch_rows"].items():
    if row["kind"] == "bridge":
        continue
    g = row["guard"]
    mean = {q: tuple((g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for i in (0, 1)) for q in register}
    matrix = cc.readout_matrix(mean, roles)
    arms = tuple(row["arms"])
    c = np.array([s["contrast"] for s in row["statistics"]])
    e = np.array([s["se"] for s in row["statistics"]])
    cv = row["statistics"][arms.index(rs.CENTER)]["visibility"]
    vis = [round(s["visibility"], 3) for s in row["statistics"]]
    line = {"kind": row["kind"], "arms": arms, "measured": c.round(4).tolist(), "visibility": vis, "exact": {}}
    for kind in rs.FIT_KINDS:
        model, strength = rs.gate_fit_model(world, kind, arms, matrix, cv)
        m = model[zero]
        line["exact"][kind] = {
            "model": m.round(4).tolist(),
            "residual": (c - m).round(4).tolist(),
            "z": ((c - m) / e).round(1).tolist(),
        }
    out[batch] = line
    print(batch, row["kind"], arms)
    print("  measured", line["measured"], "vis", vis)
    for kind, v in line["exact"].items():
        print(f"  {kind:22s} model {v['model']} residual {v['residual']} z {v['z']}")
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/exact_pulse_residuals.json").write_text(
    json.dumps(out, indent=1)
)
