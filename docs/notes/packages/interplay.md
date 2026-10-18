# Algebra package interplay: where the packages overlap, where they are isolated, and how each enters cd_core

Every algebra the installed packages reach enters this repository through one of five
measured maps onto `gororoba_quantum/cd_core.py`: identity, a signed relabeling
`T(e_p) = (-1)^eta(p) e_pi(p)`, the opposite algebra, a subalgebra on named basis
elements, or no map at all because an invariant separates the algebras. The Cayley-Dickson
packages overlap almost completely on the ordinary tower (seven implementations identical to
`cd_core` at D = 8, six at D = 16, five at D = 32); the split tower has three
independent sources that agree through the octonions and split into two inequivalent
16-dimensional constructions; the Clifford packages overlap with `cd_core` only on the
complex numbers, the quaternions and their split forms, because every Clifford algebra is
associative; and the Albert algebra H3(O) has exactly one external source, SageMath, which
maps onto the `cd_core`-built H3(O) on all 729 basis pairs.

## How the claims are checked

- [manual/checks/algebra_interplay.py](manual/checks/algebra_interplay.py) retains 91 native
  basis tables read from the installed packages (`--extract`, local) in
  [manual/checks/interplay_tables.json](manual/checks/interplay_tables.json) and verifies
  135 declared relations against `cd_core` alone (`--check`, gate
  sources-247). The signed-relabeling search fixes e0, assigns signed images to a generating
  set and closes under products; it is calibrated first on `cd_core` itself, which must
  return exactly 24 automorphisms at D = 4 and 1344 at D = 8. Non-isomorphism rests on an
  invariant, never on a failed search: associativity of the basis triples, alternativity
  (decided exactly by the linearized identities on basis triples, since the associator is
  trilinear), or the signature of the norm form of a quadratic table.
- [manual/checks/albert_algebra.py](manual/checks/albert_algebra.py) carries the Albert
  algebra comparison (gate sources-249).
- [manual/checks/run_examples.py](manual/checks/run_examples.py) replays every EXAMPLES block
  of the [manual](manual/README.md) on the build host.
- The reference tables come from `cd_core.cd_sign`: the ordinary algebra of dimension D, the
  split algebra `s(p, q) = cd_sign(D, p, q) * (-1 if p, q >= D/2 else 1)` (one split doubling
  over the ordinary algebra of dimension D/2), and the dual numbers `R[eps]`.

## Dependency and overlap diagram

Arrows point from a package to the package whose products it calls; dotted lines are
optional or non-multiplying links. Every box ends in `cd_core` through the map named on the
right.

```
                                cd_core  (cd_sign, cd_multiply, left_mult_matrix)
                                   ^
     +----------------+------------+-----------+------------------+-----------------+
     |                |                        |                  |                 |
 identity         identity                 identity           identity          identity
     |                |                        |                  |                 |
+------------+  +---------------------+  +------------+  +------------------+  +-------------+
|hypercomplex|  |hypercomplex-engine  |  |cayley-     |  |Cayley-Calculator |  |hyprat       |
| (recursive |  | (closed-form signs, |  |dickson     |  | (hard-coded L_x, |  | (Fraction,  |
|  doubling) |  |  split, dual)       |  | (KD pairs) |  |  gamma per level)|  |  mu / level)|
+------------+  +---------------------+  +------------+  +------------------+  +-------------+
      ^                   ^                                  .        |               |
      |                   | every basis product              .        +--- all +1 ----+
+-----------+   +---------------------+                      .        identical tables at
|mathdunders|   |hypercomplex-algebra |                      .        D = 4, 8, 16
| (Real only)|  | (string expressions)|                      . constructor input only
+-----------+   +---------------------+                      .
                                                   +------------------+     +-------------------+
 +-------------+      4 products per octonion      | numpy-quaternion |<----| Octonion-Sedenion |
 |pyquaternion |<----------------+                 | (compiled dtype) |     | (O and S doubled  |
 +-------------+                 |                 +------------------+     |  over quaternions)|
        identity            +-----------+                identity           +-------------------+
                            |pyoctonion |                                        identity
                            +-----------+
                              identity

 +-------------+   identity at D = 4      +--------------------------+   signed relabeling
 |quaternionic |-------------------------> cd_core                    <---+--------------------+
 +-------------+                                                        |  octonion (torch)  |
                                                                        |  Fano basis, and   |
 +---------+  +--------+  +---------+   identity / relabeling on        |  raw Baez doubling |
 |clifford |==|kingdon |==|galgebra |   Cl(0,1), Cl(1,0), Cl(0,0,1),     +--------------------+
 +---------+  +--------+  +---------+   Cl(0,2), Cl(1,1), Cl(2,0) and
     identical tables on every          even subalgebras; associative,   +--------------------+
     shared signature                   so no octonion map               |  SageMath          |
                                                                         |  opposite algebra; |
 +-------------+   +--------+   +------------+                           |  Albert H3(O)      |
 |python-flint |   |pyadic  |   |  SplitOct  |-- identity onto the       +--------------------+
 |exact L_x    |   |GF(p),  |   +------------+   split reference
 |rank, det    |   |p-adic  |
 +-------------+   +--------+   (exact backends, no table)
```

