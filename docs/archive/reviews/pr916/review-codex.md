**Scope**
- [measured] This report reviews the requested commit `43feb6fac8d447ed069aa1a721d24ae7ab114538`; all line references resolve at that commit.
- [measured] The branch advanced during review to `2510f9840`. Commits `14f827202` and `2510f9840` address some findings below, but remain outside this verdict.
- [measured] `gh pr view 916` failed because this sandbox could not reach `api.github.com`; the PR body was not independently checked.

**Ranked Defects**
1. **High — retained memory claims understate the actual peak by 2.6–3.7 times.**
   - [computed] `third-prime/README.md:45` and ledger row A5-560 at `ledger.tsv:534` report peak resident sets of 1.4 GB for E8-bar and 2.0 GB for W8.
   - [measured] The authoritative `systemd-run` stage receipts instead record 5,261,334,937 bytes = 4.900 GiB for E8-bar at `third-prime/relations/e8-nm/d2/receipt-d2.json:44`, and 7,301,444,403 bytes = 6.800 GiB for W8 at `third-prime/relations/w8-nm/d2/receipt-d2.json:44`.
   - [proved] `fiber_cone_driver.py:155` parses `systemd-run`’s `Memory peak`, while `fiber_cone_driver.py:345` records the Python linear-algebra process’s `ru_maxrss`. The README accidentally reports the latter, smaller measurement.
   - [computed] Remedy: change A5-560 and the README to report overall peaks of 4.90 and 6.80 GiB, optionally retaining 1.33 and 1.94 GiB as the linear-algebra-stage peaks.

2. **Medium — the A5-548 falsifier is expectation-directed and its main program succeeds on a false result.**
   - [proved] Calibration decides whether to run the nilpotent probe from the expected answer, `not red`, at `third-prime/quadric_rings.py:172-173`. The production run similarly hardcodes predicted nonreduced slugs at `third-prime/quadric_rings.py:200-202`.
   - [proved] An unexpected cell can therefore become undecided rather than falsified. `hypothesis_holds_on_every_decided_cell` ignores undecided cells at `third-prime/quadric_rings.py:217-218`.
   - [computed] The producer returns success unconditionally at `third-prime/quadric_rings.py:233`. Scratch probe output was:
     `return_code 0`, `defect_problems ['synthetic defect probe failed']`, `hypothesis_holds_on_every_decided_cell False`, `false_cells 6`.
   - [proved] The unit tests cover the pure `verdict` function but do not call `main` with a false or undecided record; see `tests/test_a5_owed_falsifier_programs.py:126`.
   - [computed] Remedy: compute the radical and linear nilpotents for every cell, require zero undecided cells, and return nonzero for any false hypothesis or defect problem. Add a main-level mutation test.
   - [measured] Post-scope commit `2510f9840` adds a nonreduced Cohen–Macaulay chart calibration; it does not belong to the reviewed commit.

3. **Medium — the A5-024 producer also exits successfully when its verdict is false.**
   - [proved] `sign_identity_over_qi` aggregates all decisive checks at `structure/sign-symmetry/npm_map_qi.py:377-383`, but `main` always returns zero at `npm_map_qi.py:386`.
   - [computed] A scratch probe forced every identity and reduction check false and obtained `sign_identity_over_qi: false` with `return_code 0`.
   - [proved] `ci/replay_check.py` still detects a difference from the currently retained positive record, so ordinary replay remains protective. Direct documented execution and creation of a replacement record are not fail-closed.
   - [computed] Remedy: return `0 if record["sign_identity_over_qi"] else 1`, with a main-level negative test.

4. **Low — the A5-559 replay writes generated scripts and logs into the tracked evidence tree.**
   - [proved] The output argument controls only the JSON record; `relation_ideal_orders.py:124-129` writes every `.sing` and `.log` below the source directory.
   - [proved] Consequently, `ci/replay_check.py` can overwrite tracked auxiliary evidence while comparing only `relation-ideal-orders.json`; a corrupted retained log is not itself compared.
   - [computed] Remedy: place scripts and logs beside the temporary output and separately verify retained logs by digest or byte comparison.
   - [measured] Post-scope commit `14f827202` redirects replay logs beside the output record; it is outside the scoped verdict.

