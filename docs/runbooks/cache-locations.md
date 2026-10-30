# Cache locations and periodic cleanup

This runbook lists every location outside the checkout where the repository's
work leaves environments, builds, logs and run outputs, and classifies each
by what deleting it costs. It is the specification that a future
`make clean` and `make distclean` implement. Until those targets exist, an
operator runs the commands below by hand. Deletion goes through `trash-put`,
so `trash-restore` recovers a wrong path; `trash-empty DAYS` later purges
entries older than DAYS. Paths are written with `~`, and the repository
cache is `${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum`, written `$GQ`
below. `du -sh PATH` gives a location's current size.

## Classes

Each location belongs to one class, and the class decides who may delete it.

| Class | Deleting it costs | Rule |
|---|---|---|
| scratch | nothing | trash entries older than 14 days |
| rebuildable | a rebuild command and its run time | trash when its inputs changed or space matters; rebuild before the next use |
| retained | run outputs that may exist nowhere else | delete only after confirming that the evidence they hold is merged into the repository or deliberately abandoned |
| credential | provider access | never part of a cleanup |

## Repository cache `$GQ`

| Location | Class | Contents and rebuild |
|---|---|---|
| `$GQ/*.log`, `*.err`, `*.changed`, `*.txt`, `*.md`, loose `*.py` and `*.sh` | scratch | gate, test, Codex-wait and rebind logs and one-off helper scripts written by earlier sessions; no gate reads them |
| `$GQ/session-scratch/` | scratch | a session's saved local diffs and notes; read a `.patch` before trashing it, since one can hold uncommitted work from a dirty checkout |
| `$GQ/probe/`, `$GQ/gpu-probes/`, `$GQ/a5-e8bar/` | scratch | probe outputs and gate logs whose findings live in the docs that cite them |
| `$GQ/premerge/` | scratch | premerge gate cache keyed by tree digest ([ci/AGENTS.md](../../ci/AGENTS.md)); a miss reruns the gate |
| `$GQ/rebind-logs/`, `$GQ/kaggle-msolve/`, `$GQ/kaggle-singular/` | scratch | rebind run logs, and generated Kaggle kernel directories with their templates; the generators (`make_multi.py` and its template) live in the same directories, so keep them while a kernel family is still pushed |
| `$GQ/ci-py3.14.7/`, `$GQ/replay-py3.14.7/` | rebuildable | the host environments of the pinned CI and replay runtimes; `sh ci/build_host_envs.sh` rebuilds both under `host-envs.lock` ([ci/AGENTS.md](../../ci/AGENTS.md), Host environments) |
| `$GQ/host-envs.lock` | rebuildable | the lock that rebuild holds; trash it only when no check runs |
| `$GQ/runner-image/` | rebuildable | the local CI runner image, its pin layers and receipts ([ci-runtime.md](ci-runtime.md)) |
| `$GQ/wheels/` | rebuildable | locally built wheels, among them the CUDA Aer wheel of `packaging/qiskit-aer-cuda/` |
| `$GQ/venv-passagemath-singular/`, `$GQ/venv-kaggle-sdk/`, `$GQ/seekpath-venv/` | rebuildable | task venvs: passagemath Singular and msolve, the Kaggle SDK, SeeK-path; recreate with `uv venv` and the pins of the doc that uses each |
| `$GQ/held-runs/` | retained | QPU run directories held outside the tree until their retention PR merges; check `docs/state/research_state.json` for each job before deleting |
| `$GQ/a5-fiber-runs/` | retained | the durable copy of A_5 Rees-fiber runs from Kaggle, Azure and the host, synced from the session scratchpad; delete only after the A_5 evidence that cites them lands |

## User data `~/.local/share`

Only these entries belong to the repository's work. The rest of the
directory belongs to other applications and is outside this runbook.

| Location | Class | Contents and rebuild |
|---|---|---|
| `~/.local/share/quantuminspire/venv` | rebuildable | `QI_ENV`, the Quantum Inspire provider interpreter `QI_PYTHON` ([Quantum Inspire](../notes/quantum_inspire/README.md)) |
| `~/.local/share/openquantum/venv` | rebuildable | `OQ_ENV`, the Open Quantum interpreter `OQ_PYTHON` ([Open Quantum](../notes/open_quantum/README.md)) |
| `~/.local/share/qiskit-skills-validation/venv` | rebuildable | the venv that validates the Qiskit agent skills ([AGENTS.md](../../AGENTS.md), Qiskit skills) |
| `~/.local/share/uv`, `~/.local/share/pipx` | rebuildable | uv-managed interpreters and tools, and pipx tool venvs; shared with other projects, so trim with `uv cache prune` and `pipx` rather than trashing the directories |
| `~/.local/share/Trash` | scratch | the trash itself; `trash-empty 30` purges entries older than 30 days |

## Build caches outside the repository

| Location | Class | Contents and rebuild |
|---|---|---|
| `~/.cache/uv` | rebuildable | uv's wheel and download cache; `uv cache prune` drops unreferenced entries, and `uv cache clean` drops all of them at the price of re-downloading |
| `~/.cache/paru/clone/*` | rebuildable | AUR build trees (python-qiskit, macaulay2 and others); `paru -Sc` trims them, and a package rebuilds from its clone |
| `~/Github/PKGBUILDs/*/src`, `*/pkg` | rebuildable | makepkg working trees of the local PKGBUILDs; `makepkg -C` rebuilds clean. Keep each directory's newest `*.pkg.tar.zst`, which `pacman -U` reinstalls offline |
| agent session scratchpads under the system temporary directory | scratch | session scratchpads; long runs sync their results to `$GQ/a5-fiber-runs/` before a scratchpad goes |

## Never cleaned

The cleanup never touches credentials: `~/.qiskit/qiskit-ibm.json`,
`~/.quantuminspire/`, `~/.config/<provider>/` key files, `~/.config/kaggle/`
and the model-proxy environment file. It also never touches worktrees under
`~/worktrees/<repo>/`; a worktree leaves through `git worktree remove`
([AGENTS.md](../../AGENTS.md) and the user guide's branching rules).

## Targets for a future Makefile

- `clean` trashes the scratch class: `$GQ` logs and loose scripts older
  than 14 days, `$GQ/probe`, `$GQ/gpu-probes`, `$GQ/a5-e8bar`, `$GQ/premerge`,
  `$GQ/rebind-logs`, and `$GQ/session-scratch` entries whose patches have
  been read.
- `distclean` does what `clean` does and also trashes the rebuildable `$GQ`
  environments and images. `ci/build_host_envs.sh` and the task-venv
  commands rebuild them.
- No target deletes the retained class, the credentials or the user-level
  provider venvs, because each of those needs a per-item check.

Each target prints the paths it trashes and their sizes before acting. It
refuses to run while `host-envs.lock` is held, since a check is then
reading those environments.
