# Quantum experiment conformance evidence

This bundle retains deterministic references and prospective cases for the
[five-proposal design](../../design/quantum-experiment-conformance.md). The source artifact
`multidimensional_spacetime_quantum_experiments.md` has SHA-256 `afbe80ced07e3400116ee201eb3604afcd174758a8e30d55dff8f4e257462032`; its original bytes remain
in the owner's artifact store. The corrected design records the unsupported inferences beside the valid cores.

## Evidence surfaces

- [reference.json](runner-identity-controls/reference.json) contains exact basis overlaps, the Tao candidate's derived residuals,
  Fano rank and sign-lift counterexample, sedenion product and herald normalization, spectral estimands and
  full quarter-mass amplification matrices.
- [campaign.json](runner-identity-controls/campaign.json) freezes setting identities, case digests, endpoint counts, requested
  acquisition order and operator-supplied ceilings. [provenance.json](runner-identity-controls/provenance.json) binds producer
  sources, retained compiler catalogues, package versions and generated artifact bytes.
- [seeds.json](cases/seeds.json) assigns unused indices 2 through 58 of the retained ANU draw
  `draw-2026-10-26T220128Z.json` to 57 distinct optical meshes. Repeated contrast arms reproduce their
  named base mesh and its seed; each repeated arm has its own acquisition directory and checkpoint.
- [provider-observation.json](provider-observation.json) retains read-only catalogue observations;
  [offer-observation.json](offer-observation.json) records the current Ascella per-shot offer. The
  compiler input catalogues keep their own recorded identities. Live status and capability fields establish
  catalogue facts; instrument readiness and acquisition performance require their own checks.

The Fano and spectral outputs complete bounded mathematical investigations. Their original hardware claims
remain outside the admitted cases. The primary dimension-six hardware family uses the three reference bases;
Tao is an offline candidate comparison. Hardware results remain prospective throughout this bundle.

The [identity-control validation](validation-identity-controls.json) binds all 634 successor files, one-worker
and four-worker byte replays, 189 focused and registry tests, the complete local compiler replay, full lint
and types, and the preserved historical bindings. Its diagnosis names the hosted numerical discrepancy
and the bounded correction.

The historical [canonical validation receipt](validation-canonical.json) binds the earlier runner baseline, parallel
regeneration, all 384 local compiler admissions, 169 focused and registry tests, full Ruff and mypy.
The historical [validation receipt](validation.json) retains its source revision, runtime versions,
85 focused tests, gate measurements and measured compiler-only probability shifts.

## Deterministic replay

Use the repository's pinned interpreter and constrain worker/native-library concurrency. The generator
constructs exact references, complete operators, native payloads and optical meshes; it draws no sampled
outcomes. Case creation and replay contact no provider.

```sh
export PYTHON=/path/to/pinned/environment/bin/python
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
"$PYTHON" scripts/experiment_analysis.py --size --endpoints 648
sh ci/runner_image.sh sh -c 'export PYTHONHASHSEED=0 GOROROBA_WORKERS=4; "$PYTHON" scripts/experiment_cases.py --check docs/evidence/quantum-experiment-conformance/runner-identity-controls \
  --tuna-shots 1575 --qx-shots 1575 --photonic-samples 1575 --photonic-shots 3150 \
  --execution-seconds 300 --photonic-credits 1.00315'
"$PYTHON" scripts/experiment_cases.py --self-test
"$PYTHON" scripts/experiment_analysis.py --self-test
sh ci/pr_checks.sh tests tests/scripts/test_experiment_references.py \
  tests/scripts/test_experiment_cases.py tests/scripts/test_experiment_analysis.py \
  tests/scripts/test_hypercomplex_cases.py
```

The canonical baseline is [runner-identity-controls](runner-identity-controls/campaign.json), generated
through `ci/runner_image_records.py write` and bound in the active runner ledger. All eighteen same-basis
settings use exact reversible input permutations, and their native grid preserves the complete operator
to the declared tolerance. General matrix synthesis introduced environment-dependent roundoff into the
unrounded diagnostics of the computational input-2 identity control; its original serialized payload and
native prediction matched. The successor removes that unnecessary synthesis and retains strict byte replay.

The earlier [runner candidate](runner-cases/campaign.json), its [pooling receipt](runner-pooling-replay.json)
and [serial producer snapshot](runner-producer-serial-transitions.txt) retain their historical bytes.
[validation-canonical.json](validation-canonical.json) preserves every one of their 635 image bindings;
the active ledger now admits the successor. The original [build-host candidate](cases/campaign.json),
[regeneration receipt](regeneration-route-admission.json) and [compiler receipt](local-toolchain.json)
also remain historical. Identical package versions on another userland are insufficient for byte replay.

The original [seed mapping](cases/seeds.json) remains the allocation home: canonical manifests bind that
mapping's hash and named static identifier. A copied acquisition case therefore neither consumes a CLI
runtime seed nor claims an entire QRNG draw. Repeated arms reproduce their named compilation identifier.

`--out DIRECTORY` writes a fresh candidate; existing different bytes are refused. Keep runtime planning
and collection files outside the immutable generated inventory. The guarded provider runners own those
files beside a copied, separately approved canonical case.