## Matrix: packages by algebra

Cell codes: `I` identity with the `cd_core` reference (or the split or dual reference);
`R n` signed relabeling with n maps; `op` opposite algebra; `sub` a basis subalgebra of a
larger table the package exposes; `W` reached only through the hypercomplex-engine wrapper;
`x` reachable but separated by an invariant; `.` not reached. Every entry is measured in the
checks named above unless the cell says `sampled`.

| Package | C | split-C | dual | H | split-H | O | split-O | S | split-S | D >= 32 | Cl(p,q) | H3(O) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hypercomplex | I | . | . | I | . | I | . | I | . | I at 32; 64 sampled; to 256 named | . | . |
| hypercomplex-engine | I | I | I | I | I | I | I | I | I | I at 32; to 4096 sampled | . | . |
| hypercomplex-algebra | W | W | W | W | I (dim 2) | I | W | W | W | W, 64 sampled | . | . |
| Cayley-Calculator | I | I (`set_split`) | . | I | R 8 (`set_split`) | I | R 192 (`set_split`) | I | x: all-+1 form, no signed map | I at 32; to 128 unmeasured | . | . |
| cayley-dickson | I | . | . | I | . | I | . | I | . | I at 32 | . | . |
| octonion (torch) | I (tower) | . | . | I (tower) | . | R 1344 (Fano and raw Baez) | . | . | . | . | . | . |
| SplitOct | . | sub `(1, I)` | . | sub `(1, j1, j2, j3)` | sub `(1, j1, I, J1)` | x (norm (4,4) vs (8,0)) | I | . | . | . | . | . |
| mathdunders | . | . | . | . | . | . | . | . | . | . | . | . |
| numpy-quaternion | . | . | . | I | . | . | . | . | . | . | . | . |
| quaternionic | . | . | . | I | . | . | . | . | . | . | . | . |
| pyquaternion | . | . | . | I | . | . | . | . | . | . | . | . |
| clifford | I Cl(0,1); sub of Cl(0,2), Cl(2,0) | I Cl(1,0); sub of Cl(1,1) | I Cl(0,0,1) | I Cl(0,2); even Cl(0,3) I, Cl(3,0) R 24 | R 8 Cl(1,1), Cl(2,0); even Cl(1,2), Cl(2,1) R 8 | x (associative) | x (associative) | . | . | . | native, any (p,q,r) | . |
| kingdon | as clifford | as clifford | I Cl(0,0,1) | as clifford | as clifford | x | x | . | . | . | native | . |
| galgebra | sub of Cl(0,2), Cl(2,0) | sub of Cl(1,1) | . | as clifford | as clifford | x | x | . | . | . | native (two or more generators) | . |
| pyoctonion | . | . | . | . | . | I | . | . | . | . | . | . |
| Octonion-Sedenion | . | . | . | . | . | I | . | I | . | . | . | . |
| SageMath | . | . | . | I `(-1,-1)` | R 8 `(1,1)` | op (flip e3, e5, e6) | R 192 `(1,1,1)` | . | . | . | native (`CliffordAlgebra`) | flip or conjugation on 729 pairs |
| hyprat | I | I | . | I | I | I | I | I | I | I at 32; any rank | . | . |
| python-flint | . | . | . | . | . | . | . | . | . | . | . | . |
| pyadic | . | . | . | . | . | . | . | . | . | . | . | . |

The `cd_core`-built H3(O) of `albert_algebra.py` is the repository's own entry for the last
column.

## By algebra

**Complex numbers (D = 2).** Identity from hypercomplex, the engine, Cayley-Calculator,
cayley-dickson, hyprat and the octonion package's tower `Complex`; Cl(0,1) from clifford and
kingdon is identical, and the bivector block `(1, e12)` of Cl(0,2) and Cl(2,0) is the same
algebra in all three Clifford packages.

