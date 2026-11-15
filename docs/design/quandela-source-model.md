# Quandela source model: the stated visibility and the simulated one

`gororoba_quantum/quandela_source_model.py` computes the click visibility that Perceval's `NoiseModel(indistinguishability = M, g2)` simulates for two photons on a balanced beam splitter, V = 1 - P(both modes click) / 0.5, and the overlap M whose simulated V equals a stated figure.

## Mechanism

For the input |1,1> the noisy photon-number distribution has a two-photon sector, where the coincidence fraction gives V = M exactly, and multiphoton tails ((1,2), (2,1), (2,2)) that add coincidences. At g2 = 0 the click visibility equals M (the analytic (1 - M) / 2 coincidence probability); at g2 above 0 it falls below M by about g2. A forecast that passes a measured visibility as `indistinguishability` while its noise model also carries the measured g2 therefore simulates a visibility below the one it states (issue 888).

| M (passed) | g2 | simulated click V | offset |
|---|---|---|---|
| 0.8728 | 0.020 | 0.8537 | -0.0191 |
| 0.911 | 0.020 | 0.8915 | -0.0195 |
| 0.825 | 0.009 | 0.8167 | -0.0083 |
| 0.9438 | 0.00732 | 0.9366 | -0.0072 |

Computed with Perceval 1.3.1, SLOS, `BS()`, input |1,1>, no photon filter; `tests/test_quandela_source_model.py` pins each value to 5e-5 and pins the two-photon-sector visibility of each pair (the states (2,0), (1,1) and (0,2) renormalized) to M within 1e-12.

## Rule

- A new forecast whose stated figure is a click-coincidence visibility passes `overlap_for_click_visibility(stated, g2)` as `indistinguishability`, so the simulated visibility equals the stated one.
- The producers that pass the stated figure directly (`scripts/belenos_suppression_case.py`, `scripts/ascella_cz_tomography_case.py` and `scripts/qd_teleportation_rehearsal.py`, three `NoiseModel(indistinguishability=hom, g2=g2)` constructions) keep their bytes, since their retained cases and forecasts are digest-bound; for the four parameter pairs above, the two-mode source click visibility lies 0.007 to 0.020 below that input.
- The relation `M ~ (V_HOM + g2) / (1 - g2)` that `ascella-two-photon-associator-case.md` marks as unverified does not invert this model: it maps the click visibility 0.8537 back to 0.8916, where Perceval's own M is 0.8728.

## Open

Repository evidence leaves the convention unresolved. The retained Ascella in-situ result, 0.892 +- 0.004 against calibration HOM 0.890 (`docs/design/belenos-associator-visibility-case.md`, "The g2 convention is unresolved"), supports the interpretation that the reported HOM already carries the g2 contribution. The retained Belenos jobs of 2026-10-31 did not discriminate the interpretations: per-seed mesh spread inflated the uncertainty and the closure failed. Whether the HOM figure that a platform reports is a click-coincidence visibility, a two-photon-sector visibility or Quandela's own overlap estimate therefore stays open. The helper applies only when the supplied figure is a click-coincidence visibility; a follow-up must isolate the overlap from the mesh error and compare it with a contemporaneous calibration HOM. The definition of `V_HOM` in the source of the first-order relation was not read for this note.

`overlap_for_click_visibility` is a bisection whose final overlap bracket is at most 1e-12 wide, with the exception stated in its docstring at M = 1.
