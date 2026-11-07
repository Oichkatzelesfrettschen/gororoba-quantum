"""Permutation null for the static-shifter fits: break the link between each training iteration's counts and its
compiled configuration (shuffle among the training sign/null iterations), refit, and score the held-out orientation."""

import c1_static as S
import numpy as np
from c1_common import rows_from_probs

from parallel import ordered_map

obs = S.levels_of(S.ROWS)
keys = sorted({k for k, _ in obs})
d_obs = np.array([obs[(k, 0)] - obs[(k, 1)] for k in keys])


def score(o, held):
    lev = S.levels_of(rows_from_probs(o["P"]))
    dmod = np.array([lev[(k, 0)] - lev[(k, 1)] for k in keys])
    r = np.array([obs[(k, held)] - lev[(k, held)] for k in keys])
    return np.corrcoef(d_obs, dmod)[0, 1], float(np.sqrt(np.mean(r**2)))


def main():
    # QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 6
    rng = np.random.default_rng(41577)
    out = {}
    for model, train, held in (("gain", "o1", 0), ("offset", "o1", 0)):
        tr = [i for i in range(52) if S.ORI[i] == 1 and S.ROLE[i] == "sign"]
        tasks = [(model, train, None)]
        for _ in range(11):
            perm = list(range(52))
            sh = rng.permutation(tr)
            for a, b in zip(tr, sh, strict=True):
                perm[a] = int(b)
            tasks.append((model, train, perm))
        res = ordered_map(S.fit, tasks, min_items=1)
        sc = [score(o, held) for o in res]
        out[(model, train)] = sc
        print(
            f"{model} train {train}: true link corr {sc[0][0]:+.3f} held-out rms {sc[0][1]:.4f}; shuffled links corr {[round(c, 2) for c, _ in sc[1:]]} (max {max(c for c, _ in sc[1:]):+.3f}), held-out rms median {np.median([r for _, r in sc[1:]]):.4f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
