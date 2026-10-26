# Case: primorial coherence case on 23 ibm_kingston paths at a 20 or 50 us repetition delay

Status: written case awaiting the user's approval. Nothing in this file authorizes a submission.

This case repeats [PRIMORIAL_COHERENCE_CASE.md](PRIMORIAL_COHERENCE_CASE.md) on 23 three-qubit paths at once,
adds a readout preflight at two repetition delays before the probes, and keeps that case's probe and gap-88
circuits, its estimators, its stage-2 decision rule and its calibration-identity gate, which this file does not
restate. The first case's stage 1 ran one path and voided on physical qubit 0, which read |0> as 1 in 79 percent of
its in-job readout calibration while the backend reported 0.6 percent (`results/live/PRIMORIAL_COHERENCE_FINDINGS.md`
on branch `primorial/coherence-run`, which lands after pull request #516). The review that shaped this design is
[primorial-coherence-case-2-review.md](../../docs/archive/reviews/primorial-coherence-case-2-review.md).

## What it measures and why simulation cannot answer it

The question is the first case's: whether a coherent error on a real Heron r2 path survives the gap-88 null
subtraction that cancels every single error family to first order. The answer rests on each path's drive-axis
tilt, CZ conditional phase, static detuning and ZZ rates, which the backend's calibration does not report and
which the joint-bound analysis showed can reach max_z 2.6 to 2.8 together at gate-error bounds. Simulation holds
only those bounds; the probes measure the values.

## The paths

IBM bills shots times (repetition delay plus circuit) per job, independent of how many qubits a PUB measures
([qpu_run_economy.md](../../docs/notes/qpu_run_economy.md), rule 11). The case therefore runs every member on 23
paths at once, as one replica per path in each PUB. At the calibration of 2026-10-26T00:48:55-07:00 these are the
paths of the 226-path joint-bound ranking, taken greedily in ranking order, that avoid qubit 0, read at a reported
1 - e10 - e01 of at least 0.9 on every qubit, admit the gap-88 fit, and keep one CZ hop from every other path (no
coupler joins qubits of two paths), the separation live_run keeps between replicas of one group. Middle qubit
second:

58-71-72, 33-39-53, 3-16-23, 17-27-28, 141-142-143, 15-19-35, 60-61-62, 151-152-153, 82-83-96, 38-49-50,
105-106-107, 118-129-128, 100-101-102, 55-59-75, 78-89-90, 66-67-68, 42-43-44, 10-11-12, 79-93-92, 132-133-134,
124-125-126, 98-111-110, 147-148-149.

Their worst joint max_z at their own gate-error bounds spans 1.36 to 2.57, so the set does not favor the paths
where a bounded coherent error is least visible. The pin is `--pin-layout ibm_kingston:58,71,72/33,39,53/...` in
this order; live_run maps each member onto every path with the calibration score of that path, refuses a path
that is inadmissible or within one CZ hop of another, and adds the isolated reference PUB (the group's first
member on the first path alone).

## Stages

- **Stage 0, readout preflight at two delays.** The `readout_preflight` campaign (the probes' two readout
  calibrations, every path in |000> and in |111>) runs as two jobs, first at a 50 us repetition delay, then at
  20 us, 8000 shots per circuit. Under column-wise execution the |000> circuit's shots follow |111>-ending shots,
  the worst preparation history ([qpu_run_economy.md](../../docs/notes/qpu_run_economy.md), rule 7), as long as
  the service keeps the documented column order. `scripts/primorial_probe_case.py --decide-delay` applies the
  rule:
  - a path is retained when every wire's 1 - e10 - e01 reaches 0.8 at 50 us;
  - the case runs at 20 us when every retained path also reaches 0.8 at 20 us and its zero-estimate decision at
    3200 shots still proceeds with each wire's e10 raised by the upper bound (estimate plus two standard errors)
    of its excess excitation, e10 at 20 us less e10 at 50 us; otherwise at 50 us. The repository measured equal
    initialization error at 50 us and 250 us on other Kingston qubits; 20 us is unmeasured, and this rule is its
    state-preparation control (rule 1). At the snapshot's circuit durations a 20 us execution costs about half a
    50 us one, so the rule prefers it whenever no path is lost.
- **Stage 1, probes** (`coherence_probes`, 800 shots per circuit) on the retained paths at the chosen delay.
  `--decide-paths` voids a path whose in-job readout calibration falls below 0.8 on any wire (from that path's
  own `cp_readout` distributions), decides every other path at 3200 gap-88 shots from its own per-replica summary
  (`summary_per_replica`, raw distributions with that path's in-job inversion), sets N2 to the smallest multiple
  of 100 between 1600 and 3200 that covers the largest 95th-percentile identification need among the paths that
  proceed, and decides those paths again at N2. At 20 us every decision reads the snapshot with each wire's e10
  raised by its excess.
- **Stage 2, gap-88** (`primorial_gap88`, N2 shots per circuit) on the paths that proceed. Each path's falsifier
  band is Bonferroni over the k paths in stage 2: the predicted largest bias from its 0.025/k to its 1 - 0.025/k
  quantile, widened by z(1 - 0.025/k) (at least 3) of the largest coefficient standard deviation and by the
  path's incoherent bias. A path whose stage-2 largest bias leaves its band falsifies the coherent-error model on
  that path; the device-question claim names every such path, and the family-wise false-alarm rate is at most
  0.05.

## Crosstalk

Paths one CZ hop apart share no coupler, so no static ZZ acts directly between qubits of two paths; drive
crosstalk and next-nearest ZZ through a shared neighbor remain. The gap-88 and null members are one parametrized
circuit, so every path's physical pulse stream (sx, x, CZ and their timing) is identical in both and only the
virtual-Z frames differ; drive crosstalk is therefore common to the signal and the null arms, and only the
state-dependent next-nearest ZZ can differ between them. `--crosstalk RUN --group primorial_gap88` tests the
first path's gap-88 counts in the packed PUB against the isolated reference with a chi-square homogeneity test
at 0.01. It covers the gap-88 member only, so it bounds half of the null-subtracted crosstalk term. If it
detects crosstalk, the stage-2 result is reported as descriptive and makes no device-question claim. The same
check on stage 1 is reported and binds nothing.

## Path drops without discretion

The approved envelope covers any subset of the 23 paths that these rules leave, in the listed order:
- a path with a qubit that live_run's quality policy excludes, or whose reported 1 - e10 - e01 falls below 0.8,
  at the calibration of a binding dry run;
- a path the stage-0 rule does not retain;
- a path stage 1 voids or that does not proceed.

If fewer than 12 paths remain at any stage, the case stops and returns to the user. Each stage's binding dry run
is made after the previous stage is collected, at that stage's path subset and delay, and the stage's submission
carries that dry run as its approved record.

## Expected seconds

Stage 1 of the first case billed 23 s for 78,400 executions at the 250 us default, 264 us each against a mean
probe circuit of 5.1 us, leaving about 9 us of fixed time per execution (2 to 15 us within the bill's rounding).
The gap-88 circuits average 3.0 us. With the isolated reference PUB in each job:

| | stage 0 at 50 us | stage 0 at 20 us | stage 1 (800 shots) | stage 2 at N2 = 1600 | stage 2 at N2 = 3200 |
| --- | ---: | ---: | ---: | ---: | ---: |
| executions | 3 x 8000 | 3 x 8000 | 99 x 800 | 105 x 1600 | 105 x 3200 |
| expected charge at 20 us | | 3.0 s | 5.0 s | 7.7 s | 13.1 s |
| expected charge at 50 us | 3.8 s | | 7.4 s | 12.7 s | 23.1 s |
| `--max-execution-seconds` and `--max-total-execution-seconds` | 10 s | 10 s | 20 s | 40 s | 40 s |

The whole case expects 19.5 s at 20 us and N2 = 1600 and at most about 37 s at 50 us and N2 = 3200, and caps at
80 s, on the backup instance, which held 412 s after the first case's stage 1. The first case's single-path
design expected 133 s for one path.

The raw archive grows with the width: stage 2 at 3200 shots holds about 105 x 3200 shot strings of 69 bits, near
25 MB of JSON, and stage 1 about 6 MB.

## Approval record and envelope

The binding approved records are submit-free dry runs made from main after this change merges, each the command
below minus `--submit` and the approval flags, with PATHS the `/`-joined surviving paths, K their count and DELAY
the chosen delay:

```sh
cd gororoba_quantum
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" live_run.py --groups readout_preflight --pin-layout ibm_kingston:PATHS --max-replicas K \
  --backends ibm_kingston --shots 8000 --rep-delay 50e-6 --max-execution-seconds 10 \
  --max-total-execution-seconds 10 --out ../results/live --submit --approved-record RECORD_DIR \
  --approved-record-sha256 RECORD_SHA256
# the same at --rep-delay 20e-6; then
"$PYTHON" scripts/primorial_probe_case.py --decide-delay RUN_20 --preflight-slow RUN_50 --snapshot SNAPSHOT --out V0
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:PATHS --max-replicas K \
  --backends ibm_kingston --shots 800 --rep-delay DELAY --max-execution-seconds 20 \
  --max-total-execution-seconds 20 --out ../results/live --submit --approved-record RECORD_DIR \
  --approved-record-sha256 RECORD_SHA256
"$PYTHON" scripts/primorial_probe_case.py --decide-paths RUN_1 --delay-verdict V0 --snapshot SNAPSHOT --out V1
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:PATHS --max-replicas K \
  --backends ibm_kingston --shots N2 --rep-delay DELAY --max-execution-seconds 40 \
  --max-total-execution-seconds 40 --out ../results/live --submit --approved-record RECORD_DIR \
  --approved-record-sha256 RECORD_SHA256
"$PYTHON" scripts/primorial_probe_case.py --crosstalk RUN_2 --group primorial_gap88 --out V2
```

SNAPSHOT is the calibration snapshot the stage-1 dry run exports; stage 2 proceeds only under the calibration
identity gate of the first case, comparing every shared calibration-fingerprint value of the stage-1 and stage-2
dry runs. A usage read precedes each submission. `--max-pending` is set to the queue the operator observes at
submission; a deep queue delays a job and changes neither its charge nor its calibration gate.

This case approves the envelope: the three campaigns above on any rule-made subset of the 23 listed paths, their
member structure, the policy (twirl off, dd none, the structure-preserving contract, a 20 or 50 us delay as the
stage-0 rule chooses), stage 0 at 8000 shots and 10 s per job, stage 1 at 800 shots and 20 s, stage 2 at the
decision's N2 between 1600 and 3200 with 40 s, and an expected bill of at most about 37 s against an 80 s cap. A
path outside the list, other circuits, a delay the rule did not choose, a calibration change between stages 1
and 2, or an estimated charge above those needs a fresh approval. The first case's preregistration
(`results/live/2026-10-26T044954.431433Z/preregistration.json` on the run branch) applies with the rules above
replacing its single-path decision; a new preregistration with the decision sources' digests at this case's
merge commit is written beside the stage-0 approval dry run before stage 0 is submitted.
