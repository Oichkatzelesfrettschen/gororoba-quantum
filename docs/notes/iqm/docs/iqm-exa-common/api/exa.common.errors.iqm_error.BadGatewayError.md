> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.BadGatewayError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.BadGatewayError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c85d5f61daba16fb85cbec55f3eb4092b2be1f5fa631bb0d912990353f745f67.

# exa.common.errors.iqm_error.BadGatewayError

*exception* BadGatewayError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when an invalid or unintelligible response is received from a dependency.

This dependency could be an upstream service, a database, or an external hardware controller.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
