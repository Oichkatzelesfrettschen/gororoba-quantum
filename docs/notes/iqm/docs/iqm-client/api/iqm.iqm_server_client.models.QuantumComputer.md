> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.QuantumComputer.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.QuantumComputer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 288f0165869aaf07204c833c51550fb7af2895637e71cac8559f2778f369421e.

# QuantumComputer

Module: [`iqm.iqm_server_client.models`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.html#module-iqm.iqm_server_client.models "iqm.iqm_server_client.models")

*class* iqm.iqm_server_client.models.QuantumComputer(*\**, *id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*, *alias: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *display_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *proxy_path: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: `PydanticBase`

Quantum computer attributes.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.iqm_server_client.models.QuantumComputer.model_config "iqm.iqm_server_client.models.QuantumComputer.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`id`](#iqm.iqm_server_client.models.QuantumComputer.id "iqm.iqm_server_client.models.QuantumComputer.id") | Unique ID of the quantum computer. |
| [`alias`](#iqm.iqm_server_client.models.QuantumComputer.alias "iqm.iqm_server_client.models.QuantumComputer.alias") | Quantum computer alias that can be used as a substitute for id in API calls. |
| [`display_name`](#iqm.iqm_server_client.models.QuantumComputer.display_name "iqm.iqm_server_client.models.QuantumComputer.display_name") | Quantum computer name that can be displayed in the UI. |
| [`proxy_path`](#iqm.iqm_server_client.models.QuantumComputer.proxy_path "iqm.iqm_server_client.models.QuantumComputer.proxy_path") | URL path prefix for station-proxied requests to this quantum computer. |

Methods

Parameters:  
- **id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **alias** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **display_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **proxy_path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

id*: UUID*  
Unique ID of the quantum computer.

alias*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Quantum computer alias that can be used as a substitute for id in API calls.

display_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Quantum computer name that can be displayed in the UI.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

proxy_path*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
URL path prefix for station-proxied requests to this quantum computer.

`None` if station proxy access is disabled or not permitted for this quantum computer. Absent entirely (defaults to `None`) when the server predates this field.

Inheritance

![Inheritance diagram of iqm.iqm_server_client.models.QuantumComputer](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-85252c8161aacd6d8d2a97b25d0b9187e08eff7c.png)
