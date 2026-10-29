# Tuna joint response under fixed early-label maps

The [joint-response replay](joint-response-analysis.md) reconstructs six-bit histograms
from the retained jobs. This post-acquisition analysis asks how close the rotated
job's six-bit empirical distribution can get to the arithmetic average of its two
baseline histograms if an analyst applies any one fixed permutation and polarity
choice to the three decoded early labels. All terminal labels remain fixed.

The [exact record](early-label-map-analysis.json) contains all `3! * 2^3 = 48` scores
for each preparation case. If `C_rot` is the rotated 64-cell histogram after a map and
`C_before`, `C_after` are the baseline histograms, the empirical total variation is

    sum_cells |2 C_rot - C_before - C_after| / (4 * 4096).

Marginalizing to the three terminal labels cannot increase total variation. Since each
allowed map preserves all terminal labels, the terminal marginal is a lower bound for
every mapped six-bit distance.

| Retained case | Minimum mapped joint distance | Terminal marginal lower bound | Map attaining minimum |
|---|---:|---:|---|
| Nominal one | `600/16384 = 0.03662109375` | `232/16384 = 0.01416015625` | Identity |
| Nominal-zero prefix | `6310/16384 = 0.3851318359375` | `6286/16384 = 0.3836669921875` | Flip decoded early q6 |

The nominal-zero minimum stays large even under the best fixed early-label map because
the terminal marginal itself differs across the separate jobs. That finding excludes
an early-only relabeling as a complete explanation of those *empirical histogram
differences*. It does not identify why the terminal distributions differ or prove a
causal destination effect: the jobs occurred at different times, and preparation,
schedule, calibration, temporal drift, terminal reconstruction and physical behavior
remain potential contributors. More general association faults that affect terminal
labels are outside the 48-map family. The nominal-zero case's primary endpoint remains
**implementation route unavailable**. The optimum was selected after acquisition; the
distances have no uncertainty interval and do not change either frozen case verdict.

The [producer](../../../scripts/qi_tuna_early_label_maps.py) replays the upstream joint
analysis and checks its exact bytes before applying the maps. A separate scalar integer
calculation reproduced every one of the 96 scores. Focused tests include a pure
relabeling that reaches zero distance and a disjoint-terminal example that remains at
unit distance for every map.

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/qi_tuna_early_label_maps.py --check \
  docs/evidence/tuna-projector-geometry/early-label-map-analysis.json
```
