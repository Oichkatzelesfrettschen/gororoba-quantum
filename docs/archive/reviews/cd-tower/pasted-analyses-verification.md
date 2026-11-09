# Verification of the pasted Cayley-Dickson tower analyses

Subject: [`pasted-analyses.md`](pasted-analyses.md) (two unreviewed model analyses). Checked on branch
`a5/ledger-audit-and-engine-v12` at commit 3dc4e47ff against `gororoba_quantum/cd_core.py` (the specification), the
evidence bundles and the design doc named in each row. Python 3.14.9, numpy 2.5.4. Every computation ran once,
read-only, under 10 minutes and 4 GiB; the scripts s1 to s5 are inline below and each printed the quoted output.
Paths are relative to the worktree. Rank checks use Gauss-Jordan mod 1000003 on integer matrices (a rank over F_p
cannot exceed the rational rank; the 168/168/252 histogram agrees with the repository's own record).

Conventions: An index pair is an unordered pair {i,j} of nonzero indices; "ordered pairs of index pairs" (the convention of
`docs/notes/topics/kaplansky-mechanisms-cayley-dickson.md:49-55`) doubles every unordered count. "Ordered distinct
imaginary triples" is `cd_core.classify_octonion_triples` (`cd_core.py:178-187`) at every level.

## Claim table

Verdicts: holds, wrong, partly, cannot check, hypothesis. Script names refer to the Scripts section.

| # | Claim (pasted) | Verdict | Evidence | Corrected statement |
|---|---|---|---|---|
| 1 | The tower is an exact integer structure; basis product is a sign times e_(p xor q) | holds | `cd_multiply_exact` `cd_core.py:111-121` uses Fractions; `basis_mul` in `docs/evidence/cd-tower-basis-sign/README.md:12-20` | none |
| 2 | Doubling (a,b)(c,d) = (ac - conj(d)b, da + b conj(c)), conj(a,b) = (conj a, -b) | holds | `cd_core.py:3-5`; s4 `doubling` recursion: 0 mismatches against `cd_sign` for k = 1..6 | none |
| 3 | The functor is defined and proved over any commutative ring or integral domain (Z, Q, R, C, F_p) in Rocq | partly | `docs/evidence/cd-tower-domain/README.md:3-19`: signature `OrderedDomain` (order `le`, nonnegative sums, no zero divisors, 1 <> 0); instances `ZTower`, `RTower`, `RField`; `Zmod5` appears only in `cd-twisted-product` | Proved over an ordered integral domain, instantiated at Z and R. The doubling formula itself is meaningful over any commutative ring; the proofs are not stated for C or F_p |
| 4 | Every A_k is a twisted group algebra R^sigma[Z_2^k] with e_p e_q = sigma(p,q) e_(p xor q) | partly | basis table holds (`basis_mul`, row 1); the product is not associative for k >= 3 (row 5) | A cochain-twisted (quasi-associative) group algebra; sigma defines the multiplication table but is not a group 2-cocycle |
| 5 | sigma is an integer 2-cocycle (the Albuquerque-Majid 2-cocycle) | wrong | s3: identity sigma(p,q)sigma(p^q,r) = sigma(q,r)sigma(p,q^r) fails on 0/64, 168/512, 1848/4096, 15960/32768 triples at D = 4, 8, 16, 32 (the non-associating triples); `docs/notes/open_gororoba_survey.md:21-23` states the same; `docs/notes/prior_work_synthesis.md:32` (associator is the coboundary of a 2-cochain) | sigma is a 2-cochain whose coboundary is the associator phase; it is a cocycle only for D <= 4 |
| 6 | Evidence directories cd-tower-domain, cd-tower-basis-sign, cd-associator-anf, cd-twisted-product, a5-w8-twisted-product exist | holds | `ls docs/evidence/` lists all five (paths need the `docs/` prefix) | none |
| 7 | sigma_(k+1)(p,q) = (-1)^parity(p_hi & q_lo) sigma_k(p_lo xor p_hi, q_lo xor q_hi) | wrong | s4 `literal` (hi = top index bit, lo = rest): 1, 6, 28, 124, 520, 2104 mismatching cells of 4..4096 for k = 1..6; ANF degree of [sigma_k = -1] in the 2k index bits is k (s4: 2,3,4,5 for k = 2..5), so no recursion of the form (parity of an AND of index bits) times sigma_k of XOR-linear arguments can match: its degree is at most max(2, k), while degree k+1 is needed | The correct recursion (s4 `doubling`, 0 mismatches) swaps arguments and carries a conj factor (-1)^[q_lo != 0]; Rocq proves the unrolled `cd_sign` loop (`cd_sign_loop_sigma`, `cd-tower-basis-sign/README.md:19`), not a parity form; its degree comes from the conditional argument swap, which is not linear |
| 8 | `cd_core.py:56-85` listing of `cd_sign` | holds | s4 `pasted_cd_sign`: 0 mismatches vs `cd_sign` for D = 2..64 | The real function is `cd_core.py:56-84` and adds `_dimension`/`_index` validation (58-60) |
| 9 | The recursion reduces the tower to shifts, masks and popcount parity | hypothesis | `cd_sign` (`cd_core.py:63-83`) uses comparisons and subtraction, no popcount; Boolean degree k (row 7) | Becomes a claim if a closed form with its degree is proved; `docs/notes/cd_phase_degree.md` holds the degree results |
| 10 | IEEE 754 add and multiply are non-associative | holds | standard property; s3 shows float associator 2.2e-16 (D = 2), 5.6e-16 (D = 4) on random inputs in [0,1) | none |
| 11 | D <= 4 is algebraically associative and shows only roundoff artifacts in float | holds | s1: 0 non-associating triples at D = 4; s3 values in row 10 | none |
| 12 | D = 8 is alternative; float roundoff breaks it | holds | s3: max float [x,x,y] = 1.8e-15 at D = 8 (algebraic value 0); `cd_multiply` error bound `cd_core.py:87-94` | none |
| 13 | At D >= 16 exact zero divisors degrade into numerical zero divisors under catastrophic cancellation | partly | s3: (e1+e10)(e4-e15) in float64 gives max residual 0.0 at scales 1/sqrt2 and 0.1 (paired terms are the same product up to sign); no repository measurement of near-zero-divisor behavior | Two-blade zero divisors stay exact in float64; degradation is a statement about generic near-zero-divisor operands and is unmeasured here |
| 14 | float64 matmul is exact when k (p-1)^2 < 2^53 | holds | guard `docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v12.py:63-65, 184-187, 733-734`; every partial sum is an integer below 2^53 | The bound is sufficient, not necessary (s3: numpy dot at k = 8,796,093 happens to be exact) |
| 15 | For p = 32009 the inner dimension may reach about 8,796,093; (p-1)^2 about 1.024e9 | wrong | s4: (p-1)^2 = 1,024,512,064; 2^53/(p-1)^2 = 8,791,696.62; k = 8,796,093 gives 9.0117e15 > 2^53 = 9.0072e15 | k <= 8,791,696 for p = 32009 and k <= 8,780,720 for p = 32029; (p-1)^2 is right to three digits |
| 16 | float64 GEMM runs at full GPU tensor-core throughput | wrong | `docs/design/gpu-exact-modular-linear-algebra.md:20`: FP64 0.47 TFLOP/s against INT8 62.8-68.6 TOP/s on the RTX 4070 Ti; `exact_mod_matmul` (`fiber_rank_v12.py:184-189`) is host numpy `A @ B`; `--echelon gpu` uses INT8 digits (`:68-72`) | The float64 guard is a CPU BLAS device; GPU exactness comes from INT8 digit products with INT32 accumulation (design doc `:83-90`) |
| 17 | `k2_cm.py` and `fiber_rank.py` use float64 exact matmul | partly | a grep for `float64` and one for `matmul` on `docs/evidence/a5-exceptional-fibers/k2_cm.py`, and both return nothing; no `fiber_rank.py` exists; the engines are `replay/engine/fiber_rank_v8.py` to `fiber_rank_v12.py` | The guard lives in `fiber_rank_v12.py` (`exact_mod_matmul` `:184`, `sparse_mod_matmul` `:730`), and earlier versions v8-v11 |
| 18 | gpu-exact-modular-linear-algebra.md:15-35: INT8 tensor cores run at 62.8-68.6 TOP/s on the RTX 4070 Ti (SM89) | partly | design `:15-24`: probes on the build host RTX 4070 Ti, CC 8.9, 2026-10-27, cuBLAS GEMM n = 2048; exact INT8 modular backend about 16 TOP/s on that card (`:96`); the owner's fiber runs use the RTX 4090 Laptop (`engine-v12/README.md:16`), measured at 12.1-13.7 TOP/s effective (`:208-209`) with no raw INT8 peak | The 62.8-68.6 figure is the raw INT8-to-INT32 GEMM peak of the 4070 Ti, not the exact modular product and not the 4090 Laptop |
| 19 | The exact modular product is bit-identical to FLINT and 51x faster | partly | design `:47`: 34x at n = 1024 and 51x at n = 2048 against FLINT `nmod_mat` multiplication, exact against FLINT on every sampled row; `:24` bit-identical to an int64 reference | Speedup of the modular product at two sizes on the 4070 Ti; the pasted text ties it to the raw 62.8 TOP/s peak |
| 20 | p = 32009 and 32029 fit in 16 bits | holds | both < 2^15 = 32768 (design `:83` requires p < 2^15; int16 tiles `:105`) | none |
| 20b | Fitting 16 bits halves memory bandwidth in the 6-variable slice-and-saturation pipeline | hypothesis | "slice-and-saturation" appears nowhere in the design doc; quotient mode spends 99% of wall time in the Singular export (`:213-215`) | Becomes a claim with a stage-time record showing transfer time dominating |
| 21 | INT32/FLOAT32 is the accumulator for intermediate sums and medium Groebner bases | wrong | INT32 accumulates INT8 digit GEMMs (design `:84-86`); Groebner bases run on the CPU in Singular, msolve, giac, Macaulay2 (`:3-5`) | INT32 accumulates GEMM digit products; no Groebner basis runs in INT32 |
| 22 | INT64/FLOAT64 is the domain of FLINT fmpz and exact BLAS accumulators below 2^53 | partly | `fmpz` is arbitrary precision; the engine uses `flint.nmod_mat` (`fiber_rank_v12.py:203`), word-size residues | The float64 accumulator part holds (row 14); fmpz is not a 64-bit type |
| 23 | D = 1, 2, 4: associator vanishes | holds | s1: D = 4, 0 non-associating of 6/24/64 triples | none |
| 24 | D = 8 alternative, D >= 16 not alternative | holds | s3: float [x,x,y] 1.8e-15 at D = 8, 3.3 at D = 16 (generic x) | none |
| 25 | 35 imaginary triads in O, 7 associate, 28 do not, associator is +-2 e_l | holds | s1: 7 associating unordered triads equal the 7 XOR-closed triples; associator values over all distinct imaginary triples are {-2, 0, 2} at D = 8, 16, 32 | none |
| 26 | Fano lines {1,2,3}, {1,4,5}, {1,6,7}, {2,4,6}, {2,5,7}, {3,4,7}, {3,5,6} | holds | s1 prints exactly this list | none |
| 27 | [e1,e2,e4] = e3 e4 - e1 e6 = e7 - (-e7) = 2 e7, printed at `cd_core.py:353` | holds | s1: `[0,0,0,0,0,0,0,2.0]`; `cd_sign(8,3,4)=+1`, `cd_sign(8,1,6)=-1`; `cd_core.py:353` is the print of this associator | none |
| 28 | `cd_core.py:166-187`: left = sigma(i,j) sigma(i^j,k), right = sigma(j,k) sigma(i,j^k), omega = left*right | holds | `cd_core.py:173-174` (`triple_sign` returns the pair; omega is their product) | none |
| 29 | Ordered-triple table: 24 / 24 assoc; 210 / 42 and 168; 2,184 / 168 and 2,016; 24,780 / 744 and 24,036 | wrong | s1; k = 2 counts 4*3*2 ordered distinct indices including e0, k = 3 counts 7*6*5 imaginary only; k = 4 and 5 totals fit neither rule; `docs/evidence/cd_associator_defect_census/census.json:12,18,24,30` gives non-associating 168, 1848, 15960, 130200 | See the corrected table below. Only the k = 3 row (42 / 168) is correct |
| 30 | The non-associating share rises to 92.3% and 97.0% | wrong | s1 non-fractions of ordered distinct imaginary triples: 0.800, 0.677, 0.592, 0.546 (D = 8, 16, 32, 64); census sampled rates 0.5035, 0.5023, 0.5007 at D = 1024, 2048, 4096 | The share falls toward 1/2 |
| 31 | The associator-phase ANF degree is exact and scales with the doubling level | partly | `docs/evidence/cd-associator-anf/README.md` (table): degree = max(1, bitlen(max(p,q)) - 2) for distinct nonzero p, q at k >= 3, at most k - 2 | Degree depends on the index pair, and the level only bounds it |
| 32 | Jobs e13e5ed0 and 7ae2af4b both measured +1.5859 to +1.6127 with >522 sigma against a null of +0.0099 | wrong | `docs/evidence/ascella-associator-predecessor/README.md:20-21`: e13e5ed0 contrast +1.612742, SE 0.007874, t = 204.8, null +0.000136; `job-01-deep-seismograph.md:20-21`: 7ae2af4b contrast +1.585912, SE 0.003034, t = 522.77, null +0.009992 | The two jobs differ: +1.6127 (>204 sigma, null +0.0001) and +1.5859 (>522 sigma, null +0.0099) |
| 33 | The +0.0099 quaternion control is a strict null | partly | `job-01-deep-seismograph.md:21`: +0.009992, SE 0.002969, t = 3.37, p = 0.0098, 95% CI [+0.0031, +0.0168] | Nonzero at p = 0.0098, admitted under a preregistered bound of 0.05; the sigmas are statistical standard errors of the weighted least squares fit |
| 34 | Input Fock state 1,0,1,0,0,0,0,0,0,0,0,0 on 12 modes, a = (e6+e7)/sqrt2, b = (e5+e7)/sqrt2, L_a L_b against L_(ab), quaternion control | holds | `docs/design/ascella-associator-thermal-seismograph.md:83-95`; `scripts/ascella_associator_predecessor.py:73,592`; s3: ideal the Frobenius norm of L_a L_b - L_ab = 3.4641 for the octonion pair and 0.0 for the quaternion pair | none |
| 35 | `ascella-foundations-and-architecture.md:195-217` embeds L_a in 12-mode Clements meshes with `RectangularDecomposer` | partly | lines 190-217 describe the chip (12-mode folded mesh, 132 couplers, input state); `RectangularDecomposer` appears at `:271` in the software stack; the experiment uses a 4x4 block on modes 0..3 (`ascella_associator_predecessor.py:11`, design `:239`) | The cited range does not contain the embedding |
| 36 | Hurwitz: no zero divisors for D <= 8 | holds | s2: chi = +1 count 0 at D = 8; `cd-zero-divisor-count/zd_count.json` level 3 counted 0; `docs/notes/algebra_circuit_rules.md:103` | The 1898 date was not checked |
| 37 | Zero divisors first appear at D = 16 | holds | s2: 336 signed products at D = 16 | none |
| 38 | 42 assessor pairs (84 signed two-blade zero divisors) in 7 box-kites | holds | s2: 42 distinct index pairs {i,j} (the assessors), 84 signed elements, 7 components of 6 assessors, each of degree 4; `kaplansky-mechanisms-cayley-dickson.md:49-55` | none |
| 39 | Two blades multiply to zero iff the XOR skeleton holds and chi = +1 | holds | `kaplansky-mechanisms-cayley-dickson.md:32-47`; s2: corpus (336 rows) equals the chi = +1 set, no zero product with overlapping supports at D = 16 | none |
| 40 | chi = sigma(i,k) sigma(j,l) sigma(i,l) sigma(j,k); t s = -sigma(i,k) sigma(j,l) | holds | same lines; s2 builds the D = 32 elements from `s = -sigma(i,k) sigma(j,l) t` and every one has nonzero nullity | none |
| 41 | Examples (e1+e10)(e4-e15) = (e1+e10)(e5+e14) = (e1+e10)(e6-e13) = (e1+e10)(e7+e12) = 0 | holds | s2: s = -1, +1, -1, +1 for (4,15), (5,14), (6,13), (7,12) | none |
| 42 | D = 16: 630 skeleton pairs, 168 with chi = +1, 336 signed products, 42 assessors, 7 box-kites | holds | s2: 630 / 168 / 336 / 42 / 7 | These are counts over ordered pairs of index pairs; unordered they are 315 / 84 / 168 |
| 43 | Sedenion alternativity fails; L_v^2 = -2I for v = e1+e9; det L_v = 256 and L_v^2 not scalar for v = e0+e9 | partly | values hold: `cd_core.py:302-339`, s3 (`square_scale -2`, `square_is_scalar False`, det 256 for both). s5: L_v L_v - L_(vv) = 0 for both, so [v,v,y] = 0 for every y; L_x^2 is non-scalar already in C (x = 1 + i) | The two elements are counterexamples to norm-only zero-divisor predicates (`cd_core.py:302-311`), not witnesses of non-alternativity. The witness is a generic x (row 24: float [x,x,y] = 3.3 at D = 16) |
| 44 | A_5 contains 252 two-blade zero-divisor pairs | wrong | s2: D = 32 has 5040 signed ordered zero products (2520 ordered chi = +1 skeleton pairs, 2520 unordered signed pairs) and 588 signed two-blade elements on 294 index pairs; nullity histogram {4: 168, 8: 168, 12: 252} (`kaplansky-mechanisms-cayley-dickson.md:92-93`) | 252 counts the nullity-12 two-blade zero divisors, not pairs |
| 45 | Zero-divisor locus of A_5: 12 orbits of G_2(C) x SO(2,C) x C^*, nullities 8 (5), 12 (5), 16 (2) | partly | orbit names and counts match `docs/notes/topics/a5-hardware-algebra-synthesis.md:12-16` and `docs/evidence/a5-strata-regularity/README.md:9,56-63`; the same record lists three nullity-4 strata (`:21`) | Twelve orbits plus the origin make the locus of nullity >= 8; two-blade zero divisors of nullity 4 lie outside it |
| 46 | Rocq proves W8 = J(z)+J(z'), dimension 24, degree 16, numerator N_J^2 | partly | `docs/evidence/cd-twisted-product/README.md:27`: the proofs are polynomial identities, "no theorem concerns dimension or degree"; `a5-w8-twisted-product/README.md:1-8` and result table: Singular 4.4.1 at p = 32009 and 32003 | Ideal equality is Rocq; dimension 24, degree 16 and the square numerator are Singular computations |
| 47 | n_64 = 2 n_32 for (a,0) | holds | L_(a,0)(c,d) = (ac, da), so the kernel is ker L_a x ker R_a, of dimension 2 n(L_a) because ker L_a = ker R_a (`cd-one-sided-inverses.md`, Corollary 9.3); s4: (n_32, n_64) = (16,32), (8,16), (0,0) for three elements | none |
| 48 | Mixed pairs follow the 512-pair spectrum laws of `singular_sector_dynamics.py` | partly | `singular_sector_dynamics.py:93` is `SECTOR_MAX_DIM = 512` (a dimension cap), its docstring `:21-27` gives the mixed-pair recursion for the size of the sector S+; the 512 mixed basis pairs and the refuted sum rule are `a5-w8-twisted-product/README.md:6-9` (n_32 = n_16(z)+n_16(z') fails on 480 of 512) | The 512 pairs belong to the W8 twisted-product record |
| 49 | Mod 2 the algebra is commutative and associative; (e_i+e_j)^2 = e0 + 2 e_(i^j) + e0 = 0 | holds | `kaplansky-mechanisms-cayley-dickson.md:67-70` (pasted lines 66-71): every structure constant is +-1, which is 1 mod 2, giving F_2[Z_2^k]; the expansion is the untwisted group-ring value | Note: in the Cayley-Dickson algebra itself (e_i+e_j)^2 = -2 e_0 (s3, pairs (1,2), (1,10), (3,5)); both vanish mod 2 |
| 50 | A_16 = e1 + e10 + e18 - e25 is a 4-term pathion operand | holds | `a5-hardware-algebra-synthesis.md:43` (N- representative); s4: nullity of L_a = 16 and of L_(a,0) in A_6 = 32 | none |
| 51 | Bit widths 2^n mirror CD dimensions (INT4..INT64 with H..A_6, FLOAT16 with sedenions) | hypothesis | no repository artifact ties a register width to D; p = 32009 was chosen for the 2^15 limit of the digit scheme (design `:83`) | Becomes a claim when a design fixes a word width by D and a measurement confirms it |
| 52 | A D-bit integer holds the support mask of an A_k element (INT4 the 4 quaternion coordinates, INT8 the 8 octonion signs); an 8-lane register adds octonions in one instruction | partly | support masks of D bits are a counting identity; a nibble holds one bit per basis index, not a coordinate | The INT4 "4 coordinates" line is wrong (4-bit support mask only); the 8-lane octonion addition is trivially true |
| 53 | The 42 assessors are 16-bit integers of Hamming weight 2 | holds | s2: 42 distinct supports {i,j} | A mask drops the sign, so the 84 signed elements and the chi partner relation need more |
| 54 | INT4 serves "Fano line coordinates, GF(16)" | cannot check | no `GF(16)` in `docs/notes`, `docs/design` or evidence READMEs; the Fano plane belongs to D = 8 | none |
| 55 | FLOAT8 E4M3 gives tensor-core exact GEMM at 68 TOPs | partly | design `:23`: FP8 E4M3 98.7 TFLOP/s peak, exact only on digits in [-8, 8]; `:96`: exact FP8 backend about 6 effective TOP/s against about 16 for INT8 | 68 TOP/s is the INT8 peak (row 18) |
| 56 | Synthesis: zero divisors begin at INT16 and non-associative triads at INT8 | hypothesis | numerology of rows 51 and 52 | none |
| 57 | Line citations `kaplansky-mechanisms-cayley-dickson.md` 32-48 and 66-71 | holds | criterion and gauge invariance `:32-47`; mod-2 sentence `:67-70` | none |
### Corrected triple table (s1; assoc / non-associating)

| D | ordered distinct imaginary | ordered distinct, e0 allowed | all D^3 ordered | non-fraction, distinct imaginary |
|---|---|---|---|---|
| 4 | 6 / 0 | 24 / 0 | 64 / 0 | 0 |
| 8 | 42 / 168 (total 210) | 168 / 168 (336) | 344 / 168 (512) | 0.800 |
| 16 | 882 / 1848 (2730) | 1512 / 1848 (3360) | 2248 / 1848 (4096) | 0.677 |
| 32 | 11010 / 15960 (26970) | 13800 / 15960 (29760) | 16808 / 15960 (32768) | 0.592 |
| 64 | 108066 / 130200 (238266) | 119784 / 130200 (249984) | not run | 0.546 |

The non-associating count is the same under every rule (168, 1848, 15960, 130200) because no basis triple with a repeated
index or e0 fails to associate (s1: the count is rule-independent for D = 4..32 and for both distinct-index rules at D = 64; s3 cocycle counts equal it). Unordered counts (35 -> 7/28; 455 -> 203/252; 4495 ->
2339/2156) classify only the sorted ordering, and the six orderings of a triple disagree from D = 16 on (1848 is not
6 x 252), so the pasted unordered phrasing is meaningful only at D = 8, where all six orderings agree.

## Five findings that change what the owner should rely on

1. The triple table is wrong in three of four rows and mixes two counting rules; the non-associating share falls from
   80% to about 50%, it does not climb to 97%.
2. sigma is a cochain, never a cocycle for D >= 8; calling it the Albuquerque-Majid 2-cocycle inverts the structure
   (its coboundary is the associator phase).
3. float64 GEMM does not run at tensor-core throughput: it measures 0.47 TFLOP/s on the 4070 Ti, the guard runs on
   host BLAS, and the 62.8-68.6 TOP/s figure is a raw INT8 peak of the 4070 Ti, not the 4090 Laptop used for the runs.
4. A_5 has 5040 signed two-blade zero products on 588 signed elements, not 252 pairs; 252 is the nullity-12 count.
5. The Ascella numbers merge two jobs: +1.6127 (>204 sigma, null +0.0001) is e13e5ed0, and +1.5859 (>522 sigma,
   null +0.0099, itself nonzero at p = 0.0098) is 7ae2af4b.

Also wrong: the parity(p_hi & q_lo) sign recursion (row 7) and the 8,796,093 inner-dimension bound (row 15).

## Verified facts not yet stated in docs/ (home chosen by `docs/README.md`)

- Associating counts (42, 882, 11010, 108066) beside the non-associating ones (168, 1848, 15960, 130200), the
  rule-independence of the non-associating count, and the failure of unordered counts above D = 8.
  `docs/notes/topics/cd_associator_defect_census.md` states no such count and `docs/README.md` has no row for it; the
  note and `census.json` need a map row, and the note is the home.
- The cochain statement at every level: sigma(p,q) sigma(p^q,r) = sigma(q,r) sigma(p,q^r) fails on 168/512, 1848/4096,
  15960/32768 triples. `docs/notes/open_gororoba_survey.md:147` records the count for D = 16 only (1527 of 3375
  imaginary triples vanish). Home: `docs/notes/cd_phase_degree.md`.
- The Boolean degree of [sigma_k(p,q) = -1] in all 2k index bits is k (k = 2..5), and the doubling recursion with its
  conjugate factor, checked on all k = 1..6 cells. Home: `docs/notes/cd_phase_degree.md`.
- n(L_(a,0)) = 2 n(L_a) from ker L_(a,0) = ker L_a x ker R_a and Corollary 9.3. Home: `docs/notes/topics/cd-one-sided-inverses.md`.
- The float64 inner-dimension bound for the two primes (8,791,696 at 32009; 8,780,720 at 32029), the sufficiency
  of the bound, and the distinction between design-doc `k p^2` and the engine's `k (p-1)^2`. Home:
  `docs/design/gpu-exact-modular-linear-algebra.md` (FP64 row of the host-facts table).
- Two-blade zero divisors at D = 16 stay exactly zero in float64 for scaled operands. Home:
  `docs/notes/algebra_circuit_rules.md` (sedenion determinant and membership).

## Not run

The D = 32 "zero products off the skeleton" count was not recomputed (D = 16 was). The Hurwitz date, the 4070 Ti and
4090 Laptop throughput figures, the Rocq receipts (`rocq check`) and the Ascella statistics were read from their records and not replayed: the contrast values come from narrative READMEs, and the decomposition in `ascella-associator-predecessor/README.md` multiplies to 1.632 (s5), not the stated 1.613, with V_HOM 0.8742 against 0.9296 in the foundations doc. No GPU, provider or network call was made.

## Scripts

Each ran from the repository root as `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3 FILE`; `s4`
imports `rank_mod` from `s2`; every script keeps the `__main__` guard that `cd_core`'s `ordered_map` pool needs.

### s1_triples.py
```python
import sys
sys.path.insert(0, 'gororoba_quantum')  # run from the repository root
from itertools import product, permutations, combinations
from cd_core import triple_sign, associator, basis, classify_octonion_triples
def count(D, triples):
    non = tot = 0
    for t in triples:
        left, right = triple_sign(D, *t)
        tot += 1
        non += left != right
    return tot - non, non
def main():
    for k in range(2, 7):
        D = 1 << k
        rules = {"ordered distinct imaginary": permutations(range(1, D), 3),
                 "ordered distinct, e0 allowed": permutations(range(D), 3)}
        if k <= 5:
            rules["all D^3 ordered (repeats, e0)"] = product(range(D), repeat=3)
            rules["unordered distinct imaginary"] = combinations(range(1, D), 3)
        for name, it in rules.items():
            a, n = count(D, it)
            print(f"D={D:3d} {name:30s} assoc={a:6d} non={n:6d} total={a + n:6d} non-fraction={n / (a + n):.4f}")
    print("classify_octonion_triples():", classify_octonion_triples())
    fano = [t for t in combinations(range(1, 8), 3) if triple_sign(8, *t)[0] == triple_sign(8, *t)[1]]
    print("octonion associating unordered triads:", len(fano), fano)
    print("XOR-closed triads equal them:", fano == [t for t in combinations(range(1, 8), 3) if t[0] ^ t[1] == t[2]])
    print("mixed orderings:", sum(len({triple_sign(8, *p)[0] == triple_sign(8, *p)[1] for p in permutations(t)}) > 1
                                  for t in combinations(range(1, 8), 3)))
    print("[e1,e2,e4] =", associator(8, basis(8, 1), basis(8, 2), basis(8, 4)))
    for D in (8, 16, 32):
        print(D, "associator values over ordered distinct imaginary triples:",
              sorted({triple_sign(D, *t)[0] - triple_sign(D, *t)[1] for t in permutations(range(1, D), 3)}))
if __name__ == "__main__":
    main()
```
### s2_zd.py
```python
import sys
sys.path.insert(0, 'gororoba_quantum')  # run from the repository root
from collections import Counter, defaultdict
from itertools import combinations
from cd_core import cd_sign, cd_multiply_exact, left_mult_matrix, sedenion_zero_divisor_corpus, sedenion_zero_divisors
def vec(D, terms):
    v = [0] * D
    for i, c in terms:
        v[i] += c
    return v
def chi(D, i, j, k, l):
    s = lambda p, q: cd_sign(D, p, q)
    return s(i, k) * s(j, l) * s(i, l) * s(j, k)
def rank_mod(M, p=1000003):
    a = [[int(x) % p for x in r] for r in M]
    r = 0
    for c in range(len(a[0])):
        piv = next((i for i in range(r, len(a)) if a[i][c]), None)
        if piv is None:
            continue
        a[r], a[piv] = a[piv], a[r]
        inv = pow(a[r][c], -1, p)
        a[r] = [x * inv % p for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(x - f * y) % p for x, y in zip(a[i], a[r])]
        r += 1
    return r
def main():
    for D in (8, 16, 32, 64):
        by_xor = defaultdict(list)
        for i, j in combinations(range(1, D), 2):
            by_xor[i ^ j].append((i, j))
        ordered = [(a, b) for lst in by_xor.values() for a in lst for b in lst if not set(a) & set(b)]
        plus = sum(chi(D, *a, *b) == 1 for a, b in ordered)
        print(f"D={D}: ordered skeleton pairs={len(ordered)} chi=+1: ordered={plus} unordered={plus // 2}; signed ordered products={2 * plus}")
    corpus = sedenion_zero_divisor_corpus()
    print("corpus rows:", len(corpus), "t=+1 rows:", len(sedenion_zero_divisors()))
    elems = {(i, j, t) for i, j, t, k, l, s in corpus} | {(k, l, s) for i, j, t, k, l, s in corpus}
    print("signed two-blade elements:", len(elems), "assessors (distinct {i,j}):", len({(i, j) for i, j, t in elems}))
    print("v*u = 0 also holds for every corpus row:", all(not any(cd_multiply_exact(16, vec(16, [(k, 1), (l, s)]), vec(16, [(i, 1), (j, t)]))) for i, j, t, k, l, s in corpus))
    off = sum(not any(cd_multiply_exact(16, vec(16, [(i, 1), (j, t)]), vec(16, [(k, 1), (l, s)])))
              for i, j in combinations(range(1, 16), 2) for k, l in combinations(range(1, 16), 2)
              if len({i, j, k, l}) < 4 for t in (1, -1) for s in (1, -1))
    print("zero products with overlapping supports at D=16:", off)
    nbr = defaultdict(set)
    for i, j, t, k, l, s in corpus:
        nbr[(i, j)].add((k, l))
        nbr[(k, l)].add((i, j))
    seen, comps = set(), []
    for n in nbr:
        if n in seen:
            continue
        stack, comp = [n], 0
        seen.add(n)
        while stack:
            x = stack.pop()
            comp += 1
            for y in nbr[x] - seen:
                seen.add(y)
                stack.append(y)
        comps.append(comp)
    print("box-kite components (assessors each):", sorted(comps), "degrees:", Counter(len(v) for v in nbr.values()))
    for k, l in ((4, 15), (5, 14), (6, 13), (7, 12)):
        print(f"(e1+e10)*(e{k}+s e{l}) = 0 for s in", [s for s in (1, -1) if not any(cd_multiply_exact(16, vec(16, [(1, 1), (10, 1)]), vec(16, [(k, 1), (l, s)])))])
    D = 32
    el32 = set()
    for i, j in combinations(range(1, D), 2):
        for k, l in combinations(range(1, D), 2):
            if i ^ j == k ^ l and len({i, j, k, l}) == 4 and chi(D, i, j, k, l) == 1:
                for t in (1, -1):
                    el32 |= {(i, j, t), (k, l, -cd_sign(D, i, k) * cd_sign(D, j, l) * t)}
    hist = Counter(D - rank_mod(left_mult_matrix(D, vec(D, [(i, 1), (j, t)]))) for i, j, t in el32)
    print("D=32 signed two-blade zero divisors:", len(el32), "index pairs:", len({(i, j) for i, j, t in el32}), "nullity histogram:", dict(hist))
if __name__ == "__main__":
    main()
```
### s3_misc.py
```python
import math
import random
import sys
sys.path.insert(0, 'gororoba_quantum')  # run from the repository root
from itertools import product
import numpy as np
from cd_core import (associator, cd_multiply, cd_multiply_exact, left_mult_matrix, sedenion_counterexamples,
                     triple_sign)
def main():
    print(sedenion_counterexamples())
    for D in (4, 8, 16, 32):
        bad = sum(triple_sign(D, p, q, r)[0] != triple_sign(D, p, q, r)[1] for p, q, r in product(range(D), repeat=3))
        print(f"D={D}: sigma(p,q)sigma(p^q,r) != sigma(q,r)sigma(p,q^r) on {bad} of {D ** 3} triples")
    for i, j in ((1, 2), (1, 10), (3, 5)):
        v = [0] * 16
        v[i] = v[j] = 1
        print(f"(e{i}+e{j})^2 in A_4 =", {n: int(c) for n, c in enumerate(cd_multiply_exact(16, v, v)) if c})
    random.seed(3)
    rv = lambda D: [random.random() for _ in range(D)]
    for D in (2, 4, 8, 16):
        print(f"D={D}: max |float associator|, 200 random triples:",
              max(max(abs(t) for t in associator(D, rv(D), rv(D), rv(D))) for _ in range(200)))
    for D in (8, 16):
        print(f"D={D}: max |float [x,x,y]|, 200 random pairs:",
              max(max(abs(t) for t in associator(D, x, x, y)) for x, y in ((rv(D), rv(D)) for _ in range(200))))
    r = 1 / math.sqrt(2)
    for c in (r, 0.1):
        u, v = [0.0] * 16, [0.0] * 16
        u[1] = u[10] = c
        v[4], v[15] = 3 * c, -3 * c
        print(f"float (e1+e10)*(e4-e15) with scale {c:.4f}: max residual", max(abs(t) for t in cd_multiply(16, u, v)))
    a = [0.0] * 8
    a[6] = a[7] = r
    b = [0.0] * 8
    b[5] = b[7] = r
    ab = cd_multiply(8, a, b)
    d = np.array(left_mult_matrix(8, a)) @ np.array(left_mult_matrix(8, b)) - np.array(left_mult_matrix(8, ab))
    print("Ascella operator a=(e6+e7)/r2, b=(e5+e7)/r2: ab =", [round(x, 3) for x in ab], "|L_aL_b - L_ab|_F =", round(float(np.linalg.norm(d)), 4))
    e1, e2 = [0.0] * 4, [0.0] * 4
    e1[1], e2[2] = 1.0, 1.0
    q = cd_multiply(4, e1, e2)
    dq = np.array(left_mult_matrix(4, e1)) @ np.array(left_mult_matrix(4, e2)) - np.array(left_mult_matrix(4, q))
    print("quaternion control |L_aL_b - L_ab|_F =", float(np.linalg.norm(dq)))
    k = 8_796_093
    arr = np.full(k, 32008.0)
    print("float64 dot at k=8,796,093 (exceeds the bound) equals the exact integer:", int(np.dot(arr, arr)) == k * 32008 ** 2)
if __name__ == "__main__":
    main()
```
### s4_sign.py
```python
import sys, math
sys.path.insert(0, 'gororoba_quantum')  # run from the repository root
from itertools import combinations
from cd_core import cd_sign, left_mult_matrix
from s2_zd import rank_mod
def pasted_cd_sign(dim, p, q):  # transcription of the pasted listing
    sign, half = 1, dim >> 1
    while half > 0:
        p_hi, q_hi = (p >= half), (q >= half)
        if not p_hi and q_hi:
            p, q = q - half, p
        elif p_hi and not q_hi:
            p -= half
            if q != 0:
                sign = -sign
        elif p_hi and q_hi:
            qh, ph = q - half, p - half
            if qh == 0:
                return -sign
            p, q = qh, ph
        half >>= 1
    return sign
def parity(x):
    return bin(x).count('1') & 1
def literal(k, p, q):  # pasted: (-1)^parity(p_hi & q_lo) * sigma_k(p_lo ^ p_hi, q_lo ^ q_hi), hi = top bit
    if k == 0:
        return 1
    n = k - 1
    m = (1 << n) - 1
    plo, phi, qlo, qhi = p & m, (p >> n) & 1, q & m, (q >> n) & 1
    return (-1) ** parity(phi & qlo) * literal(k - 1, plo ^ phi, qlo ^ qhi)
def doubling(k, p, q):  # (a,b)(c,d) = (ac - conj(d) b, da + b conj(c)) on basis units
    if k == 0:
        return 1
    n = k - 1
    m = (1 << n) - 1
    a, plo, b, qlo = (p >> n) & 1, p & m, (q >> n) & 1, q & m
    cj = 1 if qlo == 0 else -1
    if not a and not b:
        return doubling(n, plo, qlo)
    if not a and b:
        return doubling(n, qlo, plo)
    if a and not b:
        return cj * doubling(n, plo, qlo)
    return -cj * doubling(n, qlo, plo)
def anf_degree(bits, f):  # Moebius transform of a truth table on `bits` variables
    t = [f(x) for x in range(1 << bits)]
    for i in range(bits):
        for x in range(1 << bits):
            if x >> i & 1:
                t[x] ^= t[x ^ (1 << i)]
    return max((bin(x).count('1') for x in range(1 << bits) if t[x]), default=0)
def main():
    for k in range(1, 7):
        D = 1 << k
        pairs = [(p, q) for p in range(D) for q in range(D)]
        print(f"k={k}: pasted-listing vs cd_core mismatches", sum(pasted_cd_sign(D, p, q) != cd_sign(D, p, q) for p, q in pairs),
              "| literal parity form", sum(literal(k, p, q) != cd_sign(D, p, q) for p, q in pairs),
              "| doubling recursion", sum(doubling(k, p, q) != cd_sign(D, p, q) for p, q in pairs))
    for k in (2, 3, 4, 5):
        D = 1 << k
        print(f"ANF degree of [sigma_{k}(p,q) = -1] in the {2 * k} index bits:",
              anf_degree(2 * k, lambda x: int(cd_sign(D, x & (D - 1), x >> k) == -1)))
    # n(L_(a,0)) = 2 n(L_a) on A5 -> A6 (nullity over F_1000003 for integer matrices)
    for idx in ([(1, 1), (10, 1), (18, 1), (25, -1)], [(1, 1), (8, 1), (18, 1), (27, 1)], [(3, 1), (5, 1), (9, -1)]):
        a = [0] * 32
        for i, c in idx:
            a[i] += c
        n32 = 32 - rank_mod(left_mult_matrix(32, a))
        n64 = 64 - rank_mod(left_mult_matrix(64, a + [0] * 32))
        print("a =", idx, "n32 =", n32, "n64 =", n64)
    for p in (32009, 32029):
        b = (p - 1) ** 2
        print(f"p={p}: (p-1)^2={b}, floor(2^53/(p-1)^2)={2**53 // b}, exact = {2**53 / b:.3f}; 8,796,093*(p-1)^2 = {8796093 * b} vs 2^53 = {2**53}")
if __name__ == "__main__":
    main()
```
### s5_flex.py
```python
import sys
sys.path.insert(0, 'gororoba_quantum')  # run from the repository root
from cd_core import cd_multiply_exact, left_mult_matrix_exact
def main():
    for i, j in ((0, 9), (1, 9)):
        v = [0] * 16
        v[i] = v[j] = 1
        vv = cd_multiply_exact(16, v, v)
        lv, lvv = left_mult_matrix_exact(16, v), left_mult_matrix_exact(16, vv)
        bad = sum(sum(lv[r][k] * lv[k][c] for k in range(16)) != lvv[r][c] for r in range(16) for c in range(16))
        print(f"v = e{i}+e{j}: v*v = {[(n, int(c)) for n, c in enumerate(vv) if c]}; entries of L_v L_v - L_(vv) that are nonzero: {bad}")
    print("Ascella README product 2*0.8742*0.981*0.9882*0.963 =", 2 * 0.8742 * 0.981 * 0.9882 * 0.963)
if __name__ == "__main__":
    main()
```
