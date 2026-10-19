> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.get_conventional_control_mapping.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.get_conventional_control_mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f1ac386c7a7523402674aaf4189b89875ffb1d4f22ae1edc4c6b3952344e1a77.

# iqm.cpc.core.config.get_conventional_control_mapping

iqm.cpc.core.config.get_conventional_control_mapping(*chip_topology*, *station_control_settings=None*)  
Add conventional controller mapping if `controller_mapping` is `"qpu_convention"`.

If the configuration is set to follow the standard QPU controller naming convention, extend the [`ExperimentConfiguration.controllers`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration.controllers "iqm.cpc.core.config.ExperimentConfiguration.controllers") and [`ExperimentConfiguration.component_groups`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration.component_groups "iqm.cpc.core.config.ExperimentConfiguration.component_groups") based on the convention. Components given explicitly have priority.

The convention is that components map their functions to controller names with the following pattern:

For qubits:

- `drive: <qubit_name>__drive`

- `flux: <qubit_name>__flux`

For couplers:

- `flux: <coupler_name>__flux`

For probelines:

- `readout: <probeline_name>__readout`

- `twpa: <probeline_name>__twpa`

Parameters:  
- **chip_topology** ([*ChipTopology*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)")) – The chip topology for the QPU.

- **station_control_settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)") *\|* *None*) – The station control settings. If provided, will validate the control mappings against them such that only the controllers that exist in the settings are included.

Returns:  
The controller mapping, a dictionary from QPU component names to their operations and associated controller  
names.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]
