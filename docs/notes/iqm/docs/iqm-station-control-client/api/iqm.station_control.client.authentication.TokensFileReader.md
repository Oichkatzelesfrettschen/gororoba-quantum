> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokensFileReader.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokensFileReader.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fc22c5012c5d601e52f96568ed3dfcc7825e440e5f4180009a974a437401a7a3.

# TokensFileReader

Module: [`iqm.station_control.client.authentication`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html#module-iqm.station_control.client.authentication "iqm.station_control.client.authentication")

*class* TokensFileReader(*tokens_file*)  
Bases: [`TokenProviderInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenProviderInterface.html#iqm.station_control.client.authentication.TokenProviderInterface "iqm.station_control.client.authentication.TokenProviderInterface")

Reads token from a file

Methods

|  |  |
|----|----|
| [`close`](#iqm.station_control.client.authentication.TokensFileReader.close "iqm.station_control.client.authentication.TokensFileReader.close") | Close the authentication session. |
| [`get_token`](#iqm.station_control.client.authentication.TokensFileReader.get_token "iqm.station_control.client.authentication.TokensFileReader.get_token") | Return a valid access token. |

Parameters:  
**tokens_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

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

![Inheritance diagram of iqm.station_control.client.authentication.TokensFileReader](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-d83939185a13333e002db002f4f5e904acf0ded1.png)
