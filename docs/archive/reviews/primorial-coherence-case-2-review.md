# Adversarial review: primorial coherence case 2 (first draft)

Subject: `results/live/PRIMORIAL_COHERENCE_CASE_2.md` as first pushed on pull request #551, a single-path repeat
of the first primorial coherence case on ibm_kingston 58-71-72 with a readout preflight. The review held it to
the run-economy rules of [qpu_run_economy.md](../../notes/qpu_run_economy.md) and to the owner's constraint that the
plan bills per QPU second, uses the widest placement each moment allows and runs at a repetition delay of 20 to
50 us. Inputs: the Kingston snapshot of 2026-10-26T00:48:55-07:00, its 226-path joint-bound ranking, the stage-1
record of the first case (job `dbfdotnpc3tc739n8nm0`) and live_run.py's replica placement.

## Findings, worst first

1. **Fatal to the economy: three qubits of 156 per billed second.** The charge is shots times (repetition delay
   plus circuit) per job, independent of width (rule 11). At the snapshot's calibration, 23 three-qubit paths
   that avoid qubit 0, read at a reported 1 - e10 - e01 of at least 0.9 and keep one CZ hop from each other fit
   on Kingston (69 qubits), the same separation live_run's replica placement enforces within a group
   (`within_group_one_hop_separated`). The draft buys one path's answer at the price of 23. It also keeps the
   first case's single point of failure: one qubit's readout voided that whole case, where a per-path void would
   have cost one path of 23.
2. **Serious: the 250 us default delay is 95 percent of every execution.** Stage 1 of the first case billed 23 s
   for 78,400 executions, 264 us each, so the probe circuits average about 14 us; the draft's 102 s gap-88 estimate
   implies about 50 us per gap-88 circuit. At 50 us of delay stage 1 costs about 2.3 + 78,400 x 64 us = 7.3 s and
   stage 2 at 3200 shots about 2.3 + 332,800 x 100 us = 35.6 s; at 20 us, 5.0 s and 25.6 s. Rule 1 requires a
   state-preparation control on the run's own qubits for any delay below the default, which the draft lacks.
   The n21 control measured equal initialization error at 50 us and 250 us on other Kingston qubits; 20 us is
   unmeasured on this device.
3. **Serious: path selection favors the null.** The ranking orders paths by the joint max_z their own gate-error
   bounds allow, ascending, so the chosen path is the one where a bounded coherent error is least visible. A
   multi-path design that keeps every separated path spanning max_z 1.36 to 2.57 removes the selection.
4. **Serious once several paths run: family-wise error.** A falsifier band at 95 percent per path makes a false
   excursion likely somewhere among 23 paths. The decision and the device-question claim need a family-wise
   rule (Bonferroni over the paths that reach stage 2) and a per-path report.
5. **Serious once several paths run: spectator crosstalk.** Paths running together add drive and CZ crosstalk
   that the single-path noise model lacks. One-hop separation removes direct static ZZ between active qubits of
   different paths, and live_run's isolated reference entry (the primary member alone on its path) measures what
   remains for that member; the draft names no check on it.
6. **Sloppy: the N2 rule names one path.** With several paths the shot count needs a preregistered rule over the
   paths' decisions, and a rule for a path whose need exceeds the cap.
7. **Sloppy: 1000 preflight shots resolve the 0.8 floor but not a delay comparison.** e10 near 0.01 at 1000 shots
   has a standard error of 0.003; a 20-versus-50 us excitation difference of 0.005 needs about 8000 shots per
   circuit, which at two circuits costs 0.35 s of shot time.

## What holds

- The in-job readout calibration and its voiding floor caught qubit 0 before any gap-88 time was spent; the
  compiled circuits (`isa.qpy`, PUBs 97 and 98) measure physical qubits 0, 1 and 2 into clbits 0, 1 and 2, so the
  fault sits on physical qubit 0.
- The preflight's two circuits alternate under column-wise execution, so the |000> circuit's shots follow
  |111>-ending shots, the worst preparation history rule 7 names, as long as the service keeps the documented
  column order; the repetition-rate guide gives no order guarantee within a job.
- The calibration drift stop binds approval to values rather than timestamps (rule 12).

## Revision

The revised case runs every member on the 23 separated paths at once in each stage and decides per path with a
Bonferroni falsifier band. It runs the readout preflight at 50 us and at 20 us and takes the shorter delay only
when no retained path fails the readout floor there and every retained path's decision still proceeds with its
measured excess excitation, and it tests crosstalk through the isolated reference with a preregistered
consequence. live_run.py takes several `/`-separated pinned paths as one replica each
(`pinned_replicas`), and `scripts/primorial_probe_case.py` gains `--decide-delay`, `--decide-paths` and
`--crosstalk`.
