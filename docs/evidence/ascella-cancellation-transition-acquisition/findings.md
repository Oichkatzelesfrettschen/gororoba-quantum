# Ascella cancellation and transition findings

Six Ascella hardware jobs completed all seventeen frozen settings. The acquisitions retained **1,114,112 accepted events**, twelve physical output ports and every invalid photon-number category. The five cancellation jobs took four seconds each; the packed twelve-setting pilot took 37 seconds. Summed provider execution duration was **57 seconds**. Observed token-usage charges total **6.458752 credits**, below the 6.786432-credit ceiling. Queueing and collection add wall-clock time.

The [acquisition inventory](acquisition-inventory.json) binds every job, result hash, duration and charge. The [account observation](account-after.json) independently records six additional jobs, 57 additional seconds and 6.458752 additional consumed credits relative to the initial observation. Token occupancy after collection is zero running and zero queued. Remaining account balance and exact credit expiry remain unavailable to the job token; the account routes returned HTTP 404 and the connected-browser inventory was empty.

The [written case](README.md), [frozen profile](qualification-profile.json) and [campaign](campaign.json) preceded submission. The active [returned-mesh analysis](../../../results/quandela/ascella-cancellation-transition-returned-mesh-analysis.json) applies all 243 simultaneous endpoints, including missing-setting reservations. Every setting meets the fixed sample target and conditional interval-precision requirement. Confidence statements assume IID events within each setting.

## Cancellation

All five settings pass the frozen criteria. Herald fractions use all 65,536 returned accepted events per setting, including invalid outcomes in the denominator.

| Setting | Herald count | Herald fraction | Simultaneous interval | Qualification |
|---|---:|---:|---|---|
| dark | 147 | 0.2243% | [0.1621%, 0.3012%] | pass |
| bright | 65,276 | 99.6033% | [99.5039%, 99.6880%] | pass |
| bright-repeat | 65,354 | 99.7223% | [99.6377%, 99.7922%] | pass |
| dark-repeat | 116 | 0.1770% | [0.1224%, 0.2463%] | pass |
| fixture | 33,076 | 50.4700% | [49.7442%, 51.1956%] | pass |

The descriptive dark-minus-bright contrast is **-0.994621277**, with a derived simultaneous interval [-0.995978731, -0.992970843]. The contrast measures an output-probability difference rather than a state fidelity.

Both repeated arms returned byte-identical `computed_circuit` and `computed_input` serializations to their respective base arms. Their derived difference intervals lie inside the frozen +/-0.01 stability margin. Separate execution envelopes establish dark, bright, bright-repeat, dark-repeat, fixture order. The unequal gaps leave exact linear-drift cancellation unassessed.

## Dimension-six pilot

**The pilot fails qualification, so the full 54-setting campaign remains ineligible.** Six of twelve settings pass. The failure is retained as a hardware finding; the decision rule stays frozen.

| Computational identity input | Correct output | Nonlogical/invalid leakage | Qualification |
|---|---:|---:|---|
| 0 | 99.6597% | 0.2426% | pass |
| 1 | 99.6384% | 0.1999% | pass |
| 2 | 92.7719% | 6.2149% | fail |
| 3 | 99.4827% | 0.1755% | pass |
| 4 | 99.5102% | 0.1556% | pass |
| 5 | 94.6594% | 4.8462% | fail |

Identity inputs 2 and 5 fail both the 95% correct-output lower-bound requirement and the 2% leakage upper-bound requirement. Their leakage intervals are [5.8705%, 6.5721%] and [4.5406%, 5.1649%], respectively.

| Fourier-to-chirped input | Observed-to-returned-mesh TV | Simultaneous TV upper bound | Nonlogical/invalid leakage | Qualification |
|---|---:|---:|---:|---|
| 0 | 0.019075 | 0.036312 | 0.1434% | pass |
| 1 | 0.050678 | 0.068228 | 0.3586% | fail |
| 2 | 0.046857 | 0.064827 | 0.7553% | fail |
| 3 | 0.022756 | 0.040146 | 0.2167% | pass |
| 4 | 0.067259 | 0.087252 | 6.1691% | fail |
| 5 | 0.075648 | 0.092860 | 0.1678% | fail |

Cross-basis inputs 1, 2, 4 and 5 fail the conservative 0.05 total-variation upper-bound criterion. A failed upper-bound criterion establishes failure to qualify; it alone does not establish that the true distance exceeds 0.05. Cross-basis input 4 also fails leakage. Packed-array positions establish attribution, while physical ordering inside the pilot remains unassessed.

Every returned-mesh prediction passes its requested-distribution compilation check. The largest requested-to-returned-mesh total variation over all seventeen settings is 0.000325048. The hardware residuals therefore remain distinct from the small discrepancies represented in the returned mesh model. The acquisitions do not identify whether realization error, detection response, background counts or drift caused each residual. The six-dimensional intensity measurements establish neither arbitrary complex-amplitude tomography nor a universal bound on mutually unbiased bases.

## Analysis correction and independent review

The initial [screening report](../../../results/quandela/ascella-cancellation-transition-screening-analysis.json) computed cross-basis distances against the requested distribution. The frozen criterion requires the returned-mesh distribution. The corrected analyzer reports both distances separately and uses the returned-mesh bound for qualification. The initial report, [exact analyzer source](analysis-sources/requested-reference.py) and raw results retain their bytes. The correction preserves every pass/fail decision.

Independent local review decoded every raw histogram, checked all six raw hashes, reproduced every interval within 1.84e-14 across two Python runtimes, verified repeated meshes and execution order, and independently recomputed the returned-reference bounds. The new analyzer regressions distinguish requested and returned distributions and refuse qualification when the returned model is missing.

## Next scientific question

The failed pilot supports a separately preregistered mechanism-diagnostic study before broad acquisition: repeat failed identity inputs 2 and 5 beside passing controls, compare matched-mesh repeats with independent compilations, and permute logical outputs across physical ports. Such interventions can separate setting dependence, port response, compilation variability and drift. A new diagnostic case must freeze its sampling, mesh and multiplicity rules; repeating the pilot until qualification would change the inferential question.

An offline replay reads the collected runs and writes a successor analysis under an ignored local path:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 GOROROBA_WORKERS=4
"$PYTHON" scripts/ascella_experiment_analysis.py \
  --campaign docs/evidence/ascella-cancellation-transition-acquisition/campaign.json \
  results/quandela/runs/ascella-sedenion-cancellation-dark \
  results/quandela/runs/ascella-sedenion-cancellation-bright \
  results/quandela/runs/ascella-sedenion-cancellation-bright-repeat \
  results/quandela/runs/ascella-sedenion-cancellation-dark-repeat \
  results/quandela/runs/ascella-sedenion-cancellation-fixture \
  results/quandela/runs/ascella-dimension-six-transition-pilot \
  --out docs/local/ascella-returned-mesh-replay.json
```
