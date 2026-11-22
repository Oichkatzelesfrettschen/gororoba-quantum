# Reconciliation: A5 E8-bar open cells, replay and modulo colon

Both reviewers read commit 13d5ad48c of branch `a5-rees-open-cells` on 2026-11-22, read-only, on the brief beside this
file. Reviewer: `grok` (default model). Red-teamer: `agy` on `gemini-4-neon-high`. The Advisor did not run, by the
owner's instruction for this session. Each finding below was checked against the source; fixes land in the commit that
adds this record.

## Claims

| Claim | grok | Neon | Outcome |
|---|---|---|---|
| 1. Six certificates 148, 5, 11, L = K | values confirmed | not broken | stands; the README already states that the scripts carry the v3 guard edits, which the brief's falsifier omitted |
| 2. Replays equal beyond timers | holds | not broken | stands; the basis files are not retained, so the digests are records of the run hosts |
| 3. Modulo colon equals the quotient colon | holds on the saturated bases | not broken for a principal ideal | stands, narrowed: the README now says that the saturated file is the colon evidence, that the first-stage file precedes the colon, and that the identity is for the principal ideal (u) |
| 4. Relation lines of sign pairs | equality holds, count is 148 | count is 148, wording too wide | fixed: 148 lines, the statement names the eight cells, and the pair difference is stated by the Rees-stage sizes 5955 and 6139 |
| 5. Checker fails closed | extra-line hole | broken | fixed, see below |
| 6. Scope of A5-587 and A5-588 | holds | holds, one wording defect | fixed: A5-587 says four second runs and one resumed fiber stage |

## Findings and verdicts

| Finding | Source | Verdict | Change |
|---|---|---|---|
| `relations()` matched the header `RELATIONS 148 of 231`, so the text said 149 lines | both | confirmed (`grep -c '^REL '` reads 148) | prefix `REL `, 148 distinct lines required; README and A5-590 corrected |
| A contradicting second certified line still passed | both | confirmed from the predicate | each certified line family must occur exactly once |
| A missing or truncated log raised instead of printing a verdict | both | confirmed | input errors print `verdict: FAIL`; the Hilbert read is bounds-checked |
| Error lines other than `   ? ` passed | Neon | confirmed | any FAIL line, any line beginning `? ` and any line containing `rror` fail |
| `UNIT zero_constant_term_count 0` unchecked | Neon | confirmed | required, once |
| `EXIT 0` not required to be last | Neon | confirmed | required as the last line |
| Auxiliary logs, timing files and the resumed script unread | Neon | confirmed | every file of `sha256.txt` is rehashed by the checker |
| Identical relation lines repeated 148 times would pass | Neon | confirmed | 148 distinct lines required; a rank check as in the v2 checker is not added, since the lines of each pair are compared with a retained log that the v2 checker covers |
| Self-test did not confirm that a variant differs from the good log | Neon | confirmed | checked; seven variants added (fifteen in all) |
| README memory figure of the N- (32009, 21255) modulo run | both | confirmed (704732 kB) | 705 MB |
| `render_cells.py` treated an unknown option as `--check` | Neon | confirmed | unknown options exit 2 with a usage line |
| "the fiber ideal of a cell depends on the product" overreaches | Neon | confirmed | wording limited to the eight cells |
| "about 170 other lines" suggests more difference than the logs carry | Neon | confirmed in part: most differing lines are warnings and timers | replaced by the Rees-stage sizes |
| Missing map row in the program README | Neon | refuted: the map row `runs/` covers one directory per run | none |
| Auxiliary logs lack banner, script digest and `EXIT` lines | Neon | boundary: those runs are experiments bound by `sha256.txt`; the certificates rest on the full runs | none |
| The resumed fiber script sets `isSB` without checking saturation | Neon | boundary: the basis it reads has the sha256 of the quotient run's saturated basis, whose log holds the saturation certificate | README states the digest equality |
| The six open cells compare L with K built in the same script | Neon | boundary, stated in the scope of A5-587 | none |

## Conjectures recorded as open rows

- A5-591: an explicit conjugation substitution with two sign diagonals carries the N- script data onto the N+ data (Neon). Computed after the round in exact arithmetic (`conjugation/conjugation_map.log`): the identities hold, and the row is certified.
- A5-592: closed forms of the pivot determinant and the unit polynomials (Neon). Computed after the round (`conjugation/closed_forms.log`): every detB and UNIT line of the eight logs matches, and the row is certified at the two primes.
- grok: the Rees-stage size depends on the sign alone (5955 and 6139) and the numbered unit lines agree inside each pair; both are read from the logs and are consistent with A5-591.
