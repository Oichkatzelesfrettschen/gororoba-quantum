> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 dc1a2219b0b6dba333ab33061f6ddb301ca986f438ccf34a6e20ad647025d0ac.

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

# GPU simulators

> Running circuits on qBraid's GPU state-vector and tensor-network simulators through the QbraidProvider, with every option, their limits, daily allowance, and per-minute pricing.

<Info>
  Device IDs: `qbraid:qbraid:sim:gpu-sv` (state vector, up to 35 qubits) &nbsp;·&nbsp;
  `qbraid:qbraid:sim:gpu-tn` (tensor network, up to 500 qubits) &nbsp;·&nbsp; NVIDIA GH200
  &nbsp;·&nbsp; batch jobs &nbsp;·&nbsp; free daily allowance, then 5 credits per minute with
  usage-based billing &nbsp;·&nbsp; accessed through
  [`QbraidProvider`](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started)
</Info>

qBraid runs two GPU simulators on its Leo cluster, on NVIDIA GH200 Grace Hopper with 96 GB of
HBM3. They answer different questions:

| Simulator | Device ID                  | Use it for                                                                                                        |
| :-------- | :------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| gpu-sv    | `qbraid:qbraid:sim:gpu-sv` | **Exact** state-vector simulation of any circuit up to **35 qubits** (34 in double precision).                    |
| gpu-tn    | `qbraid:qbraid:sim:gpu-tn` | **Wide, low-entanglement** circuits, up to **500 qubits**, as a matrix product state (MPS) or exact contraction. |

If your circuit fits in 35 qubits, gpu-sv gives the exact answer whatever its entanglement. Past
that, gpu-tn can go much wider, as long as the circuit stays weakly entangled: GHZ states, shallow
circuits, and circuits whose two-qubit gates act on neighboring qubits.

