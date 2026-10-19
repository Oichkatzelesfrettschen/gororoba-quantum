> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1043d9bff12a7bf5792e77ed34f612e2cc4483efead039048b412ff5fcd29cc9.

# authentication

Full path: iqm.station_control.client.authentication

This module contains user authentication related classes and functions required by IQMClient.

Module Attributes

|  |  |
|----|----|
| [`AuthHeaderCallback`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.AuthHeaderCallback.html#iqm.station_control.client.authentication.AuthHeaderCallback "iqm.station_control.client.authentication.AuthHeaderCallback") | Function that returns an authorization header containing a bearer token. |

Classes

|  |  |
|----|----|
| [`ExternalToken`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ExternalToken.html#iqm.station_control.client.authentication.ExternalToken "iqm.station_control.client.authentication.ExternalToken") | Holds an external token |
| [`TokenManager`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenManager.html#iqm.station_control.client.authentication.TokenManager "iqm.station_control.client.authentication.TokenManager") | TokenManager manages the access token required for user authentication. |
| [`TokenProviderInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokenProviderInterface.html#iqm.station_control.client.authentication.TokenProviderInterface "iqm.station_control.client.authentication.TokenProviderInterface") | Interface to token provider |
| [`TokensFileReader`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.TokensFileReader.html#iqm.station_control.client.authentication.TokensFileReader "iqm.station_control.client.authentication.TokensFileReader") | Reads token from a file |

Exceptions

|  |  |
|----|----|
| [`ClientAuthenticationError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientAuthenticationError.html#iqm.station_control.client.authentication.ClientAuthenticationError "iqm.station_control.client.authentication.ClientAuthenticationError") | Something went wrong with user authentication. |
| [`ClientConfigurationError`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.authentication.ClientConfigurationError.html#iqm.station_control.client.authentication.ClientConfigurationError "iqm.station_control.client.authentication.ClientConfigurationError") | Wrong configuration provided. |

Inheritance

![Inheritance diagram of iqm.station_control.client.authentication](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-63e6696b2d8ed4e93934f385cdc706457cd7f819.png)
