# Algebras adjacent to the Cayley-Dickson tower

`cd_core` fixes one construction: the doubling
`(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))` over the real or rational
coefficients, gamma = -1 at every level, basis products
`e_p e_q = s(p, q) e_{p xor q}`. An adjacent algebra connects to it in one of
four ways: it changes the coefficient ring, changes the doubling parameter,
sits inside a coefficient extension, or is built from the octonion product.
The rest stay isolated. [candidates.md](candidates.md) ranks the packages
that implement each.

## Decomposition

```
                          cd_core  (gamma = -1, coefficients in Z, Q, R)
                                |
   R -- C -- H -- O -- S(16) -- 32 -- ...        (doubling levels)
   |    |    |    |      |
   |    |    |    |      +-- zero divisors: no norm multiplicativity
   |    |    |    +--------- alternative: L_i L_j + L_j L_i = -2 delta
   |    |    +-------------- associative: Cl(0,2) = H
   |    +------------------- commutative
   |
   +-- change the parameter mu (hyprat, hypercomplex-engine split, splitoct)
   |      mu = +1 : split-complex, split-quaternion (M2(R)), split-octonion
   |      mu = 0  : dual numbers R[eps]/eps^2   (degenerate, hyprat refuses)
   |      other mu: quaternion algebras (-1, 2), generalized octonions
   |
   +-- change the coefficient ring K (cd_core tables pass unchanged)
   |      K = Q_p (pyadic, Sage Qp)   K = GF(p), p odd (galois)
   |      K = C   : biquaternions = H tensor C = M2(C)
   |      K = dual numbers : dual quaternions
   |
   +-- sit inside a coefficient extension of a CD level
   |      split-complex  : (i e1)^2 = +1 inside C tensor C
   |      bicomplex = tessarines = C tensor C inside H tensor C
   |
   +-- built on the octonion product (O is a dependency)
   |      Albert algebra H3(O)  =  3 x 3 Hermitian O matrices, X o Y = (XY+YX)/2
   |      Der(O) = G2 (14),  Der(H3(O)) = F4 (52),  Freudenthal triple system, E6
   |
   +-- share only the XOR label set, different sign cocycle
   |      Clifford Cl(0,n) (clifford, kingdon, galgebra, numga)
   |      exterior algebras (Cl with zero metric, intersecting supports vanish)
   |
   +-- isolated (share only a subfield of coefficients)
          surreal numbers (dyadic rationals), hyperreals (ultrapower of R)
          p-adic completion itself (a different completion of Q)
```

## Overlaps with the tower, by class

### Coefficient-ring substitution

The cd_core sign function takes values in {-1, +1}, so the structure
constants are integers and the same table defines the algebra over any
commutative ring. Three substitutions are mathematically live.

- **Q_p.** The octonion norm form `x conj(x)` is the sum of eight squares.
  Every quadratic form in five or more variables is isotropic over Q_p, so the
  octonions over Q_p carry a nontrivial null vector and are the split octonions
  (isomorphic to Zorn vector matrices) for every prime p, 2 included. The
  quaternions (-1, -1) split at every odd p and ramify at p = 2 (and at the
  real place). The step from Q to Q_p is therefore the passage from the
  division octonions to the split octonions that splitoct already tabulates
  at signature (4, 4), without a change of the cd_core table. Confidence:
  high for the splitting statements (standard local class field facts);
  unmeasured in this repository because no package stage runs a CD level over
  `PAdic`.
- **GF(p), p odd.** The doubling needs 2 invertible for conjugation to be a
  nondegenerate involution; char 2 collapses `conj`. galois 0.4.11 is
  installed and unrecorded in the package table. A finite-field census of
  sedenion zero divisors is a direct counting question, still orthogonal to
  the real/rational census in the repository.
- **C and dual numbers.** Coefficient domain C gives the biquaternions at D = 4
  and is the complex-linear extension the docs/notes/algebra_circuit_rules.md rules already require to
  state (the complexified sedenion has `(e_0 + i e_1)(e_0 - i e_1) = 0`).
  Dual-number coefficients give dual quaternions; both reuse the D = 4 table.

### Parameter change in the doubling

hyprat's per-level mu generalizes the doubling: mu = +1 at one level gives the
split variant, rational mu gives other quaternion and octonion algebras over Q.
The split variants keep every associator sign of the ordinary tower while
changing the signature (README rule 3). mu = 0 is dual numbers; hyprat
requires mu nonzero. cd_core has no mu parameter, so a generalized table
enters evidence only through a declared map: identity at mu = -1, or "split"
for mu = +1 as in `algebra_package_tables.py`.

### Algebras that embed after extension

- **Split-complex** R[j]/(j^2 - 1) is Cl(1,0) = R + R. It is not a real
  subalgebra of any CD level (all imaginary units square to -1), and embeds
  into the complexification C tensor C as `j = i e1`.
- **Bicomplex / tessarines** C tensor C is a commutative algebra of dimension
  4 over R that contains the zero divisors `(1 + i e1)(1 - i e1) = 0` (the
  case already recorded). It is not a CD level; it sits inside the
  biquaternions H tensor C = M2(C).
- **Split quaternions / coquaternions** M2(R) = (-1, +1) is the mu = (-1, +1)
  preset and a real form of H tensor C.
- **Quaternions as Clifford** Cl(0,2) = H is measured identical at D = 4
  (clifford, kingdon, galgebra).

### Octonion left multiplications as a Clifford representation

