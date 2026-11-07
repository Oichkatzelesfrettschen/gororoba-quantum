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

A deviation that repeats for the same seed can come from the returned circuit model, from the analysis, or from the
implementation path that turns a returned circuit into light (control firmware, heater mapping, the chip).

**Returned-model mismatch (refuted).** A served circuit that implements another unitary than the target carries a deterministic error
that would repeat exactly, as Franco et al. (arXiv:2604.04691) report for compile non-convergence on Ascella. Each
served circuit's own ideal z, from its unitary and computed input, has mean 0.904500 and standard deviation 9.8e-5
across the 56 perturbed meshes, against an observed per-mesh standard deviation of 0.0114, 0.0117 and 0.0104 in
job-02, job-03 and job-08; the served ideals are identical in all three jobs and correlate with the observed
deviations at r = -0.10. A `sim:ascella` run that served the same meshes on 2026-11-06 spread its z at counting noise
(0.00211 against 0.00203). The returned circuit model reproduces the target z with a spread of 9.8e-5 (standard
deviation), a hundredth of the observed per-mesh spread; the control checks z, the statistic the reading uses, and
certifies no other element of the unitary. These fields are the
provider's reported model, not a readback of the applied voltages or of the implemented unitary (the design's
"Open problems after job-00" section), so the test excludes an error in that model and leaves every later stage open.

**Analysis (refuted).** Every iteration of the three jobs echoes its setting's compilation seed and circuit parameters
(64 of 64 each), so each z belongs to the mesh its name claims. Paired by name, job-03 and job-08 correlate at
r = 0.925; paired by position, at r = -0.199. The same mesh sat at anticorrelated positions in the two jobs (rank
correlation -0.31), so a drift shared in time would oppose the observed agreement; removing each job's linear
position trend leaves r = 0.912. The relabeling tests use the identity plus 20,000 uniform relabelings, a valid Monte
Carlo reference set, and the reviews of the case confirmed the sampled bound
([reconciliation](../../archive/reviews/ascella-long-horizon-seed-repeat-reconciliation.md)).

**Implementation path (supported).** The same commanded phases reproduce the same error after twelve days and a software update that
left every compilation byte-identical. The dark-port share of each mesh also persists (r = 0.63 between job-03 and
job-08), as light that a phase error diverts from the bright output would. The repository's element-offset fits
predict part of the per-mesh error on unseen meshes (r 0.2 to 0.4, `replication-sensitivity.json`), so the remainder
lies in quantities the returned circuit and its fitted offsets omit; the applied heater voltages that Perceval#799
requests remain the direct test. Control telemetry, voltage readback or an
independent witness of the implemented unitary is needed before the error is assigned to the photonic chip itself
rather than to the firmware and heater mapping that drive it.

## Pattern and amplitude

Against job-03, P1 reads r = 0.925 beside the ceiling 0.936 that a fully fixed error reaches through both runs'
counting noise, 98.8 % of it: the pattern of errors across meshes is essentially unchanged. The slope, 0.815 beside
the 0.916 a fully persistent error reaches through job-03's counting noise, is 89 % of full persistence, and job-08's
per-mesh standard deviation (0.0104) is 88 % of job-03's (0.0117). A reading consistent with both: the chip keeps
the pattern and scales its amplitude down by about 11 %, as a recalibration that rescales a common error gain would
(hypothesis: the voltage-to-phase coefficients changed while the per-heater offsets held). The 99 % Fisher interval of r is about
0.862 to 0.960, and the noise-corrected latent correlation is near 0.98, so a redrawn component small against the
persistent one is not detected at this precision; a bound on it needs a persistent-plus-redrawn variance fit or a
third run.

## Per-seed correction

