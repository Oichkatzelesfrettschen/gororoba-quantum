# X- -> N- at degrees 2 to 4, p = 32009: where the rank ladder closes and how its last jump splits

[`run.sh`](run.sh) ran engine v11 (`../replay/engine/fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode,
raw (every product), on the canonical header `../working/build/inputs/p32009-r10754/xm-nm.sing` (sha256
f437c9ea4f9e8861...) on 2026-11-08, each cell under an 8 GiB memory scope and a 900 s limit; every cell exited 0
([`runs.events`](runs.events)) with an empty error stream, in 1.7 to 143.1 s and at most 434 MiB. Tool versions:
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
| 4 | 12 | 99 | 29 / 28 / 21 / 21 | 240 |
| 4 | 13 | 159 | 43 / 46 / 35 / 35 | |
| 4 | 14 | 159 | 43 / 46 / 35 / 35 | |
| 4 | 15 | 240 | 68 / 66 / 53 / 53 | |
| 4 | 16 | 240 | 68 / 66 / 53 / 53 | |

Two predictions met these runs. The trends file (`../forecasts/trends-2026-11-06.md`, the X order-law bullet under
section 1.3) read the measured r_5 = 12 and r_6 = 26 as putting the closing N at 7 (T_X(2) = 6); r_7 = 26 refutes that,
and the ladder closes at N = 8 after a plateau, as the X- degree-5 ladder plateaus at 201 for N = 15 and 16. The
last-jump law (ledger row A5-244) predicts a last jump of (2d+1)^2 split by character block like the parity classes of
the box k[x, y]/(x^{2d+1}, y^{2d+1}): 25 as 9 / 6 / 5 / 5 at d = 2, 49 as 9 / 12 / 14 / 14 at d = 3 and 81 as
25 / 20 / 18 / 18 at d = 4. The measured jumps are 51 - 26 = 25 (9 / 6 / 5 / 5), 122 - 73 = 49 (9 / 12 / 14 / 14) and
240 - 159 = 81 (25 / 20 / 18 / 18), so the law survives three cells it was not fitted on.

The closing N of X- is 4, 8, 11, 15 and 18 at d = 1 to 5, not 3d + 1. Hypothesis, read off these five cells after the
runs: the closing N is floor(7d/2) + 1, the 3.5 steps per degree the trends file assigns to E8-bar -> N-; at even d the
ladder plateaus for one step before the jump (r_6 = r_7, r_13 = r_14). It predicts that X- degree 6 closes at N = 22
(target 665, last jump 169 split 49 / 42 / 39 / 39) and plateaus at N = 20 and 21. The ranks 51, 122 and 240 equal the
certified K2 counts and add no certificate.

## Degree 6, preregistered before the runs finished (2026-11-09)

`../w8-engine-map/classify.py` (engine v11's own `standard_monomials` and the xor block rule of `block_products`), run
on the canonical header with the X- degree-2 receipt (`../working/distribute/out/a5-xm-d4/xm_p1/d2/receipt-d2.json`)
and the generator export of a degree-2, N = 5 run, gives the per-block standard-monomial counts of k[y]/K2 in
[`k2-blocks-xm-p32009.json`](k2-blocks-xm-p32009.json): degree 2: 16 / 15 / 10 / 10, degree 3: 25 / 27 / 35 / 35,
degree 4: 68 / 66 / 53 / 53, each equal to the measured closing blocks above; degree 5: 93 / 96 / 114 / 114;
degree 6: 181 / 178 / 153 / 153 (sum 665); degree 7: 230 / 234 / 266 / 266.

Predictions for the laptop runs of degree 6 at N = 22, 21, 20 (`run-xm-d6.sh`, engine v11, raw, p = 32009):
r_22 = 665 with blocks 181 / 178 / 153 / 153 (the K2 count; A5-244 and the closing-N hypothesis floor(7d/2) + 1 = 22);
r_21 = r_20 = 496 with blocks 132 / 136 / 114 / 114 (the last jump 169 split 49 / 42 / 39 / 39, and the one-step
plateau at even d). Falsifiers: r_22 below 665 (closing later), r_21 = 665 (closing earlier), a last jump other than
169 or a split other than 49 / 42 / 39 / 39, or r_20 differing from r_21.
