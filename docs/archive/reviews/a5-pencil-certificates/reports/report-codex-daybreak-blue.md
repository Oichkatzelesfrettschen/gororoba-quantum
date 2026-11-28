**Verdict**
- **Computed/proved:** The tower and calibration bounds use the correct directions. The core dimensions at `e_1+e_10` for `A_4` through `A_8` are defensible.
- **Changes required:** A5-667 states a universal theorem from finite samples; A5-671 omits the theorem that supplies the four-dimensional annihilator bound; the “60 points” determinant check contains only 11 distinct points.
- **Verification:** `git diff --check origin/main...HEAD` passes, and the reviewed worktree is clean at `e9e3c33f0`.

**Findings**
1. **SERIOUS — computed evidence is presented as a universal W8 classification.**  
   A5-667 says “for a real point … of W8” the kernel intersection determines the pencil type, but its evidence covers ten named points, 312 four-term representatives, 43 points in one scan, and 2,448 signed four-term census points. The script itself calls the result true only “on every W8 point of the record” and validates ten named points plus bounded censuses. Scope the ledger statement to those families or mark the universal sentence explicitly as a hypothesis. `docs/evidence/a5-exceptional-fibers/ledger.tsv:646`, `scripts/a5_nullity_transitions.py:984`, `scripts/a5_nullity_transitions.py:1117`, `scripts/a5_nullity_transitions.py:1143`.

2. **SERIOUS — the written proof of A5-671 lacks the upper bound on sedenion annihilators.**  
   Proposition 5.3 and Lemma 6.4 of Biss–Dugger–Isaksen prove the complex structure and conjugate-linearity. They imply that the common kernel has even real dimension. They do not limit it to `0, 2, 4`. That conclusion additionally needs Biss–Dugger–Isaksen Theorem 1.2 or Proposition 9.10, which gives `dim Ann(x) <= 4` in `A_4`. The statement is true, but the current two-line attribution is incomplete. `docs/evidence/a5-nullity-transitions/README.md:175`, `docs/evidence/a5-exceptional-fibers/ledger.tsv:649`.

3. **SERIOUS — the 60 determinant evaluations contain exactly 11 distinct points.**  
   Every coordinate is reduced modulo 11, so the vector depends only on `t mod 11`. Comparing coordinates `i=0` and `i=1` proves distinct residues give distinct vectors; therefore `t=1..60` produces 11 points with multiplicities five or six. The README, prediction P26, PR body, and A5-657 all say “60 integer points,” which materially overstates sample diversity. Generate 60 deterministic distinct vectors and record both evaluation and distinct-point counts. `scripts/a5_pencil_certificates.py:478`, `scripts/a5_pencil_certificates.py:506`, `docs/evidence/a5-nullity-transitions/README.md:171`, `docs/evidence/a5-nullity-transitions/third-round-predictions.md:19`, `docs/evidence/a5-exceptional-fibers/ledger.tsv:636`.

4. **MODERATE — the second route cannot independently detect a frame-normalization error.**  
   Both routes normalize by the same factor `2**size / gram_det`: the Pfaffian route uses it in `constant**2 * 2**size / gram_det`, and the determinant route uses it in `det * 2**size / (target**2 * gram_det)`. Both also use FLINT nullspaces to construct the kernel frame. The second route independently checks multiplication and polynomial evaluation, but it does not independently check the Gram-`2I` normalization or FLINT frame construction. `scripts/a5_pencil_certificates.py:391`, `scripts/a5_pencil_certificates.py:466`, `scripts/a5_pencil_certificates.py:502`.

5. **MODERATE — the sign-table control samples only 1/2, 1/4, 1/8 or 1/16 of the left factors above A4.**  
   `table_mismatches()` steps by `dimension // 16`; at dimension 32 it never checks odd `p`, and at dimension 256 it checks only multiples of 16. The self-test mutates dimension 16, where the stride happens to be one, so it cannot expose this coverage gap. The validation message “the sign table follows the doubling formula” exceeds the check. Enumerate every `(p,q)` pair; 65,536 basis products at A8 remain small beside the certificate cost. `scripts/a5_pencil_certificates.py:116`, `scripts/a5_pencil_certificates.py:607`, `scripts/a5_pencil_certificates.py:697`.

6. **MODERATE — the certificate does not bind the authoritative Q and G source.**  
   The hard-coded definitions match the strata record now: `Q=U+mu^2+V` and `G=Q^2-4(UV-W^2)`. The stored digests cover only `cd_core.py`, `parallel.py`, and the certificate script, so a later strata-definition change would not invalidate this certificate. Add the strata script or result digest. `docs/evidence/a5-zero-divisor-strata/README.md:36`, `scripts/a5_pencil_certificates.py:349`, `scripts/a5_pencil_certificates.py:489`, `scripts/a5_pencil_certificates.py:48`, `scripts/a5_pencil_certificates.py:726`.

7. **LOW — `validate()` does not guard the determinant sample count or zero-target count.**  
   It requires 30 units, vanished lower coefficients, and ratio `4`, but it does not require `points == 60` or `zero_targets == 0`. Its message therefore can say “order 1 and order 3 at every point” when some sampled targets have a higher order and were skipped from the ratio set. `scripts/a5_pencil_certificates.py:641`, `docs/evidence/a5-nullity-transitions/certificates.json:101`.

