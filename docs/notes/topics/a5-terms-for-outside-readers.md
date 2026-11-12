# A₅ and nullity: two terms an outside reader maps onto other fields (draft)

Status: draft idea, written by a working session after an outside review read the repository's vocabulary as group
theory and spectral graph theory. Use: a review brief that goes to a reader outside the project opens with the two
definitions of "Concrete response" below. The quantum-algorithm statements follow the ledger of
[a5-exceptional-fibers](../../evidence/a5-exceptional-fibers/ledger.tsv) (row A5-320) and
[quantum-linear-algebra-fit-a5.md](quantum-linear-algebra-fit-a5.md).

Evidence status. Checked against the tree: the four nullities and the equation V(Q) ∪ V(G) of the zero-divisor locus
([a5-zero-divisor-strata](../../evidence/a5-zero-divisor-strata/README.md),
[a5-strata-regularity](../../evidence/a5-strata-regularity/README.md)) and the wording of ledger row A5-320.
hypothesis: everything said about the outside review, whose text is not retained here.

## The collision

The reviewer maps two homonyms from the repository's vocabulary onto unrelated mathematical objects.

| Token in repository | Repository meaning | Reviewer meaning |
|---|---|---|
| A₅ | 5th Cayley-Dickson algebra, 32-dimensional real non-associative algebra | Alternating group Alt(5), order 60 |
| Nullity | Operator nullity η(x) = dim ker(Lₓ) where Lₓ(y) = x · y for x ∈ 𝔸₅ ∖ {0} | Spectral graph nullity η(G) = dim ker(A(G)) of an adjacency matrix |
| Strata | Zero-divisor rank strata in ℙ³¹: loci where rank(Lₓ) ∈ {16, 20, 24, 28} (nullities 16, 12, 8, 4) | Graph families or partition classes with fixed η(G) |
| Quantum connection | Quantum linear algebra survey: the audited HHL/QSVT proposals give no end-to-end speedup for the exact 𝔽ₚ ranks | Non-abelian HSP for Alt(5); [[5, 1, 3]] stabilizer quantum code |
| Algorithms | Computer algebra: Singular standard bases over 𝔽ₚ, exact rational reconstruction over ℚ(i), certified Rocq proofs of nullity doubling | Maslen–Rockmore non-abelian FFT; graph kernelization |

The collision is total: no object, invariant, or method overlaps.

---

## Decomposed findings and required corrections

### Finding 1: A₅ denotes the 5th Cayley-Dickson algebra, not Alt(5)

The repository symbol A₅ names the 32-dimensional real algebra produced by the 5th iteration of the Cayley-Dickson construction (doubling the 16-dimensional sedenions 𝔸₄). It does not denote the alternating group on 5 letters.

**Correction**: Replace every occurrence of "A₅" or "𝔸₅" in the reviewer's analysis with "the 5th Cayley-Dickson algebra" or "the 32-dimensional algebra 𝔸₅". The alternating group Alt(5) does not appear in the repository's mathematical scope.

---

### Finding 2: Nullity denotes operator kernel dimension, not graph spectral multiplicity

The repository uses nullity to mean η(x) = dim ker(Lₓ) where Lₓ : 𝔸₅ → 𝔸₅ is the left-multiplication operator Lₓ(y) = x · y. The zero-divisor locus 𝒵(𝔸₅) = {x ∈ 𝔸₅ ∖ {0} : ∃ y ≠ 0, x y = 0} lies in the doubly pure subspace x₀ = x₁₆ = 0, and under the identification of that subspace with ℂ¹⁵ it is the union V(Q) ∪ V(G) of a quadric and a quartic hypersurface with the origin removed ([a5-zero-divisor-strata](../../evidence/a5-zero-divisor-strata/README.md)). The rank stratification of Lₓ yields strata of nullity 4, 8, 12 and 16 (ranks 28, 24, 20, 16). For sedenions 𝔸₄, non-zero zero-divisors have uniform nullity 4 (rank 12); 𝔸₅ has the four nullities 4, 8, 12 and 16.

