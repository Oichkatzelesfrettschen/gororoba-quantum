# Unapproved QPU case: state-prep-control

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-17T194115.872682Z`.
- [record.json](record.json) SHA-256: `f31a4c60fdd7c3bdaef6b9f0304d359ce83ed58c21c16615d1c86fd5408cbb88`.
- [isa.qpy](isa.qpy) SHA-256: `9756aff2fa7711d3fdd6afdc8d839a354725c95a2ead5480126f0c9e8e300580`.
- Experiment source digest: `734c65835b47ba99e4408126e54ff81889f7317c09f0f608691c9be9d13f638c`.
- Source commit: `97aad01e5a2171494fe9cb12913b062881842555`; sources_modified=`false`.
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

The state-prep-control family measures, on 14 qubits of ibm_kingston (the replica qubits of `results/live/2026-10-17T130242.718497Z/record.json`: 57, 65, 66, 67, 68, 69, 70, 104, 105, 106, 107, 117, 125, 126), the excited fraction each qubit carries after the Sampler's implicit initialization at the backend's default repetition delay. Three PUBs measure every qubit in each shot: A initializes and measures (residual excitation plus readout misassignment), B adds an active reset before the measure, and C applies an X before the measure (the |1> column of the assignment matrix). A and C share the static job; B, which the reset makes dynamic, runs in its own job with twirling and dynamical decoupling off.

Under the readout channel e10 = prob_meas1_prep0, e01 = prob_meas0_prep1, A reads (1 - eps) e10 + eps (1 - e01), so the initial excitation is eps = (A - e10) / (1 - e01 - e10) (diagnostic_experiments.state_prep_excitation), the value dynamic_density's prep_excitation and live_run's --prep-excitation take. The reset benefit A - B is positive only where initialization leaves more excitation than the reset's own misassignment. The calibration noise model starts every qubit in |0>, so it prices A at the readout error alone; the residual excitation is the device property this run measures, and only the device answers it.

Three two-sided precision contracts per qubit, 42 in all, split the family-wise alpha evenly and admit the design: half-width 0.025 on A and on C, 0.05 on A - B, Hoeffding radii valid under arbitrary dependence between the qubits of one shot. They price resolution, not an effect. The comparison of A between two repetition delays spans two jobs, so it is outside these contracts; the written addendum states that comparison and its decision rule.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| spc_prep0_q57 | `[1.0, 0.0]` |
| spc_x_q57 | `[0.0, 1.0]` |
| spc_reset_q57 | `[1.0, 0.0]` |
| spc_prep0_q65 | `[1.0, 0.0]` |
| spc_x_q65 | `[0.0, 1.0]` |
| spc_reset_q65 | `[1.0, 0.0]` |
| spc_prep0_q66 | `[1.0, 0.0]` |
| spc_x_q66 | `[0.0, 1.0]` |
| spc_reset_q66 | `[1.0, 0.0]` |
| spc_prep0_q67 | `[1.0, 0.0]` |
| spc_x_q67 | `[0.0, 1.0]` |
| spc_reset_q67 | `[1.0, 0.0]` |
| spc_prep0_q68 | `[1.0, 0.0]` |
| spc_x_q68 | `[0.0, 1.0]` |
| spc_reset_q68 | `[1.0, 0.0]` |
| spc_prep0_q69 | `[1.0, 0.0]` |
| spc_x_q69 | `[0.0, 1.0]` |
| spc_reset_q69 | `[1.0, 0.0]` |
| spc_prep0_q70 | `[1.0, 0.0]` |
| spc_x_q70 | `[0.0, 1.0]` |
| spc_reset_q70 | `[1.0, 0.0]` |
| spc_prep0_q104 | `[1.0, 0.0]` |
| spc_x_q104 | `[0.0, 1.0]` |
| spc_reset_q104 | `[1.0, 0.0]` |
| spc_prep0_q105 | `[1.0, 0.0]` |
| spc_x_q105 | `[0.0, 1.0]` |
| spc_reset_q105 | `[1.0, 0.0]` |
| spc_prep0_q106 | `[1.0, 0.0]` |
| spc_x_q106 | `[0.0, 1.0]` |
| spc_reset_q106 | `[1.0, 0.0]` |
| spc_prep0_q107 | `[1.0, 0.0]` |
| spc_x_q107 | `[0.0, 1.0]` |
| spc_reset_q107 | `[1.0, 0.0]` |
| spc_prep0_q117 | `[1.0, 0.0]` |
| spc_x_q117 | `[0.0, 1.0]` |
| spc_reset_q117 | `[1.0, 0.0]` |
| spc_prep0_q125 | `[1.0, 0.0]` |
| spc_x_q125 | `[0.0, 1.0]` |
| spc_reset_q125 | `[1.0, 0.0]` |
| spc_prep0_q126 | `[1.0, 0.0]` |
| spc_x_q126 | `[0.0, 1.0]` |
| spc_reset_q126 | `[1.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| state_prep_q57 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[57]` | `[[57]]` |
| state_prep_reset_q57 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[57]` | `[[57]]` |
| state_prep_q65 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[65]` | `[[65]]` |
| state_prep_reset_q65 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[65]` | `[[65]]` |
| state_prep_q66 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[66]` | `[[66]]` |
| state_prep_reset_q66 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[66]` | `[[66]]` |
| state_prep_q67 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[67]` | `[[67]]` |
| state_prep_reset_q67 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[67]` | `[[67]]` |
| state_prep_q68 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[68]` | `[[68]]` |
| state_prep_reset_q68 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[68]` | `[[68]]` |
| state_prep_q69 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[69]` | `[[69]]` |
| state_prep_reset_q69 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[69]` | `[[69]]` |
| state_prep_q70 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[70]` | `[[70]]` |
| state_prep_reset_q70 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[70]` | `[[70]]` |
| state_prep_q104 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[104]` | `[[104]]` |
| state_prep_reset_q104 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[104]` | `[[104]]` |
| state_prep_q105 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[105]` | `[[105]]` |
| state_prep_reset_q105 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[105]` | `[[105]]` |
| state_prep_q106 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[106]` | `[[106]]` |
| state_prep_reset_q106 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[106]` | `[[106]]` |
| state_prep_q107 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[107]` | `[[107]]` |
| state_prep_reset_q107 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[107]` | `[[107]]` |
| state_prep_q117 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[117]` | `[[117]]` |
| state_prep_reset_q117 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[117]` | `[[117]]` |
| state_prep_q125 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[125]` | `[[125]]` |
| state_prep_reset_q125 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[125]` | `[[125]]` |
| state_prep_q126 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[126]` | `[[126]]` |
| state_prep_reset_q126 | ibm_kingston | 2026-10-17T12:27:27-07:00 | 20261010 | `[126]` | `[[126]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    57,
    65,
    66,
    67,
    68,
    69,
    70,
    104,
    105,
    106,
    107,
    117,
    125,
    126
  ],
  "source_replicas": [
    [
      104,
      105,
      106,
      107,
      117,
      125,
      126
    ],
    [
      57,
      65,
      66,
      67,
      68,
      69,
      70
    ]
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "state_prep_q57": [
      {
        "57": 57
      }
    ],
    "state_prep_reset_q57": [
      {
        "57": 57
      }
    ],
    "state_prep_q65": [
      {
        "65": 65
      }
    ],
    "state_prep_reset_q65": [
      {
        "65": 65
      }
    ],
    "state_prep_q66": [
      {
        "66": 66
      }
    ],
    "state_prep_reset_q66": [
      {
        "66": 66
      }
    ],
    "state_prep_q67": [
      {
        "67": 67
      }
    ],
    "state_prep_reset_q67": [
      {
        "67": 67
      }
    ],
    "state_prep_q68": [
      {
        "68": 68
      }
    ],
    "state_prep_reset_q68": [
      {
        "68": 68
      }
    ],
    "state_prep_q69": [
      {
        "69": 69
      }
    ],
    "state_prep_reset_q69": [
      {
        "69": 69
      }
    ],
    "state_prep_q70": [
      {
        "70": 70
      }
    ],
    "state_prep_reset_q70": [
      {
        "70": 70
      }
    ],
    "state_prep_q104": [
      {
        "104": 104
      }
    ],
    "state_prep_reset_q104": [
      {
        "104": 104
      }
    ],
    "state_prep_q105": [
      {
        "105": 105
      }
    ],
    "state_prep_reset_q105": [
      {
        "105": 105
      }
    ],
    "state_prep_q106": [
      {
        "106": 106
      }
    ],
    "state_prep_reset_q106": [
      {
        "106": 106
      }
    ],
    "state_prep_q107": [
      {
        "107": 107
      }
    ],
    "state_prep_reset_q107": [
      {
        "107": 107
      }
    ],
    "state_prep_q117": [
      {
        "117": 117
      }
    ],
    "state_prep_reset_q117": [
      {
        "117": 117
      }
    ],
    "state_prep_q125": [
      {
        "125": 125
      }
    ],
    "state_prep_reset_q125": [
      {
        "125": 125
      }
    ],
    "state_prep_q126": [
      {
        "126": 126
      }
    ],
    "state_prep_reset_q126": [
      {
        "126": 126
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### spc_excited_q57

Score terms (each member averages its recorded replicas):

- `spc_prep0_q57`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00445556640625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.00815519854311.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q57

Score terms (each member averages its recorded replicas):

- `spc_prep0_q57`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q57`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000579833984375; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0246416959143.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q57

Score terms (each member averages its recorded replicas):

- `spc_x_q57`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.995086669922; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.982475904973.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q65

Score terms (each member averages its recorded replicas):

- `spc_prep0_q65`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00491333007812; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.00769743487123.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q65

Score terms (each member averages its recorded replicas):

- `spc_prep0_q65`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q65`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0006103515625; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0246111783362.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q65

Score terms (each member averages its recorded replicas):

- `spc_x_q65`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986297607422; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.973686842473.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q66

Score terms (each member averages its recorded replicas):

- `spc_prep0_q66`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0114205794025.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q66

Score terms (each member averages its recorded replicas):

- `spc_prep0_q66`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q66`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.0003662109375; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0255877408362.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q66

Score terms (each member averages its recorded replicas):

- `spc_x_q66`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.990051269531; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.977440504582.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q67

Score terms (each member averages its recorded replicas):

- `spc_prep0_q67`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0120614485431.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q67

Score terms (each member averages its recorded replicas):

- `spc_prep0_q67`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q67`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.00018310546875; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0254046353675.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q67

Score terms (each member averages its recorded replicas):

- `spc_x_q67`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.990509033203; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.977898268254.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q68

Score terms (each member averages its recorded replicas):

- `spc_prep0_q68`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.00836882158998.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q68

Score terms (each member averages its recorded replicas):

- `spc_prep0_q68`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q68`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00048828125; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0247332486487.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q68

Score terms (each member averages its recorded replicas):

- `spc_x_q68`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986907958984; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.974297194035.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q69

Score terms (each member averages its recorded replicas):

- `spc_prep0_q69`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00778198242188; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.00482878252748.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q69

Score terms (each member averages its recorded replicas):

- `spc_prep0_q69`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q69`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0249773892737.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q69

Score terms (each member averages its recorded replicas):

- `spc_x_q69`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986175537109; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.97356477216.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q70

Score terms (each member averages its recorded replicas):

- `spc_prep0_q70`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0198669433594; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.00725617841002.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q70

Score terms (each member averages its recorded replicas):

- `spc_prep0_q70`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q70`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000946044921875; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0242754849768.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q70

Score terms (each member averages its recorded replicas):

- `spc_x_q70`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982666015625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.970055250676.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q104

Score terms (each member averages its recorded replicas):

- `spc_prep0_q104`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0163269042969; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.00371613934752.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q104

Score terms (each member averages its recorded replicas):

- `spc_prep0_q104`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q104`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0246722134925.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q104

Score terms (each member averages its recorded replicas):

- `spc_x_q104`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983978271484; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.971367506535.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q105

Score terms (each member averages its recorded replicas):

- `spc_prep0_q105`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0123666243244.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q105

Score terms (each member averages its recorded replicas):

- `spc_prep0_q105`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q105`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.00030517578125; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.02552670568.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q105

Score terms (each member averages its recorded replicas):

- `spc_x_q105`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.988525390625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.975914625676.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q106

Score terms (each member averages its recorded replicas):

- `spc_prep0_q106`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0120614485431.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q106

Score terms (each member averages its recorded replicas):

- `spc_prep0_q106`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q106`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.00018310546875; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0254046353675.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q106

Score terms (each member averages its recorded replicas):

- `spc_x_q106`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98828125; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.975670485051.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q107

Score terms (each member averages its recorded replicas):

- `spc_prep0_q107`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.00696501299623.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q107

Score terms (each member averages its recorded replicas):

- `spc_prep0_q107`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q107`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000732421875; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0244891080237.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q107

Score terms (each member averages its recorded replicas):

- `spc_x_q107`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.977722167969; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.965111403019.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q117

Score terms (each member averages its recorded replicas):

- `spc_prep0_q117`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0123666243244.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q117

Score terms (each member averages its recorded replicas):

- `spc_prep0_q117`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q117`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.00030517578125; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.02552670568.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q117

Score terms (each member averages its recorded replicas):

- `spc_x_q117`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.992706298828; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.980095533879.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q125

Score terms (each member averages its recorded replicas):

- `spc_prep0_q125`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0187377929688; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.00612702801939.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q125

Score terms (each member averages its recorded replicas):

- `spc_prep0_q125`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q125`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00149536132812; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0237261685706.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q125

Score terms (each member averages its recorded replicas):

- `spc_x_q125`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.972015380859; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.95940461591.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_excited_q126

Score terms (each member averages its recorded replicas):

- `spc_prep0_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is -0.0101388411212.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

### spc_reset_benefit_q126

Score terms (each member averages its recorded replicas):

- `spc_prep0_q126`: sign +1, labeled score vector `[0.0, 1.0]`.
- `spc_reset_q126`: sign -1, labeled score vector `[0.0, 1.0]`.

The noise model predicts -0.000152587890625; the simultaneous finite-simulation allowance is +/-0.0252215298987. The lower modeled value is -0.0253741177893.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0445235636265; requested precision is 0.05.

### spc_one_column_q126

Score terms (each member averages its recorded replicas):

- `spc_x_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.992340087891; the simultaneous finite-simulation allowance is +/-0.0126107649494. The lower modeled value is 0.979729322941.

At alpha 0.00119047619048, the two-sided confidence half-width is 0.0212903871039; requested precision is 0.025.

The search-wide simulation error probability is 0.01 across 168 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.890471272531. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 1 | 8192 | 4.383979264 | 8 |
| ibm_kingston/static/1 | 2 | 16384 | 6.431979264 | 8 |

The cost model predicts 10.815958528 seconds. The per-job service ceilings sum to 16 seconds against an invocation cap of 16 seconds. The global reserve is 60 seconds; the saved quota reports 266 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 8192 | 4.392e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 8192 | 2.18e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_02 | 8192 | 2.212e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family state-prep-control \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 16.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family state-prep-control \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 16.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-17T194115.872682Z \
  --approved-record-sha256 f31a4c60fdd7c3bdaef6b9f0304d359ce83ed58c21c16615d1c86fd5408cbb88 \
  --submit
```
