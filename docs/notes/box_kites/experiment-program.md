# Box-kite experiment program: QX, Ry emulator and Tuna-17

Design only. No circuit below has been generated or submitted; every
submission waits for the owner's approval of its written case (root
AGENTS.md, "Quantum Inspire"). Dates in this note date the measurements they
cite.

## 1. What each backend can establish

The census settles the algebra. `scripts/box_kite_census.py` derives every
box-kite fact and every ideal probability below from `cd_core.cd_sign`, and
retains them in [census.json](../../evidence/box_kite_census/census.json)
(gates core-372 and core-373). A field cited as `census:x.y` is a path into
that record. A hardware run never adds algebraic evidence: the signs in every
circuit are compiled from cd_core, so a run measures whether a stated
implementation reproduces the census prediction.

| Backend | A passing run establishes | A failing run refutes |
|---|---|---|
| QX emulator (ideal state vector) | the emitted cQASM implements the intended unitary on the platform | the generator, the cQASM emission or the platform's handling of it |
| Ry emulator (neutral-atom emulator) | the interpreter accepts the dialect and the emulator reproduces the prediction under its own model | the dialect assumption, or the emulator model's fidelity at that depth |
| Tuna-17 | the stated circuit keeps the predicted contrast under the measured noise | the separation estimate for that circuit and layout |

Theorem 7, the twist and the strut law are therefore never "confirmed by
hardware"; QX checks the implementation of the census predictions, and
Tuna-17 checks how much of the predicted contrast survives.

Monograph claims enter only as the census recomputes them;
[inventory-monographs.md](inventory-monographs.md) names the census field of
each row, and rows marked "not retained" stay second-hand.

## 2. Method: one specification, many witnesses

cd_core is the specification. The census computes every basis-product, sign
and zero-product fact from it, then recomputes the same fact bundle through
each package of the repository's Cayley-Dickson stack (root AGENTS.md,
"Cayley-Dickson, quaternion and Clifford packages"; `docs/notes/packages/`)
under that package's declared map onto cd_core, and compares digests. A
package result counts only through its declared map; agreement among packages
is never the criterion.

- D = 16, identity map: python-hypercomplex with
  `cayley_dickson_algebra(4, fractions.Fraction)` and python-hyprat at mu = -1
  (exact rationals), python-hypercomplex-engine (the fast basis-sign oracle),
  python-cayley-dickson, python-cayley-calculator (float64 coefficients, each
  required to be integral) and python-octonion-sedenion (imported with its own
  octonion module bound, because its `sedenion.py` imports the top-level
  `octonion` that python-octonion owns). python-hypercomplex-algebra wraps the
  engine and is recorded as a wrapper only: its three Design B fixture
  expressions are parsed and compared, never counted as a witness.
- D = 8: python-hypercomplex, python-hyprat, the engine, python-cayley-dickson
  and python-octonion-sedenion under the identity, python-pyoctonion, python-octonion through
  its signed relabeling pi = (0, 1, 2, 4, 3, 6, 7, 5) with a flip on its e6,
  and SageMath 10.10 `OctonionAlgebra(QQ)` through both declared relations,
  the opposite algebra in natural order and the e3/e5/e6 sign flip.
- Negative control: python-splitoct, hyprat with signs (-1, -1, +1) and the
  engine's split table. The split octonions share the XOR index and every
  associator sign with the octonions, so the associator facts and the strut
  lines (u, v, S) must agree there, while the two-blade zero products and
  nullities must differ. The census requires both, which also fixes a limit
  of family (d): an associator-sign witness cannot tell the octonions from the
  split octonions.
- No witness: the D = 4 quaternion and Clifford packages (numpy-quaternion,
  quaternionic, pyquaternion, clifford, kingdon, galgebra) and mathdunders.
  They carry no D = 8 or D = 16 product, and root AGENTS.md rests no octonion
  or sedenion statement on a Clifford algebra, so no box-kite fact has a
  witness among them.

The fact bundle at D = 16 is the 210 x 210 two-blade norm table, the kite
structure derived from it, the Design B products of every census row, the
left and right annihilator nullities, the twist counts and the associator
classes; at D = 8 it is the two-blade zero products and nullities, all 512
associator signs, the 64 basis signs and the 21 strut lines. Each fact is a
sha256 of canonical JSON (`census:package_witnesses`). In the retained record
every identity, relabeling and SageMath witness agrees with cd_core on every
fact, and each split control shares `associator_signs` and `strut_lines`
while it differs on `basis_signs`, `two_blade_zero_products` and
`two_blade_left_nullities` (`census:package_witnesses.split_control`).

