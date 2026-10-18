# Verify shifted ET signs independently of occupancy

Canonical source inspected at `2b72e552b95f7fe529a5abb45049f6d3e47cdd97`.

The helper promises signed primary and shifted copies, but its shifted loop checks occupancy and lacks a shifted-value result flag.

Source: https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/2b72e552b95f7fe529a5abb45049f6d3e47cdd97/crates/algebra_experimental/src/emanation/theorem11.rs

Required work and acceptance:

- [ ] Add a shifted signed-value result and compare occupied values.
- [ ] Check blank/occupied structure separately.
- [ ] Mutate one shifted sign while retaining occupancy; the signed check must fail.
- [ ] Retain the checked dimensions and source identities.

Quantum dependency: bounded ET-row integration in gororoba-quantum. Existing exact finite fixtures support implementation; this issue tracks the upstream semantic or formal bridge. Hardware submission remains separately approval-gated.
