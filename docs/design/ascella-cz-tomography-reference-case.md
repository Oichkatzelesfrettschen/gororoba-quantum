# Ascella CZ process tomography reference across the HOM band 90 ± 6.84 points

This is the written case for two qpu:ascella jobs of 72 template iterations that repeat the CZ process tomography of
[ascella-cz-process-tomography-case.md](ascella-cz-process-tomography-case.md) at any calibration whose HOM visibility
lies within 6.8420696 percentage points of 90 %, and preregisters twelve conjectures the pair decides.
[scripts/ascella_cz_tomography_reference_case.py](../../scripts/ascella_cz_tomography_reference_case.py) builds the frozen requests in
[results/quandela/cases/ascella_cz_tomography_reference](../../results/quandela/cases/ascella_cz_tomography_reference/job-00/cases.json),
checks them, forecasts the outcome over the admitted HOM band and gates every submission. Nothing has been sent;
the owner's approval of these request digests is pending, and a submission pins the approved digest. The approval rule of gororoba-quantum `AGENTS.md` ("Hardware services") governs the submission.

## Why the case exists

The CZ compilation ensemble ([ascella-cz-compilation-ensemble-case.md](ascella-cz-compilation-ensemble-case.md))
compares its tables with the prediction of a retained process tomography. The owner's ruling of 2026-11-08 admits an
ensemble job only at a HOM strictly above 90 % and within one point of that tomography's HOM. The retained
tomography ran at 87.56 %, so no HOM satisfies both conditions and the ensemble refuses every plan by design. A
tomography acquired above 90 % gives the ensemble a non-empty band, `max(90, ref - 1) < HOM <= ref + 1`. Paired with
the retained tomography at 87.56 %, it also measures one change in process fidelity across HOM. That change is
descriptive, because two calibrations differ in more figures than HOM.

The owner's ruling of 2026-11-09 keeps 90 % as the preferred HOM and admits this tomography at any HOM from
83.1579304 % to 96.8420696 % (90 ± 6.8420696 percentage points, both ends inclusive). The retained qpu:ascella reads
of 2026-10-21 to 2026-11-07 ran from 86.86 % to 89.10 % and never reached 90 %, so the band turns a wait with no end
into a run at the next admitting calibration. A tomography below 90 % still leaves the ensemble's own floor in force:
moving that floor is a change to the ensemble case, made with its `TOMOGRAPHY_RUNS` once this pool is decided.

The estimand, the 144 settings, the eligibility rule, the estimator, the bootstrap type and the pooling rule are those
of the retained case, imported by name from
[scripts/ascella_cz_tomography_case.py](../../scripts/ascella_cz_tomography_case.py). Local SLOS and Perceval's
NoiseModel give the law of the designed unitary at modeled source figures. They cannot give what the 144
service-compiled meshes realize at the new calibration, so a simulation does not answer the question. The retained
run already sat outside the noise model (0.849 measured against 0.786 forecast).

## Latest calibration

The platform read retained in
[platform-read/ascella-perfs.json](../../results/quandela/cases/ascella_cz_tomography_reference/platform-read/ascella-perfs.json)
on 2026-11-09 shows the following.

| Field | Value |
|---|---|
| Status | available |
| HOM | 88.76 % |
| g2 | 2.0 % |
| Transmittance | 5.51 % |
| Clock | 13.33 MHz |

The gate admits this read's HOM; its transmittance sits at the floor that the caps need (below).

The dark counts of this read would move the retained case's window rule (`tomo.choose_window`, the darkest six-mode
window whose first and third modes are sources) from chip modes 0..5 to 2..7: 589 against 667 detections per second.
The difference of 78 per second is negligible next to the 1.43 million shots per second of the photons. The case pins
the retained window, photons on chip modes 0 and 2, because the compared estimand and the ensemble's `tomo.SOURCES`
both name that window.

## How qpu:ascella bills and times a job

The billing rules are those of [quandela-credit-optimization.md](../runbooks/quandela-credit-optimization.md).

- **Credits.** A completed iterated job costs 1 credit, plus 1e-6 credits per shot. The shots billed are the shots
  used, capped at the largest iteration's `max_shots`. A tomography job uses tens of millions of shots against a cap
  below a million, so the cap sets the bill: credits = 1 + 1e-6 x max(max_shots).
- **Seconds.** `max_duration` is 300 s per job. The retained tomography jobs recorded 221 s for 72 iterations
  (`results.json` status.duration, both jobs), which gives 3.069 s per iteration, compilation and a 4000-sample
  acquisition together. `iteration_seconds` reads that figure from the runs.
