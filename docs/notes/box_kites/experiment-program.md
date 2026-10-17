# Box-kite experiment program: QX, Ry emulator and Tuna-17

`scripts/box_kite_cases.py` generates the QX smoke set of family (a), the
Tuna-17 series and their QX twins under results/quantum_inspire/cases/, and
`scripts/box_kite_qx_sweep.py` runs the exhaustive family (a) on the
qxelarator emulator; nothing has been submitted. Every submission waits for
the owner's approval of its written case (root AGENTS.md, "Quantum
Inspire"). Dates in this note date the measurements they cite.

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

**Where each run goes.** Remote backends run smoke sets and questions about
the device itself; exhaustive ideal emulation runs on a Kaggle CPU kernel
(root AGENTS.md: simulations of 14 qubits or fewer run on Kaggle). Remote
QX runs the QX simulator, an ideal state vector, so a remote QX run
establishes only that the emitted cQASM passes the platform's compile path
(parser, bit order, gate set, angle grid); the generator already checks
every emitted circuit by state vector, and qxelarator 0.10.0, the same
simulator's Python binding, runs the full families on Kaggle. One replica
per gate pattern therefore goes to remote QX, and Tuna-17 time goes to the
questions the census cannot settle: how much contrast survives, at which
depth, and whether coherence and associator signs survive a stated layout.

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
- Backends: Kaggle CPU, qxelarator (exhaustive: 848 circuits, 2354
  replicas, 1010 of them at P = 1/2, `box_kite_qx_sweep.py --run`); remote
  QX (smoke set: 15 replicas in 6 circuits, 2 batches,
  results/quantum_inspire/cases/box_kite_a_qx/); Ry (smoke subset in (f));
  Tuna-17 (the rows of (g)).
- Smoke set: the first census row, in census order, matching each pattern
  of `SMOKE_PATTERNS`, recorded with its selection rule in every replica.
  Full Design B: an edge row at signs (+, +) with P = 0 and one with P = 1, a
  strut at (+, +), an edge row at (-, +) and one at (+, -), a cross-kite
  control, an (l, l^8) pair and the negative fixture (8 replicas, 4
  circuits); reduced: the same edge dark, edge bright, strut and two sign
  variants (5 replicas, 1 circuit: the local-Z SELECT of every edge, the
  Sdag-CNOT-S SELECT of every strut, both selector Z positions); reduced
  cross-kite: a cross-kite control and the fixture (1 circuit). The sign
  variants select edge rows because a strut gives P = 1/2 at both signs, so
  a dropped selector Z or data phase would read correctly on it. Reduced
  non-kite rows share the strut's SELECT and P = 1/2 and add no pattern.
- Falsifier (Kaggle sweep): the QX falsifier above on every replica; the
  record keeps each circuit's sha256 and selector counts, and
  `--replay RECORD --bind --require-pass` re-derives every verdict and binds
  the circuits to the checkout's generator.

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

- Falsifier (Kaggle sweep): the exhaustive family (a) classifies every edge;
  any face whose measured edge types differ from `census:kites[].faces`
  refutes the implementation. Falsifier (Tuna-17): T1 of (g), which carries
  one opposite-sign edge, its same-sign twist and one strut.

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
- Circuits: no new circuits; the exhaustive family (a) on Kaggle contains
  both sides of every twist pair. On Tuna-17, one pair in T1 of (g): the edge
  (1,10)(4,15) of kite 3 and its census twist (4,10)(1,15) of kite 6
  (`census:kites[2].twists[0]`), each twist pair in one batch.
- Falsifier: in the Kaggle sweep, any twist pair whose two rows read
  different deterministic outcomes; on Tuna-17, a twist pair whose
  readout-corrected P differ by more than 3 combined standard errors plus the
  pair-location allowance (the difference of the two pairs' depth-1 bright P
  in T0).

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
- Backends: remote QX runs smoke representatives (one circuit per
  sub-family d1-d3); the full sets run on a Kaggle CPU kernel under
  qxelarator, as family (a) does. Neither is generated yet (section 6).
