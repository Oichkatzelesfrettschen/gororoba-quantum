# Read-only review: A_5 fiber tooling and the nullity-16 record

Review, do not edit. Worktree: ~/worktrees/IBMQuantum/a5-kernel-attachments (branch HEAD plus untracked files).
Files (all new unless noted), under docs/evidence/a5-kernel-attachments/:
- fiber_inputs.py: regenerates fiber inputs (J, G) from the Q(i) producer at a chosen split prime and root of -1.
- fiber_cone_driver.py: degree-by-degree fiber cone F(I)=sum I^d/mI^d; h_d via F_p rank of normal forms mod std(J+m*P_d); emits relations and receipts.
- fiber_certificates.py: completion certificates (candidate ideal, dense family, bounded Hilbert scope cut).
- nullity16_rees_fibers.py: producer; changed _run_singular (cgroup MemoryMax scope, 16 GiB, SIGTERM->SystemExit, finally-killpg), prime 32009, PERMITTED_BLOCKED now modular_rees_fiber for all ten nullity-8 rows.
- nullity16-rees-fibers-result.json: regenerated record; byte-exact --check passes.
- README.md (modified section "The nullity-16 Rees fibers: eight complete, ten block at the modular fiber"), ledger.md (row 2k-c appended).
- tests/test_a5_fiber_cone_driver.py.
Validations already run: driver reproduces E8bar->VB h=10,34,80 and X- h=15,51 with 69 relations; 5 tests pass; ruff/mypy clean.

Report, ranked by severity, with file:line: correctness defects (math: is h_d exact as computed; are relations verified; does the certificate layer ever claim more than it proves), process leaks or limit defects in subprocess handling, claims in README/ledger that the record does not support, and repo-rule violations (AGENTS.md: no assert in checks, parallel.py for independent loops, seeds from QRNG, comment style). Say "none" for a category with no finding. Keep it under 80 lines.
