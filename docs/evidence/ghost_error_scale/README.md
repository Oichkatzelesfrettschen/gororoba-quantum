# Ghost error scale and the idle budget

`scripts/ghost_error_scale.py` fits, per audited run, one factor c on every
reported CZ error and one factor r on every readout flip, the pair that
brings the Aer replay closest to the hardware in mean TV distance. The fit
has two knobs, so every error the replay omits lands in c or r.
`scripts/ghost_idle_budget.py` measures one omitted error directly: the
replay simulates the unscheduled ISA circuit, so a qubit that waits while
other qubits run gates, a mid-circuit measurement or a feed-forward
broadcast stays ideal, while on hardware it relaxes. The retained
`scheduler_timing` table of every executed PUB gives that idle time per
qubit; charged at the snapshot's T1 and T2, it gives the idle error E_idle,
and `c_idle = 1 + E_idle / E_cz` is the CZ factor a fit would need if idle
relaxation were the only omission ([idle_budget.json](idle_budget.json),
gate core-343; the script's docstring states the charge and why it is an
upper estimate).

## Fitted factor against the idle budget

The fitted c and its bootstrap quantiles come from sweep parts b and c
(Kaggle CPU kernels, 2000 bootstrap draws over PUBs); broadcasts and
resets are counts over the run's replayed PUBs.

| Run | Backend | PUBs | Broadcasts | Resets | c_idle | Fitted c (16/50/84) | Fitted r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-13T025444 | fez | 146 | 0 | 0 | 1.46 | 2.0 / 2.0 / 2.0 | 1.0 |
| 2026-10-13T032011 | fez | 36 | 0 | 0 | 1.32 | 1.5 / 1.5 / 1.5 | 1.0 |
| 2026-10-15T030903 | kingston | 36 | 0 | 0 | 1.34 | 2.0 / 2.0 / 3.0 | 2.0 |
| 2026-10-15T031229 | kingston | 146 | 0 | 0 | 1.55 | 2.0 / 2.0 / 3.0 | 1.0 |
| 2026-10-15T070853 | kingston | 14 | 0 | 0 | 1.59 | 3.0 / 4.0 / 4.0 | 0.5 |
| 2026-10-15T030748 | kingston | 15 | 0 | 5 | 1.68 | 3.0 / 3.0 / 4.0 | 3.0 |
| 2026-10-13T201757 | fez | 46 | 3 | 22 | 1.69 | 1.0 / 2.0 / 3.0 | 1.5 |
| 2026-10-13T020454 | kingston | 4 | 4 | 4 | 2.32 | 5.0 / 5.0 / 5.0 | 0.5 |
| 2026-10-13T022433 | kingston | 4 | 4 | 4 | 2.32 | 5.0 / 6.0 / 6.0 | 0.5 |
| 2026-10-13T080216 | fez | 2 | 1 | 2 | 1.84 | 5.0 / 5.0 / 6.0 | 1.0 |
| 2026-10-13T083417 | fez | 8 | 4 | 8 | 1.79 | 5.0 / 6.0 / 6.0 | 3.0 |

Run 2026-10-15T070847 carries no CZ, so its c is unidentified; its idle
budget is 2.8e-4, since its waits are explicit delays the replay already
relaxes.

Readings:

- In the five runs with no broadcast and no reset, idle relaxation accounts
  for 34 to 64 percent of the excess c - 1 in four (c_idle 1.3 to 1.6
  against fitted 1.5 to 2) and 20 percent in 070853 (fitted 4).
- 030748 carries resets and no broadcast and fits 3 against 1.68, between
  the static and the dynamic group.
- The four runs that execute a feed-forward broadcast and a reset in every
  PUB or every other PUB fit c = 5 to 6 while idle relaxation supplies 1.8
  to 2.3. The factor exaggerates the difference: these circuits carry 43 to
  70 CZ, so a fixed error per circuit moves c further than it does on the
  static runs' 125 to 313 CZ. In absolute terms the unexplained error per
  PUB, (c - c_idle) E_cz / PUBs, is 0.23 to 0.42 on these four and 0.06 to
  0.43 on the four ordinary static runs, so the sweep does not localize the
  excess in the dynamic-circuit events. 201757 carries resets in half its
  PUBs and broadcasts in 3 of 46 and leaves almost none (0.004 per PUB).
  An explicit per-event error axis, rather than a CZ factor, is the
  measurement that separates them.
- 020454 and 022433 execute the same design twice (identical PUBs, CZ and
  idle budget), a test-retest pair: c = 5 and 6.
- The bootstrap resamples PUBs: 2 for 080216, 4 for 020454 and 022433, 8
  for 083417, so their quantiles bound little.
- 2026-10-15T070853, the widest static run (313 CZ per circuit over 37
  active qubits), fits 4 against an idle budget of 1.59. Its excess is
  outside both idle relaxation and the dynamic-circuit events; parallel CZ
  layers of that width are where spectator crosstalk would act, and no
  retained measurement isolates it.

