# Unapproved QPU case: state-prep-control

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-32768` at 32768 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-18T214125.791313Z`.
- [record.json](record.json) SHA-256: `63de2d2f2d305b3279a687523d693c3a69783604cebe57841086032139930d84`.
- [isa.qpy](isa.qpy) SHA-256: `b5bf2a7aa5ce5549ca71ee599f45a33733b65dc08953dd340e676000c3413e2f`.
- Experiment source digest: `54892301dc389a1b3d3cca399d3e815a82ceb1929465af769418b67d6b25f883`.
- Source commit: `5ea77f5b2b1468c87bd5509faa36d66e0f194c02`; sources_modified=`false`.
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

The state-prep-control family measures, on 148 qubits of ibm_kingston (the declared layout: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 77, 78, 79, 80, 81, 82, 83, 84, 85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 116, 117, 118, 119, 120, 122, 123, 124, 125, 126, 127, 128, 129, 130, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 147, 148, 149, 150, 151, 152, 153, 154, 155), the excited fraction each qubit carries after the Sampler's implicit initialization at a requested repetition delay of 20 us (`--rep-delay 2e-05`). One PUB measures every qubit in each shot: H initializes, measures and then applies an X, so every shot starts from the implicit initialization of a qubit the previous shot left in |1>. H, which the X after the measurement makes dynamic, is the only arm of its job, since the shots of a job's circuits interleave, and runs with twirling and dynamical decoupling off. The run selects the arms x_history (`--state-prep-arms x_history`).

Under the readout channel e10 = prob_meas1_prep0, e01 = prob_meas0_prep1, H reads (1 - eps) e10 + eps (1 - e01), so the initial excitation is eps = (H - e10) / (1 - e01 - e10) (diagnostic_experiments.state_prep_excitation), the value dynamic_density's prep_excitation and live_run's --prep-excitation take. Every shot of H after the first follows a shot that ended in |1> unless that shot's own initialization left |1> or its X failed; scripts/state_prep_excess.py bounds the excitation after an all-|1> history from H through that end-state population. The calibration noise model starts every qubit in |0>, so it prices H at the readout error alone; the residual excitation is the device property this run measures, and only the device answers it.

