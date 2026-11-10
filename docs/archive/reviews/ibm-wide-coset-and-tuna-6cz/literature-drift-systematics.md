# Literature on drift and systematics for the wide-coset and 6-CZ null-block claims

This review lists the documents held in the workspace that bear on two registered hardware claims and states what each
predicts. Every entry names a file that was opened; the tag on the entry says how far. Paths in code font name a file in
the stated repository and carry no link, because the documents repositories sit outside this tree.

- `[S]` the source bytes were opened (PDF text layer or the transcription beside the PDF) at the cited page.
- `[N]` only the registered reading note in `docs/notes/` was opened; the claim is the note's, not re-read from the source.
- `[R]` a repository record or code file of this tree was read for this review.

Documents of gororoba-documents-private are paraphrased with a page locator and never quoted, because text of the private
repository does not enter this public tree. Short quotations appear only from documents of gororoba-documents-public.

## Observations the literature has to explain

Operand names follow `docs/evidence/pathion-kernel-map/README.md`. A coset block is a group of 8 output bins read through
3 data qubits and a selector qubit; a placement is the 4-qubit tile that carries one block, and one fused job runs 16 or
17 placements side by side on the chip. The nullity estimator N_hat is defined in
`docs/evidence/pathion-kernel-map/nhat-bias/README.md`.

| Label | Observation | Registry location |
|---|---|---|
| fez-null | ibm_fez fails both null controls (the 64-dimensional operand e1 + e33, called n64, reads -0.531; the 128-dimensional e1 + e65, n128, reads -1.056) and the per-block localization and visibility rules, while its targets pass | claim `hw-ibm-pathion-wide-coset` |
| fez-placements | the loss follows two placements: placement 7 (physical qubits 79, 92, 93, 94; mean visibility 0.595) and placement 15 (qubits 10, 11, 12, 18; 0.710), against 0.888 to 0.973 on the other fourteen | same claim, boundary |
| fez-copy | copy-agreement z of -11.4 (n64) and -5.6 (the 64-dimensional target o64) against the limit 3: placement-to-placement scatter above shot noise | same claim, boundary |
| king-offset | ibm_kingston passes all rules; its null controls carry a per-block offset of -0.030 (n64) and -0.033 (n128), the same sign and size as the earlier one-CZ null reading, and its 128-dimensional target sits 0.126 above 60 | same claim, boundary |
| tuna-b0 | on Tuna-17 (Quantum Inspire) the two base replicates of the 21-CZ null block b0 = e1 + e17 read selector contrast 0.0162 and 0.0393 (chi-square 34.86 against 10.83); every 6-CZ replicate pair passes | claim `hw-tuna17-pathion-six-cz-null-blocks` |
| tuna-q11 | physical qubit 11 of Tuna-17 reads a |1> misassignment of 0.095 in batch 14 and 0.434 in batch 15; all five readout shifts above 0.02 in the series sit on that qubit | same claim, boundary |
| 32-dim | the 32-dimensional analyses carry an N_hat bias that survives readout correction, a +0.02 per-bit local-channel bias, leakage into the zero character, and non-flat all-aligned blocks | `docs/notes/topics/a5-hardware-algebra-synthesis.md`, `nhat-bias/README.md` |

Qubit 11 of Tuna-17 and qubit 11 of ibm_fez are unrelated physical qubits on different devices and different vendors.

## Record checks made for this review

These are repository observations, not literature. Each is a lead for the claim owner, produced by reading retained
records read-only, and none has passed an independent check.

1. **Tuna batch timing `[R]`.** `results/quantum_inspire/runs/2026-11-07T202323Z-pathion_one_cz_null_tuna_17-batch-NN/`
   (`submission-state.json`, `results.json`) gives the submission time of each batch: 00 at 2026-11-07 20:27Z, 01 at
   21:12Z, 03 at 22:28Z, 04 at 23:40Z, 07 at 01:25Z (2026-11-08), 08 at 05:00Z, 11 at 06:58Z, 12 at 08:01Z, 14 at 09:15Z and
   15 at 09:58Z, the last finishing at 11:09Z. The replicate pairs of `executed_order` in
   `results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json` therefore sit 13.5 hours apart for the b0 base
   (batches 00 and 15, chi-square 34.86), 12.1 hours for the b0 twin (batches 01 and 14, 3.66), 9.5 hours for k4 (03 and 12),
   7.3 hours for k8 (04 and 11) and 3.6 hours for k12 (07 and 08), each of the last three passing. The b0 twin differs by
   0.0105 (z = 1.9) with the same sign as the base pair, so both b0 pairs read higher late. Separation alone does not
   order the chi-squares (the 12.1-hour twin passes); the failing pair is also the only one whose circuit has 21 CZ.
2. **Tuna q11 readout is a switching signal, not a ramp `[R]`.** The `drift_covariate` block of the same analysis file
   flags q11's |1> misassignment at 0.362 in batch 03, 0.039 in batch 04, 0.033 in batch 08, 0.067 in batch 09, 0.095 in
   batch 14 and 0.434 in batch 15. At batch 03 to 04 the other misassignment of q11 (kind `e01`) also moves (0.0236 to
   0.068); at batch 14 to 15 it does not exceed the 0.02 threshold. The two steps therefore split in their companion
   channel.
