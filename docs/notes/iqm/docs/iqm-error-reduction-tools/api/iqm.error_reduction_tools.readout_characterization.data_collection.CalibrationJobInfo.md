> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bbae65f3a82e981a720b4aea2350c6b85e187ebff975cdfddf8a3d8836161c32.

# iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo

*class* iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo(*num_circuits*, *shots_per_circuit*, *prep_strings*, *qubits*, *context*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Metadata about a submitted calibration job.

Attributes

|  |  |
|----|----|
| [`num_circuits`](#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.num_circuits "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.num_circuits") | Total number of calibration circuits generated. |
| [`shots_per_circuit`](#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.shots_per_circuit "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.shots_per_circuit") | Number of shots allocated to each circuit. |
| [`prep_strings`](#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.prep_strings "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.prep_strings") | List of preparation strings corresponding to each circuit. |
| [`qubits`](#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.qubits "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.qubits") | List of qubits that were characterized. |
| [`context`](#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.context "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.context") | Execution context returned from the compiler. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **shots_per_circuit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **prep_strings** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **context** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

num_circuits*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Total number of calibration circuits generated.

shots_per_circuit*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Number of shots allocated to each circuit.

prep_strings*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
List of preparation strings corresponding to each circuit.

qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
List of qubits that were characterized.

context*: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*  
Execution context returned from the compiler.
