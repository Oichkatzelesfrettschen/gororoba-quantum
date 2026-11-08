# Adversarial review of pull requests #788, #789, #790 and the A5 findings

## Scope, method, and verdict

The review used detached main commit `fb122e569933f6f87c79b5ce19a36c314e00b189` and the three remote heads named in the brief. Pull-request citations below use `git show origin/<branch>:<path> | nl -ba`; main-tree citations use the checked-out line numbers. The review ran read-only `git`, `jq`, `rg`, `sed`, and `awk` commands. The review submitted no provider job and started no cloud resource. Evidence commands appear at the end.

The finite-field, exact-algebra, retained-acquisition, and preregistered-decision work is unusually strong. Four defects remain. Pull request #788 assigns nominal 95 percent coverage after discarding within-PUB covariance. The main synthesis states the sampled Iso slice inference as equality while its own next paragraph says the inference has no numerical confidence. Pull request #790 leaves contradictory ledger states after certifying the second prime. Pull request #790 also leaves a stale protocol sentence. Pull request #789 correctly reports an unresolved batch and preserves the hypothesis status; its only detected defect is trailing whitespace.

## Ranked findings

### 1. Serious: pull request #788 discards same-PUB covariance from claimed 95 percent intervals

The design puts every block of one operand arm in one fused PUB and explicitly calls the reported quantity “the sum over the blocks of one shot” (PR788 `gororoba_quantum/pathion_wide_coset.py`:14-23; PR788 `results/live/2026-11-07T102337.840878Z/CASE.md`:53-59). The retained PUB files store each placement register’s bitstrings in shot order, so the record retains the joint observations needed to estimate cross-placement covariance (command C6).

The analysis instead forms one marginal 16-bin law per placement, computes only its within-placement multinomial covariance, and then sums marginal variances for copies, whole operands, target-minus-control differences, and copy-agreement z scores (PR788 `scripts/pathion_wide_coset_analysis.py`:87-124,175-193,197-232,236-250). Disjoint qubit placement does not establish independent samples under correlated readout, crosstalk, common-mode drift, or a shared execution environment. The fixed 0.05-per-block decision allowance addresses an offset; it does not establish 95 percent shot-noise coverage (PR788 `results/live/2026-11-07T102337.840878Z/CASE.md`:85-93,184-205).

The test suite cannot detect the defect because its synthetic entry draws every placement from a separate multinomial sample, then checks the resulting independent-marginal formula (PR788 `tests/gororoba_quantum/test_pathion_wide_coset_analysis.py`:57-73,153-182). The missing covariance can widen or narrow every interval whose endpoint enters a rule, including whole-operand, null-control, target-minus-control, visibility, and device-agreement decisions (PR788 CASE:193-228).

Remedy: compute each block estimator’s influence value per retained shot and estimate the covariance matrix across aligned registers within each PUB; propagate the full covariance through sums and differences. A shot bootstrap that resamples aligned rows within each PUB provides an independent coverage check. Add a correlated synthetic fixture whose marginal laws stay fixed while its joint coupling changes. Recompute all reported intervals and verdicts before merge.

### 2. Serious: the main synthesis promotes sampled Iso evidence to equality

The synthesis says the codimension-four slices establish `E0 = V(K2)`, analytic spread 5, and `F(I) = k[y]/K2` at both primes (docs/notes/topics/a5-hardware-algebra-synthesis.md:111-114). The next paragraph concedes that a special “on” slice can hit a three-dimensional fiber and that the record has no bound on `deg(E0)`, hence no numerical confidence (same file:115-119).

The canonical slice record uses the narrower claim: each sampled family is “consistent with” dimension at least four, and all eight readings move `A5-067` only to `survives` (docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/README.md:117-125,158-165,167-175; ledger.tsv:67,217). The equality sentence therefore outruns the registered status and its falsification boundary.

Remedy: replace the result sentence with the bounded statement that two preregistered form families at each prime read on and are consistent with the equality, without numerical confidence. Promote equality only after a genericity certificate or a degree bound on the bad hypersurface; the roadmap already names that mover (a5-hardware-algebra-synthesis.md:147-154).

### 3. Moderate: pull request #790 creates contradictory ledger states

