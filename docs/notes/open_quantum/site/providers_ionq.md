> Full piece: [https://www.openquantum.com/providers/ionq](https://www.openquantum.com/providers/ionq)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --site (urllib, pandoc);
> fetched HTML sha256 6cabcf5ab49673f4441ddfbaef2e22c6f19fb09c1dd523805fa1f1fcb83d24ce.

![IonQ logo](https://www.openquantum.com/ionq-logo.svg)

# IonQ Trapped-Ion Quantum Computers Now Available on Open Quantum

Access IonQ's trapped-ion quantum computers featuring all-to-all qubit connectivity, high gate fidelities, and coherence times measured in seconds.

IonQ builds trapped-ion quantum computers using ytterbium ions confined in electromagnetic traps. Their Forte systems provide high-performance quantum computing with 99.6% two-qubit gate fidelity and software-configurable qubit topology. These systems feature all-to-all connectivity, meaning any qubit can interact directly with any other without SWAP gate overhead, and coherence times measured in seconds rather than microseconds. This combination of high fidelity, full connectivity, and long coherence makes IonQ hardware well-suited for algorithms requiring dense qubit interaction, such as quantum chemistry simulations, optimization, and variational algorithms. Through Open Quantum, you can access IonQ Forte systems using the same unified API you use for Rigetti, IQM, and AQT backends, with \$50 of free quantum compute every 90 days to start running circuits and comparing results across providers immediately.

## About IonQ

IonQ was founded in 2015 by Chris Monroe and Jungsang Kim, building on decades of trapped-ion research at the University of Maryland and Duke University. Headquartered in College Park, Maryland, and publicly traded on the NYSE under the ticker IONQ, the company has positioned itself as the provider of the most accurate quantum computers available.

IonQ's trapped-ion approach uses ytterbium ions manipulated with laser pulses. This yields inherently identical qubits with coherence times of approximately 1,000 milliseconds, orders of magnitude longer than superconducting alternatives. The all-to-all connectivity means any qubit can interact with any other without the SWAP routing overhead that limits grid-connected architectures.

IonQ has demonstrated a world-record 99.99% two-qubit gate fidelity (October 2025) and is pursuing a networked quantum computing roadmap that envisions linking multiple ion-trap modules to scale beyond single-trap limits, targeting 256 qubits by 2026 and 10,000+ physical qubits by 2027.

### All-to-All Connectivity

Any qubit can interact with any other qubit directly. No SWAP gates needed, dramatically reducing circuit depth for most algorithms.

### High Gate Fidelities

99.6% two-qubit gate fidelity on Forte systems, with single-qubit fidelity of 99.95% and coherence times measured in seconds.

### Enterprise Customers

AstraZeneca, Hyundai, Airbus, NVIDIA, and Ansys are among IonQ's active enterprise partners across drug discovery, optimization, and simulation.

## IonQ Hardware on Open Quantum

| System | Qubits | 2Q Gate Fidelity | Connectivity | Best For |
|----|----|----|----|----|
| [Forte-1View live specs](https://www.openquantum.com/providers/ionq/forte-1 "View live device profile: qubit topology, native gates, features, and limits") | 36 | 99.6% | All-to-all (full) | Commercial applications |
| [Forte EnterpriseView live specs](https://www.openquantum.com/providers/ionq/forte-ent "View live device profile: qubit topology, native gates, features, and limits") | 36 | 99.6% | All-to-all (full) | Commercial applications |
| Aria-1 Sunset 2025 | 25 | 99.4% | All-to-all (full) | Replaced by Forte |
| Aria-2 Sunset 2025 | 25 | 99.4% | All-to-all (full) | Replaced by Forte |

![IonQ trapped-ion quantum computing system](https://www.openquantum.com/_next/image?url=%2Fionq-system.jpg&w=1920&q=75)

### All-to-All Connectivity Advantage

IonQ's trapped-ion architecture provides full connectivity between all qubits. In practical terms, this means a two-qubit gate between any pair of qubits is a native operation, with no SWAP overhead. For algorithms like QAOA, VQE, and quantum chemistry simulations that require heavy qubit interaction, all-to-all connectivity dramatically reduces circuit depth and the total number of gates, leading to higher-fidelity results.

### Key Performance Highlights

- 99.6% two-qubit gate fidelity on Forte systems
- T2 coherence time: ~1,000 milliseconds (1 second)
- Single-qubit gate fidelity: 99.95%
- Software-configurable qubit topology (Forte)

## Why Run on IonQ via Open Quantum?

### Unified API

Access IonQ, Rigetti, AQT, and IQM hardware through a single SDK. No vendor-specific setup required.

### No Vendor Lock-In

Write your circuit once and run it on any backend. Compare trapped-ion vs superconducting results on the same circuit.

### Cross-Vendor Benchmarking

Compare IonQ's all-to-all trapped-ion results with Rigetti and IQM superconducting results side by side.

### Free \$50 of Compute

Every new Open Quantum account includes \$50 of free quantum compute, refreshed every 90 days. Start running circuits on IonQ immediately.

## Getting Started

Submit your first circuit to IonQ's trapped-ion hardware in minutes. Install the Open Quantum SDK, authenticate, and select the IonQ backend.

``` python
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

scheduler = SchedulerClient()  # uses OPENQUANTUM_CLIENT_ID/SECRET env vars

config = JobSubmissionConfig(
    backend_class_id="ionq:forte-1",  # or "ionq:forte-ent"
    name="Bell State on IonQ",
    shots=100,
)

job = scheduler.submit_job(config, file_path="bell_state.qasm")

result = scheduler.download_job_output(job)
```

[Run Your First Circuit on IonQ Hardware](https://www.openquantum.com/create-job)

[](https://www.openquantum.com/signup)

\$50 of Free Quantum Compute

Every new Open Quantum account includes \$50 of free quantum compute credits, refreshed every 90 days. Run circuits on IonQ, Rigetti, AQT, and IQM hardware at no cost.

## Frequently Asked Questions

What is IonQ Forte?

What is all-to-all qubit connectivity?

How do trapped-ion quantum computers compare to superconducting?

What enterprise use cases does IonQ hardware support?

How do I run a circuit on IonQ via Open Quantum?

## Explore Other Quantum Hardware Providers

[](https://www.openquantum.com/providers/rigetti)

### Rigetti

Cepheus-1 \| 108 qubits

Superconducting

99.1% CZ fidelity, modular chiplet architecture

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
