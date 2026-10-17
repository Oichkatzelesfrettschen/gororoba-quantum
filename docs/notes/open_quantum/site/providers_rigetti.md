> Full piece: [https://www.openquantum.com/providers/rigetti](https://www.openquantum.com/providers/rigetti)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --site (urllib, pandoc);
> fetched HTML sha256 e7818ffb915386919db127e35b8e65d2977a7f4b243a420f900a3e260a2e5601.

![Rigetti Computing logo](https://www.openquantum.com/rigetti-logo.svg)

# Rigetti Cepheus: Superconducting Quantum Computing at Scale on Open Quantum

Access Rigetti's 108-qubit Cepheus-1 superconducting processor with 99.1% CZ gate fidelity and 99.9% single-qubit fidelity through a unified cloud API.

Rigetti's Cepheus-1-108Q is a 108-qubit superconducting quantum processor built on transmon qubits arranged in a square lattice topology with tunable couplers. It achieves 99.1% two-qubit CZ gate fidelity and 99.9% single-qubit gate fidelity, optimized for fast gate times while reducing coherent errors. The tunable coupler architecture allows dynamic control over qubit-qubit coupling strength, enabling parametric compilation techniques that optimize circuit execution. The square lattice provides 4-fold nearest-neighbor connectivity, offering more routing options than linear or heavy-hex topologies and reducing SWAP overhead for circuits requiring non-adjacent qubit interactions. Fabricated at Rigetti's Fab-1 facility using superconducting through-silicon vias and flip-chip cap bonding, Cepheus-1 is designed for production quantum workloads and hybrid quantum-classical algorithms. Rigetti Cepheus-1 is available on Open Quantum through the same unified API used to access QPUs from IonQ, IQM, and AQT, with \$50 of free quantum compute credits every 90 days to start running circuits and comparing results across providers immediately.

## About Rigetti Computing

Founded in 2013 by Chad Rigetti, a former IBM researcher, Rigetti Computing is a full-stack quantum computing company headquartered in Berkeley, California. The company designs, fabricates, and operates its own superconducting quantum processors in its dedicated Fab-1 fabrication facility, making it one of the few quantum companies with end-to-end vertical integration.

Rigetti developed the Quil (Quantum Instruction Language) programming language and the Forest SDK, an open-source developer suite that includes the pyQuil Python library, the Rigetti Quil Compiler, and the Quantum Virtual Machine. The Forest SDK provides fine-grained pulse-level control for researchers who need direct hardware access.

Publicly traded on NASDAQ under the ticker RGTI, Rigetti entered a \$200M strategic partnership with Quanta Computer in 2025 to scale quantum processor production and establish co-located quantum-classical data centers.

### Full-Stack Vertical Integration

Rigetti designs and fabricates its own QPUs in-house at Fab-1, maintaining control over the entire hardware stack from chip design to cloud delivery.

### Modular Chiplet Architecture

The Cepheus-1-36Q (August 2025) demonstrated the modular chiplet architecture with interconnected 9-qubit chiplets. Cepheus-1-108Q is the production realization, scaling to 108 qubits using superconducting through-silicon vias and flip-chip cap bonding.

### Multi-Cloud Availability

Rigetti hardware is available via Rigetti QCS, Amazon Braket, Microsoft Azure Quantum, and now Open Quantum.

## Rigetti Hardware on Open Quantum

| System | Qubits | 2Q Gate Fidelity | Connectivity | Best For |
|----|----|----|----|----|
| [Cepheus-1-108QView live specs](https://www.openquantum.com/providers/rigetti/cepheus-1-108q "View live device profile: qubit topology, native gates, features, and limits") | 108 | 99.1% CZ | Square lattice (4-fold nearest-neighbor) | Production workloads, hybrid algorithms |
| Ankaa-3 Sunset Q2 '26 | 84 | 99.0% CZ | Square lattice (4-fold nearest-neighbor) | Replaced by Cepheus-1 |

![Rigetti Ankaa superconducting quantum processor chip](https://www.openquantum.com/_next/image?url=%2Frigetti-ankaa-chip.png&w=1920&q=75)

### Fast Gates, Reduced Coherent Errors

Rigetti's Cepheus-1 uses native CZ (Controlled-Z) entangling gates optimized for fast execution while reducing coherent errors. Fast gates mean more operations can be completed within the coherence window of the qubits (T1: 25 microseconds, T2: 10 microseconds), enabling deeper circuits and more complex algorithms. The tunable coupler architecture allows dynamic control over qubit-qubit coupling strength, enabling parametric compilation techniques that further optimize circuit execution.

### Key Performance Highlights

- 99.1% two-qubit CZ gate fidelity, 99.9% single-qubit gate fidelity
- T1: 25 microseconds, T2: 10 microseconds
- Square lattice with 4-fold connectivity for efficient circuit mapping
- Tunable coupler architecture for efficient qubit-qubit coupling

## Why Run Rigetti Circuits on Open Quantum?

### Unified API

Access Rigetti, IonQ, AQT, and IQM hardware through a single SDK. No need to learn Quil or set up the Forest SDK.

### No Vendor Lock-In

Write your circuit once in Qiskit or PennyLane and run it on any backend. Switch between vendors freely.

### Cross-Vendor Benchmarking

Compare Rigetti superconducting results with IonQ and AQT trapped-ion results on the same circuit.

### Free \$50 of Compute

Every new Open Quantum account includes \$50 of free quantum compute, refreshed every 90 days. Start running circuits on Rigetti immediately.

## Getting Started

Submit your first circuit to Rigetti's Cepheus-1 in minutes. Install the Open Quantum SDK, authenticate, and select the Rigetti backend.

``` python
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

scheduler = SchedulerClient()  # uses OPENQUANTUM_CLIENT_ID/SECRET env vars

config = JobSubmissionConfig(
    backend_class_id="rigetti:cepheus-1-108q",
    name="Bell State on Rigetti",
    shots=100,
)

job = scheduler.submit_job(config, file_path="bell_state.qasm")

result = scheduler.download_job_output(job)
```

[Run Your First Circuit on Rigetti Hardware](https://www.openquantum.com/create-job)

[](https://www.openquantum.com/signup)

\$50 of Free Quantum Compute

Every new Open Quantum account includes \$50 of free quantum compute credits, refreshed every 90 days. Run circuits on Rigetti, IonQ, AQT, and IQM hardware at no cost.

## Frequently Asked Questions

What is Rigetti's Cepheus quantum processor?

What is a superconducting quantum computer?

How many qubits does Rigetti Cepheus-1 have?

What is the gate fidelity of Rigetti's Cepheus processor?

How does Rigetti's square lattice connectivity work?

Can I use Qiskit with Rigetti hardware on Open Quantum?

## Explore Other Quantum Hardware Providers

[](https://www.openquantum.com/providers/ionq)

### IonQ

Forte & Forte Enterprise \| 36 qubits

Trapped Ion

All-to-all connectivity, 99.6% 2Q fidelity, 36 algorithmic qubits

Learn more

[](https://www.openquantum.com/providers/iqm)

### IQM

Garnet & Emerald \| 20-54 qubits

Superconducting

99.5% CZ fidelity, European HPC integration

Learn more

[](https://www.openquantum.com/providers/aqt)

### AQT

IBEX Q1 \| 12 qubits

Trapped Ion

Fully-connected topology, room temperature, rack-mounted

Learn more
