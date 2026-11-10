# A5 exceptional-fiber ledger adversarial audit

Reviewer: `codex-medium`

Reviewed checkout: detached `4635cc5a47de8458344196fc921a2953fe35d7ee`

Review boundary: committed ledger, registry, proofs, records, narratives, retained source transcriptions, and bounded deterministic recomputations. No provider action or random sample ran; therefore the review consumed no QRNG index.

## Per-row verdicts

`holds` means the status under test survived the checks required by the brief, not that every open or surviving mathematical claim is proved. Common evidence for concise rows: `ledger.py --check` counted 242 rows and the exact status totals printed below; the documented registry command printed `registry matches`; all recomputed sign, header, and K2 witnesses printed `ok`; and the previous proof reconciliation is retained in `docs/archive/reviews/findings-deep/README.md`. Exceptions carry their specific reason.

| ID | Status under test | Verdict | One-line reason |
|---|---|---|---|
| A5-001 | proved | holds | The cited exact argument and retained reconciliation cover the written scope. |
| A5-002 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-003 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-004 | proved | holds | The cited exact argument and retained reconciliation cover the written scope. |
| A5-005 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-006 | survives | holds | The corrected X+ to N+ and X- to N- fibers agree with the cited 15-generator basis. |
| A5-007 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-008 | proved | holds | The bounded C30 argument covers W8 in all degrees over the stated finite fields. |
| A5-009 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-010 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-011 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-012 | proved | holds | The cited exact argument and retained reconciliation cover the written scope. |
| A5-013 | proved | holds | All six exact generator-map sign witnesses recomputed successfully. |
| A5-014 | refuted | holds | The cited retained counterexample decisively defeats the written claim. |
| A5-015 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-016 | open | holds | Order-2 arcs on the residual plane and apex provide a reachable deciding test. |
| A5-017 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-018 | refuted | holds | The cited retained counterexample decisively defeats the written claim. |
| A5-019 | refuted | holds | The cited retained counterexample decisively defeats the written claim. |
| A5-020 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-021 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-022 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-023 | survives | holds | The exact sign witness supports the scoped correspondence. |
| A5-024 | survives | holds | The exact sign witness supports the scoped correspondence. |
| A5-025 | survives | holds | The exact sign witness supports the scoped correspondence. |
| A5-026 | survives | holds | Every compared second-prime rank duplicates the first-prime rank. |
| A5-027 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-028 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-029 | open | defect | `the limit computation` gives no kernel or Plucker acceptance and rejection condition. |
| A5-030 | survives | holds | Retained evidence supports the stated scope and the decisive falsifier remains unfired. |
| A5-031 | survives | holds | Retained ladders reach the stated bounds at practical closing orders. |
| A5-032 | survives | holds | Retained exhaustive symmetry evidence supports the bounded group claim. |
| A5-033 | refuted | holds | The cited retained counterexample decisively defeats the written claim. |
| A5-034 | refuted | holds | The two-component decomposition decisively defeats irreducibility. |
| A5-035 | refuted | holds | The cited component dimensions decisively defeat equidimensionality. |
| A5-036 | refuted | holds | Retained paths with different limiting kernels defeat path independence. |
| A5-037 | rejected | holds | The cited failed transitivity premise decisively rejects the method. |
| A5-038 | rejected | holds | The cited regularity argument cannot bound the missing relations. |
| A5-039 | refuted | holds | Retained saturation failures defeat completion on the stated hardware. |
| A5-040 | superseded | defect | The old row supplies no schema-consistent pointer to one live covering row. |
| A5-041 | refuted | defect | One presentation exceeded 3 GB, while reduced and bounded verification routes remain untested. |
| A5-042 | refuted | holds | The retained elimination run crossed the claimed session boundary. |
| A5-043 | refuted | holds | The Iso failure falsifies the universal direct-decomposition method claim. |
| A5-044 | superseded | defect | The old row supplies no schema-consistent pointer to one live covering row. |
| A5-045 | refuted | holds | Order-1 arcs omit the degree-3 component and cannot certify the full fiber. |
| A5-046 | rejected | holds | The cited grading analysis fails to force toric components. |
| A5-047 | refuted | holds | A retained counterexample defeats the naive leading-form criterion. |
| A5-048 | refuted | holds | The retained run crossed the claimed 78 GB scope. |
| A5-049 | refuted | holds | The exact diagonal sign witness transports the opposite-sign case. |
| A5-050 | refuted | holds | The retained W8 computation crossed the 24 GB claim. |
| A5-051 | rejected | holds | Later closing ranks show that a low plateau is non-decisive. |
| A5-052 | superseded | defect | The old row supplies no schema-consistent pointer to one live covering row. |
| A5-053 | refuted | holds | The retained limits and failures defeat the claimed 4 GiB cause. |
| A5-054 | refuted | holds | Raising the cap did not produce the claimed fix. |
| A5-055 | refuted | holds | Retained provider state defeats the TPU-slot claim. |
| A5-056 | refuted | holds | The cited arithmetic provenance of 155 is false. |
| A5-057 | refuted | holds | Retained chart runs exceed the stated time bound. |
| A5-058 | proved | holds | The cited exact proof covers radicality at its stated scope. |
| A5-059 | proved | holds | The cited exact proof covers dimension, degree, and Cohen-Macaulayness. |
| A5-060 | proved | holds | The cited exact proof covers geometric primeness and degree. |
| A5-061 | proved | holds | The cited exact proof covers radicality at its stated scope. |
| A5-062 | proved | holds | The cited decomposition and colon proof cover the statement. |
| A5-063 | proved | holds | The cited germ computation proves exactly the two written components. |
| A5-065 | proved | holds | The cited containment proves the lower bound and analytic spread. |
| A5-066 | proved | holds | The C30 plane-family proof covers the all-degree W8 conclusion. |
| A5-067 | survives | holds | Retained degrees support equality and the local-route falsifier remains open. |
| A5-068 | proved | holds | The cited local and tangent-cone computation covers the statement. |
| A5-069 | survives | holds | Retained point-section controls support the bounded operational claim. |
| A5-070 | refuted | defect | Deaths at 5 GB and 10 GB address-space caps do not refute fitting within 11 GB. |
| A5-071 | refuted | holds | Four retained capped runs exceed or fail the written eight-hour portfolio. |
| A5-072 | superseded | defect | The old row supplies no schema-consistent pointer to one live covering row. |
| A5-073 | superseded | defect | The field points forward despite schema semantics saying it names rows replaced by this row. |
| A5-074 | refuted | holds | The retained symbolic arc family crossed the session boundary. |
| A5-075 | proved | holds | The exact finite-field query count covers the written parameters. |
| A5-076 | refuted | holds | The query complexity decisively defeats the proposed quantum pipeline. |
| A5-077 | proved | holds | Receipt-bound and full-product runs give the same rank and blocks. |
| A5-078 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-079 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-080 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-081 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-082 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-083 | open | holds | Degree-6 membership after the degree-5 pilot is a reachable deciding test. |
| A5-084 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-085 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-086 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-087 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-088 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-089 | open | holds | Sign transport plus degree-6 membership gives a reachable deciding test. |
| A5-090 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-091 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-092 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-093 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-094 | superseded | defect | A5-183 replaces the row, but the old row carries no forward live target. |
| A5-095 | open | holds | Degree-6 membership after the degree-5 pilot is a reachable deciding test. |
| A5-096 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-097 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-098 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-099 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-100 | superseded | defect | A5-220 replaces the row, but the old row carries no forward live target. |
| A5-101 | open | holds | Sign transport plus degree-6 membership gives a reachable deciding test. |
| A5-102 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-103 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-104 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-105 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-106 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-107 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-108 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-109 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-110 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-111 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-112 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-113 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-114 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-115 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-116 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-117 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-118 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-119 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-120 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-121 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-122 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-123 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-124 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-125 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-126 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-127 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-128 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-129 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-130 | certified | defect | The receipt proves h5=4116, but `claims.json` calls the cell open because its scan omits `w8-n16-azure`. |
| A5-131 | proved | holds | The C30 proof covers degree 6 without a rank-record dependency. |
| A5-132 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-133 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-134 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-135 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-136 | certified | defect | The second-prime receipt proves h5=4116, but `claims.json` calls the cell open. |
| A5-137 | proved | holds | The C30 proof covers degree 6 without a rank-record dependency. |
| A5-138 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-139 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-140 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-141 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-142 | certified | defect | Sign transport and receipt prove h5=4116, but `claims.json` calls the cell open. |
| A5-143 | proved | holds | The C30 proof and sign isomorphism cover degree 6. |
| A5-144 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-145 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-146 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-147 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-148 | certified | defect | Sign transport and second-prime receipt prove h5=4116, but `claims.json` calls the cell open. |
| A5-149 | proved | holds | The C30 proof and sign isomorphism cover degree 6. |
| A5-150 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-151 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-152 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-153 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-154 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-155 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-156 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-157 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-158 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-159 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-160 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-161 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-162 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-163 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-164 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-165 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-166 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-167 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-168 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-169 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-170 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-171 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-172 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-173 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-174 | refuted | holds | The retained coordinate-chart run crossed the 5 GB claim. |
| A5-175 | rejected | holds | The proposed four-generator reduction cannot prove the intended bound. |
| A5-176 | refuted | holds | The retained sliced-chart run crossed the 9 GB claim. |
| A5-177 | certified | holds | Exhaustive pair enumeration reproduces the stated nullity counts. |
| A5-178 | certified | holds | Exhaustive block classification reproduces the stated equivalence classes. |
| A5-179 | refuted | holds | Hardware observations fall outside the calibrated-noise prediction. |
| A5-180 | survives | holds | Retained hardware data support the scoped observation and mutation control. |
| A5-181 | refuted | holds | The retained first standard basis crosses the 9 GiB cap. |
| A5-182 | survives | holds | Retained two-device shallow-block data support the scoped claim. |
| A5-183 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-184 | survives | holds | Retained Tuna-17 data support the stated sign-network observation. |
| A5-185 | refuted | holds | Retained null-block and cross-provider data defeat the claim. |
| A5-186 | survives | holds | The row is explicitly a bounded hypothesis with an unfired falsifier. |
| A5-187 | survives | holds | Retained regressions support the stated bounded pattern. |
| A5-188 | survives | holds | Retained preregistered Ascella data meet the 0.07 bound. |
| A5-189 | refuted | holds | Retained two-block data violate the 0.07 independence claim. |
| A5-190 | refuted | holds | Frozen per-mode efficiencies fail to explain the retained errors. |
| A5-191 | superseded | defect | The old row supplies no schema-consistent pointer to one live covering row. |
| A5-192 | survives | holds | Retained parallel IBM placements meet the stated bounds. |
| A5-193 | survives | holds | Retained IBM controls exclude the stated Tuna-sized offset. |
| A5-194 | refuted | holds | Retained corrected blocks fall outside the stated zero window. |
| A5-195 | refuted | holds | Retained odd-part regressions fail the stated criteria. |
| A5-196 | survives | holds | The row is explicitly a bounded hypothesis with an unfired falsifier. |
| A5-197 | refuted | holds | Retained within-arm repeats show a position or drift effect. |
| A5-198 | survives | holds | The retained Newcombe-Wilson interval stays inside the preregistered bound. |
| A5-199 | survives | holds | Retained IBM and Ascella block readings meet the stated comparison. |
| A5-200 | survives | holds | Identical-mesh replay meets the preregistered persistence cutoff. |
| A5-201 | survives | holds | Fresh meshes reject full carrying while leaving the stated half-carry boundary open. |
| A5-202 | open | holds | A fresh-mesh shifter-map test supplies a reachable, approval-gated falsifier. |
| A5-203 | refuted | holds | Retained anchors defeat the fixed 1.08 explanation. |
| A5-204 | refuted | holds | Retained compilations show simulator and hardware meshes differ. |
| A5-205 | refuted | holds | The first standard basis remained unfinished at 23.5 hours. |
| A5-206 | proved | holds | Exhaustive orbit classification covers every measured operand. |
| A5-207 | proved | holds | Exact polynomial and rank tests cover the listed operands. |
| A5-208 | proved | holds | Exact substitution and nullity calculations cover the plane. |
| A5-209 | proved | holds | Exact substitution and nullity calculations cover the plane. |
| A5-210 | survives | holds | Retained search supports the stated chord and bounded nonexistence claim. |
| A5-211 | survives | holds | Retained bounded search supports the stated absence claim. |
| A5-212 | proved | holds | Exact doubling and nullity calculations cover the N+ endpoint. |
| A5-213 | proved | holds | Exact path evaluation proves the stated non-incidence. |
| A5-214 | survives | holds | Retained slice controls support the scoped method claim. |
| A5-215 | survives | holds | Retained codimension-5 slice evidence supports the scoped claim. |
| A5-216 | survives | holds | Retained codimension-3 slice evidence supports the scoped claim. |
| A5-217 | survives | holds | The preregistered codimension-4 test remains decisive and pending. |
| A5-218 | rejected | holds | The slice does not distinguish the required component. |
| A5-219 | survives | holds | Exact singular-value expansions support the stated orders. |
| A5-220 | certified | holds | Retained rank, Hilbert bound, engine, and header evidence passed. |
| A5-222 | refuted | holds | Exact restricted ideals and invariants defeat equality. |
| A5-223 | proved | holds | The cited exact coordinate decomposition covers the statement. |
| A5-224 | refuted | holds | Exhaustive finite-field counterexamples defeat the sum rule. |
| A5-225 | survives | holds | Exhaustive mixed-pair enumeration supports the bounded pattern. |
| A5-226 | refuted | holds | Retained equal input-nullity pairs with different output nullity refute the function claim. |
| A5-227 | survives | holds | Generic retained points support the scoped counterpart, not the universal rule. |
| A5-228 | proved | holds | The displayed estimator identity is an exact algebraic derivation. |
| A5-229 | proved | holds | The forced-block identity is exact for the stated contrast vectors. |
| A5-230 | survives | holds | Retained block profiles support the scoped interpretive claim. |
| A5-231 | refuted | holds | Retained class means differ, defeating bin independence. |
| A5-232 | refuted | holds | Retained equal profiles across orbits defeat discrimination. |
| A5-233 | survives | holds | The row is explicitly a bounded hypothesis with an unfired relabeling test. |
| A5-234 | proved | holds | Exact block counts prove the forced and informative contributions. |
| A5-235 | refuted | holds | Retained fiber Hilbert data defeat the proposed tensor product. |
| A5-236 | survives | holds | The explicit matrix and Jacobian criterion support the scoped construction. |
| A5-237 | superseded | defect | The field points forward despite schema semantics saying it names rows replaced by this row. |
| A5-238 | proved | holds | The Walsh-channel estimator formulas follow exactly from the character decomposition. |
| A5-239 | survives | holds | Retained fits and wide-run prediction support the bounded channel hypothesis. |
| A5-240 | survives | holds | Retained leakage signs support the stated unresolved non-diagonal effect. |
| A5-241 | survives | defect | Binomial and Fisher aggregation lack a dependence-preserving null across shared runs and replicas. |
| A5-242 | open | holds | Moving the orientation phase and repeating the full map is a reachable approval-gated falsifier. |
| A5-243 | proved | holds | Exhaustive 252-operand and 35-tiling enumeration proves the blindness claim. |
| A5-244 | survives | holds | Retained ladders support the measured range; the row labels the X continuation a hypothesis. |

