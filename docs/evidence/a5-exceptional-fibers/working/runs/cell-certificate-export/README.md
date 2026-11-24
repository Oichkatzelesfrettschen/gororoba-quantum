# Hilbert-cell certificate export: A5-108

One raw-mode cell of the A5 exceptional-fiber ledger, exported as an `a5-hilbert-cell-certificate-v1` file, with an
independent checker and a profile of the Gaussian arc-rank certificates.

## Mechanism and invariant

Row A5-108 (E8-bar -> VB, p = 32029, d = 1, h_1 = 10) is a raw-mode cell: its engine record
`degree-one/d1-e8-vb-32029.json` has no `mode` field, and `fiber_rank_v8.py` main() takes the raw branch unless
`--quotient` is given. `replay/engine/fiber_cell_certificate_v1.py` runs the unchanged v8 raw pipeline
(`Space`, `Echelon`, the closure of W under the variables) for header `working/build/inputs/p32029-r9115/e8-vb.sing`
at N = 5 and emits the quotient module Q = V/W: basis (q = 32 exponent vectors), the class e of 1, the level
(degree) of each basis vector, the eight sparse matrices M_k of multiplication by t_k, the 10 product classes, and a
left inverse. The checker `replay/engine/check_cell_certificate_v1.py` uses the standard library only and recomputes
every class as g(M) e from the tables.

Raw-mode W and J. The base generators of W are the term-truncated J (`Jsp`) and t_k times every product, and the closure
multiplies by every variable, so W contains the truncation of J as design section 1.2 defines it. The exporter confirms
it by reducing every term-truncated generator of J times every monomial of degree below N minus its lowest term degree
against the reduced echelon form of W (`J_in_W: true`, method recorded in the file).

## Run (one unit, measured)

- Platform: an aarch64 host, 4 cores, python-flint 0.9.0, numpy 2.5.4, Python 3 venv.
- Command: `python -I fiber_cell_certificate_v1.py HEADER 1 5 OUT --ledger-id A5-108 --fiber "E8-bar -> VB" --h-claimed 10`
- Wall time 0.44 s (exporter-reported 0.17 s after imports), peak resident set 68,292 kB (`/usr/bin/time -v`), exit 0.
- File: `a5-108-cell-certificate.json`, 13,014 bytes, sha256 `bd2755fe13df2465ac97852b0ad15fc99e8bc754f96b122adb450dac0ed97af5`.
- Cell: p = 32029, n = 8, N = 5, dim V = 495, q = 32, r = 10, 120 nonzero entries over the eight M_k.

## Checks (all PASS on the emitted file)

1. Level: lev(row) > lev(col) for every nonzero entry.
2. The 28 pairs M_j M_k commute modulo p on all 32 basis vectors.
3. J(M) e = 0 for the 17 generators of J, and t_k times each product class is 0.
4. The selected product classes (recomputed from the G tables) have rank 10, and left_inverse times them is the identity.
5. r = 10 equals the retained r_N of `degree-one/d1-e8-vb-32029.json` and h_claimed; q equals the sum of cols - rank_W per block (32).

Header sha256 and an independent parse of the header text equal the recorded digest and tables. Calibration: five
mutated copies (one M entry, one level, one left-inverse entry in its support, one J coefficient, a duplicated
selected product) each fail at least one check; a mutation of the zero-column entry 0 of the left inverse passes,
because the products have no constant term and so no class component on e.

Run the check: `python -I replay/engine/check_cell_certificate_v1.py CERT --header HEADER --record RECORD`
(paths below `docs/evidence/a5-exceptional-fibers`).

## Gaussian arc-rank certificate profile

`docs/evidence/a5-gaussian-certificates/left-inverses.json` (schema `gororoba.a5.gaussian-left-inverses/1`,
`arc_matrices`) holds eight certificates, all of family W8 (ids `w8-nm-*` and `w8-np-*`, ledger row A5-448). It holds no
E8-bar certificate. Closest profile, per certificate: rows x columns 24 x 6 for all eight, six selected rows; the field
`norm_of_d` is the norm re^2 + im^2 of the Gaussian-integer scalar d, written as a JSON number (a float64 for the large
ones, exact for the series points). Exact bit sizes of the norm: 104 and 103 bits for the linear points (d about 2^52
in the imaginary part), 24 and 35 bits for the series points (d = -3600 and -134784). Largest left-inverse entry 48
bits (linear) and 10 or 18 bits (series).

## Retained files

`sha256.txt` lists the digests of the exporter, the checker, the certificate and this file.
