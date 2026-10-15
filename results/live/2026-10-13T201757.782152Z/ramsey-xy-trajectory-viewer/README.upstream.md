# Reality Ripple: four-coordinate trajectory explorer

Open **index.html** in a browser. This is a new visualization of the supplied Fez characterization extract, not a new QPU run or a reconstruction of the full N21 state.

## Three views in one interactive scene

1. **4D movie:** position `(X, Y, R)`, with executed idle `τ` controlled by playback and the time slider.
2. **Spacetime tracks:** position `(X, Y, τ)` so the acquired time settings appear directly along a spatial display axis.
3. **4D to 3D projection:** normalize `(X, Y, R, τ)`, rotate in the X–τ, Y–τ and R–τ planes, and retain three projection coordinates. The live matrix is displayed. These rotations only change visualization coordinates.

`R = sqrt(X² + Y²)` is derived from the two measured quadratures; it is **not independently measured Z**. Consequently this is a four-coordinate embedding, not evidence of four independent physical dimensions. A single projection discards a coordinate. Changing the projection reveals geometry already encoded in the same observations, not new measured information.

Drag/swipe the scene to rotate the displayed 3D coordinates. Scroll or pinch to zoom. Filter by physical qubit and condition. Hover or tap measured points for counts, phase, and source marginal intervals. The viewer uses native SVG and JavaScript, so no WebGL, external fonts, third-party CDN, account, API key, or internet access is needed. Save the current scene using the SVG or PNG buttons.

## Time and connecting segments

The acquired idle settings are **0.004, 3.604, 5.604 and 7.604 microseconds**. Only plain Ramsey has the near-zero-idle point. There are 26 paired X/Y observations in eight condition–qubit trajectories.

**Default playback** steps only through those four acquired settings. Enable **Animate connecting segments** to move an illustrative guide between them. X and Y are interpolated linearly, and R is recomputed from them. Intermediate positions have no shot counts and receive no invented uncertainty. No trajectory is extrapolated before its first observed point.

Filled markers are acquired points. Circles denote Q136 and diamonds denote Q144. A ring marks the current point. The moving hollow marker between settings is interpolation, not data. Dashed connectors guide the eye; they do not establish the actual intervening quantum dynamics. Labels can be enabled after filtering to reduce overlap.

The time coordinate is returned-schedule idle exposure for separately prepared circuits. X and Y are distinct measurements with matching exposure. This is **not continuous tracking of one undisturbed state**, and browser playback time is not circuit time. Echo and window detuning aliases spaced by 500 kHz remain unresolved; no connector unwraps them.

## Source and integrity

Input: the supplied `Reality_Ripple_Fez_Measured_Results.zip` derived-data archive.

- Source snapshot: `eb64ead57b75beb07ba8018ccfbc1e6242c5ec21`.
- Executed source: `9b86a1349aa48cc3834ed446cbda7da55c3724e5`.
- Collected record: `results/live/2026-10-13T201757.782152Z`.
- Executed case digest: `ec6e86629948407640b5e7a66a2306cca8bd7d1004227f66de50aedee898cc2f`.
- The executed replacement differs from the previously approved case. This viewer does not alter that history.

Both input CSV hashes are verified against the supplied package manifest. All plotted X, Y, radius and principal-phase values are independently recomputed from the supplied integer counts and compared to the source fields. No measured point is invented, smoothed or clipped. The raw maximum radius slightly above one is retained as an uncorrected finite-sample estimator, not interpreted as a physical Bloch radius.

The original raw PUB files and QPY circuit archive were **not** independently rehashed by this visualization build. It uses the exact count fields already present in the supplied derived-data package. The source uncertainty fields are marginal Jeffreys 95% intervals, not the campaign's simultaneous Hoeffding bounds, and appear only at actual acquired points.

## Files

- `index.html`: self-contained vector-based interactive explorer.
- `previews/reality_ripple_4d_time.mp4`: time animation. Intermediate connector frames are explicitly labeled as illustrative.
- `previews/reality_ripple_4d_time.gif`: compact animation preview of the same movie.
- `previews/spacetime.png` / `.svg`: fixed spacetime view.
- `previews/four_coordinates.png` / `.svg`: fixed X/Y/R view; time is animated in the interactive version.
- `previews/native_scene.png` / `.svg`: scene exported using the interactive viewer's actual export controls.
- `previews/interactive_desktop.png`, `interactive_mobile.png`, `oblique_4d_projection.png`: browser screenshots.
- `data/ramsey_observations.csv`, `ramsey_fits_model_dependent.csv`: unchanged source tables.
- `data/measurements_4d.json`: embedded numerical data, explicitly recording derived coordinates.
- `data/source_manifest.json`, `source_analysis.md`: supplied provenance and source interpretation.
- `build_visualization.py`, `viewer_template.html`: reproducible build sources.
- `validation.json`, `browser_validation.json`: numerical checks and browser interaction checks.
- `verify_viewer.py`: optional browser smoke-test source.
- `manifest.json`: SHA-256 hashes of the delivered files; not an authorization certificate.

## Rebuild

The static Python rebuild needs NumPy and Matplotlib. Optional video rendering also needs ffmpeg available on PATH. The interactive HTML does not need these dependencies once built.

```sh
python build_visualization.py
python build_visualization.py --video
```

To regenerate the GIF from the MP4:

```sh
ffmpeg -y -i previews/reality_ripple_4d_time.mp4 \
  -vf 'fps=8,scale=760:-1:flags=lanczos' -loop 0 \
  previews/reality_ripple_4d_time.gif
```

Browser smoke checks exercised all three projections, time playback, interpolated labels, pre-start absence, qubit filtering, mobile layout, and the SVG/PNG export controls. Native SVG was chosen to avoid depending on WebGL support.

## Scientific scope

The geometry displays observed local-coherence responses and their ordered settings. It does not identify the N21 coherent-error mechanism, establish a new decay constant, reconstruct every phase of the orbit state, or measure a Casimir/ZPE force. Radius and phase are derived summaries of X/Y. Straight or curved display segments are not a physical propagation claim.
