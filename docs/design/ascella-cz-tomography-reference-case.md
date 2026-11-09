# Ascella CZ process tomography reference above 90 % HOM

This is the written case for two qpu:ascella jobs of 72 template iterations that repeat the CZ process tomography of
[ascella-cz-process-tomography-case.md](ascella-cz-process-tomography-case.md) at a calibration whose HOM visibility
exceeds 90 %. [scripts/ascella_cz_tomography_reference_case.py](../../scripts/ascella_cz_tomography_reference_case.py)
builds the frozen requests in
[results/quandela/cases/ascella_cz_tomography_reference](../../results/quandela/cases/ascella_cz_tomography_reference/job-00/cases.json),
checks them, forecasts the outcome over the admitted HOM range and gates every submission. Nothing has been sent or
approved. The approval rule of gororoba-quantum `AGENTS.md` ("Hardware services") governs the submission.

## Why the case exists

The CZ compilation ensemble ([ascella-cz-compilation-ensemble-case.md](ascella-cz-compilation-ensemble-case.md))
compares its tables with the prediction of a retained process tomography. The owner's ruling of 2026-11-08 admits an
ensemble job only at a HOM strictly above 90 % and within one point of that tomography's HOM. The retained
tomography ran at 87.56 %, so no HOM satisfies both conditions and the ensemble refuses every plan by design. A
tomography acquired above 90 % gives the ensemble a non-empty band, `max(90, ref - 1) < HOM <= ref + 1`. Paired with
the retained tomography at 87.56 %, it also measures one change in process fidelity across HOM. That change is
descriptive, because two calibrations differ in more figures than HOM.

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
| Status | available (the read 20 minutes earlier showed `calibration`) |
| HOM | 88.76 % (the earlier read: 88.54 %) |
| g2 | 2.0 % |
| Transmittance | 5.51 % |
| Clock | 13.33 MHz |

The gate refuses this read at HOM, so the case waits for a calibration above 90 %.

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

Every iteration shares one shot cap, `SHOT_CAP` = 990,000. Each setting takes its own `max_samples`: the largest
multiple of 100 whose shots, scaled from Perceval's estimate at 4000 samples
([shot-estimate.json](../../results/quandela/cases/ascella_cz_tomography_reference/shot-estimate.json), the same
perfs as the platform read) and multiplied by the retained margin of 1.25, stay within the cap. The retained runs
measured 0.89 to 1.18 times Perceval's per-setting estimate, so the margin of 1.25 covers them.
[qd_platform.payload](../../scripts/qd_platform.py) sends each template iteration under its own budgets, and
`qd_records.iteration_form` validates them: positive integers, `max_shots >= max_samples`, summing to the manifest's
totals.

The objective follows from the bill and the clock: maximize the precision of the process fidelity for a given credit
ceiling, within 300 s. The bill rises with the largest cap and the time with the sum of the caps. With 72 equal
caps of 990,000, the summed caps take 50 s of the 79 s shot budget, so the time constraint has slack and the bill
binds. Lowering any one iteration's cap would save nothing and lose precision. Raising one would raise the bill of
the whole job. Equal caps are therefore optimal at this ceiling, and the per-shot term stays below one credit per
job, 0.99.

| Quantity | Retained design | This design |
|---|---|---|
| Samples per iteration | 4000 each | 2400 to 22400 (the four in-10 settings with a Z readout on the target: 7400; in-10-ZZ: 2400) |
| Samples per job | 288,000 | 1,282,800 (job-00), 1,222,800 (job-01) |
| Largest `max_shots` | 400,000 and 1,600,000 | 990,000 in both jobs |
| Credits | 1.4 + 2.6 = 4.0 | 1.99 + 1.99 = 3.98 |
| Expected eligible events | about 99,000 | about 390,000 |
| Process-fidelity spread (delta method) | 0.0104 | 0.0051 |
| Worst case, every iteration at its cap | 301 s at T = 5.51 % | 271 s at T = 5.51 % |

