# Unapproved case: walk scaffold A/B and the qubit-79 delayed readout

Not approved. This case covers two records, this one and
`2026-10-15T212016.630328Z`. A submission needs the owner's approval against
fresh dry runs of both commands below; the records go stale when ibm_kingston
recalibrates or its queue changes.

## Scaffold A/B (this record)

- **Question:** does the shared walk template's 252-CZ scaffold carry the
  walk readout floor on its tile?
  - The retained ripple run read P(0000) = 0.336 on Kingston 80-83 for a
    circuit that is logically the identity
    (`docs/evidence/walk-control-scaffolding`).
- **Design** (`gororoba_quantum/diagnostic_controls.py`, `scaffold_ab`): one
  job of four PUBs at 1024 shots on qubits 80-83:
  - the template bound to readout0 and to readout1, at 254 CZ each as
    compiled here;
  - a measure-only circuit and an X-then-measure circuit, at 0 CZ.
- **Prediction:**
  - The calibrated noise model gives the template 0.575 (P(0000)) and 0.579
    (P(1111)), against 0.947 and 0.910 without the scaffold.
  - If the scaffold carries the loss, hardware reads the template near the
    retained 0.336 and the scaffold-free arms near 0.95.
  - Scaffold-free arms near the template value would place the loss in
    preparation or readout instead.

## Qubit-79 delayed readout (`2026-10-15T212016.630328Z`)

- **Question:** what changes qubit 79's state behind the correction runs'
  first-bit correlation?
  - In those runs about 11 percent of shots record its bit as 0.
  - In the known-label arms, the shots where it reads 0 lose terminal
    success, which excludes independent, state-preserving assignment error.
- **Design** (`readout_delay`): one job of four PUBs at 1024 shots on qubit
  79: |0>, |1>, and |1> followed by 4000 dt (16 us) and 12500 dt (50 us)
  idles.
- **Prediction:**
  - The calibrated model gives P(0 | 1) of 0.008, 0.079 and 0.242 for the
    immediate, 16 us and 50 us reads, so relaxation over a 16 us window
    already approaches the 11 percent.
  - An immediate loss near 0.11 points to preparation or assignment.
  - A loss that grows with the idle along the calibrated T1 points to
    relaxation before the mid-circuit readout.

## Bindings

- **Why simulation cannot answer either:** both compare the device against
  its own calibrated model, and the retained runs show that the model
  understates both effects.
- **Records:**

  | Record | sha256 |
  | --- | --- |
  | `2026-10-15T212000.401292Z/record.json` | `d4691778749bc672381ea2ee7490d8086a4742d8ffe95c14c67c964fa036d786` |
  | `2026-10-15T212016.630328Z/record.json` | `4f791d581fc13d04d450409fcbb6de25653564339279b56281b5f01ffb04c86e` |

  Both are at source `53cc29d`, experiment digest `38d154493b48`,
  calibration 2026-10-15 13:55:38 PDT.
- **Jobs:** two static jobs of four PUBs, each with a 10 s ceiling and about
  3.5 s nominal (4 x 1024 shots at about 260 us, plus 2.3 s of overhead):
  about 7 s of the 266 s observed remaining.

Commands (run from gororoba_quantum/; refresh both dry runs first, then
replace the records and digests):

    "$PYTHON" live_run.py --groups scaffold_ab --backends ibm_kingston --exclude-qubits ibm_kingston:0-79,84-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 10 --max-total-execution-seconds 10 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T212000.401292Z --approved-record-sha256 d4691778749bc672381ea2ee7490d8086a4742d8ffe95c14c67c964fa036d786 --submit
    "$PYTHON" live_run.py --groups readout_delay --backends ibm_kingston --exclude-qubits ibm_kingston:0-78,80-155 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 10 --max-total-execution-seconds 10 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T212016.630328Z --approved-record-sha256 4f791d581fc13d04d450409fcbb6de25653564339279b56281b5f01ffb04c86e --submit
