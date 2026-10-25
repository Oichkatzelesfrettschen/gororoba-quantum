> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html](https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 622d97c6cb79f54b0cb2a0475e98b634d393907c2cdb886171017c692d09c692.

# Quandela

[Quandela Cloud](https://cloud.quandela.com/) provides access to physical and emulated quantum processing units. It is Perceval’s historical provider and offers all the capabilities that Perceval has.

## QuandelaCommunicationLayer

*class* perceval.providers.quandela.quandela_communication_layer.QuandelaCommunicationLayer(*name*, *token=None*, *url=None*, *proxies=None*)  
A communication layer able to target Quandela provided platforms.

Parameters:  
- **name** (`str`) – The name of the target platform.

- **token** (`Optional`\[`str`\]) – An authentification token to connect to the platform. Leave empty to use the one defined in the `RemoteConfig`

- **url** (`Optional`\[`str`\]) – The URL of the platform. Leave empty to use the one defined in the `RemoteConfig` (or the default one if it has never been changed)

- **proxies** (`Optional`\[`dict`\[`str`, `str`\]\]) – dictionary mapping protocol to the URL of the proxy

## RemoteConfig

Note

[Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) serialization does not store credentials. To be able to deserialize an execution made through a Quandela computer, the `RemoteConfig` needs to be configured.

``` default
>>> config = pcvl.RemoteConfig()
>>> config.set_token("your-personal-access-token")
>>> config.set_proxies({"https": "your-proxy"})  # Shared among all provider configs
>>> config.save()
```

After configuration, the token and provider name may be omitted from the communication layer:

``` default
>>> communication_layer = pcvl.QuandelaCommunicationLayer(
...     name=PLATFORM_NAME,
... )
```

Note

Do not persist authentication tokens on shared or public computers. Using an environment variable or the in-memory configuration cache avoids writing the token to disk.

*class* perceval.providers.quandela.remote_config.RemoteConfig(*persistent_data=\<perceval.utils.persistent_data.PersistentData object\>*)  
Handle the remote configuration for Quandela provider.

Parameters:  
**persistent_data** ([`PersistentData`](https://perceval.quandela.net/docs/v1.3/reference/utils/persistent_data.html#perceval.utils.persistent_data.PersistentData "perceval.utils.persistent_data.PersistentData")) – The persistent data access to use. In a standard environment, always use the default.

*classmethod* clear_cache()  
Delete the RemoteConfig cache.

get_proxies()  
Get the proxy configuration as a mapping of protocols to URLs.

Return type:  
`dict`\[`str`, `str`\]

get_token()  
Search a valid token from the environment, put it in cache and return it.

The priority for the token search is as follows: \* A token already in cache (e.g. set by the user or already found in a previous call) \* The value of the environment variable given by self.get_token_env_var() \* The value in Perceval persistent configuration

Return type:  
`str`

Returns:  
The token

*classmethod* get_token_env_var()  
Get the name of the environment variable storing a token.

Return type:  
`str`

get_url()  
Search a valid cloud URL from the environment, put it in cache and return it.

The priority for the URL search is as follows: \* A URL already in cache (e.g. set by the user or already found in a previous call) \* The value in Perceval persistent configuration

Return type:  
`str`

Returns:  
The cloud URL

save()  
Save the current remote configuration on disk. After this, the configuration is persistent and can be found in other Perceval sessions (even in different virtual envs).

Return type:  
`None`

*static* set_proxies(*proxies*)  
Set the proxy configuration. The proxy configuration is shared between all configurations.

Usage example:

``` default
>>> rc = RemoteConfig()
>>> rc.set_proxies({"http": "http://user:pass@192.168.0.1",
...                 "https": "http://user:pass@192.168.0.1:8080"
...                })
```

Parameters:  
**proxies** (`dict`\[`str`, `str`\]) – proxy configuration in the form of a dictionary which maps protocols to URLs

Return type:  
`None`

*classmethod* set_token(*token*)  
Set a user authentication token in the configuration cache. It is not saved on disk before the save method is called.

Parameters:  
**token** (`str`) – The token

Return type:  
`None`

*classmethod* set_token_env_var(*env_var*)  
Change the name of the environment variable storing a token.

Parameters:  
**env_var** (`str`) – name of the new environment variable to search for

Return type:  
`None`

*classmethod* set_url(*url*)  
Set a cloud URL in the configuration cache. It is not saved on disk before the save method is called.

Parameters:  
**url** (`str`) – The cloud URL

Return type:  
`None`

## Legacy Session

Warning

This class is about the legacy workflow for providers. It should not be used, and is kept here only for backward compatibility

*class* perceval.providers.quandela.quandela_session.Session(*platform_name*, *token*, *url=None*)  
Quandela Cloud session

Parameters:  
- **platform_name** (`str`) – Name of an available platform on Quandela Cloud (e.g. “sim:slos”)

- **token** (`str`) – A valid authentication token to use within the session

- **url** (`Optional`\[`str`\]) – URL prefix for the endpoint to connect to. If omitted the Quandela Cloud endpoints will be used.

build_remote_processor()  
Build a remote processor from the session information

Return type:  
[`RemoteProcessor`](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#perceval.runtime.legacy.remote_processor.RemoteProcessor "perceval.runtime.legacy.remote_processor.RemoteProcessor")
