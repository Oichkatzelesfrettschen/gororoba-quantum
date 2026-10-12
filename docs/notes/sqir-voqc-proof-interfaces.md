# SQIR and VOQC: checked circuit semantics and their integration boundary

Primary papers:

- Kesha Hietala, Robert Rand, Shih-Han Hung, Liyi Li, and Michael Hicks,
  *Proving Quantum Programs Correct*, ITP 2021, LIPIcs 193, 21:1-21:19,
  [DOI 10.4230/LIPIcs.ITP.2021.21](https://doi.org/10.4230/LIPIcs.ITP.2021.21).
  [Publisher PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol193-itp2021/LIPIcs.ITP.2021.21/LIPIcs.ITP.2021.21.pdf).
- Kesha Hietala, Robert Rand, Shih-Han Hung, Xiaodi Wu, and Michael Hicks,
  *A Verified Optimizer for Quantum Circuits*, POPL 2021,
  [arXiv:1912.02250v3](https://arxiv.org/abs/1912.02250v3),
  [versioned PDF](https://arxiv.org/pdf/1912.02250v3),
  DOI 10.1145/3434318.

Code inspected at SQIR commit
`134fb942265091baa3e3972f78f72da41827351f`:
[immutable source tree](https://github.com/inQWIRE/SQIR/tree/134fb942265091baa3e3972f78f72da41827351f).
The package metadata identifies SQIR 1.3.2. The paper and current source are
different artifacts; a theorem name below identifies the inspected source,
not an assertion that the 2021 artifact used identical code.

## What the sources establish

[P] SQIR's ideal semantics assigns a complex matrix to a unitary circuit and
a superoperator to a program with measurement and branching. The ITP paper
sections 3.1-3.3 define the gate language, matrix denotation, measurement, and
reset. Section 5.2 gives QFT/QPE definitions and eigenstate-based correctness.

[P] At the pinned commit, `SQIR/UnitarySem.v` defines `uc_eval` and exact
matrix equality `uc_equiv`. The same file separately defines `uc_cong` as
equivalence up to a global phase. `VOQC/Main.v:optimize_preserves_semantics`
requires well-typedness and concludes the list-level up-to-phase relation.
The optimization theorem does not claim exact matrix equality.

[P] `examples/examples/QPE.v:QPE_semantics_simplified` assumes `n>0`, `k>1`,
well-typedness, a well-formed input vector, and an exact eigenvalue whose phase
is representable with `k` bits. Its conclusion identifies the output basis
state and continuing eigenvector. Different hypotheses are needed for the
approximate-phase success bound and for an unknown superposition of eigenstates.

[P] `SQIR/DensitySem.v:c_eval` adds the two post-measurement branches.
`c_equiv` compares the resulting superoperators on well-formed matrices.
Summing branches retains the unconditional output state; the return type does
not itself retain a separately observable classical outcome history.

## Required repository bridge

[I] Use the exact semantics as a candidate target for the N21 permutation
certificate, labeled QPE laws, and ideal reset/feedback programs. A translation
must prove basis and bit ordering, gate parameters, controlled phases,
ancilla initialization/cleanup, layout permutations, and register decoding.
The existing finite Boolean permutation theorem alone omits relative phases.

[I] Preserve a subcircuit's global phase before placing it under coherent
control: a phase that is global for the subcircuit becomes relative between
control branches. The VOQC up-to-phase theorem therefore needs a phase-aware
bridge, correction, or a context theorem for each intended controlled use.

[I] The joint first-bit/terminal-bit experiment requires outcome-indexed maps
or an explicit classical register. Prove that summing those maps agrees with
`c_eval`, while their traces agree with the joint decoder law. An
unconditional density-matrix equality by itself can hide a wrong recorded
branch. Backend delays, noisy measurement instruments, dispatch latency, and
calibration remain separate physical models.

[I] Begin with one small, supported ideal family and a hash-bound generated
certificate. Treat QPY/QASM parsing and the Qiskit transpiler as unverified
front ends until a checked translation or independently checked equivalence
certificate connects their output to the formal program. A larger verified
optimizer does not automatically verify the surrounding toolchain.

## Foundations, compatibility, and reading scope

[P] The POPL paper's section 6, “Trusted Code,” explicitly leaves its
OpenQASM-to-SQIR translator and Coq extraction unverified and trusts selected
OCaml implementations of rational arithmetic, maps, and sets. Current
extraction wrappers require their own audit. Ideal SQIR uses standard-library
real/complex and QuantumLib matrix semantics; each adopted theorem needs its
actual `Print Assumptions` result and independent kernel replay.

[P] The pinned README declares Coq 8.16-8.20 support and QuantumLib 1.7.0;
package metadata gives broader lower bounds, including Coq >=8.16 and
QuantumLib >=1.6.0. Those declarations have different precision. Rocq 9.1.1
compatibility was not tested in this source-reading pass.

Reading scope: ITP pages 1-7 and 15-17; POPL sections 2-4 and the section-6
trusted-code paragraph; pinned README, package/license files, unitary and
density semantics definitions, the named QPE statement, and the optimizer
statement/proof. The pass did not replay or audit every upstream proof.

## Rights and retained versions

The unchanged 19-page Dagstuhl PDF is CC BY 4.0: its first page names all five
authors and the grant. The exact publisher landing page binds the DOI, title,
PDF URL, and license. Preserve its notices and author attribution;
[license](https://creativecommons.org/licenses/by/4.0/).
PDF SHA-256:
`a8f9a9056c03dedbb007190fbfc187f8b69272970d63941a30a13e475e2bab44`.
The publisher landing evidence SHA-256 is
`d28d80166e09b8218d12141d5df1ce9292413178a6861e73e2237ed0ac2bc2b3`.

The inspected VOQC arXiv version exposes the arXiv nonexclusive distribution
grant. Its PDF remains an external reference/personal reading copy pending
separate source-specific redistribution evidence. The pinned SQIR code has
an MIT license. Neither paper inherits that software license.
Rights evidence: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2021.21

[Retained unchanged PDF](../pdf/LIPIcs.ITP.2021.21.pdf).

External VOQC arXiv:1912.02250v3 PDF (https://arxiv.org/pdf/1912.02250v3):
SHA-256 `677fecb0313df458b7b82ed0da22d80327baaa4dc001d37e4f8284a4f52d44c5`; 5,586,016 bytes; 36 PDF pages.

Unchanged source archive: [sqir-134fb94.tar.gz](../source_archives/sqir-134fb94.tar.gz).
Retrieval: https://codeload.github.com/inQWIRE/SQIR/tar.gz/134fb942265091baa3e3972f78f72da41827351f

Archive SHA-256: `596b8e51705ab8339af709a796bad3f41c631e52148e7a9509dfb0f56c515fec`.
