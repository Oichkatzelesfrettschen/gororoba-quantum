# E8-bar -> N-, degree 5, N = 18, p = 32009: h_5 = 952

The laptop unit `a5-v11-e8nm-n18` (`run-n18.sh`) ran engine v11 (`fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in
quotient mode on `e8-nm-p32009.sing` (sha256 7d3521d0e8026e6f...) with the degree-2 K2 receipt of p = 32009, from
2026-11-05T17:35:16Z to 2026-11-07T02:29:03Z (`n18.events`). Wall 118,426.8 s, peak RSS 37,072,856 KiB (35.4 GiB,
`e8nm_d5_n18_p32009.time`); std 114,754.7 s, products 1,933.8 s, closure 1,722.1 s in 7 rounds.

## Result

`e8nm_d5_n18_p32009.json`: r_18 = 952 with blocks 215 / 197 / 270 / 270; dim_quotient 72,693; standard counts of the
representatives 21, 83, 225, 495, 952 in degrees 1 to 5; 235 consistency checks (172 targeted, 63 strided).

The lower bound: a truncated rank r_N of the arc system is at most h_5, the degree-5 Hilbert function of F(I). The upper
bound: F(I) is a quotient of k[y]/K2, so h_5 <= HF(k[y]/K2, 5) = 952 (A5-094). r_18 = 952 meets it, so h_5 = 952 over
F_32009 and F(I)_5 = (k[y]/K2)_5: no degree-5 relation beyond K2 at this prime. This supersedes the interval
861 <= h_5 <= 952 of A5-094 (row A5-183).

## Why the number is trustworthy

- Each of the four blocks reaches its own K2 count (215, 197, 270, 270, the bound `run-n18.sh` checks); a rank error
  that inflates the rank has no reason to land on four independent caps at once, and the block columns (18,018 to
  18,342) are about 70 to 85 times larger, so the rank is not capped by the matrix shape.
- Blocks 2 and 3 agree (270, 270), the symmetry invariant the script requires.
- Every block moved up from N = 17 (197, 176, 249, 249) and none exceeds its K2 count.
- The engine is the one that certified h_4 = 495 (A5-093, sha256 prefix 7849cbc71ccf1787).
- vdim 72,693 equals the exact D(18) polynomial value checked before products started.
- Preregistration: the trends analysis (written 2026-11-06T21:28Z, before the result) put about 80 percent on
  r_18 = 952 with blocks 215/197/270/270 and about 12 percent on a plateau at 871, from the ladder law that E8-bar reaches
  h_d at N = T(d) + 1 with T(d) = floor(7d/2) = 17 for d = 5, and the X- degree-5 analogue (201, 201, 296, then 417 at
  N = 18). Forecast against measured: std 82 to 106 ks against 114.75 ks; peak 37 to 39 GiB against 35.4 GiB; preflight
  35.2 GiB against 35.1 GiB.

## Scope and falsifiers

- The statement holds over F_32009. The repeat at p = 32029 runs next on the same unit (gate: p = 32009 moved with every
  invariant intact), on `e8-nm-p32029.sing` (sha256 48bdcbe0fa17d04c...) with K2 receipt sha256 5573ef662aef...; the
  degree-4 control (expected r = 495) runs first.
- hypothesis (to verify, task: characteristic 0): reduction modulo p cannot raise a rank, and HF(k[y]/K2) can only rise
  under reduction, so if the arc system and K2 at p are the reductions of their rational counterparts, 952 = r_p <= r_Q
  <= h_5(Q) <= HF_Q(k[y]/K2, 5) <= HF_p(k[y]/K2, 5) = 952 would give h_5 = 952 over Q. The step that needs proof is that
  the degree-2 K2 used at p equals the reduction of K2 over Q (it can be larger at a bad prime).
- Falsifiers: r_18 below 952 at p = 32029 (a prime-specific rank), a degree-4 control other than 495, or a replay of
  this record with a different rank.

## Files

`e8nm_d5_n18_p32009.json`, `.time`, `.err` (empty), `n18.events`, `n18-singular-version.txt`, `run-n18.sh`, and
`export-e8nm-p32009-n18-v11/` (`export.json`, `qB.txt.sha256`, `qG.txt.sha256`). The 4.1 GB export stays on the laptop
under `~/a5/exports/e8nm-p32009-n18-v11/`; `export.json` and `files_sha256_16` in the record name every file by hash.
