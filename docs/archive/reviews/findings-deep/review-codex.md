# Deep adversarial review of A5 exceptional-fiber findings

Reviewer: codex

Review target: branch `docs/a5-32d-findings`, commit `3d928b1a6afb0e922e7d8585552c39eec08f1c77`, PR #798.

Boundary: the review used the committed target. Concurrent uncommitted worktree changes are outside the reviewed diff. The review wrote only this report. Random indices used: none.

## Ranked findings and resolutions

### 1. High: A5-241 assigns a chi-square tail to a correlated statistic

**Status: falls at the statistical axiom layer.** `nhat_spectral.py:128-135` subtracts each replica's eight-bin mean and then sums squared marginal Student statistics. Mean subtraction makes the eight residual coordinates sum to zero, while the shared shot counts and conditional contrasts add covariance. The seven-dimensional residual has correlated coordinates, so the sum is not chi-square with seven degrees of freedom. The committed prose nevertheless reports `p < 0.001` on 19 of 52 blocks (`docs/evidence/pathion-kernel-map/nhat-bias/README.md:221-225`), and ledger A5-241 calls that evidence `survives` (`docs/evidence/a5-exceptional-fibers/ledger.tsv:240`). Reproduction of `result_spectral.json` confirms the implementation; the self-test checks algebraic identities and mutations, not this null distribution.

**Consequence.** The retained data still show bin spreads of 0.007 to 0.011, but the committed significance count does not establish a non-readout contraction. A5-241 must become `open` until a joint test replaces the marginal sum.

**Resolution.** Form the seven independent within-replica residual coordinates, estimate their full covariance, and use Hotelling's T-squared with its finite-replica F calibration when replicas exceed dimension. A shot-level or replica-label permutation bootstrap is the robust alternative. Correct the family of 52 blocks, retain `flatness_chi2` only as descriptive output, regenerate `result_spectral.json`, revise the README, and revise A5-241 from the new joint results. The uncommitted worktree contains a candidate Hotelling implementation; it requires review and belongs in a separate fix to the reviewed target.

### 2. Medium: the Iso degree-six note contradicts its own retained N=18 record

**Status: documentation defect; the certificate survives.** The note says N=18 was unmeasured (`iso-d6-n19-laptop/README.md:21-23`), then records N=18 as `r_18=2253` with blocks 583/568/551/551 (`:25-29`, `:47-48`). Both primes reach `r_19=2422` with blocks 632/610/590/590 (`:11-17`, `:49-54`), equal to the K2 upper bound, so A5-119 and A5-125 remain certified.

**Resolution.** Delete the sentence that calls N=18 unmeasured and retain the exact statement that N=18 falls below the bound while N=19 closes the ladder.

### 3. Medium: degree-six feasibility depends on repairs that the current engine does not implement

**Status: measured through degree four/five and extrapolated at degree six.** The four character blocks are coupled by variable multiplication (`w8-engine-map/README.md:67-86`); treating them as independent gives wrong ranks. At W8 degree 6, N=19, the retained model gives 103.3 GiB for dense products, a 129 GiB product peak, a 139-160 GiB closure peak at measured fill, a 223 GiB ceiling, and 18-27 hours (`:88-105`). These are hypotheses extrapolated from measured anchors, not a run. Engine v11 materializes dense generator matrices (`fiber_rank_v11.py:845-900`), uses a preflight model that omits important transients (`:1074-1094`), and copies or rebinds bases in closure (`:1166-1188`). The map's concrete defects are listed at `w8-engine-map/README.md:116-127`.

**Resolution and lever judgment.** Apply levers in this order, and admit the result only when a W8 degree-four rerun gives byte-equal total and block ranks and the preflight lies within 1.3 times measured peak.

