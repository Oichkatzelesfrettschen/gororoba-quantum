> Full piece: [https://docs.qbraid.com/v2/home/migration.md](https://docs.qbraid.com/v2/home/migration.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 a3674174e5175a4f60df636a91e2524181f50eba70621a547c0683c92bf192ce.

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

# Migration Guide

qBraid is migrating to a new Generation-2 platform. Below is what you need to know and what to do before and after the migration.

## Migration window

- **When:** Sunday, February 8th, 10:00 AM–2:00 PM CT (4 hours)
- **Impact:** The platform and all associated services will be unavailable during this window.

## What carries over

- **Files** — All of your files from the legacy platform will be migrated.
- **Credits** — All qBraid credits will carry over **except** promotional credits (e.g., credits from access codes). Only credits purchased with a credit card or transferred to you within an organization will be migrated.
- **Organizations** — Organizations will carry over with no service interruption.

## What does not carry over (and what to do)

### Quantum jobs

Quantum jobs data will **not** be migrated. On the new account **Jobs** page you will see a download option to export all legacy quantum jobs data as a JSON file. You can then load and work with that data (results and metadata) using the qBraid-SDK as usual.

For detailed instructions on retrieving and working with your legacy jobs, see the [Legacy Jobs Retrieval](https://docs.qbraid.com/home/legacy-jobs) guide.

### Transactions

Transactions will **not** be migrated. You can download your legacy transactions as a JSON file from **Account** > **Wallet** on the new platform.

### Submitting jobs after migration

To submit quantum jobs on the new platform, use either the updated [quantum jobs and devices API endpoints](https://docs.qbraid.com/v2/api-reference/user-guide/overview) or:

- **qBraid-SDK** version 0.11.0 or higher
- **qBraid-CORE** version 0.2.0 or higher

Older versions of the SDK and CORE are not compatible with the new API.

## Subscribers (Standard and Pro)

You will need to renew your qBraid subscription to keep access to Standard or Pro.

1. Log in to the new [account page](https://account.qbraid.com/).
2. Go to **Account** > **Wallet**.
3. Select your previous subscription tier and complete checkout.

Previous subscribers will receive an email with a promotional code for **1 month free** when they resubscribe.

## Beta users (V2 early access)

If you participated in the qBraid V2 beta: **all data on the current beta platform will be wiped** at migration (jobs, transactions, credits, and files). None of it will persist.

- Download any data you need before the migration.
- Use any remaining credits, or they will be lost.

## Questions

For questions about the migration or any of the above, contact [contact@qbraid.com](mailto:contact@qbraid.com).
