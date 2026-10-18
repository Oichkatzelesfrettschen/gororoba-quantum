# Ripple and rank-sector cases on ibm_kingston, and their runtime levers

Three submit-free dry runs priced Kingston replications of the ripple and
rank-sector families. Both families already ran on ibm_fez on 2026-10-13:
ripple in [2026-10-13T025444.603480Z](2026-10-13T025444.603480Z/collect.json)
(146 PUBs, 929 logical entries, 66 s charged) and rank sectors in
[2026-10-13T032011.664435Z](2026-10-13T032011.664435Z/collect.json) (36 PUBs,
176 logical entries, 31 s charged), with the results in sections 5 and 6 of
[CAMPAIGN_FINDINGS.md](CAMPAIGN_FINDINGS.md). The Kingston payloads are
unexecuted. Every case is UNAPPROVED and held: a calibration change after a
dry run makes the runner refuse submission, so an approval needs a fresh dry
run of the same command and its new record digest.

| Case | Record SHA-256 | Calibration | Jobs and shots | Nominal / stress (s) | Ceilings as invoked |
|---|---|---|---|---:|---:|
| [ripple](2026-10-14T113012.109467Z/UNAPPROVED_CASE.md) | `c10b99918f8c68fee09746bb5351b41bc7c3a5c104cd77329ee9dbd005c845db` | 03:51:35 PDT | 120 x 1024 and 26 x 4096 in two static jobs | 64.29 / 68.89 | 2 x 37 |
| [rank sectors, 8192 tier](2026-10-14T113945.518703Z/UNAPPROVED_CASE.md) | `e39aaccec1c6cd3c64cb034602ac52089688633a4b167d1d20143f5c88c38c8b` | 03:51:35 PDT | 15 x 1024, 19 x 4096 and 2 x 8192 in three static jobs | 34.84 / 41.74 | 3 x 25 |
| [rank sectors, 4096 tier](2026-10-14T204144.526374Z/UNAPPROVED_CASE.md) | `036237e0bae40cc7e65c3055a4a919300242b857f6c56d1ed5599600c7e211a1` | 13:06:33 PDT | 15 x 1024 and 21 x 4096 in two static jobs | 30.45 / 35.05 | 2 x 27 |

Ripple measures the signed sedenion box-kite phase atlas, four-qubit
associator-walk crossovers, the Design C ladder and readout controls (929
logical entries fused into 146 PUBs, 1138 preregistered endpoints). Rank
sectors measure selector-success norms of the four-dimensional sectors along
the dimension-32 rank path: persistent-kernel, exceptional-point and bright
probes (176 logical entries in 36 PUBs, 196 endpoints). Each case file states
its endpoints, the per-PUB cost ledger and the approval-only command.

The incremental question is transfer: whether the 84 box-kite, 8 sector and
12 pulse-difference contrasts that rejected their nulls on Fez reproduce on
a second Heron r2 processor under different placements and calibration.
Calibration noise simulation predicts conditional gate and readout behavior;
physical crosstalk, common disturbances, initialization, drift and scheduler
effects need hardware observations. A full rerun does not target the Fez
union-template walk discrepancy (lane 0 all-zero/all-one 0.064/0.046 on
hardware against 0.540/0.440 in replay); that needs its own diagnostic
progression separating preparation and readout, bound-but-inactive template
operations, active phase layers and mixer depth.

## Design search

The recorded 2026-10-12 flags reproduce on Kingston with tighter ceilings.
Ripple admits at a 37 s per-job ceiling; 36 s fails the latency stress
scenario on its 120-PUB job (36.27 s). A 512-shot tier goes unused because
every ripple contract needs at least 1024 shots. The static algebra families
reject replicas, because each row already packs distinct members across 35
to 47 physical qubits and their contracts are per PUB.

