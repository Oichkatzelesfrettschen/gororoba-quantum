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

## Darwin measurement

The hosted `arm (macos-26)` leg (run 44670995561, head 67558e856) rebuilt the four QX manifests. batch-00 differs from the stored file at `$.circuits[1].ideal[0]`: rebuilt 0.124834861469, stored 0.124844028839. The difference is 9.2e-6, a numerical difference in a circuit ideal and not a sign of zero. The signed-zero hypothesis does not explain the macOS arm64 difference; the fix removes the signed-zero hazard only. A diagnostic run (44672793029, head 62c282dfb) printed the compile of b0 on the failing macOS leg only (CPython
3.14.7, qiskit 2.6.2, numpy 2.5.4, scipy 1.18.1, transpiler seed 22836; operation totals cz 21, rz 45, sx 49, 115
gates). Mapped through the region onto the pinned `b0.cq`, which the Linux replay test reproduces byte for byte, the
two sequences agree on positions 0 to 38 and differ at 13 of 115: six rz angles (position 39, the rz on `q[4]` right
after a CZ, reads pi/4 on macOS and -3 pi/4 in the file) and seven positions where the 10th and 11th CZ sit one slot
later, over the same 21 CZ pairs in the same order. The difference is therefore a platform-dependent compile of b0,
not float serialization; the repository already records it as the darwin-arm64 expected failure of
`test_b0_replay_is_byte_equal_to_the_retained_circuit`. Linux x86_64 and aarch64 agree, which leaves the macOS
numeric identity (libm or Accelerate) rather than the architecture. hypothesis: the pi shift is an Euler-branch
choice of the one-qubit resynthesis; the moved CZ are not explained by it.

## Fix

`retained_b0` builds b0 from the pinned retained `b0.cq` of the coin series, the circuit the hardware executed,
placed on the layout of b0's compile. The build refuses a compile whose final layout differs from the retained role
map, a gate line outside the emitter's vocabulary, a gate on a qubit outside the region or with the wrong number of
qubits, and a circuit that does not re-emit the pinned bytes. On Linux the
retained circuit equals the compile, so the stored manifests and receipt digests keep their bytes. The transpile
replay keeps its own test, which stays an expected failure on darwin-arm64. An integer or rational serialization is
not adopted. The `_b0_diagnostic` probe is removed from the test file.

Correction to [the brief](brief.md): the four receipt-bound manifests are
`results/quantum_inspire/cases/pathion_one_cz_null_bracketed_qx/batch-00..03/cases.json`; `pathion_one_cz_null_qx`
holds the predecessor series' three batches. The brief's third claim (a signed-zero cause) is refuted above.

## Second round (head 8f8b061bd)

Reviewers: `grok` (review), `agy` on gemini-3.8-flash-high and `opencode` on opencode-go/glm-5.3 (red team), on one
brief with the diff inlined. All three read 8f8b061bd; the worktree stayed clean. The two red-teamers ran Python probes
of the generator on the build host. Fixes land in faba8629c. The Advisor reviewed the round last at faba8629c and confirmed rows 1 and 3 to 12 as written, with rows 2, 7 and 13 after the checks their cells now name.

| # | Finding | Reviewer | Check | Verdict | Fix |
|---|---|---|---|---|---|
| 1 | "13 of 119 gates" is wrong; the totals give 115 | grok, opencode | cz 21 + rz 45 + sx 49 = 115; the diagnostic's last index is 114 | holds | 115 in the docstring, test comment and this record |
| 2 | The diagnostic printed the macOS leg only, so "agree on gates 0 to 38" compares macOS with the pinned file, not with a Linux print; 7 of the 13 positions are two CZ moved one slot | grok | the Linux job logs of 44672793029 hold no `transpiler_seed 22836` line; the macOS print, mapped through the region and compared line by line with `b0.cq` in the session, gives 115 gates each, 13 differing positions (rz angles at 39, 41, 58, 61, 63, 65; one rz moved across the 10th and 11th CZ shifts 49 to 55) and the same 21 CZ pairs in order | holds | the paragraph above states the comparison against the pinned file; the Euler hypothesis is narrowed to the pi shift |
| 3 | "The probe leaves the test file" reads as staying | grok, opencode | `git grep _b0_diagnostic` at 8f8b061bd finds this record only | holds | reworded |
| 4 | The brief names `pathion_one_cz_null_qx`; the receipts bind `pathion_one_cz_null_bracketed_qx` | opencode | `bc.QX_SERIES` is `pathion_one_cz_null_bracketed_qx` | holds | correction above; the brief keeps its text as the first round's input |
| 5 | The initial layout is not pinned; `fixed_qubit` reads the coin's start qubit | agy, grok, opencode | only the coin index of `initial_index_layout()` is read; opencode computed that only the coin's start run is Hadamard-equivalent, so a moved coin start is refused by `coin_fixed` | holds as a boundary: fail-closed, with a message naming the run rather than the layout | the docstring states the boundary; no initial layout is recorded to pin against |
| 6 | The arity guard and a qubit outside the region (bare `list.index` error) are untested or uncontrolled | agy, grok | read at `retained_b0` | holds | an explicit region refusal and two test cases |
| 7 | The global phase of the platform's compile is carried into the retained circuit | agy, grok, opencode | `copy_empty_like` copies `global_phase`; probabilities and the file ignore it | holds, no byte effect: the consumers of the plan's circuits use only `Statevector(...).probabilities()` and the `Operator.equiv` of the coin run (grep of the generators that read `series_plan`, `twin_entry` or `retained_b0`) | `global_phase = 0.0` |
| 8 | A stale comment says a darwin rebuild rounds differently | grok | test comment read | holds | rewritten |
| 9 | The build no longer exercises the transpile of b0 | agy, grok | `test_b0_replay_is_byte_equal_to_the_retained_circuit` runs in PR CI outside the audit marker on Linux | refuted as a loss: the check moved to that test | none |
| 10 | The predecessor series' rebuild runs only in the audit-marked gate | opencode | `test_the_committed_case_directory_reproduces_its_bytes` is audit-marked | holds as a pre-existing boundary; Linux equality follows from the replay test | not run in this pull request; on-demand gate |
| 11 | `TUNA_GATE` rejects an uppercase exponent, multi-comment files, a different comma spacing; the test reads the note at line index 5 | agy | the emitter writes lowercase `e`, one note line and `, q[` | refuted as defects: each case refuses, and the file is pinned | none |
| 12 | Other transpiles (the `select` search over 23,040 compiles) may move on darwin | agy | `select` is a `--select` mode, not a PR test | hypothesis, recorded | none |
| 13 | A gimbal-lock flip of `OneQubitEulerDecomposer('ZSX')` at theta near 0 moves phi and lambda by pi | agy | the printed command uses `np` without importing it, so it cannot have produced the printed output | reported, not reproduced; no weight. agy's "76 Tuna files identical" carries no command and no weight either | none |
