> Full piece: [https://docs.qbraid.com/v2/vscode/user-guide/quantum-console.md](https://docs.qbraid.com/v2/vscode/user-guide/quantum-console.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c7390f973676e26ebfcdea3378f443824632e04a0e1c2956221fc4b462285388.

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

# Quantum Console

> Manage qBraid jobs and devices directly within Visual Studio Code.

The Quantum Console VS Code extension pack provides a powerful interface for quantum computing workflows, enabling seamless management of quantum jobs and devices through qBraid's [public APIs](https://docs.qbraid.com/v2/api-reference/user-guide/overview).

### Installation

The Quantum Console extension can be installed directly through the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=qBraid.quantum-console) -

<img
  src="https://qbraid-static.s3.us-east-1.amazonaws.com/qbraid-vscode/marketplace.png"
  alt="Quantum Console Extension"
  width="80%"
/>
## Extensions

### Cloud Providers Panel

Manage your quantum cloud providers directly from VS Code.

- **Enable/Disable Providers:** Easily toggle access to supported providers.
- **Supported Providers:** `qBraid`, `IBM`
- **Seamless Switching:** Instantly switch between providers to manage jobs and devices from multiple platforms in one place.

<img
  alt="qbraid-vscode-cloud-providers"
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/cloud-providers.gif"
  width="60%"
/>

### Quantum Devices

Monitor the status, queue depth, capabilities, and other details of quantum devices accessible through both IBM and qBraid.

**IBM Devices**

- View available IBM QPUs and simulators.
- Inspect detailed device properties: qubit count, connectivity, error rates, and more.
- Monitor real-time queue depth and device status.
- Seamlessly switch to IBM as your active provider to submit jobs and manage devices.

**qBraid Devices**

- Access QPUs from IonQ, Oxford Quantum Circuits, QuEra, Rigetti, and IQM.
- Use on-demand simulators from qBraid, AWS, IonQ, QuEra, and NEC.
- Monitor device status, queue depth, and capabilities.
- Filter and sort devices by provider, type, and other attributes.
- For more details on access and costs, see the [pricing page](https://docs.qbraid.com/home/pricing).

![qbraid-vscode-quantum-devices](https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/quantum-devices.gif)

### Quantum Jobs

The **Quantum Jobs** sidebar is where you can view and manage all your quantum jobs. Jobs submitted via the [qbraid.runtime.QbraidProvider](https://docs.qbraid.com/sdk/user-guide/providers/getting-started) will automatically appear in the **qBraid** tab. Moreover, jobs submitted directly to IBM Quantum via [Qiskit](https://quantum.cloud.ibm.com/docs/en/guides#qiskit-runtime) or [qbraid.runtime.ibm.QiskitRuntimeProvider](https://docs.qbraid.com/sdk/user-guide/providers/self-managed/ibm) will appear in the **IBM** tab. The sidebar allows you to:

- _View Jobs_ – Browse all jobs submitted to qBraid and IBM Quantum.
- _Monitor Progress_ – Track job status and queue position in real-time.
- _Manage Jobs_ – Cancel or delete jobs as needed.
- _Search & Filter_ – Find jobs by ID, status, tags, and other attributes.
- _Inspect Details_ – View job's qasm representation, cost estimates, and job metadata.
- _Retrieve Results_ – View measurement counts and execution data.

![qbraid-vscode-quantum-jobs](https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/quantum-jobs.gif)

## Authentication

The Quantum Console extension pack requires authentication for both qBraid and IBM Quantum providers:

**qBraid Access**

1. Login or create a free account at [account.qbraid.com](https://account.qbraid.com).
2. Copy your API Key from the **Plan** info card on the left side of your account page.
3. Enter the API Key in the qBraid provider dropdown.
4. Click _Save_ to complete the authentication process.

<img
  alt="qbraid-auth"
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/qbraid-provider.png"
  width="85%"
/>

For more information, refer to the [qBraid API Keys documentation](https://docs.qbraid.com/home/account#api-keys).

**IBM Quantum Access**

1. Login or create a free account at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/).
2. Obtain your IBM Cloud API Key and the Service Cloud Resource Name (CRN) for your IBM Quantum instance from the [IBM Cloud Console](https://quantum.cloud.ibm.com/).
3. Enter both the API Key and Service CRN in the IBM provider dropdown.
4. Click _Save_ to complete the authentication process.

<img
  alt="ibm-auth"
  src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/vscode/ibm-provider.png"
  width="85%"
/>

For more information, refer to the [Qiskit Runtime documentation](https://quantum.cloud.ibm.com/docs/en/api/qiskit-runtime-rest#authentication).
