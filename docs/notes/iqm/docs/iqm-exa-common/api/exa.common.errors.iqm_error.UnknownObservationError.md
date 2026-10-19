> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.UnknownObservationError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.UnknownObservationError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dacffc9dbc1663e72b859cbf94897df21b068a8c0e9c1a8287ed6d56bc8f3415.

# exa.common.errors.iqm_error.UnknownObservationError

*exception* UnknownObservationError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when an observation name is syntactically correct but contains unknown elements.

This indicates that while the format of the name is valid, the specific identifiers (e.g. keys or indices) do not exist in the current context.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
