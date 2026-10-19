> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e6968b3488265ceab965ffff80f5f38f1bb4cac7b7be599167c02943d4c1266b.

# iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData

*class* iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData  
Bases: [`TypedDict`](https://docs.python.org/3.11/library/typing.html#typing.TypedDict "(in Python v3.11)")

Single- and double-twirled covariance output container.

Attributes

|  |  |
|----|----|
| [`covariance_matrices`](#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.covariance_matrices "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.covariance_matrices") | NxN covariance matrices keyed by error ID (0–3 for single-twirled, 0–2 for double-twirled). |
| [`error_labels`](#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.error_labels "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.error_labels") | List of `(error_id, description)` pairs providing human-readable labels for each error category. |
| [`measured_qubits`](#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.measured_qubits "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.measured_qubits") | Ordered list of qubit labels corresponding to the matrix row/column indices. |

Methods

covariance_matrices*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*  
NxN covariance matrices keyed by error ID (0–3 for single-twirled, 0–2 for double-twirled). Entry \[i, j\] is the covariance between the error/syndrome flip on qubit i and the syndrome flip on qubit j.

error_labels*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
List of `(error_id, description)` pairs providing human-readable labels for each error category.

measured_qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Ordered list of qubit labels corresponding to the matrix row/column indices.
