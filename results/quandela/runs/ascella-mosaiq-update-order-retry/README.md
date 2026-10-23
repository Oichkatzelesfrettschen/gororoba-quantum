# Ascella order acquisition after the advertised Mosaiq update

Ascella completed the original eight-setting order pilot after its processor
record advertised mosaiq-arcturus 2.1.5.2.post4, replacing the earlier observed
2.1.5.1.post2. The user explicitly approved one new attempt and replaced the
consumed retry's stopping rule for that attempt. The manifest remains
`1d1b9abfe727d92f6af1c81002b3e41e056b1b16330d3b8ae9746303bc3968fa`.
The acquisition ran under an unprivileged account with directory mode 700 and
file mode 600. The runner used the normal user shell and its token submit lock.

| Observation | Result |
|---|---|
| Job | `889c0b21-6b14-473c-a81b-5ae90e244ea9` |
| Submitted | 2026-10-23 17:11:41 UTC |
| Terminal status | completed |
| Settings / detected samples | 8 / 65,536; 8,192 per setting |
| Provider execution duration | 25 seconds |
| Job-level reported shots | 16,384 |
| Sum of per-setting `nb_shots_used` | 65,536 |
| Approved sample / shot caps | 65,536 / 131,072 total |
| Approved duration / credit ceilings | 180 seconds / 1.016384 credits |
| Token-reported debit | 1.016384 free credits; zero paid credits |

The job-level shot field, per-setting shot fields and cap are different
provider accounting observations. They are not an audited laser-pulse count.
The token's Ascella totals increase from six jobs and six seconds to seven
jobs and 31 seconds. Account-wide remaining balance remains unobserved.

The [processor observation](platform-before-submission.json),
[preflight](preflight.json), [submission](submission.json),
[sent body](job-body.json), [checkpoint](submission-state.json),
[raw result](raw/result.json) and [parsed results](results.json) retain the
request and service response. The processor observation establishes an
advertised software version; the job schema supplies neither an executing
worker identity nor a hardware-configuration digest. The successful sampling
establishes recovery of this tested path. The exact provider repair remains
unobserved, and the software update alone does not prove causality.

## Questions and observations

The eight settings combine two values of each order angle (zero and pi/4)
with two encoded representative states, as defined by
[`order_settings`](../../../../scripts/hypercomplex_cases.py).
The [operator case runbook](../../../../docs/runbooks/hypercomplex-operator-cases.md)
owns their complex encoding and interpretation.

- The instrument-readiness question asks whether the unchanged request
  completes and returns positive counts after the deployment observation
  changes. All eight settings returned counts, contradicting a continuing
  failure of this particular sampling path at that observation.
- The conditional-intensity comparison asks how the recorded output law
  differs from the frozen ideal law. The [analysis](analysis.json) conditions
  on occupation sum one among the four returned modes. It retains thirteen
  excluded multiple-occupation observations (zero vacuum observations). Conditional total
  variation from the requested law ranges from 0.00048828125 to
  0.02796092796. These are descriptive distances, with no preregistered
  acceptance threshold or calibrated uncertainty claim.
- The compilation check propagates the returned twelve-mode numerical mesh
  through a bounded protobuf decoder. Its four-output conditional law differs
  from the requested law by at most 0.00029815991 total variation. Returned
  compiled metadata does not itself establish the applied controls.

This original pilot returns four modes from a twelve-mode device. It cannot
measure discarded-output leakage or absolute calibrated transmission. A
single ordered block cannot isolate temporal drift. Counting alone supplies
neither complete phase reconstruction nor a test of fundamental quaternionic
quantum mechanics.

The [local serialized-request replay](../../../local-simulation/ascella-serialized-order-replay/replay.json)
executes the previous failed job's exact computation on local SLOS and Naive
backends. Both return 65,536 simulated samples; sixteen exact-probability
checks differ from the manifest by at most 4.45e-16. The fresh cloud body
changes only its process ID, preserving the serialized computation. Local
simulation validates the request semantics and excludes the physical
instrument configuration from its execution boundary.

Replay the hardware analysis without provider access:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" results/quandela/runs/ascella-mosaiq-update-order-retry/analysis.py --check
```

## Larger packed acquisition boundary

The user allowed a 1.1-credit ceiling for a longer design while this approved
attempt was in flight. The completed job retains its approved 180-second
ceiling and original case bytes. The live service advertises a 300-second
maximum per job. Under the recorded tariff, one job with a largest iteration
shot cap of 100,000 costs at most `1 + 0.000001 * 100000 = 1.1` credits.
That arithmetic does not establish how many settings finish within 300
seconds. The observed eight-setting completion supplies one timing point,
rather than a validated scaling law. A larger written case should retain all
physical outputs, specify matched repeats and bracketed references, and
refresh its estimate and approval before another submission. Wave and
transform acquisition families retain their separate cases.
