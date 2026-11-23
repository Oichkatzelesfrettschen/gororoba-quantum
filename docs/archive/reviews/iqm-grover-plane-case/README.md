# Review record: the Grover-plane case for a fourth Grover depth on Garnet (PR 987)

Subject: the written cases results/iqm/cases/grover-plane-mirrored (variant A, 52 circuits, mark 101 and mark 011 arms)
and results/iqm/cases/grover-plane-mirrored-101 (variant B, 38 circuits, mark 101 only), the plane model of
docs/design/iqm-garnet-grover-plane-model.md, the retained fits of docs/evidence/iqm-garnet-grover-plane/ and the
decision, calibration and sizing modules gororoba_quantum/grover_plane_{decision,calibration,analysis,sizing}.py.
The branch first carried a three-family case (results/iqm/cases/grover-fourth-depth-mirrored), which stays as
superseded.

Reviewers: codex on gpt-daybreak-blue at high effort (adversarial reviewer, rounds 1 to 5); agy Neon (red team, rounds 1
to 3; its round-4 session stopped at its quota); opencode on opencode-go/deepseek-v4-pro (red team, round 4, the owner's
substitute for agy). Each round read a fixed head; raw reports stay outside the tree.

| # | Round, head | Reviewers | Finding | Disposition |
|---|---|---|---|---|
| 1 | 1 to 3, three-family case | codex (rounds 1 to 3), agy (round 3) | The family contest could not name a mechanism: ZZ and coherent leakage both read "coherent" | Fixed by the plane redesign (merged at 1e9493ebe): one noisy iteration is a rotation (ideal plus eps), a contraction and a leak, the decision tests eps = 0 against eps != 0, and mechanism labels are readings |
| 2 | 3 | codex | The analyzer pooled raw counts, so unequal copy weights inside a mirror pair broke the palindrome's drift cancellation | Fixed by the plane redesign: equal-weight mirror-pair means with propagated binomial variances |
| 3 | 1 and 3 | agy | The response was a noiseless factorization, and the frozen model omitted the exact readout inversion | Fixed by the plane redesign: the response comes from the digest-bound circuit files at analysis |
| 4 | 3 | codex | Every z, chi-square and power was conditional on homogeneous copies (no overdispersion term) | Fixed by the plane redesign: the heterogeneity gate and covariance use the bound phi = 1.54 |
| 5 | 1 to 3 | codex, agy | The runtime estimate had no support | Fixed: billing v4 (PR 992) sizes both variants (scripts/iqm_grover_plane_sizing.py) |
| 6 | 4, 1e9493ebe | codex | A sole surviving mirror pair could not be tested by heterogeneity or influence | Fixed in 9c8a03714: every depth keeps two pairs after the shot floor, else "not evaluated" |
| 7 | 4 | codex | The mark contrast read after failed gates | Fixed in 9c8a03714 and acdd03d19: it reads only when both marks pass every gate and rotation adequacy |
| 8 | 4 | codex, opencode | "At most 0.0088 over the box" and the power wording claimed bounds the calibration does not give | Fixed in 5c43fbd77, a9a1b4781 and acdd03d19: rates are estimates at 99 evaluated cells, now read on held-out points |
| 9 | 4 | codex | The approval question used the wrong PRX ratio | Fixed: the question, decision and test share 1.194651206 |
| 10 | 4 | opencode | Khan and Faryad (arXiv 2611.16398) describe the plane reduction | Fixed in 2d8dae88a: cited; the plane model is an analysis frame, not a new result |
| 11 | 4 | opencode | The uniform complement of the retained full-outcome counts was untested | Fixed in c8080779e: rejected (shell weights gain 74.8 on 6 parameters); the depth-3 rotation survives in the uniform and per-qubit forms only |
| 12 | 4 | opencode | Power at abs(eps) = 0.01 and the run's framing | Fixed: power 0.435 at worst; the run is a prospective replication or refutation of the depth-3 anomaly, with no mechanism identified |
| 13 | 4 | opencode | The mark-011 arms buy a non-decisive contrast | Fixed in a9a1b4781 and acdd03d19: variant B drops them; variant A keeps them as a reading outside its paid question |
| 14 | 5, ed1abdb48 | codex | gate_failure() admitted an inadequate rotation fit when T < delta | Fixed in acdd03d19: rotation_adequate is required (grover_plane_decision.py:337), with a low-T regression |
| 15 | 5 | codex | The false-alarm rates were read on the points that selected delta | Fixed in acdd03d19: delta is chosen on Sobol' points 1 to 2^12 and rates are read on points 2^12 + 1 to 2^13 - 1, with exact binomial intervals labeled approximate; false "coherent" is at most 8 of 1,024 (0.0078, 95% interval 0.0034 to 0.0153) |
| 16 | 5 | codex | The response digest bound six points of a fit domain of s in [0.75, 1.15], eps in [-0.3, 0.3] | Fixed in acdd03d19: the digest hashes the fitter's 91 x 121 grid, and a test changes an off-grid value and breaks analysis |
| 17 | 5 | codex | Tests that injected fail_gate() and a vacuous leave-one-pair-out test; the boundary-cell count in the design note | Fixed in acdd03d19 and 599ce89d8: the tests drive the real gates; the note says 1,024 points |
| 18 | 4 and 5 | codex, opencode | Neither credit ceiling covers a 2.2-times overrun; the garnet:mock compile estimate is unread | Boundary: the owner decides the ceiling and the cancellation risk; garnet:mock runs first after approval |
| 19 | 4 | opencode | Contrast power omits the pair and readout gates | Boundary: variant A's paid question asks the primary test only; the contrast is a reading |
| 20 | 4 and 5 | opencode, codex | The continuation fits the retained run and evaluates it at the case calibration | Boundary: disclosed in CASE.md; the continuation is a reading, not part of the decision |
| 21 | 4 and 5 | opencode, codex | The case still emits a heterogeneity threshold table that the runtime recomputes | Boundary: harmless, the decision reads the recomputed threshold; the table leaves with the next successor |
| 22 | 4 and 5 | opencode, codex | The PRX-ratio interval covers its amplitude dependence only, and the readout copy floor is not modeled | Boundary: both limits are stated in CASE.md; the powers are conditional on the gates passing |
| 23 | 6, f94bdcdb7 | hosted Codex | The response grid ran 11,011 evaluations serially (P1) | Fixed in cec34a5aa: the table is built one row per s through parallel.ordered_map; the grid digest 8c7c597d is unchanged |
| 24 | 6 | hosted Codex | The always-on ZZ phase applied once per gate step, so overlapping gates counted the same time repeatedly (P2) | Fixed in 857c8c0a3, cases rebuilt in 19ce4109c: ZZ slope 2.0e-6 -> 7.4e-7 per Hz (mark 011 1.7e-7 -> 5.2e-8); ZZ -10 kHz power 0.983 -> 0.193 (0.193 to 0.659 over the corners); the ZZ truths leave the resolved set, the claimed worst resolved power stays 0.964 (PRX +0.8 percent), and the case is not sensitive to a ZZ coupling of 10 kHz |
| 25 | 6 | hosted Codex | A rotation fit clipped at eps = +-0.3 read in-domain (P2) | Fixed in d41e95c9a: decide() checks E_BOX whenever the rotation fit is selected; a planted rotation of 0.4 reads OUT_OF_DOMAIN |
| 26 | 6 | hosted Codex | The CLI analyzer always read the default case directory, so a variant B run was refused (P1) | Fixed in 924d6e11a: analyze takes --case-dir and otherwise selects the case the run records; a test drives variant B |

