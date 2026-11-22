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
- A fourth term earns its place only when it lowers the largest leave-one-out residual over the jobs other than the
  main pinching run (`01a175ac-da6c`, the only job with many mid-circuit records). Three terms give
  0.252403 s; a heralding term 0.293192 s; a curvature in job size 0.564419 s. Neither
  earns its place.
- Leaving the main pinching run out mispredicts it by 4.04 s: the per-record term rests on that one run, as v2's
  own comment says. A measure-heavy job is still the test of it.
- The 37.5 us per circuit-shot of `scripts/iqm_signed_probe.py` (`ACTIVE_SHOT_SECONDS`) is the reset pilot's whole
  execution, 0.149965 s, over its 4000 circuit-shots (job `01a16583-43fc`); the fit puts most of it in the fixed
  term. Four replayed case builders (gates core-638, core-682, core-773, core-777) still price shots with it, so it
  keeps its value there; a new case sizes from a mock compile estimate and the refit.

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-billing-v3/billing_v3.py OUT.json
```
