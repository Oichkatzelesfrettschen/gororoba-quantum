# Python libraries in the hypercomplex campaign

The inventory explains 359 distributions over the declared source surfaces.

Each row names a distribution, its scientific or operational role, and the observed host version. The JSON register retains environment pins and import locations separately. A missing host distribution may belong to an isolated provider environment. Current import locations and unresolved roots follow a fresh tracked-source AST scan through the retained normalized module mapping. Historical import locations remain separately recorded.

Execution pins come from requirement locks and the dispatcher's top-level string literals plus referenced runtime pin files. The JSON records each pin's file, line and constant, and hashes every source. Coverage is finite over these named surfaces, not every prose mention or an implicit transitive resolver closure.

CPU, CUDA 11 and CUDA 13 Aer distributions share one simulator engine and exclusively own `qiskit_aer` within an environment. Isolate them; cross-build agreement supplies implementation conformance rather than independent algebra evidence. CUDA 12 Aer remains unused under the retained Python-wheel compatibility decision.

CVXPY models reconstruction constraints; SCS and Clarabel expose conic/PSD capabilities, whereas OSQP solves quadratic programs with linear constraints. Solver selection requires model, status, residual and tolerance qualification. [Retained metadata and source observations](solver-role-grounding.json) bind these roles; the repository's [Quandela stack](../../notes/quandela/python-stack.md) and [ecosystem audit](../../notes/qiskit-ecosystem.md) supply the operational context.

