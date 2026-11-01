# Ascella-Belenos entanglement and teleportation

This design asks whether an accessible Quandela configuration supports shared
entanglement and quantum-state teleportation between the physical systems
behind `qpu:ascella` and `qpu:belenos`, and which dependency limits the
strongest supported claim. "Tele-teleportation" means Ascella to Belenos to
Ascella sequential teleportation; entanglement swapping through a third
physical Bell-measurement station is a separate extension. Work status lives
in [the plan record](../state/plans/ascella-belenos-entanglement-teleportation.json),
scientific claims in [research_state.json](../state/research_state.json), and
execution authority in each case's approval record. Nothing here authorizes a
provider job, upload, reservation or message.

## Claim levels

| Level | Claim | Required evidence | Status |
|---|---|---|---|
| C0 | The workstation coordinates and records separate QPU jobs. | Bound requests, terminal results, platform identity, full retention. | Supported by the retained Ascella and Belenos runs. |
| C1 | A local optical circuit family conforms to its registered observables. | Qualified preparation/analyzer model, setting-to-count association, registered tolerances. | Supported for the Ascella signed-coherence family under its composite-request model ([job-00](../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/README.md), [job-01](../../results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/README.md)). |
| C2 | An accepted resource is entangled across the Ascella and Belenos partitions. | Physical resource distribution, valid local measurement and selection, witness beyond the separable bound. | Unestablished; no physical path. |
| C3 | A cross-device protocol teleports input states through a Bell resource and Bell measurement. | C2, protocol identity, classical benchmark exceeded on joint records. | Unestablished. |
| C4 | The transfer preserves entanglement with an untouched reference. | Reference-output witness after the transfer. | Unestablished. |
| C5 | The destination carrier survives into a further quantum operation. | Carrier continuity, control timing, downstream quantum-sensitive test. | Unestablished. |
| C6 | Two consecutive teleportations act on one surviving logical state. | Two resources, two physical Bell measurements, composed frame, end-to-end test. | Unestablished. |

C4 separates the transfer from every measure-and-prepare channel, because an
entanglement-breaking channel leaves the reference separable from the output
([quant-ph/0302031](../notes/papers/quant-ph-0302031.md)). The apparatus
record, not the statistics, separates teleportation from coherent
transmission, so C3 and C4 each carry both.

## The partition constraint

Local operations and classical communication map a separable state across
the Ascella|Belenos cut to a separable state, including after conditioning on
the full classical transcript
([1210.4583](../notes/papers/1210.4583.md)). Two independent terminal jobs
joined by the workstation therefore establish no C2 to C6 claim, whatever
their counts: pairing two output files by row is classical data association.
Every cross-device level needs a shared entangled resource or a physical
quantum path that creates one, which only the provider can supply. The
inspected access exposes two one-platform QPUs and no joint platform, port
map or interconnect. The March 2026 roadmap dates quantum-networking scaling
to 2028-2029 (pp. 2 and 6), opens a networking band in its 2027 column
(p. 5), places its one interconnect hardware cell, modular scaling via
interconnected cabinets, in 2030-31 (p. 6), and names Ascella and Belenos only
in single-photon and cluster-state product cells (pp. 4-6)
([roadmap note](../notes/quandela/roadmap-2026-03.md)); it is development
context, and access needs a provider record.

## Evidence baseline

