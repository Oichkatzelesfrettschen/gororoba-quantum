# Hardware plan

This plan joins the project's two hardware programs -- the Cayley-Dickson
witnesses (DESIGN_NOTES.md) and hybrid Shor order finding (HYBRID_SHOR.md) --
into one submission path under the 600 s rolling QPU budget. Every quantity
it quotes comes from the dry-run record
`results/live/2026-10-10T222132.627032Z` (code 02a5b4b) unless it names
another source; the record's predictions are noise-model values, not
hardware results.

## What each group claims and what refutes it

| group | claim | observable | control or null | falsifier |
|---|---|---|---|---|
| design A (1,2) | the octonion associator sign reaches the readout as a Fano Z-string | P1, ideal 1 | mirror twin; dephased null P1 = 0.5 | P1 at or below 0.5 |
| zero-divisor fringe | a sedenion zero-divisor pair annihilates in interference | dark/bright P0 ratio; fringe visibility and phase | sign-flipped bright control; eight-phase sweep; mirror twins | ratio at the bright level, or fringe phase off 0 |
| design C dim 8, 16, 32 | the associator's Walsh spectrum follows the algebra along the ladder | TVD to the true spectrum against the flipped and omitted predictions | flip and omit controls on the same layout | TVD to true at or above TVD to flip |
| folded QPE mod 15 | eigenphases of x -> 2x mod 15 read out by semiclassical phase estimation | P(correct s) per eigenstate | identity-multiplier null reading 0 | P(correct) at the uniform 0.25 |
| hybrid Shor N = 15 | faithful order finding from \|1> recovers r = 4 and the factors 3 and 5 | factor and order-recovery yield | schedule-matched identity null; exact uniform null 0.297 | the admission rule below fails |

## From calibration to circuits

1. **Detector.** live_run.py reads each backend's status, Target, and
   properties in the deciding process and excludes every qubit and CZ edge
   outside the QUALITY policy or flagged faulty. The record's snapshot
   excluded 11 qubits and 16 edges on ibm_fez, 7 and 24 on ibm_kingston, and 31
   and 20 on ibm_marrakesh, every one by a policy threshold -- readout error,
   T1 or T2, sx or CZ error, or missing calibration -- and none by a faulty
   flag, so the thresholds carry the detection. The eligibility gate skipped
   ibm_marrakesh outright: it reported status_msg "maintenance".
2. **Selection.** Eight transpiler seeds per group and backend; the best three
   compile their controls onto one layout, and the best geometric-mean layout
   score (ESP times the T2 dephasing factor) picks backend and layout.
   ibm_kingston won every group.
3. **Placement.** packing.py embeds the winning pattern everywhere it fits in
   admissible hardware, ranks the embeddings by the same layout score, and
   packs disjoint replicas one qubit apart down to a floor fraction of the
   best score: 0.9 by default, a group's declared floor where it has one
   (hybrid Shor declares 0.8), and an explicit --replica-floor for every group
   when given. Design A fills 63 of
   kingston's 156 qubits per shot with 21 replicas, design C dim 8 fills 54
   with 18, hybrid Shor 35 with 7, and the other five-qubit groups take 3 to
   6.
4. **Revalidation.** --submit re-reads every chosen backend and replans any
   group whose calibration values moved on its packed qubits.

## Statistics that decide a result

- **Variance.** Each member's per-shot score splits into shot and layout
  variance with a chi-squared test across replicas; folded QPE adds an
  instance axis. The noise model predicts layout variance of 2e-5 to 4e-4 in
  the primaries and none beyond shot noise in Shor factor yield (p 0.66).
- **Crosstalk.** The primary runs alone on replica 0's qubits beside the
  packed run; the noise model puts their difference at zero, so a measured
  difference is crosstalk from packing.
- **ODR.** The pooled value averages each replica's witness over its own twin
  and needs 16384 shots over all replicas, so packing meets it at the default
  4096 shots for every mirrored group: design A pools 86,016 shots over 21
  replicas (P1_ODR 0.989 in the noise model) and the fringe 24,576 over 6
  (ratio_ODR 0.0064, visibility_ODR 0.988).
- **Admission.** hybrid Shor is interpreted only through its admission rule:
  the primary factor-yield lower bound must exceed the exact uniform null
  (0.297) and the identity-null upper bound must stay below that lower bound.
  The noise model gives [0.483, 0.501] against an identity-null upper bound of
  0.013. Each bound is the union of the replicate t interval and a Wilson
  interval over the pooled shots; Shor's seven replicas put the t multiplier
  at 2.45, where three gave 4.30.

## QPU cost

QPU time scales with PUBs times shots; replicas ride along inside a PUB at no
extra shots. The record holds 38 PUBs, 29 static and 9 dynamic, so the full
program at 4096 shots is 155,648 shots. The project has not measured its own
shot rate; the literature bounds it between about 1,000 shots/s for many-twirl
runs (literature/notes/2505.22629.md) and 4,900 shots/s derived from
literature/notes/2507.08088.md, which puts the full program between 32 s and
156 s plus job overhead.

| job | groups | PUBs | shots | at 4,900/s | at 1,000/s |
|---|---|---:|---:|---:|---:|
| dynamic | folded QPE, hybrid Shor | 9 | 36,864 | 7.5 s | 37 s |
| static | design A, fringe, design C 8/16/32 | 29 | 118,784 | 24 s | 119 s |

## Path to the first submission

1. **PUB fusion.** Groups on one backend and job kind share PUBs: entry i of
   every group packs into one circuit on disjoint placements, so the static
   job needs as many PUBs as its largest group (14, the fringe) instead of 29,
   and the dynamic job 6 instead of 9. Placement then allocates one pool of
   admissible qubits across groups, and the per-group decoding is unchanged.
2. **Written case.** The case states the job split, the fused PUB count, the
   fresh dry run's predictions, and the seconds bound from the table above,
   and waits for approval (AGENTS.md).
3. **Dynamic job first.** It is the smaller job and carries the questions only
   hardware answers: hybrid Shor admission, concurrent feed-forward across
   packed replicas (the crosstalk reference), feed-forward latency from the
   execution spans, and the project's own shot rate, measured by the job's
   usage seconds. That rate replaces the literature bounds before the static
   job is costed.
4. **Static job.** Submitted with --twirl and a DD sequence only when the
   case argues that the hardware-versus-model gap with them on is the
   question; otherwise both stay off so the first static measurement compares
   directly with the noise model.

## Risks

- **Parallel feed-forward.** Hardware handling of three or more simultaneous
  if_else branches is unmeasured; the isolated reference detects a cost.
- **Drift during the job.** A calibration update inside a PUB's execution
  span removes its replayed and corrected views; packing shortens the job and
  so narrows that window.
- **Layout structure the model omits.** Measured layout variance above the
  prediction, or a flagged replica, marks hardware the exclusion policy
  missed; the replicas still report, and the flag names the qubits.
