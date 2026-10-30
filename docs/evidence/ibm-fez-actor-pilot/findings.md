# IBM Fez full-register pilot: descriptive analysis

The approved pilot supplies 24 full-register PUBs and 73,728 recorded shots. Each paired cell uses error bits relative to the commanded input; bit 0 is reporter 0 and bit 1 is reporter 1. The retained receipt replay validates the indexed raw bytes and QPY mapping. The source record leaves provider same-shot physical alignment, immediate predecessor order and statistical admission unverified.

This is an exploratory analysis. The case supplies no valid confidence procedure for dependence or adaptive selection. Submitted order does not establish physical execution order. Activity contrasts are associated differences, not identified causal effects. Repetition-delay comparisons also change the job and acquisition period.

## Paired error cells

Cells are [00, 01, 10, 11] for the two error bits. Rates and G appear in percentage points; G = p11 - max(p01,p10). Each row stays separate by prepared input and activity arm.

| Delay (µs) | Input | Arm | Shots | Error cells [00,01,10,11] | p0 (%) | p1 (%) | Parity error (%) | G (pp) |
|---:|---:|---|---:|---|---:|---:|---:|---:|
| 30 | 00 | active | 4096 | [3930, 90, 73, 3] | 1.855 | 2.271 | 3.979 | -2.124 |
| 30 | 00 | idle | 4096 | [3954, 89, 53, 0] | 1.294 | 2.173 | 3.467 | -2.173 |
| 30 | 01 | active | 4096 | [3883, 87, 124, 2] | 3.076 | 2.173 | 5.151 | -2.979 |
| 30 | 01 | idle | 4096 | [3846, 102, 143, 5] | 3.613 | 2.612 | 5.981 | -3.369 |
| 30 | 10 | active | 4096 | [3903, 133, 58, 2] | 1.465 | 3.296 | 4.663 | -3.198 |
| 30 | 10 | idle | 4096 | [3929, 108, 55, 4] | 1.440 | 2.734 | 3.979 | -2.539 |
| 30 | 11 | active | 4096 | [3834, 125, 133, 4] | 3.345 | 3.149 | 6.299 | -3.149 |
| 30 | 11 | idle | 4096 | [3811, 120, 161, 4] | 4.028 | 3.027 | 6.860 | -3.833 |
| 50 | 00 | active | 4096 | [3973, 68, 55, 0] | 1.343 | 1.660 | 3.003 | -1.660 |
| 50 | 00 | idle | 4096 | [3954, 81, 60, 1] | 1.489 | 2.002 | 3.442 | -1.953 |
| 50 | 01 | active | 4096 | [3882, 72, 142, 0] | 3.467 | 1.758 | 5.225 | -3.467 |
| 50 | 01 | idle | 4096 | [3896, 67, 131, 2] | 3.247 | 1.685 | 4.834 | -3.149 |
| 50 | 10 | active | 4096 | [3918, 107, 69, 2] | 1.733 | 2.661 | 4.297 | -2.563 |
| 50 | 10 | idle | 4096 | [3946, 99, 47, 4] | 1.245 | 2.515 | 3.564 | -2.319 |
| 50 | 11 | active | 4096 | [3843, 116, 134, 3] | 3.345 | 2.905 | 6.104 | -3.198 |
| 50 | 11 | idle | 4096 | [3852, 96, 144, 4] | 3.613 | 2.441 | 5.859 | -3.418 |
| 250 | 00 | active | 1024 | [994, 17, 13, 0] | 1.270 | 1.660 | 2.930 | -1.660 |
| 250 | 00 | idle | 1024 | [993, 17, 14, 0] | 1.367 | 1.660 | 3.027 | -1.660 |
| 250 | 01 | active | 1024 | [980, 18, 25, 1] | 2.539 | 1.855 | 4.199 | -2.344 |
| 250 | 01 | idle | 1024 | [983, 12, 26, 3] | 2.832 | 1.465 | 3.711 | -2.246 |
| 250 | 10 | active | 1024 | [978, 31, 15, 0] | 1.465 | 3.027 | 4.492 | -3.027 |
| 250 | 10 | idle | 1024 | [975, 32, 16, 1] | 1.660 | 3.223 | 4.688 | -3.027 |
| 250 | 11 | active | 1024 | [968, 22, 33, 1] | 3.320 | 2.246 | 5.371 | -3.125 |
| 250 | 11 | idle | 1024 | [957, 23, 41, 3] | 4.297 | 2.539 | 6.250 | -3.711 |

All 24 observed G values are negative. The smallest observed gap is -1.660 pp and the largest negative gap is -3.833 pp. A negative estimate does not prove a population bound or equivalence. Across all conditions, the observed cells contain 49 shared errors, 1,732 errors only on reporter 1, and 1,765 errors only on reporter 0. Those totals describe the retained sample; the acceptance rule never pools the input patterns.

