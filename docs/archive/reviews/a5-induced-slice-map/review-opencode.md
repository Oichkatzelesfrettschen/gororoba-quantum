I'll start by reading the governing guides and the change under review.

I have the evidence base; now I am confirming exact line numbers for the fail-open gates before writing the final report.

Read-only review of PR 994, head `f4633658f73ea388a847854dfd55aa414e8e689d` (branch `a5-induced-slice-map-and-orbit-checks`, parent `05f99ece3`). No file changed, no long job, no agents.

## FATAL: none

The four new evidence packages are internally consistent: hashes verify, the six induced-map checks and the twelve boost logs contain the values the READMEs and ledger rows report, and the M2 and probe records agree with their inputs. The serious issues are justification and gate coverage, not a false recorded number.

---

## SERIOUS

### 1. The `s2` argument in the induced-map README does not describe the computation, and the header-side truncation is unchecked

**File:** `docs/evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map/README.md:26-29`

**Evidence.** The README says:

> "The class of a header Pfaffian minus its combination is killed by s2, and an element killed by s2 that vanishes in the local ring at the origin is zero."

The computation uses the maximal ideal of all nine slice coordinates, not `(s2)`. `induced_slice_map.py:48` has `ideal T0=std(J+TR+m*PF);`, and `emit` at line 159 replaces the producer's `ideal m=maxideal(1);` with:

```python
"ideal m=" + ",".join(f"s{k}" for k in range(1, 10)) + ";"
```

so `m = (s1,...,s9)`. There is no `s2`-only ideal and no localization at `s2` in the emitted Singular. As written, "killed by s2" is either automatic in `I/mI` (every element of the maximal ideal acts as zero there) or not the vanishing argument the sentence claims. It does not establish that the constant matrix `G` is the map on `I/mI`.

The actual unverified step is the truncation. `weight_slice_fiber_relations.py:443-467` computes `dmax` as the maximum torus weight over the nonzero **weight-slice** Pfaffians, reports `pfaffian_inhomogeneous` for those, and builds `ideal TR=trunc(dmax)`. The header Pfaffians `HP` are never tested for homogeneity or maximum weight. `induced_slice_map.py:153` reduces each header Pfaffian modulo `J` only, and line 51 then reduces it modulo `T0 = J + TR + m*PF`. Terms of weight above `dmax` can therefore be discarded silently. The map logs print `pfaffian_inhomogeneous`, `pfaffian_max_weight 10`, `germ_inhomogeneous 0`, and `axis_unit`, but no header-weight line; `induced-nm.json` and `induced-np.json` have no header-weight field.

**Fix.** Compute the header weights and print `header_inhomogeneous` and `header_max_weight`; set `dmax = max(weight_dmax, header_dmax)`, or refuse a header with a non-homogeneous or overweight Pfaffian; add `header_inhomogeneous 0` and `header_max_weight <= dmax` to the `--collect` expectations and to the `problems` list. Rewrite lines 26-29 to state the computation actually performed (`m = (s1,...,s9)`, graded truncation at the maximum weight of both sides), or reintroduce the `s2` localization in the emitted code if that is the intended argument.

### 2. The six modular checks certify ideal equality at three primes, not that `G` is the induced map

**Files:** `induced_slice_map.py:252-303` (`check_script`), `README.md:60-65`, `docs/notes/topics/a5-exceptional-fiber-status.md:95`

**Evidence.** `check_script` builds `KW` from the 148 weight relations, `KH` from the header file, and the map `f` with the 21 images of `G`; it requires `a1 == 0`, `a2 == 0` (i.e. `f(KW) = KH`), `size(minbase(fK)) == 148`, `dim(sF) == 5`, `mult(sF) == 11`, `dt != 0`, plus the three non-membership controls. It never compares `G` with the geometric map on `I/mI`. A wrong Q(i) matrix that reduces to a correct map at 32009, 32029, and 32057 passes; so does any automorphism of `KH` composed with a valid map, since only the ideal is compared. The README acknowledges this at lines 60-65 ("the two maps need not be equal, and this directory does not compare them"; "The deduction that the induced map identifies the relation ideals is prose"). The status note line 95 headlines "The map that the change of slice induces ... A5-598, certified" without that qualifier.

