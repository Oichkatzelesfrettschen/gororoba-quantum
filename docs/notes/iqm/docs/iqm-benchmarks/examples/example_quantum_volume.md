> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_quantum_volume.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_quantum_volume.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 070f73cb3f5ab45eaf17db8b127a790657d616230fbadec26b8fe2c54d7e9187.

# Quantum Volume (QV)

```
%load_ext autoreload
%autoreload 2
```

## Set IQM Token if using Resonance

```
import os
from iqm.qiskit_iqm import IQMProvider

token = ""
os.environ["IQM_TOKEN"] = token
quantum_computer = "" # provide actual quantum computer name. i.e. "emerald", "garnet", "sirius"
iqm_server_url = "https://resonance.iqm.tech/" # provide actual IQM server URL
os.environ["IQM_SERVER_URL"] = iqm_server_url

provider = IQMProvider(iqm_server_url, quantum_computer=quantum_computer)
backend = provider.get_backend()
```

## Customizing dynamical decoupling strategy

```
from iqm.iqm_client.models import DDStrategy
from iqm.benchmarks.utils import extract_fidelities_unified
_, calibration_data = extract_fidelities_unified(backend=backend)

# Minimal dynamical decoupling with only two extra single-qubit gates per idle
dd_qubits = ["QB"+str(qubit_name+1) for qubit_name, fidelity in calibration_data["fidelity_1qb_gates_averaged"].items() if fidelity > 0.998]
strategy = DDStrategy(gate_sequences=[(2, 'XX', 'center')], target_qubits = dd_qubits)

print(f"Minimal dynamical decoupling strategy:")
for k, v in strategy.__dict__.items():
    print(f"\t{k}: {v}")
```

## Quantum Volume Configuration

```
from iqm.benchmarks.quantum_volume.quantum_volume import *
```

```
EXAMPLE_QV = QuantumVolumeConfiguration(
    num_circuits=500,
    shots=2**8,
    num_sigmas=2,
    choose_qubits_routine="custom",
    custom_qubits_array=[[0,1,2,3], [0,1,3,4]],
    max_gates_per_batch=10_000,
    rem=True,
    mit_shots=1_000,
    dd_strategy=strategy,
    use_dd=True,
)
```

## Run the experiment

```
benchmark_qv = QuantumVolumeBenchmark(backend, EXAMPLE_QV)
run0_qv = benchmark_qv.run()
```

One can perform a separate run of the benchmark (also possible with a different configuration)

```
#run1_qv = benchmark_qv.run()
```

## Perform Analysis

```
result0_qv = benchmark_qv.analyze()
```

```
#result1_qv = benchmark.analyze(run_index=0)
```

List all the keys in the attributes of the dataset

```
attr_keys = sorted([str(x) for x in list(result0_qv.dataset.attrs.keys())])
for k in attr_keys:
    print(k)
```

The data for specific experiments is indexed by 0,1,…, e.g., for the first experiment:

```
for k in result0_qv.dataset.attrs[0].keys():
    print(k)
```

```
result0_qv.dataset.attrs[0]["heavy_output_probabilities"]
```

The observation object contains the benchmark results

```
result0_qv.observations
```

## Generate plots

```
for k in result0_qv.plots.keys():
    print(k)
```

Print a specific output

```
# result0_qv.plots["vanilla_4_qubits_[0, 1, 3, 4]"]
```

Or print all the plots at once

```
result0_qv.plot_all()
```
