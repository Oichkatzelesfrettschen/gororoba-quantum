> Full piece: [https://docs.qbraid.com/v2/account/wallet/subscriptions.md](https://docs.qbraid.com/v2/account/wallet/subscriptions.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 737ea8781d8ef368346230ebcd66ce0d11ce97c7273d9085d95ddd508cb9d4e7.

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

# Personal subscriptions

> Compare personal plans, change your plan, and manage billing.

A personal subscription covers your account in **qBraid Default**. Switch to that workspace, then open [Account > Wallet](https://account.qbraid.com/account/wallet).

## Plans

| Plan     | Monthly      | Annual                    | CPU hours / month | Storage | Simulator jobs / day | AI allowance |
| -------- | ------------ | ------------------------- | ----------------- | ------- | -------------------- | ------------ |
| Free     | $0           | $0                        | 100               | 15 GB   | 100                  | $5           |
| Standard | $20 / month  | $192 / year ($16 / month) | 400               | 50 GB   | 500                  | $15          |
| Pro      | $100 / month | $960 / year ($80 / month) | 2,000             | 150 GB  | Unlimited            | $50          |

Simulator jobs are per managed simulator. The [GPU simulators](https://docs.qbraid.com/v2/home/pricing#gpu-simulators) have a smaller free allowance instead: 25 circuits a day on Free, 125 on Standard, and unlimited on Pro. A batch counts one per circuit.

You pay annual prices once a year. Review the checkout total before you subscribe. CPU hours, simulator job limits, and AI allowances are separate limits, not credits deposited in your wallet. Check **Account > Usage** for your remaining allowance and renewal date.

Standard includes full Qubes and Quantum Software Engineering course access and priority support. Pro includes dedicated support. The plan cards also list the on-demand compute discount: 10% for Standard and 18% for Pro. Check the effective resource price before you launch.

All current plans can use the AI model catalog. Plans differ in their AI allowance. See [Models and pricing](https://docs.qbraid.com/v2/account/models) and [AI usage quotas](https://docs.qbraid.com/v2/ai/user-guide/usage-quotas).

## What each part does

- **Subscription card.** Shows your tier, a Monthly or Annual badge, a status badge, and the renewal line with your price.
- **Discounted price.** When a discount applies, the card strikes through the list price and shows a **% off** badge.
- **Change plan.** Opens the plan dialog. Pick a tier and interval, preview the price, and confirm.
- **Cancel subscription.** Opens the cancellation dialog. It shortens to **Cancel** on narrow screens.
- **Scheduled change row.** A **Switches to _plan_ on _date_** row inside the card. Select **Undo** to cancel it.
- **Cancellation row.** A notice that the plan will not renew. Select **Keep my plan** to resume.
- **Compare plans.** On paid plans, a collapsed row that expands to the plan cards. Opens automatically at `/account/wallet#available-plans`.
- **Upgrade your plan.** On Free, the visible plan grid with a Monthly/Annual toggle and a savings badge.
- **Payment link.** The **Manage payment & invoices** button. Opens the Stripe customer portal for payment methods and invoices.

Plan cards show the price, key features, and the on-demand compute discount. They do not show quota meters.

<Frame>
  <img
    src="/v2/account/_static/wallet-free-plan.webp"
    alt="Free plan wallet showing the Standard and Pro upgrade cards with Annual billing selected"
  />
</Frame>

Annual billing shows the monthly equivalent and the full yearly total.

<Frame>
  <img
    src="/v2/account/_static/wallet-mobile.webp"
    alt="Wallet on a phone showing the Free subscription card and the Standard upgrade card below it"
  />
</Frame>

On narrow screens the plan cards stack in one column and **Cancel subscription** shortens to **Cancel**.

## Buy a plan

Use these steps on the **Free** plan.

<Steps>
  <Step title="Open your wallet">
    Switch to **qBraid Default**. Open **Account > Wallet**.
  </Step>
  <Step title="Pick a billing interval">
    In **Upgrade your plan**, choose **Monthly** or **Annual**.
  </Step>
  <Step title="Select a plan">
    Select **Upgrade to Standard** or **Upgrade to Pro**. A **Confirm Subscription** dialog opens. It lists the plan, the billing interval, and the total.

    <Frame>
      <img
        src="/v2/account/_static/wallet-confirm-subscription.webp"
        alt="Confirm Subscription dialog showing the Standard plan, Monthly billing, and a $20 per month total with Cancel and Proceed to Payment buttons"
      />
    </Frame>
  </Step>
  <Step title="Pay on Stripe">
    Select **Proceed to Payment**. Stripe opens. Stripe adds any taxes at checkout. Enter a promo code on the Stripe page.
  </Step>
  <Step title="Return to the wallet">
    Complete the payment and return to the wallet. Wait for the subscription card to show your plan before you use the new allowance.
  </Step>
</Steps>

## Your paid plan

A paid plan replaces the Free card with a subscription card. The card shows the tier, the billing interval, and an **Active** badge. It also shows the renewal date and the price.

<Frame>
  <img
    src="/v2/account/_static/wallet-paid-plan.webp"
    alt="Wallet with an active Standard Monthly subscription card showing Renews Nov 10, 2026 at $20.00 per month, with Cancel subscription and Change plan buttons and a collapsed Compare plans row"
  />
</Frame>

On a phone, the card puts **Change plan** first. **Cancel subscription** shortens to **Cancel**.

<Frame>
  <img
    src="/v2/account/_static/wallet-mobile-paid.webp"
    alt="Wallet on a phone showing the active Standard Monthly card with Change plan and Cancel buttons and a Compare plans row"
  />
</Frame>

Select **Compare plans** to see all three plans. Your current plan has a **Current Plan** badge. Use the **Monthly** and **Annual** toggle to switch prices.

<Frame>
  <img
    src="/v2/account/_static/wallet-compare-plans.webp"
    alt="Compare plans expanded with Free, Standard marked Current Plan, and Pro cards and the Annual toggle selected"
  />
</Frame>

## Change plan

<Steps>
  <Step title="Open the plan dialog">
    Open **Account > Wallet** in **qBraid Default**. Select **Change plan** on the subscription card.
  </Step>
  <Step title="Pick a tier and interval">
    Choose **Standard** or **Pro**. Choose **Monthly** or **Annual**. Enter a promo code if you have one.
  </Step>
  <Step title="Read the preview">
    The preview shows the cost before you confirm. **Due today** lists a credit for the unused time on your current plan. It also lists a charge for the time left on the new plan. **Total due today** adds them up. **From** and a date show your **Renewal total**. A note below says when the change starts.

    <Frame>
      <img
        src="/v2/account/_static/wallet-change-plan.webp"
        alt="Change plan dialog switching Standard Monthly to Pro Monthly, with a $80.00 total due today, a $100.00 renewal total from Nov 10, 2026, and the note Takes effect now"
      />
    </Frame>
  </Step>
  <Step title="Confirm the change">
    Select **Confirm change**. The note reads **Takes effect now** when the change starts at once. Otherwise it gives the date your plan changes. You keep your current plan until then.
  </Step>
</Steps>

A scheduled change shows a **Switches to _plan_ on _date_** row inside the card. Select **Undo** to cancel it.

## Manage payment and invoices

Select **Manage payment & invoices** at the top of the wallet to open the Stripe customer portal. Use the portal to manage your payment method and download invoices.

The wallet also has an **Invoices & receipts** tab. See [Payment history and invoices](https://docs.qbraid.com/v2/account/wallet/payment-history#invoices).

## Cancel

<Steps>
  <Step title="Start the cancellation">
    Open **Account > Wallet** in **qBraid Default**. Select **Cancel subscription**.
  </Step>
  <Step title="Pick a reason">
    The dialog asks **Why are you canceling?** Choose one reason. **Continue** stays off until you choose. Some reasons add an optional note box.

    <Frame>
      <img
        src="/v2/account/_static/wallet-cancel-reason.webp"
        alt="Cancel dialog step 1 of 2 asking why you are canceling, with five reasons and Keep my plan and Continue buttons"
      />
    </Frame>
  </Step>
  <Step title="Consider an offer">
    For some reasons, the dialog shows an offer. The offer is a discount or a lower plan. Accept it to keep a subscription. Select **Cancel anyway** to continue.
  </Step>
  <Step title="Confirm the cancellation">
    The last step reads **Cancel _plan_ at the end of your term?** It gives the end date. It lists the limits that drop to Free. It confirms that credits you bought stay in your wallet. Select **Cancel at end of term**.

    <Frame>
      <img
        src="/v2/account/_static/wallet-cancel-confirm.webp"
        alt="Cancel Pro at the end of your term dialog listing CPU hours, storage, and simulator job limits that drop, and that purchased credits stay, with Keep my plan and Cancel at end of term buttons"
      />
    </Frame>
  </Step>
</Steps>

An **Ends _date_** badge appears on the plan card. The card shows **No further charges** and a notice that your plan will not renew. You keep the paid benefits until the end date. Then your account returns to Free.

<Frame>
  <img
    src="/v2/account/_static/wallet-cancelled.webp"
    alt="Pro Monthly card with an Ends Nov 10, 2026 badge, the notice Your plan won't renew, and a Keep my plan button"
  />
</Frame>

While a cancellation is scheduled, the card hides **Change plan** and **Cancel subscription**.

## Keep my plan

Use **Keep my plan** to undo a cancellation before the end date.

<Steps>
  <Step title="Open your wallet">
    Open **Account > Wallet** in **qBraid Default**.
  </Step>
  <Step title="Resume the subscription">
    In the notice that says **Your plan won't renew**, select **Keep my plan**. The notice goes away. Your plan renews as before.
  </Step>
</Steps>

You can also select **Keep my plan** inside the cancel dialog. That closes the dialog and changes nothing.

## Personal vs team

|                 | Personal                         | [Team](https://docs.qbraid.com/v2/account/organizations/subscriptions) |
| --------------- | -------------------------------- | ----------------------------------------------- |
| Billing scope   | Your personal account            | The organization                                |
| Price           | Per account                      | Per seat, minimum two seats                     |
| Benefits        | Your account                     | Members assigned a seat                         |
| Where to manage | Wallet and the in-app dialogs    | Organization Billing                            |
| Add capacity    | Change plan or upgrade your plan | Add seats and assign them                       |

In an organization workspace, the wallet shows **Your seat** instead of the personal subscription card. A member with a seat sees the seat tier. A member without one sees **Free** with **No seat assigned** and **Plan managed by your organization**. There are no buy, plan, or cancel actions on this view.

Select the correct workspace before you review a balance or change a subscription. An organization's wallet, member allocations, and team subscription are separate from your qBraid Default wallet.