8. **LOW — the clean mypy result does not cover the result schema.**  
   `strata_item()` is typed as `dict[str, Any]` and has an early return containing only two fields; `validate()` later assumes the full schema. Mypy cannot detect this partial-row path or misspelled record keys. Use `TypedDict` variants or a dataclass and make the failure path raise through `require()`. `scripts/a5_pencil_certificates.py:319`, `scripts/a5_pencil_certificates.py:363`, `scripts/a5_pencil_certificates.py:622`.

9. **PERFORMANCE — the census repeats substantial independent work.**  
   Every one of 64 `census_chunk` workers constructs all 26,096 left-multiplication matrices: 1,670,144 matrix constructions before pair ranks. The zero-divisor enumeration is also serial. Partition enumeration with a top-level `parallel.ordered_map`, then provide workers a shared or precomputed matrix representation. The determinant’s point loop is likewise independent, but flatten it into top-level jobs because nested maps intentionally receive one worker. `scripts/a5_pencil_certificates.py:513`, `scripts/a5_pencil_certificates.py:532`, `scripts/a5_pencil_certificates.py:548`.

**Bound Audit**
- **Proved:** Mod-`p` commutant nullity is an upper bound. The full rational commutant reduces into the commutant of the three chosen combinations, while modular rank cannot exceed rational rank. `scripts/a5_pencil_certificates.py:255`.
- **Proved:** Reconstructed elements give a lower bound because every element is checked against every rational pencil operator before its rational rank is counted. A bad reconstruction can be rejected or become a valid commutant element; it cannot create a false lower bound. `scripts/a5_pencil_certificates.py:261`.
- **Proved:** The mod-`p` bracket span is a lower bound because it is generated by three members of the full pencil Lie algebra. Nongeneric weights can weaken this bound but cannot inflate it. `scripts/a5_pencil_certificates.py:292`.
- **Proved:** Gram-skew operators commuting with the verified commutant form an upper container for the closure; modular nullity then gives an upper bound. `scripts/a5_pencil_certificates.py:288`.
- **Computed:** The bounds meet at `3, 10, 36, 136, 528`; the retained record stores `136` and `528` at dimensions 128 and 256. `docs/evidence/a5-nullity-transitions/certificates.json:404`, `docs/evidence/a5-nullity-transitions/certificates.json:431`.
- **Computed:** Type R reads exact commutant `1` and closure `28`; type C reads exact commutant `2` and closure interval `[15,16]`. The README describes these meanings correctly. `docs/evidence/a5-nullity-transitions/certificates.json:28`, `docs/evidence/a5-nullity-transitions/certificates.json:63`.
- **Proved/computed:** The Pfaffian recurrence has the standard alternating signs, and the Q/G formulas match the strata record. The polynomial identity is exact; only the supplementary point sample needs correction.
- **Proved with citation repair:** Anticommutation gives doubly pure zero divisors and complex-invariant kernels. Biss–Dugger–Isaksen Theorem 1.2 or Proposition 9.10 supplies the missing dimension-four bound.

**Gate and Review Record**
- **Measured:** `ci/gates.json` assigns 1,300 CPU-like seconds against the PR body’s measured 980 CPU seconds, a 320-second or 33% margin. That entry is calibrated correctly. `ci/gates.json:4921`.
- **Documented:** Both commit subjects and the PR title follow `component: mechanism`.
- **Documented:** The PR body has the required mechanism, validation, evidence, and residual-risk sections.
- **Current-state defect:** The body says hosted checks are “not run yet,” while the public PR currently shows 10/10 checks passing. Update the validation section.
- **Control wording defect:** The body says every self-test uses a mutant, but the type-C closure check is a calibration point, not a mutated input. `scripts/a5_pencil_certificates.py:691`.
- **Current state:** PR 1045 is a draft with zero conversation comments and zero reviews, so no review-comment prose exists to assess.

**Structural Advance**
- **Proved candidate:** N− and N+ are related by the diagonal XOR-character automorphism  
  `D(e_k) = (-1)^bit3(k) e_k`.  
  It fixes `e_3` and `e_20`, negates `e_12` and `e_27`, and therefore maps N− to N+. Since the sign is an XOR character, `D(e_p e_q)=D(e_p)D(e_q)`. This explains the identical unit sets, term counts, factor degrees, and constants.
- **Falsifier:** The induced substitution `x_w -> (-1)^bit3(w) x_w` fails to carry one Pfaffian coefficient dictionary to the other.
- **Cheapest test:** Compare the two existing sparse coefficient dictionaries under that exact sign substitution; a second Pfaffian expansion is unnecessary.

**Verification Limits**
- The prescribed remote checkout is not at the reviewed state: `HEAD=b68c42d`, with modified script and certificate files plus four documents differing from `e9e3c33f0`. I therefore ran no Python computation.
- Read-only GitHub access served only to inspect the PR title, body, comments, and check state. `gh` could not reach the API; the public browser page succeeded.
- The browser exported three task-created snapshot files into the workspace. Three `trash-put` attempts and the recoverable-removal fallback failed because the sandbox presents the filesystem as read-only; the files remain at `pr1045-snapshot.md` and `.playwright-mcp/` with the `2026-11-28T05-08-4*` names.