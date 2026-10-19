# Tuna-17 bipartite designs: cubic Walsh classes and box-kite packing

Status: DRAFT, stopped at handoff. Tuna-17 work now belongs to the box-kite
session. Done and checked: the exact phase identities of the two Walsh
exemplars, the affine-relabeling rule that makes any linear prefix or suffix
free, the CNOT count of a CCZ on a path, the exhaustive layout search
(disjoint 4-qubit paths, largest induced matching) on Tuna-17 with
{0, 3, 5, 6, 7, 9} and with q15 also removed. Not done: the shot and variance
calculation, the noise prediction, the falsifier numbers, the Walsh case
generator, its cases and gates, the mid-circuit readout fold's validation,
and the Design B table. No circuit went to any backend, local or remote.

## Usable Tuna-17 graph

The coupling graph is bipartite (P = {0,4,5,6,10,11,12,16}, Q = the other
nine; [backends.md](backends.md)). With {0, 3, 5, 6, 7, 9} removed (q0, q6,
q9 readout faults; q5, q7 Ramsey visibility below 0.5; q3 left without a
usable neighbor) the usable couplers are 1-4, 2-4, 4-8, 8-11, 8-12, 10-13,
11-13, 11-14, 12-14, 12-15, 14-16, 15-16. q15 reads P(0|1) 0.270 and is
avoided for readout.

Exhaustive enumeration over that edge list (every coupler subset and every
ordered 4-tuple):

| Quantity | without q15 | with q15 |
|---|---|---|
| induced matchings of the largest size | 5 of size 3 | 14 of size 3 |
| 4-qubit paths | 18 | 27 |
| vertex-disjoint pairs of 4-qubit paths | 4 | 25 |
| fewest couplers joining such a pair | 2 (8-11 and 12-14) | 2 |

No induced matching of 4 pairs exists, so 3 reduced-LCU replicas per circuit
is the ceiling of buffered packing on this graph, and the box-kite matching
M = {(1,4), (10,13), (12,14)} already reaches it. No pair of disjoint 4-qubit
blocks is buffered: every pair is joined by at least two couplers, so the
Walsh design cannot place a buffer qubit between its blocks and carries the
parked-coupler ZZ of those two couplers instead ((8,11) +6.6 kHz,
(12,14) +10.4 kHz; [experiments.md](experiments.md)).

## Design A: the two cubic Walsh classes

### The exemplars reduce to one CCZ and one CCZ plus one CZ

Design C measures P(y) = |2^-5 sum_x (-1)^(f(x) + x.y)|^2 for the associator
phase f of a pair (predict.associator_phase). Checked by truth table against
predict.associator_phase:

- (1,16), K = 11/32: f = OR(x1, x2, x3) = 1 + (1 + x1)(1 + x2)(1 + x3).
  Bits 0 and 4 do not enter, so y0 = y4 = 0 and the spectrum is that of
  x1 x2 x3 on three bits.
- (9,18), K = 5/32: with u = x0 + x3,
  f = (1 + x1)(1 + x2)(1 + u) + 1 + x2 + x2 x3 + x4. In the coordinates
  (u, x1, x2, x3, x4) that is a b c + b d plus affine terms, with
  (a, b, c, d) = (x1, x2, u, x3); x0 x1 x2 + x0 x3 evaluates to K = 5/32.

### Linear prefix, suffix and affine terms are classical relabelings

The input |+>^n is invariant under every CNOT network and every X, so a
linear or affine change of the phase's variables before the diagonal costs
no gate. A CNOT network A_fin after the diagonal satisfies
H^n P_A H^n = P_(A^-T), so it relabels the measured string; a Z before the
final H layer flips an outcome bit. For f(x) = phi(A x + b) + c.x + d,
P_f(y) = Q_phi(A^-T (y + c)), so the hardware runs phi and the analysis maps
each measured z to y = (A_fin A)^T z + c. The collision probability K is
invariant under the map, and the full distribution maps exactly.

Consequence: the two classes differ by one CZ. On a 4-qubit path d-a-b-c
(CCZ center b), the high-class circuit is H, CCZ(a, b, c), H on all four;
the low-class circuit adds CZ(a, d) (a b c + a d is in the same class as
a b c + b d by the symmetry of the cubic). Bit d of the high circuit is
idle and reads 0 ideally, like bits 0 and 4 of the pair.

A breadth-first search over CNOT networks on the path a-b-c, requiring the
wires to visit all seven nonzero parities of F_2^3 with the end map left
free, gives 5 CNOTs (4 on a triangle, which a bipartite graph lacks). Each
CNOT is one CZ between H gates, and the seven pi/4 phases are T and Tdag,
on the pi/36 grid. Counts: high class 5 CZ, low class 6 CZ, against 99 and
94 routed CZ for the factorized circuits on Kingston
([design_c_cubic_noise](../../evidence/design_c_cubic_noise/README.md)).
These circuits measure how Tuna-17 moves two spectra that differ by one
quadratic term on a fixed CCZ; they do not test composition of the three
multiplication blocks, which the factorized circuit does.

### Planned batch (one batch, three circuits)

- Blocks X = (1, 4, 8, 12) or (2, 4, 8, 12) and Y = (10, 13, 11, 14) or
  (13, 11, 14, 16), the four disjoint q15-free pairs above. X contains
  star 4 {1, 2, 8} only through one of q1, q2, so the Q1/Q2 simultaneous
  drive pair never runs together.
- Circuit 1: high class on X, low class on Y. Circuit 2: the same two
  classes swapped between blocks, so class and block effects separate in a
  2 x 2 design inside one calibration.
- Circuit 3: readout. Proposed fold: one circuit measures every used qubit
  in |0>, applies X, waits, and measures again; Tuna-17 returns every
  mid-circuit bit (batch job 870030), so one circuit gives P(1|0) and
  P(0|1), and postselecting the first readout on 0 removes thermal
  population from the |1> arm. The fold assumes the mid-circuit and final
  measurement share one assignment matrix; no run has tested that, and QX
  returns only each qubit's last outcome, so the QX twin cannot exercise
  it. The two-circuit readout-0/readout-1 form remains the validated
  fallback, at the cost of the class swap.

Not done: shots from the collision-estimator variance, predictions from a
noise model, and the written falsifier.

## Design B: box-kite packing beyond the box-kite session's layout

Narrowed to three items: readout folding or sharing across batches, a wider
buffered matching, and the reference replica on idle qubits.

- Wider matching: none exists (table above; 3 is the maximum induced
  matching with or without q15).
- Readout fold: the single-circuit mid-circuit readout above would let a
  batch hold two witness circuits and one readout circuit, raising the
  witness circuits per batch from one to two. Sharing one readout pair
  across batches conflicts with the measured drift: q9's idle P1 moved to
  0.27 at 04:04Z, and Q6 read P(1|1) 0.670 in series P's calibration batch and
  0.86 after the 04:12Z recalibration
  ([experiments.md](experiments.md), series P), both within one series of
  consecutive batches. Not evaluated further.
- Reference replica on idle qubits: not evaluated.
