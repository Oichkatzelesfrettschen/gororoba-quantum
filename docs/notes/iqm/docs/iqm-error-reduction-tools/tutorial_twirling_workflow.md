> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/tutorial_twirling_workflow.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/tutorial_twirling_workflow.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcf8283c550cdcb003bcadcf6f280a84cbe66450e6907d3a97badf1e862f49c8.

# Tutorial: Circuit Twirling API

This tutorial walks through **circuit twirling** — a noise-tailoring technique that converts coherent gate errors and correlated readout errors into more benign stochastic noise.

The `CircuitTwirler` API covers two techniques, which can be compsed with each other.

| Technique | What it does | Controlled by |
|----|----|----|
| **Gate twirling** (PMPT) | Add generalized bitflips to existing single-qubit gates within the circuit, turning a large fraction of coherent errors into more benign stochastic noise. | `circuit_twirling=True` |
| **Readout twirling** | Applies random X-flips before measurement (with classical correction), de-correlating measurement errors | `readout_twirl_strategy` |

The `CircuitTwirler` API can be used standalone (as shown in Section 2) or together with Readout Error Mitigation within the `REMWorkflow` API (shown in Section 3 and in the dedicated tutorial).

## 0. Imports

```
import os

from matplotlib import pyplot as plt

import numpy as np

from pprint import pformat

from qiskit import QuantumCircuit, transpile

# IQM backend access
from iqm.qiskit_iqm import IQMProvider

# Low-level twirling API
from iqm.error_reduction_tools.twirling.twirling_api import CircuitTwirler, TwirlingConfiguration

# High-level REM workflow (for composition examples)
from iqm.error_reduction_tools.rem import REMWorkflow, WorkflowConfiguration

from iqm.error_reduction_tools.utils.general_utils import total_variational_distance
```

## 1. Backend and target circuit

Connect to the IQM backend, then build a 4-qubit **GHZ circuit** whose ideal distribution is just two equally-weighted bitstrings (`0000` and `1111`).

Use you own credentials to get access to the quantum computer of choice.

```
server_url = "https://resonance.iqm.tech"
quantum_computer = "emerald"
os.environ["IQM_TOKEN"]  = os.getenv("IQM_RESONANCE")

provider = IQMProvider(url=server_url, quantum_computer=quantum_computer)
backend = provider.get_backend()
iqm_client = backend.client
```

### Build the GHZ circuit

\$\$\|\mathrm{GHZ}\rangle = \frac{1}{\sqrt{2}}\bigl(\|0000\rangle + \|1111\rangle\bigr)\$\$

The ideal distribution has exactly two equally-weighted bitstrings (`0000` and `1111`), making any deviation immediately visible.

```
NUM_QUBITS = 4
SHOTS      = 20_000
SEED       = 44

# Build GHZ circuit
qc = QuantumCircuit(NUM_QUBITS)
qc.h(0)
for q in range(NUM_QUBITS - 1):
    qc.cx(q, q + 1)
qc.measure_all()

exact_counts = {
    "0" * NUM_QUBITS: 0.5,
    "1" * NUM_QUBITS: 0.5,
}

transpiled_circ = transpile(qc, backend=backend, initial_layout=list(range(1, NUM_QUBITS + 1)))

print("Ideal GHZ distribution:")
for bs, p in exact_counts.items():
    print(f"  |{bs}⟩: {p:.2f}")

transpiled_circ.draw("mpl", fold=0, idle_wires=False)
```

We can execute the circuit. This will serve us as a reference.

```
raw_job    = backend.run(transpiled_circ, shots=SHOTS)
raw_counts = raw_job.result().get_counts()

print("Baseline — raw probabilities (top 5):")
for bs, p in sorted(raw_counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {bs}: {p:.4f}")
```

## 2. Twirling circuits

### 2.1 Exploring twirling strategies: the `TwirlingConfiguration` class

`TwirlingConfiguration` is a dataclass that governs every aspect of the twirling behaviour.

| Parameter | Type | Default | Description |
|----|----|----|----|
| `circuit_twirling` | `bool` | `True` | Apply **gate-level twirling** |
| `readout_twirl_strategy` | `"LOCAL"` \| `"MINIMAL"` \| `"HADAMARD"` \| `NONE` | `"LOCAL"` | **Readout-twirling** strategy |
| `num_twirling_instances` | `int` | `40` | (Max) total randomized variants per circuit |
| `seed` | `int | None` | `None` | RNG seed for reproducibility |

