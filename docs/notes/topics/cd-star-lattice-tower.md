# Cayley-Dickson star lattices: Tuna-17 and its lifts to dimensions 3, 4, 8 and 16

Tuna-17's coupling graph is a lattice cluster in Z^2 whose four boundary
ancillas are the unit multiples of the Gaussian integer 1 + 2i. The same
rule in any Cayley-Dickson algebra builds a star lattice of 4n^2 + 1 points
in dimension n, and its boundary symmetry stays reflection-free in
dimensions 2, 4, 8 and 16. Dimension 3, which carries no Cayley-Dickson
algebra, loses the twist. In dimension 16 every sedenion two-blade zero
divisor lies in the lattice's data shell, and the lattice's symmetry group
mixes the 42 assessor planes with 14 invertible planes. The boundary is the
sign pattern of right multiplication by the sum of the imaginary units, a
skew conference matrix; in dimensions 4 and 8 it is the Paley quadratic-residue
matrix of q = 3 and 7, so the symmetry groups are SL(2, 3) and SL(2, 7) acting
on the projective line over F_q. In dimension 16, where no Paley matrix of
order 16 exists, the group is a double cover of PGL(2, 7), and it stays that
group through dimension 128.

[scripts/cd_star_lattice.py](../../../scripts/cd_star_lattice.py) computes
every number below from `cd_core.cd_sign`; the retained record is
[census.json](../../evidence/cd-star-lattice/census.json), replayed by gate
`core-record-check-05` (`tests/test_cli_record_checks.py`) and described in its [README](../../evidence/cd-star-lattice/README.md).
Tags: [P] source statement; [E] exact finite computation, where a group
order comes from an exhaustive search (the census backtracker through
n = 16, cross-checked by nauty) and an isomorphism from an explicit
certificate checked against that complete enumeration; [T] written proof
argument, not machine-checked; [R] Rocq-checked theorem, kernel-checked
with no axioms; [I] interpretation.

## Construction

S_n is the set of points of Z^n with taxicab norm at most 2, plus a boundary
set B_n at norm 3; unit-distance pairs are the edges. In the Cayley-Dickson
algebra of dimension n,

    B_n = { u (1 + 2 w) : u = +-e_a, w = +e_b, b >= 1 },

so each boundary point is s e_a + 2 s cd_sign(n, a, b) e_{a XOR b}, of
coordinate type (1, 2, 0, ..., 0). The layers by norm are:

| Norm | Points | Count | Neighbors of each |
|---|---|---|---|
| 0 | origin | 1 | 2n |
| 1 | +-e_a | 2n | 2n |
| 2 | +-2 e_a | 2n | n |
| 2 | +-e_a +- e_b | 2n(n-1) | 3 |
| 3 | B_n | 2n(n-1) | 2 |

| Statement | Status |
|---|---|
| S_n has 4n^2 + 1 points and 8n^2 - 4n edges | [T] sum of the layer counts; edges are 2n at the origin, 2n - 1 more at each unit, 2 at each boundary point; [E] n = 2, 3, 4, 8, 16 |
| Every edge joins an even site (coordinate sum even) to an odd one: 2n^2 + 1 even, 2n^2 odd | [T] a unit step changes the coordinate sum by 1; [E] |
| B_n puts exactly one point on each of the 2n(n-1) edges {s e_a, t e_c} of the cross-polytope of norm 2 | [T] in an associative algebra the partner t e_c + 2 s e_a needs w' = conj(u w) u = -w, which B_n excludes; [E] n = 2, 4, 8, 16 |

## Dimension 2 is Tuna-17

The map Q8 -> (0, 0), Q4, Q5, Q11, Q12 -> the units, Q0, Q6, Q10, Q16 ->
(1, 2), (2, -1), (-2, 1), (-1, -2) (`QUBIT_COORDINATES`) sends the 24 edges of
S_2 onto the 24 undirected couplers that the Quantum Inspire catalogue
reports for Tuna-17 ([backend table](../quantum_inspire/backends.md)) [E]:

```
              1 -- 0
              |    |
    10 -- 7 -- 4 -- 2
    |     |    |    |
    13 -- 11 - 8 -- 5 -- 3
          |    |    |    |
          14 - 12 - 9 -- 6
          |    |
          16 - 15
```

