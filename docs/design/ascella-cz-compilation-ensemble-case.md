# Ascella postselected CZ: compilation ensemble with interleaved anchors

Status: proposed design. No builder, frozen request or forecast exists, nothing has been sent, and each job waits
for the owner's approval of a written case built from this design.

## What the experiment asks

The [process tomography case](ascella-cz-process-tomography-case.md) asked how well qpu:ascella performs a
controlled-Z gate between two photonic qubits and returned an exploratory score of 0.849 (claim
`qd-ascella-postselected-cz-process-fidelity`). The score stays exploratory for three reasons, and this design
measures each one.

| Open question | Why the tomography case leaves it open | What this design measures |
|---|---|---|
| Does the gate depend on which compiled mesh serves it, and by how much? | Each of the 144 settings ran once, on its own mesh, so mesh-to-mesh differences and setting-to-setting differences are one quantity. | Each setting runs under 10 compilation seeds; the spread between seeds is the mesh variance. |
| Did the device hold still between the two jobs and inside each job? | No setting appears in both jobs. | Four anchor settings repeat at five positions in each job on byte-identical meshes. |
| Is the chance of registering a click the same for every setting? | The fit divides by `nb_shots_used` and assumes it. | Each setting's eligible fraction against its table's mean, a preregistered condition of the bound below. |

## Why one mesh cannot carry the whole measurement

A common mesh for all settings does not exist on this service, by two measured facts in
[strategy.md](../notes/quandela/strategy.md) section 7 ("Per-seed mesh variance of a share"):

- The service compiles every iteration again. The compiled mesh is a function of the iteration's circuit
  parameters and its `compilation_seed`, so two settings with different preparation or readout rotations always
  receive different meshes.
- The same parameters under the same seed return the same `computed_circuit` byte for byte, inside a job and across
  jobs minutes apart, while distinct seeds of one circuit return distinct meshes whose observables differ far beyond
  binomial error.

