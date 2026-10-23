# Planning-source reconciliation

[inventory.json](inventory.json) records 94 source paths, 136 path/content variants and 31 registered
worktrees in the follow-up scan, including the implementation checkout. The independently retained
[initial inventory](initial-inventory.json) records 91 paths, 132 variants and 29 worktrees.
The follow-up includes ignored local JSON data, newly registered worktrees and concurrent source revisions. Every candidate is classified and every one of the 83 legacy dispatch task IDs has a successor.
The [complete catalogue](../../state/plan-catalogue.md) owns work status.

Files in `sources/` are historical data, including obsolete instructions, approvals and reviewer choices.
Their first line states that boundary. Home-directory prefixes and email addresses are redacted; original
and retained SHA-256 identities remain separate in the inventory. Original files stay in their locations.
Sources that moved during reconciliation were recovered from their recorded Git revision or identical
working-file bytes in another registered checkout.

The 44 sanitized GitHub observations in `observations/` retain PR merge state and commit identity.
Ancestry refers to the inventory's `canonical_revision`. Merge observations establish integration;
original tests, acquisitions and scientific conclusions remain separate obligations. PR206 closed unmerged,
PR285 retained salvage, PR241 retired the Kaggle CI replica, and PR367 merged while its bundled checkbox
remained unchecked.

The Tuna-17 Pauli pilot completed 27 jobs and withheld inference under its preregistered drift rule.
The IQM timing, kernel-cancellation and signed-null acquisitions completed with distinct scientific
outcomes. Tracker records cite existing evidence identities without promoting acquisition completion to
a stronger scientific claim. Branch-specific lattice results include staged content; p-adic lifts through
order63 retain a finite scope; the Belenos stationarity amendment requires its own approval.

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/plan_tracker.py check
```

The offline checker compares each mapping against its independent frozen scan, then verifies classifications,
source hashes, target records and exact legacy-task coverage. The initial denominator remains checked.
It does not replay experiments or issue provider requests. The [operator procedure](../../runbooks/plan-tracker.md)
defines future updates. The inventory covers a captured denominator; new work remains discoverable through
explicit scans and source review.