The table covers 242 unique ledger IDs: 225 `holds`, 17 `defect`, and 0 `cannot check`.

## Ranked findings by consequence for `dimension32-global-topology`

1. **Critical attaching-data specification defect, A5-029 (text).** The program's consumer needs limiting 8-planes, not only fiber directions (`docs/notes/topics/a5-exceptional-fiber-status.md:8-24`). The open row's falsifier is only `the limit computation` (`docs/evidence/a5-exceptional-fibers/ledger.tsv:30`), so a computation can finish without a declared verdict. **Computed audit finding.** Replace the falsifier with: compute the exact kernel or Plucker limit on each certified generic arc family; reject if the limiting kernel has dimension other than 8, its Plucker vector vanishes, or generic branches give inconsistent 8-planes. This work can start before characteristic 0 (`docs/notes/topics/a5-exceptional-fiber-status.md:72-75`).
2. **High registry/ledger inconsistency in four W8 degree-5 cells, A5-130/136/142/148 (record and code-discovery defect).** `claims.json` says `open`; the ledger says `certified`. The registry scan roots omit `w8-n16-azure`, although the retained records give rank 4116 and blocks 1017/1005/1047/1047 at both primes with engine digest `7849cbc71ccf1787894c74182b6cd225ca8a485973f062d47f77c6b63ce12bbd` and canonical header digests (`docs/evidence/a5-exceptional-fibers/w8-n16-azure/README.md:3-18,23-34,41-44`). **Computed audit finding; mathematical rank measured in retained runs.** Add this root, teach the builder to consume the receipt `.out` JSON records, or convert them to an already scanned record form; rebuild the registry. The records support certification, so downgrading the mathematics would be the wrong remedy.
3. **High incompleteness at the actual attaching layer, not a ledger-count error.** The status recount is exact: 92 of 96 finite-field degree cells are certified or proved, one of five all-degree claims is proved, characteristic 0 has zero proofs, and A5-029 remains unstarted (`docs/notes/topics/a5-exceptional-fiber-status.md:26-35`). **Computed.** The impressive first-layer completion therefore supplies directions, while the registry goal still lacks the map from directions to kernel 8-planes.
4. **Medium false refutation, A5-070 (text/logic defect).** The p=32029 process reached 5.2 GB under a 5 GB `RLIMIT_AS`, and p=32009 reached 10.5 GB under a 10 GB cap (`docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/README.md:67-74`). Those cap crossings cannot refute `fits 11 GB`; address-space limits also differ from resident-memory capacity. **Measured inputs; computed logic finding.** Change the status at `docs/evidence/a5-exceptional-fibers/ledger.tsv:70` to `survives` or rewrite the claim to the tested 5 and 10 GB caps.
5. **Medium overbroad refutation, A5-041 (text defect).** The basis says one 18-variable presentation crossed 3 GB in 14 minutes while reduced presentation, bounded membership, and saturation witnesses remain untested (`docs/evidence/a5-exceptional-fibers/ledger.tsv:42`). **Computed audit finding.** Refute only that presentation and retain the cheaper verification question as open.
6. **Medium statistical overclaim, A5-241 (analysis/text defect).** The code correctly applies a seven-coordinate Hotelling test per forced block (`docs/evidence/pathion-kernel-map/nhat-bias/nhat_spectral.py:128-146`), but the narrative combines 52 blocks by a binomial tail and combines p-values within each run by Fisher (`docs/evidence/pathion-kernel-map/nhat-bias/README.md:221-229`). Blocks share run, calibration, and replica structure; independence or a dependence-preserving null calibration is absent. **Computed audit finding.** Preserve the individual tests; replace the family inference with a run-level permutation or bootstrap that preserves replica/block covariance, or a hierarchical multivariate test with family control.
7. **Low machine-readable supersession defect (text/schema).** Nine rows have status `superseded`. A5-040/044/052/072/094/100/191 lack a forward live target. A5-073 and A5-237 put live A5-063 and A5-066 in `supersedes`, while the schema defines that field as rows the current row replaces. **Computed.** Add one `replaced_by` field or choose one direction and validate it in `ledger.py`; backfill all nine rows.
8. **Low exact-replay drift in the spectral record (record/serialization defect).** `nhat_spectral.py --self-test` passed, while `nhat_spectral.py --check` failed because `flatness_hotelling_t2` recomputed as `765.317510966225` rather than retained `765.317510966224` at `docs/evidence/pathion-kernel-map/nhat-bias/result_spectral.json:4059`. **Computed.** The p-value and scientific verdict remain unchanged. Canonicalize rounding independently of the platform's last binary digit or compare a declared numeric tolerance; then regenerate the bound record.

