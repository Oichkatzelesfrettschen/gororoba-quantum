# Red-team brief: the generic Rees blocks of E8-bar at N- (ledger row A5-542) and rows A5-604, A5-606, A5-607

Read first: the workspace AGENTS.md, then the tree under review/AGENTS.md. You are a red-teamer: try to break the claims. Work read-only: change no file, never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents; run no test suite and no computation longer than 2 minutes on this host (git, grep and short python3 arithmetic are fine; do not run Singular here).

Tree: the tree under review (branch a5-pfaffian-boost-stability, pull request 996). See the last three commits with git -C the tree under review log -3 --stat.

## Claims under review (each is a claim, not a fact)

1. A5-542, status survives. Modulo 32009 and 32029, at s2 = 7013, 21890, 3567 and over GF(p)(s2), the Rees ideal of E8-bar -> N- on the weight slice has 32 minimal generators of y-degree 1 beyond J*y and the 2 x 2 minors, in 11 bidegrees with 2, 1, 6, 6, 1, 3, 5, 3, 2, 2, 1 generators. Support: docs/evidence/a5-exceptional-fibers/working/runs/e8-nm-rees-generic-blocks/ (README.md, stage_a.tmpl, deg1.tmpl, gen_blocks.py, run_blocks.sh, ten logs). Falsifier: the block script counts something other than minimal generators (for example the quantity Q1 - rankE, the module M1 = M + m K, the use of modulo() for the kernel, the claim that Jz is the kernel of the parametrization phi checked only in y-degree 0); the function-field unit silently specializes; the two primes are not independent evidence; the logs do not show what the README says.
2. A5-604 as extended: the E8-bar closure ideal has a 16-dimensional stabilizer among linear vector fields and the pair (closure, ten-Pfaffians) a 15-dimensional one, with the boost outside. Support: docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/alg-e8-p32009.log and README.md. Falsifier: the 210 CONSTRAINT lines do not have rank 210, or the sampled Pfaffians (every 13th) make the pair value only an upper bound that the named lower bound does not meet.
3. A5-606, status proved: the hardware twins are the primaries times e16 and s_twin(x) = -s_primary(x XOR 16). Support: docs/evidence/a5-exceptional-fibers/hardware-orbits/twin_sign_relation.py and twin-sign-relation.json. Falsifier: the script's sign convention differs from gororoba_quantum/pathion_kernel_map.py (_k_matrix, orientation_signs, upper_bit), or the conclusion "a twin reading is a bit-flip control of the bit-4 qubit and carries no algebraic information" does not follow for the compiled circuits.
4. A5-607, status survives: in the chart of a pivot Pfaffian at a point of VB, pB D(F_j) lies in (F) + I(W8) for all 21 Schur entries and 18 of 21 lie outside (F) + I(E8-bar), while a G_2 derivation passes on both. Support: pivot_stability.py, piv-w8.log, piv-e8.log in the same directory. Falsifier: the test point is not on VB or not in both closures, the Schur entries do not generate the ten-Pfaffian ideal where pB is invertible, the degree bound 9 truncates the reduction, or the reading "the boost fails locally" overstates a test at one multiplier level.

## Also deliver

- For A5-542: the cheapest computation that would lift the count to characteristic 0 or bound the exceptional set of s2, and whether the 11 bidegrees have a structural explanation (for example through the weights of the 21 generators G listed in stageA-p32029.log).
- Connections between these rows and rows A5-414, A5-428, A5-457, A5-506, A5-600, A5-602, A5-603 of docs/evidence/a5-exceptional-fibers/ledger.tsv that no row states, each marked hypothesis with its falsifier.
- Defects with file:line.

Report ranked by consequence; every finding tied to a file:line or a short computation and marked proved, computed or hypothesis. End with the claims you could not break and what you tried.
