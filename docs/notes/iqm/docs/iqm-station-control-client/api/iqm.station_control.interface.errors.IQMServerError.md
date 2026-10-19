> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.IQMServerError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 501819f7eea9d74e518795dd4222dc5cd33928303dfa06214e0e340c587c5090.

# IQMServerError

Module: [`iqm.station_control.interface.errors`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.errors.html#module-iqm.station_control.interface.errors "iqm.station_control.interface.errors")

*class* IQMServerError(*\**, *message*, *error_code=None*, *source*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Data transfer model for communicating error details over the REST API.

This model defines the structured JSON schema used to transport error details between components. It is used in both standard error response bodies (4xx/5xx) and within the ‘errors’ field of successful (200 OK) asynchronous job results.

This model acts as a data-carrying DTO (Data Transfer Object). High-level application code should map this model back into a raisable IQMError to represent the failure as a standard Python exception:

- **Domain Logic:** Errors carry a unique [`error_code`](#iqm.station_control.interface.errors.IQMServerError.error_code "iqm.station_control.interface.errors.IQMServerError.error_code") (a stable machine-readable string) and a [`message`](#iqm.station_control.interface.errors.IQMServerError.message "iqm.station_control.interface.errors.IQMServerError.message") (a human-readable description).

- **Network Transmission:** When crossing a network boundary (e.g., via REST), the exception is mapped to an HTTP status code. **Only the base category subclass (like :class:\`ValidationError\`) is recoverable on the receiving end.**

- **Information Preservation:** While the specific server-side class type (e.g., `UnknownSettingError`) is lost during transmission, the [`error_code`](#iqm.station_control.interface.errors.IQMServerError.error_code "iqm.station_control.interface.errors.IQMServerError.error_code") and [`message`](#iqm.station_control.interface.errors.IQMServerError.message "iqm.station_control.interface.errors.IQMServerError.message") attributes remain intact. This ensures the client receives full diagnostic information and can react to the specific failure code.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`detail`](#iqm.station_control.interface.errors.IQMServerError.detail "iqm.station_control.interface.errors.IQMServerError.detail") | Human-readable description of the error. |
| [`model_config`](#iqm.station_control.interface.errors.IQMServerError.model_config "iqm.station_control.interface.errors.IQMServerError.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`message`](#iqm.station_control.interface.errors.IQMServerError.message "iqm.station_control.interface.errors.IQMServerError.message") | Human-readable description of the error. |
| [`error_code`](#iqm.station_control.interface.errors.IQMServerError.error_code "iqm.station_control.interface.errors.IQMServerError.error_code") | Optional machine-readable identifier for programmatic error handling. |
| [`source`](#iqm.station_control.interface.errors.IQMServerError.source "iqm.station_control.interface.errors.IQMServerError.source") | Originating component or service of the error. |

Methods

|  |  |
|----|----|
| [`ensure_compatibility`](#iqm.station_control.interface.errors.IQMServerError.ensure_compatibility "iqm.station_control.interface.errors.IQMServerError.ensure_compatibility") | Harmonizes differences between various service response formats. |
| [`from_exception`](#iqm.station_control.interface.errors.IQMServerError.from_exception "iqm.station_control.interface.errors.IQMServerError.from_exception") | Factory method to create a DTO from an Exception. |
| [`raise_exception`](#iqm.station_control.interface.errors.IQMServerError.raise_exception "iqm.station_control.interface.errors.IQMServerError.raise_exception") | Maps the error data to the appropriate IQMError and raises it. |

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **source** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['iqm-server',* *'iqm-station-control'\]* *\|* *str*)

message*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Human-readable description of the error.

error_code*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Optional machine-readable identifier for programmatic error handling.

source*: Source*  
Originating component or service of the error.

*property* detail*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Human-readable description of the error.

*classmethod* ensure_compatibility(*data*)  
Harmonizes differences between various service response formats.

This handles both legacy fields (detail -\> message) and transitional requirements (defaulting missing ‘source’ for older server versions).

Parameters:  
**data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")

raise_exception(*status_code*)  
Maps the error data to the appropriate IQMError and raises it.

Parameters:  
**status_code** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
[*NoReturn*](https://docs.python.org/3.11/library/typing.html#typing.NoReturn "(in Python v3.11)")

*classmethod* from_exception(*exception*, *\**, *source*)  
Factory method to create a DTO from an Exception.

Parameters:  
- **exception** ([*Exception*](https://docs.python.org/3.11/library/exceptions.html#Exception "(in Python v3.11)"))

- **source** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['iqm-server',* *'iqm-station-control'\]* *\|* *str*)

Return type:  
[*IQMServerError*](#iqm.station_control.interface.errors.IQMServerError "iqm.station_control.interface.errors.IQMServerError")

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.errors.IQMServerError](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-be7c201114f074533750a84a42150fe2ea5f2352.png)
