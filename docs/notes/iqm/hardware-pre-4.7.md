# IQM Resonance hardware before IQM OS 4.7

These are the specifications of the six IQM Resonance targets as the
snapshot of 2026-10-19T06:08Z read them (`index.json` `captured_at`), before IQM OS
4.7 reached Garnet and Sirius (2026-10-21) and inside Emerald's announced
upgrade window, while every station still reported IQM station control
49.0.3 and IQM Server 3.0.0. Every value comes from
[docs/evidence/iqm/](../../evidence/iqm/) (`hardware.json` and the raw
records beside it). Quality figures belong to the default calibration sets
of that morning and change with every calibration; structure, limits and
prices change with releases. A post-upgrade snapshot compared against this
one measures what IQM OS 4.7 changed.

Calibration sets: Emerald `b306d0dc-0374-4594-9fa1-4dc45a6c4333` (metrics
2026-10-19T05:29Z), Garnet `04b7af66-cc83-4e7d-bfaa-28236f5ef1b4`
(02:29Z), Sirius `53d7843b-5634-4091-b27c-09c2b3acf9e4` (05:44Z).

## QPUs

| | Emerald | Garnet | Sirius |
|---|---|---|---|
| Chip | Crystal 54, M216 variant H03 (`M216_F0W102525_H03_F08`) | M194 variant P08 (`M194_F0W2114_P08_B15`) | M186 variant ND1 (`M186_F0W2259_ND1_O12`) |
| Station | MX07_Aphrodite_CD3 | Apollo station in XLD10.S1 | Charon, a 24Donis in MX03.S1 |
| Topology | square lattice | square lattice | star: every qubit coupled to computational resonator COMPR1 |
| Qubits | 54 | 20 | 16 operational (24 named in the static architecture) |
| Tunable couplers | 90 | 30 | 24 |
| Operational CZ loci | 85 | 30 | 16 qubit-resonator pairs |
| Probe (readout) lines | 8 | 3 | 3 |
| Native gates (DQA) | prx, cz, measure, measure_fidelity, cc_prx, prx_12, reset_wait | the same set | the same set plus move |
| CZ implementation | `slepian_crf` on 83 loci, `crf_acstarkcrf` on QB44-QB50 and QB50-QB51 | `slepian_crf` on all 30 | `crf_crf` on 14, `tgss` on QB2-COMPR1 and QB10-COMPR1 |
| PRX implementation | `drag_crf_sx` | `drag_crf_sx` | `drag_crf` |
| measure_fidelity default | `shelved_constant` | `constant` | `constant` |
| Drive frequency | 3.802 to 4.207 GHz | 4.488 to 4.770 GHz | 4.446 to 4.725 GHz |
| Readout frequency | 5.101 to 6.053 GHz | 5.062 to 6.098 GHz | 5.078 to 6.131 GHz |
| Median T1 / T2 / T2 echo | 50 / 15 / 38 us | 42 / 9 / 22 us | 26 / 10 / 24 us |
| T1 range | 11.0 to 91.9 us | 15.3 to 57.4 us | 15.7 to 46.7 us |
| Median PRX RB fidelity | 0.99967 | 0.99934 | 0.99902 |
| Median CZ IRB fidelity | 0.99632 | 0.99425 | 0.97400 (to the resonator) |
| Median readout fidelity | 0.98848 | 0.97945 | 0.98335 |
| Median PRX / CZ / measure duration | 24 / 40 / 360 ns | 16 / 40 / 480 ns | 40 / 104 / 400 ns |
| AWG channels | 2 GS/s, 8-sample granularity | 2 GS/s, 8-sample granularity | 2 GS/s, 16-sample granularity; a 10 MS/s channel at 1 sample |
| Max shots / circuits / instructions | 20000 / 100 / 30000 | 20000 / 100 / 10000 | 20000 / 100 / 75000 |
| Price | 0.75 credits/s; 2400.00 per 1 h timeslot | 0.50 credits/s; 1800.00 | 0.30 credits/s; 1080.00 |
| IQM station control | 49.0.3 | 49.0.3 | 49.0.3 |

Weakest operational loci:

- Emerald: CZ QB43-QB35 0.908, QB38-QB37 0.957, QB50-QB51 0.963; readout
  QB10 0.898, QB6 0.910. The DQA override map names QB49-QB50 and
  QB54-QB50 for `crf_acstarkcrf`, yet no CZ implementation lists them as
  loci; QB6-QB7 carries an IRB metric and no CZ locus.
- Garnet: QB10's couplings, CZ 0.988 to 0.990.
- Sirius: CZ QB11-COMPR1 0.923. A two-qubit gate between qubits runs as
  MOVE, CZ, MOVE through COMPR1.

## Mocks

The mocks run the same API against simulated chips; they are no physical
devices.

| | emerald:mock | garnet:mock | sirius:mock |
|---|---|---|---|
| Simulated chip | M160 H01 (`M160_W0_H01_Z99`) | M194 P08 (`M194_W0_P08_Z99`) | M186 ND1 (`M186_W0_ND1_Z99`) |
| Qubits / couplings | 54 / 90 | 20 / 30 | 24 / 24, with COMPR1 |
| Gate implementations | cz `tgss`, prx `drag_gaussian` | cz `crf_crf`, prx `drag_crf` | cz and move `crf_crf`, prx `drag_crf` |
| Native gates | no prx_12 | no prx_12 | no prx_12, no cc_prx |
| Max shots / circuits / instructions | 200000 / 1000 / 10000 | 20000 / 500 / 10000 | 20000 / 200 / 20000 |
| Price per second (as reported) | 0.00 | 0.00 | 0.67 |

A mock is reached as `quantum_computer="garnet:mock"` on
https://resonance.iqm.tech; the `mock_url` each record carries points at the
retired `cocos.resonance.meetiqm.com`, which iqm-client 36 rejects.

Per-qubit rows (T1, T2, T2 echo, PRX fidelity, readout fidelity and both
assignment errors, drive and readout frequency, PRX and measure duration)
and per-pair CZ fidelity, duration and implementation are in
`docs/evidence/iqm/hardware.json`.
