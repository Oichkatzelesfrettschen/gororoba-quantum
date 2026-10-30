The replay is scientifically and numerically sound as a bounded post-acquisition description. I found no FATAL or SERIOUS defect. One SLOPPY regression-coverage gap remains.

## Findings

### SLOPPY — the new tests do not protect most of the new result or the exact `--check` contract

`tests/scripts/test_qi_tuna_joint_response.py:14-36` checks one disagreement vector and two selected parity components. Lines 39-63 check only four provenance paths. Lines 66-93 test receipt re-encoding and one marginal mismatch. The suite never checks:

- all 64 Walsh numerators;
- any reported denominator;
- empirical total variation;
- either uncertainty radius;
- normal or optimized `--check`;
- exclusive-output behavior.

A mutation such as changing `4 * SHOTS` to `2 * SHOTS` at `scripts/qi_tuna_joint_response.py:95`, or changing either radius formula at lines 104-105, remains reachable through documented `--out` while all four current tests remain green. Running `--check` against the supplied candidate would detect the changed bytes, but the test suite neither invokes that path nor binds the temporary candidate.

Reproduction:

```sh
rg -n -- \
  '(--check|empirical_total_variation|response_radius|endpoint_radius|parity_.*denominator)' \
  tests/scripts/test_qi_tuna_joint_response.py
```

The command returns no matches. Required closure is a retained exact candidate or receipt exercised through normal and optimized `--check`, plus explicit TV, radius, denominator, and output-exclusivity mutations. This gap affects regression assurance, not the current candidate’s arithmetic.

## Sound portions

I directly inspected all six source programs, manifests, submissions, collected job records, result histograms, and all 24,576 ordered width-20 raw strings. An independent standard-library reconstruction found zero discrepancies.

- Reversing each output string correctly makes array index \(k\) classical bit \(k\). Baselines use early bits `(17,18,19)`; rotated arms inverse-permute `(19,17,18)` into canonical qubit order `(4,11,6)`. Terminal bits are `(4,11,6)` (`scripts/qi_tuna_joint_response.py:36-40`).
- Applying the wrong unrotated decoder to the rotated arms produced frozen-marginal L1 discrepancies of 9,036 for nominal one and 9,276 for nominal zero. The frozen-table projection check therefore catches this concrete mapping error (`scripts/qi_tuna_joint_response.py:62-74`).
- All six 64-cell tables, eight disagreement cells, and 64 Walsh numerators matched independent counts. Exact Walsh inversion recovered every original 64-cell table.
- Every per-job Walsh numerator has denominator 4,096. Response contrasts use denominator 8,192; endpoint contrasts use 4,096 (`scripts/qi_tuna_joint_response.py:82-95`).
- Empirical total variation is correctly computed as
  \[
  \frac{\sum_x|2N_R(x)-N_B(x)-N_A(x)|}{4n}.
  \]
  The retained values are:

  - nominal one: `600/16384 = 0.03662109375`;
  - nominal-zero prefix: `7918/16384 = 0.4832763671875`.

- All six joint projections exactly reproduce the frozen three four-cell early/terminal tables.
- Source, raw, manifest, submission, job, collection, and receipt identities close transitively through the two fresh frozen replays before joint analysis (`scripts/qi_tuna_joint_response.py:115-145`). All 20 declared validator hashes and the producer hash matched current bytes.
- Normal and optimized exact checks both passed:

```sh
export PYTHON="${PYTHON:-python3}"
export GOROROBA_WORKERS=1
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" scripts/qi_tuna_joint_response.py \
  --check docs/evidence/tuna-projector-geometry/joint-response-analysis.json
"$PYTHON" -O scripts/qi_tuna_joint_response.py \
  --check docs/evidence/tuna-projector-geometry/joint-response-analysis.json
```

The martingale arithmetic is correct. For parity outcomes in \([-1,1]\), the response weights give total conditional range-square \(6/n\), while endpoint weights give \(8/n\). A two-sided union over \(63\times2\) parity/contrast combinations yields \(\log(25200)\), producing conservatively rounded radii:

- response: `0.086155685839`;
- endpoint: `0.099484016822`.

The bound tolerates adapted dependence because it targets realized predictable conditional averages, not IID population parameters. It protects post-selection among the complete 63-function Walsh family only. It does not cover arbitrary posthoc functions or the empirical total-variation statistic.

## Frozen decisions and scientific boundaries

The successor does not rewrite either frozen decision:

- nominal one remains `objective established within scope`;
- nominal zero remains `implementation route unavailable`.

`--out` uses exclusive creation, and `--check` is read-only (`scripts/qi_tuna_joint_response.py:156-168`). The serialized boundary explicitly refuses causal, population, and total-variation uncertainty claims (`scripts/qi_tuna_joint_response.py:146-150`). The plan likewise leaves mapping, physical mechanism, matched controls, and any new acquisition unresolved (`docs/state/plans/tuna-readout-mapping-identifiability.json:16-20`, `94-153`).

Unknowns remain the provider’s physical shot chronology, binary-label-to-population interpretation, thresholds, IQ, scheduling, calibration context, and causal destination attribution. A synchronized transient remains an observational counterexample to a destination-causal interpretation.

I did not run pytest, Ruff, mypy, the separate two-worker suite, or any provider-facing operation.

Verdict: **bounded PASS for the current descriptive candidate’s data bindings, decoder, arithmetic, uncertainty calculation, and preservation of frozen decisions.** Durable mutation-guarded retention should close the SLOPPY test gap above. This verdict grants no causal claim and no further hardware approval.