1. **In-place update and chunked `new` (d):** remove the three-basis rebind and round-one copy first. This directly removes the known closure transients.
2. **Stream L by generator and degree (e):** required to remove the 103 GiB product wall. The current loop frees each generator but still materializes each dense generator matrix.
3. **Free-column echelon storage (c):** mathematically valid for reduced echelon bases and promising, but table multiplication must become pivot-aware before it can preserve closure.
4. **Two-byte storage with float64 panels (b):** valid for primes below 2^15 only if every panel enforces the exact BLAS bound already used by the engine. It cuts persistent coefficient arrays by four, not the arithmetic and Python-object transients.
5. **Degree filtering (a):** quotient tables already encode truncation. Skipping provably zero product rows saves work, but a degree-filtered basis/table design is needed before it removes dense L.
6. **GPU exact modular GEMM/PLUQ (f):** the prototype can accelerate panels after streaming exists. Two Kaggle T4 devices provide two separate 16 GiB memories, not one 32 GiB array; the laptop and build-host GPUs also cannot hold L. Host-device streaming remains the prerequisite.
7. **Different algebra (g):** local geometric proofs dominate rank runs when they apply. Retained msolve F4 trials used more time and memory than Singular on `J+m^N`; Macaulay2 `specialFiber` and a Rees presentation remain unbenchmarked. Test those on W8 degree four before extrapolating.

### 4. Low: the witness replay leaks file handles while warnings are required to fail

**Status: code-hygiene defect, not a failed witness.** A fresh `witnesses.py` run produced six `sign-isomorphism` rows that were byte-equal to the retained rows and all had `ok=true`. Under `-W error`, finalization emitted repeated `ResourceWarning` messages from `replay/engine/fiber_rank_v8.py:94`, where `open(path).read()` leaves the handle for garbage collection. The ignored finalizer warnings did not change the exit status.

**Resolution.** Replace the expression with `Path(path).read_text()` or a `with open(...)` block, add a warning-as-error unit test for `parse_header`, and regenerate no evidence because the parsed bytes and witness rows stay identical.

## Claim-by-claim disposition

- **C30 in the W8 to N-minus fiber: proved over F_32009 and F_32029, not in characteristic zero.** The point-blowup argument uses the invertible ideal sheaf `(s^2)`, never a unit element (`structure/c30-bounded/README.md:34-44`). Formal-implicit-function uniqueness establishes exact divisibility by `v2` (`:49-65`). The plane family has generic affine-cone dimension at least six and fills C30 (`:66-83`). Radical, saturated K2 and projective Nullstellensatz then give `L=K2` (`:84-94`). Failure requires a bad Cartier identification, nonunique formal solution, failed chart identity, a smaller generic rank, or a failure of radicality/saturation; retained identities, dual-number ranks, K2 membership, and both-prime Hilbert logs test each finite-field link.
- **E8-bar sign transport: certified.** `witnesses.jsonl:13-14` flips `t8,t9`, checks every J and G sign, compares the K2 spans, fixes the origin, preserves grading, and succeeds at both primes. The fresh six-row sign replay matched retained bytes. `build_registry.py --check ...` printed `registry matches`. The transport therefore carries h_5=952 from N-minus to N-plus. A header, generator order, specialization, or grading mismatch would falsify it; the witness checks those surfaces.
- **X degree four at 32029: certified.** The canonical engine-v11 run gives `r_15=240`, blocks 68/66/53/53, and matches the K2 bound (`d4-p2/README.md:3-16`). The sign witness separately transports X-minus to X-plus.
- **Iso degree six: certified at both primes.** The two `r_19=2422` records meet their receipt-bound K2 counts (`iso-d6-n19-laptop/README.md:11-17,49-54`). The note defect in finding 2 does not change the records.
- **A5-244 last-jump box: computed pattern that survives, not a theorem.** Out-of-sample Iso d=6 and X d=2,3,4 match `(2d+1)^2` and the block split (`ledger.tsv:243`; `xm-lown/README.md:25-37`). The X closing rule `floor(7d/2)+1`, the even-degree plateau, and any E8-bar parallel remain hypotheses. X d=2 already refuted the earlier N=7 forecast.
- **Half folds: proved at the stated strength.** `RealHalfFold.first_half` and `second_half` are kernel equivalences (`proofs/CdHalfFold.v:104-140`). `RealHalfFoldDimension` doubles an existing finite basis and derives rank arithmetic (`:237-261`); it does not prove basis existence or a cross-operand formula. The replay printed `compile_kernel_assumptions_pass CdHalfFold`. The real theorems inherit only the retained Stdlib real axioms. The independent gororoba-open theorem proves unconditional low-half nullity by splitting pure and nonpure operands (`proofs/checkpoints/schur-geometry/CDUnconditionalDoublingNullity.v:221-240`); its SQLite claim registry currently contains zero rows, so the file, not that registry, supplies corroboration.
- **Twisted W8 product: proved only as generator/ideal exchange.** `W8_ideal_exchange` is an elementary equivalence over a commutative ring with `i^2=-1` and one-half (`proofs/CdTwistedProduct.v:175-226`). The replay printed `compile_kernel_assumptions_pass CdTwistedProduct`. The theorem proves neither dimension, degree, product decomposition of a fiber ring, nor a Hilbert function; those remain computed evidence.
- **N-hat Walsh identity: proved; the records are measured; mechanism claims remain bounded.** Parseval gives the recorded estimator identity (`nhat-bias/README.md:172-187`). The committed analyzer and result reproduced in an isolated archive of HEAD, and normal and optimized self-tests passed. The local-channel fit and one-character leakage are computed readings (`:189-219`), not device laws. `minus_zero_t` correctly applies a paired one-sample t statistic across five replicas (`nhat_spectral.py:94-101`), but A5-242 was formed after the data and remains an uncorrected exploratory hypothesis (`README.md:231-247`).

