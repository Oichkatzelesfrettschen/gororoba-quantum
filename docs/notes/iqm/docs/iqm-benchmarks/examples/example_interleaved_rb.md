> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_interleaved_rb.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_interleaved_rb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f4ed2e83cf508cfd385e231a557b0fe8233cb12545a9a4e66f4c0183bbd640e5.

# Interleaved Randomized Benchmarking (IRB)

```
%load_ext autoreload
%autoreload 2
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

## Interleaved Randomized Benchmarking Configuration

### 1Q gate IRB

```
from iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb import *
import numpy as np
```

```
EXAMPLE_IRB_1Q = InterleavedRBConfiguration(
    qubits_array=[[0],[2]],#,[4],[6]],[8],[10],[12],[14],[16],[17],[19]],
    sequence_lengths=[2**(m+1)-1 for m in range(8)],
    num_circuit_samples=25,
    shots=2**9,
    parallel_execution=True,
    interleaved_gate = "RGate",
    interleaved_gate_params = [np.pi, 0],
    simultaneous_fit = ["amplitude", "offset"],
    max_circuits_per_batch=100,
)
```

#### Run the experiment - 1Q gate IRB

```
benchmark_irb_1Q = InterleavedRandomizedBenchmarking(backend, EXAMPLE_IRB_1Q)
run_irb_1Q = benchmark_irb_1Q.run()
```

#### Analyze the results - 1Q gate IRB

```
result_irb_1Q = benchmark_irb_1Q.analyze()
```

```
result_irb_1Q.observations
```

```
for v in result_irb_1Q.plots.values():
    display(v)
```

### 2Q gate IRB

```
EXAMPLE_IRB_2Q = InterleavedRBConfiguration(
    qubits_array=[[0,1],[3,4]],#,[8,9],[13,14],[17,18],[5,6],[10,11],[15,16]],
    sequence_lengths=[2**(m+1)-1 for m in range(7)],
    num_circuit_samples=25,
    shots=2**8,
    parallel_execution=True, # whether RB is run in parallel - use if you know what you're doing!
    interleaved_gate = "CZGate",
    interleaved_gate_params = None,
    simultaneous_fit = ["amplitude", "offset"],
    max_circuits_per_batch=100,
)
```

#### Run the experiment - 2Q gate IRB

```
benchmark_irb_2Q = InterleavedRandomizedBenchmarking(backend, EXAMPLE_IRB_2Q)
run_irb_2Q = benchmark_irb_2Q.run()
```

#### Analyze the results - 2Q gate IRB

```
result_irb_2Q = benchmark_irb_2Q.analyze()
```

```
for plot in result_irb_2Q.plots.values():
    display(plot)
```

## IRB for non-native gate

```
EXAMPLE_IRB_iswap = InterleavedRBConfiguration(
    qubits_array=[[3,4],[8,9]],
    sequence_lengths=[2**(m+1)-1 for m in range(7)],
    num_circuit_samples=30,
    shots=2**10,
    parallel_execution=True, # whether RB is run in parallel - use if you know what you're doing!
    interleaved_gate = "iSwapGate",
    interleaved_gate_params = None,
    simultaneous_fit = ["amplitude", "offset"],
    max_circuits_per_batch=100,
)
```

```
benchmark_irb_iswap = InterleavedRandomizedBenchmarking(backend, EXAMPLE_IRB_iswap)
run_irb_iswap = benchmark_irb_iswap.run()
```

```
result_irb_iswap = benchmark_irb_iswap.analyze()
```

```
for plot in result_irb_iswap.plots.values():
    display(plot)
```
