# Belenos interleaved mode swap

`scripts/belenos_mode_swap_interleaved.py` builds nine `qpu:belenos` jobs, one of which has run. They test the placement of a packed
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

Each block set k (the six blocks of `box_kite_photonic_packed/job-0k`) runs as template iterations that alternate the
layouts. Both layouts put the six photons on chip modes 0, 4, 8, 12, 16 and 20, so one template circuit serves every
iteration: six independent 4-mode triangular meshes, one per slot, whose parameters reproduce the retained
block-diagonal unitary of the packed or swapped `circuit.json`. `--check` holds every iteration to that unitary within
1e-9.

- **Order within a set.** The iterations alternate the layouts, packed first for an even block set (0, 2, 4) and
  swapped first for an odd one (1, 3).
- **Primary seed.** Each layout runs its primary seed at its first and last slot. The two repeats request one compiled
  mesh, so their difference is drift at a fixed mesh.
- **Replicate seeds.** Each layout runs other compilation seeds between its primary repeats: one for set 0 (`SEQUENCE`,
  six iterations) and three for sets 1 to 4 (`SEQUENCE_PACKED`, ten iterations). The pooled primary repeats and the
  replicates are m = 2 or m = 4 meshes of one layout, whose spread measures the per-seed mesh variance directly.

**Order.** In slot order the replicates of each layout sit, on average, at the mean slot of its primary pair: slot 2
between slots 0 and 4 in a six-iteration set, slots 2, 4 and 6 between 0 and 8 in a ten-iteration set (packed in an
even set; swapped one slot later). The packed and swapped mean slots sit one slot apart, and the mirror order of an odd
set flips the sign of that imbalance. An ABBA order would balance the layout means exactly but put the replicates off
their pair mean. In a ten-iteration set the replicates sit at the pair mean only on average (slots 2, 4 and 6 between
0 and 8), so a linear drift, and a step between a set's two jobs, add to the spread of a layout's meshes and raise the
measured mesh variance.

**Jobs.** A 24-mode iteration takes up to 50 s on `qpu:belenos` (see Duration), and a job costs 1.018 credits whatever it
holds, so each job carries as many iterations as fit with one iteration of margin under the 300 s cut: five. Job-00 ran
sets 0 and 1 in `SEQUENCE` and returned set 0 before the cut. Sets 1 to 4 run `SEQUENCE_PACKED` as two jobs each, its
first five and last five iterations, submitted one after the other; the two added replicate seeds per layout fill the
time a three-iteration half set would leave empty. A primary pair straddles the gap between its set's two jobs; the
within-set validity statistic measures the drift between the repeats directly, and its kappa^2 scales the binomial
variances.

| Job | Block set and part | Iterations | Samples | `max_shots` | Credit ceiling | Expected seconds |
|---|---|---|---|---|---|---|
| job-00 (ran) | sets 0 and 1 in `SEQUENCE`; cut after set 0 | 12 | 72,000 | 216,000 | 1.018 | 190 |
| job-03, job-04 | set 1, first and last five | 5 each | 150,000 | 450,000 | 1.09 | 260 |
| job-05, job-06 | set 2, first and last five | 5 each | 150,000 | 450,000 | 1.09 | 260 |
| job-07, job-08 | set 3, first and last five | 5 each | 150,000 | 450,000 | 1.09 | 260 |
| job-09, job-10 | set 4, first and last five | 5 each | 150,000 | 450,000 | 1.09 | 260 |

