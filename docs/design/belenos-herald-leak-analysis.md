# Belenos herald-leak pattern analysis

This analysis classifies the herald rejections of the split teleportation rehearsal on `qpu:belenos` by click pattern
and asks whether a compiled mesh changes where herald clicks land (a specific leak) or only how many there are (a broad
loss). It reads retained data only, sends no job and asks for no approval. It is the first item of "What to do
instead" in [belenos-best-mesh-design-investigation.md](belenos-best-mesh-design-investigation.md), whose finding 4
reads that the mesh with more herald rejections per sample reads the higher correctness (r +0.87, found after looking).

## Preregistration

This section was committed before any herald pattern was tabulated by block.

### Data

- Runs: `results/quandela/runs/2026-10-31T035736Z-qpu_belenos-teleportation_rehearsal-job-02` (block A),
  its exact replay `2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay` (block A, same compilation seeds and meshes) and
  `2026-10-31T040337Z-qpu_belenos-teleportation_rehearsal-job-03` (block B, other seeds), six inputs each, 18 iterations.
- Events: each iteration's `results.json` counts, classified by `qd_teleportation_rehearsal.classify` under the
  run's `cases.json` layout. A herald event has exactly three clicks, all on the eight logical modes
  (q0, q1, a0, a1, b0, b1, h0, h1), at least one of them on h0 or h1. Its pattern is the set of three clicked
  logical modes; 36 patterns exist.
- Samples per iteration come from the run's `analysis.json`.

### Primary test: mesh-dependent herald composition

Per input, the herald events of block A (job-02 and its replay pooled) and block B form a two-row table over the
patterns either block observed. The statistic is the Pearson chi-square of that table; the inputs' statistics add. The
null distribution conditions on each input's pattern totals and block totals: 20,000 multivariate hypergeometric
reallocations of each input's herald events between the blocks, the six inputs reallocated independently, from a
generator seeded with `qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#0`. The global p-value is the share
of reallocated sums at or above the observed sum, with the observed table counted among the draws. Alpha is 0.05.

### Null arm: same mesh, two runs

The same test between job-02 and its replay, which ran the same seeds and the same meshes 29 minutes apart, measures
how much the herald composition moves without a mesh change. The null arm runs with the same draws and alpha.

### Decision rule

| Primary | Null arm | Verdict |
|---|---|---|
| rejects | does not reject | the mesh changes the herald composition |
| rejects | rejects | composition drifts within one mesh; the mesh contrast is not attributable |
| does not reject | either | herald composition does not depend on the mesh at this power: a broad loss |

When the mesh changes the composition, each input is localized. An input carries a specific leak when one pattern
contributes at least half of that input's chi-square and its adjusted standardized residual exceeds 3.20 in absolute
value (two-sided 0.05 Bonferroni over 36 patterns). The analysis reports a specific leak overall when at least three of
the six inputs carry one and every such leak clicks the same herald mode (h0 or h1); otherwise it reports a broad
change of composition.

### Secondary, exploratory

- **Filter link.** Per input, the B minus A difference of per-sample rates of correct accepted, wrong accepted,
  herald-rejected and other-rejected events. Finding 4's filter reading predicts that the herald rate and the wrong
  rate move in opposite directions while the correct rate moves less than the wrong rate. The count of inputs that
  match and its one-sided sign-test p-value are reported; with six inputs this is descriptive.
- **Other rejection reasons.** Per mesh, the per-sample rates of the excess, outside, receiver and pattern
  rejections beside the herald rate, for both comparisons.

## Results

`scripts/belenos_herald_leak.py` writes
[results/quandela/belenos-herald-leak.json](../../results/quandela/belenos-herald-leak.json) from
`--seed qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#0` and replays it byte for byte. Its
classification of every iteration reproduces the correct, wrong, sample and rejection counts of each run's retained
`analysis.json`.

**Verdict: the mesh changes the herald composition, and the change is broad.** The mesh contrast sums to chi-square
1285.1 (p 1/20,001, the smallest the 20,000 draws can report); the same-mesh null arm sums to 208.2 (p 0.30). No
input meets the specific-leak rule: the top pattern of each input carries 12 % to 29 % of that input's chi-square,
below the preregistered half.

| Input | Herald events A / B | Chi-square, mesh contrast | Chi-square, null arm | Top pattern | Its share | Its adjusted residual (A) |
|---|---|---|---|---|---|---|
| +Z | 1574 / 876 | 94.7 | 34.9 | a0+b0+h0 | 0.13 | -3.64 |
| -Z | 1674 / 669 | 404.6 | 33.9 | a1+b1+h0 | 0.16 | -8.08 |
| +X | 1837 / 907 | 238.0 | 45.9 | a1+h0+h1 | 0.29 | -8.59 |
| -X | 1898 / 952 | 176.1 | 22.0 | a1+b1+h1 | 0.14 | -4.91 |
| +Y | 1739 / 924 | 69.9 | 41.3 | a1+b1+h0 | 0.19 | -3.70 |
| -Y | 1806 / 843 | 301.8 | 30.2 | a1+b0+h1 | 0.12 | +6.08 |

Each input's table spans 33 to 36 observed patterns, so the null-arm chi-squares sit where homogeneity puts them and
the mesh-contrast chi-squares exceed them by a factor of 1.7 to 12. Block A pools two runs and so carries about twice
block B's herald events.

**Filter link (exploratory).** Three of six inputs match the filter reading (herald and wrong rates move in opposite
directions and the correct rate moves less than the wrong rate), sign-test p 0.66, and the null arm also matches
three of six. The herald rejections do not act as a filter that removes would-be wrong events. The per-sample rates
are shares of the detected three-click events, so the four differences of an input sum to zero; in five of six
inputs the herald share and the other-rejection share (excess, outside, receiver, pattern) move in opposite
directions, with the largest swings at -Z (herald -0.104, other +0.029, correct +0.055) and +Y (herald +0.045, other
-0.039). A mesh moves events between rejection classes as a whole.

**Observed after looking.** Four of the six top patterns click a1, which sits on chip mode 17, the one logical mode
out of ascending order in the layout `(18, 19, 20, 17, 22, 23, 16, 21)`. No test was stated for this, and it raises
the question for the persistence case rather than answering it.

### Consequence for the best-mesh program

Finding 4 of the design investigation read part of a winning mesh's advantage as an acceptance filter. The herald
composition depends strongly on the mesh, but no single herald pattern or mode carries the difference, and the
herald share does not trade against the wrong share more often than between two runs of one mesh. The mesh error
redistributes photons across the output broadly. A per-seed mesh error of this kind needs the persistence replay
(item 2 of the investigation's "What to do instead") to show whether it survives a recalibration; this analysis gives
that case no narrower target.
