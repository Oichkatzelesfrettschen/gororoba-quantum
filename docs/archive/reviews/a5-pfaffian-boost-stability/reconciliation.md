# Reconciliation: gororoba-quantum PR 996 (boost-derivation stability)

One local red-teamer ran on head bc6b65e34: opencode on `opencode-go/glm-5.3` ([report](review-opencode.md), from
[this brief](brief.md)). A first attempt on `ollama-cloud/glm-5.3` ended with `provider.auth: Unauthorized` and
returned no report. Each finding was checked against the tree.

| Finding | Verdict | Check | Change |
|---|---|---|---|
| F1: `run_stability.sh algebra` regenerates a two-closure script whose sha256 differs from the pin of `alg-p32009.sing` | confirmed | the script passed `alg w8,iso`; the pin is the invocation with no closure list | the algebra path writes `alg-w8-iso-p32009.*`; the README names which invocation the pin and the retained log belong to |
| F2: a rerun strips the `EXIT 0` line of the retained logs and breaks their pins | confirmed | `tail -1 stab-qi.log` reads `EXIT 0`; the run script wrote no such line | the run script appends the exit line and gates on it |
| F3: the status note states A5-603 flatly | confirmed | two sentences of the note | both now name the argument and its identification step |
| F4: `coef` against the squarefree monomial in `cons()` | no defect | the reviewer read the Singular manual entry and the 388 constraint lines, all linear in c | none |
| F5: the degree-bounded reduction is exact | no defect | every ideal is homogeneous | the README and A5-602 now say so |
| F6: the identity control is vacuous (Euler operator); `rotation_moves` 0 for Iso and 2 for W8 agrees with the stabilizer readings | confirmed | 5 P_k for a quintic | the README and A5-602 say so |
| F7: the E8-bar section omits the radicalized germ and the local ring | confirmed | `weight_slice_fiber_relations.py` docstring; the reviewer's example (z1 z2), z1 at (1, 1) | the README lists four open readings with a test each; A5-605 names the local test |
| F8: "the closure equations are those of source_equations" | confirmed as wording | the test uses the ambient cone equations | the README and A5-602 say so |
| F9: pins, gates, totals and the parametrization reproduce | no defect | reviewer's commands | none |
| F10: prediction that the E8-bar pair stabilizer is 15 and the closure stabilizer at least 16 | hypothesis, recorded | the rerun of A5-605 decides it | none |
| N1: boost and scaling span a 2-torus acting on u + v and u - v | restates A5-604 | D(u + v) = u + v, D(u - v) = -(u - v) | none |
| N2: the boost is the one linear supply of the direction A5-414 misses on W8 and Iso | restates A5-604 | | none |
| N3: the coordinate involutions u <-> v and v -> -v exchange X+ and X- and may be the Klein group of A5-032 | hypothesis, not tested | a table lookup against the sweep of A5-032 | none; a row if tested |

The reviewer broke no claim. The local-ring reading of F7 gives the next computation for E8-bar -> VB: stability of
the localized pair at one basepoint of VB decides the boost for all but finitely many values of the parameter,
because the failure locus is closed and invariant under G_2 and the scaling.
