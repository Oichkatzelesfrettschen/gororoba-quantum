# Opus review: Ascella long-horizon seed repeat (job-08), commit e98d5b324

## Defects, most severe first

### 1. Byte-equal mesh identity reads float jitter as a redrawn mesh (blocks submission)

`scripts/ascella_long_horizon_reading.py:173` (rule at `:10-12`, stop at `:200-202`) counts a mesh as identical only
when its `computed_circuit` string equals the reference's byte for byte. The retained 2026-11-06 sim run shows that
the post-update stack writes the same mesh with different low bits:

- Sim job-02 replay against QPU job-02: 0 of 64 strings are equal, though the decompressed payloads have equal length.
- Deserialized with `perceval.serialization.deserialize(...).compute_unitary()`, 60 of 64 unitaries agree within
  1e-9. The median max|dU| is 3.2e-12 and the maximum is 2.4e-7.
- The four meshes above 1e-9 are all perturbed (`c17`, `c21`, `c22`, `c25`), and their largest phase difference is
  3.7e-7 rad. That is float jitter, not a re-solve.
- `computed_input` is equal in 64 of 64.
- Sim job-02 against sim job-08, and QPU job-02 against QPU job-03, are each byte-equal in 64 of 64.

If the QPU's post-update compile carries this jitter, M counts zero identical perturbed meshes and the run stops at
"not read". The plan (`ascella-long-horizon-seed-repeat-case.json:19`) and the design
(`ascella-signed-coherence-conformance.md:2109`) read that as "the service redraws the meshes", so the 1.03-credit job
ends as a false negative. Uncertainty is medium. It rises if `sim:ascella` shares the QPU's compile service.

The same evidence makes three statements false at the mesh level:

- Design `:2123-2124`, "served none of the QPU's meshes".
- The plan's reconciliation note, `:17`, "none equal to the QPU's".
- The research-state question at `research_state.json:2942`, whose answer is yes, to within 2.4e-7.

Fix, before acquisition:

- Define M as max|U_new - U_ref| at or below a fixed tolerance such as 1e-6, which sits above the jitter and far
  below heater resolution.
- Record both the byte-equal count and the within-tolerance count.
- Add a test: sim job-02 replay against QPU job-02 reads 64 of 64 within tolerance and 0 of 64 byte-equal.
- Correct the design text, the plan text and the research-state question.

### 2. Draw value 56 is consumed twice

`scripts/ascella_long_horizon_reading.py:176-178` seeds from value 56 of the repeat's order draw. `AGENTS.md`
("Seeds") requires each value to be used once, and two uses break that:

- The rehearsal, whose repeat is job-03, takes value 56 of `draw-2026-10-26T033936Z.json`, which
  `seed-repeat-reading.json` already consumed (`seed_index` 56).
- The job-03-against-job-08 and job-02-against-job-08 readings both take value 56 of the new draw, so they share
  relabelings.

The statistical harm is small, and `seed_provenance --check` scans literals only.

Fix: give each pair its own index and cite it in the plan and the design. Add `reserved` ledger rows.

### 3. Plan step states are stale

At `ascella-long-horizon-seed-repeat-case.json:32,38`, `request-builder` reads `doing` and `sim-rehearsal` reads
`todo`. This commit already freezes the body, retains both sim runs and writes the rehearsal. Fix: mark both steps
done.

### 4. Formatting churn in a functional commit

`scripts/ascella_coherence_request.py:678` rewrites `except (ValueError, PlatformError):` to the unparenthesized
py314 form. The form is legal, but `~/Projects/CLAUDE.md` puts formatting churn in its own commit. Fix: drop the hunk
or split it out.

## Checks that found nothing

1. **mesh_selection.**
   - With the identity in row 0, every p-value is (1 + b)/(1 + N), which is valid for persistence and useful slope.
   - One fixed sample with lost ≥ 0 keeps the p-value nonincreasing in b, so the bisection is monotone and the bound
     is valid. The identity keeps p ≥ 1/20001 at both infinities.
   - The exact path is unchanged (`relabelings_of(m, None)` is the old enumeration), and 22 tests pass.
2. **Reading script.**
   - A test pins the ceiling scaling, and delivered samples equal nominal in every QPU run.
   - Pairing by name, the identical subset, the anchor control and the order persistence, P1, P2 match the docstring.
   - The rehearsal replays with rc 0 and matches `seed-repeat-reading.json` on M, A, P1 and the exploratory values.
     P2's p-value differs (0.0003 against 0.00025, same ratio) only through the generator order, outside the plan's
     claim.
3. **Power record.** The model is as written, seeds spawn from value 57 into `ordered_map`, and `--power --check`
   returns rc 0.
4. **Request.**
   - `--check` returns rc 0 for every job, and no earlier case bytes change.
   - Job-08's settings equal job-02's by name except `observation_index`, and the anchors sit at stride 8.
   - Samples and shots are 64 × 32,768, the credit ceiling is 1.032768, and the fitted 199 s sits below 205 s.
5. **Written case.** Apart from defect 1 the text matches the code. The readings are fixed in advance, and S is the
   single primary reading.
6. **Repository rules.**
   - Seed ledger and research-state checks return rc 0, with the two sim runs listed as unclaimed, as expected.
   - The new text has no absolute paths, non-ASCII characters or British spellings.
