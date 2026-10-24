> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/quantum-jobs.md](https://docs.qbraid.com/v2/lab/user-guide/quantum-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 b514b416376e542ff540bf8525386ee821f326dfa8e923d380624ba3af7ddbf0.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# Quantum Jobs

> Submit, monitor, cancel, and delete quantum jobs across multiple providers.

qBraid Quantum Jobs give Lab direct access to QPU devices from IonQ, AQT, QuEra, Rigetti, and IQM, as well as on-demand simulators
from qBraid, AWS, Pasqal, Quantinuum, and more. No additional access keys required.

Open the Quantum Jobs sidebar by clicking the **Jobs** icon in the top-right of the Lab console.

## Submit quantum jobs

You can submit quantum jobs using the qBraid-SDK in a Jupyter Notebook using the pre-configured qBraid SDK environment. First, ensure that the `qbraid-sdk` kernel is selected in your notebook.
Next, you can use the following code snippet to submit a quantum job to a device or simulator of your choice:

```python
from qbraid.runtime import QbraidProvider

# See available devices
provider = QbraidProvider()
devices = provider.get_devices()
print("Available devices:")
for device in devices:
    print(device.id, device.status())

# Select a device
device = provider.get_device("aws:rigetti:qpu:cepheus-1-108q")
print("\nSelected device:", device)

# Define your quantum circuit (example using Qiskit)
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Run the quantum job
job = device.run(qc, shots=1024)
print("Job ID:", job.id)

print("Job submitted successfully.")

# Wait for the job to complete
job.wait_for_final_state()

# Retrieve and print the results
result = job.result()
print("Counts: ", result.data.get_counts())
```

Submitted jobs appear in the Quantum Jobs sidebar where you can monitor their status in real time.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/submitting_job.gif"
    alt="Submitting a quantum job and viewing it in the sidebar"
    width="100%"
  />
</div>

## Jobs sidebar

The sidebar displays your job history with provider logos, status indicators, timestamps, and device IDs.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/jobs_ss.png"
    alt="Quantum Jobs sidebar showing job list with provider tabs"
    width="100%"
  />
</div>

### Provider tabs

Switch between job sources using the tabs at the top of the sidebar:

- **qBraid** — jobs submitted to qBraid-managed devices via the SDK, REST API, or any client using qBraid as a backend. See [Pricing](https://docs.qbraid.com/v2/home/pricing) for details.
- **IBM Cloud** — jobs submitted to IBM Quantum (requires your own IBM credentials)
- **AWS Braket** — jobs submitted through Amazon Braket (requires your own AWS credentials)

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/ibm_jobs.png"
    alt="IBM Cloud jobs tab showing IBM Quantum job history"
    width="100%"
  />
</div>

## Devices and pricing

For available devices, visit [Quantum Devices](https://docs.qbraid.com/v2/lab/user-guide/quantum-devices). For pricing details,
visit [Pricing](https://docs.qbraid.com/v2/home/pricing).

<Note>
  Access to IBM QPUs requires your own IBM Cloud credentials. qBraid does not
  currently offer managed access to IBM QPUs.
</Note>
