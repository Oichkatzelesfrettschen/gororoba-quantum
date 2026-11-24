# The degree-3 relations of E8-bar -> VB along the boost

[e8-vb-boost-family-p32029](../e8-vb-boost-family-p32029/README.md) (ledger row A5-600) reads the degree-2 relations
of the fiber cone of E8-bar -> VB at twelve values of the boost parameter w modulo 32029. A5-428 counts the degree-3
relations at one boost, (c, s) = (5/4, 3/4), which is w = 2: 140 of the 220 cubic monomials in the 10 degree-1
generators, so h_3 = 80, the value of the quadric ring. This directory counts the degree-3 relations at all twelve
values of A5-600.

## Result

| w | targets | relations | h_3 |
|---|---|---|---|
| 1 | 220 | 140 | 80 |
| 2 | 220 | 140 | 80 |
| 3 | 220 | 140 | 80 |
| 2/3 | 220 | 140 | 80 |
| 5 | 220 | 140 | 80 |
| 7 | 220 | 140 | 80 |
| 11 | 220 | 140 | 80 |
| -3 | 220 | 140 | 80 |
| 1/4 | 220 | 140 | 80 |
| 1000 | 220 | 140 | 80 |
| 12345 | 220 | 140 | 80 |
| 9115 | 220 | 140 | 80 |

- Every value gives 140 relations, so h_3 = 80 at each, the degree-3 Hilbert value of the quadric ring of A5-600's
  ideal (first numerator 1, 0, -21, 70, -105, 84, -35, 6 in 10 variables).
- w = 9115 is a square root of -1 modulo 32029, where c = 0 and s = i: the boost is a pure rotation into the second block, the most special point of the list.
- Calibration: w = 2 reproduces the count of A5-428, which `boost_e8_vb_quadrics.py` computed by another script
  (`degree_three_row`).
- Since the degree-2 ideal K2(w) lies in the relation ideal, its degree-3 part (K2)_3, of dimension 140 by the Hilbert
  function above, lies in the degree-3 relation space, and A5-600 records the same Hilbert numerator at every listed value (its frames carry the twelve quadric ideals onto one); equal dimensions give L_3 = (K2)_3 at each listed value.

## Method

`boost_degree3.py` builds the script of `boost_family.py` with the relation stage of `boost_e8_vb_quadrics.py` at
degree 3 (`kbase(std(ideal(0)),3)`, 220 targets) and stops after the syzygies, printing the counts as
`degree_three_row` does. The products G^a are reduced modulo J + m I^3 by a standard basis of 1,777 generators
(994 elements), and the syzygies of the 220 normal forms over their 6,891 monomials are the relations.

## Scope

- One prime, 32029 with i = 9115; the twelve listed values of w. The function field F_32029(w) is not run (A5-600
  records that its degree-2 standard basis did not finish in 4 h), so nothing here decides a general w.
- Degree 3 only.

## Replay

    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-degree3-p32029/run_degree3.sh

from the repository root, with Singular on PATH and sympy and python-flint in that interpreter. A run without `check` rewrites the retained scripts and logs of this directory; the argument `check`
reads the retained logs after requiring each retained script to equal a fresh emission. One value takes 37 min on
one core at 0.32 GB alone (w = 2 and 3, run as a pair); the other ten, run at once on 16 cores with 32 threads, took
1 h 20 min 48 s to 1 h 22 min 15 s at 0.32 GB each, the syzygy stage dominant. Singular 4.4.1, Python 3.14.9, sympy 1.14.0, python-flint 0.9.0, x86_64
WSL Ubuntu 26.04.

| File | Content |
|---|---|
| `boost_degree3.py` | the script generator |
| `run_degree3.sh` | the runs, the count check and the altered-log check |
| `d3-wTAG.sing`, `.log` | one value of w (`d` for `/`, `m` for `-`) |
| `counts.txt` | value, targets, relations |
| `timings.tsv` | wall time, peak resident set and exit status of each Singular run (`/usr/bin/time -v`) |
| `sha256.txt` | sha256 of every other file of this directory |
