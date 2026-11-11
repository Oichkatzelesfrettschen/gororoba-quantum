# Reconciliation of the local review of the characteristic-0 quadrics branch (2026-11-11)

One local reviewer ran on [brief.md](brief.md): the `codex` command-line agent, read-only
([review-codex.md](review-codex.md)). The second selected reviewer, `claude-free` on the NVIDIA model, did not start:
its local gateway refused the connection, so it contributes no finding. Each finding below was checked against the
source before its disposition.

| # | Finding | Disposition | Evidence |
|---|---|---|---|
| 1 | `nfmodStd` gives no exact certificate for these inputs | survives, fixed in b5f24bb44 | `final_Test` of the installed `nfmodstd.lib` reduces the input by the result and checks that the result is a standard basis of its own ideal; it never reduces the result by the input. The README and the docstring of `quadric_lift.singular_script` now state the one-sided inclusion, and a modular record carries `relation_ideal`. |
| 2 | The direct and modular Iso records do not show equal Q(i) relation spaces | survives as a recording gap, closed by argument in b5f24bb44 | The modular ideal contains the relation ideal (finding 1), so its relation space contains the direct run's; both have dimension 68, so they are equal. Records written from that commit on carry `qi_echelon_sha256`. The retained pair was not rerun. |
| 3 | E8-bar to VB is compared at 32029 only | boundary, already stated | README ("Result for E8-bar -> VB") and ledger A5-315 name the single prime; the brief's sentence claimed both primes and was wrong. The 32009 comparison is not run. |
| 4 | The branch still presents the refuted lower-bound step of the modular transfer | survives, fixed in this revision | The governing note and active plans now require a common integral ambient model, compatible reduction and rank_Q(i) W_N = rank_F_p W_N. The README and ledger rows A5-249 and A5-277 preserve the good-reduction computations while stating that they yield no characteristic-zero lower bound by themselves. |
| 5 | An abrupt stop can lose Singular's stderr and the setup output | survives, fixed in b5f24bb44 | `runner.shim` appends stderr to `singular.stderr.log` as it is written and `runner.run_logged` appends the fetch and install output to `setup.log`; `tests/test_a5_kaggle_kernels.py` kills a stand-in Singular and fails a setup command and reads the lines back. The resource summary that `/usr/bin/time -v` prints at exit is still lost when the driver is killed. |
| 6 | The memory cause of the E8-bar stop is not retained | survives, fixed in b5f24bb44 | The README now reports exit status 137 as the observation and the memory limit as a hypothesis, and says that the workstation's out-of-memory lines sit in that host's journal and not in this tree. |
| 7 | The product loop of the Singular script is serial | boundary | The loop takes 716 s of a run whose next step, the standard basis of the relation ideal, did not finish in 27,718 s. The repository rule names loops through `parallel.py`, which runs Python workers; a split inside Singular forks processes that each hold the standard basis of J. Not changed. |
| 8 | A blank line at the end of the README | fixed in b5f24bb44 | `git diff --check` is clean. |

Not run: the `claude-free` review (gateway down), and the last review of the chain, which waits for the owner's
choice of its form.
