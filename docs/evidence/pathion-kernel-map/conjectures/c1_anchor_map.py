"""C1: does the static per-shifter map, fitted on the sign readings, reproduce the anchor efficiency ratio B/A?

The anchor efficiencies come from two configurations only (slot A: iterations 0 and 51; slot B: 1 and 50). If one
static map of shifter errors acts on every configuration, the map fitted to the counts predicts the anchor levels of
those two configurations, and the ratio B/A follows from it. Falsifier: a map that fits the sign readings yet predicts
B/A near the efficiency-only 0.99 leaves the anchor asymmetry to an anchor-specific cause. The four anchor
iterations sit inside every fit's training set (c1_static.py trains on anchors and darks with either orientation), so
this is an in-sample consistency check; the out-of-sample test is fresh anchor configurations under the frozen map."""

import numpy as np
from c1_common import an, observed_rows, rows_from_probs, settings
from c1_static import HERE


def ratio(cal):
    e = cal["efficiency"]
    return e["A"], e["B"], e["B"] / e["A"]


obs = ratio(an.calibrate(observed_rows(), settings))
print(f"observed anchors: efficiency A {obs[0]:.4f} B {obs[1]:.4f} B/A {obs[2]:.4f}")
Z = np.load(HERE / "c1_static.npz")
for key in (
    "none_all",
    "gain1_all",
    "theta1_all",
    "offset_all",
    "gain_all",
    "offset_o0",
    "offset_o1",
    "gain_o0",
    "gain_o1",
):
    a, b, r = ratio(an.calibrate(rows_from_probs(Z[key]), settings))
    share = (r - ratio(an.calibrate(rows_from_probs(Z["none_all"]), settings))[2]) / (
        obs[2] - ratio(an.calibrate(rows_from_probs(Z["none_all"]), settings))[2]
    )
    print(
        f"{key:11s} model anchors: A {a:.4f} B {b:.4f} B/A {r:.4f}; share of the observed B/A excess over efficiency-only {share:+.2f}"
    )
