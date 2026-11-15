# Predictions for the quadric rings at the third prime 32057

Recorded 2026-11-15T08:24:15Z (UTC), before any degree-2 relation file at p = 32057 existed. The prime is the first prime
p = 1 mod 4 above 32029 (`fiber_inputs.find_split_prime(32030, 1)`), with the smaller square root of -1, 8059.

The hypothesis under test is ledger row A5-548: a quadric ring k[y]/K2 of the fiber track is Cohen-Macaulay exactly
when K2 is radical, and where it is not, the whole defect is a nilradical module of rank one over a smaller cone.

| Fiber | Generators | Krull dimension | Degree | Linear-section length | h-vector | Cohen-Macaulay | Radical |
|---|---|---|---|---|---|---|---|
| X- -> N- | 15 | 4 | 12 | 15 | 1, 11, 3 | no | no (nilpotent linear forms y1, y5, y6) |
| X+ -> N+ | 15 | 4 | 12 | 15 | 1, 11, 3 | no | no |
| E8-bar -> VB | 10 | 4 | 7 | 7 | 1, 6 | yes | yes (two primes, linearly joined) |
| Iso -> N- | 17 | 5 | 23 | 23 | 1, 12, 10 | yes | yes |
| E8-bar -> N- | 21 | 5 | 11 | 20 | 1, 16, 3 | no | no (five nilpotent linear forms) |
| W8 -> N- | 24 | 6 | 50 | 50 | 1, 18, 27, 4 | yes | yes |

Degree-2 relation counts: 69 (X), 34 (E8-bar -> VB), 85 (Iso), 148 (E8-bar), 156 (W8), as at 32009 and 32029.
Correction recorded after the X, E8-bar -> VB and Iso cells ran and before the E8-bar and W8 cells started: 34, 85
and 156 are the retained h_2 values of E8-bar -> VB, Iso and W8, not relation counts; the retained relation counts
are 21, 68 and 144 (55 - 34, 153 - 85, 300 - 156).
For the non-Cohen-Macaulay rows the defect structure of A5-544 (X: A = K2 : P a plane of 12 linear forms,
K2 : A = P) and A5-547 (E8-bar: R = K2 + N, N^2 in K2, A = K2 : R prime of dimension 4 and multiplicity 2,
K2 : A = R, Hilbert identity N_K2 - N_R = N_A - (1 - t)^21) is predicted unchanged.

A row that is reduced and not Cohen-Macaulay, or nonreduced and Cohen-Macaulay, refutes A5-548.