3. **ibm_fez calibration snapshot `[R]`.** The 12 PUBs of the ibm_fez job carry one identical `placed_qubit_calibration`
   (checked on all 12 in `results/live/2026-11-07T153325.440007Z/collect.json`), so no recalibration separates its PUBs.
   Of the 68 measured qubits, qubit 11 (placement 15) ranks first-worst in both T1 (70.6 us) and T2 (24.7 us); placement
   7 holds qubit 94 (T1 rank 8 of 68 from the bottom) and qubit 79 (T2 rank 9). The median T1 is 152.6 us on ibm_fez and
   258.3 us on ibm_kingston. Placement 15 nevertheless reads visibility 0.710, better than placement 7 at 0.595, so the
   snapshot does not rank-order the loss.
4. **An extreme calibration entry that the raw bits admit `[R]`.** The execution-time snapshot in
   `results/live/2026-11-07T153325.440007Z/collect.json` lists ibm_fez qubit 90 with a |1>-to-|0> flip of 0.835
   (readout error 0.417, six times the next worst of 68), while the planning record `record.json` of the same job lists
   the same qubit at readout error 0.0039. Qubit 90 belongs to placement 2 (qubits 89, 78, 88, 90). The routed circuit
   `isa.qpy` (qiskit 2.6.2) assigns qubit 90 to `g0_r2_c[1]` in PUBs 2, 3, 8 and 9 and to `g0_r2_c[3]` in the other
   eight; in `pub_02` qubit 89 writes `g0_r2_c[3]`. The mapped qubit-90 marginals range over P(1) = 0.048 to 0.119 in the twelve
   PUBs, inside the 0 to 0.165 that a 0.835 flip admits; the 0.919 marginal of `pub_02` bit 3 belongs to qubit 89. The
   data therefore leave the entry unfalsified. The corrected readings of placement 2 carry a standard error of 0.078
   (o128 block k8) and 0.066 (n128 block k8) on ibm_fez against 0.011 and 0.0083 on ibm_kingston, the inflation a
   6-fold readout inverse produces, and the placement-2 outlier (o128 block k8 reads 2.872 against 3) is sensitive to
   that channel.
5. **The readout correction is a tensor product `[R]`.** `gororoba_quantum/live_run.py` (`readout_corrected`,
   `readout_factors`) inverts one 2 x 2 channel per classical bit from the backend's `prob_meas1_prep0` and
   `prob_meas0_prep1` and applies them as a Kronecker product. No correlated term enters.

## Per-observation reading

