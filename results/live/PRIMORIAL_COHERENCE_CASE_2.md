# Case: primorial coherence case on ibm_kingston path 58-71-72 with a readout preflight

Status: written case awaiting the user's approval. Nothing in this file authorizes a submission.

This case repeats [PRIMORIAL_COHERENCE_CASE.md](PRIMORIAL_COHERENCE_CASE.md) on a new path, adds a readout
preflight before the probes, and keeps every other design, analysis, voiding and stop rule of that case, which
this file does not restate. The first case's stage 1 voided on physical qubit 0, which read |0> as 1 in 79 percent
of its in-job readout calibration while the backend reported 0.6 percent
(`results/live/PRIMORIAL_COHERENCE_FINDINGS.md` on branch `primorial/coherence-run`, which lands after pull request #516); the 23 s it billed bought the descriptive
qubit-1 and qubit-2 estimates and no decision.

## What changes

- **Path.** ibm_kingston physical qubits 58, 71 and 72 (`--pin-layout ibm_kingston:58,71,72`), couplers (58, 71)
  and (71, 72). With qubit 0 excluded, the path ranks first of the working paths of the calibration of
  2026-10-26T00:48:55-07:00 by the worst joint tilt-and-CZ-phase max_z at its own gate-error bounds (1.36; sx
  errors 1.6, 2.0 and 1.3 x 10^-4, CZ errors 1.1 and 1.0 x 10^-3). Its reported readout fidelities 1 - e10 - e01
  are 0.97, 0.98 and 0.90. The path's noise analysis at that calibration identifies all seven coefficients at
  3379 shots per reading (incoherent bias 0.0027, coefficient standard deviations 0.007 to 0.014 at 3200 shots
  per circuit), and the zero-error decision proceeds at a 95th-percentile max_z of 0.0009.
- **Stage 0, the readout preflight** (campaign `readout_preflight`, `gororoba_quantum/primorial_campaigns.py`):
  the probes' two readout calibrations, the path in |000> and in |111>, 1000 shots each. Its summary reports each
  wire's e10, e01 and 1 - e10 - e01 and passes only when every wire reaches the case's floor of 0.8. A failed
  preflight stops the case before any probe time is spent. A passed preflight does not exempt stage 1: the
  probes keep their own in-job readout calibration and voiding rule, because the probe job runs later.
- **Order and calibration gate.** The three approval dry runs (preflight, probes, gap-88) are made back to back
  under one calibration and must agree on every shared calibration-fingerprint value. Stage 0 is submitted,
  collected and checked; stage 1 is submitted only if stage 0 passed and the calibration still matches; stage 2
  follows the first case's decision and gate.

## Expected seconds

| | stage 0 preflight | stage 1 probes at 800 | stage 2 gap-88 at 1600 to 3200 |
| --- | ---: | ---: | ---: |
| circuits x shots | 2 x 1000 = 2,000 | 78,400 | 166,400 to 332,800 |
| expected charge (the first case's cost model) | about 3 s | about 27.5 s (stage 1 of the first case billed 23 s) | about 53 to 102 s |
| `--max-execution-seconds` and `--max-total-execution-seconds` | 30 s | 60 s | 90 to 160 s |

Account: the backup instance, which held 412 s after the first case's stage 1 (435 s read at
2026-10-26T04:49Z less the 23 s billed). The whole case expects at most about 133 s and caps at 250 s.

## Approval record and envelope

The binding approved records are submit-free dry runs made from main after this change merges, back to back,
with each command below minus `--submit` and the approval flags.

```sh
cd gororoba_quantum
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" live_run.py --groups readout_preflight --pin-layout ibm_kingston:58,71,72 --max-replicas 1 \
  --backends ibm_kingston --shots 1000 --max-execution-seconds 30 --max-total-execution-seconds 30 \
  --out ../results/live --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:58,71,72 --max-replicas 1 \
  --backends ibm_kingston --shots 800 --max-execution-seconds 60 --max-total-execution-seconds 60 \
  --out ../results/live --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:58,71,72 --max-replicas 1 \
  --backends ibm_kingston --shots N2 --max-execution-seconds C2 --max-total-execution-seconds C2 \
  --out ../results/live --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
```

This case approves the envelope: the three campaigns above on ibm_kingston path 58-71-72, their member structure,
the policy (twirl off, dd none, default repetition delay, the structure-preserving contract), stage 0 at 1000
shots and 30 s, stage 1 at 800 shots and 60 s, stage 2 at the decision's N2 between 1600 and 3200 with C2 of 90 s
to 160 s, and an expected bill of at most about 133 s. A dry run on another path, with other circuits, with a
different calibration between the stages or with an estimated charge above those needs a fresh approval. The
first case's preregistration (`results/live/2026-10-26T044954.431433Z/preregistration.json` on the run branch)
applies with the path replaced; a new preregistration with the decision sources' digests at this case's merge
commit is written into the stage-1 approval dry run before stage 0 is submitted.
