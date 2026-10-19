> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 911af0df8cf7a32285592627a5c652a540c241f7488a77ee749399bd699f22ac.

# quantum_ops

Full path: iqm.pulse.quantum_ops

Quantum operations.

Module Attributes

|  |  |
|----|----|
| [`QuantumOpTable`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOpTable.html#iqm.pulse.quantum_ops.QuantumOpTable "iqm.pulse.quantum_ops.QuantumOpTable") | Type for representing tables of known quantum operations, maps names of the ops to their definitions. |

Functions

|  |  |
|----|----|
| [`diff_cal_data`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.diff_cal_data.html#iqm.pulse.quantum_ops.diff_cal_data "iqm.pulse.quantum_ops.diff_cal_data")(cal_data, impl_parameters\[, ...\]) | Compare GateImplementation calibration data to its parameters. |
| [`validate_locus_calibration`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_locus_calibration.html#iqm.pulse.quantum_ops.validate_locus_calibration "iqm.pulse.quantum_ops.validate_locus_calibration")(cal_data, impl, ...) | Validates calibration for a particular gate implementation at particular locus. |
| [`validate_op_calibration`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_op_calibration.html#iqm.pulse.quantum_ops.validate_op_calibration "iqm.pulse.quantum_ops.validate_op_calibration")(calibration, ops) | Validates quantum operation calibration data against the known quantum operations. |

Classes

|  |  |
|----|----|
| [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") | Describes a native quantum operation type. |

Inheritance

![Inheritance diagram of iqm.pulse.quantum_ops](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-a15ad0a9698fceec046d49b4292c7190e793d866.png)
