> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Coupler.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Coupler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4871d7845bb9d640e6cdac5a2650676ad5dfaa94243ac12f9e6059dc4db33f76.

# Coupler

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* Coupler(*\**, *name*, *connections=()*)  
Bases: [`Component`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html#exa.common.qcm_data.chad_model.Component "exa.common.qcm_data.chad_model.Component")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.qcm_data.chad_model.Coupler.model_config "exa.common.qcm_data.chad_model.Coupler.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `name` |  |
| `connections` |  |

Methods

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **connections** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.Coupler](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-6b0d422a9ba811e59cbfa2defa72329426cd39bd.png)
