# Formal evidence: algebra, measured counts, and prospective experiments

Rocq can certify an algebraic result, an ideal experiment, or the implication
from a declared acceptance rule to a bounded claim. Hardware samples help
choose and test models; the samples do not become axioms about the device.
The useful deliverable is a chain whose mathematical links are checked and
whose empirical and probabilistic premises remain visible.

The [folding source audit](open_gororoba_folding_proofs.md) owns the prior
proof inventory and exact zero-product witness. The [model-discrimination
decision](model_discrimination_optimizer.md) owns experiment priority. This
note owns new proof dependencies, faithful fold repairs, tomography scope,
and sequential-inference requirements. The execution owner retains circuit
preparation, admission, collection, and the QPU coordination ledger.

The [source-to-proof dependency synthesis](research_proof_experiment_dependencies.md)
adds exact upstream matrix/circuit APIs, curve-selection hypotheses and
instrument-identification/shot-allocation sources. The
[field-model map](vacuum_field_run_opportunities.md) supplies a separate
finite-model proof queue and prospective hardware gates.

## The proof chain and its assumptions

| Layer | Required object | What checking establishes | Remaining premise or bridge |
| --- | --- | --- | --- |
| Source convention | Basis order, signed doubling recursion, conjugation, left/right action, scalar field, phase and bit conventions | Exact definitions agree through a proved correspondence | Matching a few examples across Rust, Python, and Rocq is regression evidence |
| Algebra and finite certificates | Sound checker, exact witness, pivot/kernel certificates, certificate bounds | The stated identity or finite classification follows from the definitions | The denominator, dimension and search domain must match the claim |
| Ideal circuit/instrument | Gate semantics, coherent-control phases, ancilla state, reset and measurement branches | The circuit implements the specified ideal map and decoder | QPY parsing/transpilation and hardware realization need separate conformance evidence |
| Record and decoder | Immutable raw bytes, hashes, labels, shot order, register map and integer counts | The checked decoder maps the supplied record to the stated counts | Hashes bind bytes; they establish neither acquisition authenticity nor calibration truth |
| Deterministic inference | Exact interval endpoints, margin and acceptance predicate | Acceptance implies the claim on a named coverage event | Floating-point statistical routines require certified enclosures or explicit numerical premises |
| Probability | Sampling model, family, confidence level, filtration and stopping rule | The coverage event has its stated probability under the model | Independence, stationarity or conditional-mean assumptions need empirical justification |
| Physical interpretation | Defined subsystem, competing mechanisms, intervention and validation predictions | The observations support or exclude a bounded physical hypothesis | A proof of the inference algorithm cannot certify that the physical assumptions hold |

Every exported theorem should name its domain, premises, conclusion and
source dependencies. Retain `Print Assumptions`, compiler output, independent
kernel output, tool versions, source hashes and replay commands. Distinguish
standard mathematical foundations, interface hypotheses and hardware-model
premises; counting axioms alone cannot establish an appropriate theorem.

The existing [N21 certificate](../../proofs/TargetFlipN21.v) proves finite
Boolean permutation action. Qiskit Operator checks establish phase and clean
workspace behavior separately. Joining those layers requires a gate-semantics
bridge, including relative phases under coherent control.

## Repair fold-average by preserving the missing information

For the repository convention,

```text
(a,b)(c,d) = (a*c-conj(d)*b, d*a+b*conj(c))
p(a,b) = (a+b)/2
```

the retained exact witness has `x=e3+e10`, `y=e6-e15`, `x*y=0`, and
`p(x)*p(y)=e5/2`. The source audit retains the original fixture and provenance.
The new [FoldAverageDescent.v](../../proofs/FoldAverageDescent.v) proves a
different, stronger information-loss obstruction over canonical rational
scalar pairs:

```text
k=(1,-1), z=(0,1)
p(k)=p(0)=0, p(k*z)=1, p(0*z)=0
```

Consequently, every binary operation on averages fails to reproduce
`p(x*y)` for some inputs. The source quantifies over arbitrary `Qc` functions;
canonical equality avoids a rational-setoid loophole. The witness `k*z` is
nonzero. Its theorem is an obstruction to multiplication descending through
the projection, rather than another zero-product witness. A theorem about
every Cayley-Dickson level still needs the scalar-subalgebra embedding bridge.

The certificate also proves both inverse identities and injectivity for

```text
F(a,b) = (u,r) = ((a+b)/2, (a-b)/2)
F_inverse(u,r) = (u+r,u-r).
```

