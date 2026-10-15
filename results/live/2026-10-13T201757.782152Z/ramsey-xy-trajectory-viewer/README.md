# Ramsey X/Y trajectory viewer for the patch-window acquisition

`index.html` is a self-contained offline viewer (inline SVG and JavaScript,
no network requests, no external fonts or scripts) of the 26 paired X/Y
Ramsey points of record `2026-10-13T201757.782152Z`: coordinates
(X, Y, R, tau) with R = sqrt(X^2 + Y^2) derived from X and Y, so the display
has four coordinates and three measured degrees of freedom. Dashed
connectors between acquired idle settings are interpolation, not measured
evolution; echo and window detuning aliases spaced by 500 kHz stay
unresolved.

## Provenance and binding

- External build: `Reality_Ripple_4D_Trajectories.zip`, sha256
  `30e7e2ce0af47d48f8c006b2f06862cb57b84263c620158f8bd5198da8600cad`,
  generated outside this repository from a derived-data extract of source
  snapshot `eb64ead`. Every retained file keeps the archive's bytes, CSV line
  endings included (`.gitattributes`), and matches its sha256 in
  `manifest.json`; the archive's README is `README.upstream.md`, and this
  file replaces it.
- `check_viewer_binding.py` (gate core-263) recomputes those hashes and
  requires every plotted count (x_zero and y_zero with their shot counts,
  per condition, qubit and executed idle) to equal the corresponding point
  in `../patch-analysis.json`: 26 of 26 points.
- The derived media (mp4, gif, png and svg previews, about 4 MB) and the
  browser log are omitted; `build_visualization.py --video` regenerates the
  media, and `verify_viewer.py` repeats the browser check with Playwright and
  Chromium.

## Correction to data/source_analysis.md

Section II's table lists window control 0 and the work-B
measured/reset-only and paired/single comparisons as registered endpoints.
The registered family is the collector's ten rows in `../collect.json`
`family_analysis` (window control 1, spectator excess, work A only for the
reference comparisons); see `results/live/PATCH_WINDOW_FINDINGS.md`. The
other rows are descriptive.

## Scope

The viewer shows local product-state Ramsey responses. It does not reconstruct
the orbit state, identify a phase mechanism, or establish a decay constant.