The branch adds certified row `A5-220`, which proves `h_5 = 952` for E8-bar to N-minus at prime 32029 by the exact lower/upper squeeze (PR790 `docs/evidence/a5-exceptional-fibers/ledger.tsv`:220; PR790 `docs/evidence/a5-exceptional-fibers/n18-laptop/README.md`:46-53). The same branch leaves `A5-100` open at `861 <= h_5 <= 952` and leaves umbrella row `A5-009` saying the degree-five value is open outside the prime-32009 N-minus case (PR790 ledger:10,100). The main ledger demonstrates the intended transition: `A5-094` became `superseded` when `A5-183` certified the prime-32009 value (PR790 ledger:94,183).

Remedy: mark `A5-100` superseded by `A5-220`, and update `A5-009` to record degree five at both primes for N-minus while keeping the N-plus cases open. Run `scripts/plan_tracker.py check` and every ledger/inventory contract after the edit.

### 4. Moderate: pull request #790 states an unexecuted control as protocol history

The result paragraph correctly records that the prime-32029 degree-four control did not run (PR790 n18 README:46-53). The unchanged scope paragraph still says the repeat runs “after the degree-4 control” (same file:55-65). The exact degree-five squeeze remains valid because `r_18 = 952` meets the registered K2 Hilbert upper bound of 952; the missing control weakens the pre-run prime-independence protocol rather than the algebraic equality (same file:13-30,46-53).

Remedy: change the scope sentence to historical fact, identify the omitted control as an unmet corroborating check, and retain the exact squeeze as the decisive argument.

### 5. Low: pull request #789 contains whitespace errors

`git diff --check origin/main...origin/qi/pathion-one-cz-null-block` reports trailing whitespace at `docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_twins.txt`:13-21 (command C2). Remove the nine trailing runs before merge.

### Sound pull-request decisions that should remain unchanged

Pull request #789 applies its preregistered rule correctly. The rule makes any replicate chi-square above 10.83 unresolved and leaves `A5-186` unchanged (PR789 `results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/CASE.md`:101-128). The retained result reads `b0/base = 34.8597`, `decided = false`, `label = unresolved_batch`, and `a5_186 = unchanged` (PR789 `results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json`:184-232). The old “awaiting approval” line belongs to the immutable submitted case; the main synthesis explains that provenance boundary (a5-hardware-algebra-synthesis.md:134-145).

Pull request #790’s exact finite-field conclusion is sound. The record gives rank 952, block ranks 215/197/270/270, quotient dimension 72,693, and the matching K2 upper bound at prime 32029 (PR790 n18 README:46-53; PR790 ledger:220). The result proves only the finite-field statement; the same README identifies the unproved specialization step needed over characteristic zero (PR790 n18 README:60-63).

Pull request #788’s exact census and experimental construction remain useful after interval repair. The implementation certifies nullities 28 and 60 from integer rank and tiles them into eight and sixteen blocks (PR788 `gororoba_quantum/pathion_wide_coset.py`:1-23,79-99). The covariance defect changes uncertainty and possibly endpoint-based verdicts; it does not change the exact ideal nullities or the retained raw bitstrings.

## Dependency-ledger audit

The table covers the open, `survives`, and hypothesis-bearing rows on which the three pull requests or the takeaway documents rely. Each ledger line contains the evidence owner and mover; the table states the decisive boundary rather than repeating every filename.

