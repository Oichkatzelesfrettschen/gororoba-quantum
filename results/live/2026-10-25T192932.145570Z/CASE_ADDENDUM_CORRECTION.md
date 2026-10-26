# Case addendum correction: latency-recovery on ibm_kingston

[CASE_ADDENDUM.md](CASE_ADDENDUM.md) keeps the bytes the user approved on
2026-10-25 (SHA-256
`41272663d2ac60e86d94e8cce8d2690c3dd61c580f83d5cc7d19c39ed1e9454b`). This
document corrects two of its statements without changing the approval, the
admission, the predictions or the 90 s ceiling.

## Layout

The addendum's layout [150, 151, 138, 152, 149, 153] is the routing template
the replica placement started from. The planned and executed replica sits on
physical qubits [106, 105, 104, 117, 107, 125] for r, d0, d1, d2, a0, a1:
`groups[0].replicas[0].initial_layout` of this directory's record.json, and
the only qubits the scheduler tables of job `dbf5kdom94ac738ssug0` touch. The
CZ counts (24 per encoded member, 14 per unencoded member) belong to that
replica.

## Account read

The addendum dates the primary account's 117 s of 600 s to
"2026-10-25T18:4x UTC". The reading came from the budget read of the first
latency-recovery exploration, which started at 2026-10-25T19:22:34Z
(`results/live/unretained-dry-run-logs/2026-10-25T192234.800525Z-latency-recovery-w526.log`).
That log keeps the start time and none of the usage values, so the 117 s
figure rests on the session's read alone. The conclusion stands either way:
117 s less the 60 s reserve falls below the 90 s ceiling, and the backup
account ran the dry run, the submission and the collection.
