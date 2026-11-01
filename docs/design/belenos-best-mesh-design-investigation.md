# Belenos best-mesh teleportation: design investigation

This document asks whether a screen-then-replay experiment that picks the best compiled mesh per teleportation input
on `qpu:belenos` is a sound design, and answers from the retained data alone. It proposes no job and asks for no
approval. The numbers come from `scripts/belenos_best_mesh_first_principles.py` and its record
[results/quandela/belenos-best-mesh-first-principles.json](../../results/quandela/belenos-best-mesh-first-principles.json),
seeded from `qrng:docs/evidence/anu_qrng/draw-2026-10-31T193354Z.json#0`.

## Question

The split teleportation rehearsal ([ascella-belenos-entanglement-teleportation.md](ascella-belenos-entanglement-teleportation.md),
claim `qd-belenos-teleportation-split-blocks-mesh-error`) ran each of the six inputs (+Z, -Z, +X, -X, +Y, -Y) on two
compilation seeds, block A in job-02 and block B in job-03. Per-seed compiled-mesh error is the dominant error on this
chip, and a seed reproduces its mesh ([strategy.md](../notes/quandela/strategy.md) section 2, claims
`qd-belenos-compilation-seed-selects-mesh` and `qd-belenos-mode-swap-per-seed-mesh-variance`). The pooled
accepted-event correctness of 0.823 over twelve meshes is therefore an average over the meshes twelve seeds drew.

A drafted case proposed four screen jobs of six candidate seeds per input, then two confirmation jobs replaying each
input's best seed, to measure how much per-input mesh selection raises correctness over the mesh average. The
question here is whether that design measures something worth its credits.

## Findings

Block A pools job-02 with its exact replay (`...-job-02-replay`), which used the same seeds and meshes.

| Input | Block A correct / accepted | Block B correct / accepted | z (B - A) | Expected gap after shrinkage | Winner sign determined |
|---|---|---|---|---|---|
| +Z | 255 / 331 (0.770) | 85 / 97 (0.876) | -2.61 | 0.074 | yes |
| -Z | 359 / 397 (0.904) | 231 / 271 (0.852) | +1.99 | 0.043 | yes |
| +X | 186 / 236 (0.788) | 96 / 131 (0.733) | +1.18 | 0.036 | no |
| -X | 170 / 201 (0.846) | 117 / 133 (0.880) | -0.89 | 0.024 | no |
| +Y | 244 / 295 (0.827) | 127 / 140 (0.907) | -2.43 | 0.061 | yes |
| -Y | 203 / 263 (0.772) | 112 / 157 (0.713) | +1.32 | 0.039 | no |

1. **The compiler is exact; the error is on the chip.** All 18 retained meshes (the record's `compiled` section)
   reproduce their target click distribution within total variation 2.3e-4 and conditional fidelity 0.9999998 of the
   target, so the per-seed differences arise in the hardware that realizes a mesh, not in the decomposition.
2. **The between-mesh spread is real but small.** The six differences give chi-square 20.5 on 6 degrees of freedom.
   A normal-normal model with the between-mesh standard deviation tau carried as uncertain (Efron 2011, "Tweedie's
   formula and selection bias", J. Am. Stat. Assoc. 106:1602, Eqs. 3.7-3.9) gives tau 0.057 at its maximum likelihood,
   posterior mean 0.074, 90 % interval 0.029 to 0.143. The expected gain of the observed winner over the loser after
   shrinkage averages 0.046 over the inputs. Directional Benjamini-Hochberg at q 0.10 (Weinstein and Yekutieli,
   arXiv:1404.7403) fixes the winner's sign for +Z, -Z and +Y only.
3. **A replay of the winners has modest power.** Posterior-predictive simulation (200,000 trials, 1,200 samples per
   iteration) gives power 0.73 with two six-iteration jobs and 0.87 with four, falling to 0.54 and 0.70 when three of
   the six pairs drop out; size is 0.051 when no mesh error persists. The drafted case's expectation of 0.95 with four
   jobs does not hold. Each job costs 5.0 credits at the lossiest mesh's 2,662 shots per sample.
4. **Acceptance moves against correctness.** Within an input, the mesh with the higher acceptance per sample reads
   the lower correctness (r -0.75, exact one-sided permutation p 0.040, direction stated beforehand), and more herald
   rejections go with higher correctness (r +0.87, p 0.0069, direction found after looking). Winners average 0.114
   accepted events per sample, losers 0.138. Part of a winner's advantage is therefore a filter: its mesh rejects more
   of the events that would have been wrong. Both results are exploratory.
5. **The source does not explain the spread.** The provider's source model at the day's three calibration reads
   (04:27, 05:02 and 09:52 UTC: HOM 0.879, 0.886, 0.875; g2 0.014, 0.014, 0.012) moves the predicted mean conditional
   fidelity by at most 0.006 between reads. Perceval maps the reported HOM value directly to its overlap parameter, and
   its g2 penalty is smaller than the distinguishable-photon form of Ollivier et al. (arXiv:2005.01743, Eqs. 1-2);
   either reading leaves the source-only prediction input-asymmetric (+Z 0.77, -Z 0.99). The +Z and +Y block-B meshes
   exceed that prediction by about three standard errors, which a source term cannot produce.
6. **No structural property of a mesh predicts the winner.** Robustness of each compiled mesh to heater noise (0.1 rad)
   and coupler noise (0.05 rad) and its total heater phase do not order the pairs (r -0.03, 0.18 and +0.54, the last
   opposite to the predicted direction).

## Verdict

The screen-then-replay design as drafted is weak as a primary experiment.

- Selecting a mesh per input voids any comparison of the selected correctness against the classical bound of 2/3
  (Horodecki et al., [quant-ph-9807091](../notes/papers/quant-ph-9807091.md)): the selection makes the protocol
  input-dependent, and the bound's average over inputs no longer describes it.
- The expected gain, 0.046, is small, part of it is the acceptance filter of finding 4, and a confirmation has power
  0.73 to 0.87 at 10 to 20 credits.
- Nothing measured in advance identifies a better mesh (finding 6), so selection needs a hardware screen every time
  the chip recalibrates.

The design does carry one valuable question: whether a seed's mesh, and its error, survive a recalibration. A replay
of the job-02 and job-03 seeds after a recalibration answers it directly, and the answer decides whether per-seed
selection can ever pay.

## What to do instead

1. **Herald-leak pattern analysis, offline and free.** The 18 retained iterations hold the full click patterns of the
   rejected events. Classifying the herald rejections per mesh and input tests whether the acceptance filter of finding
   4 is a specific leak (one herald pattern, one mode pair) or a broad loss, using data already paid for.
2. **A persistence case, written after that analysis.** Replay the twelve job-02 and job-03 seeds at a later
   calibration read, report acceptance beside correctness per mesh, and test the correlation of each mesh's
   correctness across the two reads. It needs the owner's approval of its written case like every provider job.

## What this does not establish

- Whether the meshes of job-02 and job-03 still exist after the chip's recalibrations since 2026-10-31.
- Whether the acceptance-correctness relation holds outside these six inputs and twelve meshes.
- Any per-mesh mechanism: the structural predictors tested are the ones computable from the compiled phases alone.

Efron 2011 (PMC3325056) and Weinstein and Yekutieli (arXiv:1404.7403v4) are cited by their public identifiers; their
admission to the source registry is open.
