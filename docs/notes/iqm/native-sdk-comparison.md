# IQM native client and transpiler against our case bytes

Three offline tools compare the iqm-client 34.0.3 stack (interpreter `gq-max`, exploratory) with the retained
Garnet A_5 complex-kernel case `a5-complex-kernel-garnet` and its run
`2026-11-28T034418Z-garnet-a5-complex-kernel-garnet-kernel` (branch `a5-iqm-complex-kernel-case`). None sends a
request. Our code stays authoritative for approval binding, digests and records.

## Native transpile: `scripts/iqm_native_compile.py`

The tool reads each case circuit (native prx, cz, measure on QB names) back into Qiskit with
`deserialize_instructions`, runs `transpile_to_IQM` (optimization level 1) against the retained dynamic architecture
of calibration set a8782702 and serializes the result. The case writes one measure key `m` for all measured qubits;
the bridge reads keys as `creg_len_index_clbit`, so the tool splits each measure into one per qubit under
`m_<n>_0_<i>`.

| 80 circuits | prx | cz | measure | move |
|---|---|---|---|---|
| case bytes | 4264 | 1296 | 264 | 0 |
| native transpile | 2356 | 1296 | 264 | 0 |

The native single-qubit merge removes 44.7 percent of the prx instructions and changes no cz, measure or move
count (Garnet has no resonator). The compiled variant is a different byte string, so it would be a new case with a new
digest; equivalence of the merged circuits (unitary or simulated outcome agreement, and the frame conventions of
prx phases) is not checked here and is the next step before any use.

## Offline readout mitigation: `scripts/iqm_rem_offline.py`

The tool inverts the selector qubit's readout channel with the heralded error rates of the run's calibration metrics
(QB8: e(0 to 1) 0.0002, e(1 to 0) 0.0115) and reruns the preregistered tally and decision on the corrected zero
counts. `iqm-error-reduction` and mthree are not installed, so the inversion is written out. N_c per operand,
raw against corrected: s016 15.9391, s124 4.8344, s412 12.1205, s808 8.1297, with deltas below 2e-15. The estimator
is a ratio of arm differences, and a readout channel is affine in the zero fraction, so inversion scales every
difference by one common factor, 1 / (1 - e01 - e10), that cancels in the ratio. N_c is invariant to this readout
mitigation by construction. The standard errors in the corrected analysis shrink slightly, which is an artifact of
applying the binomial formula to inverted counts (the true variance grows by the same factor); the corrected
standard errors carry no weight. The preregistered analysis keeps its verdict.

## Transport bytes: `scripts/iqm_transport_capture.py`

The tool records our wire bytes through a recording transport and builds the `RunRequest` that
`IQMClient.create_run_request` would build, serialized by the client's own `_serialize_model` (the request wrapper
only adds headers).

| Form of the same 80-circuit body | bytes | sha256 |
|---|---|---|
| our recorded `body_sha256` (`json.dumps(sort_keys=True)`) | n/a | 5c408519... |
| our wire bytes (`json.dumps`, insertion order) | 464636 | 1114728f... |
| iqm-client wire bytes (`model_dump_json`) | 541790 | 2d689019... |

Findings. First, the recorded digest binds a canonical sorted-key form of the body and not the bytes our submitter
sends: the two differ in key order, so a replay that hashes the wire bytes does not reproduce the receipt. Second,
iqm-client sends different bytes for the same circuits, shots and options: it names eight more request fields at
their defaults (`dd_mode`, `dd_strategy`, `max_circuit_duration_over_t2`, `move_gate_validation` strict,
`move_gate_frame_tracking`, `move_validation_mode`, `move_gate_frame_tracking_mode`, `qubit_mapping`) and encodes
compactly in model order. The circuits agree as data. Moving submission to iqm-client therefore keeps the digest
binding only if the receipt keeps hashing the canonical body and a second field records the transport hash of the
bytes actually posted; the defaults it adds (strict move validation, DD disabled) are explicit, but they are
server-visible request fields the approval did not name. Decision for the owner: whether the receipt adds the transport hash.
