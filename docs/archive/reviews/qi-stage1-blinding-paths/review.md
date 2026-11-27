# Review: the stage-1 blinding check strips checkout and scratch paths

Pull request 1030 changes `tests/scripts/test_qi_replicated_series.py` alone (pool row QPU-69). The owner chose the
Advisor as the only local reviewer (2026-11-27). Head under review: `2c9097721`.

## Findings and resolutions

| Finding | Resolution |
|---|---|
| The guard must keep its strength: every blinded word (0.0123, mean, residual, lag1, order_difference, block) still fails the check outside a path | `_blinded` removes only the checkout root and the test's scratch path, longest first, then searches for every word; `test_blinding_check_ignores_the_paths_and_reads_the_rest` fails on a blinded word beside a path |
| The test file might be pinned by digest, since the series is pre-registered | Its sha256 (9eecc954...) appears nowhere in gororoba-quantum or gororoba-open |
| The path reaches stderr through a RuntimeWarning of `order_difference` | The offline stand-in alternates the residual sign by replicate, so each parity half has zero variance and the Welch degrees of freedom are 0/0; hardware replicates do not reach it, and the pre-registered analysis stays unchanged |

## Residual risk

A future warning that quotes a source line holding a blinded word would fail the check again; that failure would
point at a real leak path into stderr, which is the check's purpose.