## Multidimensional pattern audit

| Dimension | Classification | What the evidence establishes |
|---|---|---|
| Sign-paired fibers | proved | Exact generator maps carry every Y to N+ case to its paired image at N-; all six retained witnesses recomputed successfully (`docs/evidence/a5-exceptional-fibers/witnesses.py:76-109`; `witnesses.jsonl:13-18`). |
| W8 all degrees | proved | The C30 component lies in the fiber and supplies equality with K2 over the two stated finite fields; this is stronger than six isolated ranks (`docs/notes/topics/a5-exceptional-fiber-status.md:19-20`). |
| Prime dependence | computed | Per-block ranks agree in 23 of 23 two-prime cells; six E8-bar plateau cells are informative. The second-prime ranks duplicate the first-prime cells more often than any ledger row states (`docs/evidence/a5-exceptional-fibers/forecasts/trends-2026-11-06.md:13,261`). |
| Closing order, Iso and W8 | measured | Degrees 1 through 5 close at N=3d+1; out-of-sample Iso degree 6 also follows the rule. Degree 7 at N=22 remains a hypothesis. |
| Closing order, X- | measured | Degrees 1 through 6 close at N=4,8,11,15,18,22, matching floor(7d/2)+1. Degree 7 at N=25 remains a hypothesis. |
| Last jump | measured | On Iso, W8, and X-, the final increment is `(2d+1)^2` over the measured degrees. E8-bar differs, with final jumps 55 at degree 4 and 81 at degree 5; extension beyond the measured fibers and degrees is a hypothesis. |
| Block split | measured | The last jump splits as block 0 `(2*floor(d/2)+1)^2`, block 1 `d(d+1)`, and equal residual blocks 2 and 3 (`docs/evidence/a5-exceptional-fibers/forecasts/trends-2026-11-06.md:120-133`). The same split across fibers is an unstated data pattern, not a proved invariant. |
| Engine versions | computed | Registered grids agree across older engines and v10/v11; receipt-bound and unreceipted v11 W8 runs agree exactly (`docs/evidence/a5-exceptional-fibers/w8-n16-azure/README.md:8-18`). Agreement validates these grids, not arbitrary future inputs. |
| Cost driver | measured | Singular export consumes 97 to 99 percent of the E8-bar, X-, and VB wall time; matrix rank is not the main wall (`docs/notes/topics/a5-exceptional-fiber-status.md:50-56`). This cross-fiber cost pattern is absent from the ledger claims. |
| Weaker than row wording | computed | W8 degree-5 records support certification but the registry does not; A5-070 crosses only lower caps; A5-241 lacks dependence-calibrated family inference. These three status surfaces are stronger than their supporting mechanism. |

