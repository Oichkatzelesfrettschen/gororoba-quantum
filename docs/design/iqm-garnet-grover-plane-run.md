# IQM Garnet Grover-plane run: variant B, mark 101

Variant B of the plane case ([case record](../../results/iqm/proposals/grover-plane-mirrored-101/CASE.md), model in
[iqm-garnet-grover-plane-model.md](iqm-garnet-grover-plane-model.md)) ran on Garnet as job
`01a2093b-2503-756c-ab56-6621c703e128` (4.5 credits billed, 9.5 approved) after the `garnet:mock` job
`01a20936-7042-7619-89bd-fdc02fc06fd0` (compile estimate 9.66 s; `analyze` refuses a mock run by design). The run
directories are
`results/iqm/runs/2026-11-23T162638Z-garnet-grover-plane-mirrored-101-grover` and
`results/iqm/runs/2026-11-23T162130Z-garnet_mock-grover-plane-mirrored-101-grover`; each holds the submitted
`cases.json`, `prediction.json`, circuits and calibration copy, so the analysis reads the run directory as its own
case directory.

## Calibration set

Three sets appear in these records:

- The committed case directory `results/iqm/cases/grover-plane-mirrored-101/` holds the build on calibration set
  `a0e725eb`.
- The live rebuild before the submissions read Garnet's current set,
  `2951733a-f569-452e-92bc-44397d6a192e`. Both run directories carry its bytes (cases.json sha256 ccdff667...), and the
  Garnet job compiled and ran on that set, so the model response of the analysis matches the calibration of the run.
- `ef4df2bb` is the calibration the `garnet:mock` station reports for its own compilation (the mock job record), not
  a build of the case.

## Result

`scripts/iqm_grover_plane_case.py analyze` writes
[results/iqm/grover_plane_mirrored_101_analysis.json](../../results/iqm/grover_plane_mirrored_101_analysis.json);
gate core-iqm-grover-plane-run-replay recomputes it and compares every byte. The record reads:

- Departure: "not evaluated: the reading depends on one mirror pair". Dropping the depth-4 pair 0 reads "unresolved"
  (the influence gate does not stand).
- Before the gates the reading is "geometric": T = 1.797 against delta 8.0.
- The rotation fit gives eps = -0.00305 +- 0.00256 per iteration, and rotation_adequate is false.
- Heterogeneity is 8.09 on 7 degrees of freedom (threshold 18.48).
- The fixed calibrated response gives chi2_model = 270.49. The geometric fit, with a and s free, lowers it to 104.27
  (a = 0.9074, s = 1.0497); the rotation fit gives 102.47 (a = 0.9172, s = 1.0423, eps as above).
- The readout check passed.
- The mark 011 contrast is "not evaluated: the case carries no mark 011 arms".

The reading stops at these facts; the claim that interprets them is a later change.
