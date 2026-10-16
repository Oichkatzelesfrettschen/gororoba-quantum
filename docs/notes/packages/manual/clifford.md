# clifford(3) -- numerical geometric algebra Cl(p, q, r) on numba

## NAME

`clifford` 1.5.1 (PyPI `clifford`, Arch `python-clifford`): layouts for Clifford algebras of
any signature, multivectors with geometric, inner and outer products, involutions, duals,
inverses, exponentials, rotors, conformal and projective models, and multivector arrays.
Release binding: [../clifford.md](../clifford.md).

## SYNOPSIS

```python
import numpy as np
import clifford

layout, blades = clifford.Cl(0, 3)          # p generators square to +1, q to -1, r to 0
e1, e2, e3, e123 = blades["e1"], blades["e2"], blades["e3"], blades["e123"]
x = 1 + 2 * e1 + 3 * (e1 * e2)
x * e3, x | e3, x ^ e3, ~x, x.inv(), x.dual(), (np.pi / 4 * e1 * e2).exp()
layout.names, layout.sig, x.value                    # blade order and dense coefficients
```

## DESCRIPTION

`Cl(p, q, r, sig=None, names=None, firstIdx=1)` returns a `Layout` and a dict of basis
blades; a `MultiVector` holds a dense coefficient vector `.value` in `layout.names` order
(grade-sorted), and the products are numba-compiled from the layout's multiplication tables.
`clifford.g3`, `g3c`, `pga`, `sta` and the other submodules predefine common layouts.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Cl(p=0, q=0, r=0, sig=None, names=None, firstIdx=1)`, `Layout`, `ConformalLayout`, `conformalize`, `MultiVector`, `MVArray`, `randomMV`, `layout.randomV`, `layout.randomRotor`, `layout.scalar`, `layout.pseudoScalar` | |
| products | `*` geometric, `|` inner, `^` outer, `gp`, `ip`, `op`, `lc` (left contraction), `vee` / `meet` / `join`, `commutator`, `anticommutator` | |
| involutions, norm, inverse | `~x` reversion, `gradeInvol()`, `conjugate()`, `adjoint()`, `dual()`, `normal()`, `mag2()`, `abs()`, `inv()`, `leftInv()`, `rightInv()`, `hitzer_inverse()`, `shirokov_inverse()` | |
| exp, log, trigonometry | `exp()`, `general_exp`, `sin cos tan sinh cosh tanh`, `taylor_expansions` | no log |
| rotations | rotors `R = exp(-theta/2 B)`, sandwich `R * v * ~R`, `layout.randomRotor`, `tools` (frames, rotor estimation) | |
| grades | `x(k)` grade projection, `grades()`, `even`, `odd`, `isBlade()`, `isVersor()`, `factorise()`, `project` | |
| matrix representations | `layout.gmt`, `imt`, `omt` (sparse tables), `get_left_gmt_matrix(x)`, `get_right_gmt_matrix(x)`, `val_get_left_mt_matrix`, `linear_operator_as_matrix` | |
| associator | none; the algebra is associative | |
| symbolic support | none; float64 or the dtype of `.value` | |
| dimension range | any (p, q, r); dense 2^n coefficients | |
| dtype, batching, GPU | `MVArray` object arrays; numba on CPU; no GPU | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import clifford
print(inspect.signature(clifford.Cl))
layout, blades = clifford.Cl(0, 3)
print(layout.names, layout.sig.tolist())
print(sorted(n for n in dir(blades["e1"]) if not n.startswith("_")))
```

```text
(p: int = 0, q: int = 0, r: int = 0, sig=None, names=None, firstIdx=1, mvClass=<class 'clifford._multivector.MultiVector'>) -> Tuple[clifford._layout.Layout, Dict[str, clifford._multivector.MultiVector]]
['', 'e1', 'e2', 'e3', 'e12', 'e13', 'e23', 'e123'] [-1, -1, -1]
['I', 'adjoint', 'anticommutator', 'as_array', 'astype', 'basis', 'blades_list', 'clean', 'commutator', 'conjugate', 'cos', 'cosh', 'dual', 'even', 'exp', 'factorise', 'gradeInvol', 'grades', 'hitzer_inverse', 'inv', 'invPS', 'isBlade', 'isScalar', 'isVersor', 'join', 'layout', 'lc', 'leftInv', 'leftLaInv', 'left_complement', 'mag2', 'meet', 'normal', 'normalInv', 'odd', 'project', 'pseudoScalar', 'rightInv', 'right_complement', 'round', 'shirokov_inverse', 'sin', 'sinh', 'tan', 'tanh', 'value', 'vee', 'x']
```

