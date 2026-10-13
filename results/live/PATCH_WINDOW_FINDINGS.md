# Patch-window characterization findings (ibm_fez, 2026-10-13)

Jobs db794cmil99s73fnjlk0, db794dor1c5c738k1a50, db794hmr6oqs73871tbg; record
2026-10-13T201757.782152Z; commit 9b86a13; charge 25 s (7 + 9 + 9) under 27 s.
All three jobs ran 21:22:00-21:22:58Z under one calibration (13:41:52 PDT), so
cross-job comparisons share calibration. Analysis: patch-analysis.json.

| Quantity | Work A (136) | Work B (144) |
|---|---|---|
| Plain Ramsey detuning (profile 95%, model-dependent) | +3.0 kHz [0.7, 4.8] | +1.0 kHz [-0.8, 2.7] |
| Plain phase at 7.6 us | 0.09 rad | 0.02 rad |
| Measure+reset window phases (control 0 or 1), 3.6-7.6 us | within 0.08 rad | within 0.08 rad |
| Measured minus reset-only, Y | -0.008 +/- 0.087 | +0.055 +/- 0.086 |
| Paired minus single, Y | -0.025 +/- 0.086 | -0.006 +/- 0.087 |
| Plain visibility at 7.6 us | 0.884 | 0.924 |
| Excited population after 7.6 us | 0.918 (T1 94 us predicts 0.922) | 0.891 (T1 157 us predicts 0.953) |
| Spectator / neighbor population after excitation | at background (<= 0.012) | at background |

Echo and window fits with phases near zero carry 500 kHz aliases (1 / 2 us
spacing) and stay unresolved; their per-point phases are all within 0.08 rad.

Orbit contrast differences (normal 95% half-width 0.042; registered Hoeffding
0.24): nominal 0.201, barrier 0.159, barrier+echo 0.184; barrier - nominal
-0.042 +/- 0.042, echo - barrier +0.025 +/- 0.042. No intervention selected.

## Interpretation

- The idle work qubits accumulate at most about 0.1 rad over the orbit window
  length, with or without a control measurement and reset, in either control
  state. Static detuning, measurement-associated
  phase, control-state dependence, paired-preparation ZZ and population
  exchange cannot produce the 0.59-0.70 rad kickback phase of the orbit runs.
  The fitted 3.0 kHz detuning on 136 accumulates 2 pi x 3.0 kHz x 7.6 us =
  0.14 rad; the measured plain phase at 7.6 us is 0.09 rad.
- Inference (moderate confidence): the orbit phase arises inside the orbit circuit's own gate
  sequence: coherent error in the compiled controlled-swap decompositions
  (CZ conditional phase or single-qubit frame errors) or in the deferred
  work-only gates, rather than in idle or measurement windows.
- Work B shows excess population loss at 7.6 us beyond its reported T1.
- Next diagnostic: phase tomography of the round-1 multiplier block alone
  (orbit prefix with and without the control measurement), not more window
  idle characterization.
- The inference weakens if the orbit window's executed duration or carrier
  qubits differ from the characterized 3.6-7.6 us idle on 136/144, or if the
  entangled orbit state couples to a mechanism a product-state Ramsey misses;
  the returned orbit schedules and round-1 block tomography test both.
- T1 and readout values come from the execution-time calibration 13:41:52 PDT
  (136: T1 94 us; 144: T1 157 us).

## Registered endpoints (simultaneous Hoeffding half-widths)

| Endpoint | Difference | Half-width | Verdict |
|---|---:|---:|---|
| work A echo - plain, Y at 1900 dt | -0.082 | 0.229 | no effect resolved |
| work B echo - plain, Y at 1900 dt | -0.010 | 0.229 | no effect resolved |
| work A window(c0) - plain, Y at 1400 dt | -0.143 | 0.229 | no effect resolved |
| work B window(c0) - plain, Y at 1400 dt | -0.021 | 0.229 | no effect resolved |
| work A control 1 - control 0, Y at 1400 dt | +0.055 | 0.229 | no effect resolved |
| work A / B measured - reset-only, Y | -0.008 / +0.055 | 0.229 | no effect resolved |
| work A / B paired - single, Y | -0.025 / -0.006 | 0.229 | no effect resolved |
| orbit barrier - nominal, contrast | -0.042 | 0.240 | no intervention selected |
| orbit echo - barrier, contrast | +0.025 | 0.240 | no intervention selected |

All measured phases lie near zero, so the cos((phi1 + phi2) / 2) factor of the
Y-only endpoints is near 1 and the favorable-orientation condition holds in
the data. The work-qubit idle of the window circuits is read from the returned
schedule; the control's measure and reset fit inside it (3.604 us at 900 dt).

## Comparison scope

This run measures window phase and orbit contrast; it does not measure orbit
kickback phase. The 0.59-0.70 rad figure comes from window job
db6uqdkvf2bc73d1sc80 under an earlier calibration, so the interpretation
compares across calibrations (the cross-job calibration issue tracks this).

## Provenance

The approved record 2026-10-13T195251.183877Z (4aaea17, experiment digest
a8d281df7ce6) was refused at submit three times for one cause: the
single-work-qubit references measured work A before work B's basis change, so
the static group held a dynamic circuit. Commit 9b86a13 reordered the basis
changes; the executed case is 2026-10-13T201720.224397Z (record sha256
ec6e86629948407640b5e7a66a2306cca8bd7d1004227f66de50aedee898cc2f, experiment
digest 7283f357a681). It was submitted on the owner's "go" before CI or review
ran on 9b86a13; CI later passed on all six shards.
