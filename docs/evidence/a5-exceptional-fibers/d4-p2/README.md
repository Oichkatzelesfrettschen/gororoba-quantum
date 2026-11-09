# Degree 4 at the second prime p = 32029

[`run.sh`](run.sh) ran engine v11 (`../replay/engine/fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode,
raw, on the canonical header `../working/build/inputs/p32029-r9115/xm-nm.sing` on 2026-11-09, each cell under a 16 GiB
address-space cap (`prlimit --as`; the build host had no user bus) and a 1,800 s limit; both cells exited 0
([`runs.events`](runs.events)) with empty error streams.

| fiber | N | r_N | blocks 0 / 1 / 2 / 3 | wall, peak RSS |
|---|---|---|---|---|
| X- | 14 | 159 | 43 / 46 / 35 / 35 | 40.6 s, 246 MiB |
| X- | 15 | 240 | 68 / 66 / 53 / 53 | 70.2 s, 313 MiB |

r_15 = 240 = HF(k[y]/K2, 4) certifies h_4 = 240 for X- at 32029 (ledger A5-171), and the X sign isomorphism
(`../witnesses.jsonl`) carries it to X+ (A5-159); `../build_registry.py` binds the record once `d4-p2` is among its scan
roots (`../README.md`). The ladder and the block splits equal those at p = 32009 (`../xm-lown/`), including the last
jump 81 split 25 / 20 / 18 / 18 of ledger row A5-244.
