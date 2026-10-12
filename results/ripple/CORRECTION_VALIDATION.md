# Correction-policy production validation

The full first shell block in [AGENTS.md](../../AGENTS.md) exits 0 against
source commit `67106bd1d11397f0dcacb0c48f509a2e0d02fb89`. Warnings are errors;
Ruff checks pass, 83 files pass formatting and 80 source files pass mypy.
The [receipt](correction-validation-receipt.json) retains dependency versions,
test counts, bounded evidence classifications and hashes of operator-held logs.

Normal and optimized Python checks cover the circuit, statistic, schedule,
preparation, planner, collector and case contracts. Mutation checks reject 19
circuit changes, 92 schedule changes, 38 case changes and 13 malformed raw
inputs. Another 21 evidence mutations withhold collection decisions. The
complete synthetic collection test reloads actual QPY, decodes real Qiskit
BitArray results, persists raw shot strings, checks integer histograms before
normalization and reaches the gated exact-count decision. Seventeen invalid
CLI configurations fail before service construction.

Independent integration review caught late CLI rejection of unsupported
ceilings/scenarios; CLI and planner now reject those settings before compiling
or simulating. The review also narrowed the prose about floating-point power
enumeration and bound-pair validation: full support enumeration retains
underflow/rounding limits, and the source/template/archive chain supplies
algorithm provenance beyond pair conformance.

Offline fresh-compilation checks retain equal family configuration, packed
circuits, executable PUB bytes and reselection identity across six actual
compilations on three bundled device Targets. Final PUB serialization is
stable after packing removes native layout metadata. These checks establish
local reproducibility, separate from fresh hardware evidence.

The local Runtime skill verification passes client-side Sampler execution for
plain static, twirling/DD static and guarded dynamic circuits. Dynamic
mitigation remains disabled. Every probe uses a local backend; the service
constructor remains unused.

The [historical live case](../live/2026-10-12T074042.840320Z/UNAPPROVED_CASE.md) admits the complete family
after comparing 18 candidates across all three live systems. Its 41-file
source closure and seven dependency versions match. A separate audit
recomputes selection and costs, rerenders identical case bytes, parses the
literal replay command back to the recorded policy, and verifies the record,
QPY and case hashes. All five retained sidecars pass `SHA256SUMS`.

The required default live dry run exits 1 after the existing 256-combination
joint-placement limit. That bounded rejection is retained explicitly; the
four-PUB family succeeds independently. Both invocations send zero physical
or mock primitive jobs. Returned hardware schedules and actual charged
seconds remain execution-time evidence.

## Readout scoring repair and renewal

The [new receipt](scoring-repair-validation.json) binds source `efa187f`, the
full repository and source-library gates, eight real-Target ranking cases and
seven rejected scoring mutants. Normal and optimized algebra contracts agree.
Candidate scores follow readout-writer binding, deterministic reranking and
then truncation. The bounded primary frontier and primary-based placement
quality retain their separate meanings.

The live renewal exits 1 before compilation because backend eligibility
cannot supply all three required snapshots. Its [retained rejection](correction-renewal-rejection.json)
qualifies the failure path; it supplies neither a fresh timing estimate nor
an executable approval case. Earlier pilot, atlas and measured-job records
retain identical bytes. The earlier validation receipts retain their named
historical revisions and scope.
