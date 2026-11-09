# Deep review (grok) of the A5 fiber claims at HEAD d21e9a76e

Reviewer grok. Worktree `docs/a5-32d-findings`, HEAD `d21e9a76ec39967a5256282c1277dc96fe17d937`. The brief's pin `3d928b1a6` is an ancestor (`git merge-base --is-ancestor` exit 0). This file is the only write. No QRNG index from 500 upward was used. Ledger at this HEAD: 242 rows, proved 31, certified 87, survives 54, refuted 44, open 11, stalled 2, rejected 6, superseded 7 (status column, read-only). `build_registry.py` was not run. Rocq was not replayed. `witnesses.py` was not re-executed.

Field: commutative algebra of fiber cones over F_p, with a machine-checked fragment of Cayley–Dickson linear algebra and a hardware-bias audit. A ledger row is a pointer. Status words below are proved, computed, measured, or hypothesis.

## Verdict

The load-bearing theorems and the certified Hilbert numbers survive. A5-066 is a proof over F_32009 and F_32029. The sign transports, the X degree-4 and degree-6 ranks, and Iso h_6 = 2422 are certified by records whose headers match the canonical inputs. The half-fold and the twisted-product exchange are the statements the Rocq files print. What does not survive is one identification inside A5-244, and two write-ups that treat an unrun plateau as measured. Nothing in the opened literature computes these fiber cones, this jump split, or the N_hat identity. No QPU algorithm is proposed: classical linear algebra already computes the nullities those devices estimate.

## Findings, by consequence

### 1. A5-244's box sentence is false. The numerical predictor survives. (computed)

The claim text (ledger.tsv A5-244) says the last jump equals (2d+1)^2 and "splits by character block like the parity classes of the box k[x, y]/(x^{2d+1}, y^{2d+1})". The same sentence is in `docs/notes/topics/a5-exceptional-fiber-findings.md` line 353.

Monomials in that box are x^a y^b with 0 <= a,b <= 2d. The four parity classes have sizes (d+1)^2, d(d+1), d(d+1), d^2. At d = 6 that is 49, 42, 42, 36. The measured X- jump at p = 32009 is 49, 42, 39, 39 (`xm-lown/README.md` lines 58-65: r_20 = r_21 = 496 with blocks 132/136/114/114, r_22 = 665 with 181/178/153/153). Those two 4-tuples are different. The closed form that does match is `forecasts/trends-2026-11-06.md` line 130: block 0 is (2*floor(d/2)+1)^2, block 1 is d(d+1), blocks 2 and 3 split the rest. At d = 6 that is 49, 42, 39, 39. Line 133 of the same file already says no ring was identified, and it calls (2d+1)^2 the Hilbert function of P^1 x P^1 under O(2,2). h^0(O(a,b)) = (a+1)(b+1), so O(2,2) has 9 sections. O(2d,2d) has (2d+1)^2 sections, which matches the sum of the jump and none of the block split.

The out-of-sample cells stand. Iso d = 6 met r_18 = 2253 and the jump 169 (`iso-d6-n19-laptop/README.md`, corrected at 0e49570d3 so N = 18 is recorded as measured). X- d = 6 met the preregistered blocks at p = 32009. Status of A5-244 stays survives, as a predictor. It is not a theorem and it is not a ring.

Resolution. Delete "like the parity classes of the box k[x, y]/(x^{2d+1}, y^{2d+1})" from the A5-244 claim and from findings-note line 353. Keep the closed form of trends line 130. Leave the status. Do not name O(2,2) as the ring of the jump.

### 2. The second-prime plateau is unmeasured, and two texts say the ladder is the same. (measured)

`xm-lown/xm6.events` records N = 22, 21, and 20 at p = 32009, all exit 0. `xm-lown/xm6p2.events` records only N = 22 and N = 21 at p = 32029. There is no `xmnm_d6_n20_p32029.json`.

A5-173 (certified, this HEAD) says r_22 = 665 with blocks 181/178/153/153 and r_21 = 496, and it points at the p = 32009 ladder for the comparison. That certifies h_6 = 665. It does not certify r_20 at p = 32029. A5-161 transports that h_6 to X+. Findings-note lines 431-434 say the preregistered ladder met, including r_20 = r_21 = 496, and then "The same ladder holds at p = 32029 (A5-173, A5-161)." `xm-lown/README.md` lines 67-69 call r_21 and r_22 "the same ladder". The plateau clause of the closing-order hypothesis is a p = 32009 measurement.

