# Python stack for IQM Resonance

This note inventories the client stack the `iqm-resonance-stack` Arch package
installs under `/opt/iqm-resonance-stack` (interpreter `iqm-python`, Python
3.13.15 from the `python313` package) and maps what each IQM library
computes. Versions come from `importlib.metadata` in that environment; the
complete list of 185 distributions, with license, import names and
requirements, is [python-stack-versions.json](python-stack-versions.json).
Installation and the version caps that force a separate environment are in
[README.md](README.md#installation).

The repository's own `$PYTHON` (Python 3.14, Arch packages) never imports
this stack. `scripts/iqm_platform.py` and `scripts/iqm_mcp_server.py` talk to
Resonance over HTTPS with the standard library and the system's mcp 1.29;
anything that compiles, transpiles or simulates for IQM runs under
`iqm-python`.

## IQM libraries (IQM OS 4.7.0 constraints)

| Distribution | Import | Version | License (as declared) | Role |
|---|---|---|---|---|
| iqm-client | `iqm.iqm_client`, `iqm.iqm_server_client`, `iqm.qiskit_iqm`, `iqm.cirq_iqm`, `iqm.qrisp_iqm` | 36.0.0 | Apache-2.0 | IQM Server client, circuit jobs, pulse-level access, Qiskit, Cirq and Qrisp integrations, fake backends, MOVE routing |
| iqm-station-control-client | `iqm.station_control` | 14.0.0 | Apache | station-control models (circuit job body, DD strategy, heralding), `TokenManager`, sweep and run protobufs |
| iqm-pulse | `iqm.pulse` | 15.0.0 | Apache | gate implementations (DRAG, Slepian CRF, MOVE), pulse timing, playlists, schedule builder |
| iqm-pulla | `iqm.cpc` | 15.0.0 | Apache-2.0 | circuit-to-pulse compiler (`iqm.cpc.compiler`, standard DD strategy); the `Pulla` client moved into iqm-client |
| iqm-exa-common | `exa.common` | 29.0.0 | Apache | parameters, sweeps, settings trees of the calibration data |
| iqm-data-definitions | `iqm.data_definitions` | 3.1.0 | Apache | protobuf definitions of RunDefinition and SweepTaskRequest |
| iqm-benchmarks | `iqm.benchmarks` | 3.0.0 | Apache | Clifford and interleaved RB, mirror RB, EPLG, GHZ, graph state, GST, quantum volume, Q-score, CLOPS, coherence |
| iqm-qubit-selector | `iqm.qubit_selector` | 1.2.0 | Apache | qubit layout selection from calibration metrics |
| iqm-error-reduction-tools | `iqm.error_reduction_tools` | 0.3.0 | none declared | readout error mitigation (REMWorkflow) and Pauli twirling |
| iqm-qaoa | `iqm.qaoa` | 3.0.0 | "Copyright (c) 2024-2025 IQM Quantum Computers", no open-source grant | QAOA problem instances, training, circuit construction |

## Integrations and numerics

| Distribution | Version | Role |
|---|---|---|
| qiskit, qiskit-aer | 2.1.2, 0.17.2 | IQMBackend, transpiler plugins, fake-backend simulation; the repository's own stack runs qiskit 2.5.2 and 2.6.0, so circuits cross between the two as QASM or IQM JSON, never as pickled objects |
| qiskit-ibm-runtime | 0.43.1 | pulled by iqm-benchmarks; unused for IQM jobs |
| cirq-core | 1.7.0 | `iqm.cirq_iqm` devices and sampler |
| qrisp | 0.9.10 (EPL-2.0 or GPL-2.0 with Classpath exception) | the high-level language IQM's July 2025 Resonance upgrade made a default interface; `iqm.qrisp_iqm` backends, PLASMA layout, QEC detector experiments |
| stim, PyMatching | 1.16.0, 2.4.0 | stabilizer simulation and decoding behind `iqm.qrisp_iqm.qec` |
| mthree | 3.0.0 | matrix-free readout mitigation in iqm-benchmarks (built from its sdist) |
| numpy, scipy, sympy | 2.3.5, 1.18.1, 1.13.0 | numerics; IQM OS 4.7 requires NumPy >= 2.2 |
| pydantic | 2.12.5 | client models (capped below 2.13) |
| networkx, rustworkx | 3.7, 0.17.1 | topology and routing |
| lmfit, xarray, pandas, matplotlib | 1.3.4, 2026.9.0, 3.0.6, 3.11.2 | benchmark fitting, data and plots |
| numba, llvmlite | 0.63.1, 0.46.0 | Cirq extra's compiled kernels |
| protobuf, grpcio, opentelemetry-sdk | 7.36.2, 1.84.0, 1.45.1 | station-control transport and tracing |
| requests | 2.34.2 | HTTP transport of iqm-client |

## Repository use

| Item | Where |
|---|---|
| IQM Server REST and GraphQL | `scripts/iqm_platform.py` (snapshot, check, refresh), `scripts/iqm_mcp_server.py` |
| `iqm-python` stack | no repository script imports it yet; a case that transpiles for IQM runs its generator under `iqm-python` and retains the transpiled circuits with the calibration set id they were planned against |
