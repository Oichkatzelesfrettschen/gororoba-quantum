> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c72a12347e78136fde32f8d279a208270f31fc6d938aa25bcde4d214d938fcbb.

# Parameter

Module: [`exa.common.data.parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html#module-exa.common.data.parameter "exa.common.data.parameter")

*class* Parameter(*name*, *label=''*, *unit=''*, *data_type=DataType.FLOAT*, *collection_type=CollectionType.SCALAR*, *element_indices=None*)  
Bases: [`BaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel")

A basic data structure that represents a single variable.

The variable can be a high-level or low-level control knob of an instrument such as the amplitude of a pulse or a control voltage; a physical quantity such as resonance frequency; or an abstract concept like the number of averages in a measurement.

[`Setting`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting") combines Parameter with a numerical, boolean, or string value to represent a quantity.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.data.parameter.Parameter.model_config "exa.common.data.parameter.Parameter.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`parent_label`](#exa.common.data.parameter.Parameter.parent_label "exa.common.data.parameter.Parameter.parent_label") | Returns the parent label. |
| [`parent_name`](#exa.common.data.parameter.Parameter.parent_name "exa.common.data.parameter.Parameter.parent_name") | Returns the parent name. |
| [`name`](#exa.common.data.parameter.Parameter.name "exa.common.data.parameter.Parameter.name") | Parameter name used as identifier |
| [`label`](#exa.common.data.parameter.Parameter.label "exa.common.data.parameter.Parameter.label") | name |
| [`unit`](#exa.common.data.parameter.Parameter.unit "exa.common.data.parameter.Parameter.unit") | SI unit of the quantity, if applicable. |
| [`data_type`](#exa.common.data.parameter.Parameter.data_type "exa.common.data.parameter.Parameter.data_type") | Data type or a tuple of datatypes that this parameter accepts and validates. |
| [`collection_type`](#exa.common.data.parameter.Parameter.collection_type "exa.common.data.parameter.Parameter.collection_type") | Data format that this parameter accepts and validates. |
| [`element_indices`](#exa.common.data.parameter.Parameter.element_indices "exa.common.data.parameter.Parameter.element_indices") | For parameters representing a single value in a collection-valued parent parameter, this field gives the indices of that value. |

Methods

|  |  |
|----|----|
| [`build_data_array`](#exa.common.data.parameter.Parameter.build_data_array "exa.common.data.parameter.Parameter.build_data_array") | Attach Parameter information to a numerical array. |
| [`build_data_set`](#exa.common.data.parameter.Parameter.build_data_set "exa.common.data.parameter.Parameter.build_data_set") | Build an xarray Dataset, where the only DataArray is given by results and coordinates are given by variables. |
| [`create_element_parameter_for`](#exa.common.data.parameter.Parameter.create_element_parameter_for "exa.common.data.parameter.Parameter.create_element_parameter_for") | Utility for creating an element-wise parameter for a single value in a collection valued parameter. |
| [`fast_construct`](#exa.common.data.parameter.Parameter.fast_construct "exa.common.data.parameter.Parameter.fast_construct") | Fast construction alternative to \_\_init\_\_ from trusted serialized dict using model_construct. |
| [`get_cache_key`](#exa.common.data.parameter.Parameter.get_cache_key "exa.common.data.parameter.Parameter.get_cache_key") | Generates a hashable tuple from parameter metadata for cache lookups. |
| [`model_post_init`](#exa.common.data.parameter.Parameter.model_post_init "exa.common.data.parameter.Parameter.model_post_init") | This function is meant to behave like a BaseModel method to initialise private attributes. |
| [`set`](#exa.common.data.parameter.Parameter.set "exa.common.data.parameter.Parameter.set") | Create a Setting object with given value. |
| [`validate`](#exa.common.data.parameter.Parameter.validate "exa.common.data.parameter.Parameter.validate") | Validate that given value matches the [`data_type`](#exa.common.data.parameter.Parameter.data_type "exa.common.data.parameter.Parameter.data_type") and [`collection_type`](#exa.common.data.parameter.Parameter.collection_type "exa.common.data.parameter.Parameter.collection_type"). |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **data_type** ([*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType")*,* *...\]*)

- **collection_type** ([*CollectionType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType"))

- **element_indices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*)

name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Parameter name used as identifier

label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
name

Type:  
Parameter label used as pretty identifier for display purposes. Default

unit*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
SI unit of the quantity, if applicable.

data_type*: [DataType](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[DataType](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType"), ...\]*  
Data type or a tuple of datatypes that this parameter accepts and validates. One of [`DataType`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType"). Default: FLOAT.

collection_type*: [CollectionType](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType")*  
Data format that this parameter accepts and validates. One of [`CollectionType`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType"). Default: SCALAR.

element_indices*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
For parameters representing a single value in a collection-valued parent parameter, this field gives the indices of that value. If populated, the `self.name` and `self.label` will be updated in post init to include the indices (becoming `"<parent name>__<index0>__<index1>__...__<indexN>"` and `"<parent label> <indices>"` , respectively). The parent name can then be retrieved with `self.parent_name` and the parent label with `self.parent_label`.

*classmethod* fast_construct(*name*, *label=''*, *unit=''*, *data_type=DataType.FLOAT*, *collection_type=CollectionType.SCALAR*, *element_indices=None*, *\*\*kwargs*)  
Fast construction alternative to \_\_init\_\_ from trusted serialized dict using model_construct.

Does NOT call \_\_init\_\_, i.e. no validation, etc. Intended for already-normalized / trusted data.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **data_type** ([*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType")*,* *...\]* *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **collection_type** ([*CollectionType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **element_indices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*)

Return type:  
[*Parameter*](#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")

*static* get_cache_key(*name*, *label*, *unit*, *data_type*, *collection_type*, *element_indices*)  
Generates a hashable tuple from parameter metadata for cache lookups.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **data_type** ([*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType")*,* *...\]*)

- **collection_type** ([*CollectionType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType"))

- **element_indices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*)

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")

*property* parent_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Returns the parent name.

This None except in element-wise parameters where gives the name of the parent parameter.

*property* parent_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Returns the parent label.

This None except in element-wise parameters where gives the label of the parent parameter.

set(*value*)  
Create a Setting object with given value.

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Setting*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")

*static* build_data_set(*variables*, *data*, *attributes=None*, *extra_variables=None*)  
Build an xarray Dataset, where the only DataArray is given by results and coordinates are given by variables. The data is reshaped to correspond to the sizes of the variables. For example, `variables = [(par_x, [1,2,3]), (par_y: [-1, -2])]` will shape the data to 3-by-2 array. If there are not enough variables to reshape the data, remaining dimensions can be given by extra_variables. For example, `variables = [(par_x: [1,2,3])], extra_variables=[('y', 2)]` yields the same 3-by-2 data. `'y'` will then be a “dimension without coordinate” in xarray terms.

Parameters:  
- **variables** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Parameter*](#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]\]*) – Coordinates of the set.

- **data** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Parameter*](#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")*,* *Annotated\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.control.sweep.sweep_values.validate_sweep_values,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.control.sweep.sweep_values.serialize_sweep_values,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]\]*) – Data Parameter and associated data as a possible nested list.

- **attributes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – metadata to attach to the whole Dataset.

- **extra_variables** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – Valueless dimensions and their sizes.

Return type:  
[*Dataset*](https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html#xarray.Dataset "(in xarray v2026.9.0)")

validate(*value*)  
Validate that given value matches the [`data_type`](#exa.common.data.parameter.Parameter.data_type "exa.common.data.parameter.Parameter.data_type") and [`collection_type`](#exa.common.data.parameter.Parameter.collection_type "exa.common.data.parameter.Parameter.collection_type").

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

build_data_array(*data*, *dimensions=None*, *coords=None*, *metadata=None*)  
Attach Parameter information to a numerical array.

Given an array of numerical values, returns a corresponding `xr.DataArray` instance that gets its name, units, and dimension names (unless explicitly given) from the [`Parameter`](#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter") instance.

Parameters:  
- **data** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – numerical values

- **dimensions** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*\]* *\|* *None*) – names of the dimensions of `data`

- **coords** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – coordinates labeling the dimensions of `data`

- **metadata** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – additional `xr.DataArray.attrs`

Returns:  
corresponding DataArray

Return type:  
[*DataArray*](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.html#xarray.DataArray "(in xarray v2026.9.0)")

create_element_parameter_for(*indices*)  
Utility for creating an element-wise parameter for a single value in a collection valued parameter.

Parameters:  
**indices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The indices in the collection for which to create the element-wise parameter.

Returns:  
The element-wise parameter.

Raises:  
[**ValidationError**](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError") – If `self` is not collection-valued.

Return type:  
[*Parameter*](#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'frozen': True, 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': False}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

model_post_init(*context*, */*)  
This function is meant to behave like a BaseModel method to initialise private attributes.

It takes context as an argument since that’s what pydantic-core passes when calling it.

Parameters:  
- **self** ([*BaseModel*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel")) – The BaseModel instance.

- **context** (*Any*) – The context.

Return type:  
*None*

Inheritance

![Inheritance diagram of exa.common.data.parameter.Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-fe3ae5aecb29504b1552639e2f61f700d9ef551c.png)