The second fact gives the two tools of this design. Replicate seeds of one setting sample the ensemble of meshes that
can serve it, which is rule 1 of that section ("run replicate seeds of the identical circuit in the same job, and
pool their spread"). A repeat of one setting under one seed returns the identical mesh, so any change in its counts
is drift or shot noise, which is rule 2 ("keep repeats of one seed as the drift reference").

## Observable: two complementary truth tables

Full tomography under ten seeds would need 1440 iterations. The design measures the gate through two truth tables
instead (H. F. Hofmann, "Complementary Classical Fidelities as an Efficient Criterion for the Evaluation of
Experimentally Realized Quantum Operations", Physical Review Letters 94, 160504 (2005),
[doi:10.1103/PhysRevLett.94.160504](https://doi.org/10.1103/PhysRevLett.94.160504)).

- **ZX table.** Control in the Z basis, target in the X basis. The ideal CZ maps |0,+> to |0,+>, |0,-> to |0,->,
  |1,+> to |1,-> and |1,-> to |1,+>. Four inputs, each read in the ZX basis.
- **XZ table.** Control in the X basis, target in the Z basis, the same four maps with the roles exchanged. Four
  inputs, each read in the XZ basis.

Each of the eight settings is one 6 x 6 unitary on chip modes 0 to 5, built as in the tomography case (readout
rotations after the CZ after the preparations), with the photons on chip modes 0 and 2 and the same eligibility rule:
exactly two threshold clicks, one on each rail pair.

For one setting, the classical fidelity is the eligible events on the ideal output over all eligible events of that
setting. F_ZX and F_XZ are the means of that ratio over the four inputs of each table, and these two descriptive
scores are the case's result. Hofmann's result bounds the process fidelity F of one fixed process by

    F_ZX + F_XZ - 1 <= F <= min(F_ZX, F_XZ),

with the two tables read in mutually unbiased product bases. The scores reach that bound only through two conditions
the hardware does not guarantee, so the analysis tests both and reports the bound only when both hold:

- **One process for every setting.** Each setting compiles its own mesh, so the ZX and XZ settings can be served by
  different processes. A device that serves CZ·Z_control to every ZX setting and CZ·Z_target to every XZ setting
  scores 1 on both tables and stays stable at every anchor, while both processes and their mixture have process
  fidelity 0 to CZ.
- **A success probability independent of the input.** The ratio of one setting cancels that setting's chance of an
  eligible event, but a chance that differs between inputs makes the conditional map nonlinear and voids the bound.
  The Kraus operator (CZ / 3) diag(1, 0.1, 0.1, 0.1) scores 0.7995 on both tables, which would give a lower bound of
  0.599, while its trace-normalized process fidelity is 0.410.

## Schedule

Two jobs of 60 template iterations each, about 180 s at the measured 3.0 s per iteration on qpu:ascella
([quandela-credit-optimization.md](../runbooks/quandela-credit-optimization.md), "What bounds packing"), inside the
300 s `max_duration`.

| Block | Per job | Content |
|---|---|---|
| Ensemble | 40 iterations | the 8 settings, each under 5 compilation seeds; job-01 uses 5 further seeds, so each setting has 10 |
| Anchors | 20 iterations | 4 anchor settings (|0,+> and |1,-> of the ZX table, |+,0> and |-,1> of the XZ table), each under one fixed seed, repeated at 5 positions |

- The anchors use the same four seeds in both jobs, so all ten repeats of an anchor request one mesh.
- The five anchor positions divide a job into four equal ensemble segments; the anchor block sits at iterations
  0 to 3, 14 to 17, 28 to 31, 42 to 45 and 56 to 59.
- Inside each segment the ensemble order is a draw from the case's ANU QRNG record, balanced so every setting
  appears in every pair of adjacent segments.
- All 84 compilation seeds (80 ensemble, 4 anchor) and the order draw come from one ANU QRNG draw that the case owns
  whole in the seed ledger.
- Each iteration takes 4000 samples, as in the tomography case; the builder sets `max_shots` from Perceval's
  estimate with the same 1.25 margin. Each job is billed 1 credit plus one millionth of a credit per billed shot;
  the tomography jobs under the same sample count were charged 1.4 and 2.6 credits, so the case states a ceiling of
  6 credits for both jobs and the plan re-reads the price.

## Preregistered analysis

Preconditions, each a refusal when it fails:

- Each run's `cases.json` matches the retained manifest digest, its `job_id` matches its submission, and its raw
  result matches `result_sha256`.
- Every iteration echoes its `compilation_seed` and `circuit_params`.
- The ten repeats of each anchor return one `computed_circuit` digest. An anchor with two digests is reported and
  leaves the drift test.
- An iteration with fewer than 200 eligible events is uncounted, and a setting with fewer than 8 counted seeds makes
  the case undecided.

Estimates:

1. **Drift and job effect.** For each anchor, a chi-square test of its ten outcome tables against their pooled
   table, split into a within-job part (position) and a between-job part. The case pools the two jobs only when the
   between-job part of every anchor passes at the 0.01 level after a Bonferroni factor of 4.
2. **Mesh variance.** For each setting, the between-seed variance of its classical fidelity minus the binomial
   variance at its event count, floored at zero, with the anchors' repeat variance as the measured check of the
   binomial term.
3. **Fidelities.** F_ZX and F_XZ as the mean over inputs of the per-setting mean over seeds. The interval is a
   Student-t interval over the 10 seed-level table means (one mean of four inputs per seed index, 9 degrees of
   freedom), so it carries mesh variance and shot noise together.
4. **Bound conditions.** Input independence: for every setting, the 95 % interval of its eligible events per shot
   divided by its table's mean lies inside [0.9, 1.1]. One process: for every setting, the nominal unitary of each
   served mesh, with the designed preparation and readout rotations removed, equals the nominal two-photon gate of
   every other setting within the tolerance the no-hardware calculation below fixes before the data. Each condition
   is reported with its measured values whether it holds or fails.
5. **Bound.** When both conditions hold, the case reports [L, U] with L the 95 % lower limit of F_ZX + F_XZ - 1
   and U the 95 % upper limit of min(F_ZX, F_XZ), conditional on the hypothesis that physical error, which the
   nominal unitaries do not see, is the same across settings. When either fails, the case reports F_ZX and F_XZ
   with their intervals alone and no bound.

Readings fixed before the data:

| Outcome | Reading |
|---|---|
| A bound condition fails | The truth-table scores are descriptive; no bound is reported and 0.849 is compared with neither score. |
| The exploratory 0.849 lies inside [L, U] | The tomography score is compatible with the ensemble; the bound is the result that can be established. |
| 0.849 lies above U | The single-compilation tomography fit overstated the gate, by mesh selection or by its loss assumption. |
| 0.849 lies below L | The 144-mesh fit understated the gate, which the non-positive Choi matrix of that fit already suggests. |
| Mesh variance exceeds the binomial variance in more than half of the settings | The tomography interval, which covers shot noise only, is too narrow, whatever the bound reads. |
| A between-job anchor test fails | The jobs are reported separately and no pooled bound is claimed. |

## What needs no hardware

The retained tomography runs return the `computed_circuit` of all 144 iterations. Decoding each mesh and computing
its nominal unitary gives the designed-against-served law of every setting, as the Belenos suppression-law analysis
did for its eight meshes. That calculation separates the transpiler's nominal error from the physical phase error of
the chip, costs no credit, and runs before the case is built: a nominal spread that already explains the
non-positive fit changes the seed count this design needs. The spread of the nominal two-photon gate across the
144 retained meshes also fixes the tolerance of the one-process condition before any new data exist.

## Limits

- The input-independence condition divides by the shot count, the quantity the tomography fit assumed equal across
  settings; a click probability that varies with the setting for reasons other than the input therefore reads as a
  failed condition and withholds the bound.
- The one-process condition checks the nominal unitaries only. Physical phase error that differs between meshes
  passes it, so a reported bound stays conditional on that hypothesis.
- Ten seeds sample the mesh ensemble thinly; the Student-t interval states that honestly and a wide interval is a
  valid outcome.
- The truth tables bound the process fidelity only under the two conditions and give no Choi matrix. A full
  reconstruction under an ensemble needs the 1440 iterations this design declines.
- The anchors test drift over about 180 s and across one gap between jobs, the time scales of this case only.
- hypothesis: preparation and readout rotations contribute comparable mesh error to the gate itself; each compiled
  mesh carries all three, and no setting of this design separates them.

## Before a submission

1. Run the no-hardware served-mesh calculation on the retained tomography runs and record it.
2. Build the case script with `--build`, `--check`, `--forecast` and `--analyze`, its tests, and the frozen
   requests; draw the seeds; forecast both tables under Perceval's noise model at the live HOM and g2.
3. Register Hofmann 2005 as a retrieval receipt in the source registry.
4. Review the written case adversarially, then ask the owner for approval of the two jobs.
