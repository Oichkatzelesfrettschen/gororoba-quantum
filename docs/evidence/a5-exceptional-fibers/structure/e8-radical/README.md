# Radical structure of K2 for E8-bar -> N+-

Singular 4.4.1 runs, global ordering dp, retained from the session archive (paths rewritten relative to this
directory). `nm_p1`, `nm_p2`, `np_p1` and `np_p2` (E8-bar -> N- and N+ at p = 32009 and 32029) each compute, on the
retained degree-2 relation file of their target:

- the Hilbert functions of K2 and of its radical: 21, 83, 225, 495, 952, 1666 and 16, 69, 195, 440, 861, 1526 for
  d = 1 to 6;
- `rad^k_in_K2 k 2`: the square of sqrt(K2) lies in K2;
- `nilpotent_gens_outside_K2 355 linear 5`: the standard basis of the generators of sqrt(K2) reduced modulo K2,
  `std(reduce(R, std(K2)))`, has 355 elements, 5 of them with a linear term. A standard basis can hold elements that
  are redundant as generators, so 355 bounds the minimal number of generators of sqrt(K2) / K2 from above; the minimal
  count is not computed.

`k2-primes-nm-primes.sing` (E8-bar -> N-, p = 32009) splits K2 into its two minimal primes: a projective threefold of
degree 4 with Hilbert function 7, 22, 50, 95, 161, 252 and a projective fourfold of degree 11 with 12, 53, 155, 360,
721, 1302.

Consequences: the arc certificates of [`../../arcs/`](../../arcs/README.md) give L inside sqrt(K2), so F(I) surjects
onto k[y]/sqrt(K2) and 1526 <= h_6 <= 1666 (ledger A5-251). Because (sqrt K2)^2 lies in K2, the 140-dimensional space
sqrt(K2)_6 / K2_6 that decides h_6 by membership is a module killed by sqrt(K2) (A5-252).
