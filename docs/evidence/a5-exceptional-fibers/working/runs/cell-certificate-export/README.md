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

## Quotient-mode cell: A5-111

One quotient-mode cell, exported by `replay/engine/fiber_cell_certificate_quotient_v1.py` as the same schema with
`cell_mode: "quotient"`. It is a successor file: the raw-mode exporter and the A5-108 file keep their bytes, because
the A5-108 file records the exporter's digest. Row A5-111 (E8-bar -> VB, p = 32029, d = 4, h_4 = 155) cites the
engine record `d4-p2/e8vb_d4_n13_p32029.json` (quotient mode, N = 13, dim k[t]/(J + m^13) = 3627, blocks 56/35/32/32).
It is the smallest cell among the ledger rows that cite a quotient-mode engine record; the records of
`xm-lown/` are smaller but belong to the trend row A5-244, which is not a Hilbert-cell row.

Construction (recorded in the file as `module.construction`). The engine pipeline runs unchanged: Singular computes a
dp standard basis of J + m^N, its multiplication tables and the reduced generators, the products come from the tables,
and W is the closure of m P_d under the variables, per character block. The dp normal form of t_k b can lower the
degree, so the level test of the checker fails on the standard monomials. The exporter rebases Q' = Q/W on the m-adic
flag F_0 = Q', F_(j+1) = sum_k M_k F_j. Level j holds the first dim F_j - dim F_(j+1) monomials t_k alpha, alpha of
level j - 1, whose classes M^alpha e are independent modulo F_(j+1). The span of the levels from j upward is F_j and
t_k b for b of level j lies in F_(j+1), so every nonzero M_k[b', b] has lev(b') > lev(b); the exporter asserts this
before it writes. The basis lists the monomials, lev is their degree, e is the first basis vector, and M_k is the
engine matrix conjugated by the matrix T of the classes M^alpha e. The flag has dimensions 1782, 1781, 1774, 1755,
1716, 1647, 1536, 1369, 1130, 900, 679, 454, 228 for j = 0 to 12. `J_in_W` is the explicit evaluation J(M) e = 0 on
the emitted module.

Gate against the record. The exporter stops before writing unless dim_quotient, every block's `cols` and `rank_W`,
and r_N equal the engine record; all four agree (3627; 918/917/896/896 columns with ranks 462/469/457/457; r = 155).

Run (one unit, measured, twice, with identical output apart from the timing fields):

- Platform: an aarch64 host, 4 cores, python-flint 0.9.0, numpy 2.5.4, Singular 4.4.1, Python 3 venv.
- Command: `python -I fiber_cell_certificate_quotient_v1.py HEADER 4 13 OUT --ledger-id A5-111 --fiber "E8-bar -> VB"
  --h-claimed 155 --header-path PATH --record d4-p2/e8vb_d4_n13_p32029.json`
- Exporter wall time 309 s (Singular 159 s), peak resident set 1,727,684 kB (`/usr/bin/time -v`), exit 0.
- Checker: 7.5 s, peak resident set 44,156 kB, exit 0.
- File: `a5-111-cell-certificate.json`, 1,297,310 bytes, sha256
  `ccbf15218b63059d8bd55bf9dabfdbbdbaabd4d960df01ce6c3ef6c228d21705`.
- Cell: n = 8, N = 13, q = 1782, r = 155 of 715 products, 44,177 nonzero entries over the eight M_k (1907, 8419, 2183,
  6366, 3113, 11398, 2011, 8780).

Checker: the twelve checks of the A5-108 run all pass, with the record comparison reading dim_quotient in place of dim_V
for a quotient record, and the class of each product memoized on its prefix. `calibrate_cell_certificate_v1.py`
applies the five corruptions (one M entry, one level, one left-inverse entry in its support, one J coefficient, a
duplicated selected product) and requires the checker to reject each; it accepts both the A5-108 file and the A5-111
file and rejects all ten corrupted copies. The A5-108 file still hashes to its recorded digest, and a regeneration with
the unchanged raw exporter equals it except for `producer.seconds`.

## Retained files

`sha256.txt` lists the digests of the exporters, the checker, the calibration script, the certificates and this file.
