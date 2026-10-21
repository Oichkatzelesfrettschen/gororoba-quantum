# Unapproved QPU case: n21-orbit-rca

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-1536` at 1536 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-21T081814.438624Z`.
- [record.json](record.json) SHA-256: `7efa7db8e62045987012f7bc6be7d6fa25712317a8b362e2ed66e899169a50a1`.
- [isa.qpy](isa.qpy) SHA-256: `988b2804ebf0ef5c1b388a8972cab776ed440224dbd7fbc756cc8cc21e040205`.
- Experiment source digest: `5b868417b95c90311bcb293488fc83cf84b99bb0947200e155837b05fafad954`.
- Source commit: `ba7b7e1522a43eead4317d981eed2a42f7a39c74`; sources_modified=`true`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

The source flag records changes anywhere in the experiment directory, including documentation and unmanifested files. Reproduction requires verification of every declared source against the experiment digest; the broad flag alone does not establish which source bytes differ from the recorded commit. A separate source-closure audit can establish that comparison without altering the retained record.

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

--segmented-delays-dt is the segmented ground sweep: qubit 2 read in several segments per shot with the control in |0>, each segment a herald, a preparation, an idle, a basis change and a readout, a reset of qubit 2 opening every segment after the first; X and Y alternate within each shot of an xy arm and a z arm reads Z after an X preparation; scripts/n21_q143_segmented_sweep.py holds the preregistered analysis whose closure the policy binds.

--pin-layout places logical qubit i on the i-th named qubit (control, then the work qubits of bits 1, 4 and 16) with one identity replica, so the roles are control 142, work bit 1 136, work bit 4 143, work bit 16 144.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_spectator_segmented_xy_d0 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d0 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d693 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d693 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d819 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d819 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d1386 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d1386 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d1638 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d1638 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d2079 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d2079 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d2457 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d2457 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d2772 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d2772 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d3276 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d3276 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d3465 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d3465 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d4095 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d4095 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d4158 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d4158 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d4851 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d4851 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d4914 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d4914 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d5544 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d5544 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d5733 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d5733 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d6237 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d6237 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d6552 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d6552 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d6930 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d6930 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d7371 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d7371 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d7623 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d7623 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d8190 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d8190 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d8316 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_z_d8316 | `{"encoding": "support", "length": 32768, "support": {"21840": 1.0}}` |
| n21_spectator_segmented_xy_d0_pre1250 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |
| n21_spectator_segmented_xy_d693_pre1250 | `{"encoding": "support", "length": 32768, "support": {"0": 0.125, "64": 0.125, "1024": 0.125, "1088": 0.125, "16384": 0.125, "16448": 0.125, "17408": 0.125, "17472": 0.125}}` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| n21_orbit_rca | ibm_fez | 2026-10-21T00:49:22-07:00 | 20261010 | `[142, 136, 143, 144]` | `[[142, 136, 143, 144]]` |

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

The saved endpoints preregister precision intervals.

### n21_spectator_segmented_xy_d0_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d0`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.00103759765625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is -0.0166643366957.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d0_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d0`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.986511230469; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.968809296117.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d693_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d693`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.017578125; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is -0.000123809351961.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d693_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d693`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.950256347656; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.932554413304.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d819_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d819`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0228881835938; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.00518624924179.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d819_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d819`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.942077636719; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.924375702367.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d1386_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d1386`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0347900390625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0170881047105.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d1386_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d1386`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.912719726562; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.895017792211.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d1638_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d1638`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.03955078125; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.021848846898.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d1638_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d1638`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.900573730469; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.882871796117.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d2079_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d2079`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0488891601562; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0311872258043.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d2079_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d2079`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.87939453125; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.861692596898.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d2457_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d2457`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0559692382812; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0382673039293.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d2457_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d2457`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.858154296875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.840452362523.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d2772_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d2772`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0601806640625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0424787297105.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d2772_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d2772`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.841979980469; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.824278046117.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d3276_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d3276`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0730590820312; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0553571476793.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d3276_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d3276`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.822082519531; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.804380585179.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d3465_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d3465`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0750732421875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0573713078355.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d3465_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d3465`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.814697265625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.796995331273.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d4095_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d4095`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0899658203125; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0722638859605.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d4095_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d4095`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.7861328125; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.768430878148.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d4158_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d4158`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0928344726562; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0751325383043.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d4158_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d4158`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.783569335938; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.765867401586.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d4851_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d4851`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.103881835938; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0861799015855.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d4851_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d4851`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.748596191406; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.730894257054.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d4914_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d4914`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.104370117188; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.0866681828355.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d4914_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d4914`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.745544433594; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.727842499242.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d5544_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d5544`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.118469238281; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.100767303929.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d5544_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d5544`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.718505859375; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.700803925023.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d5733_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d5733`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.120300292969; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.102598358617.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d5733_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d5733`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.7119140625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.694212128148.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d6237_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d6237`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.131530761719; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.113828827367.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d6237_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d6237`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.694030761719; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.676328827367.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d6552_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d6552`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.13623046875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.118528534398.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d6552_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d6552`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.678283691406; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.660581757054.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d6930_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d6930`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.14013671875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.122434784398.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d6930_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d6930`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.66259765625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.644895721898.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d7371_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d7371`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.148681640625; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.130979706273.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d7371_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d7371`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.645874023438; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.628172089086.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d7623_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d7623`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.149169921875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.131467987523.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d7623_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d7623`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.6318359375; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.614134003148.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d8190_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d8190`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.157958984375; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.140257050023.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d8190_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d8190`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.614196777344; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.596494842992.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d8316_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d8316`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.160522460938; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.142820526586.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_z_d8316_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_z_d8316`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.613586425781; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is 0.595884491429.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d0_pre1250_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d0_pre1250`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.000732421875; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is -0.016969512477.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

