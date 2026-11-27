# Review: abelian boosts of arXiv 2606.06404 in the connections table

Pull request 1027 adds one row to `docs/design/a5-null-slice-connections-program.md` and ledger row A5-646. The owner
chose the Advisor as the only local reviewer (2026-11-27); the hosted Codex round then asked for an empty supersedes
cell and an inbound link to this record (fixed in `71221c370`) and found nothing at that head. Head under review: `8c03a1d12`, then `bd9dc702f`; fixes land
in `02c6f05fd`.

## Findings and resolutions

| Finding | Resolution |
|---|---|
| "Its boosts are abelian" claims the whole paper from three pages; JT gravity often carries sl(2,R) = so(2,1), the m = 2 case of the note's so(m,1) comparison | Searched the filed transcription for sl(2), SL(2), so(2,1), non-abelian, noncommuting and Lie algebra: no use. Page 6 states that the vertex quantizes SO(1,1) group multiplication. The row and A5-646 cite both |
| Two canonical pairs read as a mismatch with the one generator of 2611.34924 | Page 5: gluing imposes J = 0 and keeps (s, K) alone; the row now says the glued theory has one boost generator |
| That J and K commute is a deduction, not a statement of the paper | The evidence cell marks it inferred from independent canonical pairs |
| Equations 1.1 and 1.2 were cited to pages 7 and 25 | They sit on page 5; the row cites pages 5 to 7 and 25 |
| The crossed-product clause rested on an unread sentence | Page 6 read: dressing to the left boost frame makes the interior matter algebra fail to commute with the s_L edge mode, which is the crossed product of equation 1.3; the row says the noncommutativity is between matter and boost |
| The 2611.34924 row has ledger A5-628; this read had none | A5-646 added, after A5-643 to A5-645 of pull request 1026 |
| The pull-request body named a private-repository row and repository | Removed; earlier bodies (1017, 1019, 1022, 1024) name neither |

## Residual risk

The read covers pages 5 to 7 and 25 and a vocabulary search; a non-abelian structure under another name would move the
row off `boundary`, which is its stated falsifier.

A5-642 appeared twice on main after pull request 1024 (the octonion-space covariance row of pull request 1022 and an
E8-bar row); pull request 1026 renumbered the E8-bar row A5-643, and this branch merged that fix before its CI run.