## Prior art and novelty boundary

- **Fiber cones and C30.** The universal property of blowups, invertible-ideal twisting, Rees/fiber cones, and projective Nullstellensatz are standard. The specific local slice, plane family, and two-prime C30 identification are case-specific. The literature comparison at `docs/notes/topics/a5-exceptional-fiber-findings.md:372-409` finds no computation of these A5 fibers. Cooper and Price, *Bounding the degrees of defining equations of Rees rings for certain determinantal and Pfaffian ideals*, arXiv:2104.13811, Sections 1-2 and pp. 1-4, gives generic-height determinantal/Pfaffian bounds; this repository establishes none of its transfer hypotheses.
- **Cayley-Dickson folds.** Biss, Dugger and Isaksen, *Large annihilators in Cayley-Dickson algebras*, arXiv:math/0511691, Sections 9-10, Lemma 9.2 and Corollary 9.3, supplies conjugation and left/right-kernel equivalences; Theorem 10.1 supplies a product-annihilator family under narrower hypotheses (`docs/notes/math-0511691.md:31-43`). The generic Rocq formalization and explicit half-operand statement are the contribution, while much of the mathematics is prior.
- **Neighboring zero-divisor work.** Moreno, *Constructing zero divisors in the higher dimensional Cayley-Dickson algebras* (math/0512517, pp. 1-5 opened), Cawagas and Matimyas (2004, sedenion subalgebras and zero divisors), and de Marrais (math/0207003, box-kite/XOR combinatorics) study zero divisors, spectra, or subalgebras, not these blowup fibers. Their local transcriptions reside beside the PDFs in the private documents repository.
- **Sign and twisted transport.** Graded automorphism transport and complex real/imaginary generator exchange are standard. Their application to these exact headers, K2 spans, and W8 equations is case-specific.
- **Last jumps and closing orders.** The documents manifests and opened sources contain no theorem producing the retained sequences. The box law and order laws are new empirical conjectures.
- **N-hat Walsh form.** Walsh inversion and Parseval are standard. Applying them to this estimator, mapping character contractions to retained circuit records, and identifying the orientation-character hypothesis are case-specific.

