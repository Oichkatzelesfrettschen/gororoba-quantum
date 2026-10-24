> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider.md](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 74ca0be00ad209d0b1ae9f512b86a53bc5a9a7aa1471ac8c3019a0175939d1c6.

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

# Writing a New Provider

> A step-by-step guide to implementing a new provider class.

## Overview

To integrate a quantum device or simulator with qBraid Runtime, you'll need to create a custom provider class. A provider includes a
collection of devices and runtime specifications. Each `QuantumProvider` should implement a `get_devices` method to retrieve
`QuantumDevice` objects, which describe the device's supported operations, the program types accepted as run input, and other
dynamic runtime instructions. Finally, devices must implement a `submit()` method to execute or
queue programs, returning a `QuantumJob` object. This standardization allows users and APIs to uniformly submit jobs and retrieve
results, ensuring compatibility across different providers and devices.

Here are the high-level components required to establish a complete runtime implementation:

<Steps>
  <Step title="Provider Setup">
    Implement a `QuantumProvider` subclass that manages authentication and
    remote access to the available device(s).
  </Step>
  <Step title="Device + Runtime Configuration">
    Implement a `QuantumDevice` subclass and its `submit()` method. Optionally
    incorporate a custom `ConversionScheme` to broaden the range of quantum
    program types that can be accepted as run input.
  </Step>
  <Step title="Job Management">
    Implement a `QuantumJob` subclass that handles interactions with a running
    job. Process and present data collected from job executions in unified
    `Result` class.
  </Step>
</Steps>

## QuantumProvider

The provider class is responsible for managing interactions with various quantum services and for converting device metadata
into accessible Python objects.

For a simple provider implementation example, see <a href="https://github.com/qBraid/qBraid/blob/v0.7.0/qbraid/runtime/ionq/provider.py" target="_blank">qbraid.runtime.ionq.provider.py &#8599;</a>

### Server Requests

Creating a provider class requires the following REST API endpoints:

1. `GET` `/devices` (or similar) - To retrieve metadata about available quantum devices.
2. `POST` `/job` (or similar) - To submit a quantum job for execution on a specified device.
3. `GET` `/job` (or similar) - To retrieve the status and results of an executed quantum job.

If you already have a Python client for interacting with your REST API server, you can skip this section and go directly to
[Provider Setup](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider#provider-setup).

For those who need to set up a Python client, the `qbraid.runtime.Session`, a subclass of [requests.Session](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects),
is designed to manage secure HTTP connections to custom endpoints. It ensures encrypted and authenticated communication for quantum
providers and offers customizations for management of headers and secret keys, configurable retries for `5xx` errors, and more.

Below is a minimal example demonstrating how one could set up authenticated requests to the previously mentioned endpoints:

```python
from typing import Any

from qbraid.runtime import Session


class MySession(Session):

    def __init__(self, api_key: str):
        super().__init__(
            base_url="https://api.example.com/fake-endpoint",
            headers={"Content-Type": "application/json"},
            auth_headers={"apiKey": api_key},
        )
        self.api_key = api_key

    def get_device(self, device_id: str) -> dict[str, Any]:
        devices = self.get_devices(device_id=device_id)
        if not devices:
            raise ValueError(f"Device {device_id} not found")
        return devices[0]

    def get_devices(self, **kwargs) -> list[dict[str, Any]]:
        return self.get("/devices", **kwargs).json()

    def create_job(self, data: dict[str, Any]) -> dict[str, Any]:
        return self.post("/jobs", json=data).json()

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.get(f"/jobs/{job_id}").json()
```

In the above example, `base_url` corresponds to your API endpoint. The qBraid `Session` class distinguishes between `headers`
and `auth_headers`, ensuring that values in `auth_headers` are masked in all responses to safeguard against the inadvertent
exposure of secret keys.

The qBraid `Session` class offers additional customizable options such as the total number of retries for requests, the number
of connection retries, the backoff factor between retry attempts, and more. For further details, refer to the linked
API Reference below.

<Info>
  API Reference:{" "}
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.native.Session.html#qbraid.runtime.native.Session"
    target="_blank"
  >
    qbraid.runtime.Session &#8599;
  </a>
</Info>

### TargetProfile

The `qbraid.runtime.TargetProfile` encapsulates the configuration settings and runtime protocol(s) for a quantum device, presenting
them as a read-only dictionary. This class plays a crucial role in orchestrating the processes required for the submission of
quantum jobs in the current environment.

Specifically, the `TargetProfile` class specifies domain and device-specific instructions to tailor quantum programs to the
intermediate representation (IR) required for submission through the provider's API and execution on the quantum backend. This
includes compilation steps, type conversions, data mappings, and other essential runtime transformations.

Below is an example implementation of a TargetProfile:

```python
from unittest.mock import Mock

from qbraid.programs import ProgramSpec, ExperimentType
from qbraid.runtime import DeviceType, TargetProfile


profile = TargetProfile(
    device_id="abc123",
    num_qubits=7,
    device_type=DeviceType.QPU,
    experiment_type=ExperimentType.GATE_MODEL,
    program_spec=ProgramSpec(Mock, alias="mock"),
    basis_gates=["h", "x", "z", "cx", "s", "t"],
    provider_name="myprovider",
)
```

<Info>
  API Reference:{" "}
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.TargetProfile.html#qbraid.runtime.TargetProfile"
    target="_blank"
  >
    qbraid.runtime.TargetProfile &#8599;
  </a>
</Info>

### Provider Setup

Each `QuantumProvider` subclass must implement both a `get_device` and a `get_devices` method. These methods process raw device data,
adapting it into a `TargetProfile` for each device, and return either a single `QuantumDevice` object or a list of them. In this example,
we use the `MySession` class to handle API requests; however, this is illustrative and not mandatory. API interactions can also be managed
directly through other means.

In cases where the API data does not directly conform to the format needed to instantiate a `TargetProfile`, additional mappings and
adaptations will typically be necessary. Below is an example implementation of a provider using `MySession` to construct a `MyDevice`
object. We will explore implementations of `QuantumDevice` subclasses in the next section.

```python
from qbraid.runtime import QuantumProvider, TargetProfile


class MyProvider(QuantumProvider):

    def __init__(self, api_key: str):
        super().__init__()
        self.session = MySession(api_key)

    def _build_profile(self, data: dict[str, Any]) -> TargetProfile:
        return TargetProfile(**data)

    def get_device(self, device_id: str) -> MyDevice:
        data = self.get_device(device_id=device_id)
        profile = self._build_profile(data)
        return MyDevice(profile, self.session)

    def get_devices(self, **kwargs) -> list[MyDevice]:
        data = self.session.get_devices(**kwargs)
        profiles = [self._build_profile(item) for item in data]
        return [MyDevice(profile, self.session) for profile in profiles]
```

<Info>
  API Reference:{" "}
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.QuantumProvider.html#qbraid.runtime.QuantumProvider"
    target="_blank"
  >
    qbraid.runtime.QuantumProvider &#8599;
  </a>
</Info>

## QuantumDevice

The `qbraid.runtime.QuantumDevice` class describes the unique parameters and operational settings necessary for executing quantum
programs on specific hardware.

<Info>
  API Reference:{" "}
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.QuantumDevice.html#qbraid.runtime.QuantumDevice"
    target="_blank"
  >
    qbraid.runtime.QuantumDevice &#8599;
  </a>
</Info>

The device objects are the core component of the providers. These objects are how users can interface between
quantum computing frameworks and hardware/simulators to execute circuits. Any `QuantumDevice` subclass must
implement both a `status` and `submit` method.

A minimum working example could look like:

```python
from qbraid.runtime import DeviceStatus, QuantumDevice


class MyDevice(QuantumDevice):

    def __init__(self, profile: TargetProfile, session: MySession):
        super.__init__(profile=profile)
        self.session = session

    def status(self) -> DeviceStatus:
        data = self.session.get_device(self.id)
        status = data.get("status")
        if status == "online":
            return DeviceStatus.ONLINE
        return DeviceStatus.OFFLINE

    def transform(self, run_input: Mock) -> str:
        program_ir = str(run_input)
        return program_ir

    def submit(self, run_input: str, shots=1000) -> MyJob:
        job_data = {"target": self.id, "inpput": run_input, "shots": shots}
        job_data = self.session.create_job(job_data)
        job_id = job_data["job_id"]
        return MyJob(job_id, session=self.session, device=self, shots=shots)
```

## QuantumJob

The `qbraid.runtime.QuantumJob` class represents the transitional states of quantum programs, managing both ongoing and completed
quantum computations.

<Info>
  API Reference:{" "}
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.QuantumJob.html#qbraid.runtime.QuantumJob"
    target="_blank"
  >
    qbraid.runtime.QuantumJob &#8599;
  </a>
</Info>

```python
from qbraid.runtime import Result, GateModeResultData, JobStatus, QuantumJob


class MyJob(QuantumJob):

    def __init__(self, job_id: str, session: MySession, **kwargs):
        super().__init__(job_id=job_id, **kwargs)
        self.session = session

    def status(self):
        data = self.session.get_job(self.id)
        status = data.get("status")
        if status == "completed":
            return JobStatus.COMPLETED
        if status == "failed":
            return JobStatus.FAILED
        return JobStatus.QUEUED

    def result(self) -> Result:
        self.wait_for_final_state()
        job_data = self.session.get_job(self.id)
        success = job_data.pop("status") == "completed"
        counts = job_data.pop("counts")
        result_data = GateModeResultData(measurement_counts=counts)
        return Result(
            device_id=self.device.id,
            job_id=self.id,
            success=success,
            data=result_data,
            **job_data
        )

```

<Info>
  API Reference:
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.Result.html#qbraid.runtime.Result"
    target="_blank"
  >
    qbraid.runtime.Result &#8599;
  </a>
  <br />
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.GateModelResultData.html#qbraid.runtime.GateModelResultData"
    target="_blank"
  >
    qbraid.runtime.GateModelResultData &#8599;
  </a>
  <br />
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.AhsResultData.html#qbraid.runtime.AhsResultData"
    target="_blank"
  >
    qbraid.runtime.AhsResultData &#8599;
  </a>
  <br />
  <a
    href="https://qbraid.github.io/qBraid/stubs/qbraid.runtime.AnnealingResultData.html#qbraid.runtime.AnnealingResultData"
    target="_blank"
  >
    qbraid.runtime.AnnealingResultData &#8599;
  </a>
</Info>
