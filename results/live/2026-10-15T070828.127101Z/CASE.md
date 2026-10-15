# Written case: corner

Approved by the owner on 2026-10-15 ("a-c please") with bounded seconds; this
case binds the record below. No backend is pinned except where the case is a
characterization of named qubits.

- Measures: The qubit_baseline group on ibm_kingston qubits 0-4 and 16 only, to discriminate readout, relaxation and frequency causes of the steady loss in rank sector 4 and ripple lane 6. Reported calibration data show nothing wrong with these qubits, so a model cannot answer it.
- Record: `2026-10-15T070828.127101Z/record.json`, sha256 `b9fd50af55c51fd2a9e22795a765642e4b32a4225a5af69f2ecd5fb719836cc8`.
- Jobs: [('ibm_kingston', 'static', 7, 9)]; replicas {'qubit_baseline': [[0, 1, 2, 3, 4, 16]]}.
- Ceilings: 9.0 s total.
- Preregistered readout, per physical qubit of the corner: P(1) after ground preparation and P(0) after X (assignment errors), retained excited population after a 50 us idle (relaxation), and X/Y Ramsey phase and visibility at 2 us and 10 us idles. Decision rule: assignment errors well above the reported readout error point to readout; a relaxation or Ramsey visibility well below the reported T1/T2 points to decoherence; a Ramsey phase that winds between the two idles points to a frequency shift.

Command (run from gororoba_quantum/):

    "$PYTHON" live_run.py --groups qubit_baseline --backends ibm_kingston --exclude-qubits ibm_kingston:5-15,17-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 9 --max-total-execution-seconds 9 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T070828.127101Z --approved-record-sha256 b9fd50af55c51fd2a9e22795a765642e4b32a4225a5af69f2ecd5fb719836cc8 --submit
