# Written case: pathion kernel map (pkm)

Status: awaiting the owner's approval. Nothing is submitted until the owner approves this case; the binding dry run
and `--submit` then run back to back through `scripts/approved_run.sh`, which plans afresh on the calibration in force
and submits the identical flags.

## What it measures

The pair-resolved kernel map of two-term operands e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5
(`gororoba_quantum/pathion_kernel_map.py`, group `pathion_kernel_map`, 23 six-qubit circuits). Each circuit prepares
a uniform superposition over all 32 basis states, applies a diagonal orientation oracle that writes the sign of one
member of each of the 16 XOR pairs {k, k XOR (i XOR j)}, and runs one compiled A_5 SELECT inside a fixed-operand
linear combination of unitaries; the upper-member signs enter only through the compiled SELECT. The ideal selector
contrast between the two oracle orientations is N/16, with N the nullity of L_(e_i + t e_j) (python-flint exact rank,
equal to the aligned-pair count; three Cayley-Dickson packages agree with cd_core on all 1024 basis pairs and on every
operand's nullity, `docs/evidence/pathion-kernel-map/packages.json`). Every one of the 32 output bins carries an ideal
per-output contrast of +1 or -1, so the joint readout is a sign map of the compiled operator.

Members: operands of nullity 0 (e1 + e17), 4 (e1 + e26; e2 + e27), 8 (e1 + e10), 12 (e1 + e18; e1 + e24), each in two
orientations; the quarter-turn twins e17 - e10 and e17 - e2 (disjoint support, Gram operator of e1 + e26 and e1 + e18;
Moreno, math/0512517, Corollary 2.4); the cocycle-free SELECT on e1 + e10 and e1 + e18 (ideal contrasts -0.375 and
-0.125 against N/16 = 0.5 and 0.75); one SELECT sign negated at input 3 of e1 + e18 (P(minus) moves by 1/32); and the
selector-disconnected skeleton (ideal P(s = 0) = 1).

## Why a noise simulation cannot answer it

The ideal values are exact and Statevector confirms every one (`tests/gororoba_quantum/test_pathion_kernel_map.py`);
the question is the device's. Two predictions disagree by a factor near three, and only the hardware decides between
them: the calibrated noise model of today's ibm_fez predicts that the selector contrast retains 0.51 [0.44, 0.59] of
its ideal at 136 to 167 routed CZ, while compounding the excess infidelity measured on the retained 16-dimensional
Kingston witness (visibility 0.678 measured against 0.906 from today's FakeKingston model at 42 CZ,
`results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md`) per routed CZ predicts a retention near 0.18. A uniform
contraction of either size leaves the nullity ratios unchanged; a retention that differs between operands at equal
routed CZ, or a per-output sign pattern that departs from the ideal, is a property of the device's realization of the
A_5 sign network that a calibrated model does not contain. Six disjoint replicas map the result across the chip.

## Backend, shots, seconds

- Account: `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` (103 s remaining on 2026-11-06 at 17:21 UTC) for the
  dry run, the submit and the collect.
- Backend: chosen afresh by the binding dry run among ibm_fez, ibm_kingston and ibm_marrakesh; this record chose
  ibm_fez, six replicas at replica floor 0.7 (qubits 24-26, 37, 44, 45; 123, 124, 136, 142-144; 78, 87-90, 97;
  96, 103-106, 117; 50-52, 58, 70, 71; 0-4, 16).
- Shots: 16,384 per circuit, repetition delay 20 us, one job of 24 PUBs.
- Expected seconds: about 15 (2 + shots x (rep_delay + scheduled duration) summed over the 24 PUBs, durations 5.6 to
  23.3 us); ceiling 30 s per job and in total, reserve 20 s.
- Credits: IBM Open plan quantum seconds only.

## Preregistered readout and decision rules

Per replica and pooled over replicas (`summary`, `summary_interval` of the record):

1. Resolution. Each operand with N >= 4 shows a selector contrast above zero by five pooled standard errors, and at
   least 31 of 32 per-output signs agree with the ideal in the pooled map. Failure on an operand refutes "the device
   resolves this operand's A_5 kernel map at this depth".
2. The nullity class on hardware. `nullity_ratio_12_over_4` lies in [2.5, 3.5] and `nullity_ratio_8_over_4` in
   [1.6, 2.4]; `strut9_ratio_e1e24_over_e2e27` (equal strut constant, nullities 12 and 4) lies in [2.5, 3.5]. A
   ratio outside its band with a uniform per-operand retention refutes the compiled sign network; with a retention
   that tracks routed CZ it names the depth dependence instead (rule 5 separates the two).
3. Twins. Each `twin_difference` interval contains zero; a nonzero difference is a sign-network-dependent error
   between two compilations of one Gram operator.
4. Mutations. The cocycle-free contrasts are negative and differ from the true contrasts of the same operands by more
   than five pooled standard errors; the flipped-sign arm's P(minus) departs from the unflipped arm's in the predicted
   direction.
5. Depth scaling. Retention (`*_contrast_ratio`) against routed CZ across the operands decides between the model
   branch (0.51) and the compounded-excess branch (0.18): the branch whose interval contains the pooled retention
   survives; a retention outside both refutes both models of the excess.
6. Nulls. The N = 0 contrast interval contains zero; `skeleton_p0` reads one minus the selector's readout error.

## Command

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh -- --groups pathion_kernel_map \
      --shots 16384 --rep-delay 2e-5 --replica-floor 0.7 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#3 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#4 \
      --max-total-execution-seconds 30 --max-execution-seconds 30 --reserve-seconds 20 \
      --min-remaining-seconds 20 --max-pending 100 --out ../results/live

Seeds: draw `docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json`, index 3 (seed_transpiler) and index 4
(seed_simulator); indices 0 to 2 seeded the exploratory census and cost checks.

## Optional replication

The same flags with `--backends ibm_marrakesh` on the primary account (68 s remaining, reserve 20 s) repeat the map on
a second Heron r2 device, so the depth-scaling and nullity-ratio verdicts become device-to-device comparisons; about
15 s.