**Split-complex numbers.** The engine at exponent 1, hyprat `signs=(1,)` and
Cayley-Calculator after `set_split()` are identical to the split reference; Cl(1,0) in
clifford and kingdon is identical; SplitOct's `(1, I)` and the `(1, e12)` block of Cl(1,1)
are basis subalgebras.

**Dual numbers.** The engine's `dual` kind at n = 0 and Cl(0,0,1) in clifford and kingdon
are identical to `R[eps]`; galgebra builds a degenerate metric only with two or more
generators and prints a warning line when it does.

**Quaternions.** The best-covered algebra: identity from thirteen packages (hypercomplex,
engine, Cayley-Calculator, cayley-dickson, hyprat, numpy-quaternion, quaternionic,
pyquaternion, the torch tower, Sage `QuaternionAlgebra(QQ, -1, -1)`, and Cl(0,2) in all three
Clifford packages), plus the even subalgebras of Cl(0,3) (identical) and Cl(3,0) (24
relabelings, the full signed automorphism count of H). It is also the `(e0, e1, e2, e3)`
subalgebra of every larger `cd_core` level and of the split octonions.

**Split-quaternions.** Engine exponent 2, hyprat `(-1, 1)` and the expression wrapper at
`dim=2` are identical to the split reference; Cayley-Calculator `set_split()`, Sage
`QuaternionAlgebra(QQ, 1, 1)`, Cl(1,1), Cl(2,0) and the even subalgebras of Cl(1,2) and
Cl(2,1) each map by 8 signed relabelings; SplitOct's `(1, j1, I, J1)` is a subalgebra.

**Octonions.** Identity from hypercomplex, the engine (and its wrapper), Cayley-Calculator
(through `octonion_mod`), cayley-dickson, pyoctonion, Octonion-Sedenion and hyprat. Two
packages use other bases: the torch package's Fano table and its raw Baez doubling each map
by 1344 signed relabelings (the first relabels `pi = (0, 1, 2, 4, 3, 6, 7, 5)` with a flip on
its e6; the second keeps the index order and flips e5, e6, e7), and Sage's
`OctonionAlgebra(QQ)` is the opposite algebra in natural order. No Clifford algebra reaches
the octonions: the four three-generator signatures have 0 nonassociative basis triples
against 168 for the octonions.

**Split-octonions.** The engine at exponent 3, SplitOct and hyprat `(-1, -1, 1)` are
identical to the split reference; Cayley-Calculator `set_split()` and Sage
`OctonionAlgebra(QQ, 1, 1, 1)` map by 192 signed relabelings. They share all 168
nonassociative basis triples with the octonions and differ by the norm form, signature
(4, 4) against (8, 0).

**Sedenions.** Identity from hypercomplex, the engine, Cayley-Calculator, cayley-dickson,
Octonion-Sedenion and hyprat. Every D = 16 table here breaks alternativity (1008 basis
triples) and has 1848 nonassociative basis triples.

**Split sedenions.** Two constructions exist and the packages split between them. One split
doubling over the octonions (engine exponent 4, hyprat `(-1, -1, -1, 1)`) is identical to the
split reference. The all-split tower (every gamma or mu +1: Cayley-Calculator `set_split()`,
hyprat `(1, 1, 1, 1)`, identical to each other) shares the norm signature (8, 8) and 1848
nonassociative basis triples with it, and no signed relabeling joins them. Its even-parity
units `e0, e3, e5, e6, e9, e10, e12, e15` square to -1 and close into a positive-definite
quadratic algebra that breaks alternativity on 144 basis triples, so that subalgebra is not
the octonions. Whether the two 16-dimensional algebras are isomorphic is open.

**D >= 32.** Identity at D = 32 exhaustively from hypercomplex, the engine,
Cayley-Calculator, cayley-dickson and hyprat; the engine is sampled to D = 4096 and
hypercomplex to D = 64 in `docs/evidence/algebra_packages/tables.json`.

**Clifford algebras Cl(p, q, r).** clifford and kingdon reach any signature, galgebra any
metric with two or more generators, Sage any quadratic form. Their bitmask-order tables are
identical on every signature measured (p + q + r <= 3). Their exits onto `cd_core` are only
the subalgebras above: Cl(0,1), Cl(1,0), Cl(0,0,1), Cl(0,2), Cl(1,1), Cl(2,0) and the even
subalgebras of the three-generator algebras. Cl(0,3) is not the octonions: it is
associative, and its pseudoscalar e123 is central with `e123^2 = +1`, so
`(1 + e123)(1 - e123) = 0` (manual [clifford](manual/clifford.md), EXAMPLES 2).

