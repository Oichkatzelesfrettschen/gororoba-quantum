# Review: portable least-squares precision sweep (2026-11-09)

Two rounds by `codex` on gpt-daybreak-blue at high effort (range e2a694e7b..315d929bb, then head 5ba6b3791 of
`least-squares-precision/portable-sweep`), one by `claude-free` on NVIDIA nemotron-3-ultra, each checked against the
host rows in `docs/evidence/least-squares-precision/hosts/`, then the Advisor last. The fixes land on
`integration/gororoba-quantum-ultrareview`.

| Finding | Disposition | Resolution |
|---|---|---|
| M1 input digest differs | Survives | Equality scoped to the five hosts with equal digests; the M1 is its own cohort |
| Host rows exceed a public profile | Survives | Rows keep architecture, CPU model, SIMD dispatch, BLAS core and version, package versions and OS family; kernel release, distribution, memory size, macOS product version and Windows release dropped (owner ruling); `fp_export.py` validates its label |
| Cap prose | Survives | The M1 ran uncapped; `enforced` is the trial scope's readback |
| QuadBLAS disabled on the Windows wheel | Survives | `fp_host.quadblas_status` skips exactly the 12 quaddtype configurations (now a test) |
| Missing M1 comparison receipt; unretained SIGILL claim | Survive | Marked not run |
| Stale portability prose; "pinned wheels in a venv on every host" | Survive | Versions stated per host from `host.packages` |
| Required lanes never check the sweep programs | Survives | `ci/pr_checks.sh` lint and types name `fp_host.py`, `fp_sweep.py`, `fp_export.py`; mypy then found a reused loop name in `fp_export.py`, fixed; `tests/scripts/test_least_squares_precision_sweep.py` covers redaction, label refusal and the QuadBLAS skip |
| Nemotron: RLIMIT probe imports numpy before the map | Refuted | An enforced RLIMIT_AS refuses the cap plus 256 MiB map whatever numpy reserved |

Owner ruling: `cap.bytes` stays, as the limit the run applied. Not run: the M1 npz receipt, a numpy 2.5.4 probe on the
Turion host and a Windows rerun (remote hosts), and a per-child cgroup readback. The four machine-named
`quad-falsification/` records give way to successors under the sweep labels with the OS family only (owner ruling).

The briefs, every reviewer report and the full reconciliation, with its addendum on a second nemotron report, are
in [least-squares-precision-sweep/](least-squares-precision-sweep/README.md).
