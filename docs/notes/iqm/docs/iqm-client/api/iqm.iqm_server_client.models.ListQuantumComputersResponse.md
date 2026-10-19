> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.ListQuantumComputersResponse.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.ListQuantumComputersResponse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ce3162acf4c90a9886ebb37dd50a9da733de902a264d922103a4170ecee25979.

# ListQuantumComputersResponse

Module: [`iqm.iqm_server_client.models`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.html#module-iqm.iqm_server_client.models "iqm.iqm_server_client.models")

*class* iqm.iqm_server_client.models.ListQuantumComputersResponse(*\**, *quantum_computers: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumComputer](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.QuantumComputer.html#iqm.iqm_server_client.models.QuantumComputer "iqm.iqm_server_client.models.QuantumComputer")\]*)  
Bases: `PydanticBase`

Response of GET /v1/quantum-computers.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.iqm_server_client.models.ListQuantumComputersResponse.model_config "iqm.iqm_server_client.models.ListQuantumComputersResponse.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`quantum_computers`](#iqm.iqm_server_client.models.ListQuantumComputersResponse.quantum_computers "iqm.iqm_server_client.models.ListQuantumComputersResponse.quantum_computers") | List of available quantum computers. |

Methods

Parameters:  
**quantum_computers** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumComputer*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.QuantumComputer.html#iqm.iqm_server_client.models.QuantumComputer "iqm.iqm_server_client.models.QuantumComputer")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

quantum_computers*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumComputer](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.models.QuantumComputer.html#iqm.iqm_server_client.models.QuantumComputer "iqm.iqm_server_client.models.QuantumComputer")\]*  
List of available quantum computers.

Inheritance

![Inheritance diagram of iqm.iqm_server_client.models.ListQuantumComputersResponse](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-bc1dc92beaba974d1614b50b66432ff8a65faa1a.png)
