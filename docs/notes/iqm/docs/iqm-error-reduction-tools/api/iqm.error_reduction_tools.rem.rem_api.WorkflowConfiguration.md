> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ae505fd555974b84a8166e42b62b2de6e65e9b44b1ee175e1ae06d3a07f1188e.

# iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration

*class* iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration(*rec=\<factory\>*, *twirling=\<factory\>*, *shots=20000*, *nearest_probability=True*, *force_mitigation=False*, *compilation_options=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Configuration for the full readout error mitigation (REM) workflow.

Composes sub-configurations for readout error characterization and circuit twirling, plus workflow-level parameters.

Example:

```
config = WorkflowConfiguration(
    shots=40_000,
    twirling=TwirlingConfiguration(readout_twirl_strategy="LOCAL", seed=42),
)

# REM with custom compiler context (e.g. dynamical decoupling):
config_with_dd = WorkflowConfiguration(
    shots=40_000,
    twirling=TwirlingConfiguration(readout_twirl_strategy="LOCAL"),
    compilation_options={"DDStrategy": my_dd_strategy},
)
```

Attributes

|  |  |
|----|----|
| [`compilation_options`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.compilation_options "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.compilation_options") | Extra key-value pairs passed to the compiler context during circuit compilation. |
| [`force_mitigation`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.force_mitigation "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.force_mitigation") | Apply mitigation even when complexity exceeds threshold. |
| [`nearest_probability`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.nearest_probability "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.nearest_probability") | Project quasi-probabilities to nearest valid distribution. |
| [`shots`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.shots "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.shots") | Number of measurement shots per input circuit, distributed across that circuit's twirled instances. |
| [`rec`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.rec "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.rec") | Configuration for readout error characterization. |
| [`twirling`](#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.twirling "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.twirling") | Configuration for circuit twirling. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **rec** ([*RECConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration"))

- **twirling** ([*TwirlingConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration"))

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **nearest_probability** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **force_mitigation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **compilation_options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*)

rec*: [RECConfiguration](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration")*  
Configuration for readout error characterization.

twirling*: [TwirlingConfiguration](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration")*  
Configuration for circuit twirling.

shots*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 20000*  
Number of measurement shots per input circuit, distributed across that circuit’s twirled instances.

nearest_probability*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
Project quasi-probabilities to nearest valid distribution.

force_mitigation*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
Apply mitigation even when complexity exceeds threshold.

compilation_options*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Extra key-value pairs passed to the compiler context during circuit compilation.

Use this to activate compiler features such as dynamical decoupling.
