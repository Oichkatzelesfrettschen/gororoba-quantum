# Heron r2 readout resonator: public evidence for ibm_fez, ibm_kingston and ibm_marrakesh

Read date: 2026-10-16 to 2026-10-17. All fetches were read-only. Quotes are
verbatim from the fetched text, shortened with "..." where marked.

## Verdict

The sources read for this note state no readout-resonator linewidth,
dispersive shift, resonator frequency, ring-down time or residual-photon
dephasing for ibm_fez, ibm_kingston, ibm_marrakesh or any other Heron r2
device. The only Heron r2 readout numbers found are instruction durations and
errors (this repository's live Target snapshot and IBM's backend pages).
Measured kappa and chi exist in the open literature for three non-Heron-r2
IBM devices, all context: an IBM-internal flux-tunable test device of
unstated family (Thorbeck et al., section 4a) and ibm_brisbane and ibm_kyoto
(Chatterjee et al., section 4g; 127-qubit devices whose family and revision
the paper does not state, Eagle-class per section 4d and by inference). "None found" bounds the
search performed here (section "Not run" lists the gaps); it is not a claim
about every public source.

## Provenance rule

Every source and every number below carries a `Provenance:` label or a tag
naming the processor it comes from. Only values tagged Heron r2 apply to
ibm_fez, ibm_kingston and ibm_marrakesh. A value tagged with another family,
another revision, an unstated revision or "generic" is context: it bounds
what to expect and never stands in for a Heron r2 parameter. Provenance
strings take the form "family and revision (device), source and version,
location in source".

## Scope and tags

Ordering follows the coordinator's rule: (1) sources naming ibm_fez,
ibm_kingston or ibm_marrakesh, (2) other named Heron r2 devices, (3)
revision-only Heron r2 statements, (4) everything else as context only.
Tags used below:

- DEVICE-MATCHED: names one of the three account devices.
- HERON-R2-OTHER: names a different Heron r2 device.
- R2-REVISION-ONLY: says "Heron r2" with no device.
- HERON-REV-UNSTATED: says "Heron" or names a device with no revision.
- OTHER-FAMILY: Eagle, Falcon, internal test device, non-IBM.
- INFERENCE: mine.

Every tag below is a provenance label; a bare value without one does not
appear in this note.

Account devices (live API, 2026-10-17, supplied by the coordinator):
ibm_fez backend_version 1.3.37, online 2024-05-14; ibm_kingston 1.0.0, online
2025-02-20; ibm_marrakesh 1.0.21, online 2024-08-07; all processor_type
{'family': 'Heron', 'revision': '2'}. The retained snapshot
docs/evidence/heron_platform/targets.json (retrieved 2026-10-14T21:00:38+00:00,
qiskit 2.5.2, qiskit-ibm-runtime 0.50.0) records the same processor_type for
all three.

Revision resolution (IBM processor-types page,
https://quantum.cloud.ibm.com/docs/en/guides/processor-types, read 2026-10-16
via the repository's transcription docs/notes/ibm_quantum/processor-types.md;
no "last updated" date shown): "`r3` (July 2025) Heron r3 is the result of
targeted manufacturing improvements that directly impact coherence, gate
fidelity, and readout performance." / "`r2` (July 2024) This is a revision of
the original Heron processor. The chip has been redesigned to include 156
qubits in a heavy-hexagonal lattice." / "`r1` (December 2023) The first
version of Heron with 133 qubits." The page makes no statement about readout
resonators for any revision.

## 1. Device-matched evidence (ibm_fez, ibm_kingston, ibm_marrakesh)

### 1a. Live Target values (this repository; stated by the backend)

Provenance: Heron r2 (ibm_fez, ibm_kingston, ibm_marrakesh), live Target.
Source: docs/evidence/heron_platform/targets.json and
docs/notes/ibm_heron_platform.md (medians over 156 qubits, ns), live API read
2026-10-14 (snapshot) and 2026-10-17 (coordinator re-read). Tag:
DEVICE-MATCHED, backend versions as listed above.

| Instruction | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---|---|---|
| `measure` duration (readout_length) | 1660 | 2180 | 2684 |
| `measure_2` duration | 1340 | 1380 | 1884 |
| `measure_reset` = `reset` duration | 1684 | 2212 | 2720 |
| `measure_reset_2` = `reset_2` duration | 1364 | 1412 | 1920 |