CI imports no package. `--write` on the build host multiplies elements with
each package's own arithmetic and retains every verdict with the installed
version and the pinned release. `--check` recomputes the same digests through
each package's retained basis table (`docs/evidence/algebra_packages/tables.json`,
`sagemath_octonion_table.json`) under the same map and requires them to equal
the retained element verdicts, so a retained verdict follows from a retained
table; the wrapper's expressions are re-parsed. A package that fails to import
is recorded with its error and rebuilt from its PKGBUILD (root AGENTS.md)
before the record is regenerated; none is skipped. The census stops at
D = 16 (and D = 8 for the octonion-level facts); no D = 32 fact enters this
program.

## 3. Shared circuit vocabulary

**Full Design B** (root AGENTS.md, "Zero-product witnesses"). Selector plus 4
data qubits: `designs.lcu_witness` applies (L_{e_L} + L_{e_U})/2 to
y = (e_L' + y_sign e_U')/sqrt2; x_sign = -1 adds a Z on the selector after its
first H; P(selector = 0) = ||x y||^2 / 2 = `census:design_b.within_kite[]`
column `p_selector_zero`. The only Tuna-17 acquisition of it, a = e1 + e10
with 66-70 routed CZ and 26 T per replica, kept an endpoint contrast of 0.0415
+- 0.0032 (region values 0.002, 0.051, 0.072) against the ideal 1
(results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17;
[experiments.md](../quantum_inspire/experiments.md)).

**Reduced two-label LCU.** For assessors P = (L, U) and Q = (L', U') of one
kite the four product terms land on two labels, L^L' = U^U' (data d = 0) and
L^U' = U^L' (d = 1). Restricted to span{e_L', e_U'}, the LCU is a selector a
and one data qubit d: SELECT = CNOT(a -> d) after the diagonal phases
g(L,L'), g(L,U') on a = 0 and g(U,L'), g(U,U') on a = 1, and x_sign = -1 adds
a Z on the selector after its first H, the convention of full Design B; x_sign
enters once. The resulting branch coefficients are the census columns `c0`,
`c1` (selector 0) and `d0`, `d1` (selector 1), and the census requires this
restriction to reproduce P exactly on all 840 rows. The product of the
four phases is p0 p1 (`census:kites[].edges[].sign_products`,
`strut_sign_products`): +1 on every edge, so the diagonal is local Z gates and
SELECT costs one CZ; -1 on every strut, so SELECT is CNOT times CZ, which
equals Sdag on a times a controlled-Y, again one CZ. Edge and strut circuits
therefore have the same two-qubit depth. No gate checks that compile yet: the
generator verifies each emitted SELECT by unitary against the two-label
restriction, besides the state-vector check of every circuit against its
census row. Preparation is H (and Z for
y_sign = -1) on d and H on a; the final H on a precedes measurement. The circuit is a sign-pattern interference test: its
signs are compiled from cd_sign and it does not exercise the 16-dimensional
left multiplication.

**Reduced cross-kite control.** Different XOR labels put the four terms on
four labels, so a second data qubit w takes CNOT(a -> w) and the branches are
orthogonal: P = 1/2 whatever the signs (`census:design_b.cross_kite_controls`,
168 rows; `all_cross_and_nonkite_ordered_signed_pairs`: every one of the
cross-kite and non-kite signed pairs gives 1/2).

**Fixed-triple associator walk.** The Hadamard test of
W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j) on a basis input |k> moves the data
register k -> k^j -> k^j^i -> k under control, one CNOT per set bit of j, i
and i^j, and the control reads <Z_c> = omega(i, j, k) after its final H. On a
basis input the block signs are constants, so the circuit carries omega as a
compiled Z on the control: the hardware establishes coherent return of the
walked register (root AGENTS.md, "Signs, workspace and measurement basis")
and reads a compiled sign. Dropping the last block leaves the register
branch-marked and drives <Z_c> to 0 (the workspace control of
`scripts/algebra_circuit_fixtures.py`). The census retains, per kite and per
constant-sign class, the triple with the cheapest walk
(`census:associator.deterministic_exemplars`: [i, j, k, omega, CNOTs, data bits]).

**Controlled W with uniform data.** The full controlled diagonal W_ij on a
uniform data register gives <W> = (1/16) sum_k omega(i, j, k); it needs the
controlled sign diagonal, whose phases are of degree 4 and fall off Tuna's
pi/36 grid, so it runs on QX only.

## 4. Experiment families

Each family names the claim and its source, the observable (zero-product
success, associator-sign interference witness or coherence reconstruction,
never mixed), the circuit and register count, the census predictions, the
falsifier fixed before the run, and the backends.