## New conjectures and cheapest falsifiers

| Subject | Classification | Conjecture | Cheapest falsifier |
|---|---|---|---|
| Degree-7 closing orders | hypothesis | Iso and W8 close at N=22; X- closes at N=25. | Run receipt-bound rank at N=21/22 for Iso or W8 and N=24/25 for X-. Any earlier closure or failure to close at the predicted N falsifies the formula. Start with Iso because W8 degree-6 projections already exceed ordinary workstation memory (`forecasts/trends-2026-11-06.md:243-254`). |
| Last-jump law | hypothesis | The `(2d+1)^2` jump and stated block split continue for Iso/W8/X- beyond the measured range, but do not extend unchanged to E8-bar. | Iso degree 6 already supplies the cheapest next-degree control: compare N=18 to N=19 and require total 169 with blocks 49/42/39/39. A mismatch falsifies continuation. |
| VB degree-3 component | hypothesis | The missing degree-3 component appears only through order-2 arcs on t1=0 or the t7-chart apex. | Add jet parameters to those two loci and compute the order-2 pullback. An arc whose generic point lies in the fiber and whose center lies on the degree-3 component supports it; exhaustive failure on the normalized loci falsifies this route (`docs/notes/topics/a5-exceptional-fiber-status.md:44-49`). |
| E8-bar degree 6 | hypothesis | The 140 classes of `sqrt(K2)_6/K2_6` lie in the fiber relations, giving h6=1526 rather than merely h6 at most 1666. | First test the same membership implementation on the 91 known degree-5 classes, then test all 140 degree-6 classes. One nonmember falsifies equality; the resulting dimension decides the exact h6 (`docs/notes/topics/a5-exceptional-fiber-status.md:50-52,67`). |
| Characteristic 0 | hypothesis | The two finite-field K2 presentations reconstruct one ideal over Q(i), and the finite-field all-degree equality specializes without a Hilbert-function jump. | Rationally reconstruct K2 from both primes, compare reductions, test exact degree-2 membership, then prove flatness or control bad primes. Disagreement, failed membership, or a specialization Hilbert jump falsifies the claim (`docs/notes/topics/a5-exceptional-fiber-status.md:21-22,34,71`). |

