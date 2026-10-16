# Coherent error families on lane 4 of the Fez and Kingston atlas runs

`result.json` is `scripts/atlas_coherent_families.py --runs
ibm_fez,ibm_kingston --lanes 4 --out` (run from `gororoba_quantum/`). It fits
the frame-detuning, CZ-phase, static-ZZ (two frames), SX-amplitude and
axis-tilt families to the fringe phase offsets of lane 4. The data are the
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

## Gate

Gate core-329 runs `--check ../docs/evidence/atlas_coherent_families/result.json
--runs ibm_fez,ibm_kingston --lanes 4` from `gororoba_quantum/` in normal and
optimized Python. It recomputes both lanes, with every resimulation, and
compares every number within 1e-6 absolute or 1e-9 relative. It runs in the
full tier, since one worker needs several minutes per mode.
