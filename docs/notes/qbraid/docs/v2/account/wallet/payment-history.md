> Full piece: [https://docs.qbraid.com/v2/account/wallet/payment-history.md](https://docs.qbraid.com/v2/account/wallet/payment-history.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 3cd7f29025144bceb5161880b454be4efbbc75e9e1377f29a04c2513d272a7b3.

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

# Payment history

> See every transaction on your account, filter by type or category, search, and export to CSV.

The **Transactions** section at the bottom of the wallet lists every credit transaction in this workspace. That includes purchases, transfers in and out, deductions, promo credits, and refunds.

In **qBraid Default**, two tabs sit under the section title: **Credit transactions** and **Invoices & receipts**. An organization workspace shows transactions only.

## What each part does

- **Search transactions.** Filters the rows on the current page by description text.
- **All Types.** Filters by transaction type, such as Purchase, Compute, AI Chat, Received, Sent, or Refund.
- **All Categories.** Filters by category: Purchases, Subscriptions, Transfers, Usage, or AI Chat.
- **Refresh.** Reloads the transactions without reloading the page.
- **Export CSV.** Downloads the current page of sorted and filtered rows.
- **Old Transactions.** Downloads legacy records. It appears only when your account has transactions from before the current billing system.
- **Column headers.** **Date**, **Type**, **Amount**, and **Balance** sort the page. **Description** does not sort.
- **Rows.** Open a detail dialog with the amount, balance after, and per-type details.

Active filters appear as removable badges under the toolbar. A **Clear all** button clears them together.

<Frame>
  <img
    src="/v2/account/_static/wallet-transactions.webp"
    alt="Credit transactions table with the search field, type and category filters, and sortable Date, Type, Amount, and Balance columns"
  />
</Frame>

<Note>
  There is no date-range filter today. Use search or the Type and Category
  dropdowns to narrow what you see.
</Note>

## Filter and search

1. Type in **Search transactions...** to match descriptions on the current page.
2. Open **All Types** and pick a type, such as **Compute** or **Purchase**.
3. Open **All Categories** to narrow further to a business category.
4. Remove a single filter from its badge, or select **Clear all**.

<Frame>
  <img
    src="/v2/account/_static/wallet-transactions-filter.webp"
    alt="The Type filter open, listing types such as Purchase, Bonus, Job, Compute, AI Chat, Received, Sent, Refund, Credit, and Deduction"
  />
</Frame>

## Read a row

Each row shows the date and time, a type badge, a description, the signed amount, and the balance after. A dash means the row carries no positive amount or no recorded balance.

Select a row to open its details. Depending on the transaction you can see:

- Payment details and a **View Receipt** link when available.
- The related user for transfers.
- The reason or note attached at the time.
- The transaction ID and a **Report Issue** link.

<Frame>
  <img
    src="/v2/account/_static/wallet-transaction-details.webp"
    alt="Transaction details dialog for a subscription payment showing the amount, balance after, plan, status, transaction ID, and Report Issue"
  />
</Frame>

## Grouped compute rows

Repeated charges for the same compute resource fold into a grouped row under the default date sort. The group shows the UTC day and the count, such as **8 charges · UTC day**. Expand the group to inspect the individual billing periods.

Sorting by a value column such as Amount or Balance shows every row separately, so each transaction keeps its sorted position.

## Pages

The table shows 20 rows per page. Use **Previous** and **Next** to move between pages. The footer shows the current range and the total count.

On narrow screens the table becomes a list of cards with the same information.

## Export transactions

1. Filter or sort the table as needed.
2. Select **Export CSV**.
3. The file `transactions-<YYYY-MM-DD>.csv` downloads with the current page of sorted and filtered rows. Columns: Date, Type, Category, Description, Amount, Balance.

<Tip>
  The export contains one page of transactions. To download more, move through
  the table and export each page you need.
</Tip>

## Legacy transactions

If you have transactions from before the current billing system, an **Old Transactions** button appears alongside the regular export. It downloads those older records in their original format.

<Note>
  Legacy and current transactions do not combine in the same file. Download
  both if you need a complete history.
</Note>

## Invoices

Open the **Invoices & receipts** tab in **qBraid Default** for your personal Stripe invoices. The table lists the date and invoice number, billing period, amount, and status. Select **Receipt** to open the hosted invoice or **PDF** to download it when those links are available.

<Frame>
  <img
    src="/v2/account/_static/wallet-invoices.webp"
    alt="Invoices and receipts tab listing Stripe invoices with date, period, amount, paid status, and Receipt and PDF links"
  />
</Frame>

### Find invoices

1. Open **Account > Wallet** in **qBraid Default**.
2. Scroll to **Transactions**.
3. Select the **Invoices & receipts** tab. On a narrow screen the tab reads **Invoices**.
4. Select **Receipt** or **PDF** on the invoice's row.

Invoices are different from credit transactions. A credit deduction does not necessarily have a Stripe invoice. For a team purchase, open **Organizations > Billing > Invoices** in the organization workspace.
