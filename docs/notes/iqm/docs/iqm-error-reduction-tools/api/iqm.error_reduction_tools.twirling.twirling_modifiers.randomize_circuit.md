> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f44b0ce5c2e0dcf26722c1dbf9e260e08dc5b1a1e28ac93018c00ef2ec5a182d.

# iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit

iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit(*circuit*, *rgen*, *drop_final_rz=True*, *readout_twirling=False*, *twirling_probabilities=None*, *fix_axes=False*)  
Randomize a quantum circuit using Poor Man’s Pauli Twirling (PMPT).

Produces a new circuit that is logically equivalent to the input (up to readout twirling characters recorded in `TwirledCircuit.rot_dict`), but with the θ angle of (arbitrarily/randomly) selected existing single-qubit R gates increased by π. The necessary bookkeeping for tracking the changes required downstream to maintain logical equivalence is handled by the TrackingRegisters class internally, so that no extra physical gates are added to the circuit.

**Algorithm overview** (gate-by-gate processing):

1.  **PRX (single-qubit R gate)** — handled by process_r_gate:

    1.  Absorb any pending virtual-Z and π rotations (stored in the TrackingRegisters) into the gate parameters (see take_care_of_pending_operations, absorb_pending_pi_rotation).

    2.  With probability `twirling_prob`, insert a π rotation (with random φ angle) after the gate and combine the two together (see insert_twirling_pi_rotation). On the last SQG of each qubit, the probability may be overridden to enforce a desired readout twirling basis.

2.  **CZ (two-qubit gate)** — handled by process_cz_gate: Propagate (pending) operations through the CZ gate, updating the TrackingRegisters.

3.  **Measure** — handled by process_measure_gate: Record the net readout twirling basis (‘I’ or ‘X’) from the parity of accumulated π rotations. Pending virtual-Z rotations are dropped. If the measured qubit has no SQG and readout twirling enforces ‘X’, a final PRX(π, 0) is added before measurement to ensure the correct readout twirling basis.

4.  **Barrier / Delay** — passed through unchanged.

The recorded readout twirling characters can later be used by `untwirl_counts` to recover the original measurement statistics.

Note

Right now, there is no support for MOVE gates. If the input circuit contains MOVE operations, a `ValueError` will be raised.

Parameters:  
- **circuit** ([*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")) – The quantum circuit to randomize.

- **rgen** ([*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – Random number generator for twirling decisions.

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, drop final virtual-Z rotations before measurements.

- **readout_twirling** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Controls readout twirling behavior: - `False`: no readout twirling (last SQG forced to even parity). - `True`: free twirling (no constraint on last SQG). - `dict`: maps qubit names to ‘I’ or ‘X’ to enforce a specific basis.

- **twirling_probabilities** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Probability of inserting a π rotation per SQG. Can be a single float (broadcast), a per-gate iterable, or None (default 0.5).

- **fix_axes** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, twirling π rotations use the same phase as the gate instead of a uniformly random phase.

Returns:  
A new TwirledCircuit with randomized gates and `rot_dict` set to the per-qubit readout twirling characters.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If twirling_probabilities length doesn’t match the number of single-qubit gates, or if an unsupported operation is encountered.

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If readout_twirling has an invalid type.

Return type:  
[*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")
