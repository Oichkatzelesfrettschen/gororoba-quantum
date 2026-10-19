> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_mirror_rb.html](https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_mirror_rb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 00606613f6c99ac97d7e815bca65bd40da9e2f808a00f7c5bda8b587e4067294.

# Mirror Randomized Benchmarking (MRB)

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

## Mirror RB Configuration

```
from iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb import *
```

```
EXAMPLE_MRB = MirrorRBConfiguration(
    qubits_array=[[0,1],
                  [0,1,3,4]],
                  #[0,1,3,4,8,9],
                  #[0,1,3,4,8,9,13,14],
                  # [0,1,3,4,8,9,13,14,17,18],
                  # [0,1,3,4,8,9,13,14,17,18,2,7],
                  # [0,1,3,4,8,9,13,14,17,18,2,7,5,10],
                  # [0,1,3,4,8,9,13,14,17,18,2,7,5,10,6,11]],
                  # [0,1,3,4,8,9,13,14,17,18,2,7,5,10,6,11,15,16],
                  # [0,1,3,4,8,9,13,14,17,18,2,7,5,10,6,11,15,16,12,19]],
    depths_array=[[2**m for m in range(9)],
                  [2**m for m in range(8)]],
                  # [2**m for m in range(7)],
                  # [2**m for m in range(6)],
                  # [2**(m+1)-1 for m in range(6)],
                  # [2**(m+1)-1 for m in range(6)],
                  # [2**(m+1)-1 for m in range(5)],
                  # [2**(m+1)-1 for m in range(5)],
                  # [2**(m+1)-1 for m in range(4)],
                  # [2**(m+1)-1 for m in range(4)]],
                  # If only one list of depths is specified, it applies to all qubit layouts
                  # If less depths than qubit layouts is specified, the first one is applied
    num_circuit_samples=10,
    num_pauli_samples=5,
    shots=2**8,
    two_qubit_gate_ensemble={"CZGate": 0.8, "iSwapGate": 0.2}, # {GATE: PROBABILITY}
    density_2q_gates=0.25,
    max_circuits_per_batch=100,
)
```

## Run the experiment

```
benchmark_mrb = MirrorRandomizedBenchmarking(backend, EXAMPLE_MRB)
run_mrb = benchmark_mrb.run()
```

## Analyze the results

```
result_mrb = benchmark_mrb.analyze()
```

### List all the keys in the attributes of the dataset

```
attr_keys = sorted([str(x) for x in list(run_mrb.dataset.attrs.keys())])
for k in attr_keys:
    print(k)
```

```
run_mrb.dataset.attrs[0]
```

### The observation object contains the benchmark results

```
result_mrb.observations
```

### Generate plots

```
for k in result_mrb.plots.keys():
    print(k)
```

```
key_mrb_plot = "all_qubit_layouts"
result_mrb.plot(key_mrb_plot)
```
