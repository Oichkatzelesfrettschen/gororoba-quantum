# QPU time, calibration and submission mechanics

The root AGENTS.md section "QPU time and calibration" states the policy: the
600 s rolling window, the primary and backup accounts, the routing rule and the
approval workflow. This guide holds the mechanics behind that policy: how a
submission binds to its approved dry-run record, how calibration identity and
prediction reuse work, the qubit exclusion option, the per-instance inventories
and the Kaggle noise-snapshot rule.

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Simulations of 14 qubits or fewer run on Kaggle kernels through
  `scripts/kaggle_run.py` (`push`, `status`, `collect`), which bundles the
  entry's repository imports with `kaggle_kernel/` (the kernel program and
  its AGENTS.md), installs qiskit 2.6.0 and qiskit-ibm-runtime 0.50.0 with
  qiskit-aer 0.17.2 (or qiskit-aer-gpu-cu11 0.17.2 on a GPU), proves the
  hypercomplex package stack before the entry runs, and retains the output
  under results/kaggle/.
  A kernel runs on a CPU machine by default and on a GPU only when its
  widest density matrix reaches `local_compute.GPU_MIN_ACTIVE_QUBITS`;
  [Simulation on Kaggle](../kaggle/README.md#simulation-on-kaggle-cpu-gpu-and-ci-replay)
  gives the machine choice, the GPU setup and the CI replay rules.
  `docs/notes/kaggle/` holds the workflow, the measured
  substrates and the package-stack guide. Kaggle allows two concurrent GPU
  and five concurrent CPU batch sessions per account.
- A 15-qubit run is decision-gated: it waits for the user's approval of a
  written case, which names its substrate from the access inventory and
  says why that one answers the question.
  - Simulation: an optimized Aer run on the build host or on a Kaggle
    T4 x2. `SnapshotSimulator.run` cache-blocks the state across both T4s,
    and a 15-qubit density matrix takes about 4 s there
    (`docs/notes/kaggle/substrates.md`). The case's run first applies
    `docs/notes/kaggle/gpu-runbook.md`: local rehearsal, vectorized
    estimators, a sized timeout.
  - Hardware: Tuna-17 through Quantum Inspire, under its submission rules
    ([Quantum Inspire](../quantum_inspire/README.md#binding-rules)). `submit` refuses while any hardware job of the
    account is unfinished or ended under `HARDWARE_PAUSE_SECONDS` ago, so
    the run cannot overlap another session's job. Fifteen of 17 qubits
    include qubits the Tuna-17 notes exclude for readout or coupler faults
    (`docs/notes/quantum_inspire/experiments.md`), so the case names each
    one it uses.
- IBM hardware serves 16 or more qubits, or a smaller run whose question
  concerns the device itself (a named qubit's readout, detuning or drift);
  its case states why Aer cannot answer it.
- A kernel's
  noise comes from a retained `gororoba_quantum/calibration_snapshot.py`
  export, whose `--export` requires every gate and readout channel to equal
  live_run's noise model, and a Kaggle result enters the research state
  only through a CPU replay gate on a reduced case.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The case is written against a submit-free dry run, and the
  `--submit` command names that run with `--approved-record`, its record.json
  digest with `--approved-record-sha256`, and the case's seconds with
  `--max-execution-seconds` (the Sampler's max_execution_time, which the
  service enforces; the dry run is made with the same value, since the
  policy carries it). `--max-total-execution-seconds` caps the sum of all
  job ceilings, and `--reserve-seconds` names the retained quota. The fresh
  plan must match the record in experiment
  digest, shots, policy (twirling, DD, budget floor, execution ceiling),
  dependency versions, IBM Cloud instance, groups, backends, seeds, layouts,
  replica qubits, fused PUB manifests, calibration values at the refresh and
  again at each batch, and QPY bytes, or the run writes an
  `approval_required` record and sends nothing. The calibration binds by
  value: each dry-run group records `calibration_fingerprint`
  (`live_run.calibration_values` over its packed circuits: the Target timing
  constraints, error and duration of every routed instruction, T1 and T2 of
  every touched or delayed qubit, and each measured qubit's asymmetric
  readout channel), so a republished `last_update_date` with every value
  unchanged keeps the approval and the run records the accepted timestamp
  pair under `approved_record.calibration_values`, while any changed value
  refuses. An approved record without fingerprints keeps the timestamp rule,
  and timestamps compare as instants whatever their UTC offset. Right after
  the first discovery, before planning, the submission checks the approved
  isa.qpy circuits against the fresh Target and properties by the same rule
  and writes `approval_required` in seconds. When the source digest,
  dependency versions, simulator seed, policy, compiled circuits, QPY bytes
  and every group's calibration values equal the approved record's, and
  every recorded Aer batch ran on CPU by a route the host's GPU cannot
  change (`local_compute.host_independent_route`), the submission copies the approved predictions (`reuse_approved_predictions`)
  and, for a matched family whose approved search held one routed candidate
  set under the same contracts, tiers, PUB cost inputs and optimization
  budget, the approved design (`approved_family_design`) instead of
  simulating; any differing input re-plans in full, and the run records
  `prediction_reuse` with the approved record's digest. The submission plans only over
  the backends the approved record found eligible
  (`live_run.approved_backend_scope`), so a
  backend whose queue or status changed after the dry run cannot enter the
  plan; an approved backend that turns ineligible still refuses through the
  comparison. `--exclude-qubits BACKEND:Q[,Q|A-B...]` withholds named qubits
  from placement whatever their calibration; the policy records it, so the
  approval binds it, and every snapshot, the per-batch one included,
  applies it. The first batch consumes the approval by writing
  `approval-consumed.json` into the approved record's directory, so a second
  invocation on the same record sends nothing. Calibration reads,
  transpilation, noise simulation, result retrieval, and `--preserve-raw`
  need no approval.
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates, and submits; no calibration value is cached or read back from a
  file to drive a submission.
- Overflow account. The default saved account is primary. A second saved
  account named `backup-ibm-quantum-platform` holds a different IBM Cloud
  instance with its own 600 s rolling quota, and quotas never pool.
  `GOROROBA_IBM_ACCOUNT` selects the account for every script through
  `gororoba_quantum/ibm_account.py` (`open_service`); unset or empty
  constructs `QiskitRuntimeService()` and selects the default. A case
  written against the backup sets `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`
  for its dry run, `--submit` and `--collect` alike: the approval binds
  `instance_sha256_12`, so a submit under another account refuses, and
  `--collect`, `--preserve-raw`, ghost_calibrations.py and
  compare_submitted_circuits.py raise when the service resolves an instance
  other than the record's. The backup serves when the primary's remaining
  seconds minus the reserve fall below the case's summed ceilings. Each
  instance has its own inventory, `results/live/qpu-job-inventory.json` for
  the default and `results/live/qpu-job-inventory.<instance_crn_hash>.json`
  for another (observe_qpu_job_inventory.py refuses to overwrite a file that
  records a different instance), and its own `qpu-job-retention-audit` file;
  reconcile_qpu_inventory.py assigns each raw archive to the instance its
  run record names and checks coverage, the usage-window sum and the reserve
  per instance, while the historical-job and campaign accounting bind the
  default instance. The `ibm_account.py --self-test` in gate `core-self-test-05` (`tests/test_cli_self_tests.py`)
  holds the account selection and the instance refusal.
- Retaining a collected run. A run directory joins the tree with every
  register that enumerates retained jobs, in one change: the instance's job
  inventory (`scripts/observe_qpu_job_inventory.py`, a service read), the
  retention audit (`scripts/reconcile_qpu_inventory.py`, which writes each
  instance's audit and creates the file exclusively), the submitted-circuit
  comparison (a successor written by `scripts/compare_submitted_circuits.py
  --write --out NEW_PATH --seed PREVIOUS`, a service read of the missing jobs'
  submitted programs under the replay interpreter of gate core-281, because
  QPY digests follow the Qiskit version; the procedure is in
  [the comparison README](../../evidence/submitted_circuits/README.md)), and
  the registry (`scripts/research_state.py --write`, with the claim that cites
  the run). Run-family registers (the ghost, scaffolding-exposure and
  local-member CZ records) follow the gates that read the run. Gate core-281
  fails while an audited job is missing from the comparison, and the
  `research_state.py --check` gate while a retained run is missing from the
  registry.
