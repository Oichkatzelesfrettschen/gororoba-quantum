# Written case: the static job

Status: written, not approved, not submitted. The program's next hardware
question is the mechanism of the folded-QPE model-hardware gap
(HARDWARE_PLAN.md, "Risks", the four-rung ladder), and this case ranks after
that ladder's case; it is retained so the static submission is ready the
moment it is the right spend.

## What the run measures

Seventeen static PUBs at 4,096 shots (69,632 submitted PUB shots) in two
jobs, one per backend, from this dry run (`2026-10-11T180802.703006Z`, source
commit `889062d`, sources_modified=false, experiment digest
`105bdde5efe95277b74f992987eca1a28169328c66f699383df34ef36d085e52`, record
SHA-256 `17f89d7e8c78f645c9e3eed46bd924a1c0c4532814c9b9bb636e1c80401cf6ae`,
QPY SHA-256
`161fa6a827bfe3f038c7f667a653790ba1d0089d6ff3f9cdcfee23538992e682`),
twirling and DD off so the first static measurement compares directly with
the calibration-derived noise model:

| group | backend | replicas | PUBs | noise-model prediction (execution-calibration replay at submission) |
|---|---|---:|---:|---|
| design A (octonion associator Z-string) | ibm_fez | 14 | 3 | p1 0.957 [0.953, 0.961], mirror-corrected 0.986 |
| zero-divisor fringe (design B dark/bright, design D eight-phase sweep) | ibm_kingston | 2 | 11 | dark/bright ratio 0.065, visibility 0.884, phase 0.003 [-0.115, 0.121] |
| design C 8 (associator Walsh spectrum, 3 qubits) | ibm_kingston | 2 | shared with the fringe | TVD to true 0.051, to the flip prediction 0.387, to the omit prediction 0.974 |
| design C 16 (4 qubits) | ibm_kingston | 2 | shared | TVD to true 0.094, flip 0.259, omit 0.924 |
| design C 32 (5 qubits) | ibm_kingston | 2 | shared | TVD to true 0.147 [0.067, 0.228], flip 0.225, omit 0.897 |

Each group's refuter is in HARDWARE_PLAN.md, "What each group claims and
what refutes it": a bright-level dark ratio or a fringe phase off zero
refutes the zero-divisor claim; a design C distribution nearer the flip or
omit prediction than the true spectrum refutes the associator-spectrum claim;
a design A p1 at the mirror level refutes the Z-string.

## Why noise simulation cannot answer it

The dynamic job on the same device read folded QPE at 0.715 against the
model's 0.899 with the excess in both semiclassical rounds and only a
quarter of it explained by scheduled idle time (record
`2026-10-11T152922.787095Z`, ADJUDICATION.md). The static circuits carry no
mid-circuit measurement, reset, or feed-forward, so their measured distance
from the replay isolates the gate-level share of that gap: a static job
that matches its replay within the replica intervals locates the dynamic
excess in the measure-reset-feed-forward segment, and one that misses by a
similar factor locates it in the gates. The model cannot say which; it has
no term that distinguishes the two.

## Expected seconds

69,632 submitted PUB shots. IBM's estimate model prices a job by circuit
duration plus repetition delay plus per-job overhead; with the backends'
250 us default repetition delay and these circuits' Target bounds of 783 to
3,877 dt (3.1 to 15.5 us at 4 ns per dt), execution is about 18 s, and the
dynamic job showed 2.3 s of charge outside circuit execution per job, so the
expectation is about 23 s across the two jobs. The literature range of 1,000
to 4,900 shots per second bounds it between 14 s and 70 s; the ceiling named
below, 90 s, is above the conservative bound and the service cancels either
job past it. The window holds 591 s.

## Exact command

Run from a clean checkout at the source commit above, in gororoba_quantum/,
after the owner approves this case:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --groups design_a,zero_divisor_fringe,design_c_8_1_4,design_c_16_1_8,design_c_32_1_16 \
  --max-execution-seconds 90 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-11T180802.703006Z \
  --approved-record-sha256 17f89d7e8c78f645c9e3eed46bd924a1c0c4532814c9b9bb636e1c80401cf6ae \
  --submit
```

The run re-reads the live calibration, recompiles, compares the fresh plan
with this record (digest, shots, policy with the 90 s ceiling, versions,
instance, groups, backends, seeds, layouts, replica qubits, fused PUB
manifests, calibration, QPY bytes), stops with an approval_required record
on any difference, consumes this record's approval at the first batch, and
checks each batch's calibration again before its Sampler runs. A calibration
that has moved since this dry run stops the run; a fresh dry run and a
renewed case follow.
