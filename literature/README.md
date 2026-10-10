# Literature notes

One note per paper under notes/. Each note:
- carries the citation, the URL that served the PDF, and its sha256;
- tags every statement as from-paper or inference;
- rates relevance to (a) calibration-aware compilation on IBM hardware,
  (b) Cayley-Dickson structure, and (c) factoring resource estimates.

The PDFs stay local under literature/pdf/, which is git-ignored. The Nature
articles are paywalled, so their notes read the arXiv preprints, which differ
from the version of record. Each of those notes says so at the top.

| note | paper | (a) | (b) | (c) |
|---|---|---|---|---|
| s41567-023-02340-9 | Glick et al., Covariant quantum kernels for data with group structure, Nat. Phys. 20, 479 (2024); preprint arXiv:2105.03406 | medium | low | low |
| 2411.05760 | Deshpande et al., Dynamic parameterized quantum circuits | low | none | none |
| s42254-024-00770-9 | Abbas et al., Challenges and opportunities in quantum optimization, Nat. Rev. Phys. 6, 718 (2024); preprint arXiv:2312.02279 | high | none | low |
| 2501.09702 | Yu et al., Quantum-centric algorithm for sample-based Krylov diagonalization (ibm_fez) | medium | none | none |
| 2507.08088 | Cobos et al., Real-time dynamics in a (2+1)-D gauge theory (ibm_kingston, ibm_marrakesh) | high | none | low |
| 2505.22629 | Chen et al., Disambiguating Pauli noise in quantum computers, PRX Quantum 7, 033045 (2026) | high | none | low |
| 2509.18259 | Pokharel et al., Order from chaos with adaptive circuits on quantum hardware (ibm_fez) | medium | none | low |
| 2505.15917 | Gidney, How to factor 2048 bit RSA integers with less than a million noisy qubits | none | none | high |

No paper contains Cayley-Dickson, octonion, sedenion, zero-divisor, or
nonassociative content. Cayley-Dickson content enters through this repository
alone; gororoba_quantum/FACTORING_NOTES.md carries the factoring analysis.

## Action items against the repository

The notes were written against the dense design B: 224 CZ, P_zd = 0.319. The
structural compile in gororoba_quantum/select_lcu.py supersedes it at 42 to 46
CZ, so the shot and gamma budgets the notes derive from 224 CZ overstate the
cost.

In place in `live_run.py`:
- Live layout scoring from calibration: ESP over gate and readout errors on
  every candidate (2509.18259 d1, s42254 d1).
- Per-run calibration record: backend medians, exclusions, timestamps, chosen
  layouts, and scheduled durations in results/live/ (s41567 d1, 2507.08088 d5,
  2509.18259 d2).
- Backend selection across the three reachable devices from live state
  (s42254 d4).
- Historical comparison through target_history at execution time (2501.09702
  d1).

Open, by task:
- Mirror-circuit ODR, one calibration per witness, at 16,384 or more shots
  (2507.08088 d1-d2).
- Twirling and dynamical decoupling through the client-side Sampler options,
  XpXm or XY4, DD on and off (2507.08088 d4, s41567 d2, s42254 d2).
- Dephased and depolarized null models, plus the uniform-random null
  (2509.18259 d3, 2501.09702 d2).
- A coherence factor exp(-t/T2) in the layout score (2509.18259 d1).
- At least three disjoint layouts per witness, with shot, instance, and layout
  variance separated (2507.08088 d3, 2509.18259 d4).
- Dynamic-circuit capability and feed-forward latency on each backend
  (2411.05760 d4), the precondition for the semiclassical-QFT test in
  FACTORING_NOTES.md.
- PEC: count distinct CZ layers and compute gamma before committing shots. The
  paper's learning settings take 740 to 1340 s at about 1 ms per shot, more
  than the 600 s monthly budget (2505.22629 d1-d5).
- Reproduce Gidney Table 5 at n = 2048 from the Zenodo code, and keep the Eq.
  22 deviation bound as a unit test (2505.15917 d2-d3; not run).
