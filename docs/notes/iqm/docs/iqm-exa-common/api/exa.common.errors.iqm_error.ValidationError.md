> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8e62b2b4be8c6304afb8731ef3791e04b10be42c4d879d222ea93248f9e02e27.

# exa.common.errors.iqm_error.ValidationError

*exception* ValidationError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when data is well-formed but semantically invalid.

Used for invalid input values, range violations, or business logic failures.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
