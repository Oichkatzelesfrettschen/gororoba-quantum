# Unapproved case: conditional Ramsey on the coherence-window patch

Not approved. This case covers two records, this one and
`2026-10-15T204427.864020Z`. A submission needs the owner's approval against
fresh dry runs of both commands below, and the records go stale when
ibm_kingston recalibrates or its queue changes.

- **Question:** is the coherence window's -1.130 rad over 4.392 us a frame
  detuning difference between its work qubits?
  - That rotation was measured on `rho_{01,10}` of work_a (qubit 68) and
    work_b (qubit 66), with spectator 67 between them in |0>
    (`2026-10-15T030748.903241Z`).
  - It is an odd-sector coherence, so it winds at `omega_68 - omega_66`, up
    to whole turns of 227.7 kHz.
  - The work qubits are not coupled to each other; each couples to 67.
- **Design** (`docs/notes/conditional_ramsey_hamiltonian.md`): one job per
  coupled pair, each with 48 Ramsey circuits and 2 readout calibration
  circuits at 1024 shots.
  - Bell even and odd, and A given B in |0> and |1>.
  - Delays 0, 125, 500, 2000, 5000 and 10000 dt, with an unambiguous range
    of 1 MHz.

  | Record | A | B | Gives |
  | --- | --- | --- | --- |
  | this one | 68 | 67 | `omega_68`, `omega_67`, `J_68,67` |
  | `2026-10-15T204427.864020Z` | 67 | 66 | `omega_67`, `omega_66`, `J_66,67` |

- **Prediction tested:** with the spectator in |0>, the window's rate is
  `(omega_68 + J_68,67) - (omega_66 + J_66,67)`. The two runs measure
  `omega_67` twice, a consistency check across jobs.
- **Why simulation cannot answer it:** the calibrated noise model carries no
  detuning and no Z Z term. Its rates are zero in every sector.
- **Expected precision** (simulated visibilities, 1024 shots): `J` to about
  126 and 112 Hz, `omega_B` to about 145 and 138 Hz, and the falsifier
  residual to about 384 and 356 Hz.
- **Decision rule:**
  - Report every parameter with its 95 percent interval,
    `+- 1.96 x *_se_one_shot / 32`.
  - A falsifier interval that excludes zero rejects the static diagonal model
    for that pair.
  - The window comparison is descriptive. The window ran at a different time
    and calibration, so agreement within the combined intervals, modulo
    227.7 kHz windings, supports the frame-detuning reading, and disagreement
    points to a drifting or non-diagonal term. It is not a preregistered test
    of the earlier run.
- **Records:**

  | Record | sha256 |
  | --- | --- |
  | `2026-10-15T204407.674235Z/record.json` | `ab00c568d4bd00b5044ec3f2a021e3126b13c33a8a0a19e5ac48c8568a1b43e5` |
  | `2026-10-15T204427.864020Z/record.json` | `f41b6a0b980ea11cf6ac7354675c505a3bb4a041f02dc8d1d489d579cac8d029` |

  Both are at source `5e9cc80`, experiment digest `6e5733705f3a`,
  calibration 2026-10-15 13:25:14 PDT.
- **Jobs:** two static jobs of 50 PUBs on ibm_kingston, each with a 20 s
  ceiling and about 16 s nominal: about 32 s of the 266 s observed remaining.

Commands (run from gororoba_quantum/; refresh both dry runs first, then
replace the records and digests):

    "$PYTHON" live_run.py --groups conditional_ramsey --backends ibm_kingston --exclude-qubits ibm_kingston:0-66,69-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 20 --max-total-execution-seconds 20 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T204407.674235Z --approved-record-sha256 ab00c568d4bd00b5044ec3f2a021e3126b13c33a8a0a19e5ac48c8568a1b43e5 --submit
    "$PYTHON" live_run.py --groups conditional_ramsey --backends ibm_kingston --exclude-qubits ibm_kingston:0-65,68-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 20 --max-total-execution-seconds 20 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T204427.864020Z --approved-record-sha256 f41b6a0b980ea11cf6ac7354675c505a3bb4a041f02dc8d1d489d579cac8d029 --submit
