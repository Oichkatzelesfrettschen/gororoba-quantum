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

The [idle-readout successor](comparison-idle-readout.json) rebinds the same retrieval offline after `live_run.py`
gained role-patterned members and listed `idle_readout.py` in its experiment manifest.

The [idle-readout and window-dose successor](comparison-idle-readout-window-doses.json) rebinds the same
retrieval offline against the `live_run.py` that carries the role-patterned members and the window doses; it
differs from the idle-readout successor only in the `live_run.py` digest and the offline validation time.

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

The [idle-readout repeat successor](comparison-idle-readout-repeat.json) rebinds the idle-penalty repeat retrieval
offline against the `live_run.py` that adds the role-patterned members and lists `idle_readout.py` in its
experiment manifest; it differs from that retrieval only in the `live_run.py` digest and the offline validation
time. The [state-prep remeasure successor](comparison-state-prep-remeasure.json) rebinds the same retrieval
offline against the `live_run.py` whose `--state-prep-arms` help names the two-read arms `x_remeasure` and
`remeasure`; it differs from the retrieval only in that digest and the validation time.

The [detuning-sign retrieval](comparison-detuning-sign-retrieval.json) reads the same 41 jobs afresh through the
read-only job interface, seeded from the original comparison, after the retention audit added the N=21
detuning-sign Kingston job `dbge2jpj4t8s73ac6fk0` under `awaiting_observation`, which moves the audit digest every
earlier comparison binds. Its 41 rows equal the idle-penalty repeat retrieval's. A fresh retrieval binds the audit,
the original seed and the collector, so a later `live_run.py` change leaves it valid.

The [QPY-18 full retrieval](comparison-qpy18-full-retrieval.json) covers all 43 jobs of the retention audit after a
fresh primary-instance inventory bound the idle-penalty repeat's job `dbgcnp5rd2mc73cuf5p0` and the detuning-sign
job `dbge2jpj4t8s73ac6fk0`. Both runs retain an `isa.qpy` in QPY format 18, which Qiskit 2.6.0 writes and Qiskit
2.5.2 cannot read, so no seeded extension of the 2.5.2 chain can validate them. The collector therefore runs
unseeded under Qiskit 2.6.0 and qiskit-ibm-runtime 0.50.0, reads all 43 jobs' submitted inputs through the
read-only job interface, and records 786 items, each equal to its retained circuit in order, with QPY digests
serialized by 2.6.0. Its collector bytes equal the archived [collector text](collector-idle-penalty-retrieval.py.txt).
The 2.5.2 comparisons above keep their bytes as the record of the earlier serializer.

An offline rebind successor binds the audit, original seed, current collector, predecessor comparison and archived
collector text, plus the direct repository dependencies `ibm_account.py`, `parallel.py` and `live_run.py`. These
named files and the pinned Qiskit/runtime versions bound the replay; the provenance does not claim a complete
transitive import closure. Every earlier comparison retains its recorded bytes; each binds an earlier audit digest
and job set, so none checks against the current audit.

The [row ledger](jobs/) replaces whole-audit successors. `jobs/qiskit-<release>/<job_id>.json` holds one audited
job's row with its own provenance (origin, retrieval time, runtime versions, collector digest) and keeps its bytes
once written. The QPY-18 full retrieval was split into `jobs/qiskit-2.6.0/` offline (`--split`), each row naming the
comparison file and digest it came from. `--append` reads only the audited jobs without a row through the read-only
job interface and writes one file each, so a retention adds one row per new job. `--check-rows` requires exactly one
row per audited job, retrieved under the running Qiskit release, and re-derives every submitted digest from the
retained circuits; it binds neither the audit's bytes nor this script's, because the re-derivation is the check.
QPY bytes follow the Qiskit release (35 of 684 circuits serialize differently under 2.5.2 and 2.6.0 even at QPY
format 17 with the generator version masked), so a Qiskit pin change fills a new `jobs/qiskit-<release>/` by
`--append` and leaves the earlier ledger as its record.

Replay the row ledger from the repository root with the current pinned interpreter, and append rows for newly
audited jobs:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" -B -W error scripts/compare_submitted_circuits.py --check-rows
"$PYTHON" -B -W error scripts/compare_submitted_circuits.py --append
```

QPY reserialization depends on the Qiskit version: Qiskit 2.5.2 reproduces all 28 original rows, while Qiskit 2.6.0
produces different serialized digests. The checker requires the successor's recorded runtime versions; changing
serialization versions requires a separately justified successor rather than replacing the original hashes.

A future read-only extension under the current runtime uses `--write --out NEW_PATH` without a seed, because
`--seed` accepts only the v3 original, whose 2.5.2 digests the current serializer does not reproduce. With a
seed, the collector validates seed rows before opening the service,
fetches only missing jobs, validates every complete row before publication, and refuses an occupied output path.
The collector creates neither quantum jobs nor circuit uploads. Independent per-job QPY validation runs through
the order-preserving process pool; sequential service retrieval preserves the read-only request order. Tests
compare serial and two-worker results and first-failure ordering.

A source-binding successor uses `--rebind PREVIOUS_V4 --collector-snapshot ARCHIVED_TEXT --out NEW_PATH`. Offline
rebinding validates every retained row, the original seed, the predecessor's source snapshot and runtime, then
preserves retrieval identities while recording the offline operation separately. The writer refuses an occupied
destination. Retained source changes require a new comparison because the successor binds its collector's bytes.