5. **Low — the unit mutations omit the scroll family’s decisive P2-vanishing field.**
   - [proved] `problems()` checks `P2NONVAN`, but the mutation list at `tests/test_a5_owed_falsifier_programs.py:81-94` mutates only `P1NONVAN`.
   - [hypothesis] A regression deleting only the P2 check could pass this unit suite while removing one of the two minimal-component witnesses.
   - [computed] Remedy: mutate `("scroll", "plain", "P2NONVAN", 2)`.
   - [measured] Post-scope commit `14f827202` adds this mutation; it is outside the scoped verdict.

**Claim Status**
- [proved] **A5-009 and A5-559: earned.** The arc argument at `arcs/README.md:254-282` is complete given `K2 ⊂ L`.
- [proved] The scroll and top arcs give `L ⊂ P2 ∩ P1 = rad(K2)`. The embedded arc reaches the third associated prime and places each nilpotent linear form at order `ν+1 < ν+e`.
- [proved] For `M = rad(K2)/K2`, `Ass(M) ⊂ Ass(S/K2)`, `Ann(M)=A`, and only `A` contains that annihilator. Thus `M` is torsion-free over the domain `S/A`; the Hilbert identity gives rank one.
- [proved] If `L/K2` contained a nonzero homogeneous class, rank-one dependence with a nilpotent linear form would give `c∉A` with `cℓ∈L`. The embedded valuation forces `c` to vanish on the dense image and hence to lie in `A`, a contradiction.
- [computed] The retained record has 16 runs, no problems, all three associated primes at all four targets, and all five nilpotent forms with the required next coefficient.
- [proved] The N+ premise at 32009 is sound: A5-013 supplies the geometric automorphism, while A5-024 includes finite-header reduction and K2 span transport, not merely the Q(i) identity.

- [proved] **A5-548: `survives` is earned.** Three split primes support the stated CM-if-and-only-if-reduced pattern, but do not decide characteristic zero or all good primes.
- [proved] **A5-560: the mathematical `proved` status is earned.** Each nonreduced cell has an explicit linear form outside K2 whose square lies in K2; each reduced cell has the CM hypothesis plus the chart certificate.
- [proved] A squarefree characteristic polynomial on one chart is not sufficient without CM: the retained non-CM X and E8-bar cells themselves have squarefree chart matrices while remaining globally nonreduced.
- [proved] With CM, the certificate is sound. A length-`e` finite algebra with an element whose multiplication characteristic polynomial has `e` distinct roots equals the étale algebra generated by that element. The regular homogeneous system of parameters then lifts reducedness from the section through nonzerodivisors.
- [computed] The original calibration reproduces five expected cells, but its expectation-directed nilpotent switch does not independently exercise the general failure path described above.

- [proved] **A5-024: earned.** The retained Q(i) record has signed bijections for all 16 J and 21 G generators, the `t9`-only control fails on G, both mutations fail, and all four finite reductions pass.
- [proved] The finite J comparison is correctly stated as ideal equality, not generatorwise equality: only 10 of 16 displayed J generators are proportional after reduction, while mutual standard-basis reduction proves equality.

- [proved] **A5-032: earned for the actual claim.** Smith invariant factors `1,…,1,2,2` prove that the termwise diagonal stabilizer has order four, and the identity permutation enumerates every sign vector.
- [proved] The signed-permutation sweep’s profile pruning is heuristic and cannot prove absence of arbitrary non-diagonal signed permutations; `structure/README.md:118-120` states that limitation. A5-032 claims only the diagonal group, so this does not invalidate it.
- [measured] A fresh serialized sweep received no CPU progress and hit the 850-second local limit; this is an uncompleted independent replay, not contradictory evidence.

- [proved] **A5-002: earned.** The exact Q germ decompositions establish the two sheet multiplicities, their meeting, and the smooth-versus-rank-seven-quadric distinction recorded at `ledger.tsv:3`.
- [proved] **A5-003: earned.** The exact minimal-prime and colon computations decide the stated B9 base locus and residual VB/origin cases at the two primes and over Q(i), as recorded at `ledger.tsv:4`.
- [measured] The repository ledger check completed successfully with 533 rows.
- [measured] The targeted tests produced 38 passes and one environmental failure: `nullity8_fiber_import` could not start its Singular survivor selection because `systemd-run --user` had no user bus. No mathematical mismatch was observed.
- [proved] The sparse exclusions are safe for the ordinary PR jobs and these three producers: `quadric_rings.py` reads `relations-upto-d2.rel`, not the omitted `sq.txt.part*` or `nf-d2.txt*`.

