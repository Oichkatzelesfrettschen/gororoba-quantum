# Unapproved QPU case: n21-orbit-rca

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-19T170452.672515Z`.
- [record.json](record.json) SHA-256: `f21bae24840ed975cae0a6269461b12b448321a5d4710f3e913670705b7ef313`.
- [isa.qpy](isa.qpy) SHA-256: `3dab923b6306cf8bc50eff8e8be549e9427a050abcbbae25a6d24edc21da8e10`.
- Experiment source digest: `422043ccbdc90743464086f1d775b1682bec255df22c0a175c7570a8bc07acdc`.
- Source commit: `ad53b4da4721bd490a8c8e0301856e722a487942`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.5.2 |
| qiskit-aer | 0.17.2 |
| qiskit-ibm-runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The N=21, base-4 family measures the change in the labeled two-phase-bit distribution when feed-forward is removed. Array labels are 00, 01, 10, 11 (index b0 + 2*b1). The preregistered score is P(01)-P(11) with feedback, minus the same score without feedback. Two phase bits provide a feedback diagnostic; they do not establish successful general order recovery, factoring advantage, or an asymptotic speedup.

The orbit families compile each controlled multiplier only on the orbit 1, 4, 16 of the work register, which supplies the order 3 to the circuit. They measure feed-forward in a two-round semiclassical QPE and perform no order finding or factoring (Smolin, Smith and Vargo, Nature 499, 163 (2013)). The window arms of n21-orbit-rca idle the control, read it a second time, or echo the work qubits during the first measurement and reset; the family configuration records their durations in dt.

--overlap-split replaces the window sweep with the bracketed nominal and window_delay pairs, the window_delay pair without its window barriers, so work-qubit gates may overlap the control's measure-plus-reset span under the backend scheduler, and qubit-2 spectators read at once, after an idle of the control's measure plus reset durations (window_delay_dt + reset_dt) with the unrecorded control in |+>, and across the reset_only reference. Removing the barriers lets the transpiler resynthesize the block around the window, so the unbracketed arm can play one CZ fewer than its bracketed twin (the routed feedback arms hold 43 CZ and 77 sx unbracketed against 44 CZ and 79 sx bracketed); fewer CZ raise its contrast, which biases window_overlap_loss against a pass, so a fail is unresolved rather than evidence that overlap costs nothing. A pass shows that overlap costs contrast magnitude on this calibration, not that it caused the 2026-10-13T083417 loss: the pin fixes the roles, and the calibration differs.

--pin-layout places logical qubit i on the i-th named qubit (control, then the work qubits of bits 1, 4 and 16) with one identity replica, so the roles are control 142, work bit 1 136, work bit 4 143, work bit 16 144.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_orbit_nominal_feedback | `[0.375, 0.25, 0.125, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_orbit_nominal_no_feedback | `[0.375, 0.125, 0.125, 0.375, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_orbit_window_delay_feedback | `[0.375, 0.25, 0.125, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_orbit_window_delay_no_feedback | `[0.375, 0.125, 0.125, 0.375, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_orbit_window_delay_unbracketed_feedback | `[0.375, 0.25, 0.125, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_orbit_window_delay_unbracketed_no_feedback | `[0.375, 0.125, 0.125, 0.375, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_immediate_x | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_immediate_y | `[0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_idle_x | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_idle_y | `[0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_reset_only_x | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| n21_spectator_reset_only_y | `[0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| n21_orbit_rca | ibm_fez | 2026-10-19T09:47:37-07:00 | 20261010 | `[142, 136, 143, 144]` | `[[142, 136, 143, 144]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "window_delay_dt": 415,
  "echo_half_dt": 502,
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "n21_orbit_rca": [
      {
        "136": 136,
        "142": 142,
        "143": 143,
        "144": 144
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### n21_orbit_nominal_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_nominal_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_nominal_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.192291259766; the simultaneous finite-simulation allowance is +/-0.0232831326643. The lower modeled value is 0.169008127101.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0801564096734; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0758165448185 (null 0 plus one-sided radius 0.0758165448185). The admitted alternative effect is 0.169008127101, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_orbit_window_delay_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_window_delay_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_window_delay_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.19100189209; the simultaneous finite-simulation allowance is +/-0.0232831326643. The lower modeled value is 0.167718759426.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0801564096734; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0758165448185 (null 0 plus one-sided radius 0.0758165448185). The admitted alternative effect is 0.167718759426, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_orbit_window_delay_unbracketed_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_window_delay_unbracketed_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_window_delay_unbracketed_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.193786621094; the simultaneous finite-simulation allowance is +/-0.0232831326643. The lower modeled value is 0.170503488429.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0801564096734; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0758165448185 (null 0 plus one-sided radius 0.0758165448185). The admitted alternative effect is 0.170503488429, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_spectator_immediate_x_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_immediate_x`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.00327301025391; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is -0.00254777291217.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

### n21_spectator_immediate_y_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_immediate_y`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.494812011719; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is 0.488991228553.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

### n21_spectator_idle_x_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_idle_x`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.00320434570312; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is -0.00261643746295.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

### n21_spectator_idle_y_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_idle_y`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.494819641113; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is 0.488998857947.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

### n21_spectator_reset_only_x_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_reset_only_x`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.00321197509766; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is -0.00260880806842.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

### n21_spectator_reset_only_y_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_reset_only_y`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.494262695312; the simultaneous finite-simulation allowance is +/-0.00582078316607. The lower modeled value is 0.488441912146.

At alpha 0.00555555555556, the two-sided confidence half-width is 0.0189541362046; requested precision is 0.08.

The search-wide simulation error probability is 0.01 across 36 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 12 | 98304 | 8.625010432 | 15 |

The cost model predicts 8.625010432 seconds. The per-job service ceilings sum to 15 seconds against an invocation cap of 15 seconds. The global reserve is 0 seconds; the saved quota reports 180 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 8192 | 1.0956e-05 | 5e-05 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_02 | 8192 | 1.0956e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 8192 | 1.2616e-05 | 5e-05 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_04 | 8192 | 1.2616e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 8192 | 1.2316e-05 | 5e-05 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_06 | 8192 | 1.2316e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_07 | 8192 | 5.052e-06 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_08 | 8192 | 5.052e-06 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_09 | 8192 | 8.396e-06 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_10 | 8192 | 8.396e-06 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_11 | 8192 | 6.712e-06 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_12 | 8192 | 6.712e-06 | 5e-05 | 0 | 0 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family n21-orbit-rca \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 15 \
  --rep-delay 5e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 131072 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 15.0 \
  --init-herald \
  --overlap-split \
  --pin-layout ibm_fez:142,136,143,144 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family n21-orbit-rca \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 15 \
  --rep-delay 5e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 131072 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 15.0 \
  --init-herald \
  --overlap-split \
  --pin-layout ibm_fez:142,136,143,144 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-19T170452.672515Z \
  --approved-record-sha256 f21bae24840ed975cae0a6269461b12b448321a5d4710f3e913670705b7ef313 \
  --submit
```