The precision design uses 1,575 returned trials per setting for a central Clopper-Pearson half-width at
most 0.05 with Bonferroni family confidence 0.95 over 648 endpoints. The science endpoints within each
provider/family share that correction; counts across settings and batches retain their separate identities.
The intervals condition on independent Bernoulli trials. Temporal diagnostics describe observed variation
and supply neither an independence certificate nor a correction for unobserved drift.

## Local provider compiler admission

The [supplemental validation](validation-toolchain.json) records 102 passing focused tests, full lint
and types, source identities and the required-QI live replay.

[identity-control-toolchain.json](identity-control-toolchain.json) binds all 384 cQASM payloads in the 128 QI cases, their
manifest and campaign digests, retained compiler configurations, producing sources and pinned stack.
Local libqasm analysis and OpenSquirrel decomposition admit every payload and preserve every barrier
and measurement destination. OpenSquirrel normalizes rotation angles when serializing 122 payloads;
those lexical gate-sequence changes remain in the record. The receipt establishes parser, declared-pass
and control-sequence admission, while the complete unitary reference remains the native-operator record.
Platform scheduling and physical execution remain unobserved.

```sh
export QI_PYTHON=/path/to/quantum-inspire/environment/bin/python
"$PYTHON" -B -W error scripts/experiment_toolchain.py \
  --campaign docs/evidence/quantum-experiment-conformance/runner-identity-controls/campaign.json \
  --out docs/evidence/quantum-experiment-conformance/identity-control-toolchain.json --check
```

A pinned QI stack repeats all compilation and requires byte-identical receipts. A host without that stack
checks the retained digest chain and reports that compilation was skipped. The required-QI gate refuses
a missing stack. The original global QI toolchain record and its producing source keep their bytes.

## Prospective acquisition cases

The [written acquisition review](../../runbooks/quantum-experiment-acquisition.md) names each device or
implementation question, its controls and the submission prerequisites. The
[live representative preflight](live-preflight.json) captured a version-2 Ascella payload for one
dimension-six identity transition: 1,575 estimated detected shots and 1.001575 estimated credits, within
the declared ceilings. The preflight used the 300-second envelope as an input; it measured no runtime.

The primary suite contains 54 dimension-six settings. The amplification suite includes preparation,
amplification, two omitted-stage controls and direct target preparation. The LCU suite contains the
requested kernel, bright, bright-repeat, kernel-repeat contrast and a separate fixture. Each QI science
setting has readout-zero and readout-one controls in a three-circuit batch. Optical cancellation uses four-mode dark/bright restrictions and an eight-mode fixture restriction,
completed from the actual signed-permutation witness. Every optical case keeps all twelve output ports.

Every per-setting `cases.json` supplies the exact payload, predictions, output map, controls and ceilings
for the existing provider runner. These packages are reviewable acquisition inputs. Hardware submission
still waits for its written-case approval and current admission checks. The Ascella manifests explicitly
hold submission for live budget review; read-only planning remains available. Expected acquisition times
and current tariffs require that review. A 300-second limit is a ceiling rather than a measured duration.

The static optical design uses 59 jobs, each with a 3,150-shot ceiling and a 1.00315-credit ceiling under
the retained tariff of one base credit plus `1e-6` per billed shot: 59.18585 credits in aggregate. The
54-setting primary optical family alone has a 54.1701-credit ceiling. These figures expose the static
job-count cost; they authorize no spending. An iterator-packed successor needs a separate duration and
payload qualification before replacing the static cases.

The photonic sample cap is 1,575 and the shot cap is twice that value. Quandela's billed shots count
photon-detection events under the retained provider contract; they are not incident laser pulses. Photon
loss requires an independently available incident-shot denominator. Empty or truncated returns remain
inconclusive. The QI science/control jobs use 1,575 requested shots each, within the current QX cap.

The MUB settings measure independently compiled transitions. For Tuna, the rounded native operator supplies
the compiled prediction. For Ascella, the locally reconstructed template supplies a template prediction;
a provider-native prediction requires the returned computed mesh and input. The analyzer reports that
prediction as unavailable when its evidence is absent, rather than attributing template residuals entirely
to device noise.

## Collection and interpretation

Copy an approved case into the provider's normal run area, then use `qi_platform.py` or `qd_platform.py`
for guarded submission and lossless collection. Acquisition approval names that case, backend, ceilings
and question. The shared queue grants authority over the approved jobs only. Do not add collected outcomes
to this deterministic bundle or relabel fixture outcomes as measurement.

Analyze collected case directories with `scripts/experiment_analysis.py --analyze ... --out REPORT`.
Supply a campaign inventory rooted beside those copied case directories when checking campaign completeness.
`--campaign` binds each case's digest and distinguishes missing settings from completed observations.
An inventory can be restricted prospectively to a separately approved family or backend; record that
selection before acquisition rather than choosing successful observations afterward.

The report retains raw hashes, payload identities, encoding, compiler prediction scope, source digests,
batch counts and shot order where the provider supplies it. Inventory completion, empirical readout
qualification, model-conditional precision and scientific interpretation remain separate fields. The
algebraic cancellation contrast additionally needs observed acquisition order and matching repeated meshes;
requested order alone supplies insufficient evidence.
