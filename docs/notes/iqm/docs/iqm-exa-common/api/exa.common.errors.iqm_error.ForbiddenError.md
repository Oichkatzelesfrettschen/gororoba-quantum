> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ForbiddenError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ForbiddenError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e206696d9ad55d362b94983fb1906256c24141d66c839fbecaed072b36fc0227.

# exa.common.errors.iqm_error.ForbiddenError

*exception* ForbiddenError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when the user is authenticated but lacks permission for the operation.

Logging in again will not help; the user’s account does not have the required scope.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
