"""Exploratory: line amplitude of the selector-coin parity bit of every data job, with no phase reference.

The parity bit (selector read value xor coin read value) has mean near 1/2 + contrast/2, so a selector contrast
that oscillates with amplitude h shows as a line of amplitude near h/2 on the bit. Statistic per job: the largest
amplitude 2 |sum x exp(-2 pi i f n)| / N over a grid of 201 frequencies in the line band (0.02008 to 0.02016 cycles
per shot), the same maximum in an off-line band of equal width (0.02350 to 0.02358) as the null of a maximum over
that grid, and the same pair for q4's bit, which the phase folds use as their reference. Written before computing:
an arm whose folded harmonic is small because its q4 reference is lost shows a parity line above the off-line
maximum; an arm without the oscillation shows none."""

# ruff: noqa: E402  (the scan module is imported after the path insertion that locates it)
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

S = "2026-11-15T001929Z"
BANDS = {"line": (0.02008, 0.02016), "off_line": (0.02350, 0.02358)}


def largest(x, band):
    n = np.arange(len(x))
    grid = np.linspace(*band, 201)
    return float(max(2 * abs(np.sum((x - x.mean()) * np.exp(-2j * np.pi * f * n))) / len(x) for f in grid))


rows: list[dict[str, Any]] = []
for d in sorted((ROOT / "results/quantum_inspire/runs").glob(f"{S}-pathion_null_rotation_scan_tuna_17-batch-*")):
    roles = {k: int(v) for k, v in json.loads((d / "cases.json").read_text())["templates"]["b0"]["roles"].items()}
    for f in sorted((d / "raw").iterdir()):
        if f.name.startswith("readout"):
            continue
        shots = json.loads(f.read_text())
        bit = {q: np.array([s[16 - q] == "1" for s in shots], float) for q in (4, roles["selector"], roles["coin"])}
        parity = np.abs(bit[roles["selector"]] - bit[roles["coin"]])
        row = {"batch": d.name[-8:], "arm": rs.arm_of(f.name.removesuffix(".json"))}
        for name, band in BANDS.items():
            row[f"parity_{name}"] = largest(parity, band)
            row[f"q4_{name}"] = largest(bit[4], band)
        rows.append(row)
        print(row, flush=True)
summary = {}
for arm in sorted({r["arm"] for r in rows}):
    v = [r for r in rows if r["arm"] == arm]
    summary[arm] = {"jobs": len(v)} | {
        k: float(np.mean([r[k] for r in v])) for k in ("parity_line", "parity_off_line", "q4_line", "q4_off_line")
    }
    print(arm.ljust(15), {k: round(x, 4) if isinstance(x, float) else x for k, x in summary[arm].items()})
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_parity_amplitude.json").write_text(
    json.dumps({"jobs": rows, "per_arm": summary}, indent=1) + "\n"
)
