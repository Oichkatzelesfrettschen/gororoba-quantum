# Review of the types-and-loci change (pull request 1053)

The change adds [`scripts/a5_pencil_types_and_loci.py`](../../../../scripts/a5_pencil_types_and_loci.py), its record
`types-and-loci.json`, README statements 19 to 23 of [the transition record](../../../evidence/a5-nullity-transitions/README.md)
and ledger rows A5-676 to A5-681. The owner chose one reviewer and two red-teamers; the Advisor reviews last. Head
under review: `f917aa07b`, with the compute workstation's checkout synced to it before the launch. Local paths in the
retained files read `WORKTREE`, `WORKSPACE` and `SCRATCH`.

| Role | Agent | Run |
|---|---|---|
| reviewer | `codex` on gpt-daybreak-blue, high effort, read-only sandbox | [report](reports/report-codex-daybreak-blue.md), [brief](reports/brief-review.md) |
| red team | `agy` on gemini-4-neon-medium | [report](reports/report-agy-neon.md), [brief](reports/brief-redteam.md) |
| red team | `opencode` on opencode-go/hy4-flash-free | [report](reports/report-opencode-hy4-flash-free.md), same brief |

The OpenCode Go weekly window stood at its 79 percent ceiling. `opencode/deepseek-v4.1-flash-free` answered "Free
usage limit reached", and the next free model in the list, `opencode-go/hy4-flash-free`, wrote the report.

## Findings and verdicts

No reviewer refuted a mathematical claim. Each reproduced the record and added checks of its own.

| Finding | Source | Verdict |
|---|---|---|
| The PR body said every claim was predicted before its run; P31 was written after six of its first eight nullities were read | Codex | confirmed; the body gives the chronology per prediction |
| The ledger called computed results `proved` | Codex | confirmed; A5-676, A5-677 and A5-680 read `certified`, and A5-679 splits into the proved real locus and the certified line census A5-681 |
| A5-676 and A5-680 had no real falsifier, and A5-679's covered only the line census | Codex | confirmed; each row names one |
| README sentences without a `require`: VB's e_16 unit, the exact census tally and sample size, the alpha key set, the Singular exponents and ideal dimension, the leading forms of Q and G, the e_10 and e_1 + e_10 comparison | Codex, Neon, opencode | confirmed; each has a `require` (the leading forms and the named lines enter the record) |
| A5-677 said "every point ... with matched bounds" without the dim-0 sampling or the 33 points of the rational route; the fallback caught every `ValueError` | Codex, Neon | confirmed; the statement names the sample and the route, and the fallback catches the int64-bound error alone |
| The check gate calls Singular without `"requires": ["singular"]` | Codex (and this session before the round) | confirmed; added, and the self-test estimate moves from 20 to 40 s after a measured 27 s |
| The type-R control required only "not H", and the off-plane control accepted any `None` | Codex | confirmed; the first requires R, the second requires rank above 4 |
| The sub-Pfaffian loops and the three Schur batches ran serially | Codex | confirmed; both map through `parallel.ordered_map` |
| The proof of Theorem 14.6 runs to page 26, and the Singular phrase stood in rows that use no Singular | Neon | confirmed; fixed |
| The README called P28 held and P25 not run, the same claim | Codex | confirmed; P25, not run in `certificates.json`, is run here as P28 |
| The order-3 derivation: c1 and c2 enter only through F2 and F1 | Neon, opencode, Codex (block-Schur probe) | confirmed by three independent derivations; recorded in A5-680 |
| The two type routes agree on shared points; a second residue of the dim-0 sample finds no other type | Codex (nine points), opencode (residue 1, 180 W8 points) | recorded as reviewer computations |
| J_k at 21 further Case-1 alpha, and its failure in Case 2 | Neon (15), opencode (6) | recorded in A5-678 as reviewer computations, not reproduced |
| The VB second-order criterion on 1,700 further directions | Neon, opencode | recorded in A5-681 as reviewer computations |
| The order-4 term alone leaves the pencil, while total forms of orders 4 to 6 return to it | Neon | recorded in A5-660, A5-680 and the program note (T3) as a lead |
| Conjectures: the Schur complement as U^T P U (Neon); an Sp(2) x Sp(1)-equivariant pair structure (Codex); a graph-kernel route for dim A = 0 (Neon) | Neon, Codex | recorded in the program note; untested here |

Codex's browser left two snapshot files in the workspace root; they went to the trash.
