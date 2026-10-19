> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d22e236ea1d59daa872f373e13ca303ebbd063d92e4438c3874b74bf12134a50.

# errors

Full path: iqm.cpc.compiler.errors

Definitions of error classes used to raise issues during circuit compilation.

Exceptions

|  |  |
|----|----|
| [`CalibrationError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.CalibrationError.html#iqm.cpc.compiler.errors.CalibrationError "iqm.cpc.compiler.errors.CalibrationError") | Required calibration data is missing, or unknown calibration data is encountered. |
| [`CircuitError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.CircuitError.html#iqm.cpc.compiler.errors.CircuitError "iqm.cpc.compiler.errors.CircuitError") | There is something wrong with the quantum circuit. |
| [`ClientError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.ClientError.html#iqm.cpc.compiler.errors.ClientError "iqm.cpc.compiler.errors.ClientError") | Client submitted a bad request, and needs to be notified. |
| [`CompilationPassError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.CompilationPassError.html#iqm.cpc.compiler.errors.CompilationPassError "iqm.cpc.compiler.errors.CompilationPassError") | There is something wrong with the compilation pass. |
| [`InsufficientContextError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.InsufficientContextError.html#iqm.cpc.compiler.errors.InsufficientContextError "iqm.cpc.compiler.errors.InsufficientContextError") | The context provided to the compilation pass does not contain all necessary fields. |
| [`SettingsConventionError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.SettingsConventionError.html#iqm.cpc.compiler.errors.SettingsConventionError "iqm.cpc.compiler.errors.SettingsConventionError") | While parsing Station Control settings, something breaks a structural or naming convention. |
| [`UnknownCircuitExecutionOptionError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.UnknownCircuitExecutionOptionError.html#iqm.cpc.compiler.errors.UnknownCircuitExecutionOptionError "iqm.cpc.compiler.errors.UnknownCircuitExecutionOptionError") | An unsupported value was used in circuit execution options. |
| [`UnknownHardwareComponentError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.UnknownHardwareComponentError.html#iqm.cpc.compiler.errors.UnknownHardwareComponentError "iqm.cpc.compiler.errors.UnknownHardwareComponentError") | Circuit contains a reference to an unknown hardware component. |
| [`UnknownLogicalQubitError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.UnknownLogicalQubitError.html#iqm.cpc.compiler.errors.UnknownLogicalQubitError "iqm.cpc.compiler.errors.UnknownLogicalQubitError") | A logical qubit in the circuit has not been defined in the qubit mapping. |