## Quantum hardware for nullity

Classical exact elimination already answers every algebraic nullity and rank in this review. `docs/evidence/pathion-kernel-map/README.md:13-29` records both the query lower-bound context and exact `cd_core`/python-flint certification. Retained IBM, Tuna-17, and Ascella runs measure selector contrasts, block visibilities, sign networks, or noise (`:35-49`); they do not certify an F_p matrix rank.

A bounded QPU proposal could block-encode a normalized real embedding of a sparse candidate matrix, run singular-value transformation or phase estimation, and estimate weight below a registered threshold. The output may rank candidate supports or seed a classical sparse-kernel search. The algorithm needs a proved singular-value gap, expensive state preparation, and enough samples to distinguish nullity one; it therefore offers no advantage for the 17-24-generator finite-field cells. Exact CPU/GPU elimination must certify every candidate.

Any algebraic hardware probe must treat `a -> L_a` as a linear encoding only, include the mutation test, measure the `+,-,-,+` arms, and decide against a null arm. Photonic mode selection can cheaply screen sign-network candidates, while Tuna-17/IQM/Heron can test circuit-depth or noise hypotheses; each provider run still needs a separately approved case. No retained result shows a quantum-computational question that classical exact arithmetic cannot already answer, so this review recommends no new provider job for rank certification.

## Conjectures and cross-connections

- **Parity box.** Conjecture that the last layer is a character-graded copy of `H^0(P^1 x P^1,O(2d,2d))`, dimension `(2d+1)^2`, equivalently the degree-d piece of the Segre-Veronese section ring. Falsifier: a last layer with another dimension, block split, or multiplication table. Cheapest test: recover multiplication maps between successive last layers and test Segre-Veronese quadratic relations; dimension matching alone is insufficient.
- **X closing order.** Conjecture a two-step valuation semigroup with alternating increments three and four, producing `floor(7d/2)+1`. Falsifier: X d=6 closes away from N=22, misses the N=20/21 plateau, or has another final jump. Cheapest test: the preregistered N=20,21,22 cells.
- **Iso local route.** Search the point-blowup base locus for a plane family whose Jacobian rank equals the five-dimensional affine cone (`a5-exceptional-fiber-findings.md:439-442`). A missed component or rank deficit falsifies the route.
- **E8-bar local route.** K2 has components B9 and V (`structure/README.md:78-82`). A proof must place a point and rank-equal local family on every relevant component; one family on only one component is insufficient.
- **Connection status.** Rocq half folding proves a kernel-product symmetry. Finite-field fiber Hilbert values are separate computations. Hardware N-hat values are physical measurements of noisy encodings. Character gradings appear in all three, but no theorem derives the fiber last-jump law or a hardware bias from the folding theorem. That proposed unification remains a hypothesis.

## Run plan for every open or stalled ledger row

