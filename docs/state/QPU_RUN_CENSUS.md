# QPU and simulation run census

This census lists every run the repository still proposes, the machine it
belongs on, and its cost. Routing follows AGENTS.md: a simulation of 14
qubits or fewer runs on Kaggle through `scripts/kaggle_run.py`, and IBM
hardware serves 15 or more qubits or a question about the device itself.
Every IBM run still needs the owner's approval of its written case, and
nothing below has been submitted.

The account reported 334 of 600 s consumed and 266 s remaining on the
rolling 28-day window; every dry run below confirmed the 266 s.

## IBM hardware: held cases, re-planned

Each case asks about named qubits of ibm_kingston, so noise simulation
cannot answer it: the simulator only replays the calibration the question
tests. All five were dry-run again against the calibration of
2026-10-15T15:29:07-07:00. Nominal seconds are the sum over PUBs of shots x
(250 us repetition delay + scheduled circuit duration) plus 2.3 s of job
overhead; the ceiling is the `max_execution_time` the service enforces.

| Case | Qubits | Why the device | PUBs x shots | Nominal s | Ceiling s | Fresh record | record.json sha256 |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| Conditional Ramsey, pair (68, 67) | 2 | measures the detunings and Z Z behind the -1.130 rad window rotation | 50 x 1024 | 15.8 | 20 | `results/live/2026-10-15T224704.122016Z` | `b29c0a3825f09f1c90c078d244beb875739d8c97fbcb85ce328e64ed8f1707b5` |
| Conditional Ramsey, pair (67, 66) | 2 | the second pair of the same prediction | 50 x 1024 | 15.8 | 20 | `results/live/2026-10-15T224725.179602Z` | `fceebffbb3376d6c9676da907a1077719f412622ae2ad5f0199335517f597b0f` |
| Crossed tile x template | 4 + 4 | separates the Kingston qubit 0/1 readout fault from the template | 40 x 512 | 7.5 | 15 | `results/live/2026-10-15T224747.140174Z` | `8c7764d2e40c3e102b3cd089e956a951c3d19c7650a4ec9fd1b8e27d9372d030` |
| Walk scaffold A/B | 4 | the 252-CZ readout floor against measure-only on qubits 80-83 | 4 x 1024 | 3.4 | 10 | `results/live/2026-10-15T224805.443398Z` | `960baeef4f53830a75fb46eb4d8a718c5b7f4251262a9ba42e0aafdcef944a02` |
| Qubit-79 delayed readout | 1 | whether the 11 % first-bit effect is relaxation of qubit 79 | 4 x 1024 | 3.4 | 10 | `results/live/2026-10-15T224821.527684Z` | `a0f865be93b024fbcf4ba9a49bca5e818cf429490b245d1a003cda8268ef0c43` |
| **Total** | | | | **45.9** | **75** | | |

Running all five leaves at least 191 s of the 266 s.

**Qubit 79 prediction.** The fresh calibration gives qubit 79 T1 = 191.6 us,
T2 = 75.7 us and P(read 0 | prepared 1) = 0.0085. The noise model predicts
P(read 0 | X) of 0.012 immediately, 0.080 after 4000 dt (16 us) and 0.245
after 12500 dt (50 us). Relaxation alone accounts for about 8 of the 11
percentage points seen in the first-bit disagreement, so the case decides
whether the rest is a state change or a correlated readout effect. A
measured 16 us value above about 0.11 contradicts relaxation as the whole
mechanism; one near 0.08 makes the first-bit effect a property of qubit 79's
T1 at that calibration, which drifts.

**Submit commands**, valid only for the records above and only after the
owner approves the case; a calibration change before submission makes the
comparison write `approval_required` and send nothing:

```sh
"$PYTHON" live_run.py --groups conditional_ramsey --backends ibm_kingston --exclude-qubits ibm_kingston:0-66,69-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 20 --max-total-execution-seconds 20 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T224704.122016Z --approved-record-sha256 b29c0a3825f09f1c90c078d244beb875739d8c97fbcb85ce328e64ed8f1707b5 --submit
"$PYTHON" live_run.py --groups conditional_ramsey --backends ibm_kingston --exclude-qubits ibm_kingston:0-65,68-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 20 --max-total-execution-seconds 20 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T224725.179602Z --approved-record-sha256 fceebffbb3376d6c9676da907a1077719f412622ae2ad5f0199335517f597b0f --submit
"$PYTHON" live_run.py --groups crossed_tile_template --backends ibm_kingston --exclude-qubits ibm_kingston:4-103,108-155 --shots 512 --max-replicas 2 --no-isolated-reference --max-pending 100 --max-execution-seconds 15 --max-total-execution-seconds 15 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T224747.140174Z --approved-record-sha256 8c7764d2e40c3e102b3cd089e956a951c3d19c7650a4ec9fd1b8e27d9372d030 --submit
"$PYTHON" live_run.py --groups scaffold_ab --backends ibm_kingston --exclude-qubits ibm_kingston:0-79,84-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 10 --max-total-execution-seconds 10 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T224805.443398Z --approved-record-sha256 960baeef4f53830a75fb46eb4d8a718c5b7f4251262a9ba42e0aafdcef944a02 --submit
"$PYTHON" live_run.py --groups readout_delay --backends ibm_kingston --exclude-qubits ibm_kingston:0-78,80-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 10 --max-total-execution-seconds 10 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T224821.527684Z --approved-record-sha256 a0f865be93b024fbcf4ba9a49bca5e818cf429490b245d1a003cda8268ef0c43 --submit
```

