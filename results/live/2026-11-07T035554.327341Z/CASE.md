# Written case: wide parallel coset-block map on ibm_fez and ibm_kingston

Status: awaiting the owner's approval. Each run is a binding dry run and `--submit` back to back through
`scripts/approved_run.sh` with `scripts/pathion_parallel_coset_check.py` as its check. Nothing is submitted, booked or
charged until the owner approves this case.

Source of numbers. Measured values of the retained runs come from `collect.json`
(`[1].measured_statistics` and `[1].measured`, recomputed per placement from the raw counts); the `record.json` of a run
holds the noise-model prediction that its dry run made, and this case cites it only as a prediction ("model").

## What it measures

Group `pathion_parallel_coset` (`gororoba_quantum/pathion_parallel_coset.py`; four-term circuits in
`gororoba_quantum/pathion_four_term_block.py`) holds 111 four-qubit circuits that compile onto one layout, so each of its
112 fused PUBs (111 members and live_run's isolated reference) reads one circuit on every placement at once: 17
placements on ibm_fez (68 qubits per shot) and 16 on ibm_kingston (64). Four questions, each with a decision rule below.

1. Coset-block map across placements. The 64 members of the retained `pathion_coset_map` (eight two-term operands, each
   tiled by four coset blocks, both orientation arms) give the per-block estimate N_hat and every output contrast's sign
   on each placement. The retained runs (`2026-11-06T201037.234804Z` on ibm_fez, `2026-11-06T200832.558771Z` on
   ibm_marrakesh) hold per-placement values too; this case compares each placement with that placement's model
   prediction and adds the controls below.
2. The null operand e1 + e17 (nullity 0). Measured in the retained runs, N_hat of the four coset blocks k0, k4, k8, k12 is
   +0.026, +0.011, +0.004, +0.004 on ibm_fez (operand total 0.045) and +0.029, +0.054, +0.051, +0.053 on ibm_marrakesh
   (0.187); after the pooled readout correction the values are -0.010, -0.003, -0.012, -0.013 and +0.002, +0.048, +0.044,
   +0.045. The selector contrast, which needs no estimator, reads -0.0019 +- 0.0020, -0.0036 +- 0.0022, -0.0009 +- 0.0015,
   -0.0012 +- 0.0020 on ibm_fez and -0.0003 +- 0.0033, +0.0007 +- 0.0019, -0.0002 +- 0.0022, +0.0027 +- 0.0024 on
   ibm_marrakesh (mean +- standard error over 17 and 11 placements). The model predicts a positive N_hat from readout
   asymmetry (operand total 0.096 and 0.075 in those dry runs). Open: the ibm_marrakesh blocks k4, k8, k12, which route to
   1 CZ, read +0.05 and keep +0.045 after the pooled readout correction; the 20-CZ block k0 does not. The case runs the
   null operand's four blocks on every placement and reports for each placement both the selector contrast and the
   readout-corrected N_hat. Two control families split the cause. Readout-flip twins (`cflip_*`, 16 members) carry X on
   all four qubits before the measurement; the ideal law is the base law with every outcome index complemented. Mirrored
   repeats (`crep_*`, 16 members) run each arm of a block a second time on the same template and binding, listed in
   reverse order, so the arms read +, -, ..., -, + in the member list. Both families cover the four cosets of the null
   operand and of e1 + e18 (nullity 12).
3. Four-term coset blocks (`ftb_*`, 15 members) of the two Gram spectra absent below dimension 32: B12 (spectrum 0, 0, 4,
   12; operand e1 + e10 + e20 + e31, coset 2) and C8 (spectrum 0, 1.528, 4, 10.472; operand e1 + e8 + e18 + e27, coset 5).
4. Parallel-operation crosstalk: live_run's isolated reference runs the first member, the null block k0 minus arm, alone
   on replica 0 against the same circuit inside the packed PUB.

## Design

- Two-term blocks. The block circuit of `pathion_coset_block.py` (H on 3 data qubits, a diagonal, H on the selector, a
  4-qubit diagonal, CNOT, H) with the orientation parameter bound to 0 (minus) or pi (plus). Mutation test: the
  cocycle-free tiling of e1 + e18 reads N = -2 against 12 (`cmap_xor_*`). Arms: plus and minus on the parametrized
  circuit, which route to one CZ sequence; the repeats add the second pair; the null arm is the null operand (selector
  contrast 0 per block, per-bin contrast alternating +1 and -1). cd_core certifies every operand and sign:
  `pathion_coset_block.tile` returns contrast gap 0 for each tiling, and the tests compare every block with the six-qubit
  law of `pathion_kernel_map`. The null blocks route to 20 CZ (k0) and 1 CZ (k4, k8, k12).
- Four-term blocks. A two-flat operand a0 + a1 + a2 + a3 (a0 ^ a1 ^ a2 ^ a3 = 0, all coefficients +1) is block diagonal
  over the cosets of span(a0 ^ a1, a0 ^ a2); a block is a 4 x 4 matrix B of entries +-1. The circuit is a real two-qubit
  input state on two data qubits (three Ry angles), H on a two-qubit selector, one diagonal on all four qubits, CX(s0 to
  d0), CX(s1 to d1), and H on the selector, measured on all four. The probability of selector 00 is |B psi|^2 / 16. All 16
  entries of every block of both operands equal the cd_core left multiplication (`core_block_matrix`). Arms: T the top
  Gram eigenvector (level 0.75 for B12, 0.6545 for C8), D and D2 kernel vectors (level 0; D2 exists for B12, whose kernel
  has dimension 2), F the top vector with one component negated (0.25, 0.0691), E0 and E1 basis inputs (null level 0.25
  for every block), C the cocycle-free block (every entry +1; 0 and 0), N the block with the one entry negated whose
  negation moves the level most (0.5625, 0.4523). T, D, D2, F, E0 and E1 are one parametrized circuit. Every mutated arm
  lies at least 0.10 below the true top level.
- Placement. `place_replicas` takes the best-scored placements of the group's compiled pattern, each with a one-qubit
  buffer (it blocks every replica's qubits and their neighbors). Replica floor 0.5. The quality policy (readout error above
  0.08, CZ error above 0.03, T1 or T2 below 20 us) excludes 19 qubits and 20 couplers on ibm_fez and 11 qubits and 22
  couplers on ibm_kingston at the dry runs. On ibm_fez the case also excludes qubits 2-4 and 16 (`--exclude-qubits`), the
  exclusion of the retained coset-map run, whose recorded reason the repository does not hold; with it the search returns
  17 placements and without it 16, and 17 is the count of the retained run. ibm_kingston returns 16 at floor 0.5 and at
  floor 0.3 (an exploratory dry run), and no exclusion is added to reach 17. The placements sit at replica scores 0.56 to
  0.85 (ibm_fez) and 0.72 to 0.84 (ibm_kingston). The placed qubits have median readout error 0.0100 and 0.0098, median T1
  139 and 247 us, minimum T2 29 and 34 us, and E10 minus E01 from -0.010 to 0.053 (ibm_fez) and -0.021 to 0.031
  (ibm_kingston), the spread that the odd part of the null offset follows.
- Packing judgment. Patterned replica bodies (`Member.replica_bodies`) are refused for bodies whose ideal laws differ,
  which every coset and arm does. A composite member with several blocks per replica would trade replica count for blocks
  per replica at constant block reads per execution, would put adjacent blocks without the buffer (the isolated
  reference would then test nothing about separation), and a 12-qubit member exceeds the 14-qubit local-simulation
  comfort. The case keeps one block per replica; a buffer-free packing needs a policy knob in `live_run.place_replicas`
  that does not exist, and each replica blocks 9 to 10 of the 156 qubits.

## Why a noise simulation cannot answer it

The binding dry runs simulate each placement with its live calibration (T1, T2, gate error and duration, each measured
qubit's asymmetric readout channel). The model predicts for the null operand total 0.120 (ibm_fez) and 0.131
(ibm_kingston), an odd part of 0.113 and 0.135 with placement standard deviation 0.107 and 0.120, an even part of +0.007
and -0.004 with 0.014 and 0.021, a readout-corrected value of 0.011 and -0.009, a k0 selector contrast of 0.0002 and
0.0003, and for the 1-CZ blocks N_hat 0.023 to 0.036 with selector contrast within 0.002 of zero. It predicts block
visibilities 0.83 to 0.94 where the retained runs measured 0.75 to 0.87 pooled (two-term operands, ibm_fez 0.77 to 0.87,
ibm_marrakesh 0.76 to 0.87), so the model overpredicts visibility by about 0.07. The calibrated model carries no coherent
error, no crosstalk between active neighbors, no two-level-system defect, no residual excitation from the 20 us
repetition delay and no drift. The hardware answers what the model lacks: whether the selector contrast of the null
blocks is zero (a coherent sx over-rotation makes it positive on k0), whether the even part of N_hat matches the
model's, whether the placement-to-placement spread of the odd part follows the per-qubit readout calibration, whether
packing 16 or 17 placements changes a block's law, and whether a four-term block's sign network survives at 18 to 25
routed CZ.

## Four-term feasibility verdict

A circuit exists and fits. The two retained spectra route to 18 CZ (B12) and 19 CZ (C8) for the six shared arms, 8 CZ
for the cocycle-free arm and 25 CZ for the mutated-entry arm on both devices, against 20 CZ for the deepest two-term block
and a case budget of 30. The observable is the probability of selector 00, so no outcome is postselected and no
block-encoding success probability is paid; the conditional output bins of the bright arm use the selector-00 shots,
about 75 percent of 14,336 (ibm_fez, 10,752) or of 8,192 (ibm_kingston, 6,144) for B12 and 65 percent for C8, and the
dark arms (model level 0.023 to 0.037) use the full counts for their level only. The class is kept. B12's kernel
dimension of 2 is read by two orthogonal kernel arms; C8 has kernel dimension 1.

## Backends, shots, seconds

Billed seconds follow charge = 2.3 + executions x (rep_delay + planner bound + residual), the residual measured on
retained 20 us static jobs. The formula 2 + shots x (rep_delay + duration) with the planner's duration alone underprices
them:

| Retained job | Executions | Planner estimate | Billed | Residual per execution |
|---|---:|---:|---:|---:|
| ibm_fez coset map (`2026-11-06T201037.234804Z`) | 532,480 | 14.2 s | 18 s | 6.6 to 7.1 us |
| ibm_fez kernel map (`2026-11-06T183538.809814Z`) | 393,216 | 14.8 s | 18 s | 7.4 to 8.2 us |
| ibm_marrakesh coset map (`2026-11-06T200832.558771Z`) | 532,480 | 14.9 s | 24 s | 16.6 to 17.2 us |

Billed charges are integer seconds, so each residual carries about 1 us of rounding. ibm_kingston's 9 us residual per
static shot is the width-32 envelope job's (qpu_run_economy.md, rule 14). The check script prices a plan with 8.2 us
(ibm_fez), 9.0 us (ibm_kingston) and 17.2 us (ibm_marrakesh) and admits it at 92 percent of the ceiling or less.

| Run | Account (remaining at 03:10 UTC) | Binding dry run | Placements | PUBs x shots | Estimated seconds | Ceiling, reserve |
|---|---|---|---:|---|---:|---|
| ibm_fez | `backup-ibm-quantum-platform` (67 s) | `2026-11-07T035554.327341Z`, calibration 2026-11-06T19:35:16-08:00 | 17 | 112 x 14,336 | 52.3 (49.7 to 53.5) | 60 s, 5 s |
| ibm_kingston | primary (44 s) | `2026-11-07T040239.842834Z`, calibration 2026-11-06T19:47:41-08:00 | 16 | 112 x 8,192 | 32.3 (32.3 to 39.8) | 40 s, 4 s |

Repetition delay 20 us. The ibm_kingston range's upper end applies the ibm_marrakesh residual, the worst retained value,
and fits the 40 s ceiling by 0.2 s; the ibm_fez range spans the retained ibm_fez residuals 6.6 to 9.0 us. Block reads:
112 x 14,336 x 17 = 27.3 million on ibm_fez and 112 x 8,192 x 16 = 14.7 million on ibm_kingston. The two jobs run as
parallel invocations. The unspent quota is 14.7 s (ibm_fez) and 11.7 s (ibm_kingston). Raising ibm_kingston's shots to
9,216 reads 36.1 s nominal and 44.5 s at the ibm_marrakesh residual, above the 40 s ceiling, so the case keeps 8,192
until the ibm_fez job's billed charge fixes the residual of this circuit set; a job that reaches its ceiling is killed
and still billed, which loses its data.

Decisions for the owner. The 5 s and 4 s reserves sit below the 60 s account reserve that the retention audit records
(`account_reserve_met`); they follow the drain directive. The ibm_kingston job clears its ceiling by 0.2 s at the worst
retained residual; lowering that reserve to 2 s (ceiling 42 s, 2.2 s of margin at that residual) or dropping to 7,168 shots
(35.2 s at that residual, 28.6 s nominal) are the levers.

## Preregistered readout and decision rules

Intervals are Student t over the placements (17 and 16). A paired difference subtracts the dry run's per-placement model
value from the measured per-placement value before it averages, so the model's placement-to-placement spread (0.1 on the
odd part) does not enter the band; the model's own sampling noise (about 0.03 per placement on an operand total) adds
about 0.008 to a 16-placement mean and attenuates a regression slope by at most 8 percent.

- Resolution. Every two-term operand's pooled map agrees with the ideal sign on at least 31 of 32 bins, and every block's
  visibility interval lies above 0.5.
- Nullity bands. Each operand's N_hat interval covers its model value within 0.5 (model, ibm_fez: 0.12, 4.24, 4.25, 8.06,
  12.03, 12.17 for nullity 0, 4, 4, 8, 12, 12; twin 12.03; cocycle-free -2.19), and the readout-corrected values lie
  within 0.15 of the integer nullity. An operand outside its band refutes the compiled sign network's agreement with
  cd_core on that operand.