Keeping both coordinates is a faithful coordinate change with unchanged
dimension. Four repair routes have different proof obligations:

1. **Transport the complete product.** Define
   `X star Y = F(F_inverse(X) * F_inverse(Y))`. Invertibility and `F(0)=0` prove that an
   original product vanishes exactly when both transported output coordinates
   vanish. Extend the scalar inverse proof to vector coordinates and prove the
   repository convention bridge. For standard real Cayley-Dickson conjugation,
   writing the other input as `(v,s)` gives the candidate closed form

   ```text
   F(x*y) = (v*u + r*v + conj(s)*u - r*conj(s),
             -u*conj(v) + conj(v)*r + u*s + s*r).
   ||x||^2 = 2*(||u||^2 + ||r||^2).
   ```

   The formula follows by bilinearity and `conj(v)=2*Re(v)*1-v`; its general
   Rocq proof remains open. The diagonal section `i(u)=(u,u)` satisfies
   `p(i(u)*i(v))=v*u`, and `i(1)^2=(0,2)` leaves the diagonal. Even initially
   vanishing detail does not justify dropping detail after multiplication.

2. **Use a certified restricted domain.** The ordinary inclusion
   `j(a)=(a,0)` preserves multiplication. Injectivity gives preservation and
   reflection of zero products on that embedded subalgebra. Arbitrary higher
   zero divisors need a different theorem. The unconditional kernel formula
   is `ker L_(a,0) = ker L_a direct_sum ker R_a`; identifying left and right
   annihilators requires an additional result. For pure embedded inputs, the
   [ordinary-doubling derivation](four_support_doubling.md) proves
   `R_x=-C L_x C` and
   `ker L_(x,0)=ker L_x direct_sum C ker L_x`. Its all-stage written
   induction and exact implementation checks provide concrete Rocq
   formalization targets.

3. **Eliminate an invertible operator block.** For
   `M=[[A,B],[C,D]]` and invertible `A`, put `S=D-C*A^-1*B`. Prove
   `rank M=dim(A)+rank S` and the bijective lift from `ker S` to `ker M`,
   `w -> [-A^-1*B*w; w]`. The lift retains eliminated coordinates. For a basis
   change `T`, normalized partners obey `w^T*G*w=1` with
   `G=J^T*J`, `J=T*[-A^-1*B; I]`. A chart theorem needs an invertible pivot on
   its domain. A global incidence presentation needs chart coverage and
   compatible overlap maps. Computing rank components, attachments and
   topological invariants requires further geometry. The
   [dimension-32 skew-Schur construction](dimension32_skew_schur_charts.md)
   retains `S(x)w=0` across rank changes and `det A != 0` after denominator
   clearing. The lift and metric alone do not determine kernel membership.
   Coordinate transitions are isomorphisms on reduced kernels; different
   center nullities or pivot sizes permit rectangular ambient transition
   matrices. The [principal skew atlas](principal_skew_atlas.md) supplies an
   explicit cover of the nonzero doubly-pure domain at every stage `n>=2`,
   with fifteen domains in dimension 32. Its kernel-restricted overlap
   identities give a global semialgebraic incidence presentation. The
   all-stage written proof, finite exact replay and Rocq formalization remain
   separate evidence surfaces. The
   [selected-center cone proof](nullity_twelve_local_geometry.md) supplies a
   concrete next port: projected-Schur coefficient completeness, the real
   sum-of-squares reduction, actual `A15` and `B17` curves, and both Bouligand
   cone inclusions. Rocq must connect the exact certificate to matrix
   semantics and formalize positivity, denominator domains, automorphism
   flows and tangent limits; CPU replay alone leaves those bridges open.

4. **Keep every support sector.** For support in affine XOR coset `a+H`,
   the input sector `c+H` maps into `a+c+H`. Certify the coset cover and zero
   cross-block entries, then rank/kernel direct sums and
   `||L_x*y||^2=sum_C ||B_C*y_C||^2`. Sectorwise measurements must retain
   preparation probabilities, weights, normalization and uncertainty. Those
   norm identities alone establish neither coherent-output reconstruction
   nor tomography of the full kernel.

A product-defect formula can retain the average output, but the defect uses
discarded information. With ordinary lower multiplication as comparator,
`Delta=(v*u-u*v)+r*v+conj(s)*u-r*conj(s)`. A zero product implies
`u*v=-Delta`; recovering the original zero product also needs the detail
output equation. A complementary projection `h=I-i*p` alone supplies no chain
contraction: homotopy transfer needs a grading, differential, chain maps and
`d*h+h*d=I-i*p`. The inspected minimal uncurved obstruction also prevents
repairing unchanged nonassociative multiplication by merely adding `m3` while
keeping `m1=0`.

