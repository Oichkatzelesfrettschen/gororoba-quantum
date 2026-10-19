> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/qubit_selector_example.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/qubit_selector_example.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 527dea6cf434c9465e1bdc55a518800f688eba33bdb9d69715a0c0de83428b83.

# Example: for GHZ state:

We prepare a GHZ state on `nqubits` and execute it with the optimal layout vs a naive layout taken by default.

Note that this example and the framework of `qubit_selector` is based on `qiskit`.

```
import os
from iqm.qubit_selector.qubit_selector import *
from iqm.qubit_selector.qiskit_utils import get_circuit, CircuitType, perform_backend_transpilation
from iqm.qiskit_iqm import IQMProvider
from qiskit.visualization import plot_histogram
```

```
# Input your Resonance token
os.environ["IQM_TOKEN"] = "<your API token>" ## needs to be added as an environment variable!

iqm_server_url = "https://<your-iqm-server-url>"  # Replace with your IQM server URL
quantum_computer = "qc_name"  # Replace with your quantum computer name if needed
provider = IQMProvider(iqm_server_url, quantum_computer = quantum_computer)
backend = provider.get_backend()
```

Note that this is not recommended since this way it is easy to accidentally expose your API token e.g. when giving a presentation or by committing the notebook with the API token to a shared code repository.

## Define the GHZ state and find the optimal layout.

```
nqubits = 6
# Possible choices for pre-defined circuits 'ghz', 'qft', 'random', 'wstate', 'quantum_volume' 'qaoa'
qc_algo = get_circuit(CircuitType.GHZ, nqubits) ## plug in your qiskit quantum circuit of interest

layouts, cost = CostEvaluator(backend=backend, quantum_circuit=qc_algo).get_top_layouts(num_layouts=50)
print("Top 10 qiskit layouts and their costs:")
for layout, c in zip(layouts[:10], cost[:10]):
    print(f"Layout: {layout}, Cost: {c*100:.2f}%")
```

## Execute on a naively chosen layout on the hardware:

```
qc_t = transpile(qc_algo, backend=backend, optimization_level=3)
num_shots = 2000
job = backend.run(qc_t, shots=num_shots).result()
counts_naive = job.get_counts()
plot_histogram(counts_naive)
```

## Execute on an optimal layout found by qubit_selector:

As you see from `counts_qubit_selector`, the GHZ state is better prepared by choosing the optimal layout from qubit-selector.

```
best_layout = layouts[0]
best_layout_qubit_names = [backend.index_to_qubit_name(q) for q in best_layout] ## qubit names corresponding to the best layout

print(f"Best layout qubit names: {best_layout_qubit_names}")

qc_t = perform_backend_transpilation( ## transpile the circuit to the best layout and coupling map
                    [qc_algo],
                    backend,
                    best_layout,
                    backend.coupling_map.reduce(mapping=best_layout),
                    qiskit_optim_level=3,
)

job = backend.run(qc_t, shots=num_shots).result()
counts_qubit_selector = job.get_counts()
plot_histogram(counts_qubit_selector)
```

## Evaluate the Hellinger fidelity:

The performance of qubit-selector is highlighted by achieving a higher GHZ fidelity compared to the naive run.

```
from qiskit.quantum_info import hellinger_fidelity

counts_ideal = {'0'*nqubits: num_shots//2, '1'*nqubits: num_shots//2}
fidelity_naive = hellinger_fidelity(counts_ideal, counts_naive)
fidelity_qubit_selector = hellinger_fidelity(counts_ideal, counts_qubit_selector)

print(f"GHZ Hellinger Fidelity naive: {fidelity_naive:.4f}")
print(f"GHZ Hellinger Fidelity qubit selector: {fidelity_qubit_selector:.4f}")
```
