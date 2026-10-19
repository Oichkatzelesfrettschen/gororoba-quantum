> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_eplg.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_eplg.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eca641a2aa3a074dadbfc79af8ab46f7e5c78f9d8023161ec1c89c00605a4dc6.

# Error Per Layered Gate (EPLG)

```
%load_ext autoreload
%autoreload 2
```

## Set IQM Token if using Resonance.

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

## Randomized Benchmarking Configuration

```
from iqm.benchmarks.randomized_benchmarking.eplg.eplg import *
import numpy as np
```

```
EXAMPLE_EPLG = EPLGConfiguration(
    custom_qubits_array=list(backend.coupling_map),
    drb_depths=sorted(list(set(np.geomspace(1, 200, num=10, endpoint=True, dtype=int).tolist())), reverse=True),
    drb_circuit_samples=25,
    shots=2**8,
    max_circuits_per_batch=100,
    # Parameters for a linear chain layer:
    # chain_length=30,
    # chain_path_samples=200,
    # num_disjoint_layers=4,
    # max_hamiltonian_path_tries=100,
)
```

## Run the experiment

```
benchmark_eplg = EPLGBenchmark(backend, EXAMPLE_EPLG)
run_eplg = benchmark_eplg.run()
```

## Perform the analysis

```
plt.rcParams['figure.dpi'] = 175
```

```
result_eplg = benchmark_eplg.analyze()
```

**Display all the attributes in the dataset**

```
run_eplg.dataset.attrs.keys()
```

## Inspect all the fidelities and the final EPLG

```
for o in result_eplg.observations:
    if o.name != "EPLG":
        print(f"{o.name} {o.identifier.qubit_indices}: {100*o.value:.2f} +/- {100*o.uncertainty:.2f} %")
    else:
        print(f"\n{o.name} {o.identifier.qubit_indices}: {o.value:.2e} +/- {o.uncertainty:.2e}")
```

## Plot a visualization of the selected layers and all the DRB decays

```
result_eplg.plot_all()
```

## Inspect a sample circuit (parallel DRB)

```
eplg_circ_names = benchmark_eplg.circuits.benchmark_circuits[0].group_names
for x in eplg_circ_names:
    print(x)
```

```
circ_group_idx = 6
circ_sample = 6

print(f"Circuit group name: {eplg_circ_names[circ_group_idx]}")

circuit_to_draw = benchmark_eplg.circuits.get_benchmark_circuits_by_name('transpiled_circuits').circuit_groups[circ_group_idx].circuits[circ_sample]

circuit_to_draw.draw(output='mpl', fold=0, idle_wires=False)
```
