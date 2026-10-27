# Submitted circuit comparison

The [pooled-validation comparison](comparison-pooled-validation.json) covers all 40 jobs in the
[retained-job audit](../../../results/live/qpu-job-retention-audit.json). The collector revalidated and reused the
28 rows of the immutable [original comparison](comparison.json), then retrieved the twelve missing jobs' submitted
inputs through the IBM Runtime read-only job interface. The missing set includes four failed jobs and eight
completed jobs, with 148 circuit items. Every retrieved item equals its expected retained circuit in order.
These observations establish submitted-circuit agreement rather than successful execution of a failed job.

The [service-retrieval comparison](comparison-retained-audit.json) records the actual retrieval time and twelve
retrieved job IDs. The pooled-validation successor preserves those fields and all 40 rows, and records a distinct
offline validation time. The [historical collector text](collector-retained-audit.py.txt) retains the exact source
that produced the service-retrieval comparison; the snapshot is data rather than an active Python module.

The [ordered-map successor](comparison-ordered-map-cancel.json) rebinds the retained-audit comparison offline
after `parallel.py` began cancelling queued chunks once an item raises; its 40 rows equal the pooled-validation
comparison's, and only that dependency digest and the offline validation time differ.

The [experiment-manifest successor](comparison-qrng-seeds-manifest.json) rebinds the retained-audit comparison
offline after `live_run.EXPERIMENT_SOURCE_MANIFEST` began listing `qrng_seeds.py`; it differs from the
ordered-map successor only in the `live_run.py` digest and the offline validation time.

The [latency-recovery successor](comparison-latency-recovery-family.json) rebinds the retained-audit comparison
offline after `live_run.py` gained the latency-recovery family's flags; it differs from the experiment-manifest
successor only in the `live_run.py` digest and the offline validation time.

The [seed-flag successor](comparison-live-run-seed-flags.json) rebinds the retained-audit comparison offline
after `live_run.py` gained its QRNG seed flags; it differs from the latency-recovery successor only in the
`live_run.py` digest and the offline validation time.

The [QET-campaign successor](comparison-qet-campaigns.json) rebinds the retained-audit comparison offline after
`live_run.py` listed `qet_ladder.py` in its experiment manifest and refused dynamical decoupling for the three QET
campaigns; it differs from the seed-flag successor only in the `live_run.py` digest and the offline validation time.

The [primorial-campaign successor](comparison-primorial-campaigns.json) rebinds the retained-audit comparison
offline after `live_run.py` gained the structure-preserving compilation contract, pinned layouts for the
`coherence_probes` and `primorial_gap88` campaigns and their manifest entries; it differs from the QET-campaign
successor only in the `live_run.py` digest and the offline validation time.

The [readout-preflight successor](comparison-readout-preflight.json) rebinds the retained-audit comparison
offline after `live_run.py` listed the `readout_preflight` campaign among its pinned campaigns; it differs from
the primorial-campaign successor only in the `live_run.py` digest and the offline validation time.

The [measurement-sequence successor](comparison-measurement-sequence-families.json) rebinds the retained-audit
comparison offline after `live_run.py` gained the measurement-sequence and measurement-sequence-diagnostic families;
it differs from the QET-campaign successor only in the `live_run.py` digest and the offline validation time.

The [compiled-ideal successor](comparison-pooled-compiled-ideals.json) rebinds it after `live_run.py` and `qpu_planning.py`
proved the compiled ideals through the process pool; its rows equal the predecessor's.

The [idle-penalty retrieval](comparison-idle-penalty-retrieval.json) covers all 41 jobs of the retained-job audit
after Kingston job `dbfrg3fpc3tc739o4kag` joined it. Seeded from the original comparison, it retrieved the 13 jobs
that comparison lacks, the earlier twelve and the new one, through the read-only job interface, and every item equals
its retained circuit in order. [Its collector text](collector-idle-penalty-retrieval.py.txt) keeps the exact
source. The [idle-penalty successor](comparison-idle-penalty-probe.json) rebinds that retrieval offline after
`live_run.py` listed `idle_penalty.py` in its experiment manifest and refused dynamical decoupling and twirling for
the campaign. It binds the direct dependencies.

