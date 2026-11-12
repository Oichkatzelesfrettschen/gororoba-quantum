# Saturation and reducedness of the quadric ideals K2

Each script reads the retained quadrics K2 of one fiber at p = 32009 and asks a question about the projective
scheme V_+(K2), which contains the exceptional fiber E0 = V_+(L) and equals it where L = K2 is proved. A statement
about the affine cone k[y]/K2 passes to V_+(K2) only through the saturation K2 : m^∞, so each fiber gets that
check first. The same-sign X incidences are in [arcs-x-same](../arcs-x-same/README.md) (A5-303).

| Fiber | K2 | dimension, multiplicity | K2 : m = K2 | reducedness of V_+(K2) |
|---|---|---|---|---|
| E8-bar → VB | 21 quadrics in 10 variables | 4, 7 | yes | reduced: K2 equals the intersection of its two minimal primes (degrees 3 and 4); Cohen-Macaulay with a linear resolution (Betti numbers 21, 70, 105, 84, 35, 6) (A5-307) |
| Iso | 68 quadrics in 17 variables | 5, 23 | yes | reduced and irreducible: K2 is radical and geometrically prime (ledger A5-058, A5-060) |
| E8-bar → N− | 148 quadrics in 21 variables | 5, 11 | yes | nonreduced along one embedded quadric threefold, reduced off it (A5-312, below) |
| W8 → N− | 144 quadrics in 24 variables | 6, 50 | yes | reduced: K2 is radical with components of degree 20 and 30 (ledger A5-012) |

"Saturated" means the irrelevant ideal is not an associated prime, so k[y]/K2 has no nilpotent or zero divisor
supported at the vertex alone, and nonreducedness of the cone, where it occurs, is nonreducedness of V_+(K2).

## Every retained K2: saturation, initial ideal, nilpotent coordinates (A5-311)

`k2_scheme_census.py` runs the same three checks on all fourteen retained relation files (five fibers, both primes,
both headers where retained; record `k2-scheme-census.jsonl`, 2.5 s in all).

| Fiber | sources | saturated | in_dp(K2) squarefree | coordinates with y_i² in K2 |
|---|---|---|---|---|
| X− → N−, X+ → N+ | 3 | yes | no (72 generators, degree up to 3) | y1, y5, y6, with N² in K2 |
| E8-bar → VB | 2 | yes | no (25, up to 3) | none |
| Iso | 3 | yes | no (81, up to 3) | none |
| E8-bar → N−, N+ | 4 | yes | no (172, up to 4) | y4, y6, y7, y12, y14, with N² in K2 |
| W8 → N− | 2 | yes | no (202, up to 4) | none |

The initial ideal is a flat degeneration that keeps the Hilbert function, dimension and multiplicity of K2. A
squarefree initial ideal would prove K2 radical; none is squarefree in the header coordinates and the dp ordering,
which decides nothing (the Iso, W8 and VB ideals are radical by other proofs). The nilpotent coordinates of the
E8-bar ideals number 5 = 21 − 16, the 16 being the coordinates that the fiber-to-Grassmannian fit of
[kernel-limits](../kernel-limits/README.md) spans.

## The nonreduced locus of the E8-bar quadric scheme (A5-312)

`e8nm-nonreduced-locus-p32009.sing` and `e8nm-nonreduced-locus-p32029.sing` (5 s each, identical logs), with
N = (y4, y6, y7, y12, y14):

- K2 + N has dimension 5 and multiplicity 11, those of K2, with Hilbert numerator 1, 11, −1, so V_+(K2) is
  generically reduced and its nilpotents are embedded;
- the annihilator K2 : (K2 + N) has 16 linear forms and one further generator, dimension 4 and multiplicity 2: a
  quadric threefold in a P^4, lying in V(K2 + N);
- after saturation at y_j the coordinates N vanish for j = 2 and 19 and survive for the fourteen other nonempty
  charts.

Scope: this describes V_+(K2). For the exceptional fiber V_+(L) of E8-bar → N−, L contains K2 and holds no linear
form (h_1 = 21), so y4, y6, y7, y12, y14 are nonzero nilpotents of the affine fiber cone F(I); whether they survive
on the projective fiber depends on L in every degree, which is open until the elimination of
[monomial-ladder](../monomial-ladder/README.md) finishes. The radical is K2 + N (next section).

## Components and connectedness of the E8-bar quadric scheme (A5-313)