Each packed iteration takes 30,000 samples with a `max_shots` cap of 90,000 and `min_detected_photons` 1 (job-00 took
6,000 and 18,000). Quandela bills a job
1 credit plus 1e-6 per shot of its largest iteration ([credit optimization](../runbooks/quandela-credit-optimization.md)),
so job-00 billed 1 + 18,000 x 1e-6 = 1.018 and each packed job ceilings at 1 + 90,000 x 1e-6 = 1.09, 8.72 credits for
the eight. Samples cost almost no time (see Duration), so the fivefold samples cut each block's binomial error by
sqrt(5) at 0.072 credits per job. Job-00's frozen `cases.json` keeps its bytes (`RETAINED_CASES` binds its sha256), and its settings equal the
rebuilt settings of sets 0 and 1; the never-run job-01 and job-02 cases are replaced by job-03 to job-10. Job-00's frozen
preregistration names per-job kappa^2 and the R^2 formulas of a single replicate; with set 1 empty, its per-job kappa^2
is set 0's per-set kappa^2 and the m = 2 formulas reduce to those, so set 0 differs from its frozen text only in pooling
its sigma_c^2 with the m = 4 groups of sets 1 to 4, using the plain binomial variances in that pool, and in reading
nine runs.

**Set 5.** Set 5 holds two photons, not six, and stays out; the case covers 30 of the 32 blocks. The template fills an
empty slot with the identity, so set 5 could run as a six-photon template with the identity on the four other slots.
That adds 6 iterations, restores 2 of the 16 half blocks to the slot predictor and costs no credit, but its
context then differs from the retained two-photon run, so its comparison with the earlier delta is the weakest of the
six sets, and the case would pool 32 blocks where the preregistration fixes 30. The case keeps the 30 blocks; set 5 is a
later case if the slot predictor's interval needs the two half blocks.

**Compilation seeds.** The primary seed of set k and layout l (packed 0, swapped 1) is index 2k + l of the ANU QRNG
draw [`draw-2026-10-31T043029Z.json`](../evidence/anu_qrng/draw-2026-10-31T043029Z.json).
The first replicate seed of each set and layout is the same-index value of
[`draw-2026-10-31T051136Z.json`](../evidence/anu_qrng/draw-2026-10-31T051136Z.json). Replicate r (1 or 2) of set k (1 to
4) and layout l is index 4(k - 1) + 2l + r - 1 of
[`draw-2026-10-31T092245Z.json`](../evidence/anu_qrng/draw-2026-10-31T092245Z.json), drawn for the added replicates.
Each value is used once, and [`allocations.json`](../evidence/qrng_seeds/allocations.json) registers indices 0 to 9 of
the first two draws and 0 to 15 of the third in order.

## Duration

`qpu:belenos` cuts a job at 300 s (`max_duration`). Job-00 (`dc348230`) ran 12 iterations of 6,000 samples and was cut
at 300 s during its seventh iteration, with the six iterations of set 0 returned. Each returned iteration reports
`nb_shots_used` 6,000 and a global efficiency of 0.0034 to 0.0106, so at the 4.94 MHz clock its samples take under a
second; the iteration time is the reconfiguration of the 24-mode chip. Job-00 reports progress 0.5097 of 12 iterations
at the cut, 6.12 iterations in 300 s, so about 49 s per iteration, and at most 50 s since six completed. The retained
six-photon packed and swapped jobs each ran one iteration in 52 to 55 s, which the earlier bound of this case charged
to their samples. The 300 s clock runs from `start_time`: across the retained `qpu:belenos` runs `duration` counts from
`start_time`, so queue time and calibration windows before the start do not count, and a cut job reports the cut plus
its teardown (318 s and 339 s).

- **Bound.** One iteration of 6,000 samples takes at most 50 s; each further sample adds 1 / (4.94 MHz x 0.0034), the
  lowest global efficiency job-00 returned, so a 30,000-sample iteration takes at most 51.4 s and five take 257 s
  (expected seconds 260). `--check` requires the bound to stay within 0.9 x 300 s.
