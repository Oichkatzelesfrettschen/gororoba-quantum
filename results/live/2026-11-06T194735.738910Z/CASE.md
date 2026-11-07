# Written case: pathion coset-block map on ibm_fez and ibm_marrakesh (pcm)

Status: awaiting the owner's approval. Each run is a binding dry run and `--submit` back to back through
`scripts/approved_run.sh` with `scripts/pathion_kernel_map_check.py pathion_coset_map 8 30` as its check.

## What it measures

The pair-resolved kernel map of the six two-term A_5 operands of the retained Fez run
(`PATHION_KERNEL_MAP_FINDINGS.md`), tiled by coset blocks (`gororoba_quantum/pathion_coset_block.py`, group
`pathion_coset_map`): for each operand e_i + t e_j the subspace V spanned by m = i ^ j and the two lowest vectors that
extend it has four cosets, and each coset is a block of four XOR pairs on 3 data qubits and the selector, 16 of the 64
SELECT signs. The four blocks reproduce every per-output contrast of the six-qubit map exactly and their half-sums
total N (`pathion_coset_block.tile`, contrast gap 0 for all six operands). Each block's estimate N_hat_b is its own
half-sum over its own signed visibility, and the operand's N_hat sums its four blocks, so every block's visibility
cancels separately. Controls: the cocycle-free tiling of e1 + e18 (ideal -2), the quarter-turn twin e17 - e2 (ideal 12,
difference from e1 + e18 ideal 0), and the null e1 + e17 (ideal 0). 64 members (32 blocks x 2 orientations), each
orientation pair one parametrized circuit.

## Why a noise simulation cannot answer it

The full map lost most of its contrast at 136 to 173 routed CZ on ibm_fez (visibility 0.09 to 0.24, the calibrated
model's 0.49 to 0.58 refuted, ledger A5-179) and lost it entirely for m in {25, 27} on two placements (A5-180). The
blocks route to 1 to 20 CZ. Two predictions: the calibrated model of each device predicts block visibilities 0.84 to
0.93; compounding the excess measured on the Fez run (0.50 against 0.80 at 48 CZ, a factor 0.990 per CZ) predicts
0.70 to 0.80 at 15 to 20 CZ. The question is the device's: whether the compiled sign network matches cd_core on all 32
blocks once depth stops masking it, whether the m-dependent collapse persists at low depth, and whether ibm_fez and
ibm_marrakesh agree.

## Backends, shots, seconds

| Run | Account | Dry run | Replicas (scores) | PUBs | Estimated seconds |
|---|---|---|---|---|---|
| ibm_fez | `backup-ibm-quantum-platform` (85 s left) | `2026-11-06T194735.738910Z` | 17 (0.82 to 0.55), ibm_fez qubits 2-4 and 16 excluded | 65 | 14.2 |
| ibm_marrakesh | primary (68 s left) | `2026-11-06T194735.851653Z` | 11 (0.76 to 0.50) | 65 | 14.9 |

8,192 shots per circuit, repetition delay 20 us, replica floor 0.5, ceiling 30 s per run; total about 29 s.

## Preregistered readout and decision rules

Replica intervals (Student t over replicas) throughout.

1. Resolution: every operand's pooled map agrees with the ideal sign on at least 31 of 32 bins, and every block with a
   decided bin has a visibility interval above zero.
2. Nullity, primary readout: each operand's N_hat interval covers its model value within plus or minus 0.5 (model, Fez:
   0.10, 4.24, 4.25, 8.06, 12.04, 12.19 for nullity 0, 4, 4, 8, 12, 12; Marrakesh: 0.08, 4.27, 4.27, 8.05, 12.02,
   12.24). An operand outside its band refutes the compiled sign network's agreement with cd_core on that operand.
3. Controls: the twin difference interval contains zero; the cocycle-free N_hat lies within 0.5 of -2.
4. Depth: the pooled block visibility decides between the model (0.84 to 0.93) and the Fez-excess branch (0.70 to
   0.80); a value outside both refutes both.
5. The m-dependent collapse: blocks of m in {25, 27} keep a visibility within 0.15 of the blocks of m = 19 on every
   replica; a replica where they fall below that while m = 19 holds reproduces A5-180's defect at low depth.
6. Devices: the two backends' N_hat agree within the sum of their intervals for every operand.

## Commands

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_kernel_map_check.py pathion_coset_map 8 30' -- \
      --groups pathion_coset_map --backends ibm_fez --shots 8192 --rep-delay 2e-5 --replica-floor 0.5 \
      --exclude-qubits ibm_fez:2-4,16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#7 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#8 \
      --max-total-execution-seconds 30 --max-execution-seconds 30 --reserve-seconds 20 \
      --min-remaining-seconds 20 --max-pending 100 --out ../results/live

    GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_kernel_map_check.py pathion_coset_map 8 30' -- \
      --groups pathion_coset_map --backends ibm_marrakesh --shots 8192 --rep-delay 2e-5 --replica-floor 0.5 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#7 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-06T165145Z.json#8 \
      --max-total-execution-seconds 30 --max-execution-seconds 30 --reserve-seconds 20 \
      --min-remaining-seconds 20 --max-pending 100 --out ../results/live

The two runs ask one question on two devices with one circuit set, so they share the seed values (indices 7 and 8 of
the draw; indices 0 to 6 seeded the exploratory census, cost and ANF checks and the full-map case).
