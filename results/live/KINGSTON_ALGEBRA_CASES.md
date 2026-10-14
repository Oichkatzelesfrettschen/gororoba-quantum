# Ripple and rank-sector cases on ibm_kingston, and their runtime levers

Two submit-free dry runs priced the repository's never-executed Cayley-Dickson
families against fresh ibm_kingston calibration (2026-10-14T03:51:35-07:00)
and source `c84c490` with `sources_modified=false`. Both cases are
UNAPPROVED and held: a calibration change after the dry run makes the runner
refuse submission, so an approval needs a fresh dry run of the same command
and its new record digest.

| Case | Record SHA-256 | What it measures | Jobs and shots | Nominal / stress (s) | Ceilings as planned |
|---|---|---|---|---:|---:|
| [ripple](2026-10-14T113012.109467Z/UNAPPROVED_CASE.md) | `c10b99918f8c68fee09746bb5351b41bc7c3a5c104cd77329ee9dbd005c845db` | the signed sedenion box-kite phase atlas, four-qubit associator-walk crossovers, the Design C ladder and readout controls: 929 logical entries fused into 146 PUBs, 1138 preregistered endpoints | 120 x 1024 and 26 x 4096 in two static jobs | 64.29 / 68.89 | 2 x 37 |
| [rank sectors](2026-10-14T113945.518703Z/UNAPPROVED_CASE.md) | `e39aaccec1c6cd3c64cb034602ac52089688633a4b167d1d20143f5c88c38c8b` | selector-success norms of the four-dimensional sectors along the dimension-32 rank path: persistent-kernel, exceptional-point and bright probes, 176 logical entries in 36 PUBs, 196 endpoints | 15 x 1024, 19 x 4096 and 2 x 8192 in three static jobs | 34.84 / 41.74 | 3 x 25 |

Calibration noise simulation admits each design and predicts conditional
gate and readout behavior; physical crosstalk, common disturbances,
initialization, drift and scheduler effects need the hardware observations,
which is why simulation cannot answer either question. Each case file states
its endpoints, the per-PUB cost ledger and the approval-only command.

## Design search

The recorded 2026-10-12 flags reproduce on today's calibration with tighter
ceilings. Ripple admits at a 37 s per-job ceiling; 36 s fails the latency
stress scenario on its 120-PUB job (36.27 s). A 512-shot tier goes unused
because every ripple contract needs at least 1024 shots. Rank sectors fail at
4096 shots: today's model predicts the sector 5, 6 and 7 pulse contrasts
`t1d2 - t1d1` at 0.1193, 0.1163 and 0.1217, and their lower modeled values
after the 0.0256 simulation allowance, 0.0937, 0.0907 and 0.0961, fall below
the 0.0997 the directional contracts need (detection radius 0.0662 plus power
radius 0.0335); an 8192-shot tier on the two PUBs that carry them admits the
design. The static
algebra families reject replicas, because each row already packs distinct
members across 35 to 47 physical qubits and their contracts are per PUB.

## Runtime levers

[scripts/qpu_runtime_levers.py](../../scripts/qpu_runtime_levers.py) prices
every lever from the two records' own ledgers and retains the result in
[kingston-algebra-runtime-levers.json](kingston-algebra-runtime-levers.json)
(gates core-260 and core-261 replay it). A PUB costs shots x (scheduled
duration + repetition delay), plus 2.3 s per job (4.6 s under stress); the
250 microsecond repetition delay is 90.2 to 99.1 percent of each ripple PUB's
cost.

