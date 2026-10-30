# Kaggle TPU submission: why a pushed TPU kernel stays QUEUED, and a checklist that runs

Scope: read-only research. No kernel was pushed, run or cancelled, and no state-changing Kaggle API call was made.
Observed case: private script kernel `OWNER/gororoba-...` (public slug only), pushed 2026-10-29 15:10 UTC with
`{"kernel_type":"script","language":"python","is_private":true,"enable_gpu":false,"enable_tpu":true,"enable_internet":true,"machine_shape":"TpuV5E8"}`,
QUEUED until 21:10 UTC, `tpu_quota` time_used 7,390 s of 72,000 s.

## Short answer

The most likely reason the kernel stayed queued is capacity: a TPU version waits for a TPU VM in a shared pool, and the wait can run for hours. Confidence: medium (about 60 percent). The repo's own record shows that a TPU-classified version in this account reads QUEUED with zero quota use until a VM is assigned (docs/notes/kaggle/tpu-research.md, section 3 "After verification": QUEUED for 7 h 08 min with no position shown). Forum thread 745817 is titled "TPU session queued for 14+ hours - resource shortage or frozen instance?" (Kaggle product feedback; body not retrieved). Lower-ranked causes: (a) a stale TPU session in the account's single batch slot, about 20 percent; (b) the account's identity verification state, about 15 percent. The repo note previously ranked identity verification as the leading cause; that ranking applied to the CPU-fallback symptom (TPU requests silently run on a 4-core CPU image). Our kernel did not fall back. It queued, which means the server classified it as TPU. That moves identity verification down the list.

What would confirm capacity: the version page (or `kernels.KernelsService/ListKernelVersions`, `run.isTpuEnabled` true) keeps "Queued..." with no position for several hours, and the same push succeeds after a retry with no other TPU session on the account. Confirmation signal for the slot cause: the account has another version or interactive session with accelerator TPU that is QUEUED or RUNNING at 15:10 UTC; `kaggle kernels status` on each listed kernel shows it. Ruling out the slot cause: no other TPU session exists. Ruling out verification: the account settings page shows identity verification complete (or the push comes back on CPU).

Cheap next step (no state change): list the account's kernels with `kaggle kernels list --mine` and check the status of every kernel whose metadata has a TPU machine shape. Do not cancel anything from this research step.

## Checklist for a submission that runs

