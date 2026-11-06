# Per-seed mesh error on Ascella: first principles, controls and what remains

This note decomposes the persistent per-mesh error that job-08 measured
([long-horizon reading](long-horizon-reading-03-08.json)) into the sources a persistent deviation can have, states
each assumption the readings rest on with the check that tests it, and records what remains open. The numbers come
from [long-horizon-controls.json](long-horizon-controls.json), written by
[`scripts/ascella_mesh_error_controls.py`](../../../scripts/ascella_mesh_error_controls.py) from job-02, job-03 and
job-08, and from the reading records beside it.

## What is measured

Each of the 64 iterations prepares one photon in mode 0 of `qpu:ascella`, applies the theta2-x-arm0 order operator
of the signed-coherence design followed by the X analyzer on modes 0 and 3, and counts single clicks. The statistic is
z = (n0 - n3) / N over the clicks in modes 0..3; its logical ideal is 0.90451 for every iteration. Iterations differ
only in the compilation seed, which selects the served mesh (the phases the transpiler returns for the same logical
unitary); eight seed-0 anchors repeat one mesh. The per-mesh error is each perturbed mesh's z minus the mean over the
56 perturbed meshes.

## Three possible sources

A deviation that repeats for the same seed can come from the compiler, from the analysis, or from the chip.

**Compiler (refuted).** A served circuit that implements another unitary than the target carries a deterministic error
that would repeat exactly, as Franco et al. (arXiv:2604.04691) report for compile non-convergence on Ascella. Each
served circuit's own ideal z, from its unitary and computed input, has mean 0.904500 and standard deviation 9.8e-5
across the 56 perturbed meshes, against an observed per-mesh standard deviation of 0.0114, 0.0117 and 0.0104 in
job-02, job-03 and job-08; the served ideals are identical in all three jobs and correlate with the observed
deviations at r = -0.10. A `sim:ascella` run that served the same meshes on 2026-11-06 spread its z at counting noise
(0.00211 against 0.00203). The served circuits implement the target to 1e-4; the error arises in their physical
realization.

**Analysis (refuted).** Every iteration of the three jobs echoes its setting's compilation seed and circuit parameters
(64 of 64 each), so each z belongs to the mesh its name claims. Paired by name, job-03 and job-08 correlate at
r = 0.925; paired by position, at r = -0.199. The same mesh sat at anticorrelated positions in the two jobs (rank
correlation -0.31), so a drift shared in time would oppose the observed agreement; removing each job's linear
position trend leaves r = 0.912. The relabeling tests use the identity plus 20,000 uniform relabelings, a valid Monte
Carlo reference set, and the reviews of the case confirmed the sampled bound
([reconciliation](../../archive/reviews/ascella-long-horizon-seed-repeat-reconciliation.md)).

**Chip (supported).** The same commanded phases reproduce the same error after twelve days and a software update that
left every compilation byte-identical. The dark-port share of each mesh also persists (r = 0.63 between job-03 and
job-08), as light that a phase error diverts from the bright output would. The repository's element-offset fits
predict part of the per-mesh error on unseen meshes (r 0.2 to 0.4, `replication-sensitivity.json`), so the remainder
lies in quantities the returned circuit and its fitted offsets omit; the applied heater voltages that Perceval#799
requests remain the direct test.

## Pattern and amplitude

Against job-03, P1 reads r = 0.925 beside the ceiling 0.936 that a fully fixed error reaches through both runs'
counting noise, 98.8 % of it: the pattern of errors across meshes is essentially unchanged. The slope, 0.815 beside
the 0.916 a fully persistent error reaches through job-03's counting noise, is 89 % of full persistence, and job-08's
per-mesh standard deviation (0.0104) is 88 % of job-03's (0.0117). A reading consistent with both: the chip keeps
the pattern and scales its amplitude down by about 11 %, as a recalibration that rescales a common error gain would
(hypothesis: the voltage-to-phase coefficients changed while the per-heater offsets held). A redrawn share would lower
r against its ceiling, which it does not.

## Per-seed correction

Because the error persists, a table of per-seed offsets fitted on earlier runs corrects later ones. Fitted on job-02
and job-03 alone (slope of job-03's centered z on job-02's, 0.914, times the mean of the two runs' centered z) and
applied to job-08 out of sample, it lowers job-08's per-mesh standard deviation from 0.0104 to 0.0037 (variance
1.07e-4 to 1.39e-5, a factor 7.7). The residual holds job-08's counting variance 4.6e-6, the table's own counting
noise (about 6e-6 from the 8,192- and 16,384-sample runs) and about 3e-6 of changed error. A correction that also
fits the amplitude would lower it further; it needs a held-out run to score.

## Assumption ledger

| Assumption | Check | State |
|---|---|---|
| A seed selects one served mesh | 64 of 64 settings byte-identical across job-02, job-03 and job-08, and across stacks within 2.4e-7 | holds |
| The served circuit implements the target | served ideal z within 1e-4 of the logical ideal | holds |
| Each z is attributed to its mesh | echoed seed and parameters, 64 of 64 per job | holds |
| Time, order and predecessor do not mimic persistence | position pairing r -0.20, anticorrelated positions, detrended r 0.91, predecessor-transition rank correlation -0.07 | holds |
| The counting variance is multinomial | anchor z standard deviation 0.0020 and 0.0015 against counting 0.0031 and 0.0021 | holds, conservative |
| The per-mesh errors are exchangeable under relabeling for the null | one setting, one block, meshes drawn by seed | assumed; holds for the null of no persistence |
| The ceiling uses job-02's compilation variance | s_c from `heater-coupling.json` (job-02) | assumed; job-08's own spread is smaller, so the ceiling for the job-03 pair is slightly optimistic |
| The power record's Gaussian model | designed before acquisition | assumed; it sized the case and decides nothing |

## What remains

- **Mechanism.** The returned circuit and its fitted offsets explain at most part of the error; the applied voltages
  are the missing quantity.
- **Amplitude change.** The 11 % shrink is one comparison between two runs; a third run separates a trend from noise.
- **Scope.** One logical setting on one chip. Another setting on the same seeds tests whether the error belongs to
  the mesh's phases or to their interaction with this setting.
- **Transfer.** Belenos replays the same question for its own meshes in
  [belenos-mesh-persistence-case.md](../../design/belenos-mesh-persistence-case.md), held until the chip returns.

## Higher Cayley-Dickson algebras and accuracy

The 32- and 64-dimensional work in the repository
([dimension-32 program](../../design/dimension32-global-topology-program.md)) classifies the topology of zero-divisor
rank strata; it makes no hardware prediction. A one-photon encoding of an n-dimensional left multiplication L_a
needs n modes, so a 32- or 64-dimensional operator exceeds Ascella's 12 modes and Belenos's 24, and a multi-photon
encoding runs through postselected gates at rates far below these jobs'. The per-mesh error is a property of how the
chip realizes a commanded mesh and appears whatever algebra the mesh encodes; the higher algebras supply mutation
tests and null arms that decide an algebraic question, never a lower hardware error. The accuracy levers this data
supports are the per-seed correction above, averaging over seeds (the error variance falls as one over the number of
meshes, Quandela's CompilationAveraging), and choosing low-error seeds from a measured table.
