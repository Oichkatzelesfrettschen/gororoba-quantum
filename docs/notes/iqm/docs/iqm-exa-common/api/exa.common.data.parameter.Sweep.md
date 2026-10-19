> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9490743d5cce972bcb1cef6d5dbc2e4e633bf83d4654cf69c7bc14fa3d1a2f85.

# Sweep

Module: [`exa.common.data.parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html#module-exa.common.data.parameter "exa.common.data.parameter")

*class* Sweep(*\**, *parameter*, *data*)  
Bases: [`BaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html#exa.common.data.base_model.BaseModel "exa.common.data.base_model.BaseModel")

Base immutable class for sweeps.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.data.parameter.Sweep.model_config "exa.common.data.parameter.Sweep.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`parameter`](#exa.common.data.parameter.Sweep.parameter "exa.common.data.parameter.Sweep.parameter") | The Sweep represents changing the values of this Parameter. |
| [`data`](#exa.common.data.parameter.Sweep.data "exa.common.data.parameter.Sweep.data") | List of values for [`parameter`](#exa.common.data.parameter.Sweep.parameter "exa.common.data.parameter.Sweep.parameter") |

Methods

|                      |     |
|----------------------|-----|
| `validate_parameter` |     |

Parameters:  
- **parameter** ([*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter"))

- **data** (*Annotated\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.control.sweep.sweep_values.validate_sweep_values,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.control.sweep.sweep_values.serialize_sweep_values,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'frozen': True, 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': False}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

parameter*: [Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")*  
The Sweep represents changing the values of this Parameter.

data*: SweepValues*  
List of values for [`parameter`](#exa.common.data.parameter.Sweep.parameter "exa.common.data.parameter.Sweep.parameter")

Inheritance

![Inheritance diagram of exa.common.data.parameter.Sweep](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-4f9f33ab055153ea827b013e650c39fb66b8e880.png)