## Proof targets available before another QPU run

| Target | Concrete theorem/checker | Dependency and status |
| --- | --- | --- |
| Average-only obstruction | Equal averages can yield different product averages; complete average/detail coordinates have inverse maps | Newly checked scalar `Qc` certificate; full tower bridge remains open |
| Exact zero products and rank | Sound recursive sign/product checker plus the retained 16D counterexample; certified pivot and kernel dimensions | Exact Python/Rust evidence exists; port checker soundness and witnesses to Rocq |
| Schur and sector reduction | Block-elimination kernel bijection, rank sum, metric and full sector cover | Written principal-cover and overlap proofs and exact replay exist; port field/matrix lemmas, cover and refinement-checker soundness to Rocq |
| [Selected-center tangent cone](nullity_twelve_local_geometry.md) | At doubly-pure `e1+e18` in dimension 32, norm squared two and nullity twelve, prove `A15 union B17` with intersection dimension thirteen | Exact CPU certificates and written curve/limit proofs exist; Rocq correspondence and analytic lemmas remain open; neighborhood branches and attachments require additional mathematics |
| Boolean sign and synthesis | Connect checked normalized sign-code results to basis recursion and controlled-phase reconstruction | Seven historical sign-code/C881 queries are closed; the [latest C881 closure](c881_exhaustive_proof.md) kernel-checks exhaustive quadratic rejection and has six closed queries |
| Labeled QPE laws | Exact Gaussian-integer amplitudes and normalized distributions; two-bit arms use `y=b0+2*b1`, while the delay arm uses only its measured terminal bit | Port `qpe_diagnostics.py`; ideal laws require zero hardware samples |
| Finite ripple dynamics | Exact operators, unitarity, return periods and signed graph obstruction | Port the execution owner's exact checker; a depth-0-to-4 hardware run cannot prove a longer operator period |
| Common appended-channel exclusion | Binary-channel contraction plus a count-dependent incompatibility on an interval event | Retained experiment-specific arithmetic; coverage and physical applicability are separate obligations |
| Identifiability | Equal Z laws for distinct phase states; local trace-preserving noise before unconditional reset leaves the other register unchanged | Matrix/channel semantics; these explain why additional repetitions can leave a mechanism unidentifiable |

The restricted geometric port has concrete dependencies. The
[four-support rank theorem](four_support_rank_loci.md) supplies complete
sectors, polynomial minor identities, real positivity and complete kernel
frames. The [incidence construction](four_support_incidence_geometry.md)
supplies inverse continuous maps and coordinate inclusions along closures.
The [doubling theorem](four_support_doubling.md) extends those constructions
by structural induction. The
[cellular homology construction](four_support_cellular_homology.md) supplies
characteristic maps, orientations and integral unit cancellations. These
written arguments and exact implementation certificates establish the stated
results for the fixed first-operand support; Rocq formalization remains
separate. Positive-degree cohomology products vanish by degree support in
that restricted construction, so the stated ring calculation needs no
cellular diagonal.

The [terminal-channel analysis](../../results/live/2026-10-12T055624.091217Z/TERMINAL_CHANNEL_HYPOTHESIS.md)
uses `K(p)=a*(1-p)+b*p`, `0<=a,b<=1`, and contraction of pair separation.
Hardware terminal-one counts are `2964,4911`; replay counts are `4067,4057`,
each out of `8192`. If all four true means lie within radius `21/1000` of
those fractions, the hardware separation exceeds the maximum replay
separation by

```text
(1947-10)/8192 - 4*(21/1000) = 156109/1024000 > 0.
```

The new [rational certificate](../../proofs/TerminalChannelSeparation.v) and
[real certificate](../../proofs/TerminalChannelSeparationReal.v) check that
implication over their respective fields. The rational theorem is
globally closed. The real theorem uses the standard library's classical real
foundations, reported in the retained assumption output. Proving that
the event has 95% coverage also requires a concentration theorem and a
certified comparison with the specified logarithmic radius. A decimal
calculation of a square root or log is separate numerical evidence.

The retained supplemental analysis uses a fixed family of 32 means and its
own alpha 0.05. The simultaneous event permits choosing a pair within that
family after inspection. It excludes neither arbitrary observable selection
nor extra-run search. Combining its guarantee with the original contrast
family's alpha 0.05 gives at least 90% joint coverage by union bound. The
excluded hypothesis appends one common channel to noisy replay marginals;
replacement readout, context-dependent instruments and other mechanisms
remain distinct hypotheses.

