# Written case: wide parallel coset-block map on ibm_fez and ibm_kingston (ppc)

Status: awaiting the owner's approval. Each run is a binding dry run and `--submit` back to back through
`scripts/approved_run.sh` with `scripts/pathion_parallel_coset_check.py` as its check. Nothing is submitted, booked or
charged until the owner approves this case.

## What it measures

Group `pathion_parallel_coset` (`gororoba_quantum/pathion_parallel_coset.py`, four-term circuits in
`gororoba_quantum/pathion_four_term_block.py`) holds 111 four-qubit circuits that compile onto one layout, so each of its
112 fused PUBs (111 members and live_run's isolated reference) reads one circuit on 16 disjoint placements at once, 64
qubits per shot. The circuits answer four questions, each with a decision rule below.

1. Coset-block map across placements. The 64 members of the retained `pathion_coset_map` (eight two-term operands, each
   tiled by four coset blocks, both orientation arms) read the per-block estimate N_hat and the sign of every output
   contrast on 16 placements. The single-placement-set runs on ibm_fez and ibm_marrakesh
   (`2026-11-06T201037.234804Z`, `2026-11-06T200832.558771Z`) averaged placements into one interval; this case keeps the
   per-placement values and tests them against the per-placement model.
2. The null operand e1 + e17. Both retained IBM runs read a positive nullity estimate in all 8 of 8 coset blocks
   (operand total 0.096 on ibm_fez, 0.075 on ibm_marrakesh; block k0 alone 0.050 [0.028, 0.071] and 0.035 [0.009, 0.061];
   the other three blocks 0.008 to 0.018 with intervals that cover zero), and the readout-corrected values are 0.014 and
   0.008 on block k0. Two control families split the offset by cause. Readout-flip twins (`cflip_*`, 16 members) carry X on
   all four qubits before the measurement; the ideal law is the base law with every outcome index complemented. Mirrored
   repeats (`crep_*`, 16 members) run each arm of a block a second time on the same template and binding, listed in
   reverse order, so the arms read +, -, ..., -, + in the member list. Both families cover the four cosets of the null
   operand and of e1 + e18 (nullity 12), the contrast with every block resolved.
3. Four-term coset blocks (`ftb_*`, 15 members) of the two Gram spectra absent below dimension 32: B12 (spectrum 0, 0, 4,
   12, operand e1 + e10 + e20 + e31, coset 2) and C8 (spectrum 0, 1.528, 4, 10.472, operand e1 + e8 + e18 + e27, coset 5).
4. Parallel-operation crosstalk: live_run's isolated reference runs the first member, the null block k0 minus arm, alone
   on replica 0 against the same circuit inside the 16-placement PUB.

## Design

- Two-term blocks. The block circuit of `pathion_coset_block.py` (H on 3 data qubits, a diagonal, H on the selector, a
  4-qubit diagonal, CNOT, H) with the orientation parameter bound to 0 (minus) or pi (plus). Mutation test: the
  cocycle-free tiling of e1 + e18 reads N = -2 against 12 (retained as `cmap_xor_*`). Arms: plus and minus on the
  parametrized circuit, so both route to the same CZ sequence; the repeats add the second pair, and the null arm is the
  null operand e1 + e17 (ideal contrast 0 in the sum over bins, alternating +1 and -1 per bin). cd_core certifies every
  operand and sign: `pathion_coset_block.tile` returns contrast gap 0 for each tiling, and the module's tests compare
  every block with the six-qubit law of `pathion_kernel_map`.
- Four-term blocks. A two-flat operand a0 + a1 + a2 + a3 (a0 ^ a1 ^ a2 ^ a3 = 0, all coefficients +1) is block diagonal
  over the cosets of span(a0 ^ a1, a0 ^ a2); a block is a 4 x 4 matrix B of entries +-1. The circuit is a real two-qubit
  input state on two data qubits (three Ry angles, 2 CZ-equivalent), H on a two-qubit selector, one diagonal on all four
  qubits, CX(s0 to d0), CX(s1 to d1), and H on the selector, measured on all four. The probability of selector 00 is
  |B psi|^2 / 16. All 16 entries of every block of both operands equal the cd_core left multiplication
  (`core_block_matrix`). Arms: T the top Gram eigenvector (level 0.75 for B12, 0.6545 for C8), D and D2 kernel vectors
  (level 0; D2 exists for B12, whose kernel has dimension 2), F the top vector with one component negated (0.25 and
  0.0691), E0 and E1 basis inputs (null level 0.25 for every block), C the cocycle-free block (every entry +1; 0 and 0),
  N the block with the one entry negated whose negation moves the level most (0.5625 and 0.4523). T, D, D2, F, E0 and E1
  are one parametrized circuit and route identically. Every mutated arm lies at least 0.10 below the true top level.
- Placement. The replica search takes the best-scored placements of the group's compiled pattern, each with a one-qubit
  buffer (`place_replicas` blocks every replica's qubits and their neighbors), and returns 16 placements on both devices;
  the quality policy (readout error above 0.08, CZ error above 0.03, T1 or T2 below 20 us) has excluded 19 qubits and 20
  couplers on ibm_fez and 11 qubits and 22 couplers on ibm_kingston at the dry runs, and no further qubit is excluded by
  hand. The 16 placements sit at replica scores 0.57 to 0.85 (ibm_fez) and 0.72 to 0.84 (ibm_kingston); replica floor 0.5
  admits them all, and an exploratory ibm_kingston dry run at floor 0.3 returned the same count, so 16 is the limit of
  the buffer rule on a 156-qubit device (156 / 16 = 9.75 qubits per replica, its own four plus their neighbors). The 64 placed qubits have median readout error 0.0100 and 0.0098, median T1 139
  and 247 us, and E10 minus E01 from -0.010 to 0.053 (ibm_fez) and -0.021 to 0.031 (ibm_kingston), the spread that the
  placement-spread decision reads.
- Packing judgment. Patterned replica bodies (`Member.replica_bodies`) are refused for bodies whose ideal laws differ,
  which every coset and arm does. A composite member with several blocks per replica would trade replica count for blocks
  per replica at constant block reads per execution, would put adjacent blocks without the buffer (the isolated
  reference then tests nothing about separation), and a 12-qubit member leaves the 14-qubit local-simulation rule's
  comfort. The case therefore keeps one block per replica and 16 replicas; a buffer-free packing needs a policy knob in
  `live_run.place_replicas` that does not exist.

## Why a noise simulation cannot answer it

The binding dry runs simulate each of the 16 placements with the live calibration (T1, T2, gate error and duration, and
each measured qubit's asymmetric readout channel) and predict the counts the decisions read: the operand-level null
estimate 0.1235 (ibm_fez) and 0.1308 (ibm_kingston) with an odd part 0.125 and 0.135, an even part -0.001 and -0.004,
and a readout-corrected value 0.004 and -0.009; the odd part varies across the 16 placements with standard deviation
0.099 and 0.120, the even part with 0.024 and 0.021; the four-term visibility 0.879 to 0.912 with every closure within
0.011 except the cocycle-free arm at -0.025. The calibrated model contains no coherent error, no crosstalk between
active neighbors, no two-level-system defect and no drift. The hardware answers four things the model cannot: whether the
even part is zero (a nonzero value is an effect outside the calibration), whether the placement-to-placement spread of
the odd part follows the per-qubit readout calibration placement by placement, whether packing 16 placements changes a
block's law, and whether a four-term block's sign network survives at 18 to 25 routed CZ.

## Four-term feasibility verdict

A circuit exists and fits. The two retained spectra route to 18 CZ (B12) and 19 CZ (C8) for the six shared arms, 8 CZ
for the cocycle-free arm and 25 CZ for the mutated-entry arm on both devices, against 20 CZ for the deepest two-term block
and a case budget of 30. The observable is the probability of selector 00, so no outcome is postselected and no
block-encoding success probability is paid; the conditional output bins of the bright arm use the selector-00 shots,
about 75 percent of 14,336 (ibm_fez, 10,752 per placement) or 8,192 (ibm_kingston, 6,144) for B12 and 65 percent for C8,
and the dark arms (level 0, model 0.031) use the full counts for their level only. The class is kept. The kernel
dimension of B12 (2) is read by two orthogonal kernel arms; C8 has kernel dimension 1.

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
| ibm_fez | `backup-ibm-quantum-platform` (67 s) | `2026-11-07T033318.138594Z`, calibration 2026-11-06T18:48:55-08:00 | 16 | 112 x 14,336 | 52.3 (49.7 to 53.5) | 60 s, 5 s |
| ibm_kingston | primary (44 s) | `2026-11-07T033832.292636Z`, calibration 2026-11-06T19:19:09-08:00 | 16 | 112 x 8,192 | 32.3 (32.3 to 39.8) | 40 s, 4 s |

Repetition delay 20 us, replica floor 0.5. The ibm_kingston range's upper end applies the ibm_marrakesh residual, the
worst retained value, and fits the 40 s ceiling by 0.2 s; the ibm_fez range spans the retained ibm_fez residuals 6.6 to
9.0 us. Block reads: 112 x 14,336 x 16 = 25.7 million on ibm_fez and 14.7 million on ibm_kingston. The two jobs run as
parallel invocations. The unspent quota is 14.7 s (ibm_fez) and 11.7 s (ibm_kingston). Raising ibm_kingston's shots to
9,216 reads 36.1 s nominal and 44.5 s at the ibm_marrakesh residual, above the 40 s ceiling, so the case keeps 8,192 until
the ibm_fez job's billed charge fixes the residual of this circuit set; a job that reaches its ceiling is killed and
still billed, which loses its data. Decision for the owner: the 5 s and 4 s reserves sit below the 60 s account reserve
that the retention audit records (`account_reserve_met`); they follow the drain directive and the owner confirms them.

## Preregistered readout and decision rules

Placement intervals are Student t over the 16 placements. Model values come from the two binding dry runs.

1. Resolution. Every two-term operand's pooled map agrees with the ideal sign on at least 31 of 32 bins, and every
   block's visibility interval lies above 0.5 (model 0.85 to 0.94).
2. Nullity bands. Each operand's N_hat interval covers its model value within 0.5 (model, ibm_fez: 0.12, 4.25, 4.25, 8.06,
   12.04, 12.18 for nullity 0, 4, 4, 8, 12, 12; twin 12.03; cocycle-free -2.19), and the readout-corrected values lie
   within 0.15 of the integer nullity. An operand outside its band refutes the compiled sign network's agreement with
   cd_core on that operand.
3. Null offset decomposition on the e1 + e17 operand total over its four blocks, with the odd part O = (base - flip) / 2
   and the even part E = (base + flip) / 2 of N_hat. (a) E within +-0.03 (model -0.001 and -0.004; expected interval
   half-width 0.012 to 0.016); E outside names an offset that does not depend on which basis state carries the
   contrast. (b) O within 0.04 of the model value (0.125 and 0.135); below the band refutes the calibrated asymmetry,
   above it shows a population bias beyond the readout that the readout correction does not remove. (c) The regression of
   the measured per-placement O on the dry run's per-placement O has slope in [0.7, 1.3] and R squared above 0.5; the
   slope's standard error is about 0.12 at the expected 0.05 shot noise of one placement's O. (d) The readout-corrected
   null N_hat lies within 0.03 of 0.
4. Within-arm repeats. The mean over placements of `within_minus_half_sum`, `within_plus_half_sum` and
   `pair_half_sum_gap` for the null operand lies within two standard errors of zero and within 0.02 (placement standard
   deviation 0.017 to 0.037 gives standard errors 0.004 to 0.009). A larger mean marks a position or drift effect of that
   size inside the arms; the pooled `quad_nullity_estimate` is then the readout.
5. Parallel crosstalk. The 90 percent Newcombe-Wilson interval of packed minus isolated replica-0 score of the null block
   k0 minus arm lies inside +-0.01 (model difference +0.003 and -0.0004 with half-width 0.004 and 0.006). Inside: no
   crosstalk at the one-hop separation and 16-placement density at that resolution. An interval that excludes zero and
   lies below -0.01 shows crosstalk; any other interval is unresolved. The retained runs read -0.002 [-0.009, 0.005]
   and -0.005 [-0.012, 0.003] at the 0.03 margin.
6. Four-term blocks, per block: visibility V = (level T - level D) / (ideal T - ideal D) has an interval above 0.6
   (model 0.88 to 0.91); the closure (observed level minus the affine prediction D + V x (ideal - ideal D)) of F, E0, E1,
   D2 and N lies within 0.03 of the model's closure (at most 0.011 in magnitude), and of C within 0.03 of the model's
   -0.025; the separations T - F, T - C, T - N each reach half their ideal value (0.25 or more, 0.375 or more and 0.094 or
   more for B12); the E0 and E1 levels lie within 0.02 of the model's 0.253 to 0.256. A failure of the closures with a
   passing visibility shows that the compiled sign network departs from the programmed block.
7. Devices. The two backends' N_hat agree within the sum of their intervals for every operand, and each backend's odd
   part lies within rule 3(b) of its own model.

Predicted signatures by cause, from `tests/gororoba_quantum/test_pathion_parallel_coset.py` (confusion-matrix and
contraction channels on the ideal laws) and a coherent over-rotation Rzz(delta) after every routed CZ (statevector on
a star-routed block, operand totals):

| Cause | Odd part O | Even part E | Readout correction removes it | Within-arm repeat |
|---|---|---|---|---|
| readout asymmetry, E10 above E01 | +0.125 (ibm_fez), +0.135 (ibm_kingston), varies by placement | 0 | yes | 0 |
| relaxation during the circuit | model residual 0.004 and -0.009 after correction | 0 | no | 0 |
| symmetric contraction of the law | 0 | 0 | not needed | 0 |
| coherent CZ over-rotation delta | 0 | +2.3 delta^2 (0.0009 at 0.02 rad, 0.0058 at 0.05 rad; 0.03 needs 0.11 rad) | no | 0 |
| position or drift between PUBs | none unless it correlates with arm order | none | no | nonzero |
| crosstalk from active neighbors | none | nonzero, absent in the isolated reference | no | 0 |

## Commands

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_parallel_coset_check.py 10 60' -- \
      --groups pathion_parallel_coset --backends ibm_fez --shots 14336 --rep-delay 2e-5 --replica-floor 0.5 \
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

Both runs pass the check script on their binding dry runs (estimated 52.3 s and 32.3 s). The two runs ask one question on
two devices with one circuit set, so they share the seeds: indices 0 and 1 of the ANU QRNG draw
`docs/evidence/anu_qrng/draw-2026-11-07T031954Z.json` (16 uint16 values drawn 2026-11-07T03:19:54Z); the other 14
indices stay unused. The change that retains the runs adds the ledger rows with `ci/seed_provenance.py --add-runtime`.

## Limits of this case

- The arm order inside a job is IBM's choice: the +, -, ..., -, + order is that of the member list, and the job's PUB
  shots may interleave. The within-arm repeats carry the position check.
- The cost model rests on one retained job per backend for ibm_marrakesh and two for ibm_fez; ibm_kingston's residual
  comes from a different circuit family. The ceilings absorb 15 percent (ibm_fez) and 24 percent (ibm_kingston) above the
  estimate.
- `maximal_contracts._verify_isolation_contract` lists the standalone campaigns without the three pathion groups and
  fails on main already; it runs outside the contract suites and is unchanged here.
