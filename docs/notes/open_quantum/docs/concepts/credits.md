> Full piece: [https://docs.openquantum.com/concepts/credits/](https://docs.openquantum.com/concepts/credits/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f30ad8f5fa2c479a02b15b232a544428d6aa7d33fe7260d8ad9cab05ca59492c.

# Credits

Open Quantum uses a credit-based pricing system. Credits are deducted when jobs are submitted and refunded automatically if jobs fail or are canceled.

## Credit Types

| Type | Description | Usage | Expiration |
|----|----|----|----|
| **Spark** | Free or promotional credits. Granted on signup and through promotions. | Public execution plan only. | 90 days |
| **Full** | Purchased credits via Stripe. | Any execution plan (Public or Private). | 12 months |

Tip

New accounts receive \$50 of free Spark credits to get started. Spark credits refresh every 90 days, so you can continue experimenting even after your initial credits expire.

## How Pricing Works

Job pricing is calculated during the preparation phase based on the backend, shot count, execution plan, and queue priority. The exact credit cost is returned as a quote before the job is submitted.

Visit the [Open Quantum pricing page](https://www.openquantum.com/pricing) for current rates by backend and plan.

Public Compute plans qualify for use with Spark credits and are approximately half the price of retail (Private) plans.

Note

The exact pricing quote is returned during job preparation. With `"auto"`, the SDKs select the cheapest available plan and the cheapest queue priority. That pair is often Public + Standard. Friendly names (`"public"`, `"private"`, `"standard"`, `"priority"`, `"instant"`), enums, and UUIDs select that option exactly.

## Execution Plans

Open Quantum offers two execution paths:

| Plan | Description | Credit Types Accepted |
|----|----|----|
| **Public Compute** | Powered by [qBitTensor Labs](https://qbittensorlabs.com), which provides subsidized access to quantum hardware at approximately half the cost of retail. Shared queue. | Spark and Full |
| **Private Compute** | Managed infrastructure through trusted providers. Dedicated queues and priority execution. | Full only |

Core SDKPennyLane Plugin

``` python
from openquantum_sdk.enums import ExecutionPlanType

config = JobSubmissionConfig(
    backend_class_id="ionq:forte-1",
    name="My Job",
    job_subcategory_id="oth:oth",
    shots=1024,
    execution_plan=ExecutionPlanType.PUBLIC,
)
```

``` python
dev = qml.device("openquantum.device", wires=2, shots=1024,
                  backend="ionq:forte-1", execution_plan="public")
```

## Queue Priorities

| Priority | Surcharge | Description |
|----|----|----|
| **Standard** | 0 credits | No extra charge. Jobs run in FIFO order. |
| **Priority** | A small additional credit fee | Higher priority in the queue. Reduced wait time. See the [pricing page](https://www.openquantum.com/pricing) for current rates. |
| **Instant** | The largest additional credit fee | Highest priority and the shortest queue wait. See the [pricing page](https://www.openquantum.com/pricing) for current rates. |

## Credit Consumption

When a job is submitted:

1.  The platform calculates the total cost from the preparation quote.
2.  Credits are deducted from the organization's credit batches in FIFO order (earliest expiring batch first).
3.  For **Public** plans: Spark credits are consumed first, then Full credits.
4.  For **Private** plans: Only Full credits are consumed.

## Refunds

Credits are automatically refunded when:

- A job **fails** at any stage.
- A user **cancels** a Pending job.

Refunds restore credits to the original batches they were consumed from.

Note

Refunds are automatic. You do not need to request them.

## Purchasing Credits

Full credits can be purchased through the [Open Quantum Portal](https://www.openquantum.com):

1.  Navigate to **Credits**.
2.  Select a credit amount.
3.  Complete the purchase via Stripe.
4.  Credits are added to your organization's balance immediately.

**Earn more credits:** You can earn additional Spark credits through referrals -- bonus credits each time someone signs up with your referral link.

## Related Pages

- [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) -- How credits are deducted and refunded during job execution.
- [Core SDK Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Setting execution plan and queue priority.
- [PennyLane Device Options](https://docs.openquantum.com/pennylane-plugin/device-options/) -- Setting `execution_plan` and `queue_priority`.
