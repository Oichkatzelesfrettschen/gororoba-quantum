# Proof and experiment dependencies after the source audit

The source library now connects algebraic classification, circuit correctness,
statistical decisions and hardware observations to separate checkable claims.
A primary source supplies a method or theorem under its hypotheses. A retained
PDF, numerical replay or successful kernel check establishes a different
boundary. The [formal plan](formal_evidence_dependencies.md) owns the existing
proof obligations; this note supplies the additional source-to-artifact map.

## Geometry: quadratic compatibility and actual curves

[BCDI II](math-0702075.md), Theorem 7.5 and Remark 7.6, gives an S5-bundle over
V2(R7). Independent positive scaling of the two bracket entries supplies an
explicit length-ratio parameter: the fixed-norm family has dimension seventeen.
The expanded source note provides its inverse and places the selected center
in the family. The length ratio is a deduction from published results, not a
new unknown parameter.

The selected-center quadratic compatibility calculation distinguishes pieces
of dimensions seventeen and fifteen, meeting in dimension thirteen. An outer
quadratic constraint and a family of actual curves have different proof roles.
[Coste](coste-semialgebraic-geometry.md) and [Basu--Roy](1803.00505.md) require
actual closure membership before curve selection; a quadratic-compatible
vector alone supplies insufficient input. [Greenberg](papers/greenberg-henselian-lifting.md)
requires a Henselian discrete valuation ring and ideal-dependent approximation
precision. Its lifting theorem cannot turn arbitrary order-two data into an
exact solution. A real tangent direction may require ramification
`x(s)=x0+s^q*h+...`; demanding a nonzero first derivative is stronger.

The mathematics-owned selected-center construction establishes the Bouligand
cone `A15 union B17` at `e1+e18` on the doubly-pure dimension-32,
norm-squared-two nullity-twelve locus, with intersection dimension thirteen. A four-parameter exact slice
supplies the directions beyond an eleven-dimensional octonion-automorphism
orbit; the published bundle and length ratio realize B17. The nonlinear cone
rules out C1 embedded-manifold structure at that center. The owning
[proof note](nullity_twelve_local_geometry.md) and
[replay](../evidence/nullity_twelve_locus/README.md) carry the coefficient
identities, actual curves, equivariance and domain checks. Exact CPU
certificates and written arguments establish the result; Rocq formalization
remains a separate proof obligation.
A selected-center cone equality still leaves neighborhood parametrizations,
local links and attachments, other centers and the global rank-stratum
classification as separate problems. The
[rank-stratum decomposition](koebisu_rank_stratum_research.md) retains those
larger questions.

## Rocq: useful statements and trusted boundaries

| Candidate theorem / artifact | Relevant source | Required bridge and falsifier |
| --- | --- | --- |
| Exact rank at a rational/algebraic point | [MathComp / CoqEAL](papers/mathcomp-coqeal-matrix-certificates.md) | Lower witness `M*A*N=I_r` and upper factorization `A=B*C`; use correct field and dimensions. `kermx` is a left kernel, whereas repository annihilator vectors use the right/column convention |
| [Selected-center cone and curve certificate](nullity_twelve_local_geometry.md) | Same matrix libraries; curve-selection sources above | Prove determinant/pivot domain, cleared denominator signs and exact polynomial identities; finite evaluations cannot replace all-real coefficient equality |
| Ideal controlled circuit and arithmetic | [SQIR / VOQC](papers/sqir-voqc-proof-interfaces.md) | Bit/basis order, ancilla cleanup, exact relative phase, parser/translation and output decoder; up-to-global-phase optimizer equivalence needs a controlled-context bridge |
| Dynamic program with retained outcomes | SQIR density semantics; [QILGST](papers/2103.03008.md) | Outcome-indexed instrument maps or explicit classical registers; unconditional branch-summed equality can hide a wrong joint record |
| Numeric interval decision from retained counts | [CoqInterval](papers/coqinterval-certified-enclosures.md) | Rational inputs, enclosure/domain proofs, source-bound count certificate; a correct interval evaluator alone supplies no coverage theorem |
| Fixed or sequential confidence decision | [Howard et al.](papers/1810.08240.md) | Sampling model, estimand, filtration, family/tail allocation and stopping rule; an observed count theorem is conditional on these statistical assumptions |
| Faithful reduced field model | [Finite CPU evidence](../evidence/vacuum_models/README.md), [Gaussian](papers/quant-ph-0109047.md), [collision](2106.11974.md) sources | Isometry, invariant subspace, observable/channel pullback, cutoff and synthesis errors; preserve the declared information, including joint records when used |