One two-sided precision contract per qubit, 148 in all, split the family-wise alpha evenly and admit the design: half-width 0.025 on H, Hoeffding radii valid under arbitrary dependence between the qubits of one shot. They price resolution, not an effect. The comparison of H between two repetition delays, and with A, spans separate jobs, so it is outside these contracts; scripts/state_prep_excess.py states that comparison and its preregistered rule.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| spc_x_history_q0 | `[1.0, 0.0]` |
| spc_x_history_q1 | `[1.0, 0.0]` |
| spc_x_history_q2 | `[1.0, 0.0]` |
| spc_x_history_q3 | `[1.0, 0.0]` |
| spc_x_history_q4 | `[1.0, 0.0]` |
| spc_x_history_q5 | `[1.0, 0.0]` |
| spc_x_history_q6 | `[1.0, 0.0]` |
| spc_x_history_q7 | `[1.0, 0.0]` |
| spc_x_history_q8 | `[1.0, 0.0]` |
| spc_x_history_q9 | `[1.0, 0.0]` |
| spc_x_history_q10 | `[1.0, 0.0]` |
| spc_x_history_q11 | `[1.0, 0.0]` |
| spc_x_history_q12 | `[1.0, 0.0]` |
| spc_x_history_q13 | `[1.0, 0.0]` |
| spc_x_history_q14 | `[1.0, 0.0]` |
| spc_x_history_q15 | `[1.0, 0.0]` |
| spc_x_history_q16 | `[1.0, 0.0]` |
| spc_x_history_q17 | `[1.0, 0.0]` |
| spc_x_history_q18 | `[1.0, 0.0]` |
| spc_x_history_q19 | `[1.0, 0.0]` |
| spc_x_history_q21 | `[1.0, 0.0]` |
| spc_x_history_q22 | `[1.0, 0.0]` |
| spc_x_history_q23 | `[1.0, 0.0]` |
| spc_x_history_q24 | `[1.0, 0.0]` |
| spc_x_history_q25 | `[1.0, 0.0]` |
| spc_x_history_q26 | `[1.0, 0.0]` |
| spc_x_history_q27 | `[1.0, 0.0]` |
| spc_x_history_q28 | `[1.0, 0.0]` |
| spc_x_history_q29 | `[1.0, 0.0]` |
| spc_x_history_q30 | `[1.0, 0.0]` |
| spc_x_history_q31 | `[1.0, 0.0]` |
| spc_x_history_q32 | `[1.0, 0.0]` |
| spc_x_history_q33 | `[1.0, 0.0]` |
| spc_x_history_q34 | `[1.0, 0.0]` |
| spc_x_history_q35 | `[1.0, 0.0]` |
| spc_x_history_q36 | `[1.0, 0.0]` |
| spc_x_history_q37 | `[1.0, 0.0]` |
| spc_x_history_q38 | `[1.0, 0.0]` |
| spc_x_history_q39 | `[1.0, 0.0]` |
| spc_x_history_q40 | `[1.0, 0.0]` |
| spc_x_history_q41 | `[1.0, 0.0]` |
| spc_x_history_q42 | `[1.0, 0.0]` |
| spc_x_history_q43 | `[1.0, 0.0]` |
| spc_x_history_q44 | `[1.0, 0.0]` |
| spc_x_history_q45 | `[1.0, 0.0]` |
| spc_x_history_q46 | `[1.0, 0.0]` |
| spc_x_history_q47 | `[1.0, 0.0]` |
| spc_x_history_q48 | `[1.0, 0.0]` |
| spc_x_history_q49 | `[1.0, 0.0]` |
| spc_x_history_q50 | `[1.0, 0.0]` |
| spc_x_history_q51 | `[1.0, 0.0]` |
| spc_x_history_q52 | `[1.0, 0.0]` |
| spc_x_history_q53 | `[1.0, 0.0]` |
| spc_x_history_q54 | `[1.0, 0.0]` |
| spc_x_history_q55 | `[1.0, 0.0]` |
| spc_x_history_q56 | `[1.0, 0.0]` |
| spc_x_history_q57 | `[1.0, 0.0]` |
| spc_x_history_q58 | `[1.0, 0.0]` |
| spc_x_history_q59 | `[1.0, 0.0]` |
| spc_x_history_q60 | `[1.0, 0.0]` |
| spc_x_history_q61 | `[1.0, 0.0]` |
| spc_x_history_q62 | `[1.0, 0.0]` |
| spc_x_history_q63 | `[1.0, 0.0]` |
| spc_x_history_q64 | `[1.0, 0.0]` |
| spc_x_history_q65 | `[1.0, 0.0]` |
| spc_x_history_q66 | `[1.0, 0.0]` |
| spc_x_history_q67 | `[1.0, 0.0]` |
| spc_x_history_q68 | `[1.0, 0.0]` |
| spc_x_history_q69 | `[1.0, 0.0]` |
| spc_x_history_q70 | `[1.0, 0.0]` |
| spc_x_history_q71 | `[1.0, 0.0]` |
| spc_x_history_q72 | `[1.0, 0.0]` |
| spc_x_history_q73 | `[1.0, 0.0]` |
| spc_x_history_q74 | `[1.0, 0.0]` |
| spc_x_history_q75 | `[1.0, 0.0]` |
| spc_x_history_q77 | `[1.0, 0.0]` |
| spc_x_history_q78 | `[1.0, 0.0]` |
| spc_x_history_q79 | `[1.0, 0.0]` |
| spc_x_history_q80 | `[1.0, 0.0]` |
| spc_x_history_q81 | `[1.0, 0.0]` |
| spc_x_history_q82 | `[1.0, 0.0]` |
| spc_x_history_q83 | `[1.0, 0.0]` |
| spc_x_history_q84 | `[1.0, 0.0]` |
| spc_x_history_q85 | `[1.0, 0.0]` |
| spc_x_history_q87 | `[1.0, 0.0]` |
| spc_x_history_q88 | `[1.0, 0.0]` |
| spc_x_history_q89 | `[1.0, 0.0]` |
| spc_x_history_q90 | `[1.0, 0.0]` |
| spc_x_history_q91 | `[1.0, 0.0]` |
| spc_x_history_q92 | `[1.0, 0.0]` |
| spc_x_history_q93 | `[1.0, 0.0]` |
| spc_x_history_q94 | `[1.0, 0.0]` |
| spc_x_history_q95 | `[1.0, 0.0]` |
| spc_x_history_q96 | `[1.0, 0.0]` |
| spc_x_history_q97 | `[1.0, 0.0]` |
| spc_x_history_q98 | `[1.0, 0.0]` |
| spc_x_history_q99 | `[1.0, 0.0]` |
| spc_x_history_q100 | `[1.0, 0.0]` |
| spc_x_history_q101 | `[1.0, 0.0]` |
| spc_x_history_q102 | `[1.0, 0.0]` |
| spc_x_history_q103 | `[1.0, 0.0]` |
| spc_x_history_q104 | `[1.0, 0.0]` |
| spc_x_history_q105 | `[1.0, 0.0]` |
| spc_x_history_q106 | `[1.0, 0.0]` |
| spc_x_history_q107 | `[1.0, 0.0]` |
| spc_x_history_q108 | `[1.0, 0.0]` |
| spc_x_history_q109 | `[1.0, 0.0]` |
| spc_x_history_q110 | `[1.0, 0.0]` |
| spc_x_history_q111 | `[1.0, 0.0]` |
| spc_x_history_q112 | `[1.0, 0.0]` |
| spc_x_history_q114 | `[1.0, 0.0]` |
| spc_x_history_q116 | `[1.0, 0.0]` |
| spc_x_history_q117 | `[1.0, 0.0]` |
| spc_x_history_q118 | `[1.0, 0.0]` |
| spc_x_history_q119 | `[1.0, 0.0]` |
| spc_x_history_q120 | `[1.0, 0.0]` |
| spc_x_history_q122 | `[1.0, 0.0]` |
| spc_x_history_q123 | `[1.0, 0.0]` |
| spc_x_history_q124 | `[1.0, 0.0]` |
| spc_x_history_q125 | `[1.0, 0.0]` |
| spc_x_history_q126 | `[1.0, 0.0]` |
| spc_x_history_q127 | `[1.0, 0.0]` |
| spc_x_history_q128 | `[1.0, 0.0]` |
| spc_x_history_q129 | `[1.0, 0.0]` |
| spc_x_history_q130 | `[1.0, 0.0]` |
| spc_x_history_q132 | `[1.0, 0.0]` |
| spc_x_history_q133 | `[1.0, 0.0]` |
| spc_x_history_q134 | `[1.0, 0.0]` |
| spc_x_history_q135 | `[1.0, 0.0]` |
| spc_x_history_q136 | `[1.0, 0.0]` |
| spc_x_history_q137 | `[1.0, 0.0]` |
| spc_x_history_q138 | `[1.0, 0.0]` |
| spc_x_history_q139 | `[1.0, 0.0]` |
| spc_x_history_q140 | `[1.0, 0.0]` |
| spc_x_history_q141 | `[1.0, 0.0]` |
| spc_x_history_q142 | `[1.0, 0.0]` |
| spc_x_history_q143 | `[1.0, 0.0]` |
| spc_x_history_q144 | `[1.0, 0.0]` |
| spc_x_history_q145 | `[1.0, 0.0]` |
| spc_x_history_q147 | `[1.0, 0.0]` |
| spc_x_history_q148 | `[1.0, 0.0]` |
| spc_x_history_q149 | `[1.0, 0.0]` |
| spc_x_history_q150 | `[1.0, 0.0]` |
| spc_x_history_q151 | `[1.0, 0.0]` |
| spc_x_history_q152 | `[1.0, 0.0]` |
| spc_x_history_q153 | `[1.0, 0.0]` |
| spc_x_history_q154 | `[1.0, 0.0]` |
| spc_x_history_q155 | `[1.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| state_prep_x_history_q0 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[0]` | `[[0]]` |
| state_prep_x_history_q1 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[1]` | `[[1]]` |
| state_prep_x_history_q2 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[2]` | `[[2]]` |
| state_prep_x_history_q3 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[3]` | `[[3]]` |
| state_prep_x_history_q4 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[4]` | `[[4]]` |
| state_prep_x_history_q5 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[5]` | `[[5]]` |
| state_prep_x_history_q6 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[6]` | `[[6]]` |
| state_prep_x_history_q7 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[7]` | `[[7]]` |
| state_prep_x_history_q8 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[8]` | `[[8]]` |
| state_prep_x_history_q9 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[9]` | `[[9]]` |
| state_prep_x_history_q10 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[10]` | `[[10]]` |
| state_prep_x_history_q11 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[11]` | `[[11]]` |
| state_prep_x_history_q12 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[12]` | `[[12]]` |
| state_prep_x_history_q13 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[13]` | `[[13]]` |
| state_prep_x_history_q14 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[14]` | `[[14]]` |
| state_prep_x_history_q15 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[15]` | `[[15]]` |
| state_prep_x_history_q16 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[16]` | `[[16]]` |
| state_prep_x_history_q17 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[17]` | `[[17]]` |
| state_prep_x_history_q18 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[18]` | `[[18]]` |
| state_prep_x_history_q19 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[19]` | `[[19]]` |
| state_prep_x_history_q21 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[21]` | `[[21]]` |
| state_prep_x_history_q22 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[22]` | `[[22]]` |
| state_prep_x_history_q23 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[23]` | `[[23]]` |
| state_prep_x_history_q24 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[24]` | `[[24]]` |
| state_prep_x_history_q25 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[25]` | `[[25]]` |
| state_prep_x_history_q26 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[26]` | `[[26]]` |
| state_prep_x_history_q27 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[27]` | `[[27]]` |
| state_prep_x_history_q28 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[28]` | `[[28]]` |
| state_prep_x_history_q29 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[29]` | `[[29]]` |
| state_prep_x_history_q30 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[30]` | `[[30]]` |
| state_prep_x_history_q31 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[31]` | `[[31]]` |
| state_prep_x_history_q32 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[32]` | `[[32]]` |
| state_prep_x_history_q33 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[33]` | `[[33]]` |
| state_prep_x_history_q34 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[34]` | `[[34]]` |
| state_prep_x_history_q35 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[35]` | `[[35]]` |
| state_prep_x_history_q36 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[36]` | `[[36]]` |
| state_prep_x_history_q37 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[37]` | `[[37]]` |
| state_prep_x_history_q38 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[38]` | `[[38]]` |
| state_prep_x_history_q39 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[39]` | `[[39]]` |
| state_prep_x_history_q40 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[40]` | `[[40]]` |
| state_prep_x_history_q41 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[41]` | `[[41]]` |
| state_prep_x_history_q42 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[42]` | `[[42]]` |
| state_prep_x_history_q43 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[43]` | `[[43]]` |
| state_prep_x_history_q44 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[44]` | `[[44]]` |
| state_prep_x_history_q45 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[45]` | `[[45]]` |
| state_prep_x_history_q46 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[46]` | `[[46]]` |
| state_prep_x_history_q47 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[47]` | `[[47]]` |
| state_prep_x_history_q48 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[48]` | `[[48]]` |
| state_prep_x_history_q49 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[49]` | `[[49]]` |
| state_prep_x_history_q50 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[50]` | `[[50]]` |
| state_prep_x_history_q51 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[51]` | `[[51]]` |
| state_prep_x_history_q52 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[52]` | `[[52]]` |
| state_prep_x_history_q53 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[53]` | `[[53]]` |
| state_prep_x_history_q54 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[54]` | `[[54]]` |
| state_prep_x_history_q55 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[55]` | `[[55]]` |
| state_prep_x_history_q56 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[56]` | `[[56]]` |
| state_prep_x_history_q57 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[57]` | `[[57]]` |
| state_prep_x_history_q58 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[58]` | `[[58]]` |
| state_prep_x_history_q59 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[59]` | `[[59]]` |
| state_prep_x_history_q60 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[60]` | `[[60]]` |
| state_prep_x_history_q61 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[61]` | `[[61]]` |
| state_prep_x_history_q62 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[62]` | `[[62]]` |
| state_prep_x_history_q63 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[63]` | `[[63]]` |
| state_prep_x_history_q64 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[64]` | `[[64]]` |
| state_prep_x_history_q65 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[65]` | `[[65]]` |
| state_prep_x_history_q66 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[66]` | `[[66]]` |
| state_prep_x_history_q67 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[67]` | `[[67]]` |
| state_prep_x_history_q68 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[68]` | `[[68]]` |
| state_prep_x_history_q69 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[69]` | `[[69]]` |
| state_prep_x_history_q70 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[70]` | `[[70]]` |
| state_prep_x_history_q71 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[71]` | `[[71]]` |
| state_prep_x_history_q72 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[72]` | `[[72]]` |
| state_prep_x_history_q73 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[73]` | `[[73]]` |
| state_prep_x_history_q74 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[74]` | `[[74]]` |
| state_prep_x_history_q75 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[75]` | `[[75]]` |
| state_prep_x_history_q77 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[77]` | `[[77]]` |
| state_prep_x_history_q78 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[78]` | `[[78]]` |
| state_prep_x_history_q79 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[79]` | `[[79]]` |
| state_prep_x_history_q80 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[80]` | `[[80]]` |
| state_prep_x_history_q81 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[81]` | `[[81]]` |
| state_prep_x_history_q82 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[82]` | `[[82]]` |
| state_prep_x_history_q83 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[83]` | `[[83]]` |
| state_prep_x_history_q84 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[84]` | `[[84]]` |
| state_prep_x_history_q85 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[85]` | `[[85]]` |
| state_prep_x_history_q87 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[87]` | `[[87]]` |
| state_prep_x_history_q88 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[88]` | `[[88]]` |
| state_prep_x_history_q89 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[89]` | `[[89]]` |
| state_prep_x_history_q90 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[90]` | `[[90]]` |
| state_prep_x_history_q91 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[91]` | `[[91]]` |
| state_prep_x_history_q92 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[92]` | `[[92]]` |
| state_prep_x_history_q93 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[93]` | `[[93]]` |
| state_prep_x_history_q94 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[94]` | `[[94]]` |
| state_prep_x_history_q95 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[95]` | `[[95]]` |
| state_prep_x_history_q96 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[96]` | `[[96]]` |
| state_prep_x_history_q97 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[97]` | `[[97]]` |
| state_prep_x_history_q98 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[98]` | `[[98]]` |
| state_prep_x_history_q99 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[99]` | `[[99]]` |
| state_prep_x_history_q100 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[100]` | `[[100]]` |
| state_prep_x_history_q101 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[101]` | `[[101]]` |
| state_prep_x_history_q102 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[102]` | `[[102]]` |
| state_prep_x_history_q103 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[103]` | `[[103]]` |
| state_prep_x_history_q104 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[104]` | `[[104]]` |
| state_prep_x_history_q105 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[105]` | `[[105]]` |
| state_prep_x_history_q106 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[106]` | `[[106]]` |
| state_prep_x_history_q107 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[107]` | `[[107]]` |
| state_prep_x_history_q108 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[108]` | `[[108]]` |
| state_prep_x_history_q109 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[109]` | `[[109]]` |
| state_prep_x_history_q110 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[110]` | `[[110]]` |
| state_prep_x_history_q111 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[111]` | `[[111]]` |
| state_prep_x_history_q112 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[112]` | `[[112]]` |
| state_prep_x_history_q114 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[114]` | `[[114]]` |
| state_prep_x_history_q116 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[116]` | `[[116]]` |
| state_prep_x_history_q117 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[117]` | `[[117]]` |
| state_prep_x_history_q118 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[118]` | `[[118]]` |
| state_prep_x_history_q119 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[119]` | `[[119]]` |
| state_prep_x_history_q120 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[120]` | `[[120]]` |
| state_prep_x_history_q122 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[122]` | `[[122]]` |
| state_prep_x_history_q123 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[123]` | `[[123]]` |
| state_prep_x_history_q124 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[124]` | `[[124]]` |
| state_prep_x_history_q125 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[125]` | `[[125]]` |
| state_prep_x_history_q126 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[126]` | `[[126]]` |
| state_prep_x_history_q127 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[127]` | `[[127]]` |
| state_prep_x_history_q128 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[128]` | `[[128]]` |
| state_prep_x_history_q129 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[129]` | `[[129]]` |
| state_prep_x_history_q130 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[130]` | `[[130]]` |
| state_prep_x_history_q132 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[132]` | `[[132]]` |
| state_prep_x_history_q133 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[133]` | `[[133]]` |
| state_prep_x_history_q134 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[134]` | `[[134]]` |
| state_prep_x_history_q135 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[135]` | `[[135]]` |
| state_prep_x_history_q136 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[136]` | `[[136]]` |
| state_prep_x_history_q137 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[137]` | `[[137]]` |
| state_prep_x_history_q138 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[138]` | `[[138]]` |
| state_prep_x_history_q139 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[139]` | `[[139]]` |
| state_prep_x_history_q140 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[140]` | `[[140]]` |
| state_prep_x_history_q141 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[141]` | `[[141]]` |
| state_prep_x_history_q142 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[142]` | `[[142]]` |
| state_prep_x_history_q143 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[143]` | `[[143]]` |
| state_prep_x_history_q144 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[144]` | `[[144]]` |
| state_prep_x_history_q145 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[145]` | `[[145]]` |
| state_prep_x_history_q147 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[147]` | `[[147]]` |
| state_prep_x_history_q148 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[148]` | `[[148]]` |
| state_prep_x_history_q149 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[149]` | `[[149]]` |
| state_prep_x_history_q150 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[150]` | `[[150]]` |
| state_prep_x_history_q151 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[151]` | `[[151]]` |
| state_prep_x_history_q152 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[152]` | `[[152]]` |
| state_prep_x_history_q153 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[153]` | `[[153]]` |
| state_prep_x_history_q154 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[154]` | `[[154]]` |
| state_prep_x_history_q155 | ibm_kingston | 2026-10-18T14:27:34-07:00 | 20261010 | `[155]` | `[[155]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    114,
    116,
    117,
    118,
    119,
    120,
    122,
    123,
    124,
    125,
    126,
    127,
    128,
    129,
    130,
    132,
    133,
    134,
    135,
    136,
    137,
    138,
    139,
    140,
    141,
    142,
    143,
    144,
    145,
    147,
    148,
    149,
    150,
    151,
    152,
    153,
    154,
    155
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "state_prep_x_history_q0": [
      {
        "0": 0
      }
    ],
    "state_prep_x_history_q1": [
      {
        "1": 1
      }
    ],
    "state_prep_x_history_q2": [
      {
        "2": 2
      }
    ],
    "state_prep_x_history_q3": [
      {
        "3": 3
      }
    ],
    "state_prep_x_history_q4": [
      {
        "4": 4
      }
    ],
    "state_prep_x_history_q5": [
      {
        "5": 5
      }
    ],
    "state_prep_x_history_q6": [
      {
        "6": 6
      }
    ],
    "state_prep_x_history_q7": [
      {
        "7": 7
      }
    ],
    "state_prep_x_history_q8": [
      {
        "8": 8
      }
    ],
    "state_prep_x_history_q9": [
      {
        "9": 9
      }
    ],
    "state_prep_x_history_q10": [
      {
        "10": 10
      }
    ],
    "state_prep_x_history_q11": [
      {
        "11": 11
      }
    ],
    "state_prep_x_history_q12": [
      {
        "12": 12
      }
    ],
    "state_prep_x_history_q13": [
      {
        "13": 13
      }
    ],
    "state_prep_x_history_q14": [
      {
        "14": 14
      }
    ],
    "state_prep_x_history_q15": [
      {
        "15": 15
      }
    ],
    "state_prep_x_history_q16": [
      {
        "16": 16
      }
    ],
    "state_prep_x_history_q17": [
      {
        "17": 17
      }
    ],
    "state_prep_x_history_q18": [
      {
        "18": 18
      }
    ],
    "state_prep_x_history_q19": [
      {
        "19": 19
      }
    ],
    "state_prep_x_history_q21": [
      {
        "21": 21
      }
    ],
    "state_prep_x_history_q22": [
      {
        "22": 22
      }
    ],
    "state_prep_x_history_q23": [
      {
        "23": 23
      }
    ],
    "state_prep_x_history_q24": [
      {
        "24": 24
      }
    ],
    "state_prep_x_history_q25": [
      {
        "25": 25
      }
    ],
    "state_prep_x_history_q26": [
      {
        "26": 26
      }
    ],
    "state_prep_x_history_q27": [
      {
        "27": 27
      }
    ],
    "state_prep_x_history_q28": [
      {
        "28": 28
      }
    ],
    "state_prep_x_history_q29": [
      {
        "29": 29
      }
    ],
    "state_prep_x_history_q30": [
      {
        "30": 30
      }
    ],
    "state_prep_x_history_q31": [
      {
        "31": 31
      }
    ],
    "state_prep_x_history_q32": [
      {
        "32": 32
      }
    ],
    "state_prep_x_history_q33": [
      {
        "33": 33
      }
    ],
    "state_prep_x_history_q34": [
      {
        "34": 34
      }
    ],
    "state_prep_x_history_q35": [
      {
        "35": 35
      }
    ],
    "state_prep_x_history_q36": [
      {
        "36": 36
      }
    ],
    "state_prep_x_history_q37": [
      {
        "37": 37
      }
    ],
    "state_prep_x_history_q38": [
      {
        "38": 38
      }
    ],
    "state_prep_x_history_q39": [
      {
        "39": 39
      }
    ],
    "state_prep_x_history_q40": [
      {
        "40": 40
      }
    ],
    "state_prep_x_history_q41": [
      {
        "41": 41
      }
    ],
    "state_prep_x_history_q42": [
      {
        "42": 42
      }
    ],
    "state_prep_x_history_q43": [
      {
        "43": 43
      }
    ],
    "state_prep_x_history_q44": [
      {
        "44": 44
      }
    ],
    "state_prep_x_history_q45": [
      {
        "45": 45
      }
    ],
    "state_prep_x_history_q46": [
      {
        "46": 46
      }
    ],
    "state_prep_x_history_q47": [
      {
        "47": 47
      }
    ],
    "state_prep_x_history_q48": [
      {
        "48": 48
      }
    ],
    "state_prep_x_history_q49": [
      {
        "49": 49
      }
    ],
    "state_prep_x_history_q50": [
      {
        "50": 50
      }
    ],
    "state_prep_x_history_q51": [
      {
        "51": 51
      }
    ],
    "state_prep_x_history_q52": [
      {
        "52": 52
      }
    ],
    "state_prep_x_history_q53": [
      {
        "53": 53
      }
    ],
    "state_prep_x_history_q54": [
      {
        "54": 54
      }
    ],
    "state_prep_x_history_q55": [
      {
        "55": 55
      }
    ],
    "state_prep_x_history_q56": [
      {
        "56": 56
      }
    ],
    "state_prep_x_history_q57": [
      {
        "57": 57
      }
    ],
    "state_prep_x_history_q58": [
      {
        "58": 58
      }
    ],
    "state_prep_x_history_q59": [
      {
        "59": 59
      }
    ],
    "state_prep_x_history_q60": [
      {
        "60": 60
      }
    ],
    "state_prep_x_history_q61": [
      {
        "61": 61
      }
    ],
    "state_prep_x_history_q62": [
      {
        "62": 62
      }
    ],
    "state_prep_x_history_q63": [
      {
        "63": 63
      }
    ],
    "state_prep_x_history_q64": [
      {
        "64": 64
      }
    ],
    "state_prep_x_history_q65": [
      {
        "65": 65
      }
    ],
    "state_prep_x_history_q66": [
      {
        "66": 66
      }
    ],
    "state_prep_x_history_q67": [
      {
        "67": 67
      }
    ],
    "state_prep_x_history_q68": [
      {
        "68": 68
      }
    ],
    "state_prep_x_history_q69": [
      {
        "69": 69
      }
    ],
    "state_prep_x_history_q70": [
      {
        "70": 70
      }
    ],
    "state_prep_x_history_q71": [
      {
        "71": 71
      }
    ],
    "state_prep_x_history_q72": [
      {
        "72": 72
      }
    ],
    "state_prep_x_history_q73": [
      {
        "73": 73
      }
    ],
    "state_prep_x_history_q74": [
      {
        "74": 74
      }
    ],
    "state_prep_x_history_q75": [
      {
        "75": 75
      }
    ],
    "state_prep_x_history_q77": [
      {
        "77": 77
      }
    ],
    "state_prep_x_history_q78": [
      {
        "78": 78
      }
    ],
    "state_prep_x_history_q79": [
      {
        "79": 79
      }
    ],
    "state_prep_x_history_q80": [
      {
        "80": 80
      }
    ],
    "state_prep_x_history_q81": [
      {
        "81": 81
      }
    ],
    "state_prep_x_history_q82": [
      {
        "82": 82
      }
    ],
    "state_prep_x_history_q83": [
      {
        "83": 83
      }
    ],
    "state_prep_x_history_q84": [
      {
        "84": 84
      }
    ],
    "state_prep_x_history_q85": [
      {
        "85": 85
      }
    ],
    "state_prep_x_history_q87": [
      {
        "87": 87
      }
    ],
    "state_prep_x_history_q88": [
      {
        "88": 88
      }
    ],
    "state_prep_x_history_q89": [
      {
        "89": 89
      }
    ],
    "state_prep_x_history_q90": [
      {
        "90": 90
      }
    ],
    "state_prep_x_history_q91": [
      {
        "91": 91
      }
    ],
    "state_prep_x_history_q92": [
      {
        "92": 92
      }
    ],
    "state_prep_x_history_q93": [
      {
        "93": 93
      }
    ],
    "state_prep_x_history_q94": [
      {
        "94": 94
      }
    ],
    "state_prep_x_history_q95": [
      {
        "95": 95
      }
    ],
    "state_prep_x_history_q96": [
      {
        "96": 96
      }
    ],
    "state_prep_x_history_q97": [
      {
        "97": 97
      }
    ],
    "state_prep_x_history_q98": [
      {
        "98": 98
      }
    ],
    "state_prep_x_history_q99": [
      {
        "99": 99
      }
    ],
    "state_prep_x_history_q100": [
      {
        "100": 100
      }
    ],
    "state_prep_x_history_q101": [
      {
        "101": 101
      }
    ],
    "state_prep_x_history_q102": [
      {
        "102": 102
      }
    ],
    "state_prep_x_history_q103": [
      {
        "103": 103
      }
    ],
    "state_prep_x_history_q104": [
      {
        "104": 104
      }
    ],
    "state_prep_x_history_q105": [
      {
        "105": 105
      }
    ],
    "state_prep_x_history_q106": [
      {
        "106": 106
      }
    ],
    "state_prep_x_history_q107": [
      {
        "107": 107
      }
    ],
    "state_prep_x_history_q108": [
      {
        "108": 108
      }
    ],
    "state_prep_x_history_q109": [
      {
        "109": 109
      }
    ],
    "state_prep_x_history_q110": [
      {
        "110": 110
      }
    ],
    "state_prep_x_history_q111": [
      {
        "111": 111
      }
    ],
    "state_prep_x_history_q112": [
      {
        "112": 112
      }
    ],
    "state_prep_x_history_q114": [
      {
        "114": 114
      }
    ],
    "state_prep_x_history_q116": [
      {
        "116": 116
      }
    ],
    "state_prep_x_history_q117": [
      {
        "117": 117
      }
    ],
    "state_prep_x_history_q118": [
      {
        "118": 118
      }
    ],
    "state_prep_x_history_q119": [
      {
        "119": 119
      }
    ],
    "state_prep_x_history_q120": [
      {
        "120": 120
      }
    ],
    "state_prep_x_history_q122": [
      {
        "122": 122
      }
    ],
    "state_prep_x_history_q123": [
      {
        "123": 123
      }
    ],
    "state_prep_x_history_q124": [
      {
        "124": 124
      }
    ],
    "state_prep_x_history_q125": [
      {
        "125": 125
      }
    ],
    "state_prep_x_history_q126": [
      {
        "126": 126
      }
    ],
    "state_prep_x_history_q127": [
      {
        "127": 127
      }
    ],
    "state_prep_x_history_q128": [
      {
        "128": 128
      }
    ],
    "state_prep_x_history_q129": [
      {
        "129": 129
      }
    ],
    "state_prep_x_history_q130": [
      {
        "130": 130
      }
    ],
    "state_prep_x_history_q132": [
      {
        "132": 132
      }
    ],
    "state_prep_x_history_q133": [
      {
        "133": 133
      }
    ],
    "state_prep_x_history_q134": [
      {
        "134": 134
      }
    ],
    "state_prep_x_history_q135": [
      {
        "135": 135
      }
    ],
    "state_prep_x_history_q136": [
      {
        "136": 136
      }
    ],
    "state_prep_x_history_q137": [
      {
        "137": 137
      }
    ],
    "state_prep_x_history_q138": [
      {
        "138": 138
      }
    ],
    "state_prep_x_history_q139": [
      {
        "139": 139
      }
    ],
    "state_prep_x_history_q140": [
      {
        "140": 140
      }
    ],
    "state_prep_x_history_q141": [
      {
        "141": 141
      }
    ],
    "state_prep_x_history_q142": [
      {
        "142": 142
      }
    ],
    "state_prep_x_history_q143": [
      {
        "143": 143
      }
    ],
    "state_prep_x_history_q144": [
      {
        "144": 144
      }
    ],
    "state_prep_x_history_q145": [
      {
        "145": 145
      }
    ],
    "state_prep_x_history_q147": [
      {
        "147": 147
      }
    ],
    "state_prep_x_history_q148": [
      {
        "148": 148
      }
    ],
    "state_prep_x_history_q149": [
      {
        "149": 149
      }
    ],
    "state_prep_x_history_q150": [
      {
        "150": 150
      }
    ],
    "state_prep_x_history_q151": [
      {
        "151": 151
      }
    ],
    "state_prep_x_history_q152": [
      {
        "152": 152
      }
    ],
    "state_prep_x_history_q153": [
      {
        "153": 153
      }
    ],
    "state_prep_x_history_q154": [
      {
        "154": 154
      }
    ],
    "state_prep_x_history_q155": [
      {
        "155": 155
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### spc_history_excited_q0

Score terms (each member averages its recorded replicas):

- `spc_x_history_q0`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00372314453125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0088107022473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q1

Score terms (each member averages its recorded replicas):

- `spc_x_history_q1`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00607299804688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00646084873168.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q2

Score terms (each member averages its recorded replicas):

- `spc_x_history_q2`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0057589444348.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q3

Score terms (each member averages its recorded replicas):

- `spc_x_history_q3`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0130004882812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000466641502697.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q4

Score terms (each member averages its recorded replicas):

- `spc_x_history_q4`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0105807217786.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q5

Score terms (each member averages its recorded replicas):

- `spc_x_history_q5`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q6

Score terms (each member averages its recorded replicas):

- `spc_x_history_q6`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00860595703125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0039278897473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q7

Score terms (each member averages its recorded replicas):

- `spc_x_history_q7`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0195007324219; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00696688564332.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q8

Score terms (each member averages its recorded replicas):

- `spc_x_history_q8`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q9

Score terms (each member averages its recorded replicas):

- `spc_x_history_q9`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q10

Score terms (each member averages its recorded replicas):

- `spc_x_history_q10`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q11

Score terms (each member averages its recorded replicas):

- `spc_x_history_q11`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q12

Score terms (each member averages its recorded replicas):

- `spc_x_history_q12`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0289001464844; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0163662997058.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q13

Score terms (each member averages its recorded replicas):

- `spc_x_history_q13`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0105807217786.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q14

Score terms (each member averages its recorded replicas):

- `spc_x_history_q14`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0124816894531; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -5.21573254278e-05.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q15

Score terms (each member averages its recorded replicas):

- `spc_x_history_q15`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00527954101562; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00725430576293.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q16

Score terms (each member averages its recorded replicas):

- `spc_x_history_q16`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0104370117188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0020968350598.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q17

Score terms (each member averages its recorded replicas):

- `spc_x_history_q17`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0113436612317.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q18

Score terms (each member averages its recorded replicas):

- `spc_x_history_q18`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00323486328125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0092989834973.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q19

Score terms (each member averages its recorded replicas):

- `spc_x_history_q19`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0057589444348.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q21

Score terms (each member averages its recorded replicas):

- `spc_x_history_q21`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00997924804688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00255459873168.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q22

Score terms (each member averages its recorded replicas):

- `spc_x_history_q22`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0115051269531; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00102871982543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q23

Score terms (each member averages its recorded replicas):

- `spc_x_history_q23`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00173950195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0107943448254.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q24

Score terms (each member averages its recorded replicas):

- `spc_x_history_q24`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0133666992188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000832852440197.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q25

Score terms (each member averages its recorded replicas):

- `spc_x_history_q25`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00323486328125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0092989834973.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q26

Score terms (each member averages its recorded replicas):

- `spc_x_history_q26`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00445556640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0080782803723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q27

Score terms (each member averages its recorded replicas):

- `spc_x_history_q27`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00860595703125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0039278897473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q28

Score terms (each member averages its recorded replicas):

- `spc_x_history_q28`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0035400390625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00899380771605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q29

Score terms (each member averages its recorded replicas):

- `spc_x_history_q29`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q30

Score terms (each member averages its recorded replicas):

- `spc_x_history_q30`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0127258300781; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000191983299572.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q31

Score terms (each member averages its recorded replicas):

- `spc_x_history_q31`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00839233398438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00414151279418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q32

Score terms (each member averages its recorded replicas):

- `spc_x_history_q32`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.02392578125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0113919344714.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q33

Score terms (each member averages its recorded replicas):

- `spc_x_history_q33`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q34

Score terms (each member averages its recorded replicas):

- `spc_x_history_q34`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0177001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00516634853395.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q35

Score terms (each member averages its recorded replicas):

- `spc_x_history_q35`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.013916015625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00138216884645.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q36

Score terms (each member averages its recorded replicas):

- `spc_x_history_q36`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00607299804688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00646084873168.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q37

Score terms (each member averages its recorded replicas):

- `spc_x_history_q37`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00323486328125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0092989834973.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q38

Score terms (each member averages its recorded replicas):

- `spc_x_history_q38`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00399780273438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00853604404418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q39

Score terms (each member averages its recorded replicas):

- `spc_x_history_q39`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00726318359375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0052706631848.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q40

Score terms (each member averages its recorded replicas):

- `spc_x_history_q40`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q41

Score terms (each member averages its recorded replicas):

- `spc_x_history_q41`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q42

Score terms (each member averages its recorded replicas):

- `spc_x_history_q42`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q43

Score terms (each member averages its recorded replicas):

- `spc_x_history_q43`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0101928710938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0023409756848.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q44

Score terms (each member averages its recorded replicas):

- `spc_x_history_q44`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.002197265625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0103365811536.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q45

Score terms (each member averages its recorded replicas):

- `spc_x_history_q45`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00445556640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0080782803723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q46

Score terms (each member averages its recorded replicas):

- `spc_x_history_q46`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00173950195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0107943448254.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q47

Score terms (each member averages its recorded replicas):

- `spc_x_history_q47`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00274658203125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0097872647473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q48

Score terms (each member averages its recorded replicas):

- `spc_x_history_q48`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q49

Score terms (each member averages its recorded replicas):

- `spc_x_history_q49`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q50

Score terms (each member averages its recorded replicas):

- `spc_x_history_q50`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00173950195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0107943448254.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q51

Score terms (each member averages its recorded replicas):

- `spc_x_history_q51`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0191650390625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00663119228395.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q52

Score terms (each member averages its recorded replicas):

- `spc_x_history_q52`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00445556640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0080782803723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q53

Score terms (each member averages its recorded replicas):

- `spc_x_history_q53`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.007568359375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00496548740355.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q54

Score terms (each member averages its recorded replicas):

- `spc_x_history_q54`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0153198242188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0027859774402.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q55

Score terms (each member averages its recorded replicas):

- `spc_x_history_q55`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00860595703125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0039278897473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q56

Score terms (each member averages its recorded replicas):

- `spc_x_history_q56`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0113436612317.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q57

Score terms (each member averages its recorded replicas):

- `spc_x_history_q57`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00735473632812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00517911045043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q58

Score terms (each member averages its recorded replicas):

- `spc_x_history_q58`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.02099609375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00846224697145.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q59

Score terms (each member averages its recorded replicas):

- `spc_x_history_q59`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q60

Score terms (each member averages its recorded replicas):

- `spc_x_history_q60`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0133666992188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000832852440197.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q61

Score terms (each member averages its recorded replicas):

- `spc_x_history_q61`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0105807217786.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q62

Score terms (each member averages its recorded replicas):

- `spc_x_history_q62`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0204772949219; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00794344814332.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q63

Score terms (each member averages its recorded replicas):

- `spc_x_history_q63`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00957364170043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q64

Score terms (each member averages its recorded replicas):

- `spc_x_history_q64`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0113436612317.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q65

Score terms (each member averages its recorded replicas):

- `spc_x_history_q65`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00491333007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00762051670043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q66

Score terms (each member averages its recorded replicas):

- `spc_x_history_q66`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q67

Score terms (each member averages its recorded replicas):

- `spc_x_history_q67`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q68

Score terms (each member averages its recorded replicas):

- `spc_x_history_q68`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0035400390625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00899380771605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q69

Score terms (each member averages its recorded replicas):

- `spc_x_history_q69`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0107116699219; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00182217685668.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q70

Score terms (each member averages its recorded replicas):

- `spc_x_history_q70`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0153198242188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0027859774402.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q71

Score terms (each member averages its recorded replicas):

- `spc_x_history_q71`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00479125976562; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00774258701293.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q72

Score terms (each member averages its recorded replicas):

- `spc_x_history_q72`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0350036621094; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0224698153308.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q73

Score terms (each member averages its recorded replicas):

- `spc_x_history_q73`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0079345703125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00459927646605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q74

Score terms (each member averages its recorded replicas):

- `spc_x_history_q74`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q75

Score terms (each member averages its recorded replicas):

- `spc_x_history_q75`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0177001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00516634853395.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q77

Score terms (each member averages its recorded replicas):

- `spc_x_history_q77`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q78

Score terms (each member averages its recorded replicas):

- `spc_x_history_q78`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0265502929688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0140164461902.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q79

Score terms (each member averages its recorded replicas):

- `spc_x_history_q79`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0035400390625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00899380771605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q80

Score terms (each member averages its recorded replicas):

- `spc_x_history_q80`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0133666992188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000832852440197.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q81

Score terms (each member averages its recorded replicas):

- `spc_x_history_q81`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q82

Score terms (each member averages its recorded replicas):

- `spc_x_history_q82`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q83

Score terms (each member averages its recorded replicas):

- `spc_x_history_q83`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.01806640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00553255947145.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q84

Score terms (each member averages its recorded replicas):

- `spc_x_history_q84`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q85

Score terms (each member averages its recorded replicas):

- `spc_x_history_q85`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q87

Score terms (each member averages its recorded replicas):

- `spc_x_history_q87`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0166320800781; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00409823329957.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q88

Score terms (each member averages its recorded replicas):

- `spc_x_history_q88`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0125338467786.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q89

Score terms (each member averages its recorded replicas):

- `spc_x_history_q89`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00808715820312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00444668857543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q90

Score terms (each member averages its recorded replicas):

- `spc_x_history_q90`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00688809482543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q91

Score terms (each member averages its recorded replicas):

- `spc_x_history_q91`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00692749023438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00560635654418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q92

Score terms (each member averages its recorded replicas):

- `spc_x_history_q92`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.021728515625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00919466884645.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q93

Score terms (each member averages its recorded replicas):

- `spc_x_history_q93`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q94

Score terms (each member averages its recorded replicas):

- `spc_x_history_q94`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00688809482543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q95

Score terms (each member averages its recorded replicas):

- `spc_x_history_q95`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q96

Score terms (each member averages its recorded replicas):

- `spc_x_history_q96`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0223083496094; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00977450283082.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q97

Score terms (each member averages its recorded replicas):

- `spc_x_history_q97`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00372314453125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0088107022473.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q98

Score terms (each member averages its recorded replicas):

- `spc_x_history_q98`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q99

Score terms (each member averages its recorded replicas):

- `spc_x_history_q99`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.02099609375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00846224697145.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q100

Score terms (each member averages its recorded replicas):

- `spc_x_history_q100`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0064697265625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00606412021605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q101

Score terms (each member averages its recorded replicas):

- `spc_x_history_q101`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00885009765625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0036837491223.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q102

Score terms (each member averages its recorded replicas):

- `spc_x_history_q102`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0124816894531; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -5.21573254278e-05.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q103

Score terms (each member averages its recorded replicas):

- `spc_x_history_q103`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00399780273438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00853604404418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q104

Score terms (each member averages its recorded replicas):

- `spc_x_history_q104`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0137634277344; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00122958095582.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q105

Score terms (each member averages its recorded replicas):

- `spc_x_history_q105`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q106

Score terms (each member averages its recorded replicas):

- `spc_x_history_q106`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00173950195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0107943448254.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q107

Score terms (each member averages its recorded replicas):

- `spc_x_history_q107`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q108

Score terms (each member averages its recorded replicas):

- `spc_x_history_q108`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00399780273438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00853604404418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q109

Score terms (each member averages its recorded replicas):

- `spc_x_history_q109`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0057589444348.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q110

Score terms (each member averages its recorded replicas):

- `spc_x_history_q110`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00491333007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00762051670043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q111

Score terms (each member averages its recorded replicas):

- `spc_x_history_q111`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0035400390625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00899380771605.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q112

Score terms (each member averages its recorded replicas):

- `spc_x_history_q112`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0248718261719; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0123379793933.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q114

Score terms (each member averages its recorded replicas):

- `spc_x_history_q114`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00808715820312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00444668857543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q116

Score terms (each member averages its recorded replicas):

- `spc_x_history_q116`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0316467285156; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0191128817371.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q117

Score terms (each member averages its recorded replicas):

- `spc_x_history_q117`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0113436612317.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q118

Score terms (each member averages its recorded replicas):

- `spc_x_history_q118`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0115267667004.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q119

Score terms (each member averages its recorded replicas):

- `spc_x_history_q119`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0152282714844; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00269442470582.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q120

Score terms (each member averages its recorded replicas):

- `spc_x_history_q120`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0177001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00516634853395.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q122

Score terms (each member averages its recorded replicas):

- `spc_x_history_q122`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00885009765625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0036837491223.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q123

Score terms (each member averages its recorded replicas):

- `spc_x_history_q123`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q124

Score terms (each member averages its recorded replicas):

- `spc_x_history_q124`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00885009765625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0036837491223.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q125

Score terms (each member averages its recorded replicas):

- `spc_x_history_q125`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00726318359375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0052706631848.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q126

Score terms (each member averages its recorded replicas):

- `spc_x_history_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00957364170043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q127