- Null selector contrast (estimator-free). For k0 and for each of k4, k8, k12 the mean over placements of the selector
  contrast, base and flip twin, lies within two standard errors of zero and within 0.006. A positive k0 mean above 0.006
  with the 1-CZ blocks at zero is the signature of a coherent sx over-rotation epsilon = contrast / 0.57 rad (the next
  section); the retained ibm_fez and ibm_marrakesh k0 contrasts bound |epsilon| below 0.010 and 0.012 rad (mean plus two
  standard errors, over 0.57). An asymmetric product readout channel maps the contrast of a null block to exactly 0, so a nonzero
  contrast is not a readout effect.
- Null N_hat per placement. For every placement, the readout-corrected N_hat of k0 and of each 1-CZ null block comes from
  `invert_readout` with that placement's own confusion lists (physical qubit calibration of `placed_qubit_calibration`).
  The mean over placements of each 1-CZ block lies within +-0.02 of 0. A positive mean with zero selector contrast, equal
  on the flip twin (even), is a population offset before the X that the readout correction does not remove (relaxation or
  residual excitation at the 20 us repetition delay; this case cannot separate the two, a longer-delay arm would). The
  ibm_marrakesh +0.045 on the 1-CZ blocks is open and ibm_marrakesh is outside this case (41 us per execution and 11
  placements), so the ibm_fez and ibm_kingston readings test the mechanism indirectly.