**Albert algebra H3(O).** Sage's `JordanAlgebra(OctonionAlgebra(QQ))` is the only external
source. Built from `cd_core` in Sage's basis order (E11, E22, E33, then e0 ... e7 in the
entries 12, 13, 23), the entrywise e3, e5, e6 sign flip carries all 729 Sage basis products
onto `cd_core`'s exactly, and so does entrywise conjugation, which is the transpose and
absorbs Sage's opposite octonion product; the identity and the flip followed by conjugation
each fail on 252 pairs. The falsifier of either map is one basis pair `(i, j)` with
`T(B_i o_Sage B_j) != T(B_i) o_cd T(B_j)` in exact rationals. The `cd_core` product,
commutative by construction, satisfies the Jordan identity on 40 seeded rational pairs; the same builder
over the sedenions breaks the identity on 10 of 10, the control that shows the test detects
a failure.

## Built-on edges, measured

| Edge | Evidence | Consequence |
|---|---|---|
| pyoctonion -> pyquaternion | 4 `pyquaternion.Quaternion.__mul__` calls per octonion product (probe) | a pyquaternion defect reaches pyoctonion |
| Octonion-Sedenion -> numpy-quaternion | octonion halves are `quaternion.quaternion` (probe); the import is unconditional | a numpy-quaternion defect reaches both levels; the `copy.deepcopy` aliasing of quaternion scalars makes `polar()` zero its argument's real part, so `exp(log x) != x` |
| Cayley-Calculator -> numpy-quaternion | none: with `import quaternion` blocked, `QUAT_FOUND` is False in `quat_mod` and `sedenion_mod` and the D = 16 table is still identical to `cd_core` | Cayley-Calculator is independent of numpy-quaternion; the dependency is constructor input only |
| hypercomplex-algebra -> hypercomplex-engine | 4 `FastStandard.multiply_indices` calls for one product of two two-term expressions (probe) | not an independent witness |
| hypercomplex -> mathdunders | 22 generated dunder methods on the level-0 `Real` class and none on higher levels (probe) | plumbing only |
| Octonion-Sedenion and Cayley-Calculator | same author (dist-info `Author-email`), different code: a pair-of-quaternions doubling against hard-coded left matrices | agreement is two implementations by one author |
| hyprat and Cayley-Calculator | independent code; identical all-split tables at D = 4, 8, 16 | the all-split sedenion table has two independent sources |

## Isolation

- mathdunders, python-flint and pyadic carry no multiplication table. flint is the exact
  linear-algebra exit for `cd_core.left_mult_matrix` (rank 12, nullity 4 and determinant 0
  for `e1 + e10`; determinant 256 for `e0 + e9`); pyadic supplies GF(p) and p-adic
  coefficients that `cd_core.cd_multiply` accepts.
- The quaternion trio (numpy-quaternion, quaternionic, pyquaternion) stops at D = 4.
- The Clifford trio never reaches a nonassociative algebra.
- The torch octonion package stops at D = 8 and is the only GPU path (a CUDA product ran on
  the build host, manual [octonion](manual/octonion.md) EXAMPLES 3).
- SageMath stops at the octonions among Cayley-Dickson levels and is the only Albert
  algebra source.
- SplitOct is the only symbolic split-octonion implementation; hyprat and hypercomplex over
  `Fraction` are the exact rational routes, hyprat with exact zero-divisor and annihilator
  tests.

## Statements the measurements revised

The notes below now carry the measured statements.

- [README.md](README.md) and [numpy-quaternion.md](numpy-quaternion.md) say
  Cayley-Calculator builds on numpy-quaternion; it multiplies without it (table above).
- [cayley-calculator.md](cayley-calculator.md) records MIT from the build recipe; the
  installed dist-info carries no license field.
- [galgebra.md](galgebra.md) says an `int` scalar fails in products; it fails on the right
  of a product and in `blade_coefs`, while `s * e1` succeeds (manual
  [galgebra](manual/galgebra.md) EXAMPLES 3).
- [README.md](README.md) counts seventeen packages; with hyprat the set is eighteen
  algebra packages, plus python-flint and pyadic as exact backends.

## Open

- Whether the all-split sedenions (every mu +1) and the split sedenions with an ordinary
  octonion parent are isomorphic: no signed relabeling exists, the norm signatures and
  nonassociative triple counts agree, and an invariant that separates them, or an
  isomorphism off the basis, has not been found.
- Cayley-Calculator's pathions, chingons and routons beyond D = 32 and hypercomplex beyond
  D = 64 are unmeasured against `cd_core`.
