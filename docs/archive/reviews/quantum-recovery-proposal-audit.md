# Audit of the nonlocal-transport and quantum-recovery proposal against the repository

The proposal package `Quantum_Recovery_Proposal_and_Poster_Specification_20260908.zip`
(SHA-256 `52597ff29c4003daa2e59cae3c988c98351640ee8d175af9e4b9d30756a73fb4`, 15 files,
research cutoff 2026-09-08) is a six-page acmart manuscript, "Nonlocal Transport and
Latency-Constrained Quantum Recovery", with a poster brief and an evidence directory. The
package stays outside the tree; its own `SHA256SUMS.json` binds each member. This audit read
origin/main at `d53a2fe` on 2026-10-25 and checked the proposal's computational claims against
`gororoba_quantum/cd_core.py`, the retained hardware records and the proposal's cited dataset.

The proposal's Python scripts (`resolution_tests.py`, `additional_tests.py`) ran in an
external sandbox. A search of `/home` and `/tmp` and of the local open_gororoba checkout finds
neither file, so every number below comes from an independent implementation:
[replay.py](../../evidence/quantum-recovery-proposal-audit/replay.py), output
[result.json](../../evidence/quantum-recovery-proposal-audit/result.json).

## Computational claims

Each claim the replay checks reproduces. All of them restate known results.

| Claim (proposal) | Proposal value | Independent result | Authority |
|---|---|---|---|
| [[5,1,3]] code corrects every pattern of at most two located erasures | 16 of 32 subsets, max residual 9.10e-16 over 320 random states | Knill-Laflamme deviation at most 6.2e-17 on all 16 subsets; at least 0.0625 on every subset of three or more | Exhaustive Knill-Laflamme check, which implies recovery of every logical state |
| Regions {0,1,2} and {2,3,4} each reconstruct M2; their intersection {2} reconstructs only scalars | stated | Both regions are complements of a two-qubit erasure that passes the Knill-Laflamme row above; on {2} the reductions of the logical Pauli eigenstates coincide (trace distance 5.6e-17) | Knill-Laflamme row; the single-qubit reductions |
| M/G/1 useful-rate optimum `lambda* = 1/(m(1+sqrt(1-c)))` | 0.6339745962 exponential, 0.6841884324 deterministic, m = 1, delta = 0.5 | 0.6339745962 and 0.6841884324 analytic; grid optimum agrees to 2e-7 | The derivative numerator `1 - 2x + c x^2` checks by hand |
| Pinching leaves `p0(t) = (1 + e^-2t)/2`; coherent `H = X` survival without measurement | 0.5676676416 and 0.2919265817 | 0.5676676416 and 0.2919265817 | Closed forms |
| Sedenion zero divisor `(e1 + e10)(e4 - e15) = 0` | stated | zero vector under `cd_core.cd_multiply_exact` | cd_core sign convention |
| A sedenion Jordan-identity residual `-e3/2` at indices (0,1,3); the audit reads this as the Hermitian 3x3 algebra H3 over the sedenions, since the proposal names no matrices | -1/2 | Exact witness: off-diagonal units (e15, e15, e14) and (e15, e15, e5) give residual `+-e10/2` at entries (0,1) and (0,2); no failure over 4000 octonion pairs | The exact rational witness itself; the octonion pass matches the exceptional Jordan algebra of the [Baez survey](../../notes/papers/math-0105155.md) |

The magnitude 1/2 and the sedenion-only failure agree with the proposal. The H3 statement
differs from the Jordan square-preservation defect in `gororoba_quantum/claim_boundaries.py`,
which concerns left multiplication, and CLAIM_BOUNDARIES.md already scopes the Albert algebra
out of every circuit design.

Not run, because no repository observable or provider measurement corresponds to them: the
half-Caputo CP-divisibility ratios, the joint quantum-classical controller trace, stationary
and relative-entropy residuals, the Lyapunov and switching-system radii, the thermal entropy
values, the logical-operator intertwining residual and the fractional-Laplacian quadrature
bound.

## Overlap with retained repository evidence

- **The proposal's zero divisor already ran on hardware.** `(e1 + e10)(e4 - e15)` is the
  dark witness of the
  [Algebra Circuit Design Rules](../../notes/algebra_circuit_rules.md), with
  `(e1 + e10)(e4 + e15)` as its bright control. The zero-divisor fringe on ibm_kingston
  (2026-10-15, job `db87o8or1c5c738lu910`,
  [findings](../../../results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md)) reads dark 0.182
  against bright 0.828. The excess floor is incoherent device noise, at 2.2 times the
  calibrated model.