At 32768 noise-model samples the rank design fails at 4096 shots, and the
failure is the simulation allowance rather than the hardware shot count. The
sector 5, 6 and 7 pulse contrasts `t1d2 - t1d1` have point predictions
0.1193, 0.1163 and 0.1217 (03:51 calibration). Each is a difference of two
estimated success probabilities, so its simultaneous Hoeffding simulation
allowance is twice sqrt(ln(2/tail) / (2 n)), 0.0256 at n = 32768, which
leaves lower modeled values 0.0937, 0.0907 and 0.0961 below the 0.0997 the
directional contracts need (detection radius 0.0662 plus power radius
0.0335). The 8192-shot tier on the two PUBs that carry them admitted that
design. A declared sample of n = 131072 (`--model-shots 131072`, fixed
simulator seed, one run, no resampling) halves the allowance to 0.0128. On
the 13:06 calibration the same contrasts predict 0.1226, 0.1252 and 0.1215,
their lower modeled values 0.1098, 0.1124 and 0.1087 clear 0.0997, all 196
observables admit at 4096 shots, and the two 8192-shot PUBs join the 4096-shot
job. At a 25 s ceiling it fails only the latency stress check; the 27 s
ceiling the per-job model computes admits it. Neither the circuits, the
placements nor the estimator change.

## Runtime levers

[scripts/qpu_runtime_levers.py](../../scripts/qpu_runtime_levers.py) prices
every lever from the records' own ledgers and retains the result in
[kingston-algebra-runtime-levers.json](kingston-algebra-runtime-levers.json).
Gate core-260 replays it after verifying each case directory's
SHA256SUMS, the record digests above, the coupling-map edge digest and the
script's own digest; core-262 mutates a copied case (a whitespace-only
record.json change, one isa.qpy byte, one SHA256SUMS entry, a re-listed
record) and requires each mutation to fail. The admitted 4096-tier record
must reproduce the collapsed rank charges exactly, which binds the arithmetic
to a dry run. A PUB costs shots x (scheduled duration + repetition delay),
plus 2.3 s per job (4.6 s under stress); the 250 microsecond repetition delay
is 90.2 to 99.1 percent of each ripple PUB's cost.

| Program | Nominal (s) | Stress (s) | Uniform ceilings (s) | Per-job ceilings (s) |
|---|---:|---:|---:|---:|
| Ripple and rank as planned | 99.13 | 110.63 | 149 | 113 |
| Ripple and rank, 4096 tier | 94.74 | 103.94 | 128 | 106 |
| Co-batched: one job per shot tier across both families | 94.53 | 101.43 | 159 | 103 |
| Co-batched, rank 4096 tier | 90.14 | 94.74 | 110 | 96 |
| Fused as placed, pairs at least 2 hops apart (21 pairs) | 73.40 | 80.30 | 123 | 82 |
| Fused as placed, pairs at least 3 hops apart (19 pairs) | 75.49 | 82.39 | 123 | 84 |
| Fused after a joint placement of all 36 rank PUBs | 68.70 | 75.60 | 111 | 77 |
| As planned at a 100 us repetition delay | 48.29 | | | |
| Fused after a joint placement, 100 us | 33.06 | | | |
| As planned at a 50 us repetition delay | 31.35 | | | |
| Fused after a joint placement, 50 us | 21.19 | | | |

The levers in order of risk, lowest first:

1. **More noise-model samples.** The 4096-tier rank design saves 4.40 s
   nominal and one job, and its invocation ceilings fall from 75 to 54 s,
   with no change to hardware settings, circuits or estimator. It runs on the
   current runner today.
2. **Per-job ceilings.** Each covers its job's stress charge plus a declared
   scheduler residual of 2 us per shot, so a job that runs slightly long is
   not cancelled at its ceiling. A lower ceiling lowers reserved risk and
   campaign admission, not nominal time. The runner applies one
   `--max-execution-seconds` to every job of an invocation; per-job ceilings
   need a policy field, approval binding and a per-job `max_execution_time`.
