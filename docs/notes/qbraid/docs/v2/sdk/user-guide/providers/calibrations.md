> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9aa14c9c0a4bdffc4589c81db185acaeb02bbf0365a4ab850bbd18551aafeb6d.

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

# Device calibrations and connectivity

> Fetch live coupling maps and calibration data for QPUs on qBraid, plot connectivity graphs, and use the data to place circuits on the best-calibrated qubits before submitting.

<Info>
  Calibration data is refreshed from each hardware provider roughly hourly.
</Info>

Superconducting QPUs are not uniform: qubits differ in readout fidelity, and
two-qubit gates only exist between physically coupled pairs, each with its own
error rate. The [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started) exposes
both facts programmatically, so you can inspect a device before you submit to
it, and place your circuit on the qubits where it will perform best.

## Do you need this?

No. Calibration-aware qubit selection is an optimization, not a prerequisite —
you can submit jobs without ever calling `get_calibrations()`. When you submit a
circuit, the provider's compiler already chooses a physical layout for you,
using these same calibration tables to avoid the worst qubits.

Reach for this page when you hit a question the default path does not answer:

- **"Why did my results change since last week?"** Devices drift and are
  recalibrated continuously, so comparing snapshots often explains it.
- **"Which device should I run on?"** Qubit count alone says little; error rates
  and coherence times say more.
- **"Can I beat the default layout?"** For deep circuits, pinning a
  high-fidelity qubit chain can outperform automatic placement.
- **Noise characterization and benchmarking**, where the calibration data is
  itself the object of study.

## Fetching calibration data

Every `QbraidDevice` has two entry points:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("rigetti:rigetti:qpu:cepheus-1-108q")

device.coupling_map
# ((0, 1), (0, 9), (1, 2), (1, 10), (2, 3), ...)  193 physical qubit pairs

calibration = device.get_calibrations()
calibration.last_calibrated
# '2026-07-21T20:05:45+00:00'
```

`coupling_map` is the device's physical connectivity: sorted, deduplicated
`(source, target)` qubit pairs, derived from the calibrated two-qubit gate
edges. It is cached on the device instance, since hardware topology does not
change between calibrations.

`get_calibrations()` returns the full live snapshot and always fetches fresh
data. The two most useful fields:

```python
# Per-edge two-qubit gate error, keyed by gate name
calibration.edges["gateError"]["cz"][0]
# EdgeEntry(source=0, target=1, value=0.0246)

# Per-qubit metrics
calibration.qubits["0"]
# QubitCalibration(readout_error=0.04, gate_error={'rb': 0.0019}, ...)
```

Both return `None` for devices without published calibration data, such as
simulators.

### Devices with calibration data

| Physical device        | Qubits | Edges | Example device IDs                                                     |
| ---------------------- | ------ | ----- | ---------------------------------------------------------------------- |
| Rigetti Cepheus-1-108Q | 107    | 193   | `rigetti:rigetti:qpu:cepheus-1-108q`, `aws:rigetti:qpu:cepheus-1-108q` |
| IQM Garnet             | 20     | 30    | `aws:iqm:qpu:garnet`                                                   |
| IQM Emerald            | 54     | 85    | `aws:iqm:qpu:emerald`                                                  |
| AQT Ibex-Q1            | 12     | 0     | `aws:aqt:qpu:ibex-q1`                                                  |

<Note>
  All device IDs that map to the same physical hardware share one calibration
  snapshot, so `rigetti:rigetti:qpu:cepheus-1-108q` and
  `aws:rigetti:qpu:cepheus-1-108q` return identical data.
</Note>

<Note>
  A device can have calibration data with an empty edge list. AQT's Ibex-Q1 is a
  trapped-ion system with all-to-all connectivity, so there are no discrete
  coupling edges to report: `coupling_map` returns an empty tuple, not `None`.
  For IonQ trapped-ion devices, see `device.profile.characterization` instead.
</Note>

You can also query the underlying REST endpoint directly, which works for any
device ID including those not available for direct submission:

```bash
curl -H "X-API-Key: $QBRAID_API_KEY" \
  https://api.qbraid.com/api/v1/devices/rigetti:rigetti:qpu:cepheus-1-108q/calibrations
```

## Plotting the connectivity graph

The `qbraid.visualization` module renders the graph in one call, colored by
live calibration data. Edges are colored by two-qubit gate error and nodes by
readout error, on a single-hue scale where darker is better, matching the
topology view in qBraid Lab:

```python
from qbraid.visualization import plot_connectivity_graph

plot_connectivity_graph(device)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/cepheus-connectivity.png" width="75%"></img>
</div>

The dotted outline is a qubit in the lattice footprint with no working
couplings. Light qubits and edges are the ones to avoid.

The layout comes from the device document's `topology` config, so square
lattices (Rigetti) and clipped lattices (IQM) both render their true physical
geometry; devices without a lattice config fall back to a force-directed
layout. To build a custom plot, the `lattice_positions` helper maps qubit ids
to grid coordinates from the same config:

```python
from qbraid.visualization import lattice_positions

topology = device.client.get_device(device.id).topology
# {'type': 'square-lattice', 'rows': 12, 'cols': 9}

positions = lattice_positions(topology, range(108))
# {0: (0, 0), 1: (1, 0), ..., 107: (8, -11)}
```

The same call works unchanged on any device with calibration data. IQM's
Garnet renders its clipped diamond lattice:

