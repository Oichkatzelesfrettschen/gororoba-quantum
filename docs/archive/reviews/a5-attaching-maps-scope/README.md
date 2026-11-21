# Review of the A5 kernel-attachments plan reconciliation and the first attaching-map scope (PR 967)

Reviewers: codex (gpt-daybreak-blue, high) and grok, on head 3c1c72d86, one brief
(the plan reconciliation, the objects and predictions of sub-step 3a, the homotopy data, the controls and a design
question on what roadmap item 7 needs). The Advisor reviewed last. Fixes landed in 226322b8e.

| Finding | Source | Verdict | Disposition |
|---|---|---|---|
| The nullity-16 remainder ("waits on a characteristic-0 fiber cone") is stale: row 2t and the README decide the real limit sets of `Iso`, `W8` and E8-bar as point sets | codex, grok | confirmed | Fixed: the remainder names the header-slice fibers, the non-reduced E8-bar scheme and the slice identification (`A5-293`, `A5-346`, `A5-449`, `A5-559`, `A5-583`) |
| E8-bar to `VB` is cited to `A5-009`, which governs E8-bar into `N+-` | codex, grok | confirmed | Fixed: `A5-005` in every degree, `A5-315` open in characteristic 0 |
| `c_1` stated as "minus the Pluecker degree", an integer where a surface component needs a class | codex, grok | confirmed | Fixed: `c_1 = -H` componentwise, its evaluation on `H_2` for curve components only |
| The link is identified with the tautological circle bundle before the conical structure is established | codex, grok | confirmed | Fixed: the conical structure (certificate 1) gives the identification, and `kappa` on `L` is homotopic to `phi o p` |
| Rows 2b to 2d are cited as computing the 14 fibers; 2c and 2d are an upper and a lower bound | grok | confirmed | Fixed: rows 2i and 2j-c, with 2l for the real limit sets; 2k-c, 2m and 2q for nullity 16 |
| The plan's compatibility reason omits the open question of composed limits through `B9` and `V` | codex, grok | confirmed | Fixed |
| The plan's reconciliation field still reads unresolved | codex, grok | confirmed | Fixed: verified, with its basis |
| The mutation lowers the rank of `phi` globally, which need not meet a chosen component; no control tests the Euler sign, link homology or `c_1` | codex | confirmed | Fixed: a component-specific rank mutation with an explicit kernel point, a rank-2 quadric mutation, and independent Euler-number, Gysin `H_1(L)` and `c_1` checks |
| "Iterated or weighted blow-ups" for the higher-order rows is unsupported | grok | confirmed | Fixed: those rows need more than one blow-up; their resolution belongs to their sub-step |
| "The Hopf circle bundle" placed on `P^2 -> P^2` rather than on `L -> Lambda` | grok | confirmed | Fixed |
| The local datum is not item 7's input: missing the pullback sphere bundle into `S(K_0)`, variation along the boundary orbit, and coherence of direct and composed specializations | codex, grok (design question) | confirmed | Fixed in scope: the note names the pullback sphere bundle as part of the datum and lists the variation, higher-order rows, nullity-16 rows and coherence as later sub-steps |

| `docs/design/a5-open-tasks-and-compute-scope.md` still shows task 126 doing and 127 to 130 todo, with 130 waiting on 129 | Advisor | confirmed | Fixed: the table carries the reconciled states, and 3a proceeds ahead of the open remainders |
| A reviewer breadcrumb in the program note | Advisor | confirmed | Fixed: removed; this record holds it |
| The producer must certify constant nullity 8 on the punctured germ and label the step to `kappa` homotopic to `phi o p` as inferred | Advisor | confirmed | Fixed in the 3a specification (certificate 0 and the objects paragraph) |

Computed by the reviewers from the recorded generators: the E8-bar to `B9` quadratic part has rank 3 (the `t2, t4`
block has determinant -256), and each multiplicity-2 cone factors into two linear 3-spaces meeting only at 0. These are
reviewer computations; the producer of sub-step 3a certifies them.
