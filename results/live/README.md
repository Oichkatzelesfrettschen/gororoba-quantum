# Live-run audit records

Each directory records one `gororoba_quantum/live_run.py` invocation under its
UTC start time. `record.json` carries the schema-specific plan and lifecycle
evidence; `isa.qpy` carries the exact circuits produced by that revision.

- **Schema 6 records.** The
  `live-target-cross-group-fused-pubs-scheduler-usage-v1` contract keeps the
  schema-5 fused-PUB surface and adds per-PUB scheduler timing and per-job
  usage. Each PUB manifest records `target_gate_lower_bound_dt` and the
  feed-forward structure counts; every job requests
  `execution.scheduler_timing`. Collection writes one timing record per PUB
  (`timing_status`, window, `scheduled_circuit_duration_dt`,
  `scheduler_residual_dt`, reason) and one usage record per job (`usage_status`,
  `qpu_charge_time_seconds` from `job.usage(partial=False)`,
  `pub_shots_per_qpu_second`) in the collection header; group records reference
  their job by id. A PUB without an execution window keeps its counts and
  loses only its calibration-bound views.
- **Schema 5 records.** The `live-target-cross-group-fused-pubs-v1` contract
  jointly allocates same-backend, same-kind replica pools and archives the
  exact fused Runtime PUBs. Ordered manifests map each PUB to namespaced
  logical components and bind that map into recovery tags. The full experiment
  has 29 logical static entries in 14 PUBs and 9 logical dynamic entries in 6
  PUBs when each kind uses one backend. The shared reference PUB changes the
  old isolated crosstalk statistic into a global packed-workload versus global
  replica-0 comparison. Collection reconstructs each logical entry from QPY
  and fans the PUB's execution window and calibration out to every component.
- **Schema 4 records.** The `live-target-packed-replicas-v1` contract combines
  live system inventory, circuit-derived capability admission,
  degraded-hardware-filtered routing, recursive Target validation, packed
  disjoint replicas, isolated crosstalk references, per-replica variance and
  admission views, approval-gated pre-submission reselection, whole-group
  job-batch partitioning, archive integrity, immediate batch revalidation, and
  recovery identities. A changed approved plan enters `approval_required`,
  records its revised QPY digest, and sends zero Runtime jobs. `--collect`
  accepts a submitted schema-4 record only when its
  source digest and contract identifier match the checkout. The top-level
  `policy.replica_floor` records an explicit all-group override or `null`;
  `groups[].replica_floor` records the effective floor applied to each group.
- **Schema 3 packed-replica records.** Records from source commits `9384f01`,
  `b447626`, `da50fd5`, `cdb37c4`, `78a3bb7`, and `02a5b4b` carry `replicas`,
  per-replica predictions, intervals, variance, crosstalk, and admission views.
  The last two records exercise the explicit global floor and the per-group
  floor respectively. All packed schema-3 records predate system inventory,
  filtered-Target routing, approval-gated reselection, and the planned-job
  ledger.
- **Schema 3 capability-admission record.** The retained
  `2026-10-10T220438.712726Z` record from source `0205a61` carries
  `system_inventory`, `circuit_requirements`, capability decisions, and
  filtered-Target routing for 31 unreplicated base and mirror circuits. The
  record lacks replica placement, isolated references, variance views, and
  submission evidence.
- **Schema 2 records.** These records carry the earlier lifecycle, source
  digest, and commit contract. They predate system inventory and the
  planned-job ledger.
- **Legacy records.** Records without `schema_version` are historical dry-run
  plans. `--collect` rejects them.

