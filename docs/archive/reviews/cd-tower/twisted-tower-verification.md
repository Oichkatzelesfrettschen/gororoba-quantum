# Verification of the twisted-tower architecture audit and its `cd_kernel` module

Subject: an agent's "executive architectural audit" of the Cayley-Dickson tower, pasted by the owner on 2026-11-09,
and the Rust module it committed to gororoba-open (`crates/cd_kernel/src/cayley_dickson/twisted_tower.rs`, branch
`cd_kernel/twisted-tower-architecture`, commit e99fc4af). The audit's own Markdown artifact was not found in the
workspace, so the pasted summary and the committed code are the subject. Each claim was checked against
`gororoba_quantum/cd_core.py` (the specification) by exact enumeration in Fractions, against the repository records,
and against the earlier verification of overlapping claims in
[pasted-analyses-verification.md](pasted-analyses-verification.md) (cited below as "row N").

## Claim table

| # | Claim | Verdict | Evidence | Corrected statement |
|---|---|---|---|---|
| 1 | The tower is integer-exact: e_p e_q = sigma_k(p, q) e_(p xor q) | holds | row 1 | none |
| 2 | sigma_k is a 2-cocycle twist | wrong | row 5: the cocycle identity fails on 168, 1848 and 15960 triples at D = 8, 16, 32 | sigma_k is a 2-cochain; its coboundary is the associator sign omega |
| 3 | Mod 2 the algebra is F_2[Z_2^k], commutative and associative, with (e_i + e_j)^2 = 0 | holds | row 49 | none |
| 4 | IEEE 754 arithmetic is non-associative, so associator tests in floats mix roundoff with structure | holds | rows 10 to 12 | none |
| 5 | float64 GEMM is an exact integer accumulator when k p^2 < 2^53 | holds, loose | row 14: the sharp bound is k (p - 1)^2 < 2^53 | k <= 8,791,696 at p = 32009 |
| 6 | Signed base-256 digits in [-128, 127] give 68.6 TOP/s across four INT8 GEMMs, bit-identical to FLINT | partly | `docs/design/gpu-exact-modular-linear-algebra.md:23`: 62.8 to 68.6 TOP/s is the INT8 GEMM peak, bit-identical to an int64 reference; `:96`: the exact modular backend computes about 16 effective TOP/s | The four-GEMM product runs at about 16 effective TOP/s; no FLINT comparison is recorded |
| 7 | [e_a, e_b, e_c] = (sigma(a,b) sigma(a^b,c) - sigma(b,c) sigma(a,b^c)) e_(a^b^c); zero when omega = +1, +-2 e_(a^b^c) when omega = -1 | holds | every basis triple at D = 8, 16, 32 against the exact associator of `cd_core`: 0 mismatches | none |
| 8 | Linearly dependent triples (c = a xor b) associate | holds | 0 dependent non-associating triples at D = 4 to 64 | none |
| 9 | Octonions: the 7 Fano lines (42 ordered triples) associate, 168 do not | holds | enumeration; row 38 conventions | none |
| 10 | N(D) = (D - 2)(D - 4)(D + 6)/2 non-associating ordered distinct imaginary triples | holds through D = 64 | enumeration: 168, 1848, 15960, 130200 at D = 8, 16, 32, 64, equal to the closed form; the census in [README.md](README.md) gives the same three lower counts | No proof for general D is recorded |
| 11 | deg ANF(omega(a, b, .)) = n - 2 for D = 2^n >= 16 | partly | enumeration of c -> [omega(a,b,c) = -1]: degree sets {1, 2}, {1, 2, 3}, {1, 2, 3, 4} at n = 4, 5, 6; row 31 | n - 2 is the maximum over index pairs; one pair's degree depends on the pair |
| 12 | No zero divisors for D <= 8 | holds | row 36 | none |
| 13 | D = 16: two-blade zero products need i xor j = k xor l and chi(i,j;k,l) = +1; 42 assessor pairs, 84 signed elements, 336 signed products, 7 box-kites | holds | rows 37 to 42; enumeration over all signed two-blades with disjoint supports: 336 / 42 / 84, equal to `cd_core.sedenion_zero_divisor_corpus` | none |
| 14 | D = 32: 294 index pairs (588 signed elements) stratify into 12 orbits of G_2(C) x SO(2,C) x C^* across nullities 0, 4, 8, 12, 16 | wrong | enumeration: 5040 products on 294 pairs, 588 elements (row 44); the twelve orbits stratify R_8 minus 0, the nullity >= 8 locus, with nullities 8 (5), 12 (5), 16 (2) (row 45, `docs/evidence/a5-strata-regularity/README.md`); the two-blade nullity histogram is {4: 168, 8: 168, 12: 252} | The 294 two-blade index pairs and the twelve H-orbits are different objects; nullity 0 is no zero divisor |
| 15 | Every real Cayley-Dickson algebra has ker L_a = ker R_a ("direct finiteness") | partly | ker L_a = ker R_a is Corollary 9.3 of math/0511691 (row 47) | The kernel identity holds; direct finiteness (xy = 1 implies yx = 1) is a different property and was not checked |
| 16 | From D = 16 inverses are not unique: e1 + e10 is a zero divisor with several two-sided inverses | holds | exact check: x = e1 + e10, z = e4 - e15 give x z = z x = 0, and conj(x)/2 and conj(x)/2 + z are both two-sided inverses of x | "Unit-regularity fails" was not checked |
| 17 | Ascella associator contrast +1.5859 at > 522 sigma | partly | row 32: +1.585912 belongs to job 7ae2af4b against a null of +0.009992 that is itself nonzero at p = 0.0098 | none beyond row 32 |
| 18 | Hardware table: Float8 E4M3 for octonions, Int16 and Float16 for sedenions, Heron parity syndromes on 42 assessor pairs, Belenos 64-dimensional meshes | hypothesis | rows 51, 52, 56: no artifact ties a word width to D; no Heron, Tuna-17 or Belenos case runs the named mappings | Each row becomes a claim when a design fixes it and a measurement confirms it |
| 19 | Anchors CdTowerDomain.v, SchreierSignCode.v, SignCodeCardinality.v, cd_associator_defect_census.py, k2_cm.py, ledger A5-206 to A5-220 | holds | `proofs/CdTowerDomain.v` and the two scripts are in gororoba-quantum; the two other `.v` files are in gororoba-open; the 15 ledger rows exist | Whether each anchor proves what its table row says was not checked |

