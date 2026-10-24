> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/pasqal.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/pasqal.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0b041c4d04066e9739fc3a21a44ff0af618c750d6a2a0b04949b7621994adde4.

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

# Pasqal (self-managed)

> Run Pulser sequences on Pasqal neutral-atom QPUs and emulators with your own Pasqal Cloud account, using the PasqalProvider.

<Note>
  This page uses `PasqalProvider` with your own Pasqal account: jobs go straight to
  Pasqal, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.pasqal](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.pasqal.html)
</Info>

## Overview

The `qbraid.runtime.PasqalProvider` provides support for Pasqal's neutral-atom quantum computers and emulators via
[Pasqal Cloud Services](https://docs.pasqal.com/cloud/). Unlike gate-model providers, Pasqal devices run _analog_
quantum programs: pulse sequences built with [Pulser](https://pulser.readthedocs.io/), Pasqal's open-source framework
for programming neutral-atom arrays. You write a `pulser.Sequence`, and qBraid serializes it, submits it as a Pasqal
Cloud batch, and returns measurement counts—all from within the
[qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

## Getting started

Before you begin, you'll need a [Pasqal Cloud](https://portal.pasqal.cloud/) account and a **project ID**. Jobs
(batches) are billed and organized per project—you can find your project ID in the Pasqal Cloud portal.

### Set up the qBraid-SDK

Install qBraid with the `pasqal` extra from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install 'qbraid[pasqal]'
```

This installs the [pasqal-cloud](https://github.com/pasqal-io/pasqal-cloud) client and
[pulser-core](https://pypi.org/project/pulser-core/) alongside qBraid.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

We encourage doing this inside an environment management system, such as [virtualenv](https://virtualenv.pypa.io/en/latest/) or
[conda](https://docs.conda.io/en/latest/). Alternatively, you can bypass this step by using a pre-configured
[qBraid Lab environment](https://docs.qbraid.com/v2/lab/user-guide/environments).
See [qBraid-SDK installation and setup](https://docs.qbraid.com/v2/sdk/user-guide/overview#installation-and-setup) for more.

### Set up your environment

By default, qBraid will look in your local environment for variables named `PASQAL_USERNAME`, `PASQAL_PASSWORD`,
and `PASQAL_PROJECT_ID`:

```bash
export PASQAL_USERNAME="your_username_here"
export PASQAL_PASSWORD="your_password_here"
export PASQAL_PROJECT_ID="your_project_id_here"
```

Alternatively, you can pass your credentials explicitly when creating the provider object:

```python
from qbraid.runtime import PasqalProvider

provider = PasqalProvider(
    username="me@example.com",
    password="...",
    project_id="...",
)
```

If you provide a `username` but leave `password` unset, `pasqal-cloud` will prompt for it interactively. For
machine-to-machine authentication with a pre-issued token, you can pass a custom `pasqal_cloud.TokenProvider`
via the `token_provider` argument instead.

In the examples below, we show `PasqalProvider()` initialized with no arguments and assume that qBraid will
automatically find your credentials in the environment.

## List available devices

Use the `PasqalProvider` to list the available Pasqal devices:

```python
from qbraid.runtime import PasqalProvider

provider = PasqalProvider()

devices = provider.get_devices()
```

Running this script should print something like this:

```python
[<qbraid.runtime.pasqal.device.PasqalDevice('EMU_FREE')>,
<qbraid.runtime.pasqal.device.PasqalDevice('EMU_FRESNEL')>,
<qbraid.runtime.pasqal.device.PasqalDevice('EMU_MPS')>,
<qbraid.runtime.pasqal.device.PasqalDevice('EMU_SV')>,
<qbraid.runtime.pasqal.device.PasqalDevice('EMU_TN')>,
<qbraid.runtime.pasqal.device.PasqalDevice('FRESNEL')>,
<qbraid.runtime.pasqal.device.PasqalDevice('FRESNEL_CAN1')>]
```

If this works correctly, then your qBraid-SDK installation is correct and your Pasqal credentials are valid!

Device IDs starting with `EMU_` are emulators; the rest are QPUs:

| Device ID      | Type     | Description                                         |
| -------------- | -------- | --------------------------------------------------- |
| `FRESNEL`      | QPU      | Pasqal's neutral-atom quantum processor             |
| `FRESNEL_CAN1` | QPU      | FRESNEL-class QPU (Canada)                          |
| `EMU_FREE`     | Emulator | Free-tier emulator (limited resources)              |
| `EMU_FRESNEL`  | Emulator | Emulates the FRESNEL QPU, including its constraints |
| `EMU_SV`       | Emulator | State-vector emulator                               |
| `EMU_MPS`      | Emulator | Matrix-product-state emulator                       |
| `EMU_TN`       | Emulator | Tensor-network emulator                             |

You can confirm whether a device is a simulator, and inspect its runtime profile, directly from the device object:

```python
device = provider.get_device("EMU_FREE")

print(device.profile.simulator)        # True
print(device.profile.experiment_type)  # ExperimentType.ANALOG
```

## Build a Pulser sequence

Pasqal devices execute Pulser sequences rather than gate-model circuits. A sequence specifies a _register_ (the
positions of the atoms, in µm) and a series of _pulses_ applied through the device's channels. For an introduction,
see the [Pulser documentation](https://pulser.readthedocs.io/).

Here, we place two atoms 10 µm apart and drive them with a single constant global pulse:

```python
from pulser import Pulse, Register, Sequence
from pulser.devices import AnalogDevice

register = Register({"q0": (0, 0), "q1": (0, 10)})

sequence = Sequence(register, AnalogDevice)
sequence.declare_channel("rydberg_global", "rydberg_global")

pulse = Pulse.ConstantPulse(duration=1000, amplitude=5.0, detuning=0, phase=0)
sequence.add(pulse, "rydberg_global")

sequence.measure("ground-rydberg")
```

<Warning>
  Remember to end your sequence with a `measure()` call. Measurement in the
  `"ground-rydberg"` basis maps each atom to a classical bit: `1` if the atom
  was excited to the Rydberg state, `0` otherwise.
</Warning>

## Submit a sequence to an emulator

Let's run the sequence on `EMU_FREE` with 100 shots:

```python
from qbraid.runtime import PasqalProvider

provider = PasqalProvider()
device = provider.get_device("EMU_FREE")

job = device.run(sequence, shots=100)

print(job.id)        # the Pasqal Cloud batch ID, e.g. 'c2bbfadf-e2d1-...'
print(job.status())  # JobStatus.QUEUED
```

Each submission creates a Pasqal Cloud _batch_, and `job.id` is the batch ID—you can use it to look the job up
later, both through qBraid and in the Pasqal Cloud portal. Calling `job.result()` blocks until the batch reaches
a terminal state, then returns the measurement counts:

```python
result = job.result()

print(result.data.get_counts())
```

This returns a dictionary of bitstring counts, for example:

```
{'00': 38, '11': 13, '10': 29, '01': 20}
```

Since this is an analog experiment, the result data is a qBraid `AnalogResultData` instance, keyed by
measurement bitstrings in register order (`q0`, `q1`, ...).

## Submit a multi-sequence batch

You can submit several sequences in a single batch by passing a list to `device.run()`. Each sequence becomes its
own job within the Pasqal Cloud batch, and the results are returned as a list of counts dictionaries in
submission order. Given two sequences `sequence_a` and `sequence_b`, built as in the example above:

```python
batch_job = device.run([sequence_a, sequence_b], shots=50)

batch_result = batch_job.result()

counts_list = batch_result.data.get_counts()

print("\n".join(f"Sequence {i}: {c}" for i, c in enumerate(counts_list)))
```

```
Sequence 0: {'10': 12, '00': 19, '01': 14, '11': 5}
Sequence 1: {'10': 11, '00': 19, '11': 7, '01': 13}
```

## Submit a sequence to a QPU

Submitting to a QPU follows the exact same pattern—just use a QPU device ID:

```python
device = provider.get_device("FRESNEL")

job = device.run(sequence, shots=100)
```

<Tip>
  Build your sequence against a Pulser device specification that matches the
  target QPU's constraints (register geometry, channels, pulse limits), and test
  it on an emulator first—`EMU_FRESNEL` mirrors the FRESNEL QPU's constraints.
  QPU access is subject to your Pasqal Cloud project's permissions and quota.
</Tip>

QPU jobs may wait in the queue, so record `job.id` and retrieve the job later rather than blocking on
`job.result()`.

## Manage jobs

### Retrieve a job

You can retrieve a previously submitted job from its batch ID:

```python
from qbraid.runtime import PasqalJob, PasqalProvider

provider = PasqalProvider()

job = PasqalJob("your_batch_id_here", sdk=provider.sdk)

print(job.status())

result = job.result()
print(result.data.get_counts())
```

### Cancel a job

You can cancel a job (batch) while it's waiting in the queue:

```python
job.cancel()
```

## Visualize results

To plot the results of a job, first, install the qBraid visualization extra:

```bash
pip install 'qbraid[visualization]'
```

You can then visualize the measurement counts using `plot_histogram`, or display the probability distribution
with `plot_distribution`:

```python
from qbraid.visualization import plot_histogram

counts = result.data.get_counts()

plot_histogram(counts)
```

The "counts" input may be either a single dictionary or a list of dictionaries for multi-sequence batches.
See [Plot Experimental Results](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) for more.

---

## Additional resources

_Great work!_ You successfully ran your first analog quantum program - _what next?_

Explore more resources for using qBraid:

- [API Reference](https://qbraid.github.io/qBraid/)
- [Source Code on GitHub](https://github.com/qBraid/qBraid)
- [Example Notebooks on GitHub](https://github.com/qBraid/qbraid-lab-demo)

And for going deeper with Pasqal and Pulser:

- [Pasqal Runtime Provider Notebook on GitHub](https://github.com/qBraid/qbraid-lab-demo/blob/main/Provider-Jobs/qbraid_runtime_pasqal_provider.ipynb)
- [Pulser on Pasqal Devices Notebook on GitHub](https://github.com/qBraid/qbraid-lab-demo/blob/main/qBraid-Runtime/qbraid_pulser_pasqal.ipynb)
- [Pasqal Cloud documentation](https://docs.pasqal.com/cloud/)
- [Pulser documentation](https://pulser.readthedocs.io/)
- [pasqal-cloud on GitHub](https://github.com/pasqal-io/pasqal-cloud)
