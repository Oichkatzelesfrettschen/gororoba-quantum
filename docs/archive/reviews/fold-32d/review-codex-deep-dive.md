# Adversarial review of the Cayley-Dickson folding program

## Bottom line

1. **High consequence -- the proposed nullity sum rule is false and has no repair using only the two requested scalar inputs.** [COMPUTED] Exhaustive exact rank gives 480 failures among 512 mixed basis operands. The pair `(n_16(z), n_16(e_i +- e_j)) = (8,0)` maps to both `n_32 = 0` and `n_32 = 12`, so those two scalars do not determine `n_32`. The exception-aware basis law is `n_32 = 0` for `i = 0` or `j in {0,i}`, and `n_32 = 12 - 2 n_16(e_i +- e_j)` otherwise; it has zero failures (command C1 below).
2. **High consequence -- the synthesis overstates two boundaries.** [PROVED] The sentence that folding carries "never ideals or Hilbert functions" is false as a universal statement: the W8 defining ideal itself becomes `J(z) + J(z')`, so its quotient is a tensor product and its Hilbert series squares. The narrower statement about the A4 Pfaffian scheme `PB` is correct: `PB` is a proper subideal of `J` with the same radical and an embedded dimension-6 part (`docs/notes/topics/a5-hardware-algebra-synthesis.md:168-177`; `docs/evidence/a5-w8-a4-restriction/README.md:60-82`).
3. **High consequence -- the synthesis names the wrong missing lemma for general half-fold doubling.** [PROVED] `RealHalfFold.first_half` already identifies the doubled kernel with two copies of the lower kernel for every real operand, not only a pure operand. Finite-dimensional kernel dimension and rank-nullity yield general nullity and rank doubling. A scalar-part invertibility split is unnecessary; the missing Rocq artifact is the kernel-dimension/rank bridge (`proofs/CdHalfFold.v:89-101,110-125`; `docs/notes/topics/a5-hardware-algebra-synthesis.md:178-188`).
4. **High consequence -- the product identity does not reduce any listed exceptional-fiber rank job.** [PROVED] `F(W8)` depends on the kernel-coordinate ideal and map, while `J(z) + J(z')` describes the ambient W8 base. The record has no factorization of `K2`, the multiplication tables, or the degree-6 receipt computation; the W8 fiber has degree-20 and degree-30 components that are independent of the base product statement (`docs/evidence/a5-exceptional-fibers/ledger.tsv:9,13,62-66`; `docs/notes/topics/a5-hardware-algebra-synthesis.md:262-273`).
5. **Medium consequence -- the mixed recurrence has a credible proof route but claim 1 does not finish it.** [PROVED] Half-fold block formulas supply the low/high decompositions. The mixed case additionally needs the associator-sign census `omega(a,c,x)`, which identifies the nonzero commutator columns; the proof file explicitly records that absence (`proofs/CdHalfFold.v:35-45`; `docs/notes/singular_sector_dynamics.md:84-102`).
6. **Medium consequence -- the equal-frequency palindromic claim fails at the endpoints.** [COMPUTED] In dimension 32 the unsigned counts at nullities 0 and 12 are 171 and 126, and in dimension 64 the counts at 0 and 28 are 435 and 342. The positive interior counts mirror under `r -> D/2-4-r`; the support is palindromic, but endpoint multiplicities are unequal (command C4 below; `docs/notes/topics/a5-hardware-algebra-synthesis.md:160-164`).
7. **Medium consequence -- the W8 real slice explains the set/radical result, not equality with the Pfaffian scheme.** [PROVED] Setting the upper half to zero makes `z = z' = y`, so `J(z) + J(z')` restricts to `J(y)`. The result does not put `U-V` or `W` in `PB`; the record proves `PB` is properly contained in `J` and `rad(PB)=J` (`docs/evidence/a5-w8-a4-restriction/README.md:27-33,63-82`).

**Steelman.** [PROVED] Folding exactly classifies both half embeddings and, after the sign-census step, every two-term basis operand; the W8 coordinate change also gives a genuine product of base schemes rather than a numerical coincidence (`proofs/CdHalfFold.v:76-125`; `docs/notes/singular_sector_dynamics.md:84-119`; command C2). The findings below restrict only the extrapolations from those results to all nullity strata, pointwise complex nullity, Pfaffian schemes, and exceptional fibers.

