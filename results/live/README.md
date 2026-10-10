# Live-run audit records

Each directory is one run of `gororoba_quantum/live_run.py`, named by its UTC
start time: `record.json` holds the backend states, exclusions, selection
trace, noise-model predictions, and, after `--submit`, the job ids; `isa.qpy`
holds the compiled circuits.

- **Schema records.** A record carries `experiment_digest` and `code_commit`.
  Only such a record, after a submission, can be collected: `--collect` checks
  the digest against the checkout and names the commit to collect from.
- **Legacy dry-run plans.** `2026-10-10T165944+0000` and
  `2026-10-10T173416.028543Z` predate those fields. Both are dry runs with no
  submitted jobs. They record what earlier revisions of live_run.py selected
  and simulated, which the design notes cite, and `--collect` rejects them.
- **Current-schema record.** `2026-10-10T183023.567277Z` was written from
  commit 86045a0 with a clean source tree. Its zero_divisor_fringe group
  carries the readout-corrected summary: ratio 0.0436 raw and 0.0369
  corrected on ibm_kingston, under a noise model whose readout channel is
  the asymmetric one the correction inverts.
