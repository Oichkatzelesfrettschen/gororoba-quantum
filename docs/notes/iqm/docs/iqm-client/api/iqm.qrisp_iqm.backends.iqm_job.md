> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26a4d2a1b2c76e7ae400c95256c1902b02eca1b97e03137a91ed440179bdae74.

# iqm_job

Full path: iqm.qrisp_iqm.backends.iqm_job

Abstract base class for IQM job handles.

Defines shared status polling, cancellation, and result-retrieval logic that does not differ between gate-level and pulse-level submissions.

Classes

|  |  |
|----|----|
| [`IQMJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob") | ABC for wrapping IQM job trackers, shared by circuit-level and pulse-level jobs. |

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.backends.iqm_job](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-005ccea8aa2251d7027af1e7e55914568a11cceb.png)
