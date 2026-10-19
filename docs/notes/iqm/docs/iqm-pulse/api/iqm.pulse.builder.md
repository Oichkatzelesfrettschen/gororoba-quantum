> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd1d237ed89506a7ea25f2e099ba62924146082a444b2816d7b92900b1840935.

# builder

Full path: iqm.pulse.builder

Tools for building instruction schedules.

Module Attributes

|  |  |
|----|----|
| [`DEFAULT_AGGREGATOR_NAME`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.DEFAULT_AGGREGATOR_NAME.html#iqm.pulse.builder.DEFAULT_AGGREGATOR_NAME "iqm.pulse.builder.DEFAULT_AGGREGATOR_NAME") | The name for the factorizable QuantumOp aggregator that uses the locus-wise default implementation for each of its sub implementations. |

Functions

|  |  |
|----|----|
| [`build_quantum_ops`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.build_quantum_ops.html#iqm.pulse.builder.build_quantum_ops "iqm.pulse.builder.build_quantum_ops")(ops) | Builds the table of known quantum operations. |
| [`load_config`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.load_config.html#iqm.pulse.builder.load_config "iqm.pulse.builder.load_config")(path) | Load quantum operation definitions and calibration data from a YAML config file. |
| [`validate_quantum_circuit`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.validate_quantum_circuit.html#iqm.pulse.builder.validate_quantum_circuit "iqm.pulse.builder.validate_quantum_circuit")(operations, op_table, \*) | Validate a sequence of circuit operations constituting a quantum circuit. |

Classes

|  |  |
|----|----|
| [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") | Specific quantum operation applied on a specific part of the QPU, e.g. in a quantum circuit. |
| [`ScheduleBuilder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder") | Builds instruction schedules out of quantum circuits or individual quantum operations. |

Inheritance

![Inheritance diagram of iqm.pulse.builder](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-095e885b76e5d96ca3c435491757fa355a9ab950.png)
