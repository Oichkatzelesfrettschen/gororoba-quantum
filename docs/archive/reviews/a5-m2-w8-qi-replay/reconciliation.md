# Review record: Macaulay2 replay of the W8 and Q(i) quadric ideals and degree-3 boost counts

Pull request 1002 (gororoba-quantum), branch `a5-m2-w8-qi-replay`. Reviewed head a18abf088; fixes on 1121f42c0.
Local reviewers chosen by the owner (2026-11-24): codex (gpt-daybreak-blue, high, read-only) and an opencode red
team on `opencode-go/glm-5.3-flash`; the Advisor reviews last. Both read one brief (six claims, each with a
falsifier): `brief.md`; reports: `review-codex.md`, `review-opencode.md`. The Advisor reviewed last (no further
finding on the scientific content; it required retained timing artifacts, this archive layout and a ledger merge order).

## Findings and dispositions

| # | Reviewer | Finding | Disposition |
|---|---|---|---|
| 1 | codex (serious) | `run_degree3.sh` `counted` accepts a log with a conflicting or duplicated RESULT line (probe: exact, duplicate and conflicting accepted) | Fixed in 1121f42c0: exactly one `targets`, `relations` and `done` line, each with its value; four known-bad logs (altered, appended conflict, duplicate, missing done) must be rejected; `run_degree3.sh check` PASS on the retained logs (x86_64, 2026-11-24) |
| 2 | codex | A5-609 cites a same-host calibration of 63 s that no retained file shows | Fixed in 1121f42c0: `calibration-p32009-run_m2.log` (the run's output with `/usr/bin/time -v`: PASS, 1:03.19, 343,220 KiB) is retained, listed in README and `sha256.txt`, and cited by A5-609 |
| 3 | codex | A5-608 lists `expected-results.txt` but not the acquired output | Fixed in 1121f42c0: `results.txt` added to its evidence |
| 4 | opencode (low) | the M2 mutant check passes a log that printed the count and then crashed | Fixed in 1121f42c0: `DONE mutant` required; the mutant run prints it (67 generators) |
| 5 | opencode (low) | a run without `dump`/`check` rewrites the retained logs | Boundary: both READMEs now state it; the replay that should leave the record intact runs on a copy |
| 6 | opencode (info) | check mode trusts the retained logs' lines (scripts are byte-compared, logs are not regenerated) | Boundary: the retained-record trust model; a full rerun regenerates the logs (37 min a value) |
| 7 | codex (structural) | the N+ and N- relation spaces differ in native coordinates though every invariant agrees | Recorded as an observation in this record; the transport map between them is the open question of A5-598 |
| 8 | A5 computation session | A5-610's dim (K2)_3 = 140 rests on A5-600's common Hilbert numerator; w = 9115 is the point c = 0, s = i | Fixed in 1121f42c0: both stated in the row and the README |

Claims 1, 2, 3 and 5 of the brief hold for both reviewers (codex: the ring map's kernel is (jj^2+1), the dump equals
the producer's Hilbert input, all twelve emissions byte-equal; opencode: recomputed Iso numerator expansion, both
`sha256.txt` verify, the A5-610 Hilbert value 80 from the A5-600 numerator).
| 9 | Advisor | timing figures in the READMEs and rows had no retained artifact | Fixed: `timings.tsv` in both run directories (wall, peak RSS, exit status of every run, derived from `/usr/bin/time -v`) |
| 10 | Advisor | `ledger.tsv` is also appended by PR 1001 and edited by PR 1004 | Merge order proposed to both owners: 1002, then 1001 rebased, then 1004 |
