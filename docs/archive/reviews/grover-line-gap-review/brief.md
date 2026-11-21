# Brief: what are we not seeing? Gap and question review of the Garnet Grover results against the gororoba records and the math/ proofs

Read first: AGENTS.md, then gororoba-quantum/AGENTS.md and gororoba-math/AGENTS.md. Work read-only: change no file (print your report as your answer); never commit, push, stash, submit to any provider, start a cloud resource, or run a Lean build (lake build is far too slow here; reading .lean sources is fine); spawn no subagents. You may run git, grep, and python3 for small checks under 5 minutes each in a scratch directory only.

Material (all under the workspace root):
- gororoba-quantum (public, main at 6437f2866): the just-merged IQM Garnet case and its analysis. Start with docs/design/iqm-garnet-grover-line-ccz.md (sections Result and Analysis), results/iqm/grover_line_ccz_analysis.json, gororoba_quantum/grover_line_analysis.py, scripts/iqm_grover_line.py, docs/archive/reviews/grover-line-ccz/reconciliation.md. Broader context: docs/INDEX.md, docs/RESEARCH_ROADMAP.md, docs/state/research_state.json (340 claims, 565 acquisitions; scripts/research_state.py --check lists 85 unclaimed acquisitions), docs/design/, docs/notes/, gororoba_quantum/CLAIM_BOUNDARIES.md, scripts/associator_walsh_classes.py, gororoba_quantum/predict.py (associator_phase), gororoba_quantum/cd_core.py.
- gororoba-math: the workspace's machine-checked Lean (lean/GororobaMath) and Rocq (rocq/) proofs about Cayley-Dickson algebras and the quantum records' finite certificates; docs/ and README.md.
- math/: a third-party collection (721 manuscripts, 373 families, Lean library math/lean/OAI with formalization.yaml and docs/). Family 003, the quasi-Riemann hypothesis (zero-free half-plane Re s > 7/8 for every Dirichlet L-function, Lean declaration OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re, lean/docs/003.md and lean/ComparatorChallenges/QuasiRiemannHypothesis.json), is the "Riemann hypothesis Lean proof" the owner means; read its formal statement, its axioms/assumptions and how the comparator checks it.

## Findings under review (each is a claim; justify or falsify it)

1. Line-native 7-CZ CCZ Grover beats an 18-CZ qiskit 2.6.2 compile on Garnet QB20-QB16-QB17: raw +0.0699 (z 12.1), readout-corrected +0.0706 +- 0.0065 (delta method). Measured.
2. Second Grover iteration still gains: +0.044 (101, z 5.1) and +0.043 (011, z 3.8), less than the model's +0.072. Measured.
3. Output noise is close to global depolarizing: corrected Walsh parity ratios by weight 1/2/3 for the line arm are 0.98/0.96/0.98 of the pre-readout model; deeper arms lose 1-6 points more at weight 3 than weight 1. Hamming profile 0.457/0.426/0.117 vs uniform 3/7,3/7,1/7. Measured + inference.
4. Retention is multiplicative per 14-CZ iteration: 0.864 (101) and 0.866 (011); ~0.99 per CZ including single-qubit gates and idle. Measured + inference (only k = 1, 2 exist).
5. Error budget: -ln(lambda) = a n_CZ + b n_prx gives a = 0.0069, b = 0.0023 from two equations with zero residual (generic retains 0.875 of line). Hypothesis: coherent single-qubit error.
6. Cayley-Dickson degree ladder: cd_sign(2^n, m, .) as a phase on n qubits has ANF degree n-1 for every m != 0 (checked dims 8-32), so octonions need CZ, sedenions CCZ, pathions CCCZ; associator phases reach degree 3 first at dimension 32 (360 of 465 pairs). Computed. Claimed consequence: a sedenion sign oracle keeps half its contrast at ~66 CZ on Garnet.
7. Global output noise means hardware Walsh spectra keep shape up to one scalar, which justifies reading associator spectral classes from samples. Inference.

## Questions to answer

- Falsify or justify each finding; name the decisive check and run it if cheap. Look especially for: statistical issues (multiple comparisons, pooling, delta-method validity, overfitting of the 2-parameter error budget, regression to the model), confounds (path choice made on the same calibration, ABBA sufficiency, heralding selection bias, readout matrix from 8 circuits only), and over-reach in finding 6/7.
- What are we not seeing that we should be? Structure in the records, documentation, the proofs, or the math/ collection that bears on these results and that no record connects. Concrete examples to probe: do the gororoba-math proofs already state the degree law of finding 6 (or contradict it)? Is any math/ family (character sums, Walsh/Fourier analysis on F_2^n, Dirichlet characters as phase functions, Boolean degree bounds, zero-free regions) relevant to the oracles we build? What would a Dirichlet-character phase oracle on qubits test, and does the quasi-RH result say anything checkable there or is the connection empty? Say plainly when a connection is empty.
- Which questions are we failing to ask? Name the 5-10 most important unasked questions, each with why it matters, its falsifier and the cheapest test (simulation, proof, or hardware with expected credits).
- Gaps: records that contradict each other, claims without evidence, docs that overstate, proofs that do not cover what the docs say they cover, missing controls. Cite file:line.
- Also audit the quasi-RH formalization honestly: what exactly is proved, under which axioms (check for sorry, axioms, native_decide, the comparator config), and what does it NOT establish (it is not RH).

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each marked proved, computed, measured or hypothesis. Under 220 lines.
