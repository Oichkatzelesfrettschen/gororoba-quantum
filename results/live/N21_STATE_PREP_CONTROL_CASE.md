# n21 on ibm_kingston: state-preparation control, then the feedback run

## What the program measures

Stage 1 measures the excited fraction left on every admitted ibm_kingston
qubit by the Sampler's implicit initialization (`init_qubits`), after two
shot histories and at two repetition delays:

- prep0 (init, measure): shots that end near `|0>`.
- x_history (init, measure, x): shots that end near `|1>`, the worst end
  state an n21 shot leaves behind.

Stage 2 runs n21-feedback-encoded at 50 us with the `--prep-excitation`
that stage 1 bounds on its placement. The calibration noise model starts
every qubit in `|0>` with no shot history, so only the device measures the
excitation a short delay leaves behind.

## Approval

The owner approved the two-stage program and its preregistered rule, then
granted a standing approval for the four control jobs. The approval covers
the four control commands with every qubit the calibration admits at the
dry run's publish (`live_run.take_snapshot`), and the shots, delays and
ceilings below. It also covers the stage-2 plan that the rule selects. Each
submission named its own dry run by `--approved-record` and
`--approved-record-sha256`, and the runner's comparison of every
approval-bound field ran unchanged. A fixed 151-qubit layout failed one
window, because the 08:02:58Z calibration excluded q92 (readout error 0.111)
and q138 (0.131); the admitted-set rule replaced it. Unsent attempts
retained no job and are not kept.

## Stage 1 records (calibration 2026-10-18T01:02:58-07:00, 149 qubits)

All of 0..155 except 92, 113, 115, 121, 138, 139 and 146. One PUB per job
fuses 149 one-qubit members; each arm and delay is its own job, because
`rep_delay` is one value per job and the service interleaves the shots of
one job's circuits.

| Job | Approved dry run | record.json sha256 | Shots | Planner charge (s) | Ceiling (s) | Run | Job id | Billed (s) |
|---|---|---|---|---|---|---|---|---|
| prep0 @ 50 us | `2026-10-18T082231.656321Z` | `4a45c5e729ee1098581dcc3336f6724b895b034a76f8b224723d3e364e12e9b5` | 32768 | 4.01 | 6 | `2026-10-18T083402.386701Z` | `dba8huoc77vs7382f8mg` | 4 |
| prep0 @ 250 us | `2026-10-18T082231.415191Z` | `65c38ce5545bd9491baaa19af7e51611655a38507429b08e4e35cd8baf6ad112` | 16384 | 6.43 | 8 | `2026-10-18T083404.414317Z` | `dba8hr424mrc73851u8g` | 6 |
| x_history @ 50 us | `2026-10-18T082231.599609Z` | `140d8de1160010b1eb99142ac7e309bd6eb525396289fc20e91385b3a549c491` | 32768 | 4.01 | 6 | `2026-10-18T083404.226285Z` | `dba8hnk24mrc73851u30` | 4 |
| x_history @ 250 us | `2026-10-18T082231.223185Z` | `838ec9c296f0c19ceec80d54370ca3748d60fcf52ac7864b48a16e55b693c086` | 16384 | 6.43 | 8 | `2026-10-18T083403.945334Z` | `dba8hsk24mrc73851uag` | 6 |

Planner charge 20.88 s, billed 20 s, ceilings 28 s. All four jobs executed
between 08:52:48Z and 08:53:27Z under the 2026-10-18T01:38:20-07:00
calibration, which `--fetch-readout` retains per PUB in each run's
state-prep-readout.json.

## Preregistered stage-2 rule (`scripts/state_prep_excess.py`)

With alpha = 0.01:

- Bounds: one-sided Clopper-Pearson, three per controlled qubit over all
  149 (x_history upper at 50 and 250 us, prep0 lower at 250 us), so they
  hold simultaneously over every placement inside the controlled set. The
  first shot of each executor chunk counts at its worst value.
- Readout: e10 the smallest and e01 the largest of the n21 model's and
  every execution calibration's reported values; b = min(prep0 lower, e10).
- u = max(0, (U - b) / (1 - e01 - b)), the x_history arm's own excitation.
- eps = u / ((1 - u)(1 - delta)), delta = x error + (x + measure
  duration) / T1.
- eps50, eps250: the maxima over the placement S.

Fixed point: plan at `--prep-excitation 0`, bound eps on the placement,
re-plan at the larger value, and stop when the bound no longer exceeds the
eps planned with. Plans use `--shot-tiers 100000 --empirical-bernstein
--model-method exact --optimizer-candidates 1` on ibm_kingston, with
`--exclude-qubits` naming the uncontrolled qubits so S lies inside C.

1. 50 us feasible within C = 33 s: that plan's fresh digest is the stage-2
   case.
2. Otherwise 250 us at eps250 within C2 = 72 s.
3. Otherwise stop. A placement outside the controlled set stops, and an eps
   at or above 1 stops.

## Stage 2

| Step | Record | Placement | Planned eps | eps50 | eps250 | Verdict |
|---|---|---|---|---|---|---|
| plan at 0 | `2026-10-18T085503.864744Z` | 104, 105, 106, 117, 124, 125, 126 | 0 | 0.014392 | 0.015745 | replan |
| plan at eps50 | `2026-10-18T085924.738302Z` | same | 0.014393 | 0.014392 | 0.015745 | converged |

q125 sets both maxima. Rule step 1 applies: 50 us, planner charge 28.17 s
within C = 33 s. The approved stage-2 record `2026-10-18T085924.738302Z`
(sha256 `210f3ddab5753ee3f51d1a193f0bd40e80372cae15e5eb2ad679292157f95a64`)
ran as `2026-10-18T090603.530638Z`, job `dba8r7k24mrc738527d0`, one dynamic
job of two 100,000-shot PUBs, billed 28 s. The controls' execution
calibration and the stage-2 noise model share the 01:38:20-07:00
calibration (`calibration_scope.matched`).

## Budget

The window held 266 s before stage 1. Stage 1 billed 20 s and stage 2
28 s; 218 s remain (results/live/qpu-job-inventory.json).
