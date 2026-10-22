# Coherent error families on the Fez and Kingston atlas runs

`result.json` is the output of `scripts/atlas_coherent_families.py --runs
ibm_fez,ibm_kingston --lanes all` on a Kaggle CPU kernel, retained byte for
byte from `results/kaggle/2026-10-16T222749Z-gororoba-atlas-coherent-families`
(gate core-334 compares the two). It fits the frame-detuning, CZ-phase,
static-ZZ (two frames), SX-amplitude and axis-tilt families to the fringe
phase offsets of all 14 lanes; gate core-329 recomputes lane 4 of both runs
on CPU. The lane-4 tables below describe the gated case. The data are the
Fez run `results/live/2026-10-13T025444.603480Z` (12 edges, qubits 50, 51,
52, 58, 71) and the Kingston run `results/live/2026-10-15T031229.371738Z`
(10 edges, qubits 138, 150-153; 2 edges span a calibration identity change
and are excluded). The script docstring defines the observables, the
leave-one-edge-out scores, the floors and the falsifiers.

## Inputs

`inputs` names the 301 files the computation read, each with its sha256:

- both runs' `record.json`, `isa.qpy` and `raw/*/pub_*.json`;
- the Fez `results/ripple/measured-ripple.json` and the Kingston
  `collect.json`;
- the retained `docs/evidence/atlas_detuning_map/result.json`, against
  which the Fez forward detuning and CZ slopes are checked;
- the two calibration snapshots under `docs/evidence/calibration/history/`
  from which `gate_bounds` reads the sx and CZ errors.

`--check` requires every named file to hold its sha256 before it recomputes.
It also stops when the rerun reads a file the result does not name. A
re-collection that rewrites `collect.json` therefore fails the gate instead
of moving the result.

## Result

Leave-one-out phase RMS in rad, linear / resimulated, with each model's
leave-one-out noise floor and its largest fold condition number:

| Model | Fez | floor | fold cond | Kingston | floor | fold cond |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| lane mean | 0.136 | 0.030 | 1 | 0.060 | 0.027 | 1 |
| detuning | 0.103 / 0.104 | 0.044 | 72 | 0.109 / 0.140 | 0.045 | 100 |
| CZ phase | 0.091 / 0.091 | 0.039 | 10 | 0.082 / 0.082 | 0.036 | 12 |
| ZZ, partner-in-0 frame (`zz`) | 0.076 / 0.077 | 0.038 | 12 | 0.068 / 0.068 | 0.037 | 15 |
| ZZ, symmetric frame (`zz_symmetric`) | 0.182 / 0.179 | 0.038 | 4.4 | 0.160 / 0.274 | 0.034 | 6.8 |
| SX amplitude | 0.192 / 0.192 | 0.037 | 3.5 | 0.241 / 0.311 | 0.034 | 4.0 |
| axis tilt | 0.118 / 0.114 | 0.041 | 6.2 | 0.099 / 0.104 | 0.044 | 9.9 |
| detuning + CZ phase | 0.264 / 0.304 | 0.076 | 3.6e4 | unidentified | | 2.5e5 |
| detuning + `zz` | 0.166 / 0.191 | 0.122 | 1.5e3 | unidentified | | 3.4e3 |
| detuning + `zz_symmetric` | 0.159 / 0.191 | 0.123 | 1.0e3 | unidentified | | 3.5e3 |
| detuning + SX amplitude | 0.132 / 0.135 | 0.074 | 2.1e4 | 0.168 / 0.207 | 0.113 | 2.4e4 |
| detuning + axis tilt | 0.293 / 0.725 | 0.111 | 4.4e4 | unidentified | | 4.2e4 |
| detuning + constant | 0.125 / 0.128 | 0.048 | 4.1e3 | 0.132 / 0.167 | 0.054 | 5.0e3 |
| CZ phase + constant | 0.087 / 0.086 | 0.041 | 26 | 0.122 / 0.123 | 0.043 | 45 |
| `zz` + constant | 0.074 / 0.075 | 0.040 | 2.0e3 | 0.097 / 0.097 | 0.042 | 1.7e3 |
| `zz_symmetric` + constant | 0.174 / 0.162 | 0.041 | 4.7e3 | 0.076 / 0.078 | 0.039 | 9.1e3 |
| SX amplitude + constant | 0.182 / 0.174 | 0.039 | 3.9 | 0.054 / 0.057 | 0.035 | 4.1 |
| axis tilt + constant | 0.137 / 1.492 | 0.082 | 4.4e5 | 0.179 / 1.336 | 0.092 | 4.7e5 |

