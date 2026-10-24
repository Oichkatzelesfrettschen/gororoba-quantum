> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 70f44a4f8a58ee25a500cd010e2bcc5b9b70ea40c702bf4b6707a794a097ed3b.

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

# Self-managed providers

> Use the qBraid SDK with your own account and credentials at a quantum vendor or cloud. Jobs, billing, and keys are between you and the vendor.

A self-managed provider uses **your own account** with a quantum vendor or cloud: an IonQ API key, an AWS account for Amazon Braket, an IBM Quantum token, and so on. The qBraid SDK is only the client library. Your jobs go straight to the vendor, the vendor bills you, and qBraid never sees them.

<Tip>
  **Don't have your own vendor account?** You probably want [Run on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started) instead. One qBraid API
  key reaches every device in the qBraid catalog, with no vendor account, and
  it's how most people use the qBraid SDK.
</Tip>

## When self-managed makes sense

- You already have a contract, credits, or a reservation with a vendor.
- You need a device qBraid doesn't run jobs on. IBM Quantum is the main one.
- Your organization requires jobs to run in its own cloud account.

## How the two compare

|                 | Run on qBraid                                                           | Self-managed                                  |
| :-------------- | :---------------------------------------------------------------------- | :-------------------------------------------- |
| **Credentials** | One qBraid API key                                                      | Your own credentials for each vendor           |
| **Billing**     | qBraid credits                                                          | The vendor's own billing                       |
| **Job history** | Your qBraid [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs)                    | The vendor's console only                      |
| **Install**     | `pip install qbraid`                                                    | `pip install 'qbraid[<extra>]'`, listed below  |
| **Provider**    | [`QbraidProvider`](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started)       | The vendor's provider class, listed below      |

Devices with `openquantum:` IDs are the one exception on the qBraid side. They run through qBraid but spend credits from your linked [Open Quantum](https://docs.qbraid.com/v2/account/integrations/openquantum) account.

## Providers

| Vendor                                                                     | Provider class          | Install                              | Also on qBraid                                         |
| :------------------------------------------------------------------------- | :---------------------- | :----------------------------------- | :----------------------------------------------------- |
| [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws)             | `BraketProvider`        | `pip install 'qbraid[braket]'`       | [Yes](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws)                |
| [AQT](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aqt)                       | `AQTProvider`           | `pip install 'qbraid[aqt]'`          | [Yes](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt)                |
| [Azure Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/azure)           | `AzureQuantumProvider`  | `pip install 'qbraid[azure]'`        |                                                        |
| [IBM Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ibm)               | `QiskitRuntimeProvider` | `pip install 'qbraid[qiskit]'`       |                                                        |
| [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ionq)                     | `IonQProvider`          | `pip install 'qbraid[ionq]'`         | [Yes](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq)               |
| [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/openquantum) | `OpenQuantumProvider` | `pip install qbraid` | [Yes](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) |
| [OQC](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/oqc)                       | `OQCProvider`           | `pip install 'qbraid[oqc]'`          |                                                        |
| [Origin Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/origin)         | `OriginProvider`        | `pip install 'qbraid[origin]'`       |                                                        |
| [Pasqal](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/pasqal)                 | `PasqalProvider`        | `pip install 'qbraid[pasqal]'`       |                                                        |
| [QPerfect](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qperfect)             | `QPerfectProvider`      | `pip install 'qbraid[qperfect]'`     |                                                        |
| [Quantinuum](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/quantinuum)         | `QuantinuumProvider`    | `pip install 'qbraid[quantinuum]'`   |                                                        |
| [QUDORA](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qudora)                 | `QudoraProvider`        | `pip install qbraid`                 |                                                        |
| [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/rigetti)               | `RigettiProvider`       | `pip install 'qbraid[rigetti]'`      | [Yes](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti)            |

Every provider class runs on the same [qBraid Runtime](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components) interface, so code written for one, such as `provider.get_device(...)` and `device.run(...)`, carries over to another, including `QbraidProvider`.
