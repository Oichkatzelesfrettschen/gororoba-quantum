# Orientation-bit case for ledger row A5-242 (ibm_fez kernel map)

Status: written and verified offline, awaiting one red-team pass and the owner's approval. Nothing has run on a provider.
The case is sized for 30 replicas (owner decision, 2026-11-24): 15 disjoint regions read in two jobs.
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

Group `pathion_kernel_map_orientation`, 16 circuits (16 PUBs of the 24 the job allows), one layout, for e1 + e26 (nullity 4,
m = 27) and e1 + e18 (nullity 12, m = 19):

| Unit | Circuit | Ideal Walsh support carrying the contrast |
|---|---|---|
| ctrl | retained placement, orientation on bit 4 | contains 16 |
| move | the pairs split by bit 1, phase pi on data qubit 1 | contains 2, excludes 16 |
| xtwin | ctrl plus one X on data qubit 4 after the SELECT, before readout | the control's eight characters, with the sign of every character that carries bit 4 exchanged |
| swap | ctrl with data wires 1 and 4 exchanged (every gate on the other wire; each wire still measures into its own classical bit) | the control's, exactly: the outcome law is unchanged |

The swap unit puts data bit 4 on the physical qubit that carries data bit 1 in the other units, because a group runs on
one layout (`initial_layout` of the group in `live_run.py`). Its reading is G16 on the physical qubit of bit 1; the
control reads G16 on the physical qubit of bit 4. The pair separates the physical qubit from the logical bit and the
compiled SELECT, the row's own question. It costs 4 PUBs (2 per operand; the red-team priced one operand at 2 PUBs), 2.1 s
per job. Offline finding that sets its role: with every member routed on one layout, the models predict G16 swap equal to
G16 ctrl within 0.005 at nullity 4 and within 0.016 at nullity 12 (`diff_cs` in `case_compile.json`), so the unit
does not remove the difference between G16 ctrl and G2 move; that difference (C below) comes from the circuit and not from
the qubit, and C is tested against its model floor instead (below).

Compiled form (snapshot target, optimization level 3). The xtwin routes to the control's schedule plus one virtual rz on
the wire measured into data bit 4: the cz sequence (qubit pairs and order), the sx and x gates and the measure mapping are
identical, and the two circuits differ only in rz angles of that wire, in the stretch before its last sx, which holds cz and
rz gates only (rz commutes with cz). This held on all 60 compiles of a scratch sweep (5 tiles, 3 transpiler seeds, 2
operands, both arm phases; not retained) and is asserted on one tile and one seed per operand by
`test_exchange_compiles_to_one_frame_on_the_bit_four_wire`. The consequence for D is stated with its row below.

Bit 1 is a set bit of both m (27 = 11011b, 19 = 10011b); the common set bits are 0, 1 and 4. Bits 0 and 1 route to the
same CZ count (table below), so the choice is a tie on cost; bit 1 is the one the SELECT's input-X layer does not touch (i = 1
sets only bit 0), so its gates are the selector CNOTs alone. Bit 0 is the preregistered alternative.

