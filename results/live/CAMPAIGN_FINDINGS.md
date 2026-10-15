# QPU campaign findings

This note interprets the ten retained Runtime jobs in seven acquisitions on
ibm_kingston and ibm_fez, 2026-10-11 to 2026-10-13. Each section names its
retained record, measured quantity, result and interpretation boundary.
Numbers come from the linked `collect.json`, adjudication or analysis files.
The [service inventory](qpu-job-inventory.json) and
[offline retention audit](qpu-job-retention-audit.json) reconcile every completed
physical job observed at 2026-10-13T23:18:34Z: 15 jobs, 270 PUBs, 659456 physical PUB
shots, 285 indexed raw data files and 15 indexed metrics snapshots. Local
simulations and native mock outcomes retain separate evidence identities.
The total settled charge is 210 seconds: 49 historical seconds and 161 new
campaign seconds, leaving 19 seconds under the 180-second campaign ceiling.
The account observation reports 390 remaining seconds; the 60-second reserve
and fresh-account-read requirement still apply to future acquisition. The
2026-10-13T04:59:38Z observation (ten jobs, 170 seconds, 59 seconds unallocated)
precedes the N=21 orbit, orbit-window and patch-window acquisitions.
The pilot's own collection and adjudication carry its 9-second charge;
[qpu-coordination.json](qpu-coordination.json) carries the later campaign's
execution ownership and settled charges.

## 1. Pilot: hybrid Shor and folded QPE, mod 15

Record [2026-10-11T152922.787095Z](2026-10-11T152922.787095Z/ADJUDICATION.md),
job `db5qmqclf4us73c4e1ug`, ibm_kingston, six dynamic PUBs at 4096 shots.

- The hybrid Shor factor yield is 0.4971 [0.4726, 0.5216] against the exact
  uniform null 0.2969 and the identity null 0.0042. For order 4 the ideal
  outcome law is the same with and without the conditional phases, so the
  yield supports the controlled arithmetic and decoder on these hardware
  witnesses and leaves the feed-forward untested.
- Packed replica 0 differs from its isolated reference on identical qubits
  by +0.0020 for hybrid Shor and -0.0037 for folded QPE. Both pass the
  preregistered Newcombe equivalence test within the 0.03 margin. The
  distribution-free Hoeffding view leaves folded-QPE equivalence unresolved
  at [-0.0306, +0.0234]. Scheduler tables show identical per-qubit
  instruction sequences on those reference qubits. Across the fifteen
  recorded replica pairs, correctness correlations have magnitude below 0.045; that descriptive
  result does not establish independent failures or absent crosstalk.
- Correctness estimates per 512-shot block remain within the reported
  sampling variation; that inspection detects no drift at its resolution.
- Execution takes 272.9 us per shot against a 250 us default repetition
  delay and a 22.9 us mean scheduled circuit duration. Repetition delay
  dominates the measured circuit-execution metric. The final 9-second charge
  also includes time outside that metric.

## 2. Folded-QPE intervention ladder

Record [2026-10-12T055624.091217Z](2026-10-12T055624.091217Z/ANALYSIS.md),
jobs `db67fqsvf2bc73d0pk4g` and `db67frimb58s738bci4g`, ibm_kingston, 16 PUBs
at 8192 shots: archived dynamic QPE, a delay arm, a no-feed-forward arm and a
coherent two-control arm for each eigenstate label.

- Coherent minus archived terminal accuracy is +5.8 to +10.9 percentage
  points with every simultaneous interval above zero. The two-control
  implementation outperforms the archived measurement-and-feed-forward
  implementation on these device witnesses.
- Delay minus archived estimates range from -0.3 to +1.9 points; their
  simultaneous intervals span [-4.424, +6.011] points across the four
  labels and each includes zero. Those comparisons remain inconclusive.
  The delay arm replaces measurement and changes the correction's source to
  the prepared label while retaining reset. The contrast therefore isolates
  neither measurement-induced loss nor an unchanged physical mechanism.
- Odd-label no-feed-forward intervals fall below zero, as the exact law
  predicts: the programmed correction affects terminal accuracy on hardware.
- The coherent arm changes routing, terminal readout qubit and control count.
  Its advantage belongs to the complete implementations; the retained
  comparisons leave its causal mechanism unresolved.

## 3-4. Folded correction: measured bit against known label

Records [2026-10-13T020454.599853Z](2026-10-13T020454.599853Z/analysis-1fdb68508f14.json)
(job `db6p55clf4us73c5nd9g`) and
[2026-10-13T022433.333775Z](2026-10-13T022433.333775Z/collect.json)
(job `db6pepklf4us73c5nqcg`), ibm_kingston, four dynamic PUBs per run at
8192 shots, eight PUBs in total; each run charges 11 s against 11.588 s
predicted.

