# Written case: pathion kernel map (pkm)

Status: awaiting the owner's approval. Nothing is submitted until the owner approves this case; the binding dry run
and `--submit` then run back to back through `scripts/approved_run.sh` with `scripts/pathion_kernel_map_check.py`
as its check, which re-plans on the calibration in force and admits the fresh plan only inside this case's bounds.

## What it measures

The pair-resolved kernel map of two-term operands e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5
(`gororoba_quantum/pathion_kernel_map.py`, group `pathion_kernel_map`, 23 six-qubit circuits from 12 templates). Each
circuit prepares a uniform superposition over all 32 basis states, applies a diagonal oracle that orients the 16 XOR
pairs {k, k XOR (i XOR j)} by the sign of their lower member, and runs one compiled A_5 SELECT inside a fixed-operand
linear combination of unitaries; the upper-member signs enter only through the compiled SELECT. The two orientations
differ by a phase pi on one data qubit before the SELECT, so they are one parametrized circuit with identical routing.
The ideal selector contrast between them is N/16, with N the nullity of L_(e_i + t e_j); every one of the 32 output
bins carries an ideal per-output contrast of +1 or -1, so the joint readout is a sign map of the compiled operator, and
the per-circuit estimate N_hat = (half the sum of the per-output contrasts) / (their signed mean against the ideal
signs) returns N under any contraction toward the uniform law, whatever visibility the circuit has.

Nullity is python-flint exact rank, equal to the aligned-pair count, and hypercomplex, hyprat and hypercomplex-engine
agree with cd_core on all 1024 basis pairs and on every operand's nullity
(`docs/evidence/pathion-kernel-map/packages.json`).

Members: operands of nullity 0 (e1 + e17), 4 (e1 + e26; e2 + e27), 8 (e1 + e10), 12 (e1 + e18; e1 + e24), each in two
orientations; the quarter-turn twins e17 - e10 and e17 - e2 (disjoint support, Gram operator of e1 + e26 and
e1 + e18 by Moreno, math/0512517, Corollary 2.4); the cocycle-free SELECT on e1 + e10 and e1 + e18 (ideal half-sums
-6 and -2); e1 + e18 with one SELECT sign negated at input 3 inside the SELECT diagonal (ideal half-sum 11); and the
selector-disconnected skeleton (ideal P(s = 0) = 1).

## Why a noise simulation cannot answer it

The ideal values are exact and Statevector confirms every one (`tests/gororoba_quantum/test_pathion_kernel_map.py`);
the question is the device's. Two predictions of the retained visibility disagree by more than a factor of two:

- Model branch: the calibrated noise model of ibm_fez in this record predicts per-circuit visibilities 0.49 to 0.58
  (replica intervals 0.43 to 0.64) at 136 to 167 routed CZ.
- Compounded-excess branch (hypothesis: the excess infidelity of the retained 16-dimensional Kingston witness,
  visibility 0.678 measured against 0.856 from its same-day calibrated model at 42 CZ, a factor 0.792 per 42 CZ,
  `results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md`, transfers to ibm_fez and compounds per routed CZ): 0.20 to 0.27.

N_hat cancels either visibility; an N_hat that departs from N beyond the model's own bias, a per-output sign that
departs from the ideal, or a twin that reads differently from its primary is a property of the device's realization of
the A_5 sign network that the calibrated model does not contain. Five disjoint replicas map the result across the chip.

## Backend, shots, seconds

- Account: `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` (103 s remaining on 2026-11-06 at 17:21 UTC) for the
  dry run, the submit and the collect.
- Backend: chosen afresh by the binding dry run among ibm_fez, ibm_kingston and ibm_marrakesh, excluding ibm_fez
  qubits 2-4 and 16 and ibm_kingston qubits 0-4 and 16 as the retained zdac case did; this record chose ibm_fez with
  five replicas at replica floor 0.7 (qubits 24-26, 37, 44, 45; 123, 124, 136, 142-144; 78, 87-90, 97;
  96, 103-106, 117; 50-52, 58, 70, 71).
