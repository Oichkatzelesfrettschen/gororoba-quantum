> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6ba19cdd8fbff945f48133edf1588fbfb39a30e555b151b451be26640a3a52ba.

# iqm.benchmarks.quantum_volume.clops

CLOPS benchmark.

Functions

|  |  |
|----|----|
| [`clops_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.clops_analysis.html#iqm.benchmarks.quantum_volume.clops.clops_analysis "iqm.benchmarks.quantum_volume.clops.clops_analysis")(run) | Analysis function for a CLOPS (v or h) experiment. |
| [`plot_times`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.plot_times.html#iqm.benchmarks.quantum_volume.clops.plot_times "iqm.benchmarks.quantum_volume.clops.plot_times")(clops_data, observations) | Generate a figure representing the different elapsed times in the CLOPS experiment. |
| [`retrieve_clops_elapsed_times`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.retrieve_clops_elapsed_times.html#iqm.benchmarks.quantum_volume.clops.retrieve_clops_elapsed_times "iqm.benchmarks.quantum_volume.clops.retrieve_clops_elapsed_times")(job_meta) | Retrieve the elapsed times from the CLOPS job metadata. |

Classes

|  |  |
|----|----|
| [`CLOPSBenchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.html#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark")(backend_arg, configuration) | CLOPS reflect the speed of execution of parametrized QV circuits. |
| [`CLOPSConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration")(\*, benchmark, shots, ...) | CLOPS configuration. |

Inheritance

![Inheritance diagram of iqm.benchmarks.quantum_volume.clops](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-9d692324f9b4964e7fa89bee41d2a5159276086e.png)
