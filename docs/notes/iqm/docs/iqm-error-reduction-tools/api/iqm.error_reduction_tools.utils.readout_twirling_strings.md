> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.readout_twirling_strings.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.readout_twirling_strings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 02acedfcf4a2021be6dae9d0da23ab339106d069d4dc005fbcc37bfe0ce6170c.

# iqm.error_reduction_tools.utils.readout_twirling_strings

Readout twirling string generation utilities.

This module provides helper functions to build per-qubit `I/X` twirling strings used by REM workflows. The supported strategies are:

- `HADAMARD`: Ensure balanced coverage of `I/X` combinations across all qubits PAIRS.  
  Requires up to `2n` strings for `n` active qubits.

- `MINIMAL`: Two alternating strings.

- `LOCAL`: 4 strings balancing nearest-neighbor pair combinations.

- `PROBELINES`: `LOCAL` strings plus probe-line specific Hadamard masks.  
  The number of strings should be a multiple of 4, ideally four times the smaller power of 2 greater than the largest control line length. This ensures balanced coverage across all pairs of qubits connected by a control line.

Note

All strategies ensure that, for each qubit, the number of `I` and `X` operators is equal.

Functions

|  |  |
|----|----|
| [`generate_rot_strings`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings.html#iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings "iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings")(\[qpu_topology, ...\]) | Generate readout twirling strings for the requested strategy. |
