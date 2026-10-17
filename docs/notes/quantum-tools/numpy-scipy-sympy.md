# numpy, scipy, sympy

## NAME

numpy 2.5.4, scipy 1.18.1, sympy 1.14.0 -- the numerical core pinned in
`requirements.txt`.

## SYNOPSIS

```python
import numpy as np, scipy, sympy
from scipy import stats
rng = np.random.default_rng(7)
```

| Substrate | Status |
| --- | --- |
| Build host | python-numpy 2.5.4, python-scipy 1.18.1, python-sympy 1.14.0 (Arch) |
| Kaggle | the image's versions: numpy 2.1.3 and scipy 1.16.3 in the recorded probes (`docs/notes/kaggle/substrates.md`), sympy 1.14.0 and pandas 2.3.3. The runner freezes numpy and scipy while pips install, and `environment.json` records each run |

## CAPABILITIES IN THIS REPOSITORY

- numpy: state vectors, density matrices and operator matrices; seeded
  `default_rng` for replicates (`cd_core.py` itself works on plain lists).
- scipy: replicate statistics (`scipy.stats`: `binomtest`, confidence
  intervals) per `requirements.txt`; `scipy.linalg.expm` for small unitaries.
- sympy: exact polynomial rank, kernel-chart and attachment certificates
  (`requirements.txt`: "Exact polynomial rank, kernel-chart, and attachment
  certificates"); exact rationals where float64 is not a proof.
- Version skew: CI and the host pin numpy 2.5.4 and scipy 1.18.1, while a
  Kaggle kernel keeps the image's numpy and scipy, so a cross-substrate
  comparison states a tolerance.

## API ENTRY POINTS

The three libraries are used through a few entry points; their full
namespaces (hundreds of names each) are in their own documentation.

- numpy: `numpy.linalg` (`eigvals`, `det`, `matrix_rank`, `norm`),
  `numpy.random.default_rng`, `numpy.kron`, `numpy.einsum`.
- scipy: `scipy.stats` (`binomtest`, `proportion_ci`), `scipy.linalg.expm`,
  `scipy.optimize` (least squares, behind lmfit).
- sympy: `sympy.Matrix` (`rank`, `nullspace`, `det`, `rref`), `sympy.Rational`,
  `sympy.Poly`.

`numpy.linalg` by introspection:

`numpy.linalg` public names (33), by introspection:

functions:

```text
  cholesky, cond, cross, det, diagonal, eig, eigh, eigvals, eigvalsh, inv,
  lstsq, matmul, matrix_norm, matrix_power, matrix_rank, matrix_transpose,
  multi_dot, norm, outer, pinv, qr, slogdet, solve, svd, svdvals, tensordot,
  tensorinv, tensorsolve, test, trace, vecdot, vector_norm
```

## EXAMPLES

```python
import numpy as np, scipy, sympy
from scipy import stats

print("numpy", np.__version__, "| scipy", scipy.__version__, "| sympy", sympy.__version__)
rng = np.random.default_rng(7)
x = rng.binomial(1000, 0.5, size=20)
res = stats.binomtest(int(x.sum()), 20000, 0.5)
lo, hi = res.proportion_ci(method="wilson")
print("binomtest p =", round(res.pvalue, 6), " Wilson 95%% CI = [%.4f, %.4f]" % (lo, hi))

# exact rank and nullspace of an integer matrix over Q (sympy), the repo's rank-certificate tool
m = sympy.Matrix([[1, 2, 3], [2, 4, 6], [1, 0, 1]])
print("rank over Q:", m.rank(), " nullspace:", [list(v) for v in m.nullspace()])
seq = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print("determinant of 1..9: sympy", sympy.Matrix(seq).det(), "| numpy %.3e" % np.linalg.det(np.array(seq)))
print("complex128 eigenvalues of an X rotation:", np.round(np.linalg.eigvals(scipy.linalg.expm(-0.5j * np.pi / 2 * np.array([[0, 1], [1, 0]]))), 6))
```

Output:

```text
numpy 2.5.4 | scipy 1.18.1 | sympy 1.14.0
binomtest p = 0.938002  Wilson 95% CI = [0.4934, 0.5072]
rank over Q: 2  nullspace: [[-1, -1, 1]]
determinant of 1..9: sympy 0 | numpy 6.661e-16
complex128 eigenvalues of an X rotation: [0.707107+0.707107j 0.707107-0.707107j]
```

## INTEROP WITH QISKIT

Qiskit 2.5.2 requires `numpy>=2.0,<3` and `scipy>=1.14` (host package
metadata), so the Kaggle image's numpy 2.1.3 and scipy 1.16.3 satisfy it.
`Operator(...).data` and `Statevector(...).data` are NumPy arrays; the
other manuals compare against them.

## CPU AND GPU

numpy, scipy and sympy run on the CPU. GPU array work uses torch or cupy
([gpu-arrays.md](gpu-arrays.md)).

## TRAPS

- The determinant of the matrix 1..9 is exactly `0` in sympy and a nonzero
  float in numpy (printed in the example); a rank, kernel or singularity claim
  is a sympy statement, not a float one.
- `scipy.stats.binomtest` returns an exact two-sided p-value, and
  `proportion_ci(method="wilson")` the Wilson interval; the example
  uses a seeded draw so its digits replay.
- A `%` inside a printf-style format string needs `%%` (the example's 95%% CI).

## LICENSE

numpy: BSD-3-Clause with bundled component licenses; scipy: BSD-3-Clause;
sympy: BSD.
