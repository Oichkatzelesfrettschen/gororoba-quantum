# Orientation-bit case for ledger row A5-242 (ibm_fez kernel map)

Status: written and verified offline, awaiting one red-team pass and the owner's approval. Nothing has run on a provider.
Every cost and noise number below is labeled "retained snapshot": it comes from `docs/evidence/heron_platform/targets.json`
(ibm_fez, calibration 2026-10-14), and the live Target, the calibration of the day and the quota read are owed to the
binding dry run.

## Question

On the retained ibm_fez full kernel map the paired gap lambda_16 - lambda_0 of the Walsh-character contractions (lambda_a
is the observed over the ideal Walsh coefficient of the per-output contrast, `nhat_spectral.unit_spectrum`) reads
-0.155, -0.118, -0.066 on the nullity-4 units and +0.103, +0.081, +0.059 on the nullity-12 units over five replicas.
Character 16 is data bit 4, the highest bit h of m = i XOR j for these operands, and the plus arm is the minus arm with a
phase pi on data qubit h, so bit 4 is the orientation-phase qubit (ledger row A5-242). Row A5-606 adds that each
quarter-turn twin equals its primary with the two states of the bit-4 qubit exchanged, but the retained twins are
separate compiles.

The case asks whether the gap follows the orientation qubit, the compiled SELECT or the physical qubit, and whether a
state-dependent error of that qubit contributes. The observable is a property of the device's realization of the
circuit. The algebra enters only through ideal laws that Statevector and `cd_core` fix exactly (below); the case tests
the device.

## Circuits (`gororoba_quantum/pathion_kernel_map_orientation.py`)

`pathion_kernel_map.py` is digest-pinned (its sha256 occurs in retained kaggle and closure records), so the variants live in
the successor module and the retained file keeps its bytes. With default options the successor's circuits equal the
retained circuits gate for gate (`test_default_circuit_is_the_retained_circuit`, six operands and four twins).

Group `pathion_kernel_map_orientation`, 12 circuits (12 PUBs), one layout, for e1 + e26 (nullity 4, m = 27) and
e1 + e18 (nullity 12, m = 19):

| Unit | Circuit | Ideal Walsh support carrying the contrast |
|---|---|---|
| ctrl | retained placement, orientation on bit 4 | contains 16 |
| move | the pairs split by bit 1, phase pi on data qubit 1 | contains 2, excludes 16 |
| xtwin | ctrl plus one X on data qubit 4 after the SELECT, before readout | 16 (signs of the bins exchanged) |

Bit 1 is a set bit of both m (27 = 11011b, 19 = 10011b); the common set bits are 0, 1 and 4. Bits 0 and 1 route to the
same CZ count (table below), so the choice is a tie on cost; bit 1 is the one the SELECT's input-X layer does not touch (i = 1
sets only bit 0), so its gates are the selector CNOTs alone. Bit 0 is the preregistered alternative.

Verified exactly (`tests/gororoba_quantum/test_pathion_kernel_map_orientation.py`, Statevector on lab-a1, 23 tests):

- For every set bit b of m, the selector marginals are (16 -+ N)/32, every output contrast is +-1 and half their sum is N,
  so N is unchanged by b. The sign pattern of the contrast is not unchanged: moving the split exchanges which output of a
  misaligned pair carries -1, so the Walsh support moves from character 16 to character 2^b. That movement is what the
  case reads.
- Mutation test (Hardware probes of `docs/notes/algebra_circuit_rules.md`): the cocycle-free SELECT and one negated SELECT
  sign move the half-sum of the moved circuit away from N, so the ideal observable depends on the sign table.
- The X twin: for both pairs and both arms the ideal law of the primary plus one X on data qubit 4 after the SELECT equals
  the retained twin's law on all 64 outcomes (e1 + e26 with e17 - e10, e1 + e18 with e17 - e2); the primary's own law
  differs from it, and an X on qubit 0 or an X before the oracle fails the equality. The X sits after the SELECT, because
  s_twin(x) = -s_primary(x XOR 16) makes the twin the primary with output bit 4 exchanged.

Algebra status: these identities are exact finite checks (Statevector, `cd_core` matrices); none is a Lean or Rocq theorem,
and the sign relation of row A5-606 is an exact-arithmetic script. A machine-checked statement of the pair-split
invariance (N and |c| independent of b) would be a gororoba-math source; the case does not wait on it, since a hardware
reading of the device does not use it.

