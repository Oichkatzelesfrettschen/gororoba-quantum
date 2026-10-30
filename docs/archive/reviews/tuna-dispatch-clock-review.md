Artifact: a Python in-memory dispatch-clock predicate and its pytest suite. The review covers the complete staged blobs and the staged design. I performed static analysis only; I ran no tests or provider operations.

## Staged-byte identity

| File | Git blob | SHA-256 |
|---|---|---|
| `scripts/qi_tuna_dispatch_clock.py` | `a3447d0e06affc0f6bc840a8d0b4fbead45474ec` | `fc38e8c443c966e91074285eb8f9bc108b7fdb7a6b02ee61f1879a26321fe962` |
| `tests/scripts/test_qi_tuna_dispatch_clock.py` | `af5ed9d3c3e5afd1946f8a70e10176e3d930519a` | `9313e692b4bf69ee2646a66f9e42a3999166de60e729341134e5743df54266fe` |

The working-tree copies differ from these staged blobs, so every implementation and test line number below refers to the Git-index version obtained with `git show :<path>`.

## Findings

### SERIOUS — Callers can rewrite the approved horizon and clear refusal

Demonstrated bug.

The constructor publishes every security-relevant field as a writable public attribute: `initial`, `previous`, `utc_deadline`, `elapsed_limit`, `tolerance`, and `refused` at staged implementation lines 27–32. `check()` then trusts those mutable fields at lines 45–67.

A static counterexample is sufficient:

```python
clock = DispatchClock(Observation("boot-a", 1000.0, 100.0), 1010.0, 20.0, 1.0)
clock.utc_deadline = 1020.0
clock.check(Observation("boot-a", 1011.0, 111.0))
```

The original UTC horizon would reject `1011.0`; the modified object admits it because the elapsed bound remains 20 seconds. Likewise, assigning `clock.refused = False` defeats the supposedly permanent refusal latch.

The design excludes a malicious same-user process, but public mutation also exposes ordinary integration mistakes. The adapter must own private immutable configuration, keep evolving state inaccessible to callers, and test that configuration and refusal cannot be reassigned through the supported API.

### SERIOUS — A large integer escapes the refusal latch

Demonstrated bug.

