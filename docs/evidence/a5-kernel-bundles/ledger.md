# A_5 kernel bundles: ledger

State of the program set by [the program file](../../design/a5-kernel-bundles-program.md). Durable results and replay
commands live in the [evidence README](README.md). One row per sub-step: date
(UTC), item, probe, falsifier stated before the run, outcome (observed, inferred, or not run with the reason), evidence
path.

| Date | Item | Probe | Falsifier | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-10-26 | 1: kernel transport and `J` | Compute exact right kernels of `L_y` and `A(z, conjugate(z))` at B9, V, VB, V^a_+, V^a_-, N_+, and N_-; test `phi`, `conjugate(phi)`, and `J = L_(e_16)` on every basis vector. | A representative escapes `ker A` under `conjugate(phi)`, has real nullity different from twice the complex nullity, or violates either `J` phase identity. The program's unbarred `phi` formula survives if every exact kernel basis maps into `ker A` without input conjugation. | **Observed:** `conjugate(phi)` maps all 92 real kernel basis vectors into `ker A`; dimensions 12 = 2(6) and 16 = 2(8) prove equality at the representatives. `J` preserves every kernel, `phi(Jx) = i phi(x)`, and `conjugate(phi(Jx)) = -i conjugate(phi(x))`. The program's unbarred formula fails at all seven representatives. Both mutations fail in normal and optimized Python. | [`kernel_symmetry.py`](kernel_symmetry.py), [`result.json`](result.json), [`README.md`](README.md#the-transport-uses-the-conjugated-input) |
| 2026-10-26 | Baseline | Start the repository pull-request test lane before Item 1 implementation. | Any test failure would make the starting baseline ambiguous. | **Not run:** `ci/pr_checks.sh tests` could not acquire the shared host-environment lock because the sandbox makes `~/.cache/gororoba-quantum/host-envs.lock` read-only. The focused exact test ran instead; this row makes no repository-wide baseline claim. | terminal observation recorded in the executing session; focused replay in [`README.md`](README.md#replay) |
| 2026-10-26 | Process: local commit | Stage the proved sub-step for the required local commit. | The linked worktree Git index accepts its lock and records the five evidence files. | **Not run:** Git could not create `.git/worktrees/a5-kernel-bundles/index.lock` because the sandbox presents that path read-only. The working-tree files remain unstaged. | `git status --short`; retry when the Git metadata path is writable |

`BLOCKED: owner` — the program file's established-facts table and first ordered item omit the outer conjugation in the
transport identity. Repository source authority and the exact result above require the orchestrator to replace that formula with
`phi(y x) = A(z, conjugate(z)) conjugate(phi(x))` and to state the kernel identification through
`psi = conjugate o phi`. The evidence program can continue without that prose edit.

Resolved 2026-10-26 by the orchestrator: the program file's facts table and item 1 now carry the outer conjugation
and `psi = conj o phi`. The sub-step is committed by the orchestrator after review and replay; the sandbox keeps git
metadata read-only by design, so the agent never commits.

`Ruling:` the Lie algebra of `K` means the projection of constant triples `(G, H, H')` that satisfy
`L_(G y) + L_y H = H' L_y` for every doubly pure `y`; one `H'` serves every `y`. Allowing `H'` to depend on `y` would
reduce the condition to pointwise kernel preservation and would not define the requested linear symmetry group. Cost if
wrong: a different quantifier in the owner specification would require a new symmetry object and a fresh solve.

The next exact solve starts with this falsifier: the compact real `G_2`, base phase, base scaling, and universal fiber
scalars must lie in the projected solution, while the boost must stay outside it. Any missing expected direction, any
lifting boost, or any computed basis triple that fails one multiplication-table coefficient refutes the proposed Lie
algebra. The solve will report every additional direction rather than truncate the answer to the expected subgroup.

## Questions we did not think to ask

| Question | Why it matters | Cheapest decisive probe | Result |
| --- | --- | --- | --- |
| Does the bordered-matrix kernel model require coefficientwise conjugation of `phi(x)`? | The answer decides which complex bundle represents `ker_R L_y`; omitting the conjugation replaces the fiber by a generally different subspace and can reverse odd Chern-class signs. | Apply `A(z, conjugate(z))` exactly to `phi(x)` and `conjugate(phi(x))` for a rational basis of `ker_R L_y` at every nullity-12/16 representative. | **Investigated:** the conjugated input succeeds on all 92 basis vectors and has the required dimension; the unbarred input fails at all seven representatives. Thus `ker_R L_y = (conjugate o phi)^-1(ker_C A)`, while `phi(ker_R L_y) = conjugate(ker_C A)`. |
