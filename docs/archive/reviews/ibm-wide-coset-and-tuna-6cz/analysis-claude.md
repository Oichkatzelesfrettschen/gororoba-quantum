# Setting-by-setting analysis of the wide-coset pair against the retained parallel-coset pair

Inputs:
- `results/live/pathion_wide_coset_analysis.json`, with its collect records
  `results/live/2026-11-07T153325.440007Z` (ibm_fez) and `...886771Z` (ibm_kingston);
- the retained claim `hw-ibm-pathion-parallel-coset` in `docs/state/research_state.json`;
- the literature report [literature-drift-systematics.md](literature-drift-systematics.md).

Every number below is read from those records by the commands in this file's commit; the class of each statement is
marked.

## ibm_fez qubit 90: an extreme execution-time readout channel that the data admit

- **Measured.** The per-PUB execution-time calibration stored in fez's `collect.json` (`pub_calibration`, field
  `placed_qubit_calibration`) gives qubit 90 `prob_meas0_prep1 = 0.835`, `prob_meas1_prep0 = 0.0`. The
  submission-time `record.json` gives 0.0039.
- **Computed.** That channel admits a measured P(1) from 0 to 0.165. The routed circuit `isa.qpy` maps qubit 90 to a
  different classical bit in different PUBs: in `pub_02` qubit 90 writes `g0_r2_c[1]` and qubit 89 writes
  `g0_r2_c[3]`. The raw `pub_02` marginals are P(1) = 0.083 on bit 1 (qubit 90) and 0.919 on bit 3 (qubit 89), and all
  twelve mapped qubit-90 marginals lie between 0.048 and 0.119. Every qubit-90 marginal is compatible with its
  recorded channel. An earlier version of this file joined the 0.919 bit to qubit 90 and called the channel
  contradicted; the routed writer map refutes that reading (review-codex-round2.md).
- **Proved from the code.** `live_run.readout_factors` builds the classical-bit-to-physical-qubit writer map from each
  ISA circuit, and `scripts/pathion_wide_coset_analysis.py` selects one writer map per PUB, so the correction inverts
  qubit 90's channel on qubit 90's bit. Qubit 90 sits in fez placement 2 (qubits 89, 78, 88, 90).
- **Computed.** The ill-conditioned 0.835 inverse inflates placement 2's standard error 7 to 8 times against kingston's
  placement 2: 0.068 against 0.008 (n64), and 0.066 against 0.008 (n128). The n64 operand runs two copies of each block
  and `block_weights` averages them, so placement 2 enters the n64 decision total with weight 1/2: its contribution is
  -0.057 of -0.531. Without it the total reads -0.474, and with the placement-10 twin in its place -0.505, both outside
  the +-0.4 null band. At n128 placement 2 has weight 1, and the total moves from -1.056 to -0.988, outside the +-0.8
  band. The fez null-control failures and every verdict stand.
- **Open.** The data falsify no part of the 0.835 channel. Whether it describes the device or a calibration artifact
  needs an independent calibration of qubit 90; the correction of placement 2 is highly sensitive to it.

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
  inverse. Drift between the PUBs of one 10 to 11 s job lies outside the shot covariance and is unmeasured: Klimov's diffusion scale (0.26 MHz rms in 10 s on another device) is an empirical stochastic scale beside telegraphic jumps of up to about 60 MHz, not a bound. Falsifier: a correlated
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
