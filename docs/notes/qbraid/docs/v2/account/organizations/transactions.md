> Full piece: [https://docs.qbraid.com/v2/account/organizations/transactions.md](https://docs.qbraid.com/v2/account/organizations/transactions.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 b3239a4e9cbcf7941665a71264bf42064074062ec44af4d0c8e2683518b30d96.

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

# Transactions

> Filter organization credit activity, export matching transactions, and inspect charges.

Switch to your organization and open [Billing](https://account.qbraid.com/organizations/billing), then select **Transactions**. This log records organization credit purchases, transfers, deductions, and refunds.

## Filter transactions

Use the **Type**, **Status**, and **Date range** controls above the table. The default range is **Last 7 days**. Other ranges include **Last 30 days**, **Last 90 days**, **Last 12 months**, and **Custom**. For a custom range, enter the start and end dates.

Filters are stored in the page URL. **Reset filters** clears the selection. Status filtering applies to the fetched page, so a page can contain fewer visible rows than the page size.

## Read the table

The table shows **Date**, **Type**, **Description**, **Amount**, **Balance after**, and **Status**. Use the pagination controls to move through the history. Each page fetches up to 20 transactions.

Charges for the same compute resource and day can appear as a collapsed group. Expand the group to inspect its individual billing periods. The number of displayed rows can therefore be smaller than the number of transactions.

Select a transaction to open its details. Depending on the charge, the panel includes resource information, the billing period, balance after the transaction, and a receipt link. Select **Refresh** to retrieve recent activity.

## Export CSV

Select **Export CSV** to download transactions matching the selected type, date range, and status. Organization exports fetch all matching pages. This differs from the personal wallet export, which exports the current page.

The file is named `org-transactions-<YYYY-MM-DD>.csv`. If the result exceeds the supported export size, narrow the date range or type and export again. The application reports an oversized export instead of silently downloading a partial file.

## Report a transaction problem

1. Find and open the transaction.
2. Select **Report issue**.
3. Describe the problem in the support dialog.
4. Submit the report.

The dialog includes the transaction ID and billing details so support can locate the charge.

## Invoices

Use the separate **Invoices** tab for Stripe invoices issued to the organization. It shows the invoice date, billing period, total, and status, with **Receipt** and **PDF** links when available. The personal wallet's invoice section shows your personal billing account instead.

Use [Audit logs](https://docs.qbraid.com/v2/account/organizations/audit-logs) to find who initiated a credit or billing action, inspect its result, and export the recorded activity.
