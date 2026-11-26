# Review record: A_5 null-slice boost algebra

Pull request 1014, branch `a5-null-slice-boost-algebra`. The owner selected one red-team reviewer, `agy` on
`gemini-4-neon-medium` (slug read from `agy models` on 2026-11-26), held as a standing session, and the Advisor
last. Round 1 read the working tree before the first commit; round 2 read the fixed head `d933fccdb`. `git status`
in the worktree was clean after round 2. Each finding below carries the orchestrator's check against the source.

## Round 1 (working tree before the first commit)

| Finding | Class | Check against the source | Verdict |
| --- | --- | --- | --- |
| The claim that the so(n,1) relations fail on every slice of dimension 64 is false: 15 slices pass (time index 49 to 63) | computed | the script's own first full run stopped at the same `require`; `tower_control` lists the 15 rows | survives; resolved in `d933fccdb` (statement 6, `validate`) |
| `--self-test` stops: index 25 is a leaf of the module of e_2, so (1 - K_1) e_25 lies in the kernel at e_1 + e_26 | proved | reproduced; K_1 e_2 = -e_25 in `vector_orbits` | survives; resolved in `d933fccdb` by the support (2, 8, 18, 0); round 2 finds the replacement weaker (below) |
| A control ending in `or True` cannot fail | measured | the line was present | survives; removed in `d933fccdb`; round 2 asks for the control it replaced (below) |
| `tower_item` checks neither the Clifford relations of the space nor the Gram identity; in dimension 64 a slice passes the relations and fails the Gram identity; the scan covers upper-half time axes with the full clean set, not "every axis-aligned slice" | computed | `tower_control` rows of dimension 64: `space_clifford` false on all 30, `disjoint_stars` true on 15 | survives; the checks landed in `d933fccdb`, whose docstring, pull-request body and commit message kept the wording "every axis-aligned slice"; the fix commit corrects the docstring, README and pull-request body, and the message of `d933fccdb` keeps the old wording |
| The mechanism: defects are signed partial permutations, and disjoint stars give the relations | proved (reviewer), computed (record) | `disjoint_stars` equals the vanishing of relation failures on all 51 rows with a clean set | survives; adopted as statement 7. The criterion and its counting argument for dimension 16 are the reviewer's contribution |
| Conjecture: the slice with the seven octonion units as space carries so(7,1) from level 6 on | hypothesis, then computed | `octonion_space_control`: levels 6 and 7 pass | survives; adopted as statement 8 |
| Prior art: Koebisu, arXiv 2608.08232, Theorem 5.3; Biss, Dugger and Isaksen 2008, Lemma 4.4 and Proposition 11.1 | read | orchestrator read page 6 of arXiv 2608.08232v1 (det L_x = N(x)^2 D_14(x)^2) and pages 7 and 19 of arXiv math/0511691v1 (Lemma 4.4; Proposition 11.1, Ann(a, b) = {(x, (ax)b) : x in Ass'[a, b]} for a quaternionic pair of alternative vectors) | survives; the README must cite both (round 2, item 10) |

## Round 2 (head `d933fccdb`)

| # | Finding | Class | Check against the source | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Statement 7 says 44 rows; the record has 51 rows with a clean set (7 + 14 + 30) | measured | counted in `result.json` | survives |
| 2 | The last self-test control compares the Gram operator with 75 I; r^2 + t^2 is 74 at that point, so the control passes for a scalar operator too | computed | 4 + 9 + 36 + 25 = 74 | survives |
| 3 | "Every clean slice has the cubic relation": the two rows with 14 directions carry `cubic_relation: null` | measured | `LIE_SPACE_LIMIT` gates the cubic check | survives |
| 4 | so(14,1) at time index 56 rests on 1274 relations and disjoint stars; no Lie dimension is computed there | measured | `lie_dimension: null` in that row | survives; the README names the relations, and the isomorphism follows from disjoint stars |
| 5 | The Gram identity in tower rows is evaluated at one point | measured | `gram_identity` call in `tower_item` | survives in wording: as a polynomial identity it is equivalent to the Clifford relations (the x_a x_b coefficients of -L_y^2), which `space_clifford` decides; the point evaluation is a second check |
| 6 | The verdict table says the module first appears at A_5, while statement 8 has so(2,1) at A_4 on a two-direction subslice | measured | `family_control` level 4 | survives; the claim holds for full clean slices only |
| 7 | `validate` leaves README statements without a `require`: the nullity-12 rays, trace(K_a K_b) = 0, the common kernel support, H and T = e_2 H, the sign table, eta-nullity of the kernel, the tower fields, the family Clifford flags | measured | read `validate` | survives |
| 8 | Statement 1: "all of nullity 4" needs y nonzero, and adding e_2 or e_8 widens the cone to r^2 + s^2 = t^2 | measured | `invariants.six_with_e2.Q_real` | survives |
| 9 | Proof sketches: the isomorphism needs the Lie dimension 21 (or identical action on the four modules); the conjugate identity uses the Clifford relation L_x^2 = -r^2 I; triviality of the kernel bundle needs the upper bound 4 and the punctured cone | proved | each step read | survives |
| 10 | Self-test controls 1 and 5 to 7 are weaker than they can be: the specification agreement tests three tables, the flipped clock is tested on J^2 alone, and index 0 fails for a trivial reason | measured | read `self_test` | survives |
| 11 | The uniqueness sentence for full clean slices (7 of dimension 32 carry both properties, none of dimensions 16 and 64) | computed | recounted from the rows: 0 of 7, 7 of 14, 0 of 30 | confirmed by the reviewer; no change |

No finding of either round is refuted. The fixes land in one commit after the reviewed head.

## Advisor

The Advisor confirmed every finding of both tables and refuted none, with four adjustments: the scope wording of
round 1 row 4 (above); the pull-request body repeated the count 44; the equivalence of the Gram identity with the
Clifford relations needs the skew tables and J^2 = -I checked on each tower row; the conjugate identity rests on the
two coefficient identities that `conjugate_maps` checks and needs no further step. It added six findings:

| Finding | Check | Resolution |
| --- | --- | --- |
| README sentences rested on pages and records only a delegate had read | the orchestrator read pages 19, 23 and 30 of arXiv 2611.34924v1 (equations 3.39 to 3.45, 3.61 to 3.64, 4.20), the K-theory section of `a5-kernel-bundles` and ledger row A5-037 | equation references kept as read; the two record cross-references reworded to "related" and "open item" |
| Reviewer credit, session chronology and near-verbatim theorem text in a public README | read | moved here; the README states arXiv 2608.08232 Theorem 5.3 and arXiv math/0511691 Proposition 11.1 in its own notation |
| Self-test controls should be pairs: the property holds on the input and fails on a mutant | read `self_test` | nine paired controls; the flipped clock fails the Gram identity, the leaf index 25 fails at a two-axis cone point, all 32 tables are compared with cd_core |
| Hosted checks unread | `tests (core)` failed on `test_a5_findings_ledger`: the new evidence directory had no ledger row; the gate entry lacked `workers` | ledger rows A5-612 to A5-621; `"workers": "all"` and 30 s on the check gate |
| "K_1 e_m .. K_7 e_m" names seven operators where six exist | read | corrected |
| The reviewer ran in auto-approve mode | `git status --short` in all nine workspace repositories after round 2 | clean, except one untracked results directory that predates the session |

## Session chronology

- The first form of the tower claim, "the relations hold in dimension 32 only", was a prediction written into
  `validate`; the first full scan refuted it at dimension 64, and the reviewer found the same refutation
  independently.
- The family predictions for levels 4 and 7, and for the octonion-space slices at levels 6 and 7 (the reviewer's
  conjecture, verified by the reviewer at level 6), were written into the script before their first run and held.
- An informal analysis supplied by the owner stated the Gram identity, the 4, 24, 4 spectrum, the determinant and
  the non-hyperbolicity of the pencil on a three-direction slice, and listed Lorentz equivariance and the
  distinctness of A_5 as open or supporting. Statements 1 and 2 confirm the first group by exact computation;
  statement 5 decides equivariance negatively for every boost; statement 6 refutes distinctness of the cone.
- Prior art cited by the reviewer was read on the page by the orchestrator before entering the README: page 6 of
  arXiv 2608.08232v1 and pages 7 and 19 of arXiv math/0511691v1.

## Validation of the fix commit

Run on the Windows compute workstation under WSL with the pinned interpreter of `ci/build_host_envs.sh`: ruff
format and check and mypy clean; `--out` in 45 s; `--check` matches; `--self-test` passes nine controls in
normal and `-O` modes; `ledger.py --check` clean; `check_markdown_links.py` clean;
`sh ci/pr_checks.sh tests` on the record's test file and `tests/test_a5_findings_ledger.py`: 20 passed.
Earlier runs of this session on the build host: the first commit's record and tests ran there, against the
standing rule that the build host takes no Python batch.

## Advisor, second call (head `c04fcc3e3`)

The Advisor found the head sound and asked for one commit before the hosted review:

| Finding | Check | Resolution |
| --- | --- | --- |
| Gate wiring against `ci/AGENTS.md` | read the grouped-gate rule: a check keeps its own gate when its command carries more than one script invocation; `workers: all` marks a gate that takes the detected allocation | no change: the self-test gate runs the script twice (normal and `-O`), and the check gate drives the process pool, as gates core-694 and core-695 of `scripts/a5_zero_divisor_strata.py` do |
| "42 of 90 fail" and "Lie dimension 36" had no `require`; statement 1 cited a two-coordinate point under "one more coordinate" | read `validate` and the README | two `require` lines added; statement 1 reworded |
| "Instance" of Proposition 11.1 asserted from the statement alone | the record now computes [a, a, b] and [a, b, b] for slice pairs in cd_core (`quaternionic_pair`), with a sedenion pair as the failing control; the paper's doubling convention was not compared | README says "related", with the hypotheses checked |
| The absence of Cayley-Dickson structure in the paper rested on two readers | a case-insensitive search of the filed text-layer transcription for octonion, sedenion, Cayley, zero divisor, nonassociative, Clifford, spinor, twistor, division algebra and Jordan algebra returns 0 lines | kept |
| The pull-request body after its edit | read back: 51 slices, 9 paired controls, the corrected scan wording | the prior-art line now reads "related" for Proposition 11.1 |
| Repository status after the reviewer's third round | `git status --short` in the nine workspace repositories | clean, except the one untracked results directory that predates the session |

## Hosted review (Codex, head `aff943e24`)

One finding, P1: the three covariance systems ran in a serial loop, against the rule that CPU-bound loops over
independent items use `parallel.py`. Check: the loop in `covariance` built and ranked the three systems in
turn. Resolution: `covariance_item` is a module-level worker and `covariance` maps the three systems through
`parallel.ordered_map`; the record's values are unchanged and `--check` matches.

## Integration commit (owner request of 2026-11-26)

The owner asked for the findings to enter the research notes and for the merge. The commit after `55084a4cf` adds
the ledger rows A5-612 to A5-621 with their statuses to `docs/notes/topics/a5-exceptional-fiber-status.md`, a
section with one `hypothesis:` item (nullity fixtures for the kernel map, no provider job proposed) to
`docs/notes/topics/a5-hardware-algebra-synthesis.md`, and one row to `docs/RESEARCH_ROADMAP.md`. None of the three
files is pinned by digest in gororoba-quantum or gororoba-open. The commit changes no script, record or ledger row; it
ran through no second hosted round. The relation of the kernel frame to the open nullity-4 classification A5-389 reads
"related", since the frame does not meet that row's statement.
