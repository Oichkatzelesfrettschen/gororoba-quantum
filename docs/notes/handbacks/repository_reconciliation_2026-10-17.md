# Repository reconciliation — 17 October 2026

The newer results change the next experiment. Tuna-17 already has a measured
24-edge effective-ZZ map. Its largest conditional shifts agree
from both ends, but the map does not explain all driven-neighbor effects.
A second placement of the deep zero-divisor witness retained less pooled
contrast, and the readout-delay experiments did not establish a residual-photon
mechanism. On IBM, the added reanalyses refute a proposed amplitude
explanation and keep the phase mechanism unresolved. The mathematical and
software advances are substantial; their conclusions remain distinct from
claims about what causes hardware error. The sections below give the
measurements, assumptions, numerical comparisons and source links.

This review fixes merged main at
[`2860b437601bff87b3e6d3957148bb7d79b7ea19`](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/2860b437601bff87b3e6d3957148bb7d79b7ea19),
the publication-time snapshot containing PR #204. PR #144's results,
PR #174's observable proofs and PR #184's backend identity changes are all
merged in this snapshot. Four open changes have also been inspected at
the following immutable heads. Their additional results are included in
the analysis without importing their source branches into main.

| Open change | Reviewed head | Additional evidence or work |
|---|---|---|
| [#193](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/193) | `fc3e717aaaa6ff48a4962539d30b2c381414a688` | Shard provenance, dataset history and measured gate-tier correction |
| [#197](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/197) | `1b89239b700c18a9f332828f7de7560f104610bd` | Completed 997-circuit ideal CPU sweep and generated shallow hardware proposal |
| [#198](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/198) | `58ba02961ac57936182c7a5037ef311a4406e8b4` | Completed nine-batch Q-series acquisition and analysis |
| [#205](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/205) | `fb98c51a66e16ce687aad4f1e9f717e0b5430770` | Public-handle and private-account-identifier documentation |

Main has 116 claims and 75 registered acquisitions: 15 IBM and 60 Quantum
Inspire. This integration adds one proposed static-neighbor cross-check,
for **117 claims and the same 75 acquisitions**. Open-branch additions are
outside that merged census. The complete acquisition table, including
failed jobs, remains in the [research state](../../state/RESEARCH_STATE.md).

Work for this review consists of source inspection, secondary analysis,
integration, local compiler checks and repository validation. All hardware
and Kaggle results discussed below were already retained by the inspected
sources. Timestamps are UTC unless a quoted source explicitly uses a local
calibration timestamp. Historical account and catalogue snapshots do not
assert current availability or remaining balance. The integrated source
is published for review in [draft PR #206](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/206).

## Evidence across the machines

The platform name alone does not say what was measured. A calibration
replay on a classical computer, an ideal QX control and a physical-qubit
acquisition answer different questions. The reviewed record contains the
following evidence, with the primary sources developed below.

| System | Retained evidence relevant to this review | Consequence for interpretation |
|---|---|---|
| IBM Kingston, Heron r2 | Hardware coherence windows, atlas and rank-sector runs, corner controls, and Design B/D witness measurements; later reanalyses and simulated controls | The 40.9 kHz work-qubit frequency difference and 0.646 witness endpoint contrast are separate observables. The new star is still a plan. |
| IBM Fez, Heron r2 | Hardware atlas, rank-sector, N=21 orbit/window and patch-window results; later model comparisons | The fitted N=21 phase does not identify the cause of the Kingston rotation. The amplitude predictor fails its confirming-lane criterion. |
| IBM Marrakesh, Heron r2 | Retained calibration, timing, compilation and noise-model comparisons | No Marrakesh acquisition appears among the 15 registered IBM runs. Simulated Marrakesh behavior is not a third hardware replication. |
| Tuna-17 | Crosstalk/teleport acquisitions, two hardware zero-divisor placements, all-edge ZZ estimates, readout-fault analysis and P/Q readout series (Q complete in open #198) | Effective static interactions, drive-associated shifts and witness loss require separate controls. |
| QX | Ideal controls for existing circuits, including witness and a 10-qubit/12-edge ZZ subgraph | The controls establish properties of the executed payloads. They do not validate the new 416-circuit compact preflight or hardware readout history. |
| Ry emulator | A failed teleport payload, bit-order diagnostic and later cQASM reader probes | Reader compatibility is now better characterized. This is emulation, even though the catalogue marks the backend type as hardware. |
| Kaggle CPU and T4 | Retained exact/noisy simulations, timings and parity checks; open #197 adds the completed qxelarator sweep | CPU emulation and calibrated simulation test implementations and models. They add no quantum-device measurement. |
| RTX 4070 Ti build host | Actual cuStateVec library-call verification and repeated 20/26-qubit trajectory timings | The new speed result belongs to this host/configuration; it is not a retained T4 cuStateVec result. |
| IQM Garnet coupling map | Held-out routed compiler comparison for split N=21 encodings | No Garnet acquisition, native noise model or device-level fidelity comparison is present. |
| Requested Kaggle TPU | CPU executions from earlier requests and a later historically queued probe | There is no retained verified TPU performance result. |
| Spin-2+ | Captured unavailable backend instance, without an account-visible submission type | There is no spin-qubit replication in the record. |
| Open Quantum offerings | Six-backend catalogue, account credits and circuit-free estimates | There is no Open Quantum acquisition, device-bound noise model or completed witness comparison. |

The machine and acquisition distinctions above are bound by the
[baseline registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/state/RESEARCH_STATE.md),
[QI experiment record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/quantum_inspire/experiments.md),
[compute measurements](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/substrates.md)
and [Open Quantum record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/open_quantum/README.md).

## Update coverage

The review follows the final merged files and retained run directories.
Several PR titles or opening descriptions predate results added later in
the same change. In particular, #177's final merged tree includes a Tuna
hardware series despite its title emphasizing QX, and #164 includes a
completed P-series analysis and later partial Q-series retention. Open #197's retained sweep is complete despite an older handoff saying it was not run; open #198 supplies the finished Q-series. The final files control these status statements.

| Workstream | Reviewed PRs | What changed |
|---|---|---|
| QI platform and first hardware results | [#144](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/144), [#156](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/156), [#157](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/157) | Client, acquisitions, source capture and preservation of deprecated case manifests |
| Tuna interactions and readout | [#146](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/146), [#164](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/164) | Acquired 24-edge map, spectator comparison, readout-delay series and device-context evidence |
| Later witness placement and calibration | [#173](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/173), [#177](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/177) | Per-batch assignment references, several QX placements and the second hardware witness |
| QI provenance and account policy | [#170](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/170), [#178](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/178) | Fixed source inventories, complete ledger-row comparison, declared unretained jobs and account-wide pauses |
| IBM fringe and error explanations | [#145](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/145), [#147](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/147), [#158](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/158), [#165](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/165), [#167](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/167) | Coherent-family comparisons, drift, error budgets, amplitude refutation and repaired derived-data provenance |
| IBM experiment design and timing | [#160](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/160), [#162](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/162), [#169](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/169) | Device-bound readout review, unsubmitted star Ramsey, scenario-specific latency and routed window sizing |
| N=21 encoding | [#142](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/142), [#151](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/151), [#175](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/175) | Exact encoding search, routed/noisy comparisons, failed acquisition admission and all-seed verification |
| Compute | [#148](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/148), [#149](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/149), [#163](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/163), [#166](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/166) | Measured CPU/T4 routing, JAX structure reuse, bounded upload bundles and honest TPU-request provenance |
| Exact mathematics | [#137](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/137), [#138](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/138), [#141](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/141), [#172](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/172), [#176](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/176), [#179](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/179) | Degree proofs, local and D-locus certificates, source inventories, exact box-kite census and shallow experiment program |
| Engineering verification | [#155](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/155), [#159](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/159), [#171](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/171), [#181](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/181) | Credential-file exclusion, full-tier gate repairs, all-star/path model replay and whole-directory lint/types |
| Additional service | [#180](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/180) | Open Quantum source capture, account catalogue and circuit-free estimates |
| Merged observable proof and identity | [#174](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/174), [#184](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/184) | Full terminal-observation bindings, typed applications, backend version and processor revision |
| New QI context and faults | [#185](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/185), [#187](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/187), [#192](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/192) | Fresh circuit records, explicit readout-run selection and conservative fault discrimination |
| New computation and encoding | [#188](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/188), [#189](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/189), [#194](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/194), [#195](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/195) | Shard bindings, actual host cuStateVec timings, split encodings and exact-model N=21 planning |
| Revised priorities and geometry | [#191](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/191) | Two Kingston pair cases retired; Bell-rate proposal preserved; exact A₅ gap research plan |
| Calibration and circuit admission | [#196](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/196), [#202](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/202), [#204](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/204) | Cross-job calibration gate, complete dynamic-law census and shared plan/submit admission |
| Hosted and integration checks | [#190](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/190), [#199](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/199), [#200](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/200), [#201](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/201), [#203](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/203) | Combined-tree differential checks, completion of main jobs, independent upstream tables, path-filtered Rocq replay and isolated worktrees |
| Open additions, separately reviewed | #193, #197, #198, #205 at the heads above | Provenance repairs, ideal sweep, full Q-series and identifier guidance |

## Quantum Inspire: what the newer acquisitions establish

The repository now contains the 24-edge Tuna-17 conditional-Ramsey map that
the earlier discussion proposed. It also contains a second zero-divisor
hardware series and a completed P-series readout experiment; open #198
also supplies the completed Q-series. Those results
change the purpose of the prepared 416-circuit case: it is an independent
comparison with an existing map, and its long acquisition needs redesign
before execution. This assessment uses immutable main commit
[`2860b437`](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/2860b437601bff87b3e6d3957148bb7d79b7ea19).
Times below are UTC; all numerical results are retained acquisitions or
analyses, not new runs performed for this review.

### All 24 edges have an exploratory estimate

The acquired design exploits the bipartite coupling graph. One partition
runs Ramsey while the other is prepared on the equator and measured in Z.
Conditioning each target on its neighbors' outcomes estimates their
pairwise contributions together; swapping partitions measures the other
end. Ten circuits at 16,384 shots, with 0.5 and 2 microsecond delays, ran
over four batches. The current generator subsequently groups X/Y pairs
together into five batches. These are different acquisition layouts, and
the retained results belong to the former.
([Design and retained map](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/coupler_zz_tuna_17_analysis.json))

The Hamiltonian convention is
`H/hbar = sum(omega Z)/2 + sum(J ZZ)/2`. The table reports J/(2 pi)
in kilohertz, with standard errors; the full conditional frequency
difference has twice the tabulated magnitude.

| Edge | J/(2 pi) ± standard error, kHz | Usable ends |
|---|---:|---:|
| 0–1 | −2.207 ± 0.896 | 2 |
| 0–2 | −7.903 ± 0.963 | 2 |
| 1–4 | −19.282 ± 0.868 | 2 |
| 2–4 | +4.133 ± 0.938 | 2 |
| 2–5 | +5.310 ± 1.295 | 1 |
| 3–5 | +11.731 ± 1.307 | 1 |
| 3–6 | −7.824 ± 1.336 | 1 |
| 4–7 | −2.984 ± 1.339 | 1 |
| 4–8 | −4.985 ± 0.959 | 2 |
| 5–8 | −0.433 ± 1.345 | 1 |
| 5–9 | +0.029 ± 1.443 | 1 |
| 6–9 | +0.549 ± 1.463 | 1 |
| 7–10 | +3.143 ± 1.154 | 1 |
| 7–11 | −0.227 ± 1.270 | 1 |
| 8–11 | +6.613 ± 0.935 | 2 |
| 8–12 | −0.707 ± 0.913 | 2 |
| 9–12 | +3.730 ± 0.932 | 2 |
| 10–13 | −0.383 ± 0.870 | 2 |
| 11–13 | +7.502 ± 0.937 | 2 |
| 11–14 | −31.434 ± 0.944 | 2 |
| 12–14 | +10.353 ± 0.921 | 2 |
| 12–15 | +2.952 ± 0.913 | 2 |
| 14–16 | −3.127 ± 0.986 | 2 |
| 15–16 | +5.322 ± 0.975 | 2 |

The strongest edge, 11–14, reads −31.402 and −31.473 kHz from its two ends.
The 15 reciprocal comparisons agree within 1.7 standard errors except
8–11, which differs by 3.19. Q5, Q6 and Q7 lose visibility to 0.043, 0.270
and 0.084 by 2 microseconds; excluding those probe ends leaves nine edges
with one usable end. The exclusion rule was fixed after the data. Neighbor
relaxation, sector mixing from readout, calibration changes and the
666.7 kHz alias period limit the interpretation. These coefficients measure
effective interactions in the acquisition context, not flux settings.

The [spectator comparison](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/spectator_zz_split.json)
predicts +0.158 rad for Q14 driving Q11, against +0.153 measured. For Q7
driving Q4 it predicts only +0.015 against +0.633, leaving +0.618 rad.
Static ZZ explains the first pair under the model and leaves a substantial
additional effect in the second. The comparison assumes a half-excited
driver and joins runs about 90 minutes apart. Q1/Q2 have no direct edge;
their simultaneous-drive failure and the weak witness corner remain a
spatial association without a demonstrated common cause.

### Moving the witness did not restore its contrast

The final replacement placement avoids Q0, Q5, Q6, Q7 and Q9. Its hardware
run used three batches, each containing one Latin witness and both
readout-reference circuits, at 16,384 shots per circuit. Its preceding QX
twin returned dark 0, bright 1 and fixture 0.506, consistent with one half.
Earlier QX controls for the three-region and intermediate two-region
placements remain separate retained results.
([New hardware analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json))

| Hardware series | Dark | Bright | Fixture | Raw contrast |
|---|---:|---:|---:|---:|
| Original three regions | 0.470785 | 0.512288 | 0.499044 | 0.041504 |
| New two regions | 0.485413 | 0.505615 | 0.491760 | 0.020203 |

The new contrast remains resolved at z = 5.17. Its corrected bootstrap mean
is 0.02211, with 95% interval [0.01362, 0.03080]. Region {1,2,4,8,12}
retains contrast 0.0504; {10,11,13,14,16} reads −0.0100 with an interval
including zero. The exclusion increased dark/bright routes from 66 CZ to
75 and 87 CZ; fixtures require 79 and 91 CZ. Qubits, routes, depth and
calibration changed together. The outcome establishes that this relocation
did not improve pooled contrast; it does not establish depth as the cause.

The per-batch calibration update matters because a calibration boundary
can change the assignment model. Current correction and bootstrap use
each witness's own batch references. The original five-circuit acquisition
retains its original single calibration group. Its raw fixture agreement
with one half does not survive the correction model. The old corrected H
was compatible with zero, which supported compatibility with a common
affine response without establishing it. The new corrected
`H = fixture − (dark + bright)/2` interval is [0.00176, 0.01633], excluding
zero. That secondary, unadjusted comparison challenges transferring the
same response model across placements. State-dependent readout,
preparation, selector changes and gate depth remain confounders.
([Experiment record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/quantum_inspire/experiments.md))

### The readout experiment returns an inconclusive mechanism test

The [P-series analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/readout_ringdown_tuna_17_P_analysis.json)
reports the preregistered verdict “not detected”: three of seven usable
targets classify as tails, below the required half. Q6, Q10 and Q16 receive
tail labels; Q11 and Q12 receive offset labels; Q5 fails visibility. Every
classified target fails the fitted exponential model, with chi-square
30.7–193.7 on three degrees of freedom. The rule checks improvement over
the static model but not absolute fit. Its labels therefore identify
unmodeled arm differences, not established photon decay.

Q6's corrected visibility reaches 1.079 because the original assignment
calibration became stale. Q6/Q16 hit the lower decay-time bound; Q10's
offset grows with pre-delay. Q11 consistently lies 19–33 kHz below its
reference through 2 microseconds, but the design cannot distinguish a
persistent readout effect from a reference-arm shift. The original
P-05/P-06 and their replacements are all retained; only the replacements
enter the reported analysis. Merged main retains Q through batch 04. The complete open-branch analysis
is included below, with its separate provenance.

The [device context](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/readout_ringdown_tuna_17_device_context.json)
records Q9 idle P1 increasing to 0.27–0.29, and Q0/Q6 prepared-state P1
falling to approximately 0.39/0.14 after calibration. Tuna returns the full
34-bit register, whereas QX returned only final outcomes. Thus completed
QX tests did not exercise the mid-circuit postselection path. The
postselection-difference error also collapses for many high-retention
subsets; its undefined z values provide no additional falsification.

### The new readout analysis narrows the device fault

Merged PR #192 adds a reanalysis of named, already retained Tuna-17 runs. It adds no circuit or acquisition. The current record uses conservative one-sided three-standard-error bounds and a zero-delay herald test; its numbers supersede the earlier, tighter point estimates still quoted in the PR opening text. [Retained readout-fault analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/tuna_17_readout_faults.json)

For Q9, write the assignment errors as `e0 = P(report 1 | state 0)` and `e1 = P(report 0 | state 1)`, the pre-readout excited population as `p`, and the assignment scale as `s = 1-e0-e1 > 0`. Under the stated assumptions `p <= 1/2` and an X operation that inverts no more than fully,

\[
P(1\mid\mathrm{idle})=e_0+sp,
\qquad
P(1\mid X)\leq e_0+s(1-p),
\]

so `e0 >= P(1|idle)+P(1|X)-1`. The three zero-wait readout pairs at 05:26–05:33 UTC give conservative lower bounds on `e0` of **0.205554, 0.192212 and 0.196990**, against a pre-change upper bound of **0.030253**. Their corresponding population upper bounds are **0.1140–0.1146**. The separate Q-series calibration with a 2 μs wait gives the weaker limits `e0 >= 0.145214` and `p <= 0.203217`. These are conditional bounds on the fault model, with sampling uncertainty already weakened in the conservative direction; they are not a posterior probability that Q9 was perfectly in its ground state. [Model and calculation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/qi_tuna17_readout_faults.py)

The zero-delay herald test provides a more direct discrimination. Among **2,122** shots whose opening readout reported Q9 as 1, the estimated excited fraction reaching the short X90-pair probe is **`w = 0.0208202 ± 0.0131100`**. The falsifier was `w >= 0.5`. This favors an assignment fault that usually leaves the qubit in its ground state over a majority population of persistent excitations at the probe. The older PR-body value `0.021 ± 0.006` pooled longer delays, where relaxation can erase an excitation, and is not the current test. Transient excitation that decays before the probe remains outside what this measurement excludes. [Zero-delay counts and assumptions](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/tuna_17_readout_faults.json)

Q0 and Q6 have a different ambiguity. Their zero-wait prepared-one readout scales retain approximately **0.555 and 0.164** of the previous evening’s scales. Assigning all of that loss to relaxation during the 800 ns readout would require `T1 <= 1.357 μs` and `0.442 μs`. That model would limit prepared-one readout after another 2 μs wait to **0.1561 and 0.01524**; the retained wait runs instead read approximately **0.39 and 0.14**. The record’s discrepancies exceed 32 shot-noise standard errors. The comparison assumes stable device behavior between the 04:15–04:24 UTC wait runs and the 05:26–05:33 UTC zero-wait runs, and those reported z scores do not include every cross-run uncertainty. The result rejects this specific stable, readout-window-relaxation explanation. [Short-T1 hypothesis test](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/quantum_inspire/tuna_17_readout_faults.json)

A common under-rotation of X and X90 remains confounded with excited-state misassignment in the matched Ramsey quadratures. The new **double-X discriminator** has substantially separated predictions: Q0 `P1 = 0.98098` versus `0.03800`, and Q6 `0.51567` versus `0.01329`, for under-rotation versus misassignment. This is a proposed experiment, with an initial check that the fault still exists, rather than an acquired result. It is more directly tied to the observed measurement failure than interpreting the entire bad corner as one coupler fault. [Proposed discriminator](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/quantum_inspire/experiments.md)

### The Q-series is complete on open PR #198

Main still retains only the partial Q-series. Open PR #198 adds batches 05–08, a repeated readout calibration at 05:39 UTC, and the complete nine-batch Q-series analysis. Its preregistered verdict is **“not detected”**: Q9, Q14 and Q15 receive tail classifications, three of seven usable targets, below the required half. Q7 and Q8 fail the 0.3 visibility floor, with minimum corrected visibility **0.090625 and 0.212426**. No target receives the static-offset classification. Together with the P-series result, both halves of the 17-qubit device now have retained series verdicts, provided the open-branch status is stated. [Complete Q analysis, open head](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/58ba02961ac57936182c7a5037ef311a4406e8b4/results/quantum_inspire/readout_ringdown_tuna_17_Q_analysis.json)

| Q-series tail class | Minimum corrected visibility | H2 χ² / stated degrees of freedom | Fitted decay time | Interpretation |
|---|---:|---:|---:|---|
| Q9 | 0.7438 | 6.952 / 3 | 5 cycles = 100 ns | Only classified Q target with a tolerable absolute H2 fit; time sits on the lower search boundary, with no fitted time uncertainty |
| Q14 | 0.3155 | 146.753 / 3 | 5 cycles = 100 ns | Very poor absolute fit despite improvement over H1 |
| Q15 | 1.2841 | 39.336 / 3 | 5 cycles = 100 ns | Poor fit and a physically inconsistent corrected visibility under a single Bloch-vector interpretation |

The Q15 visibility reaches **1.47072**, slightly above the rounded range in the PR body. Q13 also has corrected values **1.0117–1.0420**. The repeated Q15 calibration reads prepared-one probability about **0.914** after 2 μs, compared with about **0.730** in Q-batch-00. The preregistered analysis continues to use Q-batch-00 for every arm; the later calibration is retained separately and does not silently replace it. Q15 also loses its tail classification under opening-zero postselection. These observations make the tail labels evidence of arm-dependent structure under the registered estimator; they do not establish residual photons or a measured resonator lifetime. [Calibration handling and device lessons](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/58ba02961ac57936182c7a5037ef311a4406e8b4/docs/notes/quantum_inspire/tuna-17.md)

The two outstanding statistical issues remain relevant. Issue #182 calls for joint propagation of calibration-count uncertainty and the covariance induced by sharing that calibration. Issue #183 calls for null calibration of the scan over decay time: at zero amplitude the decay time is unidentified, so the nominal two-degree-of-freedom χ² threshold is not a demonstrated false-positive guarantee. Neither issue licenses rewriting the existing preregistered verdict. A separate sensitivity analysis can assess robustness; future acquisitions can preregister the improved procedure. “Not detected” means this series failed its decision rule, rather than establishing that all readout-induced transients are absent. [Calibration issue](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/182), [scanned-time issue](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/183)

### Provenance and the next acquisition decision

The [registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/state/research_state.json)
contains 116 claims and 75 acquisitions: 15 IBM and 60 Quantum Inspire.
The proposed case in this integration raises only the claim count, to 117.
Those counts do not include the additional open-branch Q-series records.
The [05:53:53Z ledger](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/quantum_inspire/usage.json)
lists 184 jobs, 173 retained and 11 explicitly declared unretained. Those
11 completed Tuna jobs represent 90,112 shots, not an available scientific
analysis. The whole ledger reports 1,152,000 completed shots, 994.706513
execution seconds and zero transactions. Ledger v2 permits declared jobs
from other branches while checking retained evidence; passing checks do
not mean every account job's raw data are present.

Capture verification now fixes required inventories and source URLs;
transaction checks compare complete rows. The [runner](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/qi_platform.py)
also enforces a 120-second account-wide hardware pause and coordinates
token rotation across processes. The captured catalogue still has Spin-2+
offline and its backend type unavailable.

Merged PRs #185 and #187 repair retention coupling: #185 updates the toolchain record over the regenerated witness circuits and adds the three later witness readout pairs to device context; #187 makes that context depend on an explicit ordered `READOUT_RUNS` list. Newly retained runs outside the list are reported without silently changing an existing claim’s hashed record. These changes add no new hardware observation beyond the named runs and do not change the old implied-T1 inputs. [Explicit run selection](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/qi_tuna17_device_context.py)

Our prepared 416-circuit map adds explicit neighbor states, zero-idle
controls, six-delay linearity checks and joint assignment covariance.
However, its 139 batches require at least **4.6 hours of pauses alone**,
and its mandatory 20/40 microsecond points lack demonstrated all-qubit
viability. Calibration changes within minutes make an unchanged full
acquisition poorly justified. A shorter fixed pilot or targeted reciprocal
check on 11–14, 1–4 and 8–11, with a separately defined Q1/Q2 control,
addresses the concrete remaining questions. The frozen grid remains a
reviewable reference. Its separate 425,984-shot QX proposal remains
unsubmitted; previous QX twins do not validate these new payloads.

## IBM evidence and classical computation: what the newer work changes

The newer IBM work consists of reanalysis of retained hardware data,
simulation, provenance improvements and held experiment designs. The final
delta to main 2860b437 adds nine IBM records: two `design_infeasible` and
seven `planned`, all without submission. It supplies no new IBM hardware
measurement of residual ZZ. The existing phase and visibility discrepancies
remain a set of model failures with several possible physical causes.

For the Tuna follow-on, these findings favor an analysis that estimates conditional phase slopes and checks their consistency before interpreting the witness's lost contrast. Neighbor-state controls, matched exposure and readout correction make a static-coupling result interpretable. Driven-neighbor effects and post-readout tails require their own comparisons. A resolved ZZ value would support one component of the hardware model; it would not identify every error in the longer witness circuit.

### Fringe phase and amplitude now have different evidential outcomes

The coherent-family analysis compares detuning, conditional CZ phase, static ZZ in two reference frames, SX amplitude and rotation-axis tilt. Across fourteen atlas lanes, the best single family is partner-in-|0> ZZ on seven, detuning on four and axis tilt on three. Only two lanes satisfy the declared criterion of a leave-one-out residual within 1.5 times that model's noise floor. The remaining twelve stay 1.7–4.3 times above their floors. Choosing the lowest score after comparing families remains exploratory; it does not identify the physical cause. [Coherent-family evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/atlas_coherent_families/README.md)

The reference frame matters. Partner-in-|0> ZZ outperforms symmetric-frame ZZ on thirteen of fourteen linear fits and all fourteen resimulations, by a median score ratio of about 2.4. However, the repository has no source specifying the spectator state used in IBM's frequency calibration. The comparison motivates conditional Ramsey with a declared spectator state; it does not substitute for that measurement. [Frame comparison and its limits](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/coherent-error-families-report.md)

The amplitude analysis gives a firmer negative result. It studies the logarithm of hardware fringe amplitude divided by calibration-replay amplitude. Ten lanes exhibit structure beyond the declared per-lane shot-noise criterion. The proposed idle-relaxation-plus-constant predictor improves leave-one-edge-out RMS on four of eight confirming lanes, against six required. The preregistered prediction is therefore refuted. The parameter-free idle prediction is refuted on thirteen of fourteen lanes; its sole exception is also consistent with a constant. The retained full run is now `2026-10-17T030918Z-gororoba-atlas-fringe-amplitudes`, superseding the earlier run cited in the PR description. [Amplitude result and confirmation table](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/atlas_fringe_amplitudes/README.md)

This does not make idle relaxation irrelevant. The analysis demonstrates that the original unscheduled ISA replay omitted relaxation during waits between pulses. What fails is the claim that its idle-relaxation predictor explains the observed pattern across edges. The phase-fitted coherent families also fail to explain that amplitude pattern. Phase prediction and visibility prediction must remain separate tests.

### The recurring frequency scale remains a collection of distinct observations

The withdrawn common-ghost claim stays withdrawn. Kingston's matched-idle rotation corresponds to a 40.9 kHz frequency difference between work qubits 68 and 66, with winding alternatives. The Fez N=21 fitted phase involves different qubits, circuit, device and day. Similar numerical scale does not establish one shared source. Moreover, Kingston's matched idle has no preceding mid-circuit measurement, which disfavors a residual-photon explanation for that window while leaving post-readout mechanisms in other windows open. [Audited idle-phase interpretation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/ghost-frequency/README.md)

Calibration summaries do not resolve this ambiguity. The revised drift study binds 157 records and seventeen snapshots, comparing common qubit populations instead of treating every record as an independent calibration. Typical absolute T1 changes are approximately 15–25%, despite signed median changes no larger than 7.8%; the opposing movements cancel in the median. These retained medians contain no qubit frequency, so they neither establish nor exclude frame detuning. [Calibration drift evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/calibration_median_drift/README.md)

### Error multipliers expose missing model content without locating it

The error-scale sweep fits one CZ multiplier and one readout multiplier against each retained hardware distribution. Any omitted error can enter those fitted parameters. Four ordinary static runs require CZ factors of 1.5–2, compared with heuristic idle budgets of 1.3–1.6. Strongly dynamic runs require factors of 5–6 against idle budgets of 1.8–2.3. Yet the unexplained absolute budget per PUB overlaps: 0.23–0.42 for those dynamic runs versus 0.06–0.43 for the ordinary static runs. A wide static run without dynamic events also requires a factor of four. The larger dynamic multiplier therefore does not by itself identify feed-forward as the cause. [Error-scale results](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/ghost_error_scale/README.md)

The idle budget is a heuristic comparison of aggregated relaxation and reported CZ errors, not an exact channel decomposition. State averaging and the different dimensions of the compared average infidelities limit a literal causal interpretation. PUB bootstraps also omit model sampling uncertainty, and some fitted readout factors lie at the grid boundary. The later diagnostics correction halves duplicated coupler counts and separates cap fields while preserving simulation bytes; the dataset update repairs their provenance. [Budget definition](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/ghost_idle_budget.py) and [retained review](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/reviews/pr-147-ghost-error-scale.md).

The event-scale discriminator remains unfinished. Current code compares executed-schedule padding, CZ scaling, readout scaling and excess mid-circuit assignment error. The event error is now an X flip before measurement and after reset, replacing the earlier depolarizing-channel description. Conclusions use a near-best set and can be true, false or unresolved. No production event-sweep output is tracked at the reviewed commit, so it supplies no completed mechanism verdict. [Current event-sweep definition](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/ghost_event_scale.py)

### The two Kingston pair cases are retired; the Bell-rate question remains open

PR #191 retires the conditional-Ramsey cases on pairs (68,67) and (67,66), without execution. Together they represented 31.6 nominal seconds. The previously listed diagnostic reserve now contains the crossed tile/template, scaffold A/B and qubit-79 delayed-readout cases, totaling 14.3 nominal seconds and 35 seconds of ceilings. The Tuna acquisition already implements the conditional-arm fit on another device, which motivated the owner's allocation decision. It does not measure the detunings of those Kingston qubits. [Final census](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/state/QPU_RUN_CENSUS.md)

The final registry preserves `proposed-conditional-ramsey-hamiltonian` as **proposed**: no acquisition collects both Bell odd/even rates and the consistency relation `nu_odd + nu_even = nu_A|0 + nu_A|1`. The existing fourteen-star Kingston dry run also remains unsubmitted. Thus “Kingston star retired” would overstate the change. The retired pair cases, the broader rate-consistency design, and the retained star construction have different statuses. [Registry boundary](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/state/research_state.json) · [Star dry run](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/live/2026-10-17T023204.041725Z/record.json)

### The retained Kingston star covers the original work-qubit pair

The unsubmitted star-Ramsey design combines conditional, Bell and GHZ coherences. Twelve rates determine four effective qubit frequencies and three ZZ coefficients, leaving five consistency relations that can falsify the static diagonal model. The retained dry run places fourteen Kingston stars; its first has center 67 and leaves 57, 66 and 68. It therefore includes both work qubits of the original coherence-window comparison. Bell arms compile to two CZ and GHZ arms to six, with checks that preserve the physical star throughout idle and readout. Its near-zero simulated rates are properties of the supplied noise model, not measured hardware rates. [Star design](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/gororoba_quantum/star_ramsey.py) and [planned run record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/live/2026-10-17T023204.041725Z/record.json).

The readout research also narrows what can be assumed. The recorded `measure` durations are 1660 ns on Fez, 2180 ns on Kingston and 2684 ns on Marrakesh. Those pulse-to-digitization durations do not reveal resonator ring-down. The bounded source search found no device-bound resonator linewidth, dispersive shift or photon-decay measurement for these Heron r2 systems. Merged PR #184 now adds backend version and processor type to new records while preserving acceptance of historical records without those fields. [Device-bound readout evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/ibm_quantum/heron-r2-readout-resonator.md) and [PR #184](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/184).

### N=21 encoding gains and the superseded sampled plan

The exhaustive linear-encoding search covers 83,328 cosets under its declared surrogate. Routed admission on FakeFez reduces median CZ from 5422 to 3933 for ten rounds and from 1107 to 739 for the two-round diagnostic. Separate calibrated simulations raise Kingston's two-round contrast from 0.0067 to 0.0417. These are substantial compilation and modeled-signal gains; ten-round modeled order recovery nevertheless remains 0.129–0.139, at or below the depolarized statistic of 0.1445. [Encoding evidence and scope](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/linear_conjugation/README.md)

The earlier sampled dry run was `design_infeasible`. Its predicted contrast of 0.034317 loses 0.033456 to the simultaneous simulation allowance, leaving only 0.000861 as the effect used for power. That record is historical: the exact-model design below now replaces its simulation-limited admission calculation. [Admission record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/live/2026-10-17T003834.987727Z/record.json)

### N=21 now has a better ten-round encoding

PR #194 allows the five-qubit work-register encoding to change between rounds. Its exact search reaches all 9,999,360 matrices of GL(5,2); a dynamic program optimizes the declared synthesis surrogate over 83,328 permutation cosets. The ten-round winner holds coset 15265 through round nine and switches to 111 through a three-CNOT transition. The routed improvement survives eight held-out transpiler seeds. [Construction, exact checks and held-out results](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/gl52_split_conjugators/README.md)

| Compilation target, ten rounds | Best single encoding, seeds 0–7 | Best split, seeds 0–7 | Held-out single / split, seeds 8–15 |
|---|---:|---:|---:|
| FakeFez and FakeKingston | 3,933 CZ | 3,754 CZ | 3,945.5 / 3,746 CZ |
| IQM Garnet coupling | 3,190 CZ | 3,026.5 CZ | 3,172 / 3,018.5 CZ |

On Heron r2 this removes another 179 CZ, approximately 4.6%, beyond the earlier single-encoding improvement. For the two-round diagnostic, both rounds have the same surrogate minimum, so no split improves that minimum. None of sixteen routed split candidates beats the best single encoding on any target; that finite routed search is narrower than a global routed optimum. A five-CZ apparent gain for single coset 15275 reverses on held-out seeds, leaving 15265 as the two-round candidate. The Garnet comparison uses its captured coupling map with an IBM-style gate basis and no Garnet error or duration model. These are compiler results, with no Garnet acquisition or new fidelity prediction. [Routed results and limits](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/gl52_split_conjugators/README.md)

### Exact-model planning replaces the previous N=21 infeasibility

The earlier sampled plan lost almost its entire modeled contrast to a simultaneous simulation allowance. PR #195 computes the dynamic circuit's branch-resolved density matrices directly, eliminating that sampling allowance under the same Aer noise model. It distinguishes the true measurement outcome from the readout-flipped recorded bit, applies feed-forward using the recorded bit, and preserves reset and conditional-body noise ordering. Its exactness concerns the specified channel model; calibration mismatch and omitted hardware channels remain outside the calculation. Unsupported noise/control-flow cases raise explicitly, including delays under custom noise passes. [Exact engine](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/gororoba_quantum/dynamic_density.py)

The latest retained reference, `2026-10-17T130242.718497Z`, is **planned**, using Kingston's 05:40 Pacific calibration, two replicas and 122,880 shots per PUB. It estimates **83.1 QPU seconds against a 95-second ceiling**. One replica under Hoeffding needs 102.4 seconds. The two-replica saving rests on a declared per-replica variance bound of 0.55 and the planning assumption of independent replicas. Collection uses the larger of the declared variance projection and its empirical upper confidence limit, spends a 0.001 falsifier tail, and falls back to Hoeffding if registers are absent or inconsistent. At two replicas the detection threshold still uses Hoeffding; the replica assumption improves the power budget. [Budget and statistical contract](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/gororoba_quantum/N21_USAGE_BUDGET.md)

The model comparison deserves attention before acquisition. Three Kaggle CPU kernels with distinct seeds supply 589,824 shots per arm. All probability, arm-score and contrast checks pass their declared finite-sample radii. Nevertheless, the pooled contrast is **0.02817 against 0.03083 exact**, a difference of −2.04 exact-law standard deviations. This does not establish model bias, but it leaves an approximately 9% contrast deficit unresolved. Applying that fraction to the reference plan would require roughly 144,353 shots per arm and **97.3 seconds** for the specified power, exceeding its ceiling. The pooled comparison uses an earlier calibration, so this is sensitivity analysis rather than a measured correction to the new plan. [Retained sampled validation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/n21_exact_model/README.md)

Calibration changes also matter materially: the exact one-replica contrast ranges from 0.0308 through 0.0229 to 0.0249 across the retained snapshots, moving the modeled Hoeffding charge from 67.8 to 120.8 and then 102.4 seconds. Those are changes in calibrated model predictions. Reducing repetition delay or changing the statistical contract yields cheaper rows, but their extra assumptions remain explicit and their power is unverified. The latest plan is therefore a concrete held case with a narrow model margin, replacing the old infeasible result without claiming readiness for execution. [Calibration and cost table](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/gororoba_quantum/N21_USAGE_BUDGET.md)

### Cross-job comparisons now require a shared calibration

PR #196 reads every member's execution calibration and withholds comparisons when stamps differ, a calibration changes during shots, or a stamp is missing. The retained October 13 patch-window jobs all carry the same `2026-10-13T13:41:52-07:00` stamp; consequently their existing numerical results remain unchanged. The modification adds provenance and enforces future comparison boundaries. It does not retrospectively attribute the orbit-phase discrepancies to calibration drift. [Updated analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/live/2026-10-13T201757.782152Z/patch-analysis.json)

Merged PR #184 also propagates backend version and processor family/revision through new planning, simulation and collection records. Its retained identity dry run reports Fez 1.3.37, Kingston 1.0.0 and Marrakesh 1.0.21, all Heron revision 2. Historical records remain accepted without those fields; version identity is provenance and does not replace calibration/capability admission. [Identity record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/results/live/2026-10-17T124919.270570Z/record.json)

### Compute improvements expand verification capacity

The retained CPU/T4 crossover is workload-specific: static twelve-qubit density matrices take 105.4 seconds on CPU versus 8.3 on T4, while fourteen-qubit cases take 1955.2 versus 110.8 seconds. Actual seven-qubit N=21 circuits favor CPU trajectories by 1.5–8 times, and the retained batched GPU sampler fails on control flow. The measured Kaggle guidance recommends twelve static or eight dynamic qubits, but other repository routing text still uses the local eleven-qubit threshold. That inconsistency needs reconciliation before describing a uniform policy. [Substrate measurements](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/substrates.md)

The JAX bridge cuts the retained 105-replica CPU sweep from 1389 seconds to 22 by exporting once per structure and rescaling CZ channels. Independent NumPy/Aer parity is 1.9e-9; complex64 JAX differs from its reduced NumPy reference by 2.9e-6. This accelerates a specified model without validating additional physical mechanisms. [Bridge contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/jax-bridge-structure-report.md)

No verified TPU benchmark is retained. Earlier TPU requests ran on CPU workers; the verified-account probe's last timestamped observation was queued after seven hours eight minutes. This is a historical observation, not a current queue status. [TPU evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/tpu-research.md)

Validation coverage also improves: full-tier coherent-fit checks now accommodate bounded numerical conditioning effects; N=21 verification recompiles every retained seed; scenario budgets use their own latency; routed controls determine window sizes; and the IBM reconstruction of Tuna circuits checks every star and teleport path. These repairs increase confidence in the retained implementation evidence. They do not turn an independent-channel model's zero crosstalk prediction into a Kingston hardware result. [Coherent replay](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/atlas_coherent_families/README.md), [N=21 replay](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/n21_conjugation_noise.py), [planning changes](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/commit/ae2d75ba7cb747ba7d7bbbff3c1c5218bc47d895), and [Tuna-circuit comparison](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/quantum_inspire/experiments.md).

### cuStateVec has a measured host result, with workload limits

PR #189 repairs the host Aer build so `cuStateVec_enable=True` actually invokes NVIDIA's library. The retained verification note reports true result metadata and 75,079 vendor-library calls for its twenty-qubit probe, with no calls in the plain-GPU control. On an RTX 4070 Ti, repeated noisy-trajectory measurements give approximately **1.25× improvement at twenty qubits and 1.18× at twenty-six**. Tiny dynamic circuits pay additional overhead. These measurements were taken under other host load, and the seven-qubit N=21 cuStateVec timing lacks a matched plain-GPU measurement. [Host build, probes and timings](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/build_host/custatevec.md)

The Kaggle CUDA 11 library chain is now pinned, but no retained T4 run enables cuStateVec. The earlier CPU/T4 crossover results still apply to their original configurations. Tensor-network execution remains unqualified after intermittent library errors, and cuStateVec plus batched GPU shots is explicitly refused because Aer reports the former disabled. No verified TPU result has been added. [Kaggle scope](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/custatevec.md) · [TPU record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/kaggle/tpu-research.md)

### Replays and admission become harder to bypass accidentally

PR #188 binds error-scale part B to five retained CPU shard kernels while preserving the simulation values. Open PR #193, reviewed here at `fc3e717`, strengthens shard-failure tests, preserves dataset-version history, and corrects the description of the repeated computation: both kernel sets use seed 20261016, so their agreement establishes reproducibility across sessions, not an independent sample. Its latest commit moves the 143.5-second part-C regeneration into the full tier while retaining the other provenance checks on pull requests. These changes are still outside audited main. [Open provenance update](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/fc3e717aaaa6ff48a4962539d30b2c381414a688/docs/evidence/ghost_error_scale/README.md)

PR #202 extends the circuit census to exact dynamic branch laws. Main records 1,452 distinct members, including 64 dynamic members and none unchecked. Twenty-four dynamic members execute CZ despite point-mass or product output laws; each now declares what physical probe that CZ serves. The N=21 correlated laws receive separate exact checks. PR #204 closes the earlier dry-run/submit mismatch by applying one source-group admission predicate in planning and submission, before simulation. A measure-then-gate mutation now fails by member name during planning. These are meaningful implementation and reproducibility gains; they do not supply a new hardware-error mechanism. [Dynamic census](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/walk-control-scaffolding/README.md) · [Shared admission](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/gororoba_quantum/live_run.py)

## Algebra, formal proofs and the additional platform

The mathematical updates strengthen the exact specification and its
connection to recorded observables. Algebraic identities, circuit
implementations and explanations of hardware error retain separate proof
obligations. The observable reconciliation is now merged; the shallow
case generator and its completed ideal sweep are additional open-branch
evidence at the inspected #197 head.

### The box-kite census now supplies exact experimental targets

The census examines all 44,100 ordered products of 210 two-blade representatives. Its 336 zero products agree with `cd_core`'s corpus; the remaining unnormalized squared product norms are 4 for 43,428 products and 8 for 336. The finite geometry has seven box-kites, 42 assessor planes and 84 signed diagonal representatives. Each kite has six assessors, three struts and twelve edges; globally there are 42 same-sign and 42 opposite-sign assessor edges. These correspond to 168 undirected signed-diagonal zero-product pairs, or 336 ordered products. Those counts describe different objects within the continuous zero-divisor geometry. [Exact census](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/box_kite_census/census.json)

For the original operand, the retained annihilator is

\[
\operatorname{Ann}(e_1+e_{10})=
\operatorname{span}\{e_4-e_{15},e_5+e_{14},e_6-e_{13},e_7+e_{12}\}.
\]

Every listed zero-divisor diagonal has left and right nullity four. The false fixture remains `(e1+e10)(e2-e13)=e3+e7+e8-e12`. The twist passes 28,224 signed tests with zero mismatches, preserves the recorded probability on 1,008 within-kite and non-kite rows, and swaps all 84 edge sign types. The all-triples associator average remains 25/256, with control-one probability 231/512. [Census definitions and replay boundary](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/box_kite_census/README.md)

The arithmetic cross-check now includes six D=16 implementations: hypercomplex, hyprat, hypercomplex-engine, cayley-dickson, Cayley-Calculator and Octonion-Sedenion. Additional D=8 checks use pyoctonion, octonion through a signed relabeling, and Sage through its declared convention maps. The hypercomplex-algebra wrapper around hypercomplex-engine contributes no independent arithmetic witness. CI replays retained multiplication tables rather than reinstalling every package. Split-octonion controls share the octonion associator signs and strut lines while differing on basis signs, zero products and nullities. An associator-sign measurement therefore cannot distinguish these algebras by itself. [Package witness contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/box_kite_census/README.md)

### A shallower hardware witness has been generated on open PR #197

The reduced two-label LCU uses one selector, one data qubit and one CZ for
an edge or a strut. It reproduces the restricted census probabilities.
Its observable is a compiled sign pattern; full 16-dimensional Design B
remains a five-qubit circuit with 66–70 routed CZ in the first retained
Tuna acquisition. Open #197 keeps the deep family in the ideal CPU sweep
and proposes a shallow hardware depth ladder. These implementations must
retain distinct claims and observable names. [Program at the inspected open head](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/notes/box_kites/experiment-program.md)

### Box-kite implementation now has exhaustive emulator output

Open PR #197 advances beyond the proposal retained on main: it contains the circuit generator, shallow Tuna stages, remote smoke cases, and an actual completed Kaggle **qxelarator 0.10.0** sweep. The collection record is `COMPLETE`, collected at **2026-10-17 15:07:46 UTC**. Earlier text saying the full sweep was “not run” is stale relative to the retained output. This is classical ideal emulation on four CPU workers, Python 3.13.15, Qiskit 2.5.2 and NumPy 2.1.3. [Collection record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/results/kaggle/2026-10-17T131115Z-box-kite-qx-sweep/collect.json)

| Retained sweep | Circuits | Replicas | Registered checks | Probabilistic checks | Maximum absolute z | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Family a | 848 | 2,354 | 2,354 | 1,010 | 3.137786 | Pass |
| Families d/e | 149 | 281 | 399 | 267 | 2.916815 | Pass |

All circuits use **2,048 simulated shots**, totaling **997 circuits, 2,041,856 simulated shots and 2,753 checks**. Every deterministic check requires no off-prediction shot; probabilistic checks use the retained threshold `|z| < 4.5`. The passed sweep verifies these emitted implementations against their census-derived predictions. Its many checks are correlated through shared circuit outcomes and definitions; their count is not the number of independent discoveries. No shallow Tuna hardware acquisition or new remote QX/Ry acquisition is retained by this PR at the audited head. [Family-a record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/evidence/box_kite_qx_sweep/family-a.json), [family-d/e record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/evidence/box_kite_qx_sweep/family-de.json)

The open branch also reduces the proposed hardware program from the older **132-circuit, 44-batch** plan to **30 circuits in 10 batches**: ten witness circuits and twenty readout circuits. T0 has three batches at 16,384 shots, followed by two T1, two coherence and three walk batches at 4,096 shots, totaling **233,472 proposed hardware shots**. Every hardware batch has its own readout pair. Remote QX receives six family-a smoke circuits, four d/e smoke circuits and ten relabeled Tuna witness twins; exhaustive ideal work stays in the retained CPU sweep. [Generated cases and costs](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/notes/box_kites/HANDOFF-case-generator.md)

T0 uses one-, five- and nine-CZ reduced witnesses in a 3×3 Latin square on `(1,4)`, `(10,13)` and `(12,14)`. Its key advance is a **planned bright-minus-dark contrast estimator**, including each batch’s assignment correction, rather than inferring contrast from a single bright arm. The registered stop condition is a 99% upper bound on depth-one contrast below **0.5**; a per-CZ retention interval disjoint from **[0.87, 0.97]** refutes the planning range and resizes later stages. Pair-by-depth interactions and differing offsets remain accepted confounds of this small square. The proposed 0.72–0.82 shallow contrast is still a model prediction. The branch’s hardware-stage analyzer is listed as not started, so generator completion and an ideal sweep do not yet make the hardware acquisition and analysis chain complete. [T0 design, falsifiers and analysis work remaining](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/notes/box_kites/experiment-program.md), [handoff](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/1b89239b700c18a9f332828f7de7560f104610bd/docs/notes/box_kites/HANDOFF-case-generator.md)

### Source inventories preserve evidence boundaries

The retained inventories identify the monographs as secondary syntheses. D=16 facts used by the program enter through the reproducible census. Higher-dimensional scratch counts, random normal-form samples and Rule 1/Rule 2 checks remain second-hand until their computation is retained. The inventory also distinguishes the 11-dimensional single-element locus, V₂(ℝ⁷), from 14-dimensional zero-product pair geometry. Neither V₂(ℝ⁸) nor G₂ itself is interchangeable with the single-element locus. [Source and recomputation ledger](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/box_kites/inventory-monographs.md)

The ANF degree results remain written induction proofs with finite checks through dimension 256, rather than proof-assistant theorems. For n ≥ 2 and nonzero row index m, a multiplication sign row has degree n−1. For n ≥ 3 and distinct nonzero i,j, the fixed-pair associator phase has degree max(1, bitlen(max(i,j))−2). Quaternion and degenerate-pair associator phases are excluded from that latter formula. The retained upstream issue draft proposes their formalization and does not report it completed. [Degree proofs and status](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/cd_phase_degree.md)

### A₅ geometry gains provenance, not a global classification

The D-locus record contains 1,000 exact pairs from 200 frames: 200 members have nullity twelve and 800 non-members have nullity eight. PR #172 binds the limited replay's later rows to their frame, kind, keys and seeded scales. It does not fully verify suffix element hashes, A₄ nullity or kernel-combination length ratios; those require the full replay. The result reproduces known theorems on exact points. [D-locus scope](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/d_locus_nullity.py)

The earlier local-dimension certificate covers 29 named witnesses. Zero-divisor-only families attain dimensions eleven, seventeen and twenty-three at nullities sixteen, twelve and eight. Families containing a non-zero-divisor coordinate retain intervals 13–15, 19–21 or 25–27. The proposed two additional directions through e₈ and e₂₄ remain conjectural. There is no global covering or connected-component classification. [Local certificates and open bounds](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/rank_locus_local_dimension/README.md)

### The two-dimension A₅ gap is now an exact research program

PR #191 registers `a5-nonzero-divisor-two-dimension-gap` as **open**. It adds a design for deciding the remaining gaps; it does not claim that the computations have been performed. Four unit-locus families remain bounded as follows. [Rank-locus design](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/rank_locus_two_dimension_gap.md).

| Family | Nullity | Certified family dimension | Tangent upper bound |
|---|---:|---:|---:|
| `{a,0}`, with `a` a non-zero-divisor | 12 | 13 | 15 |
| `a` a zero divisor, `b` in `W(a)` | 8 | 19 | 21 |
| `a` a zero divisor, `b` a non-zero-divisor off the locus | 4 | 25 | 27 |
| Neither entry a zero divisor, C-orthogonal | 4 | 25 | 27 |

The conjecture says the upper bounds are attained and that the extra directions leave `H₅⊥` through `e₈` and `e₂₄`. The existing nullity-twelve cone at `e₁+e₁₈` has the `A15 ∪ B17` structure, and the 15-dimensional piece has actual curves leaving through `e₈`. This supplies a concrete lead for the first family, but it does not establish attachment to a non-zero-divisor axis witness. The new plan first computes the transverse projection, then the centered Schur second-order compatibility equations, and finally an exact closure test. [Gap conjecture and its lead](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/rank_locus_two_dimension_gap.md).

Two corrections in the final note matter mathematically. First, all tangent computations take place in `T(x) ∩ x⊥` and retain the norm row. The radial vector is automatically rank-preserving and contributes no evidence for the unit-locus gap. Second, the Schur obstruction must retain **all family variables**. Mixed family/transverse directions can satisfy a quadratic system even when pure transverse directions fail; restricting the equations to an arbitrarily chosen complement cannot decide the dimension. If the real second-order solution set lies wholly in the family tangent space, the obstruction can close the gap downward. If it contains a transverse solution, that supplies a candidate direction only. A larger dimension needs a certified higher-dimensional piece with exact nullity and a full-rank parameterization, or a semialgebraic tangent-cone dimension proof. A collection of curves whose velocities span many directions is insufficient. [Admission requirements](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/rank_locus_two_dimension_gap.md).

The global roadmap consequently begins with components of `D_(5,12)`, then regularity and links, kernel bundles, attachments, a global model and eventually a recurrence through the doubling tower. Each has its own proof obligation. A numerical chart does not cover all real coefficients; a frontier matrix does not supply attaching maps; matching homology does not prove the required equivalence. This work is exact classical mathematics and needs no hardware acquisition. The earlier box-kite census, package comparisons, D-locus sample certificate and local-dimension certificate are unchanged in this publication delta. [Global admission sequence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/rank_locus_two_dimension_gap.md).

### The current proof reconciliation has merged and binds every terminal observation

PR #174 merged at head `865fe58e343151585c4e0182239c4c12935de88f`. Its final retained source differs from the previously examined `c776e732` head. The current archive contains **257 files**, with **160 mathematical declarations across 11 scoped sources**, **39 original-byte binding assets**, **21 receipt targets** and a **29-source receipt closure**. Its external source is the published open_gororoba commit `d8e0c9bf263452e73f123e0525f38a955549b6d7`; its quantum inputs remain pinned to `a3d95ab60b25c4a6f18e5ff7c0435b4947abceb8`. The archive member count and manifest structure were inspected in this review; this review did not rerun the external Rust validator or the Rocq compiler. [Source identity](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/observable-contracts-source.json), [current reconciliation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/CURRENT_RECONCILIATION.md).

The schema-v2 manifest makes a useful distinction: all 160 theorem records describe mathematical results. **Seven typed terminal applications** and **one coherence application** supply the links to the experiment, including the decoder, normalization, observable and physical premises. The coherence application references all **27 coherence identities** and **12 Pauli decoders**. There are **30 raw decoder members** overall. A theorem about matrices therefore does not silently acquire the status of a verified hardware model. [Declaration and application delta](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/observable-contracts-delta.txt).

The final validator covers **all 16 hardware and all 16 replay terminal observations**. Each hardware PUB supplies 8,192 raw bitstrings with its register map and exact collected summary. Each replay count vector is uniquely recoverable from the retained six-decimal probabilities on the declared 8,192-shot grid, and its record, collection and per-replica summaries must agree. Ordered replay bitstrings were not retained. This closes the previous selected-input coverage gap while preserving a precise boundary between recovered count evidence and an assumed sampling law. The sorted inventory of all 39 assets also has a separately compiled SHA256 anchor, so coordinated changes to asset bytes and the manifest's own hashes cannot pass simply because the decoded statistic remains unchanged. [Full observation and source validation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/observable-contracts-delta.txt).

The numerical conclusion is unchanged. A degree-ten Bernoulli moment bound and finite union bound cover 32 means, each with 8,192 samples, at outward radius **0.021**. The certified family failure bound is approximately **0.04822313**. Selected hardware counts 2,964 and 4,911, and replay counts 4,067 and 4,057, yield exact separation margin **156109/1024000 = 0.1524501953125** after subtracting four radii. Under the common terminal-channel null and the declared within-mean IID Bernoulli laws, a false rejection has pre-data probability at most 0.05. Dependence across means is unrestricted. This is a conditional sampling guarantee; it supplies neither a posterior null probability nor a rejection of every ordinary hardware mechanism. [Certified concentration and multiplicity](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/observable-contracts-delta.txt).

The signed-coherence convention also remains fixed:

\[
\rho_{01,10}=\frac{XX+YY+i(XY-YX)}4.
\]

The three reconstructed coefficients remain immediate `(0.413330078125, -0.006103515625)`, matched idle `(0.15478515625, -0.34130859375)`, and measure/reset `(0.17724609375, -0.341064453125)`. Subnormalized branches retain their weights, and spectator correlations are allowed. The registered measure/reset quadrature comparison is unresolved. Physical interpretation still requires positive branch blocks with combined trace one, a justified assignment-error mixture, correct decoding and the stated sampling laws. QPY hashes establish archive identity; semantic correspondence between those bytes and the mathematical circuit remains an explicit obligation. [Coherence and physical premises](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/evidence/formal_certificates/CURRENT_RECONCILIATION.md).

### Open Quantum and engineering coverage

The captured Open Quantum account has six device offerings, 25 Spark Credits, zero Full Credits and no jobs. Thirty-nine backend/shot estimate points on both plans were retained at 05:24:54Z on October 17. At 1,024 shots, Public estimates are one credit for Rigetti, two for either IQM device, fifteen for AQT, and fifty for either IonQ device. These are captured estimates, not fresh availability or execution evidence. The catalogue supplies no gate durations or noise figures. [Platform record and costs](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/open_quantum/README.md)

PR #181 replaces enumerated lint/type lists with whole-directory coverage of live code, retaining explicitly named evidence replays. This includes twelve previously omitted files and reduces integration conflicts without rewriting checksum-bound historical evidence. [Merged CI configuration](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/ci/gates.json)

### Verification now checks upstream tables, actual proof compilation and merged records

Three changes address different failure modes.

**PR #200 restores independent table verification to hosted CI.** The `external-ground-truth` job fetches open_gororoba at `7d95d228db6be8a5b2f613430f04f2385d6ae48a`. It reconstructs the git-ignored 8D, 16D and zero-divisor CSVs from the upstream registry's headers and rows, admits the bytes only if their recorded SHA256 and size agree, then runs `verify.py` with that checkout as `GOROROBA_ROOT`. The tables are therefore not generated from the same `cd_core` implementation that the check evaluates. `core-401` exercises the materializer and `core-402` checks the fetch script. This CI source pin is distinct from the newer observable-proof snapshot's `d8e0c9bf` pin; the records serve different purposes. [Workflow](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/.github/workflows/ci.yml), [materializer](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/scripts/materialize_gororoba_csv.py).

**PR #201 adds fresh hosted Rocq replay.** A path filter selects proof sources, replay bundles, the replay driver, pins and workflow. The job builds a cached opam toolchain pinned to **Rocq 9.2.0 and OCaml 5.5.0**. Relevant pull requests replay the formal-certificate, C881, folding and N=21 target-flip bundles; matching main pushes, nightly and manual runs also include Stiefel. `core-403` checks agreement among the toolchain, bundle banners, path list and upstream fetch; `core-404` rejects twelve mutations. This is the historical receipt replay toolchain. It does not freshly compile the external 9.3 observable snapshot. A report must distinguish checksum validation, a freshly compiled implication and validation of experimental premises. [Pinned replay configuration](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/ci/rocq_toolchain.pin), [pin contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/ci/check_rocq_ci_pins.py).

**PR #190 tests the actual combined tree before merging.** `ci/premerge_gates.py` makes detached worktrees for main and the prospective merge and runs each tree's own PR-tier gates measured at five seconds or less. It fails on a newly broken or newly added failing gate; failures shared with main are listed separately. This targets whole-tree records such as the circuit toolchain record and research registry, which can pass on two branches separately and fail after their combination. It is a differential integration check, not a claim that every gate passes. `core-388` exercises the failure, clean-merge and textual-conflict cases. PR #203 adds the process ID to each scratch path so concurrent sessions cannot remove or overwrite each other's worktrees. [Premerge implementation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/ci/premerge_gates.py).

PR #199 restricts automatic cancellation to superseded pull-request runs. Started main runs can now finish their long full-tier gates while the newest pending main update waits. The change prevents rapid merges from repeatedly eliminating the long checks, though it does not itself establish that those checks are green. [Concurrency configuration](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/.github/workflows/ci.yml).

PR #205 remains an open documentation change. At its inspected head, it defines private account identifiers as credentials, account or instance IDs, CRNs and email addresses, while preserving public GitHub and Kaggle handles needed to resolve published records. It leaves the IBM CRN hashing rule unchanged. The proposal should be identified as open rather than silently applied as a merged repository rule. [Exact open head](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/fb98c51a66e16ce687aad4f1e9f717e0b5430770/AGENTS.md).

### Interpretations that remain unsupported

The new results do not establish a physical “strain” or cost of non-associativity. The linear encoding a→Lₐ is not an algebra homomorphism; ordinary associative matrix composition compares the encoded product wirings. An algebraic zero product appears as a zero-probability heralded branch, never destruction of the normalized quantum state. The registry still withdraws the common ghost, unital-error impossibility, readout-impossibility and algebra-dependent detuning claims. Implementation contrast leaves preparation, coherent control, incoherent noise, readout and sampling contributions unresolved. [Current design rules](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/AGENTS.md) · [Withdrawal registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/state/RESEARCH_STATE.md)

One historical-document trap persists: the older hardware-witness review says no zero-divisor circuit has run on hardware. That paragraph is superseded by the retained Kingston and Tuna acquisitions and the current registry; its mathematical corrections remain useful. [Historical review](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/2860b437601bff87b3e6d3957148bb7d79b7ea19/docs/notes/sedenion_hardware_witness_review.md)

## Reconciled experimental decisions

### Keep the complete ZZ design, revise the acquisition before using it

The [prepared static-neighbor case](../quantum_inspire/tuna_zz_map.md)
implements both directed Ramsey probes on every edge, with neighbor states
0 and 1, X/Y quadratures, equal explicit idles, a zero-idle reference and
four-state joint readout calibration. Eight induced matchings prevent the
selected probe pairs from directly coupling to other selected pairs in the
same pack. The estimator reconstructs the two effective frequencies and J,
propagates joint calibration covariance, tests reciprocal consistency and
adjusts the 24 edge tests with Holm's procedure. These are useful controls
for a comparison with the acquired map's equatorial-neighbor conditioning.

The new estimator defines the full flip difference as `f1 − f0 = −2 J/(2π)`
under its stated Hamiltonian. The existing map's `zz_shift_hz` field is
`+2 J/(2π)`. A comparison must convert the sign convention explicitly.
Neither quantity is the same observable as Kingston's frequency difference
between two distinct work qubits. A match near tens of kilohertz would
therefore compare scales; it would not recover the withdrawn common-ghost
premise.

Tuna's π/36 programmed-angle grid is not a hard frequency-resolution
floor. The X/Y readout rotations needed here are exactly representable;
free-precession phase remains continuous. Frequency uncertainty depends on
phase uncertainty and the separation of the retained delays, approximately
`sigma_f = sigma_phase / (2 pi delta_t)` for a two-point slope. A null result
can bound an effective conditional shift in that acquisition context; it
cannot by itself assign the IBM observation to a compiler or frame error.
The gate-only interface also yields effective Hamiltonian coefficients,
not a unique reconstruction of the coupler's parked flux or every mediated
path. CZ quality needs a separate repetition/interleaving experiment; this
idle case deliberately contains no CZ gates.

The reference has 384 Ramsey and 32 readout circuits, 139 batches, and
3,407,872 proposed hardware shots. Its six delays are 0, 0.5, 2, 8, 20 and
40 microseconds. At least 16,560 seconds of required pauses separate the
139 batches, before queueing, execution, collection or calibration. Every
delay must pass the frozen signal-quality guards. With three probes already
weak at 2 microseconds and visible calibration changes on much shorter
timescales than the series, successful all-edge estimation is unestablished.
The source-bound plan now records that limitation and the pause budget.

A scientifically useful next revision would begin with freshly calibrated,
short-delay reciprocal measurements on 11–14 and 1–4, plus 8–11 because its
two ends disagreed. Its delay range, target precision, calibration cadence,
alias restriction and stopping rules would be fixed before acquisition.
Q1/Q2 would enter a separately defined nonedge/drive comparison; there is no
direct 1–2 coupler to map. This is a recommendation for the next design,
not a generated or executed replacement pilot. The full reference and its
six-delay admission rule remain intact.

The [compact QX case](../quantum_inspire/tuna_zz_qx_preflight.md) is a
separate proposal: the same 416 circuits in 139 batches, using 2–8 active
qubits at 1,024 shots, or 425,984 emulator shots. Local parsing and
decomposition checks verify code and wiring properties. Earlier QX
acquisitions do not count as execution of this new preflight, and local
OpenSquirrel compilation does not verify the control stack's eventual ALAP
schedule.

### Preserve the corrected witness interpretation

The [secondary audit](../../../results/quantum_inspire/secondary/zero_divisor_tuna_17.md)
reproduces the first acquisition's point estimates while retaining
same-shot selector covariance and shared assignment uncertainty. Its raw
contrast is 0.041503906 with standard error 0.003197548; corrected contrast
is 0.043493846 with standard error 0.003353744. Both remain about thirteen
standard errors above zero. This confirms an encoded witness contrast
under the implemented circuit.

Several stronger readings need correction. The first run's raw bright
value is 0.512288, so the two endpoints straddle one half; their midpoint
is below one half. Corrected bright is still slightly above one half at
0.500601. The raw fixture's agreement with one half does not survive the
assignment correction: corrected fixture is 0.483588, z = −6.70. Pooled
agreement also hides opposing regional fixture deviations. The original
corrected H test is compatible with zero, while the later placement's H
interval excludes it; neither comparison isolates one channel because
selector, preparation and depth vary.

The endpoint-sum discrepancy rejects a *shared symmetric contraction*.
It does not rule out ordinary noise in general. Allowing different
effective contractions for the two circuits can reproduce their endpoints
with depolarizing-form maps. Equal CZ counts constrain a count-only
explanation, but do not prove equal channels. The corner has no resolved
contrast, with an interval including zero; an exact zero was not measured.

### Advance the remaining work according to its present evidence

**First, fix the measurement ambiguity.** The newly proposed double-X
control has widely separated predictions for Q0/Q6 under-rotation and
excited-state misassignment. A fresh fault-presence check and local
assignment references are prerequisites for interpreting a new long
scan. The readout series retain their registered verdicts. Issues #182
and #183 call for a separate sensitivity analysis that propagates shared
calibration uncertainty and calibrates the scan over decay time. Absolute
fit, boundary-hitting times and corrected visibility above one must remain
visible in that analysis.

**Then define a short reciprocal ZZ comparison.** Edges 11–14 and 1–4
have strong reciprocal estimates; 8–11 tests the existing endpoint
disagreement. Static-neighbor and driven-neighbor controls address
different terms. A separate Q1/Q2 nonedge comparison is necessary before
attributing that failure to a direct coupler. Keep the frozen 416-circuit
reference, but do not turn its unchanged 4.6-hour pause budget into the
next acquisition by default.

**Finish the shallow hardware analyzer before its first acquisition.**
Open #197 has the generator and a completed 997-circuit ideal sweep. Its
hardware analyzer remains unstarted. T0's planned bright-minus-dark
depth ladder, local assignment correction and preregistered stop rules
are the appropriate next implementation test. The predicted shallow
contrast remains a forecast. Its 30-circuit/10-batch proposal belongs to
the open branch; the older main proposal has 132 circuits and 44 batches.

**Preserve the distinct IBM case statuses.** The two Kingston pair cases
were retired. The fourteen-star construction and the Bell odd/even
consistency test remain unsubmitted proposals. The latter could test the
reduced diagonal Hamiltonian on the original device. The event-scale
sweep still has no retained production verdict; its three-valued rule
should survive completion. N=21 now has a concrete exact-model plan at
83.1 estimated seconds and a 95-second ceiling. Its model-effect and
calibration sensitivity need resolution before treating the narrow
power margin as reliable.

**Continue the exact and reproducibility work.** The A₅ gap has an exact
research design with explicit norm and second-order constraints. The
observable proof has merged and now binds every terminal observation;
its physical and sampling premises remain explicit. Open #193 improves
replay provenance without creating a second independent random sample.
The host GPU result is real and workload-specific. Open Quantum, Spin-2+
and a verified TPU remain prospects without the execution evidence needed
for a new device or accelerator comparison.

The immutable evidence links in the preceding sections support these
priorities. This integration generated no replacement short pilot and
launched no acquisition. It makes the full reference, revised scientific
interpretation and remaining concrete work reviewable in the draft.

## Integration and validation

The integration preserves current main's acquisitions, raw shot records and
historical manifests. It adds the secondary witness audit, the complete
static-neighbor generator and estimator, compact QX preflight, four new CI
gates and this reconciliation. The gates use core-497 through core-500
to avoid the IDs already introduced in open #193. The final manifest has
386 unique gates, compared with 382 on the integrated main snapshot. The two proposal manifests bind the current
catalogue, model and runner sources. All 832 new circuit files remain
byte-identical to the recovered prepared draft; the policy/source records
and interpretation were refreshed for current main.

All **28 affected gates passed** under Python 3.14.8 with the repository's
runtime, ruff 0.14.11 and mypy 1.19.1 pins. The selected set covers
whole-directory lint/format/types; shared instructions and gate identities;
research-state freshness and mutation checks; QI source/catalogue evidence;
all-case runner/retention checks; existing crosstalk, witness and ZZ replays;
the current device-context and fault records; premerge self-tests;
Rocq pin contracts; the retained exact N=21 validation; and all four new
modules. Normal and optimized Python are both exercised
where the registered commands require them.

| Validation group | Passed gates |
|---|---|
| CI, lint, formatting and types | core-000, core-001, core-002, core-039 |
| Shared instructions and manifest | core-250, core-265 |
| Registry and mutation checks | core-270, core-271 |
| QI sources, catalogue and retention | core-341, core-346, core-347 |
| Existing crosstalk/witness/map | core-327, core-330, core-331, core-332, core-333, core-348 |
| Toolchain and current device/readout context | core-368, core-387, core-400 |
| Premerge self-test and historical Rocq pins | core-388, core-403, core-404 |
| Retained exact N=21 validation | core-485 |
| Secondary witness, generator, estimator and compact QX | core-497, core-498, core-499, core-500 |

The [toolchain record](../../evidence/quantum_inspire/toolchain_check.json)
was regenerated during this integration with Python 3.13.16, libqasm 1.2.1 and
OpenSquirrel 0.9.1. All 1,000 current case circuits parsed and compiled. Its hashes and
compiler configurations were then checked again against the combined
2860b437 source; no additional regeneration was needed.
All **832 new circuits** additionally preserve their per-wire control and
gate sequences. Eleven pre-existing circuits have recorded gate sequence
changes under their configured decompositions. The new circuits have none.
The local check does not execute Quantify's ALAP scheduler, QX or hardware.

These are selected local integration checks, not a claim that every full-tier
simulation or hosted CI shard ran. No IBM, Quantum Inspire, Open Quantum or
Kaggle acquisition was launched for this integration. Publication as a draft
PR makes the source and proposed cases reviewable; acquisition status stays
unchanged.