## Preregistered statistics and decision rule

Written before any data; implemented in `docs/evidence/pathion-kernel-map/orientation-bit/orientation_bit_analysis.py`,
which reuses `nhat_spectral.coefficients` and cross-checks every gap against `nhat_spectral.unit_spectrum` (mean and t).

Replicas are disjoint six-qubit tiles of the chip. Per replica and operand:

| Statistic | Definition | A5-242 predicts |
|---|---|---|
| G16 (ctrl) | lambda_16 - lambda_0 | sign -1 at nullity 4, +1 at nullity 12 (replication) |
| G2 (move) | lambda_2 - lambda_0 | the sign of G16 (reading i) |
| L16 (move) | c_obs,16 / c_obs,0, ideal 0 | 0 (inside +-0.05) |
| G16 (xtwin) | lambda_16 - lambda_0 against the exchanged ideal | the sign of ctrl if the effect follows the operand |
| S | (G16 ctrl + G16 xtwin) / 2 | nonzero if the effect follows the operand |
| D | (G16 ctrl - G16 xtwin) / 2 | zero; nonzero if a state-dependent error of the qubit enters |

Each is a one-sample t test over replicas with n - 1 degrees of freedom; the standard error is the scatter of the replica
values, so the test holds whatever the drift between regions. The family is 12 tests (6 statistics, 2 operands); Holm's
step-down procedure holds the family error at 0.05.

Readings, per operand:

- (i) The gap follows the orientation qubit: G2 rejected with the sign of the retained gap, and L16 inside +-0.05 (upper
  bound of its one-sided 95 percent interval). Refuted if G2 is not rejected while L16 is, which is reading (ii).
- (ii) The gap stays on bit 4 whatever the orientation qubit: L16 rejected and G2 not rejected. The hypothesis is refuted as
  stated; the effect belongs to the physical qubit or the SELECT.
- (iii) The exchange: S rejected and D not reads operand-following (sign kept); D rejected and S not reads state-dependent
  (sign flipped); both reads a mixture; neither is unresolved.
