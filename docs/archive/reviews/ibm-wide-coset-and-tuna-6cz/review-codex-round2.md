# Second Codex adversarial review: wide cosets and Tuna-17 six-CZ write-up

## Scope and verdict

The reviewed artifacts are scientific reconciliation and literature prose over retained IBM Heron r2 and Quantum
Inspire records, plus the 64D/128D implication table. The review read all four named targets, the first Codex review,
the routed circuits, the raw IBM bitstrings, both IBM analysis records, the rule-producing source, and all five tier-one
PDFs. The fields are statistical hardware evidence, readout mitigation, reproducibility and finite algebraic computation.

The write-up fails this round. The claimed contradiction between ibm_fez qubit 90's execution-time channel and a raw
P(1) of 0.919 assigns the marginal to the wrong physical qubit. The routed circuit maps physical qubit 89, not qubit
90, to the bit whose P(1) is 0.919 in that PUB. Every actual qubit-90 marginal is compatible with its recorded channel.
The registered wide-coset and Tuna-17 verdicts survive, as do the 64D/128D evidence classes, but the qubit-90 finding
and every reconciliation sentence that adopts it require withdrawal.

## Findings, ranked by consequence

### FATAL, computed and proved from the routed circuit: the 0.919 marginal is not qubit 90

The write-up treats placement 2 as if its classical-bit roles stayed fixed across PUBs
(`literature-drift-systematics.md:58-70`; `analysis-claude.md:12-29`). The retained ISA says otherwise. A Qiskit 2.6.2
probe loaded `isa.qpy`, followed every `measure` instruction, and joined each physical writer to the corresponding raw
register bit. The decisive output is:

```text
pub_00 q90 -> g0_r2_c[3], P(1)=1488/18816=0.079081633
pub_01 q90 -> g0_r2_c[3], P(1)=1549/18816=0.082323554
pub_02 q90 -> g0_r2_c[1], P(1)=1564/18816=0.083120748
pub_02 g0_r2_c[3] writer -> physical qubit 89, P(1)=17294/18816=0.919111395
all 12 actual q90 marginals: 0.048044218 <= P(1) <= 0.118622449
```

The execution-time record gives qubit 90 `prob_meas1_prep0 = 0` and `prob_meas0_prep1 = 0.8349609375`
(`collect.json:555-560`), so its channel permits measured P(1) from 0 through 0.1650390625. Every mapped qubit-90
marginal lies inside that range. Qubit 89, the writer of the 0.919 bit, instead has `prob_meas0_prep1 = 0.017578125`.

The implementation already follows the routed map correctly. `live_run.readout_factors` builds the clbit-to-physical-
qubit writer map from each ISA circuit (`gororoba_quantum/live_run.py:2775-2789`), and the retained analyzer builds one
writer map per PUB and selects it through `executed["pub"]` (`scripts/pathion_wide_coset_analysis.py:70-80,162-177`).
The 0.835 inverse is ill-conditioned and inflates placement 2's uncertainty, but the raw data do not prove that the
calibration is broken. Remedy: remove the contradiction, the fallback proposal and the reconciliation row; retain only
the measured calibration discontinuity and correction-sensitivity observation unless an actual mapped marginal or an
independent calibration falsifies the channel.

### SERIOUS, source-checked and computed: the literature turns a stochastic scale into a false bound

Klimov PDF p. 3 states `sigma(t) = 2 D sqrt(t)` with `D = 2.5 +/- 0.1 MHz / sqrt(hour)`. The report drops the factor of
two at `literature-drift-systematics.md:94-103`. Direct evaluation gives 2.50 MHz at 15 minutes, 5.00 MHz at one hour,
18.371 MHz at 13.5 hours and 0.2635 MHz at 10 seconds, rather than 1.25, 2.5, 9.2 and 0.13 MHz.

The same source reports telegraphic jumps up to about 60 MHz (PDF p. 4) and describes a tunable Xmon rather than either
device under review. An empirical root-time standard deviation is not a deterministic upper bound. The statements that
Klimov "bounds drift" inside a job (`analysis-claude.md:45-50`) and that a shared calibration plus the Klimov arithmetic
bounds between-PUB drift small (`literature-drift-systematics.md:79-83`) are unsupported. The first review states the
defensible boundary: inter-PUB drift is outside the shot covariance, and the records contain no spectroscopy or time
series (`review-codex.md:150-157`). Remedy: correct the arithmetic and describe the numbers as other-device stochastic
scales; preserve inter-PUB drift as an unmeasured alternative.

### SLOPPY, computed: placement 2 is not a -0.113 contribution to the n64 decision total

The n64 operand runs two copies of each block. `block_weights` averages the copies before summing blocks
(`scripts/pathion_wide_coset_analysis.py:277-282,305-340`). Placement 2 reads -0.113067, but its decision weight is 1/2,
so its contribution to the retained n64 total is -0.0565335, not -0.113. The retained decision total is -0.530953, not
-1.062 (`pathion_wide_coset_analysis.json:950,1665`). The -1.062 number is the unweighted sum of all 16 placement
readings and is not the preregistered whole-operand statistic.

