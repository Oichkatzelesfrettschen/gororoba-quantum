# Iso -> N-, degree 6, N = 19, p = 32009: h_6 = 2,422

The laptop unit `a5-v11-iso-d6` ([`run-iso-d6.sh`](run-iso-d6.sh), sha256 dc878792b706ef17...) ran engine v11
(`fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode on `isop1/iso-nm.sing` (header sha256
1f1757d55751f1e3...) without a degree-2 receipt, from 2026-11-08T18:17:17Z to 18:48:58Z ([`iso6.events`](iso6.events)).
Wall 1,900.6 s, peak RSS 20,525,380 KiB (19.6 GiB, [`isonm_d6_n19_p32009.time`](isonm_d6_n19_p32009.time)); Singular
14.5 s, products 312.1 s, closure 1,405.3 s in 6 rounds; the error stream is empty.

## Result

[`isonm_d6_n19_p32009.json`](isonm_d6_n19_p32009.json) (sha256 86dc118092744782...): r_19 = 2,422 with blocks
632 / 610 / 590 / 590, dim_quotient 59,983, 74,613 products over 17 generators.

The lower bound: the truncated rank r_N is at most h_6, the degree-6 Hilbert function of F(I). The upper bound: F(I) is
a quotient of k[y]/K2, so h_6 <= HF(k[y]/K2, 6) = 2,422 (A5-119). r_19 = 2,422 meets it, so h_6 = 2,422 over F_32009
and F(I)_6 = (k[y]/K2)_6: no degree-6 relation beyond K2 at this prime. The run used every product (raw mode), so the
bound rests on no membership receipt.

## Checks against the forecast

- N: the law that h_d is reached at N = 3d + 1 (`../forecasts/trends-2026-11-06.md`, item 8, ten cells for d = 1 to
  5) predicted N = 19; the rank reached the K2 count there, which extends the law to an eleventh cell. Reaching the
  count at N = 19 shows N = 19 suffices; whether N = 18 already reaches it is not measured.
- Blocks 2 and 3 are equal (590, 590), as in every Iso and W8 run.
- The last jump: N = 18 at p = 32009 reads r_18 = 2,253 with blocks 583 / 568 / 551 / 551
  ([`isonm_d6_n18_p32009.json`](isonm_d6_n18_p32009.json), sha256 5efb4230edfcec7f...), so r_19 - r_18 = 169 =
  (2 x 6 + 1)^2 with blocks 49 / 42 / 39 / 39, the values the trends file predicted before the run
  (`../forecasts/trends-2026-11-06.md`, line 246, and the closed form under the last-jump table). h_6 is reached at
  exactly N = 19, not before, which makes the N = 3d + 1 law exact in an eleventh cell.
- Forecast cost: 13 to 23 GiB and 2 to 4 h; measured 19.6 GiB and 32 min.

## Registry binding

The header is the canonical producer input `working/build/inputs/p32009-r10754/iso-nm.sing`, so `../build_registry.py`
binds the record: run from `docs/evidence/a5-exceptional-fibers` with the scan roots
`d5-p2 degree-one n15-laptop n16-laptop docs/local/a5-failed-runs iso-d6-n19-laptop` (in that order, because the first
root that holds a record names its source), it adds one bound certificate and marks Iso degree 6 at p = 32009
certified in `../claims.json`; without the last root, `--check` reproduces the previous registry. Singular version:
[`iso6-singular-version.txt`](iso6-singular-version.txt).

## Second run: N = 18 at 32009, then N = 19 at 32029

The laptop unit `a5-v11-iso-d6-next` ([`run-iso-d6-next.sh`](run-iso-d6-next.sh), sha256 59d0290e70a8ddac...) ran the
same engine in the same mode from 2026-11-08T20:11:57Z to 21:03:16Z ([`iso6b.events`](iso6b.events)); both error streams
are empty.

- N = 18, p = 32009, header 1f1757d55751f1e3...: wall 1,173.2 s, peak RSS 16,134,592 KiB, closure in 5 rounds;
  r_18 = 2,253 (blocks 583 / 568 / 551 / 551), below h_6, so it certifies nothing and binds no certificate.
- N = 19, p = 32029, canonical header `working/build/inputs/p32029-r9115/iso-nm.sing` (sha256 28c3c473369c6eda...):
  wall 1,905.6 s, peak RSS 20,525,468 KiB, closure in 6 rounds;
  [`isonm_d6_n19_p32029.json`](isonm_d6_n19_p32029.json) (sha256 40a86461193f2d1e...) reads r_19 = 2,422 with blocks
  632 / 610 / 590 / 590, the same per-block values as at 32009. It meets HF(k[y]/K2, 6) = 2,422, so h_6 = 2,422 over
  F_32029 as well (A5-125). The registry build with the scan roots above (the a5-failed-runs root given as
  `../../local/a5-failed-runs` from this directory) adds one bound certificate and marks Iso degree 6 certified at
  32029.
