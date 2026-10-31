# Belenos interleaved mode swap

`scripts/belenos_mode_swap_interleaved.py` builds three `qpu:belenos` jobs. They test the placement of a packed
box-kite block on the chip against drift in time and against the per-seed variance of the compiled mesh.

## Question

Registry claim `qd-belenos-packed-mode-swap` compares two series that hold the same packed sign blocks in different
4-mode slots: `box_kite_photonic_packed` and `box_kite_photonic_packed_swapped`, which moves every block three of six
slots. The single-click algebra-mode share a of 26 of 32 blocks changed by more than 4.5 two-sample standard errors.
The slot predictor of `scripts/qd_packed_mode_swap_analysis.py` reads r = -0.585 over the half blocks, a residual that
follows the chip modes with a reversed sign. The claim's boundary is the gap: the two series ran as separate jobs about
an hour apart and carried no compilation seed, so placement is not separated from drift or from the compiled mesh.

Visibility job-00 of `belenos_associator_visibility` (run `2026-10-31T050044Z`) sizes the third term. One identical
4-mode circuit under four compilation seeds returned four different `computed_circuit` meshes, and the two-click
endpoint D read -0.646, -0.873, -0.853 and -0.672: chi-square 241 on 3 degrees of freedom against binomial errors of
0.01 to 0.017. The same parameters and seed return the same mesh (teleportation job-02 replay,
[ascella-belenos-entanglement-teleportation.md](ascella-belenos-entanglement-teleportation.md#split-recovered-chip-rehearsal-job-02-and-job-03)).
A per-seed mesh error is therefore large against binomial error, and a packed-swapped contrast between two meshes
needs a measured mesh variance as its reference.

## Design

Each block set k (the six blocks of `box_kite_photonic_packed/job-0k`) runs as six template iterations. Both layouts put
the six photons on chip modes 0, 4, 8, 12, 16 and 20, so one template circuit serves every iteration: six independent
4-mode triangular meshes, one per slot, whose parameters reproduce the retained block-diagonal unitary of the packed or
swapped `circuit.json`. `--check` holds every iteration to that unitary within 1e-9.

- **Order within a set.** The six iterations alternate the layouts: packed, swapped, packed, swapped, packed, swapped
  for an even block set (0, 2, 4) and swapped, packed, swapped, packed, swapped, packed for an odd one (1, 3).
- **Primary seed.** Each layout runs its primary seed at the first and last of its three slots. The two repeats request
  one compiled mesh, so their difference is drift at a fixed mesh, four slots (about 60 s) apart.
- **Replicate seed.** Each layout runs a second compilation seed at the slot between its primary repeats. The replicate
  against the pooled primary repeats of the same layout is a same-layout, different-seed contrast, which measures the
  per-seed mesh variance directly.

**Order.** The replicate of each layout sits exactly at the mean time of that layout's primary pair (slot 2 between
slots 0 and 4 for packed, slot 3 between 1 and 5 for swapped in an even set), so a linear drift cancels in every
replicate contrast and cannot enter the mesh variance, where it would inflate the reference and move blocks into the
"within the mesh variance" rows. The cost is the layout contrast: packed and swapped mean times sit one slot apart
(about 15 s), the least that integer slots allow once each replicate sits at its pair mean, since six slots cannot make
the layout means and the seed means all coincide. The mirror order of an odd set flips the sign of that imbalance, so the
five sets net to one slot in total. An ABBA order would balance the layout means exactly but put each replicate 2.5 to
3.5 slots from its pair mean, so drift would raise the mesh variance and could turn drift into a "mesh error"
reading.

| Job | Block sets | Iterations | Samples | `max_shots` | Credit ceiling | Expected seconds |
|---|---|---|---|---|---|---|
| job-00 | 0, 1 | 12 | 72,000 | 216,000 | 1.018 | 190 |
| job-01 | 2, 3 | 12 | 72,000 | 216,000 | 1.018 | 190 |
| job-02 | 4 | 6 | 36,000 | 108,000 | 1.018 | 100 |

Each iteration takes 6,000 samples with a `max_shots` cap of 18,000 and `min_detected_photons` 1. Quandela bills a job
1 credit plus 1e-6 per shot of its largest iteration ([credit optimization](../runbooks/quandela-credit-optimization.md)),
so each job ceilings at 1 + 18,000 x 1e-6 = 1.018 and the case at 3.054 credits.

**Set 5.** Set 5 holds two photons, not six, and stays out; the case covers 30 of the 32 blocks. The template fills an
empty slot with the identity, so set 5 could run as a six-photon template with the identity on the four other slots.
That adds 6 iterations to job-02, restores 2 of the 16 half blocks to the slot predictor and costs no credit, but its
context then differs from the retained two-photon run, so its comparison with the earlier delta is the weakest of the
six sets, and the case would pool 32 blocks where the preregistration fixes 30. The case keeps the 30 blocks; set 5 is a
later case if the slot predictor's interval needs the two half blocks.

**Compilation seeds.** The primary seed of each set and layout is, in job, set and layout order (packed, swapped), an
index 0 to 9 value of the ANU QRNG draw [`draw-2026-10-31T043029Z.json`](../evidence/anu_qrng/draw-2026-10-31T043029Z.json).
The replicate seed of each set and layout is the same-index value of
[`draw-2026-10-31T051136Z.json`](../evidence/anu_qrng/draw-2026-10-31T051136Z.json), drawn for the replicate arm and used
once. [`allocations.json`](../evidence/qrng_seeds/allocations.json) registers indices 0 to 9 of both draws in order.

## Duration

`qpu:belenos` cuts a job at 300 s (`max_duration`). The bound comes from the retained runs, not from one fixed cost.

- **Per iteration.** At most 9.6 s: the largest of the 12 to 32 iteration single-photon jobs (115 s over 12 iterations in
  `bdsc_qualification` mm-none-e1; 107 to 136 s over 16 in `belenos_mesh`, 8.5 s at most; 165 to 176 s over 24 in
  `bdsc_stationarity` and `bdsc_drift_series`, 7.3 s at most).
- **Per sample.** At most 0.917 ms: the retained six-photon packed and swapped jobs took 52 to 55 s for 60,000 samples
  with shots used equal to samples, which charges the whole job, fixed cost included, to the samples.
- **Bound.** n x 9.6 s + S x 0.917 ms for n iterations of S samples. Twelve iterations of 6,000 samples bound at 115.2 +
  66.0 = 181 s (expected seconds 190), and six iterations at 57.6 + 33.0 = 91 s (expected seconds 100).
- **Stress.** The two-photon packed and swapped jobs took 19 s and 34 s for the same 20,000 samples, a 1.8x spread
  between jobs. Scaling the sample term by 1.8 gives 234 s for twelve iterations and 117 s for six, inside 0.8 of the
  limit, and `--check` requires that margin. Samples of 8,000 per iteration stress to 274 s and 10,000 to 313 s, which is
  why the case takes 6,000.
- **Cancelled run.** Teleportation job-01 was cancelled at 318 s over twelve iterations; the three-photon iterations of
  its siblings drew about 1,900 shots per sample (13.5 million shots for 7,200 samples in job-02), a regime the
  one-detection-per-sample six-photon runs do not reach.

The live plan of 2026-10-31 against the frozen bytes of each job (`qd_platform.py plan --platform qpu:belenos
--max-credits 1.018 --per-job-credits 1.0 --admit-status running`) estimates 72,000 shots for 72,000 samples in job-00
and job-01 and 36,000 for 36,000 in job-02, one detection event per sample, against `max_shots` of three times that. It
reports `credit_ceiling` 1.018 for each. It also prints the warning that `qpu:belenos` reports HOM 88.6 %, below the
90 % that strategy.md design rule 1 asks of a six-photon interfering block; the submit step reads the live HOM again.

**Power.** One-click samples per block run 7,985 to 17,898 (median 11,269) per 60,000-sample job in the retained series,
so 798 to 1,790 (median 1,127) per iteration here. A placement contrast of median cells has a binomial standard error of
0.013, so 4.5 binomial errors are 0.058, and 13 of the 32 earlier deltas exceed that. A repeat pair gives a z of about 2.4
for a drift of 0.05.

The decisive power is against the mesh variance. A Monte Carlo of the analysis below, run through the case's own
functions on binomial cells at the retained per-block one-click rates (2,000 replicates per model), puts λ as the
fraction of each earlier delta that is true placement, with the rest of the earlier variance taken as mesh error:

| λ | Half and extreme mesh sigma | Placement beyond the mesh variance | Comparison |
|---|---|---|---|
| 0.5 | 0.051, 0.025 | 0.3 % | reproduce 29 %, indeterminate 60 % |
| 0.7 | 0.042, 0.021 | 7.7 % | reproduce 78 % |
| 0.7 | 0.063, 0.031 (sigma x 1.5) | 1.0 % | reproduce 41 %, indeterminate 54 % |
| 0.85 | 0.031, 0.015 | 55 % | reproduce 97 % |

The per-block placement reading decides only when the earlier deltas were mostly placement, and the comparison with
the earlier deltas carries the case.

## Analysis (`--analyze RUN RUN RUN`)

The three runs pool into one block table over all 30 blocks. `--analyze` checks that each run's `cases.json` is
byte-identical to the frozen case, requires one run per job, and writes one `analysis.json` to each run directory.
Every statistic below is withheld unless all 30 blocks are complete, meaning all six iterations of their set returned
counts.

- **Binding.** A result iteration binds by its echoed circuit parameters and compilation seed. The two primary repeats
  of a layout share both, so they bind in returned order. An iteration without counts holds the slot its echo names, so
  a later counted repeat keeps its label, and it counts as uncounted.
- **Observable.** Per block and iteration, a is the share of samples with exactly one click in the block's slot that
  land on an algebra mode, as in `qd_packed_mode_swap_analysis.py`.
- **Within-job validity.** For each block and layout, z is the two-sample z between the two primary repeats. Pairs whose
  returned `computed_circuit` digests agree enter D = sum z^2 per job, tested against chi-square with that many degrees
  of freedom; drift is detected at p < 0.01. D checks that the within-job contrast is internally valid. The repeats sit
  about 60 s apart and the earlier confound was an hour, so D carries no statement about the earlier claim. The inflation
  kappa^2 = max(1, D / dof) of a job scales every binomial variance of that job's blocks, which covers extra dispersion
  between iterations. A job with no mesh-identical pair (dof 0) withholds the placement reading, and so does a replicate
  digest that equals its primary digest or is missing.
- **Mesh identity.** A layout whose two primary repeats returned different or missing `computed_circuit` digests
  averages two meshes in its pooled primary cell, so its contrast leaves the mesh variance, its block leaves the
  placement test, and the block stays in the comparison with the earlier deltas. `analysis.json` lists the dropped
  block-layouts.
- **Mesh variance per class.** A single-photon share a = cos^2 theta moves by 2 sqrt(a (1 - a)) d theta under a mesh
  rotation error d theta, so a half block (p_algebra 1/2, 14 blocks) carries about three times the mesh error of an
  extreme block (p_algebra 0 or 1, 16 blocks); the retained deltas bound sigma at 0.059 and 0.029. For each block and
  layout, R = a(replicate) - a(primary, repeats pooled) has variance 2 sigma_c^2 plus the inflated binomial variances,
  c the block's class. sigma_c^2 is the mean of (R^2 - inflated binomial variance) / 2 over the class's contrasts (28
  half, 32 extreme), truncated at 0; a class with fewer than 10 contrasts withholds the reading. Its one-sided 95
  percent upper bound is (sum R^2 / chi2.ppf(0.05, m) - mean variance) / 2 over the class's m contrasts. The excess
  ratio, sum R^2 over the sum of the inflated binomial variances, is reported per class.
- **Slot homogeneity.** For each physical slot, S = sum R^2 / (2 sigma_c^2 + variance) over the ten contrasts the
  slot holds is chi-square on that count under one mesh scale per class. A slot with p below 0.01 / 6 withholds the
  "beyond" class, because one slot with a larger mesh scale would otherwise inflate both class scales and test the
  other slots' blocks against the wrong scale.
- **Placement against the mesh variance.** For each block, delta = (a(swapped, primary) + a(swapped, replicate)) / 2 -
  (a(packed, primary) + a(packed, replicate)) / 2. With no placement effect it has variance sigma_c^2 plus a quarter of
  the inflated binomial variances of its four cells, and z = delta / sqrt(sigma_c^2 + binomial variance). A block moved
  beyond the mesh variance when |z| > 4.5, and the placement lies beyond the mesh variance when at least 2 blocks do
  and the slot homogeneity holds. The same Monte Carlo with no placement effect returns "beyond" in 0 of 2,000
  replicates under each of: one sigma of 0.03 for both classes; class sigmas 0.05 and 0.01 with Gaussian, Student t3,
  and Student t3 times a log-normal (0.5) scale per compiled mesh. One slot at three times the mesh scale returns it in
  3 of 2,000 (0.15 percent); the slot check withholds "beyond" in 68 percent of all replicates of that model. Blocks moved against
  binomial error alone are the `moved` blocks of `decide()` on the pooled table, the earlier criterion.
- **Slot predictor, descriptive.** `decide()` of `qd_packed_mode_swap_analysis.py` runs once on the pooled packed and
  swapped table of all 30 blocks, each share taken over every iteration of its layout, and `analysis.json` reports its
  verdict, block predictor and slot predictor with Fisher 95 percent intervals. It carries no reading. Each block's
  predictor is the packed mean of the other half blocks on its swapped slot; those come from other compiled meshes,
  but in 10 of the 14 half blocks they include the block's own swap partner of the same set, and in 6 the predictor
  rests on one block, so a pattern of offsets that follows the blocks can read as a chip-mode sign. Fourteen half
  blocks give a Fisher half-width of 0.59 in z, and the reversed-sign reading the retained data suggest (r -0.73,
  interval -0.91 to -0.32 on the 30 blocks) would clear a -0.3 bound at most 7 percent of the time even at λ 0.85.
- **Comparison with the earlier deltas.** For each block, delta_new = a(swapped) - a(packed) of the pooled table is
  compared with delta_old of the retained `qpu_belenos` series (`qd_packed_mode_swap_analysis.collect`). The case
  reports the number of blocks whose signs agree with the one-sided exact binomial p against one half, and Pearson r with
  its Fisher interval. The comparison reads **reproduce** when r has a lower bound above 0.3 and the sign p is below
  0.01, **uncorrelated** when r has a lower bound at or below 0.3 and an upper bound below 0.7, and **indeterminate**
  otherwise. The new and the earlier deltas also differ in mesh, since the retained jobs carried no compilation seed.
- **Earlier excess.** Each earlier delta is a contrast between two independent meshes of the earlier window, so with
  no placement and no drift it has variance 2 sigma_c^2 plus its binomial variance. X(w) = sum over the 30 blocks of
  delta_old^2 / (2 w sigma_c^2 upper bound + binomial variance) is tested against the 0.99 quantile q of chi-square on
  30 degrees of freedom. An uncorrelated comparison reads **mesh** when X(1) <= q, **excess** when X(3) > q, and
  **window** otherwise. The allowance w = 3 is the change of mesh variance between acquisition windows that the two
  visibility jobs of 2026-10-31 show (control spread 1.7 times in standard deviation). In the Monte Carlo, earlier
  deltas made entirely of mesh error at the old-delta bound (sigma 0.059 and 0.029) read mesh in 99.9 percent of the
  uncorrelated outcomes; a mesh error of half that size (0.03 and 0.015) reads window in 98 percent of them; and a mesh
  error of 0.01 and 0.003, which leaves the earlier deltas to drift, reads excess in all of them, while 93 percent of
  all replicates of that model read "no moves", because no block then moves against binomial error alone.

### Reading

The reading table combines the placement class (no block moved against binomial error; moves beyond the mesh variance;
moves within it) with the comparison class.

| Placement | Comparison | Reading |
|---|---|---|
| no block moved | any | no moves: the earlier separation fails |
| beyond the mesh variance | reproduce | moves beyond the mesh variance reproduce the earlier deltas: not hour-scale drift |
| beyond the mesh variance | indeterminate | moves beyond the mesh variance with the earlier deltas neither reproduced nor excluded: inconclusive |
| beyond the mesh variance | uncorrelated, mesh | moves beyond the mesh variance do not follow the earlier deltas, which stay within the per-seed mesh variance: the earlier deltas read as mesh error |
| beyond the mesh variance | uncorrelated, window | moves beyond the mesh variance do not follow the earlier deltas, which exceed the per-seed mesh variance only within a threefold window change: the source of the earlier deltas is unresolved |
| beyond the mesh variance | uncorrelated, excess | moves beyond the mesh variance do not follow the earlier deltas, which exceed the per-seed mesh variance even at a threefold window change: the earlier deltas read as hour-scale drift or unseeded compilation |
| not shown beyond | reproduce | moves not shown beyond the mesh variance reproduce the earlier deltas: not hour-scale drift, placement per block unresolved |
| not shown beyond | indeterminate | moves not shown beyond the mesh variance with the earlier deltas neither reproduced nor excluded: inconclusive |
| not shown beyond | uncorrelated, mesh | moves not shown beyond the mesh variance do not follow the earlier deltas, which stay within the per-seed mesh variance: the earlier deltas read as mesh error |
| not shown beyond | uncorrelated, window | moves not shown beyond the mesh variance do not follow the earlier deltas, which exceed the per-seed mesh variance only within a threefold window change: the source of the earlier deltas is unresolved |
| not shown beyond | uncorrelated, excess | moves not shown beyond the mesh variance do not follow the earlier deltas, which exceed the per-seed mesh variance even at a threefold window change: the earlier deltas read as hour-scale drift or unseeded compilation |

"Not shown beyond" covers fewer than two blocks beyond the mesh variance and a failed slot homogeneity.

The preregistered interpretation in each `cases.json` repeats this paragraph:

The design shows whether moving a packed block changes its algebra-mode share by more than that share varies between
compiled meshes of one layout, and whether the per-block changes reproduce the changes of the earlier separate jobs.
Reproduction rules out hour-scale drift as their source. When the changes do not follow the earlier deltas, the size
of the earlier deltas against the measured per-seed mesh variance reads them as mesh error, as hour-scale drift or
unseeded compilation, or as unresolved within a threefold change of the mesh variance between acquisition windows. The
slot predictor is descriptive. The design does not show how a chip mode changes a share.

## Written case

- *What it measures.* Whether the packed series' block residual follows placement beyond the per-seed mesh variance, and
  whether it reproduces the earlier deltas, with mesh-identical primary repeats as the within-job validity reference and
  a replicate seed per layout as the mesh reference; the per-class per-seed mesh variance of a single-photon share on
  `qpu:belenos`, which later multi-seed designs on this chip need; and whether the earlier deltas exceed it.
- *Why a simulation cannot answer it.* The residual is the chip's compiled-mesh and detection error at each slot; an
  ideal or noise-model simulation gives every block its exact share at every slot and every seed.
- *Backend and budget.* `qpu:belenos`, three jobs submitted one after the other, 12, 12 and 6 iterations of 6,000
  samples, `max_shots` 18,000 per iteration and `min_detected_photons` 1. The credit ceiling is 1.018 per job and 3.054
  for the case. Expected seconds are 190, 190 and 100 against the 300 s limit.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` and `submit` with `--platform qpu:belenos
  --max-credits 1.018 --expected-seconds 190 --per-job-credits 1.0 --admit-status running` (expected seconds 100 for
  job-02), `collect`, and after all three `scripts/belenos_mode_swap_interleaved.py --analyze RUN_00 RUN_01 RUN_02`.
  Each run records the platform's HOM, g2 and transmittance at its plan.
- *Stopping rule.* Job-00 is checked before job-01 is planned: a job with no mesh-identical primary pair, or whose
  replicates returned their primaries' meshes, withholds the pooled reading by rule, so the case stops there. A job
  that errors or is cut short is resubmitted only on the owner's further approval.
