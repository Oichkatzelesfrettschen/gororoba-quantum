"""C1: scatter between distinct configurations and between repeats of one configuration, predecessor job vs pairs job."""

import json
from typing import Any

import numpy as np
from c1_common import observed_rows, settings, signed_diffs
from c1_mesh import FOUR, cached, propagate

a = json.loads((FOUR / "analysis.json").read_bytes())
m = json.loads((FOUR / "cases.json").read_bytes())
rd = a["readings"]
dev = np.array([r["deviation"] for r in rd])
raw = np.array([r["raw_departure_from_ideal"] for r in rd])
roles = np.array([r["role"] for r in rd])
arms = np.array([r["arm"] for r in rd])
print(
    f"predecessor readings {len(rd)}: deviation (a' - ideal) rms {np.sqrt(np.mean(dev**2)):.4f}, median |dev| {np.median(abs(dev)):.4f}, max {abs(dev).max():.4f}"
)
for role in sorted(set(roles)):
    s = roles == role
    print(f"  role {role}: n {s.sum()} rms {np.sqrt(np.mean(dev[s] ** 2)):.4f} max {abs(dev[s]).max():.4f}")
nonanchor = roles != "anchor"
print(f"  excluding anchor: rms {np.sqrt(np.mean(dev[nonanchor] ** 2)):.4f}")
rp = np.array([r["difference"] for r in a["repeated_pairs"]])
print(
    f"predecessor repeated identical-configuration pairs: n {len(rp)}, |diff| median {np.median(abs(rp)):.4f} rms {np.sqrt(np.mean(rp**2)):.4f} max {abs(rp).max():.4f} (stat se of a difference ~ {0.5 / np.sqrt(131072 / 2) * np.sqrt(2):.4f} at p=.5)"
)
# pairs job per-orientation deviations from ideal
rows = observed_rows()
keys, d, tbl, cal = signed_diffs(rows)
dv: Any = []
for k in keys:
    ideal = [s for s in settings if s["setting"] == k[0] and s["orientation"] == 0][0]["slots"]["AB"[k[1]]][
        "ideal_level"
    ]
    for o in (0, 1):
        dv.append(tbl[k][o][2] - ideal)
dv = np.array(dv)
print(
    f"pairs job readings {len(dv)}: deviation (l_hat - ideal) rms {np.sqrt(np.mean(dv**2)):.4f}, median |dev| {np.median(abs(dv)):.4f}, max {abs(dv).max():.4f}"
)
# same config, repeated: pairs job anchors and darks
for i, j in ((0, 51), (1, 50), (2, 49)):
    print(
        f"pairs job identical compiled mesh, iterations {i} and {j}: raw slot-level differences A {2 * (rows[i]['slot']['A'] / rows[i]['total'] - rows[j]['slot']['A'] / rows[j]['total']):+.4f}, B {2 * (rows[i]['slot']['B'] / rows[i]['total'] - rows[j]['slot']['B'] / rows[j]['total']):+.4f}"
    )
# predecessor: do the same models predict the repeats? simulate white per-iteration phase error and the repeat difference
kinds, lo, TH, PH, PERF = cached(FOUR, "four")
settings4 = m["settings"]
succ = m["preregistered"]["success_modes"]
fail = m["preregistered"]["failure_modes"]
# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 5
rng = np.random.default_rng(19971)
sigma = 0.033
R = 400
a_sim = np.empty((R, 88))
for i in range(88):
    dph = rng.normal(0, sigma, size=(R, PH.shape[1]))
    P = propagate(kinds, lo, TH[i], PH[i], dph=dph)
    a_sim[:, i] = P[:, succ].sum(1) / (P[:, succ].sum(1) + P[:, fail].sum(1))
ideal_a = np.array([float(s["ideal_success"]) for s in settings4])
rep = [(r["iterations"][0], r["iterations"][1]) for r in a["repeated_pairs"]]
white = np.sqrt(np.mean([np.mean((a_sim[:, i] - a_sim[:, j]) ** 2) for i, j in rep]))
print(
    f"white per-iteration phase error sigma {sigma}: predicted repeat-pair difference rms {white:.4f} against observed {np.sqrt(np.mean(rp**2)):.4f}"
)
dev_sim = np.sqrt(np.mean((a_sim - ideal_a[None, :]) ** 2))
print(
    f"static (same error on repeats) sigma {sigma}: predicted deviation of single iterations from ideal rms {dev_sim:.4f}; observed per-iteration rms deviation: see readings above (pooled over repeats)"
)
# per-iteration observed deviation raw (a - ideal) from counts
ports: Any = []
for e in json.loads((FOUR / "results.json").read_bytes())["iterations"]:
    from experiment_analysis import decode_photonic_counts

    p, inv = decode_photonic_counts(e["counts"], 12)
    ports.append(p)
ports = np.array(ports, float)
a_obs = ports[:, succ].sum(1) / (ports[:, succ].sum(1) + ports[:, fail].sum(1))
dev_obs = a_obs - ideal_a
print(
    f"observed raw per-iteration (a - ideal) rms {np.sqrt(np.mean(dev_obs**2)):.4f} median |.| {np.median(abs(dev_obs)):.4f} max {abs(dev_obs).max():.4f}"
)
for s in (0.01, 0.02, 0.033, 0.05):
    aa = np.empty((200, 88))
    for i in range(88):
        P = propagate(kinds, lo, TH[i], PH[i], dph=rng.normal(0, s, size=(200, PH.shape[1])))
        aa[:, i] = P[:, succ].sum(1) / (P[:, succ].sum(1) + P[:, fail].sum(1))
    print(
        f"  sigma {s}: simulated per-iteration (a - ideal) rms {np.sqrt(np.mean((aa - ideal_a) ** 2)):.4f}, max over iterations mean {np.mean(np.abs(aa - ideal_a).max(1)):.4f}"
    )
