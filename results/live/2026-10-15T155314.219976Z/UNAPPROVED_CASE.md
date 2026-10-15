# Unapproved case: conditional Ramsey on one coupled pair

Not approved. A submission needs the owner's approval of this written case
against a fresh dry run of the command below; this record goes stale when
the backend recalibrates or its queue changes.

- **Measures:** the four phase rates of the pair Hamiltonian
  `(omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2` on ibm_kingston qubits 149 (A)
  and 148 (B), in 50 circuits at 1024 shots each:
  - Bell even and odd, and Ramsey of A with B in |0> and in |1>, at delays 0
    to 10000 dt in both quadratures (48 circuits);
  - an in-job readout calibration of both qubits (2 circuits).

  The readout is `omega_A`, `omega_B`, `J` and the falsifier residual
  `nu_odd + nu_even - nu_A|0 - nu_A|1`, each with its propagated standard
  error (`docs/notes/conditional_ramsey_hamiltonian.md`).
- **Why simulation cannot answer it:** the calibrated noise model carries no
  detuning and no Z Z term, so this record's local simulation predicts zero
  rates in every sector. The rates exist only on the device.
- **Why it is the next coherence measurement:** the coherence window measured
  one Bell sector's idle rotation. Two Bell sectors leave `J` unidentified
  (design rank two), and the conditional arms raise the rank to three.
- **Expected precision:** at the simulated visibilities (0.77 to 0.92 at
  40 us), the propagated standard errors at 1024 shots are about 108 Hz on
  `J`, 119 Hz on `omega_B` and 322 Hz on the falsifier residual. The unwrap
  bound is 50 kHz.
- **Decision rule:**
  - Report the three parameters with 95 percent intervals, estimate
    +- 1.96 x `*_se_one_shot` / sqrt(1024).
  - A falsifier residual whose interval excludes zero rejects the static
    diagonal model for this pair under this calibration.
  - B preparation error is read per sector, and bounds the conditional phase
    bias by `arcsin(eps / (1 - eps))`.
- **Record:** `2026-10-15T155314.219976Z/record.json`, sha256
  `43540ee9cfbdbad7692979d7bb3bb88780f164fe9571103dd303004251734bc8`;
  source `c567ca8`, experiment digest `f8c111e7005d`, calibration
  2026-10-15 08:35:51 PDT.
- **Job:** one static job of 50 PUBs on ibm_kingston, ceiling 20 s. Nominal
  cost is 50 x 1024 shots x about 270 us (250 us repetition delay plus a mean
  idle under 17.5 us), about 13.8 s, plus 2.3 s of job overhead: about 16 s
  of the 266 s observed remaining.

Command (run from gororoba_quantum/; refresh the dry run first, then replace
the record and digest):

    "$PYTHON" live_run.py --groups conditional_ramsey --exclude-qubits ibm_kingston:0-4,16 --exclude-qubits ibm_fez:2-4,16 --shots 1024 --max-replicas 1 --no-isolated-reference --max-pending 100 --max-execution-seconds 20 --max-total-execution-seconds 20 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T155314.219976Z --approved-record-sha256 43540ee9cfbdbad7692979d7bb3bb88780f164fe9571103dd303004251734bc8 --submit