Every earlier family (folded QPE, folded correction, ripple atlas, rank
sectors, N21 orbit, patch window, coherence window) has a consumed approval
and a retained acquisition; their older held records are superseded dry
runs.

## IBM hardware: proposals without a case

| Proposal | Qubits | State | What it needs before a case |
| --- | --- | --- | --- |
| Readout-adjacent pre-delay discriminator (measure, variable delay, Ramsey) | 1-2 | design only | a design module and dry run; applies only to idles that follow a mid-circuit readout, such as the N21 orbit's |
| Chip-wide checkerboard detuning map | patch or chip, 15+ | design only | two quadratures, a winding-resolving delay ladder and spectators in both states; the first design in this census that needs 15 or more qubits |
| Echo-matched dilation (`proposed-echo-matched-dilation`) | 4-5 | proposed | a Kaggle noise run that sizes the rotation-error contrast, then a device case |
| Signed kernel probe (`proposed-signed-kernel-probe`) | 7 | proposed | Kaggle first: the sign-odd signal against the calibrated noise floor |
| Census-frequency witness (`proposed-census-frequency`) | 5 (fixed pair) to 13 (three registers) | proposed | Kaggle first: visibility V and the shots that resolve 231/512 |
| Dim-32 Design C spectral classes | 5 | Kaggle result retained (`docs/evidence/design_c_cubic_noise/`) | the noise model keeps the classes apart (noisy K 0.180-0.253 against 0.093-0.113); a hardware case would test coherent errors and crosstalk the model lacks, about 4.4 s nominal for both class representatives at 4096 shots (2 x 4096 x 260 us plus 2.3 s of job overhead) |

Withdrawn as QPU candidates (`docs/evidence/simulation-notebook-audit/README.md`):
the triple-dependent detuning Ramsey (no circuit sets a frequency from a
triple label), the interleaved differential Ramsey below 500 Hz (two arms at SNR 2
need 4/dP^2 shots, about 2.9 million or 750 s at 50 Hz, nearly three times
the remaining quota), the pre-delay
sweep on the 84/84 pairs, and the CCZ normal form as a fidelity test of the
84/84 circuits (dim 16 has no cubic phase).

## Kaggle: simulations of 14 qubits or fewer

| Run | Qubits | Question | State |
| --- | --- | --- | --- |
| `gororoba-aer-gpu-smoke` | 14 | qiskit 2.5.2 and qiskit-aer-gpu-cu11 0.17.2 on the Kaggle GPU | complete: 2 x T4, a 14-qubit density-matrix GHZ in 1.6 s |
| `gororoba-design-c-cubic-noise` | 5 | does the 11/32 against 5/32 collision separation survive the compiled factorized circuit under the Kingston calibration | complete: yes, ranges 0.180-0.253 and 0.093-0.113 at 20,000 shots; CPU replay gate core-282 |
| Census-frequency witness | 5-13 | V and shot count for the 231/512 test | to design |
| Walk scaffold under coherent and leakage models | 4 | which loss channel reproduces the retained readout0 floors | to design |
| Signed kernel probe at calibrated noise | 7 | the detectable t range | to design |
| Conditional Ramsey power at calibrated noise | 2-3 | the delta-method precision the case quotes | to design |

## Checks that need no QPU

- **Submitted circuits (done).** `scripts/compare_submitted_circuits.py`
  retrieved the submitted program of all 23 retained jobs through
  `job.inputs` and compared each item with the circuit expected at the same
  position: the job's ordered PUBs in `record.json` (`submission.jobs[].pubs`)
  resolved by name in `isa.qpy`, or the retained submission order for the
  recovered wide-control job. All 488 items are `CircuitItem`s equal to
  their expected circuit in order, and every job's item count equals its
  audited `pub_count`, so no job carried client-side twirling and the
  service received exactly the circuits each record holds
  (`docs/evidence/submitted_circuits/comparison.json`, gate core-281
  rechecks it offline). What the control electronics did with those
  circuits stays outside any record.
- **VLF transmitter outages.** A calendar comparison of transmitter
  maintenance against the run dates; it needs no hardware.
