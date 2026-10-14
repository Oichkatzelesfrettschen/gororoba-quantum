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
`t1d2 - t1d1` at 0.0937, 0.0907 and 0.0961, below the 0.0997 the directional
contracts need (detection radius 0.0662 plus power radius 0.0335); an
8192-shot tier on the two PUBs that carry them admits the design. The static
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
| Fused: each rank PUB rides in a ripple PUB of its shot tier | 68.70 | 75.60 | 111 | 77 |
| As planned at a 100 us repetition delay | 48.29 | | | |
| Fused at a 100 us repetition delay | 33.06 | | | |
| As planned at a 50 us repetition delay | 31.35 | | | |
| Fused at a 50 us repetition delay | 21.19 | | | |

- Per-job ceilings change no data. Sized to each job's stress charge they
  cap ripple at 37 + 33 s and rank at 9 + 25 + 9 s, so ripple, rank and the
  18 s coherence-window case fit 131 s of ceilings, inside the owner's 135 s
  allotment for 2026-10-14. The runner applies one `--max-execution-seconds`
  to every job of an invocation; per-job ceilings need a policy field,
  approval binding and a per-job `max_execution_time`.
- Fusion keeps every PUB's shots, and two ripple PUBs rise from 4096 to 8192
  shots to host the 8192-shot rank PUBs. It saves 30.43 s (31 percent): 25.83
  s because each fused shot pays one repetition delay, and 4.6 s because five
  jobs become three. A maximum matching places 21 of the 36 rank PUBs in a
  host whose current qubits are already disjoint with a one-hop buffer on the
  Kingston coupling map (1 of 15 at 1024 shots, 20 of 21 at 4096); the other
  15 need a joint placement. Fused rows need matched packed and isolated
  controls for cross-family crosstalk, which the ripple family's packing
  contrasts already model within one family.
- A shorter repetition delay raises state-preparation error (IBM's qubit
  initialization guide). At 100 and 50 us the planned program shrinks by 51
  and 68 percent, the fused one by 52 and 69 percent, and fusion with a 50 us
  delay by 79 percent against the plan. A qualification job that reads
  prepared `|0>` and `|1>` at 250, 100 and 50 us on the cases' own qubits
  costs under a second of shot time plus its 2.3 s job overhead and decides
  whether that reduction is available.

The cheapest complete program that keeps all data is fusion with per-job
ceilings at the default delay: 68.70 s nominal under 77 s of ceilings, which
leaves room for the coherence-window case and a repetition-delay
qualification inside 135 s.
