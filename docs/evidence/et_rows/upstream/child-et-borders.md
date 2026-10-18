# Add signed child-border ET certificates alongside same-level Skyboxes

Canonical source inspected at `2b72e552b95f7fe529a5abb45049f6d3e47cdd97`.

Same-level zero padding differs from actual next-level label-line cells. The child bordered box uses shifted labels V1(c)=G_old xor c and boundaries G_old,G_old xor S.

Source: https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/2b72e552b95f7fe529a5abb45049f6d3e47cdd97/crates/algebra_experimental/src/emanation/skybox.rs

Required work and acceptance:

- [ ] Provide explicit primary, shifted and boundary maps.
- [ ] Check every signed interior and border entry.
- [ ] Retain S15 counts 72+56=128, 456+120=576, 2184+248=2432.
- [ ] Keep box and whole-table denominators separate.
- [ ] Test parent(1,6)=-7, child(17,22)=-7, mixed child(1,22)=-23 for D32 to D64.

Quantum dependency: bounded ET-row integration in gororoba-quantum. Existing exact finite fixtures support implementation; this issue tracks the upstream semantic or formal bridge. Hardware submission remains separately approval-gated.
