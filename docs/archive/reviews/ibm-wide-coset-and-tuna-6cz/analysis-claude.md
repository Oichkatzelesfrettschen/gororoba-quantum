# Setting-by-setting analysis of the wide-coset pair against the retained parallel-coset pair

Inputs:
- `results/live/pathion_wide_coset_analysis.json`, with its collect records
  `results/live/2026-11-07T153325.440007Z` (ibm_fez) and `...886771Z` (ibm_kingston);
- the retained claim `hw-ibm-pathion-parallel-coset` in `docs/state/research_state.json`;
- the literature report [literature-drift-systematics.md](literature-drift-systematics.md).

Every number below is read from those records by the commands in this file's commit; the class of each statement is
marked.

## ibm_fez qubit 90: a broken execution-time readout calibration enters the correction

- **Measured.** The per-PUB execution-time calibration stored in fez's `collect.json` (`pub_calibration`, field
  `placed_qubit_calibration`) gives qubit 90 `prob_meas0_prep1 = 0.835`, `prob_meas1_prep0 = 0.0`. The
  submission-time `record.json` gives 0.0039.
- **Computed.** That channel can emit P(1) of at most 0.165, while qubit 90's raw register bit reads a marginal P(1)
  of 0.919 (literature report, record checks). The snapshot is inconsistent with the data it corrects.
- **Proved from the code.** `live_run.corrected_summary` passes each entry's execution-time properties
  (`props_by_name`) to `readout_inverse`/`readout_corrected` (`gororoba_quantum/live_run.py:2840-2858,7323-7326`), so
  the 0.835 channel was inverted. Qubit 90 sits in fez placement 2 (qubits 89, 78, 88, 90).
- **Computed.** Placement 2's standard error is inflated 7 to 8 times against kingston's placement 2: 0.068 against
  0.008 (n64), and 0.066 against 0.008 (n128). Its share of the fez null failures is small: the n64 and n128 null
  totals are -1.062 and -1.056 with placement 2, and -0.949 and -0.988 without it. The fez null-control failures
  therefore stand without qubit 90, and the claim's verdicts are unchanged.
- **Finding.** The collector applies an execution-time readout channel without checking that it can produce the
  observed marginals. A gate that refuses a correction whose channel cannot emit the measured marginal (here
  0.919 > 1 - 0.835), falling back to the submission-time calibration or withholding that bit's correction, would
  have caught it. This is a follow-up change to `live_run.py`, outside this claims branch.

## Settings compared

| setting | parallel-coset pair (retained) | wide-coset pair |
|---|---|---|
| operand dimension | two-term operands at D = 32 | whole operands at D = 64 and 128 |
| placements | fez 17, kingston 16 | fez 17, kingston 16 |
| shots per member or PUB | fez 16,384, kingston 8,192 | fez 18,816, kingston 21,888 |
| readout correction | tensor-product inverse of the calibrated confusion matrix | the same, execution-time per-PUB calibration |
| kingston null offset | 1-CZ null N_hat -0.028 to -0.031, fails its rule | per-block offset about -0.030 and -0.033, inside the wide rule's band |
| fez null offset | unresolved | fails both null controls (n64, n128) |
| integer readings | within 0.15 of the integer nullity on both devices | kingston 27.995 / 60.126; fez 28.071 / 59.978 |

- **Measured.** Kingston carries a negative per-block null offset of about -0.03 in both runs, on different
  operands and shot counts.
- **Hypothesis.** The offset is a device-level systematic of the tensor-product readout correction rather than drift.
  The parallel claim's boundary already records that the calibrated confusion matrix overstates the in-circuit
  asymmetry by about 0.09. Bravyi et al. (literature report) predict a correlated residual after a tensor-product
  inverse. Klimov's defect diffusion bounds drift within one 10 to 11 s job as small. Falsifier: a correlated
  (two-qubit) readout calibration that leaves the -0.03 offset unchanged, or a third kingston run whose offset differs
  beyond its standard error.
- **Measured.** Fez's null behavior differs between the two runs: unresolved in the parallel pair, failing in the
  wide pair.
- **Hypothesis.** The cause is calibration state, through the qubit-specific losses (placements 7 and 15, and qubit 11
  worst in T1 and T2 in the fez snapshot), not the operand dimension. Falsifier: a repeat on fez's best placements
  that still fails the null rules.

## Tuna 6-CZ replicates

- **Measured.** The two b0 base replicates are the first and last batches, 13.5 h apart. The 12.1 h b0 twin pair
  passes, and the failing pair is the only 21-CZ pair.
- **Hypothesis.** Time blocking (Sarovar) together with qubit-11 readout switching (0.362, 0.039, 0.095, 0.434 across
  batches; Thorbeck) explains the replicate split. Elapsed time alone does not. Falsifier: interleaved b0 and 6-CZ
  replicates with q11 readout brackets that still split.