### (a) Exhaustive edge and strut zero-product map

- Claim: the 42 assessors form 7 box-kites of 6 assessors, 3 struts and 12
  edges; every edge has exactly two vanishing sign choices, every strut none
  (monograph A1-A5, de Marrais Theorem 3; open_gororoba C-003 and C-454
  Verified, C-468 Verified; census `kites`, `theorem3_zero_sign_choices_over_49_planes`).
- Observable: zero-product success P(selector = 0).
- Circuits: full Design B (5 qubits: 4 data + selector) for all 840
  within-kite rows (7 kites x 30 ordered assessor pairs x 4 sign choices),
  the 168 cross-kite controls, the 168 ordered (l, l^8) pairs and the
  negative fixture (1,10)+ x (2,13)- (P = 1/2, product e3 + e7 + e8 - e12);
  then the same rows in the reduced encoding (2 qubits; 3 for cross-kite).
- Predictions: `census:design_b.within_kite[].p_selector_zero` in {0, 1/2, 1}:
  0 on the two zero sign choices of an edge, 1 on the other two, 1/2 on all
  four of a strut; 1/2 on every cross-kite and non-kite row. The LCU identity
  P(x_sign) + P(-x_sign) = 1 holds by construction and checks the selector Z,
  not the algebra.
- Falsifier (QX): any shot with selector 0 on a P = 0 row, or selector 1 on a
  P = 1 row, refutes that circuit's implementation; a P = 1/2 row outside
  |z| < 4.5 at 2048 shots (Bonferroni over the about 1010 P = 1/2 rows of
  both encodings at family error 0.01) refutes it. Uncertainty: the QX predictions are exact; the earlier QX
  runs of the (1,10) witness read dark 0.000, bright 1.000 and fixture 0.490.
- Backends: QX (exhaustive), Ry (subset in (f)), Tuna-17 (subset in (g)).

### (b) Theorem 7 edge-sign law and face classification

- Claim: per kite 6 same-sign and 6 opposite-sign edges; the zigzag sail has
  3 opposite edges, each of the 3 trefoil sails has 1 opposite edge, the one
  not incident to the vertex it shares with the zigzag; the vent opposite the
  zigzag has 3 opposite edges and the other 3 vents 1 (monograph A6, A7, A15;
  open_gororoba C-471, C-472 Verified; census `kites[].faces`, `edge_totals`).
  The two all-opposite faces are the "2 zigzag faces" of open_gororoba's
  `strut_table.rs`; the monographs call them the zigzag sail and its opposite
  vent, and the census classifies by computed properties (lows xor to 0 or
  not, opposite-edge count).
- Observable: zero-product success; the classification statistic of an edge
  is D = P(x_sign = +, y_sign = -) - P(+, +), ideal +1 on same-sign edges, -1
  on opposite-sign edges and 0 on struts.
- Discriminating subset: per kite the first zigzag edge (opposite), the
  trefoil edge from the shared apex to the next trefoil vertex (same) and the
  first strut, each at y_sign = +-1 (21 items, 42 replicas):

| S | zigzag edge (opposite, D = -1) | trefoil apex edge (same, D = +1) | strut (D = 0) |
|---|---|---|---|
| 1 | (3,10)(5,12) | (6,15)(2,11) | (2,11)(3,10) |
| 2 | (1,11)(6,12) | (1,11)(4,14) | (1,11)(3,9) |
| 3 | (2,9)(5,14) | (5,14)(1,10) | (1,10)(2,9) |
| 4 | (1,13)(2,14) | (1,13)(6,10) | (1,13)(5,9) |
| 5 | (2,15)(4,9) | (2,15)(1,12) | (1,12)(4,9) |
| 6 | (3,13)(4,10) | (3,13)(1,15) | (1,15)(7,9) |
| 7 | (1,14)(4,11) | (1,14)(2,13) | (1,14)(6,9) |

- Falsifier (QX): the exhaustive family (a) classifies every edge; any face
  whose measured edge types differ from `census:kites[].faces` refutes the
  implementation. Falsifier (Tuna-17): in (g).

### (c) Twist equivalence

- Claim: (B + b)(D + d) = 0 iff (B + d)(D - b) = 0 for low b, d and high B, D
  (monograph A13, ASSERT in its source; census `twist`: 28224 signed tests, 0
  mismatches, 1344 zero products). The census adds: the twist maps the row
  (L, U, x; L', U', y) to (L', U, x; L, U', -y), preserves P on all 1008
  within-kite and non-kite rows, sends every edge of kite S to an edge of kite
  S ^ b ^ d of the other sign type (84 of 84) and every strut to a pair of
  (l, l^8) planes (`census:kites[].twists`). This links C-473's twist
  navigation in open_gororoba to an observable.
