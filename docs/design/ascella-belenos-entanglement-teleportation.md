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
map or interconnect; the March 2026 roadmap targets scaling through modular,
high-speed optical networking in 2028-2029 and names no Ascella or Belenos
link ([roadmap note](../notes/quandela/roadmap-2026-03.md)), which makes it
development context, not access.

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
synchronization and terminal detection, with no stationary memory
([2411.12387](../notes/papers/2411.12387.md)).

## Work packages

| Package | Status | Home or blocker |
|---|---|---|
| WP00 freeze evidence | Done | This design; pinned replays run on the nightly audit ([ci/AGENTS.md](../../ci/AGENTS.md)). |
| WP01 reconcile summaries | Done | [calibration.md](../notes/quandela/calibration.md), [platform-specifications.md](../notes/quandela/platform-specifications.md). |
| WP02 replay decisions | Covered by gates | The nightly audit replays the retained Ascella and Belenos records against their pinned runtimes. |
| WP03 Ascella outside-block decomposition | Done before this design | [Conformance design](ascella-signed-coherence-conformance.md) and the job-00 README. |
| WP04 Belenos diagnostics | Done for the drift series; predecessor intervention drafted | [bdsc-qualification.md](bdsc-qualification.md), [evidence-closure.md](../runbooks/evidence-closure.md). |
| WP05 observation contract | Blocked on provider answers | [provider_contract.json](../evidence/bdsc/provider_contract.json) rows and the request below. |
| WP06 physical access | Blocked on provider answers | Request below; sending it is the owner's decision. |
| WP07 protocol model | Done | `scripts/qd_network_protocol.py` and its test. |
| WP08 records and analysis | Partly done | Witness, certified classical benchmark and joint-histogram scoring exist; a provider record parser waits on WP05. |
| WP09 to WP16 | Blocked on G1 and G2 | Every step needs a physical joint apparatus and admitted cases. |

The parent plan's scope excludes, until G2 holds, a case generator for
network acquisitions and a live joint-execution adapter: no admissible
network case exists for the first, and Perceval 1.3.1's
`RemoteProcessor.__init__` takes one platform `name`, so a joint job has no
client interface for the second.

## Provider request (unsent)

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
