# Written case: zdac

Approved by the owner on 2026-10-15 ("a-c please") with bounded seconds; this
case binds the record below. No backend is pinned except where the case is a
characterization of named qubits.

- Measures: Design B zero-divisor annihilation, (e1 + e10) on (e4 -/+ e15) through one ancilla, with the Design D eight-phase fringe (group zero_divisor_fringe), with the low-index corner qubits that underperformed in the rank and ripple runs excluded on ibm_kingston (0-4, 16) and ibm_fez (2-4, 16). Noise simulation cannot separate how much of the measured annihilation floor is coherent, incoherent or offset on the hardware; the fringe does.
- Record: `2026-10-15T070828.397109Z/record.json`, sha256 `341fcc11bdfc2e9ebb6e86a59792051a3027db992b1bcb98bc4df7259506174e`.
- Jobs: [('ibm_kingston', 'static', 14, 13)]; replicas {'zero_divisor_fringe': [[58, 70, 71, 72, 73], [47, 57, 66, 67, 68], [107, 108, 109, 110, 118], [32, 33, 34, 35, 39], [100, 101, 102, 103, 116], [138, 149, 150, 151, 152], [117, 124, 125, 126, 127], [76, 80, 81, 82, 83]]}.
- Ceilings: 13.0 s total.
- Preregistered readout: dark P(s=0) at the dark phase, bright P(s=0), and the eight-phase fringe fit P0(phi) = o + A cos phi + B sin phi with visibility V = 2 sqrt(A^2 + B^2) and phase phi0 = atan2(B, A), per replica and pooled. Decision rule: the dark value decomposes exactly as (1 - V)/2 (incoherent contraction) + (o - 1/2) (offset) + (V/2)(1 - cos phi0) (coherent phase error) up to fit residual; the term that carries most of the excess over the noise model names the floor's origin.

Command (run from gororoba_quantum/):

    "$PYTHON" live_run.py --groups zero_divisor_fringe --exclude-qubits ibm_kingston:0-4,16 --exclude-qubits ibm_fez:2-4,16 --shots 2048 --max-pending 100 --max-execution-seconds 13 --max-total-execution-seconds 13 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live --approved-record ../results/live/2026-10-15T070828.397109Z --approved-record-sha256 341fcc11bdfc2e9ebb6e86a59792051a3027db992b1bcb98bc4df7259506174e --submit
