# Source-bound evidence workbench

## Scope and ownership

The workbench extends the earlier visualization audit without modifying
retained experiments. Reusable validation belongs to `gororoba_quantum/`, the
command-line entry point to `scripts/`, and constructed behavioral tests to
`tests/`. The native partial-qubit numerical counterpart belongs to
`quantum_core` in gororoba-open. Document repositories remain source-custody
repositories; they do not receive copies of executable viewer implementations.

The [viewer components](../../gororoba_quantum/visualizations/evidence_workbench/README.md)
keep the existing original viewers and their evidence identities intact. No
provider request, new acquisition, acquisition approval, global mathematical
claim, or registry transition is part of this change.

## Build from a checkout

Choose an output outside retained inputs. The writer refuses an existing output
rather than silently replacing it. The ordinary build requires only Python's
standard library; source/raw replay additionally uses the repository's existing
parallel mapper. Browser use requires neither Python nor a server.

```sh
python -B scripts/render_evidence_workbench.py \
  --ramsey results/live/2026-10-13T201757.782152Z/ramsey-xy-trajectory-viewer/data/ramsey_observations.csv \
  --acquisition results/ripple/measured-ripple.json \
  --acquisition results/ripple/measured-rank-sector.json \
  --optical docs/evidence/ascella-order-coefficients/fixed-mesh-confirmation.json \
  --optical docs/evidence/ascella-order-coefficients/new-seed-score.json \
  --optical docs/evidence/ascella-order-coefficients/replication-score.json \
  --revision "$(git rev-parse HEAD)" \
  --out /tmp/gororoba-evidence-workbench.html
```

Repeat the identical command with `--check` to compare bytes without writing.
An independently chosen subset of the input flags is supported. Missing
workspaces show unavailable input, not fabricated records.

For source and raw-statistic verification, add one `--run-root` per acquisition,
in the same order. For the two acquisition paths above, the run roots are:

```text
results/live/2026-10-13T025444.603480Z
results/live/2026-10-13T032011.664435Z
```

The source hashes are checked before and after independent PUB replay. Each
PUB's register bitstrings reproduce its member histograms, shot-index blocks
and same-PUB joint event counts. The raw registers are combined in the retained
register order. This does not independently establish that the register map
matches the circuit in QPY. Use the original extractor's QPY-aware replay for
that separate obligation; never rename a byte-hash check as semantic replay.

## Admission levels

1. `payload_digest_and_internal_consistency`: the portable extraction's own
   digest, counts, probabilities, PUB membership, exact rank-normalization
   factors, block coverage and event moments agree. A maliciously rebuilt
   payload can still be internally consistent; this is not authenticity.
2. `source_files_and_raw_statistics`: additionally, the complete declared
   source-file hashes match and decoded raw register statistics reproduce.
   A bound QPY file receives a byte check, not circuit-semantic validation.
3. Circuit semantics, acquisition approval and physical execution chronology
   remain separate obligations. This viewer never awards that third level.

A synthetic marker persists through inspection and exports. An unknown replay
status cannot supply a visible execution-replay prediction. Retained endpoint
analyses remain in the original payload and are not recomputed or replaced by
new chart-dependent decisions.

## Statistical and geometrical invariants

The Ramsey coordinate family has `m = 2 * number_of_rows`; filtering never
reduces this family. For each expectation estimate, the simultaneous Hoeffding
half-width is `sqrt(2 * log(2*m/alpha) / shots)` at alpha 0.05, intersected with
[-1,1]. Independent stationary repetitions are needed within each circuit;
the union bound does not require independent errors across coordinates.
Interpreting outcome means as expectations of Pauli operators additionally
requires a common prepared state and calibrated measurement model. Unknown
readout bias is not included in the statistical interval.

The physical compatible set is the rectangular X/Y set intersected with
`x*x + y*y + z*z <= 1`. Its Z projection uses the rectangle point nearest the
origin. An empty intersection stays empty. The mesh draws sampled boundaries
of that set, not an observed state surface, a posterior density or measured Z.

The optional transverse estimator maximizes the sum of two binomial log
likelihoods on the unit disk. The multiplier and coordinate roots use bounded
bisection. Unequal shot counts generally rule out simple radial clipping.
Raw estimates remain retained, and no Z estimate is added.

Same-PUB covariance uses empirical population normalization by N, not N-1.
Displayed correlation is undefined when either event is constant. Exact
integer joint counts satisfy the marginal, Frechet and rational PSD checks.
The contingency order is neither, right only, left only, both. These checks
are necessary consistency conditions, not a proof that a table came from the
claimed device. Different PUBs are never paired by row number.

Shot blocks use service-returned array positions. Those positions do not
certify wall-clock chronology. No drift test or causal crosstalk attribution
is manufactured. Optical cohorts retain their frozen prediction columns and
original primary verdicts; no refitting, pooling, or substitute threshold is
introduced. Residual uncertainty is withheld without the required covariance.

## Interface and export contracts

The ordinary X/Y view uses equal screen units. Setting-space bounds cover the
rotated full cohort instead of a fixed box that can exclude permitted
rotations; filtering does not renormalize the cohort. Controls that have no
meaning in a selected geometry are disabled. Camera operation has native
range-control alternatives. Playback visits acquired settings only and
respects reduced motion. The table and previous/next buttons provide an
alternative to small scatterplot or matrix targets.

SVG carries visible context and structured metadata. PNG retains the visible
context but is not claimed to preserve SVG metadata. CSV string fields are
escaped against spreadsheet formula interpretation; numeric negatives remain
numeric. Saved views bind to the exact bundle identity and cannot relabel a
foreign dataset as the current one. External scripts, fonts, connections,
object embedding and form submission are denied by the standalone CSP.

## Validation commands

```sh
python -B -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
python -B -O -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
node tests/visualizations/test_evidence_math.cjs
python -B scripts/check_evidence_workbench_browser.py \
  --html /tmp/gororoba-evidence-workbench.html \
  --out /tmp/gororoba-evidence-browser-check
```

The browser checker supports `--engine chromium`, `firefox`, or `webkit` and
an optional `--executable`; an engine is tested only when its actual runtime
is installed and successfully invoked. A document-content harness is not a
native `file://` handler, screen-reader, Safari, or physical-touch test.

The development environment ran the constructed Python and JavaScript
contracts and Chromium checks. Pinned Ruff/mypy and the full repository CI
were unavailable locally. Full historical acquisition and raw-QPY replay
were not performed in that environment. These are open admission tasks, not
passed checks. Consult the pull request's latest receipts before merging.