#### Readout twirling strategies

- **`'NONE'`** — disable readout twirling; only gate twirling applies (if enabled).

- **`"LOCAL"`** — (Default) symmetric I/X patterns for neighboring qubit pairs; exploits QPU connectivity. Requires the backend topology (minimum 4 circuits).

- **`"MINIMAL"`** — all qubits assigned complementary I/X patterns; minimum overhead (2 circuits).

- **`"HADAMARD"`** — Full pairwise de-correlation (up to 2n circuit for n qubits).

#### Three examples

Let’s consider three twirling strategies

| Configuration                   | Circuit twirling | Readout twirling |
|---------------------------------|------------------|------------------|
| A. Only circuit twirling        |                | `NONE`           |
| B. Only reaodut twirling        |                | `LOCAL`          |
| C. Circuit and readout twirling |                | `LOCAL`          |

```
twirling_configs = {}

twirling_configs["A"] = TwirlingConfiguration(
    readout_twirl_strategy='NONE',   # no readout twirling
    circuit_twirling=True,         # gate-level Pauli twirling
    num_twirling_instances=40,     # default value is 40
    seed=SEED,
)

twirling_configs["B"] = TwirlingConfiguration(
    readout_twirl_strategy='LOCAL',   # no readout twirling
    circuit_twirling=False,         # gate-level Pauli twirling
    num_twirling_instances=40,     # default value is 40
    seed=SEED,
)

twirling_configs["C"] = TwirlingConfiguration(
    readout_twirl_strategy='LOCAL',   # no readout twirling
    circuit_twirling=True,         # gate-level Pauli twirling
    num_twirling_instances=40,     # default value is 40
    seed=SEED,
)
```

### 2.2 Preparing the circuits: the `CircuitTwirler` class

We are now in a position to prepare the circuits to be executed. Let’s do it in parallel using the three defined strategies.

```
circuit_twirlers = {}
for config in twirling_configs:
    circuit_twirlers[config] = CircuitTwirler(iqm_client, config=twirling_configs[config])
    circuit_twirlers[config] = circuit_twirlers[config].twirl([transpiled_circ])
```

Note that for config “B”, when only readout twirling is used according to the `LOCAL` strategy, only `4` different circuits have been created (instead of the `40` created when also circuit twirling is requested).

We can quickly inspect the created circuits, to see how they differ from each other. To this end, we’ll use thwo methods:

- `get_twirled_circuits` returns a list of the twirled IQM Pulse circuits.

```
for config in twirling_configs:
    circuits = circuit_twirlers[config].get_twirled_circuits()[0]
    n = len(circuits)
    print(f"Configuration {config}  ({n} circuit{'s' if n != 1 else ''})  —  first 2 instructions per circuit:")
    print("  " + "=" * 52)
    for j in range(2):
        instrs = circuits[j].instructions[:2]
        formatted = pformat(instrs, width=60).replace('\n', '\n  │  ')
        print(f"  circuit {j + 1:>2d} │  {formatted}")
        if j < 1:
            print("  " + "-" * 52)
    print("  " + "=" * 52 + "\n")
```

- `get_rot_strings` shows the “readout twirling” strings associated with each circuit. They indicate whether a bit has been flipped (`X`) or not (`I`) by the readout twirling. Note that strategy “A” has no readout twirling, so not bit have been flipped.

```
for config in twirling_configs:
    rot_strings = circuit_twirlers[config].get_rot_strings()[0]
    n = len(rot_strings)
    print(f"Configuration {config}  ({n} circuit{'s' if n != 1 else ''})  —  rot_strings:")
    print("  " + "-" * 36)
    for j, rs in enumerate(rot_strings[:4]):
        print(f"  circuit {j + 1:>2d} │ {rs}")
    if n > 4:
        print(f"  {'...':>10}   ({n - 4} more)")
    print("  " + "-" * 36 + "\n")
```

### 2.3 Running the circuits and retrieving the results

We can run the circuits asynchronously