<Note>
  Each GPU simulator has a **free daily allowance**: 25 circuits a day on Free, 125 on Standard,
  and unlimited on Pro and Enterprise. A single job is one circuit, and a batch counts one per
  circuit. Jobs past the allowance are refused unless you turn on
  usage-based billing, which charges them at 5 credits ($0.05) per minute. See
  [Pricing and daily allowance](#pricing-and-daily-allowance).
</Note>

## Quick start

Both simulators take OpenQASM 2 or OpenQASM 3. A Bell pair on gpu-sv:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("qbraid:qbraid:sim:gpu-sv")

bell = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
"""

job = device.run(bell, shots=1000)
print(job.result().data.get_counts())
# only '00' and '11', about half each: the simulation is exact and noiseless
```

A 100-qubit GHZ state is far past any state vector, but it is easy for gpu-tn. Writing it as a
chain of neighboring CNOTs keeps it fast:

```python
device = provider.get_device("qbraid:qbraid:sim:gpu-tn")

n = 100
lines = ["OPENQASM 2.0;", 'include "qelib1.inc";', f"qreg q[{n}];", f"creg c[{n}];", "h q[0];"]
lines += [f"cx q[{i}],q[{i + 1}];" for i in range(n - 1)]
lines.append("measure q -> c;")

job = device.run("\n".join(lines), shots=1000)
print(job.result().data.get_counts())
# only '000…0' and '111…1': a GHZ state stays exact under MPS at any width
```

## Runtime options

Device options go in the **`runtime_options`** dict, not in the `run()` signature. `shots` is the
exception: pass it to `run()` directly.

```python
job = device.run(program, shots=1000, runtime_options={"precision": "double"})
```

### gpu-sv

| Option      | Type | Default    | Effect                                                                                       |
| :---------- | :--- | :--------- | :------------------------------------------------------------------------------------------- |
| `shots`     | int  | —          | 1 to **1,000,000**. Passed directly to `run()`, not in the dict.                             |
| `precision` | str  | `"single"` | `"single"` (complex64, up to **35** qubits) or `"double"` (complex128, up to **34** qubits). |
| `timeout`   | int  | none       | A time limit in whole seconds, at least 1. Checked between the steps of a job. See [Timeouts](#timeouts). |
| `seed`      | int  | none       | Seeds the sampling: the same seed, circuit and options return the same counts. 0 to 4,294,967,295 (2³² − 1). See [Reproducible counts](#reproducible-counts). |

Past 33 qubits in single precision, or 32 in double, the state vector is larger than the GPU's
memory, and gpu-sv keeps the rest in the GH200's host memory. That happens automatically, with no
option to set, and those jobs take longer: see [Execution time](#execution-time).

### gpu-tn

| Option            | Type  | Default    | Effect                                                                                                                                  |
| :---------------- | :---- | :--------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| `shots`           | int   | —          | 1 to **10,000**. Passed directly to `run()`, not in the dict.                                                                           |
| `method`          | str   | `"mps"`    | `"mps"`: matrix product state, approximate once truncated. `"exact"`: full tensor-network contraction.                                 |
| `maxBondDim`      | int   | `64`       | MPS only. The largest bond dimension kept, 2 to 1024.                                                                                   |
| `relativeCutoff`  | float | `1e-5`     | MPS only. Singular values below this fraction of the largest are dropped. Strictly between 0 and 1.                                    |
| `absoluteCutoff`  | float | `1e-5`     | MPS only. Singular values below this value are dropped. Strictly between 0 and 1.                                                       |
| `precision`       | str   | `"double"` | `"double"` (complex128) or `"single"` (complex64).                                                                                      |
| `numHyperSamples` | int   | 8          | `exact` only. The number of hyper-samples the contraction-path finder tries, at least 1. Accepted and ignored for `mps`.                 |
| `timeout`         | int   | none       | A time limit in whole seconds, at least 1. Sampling is stopped when it runs out. See [Timeouts](#timeouts).                            |
| `svdAlgorithm`    | str   | `"GESVDJ"` | MPS only. The SVD that truncates the bonds: `"GESVD"` (QR), `"GESVDJ"` (Jacobi) or `"GESVDP"` (polar decomposition). Accepted and ignored for `exact`. |
| `seed`            | int   | none       | Seeds the sampling, with either method. 0 to 4,294,967,295 (2³² − 1). See [Reproducible counts](#reproducible-counts).               |

```python
device = provider.get_device("qbraid:qbraid:sim:gpu-tn")

job = device.run(program, shots=1000, runtime_options={"maxBondDim": 256, "relativeCutoff": 1e-8})
job = device.run(program, shots=1000, runtime_options={"method": "exact"})
```

Both simulators also accept `irType` (`"qasm2"` or `"qasm3"`). It only labels the input: the
program's own `OPENQASM` header selects the parser, so you don't need to set it.

<Warning>
  **The two simulators default to different precisions.** gpu-sv defaults to `"single"`, which is
  what reaches 35 qubits; gpu-tn defaults to `"double"`.
</Warning>

### Reproducible counts

Pass a `seed` and the same circuit, options and seed return the same counts:

```python
job = device.run(program, shots=1000, runtime_options={"seed": 42})
```

Leave it out and each run draws a fresh sample. Counts are reproducible on the same simulator
release; a later release may sample differently from the same seed.

### What is not an option

- **The MPS gauge.** On gpu-tn, `maxBondDim`, the two cutoffs and `svdAlgorithm` are the only
  controls over MPS truncation.

### How a bad option is refused

Options are checked when the job runs. An option the simulator doesn't know, or a value out of
range, fails the job: it ends `FAILED`, is charged 0 credits, and its status message names the
option.

```python
job = device.run(program, shots=1000, runtime_options={"max_bond_dim": 128})
job.wait_for_final_state()
print(job.status().status_message)
# Unknown option 'max_bond_dim'
```

The messages take two forms:

```text
Unknown option '<name>'
Invalid option '<name>': <what the value must be>
```

For example:

```text
Unknown option 'gauge'
Invalid option 'maxBondDim': must be less than or equal to 1024
Invalid option 'relativeCutoff': must be greater than 0
Invalid option 'numHyperSamples': must be greater than or equal to 1
Invalid option 'precision': must be 'single' or 'double'
```

## Choosing an MPS or exact contraction on gpu-tn

### MPS is approximate once bonds are truncated

A matrix product state is exact while every bond stays within `maxBondDim`. Highly entangling
circuits, such as deep random circuits or a QFT on a wide register, need larger bonds. Past
`maxBondDim`, or below the cutoffs, the simulator truncates, and the counts are sampled from an
approximation. GHZ and other low-entanglement circuits stay exact at any width.

### Choosing maxBondDim and the cutoffs

The defaults, `maxBondDim` 64 and both cutoffs at `1e-5`, keep many circuits exact. Setting them
too low shows up in the counts. On a 16-qubit mirror circuit, 12 random `u3` and `cx` brickwork
layers followed by their inverse, the ideal outcome is all zeros with probability 1. With 1,000
shots:

| Options                                       | Share of shots on all zeros | Distinct outcomes |
| :-------------------------------------------- | --------------------------: | ----------------: |
| defaults (`maxBondDim` 64)                     |                       1.000 |                 1 |
| `maxBondDim` 2                                 |                       0.012 |               676 |
| `maxBondDim` 4                                 |                       0.153 |               519 |
| `relativeCutoff` 0.2 and `absoluteCutoff` 0.2 |                       0.843 |                54 |
| `method` `"exact"`                            |                       1.000 |                 1 |
| `precision` `"single"`                        |                       1.000 |                 1 |

To check whether truncation matters for your circuit, run it again with a larger `maxBondDim`, or
with `method: "exact"` if the circuit is small, and compare the counts. If they agree, the smaller
setting was enough.

Raising `maxBondDim` costs memory and time. Time grows roughly with the cube of the bond
dimension: a 64-qubit random circuit of depth 30 took about 7 s at `maxBondDim` 64 and about 30 s
at 256. To truncate less without raising `maxBondDim`, lower the cutoffs. Both must stay above 0,
so send a tiny value such as `1e-12` rather than 0.

### MPS runs one- and two-qubit gates

With `mps`, every gate on three or more qubits is rewritten into exactly equivalent one- and
two-qubit gates before it runs. This adds gates: a Toffoli becomes 8, and an X with four controls
becomes 88. A gate with more than 6 controls is refused under `mps`:

```text
Method 'mps' runs gates with at most 6 control qubits (a controlled swap counts one more, for its
second target); this circuit has a gate with 7. Use method 'exact' for it.
```

`exact` runs those gates as written.

### Exact contraction: an estimate, then a 10-minute stop

Exact contraction can take far longer than MPS, and its cost climbs steeply with width and depth.
Two protections keep an `exact` job from holding the GPU indefinitely.

1. **An up-front estimate.** Before an `exact` job contracts anything, gpu-tn estimates its cost
   and refuses a circuit estimated beyond what the GPU can sample within the job's time limit:

   ```text
   Exact tensor-network contraction of this circuit is estimated at … floating-point operations,
   beyond what the GPU can sample within the job's time limit. Use method 'mps' (the default) or a
   smaller circuit.
   ```

2. **The 10-minute stop.** The estimate catches many out-of-reach circuits, but not all. A job it
   lets through is still stopped after [10 minutes](#timeouts). A 32-qubit QFT followed by its
   inverse passed the estimate under `exact`, ran for 10 minutes, and was stopped with
   `Exact tensor-network contraction exceeded 10 minutes and was stopped. Use method 'mps' (the
   default) or a smaller circuit.` The stopped job failed and was charged 0 credits. The same
   circuit took 10.6 s under `mps`.

## Timeouts

`timeout` is a whole number of seconds, at least 1. `0` is refused; it does not mean "no limit".
Leave the option out for no per-request limit.

**gpu-tn** samples every job in a separate process that is stopped after **10 minutes**, or when
your `timeout` runs out if that comes first. The message says which limit stopped it:

```text
Matrix product state simulation exceeded the request's timeout of 30 seconds and was stopped.
Exact tensor-network contraction exceeded the request's timeout of 30 seconds and was stopped.
Matrix product state simulation exceeded 10 minutes and was stopped. Use a smaller maxBondDim, fewer shots or a smaller circuit.
Exact tensor-network contraction exceeded 10 minutes and was stopped. Use method 'mps' (the default) or a smaller circuit.
```

A job that finishes in time keeps its result. A stopped job fails and is not charged.

**gpu-sv** checks `timeout` between the steps of a job, not during the GPU simulation itself, so a
simulation that is already running can take longer than the limit. A job stopped by it fails with:

```text
Simulation exceeded the allowed time limit of 30 seconds.
```

gpu-tn reports the same message when its `timeout` runs out before sampling has started.

## What a circuit may contain

Both simulators accept the same programs.

- **OpenQASM 2 and OpenQASM 3.** The program's own `OPENQASM` header selects the parser. Loops,
  custom gates, subroutines, broadcasts, and aliases are unrolled before the circuit runs.
- **Every gate of `qelib1.inc` and `stdgates.inc`**, plus the `ctrl @`, `negctrl @`, `inv @`, and
  integer `pow @` modifiers.
- **Hardware qubits** (`$0`, `$1`, …), as `qiskit.qasm3.dumps` writes a transpiled circuit. `$3` is
  qubit 3. A program cannot mix them with declared qubits.
- **`barrier` and `delay`** are accepted and ignored.

Circuits measure at the end. These are refused with a message that names the feature, such as
`Unsupported OpenQASM feature: mid-circuit measurement ('h' acts on q[0] after it was measured)`:

- a gate on a qubit after it was measured (mid-circuit measurement)
- `reset` after a gate or measurement on that qubit. A `reset` of a qubit nothing has acted on yet is
  skipped, since the qubit is still in |0⟩.
- `while` loops, and classical control flow on measured bits (`if`, `switch`)
- assigning or initializing classical bits other than by measurement
- `pragma`, `box`, pulse-level `cal` and `defcal`, and `input` or `output` declarations
- gates with no definition (`opaque`) and non-integer `pow @`

## Reading the results

Count keys follow your circuit's classical register, with **classical bit 0 rightmost**, the same
convention as Qiskit and every qBraid simulator. Classical bits that no measurement writes read
`0`. Multiple registers are concatenated in declaration order, with the last register leftmost.

A circuit with no measurements reports every qubit, with qubit 0 rightmost.

Each result also records how the job was simulated. The fields are in the result's `details`:

```python
result = job.result()
print(result.data.get_counts())
print(result.details["simulationMethod"], result.details["precision"])
```

| Field                                              | gpu-sv          | gpu-tn                                                         |
| :------------------------------------------------- | :-------------- | :------------------------------------------------------------- |
| `numQubits`                                        | Circuit width   | Circuit width                                                  |
| `precision`                                        | The precision used | The precision used                                         |
| `simulationMethod`                                 | `"statevector"` | `"matrix_product_state"` (`mps`) or `"tensor_network"` (`exact`) |
| `maxBondDim`, `relativeCutoff`, `absoluteCutoff`   | Not present     | `mps` only: the truncation settings the counts were sampled under |

So an MPS result always carries the approximation it was sampled under. Exact results omit the
MPS fields.

## Batch jobs

Both GPU simulators support [batch jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs#batch-jobs)
(`device.profile.batch_job_support` is `True`). Pass a list of circuits with `as_batch=True` and
they run as **one job**, with one job ID and one status, and you get one set of counts per circuit,
in order:

```python
from qiskit import QuantumCircuit

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()

ghz = QuantumCircuit(3)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(1, 2)
ghz.measure_all()

job = device.run([bell, ghz], shots=200, as_batch=True)
job.result().data.get_counts()
# [{'00': 99, '11': 101}, {'000': 108, '111': 92}]
```

The circuits run one after another in the same GPU allocation, so a batch skips the submission and
queueing overhead that separate jobs each pay.

- **The daily allowance counts circuits.** A batch of N circuits uses N of the day's free circuits.
  See [Pricing and daily allowance](#pricing-and-daily-allowance).
- **One set of options for the whole batch.** `runtime_options` apply to every circuit in it.
- **Circuits fail on their own.** One circuit that fails, for example on an unsupported gate,
  doesn't fail the others. Each failed circuit's result says why.
- **The time limit covers the whole batch.** A circuit that couldn't finish before the job's time
  limit isn't started, and its result says to submit it again in a new job:

  ```text
  Not run: the batch reached its time limit before this circuit could start. Submit it again in a new job.
  ```

Without `as_batch=True`, a list of circuits is submitted as **separate jobs**, one per circuit,
and `run()` returns a list of jobs.

## Pricing and daily allowance

Each GPU simulator has its own **free daily allowance** of circuits. A single job is one circuit,
and a [batch](#batch-jobs) of N circuits is N. A job counts against the allowance when you submit
it, and the count resets at **00:00 UTC**.

| Plan       | Free circuits per day, per GPU simulator |
| :--------- | ---------------------------------------: |
| Free       |                                       25 |
| Standard   |                                      125 |
| Pro        |                                Unlimited |
| Enterprise |                                Unlimited |

- **Jobs inside the allowance are free.** The simulator's price is waived.
- **A job inside the allowance that fails or is cancelled** gives its place in the allowance back.
  A batch that fails part-way keeps the places of the circuits that completed and gives back the
  rest.
- **Once the allowance is used**, further jobs are refused until the next reset:

  ```text
  Daily free allowance for qbraid:qbraid:sim:gpu-sv reached (25/day). Resets at midnight UTC.
  Enable usage-based billing for simulators to keep running jobs, charged from your credits at the
  device's per-minute price.
  ```

  A batch is admitted whole or not at all. One bigger than what remains of the allowance is refused
  before it runs:

  ```text
  This batch of 30 circuits needs 30 slots of your daily free allowance for qbraid:qbraid:sim:gpu-sv,
  and 23 of 25 remain today. Resets at midnight UTC. Submit fewer circuits, or enable usage-based
  billing for simulators to run the whole batch, charged from your credits at the device's
  per-minute price.
  ```

- **With usage-based billing turned on**, those further jobs run and are charged from your credits
  at **5 credits per minute** ($0.05), in proportion to each job's execution time, with a minimum of
  **3 seconds** (0.25 credits) per single-circuit job. A batch that doesn't fit in the allowance
  runs paid as a whole.
- **A job that fails is not charged**, inside or beyond the allowance. That includes a job refused
  for a bad option and a job stopped at a time limit. A batch where some circuits fail is charged
  for its full execution time; one where none complete is free.

| Execution time | Credits charged            |
| :------------- | :------------------------- |
| 1.0 s          | 0.25, the 3-second minimum |
| 14.3 s         | about 1.19                 |
| 21.8 s         | about 1.82                 |

Usage-based billing is off unless you turn it on. Turn it on with **Usage-based billing for GPU
simulators** on the **Simulator Usage** card in **Account > Usage**. See
[Simulator usage](https://docs.qbraid.com/v2/account/usage#simulator-usage). Pro and Enterprise plans have no daily limit,
so they never need it.

## Execution time

These are the execution times that jobs recorded on the GH200 at simulator version 0.3.1, with
1,000 shots. Execution time is what usage-based billing charges for. Your circuits will differ, but
the shape holds. The circuits are:

- **GHZ, fan-out**: H on qubit 0, then a CNOT from qubit 0 to every other qubit.
- **Random brickwork, depth d**: d layers, each a random `u3` on every qubit and CNOTs on
  alternating neighboring pairs.
- **Mirror brickwork, depth d**: the same brickwork followed by its inverse.
- **QFT and inverse**: a QFT followed by its inverse, which has controlled phases between every pair
  of qubits.

**gpu-sv**, single precision unless marked:

| Circuit                            | 30 qubits | 31 qubits | 32 qubits | 33 qubits |
| :--------------------------------- | --------: | --------: | --------: | --------: |
| GHZ, fan-out                       |     1.1 s |     1.2 s |     1.3 s |     1.6 s |
| QFT and inverse                    |     1.4 s |     1.7 s |     2.2 s |     3.3 s |
| Random brickwork, depth 10         |     1.3 s |     1.5 s |     1.9 s |     2.8 s |
| Random brickwork, depth 50         |     1.9 s |     2.8 s |     4.5 s |     7.9 s |
| Mirror brickwork, depth 50         |     2.7 s |     4.3 s |     7.6 s |    14.3 s |
| Random brickwork, depth 50, double |     2.1 s |     3.1 s |     5.3 s |         — |

In the same measurements, every gpu-sv job up to 28 qubits, in either precision and for every
circuit above, recorded under 1.6 s, so it would be charged the 3-second minimum.

Past 33 qubits in single precision, or 32 in double, part of the state vector is in host memory,
and each added qubit costs more than double. Measured at simulator version 0.4.0 on the same GPU,
with 1,000 shots:

| Circuit                    | 34 qubits, single | 35 qubits, single | 33 qubits, double | 34 qubits, double |
| :------------------------- | ----------------: | ----------------: | ----------------: | ----------------: |
| GHZ, fan-out               |             4.8 s |            10.6 s |             4.7 s |            10.5 s |
| QFT and inverse            |            10.8 s |            23.7 s |             9.5 s |            21.1 s |
| Random brickwork, depth 10 |             7.4 s |            15.9 s |             6.2 s |            13.7 s |
| Random brickwork, depth 50 |            19.0 s |            42.2 s |            13.4 s |            28.4 s |
| Mirror brickwork, depth 50 |            34.9 s |            74.6 s |            22.0 s |            46.5 s |

**gpu-tn** with `mps` and the default settings:

| Circuit                    | 64 qubits | 128 qubits | 256 qubits | 500 qubits |
| :------------------------- | --------: | ---------: | ---------: | ---------: |
| GHZ, fan-out               |     3.1 s |      7.9 s |     26.8 s |     97.3 s |
| Mirror brickwork, depth 10 |     2.7 s |      4.0 s |      6.6 s |     11.5 s |
| Random brickwork, depth 10 |     2.2 s |      3.0 s |      4.4 s |      7.3 s |
| Random brickwork, depth 50 |    10.8 s |     21.8 s |     43.9 s |     85.6 s |

The QFT and inverse, with its long-range gates, took 10.6 s at 32 qubits, 74.9 s at 64, and
281.7 s at 100.

**gpu-tn** with `method: "exact"`:

| Circuit                    | 8 qubits | 16 qubits | 24 qubits |                     32 qubits |
| :------------------------- | -------: | --------: | --------: | ----------------------------: |
| GHZ, fan-out               |    2.5 s |     2.6 s |     2.7 s |                         3.5 s |
| Mirror brickwork, depth 10 |    3.0 s |     3.4 s |     5.2 s |                         197 s |
| QFT and inverse            |    8.4 s |    21.8 s |    24.7 s | stopped at 10 minutes, 0 credits |

<Tip>
  **On gpu-tn, gate locality matters more than width.** MPS applies a two-qubit gate between
  distant qubits through a chain of swaps. The same 500-qubit GHZ state took about 3 s as a
  nearest-neighbor chain and about 97 s as a fan-out from qubit 0. Lay out circuits so that
  qubits that interact are adjacent. Sampling cost also grows with shots × width, so wide
  circuits stay slow even when they are easy to represent.
</Tip>

## Troubleshooting

A job that fails reports the reason as its status message: `job.status().status_message`.

| Symptom                                                                                                                  | Cause                                                                                                                                            |
| :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `Unknown option '<name>'`, for example `Unknown option 'max_bond_dim'`                        | The simulator has no option by that name. Check the spelling against [Runtime options](#runtime-options).     |
| `Invalid option '<name>': …`, for example `Invalid option 'maxBondDim': must be less than or equal to 1024`              | The value is out of range or the wrong type. The message says what it must be.                                                                   |
| `Number of qubits in the circuit (36) exceeds the device's capacity (35).`                                               | The SDK refuses the job before it is submitted: gpu-sv's limit is 35 qubits.                                                                     |
| `… Circuit has 35 qubits, exceeding the maximum of 34 that this environment's GPU nodes simulate at this precision. Use fewer qubits.` | Double precision tops out at 34 qubits on gpu-sv. Use `"single"`, the default, which reaches 35. The job is not charged.          |
| `Not enough free GPU memory: a …-qubit …-precision state vector needs … MiB, but … MiB is free. Retry later, or use fewer qubits.` | gpu-sv checks free GPU memory before it allocates the state vector. Retry later, or use fewer qubits.                      |
| `Not enough free host memory on this node: a 35-qubit single-precision state vector extends beyond the GPU only while the node has 291272 MiB of memory available, and it has … MiB. …` | Past 33 qubits single (32 double), part of the state vector goes in host memory, and the node has too little free right now. Retry later, or use fewer qubits. |
| `Circuit has 501 qubits, exceeding the maximum of 500 for tensor network simulation`                                     | gpu-tn's hard limit is 500 qubits.                                                                                                               |
| gpu-tn counts don't match the exact distribution                                                                         | MPS is approximate once a bond exceeds `maxBondDim`. See [Choosing maxBondDim and the cutoffs](#choosing-maxbonddim-and-the-cutoffs).            |
| `Exact tensor-network contraction of this circuit is estimated at …`                                                     | The `exact` estimate refused the circuit. Use `mps` or a smaller circuit.                                                                        |
| `… exceeded 10 minutes and was stopped.`                                                                                 | gpu-tn's 10-minute limit. The job is not charged. See [Timeouts](#timeouts).                                                                     |
| `Method 'mps' runs gates with at most 6 control qubits …`                                                                | Use `method: "exact"` for gates with more than 6 controls.                                                                                       |
| `Unsupported OpenQASM feature: …`                                                                                        | The circuit uses a feature these simulators refuse. See [What a circuit may contain](#what-a-circuit-may-contain).                               |
| `Daily free allowance for … reached`                                                                                     | You have used today's free circuits on that simulator. Wait for 00:00 UTC, or turn on [usage-based billing](https://docs.qbraid.com/v2/account/usage#simulator-usage).   |

## Related links

- [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installation, authentication, device discovery
- [Pricing](https://docs.qbraid.com/v2/home/pricing#quantum-circuit-simulators): simulator allowances and credits
- [Usage](https://docs.qbraid.com/v2/account/usage#simulator-usage): your daily simulator usage and the usage-based billing switch
- [Quantum jobs](https://docs.qbraid.com/v2/lab/user-guide/quantum-jobs): tracking submissions in qBraid Lab
