> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/managing-jobs.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/managing-jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 6c6ec7e1d15c5a9c3244f406152669fd2cbfb76d3050bb8f11e6b5654099aa65.

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

# Managing jobs

> Estimate what a job will cost, label and track it, read its cost and timing, see what ran on the device, and reconnect to it later.

<Info>
  API Reference:
  [qbraid.runtime.native](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.native.html)
</Info>

Everything on this page works the same on every device you reach through `QbraidProvider`, whichever vendor or [submission path](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started#submission-paths) it uses. The examples use the free QIR simulator, `qbraid:qbraid:sim:qir-sv`:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("qbraid:qbraid:sim:qir-sv")

bell = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""
```

## Before you submit

### Check the device

```python
device.status()
# <DeviceStatus.ONLINE: 'ONLINE'>

device.queue_depth()
# 0
```

`device.run()` warns when a device isn't `ONLINE`: the job may be refused, or wait a long time. `provider.get_devices()` lists the devices you can submit to now. Pass `include_retired=True` to also list devices that have been retired.

### Estimate the cost

`provider.client.estimate_cost` prices a job before you submit it, in qBraid credits:

```python
estimate = provider.client.estimate_cost("aws:iqm:qpu:garnet", shots=100)

estimate.pricingAvailable
# True
estimate.estimatedCost
# Credits('44.5')
```

Some devices are priced dynamically by their vendor, so no estimate is possible in advance. For those, `pricingAvailable` is `False` and `reason` says why, such as `'dynamic_pricing_unavailable'`. Devices with `openquantum:` IDs estimate `0`, because they spend credits from your linked [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) account rather than qBraid credits.

The [device catalog](https://account.qbraid.com/devices) shows the same prices.

### Check your balance

```python
balance = provider.client.get_credits_balance()
balance["qbraidCredits"]
```

The balance belongs to the organization your API key is tied to.

## Submitting

```python
job = device.run(
    bell,
    shots=100,
    name="bell-test",
    tags={"experiment": "docs-managing-jobs"},
)
job.id
# 'qbraid:qbraid:sim:qir-sv-8ce1-qjob-6ad8144c34188ba734e7a279'
```

| Argument          | Effect                                                                                              |
| :---------------- | :-------------------------------------------------------------------------------------------------- |
| `shots`           | Number of shots.                                                                                    |
| `name`            | A name for the job, shown in [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs).                              |
| `tags`            | Key-value labels, with string, integer or boolean values. [Find jobs by tag](#find-past-jobs) later. |
| `runtime_options` | Options passed to the device. See [Runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started#runtime-options). |

Keep `job.id`: it is all you need to [get the job back](#reconnect-to-a-job) later.

To run several circuits at once, see [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs).

## While it runs

```python
job.status()
# <QUEUED: 'job is queued'>

job.queue_position()
# 3
```

`queue_position()` returns `None` once the job has left the queue, or when the device doesn't report positions.

A job moves through `INITIALIZING`, `QUEUED`, `RUNNING`, and then one of `COMPLETED`, `FAILED` or `CANCELLED`. `job.is_terminal_state()` tells you whether it has finished.

### Wait for it

`job.result()` blocks until the job finishes. Pass `timeout`, in seconds, to give up waiting. The job keeps running.

```python
result = job.result(timeout=600)
```

`job.wait_for_final_state(timeout=600, poll_interval=5)` waits without fetching the result. In async code, `await job.async_result()` waits without blocking the event loop.

### Cancel it

```python
job.cancel()
```

`cancel()` raises `JobStateError` if the job has already finished. A job that has started running on a QPU may finish before the cancellation reaches it.

## Results

```python
result.success
# True

result.data.get_counts()
# {'00': 46, '11': 54}
```

`result.data` also has `get_probabilities()`, and `measurements` for the individual shots where the device returns them.

### Cost and timing

`result.details` records what the job actually cost and how long it took:

```python
result.details["cost"]
# Credits('0')

result.details["time_stamps"]
# TimeStamps(createdAt=datetime.datetime(2026, 10, 21, 1, 24, 30, tzinfo=datetime.timezone.utc),
#            endedAt=datetime.datetime(2026, 10, 21, 1, 24, 30, tzinfo=datetime.timezone.utc),
#            executionDuration=12)
```

`executionDuration` is in milliseconds.

### When a job fails

A job that doesn't complete still returns a result, with `success` set to `False` and no data. When the platform gives a reason, it is in `details["status_message"]`:

```python
result = job.result()

if not result.success:
    print(result.details["status"])
    print(result.details.get("status_message"))
```

## After it runs

### What you submitted

`job.program()` returns the program as qBraid received it, after any conversion from your framework:

```python
job.program()
# Program(format='qasm3', data='OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q; ...')
```

### What ran on the device

`job.compiled_program()` returns the program the device's compiler produced. On a QPU this shows which physical qubits your circuit ran on and the native gates it was compiled to, which the counts alone can't tell you:

```python
compiled = job.compiled_program()
compiled.format
# 'qir.ll'
```

| Devices                                                                                      | Format   |
| :------------------------------------------------------------------------------------------- | :------- |
| [IQM through Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#retrieving-the-compiled-program)               | `qasm3`  |
| [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti#the-compiled-program), direct or through Amazon Braket              | `quil`   |
| [QIR simulator](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started#basic-usage)                     | `qir.ll` |

It returns `None` when there is no compiled program: the job hasn't finished, the device doesn't report one, or the job predates this feature. A batch job returns a list, one program per circuit.

### Reconnect to a job

A job ID is enough to get a job back, for example after restarting a notebook kernel, or on another machine:

```python
from qbraid.runtime import load_job

job = load_job("qbraid:qbraid:sim:qir-sv-8ce1-qjob-6ad8144c34188ba734e7a279", provider="qbraid")
job.status()
# <COMPLETED: 'job has successfully run'>
```

The returned job supports everything on this page.

### Find past jobs

`provider.client.list_jobs` searches your jobs. Filter by tag, status or text:

```python
jobs = provider.client.list_jobs(tags={"experiment": "docs-managing-jobs"})
[(j.jobQrn, j.name, j.status) for j in jobs]
# [('qbraid:qbraid:sim:qir-sv-8ce1-qjob-6ad8144c34188ba734e7a279', 'bell-test', <COMPLETED: ...>)]
```

| Filter         | Example                                                    |
| :------------- | :--------------------------------------------------------- |
| `tags`         | `{"experiment": "bell-state"}`                             |
| `status`       | `"COMPLETED"`, `"FAILED"`                                  |
| `status_group` | `"pending"` (not finished yet), `"returned"` (finished), `"all"` |
| `search`       | Text matched against your jobs                             |
| `page`, `limit` | Pagination                                                |

Pass a result's `jobQrn` to `load_job` to work with that job. [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs) shows the same jobs in your account.

## Related links

- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Calibrations](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations): live calibration data for choosing qubits
- [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results): plotting results
