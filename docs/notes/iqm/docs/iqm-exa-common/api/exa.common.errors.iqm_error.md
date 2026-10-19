> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2a9965d17de16f183690e47f7743243eeda9c265c6db54f27ff1ed2a77debcf6.

# iqm_error

Full path: exa.common.errors.iqm_error

Shared error definitions for the IQM ecosystem.

This module provides the unified exception hierarchy used by both client and server components. By centralizing these definitions in a shared library, we ensure that error states are communicated and handled consistently across the network.

## Architectural Context

1.  Symmetric Logic: Components like [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") or `Experiment` use these errors for local validation. Sharing them ensures that a Validation failure on the client feels identical to one on the server.

2.  Type Preservation: Server-side errors (e.g., [`InternalServerError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InternalServerError.html#exa.common.errors.iqm_error.InternalServerError "exa.common.errors.iqm_error.InternalServerError")) are included here so the client can deserialize them into specific Python types rather than generic catch-all exceptions.

3.  Wire Compatibility: These exceptions map directly to HTTP status codes and the `IQMServerError` Pydantic data model.

## Client-Relevant Errors

While all errors can be received from the server, the following are most commonly raised or handled specifically in client-side logic:

- [`ValidationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError"): Local input/parameter checks before transmission.

- [`NotFoundError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.NotFoundError.html#exa.common.errors.iqm_error.NotFoundError "exa.common.errors.iqm_error.NotFoundError"): Handling missing resources in lookups.

- [`ConflictError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ConflictError.html#exa.common.errors.iqm_error.ConflictError "exa.common.errors.iqm_error.ConflictError"): Managing state-machine or concurrency issues.

Exceptions

|  |  |
|----|----|
| [`AuthenticationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.AuthenticationError.html#exa.common.errors.iqm_error.AuthenticationError "exa.common.errors.iqm_error.AuthenticationError")(message, \*\[, ...\]) | Raised when the caller is not authenticated or credentials are missing. |
| [`BadGatewayError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.BadGatewayError.html#exa.common.errors.iqm_error.BadGatewayError "exa.common.errors.iqm_error.BadGatewayError")(message, \*\[, error_code, ...\]) | Raised when an invalid or unintelligible response is received from a dependency. |
| [`BadRequestError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.BadRequestError.html#exa.common.errors.iqm_error.BadRequestError "exa.common.errors.iqm_error.BadRequestError") | alias of [`InvalidOperationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InvalidOperationError.html#exa.common.errors.iqm_error.InvalidOperationError "exa.common.errors.iqm_error.InvalidOperationError") |
| [`CircuitExecutionError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitExecutionError.html#exa.common.errors.iqm_error.CircuitExecutionError "exa.common.errors.iqm_error.CircuitExecutionError")(message, \*\[, ...\]) | Raised when a failure occurs during the physical execution of a circuit. |
| [`CircuitTranspilationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitTranspilationError.html#exa.common.errors.iqm_error.CircuitTranspilationError "exa.common.errors.iqm_error.CircuitTranspilationError")(message, \*\[, ...\]) | Raised when a circuit cannot be transpiled, typically due to hardware constraints. |
| [`CircuitValidationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitValidationError.html#exa.common.errors.iqm_error.CircuitValidationError "exa.common.errors.iqm_error.CircuitValidationError")(message, \*\[, ...\]) | Raised when a circuit is well-formed but violates hardware or logical constraints. |
| [`ConflictError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ConflictError.html#exa.common.errors.iqm_error.ConflictError "exa.common.errors.iqm_error.ConflictError")(message, \*\[, error_code, ...\]) | Raised when an operation conflicts with the current state of the system. |
| [`DataSizeError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.DataSizeError.html#exa.common.errors.iqm_error.DataSizeError "exa.common.errors.iqm_error.DataSizeError")(message, \*\[, error_code, ...\]) | Raised when the provided data exceeds the allowed size limits. |
| [`EmptyComponentListError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.EmptyComponentListError.html#exa.common.errors.iqm_error.EmptyComponentListError "exa.common.errors.iqm_error.EmptyComponentListError")(message, \*\[, ...\]) | Raised when an empty list is given as components for running an experiment. |
| [`EngineInitialisationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.EngineInitialisationError.html#exa.common.errors.iqm_error.EngineInitialisationError "exa.common.errors.iqm_error.EngineInitialisationError")(\[message, log_level\]) | Raised when the station control engine fails to initialize. |
| [`ForbiddenError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ForbiddenError.html#exa.common.errors.iqm_error.ForbiddenError "exa.common.errors.iqm_error.ForbiddenError")(message, \*\[, error_code, ...\]) | Raised when the user is authenticated but lacks permission for the operation. |
| [`GatewayTimeoutError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.GatewayTimeoutError.html#exa.common.errors.iqm_error.GatewayTimeoutError "exa.common.errors.iqm_error.GatewayTimeoutError") | alias of [`OperationTimeoutError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.OperationTimeoutError.html#exa.common.errors.iqm_error.OperationTimeoutError "exa.common.errors.iqm_error.OperationTimeoutError") |
| [`IQMError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.IQMError.html#exa.common.errors.iqm_error.IQMError "exa.common.errors.iqm_error.IQMError")(message, \*\[, error_code, log_level\]) | Base exception for the IQM ecosystem logic. |
| [`InternalServerError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InternalServerError.html#exa.common.errors.iqm_error.InternalServerError "exa.common.errors.iqm_error.InternalServerError") | alias of [`InternalSystemError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InternalSystemError.html#exa.common.errors.iqm_error.InternalSystemError "exa.common.errors.iqm_error.InternalSystemError") |
| [`InternalSystemError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InternalSystemError.html#exa.common.errors.iqm_error.InternalSystemError "exa.common.errors.iqm_error.InternalSystemError")(message, \*\[, ...\]) | Raised when an unexpected internal failure occurs. |
| [`InvalidOperationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.InvalidOperationError.html#exa.common.errors.iqm_error.InvalidOperationError "exa.common.errors.iqm_error.InvalidOperationError")(message, \*\[, ...\]) | Raised when the operation parameters are invalid or the action is unsupported. |
| [`NotFoundError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.NotFoundError.html#exa.common.errors.iqm_error.NotFoundError "exa.common.errors.iqm_error.NotFoundError")(message, \*\[, error_code, ...\]) | Raised when a requested resource or data point was not found. |
| [`OperationTimeoutError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.OperationTimeoutError.html#exa.common.errors.iqm_error.OperationTimeoutError "exa.common.errors.iqm_error.OperationTimeoutError")(message, \*\[, ...\]) | Raised when an operation or a call to a dependency fails to complete in time. |
| [`PayloadTooLargeError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.PayloadTooLargeError.html#exa.common.errors.iqm_error.PayloadTooLargeError "exa.common.errors.iqm_error.PayloadTooLargeError") | alias of [`DataSizeError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.DataSizeError.html#exa.common.errors.iqm_error.DataSizeError "exa.common.errors.iqm_error.DataSizeError") |
| [`RateLimitError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.RateLimitError.html#exa.common.errors.iqm_error.RateLimitError "exa.common.errors.iqm_error.RateLimitError")(message, \*\[, error_code, ...\]) | Raised when the operation frequency exceeds the allowed limit in a given timeframe. |
| [`ServiceUnavailableError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ServiceUnavailableError.html#exa.common.errors.iqm_error.ServiceUnavailableError "exa.common.errors.iqm_error.ServiceUnavailableError") | alias of [`SystemUnavailableError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.SystemUnavailableError.html#exa.common.errors.iqm_error.SystemUnavailableError "exa.common.errors.iqm_error.SystemUnavailableError") |
| [`SystemUnavailableError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.SystemUnavailableError.html#exa.common.errors.iqm_error.SystemUnavailableError "exa.common.errors.iqm_error.SystemUnavailableError")(message, \*\[, ...\]) | Raised when a required system component is temporarily unable to operate. |
| [`TooManyRequestsError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.TooManyRequestsError.html#exa.common.errors.iqm_error.TooManyRequestsError "exa.common.errors.iqm_error.TooManyRequestsError") | alias of [`RateLimitError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.RateLimitError.html#exa.common.errors.iqm_error.RateLimitError "exa.common.errors.iqm_error.RateLimitError") |
| [`UnauthorizedError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.UnauthorizedError.html#exa.common.errors.iqm_error.UnauthorizedError "exa.common.errors.iqm_error.UnauthorizedError") | alias of [`AuthenticationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.AuthenticationError.html#exa.common.errors.iqm_error.AuthenticationError "exa.common.errors.iqm_error.AuthenticationError") |
| [`UnknownObservationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.UnknownObservationError.html#exa.common.errors.iqm_error.UnknownObservationError "exa.common.errors.iqm_error.UnknownObservationError")(message, \*\[, ...\]) | Raised when an observation name is syntactically correct but contains unknown elements. |
| [`UnknownSettingError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.UnknownSettingError.html#exa.common.errors.iqm_error.UnknownSettingError "exa.common.errors.iqm_error.UnknownSettingError")(message, \*\[, ...\]) | Raised when a SettingNode attribute is not found. |
| [`ValidationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError")(message, \*\[, error_code, ...\]) | Raised when data is well-formed but semantically invalid. |