### n21_spectator_segmented_xy_d693_pre1250_one

Score terms (each member averages its recorded replicas):

- `n21_spectator_segmented_xy_d693_pre1250`: sign +1, labeled score vector `{"encoding": "bits", "length": 32768, "bits": [4], "table": [0.0, 1.0]}`.

The noise model predicts 0.0173950195312; the simultaneous finite-simulation allowance is +/-0.017701934352. The lower modeled value is -0.000306914820711.

At alpha 0.00104166666667, the two-sided confidence half-width is 0.0496081010828; requested precision is 0.08.

The search-wide simulation error probability is 0.01 across 144 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.620101263535. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 48 | 73728 | 15.516075776 | 30 |

The cost model predicts 15.516075776 seconds. The per-job service ceilings sum to 30 seconds against an invocation cap of 30 seconds. The global reserve is 0 seconds; the saved quota reports 117 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 1536 | 2.8628e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_02 | 1536 | 2.8484e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 1536 | 4.526e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_04 | 1536 | 4.5116e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 1536 | 4.8284e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_06 | 1536 | 4.814e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_07 | 1536 | 6.1892e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_08 | 1536 | 6.1748e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_09 | 1536 | 6.794e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_10 | 1536 | 6.7796e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_11 | 1536 | 7.8524e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_12 | 1536 | 7.838e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_13 | 1536 | 8.7596e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_14 | 1536 | 8.7452e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_15 | 1536 | 9.5156e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_16 | 1536 | 9.5012e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_17 | 1536 | 0.000107252 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_18 | 1536 | 0.000107108 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_19 | 1536 | 0.000111788 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_20 | 1536 | 0.000111644 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_21 | 1536 | 0.000126908 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_22 | 1536 | 0.000126764 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_23 | 1536 | 0.00012842 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_24 | 1536 | 0.000128276 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_25 | 1536 | 0.000145052 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_26 | 1536 | 0.000144908 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_27 | 1536 | 0.000146564 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_28 | 1536 | 0.00014642 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_29 | 1536 | 0.000161684 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_30 | 1536 | 0.00016154 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_31 | 1536 | 0.00016622 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_32 | 1536 | 0.000166076 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_33 | 1536 | 0.000178316 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_34 | 1536 | 0.000178172 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_35 | 1536 | 0.000185876 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_36 | 1536 | 0.000185732 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_37 | 1536 | 0.000194948 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_38 | 1536 | 0.000194804 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_39 | 1536 | 0.000205532 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_40 | 1536 | 0.000205388 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_41 | 1536 | 0.00021158 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_42 | 1536 | 0.000211436 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_43 | 1536 | 0.000225188 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_44 | 1536 | 0.000225044 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_45 | 1536 | 0.000228212 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_46 | 1536 | 0.000228068 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_47 | 1536 | 5.8628e-05 | 5e-05 | 0 | 0 |
| ibm_fez_dynamic_pub_48 | 1536 | 7.526e-05 | 5e-05 | 0 | 0 |

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
  --shots 1536 \
  --seeds 8 \
  --max-pending 100000 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --rep-delay 5e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1536 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 16384 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 30.0 \
  --init-herald \
  --ground-control-split \
  --segmented-delays-dt 0,693,819,1386,1638,2079,2457,2772,3276,3465,4095,4158,4851,4914,5544,5733,6237,6552,6930,7371,7623,8190,8316 \
  --segments 6 \
  --backaction-delays-dt 0,693 \
  --backaction-pre-idle-dt 1250 \
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
  --shots 1536 \
  --seeds 8 \
  --max-pending 100000 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --rep-delay 5e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1536 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 16384 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 30.0 \
  --init-herald \
  --ground-control-split \
  --segmented-delays-dt 0,693,819,1386,1638,2079,2457,2772,3276,3465,4095,4158,4851,4914,5544,5733,6237,6552,6930,7371,7623,8190,8316 \
  --segments 6 \
  --backaction-delays-dt 0,693 \
  --backaction-pre-idle-dt 1250 \
  --pin-layout ibm_fez:142,136,143,144 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-21T081814.438624Z \
  --approved-record-sha256 7efa7db8e62045987012f7bc6be7d6fa25712317a8b362e2ed66e899169a50a1 \
  --submit
```