- Observable: zero-product success on both factorizations.
- Circuits: no new circuits on QX; family (a) contains both sides of every
  twist pair. On Tuna-17, the pairs in (g).
- Falsifier: on QX, any twist pair whose two rows read different
  deterministic outcomes; on Tuna-17, a twist pair whose raw P differ by more
  than 3 combined standard errors plus the pair-location allowance of (g).

### (d) Associator-sign interference witnesses on box-kite triples

- Claims (census `associator`): over the 1320 ordered distinct triples of a
  kite's 12 indices the omega classes are identical in all 7 kites; the
  classes with constant sign are face-sail-xor0 (0 of 96 non-associating,
  monograph A8: every xor-zero triple associates), ik-same-vertex-third-edge
  (0 of 96), and ij-, ik- and jk-same-vertex-third-strut (24 of 24 each); the
  fixed-pair witness with uniform k is 0 on 84 index pairs, including all 42
  assessor planes, and -1/2 on the 21 pairs (l, 8), (l, l^8) and (8, h); the
  fixed-i witness with uniform (j, k) is 1 at i = 0, -5/16 at i = 8 and 1/16
  elsewhere; the uniform baseline over all 16^3 triples is 25/256 with
  P(c = 1) = 231/512 (root AGENTS.md).
- Observable: associator-sign interference witness <Z_c> after the final H.
- Circuits and register counts:
  - d1, fixed triple, controlled-W (QX): 4 data + 1 control; per kite the 5
    constant-sign exemplars plus one omit-last-block control (42 replicas).
    Prediction: omega in `census:associator.deterministic_exemplars`, and 0 for
    the control.
  - d2, fixed pair, uniform k (QX): 4 data + 1 control, all 105 pairs;
    prediction `census:associator.fixed_pair_uniform_k`.
  - d3, fixed i, uniform (j, k) (QX): 8 data + 1 control = 9 qubits, all 16
    values of i; the mean over i is 400/4096 = 25/256, so the uniform
    baseline is reached through 16 circuits that fit QX's 10 qubits. The
    uniform 12 + 1 qubit circuit fits neither QX (10) nor Ry (9) and is not run.
  - d4, fixed-triple walk (Tuna-17, in (g)).
- Falsifier (QX): d1 sign wrong, or the control's |<Z_c>| above 4.5 sigma at
  2048 shots; d2 and d3 outside 4.5 sigma of the census value. A sign
  witness cannot separate the octonion-level facts from the split octonions
  (section 2), so no claim beyond the stated sign table rests on d1-d4.

### (e) Coherence reconstruction of the post-selected product state

- Claim: after the LCU on a within-kite pair the selector-0 branch holds
  (c0 e_{L^L'} + c1 e_{L^U'}) / norm (`census:design_b.within_kite[]` columns
  `c0`, `c1`); on a bright edge row |c0| = |c1| = 2 and the coherence
  c0 c1 / (c0^2 + c1^2) is +1/2 or -1/2 (`coherence_selector_0`), on a strut
  one coefficient vanishes and the coherence is 0. The relative sign is a
  box-kite fact that the success probability does not show.
- Observable: coherence reconstruction (root AGENTS.md: X or Y on the w bits
  where the two labels differ, Z on the rest, register order fixed). The labels
  differ in the bits of X = 8 ^ S, so w = popcount(X) and the full encoding
  needs 2^w settings: 4, 4, 8, 4, 8, 8, 16 for S = 1..7
  (`census:experiment_counts.full_coherence_settings_by_kite`), plus one all-Z
  setting for the label populations. In the reduced encoding the two labels
  differ in d alone: settings X and Y on d, plus Z.
- Circuits: full Design B per kite on one bright edge row and one strut row,
  52 + 52 settings plus 14 all-Z settings (QX); reduced form on Tuna-17 (g).
- Predictions: reduced <X_d | a = 0> = 2 c0 c1 / (c0^2 + c1^2) = +-1 on the
  bright edge, <Y_d> = 0, <Z_d> = 0; on the strut <X_d> = 0 and <Z_d> = +-1.
- Falsifier: QX, a reconstructed coherence off the census value by more than
  4.5 sigma; Tuna-17, sign(<X_d>) opposite to the census coherence at |z| > 3
  on a bright edge, or |<X_d>| > 0.1 + 3 sigma on a strut.

### (f) Ry emulator

