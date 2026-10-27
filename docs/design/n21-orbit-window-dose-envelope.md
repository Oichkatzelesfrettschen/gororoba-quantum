# N=21 orbit window-dose sweep: the calibration-adaptive approval envelope

This case asks approval for a rule and its bounds, not for one calibration's values. IBM recalibrates its Heron
backends when monitoring calls for it, with no fixed period
([calibration-jobs.md](../notes/ibm_quantum/calibration-jobs.md)); across the dry run below, ibm_kingston's
calibration moved once in 53 minutes. `scripts/n21_dose_run.sh --submit` therefore plans on the calibration in
force, checks the plan against this envelope with `scripts/n21_dose_decisions.py --preflight`, and submits that
plan. The layout, the replica sets and the model values are the fresh plan's own. The bounds below are enforced by
the preflight, the runner or live_run.py, as the table names, and a plan outside any of them sends nothing.

## Question

Two retained N=21 runs bound the feedback-contrast loss from either side: the encoded circuit on ibm_kingston (336
CZ, about 15,000 dt of scheduled leaf idle) measured +0.0027 against a predicted +0.031, and the orbit circuit on
ibm_fez (28 CZ, about 2,000 dt) kept +0.197 against the idle-padded model's +0.179. One parameter-free incoherent
idle model fits both (claims `hw-n21-feedback-null-scheduled-idle` and `hw-n21-orbit-scheduled-idle-control`,
both exploratory), retrospectively and across circuits and backends. This run adds idle to the orbit circuit in
controlled doses, in one job on one calibration, with and without a Hahn echo. It estimates two numbers:
- kappa_P, the multiple of the Target's relaxation rate at which added free idle costs feedback contrast;
- kappa_P - kappa_E, how much of that loss the echo removes beyond the model's own echo gain (which comes from the
  T1 asymmetry of the echo's X pulses).

The Target reports T2 from a Hahn echo ([qpu-information.md](../notes/ibm_quantum/qpu-information.md)), and the
model charges free idle with that T2. A free-induction T2* below it, or a static detuning, makes kappa_P exceed
kappa_E. A noise simulation cannot answer either question: it assumes the Target description the run measures,
and Fez qubit 143's two-line beat (claim `hw-n21-q143-segmented-lines`) shows idle error outside that description.

## Circuit

The `n21-orbit-rca` family with `--window-doses-dt 0,1752,3500,5252,7000,10500,14000`, built by
`qpe_diagnostics` (`window_dose` and `window_dose_echo` variants). After the control's mid-circuit measurement and
reset, a barrier across the replica's four wires precedes the dose, so every dose delay starts after that
replica's reset. The plain arm holds `delay(D)` on all four wires; the echo arm holds
`delay(D/4) X delay(D/2) X delay(D/4)` on work bits 1 and 16 and `delay(D)` on the control and the bit for 4. Each
dose is a pair of feed-forward and omitted-correction members scored by their contrast difference; dose 0 has no
echo arm. That gives 13 contracts and 26 members, one PUB per member, each PUB packing every admitted disjoint
replica of the four-qubit circuit with its own barriers. The ISA archive holds no operation across two replicas;
whether the native schedule makes one replica wait on another's measurement is known only from the scheduler
timing the job returns, which the idle replay charges. The initialization herald (`--init-herald`) measures every
qubit into its own register before the circuit, and the analysis keeps only shots whose herald reads all zeros.

## Bounds

| Bound | Value | Enforced by |
|---|---|---|
| Account | backup instance, `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` | runner |
| Backends | ibm_fez, ibm_kingston, ibm_marrakesh (Heron r2), the planner's choice among those operational | preflight |
| Design | every field of `EXPECTED_DESIGN`: the seven doses, 8,192 shots, replica tier 24, one routed candidate, 32,768 model shots, the 0.09 precision screen, uniform allocation, minimum-charge objective, the herald, the 30 s total ceiling | preflight |
| Planning policy | every field of `EXPECTED_POLICY`: replica floor 0.45, calibration screens, cross-group buffer on, twirling and dynamical decoupling off, 30 s `max_execution_time`, the QRNG seed references | preflight |
| Replicas | at least 4 placed | preflight |
| Execution | one dynamic job of 26 PUBs, one member each; estimated charge at most 30 s | preflight, live_run.py |
| Repetition delay | 20 us; 50 us when no plan is admitted at 20 us, or as the bound retry below | preflight, runner |
| Seeds | `--seed-transpiler` `qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#0`, `--seed-simulator` index 1 | preflight |
| Code | the plan is made at the checked-out commit, and nothing under `gororoba_quantum/`, `scripts/`, `ci/`, `docs/design/`, `docs/evidence/anu_qrng/`, `docs/evidence/qrng_seeds/` or `requirements.txt` differs from it before each plan, preflight and submission; the draw's bytes match their pinned SHA-256 and the record's seeds are its index-0 and index-1 values | preflight, runner |

