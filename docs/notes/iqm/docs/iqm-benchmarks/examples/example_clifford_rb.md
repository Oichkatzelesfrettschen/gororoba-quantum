> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_clifford_rb.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_clifford_rb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 74bc5940aee8f67f2cd12e8740b3adb273db7453b9e6f71592f3713a3de658a5.

# Clifford Randomized Benchmarking (CRB)

```
%load_ext autoreload
%autoreload 2
```

## Set IQM Token if using Resonance.

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

## Randomized Benchmarking Configuration

NB: Clifford RB is executed by default with Interleaved RB !

```
from iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb import *
```

```
EXAMPLE_CRB = CliffordRBConfiguration(
    qubits_array=[[0,1],[3,4]],#,[8,9],[13,14],[17,18],[5,6],[10,11],[15,16]],
    sequence_lengths=[2**(m+1)-1 for m in range(6)],
    num_circuit_samples=25,
    shots=2**8,
    parallel_execution=False,
    max_circuits_per_batch=100,
)
```

## Run the experiment

```
benchmark_clifford_rb = CliffordRandomizedBenchmarking(backend, EXAMPLE_CRB)
run_clifford_rb = benchmark_clifford_rb.run()
```

## Perform the analysis

```
result_clifford_rb = benchmark_clifford_rb.analyze()
```

```
run_clifford_rb.dataset.attrs
```

```
result_clifford_rb.observations
```

```
for plot in result_clifford_rb.plots.values():
    display(plot)
```
