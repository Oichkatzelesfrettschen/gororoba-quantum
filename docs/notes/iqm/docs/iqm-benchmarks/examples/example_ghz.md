> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_ghz.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_ghz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d907f3adb427c3d1ebd6b3f99be4cc44b407356dac97377f7e04b76a1415841f.

# Greenberger–Horne–Zeilinger (GHZ) State Fidelity

The aim of this benchmark is to show whether a GHZ state with high enough fidelity can be prepared such that the state is genuinely multipartite entangled. One can show that a fidelity larger than 0.5 is a sufficient condition (see Leibfried, D. et al., Creation of a six-atom ‘Schrödinger cat’ state. Nature 438, 639–642 (2005))

The benchmark currently offers two methods to estimate the fidelity:

- Multiple quantum coherences (G. J. Mooney et al., Generation and verification of 27-qubit Greenberger-Horne-Zeilinger states in a superconducting quantum computer, J. Phys. Commun. 5, 095004 (2021))

- Randomized measurements (Elben, A. et al., Statistical correlations between locally randomized measurements: A toolbox for probing entanglement in many-body quantum states, Phys. Rev. A 99, 052323 (2019))

Additionally, for a given set of \\n\\ qubits, different circuits can be applied which lead to the same GHZ state. Currently there are the following implementations:

- “naive”: The textbook ciruit of depth \\n\\, which starts from a Hadamrd gate on one qubit and entangles each additional qubit with a CNOT operation from the first.

- “log_depth”: A logarithmic depth circuit utilizing parallel CNOT applications. Either the method in Cruz et al. https://arxiv.org/abs/1807.05572 or the method in Mooney et al. https://arxiv.org/abs/2101.08946 is used, depending on which yields the lower depth or the lower number of 2-qubit gates.

- “tree”: An in-house logarithmic depth circuit utilizing calibration data of the CZ-fidelities and a tree-graph algorithm to find a circuit with minimal depth and high fidelity 2-qubit gates. **It is recommended to use “tree” for square grid QPU layouts, for instance IQM-Emerald or IQM-Garnet.**

- “star” and “star_optimal”: CZ and move gate scheduling optimized for star architectures, which have all-to-all connectivity but no parallel CZ gates. **It is recommended to use “star_optimal” for star layouts with a central resonator like IQM-Sirius.**

Note that the first two methods will always give the same circuit for the same qubit layout (and the same coupling map), while the “tree” method relies on the latest calibration fidelities and can give different circuits on different days. Thus for consistent comparisons one of the first two methods should be chosen, while for the best results, i.e. the largest possible GME entangled GHZ state, the tree-method is preferable.

```
from iqm.benchmarks.entanglement.ghz import *
import os
from iqm.qiskit_iqm import IQMProvider

token = ""
os.environ["IQM_TOKEN"] = token
quantum_computer = "emerald" # provide quantum computer name
iqm_server_url = "https://resonance.iqm.tech/" # provide IQM server URL
os.environ["IQM_SERVER_URL"] = iqm_server_url

provider = IQMProvider(iqm_server_url, quantum_computer=quantum_computer)
backend = provider.get_backend()
```

## Dynamical decoupling strategy

The success of dynamical decoupling (DD) depends on the coherence several factors, like

- Amount and lenght of idle segments in the circuit,

- Magnitude of idling errors,

- Single qubit gate fidelities (since DD adds additional single qubit gates).

Therefore just using the default DD strategy is not guaranteed to improve the results. In this notebook we apply a minimal DD strategy which only add single qubit gates on qubits with a high single qubit gate fidelity, and only adds a minimal amount of extra gates per idle segment (just two X-Gates). This strategy should improve outcomes in most cases.

```
from iqm.iqm_client.models import DDStrategy
from iqm.benchmarks.utils import extract_fidelities_unified
_, calibration_data = extract_fidelities_unified(backend=backend)

# Minimal dynamical decoupling with only two extra single-qubit gates per idle
dd_qubits = frozenset(["QB"+str(qubit_name+1) for qubit_name, fidelity in calibration_data["fidelity_1qb_gates_averaged"].items() if fidelity > 0.999])
strategy = DDStrategy(gate_sequences=[(2, 'XX', 'center')], target_qubits = dd_qubits)

print(f"Minimal dynamical decoupling strategy:")
for k, v in strategy.__dict__.items():
    print(f"\t{k}: {v}")
```

