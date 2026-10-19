> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 51443dea4754509571ac4c1f43c1f6f804a126a68c64871cc954dc0df90fdf59.

# qrisp_iqm

Full path: iqm.qrisp_iqm

Qrisp adapter for IQM’s quantum computers.

Provides the full Qrisp → IQM toolchain:

**Backend & execution**

- [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend") — run circuits on IQM hardware.

- [`IQMCircuitJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html#iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob "iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob"), [`IQMPulseJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html#iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob "iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob") — track asynchronous execution.

**Transpilation**

- [`transpile_to_iqm()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html#iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm "iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm") — one-liner transpilation to native IQM gates.

- [`create_iqm_pass_manager()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html#iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager") — factory for the full plasma-sabre pipeline.

- `plasma_layout()`, `plasma_route()`, `vf2pp_layout()` — layout & routing passes.

- `commute_phases()`, `measurement_parallelization()` — optimisation passes.

**Pulse-level integration**

- [`extract_iqm_pulse()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse.html#iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse "iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse") — Jasp-trace and compile to pulse-level circuits.

- [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") — embed native IQM QuantumOps in Qrisp circuits.

- [`quantum_op_to_qrisp_func()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func.html#iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func "iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func") — turn an IQM QuantumOp into a Qrisp gate function.

**Circuit conversion**

- [`qrisp_to_iqm_converter()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html#iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter "iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter") — convert transpiled Qrisp circuits to IQM format.

**QEC**

- [`DetectorExperiment`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment.html#iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment "iqm.qrisp_iqm.qec.detector_experiment.DetectorExperiment") — decorator for QEC experiments with Stim + PyMatching.

Subpackages and modules

|  |  |
|----|----|
| [`backends`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.html#module-iqm.qrisp_iqm.backends "iqm.qrisp_iqm.backends") | Backend infrastructure for running Qrisp circuits on IQM hardware. |
| [`custom_pulse_operations`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.custom_pulse_operations.html#module-iqm.qrisp_iqm.custom_pulse_operations "iqm.qrisp_iqm.custom_pulse_operations") | Examples of custom quantum operations implemented at pulse level. |
| [`extract_iqm_pulse_decorator`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.extract_iqm_pulse_decorator.html#module-iqm.qrisp_iqm.extract_iqm_pulse_decorator "iqm.qrisp_iqm.extract_iqm_pulse_decorator") | Jasp decorator for converting Qrisp Jasp-traceable functions into IQM quantum circuits. |
| [`iqm_converter`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.html#module-iqm.qrisp_iqm.iqm_converter "iqm.qrisp_iqm.iqm_converter") | Circuit converter for mapping Qrisp QuantumCircuits to IQM Circuits. |
| [`passes`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.html#module-iqm.qrisp_iqm.passes "iqm.qrisp_iqm.passes") | Transpilation passes for IQM-targeted circuit compilation. |
| [`pulse_operation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.html#module-iqm.qrisp_iqm.pulse_operation "iqm.qrisp_iqm.pulse_operation") | Using IQM Pulse quantum operations in Qrisp quantum circuits. |
| [`qec`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.qec.html#module-iqm.qrisp_iqm.qec "iqm.qrisp_iqm.qec") | Quantum Error Correction utilities. |
