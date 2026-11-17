"""Final design round, exploratory. Seed: index 2 of the ANU QRNG draw
docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json.

Per series: the current rule's label and the model-light least contrasts of weighted parabolas through the pooled
z12 arms and centers (phi of -30, -10, 0, +10, +30 degrees) and through the pooled z8c arms and centers, each with
its delta-method standard error. Candidate gate G: a q12_phase label stands only when the z12 least contrast is
compatible with 0 (|least| < 3 SE), a q8_phase_at_coupler label only when the z8c least contrast is. Mechanism: an
injected Rz(-theta) cancels a q12 (q8) phase exactly, so the curve reaches the exact center, 0; a readout flip adds
a constant that no injection removes. Scenarios add true phases beside a readout flip and drifting truths (the
parameter or flip moves linearly over the 14 data batches in series order). The rule column is rule R5, the
decision with the readout flip fixed at 0: decide(..., flips=(0.0,)) under the R6 generator. Writes its per-series
record to docs/local/rebuild/final_round.json (ignored); final_round.log beside this file holds the recorded counts."""

import json
import math
import sys

import numpy as np

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

SERIES = int(sys.argv[1]) if len(sys.argv) > 1 else 300
CZ = ps.CZ_DAMPING
SEED = 35685  # index 2 of docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json


def S(world, theta, flip=0.0, noise=ps.NO_NOISE, theta_end=None, flip_end=None):
    return {
        "world": world,
        "theta": theta,
        "flip": flip,
        "noise": list(noise),
        "theta_end": theta_end,
        "flip_end": flip_end,
    }


SCENARIOS = {
    "q12 -0.18": S("q12_phase", -0.18),
    "q12 +0.18": S("q12_phase", 0.18),
    "q12 -0.15 CZ": S("q12_phase", -0.15, noise=CZ),
    "coupler -0.25": S("coupler_phase", -0.25),
    "coupler +0.25": S("coupler_phase", 0.25),
    "q8 -0.25": S(ps.Q8_PHASE, -0.25),
    "q12 -0.18 flip 0.0166": S("q12_phase", -0.18, 0.0166),
    "q12 -0.18 flip 0.036": S("q12_phase", -0.18, 0.036),
    "coupler -0.25 flip 0.0166": S("coupler_phase", -0.25, 0.0166),
    "coupler -0.25 flip 0.036": S("coupler_phase", -0.25, 0.036),
    "q8 -0.25 flip 0.036": S(ps.Q8_PHASE, -0.25, 0.036),
    "null flip 0.0166": S("exact", 0.0, 0.0166),
    "null flip 0.036": S("exact", 0.0, 0.036),
    "null flip 0.025 CZ phase 0.13": S("exact", 0.0, 0.025, (0, 0, 0, 0.13)),
    "null flip 0.025 pulse phase 0.10": S("exact", 0.0, 0.025, (0, 0.10, 0, 0)),
    "null flip 0.036 CZ phase 0.16": S("exact", 0.0, 0.036, (0, 0, 0, 0.16)),
    "drift q12 -0.12 to -0.20": S("q12_phase", -0.12, theta_end=-0.20),
    "drift coupler -0.18 to -0.30": S("coupler_phase", -0.18, theta_end=-0.30),
    "drift null flip 0 to 0.036": S("exact", 0.0, 0.0, flip_end=0.036),
    "drift null flip 0.0166 to 0.036 CZ phase 0.13": S("exact", 0.0, 0.0166, (0, 0, 0, 0.13), flip_end=0.036),
    "drift q12 -0.18, flip 0 to 0.036": S("q12_phase", -0.18, 0.0, flip_end=0.036),
}


