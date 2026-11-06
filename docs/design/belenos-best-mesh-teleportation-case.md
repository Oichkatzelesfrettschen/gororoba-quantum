# Belenos best-mesh teleportation

**Status: unapproved draft, superseded.** No job of this case was sent and none is proposed. The design
investigation [belenos-best-mesh-design-investigation.md](belenos-best-mesh-design-investigation.md) answers whether
this design is sound, with corrected figures (block A pools job-02 with its exact replay; replay power 0.73 to 0.87),
and recommends a persistence replay instead. The figures below are the draft's own and stay as written. The
builder's `--check` rebuilds the four retained screen cases byte for byte and binds every iteration, then fails its
duration requirement: nine iterations at 31 s bound 279 s against the 270 s margin of the 300 s job limit.

`scripts/belenos_teleportation_best_mesh.py` runs a screen-then-replay design on `qpu:belenos`: it
screens compilation seeds for each of the six teleportation inputs, selects the seed whose compiled mesh teleports
that input best, and replays the selected seeds to measure the selected meshes without selection bias.

## Question

The split teleportation rehearsal (claim `qd-belenos-teleportation-split-blocks-mesh-error`,
[ascella-belenos-entanglement-teleportation.md](ascella-belenos-entanglement-teleportation.md), "Split recovered-chip
rehearsal") read a pooled accepted-event correctness of 0.823 (1495 of 1816) over twelve meshes, one per input and
block, with an anytime-valid lower bound of 0.787. Per-seed compiled-mesh error is the dominant error on this chip and
a seed reproduces its mesh ([strategy.md](../notes/quandela/strategy.md) section 2; claim
`qd-belenos-mode-swap-per-seed-mesh-variance`), so 0.823 is an average over the meshes twelve seeds drew. The per-input
correctness of the two blocks differs beyond binomial error:

| Input | Block A seed, correct / accepted | Block B seed, correct / accepted | z of the difference |
|---|---|---|---|
| +Z | 122 / 163 (0.748) | 85 / 97 (0.876) | -2.68 |
| -Z | 187 / 206 (0.908) | 231 / 271 (0.852) | +1.88 |
| +X | 101 / 124 (0.815) | 96 / 131 (0.733) | +1.57 |
| -X | 86 / 100 (0.860) | 117 / 133 (0.880) | -0.44 |
| +Y | 122 / 146 (0.836) | 127 / 140 (0.907) | -1.82 |
| -Y | 109 / 148 (0.736) | 112 / 157 (0.713) | +0.45 |

The sum of squared z is 16.9 on 6 degrees of freedom (p about 0.01), and after the binomial variance the between-mesh
standard deviation of an input's correctness is about 0.041. The case asks how much a mesh selected per input raises
the correctness over the mesh average, and measures the selected meshes on fresh data.

## Design

The circuits are job-02's: layout `(18, 19, 20, 17, 22, 23, 16, 21)` on chip modes 16 to 23, the eight-mode template
of `qd_teleportation_rehearsal`, and the six inputs +Z, -Z, +X, -X, +Y, -Y, each read in its matching basis with the
Pauli frame applied in analysis. Keeping job-02's circuit parameters lets the job-02 and job-03 seeds identify their
earlier meshes. The layout includes chip modes 20 to 23, where the mode-swap case found heavier per-seed mesh tails,
which is where selection has the most room.

1. **Screen.** Four jobs of nine iterations, 600 samples per iteration. Each input gets six candidate seeds: its job-02
   seed and its job-03 seed (imported by constant name, so they replay their earlier meshes if the mesh survives the
   recalibration since) and four new seeds from a fresh ANU QRNG draw. Inputs alternate within each job so every job
   carries every input at least once; the first screen job is measured for duration before the others are sent.
2. **Select (preregistered before any screen data).** Per input, the candidate with the highest screen correctness
   (correct over accepted); ties go to the candidate with more accepted events, then to the lower seed index.
3. **Confirm.** Two jobs that each replay the six selected seeds at 1,200 samples, submitted right after the screen.
4. **Baseline.** The mesh average: per input, the mean over its six screened candidates of their screen correctness,
   averaged over the six inputs, with the between-mesh variance of the candidates in its standard error (design rule 1
   of strategy.md section 7).

## Analysis (preregistered)

- **Primary.** The confirmed correctness (pooled over both confirm jobs, per input, then averaged over inputs) minus
  the baseline, tested one-sided at alpha 0.05 with the confirm binomial variance plus the baseline's between-mesh
  variance. The selected meshes' screen scores are biased upward by the selection and enter no test; only the replay
  is the result.
- **Secondary.** The confirmed pooled correctness and its anytime-valid lower bound, as in the descriptive rule of
  the rehearsal; mesh identity of every replay against its screen iteration (sha256 of `computed_circuit`); whether
  the job-02 and job-03 seeds return their retained meshes after the recalibration since 2026-10-31 04:27 UTC.
- **Excluded.** No beats-classical comparison. Selecting each input's mesh from that input's own screen data makes
  the instrument depend on the input label, which breaks the first assumption of both classical comparisons of the
  rehearsal ("one label-blind trace-nonincreasing instrument acts on every input").

## Power

A Monte Carlo of the screen, selection and confirm at the A/B mesh spread (per-input means from the table, acceptance
0.10 to 0.20 per sample, 4,000 trials) gives:

| Candidates per input | Confirm jobs | Expected gain over the mesh average | P(z > 1.645) | Credits |
|---|---|---|---|---|
| 6 | 2 | +0.036 | 0.81 | about 21 |
| 6 | 1 | +0.036 | 0.70 | about 16 |
| 4 | 2 | +0.029 | 0.62 | about 17 |

With no mesh spread the test fires at 0.050; at a mesh spread of 0.06 the gain is +0.062 and the power 0.97. The case
takes six candidates and two confirm jobs.

## Budget and timing

Shots per sample ran 1,700 to 2,660 across the job-02 and job-03 iterations; -Z under its block-B seed reached the
3,000,000 `max_shots` at 1,127 samples. `max_shots` per iteration is samples times 2,660 times a margin: about 1.9
million for a 600-sample screen iteration (2.9 credits per screen job) and about 3.7 million for a 1,200-sample confirm
iteration (4.7 credits per confirm job). Four screen and two confirm jobs ceil at about 21 credits. A teleportation
iteration took 21 to 31 s at about 2.2 million shots; a screen iteration at about 1.3 million shots is unmeasured, so
the first screen job's duration sets whether nine iterations fit before the rest are sent.

## Stopping rule

The case stops for the owner when the first screen job runs past 270 s, when a job returns fewer iterations than
requested, when the platform's HOM, g2 or transmittance read changes between the screen and the confirm, or when a
confirm replay returns a mesh other than its screen iteration's. A job that errors or is cut short is resubmitted only
on the owner's further approval.

## Open questions for review

- Whether point-correctness selection or lower-bound selection serves the confirm better at about 75 accepted events
  per screen iteration.
- Whether the screen should weight inputs by their mesh spread (more candidates for +Z and +Y, whose A/B difference is
  largest).
- Whether the baseline should be the screen's mesh average or a fresh random-seed arm inside the confirm jobs.
