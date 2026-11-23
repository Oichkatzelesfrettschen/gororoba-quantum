# Modular Rees fiber certificates of E8-bar on the open cells, and the second-host replay of the full runs

This directory retains the Singular 4.4.1 runs that close ledger rows A5-576 and A5-578 (rows A5-587 to A5-590 state
the results). The scripts are the v2 E8-bar scripts of `../e8-rees-fibers-v2-p32009` with the zero-generator guard of
`../e8-rees-fibers-v3-p32009`, the prime and the root of -1 replaced (`render_cells.py`). A cell is a sign (N- or N+),
a prime p and a root r of -1 modulo p; the retained v2 runs cover (32009, 10754) only.

## Result

| Cell | Quotient colon, cloud VM (`NAME.v3-u-full`) | Modulo colon, Arm host (`modulo-colon/NAME.v4m-u-full`) |
|---|---|---|
| N- (32009, 21255) | 19 h 20 min 59 s, 555 MB | 7 h 21 min 57 s, 705 MB |
| N+ (32009, 21255) | 17 h 10 min 5 s, 527 MB | 5 h 50 min 8 s, 641 MB |
| N- (32029, 9115) | 19 h 25 min 24 s, 555 MB | resumed run: colon 4 h 42 min from the first-stage basis, fiber stage 31 s |
| N+ (32029, 9115) | 17 h 24 min 20 s, 527 MB | 5 h 50 min 8 s, 641 MB |
| N- (32029, 22914) | 19 h 10 min 48 s, 555 MB | 6 h 53 min 48 s, 702 MB |
| N+ (32029, 22914) | 17 h 12 min 15 s, 526 MB | 5 h 50 min 38 s, 641 MB |

- Every run prints `FIBER bound 0 minimal generators 148 dim 5 mult 11`, 148 generator degrees equal to 2,
  `FIBER outside_K 0 K_outside_fiber 0`, the Hilbert numerator of the retained (32009, 10754) runs and `EXIT 0`, with
  the certificate lines `CERT unit_identity_bad 0 all_positive_degree 1`, `CERT pivot_nonzerodivisor_mod_J 1`,
  `CERT satstd_isSB 1` and `CERT colon_equal_after_iterations 1`, and no `CERT FAIL` line. The prediction recorded in
  A5-457 and A5-576 (148 minimal generators of degree 2, dimension 5, multiplicity 11, L = K) holds on all six cells.
- The times are wall times of one process. Each cloud VM (4 hardware threads on 2 cores) ran four processes at once,
  and the same-bytes replays below reach the end 1.42 and 1.54 times later than the retained runs, which shared their
  VM with two short jobs; the Arm host ran four processes on four cores. The two columns therefore differ by host,
  by load and by method. The same-host comparison of one colon call is 578 s against 239 s on the bounded cell
  (`modulo-colon/y2-base.log`, `modulo-colon/y2-modstd.log`).
- Relation lines of sign pairs: the 148 `REL` lines of N- at root -r equal those of N+ at root r at both primes (four
  pairs, the retained (32009, 10754) logs included), so on these eight cells the quadric ideal K depends on the
  product of sign and root. The runs of a pair are distinct computations: the Rees-stage basis has 5955 elements
  for every N+ run and 6139 for every N- run.

## Modulo colon

The colon step of the v3 script is `QU=quotient(HS,ideal(u))` inside a loop that ends when QU reduces to zero modulo
HS. The `v4m` scripts replace that one call by `module MQ=modulo(ideal(u),HS); QU=ideal(matrix(MQ)); kill MQ;`, which
computes the same ideal HS : u as the kernel of multiplication by u on R/HS. The loop, its end test and every later
line are unchanged.

- Equality on recorded digests: for the five cells with both full runs, the first-stage basis file and the saturated basis
  file of the modulo run have the sha256 of the files of the quotient run (`bases.sha256`, `modulo-colon/bases.sha256`),
  across the two architectures (x86-64 and aarch64 builds of Singular 4.4.1). The saturated file is written after
  the colon loop and is the evidence for the colon; the first-stage file precedes the loop and shows equal inputs.
  The basis files are not retained, and the digests were recorded on the run hosts outside the logs.
- The identity holds for the principal ideal (u): `modulo(ideal(u),HS)` is the module of g with g*u in HS. For an
  ideal with two or more generators the same pattern returns another ideal (for HS = (x) and (x, y) it returns (1)).
- `modulo-colon/np-modstd`: on the retained first-stage basis of the N+ (32009, 10754) run, the two colons by modulo
  and the std between them take 5,785 s, 2,345 s and 4,953 s; the result reduces to zero modulo the retained saturated
  basis and conversely, and the second colon adds nothing (`CHECK fixpoint_bad 0`). The basis files are not retained;
  `../e8-rees-fibers-v2-p32009/bases.sha256` holds their digests.
- `modulo-colon/nm29-modstd` and `e8-nm-p32029-r9115.fiber-from-modsat`: the N- (32029, 9115) cell resumed from the
  first-stage basis of the quotient run (same sha256); the saturated basis has the sha256 of the quotient run's, and
  the fiber script is the v3 script with the satstd and colon section replaced by a read of that basis and the line
  `CERT H_outside_HS 0`.

## Conjugation between the two signs (A5-591, A5-592)

`conjugation/conjugation_map.sing` holds the matrix C, the frame F and the ideal J of the N- and N+ scripts with i as
a ring variable modulo i^2 + 1, and checks the substitution Phi (i -> -i, s4 -> -s5, s5 -> s4, s7 <-> s8): the log
prints zero nonzero entries for D Phi(C_N-) D + C_N+ and D Phi(F_N-) E - F_N+, mutual containment of Phi(J_N-) and
J_N+, and the factored form of detB for both signs. This is the mechanism behind the equal relation lines of a sign
pair. `conjugation/closed_forms.py` compares the detB line and the 21 UNIT lines of the eight logs with the products
of A5-592; `closed_forms.log` reads a match on all eight.

## Second-host replay of the retained v2 full runs (A5-578)

`replay-v2-full/` holds the logs of `e8-nm-p.v2-u-full.sing` and `e8-np-p.v2-u-full.sing` (retained bytes) run on a
second VM of the same size: 19 h 30 min 11 s and 17 h 27 min 51 s. Each log equals the retained log beyond the timers
of the `STAGE` lines and of the colon line, and the four basis digests equal `../e8-rees-fibers-v2-p32009/bases.sha256`.

## Check

From `docs/evidence/a5-exceptional-fibers`:

    python -B working/runs/e8-rees-fibers-v3-open-cells/render_cells.py --check
    python -B working/runs/e8-rees-fibers-v3-open-cells/check_open_cells.py
    python -B working/runs/e8-rees-fibers-v3-open-cells/check_open_cells.py --self-test

Both verdicts read PASS (Python 3.14.4, measured on the Arm host). The self-test feeds fifteen known-bad variants of one
log to the verdict (generator count, exit status, failure marker, Singular error line, numerator, inclusion, script
digest, truncation) and requires each to fail. `run2.sh` is the launcher of the cloud runs; `sha256.txt` lists every
file.

## Scope

One run per script and method; Singular 4.4.1 (banner Dec 6 2025 11:10:58) on both hosts; the two primes 32009 and
32029 and their four roots of -1. The certificates are modular: they state the fiber cone of the reduction modulo p on
the weight slice of A5-421, as A5-572 and A5-573 do.