Acceptance at 599ce89d8 (Windows compute workstation): tests/test_iqm_grover_plane.py 38 passed (rerun by the
orchestrator); the repair worker's case checks of both variants, the retained replay, core-776, core-777, the complement
and sizing checks and the link check passed. cases.json sha256: A eec4e47f37aad02344a137548875cd673b4d8835cf79846726ca0cacad5f4011,
B f5d3d4a238fe08fdb85aff8dab142b655dfbd7acc024c9966700a7d470da7653.

Acceptance at 19ce4109c (Windows compute workstation): tests/test_iqm_grover_plane.py 42 passed; the case checks of both
variants, the retained replay, core-776, core-777, the complement and sizing checks and the link check passed.
cases.json sha256: A c107c8ba248715edc785b662dd6674642072aa8662ed5c3aa72271d119455806,
B 82cbb540d96bd70e7c3d745f0d5c13a579a9f879ea39cb276b64ae865b71ccb0.

## Retention of the Garnet run (pull request 995)

The seats read 6837f7d18: codex on gpt-daybreak-blue at high effort (reviewer) and opencode on
opencode-go/deepseek-v4-pro (red team). Raw reports stay outside the tree.

| # | Round | Seats | Finding | Disposition |
|---|---|---|---|---|
| 27 | 7 | codex, opencode | The result note said the case was built on calibration set ef4df2bb. The committed case binds a0e725eb, both run directories and the Garnet job bind 2951733a, and ef4df2bb is the garnet:mock station's own compilation | Fixed in f9472349c: the note names the three sets and what each record binds |
| 28 | 7 | opencode | "Garnet recalibrated between the build and the submission" has no support: the live rebuild read the current set and the job ran on that set | Fixed in f9472349c: the sentence is removed |
| 29 | 7 | codex, opencode | The note omitted the model and fit chi2 values (270.49 fixed, 104.27 geometric, 102.47 rotation) and the fitted a and s | Fixed in f9472349c: stated as measured, with no causal reading |
| 30 | 7 | codex | docs/runbooks/results-index.md still required a claim in the retaining change, against AGENTS.md "Records" | Fixed on main by another change before this branch merged it; the merge 5dc5f628a takes main's text |
| 31 | 7 | opencode | With the run directory as its own case directory, the analyzer's case-digest comparison is self-referential | Boundary: the reader first requires cases.json to match the submission's approved digest (gororoba_quantum/iqm_records.py), so the analysis reads the approved bytes; the committed case directory holds the earlier build and would be refused by design |
| 32 | 7 | codex, opencode | Raw files, job ids, billed credits (9 s at 0.5 credit/s), the replay's recomputation, the reading, the acquisitions and the runner-image exemption | Confirmed sound by both seats |