- **Shot rate.** A shot is a detection event of at least one photon. The rate is the clock times 1 - (1 - T)^2:
  13.33 MHz x 0.1072 = 1.43 million shots per second at T = 5.51 %.
- **Job count.** 144 iterations x 3.07 s is 442 s, which exceeds 300 s, so the case needs two jobs at minimum. Each
  job's 72 iterations take 221 s, and the remaining 79 s are the shot budget.

The job fee is fixed and the per-shot term is billed only up to the largest cap. Within one job, the cap
therefore buys every iteration the same number of shots for the price of one. The retained design gave every
iteration 4000 samples. The input |1>|0> needs about six times the shots per sample of the other inputs, and
its job's uniform cap of 1.6 million then sets both the bill (2.6 credits) and the worst-case time. That worst case,
with every iteration at its cap, was 292 s at the retained transmittance of 5.82 %. At today's 5.51 % it reaches
about 301 s, past `max_duration`, so the retained design would no longer fit.

## The design

Every iteration shares one shot cap, `SHOT_CAP` = 1,567,000. Each setting takes its own `max_samples`: the largest
multiple of 100 whose shots, scaled linearly from Perceval's estimate at 4000 samples (Perceval rounds n / p, so the
scaling holds to under one shot)
([shot-estimate.json](../../results/quandela/cases/ascella_cz_tomography_reference/shot-estimate.json), the same
perfs as the platform read) and multiplied by the retained margin of 1.25, stay within the cap. The retained runs
measured 0.89 to 1.18 times Perceval's per-setting estimate, so the margin of 1.25 covers them.
[qd_platform.payload](../../scripts/qd_platform.py) sends each template iteration under its own budgets, and
`qd_records.iteration_form` validates them: positive integers, `max_shots >= max_samples`, summing to the manifest's
totals.

The design maximizes the precision of the process fidelity within the bill and the clock. The bill rises with the
largest cap, the time with the sum of the caps. Equal caps give every iteration the most shots for a given largest
cap, so for any ceiling the cap is shared. Its size is the owner's choice (2026-11-09): the largest cap whose worst
case, every iteration at its cap, fits 300 s at the read's transmittance, (300 - 221) s x 1.43 million / 72 =
1.567 million. Both constraints then bind, and any other allocation either raises the bill or passes 300 s.

| Quantity | Retained design | This design |
|---|---|---|
| Samples per iteration | 4000 each | 3900 to 35500 (the four in-10 settings with Z on exactly one qubit: 11800; in-10-ZZ: 3900) |
| Samples per job | 288,000 | 2,033,400 (job-00), 1,938,600 (job-01) |
| Largest `max_shots` | 400,000 and 1,600,000 | 1,567,000 in both jobs |
| Credits | 1.4 + 2.6 = 4.0 | 2.567 + 2.567 = 5.134 |
| Expected eligible events | about 99,000 | about 620,000 |
| Process-fidelity spread (delta method) | 0.0104 | 0.0040 |
| Worst case, every iteration at its cap | 301 s at T = 5.51 % | 300 s at T = 5.51 % |

The spread is the delta-method standard deviation of the unprojected fidelity, F = (r . a) / (r . b), under the
record forecast variant at each HOM of the curve below (`fidelity_sd`). It is 2.58 times smaller than the retained
design's at every HOM point. The two designs differ only in where the shots go, so the spread scales with how the
budget is spent. The same expression reproduces the retained run's interval: 0.0104 against the measured 95 %
interval of 0.828 to 0.869, which corresponds to a standard deviation of about 0.0105.

The cap that keeps the retained ceiling, 990,000 (1.99 credits per job, 3.98 for the pair), gives a spread of
0.0051 and a worst case of 271 s. The chosen cap buys a spread 1.26 times narrower for 1.13 more credits, and it
leaves no time margin: every plan below the read's 5.51 % transmittance is refused.

## How the request meets every HOM in the band

The request is frozen when the case is built, and the gate only admits or refuses it. The band makes one frozen body
serve every HOM it admits, because the body needs nothing that HOM changes.

- The owner's approval names the frozen request. `qd_platform.submit` binds the receipt to the `cases.json` digest,
  and `bind_reviewed` requires the posted body to equal the admitted preflight's body, minus `process_id`. A body
  rebuilt at submit time from the live read is a request nobody reviewed.
