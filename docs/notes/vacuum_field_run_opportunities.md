# Field-model experiments: source support, finite checks, and admission gates

The reviewed proposals contain three different output tasks: characterize a
physical qubit's effective noise, simulate a supplied field Hamiltonian, or
measure physical force/radiation with a calibrated apparatus. A gate experiment
can contribute to the first two. The third requires its own physical coupling,
instrument response and independent calibration. [P] marks a source result;
[I] marks a repository deduction or design; [E] marks retained finite evidence.

## Primary sources and corrected attributions

- [P] [Sabin](1909.04408.md) reports a beam-splitter experiment on IBM Q5
  Tenerife. The paper derives two-mode squeezing and proposes DCE as an
  application; the reported hardware frequencies concern the beam splitter.
- [P] [Samos-Saenz de Buruaga and Sabin](papers/1610.03272.md) study a perturbative
  Gaussian coherence measure. That entropy-based scalar differs from the
  phase-odd real pair correlator proposed here; its thermal and detuning
  assumptions bound the no-threshold statement.
- [P] [Wilson et al.](papers/1105.4714.md) physically modulate a SQUID boundary and
  measure synchronized sideband correlations and two-mode squeezing. Their
  pump-phase-dependent complex correlator supplies direct prior art for phase
  intervention; an encoded qubit correlator has a different physical meaning.
- [P] [Stecenko et al.](papers/2105.02032.md) use an IBM quantum simulator to estimate
  reference-subtracted energies of free lattice fields. The source supplies
  simulation precedent, with explicit classical mode-sum references.
- [P] [Schoelkopf et al.](cond-mat-0210247.md) and
  [Clerk et al.](0810.4729.md) relate transition rates to unsymmetrized noise
  under weak-coupling/stationarity assumptions. The notes reconcile the
  inconsistent sign table in the former against both papers' equations.
- [P] [Jin et al.](1412.2772.md) measure residual excited-state population
  using additional transmon-level control/readout. That capability and
  calibration differ from a binary gate-and-delay experiment.
- [P] [Bartlett et al.](papers/quant-ph-0109047.md) delimit efficient Gaussian
  simulation for the stated preparations, operations and quadrature
  measurements. [Collision models](2106.11974.md) distinguish fresh bath
  inputs, reset replacement channels and correlated repeated interactions.
- [P] [Circuit QED](papers/2005.12667.md) is RMP 93, 025005; it is a circuit-QED
  review. The [real-material Casimir review](papers/0902.4022.md) is RMP 81, 1827.
  Their models and physical measurement surfaces remain distinct.

## Retained finite reference

[E] The [CPU replay bundle](../evidence/vacuum_models/README.md) records the
proposal identities, explicit finite Hamiltonians, model checks and numerical
tolerances. Independent review reconstructed the cutoff-4 and cutoff-8
intertwining and evolution. The numerical replay establishes these finite
cases; an arbitrary-cutoff theorem needs the additional proof below.

[I] Let `V|n>=|n,n>` and let `B` be the truncated pair-lowering operator.
On the equal-occupation sector, `B|n>=n|n-1>`. For
`H_phi/(hbar*g)=i(exp(i*phi)*B^dagger-exp(-i*phi)*B)`, the finite certificate
checks `H_full V=V H_red` and the compressed observables. In the cutoff-4,
`q1q0` convention, the replay obtains

```text
H_0/(hbar*g) = 2 IY - XY + YX - ZY
Re(ab)       = IX + (XX + YY - ZX)/2
n            = 1.5 I - ZI - 0.5 IZ.
```

[E] The [endpoint information replay](../evidence/vacuum_endpoint_information/README.md)
compares eight ideal cutoff-four arms and 72 product-measurement laws with
288000 shots per design. Four settings `ZZ, ZX, XX, YY` recover populations and
real pair coherence; the recorded nine-over-four real-coherence variance ratios
are 2.215418 at `r=0.2` and 2.160225 at `r=0.4`. Physical imaginary-coherence
witnesses remain invisible to those four settings; adding XY alone still leaves
YX blind. The unique product-Pauli cover for full populations and both pair
quadratures is `ZZ, ZX, XX, YY, XY, YX, ZY`; state tomography uses all nine.
The replay retains same-shot covariance, declares cross-arm independence, and
keeps Neyman allocation conditional on known finite-state variances. These
finite ideal-readout results supply zero hardware-optimum, billing or submission
authority. State tomography differs from process or instrument tomography.

[E] At cutoff four, relative real-coherence error against the infinite
squeezed-vacuum reference is approximately 0.01367%, 0.71530% and 5.86524%
for `r=0.2,0.4,0.6`. At `r=0.4,0.6`, the single-mode commutator expectation
deviates from one by approximately 1.3081% and 11.2094%. Occupation-tail mass
alone therefore cannot qualify every observable. The finite ladder obeys
`[a_d,a_d^dagger]=I-d|d-1><d-1|`, whose trace is zero.

