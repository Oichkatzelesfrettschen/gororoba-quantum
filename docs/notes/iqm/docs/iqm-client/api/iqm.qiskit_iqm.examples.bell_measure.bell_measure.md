> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.examples.bell_measure.bell_measure.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.examples.bell_measure.bell_measure.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf826bb50dab480dad7b34b6e636965b7dcb80b1b51b2e0c6dce774131848aae.

# iqm.qiskit_iqm.examples.bell_measure.bell_measure

iqm.qiskit_iqm.examples.bell_measure.bell_measure(*server_url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *token: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1000*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Execute a quantum circuit that prepares and measures a generalized Bell (aka GHZ) state.

Parameters:  
- **server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – URL of the IQM Server used for execution (e.g. “[https://resonance.iqm.tech/](https://resonance.iqm.tech/)”).

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one (e.g. “garnet”). `None` means connect to the default one.

- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – API token for authentication. If not given, uses `IQM_TOKEN`.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Requested number of shots.

Returns:  
Mapping of bitstrings representing qubit measurement results to counts for each result.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]
