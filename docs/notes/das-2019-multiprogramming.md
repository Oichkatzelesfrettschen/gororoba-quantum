# Das et al. 2019 -- A Case for Multi-Programming Quantum Computers

## Source copy and license

The [source PDF](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) remains external to the published library.
Its optional personal reading copy is `docs/local_source_cache/das-2019-multiprogramming.pdf`.
The [rights evidence](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) records `LicenseRef-ACM-personal-copy`;
the inspected evidence supplies no general repository rehosting grant.
[SOURCES.json](../SOURCES.json) binds the source bytes, evidence hash and reading scope.

Tag convention: [P] identifies a statement from the paper; [I] identifies a
repository inference or proposed application. Citation and retrieval fields
record bibliographic facts and measurements of the retrieved file.

## Citation and retrieval

- Authors: Poulami Das, Swamit S. Tannu, Prashant J. Nair, Moinuddin Qureshi.
- Venue: MICRO-52 (2019), proceedings pp. 291-303.
- DOI: https://doi.org/10.1145/3352460.3358287
- Direct author-hosted PDF: https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf
- Source index: https://fast.cc.gatech.edu/publications/ links the PDF beside
  the exact title and authors; coauthor https://moin.cc.gatech.edu/ links that
  publication index.
- Publisher PDF: https://dl.acm.org/doi/pdf/10.1145/3352460.3358287 returned
  HTTP 403 HTML during retrieval; the author-hosted URL returned HTTP 200 PDF.
- Optional local ignored cache: `docs/local_source_cache/das-2019-multiprogramming.pdf`.
- Publication status: external-only PDF. [SOURCES.json](../SOURCES.json)
  retains its URL, digest and size; both published checksum inventories
  exclude its bytes. The 11-PDF library count excludes this local copy.
- File: 13 PDF pages; 2,840,791 bytes; `pdfinfo` and `pdftotext` exit 0.
- SHA-256: `78da2c5da829b74c7564ba21e89735c8802a8e16d665c4102caf2ace2fb6950a`.
- Rights: the first page permits personal/classroom copies under its stated
  conditions and reserves redistribution/server posting for permission. Keep
  the PDF in the local ignored cache; publish its links and citation.
  Author-hosted download access establishes reading availability; it does
  not grant permission to republish the file on repository servers.
- Local verification: `docs/verify_sources.py` accepts an absent cache and
  checks the exact PDF bytes against the external record when present.
  The verifier rejects Git-tracked cache files and external-only content
  in the published PDF inventory.
- Reading scope: abstract and citation on PDF p. 1; methodology in Sec. 3
  (pp. 4-5); allocation discussion in Secs. 4.1-4.2 (pp. 5-7); Sec. 5
  scheduling text and Algorithm 2 (p. 8); Secs. 6.1-6.3 and Algorithm 3
  (pp. 9-11); Secs. 7.2-7.3 and conclusion (p. 12). Figures were read through
  their captions and surrounding text; plotted values were not digitized.

## Mechanisms and evidence

[P] The work targets resource underutilization: small reliable programs leave
physical qubits available for another program. The evaluation uses IBM Q16,
three- and four-qubit Bernstein-Vazirani and reversible-gate benchmarks, and
an isolated baseline with 8192 trials on calibration-selected qubits
(Secs. 3.3-3.5). Probability of a successful trial (PST) is the fraction of
shots producing a successful result (Sec. 3.2).

[P] Fair and Reliable Partitioning accounts for connectivity, link error,
measurement error, and each program qubit's usage and interaction pattern.
Physical-qubit utility is degree divided by the sum of incident link errors.
Allocation grows a region from a useful root; the compute-to-measurement
ratio changes the gate/readout tradeoff. A variation-aware SABRE mapping
uses error information for routing. A tolerance check compares shared and
isolated allocations (Sec. 4.2; Algorithms 1 and 3).

[P] Delayed Instruction Scheduling addresses unequal circuit lengths.
Immediate measurement of the shorter program can disturb the longer one;
holding a finished short circuit until the long circuit finishes exposes
the short circuit's state to additional idle decoherence. The proposed
schedule starts the short circuit later so gate execution finishes together
and measurement follows both programs' gates (Sec. 5; Fig. 13).

[P] Adaptive Multi-Programming executes shared trials and additional isolated
trials. Its monitor compares the two output distributions using an entropy
ratio and a similarity metric defined as one minus Hellinger distance.
Accepted distributions can be merged; reliability deterioration can trigger
isolated execution (Sec. 6.1-6.2; Figs. 15-16).

[P] Section 6.3 reports 6% average and 12% maximum PST loss for the evaluated
mode with 4K shared and 4K isolated trials. The abstract reports throughput
and utilization improvements up to 2x. These are evaluated workload results;
Sec. 7.3 makes gains depend on the longest program, reliable-region
availability, architecture, and daily error variation.

## Repository relevance and boundaries

- [I] Calibration-aware IBM compilation: **high**. The allocation, schedule,
  and shared-versus-isolated comparison address the proposed packing policy.
- [I] Cayley-Dickson structure: **none**. The paper provides execution methods;
  the repository's algebraic identities and spectral census need their own
  mathematical evidence.
- [I] Factoring resource estimates: **low**. Scheduling overhead can enter a
  resource model, while the paper supplies neither a factoring construction
  nor an asymptotic resource estimate for order finding.

[I] Circuit packing and schedule alignment are known techniques reproduced.
An auditable implementation and measurement on the repository's exact QPE
or associator endpoints would be a new implementation or measurement.
The paper's small CNOT-era IBM Q16 experiments establish historical evidence;
current Heron calibration, gate basis, scheduler, dynamic-circuit behavior,
and charged execution seconds require their own observations.

[I] The paper's isolated baseline selects the best available qubits. That
comparison measures an overall allocation-and-concurrency policy. A causal
test of companion interference should additionally hold the diagnostic
patch and circuit fixed, then vary companion activity and schedule.
Such a test separates packing interference from placement quality.

[I] The paper's reliability monitor does not establish a general equivalence
test: output entropy alone cannot certify correctness, two noisy executions
can agree, and empirical distances need uncertainty treatment. Repository
admission should use preregistered endpoint tolerances, finite-shot intervals,
and retained joint shot records when correlated replicas matter.

[I] Useful endpoints per charged second is the proposed repository objective.
Account for characterization, isolated references, packing compilation,
execution, shots, and decoding. A throughput gain between quantum execution
policies does not establish computational advantage over a classical method.
Implementation connections and experiment ordering belong in the
[parallel-experiment synthesis](quantum_experiment_parallelism.md).
