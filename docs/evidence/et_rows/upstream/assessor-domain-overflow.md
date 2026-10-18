# Distinguish assessor reclassification from embedded zero-product inheritance

Canonical source inspected at `2b72e552b95f7fe529a5abb45049f6d3e47cdd97`.

carry_bit_overflow_cells compares parent and child assessors whose high indices inhabit different ranges. A lost assessor category does not establish loss of an embedded zero product.

Source: https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/2b72e552b95f7fe529a5abb45049f6d3e47cdd97/crates/algebra_experimental/src/emanation/table_builder.rs

Required work and acceptance:

- [ ] Define the intended comparison domain and rename/document structural reclassification.
- [ ] Compare embedded vectors on unchanged basis labels for multiplication inheritance.
- [ ] Retain (e2+e11)(e4-e13)=0 at D16, D32 and D64.
- [ ] Order witnesses deterministically and test intended lost/gained classifications.

Quantum dependency: bounded ET-row integration in gororoba-quantum. Existing exact finite fixtures support implementation; this issue tracks the upstream semantic or formal bridge. Hardware submission remains separately approval-gated.
