# The W8 and Q(i) quadric ideals in a second computer-algebra system

[quadric-ideals-macaulay2-p32009](../quadric-ideals-macaulay2-p32009/README.md) (ledger row A5-599) recomputes five
retained quadric ideals modulo 32009 in Macaulay2 and names two gaps: the W8 quadric ideal and the Q(i) statements.
This directory closes both. Macaulay2 1.25.11 recomputes the invariants of the W8 -> N- quadric ideal modulo 32009 and
of the six quadric ideals over Q(i) that the weight-slice producer of A5-421 computes (W8, E8-bar and Iso, each at the
N+ and the N- basepoint). Macaulay2's standard bases, `minimalPrimes` and Shimoyama-Yokoyama primary decomposition
share no code with Singular's `std`, `minAssGTZ` and `primdecGTZ`, which produced every earlier number.

## Result

| Ideal | Field | Generators, dimension, degree | Reduced Hilbert numerator | Minimal primes (dim, degree, linear forms) | Primary components (dim, degree; radical dim, degree) | Radical |
|---|---|---|---|---|---|---|
| W8 -> N- (`w8_a2/w8_k2.rel`) | F_32009, i = 10754 | 144, 6, 50 | 1 + 18 T + 27 T^2 + 4 T^3 | (6, 20, 9), (6, 30, 4) | (6, 20; 6, 20), (6, 30; 6, 30) | yes |
| W8, two basepoints (`qi-g24-*`) | Q(i) | 144, 6, 50 | 1 + 18 T + 27 T^2 + 4 T^3 | (6, 20, 9), (6, 30, 4) | (6, 20; 6, 20), (6, 30; 6, 30) | yes |
| E8-bar, two basepoints (`qi-g21-*`) | Q(i) | 148, 5, 11 | 1 + 16 T - 12 T^2 + 10 T^3 - 5 T^4 + T^5 | (4, 4, 14), (5, 11, 9) | (4, 4; 4, 2), (4, 4; 4, 4), (5, 11; 5, 11) | no |
| Iso, two basepoints (`qi-g17-*`) | Q(i) | 68, 5, 23 | 1 + 12 T + 10 T^2 | (5, 23, 0) | (5, 23; 5, 23) | yes, prime |

- The modular W8 numbers are those of the census (`quadric-census/w8.log`: 144 generators, dimension 6, multiplicity
  50, numerator 1, 18, 27, 4; `w8-component-linear-forms.log`: 9 linear forms in the degree-20 prime P, 4 in K2 : P)
  and of A5-012 (K2 radical with components of degree 20 and 30).
- Over Q(i) the W8 and E8-bar numbers are those A5-421 states (dimension 6, multiplicity 50, minimal primes of degrees
  20 and 30; dimension 5, multiplicity 11, minimal primes of dimension 5, degree 11 and dimension 4, degree 4; the
  Hilbert numerators of the modular K2), and the Iso numbers are those of A5-446 (prime of dimension 5 and degree 23).
  The E8-bar primary structure over Q(i) equals the modular one of A5-599 (three components, nonreduced along the
  degree-4 component).
- In every case the intersection of the primary components equals the ideal.
- Controls: each ideal with the square of its first variable added changes dimension or degree (recorded in the
  `control` lines), and the driver requires the first Iso ideal with its last relation removed to report 67
  generators.

## Method over Q(i)

Macaulay2 computes Hilbert series over the number field `toField(QQ[jj]/(jj^2+1))` but has no minimal-prime or
primary-decomposition strategy there (`no applicable strategy for (minimalPrimes,Ideal)`). Since
QQ[jj, y]/(jj^2 + 1) is isomorphic to Q(i)[y], `qi_invariants.m2` decomposes K + (jj^2 + 1) in QQ[jj, y] and maps each
prime, component and radical to Q(i)[y], where it reads dimension, degree and linear forms.

## Scope

- One prime for the modular W8 ideal, 32009 with the root 10754 built into the retained file.
- The Q(i) ideals are those the producer of A5-421 writes at its own commit; `qi_quadric_ideals.py` records them by
  wrapping its `hilbert_script`, and the file name carries the first 12 hex digits of the sha256 of the polynomial
  lines. The producer does not label which file belongs to N+ and which to N-; the two files of each source agree on
  every invariant.
- The relation computations that produce the ideals are Singular's (4.4.1); this directory tests the invariants of the
  ideals, not their derivation.

## Replay

    PATH=DIR_WITH_M2:$PATH sh docs/evidence/a5-exceptional-fibers/working/runs/quadric-ideals-macaulay2-w8-qi/run_m2_qi.sh

from the repository root. A run rewrites the retained logs, `results.txt` and `m2-version.txt` of this directory, so a replay that should leave the record intact runs on a copy of the tree. The argument `dump` first rewrites the Q(i) ideal files with `qi_quadric_ideals.py`
(Singular, sympy and python-flint in `$PYTHON`) and requires byte-equal files. The retained run (`run_m2_qi.sh dump`) took 14 min 29 s at 1.1 GB peak on
an x86_64 WSL host (Ubuntu 26.04) with Macaulay2 1.25.11 from the Ubuntu package `macaulay2` unpacked in a user
directory: the modular W8 ideal 10 min 27 s at 1.1 GB, the Q(i) W8 ideals 1 min 50 s each, the others under 22 s,
each below 0.36 GB; the dump 1 min 49 s at 0.15 GB with Singular 4.4.1, Python 3.14.9, sympy 1.14.0 and python-flint
0.9.0.

| File | Content |
|---|---|
| `qi_quadric_ideals.py` | writes the Q(i) quadric ideals of the weight-slice producer as `qi-gG-DIGEST.txt` |
| `qi-g17-*.txt`, `qi-g21-*.txt`, `qi-g24-*.txt` | the Iso, E8-bar and W8 ideals over Q(i), one polynomial per line |
| `qi_invariants.m2` | the invariants of one Q(i) ideal |
| `run_m2_qi.sh` | the seven runs, the comparison and the removed-relation check |
| `qi_m2_runner.py` | dispatches the seven Macaulay2 runs through `parallel.py` |
| `NAME.log` | the output for one ideal (`W8-nm-p32009.log` runs `../quadric-ideals-macaulay2-p32009/quadric_invariants.m2`) |
| `results.txt`, `expected-results.txt` | the RESULT lines of the run and the expected ones |
| `m2-version.txt` | `M2 --version` |
| `timings.tsv` | wall time, peak resident set and exit status of each Macaulay2 run and of the dump driver (`/usr/bin/time -v`) |
| `calibration-p32009-run_m2.log` | `run_m2.sh` of `../quadric-ideals-macaulay2-p32009` on the same x86_64 host before this run: PASS, 63 s, 0.34 GB (`/usr/bin/time -v` output) |
| `sha256.txt` | sha256 of every other file of this directory |
