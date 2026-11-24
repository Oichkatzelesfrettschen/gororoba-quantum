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

## K2 cofactor certificate: E8-bar -> VB at 32029

The upper bound of every d >= 2 Hilbert cell rests on K2, the ideal of the 21 quadrics q in y_1..y_10 with q(G) in
J + m P_2 (P_2 spanned by the products G_a G_b, m = (t_1..t_8)), and on the Hilbert function of k[y]/K2. Row A5-428
and the K2 table (`k2-hilbert.jsonl`) retain the quadrics and the counts but no cofactors. The file below carries the
identity of each quadric, a reduced Groebner basis of K2, and the Hilbert function, in schema
`a5-k2-cofactor-certificate-v1`.

Mechanism. `replay/engine/k2_cofactor_certificate_v1.py` reads the canonical header
`working/build/inputs/p32029-r9115/e8-vb.sing` (J: 17 generators, G: 10 generators) and the 21 quadrics of
`working/distribute/out/a5-p2-small/vb_p2/d2/relations-d2.rel` (the file behind the 32029 row of `k2-hilbert.jsonl`).
Singular 4.4.1 solves, in the global ordering dp, the membership of q(G) in the ideal generated by J and the 440
products t_i G_a G_b (i = 1..8, a <= b) with `lift`, one pass for all 21 quadrics. A second Singular process computes
the reduced standard basis of K2 in dp and the expression of each basis element in the 21 quadrics.

Identity certified: u * q(G) = sum_k a_k J_k + sum b_{i,ab} t_i G_a G_b, exact in F_32029[t_1..t_8], with u = 1 for all 21
quadrics. The identity is global, so it holds in the local ring at the origin with the unit u = 1 and no truncation
(N is null in the file). Four quadrics need no b term (q(G) lies in J).

Groebner basis: 25 elements of degrees 2 (from the quadrics) and 3, monic, reduced, order dp (Singular degree reverse
lexicographic, y_1 > ... > y_10). Hilbert function h_d of k[y]/K2 for d = 1..8: 10, 34, 80, 155, 266, 420, 624, 885;
d = 1..7 equal the retained 32029 row of `k2-hilbert.jsonl` (the 32009 row has the same counts), and d = 8 is new. First
Hilbert numerator 1, 0, -21, 70, -105, 84, -35, 6, equal to the numerator of row A5-428.

Run (one unit, measured; two full runs give the same content apart from the `producer` block):

- Platform: an aarch64 host, 4 cores, Singular 4.4.1, Python 3.14.4, GNU time.
- Command: `python3 k2_cofactor_certificate_v1.py HEADER K2.rel OUT --header-path PATH --rel-path PATH --work DIR`;
  Singular runs under `ulimit -v 16000000` and `timeout 7200`.
- Whole producer: 96.3 s wall, 864,020 kB peak resident set (`/usr/bin/time -v`), exit 0.
- Lift step: 76.6 s wall, 864,020 kB peak. Groebner step: 0.016 s wall, 11,540 kB peak.
- File: 39,644,470 bytes, sha256 `2d330081a19eb2e21dcc615185ace7b4f9e946597d6acde591786be2c5324c6f`. The file stays out of the
  repository because of its size; the command above regenerates it in under two minutes.
- Cofactor terms: 1,542,487 in total over the 21 quadrics; the largest quadric (index 20, from 0) holds 288,935; the
  largest single a_k has 26,867 terms (the cofactor of one generator of J) and the largest b_{i,ab} has 950 terms.

Checker `replay/engine/check_k2_cofactor_certificate_v1.py` (standard library only, 45.2 s with 3 processes, 508,032 kB
peak, exit 0): re-parses the header and requires J and G, the prime and the header digest to match; expands each of the
21 identities (u(0) != 0, then u * q(G) minus the right side is the zero polynomial modulo 32029); requires every
Groebner element monic, homogeneous and reduced, every S-polynomial of a pair with non-coprime leading monomials to
reduce to 0 modulo the basis (so it is a Groebner basis of its ideal), every quadric to reduce to 0 modulo the basis
(K2 inside the ideal), and every element to equal the recorded combination of the quadrics (the ideal inside K2); then
recounts the standard monomials of degree 1..8 from the leading monomials, checks the numerator against them, and
compares d = 1..7 with `k2-hilbert.jsonl`. Result: ACCEPT, 21 identities, 7 retained degrees compared.

Calibration `replay/engine/calibrate_k2_cofactor_certificate_v1.py` (24.0 s, exit 0) accepts the clean file on the
identities of the two smallest quadrics (one with a_k terms only, one with b terms) and on the Groebner checks, and
rejects four corrupted copies: one coefficient of an a_k cofactor, one of a b cofactor (both fail the identity), the
constant term of the unit set to 0 (fails u(0) != 0), and one non-leading coefficient of a Groebner element (fails an
S-polynomial reduction).

## Retained files

`sha256.txt` lists the digests of the exporters, the checkers, the calibration scripts, the certificates and this file.
The K2 cofactor certificate itself (39,644,470 bytes, sha256 above) is regenerated by the command of its section.
