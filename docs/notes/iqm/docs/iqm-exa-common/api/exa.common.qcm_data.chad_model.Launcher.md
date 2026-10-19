> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Launcher.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Launcher.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0e1312695f9949d38a7dd6bb59a18e8e2355d8af4ee8faeca8483b2dabe9b752.

# Launcher

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* Launcher(*\**, *name*, *connections=()*, *pin*, *function*)  
Bases: [`Component`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html#exa.common.qcm_data.chad_model.Component "exa.common.qcm_data.chad_model.Component")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.qcm_data.chad_model.Launcher.model_config "exa.common.qcm_data.chad_model.Launcher.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `pin` |  |
| `function` |  |
| `name` |  |
| `connections` |  |

Methods

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **connections** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

- **pin** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **function** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.Launcher](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-23908fa31026d892f8c60ef9347262a987d65239.png)