2. Cl(0,2) is the `cd_core` quaternion table; Cl(0,3) is associative, its pseudoscalar is
   central and squares to +1, and so it carries zero divisors the octonions lack.

<!-- example -->
```python
import itertools
import clifford
from cd_core import cd_sign
layout, blades = clifford.Cl(0, 2)
B = [layout.scalar, blades["e1"], blades["e2"], blades["e12"]]
bad = sum((B[p] * B[q]).value[p ^ q] != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("Cl(0,2) against cd_core D=4:", bad, "mismatches")
layout, blades = clifford.Cl(0, 3)
B = [layout.scalar] + [blades[n] for n in layout.names[1:]]
nonassoc = sum(((a * b) * c - a * (b * c)).mag2() > 0 for a, b, c in itertools.product(B, repeat=3))
I = blades["e123"]
print("nonassociative basis triples:", nonassoc, " e123^2 =", I * I, " central:", all(I * b == b * I for b in B))
print("(1 + e123)(1 - e123) =", (1 + I) * (1 - I))
print("even subalgebra squares:", [blades[n] * blades[n] for n in ("e12", "e13", "e23")])
```

```text
Cl(0,2) against cd_core D=4: 0 mismatches
nonassociative basis triples: 0  e123^2 = 1  central: True
(1 + e123)(1 - e123) = 0
even subalgebra squares: [-1, -1, -1]
```

3. A rotor, the dual numbers Cl(0,0,1) and the left multiplication matrix.

<!-- example -->
```python
import numpy as np
import clifford
layout, blades = clifford.Cl(3)
e1, e2 = blades["e1"], blades["e2"]
R = (-np.pi / 4 * e1 * e2).exp()
print("R e1 ~R =", (R * e1 * ~R).clean(1e-12))
layout, blades = clifford.Cl(0, 0, 1)
eps = blades["e1"]
print("eps * eps =", eps * eps, "| (1 + eps)^-1 =", (1 + eps).inv())
layout, blades = clifford.Cl(0, 2)
x = 1 + 2 * blades["e1"] + 3 * blades["e12"]
print(layout.get_left_gmt_matrix(x).astype(int).tolist())
```

```text
R e1 ~R = (1.0^e2)
eps * eps = 0 | (1 + eps)^-1 = 1.0 - (1.0^e1)
[[1, -2, 0, -3], [2, 1, -3, 0], [0, 3, 1, -2], [3, 0, 2, 1]]
```

## MAPPING TO cd_core

- Cl(0,1) is the `cd_core` complex numbers and Cl(0,2) the `cd_core` quaternions, identical
  in bitmask order `(1, e1, e2, e12)` (EXAMPLES 2).
- Cl(1,0) is the split-complex numbers (identical); Cl(1,1) and Cl(2,0) are the
  split-quaternions (8 signed relabelings each); Cl(0,0,1) is the dual numbers.
- Every three-generator signature Cl(0,3), Cl(1,2), Cl(2,1), Cl(3,0) is associative, so none
  is the octonions or the split-octonions (168 nonassociative basis triples). Their even
  subalgebras on `(1, e12, e13, e23)` are the quaternions for Cl(0,3) (identical) and
  Cl(3,0) (24 relabelings) and the split-quaternions for Cl(1,2) and Cl(2,1).
- All of these are measured in [checks](checks/interplay_tables.json); kingdon and galgebra
  give the same bitmask-order tables on every shared signature.

## TRAPS

- `layout.names` is grade-sorted (`e1 e2 e3 e12 e13 e23 e123`), not bitmask order; map
  blade names before comparing coefficient positions with `cd_core`.
- `Cl(p, q)` puts the first p generators at +1; the quaternions are `Cl(0, 2)`.
- Clifford algebras are associative: no signature reaches the octonions or sedenions.
- The first product of a layout compiles with numba and takes seconds.

## LICENSE

BSD-3-Clause (dist-info `License: bsd`).

## SEE ALSO

[kingdon](kingdon.md), [galgebra](galgebra.md), [interplay](../interplay.md).
