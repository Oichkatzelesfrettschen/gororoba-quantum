"""Exploratory: leak control of the phase fold. The line's frequency and phase come from q4's bit on the odd-indexed
shots; the selector contrast is folded on the even-indexed shots. Null by the same procedure: maximize q4's Fourier
amplitude in an off-line band (0.02350 to 0.02358 cycles per shot), then fold. b0 and b0-rx jobs only."""

# ruff: noqa: E402  (repository modules are imported after the path insertion that locates them)
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
ang = 2 * np.pi * (np.arange(BINS) + 0.5) / BINS


def locate(x, n, lo, hi):
    g = np.linspace(lo, hi, 201)
    z = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g])
    f0 = g[np.abs(z).argmax()]
    g2 = np.linspace(f0 - 4e-7, f0 + 4e-7, 81)
    z2 = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g2])
    j = np.abs(z2).argmax()
    return g2[j], -np.angle(z2[j])


def harmonic(shots, idx, roles, f, ph):
    theta = (2 * np.pi * f * idx - ph) % (2 * np.pi)
    b = (theta / (2 * np.pi) * BINS).astype(int) % BINS
    arr = np.array(shots, dtype=object)[idx]
    st = [rs.circuit_statistics(list(arr[b == k]), roles) for k in range(BINS)]
    c = np.array([s["contrast"] for s in st])
    e = np.array([s["se"] for s in st])
    return 2 * np.mean(c * np.exp(-1j * ang)), float(np.sqrt(2 * np.mean(e**2) / BINS))


on = []
off = []
rows: list[dict[str, Any]] = []
for d in sorted((ROOT / "results/quantum_inspire/runs").glob(f"{S}-pathion_null_rotation_scan_tuna_17-batch-*")):
    roles = {k: int(v) for k, v in json.loads((d / "cases.json").read_text())["templates"]["b0"]["roles"].items()}
    for f in sorted((d / "raw").iterdir()):
        arm = rs.arm_of(f.name.removesuffix(".json"))
        if arm not in ("b0", "b0-rx"):
            continue
        shots = json.loads(f.read_text())
        n = np.arange(len(shots))
        odd = n[1::2]
        even = n[0::2]
        x = np.array([s[16 - 4] == "1" for s in shots], float)
        xo = x[odd] - x[odd].mean()
        fo, po = locate(xo, odd, 0.02008, 0.02016)
        h, se = harmonic(shots, even, roles, fo, po)
        on.append((h, se))
        fn, pn = locate(xo, odd, 0.02350, 0.02358)
        g, _ = harmonic(shots, even, roles, fn, pn)
        off.append((g, se))
        rows.append(
            {
                "batch": d.name[-8:],
                "arm": arm,
                "f": float(fo),
                "h1": [float(abs(h)), float(np.angle(h))],
                "se": se,
                "off_line_h1": [float(abs(g)), float(np.angle(g))],
            }
        )
        print(
            d.name[-8:],
            arm.ljust(6),
            f"f={fo:.7f} |h1|={abs(h):.4f} ph={np.angle(h):+.2f} se={se:.4f} | off-line |h1|={abs(g):.4f}",
            flush=True,
        )
for name, v in (("line", on), ("off-line", off)):
    h = np.mean([x[0] for x in v])
    se = float(np.sqrt(np.mean([x[1] ** 2 for x in v]) / len(v)))
    print(
        name,
        len(v),
        f"coherent mean |h1|={abs(h):.4f} ({abs(h) / se:.1f} se) phase {np.angle(h):+.2f}; mean of |h1| "
        f"{np.mean([abs(x[0]) for x in v]):.4f}; per-job se {v[0][1]:.4f}",
    )


def job_level(values):
    """Job-level calibration of a coherent mean of per-job harmonics: the standard error of the projections on the
    mean's direction over jobs, and the exact sign-flip null (every pattern of +-1 per job), whose spread and tail
    take the fitted phases, the frequency drift and the between-job scatter as random."""
    h = np.array(values)
    mean = h.mean()
    unit = mean / abs(mean)
    projections = (h * np.conj(unit)).real
    signs = np.array(np.meshgrid(*[[1.0, -1.0]] * len(h), indexing="ij")).reshape(len(h), -1)
    null = np.abs((signs * h[:, None]).mean(0))
    return {
        "cluster_se": float(projections.std(ddof=1) / np.sqrt(len(h))),
        "sign_flip_p": float((null >= abs(mean) - 1e-15).mean()),
        "sign_flip_null_component_sd": float(np.sqrt((np.abs(h) ** 2).sum() / 2) / len(h)),
    }


summary = {}
for name, v in (("line", on), ("off_line", off)):
    h = np.mean([x[0] for x in v])
    se = float(np.sqrt(np.mean([x[1] ** 2 for x in v]) / len(v)))
    summary[name] = {
        "jobs": len(v),
        "coherent_h1": float(abs(h)),
        "shot_noise_se": se,
        "phase": float(np.angle(h)),
        **job_level([x[0] for x in v]),
    }
    print(name, summary[name])
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.json").write_text(
    json.dumps({"jobs": rows, "summary": summary}, indent=1) + "\n"
)
