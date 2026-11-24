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
| xtwin | ctrl plus one X on data qubit 4 after the SELECT, before readout | the control's eight characters, with the sign of every character that carries bit 4 exchanged |

Compiled form (snapshot target, optimization level 3). The xtwin routes to the control's schedule plus one virtual rz on
the wire measured into data bit 4: the cz sequence (qubit pairs and order), the sx and x gates and the measure mapping are
identical, and the two circuits differ only in rz angles of that wire, in the stretch before its last sx, which holds cz and
rz gates only (rz commutes with cz). This held on all 60 compiles of a scratch sweep (5 tiles, 3 transpiler seeds, 2
operands, both arm phases; not retained) and is asserted on one tile and one seed per operand by
`test_exchange_compiles_to_one_frame_on_the_bit_four_wire`. The consequence for D is stated with its row below.

Bit 1 is a set bit of both m (27 = 11011b, 19 = 10011b); the common set bits are 0, 1 and 4. Bits 0 and 1 route to the
same CZ count (table below), so the choice is a tie on cost; bit 1 is the one the SELECT's input-X layer does not touch (i = 1
sets only bit 0), so its gates are the selector CNOTs alone. Bit 0 is the preregistered alternative.

Verified exactly (`tests/gororoba_quantum/test_pathion_kernel_map_orientation.py`, Statevector on an aarch64 host, 23 tests):

- For every set bit b of m, the selector marginals are (16 -+ N)/32, every output contrast is +-1 and half their sum is N,
  so N is unchanged by b. The sign pattern of the contrast is not unchanged: moving the split exchanges which output of a
  misaligned pair carries -1. Every member's ideal contrast has a Walsh support of eight characters, with these
  coefficients times 4 (`SUPPORTS` in the test module):

  | Member | e1 + e26 (nullity 4) | e1 + e18 (nullity 12) |
  |---|---|---|
  | ctrl | 0: 1, 4: 1, 10: -1, 14: -1, **16: -3**, 20: 1, 26: -1, 30: -1 | 0: 3, 4: -1, 8: -1, 12: -1, **16: -1**, 20: -1, 24: -1, 28: -1 |
  | move (bit 1) | 0: 1, **2: -3**, 4: 1, 6: 1, 8: -1, 10: -1, 12: -1, 14: -1 | 0: 3, **2: -1**, 4: -1, 6: -1, 8: -1, 10: -1, 12: -1, 14: -1 |
  | xtwin | as ctrl, with the sign of 16, 20, 26, 30 exchanged | as ctrl, with the sign of 16, 20, 24, 28 exchanged |

  The signature character (bold) moves from 16 to 2^b = 2. Three of the other seven characters are shared by control and
  moved member (4, 10, 14 at nullity 4; 4, 8, 12 at nullity 12). No statistic reads a shared character: the gaps read
  characters 0, 16 and 2, and leak16 reads character 16 outside the moved support. The (0, signature) weight pair is
  identical between control and moved member (1/4 and 3/4 at nullity 4, 3/4 and 1/4 at nullity 12), so G16 and G2
  compare weight-matched quantities. The signature movement is what the case reads.
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
| leak16 (move) | c_obs,16, ideal 0 (character 16 is outside the moved support) | 0; reported, cannot decide |
| C | G16 ctrl - G2 move | 0 (the gap moves at equal size) |
| G16 (xtwin) | lambda_16 - lambda_0 against the exchanged ideal | the sign of ctrl if the effect follows the operand |
| S | (G16 ctrl + G16 xtwin) / 2 | nonzero if the effect follows the operand |
| D | (G16 ctrl - G16 xtwin) / 2 | zero under the row's SELECT-decay hypothesis; nonzero only for an asymmetric readout of the bit-4 physical qubit or a coherent angle error on that wire's final single-qubit tail |

What D sees. The xtwin differs from the control by one frame on the bit-4 wire after the SELECT (compiled form above), so
D is zero under any error that acts before that frame, the SELECT-decay hypothesis of row A5-242 included, and under any
error that commutes with the frame (depolarizing noise, which is unitarily covariant). It responds to asymmetric readout of
that qubit and to a coherent angle error on the tail. Relaxation enters only through the cz and idle interval that the
frame commutes through: the exact relaxation-only model predicts D = -0.00041 (nullity 4) and -0.00004 (nullity 12), about
1 percent of the control gap and under 0.5 percent of the minimum detectable effect, so D does not resolve relaxation. D
isolates the readout-asymmetry half of the row's open question (relaxation or asymmetric readout): the asymmetric-readout
model predicts D = -0.012 and -0.005.