The coordinator's 2026-10-17 read reports the same `measure` and `measure_2`
values, uniform per chip, and meas_map as one group of all 156 qubits.
Definition, from https://quantum.cloud.ibm.com/docs/en/guides/qpu-information
(no version date shown, read 2026-10-16): "The readout length specifies the
duration of the readout operation for a qubit." and "It measures the time from
the initiation of the measurement pulse to the completion of signal
digitization," and the page's example `backend.target["measure"][(0,)]`
returns `InstructionProperties(duration=1.66e-06, error=0.0126953125)` (its
example matches the ibm_fez value above; the page does not name the backend,
so that match is INFERENCE).

Consequence: the stated durations include pulse plus digitization. They do not
split into pulse, integration window and ring-down. That split is not public.

### 1b. ibm_fez: MCMit, TUM (arXiv:2604.25863)

- Provenance: Heron r2 (ibm_fez) for the experiments; the Heron-wide range
  below is Heron, revision unstated.
- Version: v3, 7 Aug 2026 (header "arXiv:2604.25863v3 [quant-ph] 7 Aug 2026").
  Earlier versions exist; v1 date not retrieved. The paper gives no
  execution date, backend version or calibration date for its ibm_fez runs,
  only "Each experiment runs for 10,000 shots on the same calibration cycle of
  ibm_fez." The experiment date is unknown, so the data cannot be ordered
  against the ibm_fez backend_version read on 2026-10-17.
- Device tag: DEVICE-MATCHED (ibm_fez), text: "we conduct experiments
  requiring quantum hardware on ibm_fez, an IBM Heron r2 QPU [12]."
- Relevance: the paper runs micro-benchmarks and MCM error mitigation on
  ibm_fez. It states no kappa, chi, ring-down or residual-photon value for
  ibm_fez. It states that "IBM does not give public access to readout traces",
  so it uses traces from a non-IBM 5-qubit device (Lienhard et al.,
  bare resonator frequencies "7 GHz", T1 12-41 us, 500 MSamples/s, 1 us
  traces). Those traces are OTHER-FAMILY context and say nothing about Heron.
- Heron-wide readout-length statement (section II-A "Readout latency", tag
  HERON-REV-UNSTATED, citing IBM compute resources page, accessed
  2025-08-20): "measurements are also the slowest operation, taking
  approximately 20-40x longer than a two-qubit gate on IBM Heron processors
  [12]. Concretely, readout length spans 1560-2584ns, while a two-qubit gate
  only spans 68-88ns." This range is a fleet range across revisions on that
  date; the 2026 snapshot values above (1660-2684 ns medians) sit inside or
  just above its upper end.
- Feedback latency (section II-A): "IBM reports a 500ns feedback latency in
  their DQC experiment (20-30% of measurement duration) [18]." Reference [18]
  as printed is Foss-Feig et al.; the device and revision of that IBM claim
  are not stated in the sentence. HERON-REV-UNSTATED, not usable for our
  devices.

### 1c. ibm_kingston: Shirgure et al. (arXiv:2604.03360)