| Observation | Explains or predicts | Falsifies or bounds |
|---|---|---|
| fez-null, fez-placements | qubit-specific two-level-system (TLS) defects lower T1, T2 and readout fidelity on named qubits for minutes to days (Klimov, Schloer, Thorbeck) and IBM monitors TLS signatures and may pause calibration for affected qubits (IBM guide) | snapshot ranks (check 3) support placement 15 and only weakly placement 7; check 4 shows placement 2's correction rests on an extreme but unfalsified qubit-90 readout channel |
| fez-null | a null control and a target in separate PUBs inherit any time-correlated difference (Sarovar p. 15) | the 12 PUBs of one job share one calibration snapshot (check 3); drift between them lies outside the shot covariance and stays an unmeasured alternative, since Klimov's diffusion scale is an other-device stochastic scale and telegraphic jumps reach about 60 MHz |
| fez-copy | context-dependent errors from concurrent gates and from neighbors that run at the same time (Sarovar, Niu note, Seif note) | cosmic-ray bursts cannot hold two placements low across 12 PUBs (McEwen, Harrington) |
| king-offset | a static assignment asymmetry; the prepare-and-measure matrix is not the readout channel (Geller p. 1) and the tensor-product inverse leaves a correlated remainder (Bravyi p. 7) | a drift reading, since the offset keeps its sign and size across runs |
| tuna-b0 | replicates 13.5 h apart straddle TLS spectral diffusion of a standard deviation of about 18 MHz (Klimov's 2 D t^(1/2) at 13.5 h) and Quantum Inspire retunes in the background (Last p. 12, tuna-17.md) | monotone slow drift alone, since q11's |1> misassignment switches both ways (check 2) |
| tuna-q11 | a TLS jump in frequency changes the lifetime during readout within 9 minutes and moves the |1> misassignment only (Thorbeck p. 3; mapping that mechanism onto one unchanged assignment channel is a hypothesis) | a discriminator-threshold shift, which moves both misassignments (split in check 2) |
| 32-dim | the N_b = 2 bias follows a local output-bit channel; the multiplicative test of its characters bounds correlated readout (Bravyi) | the recorded readout flip falls 0.005 to 0.009 per bit short of the fitted 0.020 to 0.023 |

## Tier one: the five strongest sources

### 1. Klimov et al., fluctuations of energy-relaxation times (arXiv 1809.01043)

- Repository `gororoba-documents-private`, path `physics/quantum-devices-control/1809.01043v1.pdf` (transcription
  `1809.01043v1.md` beside it), manifest sha256 `570fc9861c5d2a063f2138471abec03c6328a23dc69225e9fd5b51e61056fa9e`.
  `[S]`, registered note `docs/notes/papers/1809.01043.md`.
- Locators. PDF p. 2: T1 of a frequency-tunable transmon varies by up to an order of magnitude and switches between
  extrema abruptly on 15-minute and 5-MHz scales. PDF pp. 3 to 4 and p. 21 (Fig. S5 caption): individual TLS defects diffuse
  in frequency with a diffusivity of 2.5 +- 0.1 MHz per square-root hour, and some switch telegraphically by up to about 60
  MHz. PDF p. 9 (Fig. 2 caption): 31,278 T1 measurements over 400 MHz and 1200 minutes. PDF p. 5: the authors state that
  defect diffusivity should set how often qubit-frequency selection is rerun. PDF p. 13: the qubit-frequency calibration
  curve stayed within 1 MHz over about 25 hours, so the fluctuations are TLS motion, not qubit-frequency drift.
- Prediction. The law sigma(t) = 2 D t^(1/2) (PDF p. 3) gives a standard deviation of the TLS frequency of 2.50 MHz in
  15 minutes, 5.00 MHz in 1 hour, 18.4 MHz in 13.5 hours and 0.26 MHz in 10 seconds, in the diffusive regime of a
  tunable Xmon device, not either device under review. These are empirical stochastic scales, not bounds: telegraphic
  defects jump by up to about 60 MHz (PDF p. 4) at any time. A qubit with a TLS within a few MHz of its transition
  plausibly changes T1, readout and contrast between replicates 13.5 hours apart; a change between the PUBs of a 9 to 11
  second job is less likely but stays possible and unmeasured.
- Bears on. tuna-b0 (time scale of the replicate disagreement), fez-placements (qubit-specific loss), and the boundary
  statement that drift between PUBs of one job lies outside what the shot data test.
- Limit. A Google Xmon device with tunable qubits; Heron r2 transmons are fixed-frequency with tunable couplers. Telegraph
  switching is not a ramp, so the source predicts no monotone trend over the series.

### 2. Thorbeck et al., readout-induced suppression and enhancement of qubit lifetimes (arXiv 2305.10508)

- Repository `gororoba-documents-private`, path `physics/quantum-devices-control/2305.10508v1.pdf`, manifest sha256
  `4c03b8cbcdb8e04c166c81b099ccbc69a18b435f897f8d1dd92e63f47f6fa685`. `[S]`. Registry: `docs/SOURCES.json` registers only
  the HTML rendering (sha256 `72ba4e3f22c333aa4af6ec9f9c24abffe9f31f7323b55621387ff38e9df78d7f`), and the PDF has no row in
  `docs/sources/reading-copy-locations.tsv`; the in-tree reading note is `docs/notes/ibm_quantum/heron-r2-readout-resonator.md`
  (section 4a), which rates the device as other-family context.
- Locators. PDF p. 1 (abstract and introduction): lifetime degradation during readout is an anti-Zeno effect, in which
  readout-induced dephasing broadens the qubit onto nearby dissipation hot spots, which the authors attribute to TLS. PDF
  p. 3 ("Bath dynamics"): a TLS can jump in frequency after a thermal fluctuator flips or after ionizing radiation, and two
  measurements 9 minutes apart show a change in the qubit's frequency-dependent loss that carries through to the
  lifetime during readout.
- Prediction. A readout assignment error that jumps by a factor of several between consecutive batches belongs to a qubit
  whose TLS environment changed within minutes. The mechanism shortens T1 during the readout window, so it raises the
  |1>-to-|0> error of that qubit and leaves the |0> error unchanged, and it depends on readout power.
- Bears on. tuna-q11. The step at batch 14 to 15 (|1> misassignment +0.338, other channel unchanged) matches; the step at
  batch 03 to 04 moved both channels and does not (check 2). The pair is a split, not a fit.
- Limit. An IBM flux-tunable test device with a Purcell filter; Tuna-17's readout power, resonator detuning and layout
  are unpublished in the registered sources (`docs/notes/quantum_inspire/shot-record-literature.md`, section 4).

### 3. Sarovar et al., detecting crosstalk errors in quantum information processors (arXiv 1908.09855)

- Repository `gororoba-documents-public`, path `physics/quantum-characterization/1908.09855v3.pdf`, manifest sha256
  `af9a7d4bdf54ab2255baf093cfbd7fa8a27a98c1f6afee7e67a37f0554bc7f71`, license CC-BY-4.0. `[S]`, note
  `docs/notes/papers/1908.09855.md`.
- Locators. PDF p. 15: "If behavior of the device (e.g., error rates) is correlated with time - i.e., it drifts - then
  if the settings are also correlated with time, this will produce spurious evidence" of dependence; the same page
  names a two-state fluctuator as a drift source. PDF pp. 15 to 16: rastering or randomizing the circuit order removes the
  correlation between setting and time. PDF pp. 14 to 15 (Sec. 6.3): dependence tests run on regions with varied contexts
  and on all-idle companions.
- Prediction. A design that places the replicates of one comparison at the two ends of a 15-hour series confounds replicate
  identity with time; a design that interleaves them does not. On the IBM side, a null control and a target in separate
  PUBs are the same confound at the scale of seconds, bounded by the single calibration of the job (check 3).
- Bears on. tuna-b0 (the two b0 base replicates are batch 00 and batch 15, the cleanest design finding of this review),
  fez-null (separate-PUB differences), and fez-copy (neighbor activity as a context).
- Limit. Simulated two-qubit and six-qubit processors; no Heron-specific error map.

### 4. Proctor et al., detecting and tracking drift in quantum information processors (arXiv 1907.13608)

- Repository `gororoba-documents-private`, path `physics/quantum-characterization/1907.13608v3.pdf`, manifest sha256
  `24b8e9e8f9c62236c5e94148fa44d52881f137747b1abc6266a2c15e900a31e7`. `[S]`, note `docs/notes/papers/1907.13608.md`.
- Locators. PDF p. 1: temporal instability is ubiquitous (abrupt T1 changes, 1/f noise, 50 or 60 Hz line noise, mechanical
  vibration). PDF p. 3: each Fourier power of a standardized time-ordered bit string is chi-square with one degree of
  freedom under constant probability, with strong control of the family-wise error rate. PDF pp. 2 to 3 (Fig. 1): a trapped-ion
  Ramsey detuning drifted at 15 to 250 microhertz over 8 hours and tracked laboratory temperature. PDF pp. 11 to 12
  (Appendix A, read through the note): the highest resolvable frequency is set by the sample rate and the lowest by the
  record length.
- Prediction. The per-shot bit strings retained under `raw/<job>/pub_NN.json` support this test inside one PUB, but a PUB
  lasts a fraction of the 9 s job, so the test is blind to anything slower than one cycle per PUB duration. It cannot see the hour-scale
  separation of the Tuna replicates, which lie in different jobs. Time-resolved acquisition (interleaved replicates or a
  drift probe) is the only route to that time scale.
- Bears on. tuna-b0, fez-copy (within-PUB scatter above shot noise would show as spectral lines), and the claim boundary.
- Companion data (Zenodo `10.5281/zenodo.4033077`) is listed as unobtained in `gororoba-infrastructure`
  `docs/library/owner-fetch-list.md`.

### 5. van der Schoot et al., quantum metrics on Starmon-5 of Quantum Inspire (arXiv 2310.01120)

- Repository `gororoba-documents-public`, path `physics/quantum-characterization/2310.01120v1.pdf`, manifest sha256
  `d2beb265473ac567f7470553c4a27a9b49ba5286da706d03b59458f82ef0e655` (transcription `2310.01120v1.md`, sha256
  `34d0c599bd0192c48d5dda32975f5ab64e2e70315d934204b5cb4a862d7126be`), license CC-BY-4.0. `[S]`, note
  `docs/notes/papers/2310.01120.md`.
- Locators. PDF p. 7: the device "evolves slowly over time" and its metrics change with drift, retuning and upgrades. PDF
  p. 9: "repeating readout fidelity measurements on the qubits results in a higher variance in the results than expected
  for a stable system" (per-qubit readout fidelities 96.4 to 98.4 percent, Table 1). PDF pp. 11 to 12 (Sec. 3.2): the T2*
  series, each point of 4,096 shots, leads the authors to call the device "a rather unstable device".
- Prediction. On the same platform family (QuTech's Quantum Inspire stack, a different five-qubit chip) readout and
  coherence metrics scatter between repetitions above shot noise, so a chi-square gate across batch replicates can fail
  from device instability alone (the paper estimates no failure rate) and the replicate-heterogeneity gate of the claim is the correct first test. The magnitude does not
  transfer to Tuna-17.
- Bears on. tuna-b0, tuna-q11.

## Tier two: sources that settle one observation

### IBM Quantum calibration-jobs guide (registered web source)

- Repository `gororoba-quantum`, note `docs/notes/ibm_quantum/calibration-jobs.md`; the registered response hash of the
  page is `a57dfe7809b3acbb02f3aa2c71fcc193f550dce47da94900d68fa4433a1b984d` (row in
  `docs/notes/ibm_heron_platform.md`). No manifest row exists, since the page is not a document of the documents
  repositories. `[N]` plus the note's text `[R]`.
- Content. Parameter monitoring runs about hourly between user jobs and includes signatures of TLS activity; severe TLS
  activity can change the calibration strategy of the affected qubits and pause their calibration; a calibration job cannot
  run while a job or session runs, so two jobs submitted together can run under different calibration sets; Heron
  calibration time is typically under two hours a day.
- Prediction. A qubit under TLS attack can stay on a stale calibration, so the recorded properties that the collector uses
  for readout correction can disagree with the executing qubit (check 4). No recalibration falls inside one 9 or 11 second
  job.
- Bears on. fez-placements, the boundary on between-PUB drift, check 4. Repository prior: n21 contrast drifted 0.0229 to
  0.0308 within a day (`docs/notes/ibm_quantum/hardware-controls.md`, row G8).

### Bravyi et al., mitigating measurement errors (arXiv 2006.14044)

- Repository `gororoba-documents-private`, path `physics/quantum-characterization/2006.14044v2.pdf` (transcription
  `2006.14044v2.md`), manifest sha256 `721040ac1d9a36a460d71d4e5a0c79d15c9016fc9a62d3aa73fc3d503fc7b226`. `[S]`.
- Locators. PDF p. 7 (graph-state experiments on IBM hardware): the tensor-product model systematically overestimates the
  mean values of stabilizers of weight 3 to 6 against the full assignment matrix, and some qubit pairs carry correlated
  readout errors of a few percent. PDF p. 8: on a 20-qubit state the correlated rates fall below 1 percent for all pairs.
- Prediction. A tensor-product inverse (check 5) leaves a residual that grows with the weight of the Walsh character it
  multiplies. hypothesis: this predicts a positive bias at high-weight characters, which would fit the positive ibm_kingston offset at the
  128-dimensional target and does not fit the negative null offsets.
- Test already in the tree. The multiplicative law lambda(a XOR b) lambda(0) = lambda(a) lambda(b) of the N_b = 2 blocks
  (`nhat-bias/README.md`, "Spectral reading") holds within 1.7 standard errors on 25 of 28 fits, which bounds a few-percent
  correlated readout term at block level on the 32-dimensional runs.

### Geller, rigorous measurement error correction (arXiv 2002.01471)

- Repository `gororoba-documents-private`, path `physics/quantum-characterization/2002.01471v2.pdf`, manifest sha256
  `4c63f036641a4b4ce09b87c2d070d1afc89537698af8ba6839cbffb285bfb604`. `[S]` at PDF p. 1 (abstract).
- Content. Within the biased measurement model, nonideal measurement equals ideal projective measurement followed by a
  classical Markov process Gamma, and Gamma equals the measured prepare-and-measure matrix only when preparation error is
  negligible.
- Prediction. A confusion matrix measured by preparing basis states folds preparation error into the readout channel and
  overstates the asymmetry a circuit sees. This is the repository's own finding of an overstatement by about 0.09
  (`a5-hardware-algebra-synthesis.md`, instruments table), here with a mechanism, and it favors a static asymmetry for the
  king-offset reading.

### Schloer et al., correlating decoherence in transmon qubits (arXiv 1901.05352)

- Repository `gororoba-documents-private`, path `physics/quantum-devices-control/1901.05352v2.pdf`, manifest sha256
  `2f4e1636ed5ad0b73efdfc57d5434954f3a0dcfb991fdfef8915be24cf6ee09b`. `[S]` at PDF pp. 1 to 2, note
  `docs/notes/papers/1901.05352.md`.
- Locators. PDF p. 1 (abstract and introduction): on a fixed-frequency transmon, T1, Ramsey dephasing and transition
  frequency show telegraphic burst noise on time scales of hours or days, a millihertz-band spectrum tied to a few TLS near
  the film edge on a 1/f background. PDF p. 2 (Fig. 1): a continuous 19-hour record.
- Prediction. The fixed-frequency device matches Heron and Tuna better than Klimov's tunable Xmon. A switching TLS leaves a
  qubit in one of a few states for minutes to hours, so replicates 13.5 hours apart see different states, the same state
  persists across the 12 PUBs of one job, and rerunning a placement in a later hour can recover it. It also permits a loss
  that persists across two runs on one device a day apart.
- Bears on. fez-placements (falsifier: a rerun that moves block k28 to other qubits and keeps the loss), tuna-q11.

### McEwen et al. (arXiv 2104.05219) and Harrington et al. (arXiv 2402.03208): cosmic-ray and radiation bursts

- Repository `gororoba-documents-private`, paths `physics/quantum-devices-control/2104.05219v1.pdf` (manifest sha256
  `23e184084e13b0fd5767402602f006712a62a3fa3fbcba82978df47b2a7dd05a`) and
  `physics/quantum-devices-control/2402.03208v1.pdf` (`448bc97332fb8f96180d28bdc70b17e0864a65d71797779e6f3cf0b13a954d59`).
  `[S]` at PDF pp. 1 to 4 (McEwen) and pp. 1 to 2 (Harrington), notes `docs/notes/papers/2104.05219.md` and
  `docs/notes/papers/2402.03208.md`.
- Content. On a Sycamore patch, impacts recover with a time constant near 25 ms at an average of one event per 10 s (McEwen pp. 1 to 3;
  the jump of the simultaneous decay count from about 4 to about 24 is the note's figure). On a 10-qubit chip, correlated
  relaxation events arrive at one per 101 s (the note's figure) and cosmic rays account for 17.1 +- 1.3 percent of them (Harrington p. 1;
  recovery constants of 0.7 and 6 ms are from the note).
- Prediction and falsification. Bursts hit the whole chip at random times, so they affect a few tenths of a percent of the
  shots of a 9 to 11 second job (about 100 consecutive shots at the 250 microsecond default repetition delay named in the
  McEwen note) and add cross-placement covariance. They cannot hold the same two placements low across 12 PUBs, and the
  claim reports cross-placement covariance within 1 percent of the multinomial model, which is consistent. They falsify
  a burst reading of fez-placements and fez-copy; they leave tuna-b0 open, because Tuna's shielding is unpublished.

### Sank et al., measurement-induced state transitions (arXiv 1606.05721) and Heinsoo et al. (arXiv 1801.07904)

- Repository `gororoba-documents-private`, paths `physics/quantum-devices-control/1606.05721v2.pdf` (manifest sha256
  `bb3edf88806f12373dcf542930b40378c84ef365748b2a0a927c5879d4222796`) and
  `physics/quantum-devices-control/1801.07904v1.pdf` (`de502e220ec05d22da8850b029848d6be98e56fe09a775e0e27c39d8658a2710`).
  Sank `[S]` at PDF p. 1 (abstract); Heinsoo `[N]` (note `docs/notes/papers/1801.07904.md`).
- Content. Dispersive readout at high resonator photon number drives resonant transitions out of the computational
  subspace (Sank). On a multiplexed device with Purcell filters, individual and simultaneous five-qubit readout differ by
  under 1 percent (Heinsoo note).
- Prediction. Readout-power-dependent errors appear as a step in one qubit's misassignment when the platform retunes its
  readout point, and simultaneous readout of many qubits stays within a percent only with filters. Tuna-17's readout power
  and layout are unpublished, so neither bounds tuna-q11.

### Last et al., Quantum Inspire platform development (Tuna-17's control stack)

- Repository `gororoba-documents-private`, path `physics/quantum-devices-control/last_2020_quantum_inspire_qutechs_platform_development.pdf`,
  manifest sha256 `1c53f676c17365a103a9ab0e469d2e0834725bc0cf39974d3b81ccc8ce21eff5`. `[S]` at PDF pp. 11 to 12 (section
  4.2).
- Locator. PDF p. 12: a calibration graph runs periodically, checks whether each node needs maintenance and reruns a node
  and its dependencies when its status is not good; the time-Rabi node requires the readout point and qubit frequency
  nodes first.
- Prediction. Readout and gate parameters change in steps when a node reruns, and the platform's own retune can fall between
  two batches. The paper describes the spin-qubit device of 2020; the repository's own readout record (`docs/notes/quantum_inspire/tuna-17.md`,
  "Readout calibration drift") shows the same signature on Tuna-17: qubit 9's idle misassignment stepped from 0.027 to 0.271
  across the platform's recalibration, qubits 0 and 6 collapsed, and the fault cleared by the afternoon after platform
  benchmarking.

### Rol et al., Net Zero flux-pulsed CZ (arXiv 1903.02492)

- Repository `gororoba-documents-private`, path `physics/quantum-devices-control/1903.02492v1.pdf` (transcription
  `1903.02492v1.md`), manifest sha256 `f177d4ab9aa8f944ef5f4bfffc19dd1eb2f4ad2e4e3fe88664a4c2a546b1571d`. `[S]` at PDF pp. 2
  to 3.
- Locators. PDF p. 2: unipolar flux pulses are history dependent, which a predistortion filter with Net Zero pulses removes.
  PDF p. 3 (Fig. 3): the conditional phase is first-order sensitive to a flux offset for a unipolar pulse and second-order
  for Net Zero; remaining fidelity loss comes from high-frequency flux noise.
- Prediction. The phase error per CZ scales with the flux offset and adds coherently along a ladder, so a 21-CZ block (b0)
  shows more drift-induced contrast change than a 6-CZ block. This matches the series (b0 pairs fail, 6-CZ pairs pass) and
  is untested: whether the 6-CZ blocks also place a data bit on qubit 11 decides between this reading and the q11 readout
  reading, and the layouts were not compared in this review.

### Rudinger et al., probing context-dependent errors (arXiv 1810.05651), Seif et al. (arXiv 2403.06852), Niu and Todri-Sanial (arXiv 2102.05321), Cobos et al. (arXiv 2507.08088)

- Rudinger: `gororoba-documents-private`, `physics/quantum-characterization/1810.05651v1.pdf`, sha256
  `8c2599bc077d094cbb75fb24d4a33f9e364a0f4fe796f3dac1d0d2274b230d18`, `[N]` (`docs/notes/papers/1810.05651.md`). A
  likelihood-ratio test of identical circuits in two contexts (chi-square reference with (contexts - 1)(outcomes - 1) degrees
  of freedom), applied to an idle, active, idle sequence on an IBM device, with the warning that the active context also
  lengthens the circuit.
- Seif: `gororoba-documents-private`, `computer-science/quantum-software-architecture/2403.06852v2.pdf`, sha256
  `7cccbadaff4574964604b9b6768bb715eddf8026e3f20c5c9f943238f97f87df`, `[N]` (`docs/notes/papers/2403.06852.md`). Coherent
  and correlated errors depend on the layer context (concurrent gates and idles).
- Niu: `gororoba-documents-public`, `computer-science/quantum-software-architecture/2102.05321v3.pdf`, sha256
  `45dd14f6b5ecebfb79ad449142b3c20611f7a405ca03f93356d97cb2ba6f962a`, CC-BY-4.0, `[N]` (`docs/notes/2102.05321.md`).
  Co-running circuits lose 36.8 and 23.1 percent of success probability at crosstalk distance (one hop) and nothing
  beyond it. The wide runs pack 16 or 17 placements per PUB, which is this regime;
  `docs/notes/heron_spatial_multiprogramming.md` holds the repository's guard-band rule and states that the Heron snapshot
  carries no ZZ magnitude.
- Cobos: `gororoba-documents-public`, `physics/quantum-simulation/2507.08088v1.pdf`, sha256
  `201a18edfd9e6038fbc29cc29dc711b87701ac08b45a0baf41e0182ba25678f5`, CC-BY-4.0, `[S]` at PDF pp. 4 and 11. The
  experiments run on ibm_kingston and ibm_marrakesh and use a calibration circuit of known ideal output to estimate the
  combined decoherence factor, on the stated condition that the noise of the calibration circuit matches that of the
  simulation circuit and is Pauli. The null controls of the wide runs play that role; ibm_fez shows that the condition fails
  per placement, so a single contraction factor does not transfer.
- Prediction (shared). A lost placement should sit at one hop from another active placement if crosstalk drives it; a
  placement-by-placement table of the one-hop neighbors of placements 7 and 15 against the other fourteen tests that. Not
  done here: the coupling map of ibm_fez was not read.

### Repository notes that carry device measurements

- `docs/notes/quantum_inspire/tuna-17.md` ("Readout calibration drift") and `results/quantum_inspire/tuna_17_readout_faults.json`
  `[R]`: step changes of readout assignment at platform calibrations on Tuna-17.
- `docs/notes/quantum_inspire/shot-record-literature.md` `[R]` section 4: the candidate table for the |1> misassignment
  difference between calibration and witness circuits (drift, crosstalk, leakage, measurement-induced transitions) with the
  measurement that tests each; it states that no registered source gives a Tuna-17 drift rate.

## Statistical sources

| Source | Repository, path, manifest sha256 | Tag and locator | Bears on and predicts |
|---|---|---|---|
| DeGroot and Schervish, *Probability and Statistics*, 4th ed. | private, `statistics/inference/degroot_schervish_2012_probability_and_statistics_4th_ed.pdf`, `89a9c7538df5945fda47a93c8d1b820fcf29de69ff9781ea044022c2eadbd470` (transcription `.md`, `9c453054629a52f56e8fc202589b6e45605f35e3c6ed575dca67ad27263c7d67`) | `[S]` transcription PDF pp. 662 to 663 (book pp. 647 to 648), section 10.4 "Tests of Homogeneity" | tuna-b0. The chi-square test of homogeneity compares R samples against one common distribution with (R - 1)(C - 1) degrees of freedom. The claim's two-replicate gate is its one-degree-of-freedom case on a derived contrast: 34.86 exceeds the 0.001 quantile 10.83 (p about 3.5e-9, about 2.8e-8 after Bonferroni over the 8 replicate comparisons, computed here). The three-block bound 9.21 is the 0.99 quantile at two degrees of freedom. The book tests count tables; a test on a delta-method contrast is the same family and has no section of its own in the library |
| Efron, Tweedie's formula and selection bias | private, `statistics/inference/efron-2011-tweedie-formula.pdf`, `af27a444711d8d8c775ff8e6e3a19f7af32efe003fdb6ea9014af9782f2754c9` | `[S]` PDF p. 1 (abstract); note `docs/notes/papers/efron-2011-tweedie-formula.md` | 32-dim. The most extreme estimates of a set overestimate their expectations (winner's curse). The out-of-sample test of the local-channel bias (2.073 +- 0.010 over 9 of 10 and 3.096 +- 0.011 over 7 of 8 placements) excludes the two largest departures after inspection; the retained mean is then pulled toward the model by construction. Report both means and fix the exclusion rule beforehand |
| Weinstein and Yekutieli, sign-determining confidence intervals with FCR control (arXiv 1404.7403) | private, `statistics/inference/1404.7403v4.pdf`, `a5838b78b02b80381412129a79eeae685d34ff34c9ecec22791bc611f2287530` | `[S]` PDF p. 1 (abstract) | fez-null. The per-bin sign-resolution rule makes 128 simultaneous directional decisions per operand; the source supplies a procedure that controls the expected share of wrong signs. It predicts no hardware effect. Which bin fails the ibm_fez 127-of-128 sign rule was not confirmed; `nhat-bias/README.md` records one N_b = 3 block of o128 (block k8, placement 2) whose single minus bin reads -0.002 |
| Holm 1979 and Abdi 2007 | private, `statistics/inference/holm_1979_sequentially_rejective_multiple_test_procedure.pdf` (`4317a0d1555dad949dc1760605d925ba20037402827741fdf99cd8ea37e80c46`), `statistics/inference/abdi_2007_bonferroni_sidak_corrections.pdf` (`243227b8fc609e69791bff6909b1bd18a9b160110202ec4c6c4517d3ce6c951c`) | held, not opened for this review | multiplicity of the 23 preregistered rules and the 8 replicate comparisons; the tuna-b0 failure survives Bonferroni (above) |
| Demortier, p values and nuisance parameters; Cowan et al., asymptotic formulae (arXiv 1007.1727) | private, `statistics/inference/demortier_2008_p_values_nuisance_parameters.pdf` (`84516b1850359bd874f66bf0e6e765f63752891bf440cb94bfb734e59f32dde9`), `statistics/inference/1007.1727v3.pdf` (`618783cfea3355b83423609bde70a4b085762353ffc4386cda2621de295df6dd`) | `[S]` abstracts only (PDF p. 1) | systematic-error budget. Both treat systematic uncertainty as nuisance parameters in the test (profile likelihood, Wilks and Wald asymptotics). The claims bound a per-block offset of -0.03 and a q11 shift as hypotheses outside the interval; a budget would profile them. Content below the abstracts was not read |
| Howard et al., time-uniform confidence sequences (arXiv 1810.08240) | private, `statistics/inference/1810.08240v9.pdf`, `eb3efd547349adfbff25514ae0854c142cd29b96b398be38c9000d69a2f64ca8` | `[S]` PDF p. 1 (abstract) | the 19-batch Tuna series is a sequential acquisition with an optional-stopping rule; a confidence sequence stays valid when the stopping time depends on the data. Not read beyond the abstract |
| Riley, *Handbook of Frequency Stability Analysis* (NIST SP 1065) | private, `engineering/signal-processing/riley-2008-nist-sp-1065.pdf`, `ee6bb84554683d718638717651c75f7d487af9e04c168880760ae41a485eb52f` | `[S]` table of contents (PDF pp. 5 to 6): sigma-tau plots and the Allan variance (section 5.2.2) | method for the time scale. An Allan deviation of the per-batch selector contrast and of q11's misassignment against the separation of the batches distinguishes white noise (slope -1/2), flicker and random walk, and gives the averaging time of minimum variance. Chapter bodies were not read |

## 32-dimensional analyses

`docs/notes/topics/a5-hardware-algebra-synthesis.md` and `nhat-bias/README.md` carry the observations below. Each pairs with
the literature above.

- **Device ordering across runs.** The non-flat all-aligned blocks have a Fisher-combined p of 1e-6 and 2e-6 on the two
  ibm_fez runs, 0.0018 on ibm_marrakesh and 0.26 on ibm_kingston, and the 11-07 wide run again fails only on ibm_fez.
  A defect that persists over runs a day apart on one device favors a slowly varying property of that chip over minute-scale
  switching, which Klimov, Thorbeck and Schloer all permit (minutes to days). Bravyi's correlated-readout residual is a property of the chip's readout
  multiplexing and would persist across runs as well, so the device ordering alone does not separate TLS defects from
  correlated readout.
- **N_b = 2 bias of the local channel.** Fitted per-bit flip 0.020 to 0.023 against a recorded readout flip of 0.012 to
  0.018, an excess of 0.005 to 0.009. Geller (preparation error inside the confusion matrix) and Thorbeck (lifetime loss
  during readout, which the confusion matrix measured outside the circuit lacks) each predict an excess of this sign
  and neither predicts its size.
- **Leakage into the zero character that reverses under output relabeling** (-0.004 and -0.002 on the relabeled null
  copies). It favors relaxation or readout asymmetry toward physical outcome 0; Klimov's TLS decay and Thorbeck's
  readout-time lifetime loss both act that way, Sank's measurement-induced transitions act at high photon number only.
- **Ratio-estimator instability.** The nullity-4 operand e1 + e26 reads N_hat 10.04 from the replica-mean contrasts and 34.09 as the
  mean of per-replica readings, because V_hat approaches zero on single replicas. No document in the workspace covers intervals for a ratio of two estimated quantities;
  the searches for Fieller and for Cochran returned no text.
- **Hypotheses formed after the data** (the orientation-qubit character ordering) carry Efron's warning on selection after
  inspection; the repository's own falsifier is a full-map rerun with the orientation phase on another data qubit.
- **Tuna null offset** +0.0164 against IBM's pooled -0.0015 +- 0.0014 rad over-rotation: Rol (flux-offset sensitivity of
  the CZ phase) supplies the Tuna-specific mechanism candidate; no source gives its size for Tuna-17.