Score terms (each member averages its recorded replicas):

- `spc_x_history_q127`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0195007324219; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00696688564332.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q128

Score terms (each member averages its recorded replicas):

- `spc_x_history_q128`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0111910733411.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q129

Score terms (each member averages its recorded replicas):

- `spc_x_history_q129`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0652770996094; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0527432528308.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q130

Score terms (each member averages its recorded replicas):

- `spc_x_history_q130`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.000631991309803.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q132

Score terms (each member averages its recorded replicas):

- `spc_x_history_q132`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0057589444348.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q133

Score terms (each member averages its recorded replicas):

- `spc_x_history_q133`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0130615234375; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.000527676658947.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q134

Score terms (each member averages its recorded replicas):

- `spc_x_history_q134`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00296020507812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00957364170043.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q135

Score terms (each member averages its recorded replicas):

- `spc_x_history_q135`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0107116699219; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00182217685668.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q136

Score terms (each member averages its recorded replicas):

- `spc_x_history_q136`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0122897061536.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q137

Score terms (each member averages its recorded replicas):

- `spc_x_history_q137`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0155334472656; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00299960048707.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q138

Score terms (each member averages its recorded replicas):

- `spc_x_history_q138`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0396423339844; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0271084872058.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q139

Score terms (each member averages its recorded replicas):

