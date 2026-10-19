> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_client.StationControlClient.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_client.StationControlClient.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a6c9eb887377fb50f1bba487e290f26ad3fb05aee54ea4b981be4e4ae5d6e8de.

# StationControlClient

Module: [`iqm.station_control.client.station_control_client`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_client.html#module-iqm.station_control.client.station_control_client "iqm.station_control.client.station_control_client")

*class* StationControlClient(*station_control_url*, *\**, *token=None*, *tokens_file=None*, *get_token_callback=None*, *client_signature=None*)  
Bases: [`Serializable`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.Serializable.html#iqm.station_control.interface.serializable.Serializable "iqm.station_control.interface.serializable.Serializable")

Client implementation for station control service REST API.

Parameters:  
- **station_control_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Remote station control service URL.

- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Long-lived authentication token in plain text format. If `token` is given no other user authentication parameters should be given.

- **tokens_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Path to a tokens file used for authentication. If `tokens_file` is given no other user authentication parameters should be given.

- **get_token_callback** (*Callable\[\[\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Callback function that returns an Authorization header containing a bearer token. If `get_token_callback` is given no other user authentication parameters should be given.

- **client_signature** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – String that is added to the User-Agent header of requests sent to the server.

Attributes

|  |  |
|----|----|
| [`version`](#iqm.station_control.client.station_control_client.StationControlClient.version "iqm.station_control.client.station_control_client.StationControlClient.version") | Version of the Station Control API this client is using. |

Methods

|  |  |
|----|----|
| `clean_query_parameters` |  |
| [`deserialize`](#iqm.station_control.client.station_control_client.StationControlClient.deserialize "iqm.station_control.client.station_control_client.StationControlClient.deserialize") | Reconstruct an instance from a dictionary payload. |
| `deserialize_response` |  |
| `get_about` |  |
| [`send_request`](#iqm.station_control.client.station_control_client.StationControlClient.send_request "iqm.station_control.client.station_control_client.StationControlClient.send_request") | Send an HTTP request. |
| [`serialize`](#iqm.station_control.client.station_control_client.StationControlClient.serialize "iqm.station_control.client.station_control_client.StationControlClient.serialize") | Serialize the object instance into a dictionary payload. |
| [`serialize_model`](#iqm.station_control.client.station_control_client.StationControlClient.serialize_model "iqm.station_control.client.station_control_client.StationControlClient.serialize_model") | Serialize a Pydantic model into a JSON string. |
| [`serialize_query_params`](#iqm.station_control.client.station_control_client.StationControlClient.serialize_query_params "iqm.station_control.client.station_control_client.StationControlClient.serialize_query_params") | Serialize query parameters, skipping None values and empty dictionaries. |

serialize()  
Serialize the object instance into a dictionary payload.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data*)  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*StationControlClient*](#iqm.station_control.client.station_control_client.StationControlClient "iqm.station_control.client.station_control_client.StationControlClient")

*property* version*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Version of the Station Control API this client is using.

serialize_query_params(*params*)  
Serialize query parameters, skipping None values and empty dictionaries.

Parameters:  
**params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

send_request(*http_method*, *url_path*, *\**, *headers=None*, *params=None*, *json_data=None*, *octets=None*, *timeout=600*)  
Send an HTTP request.

Parameters `json_data` and `octets` are mutually exclusive. The first non-None argument (in this order) will be used to construct the body of the request.

Parameters:  
- **http_method** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[...\],* *Response\]*) – HTTP method to use for the request, any of requests.\[post\|get\|put\|head\|delete\|patch\|options\].

- **url_path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – URL for the request.

- **headers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Additional HTTP headers for the request. Some may be overridden.

- **params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – HTTP query parameters to store in the query string of the request URL.

- **json_data** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – JSON string to store in the body, may contain arbitrary Unicode characters.

- **octets** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)") *\|* *None*) – Pre-serialized binary data to store in the body.

- **timeout** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Timeout for the request in seconds.

Returns:  
Response to the request.

Raises:  
**IQMError** – Request was not successful.

Return type:  
*Response*

*static* serialize_model(*model*)  
Serialize a Pydantic model into a JSON string.

All Pydantic models should be serialized using this method, to keep the client behavior uniform.

Parameters:  
**model** (*BaseModel*) – Pydantic model to JSON-serialize.

Returns:  
Corresponding JSON string, may contain arbitrary Unicode characters.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.station_control.client.station_control_client.StationControlClient](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-5556d8755ff9dd86993605601696612ff81762c8.png)
