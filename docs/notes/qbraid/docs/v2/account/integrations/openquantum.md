> Full piece: [https://docs.qbraid.com/v2/account/integrations/openquantum.md](https://docs.qbraid.com/v2/account/integrations/openquantum.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 73d610c819cd1dcec75d8ffb9707feb7337e7b168e2fb14a54d9199293425688.

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

# Open Quantum

> Create and connect an Open Quantum account, review its credits, and run jobs through qBraid.

The Open Quantum integration lets you submit jobs through qBraid and pay with your connected [Open Quantum](https://www.openquantum.com/) account's credits.

<Warning>
  A job that costs no qBraid credits can still consume Open Quantum credits.
  Buying qBraid credits does not fund your Open Quantum balance. Check the
  provider's balance and pricing before submitting work.
</Warning>

## Create your Open Quantum account

1. Open [Open Quantum](https://www.openquantum.com/) and start sign-up.
2. Complete the provider's registration and any remaining onboarding steps.
3. Sign in and review the account's available credits before connecting it to qBraid.

If Open Quantum displays a welcome-credit offer, follow its claim instructions and confirm that the credits appear in your provider balance. Offer availability and eligibility are controlled by Open Quantum. Welcome credits are not a guaranteed allocation from qBraid.


## Connect Open Quantum to qBraid

1. Sign in to [qBraid Account](https://account.qbraid.com/).
2. Open [Account > Profile](https://account.qbraid.com/account/profile).
3. Find **Integrations** and locate **Open Quantum**.
4. Select **Connect**. Your browser navigates to the Open Quantum authorization flow.
5. Sign in to the Open Quantum account you want to use and complete authorization.
6. Wait to return to qBraid Profile, then check the connection as described below.


You can also reach Profile's connection setup from the connection prompt in [Circuit Composer](https://docs.qbraid.com/v2/account/composer).

## Confirm the connection

On success, qBraid displays **Open Quantum connected**. The Open Quantum entry shows a green status dot, **Connected as** followed by the linked account, and a **Disconnect** button. Check that this is the account whose credits you intend to use.


## Run a job through qBraid

1. Open [Devices](https://account.qbraid.com/devices) and find the Open Quantum device you want to use.
2. Check its availability and provider pricing.
3. Use [Circuit Composer](https://docs.qbraid.com/v2/account/composer) or the [qBraid Runtime](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components) to submit your circuit to that device.
4. Open [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs) to inspect the job's status, results, or error.

For a local Python environment, install the qBraid SDK and configure your [qBraid API key](https://docs.qbraid.com/v2/account/api-keys). Open Quantum's [installation guide](https://docs.openquantum.com/qbraid/installation/) explains local and Lab authentication. Its [backend guide](https://docs.openquantum.com/qbraid/backends-targets/) lists Open Quantum device identifiers, and its [examples](https://docs.openquantum.com/qbraid/examples/) provide complete circuits.

## Review provider credits

Open the [Open Quantum billing page](https://www.openquantum.com/settings/billing) to check the linked account's balance and transactions. Review consumption and expiration entries if the balance is lower than expected.

Open Quantum distinguishes two credit types:

| Type | Source and use | Provider's documented expiration |
| --- | --- | --- |
| **Spark** | Free or promotional credits for Public execution plans. | 90 days after grant. |
| **Full** | Purchased credits for Public or Private execution plans. | 12 months. |

For Public plans, Open Quantum spends Spark credits before Full credits. Private plans require Full credits. Check the provider's [credit documentation](https://docs.openquantum.com/concepts/credits/) for current terms and its [pricing page](https://www.openquantum.com/pricing) for rates.

To buy provider credits, open the Open Quantum portal's credit purchase flow, select an amount, complete Stripe checkout, and confirm the updated provider balance. These credits remain separate from your qBraid wallet.

## Disconnect or change accounts

1. Open **Account > Profile > Integrations**.
2. Select **Disconnect** beside Open Quantum.
3. Wait for the entry to return to **Connect**.
4. To use another Open Quantum account, select **Connect**, authorize that account, and verify **Connected as** afterward.

Link an account again before submitting another Open Quantum job through qBraid.

## Troubleshoot the connection or a failed job

- If the connection status cannot load, select **Retry**. A status-loading error does not establish that the account is disconnected.
- If authorization fails, return to Profile, select **Connect**, and complete the flow while signed in to the intended qBraid account.
- If jobs fail after connection, confirm the **Connected as** account, check its Open Quantum balance and credit expiration, and inspect the target device's availability and job error.
- If Spark credits are available but the selected execution plan requires Full credits, review the provider's supported plans before retrying.

If the error continues, open [Support](https://docs.qbraid.com/v2/account/support) with the job identifier and error message. Do not include credentials.

## Related links

- [qBraid on Open Quantum](https://www.openquantum.com/frameworks/qbraid)
- [Open Quantum's qBraid documentation](https://docs.openquantum.com/qbraid/overview/)
- [Open Quantum credits and pricing](https://docs.openquantum.com/concepts/credits/)
