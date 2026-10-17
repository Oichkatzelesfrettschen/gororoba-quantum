# sagemath(1) -- exact octonion, quaternion, Clifford and Albert algebras in SageMath

## NAME

SageMath 10.10 (Arch `sagemath` 10.10-2.1, the `sage` command): exact algebras over any
commutative ring, among them `OctonionAlgebra(R, a=1, b=1, c=1)` (Cayley-Dickson octonions
with three parameters, default `a = b = c = -1`), `QuaternionAlgebra(R, a, b)`, `CliffordAlgebra(QuadraticForm)` and
`JordanAlgebra(OctonionAlgebra(R))`, the 27-dimensional exceptional Jordan (Albert)
algebra. Measured relation: [../sagemath.md](../sagemath.md). This manual uses Sage only
through short `sage -c` calls.

## SYNOPSIS

```sh
sage -c '
O = OctonionAlgebra(QQ)                       # basis 1, i, j, k, l, li, lj, lk
Os = OctonionAlgebra(QQ, 1, 1, 1)             # split octonions
H = QuaternionAlgebra(QQ, -1, -1); Hs = QuaternionAlgebra(QQ, 1, 1)
C = CliffordAlgebra(QuadraticForm(QQ, 2, [-1, 0, -1]))
J = JordanAlgebra(O)                          # 27-dimensional, basis E11 E22 E33 then x, y, z slots
i, j = O.gens()[:2]; print(i * j, (i + j).norm(), J.basis()[3] * J.basis()[12])
'
```

## DESCRIPTION

`OctonionAlgebra(R, a=-1, b=-1, c=-1)` builds the octonion algebra with parameters
`(a, b, c)` over `R` (the installed `sage/algebras/octonion_algebra.pyx`,
`__classcall_private__`); the defaults give the ordinary octonions, every imaginary unit
squaring to -1, and `(1, 1, 1)` gives the split octonions (EXAMPLES 1 reads both). Elements expose `conjugate`, `norm`, `quadratic_form`,
`real_part`, `imag_part`, `vector`, `abs`, `is_unit`. `JordanAlgebra(O)` stores an
element as `(alpha, beta, gamma, x, y, z)` for the Hermitian matrix
`[[alpha, x, y], [x*, beta, z], [y*, z*, gamma]]` with product `(XY + YX)/2`.

## API SURFACE

| Capability | API | Behavior |
|---|---|---|
| construction | `OctonionAlgebra(R, a, b, c, names=...)`, `QuaternionAlgebra(R, a, b)`, `CliffordAlgebra(Q)`, `JordanAlgebra(O)`, `algebras.Octonion`, `.basis()`, `.gens()` | exact over `QQ`, number fields, finite fields, polynomial rings |
| products | `*`, `+`, `-`, scalar products | |
| conjugate, norm, inverse | `conjugate()`, `norm()`, `quadratic_form()`, `abs()`, `~x` / `x.inverse()`, `is_unit()` | |
| structure | `is_division_algebra()`, `is_matrix_ring()` (quaternions), `derivations_basis()` (Jordan, 52 = dim F4) | |
| exp, log | none for these algebras | |
| matrix representations | `vector()`, `monomial_coefficients()`; module morphisms | |
| symbolic support | full: coefficients in any Sage ring | |
| dimension range | quaternions, octonions, 27-dim Albert algebra, Clifford of any quadratic form; no sedenions | |
| dtype, batching, GPU | exact; scalar elements | |

## EXAMPLES

1. Octonion products: Sage's `i * j` against `cd_core` `e1 e2 = +e3`; basis squares of the
   ordinary and split forms.

<!-- example -->
```sh
sage -c '
from sage.version import version
O = OctonionAlgebra(QQ); B = O.basis()
print(version, list(B))
print("i*j =", B[1] * B[2], " j*i =", B[2] * B[1], " (i+j).norm() =", (B[1] + B[2]).norm())
print("squares", [b * b for b in B])
Os = OctonionAlgebra(QQ, 1, 1, 1)
print("split squares", [b * b for b in Os.basis()])
'
```

