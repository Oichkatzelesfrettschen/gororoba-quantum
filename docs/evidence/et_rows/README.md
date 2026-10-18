# Exact ET rows and native acquisition contracts

The ET family tests signed multiplication and column interference on a routed
device. The finite arithmetic is checked independently before acquisition.
Hardware results require a separately approved case.

`pilot.zip` preserves the supplied offline pilot bytes. `pilot_manifest.json`
and `pilot_et_fixtures.json` preserve the corresponding original records.
`rust/` contains unchanged canonical modules from the commit in
`rust_sources.json`; `harness.rs` supplies an isolated execution boundary.
`canonical_replay.json` records the exact comparison and exported-byte digest.
The harness checks source warnings as errors and builds in temporary storage.
Dead-code allowances apply only to imported canonical modules because the
harness deliberately exercises a subset of their public interfaces.

The audit supplied two reports and described an additional evidence archive.
The local Downloads, Documents and Projects search found the reports and pilot;
the described additional archive was absent from those measured search roots.
The integration regenerates its Rust and QPY receipts rather than interpreting
the supplied report's numbers as a newly executed check.

## Replay

Run from the repository root using the current requirements environment:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" -B scripts/replay_et_sources.py --check
"$PYTHON" -B scripts/replay_et_pilot.py
"$PYTHON" -B gororoba_quantum/check_et_rows.py
"$PYTHON" -O gororoba_quantum/check_et_rows.py
"$PYTHON" -B gororoba_quantum/check_et_campaign.py
"$PYTHON" -B gororoba_quantum/check_et_runtime.py
```

The original pilot verifiers intentionally reject optimized Python. Their
QPY replay runs under ordinary Python; integrated family contracts use explicit
exceptions and also run under optimized Python. New ET artifacts require
Qiskit 2.6.0. Historical evidence continues using the separately pinned replay
interpreter when its gate requests Qiskit 2.5.2.

## Mathematical scope

`claims.json` binds finite checks and inspected formal declarations to their
domains, conventions and outstanding bridges. The checksum ledger covers
every retained file in this evidence directory.

For the unnormalized assessor `a=e_l+e_(l xor X)`, the paired Gram blocks
have diagonal entries 2 and off-diagonal entries `eta1+eta2`. An occupied
block contributes one zero eigenvector and one eigenvector of eigenvalue 4.
Other blocks have eigenvalue 2. The exact finite census checks the excluded
labels as well as occupied columns. Numerical rank thresholds are unnecessary.

The signed child box contains shifted interior labels `G_old xor c` and
boundary labels `G_old,G_old xor S`. At D64/S15, rows 1, 17 and 16 sample
the primary copy, shifted interior and new boundary respectively. The
independent witness is parent(1,6)=-7, child(17,22)=-7, mixed child(1,22)=-23.

The inspected Rocq foundations include numeric multiplication-sign
correspondence, half-step recurrences, assessor rules, Brown/de Marrais
bridges, Walsh probability normalization, Boolean ANF and CD phase-degree
results. Their declaration scopes differ. Boolean ANF degree, graph degree
and multiplier nullity are separate quantities. The integrated finite ET
checks do not claim a new all-order Rocq theorem or a fresh upstream kernel
replay. `upstream/issues.json` links the missing semantic and formal bridges.

## Source identities

| Role | Commit |
|---|---|
| Imported pilot algebra | `84cefcaf64755f004da4d485f1ef1fe16f4eb0c7` |
| Imported pilot quantum | `832c9b671abf2f4a47683558f33b8d2cc83e47c4` |
| Audited canonical algebra | `2b72e552b95f7fe529a5abb45049f6d3e47cdd97` |
| Supplied integration audit quantum | `3ab52b7d2e965bf1c6dc16d56f34da7ed7b1f4eb` |
| Implementation base | `13d00a29ea9b039c4ff5eeec3f1c7939d80f65ef` |
| Existing algebra CI dependency | `7d95d228db6be8a5b2f613430f04f2385d6ae48a` |

The algebra CI dependency remains separate from the vendored canonical
constructor used by the focused comparison.
