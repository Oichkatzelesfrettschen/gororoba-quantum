> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e9755827ed1e2794678c61a20a8e643da367952e7abaed921db0493bfdcbbc54.

# iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities

*class* iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities  
Bases: [`TypedDict`](https://docs.python.org/3.11/library/typing.html#typing.TypedDict "(in Python v3.11)")

Single-qubit characterization probabilities and standard deviations.

Attributes

|  |  |
|----|----|
| [`charact_data`](#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data") | Mapping from qubit name to its readout errors. |
| [`charact_data_std`](#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data_std "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data_std") | Mapping from qubit name to 2×2 matrix of binomial standard deviations for the entries of [`charact_data`](#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data"). |

Methods

charact_data*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), ...\], [dtype](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[float64\]\]\]*  
Mapping from qubit name to its readout errors.

This can be passed directly to `iqm.error_reduction_tools.rem.mitigation.ReadoutErrorMitigation.__init__`.

charact_data_std*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*  
Mapping from qubit name to 2×2 matrix of binomial standard deviations for the entries of [`charact_data`](#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.charact_data").
