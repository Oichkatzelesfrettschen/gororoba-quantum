# Case: primorial coherence case 3, the split excitation law on 22 ibm_kingston paths

Status: approved by the user on 2026-10-27 (UTC) ("have the Advisor review the case. then execute and collect"),
within the envelope the user was shown: 22 paths including 147-148-149, the backup account, a 20 us repetition
delay, and about 25 to 40 s of quantum time.

[PRIMORIAL_COHERENCE_CASE_2.md](PRIMORIAL_COHERENCE_CASE_2.md) ran on 2026-10-26 (draft pull request #562 retains
it). Its stage 2 put three paths outside their bands: 58-71-72 on coefficients 01 and 02, 15-19-35 on 01 and 02,
and 100-101-102 on 01, all below. Its claim is descriptive, because Kingston published a new calibration label
between the stage-2 submission and its execution (every one of the 5010 snapshot values stayed equal). A
post-hoc ablation on the retained data
(`docs/evidence/primorial_cover/case2/excitation-ablation.json` on branch `primorial/case2-run`) located the
misses in the band construction, not in the coherent-error model:
- applying a path's largest excitation bound to all three of its qubits caused the 15-19-35 and 100-101-102
  misses;
- modeling q58's history-independent excess (prep0 near x_history) as an X error before the circuit caused the
  58-71-72 miss, since a terminal readout flip of that size leaves every null-subtracted coefficient unchanged
  after the in-job assignment inversion.

The variants were chosen after the data were seen, so the diagnosis is a hypothesis. Case 3 freezes it as a law
and tests it on fresh shots, with the same circuits, estimators, delay and paths.

## What it measures and why simulation cannot answer it

The device question stays the first case's: whether a coherent error on a real Heron r2 path survives the gap-88
null subtraction. Case 3 adds one question about the preparation channel. q147 reads excited in 0.06 percent of
its prep0 shots and 4.8 percent of its x_history shots (21 against 1584 of 32768), so a |1> left by the previous
shot survives the 20 us delay. Either that excess is a population the next circuit starts from, which the
null-subtracted coefficients carry, or it is a readout flip the in-job inversion absorbs. The backend reports
neither the per-qubit preparation channel nor the coherent parameters; simulation holds only bounds on both.

## The split law

`scripts/state_prep_split.py` reads the controls and gives every qubit:
- hd = max(0, (x - p) / (1 - e01 - p)), with x and p its pooled x_history and prep0 excited fractions and e01
  the largest prob_meas0_prep1 of the controls' execution calibrations: the history-dependent part, an X error of
  that probability before the circuit;
- p minus the calibration's e10, the history-independent part, a terminal readout flip added to e10.

hd carries an interval from one-sided Clopper-Pearson bounds on x and p, upper and lower each, simultaneous at
family-wise alpha 0.01 over the 4 x 66 bounds. Every prediction uses the point values. Each band widens by the
excitation envelope: per coefficient, the sum over the path's three qubits of the larger change of the
incoherent shift when that qubit's hd moves to either end of its interval
(`primorial_probe_case.split_envelope`). The history-independent part needs no envelope: it moves no
null-subtracted coefficient, since the readout3 arms invert every terminal per-qubit flip exactly (the ablation's
all-terminal variant equals zero excitation to every printed digit, reproduced by the new code).

The code reproduces the ablation's split cells exactly from the case-2 inputs: the incoherent shifts of 01 and
02 on 58-71-72, 15-19-35, 100-101-102 and 132-133-134 match to 1e-5, the ablation's printed precision.

The full decision replayed on the case-2 inputs (descriptive, made after those data were seen) admits all 22
paths at 4000 shots. On 147-148-149 the split and terminal centers lie 3.9 spreads apart, so lambda there carries
a standard error near 0.26; 58-71-72 is the only other path past 2 spreads (2.3). Every other path's centers lie
within one spread of each other, so the split law and its alternative predict alike there and the bands test the
coherent model alone. On case 2's own stage-2 biases, 58-71-72 gives lambda 1.38 +- 0.44, a post-hoc value that
selects nothing.

## Counterbalanced controls