- `spc_x_history_q139`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0174255371094; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00489169033082.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q140

Score terms (each member averages its recorded replicas):

- `spc_x_history_q140`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00688809482543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q141

Score terms (each member averages its recorded replicas):

- `spc_x_history_q141`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q142

Score terms (each member averages its recorded replicas):

- `spc_x_history_q142`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0153198242188; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.0027859774402.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q143

Score terms (each member averages its recorded replicas):

- `spc_x_history_q143`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00399780273438; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00853604404418.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q144

Score terms (each member averages its recorded replicas):

- `spc_x_history_q144`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0119845303723.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q145

Score terms (each member averages its recorded replicas):

- `spc_x_history_q145`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0137634277344; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00122958095582.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q147

Score terms (each member averages its recorded replicas):

- `spc_x_history_q147`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00018310546875; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0123507413098.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q148

Score terms (each member averages its recorded replicas):

- `spc_x_history_q148`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0113436612317.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q149

Score terms (each member averages its recorded replicas):

- `spc_x_history_q149`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00323486328125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0092989834973.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q150

Score terms (each member averages its recorded replicas):

- `spc_x_history_q150`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00247192382812; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0100619229504.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q151

Score terms (each member averages its recorded replicas):

- `spc_x_history_q151`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.0105807217786.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q152

