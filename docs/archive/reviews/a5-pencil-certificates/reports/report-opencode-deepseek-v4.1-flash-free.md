I'll start by reading the governing documents, then the change under review.

Now let me read the prior-art paper's sections 5 and 6, and the strata record definitions.

I have the paper's exact statements. Now I will run the decisive checks on the remote checkout, starting with the bound directions and the determinant scope.

The remote checkout is at b68c42da3 with uncommitted changes, not the review head. I extracted e9e3c33f0 to SCRATCH/src and verified the script and dependency hashes match the certificate. Now I will run the decisive checks: full sign-table comparison, calibration Gram-skew and rational cross-check, and determinant coverage beyond the 60 points.

# PR 1045 red-team report

**Verdict.** No claim falls on its mathematics. Claims 1 and 2 survive as stated. Claim 3 survives with a coverage correction. Claim 4 survives mathematically, but its proof as written omits the 4-dimensional-kernel premise and the statement is a corollary of Biss-Dugger-Isaksen. Claim 5 survives with three semantic-require gaps. The three-type rule of A5-667 is not proved: the complex structure gives evenness only, and the Clifford-generation route is refuted by computation.

## Findings ranked by consequence

### F1. Claim 4 cites the complex structure but not the 4-dimensional kernel (highest consequence)

`docs/evidence/a5-nullity-transitions/README.md:175-187` cites only BDI Proposition 5.3 (paper line 354) and Lemma 6.4 (line 432). Line 183 then uses "a 4-dimensional kernel" without citation. That premise is BDI Proposition 9.10 (line 771) plus Theorem 9.8 (line 735): in A_4 every annihilator has dimension at most 4 and a multiple of 4, hence exactly 4; line 781 states every zero divisor in A_4 has a 4-dimensional annihilator. Lemma 9.5 (line 706) gives p_0 = p_8 = 0; Lemma 9.6 (line 718) makes Ann(x) a C_n-vector space, hence the kernel invariant under L_(e_8). With those four citations the two-line argument is valid.

`docs/evidence/a5-exceptional-fibers/ledger.tsv:649` already says "the statement is a corollary of that work, and the record contributes the basis check and the census", so the novelty sentence is humble. The finding is the incomplete citation chain, not the mathematics.

Status: proved (BDI), computed (basis check and census); citation finding. Cheapest fix: add the four BDI references at README:183.

### F2. Claim 3: "60 integer points" are 11 distinct points

`scripts/a5_pencil_certificates.py:453-510` uses x_i = ((7*t*(i+1) + 3*i*i + t*t) mod 11) - 5 for t = 1..60. The expression has period 11 in t, so the 60 evaluations are 11 distinct vectors repeated.

Command `the compute workstation ... check_stage_a.py` gave:

```
distinct_x_60_mod11 11
det orig_Nminus count 60 ... ratios ['4']
det orig_Nplus  count 60 ... ratios ['4']
det ext_Nminus  count 200 mod 1009 lower True zero 0 ratios ['4']
det ext_Nplus   count 200 mod 1009 lower True zero 0 ratios ['4']
```

The conclusion is robust: 200 distinct points modulo 1009, x_i = ((7*t*(i+1) + 3*i*i + t*t) mod 1009) - 504 for t = 1..200, give ratio 4 at both N- and N+. The record's "60 integer points" at `ledger.tsv:636` and `README.md:164-174` therefore overstates distinct coverage; the 30-unit determinant is pointwise, not a polynomial identity.

The 18-unit Pfaffian identity is exact: `strata_item` compares the full `fmpz_mpoly` Pfaffian to c |lead Q|^2 |lead G|^2; the certificate has identity True, 8,395 terms, factor degrees [[2,1],[6,1]], constant '4'. The README's "extends beyond the 18 basis units at those points" is accurate; "60 integer points" is the wording to correct.

Status: proved (18-unit identity), computed (30-unit points); wording finding.

### F3. Claim 5: validate does not require three certified sentences

`scripts/a5_pencil_certificates.py:603-657` requires the N± factor degrees [[2,1],[6,1]] but not the VB `pfaffian_factor_degrees` (three quadratics, certificate [[2,1],[2,1],[2,1]], constant '1'); it requires determinant `normalized_ratios ['4']` and `lower_coefficients_vanish` but not `points == 60` (loop constant at line 78); it requires type-C commutant 2 and closure 15/16 but not `commutant_trace_form_negative_definite`. The byte-level `--check certificates.json` binds the stored values, so the values are correct; the semantic requires are incomplete.

