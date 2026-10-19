> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf859cddf81bb3e5b78539f2052da1bee7ed44f199ac4b521447b94d6efd9260.

# config

Full path: iqm.cpc.core.config

Configuring `Experiment` instances.

Module Attributes

|  |  |
|----|----|
| [`Components`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.Components.html#iqm.cpc.core.config.Components "iqm.cpc.core.config.Components") | Same as [`ComponentGrouping`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping") but using a normal [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)"). |

Functions

|  |  |
|----|----|
| [`get_conventional_control_mapping`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.get_conventional_control_mapping.html#iqm.cpc.core.config.get_conventional_control_mapping "iqm.cpc.core.config.get_conventional_control_mapping")(chip_topology) | Add conventional controller mapping if `controller_mapping` is `"qpu_convention"`. |
| [`set_calibration_data_for_gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.set_calibration_data_for_gate_implementation.html#iqm.cpc.core.config.set_calibration_data_for_gate_implementation "iqm.cpc.core.config.set_calibration_data_for_gate_implementation")(...) | Add gate and/or implementation name and the corresponding calibration data to `gates`. |
| [`set_gate_implementation_as_default`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.set_gate_implementation_as_default.html#iqm.cpc.core.config.set_gate_implementation_as_default "iqm.cpc.core.config.set_gate_implementation_as_default")(...) | Sets the given implementation as the default implementation for the gate. |

Classes

|  |  |
|----|----|
| [`ComponentGroup`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGroup.html#iqm.cpc.core.config.ComponentGroup "iqm.cpc.core.config.ComponentGroup") | Collection of chip components, and the executor Controllers meant to control them. |
| [`ComponentGrouping`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping") | Utility class for handling the `run` argument `components`. |
| [`ComponentGroupingMode`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGroupingMode.html#iqm.cpc.core.config.ComponentGroupingMode "iqm.cpc.core.config.ComponentGroupingMode") | Types of structures for the components given as run arguments. |
| [`ExperimentConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration") | General configuration for `Experiment` objects. |
| [`ExperimentDefaultsConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentDefaultsConfiguration.html#iqm.cpc.core.config.ExperimentDefaultsConfiguration "iqm.cpc.core.config.ExperimentDefaultsConfiguration") | Configuration for a specific `Experiment` subclass. |
| [`SweepDefaultsConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.SweepDefaultsConfiguration.html#iqm.cpc.core.config.SweepDefaultsConfiguration "iqm.cpc.core.config.SweepDefaultsConfiguration") | Default sweep configuration. |

Inheritance

![Inheritance diagram of iqm.cpc.core.config](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-ea0bade4e641695d2e421ff52668f61b104461ac.png)