On Kingston, the lane fits 10 edges, so each fold trains on 9. Detuning + CZ
phase and both detuning + ZZ models carry 9 columns, and detuning + axis
tilt carries 10, so every fold of these models interpolates its training
edges. They are reported unidentified, with no score.

The two ZZ frames differ by a zeta/2 detuning on each qubit of the coupler
(`zz_symmetric` slopes minus `zz` slopes equal (D_a + D_b)/2 of the central
detuning slopes to 3.6e-8 rad/kHz on Fez). Paired with detuning, the two
frames span the same column space only when the detuning block uses central
slopes; with those, the Fez linear scores agree, 0.15604 against 0.15608.
The script fits detuning on the forward slope, the definition of the
retained detuning map. That slope differs from the central one by at most
1.2e-5 rad/kHz, and at a fold condition of about 1e3 this moves the two
joint scores to 0.166 and 0.159.

The rows without a constant equal the retained detuning map's lane 4 where
the two overlap (detuning, CZ phase, detuning + CZ phase on Fez). The
`_plus_mean` rows and the two ZZ frames widen the model set, so the lowest
score in each column is an exploratory selection.

## All 14 lanes

Leave-one-out phase RMS in rad of the lane mean and each single family
(linear), with the best single family's ratio to its own noise floor:

| Backend | Lane | Edges | lane mean | `detuning` | `cz_phase` | `zz` | `zz_symmetric` | `sx_amplitude` | `axis_tilt` | best single, LOO / floor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fez | 0 | 12 | 0.154 | 0.180 | 0.214 | 0.201 | 0.195 | 0.174 | 0.151 | `axis_tilt`, 2.70 |
| fez | 1 | 12 | 0.238 | 0.120 | 0.180 | 0.091 | 0.379 | 0.345 | 0.078 | `axis_tilt`, 1.97 |
| fez | 2 | 12 | 0.212 | 0.093 | 0.136 | 0.059 | 0.467 | 0.437 | 0.101 | `zz`, 1.78 |
| fez | 3 | 12 | 0.173 | 0.114 | 0.165 | 0.125 | 0.192 | 0.184 | 0.124 | `detuning`, 2.44 |
| fez | 4 | 12 | 0.136 | 0.103 | 0.091 | 0.076 | 0.182 | 0.192 | 0.118 | `zz`, 1.98 |
| fez | 5 | 12 | 0.130 | 0.113 | 0.130 | 0.144 | 0.202 | 0.208 | 0.062 | `axis_tilt`, 1.31 |
| fez | 6 | 12 | 0.129 | 0.074 | 0.151 | 0.074 | 0.110 | 0.288 | 0.122 | `zz`, 2.05 |
| kingston | 0 | 10 | 0.159 | 0.100 | 0.216 | 0.136 | 1.125 | 0.581 | 0.287 | `detuning`, 2.30 |
| kingston | 1 | 10 | 0.077 | 0.063 | 0.098 | 0.077 | 0.394 | 0.234 | 0.092 | `detuning`, 1.68 |
| kingston | 2 | 10 | 0.119 | 0.049 | 0.054 | 0.048 | 0.169 | 0.131 | 0.094 | `zz`, 1.38 |
| kingston | 3 | 10 | 0.111 | 0.151 | 0.174 | 0.148 | 0.165 | 0.247 | 0.163 | `zz`, 4.01 |
| kingston | 4 | 10 | 0.060 | 0.109 | 0.082 | 0.068 | 0.160 | 0.241 | 0.099 | `zz`, 1.85 |
| kingston | 5 | 10 | 0.230 | 0.164 | 0.178 | 0.163 | 0.371 | 0.325 | 0.266 | `zz`, 4.28 |
| kingston | 6 | 10 | 0.075 | 0.106 | 0.406 | 0.127 | 0.338 | 1.031 | 0.295 | `detuning`, 2.77 |

- The partner-in-0 ZZ frame scores below the symmetric frame on 13 of 14
  lanes in the linear fit and on all 14 resimulated, by a median factor of
  2.4, and the symmetric frame beats the lane mean on one lane. The offsets
  carry no zeta/2 detuning alongside the coupler term, which is the frame in
  which qubit frequencies are calibrated with the partner in |0>; rated
  likely, since it compares two fitted models, and a conditional Ramsey with
  the partner in |0> measures it directly.
