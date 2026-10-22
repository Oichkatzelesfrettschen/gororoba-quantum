# Hypercomplex operator cases

Run commands from the repository root. Export the intended interpreter and TLS setting:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/hypercomplex_evidence.py --check docs/evidence/hypercomplex-operators/certificate.json
"$PYTHON" scripts/hypercomplex_cases.py --out results/hypercomplex/cases
"$PYTHON" scripts/hypercomplex_campaign.py results/hypercomplex/cases/quantum_inspire/order
```

The last command reads cases and prints a frozen plan; generation and planning submit nothing. Regeneration uses the compiler version recorded in each manifest. A different compiler can produce different bytes; retain a new bundle instead of overwriting an admitted case.

## Quantum Inspire written cases

| Family | Batches | Circuits | Shots per circuit | Modeled execution | Mandatory interbatch pause |
|---|---:|---:|---:|---:|---:|
| Order pilot | 8 | 24 | 16384 | 270.80 s | 840 s |
| Four-site wave and controls | 24 | 72 | 16384 | 812.41 s | 2760 s |
| Fourier inputs and identities | 8 | 24 | 16384 | 270.80 s | 840 s |

The model `2.6+0.00053*shots` estimates each child job at 11.284 s. Queueing, calibration, API latency and collection add wall time. The complete sequence also pauses between families. The live provider limit remains 300 s per circuit and 131072 shots; the plan leaves duration headroom. Empty debit history establishes zero recorded debit for that observation, rather than unlimited credit.

The first approval case descriptively measures Tuna-17 output frequencies for a faithful two-qubit complex order encoding under device noise. The [adversarial preregistration addendum](../design/tuna-order-pilot-adversarial-admission.md) withholds representative equivalence and scientific continuation claims. Ideal simulation cannot measure Tuna readout, crosstalk or drift. Each batch contains two readout references and one science circuit, with one queued hardware batch account-wide. The runner waits until all account hardware jobs finish and the latest finish precedes the next batch by at least 120 s. The rule applies between batches, rather than between children of one approved batch. API hardware classification includes any emulator marked as hardware.

The raw grouped probabilities are primary. Output readout contrast below 0.2 rejects the batch for scientific continuation. Requested and angle-quantized native operators remain distinct. The compiler retains the entire native operator, seed, version and measurement mapping. Stop on partial submission and use the provider runner's read-only reconciliation; repeating submission can duplicate acquisitions.

After the user approves the named plan digest and written case, invoke the existing campaign entry point with `--execute`, `--approval`, `--approved-plan-sha256` and an explicit `--max-wait-seconds`. Approval text records the actual user decision. A nonempty string supplied by an operator is a receipt mechanism, not an independent authorization source.

The generated files live under `results/hypercomplex/cases/quantum_inspire/`. A live acquisition must retain under the provider's canonical `results/quantum_inspire/runs/` tree and enter the usage ledger and research registry together. Copy a complete frozen family to its named acquisition directory, verify the printed plan digest agrees, and execute there. The case filenames and manifests remain unchanged. The case-only tree contains no acquisition.

Collect the complete primary wave before producing measured art:

```sh
"$PYTHON" scripts/hypercomplex_campaign.py ACQUISITION_WAVE_DIRECTORY --measured-wave MEASURED_RECORD.json
"$PYTHON" scripts/hypercomplex_evidence.py --render MEASURED_RECORD.json --out NEW_MEASURED_EVIDENCE_DIRECTORY
```

Replace uppercase command arguments with the retained acquisition paths. The collector requires seventeen distinct times, counts, matching submission/circuit digests and raw job identities. The plot shows nominal IID Wilson sensitivity intervals; temporal dependence and calibrated coverage remain separate analyses. Phase is unmeasured.

## Quandela written cases

The fixed single-photon meshes implement complete 4-mode order or 8-mode wave/Fourier operators. Every iteration requests at most 8192 detected samples and 16384 shots, under a 180 s job duration cap. The existing Quandela runner checks the complete operator for this schema. The order, wave and transform jobs contain 8, 24 and 8 iterations respectively.

Use `scripts/qd_platform.py` with the generated `cases.json` through the [Quandela guide](../notes/quandela/README.md). Obtain a fresh estimate for each supported platform before choosing Ascella, Belenos or their cloud simulators. The documented per-job formula uses the largest iteration's shot limit: where the recorded tariff applies, `1+0.000001*16384 = 1.016384` credits per job. Backend tariff, duration charge and remaining account balance require fresh read-only checks. Cloud simulator execution still requires a written case and may carry a per-job charge.

The device question concerns measured photonic mesh conformance, loss and drift. Local SLOS/Naive computation validates synthesis; it cannot measure the cloud device. Preserve raw counts and filtering/loss metadata. Obtain case approval before any provider job, upload or other charged operation, as [AGENTS.md](../../AGENTS.md#hardware-services) requires.

## Frozen approval identities

Quantum Inspire order plan SHA-256: `43e0b67a8aaaa1203eacd5f0be9e4c74ac5f4f55576dc16f96591245864dc8a2`. Maximum native operator approximation error: 0.003996 in spectral norm.

Quantum Inspire wave plan SHA-256: `621bafd5f0f96afc7d1c78330646bd50f9621430770310a2a19583627b9da059`. Maximum native operator approximation error: 0.165745 in spectral norm.

Quantum Inspire transform plan SHA-256: `51ba12723273c0fe564899ecf47d8b94e662c0d426ddc0bb7eaa32358e25920d`. Maximum native operator approximation error: 0.117699 in spectral norm.

These identities bind the generated compilation, rather than authorizing execution. The pilot asks for 24 child jobs and 393216 total shots. Its modeled execution plus seven mandatory pauses is 1110.80448 s, before queue and calibration delay.
