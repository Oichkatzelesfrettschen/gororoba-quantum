# Axiom-deep adversarial review of the A_5 findings (PR 798), 2026-11-09

Codex (gpt-daybreak-blue, high, read-only, documents repositories readable) and Grok (grok-4.7, high, confined to the
worktree, literature from the web) read one brief ([brief.md](brief.md)): [review-codex.md](review-codex.md) at
commit 3d928b1a6 and [review-grok.md](review-grok.md) at d21e9a76e. Local paths are scrubbed; the text is otherwise as
written. Codex replayed the ledger and registry checks, the sign witnesses and the Rocq receipts; Grok ran none of those
replays (`review-grok.md`, line 3) and instead re-hashed every certifying rank record against its canonical header
and inspected the rest; neither found a certificate that fails.

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
  on a local proof. By the sign isomorphism one sign per prime suffices. The local proof cannot take the C30 form
  (A5-066), which rests on K2 being radical for W8 (A5-061): E8-bar's K2 is not radical, so arcs and plane families
  bound L only by sqrt(K2) and reproduce h_6 >= 1526. The cell is decided in the 140-dimensional space
  sqrt(K2)_6 / K2_6 by a membership receipt on those forms, piloted first on the 91-dimensional sqrt(K2)_5 / K2_5,
  where h_5 = 952 fixes the answer (no form lies in L). A paid VM follows only if that route fails.
- Engine levers: both rank in-place update, streamed L and free-column storage ahead of 2-byte storage and GPU, with
  the W8 degree-4 byte-equal rerun as acceptance. The zero-row share measured on the W8 N = 19 export (28 to 45
  percent of quotient monomials have degree 16 or more) is disputed by Grok, who reads the truncation as already in
  `extend_products`; the share of stored L rows that are zero is to be measured on the degree-4 export before any
  claim.
- Quantum hardware: both find that no QPU measurement certifies an F_p rank or a fiber Hilbert function that exact
  CPU/GPU elimination does not already compute (A5-076); no provider case follows from this review.

Advisor verdict on the reconciliation and the run plan (2026-11-09): every item above confirmed, with two
corrections now in the run plan of `docs/notes/topics/a5-exceptional-fiber-findings.md`. The E8-bar degree-6 route is
the sqrt(K2)/K2 membership receipt, not a C30-style local proof (the bullet above). The E8-bar wall is the Singular
export: at degree 5 the standard basis of k[t]/(J + m^18) took 114,755 of 118,427 s (97 percent), so engine v12 and
the GPU path, which shorten the products and closure stages, speed up W8 and Iso (Iso degree 6 at N = 19: closure
1,405 s and products 312 s of 1,900 s) and leave E8-bar and X- (X- degree 6: export 1,356 of 1,700 s) at their export
time.

What survives justification, falsification and the Advisor:

- Every retained certificate: Codex's replays of the ledger, registry and sign witnesses and Grok's re-hash of every
  certifying rank record against its header find no failure, and E8-bar -> VB degree 4 at p = 32029 (A5-111) joins them at r_13 = 155.
- The last-jump law A5-244 as numbers: last jump (2d + 1)^2, block split by the trends closed form. The box-parity
  reading is falsified and removed.
- The X- plateau r_20 = r_21 as a p = 32009 measurement; at p = 32029 it is unmeasured until N = 20 runs there.
- The flatness claim A5-241 in its narrowed form: Hotelling T^2 at p < 0.05 on 15 of 52 blocks (Fisher 3e-11) on three
  of four runs.
- C30 (A5-066) with step 4's basis argument stated, and with it A5-012 proved; A5-073 and A5-237 superseded.
- The run plan: the E8-bar -> VB ladders first, the sqrt(K2)/K2 membership receipt for E8-bar degree 6, engine v12
  with its byte-equal W8 degree-4 acceptance for W8 and Iso, a paid VM only if membership fails.
- Bounded, not refuted: the engine v8 handle leak (digest-pinned engine) and the zero-row lever (unmeasured until the
  degree-4 count). Refuted: "VB unsized" (trends line 249). No QPU job certifies a rank (A5-076).
