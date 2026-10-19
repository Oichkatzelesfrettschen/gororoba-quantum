> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 71a09759a5dd1afea2c0033be468c385eed8ea5880a4a5d1d838198f2e1c86c9.

# iqm_server_client

Full path: iqm.iqm_server_client.iqm_server_client

Shared HTTP client implementation for remote IQM Server communication.

This module provides the [`IQMServerClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient"), which manages the underlying network transport, session, and authentication. It is composed inside both IQMServerExecutor and IQMServerStorage to prevent maintaining duplicate connections to the same server.

Classes

|  |  |
|----|----|
| [`IQMServerClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient") | Shared functionality for clients communicating with the same IQM server. |
| [`IQMServerClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient") | Shared functionality for clients communicating with the same IQM server. |

Inheritance

![Inheritance diagram of iqm.iqm_server_client.iqm_server_client](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-3483c65aab116eeef12576fede46642db31258d6.png)
