> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.hardwired.hardwired.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.hardwired.hardwired.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8901f049dc71e97737bed4027e7e55b163b11950a10c98a95ea16f57f22f9dbb.

# hardwired

Full path: iqm.qaoa.transpiler.hardwired.hardwired

Module containing “hard-wired” routing.

For problem sizes from 4 to 15, this creates the optimal [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") so that all 2-qubit interactions can be executed and the number of swaps is minimized. We believe this is the optimal routing strategy for fully / densely connected problems.

Functions

|  |  |
|----|----|
| [`hardwired_router`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router.html#iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router "iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router")(problem_bqm, qpu) | The function that creates an optimal routing for all-to-all connected problems, designed by hand. |
