> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c2d0170946dc1125360190388e8905b661a6de70f14bed781d4bc4d5fcc8d579.

# iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations

iqm.error_reduction_tools.twirling.twirling_modifiers.take_care_of_pending_operations(*registers*, *qubit*, *theta*, *phi*)  
Process pending Z and π-rotation operations before the current R gate.

Before a new R(θ, φ) gate is applied, any accumulated Z rotation and pending π rotation on that qubit must be commuted through. This function:

1.  **Z rotation**: absorbs the pending RZ(α) by shifting φ → φ - α, using:

    ```
    --[RZ(α)]--[R(θ, φ)]-- = --[R(θ, φ - α)]--[RZ(α)]--
    ```

2.  **Pending π rotation** (if odd count): delegates to absorb_pending_pi_rotation, which combines the pending R(π, ξ) with the current gate.

Parameters:  
- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers with `virtual_z`, `extra_pi`, `extra_phi`.

- **qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit identifier.

- **theta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Polar rotation angle of the current gate.

- **phi** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase angle of the current gate.

Returns:  
Tuple (theta, phi) with updated rotation parameters.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
