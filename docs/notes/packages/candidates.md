# Candidate packages beyond the qualified set

The seventeen packages in [README.md](README.md) cover the Cayley-Dickson
(CD) tower and its small Clifford neighbors. This table ranks the further
Python packages, library builtins and GitHub projects that touch algebras
adjacent to that tower. Every entry names its relation to
`gororoba_quantum/cd_core.py` and the binding rule of the algebra section in
AGENTS.md: a result enters evidence through a declared map onto `cd_core`,
checked on every basis pair. [adjacent-algebras.md](adjacent-algebras.md)
holds the mathematical decomposition behind the relations.

Metadata comes from the PyPI JSON API, the GitHub REST API, `pacman -Si`/`-Qi`
and the AUR RPC (info and search, by name), retrieved 2026-10-16. Source
conventions were read from unpacked sdists and GitHub archives; no downloaded
code was imported or run. Build-host facts: Python 3.14, libflint 3.6.0,
sagemath 10.10, gmpy2 2.3.2, mpmath 1.4.1, sympy 1.14.0 and galois 0.4.11
installed.

## Ranked table

| # | Package (source, version) | Algebra | Relation to cd_core | License | Arch / AUR / PKGBUILD | Kaggle pip | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | python-flint 0.9.0 (PyPI, 2026-07-03) | exact Z, Q, Z/n, GF(q) integer and rational matrices, polynomials, arb/acb balls | backend: exact `fmpq_mat` rank, nullspace and determinant of `cd_core.left_mult_matrix`, derivation spaces and Albert-algebra tables, in place of the float `_determinant` | MIT AND LGPL-3.0-or-later | Arch: none. AUR: none. System `flint 3.6.0` is installed and 0.9.0 builds against FLINT 3.0 to 3.6, so a PKGBUILD from the sdist is needed (makedepends meson-python, cython) | yes: cp313 and cp314 manylinux x86_64 wheels | **install** |
| 2 | hyprat, GitHub alreich/hyper_rationals tag v0.2.0 (not on PyPI; pure Python, no dependencies, Python >= 3.9) | exact rational CD tower with a per-level parameter mu, split and generalized (mu != -1) algebras, Hurwitz quaternions | doubling `(a,b)(c,d) = (ac + mu conj(d) b, da + b conj(c))` equals the cd_core doubling at mu = -1 with the same conjugation; labels follow doubling-level bits (`Hy.unit_square` reads the index in binary). Expected: identical table at D = 8, 16 (unmeasured). mu = +1 reproduces the split variants; other rational mu give quaternion algebras (-1, 2) and the like | MIT | Arch: none. AUR: none. PKGBUILD from the GitHub tag archive (pattern of python-cayley-dickson) | yes: pinned archive through `--fetch` and `--install` | **install**, with a bundle row mirroring hypercomplex's rational check; the project is alpha, one author, tag four days old at retrieval, so pin the archive sha256 |
| 3 | SageMath 10.10 builtins (installed) | `ExceptionalJordanAlgebra` (Albert algebra) over `OctonionAlgebra(R, a, b, c)`, `LieAlgebra(cartan_type=['F',4]` or `['G',2]` or `['E',6])`, `Qp`/`Zp`/`Qq`, quaternion algebras over any field, Clifford and exterior algebras | Albert algebra: built from Sage octonions, which are the opposite of cd_core with e3, e5, e6 sign flip an isomorphism ([sagemath.md](sagemath.md)). Expected map for H3: entrywise signed relabeling T, 27 coordinates, checkable on all 27 x 27 basis pairs (unmeasured). Qp: base change of integer tables, no new table | GPL-2.0-or-later | installed; no action | no (SageMath stays on the build host) | **use, no install**: add a retained Sage export for the 27-dimensional Jordan table beside `sagemath_octonion_table.json` |
| 4 | pyadic 0.3.0 (PyPI, 2026-03-05; GitHub GDeLaurentis/pyadic, not archived) | p-adic numbers and finite fields (`PAdic`, `ModP`, `FieldExtension`, Gaussian rationals); Fraction in, capped precision out | coefficient-field substitution: cd_core's integer sign tables pass unchanged to Q_p; the arithmetic of a CD level over `PAdic` needs a base-type hook such as hypercomplex's `base=` argument. Precision is a capped interval, so equality claims hold to stated precision only | GPL-3.0 (PyPI metadata, repository LICENSE) | Arch: none. AUR: none. PKGBUILD needed (noarch wheel, depends numpy, sympy) | yes: pure `py3-none-any` wheel | **optional install** only when a Q_p question is posed (octonion splitting over Q_p, 2-adic Hurwitz structure); it adds no CD table |
| 5 | python-hypercomplex 0.3.4 `base=` hook (installed) with galois 0.4.11 (installed, AUR python-galois) | CD over GF(p), p odd | coefficient substitution; the doubling needs char != 2 (conjugation and `-1` collapse in char 2). Installed but absent from the AGENTS.md package table | MIT | AUR: python-galois 0.4.11-1 (unrecorded here) | yes: pure wheel; needs numba | **record**, no new install |
| 6 | padic 0.2.4 (PyPI, 2023-08-04; MRaczuk/padic, MIT) | p-adic intervals `a p^v + O(p^N)`, Hensel roots, log/exp/sin/cos | coefficient field only; numpy `Polynomial` for roots | MIT | none; none; PKGBUILD needed | yes: `py3-none-any` | **skip**: pyadic covers Fraction input and finite-field work; single-author, 2023 |
| 7 | numga 2.0.0a0 (GitHub EelcoHoogendoorn/numga, not archived, pushed daily; not on PyPI) | geometric algebra Cl(p,q,r) including degenerate metrics, NumPy, JAX, PyTorch | Cl(0,2) = D = 4 table (as clifford, kingdon, galgebra); degenerate r > 0 gives exterior and dual-number factors that no installed package builds | MIT | none; none; PKGBUILD needed | pure Python, installable from an archive | **skip**: three Clifford packages already qualified; revisit if a degenerate metric is needed |
| 8 | geoalg (GitHub GPWilmot/geoalg, no release or tag) | calculators for quaternions, octonions, sedenions and split "ultronions"; Clifford algebra | `O.CayleyDicksonRule` offers the "wiki" rule `(a,b)(c,d) = (ac - conj(d) b, da + b conj(c))`, equal to cd_core, and a Baez rule; the "wiki" rule is the default. Command-line scripts, not an importable library | GPL-3.0 | none | no PyPI name | **skip**: reading and cross-checking only, like cayley-dickson |
| 9 | dual-quaternions 0.4.0 (PyPI, 2025-07-06) | dual quaternions (H tensor R[eps]/eps^2) for rigid motions | the quaternion factor is pyquaternion (identical to D = 4 cd_core); the dual part is a coefficient ring with a degenerate mu = 0, outside the CD tower of gamma = -1 | MIT | none; none | yes: pure wheel (numpy, pyquaternion) | **skip**: no table beyond D = 4 |
| 10 | dual-numbers 0.0.11 (PyPI, 2024-08-06) | R[eps]/eps^2 | degenerate mu = 0 level; patches built-in types through forbiddenfruit and custom-literals | MIT (classifier only) | none | yes | **skip**: runtime monkey-patching of built-ins |
| 11 | torch-ga 0.0.6, tfga 0.2.0, jaxga 0.0.2 (PyPI) | tensor-framework geometric algebra | Cl(p,q) only; tfga requires Python < 3.12 and TensorFlow, jaxga dates from 2021, torch-ga needs PyTorch | MIT | none | torch-ga yes; tfga no | **skip**: no CD content, heavy dependencies |
| 12 | multicomplex 0.13.0 (PyPI, 2021) | multicomplex numbers C++ extension | tower C tensor C tensor ...; wheels only for cp36 to cp39 | not stated | none | no: no cp313 wheel | **skip** |
| 13 | hyperdual 0.8.1 (PyPI, 2018, sdist only), quaternion-algebra 1.0.1 (2012) | hyper-dual numbers; quaternions | none beyond D = 4 | none stated / GPL | none | sdist only | **skip**: abandoned |
| 14 | surreal-number packages: PyPI `surreal` 0.2.1 is an unrelated reinforcement-learning stack; GitHub toys (codeinthehole/python-surreal, babou, mattiucci surreal_numbers) | Conway surreal numbers | isolated; shares only the dyadic rationals | mixed | none | no | **skip** |
| 15 | PyPI `hyperreal` 0.6.1 | a text-indexing search tool, not hyperreal arithmetic | none | Apache-2.0 | none | n/a | **skip**: name trap |
| 16 | sympy 1.14.0, mpmath 1.4.1, gmpy2 2.3.2 (installed) | `sympy.algebras.Quaternion` (no octonions), exact rationals, multiprecision | sympy: D = 4 only and no p-adic module (grep of the installed tree finds none); gmpy2 mpq: fast exact rationals for sampled products at D >= 32 | BSD, BSD-3-Clause, LGPL-3.0-or-later | installed | yes | **no action** |

