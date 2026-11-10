# Brief: the portable least-squares precision sweep and its six-host results (gororoba-quantum, branch least-squares-precision/portable-sweep, commits 54359a760 and 315d929bb)

Read first: <workspace>/AGENTS.md, then
<worktree>/AGENTS.md. Work read-only: change no
file except your report (named at the end); never commit, push, stash, submit to a provider or start a cloud
resource; spawn no subagents. You may run git and `/usr/bin/python` with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; keep each computation under 15 minutes, in a scratch
directory under /tmp. A random draw takes its seed from `docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json`
values at indices 200 to 255; name the indices you use.

Material: the worktree <worktree>, two commits on
main e2a694e7b: `git diff e2a694e7b...HEAD`. Files: `docs/evidence/least-squares-precision/fp_host.py` (new),
`fp_sweep.py` (rewritten), `fp_export.py`, `README.md` (sections "Portable sweep across hosts" and "Results across
hosts"), and `hosts/*.jsonl` (rows from six host configurations). `fp_backends.py` is unchanged.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. `fp_sweep.py` runs on Linux, macOS and native Windows. Its cap mechanism (systemd scope with memory.max read back,
   RLIMIT_AS with a 2 GiB floor, or none) is reported truthfully per row. Status: computed on four OS/arch
   combinations (rows in `hosts/`). Falsifier: a row whose recorded cap differs from what applied, or a path that
   cannot run on its named OS.
2. The thread ladder never exceeds the host's usable CPUs, and skipped configurations carry a correct reason. Status:
   computed. Falsifier: a row with threads above `os.cpu_count()`, or an x87 row run on non-x86 or on a 64-bit
   `long double`.
3. The arb, binary128 (SLEEF) and x87 configurations give the same per-quantity error on every host where they run,
   while every float64 configuration through the BLAS differs across hosts. Status: computed from `hosts/*-full.jsonl`.
   Falsifier: a non-BLAS configuration whose recorded error differs between hosts, or a float64 one that matches on
   all hosts.
4. On the hosts that ran `fp_export.py` themselves, the five producer input digests equal the build host's on Linux
   x86-64 (Zen 4, Sapphire Rapids) and Linux aarch64 (Neoverse N1). On macOS (M1), only `observed_rate_columns`
   differs, and the difference lies in the bootstrap replicate array, not in rounding. Status: measured. The
   hypothesis is that Apple libm changes accept-reject decisions in numpy's binomial and Poisson samplers. Falsifier:
   a numpy source path showing those samplers use no libm call, or a difference outside the replicate array.
5. No row carries a hostname, user name or local path. Status: computed by grep. Falsifier: any such string in
   `hosts/*.jsonl`.
6. The README states only what the rows support, and its "not run" entries (turion-linux SIGILL, Windows export) are
   accurate. Status: claim.

## Questions to answer

- Is the Windows QuadBLAS `NotImplementedError` a defect `fp_host` should detect and skip, and how cheaply?
- Do the per-row host records leak anything the workspace guide keeps out of public files?
- Defects in code, claims or records, with file:line.
- Conjecture where nothing is posited: what else do the six hosts' rows show about BLAS kernel selection, with its
  falsifier.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a function name, each
marked proved, computed, measured or hypothesis. Write it to <worktree>/docs/local/reviews/codex-sweep.md, under 150 lines.