JSON headers re-hashed against the canonical `.sing` files, all match: X- d = 6 N = 22 p = 32009 r = 665 engine `7849cbc71ccf1787` header `f437c9ea4f9e8861`; N = 20 p = 32009 r = 496 same header; N = 22 p = 32029 r = 665 header `98de6225b05399df`; N = 21 p = 32029 r = 496 same header. Block r_N values are 181/178/153/153 and 132/136/114/114 as claimed.

Resolution. In findings-note lines 431-434 and README lines 67-69, state r_21 and r_22 at p = 32029, and keep r_20 = r_21 on p = 32009. Add one clause to the A5-244 basis with that prime split. Do not change A5-167, A5-173, A5-155, or A5-161.

### 3. A5-066 holds over the two primes. Step 4's parenthetical does not prove the count. (proved, with one computed repair)

A5-066 claims V(K2 : P) = C30 lies in the fiber, equivalently F(I) = k[y]/K2, over F_32009 and F_32029. The chain that was re-read is `structure/c30-bounded/README.md` steps 1-8. Step 2 identifies the blowups of I' and of s^2 I' by the Rees algebras, and it says s^2 is not a unit on {s = 0}. Step 8 is the projective Nullstellensatz once K2 is radical (A5-061: squarefree degree-50 eliminant equal to vdim, on eight sections per prime) and saturated. The five planes and the L0 logs are the retained tests of the Jacobian, the Newton determinant, and the vanishing of J and the 24 generators on the chart curve. Scope is those two primes and those points. Characteristic 0 is not claimed.

Step 4, lines 64-66, concludes dim I^n / m I^n = binom(n+3, 3) because a product x^a y^b z^c w^(c+2e) "never lies in m I^n (the w-exponent minus the z-exponent stays even)". Parity of w - z is unchanged by multiplication by x or by y. The parenthetical does not exclude those multiplications. The count is the number of tuples a+b+c+e = n, which is what affine independence of the four exponent vectors gives. Singular, global dp, recomputed the minimal basis of I = (x, y, s*v, v^2):

`nice -n 19 prlimit --as=4294967296 timeout 90 /usr/bin/Singular -q --no-rc <scratch>/fibercone.sing < /dev/null`

At p = 32009, n = 1..6 gives mu = binom = 4, 10, 20, 35, 56, 84, each difference 0. In characteristic 2, n = 1..4 gives 4, 10, 20, 35. Singular warned that `mu` and `bin` are redefined inside the loop. That check is the monomial count. It is not a lift of A5-066.

HEAD d21e9a76e fills a blank counter. `templates/base.sing` lines 6-7 and 11 set `divBad` when `q*s^2` differs from the pulled-back generator, and the off-origin controls now print 0 at both primes (`c30-control-base-p32009.result`, `c30-control-base-p32029.result`). Exact division holds on those controls. The label is the failure count.

What would break A5-066: a generator or J nonzero on the symbolic (b, c) curve (the L0 logs say 0 of 24); a Newton or (v4, v5) determinant zero on all of the sampled U; 1-jet rank below 2; differential rank below 6 on a Zariski-open set; K2 not radical; a degree-d membership outside K2. None of those is in the retained failures. Multiplicity 50 is inherited from the radicality sections, not recomputed in this review.

Resolution. Add one sentence to step 4: the monomials with a+b+c+e = n are a basis of I^n / m I^n because the four exponent vectors are affinely independent, and the parity sentence is only the exclusion of multiplication by z or w. Do not change the status of A5-066.

### 4. The certified transports and the named ranks match their inputs. (certified)

`witnesses.py` `sign_iso` (lines 76-109) compares each J and G generator of the destination header with the same-index generator of the source after the listed sign flips, and accepts a global sign per generator. A diagonal of units fixes the origin and the fiber grading. `ok` is true when no sign is 0 and the K2 mutual remainders are absent or [0, 0] (line 102). `build_registry.py` `transport` (lines 255-283) copies a certified degree across an ok witness and refuses unequal K2 counts.

`witnesses.jsonl` lines 13-14: E8-bar N- to N+ at both primes, flip t8,t9, no zero signs, `k2_mutual_remainders` [0, 0], ok. Lines 15-16: X- to X+, flip t9, no zero signs; K2 remainders null at 32009 and [0, 0] at 32029. Lines 17-18: W8, flip t9, no zero signs, K2 files absent. A missing K2 file is a missing consistency check of stored relation files. The presentation isomorphism is the generator comparison. W8 in every degree does not rest on that missing file: A5-008 and A5-066, carried by the t9 automorphism A5-013.