The controls run as four jobs in the order prep0, x_history, x_history, prep0 over the 66 qubits of the 22
paths, 32768 shots each at 20 us. Counts pool by arm. The k-th prep0 job pairs with the k-th x_history job, so
each pair reads the history difference once with the x_history job after and once before its prep0 partner. A
two-proportion test between the replicates of one arm at alpha 0.01 / (2 x 66) marks a qubit heterogeneous,
and its hd interval widens to the hull of the pooled and per-pair intervals. A heterogeneous q147, or a raw
per-pair difference x_k - p_k on q147 (from the split output's counts, before the clamp at zero) that changes
sign between the two pairs, reads its excess as a job-identity effect rather than a history effect.

## Paths

The 22 paths of case 2 that its prep0 control kept, in a new pin order with 147-148-149 first, so that the
isolated crosstalk reference (the first member on the first path) sits on the path the excitation question rests
on (middle qubit second):

147-148-149, 58-71-72, 33-39-53, 3-16-23, 17-27-28, 141-142-143, 15-19-35, 60-61-62, 151-152-153, 38-49-50,
105-106-107, 118-129-128, 100-101-102, 55-59-75, 78-89-90, 66-67-68, 42-43-44, 10-11-12, 79-93-92, 132-133-134,
124-125-126, 98-111-110.

The list is the case-2 list rather than a fresh ranking, because case 3 tests predictions case 2 made on these
paths. live_run's quality policy and the prep0 drop rule still apply at the day's calibration.

## Stages

- **Stage 0, controls.** The four control jobs, submitted back to back, and stage 1 right after them, without
  waiting for any to finish: a recalibration between the controls and stage 1 stops the case (below), so the
  gap between them is kept short.
- **Stage 1, probes** (`coherence_probes`, 800 shots per circuit) on the 22 paths.
- **Decision.** `primorial_probe_case.py --decide-paths` with the split output, `--gap88-cap 4000` and
  `--positive-paths 147,148,149`:
  - the controls' execution readout, x error and T1 on every path qubit must equal the stage-1 snapshot's
    values (`split_identity`), whatever label either carries; a difference stops the case;
  - a path with a pooled prep0 excited fraction above 0.2 on any qubit is voided, as is one whose in-job
    readout falls below 0.8;
  - every other path is decided with the split law at its point values; a path proceeds under the case-2 rule
    (95th percentile of max_z below 1, identification need covered);
  - 147-148-149 enters as a positive-prediction path whatever its max_z, when its identification need is covered
    at 4000 shots. In case 2 its p95 max_z was 1.31: its probes predict that q149's 82 kHz detuning leaves a
    coherent shift on coefficient 2 the null subtraction does not cancel, so its bands test a nonzero
    prediction of the coherent model;
  - stage 2 runs at the smallest multiple of 100 between 1600 and 4000 covering the proceeding paths' need, and
    at 4000 when 147-148-149 enters, the count at which its split and terminal predictions separate furthest
    within the approval.
- **Stage 2, gap-88** (`primorial_gap88`) on the paths that enter.

## Preregistered tests

Each fixed before any case-3 shot, in the code at this case's commit:
1. **Bands.** A null-subtracted coefficient outside its band, center plus or minus (z times the quadrature sum of
   its stage-2 and probe-draw spreads, plus the excitation envelope), z = z(1 - 0.025 / (7k)) and at least 3 for
   k stage-2 paths, falsifies the split law with the coherent-error model on that path. The bands hold jointly
   at family-wise level 0.05 under the Gaussian approximation, given the hd confidence set (alpha 0.01), so at
   0.06 together.
2. **Split against terminal.** Each decision also carries the terminal center, the prediction with every hd
   read as a readout flip. `discrimination` places the observed biases on the line from the terminal center
   (lambda 0) to the split center (lambda 1) by weighted least squares, standard error 1 / d for a separation of
   d spreads; `pooled_discrimination` pools the paths with d of at least 2. lambda near 1 reads the excess as a
   population before the circuit at its all-|1> history value, near 0 as an absorbed flip, and between them as
   a population scaled by how often the previous shot left the qubit excited, which the gap-88 job's mixed
   history makes the physical expectation. lambda's standard error omits hd's own interval; the report brackets
   lambda by rerunning `discrimination` with the split centers at both ends of each path's hd interval.
3. **Calibration identity.** `falsify` counts a stage-2 member as executed under the decision's calibration when
   its label matches, or when every snapshot exported at its execution start (read once after collection and
   again at least 10 minutes later) carries the decision's channel digest: sha256 of each stage-2 qubit's e10,
   e01, T1, T2 and frequency and the duration and error of every instruction on those qubits alone. A
   calibration change during a member's shots makes the result descriptive.
4. **Crosstalk.** The case-2 chi-square check of the first member on the first path against its isolated
   reference, now on 147-148-149 when it enters.

## Scope cuts

Two items of the case-3 plan are out of this run, each because it needs a live_run change:
- a repeated-measurement control arm (measure, measure) that would separate a real excited population from
  misassignment directly; test 2 answers the same question through the gap-88 coefficients;
- isolated references on all five decisive paths; the single reference moves to 147-148-149.

## Stops

The case stops and returns to the user when:
- fewer than 12 paths remain at any stage;
- a control ends in error 1305 or bills above its 8 s ceiling;
- `state_prep_split.py` or `--decide-paths` refuses its inputs, including a channel difference between the
  controls and the stage-1 snapshot;
- the billed seconds so far plus stage 2 scaled from case 2's billed rate (11 s at 2700 shots, so N2 x 11 /
  2700 s) exceed 40 s, or the stage-2 dry run exceeds its 30 s ceiling.