| Statement | Status |
|---|---|
| B_2 = {1 + 2i, i(1 + 2i), -(1 + 2i), -i(1 + 2i)}; its symmetry group is C4, all rotations | [T]; [E] order 4, determinants all +1 |
| 5 = (1 + 2i)(1 - 2i) with non-associate factors; the factor 1 - 2i gives the mirror point set, a distinct set with an isomorphic graph | [T] |
| The catalogue topology lists couplers without coordinates, so it leaves the chip's handedness unfixed; only the physical layout fixes it | [T] the two mirror sets have isomorphic graphs |
| The forced-type classes are the two sets of four ancillas, and the X/Z assignment is a [[9, 1, 3]] CSS code: the distance-3 rotated surface code | [E] `check_types` |
| The layout matches the QuTech Surface-17 architecture | [I] the [2102.13071 source note](../papers/2102.13071.md) carries this inference and its limit |

## The tower

| n | Algebra | Points | Edges | Symmetry order | Element-order profile | Reflection-free | Left-unit closure |
|---|---|---|---|---|---|---|---|
| 2 | complex | 17 | 24 | 4 | C4 | yes | 16/16 |
| 3 | none (tetrahedral rule) | 37 | 60 | 24 | 7 involutions, 8 of order 3, 8 of order 6 | no, 12 of 24 elements have determinant -1 | not defined |
| 4 | quaternion | 65 | 112 | 24 | SL(2, 3) | yes | 192/192 |
| 8 | octonion | 257 | 480 | 336 | SL(2, 7) | yes | 1120/1792 |
| 16 | sedenion | 1025 | 1984 | 672 | 2.PGL(2, 7): one involution (-1), elements up to order 16 | yes | 7968/15360 |

