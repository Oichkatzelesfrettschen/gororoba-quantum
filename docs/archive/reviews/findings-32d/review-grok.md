# Adversarial synthesis: PRs #788, #789, #790 and the A_5 findings

Phase 0. Artifact: three open PRs plus the A_5 takeaway/ledger on `origin/main`. Fields: fiber-cone commutative algebra over F_p, Cayley-Dickson left-multiplication, and hardware statistics. Visibility: `git show`/`git diff` against `origin/main` (no checkout), ledger, takeaways, CASE files, analysis JSON, `collect.json` pooled summaries. Fiber_rank and QPU jobs were not rerun. A `cd_core` rank probe was blocked by the session command policy; nullities below cite retained records.

Steelman first. #790's squeeze r_18 = HF(K2,5) = 952 at a second prime, with blocks 215/197/270/270 and dim_quotient 72693 matching the committed prediction, is the strongest exact statement in the program. #788 actually ran whole-operand nullity at D=64 and 128 on two Heron r2 devices, and Kingston's targets sit on the integers. #789 wrote a preregistered heterogeneity gate and then obeyed it. Those three are SOUND. The rest of this note is what they do not buy.

## 1. Ledger rows the PRs and takeaways rest on

Status codes: J = justified by a check named here; F = falsified or over-claimed; S = survives only as labeled.

| Row | Status here | Check | What would move it |
|---|---|---|---|
| A5-220 | J, certified | `e8nm_d5_n18_p32029.json`: r_N=952, blocks 215/197/270/270, dim_quotient=72693, engine `7849cbc7`, prime 32029; `.time` wall 93763 s, RSS 37139012 KiB; `k2-hilbert.jsonl` HF(K2,5)=952; prediction in n18 README before the run | replay with a different rank |
| A5-183 | J, certified | same squeeze at 32009; A5-220 is the committed twin | none at this prime |
| A5-100 | F as `open` | same claim as A5-220; PR790 left A5-100 `open` at `861 <= h_5 <= 952` | supersede with A5-220 |
| A5-009 | F as written | still says "degree 5 otherwise open with 861 <= h_5 <= 952" after A5-183 and A5-220 | rewrite: N- degree 5 certified at both primes; N+ still open unless A5-024 is used |
| A5-082, A5-088 | S, stale | N+ h_5 interval. A5-024 (survives): N+ and N- fibers correspond under t8,t9 signs at three (p,i) specializations, and moved N- quadrics span N+ quadrics. If that map carries F(I), then A5-183/220 certify N+ too | either apply A5-024 and certify, or compute r_18 on N+ (quotient mode, same engine; ~26 h, 35 GiB) |
| A5-083, 089, 095, 101 | S, open | h_6 <= 1666 = HF(K2,6). Sequence 21,83,225,495,952 has 4th difference 11 = deg V(K2) (findings: proj dim 4, degree 11). If 4th diffs stay 11, h_6=952+457+187+59+11=1666 | r_N = 1666 at some N, or a degree-6 relation outside K2 |
| A5-067, A5-217 | S, hedge stripped in the takeaway | tslice README: an "on" at k=4 is consistent with dim E0 >= 4 for that form set, "no numerical confidence", deg(E0) unbounded. Ledger A5-067 repeats the hedge. Synthesis `a5-hardware-algebra-synthesis.md:149-150` and :67 treat E0=V(K2) as an F_p statement | a bound on deg(E0), a third independent form family, or a finished chart saturation |
| A5-011 | S | Cohen-Macaulay of K2 plus primality makes multiplicity redundant; analytic spread 5 is the remaining number. The k=4 "on" does not certify spread 5 against a special slice | same as A5-067 |
| A5-218 | J as `rejected` | tslice README: a slice of codimension l-1 cannot see a second same-dimension component | a point-count or branch-count variant (untested) |
| A5-206..209, 212, 213 | J, proved | hardware-orbits README + `result.json`: cd_core nullity equals orbit nullity; H-generator rank equals orbit dimension; arcs 1 and 2 are four-term | an operand whose pattern mismatches |
| A5-210, 211 | S | four-term absence is a bounded search (1029 planes), not a theorem | a four-term E8-bar->N- or Iso/X+ line |
| A5-219 | S as matrices; hypothesis untested | `contact_order.txt`: W8->N- four 1.414 eps and four 2.000 eps, slope 1.000; E8-bar->VB four 2.000 eps^2, slope 1.998. Float64 SVD of `cd_core.left_mult_matrix` | exact L(b)^T L(b) with another order; hardware scan (needs a forward model) |
| A5-186 | S as hypothesis; F as "the 6-CZ run decided" | analysis JSON `decision.decided=false`, `label=unresolved_batch`; b0/base chi2=34.86 > BATCH_CHI2=10.828 (`qi_pathion_one_cz_null_cases.py:364,867`). Ledger falsifier on the PR says the twins "decide against a coin-conditioned readout offset". Synthesis :163 uses present tense for the same | a rerun whose b0 batches pass chi2 10.83 |
| A5-193 | J, survives | IBM k0 selector within 0.006 of 0; pooled angle -0.0015+-0.0014 rad, 4.3 se below Tuna | a k0 contrast >= +0.006 with 1-CZ blocks at 0 |
| A5-196 | S, confidence 0.5 | Kingston paired O shortfall -0.0893+-0.0290; exploratory Fez drop of 3 placements | a same-placement readout-calibration arm |
| A5-202 | S, open | shifter-map increment over efficiency is post hoc, p=0.041 | preregistered fresh-seed increment test at alpha 0.005 |
| A5-016, A5-066 | S, open | E8-bar->VB degree-3 component; W8 C30 in the fiber. 2406 weighted families miss C30 | an arc into C30, or a relation killing the extra component |