## Remaining work for every open row

Costs labeled `measured` come from retained runs. `Estimated` values state their measured anchor; `unmeasured` means the repository supplies no defensible numeric peak or wall estimate.

| Open row(s) | Deciding computation | Cost and peak memory, with estimate evidence | Host fit |
|---|---|---|---|
| A5-016 | Order-2 Sage arcs with jet parameters on t1=0 and the t7-chart apex; test whether the degree-3 component enters the fiber. | Measured anchors: chart-5 normalization 359 s; fast t7 normalization 7 min 31 s; full t7 normalization 2 h 3 min 30 s at max RSS 5,415,944 KiB. New jet solve cost and peak are unmeasured. | Build host for small Sage charts; laptop if the new solve approaches the full normalization. OCI A1 is unsuitable because the workflow needs Sage, not only Singular. |
| A5-029 | Compute exact kernel bases and Plucker limits along each certified generic arc family using the explicit acceptance condition in finding 1. | Wall and peak are unmeasured. The certified arcs and 32 by 32 left-multiplication matrices make this plausibly minutes per arc, but that statement is a hypothesis rather than an estimate. | Laptop first; build host only after one arc measures a small fit. |
| A5-083/089/095/101 | At one N-minus representative per prime, validate membership on 91 degree-5 classes, then test all 140 degree-6 classes; transport signs. | Pilot is unmeasured. Measured predecessor: W8 degree-2 receipt took 5,619 s and 6.7 GB. Direct E8-bar degree 5 took 118,427 s and 35.4 GiB, so direct rank is the fallback, not the first test. | Laptop fits the known 35.4 GiB predecessor. Build host may run only a measured small pilot. OCI A1 lacks likely memory. A paid VM of at least 64 GiB needs a written approved case only if membership fails. |
| A5-202 | Preregister a fresh-mesh test comparing the frozen shifter-map increment with the efficiency-only model. | Measured predecessor: 84 iterations, 11,010,048 shots, 259 s, credit ceiling 1.131072 (`docs/design/ascella-pathion-mesh-persistence-case.md:32-45,150-158`). A reduced 32-iteration design estimates 99 s by 259*32/84 and retains the same ceiling; that design is a hypothesis. Provider peak memory is unavailable; local analysis is small. | Quandela Ascella only, after a new written case, simulation gate, fresh QRNG seed allocation, and owner approval. None ran in this review. |
| A5-242 | Move the orientation phase to another data qubit, repeat the IBM full map with readout correction, and compare the character ordering. | Measured predecessor: 393,216 submitted PUB shots, 18 s QPU charge, 30 s ceiling. Estimate the same shots and about 18 s, bounded by 30 s. Local spectral analysis is measured at about 45 s and 0.2 GiB (`docs/evidence/pathion-kernel-map/nhat-bias/README.md:231-242`). | IBM hardware after a new written case, live calibration, and owner approval; local analysis fits every listed host. None ran in this review. |

