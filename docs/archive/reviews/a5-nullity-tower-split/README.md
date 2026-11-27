# Review of the second nullity-transition change (pull request 1037)

The change extends [the transition record](../../../evidence/a5-nullity-transitions/README.md) with the tower, the
types of the compression pencil on W8, the pencils at VB and N+-, arcs outside the coordinate lines and the
junction orders (ledger rows A5-657, A5-660 to A5-665). The owner chose two reviewers and two red-teamers; the
Advisor reviewed last. Head under review: `7a688b9ad`. Every reviewer read one brief
([reviewer](reports/brief-review.md), [red team](reports/brief-redteam.md)) that forbade computation on the host,
so each finding is a reading or a derivation, checked here against the source or by a run on the compute
workstation. Local paths in the retained files read `WORKSPACE`, `WORKTREE` and `WORKTREE-NAME`.

| Role | Agent | Run |
|---|---|---|
| reviewer | `codex` on gpt-daybreak-blue, high effort | [report](reports/report-codex-daybreak-blue.md) |
| reviewer | `opencode` on nemotron-3-ultra-550b (the free Nemotron slug answered "free usage limit reached") | [report](reports/report-opencode-nemotron-3-ultra.md) |
| red team | `agy` on gemini-4-neon-medium (standing session) | [report](reports/report-agy-neon.md) |
| red team | `opencode` on opencode/deepseek-v4.1-flash-free | not run: free usage limit reached |

## Findings and verdicts

| Finding | Source | Verdict |
|---|---|---|
| The VB Pfaffian was factored with the coordinate on e_16 present and over Q only, so its irreducibility does not refute a tangent-cone form on the doubly pure coordinates | Neon, Nemotron; Codex on the scope of A5-657 | confirmed, and the refutation reversed by computation: restricted to the doubly pure coordinates the Pfaffian equals -\|lead Q\|^2 \|lead G\|^2 (`vb_pfaffian`); A5-657 reads "survives", holding at VB and not computed at N+- |
| A W8 point with ker L_p n ker L_q of dimension 2 would break the two-type rule; scan (e_1 + e_10, lam q) over the two-term zero divisors q | Neon (decisive test) | confirmed by the run: four such W8 points, commutant C, Lie closure su(4); the rule has three types (A5-664), and the prediction of two types is kept as failed |
| The two half-intersections of the kernel are equal for every doubly pure point | Neon, Codex (derivations) | confirmed by hand from the doubling formula; stated in README statement 13 |
| dim A = 4 forces type H; the tower continues as sp(2^(n-4)) with pencil dimension 2^(n-2) - 1 | Neon (derivation) | recorded as an argument (README "Reading", A5-661 basis); the three computed levels and every type-H point of the record agree; no proof assistant has checked it |
| The sample of statement 13 kept one sign pattern per support and every ninth point | Codex, Neon, Nemotron | confirmed; fixed: all 474 representatives are classified, the README names the choice, and `sign-census.json` classifies all 29,232 signed points (2,448 in W8: 1,920 of type R, 528 of type H) |
| Serial loops over independent items (four-term enumeration, pair census, 22 limit certificates) | Neon, Codex | confirmed; fixed with `four_term_chunk`, `zero_pair_chunk`, `zero_line_limit_item`, `split_scan_chunk`, `sign_census_chunk` through `parallel.ordered_map` |
| Serial operator construction and bracket loop inside `structure_item` | Codex | boundary: one call is one item of a pooled map, and a nested map keeps one slot (`parallel.py`); the A_6 item is the longest single item of the record |
| Missing guards: exact cofactors, the N+ split fields, both directions of the XOR witness, Gram 2 I at VB | Neon, Codex | confirmed; fixed in `validate` and the self-test |
| The 160 pair lines of nullity 8 are read at s = 3 only | Neon, Codex, Nemotron | confirmed; the census reads s = 3 and s = 5 and the README and A5-665 name both parameters |
| `sphere_normal` checks the span and not \|n\| = 1 | Nemotron (defect), Neon and Codex (harmless by the Clifford relations) | a `require` on \|n\|^2 = 1 added to the limit item |
| The gate `seconds` field is CPU time | Codex | confirmed; measured 992 CPU seconds for the record, 12 for the self-test, 3,470 for the sign census |
| P P' P = cos^2(theta/2) P needs its derivation | Nemotron; derived by Neon and Codex | the one-line expansion is in the README |
| The Koebisu result is cited from its abstract | Codex, Neon | boundary: the README says "abstract read"; the paper is held in the documents repositories |
| Seed provenance from a QRNG file; `np.linalg` in `sphere_normal`; a Pfaffian sign formula with determinants; a 380-pair loop already pooled | Nemotron | refuted: the script draws no random number, imports no NumPy, expands the Pfaffian along the first index of each subset, and held those loops serial at the reviewed head |
| The gate would time out on a small runner | Nemotron | refuted: `seconds` is an estimate that filters gate selection (ci/AGENTS.md, "Gate cost"), and no workflow runs the gate |

## Advisor

The Advisor reviewed last, on the findings above and the fixed head. Its findings, each confirmed and applied:

| Finding | Resolution |
|---|---|
| README statement 9 and two later sentences still said eight W8 points and two types | statement 9, "Reading" and the program note name ten points and three types |
| Statement 14 said "lines through the point" for an identity computed on lines along the eight doubly pure coordinate units | reworded |
| The scan labels carry dim A and the commutant only, so the closure 15 is required at the two named type-C points | statement 13 says so |
| "su(4)" needs its argument | added: a 15-dimensional subalgebra of the skew operators commuting with C, which form u(4) |
| The point counts overlap (the named C and H points inside the scan, the 474 representatives inside the census) | stated in statement 13 and in A5-664 |
| The post-red-team results rested on one implementation | an implementation that shares no code recomputed type C at the two named points (closure 15, a commutant element with X^2 = -I), the 168-case scan, the VB identity as det B = \|q1\|^4 \|g2\|^4 at 25 rational points, and the nullity tally of the 29,232 census points (3,648 of nullity 8, the sum of the census rows; it rejected a wrong expected count written into its brief) |
| The retained Neon report named the worktree directory | replaced by `WORKTREE-NAME` |
