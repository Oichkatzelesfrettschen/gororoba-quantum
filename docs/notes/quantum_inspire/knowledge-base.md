# Quantum Inspire knowledge base digest

Every page this repository captured from Quantum Inspire's site, its cQASM 3.0 specification, its SDK repositories and its component release history, with the rules each page states and an audit of its links, stale instructions and contradictions. Each entry links the retained capture and the live URL; the live pages change, and each capture header records its retrieval time (2026-10-16 UTC) and the sha256 of the fetched HTML. `scripts/capture_qi_docs.py --check` verifies the captures offline. The account-level authority for what this account can run is the live API catalogue [catalogue.json](../../evidence/quantum_inspire/catalogue.json).

Link audit method: the site capture requested every distinct body link once (HEAD, then GET, cookies kept for login redirects, one retry on 5xx) and recorded the status in [site/MANIFEST.json](site/MANIFEST.json) (`body_links`, `unreachable`, `bare_host_links`). A 403 from a publisher's bot filter and a TLS handshake failure in Python's client are recorded as such, not as dead links.

## Crawl coverage

The crawl started from 53 seed paths and followed every internal link of every fetched page; 67 pages answered 200 and were captured. Pages found beyond the seed list: `backends/qx-simulator`, `kbase/bell-states`, `kbase/bloch-sphere`, `kbase/cqasm-binary-controlled-gates`, `kbase/cqasm-error-models`, `kbase/cqasm-qubit-initialization-and-measurement`, `kbase/measure`, `kbase/measure-all`, `kbase/measure-x`, `kbase/measure-y`, `kbase/optimization-of-simulations`, `kbase/prep-x`, `kbase/prep-y`, `kbase/prep-z`.

Unreachable internal URLs and the pages that link them:

| URL | Status | Linked from |
|---|---|---|
| `/account/` | 404 | `/release-notes-old/` |
| `/backends/spin-2/` | 404 | `/backends/` |
| `/backends/starmon-7/` | 404 | `/kbase/deutsch-jozsa-algorithm/` |
| `/kbase/deutsch-jozsa-algorithm/kbase/spin-2-operational-specifics/` | 404 | `/kbase/deutsch-jozsa-algorithm/` |
| `/kbase/full-adder/kbase/spin-2-operational-specifics/` | 404 | `/kbase/full-adder/` |
| `/kbase/grover-algorithm/kbase/spin-2-operational-specifics/` | 404 | `/kbase/grover-algorithm/` |
| `/kbase/hardware/` | 404 | `/kbase/hello-quantum-world/` |
| `/kbase/managing-your-account/kbase/software-development-kit/` | 404 | `/kbase/managing-your-account/` |
| `/kbase/measure-z/` | 500 | `/kbase/cqasm-qubit-initialization-and-measurement/`, `/kbase/measure/` |
| `/kbase/quantum-classification/kbase/spin-2-operational-specifics/` | 404 | `/kbase/quantum-classification/` |
| `/kbase/spin-2-operational-specifics/` | 404 | `/kbase/quantum-classification/` |

Three link defects cause most of them: retired backend pages (`/backends/spin-2/`, `/backends/starmon-7/`, `/kbase/spin-2-operational-specifics/`, `/kbase/hardware/`, `/account`), page-relative hrefs written without a leading slash (`kbase/spin-2-operational-specifics`, `kbase/software-development-kit`), and a server error on `/kbase/measure-z/`. Scheme-less host links (`quantify-os.org` on release-notes, `www.quantum-inspire.com` on terms-and-conditions) also resolve to 404 in a browser; the capture rewrites them to https URLs.

## Site pages

### Site

#### /

