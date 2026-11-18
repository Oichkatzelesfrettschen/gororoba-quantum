# Written case: the QX remote run of the bracketed one-CZ-null series (four batches, zero credits)

Status: unsubmitted; waits for the owner's approval. Runs from the PR 881 worktree (the case exists only on that branch).

- What it measures: the plumbing of the in-batch bracketed layout on the hosted QX emulator: syntax as the platform parses it,
  a batch of five circuits (`[readout-0, coin-0 twin, coin-1 twin, readout-1, base]`), result width and order, and the QX
  control of `qi_pathion_one_cz_null_bracketed_cases.py --analyze` on noiseless data with a known answer (every circuit within
  twice its sampling floor, no misassigned readout shot, bracketed twin contrast equal to raw). It says nothing about
  Tuna-17. The remote QX applies qxelarator 0.10.0's reset map (2026-11-15 probe), which this series does not use.
- Why a local run cannot answer it: the local qxelarator run of the same 20 circuits already passes (retained, gate
  `core-pathion-one-cz-null-bracketed-qx-local-control`); only the hosted emulator shows the submit, batch and collection path and
  the platform's parser on the exact bytes before Tuna-17 depends on them.
- Backend: QX emulator (type 1), status idle, account queue empty at 2026-11-15T17:48Z.
- Shots: 4 batches x 5 circuits x 2048 shots = 40,960 shots (the emulator's maximum per job is 2048).
- Expected seconds: under 120 in all (the retained QX jobs of 2026-11-15 finished in 0.2 s each). Expected credits: 0.
- Boundary: one series, no resubmission of any run directory; no Tuna-17 or Ry job; no cancellation of any other worker's job.
- Command: `sh scripts/qi_pathion_one_cz_null_submit.sh 1 CASES/pathion_one_cz_null_bracketed_qx RUNS STAMP "<owner's words>"`, then
  `--analyze` into `results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json`. Never repeat a submit that left a
  `submission-state.json`.
- Pass: the analysis reports `qx_control.pass` and `qx_brackets.pass` true; otherwise the deviation is reported as found.
