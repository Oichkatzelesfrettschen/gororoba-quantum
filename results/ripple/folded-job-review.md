# Independent folded-QPE raw audit

The retained evidence reproduces all 16 terminal-success estimates and all 12 recorded simultaneous intervals. Both raw job indexes verify every indexed file hash (20 files), and all 26 source-file hashes remain identical across the audit. QPY measurement mappings match the record. The audit found zero integrity or numerical defects in the tested surfaces.

Each of 16 PUBs contains 8,192 shots. The two jobs charge 29 s and 11 s. Raw shot indices are paired only within their own PUB.

| Contrast versus archived | s0 | s1 | s2 | s3 |
|---|---:|---:|---:|---:|
| delay | +1.917 pp | -0.330 pp | +0.403 pp | +1.501 pp |
| no_feed_forward | +0.952 pp | -14.709 pp | +0.549 pp | -16.235 pp |
| coherent | +6.177 pp | +5.823 pp | +10.938 pp | +7.825 pp |

Each contrast has a simultaneous-family half-width of 4.094505 percentage points. The four coherent intervals exclude zero positively; the odd no-feed-forward intervals exclude zero negatively. The other six intervals contain zero. The 12 precision contracts retain `reject_null=null`.

The bound uses alpha = 0.05 / 12 per contrast and alpha / 2 per separate PUB: `2 sqrt(log(4 / alpha) / (2 N))`. The claim assumes independent stationary repetitions within each PUB and permits arbitrary within-shot and cross-PUB dependence. Descriptive lag and half-shot checks do not prove stationarity.

| Timing surface | Seconds |
|---|---:|
| charged_seconds | 40.000000000000 |
| predicted_seconds | 39.632399872000 |
| service_execution_seconds | 35.571614464000 |
| scheduler_plus_repetition_seconds | 35.572154368000 |
| scheduler_minus_service_seconds | 0.000539904000 |
| charge_prediction_residual_seconds | 0.367600128000 |
| charge_minus_service_seconds | 4.428385536000 |

The forecast residual is +0.367600128 s (about 0.93 percent), with compensating execution and overhead errors. The scheduler-plus-repetition total exceeds the service metric by 0.000539904 s; the retained records do not attribute that residual. Charge minus the service metric totals 4.428385536 s. These observations validate timing accounting for the executed schedules only.

## Interpretation boundaries

- Coherent circuits use 69 CZ gates and terminal physical qubit 94; the dynamic circuits use 72 CZ gates and terminal qubit 93. Extra control and routing differ.
- The dynamic job and coherent job occupy adjacent but separate executor windows. Shared calibration timestamp does not establish stationary hardware noise.
- The delay arm replaces the first measurement and conditional feedback with a calibrated delay and a known-label unconditional phase correction, while retaining reset. It changes several mechanisms.
- Odd-label no-feed-forward ideal terminal success equals 0.5, while archived ideal success equals 1.0. The measured difference cannot isolate a noise-only controller effect.
- Each PUB carries one member and one replica. Matching numerical shot indices across distinct PUBs does not create paired observations.
- The displayed 95 percent simultaneous intervals require independent stationary repetitions within each PUB. Dependence within a shot or across PUBs is unrestricted by the union-bound construction.
- All delay confidence intervals include zero. The intervals establish bounded uncertainty; an equivalence claim needs a declared equivalence margin.
- Replay residuals compare hardware with retained finite-sample simulation results. Residuals identify model discrepancies but do not identify their physical cause.

## Ripple opportunities

- Keep hardware-minus-ideal, hardware-minus-noise-model, and packed-minus-isolated views separate. Odd no-feed-forward residuals reverse the sign found in all other arms, defeating a uniform subtractive success penalty.
- Preserve complete joint shot vectors within each ripple PUB; draw joint-error or covariance panels from those vectors and resample those vectors as indivisible units.
- Retain physical terminal-writer controls and matched routed templates. The coherent versus dynamic routing difference demonstrates why shared logical geometry alone is insufficient for causal comparisons.
- Use contrasts with declared thresholds and familywise uncertainty for inference. Label additional harmonics, kites, correlations, and phase portraits as descriptive until their multiplicity is qualified.
- Retain scheduler duration, repetition delay, service execution metric, and charged time separately. Forecast accuracy for these 16 PUBs does not bound denser ripple schedules.
- Render finite-shot uncertainty as an explicit data layer. A dark algebraic sector should show its exact predicted null and its measured leakage interval separately.

The odd no-feed-forward hardware-minus-replay residuals are +13.464355 and +10.424805 percentage points. The other 14 residuals are negative. These are model-discrepancy observations; the 12-family intervals above cover rung contrasts, not these exploratory residuals.

## Source hashes

| Source | SHA-256 |
|---|---|
| `record.json` | `91145c3456e8670a19eea258416412d020ca5e3fa71aa37b91ce7a5cb7f74670` |
| `collect.json` | `6de820a83905e778e7c11b2e75d729ee6a40311003716e47eff9834d2199aed9` |
| `isa.qpy` | `84b5c3c7703db74fdbd6eb477d131f5353a14d63befb7d3f5375c63a85acf6a1` |
| `settled-account-usage.json` | `4dc963474fbe30efac61ca7d7728b7e0ae2ee82c10a31151ce84ff326caa1977` |
| `raw/db67fqsvf2bc73d0pk4g/index.json` | `a0208a96859cf149a0aad8a1151cfd7ab8affd490d318822708aff199bff8434` |
| `raw/db67frimb58s738bci4g/index.json` | `97f4d3143d560296f3ab68f8ba16ba7f4ec7048c334205bddcdd546c177ad648` |

The JSON companion retains all raw-file hashes, integer counts, bit-level joint errors, exact contrast endpoints, scheduler durations, measurement sites, and job metrics. The audit script reads the retained run and writes only its selected output pair; `--check` compares the retained audit without writing files.
