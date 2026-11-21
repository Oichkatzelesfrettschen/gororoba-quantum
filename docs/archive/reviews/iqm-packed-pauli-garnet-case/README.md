# Review record: the packed Pauli Garnet case (PR 972)

Local reviewers chosen by the owner (2026-11-21): codex (gpt-daybreak-blue-latest, high), grok and agy
(gemini-4-hydrogen-high), on one brief. They read the head before the buffer revision (36 circuits, ceiling 2.5
credits); the buffer revision and the second mock run followed their findings. The Advisor reviewed last.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, grok, agy | IQM runs a job's segments in order and repeats the sequence once per shot (docs/notes/iqm/docs/iqm-pulse/concepts.md:83), so each pair's arms run back to back inside every shot; one active-reset cycle leaves measured initialization error (results/iqm/reset_billing_pilot_analysis.json), and treatment-dependent carryover breaks the exact test's premise | Fixed by the owner's choice of buffer circuits (AskUserQuestion, 2026-11-21): one measure-only buffer before every science circuit gives both arms the same predecessor, and `carryover_after_dense_minus_sparse` reads the lag-two residue; the written case states both |
| 2 | grok, agy | The 2.5-credit ceiling cancels at 4.0 s, below the case's own 4.31 s | Fixed: ceiling 5.00 credits from the expected seconds plus the plan headroom, cancel at 9.0 s; the written case states that cancellation is best effort |
| 3 | codex | "Enforceable cost: closed" overclaims | Fixed in the written case |
| 4 | codex, grok | The 0.823 prediction is called a noisy device mean | Fixed: labeled the independent-cell gate and readout baseline with its omissions in prediction.json |
| 5 | agy | The final-layout predicate is dead under routing none; barrier order is not verified | Fixed: the final index layout must equal the fixed layout, and the two halves compile separately around one barrier; the self-test refuses a drifted layout and a crossed barrier |
| 6 | codex, grok, agy | Stale rows: mock, barrier, order, timing | Fixed: two mock jobs retained (01a1ff98, 36 circuits; 01a1ffe7, 68 circuits), each row updated |
| 7 | agy | A home-directory token path in the written case | Fixed: `TOKENS.json` placeholder |
| 8 | agy | Full-build tests are slow and unmarked | Fixed: marked `audit` (on-demand gate core-615 runs them); gate `core-iqm-packed-pauli-case-self-test` added |
| 9 | Advisor | The two mock runs were unregistered and the plan read inbox | Fixed: two acquisitions in docs/state/research_state.json; plan step reconcile-obligation-1 done with its receipt, plan active |
