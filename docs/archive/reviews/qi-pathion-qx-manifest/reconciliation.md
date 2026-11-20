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

The hosted `arm (macos-26)` leg (run 44670995561, head 67558e856) rebuilt the four QX manifests. batch-00 differs from the stored file at `$.circuits[1].ideal[0]`: rebuilt 0.124834861469, stored 0.124844028839. The difference is 9.2e-6, a numerical difference in a circuit ideal and not a sign of zero. The signed-zero hypothesis does not explain the macOS arm64 difference; the fix removes the signed-zero hazard only. A diagnostic run (44672793029, head 62c282dfb) printed the compile of b0 on every leg. Both legs ran CPython 3.14.7,
qiskit 2.6.2, numpy 2.5.4 and scipy 1.18.1 at transpiler seed 22836; the compiled circuits agree on gates 0 to 38, and
gate 39, the rz on q1 after `cz q0,1`, reads pi/4 on macOS and -3 pi/4 on Linux. 13 of the 119 gates differ while the
operation totals match (cz 21, rz 45, sx 49). The difference is therefore a platform-dependent compile of b0, not
float serialization; the repository already records it as the darwin-arm64 expected failure of
`test_b0_replay_is_byte_equal_to_the_retained_circuit`. Linux x86_64 and aarch64 agree, which leaves the macOS
numeric identity (libm or Accelerate) rather than the architecture. hypothesis: the one-qubit resynthesis of the
transpile picks another Euler branch there.

## Fix

`retained_b0` builds b0 from the pinned retained `b0.cq` of the coin series, the circuit the hardware executed,
placed on the layout of b0's compile. The build refuses a compile whose final layout differs from the retained role
map, a gate line outside the emitter's vocabulary, and a circuit that does not re-emit the pinned bytes. On Linux the
retained circuit equals the compile, so the stored manifests and receipt digests keep their bytes. The transpile
replay keeps its own test, which stays an expected failure on darwin-arm64. An integer or rational serialization is
not adopted. The `_b0_diagnostic` probe leaves the test file with the change.
