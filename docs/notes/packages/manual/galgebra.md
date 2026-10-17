# galgebra(3) -- symbolic geometric algebra and calculus on SymPy

## NAME

`galgebra` 0.6.0 (PyPI `galgebra`, Arch `python-galgebra`): geometric algebras over any
metric, including symbolic and curvilinear metrics, with multivectors whose coefficients
are SymPy expressions, differential operators and LaTeX printing. Release binding:
[../galgebra.md](../galgebra.md).

## SYNOPSIS

```python
import sympy
from galgebra.ga import Ga

ga, e1, e2 = Ga.build("e1 e2", g=[-1, -1])        # metric diagonal; Cl(0, 2)
one = ga.mv(sympy.S.One, "scalar")
x = ga.mv("x", "mv")                               # a general symbolic multivector
x * e1, x | e1, x ^ e1, x.rev(), x.inv(), (e1 ^ e2).blade_coefs([one, e1, e2, e1 ^ e2])
```

## DESCRIPTION

`Ga.build(names, g=metric, coords=...)` returns the algebra and its basis vectors; `Mv`
objects hold SymPy expressions over the basis blades. Products are computed symbolically
from the metric (the installed `galgebra/ga.py`, `galgebra/mv.py`); `galgebra.lt` adds
linear transformations and `galgebra.dop` differential operators.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Ga(bases, *, wedge=True, g=..., coords=..., norm=...)`, `Ga.build(...)`, `ga.mv(value, kind)` (`"scalar"`, `"vector"`, `"bivector"`, `"mv"`, ...), `ga.basis`, `ga.blades` | |
| products | `*`, `|` (inner), `^` (outer), `<` and `>` (left and right contractions), `>>` (commutator), `<<` (anticommutator) | dunders in `galgebra/mv.py` |
| involutions, norm, inverse | `rev()`, `even()`, `odd()`, `dual()`, `norm()`, `norm2()`, `inv()`, `grade(k)`, `get_grade` | |
| exp, trigonometry | `exp()`; SymPy functions of coefficients | |
| calculus | `galgebra.dop` (`Pdop`, `Sdop`), `galgebra.lt.Lt` linear transformations | |
| coefficients | `blade_coefs(blades)`, `obj` (the SymPy expression), `simplify()`, `trigsimp()` | |
| associator | none; associative | |
| symbolic support | full SymPy | |
| dimension range | any metric; symbolic cost grows fast | |
| dtype, batching, GPU | SymPy objects only | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import sympy
from galgebra.ga import Ga
ga, e1, e2 = Ga.build("e1 e2", g=[-1, -1])
print([n for n in dir(ga) if not n.startswith("_")][:60])
print(sorted(n for n in dir(e1) if not n.startswith("_")))
```

```text
['Christoffel_symbols', 'E', 'I', 'Isq', 'Mlt', 'Mul', 'Pdiffs', 'Pdop_identity', 'ReciprocalFrame', 'X', 'base_expansion', 'base_expansion_dict', 'base_to_blade_rep', 'bases', 'bases_dict', 'bases_lst', 'bases_to_grades_dict', 'bases_to_indexes', 'bases_to_indexes_dict', 'basic_mul', 'basic_mul_keys', 'basic_mul_table', 'basic_mul_table_dict', 'basic_mul_values', 'basis', 'basis_super_scripts', 'basis_vectors', 'blade_derivation', 'blade_expansion', 'blade_expansion_dict', 'blade_reduce', 'blade_super_scripts', 'blade_to_base_rep', 'blades', 'blades_lst', 'blades_to_grades_dict', 'blades_to_indexes', 'blades_to_indexes_dict', 'build', 'com', 'connect_flg', 'connection', 'coord_vec', 'coords', 'count', 'de', 'debug', 'derivatives_of_g', 'detg', 'dg', 'dop', 'dot', 'dot_mode', 'dot_orthogonal', 'dot_product_basis_blades', 'dot_table_dict', 'dslot', 'dual_mode', 'dual_mode_lst', 'dual_mode_value']
['Fmt', 'Ga', 'Grad', 'Mul', 'base_rep', 'blade_coefs', 'blade_flg', 'blade_rep', 'ccon', 'char_Mv', 'characterise_Mv', 'collect', 'components', 'coords', 'diff', 'dual', 'dual_mode_lst', 'even', 'exp', 'expand', 'fmt', 'func', 'g_invol', 'get_coefs', 'get_grade', 'grade', 'grades', 'hitzer_inverse', 'i_grade', 'inv', 'is_base', 'is_blade', 'is_blade_rep', 'is_scalar', 'is_vector', 'is_versor', 'is_zero', 'list', 'mag', 'mag2', 'norm', 'norm2', 'obj', 'odd', 'pdiff', 'proj', 'project_in_blade', 'pure_grade', 'qform', 'recp', 'reflect_in_blade', 'rev', 'rotate_multivector', 'scalar', 'set_coef', 'setup', 'shirokov_inverse', 'simplify', 'sp', 'subs', 'title', 'trigsimp', 'undual', 'versor_flg']
```

