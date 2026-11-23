# IQM Garnet depth dependence of the Grover retention as a mechanism-free departure, mark 101 only

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
This is the variant B of [grover-plane-mirrored](../grover-plane-mirrored/CASE.md) (variant A, which adds the mark 011 arms and the
mark contrast); the owner chooses between them at the spend question. Everything not stated here is as in A: the
question 1, the response, the departure rule of mark 101, the gates, the overdispersion phi = 1.54, the calibration and the power.

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (copy in the case's `calibration/`). One job of 38
circuits at 16,000 shots (608,000 executions): mark 101 at depths 1 to 4 in 4, 4, 10 and 4 copies (22 circuits) and the eight readout
preparations in two copies each (16), built by `"$PYTHON" scripts/iqm_grover_plane_case.py build results/iqm/cases/grover-plane-mirrored-101`
with the design `DESIGN_101`. The order is the first half `FIRST_HALF_101` (the local optimum of single exchanges under the placement
rules, rerun by a test) repeated reversed, so every kind sits at mirrored positions and a kind of two pairs keeps 11 positions from its
mirror image. The `cases.json` sha256 is in `docs/evidence/iqm-garnet-grover-plane/variant_sizing.json`.

This run is a prospective replication or refutation of the retained depth-3 anomaly of mark 101 (eps 0.041 +- 0.011 under the plane
family). It does not identify a CZ, ZZ, PRX or leakage mechanism and claims no algorithmic novelty (Khan and Faryad, arXiv 2611.16398,
carry the plane reduction and the rotation-angle bounds).

## What differs from A

- No mark 011 arms, no `mark_011` block, no contrast: `analyze` reads the contrast as "not evaluated: the case carries no mark 011 arms".
  The mechanism patterns of the retained depth run (z -0.93 against a CZ phase, -3.14 against a PRX amplitude, post hoc) stay untested.
- The primary test is the same: the mark 101 arms, copies, planned shots and covariance are those of A, so the calibration (delta 8.0,
  false "coherent" at most 0.0078 +- 0.0015 over 99 cells, 0.00024 for "non-geometric, not a rotation") and the power (plane rotation
  |eps| = 0.02: 0.985 to 0.992; worst resolved truth PRX +0.8 percent at a 0.92, s 0.92: 0.964 +- 0.002; |eps| = 0.01: at worst 0.435) are
  equal to A's to the digit (a test compares the two prediction files).
- Cost, billing v4 sizing: 8.47 to 9.30 s of execution (v4_sum, v4_max, v3), expected billed 5.5 credits; `max_credits` 9.5 (19 billed
  seconds, cancel threshold 18 s) under the all-jobs schedule error, 8.5 under the Grover-jobs error. Margin of the threshold over the
  longest expected runtime (9.74 s): 3.4 s at a runtime overrun of 1.5 times and -3.4 s at 2.2 times, which the ceiling does not cover.
  The earlier headroom formula gave 9.0, below the v4 value. The `garnet:mock` compile estimate is required before approval and not read.

## Steps before a submission

As A: `build --live`, owner approval of the digest for the mock, mock run and collect, owner approval of the identical digest for Garnet,
`submit`, `collect`, `analyze`. Not run.

## Falsifier and residual risk

As A for the primary decision. B drops the only test that bears on a mechanism, so a "coherent" reading says that the plane rotates and
nothing about why; the retained 3 sigma contrast against a PRX amplitude stays a lead.