```python
garnet = provider.get_device("aws:iqm:qpu:garnet")
plot_connectivity_graph(garnet)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/garnet-connectivity.png" width="60%"></img>
</div>

## Choosing the best qubits

With the calibration data in hand, qubit selection becomes a graph problem,
and `best_qubits` solves it in one call:

```python
device.best_qubits(2)
# (81, 82)                -- best-calibrated pair, 2026-07-24 snapshot

device.best_qubits(5)
# (91, 82, 81, 90, 99)    -- connected chain, in path order
```

`best_qubits(n)` fetches a fresh calibration snapshot and returns the
connected chain of `n` physical qubits maximizing estimated fidelity: the
product of `(1 - error)` over each qubit's readout and single-qubit gate
errors and each edge's two-qubit gate error. Folding readout in matters:
readout error varies by an order of magnitude across the lattice, and the
edge with the lowest two-qubit error regularly sits on a qubit that reads out
poorly. See [Scoring
edges](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti#scoring-edges) for a
hardware-verified example where the two rankings disagree.

A few variations:

```python
device.best_qubits(2, gate="cz")   # restrict edge errors to one gate
device.best_qubits(1)              # best single qubit (e.g. for a T1 sweep)
```

By default each edge uses its best calibrated two-qubit gate; naming a gate
with no calibrated edges raises `ValueError` and lists the ones available.
Devices with qubit metrics but no coupling edges (all-to-all connectivity, such
as AQT's Ibex-Q1) return the `n` individually best qubits. Devices without
calibration data return `None`. Asking for a longer connected chain than the
coupling graph contains raises `ValueError`, as does asking an all-to-all device
for more qubits than it has calibrated, or calling `best_qubits` on an analog
device, which has no fixed qubit lattice to choose from.

Metrics a device does not publish are skipped rather than penalized, so a qubit
is never scored down for data its provider withholds. Ibex-Q1 publishes no
readout error at all, for instance, so its ranking rests on single-qubit gate
error alone.

The chain search is exhaustive, and its cost climbs steeply once `n` approaches
device scale: on Cepheus-1-108Q (107 qubits, 193 edges) `best_qubits(20)`
returns in about a second and `best_qubits(24)` in under ten, while
`best_qubits(30)` does not finish in a minute. Practical circuit widths are
well inside that; whole-device chains are not what this is for.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/cepheus-best-chain.png" width="75%"></img>
</div>

<Tip>
  Calibrations shift with every refresh, and the selection moves with them: the
  chain highlighted above was the best on an earlier snapshot than the one
  quoted in the code. Re-run `best_qubits` shortly before you submit.
</Tip>

## Running on the qubits you chose

### Rigetti direct: hand-placed native gates

On the [Rigetti direct path](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti),
programs that bypass quilc must already use
[native gates](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti#native-gates) on
physical qubits, which is exactly what the coupling map enables. A Bell pair
on the best-calibrated edge:

```python
import pyquil

q0, q1 = device.best_qubits(2)  # the run below used (88, 89)

program = pyquil.Program(f"""
DECLARE ro BIT[2]
RX(pi/2) {q0}
RX(pi/2) {q1}
CZ {q0} {q1}
RX(-pi/2) {q1}
MEASURE {q0} ro[0]
MEASURE {q1} ro[1]
""")

job = device.run(program, shots=100)
job.wait_for_final_state()
job.result().data.get_counts()
# {'00': 44, '11': 44, '01': 7, '10': 5}  -- run on Cepheus-1-108Q, 2026-07-21
```

The correlated outcomes (`00` and `11`) came back at 88 percent on hardware,
consistent with the roughly 0.4 percent CZ error and few-percent readout error
of the chosen pair.

<Note>
  This program contains no timing instruction, so it takes the **compiled**
  path. The placement survives because its qubits already fit the topology,
  which makes quilc default to identity (`NAIVE`) rewiring; quilc is not
  obligated to keep it in general. To make placement a guarantee rather than a
  default, add a clock-aligned delay to take the direct path, or pin the
  compiled path with `PRAGMA INITIAL_REWIRING "NAIVE"`. See [Pinning the
  circuit](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti#pinning-the-circuit).
</Note>

### Qiskit: constrain transpilation to the real topology

If you would rather let a transpiler do the routing, feed the coupling map to
Qiskit and pin your circuit to the chain you selected. This works for any
gate-model device on qBraid:

```python
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

ghz = QuantumCircuit(5, 5)
ghz.h(0)
for i in range(4):
    ghz.cx(i, i + 1)
ghz.measure(range(5), range(5))

coupling = CouplingMap(
    [list(edge) for edge in garnet.coupling_map]
    + [[b, a] for a, b in garnet.coupling_map]
)
chain = list(garnet.best_qubits(5))  # [2, 7, 8, 13, 17] on Garnet, 2026-07-24

transpiled = transpile(
    ghz,
    coupling_map=coupling,
    initial_layout=chain,
    basis_gates=["r", "cz"],
    optimization_level=3,
)

job = garnet.run(transpiled, shots=1000)
```

Every two-qubit gate in the transpiled circuit now acts on a physically
coupled, well-calibrated pair, and no SWAP overhead is silently inserted for
qubits you did not choose.

<Warning>
  Transpile against the coupling map of the exact device ID you will submit to.
  Vendor-routed and direct device IDs share hardware and calibrations, but a
  circuit laid out for one device will not fit another.
</Warning>

## Related links

- [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): setup and credentials
- [Rigetti Cepheus-1-108Q](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti): native
  gates, Quil-T timing, and the two compilation paths
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization): histograms and other
  built-in plotting utilities
