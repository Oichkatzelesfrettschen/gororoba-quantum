# X- -> N- at degrees 2 and 3, p = 32009: where the rank ladder closes and how its last jump splits

[`run.sh`](run.sh) ran engine v11 (`../replay/engine/fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode,
raw (every product), on the canonical header `../working/build/inputs/p32009-r10754/xm-nm.sing` (sha256
f437c9ea4f9e8861...) on 2026-11-08, each cell under an 8 GiB memory scope and a 900 s limit; every cell exited 0
([`runs.events`](runs.events)) with an empty error stream, in 1.7 to 34.9 s and at most 174 MiB. Tool versions:
[`singular-version.txt`](singular-version.txt).

| d | N | r_N | blocks 0 / 1 / 2 / 3 | HF(k[y]/K2, d) |
|---|---|---|---|---|
| 2 | 5 | 12 | 4 / 4 / 2 / 2 | 51 |
| 2 | 6 | 26 | 7 / 9 / 5 / 5 | |
| 2 | 7 | 26 | 7 / 9 / 5 / 5 | |
| 2 | 8 | 51 | 16 / 15 / 10 / 10 | |
| 3 | 10 | 73 | 16 / 15 / 21 / 21 | 122 |
| 3 | 11 | 122 | 25 / 27 / 35 / 35 | |
| 3 | 12 | 122 | 25 / 27 / 35 / 35 | |
| 3 | 13 | 122 | 25 / 27 / 35 / 35 | |

Two predictions met these runs. The trends file (`../forecasts/trends-2026-11-06.md`, the X order-law bullet under
section 1.3) read the measured r_5 = 12 and r_6 = 26 as putting the closing N at 7 (T_X(2) = 6); r_7 = 26 refutes that,
and the ladder closes at N = 8 after a plateau, as the X- degree-5 ladder plateaus at 201 for N = 15 and 16. The
last-jump law (ledger row A5-244) predicts a last jump of (2d+1)^2 split by character block like the parity classes of
the box k[x, y]/(x^{2d+1}, y^{2d+1}): 25 as 9 / 6 / 5 / 5 at d = 2 and 49 as 9 / 12 / 14 / 14 at d = 3. The measured
jumps are 51 - 26 = 25 with blocks 9 / 6 / 5 / 5 and 122 - 73 = 49 with blocks 9 / 12 / 14 / 14, so the law survives
two cells it was not fitted on. The closing N of X- is 4, 8, 11 and 18 at d = 1, 2, 3 and 5, not 3d + 1; its rule is
open. The rank 51 at d = 2 and 122 at d = 3 equal the certified K2 counts and add no certificate.
