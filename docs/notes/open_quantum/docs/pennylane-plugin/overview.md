> Full piece: [https://docs.openquantum.com/pennylane-plugin/overview/](https://docs.openquantum.com/pennylane-plugin/overview/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e8cf235ef548a270b0567311ef2251265c8e239099d017dc4d267025d7a5103f.

# PennyLane Plugin Overview

The `openquantum-sdk[pennylane]` plugin connects [PennyLane](https://pennylane.ai/) to the Open Quantum platform, allowing you to run PennyLane quantum circuits on real QPU hardware. It depends on the [Core SDK](https://docs.openquantum.com/core-sdk/overview/) (`openquantum-sdk`) for authentication and job submission.

## Installation

``` bash
pip install "openquantum-sdk[pennylane]"
```

The plugin automatically registers itself with PennyLane via Python entry points. Just `import pennylane as qml` and use `qml.device("openquantum.device", ...)`.

## What the Plugin Does

The plugin registers an `openquantum.device` with PennyLane. When you execute a QNode using this device, the plugin:

1.  **Checks backend status** — when `verbose=True`, reports whether the target QPU is online and its queue depth. If the backend is unavailable, it shows alternatives and asks before continuing (unless `auto_confirm=True`).
2.  **Converts** your PennyLane circuit to an OpenQASM 2.0 program.
3.  **Prepares and quotes** — uploads the QASM, prepares the job, and computes the credit cost.
4.  **Confirms** — prompts for confirmation in terminal sessions (unless `auto_confirm=True`). The cost is printed with that prompt, and also when `verbose=True`. In Jupyter notebooks, execution proceeds immediately.
5.  **Submits** — when `verbose=True`, shows a spinner during execution. While the job is pending, you can interrupt (Ctrl+C / Jupyter stop button) to cancel it on the platform. `job_timeout_seconds` (default one day) bounds the wait.
6.  **Downloads results** — fetches the measurement counts and converts them into the result type you requested (counts, expectation values, probabilities, etc.).
7.  **Tracks spending** — `total_credits_used` accumulates the credits spent. The batch summary is printed when `verbose=True`.

## Quick Example

Run a Bell state circuit on Open Quantum hardware with PennyLane:

``` python
import pennylane as qml

dev = qml.device(
    "openquantum.device",
    wires=2,
    shots=128,
    backend="rigetti:cepheus-1-108q",
    client_id="s_your_client_id",
    client_secret="your_client_secret",
)

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.counts()

result = bell_state()
print(result)
# {'00': 507, '11': 517}
```

Tip

Set `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` as environment variables to avoid passing credentials in code. See the [Authentication](https://docs.openquantum.com/core-sdk/authentication/) guide.

### Key Components

| Component | Description |
|----|----|
| **OpenQuantumDevice** | PennyLane `Device` subclass. Implements `execute()` to run circuits on Open Quantum. |
| **QASM Serializer** | Converts PennyLane tapes to OpenQASM 2.0 strings with proper gate mapping. |
| **API Client** | HTTP client handling upload, preparation, submission, polling, and result download. |
| **Keycloak Auth** | Manages SDK key authentication, JWT token caching, and automatic refresh. |

## Supported Backends

The plugin works with any backend available on the Open Quantum platform. Backends are identified by their `short_code` (e.g., `"rigetti:cepheus-1-108q"`).

| Type | Description | Use Case |
|----|----|----|
| **QPU** | Real quantum hardware (e.g., Rigetti superconducting processors) | Production workloads, hardware noise characterization |

To see all available backends, use the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/), the [Qiskit plugin](https://docs.openquantum.com/qiskit-plugin/backends-targets/), or the [Open Quantum Portal](https://www.openquantum.com). See [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) for details.

## Shot-Based Execution Only

Open Quantum is a shot-based execution platform. Every circuit execution requires a finite number of shots.

``` python
# Correct: specify shots
dev = qml.device("openquantum.device", wires=2, shots=128, backend="rigetti:cepheus-1-108q")

# Incorrect: shots=None is not supported
dev = qml.device("openquantum.device", wires=2, shots=None, backend="rigetti:cepheus-1-108q")
```

Note

Analytic mode (`shots=None`) is not supported. The device will raise an error if you attempt to use it. All measurement results are estimated from finite samples.

## How Measurements Work

The device is counts-based: it runs each circuit with a fixed number of shots and converts the returned bitstring counts into the measurement types you requested.

1.  **Preprocessing**: `preprocess()` builds a PennyLane transform program that validates wires, measurements, and observables, splits non-commuting terms, decomposes unsupported gates, and diagonalizes measurements into the computational basis (`qml.transforms.diagonalize_measurements`).
2.  **Execution**: the plugin serializes the circuit to OpenQASM, submits it, and receives a `{bitstring: count}` histogram from the backend.
3.  **Post-processing**: each measurement's `process_counts(...)` turns the histogram into the requested result (expectation value, variance, probability, or samples).

Because every result is derived from counts, analytic mode (`shots=None`) is not supported.

## Device API

The plugin uses PennyLane's modern `Device` base class (v0.38+) with a TOML capabilities file. This is the current recommended approach, replacing the deprecated `QubitDevice` base class.

For the full list of supported gates, observables, and measurements, see [Supported Operations](https://docs.openquantum.com/pennylane-plugin/supported-operations/).

## Next Steps

- [Device Options](https://docs.openquantum.com/pennylane-plugin/device-options/) -- All configuration parameters.
- [Supported Operations](https://docs.openquantum.com/pennylane-plugin/supported-operations/) -- Gates, observables, and measurements.
- [Basic Circuits](https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/) -- Code examples to get started.
