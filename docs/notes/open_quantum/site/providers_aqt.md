> Full piece: [https://www.openquantum.com/providers/aqt](https://www.openquantum.com/providers/aqt)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --site (urllib, pandoc);
> fetched HTML sha256 0e4ee1710a8456a0de00f5cee75b690c90763bd807301d1e3a948f637d6f9e7d.

![AQT Alpine Quantum Technologies logo](https://www.openquantum.com/aqt-logo.svg)

# AQT IBEX Q1: European Trapped-Ion Quantum Computing via Open Quantum

Access AQT's compact, room-temperature trapped-ion quantum processor through a unified cloud API. 12 fully-connected qubits with no cryogenics required.

Alpine Quantum Technologies (AQT) builds compact, rack-mounted trapped-ion quantum computers based on decades of research at the University of Innsbruck and the Austrian Academy of Sciences. Their IBEX Q1 system offers 12 fully-connected qubits using calcium-40 ions, meaning any qubit can interact directly with any other without the SWAP gate overhead required by grid-connected superconducting processors. The entire system fits in two standard 19-inch server racks, operates at room temperature without cryogenic cooling, and consumes less than 2 kW of power. IBEX Q1 achieves approximately 98.85% average two-qubit gate fidelity and a Quantum Volume of 128, with single-qubit gate fidelity of 99.97%. Through Open Quantum, you can access AQT's IBEX Q1 using the same unified API you use for Rigetti, IonQ, and IQM backends, with \$50 of free quantum compute every 90 days to start running circuits and comparing results across providers immediately.

## About AQT (Alpine Quantum Technologies)

AQT was founded in 2018 as a spinoff from the University of Innsbruck and the Austrian Academy of Sciences, two institutions at the forefront of trapped-ion quantum computing research for over three decades. The company is led by CEO Thomas Monz, a physicist who brings deep academic expertise to the commercialization of trapped-ion technology.

AQT's quantum computers use calcium-40 ions confined in radio-frequency traps within ultra-high vacuum chambers. Quantum information is encoded in the electronic spin states of these charged atoms, and laser pulses perform quantum gate operations. This approach yields qubits that are inherently identical at the atomic level, with long coherence times and fully-connected topology.

What makes AQT unique in the quantum computing landscape is its compact form factor. An entire AQT quantum computer fits in just two standard 19-inch server racks, operates at room temperature without any dilution refrigerator, and consumes less than 2 kW of power. This makes AQT systems ideal for integration into existing data centers and HPC infrastructure.

### Compact Form Factor

Full quantum computer in 2x 19-inch racks. Room temperature operation. Less than 2 kW power consumption.

### European HPC Deployments

Systems deployed at the Leibniz Supercomputing Centre (Munich), Poznan Supercomputing Center (Poland), and the University of Innsbruck.

### Academic Heritage

Spinoff from the Rainer Blatt and Peter Zoller research groups, world leaders in trapped-ion physics. World record: 24-qubit entanglement.

## AQT Hardware on Open Quantum

| System | Qubits | 2Q Gate Fidelity | Connectivity | Best For |
|----|----|----|----|----|
| [IBEX Q1View live specs](https://www.openquantum.com/providers/aqt/ibex-q1 "View live device profile: qubit topology, native gates, features, and limits") | 12 | ~98.85% | Fully-connected (all-to-all) | HPC integration, research, enterprise PoC |

![AQT IBEX Q1 trapped-ion quantum computer rack unit](https://www.openquantum.com/_next/image?url=%2Faqt-ibex-q1-rack.jpg&w=1920&q=75)

Photo credit: D. Kuhl, AQT

### Fully Connected Topology: Zero SWAP Overhead

The IBEX Q1's fully-connected qubit topology is a fundamental advantage for many quantum algorithms. On grid-connected superconducting processors, implementing a gate between two non-adjacent qubits requires a chain of SWAP operations, each of which introduces noise and increases circuit depth. With AQT's trapped-ion architecture, any qubit can interact directly with any other qubit. This means your compiled circuits are shorter, faster to execute, and less susceptible to accumulated errors.

### Key Performance Highlights

- Single-qubit gate error: (3.4 +/- 1.0) x 10^-4 (~99.97% fidelity)
- Two-qubit gate fidelity: ~98.85% average, with minimum error of 0.9%
- Quantum Volume: 128
- Room temperature operation, no cryogenic cooling required

> “As we continue to expand the reach of AQT's state-of-the-art technology through this partnership with Quantum Rings, we are excited to see how users will leverage our quantum systems. Our hope is that this collaboration enables users who may not have traditionally had access to our technology to experiment freely and drive a broader diversity of use cases toward real quantum value.”

– Thomas Monz, CEO, Alpine Quantum Technologies

## Why Run AQT Circuits on Open Quantum?

### Unified API

Access AQT, Rigetti, IonQ, and IQM hardware through a single SDK. No vendor-specific toolchains required.

### No Vendor Lock-In

Write your circuit once and run it on any backend. Switch between trapped-ion and superconducting hardware freely.

### Cross-Vendor Benchmarking

Compare AQT trapped-ion results with Rigetti, IonQ, and IQM superconducting results on the same circuit.

### Free \$50 of Compute

Every new Open Quantum account includes \$50 of free quantum compute, refreshed every 90 days. Start running circuits on AQT immediately.

## Getting Started

Submit your first circuit to AQT's IBEX Q1 in minutes. Install the Open Quantum SDK, authenticate, and select the AQT backend.

``` python
from openquantum_sdk.clients import SchedulerClient, JobSubmissionConfig

scheduler = SchedulerClient()  # uses OPENQUANTUM_CLIENT_ID/SECRET env vars

config = JobSubmissionConfig(
    backend_class_id="aqt:ibex-q1",
    name="Bell State on AQT",
    shots=100,
)

job = scheduler.submit_job(config, file_path="bell_state.qasm")

result = scheduler.download_job_output(job)
```

[Run Your First Circuit on AQT Hardware](https://www.openquantum.com/create-job)

[](https://www.openquantum.com/signup)

\$50 of Free Quantum Compute

Every new Open Quantum account includes \$50 of free quantum compute credits, refreshed every 90 days. Run circuits on AQT, Rigetti, IonQ, and IQM hardware at no cost.

## Frequently Asked Questions

What is a trapped-ion quantum computer?

What does two-qubit gate fidelity mean?

How does fully-connected qubit topology reduce circuit overhead?

How does IBEX Q1 integrate with HPC infrastructure?

How do I get started running circuits on AQT via Open Quantum?

What is Quantum Volume and what does QV 128 mean?

What is the difference between AQT and superconducting quantum computers?

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

[](https://www.openquantum.com/providers/iqm)

### IQM

Garnet & Emerald \| 20-54 qubits

Superconducting

99.5% CZ fidelity, European HPC integration

Learn more