- Provenance: Heron r2 (ibm_kingston), arXiv:2604.03360v2.
- Version: v2, 15 Sep 2026 (header "arXiv:2604.03360v2 [quant-ph] 15 Sep
  2026"; v1 date not retrieved). Backend version and calibration date not
  given.
- Device tag: DEVICE-MATCHED (ibm_kingston), "IBM Kingston (Heron r2)".
- Section I-A: "on IBM Kingston, the median (final) measurement errors are
  five times higher than two-qubit gate errors, with measurement durations
  that are 34 times longer. IBM recently introduced a new MCM feature
  achieving a 65% reduction in measurement duration compared to the final
  measurement, though at an error rate ten times that of two-qubit gates.
  Beyond measurement latency, feed-forward operations incur additional
  classical communication latency of approximately 600 ns on IBM hardware."
  Check against the snapshot: ibm_kingston `measure` 2180 ns / cz 68 ns = 32,
  `measure_2` 1380 / 2180 = 0.63 (a 37 percent reduction, not 65 percent).
  The paper's 34x and 65 percent differ from the 2026-10-14 snapshot, which
  is consistent with a different backend version or calibration date;
  INFERENCE.
- The "approximately 600 ns" feed-forward latency is stated for "IBM
  hardware" without device or revision. HERON-REV-UNSTATED; not a
  device-matched value.
- "MCMs can also introduce errors on unmeasured spectator qubits through
  measurement-induced dephasing [36]." Qualitative, no number.

### 1d. ibm_kingston: Chu et al. (arXiv:2606.00433)

- Provenance: Heron r2 (ibm_kingston); Heron r3 (ibm_pittsburgh,
  ibm_boston) are context.
- Authors include Bibek Pokharel and Alireza Seif (IBM Quantum affiliation
  not confirmed from the extracted text; first-page affiliation numbers 1, 2, 3
  not resolved). Versions: v1 29 May 2026; v2 30 Sep 2026 (accepted
  manuscript for Physical Review Letters per the arXiv listing). The PDF reads
  "arXiv:2606.00433v2 [quant-ph] 30 Sep 2026".
- Device tags: ibm_kingston DEVICE-MATCHED ("ibm_kingston (Heron r2)",
  Supplemental S7.1); ibm_pittsburgh and ibm_boston are Heron r3 and are
  context.
- Content: 20 selected qubits per device; MCM instrument learned from three
  repeated measurements. Main text Fig. 2 caption: "For all 3 devices, we see
  the decay rates eta_down (1 -> 0) exceed excitation rates eta_up (0 -> 1) by
  one to two orders of magnitude, consistent with spontaneous-emission
  (T1)-dominated physics." Supplement S7.1: "For every job, we record the
  backend revision, submission and completion times, software versions" and
  the jobs were transpiled with basis {SX, RZ, X, measure} (the plain
  `measure`, not `measure_2`, per that listing).
- Result relevant to residual photons: the post-measurement state update is
  dominated by T1 decay. The text extraction contains no photon number, kappa,
  chi, ring-down time or phase shift. The backend revision string is recorded
  by the authors but not printed in the text I extracted.

### 1e. Not found for ibm_marrakesh

No paper or IBM page found that measures readout on ibm_marrakesh. IBM's
changelog (below) lists it only as an Open Plan addition.

### 1f. IBM changelog entries naming the three devices

Source: https://quantum.cloud.ibm.com/docs/en/guides/latest-updates, read
2026-10-16, undated page version (entries dated by month).

- "10 April 2025": "Launched two new QPUs: ibm_aachen (eu-de region) and
  ibm_kingston (us-east region)"; "9 April 2025": "Two new 156Q Heron R2 QPUs"
  and "ibm_kingston, located in the US region". Note the account's API
  reports ibm_kingston online 2025-02-20, so the public launch postdates the
  backend's first online date by about seven weeks; INFERENCE that the earlier
  date is a restricted-access period.
- "October 2025": "The IBM Quantum fleet welcomes ibm_fez and ibm_marrakesh to
  the Open Plan!" (available as of 27 October).
- "April 2026": "The Heron r2 ibm_kingston--one of our highest-performing
  quantum computers".
- "2 February 2025": "Improvement in mid-circuit measurement" and a "gradual
  rollout of new features to dynamic circuits" (no device named).
- "5 June 2025": "Early access to the new version of dynamic circuits on
  select QPUs"; "October 2025": "The new dynamic circuits is now available to
  all users on all backends".
- No entry mentions `measure_2`, `MidCircuitMeasure` or "backend version" by
  name (the fetched summary reported none; the page was read once, not
  searched textually).

### 1g. backend_version history: not public

No public IBM release notes or changelog found that tie `backend_version`
values (1.3.37, 1.0.0, 1.0.21) to readout or other calibration changes. The
qiskit-ibm-runtime client release notes
(https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/release-notes,
read 2026-10-16; versions through 0.50.0 dated 2026-09-24) do not contain
"backend_version", "readout" or "hamiltonian" (read for 0.50.0 down to 0.33.1;
the page was truncated after 0.29.0). Client-side entries that matter:

- 0.43 (2025-10-14): "Introduces the `MidCircuitMeasure` class", default name
  `measure_2`; `convert_to_target()` reads an `instruction_signatures` field
  from backend configuration files.
- 0.44.0 (2025-12-16): `ConvertMidCircMeas` pass, default `measure_2`.
- 0.49.0 (2026-08-10): mid-circuit reset instruction and
  `ConvertToMidCircuitResetAndMeasure` pass.
- 0.37.0 (2025-03-13): `PulseBackendConfiguration` removed.

Any claim that a readout value changed between two backend_version strings
therefore has only the repository's own dated snapshots as evidence.

## 2. Other Heron r2 devices

None found with a readout-resonator parameter. ibm_kingston is in section 1.
ibm_aachen launched as a Heron r2 QPU (changelog 9 and 10 April 2025, section
1f) and IBM calls it "Heron r3" after its upgrade (changelog April 2026: "the
upgraded Heron r3 QPU ibm_aachen"). Data from the interval between launch and
upgrade is Heron r2 (ibm_aachen) evidence, tag HERON-R2-OTHER; data after the
upgrade is Heron r3 context. No ibm_aachen readout source was located in
either interval; the search for papers naming ibm_aachen was not run (see
"Not run").

## 3. Revision-only Heron r2 statements

- IBM processor-types page (quoted above): r2 is the 156-qubit heavy-hex
  revision, July 2024, "introduces a new TLS mitigation feature". No readout
  statement. R2-REVISION-ONLY.
- IBM Qiskit docs, execute-dynamic-circuits
  (https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits, no
  version or date shown, read 2026-10-16; transcription in
  docs/notes/ibm_quantum/execute-dynamic-circuits.md line 58): "The
  `MidCircuitMeasure` instruction maps to the `measure_2` instruction reported
  in the backend's `supported_instructions`. However, `measure_2` is not
  supported on all backends." Also from the fetched page: "it adds less
  overhead to your circuit than when using `QuantumCircuit.measure`." No
  duration, ring-down or feed-forward figure. Revision unstated for the
  instruction; the Target snapshot confirms it exists on all three account
  devices.
- IBM classical-feedforward page
  (https://quantum.cloud.ibm.com/docs/en/guides/classical-feedforward-and-control-flow):
  no latency, timing or ring-down statement.

## 4. Context only (not values for the account devices)

### 4a. Thorbeck, Xiao, Kamal, Govia, arXiv:2305.10508 (IBM Quantum)

- Provenance: IBM-internal flux-tunable test device, family and revision
  unstated, arXiv:2305.10508v1, supplementary text.
- v1, 17 May 2023. IBM test device, family and revision unstated ("The device
  used in this work was designed and fabricated internally at IBM Quantum").
  Flux-tunable qubit, Purcell filter. OTHER-FAMILY / no revision; context only.
- Supplementary text (page 10 of the PDF extraction): "The latter assumption
  is valid outside of the number splitting regime, i.e. chi << kappa, and for
  our device chi/2pi = 0.98 MHz and kappa/2pi = 5.24 MHz."
- Main text: "during readout the qubit frequency is Stark shifted ... by
  nu_S = 2 chi n_r, where chi is the dispersive shift and n_r is the average
  number of photons in the readout resonator." Supplement "CALIBRATION":
  the dephasing rate is fit as a function of the readout drive amplitude
  epsilon (arbitrary DAC units), gamma_phi(epsilon) = R epsilon^2, with
  "R/2pi = 429 MHz" (supplement, calibration). The Stark shift is fit against
  the same epsilon and converted to photon number through nu_S = 2 chi n_r,
  so n_r is proportional to epsilon^2 when the Kerr term is dropped; gamma_phi
  is then approximately linear in n_r. The paper states no gamma_phi(n_r)
  fit, and R carries units of MHz per DAC-unit squared (INFERENCE).
- Statement that ring-up and ring-down were not modeled: "we have not
  accounted for the time-dynamics of the induced qubit dissipation during
  ring-up and ring-down of the readout resonator". This is the closest IBM
  statement on measurement-induced Stark shift and dephasing, and it gives no
  decay-time of a post-measurement shift.

### 4b. Yoshioka et al., arXiv:2407.14431 (Krylov diagonalization)

- Provenance: Heron r1 (ibm montecarlo), arXiv:2407.14431v3, appendix
  "Device properties".
- v3, 3 Oct 2024. Authors IBM Quantum plus collaborators. "We performed
  experiments on the Heron R1 processor ibm montecarlo. This is a 133-qubit
  device with fixed-frequency transmon qubits connected to each other via
  tunable couplers." (Section III, page with Fig. 9 text). Tag: Heron r1
  (stated), not r2.
- Appendix "Device properties": medians for the qubit subsets: "readout error
  1.6% and length 2us" (57-qubit subset; 1.8% and 2us for the 43-qubit
  subset), T1 180 us, T2 150 us, two-qubit gate length 104 ns / 88 ns. No
  kappa, chi, or resonator frequency.

### 4c. Baumer et al., arXiv:2308.13065 (dynamic circuits)

- Provenance: ibm_sherbrooke (127-qubit) and ibm_peekskill (27-qubit),
  revisions unstated in the paper, arXiv:2308.13065v2, appendix D.
- v2 18 Sep 2024 (v1 24 Aug 2023). Devices ibm_sherbrooke (127-qubit) and
  ibm_peekskill (27-qubit). Neither revision is stated in the paper. By IBM
  convention ibm_sherbrooke is Eagle and ibm_peekskill is Falcon, but I did not
  retrieve IBM's own listing in this session; INFERENCE, OTHER-FAMILY.
- Appendix D.1 (ibm_sherbrooke): "The two-qubit gate time is 0.5 us, the
  readout time 1.2 us and the feed-forward time roughly 0.7 us." Appendix D.2
  (ibm_peekskill): "The two-qubit gate time is 0.6 us, the readout time 0.9
  us and the feed-forward time roughly 0.7 us."
- Section III: the average feed-forward time "scales with the number of
  potential mid-circuit measurement bitstring outcomes" (switch tests outcomes
  one by one). Feed-forward time is "the main source of idling error in the
  dynamic circuit"; DD pulses cannot be applied during it. This describes the
  control stack of 2023-2024; whether the stack on the account devices keeps
  that scaling is not stated anywhere I found.

### 4d. Readout error mitigation for MCM and feedforward, arXiv:2406.07611

- Provenance: Falcon family (ibm_algiers, ibmq_kolkata, ibm_mumbai; 27
  qubits) and Eagle family (ibm_osaka, ibm_kyoto; 127 qubits), revisions
  unstated, arXiv:2406.07611v2 (header "03 Feb 2025"), section IV and
  appendices.
- The paper states the families: "27-qubit devices {ibm_algiers,
  ibmq_kolkata, ibm_mumbai} hosting Falcon-family processors, and 127-qubit
  devices {ibm_osaka, ibm_kyoto} hosting Eagle-family processors." The
  main-text experiments of section IV use ibmq_kolkata and ibm_osaka; the
  remaining three appear in appendix data. OTHER-FAMILY. States only:
  "waiting for mid-circuit measurements can incur considerable decoherence",
  "there may be measurement cross-talk", measurements take a small multiple
  of a CX duration. No resonator parameters.

### 4e. Kim et al., Nature 618, 500 (2023), arXiv/PMC10266970

- Provenance: ibm_kyiv, revision unstated in the retrieved page, Nature 618,
  500 (2023).
- ibm_kyiv, fixed-frequency transmon, heavy-hex, Eagle (not stated in the
  retrieved page). Retrieved page states "median T1 and T2 times of 288 us and
  127 us" and nothing on readout resonators or readout duration. The
  Supplementary Information PDF was not retrieved; I cannot confirm whether it
  holds readout parameters. Context only.

### 4g. Chatterjee, Schwinger, Gao, arXiv:2412.04053 (readout reinforcement learning)

- Provenance: ibm_brisbane qubit 2 and ibm_kyoto qubit 2, arXiv:2412.04053v2
  (11 Dec 2024; v1 5 Dec 2024), main text and Table 2 / Appendix. The paper
  does not state family or revision for either device. arXiv:2406.07611v2
  (section 4d) states ibm_kyoto is a 127-qubit Eagle-family device, revision
  unstated. ibm_brisbane is Eagle r3 per third-party papers found by search
  (not confirmed here against an IBM listing). Tag: OTHER-FAMILY, INFERENCE
  for the ibm_brisbane family and revision; context only, never a Heron r2
  value.
- Authors are from the University of Oxford and the Centre for Quantum
  Technologies, National University of Singapore; they used the IBM devices
  as users, so the values are measured by the authors on those devices.
- Main text, paragraph on the training and test devices (paper's wording):

  | Device | kappa | 2chi/2pi | kappa/chi |
  |---|---|---|---|
  | ibm_brisbane qubit 2 | "kappa ~ 21.4 MHz" | "2chi/2pi ~ 0.31 MHz" | "kappa/chi ~ 22" |
  | ibm_kyoto qubit 2 | "kappa ~ 10.4 MHz" | "2chi/2pi ~ 0.85 MHz" | "kappa/chi ~ 4" |

  The printed kappa/chi ratios agree with the printed kappa and 2chi/2pi only
  if kappa is read as an angular rate in rad/us; the paper does not state the
  convention, so the units of kappa are ambiguous (INFERENCE).
- Default readout, main text: "a 720 ns square readout pulse and a 680 ns
  delay for passive resonator reset"; "Both devices have a default
  measurement time of 1400 ns." This is the only public pulse/reset split
  found, for these two devices only.
- Table 2 (Appendix): default maximum resonator photon number 58.6
  (ibm_brisbane) and 26.8 (ibm_kyoto); optimized pulse durations 470 ns /
  490 ns (ibm_kyoto, RL / A3R) and 675 ns / 685 ns (ibm_brisbane). Appendix
  single-tone reset on ibm_brisbane: "it resets from 58.8 to 0.6 photons."
  Resonator frequency and steady-state photon number are not reported.
- Internal inconsistency: the main text lists default assignment errors
  "(5.8 +- 0.9)e-3 and (7.0 +- 1.0)e-3" in the order Brisbane, Kyoto, while
  Table 2 assigns 5.8e-3 to Kyoto and 7.0e-3 to Brisbane. The error values
  are not used here.

### 4f. Non-IBM kappa and chi (to avoid confusion)

Search surfaced Google (arXiv:2308.02079, model-based readout) and ETH
(arXiv:2503.12603, authors Norris, ..., Wallraff) kappa/chi values. They are
not IBM and are excluded.

## 5. API exposure

Evidence for what the account devices expose, from the live API read
2026-10-17 (supplied) and IBM's qpu-information page:

- `backend.configuration().hamiltonian` is None; `meas_kernels` and
  `meas_levels` are None. So chi, wr, kappa, qubit frequencies are not exposed
  on the account's three Heron r2 devices. Qubit properties contain T1, T2,
  init_error, prob_meas0_prep1, prob_meas1_prep0, readout_error,
  readout_length only; no `frequency` or `anharmonicity` (the IBM page's
  example output shows `frequency=None`, tagged as the page's own example,
  device unnamed).
- IBM doc statement on durations: "For `measure`:
  `backend.properties().readout_length(<qubit>)` For `measure_2`:
  `backend.target['measure_2'][<qubit 1>, ].duration`".
  (https://quantum.cloud.ibm.com/docs/en/guides/qpu-information, no version
  date shown.) The page uses `backend.configuration()` only for `mcps`.
- Instruction signatures: qiskit-ibm-runtime 0.43 reads an
  `instruction_signatures` field from backend configuration for `measure_2`;
  that is the only readout-related configuration field named in the release
  notes I read.
- meas_lo_range, qubit_lo_range, rep_times: a read-only
  `service.backend(NAME).configuration()` call on 2026-10-17 returned a
  `QasmBackendConfiguration` for ibm_fez (1.3.37), ibm_kingston (1.0.0) and
  ibm_marrakesh (1.0.21), all processor_type Heron r2, with no `meas_lo_range`,
  `qubit_lo_range` or `rep_times` attribute; for ibm_fez `to_dict()` carries
  no key containing "lo_range" and the only repetition fields are
  `default_rep_delay` and `rep_delay_range`. Tag: DEVICE-MATCHED, stated by
  the API (fields absent, so no LO range is exposed).
- `backend_version` is exposed as a string; no public changelog maps its
  values to calibrations (section 1g).

## 6. Quantities and answers

Feed-forward latency, for scheduling: the `measure_2` and `measure` durations
above plus a latency that no public source states for the three account
devices. Values nearby: roughly 0.7 us (ibm_sherbrooke / ibm_peekskill,
2023-2024 paper), approximately 600 ns ("IBM hardware", 2026 paper, device
unstated), 500 ns (cited by MCMit, source device unstated). These are
context, not device values. A device-matched figure can be read from the
circuit-timing output (`scheduler_timing`), which the repository already
documents (docs/notes/ibm_quantum/qiskit-runtime-circuit-timing.md), but I
did not run that probe because it needs a job submission.

## Summary table

| Quantity | Value | Exact device | Revision | Source and version | Status | Predates account version? |
|---|---|---|---|---|---|---|
| kappa/2pi | none found | ibm_fez, ibm_kingston, ibm_marrakesh | Heron r2 | none | not found | n/a |
| chi/2pi, resonator-qubit detuning, band | none found | same | Heron r2 | none | not found | n/a |
| kappa/2pi (IBM test device) | 5.24 MHz | IBM internal test device | unstated | arXiv:2305.10508v1 (17 May 2023), supplementary | context only (other-family) | n/a |
| chi/2pi (IBM test device) | 0.98 MHz | IBM internal test device | unstated | arXiv:2305.10508v1, supplementary | context only (other-family) | n/a |
| `measure` duration | 1660 / 2180 / 2684 ns (fez / kingston / marrakesh) | each of the three | Heron r2 | live Target, snapshot 2026-10-14 (targets.json), re-read 2026-10-17 | stated, device-matched | no (matches current) |
| `measure_2` duration | 1340 / 1380 / 1884 ns | each of the three | Heron r2 | same | stated, device-matched | no |
| `reset` / `measure_reset` | 1684 / 2212 / 2720 ns | each of the three | Heron r2 | same | stated, device-matched | no |
| Heron readout length range | 1560-2584 ns | fleet, device-unstated | Heron (revision unstated) | arXiv:2604.25863v3 (7 Aug 2026), citing an IBM resources page (reference accessed 2025-08-20; the table is a fleet range of unknown date) | context | cannot tell |
| ibm_kingston `measure_2` vs `measure` | 65 percent shorter; `measure` 34x a 2q gate | ibm_kingston | Heron r2 | arXiv:2604.03360v2 (15 Sep 2026) | stated, device-matched, disagrees with snapshot (37 percent) | cannot tell; no backend version given |
| Feed-forward latency | approx 600 ns | "IBM hardware", device unstated | unstated | arXiv:2604.03360v2 | not device-matched | n/a |
| Feed-forward latency | roughly 0.7 us | ibm_sherbrooke, ibm_peekskill | unstated (likely Eagle / Falcon, inference) | arXiv:2308.13065v2 (18 Sep 2024), App. D | other-family | yes |
| Ring-down / post-measurement buffer | none found | account devices | Heron r2 | none (not split out of readout_length) | not found | n/a |
| Residual-photon Stark shift / dephasing vs delay, with decay time | none found | account devices | Heron r2 | none; arXiv:2606.00433v2 reports T1-dominated backaction, no photon figure | not found | n/a |
| kappa (ibm_brisbane q2 / ibm_kyoto q2) | 21.4 / 10.4 MHz (units ambiguous) | ibm_brisbane, ibm_kyoto | unstated (127-qubit; Eagle-class, inference) | arXiv:2412.04053v2, main text | context only (other-family) | n/a |
| 2chi/2pi (ibm_brisbane q2 / ibm_kyoto q2) | 0.31 / 0.85 MHz | ibm_brisbane, ibm_kyoto | unstated (as above) | arXiv:2412.04053v2, main text | context only (other-family) | n/a |
| Readout pulse + passive reset delay | 720 ns + 680 ns = 1400 ns | ibm_brisbane, ibm_kyoto | unstated (as above) | arXiv:2412.04053v2, main text | context only (other-family) | n/a |
| Qualitative: MCM-induced spectator dephasing exists | no number | ibm_kingston (statement in paper) | Heron r2 | arXiv:2604.03360v2 section I-A | stated qualitatively | n/a |
| configuration().hamiltonian, meas_kernels, meas_levels | None | each of the three | Heron r2 | live API 2026-10-17 | stated by API (not exposed) | no |
| properties() fields | T1, T2, init_error, prob_meas*, readout_error, readout_length | each of the three | Heron r2 | live API 2026-10-17 | stated by API | no |
| backend_version change log | none found | each of the three | Heron r2 | none | not found | n/a |

No Heron r2 value was found in the sources read for: kappa, chi, resonator or qubit frequency
and detuning, integration time apart from `readout_length`, ring-down or
buffer time, device-matched feed-forward latency, residual-photon Stark shift
or dephasing with decay time, or any
backend_version-to-calibration change history. The configuration fields
`meas_lo_range`, `qubit_lo_range` and `rep_times` are absent from all three
account devices (section 5), so no LO range is exposed either. Closing those needs a
measurement on the devices (a Ramsey-after-measurement delay sweep on a
spectator and on the measured qubit, run per device and per backend version)
or IBM disclosure.

## Not run

- Kim et al. 2023 Supplementary Information PDF: not retrieved.
- IBM blog posts on Heron readout: no relevant post located by search.
- Text search of the IBM changelog for the strings above: the page was
  summarized by the fetch tool, not grepped.
- ibm_aachen readout papers and snapshots from its Heron r2 interval: no
  search run.
- Resolving ibm_sherbrooke and ibm_peekskill revisions from an IBM listing:
  not done.