- Circuits and register counts:
  - d1, fixed triple, controlled-W: 4 data + 1 control; per kite the 5
    constant-sign exemplars plus one omit-last-block control (42 replicas).
    Prediction: omega in `census:associator.deterministic_exemplars`, and 0 for
    the control.
  - d2, fixed pair, uniform k: 4 data + 1 control, all 105 pairs;
    prediction `census:associator.fixed_pair_uniform_k`.
  - d3, fixed i, uniform (j, k): 8 data + 1 control = 9 qubits, all 16
    values of i; the mean over i is 400/4096 = 25/256, so the uniform
    baseline is reached through 16 circuits that fit QX's 10 qubits. The
    uniform 12 + 1 qubit circuit fits neither QX (10) nor Ry (9) and is not run.
  - d4, fixed-triple walk (Tuna-17, the walk stage of (g)).
- Falsifier (Kaggle sweep and QX smoke): d1 sign wrong, or the control's |<Z_c>| above 4.5 sigma at
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
  52 + 52 settings plus 14 all-Z settings, on a Kaggle CPU kernel under
  qxelarator, with one kite's bright edge and strut settings as the remote QX
  smoke representatives (not generated yet, section 6); the reduced form on
  Tuna-17 is the coherence stage of (g).
- Predictions: reduced <X_d | a = 0> = 2 c0 c1 / (c0^2 + c1^2) = +-1 on the
  bright edge, <Y_d> = 0, <Z_d> = 0; on the strut <X_d> = 0 and <Z_d> = +-1.
- Falsifier: Kaggle sweep and QX smoke, a reconstructed coherence off the
  census value by more than 4.5 sigma; Tuna-17, sign(<X_d>) opposite to the census coherence at |z| > 3
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

The API flags the Ry emulator `is_hardware`, so `qi_platform.py submit`
holds its batches to three circuits. The retained construct probe
(`scripts/qi_ry_probe_cases.py`, results/quantum_inspire/cases/ry_probe/,
9 circuits in 3 batches at 1024 shots) already covers R0 (x-baseline), R3
(x-bitreg), R7 (x-measure), H, R5 (x-cnot) and R6 (rz-x), and adds H with
CNOT, with and without a bit register, and an `INIT` block. The ladder
therefore adds R1, R2, R8 and R9, 4 circuits in 2 batches, after the probe
runs. The first factor whose circuit fails is the cause; if every
single-factor circuit passes and R8 fails, a further batch runs the pairwise
combinations of {width 9, comments, bit register, H, CNOT}. Falsifier for
the documented cause: R7 completing. Uncertainty: low on which factor; the
emulator's noise model is unpublished.

**Box-kite smoke subset** (only after the diagnostic names an accepted
dialect; no measure statements, every atom read at the end, q0 the leftmost
character): the five reduced smoke replicas of (a) (edge dark, edge bright,
strut and the two sign variants), four 2-atom replicas per 9-atom circuit
(2 circuits); the T1 edge and its twist at y_sign +-1 (4 replicas, 1
circuit); and, if H and CNOT pass, the full Design B (1,10) dark, bright and
fixture witnesses, one per circuit (3 circuits): 6 circuits in 2 batches at
1024 shots, not generated yet. The ideal predictions come from the Kaggle
sweep, so the Ry run measures only the emulator. Gates come from the Ry set
X, Z, Rx, Rz, T, S, H, CNOT; Sdag is Rz(-pi/2) and a controlled-Y is S,
CNOT, Sdag.
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
stays out. The walks use the star centered on 11 {8, 13, 14} and the path
8-11-13; the star on 12 {8, 14, 15} carries q15, and the star on 4 {1, 2, 8}
is avoided because simultaneous drive of q1 and q2 raised q2's P1 from 0.046
to 0.893. Every circuit declares `qubit[17] q`, uses only
H, S, Sdag, Z, X and CZ (CNOT written as H CZ H on its target, so no rotation
and nothing off the pi/36 grid), applies no binary-controlled gate, leaves
post-selection to the analysis, and reads q0 at the rightmost character. The
generator refuses a CZ off the Tuna-17 coupling graph and any witness gate
on {0, 5, 6, 7, 9} or q15, and requires the retained exclusions
(`qi_zero_divisor_cases.EXCLUDED_QUBITS`) to equal {0, 5, 6, 7, 9}.

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
| full Design B | 66-70 | 5-qubit region | 0.042 measured | below 0.001 | Kaggle sweep, QX smoke |
| full-encoding coherence (2^w settings) | 66-70 | -- | below floor | -- | Kaggle sweep, QX smoke |
| controlled W, uniform data (d2, d3) | degree-4 phases off the pi/36 grid | -- | -- | -- | Kaggle sweep, QX smoke |
| reduced cross-kite control | 2 | path w-a-d | P = 1/2 by construction | -- | Kaggle sweep, QX smoke (carries no contrast) |

