> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitTranspilationError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitTranspilationError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 08e8c5600fc4930958548fbb156e4a61df13d0c70f85fbb6c72f56ace7749aaa.

# exa.common.errors.iqm_error.CircuitTranspilationError

*exception* CircuitTranspilationError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when a circuit cannot be transpiled, typically due to hardware constraints.

This occurs if the circuit contains gates, connectivity, or operations (like invalid MOVE loci) that are not supported by the target architecture.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
