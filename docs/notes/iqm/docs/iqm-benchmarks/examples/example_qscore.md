> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_qscore.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_qscore.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e58c200cb77dc9f9f7a7a32005f85b574fdf25699220f9a525eb42661d515d27.

# Q-Score

```
%load_ext autoreload
%autoreload 2

from iqm.benchmarks.optimization.qscore import *
import random
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

## Customize dynamical decoupling strategy

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

## Qscore Configuration

```
min_num_nodes = 6 # minimum number of nodes in the graph
max_num_nodes = 10 # maximum number of nodes in the graph]
EXAMPLE_QSCORE = QScoreConfiguration(
    num_instances = 100, # number of graph instances to run; decrease to save runtime, increase for smaller error bars
    num_qaoa_layers= 1, # number of QAOA layers (depth of the QAOA circuit). Usually is set to 1 for QScore benchmark.
    shots = 2048, # number of shots per instance
    min_num_nodes = min_num_nodes, # minimum number of nodes in the graph
    max_num_nodes= max_num_nodes, # maximum number of nodes in the graph
    use_virtual_node = True, # whether to use a virtual node in the graph (works only for depth 1 QAOA)
    use_classically_optimized_angles = True, # whether to use classically optimized angles or use
    choose_qubits_routine = "naive", # routine to choose qubits for the QAOA circuit, "naive" is the default selection, while "custom" allows for custom qubit selection
    custom_qubits_array=None, # custom qubits array, only used if choose_qubits_routine is set to "custom"
    seed = random.randint(1, 999999), # random seed for reproducibility
    REM = True, # whether to use the readout error mitigation protocol
    mit_shots=1000, # number of shots for the readout error mitigation protocol
    use_dd = False, # whether to use dynamical decoupling
    dd_strategy = strategy, # dynamical decoupling strategy
    )
```

## Run the experiment

```
benchmark_qscore = QScoreBenchmark(backend, EXAMPLE_QSCORE)
run0_qscore = benchmark_qscore.run()
```

## Perform Analysis

```
result0_qscore = benchmark_qscore.analyze()
```

```
result0_qscore.observations
```

```
result0_qscore.plot_all()
```
