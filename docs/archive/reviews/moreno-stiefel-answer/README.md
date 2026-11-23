# Review record: the answer to Moreno's Stiefel question (A_5 yes; A_6 to A_8 no)

Subject: claims a5-stiefel-universal, a5-stiefel-pfaffian-reduction, stiefel-pfaffian-transport-all-n,
a6-stiefel-witness, a6-stiefel-witness-rocq, a6-a8-stiefel-zero-divisor-cone and a7-a8-stiefel-witness, answering
Question 1 of Moreno, math/0512517, Section 5 (p. 25): whether every Stiefel element of A_(n+1) is a zero divisor.
Proof: [a5-stiefel-pfaffian-germs](../../../evidence/a5-stiefel-pfaffian-germs/README.md), Theorem 1; witnesses:
[moreno_stiefel](../../../evidence/moreno_stiefel/README.md) and [stiefel-pfaffian-higher](../../../evidence/stiefel-pfaffian-higher/README.md).

Reviewers (2026-11-22): codex on gpt-daybreak-blue at xhigh as adversarial reviewer; opencode on
opencode-go/deepseek-v4-pro as red-teamer. Each was asked to break the proof step by step and to search for a
counterexample by exact computation. Raw reports stay outside the tree.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, opencode | Every Stiefel element is doubly pure (pure halves force y_0 = y_16 = 0), so no case is missing; Q = 0 on the Stiefel set; the cofactor identities P_j = Q G z_j and Pf A(z, t) = -(z.t) Q G are global identities over Z[z, t], so Q = 0 and G = 0 need no specialization; the transport identity extends from all basis pairs by real bilinearity; rank_R L_y = 2 rank_C A; Pf A = 0 gives complex rank at most 14 and real nullity at least 4. No density or genericity step enters the proof; the square-zero route is a cross-check | Confirmed: proved |
| 2 | codex | Independent exact search: 384 Stiefel elements on a fixed lattice, outside the z_8 = 0 slice, every coordinate slice, G = 0 and the isotropic and Gram-degenerate loci: exact rank 28 for all, rank_C A = 14 for all, no transport mismatch | Confirmed |
| 3 | opencode | Independent exact search: 840 rational Stiefel elements from Cayley and Givens orthogonal columns, all outside every special slice: exact rank 28 for all, none invertible | Confirmed |
| 4 | codex, opencode | A_6 witness: pure halves, orthogonal, squared norms 62, exact rank 64; Rocq kernel-checks N L_v = d I with zero axioms. A_7 and A_8 witnesses: exact ranks 128 and 256. The codimension-2 zero-divisor cone for n = 6, 7, 8 applies the principal ideal theorem correctly | Confirmed: airtight |
| 5 | codex | verification.md said the independent verifier was not retained, while it is | Fixed: the sentence links the retained verifier |
| 6 | codex, opencode | The A_5 proof is exact computation and written argument; its Rocq formalization is owed (claims ledger) | Boundary: open |

Literature: no prior answer is known to the searches recorded in the proof README (2026-10-25 and 2026-11-22);
MathSciNet and Google Scholar remain unsearched.
