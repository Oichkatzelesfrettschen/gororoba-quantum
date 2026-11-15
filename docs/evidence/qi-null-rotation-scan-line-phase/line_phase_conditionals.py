"""Exploratory: which probabilities carry the line-phase dependence of the selector contrast in the b0 and b0-rx jobs.

The line's frequency and phase come from q4's bit on the odd-indexed shots; every statistic is folded on the
even-indexed shots in 8 phase bins and reduced to its first harmonic, coherently averaged over the jobs. Statistics:
P(selector reads 0 | coin 1), P(selector reads 0 | coin 0), their difference (the selector contrast), the marginals
P(selector reads 0) and P(coin reads 1), and the contrast within the shots where q4 reads 0 and where q4 reads 1."""

# ruff: noqa: E402  (the scan module is imported after the path insertion that locates it)
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import qi_pathion_null_rotation_scan_cases as rs

S = "2026-11-15T001929Z"
BINS = 8
ang = 2 * np.pi * (np.arange(BINS) + 0.5) / BINS


def locate(x, n):
    g = np.linspace(0.02008, 0.02016, 201)
    z = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g])
    f0 = g[np.abs(z).argmax()]
    g2 = np.linspace(f0 - 4e-7, f0 + 4e-7, 81)
    z2 = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g2])
    j = np.abs(z2).argmax()
    return g2[j], -np.angle(z2[j])


def contrast(sel0, coin, mask):
    return sel0[mask & coin].mean() - sel0[mask & ~coin].mean()


def first(values):
    return 2 * np.mean(np.array(values) * np.exp(-1j * ang))


names = (
    "sel0_given_coin1",
    "sel0_given_coin0",
    "contrast",
    "sel0",
    "coin1",
    "contrast_q4_reads_0",
    "contrast_q4_reads_1",
)
per: dict[str, list[complex]] = {k: [] for k in names}
for d in sorted((ROOT / "results/quantum_inspire/runs").glob(f"{S}-pathion_null_rotation_scan_tuna_17-batch-*")):
    roles = {k: int(v) for k, v in json.loads((d / "cases.json").read_text())["templates"]["b0"]["roles"].items()}
    for f in sorted((d / "raw").iterdir()):
        if rs.arm_of(f.name.removesuffix(".json")) not in ("b0", "b0-rx"):
            continue
        shots = json.loads(f.read_text())
        bit = {q: np.array([s[16 - q] == "1" for s in shots]) for q in (4, roles["selector"], roles["coin"])}
        n = np.arange(len(shots))
        odd, even = n[1::2], n[0::2]
        x = bit[4][odd].astype(float)
        fo, po = locate(x - x.mean(), odd)
        b = (((2 * np.pi * fo * even - po) % (2 * np.pi)) / (2 * np.pi) * BINS).astype(int) % BINS
        sel0, coin, q4 = ~bit[roles["selector"]][even], bit[roles["coin"]][even], bit[4][even]
        rows: dict[str, list[float]] = {k: [] for k in names}
        for k in range(BINS):
            m = b == k

            rows["sel0_given_coin1"].append(sel0[m & coin].mean())
            rows["sel0_given_coin0"].append(sel0[m & ~coin].mean())
            rows["contrast"].append(contrast(sel0, coin, m))
            rows["sel0"].append(sel0[m].mean())
            rows["coin1"].append(coin[m].mean())
            rows["contrast_q4_reads_0"].append(contrast(sel0, coin, m & ~q4))
            rows["contrast_q4_reads_1"].append(contrast(sel0, coin, m & q4))
        for key in names:
            per[key].append(first(rows[key]))
out = {}
for key in names:
    h = np.mean(per[key])
    proj = (np.array(per[key]) * np.conj(h / abs(h))).real
    out[key] = {
        "h1": float(abs(h)),
        "phase": float(np.angle(h)),
        "cluster_se": float(proj.std(ddof=1) / np.sqrt(len(proj))),
    }
    print(key, {k: round(v, 5) for k, v in out[key].items()})
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_conditionals.json").write_text(
    json.dumps({"jobs": len(per["contrast"]), "first_harmonic": out}, indent=1) + "\n"
)