Verified exactly (`tests/gororoba_quantum/test_pathion_kernel_map_orientation.py`, Statevector on an aarch64 host, 27 tests; the swap
unit's wire exchange, outcome law and measure map are asserted by `test_swap_member_exchanges_data_wires_one_and_four_and_keeps_the_law`):

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

A replica is one region (a disjoint six-qubit tile of the chip) in one job. Per replica and operand:

| Statistic | Definition | A5-242 predicts |
|---|---|---|
| G16 (ctrl) | lambda_16 - lambda_0 | sign -1 at nullity 4, +1 at nullity 12 (replication) |
| G2 (move) | lambda_2 - lambda_0 | the sign of G16 (reading i) |
| leak16 (move) | c_obs,16, ideal 0 (character 16 is outside the moved support) | 0; reported, cannot decide |
| C | G16 ctrl - G2 move, tested against the floor band below | inside the band (the gap moves at equal size) |
| G16 (xtwin) | lambda_16 - lambda_0 against the exchanged ideal | the sign of ctrl if the effect follows the operand |
| G16 (swap) | lambda_16 - lambda_0 of the swap unit: the bit-4 gap on the physical qubit of bit 1 | the sign of ctrl if the gap belongs to bit 4 and not to the physical qubit |
| S | (G16 ctrl + G16 xtwin) / 2 | nonzero if the effect follows the operand |
| D | (G16 ctrl - G16 xtwin) / 2 | zero under the row's SELECT-decay hypothesis; nonzero only for an asymmetric readout of the bit-4 physical qubit or a coherent angle error on that wire's final single-qubit tail |

Exploratory, outside the family, the power and the verdict: C against zero (`diff_cm` model floors are in the table below),
G16 swap - G2 move (`diff_sm`) and G16 ctrl - G16 swap (`diff_cs`).

What D sees. The xtwin differs from the control by one frame on the bit-4 wire after the SELECT (compiled form above), so
D is zero under any error that acts before that frame, the SELECT-decay hypothesis of row A5-242 included, and under any
error that commutes with the frame (depolarizing noise, which is unitarily covariant). It responds to asymmetric readout of
that qubit and to a coherent angle error on the tail. Relaxation enters only through the cz and idle interval that the
frame commutes through: the exact relaxation-only model predicts D = -0.00041 (nullity 4) and -0.00004 (nullity 12), about
1 percent of the control gap and under 0.5 percent of the minimum detectable effect, so D does not resolve relaxation. D
isolates the readout-asymmetry half of the row's open question (relaxation or asymmetric readout): the asymmetric-readout
model predicts D = -0.012 and -0.005.

Each is a one-sample t test over regions with n - 1 degrees of freedom; the standard error is the scatter of the region
values, so the test holds whatever the drift between regions. The case reads each region in two jobs, so the two replicas
of a region average before the test (every statistic is linear in the measured laws), which keeps the test valid for any
correlation between a region's two replicas and is the one change the 30-replica design makes to the preregistered test
(`merge_jobs`, `--regions`). Regions with equal qubit sets merge across jobs; regions that differ stay separate blocks.
The family is 16 tests (8 statistics, 2 operands); Holm's step-down procedure holds the family error at 0.05.

Floor band. C = G16 ctrl - G2 move compares two different circuits, and the noise models predict a nonzero C with no
orientation-qubit effect at all: +0.0297 (relaxation alone) and +0.0384 (all three) at nullity 4, +0.0105 and +0.0187 at
nullity 12, and up to +0.047 and +0.020 across the four models. The swap unit reads the same floor, so the floor belongs to
the circuit structure (`diff_sm`, `diff_cs` in `case_compile.json`), and no role swap removes it. C therefore has the
interval null [lower_i, upper_i] of each region i, where the edges are the smallest and largest of C over the four models
(depolarizing with symmetric readout, relaxation alone, asymmetric readout alone, all three; zero included) on that
region's own dry-run calibration (`compile_case.py --floors-from RECORD`, input `--floors` of the analysis). C rejects
when the excess beyond the upper edge or below the lower edge has a positive mean (two one-sided t tests, p = twice the
smaller). A floor inside the band reads as unresolved; only a C beyond every model floor reads as a difference. The band is
a modeling choice: the models reach 21 to 27 percent of the retained gap, so the band is bounded by the four mixtures the
offline models can build and carries no measured model error; a true floor beyond the band reads as a false difference,
and the exposure is tabulated below. Mean edges of the retained five regions: e1 + e26 [0, +0.054], e1 + e18 [-0.014, +0.026].

Readings, per operand:

- (i) The gap follows the orientation qubit: G2 rejected with the sign of the retained gap and C not rejected (inside its
  floor band).
- (ii) The gap stays on bit 4 whatever the orientation qubit: the control's gap replicates, C is rejected (beyond its floor
  band) and G2 does not follow (not rejected with the retained sign). The hypothesis is refuted as stated; the effect
  belongs to the physical qubit or the SELECT. This is the row's first falsifier, and C is its test: the moved support
  holds no character with bit 4, so a character-diagonal channel cannot put weight on 16 and leak16 alone cannot detect
  the mechanism; it is reported (a nonzero leak16 needs asymmetric readout or relaxation) and does not enter the verdict.
