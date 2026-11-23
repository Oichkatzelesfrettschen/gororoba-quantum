# Reconciliation of the review of the pull request (head acdcda581)

The owner chose `codex` on `gpt-daybreak-blue-latest` as reviewer and, as red-teamers, `agy` on
`gemini-4-neon-high` and `opencode` on a free OpenCode model, and ruled that the Advisor is not run. All three read
[pr-brief.md](pr-brief.md) at head `acdcda581`: [pr-review-codex.md](pr-review-codex.md),
[pr-review-agy-neon.md](pr-review-agy-neon.md), [pr-review-opencode.md](pr-review-opencode.md). No reviewer found a
fatal defect; each judged the computations sound at their stated scope. The findings concern controls, fail-closed
behavior and wording. Each is checked against the source below.

| Finding | Reviewer | Check | Outcome |
|---|---|---|---|
| The claim that the character data single out the nodal conic for R1 is false: a smooth conic a^2 - b c with the same characters has the same graded character | agy | `fiber_coefficients.py` now computes the character of k[a, b, c] modulo any quadric of trivial character and finds it equal to the nodal one for d = 1 to 12 | fixed: the README and A5-596 state that the characters leave the first conic nodal or smooth and force x y in the second |
| The smooth-conic control is hardcoded and excluded from the verdict | codex, agy | the control is now enumerated (Veronese with the linear action) against the measured splits at d = 5, 7 and enters the verdict | fixed |
| The exponent-2 control of the Pfaffian identity is entailed by the identity | opencode | pB^3 P - pB^2 P = pB^2 P (pB - 1) is nonzero whenever the identity holds | fixed: the control pairs each 4-Pfaffian with the 10-Pfaffian of the next quadruple (0 of 126 equal) |
| The drop-one-line digest control tests collision resistance only | agy, opencode | correct | fixed: the control regenerates E8bar -> N+ at the other root; it reads another digest, equal to the calibration digest |
| The checkers print counts and exit 0; drivers lack `set -e` | codex | correct | fixed: each Singular script prints a PASS verdict only on its expected counts, the drivers run under `set -eu` and require that line, and `arcs_vb_qi.py --check` enforces every line of its log |
| A5-594 has no control and one membership test does not give the exact exponent | agy | correct | fixed: tests of J + ((s2^2 - 1)^2), J + (s2 -+ 1) and the non-factor s2^2 - 2 added; no selected 10-Pfaffian lies in the square, so the row states one extra factor |
| The mutated arcs of A5-597 test membership only; the rank criterion has no control | agy, opencode | correct | fixed: the family through k = -8 stays on V(J) and has rank 2 at both points |
| A5-597 rests on primality of P1 and P2 and on the special family using the checked parametrization | agy | correct | fixed: both premises are stated in the row, the README and the script |
| A5-583 keeps "hypothesis:" and a causal clause; A5-577 keeps "the record holds no such cells"; both falsifiers are closing conditions | agy, opencode | correct | fixed: claims and falsifiers rewritten to the certified content |
| The torus reduction is stated without its hypotheses | all three | correct: the symmetry algebra is sl2 over a solvable radical | fixed: the README and docstring call the route a way of finding the map and name the conditions it does not establish |
| A5-595 says twelve cells; eight hold Hilbert data; Iso has no modular cell | all three | correct | fixed: the script also reads the successor record, ten cells, and the text lists them |
| A5-595 has no control; its component numerators are written in the script | agy | correct | fixed: a perturbed numerator must fail the division; the README and row say the numerators are transcribed from their rows |
| The status note schedules A5-418 through the modular map of A5-583, and cites A5-414 as a sample | agy | A5-418 is a characteristic-0 row on three sources; A5-414 proves a failure of congruence | fixed: T3 names the weight-slice closure argument; the boost sentence is corrected |
| Status-note cells: A5-066 and A5-067 cover N- only; V^a+- -> N+- overstates; X+ -> N+ lacks a K2 file; A5-448 missing; results rows lack "modulo 32009" and "at the retained basepoint" | codex, agy, opencode | each against its row | fixed |
| `parse()` could drop an unsigned term; a non-abelian centralizer raises instead of retrying; `transport()` omits the rank of the moved span | agy | correct as hazards; the retained files parse fully | fixed |
| A5-596 includes W8 -> N- without a measured split | opencode | correct | fixed: the row and README say that leg rests on the closed form |
| Singular warning lines in the modular Pfaffian logs | agy | correct | fixed: `--no-warn` |
| A trailing blank line in review-codex.md | codex | correct | fixed |

## Boundary

- **Status of A5-577, A5-583 and A5-594.** codex reads the ledger's definition of `certified` (matching bounds)
  and asks for `proved`; agy and opencode find `certified` consistent with the neighboring rows A5-572 to A5-592,
  which use it for a verified modular computation at one prime. The rows keep `certified`; aligning the definition
  in `ledger.py` with that use is a ledger-wide change outside this pull request.
- **Primes field of A5-595.** opencode asks for "char0 and 32009"; the ledger admits one value. The row keeps
  `char0` for its claim and lists the four modular cells in its basis.
- **Generality of the Pfaffian identity.** opencode reads the README's derivation as the general proof. The
  directory checks the identity on these matrices; the general statement is formal target 2 of the status note.

All fixes were rerun on the Arm compute host: `run_pfaffian.sh` and `run_bridge.sh` print PASS,
`weight_slice_modular_cells.py` and `fiber_coefficients.py` exit 0, and `arcs_vb_qi.py --check` reads PASS on the
new log and FAIL on the earlier log, which lacks the neighbor lines.