```text
10.10 [1, i, j, k, l, li, lj, lk]
i*j = -k  j*i = k  (i+j).norm() = sqrt(2)
squares [1, -1, -1, -1, -1, -1, -1, -1]
split squares [1, 1, 1, -1, 1, -1, -1, 1]
```

2. Quaternion algebras and a Clifford algebra.

<!-- example -->
```sh
sage -c '
H = QuaternionAlgebra(QQ, -1, -1); i, j, k = H.gens()[0], H.gens()[1], H.gens()[0] * H.gens()[1]
print(H.basis(), i * j, j * i, H.is_division_algebra())
Hs = QuaternionAlgebra(QQ, 1, 1); print([b * b for b in Hs.basis()], Hs.is_matrix_ring())
C = CliffordAlgebra(QuadraticForm(QQ, 2, [-1, 0, -1])); e1, e2 = C.gens()
print(e1 * e1, e1 * e2 + e2 * e1, (e1 * e2) ** 2)
'
```

```text
(1, i, j, k) k -k True
[1, 1, 1, -1] True
-1 0 -1
```

3. The Albert algebra: a Jordan product of two basis elements, its dimension, and
   commutativity of a random pair.

<!-- example -->
```sh
sage -c '
J = JordanAlgebra(OctonionAlgebra(QQ)); B = J.basis()
print(len(B), J.one() == B[0] + B[1] + B[2])
print(B[3] * B[12])
X = J([1, 2, -1, OctonionAlgebra(QQ).basis()[3], 1, 2]); Y = J([0, 1, 3, 2, OctonionAlgebra(QQ).basis()[5], -1])
print(X * Y == Y * X, (X * Y) * (X * X) == X * (Y * (X * X)))
'
```

```text
27 True
[     0      0      0]
[     0      0  1/2*i]
[     0 -1/2*i      0]
True True
```

## MAPPING TO cd_core

- `OctonionAlgebra(QQ)` in its natural order `(1, i, j, k, l, li, lj, lk)` = `(e0, ..., e7)`
  is the opposite algebra of `cd_core`: `e_a *Sage e_b = e_b *cd e_a` on all 64 pairs, and
  the sign flip on e3, e5, e6 is an isomorphism onto `cd_core` (the package note;
  [checks](checks/interplay_tables.json) counts 1344 signed relabelings of the opposite
  table, the identity first).
- `OctonionAlgebra(QQ, 1, 1, 1)` maps onto the split reference (one split doubling over the
  `cd_core` quaternions) by 192 signed relabelings, `QuaternionAlgebra(QQ, -1, -1)` is
  identical to the `cd_core` quaternions in the basis `(1, i, j, k)`, and
  `QuaternionAlgebra(QQ, 1, 1)` maps onto the split-quaternions by 8 signed relabelings.
- The Albert algebra `JordanAlgebra(OctonionAlgebra(QQ))` maps onto H3(O) built from
  `cd_core` on all 729 basis pairs by the entrywise e3, e5, e6 sign flip and, separately, by
  entrywise conjugation (the transpose); the untransformed tables differ on 252 pairs
  ([checks/albert_algebra.py](checks/albert_algebra.py),
  [checks/sage_albert_table.json](checks/sage_albert_table.json)).

## TRAPS

- Code ported from Sage reverses every octonion product unless it maps through the
  e3, e5, e6 flip or conjugation.
- `OctonionAlgebra(R)` defaults to `(-1, -1, -1)`, the ordinary octonions; `(1, 1, 1)` is
  the split form (EXAMPLES 1).
- `norm()` is the magnitude (`(i + j).norm()` is `sqrt(2)`); the quadratic form is
  `quadratic_form()` (EXAMPLES 1).
- `version()` at the Sage prompt prints a `DeprecationWarning`; read `sage.version.version`.
- Sage has no sedenion or higher Cayley-Dickson level among these constructors.

## LICENSE

GPL-2.0-or-later (the package note).

## SEE ALSO

[octonion](octonion.md) (the other octonion basis that differs from `cd_core`),
[splitoct](splitoct.md), [interplay](../interplay.md).
