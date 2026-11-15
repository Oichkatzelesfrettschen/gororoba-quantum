# Run case: the quadric rings of the weight slice over Q(i) (test of A5-548)

[`weight_slice_quadric_rings.py`](weight_slice_quadric_rings.py) decides, over Q(i), whether each quadric ring
Q(i)[y]/K of the weight slice is Cohen-Macaulay and whether it is reduced. The ideals are the degree-2 relations of
`weight_slice_fiber_relations.py`, which ledger row A5-474 places inside the relation ideal; the fiber cone equals
Q(i)[y]/K for Iso and W8 (A5-475) and for E8-bar (A5-457). This file is written before the run.

## Claim under test

Ledger row A5-548: a quadric ring of the fiber track is Cohen-Macaulay exactly when K is radical. The row holds at
the primes 32009, 32029 and 32057 on the header slices (A5-560). No row states the Cohen-Macaulay property of any of
these rings over Q(i), and no row states either property for same-sign X over Q(i).

## Falsifier

A cell that the program decides reduced and not Cohen-Macaulay, or Cohen-Macaulay and not reduced. The calibration
ideal "two planes meeting in a point" has the first shape and "double plane" the second, so the program reports
either shape when it meets one. A cell left undecided, a calibration answer that departs, or a relation digest that
differs from `weight-slice-fiber-relations-result.json` fails the run without deciding the claim.

## Predictions, recorded before the run

| Cell | Dimension, degree | Artinian length | Cohen-Macaulay | Reduced | Source of the prediction |
|---|---|---|---|---|---|
| X- -> N-, X+ -> N+ | 4, 12 | 15 | no | no | modular rows A5-019, A5-303, A5-560 |
| Iso -> N-, Iso -> N+ | 5, 23 | 23 | yes | yes | K prime over Q(i) (A5-446); modular A5-010 |
| W8 -> N-, W8 -> N+ | 6, 50 | 50 | yes | yes | K radical over Q(i) (A5-447); modular A5-010 |
| E8-bar -> N-, E8-bar -> N+ | 5, 11 | 20 | no | no, five nilpotent linear forms | A5-451 over Q(i); modular A5-019 |

The reducedness of Iso, W8 and E8-bar over Q(i) is already proved by the rows named; the program computes it again
by its own certificates and a difference from those rows is a finding. The Cohen-Macaulay column and the X row are
predictions from the modular pattern.

## Host, order and budget

- Host: the Windows compute workstation under WSL (infrastructure chart, `hosts/README.md`), Singular 4.4.1 from
  its `a5env`. The build host takes no jobs.
- Load check: the 1-minute load average is read before each step and stored with the step's wall time. The
  workstation carries other Singular jobs, so the stored times are upper bounds and are not a benchmark.
- Small slice first: the four calibration ideals and X- -> N- (15 generators, 69 quadrics). Its measured times set
  the estimate for the larger cells, entered below before they start.
- Memory: each Singular call runs under the producer's 8 GiB address-space limit (`prlimit --as`); the cells run
  one at a time, so the plan is 8 GiB of the workstation's 52.5 GB budget.
- Time limit: 3600 s per Singular call (the producer's limit). The radical of the E8-bar ideal is the step most
  likely to reach it; a call that reaches it leaves that cell undecided, which the record reports.
- Each step's result is written under `--steps` before the next step starts, and a rerun reads finished steps back.

## Estimate from the small slice

Entered after the small slice and before the remaining cells.

- The calibration ideals take under 1 s each. Regenerating the X- -> N- relations takes 39 s at a 1-minute load
  of 63 on 32 threads; its digest equals the retained one.
- The first form of the Cohen-Macaulay step, with dense linear forms whose coefficients reach about 32000, ran past
  the 3600 s limit on X- -> N- (load 48 to 59). A stage-timed rerun puts the time in the Groebner basis of K plus
  those forms: std(K) itself takes under 1 s. The program now chooses sparse forms greedily, and the same rerun
  decides the cell in 4 s (std(K) < 1 s, four forms chosen from 1242 candidates in 2 s, the radical of K in 2 s).
- Estimate for the other seven cells: the relation regeneration scales with the generator count (17 to 24 against
  15), so minutes per cell; the radical of the E8-bar ideal (21 variables, 148 quadrics) is the one step without a
  measured analogue and keeps the 3600 s limit. Plan: all eight cells in one run, steps persisted, one watcher
  with a 3-hour deadline; a step that reaches the limit leaves its cell undecided in the record instead of
  stopping the run.
