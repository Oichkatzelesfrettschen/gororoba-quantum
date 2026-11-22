# Garnet billing: v2 scored on every retained active-reset job, and a refit

`billing_v3.py` reads every retained active-reset Garnet QPU job (sixteen: the twelve that
`scripts/iqm_measurement_sequence.py` fits as `BILLING_MODELS["v2"]` and the four of 2026-11-20 and 2026-11-21) and
writes `billing_v3.json`. Gate `core-iqm-billing-v3-replay` reruns it and compares the bytes. It decides nothing:
`BILLING_MODELS` gains a refit in the change that first sizes a Garnet case from it.

## Readings

- v2 over-predicts each of the four later jobs: grover-line-ccz by 0.152 s, packed Pauli by 0.226 s, Grover depth by
  0.289 s and sedenion by 0.039 s. The packed and Grover-depth jobs fall outside v2's 0.17 s band, on the safe side
  of a ceiling.
- Runtime exceeded execution by at most 0.436857 s (the Grover depth job), above v2's 0.42 s margin.
- The same three terms refitted over all sixteen jobs: 0.13471 s fixed, 0.00000762001 s per circuit-shot,
  0.00000646197 s per mid-circuit record; largest residual 0.227005 s.
- Five candidate fourth terms, scored by two leave-one-out criteria (s), because no selection rule was fixed before
  the refit:

  | fit | largest residual | largest leave-one-out, all jobs | the same without the main pinching run |
  |---|---|---|---|
  | v3 | 0.227005 | 4.04284 | 0.252403 |
  | v3_herald | 0.25795 | 3.38463 | 0.293192 |
  | v3_curvature | 0.203149 | 2.37713 | 0.564419 |
  | v3_cohort | 0.163284 | 2.40907 | 0.181534 |
  | v3_circuits | 0.158005 | 2.31597 | 0.189041 |
  | v3_schedule | 0.164466 | 1.88999 | 0.191458 |

  Over all jobs every fourth term lowers the largest leave-one-out residual, because each one moves the prediction of
  the main pinching run (`01a175ac-da6c`), the only job with many mid-circuit records and the anchor of the per-record
  term; leaving it out mispredicts it by 4.04 s under three terms. Over the other jobs, the cohort term (the four
  later jobs run 0.173 s faster), a per-circuit term and a per-schedule-second term lower it, and the
  heralding and curvature terms raise it; the curvature term rests on the largest job (`01a167ac-e6f3`, 320,000
  circuit-shots). The refit adopts no term. hypothesis: the later jobs run faster by a cohort shift or a per-circuit
  saving; a small-circuit Garnet job separates the two, and a measure-heavy job tests the per-record term.
- Runtime exceeds execution by exactly the job's `compilation_seconds` on all sixteen jobs (difference below 1e-15 s),
  so the margin a ceiling needs above execution is the compilation time, at most 0.436857 s here.
- The 37.5 us per circuit-shot of `scripts/iqm_signed_probe.py` (`ACTIVE_SHOT_SECONDS`) is the reset pilot's whole
  execution, 0.149965 s, over its 4000 circuit-shots (job `01a16583-43fc`); the fit puts most of it in the fixed
  term. Four replayed case builders (gates core-638, core-682, core-773, core-777) still price shots with it, so it
  keeps its value there; a new case sizes from a mock compile estimate and the refit.

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-billing-v3/billing_v3.py OUT.json
```
