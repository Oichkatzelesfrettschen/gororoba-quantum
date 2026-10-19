> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenProviderInterface.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenProviderInterface.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 55597773cd59d465bf8ebb888442100f4372145d5c64512de35e7fecda8fcdcc.

# TokenProviderInterface

Module: [`iqm.station_control.client.authentication`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html#module-iqm.station_control.client.authentication "iqm.station_control.client.authentication")

*class* TokenProviderInterface  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

Interface to token provider

Methods

|  |  |
|----|----|
| [`close`](#iqm.station_control.client.authentication.TokenProviderInterface.close "iqm.station_control.client.authentication.TokenProviderInterface.close") | Close the authentication session. |
| [`get_token`](#iqm.station_control.client.authentication.TokenProviderInterface.get_token "iqm.station_control.client.authentication.TokenProviderInterface.get_token") | Return a valid access token. |

*abstractmethod* get_token()  
Return a valid access token.

Raises:  
[**ClientAuthenticationError**](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") – acquiring the token failed

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

*abstractmethod* close()  
Close the authentication session.

Raises:  
[**ClientAuthenticationError**](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") – closing the session failed

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.station_control.client.authentication.TokenProviderInterface](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-af76a094009166355d450646c7c1b1308db01b99.png)