No Python package exists for Freudenthal triple systems, standalone Jordan
algebras or Albert algebras: the PyPI names jordan-algebra, albert-algebra,
freudenthal, padics, padicpy, bicomplex, sedenion, sedenions, splitcomplex,
tessarine and grassmann do not exist, and `jordan` 0.0.1 (2017) is an unrelated
stub. GitHub repository searches for "albert algebra jordan" return only
unrelated research dumps. The Albert algebra therefore comes from Sage or from
a native builder over `cd_core` octonions (see adjacent-algebras.md).

Other GitHub sedenion and Cayley-Dickson projects were screened: thoppe/Cayley-Dickson
(the qualified cayley-dickson lineage), discretegames/hypercomplex and
maher1719/hypercomplex-engine (qualified), HubertHolin/Cayley-Dickson,
peawormsworth/PyHyperComplex (AGPL-3.0), hamiltron/py-cayleydickson and
ericangle/cayleyDickson (2016, no release). None carries a tag newer than the
packages already recorded except hyprat.

## Install order

1. python-flint 0.9.0: an exact kernel replaces float determinants wherever a
   certificate quotes a rank, and it enables exact derivation spaces.
2. hyprat v0.2.0: an independent exact tower with the mu parameter; its split
   presets give a second implementation of the split-octonion variant that
   the table already holds for splitoct and hypercomplex-engine.
3. A retained Sage export of the Albert algebra, which needs no install.
4. pyadic 0.3.0, on demand.

## Falsifiers

- hyprat at mu = -1 differs from `cd_core` on any basis pair at D = 8 or 16,
  or its labels do not follow bitwise XOR: the "identical" relation fails and
  the package needs a signed relabeling or is skipped.
- The Sage Albert table fails to match the cd_core-native `H3` builder under
  entrywise `T` on any of the 27 x 27 basis pairs: the entrywise map is wrong
  and the isomorphism needs a different relabeling.
- python-flint 0.9.0 fails to build against the installed FLINT 3.6.0: the
  sdist route fails and the wheel stays Kaggle-only.
