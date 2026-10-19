> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_graphstate.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_graphstate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d0796f96f34102bc864b264bfdbb6d18df09a1cfccd38682620b3bcc6c467d46.

# Graph State Bipartite Entanglement

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

```
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300
```

## Graph State Configuration

```
from iqm.benchmarks.entanglement.graph_states import *
```

```
EXAMPLE_GRAPHSTATE = GraphStateConfiguration(
    qubits=list(range(backend.num_qubits)),
    shots=2**12,
    tomography=TomographyType.STATE,
    num_bootstraps = 150,
    max_circuits_per_batch=100,
    # n_random_unitaries=25,
    # n_median_of_means=4,
)
```

## Run the experiment

```
benchmark_graphstate = GraphStateBenchmark(backend, EXAMPLE_GRAPHSTATE)
#run_graphstate = benchmark_graphstate.run()
```

## Perform Analysis

```
result_graphstate = benchmark_graphstate.analyze()
```

### Display the maximum negativity for all qubit pairs

The negativity is shown as a percentage of the ideal maximum value of 0.5 (which would be achieved on a noiseless backend).

```
for idx, o in enumerate(result_graphstate.observations):
    if idx == 0:
        print(f"Observations: {o.name}\n****************************\n")
    print(f"{o.identifier.qubit_indices}: {100.0*(o.value/0.5):.2f} +/- {100.0*(o.uncertainty/0.5):.2f} %")
```

### Inspect the available plots

```
result_graphstate.plots.keys()
```

```
result_graphstate.plots['max_negativities_IQM_Backend_20250325-160833']
```

**Plot the lowest and highest negativity resconstructed density matrices**

```
observation_dict = {obs.identifier.qubit_indices: obs.value for obs in result_graphstate.observations}
sorted_indices = np.argsort(list(observation_dict.values()))
lowest_negativity_pair = list(observation_dict.keys())[sorted_indices[0]]
highest_negativity_pair = list(observation_dict.keys())[sorted_indices[-1]]
```

```
result_graphstate.plots[f"{lowest_negativity_pair}"]
```

```
result_graphstate.plots[f"{highest_negativity_pair}"]
```

**Display max negativities in the backend graph**

```
result_graphstate.plots['max_negativities_graph_20250325-160833']
```

### Display all available dataset attributes

```
result_graphstate.dataset.attrs.keys()
```

### If using state tomography: inspect the bootstrap bias (difference between each bootstrap mean and the measured sample)

```
for qubits, x in result_graphstate.dataset.attrs['max_negativities'].items():
    print(f"{qubits} bootstrap bias: {np.abs(x['value'] - x['bootstrapped_average']):.2e}")
    print(f"\t (sample) {x['value']} | (adjusted) {(2*x['value'] - x['bootstrapped_average'])}")
```

**All the qubit pair groups generated during execution**

```
result_graphstate.dataset.attrs["all_neighbor_groups"]
```

### Inspect a graph state for some particular Pauli measurement

```
benchmark_graphstate.circuits.benchmark_circuits[0].circuit_groups[0].circuits[7].draw(fold=0,style='iqp')
```
