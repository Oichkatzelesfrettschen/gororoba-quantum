No FATAL defect appeared in the 24-slot builder or retained proposal. The artifact earns a bounded PASS as a deterministic, public catalogue of both alternatives. It does not earn submission authority or a complete private-randomization design.

## Findings

**SERIOUS — the generic submission route bypasses the proposal’s authority and provenance fields.**

[`qi_platform._submit()`](../../../scripts/qi_platform.py) consumes `backend`, `backend_type_id`, `nqubits`, `shots`, and each circuit’s `file` and `sha256`. It ignores:

- `provider_execution_authorized`
- `status`, `slot`, and `comparison_arm`
- `backend_snapshot`
- `compiled_sha256`
- `compiler_receipt_sha256`

The CLI accepts any nonempty `--approval`, and [`run()`](../../../scripts/qi_platform.py) does not pass the optional `expected_cases_sha256`. Consequently, the slot-01 baseline manifest can carry `provider_execution_authorized=false` and still reach provider client construction and POST operations if an operator invokes the generic command.

The working design accurately admits this boundary at [lines 171–173](../../../docs/design/tuna-destination-sequential-evidence-case.md). A reviewed guard must bind the exact manifest digest, current slot, allocation release, approval, admission observation, and authority before dispatch.

**SERIOUS — the QRNG custody design cannot presently rule out fabricated or selectively chosen draws.**

[`anu_qrng.admit()`](../../../scripts/anu_qrng.py) verifies internal JSON consistency, a self-computed hash, value count, and range. It authenticates neither the server response nor the first eligible request. An in-memory probe supplied 24 arbitrary zero values, labeled the response with the ANU endpoint, and obtained an admitted record.

Therefore, a custodian can presently fabricate a structurally valid receipt or request multiple draws, discard unwanted sequences, and commit only the chosen sequence. A later salted opening proves consistency with that chosen record; it does not prove first-draw use or conditional fairness.

The private design correctly leaves the protocol unimplemented, but [the candidate custody boundary](../../../docs/design/tuna-destination-private-assignment.md) does not yet specify:

- authenticated response provenance or an explicit trust assumption covering fabrication;
- a first-request/no-discard rule with every attempt, error, and retry retained;
- an independently witnessed commitment time;
- an assignment-request timestamp and response deadline fixed before arm disclosure;
- protection against a custodian delaying release according to known current or future arms.

Those omissions remain approval blockers. They do not make the current unapproved proposal an admitted run.

**SLOPPY — exact-tree checking has a hard-link and check-to-use boundary.**

[`check_proposal()`](../../../scripts/qi_tuna_destination_slot_cases.py) rejects altered bytes, extra entries, special entries, and symlinks. It does not reject hard links or bind checked file descriptors to a later dispatch.

Concrete counterexample: a hard link containing the expected source bytes passes `is_symlink()`, `is_file()`, and byte equality; mutation through the external link after checking changes the proposal. The generic submit route independently rehashes source bytes, but a coherent source-plus-manifest replacement can pass because the CLI does not bind an expected manifest digest. The future dispatch guard should snapshot or open and hash the exact files under the account lock immediately before use.

**SLOPPY — native compiler provenance and warning-clean execution remain bounded.**

The six-circuit historical replay succeeds normally under Python 3.13.15 with OpenSquirrel 0.9.1, libqasm 1.2.1, and NumPy 2.5.4. The receipt binds all 76 OpenSquirrel Python files, four repository dependencies, the compiler configuration, predecessor receipt, and exact compiled output.

Running the same replay with `-W error` exits 139. Direct `import libqasm` under `-W error -X faulthandler` also segfaults inside the SWIG/native module import. The receipt does not hash the Python executable, native shared objects, or wheel artifacts. The successful replay establishes exact behavior for the retained circuits under the normal invocation; it does not establish warning-clean native imports or complete binary provenance.

## Verified PASS surfaces

- All 150 binding entries match both staged and working bytes: 145 proposal files, producer, test, two designs, and compiler receipt.
- The proposal contains exactly 145 files: one catalogue plus `24 × 2 × 3` arm files.
- All 48 `(slot, arm)` combinations exist and have distinct manifest hashes.
- Exact source and compiled identities:

  - Baseline: source `3ab15a…f267`, compiled `47a608…c201`; early destinations q4→17, q11→18, q6→19.
  - Rotated: source `3084ee…d6d5`, compiled `a050c4…6ed`; early destinations q4→19, q11→17, q6→18.
  - Both map terminal q0–q16 to bits 0–16.

- Each expanded source has 71 instructions. The only source-stream differences are the three early classical destinations. Removing measurement destinations yields one physical-stream digest, `a7c7aa…bab4`.
- The historical receipt digest `c61eb8…ce8d`, backend digest `e92dab…1223`, predecessor receipt, compiler configuration, dependency hashes, and installed OpenSquirrel Python hashes all match.
- The documented historical compiler replay and the slot-builder replay both pass.
- In-memory mutations of the historical source, compiled source, manifest, backend snapshot, and compiler receipt were all rejected.
- The checked-in tests cover changed proposal bytes, extra files, extra directories, and symlinks.
- The sensitivity counts independently reproduce `0/65536`, `783275/1048576`, and `16764265/16777216`.
- The public catalogue contains both arms for every slot and contains no selected assignment.

A selected filename, source hash, manifest digest, or directory remains an exact arm oracle because the public catalogue maps each identifier to its arm. The current catalogue conceals future assignments by publishing both choices symmetrically. Any future custody implementation must keep all selected identifiers and access logs private until their slots become current.

Final measurements found all 150 bound bytes unchanged in the worktree and index, clean staged and working `git diff --check` results, and no workspace core file. Pytest was not executed because its `tmp_path` tests write files; mutation probes stayed in memory.
