# Operational quantum instruments: source identities and reading scope

The [algebra/device design](../../design/hypercomplex-operator-evidence.md#operational-conjecture-synthesis)
owns the exact models and experiment contracts. This note records primary arXiv identities and abstracts for the
conjecture screen. The retrieval receipts in [SOURCES.json](../../SOURCES.json) bind each response by URL, byte count,
SHA-256 and observation time. Response HTML and paper PDFs remain unretained.

## Identity corrections

- The draft attributed “Cayley-Dickson algebras and quantum circuit synthesis” to
  [2203.01234](https://arxiv.org/abs/2203.01234). The primary page instead identifies
  **Dynamical analysis of logarithmic energy-momentum squared gravity**. The supplied title/identifier pairing is
  refuted at bibliographic identity level; the supplied citation fails to identify the claimed circuit-synthesis source.
- The draft's generic “non-Hermitian dynamics on quantum hardware” novelty claim conflicts with the abstract of
  [1812.05226v1](https://arxiv.org/abs/1812.05226v1), **Observation of parity-time symmetry breaking in a single spin
  system**. The authors report a Hermitian dilation and an experiment in a diamond nitrogen-vacancy centre.
  This is source-reported prior experimental work, rather than a replay of its data or a claim about Heron devices.
- The remaining draft titles (“Hardware-aware error mitigation for superconducting qubits”, “Monitoring quantum
  processors via Prometheus/Grafana”, “Quantum-Inspire performance-improvement campaigns”, and “Quantum-Inspire vs.
  IBM-Quantum: a comparative benchmark”) lack a verified author/version/locator pairing. They remain unverified and
  support no claim in the synthesis.

## Verified arXiv identities

| Source | Authors as identified by the primary page | Relevant abstract-level statement | Boundary |
|---|---|---|---|
| [physics/9712001](https://arxiv.org/abs/physics/9712001), **Real Spectra in Non-Hermitian Hamiltonians Having PT Symmetry** | Carl M. Bender; Stefan Boettcher | Parity-time-symmetric non-Hermitian Hamiltonians and their spectral properties | No blanket implication that every parity-time-symmetric Hamiltonian has a real spectrum; the local two-by-two control is independently checked |
| [quant-ph/0004040v1](https://arxiv.org/abs/quant-ph/0004040v1), **Quantum Zeno Dynamics** | P. Facchi; V. Gorini; G. Marmo; S. Pascazio; E. C. G. Sudarshan | Measurement constraints and evolution within Zeno subspaces | The finite rotation/projector recurrence in the bundle supplies its own derivation; hardware measurement rates remain separate |
| [quant-ph/9604034](https://arxiv.org/abs/quant-ph/9604034), **A Theory of Quantum Error-Correcting Codes** | Emanuel Knill; Raymond Laflamme | Necessary and sufficient recovery conditions for a specified interaction/error model | The retrieved page supplies a PRL 84, 2525-2528 (2000) journal/DOI record; journal identity is unverified here. The finite compression test is checked directly |
| [1110.3234](https://arxiv.org/abs/1110.3234), **Gaussian Quantum Information** | Christian Weedbrook and six coauthors | Gaussian states, operations and measurements for continuous-variable information | A Gaussian simulation or passive interferometer does not qualify a physical squeezing experiment |
| [quant-ph/9707021](https://arxiv.org/abs/quant-ph/9707021), **Fault-tolerant quantum computation by anyons** | A. Yu. Kitaev | Computation using anyonic excitations, transport and fusion measurements in a two-dimensional quantum system | A periodic logical graph alone supplies neither that physical system nor a protection certificate |
| [1812.05226v1](https://arxiv.org/abs/1812.05226v1), **Observation of parity-time symmetry breaking in a single spin system** | Yang Wu and seven coauthors | A Hermitian dilation and a reported single-spin quantum experiment | Abstract-level prior work; experimental data and the full paper body remain unreviewed |

All rows have title, author and abstract reading scope. The arXiv-supplied journal/DOI fields remain source metadata,
rather than independently verified journal identities. The exact circuit and matrix controls import no unchecked
theorem from these abstracts. Paper-body review and experimental reanalysis are separate evidence operations.