def base_batches(sc, m):
    order = ps.batch_order()
    n = len(order)
    if sc["theta_end"] is None and sc["flip_end"] is None:
        return ps.planted_batches(ps.truth_row(sc["world"], sc["theta"], m, sc["flip"], noise=tuple(sc["noise"])))
    out = []
    for k in range(n):
        f = k / (n - 1)
        th = sc["theta"] + f * ((sc["theta_end"] if sc["theta_end"] is not None else sc["theta"]) - sc["theta"])
        fl = sc["flip"] + f * ((sc["flip_end"] if sc["flip_end"] is not None else sc["flip"]) - sc["flip"])
        out.append(ps.planted_batches(ps.truth_row(sc["world"], th, m, fl, noise=tuple(sc["noise"])))[k])
    return out


def least(points):
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    w = 1.0 / np.array([p[2] for p in points]) ** 2
    d = np.stack([np.ones_like(x), x, x * x], axis=1)
    normal = d.T @ (w[:, None] * d)
    c, b, a = np.linalg.solve(normal, d.T @ (w * y))
    cov = np.linalg.inv(normal)
    if a <= 0:
        return None
    value = c - b * b / (4 * a)
    grad = np.array([1.0, -b / (2 * a), b * b / (4 * a * a)])
    return float(value), float(math.sqrt(grad @ cov @ grad)), float(-b / (2 * a))


def curve_points(batches, kinds, index):
    pts = []
    for b in batches:
        if b["kind"] in kinds:
            for arm, c, e in zip(b["arms"], b["contrasts"], b["errors"], strict=True):
                pts.append((0.0 if arm == ps.CENTER else ps.ARMS[arm][index] * 5.0, c, e))
    return pts


def run(item):
    pos, sc = item
    rng = np.random.default_rng([SEED, pos])
    m = ps.predecessor_matrix()
    err = 1 / math.sqrt(ps.SCAN_SHOTS)
    base = base_batches(sc, m)
    draws = rng.standard_normal((SERIES + 1, len(base), 6))
    rows = []
    for i in range(SERIES + 1):
        s = 0.0 if i == 0 else 1.0
        bs = [
            {
                **b,
                "contrasts": [v + s * err * draws[i, n, j] for j, v in enumerate(b["contrasts"])],
                "splits": [
                    v + ps.OC_SPLIT_OFFSET + s * 2 * err * draws[i, n, 3 + j] for j, v in enumerate(b["splits"])
                ],
            }
            for n, b in enumerate(base)
        ]
        d = ps.decide(bs, lambda _b: m, flips=(0.0,))
        rows.append(
            {
                "label": d["label"],
                "z12": least(curve_points(bs, ("z12-10", "z12-30"), 1)),
                "z8c": least(curve_points(bs, ("z8c-10",), 2)),
            }
        )
    return rows


def gated(row):
    lab = row["label"]
    key = {"q12_phase": "z12", ps.Q8_PHASE: "z8c"}.get(lab)
    if key is None:
        return lab
    fit = row[key]
    return lab if fit is not None and abs(fit[0]) < 3 * fit[1] else "gate_" + lab


def fmt(t):
    return "none" if t is None else f"{t[0]:+.4f}+-{t[1]:.4f}@{t[2]:+.1f}"


def main():
    ps.build_tables()
    res = ordered_map(run, list(enumerate(SCENARIOS.values())), min_items=2)
    json.dump(dict(zip(SCENARIOS, res, strict=True)), open("docs/local/rebuild/final_round.json", "w"))
    for name, rows in zip(SCENARIOS, res, strict=True):
        e = rows[0]
        noisy = rows[1:]
        count, gcount = {}, {}
        for r in noisy:
            count[r["label"]] = count.get(r["label"], 0) + 1
            g = gated(r)
            gcount[g] = gcount.get(g, 0) + 1
        z12 = e["z12"]
        z8 = e["z8c"]
        print(f"{name:46s} exp {e['label']:20s} z12 {fmt(z12)} z8c {fmt(z8)}")
        print(f"{'':46s} rule {dict(sorted(count.items()))}")
        print(f"{'':46s} gate {dict(sorted(gcount.items()))}", flush=True)


if __name__ == "__main__":
    main()
