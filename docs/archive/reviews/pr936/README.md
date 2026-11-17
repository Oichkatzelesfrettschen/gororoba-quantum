# Review of PR 936 (the Q(i) test of A5-548 on the weight slice)

The owner chose no local reviewer beyond the Advisor for this pull request. The hosted review ran in the order of
`AGENTS.md` ("Reviews and merges"): Codex once, then Copilot once, because the Codex round needed a fix. The Advisor
reviewed the pull request partially before the hosted rounds. No reviewer brief file exists for the Advisor, which read
the pull request from the session; the hosted reviewers read the diff of the head named in the table below.
Where a source is silent the entry reads "not recorded".

## Reviewers and heads

| Reviewer | Head read | Requested | Posted | Findings |
|---|---|---|---|---|
| Advisor | not recorded; it precedes `ff7640e39` (parent `cbcebba8c`) | not recorded | 2026-11-16 08:35Z (the board entry that records it) | three blocking, five confirmed or clean |
| Codex (hosted) | `ff7640e39` | 2026-11-16 09:28Z (`@Codex review`) | 2026-11-16 09:34Z | two P1 threads |
| Copilot (hosted) | `c3b8b9c43` | not recorded | 2026-11-16 12:24Z | two threads |

The Advisor read about 26 thousand of about 670 thousand characters (its own report, as the board quotes it); its
confirmations cover what it read. The final head `4153bace5` carries the fixes of the Copilot round and has no hosted review, since the
round order allows each hosted stage once.

## Findings and dispositions

| # | Reviewer | Finding | Verdict | Action |
|---|---|---|---|---|
| 1 | Advisor | The replay record of the gate `core-a5-weight-slice-quadric-rings` is missing: the 231 s run in the body belongs to `core-a5-header-relation-ideal-orders` | holds | `ff7640e39` states in the body that the gate had not run at that head and attributes the 231 s run to the other gate. The gate then passed at `c3b8b9c43` (231 s, two workers, `replay_check` equal in every compared field) and at `4153bace5` (275 s, two workers, no differing field), on a 4-vCPU Singular 4.4.1 host. The body records both runs |
| 2 | Advisor | The root 21255 at p = 32009, degree 2, has no open ledger row | holds | `ff7640e39` adds `A5-571` with its falsifier and closing computation; no K2 file for that root exists yet |
| 3 | Advisor | The receipt directory lacks retained-bytes provenance | holds | `ff7640e39` adds a provenance table to the receipt README: 13 files unchanged, 5 edited with their original digests, none regenerated |
| 4 | Advisor | Gate wiring, lint and type file lists, runner-image record and the `A5-009` edit | confirmed | none needed |
| 5 | Advisor | Public-path scan | clean | none needed |
| 6 | Codex | The eight cells and four calibration rings run serially in a comprehension, which bypasses `parallel.py` for independent CPU-bound items | holds | Fixed in `003e9a5db`: they map through `parallel.ordered_map` in input order with one checkpoint file per ring; the cap is the case file's 52.5 GB budget over the 8 GiB per-call address-space limit (six), lowered by `GOROROBA_WORKERS`. The record bytes follow the serial run's apart from the timing fields the gate skips |
| 7 | Codex | Tests that read the retained record, its relation digests and its predictions run in the default PR lane | holds | Fixed in `c3b8b9c43`: they carry the audit marker (`pytest -m audit`, 30 pass); the default lane keeps constructed-row tests of `audit_row()` and `problems()` and a patched `main()` run that checks pool order and the worker cap (5 pass) |
| 8 | Copilot | `post_check.py` still prints `controls_reject 1 pass 1` when a control result is missing or malformed | holds | Fixed in `498407378`: `control_rejects` passes only on exactly one pair of nonnegative integer remainder counts per control with one positive count; `tests/test_a5_e8np_post_check.py` covers the missing, repeated, malformed and zero cases; the edited script reproduces `post.log` line for line on the retained receipt; `sha256.txt` and the receipt README state the second edit |
| 9 | Copilot | A relation-regeneration timeout raises through `ordered_map` and aborts `main()` before the record is written | holds | Fixed in `4153bace5`: `cell()` catches the Singular time-limit `RuntimeError` and returns an undecided row (`relations_sha256` null, `relations_match_retained` false, `hypothesis_holds` null); `problems()` reports it; any other Singular error propagates; two tests drive `main()` with a fake Singular |

All four hosted threads carry a reply that begins `Fixed in <commit>` and are resolved.

## Validation at the final head

The six `pr.yml` checks (`lint`, `types`, `tests`, `contracts`, `arm (ubuntu-26.04-arm)`, `arm (macos-15)`) passed on
`4153bace5`. The Singular replay gate is not part of those checks and ran on demand (finding 1).

## Not recorded

- The head the Advisor read and the time of its request.
- Any Advisor round after the three blocking items; the board shows none.
- The time of the Copilot request.