- Null offset decomposition on the e1 + e17 operand total over its four blocks, odd part O = (base - flip) / 2 and even
  part E = (base + flip) / 2 of N_hat. Even-part band: the paired mean of E minus the model's E lies within +-0.03
  (measurement standard error 0.012 on ibm_fez and 0.016 on ibm_kingston, plus 0.008); outside it names an offset that
  acts before the X and that the calibration does not predict. Odd-part band: the paired mean of O minus the model's O
  lies within +-0.04; below it refutes the calibrated asymmetry, above it means the readout asymmetry exceeds the
  calibration's confusion matrix. Placement spread: the regression of measured per-placement O on the model's has slope in
  [0.7, 1.3] and R squared above 0.5 (slope standard error about 0.12). O isolates the readout channel after the X; E
  pools relaxation during the gates, state-preparation excitation, coherent error and crosstalk.
- Within-arm repeats. The mean over placements of `within_minus_half_sum`, `within_plus_half_sum` and
  `pair_half_sum_gap` for the null operand lies within two standard errors of zero and within 0.02 (placement standard
  deviation 0.016 to 0.037, standard errors 0.004 to 0.009). A larger mean marks a position or drift effect of that size
  inside the arms; the pooled `quad_nullity_estimate` is then the readout.
- Parallel crosstalk. The 90 percent Newcombe-Wilson interval of packed minus isolated replica-0 score of the null block
  k0 minus arm lies inside +-0.015. Inside: no crosstalk at the one-hop separation and full density at that resolution.
  An interval that excludes zero and lies below -0.015 shows crosstalk; any other interval is unresolved. Measured on the
  retained runs (8,192 shots): +0.0011 [-0.0067, 0.0089] on ibm_fez and +0.0059 [-0.0028, 0.0145] on ibm_marrakesh, so the
  half-width is 0.008 at 8,192 shots and about 0.006 at 14,336 (model difference -0.0017 and -0.0004).