Re-hashed rank JSON, engine `7849cbc71ccf1787`, header equal to sha256 of the canonical `.sing` truncated to 16 hex:

- Iso h_6: `isonm_d6_n19_p32009.json` and `..._p32029.json`, prime 32009 and 32029, r_N = 2422, blocks 632/610/590/590, headers `1f1757d55751f1e3` and `28c3c473369c6eda`. A5-119, A5-125.
- X degree 4 at 32029: `d4-p2/xmnm_d4_n15_p32029.json`, r_N = 240, blocks 68/66/53/53, header `98de6225b05399df`. A5-171, transported to A5-159.
- E8-bar h_5: `n18-laptop/e8nm_d5_n18_p32009.json` and `..._p32029.json`, r_N = 952, blocks 215/197/270/270, headers `7d3521d0e8026e6f` and `48bdcbe0fa17d04c`. N+ is the transport of lines 13-14 (A5-082, A5-088).

Resolution. None for these rows. Optional later: store the X- p = 32009 K2 pair so line 15 has the same remainder check as line 16.

### 5. Half-fold and twisted product match the printed statements. (proved / computed)

`proofs/CdHalfFold.v` lines 43-50 leave the cross-operand fold open in the file. Lines 239-250: `has_dim` of ker L_(a,0) and of ker L_(0,b) is twice `has_dim` of the lower kernel. The dimension conclusion needs the `has_dim` hypothesis (line 161). Retained `docs/evidence/cd-half-fold/assumptions.txt` lists only `ClassicalDedekindReals.sig_forall_dec` and `FunctionalExtensionality.functional_extensionality_dep`. Not recompiled this session. The `.v` files are not in the diff after `b790fa79c`.

`proofs/CdTwistedProduct.v` `W8_ideal_exchange` (lines 213-226) is an ideal-membership equivalence over any commutative ring with i^2 = -1 and a chosen inverse of 2. The Zmod 5 instance discharges those two lemmas by `vm_compute` (lines 243-246). Dimension, degree, and the Hilbert numerator are Singular computations in the evidence directory, not Rocq conclusions. A5-235 refutes the fiber ring as a tensor product of the halves (Macaulay bound versus h_3 >= 551). A5-222 refutes equality of the A4-restricted ideal with the Pfaffian ideal as ideals; the radicals agree. A5-227 survives on the generic stratum and keeps the global pair law refuted.

Resolution. None. Do not cite the cross-operand fold as proved in this repository. The every-operand development attributed to gororoba-open was not opened.

### 6. N_hat rows stand as written. Do not promote the orientation sentence. (proved / hypothesis)

A5-228 is the algebra identity, with the ledger's exact rational residual 0 on the retained units. That residual was not recomputed here. A5-229: an all-aligned block reads N_hat = 4. A5-231 refutes bin-independence of the full map. A5-243 is an enumeration of 252 nullity-12 operands. A5-076 refutes a block-encoded HHL/QSVT pipeline as an exact F_p rank (amplitude output, singular L_a). A5-075 is the counting cost.

A5-242 stays open. Its basis records paired t statistics and calls the orientation-qubit story a hypothesis formed after the replicas. `result_spectral.json` was not re-extracted. A Hotelling or binomial summary that treats blocks as independent overstates the evidence if the blocks share a device mode. The per-run Fisher combinations already in the nhat README are the summary to keep.

Resolution. Leave A5-242 open. Do not schedule a new full-map hardware run from this review. Its falsifier is a new run, which needs a written case and the user's approval.

### 7. Stale rows. The ranks they point at are already certified or proved.

- A5-006 still says X survives through degree 5, falsifier "degree 6". Degree 6 is certified (A5-167, A5-173). Resolution: supersede by those rows, or move the falsifier to characteristic 0.
- A5-007 still stops Iso at degree 5. A5-119 and A5-125 certify degree 6. Same resolution.
- A5-012 still says survives, while its own basis says A5-066 shows the condition. Resolution: mark proved, or superseded by A5-008 and A5-066.
- A5-237 (global slice, exit 124) is superseded by A5-066. Do not rerun.
- A5-073 (direct radical, 86400 s, exit 124) is superseded by the closure-pullback route. Do not rerun.
- A5-131, A5-137, A5-143, A5-149 are proved h_6 = 8624 by A5-066, and they say `claims.json` keeps the degree open because the registry stores rank bounds. That is roadmap item 5. Leave the ledger status. A rank below 8624 would not falsify h_6.