1. Kernel metadata. Use `machine_shape` as the only accelerator field: `"machine_shape": "TpuV5E8"`, `"kernel_type": "script"` (or `"notebook"`), `"enable_gpu": false`. Source: kaggle-api docs/kernels_metadata.md (https://github.com/Kaggle/kaggle-api/blob/main/docs/kernels_metadata.md) lists `machine_shape` with `TpuV5E8` as the documented TPU example and does not document `enable_tpu` at all. Repo: docs/notes/kaggle/interfaces.md lines 106-107 mark `enable_tpu` as deprecated for `machine_shape`.
2. Drop `enable_tpu` from the metadata. Its presence is harmless in the observed runs, but the documented contract does not list it. Confidence on "harmless": low (not tested in isolation).
3. No image pin. Remove `docker_image` and `docker_image_pinning_type` from the metadata, and remove any `dockerImageVersionId` from a notebook's metadata. Source: kaggle-api issue 1197 (https://github.com/Kaggle/kaggle-api/issues/1197), per its summary, the pinned CPU/GPU image overrides the TPU VM environment; the summary says the fix landed in PR 1219 (a fetch summary, not checked against the PR itself). Repo: docs/notes/kaggle/tpu-research.md, the table "Before verification" row for `docker_image`.
4. Identity verification. Complete it for the account before pushing. Source: repo docs/notes/kaggle/tpu-research.md, section 1 and section 3 (the editor's session panel says "Some accelerators, such as TPUs, require identity verification"). Web sources found in this research name only phone verification; no public Kaggle page confirmed Persona. Treat the Persona wording as the repo's measured observation, not a public rule.
5. Accelerator from the CLI. Either set `machine_shape` in metadata or pass `kaggle kernels push -p DIR --accelerator TpuV5E8`. Both fill the same request field (docs/notes/kaggle/interfaces.md, "Accelerator, image and timeout fields"). Use one route only, and prefer the metadata field so the pushed bytes show the choice.
6. One TPU batch session per account. A second TPU push while one is live is refused with "Maximum batch TPU session count of 1 reached" (docs/notes/kaggle/tpu-research.md, section 3 table). Check the account's kernels for a live TPU version before every push. Source for the limit: kaggle-api issue 1197 summary, "limited to one active or queued batch TPU session per user".
7. Expect a queue. Budget hours, not minutes. Source: issue 1197 (staff: batch TPU runs "can queue and start more slowly than interactive ones"); forum topics 745817 and 743783 (titles only fetched). Interactive TPU requests also queue; the editor showed "You are #524 in the queue" (tpu-research.md, "Interactive versus batch"), so queue position is visible only in the editor.
8. Internet. The observed TPU run used `enable_internet: true`. No source read here says internet affects TPU allocation. Keep it on only if the job needs it, and do not expect it to change queue time.
9. Notebook versus script. No source found that says one type gets a TPU faster. Issue 1197 used a notebook; the repo's TPU probes used both. Use `script` for a batch job (no editor state, fewer moving parts).
10. CLI version. The fix path in issue 1197 cites kagglesdk PR 1192 (merged 2026-09-11) and PR 1219. Record `kaggle --version` with the push. Upgrade to a release that includes PR 1219 before retrying. Release number not confirmed in this research (no release page was readable).
11. Verify it ran on a TPU. First output cell must show a TPU VM: `os.cpu_count()` around 96 and about 330 GB RAM, `/dev/accel*` or vendor-1ae0 PCI devices present, `ISTPUVM=1`, `jax.devices()` listing 8 TPU devices (tpu-research.md, section 1 table). A 4-core, 30 GB host means a CPU fallback.
12. Monitor without polling monitors. Read status with `kaggle kernels status` at intervals, or a single self-exiting shell loop per repo rule; do not keep the session attached while queued (an attached queued session bills until idle timeout, per tpu-research.md).

## Unknown

- Current Kaggle TPU docs body (https://www.kaggle.com/docs/tpu): the fetch returned only the title. TPU types, weekly quota, verification wording and any one-session statement are unconfirmed on the page itself.
- Whether `enable_tpu` is ignored or harmful when `machine_shape` is set (not tested).
- Whether PR 1219 merged and in which CLI release; the fetched summary states "closed on Oct 29, 2026", which needs a direct check on the issue page.
- Typical TPU queue durations; forum bodies for 745817 and 743783 were not readable.
- Whether a notebook or script type, or internet on or off, changes allocation (no source found).
- Whether the account's earlier successful TPU kernel ran under verified identity; the repo does not record it.
- Persona as the verification vendor: found only in the repo's measured observation, not in a public source.

## Sources

- docs/notes/kaggle/tpu-research.md (repo; sections 1, 2, 3 and "Interactive versus batch")
- docs/notes/kaggle/interfaces.md (repo; accelerator field table)
- docs/notes/kaggle/jax-bridge-structure-report.md, lines 187-193 (repo; TpuV5E8 batch slot)
- https://github.com/Kaggle/kaggle-api/blob/main/docs/kernels_metadata.md (fetched; summary)
- https://github.com/Kaggle/kaggle-api/issues/1197 (fetched; summary)
- https://www.kaggle.com/docs/tpu (fetched; title only)
- https://www.kaggle.com/discussions/product-feedback/745817 (fetched; title only)
- Web search results (third-party, unverified): skills.sh kaggle-environment, withone.ai Kaggle API page