The retained upstream archives are original licensed source snapshots. Their
named declarations were inspected; joint build compatibility with the pinned
Rocq environment remains untested. Adoption requires a pinned dependency set,
compile/kernel replay, `Print Assumptions`, source/generator hashes and a
translation or independently checked certificate from repository inputs.
The replay toolchain should also pin formatter versions: a formatter change
can alter certificate-source bytes and requires coordinated regeneration of
dependent source hashes even when the mathematical semantics agree.
Physical stationarity, calibrated POVMs and noise laws remain stated empirical
assumptions; a proof assistant cannot infer them from a finite shot file.

## Tomography, stopping and allocation

[GST](papers/2009.07301.md) exposes gate-set gauge freedom and SPAM ambiguity.
[Instrument GST](papers/2103.03008.md) retains outcome-conditioned operations; its
reported reconstruction was trace-preserving but lacked a CP constraint.
The relevant target determines which state, process, gate-set or instrument
parameters need identification. Two known-label correction witnesses provide
bounded endpoint evidence rather than complete instrument tomography.

[Optimal-design theory](papers/quant-ph-0411093.md) gives local, model-dependent
Fisher criteria and continuous shot fractions. A Cramer--Rao lower bound on
estimator error cannot certify a finite-shot upper error guarantee.
[SHOALS](papers/2201.13438.md) separates sampling, switching and communication costs.
The repository must add integer shots, job activation, grouped schedules,
matched controls and uncertainty, then compare with uniform and exhaustive
small-case allocation references. A heuristic receives its measured scope;
source theory supplies no global optimum for a different billing problem.

[Classical shadows](papers/2002.08953.md) can estimate many specified observables;
its snapshot budget and measurement ensemble remain part of the theorem.
For a few known low-weight observables, grouped direct measurement may cost
less. Full n-qubit Pauli state tomography uses 3^n local settings for 4^n-1
real state parameters; process/instrument identification adds preparations,
outcome indexing and calibration. Positivity constraints do not repair a
rank-deficient measurement design or supply coverage by themselves.

When the same simulated noise-model event set supports many candidate designs,
retain simultaneous model-error control across the selected family or separate
selection from validation. Apply a joint bound to the actual reused events;
relabeling Monte Carlo samples as independent evidence overstates precision.
Fixed-sample tests, finite planned looks with error spending and time-uniform
confidence sequences are distinct admitted designs. Price complete additional
jobs at every adaptive decision, including the final partially useful batch.

## Ordering and hardware ownership

1. Reuse the [three retained jobs](vacuum_field_run_opportunities.md#relation-to-the-three-existing-qpu-jobs)
   within their circuit, endpoint and calibration scope.
2. Finish exact model, curve and source-bound certificate work on the CPU.
3. Qualify the smallest identifiable experiment against strong classical
   references, explicit model bias, simultaneous inference and full costs.
4. Let the execution owner prepare the approved correction/ripple/rank family
   from final sources, fresh calibration and actual backend availability.
5. Admit additional [field-model opportunities](vacuum_field_run_opportunities.md)
   only through their own source, precision, cost and approval case.

The source intake adds methods and replayable references without enlarging the
conditionally authorized campaign. Packing exploits shared execution time only
when its measured distortion and covariance stay within the declared endpoint
contract. Hardware observations can improve machine understanding without a
new theorem or a computational-advantage claim.
