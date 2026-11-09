# Review of PR 803 (engine v12, ledger audit, characteristic-0 transfer)

The owner chose two local reviewers for this pull request: `codex` on gpt-daybreak-blue at high effort and `grok`.
Both read [brief.md](brief.md) at head 5f787dfe4. `grok` stopped on its weekly usage limit before reading anything and
left no report. `codex` ran 15 min 39 s and wrote [review-codex.md](review-codex.md). Each finding is checked against
the source below; the Advisor reviews last.

| # | Finding (codex severity) | Verdict | Evidence and action |
|---|---|---|---|
| 1 | A5-270 computes the Jacobian of J in the nine-variable producer ring, so "rank 3, dimension 4" does not follow (serious) | holds | The producer ring keeps the presolve-eliminated t3 and t8. `x_opposite_qi.py` now asserts that J and G are free of them and takes the Jacobian over the seven slice variables; the rerun gives rank 3 and every other identity unchanged on both incidences (`x-opposite-qi.json`). |
| 2 | A5-270 omits the cancellation step from I = w I' to F(I) = F(I') (serious) | holds | The docstring and the A5-270 basis now state it: the local ring is regular, hence a domain, w is a non-zero-divisor, multiplication by w^d carries I'^d and m I'^d onto I^d and m I^d, and completion is faithfully flat. A5-270 stays proved on the repaired record. |
| 3 | Engine v12's production records retain ranks, not bases or pivots, so "byte equality" overstates them (serious) | holds | The engine-v12 README now names the comparison as equality of the rank-bearing fields and points at the unit tests for bases and pivots. Retaining per-block pivot and basis digests in the record is left for a later engine version. |
| 4 | The transfer note leaves the integral-matrix sandwich implicit (sloppy) | holds | `a5-char0-and-kernel-limits.md` gains a proposition for one pair, one degree and one prime, with the two matrices, both rank directions and the certificate bindings. |
| 5 | The status page prescribes two-prime reconstruction and the roadmap says v12 shortens the products stage (sloppy) | holds | Both rows corrected. Check 2's direct Q(i) computation has since stalled at the 3-hour cap (A5-248), so the status row now names a multi-prime lift with exact Q(i) verification. |
| 6 | A5-249 omits its N = 4 record (sloppy) | holds | Path added. |
| 7a | The Cayley-Dickson verification ran `python3` and seeds its floating maxima with `random.seed(3)` (sloppy) | holds, bounded | The archived report keeps what ran; its README now says those maxima are illustrations and every count and verdict is exact and seed-free. |
| 7b | `tests/test_modular_echelon.py` reuses one QRNG value across the parametrized cases of a test (sloppy) | refuted | The file declares one seed per test matrix family (line 16), each test function takes its own registered value, the parametrized cases draw different shapes, and `ci/seed_provenance.py --check` passes. |
| 8 | Two trailing-whitespace lines in the archived verification (cosmetic) | holds | Removed. |

The review's degree-7 section proposes a mechanism for the two jump laws, a one-ruling module for E8-bar -> VB and a
two-ruling module for Iso, W8 and X-; it enters the ledger as the open row A5-278 with codex's mechanism test.
