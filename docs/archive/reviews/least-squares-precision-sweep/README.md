# Review record of the portable least-squares precision sweep

These files are the briefs, reviewer reports and reconciliation of the portable least-squares precision sweep
(`docs/evidence/least-squares-precision/`), first opened as pull request 808 on branch
`least-squares-precision/portable-sweep` and carried into the integration branch with every one of its commits
(54359a760, 315d929bb, 068f1b71d, 549328395, 5ba6b3791). The one-page disposition table is
[../2026-11-09-least-squares-precision-sweep-review.md](../2026-11-09-least-squares-precision-sweep-review.md).

| File | Holds |
|---|---|
| [brief-implementation.md](brief-implementation.md) | Brief for the subagent that made the sweep portable (`fp_host.py`, the per-OS memory cap, the thread ladder, `--host-label`) |
| [report-implementation.md](report-implementation.md) | That subagent's hand-back: build-host acceptance and the open rulings |
| [brief-remote-hosts.md](brief-remote-hosts.md) | Brief for running `fp_export.py` and `fp_sweep.py` on each remote host and copying its rows back |
| [brief.md](brief.md) | Codex brief for the first review, commits 54359a760 and 315d929bb on main e2a694e7b |
| [review-codex.md](review-codex.md) | `codex` on gpt-daybreak-blue at high effort, range `e2a694e7b...315d929bb` |
| [brief-nemotron.md](brief-nemotron.md) | Read-only brief for `claude-free` on NVIDIA nemotron-3-ultra at 5ba6b3791 |
| [review-nemotron.md](review-nemotron.md) | The nemotron report the reconciliation read |
| [review-nemotron-second.md](review-nemotron-second.md) | A second nemotron report on the same brief, reconciled in the addendum; it records no head, and its citations fit 5ba6b3791 |
| [rows-summary.tsv](rows-summary.tsv) | One line per retained row (file, line, configuration, status, cap mechanism, scores, skip reason), the table the nemotron brief supplied and the second report cites by line |
| [brief-pr.md](brief-pr.md) | Codex brief for the whole pull request at head 5ba6b3791 |
| [review-codex-pr.md](review-codex-pr.md) | `codex` on gpt-daybreak-blue, range `origin/main...5ba6b3791` |
| [reconciliation.md](reconciliation.md) | Every finding checked against the rows and the source, the fix commits, the Advisor verdicts and the addendum |

The texts are the reports as written, with these substitutions so the public record carries no local path and no
machine name: `<workspace>` stands for the workspace root that holds the gororoba repositories and `<worktree>` for
the branch worktree of `least-squares-precision/portable-sweep`; the former machine names of the quaddtype records
read as their sweep labels (zen4-wsl, zen4-windows, m1-macos, turion-linux), as do the record paths, which name the
successor files; and kernel release, distribution, OS product and memory-size strings read as their category. The
reconciliation adds one passage of its own, the addendum, which opens with the owner's ruling on the quaddtype
residual. The briefs and the reconciliation name report paths under the ignored `docs/local/reviews/`; the reports
are the files listed here.

Left out of the public record, each listed with its reason; the files stay in the ignored
`docs/local/archive/least-squares-precision-portable-sweep/` of the primary checkout:

- the codex session logs `codex-sweep.log` and `codex-pr808.log`, the claude-free run log `claude-free.log`, and the
  harness stderr and exit-code files of the three nemotron launches: command transcripts;
- `codex-pr808.done`: an empty completion marker;
- the nemotron input bundle's `diff-full.patch`, `diff-code-and-docs.patch`, `diff-stat.txt` and `git-log.txt`: the
  branch history reproduces them;
- its `host-records.json`: the full host profiles, with the kernel release, distribution and memory size the owner
  ruled out of public rows;
- `briefs/sweep-review.md` and `briefs/sweep-claude-free.md`: the round-one brief with only its report line changed;
- `pr-body.md` and `pr-body-808.md`: drafts of the PR 808 description, whose final text stays on that pull request;
- `run-sweeps.sh`, `sweep-full.log`, `sweep-quick.log`, and the CI logs `runs/ci-lint.log` and `runs/ci-types.log`:
  the README's command block reproduces the build-host run, and the rows hold its results;
- the build-host `fp-inputs.npz` and the remote-host tarball `bundle/gq-sweep.tar.gz` with its `bundle/paths.txt`:
  `fp_export.py` and the tracked sweep files rebuild them, and each row records the input digests;
- a first nemotron report that could not read its brief outside its working directory and summarized the README
  instead.