Two test-quality gaps sit beside that. The type-C self-test control (`self_test`, lines 680-728) only checks `closure_lower != 16`, so a broken lower 0 would pass it; `validate` separately requires 15/16. The e_16 mutant (`strata_item`, lines 319-406) skips w = 16 in z (`if w % 16`) while keeping its form in `entries`, so it fails because the target omits the e_16 variable by construction. It demonstrates off-domain failure but is a weak mutant: it does not show that including e_16 in Q and G breaks the identity for the right reason.

Status: computed (values), require/test-quality finding. Cheapest fix: add the three requires, a type-C self-test that asserts 15 and 16, and an e_16 mutant that includes e_16 in Q and G.

### F4. A5-667: evenness is proved, the R/C/H assignment is empirical, and the Clifford-generation route is refuted

The complex structure gives dim A in {0,2,4} (A5-671; BDI Lemma 6.7, line 460), not R/C/H. `ledger.tsv:646` states the type follows dim A: 0 gives R and so(8), 2 gives C and su(4) of dimension 15, 4 gives H and sp(2) of dimension 10. The record's 312 W8 points (240 R, 72 H) and 2,448 sign-census points (1,920 R, 528 H) show no exception; the falsifier is a W8 point whose type differs from its dim A.

The naive proof "the commutant is the Clifford algebra generated by A" is refuted. At the type-C point p = e_1 + e_10, q = 2(e_4 + e_15), and the type-H point p = q = e_1 + e_10, the compressions P L_a P of a in A = ker L_p n ker L_q vanish on the A_5 kernel K. `clifford_test.py` and `clifford_test_H.py` gave `comp_rank 0`, all `Ma2_diag` zero, and all anticommutators zero. A annihilates K; it does not generate the commutant.

Status: proved (evenness), computed (type census), hypothesis (mechanism).

### F5. Claim 1 survives

The bound directions are sound. Mod-p rank never exceeds rational rank, so mod-p nullity is an upper bound on the rational commutant and on the rational closure. Reconstructed elements verified over Q give the commutant lower bound; the mod-p bracket span is a lower bound on the rational Lie closure. M_w = G^{-1} f_w is Gram-skew because f_w^T = -f_w; `check_stage_a.py` reports `gram_skew_failures []` at R and C. The Lie algebra of Gram-skew operators is closed under commutator, so the closure is contained in `skew_system(gram)`. The generic three-element commutation system contains the true commutant regardless of genericity, so the upper bound is valid.

Independent confirmation: the old rational sympy `structure_item` (`scripts/a5_nullity_transitions.py:329-394`) gives A4 kernel 4, pencil 3, commutant 4, closure 3; A5 kernel 8, pencil 7, commutant 4, closure 10; A6 (`docs/evidence/a5-nullity-transitions/result.json:13905-13920`) kernel 16, pencil 15, commutant 4, noncommutative, trace form negative definite, closure 36. Levels 4-6 are independently confirmed over Q; levels 7-8 rest on the meeting mod-p bounds 136 and 528.

The full sign table matches `cd_core.cd_sign` at all p,q for dimensions 16, 32, 64, 128, 256, with 0 mismatches (`fast_table_check.py` output `16 0 []` through `256 0 []`). The script's `table_mismatches` (lines 116-126) samples p at stride dimension//16, a weaker check, but the full check is clean.

Status: proved/computed. No finding beyond the stride-sample note.

### F6. Claim 2 survives

`check_stage_a.py` gave:

```
calibration_R kernel 8 halves 0/0 pencil 7 commutant_upper 1 lower 1 verified True
              noncommutative False trace_negative True closure 28/28 gram_scalar 0 gram_skew_failures []
calibration_C kernel 8 halves 2/2 pencil 7 commutant_upper 2 lower 2 verified True
              noncommutative False trace_negative True closure 15/16 gram_scalar 0 gram_skew_failures []
```

These match the certificate and README statement 16 (`README.md:152-163`). The bounds mean what the README says: the commutant upper is the mod-p nullity, the lower is the verified rational elements; the closure lower is the mod-p bracket span, the upper is the Gram-skew operators commuting with the verified commutant. The minor gaps are F3's type-C trace-form require and weak self-test control. Claim survives.

Status: computed.

