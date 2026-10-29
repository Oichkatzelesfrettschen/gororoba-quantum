The illustration’s algebra, attainable counts, first crossing, and stopping behavior are correct. I found zero FATAL or SERIOUS defects, two SLOPPY claim/coverage defects, and several SOUND boundaries.

## Findings

1. **SLOPPY — “favorable” and “does not estimate power” blur the actual statistical meaning.**

   [The illustration](../../../docs/design/tuna-destination-sequential-evidence-case.md) specifies a degenerate point alternative under which `X[t]=d` for every assignment. Conditional on complete jobs and valid randomization, it therefore gives exact model-specific rejection probabilities: zero by position 24 for `d=0.25`, and one by position 16 for `d=0.5`. That is conditional power for this particular zero-variance alternative, although it is neither empirical Tuna-17 power nor a forecast.

   “Favorable” supplies no general power ordering. At the same contrast `d=0.25`, potential fractions `Y(+)=1` and `Y(-)=3/4` produce scores `1` and `-1/2`; nine initial rotated assignments cross 400 with probability `2^-9` under fair independent assignment, while the centered example never crosses by 24. Other alternatives can reduce power relative to the centered case.

   The paragraph should call this a “centered, zero-score-variance point alternative,” describe its conditional crossing probability, and state that it supplies neither an upper nor lower power bound for other alternatives with the same contrast. It should also say that 4096 shots provide outcome granularity here, not 4096 independent interventions; the method permits arbitrary within-job shot dependence.

2. **SLOPPY — the cited test checks two endpoints, not “both trajectories.”**

   [The test](../../../tests/scripts/test_qi_tuna_sequential_score.py) evaluates one completed sequence for each `d`, then checks only the final `early_positive` value and the overall stop reason. It does not directly assert:

   - every prefix value;
   - the documented position-15 value;
   - `first_crossing == 16`;
   - the terminal-positive trajectory;
   - the exact integrality of `4096 * fraction`.

   The current implementation still produces the claimed trajectory, but the documentation overstates what the regression test freezes. A complete trajectory test should compare every prefix, both observables, exact counts, and the recorded first crossing.

## Confirmed sound

- The contrast is interpreted correctly: `(1+d)/2 - (1-d)/2 = d`, and [the scorer](../../../scripts/qi_tuna_sequential_score.py) gives `X[t]=d` for either assignment.

- The shot counts are exactly attainable:

  - `d=1/4`: rotated `2560/4096`, baseline `1536/4096`.
  - `d=1/2`: rotated `3072/4096`, baseline `1024/4096`.

- The numerical claims are correct:

  - `d=1/4`, position 24: `192.271533266502… < 400`.
  - `d=1/2`, position 15: `396.946672285814… < 400`.
  - `d=1/2`, position 16: `594.709465692961… > 400`.

  Because the positive trajectory is strictly increasing, position 16 is the first crossing for `d=1/2`; `d=1/4` cannot have crossed before position 24.

- The stopping results match the scorer: `slot_limit` at 24 for `d=1/4`, and `both_observables_crossed` at 16 for `d=1/2`.

- The deterministic alternating assignments in the test are legitimate as an arithmetic fixture because the score is assignment-invariant in this example. They do not test the inferential randomization law. [The uncertainty design](../../../docs/design/tuna-sequential-destination-uncertainty.md) and scorer docstring correctly reserve conditional fairness, concealment, potential-outcome consistency, and source association to other evidence.

- The inference boundaries are accurate: a crossing challenges the uniform pathwise directional conditional-mean null; it does not establish persistence, an average causal effect, equivalence, mechanism, or physical attribution. A non-crossing remains inconclusive.

## Working-tree provenance

The final stable snapshot used these SHA-256 values:

```text
8017a82059a4480394cef765ac875aa65fd95d7f5df1e54c960c1b5dbc29fecc  docs/design/tuna-destination-sequential-evidence-case.md
c386f254058dee4a0e799dc92daba65549d18cf7e7048b36c3c128e935ab08b1  tests/scripts/test_qi_tuna_sequential_score.py
d344f69db36dcc79a6ce605686aa1dfcc488fa034ad09fdfab5c7d7f9d16611b  scripts/qi_tuna_sequential_score.py
a94cbad3c6d0a007296ec5d5b36d52b73e5e31e710d4276c26c76d4c008e75b3  docs/design/tuna-sequential-destination-uncertainty.md
```

The design file initially hashed as `60338bf2dfbd8262a3424d8fb93a00dde4c14775967810640a03e35360b3e7ee`, then received a concurrent unrelated retention-review paragraph and changed to `8017a820…`. I reread the latest file; the sensitivity paragraph itself remained unchanged. HEAD remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

I issued only file reads/searches, Git metadata reads, SHA-256 calculations, and read-only arithmetic. I ran zero tests or linters and initiated zero credentials, network, provider, job, upload, random-draw, messaging, or repository-edit operations.
