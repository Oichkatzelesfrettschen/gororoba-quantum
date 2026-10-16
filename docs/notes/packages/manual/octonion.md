# octonion(3) -- batched PyTorch octonions on a Fano-plane basis

## NAME

`octonion` 0.1.0 (PyPI `octonion`, Arch `python-octonion`): octonion arithmetic on
`[..., 8]` torch tensors through an `[8, 8, 8]` structure-constant tensor, with exp, log,
associator, multiplication matrices, a real-complex-quaternion tower, autograd-aware
calculus (`octonion.calculus`) and neural-network baselines. Release binding and measured
relation: [../octonion.md](../octonion.md).

## SYNOPSIS

```python
import torch
import octonion as oc

a = oc.random_octonion(batch_size=1024, device="cuda")          # float64 by default
b = oc.Octonion(torch.randn(1024, 8, dtype=torch.float64, device="cuda"))
c = a * b                                                       # einsum over STRUCTURE_CONSTANTS
oc.octonion_mul(a.components, b.components)                     # the same on raw tensors
oc.associator(a, b, c), oc.octonion_exp(a), oc.octonion_log(a), oc.left_mul_matrix(a)
```

## DESCRIPTION

`STRUCTURE_CONSTANTS[i, j, k]` is the coefficient of `e_k` in `e_i e_j`, built from the
seven oriented Fano triples `(1,2,4), (2,3,5), (3,4,6), (4,5,7), (5,6,1), (6,7,2), (7,1,3)`
(Baez's mod-7 labeling); `octonion_mul` contracts it with `torch.einsum` after promoting both
operands to a common dtype. `cayley_dickson_mul` is a cross-check that permutes into a
Cayley-Dickson basis, applies Baez's doubling `(a, b)(c, d) = (ac - d conj(b), conj(a) d + c b)`
on quaternion halves (`_raw_cayley_dickson_mul`), and permutes back. `Real`, `Complex` and
`Quaternion` are the lower tower levels.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Octonion(data)`, `UnitOctonion(data)`, `PureOctonion(data)`, `Octonion.from_quaternion_pair(q1, q2)`, `random_octonion`, `random_unit_octonion`, `random_pure_octonion` (`batch_size`, `dtype=torch.float64`, `device`, `generator`) | last axis of length 8 |
| products | `*` on `Octonion`, `octonion_mul(a, b)`, `cayley_dickson_mul(x, y)` | broadcasting batch axes |
| conjugate, norm, inverse | `conjugate()`, `norm()`, `norm_squared()`, `inverse()`, `real`, `imag`, `to_quaternion_pair()` | |
| exp, log | `octonion_exp(o)`, `octonion_log(o)` | series below a dtype-dependent threshold |
| associator, commutator, products | `associator(a, b, c)`, `commutator(a, b)`, `inner_product(a, b)`, `cross_product(a, b)` | |
| matrix representations | `left_mul_matrix(a)`, `right_mul_matrix(b)` | `[..., 8, 8]` |
| structure data | `STRUCTURE_CONSTANTS`, `FANO_PLANE` (`triples`, `lines`, `incidence_matrix`, `quaternionic_subalgebra`, `automorphism_generators`), `FanoPlane` | |
| tower | `Real`, `Complex`, `Quaternion`, `NormedDivisionAlgebra` | |
| calculus | `octonion.calculus`: `ghr_derivative`, `jacobian_mul`, `octonion_gradcheck`, `numeric_jacobian`, autograd `Function`s for mul, exp, log, inverse, conjugate | |
| learning | `OctonionLinear(dtype=torch.float32)`, `octonion.baselines` (lazy), `octonion.trie` | |
| symbolic support | none | |
| dimension range | D = 1, 2, 4, 8 | |
| dtype, batching, GPU | any torch float dtype and device; constants cached per (device, dtype) | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import octonion as oc
print(oc.__all__)
for name in ("octonion_mul", "cayley_dickson_mul", "associator", "octonion_exp", "left_mul_matrix", "random_octonion"):
    print(name, inspect.signature(getattr(oc, name)))
print([m for m in dir(oc.Octonion) if not m.startswith("_")])
```

```text
['baselines', 'Octonion', 'UnitOctonion', 'PureOctonion', 'Real', 'Complex', 'Quaternion', 'NormedDivisionAlgebra', 'associator', 'octonion_mul', 'cayley_dickson_mul', 'octonion_exp', 'octonion_log', 'commutator', 'inner_product', 'cross_product', 'left_mul_matrix', 'right_mul_matrix', 'OctonionLinear', 'random_octonion', 'random_unit_octonion', 'random_pure_octonion', 'FANO_PLANE', 'FanoPlane', 'STRUCTURE_CONSTANTS']
octonion_mul (a: 'torch.Tensor', b: 'torch.Tensor') -> 'torch.Tensor'
cayley_dickson_mul (x: 'torch.Tensor', y: 'torch.Tensor') -> 'torch.Tensor'
associator (a: 'Octonion', b: 'Octonion', c: 'Octonion') -> 'Octonion'
octonion_exp (o: 'Octonion | torch.Tensor') -> 'Octonion | torch.Tensor'
left_mul_matrix (a: 'Octonion') -> 'torch.Tensor'
random_octonion (*, batch_size: 'int | None' = None, dtype: 'torch.dtype' = torch.float64, device: 'torch.device | None' = None, generator: 'torch.Generator | None' = None) -> 'Octonion'
['components', 'conjugate', 'dim', 'from_quaternion_pair', 'imag', 'inverse', 'norm', 'norm_squared', 'real', 'to_quaternion_pair']
```

2. Two signed relabelings onto `cd_core`: the Fano structure constants through
   `pi = (0, 1, 2, 4, 3, 6, 7, 5)` with a flip on its e6, and the raw Baez doubling with flips
   on e5, e6, e7; `cayley_dickson_mul` reproduces `octonion_mul`.

<!-- example -->
```python
import torch
import octonion as oc
from octonion import _cayley_dickson as raw
from cd_core import cd_sign
C = oc.STRUCTURE_CONSTANTS
def unit(k):
    return torch.eye(8, dtype=torch.float64)[k]
def check(product, pi, eta):
    bad = 0
    for p in range(8):
        for q in range(8):
            v = product(unit(p), unit(q))
            r = int(v.abs().argmax())
            sign = float(v[r]) * (-1) ** (eta[p] + eta[q] + eta[r])
            bad += pi[r] != pi[p] ^ pi[q] or sign != cd_sign(8, pi[p], pi[q])
    return bad
print("Fano", check(lambda x, y: torch.einsum("i,ijk,j->k", x, C, y), [0, 1, 2, 4, 3, 6, 7, 5], [0, 0, 0, 0, 0, 0, 1, 0]))
print("raw Baez", check(raw._raw_cayley_dickson_mul, list(range(8)), [0, 0, 0, 0, 0, 1, 1, 1]))
x, y = oc.random_octonion(batch_size=100).components, oc.random_octonion(batch_size=100).components
print("cayley_dickson_mul == octonion_mul:", torch.allclose(oc.cayley_dickson_mul(x, y), oc.octonion_mul(x, y)))
```

```text
Fano 0
raw Baez 0
cayley_dickson_mul == octonion_mul: True
```

3. Batched products on the GPU agree with the CPU; mixed float32 and float64 operands promote.

<!-- example -->
```python
import torch
import octonion as oc
g = torch.Generator().manual_seed(3)
a = oc.random_octonion(batch_size=4096, generator=g)
b = oc.random_octonion(batch_size=4096, generator=g)
print("cuda available:", torch.cuda.is_available())
gpu = oc.octonion_mul(a.components.cuda(), b.components.cuda())
print(gpu.device, gpu.dtype, tuple(gpu.shape), torch.allclose(gpu.cpu(), (a * b).components))
print(oc.octonion_mul(torch.ones(8), torch.ones(8, dtype=torch.float64)).dtype, torch.get_default_dtype())
```

```text
cuda available: True
cuda:0 torch.float64 (4096, 8) True
torch.float64 torch.float32
```

4. Associator, exp and log, inverse, multiplication matrices and the quaternion tower.

<!-- example -->
```python
import torch
import octonion as oc
e = torch.eye(8, dtype=torch.float64)
e1, e2, e3 = (oc.Octonion(e[k]) for k in (1, 2, 3))
print("A(e1, e2, e3) =", oc.associator(e1, e2, e3).components.tolist())
x = oc.Octonion(torch.tensor([0.2, 0.1, -0.3, 0.5, 0.0, 0.4, -0.1, 0.2], dtype=torch.float64))
print("exp(log x) == x:", torch.allclose(oc.octonion_exp(oc.octonion_log(x)).components, x.components))
print("x x^-1 == 1:", torch.allclose((x * x.inverse()).components, e[0]))
print("L_x y == x y:", torch.allclose(oc.left_mul_matrix(x) @ e3.components, (x * e3).components))
q = oc.Quaternion(torch.tensor([0.0, 1.0, 0.0, 0.0])) * oc.Quaternion(torch.tensor([0.0, 0.0, 1.0, 0.0]))
print("tower i j =", q.components.tolist())
```

```text
A(e1, e2, e3) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -2.0, 0.0]
exp(log x) == x: True
x x^-1 == 1: True
L_x y == x y: True
tower i j = [0.0, 0.0, 0.0, 1.0]
```

## MAPPING TO cd_core

Signed relabeling, never identity: `T(e_p) = (-1)^eta(p) e_pi(p)` with
`pi = (0, 1, 2, 4, 3, 6, 7, 5)` and `eta` nonzero only at this package's e6 carries every
Fano product onto `cd_core` (64 pairs, EXAMPLES 2); 1344 such maps exist, the
signed-permutation automorphisms. The raw Baez doubling `_raw_cayley_dickson_mul` keeps the
index order and differs from `cd_core` by sign flips on e5, e6 and e7 (EXAMPLES 2;
[checks](checks/interplay_tables.json)). `Complex` and `Quaternion` of the tower are identical
to `cd_core` at D = 2 and 4.

## TRAPS

- Index `i` is not `cd_core` `e_i`: map through `pi` and `eta` before comparing a
  coefficient, associator or Fano line.
- Baez's doubling differs from the `cd_core` doubling; a port of either formula into the
  other basis changes signs on e5, e6, e7.
- The package owns the top-level module name `octonion`, shadowing
  [Cayley-Calculator](cayley-calculator.md)'s `octonion.py` and breaking
  [Octonion-Sedenion](octonion-sedenion.md)'s `from octonion import Octonion`.
- The random constructors and `STRUCTURE_CONSTANTS` are float64 while torch defaults to float32
  (`OctonionLinear` defaults to float32);
  `octonion_mul` promotes a mixed pair to float64 (EXAMPLES 3).
- `import octonion.baselines` pulls in the plotting and training stack.

## LICENSE

AGPL-3.0-or-later (dist-info `License-Expression`); terms attach to code that incorporates it.

## SEE ALSO

[sagemath](sagemath.md) (the other octonion basis that differs from `cd_core`), [interplay](../interplay.md).