The spread is the delta-method standard deviation of the unprojected fidelity, F = (r . a) / (r . b), under the
record forecast variant at each HOM of the curve below (`fidelity_sd`). It is 2.05 times smaller than the retained
design's at every HOM point. The two designs differ only in where the shots go, so the spread scales with how the
budget is spent. The same expression reproduces the retained run's interval: 0.0104 against the measured 95 %
interval of 0.828 to 0.869, which corresponds to a standard deviation of about 0.0105.

The cap is the owner's credit choice. With the transmittance at 5.51 %, the largest cap whose worst case fits
300 s is (300 - 221) s x 1.43 million / 72 = 1.567 million. That costs 2.57 credits per job (5.13 for the pair) and
narrows the spread by a further factor of sqrt(1.567 / 0.99) = 1.26. At 990,000 the case keeps the retained ceiling
of 4.0 credits.

## Why the request cannot follow the live HOM

The request is frozen when the case is built, and the gate only admits or refuses it.

- The owner's approval names the frozen request. `qd_platform.submit` binds the receipt to the `cases.json` digest,
  and `bind_reviewed` requires the posted body to equal the admitted preflight's body, minus `process_id`. A body
  rebuilt at submit time from the live read is a request nobody reviewed.
- The token reads HOM and cannot set it. A job queues and runs after the read, so a design keyed to one reading
  describes a calibration the job may no longer run on. The gate's in-lock re-read and the equality of the
  estimate's perfs with the plan's narrow that window, without closing it.
- The design depends on HOM only weakly. The samples follow the shots per sample, which transmittance sets. HOM
  moves the bunching of the two photons and so the shots per sample by a few percent, which the margin of 1.25 and
  the plan's live estimate check cover.
- The forecast follows the same split. No read above 90 % exists to forecast at, and the repository forbids guessing
  hardware figures. The forecast is therefore a curve over the admitted HOM range at the read's other figures, and
  the plan read at submission picks the point.

A family of pre-approved variants, one per HOM bin, would make the request dynamic within its approval. It changes
nothing measured: the estimand, the settings and the budgets are the same at every HOM above 90 %, because
transmittance sets the budgets.

## Seeds

Every new seed comes from one fresh ANU QRNG draw,
[draw-2026-11-09T020604Z.json](../evidence/anu_qrng/draw-2026-11-09T020604Z.json) (256 uint16 values). The rule is
nonzero values in index order, repeats skipped, and none was skipped.

| Use | Indices |
|---|---|
| 144 compilation seeds, schedule order | 0 to 143 |
| Bootstrap seed of the analysis | 144 |
| One synthetic dataset per forecast HOM point | 145 to 151 |
| Owned and unused | 152 to 255 |

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

- the HOM at the plan is strictly above 90 % (`qd_platform.HOM_FLOOR`);
- the transmittance is at or above the floor at which every iteration at its cap still fits 300 s, which is 3.444 %;
  below about 4.4 %, the plan's own check of Perceval's live estimate against each cap refuses first;
- the Explorer row and the processor read `available` or `running`, while the token counts no running, no queued and
  no running quantum-task job;
- the shot estimate and a processor read taken inside the lock carry the plan's perfs, and source modes 0 and 2
  are connected;
- for job-01, a collected job-00 run completed with all 72 iterations counted;
- the plan equals the admitted preflight: the case digest, the body minus `process_id`, the perfs and the predecessor
  run.

The credit ceiling per job is 1.99. The expected time is 261 s: the iterations' recorded seconds plus the shots
the samples need, the cap divided by 1.25, at the read's shot rate.

## Forecast over HOM

[forecast.json](../../results/quandela/cases/ascella_cz_tomography_reference/forecast.json) evaluates the retained
case's noise pipeline at each HOM point, holding the read's g2, transmittance, clock and dark counts. Each point
gives two estimands: one from indistinguishability alone and one from the record variant, which includes the source,
loss and dark counts. Each point also carries the design's delta-method spread and one synthetic dataset of this
design, analyzed as a run would be.

