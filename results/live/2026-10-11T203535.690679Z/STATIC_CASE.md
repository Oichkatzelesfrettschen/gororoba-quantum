# Written case: the static job

Status: written, not approved, not submitted. The
[hardware queue](../../../gororoba_quantum/HARDWARE_PLAN.md#hardware-evidence-and-next-cases)
places the matched folded-QPE mechanism ladder first, the N = 21, a = 4
two-bit distribution test second, and this static-witness case third.
The first two cases remain unwritten. The N = 21 case also requires an
independent labeled-outcome calculation because its existing gate checks
sorted sampled masses. This case retains the static plan for approval
against a fresh matching calibration.

## What the run measures

Seventeen static PUBs at 4,096 shots (69,632 submitted PUB shots) in two
jobs, one per backend, from this dry run (`2026-10-11T203535.690679Z`, source
commit `96ca09a`, sources_modified=false, experiment digest
`297927aef46450b881786d936a77d1d2c44719325b419fe9c9ee95db631640e1`, record
SHA-256 `505ffcd719f966d59b26c34581d3d4a805f6292c1658f22b162713f90198c08e`,
QPY SHA-256
`0c2ac43cf99b1e3a03fc7c7099be70689c9c81f68549645f4241cb2e0d4d2d80`),
twirling and DD off, groups one CZ hop apart, so the first static measurement
compares directly with the calibration-derived noise model:

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

The dynamic job on ibm_kingston reads folded QPE at 0.715 against the
model's 0.899. Schedule-aware replay explains about a quarter of that gap
(record `2026-10-11T152922.787095Z`,
[ADJUDICATION.md](../2026-10-11T152922.787095Z/ADJUDICATION.md)). The static
case asks whether the listed static witnesses agree with their own
calibration-derived predictions on their selected replicas. Noise
simulation supplies those predictions; hardware supplies the observations
and any residual model error.

The static circuits, layouts, and backend allocation differ from the
dynamic pilot. Their residuals therefore measure static-workload model
conformance and cannot isolate the gate-level share of the folded-QPE gap.
Agreement supports the model for those static workloads; disagreement
identifies a static residual that needs its own diagnosis. Attribution of
the dynamic gap depends on the matched folded-QPE ladder and its control
assumptions.

## Expected seconds

69,632 submitted PUB shots. IBM's estimate model prices a job by circuit
duration plus repetition delay plus per-job overhead; with the backends'
250 us default repetition delay and these circuits' Target bounds of 783 to
3,877 dt (3.1 to 15.5 us at 4 ns per dt), execution is about 18 s, and the
dynamic job showed 2.3 s of charge outside circuit execution per job, so the
expectation is about 23 s across the two jobs. The literature range of 1,000
to 4,900 shots per second gives a planning range of 14 s to 70 s. The
`--max-execution-seconds 90` option sets a service ceiling of 90 s for each
job, so the two job ceilings total 180 s. The option does not impose a
90 s combined invocation cap. The dry run records 591 s remaining in the
rolling window; the runner refreshes remaining usage before each job.

## Exact command

Run from a clean checkout at the source commit above, in gororoba_quantum/,
after the owner approves this case:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --groups design_a,zero_divisor_fringe,design_c_8_1_4,design_c_16_1_8,design_c_32_1_16 \
  --max-execution-seconds 90 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-11T203535.690679Z \
  --approved-record-sha256 505ffcd719f966d59b26c34581d3d4a805f6292c1658f22b162713f90198c08e \
  --submit
```

The run re-reads the live calibration, recompiles, compares the fresh plan
with this record (digest, shots, policy with the 90 s per-job ceiling, versions,
instance, groups, backends, seeds, layouts, replica qubits, fused PUB
manifests, calibration, QPY bytes), stops with an approval_required record
on any difference, consumes this record's approval at the first batch, and
checks each batch's calibration again before its Sampler runs. A calibration
that has moved since this dry run stops the run; a fresh dry run and a
renewed case follow.