**Fix.** Either add a direct Q(i) check (that the 21 header Pfaffians map to the 21 weight Pfaffians in the localized ring and that the composite is the identity on the fiber cone), or compare `G` with A5-583's map and report the difference, or retitle the status row and README table to "a generator map that identifies the relation ideals at six cells, with the identification a prose deduction". The last option needs no computation but must reach line 95 and the ledger label, not only the README's closing paragraph.

### 3. `run_boost.sh` does not gate several claims the README and ledger make

**File:** `run_boost.sh:14-21`

**Evidence.** The per-point gates are only: `RESULT done 1`, absence of a `?` line, `k_generators 21 dim 4 mult 7`, the exact `k_numerator`, exactly two `RESULT prime 4 [34] [43]` lines, `radical 1`, `frame_consistent 1`, and `frame_determinant_nonzero 1`. The README at `e8-vb-boost-family-p32029/README.md:33` claims "10 generators are selected at every value, and the germ has the retained component count," and ledger A5-600 claims the same. The logs print `selected_count 10`, `germ_component_count 1`, `adjugate_identity 1`, `pivot_pfaffian_at_origin_nonzero 1`, `germ_dimension 4`, `candidate_count 21`, `eliminated_count 0`, `reduced_j_count 17`, and `normal_form_size 21`; none of these lines is examined by the driver. A regression in the selection count, the component count, or the Schur-form adjugate identity would leave the driver green.

**Fix.** Add exact greps for `^RESULT selected_count 10$`, `^RESULT germ_component_count 1$`, `^RESULT adjugate_identity 1$`, `^RESULT pivot_pfaffian_at_origin_nonzero 1$`, `^RESULT germ_dimension 4$`, `^RESULT candidate_count 21$`, `^RESULT eliminated_count 0$`, `^RESULT reduced_j_count 17$`, and `^RESULT normal_form_size 21$`, or narrow the README/ledger claim to the invariants the driver actually enforces.

### 4. The prime-count and radical gates miss a third minimal prime of a different shape

**Files:** `run_boost.sh:18-19`; `boost_family.py:62`

**Evidence.** The driver requires exactly two lines matching `^RESULT prime 4 [34] [43]$`, but never requires `size(PL) == 2`. `boost_family.py:62` computes the radical check as:

```python
size(reduce(intersect(PL[1], PL[size(PL)]), sK)) == 0
```

which intersects only the first and last minimal prime. A third component of a different dimension (for example dimension 3) would not match the `prime 4 ...` pattern, would not contribute to the top-dimensional `dim 4`/`mult 7` invariants, and would not be intersected by the radical check. The ideal could then be non-radical while both gates pass.

**Fix.** Print `RESULT prime_count <n>` from `size(PL)` and gate it to `2`; compute the radical check over all primes (`intersect(apply(PL, ideal))`), or add `size(PL) == 2` to the `RESULT radical` condition.

### 5. The Gauss-image probe gates the predicted ranks but not the Gr(2,15) premise or the rank lower bound

**File:** `docs/evidence/a5-kernel-bundles-residuals/probes/bordered_kernel_gauss_image.py:285-292`

**Evidence.** `main` adds problems only for `degree_2_rank_stable`, `generic_point_control_rejected`, a degree-2 rank at the sample that differs from the 3,887/4,022 prediction, and tangency failures. It does not gate `hilbert_function_degree_1 == 105`, `coordinates_zero_on_every_kernel_zero_based == [0]`, `linear_forms_on_image == 15`, or `gauss_image_dimension_lower_bound == 15`, although README lines 777-780 and ledger A5-601 rely on them. The recorded JSON has all four values (105, `[0]`, 15, 15), so the recorded run is sound, but a regression in the coordinate-zero condition or the differential rank would pass silently.

**Fix.** Add all four to `problems` with their recorded values, and write them into the pre-run prediction. The degree-1 span of 105 and the scalar-coordinate zero are the evidence for the `Gr(2,15)` containment; the rank 15 is the evidence for the dimension lower bound.

---

## SLOPPY

### 6. `run_m2.sh` writes the M2 version but never compares it, and does not digest its inputs

**File:** `run_m2.sh:7-14`

**Evidence.** Line 7 writes `M2 --version > m2-version.txt`, yielding `1.25.11`, but no test compares the contents to `1.25.11`, which `quadric-ideals-macaulay2-p32009/README.md:3-5` claims. The loop reads five `.sing` files from `e8-rees-fibers-v2-kcompare-p32009` without checking that directory's `sha256.txt`; the local `sha256.txt` covers only the M2 outputs and inputs to the M2 run itself.

