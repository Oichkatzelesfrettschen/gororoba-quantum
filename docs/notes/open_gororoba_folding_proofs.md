# Folding, exact rank geometry, and Rocq proof audit

The audit identifies an exact route from existing algebra to smaller operator blocks. The route preserves every block and its kernel information. Fold-average projection alone loses zero-divisor information. The sister repository proves useful all-order Boolean sign-code statements, while its formal rank-geometry coverage remains substantially narrower than Koebisu's dimension-32 question.

The [Koebisu research note](koebisu_rank_stratum_research.md) connects the primary sources to the geometric program. The [portable replay bundle](../evidence/folding_proofs/README.md) retains the exact counterexamples and fresh proof receipts. Sister-repository locators below use [open_gororoba at the audited commit](https://github.com/Oichkatzelesfrettschen/open_gororoba/tree/abbf13cada78d9b106fc610a36f6eea54567ecfc).

## Source identity and execution boundary

The inspected `open_gororoba` checkout has HEAD `abbf13cada78d9b106fc610a36f6eea54567ecfc`. Both the initial and final observations report exactly ` M .gitignore` and `?? .ignore` in `git status --short`; both report the same HEAD. The audit preserves those concurrent edits. The audit writes its report, copied proof sources, compiler outputs, and exact counterexample results under temporary storage. The audit performs read-only source inspection in the sister checkout and invokes zero QPU submissions.

The repository guide separates source propositions, implementation conformance, and phenomenological mapping (`AGENTS.md:318-348`). Its matched-control rules require support, dimension, parameter count, temporal receptive field, and measurement procedure to match (`AGENTS.md:390-404`). Its falsifier rule prioritizes the cheapest decisive test (`AGENTS.md:406-432`). Those rules directly support model discrimination and an optimizer decision before broad atlas sampling.

## What the existing implementations and theorems actually establish

| Source and locator in `open_gororoba` | Established object | Boundary and use |
| --- | --- | --- |
| `crates/algebra_analysis/src/exact_annihilator.rs:57`, `:199`, `:287` | Rational multiplication matrix, kernel columns, nonsingular pivot, and independent certificate verification | A certified rational point has the same rank over Q and R. Finite points alone do not classify a real rank locus. The file's SHA-256 matches the source pin in IBMQuantum `rank_charts.py:24`. |
| `proofs/theories/SedenionMembershipConstraints.v:13-38` | A sum-of-squares polynomial vanishes exactly when both scalar halves vanish, imaginary half norms agree, and their inner product vanishes | The statement identifies a polynomial zero set; the link to singular multiplication still uses the determinant factorization. `:40-54` proves the polynomial gradient vanishes on that zero set. Use component equations or Schur equations for smoothness. |
| `proofs/verified/C1630_SedenionOctonionDowncast.v:19-66` | Both operands with zero upper octonion half multiply exactly as octonions | A shape-conditioned reduction, not a projection of arbitrary 16D zero divisors. |
| `proofs/verified/C1638_OctonionDowncastNoZeroDivisors.v:21-72` | A zero product of two such lower-half operands forces one operand to vanish | An exact negative control: the octonion restriction cannot retain a nonzero zero-product pair. |
| `proofs/theories/CDDoubleFunctor.v:17-67`; `CDDoubleTower.v:18-86` | Generic doubling inherits declared linear identities; a real base instantiates the tower through pathions | Module-type axioms express input interfaces and the real base supplies proofs. The resulting tower supplies multiplication and linearity, not rank-stratum topology. |
| `proofs/theories/MorenoKerLaNonAlternative.v:1-31`, `:104-150` | For the concrete non-alternative sedenion `e3+e10`, four explicit annihilators are independent | A lower bound of four for one representative. The source explicitly supplies neither an upper bound nor a universal classification. |
| `proofs/theories/C1543_MorMod4Bound.v:95-126` | `is_h_module_dim ker_dim -> exists k, ker_dim=4*k`; `4+ker_dim<=2^n -> ker_dim<=2^n-4` | Conditional dimension arithmetic. The arbitrary non-alternative kernel-to-H-module bridge remains an obligation. Arithmetic comparison with the BDI bound does not prove the BDI theorem. |
| `proofs/theories/C1542_MorVlambdaArbClose.v:1-40`, `:66`, `:115` | Arbitrary unit imaginary octonion inputs have trivial nonunit eigenspaces and trivial left kernel | The arbitrary quantifier ranges over octonions. It does not cover arbitrary dimension-32 zero divisors. |
| `proofs/theories/C1549_MorHaStabilitySed.v:1-39` | The specific sedenion basis element `e1` has `L_a^2=-I` | The source explicitly identifies the trivial alternative regime. |
| `proofs/theories/SchreierSignCode.v:476-494`, `:702-780`, `:872-921` | All-order recursive sign-span characterization, unique normalized ANF representation, basis size `2^(n-1)-1`, and scalar direct sum for `n>=3` | A universal binary-code theorem, not a universal real-annihilator theorem. Reuse it for exact oracle synthesis and phase bookkeeping. |
| `proofs/theories/SignCodeCardinality.v:130-165` | Membership, duplicate-free enumeration, and codeword cardinality `2^(2^(n-1)-1)` for `n>=3` | The count concerns normalized sign tables. A small generating basis does not imply a small enumeration. |
| `proofs/theories/SignCodeProjection.v:18-74`, `:125-135` | Normalization `v(x) XOR v(0)` splits off a scalar sign; controlled reconstruction preserves the sign on the control branch | `crates/cd_kernel/src/cayley_dickson/sign_code.rs:33-122` carries the scalar as `control_z`. Dropping a global phase before coherent control changes the relative phase. |
| `proofs/theories/BooleanCochainFiltration.v:56-116`, `:158-190` | Linear pullback and the specified XOR-group cochain differential preserve degree bounds | It supplies compiler algebra; it supplies neither a query-complexity lower bound nor rank geometry. |
| `proofs/verified/C881_GF2CubicMinDegree.v:23-40`, `:50-119`, `:129-141` | A finite 15-label cubic witness separates the saved classes; selected linear/quadratic candidates fail | The file does not contain exhaustive degree-two rejection despite its header. The Rust test `crates/algebra_analysis/src/projective_geometry.rs:1573-1622` performs the broader computational rejection. Preserve that evidence split. |

The all-order sign-code proof is real formal progress. The rank-topology program should reuse its phase-exactness results without converting Boolean labels into continuous rank strata.

## Folding and collapse: preserve the complement

The actual fold-average code resides in `crates/algebra_experimental/src/sedenion_subalgebras/tests.rs:39-107`:

```text
i(u) = (u,u)
p(a,b) = (a+b)/2
h(a,b) = (a,b) - i(p(a,b))
```

The identities `p i = I` and `h = I-i p` make `h` a complementary linear projection. The comments explicitly require a differential, grading, and verified chain contraction before invoking a homotopy-transfer theorem. The test at `:2094` classifies a cubic polynomial on 210 ordered distinct imaginary basis triples. The test at `:2720-2880` evaluates a related 32D-to-16D polynomial on 455 unordered triples and prints counts; its count printing carries no assertion that closes a universal classification.

Several Rocq names overstate their mathematical surface if read without their statements:

- `HomotopyTransferAssociator.v:1-7` explicitly supplies XOR incidence counts, with neither a retraction polynomial nor transfer data.
- `WilmotRetractionTheorem.v:34-36` proves the literal natural-number identity `35+252+168=455`. The theorem contains neither a multiplication operator nor a classification function.
- `WilmotPathionRetraction.v:87-120` defines a different lower-half projection polynomial. Its `:175-184` checks counts `343+112=455`; it does not formalize the diagonal/fold-average polynomial.
- `MinimalUncurvedObstruction.v:25-46` proves the arity-three identity forces associativity when `m1=0` and the multilinear zero-input laws hold. Its `:51-62` exhibits sedenion nonassociativity. A proposed minimal uncurved A-infinity structure with unchanged nonassociative multiplication therefore faces an actual obstruction.

A fresh exact rational counterexample shows why discarding the complement fails. Under the repository convention, take

```text
x=e3+e10, y=e6-e15 in dimension 16.
x*y=0, rank(L_x)=12.
p(x)=(e3+e2)/2, p(y)=(e6-e7)/2 in dimension 8.
p(x)*p(y)=e5/2, rank(L_p(x))=8.
```

The audit evaluates those identities with integer/Fraction arithmetic and an exact independent pivot/kernel certificate. The [counterexample result](../evidence/folding_proofs/fold_projection_counterexamples.json) and [replay script](../evidence/folding_proofs/fold_projection_counterexamples.py) retain both witnesses. Fold-average sends a nonzero zero-product pair to a nonzero product. The linear retraction of ambient vector spaces does not restrict to a retraction of the zero-product incidence space.

An invertible coordinate transform retains the missing information. For `T=(1/sqrt(2))*[[I,I],[I,-I]]`, use the full `T^T L_x T`. Rank, singular values, and kernels transform exactly; the transformed blocks remain coupled. Over rationals one can use the unnormalized sum/difference transform and record its Gram metric. Discard a block only after an exact invariant-subspace or Schur-complement certificate permits the operation.

For the repository doubling convention,

```text
(a,b)(c,d) = (a*c-conj(d)*b, d*a+b*conj(c))
L_(a,b) = [[L_a, -R_b C], [L_b C, R_a]],
```

where `C` is lower-algebra conjugation. On a chart where `L_a` is invertible, block elimination gives

```text
rank(L_(a,b)) = 16 + rank(R_a + L_b C L_a^(-1) R_b C).
```

The general pivot-minor mechanism covers charts where that particular half block is singular. The dimension reduction is an exact equation transformation with a reconstruction map, not a topology-preserving assertion about projection.

## A bounded strategy for Koebisu Discussion question 4

Koebisu's question asks for the geometry of dimension-32 rank strata. IBMQuantum already converts the determinant/eigentheory literature into all-real rank predicates and rational kernel charts. `rank_polynomials.py:151-194` evaluates the trace/Newton coefficients and tests nullity. `rank_charts.py:181-289` defines fixed-pivot charts and transitions. The same real locus can require several smooth strata; all-real set membership does not supply those strata.

The useful sequence preserves each proof obligation:

1. **Certify shared conventions.** Pin the signed basis recursion, conjugation, multiplication side, normalization, and source identities in a portable certificate. The Rust exact-annihilator source hash already agrees with IBMQuantum's pin. Port that convention to the Rocq tower through a proved basis-sign bridge before using the tower as a checker for matrix certificates.
2. **Generalize the affine-XOR support reduction.** If the support of `x` lies in a coset `a+H` of a binary subgroup `H`, then multiplication sends the coordinate subspace on `c+H` into the subspace on `a+c+H`. Independent row and column permutations therefore yield `2^n/|H|` square blocks of size `|H|`. The XOR support law proves the block cover for every real coefficient on that support; the signs remain in the blocks.
3. **Retain a complete restricted family before enlarging support.** IBMQuantum's path has support `{1,10,18,25}=1+{0,11,19,24}` (`rank_attachments.py:23-51`). The eight four-by-four blocks, their minors, the exceptional parameters, and the common kernel already carry exact certificates (`:102-189`). Replace the one-parameter coefficients with independent real coefficients on that four-term support, factor the block minors, and construct the complete semialgebraic rank decomposition on that support sphere. This is a useful next theorem with a finite target. It is not the full 32-variable classification.
4. **Describe local transverse geometry.** At a certified point, choose a maximal pivot `P` and compute the residual `S-R P^(-1)Q`. Along a perturbation `x+epsilon*v`, its first derivative represents the induced map `ker L_x -> coker L_x`. The vanishing of that induced map is a necessary tangent condition for a differentiable fixed-rank path. Higher-order terms and the real radical determine whether the condition is sufficient. Singular first derivatives demand higher-order analysis; they do not certify a smooth stratum.
5. **Use symmetry only with its actual action.** Any octonion automorphism preserving multiplication and conjugation extends componentwise through the doubling formula. A diagonal G2 action therefore transports ranks and kernel frames across the four octonion quarters. A useful slice calculation must track stabilizers, orbit types, slice coverage, and residual discrete identifications. Finite Fano permutations do not by themselves establish that slice theorem.
6. **Construct the incidence attachment data.** Over each smooth base piece, attach the unit sphere of the full kernel with the actual transition matrices and Gram metrics. Near a rank drop, retain the entire limiting kernel relation and local link, including approach directions outside the existing path. A count of fibers and a closure partial order leave attaching maps unspecified.
7. **Certify a global model only after coverage.** A compatible semialgebraic triangulation or a proved homotopy-colimit model supplies the boundary maps and diagonal approximation needed for integral homology and cup products. Betti numbers, Euler characteristic, and equal fiber dimensions do not identify that model.
8. **Extend only the proven recurrence.** `rank_path_topology.py:156-220` and its documentation use ordinary embedding `(a,0)` and kernel doubling to obtain a uniform restricted family. An all-dimensional classification additionally needs a theorem controlling arbitrary high-half coefficients, every rank component, and its links. A tower implementation or many dimension checks supplies a different object.

The sparse-block idea is a methodological extension of the existing path certificate, not a literature-priority claim. Its coverage theorem comes from the XOR basis law. Dense support can generate the entire binary space, leaving one full-size block; the method records that boundary rather than assuming a reduction.

## QPU role and a concrete optimizer comparison

Hardware cannot prove the real classification. Hardware can decide whether a proposed circuit reduction preserves a calibrated observable more efficiently on the available machine.

For the affine-XOR family, `L_x` is block diagonal after independent row/column permutations. Therefore `L_x^T L_x` is block diagonal on input sectors, and

```text
||L_x y||^2 = sum_C ||B_C y_C||^2.
```

A sectorwise experiment estimates that norm with sector weights; it does not need coherent interference between distinct input sectors for this particular observable. A four-dimensional block needs two state qubits, while the full 32D state needs five. A coherent implementation with a three-qubit sector label restores the full register size, so a width-saving claim requires a sectorwise observable and a disclosed classical mixture. Full kernel tomography or coherent transfer between sectors has a different measurement contract.

The measurable optimizer decision compares full LCU and sectorwise/block compilation on the same algebraic input and norm observable. The comparison retains all sectors with their exact weights, preserves controlled scalar signs, counts state preparation and reconstruction cost, and records each normalization `alpha_C`. Shots target reconstructed norm uncertainty rather than raw success-probability width: `q=alpha_C^2*p` multiplies probability uncertainty by `alpha_C^2`. Any proposed saving counts total shots, reset/initialization time, and IBM charge rather than only gate count.

The scientific order is:

1. Fit and challenge explicit readout, coherent phase/overrotation, delay, and history-dependent hypotheses against the retained shot-ordered results, separating exploration from later validation.
2. Select a matched control that discriminates the surviving models. Terminal writer, layout, gate count, scheduling, and shot ordering remain declared covariates; one experiment cannot attribute a confounded contrast to a unique mechanism.
3. Preregister one optimizer choice and a practical noninferiority or improvement margin, equal-or-lower charged time, and a fresh independent validation rule.
4. Prepare a small dry run for the resulting case. The user's approval still binds the exact calibration, layout, QPY, shots, and time ceiling.
5. Expand the atlas only after the model comparison or validated optimizer decision produces information that justifies its expenditure.

Positive cosine fringes across many signed basis pairs validate a shared circuit law; they do not provide one independent topological discovery per row. The source and proof audit supports the user's prioritization directive.

## Deficiencies that source reconciliation must expose

`crates/algebra_analysis/src/stiefel.rs:3-14` still states `V_{8,2}` and an unrestricted equal-norm/orthogonality criterion for sedenion zero divisors. The criterion omits pure imaginary half constraints. The exact input `1+e9` has orthogonal equal-norm octonion halves and full rank 16, so the stated iff fails. The unit sedenion zero-divisor element base is `V_2(R^7)`; normalized zero-product pairs give the G2 total space with SU(2) fiber. `SedenionMembershipConstraints.v` already records the required scalar constraints. A separate sister-repository change owns the stale-header repair and dependent-attribution audit. The present source-integration change documents that follow-up and preserves its boundary.

`G2OctonionAutomorphisms.v` should also be read by theorem rather than introductory slogan. Its displayed theorems enumerate Fano lines, XOR signatures, and finite counts. A continuous G2 action does not in general permute the seven fixed imaginary basis units. The finite incidence calculation supplies different evidence from the continuous-group action used for a geometric slice.

The C881 header claims more than the theorem list establishes. The audit retains its exact cubic witness as formally checked, attributes exhaustive low-degree exclusion to finite code, and leaves the formal exhaustive rejection as a separate target.

## Fresh Rocq verification

The PATH command reports Rocq 9.2 with OCaml 5.5.0. The audit explicitly selects the repository-pinned Rocq 9.1.1 with OCaml 5.4.0. Fresh copies under temporary storage compile with `-q -w +all`, using logical roots `OpenGororoba` and `OpenGororobaVerified`.

The following sources compile successfully: `GF2Algebra.v`, `SignCodeProjection.v`, `SchreierSignCode.v`, `SignCodeCardinality.v`, `BooleanCochainFiltration.v`, and `C881_GF2CubicMinDegree.v`. A fresh query prints assumptions for `controlled_projection_exact`, `normalized_schreier_characterization`, `normalized_anf_basis_cardinality`, `normalized_code_cardinality`, `xor_group_differential_preserves_degree`, `cubic_witness_separates`, and `cubic_witness_max_degree`. All seven outputs read `Closed under the global context`. The independent `rocq check -silent -o` succeeds and reports no axioms, type-in-type dependencies, unsafe fixpoints, or assumed positivity. The checked proof closure has zero `Admitted.` declarations. Section hypotheses in the generic projection/cochain APIs become explicit theorem premises.

The attempt to compile `HomotopyTransferAssociator.v` under the same warnings-as-errors command fails while loading the installed transitive library `Stdlib.ZArith.ZArith_base`, deprecated since 9.0. The retained log identifies the failure as a library deprecation import. The audit neither suppresses that diagnostic nor advertises a fresh successful compile for the dependent Wilmot files. The audited real-algebra files receive source inspection only in this pass; their classical-real dependencies and any wider repository admission surface remain outside the fresh axiom-free closure above.

## Pinned source hashes

These SHA-256 identities refer to source bytes at the inspected sister HEAD, not stale `.vo` objects.

```text
5311372ac352568bd63ecd2f850b82639952ac6f014158f8e5c6767b1cd23d8e  proofs/theories/SignCodeProjection.v
54b9e22250f20e185139c53d83e89f362a74d13979ecc0c42b3ddf0efcb0d417  proofs/theories/SchreierSignCode.v
b21c09a7bfdcdeb4aae66ef804a8bd7b0e46edc720864b045689b28b0e2f52b7  proofs/theories/SignCodeCardinality.v
b9672d8df27dabe052e0ba32f53e9e84230b3735d570efeb311e808678454e69  proofs/theories/BooleanCochainFiltration.v
c4f8b9bcce3a8e26346c2da6fab78e36432f3c294056f2781a2b0ff0ce977026  proofs/theories/WilmotRetractionTheorem.v
97768010a07101a3e2acf17d51d51e4573430242dc9ef187df49d5e49ca32e44  proofs/theories/WilmotPathionRetraction.v
94da87caa2e0225db895125a8e1451f9455fb555637454b93e4eb2980165cf53  proofs/theories/MinimalUncurvedObstruction.v
faccbbdc5022ba4bb22e418c903c9382e5d9a7b26851fafe546b29d0c60c57e8  proofs/theories/CDDoubleFunctor.v
4388ec806d0118bf0e31d1e116bbecea334ddb4d9c21c3ce71c775e6f2f7a46f  proofs/theories/CDDoubleTower.v
cc32e70ff3d45b68510121d0dc3837e9539e010951a4fceb487a3339a4e439d3  proofs/theories/C1543_MorMod4Bound.v
53979972099cadaae5f6b48d6a4d58fa8cdd407bb47ce8e031bd50580c430e4b  proofs/theories/MorenoKerLaNonAlternative.v
ff8cd71e981c4b8d6270837e2c4d78ec2f97027559ab3c84730eb299a5258b57  proofs/theories/SedenionMembershipConstraints.v
888059f2c064d811e3d0e5a8f4faaa2a104b19eb6a521d3b34e2f339dd8598c1  proofs/verified/C881_GF2CubicMinDegree.v
8fd08fce53b1d9af769b63e51f739e93e0c169ac9179486b33ddbaecdac5aa58  proofs/verified/C1630_SedenionOctonionDowncast.v
b0ca842aeae81967d629ca7052aa69d0bdba48aa9782ed13ed5caf119a54cb3e  proofs/verified/C1638_OctonionDowncastNoZeroDivisors.v
0769f94d0ceb9bf935324a5220c5905d2826e6b88be19ef7e0c45d6b4d96ead2  crates/algebra_analysis/src/exact_annihilator.rs
a85469aa465da833fea58c022bf4c49602f26bb70e34be48d8ed056f31d1599d  crates/algebra_analysis/src/projective_geometry.rs
4bed78b71b01c594fb49d1251f107e0411d485fc42857f154e849aa006a37340  crates/algebra_analysis/src/stiefel.rs
d4c60e8b50e1b8d48c5c17ecca9bd4847323e27fe409d73661ee36791f0f7b6b  crates/cd_kernel/src/cayley_dickson/sign_code.rs
02f80898dd654755c3ead112e57bc9c9580c39faf4da586f379653d4d14db666  crates/algebra_experimental/src/sedenion_subalgebras/tests.rs
```