The conclusion survives the arithmetic repair. Removing placement 2's weighted term gives -0.4744195, outside the
+/-0.4 null band. Replacing the affected k8 copy by its placement-10 twin gives -0.5048615, also outside the band. At
n128, placement 2 has weight one: -1.055987 - (-0.067553) = -0.988434, outside the +/-0.8 band
(`pathion_wide_coset_analysis.json:820,1647`). The corresponding target-minus-null means remain beyond their 0.5 and
0.8 bands even before adding uncertainty. Remedy: report the actual decision weights and totals. The fez null and
difference failures still stand, and every verdict remains unchanged.

### SLOPPY, documented: the reconciliation overstates source inspection

`README.md:9-11` says the documents-repository sources were each opened at the cited page. The literature report itself
defines `[N]` as note-only (`literature-drift-systematics.md:7-12`), marks Heinsoo, Rudinger, Seif and Niu `[N]`
(`literature-drift-systematics.md:255-266,295-310`), and says Holm and Abdi were held but not opened
(`literature-drift-systematics.md:329-339`). Remedy: say that the report distinguishes source-opened, note-only and
unopened holdings; reserve the all-pages-opened statement for the five tier-one sources.

## Five-source literature audit

All five local PDF hashes match the report. The page checks produced the following results:

| source | pages opened | result |
|---|---:|---|
| Klimov, arXiv:1809.01043 | 2-5, 9, 13, 21 | Locators match; the report's diffusion arithmetic and deterministic-bound inference fail as described above. |
| Thorbeck, arXiv:2305.10508 | 1, 3 | Anti-Zeno broadening, TLS hot spots and the nine-minute repeat match. Mapping that mechanism to one unchanged assignment channel remains a hypothesis, not a source result. |
| Sarovar, arXiv:1908.09855 | 14-16 | The time-setting confound, two-state-fluctuator example, and raster/random-order remedy match. |
| Proctor, arXiv:1907.13608 | 1-3, 11-12 | Ubiquitous instability, chi-square Fourier powers, strong family-wise control and sample-window limits match. |
| van der Schoot, arXiv:2310.01120 | 7, 9, 11-12 | Drift, excess readout-fidelity variance, 4,096-shot T2* points and the instability conclusion match. A "platform-typical rate" of chi-square failure is not estimated by the paper. |

### SOUND, measured and hypothesis: the kingston offset recurs and has a usable falsifier

The parallel run gives corrected per-placement null readings -0.028279, -0.031266 and -0.029704
(`pathion_parallel_coset_analysis.json:1256-1317`). The wide run gives -0.238101 / 8 = -0.0297626 per n64 block and
-0.533889 / 16 = -0.0333681 per n128 block (`pathion_wide_coset_analysis.json:3273,3291`). The recurrence claim is
measured. A matched correlated readout calibration that leaves the offset unchanged can falsify the proposed
tensor-product-residual mechanism. A third run outside the earlier standard errors tests repeatability and drift, but it
does not uniquely test correlated readout. Bravyi PDF pp. 7-8 establishes that tensor-product mitigation can leave
correlated residuals; the literature report correctly notes that the reported positive high-weight bias does not predict
the negative null offsets (`literature-drift-systematics.md:198-210`). The mechanism therefore remains a hypothesis.

### SOUND, computed and proved: the reconciliation verdicts and 64D/128D evidence classes otherwise hold

The reconciliation accurately carries the first review's record equality, 23/23 and eight-failure rule counts,
case-specific difference arithmetic, Tuna-17 `unresolved_batch` decision, finite-census classification, paper-proof versus
Rocq-proof boundary and non-byte-stable Tuna regeneration (`review-codex.md:10-16,20-118`). The added qubit-90 row is the
exception and must be removed. The 64D/128D implication table keeps the finite censuses computed, half-fold doubling
proved, mixed-pair recurrence paper-proved and open in Rocq, hardware readings measured, and scheme carry-over and
weighted four-term transfer explicitly hypothetical (`docs/evidence/pathion-kernel-map/README.md:62-115`). No second
claim falsifier arises from that subsection.

## Steelman and final verdict

The strongest defensible write-up says that the registered hardware decisions reproduce their retained records;
kingston shows a repeated negative per-block offset whose mechanism remains open; fez's placement-2 correction is highly
sensitive to an extreme execution-time channel; and the literature supplies mechanism candidates and better experimental
designs rather than device-specific causal identification. The write-up separates most measurements, computations,
proofs and hypotheses well.

The core claim verdicts remain sound, but the new calibration centerpiece is false because it joins a raw classical bit
to the wrong physical writer. The literature also understates Klimov's scale by two and calls an empirical stochastic
scale a bound. Trust requires a per-PUB routed writer join for every calibration/data comparison, corrected diffusion
arithmetic, and prose that leaves unmeasured drift open. Until those repairs land, the reconciliation does not earn its
claim that nothing overstates.