**Diagnostic first.** The retained failing circuit
(runs/2026-10-16T211635Z-Rydberg/teleport.cq) declares `qubit[9]` and
`bit[9] b`, carries `//` comment lines, H and CNOT, and no measure statement;
the passing diagnostic (runs/2026-10-16T213823Z-Rydberg-diagnostic/x-only.cq)
is `qubit[2]` with one X. The documented cause, measurement statements, is
therefore unproven. The diagnostic changes one factor at a time from the
passing circuit, each with a deterministic outcome read with q0 leftmost:

| Circuit | Content beyond `qubit[2] q; X q[0]` | Prediction |
|---|---|---|
| R0 | none (replicates the pass) | `10` |
| R1 | `qubit[9] q` | `100000000` |
| R2 | a `//` comment line | `10` |
| R3 | `bit[2] b` declared, never written | `10` |
| R4 | `H q[1]; H q[1]` | `10` |
| R5 | `CNOT q[0], q[1]` | `11` |
| R6 | `Rz(-pi/2) q[1]` | `10` |
| R7 | `bit[2] b` and `b = measure q` | `10` |
| R8 | teleport.cq verbatim | job failure (replication) |
| R9 | teleport.cq without its bit register and comments | completes |

Two batches of five jobs. The first factor whose circuit fails is the cause;
if R0-R7 all pass and R8 fails, a third and fourth batch run the pairwise
combinations of {width 9, comments, bit register, H, CNOT}. Falsifier for the
documented cause: R7 completing. Uncertainty: low on which factor; the
emulator's noise model is unpublished.

**Box-kite subset** (only after the diagnostic names an accepted dialect; no
measure statements, every atom read at the end, q0 the leftmost character):
the 21 items of (b) at y_sign = +-1 in the reduced encoding, four replicas per
9-atom circuit (11 circuits), the four twist items of (g) (2 circuits), and,
if H and CNOT pass, the full Design B (1,10) dark, bright and fixture
witnesses, one per circuit (3 circuits). Gates come from the Ry set X, Z, Rx,
Rz, T, S, H, CNOT; Sdag is Rz(-pi/2) and a controlled-Y is S, CNOT, Sdag.
Predictions as in (a); the falsifier for the emulator model is a
deterministic row below 0.9 of its ideal outcome, reported with the
emulator's raw rates rather than as an algebraic result.

### (g) Tuna-17

**Admitted layout (revisitable).** The exclusion set is {0, 5, 6, 7, 9}. q0,
q6 and q9 fail on readout and pi-pulse grounds (readout batch 04:18:39Z,
2026-10-17: q9 idle P1 0.27 in a gate-free circuit, q0 and q6 prepared in |1>
read 0.39 and 0.14; [inventory-quantum-inspire-backends.md](inventory-quantum-inspire-backends.md)).
q5, q6 and q7 fall under a Ramsey visibility floor of 0.5 (minimum over
neighbor sectors at 2 us, results/quantum_inspire/coupler_zz_tuna_17_analysis.json,
runs 2026-10-16T224924Z-coupler_zz_tuna_17-batch-00..03): q5 0.043, q6 0.270,
q7 0.084, every other qubit 0.755-0.978, an empty gap between 0.30 and 0.755.
A later readout-0/readout-1 batch showing recovery, or the fresh 1.5 us
Ramsey visibilities expected after about 05:15Z on 2026-10-17, re-admits a
qubit and re-ranks the layouts. q3 keeps no usable neighbor, so the usable
coupling graph is the 12 couplers 1-4, 2-4, 4-8, 8-11, 8-12, 10-13, 11-13,
11-14, 12-14, 12-15, 14-16, 15-16. Its largest induced matching (no coupler
between the members of different pairs) has 3 pairs, and 14 such matchings
exist. Ranked by the predicted contrast below, the best one that avoids q15
(readout P(0|1) 0.270) is M = {(1,4), (10,13), (12,14)} with selectors q1,
q10 and q12 (minimum pair contrast 0.789 central); the best one through q15,
{(1,4), (10,13), (12,15)}, reaches 0.800, equal within the model, so q15
stays out. The walks use the star centred on 11 {8, 13, 14} and the path
8-11-13; the star on 12 {8, 14, 15} carries q15, and the star on 4 {1, 2, 8}
is avoided because simultaneous drive of q1 and q2 raised q2's P1 from 0.046
to 0.893. Every circuit declares `qubit[17] q`, uses only
H, S, Sdag, Z, X and CZ (on the pi/36 grid), applies no binary-controlled
gate, leaves post-selection to the analysis, and reads q0 at the rightmost
character.