## Prior art

Opened in full enough to cite a theorem:

- Biss, Dugger, Isaksen, "Large annihilators in Cayley-Dickson algebras", arXiv math/0511691v1, https://arxiv.org/pdf/math/0511691v1. Section 9, PDF page 15: Lemma 9.2 (xy = 0 iff x* y = 0 iff x y* = 0) and Corollary 9.3 (xy = 0 iff yx = 0). The section says these had been known for about a decade, including Moreno and Khalil–Yiu. The half-fold of a half-operand is that kernel statement plus a dimension hypothesis, machine-checked here. Section 8's associator dimensions are a different calculation, and they are the cross-operand case this repository leaves open.
- D'Cruz, Raghavan, Verma, "Cohen-Macaulay fiber cones", arXiv math/0212119v1, https://arxiv.org/pdf/math/0212119v1. Theorem 2.1, page 2: for any ideal of a local ring and any minimal reduction, F(I) is Cohen-Macaulay if and only if the Hilbert series equals the stated sum of lengths through the reduction number, if and only if the multiplicity equals that sum. The findings note's citation of Theorem 2.1 matches the theorem as opened. The theorem does not compute these series.

Abstracts only, no page and no internal theorem: Moreno, q-alg/9710013v1 and math/0512517v1; de Marrais, math/0011260v1 and math/0207003v2; Cawagas, Carrascal, Bautista, Sta. Maria, Urrutia, Nobles, arXiv 0907.2047v3. They describe zero-divisors, Stiefel-type constructions, box-kites, and the 32-dimensional subalgebra lattice.

Known, from those texts: annihilators of half-operands, and a general Cohen-Macaulay criterion for fiber cones. New, relative to the texts opened here: the A5 stratum fiber cones and their Hilbert functions, the sign transport, the last-jump split, the closing orders, and the N_hat identity. No opened theorem hands over F(I) = k[y]/K2 for these ideals.

Not opened, so not cited: `<workspace>/AGENTS.md`; gororoba-open, including any `CDPureDoublingKernel` development; gororoba-documents-public, private, and technical, and their TAXONOMY.md and manifest.tsv; OpenAlex (auth failed); zbMATH (not called); Northcott–Rees 1954; the rest of the prior-art list in the findings note (Skiouris, Kustin–Polini–Ulrich, Corso–Ghezzi–Polini–Ulrich, Cooper–Price, Ansaldi et al., Kumar–Venugopal, Ghorpade–Krattenthaler, Jeffries–Montaño–Varbaro, Zhilina, Chan–Dokovic). `docs/design/gpu-exact-modular-linear-algebra.md` was read through line 44.

## Engine levers for degree 6

Acceptance test, already in roadmap item 4: a W8 degree-4 rerun with byte-equal ranks, after the preflight is fixed. This review did not launch it.

Measured coupling: `w8-engine-map/README.md` lines 75-84. At d = 4 every block alone falls short of the full rank_W. L is independent of the block set (line 92).

Forecast, labeled hypothesis in the map, lines 92-104: L = 103.3 GiB, products peak 129 GiB, closure 139-160 GiB at rho = 0.67 and 191-223 GiB at rho = 0.96, wall 18-27 h. Predicted blocks 2198/2170/2128/2128. The d = 3 and d = 4 ranks equal the Hilbert function (lines 110-114). The d = 6 memory and time are extrapolated.

