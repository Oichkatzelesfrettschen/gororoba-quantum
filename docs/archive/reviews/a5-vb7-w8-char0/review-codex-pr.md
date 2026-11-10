# Adversarial pull-request review: VB degree 7 export and W8 characteristic zero

[proved] The review covers `git diff d970b76f3...19384c76a`: Python and shell launchers, engine v13 against v12,
all 54 changed Singular inputs, both design documents, ledger rows A5-279 through A5-283, and the records those rows
cite. The fields are exact computational algebra, evidence provenance, Python and POSIX-shell control flow, and
reproducible job orchestration. The 34 ladder inputs passed a mechanical filename/order/algorithm check; all changed
Singular inputs contain a ring and terminal `quit;`. Provider work and remote work stayed outside the review.

## Findings ranked by consequence

### 1. SERIOUS: the Kaggle launcher converts failed Singular jobs into a successful kernel

[proved] `run()` returns each Singular `returncode`, and the parent stores the resulting dictionaries, writes
`summary.json`, prints it, and reaches normal Python termination. The parent performs no aggregate return-code check
(`docs/evidence/a5-exceptional-fibers/vb-export-levers/kaggle/make_kernels.py:38-52`). A Singular timeout therefore
produces job `rc = 124` inside a kernel whose process exits 0. This behavior directly falsifies claim 3 for the Kaggle
launcher and can make a failed export look green to Kaggle automation.

[proved] The shell repairs cover a narrower boundary. Explicit PID waits return 1 for a child that exits 7, the serial
status accumulator returns 1, `xargs` returns 123, and `run-cells-v13.sh` returns 2 for five arguments. The shell
launchers still trust process status as their completion oracle. Ledger A5-281 records that interrupted Singular runs
can exit 0 without a result (`docs/evidence/a5-exceptional-fibers/ledger.tsv:280`), while `run-lifts.sh` and
`run-probes.sh` validate no required `RESULT` line or output artifact. The new 32009 cofactor log demonstrates the
shape: it contains setup only, while its time record says exit 0
(`docs/evidence/a5-char0-transfer/cofactors/lift-xm-nm-p32009.log:1` and
`docs/evidence/a5-char0-transfer/cofactors/lift-xm-nm-p32009.time:1-23`).

Remedy: preserve `summary.json`, then exit nonzero when any job has a nonzero `rc`, lacks both required digests, or
lacks the expected terminal `RESULT` fields. Give every shell job an analogous completion-marker and artifact check.
Add a fake-child regression test covering nonzero exit, timeout 124, zero-exit missing output, and success.

### 2. SERIOUS: both committed Kaggle kernels fail the repository's mandatory Python gates

[computed] Pinned Ruff 0.17.4 reports 22 errors in the two generated kernels: E501, E401, E402, I001, E702, and E741.
Pinned mypy 2.4.1 reports four errors at lines 24-25 because the inferred summary dictionary accepts neither the jobs
dictionary nor `total_seconds`. The failures occur in both
`docs/evidence/a5-exceptional-fibers/vb-export-levers/kaggle/a5-vb-d7-slimgb-p32009/a5-vb-d7-slimgb-p32009.py`
and the corresponding `p32029` file. Repository policy requires Ruff formatting, Ruff checking, and mypy on every
touched Python file (`AGENTS.md:36-42`).

[proved] No test or CI file mentions `fiber_rank_v13`, `make_kernels`, `a5-vb-d7-slimgb`, or `run-cells-v13` (`rg`
over `tests`, `ci`, and `.github` returned no match). The earlier final review already required a small-order export
identity test before v13 evidence promotion; the branch adds generated production jobs without that test.

Remedy: make `RUNNER` formatted, type its summary as `dict[str, object]`, generate bounded source lines, regenerate
both kernels, and run the pinned three-tool sequence on the generator and its outputs. Add a deterministic test that
regenerates into a temporary directory, compares committed bytes, and compares v12/v13 `s`, `qB`, and tables on a
small order.

### 3. SERIOUS: the topic status still schedules the cofactor certificate that A5-282 refutes