| Program | Nominal (s) | Stress (s) | Uniform ceilings (s) | Per-job ceilings (s) |
|---|---:|---:|---:|---:|
| Ripple and rank as planned | 99.13 | 110.63 | 149 | 113 |
| Co-batched: one job per shot tier across both families | 94.53 | 101.43 | 159 | 103 |
| Fused as placed, pairs at least 2 hops apart (21 pairs) | 73.40 | 80.30 | 123 | 82 |
| Fused as placed, pairs at least 3 hops apart (19 pairs) | 75.49 | 82.39 | 123 | 84 |
| Fused after a joint placement of all 36 rank PUBs | 68.70 | 75.60 | 111 | 77 |
| As planned at a 100 us repetition delay | 48.29 | | | |
| Fused after a joint placement, 100 us | 33.06 | | | |
| As planned at a 50 us repetition delay | 31.35 | | | |
| Fused after a joint placement, 50 us | 21.19 | | | |

- Per-job ceilings change no data. Each covers its job's stress charge plus a
  declared scheduler residual of 2 us per shot, so a job that runs slightly
  long is not cancelled at its ceiling: ripple 37 + 33 s, rank 9 + 25 + 9 s.
  The runner applies one `--max-execution-seconds` to every job of an
  invocation; per-job ceilings need a policy field, approval binding and a
  per-job `max_execution_time`.
- Co-batching keeps every circuit, placement and channel and only merges the
  two families' PUBs of one shot tier into one Sampler job: five jobs become
  three and 4.6 s of overhead go. With the coherence-window case retained at
  `results/live/2026-10-14T055711.938217Z` (2 x 9 s on ibm_fez) its
  ceilings total 121 s, inside the owner's stated 135 s allotment for
  2026-10-14, which no ledger records.
- Fusion lets a rank PUB ride in a ripple PUB of its shot tier, and two
  ripple PUBs rise from 4096 to 8192 shots to host the 8192-shot rank PUBs.
  A per-tier maximum matching finds 21 rank PUBs whose host's current qubits
  are at least two hops away (one idle qubit between them; 1 of 15 at 1024
  shots, 20 of 21 at 4096) and 19 at three hops. Fusing all 36 saves 30.43 s,
  of which 25.34 s is shared repetition delay (250 us times the smaller shot
  count of each pair), 0.49 s overlapping circuit time and 4.6 s job
  overhead; 15 of those pairs collide as placed and need a joint placement
  whose routed durations replace the maximum-of-components estimate. A fused
  row places another family's circuit a few hops away during every shot, and
  the sector 6 power margin is only 0.020 (lower modeled value 0.0907 against
  0.0468 + 0.0237 at 8192 shots), so fused rows need packed and isolated
  controls for cross-family crosstalk before their counts can enter the
  admitted contracts.
- A shorter repetition delay raises state-preparation error (IBM's qubit
  initialization guide). At 100 and 50 us the planned program shrinks by 51
  and 68 percent, the jointly fused one by 52 and 69 percent, and joint
  fusion with a 50 us delay by 79 percent against the plan. The service
  resets every qubit at the start of each shot by default, so the question
  is reset quality and memory between shots at a short delay. A
  qualification job at 250, 100 and 50 us on the cases' own qubits measures
  three effects: a leading measurement of every qubit in shots that follow a
  shot ending in `|1>` (initialization error after excitation), the lag-1
  correlation of consecutive shots in the shot-ordered records, and a Ramsey
  phase on a spectator (residual resonator photons shift its frequency). A
  shorter delay is admissible only when each effect moves the sector 5-7
  contrasts by less than a quarter of their 0.020 power margin and the
  contracts' radii are recomputed for the measured correlation. The job
  costs under a second of shots plus its 2.3 s overhead.
- Readout mitigation could lift the sector 5-7 lower modeled values back over
  the directional threshold at 4096 shots and remove the 8192-shot job, a net
  6.7 s under stress once its two PUBs join the 4096-shot job, but it changes
  the estimator the contracts are written on and widens its variance; it
  needs its own contract and power analysis before it replaces raw counts.

The cheapest program that changes no physics is co-batching with per-job
ceilings: 94.53 s nominal under 103 s of ceilings. Fusion as placed at two
or three hops reaches 73.40 or 75.49 s once cross-family controls qualify
the fused rows, and a joint placement 68.70 s.
