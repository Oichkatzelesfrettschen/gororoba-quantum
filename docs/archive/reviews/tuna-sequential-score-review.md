No FATAL defect appears in the scoring core. The core earns a bounded PASS against the two designs, but the tests contain SERIOUS masking gaps and should not serve as the sole verification surface.

## Findings

**SERIOUS — the q6 decoder test masks a wrong terminal-bit offset.**

[test_qi_tuna_sequential_score.py:94](../../../tests/scripts/test_qi_tuna_sequential_score.py) puts ones at both baseline-early offset 0 and terminal-q6 offset 13. Changing the implementation from `shot[13]` to `shot[0]` passed all eight tests. A decoder reading bit 19 instead of terminal q6 bit 6 would therefore receive a false pass.

Use isolated terminal and early patterns: offset 13 alone, offset 0 alone, and offset 1 alone, under both arms.

**SERIOUS — asymmetric scoring coverage permits central contract violations.**

Each of these deterministic in-memory mutations passed all eight tests:

- Treating baseline as rotated by replacing the assignment at [qi_tuna_sequential_score.py:72](../../../scripts/qi_tuna_sequential_score.py) with `assignment = 1`.
- Checking only terminal-q6 when deciding the shared stop at [qi_tuna_sequential_score.py:89](../../../scripts/qi_tuna_sequential_score.py).
- Returning a permanently neutral `terminal_negative` process.
- Accepting only `unavailable` while rejecting the specified `confirmed_failure` and `partial` neutral classifications.

The tests need non-neutral baseline cases, explicit values for all four processes, separate early-only and terminal-only crossings, and one test for each neutral classification.

**SLOPPY — the review binding omits one governing design.**

The [binding list](tuna-sequential-score-review.json) correctly binds its three entries, but it omits [tuna-sequential-destination-uncertainty.md](../../../docs/design/tuna-sequential-destination-uncertainty.md), which supplies the conditional statistical assumptions. I reviewed its staged and working bytes at:

`a94cbad3c6d0a007296ec5d5b36d52b73e5e31e710d4276c26c76d4c008e75b3`

A review receipt based only on the current list would not detect later changes to those assumptions.

## SHA-256 verification

| Artifact | Binding | Staged bytes | Working bytes |
|---|---|---|---|
| Scoring core | `d344f69d…16611b` | match | match |
| Tests | `24daee3a…add10` | match | match |
| Sequential evidence case | `749cd863…6e72f5` | match | match |
| Sequential uncertainty design | absent | `a94cbad3…08e75b3` | match |

`sha256sum -c` reported all three listed paths `OK`.

## Bounded PASS evidence

The implementation correctly provides:

- `X=2Z(Y-1/2)`, with rotated `Z=+1` and baseline `Z=-1`.
- Independent positive and negative processes for early-q6 and terminal-q6.
- The exact `9/10` full-stake plus `1/10` half-stake mixture.
- Exact `Fraction` arithmetic and `>= 400` crossings.
- Initial value and running maximum of one.
- Persistent first crossings and maxima after later adverse observations.
- Contiguous one-based slots, a 24-slot ceiling, shared stopping only after both observables cross, and rejection of observations after a stop.
- Neutral factors of one followed by stopping for all three neutral classifications.
- Width-20 binary-shot validation; baseline early offset 0, rotated early offset 1, and terminal-q6 offset 13.

Independent calculations confirmed:

- For `X=1`, one slot gives `E+=39/20` and `E-=1/20`.
- Nine `X=1` observations give
  `E+=(9/10)2^9+(1/10)(3/2)^9=2378979/5120`, first crossing at slot 9.
- A following `X=-1` zeroes the full positive product while leaving
  `E+=19683/10240`; another `X=1` gives `59049/20480`. The maximum remains `2378979/5120`.
- Adjacent ninth-slot counts straddle 400 exactly:
  - count 3524: `400 - 166639/2621440`;
  - count 3525: `400 + 519653/10485760`.
- An early-only crossing at slot 9 continues. A terminal crossing at slot 18 then produces `both_observables_crossed`.
- Negative-direction scoring is symmetric and crosses at slot 9 under nine `X=-1` observations.
- All 8,194 arm/count combinations for one attainable response count matched an independent formula.
- All 40 isolated bit-position/arm checks matched the documented decoder.
- A separately coded prefix-recomputing oracle matched 6,175 sequences of lengths zero through three over both arms and counts `{0, 2048, 4096}`.
- Twenty-five malformed scoring classes and eleven malformed decoding classes were rejected.

Ruff lint, Ruff formatting, mypy, `git diff --check`, and all eight pytest tests passed.

## Conditional statistical validity

The derivation in the designs is correct under its stated assumptions. Conditional fairness gives

`E[X[t] | F[t-1]] = tau[t]`.

For stake `lambda` equal to one or one-half,

`E[1 + lambda*d*X[t] | F[t-1]] = 1 + lambda*d*tau[t] <= 1`

under the directional null. Each factor is nonnegative, so both products and their initial-value-one mixture are nonnegative supermartingales. Ville's inequality gives `1/400=0.0025` per process, and the four-process union bound gives `0.01` without response independence.

The core establishes none of the assumptions needed to apply that result. Source/job identity, conditional half-probability assignment, independence from both augmented potential outcomes, concealment, consistency, observation-boundary timing, cost, admission, and inference eligibility remain open requirements. Neutral scoring is valid only after both counterfactual augmented outcomes have been defined prospectively at the same boundary. If the true propensity differs from one-half, the documented bias remains uncorrected.

The core is sound within its explicitly narrow preclassified-input contract. The test masking findings and incomplete design binding should be resolved before relying on the local suite as evidence. This review neither admits a campaign nor reviews an eventual runner.