**Planner screen.** The model-shot count, the candidate count and the precision screen decide which plan is
admitted, not how the result is read. The precision screen bounds one replica's 8,192 shots by Hoeffding at the
Bonferroni alpha over the thirteen contracts, 0.082 per contrast, so a 0.08 screen refused every seven-dose plan
(the infeasible records of that attempt were not retained); the decisions pool every replica. One routed candidate
makes the dry run's design reusable at submission: when the policy, dependency versions, source digest, simulator
seed, compiled circuits, QPY bytes, PUB manifests and every calibration value equal the approved record's and every
recorded Aer batch ran on CPU by a host-independent route, live_run.py copies the approved predictions and design
(`reuse_approved_predictions`, `approved_family_design`) instead of simulating again
([qpu-submission.md](../notes/ibm_quantum/qpu-submission.md)). The wall time of that path is unmeasured, because
live_run.py takes `--approved-record` only with `--submit`; a full re-plan took 8 min 37 s.

**Calibration refusals.** `--submit` checks the approved circuits against the fresh calibration values before
planning and writes an `approval_required` record within seconds when any value changed, sending nothing and
leaving the approval unconsumed. The runner then plans again on the new calibration, preflights that plan and
submits it; the first three such refusals re-plan and the fourth ends the invocation. Each attempt's plan and
submission logs stay under `docs/local/`. A submission whose approval is consumed but whose run records no job id
is reported as an unknown outcome and never retried, whether or not its log names a run directory.

**Retry.** The 20 us delay lies at the floor IBM's changelog sets for Heron. The retained 0 us jobs and the 20 us
jobs of a 100,000-shot design under a 6 s ceiling all ended in error 1305, which the service reports for a stalled
shot loop and an overrun ceiling alike
([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md)). The 50 us retry is
therefore an operational fallback, not a diagnosis: `sh scripts/n21_dose_run.sh --delay 5e-05 --retry-of RUN
--submit` runs once, after the 20 us run RUN of this envelope's design and policy whose single submitted job,
the one collected, ended in error 1305 with no PUB executed (`n21_dose_decisions.py --retry-check`). It claims the
retry by exclusive creation of `RUN/retry-consumed.json` before planning, so a failed plan spends the retry and a
second invocation stops. Any other failure after a batch was sent ends the case.

## Decisions

