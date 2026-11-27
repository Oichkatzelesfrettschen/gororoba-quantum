# Review: cd_sign as the Albuquerque-Majid cochain, and the triple count for every D

Pull request 1031 records the Hopf-type search of pool row MATH-75 in `docs/design/a5-null-slice-connections-program.md`,
proves the census count of non-associating basis triples for every D (`docs/evidence/a5-left-table-census/README.md`
statement 3), and adds ledger rows A5-648 and A5-649 (A5-634 superseded). The owner chose Neon (agy, Gemini 4 Neon
Medium, the standing tmux reviewer) as red team, with the Advisor last (2026-11-27). Head under review: `00782d12e`;
fixes land in the commit that adds this record.

## Findings and resolutions

| Finding | Resolution |
|---|---|
| Claims 1 to 6 (the cochain identity, the opposite algebra, the transcription of Proposition 4.5, the R rule, the degenerate-triple lemma, the count) hold; Neon reproduced each on the workstation: cd_sign equal to the transposed cochain to D = 128, Proposition 4.5 on all eight cases to D = 64, and each off-Gamma case count 4(D - 1)(D - 2) at D = 4 to 32 | None needed |
| The degenerate-triple step concludes that every R product is 1 from the D = 16 table, which also needs phi = 1 off Gamma at D = 8 | The census proof and A5-649 cite the tables at D = 8 and D = 16 together |
| "Proposition 3.6 makes the unit sphere a quasigroup only for a cochain with the composition property" overstates page 9, which gives the sufficient direction alone | The row reads "for a cochain with the composition property, which Hurwitz's theorem confines to n <= 3" |
| The row and A5-648 claim phi = 1 off the generic triples to D = 64, while the test ran it to D = 32 | The test runs n = 1 to 6 (D = 64) |
| Hypothesis: Proposition 4.5 gives Lemma R of the family proof in one line, since the commutation sign of a and tau is -phi(k, tau, a) phi(k, a, tau) in their convention; it does not reach the block-sign lemma, which concerns F rather than dF | Recorded in the row's falsifier cell as a hypothesis |

## Residual risk

The Hopf-quasigroup statement covers the signed basis set; Bulacu 2009 (Zbl 1247.17001) and Smith 2016
(Zbl 1350.20051) are listed unopened. The ids A5-648 and A5-649 follow A5-647 on main at the time of the push.
