The writable-bound and oversized-integer fixes work within the documented narrow boundary, but one reachable incorrect admission remains. The standalone predicate is not ready to support dispatch admission.

## Findings

- **SERIOUS — a `str` subclass can defeat boot-identity validation or escape refusal latching.**
  [qi_tuna_dispatch_clock.py:58](../../../scripts/qi_tuna_dispatch_clock.py) accepts every `str` subclass. The comparison at [line 77](../../../scripts/qi_tuna_dispatch_clock.py) then invokes the subclass’s overridable `__ne__`. A subclass can report unequal boot identifiers as equal, causing incorrect admission, or raise `TypeError`, which [lines 69–73](../../../scripts/qi_tuna_dispatch_clock.py) leave unlatched. Require `type(observation.boot_id) is str` or canonicalize to a trusted built-in string before storage and comparison. Add both deceptive-comparison and exception-raising regression cases.

- **SERIOUS INTEGRATION BLOCKER — constructor rejection cannot latch an attempt.**
  Invalid initial observations and bounds fail at [lines 40–46](../../../scripts/qi_tuna_dispatch_clock.py), before an object or latch exists. A caller can construct another clock immediately. The eventual adapter must durably mark failed initiation validation if the attempt begins before successful construction.

- **SERIOUS PROVENANCE LIMIT — the archived review covers older bytes.**
  [tuna-dispatch-clock-review.md:7](../../../docs/archive/reviews/tuna-dispatch-clock-review.md) records script blob `a3447d0…` and test blob `af5ed9d…`. The current staged blobs are `a3ba32a…` and `c259552…`. The archived report remains valid historical evidence, but its verdict cannot attest the present fixes.

- **SLOPPY — “read-only” is broader than the mechanism.**
  Normal assignment is blocked, matching the explicit design boundary. However, `__delattr__` remains available: deleting a slot succeeds and later produces an unlatched `AttributeError`. `object.__setattr__` also bypasses the guard, although the design explicitly excludes Python introspection and hostile same-process callers. The test name “callers cannot extend … or clear refusal” should say “normal assignment,” and deletion should either be blocked or documented as fail-closed behavior.

- **SLOPPY — test names claim more than their observations establish.**
  [test line 8](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) proves exact horizon expiry, not suspend detection. [Line 16](../../../tests/scripts/test_qi_tuna_dispatch_clock.py) proves changed boot-identity rejection, not same-boot process reconstruction. The design correctly admits both limitations.

Material test gaps include:

- The `str`-subclass admission and exception cases.
- Invalid initial observations and constructor bounds.
- Oversized and non-finite `boot_seconds`, not only `utc_seconds`.
- Exact-tolerance acceptance and just-over-tolerance rejection in both directions.
- Slot deletion and its refusal behavior.
- The fake-provider ordering, retry, lock, durable-consumption, ambiguity, and fault-injection tests required by the full design.

## Verified fixes

- **SOUND:** normal attribute assignment cannot rewrite bounds or set `_refused=False`.
- **SOUND:** oversized integers become `ValueError` and latch refusal.
- **SOUND:** `None`, NaN, infinity, and boolean observations reach controlled rejection paths.
- **SOUND:** UTC-only and elapsed-only expiry branches receive coverage.
- **SOUND within exact built-in numeric inputs:** static inspection found no remaining arithmetic exception after oversized-integer normalization.

The standalone class still has no production caller. It acquires no clocks, detects no short suspension, retains no restart history, supplies no synchronization, guards no provider request or retry, and attests none of its caller-supplied observations. Those are explicit integration blockers, not capabilities earned by these unit tests.

## Exact staged identities

| Artifact | Git blob | SHA-256 |
|---|---|---|
| Script | `a3ba32aa01ca93332893abf6b065e625b81e85e2` | `720cf830ce3524db2b9bee540ca0ef53f8aee1b1d1a7e0a8949be5d97c2ecf17` |
| Tests | `c259552f9d9ea599cadf6a13505083f640098e20` | `0efb0483dd750fda934055549a754a02d8a4412fc89564a7eaf28715cd92b926` |
| Archived review | `12dad5569912eb6a891bfbff28f0620e0cf2f706` | `3cfc492163cc4eeae892862c6cdf905096daf0985fe84af1ee1b899af4562cb1` |

`HEAD` remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

## Preservation and trust limits

The before-and-after observations recorded:

- Identical target staged blob IDs.
- Identical HEAD and local-ref digest `80fc94e2d0fbd665281eb1df99174d0323e40385`.
- An empty unstaged tracked diff at both observations.
- Changed complete-index, cached-diff, and porcelain-status digests during the review window.

Therefore, the measurements establish preservation of the three named staged artifacts, HEAD, refs, and the empty unstaged tracked diff. They do not establish preservation of unrelated staged entries; another shared-worktree activity changed that surrounding staged set during the review.

I issued only local read-only inspection commands. I ran no tests or repository code and performed no network, credential, provider, job, upload, draw, message, or repository-edit operation.
