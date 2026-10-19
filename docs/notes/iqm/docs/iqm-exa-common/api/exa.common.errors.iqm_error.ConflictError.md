> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ConflictError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ConflictError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5931d5358bb530fc2218a7d055db1ac0d68e58c9f2d883b5c519e299aa56903d.

# exa.common.errors.iqm_error.ConflictError

*exception* ConflictError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when an operation conflicts with the current state of the system.

Typically used for duplicate submissions of unique data or state-machine violations.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
