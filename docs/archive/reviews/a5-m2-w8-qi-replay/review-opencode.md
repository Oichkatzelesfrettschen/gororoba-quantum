# Red-team review: PR 1002 (`a5-m2-w8-qi-replay`, head a18abf08)

Review mode: read-only. No files changed, no M2/Singular runs; every verdict rests on source reading, cross-checks against retained artifacts, and arithmetic recomputed with `python3 -I`. All paths are under `docs/evidence/a5-exceptional-fibers/working/runs/` unless noted.

## Claim 1 — `qi_quadric_ideals.py` records exactly the char-0 hilbert-script ideals. **Holds (proved).**

- `qi_quadric_ideals.py` L30 saves the original `wsf.hilbert_script`; L33-47 `recording()` calls it first (a raising call never writes a file), then writes only when `characteristic == 0` (L36), serializing each relation with the same `wsf.parse_relation` and the same `f"({coefficient})*{'*'.join(f'y({k})' ...)}"` construction that `weight_slice_fiber_relations.py` L590-593 uses inside `hilbert_script` — coefficient text verbatim, one-based `y(k)`, ring `y(1..G)` dp on both sides. The wrapper adds nothing algebraic.
- Producer context (proved from source): `wsf._ring` maps characteristic 0 to `Q(i)` with symbol `i` unconditionally, so every char-0 call is genuinely over `Q(i)`; the modular calls at 32009 are the only skipped ones.
- Six files written, matching HILBERT_SOURCES × orbits exactly: `qi-g17` ×2 (Iso), `qi-g21` ×2 (E8-bar), `qi-g24` ×2 (W8); headers `generators 17 relations 68`, `21/148`, `24/144`.
- Spawn-pool mechanism sound: `parallel.py` uses the spawn context, workers re-import `__main__` as `__mp_main__`, so the module-level install (L50-51) runs in every worker; `sys.argv` carries the parent's OUT through. Digest = sha256 of the polynomial body, first 12 hex chars (L44).
- Emission side reproduced without M2: the wrapper's char-0 output is derivable from the source; every retained ideal file parses against the recorded headers.

## Claim 2 — `qi_invariants.m2` computes the invariants over `Q(i)`. **Holds (proved structurally; the run is the empirical witness).**

- L10-12: `F = toField(QQ[jj]/(jj^2+1))`, `R = F[y_1..y_n]`, `L = QQ[jj, y_1..y_n]`. L14: `KL = KL0 + ideal(jj^2+1)`; L15-16: `K = toR KL0`.
- The map `toR` (L15) induces the iso `L/(jj^2+1) ≅ R` because `jj^2+1` is irreducible over `QQ`. Every prime of `KL` contains `jj^2+1`, so `minimalPrimes(KL)` and the Shimoyama-Yokoyama primary decomposition in `L` (L20-21, L28-31) correspond one-to-one to primes of `K` over `Q(i)`; the contraction of any prime containing `jj^2+1` is `(jj^2+1)` itself (no rational sqrt of -1), so the mapped sets are prime. `dim`/`degree` are read on the mapped objects, hence are `Q(i)` values.
- The linear-form count (L21, `#select(..., f -> first degree f == 1)` on minimal generators of the prime) is correct: any linear form in a homogeneous prime lies in the span of its degree-1 minimal generators.
- `radical_equal` (L22-23) and `intersect_equal` (L28-31) are genuinely computed equalities inside M2, not assumptions — `toR(intersect pd) = intersect (toR pd)` need not hold automatically, and the run checks it: both are `true` where the row claims radical, and `false` for E8-bar, where the primary structure is what carries the claim.
- Control `C = K + ideal(R_0^2)` (L24-26) exercises that the whole pipeline is not vacuous: all four controls differ from `K` as expected (g24 dim 6 deg 20; W8 control dim 5 deg 100 in the A5-609 modular arm; g17 dim 4 deg 46; g21 dim 4 deg 28).

## Claim 3 — RESULT lines equal the cited Singular records. **Holds (computed, cross-checked).**

