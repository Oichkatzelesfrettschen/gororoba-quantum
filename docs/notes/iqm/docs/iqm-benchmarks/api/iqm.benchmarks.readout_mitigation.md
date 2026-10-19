> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 777512133c0f4c1dc721b22eee839c93a637b2491d4512364bbb66a9a8f6cea3.

# iqm.benchmarks.readout_mitigation

M3 modification for readout mitigation at IQM QPU’s.

Functions

|  |  |
|----|----|
| [`apply_readout_error_mitigation`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.apply_readout_error_mitigation.html#iqm.benchmarks.readout_mitigation.apply_readout_error_mitigation "iqm.benchmarks.readout_mitigation.apply_readout_error_mitigation")(backend_arg, ...) | Application of readout error mitigation to a list of counts. |
| [`readout_error_m3`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.readout_error_m3.html#iqm.benchmarks.readout_mitigation.readout_error_m3 "iqm.benchmarks.readout_mitigation.readout_error_m3")(counts, mit, qubits) | Counts processor using M3IQM for readout error mitigation. |

Classes

|  |  |
|----|----|
| [`M3IQM`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.M3IQM.html#iqm.benchmarks.readout_mitigation.M3IQM "iqm.benchmarks.readout_mitigation.M3IQM")(\[system, iter_threshold\]) | M3 readout mitigation class modified to work with IQM devices. |

Inheritance

![Inheritance diagram of iqm.benchmarks.readout_mitigation](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-4977e76bb2ba8d3195ba7619bd31bfcde683f1c9.png)
