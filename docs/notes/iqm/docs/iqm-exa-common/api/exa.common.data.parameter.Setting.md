> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 89e156e2f84e941cdfdb34768113d90d70bbfdd672b537b15ac13d96512d50e2.

# Setting

Module: [`exa.common.data.parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html#module-exa.common.data.parameter "exa.common.data.parameter")

*class* Setting(*parameter=None*, *value=None*, *read_only=False*, *path=''*, *source=None*)  
Bases: [`BaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel")

Physical quantity represented as a Parameter attached to a numerical value.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`element_indices`](#exa.common.data.parameter.Setting.element_indices "exa.common.data.parameter.Setting.element_indices") | Element-wise indices of the parameter in `self`. |
| [`label`](#exa.common.data.parameter.Setting.label "exa.common.data.parameter.Setting.label") | Label used as pretty identifier for display purposes, same as label of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter"). |
| [`model_config`](#exa.common.data.parameter.Setting.model_config "exa.common.data.parameter.Setting.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`name`](#exa.common.data.parameter.Setting.name "exa.common.data.parameter.Setting.name") | Name used as identifier, same as name of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter"). |
| [`parent_label`](#exa.common.data.parameter.Setting.parent_label "exa.common.data.parameter.Setting.parent_label") | Parent label of the parameter of `self`. |
| [`parent_name`](#exa.common.data.parameter.Setting.parent_name "exa.common.data.parameter.Setting.parent_name") | Parent name of the parameter of `self`. |
| [`source`](#exa.common.data.parameter.Setting.source "exa.common.data.parameter.Setting.source") | Return the source for this Setting's value. |
| [`unit`](#exa.common.data.parameter.Setting.unit "exa.common.data.parameter.Setting.unit") | SI unit of the [`value`](#exa.common.data.parameter.Setting.value "exa.common.data.parameter.Setting.value"), if applicable, same as unit of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter"). |
| [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter") | The parameter this Setting represents. |
| [`value`](#exa.common.data.parameter.Setting.value "exa.common.data.parameter.Setting.value") | Data value attached to the parameter, or None to indicate no value. |
| [`read_only`](#exa.common.data.parameter.Setting.read_only "exa.common.data.parameter.Setting.read_only") | Indicates if the attribute is read-only. |
| [`path`](#exa.common.data.parameter.Setting.path "exa.common.data.parameter.Setting.path") | Path in the settings tree (starting from the root `SettingNode`) for this setting. |

Methods

|  |  |
|----|----|
| [`create_element_parameter_for`](#exa.common.data.parameter.Setting.create_element_parameter_for "exa.common.data.parameter.Setting.create_element_parameter_for") | Utility for creating an element-wise parameter for a single value in a collection valued parameter. |
| [`diff_sets`](#exa.common.data.parameter.Setting.diff_sets "exa.common.data.parameter.Setting.diff_sets") | Return a one-sided difference between two sets of Settings, prioritising values in first. |
| [`fast_construct`](#exa.common.data.parameter.Setting.fast_construct "exa.common.data.parameter.Setting.fast_construct") | High-performance constructor that bypasses Pydantic validation. |
| `get_by_name` |  |
| `merge` |  |
| `remove_by_name` |  |
| `replace` |  |
| [`sweep`](#exa.common.data.parameter.Setting.sweep "exa.common.data.parameter.Setting.sweep") | Create a Sweep object that represents a 1d scan of this setting over the given values. |
| [`update`](#exa.common.data.parameter.Setting.update "exa.common.data.parameter.Setting.update") | Create a new setting object with updated value and source. |
| `validate_parameter_value_after` |  |
| [`with_path_name`](#exa.common.data.parameter.Setting.with_path_name "exa.common.data.parameter.Setting.with_path_name") | Copy of self with the parameter name replaced by the path name. |

Parameters:  
- **parameter** ([*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter") *\|* *None*)

- **value** (*SettingValue*)

- **read_only** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **source** (*SourceType*)

parameter*: [Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")*  
The parameter this Setting represents.

value*: SettingValue*  
Data value attached to the parameter, or None to indicate no value.

read_only*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Indicates if the attribute is read-only.

path*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Path in the settings tree (starting from the root `SettingNode`) for this setting.

*classmethod* fast_construct(*parameter*, *value*, *read_only=False*, *path=''*, *source=None*)  
High-performance constructor that bypasses Pydantic validation.

Parameters:  
- **parameter** ([*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter"))

- **value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

- **read_only** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **source** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

update(*value*, *source=None*)  
Create a new setting object with updated value and source.

Parameters:  
- **value** (*Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *\|* *None*) – New value for the setting.

- **source** (*None* *\|* [*BaseModel*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – New source for the setting.

Returns:  
Copy of `self` with modified properties.

Return type:  
[*Setting*](#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")

*property* name  
Name used as identifier, same as name of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter").

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'frozen': True, 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': False}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

*property* parent_name  
Parent name of the parameter of `self`.

*property* label  
Label used as pretty identifier for display purposes, same as label of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter").

*property* parent_label  
Parent label of the parameter of `self`.

*property* unit  
SI unit of the [`value`](#exa.common.data.parameter.Setting.value "exa.common.data.parameter.Setting.value"), if applicable, same as unit of [`parameter`](#exa.common.data.parameter.Setting.parameter "exa.common.data.parameter.Setting.parameter").

*property* element_indices*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Element-wise indices of the parameter in `self`.

*property* source*: [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| [BaseModel](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel") \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Return the source for this Setting’s value.

*static* diff_sets(*first*, *second*)  
Return a one-sided difference between two sets of Settings, prioritising values in first.

Parameters:  
- **first** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*Setting*](#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")*\]*) – Set whose values will be in the resulting diff.

- **second** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*Setting*](#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")*\]*) – Set that is compared to first.

Returns:  
A new set of Settings whose parameters are only found in first, and Settings in first whose values differ from their counterparts in second.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*Setting*](#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")\]

create_element_parameter_for(*indices*)  
Utility for creating an element-wise parameter for a single value in a collection valued parameter.

Parameters:  
**indices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The indices in the collection for which to create the element-wise parameter.

Returns:  
The element-wise parameter.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `self` is not collection-valued.

Return type:  
[*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")

with_path_name()  
Copy of self with the parameter name replaced by the path name.

Return type:  
[*Setting*](#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting")

sweep(*values*)  
Create a Sweep object that represents a 1d scan of this setting over the given values.

Parameters:  
**values** (*Annotated\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.control.sweep.sweep_values.validate_sweep_values,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.control.sweep.sweep_values.serialize_sweep_values,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*) – Sweep values.

Returns:  
The Sweep object.

Return type:  
[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep")

Inheritance

![Inheritance diagram of exa.common.data.parameter.Setting](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-b209a55fd81e2781aa6d13a4918a934799d4ce3c.png)