[capture](site/home.md) | [live](https://www.quantum-inspire.com/)

- Covers: the landing page; QI 2.0 offers free registration, hardware access, project storage and hybrid classical-quantum computing; lists transmon QPUs, the neutral-atom emulator and the Spin-2+ QPU as "archived"; links the live dashboard `dashboard.quantum-inspire.com`.
- Audit: seven decorative figures load lazily and carry no ImageRecord in the payload, so the capture keeps their captions only.
- Links: 8 distinct links; all resolve.

#### about-qi

[capture](site/about-qi.md) | [live](https://www.quantum-inspire.com/about-qi/)

- Covers: QI is designed and built by QuTech (TU Delft and TNO); the editor offers automatic bug identification and autocomplete; results can be viewed and downloaded.
- Rules: carries a cQASM 3.0 Deutsch example (`version 3.0`, `qubit[2] q`, `bit[2] b`, `b[0] = measure q[0]`).
- Stale: shows the Cartesius supercomputer at SurfSara, a QI 1.0 era host.
- Links: 7 distinct links; all resolve.

#### backends

[capture](site/backends.md) | [live](https://www.quantum-inspire.com/backends/)

- Covers: the chip overview. Available processors are Tuna-17 (17 transmons, 24 flux-tunable couplers), Tuna-9 (9, 12 couplers), Tuna-5 (5, 4 couplers), the QX emulator "up to 26 qubits" and the Rydberg emulator; legacy backends no longer available are Starmon-5, Starmon-7, Spin-2+ and Spin-2.
- Stale: the web-portal card still says algorithms run "on one of our quantum processors, Spin-2 and Starmon-7, or on our QX simulator" and describes ProjectQ and OpenQL as the transpilers and a ProjectQ SDK backend (QI 1.0 stack); the Spin-2+ and Spin-2 entries link the retired `/backends/spin-2/` page.
- Contradiction: QX "26-qubit" against the API description and this account's catalogue (C3).
- Links: 20 distinct links; unresolved: `http://quantumdelft.nl/` client-observed TLS failure; `https://api.quantum-inspire.com/` HTTP 404; `https://medium.com/qiskit/quantum-inspire-and-qiskit-f1be608f8955` blocked:403 (bot filter; not dead); `https://www.quantum-inspire.com/backends/spin-2/` HTTP 404; `https://www.tudelft.nl/ewi/onderzoek/quantum-computing/` HTTP 404.

#### backends/qx-simulator

[capture](site/backends_qx-simulator.md) | [live](https://www.quantum-inspire.com/backends/qx-simulator/)

- Covers: QX simulates cQASM 3.0 only, as a C++ executable or the `qxelarator` Python module; one commodity cloud-server instance simulates up to 26 qubits; the only error model is the symmetric depolarizing channel; "job durations could be maximized to 30 minutes compute time".
- Stale: "three powerful supercomputer instances" in the system overview contradicts the single cloud instance stated two sections later; the contribution links point at the legacy `QE-Lab` GitHub organization and a "cQASM (2.0) spec".
- Contradiction: 26 qubits and 30 minutes against the catalogue's `nqubits` 10 and `job_execution_time_limit` 3600 s (C3, C12).
- Links: 7 distinct links; all resolve.

#### backends/spin-2-plus

[capture](site/backends_spin-2-plus.md) | [live](https://www.quantum-inspire.com/backends/spin-2-plus/)

- Covers: Spin-2+ uses the left three of six quantum dots (one ancilla for Pauli-spin-blockade readout, two data qubits) in 28Si/SiGe; X90 fidelity 99.0% to 99.8% and CZ 90.0% to 95.5% relative to Spin-2; automated full calibration takes 5 to 30 minutes and keeps the system calibrated without human intervention for more than 24 h; the fridge holds about 200 mK.
- Audit: the first heading reads "Spin-2" on the Spin-2+ page; the backends page calls the device "taken offline" and the home page "archived". The fact sheet PDF is identified in the site manifest `hosted_documents` by sha256 `aeaa1513...1594` (1536485 bytes).
- Links: 4 distinct links; all resolve.

#### backends/transmons

[capture](site/backends_transmons.md) | [live](https://www.quantum-inspire.com/backends/transmons/)

- Covers: availability dates. Tuna-17 since April 2026, Tuna-9 since December 2025, Tuna-5 since May 2025; Starmon-7 replaced Starmon-5 in February 2025 and was available until December 2025; Starmon-5 ran from April 2020 to December 2025. Tuna control uses a Qblox Cluster (one QRM-RF, three QCM-RF, three QCM); OpenSquirrel exports quantify-scheduler schedules for Tuna and uses legacy OpenQL for Starmon-7.
- Stale: the Tuna-5 publication is called "Physical Review Letters (in press)"; it appeared as Phys. Rev. Lett. 136, 200801 (2026), doi:10.1103/wdfj-4nbt ([citing.md](citing.md)).
- Audit: Starmon-5 and Starmon-7 both link arXiv:2602.18388, the error-burst study of QI's superconducting processors.
- Links: 6 distinct links; all resolve.

#### contact

[capture](site/contact.md) | [live](https://www.quantum-inspire.com/contact/)

- Covers: technical support at support@quantum-inspire.com; QuTech postal and delivery addresses.
- Audit: the QuTech mail link targets `QuTech@tudelft.n` (missing final `l`).
- Links: 4 distinct links; all resolve.

#### faq

[capture](site/faq.md) | [live](https://www.quantum-inspire.com/faq/)

- Covers: maintenance and R&D downtime; bug reports to support@quantum-inspire.com; password rules (8 characters minimum, not similar to the e-mail, not common, not numeric only); account deletion by support request; a typical hardware job takes 30 to 90 s with overhead, a hybrid job up to 15 min or longer; tuning takes a few seconds to 30 minutes and adds to waiting time; outputs are not normalized for readout error.
- Contradictions: "We have two quantum chip chips available" (C2); "not allowed to have more than 3 jobs in the queue for a hardware backend" (C1); account deletion by support request against the self-service account page in managing-your-account.
- Links: 0 distinct links; all resolve.

#### kbase

[capture](site/kbase.md) | [live](https://www.quantum-inspire.com/kbase/)

- Covers: the knowledge-base index. Its content element is empty; the capture keeps the sidebar menu, which lists 40 pages in six sections (introduction, quick guide, cQASM language, advanced user guide, code examples, hardware and simulator backends).
- Audit: the sidebar omits spin-2-plus-operational-specifics, qi-tool, number-of-shots, optimization-of-simulations and the cQASM 1.0 pages (bell-states, bloch-sphere, cqasm-binary-controlled-gates, cqasm-error-models, cqasm-qubit-initialization-and-measurement, measure, measure-all, measure-x, measure-y, prep-x, prep-y, prep-z); body links reach them.
- Links: 38 distinct links; all resolve.

#### partners

[capture](site/partners.md) | [live](https://www.quantum-inspire.com/partners/)

- Covers: QuTech, TNO, TU Delft, SURF and Quantum Delta NL (CAT-1 programme executed by TNO, TU Delft, TU Eindhoven, University of Amsterdam and aQa Leiden); supporters include the National Growth Fund, NWA, OpenSuperQPlus and QLSI.
- Links: 12 distinct links; unresolved: `https://qt.eu/projects/computing/opensuperqplus.php` HTTP 404; `https://quantumdelta.nl/` client-observed TLS failure; `https://quantumdelta.nl/accelerate-in-detail/` client-observed TLS failure.

#### reference

[capture](site/reference.md) | [live](https://www.quantum-inspire.com/reference/)

- Covers: the citation QI asks for, "QuTech. (2025). Quantum Inspire Home. Retrieved from Quantum Inspire: https://www.quantum-inspire.com/", and background papers (SPIE 2020 platform paper, Physics Today spin article, Vandersypen et al. npj QI 2017, Watson et al. Nature 2018, Neumann arXiv:2004.10426, CWI graph-resistance report, two machine-learning articles). [citing.md](citing.md) verifies each.
- Links: 9 distinct links; all resolve.

#### release-notes

[capture](site/release-notes.md) | [live](https://www.quantum-inspire.com/release-notes/)

- Covers: QI 2.0 expects regular scheduled and unscheduled maintenance; jobs submitted during it may fail. Component release notes live in nine upstream repositories ([release-notes.md](release-notes.md)).
- Audit: the quantify-os.org link is written without a scheme, so a browser resolves it to `/release-notes/quantify-os.org/` (404); the capture rewrites it to https://quantify-os.org.
- Links: 11 distinct links; all resolve.

#### release-notes-old

[capture](site/release-notes-old.md) | [live](https://www.quantum-inspire.com/release-notes-old/)

- Covers: QI 1.0 notes 2018-09-04 to 2021-05-26. Maintenance window every Wednesday 08:00-12:00 CET; Starmon-5 shots raised to 16384 (default 8192) and CZ from 80 ns to 60 ns on 2020-07-31; hardware default 4096 shots from 2020-05-15; cQASM size limit 1 MB from 2018-12-17; QX on SURF Lisa from 2021-05-26; SDK notes moved to GitHub from 1.5.0.
- Stale: every rule here is QI 1.0 ("no longer supported"); the API-token page `/account` is 404.
- Links: 8 distinct links; unresolved: `https://www.quantum-inspire.com/account` HTTP 404.

#### terms-and-conditions

[capture](site/terms-and-conditions.md) | [live](https://www.quantum-inspire.com/terms-and-conditions/)

- Covers: General Conditions of Use dated 6 Feb 2025 (PDF identified in the manifest by sha256 `64c49043...2b97`, 248021 bytes) and EU Russia sanctions screening. Rules: non-commercial use only; accounts are strictly personal; queued execution with per-backend limits on qubits, shots and run time, with over-time runs aborted; staff may reprioritize, relay jobs to external providers or refuse jobs; uploaded algorithms, data and code are open to use and redistribution by QuTech unless agreed otherwise in writing and remain after account deletion; free simulation up to 26 qubits and, in principle, up to 37 on the national supercomputer; Dutch law, Court of The Hague.
- Audit: "www.quantum-inspire.com" is a scheme-less link (404 when a browser resolves it); userinfo.surfsara.nl answers 401.
- Links: 11 distinct links; unresolved: `https://userinfo.surfsara.nl/` HTTP 401.

### Introduction

#### kbase/introduction-to-quantum-computing

[capture](site/kbase_introduction-to-quantum-computing.md) | [live](https://www.quantum-inspire.com/kbase/introduction-to-quantum-computing/)

- Covers: quantum theory, quantum computers, Shor's algorithm, challenges; links the Quantum Inspire journey video. No platform rules.
- Links: 3 distinct links; all resolve.

#### kbase/what-is-a-qubit

[capture](site/kbase_what-is-a-qubit.md) | [live](https://www.quantum-inspire.com/kbase/what-is-a-qubit/)

- Covers: qubit state, x- and y-basis states written as |+>, |-> and |+i>, |-i>, the Bloch sphere with an interactive widget (theta 0.2, phi 0.4 in the capture), qubit technologies.
- Contradiction: the y-basis is |+i>/|-i> here and |R>/|L> on qubit-basis-states.
- Links: 5 distinct links; all resolve.

#### kbase/superposition-and-entanglement

[capture](site/kbase_superposition-and-entanglement.md) | [live](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/)

- Covers: superposition, entanglement, QuTech Academy videos. No platform rules.
- Links: 6 distinct links; all resolve.

#### kbase/what-is-a-quantum-algorithm

[capture](site/kbase_what-is-a-quantum-algorithm.md) | [live](https://www.quantum-inspire.com/kbase/what-is-a-quantum-algorithm/)

- Covers: quantum circuits and reversibility with a cQASM 3.0 Bell circuit.
- Links: 4 distinct links; all resolve.

#### kbase/hello-quantum-world

[capture](site/kbase_hello-quantum-world.md) | [live](https://www.quantum-inspire.com/kbase/hello-quantum-world/)

- Covers: the first Bell-state program and the editor workflow; anonymous use is not possible; all shots of a job run back to back; the histogram shows the bit register at the end of the algorithm with q[0] in the rightmost bit.
- Errors: "The Hadamard gate ... brings the basis state |0> to (|00> + |11>)/sqrt 2" (it gives (|0> + |1>)/sqrt 2); advises declaring no more qubits than used, which conflicts with the hardware rule in executing-your-algorithm (C15); links `/kbase/hardware/` (404); says Starmon-7 requires `qubit[7] q` although Starmon-7 is retired.
- Links: 8 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/hardware/` HTTP 404.

### Quick guide

#### kbase/quick-guide

[capture](site/kbase_quick-guide.md) | [live](https://www.quantum-inspire.com/kbase/quick-guide/)

- Covers: the guide index and the requested citation (same text as /reference).
- Links: 13 distinct links; all resolve.

#### kbase/creating-a-new-project

[capture](site/kbase_creating-a-new-project.md) | [live](https://www.quantum-inspire.com/kbase/creating-a-new-project/)

- Covers: `Create project` and `Create algorithm` under MyQI; a new algorithm file is `source.cq`.
- Links: 2 distinct links; all resolve.

#### kbase/managing-your-projects

[capture](site/kbase_managing-your-projects.md) | [live](https://www.quantum-inspire.com/kbase/managing-your-projects/)

- Covers: saving creates a commit with a description; old commits can be browsed; deleting a project deletes its algorithms and results. Carries a cQASM 3.0 Phi-minus program.
- Links: 5 distinct links; all resolve.

#### kbase/working-with-the-editor

[capture](site/kbase_working-with-the-editor.md) | [live](https://www.quantum-inspire.com/kbase/working-with-the-editor/)

- Covers: the editor checks syntax, simultaneous operations on one qubit and out-of-range indices; syntax errors do not block saving; the circuit renders live and exports as SVG or PNG; long programs suit the SDK.
- Links: 4 distinct links; all resolve.

#### kbase/executing-your-algorithm

[capture](site/kbase_executing-your-algorithm.md) | [live](https://www.quantum-inspire.com/kbase/executing-your-algorithm/)

- Covers: `RUN` always compiles with the backend's compilation strategy and hides intermediate stages; on hardware the qubit register must equal the chip's qubit count; qubits start in |0>; without a measure statement every qubit is measured in z; hybrid algorithms need the QI tool.
- Audit: the sections "Explicit compilation of the algorithm" and "Running a pre-compiled version" are empty on the live page; links number-of-shots, an orphan page.
- Links: 6 distinct links; all resolve.

#### kbase/displaying-and-downloading-your-results

[capture](site/kbase_displaying-and-downloading-your-results.md) | [live](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/)

- Covers: the page is marked "THIS PAGE IS OUTDATED". It describes histogram bit order (MSB left, q[0] rightmost), three QX simulation modes (deterministic N=1, deterministic N>1 Monte Carlo, non-deterministic), binning of unmeasured qubits on hardware, and CSV/JSON downloads of histogram data (decimal register value to frequency) and raw data (one decimal integer per shot).
- Contradictions: "qubit 3 is the 3th bit from the right" (it is the fourth; C14); attributes tuning to "the Spin-2 backend"; QI 1.0 execution modes.
- Links: 7 distinct links; all resolve.

#### kbase/managing-your-account

[capture](site/kbase_managing-your-account.md) | [live](https://www.quantum-inspire.com/kbase/managing-your-account/)

- Covers: QI 2.0 has one free account type (QI 1.0 had three); sign-up at compute.quantum-inspire.com by e-mail or identity provider; account deletion on the account page.
- Audit: the QI tool link is page-relative and resolves to a 404.
- Links: 5 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/managing-your-account/kbase/software-development-kit/` HTTP 404.

#### kbase/qubit-register

[capture](site/kbase_qubit-register.md) | [live](https://www.quantum-inspire.com/kbase/qubit-register/)

- Covers: virtual qubit registers map onto physical qubits in declaration order; a state vector of n qubits takes 2^n x 16 bytes (10 qubits 16 kB, 37 qubits over 2 TB).
- Errors: the example declares `version 3` and `qubit north[2]`, while cQASM 3.0 writes `qubit[2] north` ([spec](cqasm-spec/language_specification/statements/variable_declarations/qubit_register_declaration.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html))); the last comment names the `south` register 'north'.
- Links: 4 distinct links; all resolve.

#### kbase/binary-register

[capture](site/kbase_binary-register.md) | [live](https://www.quantum-inspire.com/kbase/binary-register/)

- Covers: QI 2.0 allows several bit registers, concatenated in declaration order; bits start at zero; measuring one qubit twice into two bits gives perfectly correlated bits without entanglement.
- Contradiction: "qubit 3 is shown as the third bit from the right" (C14).
- Links: 4 distinct links; all resolve.

#### kbase/qubit-basis-states

[capture](site/kbase_qubit-basis-states.md) | [live](https://www.quantum-inspire.com/kbase/qubit-basis-states/)

- Covers: z, x and y bases, declared states, and initialization and measurement in a basis.
- Stale: names `prep_z`, `prep_y`, `prep_x`, `measure_all`, `measure_x/y/z` (cQASM 1.0; C7).
- Links: 3 distinct links; all resolve.

### cQASM language

#### kbase/cqasm

[capture](site/kbase_cqasm.md) | [live](https://www.quantum-inspire.com/kbase/cqasm/)

- Covers: QI uses cQASM 3.0; a Bell example with `init q[0:1]`; cQASM 3.0 is case-sensitive (1.0 was not); cQASM 1.0 sub-circuits, static loops and curly-bracket parallel bundles are removed, with scheduling left to backends and steered by `wait` and `barrier`.
- Links: 4 distinct links; all resolve.

#### kbase/cqasm-single-gate-multiple-qubits

[capture](site/kbase_cqasm-single-gate-multiple-qubits.md) | [live](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/)

- Covers: SGMQ over registers, slices and index lists for single- and multi-qubit gates and measure; repeated indices unpack but render overlapped in the editor.
- Links: 1 distinct links; all resolve.

#### kbase/three-qubit-gates

[capture](site/kbase_three-qubit-gates.md) | [live](https://www.quantum-inspire.com/kbase/three-qubit-gates/)

- Covers: Toffoli (6 CNOT), Fredkin (9 adjacent CNOT) and Margolus (3 CNOT) decompositions.
- Contradiction: says three-qubit gates are not part of the language, while the latest spec defines CCX and CSWAP (C8); the Fredkin matrix is labeled "Toffoli=".
- Links: 3 distinct links; all resolve.

### Advanced user guide

#### kbase/advanced-guide

[capture](site/kbase_advanced-guide.md) | [live](https://www.quantum-inspire.com/kbase/advanced-guide/)

- Covers: index of the QI tool, SDK plugins, compilers and hybrid algorithms.
- Links: 2 distinct links; all resolve.

#### kbase/software-development-kit

[capture](site/kbase_software-development-kit.md) | [live](https://www.quantum-inspire.com/kbase/software-development-kit/)

- Covers: `qi login` stores credentials in `~/.quantuminspire/config.json`, read by both plugins; Qiskit `QIProvider().get_backend("QX emulator")`.
- Stale: `qi files upload` and `qi results get` are absent from the SDK README from 4.0.0 on, which uses `qi run --file ... --backend-type-id N` and `qi jobs results` ([sdk/README.md](sdk/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/quantuminspire/054a4f0be22983a5d515c31a24881bc0d875463d/README.md))); the Python example passes `backend_type_id=3` (Starmon-7, absent from this account's catalogue), writes `raw_data_enabled=true` (Python spells it `True`) and omits the `Path` and `sleep` imports; the PennyLane snippet imports `pennylane_quantuminspire2.qi_device.QI2Device`, while plugin 0.15.5 documents `pennylane_quantuminspire.qi_device.QIDevice` built from a Qiskit `QIProvider` backend ([submitting.rst](sdk/pennylane-quantuminspire/docs/getting_started/submitting.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/getting_started/submitting.rst))) (C16).
- Links: 11 distinct links; all resolve.

#### kbase/qi-tool

[capture](site/kbase_qi-tool.md) | [live](https://www.quantum-inspire.com/kbase/qi-tool/)

- Covers: the same QI tool text as software-development-kit, without the plugin sections.
- Stale: same `qi files upload` / `qi results get` commands and Python example (C16).
- Links: 6 distinct links; all resolve.

#### kbase/compilation

[capture](site/kbase_compilation.md) | [live](https://www.quantum-inspire.com/kbase/compilation/)

- Covers: libQASM parses cQASM to an AST for QX and OpenSquirrel; OpenSquirrel is the default compiler; the generic passes are mapping, routing, decomposition, optimization, scheduling and code generation.
- Links: 6 distinct links; all resolve.

#### kbase/opensquirrel

[capture](site/kbase_opensquirrel.md) | [live](https://www.quantum-inspire.com/kbase/opensquirrel/)

- Covers: QI compile stages are (internal) verification, decomposition, mapping, optimization, routing, (scheduling, unused), exporting and (internal) validation; verification and validation cannot be skipped; `Compile` in the web GUI writes one `_compiled_stage` file per stage; the compile target may differ from the run target; the QI tool may bypass stages. Shows a Spin-2+ McKay compilation of three SGMQ CNOTs into CZ, Rz and X90.
- Stale: points to the Spin-2+ and Starmon-7 pages for default strategies; the catalogue's `default_compiler_config` is the live authority (C18).
- Links: 7 distinct links; all resolve.

#### kbase/low-level-api

[capture](site/kbase_low-level-api.md) | [live](https://www.quantum-inspire.com/kbase/low-level-api/)

- Covers: REST API at api.quantum-inspire.com with OpenAPI docs at `/docs`; bearer tokens from QI's IdP; the `qi-compute-api-client` package.
- Errors: the API root answers 404; the example uses `os` without importing it and `async with` outside a coroutine (C17).
- Links: 8 distinct links; unresolved: `https://api.quantum-inspire.com/` HTTP 404.

#### kbase/libket

[capture](site/kbase_libket.md) | [live](https://www.quantum-inspire.com/kbase/libket/)

- Covers: the LibKet C++14 expression-template library with a QFT example; its device `QDeviceType::qi_26_simulator` and the IBM `ibmq_5_london` device are historical names.
- Links: 7 distinct links; all resolve.

### Code examples

#### kbase/deutsch-jozsa-algorithm

[capture](site/kbase_deutsch-jozsa-algorithm.md) | [live](https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/)

- Covers: Deutsch-Jozsa with four one-bit oracles on QX.
- Errors: the code keeps cQASM 1.0 remnants (`H q[0,1]}` and a `.measurement` label) that cQASM 3.0 rejects (C19); the Spin-2 link is page-relative (404) and the Starmon-7 link targets the retired `/backends/starmon-7/` (404).
- Links: 11 distinct links; unresolved: `https://www.quantum-inspire.com/backends/starmon-7/` HTTP 404; `https://www.quantum-inspire.com/kbase/deutsch-jozsa-algorithm/kbase/spin-2-operational-specifics/` HTTP 404.

#### kbase/full-adder

[capture](site/kbase_full-adder.md) | [live](https://www.quantum-inspire.com/kbase/full-adder/)

- Covers: Feynman's full adder with two decomposed Toffolis, and the Figgat 2018 seven-gate adder written with `ctrl.X90`, `ctrl.X` and `ctrl.mX90` gate modifiers.
- Audit: the Spin-2 link is page-relative (404).
- Links: 10 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/full-adder/kbase/spin-2-operational-specifics/` HTTP 404.

#### kbase/grover-algorithm

[capture](site/kbase_grover-algorithm.md) | [live](https://www.quantum-inspire.com/kbase/grover-algorithm/)

- Covers: three-qubit Grover search for 6 with decomposed Toffolis; one iteration about 77%, two about 95%; optimal r = pi sqrt(N)/4.
- Audit: the quiprocone lecture is 404, journals.aps.org blocks the client (403), the Spin-2 link is page-relative (404).
- Links: 11 distinct links; unresolved: `http://www.quiprocone.org/Protected/Lecture_6.htm` HTTP 404; `https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.79.325` blocked:403 (bot filter; not dead); `https://www.quantum-inspire.com/kbase/grover-algorithm/kbase/spin-2-operational-specifics/` HTTP 404.

#### kbase/repetition-code

[capture](site/kbase_repetition-code.md) | [live](https://www.quantum-inspire.com/kbase/repetition-code/)

- Covers: three-qubit bit-flip code with two ancillas and probabilistic error injection via Rx(0.45) (5%) and Rx(1.16) (30%).
- Stale: the correction step is commented out as "Not yet supported in cQASM v3" (binary-controlled gates were cQASM 1.0); the page still links cqasm-binary-controlled-gates.
- Links: 8 distinct links; all resolve.

#### kbase/code-example-getting-started-with-transmons

[capture](site/kbase_code-example-getting-started-with-transmons.md) | [live](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-transmons/)

- Covers: points to DiCarlo-lab notebooks for Tuna and Starmon (Bell pairs with and without the Qiskit transpiler, T1 and Rabi with mid-circuit measurements).
- Audit: both notebook links answer 404 (the notebooks moved or were removed).
- Links: 5 distinct links; unresolved: `https://github.com/DiCarloLab-Delft/QuantumInspireUtilities/blob/main/qi_utilities/notebook_guides/0.0_getting_started_starmon7.ipynb` HTTP 404; `https://github.com/DiCarloLab-Delft/QuantumInspireUtilities/blob/main/qi_utilities/notebook_guides/0.1_getting_started_tuna_devices.ipynb` HTTP 404.

#### kbase/code-example-getting-started-with-the-neutral-atom-platform

[capture](site/kbase_code-example-getting-started-with-the-neutral-atom-platform.md) | [live](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/)

- Covers: Rydberg physics and blockade; `asm(Rydberg) '''...'''` blocks carry the `INIT(x, y) q[i]` lattice-position directive (only before any operation; otherwise the backend places the atom) and the `RYD(rabi_freq, detuning, dt)` global pulse step, normalized to a reference Rabi frequency of 1.0; measurement is implied at the end on every qubit. The capture keeps the full cQASM example and the eight figures.
- Links: 2 distinct links; all resolve.

#### kbase/code-example-the-maximum-independent-set

[capture](site/kbase_code-example-the-maximum-independent-set.md) | [live](https://www.quantum-inspire.com/kbase/code-example-the-maximum-independent-set/)

- Covers: MIS on the Ry emulator (at most nine qubits) via Rydberg blockade and a VQAA detuning sweep.
- Audit: the live page renders its code with nested triple backticks inside `asm(Rydberg)` blocks, so several code blocks are empty or split in the capture as on the site.
- Links: 4 distinct links; all resolve.

#### kbase/quantum-classification

[capture](site/kbase_quantum-classification.md) | [live](https://www.quantum-inspire.com/kbase/quantum-classification/)

- Covers: distance-based classifier, reduced to two qubits for Spin-2 after Neumann (arXiv:2004.10426); 98% classification on QX and a less accurate Spin-2 hardware result at 1024 shots.
- Audit: both Spin-2 links answer 404.
- Links: 8 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/quantum-classification/kbase/spin-2-operational-specifics/` HTTP 404; `https://www.quantum-inspire.com/kbase/spin-2-operational-specifics/` HTTP 404.

### Backends

#### kbase/hardware-backends

[capture](site/kbase_hardware-backends.md) | [live](https://www.quantum-inspire.com/kbase/hardware-backends/)

- Covers: general hardware rules. All qubits are initialized at each shot start and all are measured at each shot end; the final measure statement selects what is returned; partial measurement is binned; too many operations per shot make the system reject the job; the shot limit comes from acquisition memory.
- Stale: lists only Tuna-5 and Tuna-9 for the Tuna page, links retired Starmon-7 and Spin-2+ pages, names `prep`, `measure_all` and `measure_x` (cQASM 1.0), and requires `qubit[2]` for Spin-2+ and `qubit[7]` for Starmon-7 (C7, C11, C15).
- Links: 8 distinct links; all resolve.

#### kbase/tuna-operational-specifics

[capture](site/kbase_tuna-operational-specifics.md) | [live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)

- Covers: Tuna-5 (Q0-Q4 starfish, center Q2), Tuna-9 (Q0-Q8 diamond, center Q4), Tuna-17 (Q0-Q16 ninja star). Native (bold): Rx, Ry, Rz, X90, Y90, mX90, mY90, X, Y, Z, I, S, Sdag, T, Tdag, CZ, init, measure, reset; decomposed: Rn, H, CNOT, CR, CRk, SWAP. Not allowed: Display, Display_binary, Not, binary-controlled `c-`, Toffoli. Rotation angles quantize to multiples of pi/36 (5 degrees). Mid-circuit measurement allowed. OpenSquirrel schedules ALAP with 20 ns single-qubit gates, 60 ns CZ, 800 ns measurement and 500 or 200 us initialization; `wait` counts 20 ns cycles per qubit; results are a shots x bits array in bit-register order; parallel measurement needs a `barrier`.
- Contradictions: the `wait q[0:4], 11` example is not cQASM 3.0 syntax (C6); the API gateset omits the decomposed gates (C5).
- Links: 6 distinct links; all resolve.

#### kbase/starmon-7-operational-specifics

[capture](site/kbase_starmon-7-operational-specifics.md) | [live](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/)

- Covers: Starmon-7 (Q0-Q6, two rhombi sharing Q3). Native: X, Y, Z, I, Rx, Ry, X90, Y90, mX90, mY90, S, Sdag, T, Tdag, CZ, init, measure, reset; decomposed: Rz, H, CNOT, SWAP; not allowed: CR, CRk, Display, Not, `c-`, Toffoli. Angles quantize to pi/28. OpenQL schedules ALAP with 20 ns single-qubit gates, 60 ns CZ, 1 us measurement and 150 us initialization.
- Stale: Starmon-7 retired in December 2025 (backends/transmons); the page repeats "the Tuna backends allow mid-circuit measurements"; same `wait` syntax error (C6, C10).
- Links: 3 distinct links; all resolve.

#### kbase/spin-2-plus-operational-specifics

[capture](site/kbase_spin-2-plus-operational-specifics.md) | [live](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/)

- Covers: two data qubits plus a readout ancilla; programs start with `version 3.0` and one declaration `qubit[1-4] name`; SGMQ for single-qubit gates; no `reset`; bit declarations and measure statements are accepted and ignored; all qubits are measured in z at the end; compilation to X90, Rz (virtual, zero time) and CZ with McKay decomposition (at most three Rz and two X90 per single-qubit sequence); single-qubit gates on different qubits run sequentially.
- Audit: orphan page (not in the sidebar); the site's Markdown turns `<number-of-bits:INT>` placeholders into links; Spin-2+ is offline (C11).
- Links: 2 distinct links; all resolve.

#### kbase/ry-emulator-operational-specifics

[capture](site/kbase_ry-emulator-operational-specifics.md) | [live](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/)

- Covers: neutral-atom emulator with 9 qubits on a rectangular lattice; single-qubit X, Z, T, S, Rx, Rz plus `INIT` and `RYD` directives; no mid-circuit measurement, implied measurement of all qubits at the end.
- Contradiction: the catalogue gateset adds H and CNOT with a CNOT and XZX decomposition; a retained 9-qubit H/CNOT run failed (C4).
- Links: 3 distinct links; all resolve.

#### kbase/emulator-backends

[capture](site/kbase_emulator-backends.md) | [live](https://www.quantum-inspire.com/kbase/emulator-backends/)

- Covers: QX simulates up to 26 qubits on a 4 GB commodity cloud server with a full state vector.
- Contradiction: 26 qubits against `nqubits` 10 (C3).
- Links: 2 distinct links; all resolve.

### Orphan

#### kbase/number-of-shots

[capture](site/kbase_number-of-shots.md) | [live](https://www.quantum-inspire.com/kbase/number-of-shots/)

- Covers: why shots repeat; a one-qubit H example with 20 sample outcomes. Orphan page linked from executing-your-algorithm.
- Links: 0 distinct links; all resolve.

#### kbase/bell-states

[capture](site/kbase_bell-states.md) | [live](https://www.quantum-inspire.com/kbase/bell-states/)

- Covers: Bell state definitions.
- Links: 1 distinct links; all resolve.

#### kbase/bloch-sphere

[capture](site/kbase_bloch-sphere.md) | [live](https://www.quantum-inspire.com/kbase/bloch-sphere/)

- Covers: Bloch sphere image and Wikipedia link.
- Links: 1 distinct links; all resolve.

### Orphan (QI 1.0)

#### kbase/optimization-of-simulations

[capture](site/kbase_optimization-of-simulations.md) | [live](https://www.quantum-inspire.com/kbase/optimization-of-simulations/)

- Covers: QI 1.0 emulator modes; an algorithm counts as deterministic when it holds no measurement and no `error_model`; N=1 returns exact probabilities, N>1 Monte Carlo sampling of the final state.
- Stale: refers to `measure_parity`, `measure_all` and `error_model` (cQASM 1.0).
- Links: 5 distinct links; all resolve.

#### kbase/cqasm-binary-controlled-gates

[capture](site/kbase_cqasm-binary-controlled-gates.md) | [live](https://www.quantum-inspire.com/kbase/cqasm-binary-controlled-gates/)

- Covers: cQASM 1.0 `c-X b[0], q[1]` and `not b[0]`, QX only.
- Stale: `version 1.0`, `qubits 2`, `prep_z`, `measure_z`; cQASM 3.0 has no binary-controlled gates.
- Links: 2 distinct links; all resolve.

#### kbase/cqasm-error-models

[capture](site/kbase_cqasm-error-models.md) | [live](https://www.quantum-inspire.com/kbase/cqasm-error-models/)

- Covers: QX symmetric depolarizing channel, `error_model depolarizing_channel, 0.001` after `qubits`.
- Stale: cQASM 1.0 syntax.
- Links: 1 distinct links; all resolve.

#### kbase/cqasm-qubit-initialization-and-measurement

[capture](site/kbase_cqasm-qubit-initialization-and-measurement.md) | [live](https://www.quantum-inspire.com/kbase/cqasm-qubit-initialization-and-measurement/)

- Covers: `prep_x/y/z`, `measure_x/y/z`, `measure_all`; one binary register indexed like the qubits; re-measurement overwrites the bit.
- Stale: mixes a cQASM 3.0 example with cQASM 1.0 instruction names; `measure-z` answers HTTP 500.
- Links: 10 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/measure-z/` HTTP 500.

#### kbase/measure

[capture](site/kbase_measure.md) | [live](https://www.quantum-inspire.com/kbase/measure/)

- Covers: `measure` is an alias for `measure_z`. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 1 distinct links; unresolved: `https://www.quantum-inspire.com/kbase/measure-z` HTTP 500.

#### kbase/measure-all

[capture](site/kbase_measure-all.md) | [live](https://www.quantum-inspire.com/kbase/measure-all/)

- Covers: `measure_all` measures every qubit in z in parallel. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 0 distinct links; all resolve.

#### kbase/measure-x

[capture](site/kbase_measure-x.md) | [live](https://www.quantum-inspire.com/kbase/measure-x/)

- Covers: `measure_x` measures in the x basis. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 0 distinct links; all resolve.

#### kbase/measure-y

[capture](site/kbase_measure-y.md) | [live](https://www.quantum-inspire.com/kbase/measure-y/)

- Covers: `measure_y` measures in the y basis. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 0 distinct links; all resolve.

#### kbase/prep-x

[capture](site/kbase_prep-x.md) | [live](https://www.quantum-inspire.com/kbase/prep-x/)

- Covers: `prep_x` initializes |+>; re-initialization also zeroes the qubit's bit. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 1 distinct links; all resolve.

#### kbase/prep-y

[capture](site/kbase_prep-y.md) | [live](https://www.quantum-inspire.com/kbase/prep-y/)

- Covers: `prep_y` initializes |R>. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 1 distinct links; all resolve.

#### kbase/prep-z

[capture](site/kbase_prep-z.md) | [live](https://www.quantum-inspire.com/kbase/prep-z/)

- Covers: `prep_z` initializes |0>. cQASM 1.0 instruction; cQASM 3.0 uses `measure`, `measureX/Y/Z` or `measure(x,y,z)` and `init`.
- Links: 1 distinct links; all resolve.

## Contradictions and their reconciliation

The live API catalogue ([catalogue.json](../../evidence/quantum_inspire/catalogue.json)) is the authority for what this account can use, because the compute job manager enforces it on submission and reports it per backend type; the cQASM specification is the authority for syntax and semantics; retained runs under [results/quantum_inspire/runs/](../../../results/quantum_inspire/runs/) settle what a backend accepted. OpenAPI field descriptions come from [api/openapi.json](api/openapi.json) ([live](https://api.quantum-inspire.com/openapi.json)).

### C1 Queue limit

- Sources: FAQ: at most 3 jobs in the queue per hardware backend. Catalogue: `batchjobs_per_queue_limit` 5 and `max_jobs_per_batch_job` 5 on every backend type; OpenAPI defines the first as the "maximum allowed number of batchjobs per a specific user and a backend type" and the second as the maximum jobs in one batch job.
- Reconciliation: The catalogue states what the service accepts: up to 5 queued batch jobs of up to 5 jobs each per backend type. The FAQ binds users and may count circuits rather than batch jobs, so on hardware `qi_platform.py submit` holds a batch to 3 circuits and refuses a batch while one of the account's batches is queued, which keeps at most 3 jobs queued under either unit (root AGENTS.md, "Quantum Inspire").

### C2 Number of hardware backends

- Sources: FAQ: "two quantum chip chips". Backends pages: Tuna-5, Tuna-9 and Tuna-17 available; Starmon-5, Starmon-7, Spin-2 and Spin-2+ retired. Catalogue backend types: QX emulator (1), Tuna-5 (4), Ry emulator (5), Tuna-9 (6), Tuna-17 (7); `backends` also lists Spin-2+ (2) and Starmon-7 (3), offline and without a backend type.
- Reconciliation: The catalogue governs: three Tuna QPUs plus two emulators. It flags the Ry emulator `is_hardware: true` (located at TU/eindhoven) although every page calls it an emulator. Starmon-7's last heartbeat in `backends` is 2026-03-27, after the December 2025 end date on backends/transmons; recorded as observed, unexplained.

### C3 QX qubit count

- Sources: emulator-backends, backends and backends/qx-simulator: 26 qubits; the catalogue's QX description: "up to 34 qubits (on the Lisa supercomputer)"; terms: free up to 26 and in principle 37 on the national supercomputer; catalogue `nqubits`: 10.
- Reconciliation: This account declares at most the catalogue's 10 qubits on QX (every retained QX run declared `qubit[10]`); a wider declaration is untested. Inference: the 34-qubit description dates from QI 1.0, when QX ran on SURF Lisa (from 2021-05-26 per release-notes-old); no source dates the text.

### C4 Ry emulator gate set

- Sources: ry-emulator-operational-specifics: X, Z, T, S, Rx, Rz plus INIT and RYD. Catalogue gateset: X, Z, Rx, Rz, T, S, H, CNOT with default decomposition CNOTDecomposer then XZXDecomposer, 9 qubits, 1024 shots maximum. Retained runs: a 9-qubit H/CNOT circuit with a 9-bit register failed with "RSP returned failure: error interpreting cQASM script"; a 2-qubit X-only circuit without a bit register completed (16.26 s for 1024 shots).
- Reconciliation: The two runs differ in width, gates and bit register at once, so the cause stays open; the gateset claim for H and CNOT is unconfirmed on this backend.

### C5 Tuna gate set

- Sources: tuna-operational-specifics accepts Rn, H, CNOT, CR, CRk and SWAP through decomposition; the catalogue gateset lists I, Rx, X, X90, mX90, Ry, Y, Y90, mY90, Rz, Z, S, T, Sdag, Tdag, H, CZ, init, measure, reset, barrier, wait and omits CNOT, CR, CRk, SWAP and Rn.
- Reconciliation: OpenAPI documents `gateset` as "the primary gatesets supported by the backend", and the default compiler config runs SWAP2CZDecomposer and CZDecomposer; the retained Tuna-17 teleport job with CNOT, SWAP and H completed (16384 shots). So the kbase list is the accepted set and the catalogue list is the primary set; CR, CRk and Rn on Tuna remain untested here.

### C6 wait syntax

- Sources: Tuna and Starmon-7 pages: `wait q[0:4], 11`. Specification: `wait(` *integer* `)` *qubit-argument*.
- Reconciliation: The specification governs, and the retained Tuna-17 runs submitted `wait(40) q[0]` and completed. The unit is one execution cycle, which the Tuna page fixes at 20 ns.

### C7 Initialization and measurement names

- Sources: qubit-basis-states, hardware-backends and the orphan pages use `prep_x/y/z`, `measure_x/y/z`, `measure_all`, `measure_parity`. cQASM 3.0 defines `init`, `reset`, `measure`, `measure(x, y, z)` and the aliases `measureX/Y/Z`.
- Reconciliation: QI runs cQASM 3.0 only (catalogue `languages`: cQASM 3.0, Python 3.11); the underscore names are cQASM 1.0.

### C8 Features in the latest spec

- Sources: The latest spec documents `measure(x,y,z)`, `measureX/Y/Z`, CCX and CSWAP; three-qubit-gates says Toffoli and Fredkin are not in the language; the catalogue QX gateset omits CCX, CSWAP and the two-qubit gates libqasm added in 2026 (CV, CY, DCNOT, ECR, ISWAP, InvSqrtSWAP, M, MS, SqrtISWAP, SqrtSWAP).
- Reconciliation: libqasm added these in 1.3.0 to 1.5.0 (2026-04-14 to 2026-10-02); the newest qx-simulator release 0.10.0 integrates libqasm 1.2.1. They are language features unverified on the platform; the catalogue gateset is what a submission may rely on.

### C9 Tuna page scope

- Sources: hardware-backends introduces the Tuna page as covering Tuna-5 and Tuna-9; the Tuna page itself covers Tuna-17 too.
- Reconciliation: The Tuna page governs; the index text predates Tuna-17 (April 2026).

### C10 Starmon-7 status

- Sources: starmon-7-operational-specifics describes a usable backend; backends/transmons says it ran February to December 2025; the catalogue has no Starmon-7 backend type.
- Reconciliation: Starmon-7 is unusable from this account.

### C11 Spin-2+ status and rules

- Sources: hardware-backends still lists Spin-2+ rules (register `qubit[2]`); spin-2-plus-operational-specifics allows `qubit[1-4]`; the spec appendix also accepts `#` comments and ignores `asm` blocks; backends calls Spin-2+ taken offline.
- Reconciliation: Spin-2+ is offline (catalogue backend 2, last heartbeat 2025-12-10, no backend type); its rules are historical. Between the two pages, the operational-specifics page and the spec appendix agree on `qubit[1-4]`.

### C12 Execution time limit

- Sources: backends/qx-simulator: jobs up to 30 minutes compute time. Catalogue `job_execution_time_limit`: QX 3600 s, Ry emulator 3600 s, Tuna 300 s.
- Reconciliation: The catalogue governs; the terms say over-limit executions are aborted.

### C13 Shot limits

- Sources: release-notes-old: Starmon-5 16384 maximum, 8192 default; hardware-backends: limited by acquisition memory. Catalogue: QX max 2048 (default 1024), Ry emulator max 1024 (default 1024), Tuna-5/9/17 max 131072 (default 8192).
- Reconciliation: The catalogue governs. Retained runs used 2048 on QX and 16384 on Tuna-17.

### C14 Bit position wording

- Sources: binary-register and displaying-and-downloading: "qubit 3 is the third bit from the right".
- Reconciliation: The spec orders bit strings with indices decreasing left to right, so b[0] is the rightmost bit and b[3] the fourth from the right. The spec's own sentence "b[n-1]b[n]...b[1]b[0]" carries a typo for b[n-1]b[n-2]...

### C15 Register width on hardware

- Sources: executing-your-algorithm: the qubit register must equal the chip's qubit count; hello-quantum-world: declare no more qubits than used; spin-2-plus page: `qubit[1-4]` on a two-data-qubit device.
- Reconciliation: For Tuna the rule is untested here: every retained Tuna-17 run declared `qubit[17]`. Declare the full chip width until a run shows otherwise.

### C16 SDK commands and imports

- Sources: software-development-kit and qi-tool: `qi files upload`, `qi results get`, `backend_type_id=3`, `pennylane_quantuminspire2.QI2Device`.
- Reconciliation: The SDK README at the pinned 4.1.0 tag governs: `qi run`, `qi jobs status|results|final-result`, `qi files compile`, `qi backends list|get`. The two old commands last appear in the 3.5.3 README and are gone from 4.0.0 (2026-08-07). The PennyLane plugin 0.15.5 module is `pennylane_quantuminspire`.

### C17 API root

- Sources: low-level-api: the REST API "can be found on https://api.quantum-inspire.com/".
- Reconciliation: The root answers 404; `/docs` and `/openapi.json` answer 200.

### C18 Compile strategy source

- Sources: opensquirrel points to the Spin-2+ and Starmon-7 pages for each backend's default strategy.
- Reconciliation: The catalogue's `default_compiler_config` governs: QX none; Tuna-5/9/17 SWAP2CZDecomposer then CZDecomposer; Ry emulator CNOTDecomposer then XZXDecomposer; no mapping, optimization or routing passes on any backend.

### C19 cQASM 1.0 code on cQASM 3.0 pages

- Sources: deutsch-jozsa carries `}` and `.measurement`; repetition-code comments out its correction; cqasm-binary-controlled-gates and cqasm-error-models are cQASM 1.0.
- Reconciliation: These examples do not parse as cQASM 3.0; QI accepts cQASM 3.0 only.

### C20 Tuning duration

- Sources: FAQ: tuning takes a few seconds to 30 minutes per backend; displaying-and-downloading attributes it to Spin-2; backends/spin-2-plus: full calibration 5 to 30 minutes, calibrated for more than 24 h.
- Reconciliation: The pages agree on the 30-minute ceiling; no page states a Tuna calibration cadence. The catalogue reports a `calibrating` status (Tuna-17 at snapshot time).

### C21 Result register

- Sources: hello-quantum-world: the bit register "is independent from the qubit register and can have an arbitrary size. This allows you to store for instance the results of intermediate measurements", and the histogram shows "the contents of the binary register". tuna-operational-specifics: results are a shots x bits array in bit-register order. qx-simulator releases: 0.7.3 took the measurement register out of `QuantumState`; no release through 0.10.0 exposes the bit register. Runs: the remote QX emulator returned 10-character strings for `qubit[10]`, `bit[20]` circuits with mid-circuit outcomes in `b[10..19]` (batch job 869986, 2026-10-17); qxelarator 0.10.0 returns the same shape.
- Reconciliation: QX returns its measurement register: one character per qubit, ordered by qubit index, holding each qubit's last outcome and 0 for an unmeasured qubit, whatever bit the measurement names. Tuna-17 returns the full bit register: circuits declaring `bit[34]` on `qubit[17]` came back as 34-character strings with every mid-circuit outcome present (batch job 870030, 2026-10-17, [run](../../../results/quantum_inspire/runs/2026-10-17T032034Z-readout_ringdown_tuna_17_P-batch-00)), so the kbase sentence holds for Tuna and fails for QX. Read QX results by qubit index and never from a mid-circuit bit ([qx-runs.md](qx-runs.md)).

### C22 Reset semantics

- Sources: the cQASM 3.0 reset instruction page: `reset` measures the qubit and flips it on outcome 1, so the qubit ends in |0> and leaves any entanglement, with the bit register untouched ([reset](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.md)). qx-simulator `QuantumState::update_data_after_reset` (src/qx/quantum_state.cpp, develop cc93e7fd2739) instead replaces each amplitude pair (a0x, a1x) over the other qubits' index x with the nonnegative real sqrt(|a0x|^2 + |a1x|^2). Runs: with q[0] in |1> and q[1] in |->, `reset q[0]` then H on q[1] read q[1] = 0 in 2048 of 2048 shots on the remote QX emulator (batch job 872957, 2026-10-18, [run](../../../results/quantum_inspire/runs/2026-10-18T161620Z-qx_reset_phase-batch-00)) and on qxelarator 0.10.0, where measure-and-flip reads 1; the same program with X in place of the reset read 1 in every shot.
- Reconciliation: The specification is the authority and both QX implementations depart from it whenever the reset qubit carries weight on |1> beside a register with relative phase. Their law then follows the sqrt map, so a QX dry run of a circuit that resets such a qubit tests syntax and plumbing only ([qx-runs.md](qx-runs.md)). Tuna's reset is a physical measure-and-reset, which the emulators do not model.

## cQASM 3.0 specification pages

Captured from https://qutech-delft.github.io/cQASM-spec/latest/appendices/ (MkDocs site built from QuTech-Delft/cQASM-spec gh-pages commit `91cff84b22553062cdb2aeebd968a1dd2a6a3ef6`; the newest tagged spec release is 3.0-beta2, 2025-02-18). Every page answered 200 and every external link resolved ([cqasm-spec/MANIFEST.json](cqasm-spec/MANIFEST.json)). [cqasm.md](cqasm.md) condenses the rules.

| Page | Content |
|---|---|
| [appendices/spin_2plus](cqasm-spec/appendices/spin_2plus.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/appendices/spin_2plus.html)) | The Spin-2+ subset (see C11). |
| [index](cqasm-spec/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/index.html)) | Version scope: cQASM 3.0 supersedes 1.x and the unfinished 2.0 draft and breaks backward compatibility. |
| [introduction/acknowledgements](cqasm-spec/introduction/acknowledgements.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/introduction/acknowledgements.html)) | Acknowledgements. |
| [introduction/context](cqasm-spec/introduction/context.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/introduction/context.html)) | cQASM 3.0 was developed for the Quantum Inspire overhaul. |
| [introduction/history](cqasm-spec/introduction/history.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/introduction/history.html)) | Placeholder ("Coming soon"). |
| [language_specification/expressions/builtin_functions](cqasm-spec/language_specification/expressions/builtin_functions.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html)) | sqrt, exp, log, abs, trig and hyperbolic functions on real values. |
| [language_specification/expressions/indices](cqasm-spec/language_specification/expressions/indices.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/indices.html)) | Index lists and inclusive ranges `i:j`. |
| [language_specification/expressions/predefined_constants](cqasm-spec/language_specification/expressions/predefined_constants.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html)) | `pi`, `tau`, `eu`. |
| [language_specification/index](cqasm-spec/language_specification/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html)) | Statement list, case sensitivity, `.cq` extension, qubit-state and bit-string ordering (indices decrease left to right; matrices use the reversed textbook order). |
| [language_specification/statements/assembly_declaration](cqasm-spec/language_specification/statements/assembly_declaration.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/assembly_declaration.html)) | `asm(Backend) '''...'''` passes raw text to one backend and fixes its position. |
| [language_specification/statements/instructions/control_instructions/barrier_instruction](cqasm-spec/language_specification/statements/instructions/control_instructions/barrier_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html)) | `barrier` blocks scheduling across it; consecutive barriers may form a uniform barrier. |
| [language_specification/statements/instructions/control_instructions/wait_instruction](cqasm-spec/language_specification/statements/instructions/control_instructions/wait_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html)) | `wait(n) q` delays by n execution cycles and acts as a barrier. |
| [language_specification/statements/instructions/non_unitary_instructions/init_instruction](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/init_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html)) | `init` only before any non-control instruction on that qubit. |
| [language_specification/statements/instructions/non_unitary_instructions/measure_instruction](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html)) | `b = measure q`, `measure(x,y,z)`, aliases `measureX/Y/Z`; SGMQ needs equal bit and qubit counts. |
| [language_specification/statements/instructions/non_unitary_instructions/reset_instruction](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html)) | `reset` measures and conditionally flips; leaves the bit register untouched. |
| [language_specification/statements/instructions/single-gate-multiple-qubit-notation](cqasm-spec/language_specification/statements/instructions/single-gate-multiple-qubit-notation.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html)) | SGMQ is syntactic sugar, not simultaneity; operands unpack pairwise. |
| [language_specification/statements/instructions/unitary_instructions](cqasm-spec/language_specification/statements/instructions/unitary_instructions.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html)) | Named gates with parameters; modifiers `inv.`, `pow(a).`, `ctrl.` on single-qubit gates only, applied right to left. |
| [language_specification/statements/variable_declarations/bit_register_declaration](cqasm-spec/language_specification/statements/variable_declarations/bit_register_declaration.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/bit_register_declaration.html)) | `bit[N] name`; required before measure (its single-bit example mistakenly declares `qubit b`). |
| [language_specification/statements/variable_declarations/qubit_register_declaration](cqasm-spec/language_specification/statements/variable_declarations/qubit_register_declaration.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html)) | `qubit[N] name` or `qubit name`; qubits start in |0>. |
| [language_specification/statements/version_statement](cqasm-spec/language_specification/statements/version_statement.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/version_statement.html)) | `version 3.0` (minor optional) first and once. |
| [language_specification/tokens/identifiers](cqasm-spec/language_specification/tokens/identifiers.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html)) | Letters, digits, underscore; no leading digit; keywords reserved. |
| [language_specification/tokens/keywords](cqasm-spec/language_specification/tokens/keywords.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html)) | Twelve keywords: asm, barrier, bit, ctrl, init, inv, measure, pow, qubit, reset, version, wait. |
| [language_specification/tokens/literals](cqasm-spec/language_specification/tokens/literals.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html)) | 64-bit signed integers and IEEE 754 doubles. |
| [language_specification/tokens/newlines](cqasm-spec/language_specification/tokens/newlines.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/newlines.html)) | Newline or `;` terminates a statement. |
| [language_specification/tokens/operators_and_punctuators](cqasm-spec/language_specification/tokens/operators_and_punctuators.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/operators_and_punctuators.html)) | Operator and punctuator table. |
| [language_specification/tokens/raw_text_string](cqasm-spec/language_specification/tokens/raw_text_string.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html)) | Triple-quoted raw text for `asm` bodies. |
| [language_specification/tokens/whitespace_and_comments](cqasm-spec/language_specification/tokens/whitespace_and_comments.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/whitespace_and_comments.html)) | `//` and `/* */` comments; only comments precede `version`. |
| [language_specification/types](cqasm-spec/language_specification/types.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html)) | Types Qubit, QubitArray, Bit, BitArray. |
| [standard_gate_set/index](cqasm-spec/standard_gate_set/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html)) | The 37 named gates: 20 single-qubit, 17 multi-qubit. |
| [standard_gate_set/multi_qubit/mq_CCX](cqasm-spec/standard_gate_set/multi_qubit/mq_CCX.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CCX.html)) | Gate `CCX`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CNOT](cqasm-spec/standard_gate_set/multi_qubit/mq_CNOT.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html)) | Gate `CNOT`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CR](cqasm-spec/standard_gate_set/multi_qubit/mq_CR.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CR.html)) | Gate `CR`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CRk](cqasm-spec/standard_gate_set/multi_qubit/mq_CRk.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html)) | Gate `CRk`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CSWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_CSWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CSWAP.html)) | Gate `CSWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CV](cqasm-spec/standard_gate_set/multi_qubit/mq_CV.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CV.html)) | Gate `CV`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CY](cqasm-spec/standard_gate_set/multi_qubit/mq_CY.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CY.html)) | Gate `CY`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_CZ](cqasm-spec/standard_gate_set/multi_qubit/mq_CZ.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CZ.html)) | Gate `CZ`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_DCNOT](cqasm-spec/standard_gate_set/multi_qubit/mq_DCNOT.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_DCNOT.html)) | Gate `DCNOT`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_ECR](cqasm-spec/standard_gate_set/multi_qubit/mq_ECR.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ECR.html)) | Gate `ECR`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_ISWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_ISWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ISWAP.html)) | Gate `ISWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_InvSqrtSWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.html)) | Gate `InvSqrtSWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_M](cqasm-spec/standard_gate_set/multi_qubit/mq_M.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_M.html)) | Gate `M`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_MS](cqasm-spec/standard_gate_set/multi_qubit/mq_MS.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_MS.html)) | Gate `MS`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_SWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_SWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SWAP.html)) | Gate `SWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_SqrtISWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_SqrtISWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SqrtISWAP.html)) | Gate `SqrtISWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/multi_qubit/mq_SqrtSWAP](cqasm-spec/standard_gate_set/multi_qubit/mq_SqrtSWAP.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SqrtSWAP.html)) | Gate `SqrtSWAP`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_H](cqasm-spec/standard_gate_set/single_qubit/sq_H.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html)) | Gate `H`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_I](cqasm-spec/standard_gate_set/single_qubit/sq_I.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_I.html)) | Gate `I`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Rn](cqasm-spec/standard_gate_set/single_qubit/sq_Rn.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)) | Gate `Rn`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Rx](cqasm-spec/standard_gate_set/single_qubit/sq_Rx.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rx.html)) | Gate `Rx`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Ry](cqasm-spec/standard_gate_set/single_qubit/sq_Ry.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Ry.html)) | Gate `Ry`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Rz](cqasm-spec/standard_gate_set/single_qubit/sq_Rz.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rz.html)) | Gate `Rz`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_S](cqasm-spec/standard_gate_set/single_qubit/sq_S.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_S.html)) | Gate `S`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Sdag](cqasm-spec/standard_gate_set/single_qubit/sq_Sdag.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Sdag.html)) | Gate `Sdag`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_T](cqasm-spec/standard_gate_set/single_qubit/sq_T.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_T.html)) | Gate `T`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Tdag](cqasm-spec/standard_gate_set/single_qubit/sq_Tdag.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Tdag.html)) | Gate `Tdag`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_U](cqasm-spec/standard_gate_set/single_qubit/sq_U.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_U.html)) | Gate `U`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_X](cqasm-spec/standard_gate_set/single_qubit/sq_X.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html)) | Gate `X`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_X90](cqasm-spec/standard_gate_set/single_qubit/sq_X90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X90.html)) | Gate `X90`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Y](cqasm-spec/standard_gate_set/single_qubit/sq_Y.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Y.html)) | Gate `Y`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Y90](cqasm-spec/standard_gate_set/single_qubit/sq_Y90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Y90.html)) | Gate `Y90`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Z](cqasm-spec/standard_gate_set/single_qubit/sq_Z.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z.html)) | Gate `Z`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_Z90](cqasm-spec/standard_gate_set/single_qubit/sq_Z90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z90.html)) | Gate `Z90`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_mX90](cqasm-spec/standard_gate_set/single_qubit/sq_mX90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mX90.html)) | Gate `mX90`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_mY90](cqasm-spec/standard_gate_set/single_qubit/sq_mY90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mY90.html)) | Gate `mY90`: identifier, matrix, properties, examples. |
| [standard_gate_set/single_qubit/sq_mZ90](cqasm-spec/standard_gate_set/single_qubit/sq_mZ90.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mZ90.html)) | Gate `mZ90`: identifier, matrix, properties, examples. |

## SDK documentation

Verbatim sources at the commits the release tags resolve to: quantuminspire 4.1.0 (`054a4f0be229`); qiskit-quantuminspire 0.18.5 (`fbe5256e6671`); pennylane-quantuminspire 0.15.5 (`0f7a6fffd396`).

| File | Content |
|---|---|
| [README.md](sdk/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/quantuminspire/054a4f0be22983a5d515c31a24881bc0d875463d/README.md)) | quantuminspire 4.1.0 CLI: `qi login/logout`, `qi run`, projects, algorithms, jobs, backends, `qi files compile` (default stage Decomposition), config. |
| [qiskit-quantuminspire/README.md](sdk/qiskit-quantuminspire/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/README.md)) | Plugin overview and doc links. |
| [qiskit-quantuminspire/docs/index.rst](sdk/qiskit-quantuminspire/docs/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/index.rst)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/contributing.md](sdk/qiskit-quantuminspire/docs/contributing.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/contributing.md)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/api/modules.rst](sdk/qiskit-quantuminspire/docs/api/modules.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/api/modules.rst)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/getting_started/index.rst](sdk/qiskit-quantuminspire/docs/getting_started/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/getting_started/index.rst)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/getting_started/installation.md](sdk/qiskit-quantuminspire/docs/getting_started/installation.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/getting_started/installation.md)) | Install with pip and log in with `qi login`. |
| [qiskit-quantuminspire/docs/getting_started/submitting.md](sdk/qiskit-quantuminspire/docs/getting_started/submitting.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/getting_started/submitting.md)) | Fetch a backend from `QIProvider` and run a circuit. |
| [qiskit-quantuminspire/docs/hybrid/index.rst](sdk/qiskit-quantuminspire/docs/hybrid/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/index.rst)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/hybrid/basics.md](sdk/qiskit-quantuminspire/docs/hybrid/basics.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/basics.md)) | Hybrid-algorithm file format (`execute` with a `QuantumInterface`, `finalize`). |
| [qiskit-quantuminspire/docs/hybrid/leveraging_qiskit.md](sdk/qiskit-quantuminspire/docs/hybrid/leveraging_qiskit.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/leveraging_qiskit.md)) | Hybrid use of Qiskit features. |
| [qiskit-quantuminspire/docs/hybrid/hqca_circuit.py](sdk/qiskit-quantuminspire/docs/hybrid/hqca_circuit.py) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/hqca_circuit.py)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/hybrid/hydrogen.py](sdk/qiskit-quantuminspire/docs/hybrid/hydrogen.py) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/hydrogen.py)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/notebooks/index.rst](sdk/qiskit-quantuminspire/docs/notebooks/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/notebooks/index.rst)) | Sphinx index, example script or notebook. |
| [qiskit-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb](sdk/qiskit-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/notebooks/basic_circuit_execution.ipynb)) | Sphinx index, example script or notebook. |
| `sdk/qiskit-quantuminspire/docs/notebooks/Super Dense Coding.ipynb` | Sphinx index, example script or notebook. |
| `sdk/qiskit-quantuminspire/docs/notebooks/QI2 Performance Test.ipynb` | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/README.md](sdk/pennylane-quantuminspire/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/README.md)) | Plugin overview and doc links. |
| [pennylane-quantuminspire/docs/index.rst](sdk/pennylane-quantuminspire/docs/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/index.rst)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/contributing.md](sdk/pennylane-quantuminspire/docs/contributing.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/contributing.md)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/api/modules.rst](sdk/pennylane-quantuminspire/docs/api/modules.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/api/modules.rst)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/getting_started/index.rst](sdk/pennylane-quantuminspire/docs/getting_started/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/getting_started/index.rst)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/getting_started/installation.md](sdk/pennylane-quantuminspire/docs/getting_started/installation.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/getting_started/installation.md)) | Install with pip and log in with `qi login`. |
| [pennylane-quantuminspire/docs/getting_started/submitting.rst](sdk/pennylane-quantuminspire/docs/getting_started/submitting.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/getting_started/submitting.rst)) | `QIDevice` from a `QIProvider` backend; `Asm` instruction for assembly declarations; non-expval measurements need per-shot backends. |
| [pennylane-quantuminspire/docs/hybrid/index.rst](sdk/pennylane-quantuminspire/docs/hybrid/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/hybrid/index.rst)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/hybrid/basics.md](sdk/pennylane-quantuminspire/docs/hybrid/basics.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/hybrid/basics.md)) | Hybrid-algorithm file format (`execute` with a `QuantumInterface`, `finalize`). |
| [pennylane-quantuminspire/docs/hybrid/leveraging_pennylane.md](sdk/pennylane-quantuminspire/docs/hybrid/leveraging_pennylane.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/hybrid/leveraging_pennylane.md)) | Hybrid use of PennyLane features. |
| [pennylane-quantuminspire/docs/hybrid/simple.py](sdk/pennylane-quantuminspire/docs/hybrid/simple.py) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/hybrid/simple.py)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/notebooks/index.rst](sdk/pennylane-quantuminspire/docs/notebooks/index.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/notebooks/index.rst)) | Sphinx index, example script or notebook. |
| [pennylane-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb](sdk/pennylane-quantuminspire/docs/notebooks/basic_circuit_execution.ipynb) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/notebooks/basic_circuit_execution.ipynb)) | Sphinx index, example script or notebook. |

## Component release histories

| Component | Files | Releases | Newest |
|---|---|---|---|
| quantuminspire | [md](releases/quantuminspire.md), [json](releases/quantuminspire.json) ([live](https://github.com/QuTech-Delft/quantuminspire/releases)) | 34 | 4.1.0 (2026-09-25) |
| cQASM-spec | [md](releases/cQASM-spec.md), [json](releases/cQASM-spec.json) ([live](https://github.com/QuTech-Delft/cQASM-spec/releases)) | 2 | 3.0-beta2 (2025-02-18) |
| libqasm | [md](releases/libqasm.md), [json](releases/libqasm.json) ([live](https://github.com/QuTech-Delft/libqasm/releases)) | 27 | 1.6.0 (2026-10-14) |
| OpenSquirrel | [md](releases/OpenSquirrel.md), [json](releases/OpenSquirrel.json) ([live](https://github.com/QuTech-Delft/OpenSquirrel/releases)) | 12 | 0.9.1 (2026-07-30) |
| OpenQL | [md](releases/OpenQL.md), [json](releases/OpenQL.json) ([live](https://github.com/QuTech-Delft/OpenQL/releases)) | 21 | 0.12.2 (2024-01-09) |
| qx-simulator | [md](releases/qx-simulator.md), [json](releases/qx-simulator.json) ([live](https://github.com/QuTech-Delft/qx-simulator/releases)) | 30 | 0.10.0 (2025-08-28) |
| qiskit-quantuminspire | [md](releases/qiskit-quantuminspire.md), [json](releases/qiskit-quantuminspire.json) ([live](https://github.com/QuTech-Delft/qiskit-quantuminspire/releases)) | 32 | 0.18.5 (2026-10-05) |
| pennylane-quantuminspire | [md](releases/pennylane-quantuminspire.md), [json](releases/pennylane-quantuminspire.json) ([live](https://github.com/QuTech-Delft/pennylane-quantuminspire/releases)) | 24 | 0.15.5 (2026-10-05) |
| quantify-scheduler | [md](releases/quantify-scheduler.md), [json](releases/quantify-scheduler.json) ([live](https://gitlab.com/quantify-os/quantify-scheduler/-/releases)) | 43 | v0.28.0 (2026-03-19) |

[release-notes.md](release-notes.md) digests the changes that affect usage.

## API description

[api/openapi.json](api/openapi.json) ([live](https://api.quantum-inspire.com/openapi.json)) is the compute job manager's OpenAPI 3 description (title "Quantum Inspire 2", version 0.1.0); its `BackendType` schema defines the catalogue fields cited above.