- **On ibm_fez qubit 143 the measured delay law is a beat, not an exponential.** The proposal
  says a measured fidelity-versus-delay law must replace its `e^(-delta T)` reward before
  device-specific use. [N21_ORBIT_RCA.md](../../../results/live/N21_ORBIT_RCA.md) records qubit
  143 losing Ramsey visibility from 0.994 at zero delay to 0.611 across one 836 dt (3.344 us)
  idle, the length of a measure plus reset with nothing measured. The calibration noise model
  predicts 0.993, a loss of a few percent from the reported echo T2. The executed coprime-swap
  sweep ([N21_Q143_COPRIME_SWAP_CASE.md](../../../results/live/N21_Q143_COPRIME_SWAP_CASE.md),
  job `dbc40u8c77vs7385ee0g`) resolves the law as two frequency lines, 90.2 kHz apart with
  weights 0.529 and 0.471 and fixed within each shot, under a slow decay (fitted T2* 152 us).
  Visibility therefore beats with a period near 11 us, and no exponential reward describes
  that qubit. Confidence that a beat-type law holds beyond qubit 143 is low: the qubit was
  selected as anomalous, and marrakesh qubit 47 carries a second-line weight of only 0.105.
  The repository's next step on this law is the parity-resolved readout that case names.
- **Feed-forward cost is a scheduler surplus, with no measured service-time distribution.**
  Retained ibm_kingston jobs give a scheduler duration equal to the Target bound plus 2246 dt,
  plus 133 dt (532 ns) per feed-forward stage
  ([case addendum](../../../results/live/2026-10-17T101105.548987Z/CASE_ADDENDUM.md)). That
  number is a scheduled duration, not a measured physical latency. The
  [readout-resonator note](../../notes/ibm_quantum/heron-r2-readout-resonator.md) records
  an unattributed "approximately 600 ns" for IBM hardware. It also records a 2023-2024 Eagle and
  Falcon stack whose feed-forward time scaled with the number of measured bitstring outcomes,
  tested one by one. Whether the account's Heron r2 stack keeps that scaling is unrecorded. The
  M/G/1 model would need a per-shot distribution of controller service times, and no retained
  record supplies one.
- **Error correction has a three-qubit reference only.** The
  [hypercomplex operator evidence](../../design/hypercomplex-operator-evidence.md) checks the
  Knill-Laflamme condition for the three-qubit repetition code. The conjecture registry rows
  `error-correcting-embedding` (capability-gated) and `measurement-sequence` (develop) in
  [algebra-device-conjectures-5](../../evidence/algebra-device-conjectures-5/README.md) are the
  homes for the [[5,1,3]] and pinching material.

## Material with no repository link

The fractional graph Laplacian and its GKSL jump realization, the half-Caputo family, the
Lyapunov and switching-system benchmarks, the joint controller generator and the holography
track share no observable with any provider this repository reaches. The proposal names no
measurement for them. The strontium-titanate Pockels reanalysis concerns a cryogenic
electro-optic material that no retained run touches, and the proposal itself states that no
interface connects it to quantum control.

## Materials dataset: corrections for the proposal's author

Zenodo record 15653571 (Anderson et al., Science 390, 394 (2025); arXiv 2502.15164v2) was
fetched on 2026-10-25.

- `Fig4a_pockels.csv` matches the published MD5 `9f29ac811cd48bd68556939497cb4dbe`. The
  record's license field reads `cc-by-4.0`. The proposal lists both as unverified.
- The headline fit reproduces from the full-precision file. Best of a 75-start least-squares
  search: amplitude 1726.74 pm/V, `E_s` 0.09781 MV/m, `E_off` -0.003324 MV/m, RMSE
  13.339 pm/V, R2 0.9815. The five-block holdout reads 19.712 pm/V, against the proposal's
  19.7115.
- The file holds three sweeps, and the proposal fits only the first.

  | Column pair | Points | Field range (MV/m) | Peak | `E_s` (MV/m) | RMSE (pm/V) | R2 | Five-block holdout RMSE |
  |---|---:|---|---|---:|---:|---:|---:|
  | 0 | 51 | -0.2 to 0.2 | 515.9 at 0.080 | 0.0978 | 13.3 | 0.982 | 19.7 |
  | 1 | 201 | -0.2 to 0.2 | 712.3 at 0.036 | 0.0415 | 57.4 | 0.683 | 149.0 |
  | 2 | 102 | 0 to 0.2 | 984.1 at 0.008 | 0.0125 | 16.4 | 0.990 | 188.6 (extrapolation: one-sided sweep) |

  The paper's Fig. 4a caption labels no sweep. Its body text says the bias field of maximum
  nonlinearity falls as the sample approaches criticality, across natural STO, STO-28 and
  STO-33 at 5 K. The falling peak fields therefore map the column pairs to STO, STO-28 and
  STO-33 in that order. Confidence in that mapping is medium: the dataset's own column labels
  or the supplement's sweep table would settle it. Under that mapping, the three-parameter
  Landau magnitude law describes the STO and STO-33 sweeps and misfits STO-28 (R2 0.68 at the
  best of 75 starts). A materials claim built on the single fitted sweep needs that misfit
  reported beside it.
