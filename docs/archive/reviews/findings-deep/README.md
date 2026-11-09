# Axiom-deep adversarial review of the A_5 findings (PR 798), 2026-11-09

Codex (gpt-daybreak-blue, high, read-only, documents repositories readable) and Grok (grok-4.7, high, confined to the
worktree, literature from the web) read one brief ([brief.md](brief.md)): [review-codex.md](review-codex.md) at
commit 3d928b1a6 and [review-grok.md](review-grok.md) at d21e9a76e. Local paths are scrubbed; the text is otherwise as
written. Both replayed the ledger and registry checks, the sign witnesses and the Rocq receipts (Codex) or re-hashed
every certifying rank record against its canonical header (Grok); neither found a certificate that fails.

Reconciliation, checked against the source:

- Flatness statistic of A5-241 (Codex 1): the chi-square tail was uncalibrated. Fixed before merge in PR 798
  (Hotelling T^2; 15 of 52 blocks at p < 0.05, three of four runs).
- Iso degree-6 note called N = 18 unmeasured (Codex 2): fixed in PR 798.
- Last-jump law A5-244 (Grok 1): the parity classes of the box k[x, y]/(x^{2d+1}, y^{2d+1}) split as (d+1)^2, d(d+1),
  d(d+1), d^2, which is not the measured block split (49/42/39/39 at d = 6). The closed form of
  `forecasts/trends-2026-11-06.md` (block 0 (2 floor(d/2)+1)^2, block 1 d(d+1), blocks 2 and 3 the rest in halves)
  matches every cell. The claim keeps its numbers and drops the box; no ring is identified (Codex: dimension matching
  alone does not identify the Segre-Veronese ring).
- Second-prime plateau (Grok 2): only N = 21 and 22 ran at p = 32029, so r_20 = r_21 is a p = 32009 measurement; the
  texts now say so. The certificates A5-167, A5-173, A5-155 and A5-161 are unaffected.
- C30 step 4 (Grok 3): the parity parenthetical did not exclude multiplication by x or y; the basis of I^n / m I^n
  follows from affine independence of the four exponent vectors, and Grok's Singular count (4, 10, 20, 35, 56, 84)
  agrees. The step now states the argument; A5-066 is unchanged.
- Stale rows (Grok 7, Codex run plan): A5-006 and A5-007 record degree 6; A5-012 is proved by A5-066; A5-073 is
  superseded by A5-063 and A5-237 by A5-066.
- File-handle leak in `replay/engine/fiber_rank_v8.py:94` (Codex 4): boundary. That engine is digest-pinned by
  retained certificates, the parsed bytes and witness rows replay unchanged, and a successor engine carries any fix.
- E8-bar -> VB rows A5-111, A5-107, A5-113 "unsized" (Grok run plan): refuted. The trends record (line 249) forecasts
  a 1.4 to 2.1 GiB preflight and under 5 GiB at degree 6; the cells run on the laptop under a 30 GiB cap.
- E8-bar degree 6 (A5-083/089/095/101): Grok places it on a paid VM (degree 5 already took 35.4 GiB and 33 h), Codex
  on a local proof. Both hold together: by the sign isomorphism one sign per prime suffices; the local route comes
  first (hours of Singular), and a paid VM follows only if it fails and only after the engine passes its acceptance
  rerun. Neither review can place the cell on a free host.
- Engine levers: both rank in-place update, streamed L and free-column storage ahead of 2-byte storage and GPU, with
  the W8 degree-4 byte-equal rerun as acceptance. The zero-row share measured on the W8 N = 19 export (28 to 45
  percent of quotient monomials have degree 16 or more) is disputed by Grok, who reads the truncation as already in
  `extend_products`; the share of stored L rows that are zero is to be measured on the degree-4 export before any
  claim.
- Quantum hardware: both find that no QPU measurement certifies an F_p rank or a fiber Hilbert function that exact
  CPU/GPU elimination does not already compute (A5-076); no provider case follows from this review.
