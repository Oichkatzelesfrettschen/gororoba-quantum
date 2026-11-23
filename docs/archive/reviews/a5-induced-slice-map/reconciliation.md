# PR 994 local review: reconciliation

Head under review: `f4633658f`. Reviewer: codex (gpt-daybreak-blue, high effort, read-only). Red team: opencode with
`opencode/deepseek-v4.1-flash-free`. Both read [brief.md](brief.md). Neither reports a fatal finding, and both confirm
that every recorded number matches its log. Each finding below was checked against the source before it was acted on.

| Finding | Source | Verdict | Action |
|---|---|---|---|
| `run_boost.sh` passes without checking the adjugate identity, the pivot Pfaffian, the selection count, the normal-form size and the exact set of minimal primes; the radical check intersects only the first and last prime | codex 1, opencode 3 and 4 | confirmed | the script prints `prime_count` and intersects every prime; the driver compares the sorted prime lines with a literal and requires seven further lines; the twelve points are rerun. The new gate rejected its first run on a pattern error of the fix itself and passes after the correction |
| The README's localization argument is too strong: the header pivot Pfaffian is not a unit of the displayed ring, "killed by s2" is not the fact used, and gradedness alone does not justify the truncation of an inhomogeneous header Pfaffian | codex 2, opencode 1 | confirmed | the README states the three facts that carry the argument: header Pfaffians lie in the graded ideal once the weight pivot is inverted (A5-593), components above the largest generator weight lie in m I, and I / (J + m I) is supported at the origin |
| The six modular checks compare ideals and cannot single out the induced map | opencode 2, codex (verified claims) | confirmed as a limit | the README and the status note say that the identification rests on a deduction in prose; the row stays `certified` for the matrix and its reductions |
| The status note's layer table still lists the E8-bar slice map as open and calls A5-597 "this change" | codex 3 | confirmed | corrected |
| The emitted boost scripts end in an extra blank line | codex 4 | confirmed | the generator strips it; the scripts are regenerated |
| The Gauss-image probe does not gate the span 105, the zero scalar coordinate or the differential rank 15 | opencode 5 | confirmed | the three values join the verdict |
| `run_m2.sh` records the Macaulay2 version without comparing it | opencode 6 | confirmed | the driver requires 1.25.11 |
| `run_induced.sh` does not reject a Singular error line | opencode 7 | confirmed | the driver fails on a line that starts with `?` |
| Header Pfaffian weights are not printed | opencode 1 | boundary | the rewritten argument needs no bound on the header weights: every component above the largest generator weight lies in m I; no line added |
| Input digests of the five ideal files and the six header files are not rechecked by the drivers | opencode 6 and 7 | boundary | the files are tracked and the neighboring directories carry their own `sha256.txt`; not added |
| The function-field boost run has no deadline in the driver | opencode 8 | boundary | the caller sets the deadline; the run of this record had a 4 h cap and is not retained |

Reruns after the fixes, on the same host and versions: `run_induced.sh` PASS, `run_m2.sh` PASS, `run_boost.sh` PASS,
the probe pass with ranks 3,887 and 4,022.

## Advisor, last

The Advisor read the head `bee2f23d6` with the two reports and the fixes above.

| Finding | Verdict | Action |
|---|---|---|
| The error-line gate of `run_boost.sh` was a negated command in the middle of a function, which `set -e` ignores | confirmed | both drivers use an `if` with an explicit exit; on a copy of the retained logs the gates accept, and with a planted error line they exit 1 |
| A5-601 read `certified` for a sampled lower bound | confirmed | the row reads `survives`, as A5-460 does; the totals are 118 certified and 114 survives |
| The probe ran its two strata in a serial loop | confirmed | `parallel.ordered_map` over the two strata; rerun with the same ranks |
| The archived reviewer reports held links relative to another directory | confirmed | the links are code spans |
| The truncation of the header Pfaffians rested on prose | confirmed | mode `high` of `induced_slice_map.py` tests the part of weight above 10 of each header Pfaffian against an untruncated standard basis of J + m I: 0 outside at both basepoints over Q(i); truncating at the header weight 29 instead did not finish in 9 min and is not used |
| The status note said X lacks a slice map | confirmed | X is decided on the header slice (A5-270, A5-305); the note and the README name W8 and Iso |
| The function-field boost run had no watcher, and "46 min" is not its cost | confirmed | a watcher on its end marker; the record states the cost when the run ends or reaches its cap |

## Hosted Codex round (1 of 1), head `087eb76e0`

| Finding | Verdict | Action |
|---|---|---|
| `run_boost.sh` runs the twelve independent boost values in a serial loop | confirmed | `boost_family.py --run` dispatches the values through `parallel.ordered_map`; the driver gates the logs afterward; rerun with one normal form at the twelve values |