`e8nm-components-p32009.sing` (7 s): K2 + N is radical, with two minimal primes, a fourfold of degree 11 and a
threefold of degree 4 (projective dimensions; ledger A5-252 has the same split). The two components meet in a
plane (affine dimension 3, multiplicity 1), so V_+(K2) is connected and its structure sheaf has only the trivial
idempotents. The embedded quadric threefold of the previous section lies in the fourfold of degree 11 and not in the
threefold of degree 4.

Connectedness of the other fibers needs no run: the reduced same-sign X and Iso fibers are irreducible, and
k[y]/K2 is Cohen-Macaulay of dimension at least 4 for E8-bar → VB, Iso and W8 → N− (ledger A5-010, A5-307), which
makes V_+(K2) connected in codimension 1.

`vb-census-p32029.sing` gives the same two components at p = 32029 (dimension 4 with multiplicities 3 and 4,
4 and 3 linear forms, meeting in dimension 3 with multiplicity 1); its log was produced on the 2-core lab host.

    Singular -q --no-warn < docs/evidence/a5-exceptional-fibers/quadric-census/vb-radical.sing

## Binomial form and linear symmetries (A5-310)

`quadric_structure.py` asks two questions of each of the fourteen retained K2 (both primes, both headers where
retained; 4 s in all; record `quadric-structure.jsonl`). Every number in the table is the same on each file of its
fiber.

Is K2 spanned by monomials and binomials in the header's coordinates y? The reduced row echelon basis of K2 on the
quadratic monomials answers it for these coordinates only. Which linear changes of coordinates could make it so?
A monomial-binomial presentation of a d-dimensional toric variety has a diagonal torus of rank at least d among
its linear symmetries, so the script computes the Lie algebra g of matrices whose derivation preserves K2, its
diagonal part, and the centralizer of one fixed element x of g. In characteristic 0 a torus of linear symmetries
lies in a Cartan subalgebra, whose dimension is at most that of the Fitting null component of ad x for every x.
hypothesis (the bound A5-310 states): the numbers computed over F_p bound those of K2 over Q(i), which needs
quadrics over Z[i] with good reduction at both primes. `symmetry_algebra.py` computes the Fitting null component
over F_p, and it equals the centralizer on every file.

| Fiber | dim of the cone | supports 1, 2, 3, more | dim g | diagonal torus | torus rank at most |
|---|---|---|---|---|---|
| X− → N−, X+ → N+ | 4 | 27, 5, 3, 34 | 23 | 1 | 5 |
| E8-bar → VB | 4 | 0, 6, 9, 6 | 15 | 3 | 5 |
| Iso | 5 | 0, 1, 3, 64 | 17 | 1 | 4 |
| E8-bar → N−, N+ | 5 | 25, 20, 16, 87 | 34 | 2 | 6 |
| W8 → N− | 6 | 3, 12, 16, 113 | 26 | 2 | 5 |

Readings. No K2 is monomial-binomial in the coordinates y; for X− → N− that is a matter of coordinates, since the
certificate of [monomial-ladder](../monomial-ladder/README.md) presents it by monomials and binomials in the
basis of M / q M. Under that hypothesis, for Iso (4 < 5) and W8 → N− (5 < 6) the bound excludes a torus of full rank among the linear
symmetries of K2, so neither K2 is the ideal of a toric variety in any linear coordinates; a torus of rank 4 on Iso
or 5 on W8 would still make them varieties with a torus action of complexity one, which is untested. For
E8-bar → VB and E8-bar → N− the bound leaves a full-rank torus possible and decides nothing. Trinomial rows
(support 3) occur in every K2 and carry no known structure here.

## Structure of the symmetry algebras over F_p (A5-347, A5-348, A5-349)

`symmetry_algebra.py --write` recomputes each g by a second stabilizer construction (the action of every matrix unit on the quadratic
monomials, projected to the quotient by K2) and decomposes it; the record is
[symmetry-algebra.json](symmetry-algebra.json). The dimensions 23, 15, 17, 34
and 26 of the table above reappear on all fourteen files, and the same number of quadrics with coefficients from a
fixed hash stream keeps the Euler field alone (dimension 1) on every file.

| Fiber | dim g | derived series | radical r | nilpotent ideal u | dim r / u | g / r | h | toral rank |
|---|---|---|---|---|---|---|---|---|
| X− → N−, X+ → N+ | 23 | 23, 19, 18 | 20 | 16 | 4 | sl2 | 5, abelian | 5 |
| E8-bar → VB | 15 | 15, 11, 10 | 12 | 8 | 4 | sl2 | 5, abelian | 5 |
| Iso | 17 | 17, 14, 13 | 14 | 11 | 3 | sl2 | 4, abelian | 4 |
| E8-bar → N−, N+ | 34 | 34, 29, 26, 23 | 31 | 26 | 5 | sl2 | 6, abelian | 6 |
| W8 → N− | 26 | 26, 22 | 23 | 19 | 4 | sl2 | 5, abelian | 5 |

