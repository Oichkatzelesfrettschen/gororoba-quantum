> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/rpchandler.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/rpchandler.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 bd07bee35ce3a15119f191c1a9bab27010f028e834383f31d826f34f080ebd9b.

# RPCHandler

Note

This class has been moved to `perceval.providers.quandela.rpc_handler`. It should not be used on its own anymore, but is only used internally in the [QuandelaCommunicationLayer](https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html#quandelacommunicationlayer).

A `RPCHandler` (RPC stands for Remote Procedure Call) is responsible for all the requests to a Cloud that Perceval supports. It sends the authentication info along with the request data, and reacts to the HTTP errors which might occur.

*class* perceval.providers.quandela.rpc_handler.RPCHandler(*name*, *url=None*, *token=None*, *proxies=None*)  
Remote Call Procedure Handler

A class to call the web API

Parameters:  
- **name** – name of the target platform

- **url** – API URL to call

- **token** – token used for authentication

- **proxies** – dictionary mapping protocol to the URL of the proxy
