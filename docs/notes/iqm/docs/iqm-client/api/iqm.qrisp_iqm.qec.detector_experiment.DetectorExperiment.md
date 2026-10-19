> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 570486ddeb276a873722dc6b503f17d1d3544e3f513bf0ef93bb19ca18afaa7c.

# DetectorExperiment

Module: [`iqm.qrisp_iqm.qec.detector_experiment`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.html#module-iqm.qrisp_iqm.qec.detector_experiment "iqm.qrisp_iqm.qec.detector_experiment")

*class* iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment(*func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[...\], [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Decorator that turns a Jasp function into a detector-experiment handle.

**What problem does this class solve?**

A quantum error correction experiment involves many moving parts: you define a syndrome-extraction circuit with noise annotations via `stim_noise()`, return detector and observable parity checks via `parity()`, then you must trace the circuit, extract a detector error model (DEM), sample the circuit, feed detection events and the DEM into a decoder (PyMatching), compare predictions against observed logical values, and tally the logical error rate (LER). Doing this by hand for every experiment — especially when sweeping parameters or switching between Stim and hardware backends — is tedious and error-prone.

`DetectorExperiment` automates this entire pipeline. Decorate your Jasp-traceable experiment function with `@DetectorExperiment`, and the class gives you:

- **One-shot LER**: [`compute_LER()`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.compute_LER "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.compute_LER") traces the function, builds the DEM from your `stim_noise` annotations, samples the circuit (via Stim’s built-in sampler or any hardware backend), decodes with PyMatching, and returns the logical error rate — all in a single call.

- **Batched sweeps**: [`batched_compute_LER()`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.batched_compute_LER "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.batched_compute_LER") submits multiple parameter sets (e.g. a delay sweep) as a single hardware batch, eliminating per-job queue overhead.

- **Circuit inspection**: [`to_stim()`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_stim "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_stim") and [`to_iqm()`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_iqm "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_iqm") let you extract and visualize the underlying Stim or IQM Pulse circuit before running on hardware, so you can verify detector / observable placement and gate decompositions at a glance.

**How it works**

When you call any of the public methods, the class internally:

1.  **Traces** your function via Jasp to obtain a quantum circuit with explicit detector and observable annotations.

2.  **Extracts** the Stim circuit (including the DEM built from your `stim_noise` calls) and, for hardware backends, a Qrisp circuit plus a post-processing function.

3.  **Samples** the circuit — either via Stim’s fast built-in sampler (when no backend is given) or via the provided hardware / simulator backend.

4.  **Decodes** the detection events with PyMatching’s minimum-weight perfect matching, using the DEM that was automatically constructed from your noise annotations.

5.  **Compares** the decoder’s predictions against the observed logical values (your `observable=True` parities) and returns the fraction of shots where they disagree — the logical error rate.

Because the DEM is derived directly from the `stim_noise` calls in your function, you never need to manually construct or synchronise error models. The same function works with Stim (for fast, noise-model-based simulation) and with real hardware (where physical noise replaces the annotated model).

Parameters:  
**func** (*callable*) – A Jasp-traceable function that implements the detector experiment. Must return `(list[Detector], list[Observable])` — each detector and observable being the result of a `parity()` call.

Examples

A minimal repetition code memory experiment:

```
from qrisp import (
    QuantumArray, QuantumBool,
    x, cx, measure, reset, parity,
)
from qrisp.misc.stim_tools import stim_noise
from iqm.qrisp_iqm.qec import DetectorExperiment

p = 0.01  # physical error strength

@DetectorExperiment
def rep_code(delay_time=0.0):
    # ── Allocate qubits ────────────────────────────────────────────
    qubits  = QuantumArray(shape=(7,), qtype=QuantumBool())
    data    = qubits[::2]      # 4 data qubits
    ancilla = qubits[1::2]     # 3 ancilla qubits

    # ── Prepare logical |1_L⟩ ──────────────────────────────────────
    x(data)

    # ── One syndrome round ─────────────────────────────────────────
    # Reset ancillas (with noise on data that idle during reset)
    reset(ancilla)
    stim_noise("X_ERROR", p, ancilla)
    stim_noise("DEPOLARIZE1", p, data)

    # CNOT layer 1:  data[i] → ancilla[i]
    for i in range(3):
        cx(data[i], ancilla[i])
        stim_noise("DEPOLARIZE2", p, data[i], ancilla[i])

    stim_noise("DEPOLARIZE1", p, data[3])   # untouched

    # CNOT layer 2:  data[i+1] → ancilla[i]
    for i in range(3):
        cx(data[i+1], ancilla[i])
        stim_noise("DEPOLARIZE2", p, data[i+1], ancilla[i])

    stim_noise("DEPOLARIZE1", p, data[0])   # untouched

    # Pre-measurement noise
    stim_noise("X_ERROR", p, ancilla)
    stim_noise("X_ERROR", p, data)

    # Measure ancillas → syndrome detectors
    anc_meas = measure(ancilla)
    # First (and only) round: compare to expected initial |0⟩
    synd_det = parity(anc_meas, expectation=0)

    # ── Final data measurement ─────────────────────────────────────
    data_meas = measure(data)

    # ── Measurement-round detectors ────────────────────────────────
    # Tie each ancilla back to its two neighboring data qubits
    det_0 = parity(data_meas[0], anc_meas[0], data_meas[1], expectation=0)
    det_1 = parity(data_meas[1], anc_meas[1], data_meas[2], expectation=0)
    det_2 = parity(data_meas[2], anc_meas[2], data_meas[3], expectation=0)

    # ── Observable ─────────────────────────────────────────────────
    # Logical |1_L⟩ → every data qubit should read 1
    obs = parity(data_meas[3], observable=True, expectation=1)

    return [synd_det, det_0, det_1, det_2], [obs]
```

Once decorated, use the provided methods to analyze the experiment:

```
# Compute logical error rate with Stim (fast simulation)
ler = rep_code.compute_LER(0.0, shots=10_000)
print(f"Logical error rate: {ler:.4f}")

# Extract the Stim circuit for visualization
stim_circuit = rep_code.to_stim(0.0)
print(stim_circuit)

# Run on hardware with an IQM backend
from iqm.qrisp_iqm import IQMBackend, vf2pp_layout
from qrisp import PassManager, convert_to_cz, convert_to_prx

backend = IQMBackend(
    device_instance="emerald",
    api_token="YOUR_TOKEN",
    server_url="https://resonance.iqm.tech/",
    pass_manager=PassManager(),
)
backend.pm += vf2pp_layout(backend.connectivity)
backend.pm += convert_to_cz()
backend.pm += convert_to_prx

ler_hw = rep_code.compute_LER(0.0, shots=10_000, backend=backend)
print(f"Hardware LER: {ler_hw:.4f}")
```

Methods

|  |  |
|----|----|
| [`batched_compute_LER`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.batched_compute_LER "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.batched_compute_LER") | Compute the logical error rate for multiple parameter sets in a single backend batch. |
| [`compute_LER`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.compute_LER "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.compute_LER") | Compute the logical error rate for the detector experiment. |
| [`to_iqm`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_iqm "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_iqm") | Extract the IQM circuit for the detector experiment. |
| [`to_qc`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_qc "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_qc") | Extract the Qrisp QuantumCircuit for the detector experiment. |
| [`to_stim`](#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_stim "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.to_stim") | Extract the Stim circuit for the detector experiment. |

compute_LER(*\*args: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10000*, *backend: Backend \| [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute the logical error rate for the detector experiment.

Parameters:  
- **\*args** – Forwarded to the decorated Jasp function.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of samples / shots.

- **backend** (*callable* *or* [*object*](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")*,* *optional*) – Backend to use for sampling. Can be either: - A callable with signature `(qc: QuantumCircuit, shots: int) -> dict[str, int]` - An object with a `run_func` attribute containing such a callable If *None*, Stim’s built-in detector sampler is used directly.

Returns:  
Logical error rate (`num_errors / shots`).

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

batched_compute_LER(*args_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), ...\]\]*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10000*, *backend: Backend \| [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Compute the logical error rate for multiple parameter sets in a single backend batch.

All tracing-based operations (`make_jaspr`, `Jaspr.to_qc`, `extract_post_processing`, `extract_stim`) are performed **sequentially on the calling thread** before any circuits are submitted, because these operations are **not thread-safe**.

When *backend* is a `Backend` (e.g. `IQMBackend`), all circuits are submitted in a single call to `backend.batch_run_func`, eliminating the per-circuit overhead. For a plain callable backend the circuits are executed one-by-one as a fallback.

Parameters:  
- **args_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\]*) – Each element is a tuple of arguments forwarded to the decorated Jasp function. For experiments that take no arguments use `[()]` or `[()] * n`.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of samples per experiment.

- **backend** (*Backend* *or* *callable,* *optional*) –

  - A `Backend` — circuits are submitted as a single batch via `batch_run_func`.

  - A plain callable `(qc, shots) -> dict[str, int]` — circuits are executed sequentially (no batching benefit, but API-compatible).

  - *None* — Stim’s built-in detector sampler is used (no hardware backend, each experiment is sampled independently).

Returns:  
A list of logical error rates, one per entry in *args_list*.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

to_stim(*\*args: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → Circuit  
Extract the Stim circuit for the detector experiment.

Parameters:  
**\*args** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – Forwarded to the decorated Jasp function.

Returns:  
The Stim circuit with detectors and observables.

Return type:  
stim.Circuit

to_qc(*\*args: Any*, *pm: PassManager \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → QuantumCircuit  
Extract the Qrisp QuantumCircuit for the detector experiment.

Parameters:  
- **\*args** – Forwarded to the decorated Jasp function.

- **pm** (*PassManager,* *optional*) – A PassManager to apply transpilation to the circuit. If provided, the circuit will be transpiled before returning.

Returns:  
The Qrisp quantum circuit (transpiled if pm was provided).

Return type:  
qrisp.QuantumCircuit

to_iqm(*\*args: Any*, *topology: Any*, *pm: PassManager \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → Any  
Extract the IQM circuit for the detector experiment.

Parameters:  
- **\*args** – Forwarded to the decorated Jasp function.

- **topology** (*ChipTopology* *or* *DynamicQuantumArchitecture*) – IQM topology object. Can be obtained from: - `pulla.get_chip_topology()` (IQM Pulse) - `iqm_client.get_dynamic_quantum_architecture()` (IQM Client)

- **pm** (*PassManager,* *optional*) – A PassManager to apply transpilation before converting to IQM format. The circuit must be transpiled to native gates (CZ, U3) before conversion. If not provided, the circuit will be converted as-is (and may fail if it contains non-native gates).

Returns:  
The IQM circuit object ready for compilation.

Return type:  
iqm.pulse.Circuit

Notes

You should provide a PassManager to transpile to native gates:

```
from qrisp import PassManager, convert_to_cz
from iqm.qrisp_iqm import plasma_layout, route
from iqm.qrisp_iqm.iqm import get_coupling_map

connectivity = get_coupling_map(topology)
pm = PassManager()
pm.add_pass(plasma_layout(connectivity=connectivity))
pm.add_pass(route(connectivity=connectivity))
pm.add_pass(convert_to_cz())

iqm_circuit = experiment.to_iqm(args, topology=topology, pm=pm)
```

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-c6804b2ceffb9e900f3460f36a3c9f45a1aa8fa2.png)
