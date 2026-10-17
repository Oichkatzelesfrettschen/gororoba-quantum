> Full piece: [https://docs.openquantum.com/core-sdk/authentication/](https://docs.openquantum.com/core-sdk/authentication/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 81479ee0dff74b1bc82cfa6912c0da3ff34cada8c7c6274e5395490e4e047e89.

# Authentication

Open Quantum uses SDK keys to authenticate API requests. SDK keys are managed through the [Open Quantum Portal](https://www.openquantum.com) and exchanged for short-lived JWT tokens via the Open Quantum identity server.

## SDK Key Authentication

An SDK key consists of two parts:

- **Client ID** -- A public identifier (format: `s_<uuid>`). Safe to log or display.
- **Client Secret** -- A private secret. Must be kept confidential.

These credentials are used with the OAuth 2.0 `client_credentials` grant to obtain a JWT access token.

## Creating SDK Keys

1.  Log in to the [Open Quantum Portal](https://www.openquantum.com).
2.  Go to the [SDK Keys](https://www.openquantum.com/keys) page.
3.  Click **Create SDK Key**.
4.  Copy both the Client ID and Client Secret.

Warning

The Client Secret is displayed only once at creation time. Store it securely. If you lose it, delete the key and create a new one.

You can create up to **2 SDK keys** per user account. Keys can be enabled, disabled, or deleted from the [SDK Keys](https://www.openquantum.com/keys) page. See [SDK Keys](https://docs.openquantum.com/portal/sdk-keys/) for more on key management, rotation, and best practices.

## Authentication Methods

### ClientCredentials + ClientCredentialsAuth (Core SDK)

The Core SDK uses `ClientCredentials` and `ClientCredentialsAuth` for authentication:

``` python
from openquantum_sdk.auth import ClientCredentials, ClientCredentialsAuth

creds = ClientCredentials(
    client_id="s_your_client_id",
    client_secret="your_client_secret",
)

auth = ClientCredentialsAuth(creds=creds)
```

Pass the `auth` object to any client:

``` python
from openquantum_sdk.clients import SchedulerClient, ManagementClient

scheduler = SchedulerClient(auth=auth)
management = ManagementClient(auth=auth)
```

### Token-Based Auth

If you already have a JWT token (obtained externally), pass it directly:

``` python
from openquantum_sdk.clients import SchedulerClient

scheduler = SchedulerClient(token="your_jwt_token")
```

Note

You cannot provide both `token` and `auth` to the same client. Use one or the other.

### Saved Accounts

The Core SDK manages saved account credentials via `OpenQuantumClient` — no plugin required. (The Qiskit plugin's `OpenQuantumService` subclasses it, so the same methods work there too.)

#### Save an Account

``` python
from openquantum_sdk import OpenQuantumClient
from openquantum_sdk.auth import ClientCredentials

OpenQuantumClient.save_account(
    name="default",
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
)
```

Credentials are stored in `~/.openquantum/accounts.json` (or the platform-appropriate config directory). If the `keyring` package is installed, secrets are stored in the system keyring instead of on disk.

#### Load a Saved Account

``` python
client = OpenQuantumClient.from_saved_account(name="default")
```

Or let `OpenQuantumClient()` auto-load the default saved account:

``` python
client = OpenQuantumClient()  # Automatically loads "default" account if saved
```

Set `OPENQUANTUM_NO_AUTOLOAD=1` to disable auto-loading.

To build a client from environment credentials **without** a saved account, use `from_env()`. It also reads `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM` when those arguments are omitted. If nothing resolves, it raises `AuthenticationError`:

``` python
client = OpenQuantumClient.from_env()
```

PennyLane, Cirq, and Qrisp construct their clients with `from_env()`, so they honor the same credential and URL variables. The MCP server does too. `OpenQuantumService()` (the Qiskit plugin) still tries a saved account first. When that account is missing or fails to load, it falls back to the same environment credentials. The plain Qiskit constructor does **not** read the URL variables; call `OpenQuantumService.from_env()` or pass `scheduler_url`, `management_url`, and `keycloak_base` explicitly.

#### List and Delete Saved Accounts

``` python
accounts = OpenQuantumClient.saved_accounts()
print(accounts)

OpenQuantumClient.delete_account(name="default")
```

#### Login Shortcut

The `login()` class method creates a client and optionally saves credentials in one call:

``` python
client = OpenQuantumClient.login(
    creds=ClientCredentials(
        client_id="s_your_client_id",
        client_secret="your_client_secret",
    ),
    save=True,
    name="default",
)
```

### SDK Key File

You can store credentials in a JSON file instead of passing them inline. This is the recommended approach for the CLI and is also useful for scripts.

Create a JSON file (e.g., `sdk-key.json`):

``` json
{
    "client_id": "s_your_client_id",
    "client_secret": "your_client_secret"
}
```

Use it with the CLI:

``` bash
python -m openquantum_sdk --sdk-key sdk-key.json --input circuit.qasm ...
```

Or load it programmatically:

``` python
from openquantum_sdk.credentials import load_creds_from_file
from openquantum_sdk.clients import SchedulerClient
from openquantum_sdk.auth import ClientCredentialsAuth

creds = load_creds_from_file("sdk-key.json")
scheduler = SchedulerClient(auth=ClientCredentialsAuth(creds=creds))
```

You can also point to the file via the `OPENQUANTUM_SDK_KEY` environment variable:

``` bash
export OPENQUANTUM_SDK_KEY="/path/to/sdk-key.json"
```

#### Credential Resolution Order

Every SDK surface resolves credentials through the same logic, in this order (first match wins):

1.  An explicit `token` argument.
2.  An explicit `client_id` + `client_secret` pair.
3.  An SDK-key JSON file (an explicit path argument, else the `OPENQUANTUM_SDK_KEY` environment variable).
4.  The `OPENQUANTUM_TOKEN` environment variable.
5.  The `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET` environment variables.

The CLI layers its own flags on top: `--sdk-key` takes precedence over `--client-id` / `--client-secret`, which in turn override the environment variables above.

### Environment Variables

All SDKs read credentials from environment variables as a fallback:

| Variable | Description |
|----|----|
| `OPENQUANTUM_CLIENT_ID` | SDK key Client ID |
| `OPENQUANTUM_CLIENT_SECRET` | SDK key Client Secret |
| `OPENQUANTUM_SDK_KEY` | Path to a JSON file containing `client_id` and `client_secret` |
| `OPENQUANTUM_TOKEN` | A pre-obtained JWT access token (used instead of an SDK key) |
| `OPENQUANTUM_ORGANIZATION_ID` | Organization UUID. PennyLane, Cirq, Qrisp, `get_backend`, and the MCP server use it when `organization_id` is omitted. `get_backend` keeps the HTTP session of the backend it returns open. The old names `OQ_ORG_ID` and `OQ_SUBCATEGORY_ID` are not read; subcategory stays an argument and defaults to `oth:oth` |
| `OPENQUANTUM_SCHEDULER_URL` | Override the scheduler API base. Read by `OpenQuantumClient.from_env` (and therefore PennyLane, Cirq, and Qrisp) and by the MCP server. The MCP server still accepts `OPENQUANTUM_SCHEDULER_BASE` when this variable is unset |
| `OPENQUANTUM_MANAGEMENT_URL` | Override the management API base. Read by `OpenQuantumClient.from_env` (and therefore PennyLane, Cirq, and Qrisp) and by the MCP server. The MCP server still accepts `OPENQUANTUM_MANAGEMENT_BASE` when this variable is unset |
| `OPENQUANTUM_KEYCLOAK_BASE` | Override the Keycloak / token base. Read by `OpenQuantumClient.from_env` and the MCP server |
| `OPENQUANTUM_KEYCLOAK_REALM` | Keycloak realm. Read by `OpenQuantumClient.from_env` and the MCP server. Default `platform` |

``` bash
export OPENQUANTUM_CLIENT_ID="s_your_client_id"
export OPENQUANTUM_CLIENT_SECRET="your_client_secret"
```

## Token Caching and Auto-Refresh

`ClientCredentialsAuth` manages JWT tokens automatically:

1.  On the first API call, the SDK exchanges your SDK key for a JWT token.
2.  The token is cached in memory for the lifetime of the auth object.
3.  Before each API call, the SDK checks if the token will expire within the next 30 seconds.
4.  If the token is about to expire, a new one is obtained automatically.

You do not need to manage tokens manually.

## Organization ID

Every job on Open Quantum belongs to an organization. The Organization ID is a UUID that identifies which organization's credits and job quotas to use. Most users have a single default organization and don't need to set this.

If you do not specify an organization ID, all SDKs auto-discover your organization. If you belong to multiple organizations, the SDK will warn you and pick the first one — pass `organization_id` explicitly to choose.

**Where to find it:**

- In the [Open Quantum Portal](https://www.openquantum.com), go to your [Dashboard](https://www.openquantum.com/dashboard) page.
- From the Qiskit plugin: `service.organizations()` returns a list of your organizations with their IDs and names.
- From the Core SDK: `management.list_user_organizations()` returns the same information.

**Setting it:**

Core SDKQiskit PluginPennyLane Plugin

``` python
config = JobSubmissionConfig(
    organization_id="your-org-uuid",
    ...
)
```

``` python
backend.run(qc, organization_id="your-org-uuid")
```

``` python
dev = qml.device("openquantum.device", ..., organization_id="your-org-uuid")
```

Or set the `OPENQUANTUM_ORGANIZATION_ID` environment variable.

## Security Best Practices

- **Never commit credentials to version control.** Use environment variables or saved accounts.
- **Do not hardcode secrets in notebooks or scripts.** Use `.env` files (excluded from git via `.gitignore`) or environment variables.
- **Rotate keys periodically.** Delete old SDK keys and create new ones in the portal.
- **Disable unused keys.** If you are not actively using a key, disable it from the portal to prevent unauthorized use.
- **Use one key per environment.** Create separate SDK keys for development and production.

## Troubleshooting

If authentication fails, see the [Troubleshooting](https://docs.openquantum.com/pennylane-plugin/troubleshooting/) page for common error messages and solutions.

## Next Steps

- [Installation](https://docs.openquantum.com/core-sdk/installation/) -- Install the SDK and plugins.
- [Quick Start](https://docs.openquantum.com/core-sdk/quickstart/) -- Submit your first quantum job.
