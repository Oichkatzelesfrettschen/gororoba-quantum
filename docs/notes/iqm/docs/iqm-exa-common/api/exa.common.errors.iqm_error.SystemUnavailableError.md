> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.SystemUnavailableError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.SystemUnavailableError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 042dc2bc5f92f7b18ec8b07f8b2e981c0ccb9a931e0114e18d9e8cb93904a6dc.

# exa.common.errors.iqm_error.SystemUnavailableError

*exception* SystemUnavailableError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when a required system component is temporarily unable to operate.

This usually indicates the component is overloaded, initializing, or undergoing maintenance.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