[E] One first-order product-formula step at `r=0.4` has operator-norm error
approximately 0.4445; eight steps give 0.05385 in the recorded order. Circuit
compression and fractional gates require a separately qualified approximation
or exact synthesis. A correct Pauli decomposition alone proves neither.

## Source-to-experiment opportunities

All rows are prospective design opportunities. The existing correction/ripple/
rank campaign retains its own source, approval and budget record. These rows
supply zero additional submission authority.

| Observable and supplied model | Primary support / independent reference | Controls and assumptions | Whole-workload cost and falsifier | Readiness and next gate |
| --- | --- | --- | --- | --- |
| Phase-odd `Re<ab>` under the equal-occupation pair Hamiltonian | Sabin squeezing construction; Wilson phase correlations; finite full/reduced replay and infinite Gaussian reference | Zero coupling, both phases, occupation-matched diagonal mixture, first-moment checks, full-encoding reference; declare sector invariance and omitted loss channels | Price four endpoint settings, phase/control arms, replicas and covariance together; reject incorrect observable pullback or a model-bias envelope exceeding tolerance | CPU reference retained; qualify compiled unitary, shot precision and model cutoff before a hardware case |
| Cutoff convergence of coherence, occupations and commutator | Finite ladder identity and exact finite evolution | Compare cutoffs and interaction strengths against a declared observable tolerance; separate cutoff, synthesis and device errors | Include additional encodings/settings in the cost; reject an accepted cutoff when any preregistered bias exceeds its tolerance | Finite reference retained; select target tolerance and synthesis independently |
| Fractional versus conventional synthesis of the same finite unitary | [IBM source note](papers/ibm_fractional_execution_sources.md); exact matrix reference | Same Hamiltonian/time, matched patch, routed controls, valid bound RZZ angles, client compatibility, verified global/relative phases | Price routing, reset, measurement, controls and job splits; compare returned usage and endpoint error; gate count alone is insufficient | Public policy checked; live Target, installed-client and full-unitary qualification required |
| Packed-minus-isolated endpoint distortion | [Parallelism](quantum_experiment_parallelism.md), [crosstalk](papers/1908.09855.md), [drift](papers/1907.13608.md) | Fix focal circuit; rotate companion, patch and time conditions; preserve joint shots and sparse references | Price fused critical path plus all controls; declare a distortion margin and covariance model; reject precision or equivalence failure | Design precedent exists; new family requires its own compiled and costed matched design |
| Excitation/relaxation rates and effective residual populations | Schoelkopf/Clerk spectral equations; Jin calibration constraints; finite SPAM counterexample | Independent preparation/readout constraints, declared delays, stationarity/drift checks, leakage model; thermodynamic temperature needs equilibrium assumptions | Long delays, calibration shots and context controls count; reject vacuum isolation or absolute rates when nuisance parameters remain unidentifiable | Source and counterexample retained; establish calibration identifiability before Fisher/shot allocation |
| Fresh versus reused bath collision channel | Collision review Eq. 4.7; finite exchange-channel reference | Correct diagonal mixed preparation, fresh independent bath per collision, matched reset schedules; retain joint-record scope | Price randomization/purification, reset and width separately; coherent RY preparation or shared hidden bath correlations falsify the intended mixture model | Small CPU law retained; certify the complete channel and implementation controls |
| Encoded force derivative or constructed rank-spectrum susceptibility | Real-material review; free-lattice Casimir source; sister-project model contracts | Specify self-adjoint Hamiltonian, Hilbert space, Gram convention, multiplicities, units, regulator, reference energy, length map and parameter-dependent encoding | Price preparation/synthesis/observable estimation and classical baseline; omitted identity/reference/basis derivatives or uncalibrated physical map reject the interpretation | Model-only opportunity; no physical force/radiation calibration established |
| Two-qubit quantum energy teleportation: Bob's local energy drop after Alice's X measurement | [Hotta](papers/1002.0200.md) minimal model; [Ikeda](papers/2301.02666.md) IBM hardware precedent; exact reference [scripts/qet_two_qubit_reference.py](../../scripts/qet_two_qubit_reference.py) (E_A = h^2/r, E_B = sqrt(h^2+4k^2) - (h^2+2k^2)/r) | Ground-state reference, measurement only, correct feedback, randomized feedback, fixed rotation, sign-reversed feedback, product-state reference; Z_A, Z_B and X_A X_B from calibrated settings | Price every arm and setting; reject when the information excess (feedback L against the Kabsch minimum over record-independent unitaries, [qet_passivity_controls.py](../../scripts/qet_passivity_controls.py)) is at most zero; a drop from the run's own reference is confounded by phase error; a failure characterizes the device, not field theory | Exact reference and passivity controls tested; arms and shot count in [pais-claims-falsification.md](topics/pais-claims-falsification.md#falsification-experiments); no case written and no QPU time assigned |

[I] For paired rate curves the observable model is
`p_obs(t)=r0+(1-r0-r1)[p_eq+(p_init-p_eq)exp(-Gamma*t)]`.
The [CPU counterexample](../evidence/vacuum_models/README.md) exhibits distinct
physical readout/preparation/equilibrium choices with identical observed
curves. More shots reduce sampling error around the same nonidentifiability.
An independently constrained calibration model must remove that ambiguity
before interpreting `Gamma_up/Gamma_down` as a thermal relation.