The analysis reads the collected run through three commands:
```sh
"$PYTHON" scripts/scheduled_idle_replay.py RUN --out RUN/idle-replay.json \
    --dose-scales 0.25,0.5,0.75,1.25,1.5,1.75,2.0,2.5,3.0,3.5,4.0,5.0,6.0
"$PYTHON" scripts/n21_dose_decisions.py RUN --out RUN/dose-decisions.json
```
The replay gives each replica's exact branch-resolved law with the explicit doses and the service-scheduled idle
charged under the execution Target, and the same law with the dose delays' relaxation multiplied by each factor
(the model family M_r(d; k), k = 1 the Target's T1 and T2). A collection whose comparisons the collector withheld
(its PUBs did not run under one calibration) is refused.

**Estimates.** Each shot measures every replica of its PUB together. The analysis reads the shot-ordered
registers, binds them to the collected marginals, keeps each replica's shots whose herald reads all zeros, and
conditions the replay laws the same way, so an initial excitation at the 20 us delay leaves the estimates instead
of evolving through the dose. The covariance across replicas comes from the shots themselves (delta method), so
common-mode readout or crosstalk within a shot enters every variance. Sixteen contiguous blocks per PUB test for
drift within the job; each member's block dispersion ratio, when above one, multiplies that member's covariance
alone. One calibration supplies no between-calibration variance, and the estimates carry none. The model curves
take the execution Target's per-qubit T1 and T2 as exact, so every interval is conditional on those point values:
an error common to them moves the fitted rates, and a per-qubit error outside that common scale carries no term.

- **D1, idle response.** The pooled plain contrast at 14,000 dt lies below the dose-0 contrast at one-sided 95
  percent. A failure withholds evidence for the drop; it is no equivalence test.
- **D2, plain rate.** kappa_P fits the six pooled plain responses, measured(d) - measured(0), by generalized least
  squares against the replica-mean model family with their full covariance (the shared dose-0 arm included), with
  a 95 percent profile interval whose limits interpolate the threshold crossing. A dose-independent offset cancels in every response, and an error common to the
  Target's T1 and T2 values moves kappa_P rather than failing a point test. The one-rate family need not hold
  exactly (quasi-static dephasing adds a Gaussian factor in dose), so when the minimum chi2 exceeds its five
  degrees of freedom the interval's delta-chi2 threshold is multiplied by chi2_min / 5, the misfit scale factor,
  and the shape p-value is reported beside it. An interval that reaches the fitted range 0.25 to 6 or splits is
  withheld; otherwise an interval that excludes 1 reads as plain idle loss at kappa_P times the Target's rate.
- **D3, echo refocusing.** kappa_P and kappa_E fit the six plain and the six echo responses (echo(d) - plain(0))
  jointly, under the same scale-factor rule on ten degrees of freedom, with a 95 percent profile interval of delta =
  kappa_P - kappa_E; the verdict is withheld when the profile of kappa_P, kappa_E or delta reaches the fitted
  range's edge. A lower bound above zero reads as idle loss the Hahn echo removes beyond the Target model:
  quasi-static dephasing or static detuning, which this design does not separate. An upper bound below zero reads
  as an echo that costs more than it refocuses. A per-replica static detuning of either sign raises each replica's
  plain loss in second order and so enters delta as well.
- **Per replica.** Each replica's kappa_P,r and its interval are reported, not decided.

The self-test (`n21_dose_decisions.py --self-test`) decides synthetic sweeps drawn inside and outside the fitted
family: Target rates (unresolved), kappa 1.9 against 1.2 (refocusing), a common rate 1.5 (unresolved), an
oscillating plain arm (scale factor above 5), a flat sweep (no idle response), a rate beyond the fitted range
(withheld), and a plain arm with a Gaussian dephasing factor and an echo arm on the Target model at 19 replicas
and per-replica sigma 0.011, which reads as refocusing with the scale factor widening its interval.

**Power.** With a conservative contract variance (scores in [-1, 1], 97 percent of shots kept, replicas
independent) and the dry run's model shape, the standard error of delta is 0.054 at the floor of 4 replicas and
0.025 at the dry run's 19; the smallest delta detected at 80 percent power against the two-sided 95 percent
interval is 0.15 and 0.07. The design is powered for delta = 0.3 (`MIN_EFFECT`). The idle-penalty probe of
2026-10-26 on ibm_kingston (62 qubits, branch `heron/idle-penalty-probe`, commit `4774d70`) measured median
dephasing-rate multiples of 1.45 for free induction (T2_reported / T2*) and 1.14 for the echo (T2_reported /
T2echo), a gap of 0.31 that sets the scale of the effect this design is built to resolve.

## Plan at the dry run

The values below come from the dry run named here and illustrate the envelope; the submitted plan replaces them
with its own calibration's.

Dry run `2026-10-26T223508.256543Z`, not retained because its QRNG seeds belong to the submitted plan's own dry
run, the experiment the runtime ledger names (record.json SHA-256
`dcc6a7e7077f03b78c50e0a39c68a9d79e64451bd225edb96dec2132e35dbb1f`, commit `fc94e2f`, one routed candidate):
ibm_kingston, calibration 2026-10-26T15:18:32-07:00, 19 replicas, 26 PUBs x 8,192 shots at a 20 us repetition
delay, an estimated 17.1 s against the 30 s ceiling on the backup instance, whose rolling window held 390 s at the
time of writing. The plan took 8 min 37 s of wall time at nice 19 with a 1.3 GiB peak.

| Dose (dt) | Plain arm, model | Echo arm, model | Model echo gain |
|---|---|---|---|
| 0 | +0.198 | n/a | n/a |
| 1,752 | +0.172 | +0.169 | -0.002 |
| 3,500 | +0.140 | +0.159 | +0.019 |
| 5,252 | +0.118 | +0.141 | +0.023 |
| 7,000 | +0.088 | +0.117 | +0.029 |
| 10,500 | +0.050 | +0.085 | +0.035 |
| 14,000 | +0.013 | +0.050 | +0.037 |

The planner's model values come from 32,768 sampled shots per member (a simulation radius of about 0.055 per
contrast); the decisions read the idle replay's exact per-replica laws instead.