## What the next fixed-sample pilot can add

The execution owner is preparing four PUBs: odd labels `s1,s3`, each with
measured feedback `F` and known-label unconditional phase `U`. The ideal
equivalence concerns those prepared labels. It supplies no replacement for
general unknown-eigenstate phase estimation.

The prepared order is `F(s1),U(s1),U(s3),F(s3)`, one replica and 8192 shots
per PUB. `U` retains the same classical dispatch and removes the correction's
dependence on the recorded bit. The two bits remain recorded in every shot;
separate PUBs are unpaired. Conditional strata remain descriptive unless a
prospective inferential contract explicitly includes them. Preparation skips
the broken mock service and refreshes Target/properties from all three live
devices before selecting the best backend for the actual matched family.
The execution owner's [retained preparation comparison](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/fb5e6aaad2a91466e1a7c1f33220ba57af1d39ef/results/ripple/CORRECTION_PREPARATION.md)
ranks 18 admitted candidates, six seeds per backend. Fez has the highest
weakest-arm calibration proxy in that snapshot; the score estimates circuit
quality and supplies no measured fidelity. The execution workstream owns
that comparison and its unapproved record.

Submission preflight must refresh and rerank all three systems. The selected
backend is refreshed again before its batch; queueing separates those checks
from physical execution. Changed selection, calibration or QPY requires
renewed approval. The execution owner separates local timing estimates from
returned schedules and measured service usage. Hardware submission remains
bound to its concrete approved record.

Freeze the following before acquisition:

1. Hypothesis family, independent predictions and the optimizer decision.
2. Circuit/QPY hashes, phase labels, register maps, layouts and control policy.
3. Estimands, score ranges, gain margin, interval method and family allocation.
4. Fixed shot allocations, missing-data handling, drift checks and conformance
   failure rules; all prior shots have already been inspected.
5. Execution ceilings, reserve, charge assumptions and the approved record.

The proposed gate is `L_U(s)-U_F(s)>1/100` for both labels, with four
one-sided Clopper-Pearson bounds at tail probability `0.05/4`. Prove the
four-event union bound and the deterministic margin implication first. After
collection, emit integer counts, outward rational endpoints, certified
binomial-tail witnesses and the resulting decision certificate. Ordinary
SciPy float64 beta quantiles implement the exact-binomial method, but their
numerical endpoints are not interval-certified. A printed float cannot stand
in for the enclosure proof.

Within-stream independent stationary Bernoulli trials justify those binomial
bounds. Union-bound coverage permits dependence between PUBs; the planning
power calculation can require stronger assumptions. Failure to pass the gate
means inconclusive admission, rather than proof of equality. A prospective
run supplies fresh validation after the model and rule freeze; repartitioning
previously inspected shots does not create an unseen holdout.

The certificate should have the shape
`well_formed_record AND assumptions AND acceptance -> bounded_claim`.
Keep four named results: circuit conformance, observed arithmetic, conditional
coverage, and physical interpretation. New ripple data can support that last
layer and falsify a model; exact recurrence and graph theorems come from the
classical algebra regardless of whether the device reproduces them.

## Define tomography before estimating its cost

Full tomography needs a named target and subsystem. State tomography recovers
an output density matrix. Process tomography characterizes an input/output
channel. Readout tomography characterizes a POVM. Mid-circuit measurement
with a continuing quantum register needs an **instrument**: outcome-indexed
completely positive maps whose sum preserves trace. Retain both the classical
outcome and its conditional continuing state.

| Target | Straightforward informationally complete design | Scope |
| --- | --- | --- |
| Four-qubit state | 255 real state parameters; 81 local Pauli settings per input | Ideal measurement bases and declared SPAM treatment |
| Five-qubit state | 1023 parameters; 243 local Pauli settings per input | Larger than the present endpoint comparison |
| Four-qubit process | 256 independent input preparations times 81 output settings = 20,736 settings | Standard complete product design; alternative designs have their own assumptions |
| Mid-circuit instrument | Informationally complete preparations and outcome-resolved output measurements, with calibration or self-consistent SPAM inference | The measurement outcome alone discards back-action information |

