> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ExternalToken.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ExternalToken.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 65b425e15579e66deee21ef34b43aab92cab044e5fd32e21c2d9a0bc97b3e4e8.

# ExternalToken

Module: [`iqm.station_control.client.authentication`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html#module-iqm.station_control.client.authentication "iqm.station_control.client.authentication")

*class* ExternalToken(*token*)  
Bases: [`TokenProviderInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenProviderInterface.html#iqm.station_control.client.authentication.TokenProviderInterface "iqm.station_control.client.authentication.TokenProviderInterface")

Holds an external token

Methods

|  |  |
|----|----|
| [`close`](#iqm.station_control.client.authentication.ExternalToken.close "iqm.station_control.client.authentication.ExternalToken.close") | Close the authentication session. |
| [`get_token`](#iqm.station_control.client.authentication.ExternalToken.get_token "iqm.station_control.client.authentication.ExternalToken.get_token") | Return a valid access token. |

Parameters:  
**token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

get_token()  
Return a valid access token.

Raises:  
[**ClientAuthenticationError**](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") – acquiring the token failed

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

close()  
Close the authentication session.

Raises:  
[**ClientAuthenticationError**](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") – closing the session failed

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.station_control.client.authentication.ExternalToken](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-870f163df2715cdfdd664020961c4f7483f915c7.png)
