# Pfaffian identity of the Schur numerator in the E8-bar Rees scripts

The Rees scripts of [../e8-rees-fibers-v2-p32009](../e8-rees-fibers-v2-p32009/README.md) split the skew matrix
T = F^T C F of the weight slice into a 6 x 6 block B, a 6 x 9 block X and a 9 x 9 block D, and take the 126 principal
4-Pfaffians of W = det(B) D + X^T adj(B) X as the generators of the kernel-coordinate ideal. Ledger row A5-592 records
that every unit polynomial stripped from the 21 selected generators is (s2^2 - 1)^3 (s2 -+ r)^3, with exponent 4 on
(s2^2 - 1) for generators 10 and 16. This directory derives both facts from one identity (rows A5-593 and A5-594).

## Result

Over Q(i)[s1..s9], for N- and for N+:

- Pf(B)^2 = det(B), with Pf(B) = -32 i (s2 - 1)(s2 + 1)(s2 - i) for N- and 32 i (s2 - 1)(s2 + 1)(s2 + i) for N+.
- For each of the 126 quadruples a < b < c < d of 1..9,

      Pf_4(W; a, b, c, d) = Pf(B)^3 Pf_10(T; 1..6, 6 + a, 6 + b, 6 + c, 6 + d),

  an identity of polynomials (`PFAFF RESULT ... checked 126 nonzero 126 failures 0`). It is the Pfaffian form of the
  Schur complement: W / det(B) is the Schur complement S of B in T, Pf_4(S) = Pf_10(T) / Pf(B), and
  Pf_4(W) = det(B)^2 Pf_4(S).
- Known-bad control: with exponent 2 in place of 3 the identity holds for none of the 126 quadruples
  (`control_exponent2_equal 0`).

So each generator carries the factor Pf(B)^3, a constant times (s2^2 - 1)^3 (s2 -+ i)^3: the unit polynomial of
A5-592. Modulo 32009 (i = 10754), with J the slice ideal of the run script:

- the identity holds modulo J on the 21 selected generators (`identity_failures 0`);
- Pf_10 of the selected quadruple lies in J + (s2^2 - 1) for generators 10 (Pfaffian 51, quadruple 1 5 7 9) and
  16 (Pfaffian 87, quadruple 2 5 8 9) and for no other selected generator, at both signs; no selected Pf_10 lies in
  J + (s2 - i) or J + (s2 + i), and none is zero modulo J. The fourth factor (s2^2 - 1) of those two generators comes
  from Pf_10, not from Pf(B).

## Scope

The identity is checked over Q(i) on the matrices of the two retained run scripts at (32009, 10754), read with i
transcendental modulo i^2 + 1; it is an instance of a general identity for skew matrices, which this directory does
not prove in general. The membership statements about Pf_10 are computed at one prime and root; membership of Pf_10 in
J + (s2^2 - 1) is the ideal form of the divisibility that the run script finds by a content computation.

## Replay

    sh docs/evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity/run_pfaffian.sh

from the repository root with Singular 4.4.1 on PATH: it rebuilds the four scripts from lines of the two run scripts
and the tails of this directory and runs them (4 s per Q(i) script, under 1 s per modular script, 16 MB).

| File | Content |
|---|---|
| `run_pfaffian.sh` | builds and runs the four scripts |
| `tail-qi-CELL.sing`, `tail-p32009-CELL.sing` | the checks appended to the cut run scripts |
| `pfaffian-schur-CELL-qi.sing`, `.log`, `.time` | the identity over Q(i) |
| `pfaffian-schur-CELL-p32009.sing`, `.log`, `.time` | the identity modulo J and the Pf_10 memberships at 32009 |
| `sha256.txt` | sha256 of every other file of this directory |