**Separation model.** A circuit with n CZ keeps the raw contrast
C = r^n x prod_q V_q^(t/2us) x (1 - e01 - e10)_readout qubit, with r the
per-CZ retention, V_q the 2 us visibility of each qubit active for t, and the
readout factor of the measured qubit. The single depth point is the Design B
witness: 0.0435 corrected contrast at about 68 CZ gives r = 0.955 (region
values give 0.913 to 0.962); the teleport paths, 5 CZ at corrected fidelity
0.746-0.862, bound r below by 0.87. The planning range is r in [0.87, 0.96],
central 0.955; r already contains idle dephasing, so the visibility factor
makes the estimate conservative. Readout factors 1 - P(1|0) - P(0|1) come
from the peer readout batches of 2026-10-17 (P(1|0) at 04:36:37Z for every
qubit; P(0|1) at 04:36:44Z for q1, q2, q3, q7, q8, q9, q13, q14, q15 and at
04:25:39Z for the rest, each with 2 us of idle before readout, so the
no-wait factor is somewhat higher): q1 0.874, q2 0.856, q4 0.840, q8 0.821,
q10 0.865, q11 0.865, q12 0.869, q13 0.808, q14 0.800, q15 0.678, q16 0.843.
The visibilities are the 2 us minima of the coupler-map run of 2026-10-16
(22:49-23:07Z). The selector sits on the better-read end of its pair; the
zero-product statistic reads the selector alone, while the coherence settings
also read the data qubit and carry its factor. The floor is 0.10: five standard errors of a
16384-shot contrast (0.028) plus the measured readout and common-shift
offsets (sum residual -0.042 after correction). A candidate enters Tuna-17
when its pessimistic C is at least 0.20. Uncertainty: low to moderate; one
depth point, and coherent over-rotation (0.050-0.061 rad per X on q6, q8, q9),
drive crosstalk and the common affine shift do not scale as r^n. The T0
ladder measures r directly and replaces this model.

| Candidate | CZ | layout (selector first) | C central | C pessimistic | verdict |
|---|---|---|---|---|---|
| reduced edge or strut LCU | 1 | q1-q4 | 0.82 | 0.74 | Tuna-17 |
| same | 1 | q10-q13 | 0.81 | 0.74 | Tuna-17 |
| same | 1 | q12-q14 | 0.79 | 0.72 | Tuna-17 |
| reduced LCU, depth ladder n = 9 | 9 | q1-q4 | 0.54 | 0.23 | Tuna-17 (T0 only) |
| associator walk, 6 CNOT, 3 data bits | 6 | star 11 {8, 13, 14} | 0.51 | 0.29 | Tuna-17 |
| associator walk, 4 CNOT, 2 data bits | 4 | path 8-11-13 | 0.65 | 0.45 | Tuna-17 |
| reduced coherence (X, Y on d) | 1 | as the LCU, data read too | 0.63-0.69 | 0.58-0.63 | Tuna-17 |
| full Design B | 66-70 | 5-qubit region | 0.042 measured | below 0.001 | QX only |
| full-encoding coherence (2^w settings) | 66-70 | -- | below floor | -- | QX only |
| controlled W, uniform data (d2, d3) | degree-4 phases off the pi/36 grid | -- | -- | -- | QX only |
| reduced cross-kite control | 2 | path w-a-d | P = 1/2 by construction | -- | QX only (carries no contrast) |