The estimator below was defined after job-08 was retained and is not part of the preregistered plan, so it is a
retrospective analysis of a held run, not a prospective test. Because the error persists, a table of per-seed offsets
fitted on earlier runs can correct later ones. Fitted on job-02
and job-03 alone (slope of job-03's centered z on job-02's, 0.914, times the mean of the two runs' centered z) and
applied unchanged to job-08, whose data the table never saw, it lowers job-08's per-mesh standard deviation from 0.0104 to 0.0037 (variance
1.07e-4 to 1.39e-5, a factor 7.7). The residual holds job-08's counting variance 4.6e-6, the table's own counting
noise (about 6e-6 from the 8,192- and 16,384-sample runs) and about 3e-6 of unexplained residual. Frozen as written in
`scripts/ascella_mesh_error_controls.py`, the estimator is scored unchanged on the next acquisition of these seeds,
which makes the reduction a prospective result or refutes it.

The [prospective correction case](../../design/ascella-signed-coherence-conformance.md#prospective-correction-case-job-09)
froze that table by setting name in [`correction-table.json`](correction-table.json) before job-09 was sent, with a
decision rule fixed in advance: R = var(d) / var(d - t) and a 98 % bootstrap interval whose lower end must reach 2.
On job-09, eleven days after job-03, the frozen table lowers the per-mesh standard deviation from 0.01085 to 0.00337,
R = 10.37 with the interval 6.16 to 16.21 over meshes resampled as exchangeable seeds
([score](correction-score-09.json)); redrawing every run's counts and refitting the table gives the conservative range
3.88 to 7.95, still above 2. The correction is therefore prospective: it removes about 90 % of the per-mesh X variance
on these 56 seeds. Of the residual variance 1.13e-5, job-09's counting variance is 4.65e-6 (41 %) and the table's own
estimation noise 6.15e-6 (54 %); together they leave about 5e-7, against the plug-in benchmark R of 10.89.

## Assumption ledger

| Assumption | Check | State |
|---|---|---|
| A seed selects one served mesh | 64 of 64 settings byte-identical across job-02, job-03 and job-08, and across stacks within 2.4e-7 | holds |
| The served circuit implements the target | served ideal z: mean 0.904500 against the logical 0.904508, standard deviation 9.8e-5 across the 56 meshes, r = -0.10 with the observed deviations | holds for z, the statistic the reading uses; no other element of the unitary is checked |
| Each z is attributed to its mesh | echoed seed and parameters, 64 of 64 per job | holds |
| A shared linear drift or one-step predecessor effect does not mimic persistence | position pairing r -0.20, anticorrelated positions, detrended r 0.91, predecessor-transition rank correlation -0.07 | the bounded controls pass; nonlinear drift, longer-memory carryover and predecessor-mesh interactions remain untested |
| The counting variance is multinomial | anchor z standard deviation 0.0020 and 0.0015 against counting 0.0031 and 0.0021 | holds for the anchor mesh; mesh-dependent overdispersion remains untested |
| The per-mesh errors are exchangeable under relabeling for the null | one setting, one block, meshes drawn by seed | assumed; holds for the null of no persistence |
| The ceiling uses job-02's compilation variance | s_c from `heater-coupling.json` (job-02) | assumed; job-08's own spread is smaller, so the ceiling for the job-03 pair is slightly optimistic |
| The power record's Gaussian model | designed before acquisition | assumed; it sized the case and decides nothing |

## What remains

- **Attribution.** The persistent error sits in the implementation path; see "What the interface returns" for the
  data that could separate its stages.
- **Redrawn share.** Bounded only by the r interval above; a variance-component fit or a third run bounds it.
- **Correction.** The frozen per-seed table holds prospectively on job-09; its reach beyond these 56 seeds, and to
  settings other than theta2-x-arm0, is untested.

- **Mechanism.** The returned circuit and its fitted offsets explain at most part of the error; the applied voltages
  are the missing quantity.
- **Amplitude change.** The 11 % shrink is one comparison between two runs; a third run separates a trend from noise.
- **Scope.** One logical setting on one chip. Another setting on the same seeds tests whether the error belongs to
  the mesh's phases or to their interaction with this setting.
- **Transfer.** Belenos replays the same question for its own meshes in
  [belenos-mesh-persistence-case.md](../../design/belenos-mesh-persistence-case.md), held until the chip returns.

## Hardware layers and where the persistent error enters

| Layer | Ascella | Belenos | Error it contributes to these jobs |
|---|---|---|---|
| Source | one quantum-dot source demultiplexed onto inputs 0, 2, 4, 6, 8, 10 | one source onto 12 inputs (0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22) through an active demultiplexer and fibre delays (arXiv:2605.10471) | one photon per iteration here: HOM visibility does not enter; g2 (2 %) adds rare multi-photon events |
| Interferometer | 12-mode universal mesh | 24-mode universal mesh with thermal, voltage-controlled phase shifters (arXiv:2605.10471) | the compiled phases set the realized unitary; a heater's voltage-to-phase map and thermal crosstalk realize each mesh with its own error, the leading candidate for the persistent per-mesh error, which the data place in the implementation path without separating firmware from chip |
| Compiler | the seed selects one of many meshes for the same logical unitary; byte-identical across the 2026-11 update | the same, with sim and QPU meshes differing (strategy section 7) | the served circuits' ideal z spreads 9.8e-5 (standard deviation) around the target, a hundredth of the observed spread and uncorrelated with it, so the returned model adds no measurable error to z |
| Detection | 12 threshold detectors, clock 13.33 MHz | 24 threshold detectors, some quasi number-resolving, clock 4.94 MHz | dark counts and detector balance set the counting floor; they are time-ordered, not mesh-ordered |
| Loss | transmittance about 5.5 % | about 5.2 % | a mode-independent loss factor lowers the rate and cancels in z, which conditions on block clicks; mode-dependent transmission reweights the four block modes as the detector_efficiency family of `scripts/ascella_physical_models.py` does, and a per-mesh difference in it belongs to the implementation-path error the data do not separate |

The literature treats the interferometer layer the same way: element-level characterization followed by compensated
compilation corrects fixed MZI errors (arXiv:2103.04993), and variance-based calibration leaves residual phase errors
of 0.1 to 0.2 rad (arXiv:2607.14759). The cloud interface exposes neither the voltages nor the element calibration, so
the per-seed table is the black-box version of that correction, available at the seed level.

## What the interface returns

The cloud interface returns granular chip data, and none of it carries the per-mesh error.

- **Returned per element:** the processor record's `specs.architecture` and every served `computed_circuit` carry
  each fixed beam splitter's calibrated angle (`BS.Rx(theta=1.4535)` and `1.4467` on Ascella's first cell, against
  pi/2 for a balanced splitter) beside the commanded phases.
