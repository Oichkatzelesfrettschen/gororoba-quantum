> Full piece: [https://docs.openquantum.com/concepts/overview/](https://docs.openquantum.com/concepts/overview/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c05ddd1e5dc7fd1a9ac8ffa67987ce3c0b4a05c95e1176a4b7160d143a84db66.

# How Open Quantum Works

Open Quantum is a quantum computing job execution platform that provides access to real quantum processing units (QPUs) from leading hardware providers.

When you submit a quantum circuit through any of the SDKs:

1.  The circuit is uploaded and validated by the platform.
2.  A pricing quote is calculated based on the backend and shot count.
3.  Credits are deducted and the job enters the execution queue.
4.  The job is dispatched to the target QPU for execution.
5.  Results are validated and made available for download.

## Key Concepts

### Backends

Backends are the quantum hardware that execute your circuits. Each backend has a `short_code` (e.g., `"ionq:forte-1"`) that you use to target it. See [Backends](https://docs.openquantum.com/concepts/backends/) for details.

### Jobs

A job represents a single circuit execution request. See [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) for the full state diagram.

### Credits

Jobs are paid for using credits. New accounts receive \$50 of free Spark credits that refresh every 90 days. See [Credits](https://docs.openquantum.com/concepts/credits/) for details.

### Public and Private Compute

Open Quantum offers Public and Private Compute options. Visit the [pricing page](https://www.openquantum.com/pricing) for details. New accounts use Public Compute with free Spark credits.

### Organizations

Every job belongs to an organization. Your user account can belong to one or more organizations, each with its own credit balance and job quotas.

## Related Pages

- [Backends](https://docs.openquantum.com/concepts/backends/) -- Available quantum backends.
- [Job Lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/) -- Detailed job status flow.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- Pricing and credit system.