| Rows | Present justification or falsification | What moves the row |
|---|---|---|
| `A5-005` | E8-bar to VB agrees with K2 through degree five at prime 32009; this supports only the bounded degrees (`ledger.tsv`:6). | Degree six or degree five at a second prime. |
| `A5-006` | X-plus/minus agrees through degree five at prime 32009 (`ledger.tsv`:7). | Degree six or degree five at a second prime. |
| `A5-007` | Iso agrees through degree five at both primes; sampled slices add non-certifying all-degree evidence (`ledger.tsv`:8,67,217). | Degree six, or a genericity certificate that upgrades `A5-067`. |
| `A5-008` | W8 agrees through degree five at 32009 and degree four at both primes; the receipt binds the K2 upper bound (`ledger.tsv`:9). | Degree five at 32029 or degree six. |
| `A5-009` | N-minus now has degree five at both primes through `A5-183` and PR790 `A5-220`; N-plus remains bounded only (`ledger.tsv`:10; PR790 ledger:183,220). | Update the stale umbrella row; decide N-plus degree five. |
| `A5-010` | Two-prime generic-section lengths equal the degrees for the three K2 rings (`ledger.tsv`:11). | The finite-field claim has no registered mover; characteristic zero needs specialization. |
| `A5-011` | Cohen-Macaulayness plus geometric primality makes analytic spread the equality criterion (`ledger.tsv`:12; a5-hardware-algebra-synthesis.md:95-100). | A flaw in the commutative-algebra argument; no numerical run is the mover. |
| `A5-012` | Radical Cohen-Macaulay components reduce W8 equality to inclusion of C20 and C30; C20 has an arc, C30 does not (`ledger.tsv`:13,66). | A C30 arc/chart proves inclusion, or a relation/component witness refutes it. |
| `A5-016` | The E8-bar to VB degree-three component remains favored only by Hilbert data (`ledger.tsv`:17). | An arc into that component, or a relation vanishing only on the degree-four component. |
| `A5-029` | Generic nullity-eight kernel-plane limits remain unevaluated (`ledger.tsv`:30). | Compute the Grassmannian limit along the registered arcs. |
| `A5-066` | A bounded search of 2,406 W8 families reaches C20 intersections but never generic C30 (`ledger.tsv`:66). | A blowup chart or arc with a five-dimensional fiber part outside C20. |
| `A5-067`, `A5-217` | Eight slices read on, but special slices have unbounded bad-set degree; equality therefore only survives (`ledger.tsv`:67,217; tslice README:117-125,167-175). | A genericity witness or degree bound proves; repeated independent off readings refute at that prime. |
| `A5-082`, `A5-088` | E8-bar to N-plus degree five stays between 861 and 952 from radical arcs and K2 (`ledger.tsv`:82,88). | A rank above 861 or a new degree-five relation. |
| `A5-100` | PR790’s rank 952 falsifies the row’s status as open, although the interval itself contains the result (main `ledger.tsv`:100; PR790 ledger:220). | Mark it superseded by `A5-220`. |
| `A5-083`, `A5-089`, `A5-095`, `A5-101` | The value 1666 is only the degree-six K2 upper bound for E8-bar to N-plus/minus at both primes (`ledger.tsv`:83,89,95,101). | A lower bound reaching 1666 proves equality; an extra degree-six relation lowers it. |
| `A5-119`, `A5-125` | The value 2422 is only the Iso degree-six K2 upper bound at each prime (`ledger.tsv`:119,125). | A lower bound reaching 2422 or an extra relation. |
| `A5-180`, `A5-182`, `A5-192` | The full-map Fez loss is depth/placement-associated, while low-depth coset blocks recover the integer nullities on Fez, Marrakesh, and Kingston (`ledger.tsv`:180,182,192). | A low-depth placement-specific loss or an out-of-band corrected nullity on another calibration/device. |
| `A5-184` | Tuna-17 resolves every retained coset sign and the cocycle-free mutation (`ledger.tsv`:184). | A calibration that loses a sign or preserves the mutation’s sign. |
| `A5-186` | Coherent over-rotation remains one bounded model, but correlated readout remains open; PR789 produced an unresolved batch (`ledger.tsv`:186; PR789 analysis:184-232). | A resolved six-CZ/twin response under the preregistered rule; rerun required. |
| `A5-187` | Misses follow logical bit d2 while d2 moves between physical qubits; routing-coupler models fit worse (`ledger.tsv`:187). | A graph-automorphic reroute that makes the effect follow the physical qubit. |
| `A5-188`, `A5-199` | Ascella realizes the four-term blocks, and matched IBM/Ascella levels agree within the registered 0.07 band (`ledger.tsv`:188,199). | A repeat or matched arm outside the band. |
| `A5-193` | IBM null-selector readings exclude the Tuna-sized over-rotation on the measured IBM circuits (`ledger.tsv`:193). | A positive IBM k0 contrast with one-CZ blocks at zero, or a much weaker Kingston response slope. |
| `A5-196` | The calibration-overcorrection mechanism has confidence 0.5 and excludes neither repetition-delay context nor a same-placement calibration arm (`ledger.tsv`:196). | The registered same-placement preparation arm matches calibrated asymmetry within 0.04. |
| `A5-198` | Packed-minus-isolated intervals stay inside 0.015 on two devices (`ledger.tsv`:198). | A denser packing/backend/block whose interval clears that boundary. |
| `A5-200` | Identical Ascella meshes reproduce mirror errors with correlation 0.9966 (`ledger.tsv`:200). | A replay below 0.988 or moved anchors. |
| `A5-202` | The preregistered static-map result is confounded by frozen per-mode efficiencies; the post-hoc increment remains suggestive (`ledger.tsv`:202). | A fresh-seed preregistered increment test at alpha 0.005. |
| `A5-210`, `A5-211` | Exact evaluations establish the named six-term chord and boundedly exclude four-term Iso/X alternatives; the absences are searches, not theorems (`ledger.tsv`:210,211). | A four-term counterexample or a hardware encoding of the six-term chord. |
| `A5-214`, `A5-215`, `A5-216` | X controls and Iso k=5/k=3 controls validate the slice implementation and support condition, not genericity (`ledger.tsv`:214-216; tslice README:105-113). | A control reversal exposes a defect; an independent family strengthens but does not certify genericity. |
| `A5-219` | Float64 SVD computes linear W8 and quadratic E8-bar contact; the hardware exponent remains explicitly hypothetical (`ledger.tsv`:219; hardware-orbits/README.md:161-168). | Exact symbolic eigenvalue valuation moves the matrix claim; an observable-specific calibrated scan moves the hardware claim. |