- **Returned per mode and per job:** input and output transmission and dark counts per mode in the processor record,
  and per iteration a noise model (g2, indistinguishability, transmittance) and `physical_perf`.
- **Static:** the architecture string has one digest (`26ce122dbfff`) on 2026-10-25 and 2026-11-06, shared by
  `qpu:ascella` and `sim:ascella`, and the served circuits are byte-identical across job-02, job-03 and job-08, while
  the per-mesh error's amplitude changed by about 11 % and HOM moved from 86.96 % to 88.98 %. A simulation of the
  served meshes under this model spreads z at counting noise alone, so the per-element calibration the interface
  returns does not contain the persistent error.
- **Absent:** the published OpenAPI document (`/openapi.json`, 35 paths, Quandela Cloud Api v2.10.1-rc1) and the
  processor routes it omits carry no heater voltage, voltage-to-phase coefficient, calibration timestamp or measured
  unitary; `GET /api/jobs/{job_id}/data` returns job metadata and the submitted payload, and
  `GET /api/jobs/{job_id}/status` returns progress.

The hardware remains measurable through ordinary jobs. Single photons injected on each source input (six on Ascella,
twelve on Belenos) give the moduli |U_ij|^2 of the implemented unitary's input columns, and two-photon interference
between inputs gives the relative phases without calibrated detectors (Laing and O'Brien, arXiv:1208.2868). Fitting
per-shifter phase offsets against the returned beam-splitter angles then locates the error element by element, as
an independent witness of the implemented unitary; it still measures the firmware and the chip together, since the
voltage-to-phase map lies inside them. Each such characterization is a provider job under its own written case.

## Higher Cayley-Dickson algebras: what folds onto 12 and 24 modes, and what it gains

**The fold is exact for coset-supported operands.** gororoba-open proves, at every tower order, that an operand
supported on one coset `anchor + G` of an XOR subgroup `G` of the basis cube gives a left multiplication that maps each
coset sector to the sector shifted by the anchor and vanishes across all others (`sparse_cross_sector_zero` and
`sparse_block_intertwining` in `proofs/theories/CDSparseBlockTransport.v`), and that its kernel is the direct sum of
the per-sector kernels (`sparse_kernel_decomposition`). A two-term operand `e_i + s e_j` spans `G = {0, i xor j}`, so
`L_a` at D = 32 or 64 is 16 or 32 two-by-two sign blocks; `RationalSignBlockRanks.v` certifies each such block's rank
as 1 or 2, and `SparsePhotonicCertificates.v` checks the retained photonic witnesses. With `cd_core` the off-block
entries of `L_(e3+e10)` vanish exactly at D = 16, 32 and 64 and the block ranks sum to rank `L_a` (12/16, 24/32,
48/64). The 84/84 box-kite program uses this collapse: 32 one-photon configurations, each a four-mode Halmos dilation
exact over Q(sqrt 2), carry all 336, 5040 and 52080 signed two-label zero products at D = 16, 32 and 64
([strategy section 8](../../notes/quandela/strategy.md#8-the-8484-box-kite-program),
`docs/evidence/box_kite_census/two_blade_blocks.json`). A two-label 32- or 64-dimensional zero product therefore runs
on Ascella and Belenos today, three Ascella blocks or six Belenos blocks per setting.

**The fold fails for dense operands.** An operand whose support differences span the whole cube is one block of size
D. A one-photon encoding carries one photon over the modes, so it needs D modes, and a non-orthogonal L_a beyond the
octonions needs a dilation besides (the program's one-hot D = 32 encoding needs 34 modes). Moreno's H-blocks
(`C1548_MorVlambdaHBlock.v`) split a sedenion kernel into four-dimensional pieces only after an orthogonal change of
basis that itself spans all D modes, and the Schur complement of the doubling formula reduces a rank question to a
16-dimensional operator classically without shortening the interferometer. A multi-photon dual-rail encoding of 32 or
64 dimensions fits 10 or 12 modes but needs postselected entangling gates: Ascella's vendor rate formula gives five photons
about 5 per second (13.33 MHz x 0.0525^5, [platform specifications](../../notes/quandela/platform-specifications.md)),
and each postselected CZ keeps one ninth of what reaches it, so ten gates leave about 1.5e-9 per second; the Belenos
three-photon rehearsal returned no three-click sample in 7.2 million shots.

**What the persistence result adds.** A rank-one block sends its kernel vector to a dark port, so a zero product's
certificate is a dark-port null, and its floor is the mesh's error at that port. On Belenos the 84/84 program's dark
configurations read algebra share 0.048 at seed 0 and move by a median of 0.043 across seeds (dark-11: 0.184, 0.061,
0.017); on Ascella each mesh's dark-port share persists between job-03 and job-08 (r = 0.63) and its X error persists
at 98.8 % of the attenuation ceiling. If Belenos meshes persist as Ascella's do (the
[Belenos persistence case](../../design/belenos-mesh-persistence-case.md) tests it), a measured table over a few seeds
per configuration lets each of the 32 configurations run on its lowest-error seed and subtract its persistent offset,
which on Ascella cut the per-mesh variance 10.4-fold on a run the frozen table never saw (job-09). The algebra also supplies its own replicates: the
thousands of zero products that share one configuration have the same ideal, so they calibrate the hardware rather
than adding unknowns. The higher algebras therefore improve accuracy through block folding, built-in replication and
seed selection; they leave the chip's per-mesh error itself unchanged.