- Four-term blocks, per block: visibility V = (level T - level D) / (ideal T - ideal D) has an interval above 0.6 (model
  0.87 and 0.91); the closure (observed level minus D + V x (ideal - ideal D)) of F, E0, E1, D2 and N lies within 0.03 of
  the model's (at most 0.008 in magnitude) and of C within 0.03 of the model's (-0.019 to -0.028); the separations T - F,
  T - C, T - N each reach half their ideal value (0.25, 0.375 and 0.094 or more for B12); the E0 and E1 levels lie within
  0.02 of the model's 0.252 to 0.255. A failure of the closures with a passing visibility shows that the compiled sign
  network departs from the programmed block.
- Devices. The two backends' N_hat agree within the sum of their intervals for every operand, and each backend's odd
  and even parts pass their bands against its own model.

Predicted signatures by cause, from `tests/gororoba_quantum/test_pathion_parallel_coset.py` (confusion-matrix, bit-flip
and contraction channels on the ideal laws) and from a statevector with a coherent error after each routed gate (a block
routed on a four-qubit star, operand totals; the star routing costs 4 CZ on the 1-CZ blocks):

| Cause | Odd part O | Even part E | Selector contrast of a null block | Readout correction removes it | Within-arm repeat |
|---|---|---|---|---|---|
| readout asymmetry after the X, E10 above E01 | +0.113 (ibm_fez), +0.135 (ibm_kingston), varies by placement | 0 | exactly 0 | yes | 0 |
| relaxation during the gates, residual excitation | 0 | model +0.007 and -0.004 | 0 | no | 0 |
| symmetric contraction of the law | 0 | 0 | 0 | not needed | 0 |
| coherent CZ over-rotation delta (Rzz after each CZ) | 0 | +2.3 delta^2 (0.0009 at 0.02 rad, 0.0058 at 0.05; 0.03 needs 0.11 rad) | second order, near 0 | no | 0 |
| coherent sx over-rotation epsilon | 0 | small | k0 +0.57 epsilon per rad (0.566 measured on the model circuit at 0.02 rad), 1-CZ blocks -0.02 per rad (zero) | no | 0 |
| position or drift between PUBs | none unless it correlates with arm order | none | none | no | nonzero |
| crosstalk from active neighbors | none | nonzero, absent in the isolated reference | nonzero | no | 0 |

