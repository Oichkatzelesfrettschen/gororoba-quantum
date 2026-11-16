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
	"$PYTHON" -B docs/evidence/qi-null-phase-scan-decision-probes/probe_decision.py MODE [--out DIR]
```

`--out` names the directory of the output file (default: this directory). A mode without a suffix runs the current
rule R6, which fits the readout flip over `FLIP_GRID`, and writes an `_r6` file; a mode with the `-r5` suffix pins
rule R5 (`flips=(0.0,)`, the flip fixed at 0) and is the only writer of the retained `coverage.json` and
`nulls.json`.

The probes read the damped law tables the generator builds on first use (3,009 s on a 12-thread host) and
caches under `GOROROBA_SCAN_TABLES`.

| Mode | Output | Content |
|---|---|---|
| `coverage` | `coverage_r6.json` | the q12 truth (-0.15 rad) and the coupler truth (-0.25 rad) at each of the 49 multiples of the retained CZ damping the fit computes: center visibility and label, under rule R6 |
| `coverage-r5` | `coverage.json` | the same probe under rule R5 |
| `nulls` | `nulls_r6.json` | no injected phase, a selector flip of 0.0166 to 0.05 beside CZ phase, pulse phase or CZ amplitude damping of 0.04 to 0.13 per qubit (48 combinations): label, center contrast, world sums, under rule R6 |
| `nulls-r5` | `nulls.json` | the same probe under rule R5 |
| `q4-zero` | `q4_zero.json` | the q4 angle of zero contrast by root finding on fractional q4 steps against the weighted line through the four q4 arms, for q12 phases of +-0.15 and +-0.18 rad and coupler phases of +-0.25 rad; no decision runs, so the rule does not enter |

`coverage.json` and `nulls.json` hold the probes with the readout flip fixed at 0 (rule R5). `coverage_r6.json` and
`nulls_r6.json` hold the same two probes under the generator that fits the flip (rule R6): the q12 truth reads
`q12_phase` through multiple 2.0 (R5: 2.125), the coupler truth through 1.875 as before, and the 48 nulls read
`exact_parabola` (42) or `offset_absent` (6) where R5 read `none_adequate` (29), `phase_unresolved` (5),
`exact_parabola` (8) or `offset_absent` (6); `q4_zero.json` is unchanged. `analyzer_crosscheck.py` compares the
generator's laws (`elementary_error_laws.py`) with the histogram-fit model of `gate_noise_histogram_fit.py` on six
arms of the case and reports them in `analyzer_crosscheck.log`: a q12 z rotation, CZ damping and pulse damping
agree to 2e-16, while a conditional phase and a q8 rotation differ by 0.032 to 0.048 in outcome probability, since
the histogram model applies them at every CZ that touches the qubit and the case at coupler 8-12 alone.

`calibration.json` holds the label counts of 500 simulated series per scenario at consistency margins 0 and 6.63,
seeded from value 0 of `docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json` through
`operating_characteristics(index=0, margin=m)`, under the decision with two error worlds (q12 and coupler) that
commit fc9c84b12 holds. It was written at 2026-11-15T08:44Z, before value 1 recorded that decision's
characteristics; the file times are the only record of that order. At margin 0 a single mechanism read
`phase_mixed` in up to 94 of 500 series, at 6.63 in at most 7, and the case kept 6.63.

`separation_calibration.json`, written by `calibrate_separation.py r5`, holds the label counts of 500 simulated series
per scenario at scaled separations 30, 35 and 40, seeded from value 9 of the same draw, under rule R5 (readout flip
fixed at 0, the consistency margin of the generator) on the 25 scenarios that existed then, in their historical order
(a scenario's position seeds its draw). The `r5` mode passes that rule, scenario list and series count explicitly
and writes the retained file byte for byte (SHA-256 `53c1d77995c053ddcc7650470d8bfe9506f8e4e9138fa8b4cf4d993a4349d2d4`);
`calibrate_separation.py r6 --index N` recalibrates under the current rule through `operating_characteristics()`
with its defaults and writes `separation_calibration_r6.json`. The script keeps the least separation under which no
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