2. Cl(0,2) against `cd_core`, and a symbolic product.

<!-- example -->
```python
import sympy
from galgebra.ga import Ga
from cd_core import cd_sign
ga, e1, e2 = Ga.build("e1 e2", g=[-1, -1])
B = [ga.mv(sympy.S.One, "scalar"), e1, e2, e1 ^ e2]
bad = sum((B[p] * B[q]).blade_coefs(B)[p ^ q] != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("mismatches", bad)
a, b = sympy.symbols("a b")
x = a + b * (e1 ^ e2)
print(x * x)
```

```text
mismatches 0
a**2 - b**2 + 2*a*b*e1^e2
```

3. Three traps: one generator, a Python int scalar, a degenerate metric that prints.

<!-- example -->
```python
import sympy
from galgebra.ga import Ga
try:
    Ga.build("e1", g=[-1])
except ValueError as e:
    print("ValueError:", e)
ga, e1, e2 = Ga.build("e1 e2", g=[-1, -1])
s = ga.mv(1, "scalar")
print("s * e1 =", s * e1, "| type of s.obj:", type(s.obj).__name__)
try:
    e1 * s
except TypeError as e:
    print("e1 * s: TypeError:", e)
ga0, f1, f2 = Ga.build("e1 e2", g=[0, -1])
print("f1 f1 =", f1 * f1)
```

```text
ValueError: for basis "e1" coords must be entered
s * e1 = e1 | type of s.obj: int
e1 * s: TypeError: 1 is not a SymPy Expr
!!!!If I**2 = 0, I cannot be normalized!!!!
f1 f1 = 0
```

## MAPPING TO cd_core

`Ga.build("e1 e2", g=[-1, -1])` on `(1, e1, e2, e1^e2)` is identical to the `cd_core`
quaternions; `g=[1, -1]` and `g=[1, 1]` give the split-quaternions by signed relabeling, and
the three-generator metrics are associative with quaternion or split-quaternion even
subalgebras, identical to [clifford](clifford.md) and [kingdon](kingdon.md) in bitmask
order ([checks](checks/interplay_tables.json)). One-generator algebras are read as the
`(1, e1e2)` or `(1, e1)` block of a two-generator algebra.

## TRAPS

- A one-generator `Ga.build` raises `ValueError` (EXAMPLES 3).
- `ga.mv(1, "scalar")` holds a Python `int`: `s * e1` works while `e1 * s`, `s | e1` and
  `blade_coefs` on it raise `TypeError: 1 is not a SymPy Expr`; pass `sympy.S.One` (EXAMPLES 3).
- A degenerate metric prints `!!!!If I**2 = 0, I cannot be normalized!!!!` to stdout at
  build time (EXAMPLES 3).
- Read coefficients with `blade_coefs(basis)`; printing order follows the blade list.

## LICENSE

BSD-3-Clause (dist-info `License: BSD`).

## SEE ALSO

[clifford](clifford.md), [kingdon](kingdon.md), [interplay](../interplay.md).
