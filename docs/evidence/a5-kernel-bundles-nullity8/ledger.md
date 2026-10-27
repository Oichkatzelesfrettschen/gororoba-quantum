# A_5 kernel bundles on the nullity-8 strata: ledger

State of the program set by [the program file](../../design/a5-kernel-bundles-nullity8-program.md). One row per
sub-step: date (UTC), item, probe, falsifier stated before the run, outcome (observed, inferred, or not run with the
reason), evidence path. [The evidence README](README.md) holds the durable results and their scope.

| Date | Item | Probe | Falsifier | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | 1, compact tangent ranks | Compute the compact `G_2 x U(1)` tangent rank at every nullity-eight representative and at exact noncompactly moved points; compare the 32-dimensional base-matrix rank with a direct complex-block rank. | Either implementation gives a different rank, a moved point changes open-orbit membership or nullity, or deleting the phase generator leaves every computed rank unchanged. | **Observed:** all twenty points retain nullity eight and their open-orbit membership pattern, both rank implementations agree, and every orbit reaches rank 15. The representative ranks are 12, 12, 15, 12, 12 on W8, E8-bar, Iso, X_+, X_-. **Inferred:** the generic ranks are 15 because a nonzero maximal minor stays nonzero on an open neighborhood; the local generic quotient dimensions are 8, 6, 6, 4, 4. The phase-deletion mutation changes downstream ranks. | [`compact-orbit-ranks.py`](compact_orbit_ranks.py), [`compact-orbit-ranks-result.json`](compact-orbit-ranks-result.json), [README](README.md#every-nullity-eight-orbit-has-generic-compact-rank-fifteen) |

## Questions we did not think to ask

| Question | Why it matters | Cheapest decisive probe | Result |
| --- | --- | --- | --- |
| Is any nullity-eight orbit homogeneous under the connected compact symmetry? | A homogeneous orbit would reduce its kernel bundle to one stabilizer representation and one associated-bundle calculation. | Compare the exact unit-section dimensions with the maximum compact tangent rank. | **Inferred:** none is homogeneous. The unit-section dimensions are 23, 21, 21, 19, and 19, while the compact group has dimension 15 and the exact rank probe reaches at most 15. |
