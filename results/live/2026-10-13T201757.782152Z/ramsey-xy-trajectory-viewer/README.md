# Ramsey X/Y trajectory viewer for the patch-window acquisition

Work in progress, kept on its own branch. `index.html` is a self-contained
offline viewer (inline SVG and JavaScript, no network requests, no external
fonts or scripts) of the 26 paired X/Y Ramsey points of record
`2026-10-13T201757.782152Z`: coordinates (X, Y, R, tau) with R = sqrt(X^2 + Y^2)
derived from X and Y, so the display has four coordinates and three measured
degrees of freedom. Dashed connectors between acquired idle settings are
interpolation, not measured evolution; echo and window detuning aliases spaced
by 500 kHz stay unresolved.

## Provenance and binding

- External build: `Reality_Ripple_4D_Trajectories.zip`, sha256 `30e7e2ce0af47d48f8c006b2f06862cb57b84263c620158f8bd5198da8600cad`,
  generated outside this repository from a derived-data extract of source
  snapshot `eb64ead`; its original README is `README.upstream.md`.
- Every plotted count (x_zero, y_zero per condition, qubit and executed idle)
  equals the corresponding point in `../patch-analysis.json`
  (sha256 `682600bda2319dc0b5c1548feddc11df91e9061a787f904a211a72503712052e`): 26 of 26 points match.
- `data/source_analysis.md` section II carries a correction: its "registered"
  table predates the collector-based correction of the findings.
- The derived media (mp4, gif, png previews, about 4 MB) are omitted;
  `build_visualization.py --video` regenerates them.

## Scope

The viewer shows local product-state Ramsey responses. It does not reconstruct
the orbit state, identify a phase mechanism, or establish a decay constant.