Rows `A5-194`, `A5-195`, and `A5-197` are already refuted, while `A5-208`, `A5-209`, and `A5-218` are proved/proved/rejected; the requested open-survives-hypothesis audit therefore does not reopen them (`ledger.tsv`:194,195,197,208,209,218).

## New structural conjectures and cheapest falsifiers

1. **Scheme-theoretic A4 restriction.** Conjecture: intersecting the A5 W8 closure with the embedded sedenion coordinate subspace gives the corresponding A4 zero-divisor-pair closure scheme-theoretically, not merely pointwise. A5 already writes a doubly pure element as a pair from A4 and identifies W8 with pairs of A4 zero divisors (docs/evidence/a5-zero-divisor-strata/README.md:34-37,353-358). Falsifier: unequal pulled-back radicals, Hilbert series, component multiplicities, or a restricted nullity component absent from A4. Cheapest test: set the upper-half coordinates to zero in the registered W8 generators, compare radicals and Hilbert series with the A4 ideal over one good prime, then check the G2 tangent action.

2. **Depth-amplified logical-role error.** Conjecture: the Tuna d2 effect and the deep Fez loss arise from logical-role-sensitive coherent error amplified by circuit depth, rather than one shared faulty qubit. Tuna’s effect follows d2 across q4 and q11, while Fez’s earlier loss follows deep placements and disappears in low-depth blocks (`ledger.tsv`:180,182,187). Falsifier: Tuna graph-automorphic reroutes make the effect stay on q11, or a low-depth Fez circuit reproduces the loss on the same placements. Cheapest test: noiseless/noisy role permutations and existing routed-circuit replays; only a surviving ambiguity justifies a provider rerun.

3. **Contact-order transfer.** Conjecture: after fixing the actual block observable and normalization, the leading hardware response exponent is determined by the first nonzero symbolic valuation of `L(a(eps))^T L(a(eps))`; an amplitude observable may retain orders one/two, while a probability observable may show orders two/four. Falsifier: an exact noiseless forward model gives equal or reversed exponents for the two registered lines. Cheapest test: symbolic characteristic-polynomial valuations followed by the existing local block simulator. The float64 matrix evidence alone cannot select the observable exponent (hardware-orbits/README.md:161-168).

4. **Maximum two-term nullity law.** Conjecture: for every Cayley-Dickson dimension `D >= 16`, the maximal two-term nullity is `D/2 - 4`. The retained exact census computes 4, 12, 28, 60, and 124 at dimensions 16, 32, 64, 128, and 256; dimension 8 is the expected boundary exception with zero (command C5; cayley_dickson_sparse_census.md:9-31,53-55). Falsifier: one exact higher-dimensional operand exceeds the formula or the exhaustive next census has another maximum. Cheapest test: derive the aligned-XOR-pair recurrence from `cd_sign`; a dimension-512 exact census is the mechanical fallback. Hardware adds no evidence to the closed form.

