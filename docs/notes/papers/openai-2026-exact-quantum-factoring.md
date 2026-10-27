# OpenAI 2026 -- Exact quantum factoring over a fixed finite gate set (openai/math family 279)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/Exact-quantum-factoring-over-a-fixed-finite-gate-set-September-25-2026/main.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-279-exact-quantum-factoring.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Printed page numbers equal the
PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README. The
  manuscript is unrefereed.
- Version read: the manuscript dated 25 September 2026, as held at openai/math commit
  `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). A Crossref bibliographic search by title on
  27 October 2026 returned no record.
- Commit-pinned PDF, 24 pages, 388,243 bytes.
- SHA-256: `35e89279253b6c8ae5ae7c941283b4b9de517243564f87e9b323ffeae4a85699`
- Reading scope: pp. 1-4 (introduction, proof strategy, Section 2 with Lemmas 2.1 and 2.2), p. 15 (end of the proof
  of Proposition 4.1) and p. 19 (Lemma 5.3 proof and the proof of Theorem 1.1) in full. Sections 3, 4, 5.1-5.2 and
  Appendix A were read for result labels only.

## Transcribed statements

- [P] Theorem 1.1 (p. 1): a polynomial-time uniform family of polynomial-size quantum circuits outputs the complete
  prime factorization of every `N >= 2` with probability one, over the fixed gate set NOT, CNOT, Toffoli, Hadamard
  and `S = diag(1, i)`, their inverses and their singly controlled versions.
- [P] Model distinctions (pp. 1-2): Shor's algorithm has bounded error; retry-until-success has no polynomial
  worst case; approximating arbitrary-angle rotations does not give probability one over a finite gate set. Mosca
  and Zalka's exact transforms use computed rotations, and Imran's exact order finding takes a supplied multiple of
  the order. The construction's "large polynomial parameters are not intended as practical resource improvements".
- [P] Strategy (pp. 2-3): an order trial whose mass on the true order is a prescribed dyadic rational, built from a
  four-phase step state and controlled modular shifts (related to Cleve, Ekert, Macchiavello and Mosca phase
  kickback and to Lev's four-phase approximation); an auxiliary tree of prime factorizations of `p - 1`, checked by
  the deterministic primality test of Appendix A (adapted from Agrawal, Kayal and Saxena); deferred filters that give
  each transition the same exact retained mass; and a preparation with success probability exactly 1/4.
- [P] Conventions (p. 3): `n = max{128, floor(log2 N) + 1}` and `B = 2^n`. Lemma 2.1 (pp. 3-4) appends a flag equal to
  1 with probability exactly a dyadic `q` using Hadamards and a reversible comparison. Lemma 2.2 (p. 4) replaces
  mid-circuit measurements and classical control by CNOT copies into retained history qubits, with the same output
  distribution and a unitary inverse over the same gate set.
- [P] Size (p. 15): the number of list and order transitions is at most `(2n + 2) n (K + 1) <= 6 n^7 < n^10 = L`.
- [P] Proof of Theorem 1.1 (p. 19): with `psi = V_N |0>` and success projection `Pi`, `||Pi psi||^2 = 1/4` (Lemma
  5.3); the sign flip `I - 2 Pi` followed by `2 |psi><psi| - I` maps `psi` to `2 Pi psi`, of norm one, which lies
  entirely in the success subspace. "No arbitrary-angle rotation or unbounded repetition is involved."

## Formal statement

- [P] [`lean/docs/279.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/279.md)
  links `ComparatorChallenges/ExactQuantumFactoring.lean`. That file defines five primitives, each with an inverse
  flag and a control flag ("a fixed set of 20 gate names, not an unbounded-control or arbitrary-angle gate model"),
  `correctProbability` as the unnormalized Born sum on correct encodings, `Uniform` as a polynomial-time TM2
  generator with finite alphabets that receives only the input length, and `MainTheorem` as one uniform family with
  polynomial qubits and instructions and `correctProbability = 1` for every `N >= 2`. Its JSON names the solution
  module `OAI.Computability.QuantumFactoring.Main` and the axioms `propext`, `Quot.sound` and `Classical.choice`. The
  Lean build and Comparator run were not run here.

## Mapping to this repository

- [I] Gate model. The hybrid Shor path of [hybrid-shor.md](../../design/hybrid-shor.md) runs a semiclassical inverse
  QFT whose classically conditioned phases include angles finer than `pi/2`, on the Heron r2 basis `cz, rz, sx, x`
  with continuous `rz`. The paper's phases stop at `S`, and its exactness is a property of the ideal gate model;
  device noise removes probability one on any hardware.
- [I] Dynamic circuits. Lemma 2.2 is the deferred-measurement principle: the paper's own procedure has the same
  output distribution in its measured and its unitary form. Heron r2 could run the measured form as a dynamic
  circuit with mid-circuit measurement and feed-forward. The statement concerns the paper's construction only; the
  hybrid Shor circuits of this repository are a different algorithm with a different output distribution.
- [I] Resources. With `n >= 128` the transition cap `n^10` exceeds `10^21`, so the construction offers nothing to the
  resource floor of [factoring-notes.md](../../design/factoring-notes.md); Gidney's estimate remains the cost
  reference there.

- [I] Finite ingredient. The [quarter-mass conformance suite](../../design/quantum-experiment-conformance.md)
  implements the ideal one-step amplification identity with two qubits, omitted-stage controls and a matched
  full-target preparation. That finite identity supplies neither the factoring construction nor immunity
  from device error.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: low (a correctness model, not a resource estimate).

## Boundaries

[I] No proof in Sections 3-5 or Appendix A was checked, and the manuscript is unrefereed.