**Correction**: The reviewer's spectral graph nullity η(G) = dim ker(A(G)) of an adjacency matrix A(G) is absent from the repository. No graph adjacency matrix appears in the fiber program's computations.

---

### Finding 3: Strata are zero-divisor rank loci in ℙ³¹, not graph families

The repository's strata are the projective loci where rank(Lₓ) takes a fixed value among {16, 20, 24, 28} for x ∈ 𝔸₅. Vanishing minors of the 32 × 32 matrix Lₓ define the closed loci Rₖ of nullity at least k; a stratum is the locally closed set Sₖ = Rₖ ∖ Rₖ₊₄, on which the kernel has constant dimension ([a5-strata-regularity](../../evidence/a5-strata-regularity/README.md)). The kernel bundle 𝒦 → 𝒵ₖ over each stratum and its exceptional fiber limits along rational arcs are the geometric objects under study.

**Correction**: The reviewer's "strata" as graph families or partition classes with fixed spectral nullity do not correspond to any repository object.

---

### Finding 4: The quantum connection is a workload audit of HHL/QSVT proposals, not Alt(5) HSP

The repository document `quantum-linear-algebra-fit-a5.md` surveys quantum linear algebra algorithms (HHL, QSVT, adiabatic QLSS, finite-field reversible circuits) and concludes that the audited proposals establish no end-to-end speedup for the fiber program's exact 𝔽ₚ computations (ledger A5-320). Ordinary inversion of the singular Lₓ is undefined, while natural LCU encodings and exact kernel filters exist; the conclusion concerns this workload and is no general impossibility theorem.

**Correction**: The non-abelian hidden subgroup problem for Alt(5) and the [[5, 1, 3]] stabilizer code are unrelated to the repository's quantum survey.

---

### Finding 5: Algorithms are computer algebra pipelines, not representation-theoretic FFTs

The fiber program's computational stack:
- Singular standard bases over 𝔽ₚ (exact rank, membership, Hilbert functions)
- Exact rational reconstruction over ℚ(i) for characteristic-zero lifts
- Certified Rocq/Coq proofs of unconditional nullity-doubling theorems
- Jet-truncated linear-algebra rank bounds that certify at the K2 count

The Maslen–Rockmore non-abelian FFT for Alt(5) and graph kernelization methods do not appear in the repository.

**Correction**: Replace the reviewer's algorithmic references with the actual pipeline: Singular std, FLINT rank over 𝔽ₚ, rational reconstruction over ℚ(i), Rocq verification.

---

## Concrete response to the reviewer

The reviewer has analyzed a completely different mathematical domain due to two homonyms:

1. **A₅ is not the alternating group**. The repository studies 𝔸₅, the 32-dimensional real non-associative algebra produced by the 5th Cayley-Dickson doubling of the sedenions 𝔸₄.
2. **Nullity is not graph spectrum multiplicity**. The repository studies the kernel dimension of the left-multiplication operator Lₓ : 𝔸₅ → 𝔸₅, Lₓ(y) = x · y.
3. **The concrete geometric objects**:
   - The zero-divisor locus 𝒵(𝔸₅) = {x ∈ 𝔸₅ ∖ {0} : ∃ y ≠ 0, x y = 0}, inside the doubly pure subspace x₀ = x₁₆ = 0 ≅ ℂ¹⁵ the union V(Q) ∪ V(G) of a quadric and a quartic hypersurface, with the origin removed.
   - The rank stratification of Lₓ: for 𝔸₄, non-zero zero-divisors have uniform nullity 4 (rank 12); in 𝔸₅ the nullities are 4, 8, 12, 16 (ranks 28, 24, 20, 16).
   - The kernel bundle 𝒦 → 𝒵ₖ over each stratum and its exceptional fiber limits along rational arcs.
4. **Algorithmic status**:
   - Exact rank and standard basis computations over 𝔽ₚ and ℚ(i) via Gröbner engines (Singular).
   - Formal verification of unconditional nullity-doubling theorems in Rocq/Coq.
   - A workload audit of quantum linear-system proposals: none of the audited ones supplies the exact modular ranks with an end-to-end speedup (ledger A5-320); this is a statement about the audited proposals.