**Fix.** `test "$(cat "$D/m2-version.txt")" = "1.25.11"` before the loop; `(cd "$K" && sha256sum -c sha256.txt)` before reading the five ideals, and include the input digests in the M2 record.

### 7. `run_induced.sh` does not reject Singular error lines or bind the six header inputs

**File:** `run_induced.sh:12,20,26,29-34`

**Evidence.** `sing()` redirects both streams and ignores the exit status. `check()` greps only `^INDUCED VERDICT p $2 root $3 PASS$`; a `?` error line alongside a PASS would not fail the run. The six header relation files come from `e8-rees-fibers-v2-kcompare-p32009`, `e8np-d2-receipt...`, `distribute/out/...`, and `third-prime/...`; the driver checks none of their digests, and it does not record a Singular version.

**Fix.** After each `sing()`, fail on a `^?` line in the log; check the relevant `sha256.txt` for each input directory; write `Singular --version` to the run directory and compare it to the version the README names.

### 8. The generic boost run has no deadline

**File:** `run_boost.sh:33-37`

**Evidence.** The per-point loop and the generic function-field case invoke `Singular` without `timeout`. The boost README line 37 says the generic run had not finished after 46 minutes. A hang in either mode stops the driver indefinitely.

**Fix.** Wrap the generic `Singular` in a documented `timeout` (for example 3,600 s) and each per-point run in a shorter one (for example 120 s); treat a timeout as a failure, not a skip.

### 9. The status note keeps a stale open item and two dates

**File:** `docs/notes/topics/a5-exceptional-fiber-status.md:37,3/28,91`

**Evidence.** Line 37 lists as open "the map between the header slice and the weight slice of E8-bar over Q(i) (it exists modulo 32009, A5-583)," while line 95 and A5-598 compute that map over Q(i). The remaining open item is the machine-checked identification, which line 65 states correctly. The header dates (lines 3 and 28) say 2026-11-22; line 91 says "Results of 2026-11-23"; the commit timestamp is 2026-11-22 20:24:43 -0800 (2026-11-23 UTC).

**Fix.** Replace line 37's parenthetical with the line-65 phrasing ("a machine-checked form of the Pfaffian-ideal step that makes A5-598's map the induced map"); use one date throughout, or label the results section "2026-11-23 UTC" if that is the intended day.

### 10. The `certified` label is stronger than the rows' own text for A5-598, A5-600, and A5-601

**Files:** `docs/evidence/a5-exceptional-fibers/ledger.tsv` rows A5-598, A5-600, A5-601; `ledger.py:55-67`

**Evidence.** `ledger.py` defines `certified` as "a lower bound and a matching upper bound decide the value." A5-600 is twelve values at one prime; A5-601 records lower bounds only and says "not covered: ... equality of the ranks with the Hilbert function"; A5-598 says its identification is "deduction, not machine-checked." The row texts are candid; the status word is not.

**Fix.** Use `proved` for the exact finite computations (the six checks, the twelve boost ideals, the M2 result) and `survives` for the sampled or general claims, or define a `computed` status for "exact computation with a retained certificate" and use it here. Keep the status-note totals consistent with the changed labels.

---

## COSMETIC

### 11. The Hilbert-function sentence attributes Gr(2,15)'s function to the image

**File:** `docs/evidence/a5-kernel-bundles-residuals/README.md:777-780`

**Evidence.** "The image lies in `Gr(2, 15)` with Hilbert function 105 and 4,200 in degrees 1 and 2" reads as the image's Hilbert function. 105 and 4,200 are `Gr(2,15)`'s; the image's degree-2 span is 3,887/4,022. The ledger's version says "whose Hilbert function," which is correct. The following clause, "rank 15, the dimension of a family of projective planes over a base of dimension 13," mixes the differential rank with a dimension decomposition that the probe does not measure.

**Fix.** Write "the image lies in `Gr(2, 15)`, whose Hilbert function in degrees 1 and 2 is 105 and 4,200"; replace the dimension clause with the measured statement "the differential has rank 15, so the image dimension is at least 15."

### 12. The probe JSON has no field for the README's "quadrics beyond Plücker"

**File:** `bordered_kernel_gauss_image.py:267`; `bordered-kernel-gauss-image-result.json`

