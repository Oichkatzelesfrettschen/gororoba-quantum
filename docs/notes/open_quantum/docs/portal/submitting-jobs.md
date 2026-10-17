> Full piece: [https://docs.openquantum.com/portal/submitting-jobs/](https://docs.openquantum.com/portal/submitting-jobs/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3e52146fde5fba704bdcd88acb273f98fd095f91ad7c5d4529db296c7cb5f60c.

# Submitting Jobs

You can submit quantum circuits directly through the [Open Quantum Portal](https://www.openquantum.com) — no SDK or Python required. This is useful for quickly evaluating the platform, running one-off experiments, or for users who prefer a visual interface over writing code.

For production workflows and programmatic access, use the [Python SDK](https://docs.openquantum.com/core-sdk/quickstart/) or one of the framework plugins ([Qiskit](https://docs.openquantum.com/qiskit-plugin/overview/), [PennyLane](https://docs.openquantum.com/pennylane-plugin/overview/), [Cirq](https://docs.openquantum.com/cirq-plugin/overview/), [Qrisp](https://docs.openquantum.com/qrisp-plugin/overview/)).

## Prepare a QASM File

You need an OpenQASM file to submit through the portal. You can write your own or grab one from the [Sample QASM](https://www.openquantum.com/sample-qasm) page.

Other input formats

The portal accepts OpenQASM uploads. Some backends support additional formats through the [Python SDK](https://docs.openquantum.com/core-sdk/job-submission/#input-formats) via `input_format`.

Here's a minimal Bell state circuit you can save as `bell.qasm`:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

Tip

The [Sample QASM](https://www.openquantum.com/sample-qasm) page has ready-to-download circuits for teleportation, Grover's search, QFT, error correction, and more.

## Create a New Job

1.  Sign in to [www.openquantum.com](https://www.openquantum.com).
2.  Navigate to **Jobs** in the sidebar.
3.  Click **New Job**.
4.  Fill in the job details:

| Field         | Description                                                |
|---------------|------------------------------------------------------------|
| **Name**      | A label for your job (e.g., "Bell State Test").            |
| **Backend**   | The QPU to target (e.g., IonQ Forte-1, Rigetti Cepheus-1). |
| **Shots**     | Number of measurement repetitions (e.g., 1024).            |
| **QASM File** | Upload your `.qasm` file.                                  |

1.  Click **Submit**.

Your job will appear in the [Jobs](https://www.openquantum.com/jobs) list. See [Monitoring Jobs](https://docs.openquantum.com/portal/monitoring-jobs/) for how to track progress and download results.