- (iv) Layout: G16 (swap) rejected with the retained sign reads that the gap travels with data bit 4 to the physical qubit of
  bit 1 (`gap_travels_with_bit_4_wire`); the control's gap replicating with G16 (swap) not rejected is reported as
  `layout_bound_candidate`, a physical-qubit effect whose absence-of-rejection reading carries the power of the table below.
  Both are reported and neither enters the verdict, whose (ii) path already refutes the hypothesis as stated.
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

Replica design and power (`power.json`, `operating.json`). The case plans 30 replicas: two jobs on up to 15 regions. A 156-qubit
chip holds at most 26 disjoint six-qubit regions and the snapshot admits 15 at guard distance 2 (10 at guard distance 3,
`disjoint_tiles_available` in `case_compile.json`), so 30 disjoint replicas do not exist, and the second job reads the
regions again. The retained five-region pattern in six jobs reads the same 5 to 15 regions six times (5 regions leave 4
degrees of freedom) and costs 63 s expected against 21 s; it is not used. Each job is a separate dry run and approval;
the second job takes whatever regions its dry run places (regions with equal qubit sets merge into one block, others
stay separate blocks, so the analysis has between 15 and 30 blocks). The analysis averages the replicas of a region before
the t test (see the statistics section), so the test has n - 1 = 14 degrees of freedom when the regions repeat and its
size holds whatever the correlation rho between a region's two replicas. Pairing within a region is unchanged: the plus and
minus arms of a unit are adjacent PUBs of one job, and the unit's contrast pairs them; the second job repeats that pairing
on the same region, so a region-persistent bias is a blocking factor that the averaging absorbs.