| Distribution | Host observation | Role |
|---|---|---|
| aiohappyeyeballs | 2.7.1 | SDK/environment infrastructure: Environment support dependency |
| aiohttp | 3.14.3 | SDK/environment infrastructure: Environment support dependency |
| aiohttp-retry | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| aiosignal | 1.4.0 | SDK/environment infrastructure: Environment support dependency |
| alabaster | 1.0.0 | SDK/environment infrastructure: A light, configurable Sphinx theme |
| alembic | 1.20.0 | SDK/environment infrastructure: A database migration tool for SQLAlchemy. |
| annotated-doc | 0.0.5 | SDK/environment infrastructure: Environment support dependency |
| annotated-types | 0.8.0 | SDK/environment infrastructure: Reusable constraint types to use with typing.Annotated |
| antlr4-python3-runtime | 4.13.2 | Parser runtime for OpenQASM import. |
| anyio | 4.15.1 | SDK/environment infrastructure: High-level concurrency and networking framework on top of asyncio or Trio |
| ast-serialize | 0.12.1 | SDK/environment infrastructure: Python bindings for mypy AST serialization |
| asteval | 1.0.10 | SDK/environment infrastructure: Safe, minimalistic evaluator of python expression using ast module |
| asttokens | 3.0.2 | SDK/environment infrastructure: Annotate AST trees with source code positions |
| attrs | 26.1.0 | SDK/environment infrastructure: Classes Without Boilerplate |
| autograd | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| autoray | 0.11.0 | Array dispatch for qualified tensor-network backends. |
| babel | 2.18.0 | SDK/environment infrastructure: Internationalization utilities |
| benchpress | separate/unobserved | Documented compiler benchmark alternative; qualification needs the same full-operator oracle. |
| bluequbit | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| build | 1.6.1 | SDK/environment infrastructure: Environment support dependency |
| cayley-calculator | 1.3.1 | Independent multiplication reference; qualify each special function before use. |
| cayley-dickson | 0.1.0 | Independent recursive doubling reference; local reading and checks under its license boundary. |
| certifi | 2026.10.18 | SDK/environment infrastructure: Python package for providing Mozilla's CA Bundle. |
| cffi | 2.1.1 | SDK/environment infrastructure: Foreign Function Interface for Python calling C code. |
| charset-normalizer | 3.5.1 | SDK/environment infrastructure: The Real First Universal Charset Detector. Open, modern and actively maintained alternative to Chardet. |
| cirq-core | separate/unobserved | IQM circuit interface in its isolated stack. |
| clarabel | 0.11.1 | Interior-point conic solver; retained CVXPY interface supports PSD cones. Qualify installed capabilities and the tomography model before selection; not interchangeable with an unconstrained fit. |
| click | 8.5.0 | SDK/environment infrastructure: Composable command line interface toolkit |
| clifford | 1.5.1 | Associative Clifford envelopes and rotor/spinor controls, not octonion multiplication. |
| cloudpickle | 3.1.2 | SDK/environment infrastructure: Pickler class to extend the standard pickle.Pickler functionality |
| coheriq | separate/unobserved | Documented ecosystem alternative outside the maintained IBM execution workflow. |
| colorama | 0.4.6 | SDK/environment infrastructure: Environment support dependency |
| colorlog | 6.10.0 | SDK/environment infrastructure: Add colours to the output of Python's logging module. |
| comm | 0.2.3 | SDK/environment infrastructure: Jupyter Python Comm implementation, for usage in ipykernel, xeus-python etc. |
| contourpy | 1.4.0 | SDK/environment infrastructure: Python library for calculating contours of 2D quadrilateral grids |
| cotengra | 0.8.2 | Contraction planning for tensor-network references. |
| cryptography | 50.0.2 | SDK/environment infrastructure: cryptography is a package which provides cryptographic recipes and primitives to Python developers. |
| cupy | 14.2.0 | Qualified CUDA array and contraction reference path. |
| cuquantum-cu11 | separate/unobserved | CUDA 11 cuQuantum dependency bundle for the isolated Aer GPU wheel; shared simulator engine infrastructure. |
| custatevec-cu13 | separate/unobserved | CUDA 13 cuQuantum statevector primitives loaded by the qualified Aer cuStateVec path; shared simulator infrastructure, not an independent algebra witness. |
| cutensor-cu11 | separate/unobserved | CUDA 11 tensor contraction library beneath cuTensorNet in the qualified Aer GPU runtime. |
| cutensor-cu13 | separate/unobserved | CUDA 13 tensor contraction support beneath cuTensorNet; qualify ABI, device and actual method separately. |
| cutensornet-cu13 | separate/unobserved | CUDA 13 cuQuantum tensor-network contraction library linked by the Aer GPU wheel; linking does not establish a selected simulation method or speedup. |
| cvxpy | 1.9.3 | Convex modeling for constrained Qiskit state/process tomography and reconstruction; PSD, trace and trace-preserving constraints depend on the declared fitter and SDP-compatible solver. Inspect status, residuals and tolerances; supplies neither an exact algebra witness nor device proof. |
| cycler | 0.12.1 | SDK/environment infrastructure: Composable style cycles |
| cython | 3.3.0 | SDK/environment infrastructure: The Cython compiler for writing C extensions in the Python language. |
| cytoolz | 1.1.0 | SDK/environment infrastructure: Cython implementation of Toolz: High performance functional utilities |
| debugpy | separate/unobserved | SDK/environment infrastructure: An implementation of the Debug Adapter Protocol for Python |
| decorator | 5.3.1 | SDK/environment infrastructure: Environment support dependency |
| dill | 0.4.1 | SDK/environment infrastructure: serialize all of Python |
| dimod | separate/unobserved | SDK/environment infrastructure: A shared API for binary quadratic model samplers. |
| distro | 1.9.0 | SDK/environment infrastructure: Environment support dependency |
| docutils | 0.23 | SDK/environment infrastructure: Docutils -- Python Documentation Utilities |
| dual-numbers | separate/unobserved | Documented algebra candidate: R[eps]/eps^2. Decision: **skip**: runtime monkey-patching of built-ins |
| dual-quaternions | separate/unobserved | Documented algebra candidate: dual quaternions (H tensor R[eps]/eps^2) for rigid motions. Decision: **skip**: no table beyond D = 4 |
| duet | separate/unobserved | SDK/environment infrastructure: A simple future-based async library for python. |
| executing | 2.2.1 | SDK/environment infrastructure: Get the currently executing AST node of a frame, and other information |
| exqalibur | 1.4.2 | Compiled photonic simulator and mesh backend; preserve binary distribution constraints. |
| fastjsonschema | 2.21.2 | SDK/environment infrastructure: Fastest Python implementation of JSON schema |
| fonttools | 4.67.0 | SDK/environment infrastructure: Tools to manipulate font files |
| frozenlist | 1.8.0 | SDK/environment infrastructure: Environment support dependency |
| galgebra | 0.6.0 | Symbolic geometric calculus in an associative Clifford algebra. |
| galois | 0.4.11 | Finite-field Fano incidence and binary algebra certificates. |
| geoalg | separate/unobserved | Documented algebra candidate: calculators for quaternions, octonions, sedenions and split "ultronions"; Clifford algebra. Decision: **skip**: reading and cross-checking only, like cayley-dickson |
| gmpy2 | 2.3.2 | Exact integer/rational arithmetic and accelerated symbolic coefficient support. |
| googleapis-common-protos | separate/unobserved | SDK/environment infrastructure: Common protobufs used in Google APIs |
| graphviz | 0.21 | SDK/environment infrastructure: Environment support dependency |
| grpcio | 1.84.0 | SDK/environment infrastructure: HTTP/2-based RPC framework |
| h11 | 0.16.0 | SDK/environment infrastructure: A pure-Python, bring-your-own-I/O implementation of HTTP/1.1 |
| highspy | 1.15.1 | SDK/environment infrastructure: A thin set of pybind11 wrappers to HiGHS |
| httpcore | 1.0.9 | SDK/environment infrastructure: A minimal low-level HTTP client. |
| httpcore2 | 2.13.1 | SDK/environment infrastructure: Environment support dependency |
| httpx | 0.28.1 | SDK/environment infrastructure: The next generation HTTP client. |
| httpx-sse | 0.4.3 | SDK/environment infrastructure: Consume Server-Sent Event (SSE) messages with HTTPX. |
| httpx2 | 2.13.1 | SDK/environment infrastructure: Environment support dependency |
| hypercomplex | 0.3.4 | Independent recursive CD products; Fraction-based exact witnesses. |
| hypercomplex-algebra | 0.2.0.2 | Expression and tensor notation; shares the hypercomplex-engine implementation. |
| hypercomplex-engine | 0.5.0 | Fast basis signs and higher-dimensional finite checks. |
| hyperdual | separate/unobserved | Documented algebra candidate: hyper-dual numbers; quaternions. Decision: **skip**: abandoned |
| hyperreal | separate/unobserved | Documented algebra candidate: a text-indexing search tool, not hyperreal arithmetic. Decision: **skip**: name trap |
| hyprat | 0.2.0 | Exact rational CD coefficients, generalized signs, annihilators and regular representations. |
| ibm-cloud-sdk-core | 3.24.4 | SDK/environment infrastructure: Core library used by SDKs for IBM Cloud Services |
| ibm-platform-services | 0.77.1 | SDK/environment infrastructure: Python client library for IBM Cloud Platform Services |
| ibm-quantum-schemas | 0.12.20260921 | Runtime task and option schema conformance. |
| idna | 3.20 | SDK/environment infrastructure: Internationalized Domain Names in Applications (IDNA) |
| imagesize | 2.0.1 | SDK/environment infrastructure: Get image size from headers (BMP/PNG/JPEG/JPEG2000/GIF/TIFF/SVG/Netpbm/WebP/AVIF/HEIC/HEIF) |
| importlib-metadata | 9.0.1 | SDK/environment infrastructure: Read metadata from Python packages |
| iniconfig | 2.3.0 | SDK/environment infrastructure: brain-dead simple config-ini parsing |
| ipykernel | 7.4.0 | SDK/environment infrastructure: IPython Kernel for Jupyter |
| ipython | 9.17.1 | SDK/environment infrastructure: IPython: Productive Interactive Computing |
| ipython-pygments-lexers | 1.1.1 | SDK/environment infrastructure: Defines a variety of Pygments lexers for highlighting IPython code. |
| iqm-benchmarks | separate/unobserved | IQM characterization experiments; device jobs require approval. |
| iqm-client | separate/unobserved | IQM circuit jobs, native integrations and calibration reads. |
| iqm-data-definitions | separate/unobserved | Common repository for data definitions inside IQM |
| iqm-error-reduction-tools | separate/unobserved | IQM readout/twirling workflow with acquisition accounting. |
| iqm-exa-common | separate/unobserved | Framework for control and measurement of superconducting qubits: common library |
| iqm-pulla | separate/unobserved | IQM circuit-to-pulse compiler, imported as iqm.cpc. |
| iqm-pulse | separate/unobserved | IQM native gate timing and playlist construction. |
| iqm-qaoa | separate/unobserved | Optional optimization examples; not evidence of advantage for the present PDE task. |
| iqm-qubit-selector | separate/unobserved | Calibration-aware IQM layout selection. |
| iqm-station-control-client | separate/unobserved | Python client for communicating with Station Control Service |
| jax | 0.9.0 | Differentiable array candidate; record actual devices rather than assuming GPU/TPU access. |
| jaxga | separate/unobserved | Documented algebra candidate: tensor-framework geometric algebra. Decision: **skip**: no CD content, heavy dependencies |
| jaxlib | 0.9.0.dev0+selfbuilt | SDK/environment infrastructure: XLA library for JAX |
| jedi | 0.20.1 | SDK/environment infrastructure: An autocompletion tool for Python that can be used for text editors. |
| jinja2 | 3.1.6 | SDK/environment infrastructure: A very fast and expressive template engine. |
| joblib | 1.6.0 | SDK/environment infrastructure: Lightweight pipelining with Python functions |
| jsonschema | 4.26.0 | SDK/environment infrastructure: An implementation of JSON Schema validation for Python |
| jsonschema-specifications | 2025.9.1 | SDK/environment infrastructure: The JSON Schema meta-schemas and vocabularies, exposed as a Registry |
| jupyter-cache | separate/unobserved | SDK/environment infrastructure: A defined interface for working with a cache of jupyter notebooks. |
| jupyter-client | 8.10.0 | SDK/environment infrastructure: Jupyter protocol implementation and client libraries |
| jupyter-core | 5.9.1 | SDK/environment infrastructure: Jupyter core package. A base package on which Jupyter projects rely. |
| kingdon | 3.0.0 | Generated symbolic or batched Clifford operators. |
| kiwisolver | 1.5.1 | SDK/environment infrastructure: A fast implementation of the Cassowary constraint solver |
| libqasm | separate/unobserved | cQASM parsing and validation before upload. |
| librt | 0.16.0 | SDK/environment infrastructure: Mypyc runtime library |
| llvmlite | 0.50.0 | SDK/environment infrastructure: lightweight wrapper around basic LLVM functionality |
| lmfit | 1.3.4 | Identifiable device/noise parameter fitting with retained residuals. |
| mako | 1.4.3.dev0 | SDK/environment infrastructure: A super-fast templating language that borrows the best ideas from the existing templating languages. |
| mapomatic | separate/unobserved | Layout-search candidate; admit only against fresh targets and measured layout controls. |
| markdown-it-py | 4.2.0 | SDK/environment infrastructure: Python port of markdown-it. Markdown parsing, done right! |
| markupsafe | 3.0.4 | SDK/environment infrastructure: Safely add untrusted strings to HTML/XML markup. |
| mathdunders | 0.4.2 | Numeric-method plumbing; supplies no independent multiplication evidence. |
| matplotlib | 3.11.2 | Measured plots and static exports with uncertainty and evidence labels. |
| matplotlib-inline | 0.2.2 | SDK/environment infrastructure: Inline Matplotlib backend for Jupyter |
| mcp | 1.29.0 | SDK/environment infrastructure: Model Context Protocol SDK |
| mcp-types | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| mdit-py-plugins | 0.6.1 | SDK/environment infrastructure: Collection of plugins for markdown-it-py |
| mdurl | 0.1.2 | SDK/environment infrastructure: Markdown URL utilities |
| ml-dtypes | 0.6.0 | SDK/environment infrastructure: ml_dtypes is a stand-alone implementation of several NumPy dtype extensions used in machine learning. |
| more-itertools | 11.2.0 | SDK/environment infrastructure: More routines for operating on iterables, beyond itertools |
| mpmath | 1.4.1 | Arbitrary-precision numerical controls; convergence and precision need explicit error budgets. |
| mthree | 3.0.0 | Readout sensitivity analysis with explicit calibration and factorization assumptions. |
| multicomplex | separate/unobserved | Documented algebra candidate: multicomplex numbers C++ extension. Decision: **skip** |
| multidict | 7.0.0 | SDK/environment infrastructure: Environment support dependency |
| mypy | 2.4.0 | Pinned static type gate. |
| mypy-extensions | 1.1.0 | SDK/environment infrastructure: Type system extensions for programs checked with the mypy type checker. |
| myst-nb | separate/unobserved | SDK/environment infrastructure: A Jupyter Notebook Sphinx reader built on top of the MyST markdown parser. |
| myst-parser | 5.1.0 | SDK/environment infrastructure: An extended [CommonMark](https://spec.commonmark.org/) compliant parser, |
| nbclient | 0.11.0 | SDK/environment infrastructure: A client library for executing notebooks. Formerly nbconvert's ExecutePreprocessor. |
| nbformat | 5.11.1 | SDK/environment infrastructure: The Jupyter Notebook format |
| nest-asyncio2 | separate/unobserved | SDK/environment infrastructure: Patch asyncio to allow nested event loops |
| networkx | 3.7 | Graph inspection and independent topology controls. |
| numba | 0.68.0 | Compiled numeric kernels; compilation speed does not change the arithmetic contract. |
| numga | separate/unobserved | Documented algebra candidate: geometric algebra Cl(p,q,r) including degenerate metrics, NumPy, JAX, PyTorch. Decision: **skip**: three Clifford packages already qualified; revisit if a degenerate metric is needed |
| numpy | 2.5.4 | Arrays, paired-channel probabilities and FFT reference arithmetic. |
| numpy-quaternion | 2024.0.13 | Vectorized quaternion fields and products. |
| numpy-typing-compat | separate/unobserved | SDK/environment infrastructure: Static typing compatibility layer for older versions of NumPy |
| nvidia-cublas | separate/unobserved | Pinned CUDA 13 dense GPU linear algebra used by the simulator runtime stack; shared infrastructure. |
| nvidia-cuda-nvrtc | separate/unobserved | Pinned CUDA 13 runtime compilation support in the GPU simulator environment. |
| nvidia-cuda-runtime | separate/unobserved | Pinned CUDA 13 runtime loaded by the repository GPU Aer wheel; verify the driver and device in each execution environment. |
| nvidia-cusolver | separate/unobserved | Pinned CUDA 13 GPU solver library for simulator numerical linear algebra; not a tomography SDP modeling layer. |
| nvidia-cusparse | separate/unobserved | Pinned CUDA 13 sparse GPU linear algebra support in the simulator environment. |
| nvidia-nvjitlink | separate/unobserved | Pinned CUDA 13 device-code JIT linking support; installation establishes neither GPU execution nor a numerical result. |
| oauthlib | 3.3.1 | SDK/environment infrastructure: Environment support dependency |
| octonion | 0.1.0 | PyTorch octonion/Fano batches after the certified signed relabeling. |
| octonion-sedenion | 1.0.0 | Independent product witness over numpy-quaternion; exclude documented mutating functions. |
| openqasm3 | 1.0.1 | OpenQASM syntax and AST support. |
| openquantum-mcp | separate/unobserved | Broker tool transport; tool auto-approval does not replace repository case approval. |
| openquantum-sdk | separate/unobserved | Read-only native credit quotes and approved brokered execution. |
| openquantum-sdk-cirq | separate/unobserved | Cirq Python SDK for Open Quantum |
| openquantum-sdk-pennylane | separate/unobserved | PennyLane Python SDK for Open Quantum |
| openquantum-sdk-qiskit | separate/unobserved | Qiskit adapter for brokered backends; Public upload is a disclosure. |
| openquantum-sdk-qrisp | separate/unobserved | Qrisp Python SDK for Open Quantum |
| opensquirrel | separate/unobserved | Native decomposition and coupling checks; record scheduling limitations. |
| opentelemetry-api | 1.45.1 | SDK/environment infrastructure: OpenTelemetry Python API |
| opentelemetry-exporter-http-transport | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Exporters HTTP transport |
| opentelemetry-exporter-otlp | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Collector Exporters |
| opentelemetry-exporter-otlp-common | separate/unobserved | SDK/environment infrastructure: OpenTelemetry OTLP HTTP export utilities |
| opentelemetry-exporter-otlp-proto-common | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Protobuf encoding |
| opentelemetry-exporter-otlp-proto-grpc | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Collector Protobuf over gRPC Exporter |
| opentelemetry-exporter-otlp-proto-http | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Collector Protobuf over HTTP Exporter |
| opentelemetry-proto | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Python Proto |
| opentelemetry-sdk | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Python SDK |
| opentelemetry-semantic-conventions | separate/unobserved | SDK/environment infrastructure: OpenTelemetry Semantic Conventions |
| opt-einsum | 3.4.0 | SDK/environment infrastructure: Path optimization of einsum functions. |
| optuna | 5.0.0 | SDK/environment infrastructure: A hyperparameter optimization framework |
| optype | separate/unobserved | SDK/environment infrastructure: Building Blocks for Precise & Flexible Type Hints |
| ordered-set | 4.1.0 | SDK/environment infrastructure: An OrderedSet is a custom MutableSet that remembers its order, so that every |
| orjson | 3.13.0 | SDK/environment infrastructure: Fast, correct Python JSON library supporting dataclasses, datetimes, and numpy |
| osqp | 1.1.3 | Operator-splitting convex quadratic-program solver for QPs with linear constraints; not a PSD-constrained tomography SDP solver. Qualify the objective and constraint class before use. |
| packaging | 26.3 | SDK/environment infrastructure: Core utilities for Python packages |
| padic | separate/unobserved | Documented algebra candidate: p-adic intervals `a p^v + O(p^N)`, Hensel roots, log/exp/sin/cos. Decision: **skip**: pyadic covers Fraction input and finite-field work; single-author, 2023 |
| pandas | 2.3.3 | Tabular evidence joins and summaries. |
| parso | 0.8.7 | SDK/environment infrastructure: A Python Parser |
| pathspec | 1.1.1 | SDK/environment infrastructure: Utility library for gitignore style pattern matching of file paths. |
| pauli-prop | separate/unobserved | Documented ecosystem candidate: skip: Pauli propagation for large observables |
| pennylane | separate/unobserved | Documented alternative differentiable circuit stack; not required for current cases. |
| pennylane-quantuminspire | separate/unobserved | Documented optional provider adapter; preserve its separate compatibility caps. |
| perceval-interop | separate/unobserved | Documented converter candidate with Qiskit version constraints. |
| perceval-quandela | 1.3.1 | Photonic meshes, local SLOS/Naive checks and approved Quandela execution. |
| pexpect | 4.9.0 | SDK/environment infrastructure: Pexpect allows easy control of interactive console applications. |
| pillow | 13.0.0 | SDK/environment infrastructure: Python Imaging Library (fork) |
| pip | 26.2.1 | SDK/environment infrastructure: The PyPA recommended tool for installing Python packages. |
| platformdirs | 4.13.0 | SDK/environment infrastructure: A small Python package for determining appropriate platform-specific dirs, e.g. a `user data dir`. |
| playwright | 1.64.0 | SDK/environment infrastructure: Environment support dependency |
| pluggy | 1.7.0 | SDK/environment infrastructure: plugin and hook calling mechanisms for python |
| ply | 3.11 | SDK/environment infrastructure: Python Lex & Yacc |
| prompt-toolkit | 3.0.53 | SDK/environment infrastructure: Library for building powerful interactive command lines in Python |
| propcache | 0.5.4 | SDK/environment infrastructure: Environment support dependency |
| protobuf | 7.36.1 | SDK/environment infrastructure: Runtime dependency |
| psutil | 7.2.2 | SDK/environment infrastructure: Cross-platform lib for process and system monitoring. |
| ptyprocess | 0.7.0 | SDK/environment infrastructure: Run a subprocess in a pseudo terminal |
| pure-eval | 0.2.3 | SDK/environment infrastructure: Safely evaluate AST nodes without side effects |
| pyadic | 0.3.0 | Finite-field and finite-precision p-adic coefficients; a separate arithmetic experiment. |
| pybind11 | 3.1.0 | SDK/environment infrastructure: Environment support dependency |
| pycparser | 3.11 | SDK/environment infrastructure: C parser in Python |
| pycurl | 7.48.0 | SDK/environment infrastructure: PycURL -- A Python Interface To The cURL library |
| pydantic | 2.14.1 | SDK/environment infrastructure: Data validation using Python type hints |
| pydantic-core | 2.50.1 | SDK/environment infrastructure: Core functionality for Pydantic validation and serialization |
| pydantic-settings | 2.16.0 | SDK/environment infrastructure: Settings management using Pydantic |
| pygments | 2.21.0 | SDK/environment infrastructure: Pygments is a syntax highlighting package written in Python. |
| pyjwt | 2.15.1 | SDK/environment infrastructure: JSON Web Token implementation in Python |
| pylatex | separate/unobserved | SDK/environment infrastructure: A Python library for creating LaTeX files and snippets |
| pylatexenc | 2.11 | SDK/environment infrastructure: Simple LaTeX parser providing latex-to-unicode and unicode-to-latex conversion |
| pymatching | separate/unobserved | Error-model decoding when a detector-code experiment requires it. |
| pyoctonion | 3.12 | Small octonion cross-check; depends on pyquaternion. |
| pyparsing | 3.3.3 | SDK/environment infrastructure: pyparsing - Classes and methods to define and execute parsing grammars |
| pyproject-hooks | 1.3.3 | SDK/environment infrastructure: Environment support dependency |
| pyqasm | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| pyqpanda3 | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| pyquafu | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| pyquaternion | 0.9.9 | Scalar quaternion and rotation bookkeeping. |
| pyspnego | 0.12.4 | SDK/environment infrastructure: Windows Negotiate Authentication Client and Server |
| pytest | 9.1.1 | Behavioral regressions and mutation checks. |
| pytest-xdist | 3.8.0 | CPU-budgeted independent test execution. |
| python-dateutil | 2.9.0 | SDK/environment infrastructure: Extensions to the standard Python datetime module |
| python-dotenv | 1.2.4 | SDK/environment infrastructure: Read key-value pairs from a .env file and set them as environment variables |
| python-flint | 0.9.0 | Exact rational/modular matrix rank and kernel certificates; defines no CD table. |
| python-multipart | 0.0.32 | SDK/environment infrastructure: A streaming multipart parser for Python |
| python-rapidjson | separate/unobserved | SDK/environment infrastructure: Python wrapper around rapidjson |
| pyyaml | 6.0.3 | SDK/environment infrastructure: YAML parser and emitter for Python |
| pyzmq | 27.2.0 | SDK/environment infrastructure: Python bindings for 0MQ |
| pyzx | 0.10.7 | ZX circuit simplification followed by exact operator-equivalence checks. |
| qbraid | separate/unobserved | Documented multi-provider SDK alternative; current cases use the repository's guarded clients. |
| qbraid-core | separate/unobserved | Python library with core abstractions for software development in the qBraid ecosystem. |
| qdldl | 0.1.9.post1 | SDK/environment infrastructure: QDLDL, a free LDL factorization routine. |
| qi-compute-api-client | separate/unobserved | Typed Quantum Inspire compute API transport beneath the guarded runner. |
| qiskit | 2.5.2 | Circuits, native synthesis, topology placement and operator verification. |
| qiskit-addon-aqc-tensor | separate/unobserved | Documented ecosystem candidate: skip: approximate quantum compilation with tensor networks; quimb and cotengra already cover contraction |
| qiskit-addon-cutting | separate/unobserved | Documented ecosystem candidate: skip: circuits stay within 14 qubits, so wire cutting has no use |
| qiskit-addon-dice-solver | separate/unobserved | Documented ecosystem candidate: skip: chemistry HPC solvers |
| qiskit-addon-mpf | separate/unobserved | Optional multiproduct-formula Trotter-error reduction using CVXPY. The 2026-10-16 ecosystem audit declined the workflow; host CVXPY availability does not establish its admission. Qualify circuit approximations, solver residuals and error budgets before use. |
| qiskit-addon-obp | separate/unobserved | Documented ecosystem candidate: skip: operator backpropagation targets observable estimation of Trotter circuits |
| qiskit-addon-opt-mapper | separate/unobserved | Documented ecosystem candidate: skip: optimization modeling |
| qiskit-addon-pna | separate/unobserved | Documented ecosystem candidate: skip: global-noise-channel mitigation of observables |
| qiskit-addon-slc | separate/unobserved | Documented ecosystem candidate: skip: PEC overhead reduction; pins pauli-prop below 0.2 |
| qiskit-addon-sqd | separate/unobserved | Documented ecosystem candidate: skip: chemistry configuration recovery, pulls pyscf (not installed) |
| qiskit-addon-sqd-hpc | separate/unobserved | Documented ecosystem candidate: skip: chemistry HPC solvers |
| qiskit-addon-utils | 0.4.0 | Supported circuit interchange and utility operations. |
| qiskit-aer | 0.17.2 | Ideal/noise circuit simulation; provider/routing approval rules apply to submitted jobs. |
| qiskit-aer-gpu | separate/unobserved | CUDA 12 Aer alternative remains unused: retained ecosystem audit records release 0.15.1 without a Python 3.13 wheel; do not coinstall qiskit_aer owners. |
| qiskit-aer-gpu-cu11 | separate/unobserved | CUDA 11 Aer wheel for the isolated Kaggle GPU path; exclusively owns qiskit_aer and shares the CPU/CUDA 13 Aer engine. |
| qiskit-aer-gpu-cu13 | separate/unobserved | Repository-built CUDA 13 Aer wheel for qualified Kaggle GPU simulation; exclusively owns qiskit_aer in that environment and shares the Aer engine, not an independent witness. |
| qiskit-algorithms | separate/unobserved | Documented ecosystem candidate: host only, optional: phase and amplitude estimation references for algebra-circuit cross-checks; no current consumer |
| qiskit-code-assistant-mcp-server | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-device-benchmarking | separate/unobserved | Documented ecosystem candidate: host only: benchmarks that submit to IBM backends; needs an IBM credential |
| qiskit-docs-mcp-server | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-dynamics | separate/unobserved | Continuous-system simulation alternative; the retained note records its archive status. |
| qiskit-experiments | 0.14.2 | Device-characterization circuits and analyses; calibration jobs require approval. |
| qiskit-fermions | separate/unobserved | Documented ecosystem candidate: skip: fermionic systems |
| qiskit-finance | separate/unobserved | Documented ecosystem candidate: skip: finance |
| qiskit-gym | separate/unobserved | Documented ecosystem candidate: skip: reinforcement-learning synthesis |
| qiskit-gym-mcp-server | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-ibm-ai-local-transpiler | separate/unobserved | Documented ecosystem candidate: skip: no consumer in the repository; pins an old networkx |
| qiskit-ibm-catalog | separate/unobserved | Documented ecosystem candidate: skip: Qiskit Functions client, cloud only |
| qiskit-ibm-experiment | separate/unobserved | Documented ecosystem candidate: skip: archived |
| qiskit-ibm-provider | separate/unobserved | Documented ecosystem candidate: skip: replaced by runtime |
| qiskit-ibm-runtime | 0.50.0 | IBM execution and result collection through the approved-record runner. |
| qiskit-ibm-runtime-mcp-server | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-ibm-transpiler | separate/unobserved | Documented ecosystem candidate: skip: cloud AI passes (credential) and a hard conflict with the pin |
| qiskit-ibm-transpiler-mcp-server | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-ionq | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-machine-learning | separate/unobserved | Documented ecosystem candidate: skip |
| qiskit-mcp-servers | separate/unobserved | SDK/environment infrastructure: Environment support dependency |
| qiskit-mitigation | 0.1.1 | Hardware mitigation tasks; invocation can submit and needs the written case. |
| qiskit-nature | separate/unobserved | Documented ecosystem candidate: skip: chemistry |
| qiskit-noise-learning | separate/unobserved | Documented ecosystem candidate: host plus Kaggle candidate via commit-pinned source: randomization-based Pauli noise characterization against the Aer replay; needs samplomatic>=0.21, numpy>=2 |
| qiskit-optimization | separate/unobserved | Documented ecosystem candidate: skip: archived |
| qiskit-paulice | separate/unobserved | Documented ecosystem candidate: skip: spacetime Pauli checks target error detection at scale |
| qiskit-qasm3-import | 0.6.0 | Validated OpenQASM interchange between isolated SDK environments. |
| qiskit-quantuminspire | separate/unobserved | Circuit conversion in the isolated Quantum Inspire environment. |
| qiskit-serverless | separate/unobserved | Documented ecosystem candidate: skip: cloud job client, exceeds Kaggle numpy |
| qrisp | separate/unobserved | IQM high-level circuit/QEC interface in its isolated stack. |
| quantuminspire | separate/unobserved | Account and case lifecycle through the existing guarded Quantum Inspire runner. |
| quaternion-algebra | separate/unobserved | Documented algebra candidate: hyper-dual numbers; quaternions. Decision: **skip**: abandoned |
| quaternionic | 1.0.18 | Numba quaternion arrays and independent numerical comparisons. |
| quimb | 1.15.0 | Tensor-network classical references and marginal/expectation calculations. |
| qutip | separate/unobserved | Reference-only Lindblad alternative; qualify a capability gap before adding it. |
| qxelarator | separate/unobserved | Local QX execution; measurement-register semantics differ from Tuna classical bits. |
| referencing | 0.37.0 | SDK/environment infrastructure: JSON Referencing + Python |
| requests | 2.34.2 | SDK/environment infrastructure: Python HTTP for Humans. |
| requests-ntlm | 1.3.0 | SDK/environment infrastructure: This package allows for HTTP NTLM authentication using the requests library. |
| rich | 15.0.0 | SDK/environment infrastructure: Environment support dependency |
| roman-numerals | 4.1.0 | SDK/environment infrastructure: Manipulate well-formed Roman numerals |
| rpds-py | 2026.9.1 | SDK/environment infrastructure: Python bindings to Rust's persistent data structures (rpds) |
| ruamel-yaml | 0.19.1 | SDK/environment infrastructure: ruamel.yaml is a YAML parser/emitter that supports roundtrip preservation of comments, seq/map flow style, and map key order |
| ruff | 0.17.1 | Pinned lint and format gate. |
| runningman | 2.3.0 | Execution support used by measurement mitigation; provider submission stays guarded. |
| rustworkx | 0.18.1 | Coupling graphs, placement and disjoint-support candidates. |
| sagemath | 10.10 | Exact derivations, Clifford and Albert references through certified convention maps. |
| samplomatic | 0.21.0 | Runtime circuit preparation; dynamic-circuit restrictions remain binding. |
| scikit-build | 0.19.1 | SDK/environment infrastructure: Environment support dependency |
| scipy | 1.18.1 | Matrix exponentiation, linear algebra, integration and uncertainty estimates. |
| scipy-stubs | separate/unobserved | SDK/environment infrastructure: The official type stubs for SciPy |
| scmver | 1.10 | A package version manager based on SCM tags |
| scs | 3.3.1 | First-order splitting conic solver supporting PSD tomography through CVXPY; qualify convergence, constraint residuals and tolerances for the actual fit. |
| seaborn | 0.13.2 | SDK/environment infrastructure: Statistical data visualization |
| setuptools | 84.0.0 | SDK/environment infrastructure: Most extensible Python build backend with support for C/C++ extension modules |
| shellingham | 1.5.4 | SDK/environment infrastructure: Environment support dependency |
| sinter | separate/unobserved | Documented ecosystem candidate: skip, same reason as pymatching |
| six | 1.17.0 | SDK/environment infrastructure: Python 2 and 3 compatibility utilities |
| snowballstemmer | 3.1.1 | SDK/environment infrastructure: This package provides 36 stemmers for 34 languages generated from Snowball algorithms. |
| sparse | 0.17.0 | SDK/environment infrastructure: Environment support dependency |
| sparsediffpy | 0.8.0 | SDK/environment infrastructure: Python bindings for SparseDiffEngine algorithmic differentiation |
| sphinx | 9.1.0 | SDK/environment infrastructure: Python documentation generator |
| sphinxcontrib-applehelp | 2.0.0 | SDK/environment infrastructure: sphinxcontrib-applehelp is a Sphinx extension which outputs Apple help books |
| sphinxcontrib-devhelp | 2.0.0 | SDK/environment infrastructure: sphinxcontrib-devhelp is a sphinx extension which outputs Devhelp documents |
| sphinxcontrib-htmlhelp | 2.1.0 | SDK/environment infrastructure: sphinxcontrib-htmlhelp is a sphinx extension which renders HTML help files |
| sphinxcontrib-jsmath | 1.0.1 | SDK/environment infrastructure: A sphinx extension which renders display math in HTML via JavaScript |
| sphinxcontrib-qthelp | 2.0.0 | SDK/environment infrastructure: sphinxcontrib-qthelp is a sphinx extension which outputs QtHelp documents |
| sphinxcontrib-serializinghtml | 2.0.0 | SDK/environment infrastructure: sphinxcontrib-serializinghtml is a sphinx extension which outputs "serialized" HTML files (json and pickle) |
| splitoct | 0.16 | Split-signature negative control; associator agreement does not establish algebra identity. |
| sqlalchemy | 2.0.54 | SDK/environment infrastructure: Database Abstraction Library |
| sse-starlette | 3.5.0 | SDK/environment infrastructure: SSE plugin for Starlette |
| stack-data | 0.6.4.dev0+g53501eb8b.d20251216 | SDK/environment infrastructure: Extract data from python stack frames and tracebacks for informative displays |
| starlette | 1.9.0 | SDK/environment infrastructure: The little ASGI library that shines. |
| stevedore | 5.7.0 | SDK/environment infrastructure: Manage dynamic plugins for Python applications |
| stim | 1.16.0 | Stabilizer controls and Clifford subcircuits; not general quaternion wave evolution. |
| surreal | separate/unobserved | Documented algebra candidate: Conway surreal numbers. Decision: **skip** |
| sympy | 1.14.0 | Exact operator identities and symbolic certificates. |
| tabulate | 0.10.0 | SDK/environment infrastructure: Pretty-print tabular data |
| tfga | separate/unobserved | Documented algebra candidate: tensor-framework geometric algebra. Decision: **skip**: no CD content, heavy dependencies |
| threadpoolctl | 3.7.0 | Inspect and bound native BLAS/OpenMP threads. |
| toolz | 1.1.0 | SDK/environment infrastructure: List processing tools and functional utilities |
| torch | 2.14.1 | Qualified GPU tensor arithmetic and the octonion package backend. |
| torch-ga | separate/unobserved | Documented algebra candidate: tensor-framework geometric algebra. Decision: **skip**: no CD content, heavy dependencies |
| tornado | 6.5.10 | SDK/environment infrastructure: Tornado is a Python web framework and asynchronous networking library, originally developed at FriendFeed. |
| tqdm | 4.70.1 | SDK/environment infrastructure: Fast, Extensible Progress Meter |
| traitlets | 5.16.1 | SDK/environment infrastructure: Traitlets Python configuration system |
| truststore | 0.10.4 | SDK/environment infrastructure: Environment support dependency |
| typer | 0.27.3 | SDK/environment infrastructure: Environment support dependency |
| types-networkx | separate/unobserved | SDK/environment infrastructure: Typing stubs for networkx |
| types-protobuf | separate/unobserved | SDK/environment infrastructure: Typing stubs for protobuf |
| types-requests | separate/unobserved | SDK/environment infrastructure: Typing stubs for requests |
| types-six | separate/unobserved | SDK/environment infrastructure: Typing stubs for six |
| types-tqdm | separate/unobserved | SDK/environment infrastructure: Typing stubs for tqdm |
| typing-extensions | 4.16.0 | SDK/environment infrastructure: Backported and Experimental Type Hints for Python 3.9+ |
| typing-inspection | 0.4.4 | SDK/environment infrastructure: Runtime typing introspection tools |
| tzdata | 2026.5 | SDK/environment infrastructure: Environment support dependency |
| uncertainties | 3.2.4 | SDK/environment infrastructure: calculations with values with uncertainties, error propagation |
| urllib3 | 2.8.0 | SDK/environment infrastructure: HTTP library with thread-safe connection pooling, file post, and more. |
| uv | separate/unobserved | Pinned environment installer used by Kaggle kernel bootstrap; records package resolution rather than quantum evidence. |
| uvicorn | 0.54.0 | SDK/environment infrastructure: The lightning-fast ASGI server. |
| wcwidth | 0.9.2 | SDK/environment infrastructure: Measures the displayed width of unicode strings in a terminal |
| wheel | 0.48.0 | SDK/environment infrastructure: Environment support dependency |
| xarray | separate/unobserved | Labeled acquisition arrays and parameter axes. |
| yarl | 1.25.1 | SDK/environment infrastructure: Environment support dependency |
| zipp | 3.21.0 | SDK/environment infrastructure: Backport of pathlib-compatible object wrapper for zip files |