- Both runs reach `retain_measured_correction`. Known-label correction fails
  the preregistered requirement for a gain above +0.01 on both odd labels:
  gain lower bounds are -0.0210 and -0.0077 in the first run, -0.0346 and
  -0.0006 in the second. Failure to admit establishes neither equivalence
  nor absence of improvement.
- Known minus measured point estimates favor the known label on s3
  (+0.0132 and +0.0209) and favor the measured bit on s1 (-0.0002 and
  -0.0129). Those point estimates alone establish no label-specific gain.
- About 11 percent of shots record the first bit as 0 despite the expected
  odd-label bit 1. Within that descriptive stratum the terminal-success
  ordering reverses by label: s3 known 0.567 and 0.553 against measured
  0.452 and 0.429; s1 measured 0.573 and 0.553 against known 0.540 and 0.512.
  Recorded-bit disagreement can arise from state preparation, evolution or
  readout. The retained counts do not identify assignment error or separate
  those mechanisms. The proposed claim `proposed-first-bit-readout-controls`
  in the [research state](../../docs/state/RESEARCH_STATE.md) adds
  repeated-readout and delayed-readout controls to investigate that boundary.
- The first run's exposed native event tables place the else-branch update
  at 4075 dt and the then-branch update at 4071 dt in both validated circuit
  pairs. Both runs pass their exposed-schedule qualification. The event
  tables omit phase values, which the circuit-pair checks supply, and the
  qualification excludes per-shot timing certification and undisclosed
  controller behavior.

## 5. Ripple: box-kite contrasts and depth-4 class return

Record [2026-10-13T025444.603480Z](2026-10-13T025444.603480Z/collect.json),
jobs `db6q2p2mb58s738c75gg` and `db6q2rklf4us73c5oq90`, ibm_fez, 146 static
PUBs (929 logical entries), 66 s against 63.967 s predicted.

- All 84 registered box-kite bright-minus-dark contrasts reject the null
  under family-wise Hoeffding bounds, with estimates +0.282 to +0.731.
  Hardware supports the registered contrast signs in the circuits compiled
  from the exact box-kite construction. Exact zero products, algebraic
  identities and topology remain classical results; the acquisition supplies
  implementation evidence rather than a new algebraic or topological proof.
- The registered depth-4 class-return contrast fails to reject its null:
  -0.0101 [-0.0848, +0.0645], against a detection radius of 0.0724.
  The interval bounds the measured circuit contrast under the stated
  stationary-repetition assumptions. It establishes neither a zero contrast
  nor absence of the ideal mathematical class return.
- The union-template walk readout controls show a large hardware-minus-replay
  discrepancy beside that result. Lane 0's expected all-zero/all-one outcome
  probabilities are 0.064453/0.045898 on hardware versus
  0.540039/0.440430 in calibration-bound replay; lane 1 gives
  0.130859/0.125977 versus 0.586914/0.521484. Each control has 1024 shots.
  These controls exercise the compiled union template, so the discrepancy
  cannot be attributed to readout assignment alone. The causal mechanism
  remains unresolved. Extra class-return shots can narrow sampling intervals
  but do not resolve that implementation/model discrepancy.

The ripple practical-packing check qualifies 19 of 21 registered scalar
controls within normalized +/-0.10. Kite 5 edge 1-2 phase 0 remains unresolved
at [-0.1010378650, +0.0483034900], as does Design C16 at
[-0.1276310163, +0.0963810163]. Each interval crosses an equivalence boundary;
neither certifies a practical distortion.

## 6. Rank-sector: sector contrasts and pulse-difference laws

Record [2026-10-13T032011.664435Z](2026-10-13T032011.664435Z/collect.json),
jobs `db6q9qo4qg6s73c57020` and `db6q9rsvf2bc73d1kpug`, ibm_fez, 36 static
PUBs (176 logical entries), 31 s against 30.413 s predicted.

- All 8 registered sector bright-minus-dark-at-one contrasts reject the
  null, with estimates +0.612 to +0.868.
- All 12 registered pulse-difference contrasts in sectors 4-7 reject the
  null: the zero-two t1d2-t0d1 contrast at +0.435 to +0.486, the zero-two
  t3d2-t2d1 contrast at +0.249 to +0.276 and the one-two t1d2-t1d1 contrast
  at +0.111 to +0.126. The point-estimate ordering agrees across the four
  sectors. The acquisition supports these implementation contrasts; exact
  rank and polynomial laws retain their classical proof boundary.