- The token reads HOM and cannot set it. A job queues and runs after the read, so a design keyed to one reading
  describes a calibration the job may no longer run on. The gate's in-lock re-read and the equality of the
  estimate's perfs with the plan's narrow that window, without closing it.
- The budgets hold at both ends of the band. `RemoteComputer.estimate_required_shots` simulates the circuit at
  indistinguishability 1 and g2 0 (`perceval.runtime.remote_computer._estimate_sample_probability`). Two photons
  bunch into output mode k with probability (1 + M) |U_k1|^2 |U_k2|^2 at photon overlap M, so the two-click
  probability falls as M rises, and the estimate at M = 1 bounds the shots per sample at every HOM. The forecast
  confirms it: the setting with the most expected shots stays 1.277 times below the cap at every point from
  83.16 % to 96.84 %, and a job's expected shots move by at most 2.7 % across the band (1.8 % for job-00,
  2.7 % for job-01).
- The forecast follows the same split. The repository forbids guessing hardware figures, so the forecast is a curve
  over the band at the read's other figures, and the plan read at submission picks the point.
- The preferred HOM is an anchor, not a wait: the forecast includes 90 %, and the analysis reports each job's HOM
  minus 90 as a covariate beside every estimate.

## Seeds

Every new seed comes from one fresh ANU QRNG draw,
[draw-2026-11-09T020604Z.json](../evidence/anu_qrng/draw-2026-11-09T020604Z.json) (256 uint16 values). The rule is
nonzero values in index order, repeats skipped, and none was skipped.

| Use | Indices |
|---|---|
| 144 compilation seeds, schedule order | 0 to 143 |
| Bootstrap seed of the analysis | 144 |
| One synthetic dataset per forecast HOM point | 145 to 156 |
| Acquisition-reference draws of the overdispersion statistic | 157 |
| Owned and unused | 158 to 255 |

The case takes fresh compilation seeds rather than reusing the retained case's. The owner ruled on 2026-11-09 to use
QRNG seeds wherever a seed is needed. The case measures a new reference at a new calibration, and the seed rule of
`AGENTS.md` ("Seeds") gives a new job its own randomness. `--check` requires that no compilation seed repeats a
retained one. Fresh seeds add compilation variation to the HOM comparison with the retained tomography, so that
comparison stays descriptive. Both `cases.json` files name the draw without an index, which makes the case its owner
in the ledger of `ci/seed_provenance.py`.

## Submission gate

`--preflight JOB` plans the job read-only, holds the plan to its submission policy and retains the admission as
`plan-read.json`. `--submit JOB --approval TEXT` posts the job through `qd_platform.submit`, with `SubmissionGate` as
its verify step inside the submit lock. The manifest names the wrapper, so the generic runner refuses any other
verifier. `SubmissionGate` refuses unless all of the following hold:

- the HOM at the plan lies in the band, 83.1579304 % to 96.8420696 % (`HOM_BAND`, both ends inclusive);
- the transmittance is at or above the floor at which every iteration at its cap still fits 300 s, which is 5.509 %,
  the read's own figure to rounding, so the case waits for a calibration that holds the transmittance at the read's
  level or higher;
- the Explorer row and the processor read `available` or `running`, while the token counts no running, no queued and
  no running quantum-task job;
- the shot estimate and a processor read taken inside the lock carry the plan's perfs, and source modes 0 and 2
  are connected;
- for job-01, a collected job-00 run completed with all 72 iterations counted, and the job-01 plan lies inside the
  retained pooling tolerances against it: HOM within 1.0 point, transmittance within 0.3 points, and at most 12 hours
  after job-00's submission. A job-01 plan outside them would buy a pool that `tomo.pooling` leaves descriptive;
- the plan equals the admitted preflight: the case digest, the body minus `process_id`, the perfs and the predecessor
  run.

The credit ceiling per job is 2.567. The expected time is 285 s: the iterations' recorded seconds plus the shots
the samples need, the cap divided by 1.25, at the read's shot rate.

## Forecast over the band

[forecast.json](../../results/quandela/cases/ascella_cz_tomography_reference/forecast.json) evaluates the retained
case's noise pipeline at each HOM point, holding the read's g2, transmittance, clock and dark counts. Each point
gives two estimands: one from indistinguishability alone and one from the record variant, which includes the source,
loss and dark counts. Each point also carries the design's delta-method spread and one synthetic dataset of this
design, analyzed as a run would be.

