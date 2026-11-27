# Matrix multiplication: the theoretical floor, the measured floor, and what each changes here

The exponent of matrix multiplication sets how the cost of an n x n product grows with n. Two results of October and
November 2026 move its theory; neither changes the cost of any computation this repository runs, and the measured
floor below is the number to plan with.

## Theory (status 2026-11-27)

| Statement | Status | Source |
|---|---|---|
| omega <= 9/4 over every field | proved several times independently; one Lean formalization (`omega_le_nine_quarters`, not built here) | Dogan, Lysikov, Sakabe, Walter, arXiv:2611.09716v1, Thm 6.3 (fractional symmetrized tensor value); Pass, arXiv:2610.28627v2, Thm 1.1 (explicit polynomial packings, O(n^(9/4+gamma)) integer operations over Q); OpenAI preprints of 2026-10-02 (over C) and the characteristic-free separation step of Lu, arXiv:2610.18914 |
| omega >= 9/4, so omega = 9/4 exactly; every formal arithmetic circuit (division allowed) needs at least ceil(n^(9/4)/2) nonscalar gates | claimed, unreviewed; no independent verification found | OpenAI, "The matrix multiplication exponent is nine fourths" (2026-11-24, 108 pp., github.com/openai/math, preprints/), Thm 1.1 and Cor. 1.2; its Lean development covers division-free circuits per its README, narrower than the stated theorem |
| Previous lower bounds | proved | Blaser: rank >= (5/2) n^2 - 3n; Landsberg: 3 n^2 - o(n^2) over C; Landsberg-Michalek: border rank >= 2 n^2 - ceil(log2 n) - 1 (as cited in the OpenAI preprint, section 1.5) |

Every upper-bound construction is galactic. Pass states that its constants are enormous and gives no crossover size; the
exponent of his (c+2)-for-c gadget reaches 2.367 only at c = 10 and 2.2511 at c = 1000. No paper gives a new explicit
decomposition of a small format (2 x 2 x 2 to 8 x 8 x 8) or an algorithm usable below n = 10^4. omega is an infimum
over tensor powers, so no finite n attains 9/4; the claimed gate bound n^(9/4)/2 first exceeds Blaser's (5/2) n^2 - 3n at
n = 621.

The papers were read in a session of 2026-11-27 (Dogan et al. and the Chen verification note in full, Pass to page 8,
the OpenAI November preprint to page 12 of 108); the 108-page lower-bound proof (Parts I to IV) is unread.

## Measured floor (the number to plan with)

Measured 2026-11-27 on the Windows compute workstation (AMD Ryzen 9 7945HX, WSL), one thread
(OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1), python-flint 0.9.0 `nmod_mat` modulo 32009 and numpy 2.5.4 float64,
one run per size:

| n | product mod p (s) | rank mod p (s) | float64 GEMM (s) |
|---|---|---|---|
| 256 | 0.0047 | 0.0021 | 0.0008 |
| 512 | 0.034 | 0.018 | 0.0065 |
| 1024 | 0.26 | 0.14 | 0.055 |
| 2048 | 1.98 | 0.94 | 0.33 |

Fitted exponents over n = 256 to 2048: 2.905 (product mod p), 2.941 (rank mod p), 2.887 (float GEMM). These sit at
the cubic algorithm with cache effects; FLINT's Strassen-type crossovers do not bring the observed exponent near 2.81 at
these sizes, and nothing at 9/4 is implementable.

## What this changes in the A_5 program

- The linear algebra of the A_5 work is small: left-multiplication matrices are 32 x 32 (64 x 64 in real form), and a
  rank modulo p of such a matrix costs well under a millisecond. Matrix multiplication is not a bottleneck anywhere in
  the fiber program; the cost sits in Groebner bases, saturations and radicals ([computer-algebra](../../runbooks/computer-algebra.md)).
  A faster matrix product would not shorten FC-029 or any Singular run.
- Large exact ranks (the census ranks of MATH-88 and the A_6 runs) sit at n in the thousands, where the measured
  exponent near 2.9 and the GL_3(F_2) orbit reduction of MATH-88 decide the cost; the 9/4 bound does not.
- Transferable tool, open: the fractional symmetrized tensor value V_tau of Dogan et al. (Corollary 4.9) bounds the
  asymptotic rank of any tensor, so it applies to the structure tensor of A_n, a twisted group algebra of Z_2^n with a
  non-bilinear cocycle (ledger A5-648). No paper treats a twisted group algebra; the flattening rank 2^n is the trivial
  lower bound, and C (x) H = M_2(C) makes the complexified quaternion product the 2 x 2 matrix product (rank 7).
  Computing V_tau or the border rank of the octonion and sedenion structure tensors is a candidate question with a
  falsifier: a decomposition below the bound it predicts.
- Circuits: the shortcut that matters on hardware is structural, not asymptotic: the kernel map of a two-term operand
  reads its nullity exactly on a 2 to 4 qubit coset block (draft PR 1039, `gororoba_quantum/pathion_complex_block.py`),
  1 to 29 CZ against 125 to 167 for the six-qubit map.
