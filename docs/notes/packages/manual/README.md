# Algebra package manual

One manpage per installed algebra package: the exact import and constructor lines, the
public API grouped by capability (construction, products, conjugate, norm and inverse,
exp and log, rotations, associator, matrix representations, symbolic support, dimension
range, dtype and batching), examples run on the build host with their exact output, the map
onto `gororoba_quantum/cd_core.py`, the traps the runs exposed, and the license. The
release bindings and the measured relations stay in the per-package notes one directory up;
the overlap map across packages is [../interplay.md](../interplay.md).

| Page | Module | Algebras reached | Map onto cd_core |
|---|---|---|---|
| [hypercomplex](hypercomplex.md) | `hypercomplex` | Cayley-Dickson D = 2 to 256 and beyond, any numeric base | identity |
| [hypercomplex-engine](hypercomplex-engine.md) | `hypercomplex_engine` | standard, split and dual basis signs, any D | identity; split reference |
| [hypercomplex-algebra](hypercomplex-algebra.md) | `hypercomplex_algebra` | expressions over the engine's kinds, tensor products | identity, through the engine |
| [cayley-calculator](cayley-calculator.md) | `Cayley_Calculator`, `sedenion`, `*_mod` | D = 2 to 128, gamma-twisted and all-split forms, special functions | identity; relabelings for split forms |
| [cayley-dickson](cayley-dickson.md) | `cayley_dickson` | nested pairs at any depth | identity |
| [octonion](octonion.md) | `octonion` (PyTorch) | D = 1, 2, 4, 8, batched, GPU | signed relabeling (Fano and Baez bases) |
| [splitoct](splitoct.md) | `SplitOct` | split octonions, symbolic | identity with the split reference |
| [mathdunders](mathdunders.md) | `mathdunders` | none (arithmetic plumbing) | none |
| [numpy-quaternion](numpy-quaternion.md) | `quaternion` | quaternion numpy dtype | identity |
| [quaternionic](quaternionic.md) | `quaternionic` | quaternion arrays, numba | identity |
| [pyquaternion](pyquaternion.md) | `pyquaternion` | scalar quaternions, rotations | identity |
| [clifford](clifford.md) | `clifford` | Cl(p, q, r), numba | identity or relabeling on Cl(0,1), Cl(1,0), Cl(0,0,1), Cl(0,2), Cl(1,1), Cl(2,0) |
| [kingdon](kingdon.md) | `kingdon` | Cl(p, q, r), numpy, SymPy, torch values | as clifford |
| [galgebra](galgebra.md) | `galgebra` | symbolic geometric algebra and calculus | as clifford, two or more generators |
| [pyoctonion](pyoctonion.md) | `pyoctonion` | octonions over pyquaternion | identity |
| [octonion-sedenion](octonion-sedenion.md) | `Octonion_Sedenion` | octonions and sedenions over numpy-quaternion | identity |
| [sagemath](sagemath.md) | `sage` (`sage -c`) | exact quaternion, octonion, Clifford and Albert algebras | opposite algebra; relabelings; Albert map |
| [hyprat](hyprat.md) | `hyprat` | exact rational Cayley-Dickson with mu per level, Hurwitz integers | identity; split reference |
| [python-flint](python-flint.md) | `flint` | exact backend, no table | exact rank and kernel of `L_x` |
| [pyadic](pyadic.md) | `pyadic` | GF(p) and p-adic backend, no table | coefficients for `cd_multiply` |

## Replaying the examples and checks

From the repository root on the build host, with `PYTHON=${PYTHON:-python3}`:

```sh
"$PYTHON" -B docs/notes/packages/manual/checks/run_examples.py --check
"$PYTHON" -B docs/notes/packages/manual/checks/algebra_interplay.py --check --verbose
"$PYTHON" -B docs/notes/packages/manual/checks/albert_algebra.py --check
```

`run_examples.py` imports the installed packages and runs only on a host that has them; it
runs each block as `$PYTHON -c` from the repository root with `PYTHONPATH=gororoba_quantum`
and warnings ignored, and reads site-packages paths as `site-packages/`. `--write` refreshes
the output blocks after a package rebuild. The two `--check` replays import `cd_core` alone
and run in CI (gates sources-247 and sources-249); their `--extract` modes re-read the
installed packages, Sage through one `sage -c` call, and rewrite the retained JSON.
