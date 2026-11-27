## Verdict

Eleven claims: 1, 2, 3, 4, 5, 9, 10, 11 hold; 6 holds except one count; 7 is falsified in the narrow sense below; 8 holds with one fixture caveat. Three defects, ranked.

## Defects, ranked by consequence

**1. The control check accepts a record the ledger says cannot exist.** `x_sign_transport.py:377` requires `set(flips) <= {0,1} and 0 in flips`, so a row with fourteen `1` entries and one `0` passes. Ledger A5-647 (`ledger.tsv:626`) and `README.md:1456` state that none of the 15 one-more-sign substitutions carries the ideal to the ideal. A record with 14 accepted substitutions would pass `problems()` and gate `core-a5-x-sign-transport`. No test covers this: `MUTATIONS` "every added sign accepted" sets all 15 (fails on `0 in flips`) and "fourteen added signs" pops one (fails on length). Fix: require `not any(flips)` and add a one-entry mutation. This falsifies claim 7's "would pass a wrong one".

**2. The README overcounts the mutations.** `README.md:1457-1458` says the test "rejects 22 mutations of a fixture". `tests/test_a5_x_sign_transport.py:65-87` defines 21 entries in `MUTATIONS`; the 27 passing tests are 21 mutations plus 6 other tests. The separate `test_another_weight_slice_matrix_is_reported` mutates a matrix, not the fixture. Correct the sentence to 21.

**3. `control_indices` is carried but never checked.** `x_sign_transport.py:417` puts `control_indices` in the exact field set but validates no value. The test fixture hardcodes header `control_indices [3,7,10]` (`tests/test_a5_x_sign_transport.py:36`) while the record has `[6,4,10]` (`x-sign-transport-result.json:156`); the fixture passes only because of this gap. `slice_module_map_comparison.py:296-298` does validate length 3, `min >= 1`, and `indices[1] != indices[2]`; reuse that check.

Minor: the archive and fibers READMEs say the X+ entry "comes from the X- row", but `build_registry.transport()` (`build_registry.py:300-328`) leaves `k2_sources` empty and copies only the degrees and certifications (`claims.json:2277-2280`). The next sentence explains the empty receipt, so the wording is defensible; it is worth saying "its degrees and certifications come from". The pre-run prediction is asserted only by ledger A5-647, with no separate retained artifact.

## Claims

1. **Holds.** With `D = diag(G_SIGNS)`, `f+∘S_w` has matrix `S_w M+ = M- D` and `S_h∘f-` has matrix `M- D`; `SQUARE` (`x_sign_transport.py:252-258`) compares exactly those. A transposition or wrong-side inverse fails, so the check is not a tautology. Row `k` of `induced-*.json` is `f(y_k)` in header generators, per `x_induced_slice_map.py:186-230`.
2. **Holds; falsifier empty.** `S_h` is diagonal with entries ±1, so `S_h = S_h^{-1}` and direction cannot matter. For `λ = ±1`, `1/λ = λ`, so the scalar is direction-invariant too. `witnesses.py` computes the same signs as `header_signs` (`x_sign_transport.py:224-258`).
3. **Holds as an argument.** A5-645 (`ledger.tsv:534`) records `c = 1/2` on X- and `-1/2` on X+, so `c+/c- = -1`; the record's `λ_h = -1`, `λ_w = 1` match. No inverted ratio or sign slip.
4. **Holds.** `NORMALIZED` (`x_sign_transport.py:88`) swaps exactly one `nrm` per slice: header changes `IMW` 1→0, weight changes `IMH` 0→1. The rename at line 335 labels `from_ = X-`, `to_ = X+`, matching `expected_images`.
5. **Holds.** `x-sign-transport-result.json`: `problems []` (line 2), signs (36, 71, 106), qi (118), header (195, 310, 425), weight (540, 658, 776), `slice_map` (845) equal to the diagonal of `W_SIGNS`, tools (1102-1105).
6. **Holds except the count.** The README's narrower "them" is safe because lines 1438-1439 already disclaim A5-638/A5-640/A5-644. Timings are measurements the brief excepts.
7. **Falsified narrowly.** See defect 1. The identity control and the three comparison controls do fail for the right reason.
8. **Holds with the caveat of defect 3.** The fixture reads no retained JSON: `expected_images` (`x_sign_transport.py:344-357`) uses the pure `X_MAP` table (`weight_slice_module_map.py:129`) and pure arithmetic (`quadric_and_germ_probes.py:514`). The mutation loop asserts every reported line contains `REASONS[name]` (lines 115-122).
9. **Holds.** `sha256sum k2-hilbert.jsonl` = `116222a7…49aa4`; `git grep -l 116222a7 | sed 's|/[^/]*$||' | sort | uniq -c` gives 20 arc-jets, 18 monomial-ladder, 2 kernel-attachments. Producers recompute the digest (`jet_rank.py:298-310`, `e8_target_basis_v2.py:~89`, `composed_limit_sections.py:649-663`, `nullity8_fiber_import.py:501-515`).
10. **Holds as recorded.** `git show --stat 10aed094b` = `ledger.tsv` only, 1/1; A5-548 at `ledger.tsv:527`. "Stays unheld" and "closed as unobtainable, not as read" agree; the two held works are the query results, not the unheld title. The query sentence is not offline-verifiable, but it contradicts nothing in the row.
11. **Holds.** `ci/gates.json:6167-6181` replays `x-sign-transport-result.json` with `--skip .tools.singular`; without `GOROROBA_SINGULAR_REQUIRED=1` it prints a skip and exits 77, not silently.

## Triviality

`λ_h = -1`, `λ_w = 1`, and diagonal `S_w` are derivable from retained records: A5-645 gives `c+/c- = -1`, the induced maps and `X_MAP` show the header maps differ by `-1` and the weight maps agree, and `witnesses.jsonl` holds the sign vector at 32009/32029. The run adds the explicit Q(i) 15×15 `S_w`, the 32057 header signs (no witness row), the Q(i) ideal and conjugate transport checks, the no-single-extra-sign control, and a replayed record. The README itself says the run is no independent evidence.

## Structural statement no record states

`S_w` is a diagonal involution and conjugation also carries `K_w(X-)` onto `K_w(X+)` (`transported [0,0]`, `conjugate [0,0]`). Hence `S_w∘conj` is an involution preserving `K_w(X-)`, a real structure on the 27-dimensional quotient, and the pair carries a Z/2 × Z/2 action. Falsifier: an off-diagonal `S_w` entry, a non-±1 sign, or `(S_w∘conj)(K_w(X-))` not contained in `K_w(X-)`. Cheapest test: square `slice_map` (all diagonal ±1) and reduce the composition against `K_w(X-)` over Q(i), one Singular reduction; the trace on the 15 generators is `-5`, while the trace on the 27-dimensional quotient is absent from the record.

## Rule compliance

`parallel.ordered_map` is used (`x_sign_transport.py:434`), no serial CPU loop; the new diff is ASCII-only with no absolute paths and no AI attribution; the change refreshes `ledger.tsv`, which satisfies the records rule. No violation of either `AGENTS.md` found.
