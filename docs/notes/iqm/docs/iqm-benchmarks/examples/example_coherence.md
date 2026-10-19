> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_coherence.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_coherence.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1460f0d6fffb1fdfd80d55754703f6becde12fd449b863462993d5d9dac9c67e.

# Coherence experiments

```
%load_ext autoreload
%autoreload 2

from iqm.benchmarks.coherence.coherence import *
from iqm.qiskit_iqm import IQMProvider
import numpy as np
import os
```

## Set IQM Token if using Resonance

```
# import os
# from iqm.qiskit_iqm import IQMProvider
#
# token = ""
# os.environ["IQM_TOKEN"] = token
# quantum_computer = "" # provide actual quantum computer name. i.e. "emerald", "garnet", "sirius"
# iqm_server_url = "https://resonance.iqm.tech/" # provide actual IQM server URL
# os.environ["IQM_SERVER_URL"] = iqm_server_url
#
# provider = IQMProvider(iqm_server_url, quantum_computer=quantum_computer)
# backend = provider.get_backend()
```

## Alternatively choose (or define) a simulator backend

```
#backend = "fakeadonis"
backend = "fakeapollo"
```

## Coherence Configuration

```
EXAMPLE = CoherenceConfiguration(
    delays = list(np.linspace(0, 100e-6, 100)), # Delays specified in seconds
    qiskit_optim_level = 3,
    optimize_sqg = True,
    coherence_exp = "t2_echo", # Options: "t1", "t2_echo"
    qubits_to_plot=list(range(10)), # Give the list of qubits you want to plot
    shots = 1000,
    max_circuits_per_batch=100,
    )
```

## Run the experiment

```
benchmark = CoherenceBenchmark(backend, EXAMPLE)
run = benchmark.run()
```

## Perform analysis and plot results

```
result = benchmark.analyze()
result.plot_all()
```

```
# Shot individual results and uncertainties
result.observations
```
