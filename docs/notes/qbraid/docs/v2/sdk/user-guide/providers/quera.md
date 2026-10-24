> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/quera.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/quera.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 1dd97c1b3c6aa6d3e40893275f3974bebd801c4023f8d90b566a883d444f3884.

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

# QuEra

> Run analog Hamiltonian simulation programs on QuEra's Aquila neutral-atom QPU through qBraid, with only a qBraid API key.

## Devices on qBraid

QuEra's Aquila is a 256-atom neutral-atom QPU. Unlike the other QPUs on qBraid, it runs **analog** programs: you place atoms and shape the laser drive over time, rather than applying gates. It is on qBraid through one submission path.

| Device ID              | Device              | Path                                    |
| :--------------------- | :------------------ | :-------------------------------------- |
| `aws:quera:qpu:aquila` | Aquila, 256 atoms   | [Amazon Braket](#through-amazon-braket) |

Aquila is available only during scheduled windows. Check its status in the [device catalog](https://account.qbraid.com/devices) before you submit.

## Quick start

Aquila takes Amazon Braket `AnalogHamiltonianSimulation` programs, so install the qBraid SDK with the Braket extra:

```bash
pip install 'qbraid[braket]'
```

Build a program: here, two atoms 6 μm apart under a constant Rabi drive for 4 μs.

```python
from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.ahs.atom_arrangement import AtomArrangement
from braket.ahs.driving_field import DrivingField
from braket.timings.time_series import TimeSeries
from qbraid.runtime import QbraidProvider

register = AtomArrangement()
register.add([0.0, 0.0]).add([0.0, 6.0e-6])

times = [0.0, 1.0e-7, 3.9e-6, 4.0e-6]
amplitude = TimeSeries().put(times[0], 0.0).put(times[1], 1.58e7).put(times[2], 1.58e7).put(times[3], 0.0)
detuning = TimeSeries().put(times[0], 0.0).put(times[3], 0.0)
phase = TimeSeries().put(times[0], 0.0).put(times[3], 0.0)

program = AnalogHamiltonianSimulation(
    register=register,
    hamiltonian=DrivingField(amplitude=amplitude, detuning=detuning, phase=phase),
)

provider = QbraidProvider()
device = provider.get_device("aws:quera:qpu:aquila")

job = device.run(program, shots=100)
print(job.result().data.get_counts())
```

Amazon Braket's [analog Hamiltonian simulation guide](https://docs.aws.amazon.com/braket/latest/developerguide/braket-analog-hamiltonian-simulation.html) explains how to design registers and drives within Aquila's limits.

## Through Amazon Braket

`aws:quera:` devices go through Amazon Braket, billed in qBraid credits. They take [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options). Aquila's local detuning and tighter atom geometries are Braket experimental capabilities, so turn them on to use them:

```python
job = device.run(
    program,
    shots=100,
    runtime_options={"experimental_capabilities": "ALL"},
)
```

## Related links

- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws): what every Braket device has in common
- [Amazon Braket (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws): Aquila with your own AWS account
- [QuEra: Aquila](https://www.quera.com/aquila)
