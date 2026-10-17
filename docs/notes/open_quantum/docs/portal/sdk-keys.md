> Full piece: [https://docs.openquantum.com/portal/sdk-keys/](https://docs.openquantum.com/portal/sdk-keys/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fdbbbd7a0c89c324642afd9b2357e50c6320996f88d67d3666514cdc0d4c4888.

# SDK Keys

SDK keys are the credentials your Python code uses to authenticate with the Open Quantum platform. You create and manage them from the [SDK Keys](https://www.openquantum.com/keys) page in the portal.

## Creating a Key

1.  Go to [SDK Keys](https://www.openquantum.com/keys).
2.  Click **Create SDK Key**.
3.  Copy the **Client ID** and **Client Secret** immediately.

Warning

The client secret is only displayed once at creation time. Store it in a secure location (e.g., a password manager or environment variable). If you lose it, delete the key and create a new one.

You can hold up to **2 SDK keys** at a time per user account. Rotate keys by deleting old keys and generating new ones.

## Deleting a Key

First disable the key by clicking the power button next to the respective key on the [SDK Keys](https://www.openquantum.com/keys) page. Then, click the delete button. Deletion is permanent and immediate. Any code using that key will stop authenticating.

Tip

Create separate keys for different environments (development, staging, production) so you can rotate or revoke them independently.

## Using Your Key in Code

See the [Authentication](https://docs.openquantum.com/core-sdk/authentication/) page for all the ways to use SDK keys in Python: environment variables, key files, saved accounts, and more.
