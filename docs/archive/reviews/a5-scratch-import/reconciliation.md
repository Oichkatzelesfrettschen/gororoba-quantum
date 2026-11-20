# Review: import of the a5 exceptional-fiber scratch runs

Pull request 955 of gororoba-quantum. Reviewers: the `codex` command-line agent (gpt-daybreak-blue, high effort, read-only), run with `--ignore-user-config` during a startup stall of the user configuration that the infrastructure session later could not reproduce, and the Advisor, last; then the hosted Codex round that this repository's guide requires before the owner's merge.

## Findings and reconciliation

| Finding (codex, f2946933f) | Check | Resolution |
|---|---|---|
| P2: 18 entries of `xpm/SHA256SUMS` and of `SOURCE-DIGESTS.tsv` name `.git` metadata that is not imported | Confirmed. | Fixed in 0f644a0be: the entries are removed, and `sha256sum -c` passes in every touched directory. |
| P2: machine-local absolute paths remain | Confirmed for four files: one `/mnt/c` path and three `/tmp` paths. | Fixed in 0f644a0be and the next commit: the absolute PowerShell path reads `powershell.exe`, and the temporary paths read the plain token `SCRATCH`, the convention of `retain_working.sh` (the Advisor found the first placeholder, `<scratch>`, a shell redirection in a retained script). The digests listed are those of the new bytes, and `SOURCE-DIGESTS.tsv` keeps the source digests. The paths in `engine/v11/out/n18-singular-version.txt` stay: they belong to the upstream Singular package's build tree (`/host/var/tmp/sage-local-...`), not to the workstation, and the README says so. |
| P3: the `kl-out` README asserts an unrecorded rerun equality | Confirmed. | Fixed: the README now says the cause is not recorded. |
| P3: the `kernel-limits-variants` README names no generator | Confirmed. | Fixed: the README states the files are scripts and names the run scripts that ran them. |
| Claim 4 (no code copies; every file under 1.5 MB) | Justified. | - |

## Advisor

The Advisor read 0f644a0be. It confirmed the git-metadata P2 and both P3s, and found a defect in the path fix: the placeholder `<scratch>` parses as shell redirections in `band-mesh.sh`. The next commit replaces it with `SCRATCH` and settles two further points the Advisor raised:
- **Layout.** `scratch-runs/` stays a level of its own. `retain_working.sh` imports the fiber working directory into `working/`, and these runs come from a different directory whose file names collide with `working/`.
- **Ascella run.** `band-mesh-out`, which is Ascella band evidence, leaves the a5 tree.