The XOR labeling is shared with Clifford algebras: `e_S e_T` in Cl(0,n) lands
on the symmetric difference of the index sets, the same operation as
`e_p e_q -> e_{p xor q}` on bitmasks. The sign functions differ: Clifford's is
associative, CD's is not. A measured consequence on cd_core: the operators
`L_i = left_mult_matrix(D, e_i)` for i = 1, ..., D-1 satisfy
`L_i L_j + L_j L_i = -2 delta_ij I` with zero violations at D = 2, 4, 8 (a
representation of Cl(0,1), Cl(0,3), Cl(0,7) on R^D) and 672 entry violations
at D = 16. The cause is alternativity: `L_x^2 = L_{x^2}` holds through D = 8
and fails at D = 16, so the sedenion left multiplications generate no
Clifford representation. Method: the 16 x 16 anticommutator check on
`cd_core._matmul` over all unit pairs.

### Derivations

A linear solve of `d(xy) = d(x) y + x d(y)` on the cd_core structure
constants (unknown d as a D x D matrix, D^3 equations in D^2 unknowns, rank by
SVD) gives derivation spaces of dimension 3, 14 and 14 at D = 4, 8, 16. This
reproduces `Der(H) = so(3)`, `Der(O) = g2` and the reported
`Der(S) = g2` (sedenion derivations collapse to the octonion ones); the
sedenion automorphism group is G2 x S3 in the literature, so this is a
consistent dimension count and no new claim. python-flint would turn the rank
into an exact certificate.

### Albert algebra and exceptional structures

`H3(O)` is the 27-dimensional real Jordan algebra of Hermitian 3 x 3 matrices
over O with `X o Y = (XY + YX)/2`; its derivation algebra is F4 (dimension
52). The product uses only octonion multiplication and octonion conjugation,
so the algebra depends on a convention, and the convention is exactly the one
`cd_core` fixes at D = 8.

- **SageMath 10.10** builds it as `ExceptionalJordanAlgebra` on
  `OctonionAlgebra(R, a, b, c)` with `2` a unit in R. Its octonions are the
  opposite of cd_core in natural order, and flipping e3, e5, e6 is an
  isomorphism onto cd_core ([sagemath.md](sagemath.md)). The signed
  relabeling T fixes e0 and sends each imaginary unit to plus or minus an
  imaginary unit, so it commutes with conjugation and carries Hermitian
  matrices to Hermitian matrices. Applied entrywise it gives an algebra
  isomorphism `H3(O_Sage) -> H3(O_cd)`. Prediction: the Jordan product tables
  agree under T on all 27 x 27 basis pairs. The prediction rests on the
  retained D = 8 isomorphism and has not been run; a Sage export in the style
  of `sagemath_octonion_table.sage` would measure it. The Sage docstring also
  fixes the check `len(J.derivations_basis()) == 52` equal to
  `LieAlgebra(QQ, cartan_type='F4').dimension()`.
- **Native builder.** Because the Albert product needs only `cd_multiply` at
  D = 8, a 30-line builder over `cd_core` yields the table without any
  package and works as the independent reference for the Sage export.
- **Other packages.** No PyPI or GitHub package implements the Albert
  algebra, Jordan algebras of other types, or Freudenthal triple systems
  (candidates.md lists the names tried). Sage provides special Jordan
  algebras from associative algebras and from symmetric bilinear forms, plus
  the exceptional one; Lie algebras of types F4, G2, E6, E7, E8 are Sage
  matrix Lie algebras.

### Isolated

- **Surreal numbers** form a real-closed ordered field, a proper class, and
  share with cd_core the dyadic rationals only. CD over No is formally defined
  (ordered coefficients), but no maintained Python implementation exists; the
  PyPI name `surreal` is an unrelated project.
- **Hyperreals** are an ultrapower of R; transfer makes every first-order fact
  of the tower hold unchanged, and no computation needs them. PyPI
  `hyperreal` is a text-search library.
- **p-adic numbers** are a completion of Q, not an algebra over it. They enter
  the repository only as a coefficient field (above) and need an additional
  rule: all p-adic equalities are stated to a precision `O(p^N)`.
- **Grassmann/exterior algebra** is the zero-metric Clifford algebra: the
  XOR label becomes a union restricted to disjoint supports, so it overlaps
  the tower only through the shared bitmask indexing.

## Package-to-cd_core entry and exit points

| Algebra | Entry onto cd_core | Exit from cd_core | Package route |
|---|---|---|---|
| CD tower, mu = -1 | identity | identity | hypercomplex, hypercomplex-engine, cayley-dickson, hyprat |
| split variants (mu = +1) | "split" relation (same index table and associators, different squares) | none | hyprat, hypercomplex-engine split, splitoct |
| Q_p coefficients | integer table passes unchanged | reduce coefficients modulo p^N | pyadic, Sage Qp |
| GF(p) coefficients | integer table mod p, p odd | lift of signs | galois |
| biquaternions, dual quaternions | D = 4 table with complex or dual coefficients | real part | pyquaternion, dual-quaternions |
| Cl(0,2), exterior | D = 4 identity | none | clifford, kingdon, galgebra |
| Albert algebra | entrywise signed relabeling T for Sage; none for a native builder | octonion block of the (1,2) entry | Sage 10.10, native over cd_core |
| G2, F4 Lie algebras | derivation spaces of the table | Cartan matrix, dimension | Sage; python-flint rank |
| surreal, hyperreal | none | none | skip |

## Not measured

The splitting of the octonions over Q_p, the entrywise map T on H3, and the
mu-parameter tables of hyprat are predictions from the cited structure. Each
joins `algebra_package_tables.py` or a retained Sage export only when a
package is installed and its table binds to a pinned archive.
