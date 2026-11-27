# Architecture of the A5-242 orientation-bit plan on the three Heron devices

Status: analysis of the three dry runs of 2026-11-27 and of redesigns; nothing was submitted. Case:
[pathion-kernel-map-orientation-bit.md](pathion-kernel-map-orientation-bit.md). Evidence and script:
docs/evidence/pathion-kernel-map/orientation-architecture/ (orientation_architecture.py --check; retained inputs
device_*.json, patterns.json, circuits.json, designs.json, coset.json; derived results.json).

Evidence classes: "record" is a retained dry-run record under results/live; "model" is the offline placement model that
this analysis validates against the records; "compile" is a transpile on the live Target of ibm_kingston (it reproduces
the dry-run compile of that backend gate for gate, 8 of 8 units); "exact" is a Statevector or Operator equality;
"inference" is a prediction that a dry run can falsify. No hardware ran.

## 1. Devices

Properties come from the backend at each dry run's calibration (historical properties of the same calibration date). The
fez and marrakesh calibrations advanced after their dry runs (14:59:25 and 14:57:13 against 14:30:34 and 14:23:04); no
stored qubit or CZ field changed (0 of 1092 qubit fields and 0 of 352 CZ fields differ), so the recalibration stamps
leave every placement input as it was and the model cannot test drift.

| Backend (calibration, PST) | Healthy qubits | T1 us min/median/max | T2 us | Readout error | sx error | CZ error (healthy couplers) |
|---|---|---|---|---|---|---|
| ibm_fez (14:30:34) | 134 | 37 / 139 / 249 | 22 / 102 / 249 | 0.0029 / 0.0104 / 0.076 | 1.2e-4 / 3.2e-4 / 3.8e-3 | 0.0016 / 0.0023 / 0.028 |
| ibm_kingston (14:49:15) | 137 | 34 / 258 / 490 | 28 / 146 / 579 | 0.0029 / 0.0103 / 0.075 | 9e-5 / 2.4e-4 / 1.2e-3 | 0.0009 / 0.0017 / 0.022 |
| ibm_marrakesh (14:23:04) | 134 | 41 / 171 / 334 | 21 / 89 / 358 | 0.0024 / 0.0137 / 0.079 | 1.1e-4 / 3.7e-4 / 3.0e-3 | 0.0010 / 0.0023 / 0.026 |

Live exclusions (policy: readout above 0.08, CZ above 0.03, sx above 0.01, T1 or T2 below 20 us, missing T1 or T2;
operator exclusions fez 2-4 and 16, kingston 0-4 and 16): fez 22 qubits (12 T1/T2, 5 readout, 4 operator, 1 missing
calibration) and 16 directed couplers; kingston 19 qubits (8 T1/T2, 6 operator, 3 readout, 1 sx, 1 missing) and 18
couplers; marrakesh 22 qubits (10 T1/T2, 9 readout, 3 missing; no operator list, so its first region sits on qubits
2-6 and 16) and 14 couplers. The record carries each reason; the model re-derives the same sets from the properties
(all three match).

### ln(score) of every placed region