5. **E8-bar degree-six equality.** Conjecture: `h_6 = 1666` for E8-bar to N-minus at both good primes. Finite differences of 21, 83, 225, 495, 952 are 62/142/270/457, then 80/128/187, then 48/59, then 11; constant fourth difference predicts 1666 (command C4). That prediction is not independent evidence: 1666 is exactly the K2 upper bound, and five points always fit a quartic (`ledger.tsv`:95,101). Falsifier: an explicit degree-six relation outside K2. Decisive test: a truncated-rank lower bound reaching 1666; a lower rank at one truncation remains inconclusive.

## Cross-program connections from first principles

| Connection | Strength | Boundary |
|---|---|---|
| Cayley-Dickson signs determine each exact block law; aligned block defects sum to the integer rank defect. The hardware then tests the compiled sign network, not a new algebra. | Proved algebraically; computed on hardware. | PR788 `pathion_wide_coset.py`:1-23 and CASE:15-49; hardware uncertainty needs finding 1 repaired. |
| Exact W8-to-N-minus and E8-bar-to-VB lines connect measured endpoint operands to attachment directions. | Proved line membership and computed endpoint nullities. | `ledger.tsv`:208-209. A point measurement still cannot identify an attachment. |
| Linear versus quadratic singular-value opening distinguishes the two incidence matrices. | Computed matrix behavior; hardware transfer is a hypothesis. | hardware-orbits/README.md:161-168 and `ledger.tsv`:219. |
| The A5 W8 description uses pairs of A4 zero divisors, so the sedenion program supplies the lower-dimensional algebra inside one A5 component. | Proved/set-theoretic in the registered model; scheme equality is the new conjecture. | a5-zero-divisor-strata/README.md:34-37,353-358; sedenion_hardware_witness_review.md:43-53. |
| Tuna’s logical d2 dependence argues against one q11 fault; Fez’s depth-associated placement loss argues against one device-independent physical-qubit mechanism. | Computed evidence; common logical-role mechanism remains a hypothesis. | `ledger.tsv`:180,182,187,193. |
| Fiber-cone Hilbert values describe limiting direction spaces, while hardware nullity estimates describe rank defects at selected points. | Separate proved/computed objects. | a5-exceptional-fiber-findings.md:3-17; no source proves a causal law from Hilbert degree to hardware contrast. |

## Remaining computations, cost, memory, and host placement

| Open item | Required computation | Evidence-based cost and memory | Placement and decision |
|---|---|---|---|
| Roadmap item 6 attachments | Finish reduced supports, compute kernel-plane limits, certify the X-minus arc, and compute nullity-eight Grassmannian limits (dimension32-global-topology-program.md:55-68). | Arc certificates replay in 8 min 4 s with an 8 GiB virtual cap, but peak RSS was unmeasured (compute-flags.md:283). Existing Rees/saturation formulations stalled up to 72 GB, and E8-bar to VB reached about 209 GB (a5-exceptional-fiber-findings.md:160-181). | Individual arc work fits the laptop or Kaggle. The complete package has no demonstrated finishing path on WSL 54 GB, Azure 84 GB, or Kaggle below about 27 GiB (compute-flags.md:240-247). |
| W8 C30 and E8-bar-to-VB degree-three components | Implement and first validate a point-count/branch-count variant; plain dimension slices cannot distinguish equal-dimensional components (tslice README:177-189). | Runtime and peak memory are unknown because the method is unimplemented and branch-count equals point-count is unproved. The known full elimination reached 209 GB in about 2 h without finishing (a5-exceptional-fiber-findings.md:173-181). | Run only a small E8-bar control on laptop/Kaggle under 12 h. The demonstrated full formulation fits none of the three hosts. |
| Characteristic zero | Prove good reduction for J, K2, normal forms, membership identities, and ranks, then lift the finite-field squeeze (a5-exceptional-fiber-findings.md:10-17,318-324). | One modular N=18 degree-five run already cost 93,763 s and 35.4 GiB on PR790; coefficient growth over Q is unmeasured, so that run is only a lower comparator (PR790 n18 README:46-53). | First compare the Q(i) degree-two K2 producer and prove good reduction. No listed host has a demonstrated path for the full characteristic-zero degree-five computation. |
| Iso degree-six ladder | Validate the Iso K2 receipt, then probe truncations and run toward lower bound 2422 (`ledger.tsv`:119,125). | The current forecast predicts N=19, 13 GiB with the receipt or 23 GiB without it, and 2-4 h for products plus closure; the forecast also says the receipt path is untested (forecasts/trends-2026-11-06.md:237-254). Measured degree five at N=16 cost 1,040-1,062 s and 11.3-11.5 GB (a5-exceptional-fiber-findings.md:135-147). | WSL is the first host after a small receipt/pilot check; Kaggle fits the forecast under 12 h and 27 GiB but has less margin; Azure is the fallback. Treat the forecast as a hypothesis until the pilot measures growth. |
| 64/128 interpretation | Prove the aligned-pair recurrence for maximum two-term nullity; the retained census already extends through dimension 256 (command C5). | Reading the retained JSON costs seconds and negligible memory. The repository records “local exact integer arithmetic” but no replay time or peak RSS, so a new exhaustive cost estimate would be invented (command C5). | Symbolic recurrence work fits the laptop. A further census also belongs locally through `parallel.py`; hardware contributes no structural evidence. |
| Tuna rerun | Repeat the same 19-batch, 56-job decision design because `b0/base` failed heterogeneity (PR789 CASE:87-128; analysis:184-232). | 2,293,760 shots, about 1,361-1,500 s execution, plus eighteen 30 s pauses and queue time (PR789 CASE:87-99). Memory is provider-managed and absent from the record. | Only Tuna-17 answers calibration-dependent heterogeneity. Laptop, Azure, and Kaggle can replay the decision rule but cannot close the device claim. The rerun requires a new written case and owner approval. |

