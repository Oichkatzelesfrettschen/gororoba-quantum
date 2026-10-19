> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Components.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Components.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 97727ad716dd3ba785adad6a1817e79e861840962e5d7230b2b84a04d4ca088a.

# Components

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* Components(*\**, *qubit=()*, *tunable_coupler=()*, *probe_line=()*, *launcher=()*, *computational_resonator=()*)  
Bases: [`ImmutableBaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.html#exa.common.qcm_data.immutable_base_model.ImmutableBaseModel "exa.common.qcm_data.immutable_base_model.ImmutableBaseModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| `all` |  |
| [`model_config`](#exa.common.qcm_data.chad_model.Components.model_config "exa.common.qcm_data.chad_model.Components.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `qubits` |  |
| `couplers` |  |
| `probe_lines` |  |
| `launchers` |  |
| `computational_resonators` |  |

Methods

|                   |     |
|-------------------|-----|
| `sort_components` |     |

Parameters:  
- **qubit** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Qubit*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Qubit.html#exa.common.qcm_data.chad_model.Qubit "exa.common.qcm_data.chad_model.Qubit")*,* *...\]*)

- **tunable_coupler** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Coupler*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Coupler.html#exa.common.qcm_data.chad_model.Coupler "exa.common.qcm_data.chad_model.Coupler")*,* *...\]*)

- **probe_line** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*ProbeLine*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.ProbeLine.html#exa.common.qcm_data.chad_model.ProbeLine "exa.common.qcm_data.chad_model.ProbeLine")*,* *...\]*)

- **launcher** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Launcher*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Launcher.html#exa.common.qcm_data.chad_model.Launcher "exa.common.qcm_data.chad_model.Launcher")*,* *...\]*)

- **computational_resonator** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*ComputationalResonator*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.ComputationalResonator.html#exa.common.qcm_data.chad_model.ComputationalResonator "exa.common.qcm_data.chad_model.ComputationalResonator")*,* *...\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.Components](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-8cc1ca831c1a8b0288bbced6f60e704f1d91060c.png)
