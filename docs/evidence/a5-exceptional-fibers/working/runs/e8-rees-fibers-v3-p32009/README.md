# Zero-generator guard for the modular Rees fiber of Iso -> N- at p = 32009

This directory retains the successor of `iso-nm-p.v2-u-full.sing` in `../e8-rees-fibers-v2-p32009/` that removes the
termination defect of issue 946, its toy run, and the control that shows the defect. The ring, the weight slice, the
prime 32009 and the root of -1 (10754) are those of the v2 directory; its README describes the mechanism of the script.

## The defect and the change

The unit replacement of each generator strips from `Gr[uk]` the content `uc`, the gcd of its coefficients in s2, by
`while(subst(uc,s2,0)==0){ uc=uc/s2; }`. A generator that is 0 modulo J has `uc = 0`, `subst(0,s2,0)` is 0 and `0/s2` is 0,
so the loop does not end, and Singular, which exits 0 on SIGTERM, leaves a log without a result line. No retained v2 run
reaches the loop with a zero generator (every log prints nonzero `UNIT terms left`). The successor differs from the v2
script in three places, which `check_rees_fibers_v3.py` rebuilds from the retained v2 script and compares byte for byte:

1. after the gcd loop, `if(uc==0){ "CERT FAIL unit_zero_generator"; quit; }`;
2. the loop condition `while(uc!=0 and subst(uc,s2,0)==0)`;
3. a count of the generators whose constant term c(0) is 0, printed as `UNIT zero_constant_term_count N`.

The v2 script already prints one `UNIT k c(0)=... c=...` line per generator (line 192); the count line sums the same test
that line 192 rejects, so the log shows the unit test as a number. The v3 script writes its basis files under the v2 name
`iso-nm-p.c-u-full` and keeps its `SOURCE sha256` line.

## Result

| Run | Script | Outcome | Wall time, memory |
|---|---|---|---|
| Iso -> N- | `iso-nm-p.v3-u-full` | `UNIT zero_constant_term_count 0`, `FIBER bound 0 minimal generators 68 dim 5 mult 23`, `FIBER outside_K 0 K_outside_fiber 0`, `EXIT 0` | 9.4 s, 34 MB |
| toy, generators 0 and s1^2 | `toy-zero-generator.v3` | `STAGE rees_start`, `CERT FAIL unit_zero_generator`, `EXIT 0` | 0.03 s |
| toy, v2 loop | `toy-zero-generator.v2-loop` | `STAGE rees_start`, then no output until `EXIT 124` | 5.0 s (timeout) |

- The v3 Iso log equals the retained v2 Iso log line for line once the script digest, the script name, the Singular timers
  and the count line are set aside; the two `.ssi` basis files have the digest `bac46ad90d228acf...` of `bases.sha256` in
  the v2 directory.
- Each run is one Singular 4.4.1 process (banner Dec 6 2025 11:10:58) on one compute host, wrapped in `timeout` inside a
  16 GiB memory scope with no swap, launched by `run2.sh` (the v2 launcher, unchanged); `NAME.time` is the
  `/usr/bin/time -v` record.
- The toy script holds the loop of the script on a two-variable ring with `Gr=0,s1^2`; the control differs from it in the
  guard and the loop condition alone, so the pair is a known-bad and a known-good run of the same loop.

## What the check decides

`check_rees_fibers_v3.py` tests the internal consistency of the logs and their ties to the v2 directory; it does not test
that Singular produced them. It runs from `docs/evidence/a5-exceptional-fibers` as
`python -B working/runs/e8-rees-fibers-v3-p32009/check_rees_fibers_v3.py` and runs no Singular. It verifies the script
rebuild above, the `UNIT` lines and the count line, the results lines through the v2 verdict (the v2 checker is bound by
`sha256.txt` of its directory and keeps its bytes), the equality with the v2 Iso log, the toy and control endings, the
toy wall time below one second, and `sha256.txt`. `--self-test` rejects 12 mutated copies of the Iso log (no per-generator
lines, a lost one, no count line, a nonzero count, a zero constant term, the failure marker, a nonzero `outside_K`, a
changed multiplicity, an `EXIT 1`, a wrong script digest, two truncations) and 3 of the toy log, and rejects the toy log
itself with the marker named. `tests/test_a5_rees_fibers_v3_check.py` runs the same verdicts in the default lane.

## Scope

One prime (32009), one root (10754), the Iso -> N- cell, one execution of the Iso run, one of the toy and one of the
control. The two E8-bar scripts of the v2 directory have the same loop and no successor here. The open cells of A5-576
(second prime 32029, second root 21255) are not run; ledger row A5-586 records the defect and this successor.

## Files

| File | Content |
|---|---|
| `iso-nm-p.v3-u-full.sing`, `.log`, `.time` | the successor script, its log and its timing record |
| `toy-zero-generator.v3.sing`, `.log`, `.time` | the toy ring with the guard |
| `toy-zero-generator.v2-loop.sing`, `.log`, `.time` | the toy ring with the v2 loop, ended by the timeout |
| `run2.sh` | the launcher of the v2 directory, unchanged |
| `check_rees_fibers_v3.py` | the verdict described above |
| `sha256.txt` | sha256 of every other retained file |
