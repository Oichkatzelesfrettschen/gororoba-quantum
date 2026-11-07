# Mechanism probes of the pathion kernel-map hardware runs

These scripts test the mechanisms behind three results of the Tuna-17 and Ascella runs
([findings, cross-platform section](../../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)):

- C1, the mirror failure of the Ascella two-block job (`c1_*.py`, `mirror_test.py`);
- C2, the positive selector-contrast offset of the Tuna-17 null block (`c2_*.py`);
- C3, the Tuna-17 `ba` misses, which follow the logical bit d2 (`c3_*.py`).

[mechanisms.md](mechanisms.md) lists each candidate mechanism with its predicted signature and the number that decides it;
each script writes the log of the same stem, and a script that saves an array or table keeps it beside the log
(`c1_observed.npz`, `c1_phase.npz`, `c1_static.npz`, `c2_scale.npz`, `c2_mech.json`, `c2_resid_fez.json`,
`c2_resid_marrakesh.json`, and the compiled-mesh caches `mesh_pairs.npz` and `mesh_four.npz`).

## Interpreter and inputs

The probes ran under the build host's `ci-py3.14.7` virtual environment
(`${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/ci-py3.14.7/bin/python`; its qiskit, qiskit-aer and ruff versions differ
from the pull-request pins, so `ci/pr_checks.sh` refuses it): Python 3.14.7, numpy 2.5.4, scipy 1.18.1, qiskit 2.6.0 and
perceval 1.3.1, with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. Every simulation is local: at most five qubits for the Tuna-17
and IBM block circuits, and single-photon propagation through the 12-mode compiled Ascella mesh. The scripts read the
retained records under `results/` (the two Ascella run directories, the Tuna-17 coin series and its stopped
predecessor, and the ibm_fez and ibm_marrakesh coset-map runs) and nothing else, so each resolves the repository
root from its own location and runs from any working directory.

Every random seed comes from `docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json` (indices 1 to 12, listed in
`docs/evidence/qrng_seeds/allocations.json`), so a rerun reproduces each log byte for byte. A log line that a seed
changes is a bootstrap or Monte Carlo statistic; every other line is deterministic.

## Run

```sh
export PYTHON="${PYTHON:-python3}" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
sh docs/evidence/pathion-kernel-map/conjectures/run_all.sh              # every step, about 5 minutes on 10 cores
sh docs/evidence/pathion-kernel-map/conjectures/run_all.sh c1_anchor    # one step by log stem
```

`run_all.sh` replaces a log only when its script exits zero and lists the steps in dependency order:
`c1_observed` writes `c1_observed.npz`, which `c1_phase`, `c1_anchor` and `c1_controls` read; `c1_phase` writes
`c1_phase.npz` and `c1_static` writes `c1_static.npz`, which `c1_heldout` reads; `c2_resid_fez` and
`c2_resid_marrakesh` write the tables that `c2_resid_informative` reads. A script that uses
`gororoba_quantum/parallel.py` (`ordered_map`) must run as a file. `mirror_test.py` takes the Ascella two-block run
directory as an optional argument and defaults to the retained one.

## Scripts and the finding each one backs

| Result | Scripts (log of the same stem) | Reads |
|---|---|---|
| C1 mirror failure of the two-block job | `mirror_test`, `c1_observed`, `c1_mesh`, `c1_predecessor`, `c1_phase`, `c1_phase_eq`, `c1_anchor`, `c1_controls`, `c1_static`, `c1_heldout`, `c1_static_null` (shared modules `c1_common`, `c1_mesh`) | `results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00`, predecessor `2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00` |
| C2 Tuna-17 null offset | `c2_scale`, `c2_algebra`, `c2_mech`, `c2_resid_fez`, `c2_resid_marrakesh`, `c2_resid_informative`, `c2_stopped`, `c2_tuna`, `c2_tuna_mech`, `c2_overrotation` (shared modules `c2_data`, `c2_circuits`) | `results/live/2026-11-06T201037.234804Z` and `2026-11-06T200832.558771Z` (`record.json`, `collect.json`, `raw/`, `isa.qpy`), `results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json` and the two series' raw shots |
| C3 Tuna-17 `ba` misses | `c3_readout`, `c3_walsh`, `c3_corr`, `c3_zz`, `c3_mech2`, `c3_depol`, `c3_multi` (shared module `c3_data`) | the coin series' cases and raw shots, `results/quantum_inspire/coupler_zz_tuna_17_analysis.json` |

The code of the checked-in analysis (`scripts/ascella_pathion_coset_block_pairs_analysis.py`,
`gororoba_quantum/pathion_coset_block.py`, `gororoba_quantum/pathion_coset_analysis.py`) is imported unchanged; the
probes add models and controls around it and never alter a retained record.

## Limits

- Static non-unitary per-path loss in the Ascella mesh is not tested: per-component loss is not retained.
- IBM ZZ crosstalk is not simulated (Heron publishes no coupler table); the IBM simulation uses calibrated target
  errors only.
- Tuna-17 gate durations (20 ns single-qubit, 60 ns CZ) and T1 are assumed, so the T1 and ZZ rows are scans.
- The static shifter fits use a ridge prior and are not an error map.
- The IBM bit mapping `int(bitstring, 2)` is verified by the exact match of the per-replica N_hat to
  `collect.json` `measured_statistics`.