Characteristic 0 is absent from the eight open ledger rows but remains mandatory program work. Its reconstruction and membership pilot have unmeasured wall and peak memory; the laptop is the first host because both finite-field inputs already fit there. Kaggle supplies no unique advantage for any listed symbolic computation. Every provider or paid-host action remains approval-gated.

## Checks, defects, and source availability

The review ran the following bounded checks with `PYTHON=python3`, `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, and `PYTHONDONTWRITEBYTECODE=1`:

```text
$ "$PYTHON" docs/evidence/a5-exceptional-fibers/ledger.py --check
rows 242
certified 90
open 8
proved 32
refuted 44
rejected 6
superseded 9
survives 53

$ "$PYTHON" build_registry.py --check d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2 xm-lown ../../local/a5-failed-runs iso-d6-n19-laptop vb-d6-laptop
registry matches

$ "$PYTHON" nhat_bias.py --check
result.json matches a recomputation

$ "$PYTHON" nhat_spectral.py --self-test
all controls passed

$ "$PYTHON" nhat_spectral.py --check
result_spectral.json differs from a fresh computation
```

The registry check proves reproducibility from its declared roots; the check does not prove that the roots are complete. A direct 96-cell comparison found only the four W8 mismatches listed above. `scripts/check_markdown_links.py` checked 1,088 Markdown files and reported that every relative link and anchor resolves. The status-page totals and 92/96 recount match the ledger.

Code/record/text defects with locators are: non-decisive A5-029 falsifier at `ledger.tsv:30`; overbroad A5-041 refutation at `ledger.tsv:42`; false 11 GB refutation at `ledger.tsv:70` and `structure/arcs-iso-w8/README.md:67-74`; omitted W8 records at `w8-n16-azure/README.md:3-44`; dependent aggregation at `nhat-bias/README.md:221-229`; spectral last-digit drift at `nhat-bias/result_spectral.json:4059`; and mixed supersession semantics in A5-040/044/052/072/073/094/100/191/237.

Every source listed by the brief was readable, including the three workspace document repositories. The review used retained transcriptions and manifests for literature reconciled by the previous deep review and did not independently reread every external PDF or perform current web verification.

The review performed deterministic exhaustive checks only. It started no provider job, cloud resource, or paid host; it made no commit, push, stash, or branch change.
