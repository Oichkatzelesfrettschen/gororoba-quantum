# Unapproved QPU case: state-prep-control

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-32768` at 32768 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-26T190257.591387Z`.
- [record.json](record.json) SHA-256: `eb5e9b4666e733a794da15266cbeff4ca61c5b1a49e4d1a75595b344d44ac55a`.
- [isa.qpy](isa.qpy) SHA-256: `2d6065784ae776743cffa8e1586e79fcba2a65b9bc5e53755cb5eccf77e0b073`.
- Experiment source digest: `68bba981397229331f52dbdc750ca36d98d8a8f4722b59856bfe38a26dc276c1`.
- Source commit: `c08555245d6f5f0892cda833dcfdf18ff4c7b5ae`; sources_modified=`false`.
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

The state-prep-control family measures, on 69 qubits of ibm_kingston (the declared layout: 58, 71, 72, 33, 39, 53, 3, 16, 23, 17, 27, 28, 141, 142, 143, 15, 19, 35, 60, 61, 62, 151, 152, 153, 82, 83, 96, 38, 49, 50, 105, 106, 107, 118, 129, 128, 100, 101, 102, 55, 59, 75, 78, 89, 90, 66, 67, 68, 42, 43, 44, 10, 11, 12, 79, 93, 92, 132, 133, 134, 124, 125, 126, 98, 111, 110, 147, 148, 149), the excited fraction each qubit carries after the Sampler's implicit initialization at a requested repetition delay of 20 us (`--rep-delay 2e-05`). One PUB measures every qubit in each shot: A initializes and measures (residual excitation plus readout misassignment). A runs in one static job. The run selects the arms prep0 (`--state-prep-arms prep0`).

Under the readout channel e10 = prob_meas1_prep0, e01 = prob_meas0_prep1, A reads (1 - eps) e10 + eps (1 - e01), so the initial excitation is eps = (A - e10) / (1 - e01 - e10) (diagnostic_experiments.state_prep_excitation), the value dynamic_density's prep_excitation and live_run's --prep-excitation take. The calibration noise model starts every qubit in |0>, so it prices A at the readout error alone; the residual excitation is the device property this run measures, and only the device answers it.