Score terms (each member averages its recorded replicas):

- `spc_x_history_q152`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00564575195312; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00688809482543.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q153

Score terms (each member averages its recorded replicas):

- `spc_x_history_q153`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0213928222656; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is 0.00885897548707.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q154

Score terms (each member averages its recorded replicas):

- `spc_x_history_q154`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00424194335938; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00829190341918.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

### spc_history_excited_q155

Score terms (each member averages its recorded replicas):

- `spc_x_history_q155`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00527954101562; the simultaneous finite-simulation allowance is +/-0.0125338467786. The lower modeled value is -0.00725430576293.

At alpha 0.000337837837838, the two-sided confidence half-width is 0.0115125688468; requested precision is 0.025.

The search-wide simulation error probability is 0.01 across 148 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.460502753874. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 1 | 32768 | 3.027842816 | 8 |

The cost model predicts 3.027842816 seconds. The per-job service ceilings sum to 8 seconds against an invocation cap of 8 seconds. The global reserve is 60 seconds; the saved quota reports 204 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 32768 | 2.212e-06 | 2e-05 | 0 | 0 |

Job `ibm_kingston/dynamic/1` adds 2.3 seconds of modeled overhead.

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
  --simulation-threads 3 \
  --simulation-memory-mb 512 \
  --optimize \
  --layout 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,77,78,79,80,81,82,83,84,85,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,114,116,117,118,119,120,122,123,124,125,126,127,128,129,130,132,133,134,135,136,137,138,139,140,141,142,143,144,145,147,148,149,150,151,152,153,154,155 \
  --state-prep-arms x_history \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --rep-delay 2e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 32768 \
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
  --simulation-threads 3 \
  --simulation-memory-mb 512 \
  --optimize \
  --layout 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,77,78,79,80,81,82,83,84,85,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,114,116,117,118,119,120,122,123,124,125,126,127,128,129,130,132,133,134,135,136,137,138,139,140,141,142,143,144,145,147,148,149,150,151,152,153,154,155 \
  --state-prep-arms x_history \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 8 \
  --rep-delay 2e-05 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 32768 \
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
  --max-total-execution-seconds 8.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-18T214125.791313Z \
  --approved-record-sha256 63de2d2f2d305b3279a687523d693c3a69783604cebe57841086032139930d84 \
  --submit
```