## Definition of the benchmark configuration

The important parameters are:

- `custom_qubits_array`: A `list[list[int]]` which includes all qubit layouts on which the benchmark is run.

- `shots`: The number of shots for the fidelity measurement

- `fidelity_routine`: Either “coherences” or “randomized_measurements”

- `rem`: Boolean value that controls whether readout error mitigation is used

- `mit_shots`: Whenever rem=True, this parameter controls the total number of shots used to calibrate readout error mitgation

- `num_RMs`: The number of randomized measurement settings (only necessary when choosing `fidelity_routine=randomized_measurements`)

```
MINIMAL_GHZ = GHZConfiguration(
    state_generation_routine="tree",
            custom_qubits_array=[ # naive layouts
                list(np.arange(30)),
                list(np.arange(35)),
                list(np.arange(40)),
                list(np.arange(45)),
            ],
    shots=1000,
    fidelity_routine="coherences",
    rem=True,
    mit_shots=1000,
    max_circuits_per_batch=100,
    use_dd=True,
    dd_strategy=strategy,
    tree_idle_penalty=1.0, ## This is the penalty for idle qubits in the tree search. It can be tuned to favor trees with fewer idle qubits.
    tree_rank=0, ## the rank of the tree candidates to be considered for the final circuit. Starts with 0 being the best tree.
)
```

## Running the benchmark

```
benchmark_ghz = GHZBenchmark(backend, MINIMAL_GHZ)
run_ghz = benchmark_ghz.run()
```

```
result = benchmark_ghz.analyze()
```

## Accessing the results

To see individual fidelitiy and uncertainty values of a given qubit layout, one can filter the `result.observations`-list by layout as shown below.

The plot allows a comparison of all layout results with and without REM, where the data point description labels “L0”, “L1”, … enumerate the layouts in the order defined in the configuration.

```
qubit_layout = list(range(10))
for observation in result.observations:
    if observation.identifier.string_identifier == str(qubit_layout):
        print(f"{observation.name}: {observation.value} +/- {observation.uncertainty}")
result.plot_all()
```

## Custom layout selection tool

For thinking about which qubit layouts to use on a large device, the below code produces a visualization of the connectivity and CZ fidelities.

Requirements:

- Access to the backend, in this example IQM Emerald.

- An access token environment variable needs to be set via `os.environ["IQM_TOKEN"] = <your_token>`.

Use of the plot:

- If the `qubit_layouts` argument is provided, the selected qubits are marked in orange.

- CZ errors are indicated with edge width (**thinner edge is better**), where the edge width is given by \\w\_{ij} = - \mathrm{log}(\mathcal{F}\_{\mathrm{CZ}}^{ij})\\.

- Each edge is also labeled with the width value.

- Some graph layouts are predefined to match the layout as shown in IQM-Resonance. If the layout is not predefined, a graph in grid or star layout will be automatically generated, dependeing on the backend. Automatically generated graphs might need to be rerun a few times until a nice node layout is found.

- Single qubit errors are visualized as node size (**smaller radius is better**), with the node size being determined by \\- \mathrm{log}(\mathcal{F})\\, where \\\mathcal{F}\\ is either the single qubit average gate fidelity, the single qubit readout fidelity, or the single qubit idle gate fidelity. Which of these is used can be controlled by the `sq_metric` argument, which can be set to “fidelity” “readout”, or “coherence”, where the latter option leads to the idle fidelities being shown.

- The option `show_ghz_path` controls whether the edges used in the GHZ state generation circuit are highlighted in red. This can be helpful to see which CZ fidelities are most relevant for the GHZ benchmark, since the state generation algorithm will try to find an optimal path along high fidelity connections.

```
from iqm.benchmarks.utils_plots import plot_layout_fidelity_graph
qubit_layouts = [list(range(20))]
fig = plot_layout_fidelity_graph(backend, qubit_layouts = qubit_layouts, sq_metric="coherence", show_ghz_path=True)
```
