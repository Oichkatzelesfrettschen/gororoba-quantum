> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a3ff2d36ea8ecf58f3d7519103bbf90c652c82cff86d7d1245e165278b4ff361.

# validation

Full path: iqm.pulse.validation

Validation of playlists and instructions schedules.

Module Attributes

|  |  |
|----|----|
| [`OperationClass`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.OperationClass.html#iqm.pulse.validation.OperationClass "iqm.pulse.validation.OperationClass") | Union of operation classes station-control actually uses, across AWG and readout controllers. |

Functions

|  |  |
|----|----|
| [`validate_channel_and_instrument_compatibility`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_channel_and_instrument_compatibility.html#iqm.pulse.validation.validate_channel_and_instrument_compatibility "iqm.pulse.validation.validate_channel_and_instrument_compatibility")(...) | Validate that the given control channel and its contents are compatible with the instrument. |
| [`validate_playlist_compatibility`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_playlist_compatibility.html#iqm.pulse.validation.validate_playlist_compatibility "iqm.pulse.validation.validate_playlist_compatibility")(playlist, ...) | Validate that the given playlist is compatible with the control instrument constraints. |

Exceptions

|  |  |
|----|----|
| [`InvalidInstructionError`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.InvalidInstructionError.html#iqm.pulse.validation.InvalidInstructionError "iqm.pulse.validation.InvalidInstructionError")(instruction, channel) | Raised when an instruction is malformed or not supported by the target instrument. |
| [`PlaylistValidationError`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.PlaylistValidationError.html#iqm.pulse.validation.PlaylistValidationError "iqm.pulse.validation.PlaylistValidationError")(channel\[, issue_string\]) | Raised when Playlist validation fails. |
