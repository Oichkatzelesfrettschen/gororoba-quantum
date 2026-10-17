> Full piece: [https://www.openquantum.com/providers/iqm](https://www.openquantum.com/providers/iqm)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --site (urllib, pandoc);
> fetched HTML sha256 9b25298f8ae0ddde7828be96e81211a0a3c06ee2a98c12a61cedc9bb57a911e0.

![IQM Quantum Computers logo](https://www.openquantum.com/_next/image?url=%2Fiqm-logo.png&w=640&q=75)

# IQM: European Quantum Hardware Built for HPC: Now on Open Quantum

Access IQM's superconducting quantum processors, purpose-built for HPC integration and deployed at Europe's leading supercomputing centers, through a unified cloud API.

IQM Quantum Computers builds superconducting quantum processors in Espoo, Finland, using a co-design methodology that tailors QPU architecture to specific application needs. Their Garnet system offers 20 computational qubits with 99.51% median CZ gate fidelity, while Emerald scales the same proven architecture to 54 qubits with 99.5% median CZ fidelity. Both processors use a square lattice topology with tunable couplers, providing a balance of connectivity and scalability that natively supports surface-code error correction. IQM systems power quantum computing at major European supercomputing centers, including the LUMI supercomputer ecosystem in Finland, the Leibniz Supercomputing Centre in Munich, and IT4Innovations in the Czech Republic. Through IQM Garnet and Emerald are available on Open Quantum through the same unified API used to access QPUs from Rigetti, IonQ, and AQT , with \$50 of free quantum compute every 90 days to start running circuits and comparing results across providers immediately.

## About IQM Quantum Computers

IQM was founded in 2018 in Espoo, Finland, with a focus on building superconducting quantum processors specifically designed for HPC integration. The company is a key technology partner in Europe's quantum computing infrastructure, supplying systems for the EuroHPC Joint Undertaking and national supercomputing centers across the continent.

IQM's co-design methodology sets it apart from other quantum hardware providers. Rather than offering a one-size-fits-all processor, IQM works with customers to tailor QPU topology and parameters to specific application requirements. This approach has led to multiple product lines serving different market segments: Resonance for cloud access, Radiance for HPC centers, and Halocene for error correction research.

IQM's partnership with the LUMI supercomputer is particularly significant. The VLQ quantum computer connected to the LUMI ecosystem, combined with planned LUMI-AI and LUMI-IQ systems, is forming the most advanced public quantum-accelerated HPC+AI infrastructure in the world.

### Co-Design Methodology

IQM tailors QPU architecture to specific customer applications, optimizing topology and gate parameters for maximum performance on targeted problems.

### LUMI Supercomputer Integration

IQM's VLQ quantum computer is connected to the LUMI supercomputer ecosystem, enabling hybrid quantum-classical workflows with minimal latency.

### European Data Sovereignty

As a key EuroHPC JU partner, IQM systems are deployed across Finland, Germany, Czech Republic, and Poland, ensuring data remains within European infrastructure.

## IQM Hardware on Open Quantum

| System | Qubits | 2Q Gate Fidelity | Connectivity | Best For |
|----|----|----|----|----|
| [GarnetView live specs](https://www.openquantum.com/providers/iqm/garnet "View live device profile: qubit topology, native gates, features, and limits") | 20 | 99.51% median CZ | Square lattice + tunable couplers | Cloud research, algorithm development |
| [EmeraldView live specs](https://www.openquantum.com/providers/iqm/emerald "View live device profile: qubit topology, native gates, features, and limits") | 54 | 99.5% median CZ | Square lattice + tunable couplers | Production workloads, error correction research |

![IQM quantum computer system](https://www.openquantum.com/_next/image?url=%2Fiqm-system.jpg&w=1920&q=75)

### Tunable Coupler Architecture

IQM's Garnet and Emerald processors use a square lattice topology augmented with tunable couplers between each pair of connected qubits. Garnet's 20 computational qubits are supplemented by 30 tunable coupler qubits (50 physical qubits total), while Emerald scales the same proven architecture to 54 computational qubits. This design enables high-fidelity CZ gates while maintaining the scalability of a regular lattice structure that natively supports surface-code error correction.

### Key Performance Highlights

- Garnet: 99.51% median CZ fidelity; Emerald: 99.5% median CZ fidelity
- 2,600 CLOPS (Circuit Layer Operations Per Second)
- Garnet: 20 qubits; Emerald: 54 qubits, same proven architecture
- Roadmap to 150+ qubits with Radiance and Halocene product lines

### European HPC Deployments

#### LUMI-Q (Finland)

24-qubit Star topology VLQ connected to the LUMI supercomputer. Nine European nations collaborating on quantum-HPC infrastructure.

#### Euro-Q-Exa (Munich)

54-qubit IQM system deployed at the Leibniz Supercomputing Centre as part of the EuroHPC Joint Undertaking.

#### IT4Innovations (Czech Republic)

24-qubit Star topology system connected to the Karolina supercomputer. EUR 5M investment, 50% EuroHPC JU funded.

#### Aalto University (Finland)

20-qubit system deployed in March 2026, the fourth IQM system installed in Finland.

## Why Run IQM Circuits on Open Quantum?

### Unified API

Access IQM, Rigetti, IonQ, and AQT hardware through a single SDK. No need to set up IQM Resonance separately.

### No Vendor Lock-In

Write your circuit once and run it on any backend. Compare European and US quantum hardware freely.

### Cross-Vendor Benchmarking

Compare IQM superconducting results with IonQ and AQT trapped-ion results on the same circuit.

### Free \$50 of Compute

Every new Open Quantum account includes \$50 of free quantum compute, refreshed every 90 days. Start running circuits on IQM immediately.

## Getting Started

Submit your first circuit to IQM's Garnet or Emerald in minutes. Install the Open Quantum SDK, authenticate, and select the IQM backend.

``` python
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

scheduler = SchedulerClient()  # uses OPENQUANTUM_CLIENT_ID/SECRET env vars

config = JobSubmissionConfig(
    backend_class_id="iqm:garnet",  # or "iqm:emerald"
    name="Bell State on IQM",
    shots=100,
)

job = scheduler.submit_job(config, file_path="bell_state.qasm")

result = scheduler.download_job_output(job)
```

[Run Your First Circuit on IQM Hardware](https://www.openquantum.com/create-job)

[](https://www.openquantum.com/signup)

\$50 of Free Quantum Compute

Every new Open Quantum account includes \$50 of free quantum compute credits, refreshed every 90 days. Run circuits on IQM, Rigetti, IonQ, and AQT hardware at no cost.

## Frequently Asked Questions

Do I need to use IQM Resonance to run on IQM hardware?

What is co-design methodology in quantum computing?

How does IQM integrate with HPC supercomputers?

What is the LUMI-Q quantum computing consortium?

What qubit fidelity do IQM's Garnet and Emerald processors achieve?

How do I run a circuit on IQM hardware via Open Quantum?

## Explore Other Quantum Hardware Providers

[](https://www.openquantum.com/providers/rigetti)

### Rigetti

Cepheus-1 \| 108 qubits

Superconducting

99.1% CZ fidelity, modular chiplet architecture

Learn more

[](https://www.openquantum.com/providers/ionq)

### IonQ

Forte & Forte Enterprise \| 36 qubits

Trapped Ion

All-to-all connectivity, 99.6% 2Q fidelity, 36 algorithmic qubits

Learn more

[](https://www.openquantum.com/providers/aqt)

### AQT

IBEX Q1 \| 12 qubits

Trapped Ion

Fully-connected topology, room temperature, rack-mounted

Learn more
