> Full piece: [https://docs.qbraid.com/v2/core/user-guide/overview.md](https://docs.qbraid.com/v2/core/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 98b45ee873c9637f44243432bd0dd54fc062bd8374a7451592694d78aa574301.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/core/_static/core_banner.png"
    alt="qBraid-CORE"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/core/_static/core_banner_dark.png"
    alt="qBraid-CORE"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _Python client for developing software with qBraid cloud services_
</div>

qBraid-CORE is a Python client for qBraid cloud services. The [qBraid CLI](https://pypi.org/project/qbraid-cli/), [qBraid SDK](https://pypi.org/project/qbraid/), and
[qBraid Lab](https://pypi.org/project/qbraid-lab/) use it to access those services.

See the [qBraid-CORE reference](https://sdk.qbraid.com/qbraid-core/) for the latest API documentation and supported services.

## Getting started

You can install qbraid-core from PyPI with:

```bash
pip install qbraid-core
```

<Warning>
qbraid-core versions &lt;0.2.0 are *not* compatible with qBraid API V2. See [migration guide](https://docs.qbraid.com/v2/api-reference/rest/migration).

Use qbraid-core &ge; 0.2.0 with API V2.

</Warning>

### Local configuration

After installing qbraid-core, you must configure your account credentials:

1. Create a qBraid account or log in to your existing account by visiting
   [account.qbraid.com](https://account.qbraid.com/)
2. Open [API Keys](https://account.qbraid.com/account/api-keys) and create a key. See [API key management](https://docs.qbraid.com/v2/account/api-keys).
3. Save your API key from step 2 in local [configuration file](https://docs.qbraid.com/v2/cli/user-guide/config-files) `~/.qbraid/qbraidrc`, where `~` corresponds to your home (`$HOME`) directory:

```ini
[default]
api-key = YOUR_KEY
url = https://api-v2.qbraid.com/api/v1
```

Or generate your `~/.qbraid/qbraidrc` file via the qbraid-core Python interface:

```python
>>> from qbraid_core import QbraidSessionV1
>>> session = QbraidSessionV1(api_key='API_KEY')
>>> session.save_config()
```

See [local CLI setup](https://docs.qbraid.com/v2/cli/user-guide/overview#local-setup) for other credential configuration methods.

### Verify setup

After configuring your qBraid credentials, verify your setup by running the following from a Python interpreter:

```python
>>> from qbraid_core.services.runtime import QuantumRuntimeClient
>>> quantum_client = QuantumRuntimeClient()
>>> device_list = quantum_client.list_devices()
>>> for device in device_list:
...     print(device.qrn)
```

### Estimate job cost

Before submitting a job, you can ask for a quote in qBraid credits for a given device and shot count:

```python
>>> estimate = quantum_client.estimate_cost("aws:aqt:qpu:ibex-q1", shots=1000)
>>> estimate.pricingAvailable
True
>>> estimate.estimatedCost
Credits('2380')
```

The quote does not cap the final charge. When you submit a job, qBraid holds its estimated cost from your credit balance. When the job finishes, qBraid charges the actual cost and refunds or debits the difference. A job that runs longer than quoted is billed for what it used. QPUs are quoted from the device's execution history, and per-minute QPUs scale with the shot count. Simulators are quoted from a fixed conservative duration, so their quote does not change with shots. Omitting `shots` quotes 1000.

Some devices, such as those with dynamic pricing, return a status instead of an upfront quote:

```python
>>> estimate = quantum_client.estimate_cost("ibm:ibm:qpu:fez")
>>> estimate.pricingAvailable
False
>>> estimate.reason
'dynamic_pricing_unavailable'
```

A missing or retired device, or a shot count outside 1 to 100000, raises `QuantumRuntimeServiceRequestError`.

## Community

- For feature requests and bug reports: [Submit an issue](https://github.com/qBraid/qBraid-Lab/issues)
- For discussions and/or specific questions about qBraid services, [join our discord community](https://discord.gg/KugF6Cnncm)
- For questions that are more suited for a forum, post to [Stack Overflow](https://stackoverflow.com/) with the [`qbraid`](https://stackoverflow.com/questions/tagged/qbraid) tag.