[I] Derived endpoints from the same shots share covariance. Fisher information
must remove gauge/nuisance degeneracies, and fixed-sample bounds require their
fixed design. [Time-uniform inference](papers/1810.08240.md) requires its own filtration,
conditional-mean, multiplicity and stopping contracts. A statistical early stop
cannot refund shots already acquired in a submitted job.

## Relation to the three existing QPU jobs

[E] Three jobs occupy two retained campaign directories:

| Job / campaign evidence | PUBs and shots | Final charge | Applicable conclusion |
| --- | --- | --- | --- |
| `db5qmqclf4us73c4e1ug`, [first adjudication](../../results/live/2026-10-11T152922.787095Z/ADJUDICATION.md) | 6 x 4096 | 9 s | Folded-QPE discrepancy, arithmetic/decoder behavior and matched-layout packing in that circuit/calibration |
| `db67fqsvf2bc73d0pk4g`, [later dynamic campaign](../../results/live/2026-10-12T055624.091217Z/ANALYSIS.md) | 12 x 8192 | 29 s | Label-specific dynamic intervention distributions |
| `db67frimb58s738bci4g`, [matched static controls](../../results/live/2026-10-12T055624.091217Z/ANALYSIS.md) | 4 x 8192 | 11 s | Static coherent comparison within the later campaign |

The retained total is 22 PUBs, 155648 PUB-shots and 49 charged QPU seconds.
Each campaign preserves its raw registers, metrics, record and QPY. The later
dynamic/static pair shares its declared calibration and design; the earlier
campaign has different circuits, shots and acquisition context. Pooling them
requires an endpoint and comparability argument. The hardware already supplies
model residuals and layout/schedule evidence. Those QPE jobs contain neither
the proposed field-model observable nor a calibrated vacuum-noise isolation
experiment, so the source intake supplies future designs rather than a new
physical interpretation of their outcomes.

## Formal work and next research decisions

[I] An arbitrary-cutoff Rocq development can prove the finite embedding isometry,
intertwining and observable compression, then lift polynomial identities to
finite evolution with its analytic assumptions. It must separately characterize
which noise channels preserve the equal-occupation sector. This reduction
preserves a specified invariant Hamiltonian and observable; it differs from a
multiplication-preserving quotient of the Cayley-Dickson algebra. The existing
[folding obstruction](open_gororoba_folding_proofs.md) therefore motivates an
explicit preservation theorem for each reduction, rather than blanket trust
in a smaller encoding.

[I] For force derivatives retain parameter-dependent identity offsets,
reference energies, scale factors and basis/encoding derivatives. At finite
temperature use the appropriate free-energy derivative. The sister-project
`casimir_optics_discrimination_contract.md` and `physical_jacobian.tsv` provide
model/discrimination inputs; their hypothetical pressure noise and identity
calibration remain hypothetical. Analytic scaling or worldline finiteness
alone cannot establish Monte Carlo agreement or physical Drude/plasma
validation. A selected acquisition schedule and physical calibration remain
separate missing inputs in that project.

[I] Further broad source collection is unnecessary for the first finite pair
model. The immediate gates are model/synthesis qualification, identifiable
calibration and a complete precision/cost design. More targeted literature is
needed if the project adopts non-Gaussian/interacting targets, claims optical
nonclassicality beyond a declared mixture alternative, or builds a physical
force/radiation apparatus. Cheap finite, covariance and mode-sum references
remain mandatory baselines; non-Clifford gates alone establish no advantage.

## Dark-sector and negative-energy claims

[I] A dark-sector or vacuum-energy reading of any residual names its field
content and coupling (scalar, pseudoscalar or kinetically mixed vector),
compares the claimed region with current exclusions ([ALPS II](papers/2512.14110.md),
[Dark SRF](papers/2510.02427.md), [dielectric haloscope](papers/2503.23354.md), the
symmetron force sensor in
[casimir-dark-sector-web-sources.md](papers/casimir-dark-sector-web-sources.md)),
and models the conventional nuisances those searches fit, such as resonator
frequency instability and Newtonian source gravity
([2511.09750](papers/2511.09750.md)). A QPU circuit residual has no physical
dark-sector source and stays a device-model discrepancy until an external,
separately predicted dependence appears. Negative local energy in a
boundary geometry or a QET protocol leaves total energy at or above the
ground state; [Ford and Roman](papers/gr-qc-9607003.md) bound free-field sampling,
and a cavity needs its own boundary-adapted inequality. Casimir residuals
first face the Drude-plasma discriminators of [Ma et al.](papers/2601.00483.md) and
Inacio et al. (web-source note) before any new-force attribution. The
gororoba-open vacuum-model code checks live in
[open_gororoba_handoff.md](topics/open_gororoba_handoff.md#vacuum-model-code-checks).
