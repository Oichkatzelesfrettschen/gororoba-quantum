# Part A: input provenance and the second-prime harness

Goal: a module `fiber_inputs.py` that emits, for a given incidence row and a split prime p = 1 mod 4 with a chosen
square root r of -1, the Singular header (ring over F_p with t variables in dp, `number I=r;`, `ideal J=...;`,
`ideal G=...;`) for the fiber computations, from the characteristic-zero Q(i) producer data, never by editing a
specialized file.
1. Map each of the six computed inputs to the code path that emitted it: X+ and X- (docs/local/a5-failed-runs/
   kaggle-pack-a/xp_np, xm_nm/input.sing), Iso (inputs/iso_K2.sing), E8-bar->N+ (inputs/e8_np_fiber.sing),
   E8-bar->N- (inputs/e8_nm_fiber.sing), W8->N- and W8->N+ (inputs/w8_nm_fiber.sing, w8_np_fiber.sing), E8-bar->VB
   (runs/e8vb_b/input.sing, from a hand-edited scratchpad script whose G0 carries a `+((10754))*(0)` artifact). The
   chain ran producer phase-one emit scripts (session scratchpad TMP/PROJECT/
   SESSION/scratchpad/probe/*_emit.sing, *_phase1*.sing) then probe/fiber_degrees.py.
   Read those as leads; the authority is nullity16_rees_fibers.py (`_ring_lines`, `_local_germ_lines`,
   `_phase_one_script`, MODULAR_PRIME, MODULAR_I_ROOTS) and its record nullity16-rees-fibers-result.json.
2. Implement the emitter by reusing the producer's functions (import them; parameterize prime and root instead of
   copying code; if a constant blocks that, propose the minimal producer change and make it).
3. Falsifier: regenerate every input at p=32009, r=10754 and compare with the computed file after normalizing
   (reduce G and J to a canonical form: J by its reduced standard basis; G compared as generator lists up to order
   and sign, and if needed by equal linear span mod J). Report each input as identical, equal-up-to-order/sign, or
   different, with the difference. A difference means results computed on that file are not reproducible: say so.
4. Exercise the second embedding r = 32009-10754 and one more split prime (choose p = 1 mod 4 near 32000, compute r
   with pow), and emit all six headers there under docs/local/a5-failed-runs/build/inputs/p<prime>-r<root>/.
5. Do not start long computations. Small Singular calls for emitting and comparing only (3G, 15 min each).
