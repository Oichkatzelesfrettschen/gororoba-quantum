"""IBM and Tuna raw-count loaders and the shared estimator N_hat = (sum_y c(y) / 2) / V for the coset blocks."""

import glob
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
HERE = Path(__file__).resolve().parent
RUNS = {
    "fez": "2026-11-06T201037.234804Z",
    "marrakesh": "2026-11-06T200832.558771Z",
    "fez_full": "2026-11-06T183538.809814Z",
}


def load_ibm(run_key):
    """{member: array (replicas, 2^n)} of raw counts indexed by the integer of the bitstring, plus the record."""
    run = ROOT / "results/live" / RUNS[run_key]
    rec = json.loads((run / "record.json").read_bytes())
    raw = Path(glob.glob(str(run / "raw/*"))[0])
    pubs = rec["execution_pubs"]
    out = {}
    for p in pubs:
        member = p["components"][0]["member"]
        pj = json.loads((raw / f"pub_{pubs.index(p):02d}.json").read_bytes())
        regs = pj["registers"]
        reps = []
        for k in range(len(regs)):
            bits = regs[f"g0_r{k}_c"]["bitstrings"] if f"g0_r{k}_c" in regs else None
            if bits is None:
                break
            n = len(bits[0])
            c = np.zeros(1 << n)
            for b in bits:
                c[int(b, 2)] += 1
            reps.append(c)
        out[member] = np.array(reps)
    return out, rec


def contrast_stats(plus, minus, ideal_plus, ideal_minus, d):
    """c(y), V (signed mean over decided bins), half-sum and N_hat from two outcome-count/prob vectors indexed y + 2^d s."""
    half = 1 << d

    def cond(law):
        tot = law[:half] + law[half:]
        return np.divide(law[:half], tot, out=np.zeros(half), where=tot > 0)

    c = cond(plus) - cond(minus)
    ci = cond(ideal_plus) - cond(ideal_minus)
    dec = np.abs(ci) > 1e-9
    V = float(np.mean(c[dec] * np.sign(ci[dec]))) if dec.any() else float("nan")
    hs = float(c.sum() / 2)
    return {
        "c": c,
        "ci": ci,
        "V": V,
        "half_sum": hs,
        "N_hat": hs / V if abs(V) > 1e-9 else float("nan"),
        "sel": float(plus[:half].sum() - minus[:half].sum()),
    }


def block_info(rec):
    """{member: (cz, ideal)}"""
    g = rec["groups"][0]
    from pathion_coset_block import __name__ as _  # noqa: F401  (ensures path)

    return {
        m["name"]: (
            m["cz"],
            np.array(__import__("ast").literal_eval(m["ideal"]) if isinstance(m["ideal"], str) else m["ideal"], float),
        )
        for m in g["members"]
    }
