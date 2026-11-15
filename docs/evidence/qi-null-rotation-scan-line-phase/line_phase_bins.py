"""Exploratory: selector contrast and bit means of each data job in 8 bins of the shot-order line's phase.

Written before computing. The line's frequency and phase per job come from the q4 bit (largest |sum x exp(-2 pi i f n)|
on a grid of 0.02008 to 0.02016 cycles per shot); phase 0 is the maximum of q4's P(1). Statistic: first and second
harmonic of the selector contrast over the phase, per job and pooled over the eleven b0-rx jobs. Null: no dependence,
harmonic amplitudes within their binomial errors; calibration: the same fold at a frequency outside the line
(0.0237 cycles per shot) gives the null distribution in the same data."""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

S = "2026-11-15T001929Z"
BINS = 8
A = json.loads((ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text())
FG = np.linspace(0.02008, 0.02016, 1601)


def fold(shots, roles, f, ph):
    n = np.arange(len(shots))
    theta = (2 * np.pi * f * n - ph) % (2 * np.pi)
    b = (theta / (2 * np.pi) * BINS).astype(int) % BINS
    arr = np.array(shots, dtype=object)
    out: list[dict[str, Any]] = []
    for k in range(BINS):
        st = rs.circuit_statistics(list(arr[b == k]), roles)
        out.append((st["contrast"], st["se"]))
    c = np.array([o[0] for o in out])
    e = np.array([o[1] for o in out])
    ang = 2 * np.pi * (np.arange(BINS) + 0.5) / BINS
    h1 = 2 * np.mean(c * np.exp(-1j * ang))
    h2 = 2 * np.mean(c * np.exp(-2j * ang))
    se = float(np.sqrt(2 * np.mean(e**2) / BINS))
    return c, h1, h2, se


rows: list[dict[str, Any]] = []
pooled: dict[str, list[Any]] = {}
for batch, _row in A["batch_rows"].items():
    d = ROOT / f"results/quantum_inspire/runs/{S}-pathion_null_rotation_scan_tuna_17-{batch}"
    roles = {k: int(v) for k, v in json.loads((d / "cases.json").read_text())["templates"]["b0"]["roles"].items()}
    for f in sorted((d / "raw").iterdir()):
        arm = rs.arm_of(f.name.removesuffix(".json"))
        shots = json.loads(f.read_text())
        x4 = np.array([s[16 - 4] == "1" for s in shots], float)
        x4 -= x4.mean()
        n = np.arange(len(x4))
        amp = np.array([np.abs(np.sum(x4 * np.exp(-2j * np.pi * fr * n))) for fr in FG[::8]])
        f0 = FG[::8][amp.argmax()]
        fine = np.linspace(f0 - 4e-7, f0 + 4e-7, 81)
        z = np.array([np.sum(x4 * np.exp(-2j * np.pi * fr * n)) for fr in fine])
        j = np.abs(z).argmax()
        fbest = fine[j]
        ph = -np.angle(z[j])
        a4 = 2 * np.abs(z[j]) / len(x4)
        c, h1, h2, se = fold(shots, roles, fbest, ph)
        c0, g1, g2, _ = fold(shots, roles, 0.0237, 0.0)
        rows.append(
            {
                "batch": batch,
                "file": f.name,
                "arm": arm,
                "f": float(fbest),
                "q4_amp": float(a4),
                "bins": c.round(4).tolist(),
                "h1": [float(abs(h1)), float(np.angle(h1))],
                "h2": [float(abs(h2)), float(np.angle(h2))],
                "se": se,
                "null_h1": float(abs(g1)),
                "null_h2": float(abs(g2)),
            }
        )
        pooled.setdefault(arm, []).append((c, h1, h2, se, g1, g2))
        print(
            batch,
            f.name[:-8].ljust(15),
            f"f={fbest:.7f} q4amp={a4:.4f} |h1|={abs(h1):.4f} ph1={np.angle(h1):+.2f} |h2|={abs(h2):.4f} "
            f"se={se:.4f} null |h1|={abs(g1):.4f} |h2|={abs(g2):.4f}",
            c.round(3).tolist(),
            flush=True,
        )
print("POOLED (coherent mean over jobs of one arm)")
for arm, v in pooled.items():
    h1 = np.mean([x[1] for x in v])
    h2 = np.mean([x[2] for x in v])
    se = float(np.sqrt(np.mean([x[3] ** 2 for x in v]) / len(v)))
    g1 = np.mean([x[4] for x in v])
    g2 = np.mean([x[5] for x in v])
    c = np.mean([x[0] for x in v], 0)
    print(
        arm.ljust(15),
        len(v),
        f"|h1|={abs(h1):.4f} ({abs(h1) / se:.1f} se) ph={np.angle(h1):+.2f} |h2|={abs(h2):.4f} "
        f"({abs(h2) / se:.1f} se) null {abs(g1) / se:.1f} {abs(g2) / se:.1f}",
        c.round(4).tolist(),
    )
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_bins.json").write_text(json.dumps(rows, indent=1))
