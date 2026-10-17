# Repository reconciliation — 17 October 2026

The newer results change the next experiment. Tuna-17 already has a measured
24-edge effective-ZZ map. Its largest conditional shifts are reproducible
from both ends, but the map does not explain all driven-neighbor effects.
A second placement of the deep zero-divisor witness retained less pooled
contrast, and the readout-delay experiment did not identify a satisfactory
decay model. On IBM, the added reanalyses refute a proposed amplitude
explanation and keep the phase mechanism unresolved. The mathematical and
software advances are substantial; their conclusions remain distinct from
claims about what causes hardware error. The sections below give the
measurements, assumptions, numerical comparisons and source links.

This review uses merged main
[`8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2`](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2)
as its fixed evidence snapshot. PR #144 is merged and its opening results
are now only part of the evidence. PR #174 is reviewed at
`c776e732e4f91c75752d614ac6864b06b8c322ed` and PR #184 at
`79ce8e10de1150336202e68098ebfb707b4d6a2d`; both remain open at the review
snapshot. Their contents are described as proposed changes, not silently
imported into main. Timestamps in this report are UTC. Historical service
snapshots are not assertions of present backend availability.

The baseline registry contains 112 claims and 75 retained acquisitions.
This integration adds one proposed static-neighbor cross-check, for 113
claims and the same 75 acquisitions. All hardware results discussed here
were already retained. Work for this review consists of source inspection,
secondary analysis, integration, local compiler checks and repository
validation. The complete acquisition table, including failed jobs, remains
in the [research state](../../state/RESEARCH_STATE.md).

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
| Tuna-17 | Crosstalk/teleport acquisitions, two hardware zero-divisor placements, all-edge ZZ estimates and readout-delay acquisitions | Effective static interactions, drive-associated shifts and witness loss require separate controls. |
| QX | Ideal controls for existing circuits, including witness and a 10-qubit/12-edge ZZ subgraph | The controls establish properties of the executed payloads. They do not validate the new 416-circuit compact preflight or hardware readout history. |
| Ry emulator | A failed teleport payload, bit-order diagnostic and later cQASM reader probes | Reader compatibility is now better characterized. This is emulation, even though the catalogue marks the backend type as hardware. |
| Kaggle CPU and T4 | Retained exact/noisy simulations, workload timings and numerical parity checks | These increase model-testing capacity without providing additional quantum-device measurements. |
| Requested Kaggle TPU | CPU executions from earlier requests and a later historically queued probe | There is no retained verified TPU performance result. |
| Spin-2+ | Captured unavailable backend instance, without an account-visible submission type | There is no spin-qubit replication in the record. |
| Open Quantum offerings | Six-backend catalogue, account credits and circuit-free estimates | There is no Open Quantum acquisition, device-bound noise model or completed witness comparison. |

The machine and acquisition distinctions above are bound by the
[baseline registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/state/RESEARCH_STATE.md),
[QI experiment record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/quantum_inspire/experiments.md),
[compute measurements](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/kaggle/substrates.md)
and [Open Quantum record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/open_quantum/README.md).

## Update coverage