| Rows | Computation and acceptance | Cost, peak memory, host, ordering |
|---|---|---|
| A5-016 | Search remaining E8-bar to VB blowup charts for a dominant degree-three component; require exact component containment and generic rank. | Minutes to hours, below 4 GiB; laptop. Parallelize independent charts only through the repository pool. |
| A5-029 | Compute exact kernel-plane limits along the registered arcs and certify generic nullity eight. | Minutes to hours, below 4 GiB; laptop. Run after chart inputs are fixed. |
| A5-073 | Do not repeat the unchanged global radical. The retained run spent 86,400 s without a radical; closure-pullback already decides the components. | No listed free host should repeat it. Mark the operational claim stalled or superseded; a redesigned bounded formulation needs its own estimate. |
| A5-083, A5-089, A5-095, A5-101 | Replace direct E8-bar N-plus/minus degree-six ranks with local arc/component proofs. A direct cell is forecast at about 230 GiB and two weeks (`forecasts/trends-2026-11-06.md:243-249`). | Laptop, OCI A1, and Kaggle cannot finish. A paid >=256 GiB host is technically possible but unjustified. Sign transport reduces four cells to one cell per prime, but does not fix cost. |
| A5-107 | E8-bar to VB, p=32009, degree six: probe closing N, then run one exact cell to 420. | 1.4-2.1 GiB preflight, under 5 GiB, hours to 10 h; laptop or Kaggle CPU. |
| A5-111 | E8-bar to VB, p=32029, degree four: replay the proven first-prime route at the second prime and require 155. | Below 5 GiB, within a Kaggle session or laptop shift; run before p=32029 degree six. |
| A5-113 | E8-bar to VB, p=32029, degree six: run only after A5-111 and a first-prime closing-order probe. | Under 5 GiB, hours to 10 h; laptop or Kaggle CPU. Do not parallelize both primes before p=32009 establishes the order. |
| A5-155, A5-167 | X-plus/minus at p=32009: run X-minus N=20,21,22 and transport X-minus to X-plus with the sign witness. Require the preregistered 496,496,665 ranks and blocks. | 4.3-8.2 GiB preflight, under 10 GiB, about one hour per closing cell; laptop or Kaggle CPU. Run the three N cells sequentially. |
| A5-161, A5-173 | Repeat only the decisive X-minus cells at p=32029 after the first prime, then transport to X-plus. | Under 10 GiB, about one hour per cell; laptop or Kaggle CPU. The two primes need not run in parallel. |
| A5-202 | Preregister a fresh-seed Ascella test of the shifter-map increment over the frozen efficiency-only model. | Provider action: host, shots, seconds, credits, pause limits, and approval belong in a separate written case. No execution is authorized here. |
| A5-237 | Retire the unchanged codimension-five W8 slice; it timed out at 900 s/8 GiB, and the C30 local proof now answers its decision purpose. | No listed host should repeat it unchanged. Mark superseded, or redesign the algebra before estimating another run. |
| A5-242 | Preregister a full-map rerun with the orientation phase moved to another data qubit and correction across planned character contrasts. | Provider action on Heron only after quota and a written case specify shots, seconds, and credits. No execution is authorized here. |

OCI A1 adds value only to small, single-threaded Singular chart work. Kaggle CPU can carry the VB and X cells within its roughly 30 GiB/12 h envelope. Separate T4 memories do not solve W8. No free listed host can finish the direct E8 degree-six cells or current W8 degree-six engine test. Paid cloud should follow, not precede, the W8 engine acceptance rerun.

## Replays performed

- `ledger.py --check`: exit 0, silent. The exact registry command from the brief: exit 0, `registry matches`.
- Fresh `witnesses.py` output in `/tmp`: six sign-isomorphism rows, all `ok`, byte-equal to retained rows.
- Rocq 9.3.0/OCaml 5.5.1, with `OCAMLRUNPARAM=s=256k` so the runtime stayed under the required 4 GiB address-space cap: `compile_kernel_assumptions_pass CdHalfFold` and `compile_kernel_assumptions_pass CdTwistedProduct`.
- `nhat_bias.py --check` and both self-test modes: retained result reproduced and both tests passed.
- The committed HEAD version of `nhat_spectral.py`, extracted with its tracked inputs to `/tmp`: `result_spectral.json` reproduced and normal and optimized self-tests passed. These checks do not calibrate the rejected chi-square tail.
- All commands ran at `nice -n 19`, under `prlimit --as=4294967296`, with the mandated Python and `GLIBC_TUNABLES`; each finished within five minutes. The final `git diff --check origin/main...HEAD` reported pre-existing whitespace in two `w8-engine-map/logs/*.prof.txt` files and `docs/evidence/cd-half-fold/kernel.txt`; this report changes none of those files.

## Fetched sources

None. The review opened only repository sources and existing documents-repository transcriptions.
