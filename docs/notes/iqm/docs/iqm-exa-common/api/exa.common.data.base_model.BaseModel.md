> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.BaseModel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 850bdfe9e220e76a0de0e6f5577ab1ec2c72b1bb52bb8343c9bbe247956b3c70.

# BaseModel

Module: [`exa.common.data.base_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.base_model.html#module-exa.common.data.base_model "exa.common.data.base_model")

*class* BaseModel  
Bases: `BaseModel`

Pydantic base model to change the behavior of pydantic globally. Note that setting model_config in child classes will merge the configs rather than override this one. [https://docs.pydantic.dev/latest/concepts/config/#change-behaviour-globally](https://docs.pydantic.dev/latest/concepts/config/#change-behaviour-globally)

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.data.base_model.BaseModel.model_config "exa.common.data.base_model.BaseModel.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |

Methods

|  |  |
|----|----|
| [`model_copy`](#exa.common.data.base_model.BaseModel.model_copy "exa.common.data.base_model.BaseModel.model_copy") | Copy the model. |

&nbsp;

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'frozen': True, 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': False}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

&nbsp;

model_copy(*\**, *update=None*, *deep=False*)  
Copy the model.

Without `deep` or `update`, return `self` (immutable fast path); otherwise defer to Pydantic’s standard `model_copy`.

Parameters:  
- **update** ([*Mapping*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*)

- **deep** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

Inheritance

![Inheritance diagram of exa.common.data.base_model.BaseModel](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-c9f0cb1f073c070018cc83cc17677e22d571163a.png)
