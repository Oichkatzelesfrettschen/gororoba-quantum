# IBM Quantum Heron & ISA Reference Documentation

> Transcribed reference copies of IBM Quantum documentation covering Heron architecture, ISA circuit requirements, native gates, timing, and dynamic execution.

| Document | Topic / Scope | Full Piece Link |
|---|---|---|
| [Processor types](processor-types.md) | Information on IBM Quantum hardware, Heron r1/r2/r3, and Nighthawk architectures. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/processor-types) |
| [View backend details](qpu-information.md) | List backends, native basis gates (cz, id, rz, sx, x, xslow), instruction sets, and calibration data. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/qpu-information) |
| [Introduction to transpilation](transpile.md) | Transpiling quantum circuits to conform to backend Instruction Set Architecture (ISA). | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/transpile) |
| [Transpile with pass managers](transpile-with-pass-managers.md) | Preset and custom pass managers for targeting backend ISA. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/transpile-with-pass-managers) |
| [Transpiler stages](transpiler-stages.md) | Six fundamental transpilation stages: init, layout, routing, translation, optimization, scheduling. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/transpiler-stages) |
| [Execute dynamic circuits](execute-dynamic-circuits.md) | Mid-circuit measurements (measure_2), fast resets, and classical feedforward (if_else) on Heron. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits) |
| [Fractional gates](fractional-gates.md) | Native RX and RZZ rotations on Heron, angle constraints, and error reporting. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/fractional-gates) |
| [Stretch](stretch.md) | Deferred timing resolution with stretch delays on Heron. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/stretch) |
| [Qiskit Runtime circuit timing](qiskit-runtime-circuit-timing.md) | Hardware circuit timing, scheduler timing, and timing differences from billed QPU time. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-circuit-timing) |
| [Repetition rate execution](repetition-rate-execution.md) | Repetition delays, execution order over shots, and state preparation error. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution) |
| [Calibration jobs](calibration-jobs.md) | Interleaved hourly calibration, CZ and RZZ calibration on Heron. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/calibration-jobs) |
| [Estimate job run time](estimate-job-run-time.md) | Predicting QPU run time, sub-job splits, and billing mechanisms. | [Online Guide](https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time) |
| [Heron r2 readout resonator](heron-r2-readout-resonator.md) | Readout durations of ibm_fez, ibm_kingston and ibm_marrakesh by backend version; public evidence for resonator linewidth, dispersive shift, ring-down and feed-forward latency, tagged by revision and device. | this repository |
| [Hardware controls audit](hardware-controls.md) | Every IBM control the repository reaches through qiskit-ibm-runtime 0.51.0 and REST: generated option inventory, live backend limits of ibm_fez, ibm_kingston and ibm_marrakesh, transpiler and billing controls, the configuration per workload type, and the gaps in live_run.py. | this repository |
| [Account access and job inventory](account-access.md) | Saved accounts, every read-only service surface on both accounts, failed-job billing and settlement, and the inventory freshness rule of core-196 and core-264. | this repository |
| [QPU time, calibration and submission mechanics](qpu-submission.md) | The 600 s rolling window, the approved-record binding of a `--submit`, calibration fingerprints, prediction reuse, qubit exclusion, the overflow account and the per-instance inventories. | this repository |
| [Learning: quantum teleportation](learning-quantum-teleportation.md) | The IBM Quantum Learning teleportation lesson: protocol, outcome-to-correction table and the reference-system extension. | [Online Lesson](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action/quantum-teleportation) |