- (a) Already the representation. Module lines 3-10 and `extend_products` (lines 365-372) truncate each product to degree below N. No further saving is claimed.
- (b) uint16 storage is valid for these primes while `exact_mod_matmul` (lines 174-178) still refuses an inner dimension with inner*(p-1)^2 >= 2^53, and p < 2^15. A 4x cut of a float64 L is an arithmetic observation about 103.3 GiB, untested. Acceptance remains the degree-4 rerun.
- (c) Free columns are already the marshaling term (map line 96, rows x free x 121 B).
- (d) In-place update and chunked `new` is the map's own hypothesis (lines 85-86, 98). One block becomes 17-25 GiB plus chunks. Products still need L = 103 GiB.
- (e) Generators are built one at a time (map lines 70-71). `extend_products` still returns every multiplied jet of that generator. Streaming L by degree level is the CPU lever aimed at the 103 GiB peak. No per-level fraction is stated, because none was measured.
- (f) 129 GiB does not fit a 16 GiB or 12 GiB GPU. The design note, lines 19-42, measures INT8 tensor-core products exact at 62.8-68.6 TOP/s on the build-host RTX 4070 Ti, HMM without migration about 45 times slower (28.6 ms against 0.6 ms at n = 2048), and with `uvm_disable_sam_migration=0` an n = 4096 FP32 GEMM at 27.6 against 28.1 TFLOP/s resident. A GPU path is chunked GEMM of panels that fit, under the same exactness guard. It does not store the closure basis. A5-052: a GPU does not shorten the Singular export, which dominated quotient-mode time. The rest of the design note was not read. A Kaggle T4 session needs a written case and approval. None is proposed.
- (g) The findings note, lines 367-370, retires the global elimination formulations that were tried. A5-073 and A5-237 are the stalled rows. A5-174 and A5-176 refute Iso chart saturations inside a few GB. M2 `specialFiber`, a Rees Gröbner basis, and msolve/F4 are not a new plan. The C30 plane is the formulation that finished (45-52 s, 26 MiB, A5-236).

Preflight defects, already in the map lines 117-120, confirmed in the engine: `walk_temporaries` at line 1086 is `2 * 8 * gen_blocks // len(blocks)`, which is half of `generator_blocks` when there are four blocks, against 0.10 L measured; `echelon_bases` at line 1088 is two full squares, which is the rank = cols assumption. Fix those before any W8 degree-6 run.

E8 degree 6 has no measurement. The neighbor that was read is degree 5, N = 18, p = 32009: wall 118,426.8 s, peak RSS 37,072,856 KiB (35.4 GiB), and the write-up says the Singular standard basis dominates (`n18-laptop/README.md` lines 5 and 36). The same peak appears at p = 32029. X- degree 6 (3.8-5.7 GiB, 676-1760 s, 15 generators) is too small to quote as the E8 cost.

## Quantum hardware

Classical linear algebra already computes every Cayley–Dickson left nullity the retained hardware runs estimate. L_a is a linear encoding. An approximate singular value does not certify a Hilbert function of a fiber cone, and the fiber-cone matrices do not fit Ascella, Belenos, Tuna-17, Garnet, or a Heron device. A5-076 closes HHL/QSVT as an exact F_p rank. N_hat is an instrument bias of a nullity the algebra already knows (A5-228, A5-229). It does not seed a modular elimination. No new QPU experiment is proposed. A5-202 stays a question about a retained Ascella fit.

## Conjectures, each with a falsifier

Nothing is posited as a theorem.

- The ring of the jump. Trends line 133 records that none was identified. O(2d, 2d) matches the sum. The parity box does not match the blocks (finding 1). Falsifier of the closed form: one block split other than line 130. Cheapest remaining test is a new degree, not a reinterpretation of d = 6.
- Closing orders. Iso and W8 close at N = 3d+1 on the measured cells, including Iso d = 6 at N = 19 and not at N = 18. X- and E8-bar match floor(7d/2)+1 with a one-step plateau at even d through the cells that were run. E8-bar's jumps are a different sequence (findings note lines 455-459: 55 at d = 4, 81 at d = 5). Falsifier: E8-bar d = 6 closing at an N other than 22, or X- d = 7 closing at an N other than 25. The untested plateau at p = 32029 is an X- N = 20 run of the same class as the existing N = 21 run (about 1100 s and 4.7 GiB). It does not change h_6. W8 N = 19 tests the engine against a value A5-066 already proved.
- Iso by the C30 route. Roadmap item 3: V(K2) is prime of degree 23 and projective dimension 4, so one full-dimensional family in E0 would give E0 = V(K2) by the same sandwich. That primality was not re-derived here. Falsifier: Jacobian rank below the cone dimension at every point of a sample, or a base locus that misses V(K2). Cheapest test: a plane script on the Iso point blowup, the shape of `c30_gen.py`. A global saturation is the computation that already died (A5-174, A5-176).
- E8-bar by the same route. Findings note lines 364-366: the fiber is not reduced, and V(K2) is not equidimensional, minimal primes (4, 11) and (3, 4). One plane family does not decide F(I) = k[y]/K2. A5-016 (the degree-3 component of E8-bar to VB) stays an arc search. Chart 5 returned in 359 s and missed that component (roadmap item 6).

## Connections

Proved: the half-fold under `has_dim`, and `W8_ideal_exchange`. They do not imply a tensor product of fiber rings (A5-235, refuted) and they do not compute a Hilbert function.

