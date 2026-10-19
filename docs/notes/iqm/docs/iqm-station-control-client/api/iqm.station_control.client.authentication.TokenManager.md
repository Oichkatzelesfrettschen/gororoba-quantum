> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenManager.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenManager.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad71310e92aeeae2d5095b4ef1a07e5462fc7f38de906bdc78ca6a95e8b6fd5c.

# TokenManager

Module: [`iqm.station_control.client.authentication`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html#module-iqm.station_control.client.authentication "iqm.station_control.client.authentication")

*class* TokenManager(*token=None*, *tokens_file=None*, *auth_header_callback=None*, *\**, *use_env_vars=True*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

TokenManager manages the access token required for user authentication.

Parameters:  
- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Long-lived IQM token in plain text format.

- **tokens_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Path to a tokens file used for authentication.

- **auth_header_callback** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Callback function that returns an Authorization header containing a bearer token.

- **use_env_vars** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, the first two parameters can also be read from the environment variables `IQM_TOKEN` and `IQM_TOKENS_FILE`, respectively. Environment variables can not be mixed with initialisation arguments.

At most one auth parameter should be given.

Methods

|  |  |
|----|----|
| [`close`](#iqm.station_control.client.authentication.TokenManager.close "iqm.station_control.client.authentication.TokenManager.close") | Close the configured token provider. |
| [`get_auth_header_callback`](#iqm.station_control.client.authentication.TokenManager.get_auth_header_callback "iqm.station_control.client.authentication.TokenManager.get_auth_header_callback") | Return a callback providing an Authorization header, or None if we cannot provide it. |
| [`time_left_seconds`](#iqm.station_control.client.authentication.TokenManager.time_left_seconds "iqm.station_control.client.authentication.TokenManager.time_left_seconds") | Check how much time is left until the token expires. |

*static* time_left_seconds(*token*)  
Check how much time is left until the token expires.

Returns:  
Time left on token in seconds.

Parameters:  
**token** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

get_auth_header_callback()  
Return a callback providing an Authorization header, or None if we cannot provide it.

Return type:  
[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[\], [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| *None*

close()  
Close the configured token provider.

Returns:  
True if closing was successful

Raises:  
[**ClientAuthenticationError**](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") – closing failed

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.station_control.client.authentication.TokenManager](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-52b7a7977d9461c93f9562ed533edffaa2360417.png)
