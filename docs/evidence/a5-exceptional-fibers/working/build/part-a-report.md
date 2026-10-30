# Part A report: fiber input provenance and the second-prime harness

## Files

- `docs/evidence/a5-kernel-attachments/fiber_inputs.py` (new, worktree `a5-kernel-attachments`). Subcommands `emit` and `check`
  (`--prime`, `--root`, `--slug`, `--out`). Ruff format/check and mypy (via `ci/pinned_tool.py`) pass.
- `docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py` (producer, untracked in the worktree), minimal change:
  `prime` parameter on `_ring_lines`, `_local_germ_lines`, `_phase_one_script`; `embedding` flag on `_phase_one_script`
  (False stops after the presolved J and G, skipping the lift); `timeout_seconds` on `_run_singular`. Defaults reproduce the
  old scripts byte for byte (checked on B9->N+ at root None and 10754 against a copy of the file before the edit).
  `nakayama_rees_fibers.py` (tracked) is unchanged.
- Outputs: `build/inputs/p32009-r10754/` (regeneration plus `receipt.json` with comparisons), `p32009-r21255/`,
  `p32029-r9115/` (nine headers and a receipt each), `build/inputs/survivors/` (cached Q(i) survivor selections).
  Logs: `build/logs/part-a-*.log`. Receipts hold tool versions (Singular 4.4.1, python-flint 0.9.0), the producer sha256 and
  header sha256; paths are repo-relative.

## Provenance map (input -> emitting path)

All headers are the producer's phase-one output (`_local_germ_lines` -> Nakayama selection by coefficient rank ->
`elimpart` -> `ReducedJ`, `ReducedG`), rendered as `ring r=p,(remaining t vars),dp; number I=r; ideal J; ideal G`.

| Input | Incidence | Computed file | Emitting path | Candidates -> selected | Vars |
| --- | --- | --- | --- | --- | --- |
| X+ | X+->N+ | kaggle-pack-a/xp_np/input.sing | nullity16 phase one, survivor-reduced | 69 -> 15 | 7 |
| X- | X-->N- | kaggle-pack-a/xm_nm/input.sing | same | 69 -> 15 | 7 |
| Iso | Iso->N+ (file matches N+) | inputs/iso_K2.sing | same, basepoint-selected 17 | 17 -> 17 | 6 |
| E8bar N+ / N- | E8bar->N+/N- | inputs/e8_np_fiber.sing, e8_nm_fiber.sing | same, survivor-reduced | 103 -> 21 | 9 |
| W8 N- / N+ | W8->N-/N+ | inputs/w8_nm_fiber.sing, w8_np_fiber.sing | same, survivor-reduced | 124 -> 24 | 7 |
| E8bar VB | E8bar->VB | runs/e8vb_b/input.sing | nakayama Schur coordinates (21) fed to the nullity16 phase-one script | 21 -> 10 | 8 |

E8bar->VB has no row in the nullity-16 record and is excluded from `nakayama-rees-fibers-result.json` (`excluded_blocked_incidence`).
`nullity16_basepoints._schur_coordinates` asserts the boundary C_z rank of N+/N- and fails on VB ("boundary C_z rank changed"), so
the VB coordinates come from `nakayama_rees_fibers.resolved._schur_polynomials`. The committed nakayama phase-one script
(sequential `std(NormalForms)` selection plus lift) ran past 900 s here, so the VB route uses the coefficient-rank selection
with no lift (0.3 s). The committed nullity-16 record's blocked rows timed out in the embedding/lift stage that this
route skips; with it off every row emits in under 10 s.

## Falsifier at p=32009, I=10754 (log: build/logs/part-a-check-all.log)

| Input | Result |
| --- | --- |
| X+ N+ | identical (J and G text) |
| X- N- | identical |
| E8bar N+, N- | identical |
| W8 N-, N+ | identical |
| Iso N+ | same J ideal (reduced std bases equal), G identical polynomials in identical order; text differs only in term order (the computed file prints in the ds ring, the header in dp) |
| Iso N- | same J ideal; G equal up to order and sign (7 of 17 equal in place, 17 of 17 up to sign). Not the computed file: it is the N+ input |
| E8bar VB | same J ideal; same selected coordinates [7,8,10,11,12,14,15,17,18,21]; G differs termwise from the computed file (the file holds unreduced coordinates with the `+((10754))*(0)` artifact, the header holds them reduced mod J), equal termwise (up to sign) modulo J for 10 of 10 and equal linear span mod J (rank 10/10/10) |

No input is "different". The E8bar VB computation read generators that differ from the regenerated ones by elements of J, so its
results (ideals, Hilbert data) agree with the producer's presentation; its file bytes are not reproducible from the producer.

## Second embedding and second prime

- r = 32009 - 10754 = 21255 at p=32009: nine headers in `p32009-r21255/`.
- p = 32029 (= 1 mod 4, prime), r = 9115 (computed with pow(g,(p-1)/4,p), r^2 = -1 verified): nine headers in `p32029-r9115/`.
- Selected counts agree with p=32009 for all nine (receipts list selected indices per input). Not compared against any
  computed file (none exists at these characteristics).

## Commands

    export PYTHON=<ci venv python> GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=1
    systemd-run --user --scope -p MemoryMax=3G -p MemorySwapMax=0 timeout -k 10 880 \
      "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_inputs.py check            # p=32009, r=10754
    ... fiber_inputs.py emit --prime 32009 --root 21255
    ... fiber_inputs.py emit --prime 32029 --root 9115

## Open limits

- `GOROROBA_WORKERS=1` keeps items serial in-process under the one-job rule; unset it for a pooled run.
- `nullity16_rees_fibers.py` is untracked and its committed record `nullity16-rees-fibers-result.json` still says prime 32003;
  the record and the producer digest need regeneration by the orchestrator.
- The VB route shims a `RowTask` for the nullity16 script (expected-germ fields zeroed, unused by the script).
- Survivor selections for X, E8bar, W8 depend on the Q(i) survivor stage; they are cached per incidence and shared across primes.
- Singular outputs of a polynomial are parsed from `RESULT` lines; line wrapping in Singular output was not observed.
