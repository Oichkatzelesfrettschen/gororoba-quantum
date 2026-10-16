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
gate core-331; the script's docstring states the charge and why it is an
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
  PUB or nearly every PUB fit c = 5 to 6, with the 16th bootstrap
  percentile at 5, while idle relaxation supplies 1.8 to 2.3. Their excess
  is localized in the dynamic-circuit events, which the replay models as a
  readout flip on the measured bit and a perfect conditional operation.
  Run 201757 carries those events in 3 of 46 PUBs and fits 2.
- 2026-10-15T070853, the widest static run (313 CZ per circuit over 37
  active qubits), fits 4 against an idle budget of 1.59. Its excess is
  outside both idle relaxation and the dynamic-circuit events; parallel CZ
  layers of that width are where spectator crosstalk would act, and no
  retained measurement isolates it.

## Prediction for sweep part a

Recorded before part a's kernel finished. Part a holds two Kingston runs:

| Run | PUBs | Broadcasts | Resets | c_idle |
| --- | --- | --- | --- | --- |
| 2026-10-11T152922 | 6 | 7 | 29 | 2.00 |
| 2026-10-12T055624 | 16 | 4 | 12 | 1.91 |

If the excess is localized in the dynamic-circuit events, 152922, which
carries a broadcast in every PUB and five resets per PUB, fits c >= 4 with
its 16th bootstrap percentile >= 3, and 055624, which carries broadcasts in
a quarter of its PUBs, fits c between 2 and 5. A fit of c <= 2.5 on 152922
refutes the localization; a fit near c_idle on both runs means idle
relaxation explains the dynamic runs after all and the four runs above are
the anomaly.