- **Platforms.** [calibration.md](../notes/quandela/calibration.md#current-state)
  holds the dated catalogue figures (12 and 24 modes, 6 and 12 declared
  photons, source-connected inputs, clocks, HOM, g2, dark maxima). Within-QPU
  HOM figures describe each source against itself and supply no cross-source
  overlap. [platform-specifications.md](../notes/quandela/platform-specifications.md)
  records that Perceval 1.3.1 reads `support_multi_photon = false` as at most
  one declared input photon per mode.
- **Ascella.** Both signed-coherence jobs qualify all 27 endpoints. The
  outside-block decomposition is done: dilution removes 18 % of the X and
  33 % of the Y sign-odd shortfall, outside-block clicks follow the
  execution sequence rather than the setting, and an analyzer contrast near
  0.97 with reproducing per-configuration residuals remains
  ([conformance design](ascella-signed-coherence-conformance.md)). The
  remaining mechanism question is the next action of
  [its plan](../state/plans/ascella-signed-coherence-conformance.json).
- **Belenos.** The stationarity primary stays inconclusive with a residual
  superposition spread ([bdsc-qualification.md](bdsc-qualification.md#stationarity-under-a-stray-detector-veto)).
  The seven-run drift series completed; its exact permutation primary reads
  consistent, p = 0.056 over 5040 orderings
  ([readout](../../results/quandela/bdsc_drift_series_readout_pinned.json),
  [design](bdsc-qualification.md#drift-series-of-one-frozen-request)). The
  imaginary-superposition Fourier setting whose counts follow the preceding
  setting's compilation keeps setting-to-count association open; the
  [predecessor intervention](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention)
  is the drafted test, with its admission conditions unresolved.
- **Observation contract.** The open semantics of returned circuits, count
  provenance, processing versions and acceptance calibration live in
  [provider_contract.json](../evidence/bdsc/provider_contract.json). Perceval
  1.3 documents `mitigations=[]` as disabling remote mitigation and `None` as
  the provider default
  ([error mitigation](../notes/quandela/perceval/reference/runtime/error_mitigation/index.md));
  an empty list is a request field, not proof of raw event provenance.
- **Tuna-17 precedent.** The Quantum Inspire run implements a Bell resource,
  an intraprocessor SWAP of one half, a Bell-basis rotation and analysis-side
  Pauli correction on one device
  ([experiments.md](../notes/quantum_inspire/experiments.md)). Its
  correction `X^m(P1) Z^m(I)` follows a full four-outcome gate-model Bell
  measurement, so the dual-rail frames here come from their own derivation;
  its role bookkeeping and terminal-record analysis carry over, and its
  cross-path summary is no uniform-ensemble channel benchmark.

## Gates

| Gate | Proceeds when | Status |
|---|---|---|
| G0 Evidence | Every premise has a dated source and stale summaries have successors. | Met by this design and the calibration reconciliation. |
| G1 Observation | Event provenance, setting identity, preparation/analyzer scope and selection support the inference. | Open: provider_contract rows and the Belenos association question. |
| G2 Physical access | A provider-bound record identifies the carrier, source, ports, quantum operation, detector boundary and access route across the partitions. | Hold: no route in the inspected access. |
| G3 Optical feasibility | Selected-path calibration and a rate budget fit an informative test. | Waits on G1 and G2. |
| G4 Entanglement | The registered lower witness bound exceeds 1/2 under valid selection. | Waits on G3. |
| G5 Teleportation | The registered lower fidelity bound exceeds the applicable classical bound on joint records. | Waits on G4. |
| G6 Reference | The reference-output witness exceeds its separable bound. | Waits on G5. |
| G7 Live output | A carrier survives into a downstream quantum operation (level O1 or higher). | Waits on G5. |
| G8 Sequential | Two Bell operations act on one coherent intermediate state and the composite benchmark passes. | Waits on G5 and G7. |

G6 and G7 answer different questions: a terminal reference test shows no
reusable output, and a surviving carrier shows no channel fidelity.

## Protocol reference

[`scripts/qd_network_protocol.py`](../../scripts/qd_network_protocol.py)
computes every table in this section from the bosonic transformation, and
[its test](../../tests/scripts/test_qd_network_protocol.py) cross-checks the
propagation against dense permanents and Perceval's SLOS backend; `--tables`
prints them. The model is ideal: indistinguishable photons, no loss, no
multiphoton emission, no dark events.

Roles are q (input, Ascella), a (sender half), b (receiver half, Belenos), R
(reference) and h (heralds). Dual rail encodes `|0_L> = |1,0>` and
`|1_L> = |0,1>`; logical labels stay separate from physical mode indices until
routing is verified. The resource is `Phi+ = (|00> + |11>)/sqrt2`.

**Partial Bell analyzer.** Balanced beam splitters mix rail j of q with rail
j of a under `q_j^dag -> (c_j^dag + d_j^dag)/sqrt2` and
`a_j^dag -> (c_j^dag - d_j^dag)/sqrt2`. In output order `[c0, c1, d0, d1]`:

| Bell input | Accepted threshold patterns | Receiver byproduct (x, z) |
|---|---|---|
| psi+ | `1100`, `0011` | (1, 0) |
| psi- | `1001`, `0110` | (1, 1) |
| phi+, phi- | single-click patterns shared by both | rejected |

Each of the six Pauli inputs is accepted with probability 1/2, the limit for
passive linear optics with vacuum ancillas
([quant-ph/0007058](../notes/papers/quant-ph-0007058.md)), and every accepted
branch reaches fidelity 1 after correction. The table fixes a convention, not
a configured Quandela analyzer; the hardware detector map comes from the
compiled optical model and its calibration. Threshold detectors resolve these
patterns only in the ideal photon-number sector, so excess emission and loss
need a false-acceptance bound.

**Decoder.** For byproduct `X^x Z^z`, a raw receiver bit d decodes to
`d xor x` in Z, `d xor z` in X and `d xor x xor z` in Y. A record keeps the
raw bit, the Bell pattern, the frame and the decoded bit together.

**Reference preservation.** With `Phi+` between R and q (four photons, eight
modes), every accepted pattern leaves (R, b) in `Phi+` after the frame
correction.

**Sequential transfer.** Two analyzers (q with a1, then b1 with b2; five
photons, ten modes) compose to `(x1 xor x2, z1 xor z2)` on all 16 accepted
pattern pairs.

**Sizes.** Logical minima are three data photons in six modes for one
teleportation, four in eight with a reference, five in ten for two hops, and
six in twelve for two hops with a reference; factory, herald, routing and
dump modes add to them. Fixed-number Fock dimensions `C(m+n-1, n)` are 56,
330, 2002 and 12,376 for those cases and 834,451,800 at 12 photons in 24
modes, so simulation restricts itself to the protocol modes and states its
truncation. Threshold patterns with 1 to 6 clicks on 12 modes number 2509, and
with 1 to 12 clicks on 24 modes 9,740,685.

## Decision statistics

**Entanglement witness.** For target `Phi+`,
`F = (1 + C_XX - C_YY + C_ZZ)/4`, and `F > 1/2` certifies entanglement of a
valid two-qubit state; the classically correlated mixture of `|00>` and `|11>`
reads exactly 1/2. For independent valid +-1 samples under a common-state and
basis-independent selection model, the one-sided Hoeffding bound is
`F_L = F_hat - sqrt(ln(1/alpha)/8 (1/n_X + 1/n_Y + 1/n_Z)) - eps_sys`, with
`eps_sys = (eps_X + eps_Y + eps_Z)/4` for known correlator error limits. A
statistical radius of 0.03 needs 1919 valid pairs per axis at alpha 0.01 and
2590 at alpha 0.002; these exclude systematics, dependence and loss, and price
nothing.

**Teleportation benchmark.** The input ensemble is the six Pauli eigenstates
with weight 1/6, measured on all three output axes: 18 setting cells per
direction before controls. For a fixed trace-nonincreasing accepted instrument
E, the success-weighted fidelity is
`F_succ = sum_i p_i tr[rho_i E(rho_i)] / sum_i p_i tr[E(rho_i)]`. A fixed
single-copy measure-and-prepare instrument `rho -> sum_k tr(M_k rho) sigma_k`
satisfies `F_succ <= 2/3`: the ensemble obeys `sum_i p_i rho_i = I/2` and
`sum_i p_i rho_i (x) rho_i = (I + SWAP)/6`, so the numerator is
`sum_k [tr M_k + tr(M_k sigma_k)]/6 <= sum_k tr M_k / 3` against the
denominator `sum_k tr M_k / 2`. Postselection alone leaves the bound intact;
input-label access, early analyzer-basis disclosure, basis-dependent
selection, a changing channel or accepted multiphoton sectors carrying extra
input copies each void it, and the benchmark for such a case is derived
again ([quant-ph/9807091](../notes/papers/quant-ph-9807091.md)). The derived
benchmark optimizes over entanglement-breaking accepted operations through
the Choi state `J = (I (x) E)(|Phi+><Phi+|)` with `J >= 0`, `J^T_in >= 0` and
`tr_out J <= I/2`; PPT characterizes separability in this 2x2 case
([quant-ph/9605038](../notes/papers/quant-ph-9605038.md)).

**Benchmark solver.** [`scripts/qd_classical_benchmark.py`](../../scripts/qd_classical_benchmark.py)
solves that program for any pure-state ensemble and priors, in the Choi
normalization `J = sum_ij |i><j| (x) E(|i><j|)` (so `tr_out J <= I`), for
three figures: the pooled conditional fidelity under free post-selection, the
pooled figure under a fixed success profile, and the mean of per-input
conditional fidelities under a fixed profile. A qubit map's success is affine
in the Bloch vector, so a profile enters as independent constraints on the
acceptance operator `tr_out J`, and a measured profile is first fitted to that
form (`realizable_profile`). Each bound comes from the dual program, with the
dual variables projected onto the PSD cone and the residual's least
eigenvalue charged against a bound on `tr J`, so it holds for every classical
strategy whatever the solver's accuracy; the primal optimum supplies the
achieving Choi operator. The uniform six-state ensemble returns 2/3, and the
tested tilted profiles keep both figures at 2/3. Unequal priors raise the
bound: Z eigenstates at weight 1/4 each give 3/4 (measure Z), and `+Z` at
1/2 with the other five at 1/10 gives 6/7, reached by keeping only the `+Z`
outcome of a Z measurement. The pooled figure of `joint_teleportation_scores`
weights each input by its matching-basis attempts, so `attempts_benchmark`
supplies the benchmark for an unequal allocation, and the four BB84 states
give 3/4 ([its test](../../tests/scripts/test_qd_classical_benchmark.py)).

**Counts and composition.** A one-sided Bernoulli decision at type-I error
alpha and power `1 - beta` needs
`N >= (sqrt(ln 1/alpha) + sqrt(ln 1/beta))^2 / (2 (F* - B - eps_sys)^2)`;
at alpha 0.01, beta 0.10, B = 2/3 and eps_sys 0.02 that is 1673, 523 and 148
outcomes for F* = 0.75, 0.80 and 0.90. Two identical depolarizing hops of
average fidelity f compose to `(1 + (2f - 1)^2)/2`: 0.625 at f = 0.75 and
0.68 at f = 0.80, above 2/3 only for `f > (1 + 1/sqrt3)/2 = 0.7887`.

**Inference conditions.** Tomography assumes one object across the
measurement set, and source drift defeats it
([1302.0932](../notes/papers/1302.0932.md)); events, settings, compilations,
jobs and calibration epochs are distinct units, so millions of counts within
a few configurations are few drift replicates. Stopping is fixed before
confirmation, or uses a time-uniform confidence sequence
([1810.08240](../notes/papers/1810.08240.md)). A proposed family error budget
of 0.01 splits 0.002 each across simultaneous systematic bounds, cross-device
entanglement, one-direction teleportation, reference preservation and
sequential transfer; it amends no registered analysis.

**Denominators.** A joint record keeps `N_attempt` (optical trials),
`N_detected` and `N_sample` (provider counters under their definitions),
`N_resource`, `N_BSM`, `N_output`, `N_correct` and `T_exposure` apart, and a
missing one is null with its reason. Retained samples, the nominal clock, job
wall time and `physical_perf` never stand in for `N_attempt`. A two-mode
threshold HOM job that keeps only two-click samples carries no visibility
([strategy.md](../notes/quandela/strategy.md)), so overlap of the photons that
actually meet in the Bell analyzer needs coincidence yields against exposure.
`joint_teleportation_scores` in the protocol module refuses a histogram
whose keys lack the Bell pattern beside the receiver outcome (independent
marginals), an unknown basis, bit, pattern or frame, a non-integer count,
and reports no success rate without an attempt count per input that covers
its accepted trials; the test exercises each refusal.

## Output capability

| Level | Demonstrated capability |
|---|---|
| O0 | Terminal characterization by destructive destination detection. |
| O1 | The coherent output enters another quantum operation. |
| O2 | Success information arrives before the operation that depends on it: `tau_available > tau_detection + tau_control + tau_switching + tau_margin`. |
| O3 | A later, independently issued service operation reaches the same persistent state. |

A fixed Clifford operation may act before the frame bits arrive when the
frame propagates through it; only a branch-dependent operation needs fast
feed-forward. A published all-photonic teleportation between two dissimilar quantum-dot
sources used fiber and free-space links, strain and magnetic-field tuning,
synchronization and terminal detection, so its demonstrated output level is
O0 ([2411.12387](../notes/papers/2411.12387.md); the memoryless reading is
inferred from the apparatus the paper describes).

## Work packages

| Package | Status | Home or blocker |
|---|---|---|
| WP00 freeze evidence | Done | This design; pinned replays run on the nightly audit ([ci/AGENTS.md](../../ci/AGENTS.md)). |
| WP01 reconcile summaries | Done | [calibration.md](../notes/quandela/calibration.md), [platform-specifications.md](../notes/quandela/platform-specifications.md). |
| WP02 replay decisions | Covered by gates | The nightly audit replays the retained Ascella and Belenos records against their pinned runtimes. |
| WP03 Ascella outside-block decomposition | Done before this design | [Conformance design](ascella-signed-coherence-conformance.md) and the job-00 README. |
| WP04 Belenos diagnostics | Done for the drift series; predecessor intervention drafted | [bdsc-qualification.md](bdsc-qualification.md), [evidence-closure.md](../runbooks/evidence-closure.md). |
| WP05 observation contract | Waits on the provider answer | [provider_contract.json](../evidence/bdsc/provider_contract.json) rows; request items 2 and 3 are [Perceval issue 798](https://github.com/Quandela/Perceval/issues/798). |
| WP06 physical access | Waits on the provider answer | Request items 1 and 4, through the Quandela contact form. |
| WP07 protocol model | Done | `scripts/qd_network_protocol.py` and its test. |
| WP08 records and analysis | Partly done | Witness, certified classical benchmark and joint-histogram scoring exist; a provider record parser waits on WP05. |
| WP09 to WP16 | Blocked on G1 and G2 | Every step needs a physical joint apparatus and admitted cases. |

The parent plan's scope excludes, until G2 holds, a case generator for
network acquisitions and a live joint-execution adapter: no admissible
network case exists for the first, and Perceval 1.3.1's
`RemoteProcessor.__init__` takes one platform `name`, so a joint job has no
client interface for the second.

## Single-chip rehearsal (job-00)

**Request.** One `qpu:belenos` job, `teleportation_rehearsal/job-00`, confirms that the teleportation circuit works
on one chip. It teleports the six Pauli eigenstates of one dual-rail qubit q through a Bell pair that a
postselected Ralph CNOT (`pcvl.catalog['postprocessed cnot']`, six modes with two vacuum heralds) builds from a in
`|+>` and b in `|0>`. Balanced beam splitters between `q_j` and `a_j` form the partial Bell analyzer
(`analyzer_unitary`), and the receiver b is read in the basis of the input's axis. The Pauli frame of the analyzer
pattern comes from the frame table (patterns 1100 and 0011 give (x, z) = (1, 0); 1001 and 0110 give (1, 1)) and
`decode_bit` applies it in analysis. An event is accepted when it carries exactly three threshold clicks across the
24 returned modes: two on the analyzer in a frame-table pattern, one on b, none on a herald or outside the eight
logical modes. The ideal instrument accepts each input with probability 1/18 (CNOT 1/9 times analyzer 1/2) at
conditional fidelity 1. Generator, analysis and tests live in
[`scripts/qd_teleportation_rehearsal.py`](../../scripts/qd_teleportation_rehearsal.py) and
[its test](../../tests/scripts/test_qd_teleportation_rehearsal.py); the case files are under
[`results/quandela/cases/teleportation_rehearsal/job-00`](../../results/quandela/cases/teleportation_rehearsal/job-00/).

**What it measures, and why simulation cannot answer it.** It measures the pooled conditional fidelity of the
frame-corrected receiver over six inputs on three photons in eight logical modes of the 24-mode chip. The local
Perceval simulation (`NoiseModel` with HOM and g2, plus transmission) fixes the ideal tables and the noise the
budget assumes. It carries neither the chip's multi-photon interference (the HOM figure is a pairwise visibility,
and the three photons of one job come from separate source pulses), nor the service's compilation (the cloud
re-transpiles every iteration and fixes only the occupied columns, [strategy.md](../notes/quandela/strategy.md)
section 2), nor the threshold detectors' per-mode efficiency and dark response. The chip is the question.

**Backend and settings.** `qpu:belenos`, one job of six template iterations in the order +Z, -Z, +X, -X, +Y, -Y.
Every iteration runs the same 24-mode Rx/phase mesh; only the 148 circuit parameters differ. The source photons
enter chip modes 8, 9 and 13 (q0, a0, b0), all in the platform's `connected_input_modes`. The layout is chip modes
(8, 14, 9, 12, 13, 11, 10, 15) for (q0, q1, a0, a1, b0, b1, h0, h1) inside the window 8 to 15, which excludes
mode 5 (21187 /s on the fresh read) and every mode above 100 dark counts per second, and which gives the
closest `t_out` over the three rails among the windows that satisfy those rules. The request is `min_detected_photons`
3, `mitigations: []`, `max_duration` 300 s, `sample_count`. Each iteration carries its own `compilation_seed`, which
`qd_platform.payload` sends per iteration: the six values are indices 0 to 5, in index order, of the ANU QRNG draw
[`draw-2026-10-25T204252Z.json`](../evidence/anu_qrng/draw-2026-10-25T204252Z.json) (42862, 37522, 45230, 47441,
29246, 17743 for +Z, -Z, +X, -X, +Y, -Y), registered in
[`allocations.json`](../evidence/qrng_seeds/allocations.json) as `COMPILATION_SEEDS` of
`scripts/qd_teleportation_rehearsal.py`. The meshes are new, so no reproduction seed applies, and validation requires
exactly those six seeds. The input state holds one photon on each of the three source modes.

**Budget.** The decision count follows `bernoulli_decision_count(alpha 0.01, beta 0.10, F*, B, eps_sys)` with
F* = 0.86, B = 0.6937 and eps_sys = 0.02: 314 accepted outcomes. F* is the lowest pooled conditional fidelity of
three noise variants at the 2026-10-24 15:35 UTC read (HOM 88.8 %, g2 1.1 %, Transmittance 5.5 %): source only
0.882, plus uniform loss 0.863, plus that read's per-mode transmission 0.868 (the per-input fidelities run from
0.79 to 0.99). The fresh read's per-mode transmission changes the pooled value by 0.006. The 0.02 allowance covers
dark clicks (at most 2e-5 per pulse per mode inside the window) and compilation phase error, which no variant
models; the result is its own check of it. The service reports shots equal to samples and no optical trials, so the
classical bound is the larger of `attempts_benchmark` at the reported shots (2/3) and at the modeled attempts, each
input's samples over its modeled three-click probability (0.6937): the retained record has no `N_attempt`, and
this case does not substitute samples for it. At the least accepted share, 0.0799 of the three-click samples,
900 samples per iteration (5400 in all) give 431 expected accepted outcomes, 1.37 times the decision count.
`estimate_required_shots` under the anchor read gives 856,264 to 938,915 shots per iteration, so `max_shots` is
1,200,000 per iteration (7,200,000 in all). The record
[`noise-model.json`](../../results/quandela/cases/teleportation_rehearsal/job-00/noise-model.json) and
[`shot-estimate.json`](../../results/quandela/cases/teleportation_rehearsal/job-00/shot-estimate.json) retain both
derivations, and `--check` re-derives the first.

**Seconds and credits.** The server compiles each iteration for about 10 s (6 iterations, 60 s), and acquiring 5400
samples at the 4.94 MHz clock and the modeled three-click probabilities of 3.3e-5 to 5.0e-5 takes about 30 s, so
the job runs under 100 s; the written case states 120 s against the 300 s limit. Credits follow the measured rule,
1 credit per job plus 1e-06 per billed shot, with the largest iteration's `max_shots` billed
([quandela-credit-optimization.md](../runbooks/quandela-credit-optimization.md)): 1 + 1.2 = 2.2 credits. An
iterated job bills its largest iteration's `max_shots` whatever it returns (`qd_platform.charged`; every retained
iterated `qpu:belenos` job charged 1 + 1e-06 times that budget), so 2.2 credits is the charge, not a ceiling. The
primary 200-credit monthly pool covers it.

**Decision rule and falsifier.** With `F_hat` the pooled conditional fidelity over `n` accepted outcomes and
`r = sqrt(ln(1/0.01)/(2n))`, the analysis (`--analyze RUN`) returns `beats-classical` when
`F_hat - r - 0.02` exceeds the classical bound, `at-or-below-classical` when `F_hat + r` falls below it, and
`inconclusive` otherwise. An input whose samples all fail the acceptance rule keeps its rejection counts and reports
no conditional fidelity; the pooled statistic covers the inputs with accepted events, and the verdict is
`inconclusive`, because the rule pools all six inputs. The falsifier is `F_hat + r < B`: the chip then teleports no
better than a measure-and-prepare strategy at this conformance level. A `beats-classical` verdict establishes C1 for the
family. A fidelity below F* with a margin under the allowance, or a rejected-event mix far from the model (many
herald, outside or pattern rejections), names the model term to revise before any further acquisition. The run also stops before submission unless
a fresh `--plan` admits the request and its model pooled fidelity at the live figures is at least F* = 0.86.

**Claim level.** C1 only: local conformance of the teleportation circuit family on one chip. The case supports no
cross-device claim and no C2 or C3.

**Dry run.** The model fidelity at the live figures decides whether the platform admits the case now. The live read
of 2026-10-25 19:04:53 UTC, retained in `platform-read/catalogue.json`, reports `available`, HOM 83.8 %, g2 16.7 %,
Transmittance 0.05 % and 21187 /s on mode 5; a second read at 20:45:52 UTC returned the same performance figures and
selects the same layout. At 20:47:10 UTC the live `--plan` refused ("Perceval estimates None shots for 5400
samples") with a model pooled fidelity of 0.635, below the classical bound; the record is `plan-refused.json`
(sha256 `c5fbd99089323d84a3a5fdf57145456a05c1c86edb743e02619783fdd5856f01`). `--plan` also retains a refusal and exits
1, without writing `plan.json`, whenever the model pooled fidelity at the live figures falls below F*, even when the
platform admits the request. The same request under the 2026-10-24 15:35:30 UTC performance figures
(`plan-anchor.json`, 20:46:51 UTC, sha256 `95d5043b8a0a422beeb3902413fca593a8fdf27ab6031b5aede459bf1ca98c85`) is
admitted: estimated 5,377,923 shots, credit ceiling 2.2, model pooled fidelity 0.868. Its job body, `job-body.json`
(sha256 `aa3102c6cebb0580d4493c39c568797fccc18333e2f3832d5e5207450fe665f0`, `cases.json` sha256
`ab75a32b06dee0073f476da4b42cc01ce62cbb098e156b35d5a8f33472f5a3e3`), has the digest without `process_id`
`3db7e1a0d519732d03e174b7ff4e14b836f2b8e318274c9dd3ce71a324cc50f7`. The body does not depend on the performance
figures, so a later live plan must reproduce that digest; each later attempt writes `plan-<UTC>.json` or `plan-refused-<UTC>.json` beside the retained records, which keep their bytes. The plan warns that three photons share one block at HOM
88.8 %, below the 90 % rule of [strategy.md](../notes/quandela/strategy.md); the warning does not hold the case.
Nothing was sent.

**Approval.** The owner approved this case in writing on 2026-10-25, for one submission that fires
without a further check-in once a fresh plan admits the request and the model pooled fidelity at the live figures
reaches F* = 0.86. The read of 22:41:26 UTC returned the degraded figures of 19:04 UTC unchanged, so the case
waits on the platform. `qd_teleportation_rehearsal.py --submit RUN APPROVAL` carries both conditions: RUN starts from
copies of the frozen `cases.json` and `circuit.json`, the platform catalogue and raw route answers land in
`RUN/platform-before/`, and `qd_platform.submit` plans afresh under the token's submit lock with `binding` as its
verify step, which refuses a body whose digest without `process_id` departs from `3db7e1a0...` or a model pooled
fidelity below F*. A refusal sends nothing and writes no checkpoint; an admitted request leaves
`RUN/submit-model.json` with the model it was admitted under. `qd_platform.py collect RUN` then retains the result and
`--analyze RUN` returns the verdict.

**Anchor-gate approval.** The `qpu:belenos` performance record held one state from 2026-10-25 18:47 UTC
([calibration.md](../notes/quandela/calibration.md#belenos-read-of-2026-10-25-1904-utc)), so the live gate above cannot
pass until the service publishes a new calibration. On 2026-10-26 the owner approved one submission now under the
anchor gate: `--submit RUN APPROVAL --anchor` plans, estimates shots and evaluates the model under the 2026-10-24
anchor read's performance figures (`anchor_perfs`), where the model pooled fidelity is 0.868, and requires the body
digest above as before. `RUN/platform-before/` keeps the live record, and `submit-model.json` carries the live model
(0.635 at the held figures) beside the admitting one. The decision rule, F*, the sample budget and the claim level
stay as written; the gate guards credits, and a chip in the held state returns an `at-or-below-classical` or
`inconclusive` verdict about itself. The approval covers this one job-00 submission. A later run on a recovered
chip is a new case, job-01, with its own compilation seeds and written case, and a watcher that sees the record
change only reports it.

**Result of job-00.** Job `55479252-d907-45ac-b1e1-84f19d21a131`, submitted 2026-10-26 02:54:50 UTC under the anchor
gate and retained in
[results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00](../../results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/),
completed in 292 s and charged 2.2 credits. Every iteration returned 0 three-click samples and reported its
`max_shots` of 1,200,000. The preregistered verdict is `inconclusive` (no accepted event, so neither the pooled
fidelity nor the bound is defined), and the record-state class is `degraded-as-recorded`: the chip was in the state the
held record describes, and the rehearsal waits for a recovered chip as job-01. Registry claim
`qd-belenos-teleportation-rehearsal-job-00` cites the run; gate `core-teleportation-rehearsal-job-00-replay`
re-derives both analyses.

## Secondary analyses of job-00

`scripts/qd_rehearsal_secondary.py RUN` writes `RUN/secondary-analysis.json`. Its three analyses are fixed here
before the job is sent, and none of them enters the verdict.

**Record state.** The returned three-click samples over the 5400 requested, counting an uncounted iteration of a
partial job as zero, classify the chip: `near-anchor` at a share of 0.5 or more, `degraded-as-recorded` at 0.01 or
less, `intermediate` between. Each iteration stops at its `max_shots` of 1,200,000. Under the anchor figures Perceval
estimates 5,377,923 shots for the 5400 samples, so every iteration returns its 900; under the held figures it finds
no finite estimate (`plan-refused.json`), and the noise model returns about one accepted event per 2e8 detected
shots. No retained run has yet been shot-limited, so the class rests on the documented `max_shots` semantics.

**In-situ fit.** Each returned event falls in one of seven categories: accepted and decoded correctly, accepted and
decoded wrongly, or one of the five rejection reasons of `classify`. A grid of Perceval's noise model (HOM 0.70 to
0.98 in steps of 0.02, g2 0 to 0.24 in steps of 0.02, transmittance scale T from 1e-4 to 1e-1 in quarter decades)
gives each category's probability conditioned on three clicks or more. The multinomial maximum-likelihood cell,
each parameter's interval where its profile log-likelihood lies within 1.92 of the maximum, the deviance against the
saturated model (33 degrees of freedom for six inputs) and the model's pooled fidelity at the best cell are reported
under the anchor read's `t_out` profile (primary) and under the profile of `RUN/platform-before`. A simulated
anchor-state run (`--simulate`) recovers HOM 0.84 (0.82 to 0.92) and g2 0 (0 to 0.02) against the generating
0.888 and 0.011, and leaves T unidentified across the whole grid: without events below three clicks the category
mix carries no absolute loss, which only a shot-limited iteration supplies. The fit needs 100 samples.

**Cayley-Dickson lens (exploratory).** An event whose clicks all lie on the eight logical modes maps to the basis
element `e_i` of the Cayley-Dickson algebra of dimension 2^n, where bit b of i is the click on logical mode b (q0 q1
a0 a1 b0 b1 h0 h1, the little-endian rule of [algebra_circuit_rules.md](../notes/algebra_circuit_rules.md)): n = 6
keeps the events without a herald click, n = 7 adds h0 and n = 8 adds h1. Each input's normalized vector `x_k`, and
the anchor noise model's `y_k`, give the separation `D = sum over input pairs a < b of |x_a x_b - y_a y_b|`, the
product taken under a sign table on the basis `e_i e_j = s(i, j) e_(i xor j)`. The Cayley-Dickson table is
`cd_core.cd_sign`, checked against `cd_core.cd_multiply` on every basis pair. The 999 control tables per dimension
keep its identity, its units squaring to -1 and the anticommutation of distinct units, and draw every other sign
independently from `numpy.random.default_rng(64095)`, index 0 of the ANU QRNG draw `draw-2026-10-26T014202Z`, in
dimension order before any map. The percentile `(1 + #controls with D >= D_CD) / 1000` flags algebra-specific
separation when it is at or below 0.01 in all three dimensions. Controls that drop the anticommutation rank the
Cayley-Dickson table near 1 even on model-consistent data, so the lens tests the algebra beyond its commutation
structure; on the simulated anchor-state run the percentiles are 0.87, 0.40 and 0.48 for n = 6, 7 and 8. A flag
motivates a designed probe that passes the mutation test of the algebra rules and enters no registry from this run.

## Recovered-chip rehearsal (job-01)

**What job-01 measures.** Job-01 runs the rehearsal's six known-input teleportation circuits again on a chip whose
performance record has left the degraded state. Job-00 returned no three-click sample, so it says nothing about the
circuits. Job-01 is a descriptive acquisition. It reports how often an accepted event decodes to the input's
eigenvalue in twelve independently compiled known-input circuits, with an anytime-valid lower confidence bound that
holds under any memory or drift of the chip. Two comparisons with classical bounds follow, each valid only under the
assumptions it names. Job-01 keeps job-00's inputs, readout bases, eligibility rule, `min_detected_photons` 3,
`mitigations: []`, `max_duration` 300 s and `sample_count`.

**Why the record admits no applicable classical bound.** The Codex research consult
([report](../archive/reviews/2026-10-26-belenos-job-01-redesign-consult.md)), the operator's research, and the source
notes of the ten registered papers settle three obstructions on this service contract:
- **The input is visible to the device.** Each input's preparation, Ralph CNOT, analyzer and receiver rotation
  compile into one mesh per iteration, so a classical operation indexed by the circuit can prepare the expected
  output and score 1. Iteration order, randomized or not, does not hide the input. The six-state benchmark assumes
  one label-blind instrument, the "same quality for all bases" assumption that [Ma et al.](../notes/papers/1210.1282.md)
  state. The martingale analyses also require each trial's input to be randomized and unknown to the null
  ([Gill](../notes/papers/quant-ph-0301059.md), [Zhang, Glancy and Knill](../notes/papers/1108.2468.md),
  [Bierhorst](../notes/papers/1312.2999.md), whose Appendix 1 shows a fixed-configuration block failing).
- **Extra input copies.** Under free postselection, the six-state classical value is the largest accepted
  photon-number sector's value, 2/3, 3/4 and 5/6 at one, two and three copies
  ([Chiribella and Xie](../notes/papers/1301.1170.md)). An efficiency constraint restores a weighted value
  ([Specht et al.](../notes/papers/1103.1528.md), [Gündoğan et al.](../notes/papers/1201.4149.md)). The service
  reports no optical attempts, and the model's acceptance per attempt, about 3e-6, lies far below the source's
  two-copy probability of 0.0056 per attempt. So a classical device may accept two-copy attempts only, and the
  bound is at least 3/4.
- **The attempt profile is unknown.** B at the modeled attempts (0.6937 for job-00) is a forecast. Equal returned
  samples are compatible with attempt profiles that raise the bound, and `physical_perf` moves with the requested
  budget ([strategy.md](../notes/quandela/strategy.md)), so no record field measures attempts.

The accepted multiphoton share is 2.0 % in the source-only model and 7.8 % under the anchor read's per-mode
transmission; the review's earlier 1.4 to 2.5 % used HOM 1.0. A `beats-classical` verdict, and C1 conformance, are
not available for job-01.

**Preregistration at its own read.** On 2026-10-26 the owner chose to preregister job-01 at its own platform read:
the first read after the record recovers, retained as
`results/quandela/cases/teleportation_rehearsal/job-01/platform-read/catalogue.json`, is both the case's fresh read
and its anchor read. The layout, the model forecasts, the attempt-box bound and the sample probabilities come from
that read, and `estimate_required_shots` under its perfs sizes `max_shots`.

The submission gate `binding` admits the case while the live performance record keeps what the frozen budget
depends on: no mode of the case's layout reads a dark rate above `DARK_LIMIT`, and the larger of `expected_seconds` at
the live clock and per-input sample probabilities and the iterations at `ITERATION_SECONDS` (27.3 s, the rate job-01
showed by running 11 iterations in the 300 s limit) stays within `MAX_DURATION`; a twelve-iteration job therefore
refuses. The anytime-valid lower bound holds at any
accepted count, so the pooled fidelity at the live figures decides nothing, and a refresh of the performance figures
leaves the case valid while it keeps both conditions. The first rule of this section compared the sha256 of the
canonical perfs object; two reads 69 minutes apart on 2026-10-30 differed, so that equality refused every submission
that followed an approval round-trip. The record most likely describes the last published calibration rather than
the chip ([calibration.md](../notes/quandela/calibration.md)), and the gate holds at read time only: `qd_platform.submit` POSTs after the last authenticated read, and no
provider precondition binds that read to execution. `--anchor` refuses a case anchored at its own read. The record
watch keeps triggering on job-00's F* = 0.86; it decides when to read.

**Iterations and blocks.** Twelve template iterations, two blocks of the six inputs:
- block A runs +Z, -Z, +X, -X, +Y, -Y, and block B runs the mirrored order -Y, +Y, -X, +X, -Z, +Z, which balances
  a linear drift across inputs without a randomizer;
- each iteration carries its own compilation seed, so a block contrast mixes time with recompilation;
- the analysis binds a result iteration to its setting by `circuit_params` and `compilation_seed` together.

The preregistered budget is 1200 samples per iteration (14,400 in all). At job-00's modeled probabilities that
expects about 1150 accepted outcomes at the least accepted share, and 240 s by job-00's seconds model: 10 s of
compilation per iteration, plus samples over the 4.94 MHz clock times the modeled three-click probability, times
1.25, rounded up to whole minutes. `--prepare` refuses a read whose expected seconds exceed the 300 s `max_duration`,
or for which Perceval estimates no shots. It retains nothing then, because a job the service cuts off bills its
`max_shots`. The seconds model is unverified on the chip: job-00, predicted under 100 s, ran 292 s in the degraded
state with every iteration at its `max_shots`.

**Compilation seeds.** Block A takes 8608, 30481, 4339, 55973, 12504 and 37710 for +Z, -Z, +X, -X, +Y, -Y: indices 0
to 5 of the Cisco Outshift QRNG draw
[`draw-2026-10-26T204106Z.json`](../evidence/outshift_qrng/draw-2026-10-26T204106Z.json). On 2026-10-26 the
operator observed the keyed ANU service answer `success` with an empty data array and the keyless service time out
twice; neither failure was retained as a receipt. Block B takes 5573, 39099, 45322, 55527, 43939 and 10803 for -Y,
+Y, -X, +X, -Z, +Z, in block order: indices 0 to 5 of the keyed ANU draw
[`draw-2026-10-26T230602Z.json`](../evidence/anu_qrng/draw-2026-10-26T230602Z.json). Both appear in
[`allocations.json`](../evidence/qrng_seeds/allocations.json) as `JOB_01_COMPILATION_SEEDS` of
`scripts/qd_teleportation_rehearsal.py`, and none repeats a job-00 seed.

**Analysis (`--analyze RUN`, schema `qd-teleportation-analysis-v2`).**
- **Descriptive record.** For every block and input: accepted and correct counts, every rejection category,
  returned samples, acceptance per returned sample, and the provider fields `nb_shots_used` and `physical_perf`. No
  field is read as optical attempts. The pooled accepted-event correctness `F_hat` covers all twelve iterations.
- **Anytime-valid lower bound.** With alpha 0.01, the planned accepted count `n*` (the model's expected accepted
  outcomes at the read) and `lambda = sqrt(8 ln(1/alpha) / n*)` fixed before acquisition, the capital
  `prod_j exp(lambda (X_j - mu_j) - lambda^2 / 8)` over accepted events is a nonnegative supermartingale for any
  conditional means `mu_j`, by Hoeffding's lemma and Ville's inequality ([Howard et al.](../notes/papers/1810.08240.md),
  Sec. 2). So `L = F_hat - lambda / 8 - ln(1/alpha) / (lambda n)` lower-bounds the average conditional correctness
  of the n accepted events, at whatever count the run ends, under any memory or drift. At `n = n*` it equals the
  Hoeffding radius. Rejected events leave the capital unchanged.
- **Block homogeneity.** For each input, a chi-square test of block against outcome category (correct, wrong and the
  five rejections, empty categories dropped) at alpha 0.01 / 6. A rejection sets the flag `blocks-differ`, which
  vetoes both comparisons; a pass establishes neither stationarity nor independence.
- **Model-conditional comparisons.** Each reports `L - B` and a label, `exceeds-under-assumptions` when `L > B`;
  neither subtracts an allowance, since the data are the realized circuits' correctness:
  - **(a) two-copy bound, B = 3/4:** one label-blind instrument; equal optical attempts per input, since unequal
    priors raise the six-state value (to 0.6937 already for single copies at job-00's modeled profile); a source with
    at most two input copies per attempt, Perceval's truncated model; free photon-number-dependent postselection. A
    three-copy tail raises the bound to 5/6.
  - **(b) attempt-box bound, B = B_box(1.1):** one label-blind instrument; single-copy inputs (photon-number-blind
    acceptance); each input's attempts within a factor 1.1 of the modeled profile. The maximum over the box lies at
    one of its 64 vertices, because for a fixed instrument the pooled score is a linear-fractional function of the
    attempts, and the maximum over instruments of such functions is quasi-convex. The record also reports the
    break-even ratio `r_BE`, the largest factor at which `L` still exceeds the box bound.
- **Partial jobs.** An errored or canceled job keeps every count descriptive, and it reports no comparison label.

**Derived at the read.** `qd_teleportation_rehearsal.py --prepare job-01` writes:
- `noise-model.json`, holding the five noise variants, the accepted shares, `n*`, `lambda`, B_box(1.1), the model's
  forecast of `F_hat` and the forecast of `L` at `n*`;
- `shot-estimate.json`, holding `max_shots` at 1.25 times the largest per-iteration estimate, rounded up to 100,000;
- the printed `REQUESTS` and `JOBS` rows, together with the forecast against each comparison.

The charge is 1 + `max_shots` * 1e-06 credits.

**Procedure.** Each step reads the platform and sends no job until the owner approves the written case.
1. `"$PYTHON" scripts/qd_platform.py snapshot --out results/quandela/cases/teleportation_rehearsal/job-01/platform-read`
   retains the read.
2. `"$PYTHON" scripts/qd_teleportation_rehearsal.py --prepare job-01` retains the derivation and the estimate. Its
   two printed rows go below `JOBS` in the script.
3. `"$PYTHON" scripts/qd_teleportation_rehearsal.py job-01` writes `cases.json` and `circuit.json`, and `--check`
   validates every registered case.
4. `--body job-01` freezes `job-body.json`, and `--plan job-01` retains `plan.json` or `plan-refused.json`.
5. A written-case paragraph below states:
   - what the run measures and the claim it supports;
   - the backend `qpu:belenos`;
   - the samples, `max_shots`, seconds and credits.
6. After the owner approves, `--submit RUN APPROVAL` sends job-01 once. `qd_platform.py collect RUN`,
   `--analyze RUN` and `qd_rehearsal_secondary.py RUN` follow, and retention mirrors job-00.

**Review of 2026-10-26.** An owner-requested Codex deep peer review
([report and disposition](../archive/reviews/2026-10-26-belenos-teleportation-rehearsal-review.md)) changed the shared
analysis before job-01's preregistration:
- a partial job (errored or canceled) is `inconclusive` even when every input has counts, because a stop the service
  chose may depend on the outcomes;
- `at-or-below-classical` requires `F_hat + r` below the *smaller* of the two candidate bounds (the bound at the
  reported shots, 2/3 at equal shots, and the bound at the modeled attempts), so neither verdict direction rests on
  the attempt profile that favors it;
- `--check` refuses a registered job whose case is absent.

Job-00's retained verdict (`inconclusive`, no accepted event) replays unchanged. F* is the noise model's power
forecast: it sizes the budget and never enters the verdict, which compares the data with B.

The review also named the open questions below. The owner chose a redesign on 2026-10-26, and the job-01 section
above records how each was settled:
- **The verdict supports a narrower claim than C1.** It establishes accepted-event pooled conditional fidelity above
  the bound; the acceptance rate and the rejection mix are reported, but no preregistered tolerance tests them.
- **Multiphoton sectors leave the single-copy benchmark.** Threshold-accepted multiphoton events (2.0 % of accepted
  mass at g2 1.1 % with ideal detection and 7.8 % under per-mode transmission; the 1.4 to 2.5 % first stated here
  used HOM 1.0) carry extra input copies or failed CNOT branches, outside the single-copy Choi-cone
  benchmark; no registered bound covers them.
- **The modeled attempts are a forecast, not an upper bound.** The service reports no optical attempts
  ([Perceval #798](https://github.com/Quandela/Perceval/issues/798)), so B at the modeled attempts does not
  upper-bound the classical optimum over the attempt profiles the record allows.
- **Independence is assumed.** The Hoeffding radius treats accepted events as independent, while each input runs as
  one compiled block.
- **The allowance is stated, not derived.** The 0.02 allowance is not a derived bound on compilation error or
  three-photon distinguishability.

## Split recovered-chip rehearsal (job-02 and job-03)

Job-01 ran 11 of its 12 iterations before the service canceled it at the 300 s `max_duration`; it billed its
4.2-credit ceiling and left block B's +Z iteration without counts. Most of its time was acquisition. The one-photon
Belenos jobs of 2026-10-21 to 2026-10-24 (BDSC qualification, diagnostic, stationarity and drift series) took 165 to
176 s for 24 iterations of about 100,000 detection events (`nb_shots_used`) each, which bounds the fixed cost of an
iteration at 6.9 s. Job-01's 11 iterations used 24.9 million detection events in 318 s, so at least 242 s of it, 76 %,
scales with detection events: at most 12.8 microseconds per event, about 9.7 once the fixed-cost bound is
subtracted. A three-photon iteration's time therefore grows with its samples, and a job's with its iterations times
its samples. Six iterations at job-01's 2.3 million mean events take about 176 s; six that each run to the 3,000,000
`max_shots` take at most 6 x (6.9 + 38.4) = 272 s, inside the 300 s limit. The service reports no per-iteration time,
so the split rests on these bounds rather than a measured per-iteration profile.

job-02 and job-03 run job-01's two-block descriptive design as two jobs of six iterations
(`CASE_HALVES` in `scripts/qd_teleportation_rehearsal.py`): job-02 runs block A (+Z, -Z, +X, -X, +Y, -Y) and job-03
block B in mirrored order (-Y, +Y, -X, +X, -Z, +Z). Both take job-02's platform read
(`results/quandela/cases/teleportation_rehearsal/job-02/platform-read/catalogue.json`, `SHARED_READ`), so they carry
one layout (q0 q1 a0 a1 b0 b1 h0 h1 on chip modes 18 19 20 17 22 23 16 21) and one preregistration: the planned
count `n*` = 1506 and `lambda` cover both blocks, 1200 samples per iteration. The analysis is the job-01 analysis of
the joined pair: `--analyze-pair RUN_A RUN_B` binds both runs' iterations to the two blocks by `circuit_params` and
`compilation_seed`, writes `pair-analysis.json` into RUN_B, and refuses a pair whose shared manifest fields or
preregistration differ. The block homogeneity test now also compares the two jobs in time, so a drift between them
vetoes both comparisons. `--analyze` of one half alone reports counts and its lower bound and evaluates no
comparison, since its homogeneity test has no second block.

The written seconds of a case registered after job-01 are the larger of the seconds model and the job's iterations
times `ITERATION_SECONDS`, in whole minutes (`written_seconds`): 180 s for six iterations. `ITERATION_SECONDS` holds
at job-01's samples per iteration only, since an iteration's time scales with its detection events.

**Compilation seeds.** job-02 takes 19918, 52848, 30689, 50293, 57001 and 12608 for +Z, -Z, +X, -X, +Y, -Y (indices 0
to 5) and job-03 takes 56057, 55550, 595, 59482, 7821 and 19846 for -Y, +Y, -X, +X, -Z, +Z (indices 6 to 11) of the
ANU QRNG draw [`draw-2026-10-30T205347Z.json`](../evidence/anu_qrng/draw-2026-10-30T205347Z.json), registered in
[`allocations.json`](../evidence/qrng_seeds/allocations.json) as `JOB_02_COMPILATION_SEEDS` and
`JOB_03_COMPILATION_SEEDS`.

**Written case.**
- *What it measures.* The accepted-event teleportation correctness of the six Pauli inputs across both blocks, with
  its anytime-valid lower bound and the two labeled comparisons, on a complete two-block acquisition: job-01 could not
  supply one, because its cut removed a block B iteration. A complete pair also tests the shortfall job-01 showed:
  its model at the reported HOM 0.871 forecast 0.841 and it measured 0.802 over 1262 accepted events, which the
  model reaches only at an effective two-photon indistinguishability near 0.81.
- *Why a simulation cannot answer it.* The question is the chip's realized correctness under its compiled meshes,
  source and detectors; the local model at the read forecasts 0.848 (lower bound 0.809 at `n*`) and is the
  comparison, not the measurement.
- *Backend and budget.* `qpu:belenos`, two jobs submitted one after the other, each six iterations of 1200 samples,
  `max_shots` 3,000,000 per iteration (1.25 times Perceval's largest estimate, 2,365,123), 180 s written seconds
  under the 300 s limit, credit ceiling 4.0 per job (1 + 3,000,000 x 1e-06), 8.0 credits for the pair. Job-01's
  observed 2.0 to 2.7 million detection events per iteration sit below the per-iteration budget.
- *Gate.* `--submit RUN APPROVAL` admits each job while no layout mode reads a dark rate above `DARK_LIMIT` and the
  floored seconds stay within `MAX_DURATION` at the live record. The plan warns that HOM 87.9 % sits at or below the
  90 % of strategy.md design rule 1; that rule warns and does not hold a case.

**Outcome: the block veto measures per-seed compiled meshes.** Both halves and an exact replay of job-02 ran on
2026-10-31 at HOM 87.9 %, g2 1.4 %, transmittance 5.37 % (claim `qd-belenos-teleportation-split-blocks-mesh-error` in
[research_state.json](../state/research_state.json)).

| Run | Job | Submitted (UTC) | Correct / accepted | Correctness | Lower bound |
|---|---|---|---|---|---|
| job-02, block A | f918c870 | 03:58:45 | 727 / 887 | 0.820 | 0.767 |
| job-03, block B | e7f527ce | 04:04:38 | 768 / 929 | 0.827 | 0.776 |
| job-02 replay, block A | 137c771c | 04:27:33 | 690 / 836 | 0.825 | 0.771 |

- The pair (`pair-analysis.json` in the job-03 run) reads 0.823 over 1816 accepted events with lower bound 0.787. The
  homogeneity veto flags +Z (p 1.3e-5) and -Z (p 4.0e-9), so the two-copy (margin +0.037) and attempt-box (+0.082)
  comparisons stay vetoed.
- The replay (`--analyze-replay`, `replay-analysis.json` in the replay run) carries job-02's circuit parameters and
  seeds. The service returned the same `computed_circuit` for all six settings, and every input agrees with job-02
  (p 0.079 to 0.985) 29 minutes later. Fixed meshes therefore reproduce, and the A-B difference follows the
  different seeds of the two blocks.
- The in-situ visibility case ([belenos-associator-visibility-case.md](belenos-associator-visibility-case.md)) ran one
  identical four-mode circuit under four seeds on chip modes 18 to 21 and 20 to 23: the two-click endpoint spread by
  0.23 and 0.39 between seeds, a chi-square of 241 and 382 on 3 degrees of freedom. Per-seed mesh error on this chip is
  large against binomial error.
- Acceptance per sample ranges from 0.08 to 0.24 across settings, mostly through herald clicks, so a mesh moves the
  accepted set as well as its correctness.

A two-block design on Belenos whose veto is meant to test time gives both blocks the same seeds, so the blocks differ
only in when they run; a design that pools independently compiled meshes treats the mesh as a random effect and
carries its spread in the interval instead of a binomial error.

The mode-swap case (claim `qd-belenos-mode-swap-per-seed-mesh-variance`) since established that per-seed mesh error
dominates drift and chip position on this chip and that a seed reproduces its mesh across jobs
([strategy.md](../notes/quandela/strategy.md) section 2). The pooled 0.823 is therefore an average over the meshes the
twelve seeds drew, and a selected mesh per input can read higher, which a case that screens seeds and replays
the best tests.

## Provider request

The request splits by channel. Items 2 and 3 concern the open-source client's
result contract and went to Quandela on 2026-10-25 at 18:33 UTC as
[Quandela/Perceval issue 798](https://github.com/Quandela/Perceval/issues/798),
with the papers, Perceval sources and retained measurements behind each
question cited inline. Items 1 and 4 concern the installations and go through
the Quandela contact form under the Research Collaboration subject, which the
owner submits under their own name; the plan record dates that submission.
Each answer enters this design dated, with the platform and version it
covers.

Identify whether the physical installations exposed as `qpu:ascella` and
`qpu:belenos` support one coordinated experiment with coherent optical routing
or a shared entangled resource before terminal detection. For each item,
state supported, unsupported or unresolved, with the platform, access route,
date and software version it applies to:

1. Apparatus: the installations behind both names, their locations, the
   quantum path between them, external injection and detector bypass ports,
   encoding at each boundary, any common entangled source or two-source
   interference station, source wavelength, bandwidth and pulse schedule, and
   overlap of the photons that would meet in a Bell analyzer.
2. Execution identity: what `computed_circuit` and `computed_experiment`
   describe, the evidence binding them to applied controls, configuration
   transition semantics, independent control of preparation and analyzer,
   worker, firmware and calibration identity per acquisition, and diagnostics
   that separate stale applied settings from result association.
3. Observation: definitions of every shot, sample, event and exposure
   counter; whether counts aggregate detector events directly; any thinning,
   resampling or probability-to-count conversion; the effect of
   `mitigations=[]`; per-channel threshold or quasi-number-resolving response,
   efficiency, background, dead time and jitter; coincidence logic; joint
   counts or trial identifiers; and an attempt denominator.
4. Output and control: survival of the receiver output past Bell detection,
   delay, switching and downstream operations, feed-forward latency and
   jitter, frame-tracking support, joint reservation, and abort and
   ambiguous-submission semantics.

A roadmap answer stays development evidence; an answer naming an accessible
apparatus, route and data contract enters G2.

## Draft network case record

A future case record carries `schema: qd-network-case-v1`, `status: draft`
and `admission: blocked` until G2, and keeps every unknown field null: the
joint platform id, physical route evidence, resource-factory and
Bell-instrument evidence, joint record contract, attempt-denominator
contract, effective processing contract, calibration bundle, benchmark
certificate, statistical case, job, second and credit ceilings, approval
record and payload digest. Its fixed fields are the protocol
(`teleportation_A_to_B`), claim level, the two local platforms, the uniform
six-state ensemble, output axes X, Y and Z, 18 base setting cells, the
`X^x Z^z` frame convention and output level O0. The scientific case record
stays separate from the provider payload.
