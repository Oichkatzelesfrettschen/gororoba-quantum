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

## What decides it, and what only corroborates

- Decisive: the exact squeeze. The lower bound is the quotient dimension
  r_18 = dim (P_5 + J + m^18) / (J + m P_5 + m^18) <= h_5 (fiber_rank_v11.py, quotient mode); the degree-2 membership
  receipt (sha256 7a4e45b11a1e4ab5..., 148 relations, 0 failures) makes the 952 K2-standard products span P_5 modulo
  J + m P_5; the upper bound HF(k[y]/K2, 5) = 952 (k2-hilbert.jsonl) uses the same 148 relations (relation sha256
  e047f996ad609a40...) in the same generator order (sha256 e7b5e2720243e85e...). The 235 nonstandard probes added no rank.
  The record's inflation surfaces are a false membership, a non-basis quotient export or wrong multiplication tables;
  the receipt and the export checks address them, and the rank itself is retained computation, not replayed here.
- The four character blocks are a valid direct sum over the odd field F_32009 (fiber_rank_v11.py checks block-respecting
  multiplication tables and rejects a generator spanning two characters), so their increments 215 + 197 + 270 + 270 sum to
  the total. The caps 215/197/270/270 in run-n18.sh come from the same character classification that produces the ranks,
  so reaching them is an internal decomposition check, not independent evidence.
- The N = 17 step (n17-laptop/) read r_17 = 871 with blocks 197/176/249/249 at both primes, identical quotient dimension
  55,913, and the degree-4 control r = 495; the ladder step agrees across primes one N below.
- Corroboration only: a trends analysis kept as an untracked local file (filesystem time 2026-11-06T21:28Z, before the
  result) put about 80 percent on r_18 = 952 with these blocks, from the ladder law T(d) = floor(7d/2) and the X- degree-5
  analogue; no commit or timestamp receipt binds that forecast, so the repository cannot authenticate it as a prediction.
  Forecast against measured: std 82 to 106 ks against 114.75 ks; peak 37 to 39 GiB against 35.4 GiB.
- The runner's check() reports a failed block invariant in n18.events but exits 0 (it only gates p = 32029); this run
  passed every check, and later runners exit nonzero on a failed invariant.

## Prediction for p = 32029, committed before that run starts

r_18 = 952 with blocks 215 / 197 / 270 / 270 and quotient dimension 72,693, and the degree-4 control r = 495. Basis: the
N = 17 step agrees across the two primes in rank, blocks and quotient dimension (n17-laptop/), and h_1..h_6 of K2 agree
at both primes (k2-hilbert.jsonl). A different value refutes the prime independence of the N = 18 step.

## Result at p = 32029 (2026-11-08)

The run ended 2026-11-08T06:29Z with exit 0 (`e8nm_d5_n18_p32029.json`, `n18.events`; wall 93,763 s, peak resident
35.4 GiB, the same engine `7849cbc71ccf1787`). It read r_18 = 952, blocks 215, 197, 270 and 270, and quotient
dimension 72,693: every degree-5 number of the prediction above, committed before the run. The degree-4 control at p = 32029 did not run (the runner ran d = 4 at p = 32009 only, `n18.events`). The degree-5 standard counts read
21, 83, 225, 495 and 952 for degrees 1 to 5. The representatives' relation file has sha256 `bfd7470c...`, the K2 whose
Hilbert function `../k2-hilbert.jsonl` records at p = 32029 with HF(k[y]/K2, 5) = 952. So the lower bound r_18 = 952
meets that upper bound, and h_5 = 952 holds at p = 32029 as at p = 32009 (ledger A5-220).

## Scope and falsifiers

- The statement holds over F_32009. The repeat at p = 32029 (gate: p = 32009 moved with every invariant intact) runs on
  `e8-nm-p32029.sing` (sha256 48bdcbe0fa17d04c...) with K2 receipt sha256 5573ef662aef... and the same engine and flags,
  after the degree-4 control (expected r = 495).
- hypothesis (to verify, task: characteristic 0): reduction modulo p cannot raise a rank, and HF(k[y]/K2) can only rise
  under reduction, so if the arc system and K2 at p are the reductions of their rational counterparts, 952 = r_p <= r_Q
  <= h_5(Q) <= HF_Q(k[y]/K2, 5) <= HF_p(k[y]/K2, 5) = 952 would give h_5 = 952 over Q. The step that needs proof is that
  the degree-2 K2 used at p equals the reduction of K2 over Q (it can be larger at a bad prime).
- Falsifiers: r_18 below 952 at p = 32029 (a prime-specific rank; not met, the run read 952), a degree-4 control other than 495, or a replay of
  this record with a different rank.

## Files

`e8nm_d5_n18_p32009.json` and `e8nm_d5_n18_p32029.json`, each with `.time` and an empty `.err`, `n18.events`, `n18-singular-version.txt`, `run-n18.sh`, and
`export-e8nm-p32009-n18-v11/` (`export.json`, `qB.txt.sha256`, `qG.txt.sha256`). The 4.1 GB export (quotient basis and
the nine multiplication tables) stays on the laptop under `~/a5/exports/e8nm-p32009-n18-v11/`; `export.json` and
`files_sha256_16` in the record name every file by hash, so a replay of the four rank increments needs those bytes.
`../n17-laptop/` holds the N = 17 records at both primes and their runners.