## The committed module

The module as committed (e99fc4af) passed its own tests, but four of those tests compared a closed form with itself.
Commits af935c12 and d41e7444 on the same branch correct it.

| Defect | Resolution |
|---|---|
| `non_associating_triple_count` and `associator_anf_degree` were tested only against their own formulas | Both now equal an enumeration through D = 64 in the tests; the degree function is renamed `max_associator_anf_degree` and documents that it is a maximum over index pairs |
| `enumerate_sedenion_zero_divisors` fixed D = 16 and duplicated `find_zero_divisors_sign_table` | `enumerate_two_blade_zero_products(dim)` covers every dimension; the tests check 336 / 42 / 84 at D = 16 and 5040 / 294 / 588 at D = 32, and that the existing sign-table enumerator lists exactly half (it fixes t = +1) |
| `split_base256_digits` documented a1 in [-64, 64] but split uncentered residues (a1 up to 125) and narrowed with `as i8` for any prime | The split centers each residue into (-p/2, p/2], panics for p >= 2^15, and the tests reconstruct every residue of F_32009 with a1 in [-64, 64] |
| `FloatingCdElement` duplicated `cd_multiply` and `cd_associator`, and named a rounded product "exact" | Removed; the float check uses `cd_associator` |
| `HardwarePlatform` returned device dimension limits (Belenos 64, Heron 64, SM89 65536) that no measurement supports and called Tuna-17 a spin processor | Removed (claim 18) |
| The new file lacked the SPDX header that gororoba-open requires of new files | `// SPDX-License-Identifier: GPL-2.0-or-later`, the crate's license |
| The module doc called sigma_k a 2-cocycle | It states the cochain and its coboundary omega (claim 2) |

Validation on the branch head: `cargo clippy -p cd_kernel --all-targets --profile validation -- -D warnings` clean;
`cargo nextest run -p cd_kernel --lib --cargo-profile validation` 427 passed; the file is ASCII.

## What survives

The exact sign algebra survives: the associator sign, the cross-ratio criterion for two-blade zero products, exact
integer and modular arithmetic, and the counts N(D) and two-blade censuses as enumerated facts through D = 64 and
D = 32. The orbit statement (claim 14), the hardware mapping (claim 18) and the throughput figure (claim 6) do not
survive as stated. The module lands in gororoba-open through its own pull request.