Each is a one-sample t test over replicas with n - 1 degrees of freedom; the standard error is the scatter of the replica
values, so the test holds whatever the drift between regions. The family is 14 tests (7 statistics, 2 operands); Holm's
step-down procedure holds the family error at 0.05.

Readings, per operand:

- (i) The gap follows the orientation qubit: G2 rejected with the sign of the retained gap and C not rejected.
- (ii) The gap stays on bit 4 whatever the orientation qubit: the control's gap replicates, C is rejected and G2 does not
  follow (not rejected with the retained sign). The hypothesis is refuted as stated; the effect belongs to the
  physical qubit or the SELECT. This is the row's first falsifier, and C is its test: the moved support holds no
  character with bit 4, so a character-diagonal channel cannot put weight on 16 and leak16 alone cannot detect the
  mechanism; it is reported (a nonzero leak16 needs asymmetric readout or relaxation) and does not enter the verdict.
- (iii) The exchange: S rejected and D not reads operand-following (sign kept); D rejected and S not reads an
  asymmetric readout or tail-angle effect of the bit-4 qubit (sign flipped; the SELECT-decay hypothesis predicts D = 0, so
  a rejected D does not support it); both reads a mixture; neither is unresolved. The reading is labeled
  `state-dependent` in the analysis output.