| HOM % | Indistinguishability only | Record variant | Spread | Synthetic dataset | 95 % interval |
|---|---|---|---|---|---|
| 83.1579304 | 0.784 | 0.741 | 0.0039 | 0.743 | 0.736 to 0.752 |
| 84.5 | 0.799 | 0.754 | 0.0039 | 0.752 | 0.745 to 0.760 |
| 86.0 | 0.816 | 0.769 | 0.0039 | 0.776 | 0.768 to 0.783 |
| 87.56 | 0.834 | 0.786 | 0.0039 | 0.779 | 0.772 to 0.788 |
| 88.5 | 0.845 | 0.796 | 0.0040 | 0.797 | 0.790 to 0.805 |
| 89.25 | 0.854 | 0.804 | 0.0040 | 0.802 | 0.795 to 0.810 |
| 90.0 | 0.864 | 0.812 | 0.0040 | 0.809 | 0.801 to 0.816 |
| 91.0 | 0.876 | 0.824 | 0.0040 | 0.827 | 0.819 to 0.834 |
| 92.5 | 0.895 | 0.841 | 0.0041 | 0.841 | 0.833 to 0.847 |
| 94.0 | 0.915 | 0.858 | 0.0041 | 0.860 | 0.852 to 0.868 |
| 95.5 | 0.935 | 0.876 | 0.0041 | 0.871 | 0.863 to 0.879 |
| 96.8420696 | 0.954 | 0.893 | 0.0042 | 0.887 | 0.879 to 0.894 |

The indistinguishability-only column is exactly F_pro = (1 + M) / (2 (2 - M)) at M = HOM / 100 (derived in the next
section; `tests/scripts/test_ascella_cz_tomography_reference_case.py` checks every point to 1e-9). The record variant
is the same linear-fractional form to 6e-6, and it rises 0.011 per HOM point at the band's center. A straight line
misses either column by up to 0.003, which a series of HOM points at a spread of 0.004 can resolve and one pair
cannot.

## Preregistered conjectures

### The overlap law of the postselected CZ

Two photons with internal-state overlap M = Tr(rho_1 rho_2) reach an output pair with probability
P = (1 + M)/2 |per A|^2 + (1 - M)/2 |det A|^2, A the 2 x 2 submatrix of the interferometer (the Gram expansion;
equivalently P = M P_indistinguishable + (1 - M) P_distinguishable). In the case's own photon model
(`tomo.forecast_setting`), the rail inputs 00, 01 and 11 succeed with probability 1/9 at every M, because their
photons never meet. Input 10 succeeds with probability (5 - 4M)/9, because its photons meet at the 1/3 coupler:
permanent 1/3, determinant -1. The Choi matrix is therefore affine in M, its trace is (4/9)(2 - M), and the
unprojected process fidelity is F_pro(M) = (1 + M) / (2 (2 - M)), with inverse M_F = (4F - 1) / (2F + 1).
The same law gives a second overlap estimate that needs no fit. Let r(xy) be the eligible rate of input xy, averaged
over its nine readouts; a local readout keeps one photon per qubit, so every readout carries the input's success
probability. Then D = r(10) r(01) / (r(00) r(11)) = 5 - 4M. Each rail's detection efficiency enters D once above and
once below. Inputs 10 and 01 belong to job-01 and inputs 00 and 11 to job-00, so a job-01 pooling scale s enters
as s^2. `rail_rate_ratio` computes D and
`control_rate_ratio` computes r(11) / r(01), which is 1 at every M on balanced rails.

### Overdispersion and the verdict rule

The Pearson statistic of the retained pair's 576 counts about the unweighted linear-inversion fit is 5288. Its
acquisition reference draws 200 synthetic pairs under the fit as the service acquires them: each setting stops at
its observed sample count, its eligible outcomes are one multinomial over that quota, its shots are the quota plus a
negative-binomial count, and each pair is refit and scored like the data. The reference has mean 3677 and 95 % range
1986 to 6914, so the observed statistic lies inside it and the ratio is 1.44. The fit predicts negative rates on 29
near-zero cells (they sum to -160 expected events), which is why the reference sits far above 320, the degrees of
freedom; the synthetic pairs carry the same bias.

The scatter test is a model check, not a correction. Every conjecture is judged on the primary bootstrap's 95 %
interval. When the model check fails, every other verdict is reported as conditional on that failure. A single
residual statistic cannot widen intervals soundly, because a systematic error inside the model space moves the fitted
Choi matrix and leaves the residual unchanged. Each `cases.json` states the rule under `preregistered.verdict_rule`,
the reads the predictions use under `preregistered.plan_reads`, and the reference under
`preregistered.overdispersion`. The reference draws take QRNG index 157.