- Shots: 16,384 per circuit, repetition delay 20 us, one job of 24 PUBs.
- Expected seconds: 14.8 (2 + shots x (rep_delay + scheduled duration) over the 24 PUBs); ceiling 30 s per job and in
  total, reserve 20 s.
- Credits: IBM Open plan quantum seconds only.

## Preregistered readout and decision rules

Every rule uses the replica interval of the record (`summary_interval`, Student t over replicas), never a pooled shot
error, because between-replica variance exceeds the shot variance in the dry run.

1. Resolution. Each operand with N >= 4 has a visibility interval above zero, and the pooled per-output map agrees
   with the ideal sign on at least 31 of 32 bins. Failure refutes "the device resolves this operand's A_5 kernel map at
   this depth".
2. Nullity on hardware, the primary readout. Each N_hat interval covers its model-branch value from this record
   (0.25, 4.26, 4.28, 8.37, 12.37, 12.57 for nullity 0, 4, 4, 8, 12, 12) within plus or minus 1, the model's own bias
   against N being +0.25 to +0.57 from readout asymmetry (hypothesis-level, so the readout-corrected N_hat of
   `summary_readout_corrected` is a preregistered cross-check). An N_hat outside that band refutes the compiled sign
   network's agreement with cd_core at that operand.
3. Differences, where a common bias cancels. The flipped arm's N_hat lies below the unflipped e1 + e18's by 1
   (model: 11.50 against 12.37); each `twin_nullity_difference` interval contains zero (model: -0.35 [-0.75, 0.06]
   and -0.04 [-0.42, 0.34]); the cocycle-free N_hat values are negative (model -6.36 and -2.14).
4. Ratios, secondary. `nullity_ratio_12_over_4` and `strut9_ratio_e1e24_over_e2e27` lie in [2.5, 3.5],
   `nullity_ratio_8_over_4` in [1.6, 2.4]; these depend on equal visibility across operands, which routed-CZ
   differences of up to 31 break, so rule 2 governs where they disagree.
5. Depth scaling. The pooled visibility against routed CZ decides between the model branch (0.49 to 0.58) and the
   compounded-excess branch (0.20 to 0.27); a visibility outside both refutes both models of the excess.
6. Nulls. The e1 + e17 N_hat interval covers 0.25 within plus or minus 1; `skeleton_p0` reads one minus the
   selector's readout error.

Power at the compounded-excess branch is hypothesis-level: N_hat's replica interval scales roughly as one over the
visibility, from about +-0.15 to +-0.25 at the model branch to about +-0.4 to +-0.7, which keeps rules 1 and 2 decided
and leaves the one-unit flip difference of rule 3 near two to three replica standard errors.

## Cross-platform prediction

The map is the union of its coset blocks: restricted to the 8 output bins of one coset of a subgroup V containing
i XOR j, the measured c(y) divided by the circuit's visibility predicts a Tuna-17 coset-block run of the same operand;
that comparison is preregistered for any later Tuna-17 case.

## Command

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_kernel_map_check.py' -- --groups pathion_kernel_map \
      --shots 16384 --rep-delay 2e-5 --replica-floor 0.7 \
      --exclude-qubits ibm_fez:2-4,16 --exclude-qubits ibm_kingston:0-4,16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#3 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#4 \
      --max-total-execution-seconds 30 --max-execution-seconds 30 --reserve-seconds 20 \
      --min-remaining-seconds 20 --max-pending 100 --out ../results/live

The check admits a plan only when both orientations of every operand route to the same CZ count, no replica touches
the excluded qubits, at least five replicas are placed, and the estimated charge is at most 30 s.

Seeds: draw `docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json`, index 3 (seed_transpiler) and index 4
(seed_simulator); indices 0 to 2 seeded the exploratory census and cost checks.

## Optional replication

The same flags with `--backends ibm_marrakesh` on the primary account (68 s remaining, reserve 20 s) repeat the map on
a second Heron r2 device, so the depth-scaling and N_hat verdicts become device-to-device comparisons; about 15 s.
