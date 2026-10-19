> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 df93652efb757ea63c79afdaae12596b796757b3dc65070044ddc66c28e97fea.

# iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation

iqm.error_reduction_tools.twirling.twirling_modifiers.insert_twirling_pi_rotation(*registers*, *qubit*, *theta*, *phi*, *xi*)  
Insert a new π rotation (to the right) after the current R gate for twirling.

Implements the identity:

```
--[R(θ, φ)]--[R(π, ξ)]-- = --[R(θ+π, φ)]--[RZ(2(ξ - φ))]--
```

followed by commuting the resulting RZ through the now-pending R(π, …):

```
extra_phi ← ξ - 2(ξ - φ)
```

The π-rotation counter is incremented and the RZ remainder is stored in `virtual_z` for later absorption.

Parameters:  
- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers (`extra_pi`, `virtual_z`, `extra_phi` are updated).

- **qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit identifier.

- **theta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Polar rotation angle of the current gate.

- **phi** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase angle of the current gate.

- **xi** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase of the inserted π rotation.

Returns:  
Updated theta value.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
