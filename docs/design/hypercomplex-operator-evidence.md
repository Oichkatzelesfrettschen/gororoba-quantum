# Hypercomplex operators, falsifiers and device evidence

The programme tests finite algebra and faithful circuit encodings before spending provider resources. Ordinary complex hardware measures implementation conformance and noise. A complex encoding of a quaternion operator reproduces its probabilities and therefore supplies no independent test of a fundamental quaternion scalar field.

## Claims and finite falsifiers

| Symbol or path | Invariant | Consequence | Falsifier and result |
|---|---|---|---|
| `quaternion_matrix` | Products and adjoints agree with quaternion multiplication | Two complex channels encode each quaternion coefficient | The `ij=k`, `ji=-k` tests pass; a component projection changes the experiment |
| Right quaternion module | `L_a(psi*q)=(L_a psi)*q` by associativity | Left multiplication is right-linear | The draft's contrary statement fails directly |
| Anti-Hermitian generator | A fixed chosen scalar imaginary unit need not commute with the generator | Fixed-scalar factorization and an operator-dependent complex structure are distinct questions | `L_j` fails commutation with `L_i`; the symplectic antiunitary condition differs from Hamiltonian time-reversal symmetry |
| `order_interferometer` | Balanced paths retain total norm one | Dark-port probability is `sin(theta)^2 sin(phi)^2` | Two distinct noncommuting phases in an ordered comparison suffice; the draft's three-element minimum fails |
| Paired-channel measurement | Sum adjacent complex probabilities | Global right-quaternion representatives have equal site laws | Resolved channels alone can change under a right-j representative and supply a false anomaly |
| Octonion left operators | Operator composition is associative | The envelope spans `M8(C)` | `L_e1 L_e2 != L_(e1 e2)`; the encoding is linear rather than a product homomorphism |
| e7-aligned ladders | Canonical anticommutation and color-number commutation | Occupation dimensions are 1,3,3,1 | The draft pairing fails 6 of 8 stabilizer commutators in `cd_core`; the generated aligned pairing fails 0 |
| Octonion derivations | Exact derivation span and e7 stabilizer | Dimensions 14 and 8 | The exact replay checks rank, nullspaces and all admitted commutators |
| Imaginary left operators in dimensions 16 and 32 | Candidate Clifford anticommutation | Extending the octonion operator argument requires another construction | The replay counts 84 and 588 failed ordered distinct-generator pairs |
| Even five-mode occupations | `Y=-Nc/3+Nw/2` | Conventional 16-state Spin(10) reference and vanishing anomaly sums | Representation agreement establishes a reference, rather than a unique derivation or measured particle model |

The [source-bound certificate](../evidence/hypercomplex-operators/README.md) records the executable subset. Soler-type field-choice results require their hypotheses; they do not classify every finite operational theory. Kramers symmetry concerns an antiunitary commuting with a Hamiltonian, while quaternionic linear dynamics commute with their quaternionic structure at the unitary level. The distinction matters when multiplication by the chosen complex imaginary unit changes sign under an antiunitary.

The [eight-generator sedenion envelope](../evidence/sedenion-clifford-envelope/README.md) supplies a complementary positive result: `L_e1` through `L_e8` satisfy `Cl(0,8)` and their 256 words span `M16(R)`. The full fifteen-generator failure does not exclude this subset. The operator result supports finite encoding controls while retaining the coefficient algebra limitations.

## Literature corrections