- W8 modular: `W8-nm-p32009.log` equals `expected-results.txt` lines 1-6 (144/6/50, numerator `1+18T+27T^2+4T^3`, primes (6,20,9),(6,30,4), primary equal, radical equal); independently matches `quadric-census/w8.log` ("RESULT w8 generators 144 dim 6 mult 50", hilbert numerator `1,18,27,4,0`) and `quadric-census/w8-component-linear-forms.log` ("linear forms in K2:P 4 in P 9 dims 6 6 mult 30 20"), which is exactly (6,30,4),(6,20,9).
- A5-421 row states W8 dim 6 mult 50, two primes of degrees 20/30, and E8-bar dim 5 mult 11 with primes (5,11)+(4,4) — all matched by the M2 outputs.
- Iso: A5-446's Hilbert numerator `1,0,-68,452,...` (15 coefficients) equals the M2 reduced `1+12T+10T^2` times `(1-T)^12`: recomputed — T¹: 12-12=0 ✓; T²: 10-144+66=-68 ✓; T³: -220+792-120=452 ✓. The two records are the same series under different denominator conventions, and `1+12T+10T^2` over `(1-T)^5` is consistent with dim 5, degree 23, zero linear forms.
- E8-bar primary structure equals the A5-599 modular record ((4,4;4,2),(4,4;4,4),(5,11;5,11), primes (4,4,14),(5,11,9)) — lines 20-23 of `expected-results.txt` ✓.
- A5-428 calibration: w=2 gives relations 140 ✓ (`counts.txt` row 2), and degree-2 gives 21 = 55-34 ✓ against the A5-428 row.
- A5-012's residual risk ("characteristic 0 needs the C30 argument over Q(i)", ledger line 13) is precisely what A5-608's `radical_equal true` with degree-20/30 components over `Q(i)` supplies.

## Claim 4 — Drivers fail closed. **Holds, with three non-fatal notes (below).**

- `run_m2_qi.sh` (41L): `set -eu`; M2 pinned to 1.25.11 by `--version` test; dump mode byte-compares the retained ideal-file list and each file against a fresh wrapper dump; `results.txt` rebuilt by `grep -E '^(RESULT|DONE) '` per log (grep failure exits) and `cmp`'d against `expected-results.txt`; the mutant drops the last relation of a `qi-g17` file (`n=$(($(wc -l < iso) - 1))`) and must reproduce `RESULT mutant K generators 67 `. Sound mutant: the 68 quadrics are minimal generators (μ(I)=68), so any 67 of them generate an ideal with μ(J)=67 exactly (no linear forms can appear from quadric generators, and the quadrics are independent in degree 2); a wrong count fails the grep and the script exits.
- `run_degree3.sh` (41L): `counted()` requires all three RESULT lines per log; check mode re-emits all twelve scripts and `cmp`s each against the retained `.sing` before trusting counts; non-check mode runs Singular under `xargs -P` (exit 123 on any failure propagates through `set -e`); the mutant (relations 140→139) must be rejected, with `exit 1` if accepted.
- `shellcheck -S error` clean and `sh -n` passes on both drivers.
- Missing-file paths still fail closed (e.g., empty `ls` makes `wc -l < ""` error).

## Claim 5 — `boost_degree3.py` emits the A5-600 script with only the degree change plus truncation. **Holds (computed).**

- Byte-level diff of `bf-w2.sing` vs `d3-w2.sing` (and all twelve normalized pairs): exactly two regions differ — `kbase(std(ideal(0)),2)` → `,3)` on the ring-Y line, and truncation at the first `"RESULT targets"` with the appended stage end (`"RESULT targets",c;"RESULT relations",size(S);"RESULT done 1";quit;`). Everything else identical, for all twelve tags.
- Mechanism verified: `bq.relation_script` patched to degree 3 with the original closure, `bf.emit` imports the same patched module, and a missing `kbase(...,3)` raises. `size(S) = #syz(coeffs)` counts independent relations among the 220 normal forms of the degree-3 products; degree-2 calibration gives 21 = 55-34 ✓.
- All twelve retained `d3-*.log` files contain exactly `RESULT targets 220`, `RESULT relations 140`, `RESULT done 1`; stage data matches the README (`sq_size 994`, monomials 6891, std basis 1,777 generators; `syzygies_done 2222` ≈ the "2,040 s syzygy stage" after subtracting the 180 s pre-stage).

## Hilbert-value check behind A5-610. **Holds (computed).**

A5-600's numerator `1,0,-21,70,-105,84,-35,6` is w.r.t. `(1-T)^10` (10 variables; verified: H₁=10 ✓, no linear forms since minbase is 21 quadrics; H₂=55-21=34 ✓; H₃=C(12,9)-21·C(10,9)+70=220-210+70=80 ✓). Hence `(K2)₃` has dimension 220-80=140, and the measured L₃=140 with `(K2)₃ ⊆ L₃` gives equality: L₃=(K2)₃ and h₃(fiber cone)=80 at every listed value. The A5-610 inference and the README line ("first numerator 1, 0, -21, 70, -105, 84, -35, 6 in 10 variables") are correct.