One two-sided precision contract per qubit, 69 in all, split the family-wise alpha evenly and admit the design: half-width 0.025 on A, Hoeffding radii valid under arbitrary dependence between the qubits of one shot. They price resolution, not an effect. The comparison of A between two repetition delays spans two jobs, so it is outside these contracts; the written addendum states that comparison and its decision rule.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| spc_prep0_q58 | `[1.0, 0.0]` |
| spc_prep0_q71 | `[1.0, 0.0]` |
| spc_prep0_q72 | `[1.0, 0.0]` |
| spc_prep0_q33 | `[1.0, 0.0]` |
| spc_prep0_q39 | `[1.0, 0.0]` |
| spc_prep0_q53 | `[1.0, 0.0]` |
| spc_prep0_q3 | `[1.0, 0.0]` |
| spc_prep0_q16 | `[1.0, 0.0]` |
| spc_prep0_q23 | `[1.0, 0.0]` |
| spc_prep0_q17 | `[1.0, 0.0]` |
| spc_prep0_q27 | `[1.0, 0.0]` |
| spc_prep0_q28 | `[1.0, 0.0]` |
| spc_prep0_q141 | `[1.0, 0.0]` |
| spc_prep0_q142 | `[1.0, 0.0]` |
| spc_prep0_q143 | `[1.0, 0.0]` |
| spc_prep0_q15 | `[1.0, 0.0]` |
| spc_prep0_q19 | `[1.0, 0.0]` |
| spc_prep0_q35 | `[1.0, 0.0]` |
| spc_prep0_q60 | `[1.0, 0.0]` |
| spc_prep0_q61 | `[1.0, 0.0]` |
| spc_prep0_q62 | `[1.0, 0.0]` |
| spc_prep0_q151 | `[1.0, 0.0]` |
| spc_prep0_q152 | `[1.0, 0.0]` |
| spc_prep0_q153 | `[1.0, 0.0]` |
| spc_prep0_q82 | `[1.0, 0.0]` |
| spc_prep0_q83 | `[1.0, 0.0]` |
| spc_prep0_q96 | `[1.0, 0.0]` |
| spc_prep0_q38 | `[1.0, 0.0]` |
| spc_prep0_q49 | `[1.0, 0.0]` |
| spc_prep0_q50 | `[1.0, 0.0]` |
| spc_prep0_q105 | `[1.0, 0.0]` |
| spc_prep0_q106 | `[1.0, 0.0]` |
| spc_prep0_q107 | `[1.0, 0.0]` |
| spc_prep0_q118 | `[1.0, 0.0]` |
| spc_prep0_q129 | `[1.0, 0.0]` |
| spc_prep0_q128 | `[1.0, 0.0]` |
| spc_prep0_q100 | `[1.0, 0.0]` |
| spc_prep0_q101 | `[1.0, 0.0]` |
| spc_prep0_q102 | `[1.0, 0.0]` |
| spc_prep0_q55 | `[1.0, 0.0]` |
| spc_prep0_q59 | `[1.0, 0.0]` |
| spc_prep0_q75 | `[1.0, 0.0]` |
| spc_prep0_q78 | `[1.0, 0.0]` |
| spc_prep0_q89 | `[1.0, 0.0]` |
| spc_prep0_q90 | `[1.0, 0.0]` |
| spc_prep0_q66 | `[1.0, 0.0]` |
| spc_prep0_q67 | `[1.0, 0.0]` |
| spc_prep0_q68 | `[1.0, 0.0]` |
| spc_prep0_q42 | `[1.0, 0.0]` |
| spc_prep0_q43 | `[1.0, 0.0]` |
| spc_prep0_q44 | `[1.0, 0.0]` |
| spc_prep0_q10 | `[1.0, 0.0]` |
| spc_prep0_q11 | `[1.0, 0.0]` |
| spc_prep0_q12 | `[1.0, 0.0]` |
| spc_prep0_q79 | `[1.0, 0.0]` |
| spc_prep0_q93 | `[1.0, 0.0]` |
| spc_prep0_q92 | `[1.0, 0.0]` |
| spc_prep0_q132 | `[1.0, 0.0]` |
| spc_prep0_q133 | `[1.0, 0.0]` |
| spc_prep0_q134 | `[1.0, 0.0]` |
| spc_prep0_q124 | `[1.0, 0.0]` |
| spc_prep0_q125 | `[1.0, 0.0]` |
| spc_prep0_q126 | `[1.0, 0.0]` |
| spc_prep0_q98 | `[1.0, 0.0]` |
| spc_prep0_q111 | `[1.0, 0.0]` |
| spc_prep0_q110 | `[1.0, 0.0]` |
| spc_prep0_q147 | `[1.0, 0.0]` |
| spc_prep0_q148 | `[1.0, 0.0]` |
| spc_prep0_q149 | `[1.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| state_prep_q58 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[58]` | `[[58]]` |
| state_prep_q71 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[71]` | `[[71]]` |
| state_prep_q72 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[72]` | `[[72]]` |
| state_prep_q33 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[33]` | `[[33]]` |
| state_prep_q39 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[39]` | `[[39]]` |
| state_prep_q53 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[53]` | `[[53]]` |
| state_prep_q3 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[3]` | `[[3]]` |
| state_prep_q16 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[16]` | `[[16]]` |
| state_prep_q23 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[23]` | `[[23]]` |
| state_prep_q17 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[17]` | `[[17]]` |
| state_prep_q27 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[27]` | `[[27]]` |
| state_prep_q28 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[28]` | `[[28]]` |
| state_prep_q141 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[141]` | `[[141]]` |
| state_prep_q142 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[142]` | `[[142]]` |
| state_prep_q143 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[143]` | `[[143]]` |
| state_prep_q15 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[15]` | `[[15]]` |
| state_prep_q19 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[19]` | `[[19]]` |
| state_prep_q35 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[35]` | `[[35]]` |
| state_prep_q60 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[60]` | `[[60]]` |
| state_prep_q61 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[61]` | `[[61]]` |
| state_prep_q62 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[62]` | `[[62]]` |
| state_prep_q151 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[151]` | `[[151]]` |
| state_prep_q152 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[152]` | `[[152]]` |
| state_prep_q153 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[153]` | `[[153]]` |
| state_prep_q82 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[82]` | `[[82]]` |
| state_prep_q83 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[83]` | `[[83]]` |
| state_prep_q96 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[96]` | `[[96]]` |
| state_prep_q38 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[38]` | `[[38]]` |
| state_prep_q49 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[49]` | `[[49]]` |
| state_prep_q50 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[50]` | `[[50]]` |
| state_prep_q105 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[105]` | `[[105]]` |
| state_prep_q106 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[106]` | `[[106]]` |
| state_prep_q107 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[107]` | `[[107]]` |
| state_prep_q118 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[118]` | `[[118]]` |
| state_prep_q129 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[129]` | `[[129]]` |
| state_prep_q128 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[128]` | `[[128]]` |
| state_prep_q100 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[100]` | `[[100]]` |
| state_prep_q101 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[101]` | `[[101]]` |
| state_prep_q102 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[102]` | `[[102]]` |
| state_prep_q55 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[55]` | `[[55]]` |
| state_prep_q59 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[59]` | `[[59]]` |
| state_prep_q75 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[75]` | `[[75]]` |
| state_prep_q78 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[78]` | `[[78]]` |
| state_prep_q89 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[89]` | `[[89]]` |
| state_prep_q90 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[90]` | `[[90]]` |
| state_prep_q66 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[66]` | `[[66]]` |
| state_prep_q67 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[67]` | `[[67]]` |
| state_prep_q68 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[68]` | `[[68]]` |
| state_prep_q42 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[42]` | `[[42]]` |
| state_prep_q43 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[43]` | `[[43]]` |
| state_prep_q44 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[44]` | `[[44]]` |
| state_prep_q10 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[10]` | `[[10]]` |
| state_prep_q11 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[11]` | `[[11]]` |
| state_prep_q12 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[12]` | `[[12]]` |
| state_prep_q79 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[79]` | `[[79]]` |
| state_prep_q93 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[93]` | `[[93]]` |
| state_prep_q92 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[92]` | `[[92]]` |
| state_prep_q132 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[132]` | `[[132]]` |
| state_prep_q133 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[133]` | `[[133]]` |
| state_prep_q134 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[134]` | `[[134]]` |
| state_prep_q124 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[124]` | `[[124]]` |
| state_prep_q125 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[125]` | `[[125]]` |
| state_prep_q126 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[126]` | `[[126]]` |
| state_prep_q98 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[98]` | `[[98]]` |
| state_prep_q111 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[111]` | `[[111]]` |
| state_prep_q110 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[110]` | `[[110]]` |
| state_prep_q147 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[147]` | `[[147]]` |
| state_prep_q148 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[148]` | `[[148]]` |
| state_prep_q149 | ibm_kingston | 2026-10-26T11:06:06-07:00 | 20261010 | `[149]` | `[[149]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    58,
    71,
    72,
    33,
    39,
    53,
    3,
    16,
    23,
    17,
    27,
    28,
    141,
    142,
    143,
    15,
    19,
    35,
    60,
    61,
    62,
    151,
    152,
    153,
    82,
    83,
    96,
    38,
    49,
    50,
    105,
    106,
    107,
    118,
    129,
    128,
    100,
    101,
    102,
    55,
    59,
    75,
    78,
    89,
    90,
    66,
    67,
    68,
    42,
    43,
    44,
    10,
    11,
    12,
    79,
    93,
    92,
    132,
    133,
    134,
    124,
    125,
    126,
    98,
    111,
    110,
    147,
    148,
    149
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "state_prep_q58": [
      {
        "58": 58
      }
    ],
    "state_prep_q71": [
      {
        "71": 71
      }
    ],
    "state_prep_q72": [
      {
        "72": 72
      }
    ],
    "state_prep_q33": [
      {
        "33": 33
      }
    ],
    "state_prep_q39": [
      {
        "39": 39
      }
    ],
    "state_prep_q53": [
      {
        "53": 53
      }
    ],
    "state_prep_q3": [
      {
        "3": 3
      }
    ],
    "state_prep_q16": [
      {
        "16": 16
      }
    ],
    "state_prep_q23": [
      {
        "23": 23
      }
    ],
    "state_prep_q17": [
      {
        "17": 17
      }
    ],
    "state_prep_q27": [
      {
        "27": 27
      }
    ],
    "state_prep_q28": [
      {
        "28": 28
      }
    ],
    "state_prep_q141": [
      {
        "141": 141
      }
    ],
    "state_prep_q142": [
      {
        "142": 142
      }
    ],
    "state_prep_q143": [
      {
        "143": 143
      }
    ],
    "state_prep_q15": [
      {
        "15": 15
      }
    ],
    "state_prep_q19": [
      {
        "19": 19
      }
    ],
    "state_prep_q35": [
      {
        "35": 35
      }
    ],
    "state_prep_q60": [
      {
        "60": 60
      }
    ],
    "state_prep_q61": [
      {
        "61": 61
      }
    ],
    "state_prep_q62": [
      {
        "62": 62
      }
    ],
    "state_prep_q151": [
      {
        "151": 151
      }
    ],
    "state_prep_q152": [
      {
        "152": 152
      }
    ],
    "state_prep_q153": [
      {
        "153": 153
      }
    ],
    "state_prep_q82": [
      {
        "82": 82
      }
    ],
    "state_prep_q83": [
      {
        "83": 83
      }
    ],
    "state_prep_q96": [
      {
        "96": 96
      }
    ],
    "state_prep_q38": [
      {
        "38": 38
      }
    ],
    "state_prep_q49": [
      {
        "49": 49
      }
    ],
    "state_prep_q50": [
      {
        "50": 50
      }
    ],
    "state_prep_q105": [
      {
        "105": 105
      }
    ],
    "state_prep_q106": [
      {
        "106": 106
      }
    ],
    "state_prep_q107": [
      {
        "107": 107
      }
    ],
    "state_prep_q118": [
      {
        "118": 118
      }
    ],
    "state_prep_q129": [
      {
        "129": 129
      }
    ],
    "state_prep_q128": [
      {
        "128": 128
      }
    ],
    "state_prep_q100": [
      {
        "100": 100
      }
    ],
    "state_prep_q101": [
      {
        "101": 101
      }
    ],
    "state_prep_q102": [
      {
        "102": 102
      }
    ],
    "state_prep_q55": [
      {
        "55": 55
      }
    ],
    "state_prep_q59": [
      {
        "59": 59
      }
    ],
    "state_prep_q75": [
      {
        "75": 75
      }
    ],
    "state_prep_q78": [
      {
        "78": 78
      }
    ],
    "state_prep_q89": [
      {
        "89": 89
      }
    ],
    "state_prep_q90": [
      {
        "90": 90
      }
    ],
    "state_prep_q66": [
      {
        "66": 66
      }
    ],
    "state_prep_q67": [
      {
        "67": 67
      }
    ],
    "state_prep_q68": [
      {
        "68": 68
      }
    ],
    "state_prep_q42": [
      {
        "42": 42
      }
    ],
    "state_prep_q43": [
      {
        "43": 43
      }
    ],
    "state_prep_q44": [
      {
        "44": 44
      }
    ],
    "state_prep_q10": [
      {
        "10": 10
      }
    ],
    "state_prep_q11": [
      {
        "11": 11
      }
    ],
    "state_prep_q12": [
      {
        "12": 12
      }
    ],
    "state_prep_q79": [
      {
        "79": 79
      }
    ],
    "state_prep_q93": [
      {
        "93": 93
      }
    ],
    "state_prep_q92": [
      {
        "92": 92
      }
    ],
    "state_prep_q132": [
      {
        "132": 132
      }
    ],
    "state_prep_q133": [
      {
        "133": 133
      }
    ],
    "state_prep_q134": [
      {
        "134": 134
      }
    ],
    "state_prep_q124": [
      {
        "124": 124
      }
    ],
    "state_prep_q125": [
      {
        "125": 125
      }
    ],
    "state_prep_q126": [
      {
        "126": 126
      }
    ],
    "state_prep_q98": [
      {
        "98": 98
      }
    ],
    "state_prep_q111": [
      {
        "111": 111
      }
    ],
    "state_prep_q110": [
      {
        "110": 110
      }
    ],
    "state_prep_q147": [
      {
        "147": 147
      }
    ],
    "state_prep_q148": [
      {
        "148": 148
      }
    ],
    "state_prep_q149": [
      {
        "149": 149
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### spc_excited_q58

Score terms (each member averages its recorded replicas):

- `spc_prep0_q58`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0135192871094; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00145888723606.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q71

Score terms (each member averages its recorded replicas):

- `spc_prep0_q71`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0107176264358.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q72

Score terms (each member averages its recorded replicas):

- `spc_prep0_q72`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0415954589844; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0295350591111.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q33

Score terms (each member averages its recorded replicas):

- `spc_prep0_q33`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00910019479519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q39

Score terms (each member averages its recorded replicas):

- `spc_prep0_q39`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0130004882812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00094008840794.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q53

Score terms (each member averages its recorded replicas):

- `spc_prep0_q53`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0079345703125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00412582956081.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q3

Score terms (each member averages its recorded replicas):

- `spc_prep0_q3`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00173950195312; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0103208979202.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q16

Score terms (each member averages its recorded replicas):

- `spc_prep0_q16`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0130004882812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00094008840794.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q23

Score terms (each member averages its recorded replicas):

- `spc_prep0_q23`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0110533197952.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q17

Score terms (each member averages its recorded replicas):

- `spc_prep0_q17`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00958847604519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q27

Score terms (each member averages its recorded replicas):

- `spc_prep0_q27`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0079345703125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00412582956081.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q28

Score terms (each member averages its recorded replicas):

- `spc_prep0_q28`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00399780273438; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00806259713894.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q141

Score terms (each member averages its recorded replicas):

- `spc_prep0_q141`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0118162592483.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q142

Score terms (each member averages its recorded replicas):

- `spc_prep0_q142`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.01806640625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00600600637669.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q143

Score terms (each member averages its recorded replicas):

- `spc_prep0_q143`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00778198242188; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00427841745144.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q15

Score terms (each member averages its recorded replicas):

- `spc_prep0_q15`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00491333007812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00714706979519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q19

Score terms (each member averages its recorded replicas):

- `spc_prep0_q19`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00735473632812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00470566354519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q35

Score terms (each member averages its recorded replicas):

- `spc_prep0_q35`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0130615234375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00100112356419.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q60

Score terms (each member averages its recorded replicas):

- `spc_prep0_q60`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0093994140625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00266098581081.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q61

Score terms (each member averages its recorded replicas):

- `spc_prep0_q61`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0101072748733.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q62

Score terms (each member averages its recorded replicas):

- `spc_prep0_q62`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0108702143264.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q151

Score terms (each member averages its recorded replicas):

- `spc_prep0_q151`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00910019479519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q152

Score terms (each member averages its recorded replicas):

- `spc_prep0_q152`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0108702143264.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q153

Score terms (each member averages its recorded replicas):

- `spc_prep0_q153`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0674743652344; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0554139653611.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q82

Score terms (each member averages its recorded replicas):

- `spc_prep0_q82`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00910019479519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q83

Score terms (each member averages its recorded replicas):

- `spc_prep0_q83`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0711975097656; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0591371098923.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q96

Score terms (each member averages its recorded replicas):

- `spc_prep0_q96`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0206298828125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00856948293919.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q38

Score terms (each member averages its recorded replicas):

- `spc_prep0_q38`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00274658203125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00931381784206.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q49

Score terms (each member averages its recorded replicas):

- `spc_prep0_q49`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00445556640625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00760483346706.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q50

Score terms (each member averages its recorded replicas):

- `spc_prep0_q50`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0108702143264.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q105

Score terms (each member averages its recorded replicas):

- `spc_prep0_q105`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0107176264358.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q106

Score terms (each member averages its recorded replicas):

- `spc_prep0_q106`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00910019479519.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q107

Score terms (each member averages its recorded replicas):

- `spc_prep0_q107`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.013916015625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00185561575169.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q118

Score terms (each member averages its recorded replicas):

- `spc_prep0_q118`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0107176264358.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q129

Score terms (each member averages its recorded replicas):

- `spc_prep0_q129`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00528549752956.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q128

Score terms (each member averages its recorded replicas):

- `spc_prep0_q128`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00625610351562; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00580429635769.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q100

Score terms (each member averages its recorded replicas):

- `spc_prep0_q100`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.007568359375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00449204049831.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q101

Score terms (each member averages its recorded replicas):

- `spc_prep0_q101`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0265502929688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0144898930954.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q102

Score terms (each member averages its recorded replicas):

- `spc_prep0_q102`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0207824707031; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00872207082981.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q55

Score terms (each member averages its recorded replicas):

- `spc_prep0_q55`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0110533197952.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q59

Score terms (each member averages its recorded replicas):

- `spc_prep0_q59`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00274658203125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00931381784206.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q75

Score terms (each member averages its recorded replicas):

- `spc_prep0_q75`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0163269042969; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00426650442356.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q78

Score terms (each member averages its recorded replicas):

- `spc_prep0_q78`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0187377929688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00667739309544.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q89

Score terms (each member averages its recorded replicas):

- `spc_prep0_q89`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0107176264358.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q90

Score terms (each member averages its recorded replicas):

- `spc_prep0_q90`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0119018554688; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00015854440456.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q66

Score terms (each member averages its recorded replicas):

- `spc_prep0_q66`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00641464792019.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q67

Score terms (each member averages its recorded replicas):

- `spc_prep0_q67`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0096435546875; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00241684518581.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q68

Score terms (each member averages its recorded replicas):

- `spc_prep0_q68`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0101928710938; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00186752877956.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q42

Score terms (each member averages its recorded replicas):

- `spc_prep0_q42`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0110533197952.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q43

Score terms (each member averages its recorded replicas):

- `spc_prep0_q43`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0400695800781; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0280091802048.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q44

Score terms (each member averages its recorded replicas):

- `spc_prep0_q44`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00479125976562; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00726914010769.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q10

Score terms (each member averages its recorded replicas):

- `spc_prep0_q10`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0118162592483.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q11

Score terms (each member averages its recorded replicas):

- `spc_prep0_q11`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00781845651394.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q12

Score terms (each member averages its recorded replicas):

- `spc_prep0_q12`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.03173828125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0196778813767.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q79

Score terms (each member averages its recorded replicas):

- `spc_prep0_q79`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00479125976562; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00726914010769.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q93

Score terms (each member averages its recorded replicas):

- `spc_prep0_q93`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00528549752956.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q92

Score terms (each member averages its recorded replicas):

- `spc_prep0_q92`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0954895019531; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0834291020798.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q132

Score terms (each member averages its recorded replicas):

- `spc_prep0_q132`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.007568359375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00449204049831.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q133

Score terms (each member averages its recorded replicas):

- `spc_prep0_q133`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0035400390625; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00852036081081.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q134

Score terms (each member averages its recorded replicas):

- `spc_prep0_q134`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0110533197952.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q124

Score terms (each member averages its recorded replicas):

- `spc_prep0_q124`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0111999511719; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.000860448701435.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q125

Score terms (each member averages its recorded replicas):

- `spc_prep0_q125`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0382385253906; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.0261781255173.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q126

Score terms (each member averages its recorded replicas):

- `spc_prep0_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00372314453125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00833725534206.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q98

Score terms (each member averages its recorded replicas):

- `spc_prep0_q98`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00726318359375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00479721627956.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q111

Score terms (each member averages its recorded replicas):

- `spc_prep0_q111`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0166320800781; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is 0.00457168020481.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q110

Score terms (each member averages its recorded replicas):

- `spc_prep0_q110`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00323486328125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00882553659206.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q147

Score terms (each member averages its recorded replicas):

- `spc_prep0_q147`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000762939453125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0112974604202.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q148

Score terms (each member averages its recorded replicas):

- `spc_prep0_q148`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00274658203125; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.00931381784206.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

### spc_excited_q149

Score terms (each member averages its recorded replicas):

- `spc_prep0_q149`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0120603998733. The lower modeled value is -0.0107176264358.

At alpha 0.000724637681159, the two-sided confidence half-width is 0.0109952340352; requested precision is 0.025.

The search-wide simulation error probability is 0.01 across 69 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.439809361409. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 1 | 32768 | 3.02679424 | 8 |

The cost model predicts 3.02679424 seconds. The per-job service ceilings sum to 8 seconds against an invocation cap of 8 seconds. The global reserve is 0 seconds; the saved quota reports 412 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 32768 | 2.18e-06 | 2e-05 | 0 | 0 |

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
  --layout 58,71,72,33,39,53,3,16,23,17,27,28,141,142,143,15,19,35,60,61,62,151,152,153,82,83,96,38,49,50,105,106,107,118,129,128,100,101,102,55,59,75,78,89,90,66,67,68,42,43,44,10,11,12,79,93,92,132,133,134,124,125,126,98,111,110,147,148,149 \
  --state-prep-arms prep0 \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 400 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --rep-delay 2e-05 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 8.0 \
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
  --layout 58,71,72,33,39,53,3,16,23,17,27,28,141,142,143,15,19,35,60,61,62,151,152,153,82,83,96,38,49,50,105,106,107,118,129,128,100,101,102,55,59,75,78,89,90,66,67,68,42,43,44,10,11,12,79,93,92,132,133,134,124,125,126,98,111,110,147,148,149 \
  --state-prep-arms prep0 \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 400 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --rep-delay 2e-05 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 8.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-26T190257.591387Z \
  --approved-record-sha256 eb5e9b4666e733a794da15266cbeff4ca61c5b1a49e4d1a75595b344d44ac55a \
  --submit
```