live_run.layout_score is esp x coherence: esp is the product of 1 - error over every CZ, sx, x and measurement of the
routed primary (ctrl, e1+e26, plus arm), and coherence is exp(-T sum_q 1/T2_q) over the six qubits for the scheduled
duration T. The model splits ln(score) into CZ, sx, x, rz (error 0), measure and coherence terms (model values equal
the record's esp, coherence and duration to 1e-15).

| Backend | T of region 0 | coherence term (min to max over regions) | CZ term | measure term | sx term | x term | Dominant term |
|---|---|---|---|---|---|---|---|
| ibm_fez (4 regions) | 14.0 us | -0.53 to -0.75 | -0.29 to -0.36 | -0.07 to -0.13 | -0.07 to -0.13 | -0.001 | coherence in 4 of 4 |
| ibm_kingston (8) | 16.1 us | -0.42 to -0.72 | -0.16 to -0.40 | -0.05 to -0.10 | -0.04 to -0.08 | -0.003 | coherence in 8 of 8 |
| ibm_marrakesh (3) | 18.2 us | -0.78 to -1.02 | -0.29 to -0.35 | -0.05 to -0.13 | -0.10 to -0.14 | -0.001 | coherence in 3 of 3 |

The idle-dephasing term is the largest negative term of every region (15 of 15). It scales with T, which the routed CZ
chain sets, so a shorter routed circuit lowers the dominant term directly.

### Why 4, 8 and 3 regions

Model (orientation_model.py): enumerate every embedding of the compiled pattern (the 6-qubit tree of every touched
qubit and CZ, union over the 16 members) into the healthy coupling graph, score each by the term sum above, keep those
within floor 0.7 of the best, then take them best first, skipping any whose qubits meet an earlier region or its
neighbors (guard 1).

| Backend | Embeddings (floor 0) | Within floor 0.7 | Placed | Blocked by overlap or guard | Below floor | Best below floor against cut |
|---|---|---|---|---|---|---|
| ibm_fez | 114 | 18 | 4 | 14 | 96 | 0.249 against 0.261 |
| ibm_kingston | 150 | 49 | 8 | 41 | 101 | 0.313 against 0.315 |
| ibm_marrakesh | 156 | 30 | 3 | 27 | 126 | 0.189 against 0.193 |

selection_trace of the three records holds only the capability and routing admission stages (nothing rejected); the
rejected placements above are the model's. Validation (--check): exclusion sets equal the records, floor candidate
counts equal the records (18, 49, 30), placed counts are 4, 8 and 3, every placed score and every region's esp,
coherence and duration equal the records, and the per-PUB duration bound (hence the charge of 11.37, 12.23 and 12.74
s) equals the records' to one dt. The three runs are the sample; the model had no free parameter.

The case's 15 regions are a geometric tile count. With guard 1 the exact maximum of disjoint, guard-separated
embeddings (0-1 program, floor 0) is 11 (fez), 13 (kingston) and 13 (marrakesh) for the retained pattern, so the
admission minimum of 14 regions in scripts/pathion_kernel_map_orientation_check.py is unreachable on all three devices
whatever the calibration. Lifting the operator exclusions gains at most one region (kingston 8 to 9).

## 2. Circuits

Logical CZ (all-to-all, level 1) of a member: oracle diagonal 30 (five-qubit DiagonalGate, 2^5 - 2), SELECT diagonal 62
(six-qubit DiagonalGate), CX fan 4 (e1+e26) or 3 (e1+e18) for the XOR of i and j; H layers, the orientation and
selector phase, the X layer and the final H cost 0. Totals 96 and 95, identical for ctrl, move, xtwin and swap.

Routed (compile, kingston Target, dry-run layout and seed 23084, prefix compiles; the marginal of a stage re-optimizes
globally, the sums equal the full compiles):

| Stage | e1+e26 logical | e1+e26 routed | e1+e18 logical | e1+e18 routed |
|---|---|---|---|---|
| H layer, orientation and selector phase | 0 | 0 | 0 | 0 |
| oracle diagonal | 30 | 44 | 30 | 44 |
| SELECT diagonal | 62 | 94 | 62 | 77 |
| CX fan | 4 | 10 | 3 | 4 |
| X layer, final H | 0 | 0 | 0 | 0 |
| Total | 96 | 148 | 95 | 125 |

Routing adds 52 CZ (54 percent) at e1+e26 and 30 (32 percent) at e1+e18; the SELECT diagonal carries most of it.

The 125 of today and the 158 to 160 of the snapshot: the six qubits of a tile form a tree (heavy-hex has no triangle),
and the routed count is a function of the tile shape and of which logical qubit sits on which tree node. Enumerating all
720 assignments on a spider(2,2,1) tile of kingston at one fixed seed gives the control e1+e18 a minimum of 125, a
median of 153 and a maximum of 188; 125 occurs in 2 of 720 assignments (0.3 percent), and 71 to 77 percent of the
assignments cost 158 to 160 or less. The dry-run compile of fez and kingston found the optimum of that shape; the
snapshot compile at its best-ESP tile sits at a typical assignment. Marrakesh's Sabre layout fell on a different tile
shape (spider(3,1,1), minimum 156 at e1+e18, 160 obtained). The swap unit's excess is the same effect: it exchanges
logical wires 1 and 4, so its cost depends on whether those wires sit adjacent; at the retained layout optimum it is
159 and 152 (e1+e26 +9 percent, e1+e18 +21.6 percent, past the 20 percent bound), at the merged optimum below it is
102 and 92 (+3 and -1 percent).

Seeds of the search and its two confirmations are values 30, 31 and 32 of docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json
(reserved rows of docs/evidence/qrng_seeds/allocations.json).

## 3. Design candidates

The model drives every row: regions at floor 0.7 and guard 1 unless stated; seconds are 2 + shots x sum over the 17 PUBs
of (rep delay 20 us + the longest placed replica's duration), the charge method of the admission check; power is the
case's noncentral-t power (orientation_bit_analysis.power_at, retained scatter and effects, alpha 0.05/16) for G16 of
the control, per operand, with one job. A smaller circuit may also shrink the scatter; no measurement supports that, so
power uses the retained scatter (inference). Falsifier for every row: a dry run (no --submit) with the stated flags.

### (a) Placement rule

| Rule (retained dry-run compile) | fez | kingston | marrakesh | Worst region score at that rule |
|---|---|---|---|---|
| floor 0.7, guard 1 (today) | 4 | 8 | 3 | 0.285, 0.329, 0.201 |
| floor 0.5, guard 1 | 5 | 11 | 7 | 0.218, 0.249, 0.142 |
| floor 0.3, guard 1 | 8 | 11 | 9 | 0.142, 0.249, 0.084 |
| floor 0.7, guard 0 | 4 | 8 | 3 | 0.285, 0.342, 0.201 |
| exact maximum, floor 0, guard 1 | 11 | 13 | 13 | not ranked |

Lowering the floor buys regions of lower score (the dead-region rule, visibility below 0.05, already removed two of
five retained regions at scores 0.25 to 0.35, so a lower floor trades regions for dead regions). Per-member patterns
change nothing: all 16 members use the same five-coupler tree (model, 16 of 16). Guard 0 adds nothing beyond the guard-1
count at floor 0.7 (kingston 8 both ways) and drops the one-hop crosstalk separation. The operator exclusions cost
at most one region. Falsifier: --replica-floor 0.5 places other than 5, 11 and 7.

### (b) Architecture-aware synthesis

Pinned qiskit 2.6.2 offers synth_cnot_phase_aam, synth_cnot_depth_line_kms, synth_cnot_count_full_pmh,
synth_cx_cz_depth_line_my, synth_cz_depth_line_mr, the LNN permutation synthesizers, CNOT-dihedral synthesis and
synth_mcx_*; none synthesizes a diagonal of arbitrary angles under a coupling map (AAM and CNOT-dihedral take multiples
of pi/4; DiagonalGate is the all-to-all Gray-code form). No external literature is cited.

b1, merge the diagonals. The oracle acts on the data qubits only, so it commutes with the selector's H and with the
orientation phase and joins the SELECT diagonal that follows: one six-qubit DiagonalGate with signs oracle(x) x
select(x, a). Operator equality with the retained member is exact on both arms for all eight units (Operator). Logical
CZ falls from 96 and 95 to 64 and 63. Routed on the spider(2,2,1) tile at the best of 720 assignments (confirmed at two
further seeds, identical sums):

| Unit | e1+e26 | e1+e18 |
|---|---|---|
| ctrl, xtwin | 99 | 93 |
| move | 95 | 93 |
| swap | 102 | 92 |

Sum of the eight units 766 against 1122 for the retained best (-32 percent); every unit 26 to 39 percent below the
retained best, swap ratios 1.03 and 0.99, so the 20 percent bound holds by layout and needs no dropped unit. On the
other tile shapes the merged best is 839 (spider 3,1,1) and 1078 (path), so the tile shape is part of the design (a
pinned layout; whether live_run's --pin-layout carries it through placement is untested).

| Merged, optimal layout | fez | kingston | marrakesh |
|---|---|---|---|
| regions at floor 0.7 (retained: 4, 8, 3) | 4 | 8 | 6 |
| regions at floor 0.5 (retained: 5, 11, 7) | 7 | 11 | 6 |
| best and worst score at floor 0.5 | 0.484, 0.257 | 0.562, 0.357 | 0.405, 0.290 |
| expected seconds per job (retained: 11.4, 12.2, 12.7) | 10.4 | 11.2 | 11.1 |

At floor 0.5 the merged circuits place regions whose worst score (0.26, 0.36, 0.29) matches or exceeds the retained
worst at floor 0.7 (0.285, 0.329, 0.201). The seconds fall 9 to 13 percent only: the repetition delay and job
overhead are 7.6 s of a charge near 11 s. Power for G16 of the control with one job: 4 regions 0.085 (e1+e26) and 0.043
(e1+e18); 7 regions 0.505 and 0.245; 8 regions 0.659 and 0.346; 11 regions 0.926 and 0.644; 13 regions (the geometric
bound) 0.980 and 0.791. Two jobs read 7 regions at rho 0 give 0.864 and 0.563. The power of C (e1+e18, beyond its band)
is 0.32 at 11 regions and 0.45 at 13. Falsifier: a dry run on a pinned spider(2,2,1) tile compiles to other counts than
the table, or places other region counts.

b2, sparse phase polynomial. The merged diagonal has 44 (e1+e26) and 40 (e1+e18) nonzero parities of 63. A CX network
that visits only those (groups by highest qubit, greedy Hamming order, own code, Operator-equal) reaches logical CZ 56 and
51. Routed, the best of 720 assignments sums to 894 against 766 for b1: the sparse form routes worse on the tile
(measured negative; b1 stays).

### (c) Smaller register

Question from the IQM case (PR 1039, coset blocks of the kernel map): do the A5-242 statistics survive on a coset block
that contains bits 4 and 1? Exact statevector over all 35 three-dimensional subspaces V that contain m, four cosets each
(140 blocks per operand), with the orientation split by bit 4 (control) and bit 1 (moved). A block keeps the test when
(A) the control's per-output contrast has a nonzero Walsh coefficient at the character of bit 4, (B) the moved unit has
one at the character of bit 1 and none at that of bit 4, (C) the two characters differ, (D) the zero character is
nonzero in both, and (E) the (zero, signature) magnitudes agree between the units, as they do at six qubits.

| Operand | A | B | C | D | E (weight-matched) |
|---|---|---|---|---|---|
| e1+e26 (nullity 4) | 133 | 26 | 26 | 10 | 2 |
| e1+e18 (nullity 12) | 103 | 9 | 9 | 5 | 0 |

e1+e26 has two weight-matched blocks: basis [27, 3, 5] coset 9 and basis [27, 3, 12] coset 5 (coefficients 0.25 and
-0.25 for control and moved at the zero and signature characters). e1+e18 has none: five blocks keep A to D with
unequal weights, so G16 and G2 would compare unequal quantities and the floor band (built for the weight-matched pair)
would not apply. On a block the case therefore reads (i) and (ii) for the nullity-4 operand at most; the nullity-12
operand (the positive gap, the replication across nullities) stays on the six-qubit register. Neither block contains
16, so the bit-4 exchange (xtwin, D) has no counterpart inside it; the swap unit was not examined on a block.

Price of block [27, 3, 5] coset 9 (four qubits, logical CZ 21 control and 19 moved; routed on the best of 24
assignments at one seed): star tile 28 and 27, path tile 31 and 30. Regions at floor 0.7 (guard 1): star tile fez 15,
kingston 14, marrakesh 12 (worst scores 0.60, 0.70, 0.54; best 0.81, 0.84, 0.76); path tile 17, 15 and 17. A block
covers one quarter of the pairs, so it is a nullity-4 probe with 12 to 17 regions, not a replacement. Falsifier: the
measured sd of the block gap on hardware exceeds the retained 0.09 enough to cancel the region gain (no measurement
exists).

### (d) The swap unit

The swap excess past 20 percent is a layout effect (section 2), not a property of the unit: b1 with the optimal layout
gives swap ratios 1.03 and 0.99, so the unit stays and the bound holds. The unit's role (separating the physical qubit
from the logical bit) is unchanged by the merge; the case's finding that G16 swap equals G16 ctrl within the model
floor holds because the operator is unchanged.

## 4. Invariants of a re-synthesis

Checked by --check unless marked: (1) operator equality with the retained circuit for every role and operand on both arms
(exact, 16 of 16 for merged and for sparse); (2) equal CZ on both arms (the plus and minus arms are one parametrized
circuit; the three records show equal counts for every plus and minus pair); (3) one layout per tile (the six-qubit
layout is a permutation of one tile in every design); (4) the xtwin equals the control plus one frame on the bit-4
wire (the non-rz gate sequence of xtwin equals the control's in every design and operand, 2 of 2 for each design; the
rz frame lies on the bit-4 wire, as the case states); (5) a successor module: merged_template and sparse_template live
in the analysis; a production member needs its own module beside pathion_kernel_map_orientation.py, whose bytes and the
digest-pinned pathion_kernel_map.py stay. The ratio bound of the admission check (20 percent of the control) holds in
the merged optimum (maximum 1.03).

## 5. Open items

- Pin: the merged optimum needs the tile shape and assignment held through placement; run a dry run with --pin-layout on
  each backend before any approval, because the retained path leaves the layout to Sabre (marrakesh drew a worse shape).
- Admission: MIN_REGIONS 14 cannot be met; a minimum near 8 (kingston) or 11 (floor 0.5, merged) follows from section 3.
- Records: the three results/live/archives/*.qpy files are the isa.qpy of the three dry runs (each record's
  isa.qpy.sha256 names its file); collect.py reads them to build patterns.json, and the offline check does not.
- Reproduce: "$PYTHON" docs/evidence/pathion-kernel-map/orientation-architecture/orientation_architecture.py --check
  (offline); --recompute-circuits needs the live Target of ibm_kingston.

