> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d38903c0462b3047d027016a8c9a53eccbd0abe2f8a95471609e3d1bb53f102a.

# iqm.error_reduction_tools.readout_characterization.topologies

QPU topology utilities for readout error characterization.

This module provides topology data for IQM quantum processing units (QPUs).

For production use, coupler connectivity and probe-line groupings are fetched directly from the quantum computer via [`topology_from_qc()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.topology_from_qc "iqm.error_reduction_tools.utils.topology_utils.topology_from_qc").

Qubit grid positions are computed from the connectivity using [`compute_crystal_layout()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout.html#iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout "iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout").

Usage with data_collection and data_processing:  
```
>>> from iqm.error_reduction_tools.utils.topology_utils import topology_from_qc
>>> topology = topology_from_qc(client)
>>> qubit_list = topology.get_qubit_labels()
>>> # Use qubit_list with run_calibration_circuits or create_calibration_circuits
```

Functions

|  |  |
|----|----|
| [`get_qubits_by_control_line`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line.html#iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line "iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line")(topology\[, ...\]) | Get qubit labels grouped by control lines. |
| [`get_subset_positions`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions.html#iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions "iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions")(topology, qubit_labels) | Get positions for a subset of qubits from a topology. |

Classes

|  |  |
|----|----|
| [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology")(name, num_qubits\[, positions, ...\]) | Container for QPU topology information. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.readout_characterization.topologies](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-69982a0a8ee301aa6acbfaa0a04ed1d03f4e2739.png)
