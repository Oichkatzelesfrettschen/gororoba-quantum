# Archive branch imports

Every `archive/*` branch's unique content is either in the tree in a later
revision or retained here and in the paths listed below. A file whose branch
version differs from the tree's is resolved in favor of the later reviewed
revision; the branch commit stays reachable by its hash.

## Retained historical artifacts

| Artifact | Source commit | Status |
|---|---|---|
| `docs/evidence/{kernel_determinant,projective_kernel_limits,real_frontier_graphs}/resource-policy-replay.{json,md}` and `SHA256SUMS.resource-policy-replay` | `42b463a` (archive/codex-qpu-job-retention-reconciliation) | Receipts of the half-CPU worker-policy replay. They bind the source ledgers and `gororoba_quantum/parallel.py` as they stood at `42b463a`; both have changed since, so no gate rechecks them, and their checker `scripts/check_kernel_resource_policy_receipt.py` replays only at that commit. |
| `retained-run-channel-inventory.json` (this directory) | `37e2929` (same branch) | Runner, local and mock record inventory observed then. `scripts/inventory_retained_runs.py --out` regenerates the current inventory and keeps it outside `results/`. |
| `results/ripple/campaign-execution/README.md` | `ad12c82` (archive/qpu-campaign-execution-evidence) | Narrative of the reviewed campaign execution; every JSON it links was already in the tree. |
| `docs/notes/handbacks/repository_reconciliation_2026-10-17.md` | `8b0c3e7` (archive/tuna-zz-map) | The publication-time revision of the reconciliation report, later than the `9606658` revision the tree held. |

## Superseded in the tree

- archive/heron-citations-pre-rebase (`1d793b5`): the earlier wording of
  `docs/notes/heron_spatial_multiprogramming.md` and its module and tests;
  the tree holds the revised text and the `quadrature` and keyword-only
  `alphabet_size` interfaces.
- archive/kaggle-aer-runner (`adb795d`): every Kaggle runner, kernel,
  calibration snapshot and note file is in the tree at a later revision;
  `docs/notes/kaggle_gpu_simulation.md`, which the branch deletes, was
  replaced by `docs/notes/kaggle/`.
- archive/codex-qpu-job-retention-reconciliation (`cc6801d`): the CI gate
  runner, the inventory reconciliation and the retained-run inventory are in
  the tree at later revisions; the ripple measured records it rewrote are
  superseded by the current renders.
- archive/n21-orbit-rca-window-unitary-model (`0fa93f5`): the window-unitary
  model is in `scripts/n21_orbit_rca.py` (`window_segments`, `CompiledLaw`,
  `piecewise_fit`).
- archive/n21-window-bracket-refreshed-case (`5e77675`),
  archive/tuna-bipartite-walsh-and-lcu-packing (`6fc0af4`) and
  archive/qpu-campaign-findings (`9848cd2`): every file is in the tree with
  identical bytes.
- archive/tuna-zz-map (`8b0c3e7`): the static-neighbor ZZ cases are
  regenerated against the current Quantum Inspire catalogue (gates core-588
  to core-590), with identical circuits.