The review follows the final merged files and retained run directories.
Several PR titles or opening descriptions predate results added later in
the same change. In particular, #177's final merged tree includes a Tuna
hardware series despite its title emphasizing QX, and #164 includes a
completed P-series analysis and later partial Q-series retention.

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
| Still open | [#174](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/174), [#184](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/184) | Observable-proof reconciliation; backend-version and processor-type provenance |

## Quantum Inspire: what the newer acquisitions establish

The repository now contains the 24-edge Tuna-17 conditional-Ramsey map that
the earlier discussion proposed. It also contains a second zero-divisor
hardware series and a completed P-series readout experiment. Those results
change the purpose of the prepared 416-circuit case: it is an independent
comparison with an existing map, and its long acquisition needs redesign
before execution. This assessment uses immutable main commit
[`8d5f038`](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2).
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
([Design and retained map](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/quantum_inspire/coupler_zz_tuna_17_analysis.json))

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

The [spectator comparison](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/quantum_inspire/spectator_zz_split.json)
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
([New hardware analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json))

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
([Experiment record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/quantum_inspire/experiments.md))

### The readout experiment returns an inconclusive mechanism test

The [P-series analysis](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/quantum_inspire/readout_ringdown_tuna_17_P_analysis.json)
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
enter the reported analysis. Series Q is retained through batch 04, with
no complete Q-series analysis at this snapshot.

The [device context](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/quantum_inspire/readout_ringdown_tuna_17_device_context.json)
records Q9 idle P1 increasing to 0.27–0.29, and Q0/Q6 prepared-state P1
falling to approximately 0.39/0.14 after calibration. Tuna returns the full
34-bit register, whereas QX returned only final outcomes. Thus completed
QX tests did not exercise the mid-circuit postselection path. The
postselection-difference error also collapses for many high-retention
subsets; its undefined z values provide no additional falsification.

### Provenance and the next acquisition decision

The [registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/state/research_state.json)
contains 112 claims and 75 acquisitions: 15 IBM and 60 Quantum Inspire.
The [05:53:53Z ledger](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/quantum_inspire/usage.json)
lists 184 jobs, 173 retained and 11 explicitly declared unretained. Those
11 completed Tuna jobs represent 90,112 shots, not an available scientific
analysis. The whole ledger reports 1,152,000 completed shots, 994.706513
execution seconds and zero transactions. Ledger v2 permits declared jobs
from other branches while checking retained evidence; passing checks do
not mean every account job's raw data are present.

Capture verification now fixes required inventories and source URLs;
transaction checks compare complete rows. The [runner](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/scripts/qi_platform.py)
also enforces a 120-second account-wide hardware pause and coordinates
token rotation across processes. The captured catalogue still has Spin-2+
offline and its backend type unavailable.

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

This section reads the repository at main commit `8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2`. The newer IBM work consists of reanalysis of retained hardware data, simulation and provenance improvements, and unsubmitted experiment designs. It supplies no new IBM hardware measurement of residual ZZ. Its main consequence is to make direct, controlled measurements more valuable: the existing phase and visibility discrepancies do not converge on one established mechanism.

For the Tuna follow-on, these findings favor an analysis that estimates conditional phase slopes and checks their consistency before interpreting the witness's lost contrast. Neighbor-state controls, matched exposure and readout correction make a static-coupling result interpretable. Driven-neighbor effects and post-readout tails require their own comparisons. A resolved ZZ value would support one component of the hardware model; it would not identify every error in the longer witness circuit.

### Fringe phase and amplitude now have different evidential outcomes

The coherent-family analysis compares detuning, conditional CZ phase, static ZZ in two reference frames, SX amplitude and rotation-axis tilt. Across fourteen atlas lanes, the best single family is partner-in-|0> ZZ on seven, detuning on four and axis tilt on three. Only two lanes satisfy the declared criterion of a leave-one-out residual within 1.5 times that model's noise floor. The remaining twelve stay 1.7–4.3 times above their floors. Choosing the lowest score after comparing families remains exploratory; it does not identify the physical cause. [Coherent-family evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/atlas_coherent_families/README.md)

The reference frame matters. Partner-in-|0> ZZ outperforms symmetric-frame ZZ on thirteen of fourteen linear fits and all fourteen resimulations, by a median score ratio of about 2.4. However, the repository has no source specifying the spectator state used in IBM's frequency calibration. The comparison motivates conditional Ramsey with a declared spectator state; it does not substitute for that measurement. [Frame comparison and its limits](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/coherent-error-families-report.md)

The amplitude analysis gives a firmer negative result. It studies the logarithm of hardware fringe amplitude divided by calibration-replay amplitude. Ten lanes exhibit structure beyond the declared per-lane shot-noise criterion. The proposed idle-relaxation-plus-constant predictor improves leave-one-edge-out RMS on four of eight confirming lanes, against six required. The preregistered prediction is therefore refuted. The parameter-free idle prediction is refuted on thirteen of fourteen lanes; its sole exception is also consistent with a constant. The retained full run is now `2026-10-17T030918Z-gororoba-atlas-fringe-amplitudes`, superseding the earlier run cited in the PR description. [Amplitude result and confirmation table](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/atlas_fringe_amplitudes/README.md)

This does not make idle relaxation irrelevant. The analysis demonstrates that the original unscheduled ISA replay omitted relaxation during waits between pulses. What fails is the claim that its idle-relaxation predictor explains the observed pattern across edges. The phase-fitted coherent families also fail to explain that amplitude pattern. Phase prediction and visibility prediction must remain separate tests.

### The recurring frequency scale remains a collection of distinct observations

The withdrawn common-ghost claim stays withdrawn. Kingston's matched-idle rotation corresponds to a 40.9 kHz frequency difference between work qubits 68 and 66, with winding alternatives. The Fez N=21 fitted phase involves different qubits, circuit, device and day. Similar numerical scale does not establish one shared source. Moreover, Kingston's matched idle has no preceding mid-circuit measurement, which disfavors a residual-photon explanation for that window while leaving post-readout mechanisms in other windows open. [Audited idle-phase interpretation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/ghost-frequency/README.md)

Calibration summaries do not resolve this ambiguity. The revised drift study binds 157 records and seventeen snapshots, comparing common qubit populations instead of treating every record as an independent calibration. Typical absolute T1 changes are approximately 15–25%, despite signed median changes no larger than 7.8%; the opposing movements cancel in the median. These retained medians contain no qubit frequency, so they neither establish nor exclude frame detuning. [Calibration drift evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/calibration_median_drift/README.md)

### Error multipliers expose missing model content without locating it

The error-scale sweep fits one CZ multiplier and one readout multiplier against each retained hardware distribution. Any omitted error can enter those fitted parameters. Four ordinary static runs require CZ factors of 1.5–2, compared with heuristic idle budgets of 1.3–1.6. Strongly dynamic runs require factors of 5–6 against idle budgets of 1.8–2.3. Yet the unexplained absolute budget per PUB overlaps: 0.23–0.42 for those dynamic runs versus 0.06–0.43 for the ordinary static runs. A wide static run without dynamic events also requires a factor of four. The larger dynamic multiplier therefore does not by itself identify feed-forward as the cause. [Error-scale results](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/ghost_error_scale/README.md)

The idle budget is a heuristic comparison of aggregated relaxation and reported CZ errors, not an exact channel decomposition. State averaging and the different dimensions of the compared average infidelities limit a literal causal interpretation. PUB bootstraps also omit model sampling uncertainty, and some fitted readout factors lie at the grid boundary. The later diagnostics correction halves duplicated coupler counts and separates cap fields while preserving simulation bytes; the dataset update repairs their provenance. [Budget definition](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/scripts/ghost_idle_budget.py) and [retained review](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/reviews/pr-147-ghost-error-scale.md).

The event-scale discriminator remains unfinished. Current code compares executed-schedule padding, CZ scaling, readout scaling and excess mid-circuit assignment error. The event error is now an X flip before measurement and after reset, replacing the earlier depolarizing-channel description. Conclusions use a near-best set and can be true, false or unresolved. No production event-sweep output is tracked at the reviewed commit, so it supplies no completed mechanism verdict. [Current event-sweep definition](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/scripts/ghost_event_scale.py)

### The new Kingston star directly covers the original work-qubit pair

The unsubmitted star-Ramsey design combines conditional, Bell and GHZ coherences. Twelve rates determine four effective qubit frequencies and three ZZ coefficients, leaving five consistency relations that can falsify the static diagonal model. The retained dry run places fourteen Kingston stars; its first has center 67 and leaves 57, 66 and 68. It therefore includes both work qubits of the original coherence-window comparison. Bell arms compile to two CZ and GHZ arms to six, with checks that preserve the physical star throughout idle and readout. Its near-zero simulated rates are properties of the supplied noise model, not measured hardware rates. [Star design](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/gororoba_quantum/star_ramsey.py) and [planned run record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/live/2026-10-17T023204.041725Z/record.json).

The readout research also narrows what can be assumed. The recorded `measure` durations are 1660 ns on Fez, 2180 ns on Kingston and 2684 ns on Marrakesh. Those pulse-to-digitization durations do not reveal resonator ring-down. The bounded source search found no device-bound resonator linewidth, dispersive shift or photon-decay measurement for these Heron r2 systems. PR #184, which adds backend version and processor type to every run record, remained open and is absent from this main commit. [Device-bound readout evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/ibm_quantum/heron-r2-readout-resonator.md) and [PR #184](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/184).

### N=21 synthesis improves, but acquisition admission still fails

The exhaustive linear-encoding search covers 83,328 cosets under its declared surrogate. Routed admission on FakeFez reduces median CZ from 5422 to 3933 for ten rounds and from 1107 to 739 for the two-round diagnostic. Separate calibrated simulations raise Kingston's two-round contrast from 0.0067 to 0.0417. These are substantial compilation and modeled-signal gains; ten-round modeled order recovery nevertheless remains 0.129–0.139, at or below the depolarized statistic of 0.1445. [Encoding evidence and scope](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/linear_conjugation/README.md)

The subsequent dry run is explicitly `design_infeasible`. Its predicted contrast of 0.034317 loses 0.033456 to the simultaneous simulation allowance, leaving only 0.000861 as the effect used for power. This supersedes any reading of the earlier optimistic shot estimate as an admitted experiment. [Admission record](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/results/live/2026-10-17T003834.987727Z/record.json)

### Compute improvements expand verification capacity

The retained CPU/T4 crossover is workload-specific: static twelve-qubit density matrices take 105.4 seconds on CPU versus 8.3 on T4, while fourteen-qubit cases take 1955.2 versus 110.8 seconds. Actual seven-qubit N=21 circuits favor CPU trajectories by 1.5–8 times, and the retained batched GPU sampler fails on control flow. The measured Kaggle guidance recommends twelve static or eight dynamic qubits, but other repository routing text still uses the local eleven-qubit threshold. That inconsistency needs reconciliation before describing a uniform policy. [Substrate measurements](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/kaggle/substrates.md)

The JAX bridge cuts the retained 105-replica CPU sweep from 1389 seconds to 22 by exporting once per structure and rescaling CZ channels. Independent NumPy/Aer parity is 1.9e-9; complex64 JAX differs from its reduced NumPy reference by 2.9e-6. This accelerates a specified model without validating additional physical mechanisms. [Bridge contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/kaggle/jax-bridge-structure-report.md)

No verified TPU benchmark is retained. Earlier TPU requests ran on CPU workers; the verified-account probe's last timestamped observation was queued after seven hours eight minutes. This is a historical observation, not a current queue status. [TPU evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/kaggle/tpu-research.md)

Validation coverage also improves: full-tier coherent-fit checks now accommodate bounded numerical conditioning effects; N=21 verification recompiles every retained seed; scenario budgets use their own latency; routed controls determine window sizes; and the IBM reconstruction of Tuna circuits checks every star and teleport path. These repairs increase confidence in the retained implementation evidence. They do not turn an independent-channel model's zero crosstalk prediction into a Kingston hardware result. [Coherent replay](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/atlas_coherent_families/README.md), [N=21 replay](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/scripts/n21_conjugation_noise.py), [planning changes](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/commit/ae2d75ba7cb747ba7d7bbbff3c1c5218bc47d895), and [Tuna-circuit comparison](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/quantum_inspire/experiments.md).

## Algebra, formal proofs and the additional platform

The mathematical updates strengthen the repository's exact specification and its connection to recorded observables. They preserve the distinction between an algebraic identity, an implementation of that identity, and an explanation of hardware error. The merged baseline for this section is `8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2`. The observable-proof reconciliation remains open in PR #174 at `c776e732e4f91c75752d614ac6864b06b8c322ed`.

### The box-kite census now supplies exact experimental targets

The census examines all 44,100 ordered products of 210 two-blade representatives. Its 336 zero products agree with `cd_core`'s corpus; the remaining unnormalized squared product norms are 4 for 43,428 products and 8 for 336. The finite geometry has seven box-kites, 42 assessor planes and 84 signed diagonal representatives. Each kite has six assessors, three struts and twelve edges; globally there are 42 same-sign and 42 opposite-sign assessor edges. These correspond to 168 undirected signed-diagonal zero-product pairs, or 336 ordered products. Those counts describe different objects within the continuous zero-divisor geometry. [Exact census](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/box_kite_census/census.json)

For the original operand, the retained annihilator is

\[
\operatorname{Ann}(e_1+e_{10})=
\operatorname{span}\{e_4-e_{15},e_5+e_{14},e_6-e_{13},e_7+e_{12}\}.
\]

Every listed zero-divisor diagonal has left and right nullity four. The false fixture remains `(e1+e10)(e2-e13)=e3+e7+e8-e12`. The twist passes 28,224 signed tests with zero mismatches, preserves the recorded probability on 1,008 within-kite and non-kite rows, and swaps all 84 edge sign types. The all-triples associator average remains 25/256, with control-one probability 231/512. [Census definitions and replay boundary](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/box_kite_census/README.md)

The arithmetic cross-check now includes six D=16 implementations: hypercomplex, hyprat, hypercomplex-engine, cayley-dickson, Cayley-Calculator and Octonion-Sedenion. Additional D=8 checks use pyoctonion, octonion through a signed relabeling, and Sage through its declared convention maps. The hypercomplex-algebra wrapper around hypercomplex-engine contributes no independent arithmetic witness. CI replays retained multiplication tables rather than reinstalling every package. Split-octonion controls share the octonion associator signs and strut lines while differing on basis signs, zero products and nullities. An associator-sign measurement therefore cannot distinguish these algebras by itself. [Package witness contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/box_kite_census/README.md)

### The proposed hardware program uses a narrower, shallower witness

PR #179 proposes a two-label LCU with one selector, one data qubit and one CZ for either an edge or a strut. It reproduces the restricted census probabilities, but it tests a compiled sign pattern rather than full 16-dimensional left multiplication. Full Design B remains a five-qubit implementation with 66–70 routed CZ in the retained Tuna acquisition. The new program keeps that deep version on QX. It includes no new circuit generator or acquisition. [Experiment program](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/box_kites/experiment-program.md)

| Proposed program | Circuits | Batches | Shots |
|---|---:|---:|---:|
| Exhaustive QX families | 997 | 203 | 2,041,856 |
| QX twins of Tuna stages | 132 | 44 | 270,336 |
| Ry diagnostics and subset | 26, plus up to 10 adaptive | 6, plus adaptive | 1,024 per circuit |
| Tuna stages T0–T2 | 132: 44 witnesses and 88 readout controls | 44 | 2,162,688 |

T0 measures a depth ladder before T1 classifies the seven-kite subset and T2 measures twist pairs, coherence and associator walks. The proposed matching `{(1,4),(10,13),(12,14)}` and predicted pessimistic contrast 0.72–0.74 depend on older visibility/readout measurements and a single-depth-point model. The document explicitly allows newer Ramsey data to re-rank layouts. These are planning estimates, not observed shallow-witness performance. [Stages, admission and budgets](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/box_kites/experiment-program.md)

### Source inventories preserve evidence boundaries

The retained inventories identify the monographs as secondary syntheses. D=16 facts used by the program enter through the reproducible census. Higher-dimensional scratch counts, random normal-form samples and Rule 1/Rule 2 checks remain second-hand until their computation is retained. The inventory also distinguishes the 11-dimensional single-element locus, V₂(ℝ⁷), from 14-dimensional zero-product pair geometry. Neither V₂(ℝ⁸) nor G₂ itself is interchangeable with the single-element locus. [Source and recomputation ledger](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/box_kites/inventory-monographs.md)

The ANF degree results remain written induction proofs with finite checks through dimension 256, rather than proof-assistant theorems. For n ≥ 2 and nonzero row index m, a multiplication sign row has degree n−1. For n ≥ 3 and distinct nonzero i,j, the fixed-pair associator phase has degree max(1, bitlen(max(i,j))−2). Quaternion and degenerate-pair associator phases are excluded from that latter formula. The retained upstream issue draft proposes their formalization and does not report it completed. [Degree proofs and status](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/cd_phase_degree.md)

### A₅ geometry gains provenance, not a global classification

The D-locus record contains 1,000 exact pairs from 200 frames: 200 members have nullity twelve and 800 non-members have nullity eight. PR #172 binds the limited replay's later rows to their frame, kind, keys and seeded scales. It does not fully verify suffix element hashes, A₄ nullity or kernel-combination length ratios; those require the full replay. The result reproduces known theorems on exact points. [D-locus scope](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/scripts/d_locus_nullity.py)

The earlier local-dimension certificate covers 29 named witnesses. Zero-divisor-only families attain dimensions eleven, seventeen and twenty-three at nullities sixteen, twelve and eight. Families containing a non-zero-divisor coordinate retain intervals 13–15, 19–21 or 25–27. The proposed two additional directions through e₈ and e₂₄ remain conjectural. There is no global covering or connected-component classification. [Local certificates and open bounds](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/evidence/rank_locus_local_dimension/README.md)

### Open PR #174 supplies a conditional statistical proof

The unmerged reconciliation retains 235 snapshot files binding 160 declarations across eleven sources to 25 original-byte assets, with 21 receipt targets over a 29-source closure. It records the external Rocq 9.3 toolchain while preserving historical Rocq 9.2 receipts. Its terminal-channel certificate adds a degree-ten Bernoulli moment bound and a union bound for 32 means of 8,192 samples, using exact radius 0.021. The certified family failure bound is approximately 0.04822313. Hardware counts 2964 and 4911, and replay counts 4067 and 4057, give an exact separation margin of 156109/1024000 after four radii are subtracted. [Retained proof delta](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/c776e732e4f91c75752d614ac6864b06b8c322ed/docs/evidence/formal_certificates/observable-contracts-delta.txt)

This is a pre-data false-rejection guarantee under the common terminal-channel null and declared IID Bernoulli marginal laws. Across-mean dependence is allowed; within-mean stationarity, independence and decoder correctness remain premises. The result supplies no posterior probability that the null is true and excludes no unspecified alternative mechanism. QPY hashes establish archive identity, while circuit-semantic correspondence remains an obligation. [Current proof reconciliation](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/c776e732e4f91c75752d614ac6864b06b8c322ed/docs/evidence/formal_certificates/CURRENT_RECONCILIATION.md)

The signed-coherence convention is

\[
\rho_{01,10}=(XX+YY+i(XY-YX))/4.
\]

It retains subnormalized branch weights and permits spectator correlations. Positive branch blocks with combined trace one and independent assignment mixing are physical premises. The registered measure/reset quadrature comparison remains unresolved; a rotated coefficient alone identifies no cause. [Signed-coherence contracts](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/c776e732e4f91c75752d614ac6864b06b8c322ed/docs/evidence/formal_certificates/CURRENT_RECONCILIATION.md)

### Open Quantum and engineering coverage

The captured Open Quantum account has six device offerings, 25 Spark Credits, zero Full Credits and no jobs. Thirty-nine backend/shot estimate points on both plans were retained at 05:24:54Z on October 17. At 1,024 shots, Public estimates are one credit for Rigetti, two for either IQM device, fifteen for AQT, and fifty for either IonQ device. These are captured estimates, not fresh availability or execution evidence. The catalogue supplies no gate durations or noise figures. [Platform record and costs](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/open_quantum/README.md)

PR #181 replaces enumerated lint/type lists with whole-directory coverage of live code, retaining explicitly named evidence replays. This includes twelve previously omitted files and reduces integration conflicts without rewriting checksum-bound historical evidence. [Merged CI configuration](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/ci/gates.json)

### Interpretations that remain unsupported

The new results do not establish a physical “strain” or cost of non-associativity. The linear encoding a→Lₐ is not an algebra homomorphism; ordinary associative matrix composition compares the encoded product wirings. An algebraic zero product appears as a zero-probability heralded branch, never destruction of the normalized quantum state. The registry still withdraws the common ghost, unital-error impossibility, readout-impossibility and algebra-dependent detuning claims. Implementation contrast leaves preparation, coherent control, incoherent noise, readout and sampling contributions unresolved. [Current design rules](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/AGENTS.md) · [Withdrawal registry](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/state/RESEARCH_STATE.md)

One historical-document trap persists: the older hardware-witness review says no zero-divisor circuit has run on hardware. That paragraph is superseded by the retained Kingston and Tuna acquisitions and the current registry; its mathematical corrections remain useful. [Historical review](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/8d5f038b56631f4c1a97dce6f57b59ae6a15a3e2/docs/notes/sedenion_hardware_witness_review.md)

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

The **IBM star** is the most direct prepared device-specific probe of the
original Kingston work-qubit setting. Its consistency relations can test
the reduced diagonal Hamiltonian. Its next acquisition still needs a
current admitted record and measured rates; simulation supplies neither.

The **readout study** needs an analysis that distinguishes persistent arm
offsets, calibration drift and a decaying response, with absolute
goodness-of-fit. The partial Q series and failed exponential fits cannot
be summarized as a measured resonator lifetime. Reusing a stale assignment
matrix would also carry the existing visibility pathology forward.

The **shallow box-kite program** offers a lower-depth experiment with
well-defined algebraic targets. Its first depth ladder is more informative
than treating the proposed 0.72–0.74 contrast as a prediction already
validated on Tuna. A restricted two-label witness and full Design B should
keep distinct observable names and claims.

The **event-scale sweep** remains an analysis task, with no completed
production result at this snapshot. Its three-valued decision rule should
be retained. The **N=21 encoded acquisition** remains inadmissible under
the current simultaneous-error allowance despite improved compilation.
The **formal-proof update** adds precise statistical guarantees subject to
its premises; connecting archived circuit semantics to those premises
remains necessary. **Open Quantum and TPU** remain service/compute
prospects without the hardware or accelerator result needed for a new
cross-platform claim.

The sources for these decisions are the immutable evidence links in the
preceding sections. The report preserves withdrawn mechanism claims,
failed predictions and unresolved comparisons alongside positive results.

## Integration and validation

The integration preserves current main's acquisitions, raw shot records and
historical manifests. It adds the secondary witness audit, the complete
static-neighbor generator and estimator, compact QX preflight, four new CI
gates and this reconciliation. The two proposal manifests bind the current
catalogue, model and runner sources. All 832 new circuit files remain
byte-identical to the recovered prepared draft; the policy/source records
and interpretation were refreshed for current main.

All **22 affected gates passed** under Python 3.14.8 with the repository's
runtime, ruff 0.14.11 and mypy 1.19.1 pins. The selected set covers
whole-directory lint/format/types; shared instructions and gate identities;
research-state freshness and mutation checks; QI source/catalogue evidence;
all-case runner/retention checks; existing crosstalk, witness and ZZ replays;
and all four new modules. Normal and optimized Python are both exercised
where the registered commands require them.

| Validation group | Passed gates |
|---|---|
| CI, lint, formatting and types | core-000, core-001, core-002, core-039 |
| Shared instructions and manifest | core-250, core-265 |
| Registry and mutation checks | core-270, core-271 |
| QI sources, catalogue and retention | core-341, core-346, core-347 |
| Existing crosstalk/witness/map | core-327, core-330, core-331, core-332, core-333, core-348 |
| Toolchain record | core-368 |
| Secondary witness, generator, estimator and compact QX | core-390, core-391, core-392, core-393 |

The [toolchain record](../../evidence/quantum_inspire/toolchain_check.json)
was freshly regenerated with Python 3.13.16, libqasm 1.2.1 and
OpenSquirrel 0.9.1. All 1,000 current case circuits parsed and compiled.
All **832 new circuits** additionally preserve their per-wire control and
gate sequences. Eleven pre-existing circuits have recorded gate sequence
changes under their configured decompositions. The new circuits have none.
The local check does not execute Quantify's ALAP scheduler, QX or hardware.

These are selected local integration checks, not a claim that every full-tier
simulation or hosted CI shard ran. No IBM, Quantum Inspire, Open Quantum or
Kaggle acquisition was launched for this integration. Publication as a draft
PR makes the source and proposed cases reviewable; acquisition status stays
unchanged.