3. **Co-batching.** The two families' PUBs of one shot tier share one Sampler
   job, keeping every circuit, placement and channel. The saving is job
   overhead, 2.3 s per removed client job, and it holds only when each client
   job runs as one sub-job: IBM bills overhead per sub-job (about 2 s each)
   and splits a primitive job that is too large for the execution engine
   ([estimate-job-run-time](../../docs/notes/ibm-runtime-execution-guides.md)).
   The retained usage of an executed job decides the saving. The client-side
   Sampler takes one shot count per job, so shot tiers stay separate jobs.
4. **Fusion.** A rank PUB rides in a ripple PUB of its shot tier. A per-tier
   maximum matching finds 21 rank PUBs whose host's current qubits are at
   least two hops away (1 of 15 at 1024 shots, 20 of 21 at 4096) and 19 at
   three hops; fusing all 36 saves 30.43 s, of which 25.34 s is shared
   repetition delay, 0.49 s overlapping circuit time and 4.6 s job overhead.
   Graph distance and the maximum of component durations are planning
   inputs, not a timing, readout-resource or crosstalk certificate. Fused
   rows need joint compilation, the actual register mapping,
   calibration-admitted couplers and packed and isolated controls whose cost
   enters the price; the sector 6 power margin of 0.020 at 8192 shots leaves
   little room for cross-family disturbance. Maximum-cardinality matching is
   not minimum-cost matching; a production planner weighs shot uplift,
   scheduled duration, placement risk and control cost.
5. **Shorter repetition delay.** IBM's
   [repetition-rate guide](https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution)
   states that a lower `rep_delay` raises state-preparation error, that the
   supported range differs by QPU and changes over time
   (`backend.rep_delay_range`), and that neither PUB order nor single-batch execution of a job is
   guaranteed. At 100 and 50 us the planned program shrinks by 51 and 68
   percent and joint fusion at 50 us by 79 percent against the plan.

The repetition-delay screening workload is priced, not qualified.
`execution.rep_delay` is a Sampler-wide option, so three PUBs of 2048 shots
at 250, 100 and 50 us with a declared 20 us circuit are three jobs: 9.73 s
nominal (6.9 s of it job overhead) and 16.63 s under stress, under 7 + 6 + 6
s of ceilings. Its three diagnostics (initialization error after a shot
ending in `|1>`, lag-one correlation, spectator Ramsey phase) have no
declared score, no sensitivity map to the sector contrasts, no uncertainty
propagation and no acceptance rule yet, so the workload cannot admit a
shorter delay. For scale, a direct two-arm comparison at p = 0.1163 and 2048
shots per arm has a 95 percent half-width of 0.0196; a quarter of the 0.020
margin, 0.005, needs about 31,600 shots per arm, and the 4096-tier design's
sector 5-7 margins (0.009 to 0.013) tighten the tolerance further.
Adjacent entries of one PUB's shot array are not guaranteed adjacent
physical executions, so an inter-shot memory test needs an execution-history
construction inside one circuit (for example a conditional preparation
followed by a re-measurement) or a narrower reading, and a lag-one statistic
does not bound longer-range dependence.

## Budget

135 s is the owner's planning bound for 2026-10-14; it appears in no
ledger, and authorization is each case's approval with its record digest.
With per-job ceilings the co-batched 4096-tier program (96 s) plus the
coherence-window case `results/live/2026-10-14T055711.938217Z` (18 s, an
ibm_fez case) is 114 s. As the runner invokes them today, ripple (74 s),
4096-tier rank (54 s) and the coherence case (18 s) total 146 s of ceilings,
above the bound, so one of them waits or per-job ceilings land first. A
short-delay program is conditional: running the screening workload and then
falling back to the default delay costs 19 + 96 + 18 = 133 s of ceilings, so
the policy is screen, then either admit a shortened workload with its own
recomputed ceilings or stop, never reserving both.