## Commands

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_parallel_coset_check.py 10 60' -- \
      --groups pathion_parallel_coset --backends ibm_fez --shots 14336 --rep-delay 2e-5 --replica-floor 0.5 \
      --exclude-qubits ibm_fez:2-4,16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json#1 \
      --max-total-execution-seconds 60 --max-execution-seconds 60 --reserve-seconds 5 \
      --min-remaining-seconds 5 --max-pending 100 --out ../results/live

    GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_parallel_coset_check.py 10 40' -- \
      --groups pathion_parallel_coset --backends ibm_kingston --shots 8192 --rep-delay 2e-5 --replica-floor 0.5 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json#1 \
      --max-total-execution-seconds 40 --max-execution-seconds 40 --reserve-seconds 4 \
      --min-remaining-seconds 4 --max-pending 100 --out ../results/live

Both runs pass the check script on their binding dry runs (estimated 52.3 s and 32.3 s), made from a clean source tree
at 48cf5619a. The two runs ask one question on two devices with one circuit set, so they share the seeds: indices 0 and
1 of the ANU QRNG draw `docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json` (16 uint16 values drawn
2026-11-07T03:19:54Z); the other 14 indices stay unused. The change that retains the runs adds the ledger rows with
`ci/seed_provenance.py --add-runtime`.

## Limits of this case

- The arm order inside a job is IBM's choice: the +, -, ..., -, + order is that of the member list, and the job's PUB
  shots may interleave. The within-arm repeats carry the position check.
- The case has 17 placements on ibm_fez and 16 on ibm_kingston, 33 together; the buffer rule caps one device at 16 or 17.
- The cost model rests on one retained job per backend for ibm_marrakesh and two for ibm_fez; ibm_kingston's residual
  comes from a different circuit family. The ceilings absorb 15 percent (ibm_fez) and 24 percent (ibm_kingston) above the
  estimate.
- Relaxation and residual excitation both land in the even part; separating them needs an arm at a longer repetition
  delay, which this case omits.
- `maximal_contracts._verify_isolation_contract` lists the standalone campaigns without the three pathion groups and
  fails on main already; it runs outside the contract suites and is unchanged here.