- The `E_s` sign carries no information, because `|r|` depends on `|z|` and `z` is odd in
  the field. The replay reports `|E_s|`.

## Experiment candidates

Two candidates connect the proposal to reachable hardware. Each needs the repository's dry
run, written case and approval before any submission.

1. **Nonselective measurement sequence: the proposal's pinching claim run on a device.**
   - **Circuit.** Prepare `|0>`, apply N steps of `RX(THETA/N)` with THETA = 8 pi/9, each
     followed by a mid-circuit measurement whose outcome is discarded, then read Z after a
     fixed pre-readout idle. THETA/N is a multiple of pi/36 for every N up to 16, so the
     sequence survives Tuna-17's angle grid, which quantizes each rotation to the nearest
     multiple of pi/36
     ([Tuna operational specifics](../../notes/quantum_inspire/site/kbase_tuna-operational-specifics.md)).
     The proposal's 2 rad total fails that grid: RX(1/8) quantizes to pi/36 at N = 16.
   - **Ideal prediction.** Ideal pinching gives `P0 = (1 + cos(THETA/N)^N)/2`: 0.0302,
     0.5151, 0.6722, 0.8040 and 0.8914 for N = 1, 2, 4, 8 and 16.
   - **Arms.** The mutation null is the unitary arm: the N = 16 rotations back to back with
     no mid-circuit operation, ideal `cos(THETA/2)^2 = 0.0302`. A delay of the measurement's
     duration is not an inert null, because idle dephasing during it pinches the qubit too;
     it serves as the elapsed-time control. Arms with `RX(+THETA/N)` and `RX(-THETA/N)` share
     the same ideal value because cosine is even, so they run in the order +, -, -, + to
     balance drift and carry no signed contrast.
   - **What it isolates.** After each measurement the state is diagonal, so a post-readout
     frequency shift acts only while the next rotation pulse is on. A shift delta over a pulse
     of length tau changes that pulse's flip probability at second order in delta tau. With
     tau at most 100 ns and delta at most 2 pi x 100 kHz, delta tau is at most 0.063. The
     exact detuned-rotation flip probability at N = 16 (ideal sin(THETA/32)^2 = 0.0076) then
     moves by -2.5e-6 per step, or -4e-5 summed over the sixteen steps. The retained Tuna-17 tails stay within about 33 kHz
     ([ringdown claims](../../state/RESEARCH_STATE.md)). The sequence therefore reads
     measurement-induced transitions, which the calibration noise model omits because it
     treats a mid-circuit measurement as projective, up to that bound. A departure larger
     than the bound still needs a settle-gap control before it is read as
     measurement-induced: the N = 16 measure arm repeated with an idle longer than the
     resonator ring-down after each measurement. A departure that survives the settle gap
     unchanged excludes a readout tail. The duration-matched delay arm cannot serve as this
     control, because it never drives the resonator. The retained post-readout frequency-tail
     runs on Tuna-17 and the single extra-readout arm on ibm_fez measure phase after one
     readout, not this quantity.
   - **Placement.** This is the `measurement-sequence` row's question, with the
     elapsed-time-matched control that row requires (the delay arm). It needs no feed-forward. Tuna-17 has run
     one mid-circuit readout followed by gates on the same qubit (`readout_ringdown_tuna_17`
     runs). Up to 16 repeated readouts of one qubit there are unverified, so the dry run
     establishes them first.
2. **[[5,1,3]] located-erasure reconstruction.**
   - **Circuit.** Encode the six logical Pauli eigenstates, reset two located qubits, and read
     logical X, Y and Z through weight-3 representatives on the three surviving qubits.
   - **Null arm.** Resetting three qubits leaves the surviving pair with no logical
     information (trace distance 1.0e-16 in the replay).
   - **Placement.** Five data qubits fall under the Kaggle routing rule, so this candidate
     starts as a noise simulation against a Heron r2 snapshot. Hardware follows only if a
     device question emerges, such as reset quality as a located erasure. It extends the
     `error-correcting-embedding` row from the repetition code to a distance-3 code.

The M/G/1 model gets no experiment until a record supplies a per-shot service-time
distribution for the controller.
