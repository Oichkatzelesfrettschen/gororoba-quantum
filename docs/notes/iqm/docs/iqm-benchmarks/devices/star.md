> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/devices/star.html](https://docs.iqm.tech/4.7/iqm-benchmarks/devices/star.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 79f0f4fe98c8d349d6b87d5191d2496fb581396c5dbba9e625e0ac9b33d7b97e.

# Benchmarking IQM Star

This notebook allows you to run some useful benchmarks for the Star system.

## Connect to the backend

```
import os
from iqm.qiskit_iqm import IQMProvider
import random

os.environ["IQM_TOKENS_FILE"]="YOUR TOKEN HERE"
iqm_url =  'YOUR URL HERE'
provider = IQMProvider(iqm_url)
backend = provider.get_backend()
```

We can access the Star backend and plot its connectivity graph to check that everything is working properly.

```
import networkx as nx
import matplotlib.pyplot as plt

coupling_map = backend.coupling_map

G = nx.Graph()
G.add_edges_from(coupling_map) 
pos = nx.spring_layout(G, seed=42) 
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', 
        node_size=1000, font_size=10, linewidths=1.5, width=2)
plt.show()
```

We run the cell below to ignore those warnings that are not critical for the correct run of the benchmarks.

```
import warnings
warnings.filterwarnings(action="ignore")  
```

## GHZ state fidelity

The GHZ (Greenberger-Horne-Zeilinger) state is a maximally entangled quantum state that involves three or more qubits, \\n\\. It is an equal superposition of all qubits being in state 0 and all qubits being in state 1, i.e., \\\| GHZ \rangle = \frac{1}{\sqrt{2}}(\|0\rangle^{\otimes n}+\|1\rangle^{\otimes n})\\.

The GHZ state fidelity acts as a **witness** for genuine multi-qubit entanglement if found to be above \\0.5\\. This means that the measurement results cannot be explained without entanglement involving **all** qubits, so it is a great way to evaluate the “quantumness” of the computer.

The state \\\rho\_{\text{ideal}}= \|GHZ\rangle\langle GHZ\|\\ is a pure state, so in this case the fidelity can be computed as:

\\ F(\text{ideal}, \text{measured})= \langle GHZ \| \rho\_{\text{measured}} \| GHZ \rangle,\\

where \\\rho\_{\text{measured}}\\ is the density matrix given by the actual results of the quantum computer. The ideal GHZ state density matrix entries can be written as \\\rho\_{i,j}=\langle i\| \rho\_{\text{ideal}} \| j \rangle\\ where \\i,j\\ are the \\n\\ basis states \\\\\|00..0\rangle, ..., \|11..1\rangle\\\\; only the corner entries \\\rho\_{0,0},\rho\_{0,n},\rho\_{n,0}\\ and \\\rho\_{n,n} \\ are non-zero. This simplifies the process since we only need to measure these four components. In the fidelity formula, all other entries are effectively nullified by the zero entries in the ideal state matrix. To measure the coherences (off-diagonal entries) we use the method of multiple quantum coherences [Mooney, 2021](https://iopscience.iop.org/article/10.1088/2399-6528/ac1df7/meta).

```
from iqm.benchmarks.entanglement.ghz import GHZConfiguration, GHZBenchmark
```

```
num_qubits = backend.num_qubits
chosen_layout = [list(range(qubits)) for qubits in range(2,num_qubits+1)]
GHZ = GHZConfiguration(
    state_generation_routine="star",
    custom_qubits_array=chosen_layout,
    shots=2000,
    fidelity_routine="coherences", 
    rem=True,
    mit_shots=1000,
)
```

```
benchmark_ghz = GHZBenchmark(backend, GHZ)
run_ghz = benchmark_ghz.run()
```

```
result_ghz = benchmark_ghz.analyze()
result_ghz.plot_all()
```

## Quantum Volume

Quantum volume is a single-number metric that was introduced in [Cross, 2019](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.100.032328). It evaluates the quality of a quantum processor via the largest random *square* circuit, i.e., with the same number of layers of parallel random 2-qubit unitaries as number of qubits, that it can run successfully.

The success of a run is based on the heavy output probability, which corresponds to the probability of observing *heavy outputs*, i.e. the measurement outputs that occcur with a probability greater than the median of the distribution. The heavy output generation problem asks if the generated distribution of the random circuit we run contains heavy outputs at least 2/3 of the time (on average) with a high confidence level, typically higher than 97.5%. It can be shown that the heavy output probability for an ideal device is at around 0.85 asymptotically. The quantum volume is then defined as

\\\log_2 V_q = \underset{n}{\text{argmax}} \min (n, d(n))\\

where \\n \leq N\\ is a number of qubits and \\d(n)\\ is the *achievable depth*, i.e. the largest depth such that we are confident the probability of observing a heavy output is greater than 2/3.

```
from iqm.benchmarks.quantum_volume.quantum_volume import QuantumVolumeConfiguration, QuantumVolumeBenchmark
```

We define a combination of qubits to test quantum volume on.

```
chosen_layouts = [[14, 3, 5]] ## choose the optimal layouts to run
QV = QuantumVolumeConfiguration(
    num_circuits=500, 
    shots=2**8,
    calset_id=None,
    num_sigmas=2,
    choose_qubits_routine="custom",
    custom_qubits_array=chosen_layouts, 
    qiskit_optim_level=3,
    optimize_sqg=True,
    max_gates_per_batch=60_000,
    rem=True,
    mit_shots=1_000,
)
```

> If you want to modify the settings above, please refer to the documentation [here](https://docs.iqm.tech/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration).

Warning: The following code cell may take few minutes to run since it will compute the benchmark on all the qubit layouts specified above.

```
benchmark_qv = QuantumVolumeBenchmark(backend, QV)
run_qv = benchmark_qv.run()
```

```
result_qv = benchmark_qv.analyze()
for v in result_qv.plots.values():
    display(v)
```

## Circuit Layer Operations Per Second (CLOPS)

CLOPS is a metric that estimates the speed at which a quantum computer can execute Quantum Volume (QV) layers of a quantum circuit. That is, the circuits to calculate this benchmark have the same structure as the ones used for QV. Here we follow the definition introduced in ([Wack, 2021](https://arxiv.org/abs/2110.14108)), but other versions of this benchmark exist.

CLOPS is measured by means of a quantum variational-like protocol, where templates of parametrized QV circuits are assigned random parameters, executed, and outcomes are used as a seed to assign new parameters and repeat the process. The ratio of number of templates (\\M\\), parameter updates (\\K\\), measurement shots (\\S\\) and QV layers (\\\log_2\mathrm{QV}\\) with the time taken to run all, constitutes the CLOPS value:

\\ \mathrm{CLOPS}=M\times{K}\times{S}\times\log_2\mathrm{QV}/\mathrm{total\\time}. \\

Notice that the total CLOPS time includes that of assignment of parameters, submission of circuits and retrieval of results.

```
from iqm.benchmarks.quantum_volume.clops import CLOPSConfiguration, CLOPSBenchmark, plot_times
```

```
CLOPS = CLOPSConfiguration(
    qubits=[14, 3, 5], # run with the same layout as 
    num_circuits=100,
    num_updates=10, 
    num_shots=100, 
    calset_id=None,
    qiskit_optim_level=3,
    optimize_sqg=True,
)
```

> If you want to modify the settings above, please refer to the documentation [here](https://docs.iqm.tech/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration).

```
benchmark_clops = CLOPSBenchmark(backend, CLOPS)
run_clops = benchmark_clops.run()
```

```
result_clops = benchmark_clops.analyze()
result_clops.observations
```

```
result_clops.plot_all()
```

## Q-Score

*The Q-score measures the maximum number of qubits that can be used effectively to solve the MaxCut combinatorial optimization problem with the Quantum Approximate Optimization Algorithm* - [Martiel,2021](https://ieeexplore.ieee.org/document/9459509)

The graphs chosen for the benchmark are random Erdős-Rényi graphs with 50% edge-probability between nodes. The obtained cost of the solution, i.e. the average number of cut edges, must be above a certain threshold. Specifically, one has to find the cost of a graph to be above \\\beta\geq 0.2\\ on a scale where \\\beta = 0\\ corresponds to a random solution and \\\beta = 1\\ to an ideal solution.

```
from iqm.benchmarks.optimization.qscore import QScoreConfiguration, QScoreBenchmark
import random
```

```
num_qubits = backend.num_qubits
chosen_layout = [list(range(qubits)) for qubits in range(1,num_qubits+1)]
QSCORE = QScoreConfiguration(
    num_instances = 60,
    num_qaoa_layers= 1,
    shots = 1000,
    calset_id=None, 
    min_num_nodes = 2,
    max_num_nodes = None,
    use_virtual_node = True,
    use_classically_optimized_angles = True,
    choose_qubits_routine = "custom",
    custom_qubits_array= chosen_layout,
    seed = random.randint(1, 999999),
    REM = True,
    mit_shots = 1000,
    )
```

> If you want to modify the settings above, please refer to the documentation [here](https://docs.iqm.tech/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html#iqm.benchmarks.optimization.qscore.QScoreConfiguration).

Warning: The following code cell may take **several** minutes to run.

```
benchmark_qscore = QScoreBenchmark(backend, QSCORE)
run_qscore = benchmark_qscore.run()
```

```
result_qscore = benchmark_qscore.analyze()
```

```
result_qscore.plot_all()
```

## Summary

```
import numpy as np

### GHZ
obs_ghz = result_ghz.observations
fidelity = round(min([obs_ghz[i].value for i in range(len(obs_ghz)) if obs_ghz[i].name=='fidelity']),2)

### QV
obs_qv = result_qv.observations
qv = max([obs_qv[i].value for i in range(len(obs_qv)) if obs_qv[i].name=='QV_result'])

### CLOPS
obs_clops = result_clops.observations
clops = max([obs_clops[0].value])

### QS 
obs_qs = result_qscore.observations
qs = np.argmin([obs_qs[i].value-0.2 for i in range(len(obs_qs)) if obs_qs[i].name == 'mean_approximation_ratio' and obs_qs[i].value-0.2>0])+2


summary = {'GHZ state fidelity': ['≥ 0.5', fidelity],
    'Quantum Volume': qv, 
    'CLOPS':  clops, 
    'Q-Score':  qs 
}
```

```
summary
```