What the record proves, over F_p on each file. r, the orthogonal complement of [g, g] under the Killing form, is
an ideal whose derived series reaches 0, [g, g] + r = g, and g / r has dimension 3 and holds three elements h, e,
f with [h, e] = 2e, [h, f] = −2f and [e, f] = h, which the script finds and verifies in coordinates. The quotient
is therefore sl2, and r, a solvable ideal with simple quotient, is the radical. u, the part of r
orthogonal to g under the trace form of the defining representation, is an ideal whose lower central series
reaches 0. h, the Fitting null component of ad x for one fixed x, is abelian and each basis matrix is annihilated
by the squarefree part of its characteristic polynomial, so h is a toral subalgebra (commuting semisimple matrices)
of the dimension in the last column; the trace form on h has full rank on every file, which torality alone does
not force over F_p. The center is the line of the Euler field. The script returns the known
numbers for so(4) with scalars, a parabolic subalgebra of gl(3), gl(3) and the Heisenberg algebra
(`tests/test_a5_symmetry_algebra.py`), and each check has a failing case there: a subspace that is no ideal, a
derived series that stops above 0, two subspaces that miss the whole space, quotients without an sl2 triple, and a
Cartan subalgebra holding a Jordan block. The stabilizer construction is independent of `quadric_structure.py`; the
relation parser is shared.

What the record does not prove. K2 is a modular object here, and so is g. The reading in characteristic 0, where g
would be sl2 with a Levi complement, h the Lie algebra of a maximal torus of the symmetry group, and that torus
would act on the cone, is a hypothesis: equal numbers at 32009 and 32029 give no integral model. The same
computation on quadrics over Q(i) decides it, and no record holds those quadrics for all five fibers. The Levi
factor has the dimension 3 of SU(2), the derived group of the connected stabilizer (SU(2) x U(1)) / Z_2 = U(2) of
the base point of the two N headers in G_2 x U(1), which the kernel-bundle record computes over Q; no record
builds the map from that stabilizer into g, and dim g (15 to 34) exceeds dim G_2 = 14 on every fiber, so
the automorphisms of the algebra account for the Levi factor at most.

Iso (A5-348). K2 is geometrically prime of projective dimension 4 in 17 coordinates with no linear form (ledger
A5-060), so the cone spans the coordinates and a matrix that vanishes on the cone vanishes: the 4-dimensional
toral subalgebra acts faithfully on the 5-dimensional cone. hypothesis: over Q(i) this is a torus of rank 4 acting
effectively, a torus action of complexity one.

W8 → N− (A5-349). V(K2) is the union of two 6-dimensional components C20 and C30 of degrees 20 and 30 (ledger
A5-062), and neither spans the 24 coordinates: the retained ideals at 32009 hold 9 linear forms (`P-p32009.txt`,
V(P) = C20) and 4 (`quotient.txt`, K2 : P = I(C30)), which a Singular standard basis confirms as the whole degree-1
part of each (`w8-component-linear-forms.sing`, run from the repository root; log beside it). The script restricts
h to the subspace cut out by those linear forms: h preserves the 20-dimensional span W of C30 with rank 5 there,
and preserves the 15-dimensional subspace W_P cut out by the linear forms of P, which contains C20, with rank 4
there. K2 : P is radical and C30 is geometrically irreducible, so C30 spans W and no nonzero element of h vanishes
on C30. Whether the derivations of h preserve the ideal K2 : P itself is not checked; with that, and under the
same hypothesis as for Iso, C30 would carry a torus action of complexity one. P is not known to be radical, so the
span of C20 may be a proper subspace of W_P, and the record gives no rank of h on C20. The component ideals are
retained at 32009 only.

X, E8-bar → VB and E8-bar → N have a toral subalgebra larger than the dimension of the cone (5 > 4, 5 > 4,
6 > 5). A torus acts effectively on an irreducible variety of dimension d with rank at most d, so if h integrates,
a subtorus of positive dimension fixes every point of each irreducible component: these K2 would have components
inside proper linear subspaces or nilpotent coordinates, as the monomial quadrics of the X and E8-bar → N echelon
bases (27 and 25 rows of support 1) and the non-reduced E8-bar schemes already show.