### The conjectures and the retained pair's verdicts

`--retained-verdicts` runs the same code on the retained 2026-10-31 pair (HOM 87.56 %, g2 1.8 %, T 5.81 %) and
writes [retained-conjecture-verdicts.json](../../results/quandela/cases/ascella_cz_tomography_reference/retained-conjecture-verdicts.json);
`--check` recomputes it. The retained process fidelity is 0.849, with interval 0.828 to 0.869.

| Conjecture | Prediction (retained) | Held against (retained) | Retained verdict |
|---|---|---|---|
| Overlap is the only error: F = (1 + M)/(2(2 - M)), M = V | 0.834 | F 0.828 to 0.869 | survives |
| The same law at M = min(1, (V + g2)/(1 - g2)) | 0.876 | F | falsified |
| Noise pipeline, record variant (source, loss, dark counts) | 0.788 | F | falsified |
| Noise pipeline, g2-corrected overlap variant | 0.826 | F | falsified, by 0.002 |
| The rail ratio reads the platform HOM: M_R = V | 0.8756 | M_R 0.914, 0.896 to 0.931 | falsified |
| The two overlaps agree: M_F = M_R | 0 | M_F - M_R -0.025, -0.049 to -0.001 | falsified |
| No overlap beats M = 1: F at or below the record variant at HOM 100 % | 0.937 | lower end of F | survives |
| Balanced rails: r(11)/r(01) = 1 | 1 | 1.009, 0.969 to 1.051 | survives |
| r(11)/r(01) takes the record variant's value (lost-twin multiphoton events) | 1.038 | same | survives |
| Model check: scatter matches the acquisition law | 5288 | reference up to 6914 | survives |
| Constant variance factor: the ratio stays at the retained 1.44 | 1.44 | 1.08 to 1.80 | survives by construction |
| Relative systematic per rate: ratio - 1 grows with events per rate | 1.44 | 1.08 to 1.80 | survives by construction |

The twelve verdicts read four observed summaries: the process fidelity, the rail ratio with its joint difference,
the control ratio and the Pearson statistic. They are distinct benchmarks on those summaries, not twelve independent
pieces of evidence. Five fall on the retained pair. The overlap-only law survives, and every model that adds g2 to
the overlap overshoots or undershoots the measured fidelity. The rail overlap, 0.914, sits 3.8 points above the
platform's HOM read and 2.5 points above the fidelity overlap M_F = 0.888; under overlap-only error the two would
agree, so an error beyond overlap lowers the fidelity, or the rail rates carry a setting-dependent factor the double
ratio does not cancel. The new pair carries about six times the events per setting. Its overdispersion ratio
separates a constant factor (1.44) from a relative systematic per rate (about 1 + 0.44 x 6.2 = 3.7), and its
narrower intervals test the two overlap estimates again at a new HOM.

The workspace's algebraic lineages (de Marrais box-kites, Hurwitz, Cayley-Dickson, Moreno and the Pfaffian
reduction, Hilbert-Samuel fibers, Levratti) predict no rate of this measurement: the only matrix functions it reads
are the 2 x 2 permanent and determinant. [ascella-cz-tomography-ledgers.md](../notes/topics/ascella-cz-tomography-ledgers.md)
holds both ledgers, the sources by manifest digest and the verdict per lineage.

## Stopping rule

- A terminal error with no counted iteration allows one resubmission of the identical body under the same approval,
  after the gate passes again. A second error stops the case.
- A job that returned counts is never resubmitted under this approval.
- A truncation leaves the pool undecided. Running the missing settings is a new written case.
- A setting that stops at its `max_shots` before its `max_samples` returns counts, and the analysis reads its actual
  samples and shots, but the pool is then reported as descriptive and job-01 is not admitted after such a job-00.
- `--submit` enforces the attempt limit: it refuses while an earlier posted attempt of the job is uncollected or
  returned counts, and after two posted attempts. A refused `--submit` removes the run directory it created, which
  holds only the request copies.
- A plan that reads a HOM outside the band sends nothing, and the case retries it at a later calibration. The band
  is never widened under this approval.
- A pool decided by the retained case's tolerances (HOM within 1.0 point, transmittance within 0.3 points,
  submissions within 12 hours) replaces the ensemble's `TOMOGRAPHY_RUNS` in one change. That change regenerates the
  ensemble's prediction, manifests and ledger rows, and the ensemble's preflights are then taken again.