## Present, absent and gaps

- **Present.** Every entry above has its file in the documents repository named, and the manifest sha256 of each was
  recomputed from the file and equals the manifest row for every manifest sha256 in this file; the two hashes of web sources
  (the IBM guide and the Thorbeck HTML rendering) are registry values, not manifest rows.
- **Cited but absent.** `WORKS-WANTED.md` at the workspace root lists five hand-curated works (Freudenthal 1951, Kok and
  Lovett, Gerry and Knight, Bachor and Ralph, Michler) and four references of Feigin and Fuchs 1988; none concerns drift,
  readout, crosstalk, TLS, heterogeneity or systematics. `gororoba-infrastructure` `docs/library/owner-fetch-list.md` line 756
  lists the Zenodo dataset and analysis code of Proctor et al. (`10.5281/zenodo.4033077`) as unobtained; the paper itself
  is held. No held document names a Tuna-17 drift rate, resonator parameters or shielding.
- **Registry gap.** Thorbeck (2305.10508) has a manifest row in gororoba-documents-private, is registered in
  `docs/SOURCES.json` by its HTML rendering only, and has no row in `docs/sources/reading-copy-locations.tsv`. The
  gap blocks `scripts/source_reading_copies.py --locate` from resolving its PDF.
- **No document held for.** a TLS review article; a text on Cochran Q or random-effects heterogeneity (the repository applies
  a DerSimonian-Laird estimate in the atlas-fringe analysis according to
  `docs/archive/reviews/pr-149-jax-bridge-and-atlas-fringe.md`, which cites no text for it; the script was not opened);
  Fieller intervals; a dedicated treatment of postselection or heralding bias (the nearest holdings are Efron on selection
  and the exact bias identity in `nhat-bias/README.md`, claim 1); a calibration-drift time series for IBM Heron.
  Searches by name or phrase ("batch effect", "Cochran", "DerSimonian", "Fieller", "winner's curse") over the notes, the
  public documents and the private physics and statistics folders returned no other hit.

## Tests the literature implies

1. Interleave the replicates of b0 with the 6-CZ blocks in one batch and read q11's misassignment before and after each
   (Sarovar pp. 15 to 16; Proctor p. 7 through its note). A rerun whose b0 replicates still disagree with q11 steady falsifies the q11
   reading, as the claim states.
2. Read the layouts of the 6-CZ blocks for a data bit on qubit 11. If they use it and agree across 3.6 to 9.5 hours, the q11
   reading weakens and the CZ-count reading (Rol) gains.
3. Compute an Allan deviation of per-batch q11 misassignment and b0 contrast (Riley section 5.2.2) from the retained
   readout circuits.
4. Rerun ibm_fez with the block of placement 7 on other qubits (the claim's own falsifier) and compare the calibration
   snapshot at that time (IBM guide; check 3).
5. Calibrate qubit 90 independently of the execution-time snapshot (resolved part of check 4: the routed writer map
   shows every qubit-90 marginal inside its recorded channel, so only an independent calibration can test the 0.835
   flip).
6. Report the local-channel out-of-sample test with and without the two excluded placements (Efron).
