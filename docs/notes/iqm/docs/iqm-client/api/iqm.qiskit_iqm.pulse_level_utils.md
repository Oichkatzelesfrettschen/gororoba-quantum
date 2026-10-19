> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5bfff18a26bf296d2f40f535d86c23b3fe4656fed153d66c045db7b1e8c39231.

# pulse_level_utils

Full path: iqm.qiskit_iqm.pulse_level_utils

Utilities for running pulse-level jobs using Qiskit classes.

Functions

|  |  |
|----|----|
| [`get_qiskit_compiler`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler.html#iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler "iqm.qiskit_iqm.pulse_level_utils.get_qiskit_compiler")(backend, \*\[, ...\]) | IQM Compiler for transforming Qiskit circuits into pulse-level jobs. |
| [`parallelize_and_transpile`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile.html#iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile "iqm.qiskit_iqm.pulse_level_utils.parallelize_and_transpile")(circuits, ...\[, ...\]) | Transpile Qiskit circuits and parallelize them if colour grouped components were inputted. |
| [`qiskit_circuits_to_iqm_circuits`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits.html#iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits "iqm.qiskit_iqm.pulse_level_utils.qiskit_circuits_to_iqm_circuits")(circuits, ...) | Convert Qiskit QuantumCircuits to IQM circuits. |
| [`qiskit_to_iqm`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm.html#iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm "iqm.qiskit_iqm.pulse_level_utils.qiskit_to_iqm")(backend, qiskit_circuits, \*\[, ...\]) | Convert transpiled Qiskit quantum circuits to IQM format, for compiling to pulse level. |
| [`sweep_job_to_qiskit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit.html#iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit "iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit")(job_tracker, \*, shots) | Query the results of a completed pulse-level job and convert it to a Qiskit Result. |