"Symmetry order" is the order of the group of signed permutation matrices
that maps B_n onto itself. It equals the full automorphism group of the
graph S_n at n = 2, 4, 8, 16: nauty returns orders 4, 24, 336 and 672
([external replay](../../evidence/cd-star-lattice/README.md#external-replay)).
"Reflection-free" means no element has determinant -1. The section below
derives the group column; at n = 4 the column names the abstract group, and
its action on R^4 differs from left multiplication by the 24 Hurwitz units
(the commutant is Q(sqrt -3), where the Hurwitz action has a quaternion
commutant). Left-unit closure
counts the products u' p, u' = +-e_a, p in B_n, that stay in B_n; at n = 4
those units generate the quaternion group of order 8, so left
multiplication accounts for a subgroup of order 8 of the 24. [E] for every
cell.

| Statement | Status |
|---|---|
| The group acts transitively on the 2n signed units at every n of the tower; the stabilizer of e_0 has orders 1, 3, 21, 21 | [E] |
| The octonion-to-sedenion step doubles the group without enlarging the stabilizer of e_0 | [E] 336 = 16 x 21, 672 = 32 x 21 |
| The doubling stops at the sedenions: the signed-permutation centralizer of the boundary has order 672 at n = 32, 64 and 128, isomorphic to the n = 16 group, with n/16 orbits of 32 signed units | [E] external nauty replay, the only search above n = 16 (the census backtracker agrees at n = 32); the e_0 orbit at n = 32 holds 32 of 64 signed units, so the action is no longer transitive. A prediction of order 1344 at n = 32, recorded before the run, failed |
| Left multiplication by units leaves B_n invariant in the associative algebras and fails from the octonions on, where the units form a Moufang loop | [E] closure counts; [T] associativity gives (u' u)(1 + 2w) = u'(u(1 + 2w)) |

## The boundary as a Paley matrix

The arc matrix W_n has W_n[a XOR b][a] = cd_sign(n, a, b) for b >= 1, so its
column a is e_a s with s = e_1 + ... + e_{n-1}: W_n is right multiplication
by s, and B_n is the set of points s' e_a + 2 s' W_n[a XOR b][a] e_{a XOR b}.
A signed permutation maps B_n onto itself exactly when it commutes with W_n,
so the symmetry group G_n is the signed-permutation centralizer of W_n [T].
The `identification` block of the census carries the [E] cells.

**Induction for the conference property.** Write A_n for the algebra of
dimension n, x = (x1, x2) in A_n + A_n, and the product as cd_sign's four
cases read it: (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)). The imaginary
sum doubles as s' = (s, 1 + s), with s = 0 at n = 1. Let L and R be left and
right multiplication by s on A_n and C conjugation, the diagonal matrix
diag(1, -1, ..., -1). Expanding (x1, x2) s' and s' (x1, x2) gives

    R' = [[R, L - I], [I + L, -R]],   L' = [[L, -(I + R) C], [(I + L) C, R]].

The census checks both block forms against cd_sign at n = 4 to 128 [E]
(`doubling_blocks_match_cd_sign`). Three facts hold at every n: C^2 = I and
C^T = C; C L C = -R, because conjugation reverses products and conj(s) = -s;
and L e_0 = R e_0 = s. The induction hypothesis at n is (H1) L^T = -L and
R^T = -R, (H2) L^2 = R^2 = -(n - 1) I, (H3) LR = RL; at n = 1 all three hold
with L = R = 0. From C L = -R C and C R = -L C:

- Transposes. R'^T has blocks R^T, (I + L)^T, (L - I)^T, -R^T, which H1
  turns into -R, I - L, -(I + L), R: R'^T = -R'. L'^T has diagonal -L, -R
  and off-diagonal blocks C(I - L) = (I + R) C and -C(I - R) = -(I + L) C:
  L'^T = -L'.
- Squares. The diagonal blocks of R'^2 are R^2 + (L - I)(L + I) and
  (L + I)(L - I) + R^2, both L^2 + R^2 - I = -(2n - 1) I by H2; the
  off-diagonal blocks are +-(RL - LR) = 0 by H3. In L'^2, C(I + L)C = I - R
  and C(I + R)C = I - L make the diagonal blocks L^2 - (I + R)(I - R) and
  R^2 - (I + L)(I - L), again L^2 + R^2 - I; the off-diagonal blocks reduce
  to (RL - LR) C = 0.
- Commutation. The upper-left block of L'R' - R'L' is
  (LR - RL) - ((I + R)(I - R) + L^2 - I) C = (R^2 - L^2) C = 0. The
  lower-right block is (I + L)(C(L - I) + (I + R) C) = (I + L)(-RC - C + C
  + RC) = 0. The off-diagonal blocks reduce by H2 and H3 to
  Q (I + C) and Q' (I + C) with Q = R^2 + R - L - LR and
  Q' = R + RL - L - L^2. I + C = 2 e_0 e_0^T, and
  Q e_0 = Rs + s - s - Ls = (R^2 - L^2) e_0 = 0, likewise Q' e_0 = 0.

So H1 to H3 hold at 2n with n - 1 replaced by 2n - 1. W_n = R, so
W_n^T W_n = -W_n^2 = (n - 1) I and (I + W_n)(I + W_n)^T = n I for every n.
The step proves LR = RL itself, so the argument does not depend on the
flexibility of Cayley-Dickson algebras. `proofs/CdImaginarySumConference.v`
checks the same induction in Rocq over integer coefficients, in element form:
s (s x) = (x s) s = -(n - 1) x, s (x s) = (s x) s, and the skew and
conference identities for the coordinate inner product.

| Statement | Status |
|---|---|
| W_n is a skew conference matrix: W_n^T = -W_n and W_n^T W_n = (n - 1) I, so I + W_n is a skew Hadamard matrix | [R] for every n on the recursive pair tower ([proof bundle](../../evidence/cd-imaginary-sum-conference/README.md)); [E] that tower's products equal cd_sign through n = 64; [T] the induction below; [E] n = 2 to 128 |
| I + W_n is a Hadamard matrix of class 4 in McKay's list of order 16 (its transpose and the sedenion sign table lie in class 5, the transpose class), with 86016 automorphism pairs (P, Q), P (I + W) Q^T = I + W, counted with (-I, -I). G_n embeds as the pairs (P, P), of index 8, 64 and 128 at n = 4, 8, 16; at n = 32 and 64 the whole Hadamard automorphism group has order 2688, index 4 | [E] external Hadamard replay. A prediction that I + W_16 is the Sylvester class (line 1), recorded before the run, failed |
| At n = 4 and 8, W_n is signed-permutation equivalent to the Paley matrix of q = 3 and 7, whose entry (x, y) on the projective line over F_q is the quadratic character of y - x; the equivalences number 24 and 336, the group orders | [E] |
| Read through that equivalence, each symmetry permutes the projective line by a map of PSL(2, q) with kernel {+-1}, and a lift of those maps to SL(2, q) is a bijective homomorphism: G_4 = SL(2, 3) and G_8 = SL(2, 7) | [E] explicit lift |
| The octonion boundary is the quadratic-residue tournament mod 7, whose residues {1, 2, 4} form a line of the Fano plane | [I] |
| G_16 preserves the eight doubling pairs {a, a + 8} and acts on them as PGL(2, 7) with kernel {+-1}; the preimage of PSL(2, 7) is the derived subgroup, which lifts to SL(2, 7) | [E] |
| G_16 has one involution, Sylow 2-subgroup Q32 and SmallGroup id (672, 1045): the double cover of PGL(2, 7) whose elements over PGL(2, 7) minus PSL(2, 7) include no involution | [E] the census certifies the involution count and the PGL(2, 7) quotient; GAP gives the id and Q32 in the external replay |
| No Paley matrix has order 16, since 15 is no prime power. One has order 32 (q = 31), and W_32 is not equivalent to it: x -> x + 1 is a Paley automorphism of order 31, and 31 does not divide 672 | [T] given the [E] order 672 at n = 32 |
| The commutant of G_n is Q(sqrt -3) at n = 4 and Q(sqrt -7) at n = 8; at n = 16 it has basis 1, J, R, JR with J^2 = -7, R^2 = -1, JR = -RJ and R right multiplication by e_8, the quaternion algebra (-7, -1) over Q | [E]; (-7, -1) ramifies at 7 and infinity [T]: -7 is a square in Q_2 and -1 a non-residue mod 7 |
| The stabilizer of e_0 equals the set of unsigned, XOR-linear index permutations that preserve cd_sign: 3, 21 and 21 elements at n = 4, 8, 16, the order-21 group being 7:3 | [E] |
| 6, 42 and 42 elements have XOR-linear index maps, the stabilizer and its product with -1, so the lattice group meets the algebra's permutation automorphisms only there | [E] |
| At n = 16 the 120 index pairs fall into orbits of 8 (the doubling pairs), 56 (the 42 assessors and 14 more) and 56; the derived subgroup's index orbits are {0, 9, ..., 15} and {1, ..., 8} | [E] |

## Dimension 3

The tetrahedral rule takes B_3 as the orbit of (1, 2, 0) under cyclic
coordinate shifts and sign flips of even count: the 12 points
(0, +-1, +-2) and their cyclic shifts, the vertex set of a pyritohedral
pseudo-icosahedron (the icosahedron (0, +-1, +-phi) with phi replaced by 2).

| Statement | Status |
|---|---|
| No boundary of type (1, 2, 0) keeps the full rotation group O of the cube | [T] O acts freely on the 24 type-(1, 2, 0) points, so an O-invariant subset holds 0 or 24 of them, never the 12 a one-per-edge boundary needs |
| Of the 4096 one-per-edge boundaries of the octahedron, 2 reach symmetry order 24 (the two tetrahedral orbits, both with reflections); the largest reflection-free symmetry has order 4 and is cyclic, a C4 pinwheel about one coordinate axis, on 12 boundaries | [E] `octahedron_selections`; [T] every order-4 rotation of the cube turns about a coordinate axis |
| The ancillas split into 3 forced-type classes of 6, one per coordinate axis; each of the 6 two-type assignments commutes and encodes 1 logical qubit with least logical weight 1 | [E] `check_types`: a [[19, 1, 1]] code, which corrects nothing |

## The sedenions

| Statement | Status |
|---|---|
| The 168 signed two-blade zero divisors of `cd_core.sedenion_zero_divisor_corpus` all lie in the data layer +-e_a +- e_b of S_16 (480 points); none involves e_0 | [E] |
| They occupy 42 index pairs, the assessors of the [box-kite program](box-kites/README.md), with all 4 sign patterns each | [E] |
| Every unit +-e_a and every boundary point u(1 + 2w) is invertible; the determinant zeros among the 992 probed points equal the corpus exactly | [E] `cd_core.left_mult_determinant_exact` |
| The symmetry group of order 672 moves the 42 assessor pairs inside one orbit of 56 index pairs: the assessors plus (0, b) for b = 1..7 and (8, b) for b = 9..15 | [E] |
| The lattice symmetry does not preserve the zero-divisor set | [E] |
| The boundary rule reads cd_sign on one pair (a, b) at a time, while a two-blade zero divisor needs the sign relations of four indices, so the shape's symmetry cannot see the box-kite structure | [I] |

## Quantum-code reading

A CSS code that measures each odd site's full neighborhood must give one
Pauli type to two odd sites whose neighborhoods share an odd number of data
sites. In S_2 that relation leaves two classes and the surface code; in S_3,
three classes and a distance-1 code; at n = 4, 8 and 16 it joins all 2n^2
odd sites into one class, so no assignment with both Pauli types exists and
the lifts are geometries rather than codes [E] `check_types`.

## Open questions

- A Rocq statement that the recursive tower's basis products equal a Rocq
  transcription of `cd_core.cd_sign` for every n; the bridge is an [E] check
  through n = 64.
- Rocq certificates for the finite group identifications, which need a
  verified complete enumeration of each centralizer, not only a checked
  isomorphism.
- Whether G_n has order 672 for every n >= 16, acting as G_16 on each block
  of 32 signed units; the nauty replay reaches n = 128.
- A boundary rule that reads four-index sign relations and whose symmetry
  preserves the box-kites.
