> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6425a6fc682032a5bd1dbed55680c1ea950cf18af36e734146eaeb9b325d09bd.

# iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation

iqm.error_reduction_tools.twirling.twirling_modifiers.absorb_pending_pi_rotation(*registers*, *qubit*, *theta*, *phi*)  
Absorb a pending π rotation (from the left) into the current R gate.

Implements the identity:

```
--[R(π, ξ)]--[R(θ, φ)]-- = --[R(θ+π, 2ξ - φ)]--[RZ(2(φ - ξ))]--
```

The pending π rotation (with phase `extra_phi`) is combined with the current gate R(θ, φ). The resulting RZ remainder is folded into `virtual_z`, the π-rotation counter is incremented (making it even again), and `extra_phi` is reset.

Parameters:  
- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers (`extra_phi`, `extra_pi`, `virtual_z` are updated).

- **qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit identifier.

- **theta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Polar rotation angle of the current gate.

- **phi** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase angle of the current gate.

Returns:  
Tuple (theta, phi) with updated rotation parameters.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
