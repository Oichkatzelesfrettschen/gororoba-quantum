> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.print_env_vars.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.print_env_vars.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 35c8a3fff5b933e7555760faa9244d61cc3c1ae1d1fa8c0a5e6f831c5971bd97.

# iqm.iqm_client.util.print_env_vars

iqm.iqm_client.util.print_env_vars() → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Print the values of the environment variables used by IQMClient to connect to the server.

Meant for manually validating the environment configuration. Does not include the authentication variables `IQM_TOKEN` and `IQM_TOKENS_FILE` to avoid accidentally exposing your token.

Return type:  
None