A5-007 (Iso F(I)=K2 through degree 5 at both primes) is J as a truncated-rank squeeze, independent of A5-067's spread claim. A5-005, 006, 008 are the same kind of squeeze at the degrees they name.

## 2. Conjectures the records do not state

C1. Max two-term nullity is N(D)=D/2-4 for D=2^n, n>=4, hence N(2D)/N(D)=2(D-4)/(D-8). At D=64 this is 15/7=2.143. Census-wide.json: D=64 new nullities 16,20,24,28; D=128 to 60, 1740 operands at 60. Recurrence 4,12,28,60 = 2a+4. Falsifier: a two-term operand at D=256 with nullity >124, or census max ≠124. Cheapest test: `census.py --wide` at D=256 (laptop; D=128 already did 16002 operands). Proof target: doubling formula for rank of L_{e_i+e_j}.

C2. A_5 nullity-8 orbits restrict to A_4 zero-divisors under doubling. e1+e10 is W8, nullity 8 in A_5 (hardware-orbits README:25); L_{e1+e10} has rank 12 of 16 in A_4 (sedenion_hardware_witness_review.md:54), nullity 4. Kernel dimension doubles. G_2 in H=G_2(C)×SO(2,C)×C^* is Aut(O). Falsifier: an A_5 orbit of nullity >=8 whose intersection with the A_4 span is empty of A_4 zero-divisors, or a kernel that does not double. Cheapest test: for each of the 12 orbit representatives, restrict a to the first 16 coordinates and compare `cd_core` nullity in dim 16 and 32 (seconds, host).

C3. Contact order of L_a predicts the order of arc limit vectors, and (after a forward model) the hardware contrast's order in b. Already hypothesized in A5-219. The missing algebraic half: E8-bar->VB quadratic opening is the same phenomenon as the X certificate's order-2 limits (arcs-x). Falsifier: an incidence whose arc limit order differs from its singular-value order. Cheapest test: exact SVD of L(a(eps))^T L(a(eps)) along arcs 1 and 2, and along one X arc, over Q (flint, seconds).

