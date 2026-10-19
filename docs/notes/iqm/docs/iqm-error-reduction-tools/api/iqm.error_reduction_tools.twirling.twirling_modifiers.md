> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 251c5f27067e66105f5bf47984150a394baa5d8ed4aba0805ee66f441c927b0a.

# iqm.error_reduction_tools.twirling.twirling_modifiers

Module for Poor Man’s Pauli Twirling (PMPT) and circuit manipulation utilities.

This module provides functions and classes for randomizing quantum circuits using PMPT and readout twirling techniques, as well as helpers for circuit analysis and gate manipulation. It is designed to work with Qiskit circuits transpiled to a restricted gate set (typically R and CZ gates), and supports readout twirling, Z rotation tracking, and logical equivalence checks. The main entry point is randomize_circuit, which returns a randomized circuit logically equivalent to the input (considering readout twirling and suppression of Z rotations before measurement).

Functions

|  |  |
|----|----|
| [`absorb_pending_pi_rotation`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation.html#iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation "iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation")(registers, qubit, ...) | Absorb a pending π rotation (from the left) into the current R gate. |
| [`insert_twirling_pi_rotation`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation.html#iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation "iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation")(registers, ...) | Insert a new π rotation (to the right) after the current R gate for twirling. |
| [`process_cz_gate`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate.html#iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate "iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate")(operation, new_circuit, ...) | Process a CZ gate: propagate pending π-rotation parity as Z kicks. |
| [`process_measure_gate`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate.html#iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate "iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate")(operation, new_circuit, ...) | Process a measurement gate: record readout twirling character and append. |
| [`process_r_gate`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate.html#iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate "iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate")(operation, twirled_circuit, ...) | Process an R gate: absorb pending operations, then optionally insert a twirling π rotation. |
| [`randomize_circuit`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit.html#iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit "iqm.error_reduction_tools.twirling.twirling_modifiers.randomize_circuit")(circuit, rgen\[, ...\]) | Randomize a quantum circuit using Poor Man's Pauli Twirling (PMPT). |
| [`take_care_of_pending_operations`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations.html#iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations "iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations")(registers, ...) | Process pending Z and π-rotation operations before the current R gate. |

Classes

|  |  |
|----|----|
| [`TrackingRegisters`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")(\[virtual_z, extra_phi, ...\]) | Container for tracking registers during circuit randomization. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.twirling.twirling_modifiers](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-aae5f44d692982950517eff435558a03ca6f8dcc.png)