The per-replica standard deviation of a gap is the standard error of five replicas, minus_zero over minus_zero_t of
`result_spectral.json`, times the square root of 5: 0.0906 (e1 + e26, effect -0.155) and 0.0808 (e1 + e18, effect
+0.103). The scatter of C is estimated by the standard deviation over the five retained replicas of G16 of the primary
minus G16 of its quarter-turn twin on the same region (two circuits on one region): 0.0835 and 0.0818, correlations 0.49
and 0.14 (`power.json`; a weak estimate from five replicas). The scatter of S, D and the twin gap come from the same
five replicas (primary and retained twin); leak16 takes the shot-noise scale 0.017. The standard deviation of a region's
mean of two replicas is sd x sqrt(rho + (1 - rho) / 2); rho is unknown and between 0 (independent replicas) and 1 (the
second job adds nothing), so the table gives both. Level 0.05 / 16 = 0.0031 per test (Holm's first step), power by the
exact noncentral t over 15 regions, effect = the retained effect and half of it; C is read beyond the upper edge of its
floor band (mean edge 0.054 and 0.026), so its effect is the retained effect less that edge (0.102 and 0.078), the worst
case in which the true floor is zero.

| Statistic | Operand | Retained effect | SD per replica | Power at full effect, rho 0 / rho 1 | Power at half effect, rho 0 / rho 1 | Minimum detectable effect, rho 0 / rho 1 |
|---|---|---|---|---|---|---|
| G16 ctrl | e1 + e26 | 0.155 | 0.091 | 1.000 / 0.995 | 0.841 / 0.444 | 0.075 / 0.106 |
| G16 ctrl | e1 + e18 | 0.103 | 0.081 | 0.998 / 0.887 | 0.504 / 0.198 | 0.067 / 0.095 |
| G2 move | e1 + e26 | 0.155 | 0.091 | 1.000 / 0.995 | 0.841 / 0.444 | 0.075 / 0.106 |
| G2 move | e1 + e18 | 0.103 | 0.081 | 0.998 / 0.887 | 0.504 / 0.198 | 0.067 / 0.095 |
| G16 swap | e1 + e26 | 0.155 | 0.091 | 1.000 / 0.995 | 0.841 / 0.444 | 0.075 / 0.106 |
| G16 swap | e1 + e18 | 0.103 | 0.081 | 0.998 / 0.887 | 0.504 / 0.198 | 0.067 / 0.095 |
| C = G16 ctrl - G2 move (beyond the band) | e1 + e26 | 0.102 | 0.083 | 0.995 / 0.845 | 0.448 / 0.172 | 0.069 / 0.098 |
| C = G16 ctrl - G2 move (beyond the band) | e1 + e18 | 0.078 | 0.082 | 0.922 / 0.563 | 0.229 / 0.083 | 0.068 / 0.096 |
| G16 xtwin | e1 + e26 | 0.066 | 0.071 | 0.907 / 0.536 | 0.215 / 0.078 | 0.059 / 0.083 |
| G16 xtwin | e1 + e18 | 0.059 | 0.028 | 1.000 / 1.000 | 0.971 / 0.693 | 0.023 / 0.033 |
| S | e1 + e26 | 0.111 | 0.070 | 1.000 / 0.985 | 0.758 / 0.361 | 0.058 / 0.082 |
| S | e1 + e18 | 0.081 | 0.045 | 1.000 / 0.998 | 0.893 / 0.514 | 0.037 / 0.052 |
| D | e1 + e26 | 0.045 | 0.042 | 0.974 / 0.705 | 0.319 / 0.117 | 0.035 / 0.049 |
| D | e1 + e18 | 0.022 | 0.041 | 0.334 / 0.123 | 0.046 / 0.020 | 0.034 / 0.048 |
| leak16 move | e1 + e26 | none (ideal 0) | 0.017 | n/a | n/a | 0.014 / 0.020 |
| leak16 move | e1 + e18 | none (ideal 0) | 0.017 | n/a | n/a | 0.014 / 0.020 |

Reading of the table. At rho 1 the design equals the earlier 15-replica plan and holds power 0.8 for the three gaps (0.887
at nullity 12); at rho 0 it equals 30 independent replicas with the t quantile of 14 degrees of freedom (the all-replica
test with 29 degrees of freedom has the smaller minimum detectable effects 0.061 to 0.068 in `power.json`). The half
retained effect has power 0.20 to 0.84 on the gaps, so a smaller true effect reads unresolved and not refuted
(the retained effects were chosen after the data from six units). The floor band costs C power at nullity 12 (0.92 at
rho 0, 0.56 at rho 1): a real bit-4-bound gap of the retained size at nullity 12 is then more likely to read unresolved
than refuted. D at nullity 12 (power 0.12 to 0.33) cannot resolve a readout asymmetry of its predicted size (-0.005);
D at nullity 4 (-0.012 predicted against a minimum detectable 0.035 to 0.049) cannot either. leak16 detects 0.014 to 0.020
and decides nothing.

Operating characteristics of the rule (`orientation_bit_analysis.py --operating`): the probability of each row reading
when the truth is a model floor of `case_compile.json` with or without an operand-following effect, over 15 region
means (4096 trials per cell, the exact law of the sample mean and covariance at deterministic Sobol points, scatter and
correlations of the retained five replicas, rho 0 and 1), for the band rule and for the superseded rule that tested C
against zero.

| Truth | rho | Band rule: supported / refuted / unresolved | Zero-null rule: supported / refuted / unresolved |
|---|---|---|---|
| no floor, no effect | 0 | 0.000 / 0.004 / 0.996 | 0.000 / 0.004 / 0.996 |
| | 1 | 0.000 / 0.004 / 0.996 | 0.000 / 0.004 / 0.996 |
| relaxation-only floor | 0 | 0.000 / 0.001 / 0.999 | 0.000 / 0.002 / 0.998 |
| | 1 | 0.000 / 0.002 / 0.998 | 0.000 / 0.002 / 0.998 |
| all-three-model floor | 0 | 0.000 / 0.004 / 0.996 | 0.000 / 0.005 / 0.995 |
| | 1 | 0.000 / 0.003 / 0.997 | 0.000 / 0.004 / 0.996 |
| all-three floor + half the retained gap, operand-following | 0 | 0.083 / 0.001 / 0.916 | 0.066 / 0.029 / 0.906 |
| | 1 | 0.012 / 0.002 / 0.985 | 0.013 / 0.010 / 0.978 |
| all-three floor + the retained gap, operand-following | 0 | 0.950 / 0.000 / 0.050 | 0.683 / 0.004 / 0.312 |
| | 1 | 0.667 / 0.001 / 0.331 | 0.592 / 0.010 / 0.398 |

| Truth | rho | e1 + e18 reading (ii), band rule / zero-null rule | e1 + e26 reading (ii), band rule / zero-null rule |
|---|---|---|---|
| all-three floor + half the retained gap, operand-following | 0 | 0.001 / 0.029 | 0.000 / 0.000 |
| all-three floor + half the retained gap, operand-following | 1 | 0.002 / 0.009 | 0.000 / 0.000 |
| all-three floor + the retained gap, operand-following | 0 | 0.000 / 0.004 | 0.000 / 0.000 |
| all-three floor + the retained gap, operand-following | 1 | 0.001 / 0.010 | 0.000 / 0.000 |

Reading of the operating table. The relaxation floor alone cannot refute the row: reading (ii) needs the control's own gap
to replicate at the Holm level, and the model's own gaps (-0.044 and -0.033 at nullity 4) sit at about 1.4 to 1.9 standard
errors against a threshold near 3.6, so the row reads unresolved in at least 99.5 percent of trials under the floors, for
both rules. The exposure of the zero-null rule is a true operand-following gap that C then reads as different: at half the
retained gap it refutes the row in 2.9 percent of trials at rho 0 and 1.0 percent at rho 1 (0.1 and 0.2 percent under the
band rule), and it costs the supported reading 27 points at rho 0 (0.683 against 0.950) and 8 points at rho 1 with the full
gap. The null of the family itself reads refuted in 0.4 percent of trials. The band rule's own exposure is a floor above its
edge, which the models cannot exclude (stated above). A true effect smaller than the minimum detectable reads unresolved.

The retained scatter is itself a risk: two of the five retained replicas of e1 + e26 and of its twin read a visibility near
zero (0.004, -0.033 and 0.027, 0.007 against 0.14 to 0.26 on the others), so the dead-region rule above applies to the
live run, and the standard deviations above, which include those regions, can overstate the scatter of the live ones. The
off-support coefficient c_obs,16 of the retained units has a median scatter of 0.012 to 0.017 over replicas (the shot-noise
scale of 32 bins at 16,384 shots), which sets the scale of leak16.

## Routed cost (retained snapshot, `case_compile.json`)

Basis cz, rz, sx, x, optimization level 3 (`live_run.OPT_LEVEL`), five best-ESP six-qubit tiles of the snapshot, three
transpiler seeds (draw `docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json`, indices 0 to 2). Every member of a tile and
seed routes on the layout of the first operand's control, as the live run routes a group on one layout. CZ count on all 15
(tile, seed) pairs:

| Member | e1 + e26 | e1 + e18 |
|---|---|---|
| ctrl, move (bit 1), xtwin, alternative bit 0, retained primary of the same compile | 155 to 167 | 158 to 160 |
| swap (wires 1 and 4 exchanged) | 158 to 170 | 161 to 163 |
| retained twin, same compile | 155 | 153 to 155 |

Every moved circuit and the alternative bit 0 has ratio 1.00 to its control (the 20 percent rejection bound is not reached; the
oracle's diagonal synthesis has a data-independent CZ network); the swap unit has ratio 0.95 to 1.02 at nullity 4 and 1.01
to 1.03 at nullity 12. The retained live compile read 136 to 173 (167 and 155 for the nullity-4 pair); this compile is in
range. Live CZ counts are owed to the dry run.

## Noise prediction (retained snapshot)

Snapshot rows. An exact density-matrix run (no sampling) of the routed circuits under a depolarizing model from the snapshot
(each cz at its coupler error, sx and x at their qubit error, a symmetric readout flip at the measure error), on the five
tiles as replicas. Statistics, mean and 95 percent t interval over tiles:

| Statistic | e1 + e26 | e1 + e18 |
|---|---|---|
| G16 ctrl (= xtwin = S) | -0.0118 [-0.0147, -0.0089] | -0.0084 [-0.0135, -0.0034] |
| G16 swap | -0.0108 [-0.0137, -0.0080] | -0.0089 [-0.0140, -0.0037] |
| G2 move | -0.0268 [-0.0339, -0.0196] | -0.0283 [-0.0344, -0.0222] |
| leak16 move | -0.0013 [-0.0016, -0.0009] | +0.0009 [0.0007, 0.0012] |
| C = G16 ctrl - G2 move | +0.0149 [0.0094, 0.0205] | +0.0199 [0.0135, 0.0262] |
| G16 ctrl - G16 swap | -0.0010 [-0.0020, 0.0001] | +0.0005 [-0.0006, 0.0015] |
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
| G16 ctrl | depolarizing, symmetric readout | -0.0140 | -0.0118 |
| G16 ctrl | relaxation only | -0.0437 | -0.0003 |
| G16 ctrl | asymmetric readout only | -0.0072 | -0.0421 |
| G16 ctrl | all three | -0.0327 | -0.0053 |
| G2 move | all three | -0.0704 | -0.0233 |
| G16 swap | all three | -0.0324 | -0.0101 |
| C = G16 ctrl - G2 move | depolarizing | +0.0264 | +0.0201 |
| C = G16 ctrl - G2 move | relaxation only | +0.0336 | +0.0105 |
| C = G16 ctrl - G2 move | asymmetric readout only | +0.0470 | +0.0037 |
| C = G16 ctrl - G2 move | all three | +0.0377 | +0.0180 |
| D | depolarizing, relaxation only, asymmetric readout only, all three | 0, -0.0004, -0.0124, -0.0040 | 0, -0.00004, -0.00507, -0.00177 |

Relaxation alone reaches the retained sign at nullity 4 at 28 percent of the size (-0.044 against -0.155; all three
together 21 percent) and does not reach the retained sign at nullity 12 (-0.0003 against +0.103); no model predicts a
positive gap at either nullity. The models also predict a C of +0.004 to +0.047: a floor from the two circuits that stays
below the minimum detectable effect (0.07 to 0.10) and equals 0.3 to 2.0 standard errors of C over 15 regions (0.0835
and 0.0818 per replica), which is why C is tested against its floor band and why the swap unit, which reads the same
floor (G16 ctrl - G16 swap within 0.01), does not remove it. Intervals of the snapshot table reflect tile scatter of the
exact model and exclude shot noise.

Why a simulation cannot answer the question: no modeled combination of depolarizing error, relaxation and asymmetric
readout predicts the retained positive gap at nullity 12 (+0.103, against -0.007 to -0.037), and the nullity-4 gaps reach
at most 27 percent of the retained -0.155; the remainder, and the sign at nullity 12, belong to an effect the models omit,
which is what the device measurement tests. The comparison rests on one calibration of one day and five regions; a
different day's T1 and T2 shift the relaxation share, which the dry run's live calibration reads.

## Backend, shots, expected seconds

- Backend ibm_fez (the retained device; a second backend is a separate case). Account and quota read at the dry run: the
  window is 600 s rolling and 484 s were free at the last read.
- 16 PUBs per job, 16,384 shots per PUB, repetition delay 20 us, replica floor 0.7 (as retained), 15 regions per job when
  the dry run places them; two jobs (the second a separate dry run and approval).
- Expected seconds per job: 2 s of overhead plus 16 PUBs at the retained 0.533 s per PUB (14.8 s expected over 24 PUBs in the
  retained case, 18 s measured, 0.75 s per PUB with overhead) is 10.5 s expected and 12.0 s at the measured rate. Two jobs:
  21.1 s expected, 24 s at the measured rate; ceiling 18 s per job, 36 s in total, reserve 20 s, so at most 56 s of the
  484 s free in the 600 s rolling window (9 percent). Replica count adds no device seconds, since regions pack inside each
  PUB; the six-job retained pattern would cost 63 s expected and is not used. If a dry run places fewer than 15 regions the
  job count per pass rises (ceil(15 / regions)) with the same 10.5 s per job.
- Credits: IBM Open plan quantum seconds only; 0 credits.
- Arm order: arms alternate (plus first on unit 1, minus first on unit 2, and so on), each unit's two arms adjacent. This
  places each arm early and late in the job; it is a partial balance, not the +, -, -, + order, whose full form needs both orders in
  one calibration and doubles the PUBs.

## What the run measures

Whether the retained gap of character 16 moves with the orientation phase to data qubit 1 and whether it keeps or flips
sign under the exchange of the bit-4 states, on the device, over 15 disjoint regions each read in two jobs (30 replicas), with one family-wise error of 0.05.
Reading (ii) refutes A5-242 as stated; reading (i) with operand-following (iii) supports an operand-following
orientation-qubit effect and leaves the mechanism hypothesis (SELECT-set decay) open; a rejected D reports an asymmetric
readout or tail-angle effect of the bit-4 qubit, the half of the row's open question that the retained separate-compile
twins could not isolate, and D = 0 leaves relaxation and readout asymmetry unseparated.

## Falsifiers of the design

- The routed CZ of a moved circuit departing by more than 20 percent from its control rejects bit 1 and selects bit 0.
- A dry-run plan placing fewer than five regions at floor 0.7 changes the run count; fewer than 14 distinct regions in total
  leaves the case under-powered for e1 + e18 at rho 1 (`regions_needed_if_replicas_of_a_region_are_identical` in
  `power.json`) and is refused.
- Either arm of a unit routing to a different CZ count from its partner refuses the plan (as in the retained check); a swap
  unit departing by more than 20 percent from its control refuses it too (0.95 to 1.03 on the snapshot).
- A dry-run floor band whose upper edge exceeds the retained effect of C (0.155 and 0.103) leaves C unable to decide and
  refuses the plan.

## Owed

- The live dry run through `scripts/approved_run.sh --check` (live Target, calibration, quota, placement), and a check
  script for the placement, as `scripts/pathion_kernel_map_check.py` is for the retained map.
- One red-team pass, the Advisor review and the owner's approval of this case.
- Ledger rows for the case in `docs/evidence/a5-exceptional-fibers/ledger.tsv` (rows A5-242 and A5-606 are not on main yet).
- Seeds for the live plan: the compile owns the draw named above, so the live seed_transpiler and seed_simulator take a fresh draw.
- A Lean or Rocq statement of the algebra the case rests on (pair-split invariance of N and |c|, the exchange identity) is
  owed to gororoba-math; the case tests the device, not the algebra, and the statements above are Statevector checks.
- Owner decision: the +, -, -, + arm order with a null arm needs both orders in one calibration, 32 PUBs against the 24-PUB
  cap; the case uses alternating arm order (16 PUBs) and the in-circuit zero character as the null.
- The floor band comes from `compile_case.py --floors-from RECORD` on the dry-run record of each job. The reader is
  verified on the retained live record only; that a dry-run record carries the same `placed_qubit_calibration` and
  `calibration_fingerprint` fields is checked at the dry run.
- The band rests on four offline noise mixtures on one calibration day and five regions; a live floor outside the band is an
  unmodeled difference between the circuits and reads as a difference of C.
- A Lean or Rocq statement of the pair-split invariance (N and |c| independent of b) and of the exchange identity is a
  gororoba-math source and is not written.

## Reproduction

On an aarch64 host with the pinned environment: `orientation_bit_analysis.py --self-test` and `--power DIR`, each with
`--retained-collect` naming the retained collect.json of `results/live/2026-11-06T183538.809814Z` (`--power` reads
`DIR/case_compile.json`); `--operating DIR` writes `operating.json` from `power.json` and `case_compile.json`;
`--analyze COLLECT... --regions JSON... --floors JSON...` reads the collected jobs;
`compile_case.py --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#0 ...#1 ...#2 --out DIR`;
`compile_case.py --check` recomputes the record and compares it with the committed `case_compile.json`;
`compile_case.py --floors-from RECORD --seed-transpiler REF --out DIR` writes `DIR/floors.json`.
