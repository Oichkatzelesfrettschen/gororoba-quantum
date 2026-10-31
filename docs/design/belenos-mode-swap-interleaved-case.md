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

- **Primary arm, iterations 0 to 3.** The order packed, swapped, swapped, packed (ABBA) runs each layout twice under one
  compilation seed. The two repeats request one compiled mesh, so their difference is drift at a fixed mesh. ABBA gives
  packed and swapped the same mean time, so linear drift cancels in the primary packed-swapped contrast.
- **Replicate arm, iterations 4 and 5.** One packed and one swapped iteration under a second compilation seed per layout.
  The replicate against the primary of the same layout is a same-layout, different-seed contrast, which measures the
  per-seed mesh variance directly. An even block set runs the replicate pair packed, swapped and an odd one swapped,
  packed.

**Order.** Six slots cannot balance every contrast against a linear drift. Packed and swapped share a mean time only when
the three slots of each sum to 7.5, which integer slots cannot do, and a primary pair shares a mean time with its single
replicate only when the replicate sits between the pair, which forces the alternation packed, swapped, packed, swapped,
packed, swapped and puts the packed and swapped means three slots apart. The order keeps the exact balance in the ABBA
pair, the contrast the claim rests on, and appends the replicate pair after it. The mesh-averaged placement contrast
then carries a drift imbalance of half a slot (about 8 s), with opposite sign in even and odd block sets, so it largely
cancels over the five sets. The replicate sits 2.5 to 3.5 slots (about 40 to 55 s) from the mean time of its primary
pair, so drift between them adds to the measured mesh variance and raises the bar the placement contrast must clear; a
drift artifact never lowers it.

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
  15 to 45 s apart and the earlier confound was an hour, so D carries no statement about the earlier claim. The inflation
  kappa^2 = max(1, D / dof) of a job scales every binomial variance of that job's blocks, which covers extra dispersion
  between iterations. A job with no mesh-identical pair (dof 0) withholds the placement reading, and so does a replicate
  digest that equals its primary digest or is missing.
- **Mesh variance.** For each block and layout, R = a(replicate) - a(primary, repeats pooled) has variance 2 sigma^2 plus
  the inflated binomial variances. sigma^2 is the mean of (R^2 - inflated binomial variance) / 2 over the 60 contrasts,
  truncated at 0. The excess ratio, sum R^2 over the sum of the inflated binomial variances, is reported beside it.
- **Placement against the mesh variance.** For each block, delta = (a(swapped, primary) + a(swapped, replicate)) / 2 -
  (a(packed, primary) + a(packed, replicate)) / 2. With no placement effect it has variance sigma^2 plus a quarter of the
  inflated binomial variances of its four cells, and z = delta / sqrt(sigma^2 + binomial variance). A block moved beyond
  the mesh variance when |z| > 4.5, and the placement lies beyond the mesh variance when at least 2 blocks do. With the
  scale estimated from ten independent set-layout pairs, a block crosses 4.5 under mesh error alone with probability
  about 0.0011 (Student t, 10 degrees of freedom), so one block of 30 does so about 3 percent of the time and two or
  more below 0.1 percent. Blocks moved against binomial error alone are the `moved` blocks of `decide()` on the pooled
  table, the earlier criterion. The six blocks of one set share their meshes and the pooled scale assumes one sigma for
  all blocks; `analysis.json` lists the contrasts per block and layout so a reader can see heterogeneity.
- **Slot predictor.** `decide()` of `qd_packed_mode_swap_analysis.py` runs once on the pooled packed and swapped table of
  all 30 blocks, each share taken over every iteration of its layout. Each block's predictor is the packed mean of the
  other half blocks on its swapped slot, taken from other block sets and so from other compiled meshes. The slot
  predictor's r with its Fisher 95 percent interval reads a **reversed-sign chip-mode effect** when the upper bound is
  below -0.3, a **positive-sign chip-mode effect** when the lower bound is above +0.3, and no sign-specific chip-mode
  reading otherwise. The verdict string of `decide()` is reported but carries no reading, since it returns `slot` only
  for a positive correlation. Fourteen half blocks give a Fisher half-width of 0.59 in z.
- **Comparison with the earlier deltas.** For each block, delta_new = a(swapped) - a(packed) of the pooled table is
  compared with delta_old of the retained `qpu_belenos` series (`qd_packed_mode_swap_analysis.collect`). The case
  reports the number of blocks whose signs agree with the one-sided exact binomial p against one half, and Pearson r with
  its Fisher interval. The comparison reads **reproduce** when r has a lower bound above 0.3 and the sign p is below
  0.01, **uncorrelated** when r has a lower bound at or below 0.3 and an upper bound below 0.7, and **indeterminate**
  otherwise. The new and the earlier deltas also differ in mesh, since the retained jobs carried no compilation seed.

### Reading

The reading table combines the placement class (no block moved against binomial error; moves beyond the mesh variance;
moves within it) with the comparison class.

| Placement | Comparison | Reading |
|---|---|---|
| no block moved | any | no moves: the earlier separation fails |
| beyond the mesh variance | reproduce | moves beyond the mesh variance reproduce the earlier deltas: not hour-scale drift |
| beyond the mesh variance | uncorrelated | moves beyond the mesh variance do not follow the earlier deltas: mesh-specific |
| beyond the mesh variance | indeterminate | moves beyond the mesh variance with the earlier deltas neither reproduced nor excluded: inconclusive |
| within the mesh variance | reproduce | moves within the per-block mesh variance reproduce the earlier deltas: not hour-scale drift, placement per block unresolved |
| within the mesh variance | uncorrelated | moves within the mesh variance do not follow the earlier deltas: mesh-specific |
| within the mesh variance | indeterminate | moves within the mesh variance with the earlier deltas neither reproduced nor excluded: inconclusive |

The preregistered interpretation in each `cases.json` repeats this paragraph:

The design shows whether moving a packed block changes its algebra-mode share by more than that share varies between
compiled meshes of one layout, and whether the per-block changes reproduce the changes of the earlier separate jobs.
Reproduction rules out hour-scale drift as their source; changes that do not follow the earlier deltas, or that stay
within the mesh variance, read as mesh-specific. The slot predictor of the pooled blocks reads the sign of the chip-mode
effect. The design does not show how a chip mode changes a share.

## Written case

- *What it measures.* Whether the packed series' block residual follows placement beyond the per-seed mesh variance, and
  whether it reproduces the earlier deltas, with mesh-identical primary repeats as the within-job validity reference and
  a replicate seed per layout as the mesh reference.
- *Why a simulation cannot answer it.* The residual is the chip's compiled-mesh and detection error at each slot; an
  ideal or noise-model simulation gives every block its exact share at every slot and every seed.
- *Backend and budget.* `qpu:belenos`, three jobs submitted one after the other, 12, 12 and 6 iterations of 6,000
  samples, `max_shots` 18,000 per iteration and `min_detected_photons` 1. The credit ceiling is 1.018 per job and 3.054
  for the case. Expected seconds are 190, 190 and 100 against the 300 s limit.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` and `submit` with `--platform qpu:belenos
  --max-credits 1.018 --expected-seconds 190 --per-job-credits 1.0 --admit-status running` (expected seconds 100 for
  job-02), `collect`, and after all three `scripts/belenos_mode_swap_interleaved.py --analyze RUN_00 RUN_01 RUN_02`.
