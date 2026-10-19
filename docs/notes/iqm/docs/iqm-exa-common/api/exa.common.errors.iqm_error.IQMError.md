> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.IQMError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.IQMError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eac8fe8e6d2465dc1dcf8d8a424e282d9aa7f8dab6b0b7525def5e2fdfa29daa.

# exa.common.errors.iqm_error.IQMError

*exception* IQMError(*message*, *\**, *error_code=None*, *log_level=40*)  
Base exception for the IQM ecosystem logic.

This class serves as a universal functional representation of a failure within application logic. It is defined in ‘exa-common’ to provide a consistent error contract for all services, libraries, and clients, regardless of whether they communicate over a network or run locally.

IQMError is abstract and cannot be instantiated directly. Instead, specialized subclasses are used to categorize the failure (e.g., [`NotFoundError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.NotFoundError.html#exa.common.errors.iqm_error.NotFoundError "exa.common.errors.iqm_error.NotFoundError") or [`ValidationError`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError")).

While these exceptions are context-agnostic, the core subclasses are loosely equivalent to standard HTTP status codes. This enables a consistent transmission contract.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
