> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementResults.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementResults.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8d77ca8f46baae6f37b271969a70b9828a8efee05cc01aac6d8dbc982d504f84.

# CircuitMeasurementResults

CircuitMeasurementResults  
Measurement results from a single circuit.

For each measurement operation in the circuit, maps the measurement key to the corresponding results. `results[key][shot][qubit_index]` is the result of measuring the `qubit_index`’th qubit in measurement operation `key` in the shot `shot`. The results are non-negative integers representing the computational basis state (for qubits, 0 or 1) that was the measurement outcome.

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[`int`](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]
