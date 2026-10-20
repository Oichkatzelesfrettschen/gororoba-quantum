# Audit: dangling docs references on main (942319f)

## 1. docs/verify_sources.py

Command: python3 -W error docs/verify_sources.py -- exit 0.

Output: Verified 23 published PDFs, 84 external-only PDFs, 67 rights captures (40 external manual-audit records without captures), 4 source archives, 2 PDF aliases, historical identities, and 1488 local links

## 2. Missing relative links and backticked paths on main

Checked against git ls-tree -r main (3209 paths) for AGENTS.md, README.md, gororoba_quantum/AGENTS.md, scripts/AGENTS.md, kaggle_kernel/AGENTS.md, docs/INDEX.md, docs/notes/kaggle/*.md, docs/notes/quantum_inspire/*.md.

| Source | Target | Status |
|---|---|---|
| AGENTS.md:535 | docs/notes/quantum_inspire/README.md | absent on main; carried by docs/quantum-inspire-kbase (ca8e104) |
| AGENTS.md:162 | docs/local_source_cache/ | gitignored by design (.gitignore:30); not dangling |
| docs/INDEX.md:11, 87, 276 | docs/local_source_cache/ | gitignored by design; not dangling |
| docs/notes/kaggle/substrates.md:53 | docs/local/ | gitignored by design (.gitignore:34), untracked build-host guide; not dangling |
| kaggle_kernel/AGENTS.md:19 | docs/local/ | gitignored by design; not dangling |

Only one dangling reference on main: docs/notes/quantum_inspire/README.md (AGENTS.md:535). Its link text is 'docs/notes/quantum_inspire/'. Note that main holds other quantum_inspire files (api/, sdk/, site/ directories, backends.md, cli-reference.md, experiments.md, mcp.md, setup.md, usage.md, requirements-qi.txt).

## 3. Branch carriers

- docs/notes/quantum_inspire/README.md: first added in ca8e104 (quantum-inspire: guide index, durable platform facts, Ry failure message); contained by docs/quantum-inspire-kbase (local and origin).

## 4. docs/notes files on branches, absent from main (diff-filter=A, docs/notes AGENTS.md kaggle_kernel/AGENTS.md)

- sim/atlas-fringe-amplitudes: none. Branch is 4 ahead, 37 behind main; its 46 changed files are modifications (M) and deletions (D) of main files, because it predates the Quantum Inspire docs on main.
- quantum-inspire/tuna17-coupler-zz-map: none. Branch is 50 ahead, 0 behind main; 3 modified files (AGENTS.md, docs/notes/quantum_inspire/experiments.md, usage.md).
- kaggle/substrate-routing-libraries, kaggle/jax-bridge-structure and docs/quantum-inspire-kbase: listed below.

### kaggle/substrate-routing-libraries

- docs/notes/kaggle/interfaces.md: Kaggle interfaces: CLI, kagglesdk, MCP and the web API
- docs/notes/kaggle/libraries.md: Kaggle Python packages
- docs/notes/kaggle/site/competitions-setup.md: Competitions Setup
- docs/notes/kaggle/site/competitions.md: Competitions
- docs/notes/kaggle/site/efficient-gpu-usage.md: Efficient GPU Usage Tips
- docs/notes/kaggle/site/groups.md: Groups
- docs/notes/kaggle/site/organizations.md: Organizations
- docs/notes/kaggle/tpu-research.md: Kaggle TPU access: sources, measured routes and root-cause analysis
- docs/notes/packages/adjacent-algebras.md: Algebras adjacent to the Cayley-Dickson tower
- docs/notes/packages/candidates.md: Candidate packages beyond the qualified set
- docs/notes/packages/clifford.md: clifford 1.5.1
- docs/notes/packages/galgebra.md: galgebra 0.6.0
- docs/notes/packages/interplay.md: Algebra package interplay: where the packages overlap, where they are isolated, and how each enters cd_core
- docs/notes/packages/kingdon.md: kingdon 3.0.0
- docs/notes/packages/manual/README.md: Algebra package manual
- docs/notes/packages/manual/cayley-calculator.md: cayley-calculator(3) -- float Cayley-Dickson numbers to D = 128 with elementary functions and gamma-twisted doublings
- docs/notes/packages/manual/cayley-dickson.md: cayley-dickson(3) -- nested ordered pairs and multiplication tables by doubling
- docs/notes/packages/manual/checks/albert_algebra.py: Entrywise maps on Sage coordinates: (octonion coefficient sign by index, conjugate the slot).
- docs/notes/packages/manual/checks/algebra_interplay.py: Distributions whose tables this file retains; scripts/algebra_package_tables.py pins every one
- docs/notes/packages/manual/checks/interplay_tables.json: <no heading>
- docs/notes/packages/manual/checks/run_examples.py: <no heading>
- docs/notes/packages/manual/checks/sage_albert_table.json: <no heading>
- docs/notes/packages/manual/clifford.md: clifford(3) -- numerical geometric algebra Cl(p, q, r) on numba
- docs/notes/packages/manual/galgebra.md: galgebra(3) -- symbolic geometric algebra and calculus on SymPy
- docs/notes/packages/manual/hypercomplex-algebra.md: hypercomplex-algebra(3) -- string expressions over hypercomplex-engine
- docs/notes/packages/manual/hypercomplex-engine.md: hypercomplex-engine(3) -- basis-sign oracle for standard, split and dual Cayley-Dickson algebras
- docs/notes/packages/manual/hypercomplex.md: hypercomplex(3) -- recursive Cayley-Dickson number classes over any numeric base
- docs/notes/packages/manual/hyprat.md: hyprat(3) -- exact rational Cayley-Dickson numbers with a per-level mu, and Hurwitz integers
- docs/notes/packages/manual/kingdon.md: kingdon(3) -- code-generated geometric algebra over numpy, SymPy, torch or JAX values
- docs/notes/packages/manual/mathdunders.md: mathdunders(3) -- class decorator that keeps arithmetic closed over a numeric subclass
- docs/notes/packages/manual/numpy-quaternion.md: numpy-quaternion(3) -- a compiled quaternion dtype for numpy arrays
- docs/notes/packages/manual/octonion-sedenion.md: octonion-sedenion(3) -- octonions and sedenions doubled over numpy-quaternion
- docs/notes/packages/manual/octonion.md: octonion(3) -- batched PyTorch octonions on a Fano-plane basis
- docs/notes/packages/manual/pyadic.md: pyadic(3) -- finite fields, p-adic numbers and rational reconstruction
- docs/notes/packages/manual/pyoctonion.md: pyoctonion(3) -- scalar octonions doubled over pyquaternion
- docs/notes/packages/manual/pyquaternion.md: pyquaternion(3) -- scalar quaternions for 3D rotation bookkeeping
- docs/notes/packages/manual/python-flint.md: python-flint(3) -- FLINT exact integers, rationals, matrices and ball arithmetic as a backend
- docs/notes/packages/manual/quaternionic.md: quaternionic(3) -- numba-accelerated quaternion arrays as a numpy subclass
- docs/notes/packages/manual/sagemath.md: sagemath(1) -- exact octonion, quaternion, Clifford and Albert algebras in SageMath
- docs/notes/packages/manual/splitoct.md: splitoct(3) -- symbolic split octonions on SymPy
- docs/notes/packages/numpy-quaternion.md: numpy-quaternion 2024.0.13
- docs/notes/packages/octonion-sedenion.md: Octonion-Sedenion 1.0.0
- docs/notes/packages/pyoctonion.md: pyoctonion 3.12
- docs/notes/packages/pyquaternion.md: pyquaternion 0.9.9
- docs/notes/packages/quaternionic.md: quaternionic 1.0.18
- docs/notes/qiskit-ecosystem-install-plan.md: Qiskit ecosystem install plan
- docs/notes/qiskit-ecosystem.md: Qiskit ecosystem audit
- docs/notes/quantum-tools/README.md: Quantum and numerics tools: usage manuals
- docs/notes/quantum-tools/galois.md: galois
- docs/notes/quantum-tools/gpu-arrays.md: torch, cupy, jax (and numba CUDA)
- docs/notes/quantum-tools/ibm-quantum-schemas.md: ibm-quantum-schemas
- docs/notes/quantum-tools/lmfit.md: lmfit
- docs/notes/quantum-tools/mthree.md: mthree
- docs/notes/quantum-tools/numpy-scipy-sympy.md: numpy, scipy, sympy
- docs/notes/quantum-tools/pyzx.md: pyzx
- docs/notes/quantum-tools/qiskit-addon-utils.md: qiskit-addon-utils
- docs/notes/quantum-tools/qiskit-aer.md: qiskit-aer
- docs/notes/quantum-tools/qiskit-experiments.md: qiskit-experiments
- docs/notes/quantum-tools/qiskit-ibm-runtime.md: qiskit-ibm-runtime
- docs/notes/quantum-tools/qiskit-mitigation.md: qiskit-mitigation
- docs/notes/quantum-tools/qiskit-qasm3-import.md: qiskit-qasm3-import and openqasm3
- docs/notes/quantum-tools/qiskit.md: qiskit
- docs/notes/quantum-tools/quimb.md: quimb (with cotengra and autoray)
- docs/notes/quantum-tools/rustworkx.md: rustworkx
- docs/notes/quantum-tools/samplomatic.md: samplomatic
- docs/notes/quantum-tools/stim.md: stim

### kaggle/jax-bridge-structure

- docs/notes/kaggle/interfaces.md: Kaggle interfaces: CLI, kagglesdk, MCP and the web API
- docs/notes/kaggle/jax-bridge-structure-report.md: JAX bridge sweep: export once per structure, rescale CZ stacks, sample parity
- docs/notes/kaggle/libraries.md: Kaggle Python packages
- docs/notes/kaggle/site/competitions-setup.md: Competitions Setup
- docs/notes/kaggle/site/competitions.md: Competitions
- docs/notes/kaggle/site/efficient-gpu-usage.md: Efficient GPU Usage Tips
- docs/notes/kaggle/site/groups.md: Groups
- docs/notes/kaggle/site/organizations.md: Organizations
- docs/notes/kaggle/tpu-research.md: Kaggle TPU access: sources, measured routes and root-cause analysis
- docs/notes/packages/adjacent-algebras.md: Algebras adjacent to the Cayley-Dickson tower
- docs/notes/packages/candidates.md: Candidate packages beyond the qualified set
- docs/notes/packages/clifford.md: clifford 1.5.1
- docs/notes/packages/galgebra.md: galgebra 0.6.0
- docs/notes/packages/interplay.md: Algebra package interplay: where the packages overlap, where they are isolated, and how each enters cd_core
- docs/notes/packages/kingdon.md: kingdon 3.0.0
- docs/notes/packages/manual/README.md: Algebra package manual
- docs/notes/packages/manual/cayley-calculator.md: cayley-calculator(3) -- float Cayley-Dickson numbers to D = 128 with elementary functions and gamma-twisted doublings
- docs/notes/packages/manual/cayley-dickson.md: cayley-dickson(3) -- nested ordered pairs and multiplication tables by doubling
- docs/notes/packages/manual/checks/albert_algebra.py: Entrywise maps on Sage coordinates: (octonion coefficient sign by index, conjugate the slot).
- docs/notes/packages/manual/checks/algebra_interplay.py: Distributions whose tables this file retains; scripts/algebra_package_tables.py pins every one
- docs/notes/packages/manual/checks/interplay_tables.json: <no heading>
- docs/notes/packages/manual/checks/run_examples.py: <no heading>
- docs/notes/packages/manual/checks/sage_albert_table.json: <no heading>
- docs/notes/packages/manual/clifford.md: clifford(3) -- numerical geometric algebra Cl(p, q, r) on numba
- docs/notes/packages/manual/galgebra.md: galgebra(3) -- symbolic geometric algebra and calculus on SymPy
- docs/notes/packages/manual/hypercomplex-algebra.md: hypercomplex-algebra(3) -- string expressions over hypercomplex-engine
- docs/notes/packages/manual/hypercomplex-engine.md: hypercomplex-engine(3) -- basis-sign oracle for standard, split and dual Cayley-Dickson algebras
- docs/notes/packages/manual/hypercomplex.md: hypercomplex(3) -- recursive Cayley-Dickson number classes over any numeric base
- docs/notes/packages/manual/hyprat.md: hyprat(3) -- exact rational Cayley-Dickson numbers with a per-level mu, and Hurwitz integers
- docs/notes/packages/manual/kingdon.md: kingdon(3) -- code-generated geometric algebra over numpy, SymPy, torch or JAX values
- docs/notes/packages/manual/mathdunders.md: mathdunders(3) -- class decorator that keeps arithmetic closed over a numeric subclass
- docs/notes/packages/manual/numpy-quaternion.md: numpy-quaternion(3) -- a compiled quaternion dtype for numpy arrays
- docs/notes/packages/manual/octonion-sedenion.md: octonion-sedenion(3) -- octonions and sedenions doubled over numpy-quaternion
- docs/notes/packages/manual/octonion.md: octonion(3) -- batched PyTorch octonions on a Fano-plane basis
- docs/notes/packages/manual/pyadic.md: pyadic(3) -- finite fields, p-adic numbers and rational reconstruction
- docs/notes/packages/manual/pyoctonion.md: pyoctonion(3) -- scalar octonions doubled over pyquaternion
- docs/notes/packages/manual/pyquaternion.md: pyquaternion(3) -- scalar quaternions for 3D rotation bookkeeping
- docs/notes/packages/manual/python-flint.md: python-flint(3) -- FLINT exact integers, rationals, matrices and ball arithmetic as a backend
- docs/notes/packages/manual/quaternionic.md: quaternionic(3) -- numba-accelerated quaternion arrays as a numpy subclass
- docs/notes/packages/manual/sagemath.md: sagemath(1) -- exact octonion, quaternion, Clifford and Albert algebras in SageMath
- docs/notes/packages/manual/splitoct.md: splitoct(3) -- symbolic split octonions on SymPy
- docs/notes/packages/numpy-quaternion.md: numpy-quaternion 2024.0.13
- docs/notes/packages/octonion-sedenion.md: Octonion-Sedenion 1.0.0
- docs/notes/packages/pyoctonion.md: pyoctonion 3.12
- docs/notes/packages/pyquaternion.md: pyquaternion 0.9.9
- docs/notes/packages/quaternionic.md: quaternionic 1.0.18
- docs/notes/qiskit-ecosystem-install-plan.md: Qiskit ecosystem install plan
- docs/notes/qiskit-ecosystem.md: Qiskit ecosystem audit
- docs/notes/quantum-tools/README.md: Quantum and numerics tools: usage manuals
- docs/notes/quantum-tools/galois.md: galois
- docs/notes/quantum-tools/gpu-arrays.md: torch, cupy, jax (and numba CUDA)
- docs/notes/quantum-tools/ibm-quantum-schemas.md: ibm-quantum-schemas
- docs/notes/quantum-tools/lmfit.md: lmfit
- docs/notes/quantum-tools/mthree.md: mthree
- docs/notes/quantum-tools/numpy-scipy-sympy.md: numpy, scipy, sympy
- docs/notes/quantum-tools/pyzx.md: pyzx
- docs/notes/quantum-tools/qiskit-addon-utils.md: qiskit-addon-utils
- docs/notes/quantum-tools/qiskit-aer.md: qiskit-aer
- docs/notes/quantum-tools/qiskit-experiments.md: qiskit-experiments
- docs/notes/quantum-tools/qiskit-ibm-runtime.md: qiskit-ibm-runtime
- docs/notes/quantum-tools/qiskit-mitigation.md: qiskit-mitigation
- docs/notes/quantum-tools/qiskit-qasm3-import.md: qiskit-qasm3-import and openqasm3
- docs/notes/quantum-tools/qiskit.md: qiskit
- docs/notes/quantum-tools/quimb.md: quimb (with cotengra and autoray)
- docs/notes/quantum-tools/rustworkx.md: rustworkx
- docs/notes/quantum-tools/samplomatic.md: samplomatic
- docs/notes/quantum-tools/stim.md: stim

### docs/quantum-inspire-kbase

- docs/notes/quantum_inspire/README.md: Quantum Inspire guides
- docs/notes/quantum_inspire/citing.md: Citing Quantum Inspire
- docs/notes/quantum_inspire/cqasm-spec/MANIFEST.json: <no heading>
- docs/notes/quantum_inspire/cqasm-spec/appendices/spin_2plus.md: Spin-2+
- docs/notes/quantum_inspire/cqasm-spec/index.md: Home
- docs/notes/quantum_inspire/cqasm-spec/introduction/acknowledgements.md: Acknowledgements
- docs/notes/quantum_inspire/cqasm-spec/introduction/context.md: Context
- docs/notes/quantum_inspire/cqasm-spec/introduction/history.md: History
- docs/notes/quantum_inspire/cqasm-spec/language_specification/expressions/builtin_functions.md: Built-in functions
- docs/notes/quantum_inspire/cqasm-spec/language_specification/expressions/indices.md: Indices
- docs/notes/quantum_inspire/cqasm-spec/language_specification/expressions/predefined_constants.md: Predefined constants
- docs/notes/quantum_inspire/cqasm-spec/language_specification/index.md: Language specification
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/assembly_declaration.md: Assembly declaration
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/control_instructions/barrier_instruction.md: Barrier instruction
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/control_instructions/wait_instruction.md: Wait instruction
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/init_instruction.md: Init instruction
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.md: Measure instruction
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.md: Reset instruction
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/single-gate-multiple-qubit-notation.md: Single-gate-multiple-qubit (SGMQ) notation
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/instructions/unitary_instructions.md: Unitary instructions
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/variable_declarations/bit_register_declaration.md: Bit (register) declaration
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/variable_declarations/qubit_register_declaration.md: Qubit (register) declaration
- docs/notes/quantum_inspire/cqasm-spec/language_specification/statements/version_statement.md: Version statement
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/identifiers.md: Identifiers
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/keywords.md: Keywords
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/literals.md: Literals
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/newlines.md: Newlines
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/operators_and_punctuators.md: Operators and punctuators
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/raw_text_string.md: Raw text string
- docs/notes/quantum_inspire/cqasm-spec/language_specification/tokens/whitespace_and_comments.md: Whitespace and comments
- docs/notes/quantum_inspire/cqasm-spec/language_specification/types.md: Types
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/index.md: Standard gate set
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CCX.md: Toffoli gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CNOT.md: Controlled-NOT gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CR.md: Controlled phase shift gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CRk.md: Parametrized controlled phase shift gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CSWAP.md: Fredkin gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CV.md: CV gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CY.md: CY gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_CZ.md: C-Phase gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_DCNOT.md: Double-CNOT gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_ECR.md: Echoed Cross-Resonance gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_ISWAP.md: iSWAP gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.md: Inverse-square-root-SWAP gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_M.md: Magic gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_MS.md: Mølmer-Sørensen gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_SWAP.md: SWAP gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_SqrtISWAP.md: Square-root-iSWAP gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/multi_qubit/mq_SqrtSWAP.md: Square-root-SWAP gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_H.md: Hadamard gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_I.md: Identity gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Rn.md: Rn gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Rx.md: Rx gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Ry.md: Ry gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Rz.md: Rz gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_S.md: S gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Sdag.md: S-dagger gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_T.md: T gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Tdag.md: T-dagger gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_U.md: U gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_X.md: Pauli-X gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_X90.md: X90 gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Y.md: Pauli-Y gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Y90.md: Y90 gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Z.md: Pauli-Z gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_Z90.md: Z90 gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_mX90.md: minus-X90 gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_mY90.md: minus-Y90 gate
- docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/sq_mZ90.md: minus-Z90 gate
- docs/notes/quantum_inspire/cqasm.md: cQASM 3.0 on Quantum Inspire
- docs/notes/quantum_inspire/knowledge-base.md: Quantum Inspire knowledge base digest
- docs/notes/quantum_inspire/platform-facts.md: Quantum Inspire platform facts by source
- docs/notes/quantum_inspire/release-notes.md: Quantum Inspire release digest
- docs/notes/quantum_inspire/releases/MANIFEST.json: <no heading>
- docs/notes/quantum_inspire/releases/OpenQL.json: <no heading>
- docs/notes/quantum_inspire/releases/OpenQL.md: OpenQL releases
- docs/notes/quantum_inspire/releases/OpenSquirrel.json: <no heading>
- docs/notes/quantum_inspire/releases/OpenSquirrel.md: OpenSquirrel releases
- docs/notes/quantum_inspire/releases/cQASM-spec.json: <no heading>
- docs/notes/quantum_inspire/releases/cQASM-spec.md: cQASM-spec releases
- docs/notes/quantum_inspire/releases/libqasm.json: <no heading>
- docs/notes/quantum_inspire/releases/libqasm.md: libqasm releases
- docs/notes/quantum_inspire/releases/pennylane-quantuminspire.json: <no heading>
- docs/notes/quantum_inspire/releases/pennylane-quantuminspire.md: pennylane-quantuminspire releases
- docs/notes/quantum_inspire/releases/qiskit-quantuminspire.json: <no heading>
- docs/notes/quantum_inspire/releases/qiskit-quantuminspire.md: qiskit-quantuminspire releases
- docs/notes/quantum_inspire/releases/quantify-scheduler.json: <no heading>
- docs/notes/quantum_inspire/releases/quantify-scheduler.md: quantify-scheduler releases
- docs/notes/quantum_inspire/releases/quantuminspire.json: <no heading>
- docs/notes/quantum_inspire/releases/quantuminspire.md: quantuminspire releases
- docs/notes/quantum_inspire/releases/qx-simulator.json: <no heading>
- docs/notes/quantum_inspire/releases/qx-simulator.md: qx-simulator releases
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/README.md: PennyLane-QuantumInspire Plugin
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/api/modules.rst: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/contributing.md: Contributing
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/getting_started/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/getting_started/installation.md: Installation and login
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/getting_started/submitting.rst: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/hybrid/basics.md: Basics
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/hybrid/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/hybrid/leveraging_pennylane.md: Leveraging Pennylane
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/hybrid/simple.py: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb: <no heading>
- docs/notes/quantum_inspire/sdk/pennylane-quantuminspire/docs/notebooks/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/README.md: Qiskit Quantum Inspire
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/api/modules.rst: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/contributing.md: Contributing
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/getting_started/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/getting_started/installation.md: Installation and login
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/getting_started/submitting.md: How to: Submit a circuit
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/hybrid/basics.md: Basics
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/hybrid/hqca_circuit.py: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/hybrid/hydrogen.py: (H2) Hydrogen molecuole ground state energy determined using VQE with a UCCSD-ansatz function.
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/hybrid/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/hybrid/leveraging_qiskit.md: Leveraging Qiskit
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/index.rst: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/notebooks/QI2 Performance Test.ipynb: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/notebooks/Super Dense Coding.ipynb: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb: <no heading>
- docs/notes/quantum_inspire/sdk/qiskit-quantuminspire/docs/notebooks/index.rst: <no heading>
- docs/notes/quantum_inspire/site/about-qi.md: About QI
- docs/notes/quantum_inspire/site/backends.md: Chip Overview
- docs/notes/quantum_inspire/site/backends_qx-simulator.md: QX Quantum Computer Simulator
- docs/notes/quantum_inspire/site/contact.md: Contact
- docs/notes/quantum_inspire/site/home.md: The multi hardware Quantum Technology platform
- docs/notes/quantum_inspire/site/kbase.md: Introduction to quantum computing
- docs/notes/quantum_inspire/site/kbase_advanced-guide.md: Introduction advanced guide
- docs/notes/quantum_inspire/site/kbase_bell-states.md: Bell states
- docs/notes/quantum_inspire/site/kbase_bloch-sphere.md: Bloch sphere
- docs/notes/quantum_inspire/site/kbase_code-example-the-maximum-independent-set.md: Code example: the Maximum Independent Set
- docs/notes/quantum_inspire/site/kbase_cqasm-binary-controlled-gates.md: cQASM: Binary controlled gates
- docs/notes/quantum_inspire/site/kbase_cqasm-error-models.md: cQASM: Error models
- docs/notes/quantum_inspire/site/kbase_cqasm-qubit-initialization-and-measurement.md: cQASM: Qubit initialization and measurement
- docs/notes/quantum_inspire/site/kbase_creating-a-new-project.md: Creating a new project
- docs/notes/quantum_inspire/site/kbase_deutsch-jozsa-algorithm.md: Code example: Deutsch-Jozsa algorithm
- docs/notes/quantum_inspire/site/kbase_full-adder.md: Code example: Quantum full adder
- docs/notes/quantum_inspire/site/kbase_grover-algorithm.md: Code example: Grover's algorithm
- docs/notes/quantum_inspire/site/kbase_hello-quantum-world.md: Hello quantum world
- docs/notes/quantum_inspire/site/kbase_introduction-to-quantum-computing.md: The basics of Quantum Computing
- docs/notes/quantum_inspire/site/kbase_libket.md: LibKet
- docs/notes/quantum_inspire/site/kbase_measure-all.md: Measure_all
- docs/notes/quantum_inspire/site/kbase_measure-x.md: Measure_x
- docs/notes/quantum_inspire/site/kbase_measure-y.md: Measure_y
- docs/notes/quantum_inspire/site/kbase_measure.md: Measure
- docs/notes/quantum_inspire/site/kbase_number-of-shots.md: Number of shots
- docs/notes/quantum_inspire/site/kbase_optimization-of-simulations.md: Optimization of simulations
- docs/notes/quantum_inspire/site/kbase_prep-x.md: Prep_x
- docs/notes/quantum_inspire/site/kbase_prep-y.md: Prep_y
- docs/notes/quantum_inspire/site/kbase_prep-z.md: Prep_z
- docs/notes/quantum_inspire/site/kbase_quantum-classification.md: Code example: Quantum classification
- docs/notes/quantum_inspire/site/kbase_qubit-basis-states.md: Qubit basis states
- docs/notes/quantum_inspire/site/kbase_quick-guide.md: Introduction quick guide
- docs/notes/quantum_inspire/site/kbase_repetition-code.md: Code example: Repetition code
- docs/notes/quantum_inspire/site/kbase_superposition-and-entanglement.md: Superposition and entanglement
- docs/notes/quantum_inspire/site/kbase_three-qubit-gates.md: Three-qubit gates
- docs/notes/quantum_inspire/site/kbase_what-is-a-quantum-algorithm.md: What is a quantum algorithm?
- docs/notes/quantum_inspire/site/kbase_what-is-a-qubit.md: What is a qubit?
- docs/notes/quantum_inspire/site/kbase_working-with-the-editor.md: Working with the editor
- docs/notes/quantum_inspire/site/partners.md: Partners
- docs/notes/quantum_inspire/site/reference.md: Referring to Quantum Inspire
- docs/notes/quantum_inspire/site/release-notes-old.md: Release notes (Quantum Inspire 1.0)

