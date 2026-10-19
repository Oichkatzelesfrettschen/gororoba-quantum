> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1c914572286b3d96f69080843113598169c120c27dd81905822e9ea3e0924eb6.

# iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData

*class* iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData  
Bases: [`TypedDict`](https://docs.python.org/3.11/library/typing.html#typing.TypedDict "(in Python v3.11)")

State-dependent covariance output container.

Attributes

|  |  |
|----|----|
| [`covariance_matrices`](#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.covariance_matrices "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.covariance_matrices") | NxN covariance matrices keyed by error ID pairs (error_i, error_j). |
| [`error_labels`](#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.error_labels "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.error_labels") | List of `((error_i, error_j), description)` pairs providing human-readable labels for each error pair. |
| [`measured_qubits`](#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.measured_qubits "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.measured_qubits") | Ordered list of qubit labels corresponding to the matrix row/column indices. |

Methods

covariance_matrices*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*  
NxN covariance matrices keyed by error ID pairs (error_i, error_j). Entry \[m, n\] is the covariance between error type error_i on qubit m and error type error_j on qubit n for a key (error_i, error_j), conditioned on the respective preparation states of both qubits.

error_labels*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
List of `((error_i, error_j), description)` pairs providing human-readable labels for each error pair.

measured_qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Ordered list of qubit labels corresponding to the matrix row/column indices.
