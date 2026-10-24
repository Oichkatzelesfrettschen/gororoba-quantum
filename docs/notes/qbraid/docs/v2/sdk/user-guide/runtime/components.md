> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/runtime/components.md](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 b0f6e1b4aaf6f8e1ff9c91f4b8cb048fba8c83c7a7faced57692223cd5ecbfa7.

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

# Runtime Components

> Universal building blocks for constructing client-side quantum software pipelines.

## Runtime Overview

The qBraid Runtime framework defines essential abstractions for sessions, providers, devices, jobs, and results,
integrating them into a complete client-side software pipeline. Leveraging device and domain-specific requirements
outlined by each provider, it generates coherent target "profiles," program "specs," and compilation "schemes".

These elements, referred to as Universal Pipeline Components (UPCs), form the foundational building blocks for constructing scalable
quantum software pipelines. Each UPC plays a unique and distinct role, utilizing quantum and/or classical resources. Collectively,
these components optimize the management of the entire quantum job lifecycle—from defining quantum programs to dispatching jobs to
remote servers to post-processing results—and ensure the efficient production of outputs for diverse computational tasks.

<img
  src="/v2/sdk/_static/qbraid-runtime-sdk.png"
  alt="Runtime Architecture"
  className="block dark:hidden"
/>
<img
  src="/v2/sdk/_static/qbraid-runtime-sdk_dark.png"
  alt="Runtime Architecture"
  className="hidden dark:block"
/>

Distinguishing itself through a streamlined and highly-configurable approach to cross-platform integration,
qBraid Runtime does not adhere to a fixed circuit-building library, or quantum program representation. Instead,
it empowers providers to dynamically register any desired input program type as the target based on their specific needs.
This flexibility is extended by the framework's modular pipeline, which facilitates any number of additional program
validation, transpilation, and compilation steps.

Unlike existing runtime frameworks that focus their automation and abstractions primarily on quantum components—such as
adapting the input quantum program to the supported operations and connectivity of the target device—qBraid Runtime adds an
_extra_ layer of functionalities. This layer considers the ultimate IR needed to encode the quantum program and securely submit
it to a remote API. By addressing the full scope of client-side software requirements necessary for secure submission and
management of quantum jobs, qBraid Runtime significantly streamlines the development process, enhancing the agility with which
quantum hardware providers can construct a complete stack and facilitate access to their devices.

## Building Pipelines

The `qbraid.runtime` module provides the following Universal Pipeline Components (UPCs):

- [TargetProfile](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider#targetprofile): Specifies domain and device-specific runtime instructions to tailor quantum executions to particular hardware configurations.
- [QuantumProvider](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider#quantumprovider): Converts device metadata into accessible Python objects, facilitating interaction with diverse quantum computing resources.
- [QuantumDevice](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider#quantumdevice): Describes the unique parameters and operational settings necessary for executing quantum programs on specific hardware.
- [QuantumJob](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider#quantumjob): Represents the transitional states of quantum programs, managing both ongoing and completed quantum computations.
- [Result](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results): Captures and structures the output from quantum computations, including histograms and raw data, for analysis and interpretation.

In the subsequent sections, we will demonstrate how these UPCs enable quantum software and hardware providers to configure a
comprehensive client-side quantum software pipeline using just three essential REST API endpoints:

1. `GET` `/devices` (or similar) - To retrieve metadata about available quantum devices.
2. `POST` `/jobs` (or similar) - To submit a quantum job for execution on a specified device.
3. `GET` `/jobs` (or similar) - To retrieve the status and results of an executed quantum job.

## Quantum Job Submission Process

When a `QuantumDevice.run` method is called, the following steps are performed to process a quantum program and submit it as a job to a remote API:

1. **Transpile**: Performs a "program type conversion" according to the `ProgramSpec`(s) specified by the device's `TargetProfile`
2. **Transform**: Applies any device-specific passes (e.g., gate decompositions to map the circuit to a `TargetProfile.basis_gates` set).
3. **Validate**: Verify that the run input satisfies all criteria for submitting to the given device (e.g., ensuring the number of qubits in the circuit does not exceed the device's capacity).
4. **Prepare**: Serializes the run input or converts it to any lower-level IR required for submission to the remote API (e.g., string, JSON, or bytecode format).
5. **Submit**: Sends `POST` request (or equivalent) with program and all runtime parameters to the remote API, and returns a `QuantumJob` instance.

### Discovering valid run inputs

`QuantumDevice.supported_run_inputs()` returns the sorted program type aliases the transpile step can deliver to a given device — the programmatic answer to "what can I pass to `run()`?":

```python
>>> device.supported_run_inputs()
['braket', 'cirq', 'pytket', 'qasm2', 'qasm3', 'qiskit']
```

The answer reflects the device's own configuration, not just the conversion graph: a `ConversionScheme` constraint such as `max_path_depth` narrows it exactly the way it narrows `run()`, and a device whose `transpile` [option](https://docs.qbraid.com/v2/sdk/user-guide/runtime/options) is disabled reports only its native aliases. To find the exact Python object type behind each alias, look it up in [`QPROGRAM_REGISTRY`](https://docs.qbraid.com/v2/sdk/user-guide/programs#quantum-program-registry).

For a server-side view of how this flow integrates with the qBraid API, see the [API overview](https://docs.qbraid.com/v2/api-reference/user-guide/overview#quantum-job-flow).