## Procedure after approval

`--submit` copies the job's `cases.json` and `circuit.json` into a fresh run directory,
`results/quandela/runs/<UTC stamp>-qpu_ascella-ascella_cz_tomography_reference-<job>`. `qd_platform.submit` writes
the receipt there, and `qd_platform.py collect` reads it from there. The case directory keeps only the request and
its admitted preflight.

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASE=scripts/ascella_cz_tomography_reference_case.py
"$PYTHON" "$CASE" --preflight job-00
"$PYTHON" "$CASE" --submit job-00 --approval "APPROVAL TEXT"
RUN_00=results/quandela/runs/STAMP-qpu_ascella-ascella_cz_tomography_reference-job-00  # printed by --submit
"$PYTHON" scripts/qd_platform.py collect "$RUN_00" --timeout 3600
"$PYTHON" "$CASE" --preflight job-01 --after "$RUN_00"
"$PYTHON" "$CASE" --submit job-01 --approval "APPROVAL TEXT" --after "$RUN_00"
RUN_01=results/quandela/runs/STAMP-qpu_ascella-ascella_cz_tomography_reference-job-01  # printed by --submit
"$PYTHON" scripts/qd_platform.py collect "$RUN_01" --timeout 3600
"$PYTHON" "$CASE" --analyze results/quandela/ascella-cz-tomography-reference-analysis.json "$RUN_00" "$RUN_01"
```

## Checks

| Check | Result |
|---|---|
| `ascella_cz_tomography_reference_case.py --check` | passes: both requests rebuild byte for byte, every iteration's samples fill the cap to one quantum, worst case 300.0 s, ceiling 2.567, fresh disjoint seeds, design spread below the retained design's at every HOM point of the band, and the retained pair's conjecture verdicts recompute |
| gate `core-record-check-07` (ci/gates.json, on demand on the build host) | runs `--check`, which rebuilds both requests byte for byte; the decomposed mesh floats follow the CPU's numeric path, so the `tests` check runs the budget, bound and identity checks without the rebuild |
| `ascella_cz_tomography_case.py --check` | passes: the retained requests still rebuild byte for byte after the loader and pooling take a family |
| `qd_platform.py --self-test` | passes, with budgeted and unbudgeted template cases and three malformed budget lists |
| `qd_platform.payload` on both ensemble jobs | each body's digest without `process_id` equals its retained `plan-read.json` value, so an unbudgeted template case sends the same bytes |
| `tests/scripts/test_ascella_cz_tomography_reference_case.py` | 61 pass: the gate's refusals, the band's ends, the floors, the budgets, the overlap law against every forecast point, the rail ratios against the photon model, the seed partition, strict JSON with one-sided bands, and the retained verdict list |

## Limits

- The fit is one Choi matrix of 144 mesh-specific tables, as in the retained case. Fresh compilation seeds give new
  meshes, so the HOM comparison carries compilation variation.
- Unequal samples per setting leave the estimator's unweighted linear inversion unchanged: the rates divide by each
  iteration's shots. The settings of input |1>|0> carry fewer samples and a wider share of the spread.
- Unequal per-iteration samples within one job have one hardware precedent: the qpu:belenos mesh run
  `2026-10-18T090534Z-qpu_belenos-belenos_mesh-job-12` returned every iteration at its own budget (1500 to 60000
  samples, 9 of 9). No qpu:ascella template job has carried unequal budgets. The analysis reads each iteration's
  actual samples and shots, and the caps bound time and bill whatever the service does with the samples.
- The rate of 3.069 s per iteration comes from two runs of one template at 4000 samples, and the time model adds the
  shot time on top of it. Hypothesis: the model is the right bound. The retained runs cannot tell an additive shot
  time from an overlapped one: they used 13.6 and 15.4 million shots, which at 1.43 million a second differ by about
  1.3 s, while qpu:ascella iteration time varies from 2.9 to 3.07 s across retained runs (about 5 s over 72
  iterations), and this design spends about 90 million shots a job, six times any retained job. The time to reach a
  cap of 1.5 million shots varies by about 0.1 % (a sum of geometric attempt counts). Falsifier: job-00's recorded
  duration. The transmittance floor is rounded up to four decimals.
- With no time margin, a `max_duration` cut of job-00 returns counts, so the stopping rule forbids rerunning it and
  the pool cannot be decided under this approval. Iterations that spend up
  to 1,567,000 shots assume that acquisition adds to compilation, which is the conservative reading.
