Complete static review of the staged Python clock predicate and tests found no reachable incorrect admission or in-instance refusal-latch escape under the trusted, serialized, single-process contract.

## Findings

- **SERIOUS integration limit — construction remains outside the refusal latch.** Invalid inputs fail at [qi_tuna_dispatch_clock.py:43](../../../scripts/qi_tuna_dispatch_clock.py) before `_refused` is installed at line 55. A caller can also construct a fresh object after refusal. The external adapter must bind one clock instance to the attempt and handle failed construction or reconstruction. The standalone contract explicitly excludes persistence and dispatch guarding, so this remains an acknowledged integration blocker rather than an implementation defect.

- **SLOPPY — the test-module claim exceeds the evidence.** [test_qi_tuna_dispatch_clock.py:1](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) says the horizon “includes suspended time and rejects clock discontinuities.” The tests supply synthetic observations; they establish neither clock-source provenance nor short-suspend detection. “Compares supplied UTC and boot-clock observations” would match the tested mechanism.

- **SLOPPY — a test again calls identity validation restart detection.** [test_qi_tuna_dispatch_clock.py:102](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) proves that a deceptive string subclass cannot control comparison. The clock acquires no kernel boot identity, so “cannot hide a restart” overstates the observation.

- **SLOPPY — the equality test name claims two independently proven branches.** [test_qi_tuna_dispatch_clock.py:8](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) reaches equality on both limits, but the UTC side of the `or` short-circuits first. The elapsed-only case at line 58 separately covers elapsed equality. The first name should identify UTC equality, or the test should split the cases.

- **Important missing tests:**

  - The broad constructor test at [line 151](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) omits wrong `Observation` types, identity subclasses, invalid initial NaN/infinity/Boolean/oversized readings, and infinity/Boolean/oversized bounds.
  - The post-admission rollback test at [line 30](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) covers UTC rollback only. A symmetric boot-clock rollback test would kill a mutation that compares boot time with `_initial` instead of `_previous`.
  - The tolerance-rejection test does not verify that the rejection permanently latches the instance.
  - An isolated UTC-deadline equality case remains useful.

Fake-provider ordering, durable consumption, locking, retry enforcement, short-suspend detection, and restart persistence belong to the eventual adapter and fall outside this standalone review.

## Addressed defects

- **SOUND:** Exact `Observation` and built-in `str` validation at [lines 59–65](../../../scripts/qi_tuna_dispatch_clock.py) closes both string-subclass admission and comparison-exception latch escape.
- **SOUND:** Normal assignment and deletion are blocked at lines 37–41.
- **SOUND:** Oversized integers become controlled validation failures through lines 17–23.
- **SOUND:** Controlled validation, clock, and expiry failures latch through lines 69–76.
- **SOUND:** Admission updates `_previous` only after every predicate passes, at line 95.
- **SOUND:** Extreme finite arithmetic cannot admit through an `inf - inf` NaN comparison because the recomputed boot elapsed necessarily reaches the finite elapsed limit.
- **SOUND:** The renamed assignment test now limits its claim to normal assignment. The earlier suspend/restart test names were narrowed, although the new subclass test reintroduces “restart” language.

Direct `_check()`, explicit `__init__()` reinvocation, and `object.__setattr__()` can bypass state, but those paths violate the trusted-caller/private-interface boundary and are not findings under this contract.

## Exact staged identities

| Artifact | Git blob | SHA-256 |
|---|---|---|
| Script | `cbb97046ac3215343153571f2a9d796f44c9e257` | `7345578f3407dec019bfd4e76394188937c32926d0df5ccf2049fd2010b93c47` |
| Tests | `178b9f2cd41e1620a1c2b93c491405a7354d5e2d` | `8af6c5c4dc3aed7b74b00baeebb2fd789e14533fe8fb764253e03deb78c803cf` |
| Follow-up review | `3f20360d75b1849fc40ed6040831039532dd4059` | `786354cb3021f9153aefc29ed732adba70127eabbadb9d5139fca92acf953d98` |

## Preservation

`HEAD` remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`. Before-and-after observations recorded identical target index blob IDs and staged SHA-256 digests. The three target paths remained staged-only, their final unstaged diffs were empty, and both staged whitespace checks produced empty output.

I ran local read-only Git, text-search, and hashing commands. I ran no tests or repository code and performed no network, credential, provider, job, upload, draw, external-message, or repository-edit operation. Unrelated worktree and index surfaces were not remeasured and remain outside the preservation claim.