The rank-sector practical-packing check qualifies all 16 registered scalar
controls within normalized +/-0.10. These bounded observables retain their
selected circuits and layouts; complete distributional equivalence remains
unestablished.

## 7. Recovered wide control: active laws, spectators and joint residuals

Job `db6qe7klf4us73c5pdc0`, ibm_kingston, two PUBs at 512 shots, settled 2 s.
The [retrospective archive and replay](kingston-wide-control-result/README.md)
retain decoded submitted circuits, immutable shot-order data and a separate
descriptive analysis. The original approval, local submission archive and
execution calibration remain unavailable; retrieval supplies neither a
preregistered inference case nor byte identity to an original local QPY.

- The nominal 156-qubit Ramsey PUB has two gate-active qubits and 154
  measurement-only spectators. Its final two active bits have exact uniform
  law `(00,01,10,11)=(1/4,1/4,1/4,1/4)` and hardware counts
  `(142,140,121,109)`. Measuring the recycled qubit overwrites its earlier
  classical value. The post-reset conditional RZ changes only global phase
  on the reset state. Every active outcome is supported, so zero forbidden
  outcomes supplies no fidelity certificate. All 154 spectators remain zero
  in only 27 of 512 shots.
- The carpet occupies 87 gate-active qubits in 29 disconnected three-qubit
  components; 69 qubits carry neither decoded gates nor measurements.
  Every replica's exact law is `(00,01,10,11)=(1/2,1/4,0,1/4)`, ordered with
  the later measured bit on the left. Forbidden `10` counts range from 2
  to 117 per 512 shots. At least one replica violates ideal support in
  403 of 512 shared shots, with mean 1.357422 violating replicas per shot.
  The exact finite branch evaluator and Qiskit Statevector cross-check use
  states of at most three qubits.
- The derived analysis keeps all 406 replica pairs' joint counts, covariance
  and correlation, a per-shot error histogram, and shot-order block and lag
  descriptions. Marginal Wilson intervals assume iid repetitions and carry
  retrospective scope; they supply neither simultaneous error control nor
  causal crosstalk attribution. The two PUBs remain separate observations.

The experiment measures implementation residuals with high acquisition
density. Nominal circuit width, idle spectators and 29 replicas do not certify
156 useful qubits, independent measurements or an accuracy advantage.

## Findings across runs

- **Charge predictions have measured residuals.** The following residuals
  use `(settled charge - prediction) / prediction`. Their agreement on these
  completed workloads supplies empirical cost evidence; future service
  ceilings still require budget admission and cannot inherit a billing
  guarantee from these residuals.

  | Acquisition | Predicted seconds | Settled seconds | Relative residual |
  | --- | ---: | ---: | ---: |
  | Folded-QPE ladder | 39.632400 | 40 | +0.9275% |
  | Correction, first | 11.588024 | 11 | -5.0744% |
  | Correction, second | 11.588024 | 11 | -5.0744% |
  | Ripple | 63.966765 | 66 | +3.1786% |
  | Rank-sector | 30.413467 | 31 | +1.9285% |

- **Repetition delay dominates the retained execution-time arithmetic.**
  Reducing the 250 us default delay could improve throughput, subject to a
  separately qualified preparation-error and temporal-dependence check.
- **Packing passes a bounded scalar comparison.** Across ripple and rank,
  35 of 37 packed-versus-isolated control intervals lie within the normalized
  +/-0.10 equivalence margin, each interval divided by its score range as
  [STATIC_PACKING_ACCURACY.md](../ripple/STATIC_PACKING_ACCURACY.md)
  defines. Two ripple controls remain unresolved. Those
  results concern registered scalar observables on selected layouts; they
  establish neither failure independence, absence of crosstalk nor full
  outcome-distribution equivalence. Filling qubits can improve acquisition
  density only within the qualified measurement and statistical contract.
- **Recorded first-bit disagreement is correlated with the terminal
  outcome.** The roughly 11 percent disagreement on qubit 79 is measured. In
  the known-label arms the terminal success falls from 0.80 to 0.54-0.57 when
  the first bit reads 0. Independent, state-preserving assignment error
  cannot do that
  ([novel-insights](../../docs/evidence/novel-insights/REPORT.md),
  section 2). A state change of qubit 79 and a common cause behind both the
  misread and the terminal loss remain, and the strata stay descriptive.
- **The coherent advantage remains implementation-specific.** The ladder's
  inconclusive and confounded delay comparison, the correction adoption
  failures and the walk control/replay discrepancy motivate matched controls.
  The existing observations do not isolate a common causal explanation.
