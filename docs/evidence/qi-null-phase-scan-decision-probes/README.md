# Decision-rule probes of the Tuna-17 null phase scan

Records behind the coverage, null and q4 statements of
[the phase-scan case](../../../results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/CASE.md) and the
calibration of its consistency margin. Evidence class: numerical simulation at expected values of the case's
forward model (`scripts/qi_pathion_null_phase_scan_cases.py`); no shot, no provider job and no random draw enters
the three probes.

Run from the repository root under the pinned interpreter:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 \
	"$PYTHON" -B docs/evidence/qi-null-phase-scan-decision-probes/probe_decision.py MODE
```

The probes read the damped law tables the generator builds on first use (3,009 s on a 12-thread host) and
caches under `GOROROBA_SCAN_TABLES`.

| Mode | Output | Content |
|---|---|---|
| `coverage` | `coverage.json` | the q12 truth (-0.15 rad) and the coupler truth (-0.25 rad) at each of the 49 multiples of the retained CZ damping the fit computes: center visibility and label |
| `nulls` | `nulls.json` | no injected phase, a selector flip of 0.0166 to 0.05 beside CZ phase, pulse phase or CZ amplitude damping of 0.04 to 0.13 per qubit (48 combinations): label, center contrast, world sums |
| `q4-zero` | `q4_zero.json` | the q4 angle of zero contrast by root finding on fractional q4 steps against the weighted line through the four q4 arms, for q12 phases of +-0.15 and +-0.18 rad and coupler phases of +-0.25 rad |

`calibration.json` holds the label counts of 500 simulated series per scenario at consistency margins 0 and 6.63,
seeded from value 0 of `docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json` through
`operating_characteristics(index=0, margin=m)`, under the decision with two error worlds (q12 and coupler) that
commit fc9c84b12 holds. It was written at 2026-11-15T08:44Z, before value 1 recorded that decision's
characteristics; the file times are the only record of that order. At margin 0 a single mechanism read
`phase_mixed` in up to 94 of 500 series, at 6.63 in at most 7, and the case kept 6.63.

`separation_calibration.json`, written by `calibrate_separation.py`, holds the label counts of 500 simulated series
per scenario of `operating_characteristics()` at scaled separations 30, 35 and 40, seeded from value 9 of the same
draw, with every other rule as the generator holds it. The script keeps the least separation under which no
scenario reads a deciding label of another world; all three read none, so it chose 30. `separation_30_value_10.json`
holds the record at 30 on value 10: the null with selector flip 0.025 and CZ phase damping 0.13 read `q12_phase`
in 1 of 500 series. The owner then fixed the separation at 40, recorded on value 11 with no wrong label
(`readout-flip/prediction_value11.json`); `prediction.json` of the case records rule R6, which keeps it, on value
12.

Exploratory draws on a fixed pseudo-random seed (no QRNG value) motivated the scaling: no-phase nulls outside the
noise models (a selector flip of 0.0166 to 0.05 beside CZ phase damping of 0.08 to 0.16 or pulse phase damping of
0.06 to 0.12) read `q12_phase` while fitting the q12 world at 1.26 to 1.97 per degree of freedom, leading the next
error world by up to 45 unscaled and 29.0 scaled; single q12 and coupler phases at damping up to 1.25 times the
retained strength led by 24 to 384 scaled. Value 8 had recorded the decision with an unscaled separation of 25,
under which two of those nulls read `q12_phase` in 29 and 48 of 500 series; the writes on values 10 and 11
replaced that record, and only these counts, read in the session, remain.

`readout-flip/` holds the final design round: rule R5 beside a readout flip of the selector, the flip fitted as a
nuisance parameter (rule R6, which the case records on value 12 of the draw), drifting flips and truths, the
refuted least-contrast gate, and the regressions that tie the R6 generator to the value-11 record of R5. Its
README gives the files and findings.
