# The quadric ideal of E8-bar -> VB along the boost

G_2(C) x C^* reaches six of the seven directions of the VB orbit; the seventh is the boost u -> c u + s v,
v -> s u + c v with c^2 - s^2 = 1, which has no lift to the kernel bundle (A5-414). Ledger row A5-428 compares the
degree-2 relations of the fiber cone of E8-bar -> VB at the retained basepoint and three boosts of it. This directory
parametrizes the boost by c = (w^2 + 1) / (2 w), s = (w^2 - 1) / (2 w) (w = 1 is the retained point; w = 2, 3 and 2/3
are the three boosts of A5-428), computes the relations with the basepoint a function of w, and reads the quadric
ideal K(w) at twelve values of w modulo 32029 (ledger row A5-600).

## Method

`boost_family.py` rewrites the Singular script of `boost_e8_vb_quadrics.py` for the retained point: the basepoint
becomes the boosted point as an expression in w, the slice columns and the pivot of C(z_0) stay, and the 21
coordinates are computed in Singular as the upper-triangle entries of Pf(B) D + X^T adj_Pf(B) X for the principal
block B on the retained pivot. The Schur form of a principal block does not depend on the kernel frame, so at w = 1
these entries equal the retained coordinates polynomial by polynomial (`schur_matches_retained 1`). The germ of the
E8-bar closure, the Nakayama selection and the relations {q : q(G) in J + m I^2} follow as in the retained script.
The tail computes the invariants of K(w) and the adapted frame of A5-428: the scalars a, b, d are read from the
linear span of the component with four linear forms, and the substitution they define gives a reduced standard basis
(`NORMALFORM` lines).

## Result

| w | (c, s) | Generators, dimension, multiplicity | First Hilbert numerator | Minimal primes (dim, mult, linear forms) | Radical | Normal form |
|---|---|---|---|---|---|---|
| 1, 2, 3, 2/3, 5, 7, 11, -3, 1/4, 1000, 12345 | boosts over F_32029 | 21, 4, 7 | 1, 0, -21, 70, -105, 84, -35, 6 | (4, 3, 4), (4, 4, 3) | yes | one digest, `1bf1a88c2fad...` |
| 9115 (a root of -1) | (0, 9115) | the same | the same | the same | yes | the same digest |

- At every sampled value the frame is consistent and invertible, and the twelve normal forms are one ideal: the
  twelve quadric schemes are projectively equivalent over F_32029, by explicit changes of the 10 generators.
- Control: the reduced standard bases of K(w) before the frame (`KBASIS` lines) differ between sample points, so
  the frame, not the choice of generators, produces the agreement.
- 10 generators are selected at every value, and the germ has the retained component count.

## Scope

- One prime, 32029 with i = 9115; twelve values of w. The run over the function field F_32029(w) (`run_boost.sh generic`) had not finished the standard basis of J + m I^2 after 46 min, against 2 s at a point, when this record was written; it is no part of the result, so the statement holds at the sampled values and decides nothing about a general w.
- Degree 2 of the fiber cone. L = K2 in every degree is proved at the retained basepoint over Q(i) (A5-597) and is
  not recomputed along the boost; no limiting plane is compared.
- The four incidences of A5-419 (Iso, W8, X+, X- into VB) are not rerun here.

## Replay

    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-family-p32029/run_boost.sh

from the repository root, with Singular on PATH and sympy and python-flint in that interpreter; the argument
`generic` adds the function-field run, which is not retained. The driver exits nonzero unless every point shows the invariants above and
one normal form and the bases before the frame differ. The twelve points run through `parallel.py`; the retained sample run took about 1 min on four cores (11 s a point) with
Singular 4.4.1, Python 3.14.4, sympy 1.14.0 and python-flint 0.9.0 on an aarch64 Linux host.

| File | Content |
|---|---|
| `boost_family.py` | the script generator; `--run` dispatches the values through `parallel.py` |
| `run_boost.sh` | the sample points, the comparison and the function-field run (argument `generic`) |
| `bf-wTAG.sing`, `.log` | one value of w (`d` for `/`, `m` for `-`) |
| `normal-forms.txt` | per point: sha256 of the normal form and of the basis before the frame |
| `sha256.txt` | sha256 of every other file of this directory |
