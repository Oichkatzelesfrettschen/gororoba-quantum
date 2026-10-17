> Full piece: [https://docs.openquantum.com/](https://docs.openquantum.com/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c36867104e46f7102ad113989d36cb6f54d0bc0913ed74f2f63177481d79d696.

# Run circuits on real QPU hardware

Access IonQ, Rigetti, IQM, and AQT processors through a single platform.\
Use the web portal, or integrate with Python via Qiskit, PennyLane, Cirq, and Qrisp.

[Quick Start](https://docs.openquantum.com/core-sdk/quickstart/) [Create Free Account](https://www.openquantum.com)

## Choose Your Path

[](https://docs.openquantum.com/portal/overview/)

→

Web Portal

Submit QASM circuits, monitor jobs, and manage your account from your browser.

[](https://docs.openquantum.com/core-sdk/overview/)

→

Python SDK

Direct access to job submission, backend discovery, and account management.

[](https://docs.openquantum.com/qiskit-plugin/overview/)

→

Qiskit Plugin

Use BackendV2, SamplerV2, and EstimatorV2 with Open Quantum hardware.

[](https://docs.openquantum.com/pennylane-plugin/overview/)

→

PennyLane Plugin

Build quantum circuits with PennyLane and execute on real QPUs.

[](https://docs.openquantum.com/cirq-plugin/overview/)

→

Cirq Plugin

Build hardware-aware circuits with Google's Cirq and run them on real QPUs via cirq.Sampler.

[](https://docs.openquantum.com/qrisp-plugin/overview/)

→

Qrisp Plugin

Write high-level Qrisp programs with quantum variables and run them on real QPUs.

[](https://docs.openquantum.com/mcp/overview/)

→

AI Agents & MCP

Submit and monitor jobs from Claude, Cursor, and other MCP-compatible agents.

[](https://docs.openquantum.com/integrations/)

→

Run Through a Third Party

Reach Open Quantum backends from a partner platform like qBraid, using the tools you already work in.

## Step 1: Create Your Free Account

Sign up at [openquantum.com](https://www.openquantum.com) and get \$50 of free Spark credits.

## Step 2: Choose How to Run Circuits

There are two ways to use Open Quantum:

### The Web Portal

The [Open Quantum Portal](https://www.openquantum.com) lets you submit QASM circuits, monitor jobs, and download results all from your browser. It's also where you manage your account, credits, and SDK keys.

See the [OpenQuantum.com](https://docs.openquantum.com/portal/overview/) section for a full walkthrough.

### The Python SDK

For programmatic access, install the Python SDK, along with framework plugins to match your workflow.

See the [Python SDK](https://docs.openquantum.com/core-sdk/overview/) section for installation, authentication, and a quick start guide.

## Step 3: Run Your First Circuit

Once you have an account, you can run circuits right away:

- **From the web portal:** Upload a QASM file on the [Submit Job](https://docs.openquantum.com/portal/submitting-jobs/) page and pick a backend.
- **From Python:** Follow the [Quick Start](https://docs.openquantum.com/core-sdk/quickstart/) guide to submit a Bell state circuit in a few lines of code.

## Available QPU Backends

| Provider | Backend   | Qubits | Technology      |
|----------|-----------|--------|-----------------|
| IonQ     | Forte-1   | 36     | Trapped ion     |
| Rigetti  | Cepheus-1 | 108    | Superconducting |
| IQM      | Emerald   | 54     | Superconducting |
| IQM      | Garnet    | 20     | Superconducting |
| AQT      | Ibex-Q1   | 12     | Trapped ion     |

See [Backends & Hardware](https://docs.openquantum.com/concepts/backends/) for details on each processor, including native gate sets and topology.

## Sample Circuits & Notebooks

Open Quantum provides ready-to-run [QASM circuits](https://www.openquantum.com/sample-qasm) and [Jupyter notebooks](https://www.openquantum.com/notebooks) to help you get started. See [Sample Circuits & Notebooks](https://docs.openquantum.com/getting-started/resources/) for the full list.