**Stages.** Ten batches in four case directories, so the owner approves T0
alone first: results/quantum_inspire/cases/box_kite_tuna_t0/,
box_kite_tuna_t1/, box_kite_tuna_coherence/ and box_kite_tuna_walk/, each a
series of batch-NN/ cases. Each batch is one witness circuit, then readout-0
and readout-1 (`qi_zero_divisor_cases.readout_circuits`; three circuits, the
repository's hardware cap), so every readout correction uses its own batch's
calibration. Each manifest carries its stage's preregistered observable,
predictions and falsifier.

- T0, depth ladder (3 batches, 16384 shots). The reduced LCU of the acquired
  edge (1,10)(4,15) of kite 3 (opposite-sign, P(+,+) = 1, P(+,-) = 0), so
  it joins the earlier full Design B run, at CZ depths n = 1, 5 and 9: the
  SELECT CZ followed by (n - 1)/2 identity CZ pairs on the same pair, each
  repeat after a per-qubit barrier run so no compiler pass meets two
  adjacent CZ. A 3 x 3 Latin square: batch b places depth index
  (pair + b) mod 3 on each pair of M and y_sign -1 (P = 0) on pair b, y_sign
  +1 (P = 1) on the other two, so every depth, pair and batch holds one dark
  and two bright replicas.
  - Contrast: C(n) = mean Pc(bright, n) - Pc(dark, n), with Pc the
    P(selector = 0) corrected by the batch's readout pair. The difference
    cancels a common additive shift of P (amplitude damping toward |0>, the
    measured common-shift offset), which 2 Pc(bright) - 1 alone would carry
    into C as a bias.
  - Accepted confound: the dark replica of a depth sits on one pair in one
    batch and its brights on the other two, so C(n) carries that pair's and
    batch's offset against the others; the square balances pair and batch
    main effects across depths, and a pair x depth interaction stays inside
    the fitted r.
  - Fit: r = exp(slope) of the weighted least-squares line of ln C(n) on n;
    its 99% interval from a parametric bootstrap of the binomial counts and
    each batch's readout pair.
  - Predictions: C(1) in [0.72, 0.82]; C(9)/C(1) = r^8.
  - Falsifier, fixed now: the pooled depth-1 contrast with its 99% upper
    bound below 0.5 refutes the shallow admission and ends the Tuna-17
    program; a 99% interval of r disjoint from [0.87, 0.97] refutes the
    planning range and resizes T1, coherence and walk before they run.
- T1, edge-sign classification and twist (2 batches, 4096 shots). The
  opposite-sign edge (1,10)(4,15) of kite 3 on (1,4), its census twist the
  same-sign edge (4,10)(1,15) of kite 6 on (10,13) (`census:kites[2].twists[0]`,
  checked by the generator), and the strut (1,10)(2,9) of kite 3 on (12,14);
  batch-00 holds the edge at y_sign +1, the twist at -1 and the strut at +1,
  batch-01 the opposite signs. Each row keeps its pair in both batches, so
  the Theorem 7 statistic D = Pc(+,-) - Pc(+,+) compares one pair across the
  two batches, and each twist pair (edge at y, twist at -y, equal P under
  (L, U, x; L', U', y) -> (L', U, x; L, U', -y)) shares a batch. Predictions:
  D = -1 on the edge, +1 on the twist, 0 on the strut. Classification rule:
  D above +0.4 same-sign, below -0.4 opposite-sign, |D| below 0.2 strut,
  otherwise unresolved; predicted |D| on edges at least 0.72 (pessimistic,
  readout of 2026-10-17 04:25-04:36Z). Falsifier: a row misclassified or
  unresolved refutes the separation estimate for its pair; a strut with
  |D| > 0.1 + 3 sigma exposes a pair-dependent bias the analysis carries; a
  twist pair outside 3 combined standard errors plus the pair-location
  allowance of (c) refutes twist equality for that layout.
- Coherence (2 batches, 4096 shots). Setting X (H on d) in batch-00 and Y
  (Sdag, H on d) in batch-01, on the bright same-sign edge (4,10)+ x (1,15)-
  of kite 6 on (1,4) and the strut (1,10)+ x (2,9)+ of kite 3 on (10,13),
  each row on one pair in both batches, plus the reference (1,10)+ x (4,15)+
  (P = 1) on (12,14). Predictions: on the edge <X_d | a = 0> = 2 x the
  census coherence_selector_0 = -1 and <Y_d | a = 0> = 0; on the strut both
  0. Falsifier: sign(<X_d>) opposite to the census coherence at |z| > 3 on
  the edge, or |<X_d>| above 0.1 + 3 sigma on the strut.
- Walk (3 batches, 4096 shots). From `census:associator.deterministic_exemplars["1"]`:
  (2,11,3) ij-same-vertex-third-strut omega -1 (6 CNOT, control q11, data
  bits 0, 1, 3 on q8, q13, q14), (2,3,10) jk-same-vertex-third-strut
  omega -1 (4 CNOT, data bits 0, 1 on q8, q13 of the path 8-11-13) and the
  omit-last-block control of (2,11,3), one per batch, each with the
  reference on (1,4), the pair that meets the walk qubits through one
  coupler (4-8). The generator reads omega from the census, requires each
  exemplar's CNOT and data-bit counts to equal the walk of j, i and i^j, and
  never computes a sign from cd_core. Prediction: <Z_c> = -1 on both walks,
  0 on the control. Falsifier: sign(<Z_c>) opposite to omega at |z| > 3, or
  the control's |<Z_c>| above 0.1 + 3 sigma.

**Per-batch procedure.** Before each Tuna-17 batch its identical cQASM runs
on the local qxelarator emulator (`box_kite_qx_sweep.py --emulate CASE_DIR`,
the readout pair included), and the relabeled twin of its witness circuit
(the same gate list on QX qubits 0-9, the Tuna qubits in ascending order,
map recorded as `qubit_map`) runs on the remote QX emulator, because remote
QX serves 10 qubits and the Tuna circuits address qubits up to 16. The
readout circuits have no twin: they measure the device and carry no
prediction an ideal emulator tests. The twins live in
results/quantum_inspire/cases/box_kite_tuna_twins_qx/, one batch per stage
(3, 2, 2 and 3 circuits at 2048 shots), so the T0 twin runs before T0 is
approved. Then submit through `qi_platform.py submit`, collect, and check
before a 120 s pause: every job completed with the manifest's shots;
readout-0 P1 at most 0.10 and readout-1 P1 at least 0.80 on every used qubit
(a failure stops the series and re-plans the layout); every bright or
reference replica at P(selector = 0) at least 0.7; circuit digests equal
cases.json; the account's queue empty.

## 5. Run order and budget

The Kaggle sweep runs first: it sets the ideal outcome of every family (a)
circuit on the remote backends' own simulator. Then the remote QX smoke set,
the Ry probe, ladder and smoke subset, and Tuna-17 stage by stage, each
stage after its QX twins pass and T0 before any other stage is approved.
Counts below come from `box_kite_cases.py --summary` and, for the exhaustive
family, from `series("a", "qx")`.

| Substrate | Set | Replicas | Circuits | Batches | Shots per circuit | Shots |
|---|---|---|---|---|---|---|
| Kaggle CPU, qxelarator | (a) exhaustive (1010 replicas at P = 1/2) | 2354 | 848 | one kernel | 2048 | 1736704 |
| remote QX | (a) smoke set | 15 | 6 | 2 | 2048 | 12288 |
| remote QX | Tuna-17 witness twins | 27 | 10 | 4 | 2048 | 20480 |
| Ry | construct probe (retained `ry_probe`) | -- | 9 | 3 | 1024 | 9216 |
| Ry | ladder residue R1, R2, R8, R9 (not generated) | -- | 4 | 2 | 1024 | 4096 |
| Ry | box-kite smoke subset (not generated) | 12 | 6 | 2 | 1024 | 6144 |
| Tuna-17 | T0 depth ladder | 9 | 9 (3 witness, 6 readout) | 3 | 16384 | 147456 |
| Tuna-17 | T1 classification and twist | 6 | 6 (2 witness) | 2 | 4096 | 24576 |
| Tuna-17 | coherence | 6 | 6 (2 witness) | 2 | 4096 | 24576 |
| Tuna-17 | walk | 6 | 9 (3 witness) | 3 | 4096 | 36864 |
| Tuna-17 | total | 27 | 30 jobs (10 witness, 20 readout) | 10 | | 233472 |

Families (b) and (c) need no circuits beyond (a); (d1)-(d3) and (e) are not
generated, so their Kaggle sweep and QX smoke rows wait for the generator
(section 6). qxelarator ran 0.14 to 0.23 s per family (a) circuit at 2048
shots on the build host, so the sweep is minutes of CPU on a Kaggle kernel.
Tuna-17 executes 233472 shots, 140 to 219 s at the measured 0.60-0.94 ms per
shot, about 3 minutes, each job inside the 300 s limit; with queue,
collection and the ten 120 s pauses the series takes about 45 minutes. QX
2048 shots per circuit is its maximum and Ry 1024 its maximum. Quantum
Inspire records no charge for this account; the limits are structural
(catalogue in docs/evidence/quantum_inspire/catalogue.json).

## 6. Generators

`scripts/box_kite_cases.py` reads census.json and never recomputes a sign.
Built:

- `reduced_lcu(row)` and `reduced_cross_control(row)` (x_sign-free SELECT
  phases, selector Z for x_sign = -1, SELECT verified by unitary), and
  `full_design_b(row)` (wrapping `designs.lcu_witness`, adding the selector Z
  for x_sign = -1);
- `associator_walk(i, j, k, omega, bits, omit_last)` with omega from
  `census:associator.deterministic_exemplars`, `coherence_setting(row,
  setting)` for the reduced X and Y settings, and `lower_for_tuna` (CNOT as
  H CZ H, identity CZ-pair padding behind barriers);
- `pack`, `emit(circuit, place, dialect)` for the qx and tuna dialects,
  `parse_cqasm` back, `twin(witness, text, source)` for the relabeled QX
  twin, and `verify_text`, which simulates every emitted text on the qubits
  it uses and checks each replica's selector or control marginal, each
  coherence setting's conditional data marginal and each padded replica's
  CZ count;
- `series("a", "qx")` (the exhaustive family, in memory), `smoke_series()`,
  `tuna_series()`, `--summary` and `self_test()`; gates core-375 (`--check`)
  and core-376 (`--self-test`), each in normal and optimized mode.

`scripts/box_kite_qx_sweep.py` runs the exhaustive family on qxelarator
(`--run`), replays a record from its counts and the census (`--replay`,
`--bind`, `--require-pass`), runs retained case directories locally
(`--emulate`), and self-tests on a synthetic record (gate core-377). A
Kaggle CPU kernel installs qxelarator through the `qx-emulator` pin group of
`scripts/kaggle_run.py`; qxelarator 0.10.0 ships cp313 wheels only, so the
sweep runs on the image's Python and never under `--ci-env`, and the CI
replay binds the record to CI's own regeneration instead.

Not built: `controlled_w_fixed_pair(i, j)` and `controlled_w_fixed_i(i)`
(from `designs.left_mult_gate` and `left_mult_adjoint_gate`, with the sign set
before control as in `scripts/algebra_circuit_fixtures.py`) for (d1)-(d3);
`coherence_settings(row, encoding)` for the full-encoding 2^w rule of (e);
the ry dialect, the ladder residue and the Ry smoke subset; and `analyze`
with its replay for the Tuna-17 stages (C(n) and r, D, twist pairs,
coherences, <Z_c>).

Reused unchanged: `qi_platform.py` (submit, collect, the three-circuit and
one-queued-batch caps), `qi_zero_divisor_cases.py` (`header`,
`readout_circuits`, `catalogue_backends`, `EXCLUDED_QUBITS`, `TUNA17`),
`select_lcu.sparse_pair_prep`, `scripts/check_qi_platform_retention.py`
(every generated batch through submit's checks), the toolchain record of
`scripts/qi_toolchain_check.py` (gate core-368; every box-kite Tuna circuit
keeps its gate sequence, CZ count included, through the Tuna decomposition
passes), and the research-state registration of retained runs.

| Family | Reuses | In `box_kite_cases.py` |
|---|---|---|
| (a) full | `designs.lcu_witness`, `select_lcu.select_circuit`, `sparse_pair_prep` | `full_design_b`, `pack`, `emit` (qx) |
| (a), (b), (c) reduced, (g) LCU stages | `qi_zero_divisor_cases.header`, `readout_circuits`, `catalogue_backends`, `qi_platform.py` | `reduced_lcu`, `reduced_cross_control`, `lower_for_tuna`, `twin`, `emit` (tuna) |
| (b), (c) analysis | census.json rows and `kites[].twists` | `analyze` (not built) |
| (d1)-(d3) | `designs.left_mult_gate`, `left_mult_adjoint_gate`, the controlled-block idiom of `algebra_circuit_fixtures.hadamard_test` | `controlled_w_fixed_pair`, `controlled_w_fixed_i` (not built) |
| (d4) | the workspace control of `algebra_circuit_fixtures` | `associator_walk` |
| (e) | the 2^w settings rule (root AGENTS.md) | `coherence_setting` (reduced); `coherence_settings` (full, not built) |
| (f) | `qi_ry_probe_cases.py`, `qi_platform.py` submit and collect | `emit` (ry) and the ladder residue (not built) |

**QX and Ry stop rules.** In the Kaggle sweep and on remote QX one shot
violating a deterministic row stops that family's series until the circuit
is explained, and a P = 1/2 row outside the Bonferroni bound of (a) does the
same; each remote batch also checks completed jobs, 2048 shots per job and
circuit digests against cases.json. On Ry the diagnostic's first failing
factor stops the ladder and fixes the dialect; in the box-kite smoke subset
a deterministic row below 0.9 of its ideal outcome stops the series, and the
result is reported as an emulator rate. If the probe shows Rz rejected, Sdag
is written as S S S, which keeps every reduced circuit on the Ry gate set.

## 7. Open points

- The remote QX dry run of the identical Tuna-17 cQASM is impossible at 10
  qubits; the plan runs the identical bytes on local qxelarator
  (`box_kite_qx_sweep.py --emulate`) and the relabeled twin of each witness
  circuit on remote QX. Whether that satisfies the dry-run rule is the
  owner's decision.
- T0 is approved alone; its falsifier can end the Tuna-17 program or resize
  T1, coherence and walk before they run.
- OpenSquirrel prints compiled Rz angles at 8 significant digits, so the
  toolchain record marks the QX full Design B smoke circuits as a changed
  gate sequence (angle text only, a rounding near 1e-9 rad); whether the
  platform executes the source or the compiled text is not established.
- The Ry emulator's error model is undocumented, so a Ry deviation is
  reported as an emulator rate, not interpreted.
- The Tuna-17 separation estimates rest on one depth point; T0 replaces them.
- Every monograph statement beyond the census fields (32D and 64D counts,
  Rule 1 and Rule 2, random normal-form nullities) stays second-hand here.
