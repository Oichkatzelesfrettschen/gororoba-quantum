"""C1: held-out score on the unseen orientation's levels only: corr(obs - base, model - base) with base the
efficiency-and-background-only model trained on the same iterations, and the rms gain over that base."""

from pathlib import Path

import numpy as np
from c1_common import mirror_table, observed_rows, rows_from_probs

HERE = Path(__file__).resolve().parent

Z = np.load(HERE / "c1_static.npz")
rows = observed_rows()


def levels(P):
    t, _ = mirror_table(rows_from_probs(P))
    return {(k, o): t[k][o][2] for k in t for o in (0, 1)}


t, _ = mirror_table(rows)
obs = {(k, o): t[k][o][2] for k in t for o in (0, 1)}
keys = sorted({k for k, _ in obs})
for train, held in (("o0", 1), ("o1", 0)):
    base = levels(Z[f"none_{train}"])
    ro = np.array([obs[(k, held)] - base[(k, held)] for k in keys])
    print(
        f"trained on orientation {train[1]}, scored on orientation {held} levels (46 readings): base rms {np.sqrt(np.mean(ro**2)):.4f}"
    )
    for m in ("gain1", "theta1", "offset", "gain"):
        mod = levels(Z[f"{m}_{train}"])
        rm = np.array([mod[(k, held)] - base[(k, held)] for k in keys])
        res = ro - rm
        print(
            f"  {m:7s} corr(obs - base, model - base) {np.corrcoef(ro, rm)[0, 1]:+.3f}; residual rms {np.sqrt(np.mean(res**2)):.4f} ({100 * (1 - np.sqrt(np.mean(res**2)) / np.sqrt(np.mean(ro**2))):+.0f} percent vs base)"
        )
