> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 f22ee9a628f8b87ad3b1d243f955fcfc4866a6238b299146f9b38d2a41156a8a.

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

# Batch and group jobs

> Run several circuits through the QbraidProvider as separate jobs, as one batch job on one device, or as a group of jobs across devices.

<Info>
  API Reference:
  [qbraid.runtime.native](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.native.html)
</Info>

There are three ways to run more than one circuit through the `QbraidProvider`. For a single
circuit, see [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started#basic-usage).

## Which one to use

|                       | Separate jobs                      | Batch job                                       | Group job                            |
| --------------------- | ---------------------------------- | ----------------------------------------------- | ------------------------------------ |
| **Scope**             | Multiple circuits, one device      | Multiple circuits, one device                   | Multiple jobs, any devices           |
| **Submission**        | `device.run(programs)`             | `device.run(programs, as_batch=True)`           | `GroupJobSession` context            |
| **Return type**       | A list of `QbraidJob`              | Single `QbraidJob` → `BatchResult`              | Multiple `QbraidJob` → `GroupResult` |
| **Use case**          | A few unrelated circuits           | Parameterized circuits, algorithm variants      | Cross-device benchmarks, sweeps      |
| **Supported devices** | All devices                        | Devices with `device.profile.batch_job_support` | All devices                          |

## Separate jobs

Passing a list of programs to `device.run()` submits each one as its own job:

```python
programs = [bell_circuit, ghz_circuit, qft_circuit]
jobs = device.run(programs, shots=100)
results = [job.result() for job in jobs]
```

For async applications, [`async_result()`](https://docs.qbraid.com/v2/sdk/user-guide/overview#async-results) awaits a
job without blocking the event loop:

```python
result = await job.async_result(timeout=120, poll_interval=5)
print(result.data.get_counts())
```

## Batch Jobs

Submit multiple circuits as a **single job** to a device that supports batched execution.
Unlike [group jobs](#group-jobs), which coordinate independent jobs across devices, batch
jobs send all circuits in one request and return a unified result.

### Submitting a Batch

Pass a list of programs with `as_batch=True` to submit them as a single job:

```python
from qiskit import QuantumCircuit
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("qbraid:equal1:sim:bell-1")

# Define multiple circuits
bell = QuantumCircuit(2, 2)
bell.h(0)
bell.cx(0, 1)
bell.measure([0, 1], [0, 1])

ghz = QuantumCircuit(3, 3)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(1, 2)
ghz.measure([0, 1, 2], [0, 1, 2])

x_gate = QuantumCircuit(1, 1)
x_gate.x(0)
x_gate.measure(0, 0)

# Submit all three circuits as a single batch job
job = device.run([bell, ghz, x_gate], shots=1000, as_batch=True)
print(type(job))
# <class 'qbraid.runtime.native.job.QbraidJob'>
```

A batch submission returns a single `QbraidJob`, not a list. All circuits share the same
job ID, device, and shot count.

<Note>
  `as_batch=True` requires a device that supports batch execution. You can check
  this via the device profile's `batch_job_support` flag. Passing
  `as_batch=True` to an unsupported device raises a `ValueError`. Devices that
  support it include `qbraid:equal1:sim:bell-1`, the QUDORA simulators
  `qudora:qudora:sim:qvls-q1-emulator` and `qudora:qudora:sim:qamelion`, and the
  [GPU simulators](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators#batch-jobs)
  `qbraid:qbraid:sim:gpu-sv` and `qbraid:qbraid:sim:gpu-tn`.
</Note>

### Retrieving Batch Results

Calling `job.result()` on a batch job returns a `BatchResult` object:

<CodeGroup>

```python Retrieval
result = job.result()
print(type(result))
print(result.num_circuits)
```

```text Output
<class 'qbraid.runtime.result.BatchResult'>
3
```

</CodeGroup>

`BatchResult` provides two ways to access measurement data:

**Aggregate access** — indexed by circuit position:

<CodeGroup>

```python Aggregate
# All circuit counts as a list
all_counts = result.data.get_counts()
for i, counts in enumerate(all_counts):
    print(f"Circuit {i}: {counts}")
```

```text Output
Circuit 0: {'00': 512, '11': 488}
Circuit 1: {'000': 498, '111': 502}
Circuit 2: {'1': 1000}
```

</CodeGroup>

**Per-circuit access** — each circuit's `Result` is a full object with its own status and metadata:

<CodeGroup>

```python Per-Circuit
for i, circuit_result in enumerate(result.results):
    print(f"Circuit {i}: status={circuit_result.success}, counts={circuit_result.data.get_counts()}")
```

```text Output
Circuit 0: status=True, counts={'00': 512, '11': 488}
Circuit 1: status=True, counts={'000': 498, '111': 502}
Circuit 2: status=True, counts={'1': 1000}
```

</CodeGroup>

### BatchResult Properties

| Property       | Type           | Description                                                             |
| -------------- | -------------- | ----------------------------------------------------------------------- |
| `num_circuits` | `int`          | Number of circuits in the batch                                         |
| `results`      | `list[Result]` | Per-circuit `Result` objects                                            |
| `data`         | `ResultData`   | Aggregated data — `get_counts()` and `get_probabilities()` return lists |
| `details`      | `list[dict]`   | Per-circuit metadata (e.g. `compiledOutput`)                            |
| `success`      | `bool`         | Whether the overall job completed successfully                          |
| `device_id`    | `str`          | Device QRN                                                              |
| `job_id`       | `str`          | Job QRN                                                                 |

### Per-Circuit Error Handling

In a batch job, individual circuits can fail while others succeed. Failed circuits
carry their own error message, accessible through their per-circuit result:

```python
result = job.result()

for i, circuit_result in enumerate(result.results):
    if not circuit_result.success:
        print(f"Circuit {i} failed: {circuit_result.details.get('statusMsg')}")
    else:
        print(f"Circuit {i}: {circuit_result.data.get_counts()}")
```

## Group Jobs

### Why Group?

When running related quantum experiments — parameter sweeps, algorithm comparisons,
cross-device benchmarks — you often end up with many independent jobs that are logically
part of the same workflow. Without grouping, these jobs are scattered across your job history
with no way to track or retrieve them together.

**`GroupJobSession`** solves this by grouping any number of jobs under a single group ID.
Key benefits:

- **Cross-device, cross-provider**: submit jobs to different backends (AWS SV1, IonQ, qBraid simulators) within the same group
- **Unified tracking**: all jobs share a group QRN visible in the qBraid dashboard
- **Aggregated results**: retrieve all results at once with `group.results()`
- **Lifecycle management**: auto-close with TTL, cancellation, completion callbacks

<Note>
  `GroupJobSession` builds its own API client rather than borrowing one from a provider. The examples below rely on credentials already configured on the machine, through `qbraid configure` or the `QBRAID_API_KEY` environment variable.

  If you pass your key in code instead, hand the session your provider's client. Without it the session cannot see your credentials and fails to authenticate:

  ```python
  provider = QbraidProvider(api_key=API_KEY)
  
  with GroupJobSession(name="sweep", client=provider.client) as group:
      job = device.run(circuit, shots=100)
  ```
</Note>

### Context Manager

The simplest way to use group jobs. All jobs submitted inside the `with` block are
automatically tagged with the group ID. The group closes when the block exits.

```python
from qbraid.runtime import GroupJobSession, QbraidProvider

provider = QbraidProvider()

bell = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

# All jobs inside this block belong to the same group
with GroupJobSession(name="Bell State Sweep") as group:
    # Submit to different devices within the same group
    sv1 = provider.get_device("aws:aws:sim:sv1")
    job1 = sv1.run(bell, shots=100)

    tn1 = provider.get_device("aws:aws:sim:tn1")
    job2 = tn1.run(bell, shots=100)

    print(f"Group ID: {group.group_id}")
    print(f"Jobs in group: {len(group.jobs)}")

# Group ID: group:abc-123456
# Jobs in group: 2
```

### Manual Open / Close

For interactive workflows like Jupyter notebooks, you can open and close the group
manually across multiple cells.

```python
from qbraid.runtime import GroupJobSession, QbraidProvider

provider = QbraidProvider()

# Create and open the group manually
group = GroupJobSession(name="Notebook Experiment")
group.open()

# Cell 2: submit jobs (can be in separate notebook cells)
device = provider.get_device("qbraid:qbraid:sim:qir-sv")
job1 = device.run(circuit_1, shots=100)
job2 = device.run(circuit_2, shots=100)

# Cell 3: close when done submitting
group.close()
```

### Auto-Close with TTL

Set a time-to-live so the group automatically closes after a duration, even if you
forget to call `close()` or your kernel crashes. Defaults to 1 hour (3600s) if not specified.

```python
# Group auto-closes after 60 seconds (default: 3600s / 1 hour)
with GroupJobSession(name="Quick Sweep", max_ttl=60) as group:
    device = provider.get_device("aws:aws:sim:sv1")
    job = device.run(bell, shots=10)
    print(f"TTL: {group.max_ttl}s")
```

<Tip>
  The `max_ttl` parameter accepts values from 1 to 86400 seconds (24 hours). If
  not specified, the backend defaults to 3600 seconds (1 hour).
</Tip>

### Retrieving Results

After closing a group, retrieve all job results at once. `group.results()` blocks until
every job reaches a terminal state (completed, failed, or cancelled).

<CodeGroup>

```python Submission
with GroupJobSession(name="Result Demo") as group:
    device = provider.get_device("qbraid:qbraid:sim:qir-sv")
    job1 = device.run(bell, shots=100)
    job2 = device.run(bell, shots=100)

# Wait for all jobs and collect results
results = group.results(timeout=300)
print(results)

for job_id, result in results.results.items():
    print(f"{job_id}: {result.data.get_counts()}")
```

```text Results
GroupResult(group_id='group:ghi-345678', total=2, successful=2, failed=0)
job:aaa-111: {'00': 48, '11': 52}
job:bbb-222: {'00': 51, '11': 49}
```

</CodeGroup>

You can also filter results by outcome:

```python
# Only successful results
successful = results.successful()

# Only failed results
failed = results.failed()
```

### Completion Callback

Register a callback that fires automatically when all jobs complete. The callback
runs at context exit, after the group is closed.

<CodeGroup>

```python Callback Setup
def analyze(results):
    """Process results when all jobs finish."""
    for job_id, result in results.items():
        counts = result.data.get_counts()
        print(f"{job_id}: {counts}")

with GroupJobSession(name="With Callback") as group:
    device = provider.get_device("qbraid:qbraid:sim:qir-sv")
    device.run(bell, shots=100)
    device.run(bell, shots=100)

    # Callback fires automatically when the context exits
    group.on_all_complete(analyze, timeout=600)
```

```text Callback Output
job:ccc-333: {'00': 47, '11': 53}
job:ddd-444: {'00': 50, '11': 50}
```

</CodeGroup>

### Cancellation

Cancel a group and all its non-terminal jobs:

```python
group = GroupJobSession(name="Cancellable")
group.open()

device = provider.get_device("aws:aws:sim:sv1")
job1 = device.run(bell, shots=1000)
job2 = device.run(bell, shots=1000)

# Cancel the entire group and reset the session
group.cancel()

print(group.status())
# GroupStatus.CANCELLED
```