- Replication: G16 (ctrl) rejected with the retained sign is required; rejected with the opposite sign refutes A5-242
  (the row's own falsifier: a rerun whose paired gaps change sign).
- Verdict per operand: supported when replication, (i) and operand-following (iii) hold; refuted on (ii) or a flipped
  sign; unresolved otherwise. `--self-test` injects each case (and a null run, a flipped sign, leakage) and requires the
  verdict; 8 checks pass.

Replica count (`power.json`). The per-replica standard deviation is the standard error of five replicas, minus_zero over
minus_zero_t of `result_spectral.json`, times the square root of 5: 0.0906 (e1 + e26, effect -0.155) and 0.0808 (e1 + e18,
effect +0.103). At the Bonferroni level 0.05/12 = 0.0042 per test and power 0.8, the exact noncentral t needs 9 replicas
(e1 + e26) and 13 (e1 + e18) at the retained effect, and 23 and 38 at half of it. The case plans 15 replicas (3 runs of 5
regions), power 0.997 and 0.911 at the retained effects. Half the retained effect has power 0.49 and 0.23, and the minimum
detectable effect at 15 replicas is 0.102 and 0.091: the retained effects were chosen after the data from six units, so a
smaller true effect is likely unresolved, and the case states that outcome as unresolved rather than as a refutation.
Regions of later runs exclude the qubits of earlier ones (`--exclude-qubits`); the pooled test treats each region as one
replica and the run as no blocking factor, so between-run drift enters the scatter.

## Routed cost (retained snapshot, `case_compile.json`)

Basis cz, rz, sx, x, optimization level 3 (`live_run.OPT_LEVEL`), five best-ESP six-qubit tiles of the snapshot, three
transpiler seeds (draw `docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json`, indices 0 to 2). CZ count on all 15
(tile, seed) pairs:

| Member | e1 + e26 | e1 + e18 |
|---|---|---|
| ctrl, move (bit 1), xtwin, alternative bit 0 | 155 | 158 |
| retained primary, same compile | 155 | 158 |
| retained twin, same compile (range over 15) | 155 to 164 | 153 to 155 |

Every moved circuit has ratio 1.00 to its control (the 20 percent rejection bound is not reached; the oracle's diagonal
synthesis has a data-independent CZ network). The retained live compile read 136 to 173 (167 and 155 for the
nullity-4 pair); this compile is in range. Live CZ counts are owed to the dry run.

## Noise prediction (retained snapshot)

An exact density-matrix run (no sampling) of the routed circuits under a depolarizing model from the snapshot (each cz at
its coupler error, sx and x at their qubit error, a symmetric readout flip at the measure error), on the five tiles as
replicas. Gap statistics, mean and 95 percent t interval over tiles:

| Statistic | e1 + e26 | e1 + e18 |
|---|---|---|
| G16 ctrl (= xtwin = S) | -0.0110 [-0.0139, -0.0081] | -0.0172 [-0.0207, -0.0137] |
| G2 move | -0.0277 [-0.0338, -0.0216] | -0.0260 [-0.0290, -0.0229] |
| L16 move | -0.0071 [-0.0088, -0.0055] | -0.0012 [-0.0013, -0.0010] |
| D | 0 | 0 |

Why a simulation cannot answer the question: the snapshot carries no T1, T2 or operand-dependent decay of the orientation
qubit, so the model's gaps arise from character weight and readout alone. They are negative at both nullities and a
factor 7 to 14 smaller than the retained -0.155 (nullity 4), with the opposite sign of the retained +0.103 (nullity 12),
below the minimum detectable effect of 0.09 to 0.10. The model's exchange is a relabeling, so D is zero by construction;
whether the physical exchange carries a state-dependent error is the measurement. Intervals reflect tile scatter of the
exact model and exclude shot noise.

## Backend, shots, expected seconds

- Backend ibm_fez (the retained device; a second backend is a separate case). Account and quota read at the dry run: the
  window is 600 s rolling and 484 s were free at the last read.
- 12 PUBs per run, 16,384 shots per PUB, repetition delay 20 us, five regions per run at replica floor 0.7 (as retained),
  3 runs, at most 15 replicas, one job per run.
- Expected seconds per run: 2 s of overhead plus 12 PUBs at the retained 0.533 s per PUB (14.8 s expected over 24 PUBs in the
  retained case, 18 s measured) is 8.4 s expected and about 10 s at the measured rate. Three runs: 25 s expected,
  about 31 s at the measured rate; ceiling 15 s per job, 45 s in total, reserve 20 s.
- Credits: IBM Open plan quantum seconds only; 0 credits.
- Arm order: arms alternate (plus first on unit 1, minus first on unit 2, and so on), each unit's two arms adjacent. This
  places each arm early and late in the job; it is a partial balance, not the +, -, -, + order, whose full form needs both orders in
  one calibration and doubles the PUBs.

## What the run measures

Whether the retained gap of character 16 moves with the orientation phase to data qubit 1 and whether it keeps or flips
sign under the exchange of the bit-4 states, on the device, over 15 disjoint regions, with one family-wise error of 0.05.
Reading (ii) refutes A5-242 as stated; reading (i) with operand-following (iii) supports an operand-following
orientation-qubit effect and leaves the mechanism hypothesis (SELECT-set decay) open; a state-dependent D resolves
the exchange part that the retained twins could not.

## Falsifiers of the design

- The routed CZ of a moved circuit departing by more than 20 percent from its control rejects bit 1 and selects bit 0.
- A dry-run plan placing fewer than five regions at floor 0.7 changes the run count; fewer than 13 regions in total
  leaves the case under-powered for e1 + e18 and is refused.
- Either arm of a unit routing to a different CZ count from its partner refuses the plan (as in the retained check).

## Owed

- The live dry run through `scripts/approved_run.sh --check` (live Target, calibration, quota, placement), and a check
  script for the placement, as `scripts/pathion_kernel_map_check.py` is for the retained map.
- One red-team pass, the Advisor review and the owner's approval of this case.
- Ledger rows for the case in `docs/evidence/a5-exceptional-fibers/ledger.tsv` (A5-242 and A5-606 live on
  branch a5-pfaffian-boost-stability, not on main).
- Seeds for the live plan: indices 3 (seed_transpiler) and 4 (seed_simulator) of the draw above are reserved.

## Reproduction

On an aarch64 host with the pinned environment: `orientation_bit_analysis.py --self-test`, `--power DIR`;
`compile_case.py --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#0 ...#1 ...#2 --out DIR`.