Staged implementation lines 38–40 accept exact Python `int` objects and pass them to `math.isfinite()`. Python must convert an integer such as `10**400` to a floating-point value for that call, which raises `OverflowError`. `check()` catches only `ValueError` and `TimeoutError at lines 47–51.

Consequently:

1. A malformed observation raises `OverflowError`.
2. `refused` remains false.
3. A later valid observation can be admitted under the same object.

That contradicts the staged design’s statement that malformed numbers latch refusal for the attempt at [tuna-qx-exact-dispatch-guard.md:135](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

Validation should translate every numeric conversion or arithmetic failure into the contract’s controlled refusal exception before returning to the caller. A regression test should submit oversized integers in both clock fields and verify both exception normalization and permanent refusal.

### SERIOUS INTEGRATION BLOCKER — Short suspension remains indistinguishable from awake time

Demonstrated false admission against the full dispatch boundary; limitation rather than a standalone-contract bug.

The full design says a suspend makes the attempt inadmissible at [tuna-qx-exact-dispatch-guard.md:66](../../../docs/design/tuna-qx-exact-dispatch-guard.md). The staged observation contains only UTC and suspend-aware boot time. Both clocks advance during suspension.

For an initial observation `(1000, 100)`, a five-second suspend can produce `(1005, 105)`. With a 20-second horizon, the implementation sees equal five-second deltas and admits the observation. The staged test at lines 6–11 proves only that a suspension which exhausts the entire horizon expires it.

The design correctly limits the standalone component at [tuna-qx-exact-dispatch-guard.md:135](../../../docs/design/tuna-qx-exact-dispatch-guard.md), so the missing suspend detector is not an undisclosed standalone defect. The final adapter nevertheless needs an additional reviewed suspend observation, or the design must explicitly change the policy to “suspend counts toward elapsed time” instead of “suspend refuses.”

### SERIOUS INTEGRATION BLOCKER — Restart discards the attempt latch and time history

Limitation of the in-memory component.

All attempt state exists only inside one `DispatchClock` instance. A fresh process can construct a new instance and forget:

- a prior refusal;
- the original `previous` observation;
- the original boot identity;
- any earlier backward or disagreeing reading.

The test named `test_clock_rejects_restart_and_backward_or_disagreeing_clocks` at staged test lines 14–25 checks a changed boot ID against an existing instance. It does not test process reconstruction or same-boot restart.

The full design consumes approval after marker creation and treats a crash as spent or ambiguous at [tuna-qx-exact-dispatch-guard.md:87](../../../docs/design/tuna-qx-exact-dispatch-guard.md). The adapter must therefore retain the original initiation observation and attempt disposition durably, and refuse reconstruction after a crash or latched failure.

### LIMITATION — Concurrent checks are not linearizable

Serious if the future adapter shares one clock across threads; otherwise a documented single-owner constraint can contain it.

`check()` reads `refused` at staged line 45, performs several operations, and writes refusal or `previous` later at lines 50 and 67 without synchronization. Possible interleavings include:

- One call passes the `refused` check, another call latches refusal, and the first call subsequently returns successfully.
- Two successful calls compare against the same old `previous`, then store observations in reverse chronological order.

The component makes no thread-safety claim. The final adapter must serialize every clock check or make the transition atomic. Tests should either exercise concurrent calls or enforce/document exclusive ownership.

## Missing tests

The staged suite usefully covers exact expiry, changed boot ID, backwards readings, one disagreement direction, handled-error latching, and an elapsed-only deadline. Material omissions are:

- Oversized integers and refusal after `OverflowError`.
- Mutation of every public configuration/state field.
- UTC-only expiry while the elapsed limit remains open.
- Exact-tolerance acceptance and just-over-tolerance rejection in both disagreement directions.
- Invalid initial observations and invalid constructor bounds.
- Timeout-based refusal persistence, not only `ValueError` persistence.
- Same-boot process reconstruction and reconstruction after a latched refusal.
- A short suspension under the design’s full any-suspend refusal rule.
- Concurrent calls or an enforced single-owner contract.

## Integration prerequisites

The staged tree contains no production reference to `DispatchClock`; only the design and its tests import or name it.

The existing deadline-aware helper already supplies a callback after fresh backend and queue reads at [qi_platform_submission_deadline.py:163](../../../scripts/qi_platform_submission_deadline.py), but its client enforces only a monotonic deadline at [qi_platform_submission_deadline.py:34](../../../scripts/qi_platform_submission_deadline.py). A final adapter still needs to:

- Bind the initial observation, UTC deadline, elapsed limit, tolerance, packet digest, and approval identity.
- Acquire and validate genuine clock and boot observations.
- Check the clock during bounded, nonblocking lock acquisition.
- Invoke the clock before every request and authentication retry, not only once in the admission callback.
- Persist consumption/refusal before resource creation and fail closed after restart.
- Serialize clock transitions.
- Exercise the fake-provider ordering, ambiguity, fault-injection, and duplicate-consumption cases required at [tuna-qx-exact-dispatch-guard.md:144](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

## Verdict

The cumulative two-clock comparison, strict deadline equality, boot-ID comparison, and handled-error latch form a reasonable small offline predicate. The current staged implementation is not yet safe as an attempt guard because its policy state is writable and one valid input type can escape permanent refusal. Suspend detection, restart durability, concurrency control, and per-request enforcement remain explicit integration work rather than hidden standalone capabilities.

No tests, network calls, provider calls, credential reads, resource requests, seed draws, messages, or repository edits occurred. The target staged blob IDs and `HEAD` (`55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`) remained identical across the review. The complete index-entry digest changed from `910cbfe0...fccba` to `60a5e2a7...5a737` during the review window, so the observations establish preservation of the three target staged blobs, but cannot establish that the surrounding staged set remained unchanged by other activity.