## Conjectures with falsifiers and cheapest tests

**C1 (three-type rule, the open mechanism).** The commutant of the compression pencil on K is the division algebra D = R, C, or H, and dim D = 1, 2, 4 equals the dimension of the common kernel A; equivalently the Lie closure is the compact real form so(8), su(4), or sp(2) preserving a real, complex, or quaternionic structure on K.

Falsifier: a W8 point with dim A = 2 and commutant not C, or dim A = 4 and commutant not H; or a commutant element not in the algebra generated by the pencil operators. This is exactly the A5-667 falsifier.

Cheapest test: at the existing type-C point, express the nontrivial commutant element J' in the algebra generated by the pencil operators and check J'^2 = -I and J' M = M J'; at the type-H point, do the same for three elements and check the quaternion relations. A second test: enumerate all 2,448 sign-census points and compare the commutant dimension to dim A; the record already does 312, and the extension is deterministic and cheap.

Proof route: show the pencil generates a compact Lie algebra whose centralizer is D. The trace form on the commutant is negative definite (certificate `commutant_trace_form_negative_definite True`), so the closure is compact; the classification of irreducible real representations of so(8), su(4), sp(2) gives D. The missing step is the link from dim A to the real form. The common-kernel complex structure gives only evenness, so a proof of that link would be the new result.

Status: hypothesis.

**C2 (30-unit determinant identity).** The determinant identity may hold as a polynomial identity in all 30 doubly pure coordinates, not only at points. Falsifier: a deterministic point where the ratio differs from 4 or the lower coefficients do not vanish. Cheapest test: the 200-point mod-1009 sweep already gives 4; extend to 1,000 deterministic points modulo a larger prime, or attempt a symbolic check on a subset of variables. Status: hypothesis; the 18-unit case is proved.

**C3 (full e_16 Pfaffian at N±).** The full 19-unit Pfaffian at N± may also factor as c |lead Q|^2 |lead G|^2 or as an irreducible sextic. Falsifier: a computed factorization that differs. Cheapest test: compute the 19-unit Pfaffian at N± in the `fmpz_mpoly` ring; the record explicitly says it is not computed, and the VB case is an irreducible sextic. Status: hypothesis; not needed for claim 3.

**C4 (type-C closure upper bound).** The type-C closure is 15 at every tested point, and the upper bound 16 can be sharpened by one more verified commutant element or a bracket relation. Falsifier: a type-C point with closure 16. Cheapest test: at the existing type-C point, extend the bracket generation with a fourth generic element and check whether the span grows; if it stays 15, the lower bound is tight and the upper bound is an artifact of the commutation system. Status: hypothesis; the record's 15/16 is accurate as a bound.

## What would break each claim

- Claim 1: a level where the two closure bounds do not meet at 2^(n-4)(2^(n-3)+1), a reconstructed element that fails to commute over Q, or a Gram-skew failure. None observed.
- Claim 2: a calibration point whose bounds do not match the stated values. None observed.
- Claim 3: a 30-unit point where the ratio differs from 4, a wrong Q/G leading coefficient, or a shared-code dependency between `strata_item` and `determinant_item`. The 200-point sweep gives 4; the determinant route uses `doubled` and Gaussian-integer polynomials, not `cd_core` or the polynomial ring; the 18-unit identity is exact. Residual risk: `doubled` is checked against `cd_core` only at a stride sample, and the determinant is sign-insensitive, so a global sign error in `doubled` would not show in the ratio. The 18-unit identity uses `cd_core` and anchors the sign, so the risk is low.
- Claim 4: a sedenion zero divisor with nonzero e_0 or e_8, or an odd common-kernel dimension. The basis check and BDI prove none; the census finds none.
- Claim 5: a ledger sentence without a require (F3) or a scope word unsupported by loop bounds (F2). Both are wording/require findings, not false values.

## Run record

Remote work ran over the compute workstation in `SCRATCH`, using a `git archive` of head e9e3c33f0 and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON"`. The extracted script sha256 c9a6de9e..., `cd_core` 3ca79d18..., and `parallel` 90a8ad47... match the certificate. The workstation checkout `WORKTREE` was at b68c42da3 with uncommitted modifications and was not touched. The initial combined run exceeded 900 s and was killed; Stage A, `fast_table_check.py`, and the two Clifford tests completed under the cap. No file in any checkout changed; no commit, push, stash, provider submission or subagent.
