# Reconciliation of the review of pull request 961

One local reviewer ran, `codex` ([codex-report.md](codex-report.md)), on [the brief](brief.md). Each finding was checked
against the source at head `eb8c234e4`; every finding holds and is fixed by narrowing the claim or adding the test.

| # | Finding | Source | Check | Verdict | Fixing commit |
|---|---|---|---|---|---|
| 1 | High: the change does not establish platform-stable serialization; the docstring says values keep their digits on every platform | scripts/qi_pathion_one_cz_null_cases.py docstring of canonical_float; test comment on the darwin hypothesis | cited line read | fixed: the docstring states that only the signed-zero difference is removed, that a last-bit difference across a rounding boundary is not addressed, and gives the 4e-14 boundary distance with its platform; the macOS cause stays a hypothesis | 5b359bcf8 |
| 2 | Medium: only one of the two new tests fails on old code; the writer wiring has no failing regression | the retained-manifest test reads files only; the helper test needs the new symbol | cited line read | fixed: `test_the_manifest_writer_serializes_a_negative_residue_as_zero` feeds -1e-33 through the plan ideals, contrasts and twin ideals and asserts the written bytes hold 0.0; it fails against the script of origin/main and passes now | 5b359bcf8, 51fc9df04, 349755a3e |
| 3 | Medium: the 1200-of-2007 comparison has no retained source | git grep finds the number in one comment only; no output, versions or command retained | cited line read | fixed by removal: the number leaves the comment; the 4-of-4 byte equality on linux x86_64 and aarch64 stays, bound by the receipt digests | 5b359bcf8 |
| 4 | Low: every other value bit-identical is overbroad | a signaling NaN gains the quiet bit under + 0.0 | cited line read | fixed: the docstring reads every finite value | 5b359bcf8 |
| 5 | Low: the BLAS and FMA attribution has no source | the visible path is Statevector.probabilities() and NumPy accumulation | cited line read | fixed: the docstring and test comment read hypothesis: the sign follows the accumulation order of the probability computation | 5b359bcf8 |