`2026-10-11T062204.877756Z` is the first retained schema-5 fused-PUB
qualification. It comes from clean source commit `4b5dd78` with experiment
digest `7d756845d39509883131ed3453f61be6b6ce4b35fba25677a070128cf3063374`.
The explicit `--max-pending 300` dry-run bound admits Fez at 270 pending jobs
and Kingston at 183; Marrakesh reports maintenance. Kingston wins all seven
groups. The archive holds 20 uniquely named circuits and its manifests map 38
unique logical components to 14 static and six dynamic PUBs. Independent QPY
validation confirms exact manifest/register order, component ownership,
disjoint cross-group footprints, and the required joint-placement rounds. The
record stays `planned`, has no `submission` field, and sends zero QPU jobs, so
the explicit queue bound leaves default-policy submission readiness
unestablished. Record SHA-256 is
`813be4a7e9e654c5a0043c596f900d4f3537c010d5bc9a863037f77163f4ae50`; QPY
SHA-256 is
`999c9efdf2aa68113eacd0160774e9178a4d3dc46be6939991a9b1003821b7bb`.

`2026-10-11T114958.902835Z` requalifies the packing equivalence statistic on the merged
scheduler-timing main. Clean source commit `6ed540f` (sources_modified=false)
carries experiment digest
`9cba470744c884f88ee3c8ce299d99fea2131850a002080bd3ba866e6adc9a4e`.
At 4096 shots the noise model reads design_a single_group/equivalent_within_0.03; zero_divisor_fringe global/equivalent_within_0.03; design_c_8_1_4 global/equivalent_within_0.03; design_c_16_1_8 global/equivalent_within_0.03; design_c_32_1_16 global/difference_not_resolved; folded_qpe_mod15 single_group/equivalent_within_0.03; hybrid_shor_mod15 single_group/equivalent_within_0.03.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`9c4285d7a293ea52fb5364494aaae14f896d5e610efc8d9d782330bfe71dbdde`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T113111.266543Z` requalifies the packing equivalence statistic with the PUB scope
carried into the fidelity comparison. Clean source commit `7f2e7f8`
(sources_modified=false) carries experiment digest
`72a8321ffd65a0cf101c1227677bafe410489de6d083688577f3e565ea732979`.
At 4096 shots the noise model reads design_a single_group/equivalent_within_0.03; zero_divisor_fringe global/equivalent_within_0.03; design_c_8_1_4 global/equivalent_within_0.03; design_c_16_1_8 global/equivalent_within_0.03; design_c_32_1_16 global/difference_not_resolved; folded_qpe_mod15 single_group/equivalent_within_0.03; hybrid_shor_mod15 single_group/equivalent_within_0.03.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`2e08db3de61e25e1c272bafafe74034cb00291367a4da2d7ad9675f6bd728553`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T111555.975109Z` requalifies the packing equivalence statistic with the
continuity-corrected hybrid interval, the 64-shot floor from exact
enumeration, and the mechanism-neutral interpretation, on the bounded fusion
search. Clean source commit `32f8b06` (sources_modified=false) carries
experiment digest
`0f776a7f3b1b93616fc6047911ca81fe9a5aa91d8b956edfabbd2d8b9868f36b`.
At 4096 shots the noise model reads design_a equivalent_within_0.03; zero_divisor_fringe equivalent_within_0.03; design_c_8_1_4 equivalent_within_0.03; design_c_16_1_8 equivalent_within_0.03; design_c_32_1_16 difference_not_resolved; folded_qpe_mod15 equivalent_within_0.03; hybrid_shor_mod15 equivalent_within_0.03.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`6e75d92d50ecd7bf7201e45c751973b91eae7089ef574326f32c490cab903f65`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T101630.331262Z` requalifies the packing equivalence statistic with the 1024-shot
floor from exact enumeration. Clean source commit `fbdb3bc`
(sources_modified=false) carries experiment digest
`1a65cf8d997a6c6ad8e2dbd14a3120cbc30ab4fe3f3efd7c3859952cdeaa4945`.
At 4096 shots the noise model reads design_a equivalent_within_0.03; zero_divisor_fringe equivalent_within_0.03; design_c_8_1_4 equivalent_within_0.03; design_c_16_1_8 equivalent_within_0.03; design_c_32_1_16 difference_not_resolved; folded_qpe_mod15 equivalent_within_0.03; hybrid_shor_mod15 equivalent_within_0.03.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`277204b26629986b77622943ddb765500e6afc3c27972966e70fb872e0a48adf`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T100158.375275Z` requalifies the packing equivalence statistic with the shot
floor and the residual-status gate. Clean source commit `adc8d97`
(sources_modified=false) carries experiment digest
`190590c17df61a37a5aef34151e7e7b9fdcbb46111df760b9545b61465ba6cb1`.
The noise model reads design_a equivalent_within_0.03; zero_divisor_fringe equivalent_within_0.03; design_c_8_1_4 equivalent_within_0.03; design_c_16_1_8 equivalent_within_0.03; design_c_32_1_16 difference_not_resolved; folded_qpe_mod15 equivalent_within_0.03; hybrid_shor_mod15 equivalent_within_0.03.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`2d54cb68e1fd04465eb6753f8a40a250a197bdade6210ef6b5c9659b48418a92`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T094055.608273Z` requalifies the packing equivalence statistic with the
bounded Newcombe interval for every score and the improvement verdict. Clean
source commit `ddbbcb8` (sources_modified=false) carries experiment
digest
`22702d25e3eb68081e0f774c1c048d3809973b4f242b30ec0e3c049be9e3a488`.
The noise model reads design_a equivalent_within_0.03 (newcombe_wilson); zero_divisor_fringe equivalent_within_0.03 (newcombe_wilson); design_c_8_1_4 equivalent_within_0.03 (newcombe_wilson); design_c_16_1_8 equivalent_within_0.03 (newcombe_wilson); design_c_32_1_16 difference_not_resolved (newcombe_wilson_bhatia_davis); folded_qpe_mod15 equivalent_within_0.03 (newcombe_wilson); hybrid_shor_mod15 equivalent_within_0.03 (newcombe_wilson).
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`3734874afce712274a239478ad6b17e6564befff66116f6f54647bbbe6e8e64d`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T091715.073826Z` qualifies the packing equivalence statistic. Clean source
commit `d1a0920` (sources_modified=false) carries experiment digest
`bbb43a7d1e9e09febbda2ca3812f58b6c5c3efd0a66294d4ba1ff6afd3b29ae7`.
Every group's `global_packing_crosstalk` now carries the packed-minus-reference
difference with its 95 percent interval and the two-one-sided verdict against
the preregistered margin 0.03; the noise model reads
design_a equivalent_within_0.03 [-0.0028, 0.0131] (newcombe_wilson); zero_divisor_fringe equivalent_within_0.03 [-0.0071, 0.0129] (newcombe_wilson); design_c_8_1_4 equivalent_within_0.03 [-0.0182, 0.0011] (newcombe_wilson); design_c_16_1_8 equivalent_within_0.03 [-0.0243, 0.0013] (newcombe_wilson); design_c_32_1_16 difference_not_resolved [-0.0363, 0.0032] (normal); folded_qpe_mod15 equivalent_within_0.03 [-0.0200, 0.0073] (newcombe_wilson); hybrid_shor_mod15 equivalent_within_0.03 [-0.0297, 0.0136] (newcombe_wilson).
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`79e35c6a8a6bef2e215bb4ea07e450370c74fc8622612cc0d14db3255ec8bd58`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T093445.248590Z` requalifies schema 6 after collection moved the residual bound
to the execution-time Target and began reading usage before results. Clean
source commit `878167f` (sources_modified=false) carries experiment
digest
`47f6564d67cfd6f72fb89fcdef77f7d3454c629e7d37d22a3b9e132e62b2d004`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`54c1705b70e1b7884cff4ebfc5610e3af090df0303f92689e8b67d0eb521fb23`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T114048.080610Z` requalifies schema 6 after collection began polling a finished
job's usage until the service's calculation completes. Clean source commit
`106e59b` (sources_modified=false) carries experiment digest
`ce8bc72d890ce3aa57b48f5f12aabd3295d15fe6e70b653923a083d9e4a37ec7`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`d18c0ef542b10260bc9affc275c9a4eae6a963a9719fa85a2b3881a2162792af`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T111237.410777Z` requalifies schema 6 after the joint-placement search gained
its attempt bound and per-candidate entry bases, and after collection began
re-reading usage for a job that fails while collection waits. Clean source
commit `76eb303` (sources_modified=false) carries experiment digest
`e38510b4a6d3a4fe87b7cd0fdc6473143e34fe617b5e8acbdca3e668af6f9a05`.
The search accepted combination 1 of a frontier of
4782969. The record stays `planned` and sends zero QPU jobs.
Record SHA-256 is
`b7223494e0b11a7672a0949007c04952e0156ab19b7d6d7da028ae5d98051aed`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T102037.475268Z` requalifies schema 6 after collection moved its checkpoints to
collect.partial.json, confined throughput to DONE jobs, and scoped the packing
comparison. Clean source commit `37506e4` (sources_modified=false) carries
experiment digest
`7b0de60e5005b33c7e0a16e87a4f459e7b42e19330fe650f5f6368cddca8ac62`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`5f8ec0bf35d0f30ee35db204203f1b84df764da9c9dcc20de863bd9e4075a270`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T100526.684788Z` requalifies schema 6 after packing_schedule moved to scheduler
residuals gated on a complete timing status. Clean source commit `9756ec3`
(sources_modified=false) carries experiment digest
`20bd45a5149145e8164bb382dd061b03c66e54dd21d3a4ff275f74d1a31fa00a`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`d7400b165b2089d5081167bf60d56e6638c9fd8e11786f8f00e6ce3ffaab4f92`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T095108.705673Z` requalifies schema 6 after collection began checkpointing
each job's usage and refreshing it once a running job's result returns.
Clean source commit `abb481e` (sources_modified=false) carries
experiment digest
`33a529a3a2980f7a148ab71db4f0c5a16b100ce972eccac3efca9197850548c3`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`4836ac0086cf84e5f2cff1837c9d4423ac2af00833cfa3c82d3adbda7663415a`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T090500.749224Z` is the first schema-6 record, contract
`live-target-cross-group-fused-pubs-scheduler-usage-v1`, from clean source
commit `51a55ae` (sources_modified=false) with experiment digest
`5543c0f06d36339949cc8fdd76841e7d307c03fc28e3c21fb3fbcd50506063e4`.
Every PUB manifest now carries `target_gate_lower_bound_dt` and the
feed-forward structure counts; the 6 dynamic PUBs read
(parallel streams, sequential stages, control-flow operations) =
{'ibm_kingston_dynamic_pub_01': (9, 1, 9), 'ibm_kingston_dynamic_pub_02': (2, 1, 2), 'ibm_kingston_dynamic_pub_03': (9, 1, 9), 'ibm_kingston_dynamic_pub_04': (3, 1, 3), 'ibm_kingston_dynamic_pub_05': (3, 1, 3), 'ibm_kingston_dynamic_pub_06': (3, 1, 3)}
with Target lower bounds {'ibm_kingston_dynamic_pub_01': 3334, 'ibm_kingston_dynamic_pub_02': 3295, 'ibm_kingston_dynamic_pub_03': 3334, 'ibm_kingston_dynamic_pub_04': 3334, 'ibm_kingston_dynamic_pub_05': 3334, 'ibm_kingston_dynamic_pub_06': 1659} dt. The record stays
`planned`, sends zero QPU jobs, and carries no timing or usage records, which
only a collected job supplies. Record SHA-256 is
`6c0d04b9cc4e7417ccd872af39ebe8935a3d5b3c301b0870df251d7df0607472`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T095541.923847Z` requalifies the affine challenger branch after it took the
process-pool main. Clean source commit `07f197b` (sources_modified=false)
carries experiment digest
`c5e78d489bf098dfba152eaf276915f66ef0d97b37c13a8ded7fe86fa4364765`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`4b5e61dcaa5e87c5a76a7cbccf7bf85e5ef115951d87fe118a5b8b4fd5f28dfa`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T093336.320234Z` qualifies the experiment digest after affine_residual.py joined
the source manifest (modular_arithmetic imports it for the explicit-only
affine-residual candidate). Source commit `ce40cd6` (sources_modified=false;
the commit message was reworded afterward on an identical tree) carries
experiment digest
`097c5b48dca92ffe4e45bec4c3da45844ce26c26a6d41b4e33698b1729546232`.
The record stays `planned` and sends zero QPU jobs. Record SHA-256 is
`2245c42f8eb4f853c93fdf672c3979760eba85a96708394eb4db27627e2b58c0`; QPY
SHA-256 is
`9bcc20c25bde69a889ea641a93606478074e063f23f4f53fb4693a5ab6c88917`.

`2026-10-11T091019.824103Z` requalifies the process-pool branch after collection replay
moved to one seeded batch per calibration (replay_entries). Clean source
commit `eb40fa1` (sources_modified=false) carries experiment digest
`39644e96aead937775a48e3f7e3ee418fab0e0005d67a9744b0248e3d55357d0`.
The default-policy invocation plans in 50 s wall and stays `planned` with zero
QPU jobs. Record SHA-256 is
`96318b9b46ca355089b99011136311b4f6d8ee252ea87b6d93e69a4586b253cd`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T085437.294823Z` qualifies the process-pool branch. Clean source
commit `1ea5de1` (sources_modified=false) carries experiment digest
`7bbc903555609d683b13055e1d903ad8c18de0a28a0422bd7196759238d326eb`,
including the new `parallel.py` dependency. The default-policy invocation
`live_run.py --out ../results/live` plans on ibm_fez, ibm_kingston in 60 s wall
at about 2.5 cores, against 172 s for the previous record on one core. Every
replica now draws from its own batch-position seed, so the global packing
differences read {'design_a': 0.0071, 'zero_divisor_fringe': 0.0029, 'design_c_8_1_4': -0.0085, 'design_c_16_1_8': -0.0115, 'design_c_32_1_16': -0.0166, 'folded_qpe_mod15': -0.0132, 'hybrid_shor_mod15': -0.0105} instead of the exact 0.0 of
the shared-seed records. The record stays `planned` and sends zero QPU jobs.
Record SHA-256 is
`522e3bf7f765cda7a0139a326147a54b966a38188e104030de660e8653fb8e75`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T082455.919602Z` qualifies the dynamic-mitigation boundaries:
ODR mirrors reject dynamic circuits, and terminal readout correction is
withheld only for feed-forward circuits. Clean source commit `54aa215` carries
experiment digest
`79a34743244b77cd2b3356f6951abbb8abaf5ad668857ac3e8a734193e36463e`.
The default-policy invocation `live_run.py --out ../results/live` admits Fez
and Kingston; Marrakesh reports maintenance. Fez wins design A and hybrid
Shor, and Kingston the other five groups. The record stays `planned` and sends
zero QPU jobs. Every group's `global_packing_crosstalk` difference reads
exactly 0.0, because every entry's simulation shares one seed and the
reference copy reproduces packed replica 0 shot for shot. Record SHA-256 is
`503cc3da9d08f2426b80a145bf6091dc18405ea416d33aef0621777c66e188ef`; QPY
SHA-256 is
`9f89eb73365278c1a94c8cf2888657089c212f96d854e44ff175ff691ef80a23`.

`2026-10-11T071616.724800Z` requalifies schema 5 after coupled candidate
selection, complete required-set placement backtracking, and integration of
the reviewed modular synthesis sources. Clean source commit `b89fdf6` carries
experiment digest
`2544c7b1b031ed9631785dabded7f0c65fae166de51513725b976532a176300f`,
including the new `target_flip.py` dependency. The submit-free invocation uses
`live_run.py --out ../results/live --max-pending 300`; Fez, Kingston, and
Marrakesh report 3, 48, and 24 pending jobs respectively. The first ranked
combination satisfies joint placement, selects Kingston for all seven groups,
and archives 14 static plus six dynamic PUBs covering 38 unique components.
Independent QPY checks confirm manifest and register order, member ownership,
disjoint reserved footprints, and instruction confinement to each component.
The identity-null control leaves part of its reserved footprint idle. The
record stays `planned`, carries `sources_modified=false`, and has no
`submission` field. Local simulation and archive validation establish the
dry-run implementation surface; QPU behavior and default-queue-policy
readiness remain separate. Record SHA-256 is
`54946d4b19b9ec9ff92d7c536ff050ba4dbdd0e3504d7f4e621ff70198682524`; QPY
SHA-256 is
`d0894ad616d82f0ee6b896304b214d3f9e18b9fd3e500019c44452df9b234e5c`.

`2026-10-10T223619.798923Z` is the first combined schema-4 qualification. The
default queue gate first rejects Fez at 194 pending jobs and Kingston at 81;
Marrakesh reports maintenance. The retained rerun sets `--max-pending 250` for
submit-free compilation and local simulation, selects Kingston for all seven
groups, and archives 38 circuits. Its QPY circuit names equal the group-member
and execution-requirement names. The record stays `planned` with `submission`
absent, so it records zero QPU jobs and does not establish default-policy
submission readiness. Record SHA-256 is
`6c347e70e0ea22de682fc935d810612287bbb984d1a3ac551b367f550d5f0f7c`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

`2026-10-10T230646.694665Z` requalifies schema 4 after the first review fixes at
source `2563b3a`, with `code_commit.sources_modified=false` and an experiment
digest that matches that source tree. The default gate records Fez at 141
pending jobs, Kingston at 92, and Marrakesh in maintenance. The retained
`--max-pending 250` rerun again selects Kingston for all seven groups, archives
the same 38 uniquely named circuits, applies the hybrid group's 0.8 floor to
nine replicas, and admits the hybrid factor and order-recovery yields in the
local noise model. Its state remains `planned`, `submission` remains absent,
and the explicit bound leaves default-policy submission readiness
unestablished. Record SHA-256 is
`8452d0751b1aa505c2abf02f19c3d17184b6f8585c39cec5c27f6c58a4a2b09b`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

`2026-10-10T232219.919322Z` requalifies the final direct-pinned-discovery source
at `584a78d`, again with clean source provenance and the matching experiment
digest. The default gate records Fez at 147 pending jobs, Kingston at 95, and
Marrakesh in maintenance. The retained 250-job-bound run has the same Kingston
selection, 38-circuit archive, nine hybrid replicas, and locally admitted
hybrid intervals. Its state remains `planned`, `submission` remains absent, and
the run records zero QPU jobs. Record SHA-256 is
`0c5b57a2db2d4e246908c5a05ccf1eadc0aa87629e2ac3950586f38ef7c55744`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

A dynamic member marks `duration_bound: lower_without_classical_latency`.
Schema-5 and schema-4 top-level inventory fields describe initial planning;
`revalidation[].system_inventory` describes each full pre-submission refresh;
`submission.planned_jobs[].pre_submit_revalidation` describes each immediate
batch refresh. Record, QPY, and collection writes use atomic replacement with
file and containing-directory fsync.

The two historical schema-3 contracts require shape-aware classification:

```sh
for record_path in results/live/*/record.json; do
    jq -r --arg path "$record_path" '
      if .schema_version == 6 then "schema6-scheduler-usage"
      elif .schema_version == 5 then "schema5-fused-pubs"
      elif .schema_version == 4 then "schema4-combined"
      elif .schema_version == 3 and has("system_inventory")
        then "schema3-capability"
      elif .schema_version == 3 then "schema3-replicas"
      elif .schema_version == 2 then "schema2"
      else "legacy"
      end + " " + (.state // "planned") + " " +
      (.code_commit.head[0:7] // "-") + "  " + $path
    ' "$record_path"
done
```