## Integrity checks. **All pass (computed).**

- `sha256.txt` in both new dirs: 20 and 28 entries, zero mismatches, zero unlisted files (recomputed with `python3 -I`, hashlib).
- `expected-results.txt` is byte-identical to `results.txt` (`cmp` clean).
- Ledger: rows A5-608/609/610 added with the reviewed content; A5-599 amended only by the one-sentence pointer to A5-608/609; `quadric-ideals-macaulay2-p32009/` (the A5-599 directory) intact and unmodified.

## Structural statements the evidence suggests and no row states

Each with falsifier and cheapest check:

1. **The M2 wrapper is input-faithful (no algebra drift between Singular and M2).** The ideal files are derived verbatim from `parse_relation` text; the only degrees of freedom are file naming and whitespace. Falsifier: a wrapper that rewrites a coefficient (e.g., normalizing `1*i`). Cheapest check: parse a retained `qi-g*.txt` and re-derive its body from `w8_k2.rel` through the same code path — no M2 needed (done here for the headers; full body re-derivation is the residual gap, hypothesis until run).
2. **`intersect_equal true` implies the primary decomposition is complete, not merely consistent.** The check verifies `K = ∩ pd` inside M2; a truncated decomposition could still pass if it happened to intersect to K. Falsifier: a decomposition missing a component whose removal changes the intersection. Cheapest check: compare the number of primary components against `len minimalPrimes K` in the results (already visible: W8 two/two, g17 one/one, g21 three components vs two minimal primes — consistent with the (4,4) double structure, no gap).
3. **The twelve degree-3 relation spaces are all 140-dimensional, so the A5-610 statement is uniform in w.** No row asserts what makes all twelve agree; the row says "at each listed value", which is honest, but the uniformity itself is an observed regularity worth one sentence. Falsifier: any value with L₃ ≠ 140. Cheapest check: none beyond what the logs already show — this is an observation, not a theorem.
4. **Char-0 ideals over `Q(i)` are reductions of a number-ring ideal, so the M2 result is characteristic-0 evidence, not modular evidence.** The ledger states this via the iso rationale, but the structural point — the M2 run cannot detect modular-only artifacts, and vice versa — is the reason A5-608 and A5-609 are complementary rather than redundant. Falsifier: an invariant that differs between the 32009 arm and the Q(i) arm for the same source (none does: W8 agrees exactly).

## Findings, ranked by severity

1. **Non-dump reruns overwrite retained evidence in `quadric-ideals-macaulay2-w8-qi/`** (run_m2_qi.sh rewrites `m2-version.txt`, `W8-nm-p32009.log`, all `qi-g*.log`). Class: observed from source; not a false PASS. Same hazard in `run_degree3.sh` non-check mode (overwrites retained `d3-*.sing`/`.log`). Mitigation exists: dump + check modes are the safe paths; recommend the README or row state that non-dump/non-check modes mutate evidence. Severity: low.
2. **The M2 mutant gate accepts a log that printed `RESULT mutant K generators 67 ` then crashed** (no `DONE` required). The key number is still verified by grep, so this weakens only crash detection, not correctness. Cheapest fix: require `DONE` in the same grep. Severity: low.
3. **Check mode in `run_degree3.sh` trusts the retained logs' three RESULT lines without re-deriving them from the re-emitted scripts** (byte-compare covers scripts, not logs). Inherent to the retained-record trust model; a tampered log keeping the three lines passes. Severity: informational.
4. **A5-609's calibration-run timing ("run_m2.sh 63 s") is claimed but not verifiable from the tree** (no retained timing artifact). Harmless: it supports no invariant, only the replay-cost sentence. Severity: informational.

## Verdict

All five claims hold; the arithmetic behind A5-610 is independently recomputed and correct; both directories' digests verify byte-clean against the retained artifacts; both drivers fail closed under `set -e` with clean `shellcheck -S error`. The four findings above are robustness/hygiene notes, none of which undermines a scientific statement. The PR's additions (A5-608, A5-609, A5-610 and the A5-599 amendment) are sound and internally consistent with the cited A5-012, A5-421, A5-428, A5-446 and A5-599 records.
