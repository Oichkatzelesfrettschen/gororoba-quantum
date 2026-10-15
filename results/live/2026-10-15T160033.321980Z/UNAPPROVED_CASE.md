# Unapproved case: crossed tile x template on ibm_kingston

Not approved. A submission needs the owner's approval of this written case
against a fresh dry run of the command below; this record goes stale when
the backend recalibrates or its queue changes.

- **Question:** does the Kingston rank-sector weak-lane loss follow the
  physical tile, the circuit template, or their combination? Sector 4 always
  ran on qubits 0-3, so the earlier acquisitions cannot separate them.
- **Selection history:** the tiles were chosen after seeing the data:
  - the weak tile 0-3 is where the endpoint decomposition located 15 of
    Kingston's 29 off-model endpoints;
  - the corner baseline then measured P(1|0) of 0.388 and 0.274 on qubits 0
    and 1;
  - the reference tile 104-107 is where sector 7 ran in the same rank
    acquisition.

  Only this prospective run can confirm a tile effect.
- **Design** (`gororoba_quantum/crossed_tile_template.py`): one group holding
  the 20 science members of sector 4 (affected template) and of sector 7
  (reference template). Their exact selector-success laws match member for
  member. The group runs as two replicas, one on each tile, so every PUB row
  executes one member on both tiles in the same shots: 40 PUBs at 512 shots.
- **Response and contrasts:** the response is the endpoint error
  `y = (mean over ideal-one members of (1 - p) + mean over ideal-zero members of p) / 2`.
  From it come the tile effect T, the template effect L, and the interaction
  `I = (y_w4 - y_w7) - (y_r4 - y_r7)`, each with a Bonferroni 95 percent
  interval (z = 2.394).
- **Predictions:**
  - The calibrated noise model of this dry run reads T = -0.003
    [-0.009, +0.003], L = -0.003 and I = +0.005: no tile effect.
  - The corner-measured readout channel of qubits 0 and 1, applied to the
    weak tile's selector bits, predicts T = 0.315 with L = I = 0, whichever
    selector bit each qubit reads.
- **Why simulation cannot answer it:** the reported calibration of qubits
  0-3 is nominal, so the planner's model predicts no tile effect. The fault
  is visible only in measured data.
- **Decision rule:**
  - Loss follows the tile when T's interval excludes zero and L's contains it.
  - It follows the template when L excludes zero and T contains zero.
  - A resolved I means one template is especially sensitive on one tile.
  - The readout hypothesis is consistent with the run when T falls within
    0.315 +- its interval half-width; a resolved T far below it leaves part of
    the loss unexplained.
- **Record:** `2026-10-15T160033.321980Z/record.json`, sha256
  `d2a0ccc356c414febe78ddde1b3f6a184c2e80e907d48a591dcd280e49989d41`;
  source `8eb17cc`, experiment digest `a11d092c2164`, calibration
  2026-10-15 08:49:10 PDT. Replica 0 sits on 104-107 and replica 1 on 0-3,
  at 20 CZ per member.
- **Job:** one static job of 40 PUBs on ibm_kingston, ceiling 15 s. Nominal
  cost is 40 x 512 shots x about 260 us, about 5.3 s, plus 2.3 s of job
  overhead: about 8 s of the 266 s observed remaining.

`"$PYTHON" crossed_tile_template.py --record <collect.json>` prints the
contrasts after collection.

Command (run from gororoba_quantum/; refresh the dry run first, then replace
the record and digest):

    "$PYTHON" live_run.py --groups crossed_tile_template --backends ibm_kingston --exclude-qubits ibm_kingston:4-103,108-155 --shots 512 --max-replicas 2 --no-isolated-reference --max-pending 100 --max-execution-seconds 15 --max-total-execution-seconds 15 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T160033.321980Z --approved-record-sha256 d2a0ccc356c414febe78ddde1b3f6a184c2e80e907d48a591dcd280e49989d41 --submit