C4. Hilbert polynomial of F(I) for E8-bar->N- is that of a projective 4-fold of degree 11: leading coefficient 11/24, 4th difference 11, so h_6=1666 if F(I)=k[y]/K2. Falsifier: r_N < 1666 at a plateau that meets a lower bound from sqrt(K2), or a degree-6 generator of L outside K2. Cheapest test: receipt-bound fiber_rank d=6, smallest N that moved at d=5 was 18; see costs below.

C5. Tuna q11 e10 collapse and Fez k28 visibility collapse are the same class of instrument fault: one physical site destroying a block that algebraically is null. Tuna `drift_covariate.references.flagged`: q11 e10 0.362 (batch-03) to 0.039 (batch-04) to 0.434 (batch-15), threshold 0.02. Fez `wide_n128_k28_nullity_estimate`=-0.742, visibility 0.594; every other Fez n128 block is within 0.21 of 0 and vis >0.73; Kingston k28 vis 0.970. Falsifier: a Fez rerun on a disjoint placement set with k28 vis >0.8 and n128 within 0+-0.8, or a Tuna rerun with q11 e10 deltas <0.02 and b0 chi2 <10.83. Cheapest test: no QPU; recompute Fez per-placement vis from `collect.json` (the analysis script already does this; the PR did not retain the JSON).

C6. The estimator N_hat saturates at the integer ideal when all signs agree, so a dead placement on a null block moves the null sum and leaves a target block at its ideal (Fez o128 k28 = 4.0 at vis 0.649). Null-referenced difference then fails in the direction of the target. Falsifier: a placement with vis <0.6 whose target N_hat leaves its integer by >0.25. Cheapest test: the same analysis script on the retained Fez run.

## 3. Cross-program connections