```
# Submitting the jobs
for config in twirling_configs:
    circuit_twirlers[config].submit(shots=SHOTS)
```

```
# Retrieving the results
exp_counts = {}
for config in twirling_configs:
    exp_counts[config] = circuit_twirlers[config].retrieve_counts()[0]
```

### 2.4 Looking at the results

We plot the counts of the two target bitstrings `0000` and `1111` across configurations. The raw data typically shows more `0000` counts than `1111`. Both gate twirling and readout twirling help reduce this imbalance, with the combined strategy (C) generally performing best.

```
import numpy as np

cases = {"Raw": raw_counts, "A. Circuit\n twirling": exp_counts["A"], "B. Readout\n twirling": exp_counts["B"], "C. Circuit + readout\ntwirling": exp_counts["C"]}
bs_0, bs_1 = "0" * NUM_QUBITS, "1" * NUM_QUBITS

x = np.arange(len(cases))
w = 0.35

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(x - w/2, [c.get(bs_0, 0) for c in cases.values()], w, label=f"|{bs_0}>", color="tab:blue", edgecolor="black", lw=0.7)
ax.bar(x + w/2, [c.get(bs_1, 0) for c in cases.values()], w, label=f"|{bs_1}>", color="tab:orange", edgecolor="black", lw=0.7)
ax.set(xticks=x, ylabel="Counts", title="Most probable bistrings per configuration")
ax.set_xticklabels(cases.keys())
ax.legend(loc="lower left")
plt.tight_layout()
```

## 3. Composing twirling with REM, using `REMWorkflow`

`REMWorkflow` wraps `CircuitTwirler` and adds a full **Readout Error Mitigation** pipeline (see the dedicated tutorial for more details). It consists of:

1.  **Characterization** of readout errors (handled by `ReadoutErrorCharacterization`)

2.  **Twirled execution** of the desired circuit(s) (handled by `CircuitTwirler`)

3.  **Postprocessing** counts are untwirled and REM is performed (handled by `ReadoutErrorMitigation`).

`TwirlingConfiguration` is passed directly to `WorkflowConfiguration`, so every combination explored above also works inside `REMWorkflow`.

```
workflow_configurations = {}
workflow_configurations["REM"] = WorkflowConfiguration(
    shots=SHOTS,
    twirling=TwirlingConfiguration(readout_twirl_strategy="NONE", circuit_twirling=False),
)
for config in twirling_configs:
    workflow_configurations[config] = WorkflowConfiguration(
        shots=SHOTS,
        twirling=twirling_configs[config]
)
```

This high-level API performs everything in one go. For asynchronous execution, see the dedicated tutorial. Note that readout characterization is executed only within the first iteration of the loop. The obtained `ReadoutErrorCharacterization` object is then passed directly to the remaining `REMWorkflow` objects, so it can be reused without extra calibration shots.

```
workflows = {}
rem_results = {}
characterization = None

# Circuit submission
for j, config in enumerate(workflow_configurations):
    workflows[config] = REMWorkflow(iqm_client, config = workflow_configurations[config], characterization = characterization)
    results = workflows[config].run([transpiled_circ])
    rem_results[config] = results.mitigated_distributions[0]
    characterization = workflows[config].get_characterization()
```

Finally, we can plot again the mitigated probabilities associated with the two most probable bistrings, for each run.

```
cases = {"REM": rem_results["REM"], "Circuit\ntwirling  + REM": rem_results["A"], "Readout\ntwirling + REM": rem_results["B"], "Circuit + readout\ntwirling + REM": rem_results["C"]}
bs_0, bs_1 = "0" * NUM_QUBITS, "1" * NUM_QUBITS

x = np.arange(len(cases))
w = 0.35

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(x - w/2, [c.get(bs_0, 0) for c in cases.values()], w, label=f"|{bs_0}>", color="tab:green", edgecolor="black", lw=0.7)
ax.bar(x + w/2, [c.get(bs_1, 0) for c in cases.values()], w, label=f"|{bs_1}>", color="tab:red", edgecolor="black", lw=0.7)
ax.set(xticks=x, ylabel="Counts", title="Most probable bistrings per configuration")
ax.set_xticklabels(cases.keys())
ax.legend(loc="lower left")
plt.tight_layout()
```