[proved] The revised plan correctly replaces noncanonical `lift` cofactors with a canonical degree-bounded RREF,
both conjugate roots, and exact identities over Q(i)
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:120-148`). Ledger A5-282 correctly marks the one-root/support
certificate `refuted` (`docs/evidence/a5-exceptional-fibers/ledger.tsv:281`). The topic status nevertheless says a
“cofactor-identity route” is next and schedules “modular cofactors reconstructed and checked”
(`docs/notes/topics/a5-exceptional-fiber-status.md:38,78`). That stale route can dispatch the exact computation the
branch has just shown cannot certify the claim.

Remedy: replace both topic-status passages with the canonical bounded system, two-root divisibility check, rational
reconstruction, and exact Q(i) verification. Link A5-282 so the rejected certificate stays rejected.

### 4. SERIOUS: A5-279 gives a falsified operational claim the status `stalled`

[proved] A5-279 claims that the engine-v11 degree-7 order-22 job “fits the 3-hour run cap,” then records both cells
still inside the export at 3:02 (`docs/evidence/a5-exceptional-fibers/ledger.tsv:278`). The three-hour fit is decided
against by the row's own evidence. `stalled` is appropriate for an undecided mathematical claim such as A5-248; it
is inaccurate for a bounded-time claim after the bound elapsed. The new 24-hour v13 campaign is a different method
and cannot rescue the historical v11 claim.

Remedy: mark A5-279 `refuted`, or rewrite its claim as the measured statement that both v11 attempts exceeded three
hours and keep a status consistent with that statement. Track the v13 campaign in a separate row after retained
results exist.

### 5. SLOPPY: the scope and detailed plan give different order-22 cost bounds

[computed] The detailed plan derives 22,300 to 89,300 seconds from the retained order-20 measurements and the
observed 1.45-to-2.90 step ratios
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:35-46`). Direct recomputation gives 22,062 to 89,313 seconds before
the plan's rounding. The scope instead states 22,700 to 81,600 seconds
(`docs/design/a5-open-tasks-and-compute-scope.md:65`). The upper bounds differ by 7,700 seconds, so claim 6 fails its
own “number differs from its record” falsifier.

Remedy: make one cited calculation the source of both documents, and label the subsequent division by the measured
`slimgb` factor as an extrapolation tied to host and load.

## Claims under review

| Claim | Verdict | Evidence boundary |
|---|---|---|
| 1. Engine v13 changes only the reduced-basis algorithm and preserves export identity | **Supported within its stated mixed proof/measurement status.** | [proved] The v12/v13 diff changes only documentation, the version string, and `std` to `slimgb`; fixed `dp` plus `redSB` gives the unique reduced basis. [measured] Order 13 binds equal basis, kbase, and tables; order 15 binds one known rank. An all-order runtime regression remains untested. |
| 2. The levers and cofactor certificate are correctly refuted | **Supported.** | [measured] Tail reduction is slower and the seeded run already exceeds the matched baseline at order 15. [proved] Noncanonical lift solutions and the one-root Gaussian counterexample refute the proposed certificate. |
| 3. Every launcher propagates failure and the cell launcher refuses more than four cells | **Refuted in part.** | [computed] The shell PID/xargs paths propagate nonzero status and five cells return 2. [proved] The Kaggle parent exits 0 after nonzero job return codes, and zero-exit incomplete Singular work lacks a completion check. |
| 4. Kaggle outputs are byte-comparable with workstation exports | **Supported as a prospective interface claim.** | [computed] The committed job dictionaries exactly match the current generator. Canonical jobs preserve the same ring, ideal, `redSB`, `slimgb`, `kbase`, and `short=0` write representation. The branch contains no completed order-21/order-22 cross-host comparison. |
| 5. AGENTS.md records the owner's ruling without loosening other provider rules | **Supported.** | [proved] Kaggle retains a written case and timeout; owned-host runs require falsifier, host, measured-rate estimate, memory budget, and deadline. Every other provider job, upload, paid machine, booking, and provider QRNG read retains prior approval. |
| 6. The scope and plan contain only record-supported numbers | **Refuted.** | [computed] Finding 5 gives a direct numerical contradiction. The retained VB shares do support 94.528 to 98.648 percent, and the W8 receipts support 6,559.564/9,860.33-second product-and-basis stages plus 325.071/575.423-second membership stages. |
| 7. A5-279 through A5-283 match their evidence and statuses | **Refuted in part.** | [proved] A5-279 has the status defect in finding 4. A5-280 is conservatively `survives`; A5-281 and A5-282 are `refuted`; A5-283 remains `open`. A5-282's 32009 pilot is sourced indirectly through A5-248 and the prior review rather than by its own direct evidence list. |

## Checks

[computed] `git diff --check`, `sh -n`, ShellCheck at warning severity on all six shell launchers, the 144-record plan
tracker, and all 1,117 Markdown link and anchor checks pass. The in-memory generator replay reproduces both committed
job lists and deadlines exactly. Pinned Ruff and mypy fail as finding 2 records. No QPU, provider, Kaggle, cloud, GPU,
or remote computation ran.

## Steelman and verdict

[proved] Engine v13 is a disciplined versioned successor: the algorithm substitution is minimal, the uniqueness
argument is sound under the fixed global order, and the retained order-13 comparison checks more than rank alone.
The plan also correctly retracts the noncanonical cofactor certificate, preserves the characteristic-zero gaps, and
keeps `degBound` open rather than promoting a seductive optimization without a certificate. The Kaggle canonical jobs
carry enough information for a real byte comparison once they finish.

The mathematical core survives, but the pull request is not merge-ready. The Kaggle launcher can publish a successful
kernel after failed jobs, both generated kernels fail mandatory Python gates, stale status text revives a refuted
certificate, and two record-governance claims contradict their own evidence. Repair the failure oracle and generated
Python first; then reconcile A5-279, the topic status, and the order-22 estimate before treating the branch as a
reproducible execution surface.