The [idle-penalty pin successor](comparison-idle-penalty-pin.json) rebinds the same retrieval offline after
`live_run.py` admitted `idle_penalty` to `--pin-layout`; it differs from the idle-penalty successor only in the
`live_run.py` digest and the offline validation time.

The [window-dose successor](comparison-window-doses.json) rebinds the idle-penalty retrieval offline after
`live_run.py` gained `--window-doses-dt`; it differs from the idle-penalty successor only in the `live_run.py`
digest and the offline validation time.

The [pin and window-dose successor](comparison-pin-window-doses.json) rebinds the same retrieval offline
against the `live_run.py` that carries both changes; it differs from its two siblings only in the `live_run.py`
digest and the offline validation time.

The [adaptive-envelope successor](comparison-adaptive-envelope.json) rebinds the idle-penalty retrieval offline
after `live_run.py` gained the measurement-sequence envelope's approval, fallback and replan contract beside the
window doses; its 41 rows equal the window-dose successor's.

The [detuning-sign successor](comparison-detuning-sign.json) rebinds the idle-penalty retrieval offline after
`live_run.py` gained `--detuning-sign`; its 41 rows equal the adaptive-envelope successor's, and it differs from that
successor only in the `live_run.py` digest and the offline validation time.

The [idle-penalty repeat retrieval](comparison-idle-penalty-repeat-retrieval.json) reads the same 41 jobs afresh
through the read-only job interface, seeded from the original comparison, after the retention audit listed the
stability repeat's Kingston job `dbgcnp5rd2mc73cuf5p0` under `awaiting_observation`; that audit change ends the
offline rebind chain, which binds the audit's digest. Its collector equals the archived
[collector text](collector-idle-penalty-retrieval.py.txt), and it binds the `live_run.py` that carries the pin
admission, the window doses, the envelope contract and `--detuning-sign`. Every item equals its retained circuit
in order.

The [detuning-sign retrieval](comparison-detuning-sign-retrieval.json) reads the same 41 jobs afresh through the
read-only job interface, seeded from the original comparison, after the retention audit added the N=21
detuning-sign Kingston job `dbge2jpj4t8s73ac6fk0` under `awaiting_observation`, which moves the audit digest the
previous retrieval binds. Its 41 rows equal the idle-penalty repeat retrieval's. Gate `core-281` checks it.

The active successor binds the audit, original seed, current collector, predecessor comparison and archived
collector text, plus the direct repository dependencies `ibm_account.py`, `parallel.py` and `live_run.py`. These
named files and the pinned Qiskit/runtime versions bound the replay; the provenance does not claim a complete
transitive import closure. Every earlier comparison retains its recorded bytes. Gate `core-281` checks the
active successor and its predecessor chain on the historical `qiskit-2.5` replay runtime.

Replay from the repository root with the interpreter qualified against `ci/requirements-replay.txt`:

```sh
export PYTHON="${REPLAY_PYTHON:?Set REPLAY_PYTHON to the qualified qiskit-2.5 interpreter}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" -B -W error scripts/compare_submitted_circuits.py --check \
  --out docs/evidence/submitted_circuits/comparison-detuning-sign-retrieval.json
```

QPY reserialization depends on the Qiskit version: Qiskit 2.5.2 reproduces all 28 original rows, while Qiskit 2.6.0
produces different serialized digests. The checker requires the successor's recorded runtime versions; changing
serialization versions requires a separately justified successor rather than replacing the original hashes.

An authorized future read-only extension uses `--write --out NEW_PATH --seed
docs/evidence/submitted_circuits/comparison.json`. The collector validates seed rows before opening the service,
fetches only missing jobs, validates every complete row before publication, and refuses an occupied output path.
The collector creates neither quantum jobs nor circuit uploads. Independent per-job QPY validation runs through
the order-preserving process pool; sequential service retrieval preserves the read-only request order. Tests
compare serial and two-worker results and first-failure ordering.

A source-binding successor uses `--rebind PREVIOUS_V4 --collector-snapshot ARCHIVED_TEXT --out NEW_PATH`. Offline
rebinding validates every retained row, the original seed, the predecessor's source snapshot and runtime, then
preserves retrieval identities while recording the offline operation separately. The writer refuses an occupied
destination. Retained source changes require a new comparison because the successor binds its collector's bytes.
