# Separate fixed-strut and moving-strut ET growth contracts

Canonical source inspected at `2b72e552b95f7fe529a5abb45049f6d3e47cdd97`.

Fixed S15 and moving S=G/2+1 agree at D32 and diverge afterwards. Finite census agreement alone does not prove an all-order recurrence.

Source: https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/2b72e552b95f7fe529a5abb45049f6d3e47cdd97/crates/algebra_experimental/src/emanation/balloon_ride.rs

Required work and acceptance:

- [ ] Record fixed counts 72,456,2184,9480,39432 through D512.
- [ ] Record moving counts 72,168,360,744,1512 over the same dimensions.
- [ ] Specify minimum admissible level and denominator (G-2)(G-4).
- [ ] Bind asymptotic claims to proved recurrences or explicitly bounded evidence.

Quantum dependency: bounded ET-row integration in gororoba-quantum. Existing exact finite fixtures support implementation; this issue tracks the upstream semantic or formal bridge. Hardware submission remains separately approval-gated.