| HOM % | Indistinguishability only | Record variant | Spread | Synthetic dataset | 95 % interval |
|---|---|---|---|---|---|
| 90.5 | 0.870 | 0.818 | 0.0050 | 0.814 | 0.805 to 0.824 |
| 91.0 | 0.876 | 0.824 | 0.0051 | 0.811 | 0.803 to 0.821 |
| 91.5 | 0.883 | 0.829 | 0.0051 | 0.833 | 0.823 to 0.842 |
| 92.0 | 0.889 | 0.835 | 0.0051 | 0.837 | 0.828 to 0.847 |
| 92.5 | 0.895 | 0.841 | 0.0051 | 0.838 | 0.828 to 0.848 |
| 93.0 | 0.902 | 0.847 | 0.0051 | 0.850 | 0.840 to 0.860 |
| 94.0 | 0.915 | 0.858 | 0.0051 | 0.854 | 0.844 to 0.864 |

The record variant rises about 0.0115 in process fidelity per point of HOM. The design resolves that step at about
two standard deviations per point. The retained run measured 0.849 at 87.56 %, above every variant at its read, so
the curve gives a floor for the outcome rather than a prediction of it.

## Stopping rule

- A terminal error with no counted iteration allows one resubmission of the identical body under the same approval,
  after the gate passes again. A second error stops the case.
- A job that returned counts is never resubmitted under this approval.
- A truncation leaves the pool undecided. Running the missing settings is a new written case.
- A plan that reads 90 % or below sends nothing, and the case retries it at a later calibration. The HOM floor is
  never waived.
- A pool decided by the retained case's tolerances (HOM within 1.0 point, transmittance within 0.3 points,
  submissions within 12 hours) replaces the ensemble's `TOMOGRAPHY_RUNS` in one change. That change regenerates the
  ensemble's prediction, manifests and ledger rows, and the ensemble's preflights are then taken again.

## Procedure after approval

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASE=scripts/ascella_cz_tomography_reference_case.py
"$PYTHON" "$CASE" --preflight job-00
"$PYTHON" "$CASE" --submit job-00 --approval "APPROVAL TEXT"
# collect job-00 into its run directory with scripts/qd_platform.py collect, then:
"$PYTHON" "$CASE" --preflight job-01 --after RUN_00
"$PYTHON" "$CASE" --submit job-01 --approval "APPROVAL TEXT" --after RUN_00
"$PYTHON" "$CASE" --analyze results/quandela/ascella-cz-tomography-reference-analysis.json RUN_00 RUN_01
```

## Checks

| Check | Result |
|---|---|
| `ascella_cz_tomography_reference_case.py --check` | passes: both requests rebuild byte for byte, every iteration's samples fill the cap to one quantum, worst case 270.9 s, ceiling 1.99, fresh disjoint seeds, design spread below the retained design's at every HOM point |
| `ascella_cz_tomography_case.py --check` | passes: the retained requests still rebuild byte for byte after the loader and pooling take a family |
| `qd_platform.py --self-test` | passes, with budgeted and unbudgeted template cases and three malformed budget lists |
| `tests/scripts/test_ascella_cz_tomography_reference_case.py` | the gate's refusals, the floors, the budgets and the rebuild |

## Limits

- The fit is one Choi matrix of 144 mesh-specific tables, as in the retained case. Fresh compilation seeds give new
  meshes, so the HOM comparison carries compilation variation.
- Unequal samples per setting leave the estimator's unweighted linear inversion unchanged: the rates divide by each
  iteration's shots. The settings of input |1>|0> carry fewer samples and a wider share of the spread.
- The rate of 3.069 s per iteration comes from two runs of one template at 4000 samples. Iterations that spend up
  to 990,000 shots assume that acquisition adds to compilation, which is the conservative reading.