The algebraic decomposition G = p11 - (p01+p10)/2 - |p01-p10|/2 separates shared failures, isolated failures and asymmetry. The two paired-score sample variances span 0.01234 to 0.04163, and their paired sample covariance spans -0.000610 to 0.002735. Those are descriptive within-PUB estimates, not an established variance envelope or confidence radius.

## Actor-associated contrasts

The following table subtracts idle from active for the same delay and preparation. A positive change in G alone can coexist with a higher parity-error rate, so both quantities remain visible.

| Delay (µs) | Input | Δp0 (pp) | Δp1 (pp) | Δ parity error (pp) | ΔG (pp) |
|---:|---:|---:|---:|---:|---:|
| 30 | 00 | +0.562 | +0.098 | +0.513 | +0.049 |
| 30 | 01 | -0.537 | -0.439 | -0.830 | +0.391 |
| 30 | 10 | +0.024 | +0.562 | +0.684 | -0.659 |
| 30 | 11 | -0.684 | +0.122 | -0.562 | +0.684 |
| 50 | 00 | -0.146 | -0.342 | -0.439 | +0.293 |
| 50 | 01 | +0.220 | +0.073 | +0.391 | -0.317 |
| 50 | 10 | +0.488 | +0.146 | +0.732 | -0.244 |
| 50 | 11 | -0.269 | +0.464 | +0.244 | +0.220 |
| 250 | 00 | -0.098 | +0.000 | -0.098 | +0.000 |
| 250 | 01 | -0.293 | +0.391 | +0.488 | -0.098 |
| 250 | 10 | -0.195 | -0.195 | -0.195 | +0.000 |
| 250 | 11 | -0.977 | -0.293 | -0.879 | +0.586 |

## Full-register exploration

For each condition, the scan computes four-cell gains for all 11,628 pairs among 153 measured qubits other than reporters 0 and 1 and actor 2. Of 279,072 condition-pair tables, exactly one has positive empirical G: qubits 70 and 134 in the 250 µs idle, input-00 PUB, with cells [1023,0,0,1] and G=1/1024. An independent exact pair calculation reproduces the top three scanned pairs for each condition, including those cells. The candidate is selected after seeing all tables and rests on one event; it supplies no confirmation of parity protection.

Among those 153 spectators, the observed mean number of error bits per shot ranges from 1.927 to 2.140 across conditions. For the threshold of at least five spectator errors, the analysis also calculates a plug-in independent-Bernoulli reference from the observed per-qubit marginals. The largest observed-minus-reference difference is +1.284 percentage points and the smallest is -1.026 points. The reference ignores spatial dependence and its parameters are estimated from the same shots; neither value is a burst test.

## Uniform-input information (exploratory)

Each of the four prepared input rows receives weight one quarter after normalization. The SciPy entropy calculation is a plug-in channel summary, distinct from the per-pattern parity-error margin.

| Delay (µs) | Arm | I(input bit 0; output) | I(input bit 1; output) | I(input parity; output) |
|---:|---|---:|---:|---:|
| 30 | idle | 0.8305 | 0.8244 | 0.7119 |
| 30 | active | 0.8365 | 0.8204 | 0.7139 |
| 50 | idle | 0.8399 | 0.8500 | 0.7407 |
| 50 | active | 0.8353 | 0.8459 | 0.7296 |
| 250 | idle | 0.8328 | 0.8482 | 0.7413 |
| 250 | active | 0.8525 | 0.8485 | 0.7478 |

The plug-in parity information is below the better coordinate information in all six mixtures. These estimates do not establish an uncertainty bound or a confirmatory information-order result.

## Returned timing and provenance

The returned scheduler metadata reports the same measurement start for each of the 156 qubits in every PUB: tick 881. It reports circuit duration 2,138 ticks and the actor X instruction in the active arms. At the reported 4 ns tick, those are 3.524 µs and 8.552 µs respectively. Scheduler metadata is evidence of the reported schedule, not a physical measurement of pulse delivery or initialization quality.

The three job records report overlapping running intervals. The returned shot list provides within-PUB positions; it does not establish cross-PUB order or immediate physical predecessor relations. The first-half/second-half and lag summaries in the machine-readable output describe list positions only.

Collection SHA-256: `979b07a5ab676cca4918dc9c2b690ab4c145e93b017a4d5cc45537ed6138b186`. Submission record SHA-256: `57ba884d85602af45de06e6604b289482cecca4cec184ea58f73109eaf28d00c`. The analysis uses NumPy 2.5.4, SciPy 1.18.1 and the repository paired-moment and channel-summary functions. [Machine-readable output](analysis.json), [analysis source](analyze.py), [figure](reporter-pair-and-activity.png).