## Steelman and final assessment

The strongest interpretation preserves the exact results and narrows only their epistemic boundary. Pull request #788 retains joint shot data, exact circuits, calibration, and integer-rank targets, so the interval defect is repairable without another QPU run. Pull request #789 honors a preregistered unresolved outcome instead of forcing a mechanism label. Pull request #790 matches a committed prediction at a second prime and binds the exact squeeze to hashes and receipts. The slice program records its own genericity limitation, and the host records distinguish measurements from forecasts.

The merge recommendation is conditional. Pull request #789 needs only whitespace cleanup. Pull request #790 needs ledger reconciliation and scope wording, while its exact result can stand. Pull request #788 needs covariance-aware reanalysis before any claimed 95 percent interval or endpoint-based verdict can stand. The main synthesis needs the Iso equality rewritten as non-certifying evidence.

## Evidence commands

- **C1, branch identities:** `git rev-parse origin/ibm/cd64-128-coset-blocks origin/qi/pathion-one-cz-null-block origin/a5/e8bar-n18-p32029` returned `95eb0301761cd90a9af2b7d1e4b7c00f23ce952d`, `6f8891b94b34ba3bc8b0c4e56dcbf0d6bf8437b8`, and `5c1c566e2ce5f43c65f3f18c0e639d1e1c2f68af`.
- **C2, whitespace:** `git diff --check origin/main...origin/<branch>` was clean for #788 and #790 and reported PR789 `c2_one_cz_twins.txt`:13-21.
- **C3, scope:** `git diff --stat origin/main...origin/ibm/cd64-128-coset-blocks` reported 86 files and 8,372,071 insertions; the large additions are retained raw PUB records, not duplicated source implementations.
- **C4, finite differences:** applying successive adjacent subtraction to `21 83 225 495 952` returned `62 142 270 457`, `80 128 187`, `48 59`, and `11`; extending the fourth difference by 11 returns 1666.
- **C5, exact ladder census:** `jq '[.dimensions[] | {dimension, largest_two_term_nullity, signed_element_count}]' results/hw_estimate/annihilator_strata.json` returned `(8,0,42)`, `(16,4,210)`, `(32,12,930)`, `(64,28,3906)`, `(128,60,16002)`, `(256,124,64770)`.
- **C6, joint shots:** `git show origin/ibm/cd64-128-coset-blocks:results/live/2026-11-07T153325.440007Z/raw/dbnk9noou4as73b4nn90/pub_00.json` shows one PUB object with registers `g0_r0_c`, `g0_r1_c`, and later placements, each carrying aligned `bitstrings` arrays; the adjacent `index.json` binds all twelve PUB files by SHA-256.