- Replication: G16 (ctrl) rejected with the retained sign is required; rejected with the opposite sign refutes A5-242
  (the row's second falsifier: a rerun whose paired gaps change sign).
- Verdict per operand: supported when replication, (i) and operand-following (iii) hold; refuted on (ii) or a flipped
  sign; unresolved otherwise (including a moved gap that follows with a different size).
- Row rule: A5-242 reads supported only when both operands read supported, refuted when either operand reads refuted,
  and unresolved otherwise (`row_verdict`, tested). The two operands were chosen after the data as the largest retained
  effect at each nullity among those with a retained twin, so the retained effects carry a winner's curse; the
  replication test answers it, and a smaller true effect reads unresolved.
- Dead-region rule: a region is dead when its visibility, the mean over its six units of the estimator's signed
  visibility V_hat (the quantity behind the retained 0.004 and -0.033), is below 0.05. When more than one third of the
  regions are dead the analysis runs again over the live regions and a verdict counts only when both runs read it; fewer
  than three live regions leave every verdict unresolved. The retained run has two dead regions of five.
- Exploratory output, outside the family of 14, the power calculation and the verdict: with `--readout-errors` (one
  calibration readout error of the bit-4 physical qubit per replica, read at the dry run) the analysis reports the
  Pearson and Spearman correlation of each replica's control gap G16 with it.
- Floor argument: a per-qubit readout flip predicts negative gaps at both nullities (asymmetric-readout model below:
  -0.007 and -0.037), so the nullity-12 gap reading positive is the sign that readout cannot produce; the e1 + e18 G16
  and G2 signs are the discriminating reading, and a negative gap at nullity 4 alone is not.
- Coherent errors: the case carries no ZZ or crosstalk row. The Target and the retained calibration hold no coupling
  rates, so a coherent-error response cannot be predicted offline; D is the case's first-order probe of a coherent angle
  error on the tail, and a coherent-error audit of the compiled circuits (as `scripts/iqm_probe_audit.py` does for IQM) is
  owed to the dry run if the rates become readable. `--self-test` injects each case
  (null run, operand-following effect, gap on bit 4 only, a third-size moved gap, leakage, state-dependent exchange,
  flipped sign) and requires the verdict; 10 checks pass.

Replica count (`power.json`). The per-replica standard deviation of a gap is the standard error of five replicas, minus_zero
over minus_zero_t of `result_spectral.json`, times the square root of 5: 0.0906 (e1 + e26, effect -0.155) and 0.0808
(e1 + e18, effect +0.103). The scatter of C is estimated by the standard deviation over the five retained replicas of
G16 of the primary minus G16 of its quarter-turn twin on the same region (two circuits on one region): 0.0835 and 0.0818
(`retained_collect_sha256` in `power.json`; the correlations are 0.49 and 0.14, a weak estimate from five replicas). At
the Bonferroni level 0.05/14 = 0.0036 per test and power 0.8 the exact noncentral t needs 9 and 13 replicas for the gap
and 9 and 14 for C at the retained effect (C taken at its alternative that the moved gap is zero), and 24 and 39 for the
gap at half of it. The case plans 15 replicas: power 0.996 and 0.898 for the gap, 0.999 and 0.889 for C. Half the retained
effect has power 0.47 and 0.21, and the minimum detectable gap at 15 replicas is 0.104 and 0.093, so a smaller true effect
(the retained effects were chosen after the data from six units) reads as unresolved, not as a refutation.

The retained scatter is itself a risk: two of the five retained replicas of e1 + e26 and of its twin read a visibility near
zero (0.004, -0.033 and 0.027, 0.007 against 0.14 to 0.26 on the others), so the dead-region rule above applies to the
live run, and the standard deviations above, which include those regions, can overstate the scatter of the live ones. The
off-support coefficient c_obs,16 of the retained units has a median scatter of 0.012 to 0.017 over replicas (the shot-noise
scale of 32 bins at 16,384 shots), which sets the scale of leak16.

Replicas are disjoint regions packed inside each PUB, so they cost no extra device seconds. The snapshot admits 15
disjoint six-qubit tiles at guard distance 2 and ESP floor 0.5 to 0.7 (10 at guard distance 3), so one job of 15 regions
fits the snapshot; the retained live run placed 5. If the dry run places fewer than 15, the case runs
ceil(15 / regions) jobs (3 at five regions), each a separate dry run and approval, with later runs excluding the qubits of
earlier ones (`--exclude-qubits`); the pooled test treats each region as one replica and the job as no blocking factor,
so between-run drift enters the scatter.

## Routed cost (retained snapshot, `case_compile.json`)

Basis cz, rz, sx, x, optimization level 3 (`live_run.OPT_LEVEL`), five best-ESP six-qubit tiles of the snapshot, three
transpiler seeds (draw `docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json`, indices 0 to 2). CZ count on all 15
(tile, seed) pairs:

| Member | e1 + e26 | e1 + e18 |
|---|---|---|
| ctrl, move (bit 1), xtwin, alternative bit 0 | 155 | 158 |
| retained primary, same compile | 155 | 158 |
| retained twin, same compile (range over 15) | 155 to 164 | 153 to 155 |

Every moved circuit and the alternative bit 0 has ratio 1.00 to its control (the 20 percent rejection bound is not reached; the oracle's diagonal
synthesis has a data-independent CZ network). The retained live compile read 136 to 173 (167 and 155 for the
nullity-4 pair); this compile is in range. Live CZ counts are owed to the dry run.

## Noise prediction (retained snapshot)

Snapshot rows. An exact density-matrix run (no sampling) of the routed circuits under a depolarizing model from the snapshot (each cz at
its coupler error, sx and x at their qubit error, a symmetric readout flip at the measure error), on the five tiles as
replicas. Gap statistics, mean and 95 percent t interval over tiles:

| Statistic | e1 + e26 | e1 + e18 |
|---|---|---|
| G16 ctrl (= xtwin = S) | -0.0110 [-0.0139, -0.0081] | -0.0172 [-0.0207, -0.0137] |
| G2 move | -0.0277 [-0.0338, -0.0216] | -0.0260 [-0.0290, -0.0229] |
| leak16 move | -0.0009 [-0.0010, -0.0007] | -0.0004 [-0.0005, -0.0003] |
| C = G16 ctrl - G2 move | +0.0167 [0.0131, 0.0203] | +0.0088 [0.0033, 0.0142] |
| D | 0 | 0 |

Relaxation prediction (retained calibration of 2026-11-06). The snapshot holds no T1 or T2. The only per-qubit T1, T2 and
asymmetric readout errors of ibm_fez in the tree belong to the retained kernel-map run
(`results/live/2026-11-06T183538.809814Z/record.json`, calibration 2026-11-06T10:24:29-08:00, five regions, no T2 above
2 T1), so the same members route with the first transpiler seed onto those five regions and run exactly under four models
built from that record: depolarizing gate errors with a symmetric readout flip (the snapshot model, on these regions),
relaxation alone (T1 and T2 over every gate and idle interval of an ASAP schedule that ends all wires together, rz
virtual, ideal gates and readout), asymmetric readout alone (`prob_meas1_prep0`, `prob_meas0_prep1`), and all three.
The producer is `compile_case.py` (`"relaxation"` block of `case_compile.json`, `compile_case.py --check` recomputes and
compares). Means over the five regions; the retained gaps are -0.155 and +0.103 over the same regions:

| Statistic | Model | e1 + e26 | e1 + e18 |
|---|---|---|---|
| G16 ctrl | depolarizing, symmetric readout | -0.0137 | -0.0202 |
| G16 ctrl | relaxation only | -0.0417 | -0.0072 |
| G16 ctrl | asymmetric readout only | -0.0072 | -0.0374 |
| G16 ctrl | all three | -0.0326 | -0.0141 |
| G2 move | all three | -0.0710 | -0.0328 |
| C = G16 ctrl - G2 move | all three | +0.0384 | +0.0187 |
| D | depolarizing, relaxation only, asymmetric readout only, all three | 0, -0.0004, -0.0124, -0.0043 | 0, -0.00004, -0.0052, -0.0017 |

Relaxation alone reaches the retained sign at nullity 4 at 27 percent of the size (-0.042 against -0.155; all three
together 21 percent) and does not reach the retained sign at nullity 12 (-0.007 against +0.103); no model predicts a
positive gap at either nullity. The models also predict a C of +0.019 to +0.038: a bias between the control and the
moved member that stays below the minimum detectable effect (0.09 to 0.10) and equals 0.9 to 1.8 standard errors of C over
15 replicas (0.0835 and 0.0818 per replica). Intervals of the snapshot table reflect tile scatter of the exact model and
exclude shot noise.

Why a simulation cannot answer the question: no modeled combination of depolarizing error, relaxation and asymmetric
readout predicts the retained positive gap at nullity 12 (+0.103, against -0.007 to -0.037), and the nullity-4 gaps reach
at most 27 percent of the retained -0.155; the remainder, and the sign at nullity 12, belong to an effect the models omit,
which is what the device measurement tests. The comparison rests on one calibration of one day and five regions; a
different day's T1 and T2 shift the relaxation share, which the dry run's live calibration reads.

## Backend, shots, expected seconds

- Backend ibm_fez (the retained device; a second backend is a separate case). Account and quota read at the dry run: the
  window is 600 s rolling and 484 s were free at the last read.
- 12 PUBs per job, 16,384 shots per PUB, repetition delay 20 us, replica floor 0.7 (as retained), 15 regions in one job when
  the dry run places them, else up to 3 jobs of 5.
- Expected seconds per job: 2 s of overhead plus 12 PUBs at the retained 0.533 s per PUB (14.8 s expected over 24 PUBs in the
  retained case, 18 s measured) is 8.4 s expected and about 10 s at the measured rate. One job of 15 regions: 8.4 s; three jobs of 5: 25 s expected,
  about 31 s at the measured rate; ceiling 15 s per job, 45 s in total, reserve 20 s.
- Credits: IBM Open plan quantum seconds only; 0 credits.
- Arm order: arms alternate (plus first on unit 1, minus first on unit 2, and so on), each unit's two arms adjacent. This
  places each arm early and late in the job; it is a partial balance, not the +, -, -, + order, whose full form needs both orders in
  one calibration and doubles the PUBs.

## What the run measures

Whether the retained gap of character 16 moves with the orientation phase to data qubit 1 and whether it keeps or flips
sign under the exchange of the bit-4 states, on the device, over 15 disjoint regions, with one family-wise error of 0.05.
Reading (ii) refutes A5-242 as stated; reading (i) with operand-following (iii) supports an operand-following
orientation-qubit effect and leaves the mechanism hypothesis (SELECT-set decay) open; a rejected D reports an asymmetric
readout or tail-angle effect of the bit-4 qubit, the half of the row's open question that the retained separate-compile
twins could not isolate, and D = 0 leaves relaxation and readout asymmetry unseparated.

## Falsifiers of the design

- The routed CZ of a moved circuit departing by more than 20 percent from its control rejects bit 1 and selects bit 0.
- A dry-run plan placing fewer than five regions at floor 0.7 changes the run count; fewer than 13 regions in total
  leaves the case under-powered for e1 + e18 and is refused.
- Either arm of a unit routing to a different CZ count from its partner refuses the plan (as in the retained check).

## Owed

- The live dry run through `scripts/approved_run.sh --check` (live Target, calibration, quota, placement), and a check
  script for the placement, as `scripts/pathion_kernel_map_check.py` is for the retained map.
- One red-team pass, the Advisor review and the owner's approval of this case.
- Ledger rows for the case in `docs/evidence/a5-exceptional-fibers/ledger.tsv` (rows A5-242 and A5-606 are not on main yet).
- Seeds for the live plan: the compile owns the draw named above, so the live seed_transpiler and seed_simulator take a fresh draw.
- A Lean or Rocq statement of the algebra the case rests on (pair-split invariance of N and |c|, the exchange identity) is
  owed to gororoba-math; the case tests the device, not the algebra, and the statements above are Statevector checks.
- Owner decision: the +, -, -, + arm order with a null arm needs both orders in one calibration, which is exactly the 24-PUB
  cap with no spare; the case uses alternating arm order and the in-circuit zero character as the null.
- A Lean or Rocq statement of the pair-split invariance (N and |c| independent of b) and of the exchange identity is a
  gororoba-math source and is not written.

## Reproduction

On an aarch64 host with the pinned environment: `orientation_bit_analysis.py --self-test` and `--power DIR`, each with
`--retained-collect` naming the retained collect.json of `results/live/2026-11-06T183538.809814Z`;
`compile_case.py --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#0 ...#1 ...#2 --out DIR`;
`compile_case.py --check` recomputes the record and compares it with the committed `case_compile.json`.