**Unrecorded Conjectures**
- [hypothesis] **Full good-prime constancy:** all six quadric rings retain the same Hilbert data, reducedness, CM status, and defect structure at every good split prime.
  Falsifier: any changed degree, length, radicality, CM verdict, or colon structure.
  Cheapest test: repeat the 32057 program at the next split prime, computed as `(32069, root 4215)`.

- [hypothesis] **Direct characteristic-zero header equality:** on the Q(i) header slices, not merely the weight slices, `L=K2` in every degree.
  Falsifier: fewer or more than 148 exact quadrics, a failed exact membership, a changed associated prime, or an embedded order reaching `ν+e`.
  Cheapest test: lift the modular 148-dimensional relation basis, prove all lifted relations exactly, use modular rank as the upper bound, then run the three Q(i) order functions only for N− and transport N+ by A5-024.

- [hypothesis] **The non-CM defect is killed by the chosen linear section:** the squarefree chart observed on every nonreduced cell occurs because the nonregular parameter sequence annihilates the nilradical module.
  Falsifier: a non-CM nonreduced cell where the nilradical survives in the chart, or a colon computation showing no parameter annihilates it.
  Cheapest test: compute successive colons of the nilradical by the selected `l_i` and record where its Hilbert series collapses.

**Remaining Work**
- [hypothesis] **A5-548, fourth prime:** generate the six degree-two receipts at `(32069,4215)`, then run the unchanged CM, radical/chart, and defect-probe program.
- [measured] The 32057 E8-bar work took 6,684.810 s for products plus 486.489 s for membership; W8 took 6,375.954 s plus 315.744 s.
- [hypothesis] Sequential fourth-prime cost is approximately four hours: about two hours each for E8-bar and W8, under one minute for the smaller cells, and under one minute for the final verdict program.
- [measured] Peak planning must use 6.80 GiB, not 2.0 GB. An 8 GiB effective floor with no swap margin is tight; the retained driver budgets of 12 GiB for W8 and 20 GiB for E8-bar are defensible.

- [hypothesis] **A5-548, characteristic zero:** reuse the already retained A5-474 Q(i) quadric ideals; run exact hsop-length, radical/nilpotent, squarefree-chart, and colon probes over Q(i). No new relation search is required.
- [hypothesis] Expected cost is 2–10 minutes for the five sign representatives. Evidence: the finite-field verdict takes 44 s, the Q(i) weight-slice relation census took 60 s in parallel, and the Q(i) E8 order computations take 50–70 s per basepoint.
- [hypothesis] Provision 8 GiB. The analogous exact producer has an 8 GiB address-space cap, but no trustworthy child-process peak was retained; an exact peak requires one resource-scoped replay.

- [hypothesis] **A5-559, characteristic-zero headers:** regenerate the Q(i) J/G headers; lift and exactly verify 148 independent quadrics on N−; use reduction at 32009 to bound the nullity above by 148; compute the primary decomposition and Hilbert identity; run the three Q(i) order functions; transport N+ by the signed bijection.
- [hypothesis] Expected cost on an uncongested build host is 4–8 minutes: 158 s for Q(i) header generation, roughly 20–100 s for 148 exact memberships based on A5-474’s 858 relations in 100 s, and 50–70 s for the N− order proof.
- [measured] Under the current heavily contended serialized environment, the analogous all-cell Q(i) builder and signed sweep both reached the 850-second limit with negligible CPU allocation. Those timeouts measure host contention, not algebraic complexity.
- [hypothesis] Provision 8 GiB until a resource-scoped run records the real child peak; the retained Q(i) producer’s 8 GiB hard cap is the only current defensible bound.

**Verdict**
- [proved] The mathematical statuses of A5-002, A5-003, A5-009, A5-024, A5-032, A5-548, A5-559, and A5-560 are supported at the fields and primes they state.
- [computed] Commit `43feb6fac` still contains one incorrect resource claim and several fail-closed/calibration weaknesses. The resource correction and nonzero exits remain required even though later branch commits address the replay side effect and chart calibration.

