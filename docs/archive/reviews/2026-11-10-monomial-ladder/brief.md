# Brief: gororoba-quantum pull request 818, truncated ranks of the fiber cone without a standard basis

Read first: WORKSPACE/AGENTS.md, then AGENTS.md.
Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no
subagents. You may run git and python3 (python-flint is in the repository interpreter that docs/PYTHON.md names; torch
may be absent); keep each computation under 5 minutes and write scratch files under /tmp only. Draw no random numbers.

Material: the worktree the worktree of branch a5-monomial-ladder on branch a5-monomial-ladder; the
change is `git diff origin/main...HEAD` (one commit). Evidence root: docs/evidence/a5-exceptional-fibers (E); the
files under review are E/monomial-ladder (five scripts, README.md, records/), five ledger rows A5-298 to A5-302 in
E/ledger.tsv and one map row in E/README.md.

Background. For an incidence of nullity strata of left multiplication on the 32-dimensional Cayley-Dickson algebra
A_5, a slice through a base point has ideal I = (G_1..G_s) in its local ring R, and the fiber cone is
F(I) = sum_d I^d / m_R I^d = k[y]/L with K2 the degree-2 part of L, so h_d <= HF(k[y]/K2, d). The scripts embed R in a
power series ring P with maximal ideal n and compute r_N(d) = dim A_d - dim B_d, A_d and B_d the images of I^d and
m_R I^d in P/n^N. The slice parametrization of the same-sign X incidences is E/arcs-x-same (on main).

## Claims under review (each is a claim; justify or falsify it against the source)

1. x_same_ladder.py: the completed local ring of the slice is R = k[[t]] + (a, rho, sig) k[[a, rho, sig, w]],
   t = w^2/(1 + w), and r_N(d) <= h_d for every N. Falsifiers: R is larger or smaller than the image ring; the
   recursion A_d = sum g_j A_(d-1), B_d = sum g_j B_(d-1) with one order less per unit of generator order loses or
   invents elements modulo n^N, so that dim A_d - dim B_d could exceed h_d (the inequality needs
   B_d = image of m_R I^d exactly, and A_d ∩ n^N handled consistently).
2. e8_ladder.py: the same for E8-bar with ring P + P b, b^2 = X (X - s).
3. fast_ladder.py: the float64 batched echelon is exact for p < 2^15 (the docstring's bound: entries below p, products
   below 2^30, sums of fewer than 2^17 terms). Falsifier: a code path where a sum has more terms or a value is not
   reduced before the next product.
4. monomial_probe.py: "every reduced echelon row has one nonzero entry" is equivalent to the truncated space being a
   span of monomials, and the spanning sets it reduces are those of I and m_R I modulo n^N.
5. monomial_model.py computes dim M^d / (w^2, a, rho, sig) M^d for the stated monomial ideal M.
6. README.md tables and ledger rows A5-298 to A5-302 state no more than the records under records/ hold. In
   particular A5-298 (h_7 = 996 certified from r_29 = r_31 = 996 and HF(k[y]/K2, 7) = 996 in E/k2-hilbert.jsonl)
   and A5-299 (h_8 >= 1422).

## Questions to answer

- Is r_N(d) <= h_d proved by the construction, or can truncation make r_N(d) overshoot? Give the argument or a
  counterexample; a small independent recomputation of one cell (for example degree 3 at order 13 on xm-nm) is welcome.
- Defects in code, claims and records, with file:line. CPU-bound loops over independent items that bypass
  gororoba_quantum/parallel.py count as defects under the repository guide.
- Conjectures the evidence suggests and no record states, each with its falsifier and cheapest test.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each
marked proved, computed, measured or hypothesis. Print it as your answer, under 200 lines.