- **Cut.** A cut stops a job in its last iteration. The last iteration of a set's second job is a primary repeat, which
  every block of the set needs, so a cut withholds the pooled reading until that job reruns in full (1.09 credits, on
  the owner's further approval). A cut needs a slowdown of about 17 percent over job-00; a repeat of the teleportation
  job-02 ran within 1 percent of the original, and the ten single-iteration six-photon jobs within 52 to 55 s.

The live plan of each packed job (`qd_platform.py plan --platform qpu:belenos --max-credits 1.018 --expected-seconds
260 --per-job-credits 1.0 --admit-status running`) runs against its frozen bytes before its submit. It prints the
warning that `qpu:belenos` reports HOM below the 90 % that strategy.md design rule 1 asks of a six-photon interfering
block; the template is block-diagonal with one photon per 4-mode slot, so no two photons interfere and the warning does
not bind this case.

**Power.** One-click samples per block run 7,985 to 17,898 (median 11,269) per 60,000-sample job in the retained series,
so 798 to 1,790 (median 1,127) per iteration here. A placement contrast of median cells has a binomial standard error of
0.013, so 4.5 binomial errors are 0.058, and 13 of the 32 earlier deltas exceed that. A repeat pair gives a z of about 2.4
for a drift of 0.05.

The decisive power is against the mesh variance. A Monte Carlo of the analysis below, run through the case's own
functions on binomial cells at the retained per-block one-click rates (2,000 replicates per model), puts λ as the
fraction of each earlier delta that is true placement, with the rest of the earlier variance taken as mesh error:

| λ | Half and extreme mesh sigma | Placement beyond the mesh variance | Comparison |
|---|---|---|---|
| 0.5 | 0.051, 0.025 | 2.0 % | reproduce 55 %, indeterminate 43 % |
| 0.7 | 0.042, 0.021 | 35 % | reproduce 92 % |
| 0.7 | 0.063, 0.031 (sigma x 1.5) | 4.3 % | reproduce 65 %, indeterminate 34 % |
| 0.85 | 0.031, 0.015 | 98 % | reproduce 99.7 % |

The per-block placement reading decides when the earlier deltas were mostly placement (λ 0.85), and the comparison
with the earlier deltas carries the case below that. The model runs set 0 with one replicate and sets 1 to 4 with three,
as the jobs do, at 6,000 samples per iteration for set 0 and 30,000 for sets 1 to 4.

**Set 0 preview.** Job-00's set 0 gives a mesh sigma of about 0.057 for half blocks (8 contrasts) and 0.047 for extreme
blocks (4), with heavy tails: the two largest contrasts, 11 and 12 binomial standard errors (a p_algebra 0 block from
0.05 to 0.18 and a half block from 0.54 to 0.73), both sit on slot 5. A mesh sigma near the old-delta bound (0.059 and
0.029) points to the rows that read the earlier deltas as mesh error, and outliers confined to one slot would fire the
slot check; the power table assumes Gaussian mesh error, which these data do not fit.

## Analysis (`--analyze RUN x 9`)

The nine runs pool into one block table over all 30 blocks. `--analyze` checks that each run's `cases.json` is
byte-identical to the frozen case, requires one run per job, and writes one `analysis.json` to each run directory.
Every statistic below is withheld unless all 30 blocks are complete, meaning each of the iterations of their set
returned counts in exactly one run; an iteration counted in two runs raises.

- **Binding.** A result iteration binds by its echoed circuit parameters and compilation seed. The two primary repeats
  of a layout share both, so they bind in returned order. An iteration without counts holds the slot its echo names, so
  a later counted repeat keeps its label, and it counts as uncounted.
- **Observable.** Per block and iteration, a is the share of samples with exactly one click in the block's slot that
  land on an algebra mode, as in `qd_packed_mode_swap_analysis.py`.
- **Within-set validity.** For each block and layout, z is the two-sample z between the two primary repeats. Pairs whose
  returned `computed_circuit` digests agree enter D = sum z^2 per block set, tested against chi-square with that many
  degrees of freedom; drift is detected at p < 0.01. D checks that the within-set contrast is internally valid. The
  repeats sit minutes apart and the earlier confound was an hour, so D carries no statement about the earlier claim. The
  inflation kappa^2 = max(1, D / dof) of a set scales the binomial variances of that set's blocks in the placement test,
  which covers extra dispersion between iterations and drift across the gap between a set's two jobs. The mesh
  variance uses the plain binomial variances: subtracting a drift-inflated binomial term from the mesh spread would
  drive sigma_c^2 toward 0 and read the earlier deltas as drift. A set with no mesh-identical pair
  (dof 0) withholds the placement reading, and so does a replicate digest that equals its primary digest or is missing.
- **Mesh identity.** A layout whose two primary repeats returned different or missing `computed_circuit` digests
  averages two meshes in its pooled primary cell, so its group leaves the mesh variance, its block leaves the placement
  test, and the block stays in the comparison with the earlier deltas. `analysis.json` lists the dropped block-layouts.
  The reading is withheld unless every replicate digest differs from its primary digest and from the other replicate
  digests of its layout.
- **Mesh variance per class.** A single-photon share a = cos^2 theta moves by 2 sqrt(a (1 - a)) d theta under a mesh
  rotation error d theta, so a half block (p_algebra 1/2, 14 blocks) carries about three times the mesh error of an
  extreme block (p_algebra 0 or 1, 16 blocks); the retained deltas bound sigma at 0.059 and 0.029. For each block and
  layout, the m meshes (the pooled primary repeats and each replicate) have shares a_i whose sample variance s^2, on
  m - 1 degrees of freedom, has expectation sigma_c^2 plus the mean binomial variance, c the block's class.
  sigma_c^2 = sum (m - 1)(s^2 - mean variance) / sum (m - 1) over the class's groups, truncated at 0; with all sets
  complete the half class holds 68 degrees of freedom and the extreme class 88, and a class with fewer than 10
  withholds the reading. Its one-sided 95 percent upper bound is sum (m - 1) s^2 / chi2.ppf(0.05, dof) - sum (m - 1)
  mean variance / dof. The excess ratio, sum (m - 1) s^2 over sum (m - 1) mean variance, is reported per class.
- **Slot homogeneity.** For each physical slot, S = sum (m - 1) s^2 / (sigma_c^2 + mean variance) over the groups the
  slot holds is chi-square on their summed degrees of freedom under one mesh scale per class. A slot with p below
  0.01 / 6 withholds the "beyond" class, because one slot with a larger mesh scale would otherwise inflate both class
  scales and test the other slots' blocks against the wrong scale.
- **Placement against the mesh variance.** For each block, delta = (mean over the swapped meshes of a) - (mean over the
  packed meshes of a). With no placement effect it has variance sigma_c^2 (1 / m_swapped + 1 / m_packed), sigma_c^2 for
  set 0 and sigma_c^2 / 2 for sets 1 to 4, plus each mesh's inflated binomial variance divided by its layout's m
  squared; z = delta / sqrt(that). A block moved beyond the mesh variance when |z| > 4.5, and the placement lies beyond
  the mesh variance when at least 2 blocks do and the slot homogeneity holds. The same Monte Carlo with no placement effect returns "beyond" in 0 of
  2,000 replicates under each of: one sigma of 0.03 for both classes; class sigmas 0.05 and 0.01 with Gaussian, Student
  t3, and Student t3 times a log-normal (0.5) scale per compiled mesh; and one slot at three times the mesh scale, where
  the slot check withholds "beyond" in 99.9 percent of replicates (96.7 percent with t3 tails). Under the heavy-tailed
  t3 nulls the slot check also withholds in 19 to 24 percent of replicates, which only moves a reading to "not shown
  beyond". A per-block drift step between a set's two jobs (standard deviation 0.02 to 0.10 times 2 sqrt(a (1 - a)))
  returns "beyond" in 0 of 1,000 replicates; it raises the mesh sigma slightly and moves the earlier-excess verdict
  toward "mesh", and its kappa^2 (median 8 to 150) fires the drift statistic that stops the case. Blocks moved against
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
  deltas made entirely of mesh error at the old-delta bound (sigma 0.059 and 0.029) read mesh in all of the
  uncorrelated outcomes but one; a mesh error of half that size (0.03 and 0.015) reads window in 99.9 percent of them;
  and a mesh error of 0.01 and 0.003, which leaves the earlier deltas to drift, reads excess in all of them, while 23
  percent of all replicates of that model read "no moves", because no block then moves against binomial error alone.

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
- *Backend and budget.* `qpu:belenos`. Job-00 ran 12 iterations and billed 1.018 credits. Eight packed jobs of 5
  iterations of 30,000 samples each, `max_shots` 90,000 per iteration and `min_detected_photons` 1, submitted one after
  the other: 1.09 credits per job, 8.72 for the eight, 9.738 for the case. Expected seconds are 260 per job against
  the 300 s limit.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` and `submit` with `--platform qpu:belenos
  --max-credits 1.09 --expected-seconds 260 --per-job-credits 1.0 --admit-status running`, `collect`, and after all
  nine `scripts/belenos_mode_swap_interleaved.py --analyze` on the runs of job-00 and job-03 to job-10. Each run
  records the platform's HOM, g2 and transmittance at its plan.
- *Stopping rule.* A set's second job is planned and submitted as soon as its first job returns and its mesh digests
  check (primary repeats on one mesh, replicates distinct), which keeps the gap between them short. After a set's
  second job, the set's drift statistic D and the job's duration are read before the next set: a set whose primary
  repeats return two meshes in every pair, whose replicates return their primaries' meshes, or whose kappa^2 exceeds
  20 stops the case for the owner, and so does a job that ran longer than 270 s. At 30,000 samples a primary pair's
  two-sample standard error is about 0.0095, so D detects a step of 0.01 to 0.02 between a set's two jobs, which the
  Monte Carlo shows leaves the readings unchanged (kappa^2 median 8.5); the excess verdict moves toward "mesh" from a
  step of about 0.05 (kappa^2 about 43). A set whose D detects drift below that threshold is recorded and the case
  continues. A job that errors or is cut
  short is resubmitted only on the owner's further approval.

## Outcome

All nine jobs ran on 2026-10-31 (claim `qd-belenos-mode-swap-per-seed-mesh-variance` in
[research_state.json](../state/research_state.json)). Job-00 (`dc348230`, HOM 88.6 %) returned set 0 before its cut;
job-03 to job-10 (HOM 87.5 %, g2 1.2 %, transmittance 5.42 %) each returned five iterations of 30,000 samples in 213
to 245 s, 43 to 49 s per iteration. Every primary pair kept one mesh, across the two jobs of sets 1 to 4, and every
replicate returned a distinct mesh.

| Statistic | Value |
|---|---|
| Within-set drift D (12 degrees of freedom each), sets 0 to 4 | 4.9, 17.2, 3.9, 15.9, 22.4; pooled p 0.33; largest kappa^2 1.87 |
| Mesh sigma, half blocks | 0.0515 on 68 degrees of freedom (upper bound 0.060), spread 50 times binomial |
| Mesh sigma, extreme blocks | 0.0177 on 88 degrees of freedom (upper bound 0.020), spread 80 times binomial |
| Slot homogeneity | slot 5 S 85.9 on 26 degrees of freedom, p 2.5e-8; slots 0 to 4 p 0.55 to 1 |
| Blocks beyond the mesh variance | 1 of 30 (z -5.39, an extreme block of set 0 on slot 5); 23 of 30 against binomial error alone |
| New against earlier deltas | r 0.15 (-0.23 to 0.48), 22 of 30 signs agree (p 0.008): uncorrelated |
| Earlier excess | X(1) 46.2, X(3) 15.5 against q 50.9: mesh |
| Slot predictor (descriptive) | r 0.18 (-0.39 to 0.65) |

Reading: moves not shown beyond the mesh variance do not follow the earlier deltas, which stay within the per-seed mesh
variance: the earlier deltas read as mesh error. The packed-swapped deltas of claim `qd-belenos-packed-mode-swap` are
the size two compiled meshes of one layout differ by, and the reversed-sign slot pattern does not recur. Slot 5 (chip
modes 20 to 23) carries larger per-seed mesh error than the other slots, from seed-to-seed jumps of 0.07 to 0.13 in
extreme blocks of sets 0, 1 and 3. The sign agreement above chance leaves room for a placement component smaller than
the mesh error, which this design cannot resolve.
