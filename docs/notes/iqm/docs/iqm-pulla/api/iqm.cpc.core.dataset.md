> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b8425a863790b2c67349628e0cbf5e353b75d3113d87d13e552c7c8ec4e38b17.

# dataset

Full path: iqm.cpc.core.dataset

Utilities related to xarray dataset handling.

Functions

|  |  |
|----|----|
| [`add_many_data_arrays`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.add_many_data_arrays.html#iqm.cpc.core.dataset.add_many_data_arrays "iqm.cpc.core.dataset.add_many_data_arrays")(ds, arrays) | Efficiently add multiple DataArrays to a Dataset in one shot. |
| [`annotate`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.annotate.html#iqm.cpc.core.dataset.annotate "iqm.cpc.core.dataset.annotate")(data\[, annotation, prefix\]) | Add parameter data to an array. |
| [`apply_along_coordinate`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.apply_along_coordinate.html#iqm.cpc.core.dataset.apply_along_coordinate "iqm.cpc.core.dataset.apply_along_coordinate")() | Apply a 1-dimensional function along a selected coordinate axis inside a Nd data array. |
| [`compute_1d_fit`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_1d_fit.html#iqm.cpc.core.dataset.compute_1d_fit "iqm.cpc.core.dataset.compute_1d_fit")(x_values, y_values, model, ...) | Compute and return the fit results for a 1-dimensional array of values. |
| [`compute_2d_fit`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_2d_fit.html#iqm.cpc.core.dataset.compute_2d_fit "iqm.cpc.core.dataset.compute_2d_fit")(x_values, y_values, z_values, ...) | Compute and return the fit results for a 2-dimensional array of values. |
| [`convert_2d_model`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.convert_2d_model.html#iqm.cpc.core.dataset.convert_2d_model "iqm.cpc.core.dataset.convert_2d_model")(model\[, ...\]) | Convert a function to a format usable with curve_fit, by flattening the model by the second dimension. |
| [`generate_fit_parameter`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.generate_fit_parameter.html#iqm.cpc.core.dataset.generate_fit_parameter "iqm.cpc.core.dataset.generate_fit_parameter")(data) | Construct a Parameter representing a fit to the given data array. |
| [`multifit_along_coordinates`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.multifit_along_coordinates.html#iqm.cpc.core.dataset.multifit_along_coordinates "iqm.cpc.core.dataset.multifit_along_coordinates")(\[returns, ...\]) | Extension of [`apply_along_coordinate()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.apply_along_coordinate.html#iqm.cpc.core.dataset.apply_along_coordinate "iqm.cpc.core.dataset.apply_along_coordinate") to two dimensions. |
| [`split_along_dimension`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.split_along_dimension.html#iqm.cpc.core.dataset.split_along_dimension "iqm.cpc.core.dataset.split_along_dimension")(data, dimension) | Slice an N-dimensional dataArray along specified dimension. |
| [`stack_along_dimension`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.stack_along_dimension.html#iqm.cpc.core.dataset.stack_along_dimension "iqm.cpc.core.dataset.stack_along_dimension")(data\[, dimension, stack\]) | Stack (that is, combine) all other dimensions other than the given dimension into a single dimension. |
| [`turn_variable_to_coordinate`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.turn_variable_to_coordinate.html#iqm.cpc.core.dataset.turn_variable_to_coordinate "iqm.cpc.core.dataset.turn_variable_to_coordinate")(dataset, ...) | Turns variable of xarray dataset into a coordinate. |