The [source index](../INDEX.md#hypercomplex-operator-audit-sources) binds eight exact versions and their reading scopes. Furey's 2018 EPJC article is **1806.00612**, not 1702.04336. DOI 10.1038/s41598-021-01814-1 names **N. Masi**, rather than Gresnigt. The sister Rust repository repairs those canonical bibliography records and generated mirrors.

Furey and Hughes 2409.17948 proposes a triality-based three-generation construction. Furey 2607.18450v3 explicitly includes a sedenionic embedding; 2505.07923v4 describes a Jordan superalgebra while identifying missing top-quark representations. Gresnigt 2604.24795 introduces Higgs and Yukawa structures with six Higgs doublets. These sources refute blanket claims that later programmes never address generations, dynamics-related structure or sedenions. They leave predictive uniqueness and empirical discrimination as separate obligations.

Fernandez and Schneeberger's ordered-circuit simulation theorem explains the extra complex channel. Moretti and Oppio's reduction requires its relativistic symmetry assumptions. The recent operational-foundations preprint supplies additional claims to check, rather than a proof certificate admitted by retrieval alone.

The [foundational citation review](../notes/papers/quaternionic-foundational-source-review.md) distinguishes verified identities from pending theorem and historical-experiment body readings. The [exact-version optical addendum](../notes/papers/quaternionic-optical-bound-reading.md) records the reported `0.03 degrees` effective-phase bound, Gaussian propagation, an insensitive noncommuting case and the scattering assumptions disputed by Adler and the authors. The Procopio interferometry result constrains a specified optical model. Its reported phase bound cannot become a universal quaternionic coupling bound without the model map and uncertainty treatment. Renou's 2021 Nature article is an independent-source real-versus-complex theoretical discrimination result; experimental realizations require their own citations. Conventional controlled internal operators can produce order sensitivity in complex quantum mechanics, so order sensitivity alone fails as scalar-field discrimination.

## Numerical and transform contracts

`periodic_generator` discretizes `A=L_i*d_xx + g*L_j*cos(x) + (g/2)*L_k*sin(x)` on a periodic grid. The generator is anti-Hermitian. `split_evolve` uses symmetric Fourier/potential splitting without renormalizing numerical errors away. A four-site grid resolves `sin(x)`; `sin(2x)` aliases to zero. The tests compare propagation against a matrix exponential and check norm preservation.

The left-i Fourier transform has two conjugate complex channels. The right-j transform is real-orthogonal on four real coefficients per site; it fails complex linearity relative to right-i. Device cases implement the complex-linear left transform. Identity references are labeled as identities; real and imaginary superposition inputs expose phase-sensitive output laws. A synthesized identity is not evidence of a Fourier round trip.

`dephase_evolve` implements a site-projector GKSL channel and checks Hermiticity, positivity and trace. `shot_diagnostics` reports block variability and lag-one dependence. Neither a finite linear unitary system nor a noisy shot sequence establishes chaos. Lyapunov claims require a defined nonlinear/state-space model, perturbations, scaling ranges and independent controls. The implementation makes no chaos or computational-advantage claim.

## Library admission and device routing

The [distribution inventory](../state/hypercomplex-libraries/libraries.md) explains each declared distribution and considered scientific alternative; its JSON preserves pins, host observations and import locations. The [existing algebra package rules](../notes/algebra_circuit_rules.md) retain every convention map. A package joins algebra evidence only after every basis product matches `cd_core` under its declared signed map. A wrapper shares its engine's independence boundary. Split-signature packages provide negative controls.

Use NumPy/SciPy/SymPy for array, propagation and exact certificates; use qualified hypercomplex libraries for independent arithmetic witnesses. Use Qiskit for native compilation and operator comparison, Perceval for complete photonic mesh checks, and the isolated Quantum Inspire stack for cQASM parsing and local QX semantics. Use mitigation packages for sensitivity analyses with explicit calibration assumptions. Infrastructure dependencies support SDKs and supply no independent mathematical witness.

The repository routes ordinary small circuit simulations through its Kaggle workflow. The finite matrix and algebra checks here are host-side mathematical validation. Provider-backed simulators, emulators, hardware, uploads and notebook sessions follow the written-case rule. IBM's small-device exception requires a question about the device itself; a larger circuit width alone does not create useful physics.

## Execution dependency gates

1. Replay the exact certificate, behavioral tests, full photonic operators and native quantization records.
2. Freeze each provider case and plan digest. Refresh backend availability, coupling, queue, usage and tariff through read-only provider operations.
3. Present the concrete written case, shots, expected seconds, credits and device question for approval.
4. Run an isolated Quantum Inspire pilot with contemporaneous all-zero/all-one readout references. Collect and inspect every batch before the next submission.
5. Qualify disjoint-pair packing against isolated baselines before maximizing concurrent drive. The documented graph and measured crosstalk govern usable placement; a maximum graph matching alone supplies no equivalence certificate. Keep packed execution unadmitted until a paired equivalence case has approved margins and temporal-dependence treatment.
6. Assess the descriptive pilot against the [adversarial admission addendum](tuna-order-pilot-adversarial-admission.md). Wave and transform acquisitions require their own reviewed entry conditions and approved cases. Preserve raw shots and provider identity, refresh the account ledger and research registry in the same evidence change, then render measured probabilities.

The [operator runbook](../runbooks/hypercomplex-operator-cases.md) provides submit-free commands and the approval boundary. The branch implements isolated cases and guard reuse. Packed equivalence measurements and additional provider acquisitions remain contingent on their concrete approved cases.

## Retained Tuna-17 order pilot

The approved order pilot completed eight batches, 24 jobs and 393216 shots on 22 October 2026. The
[retained summary](../../results/quantum_inspire/runs/tuna17-quaternion-order-noise/pilot-summary.json)
binds each batch analysis and the corrected approval digest. The refreshed provider ledger records
186.801814 execution seconds and zero credit debit for the 24 jobs. The observed debit describes
these acquisitions rather than a guaranteed future tariff.

The table reports the grouped dark-port frequency after summing the internal complex encoding
channels. The two phase angles specify the frozen i/j phase settings. The representative is the
identity or global right-j quaternion representative. Every science job contains 16384 shots.

| i phase | j phase | Representative | Native dark probability | Measured dark probability |
|---|---|---|---|---|
| 0 | 0 | identity | 0 | 0.0398559570 |
| 0 | 0 | right-j | 0 | 0.0467529297 |
| 0 | pi/4 | identity | 0 | 0.0396118164 |
| 0 | pi/4 | right-j | 0 | 0.0479125977 |
| pi/4 | 0 | identity | 0 | 0.0408325195 |
| pi/4 | 0 | right-j | 0 | 0.0508422852 |
| pi/4 | pi/4 | identity | 0.25 | 0.2669067383 |
| pi/4 | pi/4 | right-j | 0.25 | 0.2703857422 |

The [measured probability figure](../evidence/hypercomplex-operators/tuna-order-analysis-bound-probabilities.png)
compares the raw frequencies with native predictions; its
[retained producer and replay](../evidence/hypercomplex-operators/README.md) bind the source and rendering.

Every contemporaneous output readout contrast exceeds the preregistered 0.2 acquisition guard;
the observed contrasts range from 0.7619018555 to 0.92578125. The guard establishes acquisition
quality only. The fixed chronological order and one acquisition per science setting leave
preparation, compiled-circuit effects, readout and time-dependent drift confounded. The measured
representative differences establish neither ray invariance nor its violation. The
[admission addendum](tuna-order-pilot-adversarial-admission.md) supplies the inference boundaries;
additional wave, transform, packing or replication acquisitions retain separate approval cases.
