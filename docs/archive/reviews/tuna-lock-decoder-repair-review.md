The staged helpers are coherent offline predicates, but they are not admission-ready. One concrete false acceptance remains in staged source association: ordinary JSON decoding can collapse duplicate provider identities before validation. The bounded lock also cannot serve as an exact dispatch boundary without a lock-owning adapter.

I reviewed every line of the four staged blobs, the archived review, the staged designs, and the current unstaged design deltas. No tests or provider operations ran.

## Findings

1. **SERIOUS — duplicate provider identities can be falsely accepted.**

   `INDEX scripts/qi_tuna_source_association.py:31-40` applies duplicate-key and non-finite-number rejection only to catalogue and manifest bytes. Checkpoint, job, batch, file, result-page, raw-data, and histogram inputs arrive as decoded dictionaries at lines 153-160 and 203-245.

   Concrete false acceptance:

   ```json
   {
     "id": 11,
     "file_id": 999,
     "file_id": 12,
     "batch_job_id": 14,
     "number_of_shots": 4096,
     "raw_data_enabled": true
   }
   ```

   A conventional Python JSON decode retains `file_id: 12`; the staged verifier then accepts that identity chain. The acquisition design requires duplicate identities to be rejected, and its current working-tree wording explicitly requires byte-oriented parsing into privately owned objects at [tuna-destination-sequential-evidence-case.md:125](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   The staged tests construct dictionaries directly and therefore cannot falsify this acceptance. Every provider/checkpoint response must enter through a byte-oriented entry point using the same duplicate-key and non-finite-number policy as `_json_object`.

2. **SERIOUS if used as admission — expiry can occur between the final check and context entry.**

   `INDEX scripts/qi_tuna_bounded_lock.py:45-48` checks the external clock, checks `CLOCK_BOOTTIME`, and then yields. Suspension or scheduler preemption between lines 46 and 48 can resume after the deadline and enter the guarded body.

   The post-acquire regression at `INDEX tests/scripts/test_qi_tuna_bounded_lock.py:43-52` exercises an external callback that raises before the local deadline check. It does not exercise expiry after that check.

   The current dispatch design correctly limits the primitive: the adapter must check the approved boundary before every later request and retry, not infer admission from context entry ([dispatch design:145](../../../docs/design/tuna-qx-exact-dispatch-guard.md)). The staged helper is therefore defensible only as a lock primitive.

3. **SERIOUS — an arbitrary clock callback defeats the real-time wait bound.**

   `check_clock()` runs before the remaining-time calculation at line 35 and while holding the acquired kernel lock at line 45. A callback that stalls for five seconds with a one-second wait eventually produces a timeout but already exceeded the promised real-time bound. A callback that never returns creates an indefinite wait; after acquisition, it also retains the kernel lock indefinitely.

   The final adapter must restrict this callback to bounded local clock sampling. Provider reads, authentication refresh, filesystem operations, and other blocking work do not belong in it.

4. **SERIOUS integration boundary — descriptor lifetime remains entirely caller-owned.**

   The helper validates a bare descriptor with `fstat`, then later locks and unlocks the same integer. A same-process close/reuse between those operations can redirect the lock to another open file. Closing the descriptor after acquisition releases the intended lock while the body continues; `LOCK_UN` then raises `EBADF`. If another duplicate descriptor retains the same open-file description, the failed unlock can leave the kernel lock alive and mask an exception from the body.

   This behavior matches the documented caller-owned boundary, but the eventual adapter must open, validate, retain, and close the descriptor within one lexical ownership scope. It must also control duplication, inheritance, fork behavior, path/inode identity, filesystem semantics, and lock ordering.

5. **SLOPPY — lock tests establish exclusion, not a complete timing contract.**

   The tests correctly use real same-host kernel contention. They omit:

   - measured elapsed-time bounds;
   - local `CLOCK_BOOTTIME` expiry immediately after acquisition;
   - suspension or simulated clock advancement between the final check and entry;
   - exceptions raised inside the guarded body;
   - a blocked clock callback;
   - descriptor close/reuse and unlock failure;
   - inherited or duplicated descriptors.

   Static control flow does establish that a valid descriptor is unlocked through `finally` when the external check, local deadline check, or body raises normally.

## Archived decoder-review disposition

The archived review covers older hashes (`fa8198…` and `1f9efb…`), so several findings changed:

- **Malformed zero-count histogram key:** fixed. Width and binary-alphabet validation now precede comparison at `INDEX script:302-309`.
- **Valid width-20 zero-count bins:** accepted intentionally, as the acquisition design states. `Counter` equality therefore remains appropriate for that policy.
- **Batch/result pages:** improved. Both now require one supplied page, one item, exact positive identities, and `total=page=pages=1`.
- **Atomic page completeness:** unresolved. Supplied metadata cannot authenticate the query, establish a stable provider snapshot, or prevent a later result.
- **Lossy decoded JSON and mutable input ownership:** unresolved in the staged blob. The later unstaged design calls for a byte-oriented, privately owned parse.
- **Decoder drift:** substantially fixed. The code validates width, early-qubit order, arm-specific classical bits, and terminal bits, then independently recomputes counts before accepting `decode_counts`.
- **All-zero-only coverage:** fixed. The tests now include asymmetric baseline and rotated records plus a mutated-decoder rejection.
- **Stale design prose:** fixed in the staged acquisition design for raw-shot and histogram validation.

## Remaining admission, provenance, and timing limits

Index-wide search found only definitions, internal calls, and tests for these helpers. No staged production runner composes them.

The following obligations remain outside the reviewed predicates:

- authenticated catalogue digest, assignment opening, custody, concealment, and conditional fairness;
- account-bound approval consumption and durable attempt disposition;
- trusted source, interpreter, dependency, and producer snapshots;
- live backend, queue, heartbeat, pricing, terms, compiler, and transaction admission;
- stable pagination or explicit approval of the non-atomic page boundary;
- slot and campaign clocks persisted across restart;
- short-suspend detection beyond UTC plus `CLOCK_BOOTTIME`;
- per-request and authenticated-retry clock checks;
- result availability and zero-charge evidence by the observation boundary;
- late-charge reconciliation;
- served analog schedule, acquisition-index mapping, calibration, discrimination, thresholds, and IQ evidence;
- the separately approved QX-first run and explicit hardware approval.

Provider source readback proves stored source association. It does not prove that Tuna-17 served the corresponding physical schedule or that a decoded response identifies an algebra-specific mechanism.

## Exact staged SHA-256 hashes

| Staged blob | SHA-256 |
|---|---|
| `scripts/qi_tuna_bounded_lock.py` | `9eca83041bdce9c5681050310932be6f57bbd213b7c60a0e7e4f8324a7b297b1` |
| `tests/scripts/test_qi_tuna_bounded_lock.py` | `f8261547e1b963ef6167c6667645333a7563e1beebcb5cee67012ce04f84942f` |
| `scripts/qi_tuna_source_association.py` | `f2aba9288bc949d0e8693afa600a19c4755be3bf27ed60b4a14fc549cdc5a526` |
| `tests/scripts/test_qi_tuna_source_association.py` | `3205858ce0ab4efedee54823f0f70b8603d40f519d6e2f342344b4995b83c655` |

The final observed `HEAD` remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`. The source-association pair and both designs have unstaged edits (`AM`); this verdict applies to the exact index hashes above.