## Expected seconds

Case 2 billed, at 20 us on the same paths: 3 s for each 69-qubit control, 5 s for stage 1 at 800 shots, and
11 s for stage 2 at 2700 shots. Billing scales with shots times (delay plus circuit) per PUB and not with
width, so:

| stage | shots | expected | ceiling |
| --- | ---: | ---: | ---: |
| four controls, 66 qubits | 32768 each | 12 s | 8 s each |
| stage 1, probes | 800 | 5 s | 15 s |
| stage 2, gap-88 | 4000 (1600 to 4000) | 16 s (7 to 16 s) | 30 s |
| total | | 33 s | 77 s |

The backup instance held 390 s at 2026-10-27T00:35Z.

## Dry runs

Made from commit ce37063 (the decision code above, pushed before any submission) at the calibration of
2026-10-26T17:15:01-07:00, all 22 paths admitted by live_run's quality policy:

| record | campaign | PUBs | shots | record.json sha256 |
| --- | --- | ---: | ---: | --- |
| `2026-10-27T005603.796934Z` | state-prep-control prep0 (A) | 1 | 32768 | `30215a9ee48a63d211215d565ec6b0453b4b97b91c8c86a65cb706153dd04b89` |
| `2026-10-27T005625.918478Z` | state-prep-control x_history (A) | 1 | 32768 | `a5764b91ead604c027009c6583b81d5205c7cc49ccbf049ffe0d204dcc3f2849` |
| `2026-10-27T005647.453920Z` | state-prep-control x_history (B) | 1 | 32768 | `bdffb066cfcfa53daa4f1ce427308618a99b262a5dc109bbfda87c43a4a39cf6` |
| `2026-10-27T005707.592661Z` | state-prep-control prep0 (B) | 1 | 32768 | `8f8596b420bdaf6449ea9013e1b4022a6c0f500ecf8b4709465d531fe06f8cff` |
| `2026-10-27T005728.992643Z` | coherence_probes, 22 paths | 99 | 800 | `0191048c876174937a497ecb42d393050290b1c1f53a7924b43dc7bec786741c` |
| `2026-10-27T005842.636425Z` | primorial_gap88, 22 paths (representative) | 105 | 4000 | `bc0d5c16b2e8573f06fc30bb72e720cea28d55a934d8ceb19b865ade7be2565b` |

These records, made from ce37063, are superseded: commit 386011f changed `falsify` before any submission, and
Kingston recalibrated to 2026-10-26T17:47:10-07:00. The binding approved records, each made immediately before
its own submission from 386011f:

| record | campaign | record.json sha256 | submitted run |
| --- | --- | --- | --- |
| `2026-10-27T010649.227019Z` | prep0 (A) | `f1accbbcb4fe43b7b1d8cea867b28e35d6c7bab241a1267e5537bb6e3742e836` | `2026-10-27T010741.272123Z` |
| `2026-10-27T010823.590534Z` | x_history (A) | `3259a74820355d38868fb269b2ff5db9c3720efbd2dec14068f9f310a652e84a` | `2026-10-27T010917.104805Z` |
| `2026-10-27T010945.923159Z` | x_history (B) | `380b115c39506022d4a48d005f541357e6ab1060597b77cf7a43c769eae01ba2` | `2026-10-27T011025.944327Z` |
| `2026-10-27T011052.603194Z` | prep0 (B) | `b03a55314dec5870521a6e246adccf74547230dba3a4fe52ec8ed8a5ad1e65ff` | `2026-10-27T011140.821404Z` |
| `2026-10-27T011212.783117Z` | coherence_probes | `83e278b2d903686bf643fe24c3aebe22df17a5c9d0911a911e30fade842984c5` | `2026-10-27T011538.241671Z` |
| `2026-10-27T013519.244840Z` | primorial_gap88, 4000 shots | `3e2eab8a7a076f9fb04ae81da78a0bf6608ce4a84d21d18b043a915acdcf705c` | `2026-10-27T013626.332783Z` |

Results: [case3/README.md](../../docs/evidence/primorial_cover/case3/README.md).

## Commands

From `gororoba_quantum/`, with `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`,
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `PATHS` the pin above and `QUBITS` its 66 qubits. Each
submission is its own dry run's command plus `--submit --approved-record RECORD_DIR
--approved-record-sha256 SHA256`.

```sh
for arm in prep0 x_history x_history prep0; do
  "$PYTHON" live_run.py --family state-prep-control --layout QUBITS --state-prep-arms $arm --max-replicas 1 \
    --backends ibm_kingston --shots 32768 --rep-delay 2e-05 --max-execution-seconds 8 \
    --max-total-execution-seconds 8 --out ../results/live
done
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:PATHS --max-replicas 22 \
  --backends ibm_kingston --shots 800 --rep-delay 2e-05 --max-execution-seconds 15 \
  --max-total-execution-seconds 15 --out ../results/live
"$PYTHON" ../scripts/state_prep_excess.py --fetch-readout CONTROL_RUN        # each of the four
"$PYTHON" ../scripts/state_prep_split.py --control PREP0_A --control XH_A --control XH_B --control PREP0_B \
  --out SPLIT
"$PYTHON" calibration_snapshot.py --export ibm_kingston --at STAGE1_EXECUTION_START --out SNAPSHOT
"$PYTHON" ../scripts/primorial_probe_case.py --decide-paths STAGE1_RUN --excess SPLIT --snapshot SNAPSHOT \
  --gap88-cap 4000 --positive-paths 147,148,149 --out DECISION
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:STAGE2_PATHS --max-replicas K \
  --backends ibm_kingston --shots N2 --rep-delay 2e-05 --max-execution-seconds 30 \
  --max-total-execution-seconds 30 --out ../results/live
"$PYTHON" calibration_snapshot.py --export ibm_kingston --at STAGE2_EXECUTION_START --out STAGE2_SNAPSHOT_A
"$PYTHON" calibration_snapshot.py --export ibm_kingston --at STAGE2_EXECUTION_START --out STAGE2_SNAPSHOT_B
"$PYTHON" ../scripts/primorial_probe_case.py --crosstalk STAGE2_RUN --group primorial_gap88 --out CROSSTALK
"$PYTHON" ../scripts/primorial_probe_case.py --falsify STAGE2_RUN --decision DECISION \
  --crosstalk-verdict CROSSTALK --stage2-snapshot STAGE2_SNAPSHOT_A --stage2-snapshot STAGE2_SNAPSHOT_B \
  --out FALSIFICATION
```

The second stage-2 export runs at least 10 minutes after the first. The decision takes about 13 minutes on the
build host for 22 paths, the stage-1-to-stage-2 gap a recalibration can fall into; test 3 then decides by
channel values.