- The best single family is `zz` on 7 lanes, `detuning` on 4 and
  `axis_tilt` on 3; `cz_phase` and `sx_amplitude` are never best, and
  `sx_amplitude` never beats the lane mean.
- Two lanes reach the 1.5x-floor criterion with a single family (Fez lane 5
  with `axis_tilt`, Kingston lane 2 with `detuning` and with `zz`). On the
  other twelve, every single family stays above it, the lowest ratio per lane
  ranging from 1.68 to 3.70, so no single coherent family accounts for the
  offsets. The ratio column above belongs to the family with the lowest
  leave-one-out RMS, which on four lanes differs from the family with the
  lowest ratio.
- The selection over families is exploratory: the lowest score in a row is
  chosen after the fact.

## Cross-substrate agreement

The host recompute of lane 4 and the Kaggle kernel's lane 4 differ in four
numbers: two below 5e-16 rad and two by one unit of the last retained
decimal (a fold condition number near 4.4e5 and a predicted log contrast in
the ill-conditioned `axis_tilt_plus_mean` model). CI's OpenBLAS build moves
five resimulated contrast values of that model (Fez and Kingston lane 4) by
one to three units (largest 3e-6 on a predicted log ratio of -2.22),
reproduces its fitted parameters to all six decimals, and reproduces every
other model exactly. A least-squares
solution with a nonzero residual carries roundoff of order eps * kappa^2,
and Fez lane 4's worst fold has kappa = 4.4e5, so eps * kappa^2 is 4.3e-5
relative. The self-test (core-325) measures that law with
`lsq_roundoff_scaling()`: on a 12 x 6 design with a residual of a tenth of
the signal, perturbed at eps, the solution drift stays inside eps * kappa^2
* |x| and exceeds 50 * eps * kappa * |x| at kappa 1e5 and 4.4e5 (measured
0.2 % of the first and about 200 to 700 times the second on both the AOCL
and OpenBLAS builds). `--check` therefore allows one rounding unit, 1.5e-6,
1e-6 relative on condition numbers, and inside each model eps * kappa^2 *
|value| on every other value, kappa the model's retained fold_condition_max
for outputs of the leave-one-out fits (the leave-one-out RMS and noise
floor values and the contrast block) and its full-design condition for the
full-fit parameters and RMS values. On Fez lane 4's `axis_tilt_plus_mean`
that is 4.3e-5 relative for the leave-one-out outputs and 1.1e-6 (full
condition 7.0e4) for the full fit; a kappa below about 8e4 keeps the
one-unit floor for values near 1. The probe bounds the drift normwise, against the solution's largest
component. `--check` applies the bound to each parameter and RMS value's
own magnitude, and to each resimulated contrast vector (`predicted_log_ratio`)
normwise, against that vector's largest entry, because every prediction
inherits the leave-one-out solution's normwise drift.

Measured on lane 4 of both backends against the retained Kaggle result:
- The build host's AOCL numpy and CI's scipy-openblas 0.3.34 numpy (Python
  3.14.7, requirements.txt pins) reproduce every fitted parameter exactly.
- Their least-squares designs differ by at most 3.5e-13 relative (about
  1585 eps, median 1.3e-14).
- Perturbing each design at eps leaves every parameter component at least
  1640 times inside its per-value tolerance.
- Under the componentwise rule, OpenBLAS moved Kingston's near-zero
  prediction `axis_tilt_plus_mean` `predicted_log_ratio[0]` (-0.060228) by
  one unit against a 2.95e-6 tolerance.
- Under the normwise contrast rule, the smallest margin, tolerance over
  difference, is 31.7 on OpenBLAS and 95 on AOCL, both at Fez
  `predicted_log_ratio[1]`. `--check` prints it per lane.

A future substrate whose design moves by the largest measured difference on
every model would leave the thinnest parameter solve, the `axis_tilt_plus_mean`
full fit, with a margin near 1. That is the residual this rule carries. The host also reproduced all seven Fez lanes of the Kaggle
result under that check.

## Gate

Gate core-329 runs `--check ../docs/evidence/atlas_coherent_families/result.json
--runs ibm_fez,ibm_kingston --lanes 4` from `gororoba_quantum/`. It recomputes both lanes, with every resimulation, and
compares every number within the tolerance above. It runs in the
full tier, since one worker needs several minutes per mode.