**Evidence.** `quadrics_on_image` is `7260 - rank` = 3,373/3,238, the total quadrics on the image. The README's 313/178 is `4200 - rank`, the quadrics beyond the 3,060 Plücker quadrics. The JSON records the former but not the latter; a reader must know the 3,060 to recover the table.

**Fix.** Add `quadrics_beyond_plucker = 4200 - rank` (or `quadrics_on_image - 3060`) to the record and use that field in the README table.

### 13. The induced-map JSONs do not record the six check verdicts

**Files:** `induced-nm.json`, `induced-np.json`; `run_induced.sh:29-34`

**Evidence.** The six `INDUCED VERDICT ... PASS` lines and the control values live only in `check-*.log`. The JSONs record the map, the 148 relations, the selected indices, and the relation digest, but not the checks; `sha256.txt` covers the logs, so the evidence is retained, but the machine-readable record is incomplete.

**Fix.** Have `run_induced.sh` append a `checks` array (cell, prime, root, verdict, control values) to the JSON, or write a `checks.json` and add it to `sha256.txt`.

### 14. The probe's default sample differs from the recorded run, and the probe directory has no manifest

**File:** `bordered_kernel_gauss_image.py:273-275`

**Evidence.** The default is 9,000 points; the recorded run and the README replay use 7,000. The prediction is sample-size-dependent, so running the script with no argument tests a different experiment. The induced, boost, and M2 directories each have a `sha256.txt`; the probe directory does not.

**Fix.** Make the sample argument required or default to 7,000; add a `sha256.txt` for the probe script and its JSON, or cite the ledger's digest for the probe.

---

## Verified sound

- **Pfaffian arithmetic:** the code's `AH[i,j] = (-1)^(i+j) Pf(minor)` with `AH[j,i] = -AH[i,j]` satisfies `B*AH = Pf(B) I` on a generic skew 6x6 matrix (sympy); `pf4(A,a,b,c,d) = A[a,b]A[c,d] - A[a,c]A[b,d] + A[a,d]A[b,c]` has the correct signs, and `quadruples = combinations(range(1,10),4)` is ascending.
- **Map direction:** `CH = Lm^T CW` and `G = inverse(transpose(Lm))` give `W = G H`, so substituting `y -> G y` into a weight relation gives a header relation. The 21x21 map is the correct inverse transpose for the lift the script computes.
- **Frame:** `header_frame` matches `nullity16_basepoints.py:239-246` (`_original_z_from_split`, `_c_matrix`, `_principal_frame`, `_transformation_matrix`), and the 21 selected indices match `nullity16-rees-fibers-result.json` for both orbits.
- **Induced checks:** all six logs show `transported modulo header 0`, `header modulo transported 0`, `generators 148 dim 5 mult 11 det nonzero 1`, `INDUCED VERDICT ... PASS`, and the control values in the README table; the 32009 N- and N+ logs also show the KA reduction `0 0`.
- **Boost checks:** all twelve logs show the gated invariants, the two primes `4 3 4` and `4 4 3`, `radical 1`, `schur_matches_retained 1` at `w=1`, and the ungated printed values (`selected_count 10`, `germ_component_count 1`, `adjugate_identity 1`, and the rest). The boost convention matches A5-428's `act_boost(5/4,3/4,·)`; `w=9115` is `i`, giving `(c,s)=(0,9115)`.
- **M2:** `results.txt` equals `expected-results.txt`, and `m2-version.txt` is `1.25.11`.
- **Probe:** the z/w split matches `kernel_frames._bordered_matrix` and `_original_z_from_split`; `closure_ideals()` returns split coordinates, so evaluating at the split x is correct. The recorded JSON has `hilbert_function_degree_1 105`, `coordinates_zero_on_every_kernel_zero_based [0]`, `linear_forms_on_image 15`, `gauss_image_dimension_lower_bound 15`, ranks 3,887/4,022, and no tangency failure.
- **Manifests:** `sha256sum -c` passes in the three new run directories (25, 28, and 11 files).
- **Ledger:** `ledger.py --summary` gives 579 rows: 216 proved, 119 certified, 113 survives, 62 refuted, 37 superseded, 12 open, 9 stalled, 7 rejected, 4 boundary, matching the status note.

The strongest claim I would remove or qualify before merge is the status note's unqualified "the map that the change of slice induces"; the strongest gate to add is the header-weight check on the induced-map side, because it is the one step that turns the six modular checks into the general argument the README describes.