## Reproducible evidence

**C1 -- exact rational nullities and seeded off-basis probes.** [COMPUTED]

```sh
cd /tmp/fold-deep-dive-codex
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
PYTHONPATH=gororoba_quantum \
"${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python" probe.py
```

The command exited 0 in 5.67 s. [COMPUTED] Its mixed-basis output was `(0,0,0) x32`, `(0,8,8) x60`, `(4,4,4) x168`, `(12,8,8) x252; `sum_rule_failures=480`; the augmented cells were `(0,0,0,0) x16`, `(0,0,0,16) x16`, `(0,8,8,0) x60`, `(4,4,4,4) x168`, `(12,8,8,0) x252`; and `exception_aware_law_failures=0`. The tuple order is `(n_32,n_16(z),n_16(z'))`, with real nullity appended in the augmented cells.

[COMPUTED] The same command used ANU draw indices 2, 3, and 4 with values 11166, 29825, and 52058. Six W8 points gave `(8,4,4)` with supports 24--27 and passed `U-V=W=0`; two real-diagonal points gave `(8,4,4)` with supports 8 and 10; two off-W8 points gave `(0,0,0)` with support 27. All ten satisfied the sum relation. The finite sample supports only the hypothesis stated below.

**C2 -- record-generated W8 product ideal.** [COMPUTED]

`probe.py` imported `piece_ideals(...)["W8"]`; that producer constructs W8 as `mu, U-V, W` from the repository's original-coordinate arithmetic (`docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py:266-289`). It generated both Singular inputs outside the repositories. The commands

```sh
Singular twisted-product-p32009.sing
Singular twisted-product-p32003.sing
```

each exited 0 under Singular 4.4.1 in 0.29 s. [COMPUTED] Both outputs reported dimension 24, degree 16, and Hilbert numerator `1,-4,2,12,-17,-8,28,-8,-17,12,2,-4,1`. This equals the square of `1,-2,-1,4,-1,-2,1`, the recorded numerator of `J` (`docs/evidence/a5-w8-a4-restriction/README.md:54-66`).

**C3 -- formal replay.** [COMPUTED]

```sh
ROCQ=rocq sh docs/evidence/cd-half-fold/replay_rocq.sh
sha256sum -c docs/evidence/cd-half-fold/source_hashes.sha256
```

The commands exited 0 in 53.6 s with `compile_kernel_assumptions_pass CdHalfFold` and `OK` for all seven bound files. [PROVED] The replay checks the theorem receipts and assumptions; it does not add a kernel-dimension theorem (`docs/evidence/cd-half-fold/README.md:34-62`).

**C4 -- two-term multiplicity census.** [COMPUTED]

```sh
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
PYTHONPATH=gororoba_quantum:scripts \
"${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/ci-py3.14.7/bin/python" -c \
'from collections import Counter; from singular_sector_dynamics import pair_sizes, sign_table; print({d: dict(sorted(Counter(n//2 for n in pair_sizes(d, sign_table(d)).values()).items())) for d in (16,32,64,128,256)})'
```

The command exited 0 in 1.44 s. [COMPUTED] The first three unsigned-pair distributions were `D=16: {0:63,4:42}`, `D=32: {0:171,4:84,8:84,12:126}`, and `D=64: {0:435,4:252,8:168,12:168,16:168,20:168,24:252,28:342}`. The dimension-128 and dimension-256 outputs also mirrored every positive interior count and differed at the two endpoints.

## Claims 1--5

### 1. Half fold

- [PROVED] `mul_low` states `(a,0)(c,d)=(ac,da)`, and `first_half` rewrites `da=0` to `ad=0`; `second_half` proves the analogous high-half kernel statement. The theorems quantify over all operands in every ordered-domain tower (`proofs/CdHalfFold.v:76-101`).
- [PROVED] The gororoba-open theorem is narrower at the kernel level: `pure_doubling_kernel_decomposition` assumes `tower_pure`. Its matrix theorem then proves rank and nullity doubling under that same premise (`gororoba-open:proofs/theories/CDPureDoublingKernel.v:47-79,100-138`).
- [PROVED] Over the real finite-dimensional tower, `ker L_(a,0) = ker L_a x ker L_a` implies `null L_(a,0)=2 null L_a`; rank-nullity with dimensions `2h` and `h` then gives `rank L_(a,0)=2 rank L_a`. These are mathematical consequences for every operand, but the current Rocq files declare neither general dimension statement.
- [PROVED] Strongest valid form: the current repository has the stronger all-operand kernel theorem; gororoba-open has the stronger matrix/rank packaging but only for pure operands.

### 2. Mixed fold

- [COMPUTED] The retained checker implements `|S+| = 2(h-4-|S+|_lower)` outside `j in {0,i}`, zero in the two exceptional cases, and checks every pair through dimension 512 (`scripts/singular_sector_dynamics.py:197-225`).
- [PROVED] The paper route decomposes low and high anticommutators into conjugate blocks, but the mixed block contains `[L_a,R_x]` and `[R_a,L_x]`. Census Theorem 3 supplies the necessary `omega` sign classification (`docs/notes/singular_sector_dynamics.md:84-119`). Claim 1 alone therefore does not prove the recurrence.
- [PROVED] The precise next target for `h=2^k`, `k>=3`, `0<i<h`, `0<=j<h`, and `t in {+1,-1}` is
  `null L_(e_i+t e_(h+j)) = 0` when `j=0` or `j=i`, and otherwise
  `null L_(e_i+t e_(h+j)) = h-4-2 null L_(e_i+t e_j)`.
  The stronger precursor is `|S+_(2h)(i,h+j)|=2(h-4-|S+_h(i,j)|)` in the ordinary case, with cardinality zero in the exceptional cases (`docs/notes/singular_sector_dynamics.md:96-108`).

### 3. Twisted W8 product

- [PROVED] Let `K` have characteristic other than 2 and contain `i` with `i^2=-1`. For every generator `f` of `J`, `Re f=(f(z)+f(z'))/2` and `Im f=(f(z)-f(z'))/(2i)`. The change between `(x_low,x_high)` and `(z,z')` is invertible. Hence the real/imaginary W8 ideal equals `J(z)+J(z')`.
- [PROVED] The quotient is `(K[z]/J) tensor_K (K[z']/J)`. Dimension adds to 24, degree multiplies to 16, and the Hilbert numerator squares. C2 independently checks those invariants at 32009 and 32003; the ideal equality over the original field requires adjoining `i` when the field lacks it.
- [PROVED] The earlier strata record already says `W8=N x N` (`docs/evidence/a5-zero-divisor-strata/README.md:55-66,271-281`). The explicit `J(z)+J(z')` equality and squared numerator are a coordinate and scheme-level corollary, not a new geometric product discovery. The current ledger now records that corollary explicitly (`docs/evidence/a5-exceptional-fibers/ledger.tsv:221`).
- [PROVED] The identity says nothing by itself about `F(W8)` or `h_d`: those objects use kernel-coordinate generators and their graded relations. The degree-5 W8 result and open degree-6 test concern that separate ring (`docs/evidence/a5-exceptional-fibers/README.md:49-54`; `docs/evidence/a5-exceptional-fibers/ledger.tsv:9`).

### 4. Nullity sum rule

- [COMPUTED] C1 reproduces the four claimed cells and all 480 failures over exact rationals. The current retained finite-field record reports the same refutation (`docs/evidence/a5-exceptional-fibers/ledger.tsv:222`).
- [PROVED] No function of only `(n_16(z), n_16(e_i+t e_j))` can fit the basis census: input `(8,0)` has outputs 0 and 12. Adding the exceptional-index flag gives the zero-failure law in finding 1. The complex nullity is redundant once that flag and the real nullity are known.
- [HYPOTHESIS] On each irreducible operand family, the generic ranks satisfy `n_32(a,b)=n_16(a+i b)+n_16(a-i b)` on a Zariski-open subset. C1 tests the ambient complement, W8, and the real diagonal at ten exact off-basis points but does not prove the family-wide claim. An exact minor certificate that establishes the three generic ranks for one irreducible family and gives unequal nullities falsifies the conjecture; a symbolic generic-rank calculation with unequal sides does the same.

### 5. W8 restriction

- [PROVED] The real slice sets `b=0`, hence `z=z'=a`; the sum of the two copied ideals becomes `J(a)`. This explains the restricted W8 ideal (`docs/evidence/a5-w8-a4-restriction/README.md:20-33`).
- [PROVED] The explanation stops at `J`. The Pfaffian ideal `PB` lacks `U-V` and `W`, has a different Hilbert series, and has embedded support of dimension 6 even though `rad(PB)=J` and both schemes have dimension 12 and degree 4 (`docs/evidence/a5-w8-a4-restriction/README.md:63-82`).

## Audit of the synthesis folding section

| Synthesis statement | Determination | Evidence |
|---|---|---|
| Half nullities double; mixed recurrence and special cases | [PROVED/COMPUTED] Correct, with the distinction that the mixed theorem remains unformalized | `docs/notes/topics/a5-hardware-algebra-synthesis.md:155-159`; C3; `proofs/CdHalfFold.v:35-45` |
| Maximum `D/2-4`, maximum count, palindromic spectrum | [PROVED/COMPUTED] The maximum follows from the recurrence, and the checker verifies the bound. C4 confirms the listed maximum counts after doubling unsigned counts for the two signs. The equal-frequency palindromic claim is false at nullities 0 and `D/2-4`; only the support and positive interior multiplicities mirror | `docs/notes/topics/a5-hardware-algebra-synthesis.md:160-164`; `scripts/singular_sector_dynamics.py:197-225`; C4 |
| IBM values 28 and 60 test the ladder | [COMPUTED] Correctly bounded as instrument checks at selected points, not evidence for the algebraic law | `docs/notes/topics/a5-hardware-algebra-synthesis.md:165-167` |
| W8 real restriction and `PB` boundary | [PROVED] Correct through the sentence describing embedded components | `docs/notes/topics/a5-hardware-algebra-synthesis.md:168-175`; `docs/evidence/a5-w8-a4-restriction/README.md:63-82` |
| Folding carries "never ideals or Hilbert functions" | [PROVED] Overbroad and refuted by the W8 product ideal; retain only the claim that a kernel equality does not identify an unrelated Pfaffian scheme | `docs/notes/topics/a5-hardware-algebra-synthesis.md:175-177`; C2 |
| Pure gororoba-open theorem versus general local kernel theorem | [PROVED] Correct distinction | `docs/notes/topics/a5-hardware-algebra-synthesis.md:178-185`; `proofs/CdHalfFold.v:89-125`; `gororoba-open:proofs/theories/CDPureDoublingKernel.v:47-79,100-138` |
| General real doubling needs the nonzero-scalar-part lemma | [PROVED] Incorrect as a necessity; kernel dimension and rank-nullity suffice | `docs/notes/topics/a5-hardware-algebra-synthesis.md:186-188`; `proofs/CdHalfFold.v:110-125` |
| Mixed census theorem is the open formal target | [PROVED] Correct | `docs/notes/topics/a5-hardware-algebra-synthesis.md:188`; `proofs/CdHalfFold.v:35-45` |

## Nullity atlas: reach and blind spots

| Surface | Folding locates | Folding misses |
|---|---|---|
| A5, dimension 32 | [PROVED] Half embeddings carry each A4 kernel to two copies. All two-term basis operands are classified by low, high, and mixed recursion; the A4 zero-divisor half image lies on the real slice of W8 with nullity 8 | [PROVED] Folding does not recover the full components `R_8=W8 union E8-bar`, `R_12=V union B9`, `R_16=N+ union N-`, or `R_4=V(Q) union V(G)`; it gives selected points and the W8 half slice (`docs/evidence/a5-zero-divisor-strata/README.md:248-305`) |
| A6 and A7 | [COMPUTED] The recurrence classifies every two-term basis operand and gives maxima 28 and 60; half embeddings propagate every already-known lower operand (`docs/notes/singular_sector_dynamics.md:104-119`; `scripts/singular_sector_dynamics.py:197-225`) | [PROVED] It supplies no classification of general multi-term operands, orbit closures, or irreducible nullity strata |
| Named off-slice families | [PROVED] W8 is reached only through its half slice and its two-term representatives | [PROVED] E8-bar, Iso, X+, and X- need independent orbit, slice, or fiber data; the hardware record also lists Iso and X among unmeasured blind spots (`docs/notes/topics/a5-hardware-algebra-synthesis.md:68-72`) |

[PROVED] The atlas is therefore a complete atlas of two-term basis nullities, not a complete nullity-stratum atlas for A5, A6, or A7.

## Compute-cost consequences

| Open item | Justified shrink | Reason |
|---|---:|---|
| Iso degree 6 | [PROVED] factor 1 | The identity concerns W8, while the Iso degree-6 fiber rank has its own `K2` and receipt (`docs/evidence/a5-exceptional-fibers/ledger.tsv:8`) |
| W8 degree 6 | [PROVED] factor 1 | The ambient base factors, but the kernel-coordinate fiber ideal and degree-6 multiplication tables have no proved tensor factorization (`docs/evidence/a5-exceptional-fibers/ledger.tsv:9,62-66`) |
| E8-bar degree 6 | [PROVED] factor 1 | E8-bar is the other nullity-8 component and is outside the W8 product identity (`docs/evidence/a5-zero-divisor-strata/README.md:271-281`; `docs/evidence/a5-exceptional-fibers/ledger.tsv:83,95,101`) |
| A5-218 same-dimension components | [PROVED] factor 1 | The degree-20/30 W8 components and degree-4/3 E8-bar-to-VB components live in `V(K2)`; a base-ring product does not decide their attachment (`docs/evidence/a5-exceptional-fibers/ledger.tsv:218`) |
| Characteristic zero | [PROVED] base-only simplification; fiber factor 1 | The algebraic product proof gives W8 base dimension, degree, and Hilbert series over `Q(i)` and permits descent of those invariants. It proves neither characteristic-zero `K2` nor receipt ranks (`docs/notes/topics/a5-hardware-algebra-synthesis.md:273`) |

[PROVED] For a base-only W8 calculation, the identity replaces one 32-coordinate standard-basis problem by two copies of the 16-coordinate `J` calculation plus Hilbert-series multiplication. The listed open jobs are fiber computations, so assigning a runtime or memory reduction to them would be unsupported.

## Hardware-testable statements

| Platform | Testable statement and observable | Ideal value and required mutation |
|---|---|---|
| IBM Heron r2 | [COMPUTED] The kernel-map observable `N_hat` can compare a half operand `(a,0)` with `a`, or read mixed maximum points at 28 and 60; only IBM kernel/coset maps directly estimate nullity (`docs/notes/topics/a5-hardware-algebra-synthesis.md:21-25,165-167`) | [PROVED] Ideal pair `(n,2n)` or exact 28/60. Replace a kernel input by its bright partner or flip a Cayley-Dickson sign and require `N_hat` to change (`docs/notes/algebra_circuit_rules.md:213-222`) |
| Tuna-17 | [COMPUTED] A selector can test one mixed-basis zero-product witness, not global nullity. For `(e1+e10)(e4-e15)=0`, Design B reads selector success | [PROVED] Ideal dark value 0 and bright-control value 1 for `e4+e15` (`docs/notes/algebra_circuit_rules.md:107-124`). The case must use `+,-,-,+` arms, a zero odd-part arm, and the executed order (`docs/notes/algebra_circuit_rules.md:226-243`) |
| Ascella | [COMPUTED] Existing meshes test conditional block levels for four-term operands rather than `N_hat`: B12 has ideal 0.5/0.75, C8 0.6545, and A16 1.0 (`docs/evidence/a5-exceptional-fibers/hardware-orbits/table.tsv:46-48`) | [PROVED] Mutated arms F/C/N change an input or sign table; E0/E1/D are null arms (`docs/evidence/a5-exceptional-fibers/hardware-orbits/result.json:630-632`). A passing level tests the mesh instrument at that point, not the folding theorem globally |
| Belenos | [COMPUTED] The retained record measures conditional one-click frequencies and explicitly leaves source, mesh, processing, and temporal effects entangled (`results/hypercomplex/belenos-repeat-readout.json:1-79`) | [HYPOTHESIS] A future named mesh observable could test a selected fold only after an ideal prediction and a mutation are supplied. The present record establishes no admitted folding/nullity observable |

[PROVED] Every platform result can validate or falsify an instrument prediction at chosen operands; finite hardware samples cannot prove the algebraic laws. The mutation and null-arm rules make that boundary operational (`docs/notes/algebra_circuit_rules.md:207-253`).

## Rocq theorem queue

1. **General real half-fold dimensions.** [PROVED mathematically; Rocq target] For every `k` and `a : cd k`, prove
   `dim_R ker(L_(a,0) : cd(S k)->cd(S k)) = 2 * dim_R ker(L_a)` and
   `rank_R L_(a,0) = 2 * rank_R L_a`; state the same pair for `(0,a)`. Reuse `RealHalfFold.first_half` and `second_half` (`proofs/CdHalfFold.v:110-125`) plus a finite-dimensional product-kernel dimension lemma. Evidence: C3 and the mathematical rank-nullity deduction.
2. **Mixed `S+` cardinality.** [PROVED on paper; Rocq target] For `k>=3`, `h=2^k`, `0<i<h`, `0<=j<h`, prove cardinality zero for `j in {0,i}` and otherwise
   `card S+_(2h)(i,h+j)=2*(h-4-card S+_h(i,j))`.
   Reuse `mul_low`, `mul_high`, and kernel symmetry (`proofs/CdHalfFold.v:78-101`); formalize the census-Theorem-3 `omega` identity described at `docs/notes/singular_sector_dynamics.md:96-102`. Evidence: the checker at `scripts/singular_sector_dynamics.py:197-225`.
3. **Mixed nullity recurrence and maximum.** [PROVED on paper; Rocq target] For the same indices and `t=+-1`, prove the exact nullity formula in claim 2 and derive `nullity <= h-4`, with equality when the lower pair has nullity zero. Reuse theorem 2 and the established `nullity=|S+|/2` Gram-block argument (`docs/notes/singular_sector_dynamics.md:104-119`). Evidence: exhaustive computation through 512.
4. **Corrected two-term census.** [HYPOTHESIS] For dimension `D=2h` and `M=h-4`, prove for every attained `r` with `0<r<M` that the number of distinct imaginary basis/sign operands of nullity `r` equals the number of nullity `M-r`; state the endpoint counts separately, and prove that maximum-nullity pairs correspond to lower invertible pairs. Reuse the low/high and mixed recurrences of theorems 2 and 3. C4 verifies the corrected statement through dimension 256 and refutes endpoint equality; the synthesis states the overbroad version at `docs/notes/topics/a5-hardware-algebra-synthesis.md:160-164`.
5. **Twisted W8 ideal equivalence.** [PROVED algebraically; Rocq target] Over every field `K` with `2` invertible and `i^2=-1`, prove that the ideal generated by `x_0,x_16` and the real/imaginary parts of `mu,U-V,W` equals `J(z)+J(z')` under `z=x_low+i x_high`, `z'=x_low-i x_high`. Reuse the repository generator definition (`docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py:266-289`) and the two inverse linear combinations. Evidence: C2 and ledger A5-223 (`docs/evidence/a5-exceptional-fibers/ledger.tsv:221`).
6. **Product invariants.** [PROVED algebraically; Rocq target] From theorem 5, prove
   `K[x]/I_W8 ~= (K[z]/J) tensor_K (K[z']/J)`,
   `dim=24`, `degree=16`, and `Hilb_I(t)=Hilb_J(t)^2`. Reuse the recorded complete-intersection numerator of `J` (`docs/evidence/a5-w8-a4-restriction/README.md:60-66`). Evidence: C2. This theorem must carry an explicit boundary excluding kernel-coordinate fiber ideals.

## Final assessment

[PROVED] The half fold is stronger than the synthesis says: its general real rank and nullity consequences already follow mathematically. [PROVED] The mixed fold remains a separate sign-census theorem. [COMPUTED] Its claimed equal-frequency palindromicity needs the endpoint correction above. [PROVED] The twisted product is exact and useful for the W8 base scheme, but it neither repairs the pointwise nullity sum rule nor factors the exceptional fiber. [HYPOTHESIS] A generic-stratum nullity sum remains plausible and has a concrete exact-rank falsifier; the current ten seeded points provide finite support only.
