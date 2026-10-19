> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.AuthenticationError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.AuthenticationError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 05d058754e9538e4268e256ff3204448eedc2d064c4ef725a468cfe5571d6ea2.

# exa.common.errors.iqm_error.AuthenticationError

*exception* AuthenticationError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when the caller is not authenticated or credentials are missing.

The client must provide valid credentials or log in to access the resource.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