Proved. L_a is a linear encoding, not an algebra homomorphism (AGENTS.md). cd_core nullity of every measured A_5 operand of nullity >=8 equals its H-orbit nullity (A5-206). Coset blocks recover those integers at 1-20 CZ on two Heron r2 devices (A5-182, A5-192). The mutation (XOR permutation of SELECT) flips the sign of the reading (A5-184 Tuna; IBM mutation sums ~-2 against true 28 and 60 in #788). That is the hardware reading the cochain, not the XOR skeleton.

Computed. Contact orders of the two four-term incidences that hardware can scan (A5-208, 209, 219). Whole-operand sums at D=64,128 on Kingston: o64=27.995, o128=60.126, ratio 2.148 against 60/28=2.143 (`collect.json` of `2026-11-07T153325.886771Z`). Fez targets also sit on 28.071 and 59.978. Fiber Hilbert functions through the degrees in A5-005..009, 183, 220.

Hypothesis. A hardware contrast scanned in b along arcs 1 and 2 shows orders 1 and 2 (A5-219). Tuna +0.0164 is one X90 over-rotation of ~0.03 rad, absent on IBM (A5-186, A5-193). Ascella per-mesh fixed error, not a shifter map beyond efficiencies (A5-200 survives, A5-202 open). Iso F(I)=K2 in every degree over F_p (A5-067 hedge). N(D)=D/2-4 (C1).

The reverse direction: every hardware deviation found so far is an instrument realization (placement, mesh, readout, over-rotation). None has contradicted an ideal nullity. That is a calibration theorem, not a classification theorem. A point reading cannot see an attachment; only a path into the boundary can (synthesis :32). The 64/128 case is outside the A_5 orbit diagram; it tests the doubling of the same function L_a.

## 4. Remaining items: cost, memory, host

Evidence for estimates: n18-laptop README (d5 N=18: 26 h / 35.4 GiB laptop; 32029: 26.0 h / 35.4 GiB); w8-n16-azure README (d5 N=16 receipt-bound: 2.18 h / 24.9 GiB on FX4mds_v2); Iso d5 N=16: 1062 s / 11.3 GB (findings); tslice Iso k=4: 486 s / 320 MB; A5-205 chart: 23.5 h / 25.7 GB still growing, killed by auto-shutdown; Kaggle CPU 12 h / 30 GB (kaggle/README.md:32-34); laptop 47 GiB visible (tslice README). FX4mds_v2 84 GB.

| Item | Computation | Time / peak | Host | Blocker |
|---|---|---|---|---|
| Iso degree-6 ladder | fiber_rank d=6, N~19, 6 t-vars, receipt | ~1-3 h / ~20-25 GiB (d5 was 11.3 GB; products ×6) | laptop | none |
| W8 degree-6 | fiber_rank d=6, N~19, 7 vars, receipt | ~6-10 h / ~40-70 GiB (d5 24.9 GiB receipt; products ×3) | FX4mds_v2 | Kaggle 30 GB too small; laptop tight |
| E8-bar d=6, h_6=1666 | fiber_rank d=6. N=18 just met 952. N~21 scales dim C(N+8,8) by ~2.75, preflight ~97 GB raw; receipt ~0.54× peak (W8 ratio) => ~50 GB | ~80 h wall if time scales with dim (26 h ×3) | FX4mds_v2 only, multi-day, shutdown moved (A5-205) | laptop 35 GiB peak already at d=5; Kaggle 12 h and 30 GB both fail |
| A5-218 C30 / VB degree-3 | point-count of a same-dimension component inside E0, not of V(K2) | QRNG sections of V(K2) are seconds (A5-069); 2406 arc families already miss C30 | laptop for more families | needs a new search (blowup chart off both linear spans). Dense chart failed six times, last on 84 GB |
| Iso characteristic 0 | specialization argument that K2 and the arc system reduce from Q(i) | writing, plus a Q(i) generator comparison (A5-024 falsifier) | host, minutes | compute cannot lift spread; reduction can change it (synthesis :153) |
| Item 6 attachments | kernel-plane limits along arcs 1,2; then 8->16, 12->16 | exact arcs: host, minutes to hours. Hardware scan: QPU case + approval | host for algebra; IBM/Ascella for the scan | IBM encodes +-1 only; Ascella sets reals (synthesis :160) |
| 64/128 interpretation | prove N(D)=D/2-4; retain analysis JSON of #788 | census at D=256: laptop, minutes to an hour. Analysis script: minutes | laptop | #788 has no committed analysis record |
| Tuna rerun of A5-186 | same 19-batch design after q11 e10 is stable | one Tuna-17 session, shots as CASE.md:50 | Tuna-17 QPU, written case + approval | q11 e10 deltas of 0.32-0.34 make heterogeneity fail; a rerun on the same qubit is wasted until that rate is quiet |

No available host: Iso 23-variable chart std (A5-070,071,174,176,181,205); msolve Rees of E8-bar->VB (209 GB at degree 16, findings); W8 std(J+m P_3) OOM at 77.8 GiB on an 84 GB VM. Those routes are dead.

## 5. PR defects, file:line, worst first

### FATAL / SERIOUS

1. SERIOUS, #790. A5-220 certifies the claim A5-100 still lists as `open`. A5-009's basis still says degree 5 is open except 32009 N-. Ledger.tsv A5-100, A5-009 vs A5-220. Remedy: supersede A5-100, rewrite A5-009, and either certify N+ via A5-024 or say why the sign map does not carry h_5.

2. SERIOUS, #790. Degree-4 control at p=32029 did not run (`n18.events`: after p=32029 d=5, "done"; README: "the runner ran d=4 at p=32009 only"). The prediction named r=495 at d=4 as a gate. The d=5 standard counts include 495 as a representative count, which is not the N=18 truncated rank at d=4. Remedy: run d=4 at 32029 (n17 already had r=495 at both primes one N below; this is a cheap control, hours not days).

3. SERIOUS, #789. Ledger A5-186 falsifier on the branch: "the 6-CZ blocks and their coin-fixed twins decide against a coin-conditioned readout offset". Analysis: `decision.decided=false`, `label=unresolved_batch` (`pathion_one_cz_null_tuna_17_analysis.json`). m_six_cz=-0.00068+-0.00130 would have been the "zero" class; b0/base chi2=34.86 vetoed the whole decision. Synthesis :163 on main already speaks as if the case separates dropout. Remedy: A5-186 stays hypothesis; record unresolved_batch; do not claim dropout is excluded.

4. SERIOUS, #789. CASE.md:3 still reads "awaiting the owner's approval; nothing has been submitted" while 19 Tuna batches and 3 QX batches are retained. The synthesis itself records that this wording already fooled a Codex review. Bytes of a submitted case stay; the status line is a lie about the present.

5. SERIOUS, #788. No retained analysis JSON of the two jobs the research_state now lists (`ibm-fez-pathion-wide-coset`, `ibm-kingston-pathion-wide-coset`). `pathion_wide_coset_analysis.py:18-19` is the rule engine; exit 0 iff every rule passes. Pooled `collect.json` already falsifies Fez null control: n64=-0.531 against band 0.4, n128=-1.056 against 0.8 (`analysis.py:271-274`, CASE.md:199-201). Fez n128 k28=-0.742 against PER_BLOCK_BAND 0.25 (`:50,294`). Kingston targets pass (o64=27.995, o128=60.126). Claiming the case "extends the nullity readings" (synthesis :165) without the script's verdict is HARKing on the passing targets.

6. SERIOUS, #788. Fez k28 is a placement fault, not a 64/128 algebraic effect. Visibilities 0.533 (o64), 0.594 (n128), 0.649 (o128), 0.650 (m128) against Kingston 0.96-0.97. o128 k28 still reads 4.0 exactly, so the null-referenced difference cannot cancel it (C6). The 17th Fez placement is the worst-scored (CASE.md:137-138, score 0.559) and is the A_5 ref32 block, not k28; k28 is one of the 16 operand placements. Remedy: name the physical qubits of placement k28 from the archive, compare to the drain-job exclusions 2-4,16, and drop that placement from the sum in a report-only column.

### SLOPPY

7. #788 CASE.md of the binding dry run still "awaiting the owner's approval" (`2026-11-07T102337.840878Z/CASE.md:5`) after submit. Same class as #789:4.

8. #788 ratio is report-only (CASE.md:227-228, analysis.py:358-359). Kingston 2.148 vs 2.143 is a 0.2% relative gap on two passing integers. It is not evidence for C1 until N(D)=D/2-4 is checked at another D.

9. #788 `within` uses the 95% interval (`analysis.py:255-256`), which is the CASE rule. Pooled collect.json means have no se, so this review's Fez fails are from means that already sit outside the band (interval cannot rescue a mean of -1.056 vs 0.8). Run the script.

10. #789 calibration `coin_dropout=small`, `q12_correlation=small` (`analysis.json` calibration.classes) is the secondary X-only arm, not the 6-CZ decision. Do not read it as excluding dropout.

11. #790 README title still "p = 32009: h_5 = 952" after the 32029 section. Cosmetic until someone cites the title as scope.

### SOUND

#790 engine, hashes, block sum 215+197+270+270=952, and the pre-registered prediction. #788 per-placement inversion tests (`test_pathion_wide_coset_analysis.py`). #789 BATCH_CHI2 gate doing what it was written to do.

## Verdict

The algebraic core that #790 adds is real: h_5(E8-bar->N-)=952 over F_32009 and F_32029, so F(I)_5=(k[y]/K2)_5 at those primes. The takeaway's "Iso is done over F_p" is one special-slice family away from a certificate. The hardware core that #788 adds is real on Kingston and broken on one Fez placement; without the analysis JSON the PR cannot say which rules passed. The hardware core that #789 adds is a correctly unresolved instrument test, then over-claimed in the ledger. Ranked work: (1) fix the three ledgers, (2) run `pathion_wide_coset_analysis.py` on both retained jobs and keep the JSON, (3) rerun Tuna only after q11 e10 is quiet, (4) receipt-bound E8-bar d=6 on FX4 with the shutdown moved, (5) write the char-0 specialization, which no host will compute for you.
