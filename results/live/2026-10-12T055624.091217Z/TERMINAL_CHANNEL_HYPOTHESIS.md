# A common terminal postprocessing channel fails to repair the replay

The retained terminal marginals exclude one additional common binary
stochastic postprocessing channel as a complete repair of the replay
discrepancy, conditional on the sampling assumptions below. Binary-channel
contraction supplies the mathematical mechanism; its application to the
retained hardware and replay counts supplies the experiment-specific finding.
The check uses existing evidence and consumes zero additional QPU seconds.

## Hypothesis and exact inequality

Let `p` denote the replay probability of terminal bit one. Any binary
stochastic channel maps that marginal to

```text
K(p) = a * (1 - p) + b * p,  0 <= a,b <= 1.
|K(p1) - K(p3)| = |b - a| * |p1 - p3| <= |p1 - p3|.
```

The common-channel hypothesis requires the same `a,b` for both members.
The inequality allows bit inversion and arbitrary asymmetric assignment
probabilities. It cannot increase separation between the input marginals.

The no-feed-forward s1 and s3 members both terminate on physical qubit 93.
Their expected terminal bits differ, so s1 probability of one is the
complement of its terminal correctness; s3 probability of one is its
correctness directly.

| Terminal probability of one | s1 | s3 | Absolute separation |
|---|---:|---:|---:|
| Hardware | 0.36181640625 | 0.5994873046875 | 0.2376708984375 |
| CPU replay | 0.4964599609375 | 0.4952392578125 | 0.001220703125 |

The hardware numerators are 2964 and 4911 out of 8192. The
[record](record.json) fixes 8192 shots. `collect()` in the recorded
`c6b8a79e8981` source reads that count and passes it to replay;
`local_compute.run()` passes the count directly to Aer. All sixteen replay
terminal means lie on the 1/8192 grid. The source-closure and raw decoder
checks remain separate provenance gates.

## Simultaneous finite-sample bound

Take all sixteen terminal observables from hardware and all sixteen from
replay as the fixed family of 32 bounded sample means. For separate
supplemental alpha 0.05 and `n=8192`, the union of two-sided Hoeffding bounds
has simultaneous coverage at least 0.95, with radius

```text
r = sqrt(log(2 * 32 / 0.05) / (2 * 8192))
  = 0.02089696308600546.

hardware_separation_lower = 0.2376708984375 - 2*r
                          = 0.19587697226548909
replay_separation_upper   = 0.001220703125 + 2*r
                          = 0.04301462929701092
remaining_violation      = 0.15286234296847817
```

The positive 15.2862-percentage-point margin contradicts contraction on the
simultaneous event. [terminal-channel-check.json](terminal-channel-check.json)
records the inputs, arithmetic, and record/collection hashes.

The sampling assumption requires independent, stationary repetitions within
each hardware or Monte Carlo stream. Dependence between streams or PUBs
requires no additional independence assumption for the union bound.
Calibration continuity and the exploratory shot-order summaries do not prove
within-stream stationarity or independence.

The all-32 simultaneous event permits choosing this pair after inspecting
these fixed means. It excludes neither additional-run search bias nor
postselection from redefining observables, filtering shots, or fitting a new
simulator to the same data. The supplemental family has its own alpha 0.05;
combining it with the original twelve-contrast 0.05 family gives at least
0.90 joint coverage by the union bound, not an automatic 0.95 joint claim.

## Interpretation boundary

Replay already contains modeled readout noise. The rejected class appends
one common stochastic channel to those noisy terminal marginals. Replacing
the modeled readout channel is a different hypothesis and can expand
separations relative to already-noisy inputs. The result therefore supplies
neither a general exclusion of readout-only explanations nor attribution to
reset, measurement, controller, routing, or coherent error. A shared physical
readout site motivates the common-channel hypothesis but does not establish
context independence.

A next model must explain the labeled joint distributions and pass separate
validation. Adding more physical samples cannot make an incompatible fixed
channel fit these central estimates. The [main report](ANALYSIS.md) preserves
the broader control, routing, and timing limits.

## Reproduce the arithmetic

Run from the repository root after the raw decoder and checksum gates pass:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" - <<'PYTHON'
import json
import math
from pathlib import Path
run = Path("results/live/2026-10-12T055624.091217Z")
record = json.loads((run / "record.json").read_text())
groups = json.loads((run / "collect.json").read_text())[1:]
streams = []
for kind in ("measured_statistics", "replayed_statistics"):
    values = {key: value for group in groups
              for key, value in group[kind]["summary"].items()
              if key.endswith("_terminal_correct")}
    if len(values) != 16:
        raise ValueError("the fixed family requires sixteen terminal means")
    streams.append([1 - values["qpe_no_feed_forward_s1_terminal_correct"],
                    values["qpe_no_feed_forward_s3_terminal_correct"]])
radius = math.sqrt(math.log(64 / 0.05) / (2 * record["shots"]))
hardware_lower = abs(streams[0][0] - streams[0][1]) - 2 * radius
replay_upper = abs(streams[1][0] - streams[1][1]) + 2 * radius
print(radius, hardware_lower, replay_upper, hardware_lower - replay_upper)
PYTHON
```
