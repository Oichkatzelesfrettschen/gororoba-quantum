"""Shared loader for the Ascella pair-run mirror analysis: rows, calibration and the 46 mirror pairs."""

import importlib
import json

import numpy as np
from c1_mesh import PAIRS, ROOT  # noqa: F401  (c1_mesh puts scripts/ and gororoba_quantum/ on sys.path)

an = importlib.import_module("ascella_pathion_coset_block_pairs_analysis")

manifest = json.loads((PAIRS / "cases.json").read_bytes())
results = json.loads((PAIRS / "results.json").read_bytes())
settings = manifest["settings"]
reg = manifest["preregistered"]
modes = {"slots": reg["slot_modes"], "failure": reg["failure_mode"], "sentinel": reg["sentinel_modes"]}
structure = an.layout(manifest)
samples = manifest["max_samples"] // manifest["iterations"]
cap = manifest["max_shots"] // manifest["iterations"]
TOL = reg["thresholds"]["level_tolerance"]
MIRROR = reg["thresholds"]["mirror_spread"]


def observed_rows():
    return [
        an.observation((i, s, e, samples, cap, modes))
        for i, (s, e) in enumerate(zip(settings, results["iterations"], strict=True))
    ]


def rows_from_probs(P, total=None):
    """Row dicts from per-iteration probability vectors P (52, 12) over output modes (all clicks in modes 0..11)."""
    rows = []
    for i, p in enumerate(P):
        p9 = np.asarray(p)
        n = float(samples) if total is None else total
        tot9 = p9[:9].sum()
        counts = n * p9[:9] / tot9
        rows.append(
            {
                "index": i,
                "name": settings[i]["name"],
                "returned": True,
                "port_counts": list(counts) + [0, 0, 0],
                "slot": {k: float(sum(counts[m] for m in modes["slots"][k])) for k in an.SLOTS},
                "failure": float(counts[8]),
                "total": float(counts.sum()),
            }
        )
    return rows


def mirror_table(rows, with_idx=False):
    """Signed mirror differences l(o0) - l(o1) per (setting, item) and the two calibrated levels."""
    cal = an.calibrate(rows, settings)
    out = {}
    for name, design in structure["designs"].items():
        if design["role"] not in ("sign", "null"):
            continue
        for item in (0, 1):
            ls = []
            for o in (0, 1):
                idx = structure["by_setting"][name][o][0]
                slot = an.SLOTS[item if o == 0 else 1 - item]
                ls.append((idx, slot, an.slot_levels(rows[idx], cal)[slot]["l_hat"]))
            out[(name, item)] = ls
    return out, cal


def signed_diffs(rows):
    t, cal = mirror_table(rows)
    keys = sorted(t)
    return keys, np.array([t[k][0][2] - t[k][1][2] for k in keys]), t, cal


def bootstrap_diffs(rows, draws):
    """Signed mirror differences of one parametric-bootstrap replicate: rows with their 12-mode counts replaced by draws
    (one multinomial per row, in row order), recalibrated through signed_diffs."""
    rr = []
    for r, c12 in zip(rows, draws, strict=True):
        k9 = c12[:9]
        rr.append(
            {
                **r,
                "port_counts": list(c12),
                "slot": {k: float(sum(c12[m] for m in modes["slots"][k])) for k in an.SLOTS},
                "failure": float(c12[8]),
                "total": float(k9.sum()),
            }
        )
    return signed_diffs(rr)[1]