**Stages.** Each batch is one witness circuit, then readout-0 and readout-1
(three circuits, the repository's hardware cap), 16384 shots per circuit.

- T0, depth ladder (6 batches). The ladder uses the acquired edge
  (1,10)(4,15) of kite 3 (opposite-sign, P(+,+) = 1, P(+,-) = 0), so it
  joins the earlier full Design B run: depths n = 1, 5,
  9 (CZ-pair identity padding on the same pair) on the three pairs of M in a
  Latin rotation, y_sign + in batches 0-2 and - in batches 3-5. Predictions:
  C(1) in [0.72, 0.82]; C(9)/C(1) = r^8. Falsifier, fixed now: the pooled
  depth-1 contrast with its 99% upper bound below 0.5 refutes the shallow
  admission and ends the Tuna-17 program; a fitted r outside [0.87, 0.97] at
  99% refutes the planning range and resizes every later stage before it runs.
- T1, Theorem 7 subset (21 batches). One item of (b) per circuit: y_sign + on
  one pair of M, y_sign - on another, and the reference replica (1,10)(4,15)
  at y_sign + (ideal 1) on the third, rotating the pair roles by item index.
  Classification rule fixed now: D above +0.4 is same-sign, below -0.4
  opposite-sign, |D| below 0.2 strut, otherwise unresolved. Predicted |D| on
  edges at least 0.72 (pessimistic, readout of 2026-10-17 04:25-04:36Z). Falsifier: any item misclassified or unresolved
  refutes the separation estimate for its layout; a strut with
  |D| > 0.1 + 3 sigma exposes a pair-dependent bias the analysis must carry.
- T2, twist, coherence and associator (17 batches).
  - Twist (8 batches): the edges (1,10)(4,15) of kite 3 and (1,14)(4,11) of
    kite 7, whose twists are the same-sign edges (4,10)(1,15) of kite 6 and
    (4,14)(1,11) of kite 2, and the struts (1,10)(2,9) and (1,14)(6,9), whose
    twists are the non-kite pairs (2,10)(1,9) and (6,14)(1,9). Each circuit
    holds one row and its twisted row (y_sign negated) plus the reference.
    Prediction: equal P.
  - Coherence (3 batches): a bright same-sign edge, a bright opposite-sign
    edge and a strut, X and Y settings on d in one circuit plus the reference.
  - Associator walk (6 batches): the five kite 1 exemplars of
    `census:associator.deterministic_exemplars["1"]`, (2,11,3)
    ij-same-vertex-third-strut omega -1 (6 CNOT, star 11), (2,4,6)
    face-sail-xor0 +1, (2,3,11) ik-same-vertex-third-strut -1, (2,4,11)
    ik-same-vertex-third-edge +1 and (2,3,10) jk-same-vertex-third-strut -1
    (4 CNOT each, path 8-11-13), and the omit-last-block control of
    (2,11,3), one per batch, each plus the reference on a disjoint pair. Falsifier: sign(<Z_c>) opposite to omega at
    |z| > 3, or the control's |<Z_c>| above 0.1 + 3 sigma.

**Per-batch procedure.** Before each Tuna-17 batch the identical cQASM runs on
the local qxelarator emulator, and its relabeled twin (the same gate list on
QX qubits 0-9, map recorded) on the remote QX emulator, because remote QX
serves 10 qubits and the Tuna circuits address qubits up to 16. Then submit
through `qi_platform.py submit`, collect, and check before a 120 s pause:
every job completed with 16384 shots; readout-0 P1 at most 0.10 and readout-1
P1 at least 0.80 on every used qubit (a failure stops the series and
re-plans the layout); the reference replica at P(selector = 0) at least 0.7;
circuit digests equal cases.json; the account's queue empty.

## 5. Run order and budget

QX first, then Ry, then Tuna-17; a later backend runs a family only after
QX has passed it.

| Backend | Family | Replicas | Per circuit | Circuits | Batches (5 jobs) | Shots |
|---|---|---|---|---|---|---|
| QX | (a) full Design B, within kite | 840 | 2 | 420 | 84 | 860160 |
| QX | (a) reduced, within kite | 840 | 5 | 168 | 34 | 344064 |
| QX | (a) full, cross-kite + fixture | 169 | 2 | 85 | 17 | 174080 |
| QX | (a) reduced, cross-kite + fixture | 169 | 3 | 57 | 12 | 116736 |
| QX | (a) full, non-kite pairs | 168 | 2 | 84 | 17 | 172032 |
| QX | (a) reduced, non-kite pairs | 168 | 5 | 34 | 7 | 69632 |
| QX | (d1) fixed triples + controls | 42 | 2 | 21 | 5 | 43008 |
| QX | (d2) fixed pairs, uniform k | 105 | 2 | 53 | 11 | 108544 |
| QX | (d3) fixed i, uniform (j, k) | 16 | 1 | 16 | 4 | 32768 |
| QX | (e) full coherence settings | 118 | 2 | 59 | 12 | 120832 |
| QX | total | | | 997 | 203 | 2041856 |
| QX | Tuna-17 twins (one per Tuna batch) | | | 132 | 44 | 270336 |
| Ry | (f) diagnostic | 10 | 1 | 10 | 2 (+2 adaptive) | 10240 |
| Ry | (f) box-kite subset | 53 | 4 or 1 | 16 | 4 | 16384 |
| Tuna-17 | T0 + T1 + T2 | | 3 LCU replicas, or one walk plus the reference | 132 (44 witness, 88 readout) | 44 (3 jobs) | 2162688 |

Families (b) and (c) need no circuits beyond (a) on QX. Shots: QX 2048 per
circuit (its maximum), Ry 1024 (its maximum), Tuna-17 16384 (about 11 s per
job at the measured 0.60-0.94 ms per shot, inside the 300 s limit). Tuna-17
execution totals about 23 minutes; with queue, collection and pauses the
series takes about three hours. Quantum Inspire records no charge for this
account; the limits are structural (catalogue in
docs/evidence/quantum_inspire/catalogue.json).

## 6. Generators to build next

One generator, `scripts/box_kite_cases.py`, reads census.json and never
recomputes a sign:

- `reduced_lcu(row)` and `reduced_cross_control(row)` (x_sign-free SELECT
  phases, selector Z for x_sign = -1, SELECT verified by unitary), and
  `full_design_b(row)` (wrapping `designs.lcu_witness`, adding the selector Z
  for x_sign = -1);
- `associator_walk(i, j, k, omit_last)`, `controlled_w_fixed_pair(i, j)` and
  `controlled_w_fixed_i(i)` (from `designs.left_mult_gate` and
  `left_mult_adjoint_gate`, with the sign set before control as in
  `scripts/algebra_circuit_fixtures.py`);
- `coherence_settings(row, encoding)` for the 2^w rule;
- `ry_diagnostic_ladder()`;
- `pack(replicas, backend, layout)`, `emit(circuit, place, dialect)` for the
  qx, tuna and ry dialects, and `twin(case)` for the relabeled QX twin;
- `series(family, backend)` writing batch-NN/ cases with the layout of
  `qi_zero_divisor_cases.finish`, `analyze(run_dirs)`, `replay` and
  `self_test()`.

Reused unchanged: `qi_platform.py` (submit, collect, the three-circuit and
one-queued-batch caps), `qi_zero_divisor_cases.py` (`finish`, `header`,
`wilson`, the catalogue admission pattern of `catalogue_backends`),
`select_lcu.sparse_pair_prep`, `scripts/check_qi_platform_retention.py`
(every generated batch through submit's checks), and the research-state
registration of retained runs. Each generated circuit is required to
reproduce its census row by state vector before emission, and the generator
joins ci/gates.json with `--check` and `--self-test` gates in the change that
adds it.

Reuse per family:

| Family | Reuses | New in `box_kite_cases.py` |
|---|---|---|
| (a) full | `designs.lcu_witness`, `select_lcu.select_circuit`, `sparse_pair_prep`, the batching of `qi_zero_divisor_cases` | `full_design_b`, `pack`, `emit` (qx) |
| (a), (b), (c) reduced, (g) T0-T2 LCU | `qi_zero_divisor_cases.finish`, `header`, `wilson`, readout-0/readout-1 circuits, `qi_platform.py` | `reduced_lcu`, `reduced_cross_control`, `twin`, `emit` (tuna, ry) |
| (b), (c) analysis | census.json rows and `kites[].twists` | `analyze` (edge classification statistic D, twist pairing) |
| (d1)-(d3) | `designs.left_mult_gate`, `left_mult_adjoint_gate`, the controlled-block idiom of `algebra_circuit_fixtures.hadamard_test` | `controlled_w_fixed_pair`, `controlled_w_fixed_i` and the fixed-triple form |
| (d4) | the workspace control of `algebra_circuit_fixtures` | `associator_walk` |
| (e) | the 2^w settings rule (root AGENTS.md) | `coherence_settings` |
| (f) | `qi_platform.py` submit and collect, leftmost-q0 parsing of the Ry diagnostic run | `ry_diagnostic_ladder`, `emit` (ry) |

**QX and Ry stop rules.** On QX one shot violating a deterministic row stops
that family's series until the circuit is explained, and a P = 1/2 row
outside the Bonferroni bound of (a) does the same; each batch also checks
completed jobs, 2048 shots per job and circuit digests against cases.json.
On Ry the diagnostic's first failing factor stops the ladder and fixes the
dialect; in the box-kite subset a deterministic row below 0.9 of its ideal
outcome stops the series, and the result is reported as an emulator rate. If
R6 shows Rz rejected, Sdag is written as S S S, which keeps every reduced
circuit on the Ry gate set.

## 7. Open points

- The remote QX dry run of the identical Tuna-17 cQASM is impossible at 10
  qubits; the plan runs the identical bytes on local qxelarator and a
  relabeled twin on remote QX. Whether that satisfies the dry-run rule is
  the owner's decision.
- The Ry emulator's error model is undocumented, so a Ry deviation is
  reported as an emulator rate, not interpreted.
- The Tuna-17 separation estimates rest on one depth point; T0 replaces them.
- Every monograph statement beyond the census fields (32D and 64D counts,
  Rule 1 and Rule 2, random normal-form nullities) stays second-hand here.