## Retained parts

`part_a.json`, `part_b.json` and `part_c.json` hold, unchanged, the
simulation fields of the three sweep kernels that ran commit 2298108
(`results/kaggle/2026-10-16T160703Z-gororoba-ghost-error-scale-a`, `-b` at
160706Z and `-c` at 160710Z). Their calibration-derived fields -- each
run's per-snapshot diagnostics, which count every coupler once, and the
`scaled` block with its separate `cz_cap` and `readout_cap` -- are
regenerated on the build host by `ghost_error_scale.py
--regenerate-diagnostics` from the archived calibration and circuits.
Gates core-349 and core-390 are the provenance gates: `--provenance`
requires each part to be, byte for byte, the regeneration of its kernel's
output. core-390 regenerates part c, the slowest of the three regenerations,
in the `full` tier; core-349 runs the other clauses on pull requests, among
them a plain `cmp` that
requires `part_c.json` to equal the output of a second part c kernel, which
ran commit dfb4384 with the per-coupler diagnostics
(`results/kaggle/2026-10-17T004620Z-gororoba-ghost-error-scale-c`). That
kernel resampled every grid point and wrote the same simulation bytes, so
the identity shows that local regeneration reproduces a kernel's output.
core-349 also binds `part_b.json` run by run to five shard kernels that ran
commit 215b81d on Kaggle CPU sessions, one run each
(`results/kaggle/2026-10-17T024808Z-gororoba-ghost-error-scale-b1` through
`-b5` at 025050Z): `--provenance` with several kernel outputs requires equal
headers, concatenates their runs in argument order and requires the
regeneration of the merged part to equal `part_b.json` byte for byte. Both
kernel sets sample under the fixed seed 20261016, so the identity shows that
part b reproduces across sessions and commits; it is one deterministic
computation run twice, not two independent samples. Gate core-389
(`--self-test`) drives the merge on synthetic shards and requires swapped or
missing shards, a differing header and a reserialized part to fail.
The `bundle` digests in each run's `submission.json` record the files each
kernel carried. Gate core-339 is the recomputation gate: it runs
`ghost_error_scale.py --check` on the three parts, which rebuilds every
audited run's members, shots, snapshots and diagnostics from the archived
inputs and reruns 2026-10-13T080216 on the CPU.
`scripts/ghost_event_scale.py` reads each dynamic run's fitted readout
factor from these parts.

## Prediction for sweep part a

Recorded before part a's kernel finished. Part a holds two Kingston runs:

| Run | PUBs | Broadcasts | Resets | c_idle |
| --- | --- | --- | --- | --- |
| 2026-10-11T152922 | 6 | 7 | 29 | 2.00 |
| 2026-10-12T055624 | 16 | 4 | 12 | 1.91 |

Three readings make distinct predictions on the sweep grid
(c = 1.5, 2, 3, 4, 5, ...):

| Reading | 152922 | 055624 |
| --- | --- | --- |
| idle relaxation only | c near 2 | c near 2 |
| excess proportional to CZ error, as in the four dynamic runs | c >= 4 | c between 2 and 5 |
| fixed error per broadcast, 0.23 to 0.31 per PUB at one broadcast per PUB (020454, 022433) | c = 2.8 to 3.1, grid point 3 | c = 2.5 to 2.8, grid point 3 |

The second reading was recorded first; the per-PUB comparison above,
recorded before part a's kernel finished as well, added the first and the
third.

## Part a against the prediction

| Run | Fitted c (16/50/84) | Fitted r | Best mean TV | Resample floor | Unexplained error per PUB |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11T152922 | 5.0 / 5.0 / 5.0 | 1.0 | 0.0334 | 0.0094 | 0.99 |
| 2026-10-12T055624 | 4.0 / 4.0 / 4.0 | 0.5 | 0.0467 | 0.0066 | 0.19 |

- The idle-only reading (c near 2) and the per-broadcast reading (grid point
  3 on both) fail; the CZ-proportional reading (c >= 4 on 152922, 2 to 5 on
  055624) holds on both runs.
- Neither fit reaches its resample floor: the best distances are 3.6 and 7.1
  times the floor, where 020454 comes within 1.8 times. One CZ factor and one
  readout factor leave structure in these two runs unexplained.
- On 152922, 220 CZ per circuit carry the factor to 0.99 of unexplained
  error per PUB, more than twice the 0.43 of any other run; 055624's 0.19 sits inside the
  0.06 to 0.43 of the static and the other dynamic runs.
- The bootstrap resamples 6 and 16 PUBs, so its tight quantiles bound PUB
  selection, not the model's shot noise.

`scripts/ghost_event_scale.py` separates scheduled idle, a per-event error
and the CZ factor on these runs and the other dynamic runs.