Computed at F_p: the certified ranks, the K2 Hilbert functions used as upper bounds, and the C30 plane arithmetic. Proved at the two primes, from that arithmetic plus the Nullstellensatz: W8, F(I) = k[y]/K2 in every degree.

Hypothesis: the last-jump closed form, and the floor(7d/2)+1 closing order.

The N_hat identity is an algebra identity about a biased estimator. It is not an input to the modular elimination.

## Run plan for the open and stalled rows

Hosts named by the brief. Peak figures below are retained measurements or the engine map's labeled extrapolations. No new GiB figure is invented.

| Row | What | Cost evidence | Host |
|---|---|---|---|
| A5-083, A5-095 | E8-bar to N- and N+, h_6 <= 1666, p = 32009. Compute N- only; N+ waits on the witness of line 13. | d = 5 already 35.4 GiB and 118,427 s, std-dominated. d = 6 unmeasured. | Not the laptop (36 GiB cap already met at d = 5), not OCI (11 GiB), not Kaggle CPU (about 30 GB, 12 h) on this evidence. A paid cloud VM is the only candidate, and only after a preflight that is not the broken square-basis estimator. |
| A5-089, A5-101 | The same at p = 32029. Independent of the first prime. | Same d = 5 peak, 93,763 s at this prime (`n18-laptop/README.md`). | Same constraint. The two primes can run on two paid VMs at once. They must not share one 36 GiB machine. |
| A5-111 | E8-bar to VB, h_4 <= 155 at p = 32029. | No VB degree-4 timing was read this session. | Unassigned until a preflight on the real engine exists. It is the smallest open rank. |
| A5-107, A5-113 | VB h_6 <= 420. | Unsized. 420 against E8's 1666 is not a memory model. | Unassigned. Do not start from the X- degree-6 wall times. |
| A5-016 | Arc into the degree-3 component. | Chart 5: 359 s, one ring, missed the component. | Laptop or OCI, Singular, charts not yet tried (t7 = 1, k^2+3 = 0, singular points). |
| A5-029 | Kernel-plane limits along arcs. | Not sized. Classical `cd_core`. | Laptop, no provider. |
| A5-202 | Ascella shifter map. | Retained fit. | No new job. |
| A5-242 | Orientation-qubit hypothesis. | Needs a new full map. | Do not submit. |
| A5-073, A5-237 | Stalled global computations. | Already timed out. | Supersede. Do not rerun. |

Parallel with the E8 jobs off the laptop: the Iso plane probe (hypothesis on cost: one C30 plane was 45-52 s and 26 MiB; a global saturation is the run that does not finish), the documentation patches in findings 1, 2, and 7, and an optional X- N = 20 at p = 32029 (about 5 GiB and 20 minutes, not on the critical path). The laptop runs at most one memory-heavy rank.

What no host on the list can finish, on present evidence: the W8 degree-6 rank at 129-223 GiB and 18-27 h, and an E8 degree-6 quotient standard basis whose degree-5 neighbor already used 35.4 GiB and about 33 h. A 252 GB VM might hold the low-rho W8 estimate and might trip the 225 GiB guard at the ceiling. Do not buy it until the preflight at engine lines 1086 and 1088 is fixed and the degree-4 byte-equal rerun exists. W8 N = 19 is an engine test of a proved value, not the critical path. The critical path is E8 h_6 on paid cloud, N- only, and the Iso plane probe.

Not run, so not cited as clean: `git diff --check`, `build_registry.py --check`, the Rocq replay, `tests/gororoba_quantum/test_nhat_bias.py`, `test_nhat_spectral.py`.

## Fetched sources

- https://arxiv.org/pdf/math/0511691v1 — Biss, Dugger, Isaksen, PDF opened, section 9 page 15 and the section 8 associator formulas.
- https://arxiv.org/pdf/math/0212119v1 — D'Cruz, Raghavan, Verma, PDF opened through Theorem 2.1 on page 2.
- Abstracts only: https://arxiv.org/abs/q-alg/9710013v1, https://arxiv.org/abs/math/0512517v1, https://arxiv.org/abs/math/0011260v1, https://arxiv.org/abs/math/0207003v2, https://arxiv.org/abs/0907.2047v3.

Could not open: the workspace AGENTS.md, gororoba-open, and the three documents repositories (session confined to this worktree); OpenAlex (auth); zbMATH (not called); Northcott–Rees 1954; the findings-note prior-art PDFs listed above.
