> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/qubit_selector_quick_start.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/qubit_selector_quick_start.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 09d0bd1e3230f78ab63b659a1ec55f4f79d25bfac9f2961be51324ac7d40f84d.

# Qubit Selector Workflow

`iqm-qubit-selector` is a client package which allows the user to pick optimal layouts for quantum circuits for IQM QPUs of crystal (square grid) topology. This notebook demonstrates the workflow for using `iqm-qubit-selector` to optimize quantum circuit execution on IQM hardware. Note that currently this framework supports `qiskit` circuit type.

**Key steps in the workflow:**

1.  **Setup and Authentication**

    - Import required modules and set up your IQM token and `iqm_server_url`.

2.  **Fetch Calibration Data (Optional)**

    - Retrieve calibration fidelities to visualize it.

3.  **Layout Generation and Cost Evaluation**

    - Use `iqm-qubit-selector` to generate possible qubit layouts for your circuit.

    - Evaluate the cost of each layout based on calibration data.

4.  **Select the Best Layout**

    - Choose the layout with the lowest cost and transpile your circuit accordingly.

5.  **Advanced Options**

    - Customize cost functions (e.g., include readout fidelity or use different two-qubit gate fidelities).

    - Generate additional layouts by increasing the number of trials.

    - Remove specific qubits from consideration.

Refer to the code cells for detailed usage and customization options.

```
import os
import matplotlib.pyplot as plt
from iqm.qubit_selector.qubit_selector import *
from iqm.qubit_selector.qiskit_utils import get_circuit, CircuitType
from iqm.qiskit_iqm import IQMProvider
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

## Fetch calibration data for the given device and visualize it

```
calibration_data = CalibrationDataManager().get_calibration_fidelities(backend)
```

```
def plot_calibration_data(key, data):
    two_qubit_keys = [CalibrationType.CZ.value, CalibrationType.CLIFFORD.value]
    coherence_keys = [CalibrationType.T1.value, CalibrationType.T2.value]
    every_second = key in two_qubit_keys
    coherence = key in coherence_keys
    xlabel = 'Pairs' if key in two_qubit_keys else 'Qubits'
    ylabel = 'Error' if key not in coherence_keys else 'Coherence in (us)'
    pairs = list(data.items())
    if every_second:
        pairs = pairs[::2]
    labels = [pair[0] for pair in pairs]

    if coherence:
        values = [pair[1] for pair in pairs]
    else:
        values = [1-pair[1] for pair in pairs]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'{key} metrics')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

## uncomment for visualization of calibration data
# for k, v in calibration_data.items():
#     plot_calibration_data(k, v)
```

## Single API call to get the best layout

Note that the lower the value of the cost, the better is the layout! The qubit indices in the layout are `qiskit` based.

```
nqubits = 10
# Possible choices for pre-defined circuits 'ghz', 'qft', 'random', 'wstate', 'quantum_volume' 'qaoa'
qc_algo = get_circuit(CircuitType.GHZ, nqubits) ## plug in your qiskit quantum circuit of interest

layouts, cost = CostEvaluator(backend=backend, quantum_circuit=qc_algo).get_top_layouts(num_layouts=50)
print("Top 10 qiskit layouts and their costs:")
for layout, c in zip(layouts[:10], cost[:10]):
    print(f"Layout: {layout}, Cost: {c*100:.2f}%")
```

## Finding list of matching layouts to run your quantum circuit

Enables users to get a list of possible compatible layouts for the quantum circuit of interest.

```
layouts = LayoutGenerator(backend, qc_algo).generate_unique_layouts()
```

## Adding readout fidelity in the cost function:

Users can add the readout error to the cost function, by using the `readoutmode` argument in `CostEvaluator`.

The `ReadoutMode.FIDELITY` option will add the readout fidelity metric to the cost function, while `ReadoutMode.QNDNESS` will add the readout QNDness metric. This comes in handy when one is not performing readout error mitigation for the target circuits. You can also choose to ignore the readout error by not providing the `readoutmode` argument or setting it to `ReadoutMode.NONE` (which is the default option).

```
layouts_with_readout, cost_with_readout = CostEvaluator(backend, qc_algo, readoutmode=ReadoutMode.QNDNESS).get_top_layouts(num_layouts=10)
```

## Changing two-qubit gate fidelity in the cost function:

The `cost_function` argument in the `CostEvaluator` class allows the user to choose the two-qubit gate fidelity for the cost function evaluation.

By default, the cost function uses the CZ gate fidelity (`CostFunction.GATE_COST_CZ`). The user can alternately use the Clifford gate fidelity instead, by setting `cost_function=CostFunction.GATE_COST_CLIFFORD` when calling `CostEvaluator`.

```
clifford_layouts, cost_clifford = CostEvaluator(backend, qc_algo, cost_function=CostFunction.GATE_COST_CLIFFORD,layouts= layouts, readoutmode=ReadoutMode.NONE).get_top_layouts(num_layouts=10)
```

## Increasing the number of proposed layouts:

To increase the search of additonal layout, the user can increase the `num_trials` argument. This has been currently defaulted to `2000`.

Note that this also increases the run time of the cost-function evaluation but offers a better search across different layouts.

```
more_layouts, cost = CostEvaluator(backend, qc_algo, num_trials=20000, readoutmode=ReadoutMode.NONE).get_top_layouts(num_layouts=10)
```

## Removing qubits:

There is an option to remove certain qubits prior to cost evalatuation of the layouts. So these qubits are not considered in the layouts at all.

```
qubits_to_remove = ["QB1", "QB2"]  ## plug in the qubits you want to remove from consideration
qubits_to_remove_qiskit_indices = [backend.qubit_name_to_index(qubit) for qubit in qubits_to_remove]  ## convert to indices assuming qubit names are in the format 'QB{index}'
layouts_with_removed_qubits, cost_with_removed_qubits = CostEvaluator(backend, qc_algo, remove_qubits=qubits_to_remove_qiskit_indices).get_top_layouts(num_layouts=10)
```