An unrestricted `m`-outcome instrument on equal input/output dimension `d`
has generic interior dimension `m*d^4-d^2`: each Choi matrix is Hermitian and
the sum has a trace-preserving constraint. Positivity restricts the domain;
rank/structure assumptions reduce dimension only after justification. Unknown
SPAM adds parameters and, in gate-set methods, gauge freedom.

The [Rudinger instrument-GST source](papers/2103.03008.md) supplies the relevant
experimental framework. The [Wysocki source](papers/2602.03938.md) studies an
interpretable small-Markovian-error model; it does not attribute the retained
Heron r2 discrepancy. A tomography plan needs preparation/measurement rank
checks, CP/TP constraints, leakage/outcome completeness, gauge interpretation,
an uncertainty metric, drift/Markov tests and held-out predictive checks.
If a finite Markovian instrument cannot explain context dependence, inspect
multi-time/process-memory models before claiming complete characterization.

For scale only, 81 settings at 8192 shots and the historical 250-microsecond
repetition delay already contribute 165.888 seconds of repetition delay.
Circuit duration, scheduling and other costs add to that arithmetic; fresh
backend timing governs an admission case. Marginal tomography of packed
components does not establish their full joint state or independence.
Packing adds useful throughput only when the chosen endpoints and companion
effects remain identifiable. Targeted witnesses or selected observables can
answer a smaller scientific question with a separately justified protocol.

## Adaptive stopping needs a new statistical and execution contract

Repeatedly inspecting ordinary fixed-sample intervals changes their coverage.
Use a prespecified finite set of looks with alpha allocated across every look
and endpoint, or prove an anytime-valid confidence sequence/e-process.
The [Howard et al. source](papers/1810.08240.md) develops time-uniform guarantees;
those guarantees still depend on declared filtration and conditional moment
assumptions. The paper also covers changing conditional means for a running
average of those means. Such a target does not establish a constant hardware
rate or remove temporal confounding between arms.

Before implementing stopping, specify:

1. The estimand, null/alternative, scientifically relevant
   margin, arm/layout family, and population to which the claim applies.
2. The observation filtration, predictable allocation rule, dependence and
   conditional-mean assumptions, and any block/randomization design.
3. The confidence process or finite-look spending proof, including endpoint
   multiplicity and conservative numerical evaluation.
4. Success, futility and inconclusive stopping rules; maximum shots, charge
   and quota reserve; missing-job and drift responses.
5. Executable Runtime job/chunk boundaries. Inspecting counts between jobs
   may add compilation, queue, refresh and control overhead; per-shot
   interruption must be established by the actual service contract.
6. An audit record of every look, all included data, policy version,
   allocations, boundaries and decisions.
7. A fresh approval format binding the full adaptive policy and its maximum
   budget. The existing approval binds exact shots/QPY and does not authorize
   an open-ended sequence of future jobs.

Prove the simultaneous-in-time event before proving the stopped acceptance
implication. The fixed-sample pilot can proceed through its existing gates;
tomography and sequential inference retain their own designs and approvals.

## Dependency-ordered implementation queue

| Order | Artifact and acceptance criterion | Owner |
| --- | --- | --- |
| 1 | Replay the new fold certificate and inspect its assumptions; retain source and raw logs | Formal-evidence follow-up |
| 2 | Prove the basis-sign/scalar embedding bridge, then the full transported product and zero-product equivalence | Formal algebra, coordinated with source audit |
| 3 | Formalize the principal cover, Schur/kernel/metric identities with pivot inequations, maximal-refinement checker and reduced-kernel overlap maps; instantiate complete sector covers | Formal algebra and rank-geometry workstream |
| 4 | Prove ideal labeled-law/decoder and deterministic terminal-channel implications; bind count fixtures | Formal-evidence follow-up with execution-owner review |
| 5 | Certify binomial-tail enclosures and fixed-sample gate soundness before issuing prospective count certificates | Statistics/proof workstream; execution owner supplies frozen policy and records |
| 6 | Acquire an approved pilot, retain full provenance, evaluate the frozen rule and validate predictions | Execution owner; user approves the concrete submission |
| 7 | Design identifiable instrument tomography or a sequential protocol only when the pilot decision requires it | Execution and research owners jointly |
| 8 | Formalize the restricted incidence, doubling and cellular constructions; pursue unrestricted rank components, attachments, invariants or stronger complexity claims after their independent hypotheses close | Rank-geometry or complexity workstream |

The queue separates reusable mathematical theorems from experiment-specific
instances. A finite census, a compilation improvement, a new formalization
and a measured model failure are distinct results. None alone establishes
global rank topology, a universal classification, or computational advantage.
