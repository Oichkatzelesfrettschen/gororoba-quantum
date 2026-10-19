> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 173a1e4d53e52a7b21e04c4d3b9bdd62950c6b0ec078b7c8e2394ddb2953b9bc.

# IQMServerClient

Module: [`iqm.iqm_server_client.iqm_server_client`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.html#module-iqm.iqm_server_client.iqm_server_client "iqm.iqm_server_client.iqm_server_client")

*class* iqm.iqm_server_client.iqm_server_client.IQMServerClient(*iqm_server_url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *token: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *tokens_file: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *client_signature: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *enable_opentelemetry: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *timeout: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 120.0*)  
Bases: `Serializable`

Shared functionality for clients communicating with the same IQM server.

Parameters:  
- **iqm_server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Remote IQM Server URL to connect to.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one.

- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Long-lived IQM token in plain text format.

- **tokens_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Path to a tokens file used for authentication.

- **client_signature** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – String that is added to the User-Agent header of requests sent to the server.

- **enable_opentelemetry** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, enable Jaeger/OpenTelemetry tracing.

- **timeout** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Timeout for the request in seconds.

Attributes

|  |  |
|----|----|
| [`api_version`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.api_version "iqm.iqm_server_client.iqm_server_client.IQMServerClient.api_version") | API version of the IQM Server API this client is using. |
| [`proxy_path`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.proxy_path "iqm.iqm_server_client.iqm_server_client.IQMServerClient.proxy_path") | Resolved URL path prefix for station-proxied requests to this quantum computer. |
| [`quantum_computer`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.quantum_computer "iqm.iqm_server_client.iqm_server_client.IQMServerClient.quantum_computer") | Human-readable alias of the quantum computer this client connects to. |

Methods

|  |  |
|----|----|
| [`clean_query_parameters`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.clean_query_parameters "iqm.iqm_server_client.iqm_server_client.IQMServerClient.clean_query_parameters") | Sanitize query parameters, defaulting 'invalid' to False if supported by the model. |
| [`deserialize`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.deserialize "iqm.iqm_server_client.iqm_server_client.IQMServerClient.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`deserialize_response`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.deserialize_response "iqm.iqm_server_client.iqm_server_client.IQMServerClient.deserialize_response") | Parse HTTP response text directly into Pydantic models. |
| [`get_about`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.get_about "iqm.iqm_server_client.iqm_server_client.IQMServerClient.get_about") | Get information about IQM Server. |
| [`get_health`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.get_health "iqm.iqm_server_client.iqm_server_client.IQMServerClient.get_health") | Get the status of the IQM Server. |
| [`prepare_request_kwargs`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.prepare_request_kwargs "iqm.iqm_server_client.iqm_server_client.IQMServerClient.prepare_request_kwargs") | Return the keyword arguments for a `requests` HTTP method. |
| [`send_request`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.send_request "iqm.iqm_server_client.iqm_server_client.IQMServerClient.send_request") | Send an HTTP request. |
| [`serialize`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize "iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize") | Serialize the object instance into a dictionary payload. |
| [`serialize_model`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize_model "iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize_model") | Serialize a Pydantic model into a JSON string. |
| [`serialize_query_params`](#iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize_query_params "iqm.iqm_server_client.iqm_server_client.IQMServerClient.serialize_query_params") | Serialize query parameters, skipping None values and empty dictionaries. |

serialize() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Serialize the object instance into a dictionary payload.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [IQMServerClient](#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient")  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*IQMServerClient*](#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient")

*property* api_version*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
API version of the IQM Server API this client is using.

*property* quantum_computer*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Human-readable alias of the quantum computer this client connects to.

*property* proxy_path*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Resolved URL path prefix for station-proxied requests to this quantum computer.

Raises:  
**ClientConfigurationError** – Station-proxied requests are not available for this quantum computer, e.g. due to missing permissions, or the station proxy feature not being enabled on the server.

get_about() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")  
Get information about IQM Server.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")

get_health() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Get the status of the IQM Server.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*static* serialize_model(*model: BaseModel*) → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Serialize a Pydantic model into a JSON string.

All Pydantic models should be serialized using this method, to keep the client behavior uniform.

Parameters:  
**model** (*BaseModel*) – Pydantic model to JSON-serialize.

Returns:  
Corresponding JSON string, may contain arbitrary Unicode characters.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

send_request(*http_method: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[...\], Response\]*, *url_path: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *\**, *headers: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *params: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *json_data: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *protobuf_data: [bytes](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → Response  
Send an HTTP request.

Parameters `json_str` and `octets` are mutually exclusive. The first non-None argument (in this order) will be used to construct the body of the request.

Parameters:  
- **http_method** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[...\],* *Response\]*) – HTTP method to use for the request, any of requests.\[post\|get\|put\|head\|delete\|patch\|options\].

- **url_path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – URL for the request.

- **headers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Additional HTTP headers for the request. Some may be overridden.

- **params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – HTTP query parameters to store in the query string of the request URL.

- **json_data** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – JSON string to store in the body, may contain arbitrary Unicode characters.

- **protobuf_data** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)") *\|* *None*) – Pre-serialized protobuf binary data to store in the body.

Returns:  
Response to the request.

Raises:  
**IQMError** – Request was not successful.

Return type:  
*Response*

*static* clean_query_parameters(*model: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*, *\*\*kwargs*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Sanitize query parameters, defaulting ‘invalid’ to False if supported by the model.

Parameters:  
**model** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

prepare_request_kwargs(*\**, *is_mutating: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*, *headers: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *params: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *json_data: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *protobuf_data: [bytes](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *timeout: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Return the keyword arguments for a `requests` HTTP method.

Parameters:  
- **is_mutating** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **headers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **json_data** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **protobuf_data** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)") *\|* *None*)

- **timeout** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*static* deserialize_response(*response: Response*, *model_class: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[TypePydanticBase \| ListModel\]*, *\**, *list_with_meta: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → TypePydanticBase \| ListWithMeta  
Parse HTTP response text directly into Pydantic models.

Logs metadata errors as warnings if list_with_meta is enabled.

Parameters:  
- **response** (*Response*)

- **model_class** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[TypePydanticBase* *\|* *ListModel\]*)

- **list_with_meta** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Return type:  
*TypePydanticBase* \| *ListWithMeta*

serialize_query_params(*params: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Serialize query parameters, skipping None values and empty dictionaries.

Parameters:  
**params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.iqm_server_client.iqm_server_client.IQMServerClient](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-0763971a41cc9b79e753b5681e256b6027567b76.png)
