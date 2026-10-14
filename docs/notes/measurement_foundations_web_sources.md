# Documentation and journal records without a retained copy: pulse access, tomography API, early superconducting tomography

## Pages and retrieval

Retrieved 2026-10-14T06:18:30Z with a browser user agent. Each SHA-256 identifies the bytes
served at retrieval; the two journal articles have no arXiv preprint under their titles
(arXiv title search), so their records are Crossref DOI metadata. No PDF of these works is retained.

| Source | URL | SHA-256 of retrieved bytes | Cited for |
|---|---|---|---|
| IBM Quantum Compute Service changelog | https://quantum.cloud.ibm.com/docs/en/guides/changelog-quantum-compute-service | `31f496b6577a18272b9676d43f64a809a229b5f085247aec965ceb62234da1c2` | [P] Entry of 3 February 2025: "Pulse-level control on all IBM Quantum processors has been removed"; the pulse module was scheduled for removal in Qiskit SDK v2.0, and fractional gates in the ISA replace it. |
| Qiskit Experiments 0.14.2, `StateTomography` API | https://qiskit-community.github.io/qiskit-experiments/stubs/qiskit_experiments.library.tomography.StateTomography.html | `4a6c21f6d31ff7e1ef9d3e64d2ccc6ed4645774fcc27be1b4e544c7ffcbf2abf` | [P] `measurement_indices` selects the measured qubits, `basis_indices` generates partial tomography data, and `conditional_circuit_clbits` returns reconstructed state components conditional on the values of the named clbits. |
| Qiskit Experiments 0.14.2, state tomography manual | https://qiskit-community.github.io/qiskit-experiments/manuals/verification/state_tomography.html | `217fa1cbb9ec3a56a73134bb645e82f1e40bbcb41f4a5dc4ff5acebf16fde7da` | [P] State tomography measures repeated preparations in a tomographically complete basis; `ParallelExperiment` runs subsystem tomography on several qubits at once. |
| Steffen et al. 2006, Science 313(5792), 1423-1425, DOI 10.1126/science.1130886 | https://api.crossref.org/works/10.1126/science.1130886 | `c773b969297e806358ff05e9dd61669858ffdbf8975d70125fdfe893bd1dda01` | Bibliographic identity: "Measurement of the Entanglement of Two Superconducting Qubits via State Tomography", Steffen, Ansmann, Bialczak, Katz, Lucero, McDermott, Neeley, Weig, Cleland, Martinis, published 2006-09-08. |
| Hofheinz et al. 2009, Nature 459(7246), 546-549, DOI 10.1038/nature08005 | https://api.crossref.org/works/10.1038/nature08005 | `79f3782cdcfddeae32dfafd45f704df64a1cd01c0ef1472b9c299c5185e591a6` | Bibliographic identity: "Synthesizing arbitrary quantum states in a superconducting resonator", Hofheinz, Wang, Ansmann, Bialczak, Lucero, Neeley, O'Connell, Sank, Wenner, Martinis, Cleland, May 2009. |

## Mapping to this repository

- [I] The pulse removal fixes the hardware boundary: continuous-record trajectories ([1305.7270](1305.7270.md)) and resonator Wigner tomography (Hofheinz 2009, [0909.4585](0909.4585.md)) do not transfer to the cloud gate set, while gate-level selected-coherence measurement does.
- [I] `conditional_circuit_clbits` reconstructs the branch states `rho_b` that the branch-signed coherence `C = sum_b p_b (-1)^b <01|rho_b|10>` weights. The selected-coherence design reads that one element with the four Pauli settings XX, XY, YX, YY plus ZZ for populations: five settings per context where conditional two-qubit tomography needs nine.
- [I] Steffen et al. and Hofheinz et al. are cited as the early superconducting density-matrix and phase-sensitive reconstructions; the repository relies on no content beyond their bibliographic identity.

## Boundaries

[I] Changelog and API pages read for the quoted statements; the two journal articles at the metadata level only.
